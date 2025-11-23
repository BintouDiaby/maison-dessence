# d:\Projets\maison-dessence\backend\scripts\test_integration.ps1
# Script pour lancer UNIQUEMENT les tests d'intégration (1 test)
# USAGE: .\scripts\test_integration.ps1
# RELEVANT FILES: backend/orders/tests.py

Write-Host "`n=== TESTS D'INTÉGRATION (1 test) ===" -ForegroundColor Cyan
Write-Host "Tests de l'interaction entre modules (Cart + Products + Orders)`n" -ForegroundColor Yellow

# Test calcul panier (TC22)
python manage.py test orders.tests --verbosity=2

Write-Host "`n✅ Tests d'intégration terminés!" -ForegroundColor Green
