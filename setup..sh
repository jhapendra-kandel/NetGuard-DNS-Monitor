#!/bin/bash
# NetGuard DNS Monitor - Linux/macOS Setup Script
# Automated installation for Unix-like systems

echo ""
echo "================================================================"
echo ""
echo "       NetGuard DNS Monitor - Linux/macOS Setup"
echo ""
echo "================================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager"
    exit 1
fi

echo "✅ [1/4] Python detected successfully"
echo ""

# Create virtual environment
echo "📦 [2/4] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created successfully"
fi
echo ""

# Activate virtual environment and install dependencies
echo "📥 [3/4] Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed successfully"
echo ""

# Setup complete
echo "🎉 [4/4] Setup complete!"
echo ""
echo "================================================================"
echo ""
echo "  Setup Complete! Next Steps:"
echo ""
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run NetGuard (with sudo):"
echo "     sudo python3 main.py"
echo ""
echo "  3. Configure device DNS settings"
echo "     - Set Primary DNS to your computer's IP"
echo "     - Set Secondary DNS to 8.8.8.8"
echo ""
echo "  Read QUICK_SETUP.md for more details"
echo ""
echo "================================================================"
echo ""