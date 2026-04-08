---
x-i18n:
    generated_at: "2026-04-08T06:01:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4a9066b2a939c5a9ba69141d75405f0e8097997b523164340e2f0e9a0d5060dd
    source_path: refactor/qa.md
    workflow: 15
---

# Refactor di QA

Stato: migrazione fondamentale completata.

## Obiettivo

Spostare il sistema QA di OpenClaw da un modello a definizione suddivisa a un'unica fonte di verità:

- metadati degli scenari
- prompt inviati al modello
- setup e teardown
- logica dell'harness
- asserzioni e criteri di successo
- artifact e suggerimenti per i report

Lo stato finale desiderato è un harness QA generico che carichi file di definizione degli scenari potenti invece di hardcodare la maggior parte del comportamento in TypeScript.

## Stato attuale

La fonte primaria di verità ora si trova in `qa/scenarios/index.md` più un file per
ogni scenario in `qa/scenarios/*.md`.

Implementato:

- `qa/scenarios/index.md`
  - metadati canonici del pacchetto QA
  - identità dell'operatore
  - missione di avvio
- `qa/scenarios/*.md`
  - un file markdown per scenario
  - metadati dello scenario
  - binding degli handler
  - configurazione di esecuzione specifica dello scenario
- `extensions/qa-lab/src/scenario-catalog.ts`
  - parser del pacchetto markdown + validazione zod
- `extensions/qa-lab/src/qa-agent-bootstrap.ts`
  - rendering del piano dal pacchetto markdown
- `extensions/qa-lab/src/qa-agent-workspace.ts`
  - genera file di compatibilità iniziali più `QA_SCENARIOS.md`
- `extensions/qa-lab/src/suite.ts`
  - seleziona gli scenari eseguibili tramite binding degli handler definiti nel markdown
- protocollo QA bus + UI
  - allegati inline generici per il rendering di immagini/video/audio/file

Superfici ancora suddivise:

- `extensions/qa-lab/src/suite.ts`
  - possiede ancora la maggior parte della logica eseguibile degli handler personalizzati
- `extensions/qa-lab/src/report.ts`
  - ricava ancora la struttura del report dagli output di runtime

Quindi la divisione della fonte di verità è stata risolta, ma l'esecuzione è ancora per lo più basata su handler invece di essere completamente dichiarativa.

## Come appare davvero la superficie degli scenari

Leggere la suite attuale mostra alcune classi distinte di scenari.

### Interazione semplice

- baseline del canale
- baseline DM
- follow-up in thread
- cambio di modello
- completamento dell'approvazione
- reazione/modifica/eliminazione

### Configurazione e mutazione del runtime

- patch di config con disabilitazione delle Skills
- config apply con riavvio e wake-up
- inversione della capacità al riavvio della config
- controllo del drift dell'inventario di runtime

### Asserzioni su filesystem e repository

- report di rilevamento source/docs
- build di Lobster Invaders
- ricerca di artifact di immagini generate

### Orchestrazione della memoria

- richiamo della memoria
- strumenti di memoria nel contesto del canale
- fallback in caso di errore della memoria
- ranking della memoria di sessione
- isolamento della memoria del thread
- sweep di dreaming della memoria

### Integrazione di tool e plugin

- chiamata MCP plugin-tools
- visibilità delle Skills
- installazione a caldo delle Skills
- generazione nativa di immagini
- roundtrip delle immagini
- comprensione di immagini da allegato

### Multi-turno e multi-attore

- handoff del subagent
- sintesi fanout del subagent
- flussi in stile recupero dopo riavvio

Queste categorie sono importanti perché guidano i requisiti della DSL. Un elenco piatto di prompt + testo atteso non è sufficiente.

## Direzione

### Unica fonte di verità

Usare `qa/scenarios/index.md` più `qa/scenarios/*.md` come fonte di verità
scritta.

Il pacchetto deve rimanere:

- leggibile dagli umani in review
- analizzabile dalle macchine
- sufficientemente ricco da guidare:
  - esecuzione della suite
  - bootstrap dello spazio di lavoro QA
  - metadati dell'interfaccia QA Lab
  - prompt per documentazione/discovery
  - generazione dei report

### Formato di authoring preferito

Usare markdown come formato di livello superiore, con YAML strutturato al suo interno.

Struttura consigliata:

- frontmatter YAML
  - id
  - title
  - surface
  - tags
  - riferimenti docs
  - riferimenti codice
  - override di modello/provider
  - prerequisiti
- sezioni in prosa
  - obiettivo
  - note
  - suggerimenti per il debugging
- blocchi YAML fenced
  - setup
  - steps
  - assertions
  - cleanup

Questo offre:

- migliore leggibilità nelle PR rispetto a enormi file JSON
- contesto più ricco rispetto al solo YAML
- parsing rigoroso e validazione zod

Il JSON grezzo è accettabile solo come formato intermedio generato.

## Forma proposta del file di scenario

Esempio:

````md
---
id: image-generation-roundtrip
title: Image generation roundtrip
surface: image
tags: [media, image, roundtrip]
models:
  primary: openai/gpt-5.4
requires:
  tools: [image_generate]
  plugins: [openai, qa-channel]
docsRefs:
  - docs/help/testing.md
  - docs/concepts/model-providers.md
codeRefs:
  - extensions/qa-lab/src/suite.ts
  - src/gateway/chat-attachments.ts
---

# Objective

Verify generated media is reattached on the follow-up turn.

# Setup

```yaml scenario.setup
- action: config.patch
  patch:
    agents:
      defaults:
        imageGenerationModel:
          primary: openai/gpt-image-1
- action: session.create
  key: agent:qa:image-roundtrip
```

# Steps

```yaml scenario.steps
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Image generation check: generate a QA lighthouse image and summarize it in one short sentence.
- action: artifact.capture
  kind: generated-image
  promptSnippet: Image generation check
  saveAs: lighthouseImage
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Roundtrip image inspection check: describe the generated lighthouse attachment in one short sentence.
  attachments:
    - fromArtifact: lighthouseImage
```

# Expect

```yaml scenario.expect
- assert: outbound.textIncludes
  value: lighthouse
- assert: requestLog.matches
  where:
    promptIncludes: Roundtrip image inspection check
  imageInputCountGte: 1
- assert: artifact.exists
  ref: lighthouseImage
```
````

## Capacità del runner che la DSL deve coprire

In base alla suite attuale, il runner generico ha bisogno di più della semplice esecuzione dei prompt.

### Azioni di ambiente e setup

- `bus.reset`
- `gateway.waitHealthy`
- `channel.waitReady`
- `session.create`
- `thread.create`
- `workspace.writeSkill`

### Azioni di turno dell'agente

- `agent.send`
- `agent.wait`
- `bus.injectInbound`
- `bus.injectOutbound`

### Azioni di configurazione e runtime

- `config.get`
- `config.patch`
- `config.apply`
- `gateway.restart`
- `tools.effective`
- `skills.status`

### Azioni su file e artifact

- `file.write`
- `file.read`
- `file.delete`
- `file.touchTime`
- `artifact.captureGeneratedImage`
- `artifact.capturePath`

### Azioni su memoria e cron

- `memory.indexForce`
- `memory.searchCli`
- `doctor.memory.status`
- `cron.list`
- `cron.run`
- `cron.waitCompletion`
- `sessionTranscript.write`

### Azioni MCP

- `mcp.callTool`

### Asserzioni

- `outbound.textIncludes`
- `outbound.inThread`
- `outbound.notInRoot`
- `tool.called`
- `tool.notPresent`
- `skill.visible`
- `skill.disabled`
- `file.contains`
- `memory.contains`
- `requestLog.matches`
- `sessionStore.matches`
- `cron.managedPresent`
- `artifact.exists`

## Variabili e riferimenti agli artifact

La DSL deve supportare output salvati e riferimenti successivi.

Esempi dalla suite attuale:

- creare un thread, poi riutilizzare `threadId`
- creare una sessione, poi riutilizzare `sessionKey`
- generare un'immagine, poi allegare il file al turno successivo
- generare una stringa marcatore di wake, poi verificare che compaia in seguito

Capacità necessarie:

- `saveAs`
- `${vars.name}`
- `${artifacts.name}`
- riferimenti tipizzati per percorsi, chiavi di sessione, id dei thread, marcatori, output dei tool

Senza supporto per le variabili, l'harness continuerà a far rifluire la logica degli scenari in TypeScript.

## Cosa dovrebbe restare come via di fuga

Un runner completamente dichiarativo non è realistico nella fase 1.

Alcuni scenari sono intrinsecamente pesanti sul piano dell'orchestrazione:

- sweep di dreaming della memoria
- config apply con riavvio e wake-up
- inversione della capacità al riavvio della config
- risoluzione dell'artifact di immagine generato per timestamp/percorso
- valutazione del discovery-report

Per ora, questi dovrebbero usare handler personalizzati espliciti.

Regola consigliata:

- 85-90% dichiarativo
- passaggi `customHandler` espliciti per la parte restante più difficile
- solo handler personalizzati nominati e documentati
- nessun codice inline anonimo nel file di scenario

Questo mantiene pulito il motore generico pur consentendo comunque progressi.

## Cambiamento architetturale

### Attuale

Il markdown degli scenari è già la fonte di verità per:

- esecuzione della suite
- file bootstrap dello spazio di lavoro
- catalogo degli scenari dell'interfaccia QA Lab
- metadati dei report
- prompt di discovery

Compatibilità generata:

- lo spazio di lavoro inizializzato include ancora `QA_KICKOFF_TASK.md`
- lo spazio di lavoro inizializzato include ancora `QA_SCENARIO_PLAN.md`
- lo spazio di lavoro inizializzato ora include anche `QA_SCENARIOS.md`

## Piano di refactor

### Fase 1: loader e schema

Fatto.

- aggiunto `qa/scenarios/index.md`
- suddivisi gli scenari in `qa/scenarios/*.md`
- aggiunto il parser per il contenuto YAML markdown nominato del pacchetto
- validato con zod
- passati i consumer al pacchetto analizzato
- rimossi `qa/seed-scenarios.json` e `qa/QA_KICKOFF_TASK.md` a livello di repository

### Fase 2: motore generico

- suddividere `extensions/qa-lab/src/suite.ts` in:
  - loader
  - motore
  - registry delle azioni
  - registry delle asserzioni
  - handler personalizzati
- mantenere le funzioni helper esistenti come operazioni del motore

Deliverable:

- il motore esegue scenari dichiarativi semplici

Iniziare con scenari che sono soprattutto prompt + attesa + asserzione:

- follow-up in thread
- comprensione di immagini da allegato
- visibilità e invocazione delle Skills
- baseline del canale

Deliverable:

- primi scenari reali definiti nel markdown distribuiti tramite il motore generico

### Fase 4: migrare scenari di media complessità

- roundtrip di generazione di immagini
- strumenti di memoria nel contesto del canale
- ranking della memoria di sessione
- handoff del subagent
- sintesi fanout del subagent

Deliverable:

- variabili, artifact, asserzioni sui tool e asserzioni sul request log verificati nella pratica

### Fase 5: mantenere gli scenari difficili su handler personalizzati

- sweep di dreaming della memoria
- config apply con riavvio e wake-up
- inversione della capacità al riavvio della config
- drift dell'inventario di runtime

Deliverable:

- stesso formato di authoring, ma con blocchi di passaggi personalizzati espliciti dove necessario

### Fase 6: eliminare la mappa degli scenari hardcoded

Quando la copertura del pacchetto sarà sufficientemente buona:

- rimuovere la maggior parte della logica TypeScript specifica per scenario da `extensions/qa-lab/src/suite.ts`

## Supporto Fake Slack / Rich Media

L'attuale QA bus è orientato principalmente al testo.

File rilevanti:

- `extensions/qa-channel/src/protocol.ts`
- `extensions/qa-lab/src/bus-state.ts`
- `extensions/qa-lab/src/bus-queries.ts`
- `extensions/qa-lab/src/bus-server.ts`
- `extensions/qa-lab/web/src/ui-render.ts`

Oggi il QA bus supporta:

- testo
- reazioni
- thread

Non modella ancora gli allegati multimediali inline.

### Contratto di trasporto necessario

Aggiungere un modello generico di allegato QA bus:

```ts
type QaBusAttachment = {
  id: string;
  kind: "image" | "video" | "audio" | "file";
  mimeType: string;
  fileName?: string;
  inline?: boolean;
  url?: string;
  contentBase64?: string;
  width?: number;
  height?: number;
  durationMs?: number;
  altText?: string;
  transcript?: string;
};
```

Poi aggiungere `attachments?: QaBusAttachment[]` a:

- `QaBusMessage`
- `QaBusInboundMessageInput`
- `QaBusOutboundMessageInput`

### Perché prima il generico

Non costruire un modello media solo per Slack.

Invece:

- un unico modello di trasporto QA generico
- più renderer costruiti sopra di esso
  - chat attuale di QA Lab
  - futuro fake Slack web
  - qualsiasi altra vista di trasporto fittizio

Questo evita la logica duplicata e permette agli scenari multimediali di restare agnostici rispetto al trasporto.

### Lavoro UI necessario

Aggiornare l'interfaccia QA per renderizzare:

- anteprima immagine inline
- player audio inline
- player video inline
- chip per allegato file

L'interfaccia attuale può già renderizzare thread e reazioni, quindi il rendering degli allegati dovrebbe stratificarsi sullo stesso modello di scheda messaggio.

### Lavoro sugli scenari abilitato dal trasporto media

Una volta che gli allegati fluiscono attraverso il QA bus, possiamo aggiungere scenari fake-chat più ricchi:

- risposta con immagine inline in fake Slack
- comprensione di allegati audio
- comprensione di allegati video
- ordinamento misto degli allegati
- risposta in thread con media mantenuti

## Raccomandazione

Il prossimo blocco di implementazione dovrebbe essere:

1. aggiungere loader degli scenari markdown + schema zod
2. generare il catalogo attuale dal markdown
3. migrare prima alcuni scenari semplici
4. aggiungere supporto generico agli allegati QA bus
5. renderizzare immagini inline nell'interfaccia QA
6. poi estendere ad audio e video

Questo è il percorso più piccolo che dimostra entrambi gli obiettivi:

- QA generico definito nel markdown
- superfici di messaggistica fittizia più ricche

## Questioni aperte

- se i file di scenario debbano consentire template di prompt markdown incorporati con interpolazione di variabili
- se setup/cleanup debbano essere sezioni nominate o semplicemente elenchi ordinati di azioni
- se i riferimenti agli artifact debbano essere fortemente tipizzati nello schema o basati su stringhe
- se gli handler personalizzati debbano risiedere in un unico registry o in registry per superficie
- se il file di compatibilità JSON generato debba restare versionato durante la migrazione
