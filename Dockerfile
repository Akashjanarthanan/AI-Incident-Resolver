FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV HF_HOME=/root/.cache/huggingface

WORKDIR /workspace

# Runtime library required by common scientific Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

# Copy the application, knowledge base, frontend and index
COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--app-dir", "app", "--host", "0.0.0.0", "--port", "8000"]