# 🔌 VetrIAge RAG - Flexible Port Configuration

## ⚡ Core Principle: NEVER HARDCODE PORTS

This system follows the **Flexible Port System** design pattern, ensuring zero conflicts in multi-service environments, CI/CD pipelines, and production deployments.

---

## 📋 Port Configuration Priority

The system uses a **cascading priority order** for port selection:

```
1. Command Line Argument (highest priority)
   └─> ./start-rag-api.sh 9000

2. PORT Environment Variable
   └─> PORT=8080 python fastapi_integration.py

3. .env File Configuration
   └─> PORT=8000 in .env

4. Default Fallback (lowest priority)
   └─> 8000
```

---

## 🚀 Usage Examples

### Method 1: Startup Script (RECOMMENDED)

```bash
cd /home/user/webapp/cognition_base/rag

# Use default port (8000)
./start-rag-api.sh

# Use custom port via argument
./start-rag-api.sh 9000

# Use custom port via environment variable
PORT=8080 ./start-rag-api.sh

# Custom host and port
HOST=127.0.0.1 PORT=3001 ./start-rag-api.sh
```

**Benefits:**
- ✅ Automatic port conflict detection
- ✅ API key validation
- ✅ Dependency checking
- ✅ Clean colored output
- ✅ Environment loading

---

### Method 2: Direct Uvicorn Execution

```bash
# With environment variable
PORT=9000 uvicorn fastapi_integration:app --reload

# With host and port
PORT=8080 HOST=0.0.0.0 uvicorn fastapi_integration:app --reload

# Load from .env automatically
uvicorn fastapi_integration:app --reload
```

---

### Method 3: Python Module Execution

```bash
# Simple port override
PORT=9000 python fastapi_integration.py

# Full configuration
HOST=0.0.0.0 PORT=8080 python fastapi_integration.py

# Using .env file
python fastapi_integration.py  # Reads PORT from .env
```

---

## 🔧 Configuration Files

### .env File Setup

```bash
# Copy example template
cp .env.example .env

# Edit port configuration
nano .env
```

**.env content:**
```bash
# Server Configuration (⚡ FLEXIBLE PORT SYSTEM)
PORT=8000                    # Override with PORT=9000 python ...
HOST=0.0.0.0                # Bind to all interfaces
```

---

## 🌐 Multi-Instance Deployment

### Running Multiple RAG Instances

```bash
# Terminal 1: Development instance
PORT=8000 ./start-rag-api.sh &

# Terminal 2: Testing instance
PORT=9000 ./start-rag-api.sh &

# Terminal 3: Staging instance
PORT=10000 ./start-rag-api.sh &
```

### Docker Compose

```yaml
version: '3.8'

services:
  rag-api-prod:
    build: .
    ports:
      - "${PORT:-8000}:${PORT:-8000}"
    environment:
      - PORT=${PORT:-8000}
      - HOST=0.0.0.0
    env_file:
      - .env

  rag-api-dev:
    build: .
    ports:
      - "${DEV_PORT:-9000}:${DEV_PORT:-9000}"
    environment:
      - PORT=${DEV_PORT:-9000}
      - HOST=0.0.0.0
    env_file:
      - .env.dev
```

**Start containers:**
```bash
# Production on port 8000
PORT=8000 docker-compose up rag-api-prod

# Development on port 9000
DEV_PORT=9000 docker-compose up rag-api-dev
```

---

## 🧪 CI/CD Integration

### GitHub Actions

```yaml
name: RAG API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        port: [8000, 8080, 9000]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd cognition_base/rag
          pip install -r requirements.txt
      
      - name: Start RAG API
        run: |
          cd cognition_base/rag
          PORT=${{ matrix.port }} python fastapi_integration.py &
          sleep 5
        env:
          PORT: ${{ matrix.port }}
          NCBI_API_KEY: ${{ secrets.NCBI_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      
      - name: Test health endpoint
        run: |
          curl http://localhost:${{ matrix.port }}/api/v2/health
```

### Random Port Assignment (Conflict Avoidance)

```bash
# Generate random port between 8000-9000
PORT=$(shuf -i 8000-9000 -n 1)
echo "Using random port: $PORT"
./start-rag-api.sh $PORT
```

---

## 🔍 Port Verification

### Check Current Port Configuration

```bash
# View environment variables
echo "PORT: ${PORT:-8000}"
echo "HOST: ${HOST:-0.0.0.0}"

# View .env configuration
grep -E "^(PORT|HOST)=" .env

# List all environment variables
env | grep -E "(PORT|HOST|API_URL)"
```

### Check If Port Is In Use

```bash
# Check specific port
lsof -i :8000

# Check and kill process on port
lsof -ti:8000 | xargs kill -9

# Find available port
for port in {8000..8100}; do
  ! lsof -i:$port &>/dev/null && echo "Port $port available" && break
done
```

### Test API After Startup

```bash
export PORT=9000  # Set to your configured port

# Health check
curl http://localhost:${PORT}/api/v2/health

# Root endpoint
curl http://localhost:${PORT}/

# OpenAPI docs
open http://localhost:${PORT}/docs
```

---

## 🚫 Anti-Patterns (DO NOT DO THIS)

### ❌ WRONG: Hardcoded Port

```python
# BAD - Don't do this!
uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
# BAD - Don't do this!
curl http://localhost:8000/api/v2/health
```

```javascript
// BAD - Don't do this!
const API_URL = 'http://localhost:8000';
```

---

### ✅ CORRECT: Dynamic Port

```python
# GOOD - Use environment variable
port = int(os.getenv("PORT", "8000"))
uvicorn.run(app, host="0.0.0.0", port=port)
```

```bash
# GOOD - Use PORT variable
curl http://localhost:${PORT}/api/v2/health
```

```javascript
// GOOD - Use environment variable
const API_URL = process.env.REACT_APP_API_URL || `http://localhost:${process.env.PORT || 8000}`;
```

---

## 🌍 Production Best Practices

### 1. Use Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Start with flexible port
PORT=8000 pm2 start fastapi_integration.py --name rag-api-prod --interpreter python3

# Start multiple instances
PORT=8000 pm2 start fastapi_integration.py --name rag-api-1
PORT=9000 pm2 start fastapi_integration.py --name rag-api-2
PORT=10000 pm2 start fastapi_integration.py --name rag-api-3

# Check status
pm2 status

# View logs
pm2 logs rag-api-prod
```

### 2. Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/vetriage-rag

upstream rag_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    server_name api.vetriage.com;

    location /api/v2/ {
        proxy_pass http://rag_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Systemd Service

```ini
# /etc/systemd/system/vetriage-rag.service

[Unit]
Description=VetrIAge RAG API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/webapp/cognition_base/rag
Environment="PORT=8000"
Environment="HOST=0.0.0.0"
EnvironmentFile=/home/user/webapp/cognition_base/rag/.env
ExecStart=/usr/bin/python3 fastapi_integration.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable vetriage-rag
sudo systemctl start vetriage-rag
sudo systemctl status vetriage-rag
```

---

## 📊 Monitoring & Logging

### Log Port on Startup

The system automatically logs:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  VetrIAge RAG API - Startup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Port from environment: 9000
✓ Host: 0.0.0.0
✓ All required API keys configured
✓ Dependencies installed
✓ Port 9000 is available
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Starting VetrIAge RAG API...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URL: http://0.0.0.0:9000
Docs: http://localhost:9000/docs
Health: http://localhost:9000/api/v2/health
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🆘 Troubleshooting

### Port Already In Use

```bash
# Error: Address already in use
ERROR: [Errno 48] Address already in use

# Solution 1: Check what's using the port
lsof -i :8000

# Solution 2: Kill process on port
lsof -ti:8000 | xargs kill -9

# Solution 3: Use different port
PORT=9000 ./start-rag-api.sh
```

### Port Not Detected

```bash
# Check environment variable
echo $PORT

# Check .env file
cat .env | grep PORT

# Force port explicitly
PORT=8000 python fastapi_integration.py
```

### Health Check Fails

```bash
# Wrong (hardcoded port)
curl http://localhost:8000/api/v2/health  # May fail if different port

# Correct (dynamic port)
curl http://localhost:${PORT}/api/v2/health
```

---

## 📚 Related Documentation

- [Main README](./README.md) - Complete RAG system documentation
- [fastapi_integration.py](./fastapi_integration.py) - FastAPI application code
- [start-rag-api.sh](./start-rag-api.sh) - Startup script source
- [.env.example](./.env.example) - Environment template

---

## ✅ Quick Reference Card

| Action | Command |
|--------|---------|
| Start with default port | `./start-rag-api.sh` |
| Start with custom port | `./start-rag-api.sh 9000` |
| Check current port | `echo ${PORT:-8000}` |
| Test health endpoint | `curl http://localhost:${PORT}/api/v2/health` |
| View logs | `tail -f logs/uvicorn.log` |
| Stop server | `Ctrl+C` or `pkill -f fastapi_integration` |
| Find available port | `./start-rag-api.sh $(shuf -i 8000-9000 -n 1)` |

---

**Version**: 2.0.0  
**Last Updated**: February 2026  
**Maintainer**: VetrIAge Development Team  
**License**: MIT
