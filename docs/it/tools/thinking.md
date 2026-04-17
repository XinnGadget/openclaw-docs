---
read_when:
    - Regolazione dell’analisi, della modalità rapida o dell’analisi dettagliata della sintassi delle direttive o dei valori predefiniti
summary: Sintassi delle direttive per /think, /fast, /verbose, /trace e visibilità del ragionamento
title: Livelli di ragionamento
x-i18n:
    generated_at: "2026-04-17T08:17:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1cb44a7bf75546e5a8c3204e12f3297221449b881161d173dea4983da3921649
    source_path: tools/thinking.md
    workflow: 15
---

# Livelli di ragionamento (direttive /think)

## Cosa fa

- Direttiva inline in qualsiasi corpo in ingresso: `/t <level>`, `/think:<level>` o `/thinking <level>`.
- Livelli (alias): `off | minimal | low | medium | high | xhigh | adaptive`
  - minimal → “think”
  - low → “think hard”
  - medium → “think harder”
  - high → “ultrathink” (budget massimo)
  - xhigh → “ultrathink+” (GPT-5.2 + modelli Codex ed effort Anthropic Claude Opus 4.7)
  - adaptive → ragionamento adattivo gestito dal provider (supportato per Anthropic Claude 4.6 e Opus 4.7)
  - `x-high`, `x_high`, `extra-high`, `extra high` e `extra_high` vengono mappati a `xhigh`.
  - `highest`, `max` vengono mappati a `high`.
- Note sul provider:
  - I modelli Anthropic Claude 4.6 usano `adaptive` per impostazione predefinita quando non è impostato alcun livello di ragionamento esplicito.
  - Anthropic Claude Opus 4.7 non usa il ragionamento adattivo per impostazione predefinita. Il valore predefinito dell’effort API resta gestito dal provider a meno che non imposti esplicitamente un livello di ragionamento.
  - Anthropic Claude Opus 4.7 mappa `/think xhigh` al ragionamento adattivo più `output_config.effort: "xhigh"`, perché `/think` è una direttiva di ragionamento e `xhigh` è l’impostazione di effort di Opus 4.7.
  - MiniMax (`minimax/*`) nel percorso di streaming compatibile con Anthropic usa per impostazione predefinita `thinking: { type: "disabled" }` a meno che tu non imposti esplicitamente il ragionamento nei parametri del modello o della richiesta. Questo evita deltas `reasoning_content` esposti dal formato stream Anthropic non nativo di MiniMax.
  - Z.AI (`zai/*`) supporta solo ragionamento binario (`on`/`off`). Qualsiasi livello diverso da `off` viene trattato come `on` (mappato a `low`).
  - Moonshot (`moonshot/*`) mappa `/think off` a `thinking: { type: "disabled" }` e qualsiasi livello diverso da `off` a `thinking: { type: "enabled" }`. Quando il ragionamento è abilitato, Moonshot accetta solo `tool_choice` `auto|none`; OpenClaw normalizza i valori incompatibili in `auto`.

## Ordine di risoluzione

1. Direttiva inline nel messaggio (si applica solo a quel messaggio).
2. Override di sessione (impostato inviando un messaggio contenente solo la direttiva).
3. Valore predefinito per agente (`agents.list[].thinkingDefault` nella config).
4. Valore predefinito globale (`agents.defaults.thinkingDefault` nella config).
5. Fallback: `adaptive` per i modelli Anthropic Claude 4.6, `off` per Anthropic Claude Opus 4.7 se non configurato esplicitamente, `low` per gli altri modelli capaci di ragionamento, `off` altrimenti.

## Impostazione di un valore predefinito di sessione

- Invia un messaggio che contenga **solo** la direttiva (spazi consentiti), ad esempio `/think:medium` o `/t high`.
- Questo resta valido per la sessione corrente (per mittente per impostazione predefinita); viene cancellato con `/think:off` o al reset per inattività della sessione.
- Viene inviata una risposta di conferma (`Thinking level set to high.` / `Thinking disabled.`). Se il livello non è valido (ad esempio `/thinking big`), il comando viene rifiutato con un suggerimento e lo stato della sessione resta invariato.
- Invia `/think` (o `/think:`) senza argomento per vedere il livello di ragionamento corrente.

## Applicazione per agente

- **Pi incorporato**: il livello risolto viene passato al runtime dell’agente Pi in-process.

## Modalità rapida (/fast)

- Livelli: `on|off`.
- Un messaggio contenente solo la direttiva attiva/disattiva un override della modalità rapida di sessione e risponde con `Fast mode enabled.` / `Fast mode disabled.`.
- Invia `/fast` (o `/fast status`) senza modalità per vedere lo stato effettivo corrente della modalità rapida.
- OpenClaw risolve la modalità rapida in questo ordine:
  1. `/fast on|off` inline/solo direttiva
  2. Override di sessione
  3. Valore predefinito per agente (`agents.list[].fastModeDefault`)
  4. Config per modello: `agents.defaults.models["<provider>/<model>"].params.fastMode`
  5. Fallback: `off`
- Per `openai/*`, la modalità rapida viene mappata all’elaborazione prioritaria di OpenAI inviando `service_tier=priority` nelle richieste Responses supportate.
- Per `openai-codex/*`, la modalità rapida invia lo stesso flag `service_tier=priority` nelle Codex Responses. OpenClaw mantiene un unico interruttore `/fast` condiviso tra entrambi i percorsi di autenticazione.
- Per le richieste pubbliche dirette `anthropic/*`, incluso il traffico autenticato via OAuth inviato a `api.anthropic.com`, la modalità rapida viene mappata ai service tier di Anthropic: `/fast on` imposta `service_tier=auto`, `/fast off` imposta `service_tier=standard_only`.
- Per `minimax/*` nel percorso compatibile con Anthropic, `/fast on` (o `params.fastMode: true`) riscrive `MiniMax-M2.7` in `MiniMax-M2.7-highspeed`.
- I parametri di modello espliciti Anthropic `serviceTier` / `service_tier` hanno priorità sul valore predefinito della modalità rapida quando sono entrambi impostati. OpenClaw continua comunque a saltare l’iniezione del service tier Anthropic per URL base proxy non Anthropic.

## Direttive verbose (/verbose o /v)

- Livelli: `on` (minimal) | `full` | `off` (predefinito).
- Un messaggio contenente solo la direttiva attiva/disattiva il verbose di sessione e risponde con `Verbose logging enabled.` / `Verbose logging disabled.`; i livelli non validi restituiscono un suggerimento senza modificare lo stato.
- `/verbose off` memorizza un override di sessione esplicito; cancellalo tramite l’interfaccia Sessions scegliendo `inherit`.
- La direttiva inline si applica solo a quel messaggio; altrimenti si applicano i valori predefiniti di sessione/globali.
- Invia `/verbose` (o `/verbose:`) senza argomento per vedere il livello verbose corrente.
- Quando il verbose è attivo, gli agenti che emettono risultati strutturati degli strumenti (Pi, altri agenti JSON) rimandano ogni chiamata di strumento come messaggio separato contenente solo metadati, con prefisso `<emoji> <tool-name>: <arg>` quando disponibile (path/comando). Questi riepiloghi degli strumenti vengono inviati non appena ogni strumento si avvia (bolle separate), non come delta in streaming.
- I riepiloghi degli errori degli strumenti restano visibili in modalità normale, ma i suffissi con i dettagli grezzi dell’errore sono nascosti a meno che verbose non sia `on` o `full`.
- Quando verbose è `full`, anche gli output degli strumenti vengono inoltrati dopo il completamento (bolla separata, troncata a una lunghezza sicura). Se attivi/disattivi `/verbose on|full|off` mentre un’esecuzione è in corso, le bolle degli strumenti successive rispettano la nuova impostazione.

## Direttive di trace del Plugin (/trace)

- Livelli: `on` | `off` (predefinito).
- Un messaggio contenente solo la direttiva attiva/disattiva l’output di trace del Plugin di sessione e risponde con `Plugin trace enabled.` / `Plugin trace disabled.`.
- La direttiva inline si applica solo a quel messaggio; altrimenti si applicano i valori predefiniti di sessione/globali.
- Invia `/trace` (o `/trace:`) senza argomento per vedere il livello di trace corrente.
- `/trace` è più ristretto di `/verbose`: espone solo righe di trace/debug possedute dal Plugin come i riepiloghi di debug di Active Memory.
- Le righe di trace possono apparire in `/status` e come messaggio diagnostico di follow-up dopo la normale risposta dell’assistente.

## Visibilità del ragionamento (/reasoning)

- Livelli: `on|off|stream`.
- Un messaggio contenente solo la direttiva attiva/disattiva se i blocchi di ragionamento vengono mostrati nelle risposte.
- Quando è abilitato, il ragionamento viene inviato come **messaggio separato** con prefisso `Reasoning:`.
- `stream` (solo Telegram): trasmette il ragionamento nella bozza del messaggio Telegram mentre la risposta viene generata, poi invia la risposta finale senza ragionamento.
- Alias: `/reason`.
- Invia `/reasoning` (o `/reasoning:`) senza argomento per vedere il livello di ragionamento corrente.
- Ordine di risoluzione: direttiva inline, poi override di sessione, poi valore predefinito per agente (`agents.list[].reasoningDefault`), poi fallback (`off`).

## Correlati

- La documentazione sulla modalità elevata si trova in [Modalità elevata](/it/tools/elevated).

## Heartbeat

- Il corpo della probe Heartbeat è il prompt heartbeat configurato (predefinito: `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`). Le direttive inline in un messaggio heartbeat si applicano normalmente (ma evita di cambiare i valori predefiniti di sessione dagli heartbeat).
- La consegna di Heartbeat usa per impostazione predefinita solo il payload finale. Per inviare anche il messaggio separato `Reasoning:` (quando disponibile), imposta `agents.defaults.heartbeat.includeReasoning: true` oppure per agente `agents.list[].heartbeat.includeReasoning: true`.

## Interfaccia chat web

- Il selettore di ragionamento della chat web rispecchia il livello memorizzato della sessione dallo store/config della sessione in ingresso quando la pagina viene caricata.
- Selezionare un altro livello scrive immediatamente l’override di sessione tramite `sessions.patch`; non attende l’invio successivo e non è un override `thinkingOnce` monouso.
- La prima opzione è sempre `Default (<resolved level>)`, dove il valore predefinito risolto proviene dal modello attivo della sessione: `adaptive` per Claude 4.6 su Anthropic, `off` per Anthropic Claude Opus 4.7 se non configurato, `low` per gli altri modelli capaci di ragionamento, `off` altrimenti.
- Il selettore resta consapevole del provider:
  - la maggior parte dei provider mostra `off | minimal | low | medium | high | adaptive`
  - Anthropic Claude Opus 4.7 mostra `off | minimal | low | medium | high | xhigh | adaptive`
  - Z.AI mostra il formato binario `off | on`
- `/think:<level>` continua a funzionare e aggiorna lo stesso livello di sessione memorizzato, così le direttive chat e il selettore restano sincronizzati.
