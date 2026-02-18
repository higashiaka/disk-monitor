@echo off
pushd %~dp0

call build_backend.bat
call build_frontend.bat

echo All builds complete.
pause
popd
