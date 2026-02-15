; Inno Setup Script dla Strazak Desktop App

#define MyAppName "Strażak"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Twoja Firma"
#define MyAppURL "https://example.com"
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

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\desktop\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\data\app.db"; Flags: dontcopy

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DatabaseTypePage: TInputOptionWizardPage;
  LocalDatabaseDirPage: TInputDirWizardPage;
  NetworkDatabasePage: TInputFileWizardPage;

procedure InitializeWizard;
begin
  DatabaseTypePage := CreateInputOptionPage(wpSelectDir,
    'Konfiguracja bazy danych',
    'Wybierz sposób przechowywania danych',
    'Aplikacja może używać lokalnej bazy danych lub współdzielonej bazy w sieci.' + #13#10 + #13#10 +
    'Wybierz odpowiednią opcję:',
    True, False);
  
  DatabaseTypePage.Add('Lokalna baza danych (tylko dla tego komputera)');
  DatabaseTypePage.Add('Baza danych w zasobie sieciowym (współdzielona z innymi komputerami)');
  DatabaseTypePage.Values[0] := True;
  
  LocalDatabaseDirPage := CreateInputDirPage(DatabaseTypePage.ID,
    'Lokalizacja lokalnej bazy danych',
    'Gdzie zapisać lokalną bazę danych?',
    'Wybierz folder, w którym będzie przechowywana baza danych aplikacji.' + #13#10 + #13#10 +
    'ZALECANE: Użyj domyślnej lokalizacji (kliknij Dalej bez zmian).',
    False, '');
  
  LocalDatabaseDirPage.Add('');
  { Nie ustawiaj tutaj - zostaw puste }
  LocalDatabaseDirPage.Values[0] := '';
  
  NetworkDatabasePage := CreateInputFilePage(DatabaseTypePage.ID,
    'Ścieżka do bazy sieciowej',
    'Podaj ścieżkę do współdzielonej bazy danych',
    'Wprowadź pełną ścieżkę sieciową do pliku bazy danych (np. \\serwer\udział\StrazakApp\app.db)' + #13#10 + #13#10 +
    'Upewnij się, że masz uprawnienia do odczytu i zapisu w tej lokalizacji.');
  
  NetworkDatabasePage.Add('Ścieżka do bazy danych:', 'Pliki bazy SQLite (*.db)|*.db|Wszystkie pliki (*.*)|*.*', '.db');
  NetworkDatabasePage.Values[0] := '\\serwer\udział\StrazakApp\app.db';
end;

procedure CurPageChanged(CurPageID: Integer);
begin
   // Set default value when user enters the page 
  if CurPageID = LocalDatabaseDirPage.ID then
  begin
    if LocalDatabaseDirPage.Values[0] = '' then
    begin
      // Now app is already initialized 
      LocalDatabaseDirPage.Values[0] := ExpandConstant('{app}\data');
    end;
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  
  if PageID = LocalDatabaseDirPage.ID then
    Result := DatabaseTypePage.Values[1]
  else if PageID = NetworkDatabasePage.ID then
    Result := DatabaseTypePage.Values[0];
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  NetworkPath: string;
  NetworkDir: string;
begin
  Result := True;
  
  { Walidacja ścieżki sieciowej }
  if CurPageID = NetworkDatabasePage.ID then
  begin
    NetworkPath := NetworkDatabasePage.Values[0];
    
    { Sprawdź czy ścieżka zaczyna się od \\ (UNC path) }
    if (Length(NetworkPath) < 3) or (Copy(NetworkPath, 1, 2) <> '\\') then
    begin
      MsgBox('Ścieżka sieciowa musi zaczynać się od \\ (np. \\serwer\udział\folder\app.db)', mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    NetworkDir := ExtractFileDir(NetworkPath);
    
    { Sprawdź czy katalog jest dostępny }
    if not DirExists(NetworkDir) then
    begin
      if MsgBox('Nie można uzyskać dostępu do folderu sieciowego:' + #13#10 +
                NetworkDir + #13#10 + #13#10 +
                'Czy na pewno chcesz kontynuować?' + #13#10 +
                '(Upewnij się, że zasób sieciowy jest dostępny przed uruchomieniem aplikacji)',
                mbConfirmation, MB_YESNO) = IDNO then
      begin
        Result := False;
        Exit;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: string;
  ConfigContent: TStringList;
  DatabasePath: string;
  LocalDir: string;
  UseDefaultLocation: Boolean;
begin
  if CurStep = ssPostInstall then
  begin
    { Lokalna baza danych }
    if DatabaseTypePage.Values[0] then
    begin
      LocalDir := LocalDatabaseDirPage.Values[0];
      
      { Sprawdź czy to domyślna lokalizacja (obok exe) }
      UseDefaultLocation := (LocalDir = ExpandConstant('{app}\data'));
      
      if UseDefaultLocation then
      begin
        { DOMYŚLNA LOKALIZACJA - NIE twórz config.ini }
        DatabasePath := ExpandConstant('{app}\data\app.db');
        
        { Utwórz folder data }
        ForceDirectories(ExpandConstant('{app}\data'));
        
        { Kopiuj przykładową bazę jeśli nie istnieje }
        if not FileExists(DatabasePath) then
        begin
          ExtractTemporaryFile('app.db');
          FileCopy(ExpandConstant('{tmp}\app.db'), DatabasePath, False);
        end;
        
        MsgBox('Aplikacja zostanie zainstalowana z domyślną bazą danych w:' + #13#10 +
               DatabasePath + #13#10 + #13#10 +
               'Dane będą przechowywane lokalnie na tym komputerze.',
               mbInformation, MB_OK);
      end
      else
      begin
        { WŁASNA LOKALIZACJA - utwórz config.ini }
        DatabasePath := LocalDir + '\app.db';
        
        { Utwórz folder }
        ForceDirectories(LocalDir);
        
        { Kopiuj przykładową bazę jeśli nie istnieje }
        if not FileExists(DatabasePath) then
        begin
          ExtractTemporaryFile('app.db');
          FileCopy(ExpandConstant('{tmp}\app.db'), DatabasePath, False);
        end;
        
        { Zapisz config.ini }
        ConfigContent := TStringList.Create;
        try
          ConfigContent.Add('[Database]');
          ConfigContent.Add('Type=local');
          ConfigContent.Add('Path=' + DatabasePath);
          
          ConfigFile := ExpandConstant('{app}\config.ini');
          ConfigContent.SaveToFile(ConfigFile);
        finally
          ConfigContent.Free;
        end;
        
        MsgBox('Lokalna baza danych została utworzona w:' + #13#10 +
               DatabasePath,
               mbInformation, MB_OK);
      end;
    end
    { Baza sieciowa - zawsze twórz config.ini }
    else
    begin
      DatabasePath := NetworkDatabasePage.Values[0];
      
      ConfigContent := TStringList.Create;
      try
        ConfigContent.Add('[Database]');
        ConfigContent.Add('Type=network');
        ConfigContent.Add('Path=' + DatabasePath);
        
        ConfigFile := ExpandConstant('{app}\config.ini');
        ConfigContent.SaveToFile(ConfigFile);
      finally
        ConfigContent.Free;
      end;
      
      { Sprawdź czy plik istnieje, jeśli nie - zaoferuj utworzenie }
      if not FileExists(DatabasePath) then
      begin
        if MsgBox('Plik bazy danych nie istnieje w lokalizacji:' + #13#10 +
                  DatabasePath + #13#10 + #13#10 +
                  'Czy chcesz utworzyć nową bazę danych w tej lokalizacji?',
                  mbConfirmation, MB_YESNO) = IDYES then
        begin
          try
            ForceDirectories(ExtractFileDir(DatabasePath));
            ExtractTemporaryFile('app.db');
            FileCopy(ExpandConstant('{tmp}\app.db'), DatabasePath, False);
            
            MsgBox('Baza danych została utworzona w zasobie sieciowym.' + #13#10 + #13#10 +
                   'Wszystkie komputery będą współdzielić dane.',
                   mbInformation, MB_OK);
          except
            MsgBox('BŁĄD: Nie można utworzyć bazy danych!' + #13#10 + #13#10 +
                   'Sprawdź uprawnienia i dostępność zasobu sieciowego.',
                   mbError, MB_OK);
          end;
        end;
      end
      else
      begin
        MsgBox('Aplikacja zostanie skonfigurowana do używania istniejącej bazy:' + #13#10 +
               DatabasePath,
               mbInformation, MB_OK);
      end;
    end;
  end;
end;
