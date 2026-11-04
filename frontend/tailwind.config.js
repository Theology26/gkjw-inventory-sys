/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          canvas: '#F6F5F0',
          surface: '#FFFFFF',
          subtle: '#ECEAE2',
          border: '#D6D3C9',
        },
        ink: {
          primary: '#141413',
          secondary: '#52514E',
          muted: '#85837E',
        },
        church: {
          terracotta: '#C84B31',
          'terracotta-hover': '#A83820',
          forest: '#1E3A2F',
        },
        status: {
          'good-bg': '#E6F4EA',
          'good-ink': '#137333',
          'warn-bg': '#FEF7E0',
          'warn-ink': '#B06000',
          'bad-bg': '#FCE8E6',
          'bad-ink': '#C5221F',
          'archive-bg': '#E8EAED',
          'archive-ink': '#3C4043',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        tactile: '2px 2px 0px #141413',
        'tactile-lg': '4px 4px 0px #141413',
      },
      borderRadius: {
        sm: '4px',
        md: '6px',
      }
    },
  },
  plugins: [],
}

