---
x-i18n:
    generated_at: "2026-04-08T02:18:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0e156cc8e2fe946a0423862f937754a7caa1fe7e6863b50a80bff49a1c86e1e8
    source_path: refactor/qa.md
    workflow: 15
---

# Refactor QA

Stato: migrazione fondamentale completata.

## Obiettivo

Spostare la QA di OpenClaw da un modello a definizione suddivisa a una singola fonte di verità:

- metadati dello scenario
- prompt inviati al modello
- setup e teardown
- logica dell'harness
- asserzioni e criteri di successo
- artifact e suggerimenti per il report

Lo stato finale desiderato è un harness QA generico che carica potenti file di definizione degli scenari invece di codificare rigidamente la maggior parte del comportamento in TypeScript.

## Stato attuale

La fonte di verità primaria ora si trova in `qa/scenarios.md`.

Implementato:

- `qa/scenarios.md`
  - pack QA canonico
  - identità dell'operatore
  - missione di kickoff
  - metadati dello scenario
  - binding degli handler
- `extensions/qa-lab/src/scenario-catalog.ts`
  - parser del pack Markdown + validazione zod
- `extensions/qa-lab/src/qa-agent-bootstrap.ts`
  - rendering del piano dal pack Markdown
- `extensions/qa-lab/src/qa-agent-workspace.ts`
  - inizializza file di compatibilità generati più `QA_SCENARIOS.md`
- `extensions/qa-lab/src/suite.ts`
  - seleziona scenari eseguibili tramite binding degli handler definiti nel Markdown
- Protocollo bus QA + UI
  - allegati inline generici per il rendering di immagini/video/audio/file

Superfici ancora suddivise:

- `extensions/qa-lab/src/suite.ts`
  - gestisce ancora la maggior parte della logica eseguibile degli handler personalizzati
- `extensions/qa-lab/src/report.ts`
  - deriva ancora la struttura del report dagli output di runtime

Quindi la divisione della fonte di verità è stata corretta, ma l'esecuzione è ancora per lo più supportata da handler anziché essere completamente dichiarativa.

## Che aspetto ha realmente la superficie degli scenari

Leggendo la suite attuale si vedono alcune classi distinte di scenari.

### Interazione semplice

- baseline del canale
- baseline DM
- follow-up in thread
- cambio modello
- completamento dell'approvazione
- reaction/edit/delete

### Mutazione di configurazione e runtime

- config patch skill disable
- config apply restart wake-up
- config restart capability flip
- controllo del drift dell'inventario runtime

### Asserzioni su filesystem e repository

- report di individuazione source/docs
- build Lobster Invaders
- lookup di artifact immagine generata

### Orchestrazione della memoria

- memory recall
- strumenti di memoria nel contesto del canale
- fallback in caso di errore della memoria
- ranking della memoria di sessione
- isolamento della memoria del thread
- sweep di dreaming della memoria

### Integrazione di tool e plugin

- chiamata MCP plugin-tools
- visibilità delle Skills
- installazione a caldo delle skill
- generazione nativa di immagini
- roundtrip delle immagini
- comprensione di immagini da allegato

### Multi-turn e multi-attore

- handoff a subagent
- sintesi fanout del subagent
- flussi in stile recovery dopo riavvio

Queste categorie sono importanti perché guidano i requisiti della DSL. Un elenco piatto di prompt + testo atteso non è sufficiente.

## Direzione

### Singola fonte di verità

Usare `qa/scenarios.md` come fonte di verità creata manualmente.

Il pack dovrebbe restare:

- leggibile per gli umani in review
- interpretabile dalla macchina
- abbastanza ricco da guidare:
  - esecuzione della suite
  - bootstrap del workspace QA
  - metadati della UI di QA Lab
  - prompt di docs/discovery
  - generazione del report

### Formato di authoring preferito

Usare Markdown come formato di primo livello, con YAML strutturato al suo interno.

Struttura consigliata:

- YAML frontmatter
  - id
  - title
  - surface
  - tags
  - docs refs
  - code refs
  - override di modello/provider
  - prerequisiti
- sezioni in prosa
  - objective
  - notes
  - debugging hints
- blocchi YAML delimitati
  - setup
  - steps
  - assertions
  - cleanup

Questo offre:

- migliore leggibilità nelle PR rispetto a grandi file JSON
- contesto più ricco rispetto al puro YAML
- parsing rigoroso e validazione zod

Il JSON grezzo è accettabile solo come forma intermedia generata.

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

In base alla suite attuale, il runner generico ha bisogno di più della sola esecuzione dei prompt.

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
- generare una stringa wake marker, poi verificare che compaia più tardi

Capacità necessarie:

- `saveAs`
- `${vars.name}`
- `${artifacts.name}`
- riferimenti tipizzati per percorsi, chiavi di sessione, id thread, marker, output dei tool

Senza supporto per le variabili, l'harness continuerà a far trapelare la logica degli scenari in TypeScript.

## Cosa dovrebbe restare come via di fuga

Un runner completamente dichiarativo puro non è realistico nella fase 1.

Alcuni scenari sono intrinsecamente pesanti dal punto di vista dell'orchestrazione:

- sweep di dreaming della memoria
- config apply restart wake-up
- config restart capability flip
- risoluzione dell'artifact immagine generata tramite timestamp/percorso
- valutazione del discovery-report

Per ora questi dovrebbero usare handler personalizzati espliciti.

Regola consigliata:

- 85-90% dichiarativo
- step `customHandler` espliciti per il resto più difficile
- solo custom handler con nome e documentati
- nessun codice inline anonimo nel file di scenario

Questo mantiene pulito il motore generico pur consentendo di progredire.

## Cambio architetturale

### Attuale

Il Markdown degli scenari è già la fonte di verità per:

- esecuzione della suite
- file di bootstrap del workspace
- catalogo degli scenari della UI di QA Lab
- metadati del report
- prompt di discovery

Compatibilità generata:

- il workspace inizializzato include ancora `QA_KICKOFF_TASK.md`
- il workspace inizializzato include ancora `QA_SCENARIO_PLAN.md`
- il workspace inizializzato ora include anche `QA_SCENARIOS.md`

## Piano di refactor

### Fase 1: loader e schema

Completata.

- aggiunto `qa/scenarios.md`
- aggiunto parser per contenuti pack YAML Markdown con nome
- validato con zod
- passati i consumer al pack parsato
- rimossi `qa/seed-scenarios.json` e `qa/QA_KICKOFF_TASK.md` a livello repository

### Fase 2: motore generico

- dividere `extensions/qa-lab/src/suite.ts` in:
  - loader
  - motore
  - registro delle azioni
  - registro delle asserzioni
  - custom handler
- mantenere le funzioni helper esistenti come operazioni del motore

Deliverable:

- il motore esegue scenari dichiarativi semplici

Iniziare con scenari che sono per lo più prompt + attesa + asserzione:

- follow-up in thread
- comprensione di immagini da allegato
- visibilità e invocazione delle skill
- baseline del canale

Deliverable:

- primi veri scenari definiti in Markdown distribuiti tramite il motore generico

### Fase 4: migrare scenari di media complessità

- roundtrip di generazione immagini
- strumenti di memoria nel contesto del canale
- ranking della memoria di sessione
- handoff a subagent
- sintesi fanout del subagent

Deliverable:

- variabili, artifact, asserzioni sui tool, asserzioni sui request log verificati nella pratica

### Fase 5: mantenere gli scenari difficili su custom handler

- sweep di dreaming della memoria
- config apply restart wake-up
- config restart capability flip
- runtime inventory drift

Deliverable:

- stesso formato di authoring, ma con blocchi di step personalizzati espliciti dove necessario

### Fase 6: eliminare la mappa degli scenari hardcoded

Quando la copertura del pack sarà abbastanza buona:

- rimuovere la maggior parte del branching TypeScript specifico per scenario da `extensions/qa-lab/src/suite.ts`

## Supporto Fake Slack / Rich Media

L'attuale bus QA è incentrato sul testo.

File rilevanti:

- `extensions/qa-channel/src/protocol.ts`
- `extensions/qa-lab/src/bus-state.ts`
- `extensions/qa-lab/src/bus-queries.ts`
- `extensions/qa-lab/src/bus-server.ts`
- `extensions/qa-lab/web/src/ui-render.ts`

Oggi il bus QA supporta:

- testo
- reaction
- thread

Non modella ancora allegati media inline.

### Contratto di transport necessario

Aggiungere un modello generico di allegato per il bus QA:

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

### Perché prima un approccio generico

Non costruire un modello media solo per Slack.

Invece:

- un unico modello di transport QA generico
- più renderer sopra di esso
  - l'attuale chat di QA Lab
  - il futuro fake Slack web
  - qualsiasi altra vista di fake transport

Questo evita logica duplicata e consente agli scenari media di restare indipendenti dal transport.

### Lavoro UI necessario

Aggiornare la UI QA per renderizzare:

- anteprima immagine inline
- player audio inline
- player video inline
- chip allegato file

L'attuale UI può già renderizzare thread e reaction, quindi il rendering degli allegati dovrebbe sovrapporsi allo stesso modello di card dei messaggi.

### Lavoro sugli scenari abilitato dal transport media

Una volta che gli allegati passano attraverso il bus QA, possiamo aggiungere scenari fake-chat più ricchi:

- reply con immagine inline in fake Slack
- comprensione di allegati audio
- comprensione di allegati video
- ordinamento misto degli allegati
- reply in thread con media mantenuti

## Raccomandazione

Il prossimo blocco di implementazione dovrebbe essere:

1. aggiungere loader di scenari Markdown + schema zod
2. generare il catalogo attuale dal Markdown
3. migrare prima alcuni scenari semplici
4. aggiungere supporto generico agli allegati del bus QA
5. renderizzare immagini inline nella UI QA
6. poi espandere ad audio e video

Questo è il percorso più piccolo che dimostra entrambi gli obiettivi:

- QA generica definita in Markdown
- superfici di messaggistica simulata più ricche

## Domande aperte

- se i file di scenario debbano consentire template di prompt Markdown incorporati con interpolazione di variabili
- se setup/cleanup debbano essere sezioni nominate o semplicemente elenchi ordinati di azioni
- se i riferimenti agli artifact debbano essere fortemente tipizzati nello schema o basati su stringhe
- se i custom handler debbano vivere in un unico registro o in registri per superficie
- se il file di compatibilità JSON generato debba restare versionato durante la migrazione
