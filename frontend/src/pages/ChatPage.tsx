import React, { useState, useRef, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import MobileSidebar from '../components/MobileSidebar';
import ApiConfigModal from '../components/ApiConfigModal';
import TutorialOverlay from '../components/TutorialOverlay';
import '../style_sensei.css';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import { universoLinks, sobreLinks } from '@cidqueiroz/cdkteck-ui';

interface ChatPageProps {
  isMobileSidebarOpen: boolean;
  toggleMobileSidebar: () => void;
}

const ChatPage: React.FC<ChatPageProps> = ({ isMobileSidebarOpen, toggleMobileSidebar }) => {
  const { user } = useAuth();
  const [isApiModalOpen, setIsApiModalOpen] = useState(false);
  const [isTutorialOverlayOpen, setIsTutorialOverlayOpen] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [showUniversoDropdown, setShowUniversoDropdown] = useState(false);
  const [showSobreDropdown, setShowSobreDropdown] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [selectedPersona, setSelectedPersona] = useState<string>(localStorage.getItem('selected_persona') || 'mentor_sensei');

  const toggleApiModal = () => setIsApiModalOpen(!isApiModalOpen);
  const toggleTutorialOverlay = () => setIsTutorialOverlayOpen(!isTutorialOverlayOpen);
  const clearChatMessages = () => setMessages([]);
  const toggleSidebarCollapsed = () => setIsSidebarCollapsed(!isSidebarCollapsed); // New toggle function

  const addMessage = (content: string, role: 'user' | 'assistant', aiUsed?: string, numContextos?: number, persona?: string) => {
    setMessages((prevMessages) => [...prevMessages, { content, role, aiUsed, numContextos, persona }]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (currentInput.trim() === '' || isLoading) return;

    const userMessage = currentInput.trim();
    addMessage(userMessage, 'user');
    setCurrentInput('');
    setIsLoading(true);

    try {
      // Get preferred provider from localStorage (migrated logic from old version)
      const preferredProvider = localStorage.getItem('api_provider') || 'groq';

      const response = await api.post('/chat/', { 
        query: userMessage,
        provider: preferredProvider,
        role: selectedPersona
      });
      
      const { resposta, ia_usada, num_contextos } = response.data;
      addMessage(resposta, 'assistant', ia_usada, num_contextos, selectedPersona);
    } catch (error: any) {
      console.error('Error sending message to backend:', error);
      let errorMessage = 'O Sensei está pensando muito forte, tente simplificar a pergunta ou verifique sua conexão.';
      if (error.response && error.response.data && error.response.data.error === 'INVALID_API_KEY') {
        errorMessage = `Sua chave da API ${error.response.data.provider.toUpperCase()} é inválida. Por favor, gerencie suas chaves API.`;
      }
      addMessage(errorMessage, 'assistant', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const checkIfFirstTime = async () => {
      if (!user) return;

      // Check if tutorial was seen from local storage
      const tutorialSeen = localStorage.getItem(`tutorial_seen_${user.uid}`);
      if (tutorialSeen) return;

      try {
        // Now calling the Django backend endpoint
        const response = await api.get(`/contexto/check/${user.uid}/`);

        if (!response.data.has_contexts) { // Assuming backend returns { has_contexts: boolean }
          setIsTutorialOverlayOpen(true);
        }
      } catch (error) {
        console.error('Error checking context:', error);
        // If there's an error, still show tutorial as a fallback
        setIsTutorialOverlayOpen(true);
      }
    };
    if (user) {
      checkIfFirstTime();
    }
  }, [user]);

  // Filtra o link da página atual para não aparecer no menu
  const filteredUniversoLinks = universoLinks.filter((link: any) => !link.href.includes('senseidb'));
  const filteredSobreLinks = sobreLinks;

  return (
    <div className={`chat-layout ${isMobileSidebarOpen ? 'mobile-sidebar-open' : ''} ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      {/* Desktop Sidebar */}
      <Sidebar 
        toggleApiModal={toggleApiModal} 
        clearChat={clearChatMessages} 
        isCollapsed={isSidebarCollapsed}
        toggleCollapsed={toggleSidebarCollapsed}
        selectedPersona={selectedPersona}
        setSelectedPersona={(role) => {
          setSelectedPersona(role);
          localStorage.setItem('selected_persona', role);
        }}
      />

      <div className="chat-main-content">
        {/* Custom Chat Header */}
        <header className="chat-page-header">
          {/* Mobile Toggle Button */}
          <button className="mobile-sidebar-toggle-button" onClick={toggleMobileSidebar}>
            ☰
          </button>
          
          <div className="chat-header-left">
            <a href="https://cdkteck.com.br" className="cabecalho-logo"> {/* <--- Classe aqui */}
              <span>CDK TECK</span>
            </a>
          </div>

          <div className="chat-header-center">
            <h2>🧠 Assistente Sensei</h2>
          </div>

          <nav className="chat-header-nav">
            {/* Universo CDK TECK Dropdown */}
            <div 
              className="dropdown"
              onMouseEnter={() => setShowUniversoDropdown(true)}
              onMouseLeave={() => setShowUniversoDropdown(false)}
            >
              <button className="dropdown-toggle">Universo CDK TECK</button>
              {showUniversoDropdown && (
                <div className="dropdown-menu">
                  {filteredUniversoLinks.map((link: any) => {
                    if (link.disabled) {
                      return (
                        <span key={link.text} className="disabled-link" title="Em desenvolvimento">
                          {link.text}
                        </span>
                      );
                    }
                    const isExternal = link.external || (link.href.startsWith('http'));
                    if (isExternal) {
                      return (
                        <a 
                          key={link.href} 
                          href={link.href} 
                          target="_blank"
                          rel="noopener noreferrer"
                          className="external-link"
                        >
                          {link.text} ↗
                        </a>
                      );
                    }
                    return (
                      <a key={link.href} href={link.href} className="internal-link">
                        {link.text}
                      </a>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Sobre Dropdown */}
            <div 
              className="dropdown"
              onMouseEnter={() => setShowSobreDropdown(true)}
              onMouseLeave={() => setShowSobreDropdown(false)}
            >
              <button className="dropdown-toggle">Sobre</button>
              {showSobreDropdown && (
                <div className="dropdown-menu">
                  {filteredSobreLinks.map((link: any) => {
                    const isExternal = link.external || (link.href.startsWith('http'));
                    if (isExternal) {
                      return (
                        <a 
                          key={link.href} 
                          href={link.href} 
                          target="_blank"
                          rel="noopener noreferrer"
                          className="external-link"
                        >
                          {link.text} ↗
                        </a>
                      );
                    }
                    return (
                      <a key={link.href} href={link.href} className="internal-link">
                        {link.text}
                      </a>
                    );
                  })}
                </div>
              )}
            </div>
          </nav>
        </header>

        {/* Chat Messages */}
        <div className="chat-messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h3>Olá! Eu sou o Sensei 🧠</h3>
              <p>
                Sou seu mentor de IA adaptativo, criado pela CDK TECK para ajudar você a extrair
                insights profundos dos seus dados.
                <br />
                <br />
                Como posso ajudar você hoje? 💡
              </p>
            </div>
          ) : (
            <>
              <ChatWindow
                messages={messages}
                addMessage={addMessage}
                toggleMobileSidebar={toggleMobileSidebar}
              />
              {isLoading && (
                <div className="message assistant">
                  <div className="message-avatar">
                    {selectedPersona === 'professor' ? '🎓' : 
                     selectedPersona === 'nutricionista' ? '🍎' :
                     selectedPersona === 'atendente' ? '🎧' : '🧠'}
                  </div>
                  <div className="message-bubble">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="chat-input-area">
          <input
            type="text"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            placeholder="Converse com o SenseiDB..."
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            disabled={isLoading}
          />
          <button onClick={handleSendMessage} disabled={isLoading}>
            {isLoading ? 'Enviando...' : 'Enviar'}
          </button>
        </div>
      </div>

      {/* Mobile Sidebar */}
      <MobileSidebar
        isOpen={isMobileSidebarOpen}
        toggleSidebar={toggleMobileSidebar}
        toggleApiModal={toggleApiModal}
        clearChat={clearChatMessages}
        selectedPersona={selectedPersona}
        setSelectedPersona={(role) => {
          setSelectedPersona(role);
          localStorage.setItem('selected_persona', role);
        }}
      />
      {isMobileSidebarOpen && (
        <div className="mobile-sidebar-overlay" onClick={toggleMobileSidebar}></div>
      )}

      {/* Modals */}
      <ApiConfigModal isOpen={isApiModalOpen} toggleModal={toggleApiModal} />
      <TutorialOverlay isOpen={isTutorialOverlayOpen} toggleOverlay={toggleTutorialOverlay} />
    </div>
  );
};

export default ChatPage;