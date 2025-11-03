#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Creating DMG Installer${NC}"
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
    echo -e "${RED}Error: dist/Evading PSCP.app not found${NC}"
    echo "Please run ./scripts/build.sh first"
    exit 1
fi

APP_NAME="Evading PSCP"
DMG_NAME="Evading_PSCP"
APP_PATH="dist/${APP_NAME}.app"
INSTALLERS_DIR="installers"

# Create installers directory if it doesn't exist
mkdir -p "$INSTALLERS_DIR"

DMG_PATH="${INSTALLERS_DIR}/${DMG_NAME}.dmg"

# Clean up old DMG and any leftover temp files
rm -f "$DMG_PATH" "${INSTALLERS_DIR}/${DMG_NAME}_temp.dmg"

# Clean up any leftover mounted volumes
echo -e "${YELLOW}Cleaning up any leftover mounts...${NC}"
hdiutil info | grep "/dev/" | awk '{print $1}' | while read device; do
    hdiutil info | grep -A 10 "^$device" | grep -q "Evading" && hdiutil detach "$device" 2>/dev/null || true
done
sleep 1

# Create DMG directly (simpler approach)
echo -e "${YELLOW}Creating DMG...${NC}"
hdiutil create -volname "$APP_NAME" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_PATH"

# If direct creation failed, try with more overhead
if [ ! -f "$DMG_PATH" ]; then
    echo -e "${YELLOW}First attempt failed, trying with more space...${NC}"
    SIZE=$(du -sk "$APP_PATH" | cut -f1)
    SIZE=$(echo "$SIZE + 50000" | bc)
    TEMP_DMG="${INSTALLERS_DIR}/${DMG_NAME}_temp.dmg"
    hdiutil create -volname "$APP_NAME" -srcfolder "$APP_PATH" -fs HFS+ -format UDRW -size ${SIZE}k "$TEMP_DMG"
    hdiutil convert "$TEMP_DMG" -format UDZO -imagekey zlib-level=9 -o "$DMG_PATH"
    rm -f "$TEMP_DMG"
fi

# Check if DMG was created successfully
if [ -f "$DMG_PATH" ]; then
    echo -e "${GREEN}✓ DMG created successfully!${NC}"
    echo -e "${GREEN}Installer: $DMG_PATH${NC}"
    DMG_SIZE=$(du -h "$DMG_PATH" | cut -f1)
    echo -e "${GREEN}Size: $DMG_SIZE${NC}"
else
    echo -e "${RED}✗ DMG creation failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DMG Installer Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "You can distribute: $DMG_PATH"
echo ""
echo "Note: To avoid Gatekeeper warnings, you may need to:"
echo "  1. Sign the app: codesign --deep --force --verify --verbose --sign 'Developer ID Application: Your Name' dist/${APP_NAME}.app"
echo "  2. Notarize with Apple (requires Apple Developer account)"
