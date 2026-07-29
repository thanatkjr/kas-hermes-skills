@echo off
title FixSkill — แก้ไข references + paths ใน OKAS/KAS Skills

echo.
echo ============================================
echo   FixSkill v1.0
echo   แก้ไข SKILL.md: old references + user paths
echo ============================================
echo.

set "SKILLS_DIR=%LOCALAPPDATA%\hermes\skills"

echo Skills directory: %SKILLS_DIR%
echo Current user    : %USERNAME%
echo Profile path    : %USERPROFILE%
echo.

:: ============================================================
:: เขียน PowerShell script ลง temp file (เลี่ยง special chars)
:: ============================================================
set "PSFILE=%TEMP%\fixskill.ps1"

(
echo $dir = $env:LOCALAPPDATA + '\hermes\skills'
echo $userPath = $env:USERPROFILE
echo $fixed = 0
echo.
echo $replacements = @(
echo     @{old='C:\\Users\\ASUS'; new=$userPath},
echo     @{old='\bkas-guard\b'; new='okas-guard'},
echo     @{old='\bkas-note\b'; new='xkas-note'},
echo     @{old='\bkas-markitdown\b'; new='okas-markitdown'},
echo     @{old='\bkas-client-knowledge-base\b'; new='xkas-client-knowledge-base'},
echo     @{old='\bkas-master-context\b'; new='xkas-master-context'},
echo     @{old='\bkas-db-prevention\b'; new='okas-db-prevention'},
echo     @{old='\bkas-google-search-v2\b'; new='okas-google-search-v2'},
echo     @{old='\bkas-model-guard\b'; new='okas-model-guard'},
echo     @{old='\bkas-model-routing\b'; new='okas-model-routing'}
echo )
echo.
echo $files = Get-ChildItem -Path $dir -Recurse -Filter 'SKILL.md'
echo foreach ($f in $files) {
echo     $content = Get-Content $f.FullName -Raw -Encoding UTF8
echo     $orig = $content
echo     $name = $f.Directory.Name
echo.
echo     foreach ($r in $replacements) {
echo         $content = $content -replace $r.old, $r.new
echo     }
echo.
echo     if ($content -ne $orig) {
echo         [System.IO.File]::WriteAllText($f.FullName, $content, [System.Text.UTF8Encoding]::new($false))
echo         Write-Host ('  [FIXED] ' + $name)
echo         $fixed++
echo     }
echo }
echo.
echo Write-Host ('')
echo Write-Host ('  >>> Fixed ' + $fixed + ' files <<<')
echo exit $fixed
) > "%PSFILE%"

:: ============================================================
:: รัน PowerShell
:: ============================================================
powershell -ExecutionPolicy Bypass -File "%PSFILE%"

if errorlevel 1 (
    echo.
    echo   Fixed at least 1 file.
) else (
    echo.
    echo   No fixes needed - all clean!
)

:: Cleanup
del "%PSFILE%" 2>nul

echo.
echo ============================================
echo   Done! Restart Hermes or /reload-skills
echo ============================================
echo.

pause
exit /b 0
