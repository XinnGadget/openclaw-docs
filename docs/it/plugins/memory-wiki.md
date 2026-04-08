---
read_when:
    - Vuoi una conoscenza persistente oltre alle semplici note MEMORY.md
    - Stai configurando il plugin bundled memory-wiki
    - Vuoi capire wiki_search, wiki_get o la modalità bridge
summary: 'memory-wiki: archivio di conoscenza compilato con provenienza, asserzioni, dashboard e modalità bridge'
title: Wiki della memoria
x-i18n:
    generated_at: "2026-04-08T06:01:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: b78dd6a4ef4451dae6b53197bf0c7c2a2ba846b08e4a3a93c1026366b1598d82
    source_path: plugins/memory-wiki.md
    workflow: 15
---

# Wiki della memoria

`memory-wiki` è un plugin bundled che trasforma la memoria durevole in un
archivio di conoscenza compilato.

**Non** sostituisce il plugin di memoria attivo. Il plugin di memoria attivo
continua a gestire richiamo, promozione, indicizzazione e dreaming. `memory-wiki`
si affianca ad esso e compila la conoscenza durevole in una wiki navigabile con
pagine deterministiche, asserzioni strutturate, provenienza, dashboard e digest
leggibili dalle macchine.

Usalo quando vuoi che la memoria si comporti più come un livello di conoscenza
mantenuto e meno come un insieme di file Markdown.

## Cosa aggiunge

- Un archivio wiki dedicato con layout delle pagine deterministico
- Metadati strutturati per asserzioni ed evidenze, non solo prosa
- Provenienza a livello di pagina, confidenza, contraddizioni e domande aperte
- Digest compilati per i consumer agent/runtime
- Strumenti nativi della wiki per search/get/apply/lint
- Modalità bridge opzionale che importa artefatti pubblici dal plugin di memoria attivo
- Modalità di rendering opzionale compatibile con Obsidian e integrazione CLI

## Come si integra con la memoria

Considera la suddivisione in questo modo:

| Livello                                                 | Gestisce                                                                                   |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Plugin di memoria attivo (`memory-core`, QMD, Honcho, ecc.) | Richiamo, ricerca semantica, promozione, dreaming, runtime della memoria               |
| `memory-wiki`                                           | Pagine wiki compilate, sintesi ricche di provenienza, dashboard, search/get/apply specifici della wiki |

Se il plugin di memoria attivo espone artefatti di richiamo condivisi, OpenClaw può cercare
in entrambi i livelli in un unico passaggio con `memory_search corpus=all`.

Quando ti servono ranking specifico della wiki, provenienza o accesso diretto
alle pagine, usa invece gli strumenti nativi della wiki.

## Modalità dell'archivio

`memory-wiki` supporta tre modalità di archivio:

### `isolated`

Archivio proprio, sorgenti proprie, nessuna dipendenza da `memory-core`.

Usa questa modalità quando vuoi che la wiki sia il proprio archivio di
conoscenza curato.

### `bridge`

Legge artefatti pubblici della memoria ed eventi di memoria dal plugin di memoria attivo
tramite punti di integrazione pubblici del plugin SDK.

Usa questa modalità quando vuoi che la wiki compili e organizzi gli
artefatti esportati dal plugin di memoria senza accedere agli elementi interni
privati del plugin.

La modalità bridge può indicizzare:

- artefatti di memoria esportati
- report di dream
- note giornaliere
- file radice della memoria
- log degli eventi di memoria

### `unsafe-local`

Via di fuga esplicita sulla stessa macchina per percorsi privati locali.

Questa modalità è intenzionalmente sperimentale e non portabile. Usala solo se
comprendi il confine di fiducia e hai bisogno in modo specifico di accesso al
filesystem locale che la modalità bridge non può fornire.

## Layout dell'archivio

Il plugin inizializza un archivio in questo modo:

```text
<vault>/
  AGENTS.md
  WIKI.md
  index.md
  inbox.md
  entities/
  concepts/
  syntheses/
  sources/
  reports/
  _attachments/
  _views/
  .openclaw-wiki/
```

Il contenuto gestito rimane all'interno di blocchi generati. I blocchi di note
umani vengono preservati.

I gruppi principali di pagine sono:

- `sources/` per materiale grezzo importato e pagine supportate dal bridge
- `entities/` per elementi durevoli, persone, sistemi, progetti e oggetti
- `concepts/` per idee, astrazioni, pattern e policy
- `syntheses/` per riepiloghi compilati e rollup mantenuti
- `reports/` per dashboard generate

## Asserzioni ed evidenze strutturate

Le pagine possono includere `claims` nel frontmatter strutturato, non solo testo libero.

Ogni asserzione può includere:

- `id`
- `text`
- `status`
- `confidence`
- `evidence[]`
- `updatedAt`

Le voci di evidenza possono includere:

- `sourceId`
- `path`
- `lines`
- `weight`
- `note`
- `updatedAt`

È questo che fa sì che la wiki si comporti più come un livello di credenze che
come un archivio passivo di note. Le asserzioni possono essere tracciate,
valutate, contestate e ricondotte alle sorgenti.

## Pipeline di compilazione

Il passaggio di compilazione legge le pagine della wiki, normalizza i riepiloghi
ed emette artefatti stabili orientati alle macchine in:

- `.openclaw-wiki/cache/agent-digest.json`
- `.openclaw-wiki/cache/claims.jsonl`

Questi digest esistono affinché gli agent e il codice runtime non debbano fare scraping
delle pagine Markdown.

L'output compilato alimenta anche:

- indicizzazione iniziale della wiki per i flussi di search/get
- lookup degli id delle asserzioni per risalire alle pagine proprietarie
- supplementi compatti per i prompt
- generazione di report/dashboard

## Dashboard e report di stato

Quando `render.createDashboards` è abilitato, la compilazione mantiene le dashboard in `reports/`.

I report integrati includono:

- `reports/open-questions.md`
- `reports/contradictions.md`
- `reports/low-confidence.md`
- `reports/claim-health.md`
- `reports/stale-pages.md`

Questi report tengono traccia di elementi come:

- cluster di note di contraddizione
- cluster di asserzioni concorrenti
- asserzioni prive di evidenze strutturate
- pagine e asserzioni a bassa confidenza
- aggiornamento obsoleto o sconosciuto
- pagine con domande irrisolte

## Ricerca e recupero

`memory-wiki` supporta due backend di ricerca:

- `shared`: usa il flusso di ricerca della memoria condivisa quando disponibile
- `local`: cerca nella wiki localmente

Supporta anche tre corpora:

- `wiki`
- `memory`
- `all`

Comportamento importante:

- `wiki_search` e `wiki_get` usano i digest compilati come primo passaggio quando possibile
- gli id delle asserzioni possono essere ricondotti alla pagina proprietaria
- asserzioni contestate/obsolete/aggiornate influenzano il ranking
- le etichette di provenienza possono essere mantenute nei risultati

Regola pratica:

- usa `memory_search corpus=all` per un singolo passaggio ampio di richiamo
- usa `wiki_search` + `wiki_get` quando ti interessano ranking specifico della wiki,
  provenienza o struttura delle credenze a livello di pagina

## Strumenti dell'agente

Il plugin registra questi strumenti:

- `wiki_status`
- `wiki_search`
- `wiki_get`
- `wiki_apply`
- `wiki_lint`

Cosa fanno:

- `wiki_status`: modalità dell'archivio corrente, stato, disponibilità della CLI di Obsidian
- `wiki_search`: cerca nelle pagine wiki e, quando configurato, nei corpora di memoria condivisa
- `wiki_get`: legge una pagina wiki per id/percorso o ripiega sul corpus di memoria condivisa
- `wiki_apply`: mutazioni ristrette di sintesi/metadati senza interventi liberi sulla pagina
- `wiki_lint`: controlli strutturali, lacune di provenienza, contraddizioni, domande aperte

Il plugin registra anche un supplemento di corpus di memoria non esclusivo, così
`memory_search` e `memory_get` condivisi possono raggiungere la wiki quando il plugin di memoria
attivo supporta la selezione del corpus.

## Comportamento di prompt e contesto

Quando `context.includeCompiledDigestPrompt` è abilitato, le sezioni del prompt della memoria
aggiungono uno snapshot compilato compatto da `agent-digest.json`.

Quello snapshot è intenzionalmente piccolo e ad alto segnale:

- solo pagine principali
- solo asserzioni principali
- conteggio delle contraddizioni
- conteggio delle domande
- qualificatori di confidenza/aggiornamento

Questa opzione è facoltativa perché modifica la forma del prompt ed è utile
soprattutto per i motori di contesto o per l'assemblaggio legacy dei prompt che
consumano esplicitamente supplementi di memoria.

## Configurazione

Inserisci la configurazione sotto `plugins.entries.memory-wiki.config`:

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "isolated",
          vault: {
            path: "~/.openclaw/wiki/main",
            renderMode: "obsidian",
          },
          obsidian: {
            enabled: true,
            useOfficialCli: true,
            vaultName: "OpenClaw Wiki",
            openAfterWrites: false,
          },
          bridge: {
            enabled: false,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          ingest: {
            autoCompile: true,
            maxConcurrentJobs: 1,
            allowUrlIngest: true,
          },
          search: {
            backend: "shared",
            corpus: "wiki",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
          render: {
            preserveHumanBlocks: true,
            createBacklinks: true,
            createDashboards: true,
          },
        },
      },
    },
  },
}
```

Interruttori principali:

- `vaultMode`: `isolated`, `bridge`, `unsafe-local`
- `vault.renderMode`: `native` o `obsidian`
- `bridge.readMemoryArtifacts`: importa gli artefatti pubblici del plugin di memoria attivo
- `bridge.followMemoryEvents`: include i log degli eventi in modalità bridge
- `search.backend`: `shared` o `local`
- `search.corpus`: `wiki`, `memory` o `all`
- `context.includeCompiledDigestPrompt`: aggiunge uno snapshot compatto del digest alle sezioni del prompt della memoria
- `render.createBacklinks`: genera blocchi correlati deterministici
- `render.createDashboards`: genera pagine dashboard

## CLI

`memory-wiki` espone anche una superficie CLI di primo livello:

```bash
openclaw wiki status
openclaw wiki doctor
openclaw wiki init
openclaw wiki ingest ./notes/alpha.md
openclaw wiki compile
openclaw wiki lint
openclaw wiki search "alpha"
openclaw wiki get entity.alpha
openclaw wiki apply synthesis "Alpha Summary" --body "..." --source-id source.alpha
openclaw wiki bridge import
openclaw wiki obsidian status
```

Vedi [CLI: wiki](/cli/wiki) per il riferimento completo dei comandi.

## Supporto Obsidian

Quando `vault.renderMode` è impostato su `obsidian`, il plugin scrive Markdown
compatibile con Obsidian e può facoltativamente usare la CLI ufficiale `obsidian`.

I flussi di lavoro supportati includono:

- verifica dello stato
- ricerca nell'archivio
- apertura di una pagina
- invocazione di un comando Obsidian
- salto alla nota giornaliera

Questa opzione è facoltativa. La wiki continua a funzionare in modalità nativa
anche senza Obsidian.

## Flusso di lavoro consigliato

1. Mantieni il tuo plugin di memoria attivo per richiamo/promozione/dreaming.
2. Abilita `memory-wiki`.
3. Inizia con la modalità `isolated` a meno che tu non voglia esplicitamente la modalità bridge.
4. Usa `wiki_search` / `wiki_get` quando la provenienza è importante.
5. Usa `wiki_apply` per sintesi ristrette o aggiornamenti dei metadati.
6. Esegui `wiki_lint` dopo modifiche significative.
7. Attiva le dashboard se vuoi visibilità su contenuti obsoleti/contraddizioni.

## Documentazione correlata

- [Panoramica della memoria](/it/concepts/memory)
- [CLI: memory](/cli/memory)
- [CLI: wiki](/cli/wiki)
- [Panoramica del Plugin SDK](/it/plugins/sdk-overview)
