// senseidb-agent/frontend/src/components/MobileSidebar.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '@cidqueiroz/cdkteck-ui';
import { api } from '../api';

interface MobileSidebarProps {
  isOpen: boolean;
  toggleSidebar: () => void;
  toggleApiModal: () => void; // Passed from ChatPage
  clearChat: () => void;     // Passed from ChatPage
}

const MobileSidebar: React.FC<MobileSidebarProps> = ({ isOpen, toggleSidebar, toggleApiModal, clearChat }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [newContext, setNewContext] = useState('');
  const [apiProvider, setApiProvider] = useState<string>(localStorage.getItem('api_provider') || 'groq');
  const [groqApiKey, setGroqApiKey] = useState<string>(localStorage.getItem('groq_api_key') || '');
  const [googleApiKey, setGoogleApiKey] = useState<string>(localStorage.getItem('google_api_key') || '');
  const [aiStatusText, setAiStatusText] = useState('Nível Gratuito');

  useEffect(() => {
    updateAIStatus();
  }, [apiProvider, groqApiKey, googleApiKey, user]);

  const updateAIStatus = (usedAi?: string) => {
    let statusText = 'Nível Gratuito';
    if (usedAi) {
      statusText = usedAi === 'groq' ? '🚀 Groq AI Ativo' : '🌐 Google AI Ativo';
    } else if (apiProvider === 'groq' && groqApiKey) {
      statusText = '🚀 Groq AI Ativo';
    } else if (apiProvider === 'google' && googleApiKey) {
      statusText = '🌐 Google AI Ativo';
    }
    setAiStatusText(statusText);
  };

  const handleSaveContext = async () => {
    if (!newContext.trim() || !user) return;

    try {
      await api.post('/contexto/', {
        user_id: user.uid,
        contexto: newContext,
      });
      setNewContext('');
      alert('✅ Contexto salvo com sucesso!'); // Revisit with a proper alert system
    } catch (error) {
      console.error('Erro ao salvar contexto:', error);
      alert('❌ Erro ao salvar contexto'); // Revisit with a proper alert system
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      toggleSidebar(); // Close sidebar on logout
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      alert('Erro ao fazer logout.');
    }
  };

  return (
    <>
      <div className={`mobile-sidebar ${isOpen ? 'open' : ''}`}>
        <a href="https://www.cdkteck.com.br" target="_blank" rel="noopener noreferrer">
          <h1>🧠 SenseiDB</h1>
        </a>
        <p className="subtitle">v5.0.5 - Mentor IA Adaptativo</p>

        <div className="user-info">
          <div className="email">{user?.email || 'Convidado'}</div>
          <div className="ai-status">
            <span>{aiStatusText}</span>
            <button id="mobile-theme-toggle-btn" title="Alternar tema" onClick={toggleTheme}>
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
          </div>
        </div>

        <div className="section">
          <div className="section-title">Adicionar Contexto</div>
          <textarea
            id="mobileNewContext"
            value={newContext}
            onChange={(e) => setNewContext(e.target.value)}
            placeholder="Digite um insight..."
          ></textarea>
          <button className="btn btn-primary" onClick={handleSaveContext} style={{ marginTop: '10px' }}>
            💾 Salvar
          </button>
        </div>

        <div className="section">
          <div className="section-title">Configurações</div>
          <button className="btn btn-secondary" onClick={toggleApiModal}>
            🔧 Gerenciar API
          </button>
          <button className="btn btn-secondary" onClick={clearChat} style={{ marginTop: '10px' }}>
            🗑️ Limpar Conversa
          </button>
        </div>

        <button className="btn btn-danger" onClick={handleLogout} style={{ marginTop: 'auto' }}>
          🚪 Sair
        </button>
      </div>
    </>
  );
};

export default MobileSidebar;
