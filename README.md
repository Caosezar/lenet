# Expression Recognition Dashboard

Sistema de reconhecimento e classificação de expressões faciais em tempo real usando MediaPipe, FastAPI e React.

## 🚀 Arquitetura

- **Backend**: FastAPI + WebSocket (processamento de video + IA)
- **Frontend**: React + Vite + Tailwind CSS + shadcnUI (interface web em tempo real)
- **Processamento**: MediaPipe FaceLandmarker (52 blendshapes)
- **Fonte**: JetBrains Mono (design profissional)

## 📋 Requisitos

- Python 3.12+
- Node.js 16+
- npm ou yarn
- Webcam funcionando

## ⚙️ Instalação

### Backend

1. **Instalar dependências Python**:
```bash
uv add fastapi uvicorn mediapipe opencv-python pillow numpy pydantic
```

2. **Modelo MediaPipe** (já baixado automaticamente):
```bash
# O arquivo `core/face_landmarker.task` deve estar presente
ls core/face_landmarker.task
```

3. **Rodar servidor FastAPI**:
```bash
uv run uvicorn backend.api.server:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000`

### Frontend

1. **Navegar para o diretório frontend**:
```bash
cd frontend
```

2. **Instalar dependências Node**:
```bash
npm install
```

3. **Rodar servidor de desenvolvimento**:
```bash
npm run dev
```

Acesse em `http://localhost:5173`

## 📊 Como Usar

1. **Conectar câmera**:
   - Abra o dashboard em `http://localhost:5173`
   - Permita acesso à câmera
   - O status "Conectado" aparecerá no canto superior

2. **Ver dados em tempo real**:
   - O bloco "AI Expression Data" mostra:
     - Usuário detectado
     - Expressão atual
     - Confiança (%)
     - Latência de processamento
   - Clique na seta para expandir e ver os 52 blendshapes

3. **Registrar uma expressão**:
   - Faça uma expressão (ex: sorrir)
   - Escreva um rótulo (ex: "Sorrindo")
   - Clique "Registrar"
   - A expressão será salva na memória

4. **Reconhecer expressão**:
   - Reproduza a expressão registrada
   - O sistema detectará automaticamente com confiança (%)

5. **Monitorar performance**:
   - O gráfico mostra latência dos últimos 30 segundos
   - Valores típicos: 20-50ms em máquina moderna

## 🔌 Endpoints WebSocket

### POST /register-expression
```json
{
  "user_id": "Usuario Principal",
  "label": "Sorrindo",
  "blendshapes": [
    {"category_name": "mouthSmile", "score": 0.85},
    ...
  ]
}
```

### WS /ws/process-video

**Message (predição)**:
```json
{
  "action": "predict",
  "frame_base64": "...",
  "user_id": "Usuario Principal"
}
```

**Response**:
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
    ...
  ]
}
```

**Message (registrar)**:
```json
{
  "action": "register",
  "frame_base64": "...",
  "user_id": "Usuario Principal",
  "label": "Sorrindo"
}
```

## 🎨 Design

- **Darkmode**: Paleta `slate-900` e `slate-950`
- **Acentos**: Verde neon (`#00ff00`)
- **Fonte**: JetBrains Mono (monoespacial)
- **Layout**:
  - ➜ Câmera à esquerda (grande)
  - ➜ Dados + Gráfico + Input à direita (coluna)
  - ➜ Responsive (mobile-friendly)

## 📈 Performance

- **FPS**: 30 FPS captura contínua
- **Latência**: 20-50ms por frame (processamento + IA)
- **Banda**: ~30-50 KB/s (Base64 JPEG comprimido)
- **CPU**: < 5% em máquina moderna (i7/Ryzen 5+)

## 🐛 Troubleshooting

### Câmera não conecta
```bash
# Verificar permissões no navegador
# Chrome: Configurações > Privacidade > Câmera > Permitir localhost:5173
```

### WebSocket não conecta
```bash
# Verificar se backend está rodando em http://localhost:8000
curl http://localhost:8000/health
```

### Frames muito lentos
```bash
# Reduzir qualidade JPEG (arquivo: frontend/src/utils/canvasUtils.js)
# Linha: return dataUri.split(',')[1];
# Mudar quality de 0.7 para 0.5
```

## 📂 Estrutura do Projeto

```
lenet/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── models.py       # Pydantic schemas
│   │   ├── core.py         # Lógica IA (FacialRecognitionAPI + ExpressionAPI)
│   │   └── server.py       # FastAPI app + WebSocket
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CameraStream.jsx
│   │   │   ├── DataBlock.jsx
│   │   │   ├── LatencyGraph.jsx
│   │   │   └── ExpressionRegister.jsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.js
│   │   ├── utils/
│   │   │   └── canvasUtils.js
│   │   ├── pages/
│   │   │   └── Dashboard.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   └── .gitignore
├── core/
│   ├── face_landmarker.task
│   ├── JetBrainsMono-Regular.ttf
│   └── webcam_mediapipe.py (legado)
├── pyproject.toml
├── main.py
└── README.md
```

## 🔮 Future Features

- [ ] Persistência em banco de dados (SQLite/PostgreSQL)
- [ ] Autenticação multi-usuário
- [ ] Face embedding real (face_recognition lib)
- [ ] Exportar dados para CSV
- [ ] Dashboard admin
- [ ] Mobile app (React Native)
- [ ] Análise de emoções (anger, happy, sad, etc)

## 📝 Licença

MIT © 2026

## 👨‍💻 Autor

Desenvolvido com ❤️ e cafeína ☕
