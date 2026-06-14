import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/',
  plugins: [react()],
  optimizeDeps: {
    exclude: ['school-erp-ui-shared'],
  },
  server: {
    proxy: {
      '/api': {
        target: 'https://schoolmanagement-prod.up.railway.app',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
