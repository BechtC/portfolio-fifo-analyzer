## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/1

## What to build

Den generierten HTML-Report um einen neuen Abschnitt "Re-Entry Analyse" erweitern — Tab "Abgeschlossene Verkäufe". Ein Dropdown listet alle Verkäufe. Bei Auswahl werden Verkaufskurs, tatsächliche Steuern, Stückzahl und Gebühren automatisch eingetragen. Als Referenz-Kaufkurs wird das älteste noch offene Lot aus dem Portfolio verwendet. Der Rechner zeigt sofort: Nettokapital, Gewinn vor Steuern, Steuern, Break-Even Re-Entry-Kurs und nötigen Kursrückgang in Prozent. Alle Felder sind manuell überschreibbar.

Das eingebettete JSON-Objekt (`FIFO_DATA`) aus Issue #3 ist die Datenquelle — kein Server, keine API.

## Acceptance criteria

- [ ] Report enthält `<script>const FIFO_DATA = ...;</script>` mit den FIFO-Daten
- [ ] Abschnitt "Re-Entry Analyse" erscheint unterhalb der Kennzahl-Karten
- [ ] Tab "Abgeschlossene Verkäufe" ist der Standard-Tab beim Öffnen
- [ ] Dropdown zeigt alle SELL-Transaktionen mit Datum und Verkaufskurs
- [ ] Auswahl eines Verkaufs befüllt alle Felder automatisch
- [ ] Kaufkurs-Feld zeigt das älteste offene Lot; bei leerem Portfolio den gewichteten Durchschnittskaufkurs
- [ ] Berechnung aktualisiert sich sofort bei jeder Eingabeänderung (kein Submit-Button nötig)
- [ ] Break-Even Re-Entry-Kurs und prozentualer Rückgang werden korrekt angezeigt
- [ ] Design passt zum bestehenden Report-Stil (kein Tailwind, kein zusätzliches CDN)
- [ ] Kein JavaScript-Fehler in der Browser-Konsole

## Blocked by

- https://github.com/BechtC/portfolio-fifo-analyzer/issues/3 (`_build_reentry_data()` muss existieren)
