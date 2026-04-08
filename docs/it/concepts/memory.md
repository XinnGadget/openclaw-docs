---
read_when:
    - Vuoi capire come funziona la memoria
    - Vuoi sapere quali file di memoria scrivere
summary: Come OpenClaw ricorda le cose tra una sessione e l'altra
title: Panoramica della memoria
x-i18n:
    generated_at: "2026-04-08T06:00:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3bb8552341b0b651609edaaae826a22fdc535d240aed4fad4af4b069454004af
    source_path: concepts/memory.md
    workflow: 15
---

# Panoramica della memoria

OpenClaw ricorda le cose scrivendo **semplici file Markdown** nello spazio di
lavoro del tuo agente. Il modello "ricorda" solo ciò che viene salvato su disco:
non esiste alcuno stato nascosto.

## Come funziona

Il tuo agente ha tre file relativi alla memoria:

- **`MEMORY.md`** -- memoria a lungo termine. Fatti duraturi, preferenze e
  decisioni. Caricato all'inizio di ogni sessione di messaggi diretti.
- **`memory/YYYY-MM-DD.md`** -- note giornaliere. Contesto in corso e osservazioni.
  Le note di oggi e di ieri vengono caricate automaticamente.
- **`DREAMS.md`** (sperimentale, facoltativo) -- Diario dei sogni e riepiloghi
  delle sessioni di dreaming per la revisione umana.

Questi file si trovano nello spazio di lavoro dell'agente (predefinito `~/.openclaw/workspace`).

<Tip>
Se vuoi che il tuo agente ricordi qualcosa, basta chiederglielo: "Ricorda che
preferisco TypeScript." Lo scriverà nel file appropriato.
</Tip>

## Strumenti di memoria

L'agente dispone di due strumenti per lavorare con la memoria:

- **`memory_search`** -- trova note pertinenti usando la ricerca semantica, anche
  quando la formulazione è diversa dall'originale.
- **`memory_get`** -- legge un file di memoria specifico o un intervallo di righe.

Entrambi gli strumenti sono forniti dal plugin di memoria attivo (predefinito: `memory-core`).

## Plugin complementare Memory Wiki

Se vuoi che la memoria duratura si comporti più come una base di conoscenza
mantenuta che come semplici note grezze, usa il plugin incluso `memory-wiki`.

`memory-wiki` compila la conoscenza duratura in un archivio wiki con:

- struttura delle pagine deterministica
- affermazioni ed evidenze strutturate
- tracciamento delle contraddizioni e dell'attualità
- dashboard generate
- digest compilati per i consumer agent/runtime
- strumenti nativi wiki come `wiki_search`, `wiki_get`, `wiki_apply` e `wiki_lint`

Non sostituisce il plugin di memoria attivo. Il plugin di memoria attivo
continua a gestire il richiamo, la promozione e il dreaming. `memory-wiki`
aggiunge accanto ad esso un livello di conoscenza ricco di provenienza.

Vedi [Memory Wiki](/it/plugins/memory-wiki).

## Ricerca nella memoria

Quando è configurato un provider di embedding, `memory_search` usa la **ricerca
ibrida** -- combinando similarità vettoriale (significato semantico) con
corrispondenza di parole chiave (termini esatti come ID e simboli di codice).
Funziona subito, non appena disponi di una chiave API per qualsiasi provider supportato.

<Info>
OpenClaw rileva automaticamente il tuo provider di embedding dalle chiavi API
disponibili. Se hai configurato una chiave OpenAI, Gemini, Voyage o Mistral, la
ricerca nella memoria viene abilitata automaticamente.
</Info>

Per i dettagli su come funziona la ricerca, le opzioni di regolazione e la
configurazione del provider, vedi
[Memory Search](/it/concepts/memory-search).

## Backend di memoria

<CardGroup cols={3}>
<Card title="Integrato (predefinito)" icon="database" href="/it/concepts/memory-builtin">
Basato su SQLite. Funziona subito con ricerca per parole chiave, similarità
vettoriale e ricerca ibrida. Nessuna dipendenza aggiuntiva.
</Card>
<Card title="QMD" icon="search" href="/it/concepts/memory-qmd">
Sidecar local-first con reranking, espansione delle query e la possibilità di
indicizzare directory esterne allo spazio di lavoro.
</Card>
<Card title="Honcho" icon="brain" href="/it/concepts/memory-honcho">
Memoria cross-session AI-native con modellazione dell'utente, ricerca semantica
e consapevolezza multi-agente. Installazione tramite plugin.
</Card>
</CardGroup>

## Livello wiki della conoscenza

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/it/plugins/memory-wiki">
Compila la memoria duratura in un archivio wiki ricco di provenienza con
affermazioni, dashboard, modalità bridge e flussi di lavoro compatibili con Obsidian.
</Card>
</CardGroup>

## Flush automatico della memoria

Prima che la [compaction](/it/concepts/compaction) riepiloghi la tua conversazione, OpenClaw
esegue un turno silenzioso che ricorda all'agente di salvare il contesto importante nei file
di memoria. È attivo per impostazione predefinita: non devi configurare nulla.

<Tip>
Il flush della memoria previene la perdita di contesto durante la compaction. Se
nella conversazione sono presenti fatti importanti che il tuo agente non ha
ancora scritto in un file, verranno salvati automaticamente prima che venga
generato il riepilogo.
</Tip>

## Dreaming (sperimentale)

Il dreaming è un passaggio opzionale di consolidamento della memoria in background. Raccoglie
segnali a breve termine, valuta i candidati e promuove nella memoria a lungo
termine (`MEMORY.md`) solo gli elementi qualificati.

È progettato per mantenere alta la qualità della memoria a lungo termine:

- **Attivazione esplicita**: disabilitato per impostazione predefinita.
- **Pianificato**: quando è abilitato, `memory-core` gestisce automaticamente un
  job cron ricorrente per una sessione completa di dreaming.
- **Con soglia**: le promozioni devono superare soglie di punteggio, frequenza
  di richiamo e diversità delle query.
- **Verificabile**: i riepiloghi delle fasi e le voci del diario vengono scritti
  in `DREAMS.md` per la revisione umana.

Per il comportamento delle fasi, i segnali di punteggio e i dettagli del Diario
dei sogni, vedi [Dreaming (experimental)](/it/concepts/dreaming).

## CLI

```bash
openclaw memory status          # Controlla lo stato dell'indice e il provider
openclaw memory search "query"  # Cerca dalla riga di comando
openclaw memory index --force   # Ricostruisce l'indice
```

## Approfondimenti

- [Builtin Memory Engine](/it/concepts/memory-builtin) -- backend SQLite predefinito
- [QMD Memory Engine](/it/concepts/memory-qmd) -- sidecar local-first avanzato
- [Honcho Memory](/it/concepts/memory-honcho) -- memoria cross-session AI-native
- [Memory Wiki](/it/plugins/memory-wiki) -- archivio di conoscenza compilato e strumenti nativi wiki
- [Memory Search](/it/concepts/memory-search) -- pipeline di ricerca, provider e
  regolazione
- [Dreaming (experimental)](/it/concepts/dreaming) -- promozione in background
  dal richiamo a breve termine alla memoria a lungo termine
- [Memory configuration reference](/it/reference/memory-config) -- tutte le opzioni di configurazione
- [Compaction](/it/concepts/compaction) -- come la compaction interagisce con la memoria
