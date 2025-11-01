<#
Lance le serveur Django dans un nouveau processus puis teste l'endpoint /api/products/1/similar/
Usage: depuis le dossier scripts : .\dev_run_and_test.ps1
#>

Write-Host "==> dev_run_and_test.ps1: démarrage du serveur en arrière-plan puis test" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $scriptDir '..'
Set-Location $backendPath
Write-Host "Chemin courant : $(Get-Location)" -ForegroundColor Green

# Activer venv si présent
$venvActivate = Join-Path $backendPath "venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activation de venv..." -ForegroundColor Yellow
    . $venvActivate
}

# Vérifier python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Erreur: 'python' introuvable dans le PATH. Activez votre venv ou installez Python." -ForegroundColor Red
    exit 1
}

Write-Host "Démarrage du serveur Django (même fenêtre, sortie affichée ici)..." -ForegroundColor Cyan
# Démarre le serveur sans ouvrir une nouvelle fenêtre; la sortie apparaîtra dans cette console
$proc = Start-Process -FilePath $python.Path -ArgumentList 'manage.py','runserver' -WorkingDirectory $backendPath -NoNewWindow -PassThru
Write-Host "Serveur lancé en arrière-plan (PID $($proc.Id)). Attendez quelques secondes que le serveur soit prêt..." -ForegroundColor Green

Start-Sleep -Seconds 3

$testUrl = 'http://127.0.0.1:8000/api/products/1/similar/'
Write-Host "Test de l'endpoint $testUrl" -ForegroundColor Cyan
try {
    $res = Invoke-RestMethod -Uri $testUrl -Method GET -TimeoutSec 10 -ErrorAction Stop
    Write-Host "OK: endpoint répondu." -ForegroundColor Green
    $res | ConvertTo-Json -Depth 4
} catch {
    Write-Host "Le test a échoué :" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "---" -ForegroundColor Gray
Write-Host "Serveur en cours d'exécution dans la fenêtre lancée (PID $($proc.Id))." -ForegroundColor Cyan
Write-Host "Appuyez sur Entrée ici pour arrêter le serveur (ou fermez la fenêtre du serveur manuellement)." -ForegroundColor Yellow
Read-Host

if ($proc -and -not $proc.HasExited) {
    Write-Host "Arrêt du serveur (PID $($proc.Id))..." -ForegroundColor Cyan
    Stop-Process -Id $proc.Id -Force
    Write-Host "Serveur arrêté." -ForegroundColor Green
} else {
    Write-Host "Le processus serveur est déjà arrêté." -ForegroundColor Yellow
}
