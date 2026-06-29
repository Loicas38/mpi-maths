# compile-multiple-chapters.ps1
# Script pour compiler plusieurs chapitres LaTeX et les copier vers Google Drive

# commande pour enlever les parametres de securite pour executer : 
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Pour remettre la politique de securite par defaut :
# Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser

param(
    [Parameter(Mandatory=$false)]
    [string]$Chapitres = "last",  # Ex: "1,3,5" ou "all" pour tous ou "last" (defaut) pour le dernier chapitre + integrale
    
    [string]$CoursRoot = "C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\Maths\cours",
    [string]$DriveDestination = "G:\Mon Drive\cours_latex_MPI\MPI\Maths"
)

# Fonction pour compiler l'integrale du cours
function Compile-Integrale {
    $IntegraleFolder = "integrale"
    $IntegraleFullPath = Join-Path $CoursRoot $IntegraleFolder
    
    # Verifier que le dossier existe
    if (-not (Test-Path $IntegraleFullPath)) {
        Write-Host "ATTENTION: Le dossier $IntegraleFolder n'existe pas" -ForegroundColor Yellow
        return $false
    }
    
    # Se deplacer dans le dossier integrale
    Push-Location $IntegraleFullPath
    
    try {
        # Trouver le fichier .tex principal (generalement integrale.tex ou cours_complet.tex)
        $TexFiles = Get-ChildItem -Filter "*.tex" | Where-Object { $_.Name -notmatch '^contenu' }
        
        if ($TexFiles.Count -eq 0) {
            Write-Host "ATTENTION: Aucun fichier .tex trouve dans $IntegraleFolder" -ForegroundColor Yellow
            Pop-Location
            return $false
        }
        
        # Prendre le premier fichier .tex trouve
        $IntegraleTexFile = $TexFiles[0].Name
        $IntegralePdfFile = $IntegraleTexFile -replace '\.tex$', '.pdf'
        
        Write-Host "`nCompilation de l'integrale du cours ($IntegraleTexFile)..." -ForegroundColor Cyan
        
        # Compilation LaTeX (silencieuse)
        $output = pdflatex -interaction=nonstopmode $IntegraleTexFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERREUR lors de la compilation de $IntegraleTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        # Verifier que le PDF a ete genere
        if (-not (Test-Path $IntegralePdfFile)) {
            Write-Host "ERREUR: Le PDF n'a pas ete genere pour $IntegraleTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        Write-Host "OK: Compilation reussie de l'integrale du cours" -ForegroundColor Green
        
        # Copier le PDF vers Google Drive (racine du dossier PDFs)
        if (-not (Test-Path $DriveDestination)) {
            New-Item -ItemType Directory -Path $DriveDestination -Force | Out-Null
            Write-Host "Dossier cree : $DriveDestination" -ForegroundColor Yellow
        }
        
        $DestPath = Join-Path $DriveDestination $IntegralePdfFile
        Copy-Item $IntegralePdfFile -Destination $DestPath -Force
        Write-Host "PDF copie vers : $DestPath" -ForegroundColor Green
        
        Pop-Location
        return $true
        
    } catch {
        Write-Host "ERREUR inattendue : $_" -ForegroundColor Red
        Pop-Location
        return $false
    }
}

# Fonction pour compiler un chapitre
function Compile-Chapitre {
    param(
        [int]$NumChapitre
    )
    
    $ChapitreFolder = "chapitre$NumChapitre"
    $ChapitreTexFile = "chapitre$NumChapitre.tex"
    $ChaptrePdfFile = "chapitre$NumChapitre.pdf"
    $ChapitreFullPath = Join-Path $CoursRoot $ChapitreFolder
    
    # Verifier que le dossier existe
    if (-not (Test-Path $ChapitreFullPath)) {
        Write-Host "ATTENTION: Le dossier $ChapitreFolder n'existe pas" -ForegroundColor Yellow
        return $false
    }
    
    # Se deplacer dans le dossier du chapitre
    Push-Location $ChapitreFullPath
    
    try {
        # Verifier que le fichier .tex existe
        if (-not (Test-Path $ChapitreTexFile)) {
            Write-Host "ATTENTION: Le fichier $ChapitreTexFile n'existe pas dans $ChapitreFolder" -ForegroundColor Yellow
            Pop-Location
            return $false
        }
        
        Write-Host "`nCompilation de $ChapitreTexFile..." -ForegroundColor Cyan
        
        # Compilation LaTeX (silencieuse)
        $output = pdflatex -interaction=nonstopmode $ChapitreTexFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERREUR lors de la compilation de $ChapitreTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        # Verifier que le PDF a ete genere
        if (-not (Test-Path $ChaptrePdfFile)) {
            Write-Host "ERREUR: Le PDF n'a pas ete genere pour $ChapitreTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        Write-Host "OK: Compilation reussie de $ChapitreTexFile" -ForegroundColor Green
        
        # Creer le dossier de destination sur Google Drive si necessaire
        $DriveFolderDest = Join-Path $DriveDestination $ChapitreFolder
        if (-not (Test-Path $DriveFolderDest)) {
            New-Item -ItemType Directory -Path $DriveFolderDest -Force | Out-Null
            Write-Host "Dossier cree : $DriveFolderDest" -ForegroundColor Yellow
        }
        
        # Copier le PDF vers Google Drive
        $DestPath = Join-Path $DriveFolderDest $ChaptrePdfFile
        Copy-Item $ChaptrePdfFile -Destination $DestPath -Force
        Write-Host "PDF copie vers : $DestPath" -ForegroundColor Green
        
        Pop-Location
        return $true
        
    } catch {
        Write-Host "ERREUR inattendue : $_" -ForegroundColor Red
        Pop-Location
        return $false
    }
}

# Programme principal
Write-Host "=======================================================" -ForegroundColor Magenta
Write-Host "   Compilation et copie de chapitres LaTeX" -ForegroundColor Magenta
Write-Host "=======================================================" -ForegroundColor Magenta

# Determiner quels chapitres compiler
$ChapitresACompiler = @()
$CompilerIntegrale = $false
$OptionLast = $false

if ($Chapitres -eq "integrale" -or $Chapitres -eq "intégrale" -or $Chapitres -eq "complet") {
    # Compiler l'integrale du cours
    Write-Host "`nCompilation de l'integrale du cours..." -ForegroundColor Cyan
    $CompilerIntegrale = $true
    
} elseif ($Chapitres -eq "all" -or $Chapitres -eq "tout") {
    Write-Host "`nRecherche de tous les chapitres..." -ForegroundColor Cyan
    
    # Trouver tous les dossiers chapitre*
    $ChapitresFolders = Get-ChildItem -Path $CoursRoot -Directory -Filter "chapitre*" | 
                        Where-Object { $_.Name -match '^chapitre(\d+)$' } |
                        ForEach-Object { [int]$Matches[1] } |
                        Sort-Object
    
    if ($ChapitresFolders.Count -eq 0) {
        Write-Host "ERREUR: Aucun chapitre trouve dans $CoursRoot" -ForegroundColor Red
        exit 1
    }
    
    $ChapitresACompiler = $ChapitresFolders
    Write-Host "Chapitres trouves : $($ChapitresACompiler -join ', ')" -ForegroundColor Cyan
    
    # Inclure aussi l'integrale
    $CompilerIntegrale = $true
    Write-Host "L'integrale sera aussi compilee" -ForegroundColor Cyan
    
} elseif ($Chapitres -eq "last" -or $Chapitres -eq "dernier") {
    Write-Host "`nRecherche du dernier chapitre..." -ForegroundColor Cyan
    
    # Trouver tous les dossiers chapitre* et prendre le numero le plus eleve
    $ChapitresFolders = Get-ChildItem -Path $CoursRoot -Directory -Filter "chapitre*" | 
                        Where-Object { $_.Name -match '^chapitre(\d+)$' } |
                        ForEach-Object { [int]$Matches[1] } |
                        Sort-Object
    
    if ($ChapitresFolders.Count -eq 0) {
        Write-Host "ERREUR: Aucun chapitre trouve dans $CoursRoot" -ForegroundColor Red
        exit 1
    }
    
    # Prendre le dernier chapitre (numero le plus eleve)
    $DernierChapitre = $ChapitresFolders[-1]
    $ChapitresACompiler = @($DernierChapitre)
    Write-Host "Dernier chapitre trouve : $DernierChapitre" -ForegroundColor Cyan
    
    # Inclure aussi l'integrale
    $CompilerIntegrale = $true
    Write-Host "L'integrale sera aussi compilee" -ForegroundColor Cyan
    
    # Marquer que l'option last est utilisee
    $OptionLast = $true
    
} else {
    # Parser les numeros de chapitres
    $ChapitresACompiler = $Chapitres -split ',' | ForEach-Object { 
        $_.Trim() 
    } | Where-Object { 
        $_ -match '^\d+$' 
    } | ForEach-Object { 
        [int]$_ 
    } | Sort-Object -Unique
    
    if ($ChapitresACompiler.Count -eq 0) {
        Write-Host "ERREUR: Aucun numero de chapitre valide specifie" -ForegroundColor Red
        Write-Host "Usage: .\compile-multiple-chapters.ps1 -Chapitres '1,3,5' ou -Chapitres 'all' ou -Chapitres 'last' ou -Chapitres 'integrale'" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "Chapitres a compiler : $($ChapitresACompiler -join ', ')" -ForegroundColor Cyan
}

# Compiler l'integrale ou les chapitres
$Reussites = 0
$Echecs = 0

# Compiler les chapitres si necessaire
if ($ChapitresACompiler.Count -gt 0) {
    foreach ($NumChapitre in $ChapitresACompiler) {
        if (Compile-Chapitre -NumChapitre $NumChapitre) {
            $Reussites++
        } else {
            $Echecs++
        }
    }
}

# Compiler l'integrale si necessaire
if ($CompilerIntegrale) {
    if (Compile-Integrale) {
        $Reussites++
    } else {
        $Echecs++
    }
}

# Resume
Write-Host "`n=======================================================" -ForegroundColor Magenta
Write-Host "   Resume" -ForegroundColor Magenta
Write-Host "=======================================================" -ForegroundColor Magenta
Write-Host "OK: Reussites : $Reussites" -ForegroundColor Green
Write-Host "ERREUR: Echecs : $Echecs" -ForegroundColor $(if ($Echecs -gt 0) { "Red" } else { "Gray" })
Write-Host "Les fichiers seront synchronises automatiquement avec Google Drive" -ForegroundColor Cyan

if ($Echecs -eq 0) {
    if ($CompilerIntegrale -and $ChapitresACompiler.Count -gt 0) {
        Write-Host "`nSUCCES: Les chapitres et l'integrale ont ete compiles et copies avec succes !" -ForegroundColor Green
    } elseif ($CompilerIntegrale) {
        Write-Host "`nSUCCES: L'integrale du cours a ete compilee et copiee avec succes !" -ForegroundColor Green
    } else {
        Write-Host "`nSUCCES: Tous les chapitres ont ete compiles et copies avec succes !" -ForegroundColor Green
    }
    
    # Si l'option last est utilisee et qu'un chapitre a ete compile, lancer le script Python
    if ($OptionLast -and $ChapitresACompiler.Count -gt 0) {
        $NumeroChapitre = $ChapitresACompiler[0]
        $ScriptPython = "C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\Maths\cours\scripts_anki\scripts\importation_auto.py"
        
        Write-Host "`n======================================================="-ForegroundColor Magenta
        Write-Host "   Lancement du script d'importation Anki" -ForegroundColor Magenta
        Write-Host "=======================================================" -ForegroundColor Magenta
        Write-Host "Execution du script Python pour le chapitre $NumeroChapitre..." -ForegroundColor Cyan
        
        try {
            python $ScriptPython -c $NumeroChapitre
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "SUCCES: Script Python execute avec succes !" -ForegroundColor Green
            } else {
                Write-Host "ATTENTION: Le script Python a renvoye un code d'erreur: $LASTEXITCODE" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "ERREUR lors de l'execution du script Python: $_" -ForegroundColor Red
        }
    }
    
    exit 0
} else {
    exit 1
}
