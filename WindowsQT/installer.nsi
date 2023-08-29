; Include utilities for creating shortcuts
!include "MUI2.nsh"
!include "FileFunc.nsh"

Icon "C:\Users\uldarik\Documents\WindowsQT\icon.ico"

; The name of the installer and its properties
Outfile "AmiiboCardGeneratorSuite_Install.exe"
Name "Amiibo Card Generator Suite QT"
InstallDir "$PROFILE\AmiiboCardGen" ; Default installation directory

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

; Define Start Menu folder
!define STARTMENUNAME "Amiibo Card Generator Suite"

; Sections
Section "Main Program"

    ; Set the installation directory
    SetOutPath "$INSTDIR"

    ; Include your files here
    File /r "C:\Users\uldarik\Documents\WindowsQT\*.*"

    ; Create a shortcut on the desktop
    CreateShortCut "$DESKTOP\Amiibo Cards Generator Suite.lnk" "$INSTDIR\launcher.exe" "" "$INSTDIR\icon.ico"
    WriteUninstaller "$INSTDIR\Uninstaller.exe"



    ; Run Python commands to install required packages
    Exec "python.exe -m pip install --upgrade pip"
    Exec "python.exe -m pip install requests"
    Exec "python.exe -m pip install pillow"
    Exec "python.exe -m pip install pyside6"

SectionEnd

Section /o "Start Menu Shortcut"

    ; Create a Start Menu entry
    CreateDirectory "$SMPROGRAMS\${STARTMENUNAME}"
    CreateShortCut "$SMPROGRAMS\${STARTMENUNAME}\Amiibo Cards Generator Suite.lnk" "$INSTDIR\launcher.exe" "" "$INSTDIR\icon.ico"
    CreateShortCut "$SMPROGRAMS\${STARTMENUNAME}\Uninstall Amiibo Cards Generator Suite.lnk" "$INSTDIR\Uninstaller.exe"

SectionEnd

; Uninstaller Section
Section "Uninstall"

    
    ; Remove the desktop shortcut
    Delete "$DESKTOP\Amiibo Cards Generator Suite.lnk"

    ; Remove Start Menu entry
    Delete "$SMPROGRAMS\${STARTMENUNAME}\Amiibo Cards Generator Suite.lnk"
    RMDir "$SMPROGRAMS\${STARTMENUNAME}"

    ; Remove files
    RMDir /r "$INSTDIR"
    Delete "$INSTDIR\Uninstaller.exe"


SectionEnd
