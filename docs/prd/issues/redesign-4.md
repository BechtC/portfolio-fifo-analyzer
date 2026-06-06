## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/9

## What to build

Den `chart-section` mit einem Kauf/Verkauf-Timeline Chart befüllen. Chart.js Scatter-Chart: X-Achse zeigt Datum der Transaktionen, Y-Achse zeigt den Transaktionsbetrag in EUR. Käufe als grüne Punkte (▲), Verkäufe als rote Punkte (▼). Daten kommen aus `FIFO_DATA.sells` und dem Portfolio-Array. Chart-Hintergrund ist transparent (passt zum Dark-Mode-Dashboard).

## Acceptance criteria

- [ ] Chart rendert im Browser ohne Fehler
- [ ] Kauf-Datenpunkte sind grün (`emerald`), Verkauf-Datenpunkte sind rot
- [ ] X-Achse zeigt Datum, Y-Achse zeigt Betrag in EUR
- [ ] Tooltip zeigt bei Hover: Datum, Typ (Kauf/Verkauf), Betrag, Stückzahl
- [ ] Chart ist responsive (passt sich der Container-Breite an)
- [ ] Chart-Farben passen zum Dark-Mode (helle Achsenbeschriftung, transparenter Hintergrund)

## Blocked by

- https://github.com/BechtC/portfolio-fifo-analyzer/issues/10 (Grundgerüst muss existieren)
