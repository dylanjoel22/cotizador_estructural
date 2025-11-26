import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: '/static/', 
  build: {
    manifest: "manifest.json",
    // IMPORTANTE: Guardamos esto dentro de la estructura de Django
    outDir: resolve(__dirname, '../assets/django-assets'), 
    emptyOutDir: true, 
    rollupOptions: {
      input: {
        main: resolve(__dirname, './src/main.js'), 
      },
    },
  },
});