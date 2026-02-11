// senseidb-agent/frontend/src/components/ApiConfigModal.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../api'; // Your Axios instance for backend calls
import { useAuth } from '../context/AuthContext'; // To potentially show user info

interface ApiConfigModalProps {
  isOpen: boolean;
  toggleModal: () => void;
  // Prop to update AI status text in Sidebar/MobileSidebar if needed
  // updateAIStatus: (usedAi?: string) => void;
}

const ApiConfigModal: React.FC<ApiConfigModalProps> = ({ isOpen, toggleModal /*, updateAIStatus */ }) => {
  const { user } = useAuth(); // Get user to ensure authenticated
  const [apiProvider, setApiProvider] = useState<string>('groq'); // Default to groq
  const [groqApiKey, setGroqApiKey] = useState<string>('');
  const [googleApiKey, setGoogleApiKey] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && user) {
      setLoading(true);
      setError(null);
      api.get('/api-keys/')
        .then(response => {
          const { groq_api_key, google_api_key } = response.data;
          setGroqApiKey(groq_api_key || '');
          setGoogleApiKey(google_api_key || '');
          // You might want to infer apiProvider based on which key is present or set a default
          if (groq_api_key) setApiProvider('groq');
          else if (google_api_key) setApiProvider('google');
        })
        .catch(err => {
          console.error("Erro ao buscar chaves API:", err);
          setError("Falha ao carregar chaves API.");
        })
        .finally(() => setLoading(false));
    }
  }, [isOpen, user]); // Re-fetch when modal opens or user changes

  const saveApiKey = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.post('/api-keys/', {
        groq_api_key: groqApiKey.trim() || null, // Send null if empty
        google_api_key: googleApiKey.trim() || null, // Send null if empty
      });
      alert('✅ Configuração de API atualizada!');
      toggleModal();
    } catch (err) {
      console.error("Erro ao salvar chaves API:", err);
      setError("Falha ao salvar chaves API. Verifique sua conexão e autenticação.");
    } finally {
      setLoading(false);
    }
  };

  const toggleApiInputFields = (selectedProvider: string) => {
    setApiProvider(selectedProvider);
  };

  if (!isOpen) return null;

  return (
    <div className="modal">
      <div className="modal-content">
        <button className="close-button" onClick={toggleModal}>&times;</button>
        <div className="modal-header">Configurar API Key</div>
        
        {loading && <p>Carregando configurações...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {!loading && (
          <>
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
                <button className="btn btn-primary" onClick={saveApiKey} disabled={loading}>Salvar</button>
                <button className="btn btn-secondary" onClick={toggleModal} disabled={loading}>Cancelar</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ApiConfigModal;
