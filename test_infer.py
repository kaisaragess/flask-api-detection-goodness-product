from inference_sdk import InferenceHTTPClient
import json

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="7BhqkUJyu0t9H39krypf"
)

print("Mencoba opsi 2: Inference Biasa (apple-ripeness-pj4d3/3)...")
try:
    result = client.infer("D:/Kuliah/semester4/ai-project/apple-6939451_1280.jpg", model_id="apple-ripeness-pj4d3/3")
    print("BERHASIL! Hasil deteksi:")
    print(json.dumps(result, indent=2)[:500] + "...(dipotong)")
except Exception as e:
    print("GAGAL:", e)
