#!/usr/bin/env bash
# Orchestrator Toolkit Setup Script for Unix/macOS
# This script sets up the development environment automatically

set -e  # Exit on error

echo "🎯 Orchestrator Toolkit Setup"
echo "=============================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📦 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.10 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python $PYTHON_VERSION is too old. Required: >= $REQUIRED_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"
echo

# Create virtual environment
VENV_DIR=".otk-venv"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists at $VENV_DIR${NC}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf "$VENV_DIR"
    else
        echo "Using existing virtual environment..."
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel --quiet

# Install package
echo "📦 Installing Orchestrator Toolkit..."
pip install -e . --quiet

echo -e "${GREEN}✅ Orchestrator Toolkit installed${NC}"
echo

# Create ai_docs directory
if [ ! -d "ai_docs" ]; then
    echo "📁 Creating ai_docs directory..."
    mkdir -p ai_docs/tasks ai_docs/plans
    echo -e "${GREEN}✅ Artifact directories created${NC}"
fi

# Check for direnv (optional)
if command -v direnv &> /dev/null; then
    echo "🔧 Detected direnv. Creating .envrc file..."
    cat > .envrc << 'EOF'
source .otk-venv/bin/activate
export OTK_ARTIFACT_ROOT=ai_docs
EOF
    echo -e "${YELLOW}Run 'direnv allow' to auto-activate this environment${NC}"
else
    echo -e "${YELLOW}💡 Tip: Install direnv for automatic environment activation${NC}"
fi

# Create activation script
cat > activate_otk.sh << 'EOF'
#!/bin/bash
source .otk-venv/bin/activate
export OTK_ARTIFACT_ROOT=ai_docs
echo "✅ Orchestrator Toolkit environment activated"
echo "📁 Artifacts will be stored in: ai_docs/"
EOF
chmod +x activate_otk.sh

echo
echo "================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "================================"
echo
echo "To activate the environment:"
echo -e "  ${YELLOW}source activate_otk.sh${NC}"
echo
echo "Available commands:"
echo "  task-new \"Task title\" --owner Name"
echo "  plan-new \"Plan title\" --task T-0001"
echo "  orchestrator-once"
echo
echo "Quick test:"
echo -e "  ${YELLOW}task-new \"My first task\" --owner $USER${NC}"
echo
echo "For more information, see README.md"

# Test installation
echo
echo "🧪 Running quick test..."
if python -c "from orchestrator_toolkit.settings import OrchSettings; OrchSettings.load()" 2>/dev/null; then
    echo -e "${GREEN}✅ Installation verified successfully!${NC}"
else
    echo -e "${RED}❌ Installation test failed. Please check for errors above.${NC}"
    exit 1
fi