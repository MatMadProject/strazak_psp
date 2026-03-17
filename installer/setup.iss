; Inno Setup Script dla Strazak Desktop App

#define MyAppName "Strażak"
#define MyAppVersion "0.5.2"
#define MyAppPublisher "MatMad Software"
#define MyAppURL "https://straznica.com.pl"
#define MyAppExeName "Strazak-DesktopApp.exe"

[Setup]
AppId={{92BE2677-9806-4A64-A3AC-3345859EF48C}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=output
OutputBaseFilename=Strazak-Setup-v{#MyAppVersion}
SetupIconFile=..\desktop\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
; Zamknij aplikację jeśli jest uruchomiona przed instalacją
CloseApplications=yes
CloseApplicationsFilter=*.exe

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\desktop\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  OldVersion: String;
  UninstallPath: String;
  ResultCode: Integer;
begin
  Result := True;

  { Sprawdź czy poprzednia wersja jest zainstalowana }
  if RegQueryStringValue(HKLM,
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\{92BE2677-9806-4A64-A3AC-3345859EF48C}_is1',
    'DisplayVersion', OldVersion) then
  begin
    if MsgBox('Wykryto zainstalowaną wersję ' + OldVersion + ' aplikacji ' + '{#MyAppName}' + '.' + #13#10 + #13#10 +
              'Przed instalacją nowej wersji należy odinstalować poprzednią.' + #13#10 +
              'Czy chcesz to zrobić teraz?',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      if RegQueryStringValue(HKLM,
        'Software\Microsoft\Windows\CurrentVersion\Uninstall\{92BE2677-9806-4A64-A3AC-3345859EF48C}_is1',
        'UninstallString', UninstallPath) then
      begin
        Exec(RemoveQuotes(UninstallPath), '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
        if ResultCode <> 0 then
        begin
          MsgBox('Odinstalowanie nie powiodło się (kod: ' + IntToStr(ResultCode) + ').' + #13#10 +
                 'Spróbuj odinstalować ręcznie z Panelu sterowania.',
                 mbError, MB_OK);
          Result := False;
        end;
      end;
    end
    else
    begin
      Result := False;
    end;
  end;
end;
