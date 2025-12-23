// senseidb-agent/frontend/src/pages/ChatPage.tsx
import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import MobileSidebar from '../components/MobileSidebar';
import ApiConfigModal from '../components/ApiConfigModal';
import TutorialOverlay from '../components/TutorialOverlay';
import { useAuth } from '../context/AuthContext'; // Import useAuth to access user
import { api } from '../api'; // Import api instance

const ChatPage: React.FC = () => {
  const { user } = useAuth(); // Get user from AuthContext
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [isApiModalOpen, setIsApiModalOpen] = useState(false);
  const [isTutorialOverlayOpen, setIsTutorialOverlayOpen] = useState(false);
  const [messages, setMessages] = useState<any[]>([]); // State for chat messages

  // These states and their toggles will be managed here and passed down
  const toggleMobileSidebar = () => setIsMobileSidebarOpen(!isMobileSidebarOpen);
  const toggleApiModal = () => setIsApiModalOpen(!isApiModalOpen);
  const toggleTutorialOverlay = () => setIsTutorialOverlayOpen(!isTutorialOverlayOpen);

  // Function to clear chat messages, passed to Sidebar and MobileSidebar
  const clearChatMessages = () => setMessages([]);

  // Function to add a new message, passed to ChatWindow
  const addMessage = (content: string, role: 'user' | 'assistant', aiUsed?: string) => {
    setMessages((prevMessages) => [...prevMessages, { content, role, aiUsed }]);
  };

  // Logic to check if tutorial should be shown
  React.useEffect(() => {
    const checkIfFirstTime = async () => {
        if (!user) return;

        const tutorialSeen = localStorage.getItem(`tutorial_seen_${user.uid}`);
        if (tutorialSeen) return;

        try {
            const response = await api.get(`/contexto/check/${user.uid}`);
            
            if (response.status === 404 || response.data.count === 0 || !response.data.has_contexts) {
                setIsTutorialOverlayOpen(true);
            }
        } catch (error) {
            console.error('Error checking context:', error);
            setIsTutorialOverlayOpen(true); // Fallback to showing tutorial
        }
    };
    if (user) {
        checkIfFirstTime();
    }
  }, [user]);

  return (
    <div className="chat-app-container"> {/* This is the main container for the chat UI */}
      <Sidebar 
        toggleApiModal={toggleApiModal} 
        clearChat={clearChatMessages} 
      />
      <ChatWindow 
        messages={messages} 
        addMessage={addMessage} 
        toggleMobileSidebar={toggleMobileSidebar}
      />

      {/* Mobile-specific components */}
      <MobileSidebar 
        isOpen={isMobileSidebarOpen} 
        toggleSidebar={toggleMobileSidebar} 
        toggleApiModal={toggleApiModal}
        clearChat={clearChatMessages}
      />
      {isMobileSidebarOpen && <div className="overlay" onClick={toggleMobileSidebar}></div>}

      <ApiConfigModal isOpen={isApiModalOpen} toggleModal={toggleApiModal} />
      <TutorialOverlay isOpen={isTutorialOverlayOpen} toggleOverlay={toggleTutorialOverlay} />
    </div>
  );
};

export default ChatPage;
