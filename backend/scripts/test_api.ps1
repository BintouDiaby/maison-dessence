# Test script pour vérifier les endpoints simple API et Django
Write-Host "Test: simple API (http://127.0.0.1:8000/api/products/1/similar/)" -ForegroundColor Cyan

function Test-Endpoint($url) {
    try {
        $res = Invoke-RestMethod -Uri $url -Method GET -ErrorAction Stop
        Write-Host "OK: $url" -ForegroundColor Green
        $res | ConvertTo-Json -Depth 4
    } catch {
        Write-Host "ERROR calling $url" -ForegroundColor Red
        Write-Host $_.Exception.Message
    }
}

# Test simple API (standalone)
Test-Endpoint 'http://127.0.0.1:8000/api/products/1/similar/'

# Test explicit Django path (if Django used a different path, adjust accordingly)
Test-Endpoint 'http://127.0.0.1:8000/api/products/1/similar/'

Write-Host "Fin du test." -ForegroundColor Cyan
