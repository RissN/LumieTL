# LumieTL

**Auto-translator untuk Manga, Manhwa, dan Manhua — versi Web self-hostable.**

Jalankan server secara lokal (localhost), akses via browser. Terjemahkan gambar manga secara otomatis menggunakan AI — deteksi teks, OCR, inpainting, dan terjemahan dalam satu pipeline.

---

## Fitur

- **Terjemahkan** — Upload gambar, pilih bahasa, lihat hasil before/after dengan slider
- **Batch Processing** — Terjemahkan puluhan gambar sekaligus, download sebagai ZIP
- **Multi-Engine** — Google Translate (gratis), DeepL, OpenAI GPT-4o
- **Multi-Bahasa** — Jepang, Korea, Mandarin → Indonesia, Inggris, Vietnam, Thailand
- **Riwayat** — Semua terjemahan tercatat di database lokal
- **Keamanan** — API key terenkripsi, rate limiting, CSRF protection
- **Self-Hosted** — Data 100% di mesin Anda, tidak ada cloud dependency

---

## Quick Start

### Prasyarat
- Python 3.11
- Node.js 20+ (untuk build frontend)

### 1. Clone & Setup

```bash
git clone https://github.com/your-repo/LumieTL.git
cd LumieTL

# Buat virtual environment
python3.11 -m venv venv        # Linux
py -3.11 -m venv venv          # Windows

# Aktifkan venv
source venv/bin/activate       # Linux
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt          # CPU (default)
# pip install -r requirements-gpu.txt   # GPU (CUDA 12.1)
```

### 2. Build Frontend

```bash
npm install
npm run build
```

### 3. Jalankan

```bash
# Linux
./start.sh

# Windows
start.bat
```

Buka **http://localhost:18420** di browser.

---

## Konfigurasi

### Environment Variables

| Variable | Default | Keterangan |
|---|---|---|
| `LUMIETL_PORT` | `18420` | Port server |
| `LUMIETL_AUTH_ENABLED` | `false` | Aktifkan Basic Auth |
| `LUMIETL_AUTH_USER` | `admin` | Username Basic Auth |
| `LUMIETL_AUTH_PASS` | _(kosong)_ | Password Basic Auth |

### API Keys

Masukkan API key via halaman **Pengaturan** di browser. Key disimpan terenkripsi di disk — tidak pernah ditampilkan kembali.

---

## Stack

| Layer | Teknologi |
|---|---|
| Backend | Python 3.11 + FastAPI + Uvicorn |
| Translation | manga-image-translator + PyTorch |
| Frontend | Vue 3 + Vite + TypeScript + Tailwind CSS v4 |
| Database | SQLite (built-in) |
| Keamanan | Fernet encryption, CSRF, rate limiting |

---

## License

MIT
