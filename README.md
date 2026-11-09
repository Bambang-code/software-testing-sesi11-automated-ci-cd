# Software Testing Sesi 11 — ZENTA

Tugas individu Bambang Herlambang (5803024019) tentang pengujian otomatis dan pipeline CI. Studi kasusnya adalah pengajuan seller pada aplikasi latihan Flask dan SQLite. Model dan 82 tes unit seller diambil dari [tugas Sesi 10](https://github.com/Bambang-code/software-testing-sesi10-procedural-oo/tree/b2ab785ceba74e9dccb334588ab11bb70a45587c). Aplikasi Sesi 11 membatasi alur web pada status Draf dan Menunggu peninjauan. Setiap sesi browser memiliki pengajuannya sendiri selama server berjalan.

## Jalankan di Windows

Jalankan perintah berikut dari folder Sesi 11. Siapkan Python 3.10 dan Chromium milik Playwright saat instalasi pertama.

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m playwright install --only-shell chromium
.\.venv\Scripts\python.exe scripts/run_tests.py
```

Untuk mencoba formulir lewat browser, jalankan Flask dari folder ini lalu buka `http://127.0.0.1:5000/`.

```powershell
.\.venv\Scripts\python.exe -m flask --app zenta_auth.web:create_app run --host 127.0.0.1
```

Mode demonstrasi menjalankan tes unit dengan cakupan pengukuran yang sama. Kode keluar `1` menandakan gate menghentikan proses ketika coverage berada di bawah 80%.

```powershell
.\.venv\Scripts\python.exe scripts/run_tests.py --unit-only
$LASTEXITCODE
```

## Skenario browser

| ID | Skenario | Hasil yang diperiksa |
| --- | --- | --- |
| UI-01 | Kirim pengajuan dengan nama toko valid | Status berubah dari Draf ke Menunggu peninjauan. Spasi di awal dan akhir nama dibuang. |
| UI-02 | Kirim nama toko yang hanya berisi spasi | Server mengembalikan HTTP 400. Pesan validasi muncul dan status tetap Draf. |
| UI-03 | Muat ulang setelah pengajuan dikirim | Status dan nama toko tetap terlihat pada sesi yang sama. |
| UI-04 | Tarik pengajuan dan ajukan ulang | Status kembali ke Draf, lalu pengajuan baru dapat dibuat. |
| UI-05 | Buka formulir dari sesi browser lain | Sesi lain dimulai sebagai Draf tanpa menampilkan pengajuan sebelumnya. |

Playwright membuka aplikasi lewat HTTP loopback. `SellerPage` menyimpan locator `data-testid` dan aksi browser. Assertion seperti `expect(...).to_have_text(...)` menunggu kondisi yang dapat diamati. Setiap tes browser memakai konteks baru. Dua tes integrasi HTTP juga memeriksa konflik pada kiriman ganda dan penarikan pengajuan yang belum ada.

## CI dan hasil lokal

Workflow [ZENTA CI](.github/workflows/ci.yml) berjalan setiap push dan pull request. Runner memasang dependensi dan Chromium, menjalankan PyTest dengan `--cov-branch`, lalu mengunggah log terminal, JUnit XML, coverage JSON, dan laporan HTML dalam artefak `zenta-test-reports`. Gate memakai cakupan gabungan statement dan tujuan cabang sebesar minimal 80%.

| Mode lokal | Tes lulus | Statement | Tujuan cabang | Coverage gabungan | Kode keluar |
| --- | ---: | ---: | ---: | ---: | ---: |
| Lengkap | 89 | 93/93 | 16/16 | 100,00% | 0 |
| Demo gagal | 82 | 52/93 | 12/16 | 58,72% | 1 |

Pada mode lengkap, 82 tes unit, dua tes integrasi, dan lima tes browser lulus. Dalam mode demo gagal, 82 tes unit tetap lulus. Modul web tidak dieksekusi sehingga 41 statement dan empat tujuan cabang tidak tercakup. Ini menunjukkan gate dapat menolak hasil tes yang seluruh kasusnya lulus ketika coverage masih di bawah ambang.

Bukti lokal dibuat di `reports/lengkap/` dan `reports/demo-gagal/`. Masing-masing memiliki `pytest.txt`, `junit.xml`, `coverage.json`, dan `html/index.html`. Status run GitHub perlu dibuktikan dengan tangkapan layar dari tab Actions setelah kode dipublikasikan.

## Ambil dua tangkapan layar GitHub Actions

1. Push folder ini ke branch `main` repo GitHub pribadi. Workflow yang mendukung **Run workflow** perlu ada di branch default.
2. Buka **Actions → ZENTA CI → Pengujian lengkap** dari push tadi. Saat status **Success**, buka job **PyTest dan Chromium** dan perluas langkah **Jalankan tes dan cek coverage 80%**. Simpan layar sebagai `ci-lulus.png` dengan nama run, status, dan ringkasan coverage terlihat.
3. Kembali ke **ZENTA CI → Run workflow**. Pilih `main`, centang **Demonstrasi gagal karena coverage**, lalu klik **Run workflow**. Buka **Demo gerbang coverage (sengaja gagal)**, perluas langkah tes, dan pastikan baris `FAIL Required test coverage of 80% not reached` terlihat. Simpan sebagai `ci-gagal.png`.
4. Di Windows, tekan **Win + Shift + S**, pilih **Layar penuh**, lalu simpan PNG dari Snipping Tool. Catat tautan masing-masing run untuk bukti laporan.

Folder ini sudah memiliki repositori Git lokal. Jika belum memiliki remote, buat repo GitHub pribadi kosong, salin URL-nya, lalu jalankan perintah berikut setelah mengganti `URL_REPO_PRIBADI`.

```powershell
git add .
git commit -m "Add session 11 automated tests and CI"
git remote add origin URL_REPO_PRIBADI
git push -u origin main
```

## Referensi

- Materi kuliah *Sesi 11 — Automated Testing & Pengenalan CI_CD*, halaman 8.
- [Menjalankan workflow secara manual](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).
- [Menjalankan Playwright pada CI](https://playwright.dev/python/docs/ci).
- [Mengambil tangkapan layar dengan Snipping Tool](https://support.microsoft.com/en-us/windows/apps/use-snipping-tool-to-capture-screenshots).
