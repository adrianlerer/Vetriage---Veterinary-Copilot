#!/bin/bash

###############################################################################
# VetrIAge RAG API - Flexible Port Startup Script
###############################################################################
#
# Usage:
#   ./start-rag-api.sh                 # Use default port 8000
#   ./start-rag-api.sh 9000           # Use specific port 9000
#   PORT=8080 ./start-rag-api.sh      # Use environment variable
#
# Port Priority:
#   1. Command line argument (./start-rag-api.sh PORT)
#   2. PORT environment variable
#   3. PORT from .env file
#   4. Default: 8000
#
###############################################################################

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  VetrIAge RAG API - Startup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Determine port (priority order)
if [ -n "$1" ]; then
    # Command line argument has highest priority
    PORT="$1"
    echo -e "${GREEN}✓${NC} Port from command line: ${YELLOW}${PORT}${NC}"
elif [ -n "$PORT" ]; then
    # Environment variable
    echo -e "${GREEN}✓${NC} Port from environment: ${YELLOW}${PORT}${NC}"
elif [ -f .env ]; then
    # Load from .env file
    PORT=$(grep -E "^PORT=" .env | cut -d '=' -f2 | tr -d ' ')
    if [ -n "$PORT" ]; then
        echo -e "${GREEN}✓${NC} Port from .env file: ${YELLOW}${PORT}${NC}"
    else
        PORT=8000
        echo -e "${YELLOW}⚠${NC} No PORT in .env, using default: ${YELLOW}${PORT}${NC}"
    fi
else
    # Default port
    PORT=8000
    echo -e "${YELLOW}⚠${NC} Using default port: ${YELLOW}${PORT}${NC}"
fi

# Determine host
HOST="${HOST:-0.0.0.0}"
echo -e "${GREEN}✓${NC} Host: ${YELLOW}${HOST}${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}✗${NC} No .env file found!"
    echo -e "${YELLOW}ℹ${NC} Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓${NC} Created .env file. ${RED}Please configure API keys before starting!${NC}"
        exit 1
    else
        echo -e "${RED}✗${NC} .env.example not found!"
        exit 1
    fi
fi

# Validate required API keys
echo -e "\n${BLUE}Validating Configuration...${NC}"

missing_keys=0

if ! grep -q "NCBI_API_KEY=.\+" .env; then
    echo -e "${RED}✗${NC} NCBI_API_KEY not configured in .env"
    missing_keys=1
fi

if ! grep -q "OPENAI_API_KEY=sk-.\+" .env; then
    echo -e "${RED}✗${NC} OPENAI_API_KEY not configured in .env"
    missing_keys=1
fi

if ! grep -q "ANTHROPIC_API_KEY=sk-ant-.\+" .env; then
    echo -e "${RED}✗${NC} ANTHROPIC_API_KEY not configured in .env"
    missing_keys=1
fi

if [ $missing_keys -eq 1 ]; then
    echo -e "\n${RED}✗${NC} Missing required API keys. Please configure .env file."
    echo -e "${YELLOW}ℹ${NC} Get API keys from:"
    echo -e "  • NCBI: https://www.ncbi.nlm.nih.gov/account/"
    echo -e "  • OpenAI: https://platform.openai.com/api-keys"
    echo -e "  • Anthropic: https://console.anthropic.com/"
    exit 1
fi

echo -e "${GREEN}✓${NC} All required API keys configured"

# Check dependencies
echo -e "\n${BLUE}Checking Dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} Python 3 not found!"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 available"

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} FastAPI not installed. Installing dependencies..."
    pip install -r requirements.txt
fi
echo -e "${GREEN}✓${NC} Dependencies installed"

# Check if port is available
if command -v lsof &> /dev/null; then
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}✗${NC} Port ${PORT} is already in use!"
        echo -e "${YELLOW}ℹ${NC} Try a different port: ./start-rag-api.sh <port>"
        echo -e "${YELLOW}ℹ${NC} Or kill the process: lsof -ti:$PORT | xargs kill -9"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Port ${PORT} is available"
fi

# Start server
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Starting VetrIAge RAG API...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}URL:${NC} http://${HOST}:${PORT}"
echo -e "${GREEN}Docs:${NC} http://localhost:${PORT}/docs"
echo -e "${GREEN}Health:${NC} http://localhost:${PORT}/api/v2/health"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}ℹ${NC} Press Ctrl+C to stop the server\n"

# Load environment variables and start server
export PORT=$PORT
export HOST=$HOST
source .env 2>/dev/null || true

# Start uvicorn with flexible port
exec uvicorn fastapi_integration:app \
    --host "$HOST" \
    --port "$PORT" \
    --reload \
    --log-level info
