@echo off
echo ===================================
echo Extracteur Anki vers LaTeX
echo ===================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé ou n'est pas dans le PATH
    echo Téléchargez Python depuis https://www.python.org/
    pause
    exit /b 1
)

REM Installer les dépendances si nécessaire
echo Installation des dépendances...
pip install -q -r requirements.txt

echo.
echo Lancement du script...
echo.

REM Lancer le script Python
python anki_to_latex.py

echo.
pause
