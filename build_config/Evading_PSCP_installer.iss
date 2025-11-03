; Inno Setup script for Evading PSCP
; Compile with Inno Setup Compiler

[Setup]
AppId={{A1B2C3D4-E5F6-4789-ABCD-123456789012}
AppName=Evading PSCP
AppVersion=1.0.0
AppPublisher=Team Gloria F, KMITL
AppPublisherURL=
DefaultDirName={autopf}\Evading PSCP
DefaultGroupName=Evading PSCP
AllowNoIcons=yes
LicenseFile=
OutputDir=installers
OutputBaseFilename=Evading_PSCP_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\Evading PSCP\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Evading PSCP"; Filename: "{app}\Evading PSCP.exe"
Name: "{group}\{cm:UninstallProgram,Evading PSCP}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Evading PSCP"; Filename: "{app}\Evading PSCP.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Evading PSCP"; Filename: "{app}\Evading PSCP.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\Evading PSCP.exe"; Description: "{cm:LaunchProgram,Evading PSCP}"; Flags: nowait postinstall skipifsilent
