import subprocess
import json
import os
import psutil

diag_log = "network_diag_v2.txt"

def log(msg):
    print(msg)
    with open(diag_log, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

if os.path.exists(diag_log):
    os.remove(diag_log)

log("--- Starting Network I/O Diagnostic v2 ---")

# 1. psutil partitions
log("\n1. psutil.disk_partitions(all=True):")
try:
    parts = psutil.disk_partitions(all=True)
    for p in parts:
        log(f"Device: {p.device}, Mount: {p.mountpoint}, Fstype: {p.fstype}, Opts: {p.opts}")
except Exception as e:
    log(f"Error: {e}")

# 2. Redirected Drive Counters
log("\n2. Get-Counter '\\Redirected Drive(*)\\*':")
try:
    # Use a simpler command to just get the instance names
    cmd = ["powershell", "-NoProfile", "-Command", "Get-Counter -ListSet 'Redirected Drive' | Select-Object -ExpandProperty PathsWithInstances"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    log(proc.stdout)
except Exception as e:
    log(f"Error checking counter instances: {e}")

# 3. Check for UNC or SMB specifically in performance counters
log("\n3. Checking for specific SMB counters:")
try:
    cmd = ["powershell", "-NoProfile", "-Command", "Get-Counter -ListSet * | Where-Object { $_.CounterSetName -like '*SMB*' } | Select-Object CounterSetName"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    log(proc.stdout)
except Exception as e:
    log(f"Error: {e}")

log("\n--- Diagnostic Complete ---")
