# LumieTL

**Auto-translator untuk Manga, Manhwa, dan Manhua — versi Web self-hostable.**

Jalankan server secara lokal (localhost), akses via browser. Terjemahkan gambar manga secara otomatis menggunakan AI — deteksi teks, OCR, inpainting, dan terjemahan dalam satu pipeline.

---

## Fitur

- **Terjemahkan** — Upload gambar, pilih bahasa, lihat hasil before/after dengan slider
- **Batch Processing** — Terjemahkan puluhan gambar sekaligus, download sebagai ZIP
- **Multi-Engine** — Google Translate (gratis), DeepL, OpenAI GPT-4o
- **Multi-Bahasa** — Jepang, Korea, Mandarin -> Indonesia, Inggris, Vietnam, Thailand
- **Riwayat** — Semua terjemahan tercatat di database lokal
- **Keamanan** — API key terenkripsi, rate limiting, CSRF protection
- **Self-Hosted** — Data 100% di mesin Anda, tidak ada cloud dependency

---

## Prasyarat Sistem

Sebelum memulai, pastikan perangkat Anda telah terinstall:
- **Python 3.11** (64-bit)
- **Node.js 20+** dan **npm** (untuk build frontend)
- **Git**

---

## Panduan Memulai

### 1. Clone Repository

```bash
git clone https://github.com/RissN/LumieTL.git
cd LumieTL
```

### 2. Setup Lingkungan (Hanya Perlu Dilakukan Sekali)

#### Windows:

1. Buat virtual environment Python:
   ```powershell
   py -3.11 -m venv venv
   ```
2. Aktifkan virtual environment:
   ```powershell
   .\venv\Scripts\activate
   ```
3. Install dependensi Python:
   ```powershell
   # Versi CPU (default):
   pip install -r requirements.txt

   # ATAU versi GPU (jika memiliki kartu grafis NVIDIA dengan CUDA 12.1):
   # pip install -r requirements-gpu.txt
   ```
4. Install dependensi frontend dan kompilasi:
   ```powershell
   npm install
   npm run build
   ```

#### Linux / macOS:

1. Buat virtual environment Python:
   ```bash
   python3.11 -m venv venv
   ```
2. Aktifkan virtual environment:
   ```bash
   source venv/bin/activate
   ```
3. Install dependensi Python:
   ```bash
   # Versi CPU (default):
   pip install -r requirements.txt

   # ATAU versi GPU (CUDA 12.1):
   # pip install -r requirements-gpu.txt
   ```
4. Beri izin eksekusi skrip dan kompilasi frontend:
   ```bash
   chmod +x start.sh
   npm install
   npm run build
   ```

---

## Cara Menjalankan

### Cara Praktis (Rekomendasi)

- **Windows**: Double-click berkas `start.bat` di File Explorer, atau jalankan via terminal:
  ```powershell
  .\start.bat
  ```
  *(Skrip akan otomatis membuka browser ke http://localhost:18420 dan menjalankan server)*

- **Linux**: Jalankan berkas skrip di terminal:
  ```bash
  ./start.sh
  ```

Buka peramban (browser) dan akses: **http://localhost:18420**

### Cara Manual

Jika ingin menjalankan server secara manual melalui terminal:

```bash
# Windows
.\venv\Scripts\activate
uvicorn main:app --host 127.0.0.1 --port 18420

# Linux
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 18420
```

---

## Mode Pengembangan (Development)

Gunakan mode ini jika Anda ingin memodifikasi source code dengan fitur hot-reload:

1. **Terminal 1 — Backend (Auto-reload):**
   ```bash
   # Aktifkan venv terlebih dahulu
   uvicorn main:app --host 127.0.0.1 --port 18420 --reload
   ```

2. **Terminal 2 — Frontend (Vite HMR):**
   ```bash
   npm run dev
   ```
   Akses frontend pengembangan di **http://localhost:5173**. Permintaan API akan otomatis di-proxy ke backend di port 18420.

---

## Konfigurasi

### Environment Variables

| Variable | Default | Keterangan |
|---|---|---|
| `LUMIETL_PORT` | `18420` | Port server lokal |
| `LUMIETL_AUTH_ENABLED` | `false` | Aktifkan HTTP Basic Auth |
| `LUMIETL_AUTH_USER` | `admin` | Username Basic Auth |
| `LUMIETL_AUTH_PASS` | *(kosong)* | Password Basic Auth |

### API Keys

Masukkan API key untuk DeepL atau OpenAI GPT-4o melalui menu **Pengaturan** di peramban web. Kunci disimpan dalam format terenkripsi di penyimpanan lokal dan tidak pernah dibagikan ke server eksternal selain penyedia API terkait.

---

## Stack Teknologi

| Layer | Teknologi |
|---|---|
| Backend | Python 3.11 + FastAPI + Uvicorn |
| Translation Engine | manga-image-translator + PyTorch |
| Frontend | Vue 3 + Vite + TypeScript + Tailwind CSS v4 |
| Database | SQLite (built-in) |
| Keamanan | Fernet encryption, CSRF protection, Rate limiting |

---

## License

MIT
