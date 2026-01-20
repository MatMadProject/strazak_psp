@echo off
echo ============================================
echo   BUILD DESKTOP APP - COMPLETE
echo ============================================
echo.

REM KROK 1: Build React
echo [KROK 1/3] Budowanie React frontendu...
cd ..\frontend
call npm run build
if %errorlevel% neq 0 (
    echo BLAD: Nie udalo sie zbudowac frontendu
    pause
    exit /b 1
)

REM KROK 2: Zainstaluj PyInstaller
echo.
echo [KROK 2/3] Instalacja PyInstaller...
pip install pyinstaller

REM KROK 3: Pakowanie
echo.
echo [KROK 3/3] Pakowanie aplikacji...
echo To moze potrwac 2-5 minut...
cd ..\desktop

pyinstaller --clean --noconfirm ^
    --name "SWD-DesktopApp" ^
    --onefile ^
    --windowed ^
    --add-data "..\backend;backend" ^
    --add-data "..\frontend\build;frontend\build" ^
    --hidden-import "uvicorn" ^
    --hidden-import "fastapi" ^
    --hidden-import "sqlalchemy" ^
    --hidden-import "pandas" ^
    --hidden-import "openpyxl" ^
    --collect-all "uvicorn" ^
    --collect-all "fastapi" ^
    main.py

if %errorlevel% neq 0 (
    echo BLAD: Pakowanie nie powiodlo sie!
    pause
    exit /b 1
)

REM Czyszczenie
echo.
echo Czyszczenie plikow tymczasowych...
rmdir /s /q build 2>nul

echo.
echo ============================================
echo   BUILD ZAKOŃCZONY POMYŚLNIE!
echo ============================================
echo.
echo Aplikacja znajduje sie w:
echo   desktop\dist\SWD-DesktopApp.exe
echo.
dir dist\SWD-DesktopApp.exe | find "SWD-DesktopApp.exe"
echo.
echo Testowanie:
echo   Uruchom: desktop\dist\SWD-DesktopApp.exe
echo.
echo Nastepny krok:
echo   Stwórz installer: scripts\create_installer.bat
echo.
pause