@echo off
cls
echo ====================================================
echo          Auto-Py-to-Exe CLI Tool
echo ====================================================
echo.

:: Check if auto-py-to-exe is installed
echo Checking if auto-py-to-exe is installed...
pip show auto-py-to-exe >nul 2>nul
if %errorlevel% neq 0 (
    echo auto-py-to-exe is not installed.
    echo Installing auto-py-to-exe...
    call :InstallAutoPyToExe
) else (
    echo auto-py-to-exe is already installed.
    echo Running auto-py-to-exe...
    call :RunAutoPyToExe
)
goto :EOF

:InstallAutoPyToExe
:: Install auto-py-to-exe with a progress bar
echo.
echo Installing auto-py-to-exe...
echo.

setlocal enabledelayedexpansion
set /a "progress=0"
set "barLength=50"

:: Start the installation and simulate progress
for /f "delims=" %%i in ('pip install auto-py-to-exe --disable-pip-version-check --quiet') do (
    set /a progress+=1
    set /a completed=!progress! * 100 / 5
    set /a barCompleted=!completed!*%barLength%/100
    set "bar="
    for /L %%a in (1,1,!barCompleted!) do set "bar=!bar!#"
    for /L %%a in (!barCompleted!,1,%barLength%) do set "bar=!bar!."
    echo [!bar!] !completed!%% Completed
    timeout /t 1 >nul
)

echo.
echo Installation complete!
goto :RunAutoPyToExe

:RunAutoPyToExe
:: Run auto-py-to-exe after installation
echo.
echo Launching auto-py-to-exe...
echo ====================================================
auto-py-to-exe
goto :EOF
