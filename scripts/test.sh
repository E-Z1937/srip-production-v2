#!/bin/bash
echo "🧪 Running SRIP Test Suite"
echo "=========================="

pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Tests complete! Coverage report: htmlcov/index.html"
