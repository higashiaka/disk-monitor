import sys
import os

# Standard PyInstaller and local dev path handling
if getattr(sys, 'frozen', False):
    # Run from bundled EXE - PyInstaller unpacks assets here
    base_path = sys._MEIPASS
    # Add base_path to sys.path to find sibling modules directly
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
else:
    # Run from source
    base_path = os.path.dirname(os.path.abspath(__file__))
    if base_path not in sys.path:
        sys.path.insert(0, base_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
import disk_io
import disk_space
import disk_temp
from logger import logger

logger.info(f"Storage Monitor Backend starting. Frozen: {getattr(sys, 'frozen', False)}")

app = FastAPI()

# Allow CORS for Electron (usually serves from localhost or file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for metrics
current_metrics = {
    "io": {},
    "space": [],
    "temp": {},
    "timestamp": 0
}

# Background task for updating metrics
async def update_metrics_loop():
    prev_io = disk_io.get_disk_io_raw()
    prev_time = time.time()
    
    while True:
        await asyncio.sleep(1) # 1 second interval
        
        curr_time = time.time()
        curr_io = disk_io.get_disk_io_raw()
        
        # Calculate rates
        interval = curr_time - prev_time
        try:
            io_rates = disk_io.calculate_io_rate(prev_io, curr_io, interval)
            if not io_rates:
                 logger.warning("No I/O rates calculated in this loop.")
        except Exception as e:
            logger.error(f"Error in update_metrics_loop io calc: {e}")
            io_rates = {}
        
        # Space info
        try:
            space_info = disk_space.get_all_disk_space_info()
        except Exception as e:
            logger.error(f"Error in update_metrics_loop space: {e}")
            space_info = []
        
        # Temp info
        try:
            temps = disk_temp.get_dummy_temperatures() 
        except Exception as e:
            logger.error(f"Error in update_metrics_loop temp: {e}")
            temps = {}
        
        # Update global state
        current_metrics["io"] = io_rates
        current_metrics["space"] = space_info
        current_metrics["temp"] = temps
        current_metrics["timestamp"] = curr_time
        
        prev_io = curr_io
        prev_time = curr_time

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_metrics_loop())

from pydantic import BaseModel
from typing import List, Optional

class MetricRequest(BaseModel):
    custom_paths: Optional[List[str]] = []

@app.post("/metrics")
async def get_metrics(req: MetricRequest = None):
    # Update global state with latest info (including custom paths if provided)
    # Note: In a real app we might want to decouple collection from the request 
    # if it takes too long, but for a few paths it's fast.
    
    # We can still return the cached global metrics for standard disks
    # and append custom paths on demand, or update the global loop to handle them.
    # For simplicity, let's fetch custom paths on demand here and merge.
    
    response_data = current_metrics.copy()
    
    if req and req.custom_paths:
        custom_usage = disk_space.get_custom_path_usage(req.custom_paths)
        # Append to existing space list
        # We need to make sure we don't duplicate if they are already in the main list
        # But for now, let's just append.
        existing_mounts = {d['mountpoint'] for d in response_data['space']}
        for c in custom_usage:
            if c['mountpoint'] not in existing_mounts:
                 response_data['space'].append(c)
                 
    return response_data

@app.get("/metrics")
async def get_metrics_get():
    return current_metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
