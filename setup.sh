#!/bin/bash

# AI Notetaker API - Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "🚀 Setting up AI Notetaker API..."

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   Virtual environment created"
else
    echo "   Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Setup environment file
echo "⚙️  Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   Created .env file from .env.example"
    echo "   ⚠️  Please edit .env and add your API keys!"
else
    echo "   .env file already exists"
fi

# Initialize database
echo "🗄️  Initializing database..."
if [ ! -f "notetaker.db" ]; then
    alembic upgrade head
    echo "   Database initialized"
else
    echo "   Database already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env and add your API keys (RECALL_API_KEY, etc.)"
echo "   2. Start the server: uvicorn src.main:app --reload"
echo "   3. Start ngrok for webhooks: ngrok http 8000"
echo "   4. Configure webhook at Recall.ai dashboard"
echo ""
echo "📖 API documentation will be at: http://localhost:8000/docs"
echo ""
