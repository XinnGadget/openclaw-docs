---
read_when:
    - Regolare la cadenza o i messaggi dell'heartbeat
    - Decidere tra heartbeat e cron per le attività pianificate
summary: Messaggi di polling heartbeat e regole di notifica
title: Heartbeat
x-i18n:
    generated_at: "2026-04-08T02:15:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: a8021d747637060eacb91ec5f75904368a08790c19f4fca32acda8c8c0a25e41
    source_path: gateway/heartbeat.md
    workflow: 15
---

# Heartbeat (Gateway)

> **Heartbeat o Cron?** Consulta [Automation & Tasks](/it/automation) per indicazioni su quando usare ciascuno.

Heartbeat esegue **turni periodici dell'agente** nella sessione principale in modo che il modello possa
far emergere tutto ciò che richiede attenzione senza inviarti spam.

Heartbeat è un turno pianificato della sessione principale — **non** crea record di [background task](/it/automation/tasks).
I record delle attività servono per il lavoro scollegato (esecuzioni ACP, subagent, processi cron isolati).

Risoluzione dei problemi: [Scheduled Tasks](/it/automation/cron-jobs#troubleshooting)

## Avvio rapido (principianti)

1. Lascia gli heartbeat abilitati (il valore predefinito è `30m`, oppure `1h` per l'autenticazione Anthropic OAuth/token, incluso il riutilizzo di Claude CLI) oppure imposta una tua cadenza.
2. Crea una piccola checklist `HEARTBEAT.md` o un blocco `tasks:` nell'area di lavoro dell'agente (opzionale ma consigliato).
3. Decidi dove devono andare i messaggi heartbeat (`target: "none"` è il valore predefinito; imposta `target: "last"` per instradare verso l'ultimo contatto).
4. Facoltativo: abilita la consegna del ragionamento heartbeat per maggiore trasparenza.
5. Facoltativo: usa un contesto bootstrap leggero se le esecuzioni heartbeat richiedono solo `HEARTBEAT.md`.
6. Facoltativo: abilita sessioni isolate per evitare di inviare l'intera cronologia della conversazione a ogni heartbeat.
7. Facoltativo: limita gli heartbeat alle ore attive (ora locale).

Configurazione di esempio:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // consegna esplicita all'ultimo contatto (il valore predefinito è "none")
        directPolicy: "allow", // predefinito: consenti target diretti/DM; imposta "block" per sopprimere
        lightContext: true, // facoltativo: inserisce solo HEARTBEAT.md dai file bootstrap
        isolatedSession: true, // facoltativo: sessione nuova a ogni esecuzione (senza cronologia della conversazione)
        // activeHours: { start: "08:00", end: "24:00" },
        // includeReasoning: true, // facoltativo: invia anche un messaggio `Reasoning:` separato
      },
    },
  },
}
```

## Valori predefiniti

- Intervallo: `30m` (oppure `1h` quando la modalità di autenticazione rilevata è Anthropic OAuth/token, incluso il riutilizzo di Claude CLI). Imposta `agents.defaults.heartbeat.every` o `agents.list[].heartbeat.every` per agente; usa `0m` per disabilitare.
- Corpo del prompt (configurabile tramite `agents.defaults.heartbeat.prompt`):
  `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
- Il prompt heartbeat viene inviato **verbatim** come messaggio utente. Il
  prompt di sistema include una sezione “Heartbeat” solo quando gli heartbeat sono abilitati per l'agente
  predefinito e l'esecuzione è contrassegnata internamente.
- Quando gli heartbeat sono disabilitati con `0m`, le esecuzioni normali omettono anche `HEARTBEAT.md`
  dal contesto bootstrap, così il modello non vede istruzioni solo per heartbeat.
- Le ore attive (`heartbeat.activeHours`) vengono controllate nel fuso orario configurato.
  Fuori dalla finestra, gli heartbeat vengono saltati fino al tick successivo all'interno della finestra.

## A cosa serve il prompt heartbeat

Il prompt predefinito è intenzionalmente ampio:

- **Attività in background**: “Consider outstanding tasks” spinge l'agente a esaminare
  i follow-up (posta in arrivo, calendario, promemoria, lavoro in coda) e a far emergere tutto ciò che è urgente.
- **Controllo umano**: “Checkup sometimes on your human during day time” spinge a
  un occasionale messaggio leggero del tipo “hai bisogno di qualcosa?”, ma evita spam notturno
  usando il tuo fuso orario locale configurato (consulta [/concepts/timezone](/it/concepts/timezone)).

Heartbeat può reagire a [background task](/it/automation/tasks) completati, ma un'esecuzione heartbeat di per sé non crea un record di attività.

Se vuoi che un heartbeat faccia qualcosa di molto specifico (ad esempio “controlla le statistiche Gmail PubSub”
o “verifica lo stato del gateway”), imposta `agents.defaults.heartbeat.prompt` (o
`agents.list[].heartbeat.prompt`) su un corpo personalizzato (inviato verbatim).

## Contratto di risposta

- Se nulla richiede attenzione, rispondi con **`HEARTBEAT_OK`**.
- Durante le esecuzioni heartbeat, OpenClaw tratta `HEARTBEAT_OK` come conferma quando compare
  all'**inizio o alla fine** della risposta. Il token viene rimosso e la risposta viene
  eliminata se il contenuto rimanente è **≤ `ackMaxChars`** (predefinito: 300).
- Se `HEARTBEAT_OK` compare nel **mezzo** di una risposta, non viene trattato
  in modo speciale.
- Per gli avvisi, **non** includere `HEARTBEAT_OK`; restituisci solo il testo dell'avviso.

Fuori dagli heartbeat, un `HEARTBEAT_OK` accidentale all'inizio/fine di un messaggio viene rimosso
e registrato; un messaggio che è solo `HEARTBEAT_OK` viene eliminato.

## Configurazione

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // predefinito: 30m (0m disabilita)
        model: "anthropic/claude-opus-4-6",
        includeReasoning: false, // predefinito: false (consegna un messaggio Reasoning: separato quando disponibile)
        lightContext: false, // predefinito: false; true mantiene solo HEARTBEAT.md dai file bootstrap dell'area di lavoro
        isolatedSession: false, // predefinito: false; true esegue ogni heartbeat in una sessione nuova (senza cronologia della conversazione)
        target: "last", // predefinito: none | opzioni: last | none | <channel id> (core o plugin, ad esempio "bluebubbles")
        to: "+15551234567", // override facoltativo specifico del canale
        accountId: "ops-bot", // id canale multi-account facoltativo
        prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        ackMaxChars: 300, // numero massimo di caratteri consentiti dopo HEARTBEAT_OK
      },
    },
  },
}
```

### Ambito e precedenza

- `agents.defaults.heartbeat` imposta il comportamento globale dell'heartbeat.
- `agents.list[].heartbeat` si unisce sopra; se un agente qualsiasi ha un blocco `heartbeat`, **solo quegli agenti** eseguono heartbeat.
- `channels.defaults.heartbeat` imposta i valori predefiniti di visibilità per tutti i canali.
- `channels.<channel>.heartbeat` sovrascrive i valori predefiniti del canale.
- `channels.<channel>.accounts.<id>.heartbeat` (canali multi-account) sovrascrive le impostazioni per canale.

### Heartbeat per agente

Se una qualunque voce `agents.list[]` include un blocco `heartbeat`, **solo quegli agenti**
eseguono heartbeat. Il blocco per agente si unisce sopra `agents.defaults.heartbeat`
(così puoi impostare una volta sola i valori condivisi e sovrascriverli per agente).

Esempio: due agenti, solo il secondo agente esegue heartbeat.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // consegna esplicita all'ultimo contatto (il valore predefinito è "none")
      },
    },
    list: [
      { id: "main", default: true },
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "whatsapp",
          to: "+15551234567",
          prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        },
      },
    ],
  },
}
```

### Esempio di ore attive

Limita gli heartbeat all'orario lavorativo in un fuso orario specifico:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // consegna esplicita all'ultimo contatto (il valore predefinito è "none")
        activeHours: {
          start: "09:00",
          end: "22:00",
          timezone: "America/New_York", // facoltativo; usa userTimezone se impostato, altrimenti il fuso orario dell'host
        },
      },
    },
  },
}
```

Fuori da questa finestra (prima delle 9:00 o dopo le 22:00 Eastern), gli heartbeat vengono saltati. Il tick pianificato successivo all'interno della finestra verrà eseguito normalmente.

### Configurazione 24/7

Se vuoi che gli heartbeat vengano eseguiti tutto il giorno, usa uno di questi schemi:

- Ometti del tutto `activeHours` (nessuna limitazione della finestra temporale; questo è il comportamento predefinito).
- Imposta una finestra per l'intera giornata: `activeHours: { start: "00:00", end: "24:00" }`.

Non impostare la stessa ora per `start` ed `end` (ad esempio da `08:00` a `08:00`).
Questo viene trattato come una finestra di larghezza zero, quindi gli heartbeat vengono sempre saltati.

### Esempio multi-account

Usa `accountId` per indirizzare un account specifico su canali multi-account come Telegram:

```json5
{
  agents: {
    list: [
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "telegram",
          to: "12345678:topic:42", // facoltativo: instrada verso un topic/thread specifico
          accountId: "ops-bot",
        },
      },
    ],
  },
  channels: {
    telegram: {
      accounts: {
        "ops-bot": { botToken: "YOUR_TELEGRAM_BOT_TOKEN" },
      },
    },
  },
}
```

### Note sui campi

- `every`: intervallo dell'heartbeat (stringa di durata; unità predefinita = minuti).
- `model`: override facoltativo del modello per le esecuzioni heartbeat (`provider/model`).
- `includeReasoning`: quando abilitato, consegna anche il messaggio separato `Reasoning:` quando disponibile (stessa forma di `/reasoning on`).
- `lightContext`: quando true, le esecuzioni heartbeat usano un contesto bootstrap leggero e mantengono solo `HEARTBEAT.md` dai file bootstrap dell'area di lavoro.
- `isolatedSession`: quando true, ogni heartbeat viene eseguito in una sessione nuova senza cronologia della conversazione precedente. Usa lo stesso schema di isolamento del cron `sessionTarget: "isolated"`. Riduce drasticamente il costo in token per heartbeat. Combinalo con `lightContext: true` per il massimo risparmio. L'instradamento della consegna usa comunque il contesto della sessione principale.
- `session`: chiave di sessione facoltativa per le esecuzioni heartbeat.
  - `main` (predefinito): sessione principale dell'agente.
  - Chiave di sessione esplicita (copiala da `openclaw sessions --json` o dalla [sessions CLI](/cli/sessions)).
  - Formati della chiave di sessione: consulta [Sessions](/it/concepts/session) e [Groups](/it/channels/groups).
- `target`:
  - `last`: consegna all'ultimo canale esterno usato.
  - canale esplicito: qualunque canale configurato o id plugin, ad esempio `discord`, `matrix`, `telegram` o `whatsapp`.
  - `none` (predefinito): esegue l'heartbeat ma **non consegna** all'esterno.
- `directPolicy`: controlla il comportamento di consegna diretta/DM:
  - `allow` (predefinito): consente la consegna diretta/DM dell'heartbeat.
  - `block`: sopprime la consegna diretta/DM (`reason=dm-blocked`).
- `to`: override facoltativo del destinatario (id specifico del canale, ad esempio E.164 per WhatsApp o un chat id Telegram). Per topic/thread Telegram, usa `<chatId>:topic:<messageThreadId>`.
- `accountId`: id account facoltativo per canali multi-account. Quando `target: "last"`, l'id account si applica all'ultimo canale risolto se supporta account; altrimenti viene ignorato. Se l'id account non corrisponde a un account configurato per il canale risolto, la consegna viene saltata.
- `prompt`: sovrascrive il corpo del prompt predefinito (non unito).
- `ackMaxChars`: numero massimo di caratteri consentiti dopo `HEARTBEAT_OK` prima della consegna.
- `suppressToolErrorWarnings`: quando true, sopprime i payload di avviso di errore degli strumenti durante le esecuzioni heartbeat.
- `activeHours`: limita le esecuzioni heartbeat a una finestra temporale. Oggetto con `start` (HH:MM, inclusivo; usa `00:00` per l'inizio del giorno), `end` (HH:MM esclusivo; `24:00` consentito per la fine del giorno) e `timezone` facoltativo.
  - Ometto o `"user"`: usa `agents.defaults.userTimezone` se impostato, altrimenti ricorre al fuso orario del sistema host.
  - `"local"`: usa sempre il fuso orario del sistema host.
  - Qualsiasi identificatore IANA (ad esempio `America/New_York`): usato direttamente; se non valido, ricade sul comportamento `"user"` descritto sopra.
  - `start` ed `end` non devono essere uguali per una finestra attiva; valori uguali vengono trattati come larghezza zero (sempre fuori dalla finestra).
  - Fuori dalla finestra attiva, gli heartbeat vengono saltati fino al tick successivo all'interno della finestra.

## Comportamento di consegna

- Gli heartbeat vengono eseguiti per impostazione predefinita nella sessione principale dell'agente (`agent:<id>:<mainKey>`),
  oppure `global` quando `session.scope = "global"`. Imposta `session` per sovrascrivere verso una
  sessione di canale specifica (Discord/WhatsApp/ecc.).
- `session` influisce solo sul contesto di esecuzione; la consegna è controllata da `target` e `to`.
- Per consegnare a un canale/destinatario specifico, imposta `target` + `to`. Con
  `target: "last"`, la consegna usa l'ultimo canale esterno per quella sessione.
- Le consegne heartbeat consentono target diretti/DM per impostazione predefinita. Imposta `directPolicy: "block"` per sopprimere gli invii a target diretti pur continuando a eseguire il turno heartbeat.
- Se la coda principale è occupata, l'heartbeat viene saltato e ritentato in seguito.
- Se `target` non si risolve in alcuna destinazione esterna, l'esecuzione avviene comunque ma non
  viene inviato alcun messaggio in uscita.
- Se `showOk`, `showAlerts` e `useIndicator` sono tutti disabilitati, l'esecuzione viene saltata subito come `reason=alerts-disabled`.
- Se è disabilitata solo la consegna degli avvisi, OpenClaw può comunque eseguire l'heartbeat, aggiornare i timestamp delle attività dovute, ripristinare il timestamp di inattività della sessione e sopprimere il payload dell'avviso esterno.
- Le risposte solo-heartbeat **non** mantengono attiva la sessione; l'ultimo `updatedAt`
  viene ripristinato in modo che la scadenza per inattività si comporti normalmente.
- I [background task](/it/automation/tasks) scollegati possono accodare un evento di sistema e riattivare heartbeat quando la sessione principale deve accorgersi rapidamente di qualcosa. Questa riattivazione non rende l'esecuzione heartbeat un'attività in background.

## Controlli di visibilità

Per impostazione predefinita, le conferme `HEARTBEAT_OK` vengono soppresse mentre il contenuto degli avvisi viene
consegnato. Puoi regolare questo comportamento per canale o per account:

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false # Nasconde HEARTBEAT_OK (predefinito)
      showAlerts: true # Mostra i messaggi di avviso (predefinito)
      useIndicator: true # Emette eventi indicatore (predefinito)
  telegram:
    heartbeat:
      showOk: true # Mostra le conferme OK su Telegram
  whatsapp:
    accounts:
      work:
        heartbeat:
          showAlerts: false # Sopprime la consegna degli avvisi per questo account
```

Precedenza: per-account → per-channel → valori predefiniti del canale → valori predefiniti integrati.

### Cosa fa ciascun flag

- `showOk`: invia una conferma `HEARTBEAT_OK` quando il modello restituisce una risposta solo-OK.
- `showAlerts`: invia il contenuto dell'avviso quando il modello restituisce una risposta non-OK.
- `useIndicator`: emette eventi indicatore per le superfici UI di stato.

Se **tutti e tre** sono false, OpenClaw salta completamente l'esecuzione heartbeat (nessuna chiamata al modello).

### Esempi per canale e per account

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false
      showAlerts: true
      useIndicator: true
  slack:
    heartbeat:
      showOk: true # tutti gli account Slack
    accounts:
      ops:
        heartbeat:
          showAlerts: false # sopprime gli avvisi solo per l'account ops
  telegram:
    heartbeat:
      showOk: true
```

### Schemi comuni

| Obiettivo                                | Configurazione                                                                           |
| ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| Comportamento predefinito (OK silenziosi, avvisi attivi) | _(nessuna configurazione necessaria)_                                                    |
| Completamente silenzioso (nessun messaggio, nessun indicatore) | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: false }` |
| Solo indicatore (nessun messaggio)       | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: true }`  |
| OK in un solo canale                     | `channels.telegram.heartbeat: { showOk: true }`                                          |

## HEARTBEAT.md (facoltativo)

Se esiste un file `HEARTBEAT.md` nell'area di lavoro, il prompt predefinito dice all'agente di
leggerlo. Consideralo come la tua “checklist heartbeat”: piccola, stabile e
sicura da includere ogni 30 minuti.

Nelle esecuzioni normali, `HEARTBEAT.md` viene inserito solo quando la guida heartbeat è
abilitata per l'agente predefinito. Disabilitare la cadenza heartbeat con `0m` o
impostare `includeSystemPromptSection: false` lo omette dal normale contesto bootstrap.

Se `HEARTBEAT.md` esiste ma è di fatto vuoto (solo righe vuote e intestazioni
Markdown come `# Heading`), OpenClaw salta l'esecuzione heartbeat per risparmiare chiamate API.
Questo salto viene riportato come `reason=empty-heartbeat-file`.
Se il file manca, l'heartbeat viene comunque eseguito e il modello decide cosa fare.

Tienilo piccolo (breve checklist o promemoria) per evitare di appesantire il prompt.

Esempio di `HEARTBEAT.md`:

```md
# Heartbeat checklist

- Quick scan: anything urgent in inboxes?
- If it’s daytime, do a lightweight check-in if nothing else is pending.
- If a task is blocked, write down _what is missing_ and ask Peter next time.
```

### Blocchi `tasks:`

`HEARTBEAT.md` supporta anche un piccolo blocco strutturato `tasks:` per controlli
basati su intervalli all'interno dello stesso heartbeat.

Esempio:

```md
tasks:

- name: inbox-triage
  interval: 30m
  prompt: "Check for urgent unread emails and flag anything time sensitive."
- name: calendar-scan
  interval: 2h
  prompt: "Check for upcoming meetings that need prep or follow-up."

# Additional instructions

- Keep alerts short.
- If nothing needs attention after all due tasks, reply HEARTBEAT_OK.
```

Comportamento:

- OpenClaw analizza il blocco `tasks:` e controlla ogni attività rispetto al proprio `interval`.
- Solo le attività **dovute** vengono incluse nel prompt heartbeat per quel tick.
- Se nessuna attività è dovuta, l'heartbeat viene saltato completamente (`reason=no-tasks-due`) per evitare una chiamata al modello sprecata.
- Il contenuto non relativo alle attività in `HEARTBEAT.md` viene conservato e aggiunto come contesto supplementare dopo l'elenco delle attività dovute.
- I timestamp dell'ultima esecuzione delle attività vengono memorizzati nello stato della sessione (`heartbeatTaskState`), così gli intervalli sopravvivono ai normali riavvii.
- I timestamp delle attività vengono avanzati solo dopo che un'esecuzione heartbeat completa il suo normale percorso di risposta. Le esecuzioni saltate `empty-heartbeat-file` / `no-tasks-due` non contrassegnano le attività come completate.

La modalità attività è utile quando vuoi che un solo file heartbeat contenga vari controlli periodici senza pagare per tutti a ogni tick.

### L'agente può aggiornare HEARTBEAT.md?

Sì — se glielo chiedi.

`HEARTBEAT.md` è semplicemente un file normale nell'area di lavoro dell'agente, quindi puoi dire all'agente
(in una chat normale) qualcosa come:

- “Aggiorna `HEARTBEAT.md` per aggiungere un controllo quotidiano del calendario.”
- “Riscrivi `HEARTBEAT.md` in modo che sia più breve e focalizzato sui follow-up della posta in arrivo.”

Se vuoi che questo accada in modo proattivo, puoi anche includere una riga esplicita nel
tuo prompt heartbeat come: “If the checklist becomes stale, update HEARTBEAT.md
with a better one.”

Nota sulla sicurezza: non inserire segreti (chiavi API, numeri di telefono, token privati) in
`HEARTBEAT.md` — entra a far parte del contesto del prompt.

## Riattivazione manuale (on-demand)

Puoi accodare un evento di sistema e attivare immediatamente un heartbeat con:

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
```

Se più agenti hanno `heartbeat` configurato, una riattivazione manuale esegue immediatamente gli
heartbeat di ciascuno di quegli agenti.

Usa `--mode next-heartbeat` per attendere il tick pianificato successivo.

## Consegna del ragionamento (facoltativa)

Per impostazione predefinita, gli heartbeat consegnano solo il payload finale di “risposta”.

Se vuoi trasparenza, abilita:

- `agents.defaults.heartbeat.includeReasoning: true`

Quando abilitato, gli heartbeat consegneranno anche un messaggio separato con prefisso
`Reasoning:` (stessa forma di `/reasoning on`). Questo può essere utile quando l'agente
gestisce più sessioni/codex e vuoi vedere perché ha deciso di contattarti
— ma può anche esporre più dettagli interni di quanto desideri. È preferibile lasciarlo
disattivato nelle chat di gruppo.

## Consapevolezza dei costi

Gli heartbeat eseguono turni completi dell'agente. Intervalli più brevi consumano più token. Per ridurre il costo:

- Usa `isolatedSession: true` per evitare di inviare l'intera cronologia della conversazione (da ~100K token fino a ~2-5K per esecuzione).
- Usa `lightContext: true` per limitare i file bootstrap al solo `HEARTBEAT.md`.
- Imposta un `model` più economico (ad esempio `ollama/llama3.2:1b`).
- Mantieni `HEARTBEAT.md` piccolo.
- Usa `target: "none"` se vuoi solo aggiornamenti dello stato interno.

## Correlati

- [Automation & Tasks](/it/automation) — tutti i meccanismi di automazione a colpo d'occhio
- [Background Tasks](/it/automation/tasks) — come viene tracciato il lavoro scollegato
- [Timezone](/it/concepts/timezone) — come il fuso orario influisce sulla pianificazione heartbeat
- [Troubleshooting](/it/automation/cron-jobs#troubleshooting) — debug dei problemi di automazione
