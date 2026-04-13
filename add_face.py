import cv2
import os

def add_face_manually():
    name = input("Enter person's name: ")
    
    # Create folder for this person
    person_folder = os.path.join("known_faces", name)
    os.makedirs(person_folder, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    print(f"Press SPACE to capture photo of {name}")
    print("Press ESC to cancel")
    
    photo_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.putText(frame, f"Adding: {name} - Press SPACE", (20, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Photos captured: {photo_count}", (20, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Add Face Manually", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            photo_count += 1
            filename = os.path.join(person_folder, f"{name}_{photo_count}.jpg")
            cv2.imwrite(filename, frame)
            print(f"✅ Saved: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n✅ Added {photo_count} photos of {name}")

if __name__ == "__main__":
    add_face_manually()