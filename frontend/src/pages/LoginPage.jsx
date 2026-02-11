// GestaoRPD/frontend/src/pages/LoginPage.jsx
import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LoginPage as CdkLoginPage } from '@cidqueiroz/cdkteck-ui';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const { login, register, loginWithGoogle, loginWithGitHub, loginWithFace, isLoading, error } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async ({ email, password }) => {
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      // Error is handled in AuthContext
    }
  };

  const handleRegister = async ({ email, password }) => {
    try {
      await register(email, password);
      navigate('/'); // Redirect after successful registration
    } catch (err) {
      // Error is handled in AuthContext
    }
  };
  
  const handleGoogleLogin = async () => {
    try {
      await loginWithGoogle();
      navigate('/'); // Redirect after successful Google login
    } catch (err) {
      // Error is handled in AuthContext
    }
  };
  
  const handleFaceLogin = async () => {
    try {
      await loginWithFace();
      navigate('/'); // Redirect after successful Google login
    } catch (err) {
      // Error is handled in AuthContext
    }
  };

  const handleGitHubLogin = async () => {
    try {
      await loginWithGitHub();
      navigate('/');
    } catch (err) {
    }
  };

  return (
    <CdkLoginPage
      onLogin={handleLogin}
      onRegister={handleRegister}
      onGoogleLogin={handleGoogleLogin}
      onFacebookLogin={handleFaceLogin}
      onGitHubLogin={handleGitHubLogin}
      isLoading={isLoading}
      error={error}
      appName="SenseiDB"
    />
  );
};

export default LoginPage;
