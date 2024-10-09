FROM python:3.10-slim

WORKDIR /app

# Copiar o arquivo de dependências
COPY requirements.txt .

# Atualizar pip e instalar dependências
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos personalizados da aplicação
COPY .streamlit/ .streamlit/

# Executar o streamlit
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
