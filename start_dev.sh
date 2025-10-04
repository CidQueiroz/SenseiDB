#!/bin/bash

echo "🚀 Iniciando Ambiente de Desenvolvimento SenseiDB..."

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Iniciando Backend Django...${NC}"
echo "Acesse o frontend abrindo o arquivo 'frontend/index.html' em seu navegador."

cd backend

# Ativa o ambiente virtual, se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
fi

python manage.py runserver 8000

echo "🛑 Backend encerrado."
