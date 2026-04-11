---
read_when:
    - Stai modificando il runtime incorporato dell'agente o il registro harness
    - Stai registrando un agent harness da un plugin bundled o trusted
    - Devi capire come il plugin Codex si relaziona ai provider di modelli
sidebarTitle: Agent Harness
summary: Superficie SDK sperimentale per plugin che sostituiscono l'esecutore incorporato dell'agente di basso livello
title: Plugin Agent Harness
x-i18n:
    generated_at: "2026-04-11T02:46:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 43c1f2c087230398b0162ed98449f239c8db1e822e51c7dcd40c54fa6c3374e1
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# Plugin Agent Harness

Un **agent harness** è l'esecutore di basso livello per un singolo turno di agente
OpenClaw già preparato. Non è un provider di modelli, non è un canale e non è un registro degli strumenti.

Usa questa superficie solo per plugin nativi bundled o trusted. Il contratto è
ancora sperimentale perché i tipi dei parametri rispecchiano intenzionalmente l'attuale
runner incorporato.

## Quando usare un harness

Registra un agent harness quando una famiglia di modelli ha il proprio runtime
di sessione nativo e il normale trasporto provider di OpenClaw è l'astrazione sbagliata.

Esempi:

- un server di agente di coding nativo che gestisce thread e compattazione
- una CLI o un daemon locale che deve trasmettere eventi nativi di piano/ragionamento/strumenti
- un runtime di modello che necessita del proprio resume id oltre alla
  trascrizione di sessione OpenClaw

**Non** registrare un harness solo per aggiungere una nuova API LLM. Per normali API di modelli HTTP o
WebSocket, crea un [plugin provider](/it/plugins/sdk-provider-plugins).

## Cosa continua a essere gestito dal core

Prima che venga selezionato un harness, OpenClaw ha già risolto:

- provider e modello
- stato auth del runtime
- livello di ragionamento e budget di contesto
- la trascrizione/sessione OpenClaw
- policy di workspace, sandbox e strumenti
- callback di risposta del canale e callback di streaming
- policy di fallback del modello e di cambio modello live

Questa separazione è intenzionale. Un harness esegue un tentativo preparato; non sceglie
provider, non sostituisce la consegna del canale e non cambia silenziosamente modello.

## Registrare un harness

**Import:** `openclaw/plugin-sdk/agent-harness`

```typescript
import type { AgentHarness } from "openclaw/plugin-sdk/agent-harness";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const myHarness: AgentHarness = {
  id: "my-harness",
  label: "My native agent harness",

  supports(ctx) {
    return ctx.provider === "my-provider"
      ? { supported: true, priority: 100 }
      : { supported: false };
  },

  async runAttempt(params) {
    // Start or resume your native thread.
    // Use params.prompt, params.tools, params.images, params.onPartialReply,
    // params.onAgentEvent, and the other prepared attempt fields.
    return await runMyNativeTurn(params);
  },
};

export default definePluginEntry({
  id: "my-native-agent",
  name: "My Native Agent",
  description: "Runs selected models through a native agent daemon.",
  register(api) {
    api.registerAgentHarness(myHarness);
  },
});
```

## Policy di selezione

OpenClaw sceglie un harness dopo la risoluzione di provider/modello:

1. `OPENCLAW_AGENT_RUNTIME=<id>` forza un harness registrato con quell'id.
2. `OPENCLAW_AGENT_RUNTIME=pi` forza l'harness PI integrato.
3. `OPENCLAW_AGENT_RUNTIME=auto` chiede agli harness registrati se supportano il
   provider/modello risolto.
4. Se nessun harness registrato corrisponde, OpenClaw usa PI a meno che il fallback a PI non sia
   disabilitato.

Gli errori di un harness plugin forzato emergono come errori di esecuzione. In modalità `auto`,
OpenClaw può tornare a PI quando l'harness plugin selezionato fallisce prima che un
turno abbia prodotto effetti collaterali. Imposta `OPENCLAW_AGENT_HARNESS_FALLBACK=none` oppure
`embeddedHarness.fallback: "none"` per rendere invece quel fallback un errore definitivo.

Il plugin Codex bundled registra `codex` come id del proprio harness. Il core tratta questo
come un normale id di harness plugin; gli alias specifici di Codex appartengono al plugin
o alla configurazione dell'operatore, non al selettore runtime condiviso.

## Associazione provider più harness

La maggior parte degli harness dovrebbe registrare anche un provider. Il provider rende i riferimenti ai modelli,
lo stato auth, i metadati del modello e la selezione `/model` visibili al resto di
OpenClaw. L'harness poi rivendica quel provider in `supports(...)`.

Il plugin Codex bundled segue questo schema:

- id provider: `codex`
- riferimenti modello utente: `codex/gpt-5.4`, `codex/gpt-5.2` o un altro modello restituito
  dal server app Codex
- id harness: `codex`
- auth: disponibilità sintetica del provider, perché l'harness Codex gestisce il
  login/sessione Codex nativo
- richiesta al server app: OpenClaw invia l'id modello nudo a Codex e lascia che
  l'harness parli con il protocollo nativo del server app

Il plugin Codex è additivo. I semplici riferimenti `openai/gpt-*` restano riferimenti del provider OpenAI
e continuano a usare il normale percorso provider di OpenClaw. Seleziona `codex/gpt-*`
quando vuoi auth gestita da Codex, rilevamento modelli Codex, thread nativi e
esecuzione del server app Codex. `/model` può passare tra i modelli Codex restituiti
dal server app Codex senza richiedere credenziali del provider OpenAI.

Per la configurazione dell'operatore, esempi di prefisso modello e configurazioni solo Codex, vedi
[Codex Harness](/it/plugins/codex-harness).

OpenClaw richiede Codex app-server `0.118.0` o successivo. Il plugin Codex controlla
l'handshake di inizializzazione del server app e blocca server più vecchi o senza versione, così
OpenClaw viene eseguito solo contro la superficie di protocollo su cui è stato testato.

## Disabilitare il fallback a PI

Per impostazione predefinita, OpenClaw esegue agenti incorporati con `agents.defaults.embeddedHarness`
impostato su `{ runtime: "auto", fallback: "pi" }`. In modalità `auto`, gli harness plugin registrati
possono rivendicare una coppia provider/modello. Se nessuno corrisponde, oppure se un harness plugin
selezionato automaticamente fallisce prima di produrre output, OpenClaw torna a PI.

Imposta `fallback: "none"` quando devi dimostrare che un harness plugin è l'unico
runtime effettivamente usato. Questo disabilita il fallback automatico a PI; non blocca
un `runtime: "pi"` esplicito o `OPENCLAW_AGENT_RUNTIME=pi`.

Per esecuzioni incorporate solo Codex:

```json
{
  "agents": {
    "defaults": {
      "model": "codex/gpt-5.4",
      "embeddedHarness": {
        "runtime": "codex",
        "fallback": "none"
      }
    }
  }
}
```

Se vuoi che qualsiasi harness plugin registrato rivendichi i modelli corrispondenti ma non
vuoi mai che OpenClaw torni silenziosamente a PI, mantieni `runtime: "auto"` e disabilita
il fallback:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "none"
      }
    }
  }
}
```

Gli override per agente usano la stessa struttura:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "pi"
      }
    },
    "list": [
      {
        "id": "codex-only",
        "model": "codex/gpt-5.4",
        "embeddedHarness": {
          "runtime": "codex",
          "fallback": "none"
        }
      }
    ]
  }
}
```

`OPENCLAW_AGENT_RUNTIME` continua a sovrascrivere il runtime configurato. Usa
`OPENCLAW_AGENT_HARNESS_FALLBACK=none` per disabilitare il fallback a PI
dall'ambiente.

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Con il fallback disabilitato, una sessione fallisce subito quando l'harness richiesto non è
registrato, non supporta il provider/modello risolto o fallisce prima di
produrre effetti collaterali del turno. Questo è intenzionale per distribuzioni solo Codex e
per test live che devono dimostrare che il percorso del server app Codex è realmente in uso.

Questa impostazione controlla solo l'agent harness incorporato. Non disabilita
l'instradamento specifico del provider per immagini, video, musica, TTS, PDF o altri modelli.

## Sessioni native e mirror della trascrizione

Un harness può mantenere un id di sessione nativo, id thread o token di ripresa lato daemon.
Mantieni questa associazione esplicitamente collegata alla sessione OpenClaw e continua a
rispecchiare nella trascrizione OpenClaw l'output di assistente/strumenti visibile all'utente.

La trascrizione OpenClaw resta il livello di compatibilità per:

- cronologia della sessione visibile nel canale
- ricerca e indicizzazione della trascrizione
- ritorno all'harness PI integrato in un turno successivo
- comportamento generico di `/new`, `/reset` ed eliminazione della sessione

Se il tuo harness memorizza un'associazione sidecar, implementa `reset(...)` in modo che OpenClaw possa
cancellarla quando la sessione OpenClaw proprietaria viene reimpostata.

## Risultati di strumenti e media

Il core costruisce l'elenco degli strumenti OpenClaw e lo passa al tentativo preparato.
Quando un harness esegue una chiamata dinamica a uno strumento, restituisci il risultato dello strumento tramite
la forma di risultato dell'harness invece di inviare tu stesso i media al canale.

Questo mantiene testo, immagine, video, musica, TTS, approvazione e output degli
strumenti di messaggistica sullo stesso percorso di consegna delle esecuzioni supportate da PI.

## Limitazioni attuali

- Il percorso di import pubblico è generico, ma alcuni alias di tipo per tentativo/risultato
  portano ancora nomi `Pi` per compatibilità.
- L'installazione di harness di terze parti è sperimentale. Preferisci i plugin provider
  finché non ti serve un runtime di sessione nativo.
- Il cambio di harness è supportato tra i turni. Non cambiare harness nel
  mezzo di un turno dopo che strumenti nativi, approvazioni, testo dell'assistente o invii di messaggi sono iniziati.

## Correlati

- [Panoramica SDK](/it/plugins/sdk-overview)
- [Helper di runtime](/it/plugins/sdk-runtime)
- [Plugin provider](/it/plugins/sdk-provider-plugins)
- [Codex Harness](/it/plugins/codex-harness)
- [Provider di modelli](/it/concepts/model-providers)
