## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/1

## What to build

Die Historie-Funktion im Re-Entry-Abschnitt: Trades aus Tab 1 (Abgeschlossene Verkäufe) können per Button in einer persistenten Liste gespeichert werden. Die Liste wird in LocalStorage gehalten und überlebt Browser-Neustarts. Einzelne Einträge können gelöscht werden, die gesamte Liste kann geleert werden. Ein CSV-Export lädt alle gespeicherten Einträge als Datei herunter.

## Acceptance criteria

- [ ] Button "In Historie speichern" im Tab "Abgeschlossene Verkäufe" ist klickbar
- [ ] Nach Klick erscheint die Tabelle mit dem gespeicherten Eintrag (Datum, Aktie, Kauf/Verkauf, Stück, Nettokapital, Re-Entry-Kurs, Drop%)
- [ ] Tabelle bleibt nach Browser-Neustart erhalten (LocalStorage)
- [ ] Einzelner Eintrag kann per Löschen-Button entfernt werden
- [ ] "Leeren"-Button löscht nach Bestätigung alle Einträge
- [ ] "CSV Export"-Button lädt eine valide CSV-Datei herunter
- [ ] CSV enthält alle Spalten: Datum, Aktie, Kaufkurs, Verkaufskurs, Stück, NettoKapital, ReEntryKurs, DropProzent
- [ ] Wenn keine Einträge vorhanden: Tabelle ist ausgeblendet

## Blocked by

- https://github.com/BechtC/portfolio-fifo-analyzer/issues/4 (Tab Verkäufe muss existieren)
