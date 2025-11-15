# 📁 Beispiel-CSV-Dateien

Dieses Verzeichnis enthält Beispiel-CSV-Dateien zum Testen des Portfolio FIFO Analyzers.

## 📋 Verfügbare Beispiele

### 1. **palantir_example.csv**
- **Unternehmen:** Palantir Technologies
- **Zeitraum:** Januar 2023 - Juli 2024
- **Transaktionen:** 8 (5 Käufe, 3 Verkäufe)
- **Komplexität:** Mittel
- **Besonderheiten:**
  - Mehrere FIFO-Matches über Zeitraum
  - Realisierte Gewinne in verschiedenen Größenordnungen
  - Steuerberechnungen
  - Verbleibende Positionen

**Beispiel-Verwendung:**
```bash
python portfolio_analyzer.py
```
Dann anpassen:
```python
csv_file = "examples/palantir_example.csv"
current_price = 35.00  # Aktueller Palantir-Kurs
currency = "EUR"
```

### 2. **nvidia_example.csv**
- **Unternehmen:** NVIDIA Corporation
- **Zeitraum:** Januar - Mai 2024
- **Transaktionen:** 5 (3 Käufe, 2 Verkäufe)
- **Komplexität:** Mittel
- **Format:** Deutsch (Semicolon-separated, Komma als Dezimaltrenner)
- **Besonderheiten:**
  - Deutsches CSV-Format
  - Deutsche Spaltennamen
  - Höhere Aktienkurse

**Beispiel-Verwendung:**
```python
from portfolio_analyzer import analyze_portfolio_from_csv

analyzer = analyze_portfolio_from_csv(
    "examples/nvidia_example.csv",
    current_price=485.00,
    currency="EUR"
)

# HTML-Report generieren
analyzer.generate_html_report("output/nvidia_report.html")
```

### 3. **simple_example.csv**
- **Unternehmen:** Simple Stock
- **Zeitraum:** Januar - März 2024
- **Transaktionen:** 3 (2 Käufe, 1 Verkauf)
- **Komplexität:** Einfach
- **Besonderheiten:**
  - Minimales Beispiel für Schnellstart
  - Einfache FIFO-Berechnung
  - Gut für Tests

**Beispiel-Verwendung:**
```python
from portfolio_analyzer import analyze_portfolio_from_csv

analyzer = analyze_portfolio_from_csv(
    "examples/simple_example.csv",
    current_price=65.00,
    currency="EUR"
)
```

## 🔧 CSV-Format-Anforderungen

### Erforderliche Spalten

#### Englisches Format (Comma-separated):
```csv
Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,100,50.00,5000.00,0.00,Company Name
```

#### Deutsches Format (Semicolon-separated):
```csv
Datum;Typ;Anzahl;Preis;Betrag;Steuer;Unternehmen
15.01.2024;Kauf;100;50,00;5000,00;0,00;Firmenname
```

### Optionale Spalten
- **RealizedGains / Gewinn**: Bereits berechnete realisierte Gewinne
- **Fee / Gebühr**: Transaktionsgebühren
- **Time / Zeit**: Uhrzeit der Transaktion
- **DateTime**: Kombiniertes Datum/Zeit-Feld

## 📊 Erwartete Ausgabe

Für jedes Beispiel kannst du folgende Ausgaben erwarten:

### Console Output
```
🚀 [COMPANY] PORTFOLIO-ANALYSE (FIFO)
============================================================

💰 INVESTITIONS-ÜBERSICHT:
   Gesamt eingezahlt: X.XXX EUR
   Gesamt entnommen:  X.XXX EUR

📈 REALISIERTE GEWINNE:
   Brutto-Gewinne:    X.XXX EUR
   Steuern gezahlt:   XXX EUR
   Netto-Gewinne:     X.XXX EUR

🎯 GESAMTERGEBNIS:
   Gesamtgewinn:      X.XXX EUR
   Netto-Cashflow:    X.XXX EUR
   Gesamtrendite:     XX.X%
```

### HTML-Report
- 12 interaktive Kennzahl-Karten
- Transaktionshistorie-Tabelle
- Portfolio-Positionen-Übersicht
- Responsive Design

## 🧪 Eigene CSV-Dateien erstellen

### Schritt 1: Daten exportieren
Exportiere deine Transaktionen von deinem Broker im CSV-Format.

### Schritt 2: Format anpassen (falls nötig)
Stelle sicher, dass die CSV mindestens diese Spalten enthält:
- Datum/Date
- Typ/Type (Buy/Kauf oder Sell/Verkauf)
- Anzahl/Shares
- Preis/Price
- Betrag/Amount

### Schritt 3: In `csvs/` speichern
```bash
cp meine_transaktionen.csv csvs/meine_aktie.csv
```

### Schritt 4: Analysieren
```python
from portfolio_analyzer import analyze_portfolio_from_csv

analyzer = analyze_portfolio_from_csv(
    "csvs/meine_aktie.csv",
    current_price=100.00,  # Aktueller Kurs
    currency="EUR"
)

# HTML-Report erstellen
analyzer.generate_html_report("output/meine_aktie_report.html")
```

## ⚠️ Wichtige Hinweise

1. **Datenschutz**: Beispieldateien enthalten fiktive Daten. Deine echten Transaktionsdaten sollten im `csvs/` Ordner gespeichert werden (der in `.gitignore` ist).

2. **Steuerliche Korrektheit**: Die FIFO-Berechnungen sind für deutsche Steuergesetze optimiert. Bei anderen Ländern können abweichende Regeln gelten.

3. **Genauigkeit**: Alle Berechnungen sollten vor steuerlichen Entscheidungen von einem Steuerberater überprüft werden.

4. **Währungen**: Das Tool unterstützt verschiedene Währungen, berechnet aber keine Wechselkurse. Alle Transaktionen sollten in derselben Währung sein.

## 📞 Support

Bei Fragen zu den Beispielen oder eigenen CSV-Dateien:
- Siehe [README.md](../README.md#-troubleshooting) im Hauptverzeichnis
- Öffne ein [GitHub Issue](https://github.com/BechtC/portfolio-fifo-analyzer/issues)
