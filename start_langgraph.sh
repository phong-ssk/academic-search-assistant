#!/bin/bash

# Quick Start Script for LangGraph App
# Khởi chạy nhanh app LangGraph

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║         🧠 Academic Search - LangGraph Quick Start              ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "🔍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"
echo ""

# Check .env file
echo "🔍 Checking .env file..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << 'EOF'
# Gemini API Key (REQUIRED for LangGraph)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional API Keys
PUBMED_API_KEY=your_pubmed_key_optional
SCOPUS_API_KEY=your_scopus_key_optional
SEMANTIC_SCHOLAR_API_KEY=your_semantic_key_optional
EOF
    echo "⚠️  Please edit .env file and add your GEMINI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=.*[^_here]" .env; then
    echo "⚠️  GEMINI_API_KEY not configured in .env"
    echo "   Please edit .env and add your API key"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Run the app
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                  🚀 Launching LangGraph App                      ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 App will open at: http://localhost:8501"
echo ""
echo "⚡ Features:"
echo "   - Auto query optimization"
echo "   - Smart deduplication (DOI, PMID, Title)"
echo "   - 30-min cache"
echo "   - Async parallel search"
echo "   - Auto refinement (max 2 times)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "─────────────────────────────────────────────────────────────────────"

streamlit run app_langgraph.py
