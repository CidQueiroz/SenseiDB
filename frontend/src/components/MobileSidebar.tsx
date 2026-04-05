// SenseiDB/frontend/src/components/MobileSidebar.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '@cidqueiroz/cdkteck-ui';
import { api } from '../api';
import '../style_sensei.css'; 

interface MobileSidebarProps {
  isOpen: boolean;
  toggleSidebar: () => void;
}

const MobileSidebar: React.FC<MobileSidebarProps> = ({ isOpen, toggleSidebar }) => {
  const { user } = useAuth();
  const { theme } = useTheme();
  const [conversations, setConversations] = useState<any[]>([]);

  useEffect(() => {
    if (user && isOpen) {
      fetchConversations();
    }
  }, [user, isOpen]);

  const fetchConversations = async () => {
    try {
      const response = await api.get('/api/chat/conversations/');
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  return (
    <div className={`mobile-sidebar ${isOpen ? 'open' : ''} ${theme}`}>
      <div className="mobile-sidebar-header">
        <h3>SenseiDB</h3>
        <button onClick={toggleSidebar} className="close-btn">&times;</button>
      </div>
      <div className="mobile-sidebar-content">
        <div className="new-chat-btn" onClick={() => { /* clearChat(); toggleSidebar(); */ }}>
          + Novo Chat
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
