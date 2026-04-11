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
    Inicializa o Firebase Admin SDK com suporte a JSON e Base64 vindo do ambiente.
    Retorna uma instância do cliente Firestore.
    """
    if not firebase_admin._apps:
        try:
            print("🔑 Iniciando inicialização robusta do Firebase...")
            
            google_application_credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            
            if google_application_credentials_json:
                import json
                # Tenta carregar como JSON puro primeiro
                content = google_application_credentials_json.strip()
                
                # Se não começar com '{', pode ser Base64
                if not content.startswith('{'):
                    import base64
                    try:
                        decoded = base64.b64decode(content).decode('utf-8')
                        if decoded.strip().startswith('{'):
                            content = decoded
                            print("🛠️ Firebase: Credenciais Base64 decodificadas com sucesso.")
                    except Exception as b64e:
                        print(f"⚠️ Firebase: Falha ao tentar decodificar Base64: {b64e}")

                try:
                    cred_dict = json.loads(content)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase inicializado a partir de variável de ambiente (JSON/B64).")
                except json.JSONDecodeError as je:
                    print(f"❌ Firebase: Erro ao parsear JSON: {je}")
                    # Fallback para inicialização padrão sem argumentos
                    firebase_admin.initialize_app()
                    print("⚠️ Firebase inicializado com credenciais padrão (fallback) após erro de JSON.")
            else:
                # Caso onde não há variável de ambiente explícita
                firebase_admin.initialize_app()
                print("✅ Firebase inicializado com credenciais padrão do ambiente Google Cloud.")

        except Exception as e:
            print(f"❌ Erro Crítico ao inicializar o Firebase: {e}")
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
def gerar_prompt_sistema(contextos: List[str], role: str = 'mentor') -> str:
    """
    Seleciona e carrega a persona correta baseada no papel (role),
    injetando o contexto do RAG.
    """
    # 1. Mapeamento de Papéis para Arquivos
    mapa_personas = {
        'mentor': 'mentor_sensei.txt',
        'professor': 'professor.txt',
        'atendente': 'atendente.txt',
        'nutricionista': 'nutricionista.txt'
    }

    arquivo_persona = mapa_personas.get(role.lower(), 'mentor_sensei.txt')

    # 2. Carregamento do Texto
    prompt_base = carregar_persona(arquivo_persona)

    # 3. Injeção de Contexto (RAG)
    if contextos:
        contexto_formatado = "\n".join([f"• {ctx}" for ctx in contextos])
        prompt_final = f"""{prompt_base}

**CONTEXTO DOS DADOS DO USUÁRIO:**
{contexto_formatado}"""
    else:
        prompt_final = prompt_base

    return prompt_final


# ============================================ 
# FUNÇÕES DE EMBEDDING E BUSCA
# ============================================ 
def gerar_embedding_google(texto: str) -> List[float]:
    """
    Gera embedding usando Google AI com rotação de chaves.
    Tenta a chave principal (GOOGLE_API_KEY) e depois as do proprietário (1 a 10).
    """
    keys_to_try = []
    
    # 1. Tenta a chave principal do ambiente
    main_key = os.environ.get('GOOGLE_API_KEY')
    if main_key:
        keys_to_try.append(main_key)
        
    # 2. Adiciona as chaves de rotação do proprietário
    keys_to_try.extend(get_owner_google_keys())
    
    if not keys_to_try:
        raise InvalidGoogleApiKey("Nenhuma chave Google API encontrada para gerar embeddings.")

    last_error = None
    for i, api_key in enumerate(keys_to_try):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
            payload = {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": texto}]}}
            
            # print(f"🧠 Tentando gerar embedding com chave {i+1}...")
            response = requests.post(url, json=payload, timeout=20)
            
            if response.status_code == 200:
                print(f"✅ Embedding gerado com sucesso (Chave {i+1}).")
                return response.json()['embedding']['values']
            
            error_data = response.text
            if response.status_code == 429:
                print(f"⚠️ Chave {i+1} atingiu cota (429). Tentando próxima...")
                last_error = f"Quota Excedida: {error_data}"
            elif "API key not valid" in error_data:
                print(f"❌ Chave {i+1} inválida. Tentando próxima...")
                last_error = f"Chave Inválida: {error_data}"
            else:
                print(f"❓ Erro inesperado na chave {i+1} ({response.status_code}): {error_data}")
                last_error = f"Erro {response.status_code}: {error_data}"
                
        except Exception as e:
            print(f"⚠️ Erro ao tentar chave {i+1}: {e}")
            last_error = str(e)

    raise Exception(f"Falha total ao gerar embedding após tentar {len(keys_to_try)} chaves. Último erro: {last_error}")


def buscar_contextos_relevantes(user_id: str, query: str, top_k: int = 5, role: str = None) -> List[str]:
    """
    Busca contextos em fluxo duplo: 
    1. Privado (Usuário - inteligência_critica)
    2. Global (Papel - global_knowledge)
    """
    try:
        db = init_firebase()
        
        # Gera o embedding da busca com rotação robusta
        search_query = f"Contexto para {role}: {query}" if role else query
        print(f"🧠 Gerando embedding para busca: {search_query[:50]}...")
        
        try:
            query_embedding = gerar_embedding_google(search_query)
        except Exception as e:
            print(f"❌ Abortando RAG: Falha ao gerar embedding de busca: {e}")
            return []
        
        contexts = []

        # STREAM A: Privado (User)
        print(f"📡 Buscando Stream Privado (User: {user_id} | Collection: inteligencia_critica)")
        user_docs_ref = db.collection('users').document(user_id).collection('inteligencia_critica')
        user_docs = list(user_docs_ref.stream())
        
        print(f"📊 Documentos encontrados no Firestore (Privado): {len(user_docs)}")
        
        for doc in user_docs:
            data = doc.to_dict()
            if 'embedding' in data and 'contexto' in data:
                try:
                    similarity = np.dot(query_embedding, data['embedding']) / (np.linalg.norm(query_embedding) * np.linalg.norm(data['embedding']))
                    contexts.append({
                        'texto': data['contexto'], 
                        'similarity': similarity, 
                        'source': 'private',
                        'id': doc.id
                    })
                except Exception as sim_err:
                    print(f"⚠️ Erro ao calcular similaridade para doc {doc.id}: {sim_err}")
            else:
                missing = [f for f in ['embedding', 'contexto'] if f not in data]
                print(f"⚠️ Documento {doc.id} ignorado. Campos faltando: {missing}")

        # STREAM B: Global (Role)
        if role:
            print(f"🌍 Buscando Stream Global (Role: {role} | Collection: global_knowledge)")
            global_docs_ref = db.collection('global_knowledge').document(role.lower()).collection('concepts')
            global_docs = list(global_docs_ref.stream())
            print(f"📊 Documentos encontrados no Firestore (Global): {len(global_docs)}")
            
            for doc in global_docs:
                data = doc.to_dict()
                if 'embedding' in data and 'content' in data:
                    try:
                        similarity = np.dot(query_embedding, data['embedding']) / (np.linalg.norm(query_embedding) * np.linalg.norm(data['embedding']))
                        contexts.append({
                            'texto': data['content'], 
                            'similarity': similarity, 
                            'source': 'global',
                            'id': doc.id
                        })
                    except Exception as sim_err:
                        print(f"⚠️ Erro no cálculo global doc {doc.id}: {sim_err}")

        if contexts:
            # Ordena por similaridade e pega os top_k
            contexts.sort(key=lambda x: x['similarity'], reverse=True)
            top_score = contexts[0]['similarity']
            print(f"🎯 Melhor similaridade encontrada: {top_score:.4f}")
            
            final_selection = [ctx['texto'] for ctx in contexts[:top_k]]
            print(f"📦 Selecionados {len(final_selection)} contextos mais relevantes.")
            return final_selection
        
        print("⚠️ Busca finalizada, mas nenhum contexto foi acumulado.")
        return []
    except Exception as e:
        print(f"❌ Erro Crítico no Dual-Stream RAG: {e}")
        traceback.print_exc()
        return []


def salvar_contexto_usuario(user_id: str, contexto_texto: str, google_api_key: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Salva novo contexto com embedding na collection 'inteligencia_critica'"""
    try:
        print("\n--- INICIANDO salvar_contexto_usuario ---")
        
        # Passo 1: Gera o embedding com rotação
        print("LOG: Gerando embedding para o arquivo/contexto...")
        try:
            embedding = gerar_embedding_google(contexto_texto)
            print("LOG: Embedding gerado com sucesso via rotação.")
        except Exception as e:
             return False, f"Falha ao gerar embedding após tentar todas as chaves: {e}"

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


def gerar_resposta_google(prompt: str, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash") -> Tuple[Optional[str], Optional[str]]:
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
    google_api_key: Optional[str] = None,
    preferred_provider: Optional[str] = None,
    role: str = 'mentor'
) -> Dict[str, any]:
    """
    Processa a query do usuário com RAG e IA, com sistema de rotação de chaves.
    """ 
    try:
        print(f"🔍 Buscando contextos para user_id: {user_id} com papel: {role}")
        contextos_relevantes = buscar_contextos_relevantes(user_id, query, top_k=5, role=role)
        
        if contextos_relevantes:
            print(f"✅ {len(contextos_relevantes)} contextos encontrados")
        else:
            print("⚠️ Nenhum contexto encontrado")
        
        prompt_sistema = gerar_prompt_sistema(contextos_relevantes, role)
        prompt_final = f"""{prompt_sistema}\n\n---\n**MENSAGEM DO USUÁRIO:**\n{query}\n\n---\n\n**INSTRUÇÕES:**\n- Responda de forma natural e conversacional em português do Brasil.\n- Não use estruturas rígidas ou listas obrigatórias.\n- Integre as informações do contexto organicamente na resposta."""
        
        resposta_ia = None
        erro = None
        ia_usada = None
        erros_acumulados = []

        # Determina a ordem de tentativa baseada na preferência
        tentativas = []
        if preferred_provider == 'groq':
            tentativas = [('groq', groq_api_key), ('google_user', google_api_key)]
        elif preferred_provider in ['google', 'google_user']:
            tentativas = [('google_user', google_api_key), ('groq', groq_api_key)]
        else:
            # Padrão: tenta Groq primeiro (geralmente mais rápido)
            tentativas = [('groq', groq_api_key), ('google_user', google_api_key)]

        # 1️⃣ e 2️⃣ Tenta as chaves do usuário na ordem definida
        for provedor, chave in tentativas:
            if not chave:
                continue
                
            if provedor == 'groq':
                print("🔑 Usuário tentando Groq (chave própria)")
                try:
                    resposta_ia, erro = gerar_resposta_groq(prompt_final, chave)
                    if resposta_ia:
                        ia_usada = "groq"
                        break
                    else:
                        erros_acumulados.append(f"Groq (usuário): {erro}")
                except InvalidGroqApiKey as e:
                    erros_acumulados.append(f"Groq (usuário): {str(e)}")
            
            elif provedor == 'google_user':
                print("🔑 Usuário tentando Google AI (chave própria)")
                try:
                    resposta_ia, erro = gerar_resposta_google(prompt_final, api_key=chave)
                    if resposta_ia:
                        ia_usada = "google_user"
                        break
                    else:
                        erros_acumulados.append(f"Google (usuário): {erro}")
                except (InvalidGoogleApiKey, QuotaExceededError) as e:
                    erros_acumulados.append(f"Google (usuário): {str(e)}")

        # 3️⃣ Fallback: Tenta Groq com chave do proprietário primeiro (mais estável e rápido)
        if not resposta_ia:
            admin_groq_key = os.environ.get("GROQ_API_KEY")
            if admin_groq_key:
                print("🌐 FALLBACK: Tentando Groq do proprietário")
                try:
                    resposta_ia, erro = gerar_resposta_groq(prompt_final, admin_groq_key)
                    if resposta_ia:
                        ia_usada = "groq_owner"
                        print("✅ Resposta gerada com Groq do proprietário")
                except Exception as e:
                    print(f"⚠️ Groq do proprietário falhou: {e}")
                    erros_acumulados.append(f"Groq proprietário: {str(e)}")

        # 4️⃣ Fallback Final: Rotação de chaves do proprietário Google
        if not resposta_ia:
            print("🌐 FALLBACK FINAL: Tentando chaves do proprietário Google em rotação")
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