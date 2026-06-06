# Beispiel-CSV-Dateien für Portfolio FIFO Analyzer

Dieses Verzeichnis enthält Beispiel-CSV-Dateien in verschiedenen Formaten, die mit dem Portfolio FIFO Analyzer getestet werden können.

## 📁 Verfügbare Beispiele:

### `palantir_example.csv`
- **Format**: Smartbroker/Trade Republic Style
- **Trennzeichen**: Semicolon (`;`)
- **Zeitraum**: 2020-2025
- **Transaktionen**: 11 Käufe und Verkäufe
- **Besonderheiten**: Deutsche Zahlenformate mit Komma

### `amd_example.csv`
- **Format**: Comdirect Style
- **Trennzeichen**: Comma (`,`)
- **Zeitraum**: 2021-2025
- **Transaktionen**: 8 Käufe und Verkäufe
- **Besonderheiten**: Englische Spaltennamen

### `tesla_example.csv`
- **Format**: Generic Format
- **Trennzeichen**: Tab (`\t`)
- **Zeitraum**: 2022-2025
- **Transaktionen**: 6 Käufe und Verkäufe
- **Besonderheiten**: Gemischte Sprachen

## 🚀 Verwendung:

```python
# Palantir Beispiel analysieren
from portfolio_analyzer import analyze_portfolio_from_csv

analyzer = analyze_portfolio_from_csv(
    "examples/palantir_example.csv", 
    current_price=157.0, 
    currency="EUR"
)
```

## 📊 CSV-Format Anforderungen:

### Mindest-Spalten (deutsche oder englische Namen):
- **Datum/Date**: Transaktionsdatum
- **Type/Typ**: "Buy/Kauf" oder "Sell/Verkauf" 
- **Shares/Anzahl**: Anzahl Aktien
- **Price/Preis**: Kurs pro Aktie
- **Amount/Betrag**: Gesamtsumme

### Optional-Spalten:
- **Tax/Steuer**: Gezahlte Steuern
- **RealizedGains/Gewinn**: Realisierte Gewinne
- **Company/Unternehmen**: Firmenname

## 💡 Eigene CSV-Dateien erstellen:

1. **Exportiere** deine Transaktionen vom Broker
2. **Prüfe** die Spaltennamen (siehe oben)
3. **Teste** mit dem Analyzer
4. **Kopiere** ins `csvs/` Verzeichnis für reguläre Nutzung

## ⚠️ Hinweise:

- **Datenschutz**: Beispieldateien enthalten **keine echten** Finanzdaten
- **Testdaten**: Nur für Demonstrations- und Testzwecke
- **Anonymisiert**: Alle Werte sind fiktiv oder anonymisiert