// vite.config.js
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  // La base debe coincidir con tu STATIC_URL en Django
  base: '/static/',
  build: {
    manifest: "manifest.json",
    outDir: resolve(__dirname, '../assets'),
    assetsDir: "django-assets",
    rollupOptions: {
      input: {
        // La ruta de tu archivo de entrada, relativa a la raíz del proyecto
        main: resolve('./src/main.js'),
      },
    },
  },
  server: {
    // El puerto en el que se ejecutará el servidor de Vite
    port: 5173,
    open: false,
    strictPort: true,
  },
});