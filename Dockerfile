# Portfolio FIFO Analyzer - Docker Container
# ==========================================
# 
# Dieses Dockerfile erstellt einen Container mit dem Portfolio-Analyzer
# Basiert auf Python 3.9 und enthält alle notwendigen Abhängigkeiten
#
# Build: docker build -t portfolio-analyzer .
# Run:   docker run -v $(pwd)/csvs:/app/data portfolio-analyzer data/your_file.csv

# === BASIS-IMAGE ===
FROM python:3.9-slim

# === METADATEN ===
LABEL maintainer="portfolio-analyzer@example.com"
LABEL version="1.0"
LABEL description="Portfolio FIFO Analyzer - Automatische Aktienportfolio-Analyse"

# === SYSTEM-UPDATES UND ABHÄNGIGKEITEN ===
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    libatlas-base-dev \
    gfortran \
    xvfb \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# === ARBEITSVERZEICHNIS ERSTELLEN ===
WORKDIR /app

# === PYTHON-ABHÄNGIGKEITEN ===
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# === MATPLOTLIB KONFIGURATION ===
ENV MPLBACKEND=Agg

# === ANWENDUNGS-CODE ===
COPY portfolio_analyzer.py .

# === VERZEICHNISSE FÜR DATEN ===
RUN mkdir -p /app/data /app/output

# === BENUTZER-EINSTELLUNGEN ===
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# === VOLUMES ===
VOLUME ["/app/data", "/app/output"]

# === STARTSCRIPT ERSTELLEN ===
USER root
RUN echo '#!/bin/bash\n\
\n\
echo "🐳 Portfolio FIFO Analyzer Container"\n\
echo "===================================="\n\
echo "Container gestartet: $(date)"\n\
echo ""\n\
\n\
if [ $# -eq 0 ]; then\n\
    echo "❌ Keine CSV-Datei angegeben!"\n\
    echo ""\n\
    echo "💡 Verwendung:"\n\
    echo "   docker run -v /pfad/zu/csvs:/app/data portfolio-analyzer data/datei.csv [aktueller_kurs] [währung]"\n\
    echo ""\n\
    echo "📁 Verfügbare CSV-Dateien in /app/data:"\n\
    ls -la /app/data/ 2>/dev/null || echo "   (Keine Dateien gefunden - Volume nicht gemounted?)"\n\
    exit 1\n\
fi\n\
\n\
CSV_FILE="$1"\n\
CURRENT_PRICE="${2:-}"\n\
CURRENCY="${3:-EUR}"\n\
\n\
echo "📊 Parameter:"\n\
echo "   CSV-Datei: $CSV_FILE"\n\
echo "   Aktueller Kurs: ${CURRENT_PRICE:-Nicht angegeben}"\n\
echo "   Währung: $CURRENCY"\n\
echo ""\n\
\n\
if [ ! -f "$CSV_FILE" ]; then\n\
    echo "❌ CSV-Datei nicht gefunden: $CSV_FILE"\n\
    echo ""\n\
    echo "📁 Verfügbare Dateien:"\n\
    find /app -name "*.csv" 2>/dev/null\n\
    exit 1\n\
fi\n\
\n\
echo "🚀 Starte Analyse..."\n\
echo ""\n\
\n\
cat > /tmp/run_analysis.py << EOF\n\
import sys\n\
sys.path.append("/app")\n\
from portfolio_analyzer import analyze_portfolio_from_csv\n\
\n\
csv_file = "$CSV_FILE"\n\
current_price = float("$CURRENT_PRICE") if "$CURRENT_PRICE" else None\n\
currency = "$CURRENCY"\n\
\n\
print(f"Analysiere: {csv_file}")\n\
analyzer = analyze_portfolio_from_csv(csv_file, current_price, currency)\n\
print(f"\\n✅ Analyse abgeschlossen!")\n\
print(f"📊 HTML-Report erstellt in: /app/output/")\n\
EOF\n\
\n\
cd /app && python /tmp/run_analysis.py\n\
\n\
cp *.html /app/output/ 2>/dev/null || true\n\
\n\
echo ""\n\
echo "🎉 Fertig! HTML-Report verfügbar in /app/output/"\n\
echo "💡 Öffne die .html Datei in deinem Browser für die Analyse"\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# === BENUTZER WECHSELN ===
USER appuser

# === PORT EXPOSITION ===
EXPOSE 8080

# === ENTRYPOINT ===
ENTRYPOINT ["/app/entrypoint.sh"]

# === STANDARD COMMAND ===
CMD ["--help"]

# === BUILD-INFORMATIONEN ===
ARG BUILD_DATE
ARG VCS_REF
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/yourusername/portfolio-fifo-analyzer" \
      org.label-schema.schema-version="1.0"

# === HEALTHCHECK ===
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import pandas, numpy, matplotlib; print('Container healthy')" || exit 1