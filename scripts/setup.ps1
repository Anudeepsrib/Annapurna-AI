#!/usr/bin/env pwsh
# Annapurna-AI Local Setup Script (Windows)
# This script sets up the local-first version of Annapurna-AI

$ErrorActionPreference = "Stop"

Write-Host "🍛 Annapurna-AI Local Setup" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..."

# Check Node.js
try {
    $nodeVersion = node --version
    $majorVersion = [int]($nodeVersion -replace 'v','' -split '\.' | Select-Object -First 1)
    if ($majorVersion -lt 20) {
        Write-Host "❌ Node.js version 20+ required. Found: $nodeVersion" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js 20+ first." -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    try {
        $pythonVersion = python3 --version 2>&1
        Write-Host "✅ $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python is not installed. Please install Python 3.11+ first." -ForegroundColor Red
        exit 1
    }
}

# Check Ollama
Write-Host ""
Write-Host "🤖 Checking Ollama..."
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama not found. Please install from https://ollama.ai" -ForegroundColor Yellow
    Write-Host "   After installing, run this script again." -ForegroundColor Yellow
}

# Pull default model
Write-Host ""
Write-Host "📦 Pulling default model (llama3.2:latest)..."
try {
    ollama pull llama3.2:latest
    Write-Host "✅ Model pulled successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Failed to pull model. You can do this manually later with: ollama pull llama3.2:latest" -ForegroundColor Yellow
}

# Setup backend
Write-Host ""
Write-Host "🔧 Setting up backend..."
Set-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..."
    Copy-Item ..\env.example .env
    Write-Host "✅ Created backend/.env with defaults" -ForegroundColor Green
}

Set-Location ..

# Setup frontend
Write-Host ""
Write-Host "🎨 Setting up frontend..."
npm install

Write-Host ""
Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 - Backend:" -ForegroundColor Yellow
Write-Host "  cd backend"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  python -m uvicorn app.main:app --reload"
Write-Host ""
Write-Host "Terminal 2 - Frontend:" -ForegroundColor Yellow
Write-Host "  npm run dev"
Write-Host ""
Write-Host "Then open: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔒 Your data stays local in: backend/annapurna.db" -ForegroundColor Cyan
