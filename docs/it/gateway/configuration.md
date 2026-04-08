---
read_when:
    - Configurare OpenClaw per la prima volta
    - Cercare modelli di configurazione comuni
    - Passare a sezioni specifiche della configurazione
summary: 'Panoramica della configurazione: attività comuni, configurazione rapida e link al riferimento completo'
title: Configurazione
x-i18n:
    generated_at: "2026-04-08T06:01:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 199a1e515bd4003319e71593a2659bb883299a76ff67e273d92583df03c96604
    source_path: gateway/configuration.md
    workflow: 15
---

# Configurazione

OpenClaw legge una configurazione facoltativa in <Tooltip tip="JSON5 supporta commenti e virgole finali">**JSON5**</Tooltip> da `~/.openclaw/openclaw.json`.

Se il file manca, OpenClaw usa impostazioni predefinite sicure. Motivi comuni per aggiungere una configurazione:

- Collegare i canali e controllare chi può inviare messaggi al bot
- Impostare modelli, strumenti, sandboxing o automazione (cron, hook)
- Regolare sessioni, contenuti multimediali, rete o UI

Consulta il [riferimento completo](/it/gateway/configuration-reference) per ogni campo disponibile.

<Tip>
**Sei nuovo alla configurazione?** Inizia con `openclaw onboard` per una configurazione interattiva, oppure consulta la guida [Esempi di configurazione](/it/gateway/configuration-examples) per configurazioni complete da copiare e incollare.
</Tip>

## Configurazione minima

```json5
// ~/.openclaw/openclaw.json
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

## Modifica della configurazione

<Tabs>
  <Tab title="Procedura guidata interattiva">
    ```bash
    openclaw onboard       # flusso di onboarding completo
    openclaw configure     # procedura guidata di configurazione
    ```
  </Tab>
  <Tab title="CLI (one-liner)">
    ```bash
    openclaw config get agents.defaults.workspace
    openclaw config set agents.defaults.heartbeat.every "2h"
    openclaw config unset plugins.entries.brave.config.webSearch.apiKey
    ```
  </Tab>
  <Tab title="UI di controllo">
    Apri [http://127.0.0.1:18789](http://127.0.0.1:18789) e usa la scheda **Config**.
    La UI di controllo visualizza un modulo dallo schema di configurazione live, inclusi i metadati della documentazione dei campi
    `title` / `description` più gli schemi di plugin e canali quando
    disponibili, con un editor **Raw JSON** come via di fuga. Per UI di
    approfondimento e altri strumenti, il gateway espone anche `config.schema.lookup` per
    recuperare un nodo dello schema limitato a un percorso più riepiloghi immediati dei nodi figli.
  </Tab>
  <Tab title="Modifica diretta">
    Modifica direttamente `~/.openclaw/openclaw.json`. Il Gateway osserva il file e applica automaticamente le modifiche (vedi [ricaricamento a caldo](#config-hot-reload)).
  </Tab>
</Tabs>

## Convalida rigorosa

<Warning>
OpenClaw accetta solo configurazioni che corrispondono completamente allo schema. Chiavi sconosciute, tipi non validi o valori non validi fanno sì che il Gateway **si rifiuti di avviarsi**. L'unica eccezione a livello root è `$schema` (stringa), così gli editor possono associare metadati JSON Schema.
</Warning>

Note sugli strumenti dello schema:

- `openclaw config schema` stampa la stessa famiglia di JSON Schema usata dalla UI di controllo
  e dalla convalida della configurazione.
- Tratta l'output di quello schema come il contratto canonico leggibile dalle macchine per
  `openclaw.json`; questa panoramica e il riferimento di configurazione lo riassumono.
- I valori dei campi `title` e `description` vengono riportati nell'output dello schema per
  strumenti di editing e moduli.
- Le voci di oggetti nidificati, wildcard (`*`) e elementi di array (`[]`) ereditano gli stessi
  metadati della documentazione dove esiste documentazione del campo corrispondente.
- Anche i rami di composizione `anyOf` / `oneOf` / `allOf` ereditano gli stessi
  metadati della documentazione, così le varianti union/intersection mantengono lo stesso aiuto per il campo.
- `config.schema.lookup` restituisce un percorso di configurazione normalizzato con un nodo di
  schema superficiale (`title`, `description`, `type`, `enum`, `const`, limiti comuni
  e campi di convalida simili), metadati dei suggerimenti UI corrispondenti e riepiloghi immediati dei nodi figli
  per strumenti di approfondimento.
- Gli schemi runtime di plugin/canali vengono uniti quando il gateway può caricare il
  registro dei manifest corrente.
- `pnpm config:docs:check` rileva divergenze tra gli artefatti di baseline della configurazione rivolti alla documentazione
  e la superficie dello schema corrente.

Quando la convalida fallisce:

- Il Gateway non si avvia
- Funzionano solo i comandi diagnostici (`openclaw doctor`, `openclaw logs`, `openclaw health`, `openclaw status`)
- Esegui `openclaw doctor` per vedere i problemi esatti
- Esegui `openclaw doctor --fix` (o `--yes`) per applicare le riparazioni

## Attività comuni

<AccordionGroup>
  <Accordion title="Configurare un canale (WhatsApp, Telegram, Discord, ecc.)">
    Ogni canale ha la propria sezione di configurazione sotto `channels.<provider>`. Consulta la pagina dedicata al canale per i passaggi di configurazione:

    - [WhatsApp](/it/channels/whatsapp) — `channels.whatsapp`
    - [Telegram](/it/channels/telegram) — `channels.telegram`
    - [Discord](/it/channels/discord) — `channels.discord`
    - [Feishu](/it/channels/feishu) — `channels.feishu`
    - [Google Chat](/it/channels/googlechat) — `channels.googlechat`
    - [Microsoft Teams](/it/channels/msteams) — `channels.msteams`
    - [Slack](/it/channels/slack) — `channels.slack`
    - [Signal](/it/channels/signal) — `channels.signal`
    - [iMessage](/it/channels/imessage) — `channels.imessage`
    - [Mattermost](/it/channels/mattermost) — `channels.mattermost`

    Tutti i canali condividono lo stesso modello di criterio DM:

    ```json5
    {
      channels: {
        telegram: {
          enabled: true,
          botToken: "123:abc",
          dmPolicy: "pairing",   // pairing | allowlist | open | disabled
          allowFrom: ["tg:123"], // solo per allowlist/open
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Scegliere e configurare i modelli">
    Imposta il modello primario e gli eventuali fallback:

    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "anthropic/claude-sonnet-4-6",
            fallbacks: ["openai/gpt-5.4"],
          },
          models: {
            "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
            "openai/gpt-5.4": { alias: "GPT" },
          },
        },
      },
    }
    ```

    - `agents.defaults.models` definisce il catalogo dei modelli e funge da allowlist per `/model`.
    - I riferimenti ai modelli usano il formato `provider/model` (ad esempio `anthropic/claude-opus-4-6`).
    - `agents.defaults.imageMaxDimensionPx` controlla il ridimensionamento delle immagini di transcript/tool (predefinito `1200`); valori più bassi di solito riducono l'uso di vision token nelle esecuzioni ricche di screenshot.
    - Consulta [Models CLI](/it/concepts/models) per cambiare modello in chat e [Model Failover](/it/concepts/model-failover) per il comportamento di rotazione dell'autenticazione e fallback.
    - Per provider personalizzati/self-hosted, consulta [Provider personalizzati](/it/gateway/configuration-reference#custom-providers-and-base-urls) nel riferimento.

  </Accordion>

  <Accordion title="Controllare chi può inviare messaggi al bot">
    L'accesso DM è controllato per canale tramite `dmPolicy`:

    - `"pairing"` (predefinito): i mittenti sconosciuti ricevono un codice di pairing monouso da approvare
    - `"allowlist"`: solo i mittenti in `allowFrom` (o nello store allow associato)
    - `"open"`: consenti tutti i DM in ingresso (richiede `allowFrom: ["*"]`)
    - `"disabled"`: ignora tutti i DM

    Per i gruppi, usa `groupPolicy` + `groupAllowFrom` o allowlist specifiche del canale.

    Consulta il [riferimento completo](/it/gateway/configuration-reference#dm-and-group-access) per i dettagli per canale.

  </Accordion>

  <Accordion title="Configurare il filtro per menzione nelle chat di gruppo">
    Per impostazione predefinita, i messaggi di gruppo **richiedono una menzione**. Configura i pattern per agente:

    ```json5
    {
      agents: {
        list: [
          {
            id: "main",
            groupChat: {
              mentionPatterns: ["@openclaw", "openclaw"],
            },
          },
        ],
      },
      channels: {
        whatsapp: {
          groups: { "*": { requireMention: true } },
        },
      },
    }
    ```

    - **Menzioni nei metadati**: @-mention native (WhatsApp tap-to-mention, Telegram @bot, ecc.)
    - **Pattern di testo**: pattern regex sicuri in `mentionPatterns`
    - Consulta il [riferimento completo](/it/gateway/configuration-reference#group-chat-mention-gating) per gli override per canale e la modalità self-chat.

  </Accordion>

  <Accordion title="Limitare le Skills per agente">
    Usa `agents.defaults.skills` per una baseline condivisa, quindi fai override di agenti specifici con `agents.list[].skills`:

    ```json5
    {
      agents: {
        defaults: {
          skills: ["github", "weather"],
        },
        list: [
          { id: "writer" }, // eredita github, weather
          { id: "docs", skills: ["docs-search"] }, // sostituisce i valori predefiniti
          { id: "locked-down", skills: [] }, // nessuna Skills
        ],
      },
    }
    ```

    - Ometti `agents.defaults.skills` per Skills senza restrizioni per impostazione predefinita.
    - Ometti `agents.list[].skills` per ereditare i valori predefiniti.
    - Imposta `agents.list[].skills: []` per nessuna Skills.
    - Consulta [Skills](/it/tools/skills), [Configurazione delle Skills](/it/tools/skills-config), e
      il [Riferimento di configurazione](/it/gateway/configuration-reference#agentsdefaultsskills).

  </Accordion>

  <Accordion title="Regolare il monitoraggio dello stato dei canali del gateway">
    Controlla quanto aggressivamente il gateway riavvia i canali che sembrano inattivi:

    ```json5
    {
      gateway: {
        channelHealthCheckMinutes: 5,
        channelStaleEventThresholdMinutes: 30,
        channelMaxRestartsPerHour: 10,
      },
      channels: {
        telegram: {
          healthMonitor: { enabled: false },
          accounts: {
            alerts: {
              healthMonitor: { enabled: true },
            },
          },
        },
      },
    }
    ```

    - Imposta `gateway.channelHealthCheckMinutes: 0` per disabilitare globalmente i riavvii del monitor di stato.
    - `channelStaleEventThresholdMinutes` deve essere maggiore o uguale all'intervallo di controllo.
    - Usa `channels.<provider>.healthMonitor.enabled` o `channels.<provider>.accounts.<id>.healthMonitor.enabled` per disabilitare i riavvii automatici per un canale o account senza disabilitare il monitor globale.
    - Consulta [Controlli di stato](/it/gateway/health) per il debug operativo e il [riferimento completo](/it/gateway/configuration-reference#gateway) per tutti i campi.

  </Accordion>

  <Accordion title="Configurare sessioni e reimpostazioni">
    Le sessioni controllano la continuità e l'isolamento delle conversazioni:

    ```json5
    {
      session: {
        dmScope: "per-channel-peer",  // consigliato per più utenti
        threadBindings: {
          enabled: true,
          idleHours: 24,
          maxAgeHours: 0,
        },
        reset: {
          mode: "daily",
          atHour: 4,
          idleMinutes: 120,
        },
      },
    }
    ```

    - `dmScope`: `main` (condivisa) | `per-peer` | `per-channel-peer` | `per-account-channel-peer`
    - `threadBindings`: valori predefiniti globali per l'instradamento delle sessioni associate ai thread (Discord supporta `/focus`, `/unfocus`, `/agents`, `/session idle` e `/session max-age`).
    - Consulta [Gestione delle sessioni](/it/concepts/session) per ambito, collegamenti di identità e criterio di invio.
    - Consulta il [riferimento completo](/it/gateway/configuration-reference#session) per tutti i campi.

  </Accordion>

  <Accordion title="Abilitare il sandboxing">
    Esegui le sessioni dell'agente in container Docker isolati:

    ```json5
    {
      agents: {
        defaults: {
          sandbox: {
            mode: "non-main",  // off | non-main | all
            scope: "agent",    // session | agent | shared
          },
        },
      },
    }
    ```

    Crea prima l'immagine: `scripts/sandbox-setup.sh`

    Consulta [Sandboxing](/it/gateway/sandboxing) per la guida completa e il [riferimento completo](/it/gateway/configuration-reference#agentsdefaultssandbox) per tutte le opzioni.

  </Accordion>

  <Accordion title="Abilitare il push supportato da relay per le build iOS ufficiali">
    Il push supportato da relay è configurato in `openclaw.json`.

    Imposta questo nella configurazione del gateway:

    ```json5
    {
      gateway: {
        push: {
          apns: {
            relay: {
              baseUrl: "https://relay.example.com",
              // Facoltativo. Predefinito: 10000
              timeoutMs: 10000,
            },
          },
        },
      },
    }
    ```

    Equivalente CLI:

    ```bash
    openclaw config set gateway.push.apns.relay.baseUrl https://relay.example.com
    ```

    Cosa fa:

    - Consente al gateway di inviare `push.test`, solleciti di wake e wake di riconnessione tramite il relay esterno.
    - Usa un'autorizzazione di invio limitata alla registrazione inoltrata dall'app iOS associata. Il gateway non ha bisogno di un token relay valido per l'intera distribuzione.
    - Associa ogni registrazione supportata da relay all'identità del gateway con cui l'app iOS è stata associata, così un altro gateway non può riutilizzare la registrazione memorizzata.
    - Mantiene le build iOS locali/manuali su APNs diretto. Gli invii supportati da relay si applicano solo alle build ufficiali distribuite che si sono registrate tramite il relay.
    - Deve corrispondere al base URL del relay incorporato nella build iOS ufficiale/TestFlight, così il traffico di registrazione e invio raggiunge la stessa distribuzione relay.

    Flusso end-to-end:

    1. Installa una build iOS ufficiale/TestFlight compilata con lo stesso base URL del relay.
    2. Configura `gateway.push.apns.relay.baseUrl` sul gateway.
    3. Associa l'app iOS al gateway e lascia che si connettano sia le sessioni node sia quelle operatore.
    4. L'app iOS recupera l'identità del gateway, si registra presso il relay usando App Attest più la ricevuta dell'app e poi pubblica il payload `push.apns.register` supportato da relay sul gateway associato.
    5. Il gateway memorizza l'handle relay e l'autorizzazione di invio, quindi li usa per `push.test`, solleciti di wake e wake di riconnessione.

    Note operative:

    - Se passi l'app iOS a un gateway diverso, riconnetti l'app così può pubblicare una nuova registrazione relay associata a quel gateway.
    - Se distribuisci una nuova build iOS che punta a una distribuzione relay diversa, l'app aggiorna la registrazione relay memorizzata nella cache invece di riutilizzare il vecchio relay di origine.

    Nota di compatibilità:

    - `OPENCLAW_APNS_RELAY_BASE_URL` e `OPENCLAW_APNS_RELAY_TIMEOUT_MS` funzionano ancora come override temporanei dell'env.
    - `OPENCLAW_APNS_RELAY_ALLOW_HTTP=true` resta una via di fuga di sviluppo solo loopback; non rendere persistenti URL relay HTTP nella configurazione.

    Consulta [App iOS](/it/platforms/ios#relay-backed-push-for-official-builds) per il flusso end-to-end e [Flusso di autenticazione e trust](/it/platforms/ios#authentication-and-trust-flow) per il modello di sicurezza del relay.

  </Accordion>

  <Accordion title="Configurare heartbeat (check-in periodici)">
    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "30m",
            target: "last",
          },
        },
      },
    }
    ```

    - `every`: stringa di durata (`30m`, `2h`). Imposta `0m` per disabilitare.
    - `target`: `last` | `none` | `<channel-id>` (ad esempio `discord`, `matrix`, `telegram` o `whatsapp`)
    - `directPolicy`: `allow` (predefinito) o `block` per target heartbeat in stile DM
    - Consulta [Heartbeat](/it/gateway/heartbeat) per la guida completa.

  </Accordion>

  <Accordion title="Configurare job cron">
    ```json5
    {
      cron: {
        enabled: true,
        maxConcurrentRuns: 2,
        sessionRetention: "24h",
        runLog: {
          maxBytes: "2mb",
          keepLines: 2000,
        },
      },
    }
    ```

    - `sessionRetention`: elimina dalle `sessions.json` le sessioni isolate completate (predefinito `24h`; imposta `false` per disabilitare).
    - `runLog`: riduce `cron/runs/<jobId>.jsonl` in base a dimensione e righe mantenute.
    - Consulta [Job cron](/it/automation/cron-jobs) per la panoramica della funzionalità e gli esempi CLI.

  </Accordion>

  <Accordion title="Configurare webhook (hook)">
    Abilita endpoint webhook HTTP sul Gateway:

    ```json5
    {
      hooks: {
        enabled: true,
        token: "shared-secret",
        path: "/hooks",
        defaultSessionKey: "hook:ingress",
        allowRequestSessionKey: false,
        allowedSessionKeyPrefixes: ["hook:"],
        mappings: [
          {
            match: { path: "gmail" },
            action: "agent",
            agentId: "main",
            deliver: true,
          },
        ],
      },
    }
    ```

    Nota sulla sicurezza:
    - Tratta tutto il contenuto dei payload hook/webhook come input non attendibile.
    - Usa un `hooks.token` dedicato; non riutilizzare il token condiviso del Gateway.
    - L'autenticazione degli hook è solo tramite header (`Authorization: Bearer ...` o `x-openclaw-token`); i token nella query string vengono rifiutati.
    - `hooks.path` non può essere `/`; mantieni l'ingresso webhook su un sottopercorso dedicato come `/hooks`.
    - Mantieni disabilitati i flag di bypass per contenuti non sicuri (`hooks.gmail.allowUnsafeExternalContent`, `hooks.mappings[].allowUnsafeExternalContent`) a meno che tu non stia facendo debug strettamente circoscritto.
    - Se abiliti `hooks.allowRequestSessionKey`, imposta anche `hooks.allowedSessionKeyPrefixes` per limitare le chiavi di sessione selezionate dal chiamante.
    - Per agenti guidati da hook, preferisci tier di modelli moderni e robusti e un criterio tool rigoroso (ad esempio solo messaggistica più sandboxing dove possibile).

    Consulta il [riferimento completo](/it/gateway/configuration-reference#hooks) per tutte le opzioni di mapping e l'integrazione con Gmail.

  </Accordion>

  <Accordion title="Configurare l'instradamento multi-agent">
    Esegui più agenti isolati con workspace e sessioni separate:

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

    Consulta [Multi-Agent](/it/concepts/multi-agent) e il [riferimento completo](/it/gateway/configuration-reference#multi-agent-routing) per le regole di binding e i profili di accesso per agente.

  </Accordion>

  <Accordion title="Suddividere la configurazione in più file ($include)">
    Usa `$include` per organizzare configurazioni di grandi dimensioni:

    ```json5
    // ~/.openclaw/openclaw.json
    {
      gateway: { port: 18789 },
      agents: { $include: "./agents.json5" },
      broadcast: {
        $include: ["./clients/a.json5", "./clients/b.json5"],
      },
    }
    ```

    - **File singolo**: sostituisce l'oggetto contenitore
    - **Array di file**: unione profonda in ordine (vince l'ultimo)
    - **Chiavi sibling**: unite dopo gli include (sovrascrivono i valori inclusi)
    - **Include nidificati**: supportati fino a 10 livelli di profondità
    - **Percorsi relativi**: risolti relativamente al file che include
    - **Gestione degli errori**: errori chiari per file mancanti, errori di parsing e include circolari

  </Accordion>
</AccordionGroup>

## Ricaricamento a caldo della configurazione

Il Gateway osserva `~/.openclaw/openclaw.json` e applica automaticamente le modifiche — nella maggior parte dei casi non è necessario alcun riavvio manuale.

### Modalità di ricaricamento

| Modalità               | Comportamento                                                                          |
| ---------------------- | -------------------------------------------------------------------------------------- |
| **`hybrid`** (predefinita) | Applica a caldo immediatamente le modifiche sicure. Riavvia automaticamente per quelle critiche. |
| **`hot`**              | Applica a caldo solo le modifiche sicure. Registra un avviso quando è necessario un riavvio — te ne occupi tu. |
| **`restart`**          | Riavvia il Gateway per qualsiasi modifica della configurazione, sicura o meno.         |
| **`off`**              | Disabilita l'osservazione del file. Le modifiche hanno effetto al successivo riavvio manuale. |

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

### Cosa viene applicato a caldo e cosa richiede un riavvio

La maggior parte dei campi viene applicata a caldo senza downtime. In modalità `hybrid`, le modifiche che richiedono riavvio vengono gestite automaticamente.

| Categoria            | Campi                                                                | Riavvio necessario? |
| -------------------- | -------------------------------------------------------------------- | ------------------- |
| Canali               | `channels.*`, `web` (WhatsApp) — tutti i canali built-in e di estensione | No                  |
| Agente e modelli     | `agent`, `agents`, `models`, `routing`                               | No                  |
| Automazione          | `hooks`, `cron`, `agent.heartbeat`                                   | No                  |
| Sessioni e messaggi  | `session`, `messages`                                                | No                  |
| Strumenti e media    | `tools`, `browser`, `skills`, `audio`, `talk`                        | No                  |
| UI e varie           | `ui`, `logging`, `identity`, `bindings`                              | No                  |
| Server gateway       | `gateway.*` (port, bind, auth, tailscale, TLS, HTTP)                 | **Sì**              |
| Infrastruttura       | `discovery`, `canvasHost`, `plugins`                                 | **Sì**              |

<Note>
`gateway.reload` e `gateway.remote` sono eccezioni — modificarli **non** attiva un riavvio.
</Note>

## RPC di configurazione (aggiornamenti programmatici)

<Note>
Le RPC di scrittura del control plane (`config.apply`, `config.patch`, `update.run`) sono soggette a rate limit di **3 richieste ogni 60 secondi** per `deviceId+clientIp`. Quando si raggiunge il limite, la RPC restituisce `UNAVAILABLE` con `retryAfterMs`.
</Note>

Flusso sicuro/predefinito:

- `config.schema.lookup`: ispeziona un sottoalbero della configurazione limitato a un percorso con un nodo di schema superficiale,
  metadati dei suggerimenti corrispondenti e riepiloghi immediati dei nodi figli
- `config.get`: recupera lo snapshot corrente + hash
- `config.patch`: percorso preferito per aggiornamenti parziali
- `config.apply`: solo sostituzione completa della configurazione
- `update.run`: autoaggiornamento esplicito + riavvio

Quando non stai sostituendo l'intera configurazione, preferisci `config.schema.lookup`
poi `config.patch`.

<AccordionGroup>
  <Accordion title="config.apply (sostituzione completa)">
    Convalida + scrive l'intera configurazione e riavvia il Gateway in un solo passaggio.

    <Warning>
    `config.apply` sostituisce l'**intera configurazione**. Usa `config.patch` per aggiornamenti parziali, oppure `openclaw config set` per singole chiavi.
    </Warning>

    Parametri:

    - `raw` (stringa) — payload JSON5 per l'intera configurazione
    - `baseHash` (facoltativo) — hash della configurazione da `config.get` (richiesto quando la configurazione esiste)
    - `sessionKey` (facoltativo) — chiave di sessione per il ping di riattivazione post-riavvio
    - `note` (facoltativo) — nota per il sentinel di riavvio
    - `restartDelayMs` (facoltativo) — ritardo prima del riavvio (predefinito 2000)

    Le richieste di riavvio vengono accorpate mentre una è già in attesa/in corso, e si applica un cooldown di 30 secondi tra i cicli di riavvio.

    ```bash
    openclaw gateway call config.get --params '{}'  # acquisisci payload.hash
    openclaw gateway call config.apply --params '{
      "raw": "{ agents: { defaults: { workspace: \"~/.openclaw/workspace\" } } }",
      "baseHash": "<hash>",
      "sessionKey": "agent:main:whatsapp:direct:+15555550123"
    }'
    ```

  </Accordion>

  <Accordion title="config.patch (aggiornamento parziale)">
    Unisce un aggiornamento parziale nella configurazione esistente (semantica JSON merge patch):

    - Gli oggetti vengono uniti ricorsivamente
    - `null` elimina una chiave
    - Gli array vengono sostituiti

    Parametri:

    - `raw` (stringa) — JSON5 con solo le chiavi da modificare
    - `baseHash` (obbligatorio) — hash della configurazione da `config.get`
    - `sessionKey`, `note`, `restartDelayMs` — uguali a `config.apply`

    Il comportamento di riavvio corrisponde a `config.apply`: riavvii in attesa accorpati più un cooldown di 30 secondi tra i cicli di riavvio.

    ```bash
    openclaw gateway call config.patch --params '{
      "raw": "{ channels: { telegram: { groups: { \"*\": { requireMention: false } } } } }",
      "baseHash": "<hash>"
    }'
    ```

  </Accordion>
</AccordionGroup>

## Variabili d'ambiente

OpenClaw legge le variabili d'ambiente dal processo padre più:

- `.env` dalla directory di lavoro corrente (se presente)
- `~/.openclaw/.env` (fallback globale)

Nessuno dei due file sovrascrive le variabili d'ambiente esistenti. Puoi anche impostare variabili d'ambiente inline nella configurazione:

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

<Accordion title="Importazione env della shell (facoltativa)">
  Se abilitato e le chiavi previste non sono impostate, OpenClaw esegue la tua login shell e importa solo le chiavi mancanti:

```json5
{
  env: {
    shellEnv: { enabled: true, timeoutMs: 15000 },
  },
}
```

Equivalente come variabile d'ambiente: `OPENCLAW_LOAD_SHELL_ENV=1`
</Accordion>

<Accordion title="Sostituzione di variabili d'ambiente nei valori di configurazione">
  Riferisci le variabili d'ambiente in qualsiasi valore stringa della configurazione con `${VAR_NAME}`:

```json5
{
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } },
  models: { providers: { custom: { apiKey: "${CUSTOM_API_KEY}" } } },
}
```

Regole:

- Vengono corrisposti solo nomi in maiuscolo: `[A-Z_][A-Z0-9_]*`
- Variabili mancanti/vuote generano un errore in fase di caricamento
- Usa l'escape `$${VAR}` per output letterale
- Funziona all'interno dei file `$include`
- Sostituzione inline: `"${BASE}/v1"` → `"https://api.example.com/v1"`

</Accordion>

<Accordion title="Riferimenti a segreti (env, file, exec)">
  Per i campi che supportano oggetti SecretRef, puoi usare:

```json5
{
  models: {
    providers: {
      openai: { apiKey: { source: "env", provider: "default", id: "OPENAI_API_KEY" } },
    },
  },
  skills: {
    entries: {
      "image-lab": {
        apiKey: {
          source: "file",
          provider: "filemain",
          id: "/skills/entries/image-lab/apiKey",
        },
      },
    },
  },
  channels: {
    googlechat: {
      serviceAccountRef: {
        source: "exec",
        provider: "vault",
        id: "channels/googlechat/serviceAccount",
      },
    },
  },
}
```

I dettagli di SecretRef (inclusi `secrets.providers` per `env`/`file`/`exec`) sono in [Gestione dei segreti](/it/gateway/secrets).
I percorsi delle credenziali supportati sono elencati in [Superficie delle credenziali SecretRef](/it/reference/secretref-credential-surface).
</Accordion>

Consulta [Ambiente](/it/help/environment) per la precedenza completa e le origini.

## Riferimento completo

Per il riferimento completo campo per campo, consulta **[Riferimento di configurazione](/it/gateway/configuration-reference)**.

---

_Correlati: [Esempi di configurazione](/it/gateway/configuration-examples) · [Riferimento di configurazione](/it/gateway/configuration-reference) · [Doctor](/it/gateway/doctor)_
