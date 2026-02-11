// senseidb-agent/frontend/src/api.ts
import axios from 'axios';
import { auth } from './context/AuthContext'; // Import auth instance directly

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

// Request interceptor para adicionar o token de autenticação
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser; // Get current Firebase user
  if (user) {
    const token = await user.getIdToken(); // Get ID token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});