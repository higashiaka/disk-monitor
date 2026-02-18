import sys
import os
import json

# Add parent dir to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app

def test_metrics_endpoint():
    client = TestClient(app)
    response = client.get("/metrics")
    
    if response.status_code == 200:
        data = response.json()
        print("SUCCESS: Metrics endpoint returned 200 OK")
        print(f"Data keys: {list(data.keys())}")
        
        # Check basic structure
        if "io" in data and "space" in data and "temp" in data:
            print("SUCCESS: Data structure is correct")
            
            # Print sample specific data
            if data['space']:
                print(f"Sample Space Info: {data['space'][0]}")
            else:
                print("WARNING: No space info returned (maybe no fixed disks found?)")
                
        else:
            print("FAILURE: Data structure is incorrect")
            sys.exit(1)
            
    else:
        print(f"FAILURE: Metrics endpoint returned {response.status_code}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_metrics_endpoint()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
