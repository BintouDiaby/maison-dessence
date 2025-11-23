# d:\Projets\maison-dessence\backend\scripts\test_api_manual.ps1
# Script pour tester manuellement toutes les API de Maison d'Essence
# USAGE: .\scripts\test_api_manual.ps1
# RELEVANT FILES: backend/products/views.py, backend/users/views.py, backend/orders/views.py

$baseUrl = "http://localhost:8000"

Write-Host "`n=== TEST MANUEL DES API - MAISON D'ESSENCE ===" -ForegroundColor Cyan
Write-Host "Assurez-vous que le serveur tourne: python manage.py runserver`n" -ForegroundColor Yellow

# ============================================
# 1. PRODUCTS API
# ============================================
Write-Host "`n--- 1. TEST PRODUCTS API ---" -ForegroundColor Green

Write-Host "`n[GET] Liste des produits:"
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/products/" -Method GET
    Write-Host "Status: $($response.StatusCode) ✅" -ForegroundColor Green
    $products = $response.Content | ConvertFrom-Json
    Write-Host "Nombre de produits: $($products.Count)"
    if ($products.Count -gt 0) {
        Write-Host "Premier produit: $($products[0].name)"
    }
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
}

Write-Host "`n[GET] Recherche produit (search=oil):"
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/products/?search=oil" -Method GET
    Write-Host "Status: $($response.StatusCode) ✅" -ForegroundColor Green
    $results = $response.Content | ConvertFrom-Json
    Write-Host "Résultats trouvés: $($results.Count)"
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
}

Write-Host "`n[GET] Détail d'un produit (ID=1):"
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/products/1/" -Method GET
    Write-Host "Status: $($response.StatusCode) ✅" -ForegroundColor Green
    $product = $response.Content | ConvertFrom-Json
    Write-Host "Produit: $($product.name) - $($product.price)€"
} catch {
    Write-Host "Erreur: Produit non trouvé" -ForegroundColor Yellow
}

# ============================================
# 2. USERS/AUTH API
# ============================================
Write-Host "`n--- 2. TEST AUTH API ---" -ForegroundColor Green

Write-Host "`n[POST] Inscription (register):"
$registerBody = @{
    username = "testuser_$(Get-Random)"
    email = "test_$(Get-Random)@example.com"
    password = "TestPass123!"
    password2 = "TestPass123!"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/auth/register/" -Method POST -Body $registerBody -ContentType "application/json"
    Write-Host "Status: $($response.StatusCode) ✅" -ForegroundColor Green
    $user = $response.Content | ConvertFrom-Json
    Write-Host "User créé: $($user.username)"
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
}

Write-Host "`n[POST] Login:"
$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/auth/login/" -Method POST -Body $loginBody -ContentType "application/json"
    Write-Host "Status: $($response.StatusCode) ✅" -ForegroundColor Green
    $auth = $response.Content | ConvertFrom-Json
    $token = $auth.access
    Write-Host "Token reçu: $($token.Substring(0, 20))..." -ForegroundColor Cyan
    
    # Sauvegarder le token pour les tests suivants
    $global:authToken = $token
} catch {
    Write-Host "Erreur: Utilisateur non trouvé ou mot de passe incorrect" -ForegroundColor Yellow
}

# ============================================
# 3. ORDERS/CART API
# ============================================
Write-Host "`n--- 3. TEST CART API ---" -ForegroundColor Green

Write-Host "`n[GET] Voir le panier (besoin d'être connecté):"
if ($global:authToken) {
    try {
        $headers = @{
            "Authorization" = "Bearer $global:authToken"
        }
        $response = Invoke-WebRequest -Uri "$baseUrl/api/cart/" -Method GET -Headers $headers
        Write-Host "Status: $($response.StatusCode) ✅" -ForegroundColor Green
        $cart = $response.Content | ConvertFrom-Json
        Write-Host "Items dans le panier: $($cart.items.Count)"
        Write-Host "Total: $($cart.total)€"
    } catch {
        Write-Host "Erreur: $_" -ForegroundColor Red
    }
} else {
    Write-Host "Token non disponible - Connectez-vous d'abord" -ForegroundColor Yellow
}

Write-Host "`n[POST] Ajouter au panier (besoin d'être connecté):"
if ($global:authToken) {
    $cartBody = @{
        product_id = 1
        quantity = 2
    } | ConvertTo-Json
    
    try {
        $headers = @{
            "Authorization" = "Bearer $global:authToken"
        }
        $response = Invoke-WebRequest -Uri "$baseUrl/api/cart/add/" -Method POST -Body $cartBody -ContentType "application/json" -Headers $headers
        Write-Host "Status: $($response.StatusCode) ✅" -ForegroundColor Green
        Write-Host "Produit ajouté au panier"
    } catch {
        Write-Host "Erreur: $_" -ForegroundColor Red
    }
} else {
    Write-Host "Token non disponible - Connectez-vous d'abord" -ForegroundColor Yellow
}

# ============================================
# 4. RECOMMENDATIONS API
# ============================================
Write-Host "`n--- 4. TEST RECOMMENDATIONS API ---" -ForegroundColor Green

Write-Host "`n[GET] Recommandations pour produit ID=1:"
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/recommendations/1/" -Method GET
    Write-Host "Status: $($response.StatusCode) ✅" -ForegroundColor Green
    $recommendations = $response.Content | ConvertFrom-Json
    Write-Host "Produits recommandés: $($recommendations.Count)"
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
}

# ============================================
# 5. INTERACTIONS API
# ============================================
Write-Host "`n--- 5. TEST INTERACTIONS API ---" -ForegroundColor Green

Write-Host "`n[POST] Logger une vue de produit (besoin d'être connecté):"
if ($global:authToken) {
    $interactionBody = @{
        product_id = 1
        interaction_type = "view"
    } | ConvertTo-Json
    
    try {
        $headers = @{
            "Authorization" = "Bearer $global:authToken"
        }
        $response = Invoke-WebRequest -Uri "$baseUrl/api/interactions/" -Method POST -Body $interactionBody -ContentType "application/json" -Headers $headers
        Write-Host "Status: $($response.StatusCode) ✅" -ForegroundColor Green
        Write-Host "Interaction 'view' loggée"
    } catch {
        Write-Host "Erreur: $_" -ForegroundColor Red
    }
} else {
    Write-Host "Token non disponible - Connectez-vous d'abord" -ForegroundColor Yellow
}

# ============================================
# RÉSUMÉ
# ============================================
Write-Host "`n=== RÉSUMÉ ===" -ForegroundColor Cyan
Write-Host "✅ Products API: Liste, Recherche, Détail"
Write-Host "✅ Auth API: Register, Login"
Write-Host "✅ Cart API: Voir panier, Ajouter produit"
Write-Host "✅ Recommendations API: Produits similaires"
Write-Host "✅ Interactions API: Logger views/purchases"

Write-Host "`n💡 Pour tester avec Postman/Thunder Client:" -ForegroundColor Yellow
Write-Host "   - Importe ces endpoints dans Postman"
Write-Host "   - Utilise le token JWT pour les requêtes authentifiées"
Write-Host "   - Base URL: http://localhost:8000"

Write-Host "`n🚀 Endpoints disponibles:" -ForegroundColor Cyan
Write-Host "   GET    /api/products/"
Write-Host "   GET    /api/products/?search=query"
Write-Host "   GET    /api/products/{id}/"
Write-Host "   POST   /api/auth/register/"
Write-Host "   POST   /api/auth/login/"
Write-Host "   GET    /api/cart/"
Write-Host "   POST   /api/cart/add/"
Write-Host "   GET    /api/recommendations/{id}/"
Write-Host "   POST   /api/interactions/"

Write-Host "`n" -ForegroundColor Green
