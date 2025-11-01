# Script PowerShell pour automatiser le démarrage du serveur Django (migrations, seed, runserver)
# Usage: Ouvrir PowerShell en mode normal (ou Administrateur si nécessaire) et exécuter :
#   cd "C:\Users\moije\Desktop\Maison d'essence\backend\scripts"
#   .\start_dev.ps1

Write-Host "==> Script: démarrage de l'API Django (migrations -> seed -> runserver)" -ForegroundColor Cyan

# Aller au dossier parent (backend)
# Le script se trouve dans backend\scripts, on remonte d'un niveau pour atteindre backend
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Split-Path -Parent $scriptDir
Set-Location $backendPath
Write-Host "Chemin courant : $(Get-Location)" -ForegroundColor Green

# Vérifier python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Erreur: 'python' introuvable dans le PATH. Veuillez activer votre environnement virtuel ou installer Python." -ForegroundColor Red
    Write-Host "Si vous avez un venv dans ./venv, activez-le avec : .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

# Optionnel : activer venv automatiquement s'il existe
$venvActivate = Join-Path $backendPath "venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activation automatique de l'environnement virtuel venv..." -ForegroundColor Yellow
    . $venvActivate
}

# Exécuter les migrations
Write-Host "Exécution des migrations..." -ForegroundColor Cyan
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "migrations a échoué (code $LASTEXITCODE). Copiez les messages d'erreur et partagez-les." -ForegroundColor Red
    exit 1
}

# Tenter d'exécuter la commande de seed si elle existe
$seedCmd = "python manage.py seed_products"
Write-Host "Tentative de seed des données (si la commande existe)..." -ForegroundColor Cyan
try {
    & python manage.py seed_products
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Seed exécuté avec succès (ou commande inexistante ignorée)." -ForegroundColor Green
    } else {
        Write-Host "La commande seed_products a retourné code $LASTEXITCODE (peut-être inexistante). Je continue." -ForegroundColor Yellow
    }
} catch {
    Write-Host "La commande seed_products n'a pas été trouvée ou a échoué. Je continue." -ForegroundColor Yellow
}

# Lancer le serveur en affichant l'URL
Write-Host "Lancement du serveur de développement Django sur 127.0.0.1:8000..." -ForegroundColor Cyan
Write-Host "Ouvrez un nouveau terminal pour tester l'API (Invoke-RestMethod...)." -ForegroundColor Cyan

# Démarrer le serveur et garder le terminal interactif (Ctrl+C pour arrêter)
python manage.py runserver

# Fin
Write-Host "Serveur arrêté." -ForegroundColor Gray
