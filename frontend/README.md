# Frontend: Business Listings Dashboard

React (Vite) dashboard that reads aggregated counts from the FastAPI backend.

## Run locally

```bash
npm install
npm run dev          # http://localhost:5173
```

The backend must be running (default `http://localhost:8000`). To point at another API, copy `.env.example` to `.env` and set `VITE_API_BASE_URL`.

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Development server with hot reload |
| `npm run build` | Production build into `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Lint with oxlint |

## Structure

| File | Role |
|---|---|
| `src/api.js` | API client; base URL from `VITE_API_BASE_URL` |
| `src/useDashboardData.js` | Loads all dashboard endpoints; exposes loading / error / ready state and `reload` |
| `src/App.jsx` | Page layout |
