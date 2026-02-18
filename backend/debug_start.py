import sys
import os

print("Starting debug script...")
try:
    print("Importing disk_io...")
    from app import disk_io
    print("Importing disk_space...")
    from app import disk_space
    print("Importing disk_temp...")
    from app import disk_temp
    print("Importing main...")
    from app import main
    print("All imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
