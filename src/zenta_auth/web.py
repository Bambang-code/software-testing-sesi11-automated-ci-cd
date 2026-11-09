"""Antarmuka lokal untuk pengajuan seller pada tugas individu Sesi 11."""

import sqlite3
from contextlib import closing
from pathlib import Path
from secrets import token_hex

from flask import Flask, redirect, render_template, request, session, url_for

from .seller import ApplicationStatus, SellerApplication


def create_app(database_path: Path | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(SECRET_KEY=token_hex(32), SESSION_COOKIE_SAMESITE="Lax")
    database_path = database_path or Path("instance") / "seller.sqlite3"
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(database_path)) as database, database:
        database.execute(
            """CREATE TABLE IF NOT EXISTS pending_applications (
                session_id TEXT PRIMARY KEY,
                shop_name TEXT NOT NULL
            )"""
        )

    def session_id() -> str:
        return session.setdefault("seller_session_id", token_hex(16))

    def render_application(error: str | None = None, status: int = 200):
        with closing(sqlite3.connect(database_path)) as database:
            pending = database.execute(
                "SELECT shop_name FROM pending_applications WHERE session_id = ?",
                (session_id(),),
            ).fetchone()
        return render_template(
            "seller.html",
            status=ApplicationStatus.PENDING if pending else ApplicationStatus.DRAFT,
            shop_name=pending[0] if pending else None,
            error=error,
        ), status

    @app.get("/")
    def show_application():
        return render_application()

    @app.post("/pengajuan")
    def submit_application():
        try:
            application = SellerApplication(request.form.get("shop_name", ""))
        except ValueError:
            return render_application("Nama toko wajib diisi.", 400)

        with closing(sqlite3.connect(database_path)) as database, database:
            inserted = database.execute(
                """INSERT INTO pending_applications (session_id, shop_name)
                VALUES (?, ?) ON CONFLICT (session_id) DO NOTHING""",
                (session_id(), application.shop_name),
            ).rowcount
        if not inserted:
            return render_application("Sudah ada pengajuan yang menunggu.", 409)
        return redirect(url_for("show_application"), code=303)

    @app.post("/pengajuan/tarik")
    def withdraw_application():
        with closing(sqlite3.connect(database_path)) as database, database:
            deleted = database.execute(
                "DELETE FROM pending_applications WHERE session_id = ?", (session_id(),)
            ).rowcount
        if not deleted:
            return render_application("Tidak ada pengajuan yang bisa ditarik.", 409)
        return redirect(url_for("show_application"), code=303)

    return app
