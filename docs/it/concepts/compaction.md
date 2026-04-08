---
read_when:
    - Vuoi capire la compattazione automatica e /compact
    - Stai eseguendo il debug di sessioni lunghe che raggiungono i limiti di contesto
summary: Come OpenClaw riassume le conversazioni lunghe per rimanere entro i limiti del modello
title: Compattazione
x-i18n:
    generated_at: "2026-04-08T02:14:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: e6590b82a8c3a9c310998d653459ca4d8612495703ca0a8d8d306d7643142fd1
    source_path: concepts/compaction.md
    workflow: 15
---

# Compattazione

Ogni modello ha una finestra di contesto, ovvero il numero massimo di token che può elaborare.
Quando una conversazione si avvicina a quel limite, OpenClaw **compatta** i messaggi meno recenti
in un riepilogo in modo che la chat possa continuare.

## Come funziona

1. I turni meno recenti della conversazione vengono riassunti in una voce compatta.
2. Il riepilogo viene salvato nella trascrizione della sessione.
3. I messaggi recenti vengono mantenuti intatti.

Quando OpenClaw divide la cronologia in blocchi di compattazione, mantiene le
chiamate agli strumenti dell'assistente abbinate alle rispettive voci `toolResult`. Se un punto di divisione cade
all'interno di un blocco di strumenti, OpenClaw sposta il confine in modo che la coppia rimanga unita e
venga preservata la coda corrente non riassunta.

La cronologia completa della conversazione rimane su disco. La compattazione modifica solo ciò che il
modello vede nel turno successivo.

## Compattazione automatica

La compattazione automatica è attiva per impostazione predefinita. Viene eseguita quando la sessione si avvicina al
limite di contesto, o quando il modello restituisce un errore di overflow del contesto (in tal caso
OpenClaw compatta e riprova). Le tipiche firme di overflow includono
`request_too_large`, `context length exceeded`, `input exceeds the maximum
number of tokens`, `input token count exceeds the maximum number of input
tokens`, `input is too long for the model` e `ollama error: context length
exceeded`.

<Info>
Prima della compattazione, OpenClaw ricorda automaticamente all'agente di salvare note importanti
nei file di [memory](/it/concepts/memory). Questo evita la perdita di contesto.
</Info>

Usa l'impostazione `agents.defaults.compaction` nel tuo `openclaw.json` per configurare il comportamento della compattazione (modalità, token di destinazione, ecc.).
La sintesi della compattazione preserva per impostazione predefinita gli identificatori opachi (`identifierPolicy: "strict"`). Puoi modificarlo con `identifierPolicy: "off"` oppure fornire testo personalizzato con `identifierPolicy: "custom"` e `identifierInstructions`.

Facoltativamente, puoi specificare un modello diverso per la sintesi della compattazione tramite `agents.defaults.compaction.model`. Questo è utile quando il tuo modello principale è un modello locale o piccolo e vuoi che i riepiloghi di compattazione siano prodotti da un modello più capace. L'override accetta qualsiasi stringa `provider/model-id`:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "model": "openrouter/anthropic/claude-sonnet-4-6"
      }
    }
  }
}
```

Questo funziona anche con modelli locali, ad esempio un secondo modello Ollama dedicato alla sintesi o uno specialista della compattazione fine-tuned:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "model": "ollama/llama3.1:8b"
      }
    }
  }
}
```

Se non impostato, la compattazione usa il modello principale dell'agente.

## Provider di compattazione collegabili

I plugin possono registrare un provider di compattazione personalizzato tramite `registerCompactionProvider()` nell'API del plugin. Quando un provider è registrato e configurato, OpenClaw gli delega la sintesi invece di usare la pipeline LLM integrata.

Per usare un provider registrato, imposta l'id del provider nella tua configurazione:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "provider": "my-provider"
      }
    }
  }
}
```

L'impostazione di un `provider` forza automaticamente `mode: "safeguard"`. I provider ricevono le stesse istruzioni di compattazione e la stessa policy di preservazione degli identificatori del percorso integrato, e OpenClaw continua a preservare il contesto del suffisso dei turni recenti e dei turni divisi dopo l'output del provider. Se il provider fallisce o restituisce un risultato vuoto, OpenClaw torna alla sintesi LLM integrata.

## Compattazione automatica (attiva per impostazione predefinita)

Quando una sessione si avvicina o supera la finestra di contesto del modello, OpenClaw attiva la compattazione automatica e può riprovare la richiesta originale usando il contesto compattato.

Vedrai:

- `🧹 Auto-compaction complete` in modalità dettagliata
- `/status` che mostra `🧹 Compactions: <count>`

Prima della compattazione, OpenClaw può eseguire un turno di **scaricamento silenzioso della memoria** per archiviare
note persistenti su disco. Consulta [Memory](/it/concepts/memory) per dettagli e configurazione.

## Compattazione manuale

Digita `/compact` in qualsiasi chat per forzare una compattazione. Aggiungi istruzioni per guidare
il riepilogo:

```
/compact Focus on the API design decisions
```

## Uso di un modello diverso

Per impostazione predefinita, la compattazione usa il modello principale del tuo agente. Puoi usare un modello più
capace per ottenere riepiloghi migliori:

```json5
{
  agents: {
    defaults: {
      compaction: {
        model: "openrouter/anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

## Avviso di avvio della compattazione

Per impostazione predefinita, la compattazione viene eseguita in modo silenzioso. Per mostrare un breve avviso quando la compattazione
inizia, abilita `notifyUser`:

```json5
{
  agents: {
    defaults: {
      compaction: {
        notifyUser: true,
      },
    },
  },
}
```

Quando è abilitato, l'utente vede un breve messaggio (ad esempio, "Compacting
context...") all'inizio di ogni esecuzione della compattazione.

## Compattazione vs pruning

|                  | Compattazione                 | Pruning                         |
| ---------------- | ----------------------------- | -------------------------------- |
| **Cosa fa**      | Riassume la conversazione meno recente | Riduce i vecchi risultati degli strumenti |
| **Salvato?**     | Sì (nella trascrizione della sessione) | No (solo in memoria, per richiesta) |
| **Ambito**       | Intera conversazione          | Solo risultati degli strumenti   |

Il [pruning della sessione](/it/concepts/session-pruning) è un complemento più leggero che
riduce l'output degli strumenti senza riassumere.

## Risoluzione dei problemi

**Compatta troppo spesso?** La finestra di contesto del modello potrebbe essere piccola, oppure gli output degli strumenti
potrebbero essere grandi. Prova ad abilitare il
[pruning della sessione](/it/concepts/session-pruning).

**Il contesto sembra obsoleto dopo la compattazione?** Usa `/compact Focus on <topic>` per
guidare il riepilogo, oppure abilita il [memory flush](/it/concepts/memory) in modo che le note
persistano.

**Hai bisogno di ripartire da zero?** `/new` avvia una nuova sessione senza compattare.

Per la configurazione avanzata (token di riserva, preservazione degli identificatori, motori di
contesto personalizzati, compattazione lato server OpenAI), consulta
l'[Approfondimento sulla gestione delle sessioni](/it/reference/session-management-compaction).

## Correlati

- [Session](/it/concepts/session) — gestione e ciclo di vita della sessione
- [Session Pruning](/it/concepts/session-pruning) — riduzione dei risultati degli strumenti
- [Context](/it/concepts/context) — come viene costruito il contesto per i turni dell'agente
- [Hooks](/it/automation/hooks) — hook del ciclo di vita della compattazione (before_compaction, after_compaction)
