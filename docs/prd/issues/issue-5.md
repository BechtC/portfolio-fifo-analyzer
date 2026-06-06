## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/1

## What to build

Den zweiten Tab "Offene Positionen" im Re-Entry-Abschnitt implementieren. Alle noch gehaltenen Kauflots werden als Karten angezeigt. Der Nutzer wählt ein Lot aus und gibt einen hypothetischen Verkaufskurs ein (Startwert: aktueller Kurs falls bekannt). Die Steuerberechnung erfolgt mit der deutschen KapESt-Formel (25% + Soli 5,5%), mit optionaler Kirchensteuer (Checkbox, 8% oder 9%) und editierbarem Sparer-Pauschbetrag. Das Ergebnis zeigt Break-Even Re-Entry-Kurs und nötigen Kursrückgang.

## Acceptance criteria

- [ ] Tab "Offene Positionen" ist per Klick erreichbar
- [ ] Alle offenen Kauflots werden als Karten mit Kaufkurs, Stückzahl und Datum angezeigt
- [ ] Dropdown zur Lot-Auswahl für die Berechnung
- [ ] Hypothetischer Verkaufskurs ist vorbelegt mit `currentPrice` (falls vorhanden), sonst leer
- [ ] Kirchensteuer-Checkbox ist standardmäßig deaktiviert
- [ ] Bei aktivierter Kirchensteuer: Auswahl 8% (Bayern/BaWü) oder 9% (andere BL)
- [ ] Freibetrag-Feld akzeptiert Eingabe und verändert die Steuerberechnung korrekt
- [ ] Berechnung aktualisiert sich sofort bei jeder Eingabeänderung
- [ ] Wenn keine offenen Positionen vorhanden: Hinweis "Keine offenen Positionen vorhanden"
- [ ] Kein JavaScript-Fehler in der Browser-Konsole

## Blocked by

- https://github.com/BechtC/portfolio-fifo-analyzer/issues/3 (`_build_reentry_data()` muss existieren)
