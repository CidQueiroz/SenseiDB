FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia aplicação
COPY backend/ .

# Coleta estáticos
RUN python manage.py collectstatic --noinput || true

# Executa as migrações do banco de dados
RUN python manage.py migrate

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 senseidb_backend.wsgi:application