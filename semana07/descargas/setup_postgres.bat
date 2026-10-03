@echo off
rem Script ejecutable para CMD en Windows (Batch)
rem Invoca el script de PowerShell setup_postgres.ps1 omitiendo la política de ejecución local

powershell -ExecutionPolicy Bypass -File "%~dp0setup_postgres.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Ocurrió un fallo al ejecutar setup_postgres.ps1 (Código de salida %ERRORLEVEL%).
    exit /b %ERRORLEVEL%
)
