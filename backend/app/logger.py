import logging
import os
from pathlib import Path

def setup_logger():
    # Log to %USERPROFILE%/.disk_monitor/debug.log
    log_dir = Path(os.environ["USERPROFILE"]) / ".disk_monitor"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "debug.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("DiskMonitor")

logger = setup_logger()
