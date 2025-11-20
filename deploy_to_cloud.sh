#!/bin/bash

echo "☁️  Deploy SenseiDB para Google Cloud"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Carrega configurações do .env.deploy
echo -e "${BLUE}📝 Carregando configurações de .env.deploy...${NC}"
if [ -f .env.deploy ]; then
    set -a # Automatically export all variables
    source .env.deploy
    set +a # Stop automatically exporting
else
    echo -e "${RED}❌ Arquivo .env.deploy não encontrado!${NC}"
    exit 1
fi

if [ -z "$PROJECT_ID" ] || [ -z "$GOOGLE_API_KEY" ] || [ -z "$DJANGO_SECRET_KEY" ]; then
    echo -e "${RED}❌ Variáveis essenciais não estão definidas no .env.deploy!${NC}"
    exit 1
fi

REGION=${REGION:-southamerica-east1}

echo "   Project: $PROJECT_ID"
echo "   Região: $REGION"
echo -e "${GREEN}✅ Configurações carregadas.${NC}"

gcloud config set project $PROJECT_ID

echo ""
echo -e "${BLUE}🚀 Deploy do Backend Django usando o Dockerfile...${NC}"

# O comando agora roda da raiz, e o --source=. faz com que ele encontre o Dockerfile
gcloud run deploy senseidb-agent \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --clear-base-image \
    --set-env-vars="GOOGLE_API_KEY=$GOOGLE_API_KEY,GROQ_API_KEY=$GROQ_API_KEY,DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY,DEBUG=False,ADMIN_USER_ID=$ADMIN_USER_ID" \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend deployado com sucesso!${NC}"
    BACKEND_URL=$(gcloud run services describe senseidb-agent --region $REGION --format="value(status.url)")
    echo -e "${GREEN}📍 URL do Backend: $BACKEND_URL${NC}"
else
    echo -e "${RED}❌ Erro no deploy do backend${NC}"
    exit 1
fi