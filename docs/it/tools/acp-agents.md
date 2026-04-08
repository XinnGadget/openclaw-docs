---
read_when:
    - Esecuzione di harness di coding tramite ACP
    - Configurazione di sessioni ACP vincolate alla conversazione sui canali di messaggistica
    - Associazione di una conversazione di un canale di messaggi a una sessione ACP persistente
    - Risoluzione dei problemi del backend ACP e del wiring dei plugin
    - Uso dei comandi /acp dalla chat
summary: Usa sessioni runtime ACP per Codex, Claude Code, Cursor, Gemini CLI, OpenClaw ACP e altri agent harness
title: Agenti ACP
x-i18n:
    generated_at: "2026-04-08T02:20:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: 71c7c0cdae5247aefef17a0029360950a1c2987ddcee21a1bb7d78c67da52950
    source_path: tools/acp-agents.md
    workflow: 15
---

# Agenti ACP

Le sessioni [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) consentono a OpenClaw di eseguire harness di coding esterni (ad esempio Pi, Claude Code, Codex, Cursor, Copilot, OpenClaw ACP, OpenCode, Gemini CLI e altri harness ACPX supportati) tramite un plugin backend ACP.

Se chiedi a OpenClaw in linguaggio naturale di "eseguire questo in Codex" o "avviare Claude Code in un thread", OpenClaw dovrebbe instradare quella richiesta al runtime ACP (non al runtime nativo dei sub-agent). Ogni avvio di sessione ACP viene tracciato come [attività in background](/it/automation/tasks).

Se vuoi che Codex o Claude Code si connettano direttamente come client MCP esterni
a conversazioni di canale OpenClaw esistenti, usa invece [`openclaw mcp serve`](/cli/mcp) di ACP.

## Quale pagina mi serve?

Ci sono tre superfici vicine che è facile confondere:

| Vuoi... | Usa questo | Note |
| --- | --- | --- |
| Eseguire Codex, Claude Code, Gemini CLI o un altro harness esterno _tramite_ OpenClaw | Questa pagina: agenti ACP | Sessioni vincolate alla chat, `/acp spawn`, `sessions_spawn({ runtime: "acp" })`, attività in background, controlli runtime |
| Esporre una sessione OpenClaw Gateway _come_ server ACP per un editor o client | [`openclaw acp`](/cli/acp) | Modalità bridge. L'IDE/client parla ACP con OpenClaw su stdio/WebSocket |
| Riutilizzare una CLI AI locale come modello di fallback solo testuale | [CLI Backends](/it/gateway/cli-backends) | Non ACP. Nessun tool OpenClaw, nessun controllo ACP, nessun runtime harness |

## Funziona immediatamente?

Di solito sì.

- Le installazioni nuove ora includono il plugin runtime `acpx` integrato abilitato per impostazione predefinita.
- Il plugin `acpx` integrato preferisce il proprio binario `acpx` locale al plugin e bloccato a una versione specifica.
- All'avvio, OpenClaw verifica quel binario e lo autoripara se necessario.
- Inizia con `/acp doctor` se vuoi un rapido controllo di disponibilità.

Cosa può ancora succedere al primo utilizzo:

- Un adapter harness di destinazione può essere recuperato on demand con `npx` la prima volta che usi quell'harness.
- L'autenticazione del vendor deve comunque esistere sull'host per quell'harness.
- Se l'host non ha accesso a npm/rete, i recuperi dell'adapter al primo avvio possono fallire finché le cache non vengono preriscaldate o l'adapter non viene installato in un altro modo.

Esempi:

- `/acp spawn codex`: OpenClaw dovrebbe essere pronto a inizializzare `acpx`, ma l'adapter ACP di Codex potrebbe comunque richiedere un recupero al primo avvio.
- `/acp spawn claude`: stessa situazione per l'adapter ACP di Claude, più l'autenticazione lato Claude su quell'host.

## Flusso operativo rapido

Usa questo se vuoi un runbook pratico per `/acp`:

1. Avvia una sessione:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. Lavora nella conversazione o nel thread vincolato (oppure indirizza esplicitamente quella session key).
3. Controlla lo stato runtime:
   - `/acp status`
4. Regola le opzioni runtime secondo necessità:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. Dai un'indicazione a una sessione attiva senza sostituire il contesto:
   - `/acp steer restringi il logging e continua`
6. Interrompi il lavoro:
   - `/acp cancel` (interrompe il turno corrente), oppure
   - `/acp close` (chiude la sessione + rimuove i binding)

## Avvio rapido per le persone

Esempi di richieste naturali:

- "Associa questo canale Discord a Codex."
- "Avvia una sessione Codex persistente in un thread qui e mantienila focalizzata."
- "Esegui questo come sessione ACP Claude Code one-shot e riassumi il risultato."
- "Associa questa chat iMessage a Codex e mantieni i follow-up nello stesso workspace."
- "Usa Gemini CLI per questo compito in un thread, poi mantieni i follow-up in quello stesso thread."

Cosa dovrebbe fare OpenClaw:

1. Scegliere `runtime: "acp"`.
2. Risolvere il target harness richiesto (`agentId`, ad esempio `codex`).
3. Se viene richiesto il binding alla conversazione corrente e il canale attivo lo supporta, associare la sessione ACP a quella conversazione.
4. Altrimenti, se viene richiesto il binding al thread e il canale corrente lo supporta, associare la sessione ACP al thread.
5. Instradare i messaggi di follow-up vincolati alla stessa sessione ACP finché non viene tolto il focus/chiusa/scaduta.

## ACP rispetto ai sub-agent

Usa ACP quando vuoi un runtime harness esterno. Usa i sub-agent quando vuoi esecuzioni delegate native di OpenClaw.

| Area | Sessione ACP | Esecuzione sub-agent |
| --- | --- | --- |
| Runtime | Plugin backend ACP (ad esempio acpx) | Runtime nativo sub-agent di OpenClaw |
| Session key | `agent:<agentId>:acp:<uuid>` | `agent:<agentId>:subagent:<uuid>` |
| Comandi principali | `/acp ...` | `/subagents ...` |
| Tool di avvio | `sessions_spawn` con `runtime:"acp"` | `sessions_spawn` (runtime predefinito) |

Vedi anche [Sub-agents](/it/tools/subagents).

## Come ACP esegue Claude Code

Per Claude Code tramite ACP, lo stack è:

1. Piano di controllo della sessione ACP di OpenClaw
2. Plugin runtime `acpx` integrato
3. Adapter ACP Claude
4. Runtime/meccanismo di sessione lato Claude

Distinzione importante:

- ACP Claude è una sessione harness con controlli ACP, ripresa della sessione, tracciamento delle attività in background e binding opzionale a conversazione/thread.
- I CLI backend sono runtime di fallback locali separati solo testuali. Vedi [CLI Backends](/it/gateway/cli-backends).

Per gli operatori, la regola pratica è:

- vuoi `/acp spawn`, sessioni associabili, controlli runtime o lavoro harness persistente: usa ACP
- vuoi un semplice fallback testuale locale tramite la CLI grezza: usa i CLI backend

## Sessioni vincolate

### Binding alla conversazione corrente

Usa `/acp spawn <harness> --bind here` quando vuoi che la conversazione corrente diventi un workspace ACP durevole senza creare un thread figlio.

Comportamento:

- OpenClaw continua a gestire il trasporto del canale, auth, sicurezza e consegna.
- La conversazione corrente viene fissata alla session key ACP generata.
- I messaggi di follow-up in quella conversazione vengono instradati alla stessa sessione ACP.
- `/new` e `/reset` reimpostano sul posto la stessa sessione ACP vincolata.
- `/acp close` chiude la sessione e rimuove il binding alla conversazione corrente.

Cosa significa in pratica:

- `--bind here` mantiene la stessa superficie di chat. Su Discord, il canale corrente resta il canale corrente.
- `--bind here` può comunque creare una nuova sessione ACP se stai avviando nuovo lavoro. Il bind collega quella sessione alla conversazione corrente.
- `--bind here` non crea da solo un thread figlio Discord o un topic Telegram.
- Il runtime ACP può comunque avere la propria directory di lavoro (`cwd`) o un workspace su disco gestito dal backend. Quel workspace runtime è separato dalla superficie di chat e non implica un nuovo thread di messaggistica.
- Se avvii verso un agente ACP diverso e non passi `--cwd`, OpenClaw eredita per impostazione predefinita il workspace **dell'agente di destinazione**, non quello del richiedente.
- Se quel percorso workspace ereditato è mancante (`ENOENT`/`ENOTDIR`), OpenClaw torna al `cwd` predefinito del backend invece di riutilizzare silenziosamente l'albero sbagliato.
- Se il workspace ereditato esiste ma non è accessibile (ad esempio `EACCES`), l'avvio restituisce il vero errore di accesso invece di scartare `cwd`.

Modello mentale:

- superficie di chat: dove le persone continuano a parlare (`canale Discord`, `topic Telegram`, `chat iMessage`)
- sessione ACP: lo stato runtime durevole di Codex/Claude/Gemini verso cui OpenClaw instrada
- thread/topic figlio: una superficie di messaggistica aggiuntiva facoltativa creata solo da `--thread ...`
- workspace runtime: la posizione del filesystem in cui l'harness viene eseguito (`cwd`, checkout del repo, workspace backend)

Esempi:

- `/acp spawn codex --bind here`: mantieni questa chat, avvia o collega una sessione ACP Codex e instrada qui i messaggi futuri
- `/acp spawn codex --thread auto`: OpenClaw può creare un thread/topic figlio e associare lì la sessione ACP
- `/acp spawn codex --bind here --cwd /workspace/repo`: stesso binding di chat dell'esempio sopra, ma Codex viene eseguito in `/workspace/repo`

Supporto al binding della conversazione corrente:

- I canali chat/messaggi che dichiarano il supporto al binding della conversazione corrente possono usare `--bind here` tramite il percorso condiviso di conversation-binding.
- I canali con semantiche personalizzate di thread/topic possono comunque fornire una canonicalizzazione specifica del canale dietro la stessa interfaccia condivisa.
- `--bind here` significa sempre "associa la conversazione corrente sul posto".
- I binding generici alla conversazione corrente usano lo store di binding condiviso di OpenClaw e sopravvivono ai normali riavvii del gateway.

Note:

- `--bind here` e `--thread ...` si escludono a vicenda in `/acp spawn`.
- Su Discord, `--bind here` associa sul posto il canale o thread corrente. `spawnAcpSessions` è richiesto solo quando OpenClaw deve creare un thread figlio per `--thread auto|here`.
- Se il canale attivo non espone binding ACP alla conversazione corrente, OpenClaw restituisce un chiaro messaggio di non supportato.
- `resume` e le domande su "nuova sessione" riguardano la sessione ACP, non il canale. Puoi riutilizzare o sostituire lo stato runtime senza cambiare la superficie di chat corrente.

### Sessioni vincolate al thread

Quando i thread binding sono abilitati per un adapter di canale, le sessioni ACP possono essere associate ai thread:

- OpenClaw associa un thread a una sessione ACP di destinazione.
- I messaggi di follow-up in quel thread vengono instradati alla sessione ACP associata.
- L'output ACP viene consegnato di nuovo allo stesso thread.
- La rimozione del focus/chiusura/archiviazione/scadenza per inattività o per età massima rimuove il binding.

Il supporto al thread binding dipende dall'adapter. Se l'adapter del canale attivo non supporta i thread binding, OpenClaw restituisce un chiaro messaggio di non supportato/non disponibile.

Feature flag richiesti per ACP vincolato al thread:

- `acp.enabled=true`
- `acp.dispatch.enabled` è attivo per impostazione predefinita (imposta `false` per mettere in pausa il dispatch ACP)
- Feature flag di spawn ACP thread del channel-adapter abilitato (specifico dell'adapter)
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### Canali che supportano thread

- Qualsiasi adapter di canale che espone la capacità di binding sessione/thread.
- Supporto integrato attuale:
  - thread/canali Discord
  - topic Telegram (topic del forum in gruppi/supergruppi e topic DM)
- I canali plugin possono aggiungere supporto tramite la stessa interfaccia di binding.

## Impostazioni specifiche del canale

Per flussi di lavoro non effimeri, configura binding ACP persistenti nelle voci `bindings[]` di primo livello.

### Modello di binding

- `bindings[].type="acp"` contrassegna un binding persistente di conversazione ACP.
- `bindings[].match` identifica la conversazione di destinazione:
  - Canale o thread Discord: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Topic forum Telegram: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - Chat DM/di gruppo BlueBubbles: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Preferisci `chat_id:*` o `chat_identifier:*` per binding di gruppo stabili.
  - Chat DM/di gruppo iMessage: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Preferisci `chat_id:*` per binding di gruppo stabili.
- `bindings[].agentId` è l'ID dell'agente OpenClaw proprietario.
- Gli override ACP facoltativi si trovano sotto `bindings[].acp`:
  - `mode` (`persistent` o `oneshot`)
  - `label`
  - `cwd`
  - `backend`

### Valori predefiniti runtime per agente

Usa `agents.list[].runtime` per definire una sola volta i valori predefiniti ACP per agente:

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent` (ID harness, ad esempio `codex` o `claude`)
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

Precedenza degli override per sessioni ACP vincolate:

1. `bindings[].acp.*`
2. `agents.list[].runtime.acp.*`
3. valori predefiniti ACP globali (ad esempio `acp.backend`)

Esempio:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
      {
        id: "claude",
        runtime: {
          type: "acp",
          acp: { agent: "claude", backend: "acpx", mode: "persistent" },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
    {
      type: "acp",
      agentId: "claude",
      match: {
        channel: "telegram",
        accountId: "default",
        peer: { kind: "group", id: "-1001234567890:topic:42" },
      },
      acp: { cwd: "/workspace/repo-b" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "discord", accountId: "default" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "telegram", accountId: "default" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": { requireMention: false },
          },
        },
      },
    },
    telegram: {
      groups: {
        "-1001234567890": {
          topics: { "42": { requireMention: false } },
        },
      },
    },
  },
}
```

Comportamento:

- OpenClaw garantisce che la sessione ACP configurata esista prima dell'uso.
- I messaggi in quel canale o topic vengono instradati alla sessione ACP configurata.
- Nelle conversazioni vincolate, `/new` e `/reset` reimpostano sul posto la stessa session key ACP.
- I binding runtime temporanei (ad esempio creati dai flussi di focus del thread) si applicano comunque quando presenti.
- Per avvii ACP cross-agent senza un `cwd` esplicito, OpenClaw eredita il workspace dell'agente di destinazione dalla configurazione dell'agente.
- I percorsi workspace ereditati mancanti tornano al `cwd` predefinito del backend; i veri errori di accesso su percorsi esistenti emergono come errori di avvio.

## Avviare sessioni ACP (interfacce)

### Da `sessions_spawn`

Usa `runtime: "acp"` per avviare una sessione ACP da un turno agente o chiamata tool.

```json
{
  "task": "Apri il repository e riassumi i test che falliscono",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

Note:

- `runtime` ha come valore predefinito `subagent`, quindi imposta esplicitamente `runtime: "acp"` per le sessioni ACP.
- Se `agentId` viene omesso, OpenClaw usa `acp.defaultAgent` quando configurato.
- `mode: "session"` richiede `thread: true` per mantenere una conversazione persistente associata.

Dettagli dell'interfaccia:

- `task` (obbligatorio): prompt iniziale inviato alla sessione ACP.
- `runtime` (obbligatorio per ACP): deve essere `"acp"`.
- `agentId` (facoltativo): ID dell'harness ACP di destinazione. Usa `acp.defaultAgent` come fallback se impostato.
- `thread` (facoltativo, predefinito `false`): richiede il flusso di binding al thread quando supportato.
- `mode` (facoltativo): `run` (one-shot) o `session` (persistente).
  - il valore predefinito è `run`
  - se `thread: true` e il mode viene omesso, OpenClaw può usare come predefinito il comportamento persistente in base al percorso runtime
  - `mode: "session"` richiede `thread: true`
- `cwd` (facoltativo): directory di lavoro runtime richiesta (convalidata dalla policy backend/runtime). Se omesso, l'avvio ACP eredita il workspace dell'agente di destinazione quando configurato; i percorsi ereditati mancanti tornano ai valori predefiniti del backend, mentre i veri errori di accesso vengono restituiti.
- `label` (facoltativo): etichetta visibile all'operatore usata nel testo di sessione/banner.
- `resumeSessionId` (facoltativo): riprende una sessione ACP esistente invece di crearne una nuova. L'agente riproduce la propria cronologia di conversazione tramite `session/load`. Richiede `runtime: "acp"`.
- `streamTo` (facoltativo): `"parent"` inoltra i riepiloghi del progresso iniziale dell'esecuzione ACP alla sessione richiedente come eventi di sistema.
  - Quando disponibile, le risposte accettate includono `streamLogPath` che punta a un log JSONL con scope di sessione (`<sessionId>.acp-stream.jsonl`) che puoi seguire per la cronologia completa del relay.

### Riprendere una sessione esistente

Usa `resumeSessionId` per continuare una sessione ACP precedente invece di ricominciare da zero. L'agente riproduce la propria cronologia di conversazione tramite `session/load`, quindi riprende con il contesto completo di ciò che è accaduto prima.

```json
{
  "task": "Continua da dove ci eravamo fermati — correggi i test rimanenti che falliscono",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

Casi d'uso comuni:

- Passare una sessione Codex dal laptop al telefono — chiedi al tuo agente di riprendere da dove avevi lasciato
- Continuare una sessione di coding iniziata in modo interattivo nella CLI, ora in modalità headless tramite il tuo agente
- Riprendere un lavoro interrotto da un riavvio del gateway o da un timeout di inattività

Note:

- `resumeSessionId` richiede `runtime: "acp"` — restituisce un errore se usato con il runtime sub-agent.
- `resumeSessionId` ripristina la cronologia della conversazione ACP upstream; `thread` e `mode` continuano ad applicarsi normalmente alla nuova sessione OpenClaw che stai creando, quindi `mode: "session"` richiede comunque `thread: true`.
- L'agente di destinazione deve supportare `session/load` (Codex e Claude Code lo fanno).
- Se l'ID sessione non viene trovato, l'avvio fallisce con un errore chiaro — nessun fallback silenzioso a una nuova sessione.

### Smoke test per operatori

Usa questo dopo un deploy del gateway quando vuoi un rapido controllo live che l'avvio ACP
funzioni davvero end-to-end, non soltanto nei test unitari.

Gate consigliato:

1. Verifica la versione/commit del gateway distribuito sull'host di destinazione.
2. Conferma che il sorgente distribuito includa l'accettazione della lineage ACP in
   `src/gateway/sessions-patch.ts` (`subagent:* or acp:* sessions`).
3. Apri una sessione bridge ACPX temporanea verso un agente live (ad esempio
   `razor(main)` su `jpclawhq`).
4. Chiedi a quell'agente di chiamare `sessions_spawn` con:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - task: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. Verifica che l'agente segnali:
   - `accepted=yes`
   - una `childSessionKey` reale
   - nessun errore di validazione
6. Pulisci la sessione bridge ACPX temporanea.

Prompt di esempio per l'agente live:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

Note:

- Mantieni questo smoke test su `mode: "run"` a meno che tu non stia testando intenzionalmente
  sessioni ACP persistenti associate a thread.
- Non richiedere `streamTo: "parent"` per il gate di base. Quel percorso dipende da
  capacità del richiedente/sessione ed è un controllo di integrazione separato.
- Tratta il test di `mode: "session"` associato a thread come un secondo passaggio di integrazione
  più ricco da un thread Discord reale o un topic Telegram.

## Compatibilità con il sandbox

Le sessioni ACP attualmente vengono eseguite sul runtime host, non all'interno del sandbox OpenClaw.

Limitazioni attuali:

- Se la sessione richiedente è in sandbox, gli avvii ACP vengono bloccati sia per `sessions_spawn({ runtime: "acp" })` sia per `/acp spawn`.
  - Errore: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `sessions_spawn` con `runtime: "acp"` non supporta `sandbox: "require"`.
  - Errore: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

Usa `runtime: "subagent"` quando hai bisogno di un'esecuzione imposta dal sandbox.

### Dal comando `/acp`

Usa `/acp spawn` per un controllo esplicito da operatore dalla chat quando necessario.

```text
/acp spawn codex --mode persistent --thread auto
/acp spawn codex --mode oneshot --thread off
/acp spawn codex --bind here
/acp spawn codex --thread here
```

Flag principali:

- `--mode persistent|oneshot`
- `--bind here|off`
- `--thread auto|here|off`
- `--cwd <absolute-path>`
- `--label <name>`

Vedi [Slash Commands](/it/tools/slash-commands).

## Risoluzione della destinazione della sessione

La maggior parte delle azioni `/acp` accetta una destinazione di sessione facoltativa (`session-key`, `session-id` o `session-label`).

Ordine di risoluzione:

1. Argomento target esplicito (o `--session` per `/acp steer`)
   - prova prima la key
   - poi l'ID sessione in forma UUID
   - poi l'etichetta
2. Binding del thread corrente (se questa conversazione/thread è associata a una sessione ACP)
3. Fallback alla sessione richiedente corrente

Sia i binding della conversazione corrente sia i thread binding partecipano al passaggio 2.

Se nessuna destinazione viene risolta, OpenClaw restituisce un errore chiaro (`Unable to resolve session target: ...`).

## Modalità di bind all'avvio

`/acp spawn` supporta `--bind here|off`.

| Modalità | Comportamento |
| --- | --- |
| `here` | Associa sul posto la conversazione attiva corrente; fallisce se non ce n'è una attiva. |
| `off` | Non crea un binding alla conversazione corrente. |

Note:

- `--bind here` è il percorso operativo più semplice per "rendere questo canale o chat supportato da Codex".
- `--bind here` non crea un thread figlio.
- `--bind here` è disponibile solo sui canali che espongono il supporto al binding della conversazione corrente.
- `--bind` e `--thread` non possono essere combinati nella stessa chiamata `/acp spawn`.

## Modalità thread all'avvio

`/acp spawn` supporta `--thread auto|here|off`.

| Modalità | Comportamento |
| --- | --- |
| `auto` | In un thread attivo: associa quel thread. Fuori da un thread: crea/associa un thread figlio quando supportato. |
| `here` | Richiede il thread attivo corrente; fallisce se non sei in un thread. |
| `off` | Nessun binding. La sessione viene avviata non vincolata. |

Note:

- Sulle superfici che non supportano thread binding, il comportamento predefinito è di fatto `off`.
- L'avvio con binding al thread richiede il supporto della policy del canale:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- Usa `--bind here` quando vuoi fissare la conversazione corrente senza creare un thread figlio.

## Controlli ACP

Famiglia di comandi disponibile:

- `/acp spawn`
- `/acp cancel`
- `/acp steer`
- `/acp close`
- `/acp status`
- `/acp set-mode`
- `/acp set`
- `/acp cwd`
- `/acp permissions`
- `/acp timeout`
- `/acp model`
- `/acp reset-options`
- `/acp sessions`
- `/acp doctor`
- `/acp install`

`/acp status` mostra le opzioni runtime effettive e, quando disponibili, sia gli identificatori di sessione a livello runtime sia quelli a livello backend.

Alcuni controlli dipendono dalle capacità del backend. Se un backend non supporta un controllo, OpenClaw restituisce un chiaro errore di controllo non supportato.

## Ricettario dei comandi ACP

| Comando | Cosa fa | Esempio |
| --- | --- | --- |
| `/acp spawn` | Crea una sessione ACP; binding corrente o binding al thread facoltativi. | `/acp spawn codex --bind here --cwd /repo` |
| `/acp cancel` | Annulla il turno in corso per la sessione di destinazione. | `/acp cancel agent:codex:acp:<uuid>` |
| `/acp steer` | Invia un'istruzione di steer a una sessione in esecuzione. | `/acp steer --session support inbox dai priorità ai test che falliscono` |
| `/acp close` | Chiude la sessione e rimuove il binding dai target thread. | `/acp close` |
| `/acp status` | Mostra backend, modalità, stato, opzioni runtime, capacità. | `/acp status` |
| `/acp set-mode` | Imposta la modalità runtime per la sessione di destinazione. | `/acp set-mode plan` |
| `/acp set` | Scrittura generica di opzione di configurazione runtime. | `/acp set model openai/gpt-5.4` |
| `/acp cwd` | Imposta l'override della directory di lavoro runtime. | `/acp cwd /Users/user/Projects/repo` |
| `/acp permissions` | Imposta il profilo della policy di approvazione. | `/acp permissions strict` |
| `/acp timeout` | Imposta il timeout runtime (secondi). | `/acp timeout 120` |
| `/acp model` | Imposta l'override del modello runtime. | `/acp model anthropic/claude-opus-4-6` |
| `/acp reset-options` | Rimuove gli override delle opzioni runtime della sessione. | `/acp reset-options` |
| `/acp sessions` | Elenca le sessioni ACP recenti dallo store. | `/acp sessions` |
| `/acp doctor` | Integrità backend, capacità, correzioni operative. | `/acp doctor` |
| `/acp install` | Stampa passaggi deterministici di installazione e abilitazione. | `/acp install` |

`/acp sessions` legge lo store per la sessione corrente vincolata o richiedente. I comandi che accettano token `session-key`, `session-id` o `session-label` risolvono i target tramite la discovery delle sessioni gateway, incluse root `session.store` personalizzate per agente.

## Mappatura delle opzioni runtime

`/acp` ha comandi convenience e un setter generico.

Operazioni equivalenti:

- `/acp model <id>` corrisponde alla chiave di configurazione runtime `model`.
- `/acp permissions <profile>` corrisponde alla chiave di configurazione runtime `approval_policy`.
- `/acp timeout <seconds>` corrisponde alla chiave di configurazione runtime `timeout`.
- `/acp cwd <path>` aggiorna direttamente l'override `cwd` runtime.
- `/acp set <key> <value>` è il percorso generico.
  - Caso speciale: `key=cwd` usa il percorso di override `cwd`.
- `/acp reset-options` cancella tutti gli override runtime per la sessione di destinazione.

## Supporto harness acpx (attuale)

Alias harness integrati attuali di acpx:

- `claude`
- `codex`
- `copilot`
- `cursor` (Cursor CLI: `cursor-agent acp`)
- `droid`
- `gemini`
- `iflow`
- `kilocode`
- `kimi`
- `kiro`
- `openclaw`
- `opencode`
- `pi`
- `qwen`

Quando OpenClaw usa il backend acpx, preferisci questi valori per `agentId` a meno che la tua configurazione acpx non definisca alias agente personalizzati.
Se la tua installazione locale di Cursor espone ancora ACP come `agent acp`, esegui l'override del comando agente `cursor` nella configurazione acpx invece di cambiare il valore predefinito integrato.

L'uso diretto della CLI acpx può anche indirizzare adapter arbitrari tramite `--agent <command>`, ma questa via di fuga grezza è una funzionalità della CLI acpx (non il normale percorso `agentId` di OpenClaw).

## Configurazione richiesta

Baseline ACP core:

```json5
{
  acp: {
    enabled: true,
    // Facoltativo. Il valore predefinito è true; imposta false per mettere in pausa il dispatch ACP mantenendo i controlli /acp.
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: [
      "claude",
      "codex",
      "copilot",
      "cursor",
      "droid",
      "gemini",
      "iflow",
      "kilocode",
      "kimi",
      "kiro",
      "openclaw",
      "opencode",
      "pi",
      "qwen",
    ],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

La configurazione del thread binding è specifica del channel-adapter. Esempio per Discord:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true,
      },
    },
  },
}
```

Se l'avvio ACP vincolato al thread non funziona, verifica prima la feature flag dell'adapter:

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

I binding alla conversazione corrente non richiedono la creazione di thread figli. Richiedono un contesto di conversazione attivo e un channel-adapter che esponga binding ACP alla conversazione.

Vedi [Configuration Reference](/it/gateway/configuration-reference).

## Configurazione del plugin per il backend acpx

Le installazioni nuove includono il plugin runtime `acpx` integrato abilitato per impostazione predefinita, quindi ACP
di solito funziona senza un passaggio manuale di installazione plugin.

Inizia con:

```text
/acp doctor
```

Se hai disabilitato `acpx`, lo hai negato tramite `plugins.allow` / `plugins.deny`, o vuoi
passare a un checkout locale di sviluppo, usa il percorso plugin esplicito:

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

Installazione del workspace locale durante lo sviluppo:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

Poi verifica l'integrità del backend:

```text
/acp doctor
```

### Configurazione del comando e della versione di acpx

Per impostazione predefinita, il plugin backend acpx integrato (`acpx`) usa il binario locale al plugin bloccato:

1. Il comando usa per impostazione predefinita `node_modules/.bin/acpx` locale al plugin all'interno del pacchetto plugin ACPX.
2. La versione prevista usa per impostazione predefinita il pin dell'estensione.
3. All'avvio, OpenClaw registra immediatamente il backend ACP come non pronto.
4. Un job di verifica in background controlla `acpx --version`.
5. Se il binario locale al plugin manca o non corrisponde, esegue:
   `npm install --omit=dev --no-save acpx@<pinned>` e verifica di nuovo.

Puoi eseguire l'override di comando/versione nella configurazione del plugin:

```json
{
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "command": "../acpx/dist/cli.js",
          "expectedVersion": "any"
        }
      }
    }
  }
}
```

Note:

- `command` accetta un percorso assoluto, un percorso relativo o un nome comando (`acpx`).
- I percorsi relativi vengono risolti dalla directory workspace OpenClaw.
- `expectedVersion: "any"` disabilita il controllo rigoroso della versione.
- Quando `command` punta a un binario/percorso personalizzato, l'auto-installazione locale al plugin viene disabilitata.
- L'avvio di OpenClaw resta non bloccante mentre viene eseguito il controllo di integrità del backend.

Vedi [Plugins](/it/tools/plugin).

### Installazione automatica delle dipendenze

Quando installi OpenClaw globalmente con `npm install -g openclaw`, le dipendenze runtime di acpx
(binari specifici per piattaforma) vengono installate automaticamente
tramite un hook postinstall. Se l'installazione automatica fallisce, il gateway continua comunque ad avviarsi
normalmente e segnala la dipendenza mancante tramite `openclaw acp doctor`.

### Bridge MCP dei tool plugin

Per impostazione predefinita, le sessioni ACPX **non** espongono ai harness ACP i tool registrati dai plugin OpenClaw.

Se vuoi che agenti ACP come Codex o Claude Code possano chiamare i tool dei plugin OpenClaw installati
come memory recall/store, abilita il bridge dedicato:

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

Cosa fa:

- Inietta un server MCP integrato chiamato `openclaw-plugin-tools` nel bootstrap della sessione ACPX.
- Espone i tool plugin già registrati dai plugin OpenClaw installati e abilitati.
- Mantiene la funzionalità esplicita e disattivata per impostazione predefinita.

Note su sicurezza e trust:

- Questo espande la superficie dei tool dell'harness ACP.
- Gli agenti ACP ottengono accesso solo ai tool plugin già attivi nel gateway.
- Tratta questo come lo stesso confine di trust che consentire a quei plugin di eseguire all'interno di
  OpenClaw stesso.
- Controlla i plugin installati prima di abilitarlo.

Le configurazioni `mcpServers` personalizzate continuano a funzionare come prima. Il bridge integrato dei tool plugin è una
comodità aggiuntiva opt-in, non un sostituto della configurazione generica del server MCP.

### Configurazione del timeout runtime

Il plugin `acpx` integrato imposta per impostazione predefinita i turni runtime incorporati a un
timeout di 120 secondi. Questo dà a harness più lenti come Gemini CLI abbastanza tempo per completare
l'avvio e l'inizializzazione ACP. Esegui l'override se il tuo host richiede un limite
runtime diverso:

```bash
openclaw config set plugins.entries.acpx.config.timeoutSeconds 180
```

Riavvia il gateway dopo aver modificato questo valore.

## Configurazione dei permessi

Le sessioni ACP vengono eseguite in modo non interattivo — non c'è alcun TTY per approvare o negare prompt di permessi di scrittura file ed esecuzione shell. Il plugin acpx fornisce due chiavi di configurazione che controllano come vengono gestiti i permessi:

Questi permessi degli harness ACPX sono separati dalle approvazioni exec di OpenClaw e separati dai flag di bypass vendor dei CLI backend come Claude CLI `--permission-mode bypassPermissions`. ACPX `approve-all` è lo switch break-glass a livello harness per le sessioni ACP.

### `permissionMode`

Controlla quali operazioni l'agente harness può eseguire senza chiedere conferma.

| Valore | Comportamento |
| --------------- | --------------------------------------------------------- |
| `approve-all`   | Approva automaticamente tutte le scritture di file e i comandi shell. |
| `approve-reads` | Approva automaticamente solo le letture; scritture ed exec richiedono prompt. |
| `deny-all`      | Nega tutti i prompt di permesso. |

### `nonInteractivePermissions`

Controlla cosa succede quando dovrebbe essere mostrato un prompt di permesso ma non è disponibile alcun TTY interattivo (che è sempre il caso per le sessioni ACP).

| Valore | Comportamento |
| ------ | ----------------------------------------------------------------- |
| `fail` | Interrompe la sessione con `AcpRuntimeError`. **(predefinito)** |
| `deny` | Nega silenziosamente il permesso e continua (degrado graduale). |

### Configurazione

Imposta tramite la configurazione del plugin:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

Riavvia il gateway dopo aver modificato questi valori.

> **Importante:** OpenClaw attualmente usa per impostazione predefinita `permissionMode=approve-reads` e `nonInteractivePermissions=fail`. Nelle sessioni ACP non interattive, qualsiasi scrittura o exec che attiva un prompt di permesso può fallire con `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`.
>
> Se devi limitare i permessi, imposta `nonInteractivePermissions` su `deny` in modo che le sessioni degradino in modo graduale invece di andare in crash.

## Risoluzione dei problemi

| Sintomo | Causa probabile | Correzione |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured` | Plugin backend mancante o disabilitato. | Installa e abilita il plugin backend, poi esegui `/acp doctor`. |
| `ACP is disabled by policy (acp.enabled=false)` | ACP disabilitato globalmente. | Imposta `acp.enabled=true`. |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)` | Il dispatch dai normali messaggi del thread è disabilitato. | Imposta `acp.dispatch.enabled=true`. |
| `ACP agent "<id>" is not allowed by policy` | L'agente non è nella allowlist. | Usa un `agentId` consentito o aggiorna `acp.allowedAgents`. |
| `Unable to resolve session target: ...` | Token key/id/label errato. | Esegui `/acp sessions`, copia la key/label esatta e riprova. |
| `--bind here requires running /acp spawn inside an active ... conversation` | `--bind here` usato senza una conversazione attiva associabile. | Spostati nella chat/canale di destinazione e riprova, oppure usa l'avvio non vincolato. |
| `Conversation bindings are unavailable for <channel>.` | L'adapter non ha la capacità ACP di binding alla conversazione corrente. | Usa `/acp spawn ... --thread ...` dove supportato, configura `bindings[]` di primo livello o passa a un canale supportato. |
| `--thread here requires running /acp spawn inside an active ... thread` | `--thread here` usato fuori da un contesto thread. | Spostati nel thread di destinazione o usa `--thread auto`/`off`. |
| `Only <user-id> can rebind this channel/conversation/thread.` | Un altro utente possiede il target di binding attivo. | Riesegui il bind come proprietario o usa una conversazione o thread diversi. |
| `Thread bindings are unavailable for <channel>.` | L'adapter non ha capacità di thread binding. | Usa `--thread off` o passa a un adapter/canale supportato. |
| `Sandboxed sessions cannot spawn ACP sessions ...` | Il runtime ACP è lato host; la sessione richiedente è in sandbox. | Usa `runtime="subagent"` da sessioni in sandbox, oppure avvia ACP da una sessione non in sandbox. |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...` | `sandbox="require"` richiesto per il runtime ACP. | Usa `runtime="subagent"` per sandbox obbligatorio, oppure usa ACP con `sandbox="inherit"` da una sessione non in sandbox. |
| Metadati ACP mancanti per la sessione vincolata | Metadati della sessione ACP obsoleti/eliminati. | Ricrea con `/acp spawn`, poi riesegui bind/focus del thread. |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode` | `permissionMode` blocca scritture/exec nella sessione ACP non interattiva. | Imposta `plugins.entries.acpx.config.permissionMode` su `approve-all` e riavvia il gateway. Vedi [Configurazione dei permessi](#configurazione-dei-permessi). |
| La sessione ACP fallisce presto con poco output | I prompt di permesso sono bloccati da `permissionMode`/`nonInteractivePermissions`. | Controlla i log del gateway per `AcpRuntimeError`. Per permessi completi, imposta `permissionMode=approve-all`; per degrado graduale, imposta `nonInteractivePermissions=deny`. |
| La sessione ACP resta bloccata indefinitamente dopo aver completato il lavoro | Il processo harness è terminato ma la sessione ACP non ha segnalato il completamento. | Monitora con `ps aux \| grep acpx`; termina manualmente i processi obsoleti. |
