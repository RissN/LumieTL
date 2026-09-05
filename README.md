# LumieTL — Manga/Manhwa/Manhua Auto-Translator

> Aplikasi auto-translator offline/hybrid untuk manga, manhwa, dan manhua dalam dua versi (Desktop Windows native & Web self-hostable) dari satu basis kode terpadu (*shared core*).

---

## ✨ Fitur Utama

- **Dual-Version**:
  - **Desktop App**: Native Windows 10/11 x64 berbasis PySide6 (Qt6) dengan Dark Theme elegan dan responsif.
  - **Web App**: FastAPI backend dengan SPA frontend Vue 3 + TypeScript + Tailwind CSS v4.
- **Shared Pure Core**: Tidak ada duplikasi business logic. Modul OCR, model manager, enkripsi, dan rate limiter berbagi kode yang identik.
- **Penerjemahan Single Image**:
  - Drag & drop atau pemilih file (JPG, PNG, WebP, AVIF).
  - Before/After viewer interaktif dengan slider pembatas tengah dan kontrol zoom.
  - Simpan hasil atau salin langsung ke clipboard.
- **Penerjemahan Batch**:
  - Pemrosesan satu folder/chapter sekaligus.
  - Antrean dengan indikator status, durasi, progress bar ganda, dan kemampuan jeda/lanjut/batal.
  - Ekspor log laporan batch ke format `.txt`.
- **Dukungan Multi-Bahasa**:
  - **Bahasa Sumber**: Auto-detect, Jepang (JPN), Korea (KOR), Mandarin Simplified (CHS), Mandarin Traditional (CHT).
  - **Bahasa Target**: Indonesia (ID), Inggris (EN), Vietnam (VI), Thailand (TH).
  - **Engine Translasi**: Google Translate (gratis), DeepL (API), OpenAI GPT-4o (API).
- **Keamanan Tingkat Tinggi**:
  - Kunci API tidak disimpan plaintext (Windows Credential Manager via `keyring` & file Fernet terenkripsi).
  - Enkripsi settings dengan master key persisten.
  - Validasi magic bytes ketat dan perlindungan terhadap serangan *image decompression bomb* serta *path traversal*.
  - Rate limiting engine dan middleware web anti-DoS dengan memory cleanup otomatis.

---

## 🚀 Memulai (Pengembangan Lokal)

### Persyaratan Sistem
- Python 3.11 (64-bit)
- Node.js 20+ & npm (khusus untuk frontend versi web)

### 1. Setup Virtual Environment
```powershell
# Buat virtual environment dengan Python 3.11
py -3.11 -m venv venv

# Aktifkan virtual environment
.\venv\Scripts\Activate.ps1

# Instal dependensi Desktop & Core
pip install -r requirements.txt
```

### 2. Menjalankan Versi Desktop
```powershell
python -m desktop.main
```
*Catatan: Pada saat pertama kali dijalankan, aplikasi akan menampilkan dialog setup untuk mengunduh model ONNX yang dibutuhkan.*

### 3. Menjalankan Versi Web
```powershell
# Instal dependensi web backend
pip install -r requirements-web.txt

# Jalankan build frontend Vue (satu kali)
cd web\frontend
npm install
npm run build
cd ..\..

# Jalankan server FastAPI
python -m web.backend.main
```
Akses web melalui browser di `http://127.0.0.1:18420`.

---

## 🧪 Menjalankan Automated Unit Tests

Suite pengujian otomatis mencakup verifikasi sanitasi path traversal, validasi magic bytes & decompression bomb, enkripsi settings, SQLite history manager, dan rate limiter:

```powershell
.\venv\Scripts\pytest tests\ -v
```

---

## 📦 Build & Distribusi

Tersedia script PowerShell di folder `scripts/`:

- **Build Desktop Standalone (.exe)**:
  ```powershell
  .\scripts\build_desktop.ps1
  ```
  Hasil tersimpan di `dist\LumieTL\`.

- **Build Web Distribution**:
  ```powershell
  .\scripts\build_web.ps1
  ```

- **Build Inno Setup Installer**:
  ```powershell
  .\scripts\build_installer.ps1
  ```
  Menghasilkan installer installer tunggal: `dist\LumieTL_Setup_v1.0.0.exe`.

---

## 🛡 Lisensi
Dilisensikan di bawah [MIT License](LICENSE).
