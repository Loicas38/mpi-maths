# compile-multiple-chapters.ps1
# Script pour compiler plusieurs chapitres LaTeX et les copier vers Google Drive

# commande pour enlever les paramètres de sécurité pour exécuter : 
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Pour remetrre la politique de sécurité par défaut :
# Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser

param(
    [Parameter(Mandatory=$true)]
    [string]$Chapitres,  # Ex: "1,3,5" ou "all" pour tous ou "integrale" pour le cours complet
    
    [string]$CoursRoot = "C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\Maths\cours\test_compile",
    [string]$DriveDestination = "C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\Maths\cours\test_compile\pdfs"
)

# Fonction pour compiler l'intégrale du cours
function Compile-Integrale {
    $IntegraleFolder = "integrale"
    $IntegraleFullPath = Join-Path $CoursRoot $IntegraleFolder
    
    # Vérifier que le dossier existe
    if (-not (Test-Path $IntegraleFullPath)) {
        Write-Host "⚠️  Le dossier $IntegraleFolder n'existe pas" -ForegroundColor Yellow
        return $false
    }
    
    # Se déplacer dans le dossier intégrale
    Push-Location $IntegraleFullPath
    
    try {
        # Trouver le fichier .tex principal (généralement integrale.tex ou cours_complet.tex)
        $TexFiles = Get-ChildItem -Filter "*.tex" | Where-Object { $_.Name -notmatch '^contenu' }
        
        if ($TexFiles.Count -eq 0) {
            Write-Host "⚠️  Aucun fichier .tex trouvé dans $IntegraleFolder" -ForegroundColor Yellow
            Pop-Location
            return $false
        }
        
        # Prendre le premier fichier .tex trouvé
        $IntegraleTexFile = $TexFiles[0].Name
        $IntegralePdfFile = $IntegraleTexFile -replace '\.tex$', '.pdf'
        
        Write-Host "`n📚 Compilation de l'intégrale du cours ($IntegraleTexFile)..." -ForegroundColor Cyan
        
        # Compilation LaTeX (silencieuse)
        $output = pdflatex -interaction=nonstopmode $IntegraleTexFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Erreur lors de la compilation de $IntegraleTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        # Vérifier que le PDF a été généré
        if (-not (Test-Path $IntegralePdfFile)) {
            Write-Host "❌ Le PDF n'a pas été généré pour $IntegraleTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        Write-Host "✅ Compilation réussie de l'intégrale du cours" -ForegroundColor Green
        
        # Copier le PDF vers Google Drive (racine du dossier PDFs)
        if (-not (Test-Path $DriveDestination)) {
            New-Item -ItemType Directory -Path $DriveDestination -Force | Out-Null
            Write-Host "📁 Dossier créé : $DriveDestination" -ForegroundColor Yellow
        }
        
        $DestPath = Join-Path $DriveDestination $IntegralePdfFile
        Copy-Item $IntegralePdfFile -Destination $DestPath -Force
        Write-Host "📤 PDF copié vers : $DestPath" -ForegroundColor Green
        
        Pop-Location
        return $true
        
    } catch {
        Write-Host "❌ Erreur inattendue : $_" -ForegroundColor Red
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
    
    # Vérifier que le dossier existe
    if (-not (Test-Path $ChapitreFullPath)) {
        Write-Host "⚠️  Le dossier $ChapitreFolder n'existe pas" -ForegroundColor Yellow
        return $false
    }
    
    # Se déplacer dans le dossier du chapitre
    Push-Location $ChapitreFullPath
    
    try {
        # Vérifier que le fichier .tex existe
        if (-not (Test-Path $ChapitreTexFile)) {
            Write-Host "⚠️  Le fichier $ChapitreTexFile n'existe pas dans $ChapitreFolder" -ForegroundColor Yellow
            Pop-Location
            return $false
        }
        
        Write-Host "`n📝 Compilation de $ChapitreTexFile..." -ForegroundColor Cyan
        
        # Compilation LaTeX (silencieuse)
        $output = pdflatex -interaction=nonstopmode $ChapitreTexFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Erreur lors de la compilation de $ChapitreTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        # Vérifier que le PDF a été généré
        if (-not (Test-Path $ChaptrePdfFile)) {
            Write-Host "❌ Le PDF n'a pas été généré pour $ChapitreTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        Write-Host "✅ Compilation réussie de $ChapitreTexFile" -ForegroundColor Green
        
        # Créer le dossier de destination sur Google Drive si nécessaire
        $DriveFolderDest = Join-Path $DriveDestination $ChapitreFolder
        if (-not (Test-Path $DriveFolderDest)) {
            New-Item -ItemType Directory -Path $DriveFolderDest -Force | Out-Null
            Write-Host "📁 Dossier créé : $DriveFolderDest" -ForegroundColor Yellow
        }
        
        # Copier le PDF vers Google Drive
        $DestPath = Join-Path $DriveFolderDest $ChaptrePdfFile
        Copy-Item $ChaptrePdfFile -Destination $DestPath -Force
        Write-Host "📤 PDF copié vers : $DestPath" -ForegroundColor Green
        
        Pop-Location
        return $true
        
    } catch {
        Write-Host "❌ Erreur inattendue : $_" -ForegroundColor Red
        Pop-Location
        return $false
    }
}

# Programme principal
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "   Compilation et copie de chapitres LaTeX" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta

# Déterminer quels chapitres compiler
$ChapitresACompiler = @()
$CompilerIntegrale = $false

if ($Chapitres -eq "integrale" -or $Chapitres -eq "intégrale" -or $Chapitres -eq "complet") {
    # Compiler l'intégrale du cours
    Write-Host "`n📚 Compilation de l'intégrale du cours..." -ForegroundColor Cyan
    $CompilerIntegrale = $true
    
} elseif ($Chapitres -eq "all" -or $Chapitres -eq "tout") {
    Write-Host "`n🔍 Recherche de tous les chapitres..." -ForegroundColor Cyan
    
    # Trouver tous les dossiers chapitre*
    $ChapitresFolders = Get-ChildItem -Path $CoursRoot -Directory -Filter "chapitre*" | 
                        Where-Object { $_.Name -match '^chapitre(\d+)$' } |
                        ForEach-Object { [int]$Matches[1] } |
                        Sort-Object
    
    if ($ChapitresFolders.Count -eq 0) {
        Write-Host "❌ Aucun chapitre trouvé dans $CoursRoot" -ForegroundColor Red
        exit 1
    }
    
    $ChapitresACompiler = $ChapitresFolders
    Write-Host "📚 Chapitres trouvés : $($ChapitresACompiler -join ', ')" -ForegroundColor Cyan
    
} else {
    # Parser les numéros de chapitres
    $ChapitresACompiler = $Chapitres -split ',' | ForEach-Object { 
        $_.Trim() 
    } | Where-Object { 
        $_ -match '^\d+$' 
    } | ForEach-Object { 
        [int]$_ 
    } | Sort-Object -Unique
    
    if ($ChapitresACompiler.Count -eq 0) {
        Write-Host "❌ Aucun numéro de chapitre valide spécifié" -ForegroundColor Red
        Write-Host "Usage: .\compile-multiple-chapters.ps1 -Chapitres '1,3,5' ou -Chapitres 'all' ou -Chapitres 'integrale'" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "📚 Chapitres à compiler : $($ChapitresACompiler -join ', ')" -ForegroundColor Cyan
}

# Compiler l'intégrale ou les chapitres
$Reussites = 0
$Echecs = 0

if ($CompilerIntegrale) {
    if (Compile-Integrale) {
        $Reussites++
    } else {
        $Echecs++
    }
} else {
    # Compiler chaque chapitre
    foreach ($NumChapitre in $ChapitresACompiler) {
        if (Compile-Chapitre -NumChapitre $NumChapitre) {
            $Reussites++
        } else {
            $Echecs++
        }
    }
}

# Résumé
Write-Host "`n═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "   Résumé" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "✅ Réussites : $Reussites" -ForegroundColor Green
Write-Host "❌ Échecs    : $Echecs" -ForegroundColor $(if ($Echecs -gt 0) { "Red" } else { "Gray" })
Write-Host "🔄 Les fichiers seront synchronisés automatiquement avec Google Drive" -ForegroundColor Cyan

if ($Echecs -eq 0) {
    if ($CompilerIntegrale) {
        Write-Host "`n🎉 L'intégrale du cours a été compilée et copiée avec succès !" -ForegroundColor Green
    } else {
        Write-Host "`n🎉 Tous les chapitres ont été compilés et copiés avec succès !" -ForegroundColor Green
    }
    exit 0
} else {
    exit 1
}
