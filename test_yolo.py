# test_yolo.py
from ultralytics import YOLO
import cv2

# Load model
model = YOLO("yolov8n.pt")

# Test on an image
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

if ret:
    results = model(frame)[0]
    print(f"Detections found: {len(results.boxes) if results.boxes else 0}")
    
    for box in results.boxes:
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = model.names[cls]
        print(f"  - {label}: {conf:.2f}")
else:
    print("Camera error")

cap.release()