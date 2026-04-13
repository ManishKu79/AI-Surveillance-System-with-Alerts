import cv2
from smart_face_tracker import SmartFaceTracker
from object_detection_module import ObjectDetector
from motion_detection_module import MotionDetector
from recorder import EvidenceRecorder
from alert_system import AlertSystem

def main():
    face_tracker = SmartFaceTracker()
    object_detector = ObjectDetector()
    motion_detector = MotionDetector()
    recorder = EvidenceRecorder()
    alert_system = AlertSystem()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Camera error")
        return

    frame_count = 0
    unknown_save_cooldown = 0
    motion_save_cooldown = 0

    print("=" * 60)
    print("AI SURVEILLANCE SYSTEM WITH ALERTS")
    print("=" * 60)
    print("Features:")
    print("  📸 Unknown faces: Auto-save + ALERT")
    print("  ⚠️ Motion detected: Auto-save + ALERT")
    print("  📱 Telegram alerts enabled (if configured)")
    print("  📧 Email alerts enabled (if configured)")
    print("  Press ESC to exit")
    print("=" * 60)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # FACE RECOGNITION
        faces = face_tracker.detect_and_recognize(frame)

        for name, (x1, y1, x2, y2) in faces:
            if name.startswith("Person_"):
                color = (255, 255, 0)
            elif name == "Unknown":
                color = (0, 0, 255)
                
                # Save and send alert for unknown face
                if unknown_save_cooldown == 0:
                    snapshot_path = recorder.save_snapshot(frame, "unknown_face", name, alert_sent=True)
                    alert_system.alert_unknown_face(name, snapshot_path)
                    unknown_save_cooldown = 50  # Wait 50 frames between alerts
            else:
                color = (0, 255, 0)
                # Optional: Log known faces without alert
                # recorder.save_snapshot(frame, "known_face", name)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # OBJECT DETECTION
        objects = object_detector.detect(frame)

        for label, conf, (x1, y1, x2, y2) in objects:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 100, 0), 2)
            cv2.putText(frame, f"{label}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 0), 1)
            
            # Alert for critical objects
            critical_objects = ['knife', 'scissors', 'gun']
            if label.lower() in critical_objects and frame_count % 30 == 0:
                snapshot_path = recorder.save_snapshot(frame, "critical_object", label)
                alert_system.alert_object_detected(label, conf, snapshot_path)

        # MOTION DETECTION with alert
        motion_detected = motion_detector.detect(frame)
        if motion_detected:
            cv2.putText(frame, "⚠️ MOTION DETECTED!", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if motion_save_cooldown == 0:
                snapshot_path = recorder.save_snapshot(frame, "motion", "detected", alert_sent=True)
                alert_system.alert_motion(snapshot_path)
                motion_save_cooldown = 30

        # Update cooldowns
        if unknown_save_cooldown > 0:
            unknown_save_cooldown -= 1
        if motion_save_cooldown > 0:
            motion_save_cooldown -= 1

        # Display status
        cv2.putText(frame, f"Faces: {len(faces)} | Objects: {len(objects)}", 
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("AI Surveillance - Alerts Active", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 50)
    print("SESSION COMPLETE")
    print("=" * 50)
    print("Check evidence folder for saved snapshots")
    print("Alerts were sent for unknown faces and motion")

if __name__ == "__main__":
    main()