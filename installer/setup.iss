#define MyAppName      "LumieTL"
#define MyAppVersion   "1.0.0"
#define MyAppExeName   "LumieTL.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=LumieTL_Setup_v{#MyAppVersion}
SetupIconFile=..\assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
MinVersion=10.0.17763
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Buat shortcut di Desktop"; Flags: unchecked

[Files]
Source: "..\dist\LumieTL\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}";             Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}";   Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}";     Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -Command ""try { cmdkey /list | Select-String 'Target:\s*(LumieTL.*)' | ForEach-Object { cmdkey /delete:$($_.Matches[0].Groups[1].Value.Trim()) } } catch {}"""; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\{#MyAppName}"
Type: filesandordirs; Name: "{localappdata}\{#MyAppName}"
Type: filesandordirs; Name: "{app}"
