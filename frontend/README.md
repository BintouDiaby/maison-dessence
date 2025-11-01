# Frontend - Maison d'essence

This is a minimal Next.js frontend for the Maison d'essence project.

Quick start (Windows PowerShell)

1. Open a terminal in `frontend/` and install dependencies:

```powershell
cd C:\Users\moije\Desktop\Maison d\'essence\frontend
npm install
```

2. Start the dev server:

```powershell
npm run dev
```

The frontend runs on port 3001 by default. It expects the backend to be available at `http://127.0.0.1:8000` by default. You can override the backend base URL by setting the env variable `BACKEND_URL` before starting the frontend (e.g. `BACKEND_URL=http://localhost:8000`).

Notes
- Uses Tailwind CSS. After `npm install`, Tailwind is configured automatically via `postcss.config.js` and `tailwind.config.js`.
- The homepage is intentionally visual (Hero) and uses product data from `/api/products/`.
- For Stripe checkout (test), the frontend will call the backend endpoint `/api/orders/stripe/create-payment-intent/` and then use Stripe.js client-side to confirm payment. You need to set `STRIPE_PUBLISHABLE_KEY` as an env var in your Next.js runtime (or embed it in a .env.local file).

If you want I can:
- add a polished cart drawer and client-side cart state (React Context)
- wire Stripe.js in the product page to perform a real test payment flow (requires `STRIPE_PUBLISHABLE_KEY`)

Tell me which of these you want next and I’ll implement it quickly.
