# 🧪 Test Suite für Portfolio FIFO Analyzer

Umfassende Test-Suite mit Unit-, Integration- und End-to-End-Tests.

## 📁 Struktur

```
tests/
├── __init__.py                 # Test Package Init
├── conftest.py                 # Gemeinsame Fixtures und Konfiguration
├── test_portfolio_analyzer.py  # Unit Tests für Kernfunktionalität
├── test_csv_processing.py      # Integration Tests für CSV-Verarbeitung
├── test_fifo_analysis.py       # Integration Tests für FIFO-Logik
├── test_summary_stats.py       # Integration Tests für Statistik-Berechnung
├── test_end_to_end.py         # End-to-End Tests
├── test_data/                 # Test-CSV-Dateien
│   ├── simple_english.csv     # Einfaches Beispiel (Englisch)
│   ├── simple_german.csv      # Einfaches Beispiel (Deutsch)
│   ├── broker_format.csv      # Broker-Format (Smartbroker/TR)
│   ├── palantir_example.csv   # Komplexes Beispiel
│   ├── complete_liquidation.csv
│   └── with_losses.csv
└── README.md                  # Diese Datei
```

## 🚀 Tests ausführen

### Alle Tests ausführen

```bash
pytest
```

### Spezifische Test-Dateien ausführen

```bash
# Nur Unit Tests
pytest tests/test_portfolio_analyzer.py

# Nur CSV-Verarbeitungs-Tests
pytest tests/test_csv_processing.py

# Nur FIFO-Analyse-Tests
pytest tests/test_fifo_analysis.py

# Nur End-to-End Tests
pytest tests/test_end_to_end.py
```

### Mit Coverage-Report

```bash
# Terminal Report
pytest --cov=portfolio_analyzer --cov-report=term-missing

# HTML Report (erstellt htmlcov/index.html)
pytest --cov=portfolio_analyzer --cov-report=html

# Beide
pytest --cov=portfolio_analyzer --cov-report=term-missing --cov-report=html
```

### Verbose Output

```bash
pytest -v
```

### Nur erfolgreiche/fehlgeschlagene Tests

```bash
# Nur fehlgeschlagene Tests
pytest --lf

# Nur erfolgreiche Tests
pytest --passed
```

## 📊 Test-Kategorien

### 1. **Unit Tests** (`test_portfolio_analyzer.py`)
- ✅ Tests für `__init__()` Methode
- ✅ Tests für `print_summary_report()` Methode
- ✅ Tests für `analyze_portfolio_from_csv()` Funktion
- ⏳ Tests für noch nicht implementierte Methoden (als xfail markiert)

**Status:** Kann bereits ausgeführt werden (mocked)

### 2. **CSV-Verarbeitungs-Tests** (`test_csv_processing.py`)
- Automatische Trennzeichen-Erkennung (`;`, `,`, Tab)
- Spaltennamen-Mapping (Deutsch ↔ Englisch)
- Zahlenformat-Konvertierung (deutsche Komma → Punkt)
- Datums-Parsing (verschiedene Formate)
- Firmenname-Extraktion
- Fehlerbehandlung

**Status:** Als xfail markiert, bis `_load_and_clean_data()` implementiert ist

### 3. **FIFO-Analyse-Tests** (`test_fifo_analysis.py`)
- Grundlegende FIFO-Logik
- Mehrfache Käufe/Verkäufe
- Realisierte Gewinne/Verluste
- Unrealisierte Gewinne
- Komplexe Szenarien
- Edge Cases (Überverkauf, Verkauf vor Kauf, etc.)

**Status:** Als xfail markiert, bis `_perform_fifo_analysis()` implementiert ist

### 4. **Summary-Stats-Tests** (`test_summary_stats.py`)
- Berechnung aller Statistiken
- Cashflow-Tracking
- Rendite-Berechnung
- Edge Cases (nur Käufe, vollständige Liquidation, etc.)

**Status:** Als xfail markiert, bis `_calculate_summary_stats()` implementiert ist

### 5. **End-to-End-Tests** (`test_end_to_end.py`)
- Kompletter Workflow von CSV bis Report
- Verschiedene CSV-Formate
- Datenintegrität
- Fehlerbehandlung

**Status:** Als xfail markiert, bis vollständige Implementierung erfolgt ist

## 🎯 xfail Tests

Die meisten Tests sind derzeit als `xfail` (expected to fail) markiert, weil die Kern-Implementierung noch fehlt:

- `_load_and_clean_data()` - CSV-Verarbeitung
- `_perform_fifo_analysis()` - FIFO-Berechnung
- `_calculate_summary_stats()` - Statistik-Berechnung

**Diese Tests werden erfolgreich sein, sobald die Implementierung abgeschlossen ist!**

Sie definieren die erwartete Funktionalität und dienen als **Spezifikation** für die Implementierung.

## 📝 Test-Fixtures

In `conftest.py` definierte Fixtures:

- `test_data_dir` - Pfad zum Test-Daten-Verzeichnis
- `temp_csv_file` - Temporäre CSV-Datei für Tests
- `sample_transactions_df` - Sample DataFrame
- `simple_csv_content` - Einfacher CSV-Inhalt (Englisch)
- `german_csv_content` - CSV-Inhalt (Deutsch)
- `broker_format_csv_content` - Broker-Format CSV
- `complex_portfolio_csv_content` - Komplexes Portfolio
- `expected_analysis_results_simple` - Erwartete Ergebnisse
- `mock_analyzer_results` - Mock für Analyzer-Ergebnisse

## 🔍 Test-Daten

### `simple_english.csv`
Einfaches Szenario mit 4 Transaktionen (Englisch, Comma-separated)

### `simple_german.csv`
Einfaches Szenario mit 4 Transaktionen (Deutsch, Semicolon-separated, Komma-Dezimaltrenner)

### `broker_format.csv`
Broker-Format (Smartbroker/Trade Republic Style) mit zusätzlichen Spalten

### `palantir_example.csv`
Komplexes realistisches Beispiel mit 7 Transaktionen

### `complete_liquidation.csv`
Portfolio mit vollständiger Liquidation (alle Aktien verkauft)

### `with_losses.csv`
Portfolio mit sowohl Gewinnen als auch Verlusten

## ✅ Aktueller Status

### Kann ausgeführt werden:
- ✅ Unit Tests für `print_summary_report()` (mit Mocking)
- ✅ Unit Tests für `analyze_portfolio_from_csv()` (mit Mocking)
- ✅ Alle Test-Infrastruktur ist einsatzbereit

### Wartet auf Implementierung:
- ⏳ CSV-Verarbeitungs-Tests
- ⏳ FIFO-Analyse-Tests
- ⏳ Summary-Stats-Tests
- ⏳ End-to-End-Tests

## 🛠️ Verwendung für Entwicklung

### Test-Driven Development (TDD)

Die Tests sind bereits geschrieben und definieren die erwartete Funktionalität.

**Workflow:**

1. Wähle eine fehlende Methode (z.B. `_load_and_clean_data()`)
2. Führe die zugehörigen Tests aus: `pytest tests/test_csv_processing.py`
3. Implementiere die Methode
4. Führe Tests erneut aus, um zu prüfen ob sie bestehen
5. Wiederhole für nächste Methode

### Coverage Tracking

```bash
# Erstelle Coverage Report
pytest --cov=portfolio_analyzer --cov-report=html

# Öffne Report
open htmlcov/index.html  # MacOS
xdg-open htmlcov/index.html  # Linux
```

## 📈 Nächste Schritte

1. **Implementiere `_load_and_clean_data()`**
   - Führe `pytest tests/test_csv_processing.py -v` aus
   - Implementiere bis alle Tests bestehen

2. **Implementiere `_perform_fifo_analysis()`**
   - Führe `pytest tests/test_fifo_analysis.py -v` aus
   - Implementiere bis alle Tests bestehen

3. **Implementiere `_calculate_summary_stats()`**
   - Führe `pytest tests/test_summary_stats.py -v` aus
   - Implementiere bis alle Tests bestehen

4. **End-to-End Tests**
   - Führe `pytest tests/test_end_to_end.py -v` aus
   - Alle sollten nun bestehen!

## 🤝 Beitragen

Bei neuen Features:

1. Schreibe zuerst Tests in der entsprechenden Datei
2. Markiere sie als xfail wenn die Implementierung noch fehlt
3. Implementiere das Feature
4. Entferne xfail-Markierung wenn Tests bestehen

---

**Happy Testing! 🎉**
