---
read_when:
    - Vuoi capire come funziona la memoria
    - Vuoi sapere quali file di memoria scrivere
summary: Come OpenClaw ricorda le cose tra una sessione e l'altra
title: Panoramica della memoria
x-i18n:
    generated_at: "2026-04-15T14:40:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# Panoramica della memoria

OpenClaw ricorda le cose scrivendo **semplici file Markdown** nello spazio di lavoro
del tuo agente. Il modello "ricorda" solo ciò che viene salvato su disco -- non esiste
alcuno stato nascosto.

## Come funziona

Il tuo agente ha tre file relativi alla memoria:

- **`MEMORY.md`** -- memoria a lungo termine. Fatti durevoli, preferenze e
  decisioni. Caricato all'inizio di ogni sessione di DM.
- **`memory/YYYY-MM-DD.md`** -- note giornaliere. Contesto in evoluzione e osservazioni.
  Le note di oggi e di ieri vengono caricate automaticamente.
- **`DREAMS.md`** (facoltativo) -- diario dei sogni e riepiloghi delle scansioni di
  Dreaming per la revisione umana, incluse voci di backfill storico con fondamento.

Questi file si trovano nello spazio di lavoro dell'agente (predefinito: `~/.openclaw/workspace`).

<Tip>
Se vuoi che il tuo agente ricordi qualcosa, chiediglielo semplicemente: "Ricorda che
preferisco TypeScript." Lo scriverà nel file appropriato.
</Tip>

## Strumenti di memoria

L'agente dispone di due strumenti per lavorare con la memoria:

- **`memory_search`** -- trova note rilevanti usando la ricerca semantica, anche quando
  la formulazione differisce dall'originale.
- **`memory_get`** -- legge un file di memoria specifico o un intervallo di righe.

Entrambi gli strumenti sono forniti dal Plugin di memoria attivo (predefinito: `memory-core`).

## Plugin complementare Memory Wiki

Se vuoi che la memoria durevole si comporti più come una base di conoscenza mantenuta
che come semplici note grezze, usa il Plugin integrato `memory-wiki`.

`memory-wiki` compila la conoscenza durevole in un archivio wiki con:

- struttura delle pagine deterministica
- affermazioni ed evidenze strutturate
- tracciamento di contraddizioni e aggiornamento
- dashboard generate
- digest compilati per i consumatori agente/runtime
- strumenti nativi della wiki come `wiki_search`, `wiki_get`, `wiki_apply` e `wiki_lint`

Non sostituisce il Plugin di memoria attivo. Il Plugin di memoria attivo continua
a gestire richiamo, promozione e Dreaming. `memory-wiki` aggiunge accanto a esso
un livello di conoscenza ricco di provenienza.

Vedi [Memory Wiki](/it/plugins/memory-wiki).

## Ricerca nella memoria

Quando è configurato un provider di embedding, `memory_search` usa la **ricerca
ibrida** -- combinando similarità vettoriale (significato semantico) con corrispondenza
per parole chiave (termini esatti come ID e simboli di codice). Funziona subito
appena disponi di una chiave API per qualsiasi provider supportato.

<Info>
OpenClaw rileva automaticamente il tuo provider di embedding dalle chiavi API disponibili. Se
hai configurato una chiave OpenAI, Gemini, Voyage o Mistral, la ricerca nella memoria
viene abilitata automaticamente.
</Info>

Per dettagli su come funziona la ricerca, sulle opzioni di regolazione e sulla configurazione
del provider, vedi [Memory Search](/it/concepts/memory-search).

## Backend di memoria

<CardGroup cols={3}>
<Card title="Integrato (predefinito)" icon="database" href="/it/concepts/memory-builtin">
Basato su SQLite. Funziona subito con ricerca per parole chiave, similarità vettoriale e
ricerca ibrida. Nessuna dipendenza aggiuntiva.
</Card>
<Card title="QMD" icon="search" href="/it/concepts/memory-qmd">
Sidecar local-first con reranking, espansione delle query e capacità di indicizzare
directory esterne allo spazio di lavoro.
</Card>
<Card title="Honcho" icon="brain" href="/it/concepts/memory-honcho">
Memoria cross-session AI-native con modellazione dell'utente, ricerca semantica e
consapevolezza multi-agente. Installazione del Plugin.
</Card>
</CardGroup>

## Livello wiki della conoscenza

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/it/plugins/memory-wiki">
Compila la memoria durevole in un archivio wiki ricco di provenienza con affermazioni,
dashboard, bridge mode e flussi di lavoro compatibili con Obsidian.
</Card>
</CardGroup>

## Flush automatico della memoria

Prima che la [Compaction](/it/concepts/compaction) riepiloghi la tua conversazione, OpenClaw
esegue un turno silenzioso che ricorda all'agente di salvare il contesto importante nei file
di memoria. È attivo per impostazione predefinita -- non devi configurare nulla.

<Tip>
Il flush della memoria impedisce la perdita di contesto durante la Compaction. Se il tuo agente ha
fatti importanti nella conversazione che non sono ancora stati scritti in un file, verranno
salvati automaticamente prima che avvenga il riepilogo.
</Tip>

## Dreaming

Dreaming è un passaggio facoltativo di consolidamento in background per la memoria. Raccoglie
segnali a breve termine, assegna un punteggio ai candidati e promuove nella memoria a lungo termine
(`MEMORY.md`) solo gli elementi qualificati.

È progettato per mantenere alta la qualità della memoria a lungo termine:

- **Su adesione esplicita**: disattivato per impostazione predefinita.
- **Pianificato**: quando è abilitato, `memory-core` gestisce automaticamente un processo Cron
  ricorrente per una scansione completa di Dreaming.
- **Con soglia**: le promozioni devono superare soglie di punteggio, frequenza di richiamo e
  diversità delle query.
- **Revisionabile**: i riepiloghi delle fasi e le voci del diario vengono scritti in `DREAMS.md`
  per la revisione umana.

Per il comportamento delle fasi, i segnali di punteggio e i dettagli del diario dei sogni, vedi
[Dreaming](/it/concepts/dreaming).

## Backfill con fondamento e promozione in tempo reale

Il sistema di Dreaming ora ha due percorsi di revisione strettamente correlati:

- **Live dreaming** lavora dall'archivio Dreaming a breve termine sotto
  `memory/.dreams/` ed è ciò che la normale fase profonda usa per decidere cosa
  può essere promosso in `MEMORY.md`.
- **Grounded backfill** legge le note storiche `memory/YYYY-MM-DD.md` come
  file giornalieri autonomi e scrive output di revisione strutturato in `DREAMS.md`.

Grounded backfill è utile quando vuoi ripercorrere note più vecchie e ispezionare
ciò che il sistema considera durevole senza modificare manualmente `MEMORY.md`.

Quando usi:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

i candidati durevoli con fondamento non vengono promossi direttamente. Vengono messi in staging
nello stesso archivio Dreaming a breve termine che la normale fase profonda usa già. Questo significa:

- `DREAMS.md` rimane la superficie di revisione umana.
- l'archivio a breve termine rimane la superficie di classificazione rivolta alla macchina.
- `MEMORY.md` continua a essere scritto solo dalla promozione profonda.

Se decidi che il replay non è stato utile, puoi rimuovere gli artefatti messi in staging
senza toccare le normali voci del diario o il normale stato di richiamo:

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # Controlla lo stato dell'indice e il provider
openclaw memory search "query"  # Esegue una ricerca dalla riga di comando
openclaw memory index --force   # Ricostruisce l'indice
```

## Approfondimenti

- [Builtin Memory Engine](/it/concepts/memory-builtin) -- backend SQLite predefinito
- [QMD Memory Engine](/it/concepts/memory-qmd) -- sidecar local-first avanzato
- [Honcho Memory](/it/concepts/memory-honcho) -- memoria cross-session AI-native
- [Memory Wiki](/it/plugins/memory-wiki) -- archivio di conoscenza compilato e strumenti nativi della wiki
- [Memory Search](/it/concepts/memory-search) -- pipeline di ricerca, provider e
  regolazione
- [Dreaming](/it/concepts/dreaming) -- promozione in background
  dal richiamo a breve termine alla memoria a lungo termine
- [Riferimento della configurazione della memoria](/it/reference/memory-config) -- tutte le opzioni di configurazione
- [Compaction](/it/concepts/compaction) -- come la Compaction interagisce con la memoria
