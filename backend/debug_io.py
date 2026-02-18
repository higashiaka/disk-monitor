import psutil
import time

print("--- Partitions ---")
try:
    parts = psutil.disk_partitions(all=True)
    for p in parts:
        print(f"Device: {p.device}, Mount: {p.mountpoint}, FSType: {p.fstype}")
except Exception as e:
    print(e)

print("\n--- I/O Counters (First Run) ---")
try:
    io = psutil.disk_io_counters(perdisk=True)
    for k, v in io.items():
        print(f"Key: {k}")
except Exception as e:
    print(e)

print("Waiting 1 second...")
time.sleep(1)

print("\n--- I/O Counters (Second Run) ---")
try:
    io = psutil.disk_io_counters(perdisk=True)
    for k, v in io.items():
        print(f"Key: {k}, Read: {v.read_bytes}, Write: {v.write_bytes}")
except Exception as e:
    print(e)
