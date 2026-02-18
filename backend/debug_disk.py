import psutil
import subprocess
import re
import time

def test_psutil():
    print("--- PSUTIL DISK IO COUNTERS ---")
    try:
        counters = psutil.disk_io_counters(perdisk=True)
        print(f"Counters: {counters}")
        return counters
    except Exception as e:
        print(f"Psutil Error: {e}")
        return None

def test_wmic():
    print("\n--- WMIC MAPPING ---")
    cmd = ["wmic", "path", "Win32_LogicalDiskToPartition", "get", "Antecedent,Dependent"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Return Code: {proc.returncode}")
        print("Output:")
        print(proc.stdout)
        
        mapping = {}
        for line in proc.stdout.splitlines():
            if "Disk #" in line and "Partition #" in line:
                match = re.search(r'Disk #(\d+).*DeviceID="([A-Z]:)"', line)
                if match:
                    disk_idx = match.group(1)
                    drive_letter = match.group(2)
                    p_drive = f"PhysicalDrive{disk_idx}"
                    if p_drive not in mapping:
                        mapping[p_drive] = []
                    mapping[p_drive].append(drive_letter)
                    print(f"Matched: {p_drive} -> {drive_letter}")
        print(f"Final Mapping: {mapping}")
        return mapping
    except Exception as e:
        print(f"WMIC Error: {e}")
        return None

if __name__ == "__main__":
    test_psutil()
    test_wmic()
