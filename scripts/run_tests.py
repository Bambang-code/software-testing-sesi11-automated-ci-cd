"""Jalankan PyTest dan simpan laporan untuk pemeriksaan lokal maupun CI."""

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--unit-only", action="store_true", help="Demonstrasikan gate coverage gagal."
    )
    args = parser.parse_args()

    mode = "demo-gagal" if args.unit_only else "lengkap"
    report_dir = ROOT / "reports" / mode
    report_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--color=no",
        "--cov=zenta_auth",
        "--cov-branch",
        "--cov-fail-under=80",
        "--cov-report=term-missing",
        f"--cov-report=json:{report_dir / 'coverage.json'}",
        f"--cov-report=html:{report_dir / 'html'}",
        f"--junitxml={report_dir / 'junit.xml'}",
    ]
    if args.unit_only:
        command.append("tests/unit")

    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    (report_dir / "pytest.txt").write_text(result.stdout, encoding="utf-8")
    print(result.stdout, end="")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
