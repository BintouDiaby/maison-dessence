/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          light: '#F6EFF6',
          DEFAULT: '#2B2A4A',
          accent: '#E5A4A4'
        }
      }
    }
  },
  plugins: []
}
