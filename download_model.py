from ultralytics import YOLO

def download_model():
    print("Downloading YOLOv8s model...")
    model = YOLO('yolov8s.pt')
    print("Model downloaded successfully!")

if __name__ == "__main__":
    download_model()