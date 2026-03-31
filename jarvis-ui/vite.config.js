import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { nodePolyfills } from 'vite-plugin-node-polyfills';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    nodePolyfills({
      include: ['punycode', 'util', 'stream'],
    }),
  ],
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/index.jsx'),
      name: 'JarvisSDK',
      fileName: 'index',
      formats: ['es'], // IMPORTANTE: Solo ESM para evitar CJS/Require
    },
    rollupOptions: {
      external: ['react', 'react-dom', '@tanstack/react-query'],
      output: {
        // Esta opción es LA CLAVE para paquetes modernos:
        // Evita que el bundler cree estructuras complejas de "interop"
        interop: 'esModule', 
        format: 'es',
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM'
        }
      }
    },
    // DESACTIVA el procesamiento de CommonJS para las dependencias externas
    commonjsOptions: {
      transformMixedEsModules: false, 
    }
  }
});