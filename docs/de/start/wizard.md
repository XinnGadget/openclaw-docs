---
read_when:
    - CLI-Onboarding ausführen oder konfigurieren
    - Einrichtung eines neuen Rechners
sidebarTitle: 'Onboarding: CLI'
summary: 'CLI-Onboarding: geführte Einrichtung für Gateway, Workspace, Channels und Skills'
title: Onboarding (CLI)
x-i18n:
    generated_at: "2026-04-05T10:50:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 81e33fb4f8be30e7c2c6e0024bf9bdcf48583ca58eaf5fff5afd37a1cd628523
    source_path: start/wizard.md
    workflow: 15
---

# Onboarding (CLI)

CLI-Onboarding ist der **empfohlene** Weg, um OpenClaw unter macOS,
Linux oder Windows (über WSL2; dringend empfohlen) einzurichten.
Es konfiguriert ein lokales Gateway oder eine Remote-Gateway-Verbindung sowie Channels, Skills
und Workspace-Standards in einem geführten Ablauf.

```bash
openclaw onboard
```

<Info>
Schnellster erster Chat: Öffne die Control UI (keine Channel-Einrichtung erforderlich). Führe
`openclaw dashboard` aus und chatte im Browser. Dokumentation: [Dashboard](/web/dashboard).
</Info>

Zum späteren Neukonfigurieren:

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
`--json` impliziert keinen nicht-interaktiven Modus. Verwende für Skripte `--non-interactive`.
</Note>

<Tip>
Das CLI-Onboarding enthält einen Websuch-Schritt, in dem du einen Provider
wie Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search,
Ollama Web Search, Perplexity, SearXNG oder Tavily auswählen kannst. Einige Provider erfordern einen
API-Schlüssel, andere nicht. Du kannst dies später auch mit
`openclaw configure --section web` konfigurieren. Dokumentation: [Web-Tools](/tools/web).
</Tip>

## QuickStart vs. Erweitert

Das Onboarding beginnt mit **QuickStart** (Standardeinstellungen) oder **Erweitert** (volle Kontrolle).

<Tabs>
  <Tab title="QuickStart (Standardeinstellungen)">
    - Lokales Gateway (loopback)
    - Workspace-Standard (oder bestehender Workspace)
    - Gateway-Port **18789**
    - Gateway-Authentifizierung **Token** (automatisch generiert, auch auf loopback)
    - Standard-Tool-Richtlinie für neue lokale Setups: `tools.profile: "coding"` (ein bestehendes explizites Profil bleibt erhalten)
    - Standard für DM-Isolierung: Lokales Onboarding schreibt `session.dmScope: "per-channel-peer"`, wenn nicht gesetzt. Details: [CLI Setup Reference](/start/wizard-cli-reference#outputs-and-internals)
    - Tailscale-Freigabe **Aus**
    - Telegram- und WhatsApp-DMs verwenden standardmäßig eine **Allowlist** (du wirst nach deiner Telefonnummer gefragt)
  </Tab>
  <Tab title="Erweitert (volle Kontrolle)">
    - Zeigt jeden Schritt an (Modus, Workspace, Gateway, Channels, Daemon, Skills).
  </Tab>
</Tabs>

## Was das Onboarding konfiguriert

**Lokaler Modus (Standard)** führt dich durch diese Schritte:

1. **Modell/Auth** — Wähle einen beliebigen unterstützten Provider-/Auth-Ablauf (API-Schlüssel, OAuth oder providerspezifische manuelle Authentifizierung), einschließlich Custom Provider
   (OpenAI-kompatibel, Anthropic-kompatibel oder Unknown Auto-Detect). Wähle ein Standardmodell.
   Sicherheitshinweis: Wenn dieser Agent Tools ausführen oder Inhalte aus Webhooks/Hooks verarbeiten soll, verwende bevorzugt das stärkste verfügbare Modell der neuesten Generation und halte die Tool-Richtlinie strikt. Schwächere/ältere Stufen sind leichter per Prompt Injection angreifbar.
   Bei nicht-interaktiven Ausführungen speichert `--secret-input-mode ref` umgebungsvariablenbasierte Referenzen in Auth-Profilen anstelle von API-Schlüsselwerten im Klartext.
   Im nicht-interaktiven `ref`-Modus muss die Provider-Umgebungsvariable gesetzt sein; das Übergeben von Inline-Key-Flags ohne diese Umgebungsvariable schlägt sofort fehl.
   In interaktiven Ausführungen kannst du durch Auswahl des Secret-Reference-Modus entweder auf eine Umgebungsvariable oder auf eine konfigurierte Provider-Referenz (`file` oder `exec`) verweisen, mit einer schnellen Vorabvalidierung vor dem Speichern.
   Für Anthropic bietet interaktives Onboarding/Konfigurieren **Anthropic Claude CLI** als lokalen Fallback und **Anthropic API key** als empfohlenen Produktionspfad. Anthropic setup-token ist außerdem wieder als Legacy-/manueller OpenClaw-Pfad verfügbar, mit der Anthropic-spezifischen Erwartung zur Abrechnung von **Extra Usage** für OpenClaw.
2. **Workspace** — Speicherort für Agent-Dateien (Standard `~/.openclaw/workspace`). Legt Bootstrap-Dateien an.
3. **Gateway** — Port, Bind-Adresse, Auth-Modus, Tailscale-Freigabe.
   Im interaktiven Token-Modus kannst du zwischen der standardmäßigen Klartext-Token-Speicherung wählen oder dich für SecretRef entscheiden.
   Nicht-interaktiver Token-SecretRef-Pfad: `--gateway-token-ref-env <ENV_VAR>`.
4. **Channels** — integrierte und gebündelte Chat-Channels wie BlueBubbles, Discord, Feishu, Google Chat, Mattermost, Microsoft Teams, QQ Bot, Signal, Slack, Telegram, WhatsApp und mehr.
5. **Daemon** — Installiert einen LaunchAgent (macOS), eine systemd-Benutzereinheit (Linux/WSL2) oder eine native geplante Windows-Aufgabe mit benutzerspezifischem Startup-Ordner-Fallback.
   Wenn die Token-Authentifizierung ein Token erfordert und `gateway.auth.token` per SecretRef verwaltet wird, validiert die Daemon-Installation dieses, speichert das aufgelöste Token jedoch nicht in den Umgebungsmetadaten des Supervisor-Dienstes.
   Wenn die Token-Authentifizierung ein Token erfordert und die konfigurierte Token-SecretRef nicht aufgelöst werden kann, wird die Daemon-Installation mit konkreten Hinweisen blockiert.
   Wenn sowohl `gateway.auth.token` als auch `gateway.auth.password` konfiguriert sind und `gateway.auth.mode` nicht gesetzt ist, wird die Daemon-Installation blockiert, bis der Modus explizit gesetzt wird.
6. **Health check** — Startet das Gateway und überprüft, ob es läuft.
7. **Skills** — Installiert empfohlene Skills und optionale Abhängigkeiten.

<Note>
Ein erneutes Ausführen des Onboardings löscht **nichts**, es sei denn, du wählst ausdrücklich **Reset** (oder übergibst `--reset`).
CLI-`--reset` betrifft standardmäßig Konfiguration, Anmeldedaten und Sitzungen; verwende `--reset-scope full`, um den Workspace einzuschließen.
Wenn die Konfiguration ungültig ist oder Legacy-Schlüssel enthält, fordert dich das Onboarding zuerst auf, `openclaw doctor` auszuführen.
</Note>

**Remote-Modus** konfiguriert nur den lokalen Client für die Verbindung zu einem Gateway an einem anderen Ort.
Er installiert oder ändert **nichts** auf dem Remote-Host.

## Weiteren Agenten hinzufügen

Verwende `openclaw agents add <name>`, um einen separaten Agenten mit eigenem Workspace,
eigenen Sitzungen und eigenen Auth-Profilen zu erstellen. Das Ausführen ohne `--workspace` startet das Onboarding.

Was dabei gesetzt wird:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

Hinweise:

- Standard-Workspaces folgen dem Muster `~/.openclaw/workspace-<agentId>`.
- Füge `bindings` hinzu, um eingehende Nachrichten weiterzuleiten (das Onboarding kann das übernehmen).
- Nicht-interaktive Flags: `--model`, `--agent-dir`, `--bind`, `--non-interactive`.

## Vollständige Referenz

Für detaillierte schrittweise Aufschlüsselungen und Konfigurationsausgaben siehe
[CLI Setup Reference](/start/wizard-cli-reference).
Für nicht-interaktive Beispiele siehe [CLI Automation](/start/wizard-cli-automation).
Für die ausführlichere technische Referenz einschließlich RPC-Details siehe
[Onboarding Reference](/reference/wizard).

## Verwandte Dokumentation

- CLI-Befehlsreferenz: [`openclaw onboard`](/cli/onboard)
- Onboarding-Überblick: [Onboarding Overview](/start/onboarding-overview)
- macOS-App-Onboarding: [Onboarding](/start/onboarding)
- Ritual beim ersten Start eines Agenten: [Agent Bootstrapping](/start/bootstrapping)
