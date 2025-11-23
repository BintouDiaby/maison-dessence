# d:\Projets\maison-dessence\backend\scripts\test_fonctionnels.ps1
# Script pour lancer UNIQUEMENT les tests fonctionnels/API (4 tests)
# USAGE: .\scripts\test_fonctionnels.ps1
# RELEVANT FILES: backend/products/tests.py, backend/users/tests.py

Write-Host "`n=== TESTS FONCTIONNELS / API (4 tests) ===" -ForegroundColor Cyan
Write-Host "Tests des endpoints API REST`n" -ForegroundColor Yellow

# Tests API Products (3 tests) + Users (1 test)
python manage.py test `
    products.tests.ProductModelTests.test_search_products_by_name `
    products.tests.ProductModelTests.test_vendor_cannot_edit_other_products `
    products.tests.ProductAPITests `
    users.tests.UserAPITests `
    --verbosity=2

Write-Host "`n✅ Tests fonctionnels terminés!" -ForegroundColor Green
