# Multi-stage Dockerfile for Wigor Viewer CLI
# Stage 1: Build executable with PyInstaller
FROM python:3.10-slim AS builder

# Métadonnées
LABEL maintainer="wigor-viewer-team@example.com"
LABEL description="Wigor Viewer CLI - Build stage"
LABEL stage="builder"

# Variables d'environnement pour le build
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Installation des dépendances système nécessaires pour le build
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    binutils \
    g++ \
    gcc \
    python3-dev \
    upx-ucl \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt requirements-dev.txt ./

# Installation des dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt && \
    pip install pyinstaller>=5.13.0

# Copie du code source complet
COPY . .

# Exécution des tests et vérifications qualité
RUN echo "🧪 Running tests and quality checks..." && \
    # Tests de régression
    python -m pytest test_regression.py -v --tb=short && \
    # Smoke test CLI
    python -m src.cli --check && \
    python -m src.cli --version && \
    echo "✅ All tests passed"

# Nettoyage des builds précédents
RUN rm -rf ./dist/ ./build/ ./*.spec

# Construction de l'exécutable PyInstaller
RUN echo "🏗️ Building executable with PyInstaller..." && \
    pyinstaller wigor.spec --clean --noconfirm && \
    echo "✅ Executable built successfully"

# Vérification que l'exécutable fonctionne
RUN echo "🔍 Testing executable..." && \
    ./dist/wigor-viewer --version && \
    ./dist/wigor-viewer --check && \
    echo "✅ Executable verification completed"

# Compression avec UPX si disponible
RUN if command -v upx >/dev/null 2>&1; then \
        echo "📦 Compressing executable with UPX..." && \
        upx --best --lzma ./dist/wigor-viewer || true; \
    fi

# Stage 2: Runtime image minimal
FROM python:3.10-slim AS runtime

# Métadonnées de l'image finale
LABEL maintainer="wigor-viewer-team@example.com"
LABEL description="Wigor Viewer CLI - Lightweight runtime"
LABEL version="2.0"
LABEL stage="runtime"

# Variables d'environnement runtime
ENV PYTHONUNBUFFERED=1
ENV PATH="/app:$PATH"

# Installation des dépendances runtime et création utilisateur
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && useradd --create-home --shell /bin/bash --uid 1000 wigor

# Répertoire de travail
WORKDIR /app

# Copie de l'exécutable depuis le stage builder
COPY --from=builder /app/dist/wigor-viewer /app/wigor-viewer

# Copie des fixtures nécessaires pour les tests CLI
COPY --from=builder /app/fixtures /app/fixtures

# Permissions et propriétaire
RUN chmod +x /app/wigor-viewer \
    && chown -R wigor:wigor /app

# Utilisateur non-root
USER wigor

# Vérification de santé de l'image
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/wigor-viewer --version || exit 1

# Métadonnées additionnelles
LABEL org.opencontainers.image.title="Wigor Viewer CLI"
LABEL org.opencontainers.image.description="CLI tool for EPSI Wigor timetable viewing"
LABEL org.opencontainers.image.vendor="EPSI"
LABEL org.opencontainers.image.version="2.0"
LABEL org.opencontainers.image.licenses="MIT"

# Point d'entrée par défaut avec smoke test
ENTRYPOINT ["/app/wigor-viewer"]
CMD ["--check"]