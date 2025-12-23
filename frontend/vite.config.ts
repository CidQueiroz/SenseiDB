import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ command }) => {
  const isDevelopment = command === 'serve';

  return {
    plugins: [react()],
    resolve: {
      alias: isDevelopment ? {
        '@cidqueiroz/cdkteck-ui': path.resolve(__dirname, '../../cdkteck-ui/src')
      } : {}
    },
    server: {
      fs: {
        // Allow serving files from one level up to the project root
        allow: ['../..']
      }
    },
    optimizeDeps: {
      exclude: ['@cidqueiroz/cdkteck-ui']
    }
  }
});
