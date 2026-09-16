import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': resolve(import.meta.dirname, 'src'),
    },
  },
  build: {
    outDir: './static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:18420',
        changeOrigin: true,
      },
    },
  },
})
