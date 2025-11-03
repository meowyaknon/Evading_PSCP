# Quick Start Guide

## For Players 👾

### Installing the Game

**macOS:**
1. **Download**: `Evading_PSCP.dmg` from installers folder
2. **Open**: Double-click the DMG file
3. **Install**: Drag "Evading PSCP.app" to Applications
4. **Play**: Launch from Applications!

**Windows:**
1. **Download**: `Evading_PSCP_Setup.exe` from installers folder
2. **Run**: Double-click the installer
3. **Follow**: Installation wizard
4. **Play**: Launch from Start menu!

**Having trouble?** See `INSTALLER_USAGE.md`

---

## For Developers 🛠️

### Build the Installer

**macOS:**

First time or major changes:
```bash
./build.sh          # Build the app
./create_dmg.sh     # Create DMG
```

Quick rebuild:
```bash
./rebuild.sh        # Rebuilds app & optionally creates DMG
```

**Windows:**

First time or major changes:
```batch
build_windows.bat              # Build the app
build_windows_installer.bat    # Create installer
```

**Output:** All installers go to `installers/` folder:
- `installers/Evading_PSCP.dmg` (macOS)
- `installers/Evading_PSCP_Setup.exe` (Windows)

### Run from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python3 Evading_PSCP/Evading_PSCP.py
```

### Project Structure

```
Evading_PSCP/
├── build_config/
│   └── Evading_PSCP.spec      # PyInstaller config
├── scripts/
│   ├── build.sh               # Full build script
│   ├── rebuild.sh             # Quick rebuild script
│   └── create_dmg.sh          # DMG creation script
├── requirements.txt       # Dependencies
├── Evading_PSCP/
│   ├── Evading_PSCP.py   # Main game file
│   └── Asset/            # Game assets
├── dist/                  # Build output
└── installers/            # Final installers
    └── Evading_PSCP.dmg
```

Need more details? Check `BUILD_INSTRUCTIONS.md`

---

## Quick Links

- 📖 [Full README](README.md)
- 📦 [Installer Usage](INSTALLER_USAGE.md)
- 🔨 [macOS Build Instructions](BUILD_INSTRUCTIONS.md)
- 🪟 [Windows Build Instructions](BUILD_INSTRUCTIONS_WINDOWS.md)
