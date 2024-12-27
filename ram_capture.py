import os
import subprocess
import time

def capture_ram(output_dir):
    """Capture RAM on rooted devices (deprecated, use capture_root_ram instead)."""
    return capture_root_ram(output_dir)

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



def capture_root_ram(output_dir):
    """
    Capture a full memory dump from a rooted Android device.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Path for memory dump file
        ram_dump_path = os.path.join(output_dir, "ram_dump.img")  # Default to .img

        # Command to use `su` for root permissions and capture memory
        command = ["adb", "shell", "su", "-c", f"dd if=/dev/mem of=/sdcard/ram_dump.img bs=4096"]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            # Pull the RAM dump file from the device
            subprocess.run(["adb", "pull", "/sdcard/ram_dump.img", ram_dump_path], check=True)

            # If the file already exists, modify the name by adding a timestamp
            if os.path.exists(ram_dump_path):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                ram_dump_path = os.path.join(output_dir, f"ram_dump_{timestamp}.img")

            return f"Rooted RAM capture completed. RAM dump saved at {ram_dump_path}"
        else:
            return f"Error capturing rooted RAM: {result.stderr.strip()}"

    except Exception as e:
        return f"Error capturing rooted memory: {str(e)}"



def non_root_ram_capture(output_dir):
    """
    Capture accessible memory-related data from a non-rooted Android device.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []
    
    try:
        # Command outputs to capture
        commands = {
            "Device State": ["adb", "get-state"],
            "Serial Number": ["adb", "get-serialno"],
            "IMEI": ["adb", "shell", "dumpsys", "iphonesybinfo"],
            "Battery Status": ["adb", "shell", "dumpsys", "battery"],
            "TCP Connectivity": ["adb", "shell", "netstat"],
            "Process Status": ["adb", "shell", "ps"],
            "Screen Resolution": ["adb", "shell", "wm", "size"],
            "Current Activity": [
                "adb", "shell", "dumpsys", "window", "windows", 
                "|", "grep", "-E", "'mCurrentFocus|mFocusedApp'"
            ],
        }

        for key, command in commands.items():
            try:
                process = subprocess.run(command, capture_output=True, text=True)
                if process.returncode == 0:
                    result = process.stdout.strip()
                    results.append(f"{key}:\n{result}\n")
                    # Save output to a file
                    with open(os.path.join(output_dir, f"{key.replace(' ', '_').lower()}.txt"), "w") as f:
                        f.write(result)
                else:
                    results.append(f"{key}: Command failed with error {process.stderr.strip()}\n")
            except Exception as e:
                results.append(f"{key}: Error executing command - {str(e)}\n")

        return "Non-rooted RAM capture completed. Files saved in {output_dir}.\n" + "\n".join(results)
    
    except Exception as e:
        return f"Error capturing non-rooted RAM data: {str(e)}"

