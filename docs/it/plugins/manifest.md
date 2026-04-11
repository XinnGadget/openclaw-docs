---
read_when:
    - Stai creando un plugin OpenClaw
    - Devi distribuire uno schema di configurazione del plugin o eseguire il debug degli errori di validazione del plugin
summary: Manifest del plugin + requisiti dello schema JSON (validazione rigorosa della configurazione)
title: Manifest del plugin
x-i18n:
    generated_at: "2026-04-11T02:46:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6b254c121d1eb5ea19adbd4148243cf47339c960442ab1ca0e0bfd52e0154c88
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifest del plugin (`openclaw.plugin.json`)

Questa pagina riguarda solo il **manifest nativo dei plugin OpenClaw**.

Per i layout bundle compatibili, vedi [Bundle di plugin](/it/plugins/bundles).

I formati bundle compatibili usano file manifest diversi:

- Bundle Codex: `.codex-plugin/plugin.json`
- Bundle Claude: `.claude-plugin/plugin.json` oppure il layout componente Claude predefinito
  senza manifest
- Bundle Cursor: `.cursor-plugin/plugin.json`

OpenClaw rileva automaticamente anche quei layout bundle, ma non vengono validati
rispetto allo schema `openclaw.plugin.json` descritto qui.

Per i bundle compatibili, OpenClaw al momento legge i metadati del bundle più le
root delle skill dichiarate, le root dei comandi Claude, i valori predefiniti di `settings.json` del bundle Claude,
i valori predefiniti LSP del bundle Claude e i pacchetti hook supportati quando il layout corrisponde
alle aspettative di runtime di OpenClaw.

Ogni plugin nativo OpenClaw **deve** includere un file `openclaw.plugin.json` nella
**root del plugin**. OpenClaw usa questo manifest per validare la configurazione
**senza eseguire il codice del plugin**. I manifest mancanti o non validi vengono trattati come
errori del plugin e bloccano la validazione della configurazione.

Consulta la guida completa al sistema di plugin: [Plugin](/it/tools/plugin).
Per il modello di capability nativo e le indicazioni attuali sulla compatibilità esterna:
[Modello di capability](/it/plugins/architecture#public-capability-model).

## A cosa serve questo file

`openclaw.plugin.json` sono i metadati che OpenClaw legge prima di caricare il
codice del tuo plugin.

Usalo per:

- identità del plugin
- validazione della configurazione
- metadati di autenticazione e onboarding che devono essere disponibili senza avviare il
  runtime del plugin
- metadati di alias e auto-enable che devono essere risolti prima che il runtime del plugin venga caricato
- metadati sintetici di proprietà delle famiglie di modelli che devono attivare automaticamente il
  plugin prima del caricamento del runtime
- snapshot statiche della proprietà delle capability usate per il wiring di compatibilità bundled e
  la copertura dei contratti
- metadati di configurazione specifici del canale che devono essere uniti nelle superfici di catalogo e validazione
  senza caricare il runtime
- suggerimenti UI per la configurazione

Non usarlo per:

- registrare il comportamento runtime
- dichiarare entrypoint di codice
- metadati di installazione npm

Questi appartengono al codice del plugin e a `package.json`.

## Esempio minimo

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## Esempio completo

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "Plugin provider OpenRouter",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "Chiave API OpenRouter",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "Chiave API OpenRouter",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "Chiave API",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## Riferimento dei campi di primo livello

| Campo                               | Obbligatorio | Tipo                             | Significato                                                                                                                                                                                                  |
| ----------------------------------- | ------------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Sì           | `string`                         | ID canonico del plugin. È l'ID usato in `plugins.entries.<id>`.                                                                                                                                              |
| `configSchema`                      | Sì           | `object`                         | Schema JSON inline per la configurazione di questo plugin.                                                                                                                                                    |
| `enabledByDefault`                  | No           | `true`                           | Contrassegna un plugin bundled come abilitato per impostazione predefinita. Omettilo, oppure imposta qualsiasi valore diverso da `true`, per lasciare il plugin disabilitato per impostazione predefinita. |
| `legacyPluginIds`                   | No           | `string[]`                       | ID legacy che vengono normalizzati a questo ID plugin canonico.                                                                                                                                               |
| `autoEnableWhenConfiguredProviders` | No           | `string[]`                       | ID provider che devono abilitare automaticamente questo plugin quando autenticazione, configurazione o riferimenti al modello li menzionano.                                                                  |
| `kind`                              | No           | `"memory"` \| `"context-engine"` | Dichiara un tipo esclusivo di plugin usato da `plugins.slots.*`.                                                                                                                                             |
| `channels`                          | No           | `string[]`                       | ID dei canali posseduti da questo plugin. Usati per discovery e validazione della configurazione.                                                                                                             |
| `providers`                         | No           | `string[]`                       | ID dei provider posseduti da questo plugin.                                                                                                                                                                   |
| `modelSupport`                      | No           | `object`                         | Metadati sintetici di famiglie di modelli posseduti dal manifest usati per caricare automaticamente il plugin prima del runtime.                                                                             |
| `cliBackends`                       | No           | `string[]`                       | ID dei backend di inferenza CLI posseduti da questo plugin. Usati per l'auto-attivazione all'avvio da riferimenti espliciti di configurazione.                                                             |
| `commandAliases`                    | No           | `object[]`                       | Nomi di comandi posseduti da questo plugin che devono produrre diagnostica di configurazione e CLI consapevole del plugin prima del caricamento del runtime.                                                |
| `providerAuthEnvVars`               | No           | `Record<string, string[]>`       | Metadati env leggeri di autenticazione provider che OpenClaw può ispezionare senza caricare il codice del plugin.                                                                                            |
| `providerAuthAliases`               | No           | `Record<string, string>`         | ID provider che devono riutilizzare un altro ID provider per la ricerca dell'autenticazione, ad esempio un provider di coding che condivide la chiave API del provider base e i profili di autenticazione. |
| `channelEnvVars`                    | No           | `Record<string, string[]>`       | Metadati env leggeri di canale che OpenClaw può ispezionare senza caricare il codice del plugin. Usali per setup del canale guidato da env o superfici di autenticazione che helper generici di avvio/config dovrebbero vedere. |
| `providerAuthChoices`               | No           | `object[]`                       | Metadati leggeri di scelta autenticazione per selettori di onboarding, risoluzione del provider preferito e semplice wiring dei flag CLI.                                                                   |
| `contracts`                         | No           | `object`                         | Snapshot statica delle capability bundled per speech, trascrizione realtime, voce realtime, media-understanding, generazione di immagini, generazione musicale, generazione video, web-fetch, ricerca web e proprietà degli strumenti. |
| `channelConfigs`                    | No           | `Record<string, object>`         | Metadati di configurazione del canale posseduti dal manifest uniti nelle superfici di discovery e validazione prima del caricamento del runtime.                                                             |
| `skills`                            | No           | `string[]`                       | Directory Skills da caricare, relative alla root del plugin.                                                                                                                                                  |
| `name`                              | No           | `string`                         | Nome leggibile del plugin.                                                                                                                                                                                    |
| `description`                       | No           | `string`                         | Breve riepilogo mostrato nelle superfici del plugin.                                                                                                                                                          |
| `version`                           | No           | `string`                         | Versione informativa del plugin.                                                                                                                                                                              |
| `uiHints`                           | No           | `Record<string, object>`         | Etichette UI, segnaposto e suggerimenti di sensibilità per i campi di configurazione.                                                                                                                        |

## Riferimento `providerAuthChoices`

Ogni voce `providerAuthChoices` descrive una scelta di onboarding o autenticazione.
OpenClaw la legge prima che il runtime del provider venga caricato.

| Campo                 | Obbligatorio | Tipo                                            | Significato                                                                                              |
| --------------------- | ------------ | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `provider`            | Sì           | `string`                                        | ID del provider a cui appartiene questa scelta.                                                          |
| `method`              | Sì           | `string`                                        | ID del metodo di autenticazione a cui inviare.                                                           |
| `choiceId`            | Sì           | `string`                                        | ID stabile della scelta di autenticazione usato dai flussi di onboarding e CLI.                         |
| `choiceLabel`         | No           | `string`                                        | Etichetta visibile all'utente. Se omessa, OpenClaw usa `choiceId` come fallback.                        |
| `choiceHint`          | No           | `string`                                        | Breve testo di supporto per il selettore.                                                                |
| `assistantPriority`   | No           | `number`                                        | I valori più bassi vengono ordinati prima nei selettori interattivi guidati dall'assistente.            |
| `assistantVisibility` | No           | `"visible"` \| `"manual-only"`                  | Nasconde la scelta dai selettori dell'assistente pur consentendo comunque la selezione manuale via CLI. |
| `deprecatedChoiceIds` | No           | `string[]`                                      | ID legacy della scelta che devono reindirizzare gli utenti a questa scelta sostitutiva.                 |
| `groupId`             | No           | `string`                                        | ID gruppo facoltativo per raggruppare scelte correlate.                                                 |
| `groupLabel`          | No           | `string`                                        | Etichetta visibile all'utente per quel gruppo.                                                           |
| `groupHint`           | No           | `string`                                        | Breve testo di supporto per il gruppo.                                                                   |
| `optionKey`           | No           | `string`                                        | Chiave opzione interna per flussi di autenticazione semplici a un solo flag.                            |
| `cliFlag`             | No           | `string`                                        | Nome del flag CLI, come `--openrouter-api-key`.                                                          |
| `cliOption`           | No           | `string`                                        | Forma completa dell'opzione CLI, come `--openrouter-api-key <key>`.                                     |
| `cliDescription`      | No           | `string`                                        | Descrizione usata nell'help della CLI.                                                                   |
| `onboardingScopes`    | No           | `Array<"text-inference" \| "image-generation">` | In quali superfici di onboarding deve comparire questa scelta. Se omesso, il valore predefinito è `["text-inference"]`. |

## Riferimento `commandAliases`

Usa `commandAliases` quando un plugin possiede un nome di comando runtime che gli utenti potrebbero
mettere per errore in `plugins.allow` o provare a eseguire come comando CLI root. OpenClaw
usa questi metadati per la diagnostica senza importare il codice runtime del plugin.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| Campo        | Obbligatorio | Tipo              | Significato                                                                  |
| ------------ | ------------ | ----------------- | ---------------------------------------------------------------------------- |
| `name`       | Sì           | `string`          | Nome del comando che appartiene a questo plugin.                             |
| `kind`       | No           | `"runtime-slash"` | Contrassegna l'alias come comando slash di chat invece che come comando CLI root. |
| `cliCommand` | No           | `string`          | Comando CLI root correlato da suggerire per le operazioni CLI, se esiste.    |

## Riferimento `uiHints`

`uiHints` è una mappa dai nomi dei campi di configurazione a piccoli suggerimenti di rendering.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "Chiave API",
      "help": "Usata per le richieste OpenRouter",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Ogni suggerimento di campo può includere:

| Campo         | Tipo       | Significato                              |
| ------------- | ---------- | ---------------------------------------- |
| `label`       | `string`   | Etichetta del campo visibile all'utente. |
| `help`        | `string`   | Breve testo di supporto.                 |
| `tags`        | `string[]` | Tag UI facoltativi.                      |
| `advanced`    | `boolean`  | Contrassegna il campo come avanzato.     |
| `sensitive`   | `boolean`  | Contrassegna il campo come segreto o sensibile. |
| `placeholder` | `string`   | Testo segnaposto per gli input del modulo. |

## Riferimento `contracts`

Usa `contracts` solo per metadati statici di proprietà delle capability che OpenClaw può
leggere senza importare il runtime del plugin.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

Ogni elenco è facoltativo:

| Campo                            | Tipo       | Significato                                               |
| -------------------------------- | ---------- | --------------------------------------------------------- |
| `speechProviders`                | `string[]` | ID provider speech posseduti da questo plugin.            |
| `realtimeTranscriptionProviders` | `string[]` | ID provider di trascrizione realtime posseduti da questo plugin. |
| `realtimeVoiceProviders`         | `string[]` | ID provider di voce realtime posseduti da questo plugin.  |
| `mediaUnderstandingProviders`    | `string[]` | ID provider media-understanding posseduti da questo plugin. |
| `imageGenerationProviders`       | `string[]` | ID provider di generazione immagini posseduti da questo plugin. |
| `videoGenerationProviders`       | `string[]` | ID provider di generazione video posseduti da questo plugin. |
| `webFetchProviders`              | `string[]` | ID provider web-fetch posseduti da questo plugin.         |
| `webSearchProviders`             | `string[]` | ID provider di ricerca web posseduti da questo plugin.    |
| `tools`                          | `string[]` | Nomi degli strumenti agente posseduti da questo plugin per i controlli di contratto bundled. |

## Riferimento `channelConfigs`

Usa `channelConfigs` quando un plugin di canale ha bisogno di metadati di configurazione leggeri prima
del caricamento del runtime.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "URL Homeserver",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Connessione al homeserver Matrix",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Ogni voce di canale può includere:

| Campo         | Tipo                     | Significato                                                                                 |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | Schema JSON per `channels.<id>`. Obbligatorio per ogni voce dichiarata di configurazione canale. |
| `uiHints`     | `Record<string, object>` | Etichette UI/segnaposto/suggerimenti di sensibilità facoltativi per quella sezione di configurazione canale. |
| `label`       | `string`                 | Etichetta del canale unita nelle superfici di selezione e ispezione quando i metadati runtime non sono pronti. |
| `description` | `string`                 | Breve descrizione del canale per le superfici di ispezione e catalogo.                      |
| `preferOver`  | `string[]`               | ID di plugin legacy o a priorità inferiore che questo canale deve superare nelle superfici di selezione. |

## Riferimento `modelSupport`

Usa `modelSupport` quando OpenClaw deve inferire il tuo plugin provider da
ID modello sintetici come `gpt-5.4` o `claude-sonnet-4.6` prima del caricamento
del runtime del plugin.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw applica questa precedenza:

- i riferimenti espliciti `provider/model` usano i metadati manifest `providers`
- `modelPatterns` hanno precedenza su `modelPrefixes`
- se sia un plugin non bundled sia un plugin bundled corrispondono, vince il plugin
  non bundled
- l'ambiguità rimanente viene ignorata finché l'utente o la configurazione non specificano un provider

Campi:

| Campo           | Tipo       | Significato                                                                |
| --------------- | ---------- | -------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Prefissi confrontati con `startsWith` rispetto agli ID modello sintetici.  |
| `modelPatterns` | `string[]` | Sorgenti regex confrontate con gli ID modello sintetici dopo la rimozione del suffisso del profilo. |

Le chiavi capability legacy di primo livello sono deprecate. Usa `openclaw doctor --fix` per
spostare `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` e `webSearchProviders` sotto `contracts`; il normale
caricamento del manifest non tratta più quei campi di primo livello come
proprietà di capability.

## Manifest rispetto a package.json

I due file svolgono ruoli diversi:

| File                   | Usalo per                                                                                                                        |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Discovery, validazione della configurazione, metadati delle scelte di autenticazione e suggerimenti UI che devono esistere prima dell'esecuzione del codice del plugin |
| `package.json`         | Metadati npm, installazione delle dipendenze e blocco `openclaw` usato per entrypoint, gating di installazione, setup o metadati di catalogo |

Se non sei sicuro di dove debba stare un metadato, usa questa regola:

- se OpenClaw deve conoscerlo prima di caricare il codice del plugin, mettilo in `openclaw.plugin.json`
- se riguarda packaging, file entrypoint o comportamento di installazione npm, mettilo in `package.json`

### Campi `package.json` che influiscono sulla discovery

Alcuni metadati del plugin pre-runtime vivono intenzionalmente in `package.json` sotto il
blocco `openclaw` invece che in `openclaw.plugin.json`.

Esempi importanti:

| Campo                                                             | Significato                                                                                                                                    |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Dichiara gli entrypoint dei plugin nativi.                                                                                                      |
| `openclaw.setupEntry`                                             | Entrypoint leggero solo setup usato durante onboarding e avvio differito dei canali.                                                           |
| `openclaw.channel`                                                | Metadati leggeri del catalogo canali come etichette, percorsi docs, alias e testo per la selezione.                                           |
| `openclaw.channel.configuredState`                                | Metadati leggeri del verificatore di stato configurato che possono rispondere a “esiste già una configurazione solo-env?” senza caricare il runtime completo del canale. |
| `openclaw.channel.persistedAuthState`                             | Metadati leggeri del verificatore di autenticazione persistita che possono rispondere a “c'è già qualcosa con accesso effettuato?” senza caricare il runtime completo del canale. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Suggerimenti di installazione/aggiornamento per plugin bundled e pubblicati esternamente.                                                      |
| `openclaw.install.defaultChoice`                                  | Percorso di installazione preferito quando sono disponibili più sorgenti di installazione.                                                     |
| `openclaw.install.minHostVersion`                                 | Versione minima supportata dell'host OpenClaw, usando una soglia semver come `>=2026.3.22`.                                                   |
| `openclaw.install.allowInvalidConfigRecovery`                     | Consente un percorso ristretto di recupero tramite reinstallazione del plugin bundled quando la configurazione non è valida.                   |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Permette alle superfici del canale solo-setup di caricarsi prima del plugin di canale completo durante l'avvio.                               |

`openclaw.install.minHostVersion` viene applicato durante l'installazione e il
caricamento del registro dei manifest. I valori non validi vengono rifiutati; i
valori validi ma più recenti saltano il plugin sugli host più vecchi.

`openclaw.install.allowInvalidConfigRecovery` è intenzionalmente ristretto. Non
rende installabili configurazioni arbitrarie rotte. Oggi consente solo ai flussi di installazione
di recuperare da specifici errori legacy di aggiornamento dei plugin bundled, come
un percorso mancante di plugin bundled o una voce `channels.<id>` obsoleta per quello stesso
plugin bundled. Gli errori di configurazione non correlati continuano a bloccare l'installazione e inviano gli operatori a `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` è un metadato di package per un piccolo modulo verificatore:

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

Usalo quando setup, doctor o i flussi di stato configurato hanno bisogno di una sonda di autenticazione
economica sì/no prima che il plugin di canale completo venga caricato. L'export di destinazione dovrebbe essere una piccola
funzione che legge solo lo stato persistito; non instradarla attraverso il barrel completo del runtime del canale.

`openclaw.channel.configuredState` segue la stessa forma per controlli economici
dello stato configurato solo-env:

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

Usalo quando un canale può rispondere allo stato configurato da env o altri piccoli
input non-runtime. Se il controllo richiede la risoluzione completa della configurazione o il vero
runtime del canale, mantieni invece quella logica nell'hook `config.hasConfiguredState` del plugin.

## Requisiti dello schema JSON

- **Ogni plugin deve includere uno schema JSON**, anche se non accetta alcuna configurazione.
- È accettabile uno schema vuoto (ad esempio `{ "type": "object", "additionalProperties": false }`).
- Gli schemi vengono validati al momento della lettura/scrittura della configurazione, non a runtime.

## Comportamento della validazione

- Chiavi `channels.*` sconosciute sono **errori**, a meno che l'ID canale non sia dichiarato da
  un manifest di plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` e `plugins.slots.*`
  devono fare riferimento a ID plugin **rilevabili**. Gli ID sconosciuti sono **errori**.
- Se un plugin è installato ma ha un manifest o uno schema rotto o mancante,
  la validazione fallisce e Doctor segnala l'errore del plugin.
- Se la configurazione del plugin esiste ma il plugin è **disabilitato**, la configurazione viene mantenuta e
  viene mostrato un **avviso** in Doctor e nei log.

Consulta [Riferimento configurazione](/it/gateway/configuration) per lo schema completo `plugins.*`.

## Note

- Il manifest è **obbligatorio per i plugin OpenClaw nativi**, inclusi i caricamenti dal filesystem locale.
- Il runtime continua comunque a caricare separatamente il modulo del plugin; il manifest serve solo per
  discovery + validazione.
- I manifest nativi vengono analizzati con JSON5, quindi commenti, virgole finali e
  chiavi senza virgolette sono accettati purché il valore finale resti un oggetto.
- Solo i campi del manifest documentati vengono letti dal loader dei manifest. Evita di aggiungere
  qui chiavi personalizzate di primo livello.
- `providerAuthEnvVars` è il percorso di metadati economico per sonde di autenticazione, validazione
  dei marker env e superfici simili di autenticazione provider che non devono avviare il runtime del plugin
  solo per ispezionare i nomi env.
- `providerAuthAliases` consente alle varianti di provider di riutilizzare le variabili env di autenticazione di un altro provider,
  i profili di autenticazione, l'autenticazione supportata da configurazione e la scelta di onboarding con chiave API
  senza hardcodare quella relazione nel core.
- `channelEnvVars` è il percorso di metadati economico per fallback shell-env, prompt
  di setup e superfici simili di canale che non devono avviare il runtime del plugin
  solo per ispezionare i nomi env.
- `providerAuthChoices` è il percorso di metadati economico per selettori di scelta autenticazione,
  risoluzione di `--auth-choice`, mappatura del provider preferito e semplice registrazione
  dei flag CLI di onboarding prima che il runtime del provider venga caricato. Per i metadati wizard runtime
  che richiedono codice provider, vedi
  [Hook runtime del provider](/it/plugins/architecture#provider-runtime-hooks).
- I tipi esclusivi di plugin vengono selezionati tramite `plugins.slots.*`.
  - `kind: "memory"` viene selezionato da `plugins.slots.memory`.
  - `kind: "context-engine"` viene selezionato da `plugins.slots.contextEngine`
    (predefinito: `legacy` incorporato).
- `channels`, `providers`, `cliBackends` e `skills` possono essere omessi quando un
  plugin non ne ha bisogno.
- Se il tuo plugin dipende da moduli nativi, documenta i passaggi di build e ogni
  requisito di allowlist del package manager (ad esempio, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Correlati

- [Creare plugin](/it/plugins/building-plugins) — introduzione ai plugin
- [Architettura dei plugin](/it/plugins/architecture) — architettura interna
- [Panoramica dell'SDK](/it/plugins/sdk-overview) — riferimento del Plugin SDK
