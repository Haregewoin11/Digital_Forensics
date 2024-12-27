import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,QGroupBox,
    QPushButton, QLabel, QTextEdit, QFileDialog, QComboBox,QProgressBar,QHBoxLayout,QRadioButton
)
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import QThread, pyqtSignal,Qt


# Import all modules
from ram_capture import non_root_ram_capture, capture_root_ram,capture_ram
import data_acquisition
# import dump_analysis
import logs
import setting
from dump_analysis import analyze_ram_dump


class RAMCaptureWorker(QThread):
    result_signal = pyqtSignal(str)  # Signal to send results back to the main GUI

    def __init__(self, capture_type, output_dir, parent=None):
        super().__init__(parent)
        self.capture_type = capture_type
        self.output_dir = output_dir

    def run(self):
        """
        This method runs in the background when the thread starts.
        """
        try:
            if self.capture_type == "Non-Rooted":
                from ram_capture import non_root_ram_capture
                result = non_root_ram_capture(self.output_dir)
            elif self.capture_type == "Rooted":
                from ram_capture import capture_root_ram
                result = capture_root_ram(self.output_dir)
            else:
                result = "Invalid capture type selected."
        except Exception as e:
            result = f"Error capturing RAM: {str(e)}"

        # Emit the result back to the main thread
        self.result_signal.emit(result)



class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mobile Device Digital Forensics")
        self.setWindowIcon(QIcon("icon.png"))  # Add a custom icon file
        self.setGeometry(150, 150, 850, 650)

        self.init_ui()

    def init_ui(self):
        # Main container with tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setStyleSheet("""
    QTabBar::tab {
        font-size: 14px;
        padding: 10px 20px; /* Add padding for spacing inside each tab */
        margin: 2px; /* Add margin between tabs */
    }
    QTabBar::tab:selected {
        background-color: #D3D3D3; /* Highlight for selected tab */
    }
    QTabBar::tab:hover {
        background-color: #E8E8E8; /* Highlight on hover */
    }
""")

        # Add tabs for each module
        self.tabs.addTab(self.create_home_tab(), "Home")
        self.tabs.addTab(self.create_ram_capture_tab(), "RAM Capture")
        self.tabs.addTab(self.create_data_acquisition_tab(), "Data Acquisition")
        self.tabs.addTab(self.create_analysis_tab(), "Analysis")
        self.tabs.addTab(self.create_logs_tab(), "Logs")
        self.tabs.addTab(self.create_settings_tab(), "Settings")

    
    def create_home_tab(self):
        home_tab = QWidget()
        layout = QVBoxLayout()

    # Title Section
        title_label = QLabel("Android Device RAM Capturing ")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

    # Description Section
        description_group = QGroupBox("About the Tool")
        description_layout = QVBoxLayout()

        description_label = QLabel(
           
         "<p>This tool is a beginner-friendly Android Forensics application designed to empower forensic investigators by enabling them to capture, analyze, and acquire data from Android devices with ease. Developed with a focus on usability and accessibility.</p>"
    )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignJustify)
        description_layout.addWidget(description_label)

        description_group.setLayout(description_layout)
        layout.addWidget(description_group)

    # Purpose and Vision Section
        purpose_group = QGroupBox("Purpose and Vision")
        purpose_layout = QVBoxLayout()

        purpose_text = QLabel(
        "<p><strong>Purpose:</strong> This application is proudly created by a beginner developer to showcase the potential of software innovations originating from our community. It promotes the development and usage of locally crafted security tools.</p>"
    )
        purpose_text.setWordWrap(True)
        purpose_layout.addWidget(purpose_text)

        vision_text = QLabel(
        "<p><strong>Vision:</strong> By fostering the growth of local talent in technology, this tool aspires to inspire future advancements in digital forensics and cybersecurity in our country.</p>"
    )
        vision_text.setWordWrap(True)
        purpose_layout.addWidget(vision_text)

        purpose_group.setLayout(purpose_layout)
        layout.addWidget(purpose_group)
 
    # Steps for Usage Section
        steps_group = QGroupBox("Steps to Use")
        steps_layout = QVBoxLayout()

        steps_label = QLabel(
        "<ol>"
        "<li>Ensure ADB (Android Debug Bridge) is installed and added to your system's PATH.</li>"
        "<li>Connect your Android device via USB and enable USB Debugging on the device.</li>"
        "<li>Click the <strong>Detect Connected Devices</strong> button to verify the connection.</li>"
        "<li>Navigate to the RAM Capture tab and choose the capture method (Rooted/Non-Rooted).</li>"
        "<li>Select the output directory and start the RAM capture process.</li>"
        "<li>Use the Analysis tab to analyze captured RAM dumps for further insights.</li>"
        "<li>Visit the Logs tab to view detailed actions performed by the application.</li>"
        "<li>Customize application settings from the Settings tab as needed.</li>"
        "</ol>"
    )
        steps_label.setWordWrap(True)
        steps_layout.addWidget(steps_label)

        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)

    # Detect Devices Section
        detect_group = QGroupBox("Device Detection")
        detect_layout = QVBoxLayout()

        detect_button = QPushButton("Detect Connected Devices")
        detect_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        detect_button.setFont(QFont("Arial", 12))
        detect_button.clicked.connect(self.display_connected_devices)
        detect_layout.addWidget(detect_button)

        self.device_label = QLabel("<em>Connected devices will be shown here.</em>")
        self.device_label.setAlignment(Qt.AlignCenter)
        self.device_label.setStyleSheet("color: gray; font-style: italic;")
        detect_layout.addWidget(self.device_label)

        detect_group.setLayout(detect_layout)
        layout.addWidget(detect_group)

    # Add padding and spacing for better aesthetics
        layout.addStretch()
        layout.setSpacing(15)
        home_tab.setLayout(layout)
    
        return home_tab
    
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

    def display_connected_devices(self):
        devices = self.get_connected_devices()
        self.device_label.setText(f"Connected Devices: {devices}")

    def create_ram_capture_tab(self):
        ram_tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Select RAM Capture Method:")
        layout.addWidget(label)

        self.capture_type_dropdown = QComboBox()
        self.capture_type_dropdown.addItem("Non-Rooted")
        self.capture_type_dropdown.addItem("Rooted")
        layout.addWidget(self.capture_type_dropdown)

        output_dir = "captured_data"
        start_button = QPushButton("Capture RAM")
        start_button.clicked.connect(lambda: self.run_ram_capture(output_dir))
        layout.addWidget(start_button)

        ram_tab.setLayout(layout)
        return ram_tab


    

    def run_ram_capture(self, output_dir):
        capture_type = self.capture_type_dropdown.currentText()
        if capture_type == "Non-Rooted":
            result = non_root_ram_capture(output_dir)
            logs.log_action(result)
            self.update_logs(result)
            # result = non_root_ram_capture(output_dir)
        elif capture_type == "Rooted":
            result = capture_root_ram(output_dir)
        else:
            result = "Invalid RAM capture method selected."
        self.update_logs(result)

    # def run_ram_capture(self, output_dir):
    
    #     capture_type = self.capture_type_dropdown.currentText()  # Get selected capture type

    # # Initialize the worker thread
    #     self.ram_capture_worker = RAMCaptureWorker(capture_type, output_dir)
    #     self.ram_capture_worker.result_signal.connect(self.handle_ram_capture_result)

    # # Start the worker thread
    #     self.ram_capture_worker.start()

    # # Log a message indicating the process has started
    #     self.update_logs("RAM capture process started...")


    def handle_ram_capture_result(self, result):
    
    
    # Log the result
      logs.log_action(result)
      self.update_logs(result)

    # Optionally, display a popup or notification
      self.update_logs("RAM capture process completed.")


    def create_data_acquisition_tab(self):
        data_tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Extract Additional Data:")
        layout.addWidget(label)

        file_paths = ["/data/app", "/data/system"]
        start_button = QPushButton("Acquire Data")
        start_button.clicked.connect(lambda: self.run_data_acquisition("acquired_data", file_paths))
        layout.addWidget(start_button)

        data_tab.setLayout(layout)
        return data_tab

    def run_data_acquisition(self, output_dir, file_paths):
        result = data_acquisition.acquire_data(output_dir, file_paths)
        self.update_logs(result)

    def create_analysis_tab(self):
        analysis_tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Analyze Memory Dump:")
        layout.addWidget(label)

        open_button = QPushButton("Open File")
        open_button.clicked.connect(self.open_file)
        layout.addWidget(open_button)

        analysis_tab.setLayout(layout)
        return analysis_tab

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Memory Dump", "", "Image Files (*.img *.bin)")
        if file_name:
            output_dir = "analysis_results"  # Directory to save analysis results
            result = analyze_ram_dump(file_name, output_dir)
            logs.log_action(result)
            self.update_logs(result)


    def create_logs_tab(self):
        logs_tab = QWidget()
        layout = QVBoxLayout()

        logs_label = QLabel("Activity Logs:")
        layout.addWidget(logs_label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        logs_tab.setLayout(layout)
        return logs_tab

    def update_logs(self, message):
    
       self.log_area.append(message)


    def create_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Settings:")
        layout.addWidget(label)

        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(lambda: self.save_app_settings({"output_dir": "default_path"}))
        layout.addWidget(save_button)

        load_button = QPushButton("Load Settings")
        load_button.clicked.connect(self.load_app_settings)
        layout.addWidget(load_button)

        settings_tab.setLayout(layout)
        return settings_tab

    def save_app_settings(self, settings):
        result = setting.save_settings(settings)
        self.update_logs(result)

    def load_app_settings(self):
        settings = setting.load_settings()
        result = f"Loaded settings: {settings}"
        self.update_logs(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())   