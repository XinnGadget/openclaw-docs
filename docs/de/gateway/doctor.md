---
read_when:
    - Sie fügen Doctor-Migrationen hinzu oder ändern sie
    - Sie führen nicht abwärtskompatible Konfigurationsänderungen ein
summary: 'Doctor-Befehl: Integritätsprüfungen, Konfigurationsmigrationen und Reparaturschritte'
title: Doctor
x-i18n:
    generated_at: "2026-04-09T01:29:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 75d321bd1ad0e16c29f2382e249c51edfc3a8d33b55bdceea39e7dbcd4901fce
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor` ist das Reparatur- und Migrationstool für OpenClaw. Es behebt veraltete
Konfigurationen/Zustände, prüft die Integrität und bietet umsetzbare Reparaturschritte.

## Schnellstart

```bash
openclaw doctor
```

### Headless / Automatisierung

```bash
openclaw doctor --yes
```

Akzeptiert Standardwerte ohne Rückfrage (einschließlich Neustart-/Service-/Sandbox-Reparaturschritten, falls zutreffend).

```bash
openclaw doctor --repair
```

Wendet empfohlene Reparaturen ohne Rückfrage an (Reparaturen + Neustarts, wo sicher).

```bash
openclaw doctor --repair --force
```

Wendet auch aggressive Reparaturen an (überschreibt benutzerdefinierte Supervisor-Konfigurationen).

```bash
openclaw doctor --non-interactive
```

Wird ohne Rückfragen ausgeführt und wendet nur sichere Migrationen an (Konfigurationsnormalisierung + Verschieben von On-Disk-Zuständen). Überspringt Neustart-/Service-/Sandbox-Aktionen, die eine menschliche Bestätigung erfordern.
Legacy-Zustandsmigrationen werden bei Erkennung automatisch ausgeführt.

```bash
openclaw doctor --deep
```

Durchsucht Systemdienste nach zusätzlichen Gateway-Installationen (launchd/systemd/schtasks).

Wenn Sie Änderungen vor dem Schreiben prüfen möchten, öffnen Sie zuerst die Konfigurationsdatei:

```bash
cat ~/.openclaw/openclaw.json
```

## Was es tut (Zusammenfassung)

- Optionale Vorab-Aktualisierung für Git-Installationen (nur interaktiv).
- Prüfung der Aktualität des UI-Protokolls (erstellt die Control UI neu, wenn das Protokollschema neuer ist).
- Integritätsprüfung + Neustartaufforderung.
- Skills-Statuszusammenfassung (geeignet/fehlend/blockiert) und Plugin-Status.
- Konfigurationsnormalisierung für Legacy-Werte.
- Migration der Talk-Konfiguration von alten flachen `talk.*`-Feldern nach `talk.provider` + `talk.providers.<provider>`.
- Browser-Migrationsprüfungen für alte Chrome-Erweiterungskonfigurationen und Chrome-MCP-Bereitschaft.
- Warnungen zu OpenCode-Provider-Overrides (`models.providers.opencode` / `models.providers.opencode-go`).
- Warnungen zu Codex-OAuth-Überschattung (`models.providers.openai-codex`).
- Prüfung der OAuth-TLS-Voraussetzungen für OpenAI-Codex-OAuth-Profile.
- Legacy-Migration von On-Disk-Zuständen (Sitzungen/Agent-Verzeichnis/WhatsApp-Authentifizierung).
- Migration von Legacy-Schlüsseln für Plugin-Manifestverträge (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- Migration des Legacy-Cron-Speichers (`jobId`, `schedule.cron`, Delivery-/Payload-Felder auf oberster Ebene, Payload-`provider`, einfache Fallback-Jobs für Webhooks mit `notify: true`).
- Prüfung von Sitzungs-Sperrdateien und Bereinigung veralteter Sperren.
- Prüfungen auf Zustandsintegrität und Berechtigungen (Sitzungen, Abschriften, Zustandsverzeichnis).
- Prüfungen der Konfigurationsdateiberechtigungen (`chmod 600`) bei lokaler Ausführung.
- Integrität der Modell-Authentifizierung: prüft OAuth-Ablauf, kann ablaufende Tokens aktualisieren und meldet Abklingzeiten/deaktivierte Zustände von Auth-Profilen.
- Erkennung zusätzlicher Workspace-Verzeichnisse (`~/openclaw`).
- Reparatur von Sandbox-Images, wenn Sandboxing aktiviert ist.
- Legacy-Servicemigration und Erkennung zusätzlicher Gateways.
- Migration von Legacy-Zuständen für den Matrix-Kanal (im Modus `--fix` / `--repair`).
- Laufzeitprüfungen des Gateways (Dienst installiert, aber nicht aktiv; zwischengespeichertes launchd-Label).
- Warnungen zum Kanalstatus (vom laufenden Gateway geprüft).
- Audit der Supervisor-Konfiguration (launchd/systemd/schtasks) mit optionaler Reparatur.
- Prüfungen bewährter Laufzeitpraktiken für das Gateway (Node vs Bun, Pfade von Versionsmanagern).
- Diagnose von Gateway-Portkonflikten (Standard `18789`).
- Sicherheitswarnungen bei offenen DM-Richtlinien.
- Prüfungen der Gateway-Authentifizierung für den lokalen Token-Modus (bietet Tokenerzeugung an, wenn keine Tokenquelle vorhanden ist; überschreibt keine SecretRef-Token-Konfigurationen).
- Prüfung von `systemd linger` unter Linux.
- Prüfung der Dateigröße von Workspace-Bootstrap-Dateien (Warnungen bei Abschneidung/nahe am Limit für Kontextdateien).
- Prüfung des Shell-Completion-Status und automatische Installation/Aktualisierung.
- Bereitschaftsprüfung für den Embedding-Provider der Speichersuche (lokales Modell, API-Schlüssel für Remote-Anbieter oder QMD-Binary).
- Prüfungen für Source-Installationen (Nichtübereinstimmung des pnpm-Workspaces, fehlende UI-Assets, fehlende `tsx`-Binärdatei).
- Schreibt aktualisierte Konfiguration + Wizard-Metadaten.

## Dreams-UI-Backfill und -Zurücksetzen

Die Dreams-Ansicht der Control UI enthält die Aktionen **Backfill**, **Reset** und **Clear Grounded**
für den fundierten Träumen-Workflow. Diese Aktionen verwenden Gateway-RPC-Methoden
im Doctor-Stil, sind aber **nicht** Teil der CLI-Reparatur-/Migrationsfunktion von `openclaw doctor`.

Was sie tun:

- **Backfill** durchsucht historische `memory/YYYY-MM-DD.md`-Dateien im aktiven
  Workspace, führt den fundierten REM-Tagebuchdurchlauf aus und schreibt reversible Backfill-Einträge in `DREAMS.md`.
- **Reset** entfernt nur die markierten Backfill-Tagebucheinträge aus `DREAMS.md`.
- **Clear Grounded** entfernt nur bereitgestellte, ausschließlich fundierte kurzfristige Einträge, die
  aus historischem Replay stammen und noch keine Unterstützung durch aktiven Recall oder tägliche
  Einträge gesammelt haben.

Was sie für sich genommen **nicht** tun:

- sie bearbeiten nicht `MEMORY.md`
- sie führen keine vollständigen Doctor-Migrationen aus
- sie stellen fundierte Kandidaten nicht automatisch in den aktiven kurzfristigen
  Promotionsspeicher ein, es sei denn, Sie führen zuerst ausdrücklich den vorbereitenden CLI-Pfad aus

Wenn Sie möchten, dass fundiertes historisches Replay den normalen Deep-Promotionspfad
beeinflusst, verwenden Sie stattdessen den CLI-Ablauf:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

Dadurch werden fundierte dauerhafte Kandidaten in den kurzfristigen Träumen-Speicher eingestellt, während
`DREAMS.md` als Prüfoberfläche erhalten bleibt.

## Detailliertes Verhalten und Begründung

### 0) Optionale Aktualisierung (Git-Installationen)

Wenn dies ein Git-Checkout ist und Doctor interaktiv ausgeführt wird, bietet es an,
vor der Ausführung von Doctor zu aktualisieren (fetch/rebase/build).

### 1) Konfigurationsnormalisierung

Wenn die Konfiguration alte Werteformen enthält (zum Beispiel `messages.ackReaction`
ohne kanalspezifisches Override), normalisiert Doctor sie auf das aktuelle
Schema.

Dazu gehören auch alte flache Talk-Felder. Die aktuelle öffentliche Talk-Konfiguration ist
`talk.provider` + `talk.providers.<provider>`. Doctor schreibt alte
Formen von `talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` in die Provider-Map um.

### 2) Migrationen von Legacy-Konfigurationsschlüsseln

Wenn die Konfiguration veraltete Schlüssel enthält, verweigern andere Befehle die Ausführung und fordern
Sie auf, `openclaw doctor` auszuführen.

Doctor wird:

- Erklären, welche Legacy-Schlüssel gefunden wurden.
- Die angewendete Migration anzeigen.
- `~/.openclaw/openclaw.json` mit dem aktualisierten Schema neu schreiben.

Das Gateway führt Doctor-Migrationen beim Start ebenfalls automatisch aus, wenn es ein
altes Konfigurationsformat erkennt, sodass veraltete Konfigurationen ohne manuelles Eingreifen repariert werden.
Migrationen des Cron-Job-Speichers werden von `openclaw doctor --fix` verarbeitet.

Aktuelle Migrationen:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → oberstes `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- altes `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `messages.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `messages.tts.providers.<provider>`
- `channels.discord.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.voice.tts.providers.<provider>`
- `channels.discord.accounts.<id>.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.accounts.<id>.voice.tts.providers.<provider>`
- `plugins.entries.voice-call.config.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `plugins.entries.voice-call.config.tts.providers.<provider>`
- `plugins.entries.voice-call.config.provider: "log"` → `"mock"`
- `plugins.entries.voice-call.config.twilio.from` → `plugins.entries.voice-call.config.fromNumber`
- `plugins.entries.voice-call.config.streaming.sttProvider` → `plugins.entries.voice-call.config.streaming.provider`
- `plugins.entries.voice-call.config.streaming.openaiApiKey|sttModel|silenceDurationMs|vadThreshold`
  → `plugins.entries.voice-call.config.streaming.providers.openai.*`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- Bei Kanälen mit benannten `accounts`, aber verbliebenen einkonto-spezifischen Kanalwerten auf oberster Ebene, diese kontobezogenen Werte in das für diesen Kanal ausgewählte hochgestufte Konto verschieben (`accounts.default` für die meisten Kanäle; Matrix kann ein vorhandenes passendes benanntes/Standardziel beibehalten)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- `browser.relayBindHost` entfernen (alte Relay-Einstellung der Erweiterung)

Doctor-Warnungen enthalten auch Hinweise zu Standardkonten für Mehrkonten-Kanäle:

- Wenn zwei oder mehr `channels.<channel>.accounts`-Einträge konfiguriert sind, ohne `channels.<channel>.defaultAccount` oder `accounts.default`, warnt Doctor davor, dass Fallback-Routing ein unerwartetes Konto auswählen kann.
- Wenn `channels.<channel>.defaultAccount` auf eine unbekannte Konto-ID gesetzt ist, warnt Doctor und listet die konfigurierten Konto-IDs auf.

### 2b) OpenCode-Provider-Overrides

Wenn Sie `models.providers.opencode`, `opencode-zen` oder `opencode-go`
manuell hinzugefügt haben, überschreibt dies den integrierten OpenCode-Katalog aus `@mariozechner/pi-ai`.
Das kann Modelle auf die falsche API zwingen oder Kosten auf null setzen. Doctor warnt Sie, damit Sie
das Override entfernen und das API-Routing plus die Kosten pro Modell wiederherstellen können.

### 2c) Browser-Migration und Chrome-MCP-Bereitschaft

Wenn Ihre Browser-Konfiguration noch auf den entfernten Pfad der Chrome-Erweiterung verweist, normalisiert Doctor
sie auf das aktuelle host-lokale Chrome-MCP-Attach-Modell:

- `browser.profiles.*.driver: "extension"` wird zu `"existing-session"`
- `browser.relayBindHost` wird entfernt

Doctor prüft außerdem den host-lokalen Chrome-MCP-Pfad, wenn Sie `defaultProfile:
"user"` oder ein konfiguriertes `existing-session`-Profil verwenden:

- prüft, ob Google Chrome auf demselben Host für Standardprofile mit
  automatischer Verbindung installiert ist
- prüft die erkannte Chrome-Version und warnt, wenn sie unter Chrome 144 liegt
- erinnert daran, Remote-Debugging auf der Browser-Inspect-Seite zu aktivieren (zum
  Beispiel `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`
  oder `edge://inspect/#remote-debugging`)

Doctor kann die Chrome-seitige Einstellung nicht für Sie aktivieren. Host-lokales Chrome MCP
erfordert weiterhin:

- einen Chromium-basierten Browser 144+ auf dem Gateway-/Knoten-Host
- den lokal laufenden Browser
- aktiviertes Remote-Debugging in diesem Browser
- die Bestätigung der ersten Attach-Zustimmungsaufforderung im Browser

Bereitschaft bezieht sich hier nur auf lokale Voraussetzungen für das Attach. Existing-session behält
die aktuellen Routenbeschränkungen von Chrome MCP bei; erweiterte Routen wie `responsebody`, PDF-
Export, Download-Interception und Batch-Aktionen erfordern weiterhin einen verwalteten
Browser oder ein Roh-CDP-Profil.

Diese Prüfung gilt **nicht** für Docker-, Sandbox-, Remote-Browser- oder andere
headless Abläufe. Diese verwenden weiterhin Roh-CDP.

### 2d) OAuth-TLS-Voraussetzungen

Wenn ein OpenAI-Codex-OAuth-Profil konfiguriert ist, prüft Doctor den OpenAI-
Autorisierungsendpunkt, um zu verifizieren, dass der lokale Node-/OpenSSL-TLS-Stack die
Zertifikatskette validieren kann. Wenn die Prüfung mit einem Zertifikatsfehler fehlschlägt (zum
Beispiel `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, abgelaufenes Zertifikat oder selbstsigniertes Zertifikat),
gibt Doctor plattformspezifische Lösungshinweise aus. Auf macOS mit einem Homebrew-Node ist die
Lösung meist `brew postinstall ca-certificates`. Mit `--deep` wird die Prüfung auch dann ausgeführt,
wenn das Gateway in Ordnung ist.

### 2c) Codex-OAuth-Provider-Overrides

Wenn Sie zuvor alte OpenAI-Transporteinstellungen unter
`models.providers.openai-codex` hinzugefügt haben, können diese den integrierten Codex-OAuth-
Provider-Pfad überschatten, den neuere Releases automatisch verwenden. Doctor warnt, wenn diese
alten Transporteinstellungen zusammen mit Codex OAuth gefunden werden, damit Sie das veraltete
Transport-Override entfernen oder umschreiben und das integrierte Routing-/Fallback-Verhalten
wiederherstellen können. Benutzerdefinierte Proxys und reine Header-Overrides werden weiterhin unterstützt und lösen diese Warnung nicht aus.

### 3) Legacy-Zustandsmigrationen (Datenträgerlayout)

Doctor kann ältere Layouts auf dem Datenträger in die aktuelle Struktur migrieren:

- Sitzungsspeicher + Abschriften:
  - von `~/.openclaw/sessions/` nach `~/.openclaw/agents/<agentId>/sessions/`
- Agent-Verzeichnis:
  - von `~/.openclaw/agent/` nach `~/.openclaw/agents/<agentId>/agent/`
- WhatsApp-Authentifizierungszustand (Baileys):
  - von altem `~/.openclaw/credentials/*.json` (außer `oauth.json`)
  - nach `~/.openclaw/credentials/whatsapp/<accountId>/...` (Standard-Konto-ID: `default`)

Diese Migrationen erfolgen nach bestem Bemühen und sind idempotent; Doctor gibt Warnungen aus, wenn
Legacy-Ordner als Sicherungen zurückbleiben. Gateway/CLI migrieren außerdem die alten
Sitzungen + das Agent-Verzeichnis beim Start automatisch, sodass Verlauf/Auth/Modelle ohne
manuelle Doctor-Ausführung im pfad pro Agent landen. Die WhatsApp-Authentifizierung wird absichtlich nur
über `openclaw doctor` migriert. Die Normalisierung von Talk-Provider/Provider-Map vergleicht nun
nach struktureller Gleichheit, sodass Unterschiede nur in der Schlüsselreihenfolge keine
wiederholten No-op-Änderungen von `doctor --fix` mehr auslösen.

### 3a) Legacy-Migrationen von Plugin-Manifesten

Doctor durchsucht alle installierten Plugin-Manifeste nach veralteten Capability-
Schlüsseln auf oberster Ebene (`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`). Wenn sie gefunden werden, bietet es an, sie in das Objekt `contracts`
zu verschieben und die Manifestdatei direkt zu überschreiben. Diese Migration ist idempotent;
wenn der Schlüssel `contracts` bereits dieselben Werte enthält, wird der alte Schlüssel entfernt,
ohne die Daten zu duplizieren.

### 3b) Legacy-Migrationen des Cron-Speichers

Doctor prüft auch den Cron-Job-Speicher (`~/.openclaw/cron/jobs.json` standardmäßig,
oder `cron.store`, wenn überschrieben) auf alte Job-Formen, die der Scheduler aus
Kompatibilitätsgründen weiterhin akzeptiert.

Aktuelle Bereinigungen für Cron umfassen:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- Payload-Felder auf oberster Ebene (`message`, `model`, `thinking`, ...) → `payload`
- Delivery-Felder auf oberster Ebene (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- Delivery-Aliasse für Payload-`provider` → explizites `delivery.channel`
- einfache alte Fallback-Jobs für Webhooks mit `notify: true` → explizites `delivery.mode="webhook"` mit `delivery.to=cron.webhook`

Doctor migriert Jobs mit `notify: true` nur dann automatisch, wenn dies ohne
Verhaltensänderung möglich ist. Wenn ein Job den alten Notify-Fallback mit einem vorhandenen
Nicht-Webhook-Delivery-Modus kombiniert, warnt Doctor und überlässt diesen Job der manuellen Prüfung.

### 3c) Bereinigung von Sitzungs-Sperren

Doctor durchsucht jedes Sitzungsverzeichnis eines Agenten nach veralteten Schreib-Sperrdateien — Dateien, die
zurückbleiben, wenn eine Sitzung abnormal beendet wurde. Für jede gefundene Sperrdatei meldet es:
den Pfad, die PID, ob die PID noch aktiv ist, das Alter der Sperre und ob sie
als veraltet gilt (tote PID oder älter als 30 Minuten). Im Modus `--fix` / `--repair`
entfernt es veraltete Sperrdateien automatisch; andernfalls wird ein Hinweis ausgegeben und
angewiesen, den Befehl mit `--fix` erneut auszuführen.

### 4) Prüfungen der Zustandsintegrität (Sitzungspersistenz, Routing und Sicherheit)

Das Zustandsverzeichnis ist das operative Stammhirn. Wenn es verschwindet, verlieren Sie
Sitzungen, Anmeldedaten, Logs und Konfigurationen (außer Sie haben anderswo Sicherungen).

Doctor prüft:

- **Fehlendes Zustandsverzeichnis**: warnt vor katastrophalem Zustandsverlust, fordert zur Neuerstellung
  des Verzeichnisses auf und erinnert daran, dass fehlende Daten nicht wiederhergestellt werden können.
- **Berechtigungen des Zustandsverzeichnisses**: prüft Schreibbarkeit; bietet an, Berechtigungen zu reparieren
  (und gibt einen `chown`-Hinweis aus, wenn eine Nichtübereinstimmung bei Eigentümer/Gruppe erkannt wird).
- **Cloud-synchronisiertes Zustandsverzeichnis unter macOS**: warnt, wenn sich der Zustand unter iCloud Drive
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) oder
  `~/Library/CloudStorage/...` befindet, da synchronisierte Pfade langsamere I/O-
  Vorgänge und Sperr-/Synchronisierungsrennen verursachen können.
- **SD- oder eMMC-Zustandsverzeichnis unter Linux**: warnt, wenn sich der Zustand auf einer `mmcblk*`-
  Mount-Quelle befindet, da zufällige I/O auf SD- oder eMMC-Medien langsamer sein und
  bei Sitzungs- und Credential-Schreibvorgängen schneller verschleißen kann.
- **Fehlende Sitzungsverzeichnisse**: `sessions/` und das Sitzungsverzeichnis sind
  erforderlich, um Verlauf zu speichern und `ENOENT`-Abstürze zu vermeiden.
- **Nichtübereinstimmung von Abschriften**: warnt, wenn bei aktuellen Sitzungseinträgen
  Abschriftdateien fehlen.
- **Hauptsitzung „1-zeiliges JSONL“**: markiert, wenn die Hauptabschrift nur eine Zeile hat
  (Verlauf sammelt sich nicht an).
- **Mehrere Zustandsverzeichnisse**: warnt, wenn mehrere `~/.openclaw`-Ordner in
  Home-Verzeichnissen vorhanden sind oder wenn `OPENCLAW_STATE_DIR` auf einen anderen Ort zeigt (der Verlauf kann
  sich zwischen Installationen aufteilen).
- **Erinnerung an den Remote-Modus**: wenn `gateway.mode=remote`, erinnert Doctor daran, den Befehl
  auf dem Remote-Host auszuführen (dort liegt der Zustand).
- **Berechtigungen der Konfigurationsdatei**: warnt, wenn `~/.openclaw/openclaw.json`
  für Gruppe/Welt lesbar ist, und bietet an, auf `600` zu verschärfen.

### 5) Integrität der Modell-Authentifizierung (OAuth-Ablauf)

Doctor prüft OAuth-Profile im Auth-Speicher, warnt bei
ablaufenden/abgelaufenen Tokens und kann sie aktualisieren, wenn das sicher ist. Wenn das Anthropic-
OAuth-/Token-Profil veraltet ist, schlägt es einen Anthropic-API-Schlüssel oder den
Anthropic-Setup-Token-Pfad vor.
Aufforderungen zur Aktualisierung erscheinen nur bei interaktiver Ausführung (TTY); `--non-interactive`
überspringt Aktualisierungsversuche.

Wenn eine OAuth-Aktualisierung dauerhaft fehlschlägt (zum Beispiel `refresh_token_reused`,
`invalid_grant` oder ein Provider mitteilt, dass Sie sich erneut anmelden müssen), meldet Doctor,
dass eine erneute Authentifizierung erforderlich ist, und gibt den exakten Befehl
`openclaw models auth login --provider ...` aus, der auszuführen ist.

Doctor meldet auch Auth-Profile, die vorübergehend nicht verwendbar sind aufgrund von:

- kurzen Abklingzeiten (Ratenbegrenzungen/Timeouts/Auth-Fehler)
- längeren Deaktivierungen (Abrechnungs-/Guthabenfehler)

### 6) Validierung des Hooks-Modells

Wenn `hooks.gmail.model` gesetzt ist, validiert Doctor den Modellverweis gegen den
Katalog und die Allowlist und warnt, wenn er nicht aufgelöst werden kann oder nicht erlaubt ist.

### 7) Reparatur von Sandbox-Images

Wenn Sandboxing aktiviert ist, prüft Doctor Docker-Images und bietet an, sie zu erstellen oder
zu alten Namen zu wechseln, falls das aktuelle Image fehlt.

### 7b) Laufzeitabhängigkeiten gebündelter Plugins

Doctor prüft, ob Laufzeitabhängigkeiten gebündelter Plugins (zum Beispiel die
Laufzeitpakete des Discord-Plugins) im OpenClaw-Installationsstamm vorhanden sind.
Wenn welche fehlen, meldet Doctor die Pakete und installiert sie im Modus
`openclaw doctor --fix` / `openclaw doctor --repair`.

### 8) Migrationen von Gateway-Diensten und Bereinigungshinweise

Doctor erkennt alte Gateway-Dienste (launchd/systemd/schtasks) und
bietet an, sie zu entfernen und den OpenClaw-Dienst mit dem aktuellen Gateway-Port zu installieren.
Es kann auch nach zusätzlichen gatewayähnlichen Diensten suchen und Bereinigungshinweise ausgeben.
Profilbenannte OpenClaw-Gateway-Dienste gelten als erstklassig und werden nicht
als „zusätzlich“ markiert.

### 8b) Startup-Matrix-Migration

Wenn für ein Matrix-Kanalkonto eine ausstehende oder durchführbare Legacy-Zustandsmigration vorliegt,
erstellt Doctor (im Modus `--fix` / `--repair`) einen Snapshot vor der Migration und
führt dann die Migrationsschritte nach bestem Bemühen aus: Legacy-Migration des Matrix-Zustands und Vorbereitung des alten
verschlüsselten Zustands. Beide Schritte sind nicht fatal; Fehler werden protokolliert und
der Start wird fortgesetzt. Im Nur-Lesen-Modus (`openclaw doctor` ohne `--fix`) wird diese Prüfung
vollständig übersprungen.

### 9) Sicherheitswarnungen

Doctor gibt Warnungen aus, wenn ein Provider für DMs ohne Allowlist offen ist oder
wenn eine Richtlinie gefährlich konfiguriert ist.

### 10) systemd linger (Linux)

Wenn die Ausführung als systemd-Benutzerdienst erfolgt, stellt Doctor sicher, dass Linger aktiviert ist, damit das
Gateway nach dem Abmelden aktiv bleibt.

### 11) Workspace-Status (Skills, Plugins und alte Verzeichnisse)

Doctor gibt eine Zusammenfassung des Workspace-Zustands für den Standard-Agenten aus:

- **Skills-Status**: Anzahl geeigneter, Anforderungen-fehlen- und Allowlist-blockierter Skills.
- **Alte Workspace-Verzeichnisse**: warnt, wenn `~/openclaw` oder andere alte Workspace-Verzeichnisse
  neben dem aktuellen Workspace vorhanden sind.
- **Plugin-Status**: zählt geladene/deaktivierte/fehlerhafte Plugins; listet Plugin-IDs für alle
  Fehler auf; meldet Fähigkeiten gebündelter Plugins.
- **Plugin-Kompatibilitätswarnungen**: markiert Plugins mit Kompatibilitätsproblemen mit
  der aktuellen Laufzeit.
- **Plugin-Diagnosen**: zeigt beim Laden ausgegebene Warnungen oder Fehler aus der
  Plugin-Registry an.

### 11b) Größe der Bootstrap-Datei

Doctor prüft, ob Bootstrap-Dateien des Workspace (zum Beispiel `AGENTS.md`,
`CLAUDE.md` oder andere injizierte Kontextdateien) nahe am oder über dem konfigurierten
Zeichenbudget liegen. Es meldet pro Datei rohe vs. injizierte Zeichenzahlen, den Abschneidungs-
Prozentsatz, die Ursache der Abschneidung (`max/file` oder `max/total`) und die gesamte Zahl injizierter
Zeichen als Anteil am Gesamtbudget. Wenn Dateien abgeschnitten werden oder nahe am
Limit liegen, gibt Doctor Tipps zur Anpassung von `agents.defaults.bootstrapMaxChars`
und `agents.defaults.bootstrapTotalMaxChars`.

### 11c) Shell-Completion

Doctor prüft, ob Tab-Completion für die aktuelle Shell installiert ist
(zsh, bash, fish oder PowerShell):

- Wenn das Shell-Profil ein langsames Muster für dynamische Completion verwendet
  (`source <(openclaw completion ...)`), aktualisiert Doctor es auf die schnellere
  Variante mit zwischengespeicherter Datei.
- Wenn Completion im Profil konfiguriert ist, aber die Cache-Datei fehlt,
  regeneriert Doctor den Cache automatisch.
- Wenn überhaupt keine Completion konfiguriert ist, fordert Doctor zur Installation auf
  (nur im interaktiven Modus; übersprungen mit `--non-interactive`).

Führen Sie `openclaw completion --write-state` aus, um den Cache manuell neu zu erzeugen.

### 12) Prüfungen der Gateway-Authentifizierung (lokaler Token)

Doctor prüft die Bereitschaft der lokalen Gateway-Token-Authentifizierung.

- Wenn der Token-Modus einen Token benötigt und keine Tokenquelle vorhanden ist, bietet Doctor an, einen zu erzeugen.
- Wenn `gateway.auth.token` per SecretRef verwaltet wird, aber nicht verfügbar ist, warnt Doctor und überschreibt ihn nicht mit Klartext.
- `openclaw doctor --generate-gateway-token` erzwingt eine Erzeugung nur dann, wenn kein Token-SecretRef konfiguriert ist.

### 12b) SecretRef-bewusste Reparaturen im Nur-Lesen-Modus

Einige Reparaturabläufe müssen konfigurierte Anmeldedaten prüfen, ohne das Laufzeitverhalten beim schnellen Fehlschlagen abzuschwächen.

- `openclaw doctor --fix` verwendet jetzt dasselbe schreibgeschützte SecretRef-Zusammenfassungsmodell wie Befehle der Statusfamilie für gezielte Konfigurationsreparaturen.
- Beispiel: Die Reparatur von Telegram-`allowFrom` / `groupAllowFrom` mit `@username` versucht, konfigurierte Bot-Anmeldedaten zu verwenden, wenn verfügbar.
- Wenn der Telegram-Bot-Token per SecretRef konfiguriert ist, aber im aktuellen Befehlsablauf nicht verfügbar ist, meldet Doctor, dass die Anmeldedaten konfiguriert, aber nicht verfügbar sind, und überspringt die automatische Auflösung, anstatt abzustürzen oder den Token fälschlich als fehlend zu melden.

### 13) Integritätsprüfung des Gateways + Neustart

Doctor führt eine Integritätsprüfung aus und bietet an, das Gateway neu zu starten, wenn es
ungesund wirkt.

### 13b) Bereitschaft der Speichersuche

Doctor prüft, ob der konfigurierte Embedding-Provider der Speichersuche für den
Standard-Agenten bereit ist. Das Verhalten hängt vom konfigurierten Backend und Provider ab:

- **QMD-Backend**: prüft, ob die `qmd`-Binärdatei verfügbar und startbar ist.
  Wenn nicht, werden Lösungshinweise ausgegeben, einschließlich des npm-Pakets und einer manuellen Binärpfadoption.
- **Expliziter lokaler Provider**: prüft auf eine lokale Modelldatei oder eine erkannte
  Remote-/herunterladbare Modell-URL. Wenn sie fehlt, wird vorgeschlagen, zu einem Remote-Provider zu wechseln.
- **Expliziter Remote-Provider** (`openai`, `voyage` usw.): prüft, ob ein API-Schlüssel
  in der Umgebung oder im Auth-Speicher vorhanden ist. Gibt umsetzbare Lösungshinweise aus, wenn er fehlt.
- **Auto-Provider**: prüft zuerst die Verfügbarkeit lokaler Modelle und versucht dann jeden Remote-
  Provider in der Auto-Auswahlreihenfolge.

Wenn ein Ergebnis einer Gateway-Prüfung verfügbar ist (das Gateway war zum Zeitpunkt der
Prüfung in Ordnung), vergleicht Doctor das Ergebnis mit der in der CLI sichtbaren Konfiguration und weist
auf etwaige Abweichungen hin.

Verwenden Sie `openclaw memory status --deep`, um die Embedding-Bereitschaft zur Laufzeit zu prüfen.

### 14) Warnungen zum Kanalstatus

Wenn das Gateway in Ordnung ist, führt Doctor eine Prüfung des Kanalstatus aus und meldet
Warnungen mit vorgeschlagenen Lösungen.

### 15) Audit der Supervisor-Konfiguration + Reparatur

Doctor prüft die installierte Supervisor-Konfiguration (launchd/systemd/schtasks) auf
fehlende oder veraltete Standardwerte (z. B. systemd-Abhängigkeiten von network-online und
Neustartverzögerung). Wenn es eine Nichtübereinstimmung findet, empfiehlt es eine Aktualisierung und kann
die Dienstdatei/Aufgabe auf die aktuellen Standardwerte umschreiben.

Hinweise:

- `openclaw doctor` fragt vor dem Umschreiben der Supervisor-Konfiguration nach.
- `openclaw doctor --yes` akzeptiert die Standard-Reparaturaufforderungen.
- `openclaw doctor --repair` wendet empfohlene Korrekturen ohne Rückfragen an.
- `openclaw doctor --repair --force` überschreibt benutzerdefinierte Supervisor-Konfigurationen.
- Wenn die Token-Authentifizierung einen Token erfordert und `gateway.auth.token` per SecretRef verwaltet wird, validiert die Dienstinstallation/-reparatur von Doctor den SecretRef, speichert aber keine aufgelösten Klartext-Tokenwerte in den Umgebungsmetadaten des Supervisor-Dienstes.
- Wenn die Token-Authentifizierung einen Token erfordert und der konfigurierte Token-SecretRef nicht aufgelöst werden kann, blockiert Doctor den Installations-/Reparaturpfad mit umsetzbaren Hinweisen.
- Wenn sowohl `gateway.auth.token` als auch `gateway.auth.password` konfiguriert sind und `gateway.auth.mode` nicht gesetzt ist, blockiert Doctor Installation/Reparatur, bis der Modus explizit gesetzt ist.
- Für Linux-User-systemd-Units umfassen Doctor-Prüfungen auf Token-Abweichungen jetzt sowohl `Environment=`- als auch `EnvironmentFile=`-Quellen beim Vergleich der Dienst-Auth-Metadaten.
- Sie können jederzeit ein vollständiges Umschreiben mit `openclaw gateway install --force` erzwingen.

### 16) Gateway-Laufzeit + Portdiagnose

Doctor prüft die Dienstlaufzeit (PID, letzter Exit-Status) und warnt, wenn der
Dienst installiert, aber nicht tatsächlich aktiv ist. Es prüft außerdem auf Portkonflikte
am Gateway-Port (Standard `18789`) und meldet wahrscheinliche Ursachen (Gateway läuft bereits,
SSH-Tunnel).

### 17) Bewährte Laufzeitpraktiken für das Gateway

Doctor warnt, wenn der Gateway-Dienst auf Bun oder einem versionsverwalteten Node-Pfad
(`nvm`, `fnm`, `volta`, `asdf` usw.) läuft. WhatsApp- und Telegram-Kanäle erfordern Node,
und Pfade von Versionsmanagern können nach Upgrades Probleme verursachen, weil der Dienst Ihre Shell-Initialisierung nicht
lädt. Doctor bietet an, auf eine System-Node-Installation zu migrieren, wenn
verfügbar (Homebrew/apt/choco).

### 18) Konfigurationsschreiben + Wizard-Metadaten

Doctor speichert alle Konfigurationsänderungen und setzt Wizard-Metadaten, um die
Doctor-Ausführung zu protokollieren.

### 19) Workspace-Tipps (Sicherung + Speichersystem)

Doctor schlägt ein Workspace-Speichersystem vor, wenn keines vorhanden ist, und gibt einen Sicherungshinweis aus,
wenn der Workspace noch nicht unter Git steht.

Siehe [/concepts/agent-workspace](/de/concepts/agent-workspace) für eine vollständige Anleitung zur
Workspace-Struktur und Git-Sicherung (empfohlen: privates GitHub oder GitLab).
