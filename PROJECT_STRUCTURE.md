# Project Structure

This document describes the organization of the Evading PSCP project.

## Directory Overview

```
Evading_PSCP/
├── build_config/           # Build configuration files
│   ├── Evading_PSCP.spec          # PyInstaller config for macOS
│   ├── Evading_PSCP_windows.spec  # PyInstaller config for Windows
│   └── Evading_PSCP_installer.iss # Inno Setup config for Windows installer
│
├── docs/                   # Documentation
│   ├── BUILD_INSTRUCTIONS.md       # macOS build instructions
│   ├── BUILD_INSTRUCTIONS_WINDOWS.md # Windows build instructions
│   ├── INSTALLER_USAGE.md          # End user installer guide
│   ├── LICENSE                     # Project license
│   ├── QUICKSTART.md               # Quick start guide
│   └── README.md                   # Documentation index
│
├── scripts/                # Build scripts
│   ├── build.sh                    # Full macOS build script
│   ├── rebuild.sh                  # Quick macOS rebuild script
│   ├── create_dmg.sh              # DMG installer creation script
│   ├── build_windows.bat          # Full Windows build script
│   └── build_windows_installer.bat # Windows installer creation script
│
├── Evading_PSCP/          # Source code
│   ├── Evading_PSCP.py            # Main game file
│   └── Asset/                     # Game assets (images, etc.)
│
├── build/                  # Temporary build files (auto-generated)
├── dist/                   # Build output (auto-generated)
├── installers/             # Final installers (auto-generated)
├── venv/                   # Python virtual environment (auto-generated)
│
├── README.md               # Main project README
├── PROJECT_STRUCTURE.md   # This file
├── .gitignore             # Git ignore rules
└── requirements.txt       # Python dependencies
```

## Wrapper Scripts

For convenience, wrapper scripts are also available in the root directory:

- `build.sh` → `scripts/build.sh`
- `rebuild.sh` → `scripts/rebuild.sh`
- `create_dmg.sh` → `scripts/create_dmg.sh`
- `build_windows.bat` → `scripts/build_windows.bat`
- `build_windows_installer.bat` → `scripts/build_windows_installer.bat`

These wrappers change to the project root before calling the actual scripts, so you can run them from anywhere.

## Quick Reference

### Building on macOS
```bash
./build.sh          # or ./scripts/build.sh
./create_dmg.sh     # or ./scripts/create_dmg.sh
```

### Building on Windows
```batch
build_windows.bat              # or scripts\build_windows.bat
build_windows_installer.bat    # or scripts\build_windows_installer.bat
```

### Documentation
See `docs/README.md` for a complete guide to all documentation files.

## Auto-Generated Directories

These directories are created automatically during builds and should not be committed:

- **`build/`**: PyInstaller temporary files
- **`dist/`**: Final application bundles
- **`installers/`**: Installer packages (.dmg, .exe)
- **`venv/`**: Python virtual environment

These are already listed in `.gitignore`.

