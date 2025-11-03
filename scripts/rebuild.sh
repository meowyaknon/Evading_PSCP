#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Quick Rebuild (Code/Assets/Config)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Navigate to project root (parent directory of scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo -e "${YELLOW}Working directory: $PROJECT_ROOT${NC}"
echo ""

# Check if the app exists
if [ ! -d "dist/Evading PSCP.app" ]; then
    echo -e "${YELLOW}No existing app found. Running full build...${NC}"
    ./scripts/build.sh
    exit 0
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Just rebuild with PyInstaller (no cleanup)
echo -e "${YELLOW}Rebuilding application with PyInstaller...${NC}"
pyinstaller build_config/Evading_PSCP.spec --clean --noconfirm

# Check if build was successful
if [ -d "dist/Evading PSCP.app" ]; then
    echo -e "${GREEN}✓ Rebuild successful!${NC}"
    
    # Ask if user wants to create DMG
    echo ""
    read -p "Create DMG installer? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./scripts/create_dmg.sh
    fi
else
    echo -e "${RED}✗ Rebuild failed!${NC}"
    exit 1
fi

# Deactivate virtual environment
deactivate

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Rebuild Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
