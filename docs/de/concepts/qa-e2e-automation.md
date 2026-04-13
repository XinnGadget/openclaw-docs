---
read_when:
    - Erweitern von qa-lab oder qa-channel
    - Hinzufügen von repository-gestützten QA-Szenarien
    - Aufbau einer realistischeren QA-Automatisierung rund um das Gateway-Dashboard
summary: Private QA-Automatisierungsstruktur für qa-lab, qa-channel, vordefinierte Szenarien und Protokollberichte
title: QA-End-to-End-Automatisierung
x-i18n:
    generated_at: "2026-04-13T06:29:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: a4a4f5c765163565c95c2a071f201775fd9d8d60cad4ff25d71e4710559c1570
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA-End-to-End-Automatisierung

Der private QA-Stack ist dafür gedacht, OpenClaw auf eine realistischere,
kanalähnliche Weise zu prüfen, als es ein einzelner Unit-Test kann.

Aktuelle Bestandteile:

- `extensions/qa-channel`: synthetischer Nachrichtenkanal mit Oberflächen für DM, Kanal, Thread,
  Reaktion, Bearbeiten und Löschen.
- `extensions/qa-lab`: Debugger-UI und QA-Bus zum Beobachten des Transkripts,
  Einfügen eingehender Nachrichten und Exportieren eines Markdown-Berichts.
- `qa/`: repository-gestützte Seed-Assets für die Startaufgabe und grundlegende QA-
  Szenarien.

Der aktuelle QA-Operator-Workflow ist eine QA-Site mit zwei Bereichen:

- Links: Gateway-Dashboard (Control UI) mit dem Agenten.
- Rechts: QA Lab, das das Slack-ähnliche Transkript und den Szenarioplan anzeigt.

Starten Sie sie mit:

```bash
pnpm qa:lab:up
```

Dadurch wird die QA-Site gebaut, die Docker-gestützte Gateway-Umgebung gestartet und die
QA-Lab-Seite bereitgestellt, auf der ein Operator oder eine Automatisierungsschleife dem Agenten eine QA-
Mission geben, echtes Kanalverhalten beobachten und festhalten kann, was funktioniert hat, fehlgeschlagen ist oder
blockiert geblieben ist.

Für schnellere QA-Lab-UI-Iteration, ohne das Docker-Image jedes Mal neu zu bauen,
starten Sie den Stack mit einem bind-gemounteten QA-Lab-Bundle:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` hält die Docker-Dienste auf einem vorgefertigten Image und bind-mountet
`extensions/qa-lab/web/dist` in den Container `qa-lab`. `qa:lab:watch`
baut dieses Bundle bei Änderungen neu, und der Browser lädt automatisch neu, wenn sich der QA-Lab-
Asset-Hash ändert.

Für eine transportechte Matrix-Smoke-Umgebung führen Sie aus:

```bash
pnpm openclaw qa matrix
```

Diese Umgebung stellt in Docker einen temporären Tuwunel-Homeserver bereit, registriert
temporäre Driver-, SUT- und Observer-Benutzer, erstellt einen privaten Raum und führt dann
das echte Matrix-Plugin innerhalb eines untergeordneten QA-Gateway-Prozesses aus. Die Live-Transportumgebung hält
die Konfiguration des untergeordneten Prozesses auf den getesteten Transport beschränkt, sodass Matrix ohne
`qa-channel` in der Konfiguration des untergeordneten Prozesses läuft.

Für eine transportechte Telegram-Smoke-Umgebung führen Sie aus:

```bash
pnpm openclaw qa telegram
```

Diese Umgebung zielt auf eine echte private Telegram-Gruppe, anstatt einen temporären
Server bereitzustellen. Sie erfordert `OPENCLAW_QA_TELEGRAM_GROUP_ID`,
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` und
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN` sowie zwei unterschiedliche Bots in derselben
privaten Gruppe. Der SUT-Bot muss einen Telegram-Benutzernamen haben, und die Bot-zu-Bot-
Beobachtung funktioniert am besten, wenn bei beiden Bots der Modus für Bot-zu-Bot-Kommunikation
in `@BotFather` aktiviert ist.

Live-Transportumgebungen verwenden jetzt einen gemeinsamen kleineren Vertrag, statt jeweils
eine eigene Form für die Szenarioliste zu definieren:

`qa-channel` bleibt die umfassende synthetische Suite für Produktverhalten und ist nicht Teil
der Live-Transport-Abdeckungsmatrix.

| Umgebung | Canary | Erwähnungs-Gating | Allowlist-Blockierung | Antwort auf oberster Ebene | Fortsetzen nach Neustart | Thread-Nachverfolgung | Thread-Isolation | Reaktionsbeobachtung | Hilfebefehl |
| -------- | ------ | ----------------- | --------------------- | -------------------------- | ------------------------ | --------------------- | ---------------- | -------------------- | ----------- |
| Matrix   | x      | x                 | x                     | x                          | x                        | x                     | x                | x                    |             |
| Telegram | x      |                   |                       |                            |                          |                       |                  |                      | x           |

Dadurch bleibt `qa-channel` die umfassende Suite für Produktverhalten, während Matrix,
Telegram und zukünftige Live-Transporte sich eine explizite Checkliste für Transportverträge teilen.

Für eine temporäre Linux-VM-Umgebung, ohne Docker in den QA-Pfad einzubeziehen, führen Sie aus:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Dadurch wird ein frischer Multipass-Gast gestartet, Abhängigkeiten installiert, OpenClaw
innerhalb des Gasts gebaut, `qa suite` ausgeführt und dann der normale QA-Bericht sowie die
Zusammenfassung zurück nach `.artifacts/qa-e2e/...` auf dem Host kopiert.
Es verwendet dasselbe Verhalten bei der Szenarioauswahl wie `qa suite` auf dem Host.
Host- und Multipass-Suite-Läufe führen standardmäßig mehrere ausgewählte Szenarien parallel
mit isolierten Gateway-Workern aus, bis zu 64 Worker oder bis zur Anzahl der ausgewählten
Szenarien. Verwenden Sie `--concurrency <count>`, um die Anzahl der Worker anzupassen, oder
`--concurrency 1` für serielle Ausführung.
Live-Läufe leiten die unterstützten QA-Authentifizierungseingaben weiter, die für den
Gast praktikabel sind: Provider-Schlüssel per Umgebungsvariable, den Konfigurationspfad für den QA-Live-Provider und
`CODEX_HOME`, falls vorhanden. Halten Sie `--output-dir` unter dem Repository-Root, damit der Gast
über den gemounteten Workspace zurückschreiben kann.

## Repository-gestützte Seeds

Seed-Assets liegen in `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Diese liegen absichtlich in git, damit der QA-Plan sowohl für Menschen als auch für den
Agenten sichtbar ist.

`qa-lab` sollte ein generischer Markdown-Runner bleiben. Jede Markdown-Datei für ein Szenario ist
die Quelle der Wahrheit für einen Testlauf und sollte Folgendes definieren:

- Szenario-Metadaten
- Dokumentations- und Code-Referenzen
- optionale Plugin-Anforderungen
- optionaler Gateway-Konfigurations-Patch
- der ausführbare `qa-flow`

Die wiederverwendbare Laufzeitoberfläche, die `qa-flow` unterstützt, darf generisch
und querschnittlich bleiben. Markdown-Szenarien können zum Beispiel
transportseitige Hilfsfunktionen mit browserseitigen Hilfsfunktionen kombinieren, die die eingebettete Control UI über die
Gateway-`browser.request`-Schnittstelle steuern, ohne einen Spezialfall-Runner hinzuzufügen.

Die Basisliste sollte breit genug bleiben, um Folgendes abzudecken:

- DM- und Kanal-Chat
- Thread-Verhalten
- Lebenszyklus von Nachrichtenaktionen
- Cron-Callbacks
- Speicherabruf
- Modellwechsel
- Subagent-Übergabe
- Lesen von Repository und Dokumentation
- eine kleine Build-Aufgabe wie Lobster Invaders

## Transportadapter

`qa-lab` besitzt eine generische Transportschnittstelle für Markdown-QA-Szenarien.
`qa-channel` ist der erste Adapter auf dieser Schnittstelle, aber das Designziel ist breiter:
zukünftige echte oder synthetische Kanäle sollten in denselben Suite-Runner eingebunden werden, statt einen
transportspezifischen QA-Runner hinzuzufügen.

Auf Architekturebene ist die Aufteilung wie folgt:

- `qa-lab` übernimmt generische Szenarioausführung, Worker-Parallelität, Schreiben von Artefakten und Berichterstellung.
- der Transportadapter übernimmt Gateway-Konfiguration, Bereitschaft, Beobachtung eingehender und ausgehender Daten, Transportaktionen und normalisierten Transportzustand.
- Markdown-Szenariodateien unter `qa/scenarios/` definieren den Testlauf; `qa-lab` stellt die wiederverwendbare Laufzeitoberfläche bereit, die ihn ausführt.

Maintainer-orientierte Hinweise zur Einführung neuer Kanaladapter finden Sie unter
[Testing](/de/help/testing#adding-a-channel-to-qa).

## Berichterstellung

`qa-lab` exportiert einen Markdown-Protokollbericht aus der beobachteten Bus-Zeitleiste.
Der Bericht sollte Folgendes beantworten:

- Was funktioniert hat
- Was fehlgeschlagen ist
- Was blockiert geblieben ist
- Welche Folgeszenarien sich hinzuzufügen lohnen

Für Zeichen- und Stilprüfungen führen Sie dasselbe Szenario über mehrere Live-Modell-
Referenzen aus und schreiben einen bewerteten Markdown-Bericht:

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

Der Befehl führt lokale untergeordnete QA-Gateway-Prozesse aus, nicht Docker. Character-Eval-
Szenarien sollten die Persona über `SOUL.md` setzen und dann gewöhnliche Benutzerinteraktionen
wie Chat, Workspace-Hilfe und kleine Dateiaufgaben ausführen. Dem Kandidatenmodell
sollte nicht gesagt werden, dass es bewertet wird. Der Befehl bewahrt jedes vollständige
Transkript auf, erfasst grundlegende Laufstatistiken und bittet dann die Bewertungsmodelle im schnellen Modus mit
`xhigh`-Reasoning, die Läufe nach Natürlichkeit, Stimmung und Humor zu ordnen.
Verwenden Sie `--blind-judge-models`, wenn Sie Provider vergleichen: Der Bewertungs-Prompt erhält weiterhin
jedes Transkript und jeden Laufstatus, aber Kandidaten-Referenzen werden durch neutrale
Bezeichnungen wie `candidate-01` ersetzt; der Bericht ordnet die Rangfolgen nach dem
Parsen wieder den echten Referenzen zu.
Kandidatenläufe verwenden standardmäßig `high` Thinking, mit `xhigh` für OpenAI-Modelle, die dies
unterstützen. Überschreiben Sie einen bestimmten Kandidaten inline mit
`--model provider/model,thinking=<level>`. `--thinking <level>` setzt weiterhin einen
globalen Fallback, und die ältere Form `--model-thinking <provider/model=level>` bleibt aus
Kompatibilitätsgründen erhalten.
OpenAI-Kandidaten-Referenzen verwenden standardmäßig den schnellen Modus, sodass Prioritätsverarbeitung genutzt wird, wo
der Provider dies unterstützt. Fügen Sie inline `,fast`, `,no-fast` oder `,fast=false` hinzu, wenn ein
einzelner Kandidat oder Bewerter eine Überschreibung benötigt. Übergeben Sie `--fast` nur, wenn Sie
den schnellen Modus für jedes Kandidatenmodell erzwingen möchten. Kandidaten- und Bewerterlaufzeiten werden
für Benchmark-Analysen im Bericht aufgezeichnet, aber in den Bewertungs-Prompts wird ausdrücklich darauf hingewiesen,
nicht nach Geschwindigkeit zu bewerten.
Kandidaten- und Bewertungsmodellläufe verwenden standardmäßig beide eine Parallelität von 16. Verringern Sie
`--concurrency` oder `--judge-concurrency`, wenn Provider-Limits oder lokaler Gateway-Druck einen Lauf zu unruhig machen.
Wenn kein Kandidat mit `--model` übergeben wird, verwendet die Character-Eval standardmäßig
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` und
`google/gemini-3.1-pro-preview`, wenn kein `--model` übergeben wird.
Wenn kein `--judge-model` übergeben wird, verwenden die Bewerter standardmäßig
`openai/gpt-5.4,thinking=xhigh,fast` und
`anthropic/claude-opus-4-6,thinking=high`.

## Verwandte Dokumentation

- [Testing](/de/help/testing)
- [QA Channel](/de/channels/qa-channel)
- [Dashboard](/web/dashboard)
