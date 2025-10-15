@echo off
REM Script batch pour créer l'exécutable Wigor Viewer
REM Usage: double-cliquer sur ce fichier ou lancer depuis l'invite de commande

echo ========================================
echo Build Wigor Viewer - Executable Windows
echo ========================================

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé ou pas dans le PATH
    echo Installez Python depuis https://python.org
    pause
    exit /b 1
)

echo Python detecte: 
python --version

REM Installer les dépendances
echo.
echo Installation des dependances...
python -m pip install -r requirements.txt

REM Lancer le script de build
echo.
echo Lancement du build...
python build_exe.py

echo.
if exist dist\WigorViewer.exe (
    echo ✅ BUILD REUSSI!
    echo L'executable se trouve dans: dist\WigorViewer.exe
    echo.
    echo Voulez-vous ouvrir le dossier dist? (o/n)
    set /p choice=
    if /i "%choice%"=="o" (
        explorer dist
    )
) else (
    echo ❌ BUILD ECHOUE!
    echo Verifiez les erreurs ci-dessus.
)

echo.
pause