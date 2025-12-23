import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LoginPage as CdkLoginPage } from '@cidqueiroz/cdkteck-ui';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();

  const handleLoginSubmit = async ({ email, password }) => {
    const success = await login(email, password);
    if (success) {
      navigate('/dashboard'); // Or wherever you want to redirect after login
    }
  };

  const handleRegisterSubmit = ({ email, password }) => {
    // TODO: Implement registration logic in AuthContext
    alert(`Registro não implementado. E-mail: ${email}`);
  };

  const handleGoogleLogin = () => {
    // TODO: Implement Google login logic in AuthContext
    alert('Login com Google não implementado.');
  };

  return (
    <div className="bg-vitrine">
      <CdkLoginPage
        onLogin={handleLoginSubmit}
        onRegister={handleRegisterSubmit}
        onGoogleLogin={() => console.log('Google')}
        onFacebookLogin={() => console.log('Face')} 
        onLinkedInLogin={() => console.log('Linked')}
        isLoading={isLoading}
        error={error}
        appName="Sensei"
      />
    </div>

  );
};

export default LoginPage;