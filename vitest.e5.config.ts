import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/unit/**/*.test.ts', 'src/e5/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/e5/**/*.ts'],
    },
  },
  resolve: {
    alias: {
      '@e5': path.resolve(__dirname, './src/e5'),
    },
  },
});
