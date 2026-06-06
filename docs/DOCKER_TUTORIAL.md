# 🐳 Docker Tutorial - Portfolio Analyzer

**Komplette Anleitung für Docker-Einsteiger**

Docker ermöglicht es, Programme in "Containern" zu verpacken, die überall gleich laufen. Hier lernst du Docker am praktischen Beispiel des Portfolio-Analyzers.

## 📋 Was du lernst

✅ **Docker Grundlagen** - Container, Images, Volumes  
✅ **Dockerfile verstehen** - Wie Container gebaut werden  
✅ **Docker Compose** - Mehrere Services verwalten  
✅ **Praktische Anwendung** - Portfolio-Analyzer im Container  
✅ **Troubleshooting** - Häufige Probleme lösen  

## 🚀 1. Docker Installation

### Windows:
1. [Docker Desktop](https://www.docker.com/products/docker-desktop) herunterladen
2. Installieren und WSL2 aktivieren
3. Docker Desktop starten

### macOS:
1. [Docker Desktop](https://www.docker.com/products/docker-desktop) herunterladen
2. Installieren und starten

### Linux (Ubuntu/Debian):
```bash
# Docker installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Nutzer zur Docker-Gruppe hinzufügen
sudo usermod -aG docker $USER

# Neuanmeldung oder:
newgrp docker

# Docker Compose installieren
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Installation prüfen:
```bash
docker --version
docker-compose --version
```

## 📁 2. Projektstruktur einrichten

```bash
# Verzeichnis erstellen
mkdir portfolio-analyzer-docker
cd portfolio-analyzer-docker

# Unterverzeichnisse erstellen
mkdir csvs output

# Projektstruktur:
portfolio-analyzer-docker/
├── Dockerfile                 # Container-Definition
├── docker-compose.yml         # Multi-Container Setup
├── portfolio_analyzer.py      # Dein Python-Script
├── requirements.txt           # Python-Abhängigkeiten
├── csvs/                     # Deine CSV-Dateien hier rein
│   ├── palantir.csv
│   └── amd.csv
└── output/                   # HTML-Reports kommen hier rein
```

## 🔧 3. Dateien erstellen

### a) Portfolio-Analyzer kopieren
```bash
# Kopiere dein Python-Script
cp /pfad/zu/portfolio_analyzer.py .
cp /pfad/zu/requirements.txt .
```

### b) CSV-Dateien einordnen
```bash
# Kopiere deine CSV-Dateien
cp /pfad/zu/palantir.csv csvs/
cp /pfad/zu/amd.csv csvs/
```

## 🏗️ 4. Container bauen

```bash
# Container bauen (erstes Mal dauert länger)
docker build -t portfolio-analyzer .

# Mit Docker Compose:
docker-compose build
```

## 🚀 5. Container verwenden

### a) Erste Analyse durchführen:
```bash
# Mit Docker Compose (einfacher):
docker-compose run --rm analyzer data/palantir.csv 157.0 EUR
```

### b) Mehrere Analysen:
```bash
# Palantir analysieren
docker-compose run --rm analyzer data/palantir.csv 157.0 EUR

# AMD analysieren  
docker-compose run --rm analyzer data/amd.csv 120.0 USD
```

## 🌐 6. Web-Server für HTML-Reports

```bash
# Web-Server starten
docker-compose up -d webserver

# HTML-Reports öffnen
open http://localhost:8080

# Web-Server stoppen
docker-compose stop webserver
```

## 📊 7. Praktisches Beispiel - Schritt für Schritt

### Schritt 1: Setup
```bash
mkdir my-portfolio-analysis
cd my-portfolio-analysis
mkdir csvs output
```

### Schritt 2: Dateien kopieren
```bash
# Portfolio-Analyzer Script
cp /pfad/zu/portfolio_analyzer.py .
cp /pfad/zu/requirements.txt .

# CSV-Dateien
cp /pfad/zu/palantir.csv csvs/
cp /pfad/zu/amd.csv csvs/
```

### Schritt 3: Docker-Dateien erstellen
- Kopiere `Dockerfile` aus dem Repository
- Kopiere `docker-compose.yml` aus dem Repository

### Schritt 4: Container bauen
```bash
docker-compose build
```

### Schritt 5: Analysen durchführen
```bash
# Palantir analysieren
docker-compose run --rm analyzer data/palantir.csv 157.0 EUR

# Ergebnis: output/Palantir_Technologies_portfolio_analysis.html
```

### Schritt 6: Report anschauen
```bash
# Web-Server starten
docker-compose up -d webserver

# Browser öffnen: http://localhost:8080
# Klicke auf die .html Datei
```

## 🛠️ 8. Häufige Docker-Befehle

```bash
# === CONTAINER MANAGEMENT ===
docker run -it portfolio-analyzer bash    # Interaktiver Modus
docker exec -it container_name bash       # In laufenden Container einsteigen
docker logs container_name                # Container-Logs anzeigen

# === IMAGE MANAGEMENT ===
docker build -t name:tag .               # Image bauen
docker images                            # Images anzeigen
docker rmi image_name                    # Image löschen

# === SYSTEM CLEANUP ===
docker system prune                      # Aufräumen
docker system prune -a                   # Alles aufräumen

# === DOCKER COMPOSE ===
docker-compose up                        # Services starten
docker-compose up -d                     # Services im Hintergrund
docker-compose down                      # Services stoppen
docker-compose logs service_name         # Service-Logs
```

## ⚠️ 9. Troubleshooting

### Problem: "Permission denied"
```bash
# Lösung: Nutzer zur Docker-Gruppe hinzufügen
sudo usermod -aG docker $USER
# Dann neu anmelden
```

### Problem: "Port already in use"
```bash
# Anderen Port verwenden
docker run -p 8081:8080 ...
```

### Problem: "Volume not found"
```bash
# Absoluten Pfad verwenden
docker run -v /absolute/path/to/csvs:/app/data ...
```

### Problem: "CSV nicht gefunden"
```bash
# Volume-Mapping prüfen
docker-compose run --rm analyzer ls /app/data

# Sicherstellen dass CSV in csvs/ liegt
ls -la csvs/
```

---

**Erstellt mit ❤️ für bessere Portfolio-Analysen**