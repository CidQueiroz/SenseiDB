// senseidb-agent/frontend/src/components/Sidebar.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '@cidqueiroz/cdkteck-ui'; // Assuming ThemeProvider is from cdkteck-ui
import { api } from '../api'; // Your Axios instance for backend calls

interface SidebarProps {
  toggleApiModal: () => void;
  clearChat: () => void; // Function to clear chat messages in ChatWindow
}

const Sidebar: React.FC<SidebarProps> = ({ toggleApiModal, clearChat }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [newContext, setNewContext] = useState('');
  const [apiProvider, setApiProvider] = useState<string>(localStorage.getItem('api_provider') || 'groq');
  const [groqApiKey, setGroqApiKey] = useState<string>(localStorage.getItem('groq_api_key') || '');
  const [googleApiKey, setGoogleApiKey] = useState<string>(localStorage.getItem('google_api_key') || '');
  const [aiStatusText, setAiStatusText] = useState('Nível Gratuito');

  useEffect(() => {
    updateAIStatus();
  }, [apiProvider, groqApiKey, googleApiKey, user]); // Update status when these change

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
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      alert('Erro ao fazer logout.');
    }
  };

  return (
    <div className="sidebar">
      <a href="https://www.cdkteck.com.br" target="_blank" rel="noopener noreferrer">
        <h1>🧠 SenseiDB</h1>
      </a>
      <p className="subtitle">v5.0.5 - Mentor IA Adaptativo</p>

      <div className="user-info">
        <div className="email">{user?.email || 'Convidado'}</div>
        <div className="ai-status">
          <span className="status-dot"></span> {/* Placeholder for status dot */}
          <span>{aiStatusText}</span>
          <button id="theme-toggle-btn" title="Alternar tema" onClick={toggleTheme}>
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </div>

      <div className="section">
        <div className="section-title">Adicionar Contexto</div>
        <textarea
          value={newContext}
          onChange={(e) => setNewContext(e.target.value)}
          placeholder="Digite um insight sobre você..."
        ></textarea>
        <button className="btn btn-primary" onClick={handleSaveContext}>
          💾 Salvar Inteligência
        </button>
      </div>

      <div className="section">
        <div className="section-title">Configurações</div>
        <button className="btn btn-secondary" onClick={toggleApiModal}>
          🔧 Gerenciar API
        </button>
        <button className="btn btn-secondary" onClick={clearChat}>
          🗑️ Limpar Conversa
        </button>
      </div>

      <button className="btn btn-danger" onClick={handleLogout}>
        🚪 Sair
      </button>
    </div>
  );
};

export default Sidebar;