# 🚀 Portfolio FIFO Analyzer

**Automatische FIFO-Analyse für Aktien-Portfolios mit professioneller HTML-Darstellung**

Ein Python-Tool, das Portfolio-CSVs automatisch analysiert und detaillierte Reports im HTML-Format erstellt. Perfekt für die steuerrechtlich korrekte FIFO-Analyse (First-In-First-Out) von Aktienverkäufen.

## 📋 Features

### 🎯 **Automatische CSV-Erkennung**
- ✅ Erkennt Trennzeichen automatisch (`;`, `,`, Tab, `|`)
- ✅ Unterstützt deutsche und englische Spaltennamen
- ✅ Konvertiert deutsche Zahlenformate (Komma → Punkt)
- ✅ Flexible Datumsformate (DD.MM.YYYY, YYYY-MM-DD, etc.)

### 📊 **FIFO-Analyse**
- ✅ Steuerrechtlich korrekte First-In-First-Out Zuordnung
- ✅ Detaillierte Gewinn/Verlust-Berechnung pro Transaktion
- ✅ Automatische Steuerberechnung
- ✅ Unrealisierte Gewinne für aktuellen Bestand

### 📈 **Professionelle HTML-Reports**
- ✅ Responsive Design mit interaktiven Charts
- ✅ 12 Übersichtskarten mit wichtigsten Kennzahlen
- ✅ Detaillierte Transaktionshistorie mit FIFO-Zuordnung
- ✅ Portfolio-Positionen-Tabelle mit Performance
- ✅ Chart.js Integration für interaktive Diagramme

### 💡 **Universell einsetzbar**
- ✅ Funktioniert mit allen Aktien-CSVs (Palantir, AMD, Tesla, etc.)
- ✅ Verschiedene Broker-Formate unterstützt
- ✅ Automatische Firmenname-Erkennung
- ✅ Mehrere Währungen (EUR, USD, etc.)

## 🚀 Schnellstart

### 1. Installation

```bash
# Repository klonen oder Dateien herunterladen
git clone https://github.com/yourusername/portfolio-fifo-analyzer.git
cd portfolio-fifo-analyzer

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### 2. CSV-Datei vorbereiten

Stelle sicher, dass deine CSV-Datei diese Spalten enthält (deutsche oder englische Namen):
- **Datum/Date**: Transaktionsdatum
- **Type/Typ**: "Buy/Kauf" oder "Sell/Verkauf"
- **Shares/Anzahl**: Anzahl Aktien
- **Price/Preis**: Kurs pro Aktie
- **Amount/Betrag**: Gesamtsumme
- **Tax/Steuer**: Gezahlte Steuern (optional)
- **RealizedGains/Gewinn**: Realisierte Gewinne (optional)

### 3. Script ausführen

```python
python portfolio_analyzer.py
```

**Oder direkt im Code anpassen:**

```python
# Am Ende der portfolio_analyzer.py Datei:
csv_file = "csvs/deine_aktien.csv"      # Pfad zur CSV-Datei
current_price = 150.0                   # Aktueller Aktienkurs
currency = "EUR"                        # Währung

analyzer = analyze_portfolio_from_csv(csv_file, current_price, currency)
```

## 📊 Beispiel-Output

### Console Output:
```
🚀 PALANTIR TECHNOLOGIES PORTFOLIO-ANALYSE (FIFO)
============================================================

💰 INVESTITIONS-ÜBERSICHT:
   Gesamt eingezahlt: 10.226 EUR
   Gesamt entnommen:  23.259 EUR

📈 REALISIERTE GEWINNE:
   Brutto-Gewinne:    21.116 EUR
   Steuern gezahlt:   5.087 EUR
   Netto-Gewinne:     16.030 EUR

🎯 GESAMTERGEBNIS:
   Gesamtgewinn:      70.338 EUR
   Gesamtrendite:     688.0%
```

### HTML-Report:
- **Professionelles Dashboard** mit 12 Kennzahl-Karten
- **Interaktive Charts** für Portfolio-Entwicklung
- **Detaillierte FIFO-Historie** mit Verkaufszuordnungen
- **Aktuelle Positionen** mit unrealisierten Gewinnen

## 🔧 Unterstützte CSV-Formate

### Smartbroker/Trade Republic Format:
```csv
datetime;date;time;price;shares;amount;tax;fee;realizedgains;type;holdingname
2025-07-31T14:04:05.000Z;31.07.2025;16:04:00;141;35;4935;1232,26;0;4673,58;Sell;Palantir Technologies
```

### Comdirect/ING Format:
```csv
Datum,Typ,Aktien,Preis,Summe,Steuer,Unternehmen
31.07.2025,Verkauf,35,141.00,4935.00,1232.26,Palantir Technologies
```

### Allgemeines Format:
```csv
Date,Type,Shares,Price,Amount,Tax,Company
2025-07-31,Sell,35,141.00,4935.00,1232.26,Palantir Technologies
```

## 📁 Projektstruktur

```
portfolio-fifo-analyzer/
├── portfolio_analyzer.py    # Hauptscript
├── requirements.txt         # Python-Abhängigkeiten
├── README.md               # Diese Dokumentation
├── Dockerfile              # Docker-Container
├── docker-compose.yml      # Docker-Services
├── examples/               # Beispiel-CSV-Dateien
├── csvs/                   # Deine CSV-Dateien
├── output/                 # Generierte HTML-Reports
└── docs/                   # Erweiterte Dokumentation
```

## ⚙️ Konfiguration

### Verschiedene Währungen:
```python
# EUR (Standard)
analyzer = analyze_portfolio_from_csv("aktien.csv", 150.0, "EUR")

# USD
analyzer = analyze_portfolio_from_csv("stocks.csv", 180.0, "USD")

# GBP
analyzer = analyze_portfolio_from_csv("shares.csv", 120.0, "GBP")
```

### Ohne aktuellen Kurs:
```python
# Nur historische Analyse ohne aktuelle Bewertung
analyzer = analyze_portfolio_from_csv("aktien.csv")
```

## 🐳 Docker Support

### Mit Docker verwenden:
```bash
# Container bauen
docker-compose build

# Analyse durchführen
docker-compose run --rm analyzer data/palantir.csv 157.0 EUR

# Web-Server für HTML-Reports starten
docker-compose up -d webserver
# Dann öffne: http://localhost:8080
```

## 🎯 Praktische Anwendungsfälle

### 1. Steuerliche Dokumentation
- FIFO-konforme Verkaufszuordnung für Steuererklärung
- Detaillierte Gewinn/Verlust-Aufstellung
- Übersicht über gezahlte Abgeltungssteuern

### 2. Portfolio-Performance-Tracking
- Gesamtrendite über alle Transaktionen
- Unrealisierte Gewinne des aktuellen Bestands
- Entwicklung der Portfolio-Größe über Zeit

### 3. Investment-Entscheidungen
- Kostenbasis der aktuellen Positionen
- Performance einzelner Kauftranchen
- Optimaler Verkaufszeitpunkt (steuerlich)

## 🛠️ Troubleshooting

### Problem: CSV wird nicht erkannt
**Lösung:**
- Überprüfe das Trennzeichen (`;` vs `,`)
- Stelle sicher, dass Header-Zeile vorhanden ist
- Prüfe die Encoding (UTF-8 vs. Latin-1)

### Problem: Zahlenformat nicht erkannt
**Lösung:**
- Deutsche Formate: `1234,56` → wird automatisch zu `1234.56`
- Tausendertrennzeichen werden automatisch entfernt
- Leere Zellen werden als `0` interpretiert

### Problem: Datum nicht erkannt
**Lösung:**
- Unterstützte Formate: `DD.MM.YYYY`, `YYYY-MM-DD`, `DD/MM/YYYY`
- ISO-Format mit Zeitstempel: `2025-07-31T14:04:05.000Z`

## 📋 To-Do / Geplante Features

- [ ] **Multi-Asset Support**: Mehrere Aktien in einer Analyse
- [ ] **PDF-Export**: Automatische PDF-Generierung
- [ ] **Excel-Export**: Detaillierte Tabellen als .xlsx
- [ ] **Dividenden-Tracking**: Integration von Dividendenzahlungen
- [ ] **Benchmark-Vergleich**: Performance vs. Marktindizes
- [ ] **Steuer-Optimierung**: Vorschläge für steueroptimale Verkäufe

## 🤝 Beitragen

Verbesserungen und Erweiterungen sind willkommen! 

1. Fork das Repository
2. Erstelle einen Feature-Branch: `git checkout -b feature/neue-funktion`
3. Committe deine Änderungen: `git commit -m 'Neue Funktion hinzugefügt'`
4. Push zum Branch: `git push origin feature/neue-funktion`
5. Erstelle einen Pull Request

## ⚖️ Rechtlicher Hinweis

**Wichtig:** Dieses Tool dient nur zur Unterstützung bei der Portfolioanalyse. Es ersetzt keine professionelle Steuerberatung. Alle Berechnungen sollten vor steuerlichen Entscheidungen von einem Steuerberater überprüft werden.

**Haftungsausschluss:** Die Korrektheit der FIFO-Berechnungen wird nicht garantiert. Nutzer sind selbst für die Überprüfung der Ergebnisse verantwortlich.

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei für Details.

## 📞 Support

Bei Fragen oder Problemen:
- **Issues**: [GitHub Issues](https://github.com/yourusername/portfolio-fifo-analyzer/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/yourusername/portfolio-fifo-analyzer/discussions)

---

**Erstellt mit ❤️ für bessere Portfolio-Analysen**