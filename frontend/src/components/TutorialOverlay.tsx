// SenseiDB/frontend/src/components/TutorialOverlay.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import '../style_sensei.css'; // Import the new CSS file

interface TutorialOverlayProps {
  isOpen: boolean;
  toggleOverlay: () => void;
}

const TutorialOverlay: React.FC<TutorialOverlayProps> = ({ isOpen, toggleOverlay }) => {
  const { user } = useAuth();
  const [currentSlide, setCurrentSlide] = useState(1);
  const totalSlides = 3;

  useEffect(() => {
    if (isOpen) {
      setCurrentSlide(1); // Reset to first slide when opened
    }
  }, [isOpen]);

  const completeTutorial = () => {
    if (user) {
      localStorage.setItem(`tutorial_seen_${user.uid}`, 'true');
    }
    toggleOverlay();
    // Potentially add a message to chat or highlight context area
    alert('Tutorial concluído! Para começar, adicione alguns contextos sobre você na sidebar. Quanto mais eu souber, melhor posso te ajudar!');
  };

  const nextSlide = () => {
    if (currentSlide < totalSlides) {
      setCurrentSlide(currentSlide + 1);
    } else {
      completeTutorial();
    }
  };

  const previousSlide = () => {
    if (currentSlide > 1) {
      setCurrentSlide(currentSlide - 1);
    }
  };

  const skipTutorial = () => {
    if (window.confirm('Tem certeza que deseja pular o tutorial? Você pode ver essas informações novamente limpando o cache do navegador.')) {
      completeTutorial();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="tutorial-overlay">
      <div className="tutorial-card">
        <div className="tutorial-header">
          <h2>🎓 Bem-vindo ao SenseiDB!</h2>
          <p id="tutorialSubtitle">Vamos te ensinar a usar seu mentor IA</p>
        </div>

        {/* Slide 1: Introdução */}
        {currentSlide === 1 && (
          <div className="tutorial-content">
            <div className="tutorial-steps">
              <div className="tutorial-step">
                <div className="tutorial-step-icon">🧠</div>
                <div className="tutorial-step-content">
                  <h3>O que é o SenseiDB?</h3>
                  <p>Um assistente de IA que aprende com você. Quanto mais você compartilha sobre si, mais personalizadas são as respostas.</p>
                </div>
              </div>
              <div className="tutorial-step">
                <div className="tutorial-step-icon">💾</div>
                <div className="tutorial-step-content">
                  <h3>Sistema RAG Inteligente</h3>
                  <p>Suas informações são salvas e usadas para gerar respostas específicas ao seu perfil, objetivos e desafios.</p>
                </div>
              </div>
              <div className="tutorial-step">
                <div className="tutorial-step-icon">🔒</div>
                <div className="tutorial-step-content">
                  <h3>Privacidade Garantida</h3>
                  <p>Seus dados ficam protegidos no Firebase. Apenas você tem acesso aos seus contextos.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Slide 2: Como Adicionar Contextos */}
        {currentSlide === 2 && (
          <div className="tutorial-content">
            <div className="tutorial-steps">
              <div className="tutorial-step">
                <div className="tutorial-step-icon">📝</div>
                <div className="tutorial-step-content">
                  <h3>1. Adicione Contextos</h3>
                  <p>Use a área "Adicionar Contexto" na sidebar para compartilhar informações sobre você: personalidade, objetivos, desafios, preferências.</p>
                </div>
              </div>
              <div className="tutorial-step">
                <div className="tutorial-step-icon">💡</div>
                <div className="tutorial-step-content">
                  <h3>Exemplos de Contextos</h3>
                  <p><strong>Bons:</strong> "Sou desenvolvedor Python", "Tenho dificuldade com procrastinação", "MBTI: INTP"<br/>
                  <strong>Evite:</strong> Logs temporários como "indo dormir"</p>
                </div>
              </div>
              <div className="tutorial-step">
                <div className="tutorial-step-icon">🎯</div>
                <div className="tutorial-step-content">
                  <h3>Quanto Mais, Melhor</h3>
                  <p>Quanto mais contextos você adiciona, mais o Sensei entende você e gera respostas personalizadas.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Slide 3: Como Usar o Chat */}
        {currentSlide === 3 && (
          <div className="tutorial-content">
            <div className="tutorial-steps">
              <div className="tutorial-step">
                <div className="tutorial-step-icon">💬</div>
                <div className="tutorial-step-content">
                  <h3>2. Converse com o Sensei</h3>
                  <p>Faça perguntas, peça conselhos, compartilhe situações. O Sensei usará seus contextos para dar respostas adaptadas a você.</p>
                </div>
              </div>
              <div className="tutorial-step">
                <div className="tutorial-step-icon">🤖</div>
                <div className="tutorial-step-content">
                  <h3>Duas IAs Disponíveis</h3>
                  <p><strong>Groq AI:</strong> Ultra-rápido (configure sua chave em Gerenciar API)<br/>
                  <strong>Google AI:</strong> Fallback automático se Groq falhar</p>
                </div>
              </div>
              <div className="tutorial-step">
                <div className="tutorial-step-icon">🔄</div>
                <div className="tutorial-step-content">
                  <h3>Atualização Contínua</h3>
                  <p>Continue adicionando contextos conforme evolui. O Sensei sempre usará as informações mais recentes.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navegação */}
        <div className="tutorial-progress">
          {[...Array(totalSlides)].map((_, i) => (
            <div key={i} className={`progress-dot ${currentSlide === i + 1 ? 'active' : ''}`}></div>
          ))}
        </div>

        <div className="tutorial-buttons">
          <button className="tutorial-btn-secondary" onClick={previousSlide} disabled={currentSlide === 1}>
            ← Anterior
          </button>
          <button className="tutorial-btn-primary" onClick={nextSlide}>
            {currentSlide === totalSlides ? 'Começar! 🚀' : 'Próximo →'}
          </button>
        </div>

        <div className="tutorial-skip" onClick={skipTutorial}>
          Pular tutorial
        </div>
      </div>
    </div>
  );
};

export default TutorialOverlay;
