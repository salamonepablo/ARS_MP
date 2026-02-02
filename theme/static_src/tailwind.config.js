/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Templates in theme app
    '../templates/**/*.html',
    // Templates in project root
    '../../templates/**/*.html',
    // Templates in Django apps
    '../../web/**/templates/**/*.html',
    // Inline templates in Python files (rare but possible)
    '../../web/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        // Custom colors for ARS_MP branding
        'ars-blue': {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        'csr': {
          light: '#bbf7d0',
          DEFAULT: '#22c55e',
          dark: '#15803d',
        },
        'toshiba': {
          light: '#fde68a',
          DEFAULT: '#eab308',
          dark: '#a16207',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
