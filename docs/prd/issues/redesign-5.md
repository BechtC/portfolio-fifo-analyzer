## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/9

## What to build

Den `transactions-section` mit einer vollständigen Transaktions-Tabelle befüllen. Filter-Tabs oben: "Alle", "Käufe", "Verkäufe". Spalten: Datum, Typ, Kurs (€), Stückzahl, Betrag (€), Steuer (€), FIFO-Lot Kaufkurs. Daten kommen aus `FIFO_DATA` (clientseitiges Filtern per JS). Kaufzeilen haben einen grünen linken Border, Verkaufzeilen einen roten.

## Acceptance criteria

- [ ] Tabelle zeigt alle Transaktionen aus `FIFO_DATA`
- [ ] Tab "Alle" zeigt Käufe und Verkäufe
- [ ] Tab "Käufe" zeigt nur Kauf-Transaktionen
- [ ] Tab "Verkäufe" zeigt nur Verkauf-Transaktionen
- [ ] Aktiver Tab ist visuell hervorgehoben (indigo Unterstrich)
- [ ] Kaufzeilen haben grünen linken Border, Verkaufzeilen roten
- [ ] Tabelle ist horizontal scrollbar auf Mobil
- [ ] Kein JS-Fehler in der Browser-Konsole

## Blocked by

- https://github.com/BechtC/portfolio-fifo-analyzer/issues/10 (Grundgerüst muss existieren)
