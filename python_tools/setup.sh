#!/bin/bash
# Setup script for Python tools

set -e

echo "🔧 Setting up Python environment..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use the tools:"
echo "  1. Activate the environment: source venv/bin/activate"
echo "  2. Run a script: python read_index.py"
echo "  3. Deactivate when done: deactivate"
echo ""
