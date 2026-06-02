from ultralytics import YOLO

def train():
    model = YOLO("yolov8n.pt") 

    # Ubah bagian ini sesuai dengan lokasi folder yang muncul di VS Code kamu
    model.train(
        data="data/data.yaml", 
        epochs=50,             
        imgsz=640              
    )

if __name__ == "__main__":
    train()