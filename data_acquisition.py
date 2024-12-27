import os
import subprocess
from datetime import datetime

def run_adb_command(command, description):
    """
    Helper function to run ADB commands and log results.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return f"{description} completed successfully.\n{result.stdout.strip()}"
        else:
            return f"{description} failed.\n{result.stderr.strip()}"
    except Exception as e:
        return f"Error executing {description}: {str(e)}"

def acquire_data(output_dir, package_name=None):
    """
    Acquire additional data from the Android device, such as app databases,
    shared preferences, APKs, screenshots, and screen recordings.
    Files are saved with .bin or .img extensions and include timestamps.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    results = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Generate a timestamp for file names

    try:
        # General commands for data acquisition
        commands = {
            "List Features": ["adb", "shell", "pm", "list", "features"],
            "List Services": ["adb", "shell", "service", "list"],
            "Installed APKs": ["adb", "shell", "ls", "/data/app"],
            "Pre-installed APKs": ["adb", "shell", "ls", "/system/app"],
            "Encrypted Apps": ["adb", "shell", "ls", "/mnt/asec"],
        }

        if package_name:
            # Add commands specific to a package
            package_commands = {
                "App Databases": ["adb", "shell", "ls", f"/data/data/{package_name}/databases"],
                "Shared Preferences": ["adb", "shell", "ls", f"/data/data/{package_name}/shared_prefs"],
            }
            commands.update(package_commands)

        for key, command in commands.items():
            try:
                process = subprocess.run(command, capture_output=True, text=True)
                if process.returncode == 0:
                    result = process.stdout.strip()
                    results.append(f"{key}:\n{result}\n")
                    # Save output to a file with .bin extension
                    file_name = f"{key.replace(' ', '_').lower()}_{timestamp}.bin"
                    file_path = os.path.join(output_dir, file_name)
                    with open(file_path, "w") as f:
                        f.write(result)
                else:
                    results.append(f"{key}: Command failed with error {process.stderr.strip()}\n")
            except Exception as e:
                results.append(f"{key}: Error executing command - {str(e)}\n")

        # Capture a screenshot
        screenshot_path = os.path.join(output_dir, f"screenshot_{timestamp}.img")
        screenshot_command = f"adb shell screencap -p /sdcard/screenshot.png && adb pull /sdcard/screenshot.png {screenshot_path}"
        results.append(run_adb_command(screenshot_command, "Screenshot"))

        # Record screen for a fixed duration (e.g., 10 seconds)
        screen_record_path = os.path.join(output_dir, f"screen_record_{timestamp}.bin")
        screen_record_command = f"adb shell screenrecord --time-limit 10 /sdcard/screen_record.mp4 && adb pull /sdcard/screen_record.mp4 {screen_record_path}"
        results.append(run_adb_command(screen_record_command, "Screen Record"))

        return f"Data acquisition completed. Files saved in {output_dir}.\n" + "\n".join(results)

    except Exception as e:
        return f"Error acquiring data: {str(e)}"
