---
read_when:
    - Vuoi che la promozione della memoria venga eseguita automaticamente
    - Vuoi capire cosa fa ogni fase del dreaming
    - Vuoi regolare il consolidamento senza inquinare MEMORY.md
summary: Consolidamento della memoria in background con fasi light, deep e REM più un Diario dei sogni
title: Dreaming (sperimentale)
x-i18n:
    generated_at: "2026-04-09T01:27:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 26476eddb8260e1554098a6adbb069cf7f5e284cf2e09479c6d9d8f8b93280ef
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming (sperimentale)

Dreaming è il sistema di consolidamento della memoria in background in `memory-core`.
Aiuta OpenClaw a spostare segnali forti a breve termine nella memoria durevole, mantenendo
il processo spiegabile e verificabile.

Dreaming è **opt-in** ed è disattivato per impostazione predefinita.

## Cosa scrive dreaming

Dreaming mantiene due tipi di output:

- **Stato macchina** in `memory/.dreams/` (archivio di richiamo, segnali di fase, checkpoint di ingestione, lock).
- **Output leggibile da persone** in `DREAMS.md` (o `dreams.md` esistente) e file di report di fase facoltativi in `memory/dreaming/<phase>/YYYY-MM-DD.md`.

La promozione a lungo termine continua a scrivere solo in `MEMORY.md`.

## Modello di fase

Dreaming usa tre fasi cooperative:

| Fase | Scopo                                     | Scrittura durevole |
| ----- | ----------------------------------------- | ------------------ |
| Light | Ordina e prepara il materiale recente a breve termine | No                 |
| Deep  | Valuta e promuove i candidati durevoli    | Sì (`MEMORY.md`)   |
| REM   | Riflette su temi e idee ricorrenti        | No                 |

Queste fasi sono dettagli di implementazione interni, non "modalità"
separate configurate dall'utente.

### Fase light

La fase light acquisisce segnali di memoria giornalieri recenti e tracce di richiamo, li deduplica
e prepara righe candidate.

- Legge dallo stato di richiamo a breve termine, dai file di memoria giornalieri recenti e dalle trascrizioni delle sessioni redatte quando disponibili.
- Scrive un blocco gestito `## Light Sleep` quando l'archiviazione include output inline.
- Registra segnali di rinforzo per il ranking deep successivo.
- Non scrive mai in `MEMORY.md`.

### Fase deep

La fase deep decide cosa diventa memoria a lungo termine.

- Classifica i candidati usando punteggi pesati e soglie di controllo.
- Richiede il superamento di `minScore`, `minRecallCount` e `minUniqueQueries`.
- Reidrata gli snippet dai file giornalieri live prima della scrittura, quindi gli snippet obsoleti o eliminati vengono saltati.
- Aggiunge le voci promosse a `MEMORY.md`.
- Scrive un riepilogo `## Deep Sleep` in `DREAMS.md` e facoltativamente scrive `memory/dreaming/deep/YYYY-MM-DD.md`.

### Fase REM

La fase REM estrae pattern e segnali riflessivi.

- Costruisce riepiloghi di temi e riflessioni a partire da tracce recenti a breve termine.
- Scrive un blocco gestito `## REM Sleep` quando l'archiviazione include output inline.
- Registra segnali di rinforzo REM usati dal ranking deep.
- Non scrive mai in `MEMORY.md`.

## Ingestione delle trascrizioni di sessione

Dreaming può acquisire trascrizioni di sessione redatte nel corpus di dreaming. Quando
le trascrizioni sono disponibili, vengono inserite nella fase light insieme ai segnali
di memoria giornalieri e alle tracce di richiamo. I contenuti personali e sensibili vengono redatti
prima dell'ingestione.

## Diario dei sogni

Dreaming mantiene anche un **Diario dei sogni** narrativo in `DREAMS.md`.
Dopo che ogni fase ha abbastanza materiale, `memory-core` esegue un turno in background
best-effort di subagent (usando il modello di runtime predefinito) e aggiunge una breve voce di diario.

Questo diario è pensato per la lettura umana nell'interfaccia Dreams, non è una fonte di promozione.

Esiste anche un percorso di backfill storico grounded per attività di revisione e recupero:

- `memory rem-harness --path ... --grounded` mostra in anteprima l'output del diario grounded da note storiche `YYYY-MM-DD.md`.
- `memory rem-backfill --path ...` scrive voci di diario grounded reversibili in `DREAMS.md`.
- `memory rem-backfill --path ... --stage-short-term` prepara candidati durevoli grounded nello stesso archivio di evidenze a breve termine che la normale fase deep usa già.
- `memory rem-backfill --rollback` e `--rollback-short-term` rimuovono quegli artefatti di backfill preparati senza toccare le normali voci di diario o il richiamo live a breve termine.

La Control UI espone lo stesso flusso di backfill/reset del diario così puoi ispezionare
i risultati nella scena Dreams prima di decidere se i candidati grounded
meritano la promozione. La scena mostra anche un percorso grounded distinto così puoi vedere
quali voci preparate a breve termine provengono dalla riproduzione storica, quali elementi promossi
sono stati guidati dal grounded, e cancellare solo le voci preparate solo-grounded senza
toccare il normale stato live a breve termine.

## Segnali di ranking deep

Il ranking deep usa sei segnali base pesati più il rinforzo di fase:

| Segnale             | Peso   | Descrizione                                       |
| ------------------- | ------ | ------------------------------------------------- |
| Frequenza           | 0.24   | Quanti segnali a breve termine ha accumulato la voce |
| Rilevanza           | 0.30   | Qualità media di recupero per la voce             |
| Diversità delle query | 0.15 | Contesti distinti di query/giorno che l'hanno fatta emergere |
| Recenza             | 0.15   | Punteggio di freschezza con decadimento temporale |
| Consolidamento      | 0.10   | Forza di ricorrenza su più giorni                 |
| Ricchezza concettuale | 0.06 | Densità dei tag concettuali da snippet/percorso   |

I riscontri delle fasi light e REM aggiungono un piccolo incremento con decadimento della recenza da
`memory/.dreams/phase-signals.json`.

## Pianificazione

Quando abilitato, `memory-core` gestisce automaticamente un processo cron per una sweep
completa di dreaming. Ogni sweep esegue le fasi in ordine: light -> REM -> deep.

Comportamento predefinito della cadenza:

| Impostazione         | Predefinito |
| -------------------- | ----------- |
| `dreaming.frequency` | `0 3 * * *` |

## Avvio rapido

Abilita dreaming:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true
          }
        }
      }
    }
  }
}
```

Abilita dreaming con una cadenza di sweep personalizzata:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true,
            "timezone": "America/Los_Angeles",
            "frequency": "0 */6 * * *"
          }
        }
      }
    }
  }
}
```

## Comando slash

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## Flusso di lavoro CLI

Usa la promozione CLI per anteprima o applicazione manuale:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

La modalità manuale `memory promote` usa per impostazione predefinita le soglie della fase deep, a meno che non vengano sovrascritte
con flag CLI.

Spiega perché un candidato specifico verrebbe o non verrebbe promosso:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

Mostra in anteprima riflessioni REM, verità candidate e output di promozione deep senza
scrivere nulla:

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## Valori predefiniti principali

Tutte le impostazioni si trovano in `plugins.entries.memory-core.config.dreaming`.

| Chiave      | Predefinito |
| ----------- | ----------- |
| `enabled`   | `false`     |
| `frequency` | `0 3 * * *` |

La policy delle fasi, le soglie e il comportamento di archiviazione sono dettagli
di implementazione interni (non configurazione esposta all'utente).

Consulta [Riferimento della configurazione Memory](/it/reference/memory-config#dreaming-experimental)
per l'elenco completo delle chiavi.

## Interfaccia Dreams

Quando abilitata, la scheda **Dreams** del Gateway mostra:

- stato corrente di abilitazione di dreaming
- stato a livello di fase e presenza di sweep gestite
- conteggi di breve termine, grounded, segnali e promossi oggi
- tempistica della prossima esecuzione pianificata
- un percorso Scene grounded distinto per le voci preparate della riproduzione storica
- un lettore espandibile del Diario dei sogni basato su `doctor.memory.dreamDiary`

## Correlati

- [Memory](/it/concepts/memory)
- [Ricerca nella memoria](/it/concepts/memory-search)
- [CLI memory](/cli/memory)
- [Riferimento della configurazione Memory](/it/reference/memory-config)
