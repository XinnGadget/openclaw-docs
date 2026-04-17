---
read_when:
    - Estendere qa-lab o qa-channel
    - Aggiunta di scenari QA supportati dal repository
    - Creazione di automazione QA a maggiore realismo attorno alla dashboard del Gateway
summary: Forma dell'automazione QA privata per qa-lab, qa-channel, scenari preconfigurati e report di protocollo
title: Automazione QA end-to-end
x-i18n:
    generated_at: "2026-04-17T08:17:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 51f97293c184d7c04c95d9858305668fbc0f93273f587ec7e54896ad5d603ab0
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automazione QA end-to-end

Lo stack QA privato è pensato per esercitare OpenClaw in modo più realistico,
con una forma simile a quella dei canali, rispetto a quanto possa fare un singolo test unitario.

Componenti attuali:

- `extensions/qa-channel`: canale di messaggi sintetico con superfici per DM, canale, thread,
  reazioni, modifica ed eliminazione.
- `extensions/qa-lab`: interfaccia utente di debug e bus QA per osservare la trascrizione,
  iniettare messaggi in ingresso ed esportare un report in Markdown.
- `qa/`: asset seed supportati dal repository per l'attività iniziale e gli scenari QA
  di base.

L'attuale flusso dell'operatore QA è un sito QA a due pannelli:

- Sinistra: dashboard del Gateway (Control UI) con l'agente.
- Destra: QA Lab, che mostra la trascrizione in stile Slack e il piano dello scenario.

Eseguilo con:

```bash
pnpm qa:lab:up
```

Questo compila il sito QA, avvia il lane del Gateway supportato da Docker ed espone la
pagina QA Lab dove un operatore o un ciclo di automazione può assegnare all'agente una missione QA,
osservare il comportamento reale del canale e registrare ciò che ha funzionato, ciò che è fallito o
ciò che è rimasto bloccato.

Per un'iterazione più rapida dell'interfaccia utente di QA Lab senza ricompilare ogni volta l'immagine Docker,
avvia lo stack con un bundle QA Lab montato tramite bind mount:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` mantiene i servizi Docker su un'immagine precompilata e monta tramite bind mount
`extensions/qa-lab/web/dist` nel container `qa-lab`. `qa:lab:watch`
ricompila quel bundle quando cambia, e il browser si ricarica automaticamente quando cambia l'hash
degli asset di QA Lab.

Per un lane smoke Matrix con trasporto reale, esegui:

```bash
pnpm openclaw qa matrix
```

Questo lane esegue il provisioning di un homeserver Tuwunel temporaneo in Docker, registra
utenti temporanei driver, SUT e observer, crea una stanza privata, quindi esegue il vero Plugin
Matrix all'interno di un processo figlio del Gateway QA. Il lane con trasporto live mantiene
la configurazione del processo figlio limitata al trasporto in test, quindi Matrix viene eseguito senza
`qa-channel` nella configurazione del processo figlio. Scrive gli artifact del report strutturato e
un log combinato stdout/stderr nella directory di output Matrix QA selezionata. Per
acquisire anche l'output esterno di build/launcher di `scripts/run-node.mjs`, imposta
`OPENCLAW_RUN_NODE_OUTPUT_LOG=<path>` su un file di log locale al repository.

Per un lane smoke Telegram con trasporto reale, esegui:

```bash
pnpm openclaw qa telegram
```

Questo lane usa come destinazione un vero gruppo privato Telegram invece di eseguire il provisioning di un
server temporaneo. Richiede `OPENCLAW_QA_TELEGRAM_GROUP_ID`,
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` e
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`, oltre a due bot distinti nello stesso
gruppo privato. Il bot SUT deve avere un nome utente Telegram, e l'osservazione bot-to-bot
funziona al meglio quando entrambi i bot hanno la modalità Bot-to-Bot Communication Mode
abilitata in `@BotFather`.

I lane di trasporto live ora condividono un contratto più piccolo invece di inventare
ognuno una propria forma di elenco di scenari.

`qa-channel` rimane la suite ampia di comportamento sintetico del prodotto e non fa parte
della matrice di copertura dei trasporti live.

| Lane     | Canary | Vincolo di menzione | Blocco allowlist | Risposta di primo livello | Ripresa dopo riavvio | Follow-up nel thread | Isolamento del thread | Osservazione reazioni | Comando help |
| -------- | ------ | ------------------- | ---------------- | ------------------------- | -------------------- | ------------------- | --------------------- | --------------------- | ------------ |
| Matrix   | x      | x                   | x                | x                         | x                    | x                   | x                     | x                     |              |
| Telegram | x      |                     |                  |                           |                      |                     |                       |                       | x            |

Questo mantiene `qa-channel` come ampia suite di comportamento del prodotto, mentre Matrix,
Telegram e i futuri trasporti live condividono una checklist esplicita del contratto di trasporto.

Per un lane VM Linux temporaneo senza introdurre Docker nel percorso QA, esegui:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Questo avvia un guest Multipass nuovo, installa le dipendenze, compila OpenClaw
all'interno del guest, esegue `qa suite`, quindi copia il normale report QA e il
riepilogo di nuovo in `.artifacts/qa-e2e/...` sull'host.
Riutilizza lo stesso comportamento di selezione degli scenari di `qa suite` sull'host.
Le esecuzioni della suite su host e Multipass eseguono in parallelo per impostazione predefinita
più scenari selezionati con worker Gateway isolati, fino a 64 worker o al numero di
scenari selezionati. Usa `--concurrency <count>` per regolare il numero di worker, oppure
`--concurrency 1` per l'esecuzione seriale.
Le esecuzioni live inoltrano gli input di autenticazione QA supportati che sono pratici per il
guest: chiavi provider basate su env, il percorso di configurazione del provider live QA e
`CODEX_HOME` quando presente. Mantieni `--output-dir` sotto la root del repository così che il guest
possa scrivere indietro tramite il workspace montato.

## Seed supportati dal repository

Gli asset seed si trovano in `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Questi sono intenzionalmente in git in modo che il piano QA sia visibile sia agli esseri umani sia
all'agente.

`qa-lab` dovrebbe rimanere un runner Markdown generico. Ogni file Markdown di scenario è
la fonte di verità per una singola esecuzione di test e dovrebbe definire:

- metadati dello scenario
- riferimenti a documentazione e codice
- requisiti opzionali dei Plugin
- patch opzionale di configurazione del Gateway
- il `qa-flow` eseguibile

La superficie runtime riutilizzabile che supporta `qa-flow` può restare generica
e trasversale. Per esempio, gli scenari Markdown possono combinare helper lato
trasporto con helper lato browser che guidano la Control UI incorporata tramite la
seam `browser.request` del Gateway senza aggiungere un runner con casi speciali.

L'elenco di base dovrebbe restare sufficientemente ampio da coprire:

- chat DM e di canale
- comportamento dei thread
- ciclo di vita delle azioni sui messaggi
- callback Cron
- richiamo della memoria
- cambio modello
- handoff a subagent
- lettura del repository e della documentazione
- una piccola attività di build come Lobster Invaders

## Lane mock del provider

`qa suite` ha due lane mock locali del provider:

- `mock-openai` è il mock OpenClaw consapevole dello scenario. Rimane il
  lane mock deterministico predefinito per la QA supportata dal repository e i gate di parità.
- `aimock` avvia un server provider supportato da AIMock per copertura sperimentale di protocollo,
  fixture, record/replay e chaos. È aggiuntivo e non sostituisce il dispatcher di scenari
  `mock-openai`.

L'implementazione dei lane del provider si trova in `extensions/qa-lab/src/providers/`.
Ogni provider gestisce i propri valori predefiniti, l'avvio del server locale, la configurazione
del modello Gateway, le esigenze di staging del profilo auth e i flag di capacità live/mock. Il codice
condiviso di suite e Gateway dovrebbe instradare tramite il registro dei provider invece di fare branching
sui nomi dei provider.

## Adattatori di trasporto

`qa-lab` gestisce una seam di trasporto generica per gli scenari QA Markdown.
`qa-channel` è il primo adattatore su questa seam, ma l'obiettivo di progettazione è più ampio:
canali futuri, reali o sintetici, dovrebbero integrarsi nello stesso runner della suite
invece di aggiungere un runner QA specifico per il trasporto.

A livello architetturale, la suddivisione è:

- `qa-lab` gestisce l'esecuzione generica degli scenari, la concorrenza dei worker, la scrittura degli artifact e il reporting.
- l'adattatore di trasporto gestisce la configurazione del Gateway, la readiness, l'osservazione in ingresso e in uscita, le azioni di trasporto e lo stato di trasporto normalizzato.
- i file di scenario Markdown sotto `qa/scenarios/` definiscono l'esecuzione del test; `qa-lab` fornisce la superficie runtime riutilizzabile che li esegue.

Le linee guida di adozione rivolte ai maintainer per i nuovi adattatori di canale si trovano in
[Testing](/it/help/testing#adding-a-channel-to-qa).

## Reporting

`qa-lab` esporta un report di protocollo in Markdown dalla timeline del bus osservata.
Il report dovrebbe rispondere a:

- Che cosa ha funzionato
- Che cosa è fallito
- Che cosa è rimasto bloccato
- Quali scenari di follow-up vale la pena aggiungere

Per i controlli di carattere e stile, esegui lo stesso scenario su più ref di modelli live
e scrivi un report Markdown valutato:

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

Il comando esegue processi figli locali del Gateway QA, non Docker. Gli scenari di
valutazione del carattere dovrebbero impostare la persona tramite `SOUL.md`, quindi eseguire normali turni
utente come chat, aiuto sul workspace e piccole attività sui file. Al modello candidato
non dovrebbe essere detto che è in fase di valutazione. Il comando conserva ogni
trascrizione completa, registra statistiche di esecuzione di base, quindi chiede ai modelli giudice in modalità fast con
ragionamento `xhigh` di classificare le esecuzioni per naturalezza, vibe e umorismo.
Usa `--blind-judge-models` quando confronti provider: il prompt del giudice riceve comunque
ogni trascrizione e stato di esecuzione, ma i ref candidati vengono sostituiti con etichette neutre
come `candidate-01`; il report rimappa le classifiche ai ref reali dopo il parsing.
Le esecuzioni candidate usano per impostazione predefinita thinking `high`, con `xhigh` per i modelli OpenAI che
lo supportano. Sostituisci un candidato specifico inline con
`--model provider/model,thinking=<level>`. `--thinking <level>` imposta comunque un fallback
globale, e la forma precedente `--model-thinking <provider/model=level>` viene
mantenuta per compatibilità.
I ref candidati OpenAI usano per impostazione predefinita la modalità fast così da sfruttare l'elaborazione prioritaria dove
il provider la supporta. Aggiungi `,fast`, `,no-fast` o `,fast=false` inline quando un
singolo candidato o giudice ha bisogno di un override. Passa `--fast` solo quando vuoi
forzare la modalità fast per ogni modello candidato. Le durate di candidati e giudici vengono
registrate nel report per l'analisi benchmark, ma i prompt dei giudici indicano esplicitamente di
non classificare in base alla velocità.
Le esecuzioni dei modelli candidati e giudici usano entrambe per impostazione predefinita una concorrenza di 16.
Riduci `--concurrency` o `--judge-concurrency` quando i limiti del provider o la pressione sul Gateway locale
rendono un'esecuzione troppo rumorosa.
Quando non viene passato alcun candidato `--model`, la valutazione del carattere usa per impostazione predefinita
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` e
`google/gemini-3.1-pro-preview` quando non viene passato alcun `--model`.
Quando non viene passato alcun `--judge-model`, i giudici usano per impostazione predefinita
`openai/gpt-5.4,thinking=xhigh,fast` e
`anthropic/claude-opus-4-6,thinking=high`.

## Documentazione correlata

- [Testing](/it/help/testing)
- [QA Channel](/it/channels/qa-channel)
- [Dashboard](/web/dashboard)
