@echo off
cls
echo ====================================================
echo          Auto-Py-to-Exe CLI Tool
echo ====================================================
echo.

:: Main menu
:Menu
cls
echo ====================================================
echo               Auto-Py-to-Exe CLI Tool
echo ====================================================
echo.
echo 1. Install or Update auto-py-to-exe
echo 2. Uninstall auto-py-to-exe
echo 3. Run auto-py-to-exe
echo 4. Exit
echo.
set /p "option=Select an option: "
if "%option%"=="1" goto :InstallAutoPyToExe
if "%option%"=="2" goto :UninstallAutoPyToExe
if "%option%"=="3" goto :RunAutoPyToExe
if "%option%"=="4" exit /b
goto :Menu

:: Function to install/update auto-py-to-exe
:InstallAutoPyToExe
cls
echo ====================================================
echo          Installing/Updating auto-py-to-exe
echo ====================================================
echo.
echo Checking if auto-py-to-exe is installed...
pip show auto-py-to-exe >nul 2>nul
if %errorlevel% neq 0 (
    echo auto-py-to-exe is not installed. Proceeding with installation...
) else (
    echo auto-py-to-exe is already installed. Proceeding with update...
)
pip install auto-py-to-exe --upgrade --quiet
if %errorlevel% neq 0 (
    echo Error during installation/update of auto-py-to-exe.
    pause
    goto :Menu
)
echo auto-py-to-exe was successfully installed/updated.
pause
goto :Menu

:: Function to uninstall auto-py-to-exe
:UninstallAutoPyToExe
cls
echo ====================================================
echo          Uninstalling auto-py-to-exe
echo ====================================================
echo.
pip show auto-py-to-exe >nul 2>nul
if %errorlevel% neq 0 (
    echo auto-py-to-exe is not installed. Nothing to uninstall.
    pause
    goto :Menu
)

echo Are you sure you want to uninstall auto-py-to-exe? (y/n)
set /p "confirm=Your choice: "
if /i "%confirm%"=="y" (
    pip uninstall auto-py-to-exe -y --quiet
    if %errorlevel% neq 0 (
        echo Error during uninstallation of auto-py-to-exe.
        pause
        goto :Menu
    )
    echo auto-py-to-exe was successfully uninstalled.
) else (
    echo Uninstallation canceled.
)
pause
goto :Menu

:: Function to run auto-py-to-exe
:RunAutoPyToExe
cls
echo ====================================================
echo          Running auto-py-to-exe
echo ====================================================
echo.
auto-py-to-exe
if %errorlevel% neq 0 (
    echo Error running auto-py-to-exe. Ensure it is properly installed.
    pause
)
goto :Menu
