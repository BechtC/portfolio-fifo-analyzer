## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/1

## What to build

Einen "Demo-Ansicht"-Button (fest positioniert oben rechts im Report) implementieren. Ein Klick ersetzt alle sensiblen Daten im Report durch anonymisierte Werte: Aktienname wird zu "Demo Corp AG", alle Geldbeträge und Stückzahlen in den Kennzahl-Karten werden durch skalierte Zufallswerte ersetzt, Datumsangaben werden generisch. Ein zweiter Klick stellt die Originaldaten exakt wieder her. Alles läuft rein clientseitig — keine Daten verlassen den Browser.

## Acceptance criteria

- [ ] Button "🎭 Demo-Ansicht" ist fest positioniert (oben rechts, über dem Seiteninhalt)
- [ ] Nach Klick: Aktienname im Header zeigt "Demo Corp AG"
- [ ] Nach Klick: Alle Zahlenwerte in den Kennzahl-Karten sind durch Zufallswerte ersetzt
- [ ] Nach Klick: Button-Text wechselt zu "✅ Demo aktiv"
- [ ] Zweiter Klick: Alle Originaldaten sind exakt wiederhergestellt
- [ ] Zweiter Klick: Button-Text wechselt zurück zu "🎭 Demo-Ansicht"
- [ ] Kein Seitenreload bei Toggle
- [ ] Kein JavaScript-Fehler in der Browser-Konsole

## Blocked by

- https://github.com/BechtC/portfolio-fifo-analyzer/issues/4 (Tab Verkäufe muss existieren)
- https://github.com/BechtC/portfolio-fifo-analyzer/issues/5 (Tab Offene Positionen muss existieren)
