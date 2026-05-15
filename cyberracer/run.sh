#!/bin/bash
echo "╔═══════════════════════════════════════════════════╗"
echo "║         CYBERRACER — Startup Script              ║"
echo "║       OBI Cybernetic Authentication Game          ║"
echo "╚═══════════════════════════════════════════════════╝"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install OBI SDK
echo "📦 Installing OBI SDK..."
pip install obi

echo ""
echo "✓ Installation complete!"
echo ""
echo "Starting CyberRacer Backend..."
echo "Server will be available at: http://localhost:5000"
echo ""

# Start backend
cd backend
python3 app.py
