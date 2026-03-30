import sys
import os
import argparse
import socket

# Handle PyInstaller frozen state and development mode
if getattr(sys, 'frozen', False):
    # PyInstaller: all app/ modules are bundled flat into _MEIPASS
    base_path = sys._MEIPASS
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
else:
    # Development: add app/ directory to path so 'import main' works
    base_path = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_path, 'app')
    if app_path not in sys.path:
        sys.path.insert(0, app_path)

# Import the FastAPI app object from main.py
from main import app  # noqa: E402
import uvicorn         # noqa: E402


def get_local_ip() -> str:
    """Return the machine's LAN IP address for display purposes."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Disk Monitor Backend Server - standalone remote mode"
    )
    parser.add_argument(
        "--host", default="0.0.0.0",
        help="Interface to bind to (default: 0.0.0.0 = all interfaces)"
    )
    parser.add_argument(
        "--port", type=int, default=8001,
        help="Port to listen on (default: 8001)"
    )
    args = parser.parse_args()

    local_ip = get_local_ip()

    print("=" * 52)
    print("   Disk Monitor  -  Remote Backend Server")
    print("=" * 52)
    print(f"  Binding  : {args.host}:{args.port}")
    print(f"  Local IP : {local_ip}")
    print(f"  Use this URL in Disk Monitor Settings on")
    print(f"  the other PC:")
    print()
    print(f"      http://{local_ip}:{args.port}")
    print()
    print("  Press Ctrl+C to stop the server.")
    print("=" * 52)

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
