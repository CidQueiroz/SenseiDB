// senseidb-agent/frontend/src/firebase.ts
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyAAqeBcWQechliUfEFodQSJWTV3RtvOqGo",
    authDomain: "cdkteck-hub.firebaseapp.com",
    projectId: "cdkteck-hub",
    storageBucket: "cdkteck-hub.firebasestorage.app",
    messagingSenderId: "402043888600",
    appId: "1:402043888600:web:c29a42be4ab86a22d748ad",
    measurementId: "G-HTDZ2S5HFC"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const analytics = getAnalytics(app); // Initialize analytics

export { app, auth, analytics };
