import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Recharts alone is ~500 kB minified (~180 kB gzipped); the single-page dashboard needs it on first load
    chunkSizeWarningLimit: 700,
  },
})
