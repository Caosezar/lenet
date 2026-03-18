#!/bin/bash
# Script para setup automático da aplicação Expression Recognition
# Linux/macOS bash script

echo ""
echo "======================================================"
echo "   Expression Recognition Dashboard - Setup"
echo "======================================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python não encontrado. Por favor, instale Python 3.12+"
    exit 1
fi

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "[ERRO] Node.js não encontrado. Por favor, instale Node.js 16+"
    exit 1
fi

echo "[OK] Python encontrado:"
python3 --version

echo "[OK] Node.js encontrado:"
node --version

echo ""
echo "======================================================"
echo "   Instalando dependências Backend..."
echo "======================================================"
echo ""

# Instalar dependências do backend
uv add fastapi uvicorn mediapipe opencv-python pillow numpy pydantic python-dotenv python-multipart pydantic-settings

echo ""
echo "======================================================"
echo "   Instalando dependências Frontend..."
echo "======================================================"
echo ""

# Navegar para pasta frontend
cd frontend

# Instalar dependências do frontend
npm install

cd ..

echo ""
echo "======================================================"
echo "   Setup Completo!"
echo "======================================================"
echo ""
echo "Para iniciar a aplicação, abra DOIS terminais:"
echo ""
echo "TERMINAL 1 (Backend):"
echo "   uv run uvicorn backend.api.server:app --reload --port 8000"
echo ""
echo "TERMINAL 2 (Frontend):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "Depois acesse:"
echo "   Frontend: http://localhost:5173"
echo "   Backend: http://localhost:8000/health"
echo ""
