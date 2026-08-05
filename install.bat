@echo off
setlocal enabledelayedexpansion
title OKAS/KAS Skills Installer for Hermes

echo.
echo ============================================
echo   OKAS/KAS Hermes Skills Installer
echo   ติดตั้ง / อัปเดต Skills สำหรับงานตรวจสอบ
echo ============================================
echo.

:: ---------- 1. ตั้งค่า ----------
set "REPO_URL=https://github.com/thanatkjr/kas-hermes-skills.git"
set "REPO_DIR=%TEMP%\kas-hermes-skills"
set "SKILLS_DEST=%LOCALAPPDATA%\hermes\skills"

echo [1/4] กำลังดาวน์โหลด skills ล่าสุด...

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

:: ---------- 2. Cleanup — ลบ skills เก่าที่เปลี่ยนชื่อแล้ว ----------
echo [2/4] กำลังลบ skills เก่า (เปลี่ยน prefix)...

set "CLEAN_COUNT=0"

:: --- 2a: ลบ XKAS-* ทั้งหมด (test prefix) ---
for /d %%d in ("%SKILLS_DEST%\xkas-*") do (
    echo         [DEL] %%~nxd
    rmdir /s /q "%%d" 2>nul
    set /a CLEAN_COUNT+=1
)
for /d %%d in ("%SKILLS_DEST%\*\xkas-*") do (
    echo         [DEL] %%~nxd (in category)
    rmdir /s /q "%%d" 2>nul
    set /a CLEAN_COUNT+=1
)

:: --- 2b: ลบ KAS เก่าที่เปลี่ยนเป็น OKAS ---
set "OLD_TO_OKAS=kas-guard kas-model-guard kas-db-prevention kas-google-search-v2 kas-markitdown kas-model-routing"
for %%s in (%OLD_TO_OKAS%) do (
    if exist "%SKILLS_DEST%\%%s" (
        echo         [DEL] %%s
        rmdir /s /q "%SKILLS_DEST%\%%s" 2>nul
        set /a CLEAN_COUNT+=1
    )
    for /d %%c in ("%SKILLS_DEST%\*") do (
        if exist "%%c\%%s" (
            echo         [DEL] %%s (in category)
            rmdir /s /q "%%c\%%s" 2>nul
            set /a CLEAN_COUNT+=1
        )
    )
)

:: --- 2c: ลบ KAS เก่าที่เปลี่ยนเป็น XKAS ---
set "OLD_TO_XKAS=kas-client-knowledge-base kas-master-context kas-note"
for %%s in (%OLD_TO_XKAS%) do (
    if exist "%SKILLS_DEST%\%%s" (
        echo         [DEL] %%s
        rmdir /s /q "%SKILLS_DEST%\%%s" 2>nul
        set /a CLEAN_COUNT+=1
    )
    for /d %%c in ("%SKILLS_DEST%\*") do (
        if exist "%%c\%%s" (
            echo         [DEL] %%s (in category)
            rmdir /s /q "%%c\%%s" 2>nul
            set /a CLEAN_COUNT+=1
        )
    )
)

if !CLEAN_COUNT! gtr 0 (
    echo         ^>^>^> ลบแล้ว !CLEAN_COUNT! skills เก่า ^<^<^<
) else (
    echo         (ไม่มี skills เก่าต้องลบ)
)
echo.

:: ---------- 3. ติดตั้งเฉพาะ OKAS + KAS ที่อนุมัติ ----------
echo [3/4] กำลังติดตั้ง skills (OKAS + KAS)...

set "COUNT=0"
cd /d "%REPO_DIR%"

:: ใช้ dir เพื่อ list SKILL.md ทั้งหมด
dir /s /b SKILL.md > "%TEMP%\kas_skill_list.txt" 2>nul

for /f "usebackq delims=" %%f in ("%TEMP%\kas_skill_list.txt") do (
    set "SKILL_DIR=%%~dpf"
    set "SKILL_DIR=!SKILL_DIR:~0,-1!"

    :: หา relative path จาก repo
    set "REL=!SKILL_DIR:%REPO_DIR%\=!"
    
    :: ดึงชื่อ skill (โฟลเดอร์สุดท้าย)
    for %%a in ("!REL!") do set "SKILL_NAME=%%~nxa"

    :: ข้าม .git folder
    set "CHK=!REL!"
    if "!CHK:~0,4!" neq ".git" (
        if not "!REL!"=="" (
            :: --- FILTER: ติดตั้งเฉพาะ okas-* หรือ KAS ที่อนุมัติ ---
            set "APPROVED=0"
            
            :: เช็ค okas-*
            set "PREFIX=!SKILL_NAME:~0,5!"
            if /i "!PREFIX!"=="okas-" set "APPROVED=1"
            
            :: เช็ค Approved KAS list (hardcoded)
            if /i "!SKILL_NAME!"=="kas-rcm-setup"            set "APPROVED=1"
            if /i "!SKILL_NAME!"=="kas-master-note"          set "APPROVED=1"
            if /i "!SKILL_NAME!"=="kas-htmlformat"           set "APPROVED=1"
            if /i "!SKILL_NAME!"=="kas-ia-report-helper"     set "APPROVED=1"
            
            if "!APPROVED!"=="1" (
                echo         [OK] !SKILL_NAME!
                
                if exist "%SKILLS_DEST%\!REL!" rmdir /s /q "%SKILLS_DEST%\!REL!"
                robocopy "!SKILL_DIR!" "%SKILLS_DEST%\!REL!" /E /NFL /NDL /NJH /NJS >nul
                
                set /a COUNT+=1
            ) else (
                echo         [SKIP] !SKILL_NAME! ^(not in approved list^)
            )
        )
    )
)

del "%TEMP%\kas_skill_list.txt" 2>nul

echo.
echo         ^>^>^> ติดตั้งแล้ว !COUNT! skills ^<^<^<
echo.

:: ---------- 3.5 Auto-Fix: แก้ไข hardcoded paths + ตั้งค่า Hermes ----------
echo [3.5/4] กำลังแก้ไข paths และตั้งค่าระบบ...

:: --- 3.5a: แก้ไข C:\Users\ASUS -> %USERPROFILE% ในทุก SKILL.md ---
set "PSFILE=%TEMP%\fixskill.ps1"
(
echo $dir = $env:LOCALAPPDATA + '\hermes\skills'
echo $userPath = $env:USERPROFILE
echo $fixed = 0
echo $replacements = @(
echo     @{old='C:\\Users\\ASUS'; new=$userPath}
echo )
echo $files = Get-ChildItem -Path $dir -Recurse -Filter 'SKILL.md' -ErrorAction SilentlyContinue
echo foreach ($f in $files) {
echo     $content = Get-Content $f.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
echo     if (-not $content) { continue }
echo     $orig = $content
echo     $name = $f.Directory.Name
echo     foreach ($r in $replacements) {
echo         $content = $content -replace [regex]::Escape($r.old), $r.new
echo     }
echo     if ($content -ne $orig) {
echo         [System.IO.File]::WriteAllText($f.FullName, $content, [System.Text.UTF8Encoding]::new($false))
echo         Write-Host ('         [FIXED] ' + $name)
echo         $fixed++
echo     }
echo }
echo Write-Host ('         >>> Fixed ' + $fixed + ' path references <<<')
) > "%PSFILE%"
powershell -ExecutionPolicy Bypass -File "%PSFILE%" 2>nul
del "%PSFILE%" 2>nul

:: --- 3.5b: ตั้งค่า Hermes — ปิด MoA + เปลี่ยน vision model ---
echo         กำลังตั้งค่า Hermes...
hermes config set model.provider openrouter 2>nul
hermes config set moa.enabled false 2>nul
hermes config set auxiliary.vision.model google/gemini-3.6-flash 2>nul
hermes config set auxiliary.vision.provider openrouter 2>nul
if errorlevel 1 (
    echo         (Hermes CLI ไม่พร้อม — ข้ามการตั้งค่า)
) else (
    echo         >>> Provider=openrouter, MoA=OFF, Vision=gemini-3.6-flash <<<
)

echo.

:: ---------- 4. เสร็จ ----------
echo [4/4] เสร็จเรียบร้อย!
echo.
echo ============================================
echo   Approved: 6 OKAS + 4 KAS = 10 skills
if !CLEAN_COUNT! gtr 0 echo   Cleaned: !CLEAN_COUNT! old skills removed
echo   กรุณา restart Hermes หรือ /reload-skills
echo ============================================
echo.

:: ---------- แจ้ง Admin ทาง Telegram ----------
echo [แจ้งเตือน] กำลังส่งข้อความหา Thanat...
hermes send --platform telegram --to 8702982867 "🔔 %USERNAME%@%COMPUTERNAME% ติดตั้ง OKAS/KAS Skills แล้ว !COUNT! skills (cleaned !CLEAN_COUNT!) — /reload-skills" 2>nul
if errorlevel 1 (
    echo         (ไม่สามารถส่งแจ้งเตือนได้ — ข้าม)
) else (
    echo         ส่งแจ้งเตือนแล้ว!
)
echo.

pause
exit /b 0
