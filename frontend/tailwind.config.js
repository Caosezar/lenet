/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        'mono-bg': '#121212',
        'mono-surface': '#1a1a1a',
        'mono-text': '#E0E0E0',
        'mono-secondary': '#B0B0B0',
        'mono-tertiary': '#888888',
        'mono-border': '#444444',
        'mono-dark': '#0a0a0a',
      },
      fontFamily: {
        jetbrains: ["'JetBrains Mono'", 'monospace'],
      },
    },
  },
  plugins: [],
}
