@echo off
echo ============================================
echo   TWORZENIE INSTALATORA
echo ============================================
echo.


REM Szukaj Inno Setup w typowych lokalizacjach
set "ISCC_PATH="

REM Sprawdź w profilu użytkownika (AppData\Local\Programs)
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe" (
    set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\iscc.exe"
) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 5\iscc.exe" (
    set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 5\iscc.exe"
REM Sprawdź w Program Files (x86)
) else if exist "C:\Program Files (x86)\Inno Setup 6\iscc.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\iscc.exe"
) else if exist "C:\Program Files\Inno Setup 6\iscc.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\iscc.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 5\iscc.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 5\iscc.exe"
) else if exist "C:\Program Files\Inno Setup 5\iscc.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 5\iscc.exe"
) else (
    REM Sprawdź czy iscc jest w PATH
    where iscc >nul 2>nul
    if %errorlevel% equ 0 (
        set "ISCC_PATH=iscc"
    )
)

if "%ISCC_PATH%"=="" (
    echo BLAD: Inno Setup nie jest zainstalowany lub nie znaleziono iscc.exe!
    echo.
    echo Sprawdź czy Inno Setup jest zainstalowany w jednej z lokalizacji:
    echo   - %LOCALAPPDATA%\Programs\Inno Setup 6\
    echo   - C:\Program Files ^(x86^)\Inno Setup 6\
    echo   - C:\Program Files\Inno Setup 6\
    echo.
    echo Lub pobierz i zainstaluj Inno Setup z:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Znaleziono Inno Setup: %ISCC_PATH%
echo.

REM Przejdź do katalogu głównego projektu
cd /d "%~dp0\.."

REM Sprawdź czy plik exe istnieje
if not exist "desktop\dist\Strazak-DesktopApp.exe" (
    echo BLAD: Aplikacja nie zostala zbudowana!
    echo.
    echo Najpierw uruchom: scripts\build_desktop.bat
    echo.
    pause
    exit /b 1
)

REM Sprawdź czy istnieje folder installer i plik setup.iss
if not exist "installer\" (
    echo BLAD: Folder installer nie istnieje!
    echo Tworze folder installer...
    mkdir installer
)

if not exist "installer\setup.iss" (
    echo BLAD: Plik installer\setup.iss nie istnieje!
    echo Najpierw stworz plik konfiguracyjny Inno Setup.
    pause
    exit /b 1
)

REM Utwórz folder output jeśli nie istnieje
if not exist "installer\output\" mkdir installer\output

echo Tworzenie instalatora...
echo.

REM Przejdź do folderu installer i uruchom iscc
cd installer
"%ISCC_PATH%" setup.iss

if %errorlevel% neq 0 (
    echo BLAD: Nie udalo sie stworzyc instalatora!
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ============================================
echo   INSTALLER STWORZONY POMYŚLNIE!
echo ============================================
echo.
echo Installer znajduje sie w:
echo   installer\output\
echo.

REM Sprawdź czy plik istnieje i pokaż szczegóły
if exist "installer\output\*.exe" (
    dir "installer\output\*.exe"
) else (
    echo UWAGA: Nie znaleziono pliku instalatora w output
)

echo.
echo Możesz teraz:
echo  1. Przetestować installer
echo  2. Dystrybuować do użytkowników
echo.
pause