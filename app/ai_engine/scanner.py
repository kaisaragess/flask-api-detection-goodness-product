import os
from inference_sdk import InferenceHTTPClient

class FruitScanner:
    def __init__(self):
        self.api_key = os.getenv("ROBOFLOW_API_KEY")
        if not self.api_key:
            print("WARNING: ROBOFLOW_API_KEY tidak ditemukan di .env!")
        
        self.client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=self.api_key or "DUMMY_KEY"
        )
        
        # Ganti dengan versi model Anda di Roboflow jika bukan versi 1
        self.model_id = "apple-grading-sni/1"

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
            # Confidence 0.01 agar menangkap semua prediksi sekecil apapun (mirip config lokal kita)
            result = self.client.infer(image_path, model_id=self.model_id, confidence=0.01)
            predictions = result.get('predictions', [])
            
            for pred in predictions:
                label = pred.get('class', 'Unknown')
                conf = float(pred.get('confidence', 0.0))
                
                # Inference API mengembalikan x_center, y_center, width, height
                x_center = float(pred.get('x', 0))
                y_center = float(pred.get('y', 0))
                width = float(pred.get('width', 0))
                height = float(pred.get('height', 0))
                
                x1 = x_center - (width / 2)
                y1 = y_center - (height / 2)
                x2 = x_center + (width / 2)
                y2 = y_center + (height / 2)

                if conf < 0.25:
                    label = "Anomali"

                detections.append({
                    "label": label,
                    "confidence": conf,
                    "box": [x1, y1, x2, y2]
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