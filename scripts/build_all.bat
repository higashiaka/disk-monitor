@echo off
pushd %~dp0

call build_backend.bat
call build_frontend.bat

echo Packaging Application...
pushd %~dp0\..\frontend
call npm run dist
popd

echo All builds complete.
pause
popd
