# 🧠 SenseiDB v3.0.0

> Seu Mentor Estratégico Pessoal com IA

## 📋 Sobre o Projeto

SenseiDB é um assistente de IA personalizado que aprende com você através de um sistema RAG (Retrieval-Augmented Generation). Ele usa seus contextos salvos para fornecer respostas adaptadas ao seu perfil e necessidades.

### ✨ Principais Recursos

- 🧠 **RAG Inteligente**: Sistema de busca semântica com embeddings.
- 🚀 **Groq AI**: Respostas ultra-rápidas com Llama 3.
- 🌐 **Google AI**: Fallback automático com Gemini 1.5.
- 🔐 **Segurança**: Autenticação Firebase + dados protegidos.
- 🐳 **Containerizado**: Ambiente de desenvolvimento e produção 100% em Docker.
- 🤖 **Versionamento Automático**: Releases e changelogs automáticos com `semantic-release`.

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

## 🚀 Ambiente de Desenvolvimento

Este projeto usa Docker e Docker Compose para criar um ambiente de desenvolvimento consistente e fácil de usar.

### Pré-requisitos

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)

### Como Rodar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone <seu-repo>
    cd senseidb-agent
    ```

2.  **Configure as Variáveis de Ambiente:**
    *   Crie um arquivo chamado `.env.deploy` na raiz da pasta `senseidb-agent`.
    *   Adicione suas chaves de API e configurações do Firebase neste arquivo (ex: `GOOGLE_API_KEY=...`, `GROQ_API_KEY=...`, etc.).

3.  **Inicie o Ambiente:**
    *   Com o Docker Desktop em execução, rode o comando:
    ```bash
    docker-compose up
    ```

4.  **Acesse as Aplicações:**
    *   **Frontend:** [http://localhost:8001](http://localhost:8001)
    *   **Backend API:** [http://localhost:8000](http://localhost:8000) (ex: [http://localhost:8000/admin/](http://localhost:8000/admin/))

O ambiente possui **live-reload**. Qualquer alteração nos arquivos do `frontend` ou `backend` será refletida automaticamente. Para parar todo o ambiente, pressione `Ctrl+C` no terminal.

## 🤖 Versionamento e Commits

Este projeto usa [Conventional Commits](https://www.conventionalcommits.org/) para automatizar o versionamento com `semantic-release`.

- **Para fazer commits:** Em vez de `git commit`, use o assistente:
  ```bash
  npm run cz
  ```
- Siga as instruções para descrever sua alteração.
- Ao fazer `git push` para a branch `main`, uma nova versão será criada automaticamente se sua contribuição for um `feat` ou `fix`.
