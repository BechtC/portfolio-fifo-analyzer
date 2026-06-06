## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/1

## What to build

Eine neue Methode `_build_reentry_data()` in der Klasse `PortfolioFIFOAnalyzer` die alle für den Re-Entry-Rechner benötigten Daten aus den bereits berechneten FIFO-Ergebnissen (`self.fifo_transactions`, `self.portfolio`) als JSON-String aufbereitet.

Das JSON enthält: Aktienname, aktueller Kurs, Liste aller abgeschlossenen Verkäufe (mit Datum, Verkaufskurs, Stückzahl, tatsächlichen Steuern, Gebühren, gewichtetem Durchschnittskaufkurs aus FIFO-Lots), und Liste der noch offenen Kaufpositionen (Datum, Kaufkurs, Stückzahl).

Diese Methode ist die einzige Datenquelle für die gesamte clientseitige Re-Entry-Logik im HTML-Report.

## Acceptance criteria

- [ ] Methode `_build_reentry_data()` existiert in `PortfolioFIFOAnalyzer`
- [ ] Rückgabewert ist valides JSON (parsebar mit `json.loads()`)
- [ ] JSON enthält die Keys: `companyName`, `currentPrice`, `currency`, `sells`, `portfolio`
- [ ] Jeder Eintrag in `sells` enthält: `date`, `sellPrice`, `shares`, `taxes`, `fee`, `avgBuyPrice`, `fifoDetails`
- [ ] Jeder Eintrag in `portfolio` enthält: `date`, `buyPrice`, `shares`
- [ ] Test mit `examples/palantir.csv`: `sells` ist nicht leer wenn die CSV Verkäufe enthält
- [ ] Test mit `examples/amd.csv`: `portfolio` enthält die verbleibenden offenen Lots
- [ ] Kein Fehler wenn `self.portfolio` leer ist (alle Positionen verkauft)

## Blocked by

None - can start immediately
