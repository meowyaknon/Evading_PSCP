# Using the macOS Installer

## Quick Start for End Users

### Installation

1. **Download the DMG**: Get `Evading_PSCP_macOS_Installer.dmg` from your distribution method
2. **Open the DMG**: Double-click the DMG file
3. **Install**: Drag "Evading PSCP.app" to your Applications folder
4. **Launch**: Open the app from Applications or Launchpad

### First Launch (Gatekeeper)

On first launch, macOS may show a security warning. To fix this:

1. Open **System Settings** (System Preferences on older macOS)
2. Go to **Privacy & Security**
3. Scroll down to find the blocked app
4. Click **"Open Anyway"**
5. Confirm in the dialog

Alternatively:

- Right-click the app in Finder
- Select **"Open"**
- Click **"Open"** again in the security warning

### Requirements

- **macOS**: 10.14 (Mojave) or later
- **Architecture**: Works on Intel and Apple Silicon Macs
- **Disk Space**: ~50MB

### Troubleshooting

**App won't open**

- Make sure you allowed the app to run (see Gatekeeper section above)
- Check that you're running macOS 10.14 or later
- Try running from Terminal: `/Applications/Evading\ PSCP.app/Contents/MacOS/Evading\ PSCP`

**Assets missing**

- Re-download the installer (may be corrupted)
- Contact the developers

**Performance issues**

- Close other resource-intensive applications
- Update your macOS to the latest version

## For Developers

See `BUILD_INSTRUCTIONS.md` for detailed build information.

## File Sizes

- **DMG Installer**: ~18MB (compressed)
- **App Bundle**: ~41MB (uncompressed)
- **Total on disk**: ~50MB after installation

## Technical Notes

- Built with: PyInstaller 6.16.0
- Python: 3.13.7
- Pygame: 2.6.1
- Bundle ID: `com.gloria.evading.pscp`
- Not code-signed (requires Apple Developer account for distribution)
- Not notarized (requires Apple Developer account)

## Distribution

This installer is suitable for:

- Personal projects
- Internal company distribution
- Educational purposes
- Testing and development

**For public distribution**: You should code-sign and notarize the app to avoid security warnings. This requires:

1. Apple Developer Account ($99/year)
2. Code signing certificate
3. Notarization submission

See `BUILD_INSTRUCTIONS.md` for signing and notarization steps.
