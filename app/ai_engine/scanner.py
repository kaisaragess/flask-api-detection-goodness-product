import os
from inference_sdk import InferenceHTTPClient

class FruitScanner:
    def __init__(self):
        self.api_key = os.getenv("ROBOFLOW_API_KEY")
        if not self.api_key:
            print("WARNING: ROBOFLOW_API_KEY tidak ditemukan di .env!")
        
        self.client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=self.api_key or "DUMMY_KEY"
        )
        
        self.model_id = "apple-grading-sni/3"

    def scan(self, image_path):
        """
        Fungsi untuk menjalankan deteksi via Roboflow API.
        image_path: path ke file gambar yang akan di-scan.
        """
        detections = []
        
        if not self.api_key:
            print("ERROR: ROBOFLOW_API_KEY belum disetel!")
            return {"detections": []}

        try:
            # Panggil Roboflow SDK untuk model klasifikasi
            result = self.client.infer(image_path, model_id=self.model_id)
            
            # Model apple-grading-sni/3 mengembalikan dictionary classification
            predictions = result.get('predictions', {})
            
            # Cari prediksi dengan confidence paling tinggi (Top 1)
            best_label = "Anomali"
            best_conf = 0.0
            
            if isinstance(predictions, dict):
                for label, data in predictions.items():
                    conf = float(data.get('confidence', 0.0))
                    if conf > best_conf:
                        best_conf = conf
                        best_label = label
                        
            # Cek jika confidence terlalu rendah, maka anggap anomali
            if best_conf < 0.25:
                best_label = "Anomali"
                
            detections.append({
                "label": best_label,
                "confidence": best_conf,
                "box": [] # Tidak ada koordinat (ini klasifikasi)
            })

        except Exception as e:
            print(f"Error Roboflow Inference: {e}")
            
        # LOGIKA ANOMALI KOSONG:
        if len(detections) == 0:
            detections.append({
                "label": "Anomali",
                "confidence": 0.0,
                "box": []
            })
            
        return {
            "detections": detections
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    try:
        scanner = FruitScanner()
        # hasil = scanner.scan("data/train/images/contoh_buah.jpg")
        # print(hasil)
    except Exception as e:
        print(f"Error: {e}")