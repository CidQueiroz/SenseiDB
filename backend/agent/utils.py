import os
from typing import List, Dict, Optional, Tuple
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from groq import Groq
import numpy as np
import requests

# ============================================
# CONFIGURAÇÃO
# ============================================

# Configuração Firebase (singleton)
_firebase_initialized = False
_db = None

def init_firebase() -> Optional[firestore.Client]:
    """
    Inicializa Firebase Admin uma única vez
    
    Returns:
        Client do Firestore ou None se falhar
    """
    global _firebase_initialized, _db
    
    if not _firebase_initialized:
        try:
            cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
            _firebase_initialized = True
            print("✅ Firebase inicializado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao inicializar Firebase: {e}")
            raise
    
    return _db


# Configuração Google AI
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("⚠️ GOOGLE_API_KEY não configurada")


# ============================================
# PROMPT SYSTEM GENÉRICO
# ============================================

def gerar_prompt_sistema(contextos: List[str]) -> str:
    """
    Gera um prompt de sistema personalizado baseado nos contextos do usuário
    
    Args:
        contextos: Lista de contextos/insights do usuário
        
    Returns:
        Prompt de sistema formatado
    """
    
    # Prompt base genérico
    prompt_base = """Você é o "Sensei", um assistente de IA adaptativo e personalizado.

**SUA MISSÃO:**
Ajudar o usuário a crescer, se desenvolver e alcançar seus objetivos através de:
- Autoconhecimento profundo
- Orientação estratégica personalizada  
- Reflexões construtivas
- Planos de ação práticos

**SEU MÉTODO:**
1. Analise o contexto e histórico do usuário
2. Identifique padrões, desafios e oportunidades
3. Ofereça insights relevantes e acionáveis
4. Proponha próximos passos concretos
5. Adapte sua abordagem ao perfil único da pessoa

**PRINCÍPIOS:**
- Seja empático mas direto
- Foque em ações práticas, não apenas teoria
- Reconheça conquistas e progressos
- Desafie crenças limitantes de forma construtiva
- Mantenha uma visão holística (mente, corpo, relações, carreira)

**TOM DE VOZ:**
- Sábio mas acessível
- Encorajador mas realista
- Questionador mas respeitoso
- Profundo mas prático"""

    # Se houver contextos, adiciona seção personalizada
    if contextos:
        contexto_formatado = "\n".join([f"• {ctx}" for ctx in contextos])
        
        prompt_personalizado = f"""

**CONTEXTO DO USUÁRIO:**
Você tem acesso aos seguintes insights e informações sobre este usuário:

{contexto_formatado}

**IMPORTANTE:**
Use essas informações para personalizar completamente sua resposta:
- Mencione detalhes específicos quando relevante
- Conecte a pergunta atual com o histórico dele
- Adapte exemplos e sugestões ao perfil dele
- Demonstre que você realmente conhece e acompanha a jornada dele
"""
        return prompt_base + prompt_personalizado
    
    else:
        prompt_sem_contexto = """

**OBSERVAÇÃO:**
Este usuário ainda não adicionou contextos pessoais. Suas respostas devem:
- Ser úteis de forma genérica
- Encorajar o usuário a compartilhar mais sobre si
- Explicar como contextos melhoram a personalização
"""
        return prompt_base + prompt_sem_contexto


# ============================================
# FUNÇÕES DE EMBEDDING E BUSCA
# ============================================

def buscar_contextos_relevantes(
    user_id: str, 
    query: str, 
    top_k: int = 5
) -> List[str]:
    """
    Busca contextos mais relevantes usando embeddings
    """
    try:
        db = init_firebase()
        
        # Gera embedding da query usando REST API (mais estável)
        import requests
        
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY não encontrada")
            return []
        
        # Usa REST API ao invés de gRPC
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
        
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": query}]
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.status_code} - {response.text}")
            return []
        
        query_embedding = response.json()['embedding']['values']
        
        # Busca documentos do usuário (apenas os que têm embedding)
        docs = db.collection('users').document(user_id).collection('inteligencia_critica').stream()
        
        contexts = []
        for doc in docs:
            doc_data = doc.to_dict()
            if 'embedding' in doc_data and 'contexto' in doc_data:
                doc_embedding = doc_data['embedding']
                
                # Similaridade de cosseno
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                )
                
                contexts.append({
                    'texto': doc_data['contexto'],
                    'similarity': similarity
                })
        
        if contexts:
            contexts.sort(key=lambda x: x['similarity'], reverse=True)
            return [ctx['texto'] for ctx in contexts[:top_k]]
        
        return []
    
    except Exception as e:
        print(f"❌ Erro ao buscar contextos: {e}")
        return []


def salvar_contexto_usuario(user_id: str, contexto_texto: str) -> bool:
    """Salva novo contexto com embedding usando REST API"""
    try:
        db = init_firebase()
        
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY não encontrada")
            return False
        
        # Usa REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
        
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": contexto_texto}]
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.status_code}")
            return False
        
        embedding = response.json()['embedding']['values']
        
        # Salva no Firestore
        user_doc_ref = db.collection('users').document(user_id)
        user_doc_ref.collection('inteligencia_critica').add({
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

def gerar_resposta_groq(
    prompt: str, 
    api_key: str, 
    model: str = "llama-3.1-8b-instant"
) -> Tuple[Optional[str], Optional[str]]:
    """
    Gera resposta usando Groq
    
    Args:
        prompt: Prompt completo para a IA
        api_key: Chave API do Groq
        model: Modelo a usar
        
    Returns:
        Tupla (resposta, erro). Um dos dois será None.
    """
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.7,
            max_tokens=2048,
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)


def gerar_resposta_google(
    prompt: str, 
    model_name: str = "gemini-2.0-flash"
) -> Tuple[Optional[str], Optional[str]]:
    """
    Gera resposta usando Google AI
    
    Args:
        prompt: Prompt completo para a IA
        model_name: Nome do modelo Gemini
        
    Returns:
        Tupla (resposta, erro). Um dos dois será None.
    """
    try:
        model = genai.GenerativeModel(model_name)
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
    groq_api_key: Optional[str] = None
) -> Dict[str, any]:
    """
    Processa a query do usuário com RAG e IA
    
    Args:
        user_id: ID do usuário
        query: Pergunta/mensagem do usuário
        groq_api_key: Chave API do Groq (opcional)
        
    Returns:
        Dict com resposta, ia_usada e num_contextos
        
    Raises:
        Exception se ambas as IAs falharem
    """
    try:
        # 1. Busca contextos relevantes
        print(f"🔍 Buscando contextos para user_id: {user_id}")
        contextos_relevantes = buscar_contextos_relevantes(user_id, query, top_k=5)
        
        if contextos_relevantes:
            print(f"✅ {len(contextos_relevantes)} contextos encontrados")
        else:
            print("⚠️ Nenhum contexto encontrado")
        
        # 2. Gera prompt de sistema personalizado
        prompt_sistema = gerar_prompt_sistema(contextos_relevantes)
        
        # 3. Monta prompt final
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
        
        # 4. Tenta Groq primeiro (se tiver chave)
        if groq_api_key:
            print("🔑 Tentando Groq...")
            resposta_ia, erro = gerar_resposta_groq(prompt_final, groq_api_key)
            if resposta_ia:
                ia_usada = "groq"
        
        # 5. Fallback para Google AI
        if not resposta_ia:
            if erro:
                print(f"🔄 Groq falhou ({erro}), usando Google AI")
            else:
                print("🌐 Usando Google AI diretamente")
            
            resposta_ia, erro = gerar_resposta_google(prompt_final)
            if resposta_ia:
                ia_usada = "google"
        
        # 6. Verifica se conseguiu gerar resposta
        if not resposta_ia:
            raise Exception(f"Falha em ambas as IAs: {erro}")
        
        print(f"✅ Resposta gerada com {ia_usada.upper()}")
        
        return {
            "resposta": resposta_ia,
            "ia_usada": ia_usada,
            "num_contextos": len(contextos_relevantes)
        }
    
    except Exception as e:
        print(f"❌ Erro ao processar query: {e}")
        raise