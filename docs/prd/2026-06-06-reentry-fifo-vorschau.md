# PRD: Re-Entry Rechner — FIFO-Vorschau & Chargen-Anzeige

## Problem Statement

Der Re-Entry Rechner zeigt aktuell nur aggregierte Zahlen für historische Verkäufe (Gesamterlös, Break-Even, Steuern). Zwei wesentliche Informationen fehlen:

1. **Offene Positionen:** Der Anleger kann nicht simulieren, was passiert wenn er aktuell gehaltene Aktien (mit unterschiedlichen Einstiegspreisen) ganz oder teilweise verkauft. Er weiß nicht, welche FIFO-Chargen betroffen wären, wie hoch der Gewinn je Charge ist und welche Steuerlast pro Charge anfiele.

2. **Historische Verkäufe:** Wenn ein historischer Verkauf ausgewählt wird, sieht der Anleger nicht, welche Kaufchargen (FIFO-Lots) dabei aufgelöst wurden — also wann er diese Stücke gekauft hat und welcher Gewinn je Lot entstanden ist.

Das macht es schwer, fundierte Entscheidungen über Zeitpunkt und Umfang eines Verkaufs zu treffen.

## Solution

Der Re-Entry Rechner wird um zwei Bereiche erweitert:

**A) FIFO-Vorschau für offene Positionen (Verkaufssimulation)**
Der Anleger kann einen Zielkurs und eine frei wählbare Stückzahl (Teilverkauf oder Gesamtbestand) eingeben. Der Rechner berechnet daraufhin FIFO-genau, welche Chargen aufgelöst würden, und zeigt eine Tabelle mit Gewinn und Steuerschätzung je Charge sowie einem Gesamtsaldo.

**B) Chargen-Anzeige bei historischen Verkäufen**
Wenn ein historischer Verkauf ausgewählt wird, erscheint unter den Kennzahlen eine Tabelle der betroffenen FIFO-Lots (aus `fifoDetails`): Kaufdatum, Kaufkurs, Stückzahl, Gewinn je Lot, Steueranteil je Lot.

## User Stories

1. Als Privatanleger möchte ich beim Re-Entry Rechner zwischen "historischen Verkäufen" und "offene Positionen simulieren" wählen können, damit ich beide Szenarien vergleichen kann.
2. Als Privatanleger möchte ich einen Zielkurs für einen geplanten Verkauf eingeben können, damit der Rechner mir zeigt was bei diesem Kurs passieren würde.
3. Als Privatanleger möchte ich eine frei wählbare Stückzahl für die Verkaufssimulation eingeben können, damit ich Teilverkäufe simulieren kann.
4. Als Privatanleger möchte ich einen Schnellknopf "Gesamten Bestand" haben, damit die Stückzahl automatisch auf alle offenen Positionen gesetzt wird.
5. Als Privatanleger möchte ich in der FIFO-Vorschau sehen, welche Chargen in welcher Reihenfolge aufgelöst würden (älteste zuerst), damit ich die FIFO-Logik nachvollziehen kann.
6. Als Privatanleger möchte ich je Charge sehen: Kaufdatum, Kaufkurs, betroffene Stückzahl, Gewinn, geschätzte Steuer, damit ich verstehe wie der Gesamtgewinn zusammensetzt.
7. Als Privatanleger möchte ich eine Gesamtzeile mit aggregiertem Gewinn und Gesamtsteuer sehen, damit ich die Gesamtbelastung auf einen Blick erkenne.
8. Als Privatanleger möchte ich die Kirchensteuer-Option auch für die Verkaufssimulation nutzen können, damit die Steuer realistisch berechnet wird.
9. Als Privatanleger möchte ich bei historischen Verkäufen die betroffenen FIFO-Lots sehen (Kaufdatum, Kaufkurs, Stückzahl, Gewinn je Lot), damit ich nachvollziehen kann aus welchen Chargen der Verkauf bestand.
10. Als Privatanleger möchte ich bei historischen Verkäufen den Steueranteil je Lot sehen, damit ich die Gesamtsteuerlast nachvollziehen kann.
11. Als Privatanleger möchte ich dass der Live-Kurs aus dem Kurs-Eingabefeld automatisch als Zielkurs in die Simulation übernommen wird, damit ich nicht zweimal tippen muss.
12. Als Privatanleger möchte ich die simulierten Ergebnisse mit dem Notiz-Feld speichern können, damit ich verschiedene Szenarien vergleichen kann.
13. Als Privatanleger möchte ich bei einer Teilverkauf-Simulation sehen, wie viele Stücke danach noch im Bestand verbleiben würden, damit ich den verbleibenden Bestand einschätzen kann.

## Implementation Decisions

### Datenstruktur der offenen Positionen
`PORTFOLIO_DATA.assets[name].portfolio` enthält bereits alle offenen Lots in FIFO-Reihenfolge (älteste zuerst):
```
portfolio: [
  { date: "08.03.2024", buyPrice: 24.48, shares: 30 },
  { date: "08.03.2024", buyPrice: 23.80, shares: 50 },
  { date: "08.05.2024", buyPrice: 19.95, shares: 60 },
  ...
]
```
Die FIFO-Simulation läuft vollständig clientseitig in JS — keine Python-Änderungen nötig.

### FIFO-Algorithmus (clientseitig)
Gegeben: Zielkurs, gewünschte Stückzahl → iteriere über `portfolio` (älteste zuerst), löse Lots auf bis Stückzahl erreicht:
```
für jeden Lot (ältester zuerst):
  betroffene Stücke = min(Lot.shares, verbleibende Stückzahl)
  Gewinn = (Zielkurs - Lot.buyPrice) × betroffene Stücke
  Steuer = Gewinn × Steuersatz (wenn Gewinn > 0)
  verbleibende Stückzahl -= betroffene Stücke
  wenn verbleibende Stückzahl == 0: stop
```

### Steuerberechnung
Identisch zum bestehenden Re-Entry Rechner: Abgeltung 25% + Soli 5,5% + optionale Kirchensteuer (8% oder 9%). Kirchensteuer-Dropdown wird geteilt zwischen beiden Modi.

### UI-Erweiterung: Moduswahl
Im Re-Entry Rechner oben zwei Tabs oder ein Radio-Toggle:
- **"Historischer Verkauf"** — bestehende Funktionalität (Dropdown mit vergangenen Verkäufen)
- **"Verkauf simulieren"** — neue Funktionalität (Zielkurs + Stückzahl für offene Positionen)

### Chargen-Tabelle (beide Modi)
Neue Tabelle unter dem Ergebnis-Panel mit Spalten: Kaufdatum · Kaufkurs · Stück · Gewinn · Steuer. Plus Summenzeile.

### Keine Python-Änderungen
Alle FIFO-Berechnungen laufen clientseitig in JS. Die Python-Seite (FIFO-Analyse, HTML-Generierung) bleibt unverändert.

## Testing Decisions

Gute Tests prüfen beobachtbares Verhalten über die öffentliche Schnittstelle — nicht interne Implementierung.

**Was getestet wird:**
- `analyze_portfolio_from_csv()` gibt korrekte `portfolio`-Lots zurück (bereits durch bestehende Tests abgedeckt)
- Die clientseitige FIFO-Logik ist reines JS und wird manuell im Browser verifiziert
- Kein neuer Python-Testcode nötig — bestehende 7 Tests bleiben grüner Maßstab

**Manuelle Browserprüfung:**
- Simulation "alle Stücke" ergibt gleiche Summe wie Summe aller Lots
- Teilverkauf hält FIFO-Reihenfolge korrekt ein (ältester Lot zuerst)
- Kirchensteuer-Änderung aktualisiert alle Chargenzeilen sofort

## Out of Scope

- Automatische Kursabfrage (Live-Daten via API)
- Speichern der Simulationen in einer Datenbank oder Datei
- Steueroptimierungsvorschläge (z.B. "verkaufe erst nach Jahreswechsel")
- Berücksichtigung des Sparerpauschbetrags (801 €/1.602 €)
- Verlustverrechnung mit anderen Positionen

## Further Notes

Der Sparerpauschbetrag (801 € Freistellungsauftrag) wurde bewusst ausgeklammert — er hängt von der persönlichen Steuersituation ab und ist schwer allgemeingültig zu implementieren. Ein Hinweistext im UI könnte darauf hinweisen.

Die Kirchensteuer-Einstellung sollte zwischen "historischer Verkauf" und "Simulation" geteilt werden, damit der Nutzer sie nicht zweimal setzen muss.
