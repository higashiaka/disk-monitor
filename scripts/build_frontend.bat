@echo off
pushd %~dp0\..\frontend

echo Building Frontend...
call npm run build
call npm run build:electron

popd
echo Frontend build complete.
