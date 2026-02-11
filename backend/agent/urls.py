from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_endpoint, name='chat'),

    path('contextos/', views.ContextListView.as_view(), name='context_list'), # New
    path('health/', views.health_check, name='health'),
    path('contexto/check/<str:user_id>/', views.check_user_contexts, name='check_contexts'),
    path('api-keys/', views.UserApiKeysView.as_view(), name='user_api_keys'), # New
]
