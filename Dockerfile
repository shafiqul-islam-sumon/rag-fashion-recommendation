FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and source code
COPY requirements.txt ./
COPY src/ ./src/

# Clean old and extract chroma_store.zip directly into /tmp/
RUN rm -rf /tmp/chroma_store && unzip ./src/chroma_store.zip -d /tmp/chroma_store && chmod -R 777 /tmp/chroma_store


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Prevent Streamlit from writing to root
ENV STREAMLIT_HOME=/tmp/.streamlit
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Hugging Face cache paths (redirect to /tmp)
ENV HF_HOME=/tmp/huggingface

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "src/web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
