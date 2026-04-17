---
read_when:
    - Vuoi un'automazione guidata da eventi per `/new`, `/reset`, `/stop` e per gli eventi del ciclo di vita dell'agente
    - Vuoi creare, installare o eseguire il debug degli hook
summary: 'Hook: automazione guidata da eventi per i comandi e gli eventi del ciclo di vita'
title: Hook
x-i18n:
    generated_at: "2026-04-11T02:44:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 14296398e4042d442ebdf071a07c6be99d4afda7cbf3c2b934e76dc5539742c7
    source_path: automation/hooks.md
    workflow: 15
---

# Hook

Gli hook sono piccoli script che vengono eseguiti quando succede qualcosa all'interno del Gateway. Vengono rilevati automaticamente dalle directory e possono essere ispezionati con `openclaw hooks`.

In OpenClaw esistono due tipi di hook:

- **Hook interni** (questa pagina): vengono eseguiti all'interno del Gateway quando si attivano eventi dell'agente, come `/new`, `/reset`, `/stop` o eventi del ciclo di vita.
- **Webhook**: endpoint HTTP esterni che consentono ad altri sistemi di attivare lavoro in OpenClaw. Vedi [Webhook](/it/automation/cron-jobs#webhooks).

Gli hook possono anche essere inclusi nei plugin. `openclaw hooks list` mostra sia gli hook standalone sia quelli gestiti dai plugin.

## Guida rapida

```bash
# Elenca gli hook disponibili
openclaw hooks list

# Abilita un hook
openclaw hooks enable session-memory

# Controlla lo stato degli hook
openclaw hooks check

# Ottieni informazioni dettagliate
openclaw hooks info session-memory
```

## Tipi di evento

| Evento                   | Quando si attiva                                |
| ------------------------ | ----------------------------------------------- |
| `command:new`            | Comando `/new` emesso                           |
| `command:reset`          | Comando `/reset` emesso                         |
| `command:stop`           | Comando `/stop` emesso                          |
| `command`                | Qualsiasi evento di comando (listener generale) |
| `session:compact:before` | Prima che la compattazione riassuma la cronologia |
| `session:compact:after`  | Dopo il completamento della compattazione       |
| `session:patch`          | Quando le proprietà della sessione vengono modificate |
| `agent:bootstrap`        | Prima che i file di bootstrap del workspace vengano iniettati |
| `gateway:startup`        | Dopo l'avvio dei canali e il caricamento degli hook |
| `message:received`       | Messaggio in ingresso da qualsiasi canale       |
| `message:transcribed`    | Dopo il completamento della trascrizione audio  |
| `message:preprocessed`   | Dopo il completamento di tutta l'elaborazione di media e link |
| `message:sent`           | Messaggio in uscita consegnato                  |

## Scrivere hook

### Struttura di un hook

Ogni hook è una directory che contiene due file:

```
my-hook/
├── HOOK.md          # Metadati + documentazione
└── handler.ts       # Implementazione dell'handler
```

### Formato di HOOK.md

```markdown
---
name: my-hook
description: "Breve descrizione di ciò che fa questo hook"
metadata:
  { "openclaw": { "emoji": "🔗", "events": ["command:new"], "requires": { "bins": ["node"] } } }
---

# My Hook

La documentazione dettagliata va qui.
```

**Campi dei metadati** (`metadata.openclaw`):

| Campo      | Descrizione                                          |
| ---------- | ---------------------------------------------------- |
| `emoji`    | Emoji visualizzata per la CLI                        |
| `events`   | Array di eventi da ascoltare                         |
| `export`   | Export nominato da usare (predefinito: `"default"`) |
| `os`       | Piattaforme richieste (ad esempio `["darwin", "linux"]`) |
| `requires` | `bins`, `anyBins`, `env` o percorsi `config` richiesti |
| `always`   | Ignora i controlli di idoneità (booleano)            |
| `install`  | Metodi di installazione                              |

### Implementazione dell'handler

```typescript
const handler = async (event) => {
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log(`[my-hook] New command triggered`);
  // Your logic here

  // Optionally send message to user
  event.messages.push("Hook executed!");
};

export default handler;
```

Ogni evento include: `type`, `action`, `sessionKey`, `timestamp`, `messages` (aggiungi elementi per inviare messaggi all'utente) e `context` (dati specifici dell'evento).

### Punti salienti del contesto evento

**Eventi di comando** (`command:new`, `command:reset`): `context.sessionEntry`, `context.previousSessionEntry`, `context.commandSource`, `context.workspaceDir`, `context.cfg`.

**Eventi di messaggio** (`message:received`): `context.from`, `context.content`, `context.channelId`, `context.metadata` (dati specifici del provider, inclusi `senderId`, `senderName`, `guildId`).

**Eventi di messaggio** (`message:sent`): `context.to`, `context.content`, `context.success`, `context.channelId`.

**Eventi di messaggio** (`message:transcribed`): `context.transcript`, `context.from`, `context.channelId`, `context.mediaPath`.

**Eventi di messaggio** (`message:preprocessed`): `context.bodyForAgent` (corpo finale arricchito), `context.from`, `context.channelId`.

**Eventi di bootstrap** (`agent:bootstrap`): `context.bootstrapFiles` (array mutabile), `context.agentId`.

**Eventi di patch della sessione** (`session:patch`): `context.sessionEntry`, `context.patch` (solo i campi modificati), `context.cfg`. Solo i client con privilegi possono attivare eventi di patch.

**Eventi di compattazione**: `session:compact:before` include `messageCount`, `tokenCount`. `session:compact:after` aggiunge `compactedCount`, `summaryLength`, `tokensBefore`, `tokensAfter`.

## Rilevamento degli hook

Gli hook vengono rilevati da queste directory, in ordine di precedenza di override crescente:

1. **Hook inclusi**: distribuiti con OpenClaw
2. **Hook dei plugin**: hook inclusi nei plugin installati
3. **Hook gestiti**: `~/.openclaw/hooks/` (installati dall'utente, condivisi tra i workspace). Le directory aggiuntive da `hooks.internal.load.extraDirs` condividono questa stessa precedenza.
4. **Hook del workspace**: `<workspace>/hooks/` (per agente, disabilitati per impostazione predefinita finché non vengono abilitati esplicitamente)

Gli hook del workspace possono aggiungere nuovi nomi di hook, ma non possono sovrascrivere hook inclusi, gestiti o forniti da plugin con lo stesso nome.

### Pacchetti di hook

I pacchetti di hook sono pacchetti npm che esportano hook tramite `openclaw.hooks` nel `package.json`. Installali con:

```bash
openclaw plugins install <path-or-spec>
```

Le specifiche npm sono solo del registro (nome pacchetto + versione esatta opzionale o dist-tag). Le specifiche Git/URL/file e gli intervalli semver vengono rifiutati.

## Hook inclusi

| Hook                  | Eventi                         | Cosa fa                                                |
| --------------------- | ------------------------------ | ------------------------------------------------------ |
| session-memory        | `command:new`, `command:reset` | Salva il contesto della sessione in `<workspace>/memory/` |
| bootstrap-extra-files | `agent:bootstrap`              | Inietta file di bootstrap aggiuntivi da pattern glob   |
| command-logger        | `command`                      | Registra tutti i comandi in `~/.openclaw/logs/commands.log` |
| boot-md               | `gateway:startup`              | Esegue `BOOT.md` quando il gateway si avvia            |

Abilita qualsiasi hook incluso:

```bash
openclaw hooks enable <hook-name>
```

<a id="session-memory"></a>

### Dettagli di session-memory

Estrae gli ultimi 15 messaggi utente/assistente, genera uno slug descrittivo per il nome file tramite LLM e salva in `<workspace>/memory/YYYY-MM-DD-slug.md`. Richiede che `workspace.dir` sia configurato.

<a id="bootstrap-extra-files"></a>

### Configurazione di bootstrap-extra-files

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "bootstrap-extra-files": {
          "enabled": true,
          "paths": ["packages/*/AGENTS.md", "packages/*/TOOLS.md"]
        }
      }
    }
  }
}
```

I percorsi vengono risolti relativamente al workspace. Vengono caricati solo i nomi base di bootstrap riconosciuti (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`, `MEMORY.md`).

<a id="command-logger"></a>

### Dettagli di command-logger

Registra ogni comando slash in `~/.openclaw/logs/commands.log`.

<a id="boot-md"></a>

### Dettagli di boot-md

Esegue `BOOT.md` dal workspace attivo all'avvio del gateway.

## Hook dei plugin

I plugin possono registrare hook tramite il Plugin SDK per un'integrazione più profonda: intercettare chiamate agli strumenti, modificare prompt, controllare il flusso dei messaggi e altro ancora. Il Plugin SDK espone 28 hook che coprono la risoluzione del modello, il ciclo di vita dell'agente, il flusso dei messaggi, l'esecuzione degli strumenti, il coordinamento dei sottoagenti e il ciclo di vita del gateway.

Per il riferimento completo sugli hook dei plugin, inclusi `before_tool_call`, `before_agent_reply`, `before_install` e tutti gli altri hook dei plugin, vedi [Architettura dei plugin](/it/plugins/architecture#provider-runtime-hooks).

## Configurazione

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "session-memory": { "enabled": true },
        "command-logger": { "enabled": false }
      }
    }
  }
}
```

Variabili di ambiente per hook:

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "my-hook": {
          "enabled": true,
          "env": { "MY_CUSTOM_VAR": "value" }
        }
      }
    }
  }
}
```

Directory di hook aggiuntive:

```json
{
  "hooks": {
    "internal": {
      "load": {
        "extraDirs": ["/path/to/more/hooks"]
      }
    }
  }
}
```

<Note>
Il formato di configurazione legacy dell'array `hooks.internal.handlers` è ancora supportato per retrocompatibilità, ma i nuovi hook dovrebbero usare il sistema basato sul rilevamento.
</Note>

## Riferimento CLI

```bash
# Elenca tutti gli hook (aggiungi --eligible, --verbose o --json)
openclaw hooks list

# Mostra informazioni dettagliate su un hook
openclaw hooks info <hook-name>

# Mostra il riepilogo dell'idoneità
openclaw hooks check

# Abilita/disabilita
openclaw hooks enable <hook-name>
openclaw hooks disable <hook-name>
```

## Buone pratiche

- **Mantieni gli handler veloci.** Gli hook vengono eseguiti durante l'elaborazione dei comandi. Per i lavori pesanti usa fire-and-forget con `void processInBackground(event)`.
- **Gestisci gli errori con attenzione.** Incapsula le operazioni rischiose in try/catch; non lanciare eccezioni così gli altri handler possono continuare a essere eseguiti.
- **Filtra presto gli eventi.** Esci immediatamente se il tipo/azione dell'evento non è rilevante.
- **Usa chiavi evento specifiche.** Preferisci `"events": ["command:new"]` a `"events": ["command"]` per ridurre l'overhead.

## Risoluzione dei problemi

### Hook non rilevato

```bash
# Verifica la struttura della directory
ls -la ~/.openclaw/hooks/my-hook/
# Dovrebbe mostrare: HOOK.md, handler.ts

# Elenca tutti gli hook rilevati
openclaw hooks list
```

### Hook non idoneo

```bash
openclaw hooks info my-hook
```

Controlla la presenza di binari mancanti (PATH), variabili di ambiente, valori di configurazione o compatibilità con il sistema operativo.

### Hook non eseguito

1. Verifica che l'hook sia abilitato: `openclaw hooks list`
2. Riavvia il processo del gateway in modo che gli hook vengano ricaricati.
3. Controlla i log del gateway: `./scripts/clawlog.sh | grep hook`

## Correlati

- [Riferimento CLI: hooks](/cli/hooks)
- [Webhook](/it/automation/cron-jobs#webhooks)
- [Architettura dei plugin](/it/plugins/architecture#provider-runtime-hooks) — riferimento completo degli hook dei plugin
- [Configurazione](/it/gateway/configuration-reference#hooks)
