// SenseiDB/frontend/src/App.tsx
import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import { ThemeProvider, Header, Footer } from '@cidqueiroz/cdkteck-ui';
import { useAuth } from './context/AuthContext.jsx';
import LoginPage from './pages/LoginPage.jsx';
import ChatPage from './pages/ChatPage';
import '@cidqueiroz/cdkteck-ui/global.css';

const PrivateRoute = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading authentication...</div>;
  }

  return user ? children : <Navigate to="/login" />;
};

const App = () => {
  const { user, isLoading } = useAuth();
  const location = useLocation();
  const [isContactModalOpen, setContactModalOpen] = useState(false);
  const [isMobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const toggleMobileSidebar = () => {
    setMobileSidebarOpen(!isMobileSidebarOpen);
  };

  // Exibimos Header e Footer apenas na tela de login
  const shouldShowHeaderFooter = location.pathname === '/login';

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        document.body.classList.add('logged-in');
      } else {
        document.body.classList.remove('logged-in');
      }
    }
  }, [user, isLoading]);

  const ReactRouterLink = (props) => (
    <Link {...props} />
  );

  return (
    <ThemeProvider>
      <div className="app-container">
        {shouldShowHeaderFooter && (
          <Header 
            LinkComponent={ReactRouterLink}
            usePathname={() => location.pathname}
          />
        )}
        <main className="flex-grow">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <ChatPage 
                    isMobileSidebarOpen={isMobileSidebarOpen}
                    toggleMobileSidebar={toggleMobileSidebar}
                  />
                </PrivateRoute>
              }
            />
          </Routes>
        </main>
        {shouldShowHeaderFooter && (
          <Footer 
            openContactModal={() => setContactModalOpen(true)}
            LinkComponent={ReactRouterLink}
          />
        )}
      </div>
    </ThemeProvider>
  );
};

export default App;
