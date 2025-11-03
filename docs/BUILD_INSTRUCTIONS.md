# Building Evading PSCP for macOS

This guide will help you create a macOS installer for Evading PSCP.

## Quick Start

**For first-time builds or major changes:**
```bash
./build.sh          # Step 1: Build the app
./create_dmg.sh     # Step 2: Create the DMG installer
```

**For quick rebuilds (image/asset changes only):**
```bash
./rebuild.sh        # Rebuilds app & optionally creates DMG
```

## Which Script to Use?

- **`build.sh`**: Full clean build (removes old build files, reinstalls dependencies)
- **`rebuild.sh`**: Quick rebuild (for testing asset/configuration changes)
- **`create_dmg.sh`**: Creates DMG installer from existing app bundle

## Detailed Instructions

### Prerequisites

- macOS (10.14 or later)
- Python 3.8 or higher
- Internet connection (for downloading dependencies)

### Step-by-Step Build Process

#### 1. Build the App Bundle

Run the build script:

```bash
./build.sh
```

This script will:

- Create a Python virtual environment
- Install required dependencies (pygame, pyinstaller)
- Build the app using PyInstaller
- Create `dist/Evading PSCP.app`

#### 2. Create the DMG Installer

Run the DMG creation script:

```bash
./create_dmg.sh
```

This script will:

- Create a properly formatted DMG image
- Add the app bundle to the DMG
- Create a link to Applications folder
- Compress the DMG for distribution

The final installer will be at: `dist/Evading_PSCP_macOS_Installer.dmg`

### Manual Build (Alternative)

If you prefer to build manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller build_config/Evading_PSCP.spec --clean --noconfirm

# Your app is now in dist/Evading PSCP.app
```

### Distribution

The `Evading_PSCP_macOS_Installer.dmg` file can be:

- Shared via email
- Uploaded to GitHub releases
- Hosted on a website
- Burned to a disk

### Code Signing (Optional)

For distribution outside the Mac App Store, you may want to code sign:

```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/Evading\ PSCP.app
```

This requires an Apple Developer account ($99/year).

### Notarization (Optional)

For complete Gatekeeper compatibility:

1. Code sign the app (as above)
2. Notarize with Apple using `xcrun notarytool` or `altool`
3. Staple the notarization ticket

This also requires an Apple Developer account.

### Troubleshooting

**Problem:** App doesn't launch after installation

- **Solution:** Right-click the app and select "Open" to bypass Gatekeeper the first time

**Problem:** "pyinstaller: command not found"

- **Solution:** Make sure you ran `./build.sh` which sets up the environment automatically

**Problem:** Assets are missing

- **Solution:** Check that the `Evading_PSCP.spec` file includes all asset files in the `datas` section

**Problem:** DMG creation fails

- **Solution:** Make sure you're on macOS and the app bundle exists in `dist/`

## File Structure

```
Evading_PSCP/
├── build_config/
│   └── Evading_PSCP.spec        # PyInstaller configuration
├── scripts/
│   ├── build.sh                 # Build script
│   └── create_dmg.sh           # DMG creation script
├── requirements.txt        # Python dependencies
├── Evading_PSCP/
│   ├── Evading_PSCP.py    # Main game file
│   └── Asset/             # Game assets (images, etc.)
└── dist/                   # Build output (created by scripts)
    ├── Evading PSCP.app   # macOS application bundle
    └── Evading_PSCP_macOS_Installer.dmg  # Final installer
```

## Technical Details

- **Bundle ID:** com.gloria.evading.pscp
- **Minimum macOS:** 10.14 (Mojave)
- **Architecture:** Universal (works on Intel and Apple Silicon)
- **Code Signing:** Not included by default (add if needed)
- **Notarization:** Not included by default (add if needed)

## Credits

Built by Team Gloria F, KMITL using:

- Pygame for game engine
- PyInstaller for packaging
- macOS native tools for DMG creation
