; Inno Setup — R3E Stream-Overlay (Streaming-PC)
; Aufruf in CI:  iscc /DAppVersion=x.y.z installer\setup_overlay.iss
#ifndef AppVersion
#define AppVersion "0.1.0"
#endif

[Setup]
AppId={{8E1C6B77-4C2A-4F31-9A21-R3ESOOVERL01}
AppName=R3E Stream-Overlay
AppVersion={#AppVersion}
DefaultDirName={autopf}\R3E Stream-Overlay
DefaultGroupName=R3E Stream-Overlay
OutputBaseName=R3E-Stream-Overlay-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
Output=dist_installer

[Files]
Source:"dist\overlay\R3E-Stream-Overlay.exe"; DestDir:"{app}"; Flags: ignoreversion

[Tasks]
Name: "autostart"; Description: "Overlay mit Windows starten (empfohlen)"; Flags: checkedonce

[Icons]
Name: "{group}\R3E Stream-Overlay"; Filename: "{app}\R3E-Stream-Overlay.exe"
Name: "{userdesktop}\R3E Stream-Overlay"; Filename: "{app}\R3E-Stream-Overlay.exe"; Tasks: autostart

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "R3E Stream-Overlay"; \
    ValueData: """{app}\R3E-Stream-Overlay.exe"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\R3E-Stream-Overlay.exe"; Description: "Overlay jetzt starten"; \
    Flags: nowait postinstall skipifsilent unchecked
