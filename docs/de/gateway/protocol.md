---
read_when:
    - Implementierung oder Aktualisierung von Gateway-WS-Clients
    - Fehlersuche bei Protokollabweichungen oder Verbindungsfehlern
    - Erneutes Generieren von Protokollschema/-modellen
summary: 'Gateway-WebSocket-Protokoll: Handshake, Frames, Versionierung'
title: Gateway-Protokoll
x-i18n:
    generated_at: "2026-04-16T06:22:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 683e61ebe993a2d739bc34860060b0e3eda36b5c57267a2bcc03d177ec612fb3
    source_path: gateway/protocol.md
    workflow: 15
---

# Gateway-Protokoll (WebSocket)

Das Gateway-WS-Protokoll ist die **einzige Control Plane + der einzige Node-Transport** für
OpenClaw. Alle Clients (CLI, Web-UI, macOS-App, iOS-/Android-Nodes, Headless-
Nodes) verbinden sich über WebSocket und deklarieren ihre **Rolle** + ihren **Scope** beim
Handshake.

## Transport

- WebSocket, Text-Frames mit JSON-Payloads.
- Der erste Frame **muss** eine `connect`-Anfrage sein.

## Handshake (`connect`)

Gateway → Client (Pre-Connect-Challenge):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

Client → Gateway:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Gateway → Client:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": {
    "type": "hello-ok",
    "protocol": 3,
    "server": { "version": "…", "connId": "…" },
    "features": { "methods": ["…"], "events": ["…"] },
    "snapshot": { "…": "…" },
    "policy": {
      "maxPayload": 26214400,
      "maxBufferedBytes": 52428800,
      "tickIntervalMs": 15000
    }
  }
}
```

`server`, `features`, `snapshot` und `policy` sind laut Schema alle erforderlich
(`src/gateway/protocol/schema/frames.ts`). `auth` und `canvasHostUrl` sind optional.

Wenn ein Device-Token ausgestellt wird, enthält `hello-ok` außerdem:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

Während einer vertrauenswürdigen Bootstrap-Übergabe kann `hello-ok.auth` außerdem zusätzliche
gebundene Rolleneinträge in `deviceTokens` enthalten:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

Für den integrierten Bootstrap-Ablauf für Node/Operator bleibt das primäre Node-Token bei
`scopes: []`, und jedes übergebene Operator-Token bleibt auf die Bootstrap-
Operator-Allowlist beschränkt (`operator.approvals`, `operator.read`,
`operator.talk.secrets`, `operator.write`). Bootstrap-Scope-Prüfungen bleiben
rollenpräfixiert: Operator-Einträge erfüllen nur Operator-Anfragen, und Nicht-Operator-
Rollen benötigen weiterhin Scopes unter ihrem eigenen Rollenpräfix.

### Node-Beispiel

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## Framing

- **Request**: `{type:"req", id, method, params}`
- **Response**: `{type:"res", id, ok, payload|error}`
- **Event**: `{type:"event", event, payload, seq?, stateVersion?}`

Methoden mit Nebenwirkungen erfordern **Idempotenzschlüssel** (siehe Schema).

## Rollen + Scopes

### Rollen

- `operator` = Control-Plane-Client (CLI/UI/Automatisierung).
- `node` = Capability-Host (camera/screen/canvas/system.run).

### Scopes (`operator`)

Häufige Scopes:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

`talk.config` mit `includeSecrets: true` erfordert `operator.talk.secrets`
(oder `operator.admin`).

Plugin-registrierte Gateway-RPC-Methoden können ihren eigenen Operator-Scope anfordern, aber
reservierte Core-Admin-Präfixe (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) werden immer zu `operator.admin` aufgelöst.

Der Methodenscope ist nur die erste Hürde. Einige Slash-Befehle, die über
`chat.send` erreicht werden, wenden zusätzlich strengere Prüfungen auf
Befehlsebene an. Zum Beispiel erfordern persistente Schreibvorgänge mit
`/config set` und `/config unset` `operator.admin`.

`node.pair.approve` hat zusätzlich zur Basis-Methodenscope außerdem eine weitere
Scope-Prüfung zum Zeitpunkt der Freigabe:

- Anfragen ohne Befehle: `operator.pairing`
- Anfragen mit Nicht-Exec-Node-Befehlen: `operator.pairing` + `operator.write`
- Anfragen, die `system.run`, `system.run.prepare` oder `system.which` enthalten:
  `operator.pairing` + `operator.admin`

### Caps/commands/permissions (`node`)

Nodes deklarieren ihre Capability-Claims beim Verbinden:

- `caps`: allgemeine Capability-Kategorien.
- `commands`: Befehls-Allowlist für `invoke`.
- `permissions`: granulare Schalter (z. B. `screen.record`, `camera.capture`).

Das Gateway behandelt diese als **Claims** und erzwingt serverseitige Allowlists.

## Presence

- `system-presence` gibt Einträge zurück, die nach Geräteidentität indiziert sind.
- Presence-Einträge enthalten `deviceId`, `roles` und `scopes`, damit UIs eine einzelne Zeile pro Gerät anzeigen können,
  selbst wenn es sowohl als **operator** als auch als **node** verbunden ist.

## Häufige RPC-Methodenfamilien

Diese Seite ist kein generierter vollständiger Dump, aber die öffentliche WS-Oberfläche ist umfassender
als die Handshake-/Auth-Beispiele oben. Dies sind die wichtigsten Methodenfamilien, die das
Gateway derzeit bereitstellt.

`hello-ok.features.methods` ist eine konservative Discovery-Liste, die aus
`src/gateway/server-methods-list.ts` sowie geladenen Plugin-/Channel-Methodenexports aufgebaut wird.
Behandle sie als Feature Discovery, nicht als generierten Dump aller aufrufbaren Helfer,
die in `src/gateway/server-methods/*.ts` implementiert sind.

### System und Identität

- `health` gibt den gecachten oder frisch geprüften Gateway-Health-Snapshot zurück.
- `status` gibt die Gateway-Zusammenfassung im Stil von `/status` zurück; sensible Felder werden
  nur für Operator-Clients mit Admin-Scope einbezogen.
- `gateway.identity.get` gibt die Gateway-Geräteidentität zurück, die von Relay- und
  Pairing-Abläufen verwendet wird.
- `system-presence` gibt den aktuellen Presence-Snapshot für verbundene
  Operator-/Node-Geräte zurück.
- `system-event` hängt ein Systemereignis an und kann den Presence-
  Kontext aktualisieren/übertragen.
- `last-heartbeat` gibt das zuletzt persistierte Heartbeat-Ereignis zurück.
- `set-heartbeats` schaltet die Heartbeat-Verarbeitung auf dem Gateway um.

### Modelle und Nutzung

- `models.list` gibt den zur Laufzeit erlaubten Modellkatalog zurück.
- `usage.status` gibt Provider-Nutzungsfenster/Zusammenfassungen des verbleibenden Kontingents zurück.
- `usage.cost` gibt aggregierte Zusammenfassungen der Kostennutzung für einen Datumsbereich zurück.
- `doctor.memory.status` gibt den Bereitschaftsstatus für Vector Memory / Embeddings für den
  aktiven Standard-Agent-Workspace zurück.
- `sessions.usage` gibt Nutzungszusammenfassungen pro Sitzung zurück.
- `sessions.usage.timeseries` gibt Zeitreihennutzung für eine Sitzung zurück.
- `sessions.usage.logs` gibt Nutzungslogeinträge für eine Sitzung zurück.

### Channels und Login-Helfer

- `channels.status` gibt Statuszusammenfassungen für integrierte und gebündelte Channels/Plugins zurück.
- `channels.logout` meldet einen bestimmten Channel/Account ab, sofern der Channel
  Logout unterstützt.
- `web.login.start` startet einen QR-/Web-Login-Ablauf für den aktuell QR-fähigen Web-
  Channel-Provider.
- `web.login.wait` wartet darauf, dass dieser QR-/Web-Login-Ablauf abgeschlossen wird, und startet bei Erfolg den
  Channel.
- `push.test` sendet einen Test-APNs-Push an einen registrierten iOS-Node.
- `voicewake.get` gibt die gespeicherten Wake-Word-Trigger zurück.
- `voicewake.set` aktualisiert Wake-Word-Trigger und überträgt die Änderung.

### Messaging und Logs

- `send` ist die direkte RPC für ausgehende Zustellung an Channel/Account/Thread-Ziele
  außerhalb des Chat-Runners.
- `logs.tail` gibt den konfigurierten Gateway-Dateilog-Tail mit Cursor/Limit und
  Max-Byte-Steuerung zurück.

### Talk und TTS

- `talk.config` gibt die effektive Talk-Konfigurations-Payload zurück; `includeSecrets`
  erfordert `operator.talk.secrets` (oder `operator.admin`).
- `talk.mode` setzt/überträgt den aktuellen Talk-Modusstatus für WebChat-/Control-UI-
  Clients.
- `talk.speak` synthetisiert Sprache über den aktiven Talk-Speech-Provider.
- `tts.status` gibt den aktivierten TTS-Status, den aktiven Provider, Fallback-Provider
  und den Provider-Konfigurationsstatus zurück.
- `tts.providers` gibt das sichtbare TTS-Provider-Inventar zurück.
- `tts.enable` und `tts.disable` schalten den TTS-Status der Voreinstellungen um.
- `tts.setProvider` aktualisiert den bevorzugten TTS-Provider.
- `tts.convert` führt eine einmalige Text-zu-Sprache-Konvertierung aus.

### Secrets, Konfiguration, Update und Wizard

- `secrets.reload` löst aktive SecretRefs erneut auf und tauscht den Laufzeitstatus für Secrets
  nur bei vollständigem Erfolg aus.
- `secrets.resolve` löst Secret-Zuweisungen für ein bestimmtes
  Befehls-/Ziel-Set auf.
- `config.get` gibt den aktuellen Konfigurations-Snapshot und Hash zurück.
- `config.set` schreibt eine validierte Konfigurations-Payload.
- `config.patch` führt eine partielle Konfigurationsaktualisierung zusammen.
- `config.apply` validiert und ersetzt die vollständige Konfigurations-Payload.
- `config.schema` gibt die Live-Konfigurationsschema-Payload zurück, die von Control UI und
  CLI-Tooling verwendet wird: Schema, `uiHints`, Version und Generierungsmetadaten, einschließlich
  Plugin- und Channel-Schema-Metadaten, wenn die Laufzeit sie laden kann. Das Schema
  enthält Feldmetadaten `title` / `description`, die aus denselben Labels
  und Hilfetexten abgeleitet werden, die von der UI verwendet werden, einschließlich verschachtelter Objekte,
  Wildcards, Array-Items und `anyOf`- / `oneOf`- / `allOf`-Kompositionszweigen, wenn passende
  Felddokumentation existiert.
- `config.schema.lookup` gibt eine pfadbezogene Lookup-Payload für einen Konfigurationspfad zurück:
  normalisierter Pfad, ein flacher Schemaknoten, passender Hint + `hintPath` und
  Zusammenfassungen der direkten Kindknoten für UI-/CLI-Drill-down.
  - Lookup-Schemaknoten behalten die nutzerseitige Dokumentation und häufige Validierungsfelder:
    `title`, `description`, `type`, `enum`, `const`, `format`, `pattern`,
    numerische/String-/Array-/Objekt-Grenzen und boolesche Flags wie
    `additionalProperties`, `deprecated`, `readOnly`, `writeOnly`.
  - Zusammenfassungen der Kindknoten stellen `key`, normalisierten `path`, `type`, `required`,
    `hasChildren` sowie den passenden `hint` / `hintPath` bereit.
- `update.run` führt den Gateway-Update-Ablauf aus und plant einen Neustart nur dann,
  wenn das Update selbst erfolgreich war.
- `wizard.start`, `wizard.next`, `wizard.status` und `wizard.cancel` stellen den
  Onboarding-Wizard über WS RPC bereit.

### Vorhandene große Familien

#### Agent- und Workspace-Helfer

- `agents.list` gibt konfigurierte Agent-Einträge zurück.
- `agents.create`, `agents.update` und `agents.delete` verwalten Agent-Datensätze und
  Workspace-Verdrahtung.
- `agents.files.list`, `agents.files.get` und `agents.files.set` verwalten die
  exponierten Bootstrap-Workspace-Dateien eines Agenten.
- `agent.identity.get` gibt die effektive Assistentenidentität für einen Agenten oder
  eine Sitzung zurück.
- `agent.wait` wartet darauf, dass ein Lauf abgeschlossen wird, und gibt den terminalen Snapshot zurück, wenn
  verfügbar.

#### Sitzungssteuerung

- `sessions.list` gibt den aktuellen Sitzungsindex zurück.
- `sessions.subscribe` und `sessions.unsubscribe` schalten Abonnements für Sitzungsänderungsereignisse
  für den aktuellen WS-Client um.
- `sessions.messages.subscribe` und `sessions.messages.unsubscribe` schalten
  Abonnements für Transkript-/Nachrichtenereignisse für eine Sitzung um.
- `sessions.preview` gibt begrenzte Transkriptvorschauen für bestimmte Sitzungs-
  Schlüssel zurück.
- `sessions.resolve` löst ein Sitzungsziel auf oder kanonisiert es.
- `sessions.create` erstellt einen neuen Sitzungseintrag.
- `sessions.send` sendet eine Nachricht in eine bestehende Sitzung.
- `sessions.steer` ist die Variante zum Unterbrechen und Neu-Steuern für eine aktive Sitzung.
- `sessions.abort` bricht aktive Arbeit für eine Sitzung ab.
- `sessions.patch` aktualisiert Sitzungsmetadaten/-Overrides.
- `sessions.reset`, `sessions.delete` und `sessions.compact` führen Sitzungs-
  Wartung durch.
- `sessions.get` gibt die vollständige gespeicherte Sitzungszeile zurück.
- Die Chat-Ausführung verwendet weiterhin `chat.history`, `chat.send`, `chat.abort` und
  `chat.inject`.
- `chat.history` ist für UI-Clients anzeige-normalisiert: Inline-Direktiventags werden
  aus sichtbarem Text entfernt, XML-Payloads von Tool-Aufrufen im Klartext (einschließlich
  `<tool_call>...</tool_call>`, `<function_call>...</function_call>`,
  `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>` und
  abgeschnittener Tool-Call-Blöcke) sowie durchgesickerte ASCII-/Full-Width-
  Modellsteuerungstoken werden entfernt, reine Assistant-Zeilen mit stillen Tokens wie exaktem `NO_REPLY` /
  `no_reply` werden weggelassen, und übergroße Zeilen können durch Platzhalter ersetzt werden.

#### Geräte-Pairing und Device-Tokens

- `device.pair.list` gibt ausstehende und genehmigte gekoppelte Geräte zurück.
- `device.pair.approve`, `device.pair.reject` und `device.pair.remove` verwalten
  Geräte-Pairing-Einträge.
- `device.token.rotate` rotiert ein Token für ein gekoppeltes Gerät innerhalb seiner genehmigten Rollen-
  und Scope-Grenzen.
- `device.token.revoke` widerruft ein Token für ein gekoppeltes Gerät.

#### Node-Pairing, Invoke und ausstehende Arbeit

- `node.pair.request`, `node.pair.list`, `node.pair.approve`,
  `node.pair.reject` und `node.pair.verify` decken Node-Pairing und Bootstrap-
  Verifizierung ab.
- `node.list` und `node.describe` geben bekannte/verbundene Node-Zustände zurück.
- `node.rename` aktualisiert ein Label für einen gekoppelten Node.
- `node.invoke` leitet einen Befehl an einen verbundenen Node weiter.
- `node.invoke.result` gibt das Ergebnis für eine Invoke-Anfrage zurück.
- `node.event` überträgt von Nodes stammende Ereignisse zurück ins Gateway.
- `node.canvas.capability.refresh` aktualisiert bereichsbezogene Canvas-Capability-Tokens.
- `node.pending.pull` und `node.pending.ack` sind die Queue-APIs für verbundene Nodes.
- `node.pending.enqueue` und `node.pending.drain` verwalten dauerhafte ausstehende Arbeit
  für offline/getrennte Nodes.

#### Genehmigungsfamilien

- `exec.approval.request`, `exec.approval.get`, `exec.approval.list` und
  `exec.approval.resolve` decken einmalige Exec-Genehmigungsanfragen sowie Lookup/Replay
  ausstehender Genehmigungen ab.
- `exec.approval.waitDecision` wartet auf eine ausstehende Exec-Genehmigung und gibt
  die finale Entscheidung zurück (oder `null` bei Timeout).
- `exec.approvals.get` und `exec.approvals.set` verwalten Snapshots der Gateway-Exec-
  Genehmigungsrichtlinie.
- `exec.approvals.node.get` und `exec.approvals.node.set` verwalten Node-lokale Exec-
  Genehmigungsrichtlinien über Node-Relay-Befehle.
- `plugin.approval.request`, `plugin.approval.list`,
  `plugin.approval.waitDecision` und `plugin.approval.resolve` decken
  Plugin-definierte Genehmigungsabläufe ab.

#### Weitere große Familien

- Automatisierung:
  - `wake` plant eine sofortige oder beim nächsten Heartbeat erfolgende Wake-Textinjektion
  - `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`,
    `cron.run`, `cron.runs`
- Skills/Tools: `commands.list`, `skills.*`, `tools.catalog`, `tools.effective`

### Häufige Ereignisfamilien

- `chat`: UI-Chat-Updates wie `chat.inject` und andere Chat-
  Ereignisse nur für das Transkript.
- `session.message` und `session.tool`: Transkript-/Ereignisstream-Updates für eine
  abonnierte Sitzung.
- `sessions.changed`: Sitzungsindex oder -metadaten wurden geändert.
- `presence`: Updates des System-Presence-Snapshots.
- `tick`: periodisches Keepalive-/Liveness-Ereignis.
- `health`: Update des Gateway-Health-Snapshots.
- `heartbeat`: Update des Heartbeat-Ereignisstreams.
- `cron`: Ereignis für Änderung von Cron-Lauf/Job.
- `shutdown`: Benachrichtigung über das Herunterfahren des Gateways.
- `node.pair.requested` / `node.pair.resolved`: Lebenszyklus des Node-Pairings.
- `node.invoke.request`: Broadcast einer Node-Invoke-Anfrage.
- `device.pair.requested` / `device.pair.resolved`: Lebenszyklus gekoppelter Geräte.
- `voicewake.changed`: Konfiguration des Wake-Word-Triggers wurde geändert.
- `exec.approval.requested` / `exec.approval.resolved`: Lebenszyklus der Exec-
  Genehmigung.
- `plugin.approval.requested` / `plugin.approval.resolved`: Lebenszyklus der Plugin-
  Genehmigung.

### Node-Helfermethoden

- Nodes können `skills.bins` aufrufen, um die aktuelle Liste ausführbarer Skill-Dateien
  für Auto-Allow-Prüfungen abzurufen.

### Operator-Helfermethoden

- Operatoren können `commands.list` (`operator.read`) aufrufen, um das Laufzeit-
  Befehlsinventar für einen Agenten abzurufen.
  - `agentId` ist optional; lasse es weg, um den Standard-Agent-Workspace zu lesen.
  - `scope` steuert, auf welche Oberfläche sich `name` primär bezieht:
    - `text` gibt das primäre Textbefehlstoken ohne führendes `/` zurück
    - `native` und der Standardpfad `both` geben providerbewusste native Namen
      zurück, wenn verfügbar
  - `textAliases` enthält exakte Slash-Aliasse wie `/model` und `/m`.
  - `nativeName` enthält den providerbewussten nativen Befehlsnamen, wenn ein solcher existiert.
  - `provider` ist optional und beeinflusst nur die native Benennung sowie die Verfügbarkeit nativer Plugin-
    Befehle.
  - `includeArgs=false` lässt serialisierte Argumentmetadaten in der Antwort weg.
- Operatoren können `tools.catalog` (`operator.read`) aufrufen, um den Laufzeit-Toolkatalog für einen
  Agenten abzurufen. Die Antwort enthält gruppierte Tools und Herkunftsmetadaten:
  - `source`: `core` oder `plugin`
  - `pluginId`: Plugin-Eigentümer, wenn `source="plugin"`
  - `optional`: ob ein Plugin-Tool optional ist
- Operatoren können `tools.effective` (`operator.read`) aufrufen, um das zur Laufzeit effektive Tool-
  Inventar für eine Sitzung abzurufen.
  - `sessionKey` ist erforderlich.
  - Das Gateway leitet den vertrauenswürdigen Laufzeitkontext serverseitig aus der Sitzung ab, statt
    vom Aufrufer bereitgestellten Auth- oder Zustellungskontext zu akzeptieren.
  - Die Antwort ist sitzungsbezogen und spiegelt wider, was die aktive Unterhaltung derzeit verwenden kann,
    einschließlich Core-, Plugin- und Channel-Tools.
- Operatoren können `skills.status` (`operator.read`) aufrufen, um das sichtbare
  Skills-Inventar für einen Agenten abzurufen.
  - `agentId` ist optional; lasse es weg, um den Standard-Agent-Workspace zu lesen.
  - Die Antwort enthält Eignung, fehlende Voraussetzungen, Konfigurationsprüfungen und
    bereinigte Installationsoptionen, ohne rohe Secret-Werte offenzulegen.
- Operatoren können `skills.search` und `skills.detail` (`operator.read`) für
  ClawHub-Discovery-Metadaten aufrufen.
- Operatoren können `skills.install` (`operator.admin`) in zwei Modi aufrufen:
  - ClawHub-Modus: `{ source: "clawhub", slug, version?, force? }` installiert einen
    Skill-Ordner in das `skills/`-Verzeichnis des Standard-Agent-Workspace.
  - Gateway-Installer-Modus: `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    führt eine deklarierte `metadata.openclaw.install`-Aktion auf dem Gateway-Host aus.
- Operatoren können `skills.update` (`operator.admin`) in zwei Modi aufrufen:
  - Im ClawHub-Modus wird ein verfolgter Slug oder werden alle verfolgten ClawHub-Installationen im
    Standard-Agent-Workspace aktualisiert.
  - Im Konfigurationsmodus werden Werte in `skills.entries.<skillKey>` wie `enabled`,
    `apiKey` und `env` gepatcht.

## Exec-Genehmigungen

- Wenn eine Exec-Anfrage eine Genehmigung benötigt, sendet das Gateway `exec.approval.requested`.
- Operator-Clients lösen dies durch Aufruf von `exec.approval.resolve` auf (erfordert den Scope `operator.approvals`).
- Für `host=node` muss `exec.approval.request` `systemRunPlan` enthalten (kanonische `argv`-/`cwd`-/`rawCommand`-/Sitzungsmetadaten). Anfragen ohne `systemRunPlan` werden abgelehnt.
- Nach der Genehmigung verwenden weitergeleitete `node.invoke system.run`-Aufrufe denselben kanonischen
  `systemRunPlan` als maßgeblichen Befehls-/`cwd`-/Sitzungskontext.
- Wenn ein Aufrufer `command`, `rawCommand`, `cwd`, `agentId` oder
  `sessionKey` zwischen `prepare` und dem finalen weitergeleiteten genehmigten `system.run` ändert, lehnt das
  Gateway den Lauf ab, statt der geänderten Payload zu vertrauen.

## Agent-Zustellungs-Fallback

- `agent`-Anfragen können `deliver=true` enthalten, um ausgehende Zustellung anzufordern.
- `bestEffortDeliver=false` behält striktes Verhalten bei: Nicht auflösbare oder nur intern verfügbare Zustellungsziele geben `INVALID_REQUEST` zurück.
- `bestEffortDeliver=true` erlaubt Fallback auf reine Sitzungsausführung, wenn keine extern zustellbare Route aufgelöst werden kann (zum Beispiel bei internen/WebChat-Sitzungen oder mehrdeutigen Multi-Channel-Konfigurationen).

## Versionierung

- `PROTOCOL_VERSION` befindet sich in `src/gateway/protocol/schema/protocol-schemas.ts`.
- Clients senden `minProtocol` + `maxProtocol`; der Server lehnt Abweichungen ab.
- Schemas + Modelle werden aus TypeBox-Definitionen generiert:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

### Client-Konstanten

Der Referenzclient in `src/gateway/client.ts` verwendet diese Standardwerte. Die Werte sind
über Protokoll v3 hinweg stabil und bilden die erwartete Basis für Drittanbieter-Clients.

| Konstante                                 | Standardwert                                          | Quelle                                                     |
| ----------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------- |
| `PROTOCOL_VERSION`                        | `3`                                                   | `src/gateway/protocol/schema/protocol-schemas.ts`          |
| Request-Timeout (pro RPC)                 | `30_000` ms                                           | `src/gateway/client.ts` (`requestTimeoutMs`)               |
| Preauth- / Connect-Challenge-Timeout      | `10_000` ms                                           | `src/gateway/handshake-timeouts.ts` (Clamp `250`–`10_000`) |
| Initialer Reconnect-Backoff               | `1_000` ms                                            | `src/gateway/client.ts` (`backoffMs`)                      |
| Maximaler Reconnect-Backoff               | `30_000` ms                                           | `src/gateway/client.ts` (`scheduleReconnect`)              |
| Fast-Retry-Clamp nach Device-Token-Close  | `250` ms                                              | `src/gateway/client.ts`                                    |
| Force-Stop-Schonfrist vor `terminate()`   | `250` ms                                              | `FORCE_STOP_TERMINATE_GRACE_MS`                            |
| Standard-Timeout von `stopAndWait()`      | `1_000` ms                                            | `STOP_AND_WAIT_TIMEOUT_MS`                                 |
| Standard-Tick-Intervall (vor `hello-ok`)  | `30_000` ms                                           | `src/gateway/client.ts`                                    |
| Tick-Timeout-Close                        | Code `4000`, wenn Stille `tickIntervalMs * 2` überschreitet | `src/gateway/client.ts`                               |
| `MAX_PAYLOAD_BYTES`                       | `25 * 1024 * 1024` (25 MB)                            | `src/gateway/server-constants.ts`                          |

Der Server kündigt das effektive `policy.tickIntervalMs`, `policy.maxPayload`
und `policy.maxBufferedBytes` in `hello-ok` an; Clients sollten diese Werte
statt der Standardwerte vor dem Handshake beachten.

## Auth

- Authentifizierung des Gateways per Shared Secret verwendet `connect.params.auth.token` oder
  `connect.params.auth.password`, abhängig vom konfigurierten Auth-Modus.
- Identitätstragende Modi wie Tailscale Serve
  (`gateway.auth.allowTailscale: true`) oder nicht über Loopback laufendes
  `gateway.auth.mode: "trusted-proxy"` erfüllen die Connect-Auth-Prüfung über
  Request-Header statt über `connect.params.auth.*`.
- `gateway.auth.mode: "none"` für privaten Ingress überspringt die Connect-Auth per Shared Secret
  vollständig; diesen Modus nicht auf öffentlichem/nicht vertrauenswürdigem Ingress bereitstellen.
- Nach dem Pairing stellt das Gateway ein **Device-Token** aus, das auf die Rollen + Scopes
  der Verbindung begrenzt ist. Es wird in `hello-ok.auth.deviceToken` zurückgegeben und sollte
  vom Client für zukünftige Verbindungen persistiert werden.
- Clients sollten das primäre `hello-ok.auth.deviceToken` nach jeder
  erfolgreichen Verbindung persistieren.
- Beim erneuten Verbinden mit diesem **gespeicherten** Device-Token sollte auch der gespeicherte
  genehmigte Scope-Satz für dieses Token wiederverwendet werden. Dadurch bleibt bereits gewährter
  Zugriff für Lesen/Probe/Status erhalten und es wird vermieden, dass Reconnects stillschweigend auf einen
  engeren impliziten Admin-only-Scope zusammenfallen.
- Clientseitiger Aufbau der Connect-Auth (`selectConnectAuth` in
  `src/gateway/client.ts`):
  - `auth.password` ist orthogonal und wird immer weitergeleitet, wenn gesetzt.
  - `auth.token` wird in dieser Prioritätsreihenfolge befüllt: zuerst explizites Shared Token,
    dann ein explizites `deviceToken`, dann ein gespeichertes gerätespezifisches Token (indiziert nach
    `deviceId` + `role`).
  - `auth.bootstrapToken` wird nur gesendet, wenn keines der oben genannten ein
    `auth.token` aufgelöst hat. Ein Shared Token oder ein aufgelöstes Device-Token unterdrückt es.
  - Automatische Promotion eines gespeicherten Device-Tokens beim einmaligen
    Retry bei `AUTH_TOKEN_MISMATCH` ist **nur für vertrauenswürdige Endpunkte** aktiviert —
    Loopback oder `wss://` mit angeheftetem `tlsFingerprint`. Öffentliches `wss://`
    ohne Pinning qualifiziert sich nicht.
- Zusätzliche Einträge in `hello-ok.auth.deviceTokens` sind Bootstrap-Handoff-Tokens.
  Persistiere sie nur, wenn die Verbindung Bootstrap-Auth über einen vertrauenswürdigen Transport
  wie `wss://` oder Loopback/lokales Pairing verwendet hat.
- Wenn ein Client ein **explizites** `deviceToken` oder explizite `scopes` angibt, bleibt dieser
  vom Aufrufer angeforderte Scope-Satz maßgeblich; gecachte Scopes werden nur wiederverwendet, wenn
  der Client das gespeicherte gerätespezifische Token wiederverwendet.
- Device-Tokens können über `device.token.rotate` und
  `device.token.revoke` rotiert/widerrufen werden (erfordert den Scope `operator.pairing`).
- Ausstellung/Rotation von Tokens bleibt auf den genehmigten Rollensatz beschränkt, der im
  Pairing-Eintrag dieses Geräts aufgezeichnet ist; durch die Rotation eines Tokens kann ein Gerät nicht
  auf eine Rolle erweitert werden, die durch die Pairing-Genehmigung nie gewährt wurde.
- Für Sitzungen mit Tokens gekoppelter Geräte ist die Geräteverwaltung selbstbegrenzt, sofern der
  Aufrufer nicht zusätzlich `operator.admin` hat: Nicht-Admin-Aufrufer können nur ihren **eigenen**
  Geräteeintrag entfernen/widerrufen/rotieren.
- `device.token.rotate` prüft außerdem den angeforderten Operator-Scope-Satz gegen die
  aktuellen Sitzungsscopes des Aufrufers. Nicht-Admin-Aufrufer können ein Token nicht in einen
  umfassenderen Operator-Scope-Satz rotieren, als sie bereits besitzen.
- Auth-Fehler enthalten `error.details.code` sowie Wiederherstellungshinweise:
  - `error.details.canRetryWithDeviceToken` (boolesch)
  - `error.details.recommendedNextStep` (`retry_with_device_token`, `update_auth_configuration`, `update_auth_credentials`, `wait_then_retry`, `review_auth_configuration`)
- Client-Verhalten bei `AUTH_TOKEN_MISMATCH`:
  - Vertrauenswürdige Clients können einen begrenzten Retry mit einem gecachten gerätespezifischen Token versuchen.
  - Wenn dieser Retry fehlschlägt, sollten Clients automatische Reconnect-Schleifen stoppen und Hinweise für Operator-Aktionen anzeigen.

## Geräteidentität + Pairing

- Nodes sollten eine stabile Geräteidentität (`device.id`) angeben, die aus einem
  Schlüsselpaar-Fingerprint abgeleitet ist.
- Gateways stellen Tokens pro Gerät + Rolle aus.
- Pairing-Genehmigungen sind für neue Geräte-IDs erforderlich, sofern lokale automatische Genehmigung
  nicht aktiviert ist.
- Die automatische Pairing-Genehmigung ist auf direkte lokale Loopback-Verbindungen ausgerichtet.
- OpenClaw hat außerdem einen engen lokalen Self-Connect-Pfad für Backend-/Container-
  Kontexte für vertrauenswürdige Shared-Secret-Helferabläufe.
- Verbindungen über dasselbe Host-Tailnet oder LAN werden für Pairing weiterhin als remote behandelt und
  erfordern eine Genehmigung.
- Alle WS-Clients müssen während `connect` die Geräteidentität `device` angeben (`operator` + `node`).
  Control UI kann sie nur in diesen Modi weglassen:
  - `gateway.controlUi.allowInsecureAuth=true` für localhost-only-Kompatibilität mit unsicherem HTTP.
  - erfolgreiche `gateway.auth.mode: "trusted-proxy"`-Authentifizierung der Operator-Control-UI.
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true` (Break-Glass, erhebliche Sicherheitsabsenkung).
- Alle Verbindungen müssen die vom Server bereitgestellte Nonce `connect.challenge` signieren.

### Migrationsdiagnostik für Geräte-Auth

Für Legacy-Clients, die noch das Signaturverhalten vor der Challenge verwenden, gibt `connect` jetzt
Detailcodes `DEVICE_AUTH_*` unter `error.details.code` mit einem stabilen `error.details.reason` zurück.

Häufige Migrationsfehler:

| Meldung                     | details.code                     | details.reason           | Bedeutung                                                   |
| --------------------------- | -------------------------------- | ------------------------ | ----------------------------------------------------------- |
| `device nonce required`     | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | Client hat `device.nonce` weggelassen (oder leer gesendet). |
| `device nonce mismatch`     | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | Client hat mit einer veralteten/falschen Nonce signiert.    |
| `device signature invalid`  | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | Signatur-Payload entspricht nicht der v2-Payload.           |
| `device signature expired`  | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | Signierter Zeitstempel liegt außerhalb des erlaubten Skews. |
| `device identity mismatch`  | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` entspricht nicht dem Public-Key-Fingerprint.    |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | Public-Key-Format/Kanonisierung fehlgeschlagen.             |

Migrationsziel:

- Immer auf `connect.challenge` warten.
- Die v2-Payload signieren, die die Server-Nonce enthält.
- Dieselbe Nonce in `connect.params.device.nonce` senden.
- Die bevorzugte Signatur-Payload ist `v3`, die zusätzlich zu den Feldern für device/client/role/scopes/token/nonce auch `platform` und `deviceFamily` bindet.
- Legacy-Signaturen vom Typ `v2` bleiben aus Kompatibilitätsgründen akzeptiert, aber das Anheften von Metadaten gekoppelter Geräte steuert weiterhin die Befehlsrichtlinie beim erneuten Verbinden.

## TLS + Pinning

- TLS wird für WS-Verbindungen unterstützt.
- Clients können optional den Fingerprint des Gateway-Zertifikats anheften (siehe Konfiguration `gateway.tls`
  sowie `gateway.remote.tlsFingerprint` oder CLI `--tls-fingerprint`).

## Umfang

Dieses Protokoll stellt die **vollständige Gateway-API** bereit (Status, Channels, Modelle, Chat,
Agent, Sitzungen, Nodes, Genehmigungen usw.). Die genaue Oberfläche wird durch die
TypeBox-Schemas in `src/gateway/protocol/schema.ts` definiert.
