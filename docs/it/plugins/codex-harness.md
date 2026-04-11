---
read_when:
    - Vuoi usare l'harness app-server Codex incluso
    - Hai bisogno di riferimenti ai modelli Codex ed esempi di configurazione
    - Vuoi disabilitare il fallback PI per deployment solo Codex
summary: Esegui i turni dell'agente integrato di OpenClaw tramite l'harness app-server Codex incluso
title: Harness Codex
x-i18n:
    generated_at: "2026-04-11T02:45:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 60e1dcf4f1a00c63c3ef31d72feac44bce255421c032c58fa4fd67295b3daf23
    source_path: plugins/codex-harness.md
    workflow: 15
---

# Harness Codex

Il plugin `codex` incluso consente a OpenClaw di eseguire i turni dell'agente integrato tramite l'app-server Codex invece che tramite l'harness PI integrato.

Usalo quando vuoi che Codex gestisca la sessione agente di basso livello: rilevamento dei modelli, ripresa nativa del thread, compattazione nativa ed esecuzione tramite app-server.
OpenClaw continua comunque a gestire canali di chat, file di sessione, selezione del modello, strumenti, approvazioni, distribuzione dei media e il mirror visibile del transcript.

L'harness è disattivato per impostazione predefinita. Viene selezionato solo quando il plugin `codex` è abilitato e il modello risolto è un modello `codex/*`, oppure quando forzi esplicitamente `embeddedHarness.runtime: "codex"` o `OPENCLAW_AGENT_RUNTIME=codex`.
Se non configuri mai `codex/*`, le esecuzioni esistenti PI, OpenAI, Anthropic, Gemini, local e custom-provider mantengono il loro comportamento attuale.

## Scegli il prefisso del modello corretto

OpenClaw ha percorsi separati per l'accesso in stile OpenAI e Codex:

| Riferimento modello   | Percorso runtime                              | Usalo quando                                                            |
| --------------------- | --------------------------------------------- | ----------------------------------------------------------------------- |
| `openai/gpt-5.4`      | Provider OpenAI tramite l'infrastruttura OpenClaw/PI | Vuoi accesso diretto alla Platform API di OpenAI con `OPENAI_API_KEY`.  |
| `openai-codex/gpt-5.4` | Provider OpenAI Codex OAuth tramite PI       | Vuoi ChatGPT/Codex OAuth senza l'harness app-server Codex.              |
| `codex/gpt-5.4`       | Provider Codex incluso più harness Codex     | Vuoi l'esecuzione nativa dell'app-server Codex per il turno dell'agente integrato. |

L'harness Codex gestisce solo i riferimenti modello `codex/*`. I riferimenti esistenti `openai/*`, `openai-codex/*`, Anthropic, Gemini, xAI, local e custom provider mantengono i loro percorsi normali.

## Requisiti

- OpenClaw con il plugin `codex` incluso disponibile.
- App-server Codex `0.118.0` o successivo.
- Autenticazione Codex disponibile per il processo app-server.

Il plugin blocca handshake dell'app-server più vecchi o privi di versione. In questo modo OpenClaw rimane sulla superficie di protocollo su cui è stato testato.

Per i test live e smoke in Docker, l'autenticazione di solito proviene da `OPENAI_API_KEY`, più file CLI Codex facoltativi come `~/.codex/auth.json` e `~/.codex/config.toml`. Usa lo stesso materiale di autenticazione usato dal tuo app-server Codex locale.

## Configurazione minima

Usa `codex/gpt-5.4`, abilita il plugin incluso e forza l'harness `codex`:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
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

Se la tua configurazione usa `plugins.allow`, includi anche `codex` lì:

```json5
{
  plugins: {
    allow: ["codex"],
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Impostare `agents.defaults.model` o il modello di un agente su `codex/<model>` abilita automaticamente anche il plugin `codex` incluso. La voce esplicita del plugin resta comunque utile nelle configurazioni condivise perché rende evidente l'intento del deployment.

## Aggiungere Codex senza sostituire gli altri modelli

Mantieni `runtime: "auto"` quando vuoi Codex per i modelli `codex/*` e PI per tutto il resto:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: {
        primary: "codex/gpt-5.4",
        fallbacks: ["openai/gpt-5.4", "anthropic/claude-opus-4-6"],
      },
      models: {
        "codex/gpt-5.4": { alias: "codex" },
        "codex/gpt-5.4-mini": { alias: "codex-mini" },
        "openai/gpt-5.4": { alias: "gpt" },
        "anthropic/claude-opus-4-6": { alias: "opus" },
      },
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
  },
}
```

Con questa struttura:

- `/model codex` o `/model codex/gpt-5.4` usa l'harness app-server Codex.
- `/model gpt` o `/model openai/gpt-5.4` usa il percorso provider OpenAI.
- `/model opus` usa il percorso provider Anthropic.
- Se viene selezionato un modello non Codex, PI resta l'harness di compatibilità.

## Deployment solo Codex

Disabilita il fallback PI quando devi dimostrare che ogni turno dell'agente integrato usa l'harness Codex:

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

Override tramite ambiente:

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Con il fallback disabilitato, OpenClaw fallisce subito se il plugin Codex è disabilitato, il modello richiesto non è un riferimento `codex/*`, l'app-server è troppo vecchio oppure l'app-server non può avviarsi.

## Codex per agente

Puoi rendere un agente solo Codex mentre l'agente predefinito mantiene la selezione automatica normale:

```json5
{
  agents: {
    defaults: {
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
    list: [
      {
        id: "main",
        default: true,
        model: "anthropic/claude-opus-4-6",
      },
      {
        id: "codex",
        name: "Codex",
        model: "codex/gpt-5.4",
        embeddedHarness: {
          runtime: "codex",
          fallback: "none",
        },
      },
    ],
  },
}
```

Usa i normali comandi di sessione per cambiare agente e modelli. `/new` crea una nuova sessione OpenClaw e l'harness Codex crea o riprende il proprio thread sidecar dell'app-server secondo necessità. `/reset` cancella il binding della sessione OpenClaw per quel thread.

## Rilevamento dei modelli

Per impostazione predefinita, il plugin Codex chiede all'app-server i modelli disponibili. Se il rilevamento fallisce o va in timeout, usa il catalogo di fallback incluso:

- `codex/gpt-5.4`
- `codex/gpt-5.4-mini`
- `codex/gpt-5.2`

Puoi regolare il rilevamento sotto `plugins.entries.codex.config.discovery`:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: true,
            timeoutMs: 2500,
          },
        },
      },
    },
  },
}
```

Disabilita il rilevamento quando vuoi che l'avvio eviti di interrogare Codex e resti sul catalogo di fallback:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: false,
          },
        },
      },
    },
  },
}
```

## Connessione app-server e policy

Per impostazione predefinita, il plugin avvia Codex localmente con:

```bash
codex app-server --listen stdio://
```

Puoi mantenere questa impostazione predefinita e regolare solo la policy nativa di Codex:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            sandbox: "workspace-write",
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

Per un app-server già in esecuzione, usa il trasporto WebSocket:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://127.0.0.1:39175",
            authToken: "${CODEX_APP_SERVER_TOKEN}",
            requestTimeoutMs: 60000,
          },
        },
      },
    },
  },
}
```

Campi `appServer` supportati:

| Campo               | Predefinito                               | Significato                                                              |
| ------------------- | ----------------------------------------- | ------------------------------------------------------------------------ |
| `transport`         | `"stdio"`                                 | `"stdio"` avvia Codex; `"websocket"` si connette a `url`.                |
| `command`           | `"codex"`                                 | Eseguibile per il trasporto stdio.                                       |
| `args`              | `["app-server", "--listen", "stdio://"]`  | Argomenti per il trasporto stdio.                                        |
| `url`               | non impostato                             | URL WebSocket dell'app-server.                                           |
| `authToken`         | non impostato                             | Bearer token per il trasporto WebSocket.                                 |
| `headers`           | `{}`                                      | Header WebSocket aggiuntivi.                                             |
| `requestTimeoutMs`  | `60000`                                   | Timeout per le chiamate control-plane dell'app-server.                   |
| `approvalPolicy`    | `"never"`                                 | Policy di approvazione nativa Codex inviata a avvio/ripresa/turno del thread. |
| `sandbox`           | `"workspace-write"`                       | Modalità sandbox nativa Codex inviata a avvio/ripresa del thread.        |
| `approvalsReviewer` | `"user"`                                  | Usa `"guardian_subagent"` per consentire al guardian Codex di esaminare le approvazioni native. |
| `serviceTier`       | non impostato                             | Livello di servizio Codex facoltativo, ad esempio `"priority"`.          |

Le vecchie variabili di ambiente funzionano ancora come fallback per i test locali quando il campo di configurazione corrispondente non è impostato:

- `OPENCLAW_CODEX_APP_SERVER_BIN`
- `OPENCLAW_CODEX_APP_SERVER_ARGS`
- `OPENCLAW_CODEX_APP_SERVER_APPROVAL_POLICY`
- `OPENCLAW_CODEX_APP_SERVER_SANDBOX`
- `OPENCLAW_CODEX_APP_SERVER_GUARDIAN=1`

La configurazione è preferibile per deployment ripetibili.

## Ricette comuni

Codex locale con trasporto stdio predefinito:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Validazione dell'harness solo Codex, con fallback PI disabilitato:

```json5
{
  embeddedHarness: {
    fallback: "none",
  },
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Approvazioni Codex esaminate dal guardian:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            approvalsReviewer: "guardian_subagent",
            sandbox: "workspace-write",
          },
        },
      },
    },
  },
}
```

App-server remoto con header espliciti:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://gateway-host:39175",
            headers: {
              "X-OpenClaw-Agent": "main",
            },
          },
        },
      },
    },
  },
}
```

Il cambio di modello resta controllato da OpenClaw. Quando una sessione OpenClaw è collegata a un thread Codex esistente, il turno successivo invia di nuovo all'app-server il modello `codex/*` attualmente selezionato, il provider, la policy di approvazione, il sandbox e il livello di servizio.
Passare da `codex/gpt-5.4` a `codex/gpt-5.2` mantiene il binding del thread ma chiede a Codex di continuare con il modello appena selezionato.

## Comando Codex

Il plugin incluso registra `/codex` come comando slash autorizzato. È generico e funziona su qualsiasi canale che supporti i comandi di testo OpenClaw.

Forme comuni:

- `/codex status` mostra connettività live dell'app-server, modelli, account, limiti di frequenza, server MCP e skills.
- `/codex models` elenca i modelli live dell'app-server Codex.
- `/codex threads [filter]` elenca i thread Codex recenti.
- `/codex resume <thread-id>` collega la sessione OpenClaw corrente a un thread Codex esistente.
- `/codex compact` chiede all'app-server Codex di compattare il thread collegato.
- `/codex review` avvia la revisione nativa Codex per il thread collegato.
- `/codex account` mostra lo stato di account e limiti di frequenza.
- `/codex mcp` elenca lo stato dei server MCP dell'app-server Codex.
- `/codex skills` elenca le skills dell'app-server Codex.

`/codex resume` scrive lo stesso file di binding sidecar usato dall'harness per i turni normali. Al messaggio successivo, OpenClaw riprende quel thread Codex, passa all'app-server il modello OpenClaw `codex/*` attualmente selezionato e mantiene abilitata la cronologia estesa.

La superficie dei comandi richiede Codex app-server `0.118.0` o successivo. I singoli
metodi di controllo vengono segnalati come `unsupported by this Codex app-server` se un
app-server futuro o personalizzato non espone quel metodo JSON-RPC.

## Strumenti, media e compattazione

L'harness Codex modifica solo l'esecutore di basso livello dell'agente integrato.

OpenClaw continua a costruire l'elenco degli strumenti e a ricevere risultati dinamici degli strumenti dall'harness. Testo, immagini, video, musica, TTS, approvazioni e output degli strumenti di messaggistica continuano a passare attraverso il normale percorso di distribuzione di OpenClaw.

Quando il modello selezionato usa l'harness Codex, la compattazione nativa del thread viene delegata all'app-server Codex. OpenClaw mantiene un mirror del transcript per cronologia del canale, ricerca, `/new`, `/reset` e futuri cambi di modello o harness. Il mirror include il prompt dell'utente, il testo finale dell'assistente e record leggeri di ragionamento o piano di Codex quando l'app-server li emette.

La generazione di media non richiede PI. Immagini, video, musica, PDF, TTS e comprensione dei media continuano a usare le impostazioni del provider/modello corrispondenti come `agents.defaults.imageGenerationModel`, `videoGenerationModel`, `pdfModel` e `messages.tts`.

## Risoluzione dei problemi

**Codex non appare in `/model`:** abilita `plugins.entries.codex.enabled`, imposta un riferimento modello `codex/*` oppure controlla se `plugins.allow` esclude `codex`.

**OpenClaw torna a usare PI:** imposta `embeddedHarness.fallback: "none"` oppure `OPENCLAW_AGENT_HARNESS_FALLBACK=none` durante i test.

**L'app-server viene rifiutato:** aggiorna Codex in modo che l'handshake dell'app-server riporti la versione `0.118.0` o successiva.

**Il rilevamento dei modelli è lento:** riduci `plugins.entries.codex.config.discovery.timeoutMs` oppure disabilita il rilevamento.

**Il trasporto WebSocket fallisce immediatamente:** controlla `appServer.url`, `authToken` e che l'app-server remoto usi la stessa versione del protocollo app-server Codex.

**Un modello non Codex usa PI:** è previsto. L'harness Codex gestisce solo i riferimenti modello `codex/*`.

## Correlati

- [Plugin di harness agente](/it/plugins/sdk-agent-harness)
- [Provider di modelli](/it/concepts/model-providers)
- [Riferimento della configurazione](/it/gateway/configuration-reference)
- [Testing](/it/help/testing#live-codex-app-server-harness-smoke)
