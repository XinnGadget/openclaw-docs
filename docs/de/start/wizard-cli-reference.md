---
read_when:
    - Sie benötigen detailliertes Verhalten für `openclaw onboard`
    - Sie debuggen Onboarding-Ergebnisse oder integrieren Onboarding-Clients
sidebarTitle: CLI reference
summary: Vollständige Referenz für den CLI-Einrichtungsablauf, die Authentifizierungs-/Modell-Einrichtung, Ausgaben und Interna
title: CLI-Einrichtungsreferenz
x-i18n:
    generated_at: "2026-04-15T14:41:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 61ca679caca3b43fa02388294007f89db22d343e49e10b61d8d118cd8fbb7369
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# CLI-Einrichtungsreferenz

Diese Seite ist die vollständige Referenz für `openclaw onboard`.
Die Kurzfassung finden Sie unter [Onboarding (CLI)](/de/start/wizard).

## Was der Assistent macht

Der lokale Modus (Standard) führt Sie durch Folgendes:

- Modell- und Authentifizierungs-Einrichtung (OpenAI Code-Abonnement-OAuth, Anthropic Claude CLI oder API-Schlüssel sowie Optionen für MiniMax, GLM, Ollama, Moonshot, StepFun und AI Gateway)
- Workspace-Speicherort und Bootstrap-Dateien
- Gateway-Einstellungen (Port, Bind, Authentifizierung, Tailscale)
- Kanäle und Anbieter (Telegram, WhatsApp, Discord, Google Chat, Mattermost, Signal, BlueBubbles und andere gebündelte Kanal-Plugins)
- Daemon-Installation (LaunchAgent, `systemd`-Benutzereinheit oder native Windows-Aufgabe im Aufgabenplaner mit Fallback auf den Autostart-Ordner)
- Integritätsprüfung
- Skills-Einrichtung

Der Remote-Modus konfiguriert diesen Rechner für die Verbindung mit einem Gateway an einem anderen Ort.
Dabei wird auf dem Remote-Host nichts installiert oder geändert.

## Details zum lokalen Ablauf

<Steps>
  <Step title="Erkennung vorhandener Konfiguration">
    - Wenn `~/.openclaw/openclaw.json` vorhanden ist, wählen Sie Beibehalten, Ändern oder Zurücksetzen.
    - Das erneute Ausführen des Assistenten löscht nichts, außer Sie wählen ausdrücklich Zurücksetzen (oder übergeben `--reset`).
    - CLI-`--reset` verwendet standardmäßig `config+creds+sessions`; verwenden Sie `--reset-scope full`, um zusätzlich den Workspace zu entfernen.
    - Wenn die Konfiguration ungültig ist oder Legacy-Schlüssel enthält, stoppt der Assistent und fordert Sie auf, vor dem Fortfahren `openclaw doctor` auszuführen.
    - Beim Zurücksetzen wird `trash` verwendet und folgende Bereiche werden angeboten:
      - Nur Konfiguration
      - Konfiguration + Zugangsdaten + Sitzungen
      - Vollständiges Zurücksetzen (entfernt auch den Workspace)
  </Step>
  <Step title="Modell und Authentifizierung">
    - Die vollständige Optionsmatrix finden Sie unter [Auth- und Modelloptionen](#auth-und-modelloptionen).
  </Step>
  <Step title="Workspace">
    - Standard `~/.openclaw/workspace` (konfigurierbar).
    - Legt die für das Bootstrap-Ritual beim ersten Start benötigten Workspace-Dateien an.
    - Workspace-Layout: [Agent-Workspace](/de/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Fragt Port, Bind, Authentifizierungsmodus und Tailscale-Freigabe ab.
    - Empfohlen: Token-Authentifizierung auch bei local loopback aktiviert lassen, damit lokale WS-Clients sich authentifizieren müssen.
    - Im Token-Modus bietet die interaktive Einrichtung:
      - **Klartext-Token generieren/speichern** (Standard)
      - **SecretRef verwenden** (Opt-in)
    - Im Passwortmodus unterstützt die interaktive Einrichtung ebenfalls die Speicherung als Klartext oder SecretRef.
    - Nicht interaktiver Token-SecretRef-Pfad: `--gateway-token-ref-env <ENV_VAR>`.
      - Erfordert eine nicht leere Umgebungsvariable in der Onboarding-Prozessumgebung.
      - Kann nicht mit `--gateway-token` kombiniert werden.
    - Deaktivieren Sie die Authentifizierung nur, wenn Sie jedem lokalen Prozess vollständig vertrauen.
    - Nicht-loopback-Binds erfordern weiterhin Authentifizierung.
  </Step>
  <Step title="Kanäle">
    - [WhatsApp](/de/channels/whatsapp): optionale QR-Anmeldung
    - [Telegram](/de/channels/telegram): Bot-Token
    - [Discord](/de/channels/discord): Bot-Token
    - [Google Chat](/de/channels/googlechat): JSON des Dienstkontos + Webhook-Audience
    - [Mattermost](/de/channels/mattermost): Bot-Token + Basis-URL
    - [Signal](/de/channels/signal): optionale `signal-cli`-Installation + Kontokonfiguration
    - [BlueBubbles](/de/channels/bluebubbles): empfohlen für iMessage; Server-URL + Passwort + Webhook
    - [iMessage](/de/channels/imessage): Legacy-`imsg`-CLI-Pfad + DB-Zugriff
    - Sicherheit bei Direktnachrichten: Standard ist Pairing. Die erste Direktnachricht sendet einen Code; bestätigen Sie ihn mit
      `openclaw pairing approve <channel> <code>` oder verwenden Sie Zulassungslisten.
  </Step>
  <Step title="Daemon-Installation">
    - macOS: LaunchAgent
      - Erfordert eine angemeldete Benutzersitzung; für Headless-Betrieb verwenden Sie einen benutzerdefinierten LaunchDaemon (wird nicht mitgeliefert).
    - Linux und Windows über WSL2: `systemd`-Benutzereinheit
      - Der Assistent versucht `loginctl enable-linger <user>`, damit das Gateway nach dem Abmelden weiterläuft.
      - Möglicherweise wird nach sudo gefragt (schreibt nach `/var/lib/systemd/linger`); zunächst wird es ohne sudo versucht.
    - Natives Windows: zuerst Aufgabe im Aufgabenplaner
      - Wenn das Erstellen der Aufgabe verweigert wird, weicht OpenClaw auf ein benutzerspezifisches Anmeldeobjekt im Autostart-Ordner aus und startet das Gateway sofort.
      - Aufgaben im Aufgabenplaner bleiben bevorzugt, weil sie einen besseren Supervisor-Status bieten.
    - Laufzeitauswahl: Node (empfohlen; erforderlich für WhatsApp und Telegram). Bun wird nicht empfohlen.
  </Step>
  <Step title="Integritätsprüfung">
    - Startet das Gateway (falls nötig) und führt `openclaw health` aus.
    - `openclaw status --deep` ergänzt die Statusausgabe um die Live-Gateway-Integritätsprüfung, einschließlich Kanalprüfungen, wenn unterstützt.
  </Step>
  <Step title="Skills">
    - Liest verfügbare Skills und prüft Anforderungen.
    - Ermöglicht die Auswahl des Node-Managers: npm, pnpm oder bun.
    - Installiert optionale Abhängigkeiten (einige verwenden Homebrew auf macOS).
  </Step>
  <Step title="Abschluss">
    - Zusammenfassung und nächste Schritte, einschließlich Optionen für iOS-, Android- und macOS-Apps.
  </Step>
</Steps>

<Note>
Wenn keine GUI erkannt wird, gibt der Assistent SSH-Portweiterleitungsanweisungen für die Control UI aus, anstatt einen Browser zu öffnen.
Wenn Assets für die Control UI fehlen, versucht der Assistent, sie zu bauen; als Fallback dient `pnpm ui:build` (installiert UI-Abhängigkeiten automatisch).
</Note>

## Details zum Remote-Modus

Der Remote-Modus konfiguriert diesen Rechner für die Verbindung mit einem Gateway an einem anderen Ort.

<Info>
Im Remote-Modus wird auf dem Remote-Host nichts installiert oder geändert.
</Info>

Was Sie festlegen:

- URL des Remote-Gateways (`ws://...`)
- Token, falls für die Remote-Gateway-Authentifizierung erforderlich (empfohlen)

<Note>
- Wenn das Gateway nur auf loopback lauscht, verwenden Sie SSH-Tunneling oder ein Tailnet.
- Hinweise zur Erkennung:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## Auth- und Modelloptionen

<AccordionGroup>
  <Accordion title="Anthropic-API-Schlüssel">
    Verwendet `ANTHROPIC_API_KEY`, falls vorhanden, oder fordert zur Eingabe eines Schlüssels auf und speichert ihn anschließend für die Daemon-Nutzung.
  </Accordion>
  <Accordion title="OpenAI Code-Abonnement (Wiederverwendung von Codex CLI)">
    Wenn `~/.codex/auth.json` vorhanden ist, kann der Assistent es wiederverwenden.
    Wiederverwendete Codex CLI-Zugangsdaten bleiben von Codex CLI verwaltet; bei Ablauf liest OpenClaw
    zuerst erneut diese Quelle und schreibt, wenn der Anbieter sie aktualisieren kann, die
    aktualisierten Zugangsdaten zurück in den Codex-Speicher, anstatt
    selbst die Verwaltung zu übernehmen.
  </Accordion>
  <Accordion title="OpenAI Code-Abonnement (OAuth)">
    Browser-Ablauf; fügen Sie `code#state` ein.

    Setzt `agents.defaults.model` auf `openai-codex/gpt-5.4`, wenn kein Modell gesetzt ist oder `openai/*` verwendet wird.

  </Accordion>
  <Accordion title="OpenAI-API-Schlüssel">
    Verwendet `OPENAI_API_KEY`, falls vorhanden, oder fordert zur Eingabe eines Schlüssels auf und speichert die Zugangsdaten dann in Auth-Profilen.

    Setzt `agents.defaults.model` auf `openai/gpt-5.4`, wenn kein Modell gesetzt ist, `openai/*` oder `openai-codex/*` verwendet wird.

  </Accordion>
  <Accordion title="xAI (Grok)-API-Schlüssel">
    Fordert `XAI_API_KEY` an und konfiguriert xAI als Modellanbieter.
  </Accordion>
  <Accordion title="OpenCode">
    Fordert `OPENCODE_API_KEY` (oder `OPENCODE_ZEN_API_KEY`) an und lässt Sie zwischen dem Zen- oder Go-Katalog wählen.
    Einrichtungs-URL: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="API-Schlüssel (generisch)">
    Speichert den Schlüssel für Sie.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    Fordert `AI_GATEWAY_API_KEY` an.
    Weitere Details: [Vercel AI Gateway](/de/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    Fordert Konto-ID, Gateway-ID und `CLOUDFLARE_AI_GATEWAY_API_KEY` an.
    Weitere Details: [Cloudflare AI Gateway](/de/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax">
    Die Konfiguration wird automatisch geschrieben. Der gehostete Standardwert ist `MiniMax-M2.7`; bei der Einrichtung mit API-Schlüssel wird
    `minimax/...` verwendet, und bei OAuth-Einrichtung `minimax-portal/...`.
    Weitere Details: [MiniMax](/de/providers/minimax).
  </Accordion>
  <Accordion title="StepFun">
    Die Konfiguration wird automatisch für StepFun Standard oder Step Plan auf chinesischen oder globalen Endpunkten geschrieben.
    Standard umfasst derzeit `step-3.5-flash`, und Step Plan umfasst außerdem `step-3.5-flash-2603`.
    Weitere Details: [StepFun](/de/providers/stepfun).
  </Accordion>
  <Accordion title="Synthetic (Anthropic-kompatibel)">
    Fordert `SYNTHETIC_API_KEY` an.
    Weitere Details: [Synthetic](/de/providers/synthetic).
  </Accordion>
  <Accordion title="Ollama (Cloud- und lokale offene Modelle)">
    Fordert zuerst `Cloud + Local`, `Cloud only` oder `Local only` an.
    `Cloud only` verwendet `OLLAMA_API_KEY` mit `https://ollama.com`.
    Die hostgestützten Modi fragen nach der Basis-URL (Standard `http://127.0.0.1:11434`), erkennen verfügbare Modelle und schlagen Standardwerte vor.
    `Cloud + Local` prüft außerdem, ob dieser Ollama-Host für den Cloud-Zugriff angemeldet ist.
    Weitere Details: [Ollama](/de/providers/ollama).
  </Accordion>
  <Accordion title="Moonshot und Kimi Coding">
    Konfigurationen für Moonshot (Kimi K2) und Kimi Coding werden automatisch geschrieben.
    Weitere Details: [Moonshot AI (Kimi + Kimi Coding)](/de/providers/moonshot).
  </Accordion>
  <Accordion title="Benutzerdefinierter Anbieter">
    Funktioniert mit OpenAI-kompatiblen und Anthropic-kompatiblen Endpunkten.

    Das interaktive Onboarding unterstützt dieselben Speicheroptionen für API-Schlüssel wie andere API-Schlüssel-Abläufe von Anbietern:
    - **API-Schlüssel jetzt einfügen** (Klartext)
    - **Geheimnisreferenz verwenden** (Umgebungsreferenz oder konfigurierte Anbieterreferenz, mit Vorabvalidierung)

    Nicht interaktive Flags:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key` (optional; greift auf `CUSTOM_API_KEY` zurück)
    - `--custom-provider-id` (optional)
    - `--custom-compatibility <openai|anthropic>` (optional; Standard `openai`)

  </Accordion>
  <Accordion title="Überspringen">
    Lässt die Authentifizierung unkonfiguriert.
  </Accordion>
</AccordionGroup>

Modellverhalten:

- Wählen Sie das Standardmodell aus den erkannten Optionen aus oder geben Sie Anbieter und Modell manuell ein.
- Wenn das Onboarding mit einer Anbieter-Authentifizierungsoption beginnt, bevorzugt die Modellauswahl
  diesen Anbieter automatisch. Bei Volcengine und BytePlus passt dieselbe Präferenz
  außerdem zu ihren Coding-Plan-Varianten (`volcengine-plan/*`,
  `byteplus-plan/*`).
- Wenn dieser Filter für den bevorzugten Anbieter leer wäre, fällt die Auswahl auf
  den vollständigen Katalog zurück, anstatt keine Modelle anzuzeigen.
- Der Assistent führt eine Modellprüfung aus und warnt, wenn das konfigurierte Modell unbekannt ist oder die Authentifizierung fehlt.

Pfade für Zugangsdaten und Profile:

- Auth-Profile (API-Schlüssel + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Legacy-OAuth-Import: `~/.openclaw/credentials/oauth.json`

Speichermodus für Zugangsdaten:

- Das Standardverhalten im Onboarding speichert API-Schlüssel als Klartextwerte in Auth-Profilen.
- `--secret-input-mode ref` aktiviert den Referenzmodus anstelle der Speicherung von Schlüsseln im Klartext.
  In der interaktiven Einrichtung können Sie Folgendes wählen:
  - Referenz auf Umgebungsvariable (zum Beispiel `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`)
  - konfigurierte Anbieterreferenz (`file` oder `exec`) mit Anbieteralias + ID
- Der interaktive Referenzmodus führt vor dem Speichern eine schnelle Vorabvalidierung aus.
  - Umgebungsreferenzen: validiert Variablennamen + nicht leeren Wert in der aktuellen Onboarding-Umgebung.
  - Anbieterreferenzen: validiert die Anbieterkonfiguration und löst die angeforderte ID auf.
  - Wenn die Vorabprüfung fehlschlägt, zeigt das Onboarding den Fehler an und lässt Sie es erneut versuchen.
- Im nicht interaktiven Modus ist `--secret-input-mode ref` nur umgebungsbasiert.
  - Setzen Sie die Anbieter-Umgebungsvariable in der Onboarding-Prozessumgebung.
  - Inline-Schlüssel-Flags (zum Beispiel `--openai-api-key`) erfordern, dass diese Umgebungsvariable gesetzt ist; andernfalls schlägt das Onboarding sofort fehl.
  - Für benutzerdefinierte Anbieter speichert der nicht interaktive `ref`-Modus `models.providers.<id>.apiKey` als `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`.
  - In diesem Fall für benutzerdefinierte Anbieter erfordert `--custom-api-key`, dass `CUSTOM_API_KEY` gesetzt ist; andernfalls schlägt das Onboarding sofort fehl.
- Gateway-Authentifizierungsdaten unterstützen in der interaktiven Einrichtung Klartext- und SecretRef-Optionen:
  - Token-Modus: **Klartext-Token generieren/speichern** (Standard) oder **SecretRef verwenden**.
  - Passwortmodus: Klartext oder SecretRef.
- Nicht interaktiver Token-SecretRef-Pfad: `--gateway-token-ref-env <ENV_VAR>`.
- Bestehende Klartext-Konfigurationen funktionieren unverändert weiter.

<Note>
Tipp für Headless- und Server-Umgebungen: Schließen Sie OAuth auf einem Rechner mit Browser ab und kopieren Sie dann die `auth-profiles.json` dieses Agents (zum Beispiel
`~/.openclaw/agents/<agentId>/agent/auth-profiles.json` oder den entsprechenden
Pfad unter `$OPENCLAW_STATE_DIR/...`) auf den Gateway-Host. `credentials/oauth.json`
ist nur eine Legacy-Importquelle.
</Note>

## Ausgaben und Interna

Typische Felder in `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (wenn Minimax ausgewählt wurde)
- `tools.profile` (lokales Onboarding setzt standardmäßig `"coding"`, wenn kein Wert gesetzt ist; vorhandene explizite Werte bleiben erhalten)
- `gateway.*` (Modus, Bind, Authentifizierung, Tailscale)
- `session.dmScope` (lokales Onboarding setzt dies standardmäßig auf `per-channel-peer`, wenn kein Wert gesetzt ist; vorhandene explizite Werte bleiben erhalten)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Kanal-Zulassungslisten (Slack, Discord, Matrix, Microsoft Teams), wenn Sie dies während der Eingabeaufforderungen aktivieren (Namen werden nach Möglichkeit in IDs aufgelöst)
- `skills.install.nodeManager`
  - Das Flag `setup --node-manager` akzeptiert `npm`, `pnpm` oder `bun`.
  - Die manuelle Konfiguration kann später weiterhin `skills.install.nodeManager: "yarn"` setzen.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` schreibt `agents.list[]` und optionale `bindings`.

WhatsApp-Zugangsdaten werden unter `~/.openclaw/credentials/whatsapp/<accountId>/` gespeichert.
Sitzungen werden unter `~/.openclaw/agents/<agentId>/sessions/` gespeichert.

<Note>
Einige Kanäle werden als Plugins bereitgestellt. Wenn sie während der Einrichtung ausgewählt werden, fordert der Assistent Sie auf, das Plugin (npm oder lokaler Pfad) vor der Kanalkonfiguration zu installieren.
</Note>

Gateway-Assistent-RPC:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

Clients (macOS-App und Control UI) können Schritte rendern, ohne die Onboarding-Logik erneut implementieren zu müssen.

Verhalten bei der Signal-Einrichtung:

- Lädt das passende Release-Asset herunter
- Speichert es unter `~/.openclaw/tools/signal-cli/<version>/`
- Schreibt `channels.signal.cliPath` in die Konfiguration
- JVM-Builds erfordern Java 21
- Native Builds werden verwendet, wenn verfügbar
- Windows verwendet WSL2 und folgt dem Linux-`signal-cli`-Ablauf innerhalb von WSL

## Zugehörige Dokumente

- Onboarding-Hub: [Onboarding (CLI)](/de/start/wizard)
- Automatisierung und Skripte: [CLI-Automatisierung](/de/start/wizard-cli-automation)
- Befehlsreferenz: [`openclaw onboard`](/cli/onboard)
