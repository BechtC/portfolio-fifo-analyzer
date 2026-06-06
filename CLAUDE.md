# Portfolio FIFO Analyzer - Projektkontext für Claude

## Was ist dieses Projekt?
Python-Tool zur steuerrechtlich korrekten **FIFO-Analyse** (First-In-First-Out) von Aktien-Portfolios.
Liest Broker-CSVs ein → berechnet Gewinne/Verluste → generiert HTML-Report.

## Projektstruktur
```
FIFO/
├── portfolio_analyzer.py   # Einzige Hauptdatei (24 KB) - die gesamte Logik
├── requirements.txt        # pandas, numpy, matplotlib, seaborn, plotly
├── csvs/                   # Eigene Transaktions-CSVs hier rein (nur README drin)
├── examples/               # Beispiel-CSVs: amd, palantir, tesla
├── output/                 # Generierte HTML-Reports landen hier
├── docs/                   # DOCKER_TUTORIAL.md
├── Dockerfile + docker-compose.yml
└── CLAUDE.md               # Diese Datei
```

## Kern-Architektur

### Klasse: `PortfolioFIFOAnalyzer` (`portfolio_analyzer.py:33`)
Wird bei Instanziierung automatisch vollständig ausgeführt:
1. `__init__` → ruft `_load_and_clean_data()`, `_perform_fifo_analysis()`, `_calculate_summary_stats()`
2. `generate_complete_report()` → Konsole + HTML

**Wichtige Methoden:**
| Methode | Zeile | Zweck |
|---|---|---|
| `_detect_delimiter()` | :61 | Auto-Erkennung von `;`, `,`, Tab, `\|` |
| `_load_and_clean_data()` | :85 | CSV laden, Spalten normalisieren, Daten bereinigen |
| `_convert_data_types()` | :160 | Deutsche Zahlenformate (Komma→Punkt) |
| `_perform_fifo_analysis()` | :174 | Kern-FIFO-Logik |
| `_calculate_summary_stats()` | :281 | Rendite-Kennzahlen berechnen |
| `print_summary_report()` | :313 | Konsolen-Output |
| `generate_html_report()` | :347 | HTML-Report in `/output/` |

**Öffentliche Convenience-Funktion:** `analyze_portfolio_from_csv(csv_file, price, currency)` (:582)

### FIFO-Logik (`_perform_fifo_analysis()`)
- `self.portfolio` = Liste von Kauf-Positionen (älteste zuerst, FIFO-Queue)
- Bei Verkauf: älteste Position wird zuerst abgebaut (`portfolio.pop(0)`)
- Partial-Sells werden korrekt behandelt (Teilposition wird reduziert)
- Ergebnisse in `self.analysis_results` dict

### Spaltenmapping (DE → EN intern)
```python
datum→date, preis→price, anzahl→shares, betrag→amount,
steuer→tax, gewinn→realized_gains, holdingname→company_name
```

## Unterstützte CSV-Formate

### Smartbroker/Trade Republic:
```csv
datetime;date;time;price;shares;amount;tax;fee;realizedgains;type;holdingname
2025-07-31T14:04:05.000Z;31.07.2025;16:04:00;141;35;4935;1232,26;0;4673,58;Sell;Palantir Technologies
```

### Comdirect/ING:
```csv
Datum,Typ,Aktien,Preis,Summe,Steuer,Unternehmen
31.07.2025,Verkauf,35,141.00,4935.00,1232.26,Palantir Technologies
```

### Typ-Werte: `buy`/`kauf` oder `sell`/`verkauf` (case-insensitive)

## Verwendung
```python
# Minimal
analyzer = analyze_portfolio_from_csv("csvs/aktie.csv")

# Mit aktuellem Kurs
analyzer = analyze_portfolio_from_csv("csvs/aktie.csv", current_price=157.0, currency="EUR")

# Ergebnis-Zugriff
analyzer.analysis_results  # dict mit allen Kennzahlen
analyzer.fifo_transactions  # Liste aller FIFO-zugeordneten Trades
analyzer.portfolio          # Aktueller Bestand (restliche Kaufpositionen)
```

## `analysis_results` Keys
```
total_invested, total_withdrawn, total_realized_gains, total_taxes,
current_portfolio, current_shares, current_cost_basis, current_value,
unrealized_gains, total_gains, net_realized_gains, net_cashflow, total_return_pct
```

## Dependencies (Python 3.7+)
`pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `kaleido`, `python-dateutil`

## Bekannte TODO-Liste (aus README)
- [ ] Multi-Asset Support (mehrere Aktien in einer Analyse)
- [ ] PDF-Export
- [ ] Excel-Export (.xlsx)
- [ ] Dividenden-Tracking
- [ ] Benchmark-Vergleich
- [ ] Steuer-Optimierungsvorschläge

## HTML-Report
- Liegt nach Generierung in `output/<Company_Name>_portfolio_analysis.html`
- 12 Kennzahl-Karten (responsive Grid)
- Chart.js über CDN eingebunden
- Wird automatisch im Browser geöffnet (webbrowser-Modul)
- Aktuell: Kein interaktiver Chart im Template (nur Karten)

# context-mode — MANDATORY routing rules

You have context-mode MCP tools available. These rules are NOT optional — they protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## BLOCKED commands — do NOT attempt these

### curl / wget — BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error message. Do NOT retry.
Instead use:
- `ctx_fetch_and_index(url, source)` to fetch and index web pages
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` to run HTTP calls in sandbox

### Inline HTTP — BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, or `http.request(` is intercepted and replaced with an error message. Do NOT retry with Bash.
Instead use:
- `ctx_execute(language, code)` to run HTTP calls in sandbox — only stdout enters context

### WebFetch — BLOCKED
WebFetch calls are denied entirely. The URL is extracted and you are told to use `ctx_fetch_and_index` instead.
Instead use:
- `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` to query the indexed content

## REDIRECTED tools — use sandbox equivalents

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` — run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` — run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct (Edit needs content in context).
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead. Only your printed summary enters context. The raw file content stays in the sandbox.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox. Only your printed summary enters context.

## Tool selection hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` — Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` — Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` — Sandbox execution. Only stdout enters context.
4. **WEB**: `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` — Fetch, chunk, index, query. Raw HTML never enters context.
5. **INDEX**: `ctx_index(content, source)` — Store content in FTS5 knowledge base for later search.

## Subagent routing

When spawning subagents (Agent/Task tool), the routing block is automatically injected into their prompt. Bash-type subagents are upgraded to general-purpose so they have access to MCP tools. You do NOT need to manually instruct subagents about context-mode.

## Output constraints

- Keep responses under 500 words.
- Write artifacts (code, configs, PRDs) to FILES — never return them as inline text. Return only: file path + 1-line description.
- When indexing content, use descriptive source labels so others can `ctx_search(source: "label")` later.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call the `ctx_stats` MCP tool and display the full output verbatim |
| `ctx doctor` | Call the `ctx_doctor` MCP tool, run the returned shell command, display as checklist |
| `ctx upgrade` | Call the `ctx_upgrade` MCP tool, run the returned shell command, display as checklist |

## Agent skills

### Issue tracker

Issues leben auf GitHub (Voraussetzung: `git init` + GitHub Remote einrichten). Siehe `docs/agents/issue-tracker.md`.

### Triage labels

Standard-Labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. Siehe `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` am Projektroot. Siehe `docs/agents/domain.md`.
