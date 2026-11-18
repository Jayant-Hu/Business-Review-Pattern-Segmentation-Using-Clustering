# Multi-stage production build for UrbanPulse AI
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final lean runtime image
FROM python:3.11-slim AS runner

WORKDIR /app

# Non-root user setup
RUN groupadd -r urbanpulse && useradd -r -g urbanpulse urbanpulse

# Copy installed wheels from builder
COPY --from=builder /root/.local /home/urbanpulse/.local
ENV PATH=/home/urbanpulse/.local/bin:$PATH

# Copy application code
COPY . .

# Set permissions
RUN chown -R urbanpulse:urbanpulse /app

USER urbanpulse

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
