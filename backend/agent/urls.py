from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_endpoint, name='chat'),
    path('contexto/', views.salvar_contexto_endpoint, name='salvar_contexto'),
    path('health/', views.health_check, name='health'),
    path('contexto/check/<str:user_id>/', views.check_user_contexts, name='check_contexts'),
]