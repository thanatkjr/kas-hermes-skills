@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title KAS Skills Installer for Hermes

echo.
echo ============================================
echo   KAS Hermes Skills Installer
echo   ติดตั้ง / อัปเดต Skills สำหรับงานตรวจสอบ
echo ============================================
echo.

:: ---------- 1. ตั้งค่า ----------
set "REPO_URL=https://github.com/thanatkjr/kas-hermes-skills.git"
set "REPO_DIR=%TEMP%\kas-hermes-skills"
set "SKILLS_DEST=%LOCALAPPDATA%\hermes\skills"

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

:: ---------- 2. หาและติดตั้งทุก SKILL.md ----------
echo [2/3] กำลังติดตั้ง skills...

set "COUNT=0"
cd /d "%REPO_DIR%"

:: ใช้ dir เพื่อ list SKILL.md ทั้งหมด
dir /s /b SKILL.md > "%TEMP%\kas_skill_list.txt" 2>nul

for /f "usebackq delims=" %%f in ("%TEMP%\kas_skill_list.txt") do (
    set "SKILL_DIR=%%~dpf"
    set "SKILL_DIR=!SKILL_DIR:~0,-1!"

    :: หา relative path
    set "REL=!SKILL_DIR:%REPO_DIR%\=!"
    
    :: ข้าม .git folder
    set "CHK=!REL!"
    if "!CHK:~0,4!" neq ".git" (
        if not "!REL!"=="" (
            echo         [OK] !REL!
            
            if exist "%SKILLS_DEST%\!REL!" rmdir /s /q "%SKILLS_DEST%\!REL!"
            robocopy "!SKILL_DIR!" "%SKILLS_DEST%\!REL!" /E /NFL /NDL /NJH /NJS >nul
            
            set /a COUNT+=1
        )
    )
)

del "%TEMP%\kas_skill_list.txt" 2>nul

echo.
echo         ^>^>^> ติดตั้งแล้ว !COUNT! skills ^<^<^<
echo.

:: ---------- 3. เสร็จ ----------
echo [3/3] เสร็จเรียบร้อย!
echo.
echo ============================================
echo   กรุณา restart Hermes หรือ /reload-skills
echo ============================================
echo.

:: ---------- 🔔 แจ้ง Admin ทาง Telegram ----------
echo [แจ้งเตือน] กำลังส่งข้อความหา Thanat...
hermes send --platform telegram --to 8702982867 "🔔 %USERNAME%@%COMPUTERNAME% ติดตั้ง KAS Skills แล้ว !COUNT! skills — /reload-skills" 2>nul
if errorlevel 1 (
    echo         (ไม่สามารถส่งแจ้งเตือนได้ — ข้าม)
) else (
    echo         ส่งแจ้งเตือนแล้ว!
)
echo.

pause
exit /b 0