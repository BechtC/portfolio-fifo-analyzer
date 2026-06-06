## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/9

## What to build

Das neue HTML-Grundgerüst für den generierten Report: `_create_html_template()` wird komplett neu geschrieben. Das Ergebnis ist ein Dark-Mode-Dashboard mit Tailwind CSS via CDN, fünf semantischen Abschnitten (Header, Hero, Re-Entry, Chart, Transaktionen) und dem eingebetteten `FIFO_DATA` JSON. Alle bestehenden Inhalte sind zunächst als Platzhalter vorhanden — die einzelnen Abschnitte werden in Folge-Issues befüllt.

Der Header zeigt Aktienname, Generierungsdatum und zwei Button-Platzhalter (Dark-Mode-Toggle, Demo-Toggle). Das `<html>`-Tag hat `class="dark"` standardmäßig gesetzt. Das Body-Hintergrund ist `bg-gray-950`, Text `text-gray-100`.

## Acceptance criteria

- [ ] `_create_html_template()` generiert valides HTML mit `class="dark"` auf `<html>`
- [ ] Tailwind CSS CDN ist eingebunden (`https://cdn.tailwindcss.com`)
- [ ] Chart.js CDN ist eingebunden (`https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js`)
- [ ] `<script>const FIFO_DATA = ...;</script>` ist im generierten HTML vorhanden
- [ ] Fünf Abschnitte mit IDs vorhanden: `hero-section`, `reentry-section`, `chart-section`, `transactions-section`
- [ ] Header zeigt Aktienname und Generierungsdatum
- [ ] `python portfolio_analyzer.py` läuft ohne SyntaxWarning und ohne UnicodeEncodeError
- [ ] Report öffnet sich automatisch im Browser

## Blocked by

None - can start immediately
