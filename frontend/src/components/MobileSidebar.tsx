// senseidb-agent/frontend/src/components/MobileSidebar.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '@cidqueiroz/cdkteck-ui';
import { api } from '../api';
import '../style_sensei.css'; 

interface MobileSidebarProps {
  isOpen: boolean;
  toggleSidebar: () => void;
  toggleApiModal: () => void;
  clearChat: () => void;
}

const MobileSidebar: React.FC<MobileSidebarProps> = ({ isOpen, toggleSidebar, toggleApiModal, clearChat }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [newContext, setNewContext] = useState('');
  const [savingContext, setSavingContext] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const [aiStatusText, setAiStatusText] = useState('Nível Gratuito'); // Keep for now, but its logic might be simplified later

  // This useEffect now just sets a generic status. Actual API provider status will come from backend checks.
  useEffect(() => {
    // This part can be refined later with a backend call to check active provider
    setAiStatusText(user ? 'Conectado' : 'Desconectado');
  }, [user]);

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

  const handleLogout = async () => {
    try {
      await logout();
      toggleSidebar();
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <aside className={`mobile-sidebar ${isOpen ? 'open' : ''}`}>
      {/* 1. Header Idêntico ao Desktop */}
      <div className="sidebar-header">
        <div className="sidebar-logo">🧠</div>
        <div className="sidebar-title">
          <h1>SenseiDB</h1>
          <span>v5.0.5 - Mentor IA</span>
        </div>
        {/* Botão X para fechar no mobile (Opcional, mas útil) */}
        <button 
            onClick={toggleSidebar} 
            style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'var(--cor-texto-primario)', fontSize: '1.5rem' }}
        >
            ×
        </button>
      </div>

      {/* 2. User Info Idêntico ao Desktop */}
      <div className="user-info">
        <div className="user-email">
          <i className="fas fa-envelope"></i>
          <span>{user?.email || 'Convidado'}</span>
        </div>
        <div className="user-level" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
             <span style={{ color: '#06f0a8' }}>●</span>
             <span>{aiStatusText}</span>
          </div>
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </div>

      {/* 3. Context Section com classes CSS corretas */}
      <div className="context-section">
        <div className="context-label">Adicionar Contexto</div>
        <textarea
          className="context-input"
          value={newContext}
          onChange={(e) => setNewContext(e.target.value)}
          placeholder="Digite um insight..."
          disabled={savingContext}
        ></textarea>
        {saveError && <p style={{ color: 'red', fontSize: '0.8rem', marginTop: '5px' }}>{saveError}</p>}
      </div>

      {/* 4. Botões usando as classes .sidebar-btn do style_sensei.css */}
      <div className="sidebar-buttons">
        <button className="sidebar-btn btn-save" onClick={handleSaveContext} disabled={savingContext}>
          <i className="fas fa-save"></i>
          <span>{savingContext ? 'Salvando...' : 'Salvar Inteligência'}</span>
        </button>

        <button className="sidebar-btn btn-config" onClick={() => { toggleApiModal(); toggleSidebar(); }}>
          <i className="fas fa-cog"></i>
          <span>Gerenciar API</span>
        </button>

        <button className="sidebar-btn btn-clear" onClick={() => { clearChat(); toggleSidebar(); }}>
          <i className="fas fa-broom"></i>
          <span>Limpar Conversa</span>
        </button>

        <button className="sidebar-btn btn-exit" onClick={handleLogout}>
          <i className="fas fa-sign-out-alt"></i>
          <span>Sair</span>
        </button>
      </div>
    </aside>
  );
};

export default MobileSidebar;