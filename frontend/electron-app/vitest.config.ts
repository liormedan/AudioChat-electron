
import { defineConfig } from 'vitest/config';
import path from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.ts',
    // Explicitly configure esbuild for JSX in test files
    // This ensures .ts files are treated as .tsx for JSX parsing
    deps: {
      optimizer: {
        web: {
          include: ['@/components/chat/input-area'],
        },
      },
    },
    transformMode: {
      web: [/\.[jt]sx$/],
    },
    // Add esbuild options to explicitly set loader for .ts files
    esbuild: {
      loader: 'tsx',
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src/renderer'),
    },
  },
});
