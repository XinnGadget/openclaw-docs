---
read_when:
    - Stai creando o facendo debug di plugin OpenClaw nativi
    - Vuoi comprendere il modello di capacità dei plugin o i confini di proprietà
    - Stai lavorando sulla pipeline di caricamento o sul registry dei plugin
    - Stai implementando hook runtime dei provider o plugin di canale
sidebarTitle: Internals
summary: 'Dettagli interni dei plugin: modello di capacità, proprietà, contratti, pipeline di caricamento e helper runtime'
title: Dettagli interni dei plugin
x-i18n:
    generated_at: "2026-04-08T02:19:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: c40ecf14e2a0b2b8d332027aed939cd61fb4289a489f4cd4c076c96d707d1138
    source_path: plugins/architecture.md
    workflow: 15
---

# Dettagli interni dei plugin

<Info>
  Questo è il **riferimento architetturale approfondito**. Per guide pratiche, vedi:
  - [Installare e usare i plugin](/it/tools/plugin) — guida per l'utente
  - [Per iniziare](/it/plugins/building-plugins) — primo tutorial sui plugin
  - [Plugin di canale](/it/plugins/sdk-channel-plugins) — creare un canale di messaggistica
  - [Plugin provider](/it/plugins/sdk-provider-plugins) — creare un provider di modelli
  - [Panoramica SDK](/it/plugins/sdk-overview) — mappa di importazione e API di registrazione
</Info>

Questa pagina copre l'architettura interna del sistema di plugin di OpenClaw.

## Modello pubblico delle capacità

Le capacità sono il modello pubblico dei **plugin nativi** all'interno di OpenClaw. Ogni
plugin OpenClaw nativo si registra rispetto a uno o più tipi di capacità:

| Capacità              | Metodo di registrazione                           | Plugin di esempio                    |
| --------------------- | ------------------------------------------------- | ------------------------------------ |
| Inferenza testuale    | `api.registerProvider(...)`                       | `openai`, `anthropic`                |
| Backend di inferenza CLI | `api.registerCliBackend(...)`                  | `openai`, `anthropic`                |
| Voce                  | `api.registerSpeechProvider(...)`                 | `elevenlabs`, `microsoft`            |
| Trascrizione realtime | `api.registerRealtimeTranscriptionProvider(...)`  | `openai`                             |
| Voce realtime         | `api.registerRealtimeVoiceProvider(...)`          | `openai`                             |
| Comprensione dei media | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| Generazione di immagini | `api.registerImageGenerationProvider(...)`      | `openai`, `google`, `fal`, `minimax` |
| Generazione musicale  | `api.registerMusicGenerationProvider(...)`        | `google`, `minimax`                  |
| Generazione video     | `api.registerVideoGenerationProvider(...)`        | `qwen`                               |
| Recupero web          | `api.registerWebFetchProvider(...)`               | `firecrawl`                          |
| Ricerca web           | `api.registerWebSearchProvider(...)`              | `google`                             |
| Canale / messaggistica | `api.registerChannel(...)`                       | `msteams`, `matrix`                  |

Un plugin che registra zero capacità ma fornisce hook, strumenti o
servizi è un plugin **legacy solo hook**. Questo pattern è ancora pienamente supportato.

### Posizione sulla compatibilità esterna

Il modello di capacità è integrato nel core e viene usato oggi dai plugin
inclusi/nativi, ma la compatibilità dei plugin esterni richiede ancora una soglia più rigorosa di “è
esportato, quindi è congelato”.

Indicazioni attuali:

- **plugin esterni esistenti:** mantenere funzionanti le integrazioni basate su hook; considerare
  questo come baseline di compatibilità
- **nuovi plugin inclusi/nativi:** preferire la registrazione esplicita delle capacità rispetto a
  accessi specifici del vendor o nuovi design solo hook
- **plugin esterni che adottano la registrazione delle capacità:** consentito, ma trattare
  le superfici helper specifiche per capacità come in evoluzione, a meno che la documentazione non indichi esplicitamente
  che un contratto è stabile

Regola pratica:

- le API di registrazione delle capacità sono la direzione prevista
- gli hook legacy restano il percorso più sicuro per evitare rotture nei plugin esterni durante
  la transizione
- i sottopercorsi helper esportati non sono tutti uguali; preferire il contratto
  ristretto documentato, non esportazioni helper accidentali

### Forme dei plugin

OpenClaw classifica ogni plugin caricato in una forma in base al suo effettivo
comportamento di registrazione (non solo ai metadati statici):

- **plain-capability** -- registra esattamente un tipo di capacità (ad esempio un
  plugin solo provider come `mistral`)
- **hybrid-capability** -- registra più tipi di capacità (ad esempio
  `openai` possiede inferenza testuale, voce, comprensione dei media e generazione
  di immagini)
- **hook-only** -- registra solo hook (tipizzati o custom), nessuna capacità,
  strumento, comando o servizio
- **non-capability** -- registra strumenti, comandi, servizi o route ma nessuna
  capacità

Usa `openclaw plugins inspect <id>` per vedere la forma di un plugin e il dettaglio
delle capacità. Vedi [riferimento CLI](/cli/plugins#inspect) per i dettagli.

### Hook legacy

L'hook `before_agent_start` resta supportato come percorso di compatibilità per
i plugin solo hook. I plugin legacy reali dipendono ancora da esso.

Direzione:

- mantenerlo funzionante
- documentarlo come legacy
- preferire `before_model_resolve` per il lavoro di override modello/provider
- preferire `before_prompt_build` per il lavoro di mutazione del prompt
- rimuoverlo solo dopo che l'uso reale cala e la copertura delle fixture dimostra la sicurezza della migrazione

### Segnali di compatibilità

Quando esegui `openclaw doctor` o `openclaw plugins inspect <id>`, potresti vedere
una di queste etichette:

| Segnale                   | Significato                                                 |
| ------------------------- | ----------------------------------------------------------- |
| **config valid**          | La configurazione viene analizzata correttamente e i plugin si risolvono |
| **compatibility advisory** | Il plugin usa un pattern supportato ma più vecchio (ad es. `hook-only`) |
| **legacy warning**        | Il plugin usa `before_agent_start`, che è deprecato         |
| **hard error**            | La configurazione non è valida o il plugin non è stato caricato |

Né `hook-only` né `before_agent_start` romperanno il tuo plugin oggi --
`hook-only` è solo indicativo, e `before_agent_start` genera solo un avviso. Questi
segnali compaiono anche in `openclaw status --all` e `openclaw plugins doctor`.

## Panoramica dell'architettura

Il sistema di plugin di OpenClaw ha quattro livelli:

1. **Manifest + discovery**
   OpenClaw trova i plugin candidati dai percorsi configurati, dalle root workspace,
   dalle root globali delle estensioni e dalle estensioni incluse. La discovery legge prima i
   manifest nativi `openclaw.plugin.json` e i manifest bundle supportati.
2. **Abilitazione + validazione**
   Il core decide se un plugin scoperto è abilitato, disabilitato, bloccato o
   selezionato per uno slot esclusivo come la memoria.
3. **Caricamento runtime**
   I plugin OpenClaw nativi vengono caricati in-process tramite jiti e registrano
   capacità in un registry centrale. I bundle compatibili vengono normalizzati in
   record del registry senza importare codice runtime.
4. **Consumo della superficie**
   Il resto di OpenClaw legge il registry per esporre strumenti, canali, setup
   provider, hook, route HTTP, comandi CLI e servizi.

Per la CLI dei plugin in particolare, la discovery del comando root è divisa in due fasi:

- i metadati in fase di parsing provengono da `registerCli(..., { descriptors: [...] })`
- il vero modulo CLI del plugin può restare lazy e registrarsi alla prima invocazione

Questo mantiene il codice CLI di proprietà del plugin all'interno del plugin, consentendo comunque a OpenClaw
di riservare i nomi dei comandi root prima del parsing.

Il confine di progettazione importante:

- la discovery + validazione della configurazione dovrebbe funzionare da **metadati manifest/schema**
  senza eseguire il codice del plugin
- il comportamento runtime nativo deriva dal percorso `register(api)` del modulo plugin

Questa separazione consente a OpenClaw di validare la configurazione, spiegare i plugin mancanti/disabilitati e
costruire suggerimenti UI/schema prima che il runtime completo sia attivo.

### Plugin di canale e strumento messaggio condiviso

I plugin di canale non devono registrare uno strumento separato di invio/modifica/reazione per
le normali azioni di chat. OpenClaw mantiene nel core un unico strumento `message` condiviso, e
i plugin di canale possiedono la discovery e l'esecuzione specifiche del canale dietro di esso.

Il confine attuale è:

- il core possiede l'host dello strumento `message` condiviso, il wiring del prompt, la
  gestione della sessione/thread e il dispatch di esecuzione
- i plugin di canale possiedono la discovery delle azioni con scope, la discovery delle
  capacità e qualsiasi frammento di schema specifico del canale
- i plugin di canale possiedono la grammatica della conversazione di sessione specifica del provider, ad esempio
  come gli id conversazione codificano gli id thread o ereditano dalle conversazioni padre
- i plugin di canale eseguono l'azione finale tramite il loro adapter di azione

Per i plugin di canale, la superficie SDK è
`ChannelMessageActionAdapter.describeMessageTool(...)`. Questa chiamata di discovery unificata consente a un plugin di restituire insieme azioni visibili, capacità e contributi allo schema,
così queste parti non divergono.

Il core passa lo scope runtime in questo passaggio di discovery. I campi importanti includono:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- `requesterSenderId` trusted in ingresso

Questo conta per i plugin sensibili al contesto. Un canale può nascondere o esporre
azioni di messaggio in base all'account attivo, alla stanza/thread/messaggio corrente o
all'identità trusted del richiedente senza hardcodare branch specifici del canale nello
strumento `message` del core.

Per questo i cambiamenti di routing dell'embedded runner restano lavoro del plugin: il runner è
responsabile di inoltrare l'identità corrente di chat/sessione al confine di discovery del plugin
così lo strumento `message` condiviso espone la superficie corretta di proprietà del canale
per il turno corrente.

Per gli helper di esecuzione di proprietà del canale, i plugin inclusi dovrebbero mantenere il runtime di esecuzione
all'interno dei propri moduli di estensione. Il core non possiede più i
runtime delle azioni messaggio per Discord, Slack, Telegram o WhatsApp sotto `src/agents/tools`.
Non pubblichiamo sottopercorsi separati `plugin-sdk/*-action-runtime`, e i plugin inclusi
dovrebbero importare direttamente il proprio codice runtime locale dai loro
moduli di estensione.

Lo stesso confine si applica in generale ai punti di giunzione SDK con nome provider: il core non
dovrebbe importare barrel di convenienza specifici del canale per Slack, Discord, Signal,
WhatsApp o estensioni simili. Se il core ha bisogno di un comportamento, dovrebbe
consumare il barrel `api.ts` / `runtime-api.ts` del plugin incluso o promuovere l'esigenza
a una capacità generica e ristretta nello SDK condiviso.

Per i sondaggi in particolare, ci sono due percorsi di esecuzione:

- `outbound.sendPoll` è la baseline condivisa per i canali che rientrano nel modello comune
  di sondaggio
- `actions.handleAction("poll")` è il percorso preferito per semantiche di sondaggio specifiche del canale o parametri di sondaggio aggiuntivi

Il core ora rimanda il parsing condiviso dei sondaggi a dopo che il dispatch del sondaggio del plugin ha rifiutato
l'azione, così i gestori dei sondaggi di proprietà del plugin possono accettare campi specifici
del canale senza essere bloccati prima dal parser generico dei sondaggi.

Vedi [Pipeline di caricamento](#load-pipeline) per la sequenza completa di avvio.

## Modello di proprietà delle capacità

OpenClaw tratta un plugin nativo come confine di proprietà per una **azienda** o una
**funzionalità**, non come un contenitore di integrazioni scollegate.

Questo significa:

- un plugin aziendale dovrebbe di solito possedere tutte le superfici OpenClaw-facing di quella azienda
- un plugin funzionalità dovrebbe di solito possedere l'intera superficie della funzionalità che introduce
- i canali dovrebbero consumare capacità condivise del core invece di reimplementare
  comportamento del provider in modo ad hoc

Esempi:

- il plugin incluso `openai` possiede il comportamento del model provider OpenAI e il comportamento OpenAI
  per voce + realtime-voice + comprensione dei media + generazione di immagini
- il plugin incluso `elevenlabs` possiede il comportamento speech ElevenLabs
- il plugin incluso `microsoft` possiede il comportamento speech Microsoft
- il plugin incluso `google` possiede il comportamento del model provider Google più
  il comportamento Google per comprensione dei media + generazione di immagini + ricerca web
- il plugin incluso `firecrawl` possiede il comportamento web-fetch Firecrawl
- i plugin inclusi `minimax`, `mistral`, `moonshot` e `zai` possiedono i loro
  backend di comprensione dei media
- il plugin incluso `qwen` possiede il comportamento text-provider Qwen più
  il comportamento per comprensione dei media e generazione video
- il plugin `voice-call` è un plugin funzionalità: possiede trasporto chiamate, strumenti,
  CLI, route e bridging Twilio media-stream, ma consuma capacità speech condivise
  più realtime-transcription e realtime-voice invece di importare direttamente plugin vendor

Lo stato finale previsto è:

- OpenAI vive in un solo plugin anche se comprende modelli testuali, voce, immagini e
  video futuri
- un altro vendor può fare lo stesso per la propria area
- i canali non si preoccupano di quale plugin vendor possieda il provider; consumano il
  contratto di capacità condivisa esposto dal core

Questa è la distinzione chiave:

- **plugin** = confine di proprietà
- **capacità** = contratto del core che più plugin possono implementare o consumare

Quindi se OpenClaw aggiunge un nuovo dominio come il video, la prima domanda non è
“quale provider dovrebbe hardcodare la gestione video?” La prima domanda è “qual è
il contratto di capacità video del core?” Una volta che quel contratto esiste, i plugin vendor
possono registrarsi rispetto a esso e i plugin canale/funzionalità possono consumarlo.

Se la capacità non esiste ancora, di solito la mossa giusta è:

1. definire la capacità mancante nel core
2. esporla tramite l'API/plugin runtime in modo tipizzato
3. collegare canali/funzionalità a quella capacità
4. lasciare che i plugin vendor registrino implementazioni

Questo mantiene la proprietà esplicita evitando al tempo stesso comportamento del core che dipende da
un singolo vendor o da un percorso di codice specifico di un plugin una tantum.

### Stratificazione delle capacità

Usa questo modello mentale quando decidi dove deve stare il codice:

- **livello di capacità del core**: orchestrazione condivisa, policy, fallback, configurazione
  regole di merge, semantica di consegna e contratti tipizzati
- **livello plugin vendor**: API specifiche del vendor, auth, cataloghi modelli, sintesi vocale,
  generazione di immagini, backend video futuri, endpoint di utilizzo
- **livello plugin canale/funzionalità**: integrazione Slack/Discord/voice-call/ecc.
  che consuma capacità del core e le presenta su una superficie

Per esempio, la TTS segue questa forma:

- il core possiede policy TTS al momento della risposta, ordine di fallback, preferenze e consegna sul canale
- `openai`, `elevenlabs` e `microsoft` possiedono le implementazioni di sintesi
- `voice-call` consuma l'helper runtime TTS per telefonia

Lo stesso pattern dovrebbe essere preferito per capacità future.

### Esempio di plugin aziendale multi-capacità

Un plugin aziendale dovrebbe apparire coeso dall'esterno. Se OpenClaw ha contratti condivisi
per modelli, voce, trascrizione realtime, voce realtime, comprensione dei media,
generazione di immagini, generazione video, recupero web e ricerca web,
un vendor può possedere tutte le sue superfici in un unico posto:

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

Ciò che conta non sono i nomi esatti degli helper. Conta la forma:

- un plugin possiede la superficie del vendor
- il core continua a possedere i contratti di capacità
- i plugin canale e funzionalità consumano helper `api.runtime.*`, non codice vendor
- i test di contratto possono verificare che il plugin abbia registrato le capacità che
  dichiara di possedere

### Esempio di capacità: comprensione video

OpenClaw tratta già la comprensione di immagini/audio/video come una singola
capacità condivisa. Lo stesso modello di proprietà si applica anche qui:

1. il core definisce il contratto di comprensione dei media
2. i plugin vendor registrano `describeImage`, `transcribeAudio` e
   `describeVideo` a seconda dei casi
3. i plugin canale e funzionalità consumano il comportamento condiviso del core invece di
   collegarsi direttamente al codice vendor

Questo evita di incorporare nel core le assunzioni video di un singolo provider. Il plugin possiede
la superficie del vendor; il core possiede il contratto di capacità e il comportamento di fallback.

La generazione video segue già la stessa sequenza: il core possiede il contratto di
capacità tipizzato e l'helper runtime, e i plugin vendor registrano
implementazioni `api.registerVideoGenerationProvider(...)` rispetto ad esso.

Hai bisogno di una checklist concreta di rollout? Vedi
[Capability Cookbook](/it/plugins/architecture).

## Contratti e enforcement

La superficie API del plugin è intenzionalmente tipizzata e centralizzata in
`OpenClawPluginApi`. Questo contratto definisce i punti di registrazione supportati e
gli helper runtime su cui un plugin può fare affidamento.

Perché è importante:

- gli autori dei plugin ottengono un unico standard interno stabile
- il core può rifiutare proprietà duplicate, come due plugin che registrano lo stesso
  id provider
- l'avvio può mostrare diagnostica utile per registrazioni malformate
- i test di contratto possono imporre la proprietà dei plugin inclusi e prevenire derive silenziose

Ci sono due livelli di enforcement:

1. **enforcement della registrazione runtime**
   Il registry dei plugin valida le registrazioni mentre i plugin si caricano. Esempi:
   id provider duplicati, id speech provider duplicati e registrazioni
   malformate producono diagnostica dei plugin invece di comportamento indefinito.
2. **test di contratto**
   I plugin inclusi vengono acquisiti nei registry di contratto durante i test così
   OpenClaw può verificare esplicitamente la proprietà. Oggi questo viene usato per
   model provider, speech provider, web search provider e proprietà della registrazione inclusa.

L'effetto pratico è che OpenClaw sa in anticipo quale plugin possiede quale
superficie. Questo consente al core e ai canali di comporsi in modo fluido perché la
proprietà è dichiarata, tipizzata e testabile invece che implicita.

### Cosa appartiene a un contratto

I buoni contratti plugin sono:

- tipizzati
- piccoli
- specifici per capacità
- di proprietà del core
- riutilizzabili da più plugin
- consumabili da canali/funzionalità senza conoscenza del vendor

I cattivi contratti plugin sono:

- policy specifica del vendor nascosta nel core
- scappatoie una tantum del plugin che bypassano il registry
- codice del canale che accede direttamente a una implementazione vendor
- oggetti runtime ad hoc che non fanno parte di `OpenClawPluginApi` o
  `api.runtime`

In caso di dubbio, alza il livello di astrazione: definisci prima la capacità, poi
consenti ai plugin di collegarsi ad essa.

## Modello di esecuzione

I plugin OpenClaw nativi vengono eseguiti **in-process** con il Gateway. Non sono
sandboxed. Un plugin nativo caricato ha lo stesso confine di trust a livello di processo del codice core.

Implicazioni:

- un plugin nativo può registrare strumenti, gestori di rete, hook e servizi
- un bug in un plugin nativo può mandare in crash o destabilizzare il gateway
- un plugin nativo malevolo equivale a esecuzione arbitraria di codice all'interno
  del processo OpenClaw

I bundle compatibili sono più sicuri per impostazione predefinita perché OpenClaw attualmente li tratta
come pacchetti di metadati/contenuti. Nelle release attuali, questo significa soprattutto
Skills inclusi.

Usa allowlist e percorsi espliciti di installazione/caricamento per i plugin non inclusi. Tratta
i plugin workspace come codice di sviluppo, non come impostazioni predefinite di produzione.

Per i nomi dei package workspace inclusi, mantieni l'id del plugin ancorato nel nome npm:
`@openclaw/<id>` per impostazione predefinita, oppure un suffisso tipizzato approvato come
`-provider`, `-plugin`, `-speech`, `-sandbox` o `-media-understanding` quando
il package espone intenzionalmente un ruolo plugin più ristretto.

Nota importante sul trust:

- `plugins.allow` considera trusted gli **id dei plugin**, non la provenienza della sorgente.
- Un plugin workspace con lo stesso id di un plugin incluso oscura intenzionalmente
  la copia inclusa quando quel plugin workspace è abilitato/in allowlist.
- Questo è normale e utile per sviluppo locale, test di patch e hotfix.

## Confine delle esportazioni

OpenClaw esporta capacità, non comodità di implementazione.

Mantieni pubblica la registrazione delle capacità. Riduci le esportazioni helper non contrattuali:

- sottopercorsi helper specifici dei plugin inclusi
- sottopercorsi di plumbing runtime non pensati come API pubblica
- helper di convenienza specifici del vendor
- helper di setup/onboarding che sono dettagli di implementazione

Alcuni sottopercorsi helper dei plugin inclusi restano ancora nella mappa di esportazione SDK generata
per compatibilità e manutenzione dei plugin inclusi. Esempi attuali includono
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` e diversi punti di giunzione `plugin-sdk/matrix*`. Trattali come
esportazioni riservate di dettaglio implementativo, non come pattern SDK consigliato per
nuovi plugin terzi.

## Pipeline di caricamento

All'avvio, OpenClaw fa all'incirca questo:

1. scopre le root dei plugin candidati
2. legge manifest nativi o compatibili e metadati del package
3. rifiuta candidati non sicuri
4. normalizza la configurazione dei plugin (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. decide l'abilitazione per ogni candidato
6. carica i moduli nativi abilitati tramite jiti
7. chiama gli hook nativi `register(api)` (o `activate(api)` — alias legacy) e raccoglie le registrazioni nel registry dei plugin
8. espone il registry alle superfici dei comandi/runtime

<Note>
`activate` è un alias legacy di `register` — il loader risolve quale dei due è presente (`def.register ?? def.activate`) e lo chiama nello stesso punto. Tutti i plugin inclusi usano `register`; preferisci `register` per i nuovi plugin.
</Note>

I controlli di sicurezza avvengono **prima** dell'esecuzione runtime. I candidati vengono bloccati
quando l'entry esce dalla root del plugin, il percorso è scrivibile da tutti o la proprietà del percorso appare sospetta per plugin non inclusi.

### Comportamento manifest-first

Il manifest è la fonte di verità del control-plane. OpenClaw lo usa per:

- identificare il plugin
- scoprire canali/Skills/schema di configurazione dichiarati o capacità del bundle
- validare `plugins.entries.<id>.config`
- arricchire etichette/segnaposto della Control UI
- mostrare metadati di installazione/catalogo

Per i plugin nativi, il modulo runtime è la parte data-plane. Registra
il comportamento effettivo come hook, strumenti, comandi o flussi provider.

### Cosa mette in cache il loader

OpenClaw mantiene brevi cache in-process per:

- risultati della discovery
- dati del registry dei manifest
- registry dei plugin caricati

Queste cache riducono l'overhead di avvio a raffica e dei comandi ripetuti. Sono sicure
da considerare come cache prestazionali di breve durata, non persistenza.

Nota sulle prestazioni:

- Imposta `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` oppure
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` per disabilitare queste cache.
- Regola le finestre di cache con `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` e
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Modello del registry

I plugin caricati non modificano direttamente globali casuali del core. Si registrano in un
registry centrale dei plugin.

Il registry tiene traccia di:

- record dei plugin (identità, sorgente, origine, stato, diagnostica)
- strumenti
- hook legacy e hook tipizzati
- canali
- provider
- gestori RPC del gateway
- route HTTP
- registrar CLI
- servizi in background
- comandi di proprietà del plugin

Le funzionalità del core leggono poi da quel registry invece di parlare direttamente
ai moduli plugin. Questo mantiene il caricamento unidirezionale:

- modulo plugin -> registrazione nel registry
- runtime del core -> consumo del registry

Questa separazione conta per la manutenibilità. Significa che la maggior parte delle superfici del core necessita solo di un punto di integrazione: “leggere il registry”, non “gestire casi speciali per ogni modulo plugin”.

## Callback di binding della conversazione

I plugin che legano una conversazione possono reagire quando un'approvazione viene risolta.

Usa `api.onConversationBindingResolved(...)` per ricevere una callback dopo che una richiesta di binding viene approvata o negata:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // A binding now exists for this plugin + conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // The request was denied; clear any local pending state.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Campi del payload della callback:

- `status`: `"approved"` o `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` o `"deny"`
- `binding`: il binding risolto per le richieste approvate
- `request`: il riepilogo della richiesta originale, suggerimento detach, id mittente e
  metadati della conversazione

Questa callback è solo di notifica. Non cambia chi è autorizzato a legare una
conversazione, e viene eseguita dopo il completamento della gestione di approvazione del core.

## Hook runtime del provider

I plugin provider ora hanno due livelli:

- metadati del manifest: `providerAuthEnvVars` per lookup economico di auth provider da env
  prima del caricamento runtime, `channelEnvVars` per lookup economico di env/setup del canale
  prima del caricamento runtime, più `providerAuthChoices` per etichette economiche
  di onboarding/scelta auth e metadati dei flag CLI prima del caricamento runtime
- hook a tempo di configurazione: `catalog` / legacy `discovery` più `applyConfigDefaults`
- hook runtime: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw continua a possedere il loop generico dell'agente, il failover, la gestione del transcript e
la policy degli strumenti. Questi hook sono la superficie di estensione per il comportamento specifico del provider senza
richiedere un intero trasporto di inferenza personalizzato.

Usa il manifest `providerAuthEnvVars` quando il provider ha credenziali basate su env
che i percorsi generici auth/status/model-picker devono vedere senza caricare il runtime del plugin.
Usa il manifest `providerAuthChoices` quando le superfici CLI di onboarding/scelta auth
devono conoscere l'id della scelta del provider, le etichette di gruppo e il semplice wiring auth
a flag singolo senza caricare il runtime del provider. Mantieni il runtime del provider
`envVars` per suggerimenti rivolti all'operatore come etichette di onboarding o variabili di setup OAuth
client-id/client-secret.

Usa il manifest `channelEnvVars` quando un canale ha auth o setup guidati da env che
fallback generici a shell-env, controlli config/status o prompt di setup devono vedere
senza caricare il runtime del canale.

### Ordine degli hook e utilizzo

Per i plugin modello/provider, OpenClaw chiama gli hook grosso modo in questo ordine.
La colonna “Quando usarlo” è la guida rapida alla decisione.

| #   | Hook                              | Cosa fa                                                                                                        | Quando usarlo                                                                                                                              |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | Pubblica la configurazione provider in `models.providers` durante la generazione di `models.json`             | Il provider possiede un catalogo o valori predefiniti di base URL                                                                          |
| 2   | `applyConfigDefaults`             | Applica valori predefiniti globali di configurazione del provider durante la materializzazione della configurazione | I predefiniti dipendono da modalità auth, env o semantica della famiglia di modelli del provider                                         |
| --  | _(ricerca built-in del modello)_  | OpenClaw prova prima il normale percorso di registry/catalogo                                                  | _(non è un hook plugin)_                                                                                                                   |
| 3   | `normalizeModelId`                | Normalizza alias di model-id legacy o preview prima della ricerca                                              | Il provider possiede la pulizia degli alias prima della risoluzione canonica del modello                                                  |
| 4   | `normalizeTransport`              | Normalizza `api` / `baseUrl` della famiglia provider prima dell'assemblaggio generico del modello             | Il provider possiede la pulizia del trasporto per id provider personalizzati nella stessa famiglia di trasporto                           |
| 5   | `normalizeConfig`                 | Normalizza `models.providers.<id>` prima della risoluzione runtime/provider                                    | Il provider ha bisogno di pulizia della configurazione che dovrebbe vivere con il plugin; gli helper inclusi della famiglia Google fanno anche da backstop per le entry di configurazione Google supportate |
| 6   | `applyNativeStreamingUsageCompat` | Applica riscritture compat per l'uso dello streaming nativo ai provider di configurazione                     | Il provider ha bisogno di correzioni dei metadati di utilizzo dello streaming nativo guidate dall'endpoint                                |
| 7   | `resolveConfigApiKey`             | Risolve auth con marker env per i provider di configurazione prima del caricamento runtime auth               | Il provider ha una risoluzione API key con marker env di proprietà del provider; `amazon-bedrock` ha qui anche un resolver built-in per marker env AWS |
| 8   | `resolveSyntheticAuth`            | Espone auth locale/self-hosted o basata su configurazione senza persistere plaintext                          | Il provider può operare con un marker di credenziale sintetico/locale                                                                     |
| 9   | `resolveExternalAuthProfiles`     | Sovrappone profili auth esterni di proprietà del provider; il `persistence` predefinito è `runtime-only` per credenziali di proprietà CLI/app | Il provider riusa credenziali auth esterne senza persistere refresh token copiati                                                         |
| 10  | `shouldDeferSyntheticProfileAuth` | Abbassa la priorità dei placeholder di profilo sintetico memorizzati rispetto ad auth basata su env/config    | Il provider memorizza profili placeholder sintetici che non dovrebbero avere la precedenza                                                |
| 11  | `resolveDynamicModel`             | Fallback sincrono per model id di proprietà del provider non ancora presenti nel registry locale              | Il provider accetta model id upstream arbitrari                                                                                            |
| 12  | `prepareDynamicModel`             | Warm-up asincrono, poi `resolveDynamicModel` viene eseguito di nuovo                                           | Il provider ha bisogno di metadati di rete prima di risolvere id sconosciuti                                                              |
| 13  | `normalizeResolvedModel`          | Riscrittura finale prima che l'embedded runner usi il modello risolto                                          | Il provider ha bisogno di riscritture di trasporto ma usa comunque un trasporto del core                                                 |
| 14  | `contributeResolvedModelCompat`   | Contribuisce flag compat per modelli vendor dietro un altro trasporto compatibile                             | Il provider riconosce i propri modelli su trasporti proxy senza prendersi in carico il provider                                           |
| 15  | `capabilities`                    | Metadati transcript/tooling di proprietà del provider usati dalla logica condivisa del core                   | Il provider ha bisogno di particolarità del transcript/famiglia provider                                                                   |
| 16  | `normalizeToolSchemas`            | Normalizza gli schemi degli strumenti prima che l'embedded runner li veda                                      | Il provider ha bisogno di pulizia dello schema della famiglia di trasporto                                                                 |
| 17  | `inspectToolSchemas`              | Espone diagnostica degli schemi di proprietà del provider dopo la normalizzazione                              | Il provider vuole avvisi sulle keyword senza insegnare al core regole specifiche del provider                                             |
| 18  | `resolveReasoningOutputMode`      | Seleziona il contratto di output reasoning nativo o tagged                                                     | Il provider ha bisogno di reasoning/output finale tagged invece che di campi nativi                                                       |
| 19  | `prepareExtraParams`              | Normalizzazione dei parametri richiesta prima dei wrapper generici delle opzioni di stream                    | Il provider ha bisogno di parametri richiesta predefiniti o pulizia dei parametri per provider                                            |
| 20  | `createStreamFn`                  | Sostituisce completamente il normale percorso stream con un trasporto personalizzato                           | Il provider ha bisogno di un protocollo wire personalizzato, non solo di un wrapper                                                       |
| 21  | `wrapStreamFn`                    | Wrapper dello stream dopo l'applicazione dei wrapper generici                                                  | Il provider ha bisogno di wrapper per header/body/model compat della richiesta senza un trasporto personalizzato                          |
| 22  | `resolveTransportTurnState`       | Aggiunge header nativi o metadati per turno del trasporto                                                      | Il provider vuole che i trasporti generici inviino identità di turno native del provider                                                  |
| 23  | `resolveWebSocketSessionPolicy`   | Aggiunge header WebSocket nativi o policy di cool-down della sessione                                          | Il provider vuole che i trasporti WS generici regolino header di sessione o policy di fallback                                            |
| 24  | `formatApiKey`                    | Formatter del profilo auth: il profilo memorizzato diventa la stringa runtime `apiKey`                        | Il provider memorizza metadati auth aggiuntivi e ha bisogno di una forma di token runtime personalizzata                                  |
| 25  | `refreshOAuth`                    | Override del refresh OAuth per endpoint di refresh personalizzati o policy di errore refresh                   | Il provider non rientra nei refresher condivisi `pi-ai`                                                                                    |
| 26  | `buildAuthDoctorHint`             | Suggerimento di riparazione aggiunto quando il refresh OAuth fallisce                                          | Il provider ha bisogno di indicazioni di riparazione auth proprie dopo un errore di refresh                                               |
| 27  | `matchesContextOverflowError`     | Matcher di proprietà del provider per overflow della finestra di contesto                                      | Il provider ha errori raw di overflow che le euristiche generiche non vedrebbero                                                          |
| 28  | `classifyFailoverReason`          | Classificazione della ragione di failover di proprietà del provider                                            | Il provider può mappare errori raw API/trasporto a rate-limit/sovraccarico/ecc.                                                           |
| 29  | `isCacheTtlEligible`              | Policy prompt-cache per provider proxy/backhaul                                                                | Il provider ha bisogno di gating TTL cache specifico del proxy                                                                             |
| 30  | `buildMissingAuthMessage`         | Sostituzione del messaggio generico di recupero auth mancante                                                  | Il provider ha bisogno di un suggerimento di recupero auth specifico                                                                       |
| 31  | `suppressBuiltInModel`            | Soppressione di modelli upstream obsoleti più eventuale suggerimento di errore rivolto all'utente             | Il provider ha bisogno di nascondere righe upstream obsolete o sostituirle con un suggerimento vendor                                     |
| 32  | `augmentModelCatalog`             | Righe di catalogo sintetiche/finali aggiunte dopo la discovery                                                 | Il provider ha bisogno di righe sintetiche forward-compat in `models list` e nei picker                                                   |
| 33  | `isBinaryThinking`                | Toggle reasoning on/off per provider a reasoning binario                                                       | Il provider espone solo reasoning binario acceso/spento                                                                                    |
| 34  | `supportsXHighThinking`           | Supporto reasoning `xhigh` per modelli selezionati                                                             | Il provider vuole `xhigh` solo su un sottoinsieme di modelli                                                                               |
| 35  | `resolveDefaultThinkingLevel`     | Livello `/think` predefinito per una specifica famiglia di modelli                                             | Il provider possiede la policy `/think` predefinita per una famiglia di modelli                                                            |
| 36  | `isModernModelRef`                | Matcher dei modelli moderni per filtri di profilo live e selezione smoke                                       | Il provider possiede il matching preferito di modelli live/smoke                                                                           |
| 37  | `prepareRuntimeAuth`              | Scambia una credenziale configurata nel vero token/chiave runtime subito prima dell'inferenza                 | Il provider ha bisogno di uno scambio di token o di una credenziale di richiesta a breve durata                                           |
| 38  | `resolveUsageAuth`                | Risolve credenziali di utilizzo/fatturazione per `/usage` e superfici di stato correlate                      | Il provider ha bisogno di parsing personalizzato di token utilizzo/quota o di una credenziale di utilizzo diversa                         |
| 39  | `fetchUsageSnapshot`              | Recupera e normalizza snapshot provider-specifici di utilizzo/quota dopo la risoluzione auth                  | Il provider ha bisogno di un endpoint di utilizzo specifico o di un parser payload specifico                                              |
| 40  | `createEmbeddingProvider`         | Costruisce un adapter di embedding di proprietà del provider per memoria/ricerca                               | Il comportamento di embedding della memoria appartiene al plugin provider                                                                  |
| 41  | `buildReplayPolicy`               | Restituisce una policy di replay che controlla la gestione del transcript per il provider                      | Il provider ha bisogno di una policy transcript personalizzata (per esempio rimozione dei blocchi di thinking)                           |
| 42  | `sanitizeReplayHistory`           | Riscrive la cronologia di replay dopo la pulizia generica del transcript                                       | Il provider ha bisogno di riscritture di replay specifiche oltre gli helper condivisi di compattazione                                    |
| 43  | `validateReplayTurns`             | Validazione o rimodellamento finale dei turni di replay prima dell'embedded runner                             | Il trasporto del provider ha bisogno di una validazione dei turni più rigorosa dopo la sanitizzazione generica                            |
| 44  | `onModelSelected`                 | Esegue effetti collaterali post-selezione di proprietà del provider                                            | Il provider ha bisogno di telemetria o stato di proprietà del provider quando un modello diventa attivo                                   |

`normalizeModelId`, `normalizeTransport` e `normalizeConfig` controllano prima il
plugin provider corrispondente, poi passano agli altri plugin provider capaci di hook
finché uno non cambia effettivamente model id o transport/config. Questo mantiene
funzionanti gli shim alias/compat provider senza richiedere al chiamante di sapere quale
plugin incluso possiede la riscrittura. Se nessun hook provider riscrive una voce
di configurazione supportata della famiglia Google, continua comunque ad applicarsi
la normalizzazione di configurazione inclusa di Google.

Se il provider ha bisogno di un protocollo wire completamente personalizzato o di un executor di richiesta personalizzato,
questa è una classe diversa di estensione. Questi hook servono per comportamento provider
che continua a essere eseguito sul normale loop di inferenza di OpenClaw.

### Esempio di provider

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### Esempi integrati

- Anthropic usa `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  e `wrapStreamFn` perché possiede forward-compat di Claude 4.6,
  suggerimenti per famiglia provider, guida alla riparazione auth, integrazione
  dell'endpoint di utilizzo, idoneità prompt-cache, valori predefiniti di configurazione consapevoli dell'auth, policy di thinking predefinita/adattiva di Claude e modellazione dello stream specifica di Anthropic per
  header beta, `/fast` / `serviceTier` e `context1m`.
- Gli helper di stream specifici di Claude in Anthropic restano per ora nel
  punto di giunzione pubblico `api.ts` / `contract-api.ts` del plugin incluso.
  La superficie di quel package esporta
  `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` e i builder wrapper
  Anthropic di livello inferiore invece di ampliare lo SDK generico attorno alle regole degli header beta di un singolo
  provider.
- OpenAI usa `resolveDynamicModel`, `normalizeResolvedModel` e
  `capabilities` più `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` e `isModernModelRef`
  perché possiede forward-compat di GPT-5.4, la normalizzazione diretta OpenAI
  `openai-completions` -> `openai-responses`, suggerimenti auth
  consapevoli di Codex, soppressione di Spark, righe sintetiche per la lista OpenAI e policy di thinking /
  modello live di GPT-5; la famiglia stream `openai-responses-defaults` possiede i
  wrapper condivisi nativi di OpenAI Responses per header di attribuzione,
  `/fast`/`serviceTier`, verbosità del testo, ricerca web nativa Codex,
  modellazione del payload compat per reasoning e gestione del contesto Responses.
- OpenRouter usa `catalog` più `resolveDynamicModel` e
  `prepareDynamicModel` perché il provider è pass-through e può esporre nuovi
  model id prima che il catalogo statico di OpenClaw si aggiorni; usa anche
  `capabilities`, `wrapStreamFn` e `isCacheTtlEligible` per mantenere fuori dal core
  header di richiesta specifici del provider, metadati di routing, patch di reasoning e policy prompt-cache. La sua replay policy proviene dalla
  famiglia `passthrough-gemini`, mentre la famiglia stream `openrouter-thinking`
  possiede l'iniezione di reasoning proxy e gli skip per modelli non supportati / `auto`.
- GitHub Copilot usa `catalog`, `auth`, `resolveDynamicModel` e
  `capabilities` più `prepareRuntimeAuth` e `fetchUsageSnapshot` perché ha
  bisogno di login dispositivo di proprietà del provider, comportamento di fallback del modello,
  particolarità del transcript Claude, scambio GitHub token -> Copilot token e
  un endpoint di utilizzo di proprietà del provider.
- OpenAI Codex usa `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` e `augmentModelCatalog` più
  `prepareExtraParams`, `resolveUsageAuth` e `fetchUsageSnapshot` perché
  continua a funzionare su trasporti OpenAI del core ma possiede la normalizzazione del suo
  transport/base URL, la policy di fallback del refresh OAuth, la scelta di trasporto predefinita,
  righe sintetiche del catalogo Codex e integrazione dell'endpoint di utilizzo di ChatGPT; condivide
  la stessa famiglia stream `openai-responses-defaults` del diretto OpenAI.
- Google AI Studio e Gemini CLI OAuth usano `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` e `isModernModelRef` perché la
  famiglia replay `google-gemini` possiede fallback forward-compat di Gemini 3.1,
  validazione nativa del replay Gemini, sanitizzazione bootstrap del replay, modalità di output tagged
  reasoning e matching dei modelli moderni, mentre la
  famiglia stream `google-thinking` possiede la normalizzazione del payload thinking di Gemini;
  Gemini CLI OAuth usa anche `formatApiKey`, `resolveUsageAuth` e
  `fetchUsageSnapshot` per formattazione del token, parsing del token e wiring
  dell'endpoint quota.
- Anthropic Vertex usa `buildReplayPolicy` tramite la
  famiglia replay `anthropic-by-model` così la pulizia del replay specifica di Claude resta
  limitata agli id Claude invece che a ogni trasporto `anthropic-messages`.
- Amazon Bedrock usa `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` e `resolveDefaultThinkingLevel` perché possiede
  la classificazione specifica di Bedrock di errori throttle/not-ready/context-overflow
  per traffico Anthropic-on-Bedrock; la sua replay policy continua a condividere la stessa guardia
  solo-Claude `anthropic-by-model`.
- OpenRouter, Kilocode, Opencode e Opencode Go usano `buildReplayPolicy`
  tramite la famiglia replay `passthrough-gemini` perché fanno da proxy ai modelli
  Gemini tramite trasporti compatibili OpenAI e hanno bisogno di sanitizzazione
  della thought-signature Gemini senza validazione nativa del replay Gemini o
  riscritture bootstrap.
- MiniMax usa `buildReplayPolicy` tramite la
  famiglia replay `hybrid-anthropic-openai` perché un singolo provider possiede sia
  semantica Anthropic-message sia semantica compatibile OpenAI; mantiene la rimozione
  dei blocchi di thinking solo-Claude sul lato Anthropic sovrascrivendo però la modalità di output
  reasoning di nuovo a nativa, e la famiglia stream `minimax-fast-mode` possiede le riscritture
  dei modelli fast-mode sul percorso stream condiviso.
- Moonshot usa `catalog` più `wrapStreamFn` perché continua a usare il trasporto OpenAI condiviso ma ha bisogno di normalizzazione del payload thinking di proprietà del provider; la
  famiglia stream `moonshot-thinking` mappa configurazione più stato `/think` sul suo
  payload thinking binario nativo.
- Kilocode usa `catalog`, `capabilities`, `wrapStreamFn` e
  `isCacheTtlEligible` perché ha bisogno di header di richiesta di proprietà del provider,
  normalizzazione del payload reasoning, suggerimenti transcript Gemini e gating
  Anthropic cache-TTL; la famiglia stream `kilocode-thinking` mantiene l'iniezione
  del thinking Kilo sul percorso stream proxy condiviso saltando `kilo/auto` e
  altri id di modello proxy che non supportano payload di reasoning espliciti.
- Z.AI usa `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` e `fetchUsageSnapshot` perché possiede fallback GLM-5,
  valori predefiniti `tool_stream`, UX thinking binaria, matching di modelli moderni e sia auth di utilizzo sia recupero quota; la famiglia stream `tool-stream-default-on` mantiene il wrapper `tool_stream` attivo per default fuori dal glue scritto a mano per provider.
- xAI usa `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` e `isModernModelRef`
  perché possiede la normalizzazione del trasporto nativo xAI Responses, riscritture alias
  Grok fast-mode, `tool_stream` predefinito, pulizia strict-tool / reasoning-payload,
  riuso auth di fallback per strumenti di proprietà del plugin, risoluzione
  forward-compat dei modelli Grok e patch compat di proprietà del provider come profilo schema strumenti xAI, keyword di schema non supportate, `web_search` nativo e decodifica HTML entity degli argomenti delle tool-call.
- Mistral, OpenCode Zen e OpenCode Go usano solo `capabilities` per mantenere
  particolarità transcript/tooling fuori dal core.
- I provider inclusi solo catalogo come `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` e `volcengine` usano
  solo `catalog`.
- Qwen usa `catalog` per il suo text provider più registrazioni condivise di comprensione media e generazione video per le sue superfici multimodali.
- MiniMax e Xiaomi usano `catalog` più hook di utilizzo perché il loro comportamento `/usage`
  è di proprietà del plugin anche se l'inferenza continua a passare attraverso i trasporti condivisi.

## Helper runtime

I plugin possono accedere a helper selezionati del core tramite `api.runtime`. Per TTS:

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Note:

- `textToSpeech` restituisce il normale payload TTS del core per superfici file/messaggio vocale.
- Usa la configurazione `messages.tts` del core e la selezione del provider.
- Restituisce buffer audio PCM + sample rate. I plugin devono ricampionare/codificare per i provider.
- `listVoices` è facoltativo per provider. Usalo per selettori vocali o flussi di setup di proprietà del vendor.
- Gli elenchi di voci possono includere metadati più ricchi come locale, genere e tag di personalità per selettori consapevoli del provider.
- OpenAI ed ElevenLabs supportano oggi la telefonia. Microsoft no.

I plugin possono anche registrare speech provider tramite `api.registerSpeechProvider(...)`.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

Note:

- Mantieni nel core policy TTS, fallback e consegna della risposta.
- Usa speech provider per comportamento di sintesi di proprietà del vendor.
- L'input legacy Microsoft `edge` viene normalizzato all'id provider `microsoft`.
- Il modello di proprietà preferito è orientato all'azienda: un singolo plugin vendor può possedere
  provider di testo, voce, immagini e media futuri man mano che OpenClaw aggiunge quei
  contratti di capacità.

Per la comprensione di immagini/audio/video, i plugin registrano un provider tipizzato
di comprensione media invece di un contenitore generico chiave/valore:

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

Note:

- Mantieni orchestrazione, fallback, configurazione e wiring del canale nel core.
- Mantieni il comportamento del vendor nel plugin provider.
- L'espansione additiva dovrebbe restare tipizzata: nuovi metodi facoltativi, nuovi campi di risultato facoltativi, nuove capacità facoltative.
- La generazione video segue già lo stesso pattern:
  - il core possiede il contratto di capacità e l'helper runtime
  - i plugin vendor registrano `api.registerVideoGenerationProvider(...)`
  - i plugin funzionalità/canale consumano `api.runtime.videoGeneration.*`

Per gli helper runtime di comprensione media, i plugin possono chiamare:

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

Per la trascrizione audio, i plugin possono usare sia il runtime di comprensione media
sia il vecchio alias STT:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

Note:

- `api.runtime.mediaUnderstanding.*` è la superficie condivisa preferita per
  comprensione di immagini/audio/video.
- Usa la configurazione audio di comprensione media del core (`tools.media.audio`) e l'ordine di fallback dei provider.
- Restituisce `{ text: undefined }` quando non viene prodotta alcuna trascrizione (ad esempio input saltato/non supportato).
- `api.runtime.stt.transcribeAudioFile(...)` resta come alias di compatibilità.

I plugin possono anche avviare esecuzioni subagent in background tramite `api.runtime.subagent`:

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

Note:

- `provider` e `model` sono override facoltativi per esecuzione, non cambi persistenti della sessione.
- OpenClaw rispetta questi campi di override solo per chiamanti trusted.
- Per esecuzioni di fallback di proprietà del plugin, gli operatori devono attivarle con `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Usa `plugins.entries.<id>.subagent.allowedModels` per limitare i plugin trusted a target canonici specifici `provider/model`, oppure `"*"` per consentire esplicitamente qualsiasi target.
- Le esecuzioni subagent di plugin non trusted continuano a funzionare, ma le richieste di override vengono rifiutate invece di fare fallback silenzioso.

Per la ricerca web, i plugin possono consumare l'helper runtime condiviso invece di
accedere al wiring dello strumento agente:

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

I plugin possono anche registrare web-search provider tramite
`api.registerWebSearchProvider(...)`.

Note:

- Mantieni nel core selezione del provider, risoluzione delle credenziali e semantica condivisa della richiesta.
- Usa web-search provider per trasporti di ricerca specifici del vendor.
- `api.runtime.webSearch.*` è la superficie condivisa preferita per plugin funzionalità/canale che hanno bisogno di comportamento di ricerca senza dipendere dal wrapper dello strumento agente.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: genera un'immagine usando la catena configurata di provider per generazione immagini.
- `listProviders(...)`: elenca i provider disponibili di generazione immagini e le loro capacità.

## Route HTTP del gateway

I plugin possono esporre endpoint HTTP con `api.registerHttpRoute(...)`.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

Campi della route:

- `path`: percorso della route sotto il server HTTP del gateway.
- `auth`: obbligatorio. Usa `"gateway"` per richiedere la normale auth del gateway, oppure `"plugin"` per auth/validazione webhook gestite dal plugin.
- `match`: facoltativo. `"exact"` (predefinito) oppure `"prefix"`.
- `replaceExisting`: facoltativo. Consente allo stesso plugin di sostituire la propria route già registrata.
- `handler`: restituisce `true` quando la route ha gestito la richiesta.

Note:

- `api.registerHttpHandler(...)` è stato rimosso e causerà un errore di caricamento del plugin. Usa invece `api.registerHttpRoute(...)`.
- Le route dei plugin devono dichiarare esplicitamente `auth`.
- I conflitti esatti `path + match` vengono rifiutati salvo `replaceExisting: true`, e un plugin non può sostituire la route di un altro plugin.
- Route sovrapposte con livelli `auth` diversi vengono rifiutate. Mantieni catene di fallthrough `exact`/`prefix` solo sullo stesso livello auth.
- Le route `auth: "plugin"` **non** ricevono automaticamente scope runtime operatore. Servono per webhook/validazione firma gestiti dal plugin, non per chiamate helper privilegiate del Gateway.
- Le route `auth: "gateway"` vengono eseguite all'interno di uno scope runtime di richiesta Gateway, ma quello scope è intenzionalmente conservativo:
  - auth bearer con segreto condiviso (`gateway.auth.mode = "token"` / `"password"`) mantiene gli scope runtime delle route plugin fissati a `operator.write`, anche se il chiamante invia `x-openclaw-scopes`
  - le modalità HTTP trusted che portano identità (ad esempio `trusted-proxy` o `gateway.auth.mode = "none"` su un ingresso privato) rispettano `x-openclaw-scopes` solo quando l'header è esplicitamente presente
  - se `x-openclaw-scopes` è assente in quelle richieste plugin-route con identità, lo scope runtime torna a `operator.write`
- Regola pratica: non presumere che una route plugin con auth gateway sia implicitamente una superficie admin. Se la tua route ha bisogno di comportamento solo admin, richiedi una modalità auth che porti identità e documenta il contratto esplicito dell'header `x-openclaw-scopes`.

## Percorsi di importazione del Plugin SDK

Usa sottopercorsi SDK invece dell'import monolitico `openclaw/plugin-sdk` quando
scrivi plugin:

- `openclaw/plugin-sdk/plugin-entry` per le primitive di registrazione del plugin.
- `openclaw/plugin-sdk/core` per il contratto generico condiviso rivolto ai plugin.
- `openclaw/plugin-sdk/config-schema` per l'esportazione dello schema Zod root `openclaw.json`
  (`OpenClawSchema`).
- Primitive di canale stabili come `openclaw/plugin-sdk/channel-setup`,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input` e
  `openclaw/plugin-sdk/webhook-ingress` per wiring condiviso di setup/auth/risposta/webhook. `channel-inbound` è la casa condivisa per debounce, matching delle menzioni,
  helper per le policy di menzione in ingresso, formattazione delle envelope in ingresso e helper per il contesto delle envelope in ingresso.
  `channel-setup` è il punto di giunzione ristretto per setup con installazione facoltativa.
  `setup-runtime` è la superficie di setup sicura per runtime usata da `setupEntry` /
  avvio differito, inclusi gli adapter di patch setup sicuri da importazione.
  `setup-adapter-runtime` è il punto di giunzione dell'adapter env-aware per setup account.
  `setup-tools` è il piccolo punto di giunzione helper CLI/archive/docs (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Sottopercorsi di dominio come `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-gateway-runtime`,
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`,
  `openclaw/plugin-sdk/approval-handler-runtime`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store` e
  `openclaw/plugin-sdk/directory-runtime` per helper runtime/config condivisi.
  `telegram-command-config` è il punto di giunzione pubblico ristretto per normalizzazione/validazione di comandi personalizzati Telegram e resta disponibile anche se la superficie contrattuale inclusa di Telegram non è temporaneamente disponibile.
  `text-runtime` è il punto di giunzione condiviso per testo/markdown/logging, incluse
  rimozione del testo visibile all'assistente, helper di render/chunking markdown, helper di redazione, helper per directive-tag e utility di safe-text.
- I punti di giunzione di canale specifici per le approvazioni dovrebbero preferire un unico contratto `approvalCapability`
  sul plugin. Il core legge quindi auth di approvazione, consegna, render,
  routing nativo e comportamento lazy del native-handler tramite questa unica capacità
  invece di mescolare il comportamento di approvazione in campi plugin non correlati.
- `openclaw/plugin-sdk/channel-runtime` è deprecato e resta solo come
  shim di compatibilità per plugin più vecchi. Il nuovo codice dovrebbe importare invece
  le primitive generiche più ristrette, e il codice del repo non dovrebbe aggiungere nuovi import dello shim.
- I dettagli interni delle estensioni incluse restano privati. I plugin esterni dovrebbero usare solo sottopercorsi `openclaw/plugin-sdk/*`. Il codice core/test di OpenClaw può usare i punti di ingresso pubblici del repo sotto la root di un package plugin come `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` e file a scope ristretto come
  `login-qr-api.js`. Non importare mai `src/*` di un package plugin dal core o da
  un'altra estensione.
- Suddivisione del punto di ingresso del repo:
  `<plugin-package-root>/api.js` è il barrel di helper/tipi,
  `<plugin-package-root>/runtime-api.js` è il barrel solo runtime,
  `<plugin-package-root>/index.js` è l'entry del plugin incluso,
  e `<plugin-package-root>/setup-entry.js` è l'entry del plugin di setup.
- Esempi attuali di provider inclusi:
  - Anthropic usa `api.js` / `contract-api.js` per helper di stream Claude come
    `wrapAnthropicProviderStream`, helper per beta-header e parsing di `service_tier`.
  - OpenAI usa `api.js` per builder del provider, helper di modello predefinito e
    builder del provider realtime.
  - OpenRouter usa `api.js` per il suo builder del provider più helper
    di onboarding/configurazione, mentre `register.runtime.js` può ancora riesportare helper generici `plugin-sdk/provider-stream` per uso locale al repo.
- I punti di ingresso pubblici caricati tramite facade preferiscono lo snapshot della configurazione runtime attiva
  quando esiste, e in caso contrario usano la configurazione risolta su disco quando
  OpenClaw non sta ancora servendo uno snapshot runtime.
- Le primitive generiche condivise restano il contratto SDK pubblico preferito. Un piccolo insieme riservato di punti di giunzione helper compatibili con marchio di canale incluso esiste ancora. Trattali come punti di giunzione di manutenzione/compatibilità per inclusi, non nuovi target di importazione per terze parti; i nuovi contratti cross-channel dovrebbero comunque approdare su sottopercorsi generici `plugin-sdk/*` o sui barrel locali `api.js` /
  `runtime-api.js` del plugin.

Nota sulla compatibilità:

- Evita il barrel root `openclaw/plugin-sdk` nel nuovo codice.
- Preferisci prima le primitive stabili più ristrette. I sottopercorsi più recenti per setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool sono il contratto previsto per nuovo lavoro su plugin inclusi ed esterni.
  Il parsing/matching dei target appartiene a `openclaw/plugin-sdk/channel-targets`.
  I gate delle azioni messaggio e gli helper di message-id per reazioni appartengono a
  `openclaw/plugin-sdk/channel-actions`.
- I barrel helper specifici delle estensioni incluse non sono stabili per impostazione predefinita. Se un
  helper serve solo a un'estensione inclusa, mantienilo dietro il punto di giunzione
  locale `api.js` o `runtime-api.js` dell'estensione invece di promuoverlo in
  `openclaw/plugin-sdk/<extension>`.
- I nuovi punti di giunzione helper condivisi dovrebbero essere generici, non con marchio di canale. Il parsing condiviso dei target appartiene a `openclaw/plugin-sdk/channel-targets`; i dettagli interni specifici del canale restano dietro il punto di giunzione locale `api.js` o `runtime-api.js` del plugin proprietario.
- Sottopercorsi specifici per capacità come `image-generation`,
  `media-understanding` e `speech` esistono perché i plugin inclusi/nativi li usano oggi. La loro presenza non significa di per sé che ogni helper esportato sia un contratto esterno congelato a lungo termine.

## Schemi dello strumento message

I plugin dovrebbero possedere i contributi allo schema `describeMessageTool(...)` specifici del canale. Mantieni i campi specifici del provider nel plugin, non nel core condiviso.

Per frammenti di schema portabili condivisi, riusa gli helper generici esportati tramite
`openclaw/plugin-sdk/channel-actions`:

- `createMessageToolButtonsSchema()` per payload in stile griglia di pulsanti
- `createMessageToolCardSchema()` per payload di card strutturate

Se una forma di schema ha senso solo per un provider, definiscila nel codice sorgente
di quel plugin invece di promuoverla nello SDK condiviso.

## Risoluzione del target del canale

I plugin di canale dovrebbero possedere la semantica del target specifica del canale. Mantieni
generico l'host outbound condiviso e usa la superficie dell'adapter di messaggistica per le regole del provider:

- `messaging.inferTargetChatType({ to })` decide se un target normalizzato
  deve essere trattato come `direct`, `group` o `channel` prima della lookup nella directory.
- `messaging.targetResolver.looksLikeId(raw, normalized)` dice al core se un
  input deve passare direttamente alla risoluzione id-like invece che alla ricerca nella directory.
- `messaging.targetResolver.resolveTarget(...)` è il fallback del plugin quando
  il core ha bisogno di una risoluzione finale di proprietà del provider dopo la normalizzazione o
  dopo un miss nella directory.
- `messaging.resolveOutboundSessionRoute(...)` possiede la costruzione della route di sessione specifica del provider una volta che il target è risolto.

Suddivisione consigliata:

- Usa `inferTargetChatType` per decisioni di categoria che devono avvenire prima
  della ricerca tra peer/gruppi.
- Usa `looksLikeId` per i controlli “tratta questo come id target esplicito/nativo”.
- Usa `resolveTarget` per fallback di normalizzazione specifico del provider, non per
  ricerche ampie nella directory.
- Mantieni id nativi del provider come chat id, thread id, JID, handle e room id
  nei valori `target` o in parametri specifici del provider, non in campi SDK generici.

## Directory basate sulla configurazione

I plugin che derivano voci di directory dalla configurazione dovrebbero mantenere quella logica nel
plugin e riutilizzare gli helper condivisi da
`openclaw/plugin-sdk/directory-runtime`.

Usa questo quando un canale ha peer/gruppi basati su configurazione come:

- peer DM guidati da allowlist
- mappe di canale/gruppo configurate
- fallback statici della directory con scope account

Gli helper condivisi in `directory-runtime` gestiscono solo operazioni generiche:

- filtro delle query
- applicazione dei limiti
- helper di deduplica/normalizzazione
- costruzione di `ChannelDirectoryEntry[]`

L'ispezione degli account specifica del canale e la normalizzazione degli id dovrebbero restare
nell'implementazione del plugin.

## Cataloghi provider

I plugin provider possono definire cataloghi di modelli per l'inferenza con
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` restituisce la stessa forma che OpenClaw scrive in
`models.providers`:

- `{ provider }` per una voce singola di provider
- `{ providers }` per più voci provider

Usa `catalog` quando il plugin possiede model id specifici del provider, valori predefiniti di base URL o metadati dei modelli condizionati dall'auth.

`catalog.order` controlla quando il catalogo di un plugin viene unito rispetto ai
provider impliciti built-in di OpenClaw:

- `simple`: provider semplici guidati da API key o env
- `profile`: provider che compaiono quando esistono profili auth
- `paired`: provider che sintetizzano più voci provider correlate
- `late`: ultimo passaggio, dopo gli altri provider impliciti

I provider successivi vincono in caso di collisione di chiave, quindi i plugin possono intenzionalmente
sovrascrivere una voce built-in del provider con lo stesso id provider.

Compatibilità:

- `discovery` continua a funzionare come alias legacy
- se sono registrati sia `catalog` sia `discovery`, OpenClaw usa `catalog`

## Ispezione del canale in sola lettura

Se il tuo plugin registra un canale, preferisci implementare
`plugin.config.inspectAccount(cfg, accountId)` insieme a `resolveAccount(...)`.

Perché:

- `resolveAccount(...)` è il percorso runtime. Può assumere che le credenziali
  siano completamente materializzate e può fallire rapidamente quando mancano
  secret necessari.
- I percorsi di comandi in sola lettura come `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` e i flussi doctor/config
  repair non dovrebbero aver bisogno di materializzare credenziali runtime solo per
  descrivere la configurazione.

Comportamento consigliato per `inspectAccount(...)`:

- Restituisci solo stato descrittivo dell'account.
- Preserva `enabled` e `configured`.
- Includi campi relativi a sorgente/stato delle credenziali quando rilevanti, come:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Non è necessario restituire valori raw dei token solo per riportare la disponibilità in sola lettura. Restituire `tokenStatus: "available"` (e il campo sorgente corrispondente) è sufficiente per comandi in stile status.
- Usa `configured_unavailable` quando una credenziale è configurata tramite SecretRef ma non è disponibile nel percorso di comando corrente.

Questo consente ai comandi in sola lettura di riportare “configured but unavailable in this command path” invece di mandare in crash o riportare erroneamente l'account come non configurato.

## Package pack

Una directory plugin può includere un `package.json` con `openclaw.extensions`:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Ogni entry diventa un plugin. Se il pack elenca più estensioni, l'id del plugin
diventa `name/<fileBase>`.

Se il tuo plugin importa dipendenze npm, installale in quella directory così
`node_modules` è disponibile (`npm install` / `pnpm install`).

Guardrail di sicurezza: ogni entry `openclaw.extensions` deve restare all'interno della directory plugin
dopo la risoluzione dei symlink. Le entry che escono dalla directory del package vengono
rifiutate.

Nota di sicurezza: `openclaw plugins install` installa le dipendenze del plugin con
`npm install --omit=dev --ignore-scripts` (nessun lifecycle script, nessuna dev dependency a runtime). Mantieni puri JS/TS gli alberi delle dipendenze del plugin ed evita package che richiedono build `postinstall`.

Facoltativo: `openclaw.setupEntry` può puntare a un modulo leggero solo setup.
Quando OpenClaw ha bisogno di superfici di setup per un plugin di canale disabilitato, oppure
quando un plugin di canale è abilitato ma non ancora configurato, carica `setupEntry`
invece della entry completa del plugin. Questo mantiene avvio e setup più leggeri
quando la tua entry principale collega anche strumenti, hook o altro codice solo runtime.

Facoltativo: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
può far optare un plugin di canale nello stesso percorso `setupEntry` durante la fase
di avvio pre-listen del gateway, anche quando il canale è già configurato.

Usa questo solo quando `setupEntry` copre completamente la superficie di avvio che deve esistere
prima che il gateway inizi ad ascoltare. In pratica, ciò significa che l'entry di setup
deve registrare ogni capacità di proprietà del canale da cui dipende l'avvio, come:

- la registrazione del canale stesso
- qualsiasi route HTTP che deve essere disponibile prima che il gateway inizi ad ascoltare
- qualsiasi metodo gateway, strumento o servizio che deve esistere durante la stessa finestra temporale

Se la tua entry completa possiede ancora una capacità di avvio necessaria, non abilitare
questo flag. Mantieni il comportamento predefinito e lascia che OpenClaw carichi
la entry completa durante l'avvio.

I canali inclusi possono anche pubblicare helper di superficie contrattuale solo setup che il core
può consultare prima che il runtime completo del canale sia caricato. La superficie attuale di
promozione setup è:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Il core usa questa superficie quando ha bisogno di promuovere una configurazione legacy di canale single-account
in `channels.<id>.accounts.*` senza caricare la entry completa del plugin.
Matrix è l'esempio incluso attuale: sposta solo chiavi auth/bootstrap in un
account promosso con nome quando esistono già account con nome, e può preservare
una chiave default-account configurata non canonica invece di creare sempre
`accounts.default`.

Quegli adapter di patch setup mantengono lazy la discovery della superficie contrattuale inclusa. Il tempo di importazione resta leggero; la superficie di promozione viene caricata solo al primo utilizzo invece di rientrare nell'avvio del canale incluso all'import del modulo.

Quando quelle superfici di avvio includono metodi RPC del gateway, mantienili su un
prefisso specifico del plugin. I namespace admin del core (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) restano riservati e si risolvono sempre
in `operator.admin`, anche se un plugin richiede uno scope più ristretto.

Esempio:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### Metadati del catalogo canali

I plugin di canale possono pubblicizzare metadati di setup/discovery tramite `openclaw.channel` e
suggerimenti di installazione tramite `openclaw.install`. Questo mantiene il catalogo del core senza dati.

Esempio:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

Campi utili di `openclaw.channel` oltre all'esempio minimo:

- `detailLabel`: etichetta secondaria per superfici più ricche di catalogo/status
- `docsLabel`: sostituisce il testo del link alla documentazione
- `preferOver`: id plugin/canale a priorità inferiore che questa voce di catalogo dovrebbe superare
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: controlli del testo per la superficie di selezione
- `markdownCapable`: contrassegna il canale come compatibile con markdown per decisioni di formattazione outbound
- `exposure.configured`: nasconde il canale dalle superfici elenco dei canali configurati quando impostato a `false`
- `exposure.setup`: nasconde il canale dai picker interattivi di setup/configurazione quando impostato a `false`
- `exposure.docs`: contrassegna il canale come interno/privato per le superfici di navigazione della documentazione
- `showConfigured` / `showInSetup`: alias legacy ancora accettati per compatibilità; preferisci `exposure`
- `quickstartAllowFrom`: fa opt-in del canale nel flusso standard quickstart `allowFrom`
- `forceAccountBinding`: richiede binding esplicito dell'account anche quando esiste un solo account
- `preferSessionLookupForAnnounceTarget`: preferisce session lookup quando risolve target di announce

OpenClaw può anche unire **cataloghi di canale esterni** (ad esempio un export
di registry MPM). Inserisci un file JSON in uno di questi percorsi:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Oppure punta `OPENCLAW_PLUGIN_CATALOG_PATHS` (o `OPENCLAW_MPM_CATALOG_PATHS`) a
uno o più file JSON (delimitati da virgola/punto e virgola/`PATH`). Ogni file dovrebbe
contenere `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. Il parser accetta anche `"packages"` o `"plugins"` come alias legacy per la chiave `"entries"`.

## Plugin del motore di contesto

I plugin del motore di contesto possiedono l'orchestrazione del contesto di sessione per ingest, assemblaggio
e compattazione. Registrali dal tuo plugin con
`api.registerContextEngine(id, factory)`, quindi seleziona il motore attivo con
`plugins.slots.contextEngine`.

Usa questo quando il tuo plugin deve sostituire o estendere la pipeline di contesto predefinita invece di limitarsi ad aggiungere ricerca in memoria o hook.

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Se il tuo motore **non** possiede l'algoritmo di compattazione, mantieni `compact()`
implementato e delegalo esplicitamente:

```ts
import {
  buildMemorySystemPromptAddition,
  delegateCompactionToRuntime,
} from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Aggiungere una nuova capacità

Quando un plugin ha bisogno di un comportamento che non rientra nell'API attuale, non aggirare
il sistema dei plugin con un accesso privato. Aggiungi la capacità mancante.

Sequenza consigliata:

1. definisci il contratto del core
   Decidi quale comportamento condiviso il core deve possedere: policy, fallback, merge della configurazione,
   lifecycle, semantica rivolta ai canali e forma dell'helper runtime.
2. aggiungi superfici tipizzate di registrazione/runtime del plugin
   Estendi `OpenClawPluginApi` e/o `api.runtime` con la superficie tipizzata di capacità più piccola utile.
3. collega i consumer core + canale/funzionalità
   I canali e i plugin funzionalità dovrebbero consumare la nuova capacità tramite il core,
   non importando direttamente un'implementazione vendor.
4. registra implementazioni vendor
   I plugin vendor registrano quindi i loro backend rispetto alla capacità.
5. aggiungi copertura contrattuale
   Aggiungi test così la proprietà e la forma della registrazione restano esplicite nel tempo.

È così che OpenClaw resta opinionated senza diventare hardcoded alla visione del mondo di
un singolo provider. Vedi il [Capability Cookbook](/it/plugins/architecture)
per una checklist concreta dei file e un esempio completo.

### Checklist della capacità

Quando aggiungi una nuova capacità, l'implementazione dovrebbe di solito toccare insieme
queste superfici:

- tipi del contratto core in `src/<capability>/types.ts`
- runner del core/helper runtime in `src/<capability>/runtime.ts`
- superficie API di registrazione del plugin in `src/plugins/types.ts`
- wiring del registry plugin in `src/plugins/registry.ts`
- esposizione runtime del plugin in `src/plugins/runtime/*` quando i plugin funzionalità/canale
  devono consumarla
- helper di acquisizione/test in `src/test-utils/plugin-registration.ts`
- asserzioni di proprietà/contratto in `src/plugins/contracts/registry.ts`
- documentazione per operatori/plugin in `docs/`

Se una di queste superfici manca, di solito è un segno che la capacità
non è ancora completamente integrata.

### Template della capacità

Pattern minimo:

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// shared runtime helper for feature/channel plugins
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

Pattern del test di contratto:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Questo mantiene semplice la regola:

- il core possiede il contratto di capacità + l'orchestrazione
- i plugin vendor possiedono le implementazioni vendor
- i plugin funzionalità/canale consumano helper runtime
- i test di contratto mantengono esplicita la proprietà
