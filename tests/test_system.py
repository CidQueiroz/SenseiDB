import requests
import json
import sys

BACKEND_URL = "http://localhost:8000/api"

def test_health():
    """Testa health check"""
    print("🏥 Testando Health Check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health/", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Backend OK: {response.json()}")
            return True
        else:
            print(f"   ❌ Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_chat():
    """Testa endpoint de chat"""
    print("\n💬 Testando Chat Endpoint...")
    
    payload = {
        "user_id": "test_user_123",
        "query": "Olá, como você pode me ajudar?",
        "groq_api_key": None  # Testará com Google AI
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat/",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Resposta recebida")
            print(f"   🤖 IA usada: {data.get('ia_usada', 'N/A')}")
            print(f"   📝 Resposta: {data.get('resposta', 'N/A')[:100]}...")
            return True
        else:
            print(f"   ❌ Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_save_context():
    """Testa salvar contexto"""
    print("\n💾 Testando Salvar Contexto...")
    
    payload = {
        "user_id": "test_user_123",
        "contexto": "Este é um contexto de teste para verificar se o sistema está salvando corretamente."
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/contexto/",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"   ✅ Contexto salvo com sucesso")
            return True
        else:
            print(f"   ❌ Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    print("🧪 Testando Sistema SenseiDB")
    print("=" * 50)
    
    results = {
        "health": test_health(),
        "chat": test_chat(),
        "context": test_save_context()
    }
    
    print("\n" + "=" * 50)
    print("📊 Resultados dos Testes:")
    print(f"   Health Check: {'✅' if results['health'] else '❌'}")
    print(f"   Chat Endpoint: {'✅' if results['chat'] else '❌'}")
    print(f"   Save Context: {'✅' if results['context'] else '❌'}")
    
    if all(results.values()):
        print("\n🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n⚠️  Alguns testes falharam. Verifique a configuração.")
        sys.exit(1)

if __name__ == "__main__":
    main()