## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/9

## What to build

Den `hero-section` Abschnitt mit fünf prominenten Metriken befüllen: Gesamt Investiert, Gesamt Entnommen, Realisierte Gewinne, Unrealisierte Gewinne, Gesamtrendite (%). Jede Karte hat einen großen Zahlenwert, einen Label, und eine Farb-Kodierung (grün für positive Werte, rot für negative, indigo/neutral für investierte Beträge). Layout: 5-spaltiges Grid auf Desktop, 2-spaltig auf Mobil.

## Acceptance criteria

- [ ] Fünf Hero-Karten sind sichtbar: Investiert, Entnommen, Realisiert, Unrealisiert, Performance %
- [ ] Positive Werte sind in `emerald-400`, negative in `red-400` dargestellt
- [ ] Gesamtrendite zeigt `+` oder `-` Prefix
- [ ] Layout ist 5-spaltig auf Desktop (≥ 1024px) und 2-spaltig auf Mobil
- [ ] Alle Werte kommen aus `template_data` (Python-seitig generiert, kein JS nötig)
- [ ] Karten haben abgerundete Ecken, subtile Border und Hover-Effekt

## Blocked by

- https://github.com/BechtC/portfolio-fifo-analyzer/issues/10 (Grundgerüst muss existieren)
