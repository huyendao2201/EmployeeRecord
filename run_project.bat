@echo off
setlocal enabledelayedexpansion
title SecureHR - Khoi dong he thong

echo ==============================================================================
echo       SECUREHR - HE THONG QUAN LY HO SO NHAN VIEN & PHAN QUYEN TRUY CAP
echo ==============================================================================
echo.

REM 1. Tim trinh thuc thi Python co cai san Django
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
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    )
)

if not defined PYTHON_EXE (
    echo [LOI] Khong tim thay Python! Vui long cai dat Python va tick chon "Add to PATH".
    pause
    exit /b 1
)

echo [OK] Python da san sang: !PYTHON_EXE!

REM 2. Tim trinh thuc thi Node / NPM
set "NPM_EXE="

call npm --version >nul 2>&1
if !errorlevel! equ 0 (
    set "NPM_EXE=npm"
)

if not defined NPM_EXE (
    if exist "C:\Program Files\nodejs\npm.cmd" (
        set "NPM_EXE=C:\Program Files\nodejs\npm.cmd"
    )
)

if not defined NPM_EXE (
    echo [LOI] Khong tim thay Node.js / NPM! Vui long cai dat Node.js.
    pause
    exit /b 1
)

echo [OK] Node / NPM da san sang: !NPM_EXE!
echo.
echo [*] Dang khoi dong cac thanh phan he thong...
echo.

REM 3. Khoi dong Backend Django (Port 8000)
echo [1/3] Khoi dong Backend Django API tai http://127.0.0.1:8000 ...
start "SecureHR - Backend (Port 8000)" cmd /k "title Backend Django (Port 8000) && cd /d "%~dp0backend" && !PYTHON_EXE! manage.py runserver 127.0.0.1:8000"

REM 4. Khoi dong Frontend Vue/Vite (Port 5173)
echo [2/3] Khoi dong Frontend Vue/Vite tai http://localhost:5173 ...
start "SecureHR - Frontend (Port 5173)" cmd /k "title Frontend Vite (Port 5173) && cd /d "%~dp0frontend" && !NPM_EXE! run dev"

REM 5. Cho server san sang va mo trinh duyet
echo [3/3] Dang mo trinh duyet Web...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ==============================================================================
echo       HE THONG DA DUOC KHOI DONG THANH CONG!
echo ==============================================================================
echo   - Frontend: http://localhost:5173
echo   - Backend:  http://127.0.0.1:8000/api/
echo.
echo   DANH SACH TAI KHOAN TRUY CAP HE THONG:
echo   ----------------------------------------------------------------------------
echo   1. Nhan vien Nam       : nv_nam     ^| Employee@123 (Ma NV: EMP001 - ID: 1)
echo   2. Nhan vien Huong     : nv_huong   ^| Employee@123 (Ma NV: EMP002 - ID: 2)
echo   3. Nhan su (HR Linh)   : hr_linh    ^| Hr@123       (Quan ly ho so, hop dong)
echo   4. Ke toan (Hoa)       : ketoan_hoa ^| Ketoan@123   (Quan ly luong thuong)
echo   5. Quan tri vien       : admin      ^| Admin@123    (Quan tri toan he thong)
echo   ----------------------------------------------------------------------------
echo.
echo   Luu y: De tat he thong, chi can dong 2 cua so Backend va Frontend vua mo.
echo ==============================================================================
echo.
pause
