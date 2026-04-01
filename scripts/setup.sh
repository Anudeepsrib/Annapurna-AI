#!/bin/bash
# Annapurna-AI Local Setup Script (macOS/Linux)
# This script sets up the local-first version of Annapurna-AI

set -e

echo "🍛 Annapurna-AI Local Setup"
echo "============================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 20+ first.${NC}"
    exit 1
fi
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo -e "${RED}❌ Node.js version 20+ required. Found: $(node --version)${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js $(node --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Check Ollama
echo ""
echo "🤖 Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama not found. Installing...${NC}"
    curl -fsSL https://ollama.ai/install.sh | sh
fi
echo -e "${GREEN}✅ Ollama installed${NC}"

# Pull default model
echo ""
echo "📦 Pulling default model (llama3.2:latest)..."
ollama pull llama3.2:latest || {
    echo -e "${YELLOW}⚠️  Failed to pull model. You can do this manually later with: ollama pull llama3.2:latest${NC}"
}

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp ../env.example .env
    echo -e "${GREEN}✅ Created backend/.env with defaults${NC}"
fi

cd ..

# Setup frontend
echo ""
echo "🎨 Setting up frontend..."
npm install

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 - Frontend:"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "🔒 Your data stays local in: backend/annapurna.db"
