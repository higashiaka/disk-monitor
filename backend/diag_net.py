import subprocess
import json
import os

diag_log = "network_diag.txt"

def log(msg):
    with open(diag_log, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

if os.path.exists(diag_log):
    os.remove(diag_log)

log("--- Starting Network I/O Diagnostic ---")

# 1. Check PS Drives
log("\n1. PowerShell Drives:")
try:
    cmd = ["powershell", "-NoProfile", "-Command", "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Root, DisplayRoot | ConvertTo-Json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log(proc.stdout)
except Exception as e:
    log(f"Error checking drives: {e}")

# 2. Check Redirected Drive Counter Set
log("\n2. Counter Set 'Redirected Drive':")
try:
    cmd = ["powershell", "-NoProfile", "-Command", "Get-Counter -ListSet 'Redirected Drive' | Select-Object -ExpandProperty Counter | ConvertTo-Json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log(proc.stdout)
except Exception as e:
    log(f"Error checking counter set: {e}")

# 3. Check ALL Counter Sets (Search for redirected)
log("\n3. Searching for 'Redirected' or 'Network' in all sets:")
try:
    cmd = ["powershell", "-NoProfile", "-Command", "Get-Counter -ListSet * | Where-Object { $_.CounterSetName -like '*Redirected*' -or $_.CounterSetName -like '*Network*' } | Select-Object CounterSetName | ConvertTo-Json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log(proc.stdout)
except Exception as e:
    log(f"Error searching sets: {e}")

log("\n--- Diagnostic Complete ---")
