
import pytest
from django.urls import reverse, resolve
from .views import health_check, chat_endpoint, salvar_contexto_endpoint, check_user_contexts

pytestmark = pytest.mark.django_db

def test_health_url_resolves():
    """Verifica se a URL de health check resolve para a view correta."""
    url = reverse('health')
    assert resolve(url).func == health_check

def test_chat_url_resolves():
    """Verifica se a URL de chat resolve para a view correta."""
    url = reverse('chat')
    assert resolve(url).func == chat_endpoint

def test_salvar_contexto_url_resolves():
    """Verifica se a URL de salvar contexto resolve para a view correta."""
    url = reverse('salvar_contexto')
    assert resolve(url).func == salvar_contexto_endpoint

def test_check_contexts_url_resolves():
    """Verifica se a URL de checar contexto resolve para a view correta."""
    # Para URLs com parâmetros, precisamos passar um valor de exemplo
    url = reverse('check_contexts', kwargs={'user_id': 'test-id'})
    assert resolve(url).func == check_user_contexts
