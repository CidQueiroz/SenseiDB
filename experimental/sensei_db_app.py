import streamlit as st
import pyrebase
import requests
import json

# ============================================
# CONFIGURAÇÃO
# ============================================

# URL do backend Django (altere para sua URL do Cloud Run)
BACKEND_URL = "http://localhost:8000/api"  # Desenvolvimento local
# BACKEND_URL = "https://seu-backend.run.app/api"  # Produção

# Configuração Firebase para autenticação
firebaseConfig = {
    "apiKey": "AIzaSyDlL3WdqovyACEMI1M1-q82ei43PtQqlIw",
    "authDomain": "senseidb-rebranding.firebaseapp.com",
    "projectId": "senseidb-rebranding",
    "storageBucket": "senseidb-rebranding.firebasestorage.app",
    "messagingSenderId": "1022880460923",
    "appId": "1:1022880460923:web:6605c05d9c5b0528fbb2de",
    "measurementId": "G-SEN0G4F7W6",
    "databaseURL": ""
}

# Inicializa Pyrebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Email do admin
ADMIN_EMAIL = "cydy.potter@gmail.com"

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def chamar_api_chat(user_id, query, groq_api_key=None):
    """Chama o endpoint de chat do Django backend"""
    try:
        payload = {
            'user_id': user_id,
            'query': query
        }
        
        if groq_api_key:
            payload['groq_api_key'] = groq_api_key
        
        response = requests.post(
            f"{BACKEND_URL}/chat/",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "erro": f"Status {response.status_code}: {response.text}"
            }
    
    except requests.exceptions.Timeout:
        return {"erro": "Timeout: O servidor demorou muito para responder"}
    except requests.exceptions.RequestException as e:
        return {"erro": f"Erro de conexão: {str(e)}"}

def salvar_contexto_api(user_id, contexto):
    """Chama o endpoint de salvar contexto"""
    try:
        payload = {
            'user_id': user_id,
            'contexto': contexto
        }
        
        response = requests.post(
            f"{BACKEND_URL}/contexto/",
            json=payload,
            timeout=30
        )
        
        return response.status_code == 200
    
    except Exception as e:
        st.error(f"Erro ao salvar contexto: {e}")
        return False

def get_groq_key_from_state(user_email):
    """Obtém chave Groq do session_state"""
    if user_email == ADMIN_EMAIL:
        # Admin pode usar chave do secrets.toml (desenvolvimento)
        return st.secrets.get("groq_api_key", None)
    else:
        return st.session_state.get('groq_api_key', None)

def is_google_auth(user_info):
    """Verifica se o usuário está logado com Google"""
    # Firebase retorna providerData quando logado via Google
    providers = user_info.get('providerData', [])
    return any(p.get('providerId') == 'google.com' for p in providers)

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================

st.set_page_config(
    page_title="SenseiDB v3.0",
    page_icon="🧠",
    layout="wide"
)

# ============================================
# ESTADO DA SESSÃO
# ============================================

if 'user_info' not in st.session_state:
    st.session_state.user_info = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = None

# ============================================
# INTERFACE PRINCIPAL
# ============================================

# --- ÁREA LOGADA ---
if st.session_state.user_info:
    user_info = st.session_state.user_info
    user_id = user_info['localId']
    user_email = user_info['email']
    
    # Verifica se usuário tem chave Groq configurada
    groq_key = get_groq_key_from_state(user_email)
    is_google_user = is_google_auth(user_info)
    
    # Se não tem chave Groq e não é usuário Google, pede configuração
    if not groq_key and user_email != ADMIN_EMAIL and not is_google_user:
        st.title("🔐 Configuração Inicial")
        st.info("""
        **Bem-vindo ao SenseiDB!**
        
        Para usar o assistente, você tem duas opções:
        
        1. **Inserir sua chave API do Groq** (recomendado - mais rápido)
        2. **Fazer login com Google** (usa Google AI automaticamente)
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Opção 1: Groq API")
            st.markdown("Obtenha sua chave em: [console.groq.com](https://console.groq.com)")
            new_groq_key = st.text_input("Chave API Groq", type="password", key="input_groq")
            
            if st.button("💾 Salvar e Continuar"):
                if new_groq_key:
                    st.session_state.groq_api_key = new_groq_key
                    st.success("✅ Chave salva! Redirecionando...")
                    st.rerun()
                else:
                    st.error("Por favor, insira uma chave válida")
        
        with col2:
            st.subheader("Opção 2: Login Google")
            st.info("""
            Se você fez login com Google, o sistema usará 
            automaticamente a Google AI. Apenas clique abaixo.
            """)
            
            if st.button("🌐 Usar Google AI"):
                st.session_state.groq_api_key = "usar_google"
                st.success("✅ Configurado para Google AI!")
                st.rerun()
    
    # --- INTERFACE DO CHAT ---
    else:
        # Sidebar
        with st.sidebar:
            st.title("🧠 SenseiDB v3.0")
            st.markdown(f"**Operador:** `{user_email}`")
            
            # Indicador de IA ativa
            if groq_key and groq_key != "usar_google":
                st.success("🚀 Groq AI Ativo")
            elif is_google_user or groq_key == "usar_google":
                st.info("🌐 Google AI Ativo")
            else:
                st.warning("⚠️ Nenhuma IA configurada")
            
            st.markdown("---")
            
            # Gerenciar chave API (apenas não-admin)
            if user_email != ADMIN_EMAIL:
                with st.expander("🔧 Gerenciar API"):
                    st.markdown("**Chave Groq Atual:**")
                    if groq_key and groq_key != "usar_google":
                        st.code(groq_key[:20] + "..." if len(groq_key) > 20 else groq_key)
                    else:
                        st.text("Usando Google AI")
                    
                    new_key = st.text_input("Nova Chave Groq", type="password", key="update_groq")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Atualizar"):
                            if new_key:
                                st.session_state.groq_api_key = new_key
                                st.success("✅ Atualizada!")
                                st.rerun()
                    
                    with col2:
                        if st.button("Usar Google"):
                            st.session_state.groq_api_key = "usar_google"
                            st.success("✅ Mudado!")
                            st.rerun()
            
            st.markdown("---")
            
            # Adicionar contexto
            with st.expander("➕ Adicionar Contexto"):
                st.markdown("Adicione informações que o Sensei deve lembrar sobre você:")
                novo_contexto = st.text_area(
                    "Novo insight:",
                    placeholder="Ex: Tenho dificuldade com procrastinação quando..."
                )
                
                if st.button("💾 Salvar Inteligência"):
                    if novo_contexto.strip():
                        if salvar_contexto_api(user_id, novo_contexto):
                            st.success("✅ Inteligência salva!")
                        else:
                            st.error("❌ Erro ao salvar")
                    else:
                        st.warning("⚠️ Campo vazio")
            
            st.markdown("---")
            
            # Informações do sistema
            with st.expander("ℹ️ Sobre o Sistema"):
                st.markdown("""
                **SenseiDB v3.0**
                
                - 🧠 RAG inteligente com embeddings
                - 🚀 Groq AI (rápido) ou Google AI (confiável)
                - 🔄 Fallback automático entre IAs
                - 🔐 Seus dados protegidos no Firebase
                
                **Backend:** Django REST Framework
                """)
            
            st.markdown("---")
            
            # Limpar chat
            if st.button("🗑️ Limpar Conversa"):
                st.session_state.messages = []
                st.rerun()
            
            # Sair
            if st.button("🚪 Sair"):
                st.session_state.user_info = None
                st.session_state.messages = []
                st.session_state.groq_api_key = None
                st.rerun()
        
        # --- ÁREA DE CHAT ---
        st.title("🧠 Assistente Sensei")
        st.caption("Seu mentor estratégico pessoal")
        
        # Exibe histórico de mensagens
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Mostra qual IA foi usada (se disponível)
                if message["role"] == "assistant" and "ia_usada" in message:
                    ia_badge = "🚀 Groq" if message["ia_usada"] == "groq" else "🌐 Google"
                    st.caption(f"Gerado por: {ia_badge}")
        
        # Input do usuário
        if prompt := st.chat_input("Qual sua pergunta ou situação?"):
            # Adiciona mensagem do usuário
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Exibe mensagem do usuário
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Gera resposta do assistente
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analisando contexto e gerando resposta..."):
                    # Prepara chave Groq (None se for usar Google)
                    groq_key_to_send = None
                    if groq_key and groq_key != "usar_google":
                        groq_key_to_send = groq_key
                    
                    # Chama API
                    resultado = chamar_api_chat(user_id, prompt, groq_key_to_send)
                    
                    # Verifica se houve erro
                    if "erro" in resultado:
                        st.error(f"❌ Erro: {resultado['erro']}")
                        resposta = "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
                        ia_usada = "erro"
                    else:
                        resposta = resultado.get("resposta", "Sem resposta")
                        ia_usada = resultado.get("ia_usada", "desconhecida")
                        num_contextos = resultado.get("num_contextos", 0)
                        
                        # Exibe resposta
                        st.markdown(resposta)
                        
                        # Badge da IA usada
                        ia_badge = "🚀 Groq" if ia_usada == "groq" else "🌐 Google"
                        st.caption(f"Gerado por: {ia_badge} | Contextos usados: {num_contextos}")
                    
                    # Adiciona ao histórico
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": resposta,
                        "ia_usada": ia_usada
                    })

# --- ÁREA DE LOGIN ---
else:
    # Centraliza o conteúdo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🧠 SenseiDB v3.0")
        st.markdown("### Seu Mentor Estratégico Pessoal")
        
        st.markdown("---")
        
        # Tabs para Login/Cadastro
        tab1, tab2 = st.tabs(["🔓 Login", "📝 Cadastrar"])
        
        with tab1:
            st.markdown("#### Acesse sua conta")
            
            email_login = st.text_input(
                "Email",
                key="email_login",
                placeholder="seu@email.com"
            )
            
            password_login = st.text_input(
                "Senha",
                type="password",
                key="password_login",
                placeholder="••••••••"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("🚀 Entrar", use_container_width=True):
                    if email_login and password_login:
                        try:
                            user = auth.sign_in_with_email_and_password(
                                email_login,
                                password_login
                            )
                            st.session_state.user_info = user
                            st.success("✅ Login realizado!")
                            st.rerun()
                        except Exception as e:
                            st.error("❌ Email ou senha incorretos")
                    else:
                        st.warning("⚠️ Preencha todos os campos")
            
            with col_b:
                st.markdown("**ou**")
            
            st.info("💡 **Dica:** Faça login com Google para usar Google AI automaticamente!")
        
        with tab2:
            st.markdown("#### Crie sua conta")
            
            email_cadastro = st.text_input(
                "Email",
                key="email_cadastro",
                placeholder="seu@email.com"
            )
            
            password_cadastro = st.text_input(
                "Senha",
                type="password",
                key="password_cadastro",
                placeholder="••••••••",
                help="Mínimo 6 caracteres"
            )
            
            password_confirm = st.text_input(
                "Confirmar Senha",
                type="password",
                key="password_confirm",
                placeholder="••••••••"
            )
            
            if st.button("📝 Criar Conta", use_container_width=True):
                if email_cadastro and password_cadastro and password_confirm:
                    if password_cadastro == password_confirm:
                        try:
                            user = auth.create_user_with_email_and_password(
                                email_cadastro,
                                password_cadastro
                            )
                            st.success("✅ Cadastro realizado! Faça login para continuar.")
                        except Exception as e:
                            error_msg = str(e)
                            if "EMAIL_EXISTS" in error_msg:
                                st.error("❌ Este email já está cadastrado")
                            elif "WEAK_PASSWORD" in error_msg:
                                st.error("❌ Senha muito fraca. Use no mínimo 6 caracteres")
                            else:
                                st.error(f"❌ Erro no cadastro: {error_msg}")
                    else:
                        st.error("❌ As senhas não coincidem")
                else:
                    st.warning("⚠️ Preencha todos os campos")
        
        st.markdown("---")
        
        # Informações sobre o sistema
        with st.expander("ℹ️ Sobre o SenseiDB"):
            st.markdown("""
            **SenseiDB v3.0** é seu assistente de IA pessoal que aprende com você.
            
            **Recursos:**
            - 🧠 **RAG Inteligente**: Usa seus contextos salvos para respostas personalizadas
            - 🚀 **Groq AI**: Respostas ultra-rápidas com Llama 3.3
            - 🌐 **Google AI**: Fallback confiável com Gemini
            - 🔐 **Privacidade**: Seus dados protegidos no Firebase
            - 🎯 **Personalização**: O Sensei se adapta ao seu perfil
            
            **Como funciona:**
            1. Faça login ou cadastre-se
            2. Configure sua chave API Groq (ou use Google AI)
            3. Adicione contextos sobre você
            4. Converse com o Sensei!
            
            **Desenvolvido com:**
            - Frontend: Streamlit
            - Backend: Django REST Framework
            - Database: Firebase Firestore
            - AI: Groq (Llama 3.3) + Google (Gemini)
            """)
        
        st.markdown("---")
        st.caption("💻 Desenvolvido por CDK Tech | v3.0")