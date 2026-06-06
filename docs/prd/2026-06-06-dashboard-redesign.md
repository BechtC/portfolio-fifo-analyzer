# PRD: Komplettes Dashboard-Redesign des FIFO Portfolio-Reports

## Problem Statement

Der generierte HTML-Report sieht veraltet aus: statisches Layout, kein modernes Design, keine Interaktivität jenseits des Re-Entry-Rechners. Ein Privatanleger der seinen Report auf GitHub zeigt oder täglich nutzt, möchte ein professionelles Dashboard das wie eine moderne Finance-App aussieht — nicht wie eine generierte HTML-Seite aus 2015. Außerdem sind die 12 Kennzahl-Karten alle gleichwertig dargestellt, obwohl einige Metriken (Investiert, Entnommen, Realisiert, Unrealisiert) viel wichtiger sind als andere.

## Solution

`_create_html_template()` in `portfolio_analyzer.py` wird komplett neu geschrieben. Das neue Template nutzt Tailwind CSS via CDN, hat ein Dark-Mode-Dashboard-Layout (Vercel/Linear-Stil) mit Indigo/Violet als Akzentfarbe, und organisiert die Inhalte in fünf klaren Abschnitten: Header, Hero-Metriken, Re-Entry Rechner, Chart und Transaktions-Tabelle. Alle bestehenden Funktionen (Re-Entry-Rechner mit zwei Tabs, Demo-Toggle, LocalStorage-Historie, CSV-Export) bleiben erhalten.

## User Stories

1. Als Privatanleger möchte ich einen Report im Dark-Mode-Dashboard-Stil sehen, damit er professionell aussieht und ich ihn gerne zeige.
2. Als Privatanleger möchte ich die vier wichtigsten Metriken (Investiert, Entnommen, Realisiert, Unrealisiert) groß und prominent oben sehen.
3. Als Privatanleger möchte ich die Gesamtperformance in Prozent als fünfte Hero-Metrik sehen.
4. Als Privatanleger möchte ich zwischen Dark Mode und Light Mode wechseln können.
5. Als Privatanleger möchte ich eine Kauf/Verkauf-Timeline als Chart sehen, damit ich meine Trade-Geschichte visualisiert bekomme.
6. Als Privatanleger möchte ich auf dem Chart Kauf-Marker (grün) und Verkauf-Marker (rot) sehen.
7. Als Privatanleger möchte ich alle meine Transaktionen in einer Tabelle sehen.
8. Als Privatanleger möchte ich die Transaktions-Tabelle nach Alle/Käufe/Verkäufe filtern können.
9. Als Privatanleger möchte ich den Re-Entry-Rechner direkt nach den Hero-Metriken integriert sehen — nicht erst am Ende der Seite.
10. Als Privatanleger möchte ich im Re-Entry-Rechner per Dropdown einen abgeschlossenen Verkauf wählen und sofort den Break-Even Re-Entry-Kurs sehen.
11. Als Privatanleger möchte ich im Re-Entry-Rechner meine offenen Kauflots einzeln analysieren können.
12. Als Privatanleger möchte ich bei offenen Positionen die Kirchensteuer optional aktivieren können.
13. Als Privatanleger möchte ich berechnete Szenarien in einer Historie speichern können.
14. Als Privatanleger möchte ich die Historie als CSV exportieren können.
15. Als Privatanleger möchte ich per Demo-Toggle alle sensiblen Daten (Name, Beträge, Stückzahlen) auf einen Klick maskieren können.
16. Als Privatanleger möchte ich per zweitem Klick die Originaldaten wiederherstellen können.
17. Als Privatanleger möchte ich dass der Report auf Mobilgeräten (< 768px) lesbar ist.
18. Als Privatanleger möchte ich dass kein externes CDN außer Tailwind und Chart.js geladen wird.
19. Als Privatanleger möchte ich dass `python portfolio_analyzer.py` ohne Fehler und Warnings durchläuft.
20. Als Privatanleger möchte ich dass der Report automatisch im Browser geöffnet wird — wie bisher.

## Implementation Decisions

- **Einzige geänderte Methode:** `_create_html_template()` in `PortfolioFIFOAnalyzer` wird komplett neu geschrieben. Alle anderen Methoden (FIFO-Logik, CSV-Parsing, `_build_reentry_data()`) bleiben unverändert.

- **Tailwind CSS:** via CDN `https://cdn.tailwindcss.com` — kein Build-Step, keine neuen Dependencies.

- **Chart.js:** via CDN `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js` — Scatter-Chart mit Buy/Sell-Markern. X-Achse: Datum als String, Y-Achse: Transaktionsbetrag in EUR.

- **Dark Mode:** Tailwind `dark:`-Klassen + `class="dark"` auf `<html>`. Toggle-Button setzt/entfernt `dark`-Klasse und speichert Präferenz in LocalStorage.

- **Layout-Struktur:**
  ```
  <html class="dark">
    <body class="bg-gray-950 text-gray-100">
      <header>  ← Aktienname, Datum, Dark-Mode-Toggle, Demo-Toggle
      <section> ← 5 Hero-Karten (grid-cols-5)
      <section> ← Re-Entry Rechner (2 Tabs)
      <section> ← Chart (Kauf/Verkauf Timeline)
      <section> ← Transaktions-Tabelle (Filter-Tabs)
    </body>
  </html>
  ```

- **Akzentfarbe:** Tailwind `indigo-500` / `violet-500` für aktive Elemente, Buttons, Borders. Gewinne: `emerald-400`, Verluste: `red-400`, neutrale Zahlen: `gray-100`.

- **FIFO_DATA JSON:** bleibt exakt wie bisher (aus `_build_reentry_data()`) — das JS liest dieselbe Datenstruktur.

- **Re-Entry JS-Logik:** wird 1:1 aus dem bestehenden Template übernommen — nur das HTML-Gerüst und CSS-Klassen wechseln auf Tailwind.

- **Demo-Toggle:** maskiert Aktienname, alle Zahlenwerte in Hero-Karten und Tabelle, Datumsangaben — identische Logik wie bisher, angepasst an neue DOM-Selektoren.

- **SyntaxWarning `\d` Fix:** alle Regex-Literale im f-string als `[^\\d]` escapen oder in separate JS-Variablen auslagern.

- **`__main__`-Block:** bleibt unverändert — lädt `csvs/Chris-20260606-153648.csv`.

## Testing Decisions

Ein guter Test prüft beobachtbares Verhalten, nicht Template-Interna.

**Getestet wird:**
- Generierter HTML-String enthält: `cdn.tailwindcss.com`, `Chart.js`, `const FIFO_DATA =`, `id="reentry-section"`, `id="chart-section"`, `id="transactions-section"`
- `python portfolio_analyzer.py` läuft ohne SyntaxWarning und ohne UnicodeEncodeError durch
- Manuelle Browser-Prüfung: Dark Mode aktiv beim Öffnen, alle 5 Hero-Karten sichtbar, Chart rendert, Transaktions-Tabs filtern korrekt, Re-Entry-Dropdown funktioniert, Demo-Toggle maskiert und stellt wieder her

**Bestehender Test-Ansatz:** direkter Aufruf von `analyze_portfolio_from_csv()` mit Beispiel-CSV, visuelle Report-Prüfung im Browser.

## Out of Scope

- Multi-Asset-Analyse (mehrere Aktien in einem Report)
- Server-seitiges Rendering
- Echtzeit-Kursdaten
- PDF-Export
- Responsive Tabellen mit Scroll-Pagination
- Änderungen an CSV-Parsing oder FIFO-Logik
- Änderungen an `_build_reentry_data()`

## Further Notes

Der `re_entry_rechner.html` (eigenständiges Tool) bleibt unverändert. Nur der generierte Report in `output/` wird neu gestaltet.

Das neue Template ist ein Python f-string — alle `{` und `}` im HTML/CSS/JS müssen als `{{` / `}}` escaped werden, außer `{reentry_json}` und anderen echten Python-Variablen.
