@echo off
echo ============================================
echo   SETUP PROJEKTU SWD DESKTOP APP
echo ============================================
echo.

REM Sprawdź Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo BLAD: Python nie jest zainstalowany!
    echo Pobierz z: https://www.python.org/
    pause
    exit /b 1
)

REM Sprawdź Node.js
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo BLAD: Node.js nie jest zainstalowany!
    echo Pobierz z: https://nodejs.org/
    pause
    exit /b 1
)

echo [KROK 1/4] Instalacja zaleznosci backendu...
cd ..\backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo BLAD: Nie udalo sie zainstalowac zaleznosci backendu
    pause
    exit /b 1
)

echo.
echo [KROK 2/4] Instalacja zaleznosci desktopa...
cd ..\desktop
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo BLAD: Nie udalo sie zainstalowac zaleznosci desktopa
    pause
    exit /b 1
)

echo.
echo [KROK 3/4] Instalacja zaleznosci frontendu...
cd ..\frontend
call npm install
if %errorlevel% neq 0 (
    echo BLAD: Nie udalo sie zainstalowac zaleznosci frontendu
    pause
    exit /b 1
)

echo.
echo [KROK 4/4] Tworzenie struktury folderow...
cd ..
if not exist "data\" mkdir data
if not exist "data\uploads\" mkdir data\uploads

echo.
echo ============================================
echo   SETUP ZAKOŃCZONY POMYŚLNIE!
echo ============================================
echo.
echo Możesz teraz:
echo  1. Uruchomić dev mode: scripts\dev_start.bat
echo  2. Zbudować aplikację: scripts\build_desktop.bat
echo.
pause