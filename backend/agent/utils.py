import os
from typing import List, Dict, Optional, Tuple
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from groq import Groq
import numpy as np
import requests
import google.auth
import traceback
import sys


# Exceções personalizadas para erros de chave de API
class InvalidGroqApiKey(Exception):
    pass


class InvalidGoogleApiKey(Exception):
    pass

class QuotaExceededError(Exception):
    pass

# ============================================ 
# CONFIGURAÇÃO E INICIALIZAÇÃO
# ============================================ 

# Configuração Firebase
def init_firebase() -> Optional[firestore.Client]:
    """
    Inicializa o Firebase Admin SDK, se ainda não tiver sido inicializado.
    Retorna uma instância do cliente Firestore.
    """
    if not firebase_admin._apps:
        try:
            print("🔑 Tentando inicializar Firebase...")
            # Em um ambiente Google Cloud (como Cloud Run), as credenciais são detectadas
            # automaticamente a partir da conta de serviço do ambiente.
            firebase_admin.initialize_app()

            # Configura o Google AI SDK (se a chave estiver no ambiente)
            google_api_key = os.environ.get("GOOGLE_API_KEY")
            if google_api_key:
                genai.configure(api_key=google_api_key)
                print("✅ Google AI SDK configurado com API Key do ambiente.")

            print("✅ Firebase inicializado com sucesso.")
        except Exception as e:
            print(f"❌ Erro fatal ao inicializar o Firebase: {e}")
            traceback.print_exc()
            raise
    
    return firestore.client()


def carregar_persona(nome_arquivo: str) -> str:
    """Lê o arquivo de texto da persona e retorna o conteúdo."""
    # Ajuste o caminho base conforme sua estrutura de pastas no servidor
    base_path = os.path.join(os.path.dirname(__file__), 'personas')
    file_path = os.path.join(base_path, nome_arquivo)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Erro: Persona {nome_arquivo} não encontrada. Usando padrão.")
        # Fallback para o Mentor se o arquivo falhar
        return "VOCÊ É: Um assistente útil..."

# ID do usuário admin
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID", "default_admin_id")
print(ADMIN_USER_ID)

# ============================================ 
# PROMPT SYSTEM
# ============================================ 
def gerar_prompt_sistema(contextos: List[str], user_id: str = None) -> str:
    # --- DEBUG LOG START ---
    print(f"\n[DEBUG RAG] === INICIO GERACAO PROMPT ===", file=sys.stderr)
    print(f"[DEBUG RAG] User ID recebido: '{user_id}'", file=sys.stderr)
    # --- DEBUG LOG END ---
    """
    Seleciona e carrega a persona correta baseada no usuário,
    injetando o contexto do RAG.
    """   
    # 1. Lógica de Seleção de Papel
    if user_id and (user_id.strip() == "sensei@cdkteck.com.br" or user_id.strip() == "w4qlo3Q5v8USDkQwuzCzPKL75Au2"):
        print(f"[DEBUG RAG] Condição IF atendida: Selecionando RECEPCIONISTA", file=sys.stderr)
        arquivo_persona = "recepcionista_vitalita.txt"
    else:
        print(f"[DEBUG RAG] Condição ELSE (Padrão): Selecionando MENTOR", file=sys.stderr)
        arquivo_persona = "mentor_sensei.txt"

    # 2. Carregamento do Texto
    prompt_base = carregar_persona(arquivo_persona)

    # --- DEBUG LOG CONTENT ---
    print(f"[DEBUG RAG] Arquivo carregado: {arquivo_persona}", file=sys.stderr)
    print(f"[DEBUG RAG] Primeiros 200 chars do prompt carregado:\n{prompt_base[:200]}", file=sys.stderr)
    print(f"[DEBUG RAG] =================================\n", file=sys.stderr)
    # --- DEBUG LOG END ---

    # 3. Injeção de Contexto (RAG)
    if contextos:
        contexto_formatado = "\n".join([f"• {ctx}" for ctx in contextos])
        prompt_final = f"""{prompt_base}

**CONTEXTO RELEVANTE (RAG):**
{contexto_formatado}"""
    else:
        prompt_final = prompt_base

    return prompt_final


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
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={api_key}"
        payload = {"model": "embedding-001", "content": {"parts": [{"text": query}]}}
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


def salvar_contexto_usuario(user_id: str, contexto_texto: str, google_api_key: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Salva novo contexto com embedding na collection 'inteligencia_critica'"""
    try:
        print("\n--- INICIANDO salvar_contexto_usuario ---")
        
        # Passo 1: Gera o embedding
        print("LOG: Gerando embedding para o texto...")
        # Prioriza a chave do usuário, depois a do ambiente
        api_key_for_embedding = google_api_key or os.environ.get("GOOGLE_API_KEY")
        
        if not api_key_for_embedding:
            raise InvalidGoogleApiKey("Chave da API do Google não encontrada para gerar embedding.")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={api_key_for_embedding}"
        payload = {
            "model": "embedding-001", 
            "content": {"parts": [{"text": contexto_texto}]}
        }
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
        response.raise_for_status()
        embedding = response.json()['embedding']['values']
        print("LOG: Embedding gerado com sucesso.")

        # Passo 2: Salva no Firestore na collection 'inteligencia_critica'
        print("LOG: Inicializando cliente Firebase...")
        db = init_firebase()
        print(f"LOG: Cliente Firebase inicializado: {db}")
        
        print("LOG: Acessando collection 'users'...")
        users_collection = db.collection('users')
        
        print(f"LOG: Acessando document '{user_id}'...")
        user_doc = users_collection.document(user_id)
        
        print("LOG: Acessando sub-collection 'inteligencia_critica'...")
        contexts_collection = user_doc.collection('inteligencia_critica')
        
        print("LOG: Tentando executar .add() no Firestore...")
        contexts_collection.add({
            'contexto': contexto_texto,
            'embedding': embedding,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        print(f"LOG: ✅ Contexto salvo com sucesso no Firestore (inteligencia_critica) para o user_id: {user_id}")
        
        print("--- FIM salvar_contexto_usuario ---\\n")
        return True, None
        
    except Exception as e:
        error_message = f"Erro detalhado: {e}"
        print(f"❌ Erro em salvar_contexto_usuario: {error_message}")
        traceback.print_exc()
        print("--- FIM salvar_contexto_usuario (COM ERRO) ---\\n")
        return False, error_message


# ============================================ 
# FUNÇÕES DE GERAÇÃO DE RESPOSTA
# ============================================ 

def get_owner_google_keys() -> List[str]:
    """Lê as chaves de API do proprietário das variáveis de ambiente."""
    keys = []
    i = 1
    while True:
        key = os.environ.get(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            # Procura no máximo até 20 chaves para não entrar em loop infinito
            if i > 20: 
                break
            # Continua verificando para o caso de haver um buraco na numeração (ex: 1, 2, 4)
            i += 1
            if i > 20: # Checagem dupla
                 break

    print(f"🔑 Encontradas {len(keys)} chaves de API do proprietário.")
    return keys

def gerar_resposta_groq(prompt: str, api_key: str, model: str = "llama-3.1-8b-instant") -> Tuple[Optional[str], Optional[str]]:
    """Gera resposta usando Groq via API REST (mais estável que o SDK)"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        
        # Verifica erros de autenticação
        if response.status_code == 401:
            raise InvalidGroqApiKey("Chave da API Groq inválida.")
        
        # Verifica outros erros
        if response.status_code != 200:
            erro_msg = f"Erro {response.status_code}: {response.text}"
            print(f"❌ Erro na API Groq: {erro_msg}")
            return None, erro_msg
        
        # Extrai a resposta
        response_json = response.json()
        resposta = response_json['choices'][0]['message']['content']
        
        return resposta, None
        
    except InvalidGroqApiKey as e:
        raise e
    except requests.exceptions.Timeout:
        erro_msg = "Timeout na API do Groq"
        print(f"❌ {erro_msg}")
        return None, erro_msg
    except Exception as e:
        erro_msg = str(e)
        print(f"❌ Erro detalhado em gerar_resposta_groq: {erro_msg}")
        
        # Verifica se é erro de API key inválida
        if "invalid" in erro_msg.lower() and ("api" in erro_msg.lower() or "key" in erro_msg.lower()):
            raise InvalidGroqApiKey("Chave da API Groq inválida.")
        
        return None, erro_msg


def gerar_resposta_google(prompt: str, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash") -> Tuple[Optional[str], Optional[str]]:
    """Gera resposta usando Google AI, com chave de API opcional."""
    try:
        # Se uma chave de API específica do usuário for fornecida, use a API REST para thread-safety
        if api_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            response = requests.post(url, json=payload, timeout=45)
            
            # Verifica erros de autenticação e quota
            if response.status_code == 400 and "API key not valid" in response.text:
                raise InvalidGoogleApiKey("Chave da API Google inválida.")
            if response.status_code == 429:
                 raise QuotaExceededError(f"Quota excedida para a chave: ...{api_key[-4:]}")

            if response.status_code != 200:
                return None, f"Erro na API do Google: {response.status_code} - {response.text}"

            response_json = response.json()
            candidates = response_json.get('candidates', [])
            if not candidates:
                # Pode ser uma resposta bloqueada por segurança
                prompt_feedback = response_json.get('promptFeedback', {})
                block_reason = prompt_feedback.get('blockReason')
                if block_reason:
                    return f"A resposta foi bloqueada por segurança: {block_reason}", None
                return None, "Resposta da API do Google não contém 'candidates'."
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                return None, "Resposta da API do Google não contém 'parts'."
                
            return parts[0].get('text'), None

        # Caso contrário, use o SDK do genai configurado globalmente
        else:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text, None
            
    except (InvalidGoogleApiKey, QuotaExceededError) as e:
        raise e
    except Exception as e:
        error_str = str(e)
        if "400" in error_str and "API key not valid" in error_str:
            raise InvalidGoogleApiKey("Chave da API Google inválida.")
        if "429" in error_str and "quota" in error_str.lower():
            raise QuotaExceededError(error_str)
            
        print(f"❌ Erro detalhado em gerar_resposta_google: {error_str}")
        return None, error_str


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
    Processa a query do usuário com RAG e IA, com sistema de rotação de chaves.
    """ 
    try:
        print(f"🔍 Buscando contextos para user_id: {user_id}")
        contextos_relevantes = buscar_contextos_relevantes(user_id, query, top_k=5)
        
        if contextos_relevantes:
            print(f"✅ {len(contextos_relevantes)} contextos encontrados")
        else:
            print("⚠️ Nenhum contexto encontrado")
        
        prompt_sistema = gerar_prompt_sistema(contextos_relevantes, user_id)
        prompt_final = f"""{prompt_sistema}\n\n---\n**PERGUNTA/MENSAGEM DO USUÁRIO:**\n{query}\n\n---\n\n**INSTRUÇÕES FINAIS:**\n- Responda em português do Brasil\n- Seja conciso mas completo\n- Use markdown para formatação (negrito, listas, etc)\n- Termine com uma pergunta reflexiva ou próximo passo claro"""
        
        resposta_ia = None
        erro = None
        ia_usada = None
        erros_acumulados = []

        # 1️⃣ Tenta a chave Groq do usuário
        if groq_api_key:
            print("🔑 Usuário tentando Groq (chave própria)")
            try:
                resposta_ia, erro = gerar_resposta_groq(prompt_final, groq_api_key)
                if resposta_ia:
                    ia_usada = "groq"
                else:
                    erros_acumulados.append(f"Groq (usuário): {erro}")
            except InvalidGroqApiKey as e:
                erros_acumulados.append(f"Groq (usuário): {str(e)}")
        
        # 2️⃣ Tenta a chave Google do usuário
        if not resposta_ia and google_api_key:
            print("🔑 Usuário tentando Google AI (chave própria)")
            try:
                resposta_ia, erro = gerar_resposta_google(prompt_final, api_key=google_api_key)
                if resposta_ia:
                    ia_usada = "google_user"
                else:
                    erros_acumulados.append(f"Google (usuário): {erro}")
            except (InvalidGoogleApiKey, QuotaExceededError) as e:
                erros_acumulados.append(f"Google (usuário): {str(e)}")

        # 3️⃣ Fallback: Rotação de chaves do proprietário
        if not resposta_ia:
            print("🌐 FALLBACK: Tentando chaves do proprietário em rotação")
            owner_keys = get_owner_google_keys()
            if not owner_keys:
                print("⚠️ Nenhuma chave de API do proprietário encontrada no ambiente.")
                erros_acumulados.append("Nenhuma chave de API do proprietário configurada no backend.")
            else:
                for i, key in enumerate(owner_keys):
                    print(f"🔑 Tentando chave do proprietário nº {i+1}")
                    try:
                        resposta_ia, erro = gerar_resposta_google(prompt_final, api_key=key)
                        if resposta_ia:
                            ia_usada = f"google_owner_key_{i+1}"
                            print(f"✅ Resposta gerada com a chave do proprietário nº {i+1}")
                            break
                        else:
                            erros_acumulados.append(f"Proprietário (chave {i+1}): {erro}")
                    except QuotaExceededError as e:
                        print(f"⚠️ Quota excedida para a chave do proprietário nº {i+1}")
                        erros_acumulados.append(f"Proprietário (chave {i+1}): {e}")
                        continue
                    except InvalidGoogleApiKey as e:
                        print(f"❌ Chave do proprietário nº {i+1} é inválida.")
                        erros_acumulados.append(f"Proprietário (chave {i+1}): {e}")
                        continue

        # Se todas as tentativas falharem, lança a exceção que será pega pela view
        if not resposta_ia:
            # Se o último erro foi de quota, lança QuotaExceededError para a view
            if any("quota" in str(e).lower() for e in erros_acumulados):
                 raise QuotaExceededError("Todas as chaves de API disponíveis atingiram o limite de quota. Por favor, insira sua própria chave para continuar.")

            erro_completo = " | ".join(erros_acumulados) if erros_acumulados else "Nenhuma resposta pôde ser gerada."
            raise Exception(f"Todas as IAs falharam: {erro_completo}")

        print(f"✅ Resposta final gerada com: {ia_usada.upper()}")
        
        return {
            "resposta": resposta_ia,
            "ia_usada": ia_usada,
            "num_contextos": len(contextos_relevantes)
        }
    
    except (InvalidGroqApiKey, InvalidGoogleApiKey, QuotaExceededError) as e:
        raise e
    except Exception as e:
        print(f"❌ Erro ao processar query: {e}")
        raise