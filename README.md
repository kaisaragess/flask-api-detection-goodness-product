# Zona Pangan Backend 🍎

Sistem backend untuk manajemen stok pangan berbasis AI. Sistem ini memproses hasil pemindaian (scanning) untuk memprediksi kesegaran bahan pangan.

## 🛠 Tech Stack
- **Framework:** Flask (Python)
- **AI Model:** YOLOv8 (Computer Vision)
- **Database:** MongoDB (atau sesuaikan dengan DB Anda)

## 🚀 Persiapan Awal
Pastikan Anda sudah menginstall Python 3.10+ dan Git.

1. **Clone Repo:**
   `git clone [link-repo-anda]`

2. **Setup Virtual Environment:**
   ```bash
   python -m venv venv
   # Aktifkan: venv\Scripts\activate (Windows)
3. **Install**
    pip install -r requirements.txt
4. **Download dataset**
    python download_dataset.py
5. **Melatih data**
    python train_model.py
6. **Hasil Training**
    Setelah proses training selesai, file model hasil training (biasanya best.pt) akan otomatis tersimpan di dalam folder runs/detect/train/weights/.
7. **Update Model**
    Salin file best.pt yang baru tersebut ke folder models/ agar sistem AI Anda menggunakan model yang lebih akurat.
8. **Jalankan perintah**
    python app.py