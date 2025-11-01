# Lance le serveur simple standalone (pour tester la connectivité sans Django)
Write-Host "Lancement du simple API (port 8000) ..." -ForegroundColor Cyan
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)\..
python simple_api.py
