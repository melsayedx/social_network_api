import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Check if SSL certs exist
const certPath = path.resolve(__dirname, '../certs/localhost.crt')
const keyPath = path.resolve(__dirname, '../certs/localhost.key')
const hasSSL = fs.existsSync(certPath) && fs.existsSync(keyPath)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // Enable HTTPS if certs exist
    ...(hasSSL && {
      https: {
        cert: fs.readFileSync(certPath),
        key: fs.readFileSync(keyPath),
      },
    }),
    // Proxy API requests to Django backend
    proxy: {
      '/api': {
        target: hasSSL ? 'https://localhost:8000' : 'http://localhost:8000',
        changeOrigin: true,
        secure: false, // Accept self-signed certs
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
