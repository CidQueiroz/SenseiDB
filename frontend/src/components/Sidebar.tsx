// senseidb-agent/frontend/src/components/Sidebar.tsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '@cidqueiroz/cdkteck-ui';
import { api } from '../api'; // Import your API instance

interface SidebarProps {
  toggleApiModal: () => void;
  clearChat: () => void;
  isCollapsed: boolean; // New prop
  toggleCollapsed: () => void; // New prop
}

const Sidebar: React.FC<SidebarProps> = ({ toggleApiModal, clearChat, isCollapsed, toggleCollapsed }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme(); // Use the theme context
  const [newContext, setNewContext] = useState('');
  const [savingContext, setSavingContext] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const handleSaveContext = async () => {
    if (!newContext.trim() || !user) return;

    setSavingContext(true);
    setSaveError(null);
    try {
      await api.post('/contextos/', { text: newContext });
      setNewContext('');
      alert('✅ Contexto salvo com sucesso!'); // Revisit with a proper alert system
    } catch (error) {
      console.error('Erro ao salvar contexto:', error);
      setSaveError('❌ Erro ao salvar contexto. Verifique sua conexão e autenticação.');
    } finally {
      setSavingContext(false);
    }
  };

  const logoImage = theme === 'dark' 
  ? '/assets/logo_header.png' 
  : '/assets/logo_header.png';

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      {/* Header */}
      <div className="sidebar-header">
        <div className="cabecalho-logo">
          <img 
            src={logoImage} 
            alt="CDK TECK Logo"
            width={40} 
            height={40} 
          />
        </div>
        {!isCollapsed && (
          <div className="sidebar-title">
            <h1>SenseiDB</h1>
            <span>v5.0.5 - Mentor IA Adaptativo</span>
          </div>
        )}
      </div>

      {/* Collapse Toggle Button - Moved here */}
      <button className="collapse-toggle" onClick={toggleCollapsed}>
        <i className={`fas ${isCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'}`}></i>
      </button>

      {/* User Info */}
      {user && (
        <div className="user-info">
          <div className="user-email">
            <i className="fas fa-envelope"></i>
            {!isCollapsed && <span>{user.email}</span>}
          </div>
          <div className="user-level">
            <span style={{ color: '#06f0a8' }}>●</span>
            {!isCollapsed && <span>Nível Gratuito</span>}
            <button id="desktop-theme-toggle-btn" className="theme-toggle" onClick={toggleTheme}>
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
          </div>
        </div>
      )}

      {/* Context Section */}
      <div className="context-section">
        {!isCollapsed && <div className="context-label">Adicionar Contexto</div>}
        <textarea
          className="context-input"
          placeholder="Digite um insight sobre o que você precisa..."
          value={newContext}
          onChange={(e) => setNewContext(e.target.value)}
          disabled={savingContext}
          style={{ display: isCollapsed ? 'none' : 'block' }}
        ></textarea>
        {saveError && !isCollapsed && <p style={{ color: 'red', fontSize: '0.8rem', marginTop: '5px' }}>{saveError}</p>}
      </div>

      {/* Buttons */}
      <div className="sidebar-buttons">
        <button className="sidebar-btn btn-save" onClick={handleSaveContext} disabled={savingContext}>
          <i className="fas fa-save"></i>
          {!isCollapsed && <span>{savingContext ? 'Salvando...' : 'Salvar Inteligência'}</span>}
        </button>

        <button className="sidebar-btn btn-config" onClick={toggleApiModal}>
          <i className="fas fa-cog"></i>
          {!isCollapsed && <span>Gerenciar API</span>}
        </button>

        <button className="sidebar-btn btn-clear" onClick={clearChat}>
          <i className="fas fa-broom"></i>
          {!isCollapsed && <span>Limpar Conversa</span>}
        </button>

        <button className="sidebar-btn btn-exit" onClick={logout}>
          <i className="fas fa-sign-out-alt"></i>
          {!isCollapsed && <span>Sair</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;