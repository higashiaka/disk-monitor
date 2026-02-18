@echo off
pushd %~dp0\..\backend

echo Building Backend...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

call venv\Scripts\activate.bat
pyinstaller --noconfirm --onefile --windowed --name backend_main --clean --paths venv\Lib\site-packages app/main.py
:: --windowed to hide console window for backend (optional, maybe keep console first for debug?)
:: For now, let's use --console to see output in dev, but for prod build usually --windowed.
:: But our electron app spawns it. If --windowed, we won't see stdout?
:: Electron spawn with stdio: 'inherit' works if backend writes to stdout.
:: If --windowed, stdout might be null.
:: Let's use --console for now to be safe.

call venv\Scripts\deactivate.bat
popd
echo Backend build complete.
