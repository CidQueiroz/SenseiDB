import React from 'react';

const Termos: React.FC = () => {
  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto', color: 'white' }}>
      <h1>Termos de Uso</h1>
      <p>Ao utilizar o SenseiDB, você concorda com os seguintes termos:</p>
      <h2>Uso Responsável</h2>
      <p>O SenseiDB é um mentor de IA. As respostas geradas são sugestões e não devem substituir conselhos profissionais qualificados.</p>
      <h2>Responsabilidade</h2>
      <p>A CDK TECK não se responsabiliza por decisões tomadas com base nas interações com a IA.</p>
      <p>Estes termos podem ser atualizados periodicamente.</p>
    </div>
  );
};

export default Termos;
