// senseidb-agent/frontend/src/components/ApiConfigModal.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../api'; // Your Axios instance for backend calls

interface ApiConfigModalProps {
  isOpen: boolean;
  toggleModal: () => void;
  // Prop to update AI status text in Sidebar/MobileSidebar if needed
  // updateAIStatus: (usedAi?: string) => void;
}

const ApiConfigModal: React.FC<ApiConfigModalProps> = ({ isOpen, toggleModal /*, updateAIStatus */ }) => {
  const [apiProvider, setApiProvider] = useState<string>(localStorage.getItem('api_provider') || 'groq');
  const [groqApiKey, setGroqApiKey] = useState<string>(localStorage.getItem('groq_api_key') || '');
  const [googleApiKey, setGoogleApiKey] = useState<string>(localStorage.getItem('google_api_key') || '');

  useEffect(() => {
    // Sync local state with localStorage on mount
    setApiProvider(localStorage.getItem('api_provider') || 'groq');
    setGroqApiKey(localStorage.getItem('groq_api_key') || '');
    setGoogleApiKey(localStorage.getItem('google_api_key') || '');
  }, [isOpen]); // Re-sync when modal opens

  const saveApiKey = () => {
    localStorage.setItem('api_provider', apiProvider);
    localStorage.setItem('groq_api_key', groqApiKey.trim());
    localStorage.setItem('google_api_key', googleApiKey.trim());

    // You might want to provide a more sophisticated feedback
    alert('✅ Configuração de API atualizada!');
    toggleModal();
    // if (updateAIStatus) updateAIStatus(apiProvider); // Notify parent to update AI status
  };

  const toggleApiInputFields = (selectedProvider: string) => {
    setApiProvider(selectedProvider);
  };

  if (!isOpen) return null;

  return (
    <div className="modal">
      <div className="modal-content">
        <div className="modal-header">Configurar API Key</div>
        
        <div className="form-group">
            <label htmlFor="apiProvider">Provedor de IA</label>
            <select 
              id="apiProvider" 
              className="form-control" 
              value={apiProvider}
              onChange={(e) => toggleApiInputFields(e.target.value)}
            >
                <option value="groq">Groq (Rápido)</option>
                <option value="google">Google AI (Estável)</option>
            </select>
        </div>

        {apiProvider === 'groq' && (
          <div className="form-group">
              <label htmlFor="groqApiKey">Chave Groq API</label>
              <input 
                type="password" 
                id="groqApiKey" 
                className="form-control" 
                placeholder="gsk_..." 
                value={groqApiKey}
                onChange={(e) => setGroqApiKey(e.target.value)}
              />
              <small>Obtenha sua chave em <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer">Groq Console</a>.</small>
          </div>
        )}

        {apiProvider === 'google' && (
          <div className="form-group">
              <label htmlFor="googleApiKey">Chave Google AI API</label>
              <input 
                type="password" 
                id="googleApiKey" 
                className="form-control" 
                placeholder="AIza..." 
                value={googleApiKey}
                onChange={(e) => setGoogleApiKey(e.target.value)}
              />
              <small>Obtenha sua chave no <a href="https://aistudio.google.com/app/api-keys" target="_blank" rel="noopener noreferrer">Google AI Studio</a>.</small>
          </div>
        )}

        <div className="modal-buttons">
            <button className="btn btn-primary" onClick={saveApiKey}>Salvar</button>
            <button className="btn btn-secondary" onClick={toggleModal}>Cancelar</button>
        </div>
      </div>
    </div>
  );
};

export default ApiConfigModal;
