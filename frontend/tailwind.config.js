/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Subir un nivel para encontrar la carpeta 'templates'
    '../templates/**/*.html',
    // Buscar dentro de la carpeta 'src'
    './src/**/*.{js,jsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}