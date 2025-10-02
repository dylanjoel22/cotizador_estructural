/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // La ruta de tu backend
    "../main_app/templates/**/*.html",
    // La ruta de tu archivo de desarrollo
    "./index.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};