import subprocess

def get_connected_devices(self):
    # Run the adb devices command
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        output = result.stdout.strip().splitlines()

        if len(output) < 2:
            return "No devices connected."
        
        devices = []
        for line in output[1:]:  # Skip the header line
            device_id = line.split()[0]
            devices.append(device_id)

        return devices if devices else "No devices connected."
    
    except FileNotFoundError:
        return "ADB not found. Please ensure it's installed and in your PATH."
    except Exception as e:
        return f"Error detecting devices: {e}"
