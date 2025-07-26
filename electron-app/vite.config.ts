import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  root: 'src/renderer',
  base: './',
  build: {
    outDir: '../../dist/renderer',
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, 'src/renderer/index.html'),
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/components': resolve(__dirname, 'src/renderer/components'),
      '@/pages': resolve(__dirname, 'src/renderer/pages'),
      '@/hooks': resolve(__dirname, 'src/renderer/hooks'),
      '@/utils': resolve(__dirname, 'src/renderer/utils'),
      '@/types': resolve(__dirname, 'src/shared/types'),
    },
  },
  server: {
    port: 5174,
    strictPort: true,
  },
});