@echo off
echo ============================================
echo   BUILD REACT FRONTEND
echo ============================================
echo.

cd ..\frontend

echo Budowanie React...
call npm run build

if %errorlevel% neq 0 (
    echo.
    echo BLAD: Build nie powiodl sie!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   BUILD ZAKOŃCZONY!
echo ============================================
echo.
echo Build znajduje sie w: frontend\build\
echo.
pause