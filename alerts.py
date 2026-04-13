alert_status = {"alert": False, "message": ""}

def send_alert(name=None, crowd=False):
    global alert_status

    if crowd:
        alert_status["alert"] = True
        alert_status["message"] = "🚨 Crowd detected!"
    elif name == "Unknown":
        alert_status["alert"] = True
        alert_status["message"] = "🚨 Unknown person!"

def get_alert():
    return alert_status

def reset_alert():
    alert_status["alert"] = False