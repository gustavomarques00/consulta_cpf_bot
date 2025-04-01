@echo off
chcp 65001 >nul
title 🚀 Execução Manual - Tráfego BRSMM

echo ============================================
echo     INICIANDO ENVIO MANUAL DE TRÁFEGO BRSMM
echo ============================================

REM 1. Navega até a pasta do backend
cd /d %~dp0backend

REM 2. Ativa o ambiente virtual
call venv\Scripts\activate

REM 3. Executa o script de tráfego
echo 🔁 Executando script: send_daily_brsmm.py
python scripts\send_daily_brsmm.py

echo.
echo ✅ Execução finalizada! Verifique o log em /logs
pause
