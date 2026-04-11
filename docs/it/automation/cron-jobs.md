---
read_when:
    - Pianificazione di processi in background o riattivazioni
    - Collegamento di trigger esterni (webhook, Gmail) a OpenClaw
    - Scegliere tra heartbeat e cron per le attività pianificate
summary: Processi pianificati, webhook e trigger Gmail PubSub per lo scheduler del Gateway
title: Attività pianificate
x-i18n:
    generated_at: "2026-04-11T02:44:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 04d94baa152de17d78515f7d545f099fe4810363ab67e06b465e489737f54665
    source_path: automation/cron-jobs.md
    workflow: 15
---

# Attività pianificate (Cron)

Cron è lo scheduler integrato del Gateway. Mantiene persistenti i processi, riattiva l'agente al momento giusto e può inviare l'output a un canale chat o a un endpoint webhook.

## Avvio rapido

```bash
# Aggiungi un promemoria una tantum
openclaw cron add \
  --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main \
  --system-event "Reminder: check the cron docs draft" \
  --wake now \
  --delete-after-run

# Controlla i tuoi processi
openclaw cron list

# Visualizza la cronologia delle esecuzioni
openclaw cron runs --id <job-id>
```

## Come funziona cron

- Cron viene eseguito **all'interno del processo Gateway** (non all'interno del modello).
- I processi vengono mantenuti persistenti in `~/.openclaw/cron/jobs.json`, quindi i riavvii non fanno perdere le pianificazioni.
- Tutte le esecuzioni cron creano record di [attività in background](/it/automation/tasks).
- I processi una tantum (`--at`) vengono eliminati automaticamente dopo il successo per impostazione predefinita.
- Le esecuzioni cron isolate chiudono, per quanto possibile, le schede/processi del browser tracciati per la loro sessione `cron:<jobId>` al termine dell'esecuzione, così l'automazione del browser scollegata non lascia processi orfani.
- Le esecuzioni cron isolate proteggono anche dalle risposte di conferma obsolete. Se il
  primo risultato è solo un aggiornamento di stato intermedio (`on it`, `pulling everything
together` e indicazioni simili) e nessuna esecuzione discendente di subagente è ancora
  responsabile della risposta finale, OpenClaw ripropone una volta la richiesta per il risultato
  effettivo prima della consegna.

<a id="maintenance"></a>

La riconciliazione delle attività per cron è gestita dal runtime: un'attività cron attiva resta tale finché il
runtime cron traccia ancora quel processo come in esecuzione, anche se esiste ancora una vecchia riga di sessione figlia.
Quando il runtime smette di possedere il processo e scade il periodo di tolleranza di 5 minuti, la manutenzione può
contrassegnare l'attività come `lost`.

## Tipi di pianificazione

| Tipo    | Flag CLI  | Descrizione                                                  |
| ------- | --------- | ------------------------------------------------------------ |
| `at`    | `--at`    | Timestamp una tantum (ISO 8601 o relativo come `20m`)        |
| `every` | `--every` | Intervallo fisso                                             |
| `cron`  | `--cron`  | Espressione cron a 5 o 6 campi con `--tz` facoltativo        |

I timestamp senza fuso orario vengono trattati come UTC. Aggiungi `--tz America/New_York` per la pianificazione in base all'orario locale.

Le espressioni ricorrenti all'inizio dell'ora vengono automaticamente sfalsate fino a 5 minuti per ridurre i picchi di carico. Usa `--exact` per forzare la temporizzazione precisa oppure `--stagger 30s` per una finestra esplicita.

## Stili di esecuzione

| Stile           | Valore `--session`   | Eseguito in              | Ideale per                      |
| --------------- | -------------------- | ------------------------ | ------------------------------- |
| Sessione principale | `main`           | Turno heartbeat successivo | Promemoria, eventi di sistema   |
| Isolato         | `isolated`           | `cron:<jobId>` dedicato  | Report, attività in background  |
| Sessione corrente | `current`          | Vincolato al momento della creazione | Lavoro ricorrente sensibile al contesto |
| Sessione personalizzata | `session:custom-id` | Sessione nominata persistente | Flussi di lavoro che si basano sulla cronologia |

I processi in **sessione principale** accodano un evento di sistema e facoltativamente risvegliano l'heartbeat (`--wake now` o `--wake next-heartbeat`). I processi **isolati** eseguono un turno agente dedicato con una sessione nuova. Le **sessioni personalizzate** (`session:xxx`) mantengono il contesto tra le esecuzioni, abilitando flussi di lavoro come standup giornalieri che si basano sui riepiloghi precedenti.

Per i processi isolati, lo smantellamento del runtime ora include la pulizia del browser per quella sessione cron, per quanto possibile. Gli errori di pulizia vengono ignorati in modo che prevalga comunque il risultato cron effettivo.

Quando le esecuzioni cron isolate orchestrano subagenti, la consegna privilegia anche l'output finale
discendente rispetto a testo intermedio obsoleto del padre. Se i discendenti sono ancora in esecuzione,
OpenClaw sopprime quell'aggiornamento parziale del padre invece di annunciarlo.

### Opzioni del payload per i processi isolati

- `--message`: testo del prompt (obbligatorio per isolato)
- `--model` / `--thinking`: override del modello e del livello di ragionamento
- `--light-context`: salta l'iniezione del file bootstrap del workspace
- `--tools exec,read`: limita quali strumenti il processo può usare

`--model` usa il modello consentito selezionato per quel processo. Se il modello richiesto
non è consentito, cron registra un avviso e torna invece alla selezione del modello
predefinito dell'agente/del processo. Le catene di fallback configurate continuano ad applicarsi, ma un semplice
override del modello senza un elenco di fallback esplicito per processo non aggiunge più il modello primario
dell'agente come destinazione aggiuntiva di nuovo tentativo nascosta.

La precedenza di selezione del modello per i processi isolati è:

1. Override del modello del hook Gmail (quando l'esecuzione proviene da Gmail e quell'override è consentito)
2. `model` del payload per processo
3. Override del modello della sessione cron memorizzata
4. Selezione del modello predefinita/dell'agente

La modalità rapida segue anch'essa la selezione live risolta. Se la configurazione del modello selezionato
ha `params.fastMode`, cron isolato la usa per impostazione predefinita. Un override `fastMode`
della sessione memorizzata continua comunque ad avere la precedenza in entrambe le direzioni.

Se un'esecuzione isolata incontra un passaggio live di cambio modello, cron ritenta con il
provider/modello cambiato e mantiene quella selezione live prima del nuovo tentativo. Quando
il cambio comporta anche un nuovo profilo auth, cron mantiene anche quell'override del profilo auth.
I tentativi sono limitati: dopo il tentativo iniziale più 2 tentativi dovuti al cambio, cron interrompe invece di entrare in un ciclo infinito.

## Consegna e output

| Modalità   | Cosa succede                                              |
| ---------- | --------------------------------------------------------- |
| `announce` | Invia un riepilogo al canale di destinazione (predefinito per isolato) |
| `webhook`  | Esegue una richiesta POST con il payload dell'evento completato a un URL |
| `none`     | Solo interno, nessuna consegna                            |

Usa `--announce --channel telegram --to "-1001234567890"` per la consegna al canale. Per gli argomenti del forum Telegram, usa `-1001234567890:topic:123`. Le destinazioni Slack/Discord/Mattermost devono usare prefissi espliciti (`channel:<id>`, `user:<id>`).

Per i processi isolati gestiti da cron, il runner possiede il percorso di consegna finale. All'agente
viene richiesto di restituire un riepilogo in testo semplice, e quel riepilogo viene poi inviato tramite
`announce`, `webhook` oppure mantenuto interno con `none`. `--no-deliver` non restituisce la
consegna all'agente; mantiene l'esecuzione interna.

Se l'attività originale indica esplicitamente di inviare un messaggio a un destinatario esterno,
l'agente deve indicare nel suo output a chi/dove quel messaggio deve andare invece di
provare a inviarlo direttamente.

Le notifiche di errore seguono un percorso di destinazione separato:

- `cron.failureDestination` imposta una destinazione predefinita globale per le notifiche di errore.
- `job.delivery.failureDestination` la sovrascrive per singolo processo.
- Se nessuna delle due è impostata e il processo già consegna tramite `announce`, le notifiche di errore ora usano come fallback quella destinazione principale di announce.
- `delivery.failureDestination` è supportato solo sui processi `sessionTarget="isolated"` a meno che la modalità di consegna principale non sia `webhook`.

## Esempi CLI

Promemoria una tantum (sessione principale):

```bash
openclaw cron add \
  --name "Calendar check" \
  --at "20m" \
  --session main \
  --system-event "Next heartbeat: check calendar." \
  --wake now
```

Processo isolato ricorrente con consegna:

```bash
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize overnight updates." \
  --announce \
  --channel slack \
  --to "channel:C1234567890"
```

Processo isolato con override di modello e ragionamento:

```bash
openclaw cron add \
  --name "Deep analysis" \
  --cron "0 6 * * 1" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Weekly deep analysis of project progress." \
  --model "opus" \
  --thinking high \
  --announce
```

## Webhook

Gateway può esporre endpoint webhook HTTP per trigger esterni. Abilita nella configurazione:

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
  },
}
```

### Autenticazione

Ogni richiesta deve includere il token del hook tramite header:

- `Authorization: Bearer <token>` (consigliato)
- `x-openclaw-token: <token>`

I token nella query string vengono rifiutati.

### POST /hooks/wake

Accoda un evento di sistema per la sessione principale:

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"New email received","mode":"now"}'
```

- `text` (obbligatorio): descrizione dell'evento
- `mode` (facoltativo): `now` (predefinito) oppure `next-heartbeat`

### POST /hooks/agent

Esegue un turno agente isolato:

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.4-mini"}'
```

Campi: `message` (obbligatorio), `name`, `agentId`, `wakeMode`, `deliver`, `channel`, `to`, `model`, `thinking`, `timeoutSeconds`.

### Hook mappati (POST /hooks/\<name\>)

I nomi hook personalizzati vengono risolti tramite `hooks.mappings` nella configurazione. Le mappature possono trasformare payload arbitrari in azioni `wake` o `agent` con template o trasformazioni tramite codice.

### Sicurezza

- Mantieni gli endpoint hook dietro loopback, tailnet o un reverse proxy fidato.
- Usa un token hook dedicato; non riutilizzare i token auth del gateway.
- Mantieni `hooks.path` su un sottopercorso dedicato; `/` viene rifiutato.
- Imposta `hooks.allowedAgentIds` per limitare il routing esplicito `agentId`.
- Mantieni `hooks.allowRequestSessionKey=false` a meno che tu non richieda sessioni selezionate dal chiamante.
- Se abiliti `hooks.allowRequestSessionKey`, imposta anche `hooks.allowedSessionKeyPrefixes` per vincolare le forme consentite della chiave di sessione.
- I payload hook vengono racchiusi entro limiti di sicurezza per impostazione predefinita.

## Integrazione Gmail PubSub

Collega i trigger della casella Gmail a OpenClaw tramite Google PubSub.

**Prerequisiti**: CLI `gcloud`, `gog` (gogcli), hook OpenClaw abilitati, Tailscale per l'endpoint HTTPS pubblico.

### Configurazione guidata (consigliata)

```bash
openclaw webhooks gmail setup --account openclaw@gmail.com
```

Questo scrive la configurazione `hooks.gmail`, abilita il preset Gmail e usa Tailscale Funnel per l'endpoint push.

### Avvio automatico del Gateway

Quando `hooks.enabled=true` e `hooks.gmail.account` è impostato, il Gateway avvia `gog gmail watch serve` all'avvio e rinnova automaticamente il watch. Imposta `OPENCLAW_SKIP_GMAIL_WATCHER=1` per disattivarlo.

### Configurazione manuale una tantum

1. Seleziona il progetto GCP che possiede il client OAuth usato da `gog`:

```bash
gcloud auth login
gcloud config set project <project-id>
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

2. Crea il topic e concedi a Gmail l'accesso push:

```bash
gcloud pubsub topics create gog-gmail-watch
gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

3. Avvia il watch:

```bash
gog gmail watch start \
  --account openclaw@gmail.com \
  --label INBOX \
  --topic projects/<project-id>/topics/gog-gmail-watch
```

### Override del modello Gmail

```json5
{
  hooks: {
    gmail: {
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

## Gestione dei processi

```bash
# Elenca tutti i processi
openclaw cron list

# Modifica un processo
openclaw cron edit <jobId> --message "Updated prompt" --model "opus"

# Forza l'esecuzione immediata di un processo
openclaw cron run <jobId>

# Esegui solo se è scaduto
openclaw cron run <jobId> --due

# Visualizza la cronologia delle esecuzioni
openclaw cron runs --id <jobId> --limit 50

# Elimina un processo
openclaw cron remove <jobId>

# Selezione dell'agente (configurazioni multi-agente)
openclaw cron add --name "Ops sweep" --cron "0 6 * * *" --session isolated --message "Check ops queue" --agent ops
openclaw cron edit <jobId> --clear-agent
```

Nota sull'override del modello:

- `openclaw cron add|edit --model ...` cambia il modello selezionato del processo.
- Se il modello è consentito, esattamente quel provider/modello raggiunge l'esecuzione
  dell'agente isolato.
- Se non è consentito, cron avvisa e torna alla selezione del modello
  predefinita dell'agente/del processo.
- Le catene di fallback configurate continuano ad applicarsi, ma un semplice override `--model` con
  nessun elenco di fallback esplicito per processo non passa più al modello
  primario dell'agente come destinazione aggiuntiva di nuovo tentativo silenziosa.

## Configurazione

```json5
{
  cron: {
    enabled: true,
    store: "~/.openclaw/cron/jobs.json",
    maxConcurrentRuns: 1,
    retry: {
      maxAttempts: 3,
      backoffMs: [60000, 120000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "server_error"],
    },
    webhookToken: "sostituisci-con-token-webhook-dedicato",
    sessionRetention: "24h",
    runLog: { maxBytes: "2mb", keepLines: 2000 },
  },
}
```

Disabilita cron: `cron.enabled: false` oppure `OPENCLAW_SKIP_CRON=1`.

**Nuovo tentativo per esecuzioni una tantum**: gli errori transitori (limite di frequenza, sovraccarico, rete, errore del server) vengono ritentati fino a 3 volte con backoff esponenziale. Gli errori permanenti disabilitano immediatamente.

**Nuovo tentativo per esecuzioni ricorrenti**: backoff esponenziale (da 30 s a 60 min) tra i tentativi. Il backoff si reimposta dopo l'esecuzione successiva riuscita.

**Manutenzione**: `cron.sessionRetention` (predefinito `24h`) elimina le voci di sessione delle esecuzioni isolate. `cron.runLog.maxBytes` / `cron.runLog.keepLines` eliminano automaticamente i file del log di esecuzione.

## Risoluzione dei problemi

### Sequenza di comandi

```bash
openclaw status
openclaw gateway status
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
openclaw doctor
```

### Cron non si attiva

- Controlla `cron.enabled` e la variabile d'ambiente `OPENCLAW_SKIP_CRON`.
- Conferma che il Gateway sia in esecuzione continua.
- Per le pianificazioni `cron`, verifica il fuso orario (`--tz`) rispetto al fuso orario dell'host.
- `reason: not-due` nell'output di esecuzione significa che l'esecuzione manuale è stata controllata con `openclaw cron run <jobId> --due` e che il processo non era ancora in scadenza.

### Cron si è attivato ma non c'è consegna

- La modalità di consegna `none` significa che non è previsto alcun messaggio esterno.
- Una destinazione di consegna mancante/non valida (`channel`/`to`) significa che l'invio in uscita è stato saltato.
- Gli errori di autenticazione del canale (`unauthorized`, `Forbidden`) significano che la consegna è stata bloccata dalle credenziali.
- Se l'esecuzione isolata restituisce solo il token silenzioso (`NO_REPLY` / `no_reply`),
  OpenClaw sopprime la consegna diretta in uscita e sopprime anche il percorso di fallback
  del riepilogo accodato, quindi non viene pubblicato nulla nella chat.
- Per i processi isolati gestiti da cron, non aspettarti che l'agente usi lo strumento di messaggistica
  come fallback. Il runner gestisce la consegna finale; `--no-deliver` la mantiene
  interna invece di consentire un invio diretto.

### Insidie del fuso orario

- Cron senza `--tz` usa il fuso orario dell'host del gateway.
- Le pianificazioni `at` senza fuso orario vengono trattate come UTC.
- `activeHours` di heartbeat usa la risoluzione del fuso orario configurata.

## Correlati

- [Automazione e attività](/it/automation) — tutti i meccanismi di automazione in sintesi
- [Attività in background](/it/automation/tasks) — registro delle attività per le esecuzioni cron
- [Heartbeat](/it/gateway/heartbeat) — turni periodici della sessione principale
- [Fuso orario](/it/concepts/timezone) — configurazione del fuso orario
