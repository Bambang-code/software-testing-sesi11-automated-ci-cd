import pytest

from zenta_auth.web import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path / "seller.sqlite3")
    app.config["TESTING"] = True
    return app.test_client()


def test_duplicate_submission_keeps_original_application(client):
    first = client.post("/pengajuan", data={"shop_name": "Toko Pertama"})
    duplicate = client.post("/pengajuan", data={"shop_name": "Toko Duplikat"})

    assert first.status_code == 303
    assert duplicate.status_code == 409
    assert "Sudah ada pengajuan yang menunggu." in duplicate.get_data(as_text=True)
    pending_page = client.get("/").get_data(as_text=True)
    assert "Toko Pertama" in pending_page
    assert "Toko Duplikat" not in pending_page


def test_withdrawal_without_application_returns_conflict(client):
    response = client.post("/pengajuan/tarik")

    assert response.status_code == 409
    assert "Tidak ada pengajuan yang bisa ditarik." in response.get_data(as_text=True)
    assert "Draf" in client.get("/").get_data(as_text=True)
