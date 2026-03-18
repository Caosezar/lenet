#!/usr/bin/env python
"""
Script de diagnóstico para testar o backend FastAPI e WebSocket
"""

import asyncio
import json
import base64
import websockets
import os
import sys
from pathlib import Path

# Adicionar projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar backend
from backend.api.server import app, landmarker, model_path

async def test_websocket():
    """Teste básico de conexão WebSocket"""
    print("\n" + "="*60)
    print("TESTE: Conexão WebSocket")
    print("="*60)
    
    try:
        async with websockets.connect('ws://localhost:8000/ws/process-video', timeout=5) as websocket:
            print("✓ WebSocket conectado!")
            
            # Enviar um frame dummy
            dummy_frame = base64.b64encode(b'\x00' * 1000).decode()
            
            message = {
                "action": "predict",
                "frame_base64": dummy_frame,
                "user_id": "Test User"
            }
            
            print(f"Enviando mensagem teste...")
            await websocket.send(json.dumps(message))
            
            # Receber resposta
            print("Aguardando resposta...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            
            print("✓ Resposta recebida:")
            print(f"  - Expression: {data.get('expression', 'N/A')}")
            print(f"  - Confidence: {data.get('confidence', 'N/A')}")
            print(f"  - Latency: {data.get('latency_ms', 'N/A')}ms")
            if 'error' in data:
                print(f"  - Erro: {data.get('error')}")
            
            return True
            
    except Exception as e:
        print(f"✗ Erro WebSocket: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model():
    """Teste de carregamento do modelo"""
    print("\n" + "="*60)
    print("TESTE: Carregamento do Modelo")
    print("="*60)
    
    print(f"Caminho esperado: {model_path}")
    print(f"Arquivo existe: {os.path.exists(model_path)}")
    
    if not os.path.exists(model_path):
        print("\n✗ ERRO: Arquivo face_landmarker.task não encontrado!")
        print(f"  Procure por face_landmarker.task em: d:\\Devs\\DevProjs\\lenet\\core\\")
        return False
    
    print(f"✓ Arquivo encontrado!")
    
    if landmarker is None:
        print("✗ ERRO: FaceLandmarker não foi carregado!")
        return False
    
    print("✓ FaceLandmarker carregado com sucesso!")
    return True


def test_imports():
    """Teste de imports"""
    print("\n" + "="*60)
    print("TESTE: Imports Necessários")
    print("="*60)
    
    try:
        import fastapi
        print(f"✓ fastapi {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ fastapi: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✓ uvicorn {uvicorn.__version__}")
    except ImportError as e:
        print(f"✗ uvicorn: {e}")
        return False
    
    try:
        import mediapipe as mp
        print(f"✓ mediapipe {mp.__version__}")
    except ImportError as e:
        print(f"✗ mediapipe: {e}")
        return False
    
    try:
        import cv2
        print(f"✓ opencv-python {cv2.__version__}")
    except ImportError as e:
        print(f"✗ opencv-python: {e}")
        return False
    
    try:
        import websockets
        print(f"✓ websockets")
    except ImportError as e:
        print(f"✗ websockets: {e}")
        return False
    
    return True


async def main():
    """Executar todos os testes"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  DIAGNÓSTICO DO BACKEND - LeNet Expression Recognition".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Teste 1: Imports
    imports_ok = test_imports()
    
    # Teste 2: Modelo
    model_ok = test_model()
    
    # Teste 3: WebSocket (apenas se modelo carregou)
    if model_ok:
        print("\nNota: Para testar WebSocket, o backend deve estar rodando em outra janela.")
        print("Execute em outro terminal: uv run uvicorn backend.api.server:app --reload")
        print("\nDeseja testar WebSocket? (S/N): ", end="", flush=True)
        
        # Se preferir pular, apenas não aguarde
        # ws_ok = await test_websocket()
    
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    print(f"Imports: {'✓ OK' if imports_ok else '✗ ERRO'}")
    print(f"Modelo:  {'✓ OK' if model_ok else '✗ ERRO - Veja acima'}")
    
    if imports_ok and model_ok:
        print("\n✓ Tudo pronto! Inicie o backend com:")
        print("  cd backend")
        print("  uv run uvicorn api.server:app --reload")
    else:
        print("\n✗ Há erros a corrigir. Veja acima para detalhes.")


if __name__ == "__main__":
    asyncio.run(main())
