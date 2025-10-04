
import pytest
from django.urls import reverse, resolve
from agent.views import health_check

pytestmark = pytest.mark.django_db

def test_api_include_resolves_health_check():
    """
    Testa se o include('agent.urls') no urls.py principal está funcionando,
    verificando se uma URL do 'agent' (health) é resolvida corretamente.
    """
    # O nome que demos para a URL de health check no agent/urls.py foi 'health'
    # O reverse() deve montar a URL completa, incluindo o prefixo /api/
    url = reverse('health')
    
    # Verifica se a URL montada está correta
    assert url == '/api/health/'
    
    # Verifica se essa URL aponta para a view correta
    assert resolve(url).func == health_check
