# 🚀 QUICK START - Expression Recognition

## 5 Minutos para Rodar a Aplicação

### 1️⃣ Backend (FastAPI)

Abra o primeiro terminal na pasta **raiz** do projeto:

```bash
uv run uvicorn backend.api.server:app --reload --port 8000
```

✅ Você verá:
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

### 2️⃣ Frontend (React)

Abra o segundo terminal na pasta **raiz**:

```bash
cd frontend
npm install
npm run dev
```

✅ Você verá:
```
VITE v5.0.0  ready in 234 ms

➜  Local:   http://localhost:5173/
➜  Press h to show help
```

### 3️⃣ Acessar a Aplicação

Abra no navegador: **http://localhost:5173**

## ✅ Verificar se Tudo Funciona

1. **Câmera conectada?**
   - Deve aparecer o feed ao vivo
   - Status "Conectado" no canto superior direito

2. **Dados aparecem?**
   - Bloco "AI Expression Data" mostra informações em tempo real
   - Latência < 50ms é normal

3. **Gráfico atualiza?**
   - O graph de latência desenha linha verde contínua

## 📝 Como Usar

```
1. Apareça na câmera com uma expressão
   (ex: sorrir)

2. Escreva um rótulo no input abaixo
   (ex: "Sorrindo")

3. Clique o botão "Registrar"
   (a expressão é salva)

4. Reproduza a mesma expressão
   (o sistema detecta automaticamente!)
```

## 🛑 Para Parar

- Terminal 1: `Ctrl + C`
- Terminal 2: `Ctrl + C`

## 📂 Arquivo de Referência

| Pasta | Descrição |
|-------|-----------|
| `backend/api/` | Servidor FastAPI + IA |
| `frontend/src/` | Interface React |
| `core/` | Modelos MediaPipe |
| `README.md` | Documentação completa |
| `DEVELOPMENT.md` | Guia técnico detalhado |

## 🆘 Problemas Comuns

### "WebSocket connection failed"
→ Certificar que backend está rodando em `http://localhost:8000`

### "Camera not found"
→ Permitir acesso à câmera no navegador (Chrome: permissões do site)

### "npm: command not found"
→ Instalar Node.js de https://nodejs.org/

### "Python not found"
→ Instalar Python 3.12+ de https://python.org/

## 🎥 Demo

Veja o projeto em ação:
1. Abrir câmera → frames capturados
2. Dados em tempo real → bloco atualiza 30 FPS
3. Registrar expressão → salva na memória
4. Reproduzir → sistema detecta com confiança %

---

**Próximas etapas?** Veja `DEVELOPMENT.md` para integração com banco de dados, autenticação, e deploy em produção.
