import psutil
from logger import logger

def list_partitions():
    """
    Returns a list of disk partitions.
    """
    try:
        # 'all=True' to include network drives (SMB) which are usually excluded by 'all=False' on Windows.
        parts = psutil.disk_partitions(all=True)
        if not parts:
            logger.warning("psutil.disk_partitions(all=True) returned no partitions.")
        return parts
    except Exception as e:
        logger.error(f"Error listing partitions: {e}")
        return []

def get_disk_usage(path):
    """
    Returns usage statistics for a given path.
    """
    try:
        return psutil.disk_usage(path)
    except Exception as e:
        print(f"Error getting disk usage for {path}: {e}")
        return None

def get_all_disk_space_info():
    """
    High-level function to get space info for all fixed and network partitions.
    """
    partitions = list_partitions()
    result = []
    
    seen_devices = set()
    
    for part in partitions:
        # Filter out CD-ROMs and empty fstypes
        if 'cdrom' in part.opts or part.fstype == '':
            continue
            
        # Avoid duplicate physical devices if possible or just list all partitions
        # Windows partitions are C:\, D:\ etc.
        
        usage = get_disk_usage(part.mountpoint)
        if usage:
            result.append({
                'device': part.device,
                'mountpoint': part.mountpoint,
                'fstype': part.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            })
            
    return result

def get_custom_path_usage(paths):
    """
    Returns usage info for specific paths (e.g. SMB shares, NTFS mount points).
    """
    result = []
    for path in paths:
        try:
            usage = get_disk_usage(path)
            if usage:
                # Use path as device/mountpoint for custom paths
                result.append({
                    'device': 'Custom', # Label as Custom
                    'mountpoint': path,
                    'fstype': 'NTFS/SMB', # Generic or detect if possible
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
        except Exception:
            pass # Ignore invalid paths
            
    return result
