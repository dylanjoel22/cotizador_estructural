import { defineConfig } from 'vite';

export default defineConfig({
  root: './',
  base: '/',
  build: {
    outDir: '../main_app/static/dist',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
  },
});