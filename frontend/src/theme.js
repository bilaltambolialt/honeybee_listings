import { useMediaQuery } from './useMediaQuery.js'

// Chart colours for each colour scheme. SVG attributes can't read CSS variables, so charts take
// their colours from here; the page itself uses the matching CSS variables in index.css.
const PALETTES = {
  light: {
    series: ['#2a78d6', '#eb6834', '#1baf7a'],
    text: '#0b0b0b',
    textMuted: '#52514e',
    grid: '#e4e3df',
    surface: '#fcfcfb',
  },
  dark: {
    series: ['#3987e5', '#d95926', '#199e70'],
    text: '#ffffff',
    textMuted: '#c3c2b7',
    grid: '#3a3a37',
    surface: '#1f1f1e',
  },
}

// Each source keeps the same colour everywhere (charts, legend, notebook), whatever its rank
const SOURCE_ORDER = ['OpenStreetMap', 'Geoapify', 'RBI Bank Directory']

export function sourceColor(palette, source) {
  const index = SOURCE_ORDER.indexOf(source)
  return palette.series[(index === -1 ? SOURCE_ORDER.length : index) % palette.series.length]
}

// Follows the operating system's light/dark setting and updates live when it changes
export function usePalette() {
  const isDark = useMediaQuery('(prefers-color-scheme: dark)')
  return isDark ? PALETTES.dark : PALETTES.light
}
