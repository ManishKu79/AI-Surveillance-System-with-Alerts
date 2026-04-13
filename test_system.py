import cv2
from smart_face_tracker import SmartFaceTracker

def main():
    tracker = SmartFaceTracker()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Camera error")
        return
    
    print("System Ready!")
    print("Press ESC to exit")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Initialize faces as empty list
        faces = []
        
        # Detect and recognize every 3 frames (better performance)
        if frame_count % 3 == 0:
            faces = tracker.detect_and_recognize(frame)
        
        # Draw results
        for name, (x1, y1, x2, y2) in faces:
            # Green for known, Red for unknown
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            
            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw name background
            (text_w, text_h), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x1, y1 - text_h - 8), (x1 + text_w + 8, y1), color, -1)
            
            # Draw name
            cv2.putText(frame, name, (x1 + 4, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show info
        cv2.putText(frame, f"Faces: {len(faces)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.imshow("Face Recognition System", frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()