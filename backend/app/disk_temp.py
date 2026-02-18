try:
    from pySMART import DeviceList
except ImportError:
    DeviceList = None

import platform

def get_disk_temperatures():
    """
    Returns a dictionary of disk temperatures.
    Requires Admin privileges and smartctl on Windows.
    Returns:
        dict: {disk_name: temperature_celsius}
    """
    temps = {}
    
    # Check if we are on Windows and have admin rights (simplified check)
    # real check is complex, so we just try-except
    
    try:
        # pySMART wraps smartctl. 
        # On Windows, it needs to run as Admin to access physical drives.
        devices = DeviceList()
        if not devices:
            return {}

        for dev in devices.devices:
            # dev.name might be /dev/sda or similar on Linux, 
            # on Windows it might be pd0, pd1 etc.
            # We need to map this to drive letters if possible, but that's hard.
            # For now, we use the model/serial as key or just the device name.
            
            # smartctl output parsing
            temp = dev.temperature
            if temp:
                temps[dev.name] = temp
                
    except Exception as e:
        # Silent fail or log
        # print(f"Error getting disk temps: {e}")
        pass
        
    return temps

# For development/testing without Admin, we might want dummy data
def get_dummy_temperatures():
    import psutil
    temps = {}
    try:
        # Generate dummy temp for each fixed disk found
        parts = psutil.disk_partitions(all=False) # Local only
        for i, p in enumerate(parts):
            if 'cdrom' in p.opts or p.fstype == '': continue
            # Assign random-ish temp based on index
            temps[p.device] = 35 + i * 2 # e.g. C:\ -> 35
            
            # Also add PhysicalDriveN key just in case
            # temps[f"PhysicalDrive{i}"] = 35 + i
    except:
        pass
        
    if not temps:
         temps = {'C:\\': 35, 'D:\\': 38} # Fallback
         
    return temps
