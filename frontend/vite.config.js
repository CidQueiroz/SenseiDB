import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // Or any other available port
    open: true,
    watch: {
      ignored: [
        '!**/node_modules/@cidqueiroz/cdkteck-ui/dist/**'
      ]
    },
    fs: {
      allow: ['..'] 
    }
  },
  optimizeDeps: {
    exclude: ['@cidqueiroz/cdkteck-ui']
  },
  resolve: {
    preserveSymlinks: true 
  }
});