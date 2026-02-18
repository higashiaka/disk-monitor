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
            proc = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=5)
            
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
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
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

def get_network_io_rates():
    """
    Returns I/O rates for redirected (network) drives using Windows Performance Counters.
    Supports both mapped drive letters (Y:) and UNC paths (\\server\share).
    Includes localization-aware counter set detection.
    """
    rates = {}
    if not psutil.WINDOWS:
        return rates

    try:
        # Detect localized counter set name for 'Redirected Drive'
        # Default is English, but we'll try to find it if it fails
        counter_sets = ["\\Redirected Drive", "\\리디렉션된 드라이브"]
        active_set = None
        
        # Try to find which set exists
        for cs in counter_sets:
            check_cmd = ["powershell", "-NoProfile", "-Command", f"if (Get-Counter -ListSet '{cs.strip('\\')}' -ErrorAction SilentlyContinue) {{ '{cs}' }}"]
            res = subprocess.run(check_cmd, capture_output=True, text=True, timeout=3)
            if res.stdout.strip():
                active_set = res.stdout.strip()
                break
        
        if not active_set:
            # Last resort: try to find any set that looks like Redirected
            find_cmd = ["powershell", "-NoProfile", "-Command", "(Get-Counter -ListSet * | Where-Object { $_.CounterSetName -match 'Redirect|리디렉션' }).CounterSetName"]
            res = subprocess.run(find_cmd, capture_output=True, text=True, timeout=5)
            if res.stdout.strip():
                active_set = "\\" + res.stdout.splitlines()[0].strip()

        if not active_set:
            logger.warning("Could not find a valid 'Redirected Drive' counter set.")
            return rates

        # Use localized or detected set name
        read_counter = f"{active_set}(*)\\Read Bytes/sec"
        write_counter = f"{active_set}(*)\\Write Bytes/sec"
        
        # If Korean, counter names are also localized
        if "리디렉션" in active_set:
            read_counter = f"{active_set}(*)\\초당 읽기 바이트 수"
            write_counter = f"{active_set}(*)\\초당 쓰기 바이트 수"

        logger.info(f"Querying Network I/O using counters: {read_counter}, {write_counter}")
        
        ps_cmd = [
            "powershell", "-NoProfile", "-Command",
            f"Get-Counter -Counter '{read_counter}', '{write_counter}' -ErrorAction SilentlyContinue | "
            "Select-Object -ExpandProperty CounterSamples | "
            "Select-Object InstanceName, Path, CookedValue | "
            "ConvertTo-Json"
        ]
        
        proc = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=5)
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                data = json.loads(proc.stdout)
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    instance = item.get('InstanceName', '')
                    path = item.get('Path', '').lower()
                    val = item.get('CookedValue', 0)
                    
                    # Try to map instance to a key
                    drive_match = re.search(r'^([A-Z]:)', instance, re.I)
                    if drive_match:
                        key = drive_match.group(1).upper() + "\\"
                    else:
                        unc_match = re.search(r'(\\\\[^\s]+)', instance)
                        if unc_match:
                            key = unc_match.group(1)
                        elif "\\" in instance:
                            key = instance
                        else:
                            continue
                    
                    if key not in rates:
                        rates[key] = {'read_bytes_sec': 0, 'write_bytes_sec': 0}
                    
                    if 'read bytes/sec' in path or '읽기 바이트' in path:
                        rates[key]['read_bytes_sec'] = float(val)
                    elif 'write bytes/sec' in path or '쓰기 바이트' in path:
                        rates[key]['write_bytes_sec'] = float(val)
                        
                if rates:
                    logger.info(f"Fetched Network I/O for: {list(rates.keys())}")
            except json.JSONDecodeError:
                logger.error("Failed to decode Network I/O JSON output")
                
    except Exception as e:
        logger.error(f"Error getting network I/O: {e}")
        
    return rates

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
                
    # Add Network I/O rates (SMB/Redirected Drives)
    try:
        net_rates = get_network_io_rates()
        for drive, net_data in net_rates.items():
            # If we don't already have data from psutil for this drive letter
            # (which is usually true for network drives as psutil only sees physical disks)
            if drive not in rates:
                rates[drive] = net_data
            else:
                # Merge if applicable, though usually network drives won't be in physical map
                rates[drive]['read_bytes_sec'] += net_data['read_bytes_sec']
                rates[drive]['write_bytes_sec'] += net_data['write_bytes_sec']
    except Exception as e:
        logger.error(f"Error merging network I/O: {e}")

    return rates
