import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Isto força o Vite a usar caminhos relativos para TUDO (JS e CSS)
  base: './', 
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  }
})