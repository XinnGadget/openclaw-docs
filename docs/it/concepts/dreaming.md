---
read_when:
    - Vuoi che la promozione della memoria venga eseguita automaticamente
    - Vuoi capire cosa fa ogni fase del sogno
    - Vuoi regolare il consolidamento senza inquinare `MEMORY.md`
summary: Consolidamento della memoria in background con fasi leggere, profonde e REM, più un Diario dei sogni
title: Sognare (sperimentale)
x-i18n:
    generated_at: "2026-04-06T08:15:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 36c4b1e70801d662090dc8ce20608c2f141c23cd7ce53c54e3dcf332c801fd4e
    source_path: concepts/dreaming.md
    workflow: 15
---

# Sognare (sperimentale)

Il sogno è il sistema di consolidamento della memoria in background in `memory-core`.
Aiuta OpenClaw a spostare segnali forti a breve termine nella memoria duratura, mantenendo
il processo spiegabile e verificabile.

Il sogno è **facoltativo** ed è disabilitato per impostazione predefinita.

## Cosa scrive il sogno

Il sogno mantiene due tipi di output:

- **Stato macchina** in `memory/.dreams/` (archivio di richiamo, segnali di fase, checkpoint di ingestione, lock).
- **Output leggibile dagli esseri umani** in `DREAMS.md` (o `dreams.md` esistente) e file di report di fase facoltativi in `memory/dreaming/<phase>/YYYY-MM-DD.md`.

La promozione a lungo termine continua a scrivere solo in `MEMORY.md`.

## Modello di fase

Il sogno usa tre fasi cooperative:

| Fase | Scopo                                     | Scrittura duratura |
| ----- | ----------------------------------------- | ------------------ |
| Leggera | Ordinare e preparare il materiale recente a breve termine | No                 |
| Profonda  | Valutare e promuovere i candidati duraturi      | Sì (`MEMORY.md`) |
| REM   | Riflettere su temi e idee ricorrenti     | No                 |

Queste fasi sono dettagli interni di implementazione, non "modalità"
separate configurabili dall'utente.

### Fase leggera

La fase leggera acquisisce segnali recenti della memoria giornaliera e tracce di richiamo, li deduplica
e prepara righe candidate.

- Legge dallo stato di richiamo a breve termine e dai file recenti della memoria giornaliera.
- Scrive un blocco gestito `## Sonno leggero` quando l'archiviazione include output inline.
- Registra segnali di rinforzo per la successiva classificazione profonda.
- Non scrive mai in `MEMORY.md`.

### Fase profonda

La fase profonda decide cosa diventa memoria a lungo termine.

- Classifica i candidati usando punteggi ponderati e soglie di filtro.
- Richiede il superamento di `minScore`, `minRecallCount` e `minUniqueQueries`.
- Reidrata gli snippet dai file giornalieri attivi prima di scrivere, quindi gli snippet obsoleti o eliminati vengono saltati.
- Aggiunge le voci promosse a `MEMORY.md`.
- Scrive un riepilogo `## Sonno profondo` in `DREAMS.md` e facoltativamente scrive `memory/dreaming/deep/YYYY-MM-DD.md`.

### Fase REM

La fase REM estrae schemi e segnali riflessivi.

- Costruisce riepiloghi di temi e riflessioni dalle recenti tracce a breve termine.
- Scrive un blocco gestito `## Sonno REM` quando l'archiviazione include output inline.
- Registra segnali di rinforzo REM usati dalla classificazione profonda.
- Non scrive mai in `MEMORY.md`.

## Diario dei sogni

Il sogno mantiene anche un **Diario dei sogni** narrativo in `DREAMS.md`.
Dopo che ogni fase ha accumulato materiale sufficiente, `memory-core` esegue un turno
in background best-effort del sottoagente (usando il modello runtime predefinito) e aggiunge una breve voce di diario.

Questo diario è pensato per la lettura umana nell'interfaccia Dreams, non è una fonte di promozione.

## Segnali di classificazione profonda

La classificazione profonda usa sei segnali di base ponderati più il rinforzo di fase:

| Segnale              | Peso | Descrizione                                       |
| ------------------- | ------ | ------------------------------------------------- |
| Frequenza           | 0.24   | Quanti segnali a breve termine ha accumulato la voce |
| Rilevanza           | 0.30   | Qualità media di recupero per la voce           |
| Diversità delle query     | 0.15   | Contesti distinti di query/giorno in cui è emersa      |
| Recenza             | 0.15   | Punteggio di freschezza con decadimento temporale                      |
| Consolidamento       | 0.10   | Forza di ricorrenza su più giorni                     |
| Ricchezza concettuale | 0.06   | Densità dei tag concettuali da snippet/percorso             |

I riscontri delle fasi leggera e REM aggiungono un piccolo incremento con decadimento di recenza da
`memory/.dreams/phase-signals.json`.

## Pianificazione

Quando è abilitato, `memory-core` gestisce automaticamente un job cron per un ciclo
completo di sogno. Ogni ciclo esegue le fasi in ordine: leggera -> REM -> profonda.

Comportamento predefinito della frequenza:

| Impostazione              | Predefinito     |
| -------------------- | ----------- |
| `dreaming.frequency` | `0 3 * * *` |

## Avvio rapido

Abilita il sogno:

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

Abilita il sogno con una frequenza di ciclo personalizzata:

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

Usa la promozione CLI per l'anteprima o l'applicazione manuale:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

Il comando manuale `memory promote` usa per impostazione predefinita le soglie della fase profonda, salvo override
tramite flag della CLI.

Spiega perché un candidato specifico verrebbe o non verrebbe promosso:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

Visualizza in anteprima riflessioni REM, verità candidate e output della promozione profonda senza
scrivere nulla:

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## Valori predefiniti principali

Tutte le impostazioni si trovano in `plugins.entries.memory-core.config.dreaming`.

| Chiave         | Predefinito     |
| ----------- | ----------- |
| `enabled`   | `false`     |
| `frequency` | `0 3 * * *` |

La policy di fase, le soglie e il comportamento di archiviazione sono dettagli interni di implementazione
(non configurazione visibile all'utente).

Vedi [Riferimento della configurazione della memoria](/it/reference/memory-config#dreaming-experimental)
per l'elenco completo delle chiavi.

## Interfaccia Dreams

Quando è abilitata, la scheda **Dreams** del Gateway mostra:

- stato attuale di abilitazione del sogno
- stato a livello di fase e presenza del ciclo gestito
- conteggi di breve termine, lungo termine e promossi oggi
- orario della prossima esecuzione pianificata
- un lettore espandibile del Diario dei sogni basato su `doctor.memory.dreamDiary`

## Correlati

- [Memoria](/it/concepts/memory)
- [Ricerca nella memoria](/it/concepts/memory-search)
- [CLI memory](/cli/memory)
- [Riferimento della configurazione della memoria](/it/reference/memory-config)
