import sys
import os
import time

# Add parent dir to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import disk_io

def verify_io_retrieval():
    print("--- VERIFYING DISK I/O RETRIEVAL ---")
    
    # 1. Test raw counters
    raw = disk_io.get_disk_io_raw()
    print(f"Raw counters found for: {list(raw.keys())}")
    
    # 2. Test drive mapping
    mapping = disk_io.get_drive_map()
    print(f"Drive mapping: {mapping}")
    
    # 3. Test rate calculation
    print("Calculating I/O rates (waiting 2 seconds for delta)...")
    prev_io = disk_io.get_disk_io_raw()
    time.sleep(2)
    curr_io = disk_io.get_disk_io_raw()
    
    rates = disk_io.calculate_io_rate(prev_io, curr_io, 2.0)
    print("\nCalculated Rates:")
    for drive, rate in rates.items():
        print(f"  {drive}: Read {rate['read_bytes_sec']:.2f} B/s, Write {rate['write_bytes_sec']:.2f} B/s")
    
    if rates:
        print("\nSUCCESS: Disk I/O rates retrieved.")
        # Check if at least one drive letter (e.g., C:) is in the rates
        drive_letters = [k for k in rates.keys() if len(k) == 2 and k[1] == ':']
        if drive_letters:
            print(f"SUCCESS: Mapped drive letters found: {drive_letters}")
        else:
            print("WARNING: No drive letters found, only physical drives. This might be expected if mapping failed but fallback worked.")
    else:
        print("\nFAILURE: No disk I/O rates retrieved.")

if __name__ == "__main__":
    verify_io_retrieval()
