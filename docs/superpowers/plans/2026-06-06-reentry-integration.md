# Re-Entry Rechner Integration — Implementierungsplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Den generierten HTML-Report um einen eingebetteten Re-Entry-Rechner mit zwei Tabs (Verkäufe / offene Positionen) und einem Demo-Toggle erweitern.

**Architecture:** Alle FIFO-Daten werden als JSON-Objekt in einem `<script>`-Tag in den Report eingebettet. Die gesamte Re-Entry-Logik läuft clientseitig in JavaScript. `portfolio_analyzer.py` bekommt eine neue Hilfsmethode `_build_reentry_data()` die das JSON-Objekt aufbaut, sowie CSS- und JS-Blöcke die in `_create_html_template()` eingefügt werden.

**Tech Stack:** Python 3.7+, Vanilla JavaScript (ES6), CSS (passend zum bestehenden Report-Stil), kein Tailwind, kein CDN für Re-Entry-Logik.

---

## Dateien

- **Modify:** `portfolio_analyzer.py`
  - Neue Methode `_build_reentry_data()` → gibt dict mit `sells`, `portfolio`, `currentPrice`, `companyName` zurück
  - `_create_html_template()` → eingebettetes JSON + Re-Entry CSS + Re-Entry JS + HTML-Abschnitt
  - `.gitignore` wird in Task 1 angelegt

---

## Task 1: .gitignore anlegen und Security-Basis sichern

**Files:**
- Create: `.gitignore`

- [ ] **Schritt 1: .gitignore erstellen**

Datei `C:\Users\Becht\Python-Projecte\FIFO\.gitignore` anlegen mit folgendem Inhalt:

```
# Eigene Transaktions-CSVs — nie committen
csvs/*.csv

# Generierte Reports mit echten Portfoliodaten — nie committen
output/*.html
output/*.pdf

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/
.venv/
venv/
env/

# Jupyter
.ipynb_checkpoints/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

- [ ] **Schritt 2: Verifizieren dass examples/-CSVs NICHT ignoriert werden**

`examples/` ist nicht in `.gitignore` — die Beispiel-CSVs (amd, palantir, tesla) bleiben committet. Prüfe: `csvs/*.csv` ignoriert nur den `csvs/`-Ordner, nicht `examples/`.

---

## Task 2: `_build_reentry_data()` Methode implementieren

**Files:**
- Modify: `portfolio_analyzer.py` — neue Methode in Klasse `PortfolioFIFOAnalyzer`, nach `_calculate_summary_stats()` (nach Zeile ~310)

- [ ] **Schritt 1: Methode `_build_reentry_data()` einfügen**

Füge folgende Methode in die Klasse `PortfolioFIFOAnalyzer` ein (nach `_calculate_summary_stats`, vor `print_summary_report`):

```python
def _build_reentry_data(self):
    """JSON-Daten für eingebetteten Re-Entry-Rechner aufbauen."""
    import json

    # Alle SELL-Transaktionen aufbereiten
    sells = []
    for tx in self.fifo_transactions:
        if tx['type'] != 'SELL':
            continue
        # Gewichteter Durchschnitt Kaufkurs aus FIFO-Details
        fifo_details = tx.get('fifo_details', [])
        avg_buy_price = 0.0
        if fifo_details:
            total_shares = sum(d['shares'] for d in fifo_details)
            avg_buy_price = (
                sum(d['buy_price'] * d['shares'] for d in fifo_details) / total_shares
                if total_shares > 0 else 0.0
            )
        sells.append({
            'date': str(tx.get('date', '')),
            'sellPrice': float(tx.get('price', 0)),
            'shares': float(tx.get('shares', 0)),
            'taxes': float(tx.get('taxes', 0)),
            'fee': float(tx.get('fee', 0) if tx.get('fee') else 0),
            'avgBuyPrice': round(avg_buy_price, 4),
            'fifoDetails': [
                {
                    'buyDate': str(d.get('buy_date', '')),
                    'buyPrice': float(d.get('buy_price', 0)),
                    'shares': float(d.get('shares', 0)),
                }
                for d in fifo_details
            ],
        })

    # Offene Positionen aufbereiten
    portfolio = []
    for pos in self.portfolio:
        portfolio.append({
            'date': str(pos.get('date', '')),
            'buyPrice': float(pos.get('price', 0)),
            'shares': float(pos.get('shares', 0)),
        })

    data = {
        'companyName': self.company_name,
        'currentPrice': float(self.current_price) if self.current_price else None,
        'currency': self.currency,
        'sells': sells,
        'portfolio': portfolio,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)
```

- [ ] **Schritt 2: Manuelle Prüfung**

Füge temporär am Ende von `portfolio_analyzer.py` folgenden Test-Aufruf ein (nach dem `if __name__ == '__main__':`-Block falls vorhanden, sonst unten im Skript):

```python
# Temporärer Test — danach wieder entfernen
if __name__ == '__main__':
    import json
    a = analyze_portfolio_from_csv('examples/palantir.csv')
    data = a._build_reentry_data()
    parsed = json.loads(data)
    print("Sells:", len(parsed['sells']))
    print("Portfolio:", len(parsed['portfolio']))
    print("Erster Sell:", parsed['sells'][0] if parsed['sells'] else "keine")
```

Führe aus (im FIFO-Ordner, mit aktivierter Python-Umgebung):
```
python portfolio_analyzer.py
```

Erwartetes Ergebnis: Kein Fehler, `Sells:` zeigt Anzahl > 0 wenn die CSV Verkäufe enthält.

- [ ] **Schritt 3: Temporären Test-Code wieder entfernen**

Den `if __name__ == '__main__':` Testblock wieder entfernen bzw. auf den ursprünglichen Stand zurücksetzen.

---

## Task 3: Re-Entry CSS zum Report hinzufügen

**Files:**
- Modify: `portfolio_analyzer.py` — in `_create_html_template()`, im `<style>`-Block nach dem letzten `@media`-Query (nach Zeile ~481)

- [ ] **Schritt 1: CSS-Block für Re-Entry-Abschnitt einfügen**

Im `<style>`-Block von `_create_html_template()` nach dem `@media (max-width: 768px)` Block folgendes CSS anfügen (vor dem schließenden `</style>`):

```css
        /* Re-Entry Rechner */
        .reentry-section {{
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            margin-top: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}

        .reentry-section h2 {{
            color: #2d3748;
            font-size: 1.6em;
            font-weight: 700;
            margin-bottom: 20px;
            text-align: center;
        }}

        .reentry-tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0;
        }}

        .reentry-tab {{
            padding: 10px 24px;
            border: none;
            background: none;
            color: #718096;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
            transition: all 0.2s;
        }}

        .reentry-tab.active {{
            color: #2a5298;
            border-bottom-color: #2a5298;
        }}

        .reentry-panel {{ display: none; }}
        .reentry-panel.active {{ display: block; }}

        .reentry-form-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }}

        .reentry-field label {{
            display: block;
            font-size: 0.85em;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 4px;
        }}

        .reentry-field input,
        .reentry-field select {{
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #cbd5e0;
            border-radius: 8px;
            font-size: 1em;
            color: #2d3748;
            background: #f7fafc;
            outline: none;
            transition: border-color 0.2s;
        }}

        .reentry-field input:focus,
        .reentry-field select:focus {{
            border-color: #2a5298;
            background: #fff;
        }}

        .reentry-results {{
            background: #2a5298;
            border-radius: 12px;
            padding: 20px 24px;
            color: #fff;
            margin-top: 8px;
        }}

        .reentry-result-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.15);
        }}

        .reentry-result-row:last-child {{ border-bottom: none; }}

        .reentry-result-label {{ color: rgba(255,255,255,0.75); font-size: 0.9em; }}
        .reentry-result-value {{ font-weight: 700; font-size: 1.05em; }}

        .reentry-breakeven {{
            text-align: center;
            margin-top: 16px;
            padding: 16px;
            background: #1e3c72;
            border-radius: 10px;
        }}

        .reentry-breakeven .be-label {{ color: rgba(255,255,255,0.75); font-size: 0.85em; margin-bottom: 4px; }}
        .reentry-breakeven .be-price {{ font-size: 2.2em; font-weight: 800; color: #fff; }}
        .reentry-breakeven .be-drop {{ margin-top: 6px; font-size: 0.9em; color: rgba(255,255,255,0.8); }}

        .reentry-save-btn {{
            margin-top: 16px;
            width: 100%;
            padding: 12px;
            background: #fff;
            color: #2a5298;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.2s;
        }}

        .reentry-save-btn:hover {{ background: #ebf4ff; }}

        .reentry-history-section {{
            margin-top: 24px;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
        }}

        .reentry-history-section h3 {{
            font-size: 1.1em;
            color: #2d3748;
            font-weight: 600;
            margin-bottom: 12px;
        }}

        .reentry-history-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88em;
        }}

        .reentry-history-table th {{
            background: #f7fafc;
            color: #718096;
            font-weight: 600;
            padding: 8px 12px;
            text-align: left;
            border-bottom: 2px solid #e2e8f0;
        }}

        .reentry-history-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #f0f0f0;
            color: #2d3748;
        }}

        .reentry-history-btns {{
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }}

        .reentry-history-btn {{
            padding: 7px 16px;
            border-radius: 8px;
            border: none;
            font-size: 0.85em;
            font-weight: 600;
            cursor: pointer;
        }}

        .btn-export {{ background: #ebf4ff; color: #2a5298; }}
        .btn-clear  {{ background: #fff5f5; color: #c53030; }}

        /* Demo Toggle */
        .demo-toggle-btn {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            padding: 10px 18px;
            background: rgba(255,255,255,0.9);
            color: #2a5298;
            border: 2px solid #2a5298;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.85em;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: all 0.2s;
        }}

        .demo-toggle-btn.active {{
            background: #2a5298;
            color: #fff;
        }}

        .reentry-checkbox-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }}

        .reentry-checkbox-row label {{
            font-size: 0.85em;
            color: #4a5568;
            font-weight: 600;
            cursor: pointer;
        }}

        @media (max-width: 600px) {{
            .reentry-form-grid {{ grid-template-columns: 1fr; }}
        }}
```

- [ ] **Schritt 2: Report generieren und visuell prüfen**

Führe aus:
```
python portfolio_analyzer.py
```
Öffne den generierten Report. Die Seite soll aussehen wie vorher (CSS-Änderungen sind noch nicht sichtbar, weil der HTML-Abschnitt noch fehlt). Kein JS-Fehler in der Konsole.

---

## Task 4: Re-Entry HTML-Abschnitt in Template einfügen

**Files:**
- Modify: `portfolio_analyzer.py` — in `_create_html_template()`, nach dem schließenden `</div>` der `summary-grid` (nach `</div>` der letzten `.summary-card`, vor `</div>` von `.container`)

- [ ] **Schritt 1: JSON-Einbettung und HTML-Abschnitt einfügen**

In `_create_html_template()` direkt nach dem `summary-grid`-Div (nach Zeile ~552, vor `</div>` des `.container`) folgendes einfügen:

```python
        # Re-Entry Daten als JSON einbetten
        reentry_json = self._build_reentry_data()
```

Dann im f-string des HTML-Templates, nach dem schließenden `</div>` der `summary-grid` und vor `</div>` des `.container`:

```html
        <script>
        const FIFO_DATA = {reentry_json};
        </script>

        <button class="demo-toggle-btn" id="demoToggleBtn" onclick="toggleDemo()">🎭 Demo-Ansicht</button>

        <div class="reentry-section">
            <h2>🔄 Re-Entry Analyse</h2>

            <div class="reentry-tabs">
                <button class="reentry-tab active" onclick="switchTab('sells')">📉 Abgeschlossene Verkäufe</button>
                <button class="reentry-tab" onclick="switchTab('portfolio')">📂 Offene Positionen</button>
            </div>

            <!-- Tab 1: Verkäufe -->
            <div class="reentry-panel active" id="panel-sells">
                <div class="reentry-field" style="margin-bottom:16px;">
                    <label>Verkauf auswählen</label>
                    <select id="sellSelect" onchange="loadSell()">
                        <option value="">— Verkauf wählen —</option>
                    </select>
                </div>
                <div class="reentry-form-grid">
                    <div class="reentry-field">
                        <label>Kaufkurs (ältestes offenes Lot) (€)</label>
                        <input type="number" id="s_buyPrice" step="0.01" oninput="calcSell()">
                    </div>
                    <div class="reentry-field">
                        <label>Verkaufskurs (€)</label>
                        <input type="number" id="s_sellPrice" step="0.01" oninput="calcSell()">
                    </div>
                    <div class="reentry-field">
                        <label>Stückzahl</label>
                        <input type="number" id="s_shares" step="0.0001" oninput="calcSell()">
                    </div>
                    <div class="reentry-field">
                        <label>Tatsächliche Steuern (€)</label>
                        <input type="number" id="s_taxes" step="0.01" oninput="calcSell()">
                    </div>
                    <div class="reentry-field">
                        <label>Gebühren Kauf (€)</label>
                        <input type="number" id="s_feeBuy" value="0" step="0.01" oninput="calcSell()">
                    </div>
                    <div class="reentry-field">
                        <label>Gebühren Verkauf (€)</label>
                        <input type="number" id="s_feeSell" value="0" step="0.01" oninput="calcSell()">
                    </div>
                </div>
                <div class="reentry-results">
                    <div class="reentry-result-row">
                        <span class="reentry-result-label">Verkaufserlös (brutto)</span>
                        <span class="reentry-result-value" id="s_resRevenue">—</span>
                    </div>
                    <div class="reentry-result-row">
                        <span class="reentry-result-label">Gewinn (vor Steuern)</span>
                        <span class="reentry-result-value" id="s_resProfit">—</span>
                    </div>
                    <div class="reentry-result-row">
                        <span class="reentry-result-label">Steuern</span>
                        <span class="reentry-result-value" id="s_resTaxes">—</span>
                    </div>
                    <div class="reentry-result-row">
                        <span class="reentry-result-label">Nettokapital nach Verkauf</span>
                        <span class="reentry-result-value" id="s_resNetCapital">—</span>
                    </div>
                    <div class="reentry-breakeven">
                        <div class="be-label">Re-Entry Break-Even Kurs</div>
                        <div class="be-price" id="s_resBreakEven">—</div>
                        <div class="be-drop">Nötiger Kursrückgang: <strong id="s_resDrop">—</strong></div>
                    </div>
                    <button class="reentry-save-btn" onclick="saveSellToHistory()">💾 In Historie speichern</button>
                </div>
            </div>

            <!-- Tab 2: Offene Positionen -->
            <div class="reentry-panel" id="panel-portfolio">
                <div id="portfolioLots" style="margin-bottom:16px;"></div>
                <div class="reentry-form-grid">
                    <div class="reentry-field">
                        <label>Hypothetischer Verkaufskurs (€)</label>
                        <input type="number" id="p_sellPrice" step="0.01" oninput="calcPortfolio()">
                    </div>
                    <div class="reentry-field">
                        <label>Freier Freibetrag (€)</label>
                        <input type="number" id="p_allowance" value="0" step="1" oninput="calcPortfolio()">
                    </div>
                    <div class="reentry-field">
                        <label>Gebühren Kauf (€)</label>
                        <input type="number" id="p_feeBuy" value="0" step="0.01" oninput="calcPortfolio()">
                    </div>
                    <div class="reentry-field">
                        <label>Gebühren Verkauf (€)</label>
                        <input type="number" id="p_feeSell" value="0" step="0.01" oninput="calcPortfolio()">
                    </div>
                </div>
                <div class="reentry-checkbox-row">
                    <input type="checkbox" id="p_kirchensteuer" onchange="calcPortfolio()">
                    <label for="p_kirchensteuer">Kirchensteuer</label>
                    <select id="p_kirchensteuerRate" onchange="calcPortfolio()" style="width:auto;padding:4px 8px;border:1px solid #cbd5e0;border-radius:6px;font-size:0.85em;">
                        <option value="0.08">8% (Bayern, BaWü)</option>
                        <option value="0.09">9% (Restliche BL)</option>
                    </select>
                </div>
                <div class="reentry-results">
                    <div class="reentry-result-row">
                        <span class="reentry-result-label">Verkaufserlös (brutto)</span>
                        <span class="reentry-result-value" id="p_resRevenue">—</span>
                    </div>
                    <div class="reentry-result-row">
                        <span class="reentry-result-label">Gewinn (vor Steuern)</span>
                        <span class="reentry-result-value" id="p_resProfit">—</span>
                    </div>
                    <div class="reentry-result-row">
                        <span class="reentry-result-label">KapESt + Soli (berechnet)</span>
                        <span class="reentry-result-value" id="p_resTaxes">—</span>
                    </div>
                    <div class="reentry-result-row">
                        <span class="reentry-result-label">Nettokapital nach Verkauf</span>
                        <span class="reentry-result-value" id="p_resNetCapital">—</span>
                    </div>
                    <div class="reentry-breakeven">
                        <div class="be-label">Re-Entry Break-Even Kurs</div>
                        <div class="be-price" id="p_resBreakEven">—</div>
                        <div class="be-drop">Nötiger Kursrückgang: <strong id="p_resDrop">—</strong></div>
                    </div>
                </div>
            </div>

            <!-- Historia -->
            <div class="reentry-history-section" id="reentryHistorySection" style="display:none;">
                <h3>📋 Gespeicherte Trades</h3>
                <div class="reentry-history-btns">
                    <button class="reentry-history-btn btn-export" onclick="exportReentryCSV()">CSV Export</button>
                    <button class="reentry-history-btn btn-clear" onclick="clearReentryHistory()">Leeren</button>
                </div>
                <div style="overflow-x:auto;margin-top:12px;">
                    <table class="reentry-history-table">
                        <thead>
                            <tr>
                                <th>Datum</th>
                                <th>Aktie</th>
                                <th>Kauf / Verkauf</th>
                                <th>Stück</th>
                                <th style="text-align:right;">Netto-Kapital</th>
                                <th style="text-align:right;">Re-Entry Kurs</th>
                                <th style="text-align:right;">Nötiger Drop</th>
                                <th style="text-align:center;">Löschen</th>
                            </tr>
                        </thead>
                        <tbody id="reentryHistoryBody"></tbody>
                    </table>
                </div>
            </div>
        </div>
```

Wichtig: `{{reentry_json}}` muss im f-string als `{{reentry_json}}` escaped sein, aber `{reentry_json}` als echte Variable. Da `reentry_json` eine lokale Variable ist, die vor dem f-string definiert wird, muss die Zeile im Template-Code lauten:

```python
html_template = f"""...
        <script>
        const FIFO_DATA = {reentry_json};
        </script>
..."""
```

(Nur `{reentry_json}` ohne doppelte geschweifte Klammern — alle anderen `{{` im HTML bleiben doppelt wegen f-string-Escaping.)

---

## Task 5: Re-Entry JavaScript implementieren

**Files:**
- Modify: `portfolio_analyzer.py` — JavaScript-Block am Ende des `<body>`, vor `</body>` in `_create_html_template()`

- [ ] **Schritt 1: JavaScript-Block einfügen**

Direkt vor `</body>` im HTML-Template folgenden `<script>`-Block einfügen:

```html
    <script>
    // ---- Hilfsfunktionen ----
    const eur = (v) => new Intl.NumberFormat('de-DE', {{style:'currency',currency:'EUR'}}).format(v);
    const pct = (v) => new Intl.NumberFormat('de-DE', {{maximumFractionDigits:2}}).format(v) + '%';

    // ---- Tab-Switching ----
    function switchTab(name) {{
        document.querySelectorAll('.reentry-tab').forEach((t,i) => {{
            t.classList.toggle('active', (i===0 && name==='sells') || (i===1 && name==='portfolio'));
        }});
        document.getElementById('panel-sells').classList.toggle('active', name==='sells');
        document.getElementById('panel-portfolio').classList.toggle('active', name==='portfolio');
    }}

    // ---- Verkäufe: Dropdown befüllen ----
    function initSellDropdown() {{
        const sel = document.getElementById('sellSelect');
        (FIFO_DATA.sells || []).forEach((s, i) => {{
            const opt = document.createElement('option');
            opt.value = i;
            opt.text = `${{s.date}} — ${{eur(s.sellPrice)}} × ${{s.shares}} Stk`;
            sel.appendChild(opt);
        }});
    }}

    function loadSell() {{
        const idx = document.getElementById('sellSelect').value;
        if (idx === '') return;
        const s = FIFO_DATA.sells[parseInt(idx)];
        // Ältestes offenes Lot als Referenz-Kaufkurs
        const oldestLot = FIFO_DATA.portfolio.length > 0 ? FIFO_DATA.portfolio[0].buyPrice : (s.avgBuyPrice || 0);
        document.getElementById('s_buyPrice').value = oldestLot;
        document.getElementById('s_sellPrice').value = s.sellPrice;
        document.getElementById('s_shares').value = s.shares;
        document.getElementById('s_taxes').value = s.taxes;
        document.getElementById('s_feeBuy').value = s.fee || 0;
        document.getElementById('s_feeSell').value = s.fee || 0;
        calcSell();
    }}

    function calcSell() {{
        const buyPrice  = parseFloat(document.getElementById('s_buyPrice').value)  || 0;
        const sellPrice = parseFloat(document.getElementById('s_sellPrice').value) || 0;
        const shares    = parseFloat(document.getElementById('s_shares').value)    || 0;
        const taxes     = parseFloat(document.getElementById('s_taxes').value)     || 0;
        const feeBuy    = parseFloat(document.getElementById('s_feeBuy').value)    || 0;
        const feeSell   = parseFloat(document.getElementById('s_feeSell').value)   || 0;

        const invested    = buyPrice * shares + feeBuy;
        const grossRev    = sellPrice * shares - feeSell;
        const profit      = grossRev - invested;
        const netCapital  = grossRev - taxes;
        const breakEven   = shares > 0 ? (netCapital - feeBuy) / shares : 0;
        const drop        = sellPrice > 0 ? ((sellPrice - breakEven) / sellPrice) * 100 : 0;

        document.getElementById('s_resRevenue').textContent   = eur(grossRev);
        document.getElementById('s_resProfit').textContent    = eur(profit);
        document.getElementById('s_resTaxes').textContent     = eur(taxes);
        document.getElementById('s_resNetCapital').textContent = eur(netCapital);
        document.getElementById('s_resBreakEven').textContent = eur(breakEven);
        document.getElementById('s_resDrop').textContent      = pct(drop);
    }}

    // ---- Offene Positionen: Lots anzeigen ----
    function initPortfolioLots() {{
        const container = document.getElementById('portfolioLots');
        if (!FIFO_DATA.portfolio || FIFO_DATA.portfolio.length === 0) {{
            container.innerHTML = '<p style="color:#718096;font-size:0.9em;">Keine offenen Positionen vorhanden.</p>';
            return;
        }}
        let html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:12px;">';
        FIFO_DATA.portfolio.forEach((lot, i) => {{
            html += `<div style="background:#f7fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;font-size:0.85em;">
                <div style="font-weight:700;color:#2a5298;">Lot ${{i+1}}</div>
                <div style="color:#4a5568;">Kaufkurs: <strong>${{eur(lot.buyPrice)}}</strong></div>
                <div style="color:#4a5568;">Stück: <strong>${{lot.shares}}</strong></div>
                <div style="color:#718096;font-size:0.8em;">${{lot.date}}</div>
            </div>`;
        }});
        html += '</div>';
        // Lot-Auswahl für Rechner
        html += '<div class="reentry-field"><label>Lot für Berechnung verwenden</label><select id="p_lotSelect" onchange="calcPortfolio()" style="width:100%;padding:10px 12px;border:1px solid #cbd5e0;border-radius:8px;font-size:1em;">';
        FIFO_DATA.portfolio.forEach((lot, i) => {{
            html += `<option value="${{i}}">Lot ${{i+1}}: ${{eur(lot.buyPrice)}} × ${{lot.shares}} Stk (${{lot.date}})</option>`;
        }});
        html += '</select></div>';
        container.innerHTML = html;
        // Startwert Verkaufskurs
        if (FIFO_DATA.currentPrice) {{
            document.getElementById('p_sellPrice').value = FIFO_DATA.currentPrice;
        }}
        calcPortfolio();
    }}

    function calcPortfolio() {{
        const lotSel = document.getElementById('p_lotSelect');
        if (!lotSel) return;
        const lot       = FIFO_DATA.portfolio[parseInt(lotSel.value)];
        const sellPrice = parseFloat(document.getElementById('p_sellPrice').value) || 0;
        const allowance = parseFloat(document.getElementById('p_allowance').value) || 0;
        const feeBuy    = parseFloat(document.getElementById('p_feeBuy').value)    || 0;
        const feeSell   = parseFloat(document.getElementById('p_feeSell').value)   || 0;
        const kirchenOn = document.getElementById('p_kirchensteuer').checked;
        const kirchenRate = kirchenOn ? parseFloat(document.getElementById('p_kirchensteuerRate').value) : 0;

        const shares    = lot.shares;
        const buyPrice  = lot.buyPrice;
        const invested  = buyPrice * shares + feeBuy;
        const grossRev  = sellPrice * shares - feeSell;
        const profit    = grossRev - invested;

        let taxes = 0;
        if (profit > 0) {{
            const taxableProfit = Math.max(0, profit - allowance);
            if (taxableProfit > 0) {{
                const baseRate = 0.25 / (1 + 0.25 * kirchenRate);
                const kapEst   = taxableProfit * baseRate;
                const soli     = kapEst * 0.055;
                const kirchen  = kapEst * kirchenRate;
                taxes = kapEst + soli + kirchen;
            }}
        }}

        const netCapital = grossRev - taxes;
        const breakEven  = shares > 0 ? (netCapital - feeBuy) / shares : 0;
        const drop       = sellPrice > 0 ? ((sellPrice - breakEven) / sellPrice) * 100 : 0;

        document.getElementById('p_resRevenue').textContent    = eur(grossRev);
        document.getElementById('p_resProfit').textContent     = eur(profit);
        document.getElementById('p_resTaxes').textContent      = eur(taxes);
        document.getElementById('p_resNetCapital').textContent = eur(netCapital);
        document.getElementById('p_resBreakEven').textContent  = eur(breakEven);
        document.getElementById('p_resDrop').textContent       = pct(drop);
    }}

    // ---- Historie ----
    let reentryHistory = JSON.parse(localStorage.getItem('reentryHistory') || '[]');

    function saveSellToHistory() {{
        const entry = {{
            id: Date.now().toString(),
            date: new Date().toLocaleDateString('de-DE'),
            stock: FIFO_DATA.companyName,
            buyPrice: parseFloat(document.getElementById('s_buyPrice').value) || 0,
            sellPrice: parseFloat(document.getElementById('s_sellPrice').value) || 0,
            shares: parseFloat(document.getElementById('s_shares').value) || 0,
            netCapital: parseFloat((document.getElementById('s_resNetCapital').textContent || '0').replace(/[^0-9,\-]/g,'').replace(',','.')),
            breakEven: parseFloat((document.getElementById('s_resBreakEven').textContent || '0').replace(/[^0-9,\-]/g,'').replace(',','.')),
            drop: (document.getElementById('s_resDrop').textContent || '0').replace('%','').trim(),
        }};
        reentryHistory.push(entry);
        localStorage.setItem('reentryHistory', JSON.stringify(reentryHistory));
        renderReentryHistory();
    }}

    function renderReentryHistory() {{
        const section = document.getElementById('reentryHistorySection');
        const tbody   = document.getElementById('reentryHistoryBody');
        if (reentryHistory.length === 0) {{ section.style.display = 'none'; return; }}
        section.style.display = 'block';
        tbody.innerHTML = reentryHistory.map(t => `
            <tr>
                <td>${{t.date}}</td>
                <td>${{t.stock}}</td>
                <td>${{eur(t.buyPrice)}} / ${{eur(t.sellPrice)}}</td>
                <td>${{t.shares}}</td>
                <td style="text-align:right;font-weight:600;">${{eur(t.netCapital)}}</td>
                <td style="text-align:right;color:#2a5298;font-weight:600;">${{eur(t.breakEven)}}</td>
                <td style="text-align:right;">-${{t.drop}}%</td>
                <td style="text-align:center;">
                    <button onclick="deleteReentryEntry('${{t.id}}')" style="color:#c53030;background:none;border:none;cursor:pointer;font-size:1.1em;">🗑</button>
                </td>
            </tr>`).join('');
    }}

    function deleteReentryEntry(id) {{
        reentryHistory = reentryHistory.filter(t => t.id !== id);
        localStorage.setItem('reentryHistory', JSON.stringify(reentryHistory));
        renderReentryHistory();
    }}

    function clearReentryHistory() {{
        if (confirm('Historie wirklich löschen?')) {{
            reentryHistory = [];
            localStorage.removeItem('reentryHistory');
            renderReentryHistory();
        }}
    }}

    function exportReentryCSV() {{
        if (reentryHistory.length === 0) return;
        let csv = 'Datum;Aktie;Kaufkurs;Verkaufskurs;Stueck;NettoKapital;ReEntryKurs;DropProzent\n';
        reentryHistory.forEach(t => {{
            csv += `${{t.date}};${{t.stock}};${{t.buyPrice}};${{t.sellPrice}};${{t.shares}};${{t.netCapital}};${{t.breakEven}};${{t.drop}}\n`;
        }});
        const blob = new Blob([csv], {{type:'text/csv;charset=utf-8;'}});
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href = url; a.download = 'ReEntry_Historie.csv';
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
    }}

    // ---- Demo-Toggle ----
    let demoActive = false;
    let originalData = null;

    function toggleDemo() {{
        demoActive = !demoActive;
        const btn = document.getElementById('demoToggleBtn');
        btn.classList.toggle('active', demoActive);
        btn.textContent = demoActive ? '✅ Demo aktiv' : '🎭 Demo-Ansicht';

        if (demoActive) {{
            // Originaldaten sichern (DOM-Werte der Karten)
            originalData = {{}};
            document.querySelectorAll('.summary-card .value').forEach((el, i) => {{
                originalData['card_' + i] = el.textContent;
            }});
            document.querySelectorAll('.header h1').forEach(el => {{ originalData['h1'] = el.textContent; }});

            // Aktienname ersetzen
            document.querySelectorAll('.header h1').forEach(el => {{ el.textContent = '🚀 DEMO CORP AG'; }});
            document.title = 'Demo Corp AG - Portfolio-Analyse';

            // Zahlen in Karten durch Zufallswerte ersetzen (Faktor 0.4–1.6, aber plausibel)
            document.querySelectorAll('.summary-card .value').forEach((el) => {{
                const raw = el.textContent.replace(/[^0-9,\-]/g,'').replace(',','.');
                const num = parseFloat(raw);
                if (!isNaN(num) && num !== 0) {{
                    const factor = 0.5 + Math.random() * 0.8;
                    const faked  = Math.round(num * factor);
                    el.textContent = el.textContent.replace(raw.replace('.',','), faked.toLocaleString('de-DE'));
                }}
            }});
        }} else {{
            // Originaldaten wiederherstellen
            document.querySelectorAll('.summary-card .value').forEach((el, i) => {{
                if (originalData && originalData['card_' + i]) el.textContent = originalData['card_' + i];
            }});
            document.querySelectorAll('.header h1').forEach(el => {{
                if (originalData) el.textContent = originalData['h1'];
            }});
            document.title = document.querySelector('title')?.dataset?.orig || document.title;
        }}
    }}

    // ---- Init ----
    initSellDropdown();
    initPortfolioLots();
    renderReentryHistory();
    </script>
```

- [ ] **Schritt 2: Report generieren und funktional testen**

```
python portfolio_analyzer.py
```

Browser öffnet sich automatisch. Prüfe:
1. Re-Entry-Abschnitt erscheint unterhalb der Kennzahl-Karten
2. Tab "Abgeschlossene Verkäufe": Dropdown zeigt alle Verkäufe aus der CSV
3. Verkauf auswählen → Felder werden automatisch befüllt → Ergebnisse erscheinen
4. Tab "Offene Positionen": Lots werden angezeigt, Berechnung funktioniert
5. Kirchensteuer-Checkbox aktivieren → Berechnung ändert sich
6. "In Historie speichern" → Tabelle erscheint
7. Demo-Toggle Button oben rechts → Zahlen werden maskiert, nochmals klicken → Original zurück
8. Kein JS-Fehler in der Browser-Konsole (F12)

---

## Task 6: Abschluss und Bereinigung

**Files:**
- Verify: `.gitignore` korrekt
- Verify: `examples/`-CSVs nicht ignoriert

- [ ] **Schritt 1: Sicherstellen dass `output/*.html` und `csvs/*.csv` in `.gitignore` stehen**

Prüfe `C:\Users\Becht\Python-Projecte\FIFO\.gitignore`:
```
csvs/*.csv      ← muss vorhanden sein
output/*.html   ← muss vorhanden sein
```

- [ ] **Schritt 2: Prüfen dass keine Credentials oder API-Keys im Code sind**

```
grep -r "api_key\|API_KEY\|secret\|token\|password" portfolio_analyzer.py
```
Erwartetes Ergebnis: Keine Treffer.

- [ ] **Schritt 3: Finale Prüfung mit Beispiel-CSV**

```
python portfolio_analyzer.py
```
Öffnet den Report mit `examples/palantir.csv` (oder welche CSV auch immer im Hauptaufruf genutzt wird). Alle Features funktionieren wie in Task 5 Schritt 2 beschrieben.

---

## Self-Review Checkliste

- [x] **Spec-Coverage:** `.gitignore` (Task 1) ✓, `_build_reentry_data()` (Task 2) ✓, CSS (Task 3) ✓, HTML (Task 4) ✓, JS mit beiden Tabs + Demo-Toggle + Historie (Task 5) ✓
- [x] **Kein Placeholder:** Alle Schritte enthalten vollständigen Code
- [x] **Typ-Konsistenz:** `FIFO_DATA.sells`, `FIFO_DATA.portfolio`, `FIFO_DATA.currentPrice`, `FIFO_DATA.companyName` — konsistent zwischen Task 2 (Python) und Task 5 (JS)
- [x] **f-string Escaping:** Alle `{{` und `}}` im HTML-Template sind doppelt, nur `{reentry_json}` ist einfach
- [x] **Security:** Kein API-Key, kein hardcoded Secret, `.gitignore` schützt echte Daten
