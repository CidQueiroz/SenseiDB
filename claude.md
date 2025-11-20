# SenseiDB - Identidade do Projeto para Gemini

## 1. Ideologia e Filosofia

- **Missão:** Ser um mentor estratégico pessoal com IA, que se adapta ao usuário através de uma base de conhecimento privada e contextualmente relevante (RAG).

- **Filosofia de Design:**
    - **Backend Robusto:** A lógica de negócio é centralizada em uma API REST construída com Django, priorizando segurança, escalabilidade e um ecossistema maduro.
    - **Frontend Leve:** A interface é intencionalmente construída com HTML/CSS/JS "vanilla" para garantir performance máxima, universalidade e evitar a sobrecarga de frameworks.
    - **Paridade Dev/Prod:** O Docker é a fundação de todo o ciclo de vida da aplicação. O ambiente de desenvolvimento, definido no `docker-compose.yml`, espelha o ambiente de produção para eliminar surpresas.
    - **Automação Total (CI/CD):** O versionamento é um processo automatizado e determinístico, baseado em `semantic-release`. Commits geram versões, não pessoas.

## 2. Arquitetura e Stack de Tecnologias

Este projeto opera em uma arquitetura **polyrepo**, sendo um repositório independente que pode ser orquestrado localmente com outros.

### Serviços

A aplicação é dividida em dois serviços principais, orquestrados pelo `docker-compose.yml`:
1.  `backend`: A API Django.
2.  `frontend`: O cliente web estático, servido por Nginx.

### Tecnologias e Ferramentas (O "Quê" e o "Porquê")

- **Backend:**
    - **Python/Django/DRF:** Escolhido pela robustez e ecossistema para a construção da API.
    - **Gunicorn:** Servidor WSGI padrão para produção, definido no `Dockerfile`.

- **Frontend:**
    - **HTML/CSS/JS (Vanilla):** Escolhido para simplicidade e performance.
    - **Nginx:** Servidor web de alta performance para servir os arquivos estáticos.

- **Dados & IA:**
    - **Firebase (Auth & Firestore):** Utilizado como BaaS (Backend as a Service) para autenticação e armazenamento de dados NoSQL, escolhido pela facilidade de integração e escalabilidade.
    - **Groq & Google AI:** Múltiplos provedores de LLM para otimização de custo/velocidade e redundância.

- **Infraestrutura & DevOps:**
    - **Docker & Docker Compose:** Ferramenta central para containerização e orquestração do ambiente de desenvolvimento com live-reload.
    - **Node.js/npm:** Utilizado **exclusivamente** como um executor de tarefas para as ferramentas de DevOps (`semantic-release`, `commitizen`). Não faz parte da aplicação em si.
    - **Semantic Release:** Orquestra o versionamento automático a partir de Conventional Commits. A configuração reside em `.releaserc.json`.
    - **GitHub Actions:** Plataforma de CI/CD que automatiza a execução do `semantic-release`.

## 3. Paradigmas de Desenvolvimento

- **Commits:** O padrão **Conventional Commits** é mandatório, pois alimenta diretamente o versionamento. O uso de `npm run cz` é o método preferencial para garantir a conformidade.
- **Ambiente de Execução:** O ambiente de desenvolvimento é "Docker-first". `docker-compose up` é o ponto de entrada canônico.
- **Ambiente de Edição:** Ambientes virtuais Python (`venv`) são mantidos localmente com o único propósito de dar suporte às ferramentas do editor de código (linting, intellisense), não para executar a aplicação.