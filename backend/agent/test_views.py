import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from django.urls import reverse

# Marcador para todos os testes neste arquivo usarem o banco de dados
pytestmark = pytest.mark.django_db

# Cria um cliente de API reutilizável para os testes
@pytest.fixture
def client():
    return APIClient()

# --- Testes para o endpoint de Health Check ---

def test_health_check_endpoint(client):
    """ Testa se o endpoint de health check responde corretamente. """
    url = reverse('health')
    response = client.get(url)
    
    assert response.status_code == 200
    assert response.data == {"status": "healthy", "service": "SenseiDB Backend"}


# --- Testes para o endpoint de Chat ---

@patch('agent.views.processar_query_usuario')
def test_chat_endpoint_success(mock_processar_query, client):
    """ Testa o caminho de sucesso do endpoint de chat. """
    mock_processar_query.return_value = {"resposta": "Olá!", "ia_usada": "google"}
    
    url = reverse('chat')
    data = {"user_id": "123", "query": "Oi"}
    response = client.post(url, data, format='json')
    
    assert response.status_code == 200
    assert response.data["resposta"] == "Olá!"
    mock_processar_query.assert_called_once_with("123", "Oi", None)

def test_chat_endpoint_bad_request(client):
    """ Testa se o endpoint de chat retorna 400 com dados faltando. """
    url = reverse('chat')
    data = {"user_id": "123"} # Query faltando
    response = client.post(url, data, format='json')
    
    assert response.status_code == 400
    assert "erro" in response.data


# --- Testes para o endpoint de Salvar Contexto ---

@patch('agent.views.salvar_contexto_usuario')
def test_salvar_contexto_endpoint_success(mock_salvar_contexto, client):
    """ Testa o caminho de sucesso do endpoint de salvar contexto. """
    mock_salvar_contexto.return_value = True
    
    url = reverse('salvar_contexto')
    data = {"user_id": "123", "contexto": "Novo contexto"}
    response = client.post(url, data, format='json')
    
    assert response.status_code == 200
    assert response.data["mensagem"] == "Contexto salvo com sucesso"
    mock_salvar_contexto.assert_called_once_with("123", "Novo contexto")

@patch('agent.views.salvar_contexto_usuario')
def test_salvar_contexto_endpoint_failure(mock_salvar_contexto, client):
    """ Testa o que acontece se a função de salvar falhar. """
    mock_salvar_contexto.return_value = False
    
    url = reverse('salvar_contexto')
    data = {"user_id": "123", "contexto": "Novo contexto"}
    response = client.post(url, data, format='json')
    
    assert response.status_code == 500
    assert response.data["erro"] == "Falha ao salvar contexto"

def test_salvar_contexto_endpoint_bad_request(client):
    """ Testa o endpoint de salvar contexto com dados faltando. """
    url = reverse('salvar_contexto')
    data = {"user_id": "123"} # Contexto faltando
    response = client.post(url, data, format='json')
    
    assert response.status_code == 400
    assert "erro" in response.data


# --- Testes para o endpoint de Checar Contextos ---

@patch('agent.views.init_firebase')
def test_check_user_contexts_with_data(mock_init_firebase, client):
    """ Testa a checagem de um usuário que TEM contextos. """
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.collection.return_value.limit.return_value.stream.return_value = [MagicMock()]
    mock_init_firebase.return_value = mock_db
    
    url = reverse('check_contexts', kwargs={'user_id': '123'})
    response = client.get(url)
    
    assert response.status_code == 200
    assert response.data["has_contexts"] is True

@patch('agent.views.init_firebase')
def test_check_user_contexts_no_data(mock_init_firebase, client):
    """ Testa a checagem de um usuário que NÃO TEM contextos. """
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.collection.return_value.limit.return_value.stream.return_value = []
    mock_init_firebase.return_value = mock_db
    
    url = reverse('check_contexts', kwargs={'user_id': '456'})
    response = client.get(url)
    
    assert response.status_code == 200
    assert response.data["has_contexts"] is False