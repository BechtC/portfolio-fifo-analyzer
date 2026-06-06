# PRD: Multi-Asset Portfolio FIFO Analyzer

## Problem Statement

Der Nutzer hat eine einzige CSV-Datei von Smartbroker mit **77 verschiedenen Aktien** (AMD, Palantir, Tesla, Microsoft, NVIDIA, Bitcoin Group u.v.m.) und insgesamt 239 Transaktionen. Das aktuelle Tool behandelt die gesamte CSV als eine einzige Position — alle Transaktionen werden in einen gemeinsamen FIFO-Topf geworfen. Dadurch werden Käufe und Verkäufe verschiedener Aktien falsch miteinander verrechnet, und der Report zeigt nur "Advanced Micro Devices" als Unternehmensname, obwohl 76 weitere Aktien in der Datei sind.

Der Nutzer möchte sein gesamtes Portfolio auf einen Blick sehen — jede Aktie separat mit korrekter FIFO-Berechnung, und die Möglichkeit, in eine einzelne Aktie hineinzuklicken für die Detailansicht.

## Solution

Das Tool wird so erweitert, dass es beim Einlesen einer CSV automatisch alle enthaltenen Aktien erkennt (gruppiert nach `holdingname`) und für **jede Aktie separat** eine vollständige FIFO-Analyse durchführt. Der generierte HTML-Report zeigt zunächst eine **Portfolio-Übersicht** mit allen Aktien als Karten-Grid, und beim Klick auf eine Aktie öffnet sich eine **Detailansicht** mit der vollständigen Einzel-Analyse (Hero-Metriken, Chart, Transaktions-Tabelle, Re-Entry-Rechner) — alles in einer einzigen HTML-Datei, clientseitig per JS navigierbar.

## User Stories

1. Als Privatanleger möchte ich eine einzige CSV mit allen meinen Trades einlesen können, damit ich nicht für jede Aktie eine separate Datei pflegen muss.
2. Als Privatanleger möchte ich auf der Startseite des Reports alle meine Aktien als Karten sehen, damit ich einen schnellen Überblick über mein gesamtes Portfolio habe.
3. Als Privatanleger möchte ich auf jeder Aktien-Karte die wichtigsten Kennzahlen sehen (Investiert, Entnommen, Realisiert, Unrealisiert, Rendite %), damit ich sofort erkenne welche Positionen gut und welche schlecht laufen.
4. Als Privatanleger möchte ich Aktien mit Gewinn grün und Aktien mit Verlust rot hervorgehoben sehen, damit ich Verlierer sofort erkenne.
5. Als Privatanleger möchte ich auf eine Aktien-Karte klicken können, um die vollständige FIFO-Detailansicht zu öffnen.
6. Als Privatanleger möchte ich in der Detailansicht alle bisherigen Features sehen: Hero-Metriken, Chart, Transaktions-Tabelle, Re-Entry-Rechner.
7. Als Privatanleger möchte ich in der Detailansicht einen "Zurück zur Übersicht"-Button haben.
8. Als Privatanleger möchte ich dass die FIFO-Berechnung pro Aktie separat und korrekt durchgeführt wird — Käufe von AMD dürfen nicht mit Käufen von Palantir verrechnet werden.
9. Als Privatanleger möchte ich in der Portfolio-Übersicht die Gesamtsummen über alle Aktien sehen (Gesamt investiert, Gesamt realisiert, Gesamt unrealisiert).
10. Als Privatanleger möchte ich die Aktien-Karten nach Rendite, Name oder Betrag sortieren können.
11. Als Privatanleger möchte ich Aktien nach "nur offene Positionen", "nur geschlossene Positionen" oder "alle" filtern können.
12. Als Privatanleger möchte ich dass der Report als eine einzige HTML-Datei funktioniert (kein Server, kein Backend).
13. Als Privatanleger möchte ich dass `python portfolio_analyzer.py` weiterhin ohne Fehler durchläuft.
14. Als Privatanleger möchte ich dass der Demo-Toggle auf der Übersichtsseite alle Aktiennamen und Beträge maskiert.
15. Als Privatanleger möchte ich dass der Dark/Light-Mode-Toggle auch auf der Portfolio-Übersicht funktioniert.
16. Als Privatanleger möchte ich dass Aktien ohne Käufe (nur Verkäufe vorhanden, z.B. Uber Technologies) trotzdem korrekt angezeigt werden.
17. Als Privatanleger möchte ich dass Aktien mit sehr wenigen Transaktionen (1 Kauf, 0 Verkäufe) ebenfalls korrekt dargestellt werden.

## Implementation Decisions

### Kern-Architektur: Multi-Asset in einer Klasse

Die bestehende Klasse `PortfolioFIFOAnalyzer` wird auf **Single-Asset** belassen (verarbeitet eine gefilterte Teilliste von Transaktionen). Eine neue Koordinator-Funktion `analyze_portfolio_from_csv()` wird erweitert:

1. CSV einlesen und nach `holdingname` gruppieren
2. Für jede Aktie eine eigene `PortfolioFIFOAnalyzer`-Instanz erstellen
3. Alle Instanzen in einem Dict sammeln: `{ holdingname: analyzer }`
4. Einen einzigen Multi-Asset HTML-Report generieren

### Report-Struktur (eine HTML-Datei, zwei "Views")

**View 1: Portfolio-Übersicht** (`id="portfolio-view"`)
- Header mit Gesamt-Portfolio-Kennzahlen
- Karten-Grid: eine Karte pro Aktie
- Jede Karte: Name, Anzahl Käufe/Verkäufe, Investiert, Realisiert, Unrealisiert, Rendite %
- Farb-Kodierung: grüner Border bei positiver Rendite, roter bei negativer
- Klick auf Karte: `showDetail('AMD')` → blendet Übersicht aus, zeigt Detailansicht

**View 2: Aktien-Detailansicht** (`id="detail-view"`)
- Identisch mit dem bisherigen Single-Asset-Report
- "← Zurück zur Übersicht"-Button oben
- Alle Daten für alle Aktien sind im `PORTFOLIO_DATA` JSON eingebettet
- JS lädt die Daten der gewählten Aktie und rendert die Abschnitte

### Datenstruktur im HTML

```javascript
const PORTFOLIO_DATA = {
  summary: {
    total_invested: 123456.78,
    total_withdrawn: 98765.43,
    total_realized_gains: 12345.67,
    total_unrealized_gains: 234567.89
  },
  assets: {
    "Advanced Micro Devices": {
      company_name: "Advanced Micro Devices",
      analysis_results: { ... },  // alle Keys aus analysis_results
      sells: [ ... ],             // aus _build_reentry_data()
      portfolio: [ ... ]          // offene Positionen
    },
    "Palantir Technologies": { ... },
    ...
  }
};
```

### Python-seitige Änderungen

- `analyze_portfolio_from_csv()` gruppiert Transaktionen nach `holdingname` und erzeugt eine `PortfolioFIFOAnalyzer`-Instanz pro Aktie
- Neue Methode `generate_multi_asset_report(analyzers_dict)` generiert den kombinierten HTML-Report
- `__main__`-Block bleibt: lädt `csvs/Chris-20260606-153648.csv`, ruft `analyze_portfolio_from_csv()` auf, öffnet Report im Browser
- Das bestehende `_create_html_template()` bleibt als Basis — wird für die Detailansicht wiederverwendet

### Navigation (rein clientseitig)

```javascript
function showDetail(assetName) {
  document.getElementById('portfolio-view').style.display = 'none';
  document.getElementById('detail-view').style.display = 'block';
  renderDetail(PORTFOLIO_DATA.assets[assetName]);
}

function showOverview() {
  document.getElementById('detail-view').style.display = 'none';
  document.getElementById('portfolio-view').style.display = 'block';
}
```

### Sortierung & Filter der Übersicht

Clientseitig per JS — keine Server-Abhängigkeit:
- Sortierung: nach `total_return_pct`, `company_name`, `total_invested`
- Filter: "Alle", "Offen" (portfolio.length > 0), "Geschlossen" (portfolio.length === 0)

## Testing Decisions

Ein guter Test prüft beobachtbares Verhalten, nicht interne Implementierung.

**Was getestet wird:**
- `python portfolio_analyzer.py` läuft fehlerfrei mit `csvs/Chris-20260606-153648.csv` (239 Transaktionen, 77 Aktien)
- Generiertes HTML enthält `const PORTFOLIO_DATA =` mit allen 77 Aktien
- Jede Aktie hat separate FIFO-Ergebnisse (AMD-Käufe nicht mit Palantir-Käufen verrechnet)
- Manuelle Browser-Prüfung: Portfolio-Übersicht zeigt 77 Karten, Klick auf AMD öffnet Detailansicht, "Zurück"-Button funktioniert
- Aktien mit 0 Käufen (Uber) werden ohne Crash angezeigt

**Testseams:**
- `analyze_portfolio_from_csv()` gibt Dict mit korrekter Anzahl Analyzer-Instanzen zurück
- `PortfolioFIFOAnalyzer` mit gefilterter Transaktionstabelle (nur eine Aktie) liefert korrekte FIFO-Ergebnisse

## Out of Scope

- Echtzeit-Kursdaten oder automatische Kursabfrage
- Persistente Datenbank
- Benutzeranmeldung oder Multi-User-Support
- PDF-Export
- Benchmark-Vergleich (z.B. gegen DAX oder S&P 500)
- Dividenden-Tracking
- Währungsumrechnung (alle Werte bleiben in der CSV-Währung)
- Steueroptimierungsvorschläge

## Further Notes

Die CSV enthält Aktien mit 0 Käufen (z.B. "Uber Technologies", "Kyndryl Holdings") — das passiert wenn Käufe aus einem anderen Zeitraum stammen der nicht exportiert wurde. Diese Aktien sollen trotzdem angezeigt werden, aber mit Hinweis "Keine Kaufdaten vorhanden — FIFO unvollständig".

Aktien wie "Electricite de France (E.D.F.)Anrechte Aktie" haben sehr lange Namen — die Darstellung in Karten muss truncaten (`truncate` Tailwind-Klasse).
