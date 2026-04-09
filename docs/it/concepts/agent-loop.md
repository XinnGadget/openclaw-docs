---
read_when:
    - Hai bisogno di una panoramica esatta del loop dell'agente o degli eventi del ciclo di vita
summary: Ciclo di vita del loop dell'agente, stream e semantica di attesa
title: Loop dell'agente
x-i18n:
    generated_at: "2026-04-09T01:27:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 32d3a73df8dabf449211a6183a70dcfd2a9b6f584dc76d0c4c9147582b2ca6a1
    source_path: concepts/agent-loop.md
    workflow: 15
---

# Loop dell'agente (OpenClaw)

Un loop agentico è l'esecuzione completa “reale” di un agente: acquisizione → assemblaggio del contesto → inferenza del modello →
esecuzione degli strumenti → risposte in streaming → persistenza. È il percorso autorevole che trasforma un messaggio
in azioni e in una risposta finale, mantenendo coerente lo stato della sessione.

In OpenClaw, un loop è una singola esecuzione serializzata per sessione che emette eventi di ciclo di vita e di stream
mentre il modello ragiona, chiama strumenti e trasmette output in streaming. Questo documento spiega come questo loop autentico
è collegato end-to-end.

## Punti di ingresso

- RPC Gateway: `agent` e `agent.wait`.
- CLI: comando `agent`.

## Come funziona (panoramica)

1. L'RPC `agent` valida i parametri, risolve la sessione (sessionKey/sessionId), rende persistenti i metadati della sessione, restituisce immediatamente `{ runId, acceptedAt }`.
2. `agentCommand` esegue l'agente:
   - risolve il modello + i valori predefiniti di thinking/verbose
   - carica lo snapshot delle Skills
   - chiama `runEmbeddedPiAgent` (runtime pi-agent-core)
   - emette **fine/errore del ciclo di vita** se il loop incorporato non ne emette uno
3. `runEmbeddedPiAgent`:
   - serializza le esecuzioni tramite code per sessione e globali
   - risolve il profilo di modello + autenticazione e costruisce la sessione pi
   - si sottoscrive agli eventi pi e trasmette in streaming i delta dell'assistente/degli strumenti
   - applica il timeout -> interrompe l'esecuzione se superato
   - restituisce payload + metadati di utilizzo
4. `subscribeEmbeddedPiSession` collega gli eventi di pi-agent-core allo stream `agent` di OpenClaw:
   - eventi degli strumenti => `stream: "tool"`
   - delta dell'assistente => `stream: "assistant"`
   - eventi del ciclo di vita => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` usa `waitForAgentRun`:
   - attende la **fine/errore del ciclo di vita** per `runId`
   - restituisce `{ status: ok|error|timeout, startedAt, endedAt, error? }`

## Accodamento + concorrenza

- Le esecuzioni sono serializzate per chiave di sessione (corsia della sessione) e facoltativamente tramite una corsia globale.
- Questo evita race tra strumenti/sessione e mantiene coerente la cronologia della sessione.
- I canali di messaggistica possono scegliere modalità di coda (collect/steer/followup) che alimentano questo sistema di corsie.
  Vedi [Coda dei comandi](/it/concepts/queue).

## Preparazione della sessione + workspace

- Il workspace viene risolto e creato; le esecuzioni in sandbox possono reindirizzare a una root del workspace sandbox.
- Le Skills vengono caricate (o riutilizzate da uno snapshot) e iniettate nell'ambiente e nel prompt.
- I file bootstrap/contesto vengono risolti e iniettati nel report del prompt di sistema.
- Viene acquisito un lock di scrittura della sessione; `SessionManager` viene aperto e preparato prima dello streaming.

## Assemblaggio del prompt + prompt di sistema

- Il prompt di sistema viene costruito a partire dal prompt di base di OpenClaw, dal prompt delle Skills, dal contesto bootstrap e dagli override per esecuzione.
- Vengono applicati i limiti specifici del modello e i token di riserva per la compattazione.
- Vedi [Prompt di sistema](/it/concepts/system-prompt) per ciò che vede il modello.

## Punti di hook (dove puoi intercettare)

OpenClaw ha due sistemi di hook:

- **Hook interni** (hook del Gateway): script guidati da eventi per comandi ed eventi del ciclo di vita.
- **Hook plugin**: punti di estensione all'interno del ciclo di vita dell'agente/degli strumenti e della pipeline del gateway.

### Hook interni (hook del Gateway)

- **`agent:bootstrap`**: viene eseguito durante la costruzione dei file bootstrap prima che il prompt di sistema sia finalizzato.
  Usalo per aggiungere/rimuovere file di contesto bootstrap.
- **Hook dei comandi**: `/new`, `/reset`, `/stop` e altri eventi dei comandi (vedi la documentazione Hooks).

Vedi [Hooks](/it/automation/hooks) per configurazione ed esempi.

### Hook plugin (ciclo di vita dell'agente + del gateway)

Questi vengono eseguiti all'interno del loop dell'agente o della pipeline del gateway:

- **`before_model_resolve`**: viene eseguito prima della sessione (senza `messages`) per sovrascrivere in modo deterministico provider/modello prima della risoluzione del modello.
- **`before_prompt_build`**: viene eseguito dopo il caricamento della sessione (con `messages`) per iniettare `prependContext`, `systemPrompt`, `prependSystemContext` o `appendSystemContext` prima dell'invio del prompt. Usa `prependContext` per testo dinamico per turno e i campi di contesto di sistema per indicazioni stabili che devono trovarsi nello spazio del prompt di sistema.
- **`before_agent_start`**: hook di compatibilità legacy che può essere eseguito in una delle due fasi; preferisci gli hook espliciti sopra.
- **`before_agent_reply`**: viene eseguito dopo le azioni inline e prima della chiamata all'LLM, consentendo a un plugin di prendersi carico del turno e restituire una risposta sintetica o silenziare completamente il turno.
- **`agent_end`**: ispeziona l'elenco finale dei messaggi e i metadati di esecuzione dopo il completamento.
- **`before_compaction` / `after_compaction`**: osserva o annota i cicli di compattazione.
- **`before_tool_call` / `after_tool_call`**: intercetta parametri/risultati degli strumenti.
- **`before_install`**: ispeziona i risultati della scansione integrata e può facoltativamente bloccare installazioni di Skills o plugin.
- **`tool_result_persist`**: trasforma in modo sincrono i risultati degli strumenti prima che vengano scritti nella trascrizione della sessione.
- **`message_received` / `message_sending` / `message_sent`**: hook per messaggi in ingresso + in uscita.
- **`session_start` / `session_end`**: confini del ciclo di vita della sessione.
- **`gateway_start` / `gateway_stop`**: eventi del ciclo di vita del gateway.

Regole decisionali degli hook per le protezioni in uscita/degli strumenti:

- `before_tool_call`: `{ block: true }` è terminale e interrompe i gestori a priorità inferiore.
- `before_tool_call`: `{ block: false }` non ha effetto e non annulla un blocco precedente.
- `before_install`: `{ block: true }` è terminale e interrompe i gestori a priorità inferiore.
- `before_install`: `{ block: false }` non ha effetto e non annulla un blocco precedente.
- `message_sending`: `{ cancel: true }` è terminale e interrompe i gestori a priorità inferiore.
- `message_sending`: `{ cancel: false }` non ha effetto e non annulla una cancellazione precedente.

Vedi [Hook plugin](/it/plugins/architecture#provider-runtime-hooks) per l'API degli hook e i dettagli di registrazione.

## Streaming + risposte parziali

- I delta dell'assistente vengono trasmessi in streaming da pi-agent-core ed emessi come eventi `assistant`.
- Lo streaming a blocchi può emettere risposte parziali su `text_end` o `message_end`.
- Lo streaming del ragionamento può essere emesso come stream separato o come risposte a blocchi.
- Vedi [Streaming](/it/concepts/streaming) per il comportamento di suddivisione in chunk e delle risposte a blocchi.

## Esecuzione degli strumenti + strumenti di messaggistica

- Gli eventi di avvio/aggiornamento/fine degli strumenti vengono emessi sullo stream `tool`.
- I risultati degli strumenti vengono sanificati per dimensione e payload immagine prima della registrazione/emissione.
- Gli invii degli strumenti di messaggistica vengono tracciati per sopprimere conferme duplicate dell'assistente.

## Modellazione della risposta + soppressione

- I payload finali vengono assemblati da:
  - testo dell'assistente (e ragionamento facoltativo)
  - riepiloghi inline degli strumenti (quando verbose + consentito)
  - testo di errore dell'assistente quando il modello restituisce un errore
- Il token silenzioso esatto `NO_REPLY` / `no_reply` viene filtrato dai
  payload in uscita.
- I duplicati degli strumenti di messaggistica vengono rimossi dall'elenco finale dei payload.
- Se non rimangono payload renderizzabili e uno strumento ha restituito un errore, viene emessa
  una risposta di fallback per l'errore dello strumento
  (a meno che uno strumento di messaggistica abbia già inviato una risposta visibile all'utente).

## Compattazione + tentativi

- La compattazione automatica emette eventi di stream `compaction` e può attivare un nuovo tentativo.
- Al nuovo tentativo, i buffer in memoria e i riepiloghi degli strumenti vengono reimpostati per evitare output duplicati.
- Vedi [Compattazione](/it/concepts/compaction) per la pipeline di compattazione.

## Stream di eventi (attualmente)

- `lifecycle`: emesso da `subscribeEmbeddedPiSession` (e come fallback da `agentCommand`)
- `assistant`: delta in streaming da pi-agent-core
- `tool`: eventi degli strumenti in streaming da pi-agent-core

## Gestione del canale chat

- I delta dell'assistente vengono inseriti in buffer in messaggi chat `delta`.
- Un `final` della chat viene emesso alla **fine/errore del ciclo di vita**.

## Timeout

- Valore predefinito di `agent.wait`: 30s (solo l'attesa). Il parametro `timeoutMs` esegue l'override.
- Runtime dell'agente: `agents.defaults.timeoutSeconds` predefinito 172800s (48 ore); applicato nel timer di interruzione di `runEmbeddedPiAgent`.
- Timeout di inattività dell'LLM: `agents.defaults.llm.idleTimeoutSeconds` interrompe una richiesta al modello quando non arrivano chunk di risposta prima della finestra di inattività. Impostalo esplicitamente per modelli locali lenti o provider di ragionamento/chiamata strumenti; impostalo a 0 per disabilitarlo. Se non è impostato, OpenClaw usa `agents.defaults.timeoutSeconds` se configurato, altrimenti 60s. Le esecuzioni attivate da cron senza un timeout esplicito dell'LLM o dell'agente disabilitano il watchdog di inattività e si affidano al timeout esterno del cron.

## Dove le cose possono terminare in anticipo

- Timeout dell'agente (interruzione)
- AbortSignal (annullamento)
- Disconnessione del gateway o timeout RPC
- Timeout di `agent.wait` (solo attesa, non arresta l'agente)

## Correlati

- [Strumenti](/it/tools) — strumenti dell'agente disponibili
- [Hooks](/it/automation/hooks) — script guidati da eventi attivati dagli eventi del ciclo di vita dell'agente
- [Compattazione](/it/concepts/compaction) — come vengono riepilogate le conversazioni lunghe
- [Approvazioni Exec](/it/tools/exec-approvals) — controlli di approvazione per i comandi shell
- [Thinking](/it/tools/thinking) — configurazione del livello di thinking/ragionamento
