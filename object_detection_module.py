from ultralytics import YOLO
import cv2
import numpy as np

class ObjectDetector:
    def __init__(self):
        print("Loading YOLO model...")
        self.model = YOLO("yolov8n.pt")
        self.process_every_n_frames = 3
        self.frame_counter = 0
        self.last_results = []
        self.confidence_threshold = 0.3
        
        # Label mapping for better display names
        self.label_mapping = {
            'cell phone': 'Smart Phone',
            'remote': 'electronic device',
            'mouse': 'electronic device',
            'keyboard': 'electronic device',
            'laptop': 'electronic device',
            'tv': 'electronic device',
            'clock': 'electronic device',
            'book': 'reading material',
            'bottle': 'container',
            'cup': 'container',
            'chair': 'furniture',
            'couch': 'furniture',
            'dining table': 'furniture',
            'potted plant': 'plant',
            'vase': 'decor',
        }
        
        print("YOLO model loaded successfully")

    def map_label(self, label):
        """Map YOLO label to more descriptive display name"""
        return self.label_mapping.get(label, label)

    def detect(self, frame):
        self.frame_counter += 1
        
        if self.frame_counter % self.process_every_n_frames != 0:
            return self.last_results
        
        try:
            results = self.model(frame, verbose=False, conf=self.confidence_threshold)[0]
            
            detections = []
            
            if results.boxes is not None:
                for box in results.boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    original_label = self.model.names[cls]
                    
                    # Apply mapping
                    display_label = self.map_label(original_label)
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    detections.append((display_label, conf, (x1, y1, x2, y2)))
            
            self.last_results = detections
            
            if len(detections) > 0:
                print(f"Detected: {[(d[0], f'{d[1]:.2f}') for d in detections]}")
            
            return detections
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []