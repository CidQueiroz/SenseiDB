// senseidb-agent/frontend/src/components/ChatWindow.tsx
import React from 'react';

interface Message {
  content: string;
  role: 'user' | 'assistant';
  aiUsed?: string;
}

interface ChatWindowProps {
  messages: Message[];
  addMessage: (content: string, role: 'user' | 'assistant', aiUsed?: string) => void;
  toggleMobileSidebar: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, addMessage, toggleMobileSidebar }) => {
  return (
    <>
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.role}`}>
          <div className="message-avatar">
            {message.role === 'assistant' ? '🧠' : '👤'}
          </div>
          <div className="message-bubble">
            {message.content}
            {message.aiUsed && (
              <div className="ai-badge">
                Powered by {message.aiUsed}
              </div>
            )}
          </div>
        </div>
      ))}
    </>
  );
};

export default ChatWindow;