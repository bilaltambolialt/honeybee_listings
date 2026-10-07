# Frontend: Business Listings Dashboard

React (Vite) dashboard that reads aggregated counts from the FastAPI backend, plus a listings explorer with filters, search, pagination and CSV download.

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
| `src/App.jsx` | Page layout, Overview / Browse listings tabs (active tab kept in the URL hash, e.g. `#listings`) |
| `src/components/ListingsView.jsx` | Filters, debounced search, paginated table (stacked cards on phones), CSV download link |
| `src/components/KpiCards.jsx` | Headline numbers from `/api/dashboard/summary` |
| `src/components/BarCountChart.jsx` | Bar chart (vertical or horizontal) with value labels and round-number axis |
| `src/components/SourceDonut.jsx` | Donut of listings per source with a labelled legend |
| `src/components/ChartCard.jsx` | Card wrapper with a Chart / Table toggle for every chart |
| `src/components/States.jsx` | Loading skeleton, error (with retry) and empty states |
| `src/theme.js`, `src/useMediaQuery.js` | Light/dark chart palette following the OS setting; responsive breakpoints |

## Design notes

- **Chart choice:** bars for cities and categories (13 categories are unreadable as pie slices); a donut only for the 3 sources.
- **Colour follows the entity:** each source keeps one colour in every chart and in the cleaning notebook. The palette is colour-blind-safe in both light and dark mode.
- **Accessible:** every chart can be switched to a table; legends carry labels and values, never colour alone; visible keyboard focus; reduced-motion respected.
- **Responsive:** 5 → 3 → 2 KPI columns; on phones the city chart turns horizontal so names stay readable.
