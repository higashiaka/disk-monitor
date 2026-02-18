import psutil
import subprocess
import re
import time

def test_psutil():
    with open("debug_results.txt", "a") as f:
        f.write("--- PSUTIL DISK IO COUNTERS ---\n")
        try:
            counters = psutil.disk_io_counters(perdisk=True)
            f.write(f"Counters: {counters}\n")
        except Exception as e:
            f.write(f"Psutil Error: {e}\n")

def test_wmic():
    with open("debug_results.txt", "a") as f:
        f.write("\n--- WMIC MAPPING ---\n")
        cmd = ["wmic", "path", "Win32_LogicalDiskToPartition", "get", "Antecedent,Dependent"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            f.write(f"Return Code: {proc.returncode}\n")
            f.write("Output:\n")
            f.write(proc.stdout)
            
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
                        f.write(f"Matched: {p_drive} -> {drive_letter}\n")
            f.write(f"Final Mapping: {mapping}\n")
        except Exception as e:
            f.write(f"WMIC Error: {e}\n")

if __name__ == "__main__":
    with open("debug_results.txt", "w") as f:
        f.write(f"Debug run at {time.ctime()}\n")
    test_psutil()
    test_wmic()
