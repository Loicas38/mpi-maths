# compile-and-copy-latex.ps1
param(
    [string]$TexFile = "chapitre11.tex",
    [string]$Destination = "C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\Maths\cours\test_compile\pdfs"
)

# Compilation LaTeX
Write-Host "Compilation de $TexFile..." -ForegroundColor Green
pdflatex $TexFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors de la compilation" -ForegroundColor Red
    exit 1
}

# Créer le dossier de destination si nécessaire
if (-not (Test-Path $Destination)) {
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    Write-Host "Dossier créé : $Destination" -ForegroundColor Yellow
}

# Copier le PDF (écrase s'il existe)
$PdfFile = $TexFile -replace '\.tex$', '.pdf'
$DestPath = Join-Path $Destination $PdfFile
Copy-Item $PdfFile -Destination $DestPath -Force
Write-Host "PDF copié vers : $DestPath" -ForegroundColor Green
Write-Host "Le fichier sera synchronisé automatiquement avec Google Drive" -ForegroundColor Cyan