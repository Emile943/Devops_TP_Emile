FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN useradd -u 1000 appuser && apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local /usr/local
COPY . /app/
USER appuser
HEALTHCHECK --interval=5s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["python", "app.py"]
