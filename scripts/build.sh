#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Building Evading PSCP for macOS${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This script must be run on macOS${NC}"
    exit 1
fi

# Navigate to project root (parent directory of scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo -e "${YELLOW}Working directory: $PROJECT_ROOT${NC}"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build dist

# Build the app
echo -e "${YELLOW}Building application with PyInstaller...${NC}"
pyinstaller build_config/Evading_PSCP.spec --clean --noconfirm

# Check if build was successful
if [ -d "dist/Evading PSCP.app" ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo -e "${GREEN}App created at: dist/Evading PSCP.app${NC}"
else
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi

# Deactivate virtual environment
deactivate

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Build Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To create a DMG installer, run: ./create_dmg.sh"
