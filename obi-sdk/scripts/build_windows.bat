@echo off
:: OBIAI SDK Windows Build Script

setlocal EnableDelayedExpansion

echo Building OBIAI SDK for Windows...

:: Check for Visual Studio
where cl >nul 2>&1
if errorlevel 1 (
    echo ERROR: Visual Studio C++ compiler not found.
    echo Please run from "x64 Native Tools Command Prompt"
    exit /b 1
)

:: Check conda
conda info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda not found or not activated
    exit /b 1
)

:: Clean
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info

:: Build libpolycall-v1
if exist "..\libpolycall-v1" (
    echo Building libpolycall-v1...
    if not exist "..\libpolycall-v1\build" mkdir "..\libpolycall-v1\build"
    pushd "..\libpolycall-v1\build"
    cmake .. -A x64 -DCMAKE_BUILD_TYPE=Release
    cmake --build . --config Release --parallel
    popd
    set LIBPOLYCALL_ROOT=..\libpolycall-v1
)

:: Build Python extension
pip install -e . -v --no-build-isolation

:: Test
python -m pytest tests\ -v --tb=short

echo Build complete!
