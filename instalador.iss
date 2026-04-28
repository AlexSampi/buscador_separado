[Setup]
AppName=Buscador de CVs
AppVersion=1.0
AppPublisher=Ariana Garcia
DefaultDirName={autopf}\Buscador de CVs
DefaultGroupName=Buscador de CVs
OutputDir=.
OutputBaseFilename=Setup_Buscador_CVs
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Files]
Source: "Organizacion_CV\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Buscador de CVs"; Filename: "{app}\Organizacion_CV.exe"
Name: "{group}\Desinstalar Buscador de CVs"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Buscador de CVs"; Filename: "{app}\Organizacion_CV.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Organizacion_CV.exe"; Description: "Abrir Buscador de CVs"; Flags: nowait postinstall skipifsilent