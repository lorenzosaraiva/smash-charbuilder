@echo off
setlocal EnableDelayedExpansion

set ROM=ssb64asm_extra.z64
set LOG=output.log
set ASM=%~dp0smashremix\assembler
if not defined SMASH_EXTRA_ROM_DIR set "SMASH_EXTRA_ROM_DIR=C:\Users\Lorenzo\Desktop\Smash 64\roms"
set "DEPLOY_ROM=%SMASH_EXTRA_ROM_DIR%\%ROM%"

echo. > "%ROM%"
echo Building "%ROM%"...

"%ASM%\bass.exe" -o "%ROM%" main.asm -sym logfile.log > "%LOG%" 2>&1

if %ERRORLEVEL% neq 0 (
    echo BUILD FAILED
    echo.
    echo ==== Last 10 lines of %LOG% ====

    for /f %%A in ('find /c /v "" ^< "%LOG%"') do set TOTAL=%%A
    set /a SKIP=!TOTAL!-10
    if !SKIP! LSS 0 set SKIP=0

    if !SKIP! GTR 0 (
        more +!SKIP! "%LOG%"
    ) else (
        type "%LOG%"
    )
    exit /b 1
)

echo BUILD SUCCESS

"%ASM%\rn64crc.exe" -u "%ROM%" >> "%LOG%" 2>&1
if errorlevel 1 (
    echo CRC UPDATE FAILED
    type "%LOG%"
    exit /b 1
)

if not exist "%SMASH_EXTRA_ROM_DIR%\" (
    mkdir "%SMASH_EXTRA_ROM_DIR%"
    if errorlevel 1 (
        echo ROM DEPLOY DIRECTORY CREATION FAILED: "%SMASH_EXTRA_ROM_DIR%"
        exit /b 1
    )
)

copy /Y "%ROM%" "%DEPLOY_ROM%" >nul
if errorlevel 1 (
    echo ROM DEPLOY FAILED: "%DEPLOY_ROM%"
    exit /b 1
)

echo Build log exported to "%LOG%"
echo ROM copied to "%DEPLOY_ROM%"
exit /b 0
