from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User # Import Django's User model
import traceback

from .utils import (
    processar_query_usuario,
    salvar_contexto_usuario,
    init_firebase,
    InvalidGroqApiKey,
    InvalidGoogleApiKey,
    QuotaExceededError,
)
from .models import UserProfile, Context
from .serializers import UserProfileSerializer, ContextSerializer


class UserApiKeysView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    def post(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        groq_api_key = request.data.get('groq_api_key')
        google_api_key = request.data.get('google_api_key')

        if groq_api_key is not None:
            user_profile.groq_api_key = groq_api_key
        if google_api_key is not None:
            user_profile.google_api_key = google_api_key
        
        user_profile.save()
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContextListView(generics.ListCreateAPIView):
    serializer_class = ContextSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return Context.objects.filter(user_profile=user_profile).order_by('-timestamp')

    def perform_create(self, serializer):
        user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        contexto_texto = serializer.validated_data.get('text')

        # Use the utility function to save to Firestore and get embedding
        # We need the user's Google API key for embedding generation
        google_api_key_for_embedding = user_profile.google_api_key or os.environ.get("GOOGLE_API_KEY")

        if not google_api_key_for_embedding:
            raise status.HTTP_400_BAD_REQUEST("Google API Key not available for embedding.")

        # Call the utility function to save to Firestore and generate embedding
        sucesso, erro_msg = salvar_contexto_usuario(str(self.request.user.username), contexto_texto, google_api_key_for_embedding)
        
        if not sucesso:
            raise serializers.ValidationError(f"Failed to save context to Firestore: {erro_msg}")
        
        # Then save to Django model
        serializer.save(user_profile=user_profile)


@api_view(['POST'])
def chat_endpoint(request):
    """
    Endpoint principal do chat
    """
    try:
        if not request.user.is_authenticated:
            return Response(
                {"erro": "Autenticação necessária."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_id = str(request.user.username) # Firebase UID is stored as username

        query = request.data.get('query')
        if not query:
            return Response(
                {"erro": "'query' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get API keys from user profile
        groq_api_key = user_profile.groq_api_key
        google_api_key = user_profile.google_api_key

        resultado = processar_query_usuario(user_id, query, groq_api_key, google_api_key)
        
        return Response(resultado, status=status.HTTP_200_OK)

    except QuotaExceededError as e:
        return Response(
            {"error": "QUOTA_EXCEEDED", "message": "A quota de uso da API do Google foi excedida. Verifique seu plano e faturamento."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    except InvalidGroqApiKey:
        return Response(
            {"error": "INVALID_API_KEY", "provider": "groq", "message": "Chave Groq inválida."},
            status=status.HTTP_400_BAD_REQUEST
        )
    except InvalidGoogleApiKey:
        return Response(
            {"error": "INVALID_API_KEY", "provider": "google", "message": "Chave Google inválida."},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        print(f"❌ Erro no endpoint: {e}")
        traceback.print_exc()
        return Response(
            {"erro": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Refactor salvar_contexto_endpoint into ContextListView's perform_create
# @api_view(['POST'])
# def salvar_contexto_endpoint(request):
#     """
#     Endpoint para salvar novo contexto
#     """
#     # ... (logic moved to ContextListView)

@api_view(['GET'])
def check_user_contexts(request, user_id=None):
    """Verifica se usuário tem contextos no modelo Django"""
    if not request.user.is_authenticated:
        return Response(
            {"erro": "Autenticação necessária."},
            status=status.HTTP_401_UNAUTHORIZED
        )
    try:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        has_contexts = Context.objects.filter(user_profile=user_profile).exists()
        count = Context.objects.filter(user_profile=user_profile).count()
        
        return Response({
            "has_contexts": has_contexts,
            "count": count
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response(
        {"status": "healthy", "service": "SenseiDB Backend"},
        status=status.HTTP_200_OK
    )
