// senseidb-agent/frontend/src/components/ChatWindow.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api, BACKEND_URL } from '../api';

interface ChatWindowProps {
  messages: any[]; // Array of message objects { content, role, aiUsed }
  addMessage: (content: string, role: 'user' | 'assistant', aiUsed?: string) => void;
  // Prop to toggle mobile sidebar, passed from ChatPage
  toggleMobileSidebar?: () => void; 
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, addMessage, toggleMobileSidebar }) => {
  const { user } = useAuth();
  const [chatInput, setChatInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [chatInput]);

  const sendMessage = async () => {
    if (!chatInput.trim() || !user) return;

    const userMessage = chatInput.trim();
    addMessage(userMessage, 'user');
    setChatInput('');
    setIsSending(true);

    try {
      const apiProvider = localStorage.getItem('api_provider') || 'groq';
      const groqApiKey = localStorage.getItem('groq_api_key') || '';
      const googleApiKey = localStorage.getItem('google_api_key') || '';

      const requestBody: any = {
        user_id: user.uid,
        query: userMessage,
      };

      if (apiProvider === 'groq' && groqApiKey) {
        requestBody.groq_api_key = groqApiKey;
      } else if (apiProvider === 'google' && googleApiKey) {
        requestBody.google_api_key = googleApiKey;
      }

      const response = await api.post('/chat/', requestBody); // Using Axios instance

      const data = response.data;

      if (response.status === 429 && data.error === 'USAGE_LIMIT_EXCEEDED') {
        addMessage('Seu limite de uso gratuito foi atingido. Por favor, adicione sua própria chave de API para continuar.', 'assistant');
        // showApiConfig(); // This would need to be passed down
      } else if (data.error === 'INVALID_API_KEY') {
        const providerName = data.provider === 'groq' ? 'Groq' : 'Google AI';
        addMessage(`Sua chave da ${providerName} parece ser inválida ou excedeu o limite. Por favor, verifique sua chave e tente novamente.`, 'assistant');
        // showApiConfig();
      } else if (data.error) {
        addMessage(`Erro: ${data.error}`, 'assistant');
      } else {
        addMessage(data.resposta, 'assistant', data.ia_usada);
        // updateAIStatus(data.ia_usada); // This would need to be passed down
      }
    } catch (error) {
      console.error('Erro de conexão:', error);
      addMessage(`Erro de conexão: ${error instanceof Error ? error.message : String(error)}`, 'assistant');
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="main-content">
      <div className="chat-header">
        {toggleMobileSidebar && (
          <button className="hamburger-btn" onClick={toggleMobileSidebar}>
            ☰
          </button>
        )}
        <h2>Assistente Sensei</h2>
      </div>

      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? (user?.email ? user.email[0].toUpperCase() : 'U') : '🧠'}
            </div>
            <div>
              <div className="message-content" dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, '<br>') }} />
              {msg.aiUsed && <div className="message-meta">via {msg.aiUsed === 'groq' ? 'Groq' : 'Google'}</div>}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={textareaRef}
            className="chat-input"
            placeholder="Qual sua pergunta ou situação?"
            rows={1}
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isSending}
          ></textarea>
          <button className="btn-send" onClick={sendMessage} disabled={isSending}>
            {isSending ? 'Enviando...' : 'Enviar'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;