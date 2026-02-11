import React, { useState, useRef, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import MobileSidebar from '../components/MobileSidebar';
import ApiConfigModal from '../components/ApiConfigModal';
import TutorialOverlay from '../components/TutorialOverlay';
import '../style_sensei.css';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import { useTheme } from '@cidqueiroz/cdkteck-ui'; // Import useTheme
import { useLocation } from 'react-router-dom'; // Import useLocation

interface ChatPageProps {
  isMobileSidebarOpen: boolean;
  toggleMobileSidebar: () => void;
}

const ChatPage: React.FC<ChatPageProps> = ({ isMobileSidebarOpen, toggleMobileSidebar }) => {
  const { user } = useAuth();
  const { theme } = useTheme(); // Use theme context for logo
  const location = useLocation(); // Get current location
  const [isApiModalOpen, setIsApiModalOpen] = useState(false);
  const [isTutorialOverlayOpen, setIsTutorialOverlayOpen] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [showUniversoDropdown, setShowUniversoDropdown] = useState(false);
  const [showSobreDropdown, setShowSobreDropdown] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false); // New state for sidebar collapse

  const toggleApiModal = () => setIsApiModalOpen(!isApiModalOpen);
  const toggleTutorialOverlay = () => setIsTutorialOverlayOpen(!isTutorialOverlayOpen);
  const clearChatMessages = () => setMessages([]);
  const toggleSidebarCollapsed = () => setIsSidebarCollapsed(!isSidebarCollapsed); // New toggle function

  const addMessage = (content: string, role: 'user' | 'assistant', aiUsed?: string) => {
    setMessages((prevMessages) => [...prevMessages, { content, role, aiUsed }]);
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
      const response = await api.post('/chat/', { query: userMessage });
      const { resposta, ia_usada } = response.data;
      addMessage(resposta, 'assistant', ia_usada);
    } catch (error) {
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

  const universoLinks = [
    { href: 'https://cdkteck.com.br', text: 'CDK TECK (Home)', external: true, disabled: false },
    { href: '#', text: 'PapoDados', external: false, disabled: true },
    { href: '#', text: 'Caça-Preço', external: false, disabled: true },
    { href: 'https://sensei.cdkteck.com.br', text: 'SenseiDB', external: true, disabled: false },
    { href: 'https://gestaorpd.cdkteck.com.br', text: 'Gestão RPD', external: true, disabled: false },
  ];

  const sobreLinks = [
    { href: 'https://cdkteck.com.br/sobre', text: 'Filosofia & Identidade', external: true },
    { href: 'https://cdkteck.com.br/pbi', text: 'Portfólio de Dashboards', external: true },
    { href: 'https://cdkteck.com.br/portfolio', text: 'Laboratório de Projetos', external: true },
    { href: 'https://cdkteck.com.br/certificados', text: 'Certificados', external: true },
  ];

  return (
    <div className={`chat-layout ${isMobileSidebarOpen ? 'mobile-sidebar-open' : ''} ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      {/* Desktop Sidebar */}
      <Sidebar 
        toggleApiModal={toggleApiModal} 
        clearChat={clearChatMessages} 
        isCollapsed={isSidebarCollapsed} // Pass the collapsed state
        toggleCollapsed={toggleSidebarCollapsed} // Pass the toggle function
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
                  {universoLinks.map(link => {
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
                  {sobreLinks.map(link => {
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
                  <div className="message-avatar">🧠</div>
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