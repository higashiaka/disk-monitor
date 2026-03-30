@echo off
pushd %~dp0\..\backend

echo Building Backend (embedded, local mode)...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

call venv\Scripts\activate.bat

pyinstaller --noconfirm --onefile --windowed --name backend_main --clean --paths venv\Lib\site-packages --paths app app/main.py
if errorlevel 1 (
    echo ERROR: backend_main build failed.
    call venv\Scripts\deactivate.bat
    popd
    exit /b 1
)

echo.
echo Building Backend Server (standalone remote mode)...
pyinstaller --noconfirm --onefile --console --name backend_server --clean --paths venv\Lib\site-packages --paths app backend_server.py
if errorlevel 1 (
    echo ERROR: backend_server build failed.
    call venv\Scripts\deactivate.bat
    popd
    exit /b 1
)

call venv\Scripts\deactivate.bat
popd
echo Backend builds complete.
echo   dist\backend_main.exe   - embedded in Electron app
echo   dist\backend_server.exe - run on remote PC for remote monitoring
