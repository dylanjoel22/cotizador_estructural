import { defineConfig } from 'vite';

export default defineConfig({
  root: './',
  base: '/static/dist/',
  build: {
    outDir: '../main_app/static/dist',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
  },
});