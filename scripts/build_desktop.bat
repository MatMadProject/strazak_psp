@echo off
echo ============================================
echo   BUILD DESKTOP APP - COMPLETE
echo ============================================
echo.

REM Przejdź do katalogu głównego projektu (o jeden poziom wyżej niż scripts)
cd /d "%~dp0\.."

REM Zapisz ścieżkę do katalogu głównego
set "PROJECT_ROOT=%CD%"

REM KROK 1: Build React
echo [KROK 1/3] Budowanie React frontendu...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo BLAD: Nie udalo sie zbudowac frontendu
    pause
    exit /b 1
)
cd ..

REM KROK 2: Zainstaluj PyInstaller
echo.
echo [KROK 2/3] Instalacja PyInstaller...
call venv\Scripts\activate
pip install pyinstaller
if %errorlevel% neq 0 (
    echo BLAD: Instalacja PyInstaller nie powiodla sie!
    pause
    exit /b 1
)

REM KROK 3: Pakowanie
echo.
echo [KROK 3/3] Pakowanie aplikacji...
echo To moze potrwac 2-5 minut...

REM Usuń stare pliki .spec
del "%PROJECT_ROOT%\desktop\*.spec" 2>nul

pyinstaller --clean --noconfirm ^
    --name="Strazak-DesktopApp" ^
    --onefile ^
    --windowed ^
    --icon="%PROJECT_ROOT%\desktop\icon.ico" ^
    --distpath="%PROJECT_ROOT%\desktop\dist" ^
    --workpath="%PROJECT_ROOT%\desktop\build" ^
    --specpath="%PROJECT_ROOT%\desktop" ^
    --add-data="%PROJECT_ROOT%\frontend\build;frontend/build" ^
    --add-data="%PROJECT_ROOT%\backend;backend" ^
    --add-data="%PROJECT_ROOT%\backend\templates\*;backend/templates" ^
    --add-data="%PROJECT_ROOT%\data;data" ^
    --hidden-import=uvicorn ^
    --hidden-import=uvicorn.logging ^
    --hidden-import=uvicorn.loops ^
    --hidden-import=uvicorn.loops.auto ^
    --hidden-import=uvicorn.protocols ^
    --hidden-import=uvicorn.protocols.http ^
    --hidden-import=uvicorn.protocols.http.auto ^
    --hidden-import=uvicorn.protocols.websockets ^
    --hidden-import=uvicorn.protocols.websockets.auto ^
    --hidden-import=uvicorn.lifespan ^
    --hidden-import=uvicorn.lifespan.on ^
    --hidden-import=fastapi ^
    --hidden-import=sqlalchemy ^
    --hidden-import=sqlalchemy.orm ^
    --hidden-import=sqlalchemy.ext.declarative ^
    --hidden-import=pydantic ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=webview ^
    --hidden-import=zestawienie_swd ^
    --hidden-import=docx ^
    --hidden-import=reportlab.lib ^
    --hidden-import=reportlab.platypus ^
    --hidden-import=reportlab.pdfbase ^
    --hidden-import=xhtml2pdf ^
    --collect-all=uvicorn ^
    --collect-all=fastapi ^
    --collect-all=sqlalchemy ^
    --collect-all=reportlab ^
    --collect-all=xhtml2pdf ^
    --collect-all=docxtpl ^
    "%PROJECT_ROOT%\desktop\app.py"

if %errorlevel% neq 0 (
    echo BLAD: Pakowanie nie powiodlo sie!
    pause
    exit /b 1
)

REM Czyszczenie
echo.
echo Czyszczenie plikow tymczasowych...
rmdir /s /q "%PROJECT_ROOT%\desktop\build" 2>nul

echo.
echo ============================================
echo   BUILD ZAKOŃCZONY POMYŚLNIE!
echo ============================================
echo.
echo Aplikacja znajduje sie w:
echo   desktop\dist\Strazak-DesktopApp.exe
echo.
dir "%PROJECT_ROOT%\desktop\dist\Strazak-DesktopApp.exe" | find "Strazak-DesktopApp.exe"
echo.
echo Testowanie:
echo   Uruchom: desktop\dist\Strazak-DesktopApp.exe
echo.
echo Nastepny krok:
echo   Stwórz installer: scripts\create_installer.bat
echo.
pause