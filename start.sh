#!/usr/bin/env bash
# Brain-Radio Startup Script
# Starts the application and opens the browser

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
USE_DOCKER="${USE_DOCKER:-true}"
WAIT_FOR_SERVICES="${WAIT_FOR_SERVICES:-true}"
OPEN_BROWSER="${OPEN_BROWSER:-true}"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Brain-Radio Startup Script          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    local port=$1
    if command_exists lsof; then
        lsof -i ":${port}" >/dev/null 2>&1
    elif command_exists netstat; then
        netstat -an | grep -q ":${port}.*LISTEN"
    else
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}Waiting for service at ${url}...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "${url}" >/dev/null 2>&1 || curl -s -f "${url}/api/health" >/dev/null 2>&1; then
            echo -e "${GREEN}Service is ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    echo ""
    echo -e "${RED}Service did not become ready in time${NC}"
    return 1
}

# Function to open browser
open_browser() {
    local url=$1
    
    if [ "${OPEN_BROWSER}" != "true" ]; then
        return 0
    fi
    
    echo -e "${BLUE}Opening browser at ${url}...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "${url}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists xdg-open; then
            xdg-open "${url}"
        elif command_exists gnome-open; then
            gnome-open "${url}"
        else
            echo -e "${YELLOW}Could not find browser launcher. Please open ${url} manually.${NC}"
        fi
    else
        echo -e "${YELLOW}Unsupported OS. Please open ${url} manually.${NC}"
    fi
}

# Check for Docker if using Docker mode
if [ "${USE_DOCKER}" = "true" ]; then
    if ! command_exists docker; then
        echo -e "${RED}ERROR: Docker is not installed or not in PATH${NC}"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        echo -e "${RED}ERROR: docker-compose is not installed or not in PATH${NC}"
        echo "Please install docker-compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker found${NC}"
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}ERROR: Docker daemon is not running${NC}"
        echo "Please start Docker Desktop or the Docker daemon"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker daemon is running${NC}"
fi

# Check for required environment variables
echo ""
echo -e "${BLUE}Checking environment variables...${NC}"

MISSING_VARS=()

if [ -z "${SPOTIFY_CLIENT_ID:-}" ]; then
    MISSING_VARS+=("SPOTIFY_CLIENT_ID")
fi

if [ -z "${SPOTIFY_CLIENT_SECRET:-}" ]; then
    MISSING_VARS+=("SPOTIFY_CLIENT_SECRET")
fi

# Check .env file
if [ -f .env ]; then
    echo -e "${GREEN}✓ Found .env file${NC}"
    # Source .env file to load variables
    set -a
    source .env
    set +a
    
    # Re-check after loading .env
    MISSING_VARS=()
    if [ -z "${SPOTIFY_CLIENT_ID:-}" ]; then
        MISSING_VARS+=("SPOTIFY_CLIENT_ID")
    fi
    if [ -z "${SPOTIFY_CLIENT_SECRET:-}" ]; then
        MISSING_VARS+=("SPOTIFY_CLIENT_SECRET")
    fi
else
    echo -e "${YELLOW}⚠ .env file not found${NC}"
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}ERROR: Missing required environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "  ${RED}- ${var}${NC}"
    done
    echo ""
    echo "Please set them in your .env file or export them:"
    echo "  export SPOTIFY_CLIENT_ID=\"your_client_id\""
    echo "  export SPOTIFY_CLIENT_SECRET=\"your_client_secret\""
    echo "  export SPOTIFY_REDIRECT_URI=\"http://127.0.0.1:8000/api/auth/callback\""
    exit 1
fi

echo -e "${GREEN}✓ All required environment variables are set${NC}"

# Check for package-lock.json if using Docker
if [ "${USE_DOCKER}" = "true" ]; then
    if [ ! -f frontend/package-lock.json ]; then
        echo ""
        echo -e "${YELLOW}⚠ package-lock.json not found in frontend directory${NC}"
        echo -e "${YELLOW}Generating package-lock.json...${NC}"
        
        if command_exists npm; then
            cd frontend
            npm install
            cd "${ROOT_DIR}"
            echo -e "${GREEN}✓ package-lock.json generated${NC}"
        else
            echo -e "${YELLOW}⚠ npm not found. Docker build will generate it automatically.${NC}"
        fi
    else
        echo -e "${GREEN}✓ package-lock.json found${NC}"
    fi
fi

# Start the application
echo ""
echo -e "${BLUE}Starting Brain-Radio...${NC}"

if [ "${USE_DOCKER}" = "true" ]; then
    # Check if ports are already in use
    if port_in_use 8000; then
        echo -e "${YELLOW}⚠ Port 8000 is already in use${NC}"
    fi
    if port_in_use 3000; then
        echo -e "${YELLOW}⚠ Port 3000 is already in use${NC}"
    fi
    
    # Determine which docker-compose file to use
    COMPOSE_FILE="docker-compose.yml"
    if [ -f "docker-compose.dev.yml" ] && [ "${USE_DOCKER}" = "true" ]; then
        # Prefer dev file for development
        COMPOSE_FILE="docker-compose.dev.yml"
    fi
    
    echo -e "${BLUE}Using ${COMPOSE_FILE}${NC}"
    echo ""
    
    # Start docker-compose in background
    if docker compose version >/dev/null 2>&1; then
        docker compose -f "${COMPOSE_FILE}" up --build -d
    else
        docker-compose -f "${COMPOSE_FILE}" up --build -d
    fi
    
    echo ""
    echo -e "${GREEN}✓ Services started${NC}"
    
    if [ "${WAIT_FOR_SERVICES}" = "true" ]; then
        echo ""
        # Wait for backend
        if wait_for_service "${BACKEND_URL}"; then
            echo -e "${GREEN}✓ Backend is ready${NC}"
        else
            echo -e "${YELLOW}⚠ Backend may not be ready yet${NC}"
        fi
        
        # Wait for frontend
        if wait_for_service "${FRONTEND_URL}"; then
            echo -e "${GREEN}✓ Frontend is ready${NC}"
        else
            echo -e "${YELLOW}⚠ Frontend may not be ready yet${NC}"
        fi
    fi
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Brain-Radio is running!             ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "Frontend: ${BLUE}${FRONTEND_URL}${NC}"
    echo -e "Backend:  ${BLUE}${BACKEND_URL}${NC}"
    echo ""
    echo "To view logs:"
    if docker compose version >/dev/null 2>&1; then
        echo "  docker compose -f ${COMPOSE_FILE} logs -f"
    else
        echo "  docker-compose -f ${COMPOSE_FILE} logs -f"
    fi
    echo ""
    echo "To stop:"
    if docker compose version >/dev/null 2>&1; then
        echo "  docker compose -f ${COMPOSE_FILE} down"
    else
        echo "  docker-compose -f ${COMPOSE_FILE} down"
    fi
    echo ""
    
    # Open browser
    if [ "${OPEN_BROWSER}" = "true" ]; then
        sleep 2  # Give services a moment to fully start
        open_browser "${FRONTEND_URL}"
    fi
    
else
    # Local development mode (not implemented in this script)
    echo -e "${YELLOW}Local development mode not implemented in this script${NC}"
    echo "Please use Docker mode or start services manually:"
    echo "  Terminal 1: uvicorn src.brain_radio.api.main:app --reload --port 8000"
    echo "  Terminal 2: cd frontend && npm run dev"
    exit 1
fi

