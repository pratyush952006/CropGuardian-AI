FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install lightweight CPU-only PyTorch and python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and trained AI model
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY ml/model/ ./ml/model/

EXPOSE 5000

ENV PORT=5000
ENV FLASK_ENV=production

# Run with Gunicorn WSGI production server
CMD ["python", "backend/app.py", "--port", "5000"]
