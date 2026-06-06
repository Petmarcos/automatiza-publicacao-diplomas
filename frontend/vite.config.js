import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './', // CRUCIAL para não dar tela branca
  build: {
    outDir: 'dist', // Onde o build será gerado
  }
})