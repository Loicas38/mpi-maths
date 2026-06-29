# compile-multiple-seances.ps1
# Script pour compiler plusieurs seances LaTeX et les copier vers Google Drive

# commande pour enlever les parametres de securite pour executer : 
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Pour remettre la politique de securite par defaut :
# Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser

param(
    [Parameter(Mandatory=$false)]
    [string]$Seances = "last",  # Ex: "1,3,5" ou "all" pour tous ou "last" (defaut) pour la derniere seance + integrale
    
    # dossier où se trouvent les dossiers des séances 
    [string]$CoursRoot = "C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\Maths\td_x-ens\latex",
    # dossier où seront copiés les fichiers pdf générés
    [string]$DriveDestination = "G:\Mon Drive\cours_latex_MPI\MPI\Maths\TD_X-ENS"
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
        
        # Copier le PDF vers Google Drive (racine du dossier)
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

# Fonction pour compiler une seance
function Compile-Seance {
    param(
        [int]$NumSeance
    )
    
    $SeanceFolder = "seance$NumSeance"
    $SeanceTexFile = "seance$NumSeance.tex"
    $SeancePdfFile = "seance$NumSeance.pdf"
    $SeanceFullPath = Join-Path $CoursRoot $SeanceFolder
    
    # Verifier que le dossier existe
    if (-not (Test-Path $SeanceFullPath)) {
        Write-Host "ATTENTION: Le dossier $SeanceFolder n'existe pas" -ForegroundColor Yellow
        return $false
    }
    
    # Se deplacer dans le dossier de la seance
    Push-Location $SeanceFullPath
    
    try {
        # Verifier que le fichier .tex existe
        if (-not (Test-Path $SeanceTexFile)) {
            Write-Host "ATTENTION: Le fichier $SeanceTexFile n'existe pas dans $SeanceFolder" -ForegroundColor Yellow
            Pop-Location
            return $false
        }
        
        Write-Host "`nCompilation de $SeanceTexFile..." -ForegroundColor Cyan
        
        # Compilation LaTeX (silencieuse)
        $output = pdflatex -interaction=nonstopmode $SeanceTexFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERREUR lors de la compilation de $SeanceTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        # Verifier que le PDF a ete genere
        if (-not (Test-Path $SeancePdfFile)) {
            Write-Host "ERREUR: Le PDF n'a pas ete genere pour $SeanceTexFile" -ForegroundColor Red
            Pop-Location
            return $false
        }
        
        Write-Host "OK: Compilation reussie de $SeanceTexFile" -ForegroundColor Green
        
        # Creer le dossier de destination sur Google Drive si necessaire
        if (-not (Test-Path $DriveDestination)) {
            New-Item -ItemType Directory -Path $DriveDestination -Force | Out-Null
            Write-Host "Dossier cree : $DriveDestination" -ForegroundColor Yellow
        }
        
        # Copier le PDF vers Google Drive (racine du dossier)
        $DestPath = Join-Path $DriveDestination $SeancePdfFile
        Copy-Item $SeancePdfFile -Destination $DestPath -Force
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
Write-Host "   Compilation et copie de seances LaTeX" -ForegroundColor Magenta
Write-Host "=======================================================" -ForegroundColor Magenta

# Determiner quelles seances compiler
$SeancesACompiler = @()
$CompilerIntegrale = $false

if ($Seances -eq "integrale" -or $Seances -eq "intégrale" -or $Seances -eq "complet") {
    # Compiler l'integrale du cours
    Write-Host "`nCompilation de l'integrale du cours..." -ForegroundColor Cyan
    $CompilerIntegrale = $true
    
} elseif ($Seances -eq "all" -or $Seances -eq "tout") {
    Write-Host "`nRecherche de toutes les seances..." -ForegroundColor Cyan
    
    # Trouver tous les dossiers seance*
    $SeancesFolders = Get-ChildItem -Path $CoursRoot -Directory -Filter "seance*" | 
                        Where-Object { $_.Name -match '^seance(\d+)$' } |
                        ForEach-Object { [int]$Matches[1] } |
                        Sort-Object
    
    if ($SeancesFolders.Count -eq 0) {
        Write-Host "ERREUR: Aucune seance trouvee dans $CoursRoot" -ForegroundColor Red
        exit 1
    }
    
    $SeancesACompiler = $SeancesFolders
    Write-Host "Seances trouvees : $($SeancesACompiler -join ', ')" -ForegroundColor Cyan
    
    # Inclure aussi l'integrale
    $CompilerIntegrale = $true
    Write-Host "L'integrale sera aussi compilee" -ForegroundColor Cyan
    
} elseif ($Seances -eq "last" -or $Seances -eq "dernier" -or $Seances -eq "derniere") {
    Write-Host "`nRecherche de la derniere seance..." -ForegroundColor Cyan
    
    # Trouver tous les dossiers seance* et prendre le numero le plus eleve
    $SeancesFolders = Get-ChildItem -Path $CoursRoot -Directory -Filter "seance*" | 
                        Where-Object { $_.Name -match '^seance(\d+)$' } |
                        ForEach-Object { [int]$Matches[1] } |
                        Sort-Object
    
    if ($SeancesFolders.Count -eq 0) {
        Write-Host "ERREUR: Aucune seance trouvee dans $CoursRoot" -ForegroundColor Red
        exit 1
    }
    
    # Prendre la derniere seance (numero le plus eleve)
    $DerniereSeance = $SeancesFolders[-1]
    $SeancesACompiler = @($DerniereSeance)
    Write-Host "Derniere seance trouvee : $DerniereSeance" -ForegroundColor Cyan
    
    # Inclure aussi l'integrale
    $CompilerIntegrale = $true
    Write-Host "L'integrale sera aussi compilee" -ForegroundColor Cyan
    
} else {
    # Parser les numeros de seances
    $SeancesACompiler = $Seances -split ',' | ForEach-Object { 
        $_.Trim() 
    } | Where-Object { 
        $_ -match '^\d+$' 
    } | ForEach-Object { 
        [int]$_ 
    } | Sort-Object -Unique
    
    if ($SeancesACompiler.Count -eq 0) {
        Write-Host "ERREUR: Aucun numero de seance valide specifie" -ForegroundColor Red
        Write-Host "Usage: .\compilation_drive.ps1 -Seances '1,3,5' ou -Seances 'all' ou -Seances 'last' ou -Seances 'integrale'" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "Seances a compiler : $($SeancesACompiler -join ', ')" -ForegroundColor Cyan
}

# Compiler l'integrale ou les seances
$Reussites = 0
$Echecs = 0

# Compiler les seances si necessaire
if ($SeancesACompiler.Count -gt 0) {
    foreach ($NumSeance in $SeancesACompiler) {
        if (Compile-Seance -NumSeance $NumSeance) {
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
    if ($CompilerIntegrale -and $SeancesACompiler.Count -gt 0) {
        Write-Host "`nSUCCES: Les seances et l'integrale ont ete compiles et copies avec succes !" -ForegroundColor Green
    } elseif ($CompilerIntegrale) {
        Write-Host "`nSUCCES: L'integrale du cours a ete compilee et copiee avec succes !" -ForegroundColor Green
    } else {
        Write-Host "`nSUCCES: Toutes les seances ont ete compiles et copies avec succes !" -ForegroundColor Green
    }
    
    exit 0
} else {
    exit 1
}
