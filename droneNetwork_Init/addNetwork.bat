@echo off
:: Check if PowerShell is available
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo PowerShell is not installed. Please install PowerShell to run this script.
    pause
    exit /b
)

:: Set the path to your PowerShell script using a relative path
set "psScriptPath=Add-WireGuardDevice.ps1"

:: Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%psScriptPath%"
pause
