# LumieTL

LumieTL adalah perangkat lunak penerjemah otomatis (auto-translator) untuk manga, manhwa, dan manhua yang memanfaatkan model deep learning OCR dan mesin penerjemah. Aplikasi ini dirancang dalam arsitektur terpadu yang mendukung dua antarmuka: Desktop Native (Windows) dan Web Application.

---

## Fitur Utama

- **Deteksi Teks dan OCR Presisi Tinggi**: Menggunakan model deep learning berbasis ONNX Runtime untuk mendeteksi gelembung teks manga/manhwa/manhua secara akurat dan mengekstrak teks dengan format horizontal maupun vertikal.
- **Dukungan Multi-Bahasa dan Mesin Penerjemah**:
  - **Bahasa Sumber**: Deteksi Otomatis, Jepang (JPN), Korea (KOR), Mandarin Simplified (CHS), Mandarin Traditional (CHT).
  - **Bahasa Target**: Indonesia (ID), Inggris (EN), Vietnam (VI), Thailand (TH).
  - **Pilihan Engine**: Google Translate, DeepL API, dan OpenAI GPT-4o API.
- **Penerjemahan Gambar Tunggal (Single Image)**:
  - Antarmuka visual interaktif dengan slider perbandingan Sebelum dan Sesudah (Before/After).
  - Kontrol zoom dan pan untuk inspeksi detail grafis.
  - Opsi ekspor langsung ke file atau salin ke papan klip (clipboard).
- **Penerjemahan Batch (Batch Processing)**:
  - Pemrosesan sekaligus untuk seluruh halaman dalam folder atau chapter.
  - Antrean cerdas dengan pemantauan durasi, status per berkas, serta kontrol jeda (pause), lanjutkan (resume), dan batalkan (cancel).
  - Fitur ekspor laporan hasil batch ke format teks.
- **Keamanan dan Perlindungan Data**:
  - Penyimpanan kunci API terenkripsi menggunakan Windows Credential Manager dan Fernet cipher.
  - Validasi berkas berbasis magic bytes serta proteksi terhadap ancaman image decompression bomb dan path traversal.
  - Pembatasan laju permintaan (rate limiting) untuk menjaga stabilitas kuota API.
- **Antarmuka Modern dan Performa Optimal**:
  - Antarmuka bertema gelap (Dark Theme) yang ergonomis.
  - Pemrosesan latar belakang berbasis multi-threading agar antarmuka tetap responsif tanpa freeze.
  - Pencatatan riwayat pemrosesan berbasis basis data SQLite lokal.

---

## Panduan Menjalankan Aplikasi

### Prasyarat Sistem
- Python 3.11 (64-bit)
- Git

---

### 1. Menjalankan Versi Desktop

1. Buka terminal (PowerShell atau Command Prompt) di direktori proyek.
2. Buat dan aktifkan virtual environment:
   ```powershell
   py -3.11 -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Pasang paket dependensi yang dibutuhkan:
   ```powershell
   pip install -r requirements.txt
   ```
4. Jalankan aplikasi Desktop:
   ```powershell
   python -m desktop.main
   ```
   *Catatan: Saat aplikasi pertama kali dibuka, dialog setup akan mengunduh model ONNX yang diperlukan secara otomatis.*

---

### 2. Menjalankan Versi Web (Monolith)

1. Aktifkan virtual environment dan pasang dependensi web:
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install -r requirements-web.txt
   ```
2. Jalankan server web LumieTL:
   ```powershell
   python -m web.backend.main
   ```
3. Buka peramban (browser) dan akses alamat berikut:
   ```
   http://127.0.0.1:18420
   ```
