---
read_when:
    - Erweitern von qa-lab oder qa-channel
    - Hinzufügen repo-gestützter QA-Szenarien
    - Erstellen realitätsnäherer QA-Automatisierung rund um das Gateway-Dashboard
summary: Private QA-Automatisierungsform für qa-lab, qa-channel, Seed-Szenarien und Protokollberichte
title: QA E2E-Automatisierung
x-i18n:
    generated_at: "2026-04-08T06:00:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 57da147dc06abf9620290104e01a83b42182db1806514114fd9e8467492cda99
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E-Automatisierung

Der private QA-Stack soll OpenClaw auf realistischere, kanalähnliche Weise
testen, als es ein einzelner Unit-Test kann.

Aktuelle Bestandteile:

- `extensions/qa-channel`: synthetischer Nachrichtenkanal mit Oberflächen für DMs, Kanäle, Threads,
  Reaktionen, Bearbeitungen und Löschungen.
- `extensions/qa-lab`: Debugger-UI und QA-Bus zum Beobachten des Transkripts,
  Einspielen eingehender Nachrichten und Exportieren eines Markdown-Berichts.
- `qa/`: repo-gestützte Seed-Assets für die Startaufgabe und grundlegende QA-
  Szenarien.

Der aktuelle QA-Operator-Workflow ist eine QA-Site mit zwei Bereichen:

- Links: Gateway-Dashboard (Control UI) mit dem Agenten.
- Rechts: QA Lab, das das Slack-ähnliche Transkript und den Szenarioplan anzeigt.

Führe es aus mit:

```bash
pnpm qa:lab:up
```

Dadurch wird die QA-Site gebaut, der Docker-gestützte Gateway-Lane gestartet und die
QA-Lab-Seite bereitgestellt, auf der ein Operator oder eine Automatisierungsschleife dem Agenten eine QA-
Mission geben, echtes Kanalverhalten beobachten und aufzeichnen kann, was funktioniert hat, fehlgeschlagen ist oder
blockiert geblieben ist.

Für schnellere Iterationen an der QA-Lab-UI, ohne das Docker-Image jedes Mal neu zu bauen,
starte den Stack mit einem per Bind-Mount eingebundenen QA-Lab-Bundle:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` hält die Docker-Services auf einem vorab gebauten Image und bind-mountet
`extensions/qa-lab/web/dist` in den Container `qa-lab`. `qa:lab:watch`
baut dieses Bundle bei Änderungen neu, und der Browser lädt automatisch neu, wenn sich der Asset-Hash von QA Lab ändert.

## Repo-gestützte Seeds

Seed-Assets liegen in `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Diese liegen absichtlich in git, damit der QA-Plan sowohl für Menschen als auch für den
Agenten sichtbar ist. Die grundlegende Liste sollte breit genug bleiben, um Folgendes abzudecken:

- DM- und Kanal-Chat
- Thread-Verhalten
- Lebenszyklus von Nachrichtenaktionen
- Cron-Callbacks
- Memory Recall
- Modellwechsel
- Übergabe an Subagenten
- Lesen des Repos und Lesen der Dokumentation
- eine kleine Build-Aufgabe wie Lobster Invaders

## Berichterstellung

`qa-lab` exportiert einen Markdown-Protokollbericht aus der beobachteten Bus-Zeitleiste.
Der Bericht sollte Folgendes beantworten:

- Was funktioniert hat
- Was fehlgeschlagen ist
- Was blockiert geblieben ist
- Welche Folgeszenarien sich hinzuzufügen lohnen

## Verwandte Dokumentation

- [Testing](/de/help/testing)
- [QA Channel](/de/channels/qa-channel)
- [Dashboard](/web/dashboard)
