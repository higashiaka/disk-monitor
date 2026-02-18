import subprocess
import json
import os
import psutil

diag_log = "final_diag.txt"

def log(msg):
    print(msg)
    with open(diag_log, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

if os.path.exists(diag_log):
    os.remove(diag_log)

log("--- Starting Deep Network/SMB Diagnostic ---")

# 1. Check all disk partitions
log("\n1. All Partitions (psutil):")
try:
    for p in psutil.disk_partitions(all=True):
        log(f"Device: {p.device}, Mount: {p.mountpoint}, FSType: {p.fstype}, Opts: {p.opts}")
except Exception as e:
    log(f"Error: {e}")

# 2. List all Counter Sets to find localized name for 'Redirected Drive'
log("\n2. Searching for Counter Sets containing 'Redirected', 'SMB', or 'Redir':")
try:
    ps_cmd = "Get-Counter -ListSet * | Select-Object CounterSetName | ConvertTo-Json"
    proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=15)
    if proc.stdout.strip():
        sets = json.loads(proc.stdout)
        found = False
        for s in sets:
            name = s.get('CounterSetName', '')
            if any(x in name.lower() for x in ['redir', 'smb', 'network', '디스크', '리디렉션']):
                log(f"Matched Set: {name}")
                found = True
        if not found:
            log("No matches found in counter sets.")
    else:
        log("No output from Get-Counter -ListSet *")
except Exception as e:
    log(f"Error: {e}")

# 3. Try to get ANY counter output for the English name just in case
log("\n3. Testing Get-Counter for '\\Redirected Drive(*)\\*':")
try:
    ps_cmd = "Get-Counter -Counter '\\Redirected Drive(*)\\Read Bytes/sec' -ErrorAction Stop | Select-Object -ExpandProperty CounterSamples | Select-Object InstanceName | ConvertTo-Json"
    proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=10)
    log(proc.stdout if proc.stdout.strip() else "Empty results (No redirected drives found by this name)")
except Exception as e:
    log(f"Failed with English name: {e}")

log("\n--- Diagnostic End ---")
