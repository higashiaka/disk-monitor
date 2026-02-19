try:
    from pySMART import DeviceList
except ImportError:
    DeviceList = None

import platform
import psutil
from logger import logger
from disk_io import get_drive_map

def get_disk_temperatures():
    """
    Returns a dictionary of disk temperatures.
    Requires Admin privileges and smartctl on Windows.
    Returns:
        dict: {drive_letter: temperature_celsius}
    """
    temps = {}
    if not DeviceList:
        return temps

    try:
        drive_map = get_drive_map()
        devices = DeviceList()
        if not devices:
            # Check if any mapped drive is actually a network/SMB drive
            # Network drives won't show up in pySMART DeviceList
            return {}

        for dev in devices.devices:
            temp = dev.temperature
            if temp:
                dev_name = dev.name
                if dev_name.startswith('pd'):
                    norm_name = f"PhysicalDrive{dev_name[2:]}"
                else:
                    norm_name = dev_name
                
                mapped_drives = drive_map.get(norm_name, [])
                if mapped_drives:
                    for drive in mapped_drives:
                        temps[drive] = temp
                else:
                    temps[norm_name] = temp
                
                logger.info(f"Disk {dev_name} ({norm_name}) temperature: {temp}C")
                
    except Exception as e:
        logger.error(f"Error getting disk temps: {e}")
        
    return temps

def get_dummy_temperatures():
    """
    Generates dummy temperatures for all active partitions.
    """
    temps = {}
    try:
        # Generate dummy temp for each fixed disk/partition found
        parts = psutil.disk_partitions(all=True)
        for i, p in enumerate(parts):
            if 'cdrom' in p.opts or p.fstype == '':
                continue
            
            # Use mountpoint (e.g. C:\) as key, same as frontend expects
            drive = p.mountpoint
            # Assign random-ish consistent temp
            temps[drive] = 32 + (hash(drive) % 8)
            
    except Exception as e:
        logger.error(f"Error generating dummy temps: {e}")
        
    if not temps:
         temps = {'C:\\': 35}
         
    return temps
