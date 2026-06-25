FROM python:3.13-slim

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente y assets
COPY . .

# Puerto que Railway asigna dinámicamente
EXPOSE 8080

CMD ["python", "PaginaBienvenida.py"]
