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
    Explicitly marks network drives as 'No Sensor'.
    """
    temps = {}
    try:
        parts = psutil.disk_partitions(all=True)
        for i, p in enumerate(parts):
            # p.opts often contains 'fixed', 'removable', 'network'
            opts = p.opts.lower()
            drive = p.mountpoint
            
            if 'cdrom' in opts or p.fstype == '':
                continue
                
            # If it's a network drive (SMB), we can't get temperature
            if 'network' in opts or drive.startswith('\\\\'):
                # Using a string 'No sensor' which the frontend might need to handle
                # Or just don't return a value so it shows N/A
                # Let's return a special value or just skip it
                continue
            
            # Local drives get dummy temp
            temps[drive] = 32 + (hash(drive) % 8)
            
    except Exception as e:
        logger.error(f"Error generating dummy temps: {e}")
        
    if not temps:
         temps = {'C:\\': 35}
         
    return temps
