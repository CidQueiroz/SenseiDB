// senseidb-agent/frontend/src/App.tsx
import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import { ThemeProvider, Header, Footer, CDKFavicon } from '@cidqueiroz/cdkteck-ui';
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
  const { user, isLoading, getIdToken } = useAuth(); // Get getIdToken from useAuth
  const location = useLocation();
  const [isContactModalOpen, setContactModalOpen] = useState(false);
  const [isMobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const toggleMobileSidebar = () => {
    setMobileSidebarOpen(!isMobileSidebarOpen);
  };

  const shouldShowHeaderFooter = location.pathname !== '/login' && location.pathname !== '/';

  // Effect to apply/remove 'logged-in' class to body
  useEffect(() => {
    if (!isLoading) {
      if (user) {
        document.body.classList.add('logged-in');
      } else {
        document.body.classList.remove('logged-in');
      }
    }
  }, [user, isLoading]); // Removed getIdToken from dependency array as it's not used here

  const ReactRouterLink = (props) => (
    <Link {...props} />
  );

  return (
    <ThemeProvider>
      <div className="app-container">
        {shouldShowHeaderFooter && (
          <Header 
            LinkComponent={ReactRouterLink}
            usePathname={() => location.pathname} // Correctly use the hook's value
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
        {/* TODO: Add ContactModal component and manage 'isContactModalOpen' state */}
      </div>
    </ThemeProvider>
  );
};

export default App;