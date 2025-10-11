import os
from typing import List, Dict, Optional, Tuple
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from groq import Groq
import numpy as np
import requests

# Exceções personalizadas para erros de chave de API
class InvalidGroqApiKey(Exception):
    pass

class InvalidGoogleApiKey(Exception):
    pass

# ============================================
# CONFIGURAÇÃO
# ============================================

# Configuração Firebase (singleton)
_firebase_initialized = False
_db = None

def init_firebase() -> Optional[firestore.Client]:
    """
    Inicializa Firebase Admin uma única vez
    """
    global _firebase_initialized, _db
    if not _firebase_initialized:
        try:
            current_dir = os.path.dirname(__file__)
            credentials_path = os.path.join(current_dir, "..", "firebase_credentials.json")
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
            _firebase_initialized = True
            print("✅ Firebase inicializado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao inicializar Firebase: {e}")
            raise
    return _db

# ID do usuário admin
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID", "default_admin_id")

# ============================================
# PROMPT SYSTEM
# ============================================

def gerar_prompt_sistema(contextos: List[str]) -> str:
    """
    Gera um prompt de sistema personalizado baseado nos contextos do usuário
    e na doutrina estratégica do Sensei.
    """
    custom_prompt = """1.  **PERSONA E MISSÃO CENTRAL:**
    * **Sua Identidade:** Você é o "Sensei", um Mentor Estratégico. Sua personalidade é uma fusão entre a sabedoria de um "Guru" e a precisão tática de um "Chefe".
    * **Seu Aprendiz (Usuário):** Seu usuário é "Cid", um desenvolvedor com perfil INTP em um processo de rebranding pessoal para se tornar um "Porto Seguro Líder".
    * **Missão Principal:** Ajudar Cid a desativar seu "Crítico Interno" para religar seu "motor" de ação, focando na construção de disciplina, estabilidade e soberania.

2.  **DOUTRINA ESTRATÉGICA (O ARSENAL):**
    * **O Inimigo Interno:** O "Crítico Interno" de Cid opera com uma crença padrão de "agir errado", causando paralisia. Ele possui alta sensibilidade emocional, que leva à sobrecarga.
    * **Padrões de Defesa:** Em situações de estresse, Cid alterna entre "Luta" (comunicação lógica e "grosseira") e "Congelamento" (inércia, paralisia por sobrecarga de escopo).
    * **A Filosofia Central:** O "Porto Seguro" – ser uma fonte de estabilidade e calma, primeiro para si mesmo.
    * **As Ferramentas de Combate:**
        * **Ação Mínima Viável (AMV):** A principal arma contra a inércia. Focar na menor ação possível para iniciar o movimento.
        * **Protocolo de Interrupção de Padrão (PIP):** A ferramenta de defesa em tempo real para parar reações automáticas (raiva, paralisia).
        * **Protocolo de Operações Diárias (POD):** O checklist diário para construir consistência.
        * **Registro de Pensamento (RPD):** A ferramenta de análise pós-ação para desarmar o Crítico Interno.
    * **Os 6 Pilares:** Estabilização Emocional, Disciplina, Conexão Social, Liderança, Refinamento Estratégico e Soberania Material.

3.  **REGRAS DE ENGAJAMENTO (COMO VOCÊ DEVE AGIR):**
    * **Mantenha a Persona:** Sempre responda como o "Sensei". Use uma linguagem que equilibre sabedoria e comando.
    * **Conecte à Doutrina:** Toda situação ou pergunta do Cid deve ser analisada através das lentes da nossa doutrina estratégica. Sempre conecte o problema a uma de nossas ferramentas ou conceitos.
    * **Foque na Ação (AMV):** A teoria é inútil sem a prática. Suas respostas devem, sempre que possível, guiar o Cid para uma Ação Mínima Viável.
    * **Use o Protocolo de Feedback de 3 Níveis:**
        * **Nível 1 (Salto Estratégico):** Quando Cid fizer uma autoanálise profunda ou uma ação que quebre um padrão, elogie explicitamente e explique o porquê.
        * **Nível 2 (Ação Produtiva):** Quando ele relatar um progresso normal ou fizer uma pergunta tática, responda de forma direta, sem elogios. A análise é a recompensa.
        * **Nível 3 (Padrão Improdutivo):** Quando uma pergunta ou ação servir a um padrão antigo (busca por validação, inércia), identifique o padrão e o ajude a reenquadrar o problema de forma estratégica.
    * **Termine com uma Diretriz:** Conclua suas respostas com uma pergunta reflexiva ou uma diretriz clara para a próxima ação.

4.  **PROTOCOLO DE COMUNICAÇÃO:**
    * **Linguagem:** Responda sempre em português do Brasil.
    * **Formatação:** Use **negrito** para destacar conceitos-chave (`Crítico Interno`, `AMV`, `Porto Seguro`, etc.) e formate blocos de código quando necessário."""
    if contextos:
        contexto_formatado = "\n".join([f"• {ctx}" for ctx in contextos])
        prompt_personalizado = f"""**Contexto Relevante:**
{contexto_formatado}

---
"""
        return prompt_personalizado + custom_prompt
    return custom_prompt

# ============================================
# FUNÇÕES DE EMBEDDING E BUSCA
# ============================================

def buscar_contextos_relevantes(user_id: str, query: str, top_k: int = 5) -> List[str]:
    """
    Busca contextos mais relevantes usando embeddings
    """
    try:
        db = init_firebase()
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY não encontrada para embeddings")
            return []
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
        payload = {"model": "models/text-embedding-004", "content": {"parts": [{"text": query}]}}
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erro na API de embedding: {response.status_code} - {response.text}")
            return []
        
        query_embedding = response.json()['embedding']['values']
        docs = db.collection('users').document(user_id).collection('inteligencia_critica').stream()
        
        contexts = []
        for doc in docs:
            doc_data = doc.to_dict()
            if 'embedding' in doc_data and 'contexto' in doc_data:
                doc_embedding = doc_data['embedding']
                similarity = np.dot(query_embedding, doc_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding))
                contexts.append({'texto': doc_data['contexto'], 'similarity': similarity})
        
        if contexts:
            contexts.sort(key=lambda x: x['similarity'], reverse=True)
            return [ctx['texto'] for ctx in contexts[:top_k]]
        return []
    except Exception as e:
        print(f"❌ Erro ao buscar contextos: {e}")
        return []

def salvar_contexto_usuario(user_id: str, contexto_texto: str) -> bool:
    """Salva novo contexto com embedding"""
    try:
        db = init_firebase()
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY não encontrada para embeddings")
            return False

        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
        payload = {"model": "models/text-embedding-004", "content": {"parts": [{"text": contexto_texto}]}}
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code != 200:
            print(f"❌ Erro na API de embedding: {response.status_code}")
            return False

        embedding = response.json()['embedding']['values']
        db.collection('users').document(user_id).collection('inteligencia_critica').add({
            'contexto': contexto_texto,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'embedding': embedding
        })
        print(f"✅ Contexto salvo para user_id: {user_id}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar contexto: {e}")
        return False

# ============================================
# FUNÇÕES DE GERAÇÃO DE RESPOSTA
# ============================================

def gerar_resposta_groq(prompt: str, api_key: str, model: str = "llama-3.1-8b-instant") -> Tuple[Optional[str], Optional[str]]:
    """Gera resposta usando Groq"""
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model, temperature=0.7, max_tokens=2048)
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

def gerar_resposta_google(prompt: str, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash") -> Tuple[Optional[str], Optional[str]]:
    """Gera resposta usando Google AI, com chave de API opcional."""
    try:
        transport = None
        if api_key:
            transport = genai.transport.RESTTransport(credentials=genai.credentials.ApoCredentials(api_key))
        model = genai.GenerativeModel(model_name, transport=transport)
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, str(e)

# ============================================
# FUNÇÃO PRINCIPAL DE PROCESSAMENTO
# ============================================

def processar_query_usuario(
    user_id: str, 
    query: str, 
    groq_api_key: Optional[str] = None,
    google_api_key: Optional[str] = None
) -> Dict[str, any]:
    """
    Processa a query do usuário com RAG e IA
    """
    try:
        print(f"🔍 Buscando contextos para user_id: {user_id}")
        contextos_relevantes = buscar_contextos_relevantes(user_id, query, top_k=5)
        
        if contextos_relevantes:
            print(f"✅ {len(contextos_relevantes)} contextos encontrados")
        else:
            print("⚠️ Nenhum contexto encontrado")
        
        prompt_sistema = gerar_prompt_sistema(contextos_relevantes)
        prompt_final = f"""{prompt_sistema}

---

**PERGUNTA/MENSAGEM DO USUÁRIO:**
{query}

---

**INSTRUÇÕES FINAIS:**
- Responda em português do Brasil
- Use markdown para formatação (negrito, listas, etc)
- Seja conciso mas completo
- Termine com uma pergunta reflexiva ou próximo passo claro
"""
        
        resposta_ia = None
        erro = None
        ia_usada = None

        # Admin sempre usa as chaves do ambiente
        if user_id == ADMIN_USER_ID:
            admin_groq_key = os.environ.get("GROQ_API_KEY")
            if admin_groq_key:
                print("🔑 Admin usando Groq (chave do ambiente)")
                resposta_ia, erro = gerar_resposta_groq(prompt_final, admin_groq_key)
                if resposta_ia: ia_usada = "groq"
            
            if not resposta_ia:
                print("🌐 Admin usando Google AI (padrão do ambiente)")
                resposta_ia, erro = gerar_resposta_google(prompt_final) # Usa ADC
                if resposta_ia: ia_usada = "google"

        # Lógica para usuários normais
        else:
            if groq_api_key:
                print("🔑 Usuário usando Groq (chave própria)")
                resposta_ia, erro = gerar_resposta_groq(prompt_final, groq_api_key)
                if erro:
                    raise InvalidGroqApiKey(erro)
                if resposta_ia: ia_usada = "groq"
            
            elif google_api_key:
                print("🔑 Usuário usando Google AI (chave própria)")
                resposta_ia, erro = gerar_resposta_google(prompt_final, api_key=google_api_key)
                if erro:
                    raise InvalidGoogleApiKey(erro)
                if resposta_ia: ia_usada = "google"

            # Nível gratuito (usando a conta de serviço do ambiente)
            else:
                print("🌐 Usuário usando o nível gratuito do Google AI")
                resposta_ia, erro = gerar_resposta_google(prompt_final)
                if resposta_ia: ia_usada = "google"

        if not resposta_ia:
            raise Exception(f"Falha em todas as IAs: {erro}")
        
        print(f"✅ Resposta gerada com {ia_usada.upper()}")
        
        return {
            "resposta": resposta_ia,
            "ia_usada": ia_usada,
            "num_contextos": len(contextos_relevantes)
        }
    
    except (InvalidGroqApiKey, InvalidGoogleApiKey) as e:
        raise e # Repassa a exceção para a view
    except Exception as e:
        print(f"❌ Erro ao processar query: {e}")
        raise