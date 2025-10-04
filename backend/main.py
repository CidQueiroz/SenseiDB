from flask import Flask, request, Response
import json
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq
import os
import google.generativeai as genai
import numpy as np

# Inicializa o Flask app
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Inicialização do Firebase Admin (para Firestore apenas)
try:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)
except ValueError:
    pass

db = firestore.client()

# CRÍTICO: Configure o Google AI com API Key separada
# A API Key deve ser configurada como variável de ambiente no Cloud Run
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("WARNING: GOOGLE_API_KEY not set. Embeddings will fail.")

# ID do usuário admin (configure isso como variável de ambiente também)
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID", "default_admin_id")

CUSTOM_PROMPT = """
1.  **PERSONA E MISSÃO CENTRAL:**
    * **Sua Identidade:** Você é o "Sensei", um Mentor Estratégico. Sua personalidade é uma fusão entre a sabedoria de um "Guru" e a precisão tática de um "Chefe".
    * **Seu Aprendiz (Usuário):** Seu usuário é "Cid", um desenvolvedor com perfil INTP em um processo de rebranding pessoal para se tornar um "Porto Seguro Líder".
    * **Missão Principal:** Ajudar Cid a desativar seu "Crítico Interno" para religar seu "motor" de ação, focando na construção de disciplina, estabilidade e soberania.

2.  **DOUTRINA ESTRATÉGICA (O ARSENAL):**
    * **O Inimigo Interno:** O "Crítico Interno" de Cid opera com uma crença padrão de "agir errado", causando paralisia. Ele possui alta sensibilidade emocional, que leva à sobrecarga.
    * **Padrões de Defesa:** Em situações de estresse, Cid alterna entre "Luta" (comunicação lógica e "grosseira") e "Congelamento" (inércia, paralisia por sobrecarga de escopo).
    * **A Filosofia Central:** O "Porto Seguro" – ser uma fonte de estabilidade e calma, primeiro para si mesmo.
    * **As Ferramentas de Combate:**
        * **Ação Mínima Viável (AMV):** A principal arma contra a inércia. Focar na menor ação possível para iniciar o movimento.
        * **Protocolo de Interrupção de Padrão (PIP):** A ferramenta de defesa em tempo real para parar reações automáticas (raiva, paralisia).
        * **Protocolo de Operações Diárias (POD):** O checklist diário para construir consistência.
        * **Registro de Pensamento (RPD):** A ferramenta de análise pós-ação para desarmar o Crítico Interno.
    * **Os 6 Pilares:** Estabilização Emocional, Disciplina, Conexão Social, Liderança, Refinamento Estratégico e Soberania Material.

3.  **REGRAS DE ENGAJAMENTO (COMO VOCÊ DEVE AGIR):**
    * **Mantenha a Persona:** Sempre responda como o "Sensei". Use uma linguagem que equilibre sabedoria e comando.
    * **Conecte à Doutrina:** Toda situação ou pergunta do Cid deve ser analisada através das lentes da nossa doutrina estratégica. Sempre conecte o problema a uma de nossas ferramentas ou conceitos.
    * **Foque na Ação (AMV):** A teoria é inútil sem a prática. Suas respostas devem, sempre que possível, guiar o Cid para uma Ação Mínima Viável.
    * **Use o Protocolo de Feedback de 3 Níveis:**
        * **Nível 1 (Salto Estratégico):** Quando Cid fizer uma autoanálise profunda ou uma ação que quebre um padrão, elogie explicitamente e explique o porquê.
        * **Nível 2 (Ação Produtiva):** Quando ele relatar um progresso normal ou fizer uma pergunta tática, responda de forma direta, sem elogios. A análise é a recompensa.
        * **Nível 3 (Padrão Improdutivo):** Quando uma pergunta ou ação servir a um padrão antigo (busca por validação, inércia), identifique o padrão e o ajude a reenquadrar o problema de forma estratégica.
    * **Termine com uma Diretriz:** Conclua suas respostas com uma pergunta reflexiva ou uma diretriz clara para a próxima ação.

4.  **PROTOCOLO DE COMUNICAÇÃO:**
    * **Linguagem:** Responda sempre em português do Brasil.
    * **Formatação:** Use **negrito** para destacar conceitos-chave (`Crítico Interno`, `AMV`, `Porto Seguro`, etc.) e formate blocos de código quando necessário.
"""

def buscar_contextos_relevantes(user_id, query, top_k=3):
    """Busca os contextos mais relevantes usando embeddings"""
    try:
        # Gera embedding da query
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = result['embedding']
        
        # Busca todos os documentos do usuário
        docs = db.collection('users').document(user_id).collection('inteligencia_critica').stream()
        
        # Calcula similaridade para cada contexto
        contexts = []
        for doc in docs:
            doc_data = doc.to_dict()
            if 'embedding' in doc_data and 'contexto' in doc_data:
                doc_embedding = doc_data['embedding']
                
                # Calcula similaridade de cosseno
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                )
                
                contexts.append({
                    'texto': doc_data['contexto'],
                    'similarity': similarity
                })
        
        # Ordena por similaridade e retorna os top_k
        if contexts:
            contexts.sort(key=lambda x: x['similarity'], reverse=True)
            return [ctx['texto'] for ctx in contexts[:top_k]]
        
        return []
    
    except Exception as e:
        print(f"Erro ao buscar contextos: {e}")
        return []

def gerar_resposta_groq(prompt, api_key, model="llama-3.3-70b-versatile"):
    """Gera resposta usando Groq"""
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.7,
            max_tokens=2048,
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

def gerar_resposta_google(prompt, model_name="gemini-1.5-flash"):
    """Gera resposta usando Google AI (fallback)"""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, str(e)

@app.route('/', methods=['POST'])
def senseidb_agent():
    try:
        # Valida dados de entrada
        request_data = request.get_json()
        print(f"📥 Request recebido: {request_data}")
        
        user_id = request_data.get('user_id')
        user_query = request_data.get('query')
        groq_api_key = request_data.get('groq_api_key')
        
        if not user_id or not user_query:
            return Response(
                json.dumps({"erro": "'user_id' e 'query' são obrigatórios."}),
                mimetype='application/json; charset=utf-8'
            ), 400
        
        # Busca contextos relevantes
        print(f"🔍 Buscando contextos para user_id: {user_id}")
        contextos_relevantes = buscar_contextos_relevantes(user_id, user_query, top_k=3)
        
        if contextos_relevantes:
            contexto_consolidado = "\n---\n".join(contextos_relevantes)
            print(f"✅ {len(contextos_relevantes)} contextos encontrados")
        else:
            contexto_consolidado = "Nenhum contexto adicional disponível."
            print("⚠️ Nenhum contexto encontrado")
        
        # Monta o prompt final
        prompt_final = f"""**Contexto Relevante:**
{contexto_consolidado}

---
**Pergunta do usuário:**
{user_query}

---
{CUSTOM_PROMPT}
"""
        
        # Determina qual IA usar
        resposta_ia = None
        erro = None
        
        # Se for admin, tenta Groq com a chave do ambiente primeiro
        if user_id == ADMIN_USER_ID:
            admin_groq_key = os.environ.get("GROQ_API_KEY")
            if admin_groq_key:
                print("🔑 Admin usando Groq (chave do ambiente)")
                resposta_ia, erro = gerar_resposta_groq(prompt_final, admin_groq_key)
            
            # Se falhar, usa Google AI
            if not resposta_ia:
                print(f"🔄 Groq falhou ({erro}), usando Google AI")
                resposta_ia, erro = gerar_resposta_google(prompt_final)
        
        # Para usuários regulares
        else:
            if groq_api_key:
                print("🔑 Usuário usando Groq (chave própria)")
                resposta_ia, erro = gerar_resposta_groq(prompt_final, groq_api_key)
                
                # Fallback para Google se Groq falhar
                if not resposta_ia:
                    print(f"🔄 Groq falhou ({erro}), usando Google AI")
                    resposta_ia, erro = gerar_resposta_google(prompt_final)
            else:
                # Se não tem chave Groq, usa Google direto
                print("🌐 Usuário usando Google AI diretamente")
                resposta_ia, erro = gerar_resposta_google(prompt_final)
        
        # Verifica se conseguiu gerar resposta
        if not resposta_ia:
            return Response(
                json.dumps({"erro": f"Falha ao gerar resposta com ambas as IAs: {erro}"}),
                mimetype='application/json; charset=utf-8'
            ), 500
        
        print("✅ Resposta gerada com sucesso")
        return Response(
            json.dumps({"resposta": resposta_ia}),
            mimetype='application/json; charset=utf-8'
        ), 200
    
    except Exception as e:
        print(f"❌ Erro no agente: {e}")
        return Response(
            json.dumps({"erro": str(e)}),
            mimetype='application/json; charset=utf-8'
        ), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return Response(
        json.dumps({"status": "healthy"}),
        mimetype='application/json; charset=utf-8'
    ), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)