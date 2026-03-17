@echo off
echo ============================================
echo   BUILD DESKTOP APP - COMPLETE
echo ============================================
echo.

REM Przejdź do katalogu głównego projektu (o jeden poziom wyżej niż scripts)
cd /d "%~dp0\.."

REM Zapisz ścieżkę do katalogu głównego
set "PROJECT_ROOT=%CD%"

REM KROK 0: Stwórz czystą bazę danych
REM echo.
REM echo [KROK 0/3] Tworzenie czystej bazy danych...
REM call venv\Scripts\activate
REM python backend\create_fresh_db.py
REM if %errorlevel% neq 0 (
REM    echo BLAD: Nie udalo sie stworzyc bazy danych
REM     pause
REM     exit /b 1
REM )

REM KROK 1: Build React
echo [KROK 1/4] Budowanie React frontendu...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo BLAD: Nie udalo sie zbudowac frontendu
    pause
    exit /b 1
)
cd ..

REM KROK 2: Zainstaluj PyInstaller i Pillow
echo.
echo [KROK 2/4] Instalacja zaleznosci (PyInstaller, Pillow)...
call venv\Scripts\activate
pip install pyinstaller Pillow
if %errorlevel% neq 0 (
    echo BLAD: Instalacja nie powiodla sie!
    pause
    exit /b 1
)

REM KROK 3: Pakowanie
echo.
echo [KROK 3/4] Pakowanie aplikacji...
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
    --add-data="%PROJECT_ROOT%\desktop\splash.png;." ^
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
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.ImageTk ^
    --collect-all=uvicorn ^
    --collect-all=fastapi ^
    --collect-all=sqlalchemy ^
    --collect-all=reportlab ^
    --collect-all=xhtml2pdf ^
    --collect-all=docxtpl ^
    --collect-all=PIL ^
    "%PROJECT_ROOT%\desktop\app.py"

if %errorlevel% neq 0 (
    echo BLAD: Pakowanie nie powiodlo sie!
    pause
    exit /b 1
)

REM KROK 4: Czyszczenie
echo.
echo [KROK 4/4] Czyszczenie plikow tymczasowych...
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