#!/bin/bash
echo "🚀 Starting SRIP Production System"
echo "=================================="

# Check environment
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

source .env
if [ "$GROQ_API_KEY" == "your_groq_api_key_here" ]; then
    echo "❌ Please set GROQ_API_KEY in .env"
    exit 1
fi

echo "✅ Environment OK"
echo ""
echo "🎨 Starting Gradio UI on http://localhost:7860"
python -m src.ui.gradio_app
