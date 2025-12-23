// senseidb-agent/frontend/src/api.ts
import axios from 'axios';

// Define a URL do backend baseando-se no ambiente (desenvolvimento local vs. produção)
const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';
export const BACKEND_URL = isLocal 
    ? 'http://localhost:8000/api' 
    : 'https://senseidb-agent-402043888600.southamerica-east1.run.app/api';

export const api = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
