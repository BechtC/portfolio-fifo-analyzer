# HTML-Reports Output

Hier werden die generierten HTML-Reports gespeichert.

## 📊 Automatisch generierte Dateien:

```
output/
├── Palantir_Technologies_portfolio_analysis.html
├── AMD_Inc_portfolio_analysis.html
├── Tesla_Inc_portfolio_analysis.html
└── ...
```

## 🌐 Web-Server:

Die HTML-Reports können über den integrierten Web-Server angezeigt werden:

```bash
# Web-Server starten
docker-compose up -d webserver

# Browser öffnen
open http://localhost:8080
```

## 📱 Features der HTML-Reports:

- ✅ **Responsive Design** - funktioniert auf allen Geräten
- ✅ **Interaktive Charts** - mit Chart.js
- ✅ **12 Kennzahl-Karten** - übersichtliches Dashboard
- ✅ **FIFO-Details** - detaillierte Transaktionshistorie
- ✅ **Portfolio-Positionen** - aktuelle Bestände
- ✅ **Performance-Metriken** - Gesamtrendite und Cashflow

## 💡 Tipp:

Die HTML-Reports sind **selbstständig** und können:
- Per **Email** versendet werden
- Auf **USB-Stick** gespeichert werden
- In **Cloud-Storage** hochgeladen werden
- Als **Backup** archiviert werden

## 🔧 Anpassungen:

Falls du das Design anpassen möchtest, bearbeite die HTML-Template-Funktion in `portfolio_analyzer.py`.