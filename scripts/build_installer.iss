; Inno Setup script for Live Transcript v0.1.0
; Run from the project root:
;   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "scripts\build_installer.iss"
; Output will be placed in: scripts\Output\LiveTranscript_Installer.exe

#define MyAppName "Live Transcript"
#define MyAppVersion "0.1.0"
#define MyAppExeName "LiveTranscript.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Live Transcript
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputBaseFilename=LiveTranscript_Installer
OutputDir=Output
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
LicenseFile=LICENSE.txt
SetupIconFile=C:\Users\Surya\Desktop\LIVE TRANSCRIPT ANYTHING I'M WATCHING\assets\icon.ico

[Files]
; Main single-file executable
Source: "..\dist\LiveTranscript.exe"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

; App icon (used by shortcuts)
Source: "..\assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
