---
read_when:
    - Hai bisogno della semantica esatta della configurazione a livello di campo o dei valori predefiniti.
    - Stai convalidando i blocchi di configurazione di canali, modelli, Gateway o strumenti
summary: Riferimento della configurazione del Gateway per le chiavi principali di OpenClaw, i valori predefiniti e i link ai riferimenti dedicati dei sottosistemi
title: Riferimento della configurazione
x-i18n:
    generated_at: "2026-04-15T14:40:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7a4da3b41d0304389bd6359aac1185c231e529781b607656ab352f8a8104bdba
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# Riferimento della configurazione

Riferimento della configurazione principale per `~/.openclaw/openclaw.json`. Per una panoramica orientata alle attività, vedi [Configuration](/it/gateway/configuration).

Questa pagina copre le principali superfici di configurazione di OpenClaw e rimanda altrove quando un sottosistema ha un proprio riferimento più approfondito. **Non** cerca di includere in linea ogni catalogo di comandi posseduto da canali/plugin né ogni parametro avanzato di memoria/QMD in un'unica pagina.

Fonte autorevole del codice:

- `openclaw config schema` stampa lo JSON Schema live usato per la convalida e la Control UI, con i metadati bundled/plugin/channel uniti quando disponibili
- `config.schema.lookup` restituisce un nodo di schema delimitato a un singolo percorso per gli strumenti di approfondimento
- `pnpm config:docs:check` / `pnpm config:docs:gen` convalidano l'hash baseline della documentazione di configurazione rispetto alla superficie di schema corrente

Riferimenti dedicati approfonditi:

- [Riferimento della configurazione della memoria](/it/reference/memory-config) per `agents.defaults.memorySearch.*`, `memory.qmd.*`, `memory.citations` e la configurazione di Dreaming sotto `plugins.entries.memory-core.config.dreaming`
- [Comandi slash](/it/tools/slash-commands) per il catalogo corrente dei comandi integrati + bundled
- pagine del canale/plugin proprietario per le superfici di comando specifiche del canale

Il formato della configurazione è **JSON5** (commenti + virgole finali consentiti). Tutti i campi sono opzionali: OpenClaw usa valori predefiniti sicuri quando vengono omessi.

---

## Canali

Ogni canale si avvia automaticamente quando la sua sezione di configurazione esiste (a meno che `enabled: false`).

### Accesso DM e gruppi

Tutti i canali supportano criteri per i DM e criteri per i gruppi:

| Criterio DM         | Comportamento                                                  |
| ------------------- | -------------------------------------------------------------- |
| `pairing` (default) | I mittenti sconosciuti ricevono un codice di abbinamento monouso; il proprietario deve approvare |
| `allowlist`         | Solo i mittenti in `allowFrom` (o nello store allow associato) |
| `open`              | Consenti tutti i DM in ingresso (richiede `allowFrom: ["*"]`)  |
| `disabled`          | Ignora tutti i DM in ingresso                                  |

| Criterio gruppi       | Comportamento                                         |
| --------------------- | ----------------------------------------------------- |
| `allowlist` (default) | Solo i gruppi che corrispondono all'allowlist configurata |
| `open`                | Ignora le allowlist dei gruppi (la gating per menzione si applica comunque) |
| `disabled`            | Blocca tutti i messaggi di gruppo/stanza              |

<Note>
`channels.defaults.groupPolicy` imposta il valore predefinito quando `groupPolicy` di un provider non è impostato.
I codici di abbinamento scadono dopo 1 ora. Le richieste di abbinamento DM in sospeso sono limitate a **3 per canale**.
Se un blocco provider è completamente assente (`channels.<provider>` assente), il criterio gruppi a runtime torna a `allowlist` (fail-closed) con un avviso all'avvio.
</Note>

### Override del modello per canale

Usa `channels.modelByChannel` per vincolare ID di canale specifici a un modello. I valori accettano `provider/model` o alias di modello configurati. La mappatura del canale si applica quando una sessione non ha già un override del modello (ad esempio impostato tramite `/model`).

```json5
{
  channels: {
    modelByChannel: {
      discord: {
        "123456789012345678": "anthropic/claude-opus-4-6",
      },
      slack: {
        C1234567890: "openai/gpt-4.1",
      },
      telegram: {
        "-1001234567890": "openai/gpt-4.1-mini",
        "-1001234567890:topic:99": "anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

### Valori predefiniti del canale e Heartbeat

Usa `channels.defaults` per il comportamento condiviso di criterio gruppi e Heartbeat tra i provider:

```json5
{
  channels: {
    defaults: {
      groupPolicy: "allowlist", // open | allowlist | disabled
      contextVisibility: "all", // all | allowlist | allowlist_quote
      heartbeat: {
        showOk: false,
        showAlerts: true,
        useIndicator: true,
      },
    },
  },
}
```

- `channels.defaults.groupPolicy`: criterio gruppi di fallback quando il `groupPolicy` a livello provider non è impostato.
- `channels.defaults.contextVisibility`: modalità predefinita di visibilità del contesto supplementare per tutti i canali. Valori: `all` (predefinito, include tutto il contesto di citazioni/thread/storia), `allowlist` (include solo il contesto da mittenti in allowlist), `allowlist_quote` (come allowlist ma mantiene il contesto esplicito di citazione/risposta). Override per canale: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: includi gli stati sani dei canali nell'output Heartbeat.
- `channels.defaults.heartbeat.showAlerts`: includi gli stati degradati/di errore nell'output Heartbeat.
- `channels.defaults.heartbeat.useIndicator`: visualizza un output Heartbeat compatto in stile indicatore.

### WhatsApp

WhatsApp funziona tramite il canale web del Gateway (Baileys Web). Si avvia automaticamente quando esiste una sessione collegata.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // spunte blu (false in modalità chat con sé stessi)
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
  web: {
    enabled: true,
    heartbeatSeconds: 60,
    reconnect: {
      initialMs: 2000,
      maxMs: 120000,
      factor: 1.4,
      jitter: 0.2,
      maxAttempts: 0,
    },
  },
}
```

<Accordion title="WhatsApp multi-account">

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {},
        personal: {},
        biz: {
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

- I comandi in uscita usano come valore predefinito l'account `default` se presente; altrimenti il primo ID account configurato (ordinato).
- L'opzionale `channels.whatsapp.defaultAccount` sovrascrive quella selezione predefinita di account di fallback quando corrisponde a un ID account configurato.
- La directory di autenticazione Baileys legacy per account singolo viene migrata da `openclaw doctor` in `whatsapp/default`.
- Override per account: `channels.whatsapp.accounts.<id>.sendReadReceipts`, `channels.whatsapp.accounts.<id>.dmPolicy`, `channels.whatsapp.accounts.<id>.allowFrom`.

</Accordion>

### Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "Keep answers brief.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Stay on topic.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all | batched
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (default: off; opt in explicitly to avoid preview-edit rate limits)
      actions: { reactions: true, sendMessage: true },
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 100,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: {
        autoSelectFamily: true,
        dnsResultOrder: "ipv4first",
      },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- Token del bot: `channels.telegram.botToken` o `channels.telegram.tokenFile` (solo file regolare; i symlink sono rifiutati), con `TELEGRAM_BOT_TOKEN` come fallback per l'account predefinito.
- L'opzionale `channels.telegram.defaultAccount` sovrascrive la selezione predefinita dell'account quando corrisponde a un ID account configurato.
- Nelle configurazioni multi-account (2+ ID account), imposta un valore predefinito esplicito (`channels.telegram.defaultAccount` o `channels.telegram.accounts.default`) per evitare il routing di fallback; `openclaw doctor` avvisa quando questo manca o non è valido.
- `configWrites: false` blocca le scritture di configurazione avviate da Telegram (migrazioni degli ID dei supergruppi, `/config set|unset`).
- Le voci `bindings[]` di livello superiore con `type: "acp"` configurano binding ACP persistenti per gli argomenti del forum (usa il canonico `chatId:topic:topicId` in `match.peer.id`). La semantica dei campi è condivisa in [ACP Agents](/it/tools/acp-agents#channel-specific-settings).
- Le anteprime di streaming di Telegram usano `sendMessage` + `editMessageText` (funziona in chat dirette e di gruppo).
- Criterio di retry: vedi [Retry policy](/it/concepts/retry).

### Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 100,
      allowBots: false,
      actions: {
        reactions: true,
        stickers: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        voiceStatus: true,
        events: true,
        moderation: false,
      },
      replyToMode: "off", // off | first | all | batched
      dmPolicy: "pairing",
      allowFrom: ["1234567890", "123456789012345678"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["openclaw-dm"] },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          ignoreOtherMentions: true,
          reactionNotifications: "own",
          users: ["987654321098765432"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["docs"],
              systemPrompt: "Short answers only.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress maps to partial on Discord)
      maxLinesPerMessage: 17,
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // opt-in for sessions_spawn({ thread: true })
      },
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
        },
      },
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["987654321098765432"],
        agentFilter: ["default"],
        sessionFilter: ["discord:"],
        target: "dm", // dm | channel | both
        cleanupAfterResolve: false,
      },
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

- Token: `channels.discord.token`, con `DISCORD_BOT_TOKEN` come fallback per l'account predefinito.
- Le chiamate dirette in uscita che forniscono un `token` Discord esplicito usano quel token per la chiamata; le impostazioni di retry/criterio dell'account continuano comunque a provenire dall'account selezionato nello snapshot runtime attivo.
- L'opzionale `channels.discord.defaultAccount` sovrascrive la selezione predefinita dell'account quando corrisponde a un ID account configurato.
- Usa `user:<id>` (DM) o `channel:<id>` (canale guild) per i target di consegna; gli ID numerici senza prefisso vengono rifiutati.
- Gli slug delle guild sono in minuscolo con gli spazi sostituiti da `-`; le chiavi dei canali usano il nome trasformato in slug (senza `#`). Preferisci gli ID delle guild.
- I messaggi scritti dal bot vengono ignorati per impostazione predefinita. `allowBots: true` li abilita; usa `allowBots: "mentions"` per accettare solo i messaggi dei bot che menzionano il bot (i propri messaggi restano comunque filtrati).
- `channels.discord.guilds.<id>.ignoreOtherMentions` (e gli override a livello di canale) elimina i messaggi che menzionano un altro utente o ruolo ma non il bot (escludendo @everyone/@here).
- `maxLinesPerMessage` (predefinito 17) divide i messaggi lunghi in altezza anche quando sono sotto i 2000 caratteri.
- `channels.discord.threadBindings` controlla il routing associato ai thread di Discord:
  - `enabled`: override Discord per le funzionalità di sessione associate ai thread (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` e consegna/routing associati)
  - `idleHours`: override Discord per l'auto-unfocus dovuto a inattività in ore (`0` lo disabilita)
  - `maxAgeHours`: override Discord per l'età massima rigida in ore (`0` lo disabilita)
  - `spawnSubagentSessions`: interruttore opt-in per la creazione/associazione automatica di thread con `sessions_spawn({ thread: true })`
- Le voci `bindings[]` di livello superiore con `type: "acp"` configurano binding ACP persistenti per canali e thread (usa l'id del canale/thread in `match.peer.id`). La semantica dei campi è condivisa in [ACP Agents](/it/tools/acp-agents#channel-specific-settings).
- `channels.discord.ui.components.accentColor` imposta il colore d'accento per i contenitori Discord components v2.
- `channels.discord.voice` abilita le conversazioni nei canali vocali Discord e gli override opzionali di auto-join + TTS.
- `channels.discord.voice.daveEncryption` e `channels.discord.voice.decryptionFailureTolerance` vengono passati a `@discordjs/voice` come opzioni DAVE (rispettivamente `true` e `24` per impostazione predefinita).
- OpenClaw tenta inoltre il recupero della ricezione vocale uscendo e rientrando in una sessione vocale dopo ripetuti errori di decrittazione.
- `channels.discord.streaming` è la chiave canonica per la modalità di streaming. I valori legacy `streamMode` e booleani `streaming` vengono migrati automaticamente.
- `channels.discord.autoPresence` mappa la disponibilità runtime alla presenza del bot (healthy => online, degraded => idle, exhausted => dnd) e consente override opzionali del testo di stato.
- `channels.discord.dangerouslyAllowNameMatching` riabilita la corrispondenza tramite nome/tag mutabili (modalità di compatibilità break-glass).
- `channels.discord.execApprovals`: consegna nativa Discord delle approvazioni exec e autorizzazione degli approvatori.
  - `enabled`: `true`, `false` o `"auto"` (predefinito). In modalità auto, le approvazioni exec si attivano quando gli approvatori possono essere risolti da `approvers` o `commands.ownerAllowFrom`.
  - `approvers`: ID utente Discord autorizzati ad approvare le richieste exec. Se omesso, usa `commands.ownerAllowFrom` come fallback.
  - `agentFilter`: allowlist opzionale di ID agente. Omettilo per inoltrare le approvazioni per tutti gli agenti.
  - `sessionFilter`: pattern opzionali di chiavi sessione (sottostringa o regex).
  - `target`: dove inviare le richieste di approvazione. `"dm"` (predefinito) le invia ai DM degli approvatori, `"channel"` le invia al canale di origine, `"both"` le invia a entrambi. Quando il target include `"channel"`, i pulsanti possono essere usati solo dagli approvatori risolti.
  - `cleanupAfterResolve`: quando `true`, elimina i DM di approvazione dopo approvazione, rifiuto o timeout.

**Modalità di notifica delle reazioni:** `off` (nessuna), `own` (messaggi del bot, predefinita), `all` (tutti i messaggi), `allowlist` (da `guilds.<id>.users` su tutti i messaggi).

### Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": { allow: true, requireMention: true },
      },
      actions: { reactions: true },
      typingIndicator: "message",
      mediaMaxMb: 20,
    },
  },
}
```

- JSON dell'account di servizio: inline (`serviceAccount`) o basato su file (`serviceAccountFile`).
- È supportato anche SecretRef per l'account di servizio (`serviceAccountRef`).
- Fallback da env: `GOOGLE_CHAT_SERVICE_ACCOUNT` o `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- Usa `spaces/<spaceId>` o `users/<userId>` per i target di consegna.
- `channels.googlechat.dangerouslyAllowNameMatching` riabilita la corrispondenza tramite principal email mutabile (modalità di compatibilità break-glass).

### Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
      dmPolicy: "pairing",
      allowFrom: ["U123", "U456", "*"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["G123"] },
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          allowBots: false,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "Short answers only.",
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off", // off | first | all | batched
      thread: {
        historyScope: "thread", // thread | channel
        inheritParent: false,
      },
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },
      slashCommand: {
        enabled: true,
        name: "openclaw",
        sessionPrefix: "slack:slash",
        ephemeral: true,
      },
      typingReaction: "hourglass_flowing_sand",
      textChunkLimit: 4000,
      chunkMode: "length",
      streaming: {
        mode: "partial", // off | partial | block | progress
        nativeTransport: true, // use Slack native streaming API when mode=partial
      },
      mediaMaxMb: 20,
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["U123"],
        agentFilter: ["default"],
        sessionFilter: ["slack:"],
        target: "dm", // dm | channel | both
      },
    },
  },
}
```

- **La modalità Socket** richiede sia `botToken` sia `appToken` (`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` come fallback env dell'account predefinito).
- **La modalità HTTP** richiede `botToken` più `signingSecret` (alla radice o per account).
- `botToken`, `appToken`, `signingSecret` e `userToken` accettano stringhe in chiaro o oggetti SecretRef.
- Gli snapshot degli account Slack espongono campi source/status per credenziale, come `botTokenSource`, `botTokenStatus`, `appTokenStatus` e, in modalità HTTP, `signingSecretStatus`. `configured_unavailable` significa che l'account è configurato tramite SecretRef ma il percorso corrente di comando/runtime non ha potuto risolvere il valore del segreto.
- `configWrites: false` blocca le scritture di configurazione avviate da Slack.
- L'opzionale `channels.slack.defaultAccount` sovrascrive la selezione predefinita dell'account quando corrisponde a un ID account configurato.
- `channels.slack.streaming.mode` è la chiave canonica per la modalità di streaming di Slack. `channels.slack.streaming.nativeTransport` controlla il trasporto di streaming nativo di Slack. I valori legacy `streamMode`, booleani `streaming` e `nativeStreaming` vengono migrati automaticamente.
- Usa `user:<id>` (DM) o `channel:<id>` per i target di consegna.

**Modalità di notifica delle reazioni:** `off`, `own` (predefinita), `all`, `allowlist` (da `reactionAllowlist`).

**Isolamento delle sessioni thread:** `thread.historyScope` è per-thread (predefinito) o condiviso nel canale. `thread.inheritParent` copia la trascrizione del canale padre nei nuovi thread.

- Lo streaming nativo di Slack più lo stato del thread in stile assistente Slack "is typing..." richiedono un target di risposta nel thread. I DM di livello superiore restano fuori thread per impostazione predefinita, quindi usano `typingReaction` o la consegna normale invece dell'anteprima in stile thread.
- `typingReaction` aggiunge una reazione temporanea al messaggio Slack in ingresso mentre una risposta è in corso, quindi la rimuove al completamento. Usa uno shortcode emoji Slack come `"hourglass_flowing_sand"`.
- `channels.slack.execApprovals`: consegna nativa Slack delle approvazioni exec e autorizzazione degli approvatori. Stesso schema di Discord: `enabled` (`true`/`false`/`"auto"`), `approvers` (ID utente Slack), `agentFilter`, `sessionFilter` e `target` (`"dm"`, `"channel"` o `"both"`).

| Gruppo di azioni | Predefinito | Note                    |
| ---------------- | ----------- | ----------------------- |
| reactions        | abilitato   | Reagire + elencare reazioni |
| messages         | abilitato   | Leggere/inviare/modificare/eliminare |
| pins             | abilitato   | Fissare/rimuovere/elencare |
| memberInfo       | abilitato   | Informazioni membro     |
| emojiList        | abilitato   | Elenco emoji personalizzate |

### Mattermost

Mattermost viene distribuito come Plugin: `openclaw plugins install @openclaw/mattermost`.

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
      chatmode: "oncall", // oncall | onmessage | onchar
      oncharPrefixes: [">", "!"],
      groups: {
        "*": { requireMention: true },
        "team-channel-id": { requireMention: false },
      },
      commands: {
        native: true, // opt-in
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // URL esplicito opzionale per deployment reverse-proxy/pubblici
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

Modalità chat: `oncall` (risponde a @-mention, predefinita), `onmessage` (ogni messaggio), `onchar` (messaggi che iniziano con il prefisso trigger).

Quando i comandi nativi di Mattermost sono abilitati:

- `commands.callbackPath` deve essere un percorso (ad esempio `/api/channels/mattermost/command`), non un URL completo.
- `commands.callbackUrl` deve risolversi nell'endpoint Gateway di OpenClaw ed essere raggiungibile dal server Mattermost.
- I callback slash nativi vengono autenticati con i token per comando restituiti da Mattermost durante la registrazione dei comandi slash. Se la registrazione fallisce o nessun comando viene attivato, OpenClaw rifiuta i callback con `Unauthorized: invalid command token.`
- Per host di callback privati/tailnet/interni, Mattermost potrebbe richiedere che `ServiceSettings.AllowedUntrustedInternalConnections` includa l'host/dominio del callback. Usa valori host/dominio, non URL completi.
- `channels.mattermost.configWrites`: consente o nega le scritture di configurazione avviate da Mattermost.
- `channels.mattermost.requireMention`: richiede `@mention` prima di rispondere nei canali.
- `channels.mattermost.groups.<channelId>.requireMention`: override del gating per menzione per canale (`"*"` per il predefinito).
- L'opzionale `channels.mattermost.defaultAccount` sovrascrive la selezione predefinita dell'account quando corrisponde a un ID account configurato.

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // binding opzionale dell'account
      dmPolicy: "pairing",
      allowFrom: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      configWrites: true,
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50,
    },
  },
}
```

**Modalità di notifica delle reazioni:** `off`, `own` (predefinita), `all`, `allowlist` (da `reactionAllowlist`).

- `channels.signal.account`: vincola l'avvio del canale a una specifica identità account Signal.
- `channels.signal.configWrites`: consente o nega le scritture di configurazione avviate da Signal.
- L'opzionale `channels.signal.defaultAccount` sovrascrive la selezione predefinita dell'account quando corrisponde a un ID account configurato.

### BlueBubbles

BlueBubbles è il percorso iMessage consigliato (supportato da Plugin, configurato sotto `channels.bluebubbles`).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, controlli di gruppo e azioni avanzate:
      // vedi /channels/bluebubbles
    },
  },
}
```

- Percorsi delle chiavi core coperti qui: `channels.bluebubbles`, `channels.bluebubbles.dmPolicy`.
- L'opzionale `channels.bluebubbles.defaultAccount` sovrascrive la selezione predefinita dell'account quando corrisponde a un ID account configurato.
- Le voci `bindings[]` di livello superiore con `type: "acp"` possono associare le conversazioni BlueBubbles a sessioni ACP persistenti. Usa un handle BlueBubbles o una stringa target (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) in `match.peer.id`. Semantica dei campi condivisa: [ACP Agents](/it/tools/acp-agents#channel-specific-settings).
- La configurazione completa del canale BlueBubbles è documentata in [BlueBubbles](/it/channels/bluebubbles).

### iMessage

OpenClaw avvia `imsg rpc` (JSON-RPC su stdio). Non è richiesto alcun demone o porta.

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host",
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],
      historyLimit: 50,
      includeAttachments: false,
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    },
  },
}
```

- L'opzionale `channels.imessage.defaultAccount` sovrascrive la selezione predefinita dell'account quando corrisponde a un ID account configurato.

- Richiede l'accesso completo al disco per il database di Messaggi.
- Preferisci i target `chat_id:<id>`. Usa `imsg chats --limit 20` per elencare le chat.
- `cliPath` può puntare a un wrapper SSH; imposta `remoteHost` (`host` o `user@host`) per il recupero degli allegati via SCP.
- `attachmentRoots` e `remoteAttachmentRoots` limitano i percorsi degli allegati in ingresso (predefinito: `/Users/*/Library/Messages/Attachments`).
- SCP usa il controllo rigoroso della chiave host, quindi assicurati che la chiave host del relay esista già in `~/.ssh/known_hosts`.
- `channels.imessage.configWrites`: consente o nega le scritture di configurazione avviate da iMessage.
- Le voci `bindings[]` di livello superiore con `type: "acp"` possono associare le conversazioni iMessage a sessioni ACP persistenti. Usa un handle normalizzato o un target chat esplicito (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) in `match.peer.id`. Semantica dei campi condivisa: [ACP Agents](/it/tools/acp-agents#channel-specific-settings).

<Accordion title="Esempio di wrapper SSH iMessage">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix è supportato da estensione ed è configurato sotto `channels.matrix`.

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
      encryption: true,
      initialSyncLimit: 20,
      defaultAccount: "ops",
      accounts: {
        ops: {
          name: "Ops",
          userId: "@ops:example.org",
          accessToken: "syt_ops_xxx",
        },
        alerts: {
          userId: "@alerts:example.org",
          password: "secret",
          proxy: "http://127.0.0.1:7891",
        },
      },
    },
  },
}
```

- L'autenticazione tramite token usa `accessToken`; l'autenticazione tramite password usa `userId` + `password`.
- `channels.matrix.proxy` instrada il traffico HTTP di Matrix attraverso un proxy HTTP(S) esplicito. Gli account denominati possono sovrascriverlo con `channels.matrix.accounts.<id>.proxy`.
- `channels.matrix.network.dangerouslyAllowPrivateNetwork` consente homeserver privati/interni. `proxy` e questo opt-in di rete sono controlli indipendenti.
- `channels.matrix.defaultAccount` seleziona l'account preferito nelle configurazioni multi-account.
- `channels.matrix.autoJoin` ha come predefinito `off`, quindi le stanze invitate e i nuovi inviti in stile DM vengono ignorati finché non imposti `autoJoin: "allowlist"` con `autoJoinAllowlist` oppure `autoJoin: "always"`.
- `channels.matrix.execApprovals`: consegna nativa Matrix delle approvazioni exec e autorizzazione degli approvatori.
  - `enabled`: `true`, `false` o `"auto"` (predefinito). In modalità auto, le approvazioni exec si attivano quando gli approvatori possono essere risolti da `approvers` o `commands.ownerAllowFrom`.
  - `approvers`: ID utente Matrix (ad es. `@owner:example.org`) autorizzati ad approvare le richieste exec.
  - `agentFilter`: allowlist opzionale di ID agente. Omettilo per inoltrare le approvazioni per tutti gli agenti.
  - `sessionFilter`: pattern opzionali di chiavi sessione (sottostringa o regex).
  - `target`: dove inviare le richieste di approvazione. `"dm"` (predefinito), `"channel"` (stanza di origine) o `"both"`.
  - Override per account: `channels.matrix.accounts.<id>.execApprovals`.
- `channels.matrix.dm.sessionScope` controlla come i DM Matrix vengono raggruppati in sessioni: `per-user` (predefinito) condivide per peer instradato, mentre `per-room` isola ogni stanza DM.
- I probe di stato di Matrix e le ricerche live nella directory usano lo stesso criterio proxy del traffico runtime.
- La configurazione completa di Matrix, le regole di targeting e gli esempi di configurazione sono documentati in [Matrix](/it/channels/matrix).

### Microsoft Teams

Microsoft Teams è supportato da estensione ed è configurato sotto `channels.msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, criteri team/canale:
      // vedi /channels/msteams
    },
  },
}
```

- Percorsi delle chiavi core coperti qui: `channels.msteams`, `channels.msteams.configWrites`.
- La configurazione completa di Teams (credenziali, webhook, criterio DM/gruppi, override per team/per canale) è documentata in [Microsoft Teams](/it/channels/msteams).

### IRC

IRC è supportato da estensione ed è configurato sotto `channels.irc`.

```json5
{
  channels: {
    irc: {
      enabled: true,
      dmPolicy: "pairing",
      configWrites: true,
      nickserv: {
        enabled: true,
        service: "NickServ",
        password: "${IRC_NICKSERV_PASSWORD}",
        register: false,
        registerEmail: "bot@example.com",
      },
    },
  },
}
```

- Percorsi delle chiavi core coperti qui: `channels.irc`, `channels.irc.dmPolicy`, `channels.irc.configWrites`, `channels.irc.nickserv.*`.
- L'opzionale `channels.irc.defaultAccount` sovrascrive la selezione predefinita dell'account quando corrisponde a un ID account configurato.
- La configurazione completa del canale IRC (host/porta/TLS/canali/allowlist/gating per menzione) è documentata in [IRC](/it/channels/irc).

### Multi-account (tutti i canali)

Esegui più account per canale (ognuno con il proprio `accountId`):

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Bot principale",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Bot avvisi",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- `default` viene usato quando `accountId` è omesso (CLI + routing).
- I token env si applicano solo all'account **default**.
- Le impostazioni base del canale si applicano a tutti gli account, salvo override per account.
- Usa `bindings[].match.accountId` per instradare ogni account a un agente diverso.
- Se aggiungi un account non predefinito tramite `openclaw channels add` (o onboarding del canale) mentre sei ancora su una configurazione di canale di livello superiore single-account, OpenClaw promuove prima i valori single-account di livello superiore con ambito account nella mappa degli account del canale, così l'account originale continua a funzionare. La maggior parte dei canali li sposta in `channels.<channel>.accounts.default`; Matrix può invece preservare un target denominato/predefinito esistente corrispondente.
- I binding esistenti solo-canale (senza `accountId`) continuano a corrispondere all'account predefinito; i binding con ambito account restano opzionali.
- Anche `openclaw doctor --fix` ripara le forme miste spostando i valori single-account di livello superiore con ambito account nell'account promosso scelto per quel canale. La maggior parte dei canali usa `accounts.default`; Matrix può invece preservare un target denominato/predefinito esistente corrispondente.

### Altri canali di estensione

Molti canali di estensione sono configurati come `channels.<id>` e documentati nelle rispettive pagine dedicate del canale (ad esempio Feishu, Matrix, LINE, Nostr, Zalo, Nextcloud Talk, Synology Chat e Twitch).
Vedi l'indice completo dei canali: [Channels](/it/channels).

### Gating per menzione nelle chat di gruppo

I messaggi di gruppo richiedono per impostazione predefinita **una menzione obbligatoria** (menzione nei metadati o pattern regex sicuri). Si applica alle chat di gruppo di WhatsApp, Telegram, Discord, Google Chat e iMessage.

**Tipi di menzione:**

- **Menzioni nei metadati**: @-mention native della piattaforma. Ignorate nella modalità chat con sé stessi di WhatsApp.
- **Pattern di testo**: pattern regex sicuri in `agents.list[].groupChat.mentionPatterns`. I pattern non validi e le ripetizioni annidate non sicure vengono ignorati.
- Il gating per menzione viene applicato solo quando il rilevamento è possibile (menzioni native o almeno un pattern).

```json5
{
  messages: {
    groupChat: { historyLimit: 50 },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw", "openclaw"] } }],
  },
}
```

`messages.groupChat.historyLimit` imposta il valore predefinito globale. I canali possono sovrascriverlo con `channels.<channel>.historyLimit` (o per account). Imposta `0` per disabilitarlo.

#### Limiti della cronologia DM

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30,
      dms: {
        "123456789": { historyLimit: 50 },
      },
    },
  },
}
```

Risoluzione: override per-DM → valore predefinito del provider → nessun limite (tutto conservato).

Supportati: `telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

#### Modalità chat con sé stessi

Includi il tuo numero in `allowFrom` per abilitare la modalità chat con sé stessi (ignora le @-mention native, risponde solo ai pattern di testo):

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: { mentionPatterns: ["reisponde", "@openclaw"] },
      },
    ],
  },
}
```

### Comandi (gestione dei comandi in chat)

```json5
{
  commands: {
    native: "auto", // registra i comandi nativi quando supportati
    nativeSkills: "auto", // registra i comandi nativi delle skill quando supportati
    text: true, // analizza i /command nei messaggi chat
    bash: false, // consente ! (alias: /bash)
    bashForegroundMs: 2000,
    config: false, // consente /config
    mcp: false, // consente /mcp
    plugins: false, // consente /plugins
    debug: false, // consente /debug
    restart: true, // consente /restart + strumento di riavvio del gateway
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw", // raw | hash
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="Dettagli dei comandi">

- Questo blocco configura le superfici dei comandi. Per il catalogo corrente dei comandi integrati + bundled, vedi [Slash Commands](/it/tools/slash-commands).
- Questa pagina è un **riferimento delle chiavi di configurazione**, non il catalogo completo dei comandi. I comandi posseduti da canali/plugin, come QQ Bot `/bot-ping` `/bot-help` `/bot-logs`, LINE `/card`, device-pair `/pair`, memory `/dreaming`, phone-control `/phone` e Talk `/voice`, sono documentati nelle rispettive pagine del canale/plugin e in [Slash Commands](/it/tools/slash-commands).
- I comandi testuali devono essere messaggi **autonomi** con `/` iniziale.
- `native: "auto"` attiva i comandi nativi per Discord/Telegram, lascia Slack disattivato.
- `nativeSkills: "auto"` attiva i comandi nativi delle Skills per Discord/Telegram, lascia Slack disattivato.
- Override per canale: `channels.discord.commands.native` (bool o `"auto"`). `false` cancella i comandi registrati in precedenza.
- Sovrascrivi la registrazione delle skill native per canale con `channels.<provider>.commands.nativeSkills`.
- `channels.telegram.customCommands` aggiunge voci extra al menu del bot Telegram.
- `bash: true` abilita `! <cmd>` per la shell host. Richiede `tools.elevated.enabled` e il mittente in `tools.elevated.allowFrom.<channel>`.
- `config: true` abilita `/config` (legge/scrive `openclaw.json`). Per i client gateway `chat.send`, le scritture persistenti `/config set|unset` richiedono anche `operator.admin`; il solo accesso in lettura `/config show` resta disponibile per i normali client operator con ambito di scrittura.
- `mcp: true` abilita `/mcp` per la configurazione dei server MCP gestiti da OpenClaw sotto `mcp.servers`.
- `plugins: true` abilita `/plugins` per il rilevamento dei plugin, l'installazione e i controlli di abilitazione/disabilitazione.
- `channels.<provider>.configWrites` regola le mutazioni della configurazione per canale (predefinito: true).
- Per i canali multi-account, anche `channels.<provider>.accounts.<id>.configWrites` regola le scritture che hanno come destinazione quell'account (ad esempio `/allowlist --config --account <id>` o `/config set channels.<provider>.accounts.<id>...`).
- `restart: false` disabilita `/restart` e le azioni dello strumento di riavvio del gateway. Predefinito: `true`.
- `ownerAllowFrom` è l'allowlist esplicita del proprietario per i comandi/strumenti riservati al proprietario. È separata da `allowFrom`.
- `ownerDisplay: "hash"` applica l'hash agli ID del proprietario nel prompt di sistema. Imposta `ownerDisplaySecret` per controllare l'hashing.
- `allowFrom` è per provider. Quando è impostato, è l'**unica** fonte di autorizzazione (le allowlist/l'abbinamento del canale e `useAccessGroups` vengono ignorati).
- `useAccessGroups: false` consente ai comandi di bypassare i criteri dei gruppi di accesso quando `allowFrom` non è impostato.
- Mappa della documentazione dei comandi:
  - catalogo integrato + bundled: [Slash Commands](/it/tools/slash-commands)
  - superfici dei comandi specifiche del canale: [Channels](/it/channels)
  - comandi QQ Bot: [QQ Bot](/it/channels/qqbot)
  - comandi di abbinamento: [Pairing](/it/channels/pairing)
  - comando card di LINE: [LINE](/it/channels/line)
  - Dreaming della memoria: [Dreaming](/it/concepts/dreaming)

</Accordion>

---

## Valori predefiniti dell'agente

### `agents.defaults.workspace`

Predefinito: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

Radice opzionale del repository mostrata nella riga Runtime del prompt di sistema. Se non impostata, OpenClaw la rileva automaticamente risalendo dalla workspace.

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

Allowlist predefinita opzionale di Skills per gli agenti che non impostano
`agents.list[].skills`.

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // eredita github, weather
      { id: "docs", skills: ["docs-search"] }, // sostituisce i valori predefiniti
      { id: "locked-down", skills: [] }, // nessuna skill
    ],
  },
}
```

- Ometti `agents.defaults.skills` per avere Skills senza restrizioni per impostazione predefinita.
- Ometti `agents.list[].skills` per ereditare i valori predefiniti.
- Imposta `agents.list[].skills: []` per nessuna Skills.
- Un elenco non vuoto in `agents.list[].skills` è l'insieme finale per quell'agente; non viene unito ai valori predefiniti.

### `agents.defaults.skipBootstrap`

Disabilita la creazione automatica dei file bootstrap della workspace (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`).

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

Controlla quando i file bootstrap della workspace vengono iniettati nel prompt di sistema. Predefinito: `"always"`.

- `"continuation-skip"`: i turni di continuazione sicura (dopo una risposta completata dell'assistente) saltano la re-iniezione del bootstrap della workspace, riducendo la dimensione del prompt. Le esecuzioni Heartbeat e i tentativi successivi alla Compaction ricostruiscono comunque il contesto.

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

Numero massimo di caratteri per file bootstrap della workspace prima del troncamento. Predefinito: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

Numero massimo totale di caratteri iniettati in tutti i file bootstrap della workspace. Predefinito: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

Controlla il testo di avviso visibile all'agente quando il contesto bootstrap viene troncato.
Predefinito: `"once"`.

- `"off"`: non iniettare mai il testo di avviso nel prompt di sistema.
- `"once"`: inietta l'avviso una volta per ogni firma di troncamento univoca (consigliato).
- `"always"`: inietta l'avviso a ogni esecuzione quando esiste un troncamento.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

Dimensione massima in pixel del lato più lungo dell'immagine nei blocchi immagine del transcript/strumento prima delle chiamate al provider.
Predefinito: `1200`.

Valori più bassi di solito riducono l'uso di vision-token e la dimensione del payload della richiesta per esecuzioni ricche di screenshot.
Valori più alti preservano più dettaglio visivo.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

Fuso orario per il contesto del prompt di sistema (non i timestamp dei messaggi). Se assente, usa il fuso orario dell'host.

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

Formato dell'ora nel prompt di sistema. Predefinito: `auto` (preferenza del sistema operativo).

```json5
{
  agents: { defaults: { timeFormat: "auto" } }, // auto | 12 | 24
}
```

### `agents.defaults.model`

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview"],
      },
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-i2v"],
      },
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4-mini"],
      },
      params: { cacheRetention: "long" }, // parametri predefiniti globali del provider
      embeddedHarness: {
        runtime: "auto", // auto | pi | harness id registrato, ad es. codex
        fallback: "pi", // pi | none
      },
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

- `model`: accetta sia una stringa (`"provider/model"`) sia un oggetto (`{ primary, fallbacks }`).
  - La forma stringa imposta solo il modello primario.
  - La forma oggetto imposta il primario più i modelli di failover ordinati.
- `imageModel`: accetta sia una stringa (`"provider/model"`) sia un oggetto (`{ primary, fallbacks }`).
  - Usato dal percorso dello strumento `image` come configurazione del modello di visione.
  - Usato anche come routing di fallback quando il modello selezionato/predefinito non può accettare input immagine.
- `imageGenerationModel`: accetta sia una stringa (`"provider/model"`) sia un oggetto (`{ primary, fallbacks }`).
  - Usato dalla capability condivisa di generazione immagini e da qualsiasi futura superficie di strumenti/plugin che generi immagini.
  - Valori tipici: `google/gemini-3.1-flash-image-preview` per la generazione nativa di immagini Gemini, `fal/fal-ai/flux/dev` per fal, oppure `openai/gpt-image-1` per OpenAI Images.
  - Se selezioni direttamente un provider/modello, configura anche l'autenticazione/la chiave API del provider corrispondente (ad esempio `GEMINI_API_KEY` o `GOOGLE_API_KEY` per `google/*`, `OPENAI_API_KEY` per `openai/*`, `FAL_KEY` per `fal/*`).
  - Se omesso, `image_generate` può comunque dedurre un provider predefinito supportato da autenticazione. Prova prima il provider predefinito corrente, poi i restanti provider di generazione immagini registrati in ordine di provider-id.
- `musicGenerationModel`: accetta sia una stringa (`"provider/model"`) sia un oggetto (`{ primary, fallbacks }`).
  - Usato dalla capability condivisa di generazione musicale e dallo strumento integrato `music_generate`.
  - Valori tipici: `google/lyria-3-clip-preview`, `google/lyria-3-pro-preview` oppure `minimax/music-2.5+`.
  - Se omesso, `music_generate` può comunque dedurre un provider predefinito supportato da autenticazione. Prova prima il provider predefinito corrente, poi i restanti provider di generazione musicale registrati in ordine di provider-id.
  - Se selezioni direttamente un provider/modello, configura anche l'autenticazione/la chiave API del provider corrispondente.
- `videoGenerationModel`: accetta sia una stringa (`"provider/model"`) sia un oggetto (`{ primary, fallbacks }`).
  - Usato dalla capability condivisa di generazione video e dallo strumento integrato `video_generate`.
  - Valori tipici: `qwen/wan2.6-t2v`, `qwen/wan2.6-i2v`, `qwen/wan2.6-r2v`, `qwen/wan2.6-r2v-flash` oppure `qwen/wan2.7-r2v`.
  - Se omesso, `video_generate` può comunque dedurre un provider predefinito supportato da autenticazione. Prova prima il provider predefinito corrente, poi i restanti provider di generazione video registrati in ordine di provider-id.
  - Se selezioni direttamente un provider/modello, configura anche l'autenticazione/la chiave API del provider corrispondente.
  - Il provider bundled di generazione video Qwen supporta fino a 1 video in uscita, 1 immagine in ingresso, 4 video in ingresso, durata di 10 secondi e opzioni a livello provider `size`, `aspectRatio`, `resolution`, `audio` e `watermark`.
- `pdfModel`: accetta sia una stringa (`"provider/model"`) sia un oggetto (`{ primary, fallbacks }`).
  - Usato dallo strumento `pdf` per il routing del modello.
  - Se omesso, lo strumento PDF usa come fallback `imageModel`, poi il modello risolto della sessione/predefinito.
- `pdfMaxBytesMb`: limite predefinito di dimensione PDF per lo strumento `pdf` quando `maxBytesMb` non viene passato al momento della chiamata.
- `pdfMaxPages`: numero massimo predefinito di pagine considerate dalla modalità di fallback di estrazione nello strumento `pdf`.
- `verboseDefault`: livello verboso predefinito per gli agenti. Valori: `"off"`, `"on"`, `"full"`. Predefinito: `"off"`.
- `elevatedDefault`: livello predefinito di output elevato per gli agenti. Valori: `"off"`, `"on"`, `"ask"`, `"full"`. Predefinito: `"on"`.
- `model.primary`: formato `provider/model` (ad es. `openai/gpt-5.4`). Se ometti il provider, OpenClaw prova prima un alias, poi una corrispondenza univoca del provider configurato per quell'esatto model id, e solo dopo torna al provider predefinito configurato (comportamento di compatibilità deprecato, quindi è preferibile `provider/model` esplicito). Se quel provider non espone più il modello predefinito configurato, OpenClaw ripiega sul primo provider/modello configurato invece di mostrare un valore predefinito obsoleto di un provider rimosso.
- `models`: il catalogo di modelli configurato e l'allowlist per `/model`. Ogni voce può includere `alias` (scorciatoia) e `params` (specifici del provider, ad esempio `temperature`, `maxTokens`, `cacheRetention`, `context1m`).
- `params`: parametri predefiniti globali del provider applicati a tutti i modelli. Si impostano in `agents.defaults.params` (ad es. `{ cacheRetention: "long" }`).
- Precedenza di unione di `params` (config): `agents.defaults.params` (base globale) è sovrascritto da `agents.defaults.models["provider/model"].params` (per modello), poi `agents.list[].params` (ID agente corrispondente) sovrascrive per chiave. Vedi [Prompt Caching](/it/reference/prompt-caching) per i dettagli.
- `embeddedHarness`: criterio predefinito di runtime embedded a basso livello per l'agente. Usa `runtime: "auto"` per lasciare che gli harness dei plugin registrati rivendichino i modelli supportati, `runtime: "pi"` per forzare l'harness PI integrato, oppure un id harness registrato come `runtime: "codex"`. Imposta `fallback: "none"` per disabilitare il fallback automatico a Pi.
- Gli scrittori di configurazione che modificano questi campi (ad esempio `/models set`, `/models set-image` e i comandi di aggiunta/rimozione fallback) salvano la forma oggetto canonica e preservano gli elenchi fallback esistenti quando possibile.
- `maxConcurrent`: numero massimo di esecuzioni parallele degli agenti tra le sessioni (ogni sessione resta comunque serializzata). Predefinito: 4.

### `agents.defaults.embeddedHarness`

`embeddedHarness` controlla quale esecutore di basso livello esegue i turni embedded dell'agente.
La maggior parte dei deployment dovrebbe mantenere il valore predefinito `{ runtime: "auto", fallback: "pi" }`.
Usalo quando un plugin attendibile fornisce un harness nativo, come l'harness bundled del server app Codex.

```json5
{
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

- `runtime`: `"auto"`, `"pi"` o un id harness plugin registrato. Il plugin bundled Codex registra `codex`.
- `fallback`: `"pi"` o `"none"`. `"pi"` mantiene l'harness PI integrato come fallback di compatibilità. `"none"` fa sì che una selezione di harness plugin mancante o non supportata fallisca invece di usare silenziosamente Pi.
- Override da ambiente: `OPENCLAW_AGENT_RUNTIME=<id|auto|pi>` sovrascrive `runtime`; `OPENCLAW_AGENT_HARNESS_FALLBACK=none` disabilita il fallback a Pi per quel processo.
- Per deployment solo-Codex, imposta `model: "codex/gpt-5.4"`, `embeddedHarness.runtime: "codex"` e `embeddedHarness.fallback: "none"`.
- Questo controlla solo l'harness di chat embedded. Generazione media, visione, PDF, musica, video e TTS continuano a usare le rispettive impostazioni provider/modello.

**Scorciatoie alias integrate** (si applicano solo quando il modello è in `agents.defaults.models`):

| Alias               | Modello                               |
| ------------------- | ------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`           |
| `sonnet`            | `anthropic/claude-sonnet-4-6`         |
| `gpt`               | `openai/gpt-5.4`                      |
| `gpt-mini`          | `openai/gpt-5.4-mini`                 |
| `gpt-nano`          | `openai/gpt-5.4-nano`                 |
| `gemini`            | `google/gemini-3.1-pro-preview`       |
| `gemini-flash`      | `google/gemini-3-flash-preview`       |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

Gli alias configurati da te hanno sempre la precedenza sui valori predefiniti.

I modelli Z.AI GLM-4.x abilitano automaticamente la modalità thinking a meno che tu non imposti `--thinking off` o definisca tu stesso `agents.defaults.models["zai/<model>"].params.thinking`.
I modelli Z.AI abilitano `tool_stream` per impostazione predefinita per lo streaming delle chiamate agli strumenti. Imposta `agents.defaults.models["zai/<model>"].params.tool_stream` su `false` per disabilitarlo.
I modelli Anthropic Claude 4.6 usano per impostazione predefinita il thinking `adaptive` quando non è impostato alcun livello di thinking esplicito.

### `agents.defaults.cliBackends`

Backend CLI opzionali per esecuzioni di fallback solo testuali (senza chiamate a strumenti). Utili come backup quando i provider API falliscono.

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          modelArg: "--model",
          sessionArg: "--session",
          sessionMode: "existing",
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
        },
      },
    },
  },
}
```

- I backend CLI sono orientati prima di tutto al testo; gli strumenti sono sempre disabilitati.
- Le sessioni sono supportate quando `sessionArg` è impostato.
- Il pass-through delle immagini è supportato quando `imageArg` accetta percorsi di file.

### `agents.defaults.systemPromptOverride`

Sostituisce l'intero prompt di sistema assemblato da OpenClaw con una stringa fissa. Impostalo a livello predefinito (`agents.defaults.systemPromptOverride`) o per agente (`agents.list[].systemPromptOverride`). I valori per agente hanno la precedenza; un valore vuoto o composto solo da spazi viene ignorato. Utile per esperimenti controllati sul prompt.

```json5
{
  agents: {
    defaults: {
      systemPromptOverride: "Sei un assistente utile.",
    },
  },
}
```

### `agents.defaults.heartbeat`

Esecuzioni periodiche Heartbeat.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m disabilita
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        includeSystemPromptSection: true, // predefinito: true; false omette la sezione Heartbeat dal prompt di sistema
        lightContext: false, // predefinito: false; true mantiene solo HEARTBEAT.md dai file bootstrap della workspace
        isolatedSession: false, // predefinito: false; true esegue ogni heartbeat in una sessione nuova (senza cronologia conversazionale)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (predefinito) | block
        target: "none", // predefinito: none | opzioni: last | whatsapp | telegram | discord | ...
        prompt: "Leggi HEARTBEAT.md se esiste...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
        timeoutSeconds: 45,
      },
    },
  },
}
```

- `every`: stringa di durata (ms/s/m/h). Predefinito: `30m` (autenticazione con chiave API) oppure `1h` (autenticazione OAuth). Imposta `0m` per disabilitare.
- `includeSystemPromptSection`: quando è false, omette la sezione Heartbeat dal prompt di sistema e salta l'iniezione di `HEARTBEAT.md` nel contesto bootstrap. Predefinito: `true`.
- `suppressToolErrorWarnings`: quando è true, sopprime i payload di avviso sugli errori degli strumenti durante le esecuzioni Heartbeat.
- `timeoutSeconds`: tempo massimo in secondi consentito per un turno agente Heartbeat prima che venga interrotto. Se non impostato, usa `agents.defaults.timeoutSeconds`.
- `directPolicy`: criterio di consegna diretta/DM. `allow` (predefinito) consente la consegna a target diretti. `block` sopprime la consegna a target diretti ed emette `reason=dm-blocked`.
- `lightContext`: quando è true, le esecuzioni Heartbeat usano un contesto bootstrap leggero e mantengono solo `HEARTBEAT.md` tra i file bootstrap della workspace.
- `isolatedSession`: quando è true, ogni heartbeat viene eseguito in una sessione nuova senza cronologia conversazionale precedente. Stesso schema di isolamento del Cron `sessionTarget: "isolated"`. Riduce il costo in token per heartbeat da ~100K a ~2-5K token.
- Per agente: imposta `agents.list[].heartbeat`. Quando un qualsiasi agente definisce `heartbeat`, **solo quegli agenti** eseguono heartbeat.
- Gli heartbeat eseguono turni completi dell'agente: intervalli più brevi consumano più token.

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        provider: "my-provider", // id di un plugin provider di Compaction registrato (opzionale)
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "Preserva esattamente gli ID di deployment, gli ID ticket e le coppie host:port.", // usato quando identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] disabilita la re-iniezione
        model: "openrouter/anthropic/claude-sonnet-4-6", // override opzionale del modello solo per la Compaction
        notifyUser: true, // invia un breve avviso quando inizia la Compaction (predefinito: false)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "La sessione si sta avvicinando alla Compaction. Archivia ora i ricordi durevoli.",
          prompt: "Scrivi eventuali note durature in memory/YYYY-MM-DD.md; rispondi con il token silenzioso esatto NO_REPLY se non c'è nulla da archiviare.",
        },
      },
    },
  },
}
```

- `mode`: `default` oppure `safeguard` (riepilogo suddiviso in blocchi per cronologie lunghe). Vedi [Compaction](/it/concepts/compaction).
- `provider`: id di un plugin provider di Compaction registrato. Quando è impostato, viene chiamato `summarize()` del provider invece del riepilogo LLM integrato. In caso di errore torna al comportamento integrato. Impostare un provider forza `mode: "safeguard"`. Vedi [Compaction](/it/concepts/compaction).
- `timeoutSeconds`: numero massimo di secondi consentiti per una singola operazione di Compaction prima che OpenClaw la interrompa. Predefinito: `900`.
- `identifierPolicy`: `strict` (predefinito), `off` oppure `custom`. `strict` antepone linee guida integrate per la conservazione di identificatori opachi durante il riepilogo della Compaction.
- `identifierInstructions`: testo personalizzato opzionale per la conservazione degli identificatori usato quando `identifierPolicy=custom`.
- `postCompactionSections`: nomi opzionali di sezioni H2/H3 di AGENTS.md da reiniettare dopo la Compaction. Predefinito: `["Session Startup", "Red Lines"]`; imposta `[]` per disabilitare la reiniezione. Quando non è impostato o è impostato esplicitamente su quella coppia predefinita, le intestazioni legacy `Every Session`/`Safety` sono accettate anche come fallback legacy.
- `model`: override opzionale `provider/model-id` solo per il riepilogo della Compaction. Usalo quando la sessione principale deve mantenere un modello ma i riepiloghi di Compaction devono essere eseguiti con un altro; se non impostato, la Compaction usa il modello primario della sessione.
- `notifyUser`: quando `true`, invia un breve avviso all'utente quando inizia la Compaction (ad esempio, "Compattazione del contesto..."). Disabilitato per impostazione predefinita per mantenere silenziosa la Compaction.
- `memoryFlush`: turno agentico silenzioso prima della Compaction automatica per archiviare ricordi durevoli. Viene saltato quando la workspace è in sola lettura.

### `agents.defaults.contextPruning`

Rimuove **i vecchi risultati degli strumenti** dal contesto in memoria prima dell'invio all'LLM. **Non** modifica la cronologia della sessione su disco.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // durata (ms/s/m/h), unità predefinita: minuti
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Contenuto del vecchio risultato dello strumento cancellato]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="Comportamento della modalità cache-ttl">

- `mode: "cache-ttl"` abilita i passaggi di pruning.
- `ttl` controlla ogni quanto il pruning può essere eseguito di nuovo (dopo l'ultimo accesso alla cache).
- Il pruning prima applica il soft-trim ai risultati degli strumenti troppo grandi, poi, se necessario, cancella in modo completo i risultati degli strumenti più vecchi.

**Soft-trim** conserva l'inizio + la fine e inserisce `...` nel mezzo.

**Hard-clear** sostituisce l'intero risultato dello strumento con il segnaposto.

Note:

- I blocchi immagine non vengono mai tagliati/cancellati.
- I rapporti sono basati sui caratteri (approssimativi), non su conteggi esatti di token.
- Se esistono meno di `keepLastAssistants` messaggi dell'assistente, il pruning viene saltato.

</Accordion>

Vedi [Session Pruning](/it/concepts/session-pruning) per i dettagli sul comportamento.

### Streaming a blocchi

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (usa minMs/maxMs)
    },
  },
}
```

- I canali non Telegram richiedono `*.blockStreaming: true` esplicito per abilitare le risposte a blocchi.
- Override per canale: `channels.<channel>.blockStreamingCoalesce` (e varianti per account). Signal/Slack/Discord/Google Chat usano come predefinito `minChars: 1500`.
- `humanDelay`: pausa casuale tra le risposte a blocchi. `natural` = 800–2500ms. Override per agente: `agents.list[].humanDelay`.

Vedi [Streaming](/it/concepts/streaming) per i dettagli su comportamento + suddivisione in blocchi.

### Indicatori di digitazione

```json5
{
  agents: {
    defaults: {
      typingMode: "instant", // never | instant | thinking | message
      typingIntervalSeconds: 6,
    },
  },
}
```

- Predefiniti: `instant` per chat dirette/menzioni, `message` per chat di gruppo senza menzione.
- Override per sessione: `session.typingMode`, `session.typingIntervalSeconds`.

Vedi [Typing Indicators](/it/concepts/typing-indicators).

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

Sandboxing opzionale per l'agente embedded. Vedi [Sandboxing](/it/gateway/sandboxing) per la guida completa.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        backend: "docker", // docker | ssh | openshell
        scope: "agent", // session | agent | shared
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          containerPrefix: "openclaw-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256,
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "openclaw-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
          binds: ["/home/user/source:/source:rw"],
        },
        ssh: {
          target: "user@gateway-host:22",
          command: "ssh",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // Sono supportati anche SecretRef / contenuti inline:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          network: "openclaw-sandbox-browser",
          cdpPort: 9222,
          cdpSourceRange: "172.21.0.1/32",
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          autoStart: true,
          autoStartTimeoutMs: 12000,
        },
        prune: {
          idleHours: 24,
          maxAgeDays: 7,
        },
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "apply_patch",
          "sessions_list",
          "sessions_history",
          "sessions_send",
          "sessions_spawn",
          "session_status",
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"],
      },
    },
  },
}
```

<Accordion title="Dettagli del sandbox">

**Backend:**

- `docker`: runtime Docker locale (predefinito)
- `ssh`: runtime remoto generico supportato da SSH
- `openshell`: runtime OpenShell

Quando viene selezionato `backend: "openshell"`, le impostazioni specifiche del runtime si spostano in
`plugins.entries.openshell.config`.

**Configurazione del backend SSH:**

- `target`: target SSH nel formato `user@host[:port]`
- `command`: comando del client SSH (predefinito: `ssh`)
- `workspaceRoot`: radice remota assoluta usata per le workspace per scope
- `identityFile` / `certificateFile` / `knownHostsFile`: file locali esistenti passati a OpenSSH
- `identityData` / `certificateData` / `knownHostsData`: contenuti inline o SecretRef che OpenClaw materializza in file temporanei a runtime
- `strictHostKeyChecking` / `updateHostKeys`: parametri del criterio delle chiavi host di OpenSSH

**Precedenza di autenticazione SSH:**

- `identityData` ha la precedenza su `identityFile`
- `certificateData` ha la precedenza su `certificateFile`
- `knownHostsData` ha la precedenza su `knownHostsFile`
- I valori `*Data` supportati da SecretRef vengono risolti dallo snapshot runtime attivo dei segreti prima dell'avvio della sessione sandbox

**Comportamento del backend SSH:**

- inizializza la workspace remota una sola volta dopo la creazione o ricreazione
- poi mantiene canonica la workspace SSH remota
- instrada `exec`, gli strumenti per i file e i percorsi dei media tramite SSH
- non sincronizza automaticamente di nuovo sull'host le modifiche remote
- non supporta container browser nel sandbox

**Accesso alla workspace:**

- `none`: workspace sandbox per scope sotto `~/.openclaw/sandboxes`
- `ro`: workspace sandbox in `/workspace`, workspace dell'agente montata in sola lettura in `/agent`
- `rw`: workspace dell'agente montata in lettura/scrittura in `/workspace`

**Scope:**

- `session`: container + workspace per sessione
- `agent`: un container + workspace per agente (predefinito)
- `shared`: container e workspace condivisi (nessun isolamento tra sessioni)

**Configurazione del plugin OpenShell:**

```json5
{
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          mode: "mirror", // mirror | remote
          from: "openclaw",
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
          gateway: "lab", // opzionale
          gatewayEndpoint: "https://lab.example", // opzionale
          policy: "strict", // id criterio OpenShell opzionale
          providers: ["openai"], // opzionale
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**Modalità OpenShell:**

- `mirror`: inizializza il remoto dal locale prima di exec, sincronizza di ritorno dopo exec; la workspace locale resta canonica
- `remote`: inizializza il remoto una volta quando il sandbox viene creato, poi mantiene canonica la workspace remota

In modalità `remote`, le modifiche locali sull'host effettuate fuori da OpenClaw non vengono sincronizzate automaticamente nel sandbox dopo il passaggio di inizializzazione.
Il trasporto usa SSH verso il sandbox OpenShell, ma il plugin gestisce il ciclo di vita del sandbox e l'eventuale sincronizzazione mirror.

**`setupCommand`** viene eseguito una volta dopo la creazione del container (tramite `sh -lc`). Richiede uscita di rete, root scrivibile, utente root.

**I container usano per impostazione predefinita `network: "none"`** — imposta `"bridge"` (o una rete bridge personalizzata) se l'agente necessita di accesso in uscita.
`"host"` è bloccato. `"container:<id>"` è bloccato per impostazione predefinita a meno che tu non imposti esplicitamente
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` (break-glass).

**Gli allegati in ingresso** vengono preparati in `media/inbound/*` nella workspace attiva.

**`docker.binds`** monta directory host aggiuntive; i bind globali e per agente vengono uniti.

**Browser sandboxed** (`sandbox.browser.enabled`): Chromium + CDP in un container. L'URL noVNC viene iniettata nel prompt di sistema. Non richiede `browser.enabled` in `openclaw.json`.
L'accesso osservatore noVNC usa per impostazione predefinita l'autenticazione VNC e OpenClaw emette un URL con token a breve durata (invece di esporre la password nell'URL condiviso).

- `allowHostControl: false` (predefinito) impedisce alle sessioni sandboxed di puntare al browser dell'host.
- `network` ha come predefinito `openclaw-sandbox-browser` (rete bridge dedicata). Imposta `bridge` solo quando vuoi esplicitamente connettività bridge globale.
- `cdpSourceRange` limita facoltativamente l'ingresso CDP al bordo del container a un intervallo CIDR (ad esempio `172.21.0.1/32`).
- `sandbox.browser.binds` monta directory host aggiuntive solo nel container del browser sandboxed. Quando è impostato (incluso `[]`), sostituisce `docker.binds` per il container del browser.
- I valori predefiniti di avvio sono definiti in `scripts/sandbox-browser-entrypoint.sh` e ottimizzati per host container:
  - `--remote-debugging-address=127.0.0.1`
  - `--remote-debugging-port=<derivato da OPENCLAW_BROWSER_CDP_PORT>`
  - `--user-data-dir=${HOME}/.chrome`
  - `--no-first-run`
  - `--no-default-browser-check`
  - `--disable-3d-apis`
  - `--disable-gpu`
  - `--disable-software-rasterizer`
  - `--disable-dev-shm-usage`
  - `--disable-background-networking`
  - `--disable-features=TranslateUI`
  - `--disable-breakpad`
  - `--disable-crash-reporter`
  - `--renderer-process-limit=2`
  - `--no-zygote`
  - `--metrics-recording-only`
  - `--disable-extensions` (abilitato per impostazione predefinita)
  - `--disable-3d-apis`, `--disable-software-rasterizer` e `--disable-gpu` sono abilitati per impostazione predefinita e possono essere disabilitati con `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` se l'uso di WebGL/3D lo richiede.
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` riabilita le estensioni se il tuo flusso di lavoro ne dipende.
  - `--renderer-process-limit=2` può essere modificato con `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`; imposta `0` per usare il limite di processi predefinito di Chromium.
  - più `--no-sandbox` e `--disable-setuid-sandbox` quando `noSandbox` è abilitato.
  - I valori predefiniti sono la baseline dell'immagine container; usa un'immagine browser personalizzata con un entrypoint personalizzato per cambiare i valori predefiniti del container.

</Accordion>

Il sandboxing del browser e `sandbox.docker.binds` sono disponibili solo per Docker.

Crea le immagini:

```bash
scripts/sandbox-setup.sh           # immagine sandbox principale
scripts/sandbox-browser-setup.sh   # immagine browser opzionale
```

### `agents.list` (override per agente)

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // oppure { primary, fallbacks }
        thinkingDefault: "high", // override per agente del livello di thinking
        reasoningDefault: "on", // override per agente della visibilità del reasoning
        fastModeDefault: false, // override per agente della modalità veloce
        embeddedHarness: { runtime: "auto", fallback: "pi" },
        params: { cacheRetention: "none" }, // sovrascrive per chiave i params del defaults.models corrispondente
        skills: ["docs-search"], // sostituisce agents.defaults.skills quando impostato
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
        subagents: { allowAgents: ["*"] },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        },
      },
    ],
  },
}
```

- `id`: ID agente stabile (obbligatorio).
- `default`: quando ne sono impostati più di uno, vince il primo (viene registrato un avviso). Se non ne è impostato nessuno, il valore predefinito è la prima voce dell'elenco.
- `model`: la forma stringa sovrascrive solo `primary`; la forma oggetto `{ primary, fallbacks }` sovrascrive entrambi (`[]` disabilita i fallback globali). I job Cron che sovrascrivono solo `primary` continuano a ereditare i fallback predefiniti a meno che tu non imposti `fallbacks: []`.
- `params`: parametri di stream per agente uniti sopra la voce del modello selezionato in `agents.defaults.models`. Usalo per override specifici dell'agente come `cacheRetention`, `temperature` o `maxTokens` senza duplicare l'intero catalogo modelli.
- `skills`: allowlist opzionale di Skills per agente. Se omessa, l'agente eredita `agents.defaults.skills` quando è impostato; un elenco esplicito sostituisce i valori predefiniti invece di unirsi a essi, e `[]` significa nessuna Skills.
- `thinkingDefault`: livello thinking predefinito opzionale per agente (`off | minimal | low | medium | high | xhigh | adaptive`). Sovrascrive `agents.defaults.thinkingDefault` per questo agente quando non è impostato alcun override per messaggio o sessione.
- `reasoningDefault`: visibilità predefinita opzionale del reasoning per agente (`on | off | stream`). Si applica quando non è impostato alcun override del reasoning per messaggio o sessione.
- `fastModeDefault`: valore predefinito opzionale per agente per la modalità veloce (`true | false`). Si applica quando non è impostato alcun override della modalità veloce per messaggio o sessione.
- `embeddedHarness`: override opzionale per agente del criterio dell'harness di basso livello. Usa `{ runtime: "codex", fallback: "none" }` per rendere un agente solo-Codex mentre gli altri agenti mantengono il fallback predefinito a Pi.
- `runtime`: descrittore runtime opzionale per agente. Usa `type: "acp"` con i valori predefiniti di `runtime.acp` (`agent`, `backend`, `mode`, `cwd`) quando l'agente deve usare per impostazione predefinita sessioni harness ACP.
- `identity.avatar`: percorso relativo alla workspace, URL `http(s)` o URI `data:`.
- `identity` deriva i valori predefiniti: `ackReaction` da `emoji`, `mentionPatterns` da `name`/`emoji`.
- `subagents.allowAgents`: allowlist di ID agente per `sessions_spawn` (`["*"]` = qualsiasi; predefinito: solo lo stesso agente).
- Protezione ereditarietà sandbox: se la sessione richiedente è sandboxed, `sessions_spawn` rifiuta i target che verrebbero eseguiti senza sandbox.
- `subagents.requireAgentId`: quando è true, blocca le chiamate `sessions_spawn` che omettono `agentId` (forza la selezione esplicita del profilo; predefinito: false).

---

## Routing multi-agente

Esegui più agenti isolati all'interno di un Gateway. Vedi [Multi-Agent](/it/concepts/multi-agent).

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

### Campi di corrispondenza dei binding

- `type` (opzionale): `route` per il routing normale (se manca, il tipo predefinito è route), `acp` per i binding persistenti delle conversazioni ACP.
- `match.channel` (obbligatorio)
- `match.accountId` (opzionale; `*` = qualsiasi account; omesso = account predefinito)
- `match.peer` (opzionale; `{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (opzionale; specifico del canale)
- `acp` (opzionale; solo per voci `type: "acp"`): `{ mode, label, cwd, backend }`

**Ordine di corrispondenza deterministico:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (esatto, senza peer/guild/team)
5. `match.accountId: "*"` (a livello di canale)
6. Agente predefinito

All'interno di ogni livello, vince la prima voce `bindings` corrispondente.

Per le voci `type: "acp"`, OpenClaw risolve in base all'identità esatta della conversazione (`match.channel` + account + `match.peer.id`) e non usa l'ordine a livelli dei binding di route sopra.

### Profili di accesso per agente

<Accordion title="Accesso completo (nessun sandbox)">

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="Strumenti + workspace in sola lettura">

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
        tools: {
          allow: [
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="Nessun accesso al filesystem (solo messaggistica)">

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "none" },
        tools: {
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
            "gateway",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

</Accordion>

Vedi [Multi-Agent Sandbox & Tools](/it/tools/multi-agent-sandbox-tools) per i dettagli sulla precedenza.

---

## Sessione

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main", // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily", // daily | idle
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    parentForkMaxTokens: 100000, // salta il fork del thread padre sopra questo numero di token (0 disabilita)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // durata o false
      maxDiskBytes: "500mb", // budget rigido opzionale
      highWaterBytes: "400mb", // target opzionale per la pulizia
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // auto-unfocus predefinito per inattività in ore (`0` disabilita)
      maxAgeHours: 0, // età massima rigida predefinita in ore (`0` disabilita)
    },
    mainKey: "main", // legacy (il runtime usa sempre "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="Dettagli dei campi della sessione">

- **`scope`**: strategia base di raggruppamento delle sessioni per i contesti di chat di gruppo.
  - `per-sender` (predefinito): ogni mittente ottiene una sessione isolata all'interno del contesto del canale.
  - `global`: tutti i partecipanti in un contesto di canale condividono una singola sessione (usalo solo quando è previsto un contesto condiviso).
- **`dmScope`**: come vengono raggruppati i DM.
  - `main`: tutti i DM condividono la sessione principale.
  - `per-peer`: isola per ID mittente tra i canali.
  - `per-channel-peer`: isola per canale + mittente (consigliato per inbox multiutente).
  - `per-account-channel-peer`: isola per account + canale + mittente (consigliato per multi-account).
- **`identityLinks`**: mappa gli ID canonici ai peer con prefisso provider per la condivisione delle sessioni tra canali.
- **`reset`**: criterio di reset principale. `daily` resetta all'ora locale `atHour`; `idle` resetta dopo `idleMinutes`. Quando sono configurati entrambi, prevale quello che scade per primo.
- **`resetByType`**: override per tipo (`direct`, `group`, `thread`). Il legacy `dm` è accettato come alias di `direct`.
- **`parentForkMaxTokens`**: `totalTokens` massimo consentito per la sessione padre quando si crea una sessione thread derivata (predefinito `100000`).
  - Se il `totalTokens` del padre supera questo valore, OpenClaw avvia una nuova sessione thread invece di ereditare la cronologia del transcript padre.
  - Imposta `0` per disabilitare questa protezione e consentire sempre il fork del padre.
- **`mainKey`**: campo legacy. Il runtime usa sempre `"main"` per il bucket principale delle chat dirette.
- **`agentToAgent.maxPingPongTurns`**: numero massimo di turni di risposta reciproca tra agenti durante gli scambi agent-to-agent (intero, intervallo: `0`–`5`). `0` disabilita la catena ping-pong.
- **`sendPolicy`**: corrisponde in base a `channel`, `chatType` (`direct|group|channel`, con alias legacy `dm`), `keyPrefix` o `rawKeyPrefix`. Il primo deny prevale.
- **`maintenance`**: controlli di pulizia + retention dello store delle sessioni.
  - `mode`: `warn` emette solo avvisi; `enforce` applica la pulizia.
  - `pruneAfter`: soglia temporale per le voci obsolete (predefinito `30d`).
  - `maxEntries`: numero massimo di voci in `sessions.json` (predefinito `500`).
  - `rotateBytes`: ruota `sessions.json` quando supera questa dimensione (predefinito `10mb`).
  - `resetArchiveRetention`: retention per gli archivi di transcript `*.reset.<timestamp>`. Il valore predefinito è `pruneAfter`; imposta `false` per disabilitare.
  - `maxDiskBytes`: budget disco opzionale della directory delle sessioni. In modalità `warn` registra avvisi; in modalità `enforce` rimuove prima gli artefatti/sessioni più vecchi.
  - `highWaterBytes`: target opzionale dopo la pulizia del budget. Il valore predefinito è `80%` di `maxDiskBytes`.
- **`threadBindings`**: valori predefiniti globali per le funzionalità di sessione associate ai thread.
  - `enabled`: interruttore predefinito principale (i provider possono sovrascriverlo; Discord usa `channels.discord.threadBindings.enabled`)
  - `idleHours`: auto-unfocus predefinito per inattività in ore (`0` disabilita; i provider possono sovrascrivere)
  - `maxAgeHours`: età massima rigida predefinita in ore (`0` disabilita; i provider possono sovrascrivere)

</Accordion>

---

## Messaggi

```json5
{
  messages: {
    responsePrefix: "🦞", // oppure "auto"
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // group-mentions | group-all | direct | all
    removeAckAfterReply: false,
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog | steer+backlog | queue | interrupt
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
      },
    },
    inbound: {
      debounceMs: 2000, // 0 disabilita
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### Prefisso di risposta

Override per canale/account: `channels.<channel>.responsePrefix`, `channels.<channel>.accounts.<id>.responsePrefix`.

Risoluzione (vince il più specifico): account → canale → globale. `""` disabilita e interrompe la cascata. `"auto"` deriva `[{identity.name}]`.

**Variabili di template:**

| Variabile         | Descrizione               | Esempio                     |
| ----------------- | ------------------------- | --------------------------- |
| `{model}`         | Nome breve del modello    | `claude-opus-4-6`           |
| `{modelFull}`     | Identificatore completo del modello | `anthropic/claude-opus-4-6` |
| `{provider}`      | Nome del provider         | `anthropic`                 |
| `{thinkingLevel}` | Livello thinking corrente | `high`, `low`, `off`        |
| `{identity.name}` | Nome dell'identità agente | (uguale a `"auto"`)         |

Le variabili non distinguono tra maiuscole e minuscole. `{think}` è un alias di `{thinkingLevel}`.

### Reazione di conferma

- Per impostazione predefinita usa `identity.emoji` dell'agente attivo, altrimenti `"👀"`. Imposta `""` per disabilitare.
- Override per canale: `channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`.
- Ordine di risoluzione: account → canale → `messages.ackReaction` → fallback dell'identità.
- Scope: `group-mentions` (predefinito), `group-all`, `direct`, `all`.
- `removeAckAfterReply`: rimuove la conferma dopo la risposta su Slack, Discord e Telegram.
- `messages.statusReactions.enabled`: abilita le reazioni di stato del ciclo di vita su Slack, Discord e Telegram.
  Su Slack e Discord, se non impostato mantiene abilitate le reazioni di stato quando le reazioni di conferma sono attive.
  Su Telegram, impostalo esplicitamente su `true` per abilitare le reazioni di stato del ciclo di vita.

### Debounce in ingresso

Raggruppa i messaggi testuali rapidi dello stesso mittente in un singolo turno dell'agente. I media/gli allegati vengono scaricati subito. I comandi di controllo bypassano il debounce.

### TTS (text-to-speech)

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: { enabled: true },
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0,
        },
      },
      openai: {
        apiKey: "openai_api_key",
        baseUrl: "https://api.openai.com/v1",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

- `auto` controlla la modalità auto-TTS predefinita: `off`, `always`, `inbound` oppure `tagged`. `/tts on|off` può sovrascrivere le preferenze locali e `/tts status` mostra lo stato effettivo.
- `summaryModel` sovrascrive `agents.defaults.model.primary` per il riepilogo automatico.
- `modelOverrides` è abilitato per impostazione predefinita; `modelOverrides.allowProvider` ha come predefinito `false` (opt-in).
- Le chiavi API usano come fallback `ELEVENLABS_API_KEY`/`XI_API_KEY` e `OPENAI_API_KEY`.
- `openai.baseUrl` sovrascrive l'endpoint TTS di OpenAI. L'ordine di risoluzione è config, poi `OPENAI_TTS_BASE_URL`, poi `https://api.openai.com/v1`.
- Quando `openai.baseUrl` punta a un endpoint non OpenAI, OpenClaw lo tratta come un server TTS compatibile con OpenAI e allenta la convalida di modello/voce.

---

## Talk

Valori predefiniti per la modalità Talk (macOS/iOS/Android).

```json5
{
  talk: {
    provider: "elevenlabs",
    providers: {
      elevenlabs: {
        voiceId: "elevenlabs_voice_id",
        voiceAliases: {
          Clawd: "EXAVITQu4vr4xnSDxMaL",
          Roger: "CwhRBWXzGAHq8TQ4Fs17",
        },
        modelId: "eleven_v3",
        outputFormat: "mp3_44100_128",
        apiKey: "elevenlabs_api_key",
      },
    },
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

- `talk.provider` deve corrispondere a una chiave in `talk.providers` quando sono configurati più provider Talk.
- Le chiavi Talk flat legacy (`talk.voiceId`, `talk.voiceAliases`, `talk.modelId`, `talk.outputFormat`, `talk.apiKey`) sono solo per compatibilità e vengono migrate automaticamente in `talk.providers.<provider>`.
- Gli ID voce usano come fallback `ELEVENLABS_VOICE_ID` o `SAG_VOICE_ID`.
- `providers.*.apiKey` accetta stringhe in chiaro o oggetti SecretRef.
- Il fallback `ELEVENLABS_API_KEY` si applica solo quando non è configurata alcuna chiave API Talk.
- `providers.*.voiceAliases` consente alle direttive Talk di usare nomi amichevoli.
- `silenceTimeoutMs` controlla quanto tempo la modalità Talk attende dopo il silenzio dell'utente prima di inviare la trascrizione. Se non impostato, mantiene la finestra di pausa predefinita della piattaforma (`700 ms su macOS e Android, 900 ms su iOS`).

---

## Strumenti

### Profili degli strumenti

`tools.profile` imposta un'allowlist di base prima di `tools.allow`/`tools.deny`:

L'onboarding locale imposta per le nuove configurazioni locali `tools.profile: "coding"` quando non è definito (i profili espliciti esistenti vengono preservati).

| Profilo     | Include                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | solo `session_status`                                                                                                           |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                       |
| `full`      | Nessuna restrizione (uguale a non impostato)                                                                                    |

### Gruppi di strumenti

| Gruppo             | Strumenti                                                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`, `process`, `code_execution` (`bash` è accettato come alias di `exec`)                                          |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                  |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                                                           |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                   |
| `group:ui`         | `browser`, `canvas`                                                                                                     |
| `group:automation` | `cron`, `gateway`                                                                                                       |
| `group:messaging`  | `message`                                                                                                               |
| `group:nodes`      | `nodes`                                                                                                                 |
| `group:agents`     | `agents_list`                                                                                                           |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                      |
| `group:openclaw`   | Tutti gli strumenti integrati (esclude i plugin provider)                                                               |

### `tools.allow` / `tools.deny`

Criterio globale di allow/deny degli strumenti (deny prevale). Non distingue tra maiuscole e minuscole, supporta i caratteri jolly `*`. Applicato anche quando il sandbox Docker è disattivato.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

Limita ulteriormente gli strumenti per provider o modelli specifici. Ordine: profilo base → profilo provider → allow/deny.

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.4": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

### `tools.elevated`

Controlla l'accesso exec elevato fuori dal sandbox:

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["1234567890123", "987654321098765432"],
      },
    },
  },
}
```

- L'override per agente (`agents.list[].tools.elevated`) può solo restringere ulteriormente.
- `/elevated on|off|ask|full` memorizza lo stato per sessione; le direttive inline si applicano a un singolo messaggio.
- `exec` elevato bypassa il sandbox e usa il percorso di escape configurato (`gateway` per impostazione predefinita, oppure `node` quando il target exec è `node`).

### `tools.exec`

```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      notifyOnExitEmptySuccess: false,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.4"],
      },
    },
  },
}
```

### `tools.loopDetection`

I controlli di sicurezza sui loop degli strumenti sono **disabilitati per impostazione predefinita**. Imposta `enabled: true` per attivare il rilevamento.
Le impostazioni possono essere definite globalmente in `tools.loopDetection` e sovrascritte per agente in `agents.list[].tools.loopDetection`.

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

- `historySize`: cronologia massima delle chiamate agli strumenti conservata per l'analisi dei loop.
- `warningThreshold`: soglia del pattern ripetuto senza progresso per gli avvisi.
- `criticalThreshold`: soglia di ripetizione più alta per bloccare i loop critici.
- `globalCircuitBreakerThreshold`: soglia di arresto rigido per qualsiasi esecuzione senza progresso.
- `detectors.genericRepeat`: avvisa su chiamate ripetute allo stesso strumento/con gli stessi argomenti.
- `detectors.knownPollNoProgress`: avvisa/blocca sui noti strumenti di polling (`process.poll`, `command_status`, ecc.).
- `detectors.pingPong`: avvisa/blocca sui pattern a coppie alternate senza progresso.
- Se `warningThreshold >= criticalThreshold` o `criticalThreshold >= globalCircuitBreakerThreshold`, la convalida fallisce.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // oppure env BRAVE_API_KEY
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // opzionale; ometti per auto-rilevamento
        maxChars: 50000,
        maxCharsCap: 50000,
        maxResponseBytes: 2000000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        maxRedirects: 3,
        readability: true,
        userAgent: "custom-ua",
      },
    },
  },
}
```

### `tools.media`

Configura la comprensione dei media in ingresso (immagine/audio/video):

```json5
{
  tools: {
    media: {
      concurrency: 2,
      asyncCompletion: {
        directSend: false, // opt-in: invia direttamente al canale i task music/video asincroni completati
      },
      audio: {
        enabled: true,
        maxBytes: 20971520,
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }],
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  },
}
```

<Accordion title="Campi delle voci del modello media">

**Voce provider** (`type: "provider"` o omesso):

- `provider`: id provider API (`openai`, `anthropic`, `google`/`gemini`, `groq`, ecc.)
- `model`: override dell'id modello
- `profile` / `preferredProfile`: selezione del profilo `auth-profiles.json`

**Voce CLI** (`type: "cli"`):

- `command`: eseguibile da lanciare
- `args`: argomenti con template (supporta `{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}`, ecc.)

**Campi comuni:**

- `capabilities`: elenco opzionale (`image`, `audio`, `video`). Predefiniti: `openai`/`anthropic`/`minimax` → image, `google` → image+audio+video, `groq` → audio.
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: override per voce.
- In caso di errore si passa alla voce successiva.

L'autenticazione del provider segue l'ordine standard: `auth-profiles.json` → variabili env → `models.providers.*.apiKey`.

**Campi di completamento asincrono:**

- `asyncCompletion.directSend`: quando `true`, i task `music_generate`
  e `video_generate` asincroni completati provano prima la consegna diretta sul canale. Predefinito: `false`
  (percorso legacy requester-session wake/model-delivery).

</Accordion>

### `tools.agentToAgent`

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },
}
```

### `tools.sessions`

Controlla quali sessioni possono essere usate come target dagli strumenti di sessione (`sessions_list`, `sessions_history`, `sessions_send`).

Predefinito: `tree` (sessione corrente + sessioni generate da essa, come i subagenti).

```json5
{
  tools: {
    sessions: {
      // "self" | "tree" | "agent" | "all"
      visibility: "tree",
    },
  },
}
```

Note:

- `self`: solo la chiave della sessione corrente.
- `tree`: sessione corrente + sessioni generate dalla sessione corrente (subagenti).
- `agent`: qualsiasi sessione appartenente all'ID agente corrente (può includere altri utenti se esegui sessioni per-mittente sotto lo stesso ID agente).
- `all`: qualsiasi sessione. Il targeting cross-agent richiede comunque `tools.agentToAgent`.
- Limitazione sandbox: quando la sessione corrente è sandboxed e `agents.defaults.sandbox.sessionToolsVisibility="spawned"`, la visibilità viene forzata a `tree` anche se `tools.sessions.visibility="all"`.

### `tools.sessions_spawn`

Controlla il supporto agli allegati inline per `sessions_spawn`.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // opt-in: imposta true per consentire allegati file inline
        maxTotalBytes: 5242880, // 5 MB totali su tutti i file
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 MB per file
        retainOnSessionKeep: false, // mantiene gli allegati quando cleanup="keep"
      },
    },
  },
}
```

Note:

- Gli allegati sono supportati solo per `runtime: "subagent"`. Il runtime ACP li rifiuta.
- I file vengono materializzati nella workspace figlia in `.openclaw/attachments/<uuid>/` con un `.manifest.json`.
- Il contenuto degli allegati viene automaticamente redatto dalla persistenza del transcript.
- Gli input base64 vengono convalidati con controlli rigorosi su alfabeto/padding e una protezione sulla dimensione prima della decodifica.
- I permessi dei file sono `0700` per le directory e `0600` per i file.
- La pulizia segue il criterio `cleanup`: `delete` rimuove sempre gli allegati; `keep` li conserva solo quando `retainOnSessionKeep: true`.

### `tools.experimental`

Flag sperimentali per gli strumenti integrati. Disattivati per impostazione predefinita, salvo quando si applica una regola di auto-abilitazione strict-agentic GPT-5.

```json5
{
  tools: {
    experimental: {
      planTool: true, // abilita l'update_plan sperimentale
    },
  },
}
```

Note:

- `planTool`: abilita lo strumento strutturato `update_plan` per il tracciamento di lavori multi-step non banali.
- Predefinito: `false` a meno che `agents.defaults.embeddedPi.executionContract` (o un override per agente) non sia impostato su `"strict-agentic"` per un'esecuzione OpenAI o OpenAI Codex della famiglia GPT-5. Imposta `true` per forzare l'attivazione dello strumento fuori da quel contesto, oppure `false` per mantenerlo disattivato anche per le esecuzioni strict-agentic GPT-5.
- Quando è abilitato, il prompt di sistema aggiunge anche linee guida d'uso così che il modello lo usi solo per lavori sostanziali e mantenga al massimo un passo `in_progress`.

### `agents.defaults.subagents`

```json5
{
  agents: {
    defaults: {
      subagents: {
        allowAgents: ["research"],
        model: "minimax/MiniMax-M2.7",
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`: modello predefinito per i subagenti generati. Se omesso, i subagenti ereditano il modello del chiamante.
- `allowAgents`: allowlist predefinita degli ID agente target per `sessions_spawn` quando l'agente richiedente non imposta il proprio `subagents.allowAgents` (`["*"]` = qualsiasi; predefinito: solo lo stesso agente).
- `runTimeoutSeconds`: timeout predefinito (secondi) per `sessions_spawn` quando la chiamata allo strumento omette `runTimeoutSeconds`. `0` significa nessun timeout.
- Criterio degli strumenti per subagente: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## Provider personalizzati e URL base

OpenClaw usa il catalogo di modelli integrato. Aggiungi provider personalizzati tramite `models.providers` nella configurazione o `~/.openclaw/agents/<agentId>/agent/models.json`.

```json5
{
  models: {
    mode: "merge", // merge (predefinito) | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions", // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            contextTokens: 96000,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

- Usa `authHeader: true` + `headers` per esigenze di autenticazione personalizzate.
- Sovrascrivi la radice di configurazione dell'agente con `OPENCLAW_AGENT_DIR` (o `PI_CODING_AGENT_DIR`, alias legacy della variabile d'ambiente).
- Precedenza di unione per ID provider corrispondenti:
  - I valori `baseUrl` non vuoti del `models.json` dell'agente hanno la precedenza.
  - I valori `apiKey` non vuoti dell'agente hanno la precedenza solo quando quel provider non è gestito da SecretRef nel contesto attuale di config/profilo auth.
  - I valori `apiKey` del provider gestiti da SecretRef vengono aggiornati dai marker di origine (`ENV_VAR_NAME` per i riferimenti env, `secretref-managed` per i riferimenti file/exec) invece di persistere i segreti risolti.
  - I valori header del provider gestiti da SecretRef vengono aggiornati dai marker di origine (`secretref-env:ENV_VAR_NAME` per i riferimenti env, `secretref-managed` per i riferimenti file/exec).
  - `apiKey`/`baseUrl` dell'agente vuoti o mancanti usano come fallback `models.providers` nella configurazione.
  - `contextWindow`/`maxTokens` del modello corrispondente usano il valore più alto tra config esplicita e valori impliciti del catalogo.
  - `contextTokens` del modello corrispondente preserva un limite runtime esplicito quando presente; usalo per limitare il contesto effettivo senza cambiare i metadati nativi del modello.
  - Usa `models.mode: "replace"` quando vuoi che la configurazione riscriva completamente `models.json`.
  - La persistenza dei marker è autorevole rispetto alla sorgente: i marker vengono scritti dallo snapshot della configurazione sorgente attiva (pre-risoluzione), non dai valori segreti runtime risolti.

### Dettagli dei campi del provider

- `models.mode`: comportamento del catalogo provider (`merge` o `replace`).
- `models.providers`: mappa dei provider personalizzati con chiave per ID provider.
- `models.providers.*.api`: adattatore di richiesta (`openai-completions`, `openai-responses`, `anthropic-messages`, `google-generative-ai`, ecc).
- `models.providers.*.apiKey`: credenziale del provider (preferisci SecretRef/sostituzione env).
- `models.providers.*.auth`: strategia di autenticazione (`api-key`, `token`, `oauth`, `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: per Ollama + `openai-completions`, inietta `options.num_ctx` nelle richieste (predefinito: `true`).
- `models.providers.*.authHeader`: forza il trasporto delle credenziali nell'header `Authorization` quando richiesto.
- `models.providers.*.baseUrl`: URL base dell'API upstream.
- `models.providers.*.headers`: header statici extra per routing proxy/tenant.
- `models.providers.*.request`: override del trasporto per le richieste HTTP del model-provider.
  - `request.headers`: header extra (uniti ai valori predefiniti del provider). I valori accettano SecretRef.
  - `request.auth`: override della strategia di autenticazione. Modalità: `"provider-default"` (usa l'autenticazione integrata del provider), `"authorization-bearer"` (con `token`), `"header"` (con `headerName`, `value`, `prefix` opzionale).
  - `request.proxy`: override del proxy HTTP. Modalità: `"env-proxy"` (usa le variabili env `HTTP_PROXY`/`HTTPS_PROXY`), `"explicit-proxy"` (con `url`). Entrambe le modalità accettano un sotto-oggetto `tls` opzionale.
  - `request.tls`: override TLS per le connessioni dirette. Campi: `ca`, `cert`, `key`, `passphrase` (tutti accettano SecretRef), `serverName`, `insecureSkipVerify`.
  - `request.allowPrivateNetwork`: quando `true`, consente HTTPS verso `baseUrl` quando il DNS si risolve in intervalli privati, CGNAT o simili, tramite la protezione HTTP fetch SSRF del provider (opt-in dell'operatore per endpoint OpenAI-compatibili self-hosted attendibili). WebSocket usa la stessa `request` per header/TLS ma non quel controllo SSRF fetch. Predefinito `false`.
- `models.providers.*.models`: voci esplicite del catalogo modelli del provider.
- `models.providers.*.models.*.contextWindow`: metadati della finestra di contesto nativa del modello.
- `models.providers.*.models.*.contextTokens`: limite runtime opzionale del contesto. Usalo quando vuoi un budget di contesto effettivo più piccolo della `contextWindow` nativa del modello.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: suggerimento di compatibilità opzionale. Per `api: "openai-completions"` con un `baseUrl` non vuoto e non nativo (host diverso da `api.openai.com`), OpenClaw forza questo valore a `false` a runtime. `baseUrl` vuoto/omesso mantiene il comportamento OpenAI predefinito.
- `models.providers.*.models.*.compat.requiresStringContent`: suggerimento di compatibilità opzionale per endpoint chat OpenAI-compatibili che accettano solo stringhe. Quando `true`, OpenClaw appiattisce gli array `messages[].content` di puro testo in stringhe semplici prima di inviare la richiesta.
- `plugins.entries.amazon-bedrock.config.discovery`: radice delle impostazioni di auto-rilevamento di Bedrock.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: attiva/disattiva il rilevamento implicito.
- `plugins.entries.amazon-bedrock.config.discovery.region`: regione AWS per il rilevamento.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: filtro facoltativo per provider-id per un rilevamento mirato.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: intervallo di polling per l'aggiornamento del rilevamento.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: finestra di contesto di fallback per i modelli rilevati.
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: token massimi di output di fallback per i modelli rilevati.

### Esempi di provider

<Accordion title="Cerebras (GLM 4.6 / 4.7)">

```json5
{
  env: { CEREBRAS_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: {
        primary: "cerebras/zai-glm-4.7",
        fallbacks: ["cerebras/zai-glm-4.6"],
      },
      models: {
        "cerebras/zai-glm-4.7": { alias: "GLM 4.7 (Cerebras)" },
        "cerebras/zai-glm-4.6": { alias: "GLM 4.6 (Cerebras)" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      cerebras: {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" },
        ],
      },
    },
  },
}
```

Usa `cerebras/zai-glm-4.7` per Cerebras; `zai/glm-4.7` per Z.AI diretto.

</Accordion>

<Accordion title="OpenCode">

```json5
{
  agents: {
    defaults: {
      model: { primary: "opencode/claude-opus-4-6" },
      models: { "opencode/claude-opus-4-6": { alias: "Opus" } },
    },
  },
}
```

Imposta `OPENCODE_API_KEY` (o `OPENCODE_ZEN_API_KEY`). Usa riferimenti `opencode/...` per il catalogo Zen oppure riferimenti `opencode-go/...` per il catalogo Go. Scorciatoia: `openclaw onboard --auth-choice opencode-zen` oppure `openclaw onboard --auth-choice opencode-go`.

</Accordion>

<Accordion title="Z.AI (GLM-4.7)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-4.7" },
      models: { "zai/glm-4.7": {} },
    },
  },
}
```

Imposta `ZAI_API_KEY`. `z.ai/*` e `z-ai/*` sono alias accettati. Scorciatoia: `openclaw onboard --auth-choice zai-api-key`.

- Endpoint generale: `https://api.z.ai/api/paas/v4`
- Endpoint coding (predefinito): `https://api.z.ai/api/coding/paas/v4`
- Per l'endpoint generale, definisci un provider personalizzato con l'override del base URL.

</Accordion>

<Accordion title="Moonshot AI (Kimi)">

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: { "moonshot/kimi-k2.5": { alias: "Kimi K2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
        ],
      },
    },
  },
}
```

Per l'endpoint Cina: `baseUrl: "https://api.moonshot.cn/v1"` oppure `openclaw onboard --auth-choice moonshot-api-key-cn`.

Gli endpoint Moonshot nativi dichiarano la compatibilità d'uso dello streaming sul trasporto condiviso `openai-completions`, e OpenClaw basa questo comportamento sulle capability dell'endpoint invece che solo sull'ID provider integrato.

</Accordion>

<Accordion title="Kimi Coding">

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi/kimi-code" },
      models: { "kimi/kimi-code": { alias: "Kimi Code" } },
    },
  },
}
```

Compatibile con Anthropic, provider integrato. Scorciatoia: `openclaw onboard --auth-choice kimi-code-api-key`.

</Accordion>

<Accordion title="Synthetic (compatibile con Anthropic)">

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

Il base URL deve omettere `/v1` (il client Anthropic lo aggiunge). Scorciatoia: `openclaw onboard --auth-choice synthetic-api-key`.

</Accordion>

<Accordion title="MiniMax M2.7 (diretto)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.7" },
      models: {
        "minimax/MiniMax-M2.7": { alias: "Minimax" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

Imposta `MINIMAX_API_KEY`. Scorciatoie:
`openclaw onboard --auth-choice minimax-global-api` oppure
`openclaw onboard --auth-choice minimax-cn-api`.
Il catalogo dei modelli usa come predefinito solo M2.7.
Nel percorso di streaming compatibile con Anthropic, OpenClaw disabilita per impostazione predefinita il thinking di MiniMax a meno che tu non imposti esplicitamente `thinking`. `/fast on` o `params.fastMode: true` riscrivono `MiniMax-M2.7` in `MiniMax-M2.7-highspeed`.

</Accordion>

<Accordion title="Modelli locali (LM Studio)">

Vedi [Local Models](/it/gateway/local-models). In breve: esegui un grande modello locale tramite LM Studio Responses API su hardware serio; mantieni uniti i modelli hosted come fallback.

</Accordion>

---

## Skills

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn | bun
    },
    entries: {
      "image-lab": {
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // oppure stringa in chiaro
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: allowlist opzionale solo per le Skills bundled (le Skills managed/workspace non sono interessate).
- `load.extraDirs`: radici extra di Skills condivise (precedenza più bassa).
- `install.preferBrew`: quando è true, preferisce gli installer Homebrew quando `brew` è disponibile prima di ripiegare su altri tipi di installer.
- `install.nodeManager`: preferenza del gestore Node per le specifiche `metadata.openclaw.install`
  (`npm` | `pnpm` | `yarn` | `bun`).
- `entries.<skillKey>.enabled: false` disabilita una Skills anche se bundled/installata.
- `entries.<skillKey>.apiKey`: comodità per le Skills che dichiarano una variabile env primaria (stringa in chiaro o oggetto SecretRef).

---

## Plugin

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: [],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        hooks: {
          allowPromptInjection: false,
        },
        config: { provider: "twilio" },
      },
    },
  },
}
```

- Caricati da `~/.openclaw/extensions`, `<workspace>/.openclaw/extensions`, più `plugins.load.paths`.
- Il rilevamento accetta plugin OpenClaw nativi più bundle Codex compatibili e bundle Claude, inclusi i bundle Claude senza manifest con layout predefinito.
- **Le modifiche alla configurazione richiedono un riavvio del gateway.**
- `allow`: allowlist opzionale (vengono caricati solo i plugin elencati). `deny` prevale.
- `plugins.entries.<id>.apiKey`: campo di utilità per API key a livello plugin (quando supportato dal plugin).
- `plugins.entries.<id>.env`: mappa di variabili env con scope del plugin.
- `plugins.entries.<id>.hooks.allowPromptInjection`: quando `false`, il core blocca `before_prompt_build` e ignora i campi legacy che mutano il prompt da `before_agent_start`, preservando però i legacy `modelOverride` e `providerOverride`. Si applica agli hook plugin nativi e alle directory hook fornite dai bundle supportati.
- `plugins.entries.<id>.subagent.allowModelOverride`: considera esplicitamente attendibile questo plugin per richiedere override `provider` e `model` per esecuzione nei run in background dei subagenti.
- `plugins.entries.<id>.subagent.allowedModels`: allowlist opzionale di target canonici `provider/model` per gli override attendibili dei subagenti. Usa `"*"` solo quando intendi consentire qualsiasi modello.
- `plugins.entries.<id>.config`: oggetto di configurazione definito dal plugin (convalidato dallo schema del plugin OpenClaw nativo quando disponibile).
- `plugins.entries.firecrawl.config.webFetch`: impostazioni del provider Firecrawl web-fetch.
  - `apiKey`: chiave API Firecrawl (accetta SecretRef). Usa come fallback `plugins.entries.firecrawl.config.webSearch.apiKey`, il legacy `tools.web.fetch.firecrawl.apiKey` o la variabile env `FIRECRAWL_API_KEY`.
  - `baseUrl`: URL base dell'API Firecrawl (predefinito: `https://api.firecrawl.dev`).
  - `onlyMainContent`: estrae solo il contenuto principale dalle pagine (predefinito: `true`).
  - `maxAgeMs`: età massima della cache in millisecondi (predefinito: `172800000` / 2 giorni).
  - `timeoutSeconds`: timeout della richiesta di scraping in secondi (predefinito: `60`).
- `plugins.entries.xai.config.xSearch`: impostazioni di xAI X Search (ricerca web Grok).
  - `enabled`: abilita il provider X Search.
  - `model`: modello Grok da usare per la ricerca (ad esempio `"grok-4-1-fast"`).
- `plugins.entries.memory-core.config.dreaming`: impostazioni del dreaming della memoria. Vedi [Dreaming](/it/concepts/dreaming) per fasi e soglie.
  - `enabled`: interruttore principale di Dreaming (predefinito `false`).
  - `frequency`: cadenza Cron per ogni ciclo completo di Dreaming (predefinito `"0 3 * * *"`).
  - il criterio di fase e le soglie sono dettagli di implementazione (non chiavi di configurazione rivolte all'utente).
- La configurazione completa della memoria si trova in [Riferimento della configurazione della memoria](/it/reference/memory-config):
  - `agents.defaults.memorySearch.*`
  - `memory.backend`
  - `memory.citations`
  - `memory.qmd.*`
  - `plugins.entries.memory-core.config.dreaming`
- I plugin bundle Claude abilitati possono anche contribuire ai valori predefiniti embedded di Pi da `settings.json`; OpenClaw li applica come impostazioni dell'agente sanificate, non come patch raw della configurazione OpenClaw.
- `plugins.slots.memory`: scegli l'id del plugin memoria attivo, oppure `"none"` per disabilitare i plugin memoria.
- `plugins.slots.contextEngine`: scegli l'id del plugin context engine attivo; il valore predefinito è `"legacy"` finché non installi e selezioni un altro engine.
- `plugins.installs`: metadati di installazione gestiti dalla CLI usati da `openclaw plugins update`.
  - Include `source`, `spec`, `sourcePath`, `installPath`, `version`, `resolvedName`, `resolvedVersion`, `resolvedSpec`, `integrity`, `shasum`, `resolvedAt`, `installedAt`.
  - Tratta `plugins.installs.*` come stato gestito; preferisci i comandi CLI alle modifiche manuali.

Vedi [Plugins](/it/tools/plugin).

---

## Browser

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "user",
    ssrfPolicy: {
      // dangerouslyAllowPrivateNetwork: true, // opt-in solo per accesso attendibile alla rete privata
      // allowPrivateNetwork: true, // alias legacy
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: { driver: "existing-session", attachOnly: true, color: "#00AA00" },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
    // headless: false,
    // noSandbox: false,
    // extraArgs: [],
    // executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    // attachOnly: false,
  },
}
```

- `evaluateEnabled: false` disabilita `act:evaluate` e `wait --fn`.
- `ssrfPolicy.dangerouslyAllowPrivateNetwork` è disabilitato quando non è impostato, quindi la navigazione del browser resta rigorosa per impostazione predefinita.
- Imposta `ssrfPolicy.dangerouslyAllowPrivateNetwork: true` solo quando intendi fidarti esplicitamente della navigazione browser sulla rete privata.
- In modalità rigorosa, gli endpoint remoti del profilo CDP (`profiles.*.cdpUrl`) sono soggetti allo stesso blocco della rete privata durante i controlli di raggiungibilità/rilevamento.
- `ssrfPolicy.allowPrivateNetwork` resta supportato come alias legacy.
- In modalità rigorosa, usa `ssrfPolicy.hostnameAllowlist` e `ssrfPolicy.allowedHostnames` per eccezioni esplicite.
- I profili remoti sono solo attach-only (start/stop/reset disabilitati).
- `profiles.*.cdpUrl` accetta `http://`, `https://`, `ws://` e `wss://`.
  Usa HTTP(S) quando vuoi che OpenClaw rilevi `/json/version`; usa WS(S)
  quando il provider ti fornisce un URL WebSocket DevTools diretto.
- I profili `existing-session` sono solo host e usano Chrome MCP invece di CDP.
- I profili `existing-session` possono impostare `userDataDir` per puntare a un profilo specifico di browser basato su Chromium, come Brave o Edge.
- I profili `existing-session` mantengono gli attuali limiti del percorso Chrome MCP:
  azioni basate su snapshot/ref invece del targeting tramite selettori CSS, hook per upload di un solo file, nessun override del timeout dei dialoghi, nessun `wait --load networkidle` e nessun `responsebody`, esportazione PDF, intercettazione dei download o azioni batch.
- I profili locali gestiti `openclaw` assegnano automaticamente `cdpPort` e `cdpUrl`; imposta `cdpUrl` esplicitamente solo per CDP remoto.
- Ordine di auto-rilevamento: browser predefinito se basato su Chromium → Chrome → Brave → Edge → Chromium → Chrome Canary.
- Servizio di controllo: solo loopback (porta derivata da `gateway.port`, predefinita `18791`).
- `extraArgs` aggiunge flag di avvio extra all'avvio locale di Chromium (ad esempio `--disable-gpu`, dimensionamento della finestra o flag di debug).

---

## UI

```json5
{
  ui: {
    seamColor: "#FF4500",
    assistant: {
      name: "OpenClaw",
      avatar: "CB", // emoji, testo breve, URL immagine o URI data
    },
  },
}
```

- `seamColor`: colore d'accento per la chrome della UI dell'app nativa (tinta della bolla Talk Mode, ecc.).
- `assistant`: override dell'identità della Control UI. Usa come fallback l'identità dell'agente attivo.

---

## Gateway

```json5
{
  gateway: {
    mode: "local", // local | remote
    port: 18789,
    bind: "loopback",
    auth: {
      mode: "token", // none | token | password | trusted-proxy
      token: "your-token",
      // password: "your-password", // oppure OPENCLAW_GATEWAY_PASSWORD
      // trustedProxy: { userHeader: "x-forwarded-user" }, // per mode=trusted-proxy; vedi /gateway/trusted-proxy-auth
      allowTailscale: true,
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,
        lockoutMs: 300000,
        exemptLoopback: true,
      },
    },
    tailscale: {
      mode: "off", // off | serve | funnel
      resetOnExit: false,
    },
    controlUi: {
      enabled: true,
      basePath: "/openclaw",
      // root: "dist/control-ui",
      // embedSandbox: "scripts", // strict | scripts | trusted
      // allowExternalEmbedUrls: false, // pericoloso: consente URL embed esterni assoluti http(s)
      // allowedOrigins: ["https://control.example.com"], // richiesto per Control UI non loopback
      // dangerouslyAllowHostHeaderOriginFallback: false, // modalità pericolosa di fallback dell'origine Host-header
      // allowInsecureAuth: false,
      // dangerouslyDisableDeviceAuth: false,
    },
    remote: {
      url: "ws://gateway.tailnet:18789",
      transport: "ssh", // ssh | direct
      token: "your-token",
      // password: "your-password",
    },
    trustedProxies: ["10.0.0.1"],
    // Opzionale. Predefinito false.
    allowRealIpFallback: false,
    tools: {
      // deny HTTP aggiuntivi per /tools/invoke
      deny: ["browser"],
      // Rimuove strumenti dall'elenco deny HTTP predefinito
      allow: ["gateway"],
    },
    push: {
      apns: {
        relay: {
          baseUrl: "https://relay.example.com",
          timeoutMs: 10000,
        },
      },
    },
  },
}
```

<Accordion title="Dettagli dei campi del Gateway">

- `mode`: `local` (esegui il gateway) oppure `remote` (connettiti a un gateway remoto). Il Gateway rifiuta di avviarsi a meno che non sia `local`.
- `port`: singola porta multiplexata per WS + HTTP. Precedenza: `--port` > `OPENCLAW_GATEWAY_PORT` > `gateway.port` > `18789`.
- `bind`: `auto`, `loopback` (predefinito), `lan` (`0.0.0.0`), `tailnet` (solo IP Tailscale) oppure `custom`.
- **Alias bind legacy**: usa i valori della modalità bind in `gateway.bind` (`auto`, `loopback`, `lan`, `tailnet`, `custom`), non gli alias host (`0.0.0.0`, `127.0.0.1`, `localhost`, `::`, `::1`).
- **Nota Docker**: il bind predefinito `loopback` ascolta su `127.0.0.1` all'interno del container. Con il networking bridge di Docker (`-p 18789:18789`), il traffico arriva su `eth0`, quindi il gateway non è raggiungibile. Usa `--network host`, oppure imposta `bind: "lan"` (o `bind: "custom"` con `customBindHost: "0.0.0.0"`) per ascoltare su tutte le interfacce.
- **Auth**: richiesta per impostazione predefinita. I bind non loopback richiedono l'autenticazione del gateway. In pratica questo significa un token/password condiviso oppure un reverse proxy identity-aware con `gateway.auth.mode: "trusted-proxy"`. La procedura guidata di onboarding genera un token per impostazione predefinita.
- Se sono configurati sia `gateway.auth.token` sia `gateway.auth.password` (inclusi SecretRef), imposta esplicitamente `gateway.auth.mode` su `token` o `password`. L'avvio e i flussi di installazione/riparazione del servizio falliscono quando entrambi sono configurati e la modalità non è impostata.
- `gateway.auth.mode: "none"`: modalità esplicita senza autenticazione. Usala solo per configurazioni trusted local loopback; intenzionalmente non viene proposta dai prompt di onboarding.
- `gateway.auth.mode: "trusted-proxy"`: delega l'autenticazione a un reverse proxy identity-aware e considera attendibili gli header di identità da `gateway.trustedProxies` (vedi [Trusted Proxy Auth](/it/gateway/trusted-proxy-auth)). Questa modalità si aspetta una sorgente proxy **non loopback**; i reverse proxy loopback sullo stesso host non soddisfano l'autenticazione trusted-proxy.
- `gateway.auth.allowTailscale`: quando `true`, gli header di identità Tailscale Serve possono soddisfare l'autenticazione di Control UI/WebSocket (verificata tramite `tailscale whois`). Gli endpoint API HTTP **non** usano quell'autenticazione tramite header Tailscale; seguono invece la normale modalità di autenticazione HTTP del gateway. Questo flusso senza token presume che l'host del gateway sia attendibile. Il valore predefinito è `true` quando `tailscale.mode = "serve"`.
- `gateway.auth.rateLimit`: limitatore opzionale dei tentativi di autenticazione falliti. Si applica per IP client e per ambito auth (shared-secret e device-token vengono tracciati in modo indipendente). I tentativi bloccati restituiscono `429` + `Retry-After`.
  - Sul percorso asincrono di Tailscale Serve Control UI, i tentativi falliti per lo stesso `{scope, clientIp}` vengono serializzati prima della scrittura del fallimento. Tentativi concorrenti non validi dallo stesso client possono quindi attivare il limitatore sulla seconda richiesta invece di passare entrambi come semplici mismatch.
  - `gateway.auth.rateLimit.exemptLoopback` ha come predefinito `true`; impostalo su `false` quando vuoi intenzionalmente applicare il rate limit anche al traffico localhost (per configurazioni di test o deployment proxy rigorosi).
- I tentativi di autenticazione WS da origine browser vengono sempre limitati con l'esenzione loopback disabilitata (defense-in-depth contro la forza bruta localhost basata su browser).
- Su loopback, quei lockout da origine browser sono isolati per valore `Origin`
  normalizzato, così fallimenti ripetuti da un'origine localhost non bloccano automaticamente un'origine diversa.
- `tailscale.mode`: `serve` (solo tailnet, bind loopback) oppure `funnel` (pubblico, richiede auth).
- `controlUi.allowedOrigins`: allowlist esplicita delle origini browser per le connessioni WebSocket del Gateway. Richiesta quando si prevedono client browser da origini non loopback.
- `controlUi.dangerouslyAllowHostHeaderOriginFallback`: modalità pericolosa che abilita il fallback dell'origine basato sull'header Host per deployment che dipendono intenzionalmente da una policy di origine basata su Host-header.
- `remote.transport`: `ssh` (predefinito) oppure `direct` (ws/wss). Per `direct`, `remote.url` deve essere `ws://` oppure `wss://`.
- `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`: override break-glass lato client che consente `ws://` in chiaro verso IP attendibili di rete privata; il comportamento predefinito resta solo-loopback per il traffico in chiaro.
- `gateway.remote.token` / `.password` sono campi credenziali del client remoto. Non configurano da soli l'autenticazione del gateway.
- `gateway.push.apns.relay.baseUrl`: URL HTTPS base per il relay APNs esterno usato dalle build iOS ufficiali/TestFlight dopo che pubblicano al gateway registrazioni supportate da relay. Questo URL deve corrispondere all'URL relay compilato nella build iOS.
- `gateway.push.apns.relay.timeoutMs`: timeout in millisecondi per l'invio dal gateway al relay. Predefinito: `10000`.
- Le registrazioni supportate da relay vengono delegate a una specifica identità del gateway. L'app iOS associata recupera `gateway.identity.get`, include quell'identità nella registrazione relay e inoltra al gateway una send grant con scope della registrazione. Un altro gateway non può riutilizzare quella registrazione memorizzata.
- `OPENCLAW_APNS_RELAY_BASE_URL` / `OPENCLAW_APNS_RELAY_TIMEOUT_MS`: override temporanei via env per la configurazione relay sopra.
- `OPENCLAW_APNS_RELAY_ALLOW_HTTP=true`: escape hatch solo per sviluppo per URL relay HTTP loopback. Gli URL relay di produzione devono restare su HTTPS.
- `gateway.channelHealthCheckMinutes`: intervallo in minuti del monitor di salute dei canali. Imposta `0` per disabilitare globalmente i riavvii del monitor di salute. Predefinito: `5`.
- `gateway.channelStaleEventThresholdMinutes`: soglia in minuti per socket obsoleti. Mantienila maggiore o uguale a `gateway.channelHealthCheckMinutes`. Predefinito: `30`.
- `gateway.channelMaxRestartsPerHour`: numero massimo di riavvii del monitor di salute per canale/account in un'ora mobile. Predefinito: `10`.
- `channels.<provider>.healthMonitor.enabled`: opt-out per canale dei riavvii del monitor di salute mantenendo comunque abilitato il monitor globale.
- `channels.<provider>.accounts.<accountId>.healthMonitor.enabled`: override per account per i canali multi-account. Quando è impostato, ha la precedenza sull'override a livello di canale.
- I percorsi di chiamata del gateway locale possono usare `gateway.remote.*` come fallback solo quando `gateway.auth.*` non è impostato.
- Se `gateway.auth.token` / `gateway.auth.password` è configurato esplicitamente tramite SecretRef e non viene risolto, la risoluzione fallisce in modalità fail-closed (nessun fallback remoto che mascheri il problema).
- `trustedProxies`: IP di reverse proxy che terminano TLS o iniettano header del client inoltrato. Elenca solo proxy che controlli. Le voci loopback restano valide per configurazioni di rilevamento stesso-host/proxy locale (ad esempio Tailscale Serve o un reverse proxy locale), ma **non** rendono idonee le richieste loopback a `gateway.auth.mode: "trusted-proxy"`.
- `allowRealIpFallback`: quando `true`, il gateway accetta `X-Real-IP` se `X-Forwarded-For` manca. Predefinito `false` per comportamento fail-closed.
- `gateway.tools.deny`: nomi di strumenti extra bloccati per HTTP `POST /tools/invoke` (estende l'elenco deny predefinito).
- `gateway.tools.allow`: rimuove nomi di strumenti dall'elenco deny HTTP predefinito.

</Accordion>

### Endpoint compatibili con OpenAI

- Chat Completions: disabilitato per impostazione predefinita. Abilitalo con `gateway.http.endpoints.chatCompletions.enabled: true`.
- Responses API: `gateway.http.endpoints.responses.enabled`.
- Hardening dell'input URL di Responses:
  - `gateway.http.endpoints.responses.maxUrlParts`
  - `gateway.http.endpoints.responses.files.urlAllowlist`
  - `gateway.http.endpoints.responses.images.urlAllowlist`
    Le allowlist vuote vengono trattate come non impostate; usa `gateway.http.endpoints.responses.files.allowUrl=false`
    e/o `gateway.http.endpoints.responses.images.allowUrl=false` per disabilitare il recupero tramite URL.
- Header opzionale di hardening della risposta:
  - `gateway.http.securityHeaders.strictTransportSecurity` (impostalo solo per origini HTTPS che controlli; vedi [Trusted Proxy Auth](/it/gateway/trusted-proxy-auth#tls-termination-and-hsts))

### Isolamento multi-istanza

Esegui più gateway su un unico host con porte e directory di stato univoche:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \
OPENCLAW_STATE_DIR=~/.openclaw-a \
openclaw gateway --port 19001
```

Flag di utilità: `--dev` (usa `~/.openclaw-dev` + porta `19001`), `--profile <name>` (usa `~/.openclaw-<name>`).

Vedi [Multiple Gateways](/it/gateway/multiple-gateways).

### `gateway.tls`

```json5
{
  gateway: {
    tls: {
      enabled: false,
      autoGenerate: false,
      certPath: "/etc/openclaw/tls/server.crt",
      keyPath: "/etc/openclaw/tls/server.key",
      caPath: "/etc/openclaw/tls/ca-bundle.crt",
    },
  },
}
```

- `enabled`: abilita la terminazione TLS sul listener del gateway (HTTPS/WSS) (predefinito: `false`).
- `autoGenerate`: genera automaticamente una coppia locale certificato/chiave autofirmata quando non sono configurati file espliciti; solo per uso locale/dev.
- `certPath`: percorso filesystem del file del certificato TLS.
- `keyPath`: percorso filesystem della chiave privata TLS; mantienilo con permessi limitati.
- `caPath`: percorso opzionale del bundle CA per la verifica del client o catene di trust personalizzate.

### `gateway.reload`

```json5
{
  gateway: {
    reload: {
      mode: "hybrid", // off | restart | hot | hybrid
      debounceMs: 500,
      deferralTimeoutMs: 300000,
    },
  },
}
```

- `mode`: controlla come vengono applicate a runtime le modifiche alla configurazione.
  - `"off"`: ignora le modifiche live; i cambiamenti richiedono un riavvio esplicito.
  - `"restart"`: riavvia sempre il processo del gateway in caso di modifica della configurazione.
  - `"hot"`: applica i cambiamenti nel processo senza riavviare.
  - `"hybrid"` (predefinito): prova prima l'hot reload; se necessario torna al riavvio.
- `debounceMs`: finestra di debounce in ms prima che le modifiche di configurazione vengano applicate (intero non negativo).
- `deferralTimeoutMs`: tempo massimo in ms per attendere le operazioni in corso prima di forzare un riavvio (predefinito: `300000` = 5 minuti).

---

## Hook

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    maxBodyBytes: 262144,
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: false,
    allowedSessionKeyPrefixes: ["hook:"],
    allowedAgentIds: ["hooks", "main"],
    presets: ["gmail"],
    transformsDir: "~/.openclaw/hooks/transforms",
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
        agentId: "hooks",
        wakeMode: "now",
        name: "Gmail",
        sessionKey: "hook:gmail:{{messages[0].id}}",
        messageTemplate: "Da: {{messages[0].from}}\nOggetto: {{messages[0].subject}}\n{{messages[0].snippet}}",
        deliver: true,
        channel: "last",
        model: "openai/gpt-5.4-mini",
      },
    ],
  },
}
```

Auth: `Authorization: Bearer <token>` oppure `x-openclaw-token: <token>`.
I token degli hook nella query string vengono rifiutati.

Note su convalida e sicurezza:

- `hooks.enabled=true` richiede un `hooks.token` non vuoto.
- `hooks.token` deve essere **distinto** da `gateway.auth.token`; il riuso del token del Gateway viene rifiutato.
- `hooks.path` non può essere `/`; usa un sottopercorso dedicato come `/hooks`.
- Se `hooks.allowRequestSessionKey=true`, limita `hooks.allowedSessionKeyPrefixes` (ad esempio `["hook:"]`).

**Endpoint:**

- `POST /hooks/wake` → `{ text, mode?: "now"|"next-heartbeat" }`
- `POST /hooks/agent` → `{ message, name?, agentId?, sessionKey?, wakeMode?, deliver?, channel?, to?, model?, thinking?, timeoutSeconds? }`
  - `sessionKey` dal payload della richiesta è accettato solo quando `hooks.allowRequestSessionKey=true` (predefinito: `false`).
- `POST /hooks/<name>` → risolto tramite `hooks.mappings`

<Accordion title="Dettagli della mappatura">

- `match.path` corrisponde al sotto-percorso dopo `/hooks` (ad es. `/hooks/gmail` → `gmail`).
- `match.source` corrisponde a un campo del payload per i percorsi generici.
- I template come `{{messages[0].subject}}` leggono dal payload.
- `transform` può puntare a un modulo JS/TS che restituisce un'azione hook.
  - `transform.module` deve essere un percorso relativo e rimanere entro `hooks.transformsDir` (i percorsi assoluti e il traversal vengono rifiutati).
- `agentId` instrada verso un agente specifico; gli ID sconosciuti usano come fallback il predefinito.
- `allowedAgentIds`: limita il routing esplicito (`*` o omesso = consenti tutti, `[]` = nega tutti).
- `defaultSessionKey`: chiave di sessione fissa opzionale per le esecuzioni dell'agente hook senza `sessionKey` esplicito.
- `allowRequestSessionKey`: consente ai chiamanti di `/hooks/agent` di impostare `sessionKey` (predefinito: `false`).
- `allowedSessionKeyPrefixes`: allowlist opzionale di prefissi per valori espliciti di `sessionKey` (richiesta + mappatura), ad es. `["hook:"]`.
- `deliver: true` invia la risposta finale a un canale; `channel` ha come predefinito `last`.
- `model` sovrascrive l'LLM per questa esecuzione hook (deve essere consentito se è impostato il catalogo modelli).

</Accordion>

### Integrazione Gmail

```json5
{
  hooks: {
    gmail: {
      account: "openclaw@gmail.com",
      topic: "projects/<project-id>/topics/gog-gmail-watch",
      subscription: "gog-gmail-watch-push",
      pushToken: "shared-push-token",
      hookUrl: "http://127.0.0.1:18789/hooks/gmail",
      includeBody: true,
      maxBytes: 20000,
      renewEveryMinutes: 720,
      serve: { bind: "127.0.0.1", port: 8788, path: "/" },
      tailscale: { mode: "funnel", path: "/gmail-pubsub" },
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

- Il Gateway avvia automaticamente `gog gmail watch serve` all'avvio quando è configurato. Imposta `OPENCLAW_SKIP_GMAIL_WATCHER=1` per disabilitarlo.
- Non eseguire un `gog gmail watch serve` separato insieme al Gateway.

---

## Canvas host

```json5
{
  canvasHost: {
    root: "~/.openclaw/workspace/canvas",
    liveReload: true,
    // enabled: false, // oppure OPENCLAW_SKIP_CANVAS_HOST=1
  },
}
```

- Serve HTML/CSS/JS modificabili dall'agente e A2UI via HTTP sotto la porta del Gateway:
  - `http://<gateway-host>:<gateway.port>/__openclaw__/canvas/`
  - `http://<gateway-host>:<gateway.port>/__openclaw__/a2ui/`
- Solo locale: mantieni `gateway.bind: "loopback"` (predefinito).
- Bind non loopback: le route canvas richiedono l'autenticazione del Gateway (token/password/trusted-proxy), come le altre superfici HTTP del Gateway.
- I Node WebView di solito non inviano header di autenticazione; dopo che un node è associato e connesso, il Gateway pubblicizza URL capability con scope del node per l'accesso a canvas/A2UI.
- Gli URL capability sono associati alla sessione WS attiva del node e scadono rapidamente. Non viene usato un fallback basato su IP.
- Inietta il client live-reload nell'HTML servito.
- Crea automaticamente un `index.html` iniziale quando vuoto.
- Serve anche A2UI su `/__openclaw__/a2ui/`.
- Le modifiche richiedono un riavvio del gateway.
- Disabilita il live reload per directory grandi o in caso di errori `EMFILE`.

---

## Discovery

### mDNS (Bonjour)

```json5
{
  discovery: {
    mdns: {
      mode: "minimal", // minimal | full | off
    },
  },
}
```

- `minimal` (predefinito): omette `cliPath` + `sshPort` dai record TXT.
- `full`: include `cliPath` + `sshPort`.
- L'hostname predefinito è `openclaw`. Sovrascrivilo con `OPENCLAW_MDNS_HOSTNAME`.

### Wide-area (DNS-SD)

```json5
{
  discovery: {
    wideArea: { enabled: true },
  },
}
```

Scrive una zona DNS-SD unicast sotto `~/.openclaw/dns/`. Per il rilevamento cross-network, abbinala a un server DNS (CoreDNS consigliato) + split DNS Tailscale.

Configurazione: `openclaw dns setup --apply`.

---

## Ambiente

### `env` (variabili env inline)

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: {
      GROQ_API_KEY: "gsk-...",
    },
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

- Le variabili env inline vengono applicate solo se l'env del processo non contiene la chiave.
- File `.env`: `.env` nella CWD + `~/.openclaw/.env` (nessuno dei due sovrascrive le variabili esistenti).
- `shellEnv`: importa le chiavi attese mancanti dal profilo della tua shell di login.
- Vedi [Environment](/it/help/environment) per la precedenza completa.

### Sostituzione delle variabili env

Fai riferimento alle variabili env in qualsiasi stringa di configurazione con `${VAR_NAME}`:

```json5
{
  gateway: {
    auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" },
  },
}
```

- Vengono riconosciuti solo i nomi in maiuscolo: `[A-Z_][A-Z0-9_]*`.
- Variabili mancanti/vuote generano un errore al caricamento della configurazione.
- Usa l'escape `$${VAR}` per un `${VAR}` letterale.
- Funziona con `$include`.

---

## Segreti

I riferimenti ai segreti sono additivi: i valori in chiaro continuano a funzionare.

### `SecretRef`

Usa una forma oggetto:

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

Convalida:

- pattern `provider`: `^[a-z][a-z0-9_-]{0,63}$`
- pattern `id` per `source: "env"`: `^[A-Z][A-Z0-9_]{0,127}$`
- `id` per `source: "file"`: puntatore JSON assoluto (ad esempio `"/providers/openai/apiKey"`)
- pattern `id` per `source: "exec"`: `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`
- Gli `id` con `source: "exec"` non devono contenere segmenti di percorso `.` o `..` delimitati da slash (ad esempio `a/../b` viene rifiutato)

### Superficie delle credenziali supportata

- Matrice canonica: [SecretRef Credential Surface](/it/reference/secretref-credential-surface)
- `secrets apply` ha come destinazione i percorsi delle credenziali supportati in `openclaw.json`.
- I riferimenti in `auth-profiles.json` sono inclusi nella risoluzione runtime e nella copertura dell'audit.

### Configurazione dei provider di segreti

```json5
{
  secrets: {
    providers: {
      default: { source: "env" }, // provider env esplicito opzionale
      filemain: {
        source: "file",
        path: "~/.openclaw/secrets.json",
        mode: "json",
        timeoutMs: 5000,
      },
      vault: {
        source: "exec",
        command: "/usr/local/bin/openclaw-vault-resolver",
        passEnv: ["PATH", "VAULT_ADDR"],
      },
    },
    defaults: {
      env: "default",
      file: "filemain",
      exec: "vault",
    },
  },
}
```

Note:

- Il provider `file` supporta `mode: "json"` e `mode: "singleValue"` (`id` deve essere `"value"` in modalità singleValue).
- Il provider `exec` richiede un percorso `command` assoluto e usa payload di protocollo su stdin/stdout.
- Per impostazione predefinita, i percorsi di comando symlink vengono rifiutati. Imposta `allowSymlinkCommand: true` per consentire percorsi symlink convalidando però il percorso del target risolto.
- Se è configurato `trustedDirs`, il controllo della directory attendibile si applica al percorso del target risolto.
- L'ambiente figlio di `exec` è minimo per impostazione predefinita; passa esplicitamente le variabili necessarie con `passEnv`.
- I riferimenti ai segreti vengono risolti al momento dell'attivazione in uno snapshot in memoria, poi i percorsi di richiesta leggono solo dallo snapshot.
- Durante l'attivazione si applica il filtering della superficie attiva: i riferimenti non risolti sulle superfici abilitate fanno fallire avvio/reload, mentre le superfici inattive vengono saltate con diagnostica.

---

## Archiviazione auth

```json5
{
  auth: {
    profiles: {
      "anthropic:default": { provider: "anthropic", mode: "api_key" },
      "anthropic:work": { provider: "anthropic", mode: "api_key" },
      "openai-codex:personal": { provider: "openai-codex", mode: "oauth" },
    },
    order: {
      anthropic: ["anthropic:default", "anthropic:work"],
      "openai-codex": ["openai-codex:personal"],
    },
  },
}
```

- I profili per agente vengono memorizzati in `<agentDir>/auth-profiles.json`.
- `auth-profiles.json` supporta riferimenti a livello di valore (`keyRef` per `api_key`, `tokenRef` per `token`) per le modalità di credenziali statiche.
- I profili in modalità OAuth (`auth.profiles.<id>.mode = "oauth"`) non supportano credenziali dell'auth-profile supportate da SecretRef.
- Le credenziali runtime statiche provengono da snapshot risolti in memoria; le voci statiche legacy di `auth.json` vengono ripulite quando trovate.
- Import legacy OAuth da `~/.openclaw/credentials/oauth.json`.
- Vedi [OAuth](/it/concepts/oauth).
- Comportamento runtime dei segreti e tooling `audit/configure/apply`: [Secrets Management](/it/gateway/secrets).

### `auth.cooldowns`

```json5
{
  auth: {
    cooldowns: {
      billingBackoffHours: 5,
      billingBackoffHoursByProvider: { anthropic: 3, openai: 8 },
      billingMaxHours: 24,
      authPermanentBackoffMinutes: 10,
      authPermanentMaxMinutes: 60,
      failureWindowHours: 24,
      overloadedProfileRotations: 1,
      overloadedBackoffMs: 0,
      rateLimitedProfileRotations: 1,
    },
  },
}
```

- `billingBackoffHours`: backoff base in ore quando un profilo fallisce a causa di veri errori di fatturazione/credito insufficiente (predefinito: `5`). Testo esplicito di fatturazione può comunque finire qui anche su risposte `401`/`403`, ma i matcher di testo specifici del provider restano limitati al provider che li possiede (ad esempio OpenRouter `Key limit exceeded`). I messaggi HTTP `402` riprovabili relativi a finestra di utilizzo o limiti di spesa di organizzazione/workspace restano invece nel percorso `rate_limit`.
- `billingBackoffHoursByProvider`: override opzionali per provider delle ore di backoff di fatturazione.
- `billingMaxHours`: limite massimo in ore per la crescita esponenziale del backoff di fatturazione (predefinito: `24`).
- `authPermanentBackoffMinutes`: backoff base in minuti per errori `auth_permanent` ad alta confidenza (predefinito: `10`).
- `authPermanentMaxMinutes`: limite massimo in minuti per la crescita del backoff `auth_permanent` (predefinito: `60`).
- `failureWindowHours`: finestra mobile in ore usata per i contatori di backoff (predefinito: `24`).
- `overloadedProfileRotations`: numero massimo di rotazioni dello stesso auth-profile provider per errori di sovraccarico prima di passare al fallback del modello (predefinito: `1`). Le forme di provider occupato come `ModelNotReadyException` finiscono qui.
- `overloadedBackoffMs`: ritardo fisso prima di ritentare una rotazione provider/profilo sovraccarico (predefinito: `0`).
- `rateLimitedProfileRotations`: numero massimo di rotazioni dello stesso auth-profile provider per errori di rate limit prima di passare al fallback del modello (predefinito: `1`). Quel bucket rate-limit include testo caratteristico del provider come `Too many concurrent requests`, `ThrottlingException`, `concurrency limit reached`, `workers_ai ... quota limit exceeded` e `resource exhausted`.

---

## Logging

```json5
{
  logging: {
    level: "info",
    file: "/tmp/openclaw/openclaw.log",
    consoleLevel: "info",
    consoleStyle: "pretty", // pretty | compact | json
    redactSensitive: "tools", // off | tools
    redactPatterns: ["\\bTOKEN\\b\\s*[=:]\\s*([\"']?)([^\\s\"']+)\\1"],
  },
}
```

- File di log predefinito: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`.
- Imposta `logging.file` per un percorso stabile.
- `consoleLevel` passa a `debug` con `--verbose`.
- `maxFileBytes`: dimensione massima del file di log in byte prima che le scritture vengano soppresse (intero positivo; predefinito: `524288000` = 500 MB). Usa la rotazione esterna dei log per i deployment di produzione.

---

## Diagnostica

```json5
{
  diagnostics: {
    enabled: true,
    flags: ["telegram.*"],
    stuckSessionWarnMs: 30000,

    otel: {
      enabled: false,
      endpoint: "https://otel-collector.example.com:4318",
      protocol: "http/protobuf", // http/protobuf | grpc
      headers: { "x-tenant-id": "my-org" },
      serviceName: "openclaw-gateway",
      traces: true,
      metrics: true,
      logs: false,
      sampleRate: 1.0,
      flushIntervalMs: 5000,
    },

    cacheTrace: {
      enabled: false,
      filePath: "~/.openclaw/logs/cache-trace.jsonl",
      includeMessages: true,
      includePrompt: true,
      includeSystem: true,
    },
  },
}
```

- `enabled`: interruttore principale per l'output di strumentazione (predefinito: `true`).
- `flags`: array di stringhe flag che abilita output di log mirato (supporta wildcard come `"telegram.*"` oppure `"*"`).
- `stuckSessionWarnMs`: soglia di età in ms per emettere avvisi di sessione bloccata mentre una sessione resta nello stato di elaborazione.
- `otel.enabled`: abilita la pipeline di esportazione OpenTelemetry (predefinito: `false`).
- `otel.endpoint`: URL del collector per l'esportazione OTel.
- `otel.protocol`: `"http/protobuf"` (predefinito) oppure `"grpc"`.
- `otel.headers`: header metadata HTTP/gRPC extra inviati con le richieste di esportazione OTel.
- `otel.serviceName`: nome del servizio per gli attributi della risorsa.
- `otel.traces` / `otel.metrics` / `otel.logs`: abilitano l'esportazione di trace, metriche o log.
- `otel.sampleRate`: tasso di campionamento delle trace `0`–`1`.
- `otel.flushIntervalMs`: intervallo periodico di flush della telemetria in ms.
- `cacheTrace.enabled`: registra snapshot di cache trace per le esecuzioni embedded (predefinito: `false`).
- `cacheTrace.filePath`: percorso di output per il JSONL del cache trace (predefinito: `$OPENCLAW_STATE_DIR/logs/cache-trace.jsonl`).
- `cacheTrace.includeMessages` / `includePrompt` / `includeSystem`: controllano cosa viene incluso nell'output del cache trace (tutti predefiniti: `true`).

---

## Aggiornamento

```json5
{
  update: {
    channel: "stable", // stable | beta | dev
    checkOnStart: true,

    auto: {
      enabled: false,
      stableDelayHours: 6,
      stableJitterHours: 12,
      betaCheckIntervalHours: 1,
    },
  },
}
```

- `channel`: canale di rilascio per installazioni npm/git — `"stable"`, `"beta"` oppure `"dev"`.
- `checkOnStart`: controlla gli aggiornamenti npm quando il gateway si avvia (predefinito: `true`).
- `auto.enabled`: abilita l'aggiornamento automatico in background per le installazioni di pacchetti (predefinito: `false`).
- `auto.stableDelayHours`: ritardo minimo in ore prima dell'applicazione automatica sul canale stable (predefinito: `6`; massimo: `168`).
- `auto.stableJitterHours`: finestra extra di distribuzione graduale del rollout sul canale stable in ore (predefinito: `12`; massimo: `168`).
- `auto.betaCheckIntervalHours`: frequenza in ore dei controlli sul canale beta (predefinito: `1`; massimo: `24`).

---

## ACP

```json5
{
  acp: {
    enabled: false,
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "main",
    allowedAgents: ["main", "ops"],
    maxConcurrentSessions: 10,

    stream: {
      coalesceIdleMs: 50,
      maxChunkChars: 1000,
      repeatSuppression: true,
      deliveryMode: "live", // live | final_only
      hiddenBoundarySeparator: "paragraph", // none | space | newline | paragraph
      maxOutputChars: 50000,
      maxSessionUpdateChars: 500,
    },

    runtime: {
      ttlMinutes: 30,
    },
  },
}
```

- `enabled`: gate globale della funzionalità ACP (predefinito: `false`).
- `dispatch.enabled`: gate indipendente per il dispatch dei turni di sessione ACP (predefinito: `true`). Imposta `false` per mantenere disponibili i comandi ACP bloccando però l'esecuzione.
- `backend`: id del backend runtime ACP predefinito (deve corrispondere a un plugin runtime ACP registrato).
- `defaultAgent`: id agente ACP di fallback quando gli spawn non specificano un target esplicito.
- `allowedAgents`: allowlist di ID agente consentiti per le sessioni runtime ACP; vuoto significa nessuna restrizione aggiuntiva.
- `maxConcurrentSessions`: numero massimo di sessioni ACP contemporaneamente attive.
- `stream.coalesceIdleMs`: finestra di flush inattivo in ms per il testo in streaming.
- `stream.maxChunkChars`: dimensione massima del chunk prima della suddivisione della proiezione del blocco in streaming.
- `stream.repeatSuppression`: sopprime per turno le righe ripetute di stato/strumento (predefinito: `true`).
- `stream.deliveryMode`: `"live"` esegue lo streaming incrementale; `"final_only"` effettua il buffering fino agli eventi terminali del turno.
- `stream.hiddenBoundarySeparator`: separatore prima del testo visibile dopo eventi di strumenti nascosti (predefinito: `"paragraph"`).
- `stream.maxOutputChars`: numero massimo di caratteri di output dell'assistente proiettati per turno ACP.
- `stream.maxSessionUpdateChars`: numero massimo di caratteri per le righe proiettate di stato/aggiornamento ACP.
- `stream.tagVisibility`: record dei nomi dei tag con override booleani di visibilità per gli eventi in streaming.
- `runtime.ttlMinutes`: TTL di inattività in minuti per i worker di sessione ACP prima che siano idonei alla pulizia.
- `runtime.installCommand`: comando di installazione opzionale da eseguire durante il bootstrap di un ambiente runtime ACP.

---

## CLI

```json5
{
  cli: {
    banner: {
      taglineMode: "off", // random | default | off
    },
  },
}
```

- `cli.banner.taglineMode` controlla lo stile del tagline del banner:
  - `"random"` (predefinito): tagline rotanti divertenti/stagionali.
  - `"default"`: tagline neutrale fissa (`Tutte le tue chat, un solo OpenClaw.`).
  - `"off"`: nessun testo tagline (titolo/versione del banner ancora mostrati).
- Per nascondere l'intero banner (non solo i tagline), imposta la variabile env `OPENCLAW_HIDE_BANNER=1`.

---

## Wizard

Metadati scritti dai flussi di configurazione guidata della CLI (`onboard`, `configure`, `doctor`):

```json5
{
  wizard: {
    lastRunAt: "2026-01-01T00:00:00.000Z",
    lastRunVersion: "2026.1.4",
    lastRunCommit: "abc1234",
    lastRunCommand: "configure",
    lastRunMode: "local",
  },
}
```

---

## Identity

Vedi i campi identity di `agents.list` sotto [Valori predefiniti dell'agente](#agent-defaults).

---

## Bridge (legacy, rimosso)

Le build attuali non includono più il bridge TCP. I Node si connettono tramite il WebSocket del Gateway. Le chiavi `bridge.*` non fanno più parte dello schema di configurazione (la convalida fallisce finché non vengono rimosse; `openclaw doctor --fix` può eliminare le chiavi sconosciute).

<Accordion title="Configurazione bridge legacy (riferimento storico)">

```json
{
  "bridge": {
    "enabled": true,
    "port": 18790,
    "bind": "tailnet",
    "tls": {
      "enabled": true,
      "autoGenerate": true
    }
  }
}
```

</Accordion>

---

## Cron

```json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    webhook: "https://example.invalid/legacy", // fallback deprecato per i job memorizzati notify:true
    webhookToken: "replace-with-dedicated-token", // token bearer opzionale per l'autenticazione webhook in uscita
    sessionRetention: "24h", // stringa durata oppure false
    runLog: {
      maxBytes: "2mb", // predefinito 2_000_000 byte
      keepLines: 2000, // predefinito 2000
    },
  },
}
```

- `sessionRetention`: per quanto tempo mantenere le sessioni completate delle esecuzioni Cron isolate prima della rimozione da `sessions.json`. Controlla anche la pulizia dei transcript Cron eliminati archiviati. Predefinito: `24h`; imposta `false` per disabilitare.
- `runLog.maxBytes`: dimensione massima per file di log di esecuzione (`cron/runs/<jobId>.jsonl`) prima della pulizia. Predefinito: `2_000_000` byte.
- `runLog.keepLines`: righe più recenti conservate quando viene attivata la pulizia del log di esecuzione. Predefinito: `2000`.
- `webhookToken`: token bearer usato per la consegna POST del webhook Cron (`delivery.mode = "webhook"`); se omesso non viene inviato alcun header di autenticazione.
- `webhook`: URL webhook legacy deprecato di fallback (http/https) usato solo per i job memorizzati che hanno ancora `notify: true`.

### `cron.retry`

```json5
{
  cron: {
    retry: {
      maxAttempts: 3,
      backoffMs: [30000, 60000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "timeout", "server_error"],
    },
  },
}
```

- `maxAttempts`: numero massimo di retry per i job one-shot in caso di errori transitori (predefinito: `3`; intervallo: `0`–`10`).
- `backoffMs`: array di ritardi di backoff in ms per ogni tentativo di retry (predefinito: `[30000, 60000, 300000]`; 1–10 voci).
- `retryOn`: tipi di errore che attivano i retry — `"rate_limit"`, `"overloaded"`, `"network"`, `"timeout"`, `"server_error"`. Ometti per ritentare tutti i tipi transitori.

Si applica solo ai job Cron one-shot. I job ricorrenti usano una gestione dei fallimenti separata.

### `cron.failureAlert`

```json5
{
  cron: {
    failureAlert: {
      enabled: false,
      after: 3,
      cooldownMs: 3600000,
      mode: "announce",
      accountId: "main",
    },
  },
}
```

- `enabled`: abilita gli avvisi di errore per i job Cron (predefinito: `false`).
- `after`: numero di errori consecutivi prima che venga inviato un avviso (intero positivo, minimo: `1`).
- `cooldownMs`: millisecondi minimi tra avvisi ripetuti per lo stesso job (intero non negativo).
- `mode`: modalità di consegna — `"announce"` invia tramite un messaggio di canale; `"webhook"` pubblica sul webhook configurato.
- `accountId`: ID account o canale opzionale per limitare la consegna dell'avviso.

### `cron.failureDestination`

```json5
{
  cron: {
    failureDestination: {
      mode: "announce",
      channel: "last",
      to: "channel:C1234567890",
      accountId: "main",
    },
  },
}
```

- Destinazione predefinita per le notifiche di errore Cron per tutti i job.
- `mode`: `"announce"` oppure `"webhook"`; il valore predefinito è `"announce"` quando esistono dati target sufficienti.
- `channel`: override del canale per la consegna announce. `"last"` riusa l'ultimo canale di consegna noto.
- `to`: target announce esplicito o URL webhook. Obbligatorio per la modalità webhook.
- `accountId`: override opzionale dell'account per la consegna.
- `delivery.failureDestination` per job sovrascrive questo valore predefinito globale.
- Quando non è impostata né una destinazione di errore globale né per job, i job che consegnano già tramite `announce` usano come fallback quel target announce primario in caso di errore.
- `delivery.failureDestination` è supportato solo per i job `sessionTarget="isolated"` a meno che il `delivery.mode` primario del job non sia `"webhook"`.

Vedi [Cron Jobs](/it/automation/cron-jobs). Le esecuzioni Cron isolate vengono tracciate come [task in background](/it/automation/tasks).

---

## Variabili template del modello media

Segnaposto template espansi in `tools.media.models[].args`:

| Variabile          | Descrizione                                     |
| ------------------ | ----------------------------------------------- |
| `{{Body}}`         | Corpo completo del messaggio in ingresso        |
| `{{RawBody}}`      | Corpo raw (senza wrapper di cronologia/mittente) |
| `{{BodyStripped}}` | Corpo con le menzioni di gruppo rimosse         |
| `{{From}}`         | Identificatore del mittente                     |
| `{{To}}`           | Identificatore della destinazione               |
| `{{MessageSid}}`   | ID del messaggio del canale                     |
| `{{SessionId}}`    | UUID della sessione corrente                    |
| `{{IsNewSession}}` | `"true"` quando viene creata una nuova sessione |
| `{{MediaUrl}}`     | pseudo-URL del media in ingresso                |
| `{{MediaPath}}`    | percorso locale del media                       |
| `{{MediaType}}`    | tipo di media (image/audio/document/…)          |
| `{{Transcript}}`   | trascrizione audio                              |
| `{{Prompt}}`       | prompt media risolto per le voci CLI            |
| `{{MaxChars}}`     | caratteri massimi di output risolti per le voci CLI |
| `{{ChatType}}`     | `"direct"` oppure `"group"`                     |
| `{{GroupSubject}}` | oggetto del gruppo (best effort)                |
| `{{GroupMembers}}` | anteprima dei membri del gruppo (best effort)   |
| `{{SenderName}}`   | nome visualizzato del mittente (best effort)    |
| `{{SenderE164}}`   | numero di telefono del mittente (best effort)   |
| `{{Provider}}`     | suggerimento provider (whatsapp, telegram, discord, ecc.) |

---

## Include di configurazione (`$include`)

Dividi la configurazione in più file:

```json5
// ~/.openclaw/openclaw.json
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  broadcast: {
    $include: ["./clients/mueller.json5", "./clients/schmidt.json5"],
  },
}
```

**Comportamento di merge:**

- File singolo: sostituisce l'oggetto contenitore.
- Array di file: deep-merge in ordine (gli ultimi sovrascrivono i precedenti).
- Chiavi sibling: unite dopo gli include (sovrascrivono i valori inclusi).
- Include annidati: fino a 10 livelli di profondità.
- Percorsi: risolti relativamente al file che include, ma devono restare all'interno della directory di configurazione di primo livello (`dirname` di `openclaw.json`). Le forme assolute/`../` sono consentite solo quando si risolvono comunque all'interno di quel limite.
- Errori: messaggi chiari per file mancanti, errori di parsing e include circolari.

---

_Correlati: [Configuration](/it/gateway/configuration) · [Configuration Examples](/it/gateway/configuration-examples) · [Doctor](/it/gateway/doctor)_
