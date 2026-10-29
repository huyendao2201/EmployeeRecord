@echo off
setlocal enabledelayedexpansion
title SecureHR - Reset Database va Seed Data

echo ==============================================================================
echo       SECUREHR - KHOI PHUC DU LIEU DEMO MAU (RESET DATABASE)
echo ==============================================================================
echo.
echo Dang nap lai du lieu mac dinh:
echo  - 6 Tai khoan: admin, hr_linh, ketoan_hoa, nv_nam, nv_huong, nv_tuan
echo  - 5 Ho so nhan vien (Ma NV, CCCD, Phong ban, Chuc vu, Luong)
echo  - 5 Ban ghi Hop dong lao dong
echo  - Audit Logs khoi dong he thong
echo.

set "PYTHON_EXE="

py -3.13 -c "import django" >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_EXE=py -3.13"
)

if not defined PYTHON_EXE (
    python -c "import django" >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
    )
)

if not defined PYTHON_EXE (
    py -3 -c "import django" >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py -3"
    )
)

if not defined PYTHON_EXE (
    python --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
    )
)

if not defined PYTHON_EXE (
    py -3 --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py -3"
    )
)

if not defined PYTHON_EXE (
    if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Python\bin\python.exe"
    )
)

if not defined PYTHON_EXE (
    echo [LOI] Khong tim thay Python!
    pause
    exit /b 1
)

cd /d "%~dp0backend"
echo Dang ap dung migrations vao PostgreSQL...
!PYTHON_EXE! manage.py migrate
echo Dang khoi tao du lieu mau...
!PYTHON_EXE! seed_demo_data.py

echo.
echo ==============================================================================
echo       HOAN TAT KHOI PHUC DU LIEU DEMO!
echo ==============================================================================
pause
