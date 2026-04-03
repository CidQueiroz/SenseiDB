import React from 'react';

const Privacidade: React.FC = () => {
  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto', color: 'white' }}>
      <h1>Política de Privacidade</h1>
      <p>Sua privacidade é importante para nós. Esta política explica como coletamos e usamos seus dados.</p>
      <h2>Coleta de Dados</h2>
      <p>Coletamos informações básicas de perfil via Google Login para personalizar sua experiência com o SenseiDB.</p>
      <h2>Uso de Inteligência Artificial</h2>
      <p>Os dados que você insere como "contexto" são processados por modelos de IA (Google Gemini / Groq) para fornecer respostas personalizadas.</p>
      <p>Para mais detalhes, entre em contato via cdkteck.com.br.</p>
    </div>
  );
};

export default Privacidade;
