# Documentație ETAPA 2 - Dockerizare

## Descriere

În această etapă am separat componentele sistemului în 3 containere Docker separate:
1. **Ollama** - server LLM cu modelul llama3.2:3b
2. **MCP Server** - server MCP cu HTTP streaming
3. **ADK Agent** - interfața web adk-web cu agentul

## Arhitectura Sistemului

```
┌─────────────────┐
│   adk-web       │ Port 8080 (web UI)
│   (Agent)       │
└────────┬────────┘
         │
         ├──HTTP──> ┌─────────────────┐
         │          │  MCP Server     │ Port 8000
         │          │  (HTTP/SSE)     │
         │          └─────────────────┘
         │
         └──HTTP──> ┌─────────────────┐
                    │    Ollama       │ Port 11434
                    │  llama3.2:3b    │
                    └─────────────────┘
```

## Modificări față de ETAPA 1

### 1. MCP Server (`mcp_server.py`)
- **Transport**: Schimbat de la `stdio` la `http`
- **Configurare**: Folosește variabile de mediu în loc de config.yml
- **Variabile de mediu**:
  - `MCP_TRANSPORT`: tip transport (http/stdio)
  - `MCP_HOST`: host pentru server (0.0.0.0)
  - `MCP_PORT`: port pentru server (8000)
  - `MANAGED_DIR`: directorul administrat
  - `MCP_SERVER_NAME`: nume server

### 2. Agent (`src/agent.py`)
- **Conexiune MCP**: Schimbat de la `StdioConnectionParams` la `SseConnectionParams`
- **Model**: Configurare LiteLlm cu `api_base` pentru a se conecta la Ollama container
- **Variabile de mediu**:
  - `MODEL_NAME`: numele modelului Ollama
  - `OLLAMA_HOST`: URL-ul serverului Ollama
  - `MCP_URL`: URL-ul serverului MCP (HTTP/SSE)

## Fișiere Dockerfile

### Dockerfile.ollama
Creează o imagine Docker cu:
- Ollama server
- Model llama3.2:3b pre-descărcat
- Script de inițializare care pornește serverul și descarcă modelul

### Dockerfile.mcp
Creează o imagine Docker cu:
- Python 3.11
- MCP server cu transport HTTP
- Managed filesystem mount-at ca volum read-only

### Dockerfile.agent
Creează o imagine Docker cu:
- Python 3.11
- ADK agent
- adk-web pentru interfața de chat

## Docker Compose

Fișierul `docker-compose.yml` orchestrează toate cele 3 servicii:

### Servicii

1. **ollama**
   - Port: 11434
   - Volume: `ollama_data` pentru persistența modelelor
   - Healthcheck: verifică disponibilitatea API-ului

2. **mcp-server**
   - Port: 8000
   - Volume: `./managed_fs` montat read-only
   - Depends on: -

3. **agent**
   - Port: 8080 (mapped la 8000 intern)
   - Depends on: ollama (healthy), mcp-server
   - Accesibil la: http://localhost:8080

### Network
- Toate serviciile sunt conectate la rețeaua `aso-network` (bridge)

## Cum să rulezi proiectul

### 1. Build imaginilor Docker

```bash
docker-compose build
```

Aceasta va crea toate cele 3 imagini Docker.

### 2. Pornire containere

```bash
docker-compose up
```

Sau în background:
```bash
docker-compose up -d
```

### 3. Verificare status

```bash
docker-compose ps
```

### 4. Vezi logs

```bash
# Toate serviciile
docker-compose logs -f

# Un singur serviciu
docker-compose logs -f agent
docker-compose logs -f ollama
docker-compose logs -f mcp-server
```

### 5. Accesare interfață web

Deschide browser-ul la:
```
http://localhost:8080
```

Interfața adk-web va permite interacțiunea cu agentul prin chat.

### 6. Oprire containere

```bash
docker-compose down
```

Pentru a șterge și volumele:
```bash
docker-compose down -v
```

## Testare

### Test 1: Verificare conectivitate Ollama
```bash
curl http://localhost:11434/api/tags
```

### Test 2: Verificare MCP Server
```bash
curl http://localhost:8000/mcp
```

### Test 3: Test agent prin interfața web
1. Accesează http://localhost:8080
2. Selectează agentul "system_administration" din dropdown
3. Întreabă: "List all files in the managed directory"
4. Întreabă: "What is the content of test.txt?"

## Troubleshooting

### Problema: Ollama nu pornește
**Soluție**: Verifică dacă ai suficientă memorie RAM (minimum 2GB pentru llama3.2:3b)

### Problema: Agent nu se poate conecta la MCP
**Soluție**: Verifică că mcp-server a pornit corect:
```bash
docker-compose logs mcp-server
```

### Problema: Agent nu se poate conecta la Ollama
**Soluție**: Verifică health check-ul Ollama:
```bash
docker-compose ps
```

### Rebuild după modificări
```bash
docker-compose build --no-cache
docker-compose up --force-recreate
```

## Structura fișierelor

```
proiect-aso/
├── docker-compose.yml           # Orchestrare servicii
├── Dockerfile.ollama            # Imagine Ollama
├── Dockerfile.mcp               # Imagine MCP server
├── Dockerfile.agent             # Imagine Agent + adk-web
├── docker-entrypoint-ollama.sh  # Script init Ollama
├── requirements.txt             # Dependințe Python
├── .dockerignore               # Fișiere excluse din build
├── mcp_server.py               # Server MCP (modificat pt HTTP)
├── src/
│   └── agent.py                # Agent (modificat pt HTTP)
├── config/
│   ├── config.yml              # Config (opțional acum)
│   └── get_config.py           # Utilitar config
└── managed_fs/                 # Filesystem administrat
    ├── test.txt
    ├── data.txt
    └── subfolder/
        └── file.txt
```

## Dependințe Python

Fișierul `requirements.txt` conține:
- google-adk: Framework pentru agent
- mcp: Model Context Protocol
- pyyaml: Parsing YAML
- python-box: Config management
- uvicorn: ASGI server
- fastapi: Web framework (folosit de FastMCP)

## Bonus: Autentificare MCP Server

Pentru a adăuga autentificare la MCP server (bonus), modifcă `src/agent.py`:

```python
mcp_connection = SseConnectionParams(
    url=MCP_URL,
    headers={"Authorization": "Bearer your-secret-token"}
)
```

Și `mcp_server.py` pentru a valida token-ul în middleware.

## Concluzie

ETAPA 2 a implementat cu succes:
- ✅ Imagine Docker pentru Ollama cu model llama3.2:3b
- ✅ Imagine Docker pentru MCP server cu HTTP streaming
- ✅ Imagine Docker pentru adk-web + agent
- ✅ docker-compose pentru orchestrare
- ✅ Comunicare inter-containere prin HTTP/SSE
- ✅ Persistență date Ollama prin volumes
- ✅ Health checks pentru disponibilitate servicii
