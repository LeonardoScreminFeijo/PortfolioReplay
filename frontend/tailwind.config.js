/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI Variable Text"',
          '"Segoe UI"',
          'system-ui',
          'sans-serif',
        ],
        mono: [
          'ui-monospace',
          '"Cascadia Code"',
          '"Fira Code"',
          '"Roboto Mono"',
          'monospace',
        ],
      },
    },
  },
  plugins: [],
}

