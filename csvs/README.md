# Lege deine CSV-Dateien hier ab

Dieses Verzeichnis ist für deine echten Portfolio-CSV-Dateien vorgesehen.

## 📁 Empfohlene Struktur:

```
csvs/
├── palantir20250808103935.csv    # Deine echte Palantir-CSV
├── amd20250808103935.csv         # Deine echte AMD-CSV
├── tesla_transactions.csv        # Weitere Aktien-CSVs
└── ...
```

## 🚀 Verwendung:

```python
# In portfolio_analyzer.py anpassen:
csv_file = "csvs/deine_datei.csv"
current_price = 157.0
currency = "EUR"

analyzer = analyze_portfolio_from_csv(csv_file, current_price, currency)
```

## 📊 Mit Docker:

```bash
# CSV-Dateien analysieren
docker-compose run --rm analyzer data/palantir20250808103935.csv 157.0 EUR
docker-compose run --rm analyzer data/amd20250808103935.csv 120.0 USD
```

## ⚠️ Wichtig:

- **Originaldateien** hier ablegen
- **Nicht** ins Git Repository committen (sensible Daten)
- **Backup** deiner CSV-Dateien erstellen
- **Datenschutz** beachten bei Sharing

## 💡 CSV-Format:

Stelle sicher, dass deine CSV-Dateien diese Spalten enthalten:
- Datum/Date
- Type/Typ (Buy/Sell oder Kauf/Verkauf)
- Shares/Anzahl 
- Price/Preis
- Amount/Betrag
- Tax/Steuer (optional)
- RealizedGains/Gewinn (optional)