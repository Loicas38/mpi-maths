# compile-multiple-chapters-cours-td.ps1
# Script pour compiler plusieurs chapitres LaTeX (chapitre.tex, cours.tex et TD.tex) et les copier vers Google Drive

# commande pour enlever les parametres de securite pour executer : 
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Pour remettre la politique de securite par defaut :
# Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser

param(
    [Parameter(Mandatory=$false)]
    [string]$Chapitres = "last",  # Ex: "1,3,5" ou "all" pour tous ou "last" (defaut) pour le dernier chapitre
    
    [string]$CoursRoot = "C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\Maths\cours",
    [string]$DriveDestination = "G:\Mon Drive\cours_latex_MPI\MPI\Maths"
)

# Fonction pour compiler un fichier LaTeX
function Compile-LatexFile {
    param(
        [string]$TexFile,
        [string]$WorkingDirectory
    )
    
    Push-Location $WorkingDirectory
    
    try {
        if (-not (Test-Path $TexFile)) {
            Write-Host "ATTENTION: Le fichier $TexFile n'existe pas dans $WorkingDirectory" -ForegroundColor Yellow
            Pop-Location
            return $false
        }
        
        $PdfFile = $TexFile -replace '\.tex$', '.pdf'
        Write-Host "  Compilation de $TexFile..." -ForegroundColor Cyan
        
        # Compilation LaTeX (silencieuse)
        $output = pdflatex -interaction=nonstopmode $TexFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ERREUR lors de la compilation de $TexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        # Verifier que le PDF a ete genere
        if (-not (Test-Path $PdfFile)) {
            Write-Host "  ERREUR: Le PDF n'a pas ete genere pour $TexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        Write-Host "  OK: Compilation reussie de $TexFile" -ForegroundColor Green
        Pop-Location
        return $true
        
    } catch {
        Write-Host "  ERREUR inattendue lors de la compilation de $TexFile : $_" -ForegroundColor Red
        Pop-Location
        return $false
    }
}

# Fonction pour compiler l'integrale du cours
function Compile-Integrale {
    $IntegraleFolder = "integrale"
    $IntegraleFullPath = Join-Path $CoursRoot $IntegraleFolder
    
    # Verifier que le dossier existe
    if (-not (Test-Path $IntegraleFullPath)) {
        Write-Host "ATTENTION: Le dossier $IntegraleFolder n'existe pas" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "`nCompilation de l'integrale du cours..." -ForegroundColor Cyan
    
    $Success = $true
    
    # 1. Compiler Integrale_cours.tex (racine integrale)
    $IntegraleCoursTexFile = "Integrale_cours.tex"
    $IntegraleCoursPdfFile = "Integrale_cours.pdf"
    
    if (Compile-LatexFile -TexFile $IntegraleCoursTexFile -WorkingDirectory $IntegraleFullPath) {
        # Copier le PDF vers Google Drive dans le sous-dossier integrale
        Write-Host "  Deuxième compilation pour les liens ..." -ForegroundColor Blue
        if (Compile-LatexFile -TexFile $IntegraleCoursTexFile -WorkingDirectory $IntegraleFullPath) {
            $DriveFolderIntegrale = Join-Path $DriveDestination "integrale"
            if (-not (Test-Path $DriveFolderIntegrale)) {
                New-Item -ItemType Directory -Path $DriveFolderIntegrale -Force | Out-Null
                Write-Host "  Dossier cree : $DriveFolderIntegrale" -ForegroundColor Yellow
            }
            
            $DestPath = Join-Path $DriveFolderIntegrale $IntegraleCoursPdfFile
            Copy-Item (Join-Path $IntegraleFullPath $IntegraleCoursPdfFile) -Destination $DestPath -Force
            Write-Host "  PDF copie vers : $DestPath" -ForegroundColor Green
        } else {
            $Success = $false
        }
    } else {
        $Success = $false
    }
    
    # 2. Compiler Integrale_MPI.tex (racine integrale - chapitre complet)
    $IntegraleMPITexFile = "Integrale_MPI.tex"
    $IntegraleMPIPdfFile = "Integrale_MPI.pdf"
    
    if (Compile-LatexFile -TexFile $IntegraleMPITexFile -WorkingDirectory $IntegraleFullPath) {
        Write-Host "  Deuxième compilation pour les liens ..." -ForegroundColor Blue
        if (Compile-LatexFile -TexFile $IntegraleMPITexFile -WorkingDirectory $IntegraleFullPath) {
            $DriveFolderIntegrale = Join-Path $DriveDestination "integrale"
            if (-not (Test-Path $DriveFolderIntegrale)) {
                New-Item -ItemType Directory -Path $DriveFolderIntegrale -Force | Out-Null
            }
            $DestPath = Join-Path $DriveFolderIntegrale $IntegraleMPIPdfFile
            Copy-Item (Join-Path $IntegraleFullPath $IntegraleMPIPdfFile) -Destination $DestPath -Force
            Write-Host "  PDF copie vers : $DestPath" -ForegroundColor Green
        } else {
            $Success = $false
        }
    } else {
        $Success = $false
    }
    
    # 3. Compiler Integrale_MPI.tex (dans integrale_TD)
    $IntegraleTDFolder = Join-Path $IntegraleFullPath "integrale_TD"
    $IntegraleTDTexFile = "Integrale_TD.tex"
    $IntegraleTDPdfFile = "Integrale_TD.pdf"  # Renommer pour eviter les conflits
    
    if (Test-Path $IntegraleTDFolder) {
        if (Compile-LatexFile -TexFile $IntegraleTDTexFile -WorkingDirectory $IntegraleTDFolder) {
            Write-Host "  Deuxième compilation pour les liens ..." -ForegroundColor Blue
            if (Compile-LatexFile -TexFile $IntegraleTDTexFile -WorkingDirectory $IntegraleTDFolder) {
                $DriveFolderIntegrale = Join-Path $DriveDestination "integrale"
                if (-not (Test-Path $DriveFolderIntegrale)) {
                    New-Item -ItemType Directory -Path $DriveFolderIntegrale -Force | Out-Null
                }
                $DestPath = Join-Path $DriveFolderIntegrale $IntegraleTDPdfFile
                Copy-Item (Join-Path $IntegraleTDFolder ($IntegraleTDTexFile -replace '\.tex$', '.pdf')) -Destination $DestPath -Force
                Write-Host "  PDF copie vers : $DestPath" -ForegroundColor Green
            } else {
                $Success = $false
            }
        } else {
            $Success = $false
        }
    } else {
        Write-Host "  ATTENTION: Le dossier integrale_TD n'existe pas" -ForegroundColor Yellow
        $Success = $false
    }
    
    return $Success
}

# Fonction pour compiler un chapitre (chapitre.tex, cours.tex, TD.tex)
function Compile-Chapitre {
    param(
        [int]$NumChapitre
    )
    
    $ChapitreFolder = "chapitre$NumChapitre"
    $ChapitreFullPath = Join-Path $CoursRoot $ChapitreFolder
    
    # Verifier que le dossier existe
    if (-not (Test-Path $ChapitreFullPath)) {
        Write-Host "ATTENTION: Le dossier $ChapitreFolder n'existe pas" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "`nCompilation du chapitre $NumChapitre..." -ForegroundColor Cyan
    
    $Success = $true
    
    # Creer le dossier de destination sur Google Drive si necessaire
    $DriveFolderDest = Join-Path $DriveDestination $ChapitreFolder
    if (-not (Test-Path $DriveFolderDest)) {
        New-Item -ItemType Directory -Path $DriveFolderDest -Force | Out-Null
        Write-Host "  Dossier cree : $DriveFolderDest" -ForegroundColor Yellow
    }
    
    # 1. Compiler chapitre.tex (racine du chapitre)
    $ChapitreTexFile = "chapitre$NumChapitre.tex"
    $ChapitrePdfFile = "chapitre$NumChapitre.pdf"
    
    if (Compile-LatexFile -TexFile $ChapitreTexFile -WorkingDirectory $ChapitreFullPath) {
        $DestPath = Join-Path $DriveFolderDest $ChapitrePdfFile
        Copy-Item (Join-Path $ChapitreFullPath $ChapitrePdfFile) -Destination $DestPath -Force
        Write-Host "  PDF copie vers : $DestPath" -ForegroundColor Green
    } else {
        $Success = $false
    }
    
    # 2. Compiler cours.tex (dans le sous-dossier cours)
    $CoursFolder = Join-Path $ChapitreFullPath "cours"
    $CoursTexFile = "cours$NumChapitre.tex"
    $CoursPdfFile = "cours$NumChapitre.pdf"
    
    if (Test-Path $CoursFolder) {
        if (Compile-LatexFile -TexFile $CoursTexFile -WorkingDirectory $CoursFolder) {
            $DestPath = Join-Path $DriveFolderDest $CoursPdfFile
            Copy-Item (Join-Path $CoursFolder $CoursPdfFile) -Destination $DestPath -Force
            Write-Host "  PDF copie vers : $DestPath" -ForegroundColor Green
        } else {
            $Success = $false
        }
    } else {
        Write-Host "  ATTENTION: Le dossier cours n'existe pas dans $ChapitreFolder" -ForegroundColor Yellow
        $Success = $false
    }
    
    # 3. Compiler TD.tex (dans le sous-dossier TD)
    $TDFolder = Join-Path $ChapitreFullPath "TD"
    $TDTexFile = "TD$NumChapitre.tex"
    $TDPdfFile = "TD$NumChapitre.pdf"
    
    if (Test-Path $TDFolder) {
        if (Compile-LatexFile -TexFile $TDTexFile -WorkingDirectory $TDFolder) {
            $DestPath = Join-Path $DriveFolderDest $TDPdfFile
            Copy-Item (Join-Path $TDFolder $TDPdfFile) -Destination $DestPath -Force
            Write-Host "  PDF copie vers : $DestPath" -ForegroundColor Green
        } else {
            $Success = $false
        }
    } else {
        Write-Host "  ATTENTION: Le dossier TD n'existe pas dans $ChapitreFolder" -ForegroundColor Yellow
        $Success = $false
    }
    
    return $Success
}

# Programme principal
Write-Host "=======================================================" -ForegroundColor Magenta
Write-Host "   Compilation et copie de chapitres LaTeX (Cours + TD)" -ForegroundColor Magenta
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
        Write-Host "Usage: .\compilation_drive_cours_td.ps1 -Chapitres '1,3,5' ou -Chapitres 'all' ou -Chapitres 'last' ou -Chapitres 'integrale'" -ForegroundColor Yellow
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
