/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './privacy.html', './terms.html'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'Noto Sans SC', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      colors: {
        apple: {
          bg: '#000000',
          card: '#1d1d1f',
          text: '#f5f5f7',
          gray: '#86868b',
          blue: '#2997ff',
          blueHover: '#0071e3',
        },
      },
      animation: {
        'fade-in-up': 'fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: 0, transform: 'translateY(30px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
