; Inno Setup Script dla SWD Desktop App

[Setup]
; Informacje o aplikacji
AppName=SWD Desktop App
AppVersion=1.0.0
AppPublisher=Twoja Firma
AppPublisherURL=https://twojafirma.pl
AppSupportURL=https://twojafirma.pl/support
AppUpdatesURL=https://twojafirma.pl/updates

; Katalogi instalacji
DefaultDirName={autopf}\SWD Desktop App
DefaultGroupName=SWD Desktop App
DisableProgramGroupPage=yes

; Wyjście
OutputDir=output
OutputBaseFilename=SWD-DesktopApp-Setup-v1.0.0
SetupIconFile=..\desktop\icon.ico
UninstallDisplayIcon={app}\SWD-DesktopApp.exe

; Kompresja
Compression=lzma2
SolidCompression=yes

; Wizard
WizardStyle=modern

; Architektura
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Wymagania
MinVersion=10.0

; Uprawnienia
PrivilegesRequired=admin

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Główny plik exe
Source: "..\desktop\dist\SWD-DesktopApp.exe"; DestDir: "{app}"; Flags: ignoreversion

; Dodatkowe pliki jeśli potrzebne (README, LICENSE, etc.)
; Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Skrót w menu Start
Name: "{group}\SWD Desktop App"; Filename: "{app}\SWD-DesktopApp.exe"
Name: "{group}\{cm:UninstallProgram,SWD Desktop App}"; Filename: "{uninstallexe}"

; Skrót na pulpicie (jeśli użytkownik wybrał)
Name: "{autodesktop}\SWD Desktop App"; Filename: "{app}\SWD-DesktopApp.exe"; Tasks: desktopicon

[Run]
; Opcjonalnie uruchom aplikację po instalacji
Filename: "{app}\SWD-DesktopApp.exe"; Description: "{cm:LaunchProgram,SWD Desktop App}"; Flags: nowait postinstall skipifsilent

[Code]
// Sprawdź czy aplikacja jest uruchomiona przed instalacją
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Sprawdź czy aplikacja jest uruchomiona
  if CheckForMutexes('SWDDesktopAppMutex') then
  begin
    if MsgBox('SWD Desktop App jest obecnie uruchomiona. Zamknij aplikację aby kontynuować instalację.', mbError, MB_OKCANCEL) = IDOK then
    begin
      Result := False;
    end;
  end;
end;

// Pokaż komunikat po instalacji
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Możesz tutaj dodać dodatkowe akcje po instalacji
  end;
end;