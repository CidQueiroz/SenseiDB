FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=senseidb_backend.settings
ENV PORT=8000

WORKDIR /app

# Instala dependências do sistema
# gcc e python3-dev são necessários para compilar numpy e outras libs se necessário
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Atualiza pip e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta (variável dinâmica para Cloud Run ou fixa para OCI)
EXPOSE 8000

# Script de entrada para garantir migrações e coleta de estáticos antes de iniciar
# O uso de sh -c permite a expansão da variável $PORT
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 senseidb_backend.wsgi:application"]
