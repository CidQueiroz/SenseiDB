// SenseiDB/frontend/src/components/ChatWindow.tsx
import React from 'react';

interface Message {
  content: string;
  role: 'user' | 'assistant';
  aiUsed?: string;
  numContextos?: number;
}

interface ChatWindowProps {
  messages: Message[];
  addMessage: (content: string, role: 'user' | 'assistant', aiUsed?: string, numContextos?: number) => void;
  toggleMobileSidebar: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages }) => {
  return (
    <>
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.role}`}>
          <div className="message-avatar">
            {message.role === 'assistant' ? '🧠' : '👤'}
          </div>
          <div className="message-bubble">
            <div className="message-text">
              {message.content}
            </div>
            {message.role === 'assistant' && (message.aiUsed || message.numContextos !== undefined) && (
              <div className="message-meta">
                {message.aiUsed && (
                  <span className="ai-badge">
                    ⚡ {message.aiUsed}
                  </span>
                )}
                {message.numContextos !== undefined && (
                  <span className="context-badge" title="Insights recuperados do seu histórico (RAG)">
                    🧠 {message.numContextos} contextos
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
    </>
  );
};

export default ChatWindow;