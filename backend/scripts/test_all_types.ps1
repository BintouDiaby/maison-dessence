# d:\Projets\maison-dessence\backend\scripts\test_all_types.ps1
# Script pour lancer tous les tests par catégorie
# USAGE: .\scripts\test_all_types.ps1
# RELEVANT FILES: backend/*/tests.py

Write-Host "`n╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     LANCEMENT DE TOUS LES TESTS PAR CATÉGORIE        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$totalStart = Get-Date

# ============================================
# 1. TESTS UNITAIRES (17 tests)
# ============================================
Write-Host "`n┌─────────────────────────────────────────┐" -ForegroundColor Green
Write-Host "│  1/3 - TESTS UNITAIRES (17 tests)      │" -ForegroundColor Green
Write-Host "└─────────────────────────────────────────┘" -ForegroundColor Green
Write-Host "Tests des modèles et logique métier isolée`n" -ForegroundColor Yellow

$unitStart = Get-Date
python manage.py test `
    products.tests.ProductModelTests.test_create_product_and_str `
    products.tests.ProductModelTests.test_image_display_url_prefers_image_field_or_image_url `
    products.tests.ProductModelTests.test_likes_and_wishlist `
    products.tests.ProductModelTests.test_product_out_of_stock `
    users.tests.UserModelTests `
    interactions.tests `
    recommendations.tests `
    --verbosity=2
$unitEnd = Get-Date
$unitDuration = ($unitEnd - $unitStart).TotalSeconds

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tests unitaires: OK ($([math]::Round($unitDuration, 2))s)" -ForegroundColor Green
} else {
    Write-Host "❌ Tests unitaires: ÉCHEC" -ForegroundColor Red
    exit 1
}

# ============================================
# 2. TESTS FONCTIONNELS / API (4 tests)
# ============================================
Write-Host "`n┌─────────────────────────────────────────┐" -ForegroundColor Green
Write-Host "│  2/3 - TESTS FONCTIONNELS (4 tests)    │" -ForegroundColor Green
Write-Host "└─────────────────────────────────────────┘" -ForegroundColor Green
Write-Host "Tests des endpoints API REST`n" -ForegroundColor Yellow

$funcStart = Get-Date
python manage.py test `
    products.tests.ProductModelTests.test_search_products_by_name `
    products.tests.ProductModelTests.test_vendor_cannot_edit_other_products `
    products.tests.ProductAPITests `
    users.tests.UserAPITests `
    --verbosity=2
$funcEnd = Get-Date
$funcDuration = ($funcEnd - $funcStart).TotalSeconds

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tests fonctionnels: OK ($([math]::Round($funcDuration, 2))s)" -ForegroundColor Green
} else {
    Write-Host "❌ Tests fonctionnels: ÉCHEC" -ForegroundColor Red
    exit 1
}

# ============================================
# 3. TESTS D'INTÉGRATION (1 test)
# ============================================
Write-Host "`n┌─────────────────────────────────────────┐" -ForegroundColor Green
Write-Host "│  3/3 - TESTS D'INTÉGRATION (1 test)    │" -ForegroundColor Green
Write-Host "└─────────────────────────────────────────┘" -ForegroundColor Green
Write-Host "Tests de l'interaction entre modules`n" -ForegroundColor Yellow

$integStart = Get-Date
python manage.py test orders.tests --verbosity=2
$integEnd = Get-Date
$integDuration = ($integEnd - $integStart).TotalSeconds

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tests d'intégration: OK ($([math]::Round($integDuration, 2))s)" -ForegroundColor Green
} else {
    Write-Host "❌ Tests d'intégration: ÉCHEC" -ForegroundColor Red
    exit 1
}

# ============================================
# RÉSUMÉ FINAL
# ============================================
$totalEnd = Get-Date
$totalDuration = ($totalEnd - $totalStart).TotalSeconds

Write-Host "`n╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  RÉSUMÉ FINAL                         ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "✅ Tests unitaires:      17 tests - $([math]::Round($unitDuration, 2))s" -ForegroundColor Green
Write-Host "✅ Tests fonctionnels:    4 tests - $([math]::Round($funcDuration, 2))s" -ForegroundColor Green
Write-Host "✅ Tests d'intégration:   1 test  - $([math]::Round($integDuration, 2))s" -ForegroundColor Green
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 TOTAL: 22/22 tests réussis en $([math]::Round($totalDuration, 2))s" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

Write-Host "🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!" -ForegroundColor Green
