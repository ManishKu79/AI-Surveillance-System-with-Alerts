import cv2
from deepface import DeepFace
import os
import tempfile
import numpy as np
from datetime import datetime

class SmartFaceTracker:
    def __init__(self):
        prototxt_path = "models/deploy.prototxt"
        model_path = "models/res10_300x300_ssd_iter_140000.caffemodel"
        
        # Check if model files exist
        if not os.path.exists(prototxt_path):
            print(f"Error: {prototxt_path} not found!")
        if not os.path.exists(model_path):
            print(f"Error: {model_path} not found!")
        
        self.face_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
        self.known_path = "known_faces"
        
        # Auto-registration
        self.unknown_face_cache = {}
        self.auto_register_threshold = 15
        self.face_id_counter = 1
        
        # Recognition cache
        self.recognition_cache = {}
        self.cache_duration = 30
        
        # Process every N frames
        self.process_every_n_frames = 5
        self.frame_counter = 0
        self.last_faces = []
        
        os.makedirs("saved_faces", exist_ok=True)
        os.makedirs(self.known_path, exist_ok=True)
        self.load_existing_faces()

    def load_existing_faces(self):
        for person_name in os.listdir(self.known_path):
            person_folder = os.path.join(self.known_path, person_name)
            if os.path.isdir(person_folder):
                print(f"✓ Loaded: {person_name}")

    def get_face_hash(self, face_img):
        try:
            small = cv2.resize(face_img, (32, 32))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            return str(np.mean(gray)) + str(np.std(gray))
        except:
            return str(datetime.now().timestamp())

    def detect_faces_fast(self, frame, conf_threshold=0.5):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.face_net.setInput(blob)
        detections = self.face_net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 > x1 and y2 > y1 and (x2-x1) > 60:
                    faces.append((x1, y1, x2, y2))
        return faces

    def recognize_face_fast(self, face_img, face_hash):
        if face_hash in self.recognition_cache:
            name, frame_num = self.recognition_cache[face_hash]
            if self.frame_counter - frame_num < self.cache_duration:
                return name
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                temp_path = tmp.name
                face_resized = cv2.resize(face_img, (160, 160))
                cv2.imwrite(temp_path, face_resized)

            result = DeepFace.find(
                img_path=temp_path,
                db_path=self.known_path,
                enforce_detection=False,
                silent=True,
                model_name='Facenet',
                distance_metric='cosine'
            )
            os.unlink(temp_path)

            if result and len(result) > 0 and len(result[0]) > 0:
                best_match = result[0].iloc[0]
                distance = best_match['distance']
                if distance < 0.45:
                    identity_path = best_match['identity']
                    name = os.path.basename(os.path.dirname(identity_path))
                    self.recognition_cache[face_hash] = (name, self.frame_counter)
                    return name
            
            if face_hash in self.unknown_face_cache:
                self.unknown_face_cache[face_hash]['count'] += 1
                if self.unknown_face_cache[face_hash]['count'] >= self.auto_register_threshold:
                    if 'saved' not in self.unknown_face_cache[face_hash]:
                        new_name = self.register_new_face(face_img)
                        self.unknown_face_cache[face_hash]['saved'] = True
                        self.recognition_cache[face_hash] = (new_name, self.frame_counter)
                        return new_name
            else:
                self.unknown_face_cache[face_hash] = {
                    'count': 1,
                    'first_seen': self.frame_counter,
                    'best_face': face_img.copy()
                }
            
            return "Unknown"
        except Exception:
            return "Unknown"

    def register_new_face(self, face_img):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        auto_name = f"Person_{self.face_id_counter}"
        
        person_folder = os.path.join(self.known_path, auto_name)
        os.makedirs(person_folder, exist_ok=True)
        
        face_path = os.path.join(person_folder, f"{auto_name}_{timestamp}.jpg")
        cv2.imwrite(face_path, face_img)
        
        print(f"✅ AUTO-REGISTERED: {auto_name}")
        self.face_id_counter += 1
        return auto_name

    def detect_and_recognize(self, frame):
        self.frame_counter += 1
        
        # Only process face detection every N frames
        if self.frame_counter % self.process_every_n_frames == 0 or self.frame_counter == 1:
            self.last_faces = self.detect_faces_fast(frame, conf_threshold=0.5)
        
        results = []
        
        for (x1, y1, x2, y2) in self.last_faces:
            if y2 <= y1 or x2 <= x1:
                continue
                
            face_img = frame[y1:y2, x1:x2]
            if face_img.size == 0:
                continue
                
            face_hash = self.get_face_hash(face_img)
            name = self.recognize_face_fast(face_img, face_hash)
            results.append((name, (x1, y1, x2, y2)))
        
        return results