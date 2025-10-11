from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .utils import processar_query_usuario, salvar_contexto_usuario, init_firebase, InvalidGroqApiKey, InvalidGoogleApiKey
import traceback

# Simulação de rastreamento de uso em memória (para desenvolvimento)
# Em produção, isso deve ser substituído por uma contagem no Firestore.
usage_tracking = {}
FREE_TIER_LIMIT = 20

@api_view(['POST'])
def chat_endpoint(request):
    """
    Endpoint principal do chat
    """
    try:
        user_id = request.data.get('user_id')
        query = request.data.get('query')
        groq_api_key = request.data.get('groq_api_key')
        google_api_key = request.data.get('google_api_key')

        if not user_id or not query:
            return Response(
                {"erro": "'user_id' e 'query' são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        has_own_key = groq_api_key or google_api_key
        if not has_own_key:
            usage_tracking.setdefault(user_id, 0)
            if usage_tracking[user_id] >= FREE_TIER_LIMIT:
                return Response(
                    {"error": "USAGE_LIMIT_EXCEEDED"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            usage_tracking[user_id] += 1

        resultado = processar_query_usuario(user_id, query, groq_api_key, google_api_key)
        
        return Response(resultado, status=status.HTTP_200_OK)
    
    except InvalidGroqApiKey:
        return Response(
            {"error": "INVALID_API_KEY", "provider": "groq"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except InvalidGoogleApiKey:
        return Response(
            {"error": "INVALID_API_KEY", "provider": "google"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        print(f"❌ Erro no endpoint: {e}")
        traceback.print_exc()
        return Response(
            {"erro": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def salvar_contexto_endpoint(request):
    """
    Endpoint para salvar novo contexto
    
    Body esperado:
    {
        "user_id": "string",
        "contexto": "string"
    }
    """
    try:
        user_id = request.data.get('user_id')
        contexto = request.data.get('contexto')
        
        if not user_id or not contexto:
            return Response(
                {"erro": "'user_id' e 'contexto' são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sucesso = salvar_contexto_usuario(user_id, contexto)
        
        if sucesso:
            return Response(
                {"mensagem": "Contexto salvo com sucesso"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"erro": "Falha ao salvar contexto"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return Response(
            {"erro": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def check_user_contexts(request, user_id):
    """Verifica se usuário tem contextos"""
    try:
        db = init_firebase()
        docs = db.collection('users').document(user_id).collection('inteligencia_critica').limit(1).stream()
        
        has_contexts = len(list(docs)) > 0
        
        return Response({
            "has_contexts": has_contexts,
            "count": 1 if has_contexts else 0
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