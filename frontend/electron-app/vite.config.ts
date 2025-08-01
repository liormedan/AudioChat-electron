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
      '@': resolve(__dirname, 'src/renderer'),
      '@/components': resolve(__dirname, 'src/renderer/components'),
      '@/pages': resolve(__dirname, 'src/renderer/pages'),
      '@/hooks': resolve(__dirname, 'src/renderer/hooks'),
      '@/lib': resolve(__dirname, 'src/renderer/lib'),
      '@/utils': resolve(__dirname, 'src/renderer/utils'),
      '@/types': resolve(__dirname, 'src/shared/types'),
      '@/renderer': resolve(__dirname, 'src/renderer'),
    },
  },
  server: {
    port: 5176,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});