@echo off
:: Build script for conda (Windows)

set CMAKE_ARGS=-DCMAKE_BUILD_TYPE=Release -A x64

if exist "..\libpolycall-v1" (
    set CMAKE_ARGS=%CMAKE_ARGS% -DLIBPOLYCALL_ROOT=../libpolycall-v1
)

%PYTHON% -m pip install . -vv
if errorlevel 1 exit 1
