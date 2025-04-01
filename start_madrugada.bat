@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 Iniciando extração automática (modo madrugada)...

REM === Caminhos ===
set PROJECT_DIR=C:\Users\Xakep\Desktop\ExtracaoTelegram
set BACKEND_DIR=%PROJECT_DIR%\backend
set VENV_ACTIVATE=%BACKEND_DIR%\venv\Scripts\activate
set LOG_DIR=%PROJECT_DIR%\logs
set REQUEST_LOG_DIR=%LOG_DIR%\requests

REM === Gerar timestamp yyyy-mm-dd para nome do arquivo ===
for /f "tokens=1-3 delims=/" %%a in ("%date%") do (
    set DD=%%a
    set MM=%%b
    set YYYY=%%c
)
set TODAY=%YYYY%-%MM%-%DD%

REM 1. Navegar até backend e ativar ambiente virtual
cd /d %BACKEND_DIR%
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo ❌ Falha ao ativar o ambiente virtual!
    pause
    exit /b 1
)

REM 2. Voltar para a raiz do projeto
cd /d %PROJECT_DIR%

REM 3. Garantir que as pastas de logs existam
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)
if not exist "%REQUEST_LOG_DIR%" (
    mkdir "%REQUEST_LOG_DIR%"
)

REM 4. Executar script e salvar logs
echo 🕒 Início: %date% %time% >> "%LOG_DIR%\execucao_madrugada.log"
python start_extraction.py >> "%LOG_DIR%\execucao_%TODAY%.log" 2>&1

REM 5. Verificação de erro na execução
if errorlevel 1 (
    echo ❌ A execução do script falhou! >> "%LOG_DIR%\execucao_madrugada.log"
) else (
    echo ✅ Execução finalizada com sucesso. >> "%LOG_DIR%\execucao_madrugada.log"
)

echo 🔚 Fim: %date% %time% >> "%LOG_DIR%\execucao_madrugada.log"
echo. >> "%LOG_DIR%\execucao_madrugada.log"

echo ✅ Extração concluída.
pause
