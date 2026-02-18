# Disk Monitor

A real-time disk monitoring application for Windows, built with Python (FastAPI) and Electron (React).

## Features

- **Real-time Monitoring**: View read/write speeds, disk usage, and temperature (if available) for all fixed disks.
- **Overlay Mode**: Transparent, always-on-top overlay for monitoring while working in other apps.
- **Standalone**: Packed as a single executable installer.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd disk-monitor
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

## Running Locally

You can run the backend and frontend separately for development.

1. **Start Backend**
   ```bash
   cd backend
   .\venv\Scripts\uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend (Electron + React)**
   ```bash
   cd frontend
   npm run dev
   ```

## Building for Production

Use the provided scripts to build the application.

1. **Build Everything**
   ```bash
   scripts\build_all.bat
   ```

This will generate:
- `backend/dist/backend_main.exe`: The compiled Python backend.
- `frontend/dist-electron/`: The compiled Electron main process.
- `frontend/dist/`: The compiled React app.
- `frontend/dist/Disk Monitor Setup <version>.exe`: The final installer (if electron-builder is configured).

## License

MIT
