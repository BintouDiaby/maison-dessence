# Maison d'essence - Backend

Backend Django pour la boutique MVP (produits, commandes, interactions, recommandations TF-IDF).

Quick start (local, avec Docker)

1) Build & start (Postgres + Django)

```powershell
# from project root (contains docker-compose.yml)
docker compose up --build -d
# follow logs
docker compose logs -f web
```

Le service `web` exécute : migrations -> `seed_products` -> `train_recommender` -> runserver

## Personalization (OpenAI)

The project contains a personalization chat where authenticated users can describe their tastes and get a suggested perfume recipe. This feature can optionally call OpenAI. To enable it:

- Set your OpenAI API key in the environment before starting the server:

  - PowerShell (temporary for session):

    ```powershell
    $env:OPENAI_API_KEY = 'sk-...'
    ```

  - Or set it in your system environment / docker-compose for production.

- Optional: set `OPENAI_MODEL` to choose another model (default: `gpt-3.5-turbo`).

- Controls and safety:
  - The server implements a simple per-user throttle and daily quota (defaults: 10s min interval, 200 calls/day). You can change these via Django settings:
    - `OPENAI_MIN_INTERVAL_SECS`
    - `OPENAI_DAILY_LIMIT`

- If `OPENAI_API_KEY` is not provided or if the call fails, the service falls back to a local mock assistant so the flow continues.

## CinetPay (dev)

There is a permissive webhook at `/api/orders/cinetpay/webhook/` intended for sandbox testing. In production you MUST verify signatures and validate amounts before marking orders paid.

## Environment variables

Add or export these variables (non-exhaustive list):

- `OPENAI_API_KEY` - (optional) OpenAI API key to enable personalization LLM.
- `OPENAI_MODEL` - (optional) model name to use (default `gpt-3.5-turbo`).
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` - Stripe credentials for payments.
- `CINETPAY_API_KEY`, `CINETPAY_SITE_ID`, `CINETPAY_BASE_URL` - CinetPay sandbox/production keys.

## Quick local run

1. Create and activate a venv and install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt
```

2. Run migrations and start server:

```powershell
.\venv\Scripts\python.exe backend\manage.py migrate
.\venv\Scripts\python.exe backend\manage.py runserver
```

3. Open http://127.0.0.1:8000/ for the static frontend.

2) Créer un superuser (pour admin et appel sécurisé de `/api/recommender/train/`)

```powershell
# entrer dans le conteneur web
docker compose exec web python manage.py createsuperuser
```

3) Endpoints utiles

- List products: GET /api/products/
- Product detail: GET /api/products/<id>/
- Similar (fallback): GET /api/products/<id>/similar/
- Recommender train (protected - admin): POST /api/recommender/train/  (requires admin JWT)
- Recommender demo page: GET /api/recommender/demo/

Auth

- Register: POST /api/auth/register/
- Token (JWT): POST /api/auth/token/  => returns access + refresh
- Token refresh: POST /api/auth/token/refresh/

Notes

- The recommender persists a trained model to `backend/recommendations/model.joblib` to speed up restarts.
- For dev without Docker, you can run locally from `backend/` with a venv:
  - python -m pip install -r requirements.txt
  - python manage.py migrate
  - python manage.py seed_products
  - python manage.py train_recommender
  - python manage.py runserver

If you want, je peux :
- protéger `/api/recommender/train/` via JWT-only (actuellement IsAdminUser),
- ajouter des endpoints de profil utilisateur (GET/PUT) et reset de mot de passe,
- scaffolder le frontend Next.js (login/register + list produits + page produit + recommandations).

