// SenseiDB/frontend/src/firebase.ts
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

// Configuração oficial do projeto CDKTECK-HUB (Fortaleza Sustentável)
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyAAqeBcWQechliUfEFodQSJWTV3RtvOqGo",
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "cdkteck-hub.firebaseapp.com",
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "cdkteck-hub",
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "cdkteck-hub.firebasestorage.app",
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "402043888600",
    appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:402043888600:web:c29a42be4ab86a22d748ad",
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-HTDZ2S5HFC"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const analytics = getAnalytics(app);

export { app, auth, analytics };
