# Etapa 1: Python image
FROM python:3.10.6

# Etapa 2: Define work directory
WORKDIR /app

# Etapa 3: Copy application files
COPY . /app

# Etapa 4: Install all dependecies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 6
EXPOSE 8501

# Etapa 7: Command for start streamlit 
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
