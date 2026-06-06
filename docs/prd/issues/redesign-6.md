## Parent

https://github.com/BechtC/portfolio-fifo-analyzer/issues/9

## What to build

Den Dark/Light Mode Toggle im Header implementieren. Button mit Mond/Sonne-Icon: Klick entfernt/setzt `class="dark"` auf dem `<html>`-Element. Präferenz wird in LocalStorage gespeichert und beim Laden wiederhergestellt. Im Light Mode: `bg-gray-50` Body, `text-gray-900` Text, weiße Karten.

## Acceptance criteria

- [ ] Toggle-Button ist im Header sichtbar (Mond-Icon im Dark Mode, Sonne-Icon im Light Mode)
- [ ] Klick wechselt zwischen Dark und Light Mode ohne Seitenreload
- [ ] Light Mode hat hellen Hintergrund und dunklen Text
- [ ] Präferenz wird in LocalStorage gespeichert
- [ ] Beim erneuten Öffnen des Reports wird die gespeicherte Präferenz angewendet
- [ ] Kein JS-Fehler in der Browser-Konsole

## Blocked by

- https://github.com/BechtC/portfolio-fifo-analyzer/issues/11 (Hero-Karten müssen existieren)
