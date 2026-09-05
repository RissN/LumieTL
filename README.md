# LumieTL

LumieTL adalah perangkat lunak penerjemah otomatis (auto-translator) untuk manga, manhwa, dan manhua berbasis deep learning OCR dan machine translation. Proyek ini dibangun dengan arsitektur Web Monolith yang menggabungkan antarmuka Single Page Application (SPA) berbasis Vue 3 + TypeScript dan backend berkinerja tinggi berbasis FastAPI + Python Core.

---

## Fitur Utama

- **Deteksi Teks dan OCR Presisi Tinggi**: Menggunakan model deep learning berbasis ONNX Runtime untuk mendeteksi gelembung teks manga/manhwa/manhua secara otomatis dan mengekstrak teks dengan orientasi horizontal maupun vertikal.
- **Dukungan Multi-Bahasa dan Mesin Penerjemah**:
  - **Bahasa Sumber**: Deteksi Otomatis, Jepang (JPN), Korea (KOR), Mandarin Simplified (CHS), Mandarin Traditional (CHT).
  - **Bahasa Target**: Indonesia (ID), Inggris (EN), Vietnam (VI), Thailand (TH).
  - **Pilihan Engine**: Google Translate, DeepL API, dan OpenAI GPT-4o API.
- **Penerjemahan Gambar Tunggal (Single Image)**:
  - Antarmuka visual interaktif dengan slider perbandingan Sebelum dan Sesudah (Before/After).
  - Kontrol zoom dan pan untuk inspeksi detail gambar beresolusi tinggi.
  - Opsi ekspor langsung ke format berkas gambar atau papan klip.
- **Penerjemahan Batch (Batch Processing)**:
  - Pemrosesan sekaligus untuk seluruh halaman dalam folder atau chapter.
  - Antrean cerdas dengan indikator status berkas, estimasi durasi, dan progress bar.
- **Keamanan dan Perlindungan Data**:
  - Penyimpanan kunci API terenkripsi menggunakan cipher Fernet pada sistem berkas terlindungi.
  - Validasi berkas berbasis magic bytes serta mitigasi ketat terhadap ancaman image decompression bomb dan path traversal.
  - Pembatasan laju permintaan (rate limiting) terintegrasi pada middleware server dan engine.
- **Penyimpanan Riwayat Terintegrasi**:
  - Riwayat penerjemahan disimpan otomatis di basis data SQLite lokal untuk audit dan peninjauan ulang.

---

## Struktur Direktori Proyek

```
LumieTL/
├── backend/                  # Server FastAPI & REST API endpoints
│   ├── api/                  # Routers: translate, models, history, settings
│   ├── middleware/           # Rate limiting & middleware autentikasi
│   ├── frontend_dist/        # Aset terkompilasi frontend Vue 3
│   └── main.py               # Entry point FastAPI & static SPA mounting
├── frontend/                 # Source code frontend Vue 3 + TypeScript
│   ├── src/                  # Komponen, Views, Router, Pinia store, Styles
│   ├── index.html            # Vite entry point
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Konfigurasi Vite & proxy API
├── core/                     # Shared Engine (Translator, ONNX Model Manager, SQLite, Rate Limiter)
├── security/                 # Keystore File & Kriptografi Pengaturan
├── utils/                    # Validasi berkas, pengolah gambar, rotasi log
├── tests/                    # Pengujian unit & integrasi otomatis
├── requirements.txt          # Dependensi Python terpadu
└── README.md                 # Dokumentasi proyek
```

---

## Panduan Menjalankan Aplikasi

### Prasyarat Sistem
- Python 3.11 (64-bit)
- Node.js versi 20 atau lebih baru (dan npm)
- Git

---

### 1. Setup Virtual Environment & Dependensi Python

Buka terminal di direktori proyek, lalu buat dan aktifkan virtual environment:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### 2. Kompilasi Frontend Vue 3

Kompilasi aset antarmuka frontend (cukup dijalankan satu kali saat setup awal atau setelah memperbarui kode di direktori `frontend`):

```powershell
cd frontend
npm install
npm run build
cd ..
```

Hasil kompilasi akan otomatis ditempatkan ke dalam `backend/frontend_dist/` dan siap disajikan langsung oleh Uvicorn.

---

### 3. Menjalankan Server dengan Uvicorn

Jalankan server aplikasi menggunakan Uvicorn:

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 18420
```

Setelah server aktif, buka peramban (browser) dan akses alamat berikut:
```
http://127.0.0.1:18420
```

---

### Mode Pengembangan (Development)

Jika Anda sedang aktif mengembangkan atau memodifikasi kode:

1. **Backend dengan Auto-Reload**:
   ```powershell
   uvicorn backend.main:app --host 127.0.0.1 --port 18420 --reload
   ```

2. **Frontend dengan Hot-Module Replacement (HMR)**:
   ```powershell
   cd frontend
   npm run dev
   ```
   Akses `http://localhost:5173`. Semua permintaan API akan otomatis diarahkan oleh Vite ke server backend Uvicorn di port 18420.

---

## Pengujian Otomatis (Automated Tests)

Jalankan pengujian unit otomatis untuk memverifikasi fungsionalitas core, enkripsi, dan API endpoint:

```powershell
.\venv\Scripts\pytest tests\ -v
```

---

## Pemaketan Distribusi (Build Release)

Untuk membuat paket rilis mandiri siap pakai:

```powershell
.\scripts\build_web.ps1
```

Paket distribusi lengkap beserta skrip peluncur (`start.bat` & `start.sh`) akan terbentuk di direktori `release/LumieTL_Web`.
