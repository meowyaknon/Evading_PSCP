# Building Evading PSCP for Windows

This guide will help you create a Windows installer for Evading PSCP.

## Quick Start

Run these two commands in order:

```batch
build_windows.bat              # Step 1: Build the app
build_windows_installer.bat    # Step 2: Create the installer
```

## Detailed Instructions

### Prerequisites

- **Windows 10** or later
- **Python 3.8** or higher
- **Internet connection** (for downloading dependencies)
- **Inno Setup** (for creating the installer) - optional but recommended

### Step-by-Step Build Process

#### 1. Install Python

If you don't have Python installed:

1. Download Python from: https://www.python.org/downloads/
2. Run the installer
3. **Important:** Check "Add Python to PATH" during installation
4. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```

#### 2. Build the App Bundle

Run the build script:

```batch
build_windows.bat
```

This script will:
- Create a Python virtual environment
- Install required dependencies (pygame, pyinstaller, pillow)
- Build the app using PyInstaller
- Create `dist\Evading PSCP\` folder with the executable

#### 3. Create the Installer (Optional)

If you have Inno Setup installed:

```batch
build_windows_installer.bat
```

This script will:
- Create a professional Windows installer
- Add desktop shortcuts
- Add Start menu entry
- Create an uninstaller

**Installing Inno Setup:**

1. Download from: https://jrsoftware.org/isinfo.php
2. Run the installer
3. Accept default installation path
4. Done! The batch script will find it automatically

### Without Inno Setup

You can still distribute the game without an installer! Just zip the `dist\Evading PSCP\` folder and share it. Users can extract and run `Evading PSCP.exe` directly.

### Distribution

The `Evading_PSCP_Setup.exe` file can be:
- Shared via email (if size allows)
- Uploaded to GitHub releases
- Hosted on a website
- Burned to a disk

### Code Signing (Optional)

For professional distribution, you may want to code sign the installer:

1. Get a code signing certificate
2. Use `signtool` from Windows SDK
3. Sign the `.exe` before distribution

This helps avoid Windows Defender warnings.

### Troubleshooting

**Problem:** "python is not recognized"
- **Solution:** Install Python and check "Add to PATH" during installation, or add it manually

**Problem:** "ModuleNotFoundError"
- **Solution:** Make sure you ran `build_windows.bat` which installs dependencies

**Problem:** "Assets are missing"
- **Solution:** Check that `build_config/Evading_PSCP_windows.spec` includes all asset files in the `datas` section

**Problem:** Inno Setup not found
- **Solution:** Install Inno Setup or just distribute the portable folder (`dist\Evading PSCP\`)

**Problem:** Antivirus false positives
- **Solution:** Add an exception or code sign the application

## File Structure

```
Evading_PSCP/
├── build_config/
│   ├── Evading_PSCP_windows.spec      # PyInstaller config for Windows
│   └── Evading_PSCP_installer.iss     # Inno Setup script
├── scripts/
│   ├── build_windows.bat               # Build script
│   └── build_windows_installer.bat     # Installer creation script
├── Evading_PSCP/
│   ├── Evading_PSCP.py            # Main game file
│   └── Asset/                     # Game assets
├── dist/
│   └── Evading PSCP/              # Portable build (can be zipped & shared)
│       └── Evading PSCP.exe
└── installers/
    └── Evading_PSCP_Setup.exe     # Windows installer
```

## Technical Details

- **Target Architecture:** 64-bit compatible
- **Minimum Windows:** Windows 10 (may work on Windows 7+)
- **Size:** ~50-100MB unpacked
- **Dependencies:** Bundled with PyInstaller
- **Required:** None (fully portable)

## Comparison: With vs Without Inno Setup

**With Inno Setup:**
- ✓ Professional installer experience
- ✓ Desktop shortcuts
- ✓ Start menu entry
- ✓ Uninstaller
- ✓ Installation wizard
- ❌ Requires Inno Setup to build

**Without Inno Setup:**
- ✓ No extra software needed
- ✓ Just zip the `dist\Evading PSCP\` folder
- ✓ Users extract and run `Evading PSCP.exe`
- ✓ Fully portable
- ❌ No shortcuts or uninstaller

Both methods work! Choose what fits your needs.

## Credits

Built by Team Gloria F, KMITL using:
- Pygame for game engine
- PyInstaller for packaging
- Inno Setup for installer creation
