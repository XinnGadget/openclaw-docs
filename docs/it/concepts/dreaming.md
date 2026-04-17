---
read_when:
    - Vuoi che la promozione della memoria venga eseguita automaticamente
    - Vuoi capire cosa fa ogni fase del Dreaming
    - Vuoi regolare il consolidamento senza inquinare `MEMORY.md`
summary: Consolidamento della memoria in background con fasi leggere, profonde e REM, più un Diario dei sogni
title: Dreaming
x-i18n:
    generated_at: "2026-04-15T14:40:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5bcaec80f62e7611ed533094ef1917bd72c885f57252824db910e1f0496adc6
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming

Dreaming è il sistema di consolidamento della memoria in background in `memory-core`.
Aiuta OpenClaw a spostare forti segnali della memoria a breve termine in una memoria durevole, mantenendo al tempo stesso il processo spiegabile e verificabile.

Dreaming è **opt-in** ed è disabilitato per impostazione predefinita.

## Cosa scrive Dreaming

Dreaming mantiene due tipi di output:

- **Stato della macchina** in `memory/.dreams/` (archivio di richiamo, segnali di fase, checkpoint di ingestione, lock).
- **Output leggibile dall'uomo** in `DREAMS.md` (o `dreams.md` esistente) e file di report di fase opzionali in `memory/dreaming/<phase>/YYYY-MM-DD.md`.

La promozione a lungo termine continua a scrivere solo in `MEMORY.md`.

## Modello delle fasi

Dreaming usa tre fasi cooperative:

| Fase | Scopo                                     | Scrittura durevole |
| ----- | ----------------------------------------- | ------------------ |
| Light | Ordina e prepara il materiale recente a breve termine | No                 |
| Deep  | Assegna un punteggio e promuove i candidati durevoli  | Sì (`MEMORY.md`)   |
| REM   | Riflette su temi e idee ricorrenti        | No                 |

Queste fasi sono dettagli interni di implementazione, non "modalità" separate configurabili dall'utente.

### Fase Light

La fase Light acquisisce segnali recenti della memoria giornaliera e tracce di richiamo, li deduplica e prepara righe candidate.

- Legge dallo stato di richiamo a breve termine, dai file recenti della memoria giornaliera e dalle trascrizioni di sessione redatte quando disponibili.
- Scrive un blocco gestito `## Light Sleep` quando l'archiviazione include output inline.
- Registra segnali di rinforzo per il ranking deep successivo.
- Non scrive mai in `MEMORY.md`.

### Fase Deep

La fase Deep decide cosa diventa memoria a lungo termine.

- Classifica i candidati usando punteggio pesato e soglie di accesso.
- Richiede il superamento di `minScore`, `minRecallCount` e `minUniqueQueries`.
- Reidrata gli snippet dai file giornalieri attivi prima della scrittura, quindi gli snippet obsoleti/eliminati vengono saltati.
- Aggiunge le voci promosse a `MEMORY.md`.
- Scrive un riepilogo `## Deep Sleep` in `DREAMS.md` e opzionalmente scrive `memory/dreaming/deep/YYYY-MM-DD.md`.

### Fase REM

La fase REM estrae pattern e segnali riflessivi.

- Costruisce riepiloghi di temi e riflessioni a partire da tracce recenti a breve termine.
- Scrive un blocco gestito `## REM Sleep` quando l'archiviazione include output inline.
- Registra segnali di rinforzo REM usati dal ranking deep.
- Non scrive mai in `MEMORY.md`.

## Ingestione delle trascrizioni di sessione

Dreaming può acquisire trascrizioni di sessione redatte nel corpus di Dreaming. Quando
le trascrizioni sono disponibili, vengono passate alla fase Light insieme ai
segnali della memoria giornaliera e alle tracce di richiamo. Il contenuto personale e sensibile viene redatto
prima dell'ingestione.

## Diario dei sogni

Dreaming mantiene anche un **Diario dei sogni** narrativo in `DREAMS.md`.
Dopo che ogni fase ha raccolto materiale sufficiente, `memory-core` esegue un turno in background best-effort di un subagent (usando il modello di runtime predefinito) e aggiunge una breve voce di diario.

Questo diario è destinato alla lettura umana nella UI Dreams, non è una fonte di promozione.
Gli artifact di diario/report generati da Dreaming sono esclusi dalla
promozione a breve termine. Solo gli snippet di memoria fondati sono idonei alla promozione in
`MEMORY.md`.

Esiste anche un percorso di backfill storico fondato per attività di revisione e recupero:

- `memory rem-harness --path ... --grounded` mostra in anteprima l'output del diario fondato dalle note storiche `YYYY-MM-DD.md`.
- `memory rem-backfill --path ...` scrive voci di diario fondate e reversibili in `DREAMS.md`.
- `memory rem-backfill --path ... --stage-short-term` prepara candidati durevoli fondati nello stesso archivio di evidenze a breve termine che la normale fase Deep usa già.
- `memory rem-backfill --rollback` e `--rollback-short-term` rimuovono questi artifact di backfill preparati senza toccare le normali voci di diario o il richiamo attivo a breve termine.

La UI di controllo espone lo stesso flusso di backfill/reset del diario così puoi ispezionare i
risultati nella scena Dreams prima di decidere se i candidati fondati
meritano la promozione. La scena mostra anche un percorso fondato distinto così puoi vedere
quali voci preparate a breve termine provengono dalla riproduzione storica, quali elementi promossi
sono stati guidati dal grounded e cancellare solo le voci preparate esclusivamente grounded senza
toccare il normale stato attivo a breve termine.

## Segnali di ranking Deep

Il ranking Deep usa sei segnali di base pesati più il rinforzo di fase:

| Segnale             | Peso   | Descrizione                                        |
| ------------------- | ------ | -------------------------------------------------- |
| Frequenza           | 0.24   | Quanti segnali a breve termine ha accumulato la voce |
| Rilevanza           | 0.30   | Qualità media di recupero per la voce              |
| Diversità delle query | 0.15 | Contesti distinti di query/giorno in cui è emersa  |
| Recenza             | 0.15   | Punteggio di freschezza con decadimento temporale  |
| Consolidamento      | 0.10   | Forza di ricorrenza su più giorni                  |
| Ricchezza concettuale | 0.06 | Densità di tag concettuali da snippet/percorso     |

Le occorrenze delle fasi Light e REM aggiungono un piccolo incremento con decadimento di recenza da
`memory/.dreams/phase-signals.json`.

## Pianificazione

Quando è abilitato, `memory-core` gestisce automaticamente un job Cron per una sweep completa di Dreaming. Ogni sweep esegue le fasi in ordine: light -> REM -> deep.

Comportamento della cadenza predefinita:

| Impostazione         | Predefinito |
| -------------------- | ----------- |
| `dreaming.frequency` | `0 3 * * *` |

## Avvio rapido

Abilita Dreaming:

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

Abilita Dreaming con una cadenza di sweep personalizzata:

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

`memory promote` manuale usa per impostazione predefinita le soglie della fase Deep, salvo override
con flag CLI.

Spiega perché un candidato specifico verrebbe o non verrebbe promosso:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

Mostra in anteprima riflessioni REM, verità candidate e output di promozione Deep senza
scrivere nulla:

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## Valori predefiniti chiave

Tutte le impostazioni si trovano in `plugins.entries.memory-core.config.dreaming`.

| Chiave      | Predefinito |
| ----------- | ----------- |
| `enabled`   | `false`     |
| `frequency` | `0 3 * * *` |

Criteri di fase, soglie e comportamento di archiviazione sono dettagli interni di implementazione
(non configurazione rivolta all'utente).

Vedi [Riferimento alla configurazione della memoria](/it/reference/memory-config#dreaming)
per l'elenco completo delle chiavi.

## UI Dreams

Quando è abilitata, la scheda **Dreams** del Gateway mostra:

- stato attuale di abilitazione di Dreaming
- stato a livello di fase e presenza di sweep gestita
- conteggi di elementi a breve termine, grounded, segnali e promossi oggi
- orario della prossima esecuzione pianificata
- un percorso grounded distinto nella scena per le voci preparate dalla riproduzione storica
- un lettore espandibile del Diario dei sogni basato su `doctor.memory.dreamDiary`

## Correlati

- [Memoria](/it/concepts/memory)
- [Ricerca nella memoria](/it/concepts/memory-search)
- [CLI memory](/cli/memory)
- [Riferimento alla configurazione della memoria](/it/reference/memory-config)
