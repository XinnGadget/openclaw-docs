---
read_when:
    - Configurazione di Matrix in OpenClaw
    - Configurazione di E2EE e della verifica di Matrix
summary: Stato del supporto di Matrix, configurazione iniziale ed esempi di configurazione
title: Matrix
x-i18n:
    generated_at: "2026-04-09T01:29:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 28fc13c7620c1152200315ae69c94205da6de3180c53c814dd8ce03b5cb1758f
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix è un plugin di canale incluso in OpenClaw.
Usa il `matrix-js-sdk` ufficiale e supporta messaggi diretti, stanze, thread, contenuti multimediali, reazioni, sondaggi, posizione ed E2EE.

## Plugin incluso

Matrix è distribuito come plugin incluso nelle versioni correnti di OpenClaw, quindi le normali
build pacchettizzate non richiedono un'installazione separata.

Se utilizzi una build più vecchia o un'installazione personalizzata che esclude Matrix, installalo
manualmente:

Installa da npm:

```bash
openclaw plugins install @openclaw/matrix
```

Installa da un checkout locale:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Vedi [Plugins](/it/tools/plugin) per il comportamento dei plugin e le regole di installazione.

## Configurazione iniziale

1. Assicurati che il plugin Matrix sia disponibile.
   - Le versioni pacchettizzate correnti di OpenClaw lo includono già.
   - Le installazioni più vecchie o personalizzate possono aggiungerlo manualmente con i comandi sopra.
2. Crea un account Matrix sul tuo homeserver.
3. Configura `channels.matrix` con uno dei seguenti:
   - `homeserver` + `accessToken`, oppure
   - `homeserver` + `userId` + `password`.
4. Riavvia il gateway.
5. Avvia un messaggio diretto con il bot o invitalo in una stanza.
   - I nuovi inviti Matrix funzionano solo quando `channels.matrix.autoJoin` li consente.

Percorsi di configurazione interattiva:

```bash
openclaw channels add
openclaw configure --section channels
```

La procedura guidata di Matrix richiede:

- URL dell'homeserver
- metodo di autenticazione: token di accesso o password
- ID utente (solo autenticazione con password)
- nome dispositivo facoltativo
- se abilitare E2EE
- se configurare l'accesso alle stanze e l'ingresso automatico agli inviti

Comportamenti principali della procedura guidata:

- Se le variabili d'ambiente di autenticazione Matrix esistono già e quell'account non ha già l'autenticazione salvata nella configurazione, la procedura guidata offre una scorciatoia env per mantenere l'autenticazione nelle variabili d'ambiente.
- I nomi degli account vengono normalizzati all'ID account. Ad esempio, `Ops Bot` diventa `ops-bot`.
- Le voci della allowlist dei messaggi diretti accettano direttamente `@user:server`; i nomi visualizzati funzionano solo quando la ricerca live nella directory trova una corrispondenza esatta.
- Le voci della allowlist delle stanze accettano direttamente ID stanza e alias. Preferisci `!room:server` o `#alias:server`; i nomi non risolti vengono ignorati in fase di esecuzione dalla risoluzione della allowlist.
- In modalità allowlist per l'ingresso automatico agli inviti, usa solo destinazioni di invito stabili: `!roomId:server`, `#alias:server` o `*`. I nomi semplici delle stanze vengono rifiutati.
- Per risolvere i nomi delle stanze prima di salvare, usa `openclaw channels resolve --channel matrix "Project Room"`.

<Warning>
`channels.matrix.autoJoin` è impostato su `off` per impostazione predefinita.

Se lo lasci non impostato, il bot non entrerà nelle stanze invitate o nei nuovi inviti in stile messaggio diretto, quindi non apparirà in nuovi gruppi o messaggi diretti su invito a meno che tu non entri prima manualmente.

Imposta `autoJoin: "allowlist"` insieme a `autoJoinAllowlist` per limitare quali inviti accetta, oppure imposta `autoJoin: "always"` se vuoi che entri in ogni invito.

In modalità `allowlist`, `autoJoinAllowlist` accetta solo `!roomId:server`, `#alias:server` o `*`.
</Warning>

Esempio di allowlist:

```json5
{
  channels: {
    matrix: {
      autoJoin: "allowlist",
      autoJoinAllowlist: ["!ops:example.org", "#support:example.org"],
      groups: {
        "!ops:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

Entra in ogni invito:

```json5
{
  channels: {
    matrix: {
      autoJoin: "always",
    },
  },
}
```

Configurazione minima basata su token:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

Configurazione basata su password (il token viene memorizzato nella cache dopo il login):

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix memorizza nella cache le credenziali in `~/.openclaw/credentials/matrix/`.
L'account predefinito usa `credentials.json`; gli account con nome usano `credentials-<account>.json`.
Quando lì esistono credenziali memorizzate nella cache, OpenClaw considera Matrix come configurato per configurazione iniziale, doctor e rilevamento dello stato del canale, anche se l'autenticazione corrente non è impostata direttamente nella configurazione.

Equivalenti come variabili d'ambiente (usati quando la chiave di configurazione non è impostata):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

Per account non predefiniti, usa variabili d'ambiente con ambito account:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

Esempio per l'account `ops`:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

Per l'ID account normalizzato `ops-bot`, usa:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix effettua l'escape della punteggiatura negli ID account per mantenere le variabili d'ambiente con ambito prive di collisioni.
Ad esempio, `-` diventa `_X2D_`, quindi `ops-prod` viene mappato a `MATRIX_OPS_X2D_PROD_*`.

La procedura guidata interattiva offre la scorciatoia delle variabili d'ambiente solo quando tali variabili di autenticazione sono già presenti e l'account selezionato non ha già l'autenticazione Matrix salvata nella configurazione.

## Esempio di configurazione

Questa è una configurazione di base pratica con pairing per messaggi diretti, allowlist delle stanze ed E2EE abilitato:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        sessionScope: "per-room",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

`autoJoin` si applica a tutti gli inviti Matrix, inclusi gli inviti in stile messaggio diretto. OpenClaw non può
classificare in modo affidabile una stanza invitata come messaggio diretto o gruppo al momento dell'invito, quindi tutti gli inviti passano prima da `autoJoin`.
`dm.policy` si applica dopo che il bot è entrato e la stanza è stata classificata come messaggio diretto.

## Anteprime in streaming

Lo streaming delle risposte Matrix è facoltativo.

Imposta `channels.matrix.streaming` su `"partial"` quando vuoi che OpenClaw invii una singola anteprima live
della risposta, modifichi quell'anteprima sul posto mentre il modello genera testo e poi la finalizzi quando la
risposta è completata:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` è l'impostazione predefinita. OpenClaw attende la risposta finale e la invia una sola volta.
- `streaming: "partial"` crea un messaggio di anteprima modificabile per il blocco corrente dell'assistente usando normali messaggi di testo Matrix. Questo conserva il comportamento legacy di notifica basato sulla prima anteprima di Matrix, quindi i client standard possono notificare il primo testo dell'anteprima in streaming invece del blocco completato.
- `streaming: "quiet"` crea un'anteprima silenziosa modificabile per il blocco corrente dell'assistente. Usalo solo quando configuri anche regole push del destinatario per le modifiche finalizzate dell'anteprima.
- `blockStreaming: true` abilita messaggi di avanzamento Matrix separati. Con lo streaming dell'anteprima abilitato, Matrix mantiene la bozza live per il blocco corrente e conserva i blocchi completati come messaggi separati.
- Quando lo streaming dell'anteprima è attivo e `blockStreaming` è disattivato, Matrix modifica la bozza live sul posto e finalizza quello stesso evento quando il blocco o il turno termina.
- Se l'anteprima non entra più in un singolo evento Matrix, OpenClaw interrompe lo streaming dell'anteprima e torna alla consegna finale normale.
- Le risposte con contenuti multimediali continuano a inviare normalmente gli allegati. Se un'anteprima obsoleta non può più essere riutilizzata in sicurezza, OpenClaw la redige prima di inviare la risposta finale con contenuti multimediali.
- Le modifiche dell'anteprima comportano chiamate API Matrix aggiuntive. Lascia lo streaming disattivato se desideri il comportamento più conservativo rispetto ai limiti di frequenza.

`blockStreaming` non abilita da solo le anteprime di bozza.
Usa `streaming: "partial"` o `streaming: "quiet"` per le modifiche dell'anteprima; poi aggiungi `blockStreaming: true` solo se vuoi anche che i blocchi completati dell'assistente restino visibili come messaggi di avanzamento separati.

Se hai bisogno di notifiche Matrix standard senza regole push personalizzate, usa `streaming: "partial"` per il comportamento basato sulla prima anteprima oppure lascia `streaming` disattivato per la consegna solo finale. Con `streaming: "off"`:

- `blockStreaming: true` invia ogni blocco completato come normale messaggio Matrix con notifica.
- `blockStreaming: false` invia solo la risposta finale completata come normale messaggio Matrix con notifica.

### Regole push self-hosted per anteprime silenziose finalizzate

Se esegui la tua infrastruttura Matrix e vuoi che le anteprime silenziose notifichino solo quando un blocco o
una risposta finale è completata, imposta `streaming: "quiet"` e aggiungi una regola push per utente per le modifiche finalizzate dell'anteprima.

Di solito questa è una configurazione dell'utente destinatario, non una modifica di configurazione globale dell'homeserver:

Mappa rapida prima di iniziare:

- utente destinatario = la persona che deve ricevere la notifica
- utente bot = l'account Matrix OpenClaw che invia la risposta
- usa il token di accesso dell'utente destinatario per le chiamate API qui sotto
- fai corrispondere `sender` nella regola push con l'MXID completo dell'utente bot

1. Configura OpenClaw per usare anteprime silenziose:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. Assicurati che l'account destinatario riceva già le normali notifiche push Matrix. Le regole
   per le anteprime silenziose funzionano solo se quell'utente ha già pusher/dispositivi funzionanti.

3. Ottieni il token di accesso dell'utente destinatario.
   - Usa il token dell'utente ricevente, non quello del bot.
   - Riutilizzare un token di sessione client esistente è di solito il modo più semplice.
   - Se devi generare un nuovo token, puoi effettuare il login tramite la API standard Client-Server di Matrix:

```bash
curl -sS -X POST \
  "https://matrix.example.org/_matrix/client/v3/login" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "m.login.password",
    "identifier": {
      "type": "m.id.user",
      "user": "@alice:example.org"
    },
    "password": "REDACTED"
  }'
```

4. Verifica che l'account destinatario abbia già dei pusher:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

Se questo non restituisce pusher/dispositivi attivi, correggi prima le normali notifiche Matrix prima di aggiungere
la regola OpenClaw qui sotto.

OpenClaw contrassegna le modifiche finalizzate dell'anteprima di solo testo con:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. Crea una regola push di override per ogni account destinatario che deve ricevere queste notifiche:

```bash
curl -sS -X PUT \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname" \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "conditions": [
      { "kind": "event_match", "key": "type", "pattern": "m.room.message" },
      {
        "kind": "event_property_is",
        "key": "content.m\\.relates_to.rel_type",
        "value": "m.replace"
      },
      {
        "kind": "event_property_is",
        "key": "content.com\\.openclaw\\.finalized_preview",
        "value": true
      },
      { "kind": "event_match", "key": "sender", "pattern": "@bot:example.org" }
    ],
    "actions": [
      "notify",
      { "set_tweak": "sound", "value": "default" },
      { "set_tweak": "highlight", "value": false }
    ]
  }'
```

Sostituisci questi valori prima di eseguire il comando:

- `https://matrix.example.org`: URL di base del tuo homeserver
- `$USER_ACCESS_TOKEN`: token di accesso dell'utente ricevente
- `openclaw-finalized-preview-botname`: un ID regola univoco per questo bot per questo utente ricevente
- `@bot:example.org`: l'MXID del tuo bot Matrix OpenClaw, non l'MXID dell'utente ricevente

Importante per configurazioni multi-bot:

- Le regole push sono indicizzate da `ruleId`. Eseguire di nuovo `PUT` sullo stesso ID regola aggiorna quella singola regola.
- Se un utente ricevente deve ricevere notifiche da più account bot Matrix OpenClaw, crea una regola per bot con un ID regola univoco per ogni corrispondenza di sender.
- Un modello semplice è `openclaw-finalized-preview-<botname>`, ad esempio `openclaw-finalized-preview-ops` o `openclaw-finalized-preview-support`.

La regola viene valutata rispetto al mittente dell'evento:

- autentica con il token dell'utente ricevente
- fai corrispondere `sender` all'MXID del bot OpenClaw

6. Verifica che la regola esista:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Prova una risposta in streaming. In modalità silenziosa, la stanza dovrebbe mostrare una bozza di anteprima silenziosa e la modifica finale
   sul posto dovrebbe notificare quando il blocco o il turno termina.

Se in seguito devi rimuovere la regola, elimina lo stesso ID regola con il token dell'utente ricevente:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Note:

- Crea la regola con il token di accesso dell'utente ricevente, non con quello del bot.
- Le nuove regole `override` definite dall'utente vengono inserite prima delle regole di soppressione predefinite, quindi non serve alcun parametro di ordinamento aggiuntivo.
- Questo influisce solo sulle modifiche dell'anteprima di solo testo che OpenClaw può finalizzare sul posto in sicurezza. I fallback per i contenuti multimediali e per le anteprime obsolete usano ancora la consegna Matrix normale.
- Se `GET /_matrix/client/v3/pushers` non mostra pusher, l'utente non ha ancora una consegna push Matrix funzionante per questo account/dispositivo.

#### Synapse

Per Synapse, la configurazione sopra di solito è sufficiente da sola:

- Non è richiesta alcuna modifica speciale a `homeserver.yaml` per le notifiche delle anteprime OpenClaw finalizzate.
- Se la tua distribuzione Synapse invia già normali notifiche push Matrix, il token utente + la chiamata `pushrules` sopra sono il passaggio principale di configurazione.
- Se esegui Synapse dietro un reverse proxy o worker, assicurati che `/_matrix/client/.../pushrules/` raggiunga Synapse correttamente.
- Se esegui worker Synapse, assicurati che i pusher siano in buono stato. La consegna push è gestita dal processo principale o da `synapse.app.pusher` / worker pusher configurati.

#### Tuwunel

Per Tuwunel, usa lo stesso flusso di configurazione e la stessa chiamata API `pushrules` mostrati sopra:

- Non è richiesta alcuna configurazione specifica di Tuwunel per il marcatore di anteprima finalizzata stesso.
- Se le normali notifiche Matrix funzionano già per quell'utente, il token utente + la chiamata `pushrules` sopra sono il passaggio principale di configurazione.
- Se le notifiche sembrano scomparire mentre l'utente è attivo su un altro dispositivo, verifica se `suppress_push_when_active` è abilitato. Tuwunel ha aggiunto questa opzione in Tuwunel 1.4.2 il 12 settembre 2025 e può sopprimere intenzionalmente le notifiche push verso altri dispositivi mentre un dispositivo è attivo.

## Stanze bot-to-bot

Per impostazione predefinita, i messaggi Matrix provenienti da altri account Matrix OpenClaw configurati vengono ignorati.

Usa `allowBots` quando vuoi intenzionalmente traffico Matrix inter-agent:

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true` accetta messaggi da altri account bot Matrix configurati in stanze e messaggi diretti consentiti.
- `allowBots: "mentions"` accetta quei messaggi solo quando menzionano visibilmente questo bot nelle stanze. I messaggi diretti restano consentiti.
- `groups.<room>.allowBots` sovrascrive l'impostazione a livello account per una stanza.
- OpenClaw continua a ignorare i messaggi provenienti dallo stesso ID utente Matrix per evitare loop di autorisposta.
- Matrix qui non espone un flag bot nativo; OpenClaw considera "scritto da bot" come "inviato da un altro account Matrix configurato su questo gateway OpenClaw".

Usa allowlist rigide per le stanze e requisiti di menzione quando abiliti traffico bot-to-bot in stanze condivise.

## Crittografia e verifica

Nelle stanze crittografate (E2EE), gli eventi immagine in uscita usano `thumbnail_file` così le anteprime delle immagini vengono crittografate insieme all'allegato completo. Le stanze non crittografate continuano a usare `thumbnail_url` semplice. Non è necessaria alcuna configurazione: il plugin rileva automaticamente lo stato E2EE.

Abilita la crittografia:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

Controlla lo stato della verifica:

```bash
openclaw matrix verify status
```

Stato dettagliato (diagnostica completa):

```bash
openclaw matrix verify status --verbose
```

Includi la chiave di recupero memorizzata nell'output leggibile da macchina:

```bash
openclaw matrix verify status --include-recovery-key --json
```

Inizializza lo stato di cross-signing e verifica:

```bash
openclaw matrix verify bootstrap
```

Diagnostica dettagliata del bootstrap:

```bash
openclaw matrix verify bootstrap --verbose
```

Forza un reset completo dell'identità di cross-signing prima del bootstrap:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

Verifica questo dispositivo con una chiave di recupero:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

Dettagli dettagliati della verifica del dispositivo:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

Controlla lo stato di salute del backup delle chiavi della stanza:

```bash
openclaw matrix verify backup status
```

Diagnostica dettagliata dello stato di salute del backup:

```bash
openclaw matrix verify backup status --verbose
```

Ripristina le chiavi della stanza dal backup del server:

```bash
openclaw matrix verify backup restore
```

Diagnostica dettagliata del ripristino:

```bash
openclaw matrix verify backup restore --verbose
```

Elimina il backup corrente sul server e crea una nuova baseline del backup. Se la chiave del
backup memorizzata non può essere caricata correttamente, questo reset può anche ricreare lo storage segreto così
gli avvii a freddo futuri potranno caricare la nuova chiave di backup:

```bash
openclaw matrix verify backup reset --yes
```

Tutti i comandi `verify` sono concisi per impostazione predefinita (incluso il logging interno silenzioso dell'SDK) e mostrano diagnostica dettagliata solo con `--verbose`.
Usa `--json` per l'output completo leggibile da macchina negli script.

Nelle configurazioni multi-account, i comandi Matrix CLI usano l'account predefinito implicito di Matrix a meno che tu non passi `--account <id>`.
Se configuri più account con nome, imposta prima `channels.matrix.defaultAccount` oppure quelle operazioni CLI implicite si fermeranno e ti chiederanno di scegliere esplicitamente un account.
Usa `--account` ogni volta che vuoi che le operazioni di verifica o sui dispositivi puntino esplicitamente a un account con nome:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Quando la crittografia è disabilitata o non disponibile per un account con nome, gli avvisi Matrix e gli errori di verifica puntano alla chiave di configurazione di quell'account, ad esempio `channels.matrix.accounts.assistant.encryption`.

### Cosa significa "verificato"

OpenClaw considera questo dispositivo Matrix verificato solo quando è verificato dalla tua identità di cross-signing.
In pratica, `openclaw matrix verify status --verbose` espone tre segnali di attendibilità:

- `Locally trusted`: questo dispositivo è attendibile solo dal client corrente
- `Cross-signing verified`: l'SDK segnala il dispositivo come verificato tramite cross-signing
- `Signed by owner`: il dispositivo è firmato dalla tua stessa chiave di self-signing

`Verified by owner` diventa `yes` solo quando è presente la verifica tramite cross-signing o la firma del proprietario.
La fiducia locale da sola non è sufficiente perché OpenClaw tratti il dispositivo come completamente verificato.

### Cosa fa il bootstrap

`openclaw matrix verify bootstrap` è il comando di riparazione e configurazione per gli account Matrix crittografati.
Esegue tutto quanto segue in questo ordine:

- inizializza lo storage segreto, riutilizzando una chiave di recupero esistente quando possibile
- inizializza il cross-signing e carica le chiavi pubbliche di cross-signing mancanti
- tenta di contrassegnare e firmare tramite cross-signing il dispositivo corrente
- crea un nuovo backup lato server delle chiavi della stanza se non ne esiste già uno

Se l'homeserver richiede autenticazione interattiva per caricare le chiavi di cross-signing, OpenClaw prova prima il caricamento senza autenticazione, poi con `m.login.dummy`, poi con `m.login.password` quando `channels.matrix.password` è configurato.

Usa `--force-reset-cross-signing` solo quando vuoi intenzionalmente scartare l'identità di cross-signing corrente e crearne una nuova.

Se vuoi intenzionalmente scartare il backup corrente delle chiavi della stanza e iniziare una nuova
baseline di backup per i messaggi futuri, usa `openclaw matrix verify backup reset --yes`.
Fallo solo se accetti che la vecchia cronologia crittografata irrecuperabile resterà
non disponibile e che OpenClaw potrebbe ricreare lo storage segreto se l'attuale segreto di backup
non può essere caricato in sicurezza.

### Nuova baseline di backup

Se vuoi mantenere funzionanti i futuri messaggi crittografati e accetti di perdere la vecchia cronologia irrecuperabile, esegui questi comandi in ordine:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Aggiungi `--account <id>` a ogni comando quando vuoi puntare esplicitamente a un account Matrix con nome.

### Comportamento all'avvio

Quando `encryption: true`, Matrix imposta `startupVerification` su `"if-unverified"` per impostazione predefinita.
All'avvio, se questo dispositivo non è ancora verificato, Matrix richiederà l'autoverifica in un altro client Matrix,
salterà le richieste duplicate quando una è già in sospeso e applicherà un cooldown locale prima di riprovare dopo i riavvii.
I tentativi di richiesta falliti vengono ritentati prima, per impostazione predefinita, rispetto alla creazione riuscita di richieste.
Imposta `startupVerification: "off"` per disabilitare le richieste automatiche all'avvio, oppure regola `startupVerificationCooldownHours`
se vuoi una finestra di nuovo tentativo più breve o più lunga.

All'avvio viene eseguito automaticamente anche un passaggio conservativo di bootstrap crittografico.
Questo passaggio cerca prima di riutilizzare lo storage segreto e l'identità di cross-signing correnti ed evita di reimpostare il cross-signing a meno che tu non esegua un flusso esplicito di riparazione bootstrap.

Se all'avvio viene rilevato uno stato bootstrap non valido e `channels.matrix.password` è configurato, OpenClaw può tentare un percorso di riparazione più rigoroso.
Se il dispositivo corrente è già firmato dal proprietario, OpenClaw preserva quell'identità invece di reimpostarla automaticamente.

Vedi [Migrazione Matrix](/it/install/migrating-matrix) per il flusso completo di aggiornamento, i limiti, i comandi di recupero e i messaggi comuni di migrazione.

### Avvisi di verifica

Matrix pubblica gli avvisi del ciclo di vita della verifica direttamente nella stanza DM di verifica stretta come messaggi `m.notice`.
Questo include:

- avvisi di richiesta di verifica
- avvisi di verifica pronta (con istruzioni esplicite "Verifica tramite emoji")
- avvisi di inizio e completamento della verifica
- dettagli SAS (emoji e decimali) quando disponibili

Le richieste di verifica in arrivo da un altro client Matrix vengono tracciate e accettate automaticamente da OpenClaw.
Per i flussi di autoverifica, OpenClaw avvia automaticamente anche il flusso SAS quando la verifica tramite emoji diventa disponibile e conferma automaticamente il proprio lato.
Per le richieste di verifica da un altro utente/dispositivo Matrix, OpenClaw accetta automaticamente la richiesta e poi attende che il flusso SAS proceda normalmente.
Devi comunque confrontare l'emoji o il SAS decimale nel tuo client Matrix e confermare lì "Corrispondono" per completare la verifica.

OpenClaw non accetta automaticamente alla cieca flussi duplicati avviati da sé. All'avvio evita di creare una nuova richiesta quando è già in sospeso una richiesta di autoverifica.

Gli avvisi di protocollo/sistema di verifica non vengono inoltrati alla pipeline di chat dell'agente, quindi non producono `NO_REPLY`.

### Igiene dei dispositivi

Sul tuo account possono accumularsi vecchi dispositivi Matrix gestiti da OpenClaw e rendere più difficile comprendere l'attendibilità nelle stanze crittografate.
Elencali con:

```bash
openclaw matrix devices list
```

Rimuovi i dispositivi obsoleti gestiti da OpenClaw con:

```bash
openclaw matrix devices prune-stale
```

### Archivio crittografico

Matrix E2EE usa il percorso crittografico Rust ufficiale di `matrix-js-sdk` in Node, con `fake-indexeddb` come shim IndexedDB. Lo stato crittografico viene mantenuto in un file snapshot (`crypto-idb-snapshot.json`) e ripristinato all'avvio. Il file snapshot è uno stato di runtime sensibile memorizzato con permessi file restrittivi.

Lo stato di runtime crittografato si trova sotto radici per account, per utente e per hash del token in
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`.
Quella directory contiene lo storage di sincronizzazione (`bot-storage.json`), lo storage crittografico (`crypto/`),
il file della chiave di recupero (`recovery-key.json`), lo snapshot IndexedDB (`crypto-idb-snapshot.json`),
i binding dei thread (`thread-bindings.json`) e lo stato della verifica all'avvio (`startup-verification.json`).
Quando il token cambia ma l'identità dell'account resta la stessa, OpenClaw riutilizza la migliore radice esistente
per quella tupla account/homeserver/utente, così lo stato di sincronizzazione precedente, lo stato crittografico, i binding dei thread
e lo stato della verifica all'avvio restano visibili.

## Gestione del profilo

Aggiorna il profilo Matrix dell'account selezionato con:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Aggiungi `--account <id>` quando vuoi puntare esplicitamente a un account Matrix con nome.

Matrix accetta direttamente gli URL avatar `mxc://`. Quando passi un URL avatar `http://` o `https://`, OpenClaw lo carica prima su Matrix e memorizza l'URL `mxc://` risolto in `channels.matrix.avatarUrl` (o nell'override dell'account selezionato).

## Thread

Matrix supporta i thread Matrix nativi sia per le risposte automatiche sia per gli invii degli strumenti di messaggistica.

- `dm.sessionScope: "per-user"` (predefinito) mantiene l'instradamento dei DM Matrix nell'ambito del mittente, quindi più stanze DM possono condividere una sessione quando si risolvono allo stesso interlocutore.
- `dm.sessionScope: "per-room"` isola ogni stanza DM Matrix nella propria chiave di sessione continuando però a usare i normali controlli di autenticazione DM e allowlist.
- I binding espliciti delle conversazioni Matrix hanno comunque la precedenza su `dm.sessionScope`, quindi stanze e thread associati mantengono la sessione di destinazione scelta.
- `threadReplies: "off"` mantiene le risposte al livello superiore e mantiene i messaggi in arrivo nei thread sulla sessione padre.
- `threadReplies: "inbound"` risponde all'interno di un thread solo quando il messaggio in ingresso era già in quel thread.
- `threadReplies: "always"` mantiene le risposte delle stanze in un thread radicato nel messaggio che ha attivato l'azione e instrada quella conversazione tramite la sessione con ambito thread corrispondente a partire dal primo messaggio di attivazione.
- `dm.threadReplies` sovrascrive l'impostazione di livello superiore solo per i messaggi diretti. Ad esempio, puoi mantenere isolati i thread delle stanze mantenendo piatti i messaggi diretti.
- I messaggi in arrivo nei thread includono il messaggio radice del thread come contesto aggiuntivo per l'agente.
- Gli invii degli strumenti di messaggistica ereditano automaticamente il thread Matrix corrente quando la destinazione è la stessa stanza, o lo stesso utente DM di destinazione, a meno che non venga fornito un `threadId` esplicito.
- Il riutilizzo della stessa sessione per destinazione utente DM si attiva solo quando i metadati della sessione corrente dimostrano lo stesso interlocutore DM sullo stesso account Matrix; altrimenti OpenClaw torna al normale instradamento con ambito utente.
- Quando OpenClaw vede una stanza DM Matrix entrare in collisione con un'altra stanza DM sulla stessa sessione DM Matrix condivisa, pubblica in quella stanza un `m.notice` una sola volta con la via di fuga `/focus` quando i binding dei thread sono abilitati e con l'indicazione `dm.sessionScope`.
- I binding runtime dei thread sono supportati per Matrix. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` e `/acp spawn` associato a thread funzionano nelle stanze e nei DM Matrix.
- `/focus` di primo livello in stanza/DM Matrix crea un nuovo thread Matrix e lo associa alla sessione di destinazione quando `threadBindings.spawnSubagentSessions=true`.
- Eseguire `/focus` o `/acp spawn --thread here` all'interno di un thread Matrix esistente associa invece quel thread corrente.

## Binding delle conversazioni ACP

Le stanze Matrix, i DM e i thread Matrix esistenti possono essere trasformati in workspace ACP persistenti senza cambiare la superficie della chat.

Flusso rapido per operatori:

- Esegui `/acp spawn codex --bind here` all'interno del DM Matrix, della stanza o del thread esistente che vuoi continuare a usare.
- In un DM o in una stanza Matrix di primo livello, il DM/stanza corrente resta la superficie della chat e i messaggi futuri vengono instradati alla sessione ACP generata.
- All'interno di un thread Matrix esistente, `--bind here` associa quel thread corrente sul posto.
- `/new` e `/reset` reimpostano sul posto la stessa sessione ACP associata.
- `/acp close` chiude la sessione ACP e rimuove il binding.

Note:

- `--bind here` non crea un thread Matrix figlio.
- `threadBindings.spawnAcpSessions` è richiesto solo per `/acp spawn --thread auto|here`, dove OpenClaw deve creare o associare un thread Matrix figlio.

### Configurazione del binding dei thread

Matrix eredita i valori predefiniti globali da `session.threadBindings` e supporta anche override per canale:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

I flag di generazione associata ai thread Matrix sono opt-in:

- Imposta `threadBindings.spawnSubagentSessions: true` per consentire a `/focus` di primo livello di creare e associare nuovi thread Matrix.
- Imposta `threadBindings.spawnAcpSessions: true` per consentire a `/acp spawn --thread auto|here` di associare sessioni ACP ai thread Matrix.

## Reazioni

Matrix supporta azioni di reazione in uscita, notifiche di reazione in ingresso e reazioni di conferma in ingresso.

- Gli strumenti di reazione in uscita sono controllati da `channels["matrix"].actions.reactions`.
- `react` aggiunge una reazione a uno specifico evento Matrix.
- `reactions` elenca il riepilogo corrente delle reazioni per uno specifico evento Matrix.
- `emoji=""` rimuove le reazioni dell'account bot stesso su quell'evento.
- `remove: true` rimuove solo la reazione emoji specificata dall'account bot.

L'ambito della reazione di conferma viene risolto in questo ordine:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- fallback all'emoji dell'identità dell'agente

L'ambito di `ackReaction` viene risolto in questo ordine:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

La modalità delle notifiche di reazione viene risolta in questo ordine:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- predefinito: `own`

Comportamento:

- `reactionNotifications: "own"` inoltra gli eventi `m.reaction` aggiunti quando hanno come destinazione messaggi Matrix scritti dal bot.
- `reactionNotifications: "off"` disabilita gli eventi di sistema delle reazioni.
- Le rimozioni delle reazioni non vengono sintetizzate in eventi di sistema perché Matrix le espone come redazioni, non come rimozioni `m.reaction` autonome.

## Contesto della cronologia

- `channels.matrix.historyLimit` controlla quanti messaggi recenti della stanza vengono inclusi come `InboundHistory` quando un messaggio in una stanza Matrix attiva l'agente. Fa fallback a `messages.groupChat.historyLimit`; se entrambi non sono impostati, il valore effettivo predefinito è `0`. Imposta `0` per disabilitare.
- La cronologia delle stanze Matrix è limitata alla stanza. I DM continuano a usare la normale cronologia della sessione.
- La cronologia delle stanze Matrix è solo pending: OpenClaw mette in buffer i messaggi della stanza che non hanno ancora attivato una risposta, poi cattura quello stato quando arriva una menzione o un altro trigger.
- Il messaggio trigger corrente non è incluso in `InboundHistory`; resta nel corpo principale in ingresso per quel turno.
- I tentativi ripetuti sullo stesso evento Matrix riutilizzano lo snapshot originale della cronologia invece di spostarsi in avanti verso messaggi più recenti della stanza.

## Visibilità del contesto

Matrix supporta il controllo condiviso `contextVisibility` per il contesto supplementare della stanza, come il testo di risposta recuperato, le radici dei thread e la cronologia pending.

- `contextVisibility: "all"` è il valore predefinito. Il contesto supplementare viene mantenuto così come ricevuto.
- `contextVisibility: "allowlist"` filtra il contesto supplementare ai mittenti consentiti dai controlli di allowlist attivi della stanza/utente.
- `contextVisibility: "allowlist_quote"` si comporta come `allowlist`, ma mantiene comunque una risposta citata esplicita.

Questa impostazione influisce sulla visibilità del contesto supplementare, non sul fatto che il messaggio in ingresso stesso possa attivare una risposta.
L'autorizzazione del trigger continua a provenire da `groupPolicy`, `groups`, `groupAllowFrom` e dalle impostazioni della policy DM.

## Policy per DM e stanze

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

Vedi [Groups](/it/channels/groups) per il comportamento di menzione obbligatoria e allowlist.

Esempio di pairing per i DM Matrix:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Se un utente Matrix non approvato continua a inviarti messaggi prima dell'approvazione, OpenClaw riutilizza lo stesso codice di pairing in sospeso e può inviare di nuovo una risposta di promemoria dopo un breve cooldown invece di generarne uno nuovo.

Vedi [Pairing](/it/channels/pairing) per il flusso condiviso di pairing dei DM e il layout di archiviazione.

## Riparazione della stanza diretta

Se lo stato dei messaggi diretti va fuori sincronizzazione, OpenClaw può finire con mapping `m.direct` obsoleti che puntano a vecchie stanze individuali invece che al DM attivo. Ispeziona il mapping corrente per un peer con:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Riparalo con:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

Il flusso di riparazione:

- preferisce un DM stretto 1:1 già mappato in `m.direct`
- in fallback usa qualsiasi DM stretto 1:1 attualmente unito con quell'utente
- crea una nuova stanza diretta e riscrive `m.direct` se non esiste alcun DM integro

Il flusso di riparazione non elimina automaticamente le vecchie stanze. Seleziona solo il DM integro e aggiorna il mapping così i nuovi invii Matrix, gli avvisi di verifica e gli altri flussi di messaggistica diretta puntano di nuovo alla stanza corretta.

## Approvazioni exec

Matrix può fungere da client di approvazione nativo per un account Matrix. I controlli nativi
di instradamento DM/canale restano comunque nella configurazione delle approvazioni exec:

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (facoltativo; fa fallback a `channels.matrix.dm.allowFrom`)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, predefinito: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Gli approvatori devono essere ID utente Matrix come `@owner:example.org`. Matrix abilita automaticamente le approvazioni native quando `enabled` non è impostato o è `"auto"` e può essere risolto almeno un approvatore. Le approvazioni exec usano prima `execApprovals.approvers` e possono fare fallback a `channels.matrix.dm.allowFrom`. Le approvazioni plugin autorizzano tramite `channels.matrix.dm.allowFrom`. Imposta `enabled: false` per disabilitare esplicitamente Matrix come client di approvazione nativo. In caso contrario, le richieste di approvazione fanno fallback ad altre route di approvazione configurate o alla policy di fallback delle approvazioni.

L'instradamento nativo di Matrix supporta entrambi i tipi di approvazione:

- `channels.matrix.execApprovals.*` controlla la modalità nativa di fanout DM/canale per i prompt di approvazione Matrix.
- Le approvazioni exec usano l'insieme degli approvatori exec da `execApprovals.approvers` o `channels.matrix.dm.allowFrom`.
- Le approvazioni plugin usano la allowlist DM Matrix da `channels.matrix.dm.allowFrom`.
- Le scorciatoie con reazioni Matrix e gli aggiornamenti dei messaggi si applicano sia alle approvazioni exec sia a quelle plugin.

Regole di consegna:

- `target: "dm"` invia i prompt di approvazione ai DM degli approvatori
- `target: "channel"` rimanda il prompt alla stanza Matrix o al DM di origine
- `target: "both"` invia agli approvatori nei DM e alla stanza Matrix o al DM di origine

I prompt di approvazione Matrix inizializzano scorciatoie tramite reazioni sul messaggio di approvazione principale:

- `✅` = consenti una volta
- `❌` = nega
- `♾️` = consenti sempre quando quella decisione è permessa dalla policy exec effettiva

Gli approvatori possono reagire su quel messaggio oppure usare i comandi slash di fallback: `/approve <id> allow-once`, `/approve <id> allow-always` o `/approve <id> deny`.

Solo gli approvatori risolti possono approvare o negare. Per le approvazioni exec, la consegna nel canale include il testo del comando, quindi abilita `channel` o `both` solo in stanze fidate.

Override per account:

- `channels.matrix.accounts.<account>.execApprovals`

Documentazione correlata: [Approvazioni exec](/it/tools/exec-approvals)

## Multi-account

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

I valori di livello superiore di `channels.matrix` agiscono come valori predefiniti per gli account con nome, a meno che un account non li sovrascriva.
Puoi limitare una voce di stanza ereditata a un account Matrix con `groups.<room>.account`.
Le voci senza `account` restano condivise tra tutti gli account Matrix, e le voci con `account: "default"` continuano a funzionare quando l'account predefinito è configurato direttamente al livello superiore `channels.matrix.*`.
I valori predefiniti condivisi parziali di autenticazione non creano da soli un account predefinito implicito separato. OpenClaw sintetizza l'account `default` di livello superiore solo quando quel valore predefinito ha autenticazione aggiornata (`homeserver` più `accessToken`, oppure `homeserver` più `userId` e `password`); gli account con nome possono comunque restare rilevabili da `homeserver` più `userId` quando le credenziali memorizzate nella cache soddisfano l'autenticazione in seguito.
Se Matrix ha già esattamente un account con nome, oppure `defaultAccount` punta a una chiave di account con nome esistente, la promozione di riparazione/configurazione iniziale da account singolo a multi-account preserva quell'account invece di creare una nuova voce `accounts.default`. Solo le chiavi di autenticazione/bootstrap Matrix vengono spostate in quell'account promosso; le chiavi condivise della policy di consegna restano al livello superiore.
Imposta `defaultAccount` quando vuoi che OpenClaw preferisca un account Matrix con nome per l'instradamento implicito, i probe e le operazioni CLI.
Se configuri più account con nome, imposta `defaultAccount` oppure passa `--account <id>` per i comandi CLI che si basano sulla selezione implicita dell'account.
Passa `--account <id>` a `openclaw matrix verify ...` e `openclaw matrix devices ...` quando vuoi sovrascrivere quella selezione implicita per un singolo comando.

Vedi [Riferimento della configurazione](/it/gateway/configuration-reference#multi-account-all-channels) per il modello multi-account condiviso.

## Homeserver privati/LAN

Per impostazione predefinita, OpenClaw blocca gli homeserver Matrix privati/interni per protezione SSRF, a meno che tu
non faccia esplicitamente opt-in per account.

Se il tuo homeserver è in esecuzione su localhost, su un IP LAN/Tailscale o su un hostname interno, abilita
`network.dangerouslyAllowPrivateNetwork` per quell'account Matrix:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      network: {
        dangerouslyAllowPrivateNetwork: true,
      },
      accessToken: "syt_internal_xxx",
    },
  },
}
```

Esempio di configurazione tramite CLI:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

Questo opt-in consente solo destinazioni private/interne attendibili. Homeserver pubblici in chiaro come
`http://matrix.example.org:8008` restano bloccati. Preferisci `https://` quando possibile.

## Proxy del traffico Matrix

Se la tua distribuzione Matrix richiede un proxy HTTP(S) esplicito in uscita, imposta `channels.matrix.proxy`:

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

Gli account con nome possono sovrascrivere il valore predefinito di livello superiore con `channels.matrix.accounts.<id>.proxy`.
OpenClaw usa la stessa impostazione proxy per il traffico Matrix di runtime e per i probe dello stato dell'account.

## Risoluzione delle destinazioni

Matrix accetta queste forme di destinazione ovunque OpenClaw ti chieda una destinazione stanza o utente:

- Utenti: `@user:server`, `user:@user:server` o `matrix:user:@user:server`
- Stanze: `!room:server`, `room:!room:server` o `matrix:room:!room:server`
- Alias: `#alias:server`, `channel:#alias:server` o `matrix:channel:#alias:server`

La ricerca live nella directory usa l'account Matrix connesso:

- Le ricerche utente interrogano la directory utenti Matrix su quell'homeserver.
- Le ricerche stanza accettano direttamente ID stanza e alias espliciti, poi fanno fallback alla ricerca nei nomi delle stanze unite per quell'account.
- La ricerca per nome nelle stanze unite è best-effort. Se il nome di una stanza non può essere risolto in un ID o alias, viene ignorato dalla risoluzione della allowlist in fase di esecuzione.

## Riferimento della configurazione

- `enabled`: abilita o disabilita il canale.
- `name`: etichetta facoltativa per l'account.
- `defaultAccount`: ID account preferito quando sono configurati più account Matrix.
- `homeserver`: URL dell'homeserver, ad esempio `https://matrix.example.org`.
- `network.dangerouslyAllowPrivateNetwork`: consente a questo account Matrix di connettersi a homeserver privati/interni. Abilitalo quando l'homeserver si risolve in `localhost`, un IP LAN/Tailscale o un host interno come `matrix-synapse`.
- `proxy`: URL facoltativo del proxy HTTP(S) per il traffico Matrix. Gli account con nome possono sovrascrivere il valore predefinito di livello superiore con il proprio `proxy`.
- `userId`: ID utente Matrix completo, ad esempio `@bot:example.org`.
- `accessToken`: token di accesso per l'autenticazione basata su token. I valori in chiaro e i valori SecretRef sono supportati per `channels.matrix.accessToken` e `channels.matrix.accounts.<id>.accessToken` nei provider env/file/exec. Vedi [Gestione dei segreti](/it/gateway/secrets).
- `password`: password per il login basato su password. Sono supportati valori in chiaro e valori SecretRef.
- `deviceId`: ID dispositivo Matrix esplicito.
- `deviceName`: nome visualizzato del dispositivo per il login con password.
- `avatarUrl`: URL dell'avatar personale memorizzato per la sincronizzazione del profilo e gli aggiornamenti di `profile set`.
- `initialSyncLimit`: numero massimo di eventi recuperati durante la sincronizzazione di avvio.
- `encryption`: abilita E2EE.
- `allowlistOnly`: quando è `true`, aggiorna la policy delle stanze `open` a `allowlist` e forza tutte le policy DM attive eccetto `disabled` (incluse `pairing` e `open`) a `allowlist`. Non influisce sulle policy `disabled`.
- `allowBots`: consente messaggi da altri account Matrix OpenClaw configurati (`true` o `"mentions"`).
- `groupPolicy`: `open`, `allowlist` o `disabled`.
- `contextVisibility`: modalità di visibilità del contesto supplementare della stanza (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: allowlist di ID utente per il traffico nelle stanze. Le voci dovrebbero essere ID utente Matrix completi; i nomi non risolti vengono ignorati in fase di esecuzione.
- `historyLimit`: numero massimo di messaggi della stanza da includere come contesto della cronologia di gruppo. Fa fallback a `messages.groupChat.historyLimit`; se entrambi non sono impostati, il valore effettivo predefinito è `0`. Imposta `0` per disabilitare.
- `replyToMode`: `off`, `first`, `all` o `batched`.
- `markdown`: configurazione facoltativa del rendering Markdown per il testo Matrix in uscita.
- `streaming`: `off` (predefinito), `"partial"`, `"quiet"`, `true` o `false`. `"partial"` e `true` abilitano aggiornamenti di bozza basati sulla prima anteprima con normali messaggi di testo Matrix. `"quiet"` usa avvisi di anteprima senza notifica per configurazioni self-hosted con regole push. `false` equivale a `"off"`.
- `blockStreaming`: `true` abilita messaggi di avanzamento separati per i blocchi completati dell'assistente mentre lo streaming della bozza di anteprima è attivo.
- `threadReplies`: `off`, `inbound` o `always`.
- `threadBindings`: override per canale per l'instradamento e il ciclo di vita delle sessioni associate ai thread.
- `startupVerification`: modalità di richiesta automatica di autoverifica all'avvio (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: cooldown prima di ritentare richieste automatiche di verifica all'avvio.
- `textChunkLimit`: dimensione del chunk dei messaggi in uscita in caratteri (si applica quando `chunkMode` è `length`).
- `chunkMode`: `length` divide i messaggi per numero di caratteri; `newline` li divide ai confini di riga.
- `responsePrefix`: stringa facoltativa anteposta a tutte le risposte in uscita per questo canale.
- `ackReaction`: override facoltativo della reazione di conferma per questo canale/account.
- `ackReactionScope`: override facoltativo dell'ambito della reazione di conferma (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: modalità delle notifiche di reazione in ingresso (`own`, `off`).
- `mediaMaxMb`: limite di dimensione dei contenuti multimediali in MB per gli invii in uscita e l'elaborazione dei contenuti multimediali in ingresso.
- `autoJoin`: policy di ingresso automatico agli inviti (`always`, `allowlist`, `off`). Predefinito: `off`. Si applica a tutti gli inviti Matrix, inclusi gli inviti in stile messaggio diretto.
- `autoJoinAllowlist`: stanze/alias consentiti quando `autoJoin` è `allowlist`. Le voci alias vengono risolte in ID stanza durante la gestione dell'invito; OpenClaw non si fida dello stato dell'alias dichiarato dalla stanza invitata.
- `dm`: blocco della policy DM (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.policy`: controlla l'accesso ai messaggi diretti dopo che OpenClaw è entrato nella stanza e l'ha classificata come DM. Non cambia se un invito viene accettato automaticamente.
- `dm.allowFrom`: le voci dovrebbero essere ID utente Matrix completi, a meno che tu non li abbia già risolti tramite ricerca live nella directory.
- `dm.sessionScope`: `per-user` (predefinito) o `per-room`. Usa `per-room` quando vuoi che ogni stanza DM Matrix mantenga un contesto separato anche se l'interlocutore è lo stesso.
- `dm.threadReplies`: override della policy dei thread solo per DM (`off`, `inbound`, `always`). Sovrascrive l'impostazione `threadReplies` di livello superiore sia per il posizionamento delle risposte sia per l'isolamento delle sessioni nei DM.
- `execApprovals`: consegna nativa Matrix delle approvazioni exec (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: ID utente Matrix autorizzati ad approvare richieste exec. Facoltativo quando `dm.allowFrom` identifica già gli approvatori.
- `execApprovals.target`: `dm | channel | both` (predefinito: `dm`).
- `accounts`: override con nome per account. I valori di livello superiore di `channels.matrix` agiscono come valori predefiniti per queste voci.
- `groups`: mappa delle policy per stanza. Preferisci ID stanza o alias; i nomi delle stanze non risolti vengono ignorati in fase di esecuzione. L'identità di sessione/gruppo usa l'ID stanza stabile dopo la risoluzione.
- `groups.<room>.account`: limita una voce di stanza ereditata a uno specifico account Matrix nelle configurazioni multi-account.
- `groups.<room>.allowBots`: override a livello stanza per mittenti bot configurati (`true` o `"mentions"`).
- `groups.<room>.users`: allowlist dei mittenti per stanza.
- `groups.<room>.tools`: override di allow/deny degli strumenti per stanza.
- `groups.<room>.autoReply`: override a livello stanza del requisito di menzione. `true` disabilita i requisiti di menzione per quella stanza; `false` li riattiva forzatamente.
- `groups.<room>.skills`: filtro facoltativo delle Skills a livello stanza.
- `groups.<room>.systemPrompt`: snippet facoltativo di system prompt a livello stanza.
- `rooms`: alias legacy per `groups`.
- `actions`: gating degli strumenti per azione (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## Correlati

- [Panoramica dei canali](/it/channels) — tutti i canali supportati
- [Pairing](/it/channels/pairing) — autenticazione DM e flusso di pairing
- [Groups](/it/channels/groups) — comportamento delle chat di gruppo e gating delle menzioni
- [Instradamento del canale](/it/channels/channel-routing) — instradamento della sessione per i messaggi
- [Sicurezza](/it/gateway/security) — modello di accesso e hardening
