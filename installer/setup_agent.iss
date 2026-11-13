; Inno Setup — R3E Stream-Overlay Agent (Gaming-PC)
; Aufruf in CI:  iscc /DAppVersion=x.y.z installer\setup_agent.iss
#ifndef AppVersion
#define AppVersion "0.1.0"
#endif

[Setup]
AppId={{8E1C6B77-4C2A-4F31-9A21-R3ESOAGENT01}
AppName=R3E Stream-Overlay Agent
AppVersion={#AppVersion}
DefaultDirName={autopf}\R3E Stream-Overlay Agent
DefaultGroupName=R3E Stream-Overlay Agent
OutputBaseName=R3E-Stream-Agent-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
; Output ist relativ zu dieser .iss-Datei (Ordner installer\):
Output=..\dist_installer

[Files]
Source:"dist\agent\R3E-Stream-Agent.exe"; DestDir:"{app}"; Flags: ignoreversion

[Tasks]
Name: "autostart"; Description: "Agent mit Windows starten (empfohlen)"; Flags: checkedonce

[Icons]
Name: "{group}\R3E Stream-Overlay Agent"; Filename: "{app}\R3E-Stream-Agent.exe"
Name: "{userdesktop}\R3E Stream-Overlay Agent"; Filename: "{app}\R3E-Stream-Agent.exe"; Tasks: autostart

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "R3E Stream-Overlay Agent"; \
    ValueData: """{app}\R3E-Stream-Agent.exe"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\R3E-Stream-Agent.exe"; Description: "Agent jetzt starten"; \
    Flags: nowait postinstall skipifsilent unchecked
