# 🔌 VetrIAge Project - Flexible Port Standard

## 🎯 Core Principle

**🚫 NEVER HARDCODE PORTS IN ANY PROJECT FILE**

All services in the VetrIAge ecosystem must use **dynamic port configuration** to prevent conflicts in development, testing, and production environments.

---

## 📋 Standard Implementation

### 1. Configuration Priority Order

Every service MUST follow this priority order:

```
1. Command Line Argument        (Highest Priority)
2. Environment Variable
3. .env File Configuration
4. Default Fallback Value       (Lowest Priority)
```

### 2. Code Implementation

#### Python/FastAPI Services

```python
import os
import uvicorn

# ✅ CORRECT: Read from environment with fallback
port = int(os.getenv("PORT", "8000"))
host = os.getenv("HOST", "0.0.0.0")

uvicorn.run(app, host=host, port=port)
```

#### Node.js/Express Services

```javascript
// ✅ CORRECT: Read from environment with fallback
const port = process.env.PORT || 8000;
const host = process.env.HOST || '0.0.0.0';

app.listen(port, host, () => {
  console.log(`Server running on ${host}:${port}`);
});
```

#### Bash/Shell Scripts

```bash
#!/bin/bash

# ✅ CORRECT: Port argument or environment variable
PORT="${1:-${PORT:-8000}}"
HOST="${HOST:-0.0.0.0}"

echo "Starting service on ${HOST}:${PORT}"
```

---

## 🏗️ Project-Wide Implementation

### Required Files in Every Service

1. **Startup Script**: `start-[service-name].sh`
   - Accepts port as argument
   - Validates port availability
   - Checks environment variables
   - Loads .env file

2. **Environment Template**: `.env.example`
   ```bash
   # Server Configuration (⚡ FLEXIBLE PORT SYSTEM)
   PORT=8000                    # Default port
   HOST=0.0.0.0                # Bind address
   ```

3. **Port Configuration Docs**: `PORT_CONFIGURATION.md`
   - Usage examples
   - Troubleshooting
   - Best practices

---

## 📁 VetrIAge Services Port Registry

| Service | Default Port | Range | Script |
|---------|-------------|-------|--------|
| RAG API | 8000 | 8000-8999 | `cognition_base/rag/start-rag-api.sh` |
| Main Backend | 3000 | 3000-3999 | `scripts/start-backend.sh` |
| Frontend Dev | 5173 | 5000-5999 | `scripts/start-frontend.sh` |
| Evidence API | 9000 | 9000-9999 | `scripts/start-evidence-api.sh` |

**Note**: These are DEFAULT ports only. Any service can run on any available port using environment configuration.

---

## 🚀 Usage Patterns

### Single Service

```bash
# Default port
./start-rag-api.sh

# Custom port via argument
./start-rag-api.sh 9000

# Custom port via environment
PORT=8080 ./start-rag-api.sh
```

### Multiple Services (Development)

```bash
# Terminal 1: RAG API
PORT=8000 ./cognition_base/rag/start-rag-api.sh &

# Terminal 2: Main Backend
PORT=3000 ./scripts/start-backend.sh &

# Terminal 3: Frontend
PORT=5173 npm run dev &
```

### Docker Compose

```yaml
version: '3.8'

services:
  rag-api:
    build: ./cognition_base/rag
    ports:
      - "${RAG_PORT:-8000}:${RAG_PORT:-8000}"
    environment:
      - PORT=${RAG_PORT:-8000}
      - HOST=0.0.0.0
    env_file:
      - .env

  backend:
    build: ./backend
    ports:
      - "${BACKEND_PORT:-3000}:${BACKEND_PORT:-3000}"
    environment:
      - PORT=${BACKEND_PORT:-3000}
      - HOST=0.0.0.0
    env_file:
      - .env

  frontend:
    build: ./frontend
    ports:
      - "${FRONTEND_PORT:-5173}:${FRONTEND_PORT:-5173}"
    environment:
      - PORT=${FRONTEND_PORT:-5173}
    env_file:
      - .env
```

**Start all services:**
```bash
RAG_PORT=8000 BACKEND_PORT=3000 FRONTEND_PORT=5173 docker-compose up
```

---

## 🧪 CI/CD Integration

### GitHub Actions

```yaml
name: Multi-Service Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Start RAG API (Dynamic Port)
        run: |
          PORT=$(shuf -i 8000-8100 -n 1)
          echo "RAG_PORT=$PORT" >> $GITHUB_ENV
          PORT=$PORT ./cognition_base/rag/start-rag-api.sh &
          sleep 5
      
      - name: Start Backend (Dynamic Port)
        run: |
          PORT=$(shuf -i 3000-3100 -n 1)
          echo "BACKEND_PORT=$PORT" >> $GITHUB_ENV
          PORT=$PORT ./scripts/start-backend.sh &
          sleep 5
      
      - name: Test Services
        run: |
          curl http://localhost:$RAG_PORT/api/v2/health
          curl http://localhost:$BACKEND_PORT/health
```

---

## 📝 Code Review Checklist

When reviewing PRs, verify:

- [ ] **No hardcoded ports** in any `.py`, `.js`, `.ts`, `.sh` files
- [ ] **Environment variable** used for port configuration
- [ ] **Default fallback** value provided
- [ ] **Startup script** accepts port as argument
- [ ] **Documentation** updated with flexible port examples
- [ ] **curl/fetch URLs** use `${PORT}` variable
- [ ] **README** shows PORT configuration methods

---

## 🚫 Common Anti-Patterns

### ❌ WRONG

```python
# Hardcoded port
uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
# Hardcoded URL
curl http://localhost:8000/health
```

```javascript
// Hardcoded API URL
const API_URL = 'http://localhost:8000';
```

```yaml
# Hardcoded Docker port
ports:
  - "8000:8000"
```

---

### ✅ CORRECT

```python
# Dynamic port
port = int(os.getenv("PORT", "8000"))
uvicorn.run(app, host="0.0.0.0", port=port)
```

```bash
# Dynamic URL
curl http://localhost:${PORT}/health
```

```javascript
// Dynamic API URL
const API_URL = process.env.REACT_APP_API_URL || `http://localhost:${process.env.PORT || 8000}`;
```

```yaml
# Dynamic Docker port
ports:
  - "${PORT:-8000}:${PORT:-8000}"
```

---

## 🔍 Port Conflict Detection

### Manual Check

```bash
# Check if port is in use
lsof -i :8000

# Find available port
for port in {8000..8100}; do
  ! lsof -i:$port &>/dev/null && echo "Port $port available" && break
done
```

### Automated in Startup Scripts

All startup scripts SHOULD include:

```bash
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "❌ Port $PORT is already in use!"
    echo "💡 Try: ./start-service.sh <different-port>"
    exit 1
fi
```

---

## 🌍 Production Deployment

### Kubernetes

```yaml
apiVersion: v1
kind: Service
metadata:
  name: rag-api
spec:
  selector:
    app: rag-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: rag-port  # Dynamic reference
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-api
spec:
  template:
    spec:
      containers:
      - name: rag-api
        image: vetriage/rag-api:latest
        ports:
        - name: rag-port
          containerPort: 8000  # Can be overridden
        env:
        - name: PORT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: rag-api-port
```

### Nginx Load Balancer

```nginx
# /etc/nginx/sites-available/vetriage

upstream rag_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

upstream main_backend {
    server localhost:3000;
    server localhost:3001;
    server localhost:3002;
}

server {
    listen 80;
    server_name api.vetriage.com;

    location /api/v2/rag/ {
        proxy_pass http://rag_backend;
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://main_backend;
        proxy_set_header Host $host;
    }
}
```

---

## 📊 Monitoring

### Log Port Configuration

All services MUST log their port on startup:

```
✓ Starting [ServiceName] on 0.0.0.0:9000
✓ Health check: http://localhost:9000/health
✓ API Docs: http://localhost:9000/docs
```

### Prometheus Metrics

```python
from prometheus_client import Info

service_info = Info('service_info', 'Service configuration')
service_info.info({
    'port': str(port),
    'host': host,
    'environment': os.getenv('ENVIRONMENT', 'development')
})
```

---

## 🆘 Troubleshooting Guide

### Problem: Port conflict error

```bash
# Error: Address already in use

# Solution 1: Check what's using the port
lsof -i :8000

# Solution 2: Use different port
PORT=9000 ./start-service.sh

# Solution 3: Kill process on port
lsof -ti:8000 | xargs kill -9
```

### Problem: Service not accessible

```bash
# Check service is running on expected port
ps aux | grep python
netstat -tlnp | grep 8000

# Check firewall
sudo ufw status
sudo iptables -L
```

### Problem: Environment variable not detected

```bash
# Verify environment
echo $PORT
env | grep PORT

# Check .env file
cat .env | grep PORT

# Force explicit port
PORT=8000 ./start-service.sh
```

---

## 📚 Related Documentation

- [RAG API Port Configuration](./cognition_base/rag/PORT_CONFIGURATION.md)
- [Main README](./README.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Development Setup](./docs/DEVELOPMENT.md)

---

## ✅ Compliance Verification

### Automated Check Script

Create `scripts/check-port-compliance.sh`:

```bash
#!/bin/bash

echo "🔍 Checking port hardcoding compliance..."

# Find hardcoded ports in Python
echo "Checking Python files..."
PYTHON_VIOLATIONS=$(grep -r "port=800\|port=900\|port=300\|port=500" --include="*.py" . | grep -v "PORT\|getenv" || true)

# Find hardcoded ports in JavaScript
echo "Checking JavaScript/TypeScript files..."
JS_VIOLATIONS=$(grep -r "localhost:800\|localhost:900\|localhost:300\|localhost:500" --include="*.js" --include="*.ts" . | grep -v "process.env.PORT\|import.meta.env" || true)

# Find hardcoded ports in Shell scripts
echo "Checking Shell scripts..."
SH_VIOLATIONS=$(grep -r "PORT=800\|PORT=900" --include="*.sh" . | grep -v '\${PORT' || true)

# Report violations
if [ -n "$PYTHON_VIOLATIONS" ] || [ -n "$JS_VIOLATIONS" ] || [ -n "$SH_VIOLATIONS" ]; then
    echo "❌ Port hardcoding violations found:"
    [ -n "$PYTHON_VIOLATIONS" ] && echo "$PYTHON_VIOLATIONS"
    [ -n "$JS_VIOLATIONS" ] && echo "$JS_VIOLATIONS"
    [ -n "$SH_VIOLATIONS" ] && echo "$SH_VIOLATIONS"
    exit 1
else
    echo "✅ No port hardcoding violations found"
    exit 0
fi
```

**Run before commits:**
```bash
./scripts/check-port-compliance.sh
```

---

## 🎓 Training & Onboarding

### New Developer Checklist

When onboarding new developers, ensure they understand:

- [ ] Never hardcode ports in any file
- [ ] Always use `PORT` environment variable
- [ ] Provide default fallback values
- [ ] Use startup scripts for services
- [ ] Test with multiple port configurations
- [ ] Document port configuration in README
- [ ] Update `.env.example` with PORT variable

---

## 📜 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | Feb 2026 | Complete flexible port system implemented |
| 1.5.0 | Jan 2026 | Added Docker Compose support |
| 1.0.0 | Dec 2025 | Initial port standard defined |

---

**Maintainer**: VetrIAge Development Team  
**Last Updated**: February 2026  
**Status**: Mandatory Standard  
**License**: MIT
