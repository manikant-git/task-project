# ──────────────────────────────────────────────
# Stage 1 – Build / install dependencies
# ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools (needed for some C-extensions)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ──────────────────────────────────────────────
# Stage 2 – Runtime image (smaller)
# ──────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY app.py .

# Create a non-root user for security
RUN useradd -m appuser && chown appuser /app
USER appuser

# Expose the Flask port
EXPOSE 5000

# Run DB init then start Gunicorn (production WSGI server)
CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && \
     gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 app:app"]
