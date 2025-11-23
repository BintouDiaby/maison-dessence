# d:\Projets\maison-dessence\backend\scripts\test_unitaires.ps1
# Script pour lancer UNIQUEMENT les tests unitaires (17 tests)
# USAGE: .\scripts\test_unitaires.ps1
# RELEVANT FILES: backend/products/tests.py, backend/users/tests.py

Write-Host "`n=== TESTS UNITAIRES (17 tests) ===" -ForegroundColor Cyan
Write-Host "Tests des modèles et logique métier isolée`n" -ForegroundColor Yellow

# Tests unitaires Products (6 tests)
python manage.py test `
    products.tests.ProductModelTests.test_create_product_and_str `
    products.tests.ProductModelTests.test_image_display_url_prefers_image_field_or_image_url `
    products.tests.ProductModelTests.test_likes_and_wishlist `
    products.tests.ProductModelTests.test_product_out_of_stock `
    users.tests.UserModelTests `
    interactions.tests `
    recommendations.tests `
    --verbosity=2

Write-Host "`n✅ Tests unitaires terminés!" -ForegroundColor Green
