# Development Guide - Expression Recognition

Guia completo para desenvolvimento e expansão da aplicação.

## 🏗️ Arquitetura Técnica

### Backend (FastAPI)

```
backend/
├── api/
│   ├── models.py        # Pydantic schemas para validação de dados
│   ├── core.py          # Lógica core (APIs: FacialRecognition + Expression)
│   └── server.py        # FastAPI app, rotas HTTP e WebSocket
└── __init__.py
```

**Fluxo de uma requisição WebSocket**:
1. Frontend captura frame da câmera (30 FPS)
2. Converte frame para Base64 JPEG comprimido
3. Envia via WebSocket ao servidor
4. Backend decodifica Base64 → OpenCV Mat
5. Backend processa com MediaPipe (detecção facial + 52 blendshapes)
6. Backend classifica expressão via ExpressionAPI (Euclidean distance)
7. Backend retorna JSON com resultado + latência
8. Frontend atualiza UI em tempo real

### Frontend (React + Vite)

```
frontend/src/
├── components/          # Componentes React
│   ├── CameraStream.jsx     # Captura de câmera
│   ├── DataBlock.jsx        # Bloco de dados (preto/verde)
│   ├── LatencyGraph.jsx     # Gráfico de latência (Recharts)
│   └── ExpressionRegister.jsx # Input de cadastro
├── hooks/
│   └── useWebSocket.js      # Custom hook para WebSocket
├── utils/
│   └── canvasUtils.js       # Utilitários canvas → Base64
├── pages/
│   └── Dashboard.jsx        # Layout principal
└── App.jsx              # Root component
```

## 🔌 APIs

### HTTP Endpoints

#### GET /health
Status do servidor.

```bash
curl http://localhost:8000/health
# Response: {"status":"ok","version":"1.0.0"}
```

#### POST /register-expression
Registrar uma nova expressão (alternativa a WebSocket).

```bash
curl -X POST http://localhost:8000/register-expression \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "Usuario Principal",
    "label": "Sorrindo",
    "blendshapes": [
      {"category_name": "mouthSmile", "score": 0.85}
    ]
  }'
```

#### GET /expressions/{user_id}
Listar expressões registradas de um usuário.

```bash
curl http://localhost:8000/expressions/Usuario%20Principal
# Response: {"user_id":"Usuario Principal","expressions":["Sorrindo","Bravo"]}
```

### WebSocket Endpoint

#### WS /ws/process-video
Em tempo real, processa frames (predict + register).

**Mensagem de Predição**:
```json
{
  "action": "predict",
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "user_id": "Usuario Principal"
}
```

**Resposta**:
```json
{
  "user_id": "Usuario Principal",
  "expression": "Sorrindo (Gravada!)",
  "confidence": 87.5,
  "latency_ms": 32.5,
  "timestamp_ms": 1710691200000,
  "blendshapes_count": 52,
  "top_blendshapes": [
    {"name": "mouthSmile", "score": 0.85},
    {"name": "cheekSquintLeft", "score": 0.42},
    {"name": "eyeBlinkLeft", "score": 0.15}
  ]
}
```

**Mensagem de Registro**:
```json
{
  "action": "register",
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "user_id": "Usuario Principal",
  "label": "Sorrindo"
}
```

**Resposta**:
```json
{
  "action": "register_response",
  "success": true,
  "message": "Expression 'Sorrindo' registered successfully for Usuario Principal",
  "user_id": "Usuario Principal",
  "label": "Sorrindo"
}
```

## 🛠️ Como Estender

### Adicionar Nova Métrica ao DataBlock

1. **Modificar `backend/api/core.py`** para calcular a métrica
2. **Adicionar ao schema** em `backend/api/models.py::ExpressionResultResponse`
3. **Frontend recebe automaticamente** via WebSocket
4. **Renderizar em `frontend/src/components/DataBlock.jsx`**

Exemplo: Adicionar "emotion" (emoção detectada):

```python
# backend/api/core.py
def predict(self, user_id: str, blendshapes: list) -> dict:
    # ... código existente ...
    emotion = self._classify_emotion(blendshapes)  # Nova linha
    return {
        "expression": expression_result,
        "confidence": confidence,
        "top_blendshapes": top_fallback[:5],
        "emotion": emotion  # Nova linha
    }
```

### Persistir Expressões em Banco de Dados

Atualmente em memória (`ExpressionAPI.expressions`). Para SQLite:

```python
# backend/api/database.py (novo arquivo)
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///expressions.db')
Session = sessionmaker(bind=engine)

class ExpressionRecord(Base):
    __tablename__ = "expressions"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    label = Column(String)
    blendshapes = Column(JSON)  # Armazenar array numpy como JSON
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Adicionar Autenticação Multi-Usuário

```python
# backend/api/auth.py (novo arquivo)
from fastapi import Depends, HTTPException
from jose import JWTError, jwt

# Implementar autenticação JWT
# Cada usuário teria seus próprios registros de expressão

@app.post("/login")
async def login(username: str, password: str):
    # Validar credenciais
    token = create_access_token({"sub": username})
    return {"access_token": token}

@app.websocket("/ws/process-video")
async def websocket_process_video(websocket: WebSocket, token: str = Query(...)):
    # Validar token antes de processar
    user_id = validate_token(token)
    # ... processar com user_id autenticado
```

### Usar Face Embedding Real

Atualmente `FacialRecognitionAPI` é um mock. Para reconhecimento real:

```python
# backend/api/face_embedding.py (novo arquivo)
from face_recognition import face_encodings, face_distance
import numpy as np

class FacialRecognitionAPI:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
    
    def identify(self, frame, face_locations):
        encodings = face_encodings(frame, face_locations)
        
        for encoding in encodings:
            distances = face_distance(self.known_face_encodings, encoding)
            best_match = np.argmin(distances)
            
            if distances[best_match] < 0.6:  # Threshold
                return self.known_face_names[best_match]
        
        return "Unknown User"
```

### Exportar Dados para CSV

```python
# backend/api/export.py (novo arquivo)
import csv
from datetime import datetime

@app.get("/export/expressions/{user_id}")
async def export_expressions(user_id: str):
    expressions = expression_api.expressions.get(user_id, {})
    
    with open(f"expressions_{user_id}_{datetime.now().isoformat()}.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Label", "Blendshape Count", "Created At"])
        for label, blendshapes in expressions.items():
            writer.writerow([label, len(blendshapes), datetime.now()])
    
    return {"file": "expressions_export.csv"}
```

## 🧪 Testando a API

### Com curl

```bash
# Health check
curl http://localhost:8000/health

# Get expressions
curl http://localhost:8000/expressions/Usuario%20Principal

# Register (HTTP POST)
curl -X POST http://localhost:8000/register-expression \
  -H "Content-Type: application/json" \
  -d '{"user_id":"Usuario Principal","label":"Test","blendshapes":[]}'
```

### Com JavaScript (no console do navegador)

```javascript
// Testar WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/process-video');

ws.onopen = () => {
  console.log('Connected');
  // Enviar frame
  ws.send(JSON.stringify({
    action: 'predict',
    frame_base64: '...base64_jpeg_aqui...',
    user_id: 'Usuario Principal'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Resultado:', data);
};
```

### Com Python (test client)

```python
# test_backend.py
import asyncio
import websockets
import json
import base64
import cv2

async def test_websocket():
    uri = "ws://localhost:8000/ws/process-video"
    
    # Ler imagem de teste
    frame = cv2.imread('test_frame.jpg')
    _, img_encoded = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(img_encoded).decode()
    
    async with websockets.connect(uri) as websocket:
        # Enviar frame
        await websocket.send(json.dumps({
            "action": "predict",
            "frame_base64": frame_base64,
            "user_id": "Usuario Principal"
        }))
        
        # Receber resposta
        response = await websocket.recv()
        result = json.loads(response)
        print(f"Result: {result}")

asyncio.run(test_websocket())
```

## 📊 Monitoramento e Debug

### Ativar logs detalhados

```python
# backend/api/server.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.websocket("/ws/process-video")
async def websocket_process_video(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info(f"Client connected. Total: {len(manager.active_connections)}")
    # ...
```

### Monitorar FPS

```javascript
// frontend/src/components/CameraStream.jsx
// Já implementado no componente!
// Ver FPS counter no canto inferior esquerdo da câmera
```

### Profiling

```python
# backend
import cProfile
import pstats

pr = cProfile.Profile()
pr.enable()

# ... código a profilear ...

pr.disable()
ps = pstats.Stats(pr)
ps.print_stats(sort='cumulative')
```

## 🚀 Deploy

### Production Build Frontend

```bash
cd frontend
npm run build
# Output: dist/

# Servir com servidor estático
npx serve -s dist
```

### Production FastAPI

```bash
# Com Gunicorn (UNIX)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.api.server:app

# Ou Hyper (multiplataforma)
pip install hypercorn
hypercorn backend.api.server:app --bind 0.0.0.0:8000
```

### Docker

```dockerfile
# Dockerfile (backend)
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -e .
RUN pip install uvicorn

EXPOSE 8000
CMD ["uvicorn", "backend.api.server:app", "--host", "0.0.0.0"]
```

## 📚 Referências

- [MediaPipe FaceLandmarker](https://ai.google.dev/mediapipe/solutions/vision/face_landmarker)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [React Hooks](https://react.dev/reference/react)
- [Recharts](https://recharts.org/)
- [Tailwind CSS](https://tailwindcss.com/)

## ❓ FAQ

**P: Como aumentar a velocidade de processamento?**
R: Reduzir qualidade JPEG (0.5 em vez de 0.7), limitar resolução canvas (480p em vez de 1080p), usar GPU (CUDA) se disponível.

**P: Como lidar com múltiplos rostos?**
R: Modificar `num_faces=1` em `backend/api/server.py` para `num_faces=4` (etc). Depois adicionar lógica para rastrear por rosto.

**P: Posso usar isso em produção?**
R: Com caution. Atualmente em memória. Requer persistência em DB, autenticação, HTTPS/WSS e testes de carga.

**P: Como integrar com sistema externo?**
R: Usar REST API endpoints HTTP (` /register-expression`, `/expressions/{user_id}`) ou expor WebSocket públicamente com autenticação JWT.
