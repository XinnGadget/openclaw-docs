---
read_when:
    - Slack einrichten oder den Slack-Socket-/HTTP-Modus debuggen
summary: Slack-Einrichtung und Laufzeitverhalten (Socket Mode + HTTP-Request-URLs)
title: Slack
x-i18n:
    generated_at: "2026-04-08T06:02:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: cad132131ddce688517def7c14703ad314441c67aacc4cc2a2a721e1d1c01942
    source_path: channels/slack.md
    workflow: 15
---

# Slack

Status: produktionsbereit für DMs und Channels über Slack-App-Integrationen. Der Standardmodus ist Socket Mode; HTTP-Request-URLs werden ebenfalls unterstützt.

<CardGroup cols={3}>
  <Card title="Kopplung" icon="link" href="/de/channels/pairing">
    Slack-DMs verwenden standardmäßig den Kopplungsmodus.
  </Card>
  <Card title="Slash-Befehle" icon="terminal" href="/de/tools/slash-commands">
    Natives Befehlsverhalten und Befehlskatalog.
  </Card>
  <Card title="Fehlerbehebung für Channels" icon="wrench" href="/de/channels/troubleshooting">
    Kanalübergreifende Diagnose- und Reparaturleitfäden.
  </Card>
</CardGroup>

## Schnelleinrichtung

<Tabs>
  <Tab title="Socket Mode (Standard)">
    <Steps>
      <Step title="Eine neue Slack-App erstellen">
        Drücken Sie in den Slack-App-Einstellungen auf die Schaltfläche **[Create New App](https://api.slack.com/apps/new)**:

        - wählen Sie **from a manifest** und wählen Sie einen Workspace für Ihre App aus
        - fügen Sie das [Beispiel-Manifest](#manifest-and-scope-checklist) von unten ein und fahren Sie mit der Erstellung fort
        - erzeugen Sie ein **App-Level Token** (`xapp-...`) mit `connections:write`
        - installieren Sie die App und kopieren Sie das angezeigte **Bot Token** (`xoxb-...`)
      </Step>

      <Step title="OpenClaw konfigurieren">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket",
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

        Env-Fallback (nur Standardkonto):

```bash
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
```

      </Step>

      <Step title="Gateway starten">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP-Request-URLs">
    <Steps>
      <Step title="Eine neue Slack-App erstellen">
        Drücken Sie in den Slack-App-Einstellungen auf die Schaltfläche **[Create New App](https://api.slack.com/apps/new)**:

        - wählen Sie **from a manifest** und wählen Sie einen Workspace für Ihre App aus
        - fügen Sie das [Beispiel-Manifest](#manifest-and-scope-checklist) ein und aktualisieren Sie die URLs vor dem Erstellen
        - speichern Sie das **Signing Secret** zur Verifizierung von Anfragen
        - installieren Sie die App und kopieren Sie das angezeigte **Bot Token** (`xoxb-...`)

      </Step>

      <Step title="OpenClaw konfigurieren">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events",
    },
  },
}
```

        <Note>
        Verwenden Sie eindeutige Webhook-Pfade für HTTP mit mehreren Konten

        Geben Sie jedem Konto einen eigenen `webhookPath` (Standard `/slack/events`), damit Registrierungen nicht kollidieren.
        </Note>

      </Step>

      <Step title="Gateway starten">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>
</Tabs>

## Manifest- und Scope-Checkliste

<Tabs>
  <Tab title="Socket Mode (Standard)">

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    }
  }
}
```

  </Tab>

  <Tab title="HTTP-Request-URLs">

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false,
        "url": "https://gateway-host.example.com/slack/events"
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "event_subscriptions": {
      "request_url": "https://gateway-host.example.com/slack/events",
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    },
    "interactivity": {
      "is_enabled": true,
      "request_url": "https://gateway-host.example.com/slack/events",
      "message_menu_options_url": "https://gateway-host.example.com/slack/events"
    }
  }
}
```

  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="Optionale Scope-Berechtigungen für Autorschaft (Schreibvorgänge)">
    Fügen Sie die Bot-Scope-Berechtigung `chat:write.customize` hinzu, wenn ausgehende Nachrichten die aktive Agentenidentität (benutzerdefinierter Benutzername und Symbol) statt der Standardidentität der Slack-App verwenden sollen.

    Wenn Sie ein Emoji-Symbol verwenden, erwartet Slack die Syntax `:emoji_name:`.
  </Accordion>
  <Accordion title="Optionale User-Token-Scopes (Lesevorgänge)">
    Wenn Sie `channels.slack.userToken` konfigurieren, sind typische Lese-Scopes:

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read` (wenn Sie von Slack-Such-Lesezugriffen abhängen)

  </Accordion>
</AccordionGroup>

## Token-Modell

- `botToken` + `appToken` sind für Socket Mode erforderlich.
- Der HTTP-Modus erfordert `botToken` + `signingSecret`.
- `botToken`, `appToken`, `signingSecret` und `userToken` akzeptieren Klartextzeichenfolgen oder SecretRef-Objekte.
- Konfigurations-Token überschreiben das Env-Fallback.
- Das Env-Fallback `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` gilt nur für das Standardkonto.
- `userToken` (`xoxp-...`) ist nur in der Konfiguration verfügbar (kein Env-Fallback) und verwendet standardmäßig schreibgeschütztes Verhalten (`userTokenReadOnly: true`).

Verhalten der Statusübersicht:

- Die Slack-Kontoinspektion verfolgt pro Zugangsdaten `*Source`- und `*Status`-Felder (`botToken`, `appToken`, `signingSecret`, `userToken`).
- Status ist `available`, `configured_unavailable` oder `missing`.
- `configured_unavailable` bedeutet, dass das Konto über SecretRef oder eine andere nicht-inline Secret-Quelle konfiguriert ist, der aktuelle Befehls-/Laufzeitpfad den tatsächlichen Wert jedoch nicht auflösen konnte.
- Im HTTP-Modus wird `signingSecretStatus` eingeschlossen; im Socket Mode ist das erforderliche Paar `botTokenStatus` + `appTokenStatus`.

<Tip>
Für Aktionen/Verzeichnislesevorgänge kann das User-Token bevorzugt werden, wenn es konfiguriert ist. Für Schreibvorgänge bleibt das Bot-Token bevorzugt; Schreibvorgänge mit User-Token sind nur erlaubt, wenn `userTokenReadOnly: false` und das Bot-Token nicht verfügbar ist.
</Tip>

## Aktionen und Gates

Slack-Aktionen werden über `channels.slack.actions.*` gesteuert.

Verfügbare Aktionsgruppen in den aktuellen Slack-Tools:

| Group      | Default |
| ---------- | ------- |
| messages   | enabled |
| reactions  | enabled |
| pins       | enabled |
| memberInfo | enabled |
| emojiList  | enabled |

Aktuelle Slack-Nachrichtenaktionen umfassen `send`, `upload-file`, `download-file`, `read`, `edit`, `delete`, `pin`, `unpin`, `list-pins`, `member-info` und `emoji-list`.

## Zugriffskontrolle und Routing

<Tabs>
  <Tab title="DM-Richtlinie">
    `channels.slack.dmPolicy` steuert den DM-Zugriff (veraltet: `channels.slack.dm.policy`):

    - `pairing` (Standard)
    - `allowlist`
    - `open` (erfordert, dass `channels.slack.allowFrom` `"*"` enthält; veraltet: `channels.slack.dm.allowFrom`)
    - `disabled`

    DM-Flags:

    - `dm.enabled` (Standard true)
    - `channels.slack.allowFrom` (bevorzugt)
    - `dm.allowFrom` (veraltet)
    - `dm.groupEnabled` (Gruppen-DMs standardmäßig false)
    - `dm.groupChannels` (optionale MPIM-Allowlist)

    Priorität bei mehreren Konten:

    - `channels.slack.accounts.default.allowFrom` gilt nur für das Konto `default`.
    - Benannte Konten übernehmen `channels.slack.allowFrom`, wenn ihr eigenes `allowFrom` nicht gesetzt ist.
    - Benannte Konten übernehmen nicht `channels.slack.accounts.default.allowFrom`.

    Die Kopplung in DMs verwendet `openclaw pairing approve slack <code>`.

  </Tab>

  <Tab title="Channel-Richtlinie">
    `channels.slack.groupPolicy` steuert die Channel-Behandlung:

    - `open`
    - `allowlist`
    - `disabled`

    Die Channel-Allowlist befindet sich unter `channels.slack.channels` und sollte stabile Channel-IDs verwenden.

    Laufzeithinweis: Wenn `channels.slack` vollständig fehlt (nur Env-Einrichtung), fällt die Laufzeit auf `groupPolicy="allowlist"` zurück und protokolliert eine Warnung (auch wenn `channels.defaults.groupPolicy` gesetzt ist).

    Auflösung von Namen/IDs:

    - Einträge in der Channel-Allowlist und der DM-Allowlist werden beim Start aufgelöst, wenn der Token-Zugriff dies zulässt
    - nicht aufgelöste Channel-Namenseinträge bleiben wie konfiguriert erhalten, werden für das Routing aber standardmäßig ignoriert
    - eingehende Autorisierung und Channel-Routing sind standardmäßig ID-first; direkte Benutzername-/Slug-Abgleiche erfordern `channels.slack.dangerouslyAllowNameMatching: true`

  </Tab>

  <Tab title="Erwähnungen und Channel-Benutzer">
    Channel-Nachrichten sind standardmäßig durch Erwähnungen begrenzt.

    Quellen für Erwähnungen:

    - explizite App-Erwähnung (`<@botId>`)
    - Regex-Muster für Erwähnungen (`agents.list[].groupChat.mentionPatterns`, Fallback `messages.groupChat.mentionPatterns`)
    - implizites Antwort-im-Bot-Thread-Verhalten (deaktiviert, wenn `thread.requireExplicitMention` `true` ist)

    Steuerelemente pro Channel (`channels.slack.channels.<id>`; Namen nur über Auflösung beim Start oder `dangerouslyAllowNameMatching`):

    - `requireMention`
    - `users` (Allowlist)
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - Schlüsselformat für `toolsBySender`: `id:`, `e164:`, `username:`, `name:` oder Platzhalter `"*"`
      (veraltete Schlüssel ohne Präfix werden weiterhin nur `id:` zugeordnet)

  </Tab>
</Tabs>

## Threading, Sessions und Antwort-Tags

- DMs werden als `direct` geroutet, Channels als `channel`, MPIMs als `group`.
- Mit dem Standard `session.dmScope=main` werden Slack-DMs zur Hauptsession des Agenten zusammengefasst.
- Channel-Sessions: `agent:<agentId>:slack:channel:<channelId>`.
- Thread-Antworten können bei Bedarf Thread-Session-Suffixe (`:thread:<threadTs>`) erzeugen.
- Standard für `channels.slack.thread.historyScope` ist `thread`; Standard für `thread.inheritParent` ist `false`.
- `channels.slack.thread.initialHistoryLimit` steuert, wie viele vorhandene Thread-Nachrichten abgerufen werden, wenn eine neue Thread-Session startet (Standard `20`; auf `0` setzen, um dies zu deaktivieren).
- `channels.slack.thread.requireExplicitMention` (Standard `false`): Wenn `true`, werden implizite Thread-Erwähnungen unterdrückt, sodass der Bot in Threads nur auf explizite `@bot`-Erwähnungen antwortet, selbst wenn der Bot bereits am Thread teilgenommen hat. Ohne dies umgehen Antworten in einem Thread mit Bot-Beteiligung das `requireMention`-Gate.

Steuerung für Antwort-Threading:

- `channels.slack.replyToMode`: `off|first|all|batched` (Standard `off`)
- `channels.slack.replyToModeByChatType`: pro `direct|group|channel`
- veralteter Fallback für direkte Chats: `channels.slack.dm.replyToMode`

Manuelle Antwort-Tags werden unterstützt:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

Hinweis: `replyToMode="off"` deaktiviert **jegliches** Antwort-Threading in Slack, einschließlich expliziter `[[reply_to_*]]`-Tags. Dies unterscheidet sich von Telegram, wo explizite Tags im Modus `"off"` weiterhin berücksichtigt werden. Der Unterschied spiegelt die Threading-Modelle der Plattformen wider: Slack-Threads verbergen Nachrichten im Channel, während Telegram-Antworten im Haupt-Chatverlauf sichtbar bleiben.

## Bestätigungsreaktionen

`ackReaction` sendet ein Bestätigungs-Emoji, während OpenClaw eine eingehende Nachricht verarbeitet.

Reihenfolge der Auflösung:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- Emoji-Fallback der Agentenidentität (`agents.list[].identity.emoji`, sonst "👀")

Hinweise:

- Slack erwartet Shortcodes (zum Beispiel `"eyes"`).
- Verwenden Sie `""`, um die Reaktion für das Slack-Konto oder global zu deaktivieren.

## Text-Streaming

`channels.slack.streaming` steuert das Verhalten der Live-Vorschau:

- `off`: Live-Vorschau-Streaming deaktivieren.
- `partial` (Standard): Vorschautext durch die neueste Teilausgabe ersetzen.
- `block`: Chunkweise Vorschauaktualisierungen anhängen.
- `progress`: Fortschrittsstatustext während der Generierung anzeigen und dann den endgültigen Text senden.

`channels.slack.streaming.nativeTransport` steuert das native Slack-Text-Streaming, wenn `channels.slack.streaming.mode` auf `partial` gesetzt ist (Standard: `true`).

- Für natives Text-Streaming und die Anzeige des Slack-Assistenten-Thread-Status muss ein Antwort-Thread verfügbar sein. Die Auswahl des Threads folgt weiterhin `replyToMode`.
- Wurzeln von Channel- und Gruppen-Chats können weiterhin die normale Entwurfsvorschau verwenden, wenn natives Streaming nicht verfügbar ist.
- Slack-DMs auf oberster Ebene bleiben standardmäßig außerhalb von Threads und zeigen daher keine Thread-ähnliche Vorschau an; verwenden Sie Thread-Antworten oder `typingReaction`, wenn dort sichtbarer Fortschritt angezeigt werden soll.
- Medien und Nicht-Text-Payloads fallen auf die normale Zustellung zurück.
- Wenn das Streaming mitten in einer Antwort fehlschlägt, fällt OpenClaw für verbleibende Payloads auf die normale Zustellung zurück.

Verwenden Sie die Entwurfsvorschau anstelle des nativen Slack-Text-Streamings:

```json5
{
  channels: {
    slack: {
      streaming: {
        mode: "partial",
        nativeTransport: false,
      },
    },
  },
}
```

Veraltete Schlüssel:

- `channels.slack.streamMode` (`replace | status_final | append`) wird automatisch zu `channels.slack.streaming.mode` migriert.
- boolesches `channels.slack.streaming` wird automatisch zu `channels.slack.streaming.mode` und `channels.slack.streaming.nativeTransport` migriert.
- das veraltete `channels.slack.nativeStreaming` wird automatisch zu `channels.slack.streaming.nativeTransport` migriert.

## Fallback für Tippreaktion

`typingReaction` fügt der eingehenden Slack-Nachricht vorübergehend eine Reaktion hinzu, während OpenClaw eine Antwort verarbeitet, und entfernt sie, wenn der Durchlauf abgeschlossen ist. Dies ist besonders nützlich außerhalb von Thread-Antworten, die standardmäßig einen Statusindikator "is typing..." verwenden.

Reihenfolge der Auflösung:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

Hinweise:

- Slack erwartet Shortcodes (zum Beispiel `"hourglass_flowing_sand"`).
- Die Reaktion erfolgt nach Best Effort, und die Bereinigung wird nach Abschluss der Antwort oder des Fehlerpfads automatisch versucht.

## Medien, Chunking und Zustellung

<AccordionGroup>
  <Accordion title="Eingehende Anhänge">
    Slack-Dateianhänge werden von privaten, bei Slack gehosteten URLs heruntergeladen (anfrageauthentifizierter Token-Flow) und bei erfolgreichem Abruf und zulässiger Größe in den Medienspeicher geschrieben.

    Die Standardobergrenze für eingehende Daten zur Laufzeit beträgt `20MB`, sofern sie nicht durch `channels.slack.mediaMaxMb` überschrieben wird.

  </Accordion>

  <Accordion title="Ausgehender Text und Dateien">
    - Text-Chunks verwenden `channels.slack.textChunkLimit` (Standard 4000)
    - `channels.slack.chunkMode="newline"` aktiviert das Aufteilen nach Absätzen zuerst
    - Dateisendungen verwenden die Slack-Upload-APIs und können Thread-Antworten (`thread_ts`) einschließen
    - die Obergrenze für ausgehende Medien folgt `channels.slack.mediaMaxMb`, wenn konfiguriert; andernfalls verwenden Channel-Sendungen die standardmäßigen MIME-Art-Vorgaben aus der Medienpipeline
  </Accordion>

  <Accordion title="Zustellziele">
    Bevorzugte explizite Ziele:

    - `user:<id>` für DMs
    - `channel:<id>` für Channels

    Slack-DMs werden über die Slack-Conversation-APIs geöffnet, wenn an Benutzerziele gesendet wird.

  </Accordion>
</AccordionGroup>

## Befehle und Slash-Verhalten

- Der native Befehls-Automodus ist für Slack **deaktiviert** (`commands.native: "auto"` aktiviert keine nativen Slack-Befehle).
- Aktivieren Sie native Slack-Befehlshandler mit `channels.slack.commands.native: true` (oder global `commands.native: true`).
- Wenn native Befehle aktiviert sind, registrieren Sie passende Slash-Befehle in Slack (`/<command>`-Namen), mit einer Ausnahme:
  - registrieren Sie `/agentstatus` für den Statusbefehl (Slack reserviert `/status`)
- Wenn native Befehle nicht aktiviert sind, können Sie mit `channels.slack.slashCommand` einen einzelnen konfigurierten Slash-Befehl ausführen.
- Native Argumentmenüs passen ihre Rendering-Strategie jetzt an:
  - bis zu 5 Optionen: Button-Blöcke
  - 6-100 Optionen: statisches Auswahlmenü
  - mehr als 100 Optionen: externe Auswahl mit asynchroner Optionsfilterung, wenn Handler für Interaktivitätsoptionen verfügbar sind
  - wenn codierte Optionswerte die Slack-Grenzen überschreiten, fällt der Ablauf auf Buttons zurück
- Für lange Options-Payloads verwenden Slash-Befehlsargumentmenüs vor dem Senden eines ausgewählten Werts einen Bestätigungsdialog.

Standardeinstellungen für Slash-Befehle:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

Slash-Sessions verwenden isolierte Schlüssel:

- `agent:<agentId>:slack:slash:<userId>`

und routen die Befehlsausführung weiterhin gegen die Ziel-Conversation-Session (`CommandTargetSessionKey`).

## Interaktive Antworten

Slack kann interaktive, von Agenten verfasste Antwortsteuerelemente rendern, diese Funktion ist jedoch standardmäßig deaktiviert.

Global aktivieren:

```json5
{
  channels: {
    slack: {
      capabilities: {
        interactiveReplies: true,
      },
    },
  },
}
```

Oder nur für ein Slack-Konto aktivieren:

```json5
{
  channels: {
    slack: {
      accounts: {
        ops: {
          capabilities: {
            interactiveReplies: true,
          },
        },
      },
    },
  },
}
```

Wenn aktiviert, können Agenten nur für Slack geltende Antwortdirektiven ausgeben:

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

Diese Direktiven werden in Slack Block Kit kompiliert und leiten Klicks oder Auswahlen über den bestehenden Slack-Interaktionsereignispfad zurück.

Hinweise:

- Dies ist Slack-spezifische UI. Andere Channels übersetzen Slack-Block-Kit-Direktiven nicht in ihre eigenen Button-Systeme.
- Die interaktiven Callback-Werte sind von OpenClaw erzeugte undurchsichtige Token, keine rohen, vom Agenten verfassten Werte.
- Wenn erzeugte interaktive Blöcke die Slack-Block-Kit-Grenzen überschreiten würden, fällt OpenClaw auf die ursprüngliche Textantwort zurück, anstatt eine ungültige Blocks-Payload zu senden.

## Exec-Genehmigungen in Slack

Slack kann als nativer Genehmigungs-Client mit interaktiven Buttons und Interaktionen fungieren, statt auf die Web-UI oder das Terminal zurückzufallen.

- Exec-Genehmigungen verwenden `channels.slack.execApprovals.*` für natives DM-/Channel-Routing.
- Plugin-Genehmigungen können weiterhin über dieselbe native Slack-Button-Oberfläche aufgelöst werden, wenn die Anfrage bereits in Slack landet und die Art der Genehmigungs-ID `plugin:` ist.
- Die Autorisierung des Genehmigers wird weiterhin erzwungen: Nur Benutzer, die als Genehmiger identifiziert wurden, können Anfragen über Slack genehmigen oder ablehnen.

Dies verwendet dieselbe gemeinsame Oberfläche für Genehmigungsbuttons wie andere Channels. Wenn `interactivity` in Ihren Slack-App-Einstellungen aktiviert ist, werden Genehmigungsaufforderungen direkt in der Konversation als Block-Kit-Buttons gerendert.
Wenn diese Buttons vorhanden sind, sind sie die primäre UX für Genehmigungen; OpenClaw
sollte einen manuellen `/approve`-Befehl nur dann einschließen, wenn das Tool-Ergebnis angibt, dass Chat-Genehmigungen nicht verfügbar sind oder eine manuelle Genehmigung der einzige Weg ist.

Konfigurationspfad:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers` (optional; fällt nach Möglichkeit auf `commands.ownerAllowFrom` zurück)
- `channels.slack.execApprovals.target` (`dm` | `channel` | `both`, Standard: `dm`)
- `agentFilter`, `sessionFilter`

Slack aktiviert native Exec-Genehmigungen automatisch, wenn `enabled` nicht gesetzt oder `"auto"` ist und mindestens ein
Genehmiger aufgelöst wird. Setzen Sie `enabled: false`, um Slack ausdrücklich als nativen Genehmigungs-Client zu deaktivieren.
Setzen Sie `enabled: true`, um native Genehmigungen zu erzwingen, wenn Genehmiger aufgelöst werden.

Standardverhalten ohne explizite Slack-Exec-Genehmigungskonfiguration:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

Eine explizite Slack-native Konfiguration ist nur erforderlich, wenn Sie Genehmiger überschreiben, Filter hinzufügen oder
die Zustellung im Ursprungs-Chat aktivieren möchten:

```json5
{
  channels: {
    slack: {
      execApprovals: {
        enabled: true,
        approvers: ["U12345678"],
        target: "both",
      },
    },
  },
}
```

Gemeinsame `approvals.exec`-Weiterleitung ist davon getrennt. Verwenden Sie sie nur, wenn Aufforderungen für Exec-Genehmigungen zusätzlich
an andere Chats oder explizite Ziele außerhalb des Bands weitergeleitet werden müssen. Gemeinsame `approvals.plugin`-Weiterleitung ist ebenfalls
getrennt; native Slack-Buttons können Plugin-Genehmigungen weiterhin auflösen, wenn diese Anfragen bereits
in Slack landen.

Dasselbe Chat-`/approve` funktioniert auch in Slack-Channels und DMs, die bereits Befehle unterstützen. Siehe [Exec approvals](/de/tools/exec-approvals) für das vollständige Modell zur Weiterleitung von Genehmigungen.

## Ereignisse und Betriebsverhalten

- Nachrichtenbearbeitungen/-löschungen/Thread-Broadcasts werden in Systemereignisse abgebildet.
- Ereignisse zum Hinzufügen/Entfernen von Reaktionen werden in Systemereignisse abgebildet.
- Ereignisse zu Beitritt/Verlassen von Mitgliedern, erstellten/umbenannten Channels und Hinzufügen/Entfernen von Pins werden in Systemereignisse abgebildet.
- `channel_id_changed` kann Channel-Konfigurationsschlüssel migrieren, wenn `configWrites` aktiviert ist.
- Channel-Topic-/Purpose-Metadaten werden als nicht vertrauenswürdiger Kontext behandelt und können in den Routing-Kontext eingespeist werden.
- Thread-Starter und anfängliche Kontextvorbelegung mit Thread-Verlauf werden bei Bedarf anhand konfigurierter Sender-Allowlists gefiltert.
- Block-Aktionen und Modal-Interaktionen erzeugen strukturierte `Slack interaction: ...`-Systemereignisse mit umfangreichen Payload-Feldern:
  - Block-Aktionen: ausgewählte Werte, Labels, Picker-Werte und `workflow_*`-Metadaten
  - modale `view_submission`- und `view_closed`-Ereignisse mit gerouteten Channel-Metadaten und Formulareingaben

## Verweise auf die Konfigurationsreferenz

Primäre Referenz:

- [Konfigurationsreferenz - Slack](/de/gateway/configuration-reference#slack)

  Wichtige Slack-Felder:
  - Modus/Auth: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM-Zugriff: `dm.enabled`, `dmPolicy`, `allowFrom` (veraltet: `dm.policy`, `dm.allowFrom`), `dm.groupEnabled`, `dm.groupChannels`
  - Kompatibilitätsschalter: `dangerouslyAllowNameMatching` (Break-Glass; ausgeschaltet lassen, sofern nicht benötigt)
  - Channel-Zugriff: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - Threading/Verlauf: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - Zustellung: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `streaming.nativeTransport`
  - Betrieb/Funktionen: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## Fehlerbehebung

<AccordionGroup>
  <Accordion title="Keine Antworten in Channels">
    Prüfen Sie in dieser Reihenfolge:

    - `groupPolicy`
    - Channel-Allowlist (`channels.slack.channels`)
    - `requireMention`
    - `users`-Allowlist pro Channel

    Nützliche Befehle:

```bash
openclaw channels status --probe
openclaw logs --follow
openclaw doctor
```

  </Accordion>

  <Accordion title="DM-Nachrichten werden ignoriert">
    Prüfen Sie:

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy` (oder veraltet `channels.slack.dm.policy`)
    - Kopplungsfreigaben / Allowlist-Einträge

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket-Modus verbindet sich nicht">
    Validieren Sie Bot- und App-Token sowie die Aktivierung von Socket Mode in den Slack-App-Einstellungen.

    Wenn `openclaw channels status --probe --json` `botTokenStatus` oder
    `appTokenStatus: "configured_unavailable"` anzeigt, ist das Slack-Konto
    konfiguriert, aber die aktuelle Laufzeit konnte den durch SecretRef
    gesicherten Wert nicht auflösen.

  </Accordion>

  <Accordion title="HTTP-Modus empfängt keine Ereignisse">
    Validieren Sie:

    - Signing Secret
    - Webhook-Pfad
    - Slack-Request-URLs (Events + Interactivity + Slash Commands)
    - eindeutiger `webhookPath` pro HTTP-Konto

    Wenn `signingSecretStatus: "configured_unavailable"` in Konto-
    Übersichten erscheint, ist das HTTP-Konto konfiguriert, aber die aktuelle Laufzeit konnte das durch SecretRef
    gesicherte Signing Secret nicht auflösen.

  </Accordion>

  <Accordion title="Native/Slash-Befehle werden nicht ausgelöst">
    Prüfen Sie, ob Sie Folgendes beabsichtigt haben:

    - nativen Befehlsmodus (`channels.slack.commands.native: true`) mit passenden in Slack registrierten Slash-Befehlen
    - oder den Modus für einen einzelnen Slash-Befehl (`channels.slack.slashCommand.enabled: true`)

    Prüfen Sie außerdem `commands.useAccessGroups` sowie Channel-/Benutzer-Allowlists.

  </Accordion>
</AccordionGroup>

## Verwandt

- [Kopplung](/de/channels/pairing)
- [Gruppen](/de/channels/groups)
- [Sicherheit](/de/gateway/security)
- [Channel-Routing](/de/channels/channel-routing)
- [Fehlerbehebung](/de/channels/troubleshooting)
- [Konfiguration](/de/gateway/configuration)
- [Slash-Befehle](/de/tools/slash-commands)
