import os
import sys
from pathlib import Path

# Define o diretório raiz do projeto como o diretório pai da pasta 'scripts'
BASE_DIR = Path(__file__).resolve().parent.parent

def check_path(relative_path, is_dir=False, required=True):
    """Verifica se um arquivo ou diretório existe em relação à raiz do projeto."""
    path = BASE_DIR / relative_path
    exists = path.is_dir() if is_dir else path.is_file()
    
    if exists:
        print(f"   ✅ {relative_path}")
        return True
    else:
        icon = "❌" if required else "⚠️"
        status = '(obrigatório)' if required else '(opcional)'
        print(f"   {icon} {relative_path} {status}")
        return not required

def check_env_var(var_name, relative_path):
    """Verifica se variável está no .env"""
    filepath = BASE_DIR / relative_path
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if var_name in content and "cole-sua" not in content and "<SUA_" not in content:
                print(f"   ✅ {var_name} configurado em {relative_path}")
                return True
            else:
                print(f"   ❌ {var_name} não configurado em {relative_path}")
                return False
    except FileNotFoundError:
        return False

def main():
    print("🔍 Verificando Configuração do Projeto SenseiDB")
    print("=" * 50)
    
    all_ok = True
    
    # Estrutura de pastas principal
    print("\n📁 Estrutura de Pastas Principal:")
    all_ok &= check_path("backend/", is_dir=True)
    all_ok &= check_path("frontend/", is_dir=True)
    all_ok &= check_path("scripts/", is_dir=True)
    all_ok &= check_path("tests/", is_dir=True)
    
    # Arquivos do Backend
    print("\n🐍 Arquivos do Backend:")
    all_ok &= check_path("backend/manage.py")
    all_ok &= check_path("backend/senseidb_backend/settings.py")
    all_ok &= check_path("backend/agent/utils.py")
    
    # Configurações e Credenciais
    print("\n⚙️  Arquivos de Configuração:")
    all_ok &= check_path(".env.deploy", required=False) # Para deploy
    all_ok &= check_path("backend/.env", required=True) # Para desenvolvimento local
    all_ok &= check_path("backend/firebase_credentials.json", required=True)
    
    # Requirements
    print("\n📦 Arquivos de Dependências:")
    all_ok &= check_path("requirements.txt") # Frontend/geral
    all_ok &= check_path("backend/requirements.txt") # Backend
    
    # Variáveis de ambiente para o backend
    print("\n🔑 Variáveis de Ambiente (backend/.env):")
    if (BASE_DIR / "backend/.env").exists():
        all_ok &= check_env_var("DJANGO_SECRET_KEY", "backend/.env")
        all_ok &= check_env_var("GOOGLE_API_KEY", "backend/.env")
        all_ok &= check_env_var("GROQ_API_KEY", "backend/.env")
    
    # Resultado final
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ Configuração parece correta! Pronto para iniciar.")
        print("\nPara iniciar o desenvolvimento:")
        print("   make start")
        sys.exit(0)
    else:
        print("❌ Configuração incompleta. Corrija os itens marcados com ❌.")
        print("\nLembre-se de criar o arquivo 'backend/.env' a partir do 'backend/.env.example' e preencher suas chaves.")
        sys.exit(1)

if __name__ == "__main__":
    main()