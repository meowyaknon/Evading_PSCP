# Evading PSCP📚

A Python game project for PSCP Subject from Team Gloria F School of Information Technology, KMITL (1st year).

โปรเจ็กต์เกม Python วิชา Problem Solving and Computer Programming (PSCP) คณะเทคโนโลยีสารสนเทศ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง

## Contributors📝

- MeowYakNon: ศิริเทพ บดิการ 68070316
- Pun_Nep_Kin: กฤษฎิ์ ลิ้มตระกูล 68070214
- Mayb.pinny: ปรียาพร เอี่ยมประดิษฐ์ภัณ 68070286
- pearson_pesrmak: เอมม่า เพียร์สัน 68070328
- jame_thananon: ธนานนต์ เจียจงเจริญชัย 68070265

## About this project

<<<<<<< Updated upstream
<<<<<<< Updated upstream
Evading PSCP เป็นเกมแนว 2D infinite runner ที่ผู้เล่นจะต้องกระโดดหลบอุปสรรคและเก็บคะแนนให้ได้มากที่สุด โดยระหว่างทางมีบอสสุดเหี้ยมให้ต่อสู้หากเอาชนะบอสได้ก็จะสามารถไปด่านต่อไปได้และก็ได้คะแนนพิเศษจากบอสเหล่านั้นด้วย
=======
Evading PSCP เป็นเกมแนว 2D infinite runner ที่ผู้เล่นจะต้องกระโดดหลบอุปสรรคและต่อสู้กับบอสสุดโหดเหี้ยมเพือผ่านด่านและเก็บคะแนนให้ได้สูงที่สุด
>>>>>>> Stashed changes
=======
Evading PSCP เป็นเกมแนว 2D infinite runner ที่ผู้เล่นจะต้องกระโดดหลบอุปสรรคและต่อสู้กับบอสสุดโหดเหี้ยมเพือผ่านด่านและเก็บคะแนนให้ได้สูงที่สุด
>>>>>>> Stashed changes

## Installation

### For End Users

#### macOS Users

<<<<<<< Updated upstream
<<<<<<< Updated upstream
1. Download the `Evading_PSCP.dmg` file
=======
1. Download the `Evading_PSCP_macOS_Installer.dmg` file
>>>>>>> Stashed changes
=======
1. Download the `Evading_PSCP_macOS_Installer.dmg` file
>>>>>>> Stashed changes
2. Open the DMG file
3. Drag "Evading PSCP.app" to your Applications folder
4. Launch the game from your Applications folder

**Note:** If macOS blocks the app, right-click it and select "Open", then click "Open" again in the security warning.

#### Windows Users

1. Download the `Evading_PSCP_Setup.exe` file
2. Run the installer
3. Follow the installation wizard
4. Launch the game from your desktop or Start menu
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
>>>>>>> Stashed changes

### For Developers

#### Requirements

- Python 3.8 or higher
- macOS (for building macOS installer) OR Windows (for building Windows installer)

#### Building from Source

1. Clone the repository:

```bash
git clone https://github.com/yourusername/Evading_PSCP.git
cd Evading_PSCP
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

#### Building Installers

**macOS:**

Full build (first time or major changes):

```bash
./build.sh          # Build the macOS app bundle
./create_dmg.sh     # Create the DMG installer
```

Quick rebuild (for image/asset changes):

```bash
./rebuild.sh        # Rebuilds app & optionally creates DMG
```

**Windows:**

Full build:

```batch
build_windows.bat              # Build the Windows app
build_windows_installer.bat    # Create the installer
```

All installers will be created in the `installers/` directory:

- `installers/Evading_PSCP.dmg` (macOS)
- `installers/Evading_PSCP_Setup.exe` (Windows)

#### Running from Source

```bash
python3 Evading_PSCP/Evading_PSCP.py
```
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
