@echo off
chcp 65001 >nul
echo 🧹 Limpando caches, arquivos temporários e sessões...

REM ────────────────
REM ▶ Python cache
REM ────────────────
for /r %%i in (*.pyc *.pyo *.pyd) do del "%%i" >nul 2>&1
for /d /r %%i in (__pycache__) do rd /s /q "%%i" >nul 2>&1

REM ────────────────
REM ▶ Node.js cache (Next.js)
REM ────────────────
if exist frontend\.next rd /s /q frontend\.next >nul 2>&1
if exist frontend\node_modules rd /s /q frontend\node_modules >nul 2>&1

REM ────────────────
REM ▶ Pytest / coverage
REM ────────────────
if exist backend\.pytest_cache rd /s /q backend\.pytest_cache >nul 2>&1
if exist .coverage del .coverage >nul 2>&1
if exist .cache rd /s /q .cache >nul 2>&1

REM ────────────────
REM ▶ Arquivos de sessão e temporários
REM ────────────────
del /q *.session* >nul 2>&1
del /q backend\*.session* >nul 2>&1
del /q orientacao_bot.session >nul 2>&1
del /q shared\data\request_count.txt >nul 2>&1
del /q shared\data\request_date.txt >nul 2>&1
del /q shared\data\request_log.json >nul 2>&1

echo ✅ Projeto limpo com sucesso!
pause
