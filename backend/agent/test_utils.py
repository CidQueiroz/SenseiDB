
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import requests

# Importa as funções do seu utilitário
from . import utils

# Marcador para todos os testes neste arquivo usarem o banco de dados
pytestmark = pytest.mark.django_db


@patch('os.environ.get')
@patch('agent.utils.requests.post')
@patch('agent.utils.init_firebase')
def test_salvar_contexto_usuario_sucesso(mock_init_firebase, mock_requests_post, mock_os_get):
    """
    Testa se a função salvar_contexto_usuario chama corretamente as APIs 
    e o Firestore em um cenário de sucesso.
    """
    # --- Configuração do Mock ---
    mock_os_get.return_value = "DUMMY_API_KEY"
    mock_embedding_response = MagicMock()
    mock_embedding_response.status_code = 200
    mock_embedding_response.json.return_value = {
        'embedding': {'values': [0.1, 0.2, 0.3]}
    }
    mock_requests_post.return_value = mock_embedding_response
    mock_firestore_db = MagicMock()
    mock_user_doc = MagicMock()
    mock_collection = MagicMock()
    mock_user_doc.collection.return_value = mock_collection
    mock_firestore_db.collection.return_value.document.return_value = mock_user_doc
    mock_init_firebase.return_value = mock_firestore_db

    # --- Execução ---
    sucesso = utils.salvar_contexto_usuario("test_user_123", "Eu sou um desenvolvedor Python.")

    # --- Verificação ---
    assert sucesso is True
    mock_requests_post.assert_called_once()
    mock_collection.add.assert_called_once()
    saved_data = mock_collection.add.call_args[0][0]
    assert saved_data['contexto'] == "Eu sou um desenvolvedor Python."
    assert saved_data['embedding'] == [0.1, 0.2, 0.3]

@patch('os.environ.get')
@patch('agent.utils.requests.post')
def test_salvar_contexto_falha_api_embedding(mock_requests_post, mock_os_get):
    """ Testa o tratamento de erro se a API de embedding falhar ao salvar. """
    # --- Configuração do Mock ---
    mock_os_get.return_value = "DUMMY_API_KEY"
    mock_requests_post.side_effect = requests.exceptions.RequestException("Erro de rede")

    # --- Execução ---
    sucesso = utils.salvar_contexto_usuario("user", "texto")

    # --- Verificação ---
    assert sucesso is False


@patch('os.environ.get')
@patch('agent.utils.requests.post')
@patch('agent.utils.init_firebase')
def test_buscar_contextos_relevantes_sucesso(mock_init_firebase, mock_requests_post, mock_os_get):
    """
    Testa se a busca de contextos relevantes funciona, incluindo o cálculo
    de similaridade e a ordenação.
    """
    # --- Configuração do Mock ---
    mock_os_get.return_value = "DUMMY_API_KEY"
    mock_embedding_response = MagicMock()
    mock_embedding_response.status_code = 200
    mock_embedding_response.json.return_value = {
        'embedding': {'values': [1.0, 0.0, 0.0]}
    }
    mock_requests_post.return_value = mock_embedding_response
    doc1_data = {'contexto': 'Gosto de cachorros', 'embedding': [0.9, 0.1, 0.0]}
    doc2_data = {'contexto': 'Gosto de gatos', 'embedding': [0.2, 0.8, 0.1]}
    doc3_data = {'contexto': 'Gosto de pássaros', 'embedding': [0.5, 0.5, 0.5]}
    mock_doc1, mock_doc2, mock_doc3 = MagicMock(), MagicMock(), MagicMock()
    mock_doc1.to_dict.return_value = doc1_data
    mock_doc2.to_dict.return_value = doc2_data
    mock_doc3.to_dict.return_value = doc3_data
    mock_firestore_db = MagicMock()
    mock_firestore_db.collection.return_value.document.return_value.collection.return_value.stream.return_value = [mock_doc1, mock_doc2, mock_doc3]
    mock_init_firebase.return_value = mock_firestore_db

    # --- Execução ---
    contextos = utils.buscar_contextos_relevantes("test_user_abc", "animal de estimação", top_k=2)

    # --- Verificação ---
    assert len(contextos) == 2
    assert contextos[0] == 'Gosto de cachorros'
    assert contextos[1] == 'Gosto de pássaros'

@patch('os.environ.get')
@patch('agent.utils.requests.post')
def test_buscar_contextos_falha_api_embedding(mock_requests_post, mock_os_get):
    """ Testa o tratamento de erro se a API de embedding falhar ao buscar. """
    # --- Configuração do Mock ---
    mock_os_get.return_value = "DUMMY_API_KEY"
    mock_requests_post.side_effect = requests.exceptions.RequestException("Erro de rede")

    # --- Execução ---
    contextos = utils.buscar_contextos_relevantes("user", "query")

    # --- Verificação ---
    assert contextos == []


@patch('agent.utils.gerar_resposta_google')
@patch('agent.utils.gerar_resposta_groq')
@patch('agent.utils.gerar_prompt_sistema')
@patch('agent.utils.buscar_contextos_relevantes')
def test_processar_query_usuario_fallback_para_google(mock_buscar, mock_prompt, mock_groq, mock_google):
    """ Testa se a função principal faz o fallback para Google quando Groq falha. """
    # --- Configuração do Mock ---
    mock_buscar.return_value = ["contexto 1", "contexto 2"]
    mock_prompt.return_value = "Prompt gerado"
    mock_groq.return_value = (None, "Erro na API da Groq")
    mock_google.return_value = ("Resposta do Google", None)

    # --- Execução ---
    resultado = utils.processar_query_usuario("user", "query", groq_api_key="key")

    # --- Verificação ---
    mock_groq.assert_called_once()
    mock_google.assert_called_once()
    assert resultado["ia_usada"] == "google"
    assert resultado["resposta"] == "Resposta do Google"


@patch('agent.utils.gerar_resposta_google')
@patch('agent.utils.gerar_resposta_groq')
@patch('agent.utils.gerar_prompt_sistema')
@patch('agent.utils.buscar_contextos_relevantes')
def test_processar_query_usuario_sucesso_groq(mock_buscar, mock_prompt, mock_groq, mock_google):
    """ Testa o caminho feliz, onde Groq funciona de primeira. """
    # --- Configuração do Mock ---
    mock_buscar.return_value = ["contexto 1"]
    mock_prompt.return_value = "Prompt gerado"
    mock_groq.return_value = ("Resposta da Groq", None)

    # --- Execução ---
    resultado = utils.processar_query_usuario("user", "query", groq_api_key="key")

    # --- Verificação ---
    mock_groq.assert_called_once()
    mock_google.assert_not_called() # Google não deve ser chamado
    assert resultado["ia_usada"] == "groq"
    assert resultado["resposta"] == "Resposta da Groq"


@patch('agent.utils.gerar_resposta_google')
@patch('agent.utils.gerar_resposta_groq')
@patch('agent.utils.gerar_prompt_sistema')
@patch('agent.utils.buscar_contextos_relevantes')
def test_processar_query_usuario_falha_total(mock_buscar, mock_prompt, mock_groq, mock_google):
    """ Testa o que acontece quando ambas as IAs falham. """
    # --- Configuração do Mock ---
    mock_buscar.return_value = []
    mock_prompt.return_value = "Prompt gerado"
    mock_groq.return_value = (None, "Erro Groq")
    mock_google.return_value = (None, "Erro Google")

    # --- Execução & Verificação ---
    with pytest.raises(Exception, match="Falha em ambas as IAs: Erro Google"):
        utils.processar_query_usuario("user", "query", groq_api_key="key")


def test_gerar_prompt_sistema_com_contexto():
    """ Testa se o prompt de sistema é gerado corretamente com contextos. """
    contextos = ["contexto 1", "segundo contexto"]
    prompt = utils.gerar_prompt_sistema(contextos)
    assert "CONTEXTO DO USUÁRIO:" in prompt
    assert "• contexto 1" in prompt
    assert "• segundo contexto" in prompt
    assert "OBSERVAÇÃO:" not in prompt # Não deve ter a observação de novo usuário


def test_gerar_prompt_sistema_sem_contexto():
    """ Testa se o prompt de sistema é gerado corretamente para um novo usuário. """
    prompt = utils.gerar_prompt_sistema([])
    assert "OBSERVAÇÃO:" in prompt
    assert "Este usuário ainda não adicionou contextos pessoais" in prompt
    assert "CONTEXTO DO USUÁRIO:" not in prompt
