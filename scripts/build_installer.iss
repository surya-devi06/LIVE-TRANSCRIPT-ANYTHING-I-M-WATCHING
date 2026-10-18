; Inno Setup script to create an installer for Live Transcript
; ----------------------------------------------------------
; This script assumes you have already built the one‑file or onedir
; executable and that the output folder is:
;   <project_root>\dist\LiveTranscript
;
; Save this file as `scripts\build_installer.iss`
;
[Setup]
AppName=Live Transcript
AppVersion=0.1.0
DefaultDirName={autopf}\Live Transcript
DefaultGroupName=Live Transcript
UninstallDisplayIcon={app}\LiveTranscript.exe
OutputBaseFilename=LiveTranscript_Installer
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
LicenseFile=LICENSE.txt
SetupIconFile=..\assets\icon.ico
;WizardImageFile=assets\installer_bitmap.bmp ; optional background image
;WizardSmallImageFile=assets\installer_small.bmp ; optional small image

[Files]
; Main executable (either onedir or single exe)
Source: "..\dist\LiveTranscript.exe"; DestDir: "{app}"; Flags: ignoreversion

; Include any additional resources you want packaged (e.g., README, changelog)
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Live Transcript"; Filename: "{app}\LiveTranscript.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"
Name: "{commondesktop}\Live Transcript"; Filename: "{app}\LiveTranscript.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Run]
; Launch the app after install (optional)
Filename: "{app}\LiveTranscript.exe"; Description: "Run Live Transcript"; Flags: nowait postinstall skipifsilent

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Code]
function InitializeSetup(): Boolean;
begin
  // You can add custom checks here (e.g., verify Windows version)
  Result := True;
end;
