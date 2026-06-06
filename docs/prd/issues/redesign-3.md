## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/9

## What to build

Den `reentry-section` mit dem Re-Entry Rechner im neuen Tailwind-Design befüllen. Zwei Tabs: "Abgeschlossene Verkäufe" und "Offene Positionen". Die gesamte JS-Logik bleibt identisch zur bestehenden Implementierung — nur HTML-Struktur und Styling wechseln auf Tailwind-Klassen. LocalStorage-Historie und CSV-Export bleiben erhalten.

Tab 1: Dropdown wählt Verkauf → befüllt Felder automatisch → zeigt Break-Even Re-Entry-Kurs und nötigen Kursrückgang.
Tab 2: Lot-Auswahl → hypothetischer Verkaufskurs → KapESt+Soli Berechnung mit optionaler Kirchensteuer-Checkbox.

## Acceptance criteria

- [ ] Tab 1 "Abgeschlossene Verkäufe" funktioniert: Dropdown, Felder, Berechnung, Ergebnis
- [ ] Tab 2 "Offene Positionen" funktioniert: Lot-Karten, Auswahl, Steuerberechnung, Ergebnis
- [ ] Kirchensteuer-Checkbox aktiviert/deaktiviert die Kirchensteuer-Rate-Auswahl
- [ ] "In Historie speichern" speichert in LocalStorage und zeigt Tabelle
- [ ] CSV-Export funktioniert
- [ ] Design nutzt ausschließlich Tailwind-Klassen (kein inline-CSS außer wo nötig)
- [ ] Kein JS-Fehler in der Browser-Konsole

## Blocked by

- https://github.com/BechtC/portfolio-fifo-analyzer/issues/10 (Grundgerüst muss existieren)
