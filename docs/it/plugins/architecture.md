---
read_when:
    - Stai creando o eseguendo il debug di plugin OpenClaw nativi
    - Vuoi comprendere il modello di capacità dei plugin o i confini di ownership
    - Stai lavorando sulla pipeline di caricamento dei plugin o sul registry
    - Stai implementando hook di runtime dei provider o plugin di canale
sidebarTitle: Internals
summary: 'Componenti interni dei plugin: modello di capacità, ownership, contratti, pipeline di caricamento e helper di runtime'
title: Componenti interni dei plugin
x-i18n:
    generated_at: "2026-04-09T01:32:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2575791f835990589219bb06d8ca92e16a8c38b317f0bfe50b421682f253ef18
    source_path: plugins/architecture.md
    workflow: 15
---

# Componenti interni dei plugin

<Info>
  Questo è il **riferimento di architettura approfondito**. Per guide pratiche, vedi:
  - [Installare e usare i plugin](/it/tools/plugin) — guida utente
  - [Introduzione](/it/plugins/building-plugins) — primo tutorial sui plugin
  - [Plugin di canale](/it/plugins/sdk-channel-plugins) — crea un canale di messaggistica
  - [Plugin provider](/it/plugins/sdk-provider-plugins) — crea un provider di modelli
  - [Panoramica SDK](/it/plugins/sdk-overview) — mappa degli import e API di registrazione
</Info>

Questa pagina copre l'architettura interna del sistema di plugin di OpenClaw.

## Modello pubblico delle capacità

Le capacità sono il modello pubblico dei **plugin nativi** all'interno di OpenClaw. Ogni
plugin OpenClaw nativo si registra rispetto a uno o più tipi di capacità:

| Capacità              | Metodo di registrazione                         | Plugin di esempio                     |
| --------------------- | ----------------------------------------------- | ------------------------------------- |
| Inferenza testuale    | `api.registerProvider(...)`                     | `openai`, `anthropic`                 |
| Backend di inferenza CLI | `api.registerCliBackend(...)`                | `openai`, `anthropic`                 |
| Voce                  | `api.registerSpeechProvider(...)`               | `elevenlabs`, `microsoft`             |
| Trascrizione realtime | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                            |
| Voce realtime         | `api.registerRealtimeVoiceProvider(...)`        | `openai`                              |
| Comprensione dei media | `api.registerMediaUnderstandingProvider(...)`  | `openai`, `google`                    |
| Generazione di immagini | `api.registerImageGenerationProvider(...)`    | `openai`, `google`, `fal`, `minimax`  |
| Generazione musicale  | `api.registerMusicGenerationProvider(...)`      | `google`, `minimax`                   |
| Generazione video     | `api.registerVideoGenerationProvider(...)`      | `qwen`                                |
| Recupero web          | `api.registerWebFetchProvider(...)`             | `firecrawl`                           |
| Ricerca web           | `api.registerWebSearchProvider(...)`            | `google`                              |
| Canale / messaggistica | `api.registerChannel(...)`                     | `msteams`, `matrix`                   |

Un plugin che registra zero capacità ma fornisce hook, strumenti o
servizi è un plugin **legacy solo-hook**. Questo schema è ancora pienamente supportato.

### Posizione sulla compatibilità esterna

Il modello delle capacità è stato integrato nel core e viene usato oggi dai plugin
bundled/nativi, ma la compatibilità dei plugin esterni richiede ancora una soglia
più rigorosa di "è esportato, quindi è congelato".

Indicazioni attuali:

- **plugin esterni esistenti:** mantieni funzionanti le integrazioni basate su hook; considera
  questo come la base di compatibilità
- **nuovi plugin bundled/nativi:** preferisci una registrazione esplicita delle capacità rispetto a
  integrazioni specifiche del fornitore o a nuovi design solo-hook
- **plugin esterni che adottano la registrazione delle capacità:** consentito, ma tratta
  le superfici helper specifiche per capacità come in evoluzione a meno che la documentazione non contrassegni esplicitamente un contratto come stabile

Regola pratica:

- le API di registrazione delle capacità sono la direzione prevista
- gli hook legacy restano il percorso più sicuro per evitare rotture per i plugin esterni durante
  la transizione
- i sottopercorsi helper esportati non sono tutti uguali; preferisci il contratto
  ristretto documentato, non esportazioni helper incidentali

### Forme dei plugin

OpenClaw classifica ogni plugin caricato in una forma in base al suo comportamento
effettivo di registrazione (non solo ai metadati statici):

- **plain-capability** -- registra esattamente un tipo di capacità (per esempio un
  plugin solo provider come `mistral`)
- **hybrid-capability** -- registra più tipi di capacità (per esempio
  `openai` possiede inferenza testuale, voce, comprensione dei media e generazione
  di immagini)
- **hook-only** -- registra solo hook (tipizzati o personalizzati), nessuna capacità,
  strumento, comando o servizio
- **non-capability** -- registra strumenti, comandi, servizi o route ma nessuna
  capacità

Usa `openclaw plugins inspect <id>` per vedere la forma di un plugin e la suddivisione
delle capacità. Vedi [riferimento CLI](/cli/plugins#inspect) per i dettagli.

### Hook legacy

L'hook `before_agent_start` resta supportato come percorso di compatibilità per
i plugin solo-hook. Plugin legacy usati realmente dipendono ancora da esso.

Direzione:

- mantenerlo funzionante
- documentarlo come legacy
- preferire `before_model_resolve` per il lavoro di override di modello/provider
- preferire `before_prompt_build` per il lavoro di mutazione del prompt
- rimuoverlo solo dopo che l'uso reale sarà diminuito e la copertura delle fixture dimostrerà la sicurezza della migrazione

### Segnali di compatibilità

Quando esegui `openclaw doctor` o `openclaw plugins inspect <id>`, potresti vedere
una di queste etichette:

| Segnale                   | Significato                                                  |
| ------------------------- | ------------------------------------------------------------ |
| **config valid**          | La configurazione viene analizzata correttamente e i plugin vengono risolti |
| **compatibility advisory** | Il plugin usa uno schema supportato ma più vecchio (es. `hook-only`) |
| **legacy warning**        | Il plugin usa `before_agent_start`, che è deprecato          |
| **hard error**            | La configurazione non è valida o il plugin non è riuscito a caricarsi |

Né `hook-only` né `before_agent_start` interromperanno oggi il tuo plugin --
`hook-only` è solo informativo, e `before_agent_start` attiva solo un avviso. Questi
segnali compaiono anche in `openclaw status --all` e `openclaw plugins doctor`.

## Panoramica dell'architettura

Il sistema di plugin di OpenClaw ha quattro livelli:

1. **Manifest + discovery**
   OpenClaw trova i plugin candidati da percorsi configurati, radici di workspace,
   radici globali delle estensioni ed estensioni bundled. Il discovery legge prima i
   manifest nativi `openclaw.plugin.json` insieme ai manifest bundle supportati.
2. **Abilitazione + validazione**
   Il core decide se un plugin scoperto è abilitato, disabilitato, bloccato oppure
   selezionato per uno slot esclusivo come la memoria.
3. **Caricamento a runtime**
   I plugin OpenClaw nativi vengono caricati in-process tramite jiti e registrano
   capacità in un registry centrale. I bundle compatibili vengono normalizzati in
   record del registry senza importare codice di runtime.
4. **Consumo delle superfici**
   Il resto di OpenClaw legge il registry per esporre strumenti, canali, configurazione
   dei provider, hook, route HTTP, comandi CLI e servizi.

Per quanto riguarda nello specifico la CLI dei plugin, il discovery dei comandi root è suddiviso in due fasi:

- i metadati al momento del parsing provengono da `registerCli(..., { descriptors: [...] })`
- il vero modulo CLI del plugin può restare lazy e registrarsi alla prima invocazione

Questo permette di mantenere il codice CLI di proprietà del plugin all'interno del plugin stesso, lasciando comunque a OpenClaw
la possibilità di riservare i nomi dei comandi root prima del parsing.

Il confine progettuale importante:

- il discovery + la validazione della configurazione devono funzionare a partire dai **metadati di manifest/schema**
  senza eseguire il codice del plugin
- il comportamento di runtime nativo deriva dal percorso `register(api)` del modulo plugin

Questa separazione consente a OpenClaw di validare la configurazione, spiegare i plugin mancanti/disabilitati e
costruire suggerimenti UI/schema prima che il runtime completo sia attivo.

### Plugin di canale e strumento condiviso `message`

I plugin di canale non devono registrare uno strumento separato per inviare/modificare/reagire per
le normali azioni di chat. OpenClaw mantiene un unico strumento `message` condiviso nel core, e
i plugin di canale possiedono il discovery e l'esecuzione specifici del canale dietro di esso.

Il confine attuale è:

- il core possiede l'host dello strumento `message` condiviso, il wiring del prompt, la gestione di sessione/thread
  e il dispatch di esecuzione
- i plugin di canale possiedono il discovery delle azioni con scope, il discovery delle capacità e ogni
  frammento di schema specifico del canale
- i plugin di canale possiedono la grammatica di conversazione di sessione specifica del provider, ad esempio
  come gli id di conversazione codificano gli id dei thread o ereditano dalle conversazioni padre
- i plugin di canale eseguono l'azione finale tramite il loro action adapter

Per i plugin di canale, la superficie SDK è
`ChannelMessageActionAdapter.describeMessageTool(...)`. Questa chiamata unificata di discovery
consente a un plugin di restituire insieme le sue azioni visibili, capacità e contributi di schema
così che questi elementi non divergano.

Il core passa l'ambito di runtime a questo passaggio di discovery. I campi importanti includono:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- `requesterSenderId` inbound fidato

Questo è importante per i plugin sensibili al contesto. Un canale può nascondere o esporre
azioni di messaggio in base all'account attivo, alla stanza/thread/messaggio corrente o
all'identità fidata del richiedente, senza hardcodare rami specifici del canale nello strumento
core `message`.

Per questo motivo le modifiche di routing dell'embedded runner restano lavoro dei plugin: il runner è
responsabile dell'inoltro dell'identità corrente di chat/sessione al confine di discovery del plugin
in modo che lo strumento `message` condiviso esponga la superficie corretta posseduta dal canale
per il turno corrente.

Per gli helper di esecuzione posseduti dal canale, i plugin bundled dovrebbero mantenere il runtime di esecuzione
all'interno dei propri moduli di estensione. Il core non possiede più i runtime delle azioni messaggio
di Discord, Slack, Telegram o WhatsApp sotto `src/agents/tools`.
Non pubblichiamo sottopercorsi separati `plugin-sdk/*-action-runtime`, e i plugin bundled
dovrebbero importare direttamente il proprio codice di runtime locale dai
moduli di loro proprietà.

Lo stesso confine si applica in generale ai seam SDK con nome del provider: il core non dovrebbe
importare barrel di convenienza specifici del canale per Slack, Discord, Signal,
WhatsApp o estensioni simili. Se il core ha bisogno di un comportamento, deve o consumare il
barrel `api.ts` / `runtime-api.ts` del plugin bundled stesso oppure promuovere il bisogno
a una capacità generica ristretta nello SDK condiviso.

Per i poll in particolare, esistono due percorsi di esecuzione:

- `outbound.sendPoll` è la base condivisa per i canali compatibili con il modello comune
  dei poll
- `actions.handleAction("poll")` è il percorso preferito per semantiche di poll specifiche del canale
  o parametri aggiuntivi dei poll

Il core ora rinvia il parsing condiviso dei poll fino a dopo che il dispatch dei poll del plugin ha rifiutato
l'azione, in modo che i gestori di poll posseduti dal plugin possano accettare campi di poll specifici
del canale senza essere bloccati prima dal parser generico dei poll.

Vedi [Pipeline di caricamento](#load-pipeline) per la sequenza completa di avvio.

## Modello di ownership delle capacità

OpenClaw tratta un plugin nativo come il confine di ownership per una **azienda** o una
**funzionalità**, non come un contenitore di integrazioni non correlate.

Questo significa:

- un plugin aziendale dovrebbe di norma possedere tutte le superfici di OpenClaw rivolte a quell'azienda
- un plugin di funzionalità dovrebbe di norma possedere l'intera superficie della funzionalità che introduce
- i canali dovrebbero consumare capacità condivise del core invece di reimplementare
  il comportamento del provider in modo ad hoc

Esempi:

- il plugin bundled `openai` possiede il comportamento del model provider OpenAI e il comportamento OpenAI
  per voce + voce realtime + comprensione dei media + generazione di immagini
- il plugin bundled `elevenlabs` possiede il comportamento vocale ElevenLabs
- il plugin bundled `microsoft` possiede il comportamento vocale Microsoft
- il plugin bundled `google` possiede il comportamento del model provider Google insieme al comportamento Google
  per comprensione dei media + generazione di immagini + ricerca web
- il plugin bundled `firecrawl` possiede il comportamento web-fetch Firecrawl
- i plugin bundled `minimax`, `mistral`, `moonshot` e `zai` possiedono i loro
  backend di comprensione dei media
- il plugin `voice-call` è un plugin di funzionalità: possiede trasporto delle chiamate, strumenti,
  CLI, route e bridging dei media stream Twilio, ma consuma capacità condivise di voce
  più trascrizione realtime e voce realtime invece di importare direttamente plugin dei vendor

Lo stato finale previsto è:

- OpenAI vive in un unico plugin anche se copre modelli testuali, voce, immagini e
  video futuri
- un altro vendor può fare lo stesso per la propria area di superficie
- i canali non si preoccupano di quale plugin vendor possieda il provider; consumano il
  contratto di capacità condiviso esposto dal core

Questa è la distinzione chiave:

- **plugin** = confine di ownership
- **capacità** = contratto del core che più plugin possono implementare o consumare

Quindi se OpenClaw aggiunge un nuovo dominio come il video, la prima domanda non è
"quale provider dovrebbe hardcodare la gestione video?" La prima domanda è "qual è
il contratto core della capacità video?" Una volta che quel contratto esiste, i plugin vendor
possono registrarsi su di esso e i plugin di canale/funzionalità possono consumarlo.

Se la capacità non esiste ancora, la mossa corretta di solito è:

1. definire la capacità mancante nel core
2. esporla tramite l'API/runtime dei plugin in modo tipizzato
3. collegare canali/funzionalità a quella capacità
4. lasciare che i plugin vendor registrino le implementazioni

Questo mantiene esplicita l'ownership evitando al contempo un comportamento del core che dipende da un
singolo vendor o da un percorso di codice specifico di un singolo plugin.

### Stratificazione delle capacità

Usa questo modello mentale per decidere dove deve stare il codice:

- **livello delle capacità del core**: orchestrazione condivisa, policy, fallback, regole di merge
  della configurazione, semantica di consegna e contratti tipizzati
- **livello del plugin vendor**: API specifiche del vendor, autenticazione, cataloghi di modelli, sintesi vocale,
  generazione di immagini, backend video futuri, endpoint di utilizzo
- **livello del plugin di canale/funzionalità**: integrazione Slack/Discord/voice-call/ecc.
  che consuma capacità del core e le presenta su una superficie

Per esempio, il TTS segue questa forma:

- il core possiede policy TTS al momento della risposta, ordine di fallback, preferenze e consegna sul canale
- `openai`, `elevenlabs` e `microsoft` possiedono le implementazioni di sintesi
- `voice-call` consuma l'helper di runtime TTS per telefonia

Lo stesso schema dovrebbe essere preferito per le capacità future.

### Esempio di plugin aziendale multi-capacità

Un plugin aziendale dovrebbe risultare coerente dall'esterno. Se OpenClaw ha contratti condivisi
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
- il core continua a possedere i contratti delle capacità
- i plugin di canale e di funzionalità consumano helper `api.runtime.*`, non codice del vendor
- i test di contratto possono verificare che il plugin abbia registrato le capacità che
  dichiara di possedere

### Esempio di capacità: comprensione video

OpenClaw tratta già la comprensione di immagini/audio/video come una singola
capacità condivisa. Lo stesso modello di ownership si applica qui:

1. il core definisce il contratto di media-understanding
2. i plugin vendor registrano `describeImage`, `transcribeAudio` e
   `describeVideo` a seconda dei casi
3. i plugin di canale e di funzionalità consumano il comportamento condiviso del core invece di
   collegarsi direttamente al codice del vendor

Questo evita di incorporare nel core le assunzioni video di un singolo provider. Il plugin possiede
la superficie del vendor; il core possiede il contratto della capacità e il comportamento di fallback.

La generazione video segue già la stessa sequenza: il core possiede il contratto tipizzato
della capacità e l'helper di runtime, e i plugin vendor registrano
implementazioni `api.registerVideoGenerationProvider(...)` rispetto ad essa.

Ti serve una checklist concreta per il rollout? Vedi
[Capability Cookbook](/it/plugins/architecture).

## Contratti e applicazione

La superficie API dei plugin è intenzionalmente tipizzata e centralizzata in
`OpenClawPluginApi`. Questo contratto definisce i punti di registrazione supportati e
gli helper di runtime su cui un plugin può fare affidamento.

Perché è importante:

- gli autori di plugin hanno un unico standard interno stabile
- il core può rifiutare ownership duplicate come due plugin che registrano lo stesso
  provider id
- l'avvio può esporre diagnostica utile per registrazioni malformate
- i test di contratto possono imporre l'ownership dei plugin bundled e prevenire derive silenziose

Esistono due livelli di applicazione:

1. **applicazione della registrazione a runtime**
   Il registry dei plugin valida le registrazioni mentre i plugin vengono caricati. Esempi:
   id provider duplicati, id provider vocali duplicati e registrazioni
   malformate producono diagnostica del plugin invece di comportamento indefinito.
2. **test di contratto**
   I plugin bundled vengono acquisiti in registry di contratto durante l'esecuzione dei test, così
   OpenClaw può verificare esplicitamente l'ownership. Oggi questo viene usato per model
   provider, speech provider, web search provider e ownership delle registrazioni bundled.

L'effetto pratico è che OpenClaw sa in anticipo quale plugin possiede quale
superficie. Questo consente a core e canali di comporsi senza attriti perché l'ownership è
dichiarata, tipizzata e testabile anziché implicita.

### Cosa appartiene a un contratto

I buoni contratti dei plugin sono:

- tipizzati
- piccoli
- specifici per capacità
- posseduti dal core
- riutilizzabili da più plugin
- consumabili da canali/funzionalità senza conoscenza del vendor

I cattivi contratti dei plugin sono:

- policy specifiche del vendor nascoste nel core
- vie di fuga ad hoc di un singolo plugin che aggirano il registry
- codice del canale che entra direttamente in un'implementazione del vendor
- oggetti di runtime ad hoc che non fanno parte di `OpenClawPluginApi` o
  `api.runtime`

In caso di dubbio, alza il livello di astrazione: definisci prima la capacità, poi
lascia che i plugin vi si colleghino.

## Modello di esecuzione

I plugin OpenClaw nativi vengono eseguiti **in-process** con il Gateway. Non sono
sandboxed. Un plugin nativo caricato ha lo stesso confine di fiducia a livello di processo del
codice core.

Implicazioni:

- un plugin nativo può registrare strumenti, handler di rete, hook e servizi
- un bug in un plugin nativo può far crashare o destabilizzare il gateway
- un plugin nativo malevolo equivale a esecuzione di codice arbitrario all'interno
  del processo OpenClaw

I bundle compatibili sono più sicuri per impostazione predefinita perché OpenClaw attualmente li tratta
come pacchetti di metadati/contenuti. Nelle versioni attuali, questo significa soprattutto
Skills bundled.

Usa allowlist e percorsi espliciti di installazione/caricamento per plugin non bundled. Tratta
i plugin di workspace come codice di sviluppo, non come impostazioni predefinite di produzione.

Per i nomi dei pacchetti workspace bundled, mantieni l'id del plugin ancorato nel nome npm:
`@openclaw/<id>` per impostazione predefinita, oppure un suffisso tipizzato approvato come
`-provider`, `-plugin`, `-speech`, `-sandbox` o `-media-understanding` quando
il pacchetto espone intenzionalmente un ruolo plugin più ristretto.

Nota importante sulla fiducia:

- `plugins.allow` considera affidabili gli **id dei plugin**, non la provenienza della sorgente.
- Un plugin di workspace con lo stesso id di un plugin bundled oscura intenzionalmente
  la copia bundled quando quel plugin di workspace è abilitato/in allowlist.
- Questo è normale e utile per sviluppo locale, test di patch e hotfix.

## Confine di esportazione

OpenClaw esporta capacità, non praticità di implementazione.

Mantieni pubblica la registrazione delle capacità. Riduci le esportazioni helper non contrattuali:

- sottopercorsi helper specifici dei plugin bundled
- sottopercorsi di plumbing runtime non pensati come API pubblica
- helper di convenienza specifici del vendor
- helper di setup/onboarding che sono dettagli di implementazione

Alcuni sottopercorsi helper di plugin bundled restano ancora nella mappa di esportazione SDK generata
per compatibilità e manutenzione dei plugin bundled. Esempi attuali includono
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` e vari seam `plugin-sdk/matrix*`. Trattali come
esportazioni riservate di dettaglio implementativo, non come schema SDK consigliato per
nuovi plugin di terze parti.

## Pipeline di caricamento

All'avvio, OpenClaw fa approssimativamente questo:

1. scopre le radici dei plugin candidati
2. legge manifest nativi o di bundle compatibili e metadati del pacchetto
3. rifiuta i candidati non sicuri
4. normalizza la configurazione dei plugin (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. decide l'abilitazione per ogni candidato
6. carica i moduli nativi abilitati tramite jiti
7. chiama gli hook nativi `register(api)` (o `activate(api)` — alias legacy) e raccoglie le registrazioni nel registry dei plugin
8. espone il registry alle superfici dei comandi/runtime

<Note>
`activate` è un alias legacy di `register` — il loader risolve quale dei due è presente (`def.register ?? def.activate`) e lo chiama nello stesso punto. Tutti i plugin bundled usano `register`; per i nuovi plugin, preferisci `register`.
</Note>

I gate di sicurezza avvengono **prima** dell'esecuzione runtime. I candidati vengono bloccati
quando l'entry esce dalla radice del plugin, il percorso è scrivibile da tutti o
l'ownership del percorso appare sospetta per i plugin non bundled.

### Comportamento manifest-first

Il manifest è la fonte di verità del control plane. OpenClaw lo usa per:

- identificare il plugin
- scoprire canali/Skills/schema di configurazione dichiarati o capacità del bundle
- validare `plugins.entries.<id>.config`
- arricchire etichette/segnaposto della Control UI
- mostrare metadati di installazione/catalogo

Per i plugin nativi, il modulo runtime è la parte data-plane. Registra
il comportamento effettivo come hook, strumenti, comandi o flussi provider.

### Cosa memorizza in cache il loader

OpenClaw mantiene brevi cache in-process per:

- risultati del discovery
- dati del registry dei manifest
- registry dei plugin caricati

Queste cache riducono i picchi all'avvio e il sovraccarico dei comandi ripetuti. È corretto
considerarle come cache prestazionali di breve durata, non persistenza.

Nota sulle prestazioni:

- Imposta `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` oppure
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` per disabilitare queste cache.
- Regola le finestre delle cache con `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` e
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Modello del registry

I plugin caricati non mutano direttamente variabili globali casuali del core. Si registrano in un
registry centrale dei plugin.

Il registry tiene traccia di:

- record dei plugin (identità, sorgente, origine, stato, diagnostica)
- strumenti
- hook legacy e hook tipizzati
- canali
- provider
- handler Gateway RPC
- route HTTP
- registrar CLI
- servizi in background
- comandi di proprietà del plugin

Le funzionalità del core leggono quindi da quel registry invece di parlare direttamente con i moduli
plugin. Questo mantiene il caricamento unidirezionale:

- modulo plugin -> registrazione nel registry
- runtime core -> consumo del registry

Questa separazione è importante per la manutenibilità. Significa che la maggior parte delle superfici del core ha bisogno di
un solo punto di integrazione: "leggere il registry", non "gestire casi speciali per ogni modulo plugin".

## Callback di binding della conversazione

I plugin che associano una conversazione possono reagire quando un'approvazione viene risolta.

Usa `api.onConversationBindingResolved(...)` per ricevere una callback dopo che una richiesta di binding è stata approvata o negata:

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
- `request`: il riepilogo della richiesta originale, suggerimento di detach, sender id e
  metadati della conversazione

Questa callback è solo di notifica. Non cambia chi è autorizzato ad associare una
conversazione e viene eseguita dopo il completamento della gestione dell'approvazione da parte del core.

## Hook di runtime del provider

I plugin provider ora hanno due livelli:

- metadati del manifest: `providerAuthEnvVars` per un lookup economico dell'autenticazione provider via env
  prima del caricamento del runtime, `providerAuthAliases` per varianti provider che condividono
  l'autenticazione, `channelEnvVars` per un lookup economico env/setup del canale prima del caricamento del runtime,
  più `providerAuthChoices` per etichette economiche di onboarding/scelta autenticazione e
  metadati dei flag CLI prima del caricamento del runtime
- hook di tempo-configurazione: `catalog` / legacy `discovery` più `applyConfigDefaults`
- hook di runtime: `normalizeModelId`, `normalizeTransport`,
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

OpenClaw continua a possedere il loop generico dell'agente, il failover, la gestione delle trascrizioni e
la policy degli strumenti. Questi hook sono la superficie di estensione per il comportamento specifico del provider senza
richiedere un intero trasporto di inferenza personalizzato.

Usa il manifest `providerAuthEnvVars` quando il provider dispone di credenziali basate su env
che i percorsi generici di autenticazione/stato/selettore modelli devono vedere senza caricare il runtime del plugin.
Usa il manifest `providerAuthAliases` quando un provider id deve riutilizzare
env var, profili di autenticazione, autenticazione supportata da configurazione e scelta di onboarding con API key di un altro provider id.
Usa il manifest `providerAuthChoices` quando le superfici CLI di onboarding/scelta autenticazione
devono conoscere choice id del provider, etichette di gruppo e semplice
wiring di autenticazione a un solo flag senza caricare il runtime del provider. Mantieni nel runtime provider
`envVars` per suggerimenti rivolti all'operatore come etichette di onboarding o variabili di setup
client-id/client-secret OAuth.

Usa il manifest `channelEnvVars` quando un canale ha autenticazione o setup guidati da env che
fallback generico shell-env, controlli config/status o prompt di setup devono vedere
senza caricare il runtime del canale.

### Ordine e utilizzo degli hook

Per i plugin modello/provider, OpenClaw chiama gli hook in questo ordine approssimativo.
La colonna "Quando usarlo" è la guida rapida alla decisione.

| #   | Hook                              | Cosa fa                                                                                                         | Quando usarlo                                                                                                                              |
| --- | --------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | `catalog`                         | Pubblica la configurazione del provider in `models.providers` durante la generazione di `models.json`          | Il provider possiede un catalogo o valori predefiniti di base URL                                                                          |
| 2   | `applyConfigDefaults`             | Applica valori predefiniti globali di configurazione del provider durante la materializzazione della configurazione | I valori predefiniti dipendono da modalità auth, env o semantica della famiglia di modelli del provider                                   |
| --  | _(ricerca del modello integrata)_ | OpenClaw prova prima il normale percorso registry/catalog                                                       | _(non è un hook di plugin)_                                                                                                                |
| 3   | `normalizeModelId`                | Normalizza alias legacy o di anteprima degli id dei modelli prima del lookup                                   | Il provider possiede la pulizia degli alias prima della risoluzione del modello canonico                                                   |
| 4   | `normalizeTransport`              | Normalizza `api` / `baseUrl` della famiglia di provider prima dell'assemblaggio generico del modello           | Il provider possiede la pulizia del trasporto per provider id personalizzati nella stessa famiglia di trasporto                           |
| 5   | `normalizeConfig`                 | Normalizza `models.providers.<id>` prima della risoluzione runtime/provider                                    | Il provider ha bisogno di pulizia della configurazione che dovrebbe vivere con il plugin; gli helper bundled della famiglia Google coprono anche le entry di configurazione Google supportate |
| 6   | `applyNativeStreamingUsageCompat` | Applica riscritture di compatibilità native streaming-usage ai provider di configurazione                      | Il provider ha bisogno di correzioni dei metadati di utilizzo streaming native guidate dall'endpoint                                      |
| 7   | `resolveConfigApiKey`             | Risolve auth con marcatore env per i provider di configurazione prima del caricamento auth di runtime         | Il provider possiede una risoluzione di API key con marcatore env; anche `amazon-bedrock` dispone qui di un resolver integrato per marcatori env AWS |
| 8   | `resolveSyntheticAuth`            | Espone auth locale/self-hosted o supportata da configurazione senza persistere testo in chiaro                | Il provider può operare con un marcatore di credenziale sintetica/locale                                                                   |
| 9   | `resolveExternalAuthProfiles`     | Sovrappone profili di autenticazione esterni di proprietà del provider; `persistence` predefinita è `runtime-only` per credenziali di proprietà CLI/app | Il provider riutilizza credenziali di autenticazione esterne senza persistere refresh token copiati                                       |
| 10  | `shouldDeferSyntheticProfileAuth` | Declassa i placeholder di profilo sintetici memorizzati dietro auth supportata da env/config                  | Il provider memorizza profili placeholder sintetici che non dovrebbero avere precedenza                                                    |
| 11  | `resolveDynamicModel`             | Fallback sincrono per model id di proprietà del provider non ancora presenti nel registry locale              | Il provider accetta id di modelli upstream arbitrari                                                                                       |
| 12  | `prepareDynamicModel`             | Warm-up asincrono, poi `resolveDynamicModel` viene eseguito di nuovo                                           | Il provider ha bisogno di metadati di rete prima di risolvere id sconosciuti                                                              |
| 13  | `normalizeResolvedModel`          | Riscrittura finale prima che l'embedded runner usi il modello risolto                                          | Il provider necessita di riscritture del trasporto ma usa comunque un trasporto core                                                      |
| 14  | `contributeResolvedModelCompat`   | Contribuisce flag di compatibilità per modelli vendor dietro un altro trasporto compatibile                   | Il provider riconosce i propri modelli su trasporti proxy senza prendere il controllo del provider                                        |
| 15  | `capabilities`                    | Metadati posseduti dal provider su trascrizioni/strumenti usati dalla logica core condivisa                   | Il provider necessita di particolarità della famiglia provider/trascrizione                                                                |
| 16  | `normalizeToolSchemas`            | Normalizza gli schema degli strumenti prima che l'embedded runner li veda                                      | Il provider ha bisogno di pulizia degli schema per famiglia di trasporto                                                                   |
| 17  | `inspectToolSchemas`              | Espone diagnostica di schema di proprietà del provider dopo la normalizzazione                                 | Il provider vuole avvisi sulle keyword senza insegnare al core regole specifiche del provider                                              |
| 18  | `resolveReasoningOutputMode`      | Seleziona il contratto di output del reasoning nativo o con tag                                               | Il provider ha bisogno di output tagged reasoning/finale invece di campi nativi                                                            |
| 19  | `prepareExtraParams`              | Normalizzazione dei parametri di richiesta prima dei wrapper generici delle opzioni di stream                  | Il provider ha bisogno di parametri predefiniti di richiesta o pulizia per-provider dei parametri                                         |
| 20  | `createStreamFn`                  | Sostituisce completamente il normale percorso di stream con un trasporto personalizzato                        | Il provider necessita di un protocollo wire personalizzato, non solo di un wrapper                                                         |
| 21  | `wrapStreamFn`                    | Wrapper dello stream dopo l'applicazione dei wrapper generici                                                  | Il provider necessita di wrapper di compatibilità per header/body/modello della richiesta senza un trasporto personalizzato               |
| 22  | `resolveTransportTurnState`       | Allega header o metadati nativi per-turn del trasporto                                                         | Il provider vuole che i trasporti generici inviino identità native del turno del provider                                                  |
| 23  | `resolveWebSocketSessionPolicy`   | Allega header WebSocket nativi o policy di raffreddamento della sessione                                       | Il provider vuole che i trasporti WS generici regolino header di sessione o policy di fallback                                            |
| 24  | `formatApiKey`                    | Formatter del profilo auth: il profilo memorizzato diventa la stringa `apiKey` di runtime                     | Il provider memorizza metadati auth aggiuntivi e necessita di una forma personalizzata del token di runtime                               |
| 25  | `refreshOAuth`                    | Override del refresh OAuth per endpoint di refresh personalizzati o policy sui fallimenti di refresh           | Il provider non si adatta ai refresher condivisi `pi-ai`                                                                                   |
| 26  | `buildAuthDoctorHint`             | Suggerimento di riparazione aggiunto quando il refresh OAuth fallisce                                          | Il provider necessita di guida di riparazione auth di sua proprietà dopo un fallimento di refresh                                         |
| 27  | `matchesContextOverflowError`     | Matcher posseduto dal provider per overflow della finestra di contesto                                         | Il provider ha errori raw di overflow che le euristiche generiche non rileverebbero                                                       |
| 28  | `classifyFailoverReason`          | Classificazione della ragione di failover posseduta dal provider                                               | Il provider può mappare errori raw API/trasporto a rate-limit/sovraccarico/ecc.                                                           |
| 29  | `isCacheTtlEligible`              | Policy di prompt-cache per provider proxy/backhaul                                                             | Il provider ha bisogno di gating TTL della cache specifico del proxy                                                                       |
| 30  | `buildMissingAuthMessage`         | Sostituzione del messaggio generico di recupero in caso di auth mancante                                       | Il provider ha bisogno di un suggerimento di recupero per auth mancante specifico del provider                                             |
| 31  | `suppressBuiltInModel`            | Soppressione di modelli upstream obsoleti più eventuale suggerimento di errore rivolto all'utente            | Il provider ha bisogno di nascondere righe upstream obsolete o sostituirle con un suggerimento del vendor                                 |
| 32  | `augmentModelCatalog`             | Righe di catalogo sintetiche/finali aggiunte dopo il discovery                                                 | Il provider ha bisogno di righe sintetiche forward-compat in `models list` e nei picker                                                    |
| 33  | `isBinaryThinking`                | Toggle reasoning on/off per provider a thinking binario                                                        | Il provider espone solo thinking binario on/off                                                                                            |
| 34  | `supportsXHighThinking`           | Supporto al reasoning `xhigh` per modelli selezionati                                                          | Il provider vuole `xhigh` solo su un sottoinsieme di modelli                                                                               |
| 35  | `resolveDefaultThinkingLevel`     | Livello `/think` predefinito per una specifica famiglia di modelli                                             | Il provider possiede la policy `/think` predefinita per una famiglia di modelli                                                            |
| 36  | `isModernModelRef`                | Matcher di modello moderno per filtri di profilo live e selezione smoke                                        | Il provider possiede il matching del modello preferito live/smoke                                                                          |
| 37  | `prepareRuntimeAuth`              | Scambia una credenziale configurata con il vero token/chiave di runtime subito prima dell'inferenza          | Il provider necessita di uno scambio token o di una credenziale di richiesta di breve durata                                               |
| 38  | `resolveUsageAuth`                | Risolve le credenziali di utilizzo/fatturazione per `/usage` e relative superfici di stato                    | Il provider necessita di parsing personalizzato del token di utilizzo/quota o di una credenziale di utilizzo diversa                      |
| 39  | `fetchUsageSnapshot`              | Recupera e normalizza snapshot di utilizzo/quota specifici del provider dopo la risoluzione dell'auth        | Il provider necessita di un endpoint di utilizzo o parser payload specifico del provider                                                   |
| 40  | `createEmbeddingProvider`         | Costruisce un adapter embedding di proprietà del provider per memoria/ricerca                                  | Il comportamento di memory embedding appartiene al plugin provider                                                                         |
| 41  | `buildReplayPolicy`               | Restituisce una policy di replay che controlla la gestione delle trascrizioni per il provider                 | Il provider necessita di una policy personalizzata per le trascrizioni (ad esempio, rimozione dei thinking block)                         |
| 42  | `sanitizeReplayHistory`           | Riscrive la cronologia replay dopo la pulizia generica delle trascrizioni                                      | Il provider necessita di riscritture specifiche del replay oltre agli helper condivisi di compattazione                                   |
| 43  | `validateReplayTurns`             | Validazione o rimodellazione finale dei turni replay prima dell'embedded runner                                | Il trasporto provider necessita di una validazione più severa dei turni dopo la sanificazione generica                                    |
| 44  | `onModelSelected`                 | Esegue effetti collaterali post-selezione posseduti dal provider                                               | Il provider necessita di telemetria o stato posseduto dal provider quando un modello diventa attivo                                       |

`normalizeModelId`, `normalizeTransport` e `normalizeConfig` controllano prima il
plugin provider corrispondente, poi passano agli altri plugin provider con capacità di hook
finché uno non cambia davvero model id o transport/config. Questo mantiene funzionanti
shim alias/compat dei provider senza richiedere al chiamante di sapere quale plugin
bundled possieda la riscrittura. Se nessun hook provider riscrive una entry di configurazione supportata
della famiglia Google, il normalizzatore di configurazione Google bundled continua comunque ad applicare
quella pulizia di compatibilità.

Se il provider ha bisogno di un protocollo wire completamente personalizzato o di un esecutore di richieste personalizzato,
quella è una classe diversa di estensione. Questi hook sono per il comportamento del provider
che continua a funzionare sul normale loop di inferenza di OpenClaw.

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
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`
  e `wrapStreamFn` perché possiede forward-compat di Claude 4.6,
  suggerimenti della famiglia provider, guida alla riparazione auth, integrazione
  dell'endpoint di utilizzo, idoneità della prompt-cache, valori predefiniti di configurazione consapevoli dell'auth,
  policy di thinking predefinito/adattivo di Claude, e modellazione
  dello stream specifica di Anthropic per header beta, `/fast` / `serviceTier` e `context1m`.
- Gli helper di stream specifici di Claude per Anthropic restano per ora nel seam pubblico
  `api.ts` / `contract-api.ts` del plugin bundled. Questa superficie del pacchetto
  esporta `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` e i builder wrapper
  Anthropic di livello più basso invece di ampliare lo SDK generico attorno alle regole degli header beta di un solo provider.
- OpenAI usa `resolveDynamicModel`, `normalizeResolvedModel` e
  `capabilities` più `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` e `isModernModelRef`
  perché possiede forward-compat di GPT-5.4, la normalizzazione diretta OpenAI
  `openai-completions` -> `openai-responses`, suggerimenti auth consapevoli di Codex,
  soppressione di Spark, righe sintetiche della lista OpenAI, e policy di thinking /
  modello live di GPT-5; la famiglia di stream `openai-responses-defaults` possiede i
  wrapper condivisi nativi OpenAI Responses per header di attribuzione,
  `/fast`/`serviceTier`, verbosità del testo, ricerca web nativa Codex,
  modellazione del payload reasoning-compat e gestione del contesto Responses.
- OpenRouter usa `catalog` più `resolveDynamicModel` e
  `prepareDynamicModel` perché il provider è pass-through e può esporre nuovi
  model id prima dell'aggiornamento del catalogo statico di OpenClaw; usa anche
  `capabilities`, `wrapStreamFn` e `isCacheTtlEligible` per mantenere fuori dal core
  header di richiesta specifici del provider, metadati di routing, patch di reasoning e
  policy di prompt-cache. La sua policy di replay proviene dalla famiglia
  `passthrough-gemini`, mentre la famiglia di stream `openrouter-thinking`
  possiede l'iniezione del reasoning del proxy e gli skip per modelli non supportati / `auto`.
- GitHub Copilot usa `catalog`, `auth`, `resolveDynamicModel` e
  `capabilities` più `prepareRuntimeAuth` e `fetchUsageSnapshot` perché ha
  bisogno di login device di proprietà del provider, comportamento di fallback del modello,
  particolarità delle trascrizioni Claude, uno scambio GitHub token -> Copilot token,
  e un endpoint di utilizzo posseduto dal provider.
- OpenAI Codex usa `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` e `augmentModelCatalog` più
  `prepareExtraParams`, `resolveUsageAuth` e `fetchUsageSnapshot` perché
  funziona ancora sui trasporti OpenAI del core ma possiede la propria normalizzazione di
  trasporto/base URL, la policy di fallback del refresh OAuth, la scelta predefinita del trasporto,
  righe sintetiche del catalogo Codex e integrazione dell'endpoint di utilizzo ChatGPT; condivide la stessa famiglia di stream `openai-responses-defaults` di OpenAI diretto.
- Google AI Studio e Gemini CLI OAuth usano `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` e `isModernModelRef` perché la famiglia replay `google-gemini`
  possiede fallback forward-compat di Gemini 3.1,
  validazione replay nativa Gemini, sanificazione del replay bootstrap, modalità
  di output del reasoning con tag e matching dei modelli moderni, mentre la
  famiglia di stream `google-thinking` possiede la normalizzazione del payload di thinking di Gemini;
  Gemini CLI OAuth usa anche `formatApiKey`, `resolveUsageAuth` e
  `fetchUsageSnapshot` per formattazione del token, parsing del token e
  wiring dell'endpoint quota.
- Anthropic Vertex usa `buildReplayPolicy` tramite la famiglia replay
  `anthropic-by-model` così la pulizia replay specifica di Claude resta limitata
  agli id Claude invece che a ogni trasporto `anthropic-messages`.
- Amazon Bedrock usa `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` e `resolveDefaultThinkingLevel` perché possiede la classificazione specifica Bedrock
  degli errori di throttle/not-ready/context-overflow per traffico Anthropic-on-Bedrock;
  la sua policy di replay condivide comunque la stessa protezione solo-Claude `anthropic-by-model`.
- OpenRouter, Kilocode, Opencode e Opencode Go usano `buildReplayPolicy`
  tramite la famiglia replay `passthrough-gemini` perché fanno proxy dei modelli Gemini
  attraverso trasporti compatibili OpenAI e necessitano della sanificazione delle
  thought-signature Gemini senza validazione replay nativa Gemini o riscritture bootstrap.
- MiniMax usa `buildReplayPolicy` tramite la famiglia replay
  `hybrid-anthropic-openai` perché un singolo provider possiede semantiche sia
  Anthropic-message sia OpenAI-compatible; mantiene la rimozione dei thinking-block solo-Claude
  sul lato Anthropic sovrascrivendo però la modalità di output del reasoning di nuovo su nativa, e la famiglia di stream `minimax-fast-mode` possiede le riscritture dei modelli fast-mode sul percorso di stream condiviso.
- Moonshot usa `catalog` più `wrapStreamFn` perché usa ancora il trasporto
  OpenAI condiviso ma necessita di normalizzazione del payload di thinking di proprietà del provider; la
  famiglia di stream `moonshot-thinking` mappa config più stato `/think` sul proprio payload nativo di thinking binario.
- Kilocode usa `catalog`, `capabilities`, `wrapStreamFn` e
  `isCacheTtlEligible` perché necessita di header di richiesta di proprietà del provider,
  normalizzazione del payload di reasoning, suggerimenti sulle trascrizioni Gemini e gating
  Anthropic cache-TTL; la famiglia di stream `kilocode-thinking` mantiene l'iniezione del thinking Kilo
  sul percorso stream proxy condiviso saltando `kilo/auto` e altri model id proxy
  che non supportano payload di reasoning espliciti.
- Z.AI usa `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` e `fetchUsageSnapshot` perché possiede fallback GLM-5,
  valori predefiniti `tool_stream`, UX a thinking binario, matching di modelli moderni, e sia
  l'auth di utilizzo sia il recupero della quota; la famiglia di stream `tool-stream-default-on` mantiene
  il wrapper `tool_stream` attivo per impostazione predefinita fuori dal glue scritto a mano per provider.
- xAI usa `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` e `isModernModelRef`
  perché possiede la normalizzazione nativa del trasporto xAI Responses, riscritture degli alias
  Grok fast-mode, `tool_stream` predefinito, pulizia di strict-tool / reasoning-payload,
  riuso dell'auth di fallback per strumenti posseduti dal plugin, risoluzione
  forward-compat dei modelli Grok, e patch di compatibilità di proprietà del provider come
  profilo schema strumento xAI, keyword di schema non supportate, `web_search`
  nativo e decodifica degli argomenti delle tool-call con entità HTML.
- Mistral, OpenCode Zen e OpenCode Go usano solo `capabilities` per mantenere
  fuori dal core le particolarità di trascrizioni/strumenti.
- I provider bundled solo-catalogo come `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` e `volcengine` usano
  solo `catalog`.
- Qwen usa `catalog` per il proprio provider testuale più registrazioni condivise di
  media-understanding e video-generation per le sue superfici multimodali.
- MiniMax e Xiaomi usano `catalog` più hook di utilizzo perché il loro comportamento `/usage`
  è di proprietà del plugin anche se l'inferenza continua a passare attraverso i trasporti condivisi.

## Helper di runtime

I plugin possono accedere a helper selezionati del core tramite `api.runtime`. Per il TTS:

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

- `textToSpeech` restituisce il normale payload di output TTS del core per superfici file/nota vocale.
- Usa la configurazione core `messages.tts` e la selezione del provider.
- Restituisce buffer audio PCM + sample rate. I plugin devono ricampionare/codificare per i provider.
- `listVoices` è facoltativo per provider. Usalo per picker vocali o flussi di setup posseduti dal vendor.
- Gli elenchi vocali possono includere metadati più ricchi come locale, genere e tag di personalità per picker consapevoli del provider.
- OpenAI ed ElevenLabs supportano oggi la telefonia. Microsoft no.

I plugin possono anche registrare provider vocali tramite `api.registerSpeechProvider(...)`.

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
- Usa i provider vocali per il comportamento di sintesi di proprietà del vendor.
- L'input legacy Microsoft `edge` viene normalizzato all'id provider `microsoft`.
- Il modello di ownership preferito è orientato all'azienda: un singolo plugin vendor può possedere
  provider testuali, vocali, di immagini e di media futuri man mano che OpenClaw aggiunge quei
  contratti di capacità.

Per la comprensione di immagini/audio/video, i plugin registrano un singolo
provider tipizzato di media-understanding invece di un generico contenitore chiave/valore:

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

- Mantieni nel core orchestrazione, fallback, configurazione e wiring dei canali.
- Mantieni nel plugin provider il comportamento del vendor.
- L'espansione additiva deve restare tipizzata: nuovi metodi facoltativi, nuovi campi facoltativi del risultato, nuove capacità facoltative.
- La generazione video segue già lo stesso schema:
  - il core possiede il contratto della capacità e l'helper di runtime
  - i plugin vendor registrano `api.registerVideoGenerationProvider(...)`
  - i plugin di funzionalità/canale consumano `api.runtime.videoGeneration.*`

Per gli helper di runtime di media-understanding, i plugin possono chiamare:

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

Per la trascrizione audio, i plugin possono usare il runtime media-understanding
oppure il vecchio alias STT:

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
- Usa la configurazione core audio di media-understanding (`tools.media.audio`) e l'ordine di fallback dei provider.
- Restituisce `{ text: undefined }` quando non viene prodotto output di trascrizione (ad esempio input saltato/non supportato).
- `api.runtime.stt.transcribeAudioFile(...)` rimane come alias di compatibilità.

I plugin possono anche avviare esecuzioni di subagent in background tramite `api.runtime.subagent`:

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

- `provider` e `model` sono override facoltativi per esecuzione, non modifiche persistenti della sessione.
- OpenClaw onora quei campi di override solo per chiamanti fidati.
- Per esecuzioni di fallback possedute dal plugin, gli operatori devono aderire esplicitamente con `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Usa `plugins.entries.<id>.subagent.allowedModels` per limitare i plugin fidati a target canonici specifici `provider/model`, oppure `"*"` per consentire esplicitamente qualsiasi target.
- Le esecuzioni subagent di plugin non fidati continuano a funzionare, ma le richieste di override vengono rifiutate invece di ricadere silenziosamente su un fallback.

Per la ricerca web, i plugin possono consumare l'helper di runtime condiviso invece di
entrare nel wiring degli strumenti dell'agente:

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

I plugin possono anche registrare provider di ricerca web tramite
`api.registerWebSearchProvider(...)`.

Note:

- Mantieni nel core la selezione del provider, la risoluzione delle credenziali e la semantica condivisa delle richieste.
- Usa i provider di ricerca web per trasporti di ricerca specifici del vendor.
- `api.runtime.webSearch.*` è la superficie condivisa preferita per plugin di funzionalità/canale che hanno bisogno del comportamento di ricerca senza dipendere dal wrapper degli strumenti dell'agente.

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

- `generate(...)`: genera un'immagine usando la catena di provider di generazione immagini configurata.
- `listProviders(...)`: elenca i provider di generazione immagini disponibili e le loro capacità.

## Route HTTP del Gateway

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
- `auth`: obbligatorio. Usa `"gateway"` per richiedere la normale autenticazione del gateway, oppure `"plugin"` per autenticazione/verifica webhook gestite dal plugin.
- `match`: facoltativo. `"exact"` (predefinito) oppure `"prefix"`.
- `replaceExisting`: facoltativo. Consente allo stesso plugin di sostituire la propria registrazione di route esistente.
- `handler`: restituisce `true` quando la route ha gestito la richiesta.

Note:

- `api.registerHttpHandler(...)` è stato rimosso e causerà un errore di caricamento del plugin. Usa invece `api.registerHttpRoute(...)`.
- Le route dei plugin devono dichiarare esplicitamente `auth`.
- I conflitti esatti `path + match` vengono rifiutati a meno che `replaceExisting: true`, e un plugin non può sostituire la route di un altro plugin.
- Le route sovrapposte con diversi livelli `auth` vengono rifiutate. Mantieni catene di fallthrough `exact`/`prefix` solo allo stesso livello auth.
- Le route `auth: "plugin"` **non** ricevono automaticamente ambiti di runtime dell'operatore. Sono pensate per webhook/verifica firme gestiti dal plugin, non per chiamate helper Gateway privilegiate.
- Le route `auth: "gateway"` vengono eseguite all'interno di un ambito di runtime di richiesta Gateway, ma tale ambito è intenzionalmente conservativo:
  - l'autenticazione bearer con segreto condiviso (`gateway.auth.mode = "token"` / `"password"`) mantiene gli ambiti di runtime delle route plugin fissati a `operator.write`, anche se il chiamante invia `x-openclaw-scopes`
  - le modalità HTTP fidate con identità (ad esempio `trusted-proxy` o `gateway.auth.mode = "none"` su ingress privato) onorano `x-openclaw-scopes` solo quando l'header è esplicitamente presente
  - se `x-openclaw-scopes` è assente su quelle richieste di route plugin con identità, l'ambito di runtime ricade su `operator.write`
- Regola pratica: non dare per scontato che una route plugin con auth gateway sia implicitamente una superficie admin. Se la tua route ha bisogno di comportamento solo-admin, richiedi una modalità auth con identità e documenta il contratto esplicito dell'header `x-openclaw-scopes`.

## Percorsi di import del Plugin SDK

Usa i sottopercorsi dell'SDK invece dell'import monolitico `openclaw/plugin-sdk` quando
sviluppi plugin:

- `openclaw/plugin-sdk/plugin-entry` per primitive di registrazione dei plugin.
- `openclaw/plugin-sdk/core` per il contratto condiviso generico rivolto ai plugin.
- `openclaw/plugin-sdk/config-schema` per l'esportazione dello schema Zod radice `openclaw.json`
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
  `openclaw/plugin-sdk/webhook-ingress` per wiring condiviso di setup/auth/reply/webhook.
  `channel-inbound` è la sede condivisa per debounce, matching delle mention,
  helper di mention-policy inbound, formattazione dell'envelope e helper di contesto dell'envelope inbound.
  `channel-setup` è il seam ristretto di setup con installazione facoltativa.
  `setup-runtime` è la superficie di setup sicura per il runtime usata da `setupEntry` /
  avvio differito, compresi gli adapter di patch di setup sicuri per l'import.
  `setup-adapter-runtime` è il seam adapter di setup account consapevole dell'env.
  `setup-tools` è il piccolo seam helper CLI/archivio/documentazione (`formatCliCommand`,
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
  `openclaw/plugin-sdk/directory-runtime` per helper condivisi di runtime/configurazione.
  `telegram-command-config` è il seam pubblico ristretto per normalizzazione/validazione dei comandi personalizzati Telegram e resta disponibile anche se la superficie contrattuale bundled di Telegram è temporaneamente indisponibile.
  `text-runtime` è il seam condiviso per testo/markdown/logging, compresa
  la rimozione del testo visibile all'assistente, helper di rendering/chunking markdown, helper di redazione, helper di directive-tag e utilità di testo sicuro.
- I seam di canale specifici per l'approvazione dovrebbero preferire un unico contratto `approvalCapability` sul plugin. Il core legge quindi autenticazione, consegna, rendering, native-routing e comportamento lazy del native-handler per l'approvazione tramite questa unica capacità invece di mescolare il comportamento di approvazione in campi non correlati del plugin.
- `openclaw/plugin-sdk/channel-runtime` è deprecato e rimane solo come shim di compatibilità per plugin più vecchi. Il nuovo codice dovrebbe importare invece le primitive generiche più ristrette, e il codice del repo non dovrebbe aggiungere nuovi import dello shim.
- Gli interni delle estensioni bundled restano privati. I plugin esterni dovrebbero usare solo i sottopercorsi `openclaw/plugin-sdk/*`. Il codice core/test di OpenClaw può usare gli entry point pubblici del repo sotto la radice di un pacchetto plugin come `index.js`, `api.js`, `runtime-api.js`, `setup-entry.js` e file a scope ristretto come `login-qr-api.js`. Non importare mai `src/*` di un pacchetto plugin dal core o da un'altra estensione.
- Suddivisione degli entry point del repo:
  `<plugin-package-root>/api.js` è il barrel helper/tipi,
  `<plugin-package-root>/runtime-api.js` è il barrel solo-runtime,
  `<plugin-package-root>/index.js` è l'entry del plugin bundled,
  e `<plugin-package-root>/setup-entry.js` è l'entry del plugin di setup.
- Esempi attuali di provider bundled:
  - Anthropic usa `api.js` / `contract-api.js` per helper di stream Claude come
    `wrapAnthropicProviderStream`, helper per header beta e parsing di `service_tier`.
  - OpenAI usa `api.js` per builder provider, helper per il modello predefinito e
    builder provider realtime.
  - OpenRouter usa `api.js` per il proprio builder provider più helper di onboarding/configurazione,
    mentre `register.runtime.js` può comunque riesportare helper generici
    `plugin-sdk/provider-stream` per uso locale al repo.
- Gli entry point pubblici caricati tramite facade preferiscono lo snapshot attivo della configurazione runtime
  quando esiste, poi ricadono sul file di configurazione risolto su disco quando
  OpenClaw non sta ancora servendo uno snapshot runtime.
- Le primitive generiche condivise restano il contratto pubblico preferito dello SDK. Esiste ancora un piccolo insieme riservato di compatibilità di seam helper con marchio dei canali bundled. Trattali come seam di manutenzione/compatibilità dei bundled, non come nuovi target di import per terze parti; i nuovi contratti cross-channel dovrebbero comunque approdare su sottopercorsi generici `plugin-sdk/*` o sui barrel locali `api.js` / `runtime-api.js` del plugin.

Nota di compatibilità:

- Evita il barrel root `openclaw/plugin-sdk` per il nuovo codice.
- Preferisci prima le primitive stabili ristrette. I più recenti sottopercorsi di setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool sono il contratto previsto per il nuovo lavoro su plugin
  bundled ed esterni.
  Il parsing/matching dei target appartiene a `openclaw/plugin-sdk/channel-targets`.
  I gate per le azioni messaggio e gli helper per message-id delle reaction appartengono a
  `openclaw/plugin-sdk/channel-actions`.
- I barrel helper specifici delle estensioni bundled non sono stabili per impostazione predefinita. Se un
  helper serve solo a un'estensione bundled, mantienilo dietro il seam locale
  `api.js` o `runtime-api.js` dell'estensione invece di promuoverlo in
  `openclaw/plugin-sdk/<extension>`.
- I nuovi seam helper condivisi dovrebbero essere generici, non con marchio del canale. Il parsing condiviso dei target appartiene a `openclaw/plugin-sdk/channel-targets`; gli interni specifici del canale restano dietro il seam locale `api.js` o `runtime-api.js` del plugin proprietario.
- Sottopercorsi specifici per capacità come `image-generation`,
  `media-understanding` e `speech` esistono perché i plugin bundled/nativi li usano
  oggi. La loro presenza non significa di per sé che ogni helper esportato sia un contratto esterno congelato a lungo termine.

## Schema dello strumento `message`

I plugin dovrebbero possedere i contributi di schema specifici del canale di `describeMessageTool(...)`.
Mantieni i campi specifici del provider nel plugin, non nel core condiviso.

Per frammenti di schema portabili condivisi, riusa gli helper generici esportati tramite
`openclaw/plugin-sdk/channel-actions`:

- `createMessageToolButtonsSchema()` per payload in stile griglia di pulsanti
- `createMessageToolCardSchema()` per payload di card strutturata

Se una forma di schema ha senso solo per un provider, definiscila nel sorgente
di quel plugin invece di promuoverla nello SDK condiviso.

## Risoluzione del target del canale

I plugin di canale dovrebbero possedere la semantica dei target specifica del canale. Mantieni
generico l'host outbound condiviso e usa la superficie dell'adapter di messaggistica per le regole del provider:

- `messaging.inferTargetChatType({ to })` decide se un target normalizzato
  debba essere trattato come `direct`, `group` o `channel` prima del lookup di directory.
- `messaging.targetResolver.looksLikeId(raw, normalized)` dice al core se un
  input deve saltare direttamente alla risoluzione tipo-id invece che alla ricerca in directory.
- `messaging.targetResolver.resolveTarget(...)` è il fallback del plugin quando
  il core ha bisogno di una risoluzione finale posseduta dal provider dopo la normalizzazione o dopo un miss della directory.
- `messaging.resolveOutboundSessionRoute(...)` possiede la costruzione della route di sessione outbound specifica del provider una volta che un target è stato risolto.

Suddivisione consigliata:

- Usa `inferTargetChatType` per decisioni di categoria che devono avvenire prima
  della ricerca di peer/gruppi.
- Usa `looksLikeId` per controlli tipo "tratta questo come un id target esplicito/nativo".
- Usa `resolveTarget` per fallback di normalizzazione specifici del provider, non per
  ricerca ampia nella directory.
- Mantieni id nativi del provider come chat id, thread id, JID, handle e room
  id all'interno dei valori `target` o di parametri specifici del provider, non in campi generici dell'SDK.

## Directory supportate da configurazione

I plugin che derivano voci di directory dalla configurazione dovrebbero mantenere quella logica nel
plugin e riutilizzare gli helper condivisi di
`openclaw/plugin-sdk/directory-runtime`.

Usa questo schema quando un canale ha peer/gruppi supportati da configurazione come:

- peer DM guidati da allowlist
- mappe configurate di canali/gruppi
- fallback statici di directory con scope account

Gli helper condivisi in `directory-runtime` gestiscono solo operazioni generiche:

- filtraggio delle query
- applicazione dei limiti
- deduplica/helper di normalizzazione
- costruzione di `ChannelDirectoryEntry[]`

L'ispezione account specifica del canale e la normalizzazione degli id dovrebbero restare
nell'implementazione del plugin.

## Cataloghi provider

I plugin provider possono definire cataloghi di modelli per l'inferenza con
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` restituisce la stessa forma che OpenClaw scrive in
`models.providers`:

- `{ provider }` per una singola entry provider
- `{ providers }` per più entry provider

Usa `catalog` quando il plugin possiede model id specifici del provider, valori predefiniti di base URL o metadati dei modelli protetti da auth.

`catalog.order` controlla quando il catalogo di un plugin viene unito rispetto ai provider impliciti integrati di OpenClaw:

- `simple`: provider semplici con API key o guidati da env
- `profile`: provider che compaiono quando esistono profili auth
- `paired`: provider che sintetizzano più entry provider correlate
- `late`: ultimo passaggio, dopo gli altri provider impliciti

I provider successivi vincono in caso di collisione di chiave, quindi i plugin possono intenzionalmente
sovrascrivere una entry provider integrata con lo stesso provider id.

Compatibilità:

- `discovery` continua a funzionare come alias legacy
- se sono registrati sia `catalog` sia `discovery`, OpenClaw usa `catalog`

## Ispezione di canale in sola lettura

Se il tuo plugin registra un canale, preferisci implementare
`plugin.config.inspectAccount(cfg, accountId)` insieme a `resolveAccount(...)`.

Perché:

- `resolveAccount(...)` è il percorso runtime. Può presumere che le credenziali
  siano completamente materializzate e può fallire rapidamente quando mancano segreti richiesti.
- I percorsi di comando in sola lettura come `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` e i flussi doctor/config
  repair non dovrebbero aver bisogno di materializzare credenziali di runtime solo per
  descrivere la configurazione.

Comportamento consigliato per `inspectAccount(...)`:

- Restituisci solo lo stato descrittivo dell'account.
- Conserva `enabled` e `configured`.
- Includi campi di origine/stato delle credenziali quando rilevanti, come:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Non è necessario restituire i valori raw dei token solo per riportare la disponibilità in sola lettura. Restituire `tokenStatus: "available"` (e il campo di origine corrispondente) è sufficiente per comandi in stile status.
- Usa `configured_unavailable` quando una credenziale è configurata tramite SecretRef ma non disponibile nel percorso di comando corrente.

Questo consente ai comandi in sola lettura di riportare "configurato ma non disponibile in questo percorso di comando" invece di andare in crash o riportare in modo errato l'account come non configurato.

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

Ogni entry diventa un plugin. Se il pack elenca più estensioni, l'id plugin
diventa `name/<fileBase>`.

Se il tuo plugin importa dipendenze npm, installale in quella directory in modo che
`node_modules` sia disponibile (`npm install` / `pnpm install`).

Guardrail di sicurezza: ogni entry `openclaw.extensions` deve restare all'interno della directory plugin
dopo la risoluzione dei symlink. Le entry che escono dalla directory del pacchetto vengono
rifiutate.

Nota di sicurezza: `openclaw plugins install` installa le dipendenze dei plugin con
`npm install --omit=dev --ignore-scripts` (nessuno script di lifecycle, nessuna dipendenza dev a runtime). Mantieni gli alberi di dipendenze dei plugin "pure JS/TS" ed evita pacchetti che richiedono build in `postinstall`.

Facoltativo: `openclaw.setupEntry` può puntare a un modulo leggero solo-setup.
Quando OpenClaw ha bisogno di superfici di setup per un plugin di canale disabilitato, oppure
quando un plugin di canale è abilitato ma ancora non configurato, carica `setupEntry`
invece dell'entry completa del plugin. Questo rende avvio e setup più leggeri
quando l'entry principale del plugin collega anche strumenti, hook o altro codice
solo-runtime.

Facoltativo: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
può far aderire un plugin di canale allo stesso percorso `setupEntry` durante la fase
di avvio pre-listen del gateway, anche quando il canale è già configurato.

Usa questa opzione solo quando `setupEntry` copre completamente la superficie di avvio che deve esistere
prima che il gateway inizi ad ascoltare. In pratica, ciò significa che l'entry di setup
deve registrare ogni capacità posseduta dal canale da cui dipende l'avvio, come:

- la registrazione del canale stesso
- eventuali route HTTP che devono essere disponibili prima che il gateway inizi ad ascoltare
- eventuali metodi Gateway, strumenti o servizi che devono esistere durante quella stessa finestra

Se la tua entry completa possiede ancora una capacità di avvio richiesta, non abilitare
questo flag. Mantieni il comportamento predefinito del plugin e lascia che OpenClaw carichi
l'entry completa durante l'avvio.

I canali bundled possono anche pubblicare helper di superficie contrattuale solo-setup che il core
può consultare prima che il runtime completo del canale venga caricato. L'attuale superficie
di promozione del setup è:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Il core usa questa superficie quando ha bisogno di promuovere una configurazione legacy di canale
single-account in `channels.<id>.accounts.*` senza caricare l'entry completa del plugin.
Matrix è l'esempio bundled attuale: sposta solo chiavi di auth/bootstrap in un
account promosso con nome quando esistono già account con nome, e può preservare una
chiave default-account configurata non canonica invece di creare sempre
`accounts.default`.

Quegli adapter di patch di setup mantengono lazy il discovery della superficie contrattuale bundled. Il tempo
di import resta leggero; la superficie di promozione viene caricata solo al primo uso invece di rientrare nell'avvio del canale bundled durante l'import del modulo.

Quando quelle superfici di avvio includono metodi Gateway RPC, mantienile su un
prefisso specifico del plugin. Gli spazi dei nomi admin del core (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) restano riservati e si risolvono sempre
a `operator.admin`, anche se un plugin richiede un ambito più ristretto.

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
suggerimenti di installazione tramite `openclaw.install`. Questo mantiene i dati del catalogo liberi dal core.

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

- `detailLabel`: etichetta secondaria per superfici di catalogo/stato più ricche
- `docsLabel`: sovrascrive il testo del link alla documentazione
- `preferOver`: id di plugin/canale a priorità inferiore che questa entry di catalogo dovrebbe superare
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: controlli di testo per la superficie di selezione
- `markdownCapable`: contrassegna il canale come compatibile con Markdown per le decisioni di formattazione outbound
- `exposure.configured`: nasconde il canale dalle superfici di elenco dei canali configurati quando è impostato a `false`
- `exposure.setup`: nasconde il canale dai picker interattivi di setup/configurazione quando è impostato a `false`
- `exposure.docs`: contrassegna il canale come interno/privato per le superfici di navigazione della documentazione
- `showConfigured` / `showInSetup`: alias legacy ancora accettati per compatibilità; preferisci `exposure`
- `quickstartAllowFrom`: fa aderire il canale al flusso standard quickstart `allowFrom`
- `forceAccountBinding`: richiede binding esplicito dell'account anche quando esiste un solo account
- `preferSessionLookupForAnnounceTarget`: preferisce il lookup di sessione quando si risolvono target di annuncio

OpenClaw può anche unire **cataloghi di canali esterni** (ad esempio un export di
registry MPM). Inserisci un file JSON in uno di questi percorsi:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Oppure punta `OPENCLAW_PLUGIN_CATALOG_PATHS` (o `OPENCLAW_MPM_CATALOG_PATHS`) a
uno o più file JSON (delimitati da virgola/punto e virgola/`PATH`). Ogni file dovrebbe
contenere `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. Il parser accetta anche `"packages"` o `"plugins"` come alias legacy per la chiave `"entries"`.

## Plugin del motore di contesto

I plugin del motore di contesto possiedono l'orchestrazione del contesto di sessione per ingestione, assemblaggio
e compattazione. Registrali dal tuo plugin con
`api.registerContextEngine(id, factory)`, poi seleziona il motore attivo con
`plugins.slots.contextEngine`.

Usa questo schema quando il tuo plugin deve sostituire o estendere la pipeline di contesto predefinita invece di limitarsi ad aggiungere memory search o hook.

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

## Aggiunta di una nuova capacità

Quando un plugin ha bisogno di un comportamento che non rientra nell'API attuale, non aggirare
il sistema dei plugin con un accesso privato. Aggiungi la capacità mancante.

Sequenza consigliata:

1. definisci il contratto del core
   Decidi quale comportamento condiviso debba possedere il core: policy, fallback, merge della configurazione,
   lifecycle, semantica rivolta ai canali e forma dell'helper di runtime.
2. aggiungi superfici tipizzate di registrazione/runtime dei plugin
   Estendi `OpenClawPluginApi` e/o `api.runtime` con la superficie di capacità tipizzata più piccola utile.
3. collega i consumer di core + canale/funzionalità
   I canali e i plugin di funzionalità dovrebbero consumare la nuova capacità tramite il core,
   non importando direttamente un'implementazione vendor.
4. registra le implementazioni vendor
   I plugin vendor registrano quindi i loro backend rispetto alla capacità.
5. aggiungi copertura di contratto
   Aggiungi test in modo che ownership e forma di registrazione restino esplicite nel tempo.

È così che OpenClaw resta opinato senza diventare hardcoded secondo la visione del mondo di un
singolo provider. Vedi il [Capability Cookbook](/it/plugins/architecture)
per una checklist concreta dei file e un esempio completo.

### Checklist della capacità

Quando aggiungi una nuova capacità, l'implementazione di solito dovrebbe toccare insieme
queste superfici:

- tipi di contratto core in `src/<capability>/types.ts`
- runner/helper di runtime core in `src/<capability>/runtime.ts`
- superficie di registrazione dell'API plugin in `src/plugins/types.ts`
- wiring del registry dei plugin in `src/plugins/registry.ts`
- esposizione runtime dei plugin in `src/plugins/runtime/*` quando i plugin di funzionalità/canale hanno bisogno di consumarla
- helper di acquisizione/test in `src/test-utils/plugin-registration.ts`
- asserzioni di ownership/contratto in `src/plugins/contracts/registry.ts`
- documentazione per operatori/plugin in `docs/`

Se una di queste superfici manca, di solito è il segnale che la capacità non è ancora completamente integrata.

### Modello di capacità

Schema minimo:

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

Schema del test di contratto:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Questo mantiene semplice la regola:

- il core possiede il contratto della capacità + l'orchestrazione
- i plugin vendor possiedono le implementazioni del vendor
- i plugin di funzionalità/canale consumano gli helper di runtime
- i test di contratto mantengono esplicita l'ownership
