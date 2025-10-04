.PHONY: help setup start test check deploy clean

help:
	@echo "🧠 SenseiDB - Comandos Disponíveis"
	@echo ""
	@echo "  make setup    - Configura o projeto inicial"
	@echo "  make check    - Verifica configuração"
	@echo "  make start    - Inicia ambiente de desenvolvimento"
	@echo "  make test     - Executa testes do sistema"
	@echo "  make deploy   - Deploy para Google Cloud"
	@echo "  make clean    - Limpa arquivos temporários"
	@echo ""

check:
	@echo "🔍 Verificando configuração..."
	@python3 scripts/check_config.py

start:
	@echo "🚀 Iniciando ambiente de desenvolvimento..."
	@chmod +x start_dev.sh
	@./start_dev.sh

test:
	@echo "🧪 Executando testes..."
	@python3 tests/test_system.py

deploy:
	@echo "☁️  Iniciando deploy..."
	@chmod +x deploy_to_cloud.sh
	@./deploy_to_cloud.sh

clean:
	@echo "🧹 Limpando arquivos temporários..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.log" -delete
	@rm -rf backend/db.sqlite3
	@echo "✅ Limpeza concluída!"