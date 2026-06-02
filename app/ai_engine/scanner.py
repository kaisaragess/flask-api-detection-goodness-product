from ultralytics import YOLO
import os

class FruitScanner:
    def __init__(self):
        # Path ke model best.pt di folder app/models
        # Pastikan file best.pt memang ada di path ini
        self.model_path = os.path.join("app", "models", "best.pt")
        
        # Memuat model YOLO
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file tidak ditemukan di: {self.model_path}")
        
        self.model = YOLO(self.model_path)

    def scan(self, image_path):
        """
        Fungsi untuk menjalankan deteksi pada gambar.
        image_path: path ke file gambar yang akan di-scan.
        """
        # Menjalankan deteksi
        results = self.model.predict(source=image_path, conf=0.5)
        
        # Mengolah hasil menjadi format yang lebih mudah dibaca
        detections = []
        for result in results:
            for box in result.boxes:
                # Mengambil koordinat, confidence score, dan nama class
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = result.names[cls]
                
                detections.append({
                    "label": label,
                    "confidence": conf,
                    "box": [x1, y1, x2, y2]
                })
        
        return detections

# Contoh cara penggunaan jika ingin dites langsung
if __name__ == "__main__":
    try:
        scanner = FruitScanner()
        # Ganti dengan nama file gambar contoh di komputermu
        hasil = scanner.scan("data/train/images/contoh_buah.jpg")
        print(hasil)
    except Exception as e:
        print(f"Error: {e}")