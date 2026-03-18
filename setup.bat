@echo off
REM Script para setup automático da aplicação Expression Recognition
REM Windows batch script

echo.
echo ======================================================
echo    Expression Recognition Dashboard - Setup
echo ======================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado. Por favor, instale Python 3.12+
    pause
    exit /b 1
)

REM Verificar se Node.js está instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js não encontrado. Por favor, instale Node.js 16+
    pause
    exit /b 1
)

echo [OK] Python encontrado: 
python --version

echo [OK] Node.js encontrado:
node --version

echo.
echo ======================================================
echo    Instalando dependências Backend...
echo ======================================================
echo.

REM Instalar dependências do backend
uv add fastapi uvicorn mediapipe opencv-python pillow numpy pydantic python-dotenv python-multipart pydantic-settings

echo.
echo ======================================================
echo    Instalando dependências Frontend...
echo ======================================================
echo.

REM Navegar para pasta frontend
cd frontend

REM Instalar dependências do frontend
call npm install

cd ..

echo.
echo ======================================================
echo    Setup Completo!
echo ======================================================
echo.
echo Para iniciar a aplicação, abra DOIS terminais:
echo.
echo TERMINAL 1 (Backend):
echo   uv run uvicorn backend.api.server:app --reload --port 8000
echo.
echo TERMINAL 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo Depois acesse:
echo   Frontend: http://localhost:5173
echo   Backend: http://localhost:8000/health
echo.
pause
