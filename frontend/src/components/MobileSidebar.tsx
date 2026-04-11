// SenseiDB/frontend/src/components/MobileSidebar.tsx
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
  selectedPersona: string;
  setSelectedPersona: (role: string) => void;
}

const MobileSidebar: React.FC<MobileSidebarProps> = ({ 
  isOpen, 
  toggleSidebar, 
  toggleApiModal, 
  clearChat,
  selectedPersona,
  setSelectedPersona
}) => {
  const { user } = useAuth();
  const { theme } = useTheme();
  const [conversations, setConversations] = useState<any[]>([]);
  const [availablePersonas, setAvailablePersonas] = useState<string[]>([]);
  const [localPersona, setLocalPersona] = useState(selectedPersona);

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    setLocalPersona(selectedPersona);
  }, [selectedPersona]);

  useEffect(() => {
    if (user && isOpen) {
      fetchConversations();
      fetchPersonas();
    }
  }, [user, isOpen]);

  const fetchPersonas = async () => {
    try {
      const response = await api.get('/personas/');
      if (response.data && response.data.length > 0) {
        setAvailablePersonas(response.data);
      } else {
        setAvailablePersonas(['mentor_sensei', 'professor', 'nutricionista', 'atendente']);
      }
    } catch (error) {
      console.error('Error fetching personas:', error);
      setAvailablePersonas(['mentor_sensei', 'professor', 'nutricionista', 'atendente']);
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await api.get('/api/chat/conversations/');
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const handleValidate = (personaToValidate?: string) => {
    const valueToSet = (personaToValidate || localPersona).trim();
    if (valueToSet) {
      setSelectedPersona(valueToSet);
      setIsDropdownOpen(false);
      console.log(`🚀 Persona alterada: ${valueToSet}`);
    }
  };

  return (
    <div className={`mobile-sidebar ${isOpen ? 'open' : ''} ${theme}`}>
      <div className="mobile-sidebar-header">
        <h3>SenseiDB</h3>
        <button onClick={toggleSidebar} className="close-btn">&times;</button>
      </div>
      <div className="mobile-sidebar-content">
        <div className="new-chat-btn" onClick={() => { clearChat(); toggleSidebar(); }}>
          + Novo Chat
        </div>
        
        <div className="sidebar-actions-mobile">
           <button onClick={toggleApiModal} className="mobile-action-btn">Configurar API</button>
           
           <div className="mobile-persona-selector" style={{ marginTop: '10px' }}>
             <label className="persona-label">Persona (Papel)</label>
             <div className="persona-select-container">
               <div className={`persona-input-group ${isDropdownOpen ? 'active' : ''}`}>
                 <input 
                   type="text"
                   value={localPersona} 
                   onChange={(e) => {
                     setLocalPersona(e.target.value);
                     setIsDropdownOpen(true);
                   }}
                   onFocus={() => setIsDropdownOpen(true)}
                   className="persona-input-line"
                   placeholder="Digite p/ buscar..."
                 />
                 <button 
                   className="persona-dropdown-toggle" 
                   onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                 >
                   <i className={`fas fa-chevron-${isDropdownOpen ? 'up' : 'down'}`}></i>
                 </button>
               </div>

               {isDropdownOpen && (
                 <ul className="persona-dropdown-list mobile">
                   {availablePersonas
                     .filter(p => !localPersona || p.toLowerCase().includes(localPersona.toLowerCase()))
                     .map((p, idx) => (
                       <li 
                         key={idx} 
                         className="persona-option" 
                         onClick={() => {
                           setLocalPersona(p);
                           handleValidate(p);
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
           </div>
        </div>

        <div className="conversations-list">
          {conversations.map((conv) => (
            <div key={conv.id} className="conversation-item">
              {conv.title || 'Conversa sem título'}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MobileSidebar;
