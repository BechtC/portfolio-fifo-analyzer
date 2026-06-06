# PRD: Re-Entry Rechner Integration in den FIFO Portfolio-Report

## Problem Statement

Nach einem Aktienverkauf möchte ein Privatanleger wissen, ob sich der Verkauf wirklich gelohnt hat — und zu welchem Kurs er wieder einsteigen müsste, damit der Trade gegenüber dem einfachen Halten profitabel war. Diese Berechnung ist derzeit nur in einem separaten Tool (`re_entry_rechner.html`) möglich, das manuell befüllt werden muss. Die relevanten Werte — Verkaufskurs, tatsächliche Steuern, FIFO-Kaufkurse, Stückzahlen — liegen aber bereits vollständig in der FIFO-Analyse vor. Der Anleger muss dieselben Zahlen doppelt eingeben.

Zusätzlich möchte der Anleger seinen generierten Report auf GitHub zeigen können, ohne dabei seine echten Portfoliodaten (Aktiennamen, Beträge, Stückzahlen, Kaufdaten) zu veröffentlichen.

## Solution

Der generierte HTML-Report (`output/*.html`) erhält einen neuen Abschnitt "Re-Entry Analyse" direkt unterhalb der zwölf Kennzahl-Karten. Dieser Abschnitt nutzt die bereits berechneten FIFO-Daten und befüllt den Re-Entry-Rechner automatisch vor. Alle Berechnungen laufen clientseitig im Browser — kein Server, keine API, keine externen Requests.

Ein "Demo-Ansicht"-Button im Report-Header ersetzt auf Knopfdruck alle sensiblen Daten (Aktienname, Beträge, Stückzahlen, Daten) durch plausible Zufallswerte. Ein zweiter Klick stellt die echten Daten wieder her.

## User Stories

1. Als Privatanleger möchte ich nach dem Ausführen der FIFO-Analyse sofort im selben Report sehen, zu welchem Kurs ich eine verkaufte Aktie wieder kaufen müsste, damit sich der Verkauf gelohnt hat.
2. Als Privatanleger möchte ich aus einem Dropdown alle meine abgeschlossenen Verkäufe auswählen können, damit ich nicht manuell nach den richtigen Zahlen suchen muss.
3. Als Privatanleger möchte ich, dass nach Auswahl eines Verkaufs der Verkaufskurs, die tatsächlich gezahlten Steuern, die Stückzahl und die Gebühren automatisch eingetragen werden.
4. Als Privatanleger möchte ich als Referenz-Kaufkurs das älteste noch offene Kauflot (aus meinem aktuellen Portfolio) angezeigt bekommen, weil das mein realer FIFO-Einstiegspreis für einen zukünftigen Kauf wäre.
5. Als Privatanleger möchte ich den vorausgefüllten Kaufkurs manuell überschreiben können, um verschiedene Szenarien durchzuspielen.
6. Als Privatanleger möchte ich sehen: Nettokapital nach Verkauf, Gewinn vor Steuern, Break-Even Re-Entry-Kurs und den nötigen prozentualen Kursrückgang.
7. Als Privatanleger möchte ich berechnete Trades in einer persistenten Historie speichern können, damit ich verschiedene Szenarien vergleichen kann.
8. Als Privatanleger möchte ich die gespeicherte Historie als CSV exportieren können, damit ich sie in Excel weiterverarbeiten kann.
9. Als Privatanleger möchte ich die Historie auch wieder löschen können (einzelne Einträge oder komplett).
10. Als Privatanleger möchte ich im zweiten Tab meine noch offenen Kauflots sehen, damit ich beurteilen kann, ob ein hypothetischer Verkauf sinnvoll wäre.
11. Als Privatanleger möchte ich im Tab "Offene Positionen" ein bestimmtes Lot auswählen und einen hypothetischen Verkaufskurs eingeben, um den Break-Even Re-Entry-Kurs zu sehen.
12. Als Privatanleger möchte ich bei offenen Positionen die Kirchensteuer optional per Checkbox aktivieren und die Höhe (8% / 9%) wählen können.
13. Als Privatanleger möchte ich bei offenen Positionen meinen freien Sparer-Pauschbetrag eingeben können, damit die Steuerberechnung realistisch ist.
14. Als Privatanleger möchte ich, dass der aktuelle Kurs (falls beim Aufruf der Analyse angegeben) automatisch als hypothetischer Verkaufskurs vorbelegt wird.
15. Als Privatanleger möchte ich einen "Demo-Ansicht"-Button klicken können, der alle meine echten Zahlen durch anonymisierte Werte ersetzt.
16. Als Privatanleger möchte ich den Demo-Modus wieder ausschalten können, um zu meinen echten Daten zurückzukehren.
17. Als Privatanleger möchte ich sicher sein, dass meine echten Transaktions-CSVs und generierten Reports niemals versehentlich auf GitHub gepusht werden.
18. Als Privatanleger möchte ich, dass der Re-Entry-Abschnitt optisch zum bestehenden Report-Design passt, damit es sich wie ein integrierter Teil anfühlt.
19. Als Privatanleger möchte ich, dass alle berechneten Werte sofort aktualisiert werden, wenn ich eine Zahl im Rechner ändere.
20. Als Privatanleger möchte ich, dass Gebühren-Felder mit 0 € vorbelegt sind (Smartbroker hat oft keine Gebühren), aber manuell angepasst werden können.

## Implementation Decisions

- **Keine externe Abhängigkeit:** Alle FIFO-Daten werden beim Report-Generieren als JSON-Objekt in einem `<script>`-Tag in die HTML-Datei eingebettet. Das JSON enthält: Aktienname, aktueller Kurs, Liste aller SELL-Transaktionen (mit Datum, Verkaufskurs, Stückzahl, tatsächlichen Steuern, Gebühren aus CSV falls vorhanden, gewichtetem Durchschnittskaufkurs aus FIFO-Lots, Liste der Einzel-Lots), Liste der offenen Portfolio-Positionen (Datum, Kaufkurs, Stückzahl).

- **Neue Python-Methode `_build_reentry_data()`** in `PortfolioFIFOAnalyzer`: liest `self.fifo_transactions` (SELL-Einträge) und `self.portfolio` aus, gibt einen JSON-String zurück. Wird von `_create_html_template()` aufgerufen.

- **Referenz-Kaufkurs** bei abgeschlossenen Verkäufen: Das älteste noch offene Lot aus `self.portfolio` (Index 0). Falls `self.portfolio` leer ist (alles verkauft), wird der gewichtete Durchschnittskaufkurs aus den FIFO-Details des Verkaufs als Fallback genutzt.

- **Steuerberechnung:** Bei abgeschlossenen Verkäufen werden die tatsächlichen Steuern aus dem `tax`-Feld der CSV direkt verwendet — nicht neu berechnet. Bei offenen Positionen (hypothetisch) wird die deutsche KapESt-Formel verwendet: `baseRate = 0.25 / (1 + 0.25 * kirchenRate)`, dann KapESt + Soli (5,5% der KapESt) + optionale Kirchensteuer.

- **Demo-Toggle:** Rein clientseitig. Beim Aktivieren werden DOM-Texte der Kennzahl-Karten und der Header in JavaScript-Variablen gesichert. Danach werden alle Zahlenwerte mit einem Zufallsfaktor (0,5–1,3) skaliert und der Aktienname durch "Demo Corp AG" ersetzt. Beim Deaktivieren werden die gesicherten Originaldaten wiederhergestellt. Kein Reload, keine Serveranfrage.

- **Historie-Persistenz:** LocalStorage unter dem Schlüssel `reentryHistory`. JSON-Array mit Einträgen pro gespeichertem Trade. CSV-Export über Blob-Download, identisch zum bestehenden `re_entry_rechner.html`.

- **`.gitignore`:** `csvs/*.csv` und `output/*.html` werden ignoriert. `examples/`-CSVs bleiben eingecheckt.

- **Design:** Kein Tailwind, kein zusätzliches CDN. CSS passend zum bestehenden Report-Stil (Segoe UI, blaues Farbschema, `border-radius: 15px`, `box-shadow`).

## Testing Decisions

Ein guter Test prüft das beobachtbare Verhalten aus Nutzersicht — nicht interne Implementierungsdetails wie Dict-Struktur oder Variablennamen.

**Was getestet wird:**

- `_build_reentry_data()` mit der Palantir-Beispiel-CSV: JSON-String ist valides JSON, enthält mindestens einen SELL-Eintrag wenn die CSV Verkäufe hat, enthält `companyName`, `sells`, `portfolio`, `currentPrice`.
- Generierter HTML-Report: enthält das `<script>`-Tag mit `const FIFO_DATA =`, enthält den Re-Entry-Abschnitt (`reentry-section`), enthält keinen API-Key oder hardcoded Credential.
- Manuelle Browser-Prüfung (kein Test-Framework vorhanden): Dropdown zeigt Verkäufe, Felder werden befüllt, Berechnung erscheint, Demo-Toggle maskiert Daten, Historie speichert und exportiert.

**Bestehende Test-Seams:** Das Projekt hat kein automatisiertes Test-Framework. Der bestehende Ansatz ist der direkte Aufruf von `analyze_portfolio_from_csv()` und visuelle Prüfung des generierten Reports. Neue Tests folgen diesem Muster: Python-Skript das den Analyzer mit einer Beispiel-CSV aufruft und Assertions auf `_build_reentry_data()` und den HTML-String macht.

## Out of Scope

- Echtzeit-Kursdaten (kein API-Aufruf, kein automatisches Kurs-Update)
- Multi-Asset-Analyse (mehrere Aktien in einer Analyse — bestehende Limitation)
- PDF-Export des Re-Entry-Rechners
- Synchronisation der Historie zwischen verschiedenen Geräten
- Änderungen an der bestehenden CSV-Parsing-Logik
- Server-seitige Verarbeitung
- Automatisierte End-to-End-Tests im Browser

## Further Notes

Der bestehende `re_entry_rechner.html` bleibt als eigenständiges Tool erhalten — er wird nicht gelöscht oder verändert. Die Integration im Report ist eine zusätzliche Funktion, kein Ersatz.

Die `examples/`-CSVs (AMD, Palantir, Tesla) dienen als Testdaten für Entwicklung und GitHub-Demonstration. Eigene CSVs des Nutzers liegen in `csvs/` und werden durch `.gitignore` geschützt.
