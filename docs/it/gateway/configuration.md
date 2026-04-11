---
read_when:
    - Configurare OpenClaw per la prima volta
    - Cerchi schemi di configurazione comuni?
    - Passare a sezioni specifiche della configurazione
summary: 'Panoramica della configurazione: attività comuni, configurazione rapida e collegamenti al riferimento completo'
title: Configurazione
x-i18n:
    generated_at: "2026-04-11T02:44:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: e874be80d11b9123cac6ce597ec02667fbc798f622a076f68535a1af1f0e399c
    source_path: gateway/configuration.md
    workflow: 15
---

# Configurazione

OpenClaw legge una configurazione <Tooltip tip="JSON5 supports comments and trailing commas">**JSON5**</Tooltip> facoltativa da `~/.openclaw/openclaw.json`.

Se il file non esiste, OpenClaw usa impostazioni predefinite sicure. Motivi comuni per aggiungere una configurazione:

- Connettere i canali e controllare chi può inviare messaggi al bot
- Impostare modelli, strumenti, sandboxing o automazione (cron, hook)
- Regolare sessioni, media, rete o UI

Consulta il [riferimento completo](/it/gateway/configuration-reference) per ogni campo disponibile.

<Tip>
**Sei nuovo alla configurazione?** Inizia con `openclaw onboard` per una configurazione interattiva, oppure dai un'occhiata alla guida [Esempi di configurazione](/it/gateway/configuration-examples) per configurazioni complete da copiare e incollare.
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
    openclaw onboard       # flusso completo di onboarding
    openclaw configure     # procedura guidata di configurazione
    ```
  </Tab>
  <Tab title="CLI (comandi su una sola riga)">
    ```bash
    openclaw config get agents.defaults.workspace
    openclaw config set agents.defaults.heartbeat.every "2h"
    openclaw config unset plugins.entries.brave.config.webSearch.apiKey
    ```
  </Tab>
  <Tab title="Control UI">
    Apri [http://127.0.0.1:18789](http://127.0.0.1:18789) e usa la scheda **Config**.
    La Control UI visualizza un modulo basato sullo schema di configurazione attivo, inclusi i metadati di documentazione dei campi `title` / `description` e gli schemi di plugin e canali quando disponibili, con un editor **Raw JSON** come soluzione di ripiego. Per UI di approfondimento e altri strumenti, il gateway espone anche `config.schema.lookup` per recuperare un nodo di schema limitato a un percorso insieme ai riepiloghi immediati dei figli.
  </Tab>
  <Tab title="Modifica diretta">
    Modifica direttamente `~/.openclaw/openclaw.json`. Il Gateway monitora il file e applica automaticamente le modifiche (vedi [ricaricamento a caldo](#config-hot-reload)).
  </Tab>
</Tabs>

## Validazione rigorosa

<Warning>
OpenClaw accetta solo configurazioni che corrispondono completamente allo schema. Chiavi sconosciute, tipi non validi o valori non validi fanno sì che il Gateway **si rifiuti di avviarsi**. L'unica eccezione a livello radice è `$schema` (stringa), così gli editor possono associare i metadati dello schema JSON.
</Warning>

Note sugli strumenti dello schema:

- `openclaw config schema` stampa la stessa famiglia di schemi JSON usata da Control UI e dalla validazione della configurazione.
- Considera l'output di quello schema come il contratto canonico leggibile dalle macchine per `openclaw.json`; questa panoramica e il riferimento della configurazione lo riassumono.
- I valori dei campi `title` e `description` vengono riportati nell'output dello schema per gli strumenti di editing e dei moduli.
- Le voci di oggetti annidati, wildcard (`*`) e elementi di array (`[]`) ereditano gli stessi metadati di documentazione quando esiste la documentazione del campo corrispondente.
- Anche i rami di composizione `anyOf` / `oneOf` / `allOf` ereditano gli stessi metadati di documentazione, così le varianti union/intersection mantengono lo stesso aiuto per il campo.
- `config.schema.lookup` restituisce un percorso di configurazione normalizzato con un nodo di schema superficiale (`title`, `description`, `type`, `enum`, `const`, limiti comuni e campi di validazione simili), i metadati di suggerimento UI corrispondenti e i riepiloghi immediati dei figli per gli strumenti di approfondimento.
- Gli schemi runtime di plugin/canali vengono uniti quando il gateway può caricare il registro manifest corrente.
- `pnpm config:docs:check` rileva disallineamenti tra gli artefatti baseline della configurazione orientati alla documentazione e la superficie di schema corrente.

Quando la validazione fallisce:

- Il Gateway non si avvia
- Funzionano solo i comandi diagnostici (`openclaw doctor`, `openclaw logs`, `openclaw health`, `openclaw status`)
- Esegui `openclaw doctor` per vedere i problemi esatti
- Esegui `openclaw doctor --fix` (o `--yes`) per applicare le correzioni

## Attività comuni

<AccordionGroup>
  <Accordion title="Configurare un canale (WhatsApp, Telegram, Discord, ecc.)">
    Ogni canale ha una propria sezione di configurazione sotto `channels.<provider>`. Consulta la pagina dedicata del canale per i passaggi di configurazione:

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

    Tutti i canali condividono lo stesso schema per la policy dei messaggi diretti:

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
    Imposta il modello primario ed eventuali fallback:

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
    - `agents.defaults.imageMaxDimensionPx` controlla il ridimensionamento delle immagini nel transcript/strumenti (predefinito `1200`); valori inferiori di solito riducono l'uso di token di visione nelle esecuzioni ricche di screenshot.
    - Consulta [Models CLI](/it/concepts/models) per cambiare modello in chat e [Model Failover](/it/concepts/model-failover) per il comportamento di rotazione dell'autenticazione e di fallback.
    - Per provider personalizzati/self-hosted, consulta [Provider personalizzati](/it/gateway/configuration-reference#custom-providers-and-base-urls) nel riferimento.

  </Accordion>

  <Accordion title="Controllare chi può inviare messaggi al bot">
    L'accesso ai messaggi diretti è controllato per canale tramite `dmPolicy`:

    - `"pairing"` (predefinito): i mittenti sconosciuti ricevono un codice di pairing monouso da approvare
    - `"allowlist"`: solo i mittenti in `allowFrom` (o nell'archivio allow dei paired)
    - `"open"`: consente tutti i messaggi diretti in ingresso (richiede `allowFrom: ["*"]`)
    - `"disabled"`: ignora tutti i messaggi diretti

    Per i gruppi, usa `groupPolicy` + `groupAllowFrom` o allowlist specifiche del canale.

    Consulta il [riferimento completo](/it/gateway/configuration-reference#dm-and-group-access) per i dettagli per canale.

  </Accordion>

  <Accordion title="Configurare il gating delle menzioni nelle chat di gruppo">
    I messaggi di gruppo richiedono per impostazione predefinita una **menzione obbligatoria**. Configura i pattern per agente:

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

    - **Menzioni nei metadati**: menzioni @ native (@ con tocco su WhatsApp, @bot su Telegram, ecc.)
    - **Pattern di testo**: pattern regex sicuri in `mentionPatterns`
    - Consulta il [riferimento completo](/it/gateway/configuration-reference#group-chat-mention-gating) per override per canale e modalità self-chat.

  </Accordion>

  <Accordion title="Limitare le Skills per agente">
    Usa `agents.defaults.skills` per una baseline condivisa, poi sostituisci agenti specifici con `agents.list[].skills`:

    ```json5
    {
      agents: {
        defaults: {
          skills: ["github", "weather"],
        },
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
    - Imposta `agents.list[].skills: []` per non avere Skills.
    - Consulta [Skills](/it/tools/skills), [Configurazione delle Skills](/it/tools/skills-config) e il [Riferimento della configurazione](/it/gateway/configuration-reference#agents-defaults-skills).

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

    - Imposta `gateway.channelHealthCheckMinutes: 0` per disattivare globalmente i riavvii del monitoraggio dello stato.
    - `channelStaleEventThresholdMinutes` dovrebbe essere maggiore o uguale all'intervallo di controllo.
    - Usa `channels.<provider>.healthMonitor.enabled` o `channels.<provider>.accounts.<id>.healthMonitor.enabled` per disattivare i riavvii automatici per un canale o account senza disattivare il monitor globale.
    - Consulta [Controlli dello stato](/it/gateway/health) per il debug operativo e il [riferimento completo](/it/gateway/configuration-reference#gateway) per tutti i campi.

  </Accordion>

  <Accordion title="Configurare sessioni e reset">
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
    - `threadBindings`: valori predefiniti globali per il routing delle sessioni associate ai thread (Discord supporta `/focus`, `/unfocus`, `/agents`, `/session idle` e `/session max-age`).
    - Consulta [Gestione delle sessioni](/it/concepts/session) per ambito, collegamenti di identità e policy di invio.
    - Consulta il [riferimento completo](/it/gateway/configuration-reference#session) per tutti i campi.

  </Accordion>

  <Accordion title="Abilitare il sandboxing">
    Esegui le sessioni agente in container Docker isolati:

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

  <Accordion title="Abilitare il push basato su relay per le build iOS ufficiali">
    Il push basato su relay si configura in `openclaw.json`.

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

    - Consente al gateway di inviare `push.test`, solleciti di riattivazione e riattivazioni di riconnessione tramite il relay esterno.
    - Usa un'autorizzazione di invio limitata alla registrazione inoltrata dall'app iOS associata. Il gateway non ha bisogno di un token relay valido per l'intero deployment.
    - Associa ogni registrazione supportata da relay all'identità del gateway con cui l'app iOS è stata associata, così un altro gateway non può riutilizzare la registrazione memorizzata.
    - Mantiene le build iOS locali/manuali su APNs diretto. Gli invii supportati da relay si applicano solo alle build ufficiali distribuite che si sono registrate tramite il relay.
    - Deve corrispondere al base URL del relay incorporato nella build iOS ufficiale/TestFlight, in modo che il traffico di registrazione e invio raggiunga lo stesso deployment relay.

    Flusso end-to-end:

    1. Installa una build iOS ufficiale/TestFlight compilata con lo stesso base URL del relay.
    2. Configura `gateway.push.apns.relay.baseUrl` sul gateway.
    3. Associa l'app iOS al gateway e consenti la connessione sia della sessione node sia di quella operatore.
    4. L'app iOS recupera l'identità del gateway, si registra presso il relay usando App Attest più la ricevuta dell'app e quindi pubblica il payload `push.apns.register` supportato da relay nel gateway associato.
    5. Il gateway memorizza l'handle del relay e l'autorizzazione di invio, poi li usa per `push.test`, i solleciti di riattivazione e le riattivazioni di riconnessione.

    Note operative:

    - Se sposti l'app iOS su un gateway diverso, riconnetti l'app in modo che possa pubblicare una nuova registrazione relay associata a quel gateway.
    - Se distribuisci una nuova build iOS che punta a un deployment relay diverso, l'app aggiorna la registrazione relay memorizzata nella cache invece di riutilizzare il vecchio relay di origine.

    Nota di compatibilità:

    - `OPENCLAW_APNS_RELAY_BASE_URL` e `OPENCLAW_APNS_RELAY_TIMEOUT_MS` funzionano ancora come override temporanei tramite variabili di ambiente.
    - `OPENCLAW_APNS_RELAY_ALLOW_HTTP=true` rimane una via di fuga per lo sviluppo solo loopback; non salvare URL relay HTTP nella configurazione.

    Consulta [App iOS](/it/platforms/ios#relay-backed-push-for-official-builds) per il flusso end-to-end e [Flusso di autenticazione e fiducia](/it/platforms/ios#authentication-and-trust-flow) per il modello di sicurezza del relay.

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

    - `every`: stringa durata (`30m`, `2h`). Imposta `0m` per disabilitare.
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

    - `sessionRetention`: elimina le sessioni isolate completate da `sessions.json` (predefinito `24h`; imposta `false` per disabilitare).
    - `runLog`: pota `cron/runs/<jobId>.jsonl` per dimensione e righe mantenute.
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

    Nota di sicurezza:
    - Tratta tutto il contenuto dei payload hook/webhook come input non attendibile.
    - Usa un `hooks.token` dedicato; non riutilizzare il token Gateway condiviso.
    - L'autenticazione degli hook è solo via header (`Authorization: Bearer ...` o `x-openclaw-token`); i token nella query string vengono rifiutati.
    - `hooks.path` non può essere `/`; mantieni l'ingresso dei webhook su un sottopercorso dedicato come `/hooks`.
    - Mantieni disattivati i flag di bypass per contenuti non sicuri (`hooks.gmail.allowUnsafeExternalContent`, `hooks.mappings[].allowUnsafeExternalContent`) a meno che tu non stia facendo debug strettamente circoscritto.
    - Se abiliti `hooks.allowRequestSessionKey`, imposta anche `hooks.allowedSessionKeyPrefixes` per limitare le chiavi di sessione selezionate dal chiamante.
    - Per agenti guidati da hook, preferisci livelli di modello moderni e robusti e una policy degli strumenti rigorosa (ad esempio solo messaggistica più sandboxing dove possibile).

    Consulta il [riferimento completo](/it/gateway/configuration-reference#hooks) per tutte le opzioni di mapping e l'integrazione Gmail.

  </Accordion>

  <Accordion title="Configurare il routing multi-agent">
    Esegui più agenti isolati con workspace e sessioni separati:

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

  <Accordion title="Dividere la configurazione in più file ($include)">
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

    - **File singolo**: sostituisce l'oggetto che lo contiene
    - **Array di file**: unione profonda in ordine (quello successivo prevale)
    - **Chiavi sibling**: unite dopo gli include (sovrascrivono i valori inclusi)
    - **Include annidati**: supportati fino a 10 livelli di profondità
    - **Percorsi relativi**: risolti rispetto al file che include
    - **Gestione errori**: errori chiari per file mancanti, errori di parsing e include circolari

  </Accordion>
</AccordionGroup>

## Ricaricamento a caldo della configurazione

Il Gateway monitora `~/.openclaw/openclaw.json` e applica automaticamente le modifiche — per la maggior parte delle impostazioni non è necessario alcun riavvio manuale.

### Modalità di ricaricamento

| Modalità               | Comportamento                                                                          |
| ---------------------- | -------------------------------------------------------------------------------------- |
| **`hybrid`** (predefinita) | Applica a caldo istantaneamente le modifiche sicure. Riavvia automaticamente per quelle critiche. |
| **`hot`**              | Applica a caldo solo le modifiche sicure. Registra un avviso quando serve un riavvio — lo gestisci tu. |
| **`restart`**          | Riavvia il Gateway a ogni modifica della configurazione, sicura o meno.                |
| **`off`**              | Disabilita il monitoraggio del file. Le modifiche hanno effetto al successivo riavvio manuale. |

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

### Cosa viene applicato a caldo e cosa richiede un riavvio

La maggior parte dei campi viene applicata a caldo senza downtime. In modalità `hybrid`, le modifiche che richiedono un riavvio vengono gestite automaticamente.

| Categoria            | Campi                                                                | Riavvio necessario? |
| -------------------- | -------------------------------------------------------------------- | ------------------- |
| Canali               | `channels.*`, `web` (WhatsApp) — tutti i canali integrati e di estensione | No                  |
| Agente e modelli     | `agent`, `agents`, `models`, `routing`                               | No                  |
| Automazione          | `hooks`, `cron`, `agent.heartbeat`                                   | No                  |
| Sessioni e messaggi  | `session`, `messages`                                                | No                  |
| Strumenti e media    | `tools`, `browser`, `skills`, `audio`, `talk`                        | No                  |
| UI e varie           | `ui`, `logging`, `identity`, `bindings`                              | No                  |
| Server gateway       | `gateway.*` (porta, bind, auth, tailscale, TLS, HTTP)                | **Sì**              |
| Infrastruttura       | `discovery`, `canvasHost`, `plugins`                                 | **Sì**              |

<Note>
`gateway.reload` e `gateway.remote` sono eccezioni: modificarli **non** attiva un riavvio.
</Note>

## Config RPC (aggiornamenti programmatici)

<Note>
Le RPC di scrittura del control plane (`config.apply`, `config.patch`, `update.run`) sono soggette a rate limit di **3 richieste ogni 60 secondi** per `deviceId+clientIp`. Quando viene applicato il limite, la RPC restituisce `UNAVAILABLE` con `retryAfterMs`.
</Note>

Flusso sicuro/predefinito:

- `config.schema.lookup`: ispeziona un sottoalbero di configurazione limitato a un percorso con un nodo di schema superficiale, metadati di suggerimento corrispondenti e riepiloghi immediati dei figli
- `config.get`: recupera lo snapshot corrente + hash
- `config.patch`: percorso di aggiornamento parziale preferito
- `config.apply`: solo sostituzione completa della configurazione
- `update.run`: autoaggiornamento esplicito + riavvio

Quando non stai sostituendo l'intera configurazione, preferisci `config.schema.lookup` e poi `config.patch`.

<AccordionGroup>
  <Accordion title="config.apply (sostituzione completa)">
    Valida + scrive l'intera configurazione e riavvia il Gateway in un unico passaggio.

    <Warning>
    `config.apply` sostituisce l'**intera configurazione**. Usa `config.patch` per aggiornamenti parziali, oppure `openclaw config set` per singole chiavi.
    </Warning>

    Parametri:

    - `raw` (stringa) — payload JSON5 per l'intera configurazione
    - `baseHash` (facoltativo) — hash della configurazione da `config.get` (obbligatorio quando la configurazione esiste)
    - `sessionKey` (facoltativo) — chiave di sessione per il ping di riattivazione dopo il riavvio
    - `note` (facoltativo) — nota per il sentinel di riavvio
    - `restartDelayMs` (facoltativo) — ritardo prima del riavvio (predefinito 2000)

    Le richieste di riavvio vengono accorpate mentre una è già in attesa/in corso, e tra i cicli di riavvio si applica un cooldown di 30 secondi.

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
    Unisce un aggiornamento parziale alla configurazione esistente (semantica JSON merge patch):

    - Gli oggetti vengono uniti ricorsivamente
    - `null` elimina una chiave
    - Gli array vengono sostituiti

    Parametri:

    - `raw` (stringa) — JSON5 con solo le chiavi da modificare
    - `baseHash` (obbligatorio) — hash della configurazione da `config.get`
    - `sessionKey`, `note`, `restartDelayMs` — come in `config.apply`

    Il comportamento di riavvio corrisponde a `config.apply`: riavvii in attesa accorpati più un cooldown di 30 secondi tra i cicli di riavvio.

    ```bash
    openclaw gateway call config.patch --params '{
      "raw": "{ channels: { telegram: { groups: { \"*\": { requireMention: false } } } } }",
      "baseHash": "<hash>"
    }'
    ```

  </Accordion>
</AccordionGroup>

## Variabili di ambiente

OpenClaw legge le variabili di ambiente dal processo padre più:

- `.env` dalla directory di lavoro corrente (se presente)
- `~/.openclaw/.env` (fallback globale)

Nessuno dei due file sovrascrive le variabili di ambiente esistenti. Puoi anche impostare variabili di ambiente inline nella configurazione:

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

<Accordion title="Importazione env dalla shell (facoltativa)">
  Se abilitata e le chiavi previste non sono impostate, OpenClaw esegue la tua shell di login e importa solo le chiavi mancanti:

```json5
{
  env: {
    shellEnv: { enabled: true, timeoutMs: 15000 },
  },
}
```

Equivalente come variabile di ambiente: `OPENCLAW_LOAD_SHELL_ENV=1`
</Accordion>

<Accordion title="Sostituzione delle variabili di ambiente nei valori di configurazione">
  Fai riferimento alle variabili di ambiente in qualsiasi valore stringa della configurazione con `${VAR_NAME}`:

```json5
{
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } },
  models: { providers: { custom: { apiKey: "${CUSTOM_API_KEY}" } } },
}
```

Regole:

- Vengono riconosciuti solo nomi in maiuscolo corrispondenti a: `[A-Z_][A-Z0-9_]*`
- Variabili mancanti/vuote generano un errore al momento del caricamento
- Usa l'escape `$${VAR}` per un output letterale
- Funziona all'interno dei file `$include`
- Sostituzione inline: `"${BASE}/v1"` → `"https://api.example.com/v1"`

</Accordion>

<Accordion title="Riferimenti ai segreti (env, file, exec)">
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

I dettagli di SecretRef (inclusi `secrets.providers` per `env`/`file`/`exec`) sono disponibili in [Gestione dei segreti](/it/gateway/secrets).
I percorsi delle credenziali supportati sono elencati in [Superficie delle credenziali SecretRef](/it/reference/secretref-credential-surface).
</Accordion>

Consulta [Ambiente](/it/help/environment) per la precedenza completa e le origini.

## Riferimento completo

Per il riferimento completo campo per campo, consulta **[Riferimento della configurazione](/it/gateway/configuration-reference)**.

---

_Correlati: [Esempi di configurazione](/it/gateway/configuration-examples) · [Riferimento della configurazione](/it/gateway/configuration-reference) · [Doctor](/it/gateway/doctor)_
