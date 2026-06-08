# BioDex CPU Docker image
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="BioDex" \
      org.opencontainers.image.description="Local-first wildlife camera trap AI analysis (CPU)" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md constraints.txt ./
COPY core ./core
COPY ui ./ui
COPY app.py ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -c constraints.txt ".[ui,models,video]"

EXPOSE 7860
ENV BIODEX_HOST=0.0.0.0 BIODEX_DEPLOY=1
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('127.0.0.1',7860)); s.close()"

CMD ["biodex-ui"]
