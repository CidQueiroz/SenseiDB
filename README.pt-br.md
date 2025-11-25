<div align="center">

# 🧠 SenseiDB - O Agente de IA Pessoal com RAG
### Um mentor de IA privado e contextual que se adapta ao seu conhecimento.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-API-092E20?style=for-the-badge&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![GCP](https://img.shields.io/badge/Google_Cloud-Run-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 🚀 Conceito Central

O **SenseiDB** é um assistente de IA pessoal projetado para ser um mentor estratégico que se adapta à base de conhecimento privada do usuário. Ele utiliza uma arquitetura **RAG (Retrieval-Augmented Generation)** para fornecer respostas contextualmente relevantes com base em seus documentos, anotações e dados.

Diferente de chatbots genéricos, o SenseiDB baseia suas respostas em suas informações fornecidas, garantindo privacidade e entregando insights personalizados e precisos. É uma IA que realmente conhece o seu mundo.

---

## 🏛️ Fluxo da Arquitetura RAG

O sistema é projetado em torno do padrão RAG para garantir que as respostas da IA sejam aumentadas com contexto factual fornecido pelo usuário.

```mermaid
graph TD
    subgraph "Interface do Usuário (React)"
        UI(Interface do Usuário)
    end

    subgraph "Serviços de Backend (Django no GCP Cloud Run)"
        API(API Gateway)
        EmbeddingService(Serviço de Embedding)
        VectorDB[(Banco de Dados Vetorial)]
        LLM_Service(Serviço de LLM<br/>Gemini / Groq)
    end

    subgraph "Externo"
        LLM_API(API do Provedor de LLM)
    end

    UI -- 1. "Como X funciona?" --> API
    API -- 2. "Como X funciona?" --> EmbeddingService
    EmbeddingService -- 3. [Vetor de Embedding] --> VectorDB
    VectorDB -- 4. Retorna Pedaços Relevantes --> API
    API -- 5. "Contexto: [Pedaços]<br/>Pergunta: Como X funciona?" --> LLM_Service
    LLM_Service -- 6. Encaminha Prompt --> LLM_API
    LLM_API -- 7. Resposta Gerada --> LLM_Service
    LLM_Service -- 8. Resposta Formatada --> API
    API -- 9. Resposta Final --> UI

    style VectorDB fill:#4285F4,stroke:#fff,stroke-width:2px,color:#fff
    style LLM_Service fill:#34A853,stroke:#fff,stroke-width:2px,color:#fff
```

1.  **Pergunta:** O usuário faz uma pergunta através do frontend em React.
2.  **Embedding:** O backend Django gera uma representação vetorial (embedding) da pergunta.
3.  **Recuperação:** O sistema consulta um banco de dados vetorial para encontrar os "pedaços" de texto mais relevantes dos documentos carregados pelo usuário.
4.  **Aumento:** Os pedaços recuperados são anexados à pergunta original, criando um prompt aumentado.
5.  **Geração:** Este prompt aumentado é enviado para um Grande Modelo de Linguagem (LLM) poderoso como o Gemini do Google ou o Llama do Groq.
6.  **Resposta:** O LLM gera uma resposta factual e ciente do contexto, que é enviada de volta ao usuário.

---

## ✨ Funcionalidades Chave

-   **Base de Conhecimento Privada:** Carregue seus documentos (PDF, TXT, etc.) para criar um contexto seguro e privado para a IA.
-   **Q&A Contextual:** Faça perguntas complexas e receba respostas baseadas em seus dados, completas com fontes.
-   **Suporte a Múltiplos LLMs:** Alterna dinamicamente entre provedores de LLM como Google AI (Gemini) e Groq para otimização de custo/velocidade e redundância.
-   **Backend RESTful:** Uma API Django robusta gerencia toda a lógica de negócio, autenticação de usuário e orquestração da IA.
-   **Ambiente Containerizado:** Totalmente containerizado com Docker para paridade entre desenvolvimento e produção, garantindo que "funciona na minha máquina" signifique que funciona na nuvem.

---

## ⚙️ Stack de Tecnologias

| Camada | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Frontend** | React | Uma Single Page Application (SPA) responsiva e moderna para chat e gerenciamento de documentos. |
| **Backend** | Django, Django Rest Framework | API RESTful segura e escalável para lógica de negócio e orquestração de IA. |
| **IA/ML** | Google AI (Gemini), Groq (Llama) | Múltiplos provedores de Grandes Modelos de Linguagem para geração de texto. |
| **Banco de Dados** | Banco de Dados Vetorial (ex: Pinecone, FAISS) | Armazena embeddings de documentos para busca semântica rápida. |
| **Implantação** | Docker, GCP Cloud Run, Firebase Hosting | Serviços containerizados implantados em um ambiente sem servidor para escalabilidade. |
| **DevOps** | GitHub Actions, Semantic Release | CI/CD totalmente automatizado para versionamento e implantação. |

---

## 🛠️ Começando: Desenvolvimento Local

A aplicação é containerizada para uma configuração fácil.

### Pré-requisitos
* Docker & Docker Compose
* Git
* Chaves de API para o Google AI e/ou Groq.

### 1. Clone o Repositório
```bash
git clone https://github.com/CidQueiroz/SenseiDB-Agent.git
cd SenseiDB-Agent
```

### 2. Configure as Variáveis de Ambiente

Crie um arquivo `.env.deploy` na raiz do projeto.

**Principais variáveis a serem configuradas:**
-   `GCP_PROJECT_ID`: Seu ID de Projeto do Google Cloud.
-   `GOOGLE_API_KEY`: Sua chave de API para o Gemini.
-   `GROQ_API_KEY`: Sua chave de API para o Groq.
-   `SECRET_KEY`: Uma chave secreta para o Django.

### 3. Construa e Execute a Aplicação

```bash
docker-compose up --build
```
Este comando iniciará o backend Django e o frontend React.

-   **API do Backend** estará disponível em `http://localhost:8000`.
-   **Aplicação Frontend** estará disponível em `http://localhost:8501`.

---

## 🚀 Pipeline de CI/CD

O projeto possui um pipeline de CI/CD totalmente automatizado usando GitHub Actions:

1.  **No Push para a `main`:**
    - Um workflow de `release` valida o código e usa o `semantic-release` para criar uma tag de versão com base nas mensagens de commit.
2.  **Em um Novo Release:**
    - Um workflow de `deploy` é acionado.
    - Ele constrói e envia uma imagem Docker do backend para o **Google Artifact Registry**.
    - Implanta esta nova imagem no **GCP Cloud Run**.
    - Constrói e implanta o frontend React no **Firebase Hosting**.
