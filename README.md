<div align="center">

# 🧠 SenseiDB - The Personal RAG AI Agent
### A private, context-aware AI mentor that adapts to your knowledge.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-API-092E20?style=for-the-badge&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![GCP](https://img.shields.io/badge/Google_Cloud-Run-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 🚀 Core Concept

**SenseiDB** is a personal AI assistant designed to be a strategic mentor that adapts to the user's private knowledge base. It leverages a **Retrieval-Augmented Generation (RAG)** architecture to provide contextually relevant answers based on your documents, notes, and data.

Unlike generic chatbots, SenseiDB grounds its responses in your provided information, ensuring privacy and delivering personalized, accurate insights. It's an AI that truly knows your world.

---

## 🏛️ RAG Architecture Flow

The system is engineered around the RAG pattern to ensure that the AI's responses are augmented with factual, user-provided context.

```mermaid
graph TD
    subgraph "User Interface (React)"
        UI(User Interface)
    end

    subgraph "Backend Services (Django on GCP Cloud Run)"
        API(API Gateway)
        EmbeddingService(Embedding Service)
        VectorDB[(Vector Database)]
        LLM_Service(LLM Service<br/>Gemini / Groq)
    end

    subgraph "External"
        LLM_API(LLM Provider API)
    end

    UI -- 1. "How does X work?" --> API
    API -- 2. "How does X work?" --> EmbeddingService
    EmbeddingService -- 3. [Embedding Vector] --> VectorDB
    VectorDB -- 4. Returns Relevant Chunks --> API
    API -- 5. "Context: [Chunks]<br/>Question: How does X work?" --> LLM_Service
    LLM_Service -- 6. Proxies Prompt --> LLM_API
    LLM_API -- 7. Generated Answer --> LLM_Service
    LLM_Service -- 8. Formatted Answer --> API
    API -- 9. Final Response --> UI

    style VectorDB fill:#4285F4,stroke:#fff,stroke-width:2px,color:#fff
    style LLM_Service fill:#34A853,stroke:#fff,stroke-width:2px,color:#fff
```

1.  **Query:** A user asks a question through the React frontend.
2.  **Embedding:** The Django backend generates a vector embedding of the question.
3.  **Retrieval:** The system queries a vector database to find the most relevant "chunks" of text from the user's uploaded documents.
4.  **Augmentation:** The retrieved chunks are prepended to the original question, creating an augmented prompt.
5.  **Generation:** This augmented prompt is sent to a powerful Large Language Model (LLM) like Google's Gemini or Groq's Llama.
6.  **Response:** The LLM generates a factual, context-aware answer, which is streamed back to the user.

---

## ✨ Key Features

-   **Private Knowledge Base:** Upload your documents (PDF, TXT, etc.) to create a secure, private context for the AI.
-   **Contextual Q&A:** Ask complex questions and receive answers grounded in your data, complete with sources.
-   **Multi-LLM Support:** Dynamically switches between LLM providers like Google AI (Gemini) and Groq for cost/speed optimization and redundancy.
-   **RESTful Backend:** A robust Django API manages all business logic, user authentication, and AI orchestration.
-   **Containerized Environment:** Fully containerized with Docker for development and production parity, ensuring "it works on my machine" means it works in the cloud.

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React | A responsive and modern Single Page Application (SPA) for chat and document management. |
| **Backend** | Django, Django Rest Framework | Secure and scalable RESTful API for business logic and AI orchestration. |
| **AI/ML** | Google AI (Gemini), Groq (Llama) | Multiple Large Language Model providers for text generation. |
| **Database** | Vector Database (e.g., Pinecone, FAISS) | Stores document embeddings for fast semantic search. |
| **Deployment** | Docker, GCP Cloud Run, Firebase Hosting | Containerized services deployed to a serverless environment for scalability. |
| **DevOps** | GitHub Actions, Semantic Release | Fully automated CI/CD for versioning and deployment. |

---

## 🛠️ Getting Started: Local Development

The application is containerized for easy setup.

### Prerequisites
* Docker & Docker Compose
* Git
* API keys for Google AI and/or Groq.

### 1. Clone the Repository
```bash
git clone https://github.com/CidQueiroz/SenseiDB-Agent.git
cd SenseiDB-Agent
```

### 2. Configure Environment Variables

Create an `.env.deploy` file in the root directory.

**Key variables to set:**
-   `GCP_PROJECT_ID`: Your Google Cloud Project ID.
-   `GOOGLE_API_KEY`: Your API key for Gemini.
-   `GROQ_API_KEY`: Your API key for Groq.
-   `SECRET_KEY`: A Django secret key.

### 3. Build and Run the Application

```bash
docker-compose up --build
```
This command will start the Django backend and the React frontend.

-   **Backend API** will be available at `http://localhost:8000`.
-   **Frontend App** will be available at `http://localhost:8501`.

---

## 🚀 CI/CD Pipeline

The project features a fully automated CI/CD pipeline using GitHub Actions:

1.  **On Push to `main`:**
    - A `release` workflow validates the code and uses `semantic-release` to create a version tag based on commit messages.
2.  **On New Release:**
    - A `deploy` workflow is triggered.
    - It builds and pushes a Docker image of the backend to **Google Artifact Registry**.
    - It deploys this new image to **GCP Cloud Run**.
    - It builds and deploys the React frontend to **Firebase Hosting**.
