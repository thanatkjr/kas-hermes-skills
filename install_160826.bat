@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title KAS Skills Manager v160826

echo.
echo ============================================
echo   KAS Skills Manager v16.08.26
echo   ติดตั้ง / อัปเดต / ถอน Skills อัตโนมัติ
echo ============================================
echo.

:: ---------- ตั้งค่า ----------
set "REPO_URL=https://github.com/thanatkjr/kas-hermes-skills.git"
set "REPO_DIR=%TEMP%\kas-hermes-skills"

:: ---------- 1. ดาวน์โหลด repo ----------
echo [1/3] กำลังดาวน์โหลด skills ล่าสุด...

if exist "%REPO_DIR%\.git" (
    echo         อัปเดตจาก repo...
    cd /d "%REPO_DIR%"
    git pull --quiet
    if errorlevel 1 (
        echo         git pull ไม่สำเร็จ ดึงใหม่...
        rmdir /s /q "%REPO_DIR%"
        git clone --quiet "%REPO_URL%" "%REPO_DIR%"
    )
) else (
    echo         ดาวน์โหลดครั้งแรก...
    rmdir /s /q "%REPO_DIR%" 2>nul
    git clone --quiet "%REPO_URL%" "%REPO_DIR%"
)

if not exist "%REPO_DIR%\README.md" (
    echo [ERROR] ไม่สามารถดาวน์โหลด repo ได้
    echo         เช็คอินเทอร์เน็ต หรือติดต่อ Thanat
    pause
    exit /b 1
)
echo         พร้อม!
echo.

:: ---------- 2. รัน skill manager ----------
echo [2/3] กำลังตรวจสอบและติดตั้ง skills...
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ไม่พบ Python — ติดตั้ง Python แล้วลองใหม่ หรือติดต่อ Thanat
    pause
    exit /b 1
)

python "%REPO_DIR%\skill_manager.py" "%REPO_DIR%"

echo.
echo [3/3] เสร็จสิ้น
echo.

pause
exit /b 0
