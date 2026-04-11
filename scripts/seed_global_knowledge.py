import os
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json

# Setup Firebase
def init_firebase():
    if not firebase_admin._apps:
        # Use existing service account or default credentials
        firebase_admin.initialize_app()
    return firestore.client()

def get_embedding(text):
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise Exception("GOOGLE_API_KEY not found")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
    payload = {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": text}]}}
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()['embedding']['values']

def seed_role(db, role, concepts):
    print(f"📦 Seeding global knowledge for role: {role}")
    collection = db.collection('global_knowledge').document(role).collection('concepts')
    
    for concept in concepts:
        print(f"  - Adding concept: {concept['title']}")
        embedding = get_embedding(f"{concept['title']}: {concept['content']}")
        collection.add({
            'title': concept['title'],
            'content': concept['content'],
            'embedding': embedding,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

def main():
    db = init_firebase()
    
    knowledge_base = {
        'mentor': [
            {"title": "Princípio AMV", "content": "Ação Mínima Viável: foco no menor passo possível que gera progresso real."},
            {"title": "Porto Seguro", "content": "Criação de um estado mental de clareza e controle antes de tomar decisões estratégicas."},
            {"title": "Análise de Padrões", "content": "Identificação de comportamentos recorrentes que impedem o progresso."}
        ],
        'professor': [
            {"title": "Metodologia Ativa", "content": "O aluno é o centro do aprendizado, transformando teoria em prática constante."},
            {"title": "Andragogia", "content": "Ensino focado em adultos, priorizando a utilidade imediata do conhecimento."},
            {"title": "Analogias Didáticas", "content": "Uso de conceitos familiares para explicar temas novos e complexos."}
        ],
        'nutricionista': [
            {"title": "Densidade Nutricional", "content": "Foco em alimentos que oferecem o máximo de micronutrientes por caloria."},
            {"title": "Equilíbrio Glicêmico", "content": "Importância de manter níveis estáveis de açúcar no sangue para energia constante."},
            {"title": "Hidratação Metabólica", "content": "O papel da água em todos os processos de queima de gordura e síntese proteica."}
        ],
        'atendente': [
            {"title": "Escuta Ativa", "content": "Validar a dor do cliente antes de apresentar qualquer solução técnica."},
            {"title": "Agilidade Resolutiva", "content": "Resolver o problema no primeiro contato sempre que possível."},
            {"title": "Tom Empático", "content": "Linguagem que demonstra compreensão e urgência no atendimento."}
        ]
    }
    
    for role, concepts in knowledge_base.items():
        seed_role(db, role, concepts)

if __name__ == "__main__":
    main()
