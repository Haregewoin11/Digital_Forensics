import os
import re
from datetime import datetime

def analyze_ram_dump(dump_path, output_dir):
    """
    Analyze a RAM dump to extract valuable forensic information, including processes,
    network connections, potential hidden data, and malicious patterns.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the raw dump file (RAM dump)
    try:
        with open(dump_path, 'rb') as f:
            ram_data = f.read()

        # Perform initial analysis
        analysis_results = []

        # Extract process information
        processes = extract_processes(ram_data)
        analysis_results.append(f"Processes found: {len(processes)}")
        analysis_results.append("\n".join(processes))

        # Extract active network connections
        network_connections = extract_network_connections(ram_data)
        analysis_results.append(f"Active network connections: {len(network_connections)}")
        analysis_results.append("\n".join(network_connections))

        # Search for hidden or encrypted data
        hidden_data = search_for_hidden_data(ram_data)
        analysis_results.append(f"Potential hidden data found: {len(hidden_data)}")
        analysis_results.append("\n".join(hidden_data))

        # Search for deleted file remnants
        deleted_files = search_for_deleted_files(ram_data)
        analysis_results.append(f"Deleted file remnants found: {len(deleted_files)}")
        analysis_results.append("\n".join(deleted_files))

        # Detect malicious patterns
        malicious_patterns = detect_malicious_patterns(ram_data)
        analysis_results.append(f"Malicious patterns detected: {len(malicious_patterns)}")
        analysis_results.append("\n".join(malicious_patterns))

        # Generate a summary report
        report_file = os.path.join(output_dir, f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(report_file, 'w') as report:
            report.write("\n".join(analysis_results))

        return f"RAM dump analysis complete. Report saved to {report_file}"

    except Exception as e:
        return f"Error analyzing RAM dump: {str(e)}"


def detect_malicious_patterns(ram_data):
    """
    Detect malicious patterns in the RAM data.
    """
    malicious_patterns = []
    try:
        # Define known malicious patterns or signatures
        signatures = {
            "Reverse Shell": rb"bash -i >& /dev/tcp/\d+\.\d+\.\d+\.\d+/\d+ 0>&1",
            "Keylogger": rb"KeyLogger",
            "Malware Signature 1": rb"malicious_payload",
            "Encoded Commands": rb"base64 -d",
            "Suspicious Script": rb"eval\(.+\)",
            "Unauthorized Network Activity": rb"curl http://|wget http://",
        }

        # Search for these patterns in the RAM data
        for name, pattern in signatures.items():
            matches = re.findall(pattern, ram_data)
            if matches:
                malicious_patterns.append(f"Detected {name}: {len(matches)} occurrences")
        
        return malicious_patterns
    except Exception as e:
        return [f"Error detecting malicious patterns: {str(e)}"]


def extract_processes(ram_data):
    """
    Extract process information from RAM data, looking for known signatures of processes.
    """
    processes = []
    try:
        process_pattern = re.compile(r"\x00([\w\s]+)\x00\s*(\d+)\s*")
        matches = process_pattern.findall(ram_data.decode(errors='ignore'))
        for match in matches:
            process_name, process_id = match
            processes.append(f"Process: {process_name.strip()}, PID: {process_id}")
        return processes
    except Exception as e:
        return [f"Error extracting processes: {str(e)}"]


def extract_network_connections(ram_data):
    """
    Extract active network connections from RAM data.
    """
    network_connections = []
    try:
        netstat_pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+:\d+)\s+(\d+\.\d+\.\d+\.\d+:\d+)\s+(ESTABLISHED|LISTEN)")
        matches = netstat_pattern.findall(ram_data.decode(errors='ignore'))
        for match in matches:
            local_ip, remote_ip, state = match
            network_connections.append(f"Connection: {local_ip} -> {remote_ip}, State: {state}")
        return network_connections
    except Exception as e:
        return [f"Error extracting network connections: {str(e)}"]


def search_for_hidden_data(ram_data):
    """
    Search for hidden data, such as encryption keys, passwords, or other sensitive information.
    """
    hidden_data = []
    try:
        hex_pattern = re.compile(r"\b([a-f0-9]{32,64})\b")
        base64_pattern = re.compile(r"[A-Za-z0-9+/=]{16,}")
        hex_matches = hex_pattern.findall(ram_data.decode(errors='ignore'))
        for match in hex_matches:
            hidden_data.append(f"Possible hex key: {match}")
        base64_matches = base64_pattern.findall(ram_data.decode(errors='ignore'))
        for match in base64_matches:
            hidden_data.append(f"Possible base64 key: {match}")
        return hidden_data
    except Exception as e:
        return [f"Error searching for hidden data: {str(e)}"]


def search_for_deleted_files(ram_data):
    """
    Search for remnants of deleted files in RAM.
    """
    deleted_files = []
    try:
        deleted_file_pattern = re.compile(r"/[^/]+/[A-Za-z0-9]+(?:\.[a-z]+)?")
        matches = deleted_file_pattern.findall(ram_data.decode(errors='ignore'))
        for match in matches:
            deleted_files.append(f"Possible deleted file: {match}")
        return deleted_files
    except Exception as e:
        return [f"Error searching for deleted files: {str(e)}"]
