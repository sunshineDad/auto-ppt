import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 12000,
    strictPort: true,
    cors: true,
    headers: {
      'X-Frame-Options': 'ALLOWALL'
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/types': resolve(__dirname, 'src/types'),
      '@/utils': resolve(__dirname, 'src/utils'),
      '@/components': resolve(__dirname, 'src/components'),
      '@/stores': resolve(__dirname, 'src/stores'),
      '@/api': resolve(__dirname, 'src/api')
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          fabric: ['fabric'],
          konva: ['konva', 'vue-konva'],
          charts: ['chart.js', 'vue-chartjs']
        }
      }
    }
  }
})