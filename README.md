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
- 📱 **Responsivo**: Interface moderna em HTML, CSS e JavaScript

## 🏗️ Arquitetura

```
┌─────────────────┐
│   HTML/CSS/JS   │  Frontend (Estático)
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
- Conta Google Cloud com um projeto criado
- Conta Firebase
- API Keys: Google AI + Groq (opcional)

### Instalação Local

1.  **Clone o repositório:**
    ```bash
    git clone <seu-repo>
    cd senseidb-agent
    ```

2.  **Configure o Backend (Django):**
    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure as Variáveis de Ambiente:**
    *   Crie um arquivo `.env` na pasta `backend` e adicione suas chaves de API (ex: `GOOGLE_API_KEY`, `GROQ_API_KEY`, `ADMIN_USER_ID`).

4.  **Rode o Servidor de Desenvolvimento:**
    ```bash
    python3 manage.py runserver
    ```
    O backend estará rodando em `http://localhost:8000`.

5.  **Abra o Frontend:**
    *   Abra o arquivo `frontend/index.html` diretamente no seu navegador.

## 🔧 Tecnologias

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Django, Django Rest Framework
- **Database**: Firebase Firestore
- **Auth**: Firebase Authentication
- **AI**: Groq (Llama 3.3) + Google (Gemini 1.5)
- **Embeddings**: Google text-embedding-004
- **Deploy**: Google Cloud Run com GitHub Actions CI/CD

## 📝 License

MIT License - veja LICENSE para detalhes

## 👨‍💻 Desenvolvido por

**CDK Tech**  
contato@cdkteck.com.br