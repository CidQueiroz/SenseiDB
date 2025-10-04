import streamlit as st
import pyrebase
import json

# --- CONFIGURAÇÃO DO FIREBASE ---
# ATENÇÃO: Substitua com as suas credenciais web do Firebase
firebaseConfig = {
"apiKey": "AIzaSyDlL3WdqovyACEMI1M1-q82ei43PtQqlIw",
"authDomain": "senseidb-rebranding.firebaseapp.com",
"projectId": "senseidb-rebranding",
"storageBucket": "senseidb-rebranding.firebasestorage.app",
"messagingSenderId": "1022880460923",
"appId": "1:1022880460923:web:6605c05d9c5b0528fbb2de",
"measurementId": "G-SEN0G4F7W6"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# --- INTERFACE DO STREAMLIT ---
st.title("SenseiDB v2.0 - Tela de Acesso")

# Inicializa o estado de login se não existir
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# Se já estiver logado, mostra a tela principal
if st.session_state.user_info:
    user_info = st.session_state.user_info
    st.write(f"Bem-vindo, {user_info['email']}!")
    
    # Adicione aqui a lógica do seu app principal
    st.write("Você está na área logada do SenseiDB.")
    
    if st.button("Sair"):
        st.session_state.user_info = None
        st.experimental_rerun()

# Se não estiver logado, mostra a tela de login/cadastro
else:
    choice = st.selectbox("Login ou Cadastro", ["Login", "Cadastrar"])

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if choice == "Login":
        if st.button("Entrar"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.user_info = user
                st.success("Login realizado com sucesso!")
                st.experimental_rerun()
            except Exception as e:
                st.error("Email ou senha incorretos.")

    else: # Cadastro
        if st.button("Cadastrar"):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success("Cadastro realizado com sucesso! Faça o login para continuar.")
            except Exception as e:
                st.error(f"Erro no cadastro: {e}")