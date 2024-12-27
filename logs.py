# logs_module.py
import datetime

def log_action(log_text, log_file="logs.txt"):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{timestamp} - {log_text}\n"
        with open(log_file, "a") as file:
            file.write(entry)
        return entry
    except Exception as e:
        return f"Error logging action: {str(e)}"
