import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class AlertSystem:
    def __init__(self):
        # Telegram Configuration - Set these
        self.telegram_token = "8708527719:AAGB31-P8ivI7hZQAwSZ3r5SiA8K4YHZI3U"  # Leave empty to disable
        self.telegram_chat_id = "1459084103"
        
        # Email Configuration
        self.email_enabled = False
        self.sender_email = ""
        self.sender_password = ""
        self.receiver_email = ""
        
        # Alert cooldown
        self.last_alert_time = {}
        self.cooldown_seconds = 30
        
        # Check if configured
        self.telegram_enabled = bool(self.telegram_token and self.telegram_chat_id)
        if not self.telegram_enabled:
            print("ℹ️ Telegram alerts disabled. Configure token and chat_id to enable.")
        if not self.email_enabled:
            print("ℹ️ Email alerts disabled.")

    def send_telegram_message(self, message, image_path=None):
        if not self.telegram_enabled:
            return False
        
        try:
            current_time = datetime.now().timestamp()
            if "telegram" in self.last_alert_time:
                if current_time - self.last_alert_time["telegram"] < self.cooldown_seconds:
                    return False
            
            if image_path and os.path.exists(image_path):
                url = f"https://api.telegram.org/bot{self.telegram_token}/sendPhoto"
                with open(image_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {'chat_id': self.telegram_chat_id, 'caption': message}
                    response = requests.post(url, files=files, data=data, timeout=10)
            else:
                url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                data = {'chat_id': self.telegram_chat_id, 'text': message}
                response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"📱 Telegram alert sent!")
                self.last_alert_time["telegram"] = current_time
                return True
            else:
                print(f"Telegram error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Telegram error: {e}")
            return False

    def send_email_alert(self, subject, body, image_path=None):
        if not self.email_enabled:
            return False
        
        try:
            current_time = datetime.now().timestamp()
            if "email" in self.last_alert_time:
                if current_time - self.last_alert_time["email"] < self.cooldown_seconds:
                    return False
            
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            msg['Subject'] = f"[SURVEILLANCE] {subject}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                    msg.attach(img)
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email alert sent!")
            self.last_alert_time["email"] = current_time
            return True
            
        except Exception as e:
            print(f"Email error: {e}")
            return False

    def alert_unknown_face(self, name, image_path=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"🚨 UNKNOWN FACE DETECTED!\n\nTime: {timestamp}\nLocation: Camera 1\nStatus: Unauthorized person detected"
        self.send_telegram_message(message, image_path)
        self.send_email_alert("Unknown Face Detected", message, image_path)

    def alert_motion(self, image_path=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"⚠️ MOTION DETECTED!\n\nTime: {timestamp}\nLocation: Camera 1\nActivity detected in monitored area"
        self.send_telegram_message(message, image_path)
        self.send_email_alert("Motion Detected", message, image_path)

    def alert_object_detected(self, object_name, confidence, image_path=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"🔍 OBJECT DETECTED!\n\nObject: {object_name}\nConfidence: {confidence:.2f}\nTime: {timestamp}"
        
        critical_objects = ['knife', 'gun', 'scissors', 'fire', 'smoke']
        if object_name.lower() in critical_objects:
            self.send_telegram_message(f"⚠️ CRITICAL: {message}", image_path)
            self.send_email_alert(f"CRITICAL: {object_name} Detected", message, image_path)