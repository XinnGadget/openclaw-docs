---
read_when:
    - Erweitern von qa-lab oder qa-channel
    - Hinzufügen von repo-gestützten QA-Szenarien
    - Erstellen realitätsnäherer QA-Automatisierung rund um das Gateway-Dashboard
summary: Form der privaten QA-Automatisierung für qa-lab, qa-channel, vordefinierte Szenarien und Protokollberichte
title: QA-E2E-Automatisierung
x-i18n:
    generated_at: "2026-04-09T01:27:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: c922607d67e0f3a2489ac82bc9f510f7294ced039c1014c15b676d826441d833
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA-E2E-Automatisierung

Der private QA-Stack soll OpenClaw auf realistischere,
kanalähnliche Weise prüfen, als es ein einzelner Unit-Test kann.

Aktuelle Bestandteile:

- `extensions/qa-channel`: synthetischer Nachrichtenkanal mit DM-, Kanal-, Thread-,
  Reaktions-, Bearbeitungs- und Löschoberflächen.
- `extensions/qa-lab`: Debugger-UI und QA-Bus zum Beobachten des Transkripts,
  Einspeisen eingehender Nachrichten und Exportieren eines Markdown-Berichts.
- `qa/`: repo-gestützte Seed-Assets für die Startaufgabe und grundlegende QA-
  Szenarien.

Der aktuelle QA-Operator-Ablauf ist eine QA-Site mit zwei Bereichen:

- Links: Gateway-Dashboard (Control UI) mit dem Agenten.
- Rechts: QA Lab mit dem Slack-ähnlichen Transkript und dem Szenarioplan.

Starten Sie es mit:

```bash
pnpm qa:lab:up
```

Dadurch wird die QA-Site gebaut, die Docker-gestützte Gateway-Lane gestartet und
die QA-Lab-Seite bereitgestellt, auf der ein Operator oder eine
Automatisierungsschleife dem Agenten eine QA-Mission geben, echtes
Kanalverhalten beobachten und festhalten kann, was funktioniert hat,
fehlgeschlagen ist oder blockiert blieb.

Für schnellere Iteration an der QA-Lab-UI, ohne das Docker-Image jedes Mal neu
zu bauen, starten Sie den Stack mit einem bind-gemounteten QA-Lab-Bundle:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` hält die Docker-Services auf einem vorab gebauten Image und
bind-mountet `extensions/qa-lab/web/dist` in den `qa-lab`-Container. `qa:lab:watch`
baut dieses Bundle bei Änderungen neu, und der Browser lädt automatisch neu,
wenn sich der Asset-Hash von QA Lab ändert.

## Repo-gestützte Seeds

Seed-Assets liegen in `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Diese liegen bewusst in Git, damit der QA-Plan sowohl für Menschen als auch für
den Agenten sichtbar ist. Die Basisliste sollte breit genug bleiben, um
Folgendes abzudecken:

- DM- und Kanal-Chat
- Thread-Verhalten
- Lebenszyklus von Nachrichtenaktionen
- Cron-Callbacks
- Speicherabruf
- Modellwechsel
- Übergabe an Subagenten
- Lesen des Repos und Lesen der Dokumentation
- eine kleine Build-Aufgabe wie Lobster Invaders

## Berichterstellung

`qa-lab` exportiert einen Markdown-Protokollbericht aus der beobachteten
Bus-Zeitleiste.
Der Bericht sollte Folgendes beantworten:

- Was funktioniert hat
- Was fehlgeschlagen ist
- Was blockiert blieb
- Welche Folge-Szenarien sich hinzuzufügen lohnen

Für Charakter- und Stilprüfungen führen Sie dasselbe Szenario über mehrere Live-Modell-
Refs aus und schreiben einen bewerteten Markdown-Bericht:

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

Der Befehl führt lokale QA-Gateway-Kindprozesse aus, nicht Docker. Character-eval-
Szenarien sollten die Persona über `SOUL.md` festlegen und dann gewöhnliche
Benutzer-Turns ausführen, etwa Chat, Hilfe zum Workspace und kleine
Dateiaufgaben. Dem Kandidatenmodell sollte nicht mitgeteilt werden, dass es
bewertet wird. Der Befehl bewahrt jedes vollständige Transkript auf, erfasst
grundlegende Laufstatistiken und bittet dann die Bewertungsmodelle im schnellen
Modus mit `xhigh`-Reasoning, die Läufe nach Natürlichkeit, Vibe und Humor zu
bewerten.
Verwenden Sie `--blind-judge-models`, wenn Sie Provider vergleichen: Der Prompt
für die Bewertungsmodelle erhält weiterhin jedes Transkript und jeden
Laufstatus, aber Kandidaten-Refs werden durch neutrale Bezeichnungen wie
`candidate-01` ersetzt; der Bericht ordnet die Ranglisten nach dem Parsen wieder
den echten Refs zu.
Kandidatenläufe verwenden standardmäßig `high` Thinking, mit `xhigh` für
OpenAI-Modelle, die dies unterstützen. Überschreiben Sie einen bestimmten
Kandidaten inline mit
`--model provider/model,thinking=<level>`. `--thinking <level>` setzt weiterhin
einen globalen Fallback, und die ältere Form
`--model-thinking <provider/model=level>` wird aus Kompatibilitätsgründen
beibehalten.
OpenAI-Kandidaten-Refs verwenden standardmäßig den schnellen Modus, damit
Prioritätsverarbeitung genutzt wird, sofern der Provider dies unterstützt.
Fügen Sie inline `,fast`, `,no-fast` oder `,fast=false` hinzu, wenn ein einzelner
Kandidat oder ein Bewertungsmodell eine Überschreibung benötigt. Übergeben Sie
`--fast` nur, wenn Sie den schnellen Modus für jedes Kandidatenmodell erzwingen
möchten. Dauer von Kandidaten- und Bewertungsmodellläufen wird zur
Benchmark-Analyse im Bericht erfasst, aber die Prompts für die
Bewertungsmodelle weisen ausdrücklich an, nicht nach Geschwindigkeit zu
bewerten.
Kandidaten- und Bewertungsmodellläufe verwenden beide standardmäßig eine
Parallelität von 16. Senken Sie `--concurrency` oder `--judge-concurrency`,
wenn Provider-Limits oder Druck auf das lokale Gateway einen Lauf zu unruhig
machen.
Wenn kein Kandidaten-`--model` übergeben wird, verwendet character-eval
standardmäßig
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` und
`google/gemini-3.1-pro-preview`, wenn kein `--model` übergeben wird.
Wenn kein `--judge-model` übergeben wird, verwenden die Bewertungsmodelle
standardmäßig
`openai/gpt-5.4,thinking=xhigh,fast` und
`anthropic/claude-opus-4-6,thinking=high`.

## Verwandte Dokumentation

- [Tests](/de/help/testing)
- [QA Channel](/de/channels/qa-channel)
- [Dashboard](/web/dashboard)
