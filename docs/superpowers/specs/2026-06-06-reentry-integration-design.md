# Re-Entry Rechner Integration — Design Spec

## Ziel

Den bestehenden HTML-Report (`output/*.html`) um einen eingebetteten Re-Entry-Rechner erweitern, der FIFO-Analysedaten direkt vorbelegt und eine Demo-Toggle-Funktion für sichere GitHub-Screenshots bietet.

## Feature-Überblick

### Neuer Abschnitt im Report: "Re-Entry Analyse"

Unterhalb der 12 Kennzahl-Karten erscheint ein neuer Abschnitt mit zwei Tabs:

**Tab 1 — Abgeschlossene Verkäufe**
- Dropdown mit allen Verkäufen aus `fifo_transactions` (Typ=SELL)
- Auswahl befüllt automatisch: Verkaufskurs, tatsächliche Steuern aus CSV, Gebühren (aus CSV falls vorhanden, sonst 0), Stückzahl
- Kaufkurs: ältestes noch offenes Kauflot aus `self.portfolio` als Referenz
- Berechnung: Nettokapital, benötigter Re-Entry-Kurs, nötiger Kursrückgang in %
- "In Historie speichern" + CSV-Export (LocalStorage, identisch zu re_entry_rechner.html)

**Tab 2 — Offene Positionen**
- Liste aller aktuell gehaltenen Kauflots (`self.portfolio`)
- Hypothetischer Verkaufskurs als editierbares Eingabefeld (Startwert: aktueller Kurs falls bekannt)
- Steuerberechnung: KapESt 25% + Soli 5,5%, optionale Kirchensteuer (Checkbox: 8% Bayern/BaWü, 9% andere)
- Editierbarer Freibetrag (Sparer-Pauschbetrag)
- Zeigt: Break-Even Re-Entry-Kurs, nötiger Kursrückgang

### Demo-Toggle (Security)

Button "Demo-Ansicht" im Report-Header:
- Ersetzt Aktienname durch "Demo Corp AG"
- Ersetzt alle Geldbeträge durch skalierte Zufallswerte (Verhältnisse bleiben plausibel)
- Ersetzt Stückzahlen durch Zufallswerte
- Ersetzt Datumsangaben durch generische Daten (2024-01-xx)
- Toggle: einmal klicken = Demo, nochmal = echte Daten zurück
- Rein clientseitig, keine Daten verlassen den Browser

## Technische Architektur

**Datenstrategie:** Alle FIFO-Daten werden beim Report-Generieren als JSON-Objekt in einem `<script>`-Tag eingebettet:

```javascript
const FIFO_DATA = {
  companyName: "Palantir Technologies",
  sells: [
    {
      date: "31.07.2025",
      sellPrice: 141.0,
      shares: 35,
      taxes: 1232.26,
      fee: 0,
      fifoDetails: [{ buyDate: "...", buyPrice: 112.0, shares: 35 }]
    }
  ],
  portfolio: [
    { date: "2024-01-15", price: 95.0, shares: 10 }
  ],
  currentPrice: 157.0
};
```

**Kein Server, keine API, keine externen Credentials** — rein statisches HTML.

## Security-Anforderungen

1. **Kein API-Key / keine Credentials** im generierten HTML oder im Python-Code
2. **`.gitignore`** erweitern: `csvs/*.csv`, `output/*.html` — echte Transaktionsdaten werden nie committed
3. **Demo-Toggle** maskiert alle persönlichen Finanzdaten für sichere Screenshots
4. **`examples/`-CSVs** bleiben eingecheckt als Demo-Daten für GitHub

## Nicht im Scope

- Server-seitige Verarbeitung
- Echtzeit-Kursdaten (kein API-Aufruf)
- Multi-Asset-Analyse (bestehende Limitation bleibt)
- Änderungen an der CSV-Parsing-Logik
