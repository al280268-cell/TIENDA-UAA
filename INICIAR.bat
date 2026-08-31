@echo off
title FERIA UAA — Reto E-Commerce
color 0C

echo.
echo  ============================================
echo   FERIA UAA - Sistema de Reto E-Commerce
echo  ============================================
echo.
echo  Iniciando servidor...
echo.

:: Matar proceso previo en puerto 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 "') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 1 /nobreak >nul

:: Iniciar servidor unificado (API + Frontend)
start "UAA Backend" /B uvicorn backend.app:app --host 0.0.0.0 --port 8000

timeout /t 3 /nobreak >nul

:: Abrir el navegador
start "" http://localhost:8000
start "" http://localhost:8000/admin.html

echo.
echo  ============================================
echo   SERVIDOR CORRIENDO EN:
echo   Jugadores: http://localhost:8000
echo   Admin:     http://localhost:8000/admin.html
echo   Password:  uaa2026admin
echo  ============================================
echo.
echo  Presiona Ctrl+C para detener el servidor.
echo.

uvicorn backend.app:app --host 0.0.0.0 --port 8000
