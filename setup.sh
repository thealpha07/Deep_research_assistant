#!/bin/bash

echo "============================================================"
echo "Deep Research Assistant - Setup Script"
echo "============================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

echo "[1/6] Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "[2/6] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[3/6] Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "[4/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo ""

# Create .env file if not exists
echo "[5/6] Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env file created from template"
    echo "IMPORTANT: Edit .env and add your TAVILY_API_KEY"
else
    echo ".env file already exists"
fi
echo ""

# Create necessary directories
echo "[6/6] Creating directories..."
mkdir -p data/chromadb
mkdir -p outputs
mkdir -p temp
echo "Directories created"
echo ""

echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your TAVILY_API_KEY"
echo "   Get free API key from: https://tavily.com"
echo ""
echo "2. Make sure Ollama is running:"
echo "   ollama serve"
echo ""
echo "3. Pull a model (if not already done):"
echo "   ollama pull llama3.2"
echo ""
echo "4. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "5. Run the application:"
echo "   python main.py"
echo ""
echo "6. Open browser to:"
echo "   http://localhost:5000"
echo ""
echo "============================================================"
