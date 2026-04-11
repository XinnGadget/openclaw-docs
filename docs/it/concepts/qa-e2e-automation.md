---
read_when:
    - Estensione di qa-lab o qa-channel
    - Aggiunta di scenari QA supportati dal repository
    - Creazione di un'automazione QA a maggiore realismo attorno alla dashboard del Gateway
summary: Forma dell'automazione QA privata per qa-lab, qa-channel, scenari con seed e report del protocollo
title: Automazione QA E2E
x-i18n:
    generated_at: "2026-04-11T02:44:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5427b505e26bfd542e984e3920c3f7cb825473959195ba9737eff5da944c60d0
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automazione QA E2E

Lo stack QA privato è pensato per testare OpenClaw in un modo più realistico,
modellato sui canali, rispetto a quanto possa fare un singolo test unitario.

Componenti attuali:

- `extensions/qa-channel`: canale di messaggi sintetico con superfici per DM, canale, thread,
  reazione, modifica ed eliminazione.
- `extensions/qa-lab`: interfaccia utente di debug e bus QA per osservare la trascrizione,
  iniettare messaggi in ingresso ed esportare un report Markdown.
- `qa/`: asset seed supportati dal repository per il task iniziale e gli
  scenari QA di base.

L'attuale flusso operativo QA è un sito QA a due pannelli:

- Sinistra: dashboard del Gateway (Control UI) con l'agente.
- Destra: QA Lab, che mostra la trascrizione in stile Slack e il piano dello scenario.

Eseguilo con:

```bash
pnpm qa:lab:up
```

Questo compila il sito QA, avvia la corsia del gateway supportata da Docker ed espone la
pagina QA Lab dove un operatore o un loop di automazione può assegnare all'agente una
missione QA, osservare il comportamento reale del canale e registrare ciò che ha funzionato,
ciò che è fallito o ciò che è rimasto bloccato.

Per iterare più velocemente sull'interfaccia utente di QA Lab senza ricompilare ogni volta l'immagine Docker,
avvia lo stack con un bundle QA Lab montato tramite bind:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` mantiene i servizi Docker su un'immagine precompilata e monta tramite bind
`extensions/qa-lab/web/dist` nel container `qa-lab`. `qa:lab:watch`
ricompila quel bundle quando cambia, e il browser si ricarica automaticamente quando cambia l'hash
degli asset di QA Lab.

Per una corsia smoke Matrix con trasporto reale, esegui:

```bash
pnpm openclaw qa matrix
```

Questa corsia effettua il provisioning di un homeserver Tuwunel usa e getta in Docker, registra
utenti temporanei driver, SUT e observer, crea una stanza privata, quindi esegue
il plugin Matrix reale all'interno di un processo figlio del gateway QA. La corsia con trasporto live
mantiene la configurazione del processo figlio limitata al trasporto in test, quindi Matrix viene eseguito senza
`qa-channel` nella configurazione del processo figlio.

Per una corsia smoke Telegram con trasporto reale, esegui:

```bash
pnpm openclaw qa telegram
```

Questa corsia usa come target un vero gruppo Telegram privato invece di effettuare il provisioning di un
server usa e getta. Richiede `OPENCLAW_QA_TELEGRAM_GROUP_ID`,
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` e
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`, oltre a due bot distinti nello stesso
gruppo privato. Il bot SUT deve avere un nome utente Telegram, e l'osservazione
bot-to-bot funziona al meglio quando entrambi i bot hanno abilitata la Modalità di comunicazione bot-to-bot
in `@BotFather`.

Le corsie di trasporto live ora condividono un contratto più piccolo invece di inventare
ognuna la propria forma di elenco degli scenari:

`qa-channel` resta la suite ampia del comportamento del prodotto sintetico e non fa parte
della matrice di copertura del trasporto live.

| Corsia   | Canary | Gate dei mention | Blocco allowlist | Risposta di primo livello | Ripresa dopo riavvio | Follow-up nel thread | Isolamento del thread | Osservazione delle reazioni | Comando help |
| -------- | ------ | ---------------- | ---------------- | ------------------------- | -------------------- | -------------------- | -------------------- | --------------------------- | ------------ |
| Matrix   | x      | x                | x                | x                         | x                    | x                    | x                    | x                           |              |
| Telegram | x      |                  |                  |                          |                      |                      |                      |                             | x            |

Questo mantiene `qa-channel` come suite ampia del comportamento del prodotto, mentre Matrix,
Telegram e i futuri trasporti live condividono una checklist esplicita del contratto di trasporto.

Per una corsia VM Linux usa e getta senza introdurre Docker nel percorso QA, esegui:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Questo avvia un guest Multipass nuovo, installa le dipendenze, compila OpenClaw
all'interno del guest, esegue `qa suite`, quindi copia il normale report QA e il
riepilogo in `.artifacts/qa-e2e/...` sull'host.
Riutilizza lo stesso comportamento di selezione degli scenari di `qa suite` sull'host.
Le esecuzioni della suite su host e Multipass eseguono per impostazione predefinita più scenari selezionati in parallelo
con worker del gateway isolati, fino a 64 worker o al numero di scenari selezionati. Usa
`--concurrency <count>` per regolare il numero di worker, oppure
`--concurrency 1` per l'esecuzione seriale.
Le esecuzioni live inoltrano gli input di autenticazione QA supportati che sono pratici per il
guest: chiavi del provider basate su env, il percorso di configurazione del provider live QA e
`CODEX_HOME` quando presente. Mantieni `--output-dir` sotto la root del repository affinché il guest
possa scrivere indietro attraverso il workspace montato.

## Seed supportati dal repository

Gli asset seed si trovano in `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Sono intenzionalmente in git affinché il piano QA sia visibile sia agli esseri umani sia
all'agente. L'elenco di base dovrebbe restare sufficientemente ampio da coprire:

- chat DM e di canale
- comportamento dei thread
- ciclo di vita delle azioni sui messaggi
- callback cron
- richiamo della memoria
- cambio di modello
- handoff a un subagente
- lettura del repository e della documentazione
- un piccolo task di build come Lobster Invaders

## Reportistica

`qa-lab` esporta un report Markdown del protocollo a partire dalla timeline del bus osservato.
Il report dovrebbe rispondere a:

- Cosa ha funzionato
- Cosa è fallito
- Cosa è rimasto bloccato
- Quali scenari di follow-up vale la pena aggiungere

Per controlli di carattere e stile, esegui lo stesso scenario su più riferimenti di modelli live
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

Il comando esegue processi figli locali del gateway QA, non Docker. Gli scenari di valutazione del carattere
dovrebbero impostare la persona tramite `SOUL.md`, quindi eseguire normali turni utente
come chat, aiuto sul workspace e piccoli task sui file. Al modello candidato
non dovrebbe essere detto che è sotto valutazione. Il comando preserva ogni trascrizione completa,
registra statistiche di esecuzione di base, quindi chiede ai modelli giudice in modalità fast con
ragionamento `xhigh` di classificare le esecuzioni per naturalezza, vibe e umorismo.
Usa `--blind-judge-models` quando confronti provider: il prompt per il giudice riceve comunque
ogni trascrizione e stato di esecuzione, ma i riferimenti dei candidati vengono sostituiti con etichette
neutre come `candidate-01`; il report rimappa le classifiche ai riferimenti reali dopo
il parsing.
Le esecuzioni dei candidati usano per impostazione predefinita il thinking `high`, con `xhigh` per i modelli OpenAI che
lo supportano. Sostituisci un candidato specifico inline con
`--model provider/model,thinking=<level>`. `--thinking <level>` imposta comunque un
fallback globale, e la forma precedente `--model-thinking <provider/model=level>` viene
mantenuta per compatibilità.
I riferimenti candidati OpenAI usano per impostazione predefinita la modalità fast così che venga usata
l'elaborazione prioritaria dove il provider la supporta. Aggiungi `,fast`, `,no-fast` o `,fast=false` inline quando
un singolo candidato o giudice necessita di una sostituzione. Passa `--fast` solo quando vuoi
forzare la modalità fast per ogni modello candidato. Le durate di candidati e giudici vengono
registrate nel report per l'analisi comparativa, ma i prompt dei giudici dicono esplicitamente
di non classificare in base alla velocità.
Le esecuzioni dei modelli candidati e giudici usano entrambe per impostazione predefinita una concorrenza di 16.
Riduci `--concurrency` o `--judge-concurrency` quando i limiti del provider o la pressione sul gateway locale
rendono un'esecuzione troppo rumorosa.
Quando non viene passato alcun candidato `--model`, la valutazione del carattere usa per impostazione predefinita
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` e
`google/gemini-3.1-pro-preview` quando non viene passato alcun `--model`.
Quando non viene passato alcun `--judge-model`, i giudici usano per impostazione predefinita
`openai/gpt-5.4,thinking=xhigh,fast` e
`anthropic/claude-opus-4-6,thinking=high`.

## Documenti correlati

- [Testing](/it/help/testing)
- [QA Channel](/it/channels/qa-channel)
- [Dashboard](/web/dashboard)
