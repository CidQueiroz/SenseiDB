# 🧠 SenseiDB v3.0

> Seu Mentor Estratégico Pessoal com IA

## 📋 Sobre o Projeto

SenseiDB é um assistente de IA personalizado que aprende com você através de um sistema RAG (Retrieval-Augmented Generation). Ele usa seus contextos salvos para fornecer respostas adaptadas ao seu perfil e necessidades.

### ✨ Principais Recursos

- 🧠 **RAG Inteligente**: Sistema de busca semântica com embeddings
- 🚀 **Groq AI**: Respostas ultra-rápidas com Llama 3.3 70B
- 🌐 **Google AI**: Fallback automático com Gemini 1.5
- 🔐 **Segurança**: Autenticação Firebase + dados protegidos
- 🎯 **Personalização**: O Sensei aprende com seus contextos
- 📱 **Responsivo**: Interface moderna em Streamlit

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Streamlit     │  Frontend (Python)
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│     Django      │  Backend (Python)
│   REST API      │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐  ┌──────────┐
│Firebase│  │ AI APIs  │
│Firestore│  │Groq/Google│
└────────┘  └──────────┘
```

## 🚀 Quick Start

### Pré-requisitos

- Python 3.8+
- Conta Google Cloud
- Conta Firebase
- API Keys: Google AI + Groq (opcional)

### Instalação Rápida

```bash
# Clone o repositório
git clone <seu-repo>
cd Agente_AI

# Execute o setup
chmod +x setup_project.sh
./setup_project.sh

# Configure as chaves
cp functions/.env.example functions/.env
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edite os arquivos com suas chaves reais

# Inicie o desenvolvimento
make start
# ou
./start_dev.sh
```

## 📚 Documentação Completa

Veja [SETUP_GUIDE.md](SETUP_GUIDE.md) para instruções detalhadas.

## 🛠️ Comandos Disponíveis

```bash
make setup    # Configuração inicial
make check    # Verifica configuração
make start    # Inicia desenvolvimento
make test     # Executa testes
make deploy   # Deploy para Cloud
make clean    # Limpa temporários
```

## 🔧 Tecnologias

- **Frontend**: Streamlit 1.29
- **Backend**: Django 4.2 + DRF
- **Database**: Firebase Firestore
- **Auth**: Firebase Authentication
- **AI**: Groq (Llama 3.3) + Google (Gemini 1.5)
- **Embeddings**: Google text-embedding-004
- **Deploy**: Google Cloud Run

## 📖 Como Usar

1. **Login/Cadastro**: Crie sua conta ou faça login
2. **Configure API**: Insira sua chave Groq ou use Google AI
3. **Adicione Contextos**: Salve informações sobre você
4. **Converse**: Interaja com o Sensei!

## 🤝 Integração com Django

Para integrar com outro projeto Django:

```python
# settings.py
INSTALLED_APPS = [
    # ... suas apps
    'agent',  # Adicione a app do SenseiDB
]

# urls.py
urlpatterns = [
    # ... suas urls
    path('senseidb/', include('agent.urls')),
]
```

## 🐛 Troubleshooting

Veja a seção de Troubleshooting no [SETUP_GUIDE.md](SETUP_GUIDE.md).

## 📝 License

MIT License - veja LICENSE para detalhes

## 👨‍💻 Desenvolvido por

**CDK Tech**  
contato@cdkteck.com.br

---

**Versão:** 3.0  
**Status:** Production Ready
pip install google-generativeai==0.3.2