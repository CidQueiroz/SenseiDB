// SenseiDB/frontend/src/components/Sidebar.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '@cidqueiroz/cdkteck-ui';
import { api } from '../api'; // Import your API instance

interface SidebarProps {
  toggleApiModal: () => void;
  clearChat: () => void;
  isCollapsed: boolean;
  toggleCollapsed: () => void;
  selectedPersona: string;
  setSelectedPersona: (role: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  toggleApiModal,
  clearChat,
  isCollapsed,
  toggleCollapsed,
  selectedPersona,
  setSelectedPersona
}) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme(); // Use the theme context
  const [newContext, setNewContext] = useState('');
  const [savingContext, setSavingContext] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isSynced, setIsSynced] = useState<boolean | null>(null);
  const [availablePersonas, setAvailablePersonas] = useState<string[]>([]);
  const [localPersona, setLocalPersona] = useState(selectedPersona);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLocalPersona(selectedPersona);
  }, [selectedPersona]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const checkSync = async () => {
      if (user) {
        try {
          const response = await api.get('/api-keys/');
          const { groq_api_key, google_api_key } = response.data;
          setIsSynced(!!(groq_api_key || google_api_key));
        } catch (error) {
          setIsSynced(false);
        }
      }
    };
    const fetchPersonas = async () => {
      try {
        const response = await api.get('/personas/');
        if (response.data && response.data.length > 0) {
          setAvailablePersonas(response.data);
        } else {
          // Fallback se a API retornar vazio
          setAvailablePersonas(['mentor_sensei', 'professor', 'nutricionista', 'atendente']);
        }
      } catch (error) {
        console.error('Erro ao carregar personas:', error);
        // Fallback em caso de erro de conexão
        setAvailablePersonas(['mentor_sensei', 'professor', 'nutricionista', 'atendente']);
      }
    };

    checkSync();
    fetchPersonas();
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

  const handleValidatePersona = (personaToValidate?: string) => {
    const valueToSet = (personaToValidate || localPersona).trim();
    if (!valueToSet) return;
    setSelectedPersona(valueToSet);
    setIsDropdownOpen(false);
    // Removemos o alert para uma experiência mais fluida, como solicitado
    console.log(`🚀 Persona alterada para: ${valueToSet}`);
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
            <span style={{ color: isSynced ? '#06f0a8' : '#eb1d32' }}>●</span>
            {!isCollapsed && (
              <span title={isSynced ? 'Chaves sincronizadas' : 'Sem chaves configuradas'}>
                {isSynced ? '🚀 Modo Master' : 'Nível Gratuito'}
              </span>
            )}
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

        <div className="sidebar-buttons">
          <button className="sidebar-btn btn-save" onClick={handleSaveContext} disabled={savingContext}>
            <i className="fas fa-save"></i>
            {!isCollapsed && <span>{savingContext ? 'Salvando...' : 'Salvar Inteligência'}</span>}
          </button>
        </div>

      </div>

      {/* Persona Section (Searchable Dropdown) */}
      <div className="persona-section" ref={dropdownRef}>
        {!isCollapsed && <div className="persona-label">Persona (Papel)</div>}
        {!isCollapsed && (
          <div className="persona-select-container">
            <div className={`persona-input-group ${isDropdownOpen ? 'active' : ''}`}>
              <input
                type="text"
                className="persona-input-line"
                placeholder="Busque um papel..."
                value={localPersona}
                onChange={(e) => {
                  setLocalPersona(e.target.value);
                  setIsDropdownOpen(true);
                }}
                onFocus={() => setIsDropdownOpen(true)}
                onKeyPress={(e) => e.key === 'Enter' && handleValidatePersona()}
              />
              <button 
                className="persona-dropdown-toggle" 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                title="Ver todas as personas"
              >
                <i className={`fas fa-chevron-${isDropdownOpen ? 'up' : 'down'}`}></i>
              </button>
            </div>

            {isDropdownOpen && (
              <ul className="persona-dropdown-list">
                {availablePersonas
                  .filter(p => !localPersona || p.toLowerCase().includes(localPersona.toLowerCase()))
                  .map((p, idx) => (
                    <li 
                      key={idx} 
                      className="persona-option" 
                      onClick={() => {
                        setLocalPersona(p);
                        handleValidatePersona(p);
                      }}
                    >
                      {p}
                    </li>
                  ))}
                {availablePersonas.filter(p => !localPersona || p.toLowerCase().includes(localPersona.toLowerCase())).length === 0 && (
                  <li className="persona-option disabled">Nenhuma persona encontrada</li>
                )}
              </ul>
            )}
          </div>
        )}
      </div>

      {/* Buttons */}
      <div className="sidebar-buttons">
        {/* <button className="sidebar-btn btn-save" onClick={handleSaveContext} disabled={savingContext}>
          <i className="fas fa-save"></i>
          {!isCollapsed && <span>{savingContext ? 'Salvando...' : 'Salvar Inteligência'}</span>}
        </button> */}

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