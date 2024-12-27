# settings_module.py
import json

def save_settings(settings, file_path="settings.json"):
    try:
        with open(file_path, "w") as file:
            json.dump(settings, file, indent=4)
        return "Settings saved successfully."
    except Exception as e:
        return f"Error saving settings: {str(e)}"

def load_settings(file_path="settings.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        return f"Error loading settings: {str(e)}"
