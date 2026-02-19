import psutil
import time
import subprocess
import re
import json
from logger import logger

def get_disk_io_raw():
    """
    Returns raw disk I/O counters for all disks.
    """
    try:
        counters = psutil.disk_io_counters(perdisk=True)
        if not counters:
            logger.warning("psutil.disk_io_counters() returned empty data.")
        return counters
    except Exception as e:
        logger.error(f"Error getting disk io counters: {e}")
        return {}

import subprocess
import re

DISK_MAP_CACHE = {}
LAST_MAP_UPDATE = 0
MAP_UPDATE_INTERVAL = 60 # Refresh map every 60s

def get_drive_map():
    """
    Returns a map of PhysicalDriveN -> [DriveLetter:, ...]
    e.g. {'PhysicalDrive0': ['C:', 'D:'], 'PhysicalDrive1': ['E:']}
    """
    global DISK_MAP_CACHE, LAST_MAP_UPDATE
    if time.time() - LAST_MAP_UPDATE < MAP_UPDATE_INTERVAL:
        return DISK_MAP_CACHE
        
    mapping = {}
    try:
        if psutil.WINDOWS:
            # Use PowerShell for more reliable mapping on modern Windows
            ps_cmd = [
                "powershell", "-NoProfile", "-Command",
                "Get-CimInstance Win32_LogicalDiskToPartition | "
                "Select-Object @{n='DiskIndex';e={($_.Antecedent -split '#')[1].Split(',')[0]}}, "
                "@{n='DriveLetter';e={($_.Dependent -split '\\\"')[1]}} | "
                "ConvertTo-Json"
            ]
            
            logger.info("Running PowerShell drive mapping...")
            # Use CREATE_NO_WINDOW to prevent console popup
            proc = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if proc.returncode == 0 and proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout)
                    items = data if isinstance(data, list) else [data]
                    
                    for item in items:
                        disk_idx = item.get('DiskIndex')
                        drive_letter = item.get('DriveLetter')
                        if disk_idx is not None and drive_letter:
                            # Normalize drive_letter to match psutil device paths (e.g. C: -> C:\)
                            if not drive_letter.endswith('\\'):
                                drive_letter += '\\'
                            
                            p_drive = f"PhysicalDrive{disk_idx}"
                            if p_drive not in mapping:
                                mapping[p_drive] = []
                            if drive_letter not in mapping[p_drive]:
                                mapping[p_drive].append(drive_letter)
                    logger.info(f"PowerShell mapped drives: {mapping}")
                except json.JSONDecodeError as je:
                    logger.error(f"JSON decode error in PowerShell output: {je}")
            else:
                logger.warning(f"PowerShell mapping failed. Return code: {proc.returncode}")

            # Fallback for wmic if PowerShell failed or returned nothing
            if not mapping:
                logger.info("Falling back to wmic for mapping...")
                cmd = ["wmic", "path", "Win32_LogicalDiskToPartition", "get", "Antecedent,Dependent"]
                # Use CREATE_NO_WINDOW to prevent console popup
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
                if proc.returncode == 0:
                    for line in proc.stdout.splitlines():
                        if "Disk #" in line and "Partition #" in line:
                            match = re.search(r'Disk #(\d+).*DeviceID="([A-Z]:)"', line)
                            if match:
                                disk_idx = match.group(1)
                                drive_letter = match.group(2)
                                # Normalize drive_letter to match psutil device paths (e.g. C: -> C:\)
                                if not drive_letter.endswith('\\'):
                                    drive_letter += '\\'
                                
                                p_drive = f"PhysicalDrive{disk_idx}"
                                if p_drive not in mapping:
                                    mapping[p_drive] = []
                                if drive_letter not in mapping[p_drive]:
                                    mapping[p_drive].append(drive_letter)
                    logger.info(f"WMIC mapped drives: {mapping}")

    except subprocess.TimeoutExpired:
        logger.error("Drive mapping timed out!")
    except Exception as e:
        logger.error(f"Error in drive mapping: {e}")
    
    # Secondary check: combine with psutil partitions to catch missed letters
    try:
        parts = psutil.disk_partitions(all=False)
        for p in parts:
            if 'cdrom' in p.opts or p.fstype == '': continue
            pass
    except Exception as e:
        logger.error(f"Error checking partitions: {e}")
        
    DISK_MAP_CACHE = mapping
    LAST_MAP_UPDATE = time.time()
    return mapping

def calculate_io_rate(prev_io, curr_io, interval):
    """
    Calculates read/write bytes per second.
    Args:
        prev_io: Previous disk I/O counters (dict).
        curr_io: Current disk I/O counters (dict).
        interval: Time interval in seconds between prev and curr.
    Returns:
        dict: {drive_letter_or_physical: {'read_bytes_sec': float, 'write_bytes_sec': float}}
    """
    rates = {}
    if not prev_io or not curr_io:
        return rates

    # Get map
    drive_map = get_drive_map() # {'PhysicalDrive0': ['C:', 'E:']}

    for disk_name, curr_stats in curr_io.items():
        if disk_name in prev_io:
            prev_stats = prev_io[disk_name]
            
            # Calculate delta
            read_bytes_delta = curr_stats.read_bytes - prev_stats.read_bytes
            write_bytes_delta = curr_stats.write_bytes - prev_stats.write_bytes
            
            # Calculate rate
            read_rate = read_bytes_delta / interval if interval > 0 else 0
            write_rate = write_bytes_delta / interval if interval > 0 else 0
            
            # Normalize disk_name (e.g., '0' -> 'PhysicalDrive0')
            norm_name = disk_name
            if disk_name.isdigit():
                norm_name = f"PhysicalDrive{disk_name}"
            
            mapped_drives = drive_map.get(norm_name, [])
            
            if mapped_drives:
                for drive in mapped_drives:
                     rates[drive] = {
                        'read_bytes_sec': read_rate,
                        'write_bytes_sec': write_rate
                    }
            
            # Always include Normalized name
            rates[norm_name] = {
                'read_bytes_sec': read_rate,
                'write_bytes_sec': write_rate
            }
            
            # Special case for 'Total' or similar strings from psutil if any
            if disk_name == '_Total':
                 rates['Total'] = {
                    'read_bytes_sec': read_rate,
                    'write_bytes_sec': write_rate
                }
                
    return rates
