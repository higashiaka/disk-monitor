import psutil
import time

def get_disk_io_raw():
    """
    Returns raw disk I/O counters for all disks.
    """
    try:
        return psutil.disk_io_counters(perdisk=True)
    except Exception as e:
        print(f"Error getting disk io counters: {e}")
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
        # Get logical disk to partition mapping
        # wmic path Win32_LogicalDiskToPartition get Antecedent,Dependent
        cmd = ["wmic", "path", "Win32_LogicalDiskToPartition", "get", "Antecedent,Dependent"]
        # Use shell=True for wmic on some systems or just list? wmic is deprecated but standard.
        # Check if we are on Windows?
        if psutil.WINDOWS:
             proc = subprocess.run(cmd, capture_output=True, text=True)
             if proc.returncode == 0:
                 for line in proc.stdout.splitlines():
                     # Example line: 
                     # \\DESKTOP\root\cimv2:Win32_DiskPartition.DeviceID="Disk #0, Partition #2"   \\DESKTOP\root\cimv2:Win32_LogicalDisk.DeviceID="C:"
                     if "Disk #" in line and "Partition #" in line:
                         match = re.search(r'Disk #(\d+).*DeviceID="([A-Z]:)"', line)
                         if match:
                             disk_idx = match.group(1)
                             drive_letter = match.group(2)
                             p_drive = f"PhysicalDrive{disk_idx}"
                             if p_drive not in mapping:
                                 mapping[p_drive] = []
                             mapping[p_drive].append(drive_letter)
    except FileNotFoundError:
        # wmic is missing on some Windows 11 versions (deprecated/optional feature)
        pass 
    except Exception as e:
        # print(f"Error mapping drives: {e}")
        pass
        
    # Manual fallback or check psutil partitions if wmic fails?
    # For now, rely on wmic.
    
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
            
            # Use mapped drive letters if available
            mapped_drives = drive_map.get(disk_name, [])
            
            if mapped_drives:
                for drive in mapped_drives:
                     # We assign the FULL physical disk io to each partition on it?
                     # Ideally we want per-partition but we don't have it.
                     # Assigning full disk IO to partitions is a reasonable approximation for "Activity on this drive"
                     rates[drive] = {
                        'read_bytes_sec': read_rate,
                        'write_bytes_sec': write_rate
                    }
            else:
                # Keep original key (PhysicalDriveN) just in case
                rates[disk_name] = {
                    'read_bytes_sec': read_rate,
                    'write_bytes_sec': write_rate
                }
                
    return rates
