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
COPY biodex ./biodex
COPY app.py ./

# Models install order mirrors scripts/install_biodex.sh to avoid the
# megadetector/speciesnet protobuf + onnx ResolutionImpossible. CPU torch is
# installed before megadetector so its torch dependency is already satisfied
# (keeps the multi-GB CUDA wheels out of the CPU image).
RUN pip install --no-cache-dir --upgrade pip wheel \
    && pip install --no-cache-dir "protobuf==3.20.1" \
    && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir "megadetector>=10.0,<11.0" \
    && pip install --no-cache-dir "Pillow>=9.5" "numpy>=1.26.4,<2.0" "pandas>=2.1" "tqdm>=4.64" "setuptools>=65.0,<81.0" \
    && (pip install --no-cache-dir "speciesnet>=5.0,<6.0" || pip install --no-cache-dir "speciesnet>=5.0,<6.0" --no-deps) \
    && pip install --no-cache-dir ".[ui,video]" \
    && pip install --no-cache-dir "protobuf==3.20.1" --force-reinstall

EXPOSE 7860
ENV BIODEX_HOST=0.0.0.0 BIODEX_DEPLOY=1
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('127.0.0.1',7860)); s.close()"

CMD ["biodex-ui"]
