@echo off
echo ============================================
echo   TWORZENIE INSTALATORA
echo ============================================
echo.

REM Sprawdź czy Inno Setup jest zainstalowany
where iscc >nul 2>nul
if %errorlevel% neq 0 (
    echo BLAD: Inno Setup nie jest zainstalowany!
    echo.
    echo Pobierz i zainstaluj Inno Setup z:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo Po instalacji dodaj do PATH:
    echo C:\Program Files (x86)\Inno Setup 6\
    echo.
    pause
    exit /b 1
)

REM Sprawdź czy plik exe istnieje
if not exist "..\desktop\dist\SWD-DesktopApp.exe" (
    echo BLAD: Aplikacja nie zostala zbudowana!
    echo.
    echo Najpierw uruchom: scripts\build_desktop.bat
    echo.
    pause
    exit /b 1
)

REM Utwórz folder output jeśli nie istnieje
cd ..\installer
if not exist "output\" mkdir output

echo Tworzenie instalatora...
echo.

iscc setup.iss

if %errorlevel% neq 0 (
    echo BLAD: Nie udalo sie stworzyc instalatora!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   INSTALLER STWORZONY POMYŚLNIE!
echo ============================================
echo.
echo Installer znajduje sie w:
echo   installer\output\SWD-DesktopApp-Setup-v1.0.0.exe
echo.
dir output\SWD-DesktopApp-Setup-v1.0.0.exe | find "SWD-DesktopApp-Setup"
echo.
echo Możesz teraz:
echo  1. Przetestować installer
echo  2. Dystrybuować do użytkowników
echo.
pause