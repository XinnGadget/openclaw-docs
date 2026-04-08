---
read_when:
    - Configurazione di Matrix in OpenClaw
    - Configurazione di Matrix E2EE e verifica
summary: Stato del supporto Matrix, configurazione iniziale ed esempi di configurazione
title: Matrix
x-i18n:
    generated_at: "2026-04-08T02:16:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: ec926df79a41fa296d63f0ec7219d0f32e075628d76df9ea490e93e4c5030f83
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix è il plugin canale Matrix integrato per OpenClaw.
Usa il `matrix-js-sdk` ufficiale e supporta DM, stanze, thread, contenuti multimediali, reazioni, sondaggi, posizione ed E2EE.

## Plugin integrato

Matrix è distribuito come plugin integrato nelle attuali release di OpenClaw, quindi le normali
build pacchettizzate non richiedono un'installazione separata.

Se usi una build più vecchia o un'installazione personalizzata che esclude Matrix, installalo
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
   - Le attuali release pacchettizzate di OpenClaw lo includono già.
   - Le installazioni vecchie/personalizzate possono aggiungerlo manualmente con i comandi sopra.
2. Crea un account Matrix sul tuo homeserver.
3. Configura `channels.matrix` con uno dei seguenti:
   - `homeserver` + `accessToken`, oppure
   - `homeserver` + `userId` + `password`.
4. Riavvia il gateway.
5. Avvia un DM con il bot oppure invitalo in una stanza.
   - I nuovi inviti Matrix funzionano solo quando `channels.matrix.autoJoin` li consente.

Percorsi di configurazione interattiva:

```bash
openclaw channels add
openclaw configure --section channels
```

Cosa chiede realmente la procedura guidata Matrix:

- URL dell'homeserver
- metodo di autenticazione: access token o password
- ID utente solo se scegli l'autenticazione con password
- nome del dispositivo facoltativo
- se abilitare E2EE
- se configurare ora l'accesso alle stanze Matrix
- se configurare ora l'accesso automatico agli inviti Matrix
- quando l'accesso automatico agli inviti è abilitato, se deve essere `allowlist`, `always` oppure `off`

Comportamento della procedura guidata da tenere presente:

- Se per l'account selezionato esistono già variabili d'ambiente di autenticazione Matrix, e per quell'account l'autenticazione non è già salvata nella configurazione, la procedura guidata offre una scorciatoia tramite env così la configurazione può mantenere l'autenticazione nelle variabili d'ambiente invece di copiare i segreti nella configurazione.
- Quando aggiungi interattivamente un altro account Matrix, il nome dell'account inserito viene normalizzato nell'ID account usato nella configurazione e nelle variabili d'ambiente. Per esempio, `Ops Bot` diventa `ops-bot`.
- I prompt della allowlist per i DM accettano subito valori completi `@user:server`. I nomi visualizzati funzionano solo quando la ricerca live nella directory trova una sola corrispondenza esatta; altrimenti la procedura guidata ti chiede di riprovare con un ID Matrix completo.
- I prompt della allowlist per le stanze accettano direttamente ID stanza e alias. Possono anche risolvere live i nomi delle stanze unite, ma i nomi non risolti vengono mantenuti solo come inseriti durante la configurazione e poi ignorati dalla risoluzione della allowlist a runtime. Preferisci `!room:server` o `#alias:server`.
- La procedura guidata ora mostra un avviso esplicito prima del passaggio di accesso automatico agli inviti perché `channels.matrix.autoJoin` ha valore predefinito `off`; gli agent non si uniranno a stanze invitate o a nuovi inviti in stile DM a meno che tu non lo imposti.
- In modalità allowlist per l'accesso automatico agli inviti, usa solo destinazioni di invito stabili: `!roomId:server`, `#alias:server` oppure `*`. I nomi semplici delle stanze vengono rifiutati.
- L'identità di stanza/sessione a runtime usa l'ID stanza Matrix stabile. Gli alias dichiarati dalla stanza vengono usati solo come input di ricerca, non come chiave di sessione a lungo termine o identità stabile del gruppo.
- Per risolvere i nomi delle stanze prima di salvarli, usa `openclaw channels resolve --channel matrix "Project Room"`.

<Warning>
`channels.matrix.autoJoin` ha valore predefinito `off`.

Se lo lasci non impostato, il bot non si unirà alle stanze invitate o ai nuovi inviti in stile DM, quindi non apparirà in nuovi gruppi o DM invitati a meno che tu non lo faccia unire manualmente prima.

Imposta `autoJoin: "allowlist"` insieme a `autoJoinAllowlist` per limitare quali inviti accetta, oppure imposta `autoJoin: "always"` se vuoi che si unisca a ogni invito.

In modalità `allowlist`, `autoJoinAllowlist` accetta solo `!roomId:server`, `#alias:server` oppure `*`.
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

Unisciti a ogni invito:

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

Matrix memorizza le credenziali in cache in `~/.openclaw/credentials/matrix/`.
L'account predefinito usa `credentials.json`; gli account con nome usano `credentials-<account>.json`.
Quando lì esistono credenziali in cache, OpenClaw considera Matrix configurato per setup, doctor e rilevamento dello stato del canale anche se l'autenticazione corrente non è impostata direttamente nella configurazione.

Equivalenti tramite variabili d'ambiente (usati quando la chiave di configurazione non è impostata):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

Per gli account non predefiniti, usa variabili d'ambiente con ambito account:

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

Matrix esegue l'escape della punteggiatura negli ID account per evitare collisioni nelle variabili d'ambiente con ambito account.
Per esempio, `-` diventa `_X2D_`, quindi `ops-prod` viene mappato a `MATRIX_OPS_X2D_PROD_*`.

La procedura guidata interattiva offre la scorciatoia tramite variabili d'ambiente solo quando quelle variabili d'ambiente di autenticazione sono già presenti e l'account selezionato non ha già l'autenticazione Matrix salvata nella configurazione.

## Esempio di configurazione

Questa è una configurazione di base pratica con pairing DM, allowlist delle stanze ed E2EE abilitato:

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

`autoJoin` si applica agli inviti Matrix in generale, non solo agli inviti di stanze/gruppi.
Questo include i nuovi inviti in stile DM. Al momento dell'invito, OpenClaw non sa in modo affidabile se la
stanza invitata verrà trattata come DM o gruppo, quindi tutti gli inviti passano prima attraverso la stessa
decisione `autoJoin`. `dm.policy` si applica comunque dopo che il bot si è unito e la stanza viene
classificata come DM, quindi `autoJoin` controlla il comportamento di unione mentre `dm.policy` controlla il comportamento
di risposta/accesso.

## Anteprime in streaming

Lo streaming delle risposte Matrix è facoltativo.

Imposta `channels.matrix.streaming` su `"partial"` quando vuoi che OpenClaw invii una singola anteprima live
della risposta, modifichi quell'anteprima sul posto mentre il modello genera testo e poi la
finalizzi quando la risposta è pronta:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` è il valore predefinito. OpenClaw attende la risposta finale e la invia una sola volta.
- `streaming: "partial"` crea un messaggio di anteprima modificabile per il blocco corrente dell'assistente usando normali messaggi di testo Matrix. Questo preserva il comportamento legacy di notifica all'anteprima iniziale di Matrix, quindi i client standard possono notificare sul primo testo dell'anteprima in streaming invece che sul blocco completato.
- `streaming: "quiet"` crea un'anteprima silenziosa modificabile per il blocco corrente dell'assistente. Usalo solo quando configuri anche regole push dei destinatari per le modifiche finalizzate dell'anteprima.
- `blockStreaming: true` abilita messaggi di avanzamento Matrix separati. Con lo streaming di anteprima abilitato, Matrix mantiene la bozza live per il blocco corrente e conserva i blocchi completati come messaggi separati.
- Quando lo streaming di anteprima è attivo e `blockStreaming` è disattivato, Matrix modifica la bozza live sul posto e finalizza quello stesso evento quando il blocco o il turno termina.
- Se l'anteprima non entra più in un singolo evento Matrix, OpenClaw interrompe lo streaming dell'anteprima e torna alla normale consegna finale.
- Le risposte multimediali continuano a inviare normalmente gli allegati. Se un'anteprima obsoleta non può più essere riutilizzata in sicurezza, OpenClaw la redige prima di inviare la risposta multimediale finale.
- Le modifiche delle anteprime comportano chiamate API Matrix aggiuntive. Lascia lo streaming disattivato se vuoi il comportamento più conservativo rispetto ai limiti di frequenza.

`blockStreaming` da solo non abilita le anteprime in bozza.
Usa `streaming: "partial"` o `streaming: "quiet"` per le modifiche di anteprima; poi aggiungi `blockStreaming: true` solo se vuoi anche che i blocchi completati dell'assistente restino visibili come messaggi di avanzamento separati.

Se hai bisogno delle notifiche standard di Matrix senza regole push personalizzate, usa `streaming: "partial"` per il comportamento con anteprima iniziale oppure lascia `streaming` disattivato per la consegna solo finale. Con `streaming: "off"`:

- `blockStreaming: true` invia ogni blocco completato come un normale messaggio Matrix con notifica.
- `blockStreaming: false` invia solo la risposta finale completata come un normale messaggio Matrix con notifica.

### Regole push self-hosted per anteprime finalizzate silenziose

Se gestisci la tua infrastruttura Matrix e vuoi che le anteprime silenziose notifichino solo quando un blocco o la
risposta finale è terminata, imposta `streaming: "quiet"` e aggiungi una regola push per utente per le modifiche finalizzate dell'anteprima.

Di solito è una configurazione dell'utente destinatario, non una modifica globale della configurazione dell'homeserver:

Mappa rapida prima di iniziare:

- utente destinatario = la persona che deve ricevere la notifica
- utente bot = l'account Matrix OpenClaw che invia la risposta
- usa l'access token dell'utente destinatario per le chiamate API qui sotto
- fai corrispondere `sender` nella regola push all'MXID completo dell'utente bot

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

2. Assicurati che l'account del destinatario riceva già le normali notifiche push Matrix. Le regole
   delle anteprime silenziose funzionano solo se quell'utente ha già pusher/dispositivi funzionanti.

3. Ottieni l'access token dell'utente destinatario.
   - Usa il token dell'utente ricevente, non il token del bot.
   - Riutilizzare il token di una sessione client esistente è di solito la soluzione più semplice.
   - Se devi generare un token nuovo, puoi effettuare il login tramite la normale API Client-Server Matrix:

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

Se questo non restituisce pusher/dispositivi attivi, correggi prima le normali notifiche Matrix prima di aggiungere la
regola OpenClaw qui sotto.

OpenClaw contrassegna le modifiche finalizzate delle anteprime solo testuali con:

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
- `$USER_ACCESS_TOKEN`: access token dell'utente ricevente
- `openclaw-finalized-preview-botname`: un ID regola univoco per questo bot per questo utente ricevente
- `@bot:example.org`: l'MXID del tuo bot Matrix OpenClaw, non l'MXID dell'utente ricevente

Importante per configurazioni con più bot:

- Le regole push sono indicate da `ruleId`. Rieseguire `PUT` sullo stesso ID regola aggiorna quella singola regola.
- Se un utente ricevente deve notificare per più account bot Matrix OpenClaw, crea una regola per bot con un ID regola univoco per ogni corrispondenza di sender.
- Un modello semplice è `openclaw-finalized-preview-<botname>`, come `openclaw-finalized-preview-ops` o `openclaw-finalized-preview-support`.

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
   sul posto dovrebbe notificare una volta terminato il blocco o il turno.

Se devi rimuovere la regola in seguito, elimina lo stesso ID regola con il token dell'utente ricevente:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Note:

- Crea la regola con l'access token dell'utente ricevente, non con quello del bot.
- Le nuove regole `override` definite dall'utente vengono inserite prima delle regole di soppressione predefinite, quindi non è necessario alcun parametro di ordinamento aggiuntivo.
- Questo influisce solo sulle modifiche delle anteprime solo testuali che OpenClaw può finalizzare in sicurezza sul posto. I fallback per i contenuti multimediali e quelli per anteprime obsolete usano comunque la normale consegna Matrix.
- Se `GET /_matrix/client/v3/pushers` non mostra pusher, l'utente non ha ancora una consegna push Matrix funzionante per questo account/dispositivo.

#### Synapse

Per Synapse, la configurazione sopra di solito è sufficiente da sola:

- Non è richiesta alcuna modifica speciale a `homeserver.yaml` per le notifiche delle anteprime finalizzate di OpenClaw.
- Se la tua distribuzione Synapse invia già le normali notifiche push Matrix, il token utente + la chiamata `pushrules` qui sopra sono il passaggio di configurazione principale.
- Se esegui Synapse dietro un reverse proxy o worker, assicurati che `/_matrix/client/.../pushrules/` raggiunga correttamente Synapse.
- Se usi worker Synapse, assicurati che i pusher siano in stato sano. La consegna push è gestita dal processo principale oppure da `synapse.app.pusher` / worker pusher configurati.

#### Tuwunel

Per Tuwunel, usa lo stesso flusso di configurazione e la stessa chiamata API `pushrules` mostrata sopra:

- Non è richiesta alcuna configurazione specifica di Tuwunel per il marcatore delle anteprime finalizzate.
- Se le normali notifiche Matrix funzionano già per quell'utente, il token utente + la chiamata `pushrules` qui sopra sono il passaggio di configurazione principale.
- Se le notifiche sembrano sparire mentre l'utente è attivo su un altro dispositivo, verifica se `suppress_push_when_active` è abilitato. Tuwunel ha aggiunto questa opzione in Tuwunel 1.4.2 il 12 settembre 2025 e può sopprimere intenzionalmente le notifiche push verso altri dispositivi mentre un dispositivo è attivo.

## Crittografia e verifica

Nelle stanze cifrate (E2EE), gli eventi immagine in uscita usano `thumbnail_file` così le anteprime immagine sono cifrate insieme all'allegato completo. Le stanze non cifrate continuano a usare `thumbnail_url` semplice. Non è richiesta alcuna configurazione: il plugin rileva automaticamente lo stato E2EE.

### Stanze bot-to-bot

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

- `allowBots: true` accetta messaggi da altri account bot Matrix configurati in stanze e DM consentiti.
- `allowBots: "mentions"` accetta quei messaggi solo quando menzionano visibilmente questo bot nelle stanze. I DM restano comunque consentiti.
- `groups.<room>.allowBots` sovrascrive l'impostazione a livello account per una singola stanza.
- OpenClaw continua a ignorare i messaggi provenienti dallo stesso ID utente Matrix per evitare loop di autorisposta.
- Matrix qui non espone un flag bot nativo; OpenClaw considera "scritto da un bot" come "inviato da un altro account Matrix configurato su questo gateway OpenClaw".

Usa allowlist rigorose delle stanze e requisiti di menzione quando abiliti traffico bot-to-bot in stanze condivise.

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

Includi la recovery key memorizzata nell'output leggibile da macchina:

```bash
openclaw matrix verify status --include-recovery-key --json
```

Inizializza lo stato di cross-signing e verifica:

```bash
openclaw matrix verify bootstrap
```

Supporto multi-account: usa `channels.matrix.accounts` con credenziali per account e `name` facoltativo. Vedi [Riferimento configurazione](/it/gateway/configuration-reference#multi-account-all-channels) per il modello condiviso.

Diagnostica dettagliata del bootstrap:

```bash
openclaw matrix verify bootstrap --verbose
```

Forza un reset completo dell'identità di cross-signing prima del bootstrap:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

Verifica questo dispositivo con una recovery key:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

Dettagli dettagliati della verifica del dispositivo:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

Controlla lo stato di salute del backup delle chiavi stanza:

```bash
openclaw matrix verify backup status
```

Diagnostica dettagliata dello stato di salute del backup:

```bash
openclaw matrix verify backup status --verbose
```

Ripristina le chiavi stanza dal backup sul server:

```bash
openclaw matrix verify backup restore
```

Diagnostica dettagliata del ripristino:

```bash
openclaw matrix verify backup restore --verbose
```

Elimina il backup corrente sul server e crea una nuova baseline di backup. Se la
chiave di backup memorizzata non può essere caricata in modo pulito, questo reset può anche ricreare lo storage segreto così
i futuri avvii a freddo potranno caricare la nuova chiave di backup:

```bash
openclaw matrix verify backup reset --yes
```

Tutti i comandi `verify` sono sintetici per impostazione predefinita (incluso il logging interno SDK silenzioso) e mostrano una diagnostica dettagliata solo con `--verbose`.
Usa `--json` per l'output completo leggibile da macchina quando fai scripting.

Nelle configurazioni multi-account, i comandi Matrix CLI usano l'account predefinito implicito di Matrix a meno che tu non passi `--account <id>`.
Se configuri più account con nome, imposta prima `channels.matrix.defaultAccount` oppure quelle operazioni CLI implicite si fermeranno e ti chiederanno di scegliere esplicitamente un account.
Usa `--account` ogni volta che vuoi che le operazioni di verifica o sul dispositivo prendano di mira esplicitamente un account con nome:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Quando la crittografia è disabilitata o non disponibile per un account con nome, gli avvisi Matrix e gli errori di verifica puntano alla chiave di configurazione di quell'account, per esempio `channels.matrix.accounts.assistant.encryption`.

### Cosa significa "verified"

OpenClaw tratta questo dispositivo Matrix come verificato solo quando è verificato dalla tua stessa identità di cross-signing.
In pratica, `openclaw matrix verify status --verbose` espone tre segnali di fiducia:

- `Locally trusted`: questo dispositivo è attendibile solo per il client corrente
- `Cross-signing verified`: l'SDK segnala il dispositivo come verificato tramite cross-signing
- `Signed by owner`: il dispositivo è firmato dalla tua stessa chiave self-signing

`Verified by owner` diventa `yes` solo quando è presente la verifica tramite cross-signing o la firma del proprietario.
La fiducia locale da sola non è sufficiente perché OpenClaw tratti il dispositivo come completamente verificato.

### Cosa fa bootstrap

`openclaw matrix verify bootstrap` è il comando di riparazione e configurazione per gli account Matrix cifrati.
Esegue tutto quanto segue, in questo ordine:

- inizializza lo storage segreto, riutilizzando una recovery key esistente quando possibile
- inizializza il cross-signing e carica le chiavi pubbliche di cross-signing mancanti
- tenta di contrassegnare e firmare tramite cross-signing il dispositivo corrente
- crea un nuovo backup lato server delle chiavi stanza se non ne esiste già uno

Se l'homeserver richiede autenticazione interattiva per caricare le chiavi di cross-signing, OpenClaw tenta prima il caricamento senza autenticazione, poi con `m.login.dummy`, poi con `m.login.password` quando `channels.matrix.password` è configurato.

Usa `--force-reset-cross-signing` solo quando vuoi intenzionalmente scartare l'attuale identità di cross-signing e crearne una nuova.

Se vuoi intenzionalmente scartare l'attuale backup delle chiavi stanza e avviare una nuova
baseline di backup per i messaggi futuri, usa `openclaw matrix verify backup reset --yes`.
Fallo solo se accetti che la vecchia cronologia cifrata irrecuperabile resti
non disponibile e che OpenClaw possa ricreare lo storage segreto se l'attuale segreto
di backup non può essere caricato in sicurezza.

### Nuova baseline di backup

Se vuoi mantenere funzionanti i futuri messaggi cifrati e accetti di perdere la vecchia cronologia irrecuperabile, esegui questi comandi in ordine:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Aggiungi `--account <id>` a ogni comando quando vuoi prendere di mira esplicitamente un account Matrix con nome.

### Comportamento all'avvio

Quando `encryption: true`, Matrix imposta `startupVerification` su `"if-unverified"` per impostazione predefinita.
All'avvio, se questo dispositivo non è ancora verificato, Matrix richiederà l'autoverifica in un altro client Matrix,
salterà le richieste duplicate quando una è già in sospeso e applicherà un cooldown locale prima di riprovare dopo i riavvii.
I tentativi di richiesta falliti vengono ritentati prima, per impostazione predefinita, rispetto alla creazione di richieste riuscite.
Imposta `startupVerification: "off"` per disabilitare le richieste automatiche all'avvio, oppure regola `startupVerificationCooldownHours`
se vuoi una finestra di nuovo tentativo più breve o più lunga.

All'avvio viene anche eseguito automaticamente un passaggio conservativo di bootstrap crittografico.
Quel passaggio prova prima a riutilizzare lo storage segreto e l'identità di cross-signing correnti, ed evita di reimpostare il cross-signing a meno che tu non esegua un flusso esplicito di riparazione bootstrap.

Se all'avvio viene trovato uno stato bootstrap danneggiato e `channels.matrix.password` è configurato, OpenClaw può tentare un percorso di riparazione più rigoroso.
Se il dispositivo corrente è già firmato dal proprietario, OpenClaw conserva quell'identità invece di reimpostarla automaticamente.

Aggiornamento dal precedente plugin Matrix pubblico:

- OpenClaw riutilizza automaticamente lo stesso account Matrix, access token e identità del dispositivo quando possibile.
- Prima che vengano eseguite modifiche di migrazione Matrix effettivamente applicabili, OpenClaw crea o riutilizza uno snapshot di recupero in `~/Backups/openclaw-migrations/`.
- Se usi più account Matrix, imposta `channels.matrix.defaultAccount` prima dell'aggiornamento dal vecchio layout flat-store così OpenClaw saprà quale account deve ricevere quello stato legacy condiviso.
- Se il plugin precedente memorizzava localmente una chiave di decrittazione del backup delle chiavi stanza Matrix, l'avvio o `openclaw doctor --fix` la importeranno automaticamente nel nuovo flusso della recovery key.
- Se l'access token Matrix è cambiato dopo la preparazione della migrazione, l'avvio ora analizza le radici di storage hash token adiacenti alla ricerca di stato legacy di ripristino in sospeso prima di rinunciare al ripristino automatico del backup.
- Se l'access token Matrix cambia in seguito per lo stesso account, homeserver e utente, OpenClaw ora preferisce riutilizzare la radice di storage hash token esistente più completa invece di partire da una directory di stato Matrix vuota.
- Al successivo avvio del gateway, le chiavi stanza sottoposte a backup vengono ripristinate automaticamente nel nuovo crypto store.
- Se il vecchio plugin aveva chiavi stanza solo locali che non erano mai state sottoposte a backup, OpenClaw mostrerà un avviso chiaro. Quelle chiavi non possono essere esportate automaticamente dal precedente rust crypto store, quindi parte della vecchia cronologia cifrata potrebbe restare non disponibile finché non viene recuperata manualmente.
- Vedi [Migrazione Matrix](/it/install/migrating-matrix) per il flusso completo di aggiornamento, i limiti, i comandi di recupero e i messaggi di migrazione più comuni.

Lo stato runtime cifrato è organizzato in radici per account, utente e hash token in
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`.
Quella directory contiene il sync store (`bot-storage.json`), il crypto store (`crypto/`),
il file della recovery key (`recovery-key.json`), lo snapshot IndexedDB (`crypto-idb-snapshot.json`),
i binding dei thread (`thread-bindings.json`) e lo stato della verifica all'avvio (`startup-verification.json`)
quando queste funzionalità sono in uso.
Quando il token cambia ma l'identità dell'account resta la stessa, OpenClaw riutilizza la migliore radice esistente
per quella tupla account/homeserver/utente così stato di sync precedente, stato crypto, binding dei thread
e stato della verifica all'avvio restano visibili.

### Modello del crypto store Node

L'E2EE Matrix in questo plugin usa il percorso Rust crypto ufficiale di `matrix-js-sdk` in Node.
Quel percorso si aspetta una persistenza basata su IndexedDB quando vuoi che lo stato crittografico sopravviva ai riavvii.

Attualmente OpenClaw lo fornisce in Node tramite:

- uso di `fake-indexeddb` come shim API IndexedDB atteso dall'SDK
- ripristino del contenuto IndexedDB del Rust crypto da `crypto-idb-snapshot.json` prima di `initRustCrypto`
- persistenza del contenuto IndexedDB aggiornato di nuovo in `crypto-idb-snapshot.json` dopo l'inizializzazione e durante il runtime
- serializzazione di ripristino e persistenza dello snapshot rispetto a `crypto-idb-snapshot.json` con un lock file consultivo così la persistenza del runtime gateway e la manutenzione CLI non entrino in competizione sullo stesso file snapshot

Si tratta di infrastruttura di compatibilità/storage, non di un'implementazione crittografica personalizzata.
Il file snapshot è stato runtime sensibile ed è memorizzato con permessi file restrittivi.
Nel modello di sicurezza di OpenClaw, l'host del gateway e la directory di stato locale di OpenClaw sono già all'interno del confine di fiducia dell'operatore, quindi questo è principalmente un aspetto di durabilità operativa piuttosto che un distinto confine di fiducia remoto.

Miglioramento pianificato:

- aggiungere il supporto SecretRef per il materiale di chiavi Matrix persistenti così recovery key e relativi segreti di cifratura dello store possano provenire dai provider di segreti OpenClaw invece che solo da file locali

## Gestione del profilo

Aggiorna l'autoprofilo Matrix per l'account selezionato con:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Aggiungi `--account <id>` quando vuoi prendere di mira esplicitamente un account Matrix con nome.

Matrix accetta direttamente URL avatar `mxc://`. Quando passi un URL avatar `http://` o `https://`, OpenClaw lo carica prima su Matrix e memorizza l'URL `mxc://` risolto in `channels.matrix.avatarUrl` (o nell'override dell'account selezionato).

## Avvisi automatici di verifica

Matrix ora pubblica avvisi sul ciclo di vita della verifica direttamente nella stanza DM di verifica rigorosa come messaggi `m.notice`.
Questo include:

- avvisi di richiesta di verifica
- avvisi di verifica pronta (con istruzioni esplicite "Verifica tramite emoji")
- avvisi di avvio e completamento della verifica
- dettagli SAS (emoji e decimali) quando disponibili

Le richieste di verifica in arrivo da un altro client Matrix vengono tracciate e auto-accettate da OpenClaw.
Per i flussi di autoverifica, OpenClaw avvia automaticamente anche il flusso SAS quando la verifica tramite emoji diventa disponibile e conferma il proprio lato.
Per le richieste di verifica da un altro utente/dispositivo Matrix, OpenClaw auto-accetta la richiesta e poi attende che il flusso SAS proceda normalmente.
Devi comunque confrontare le emoji o il SAS decimale nel tuo client Matrix e confermare lì "Corrispondono" per completare la verifica.

OpenClaw non auto-accetta ciecamente flussi duplicati avviati da sé. All'avvio salta la creazione di una nuova richiesta quando una richiesta di autoverifica è già in sospeso.

Gli avvisi di protocollo/sistema di verifica non vengono inoltrati alla pipeline chat dell'agent, quindi non producono `NO_REPLY`.

### Igiene dei dispositivi

I vecchi dispositivi Matrix gestiti da OpenClaw possono accumularsi nell'account e rendere più difficile interpretare la fiducia nelle stanze cifrate.
Elencali con:

```bash
openclaw matrix devices list
```

Rimuovi i dispositivi OpenClaw obsoleti con:

```bash
openclaw matrix devices prune-stale
```

### Riparazione Direct Room

Se lo stato dei messaggi diretti va fuori sincronia, OpenClaw può ritrovarsi con mapping `m.direct` obsoleti che puntano a vecchie stanze singole invece che al DM attivo. Ispeziona il mapping corrente per un peer con:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Riparalo con:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

La riparazione mantiene la logica specifica di Matrix all'interno del plugin:

- preferisce un DM 1:1 rigoroso già mappato in `m.direct`
- altrimenti usa come fallback qualunque DM 1:1 rigoroso attualmente unito con quell'utente
- se non esiste un DM sano, crea una nuova stanza diretta e riscrive `m.direct` per farla puntare lì

Il flusso di riparazione non elimina automaticamente le vecchie stanze. Seleziona solo il DM sano e aggiorna il mapping così i nuovi invii Matrix, gli avvisi di verifica e altri flussi di messaggi diretti prendano di nuovo di mira la stanza corretta.

## Thread

Matrix supporta thread Matrix nativi sia per le risposte automatiche sia per gli invii tramite message-tool.

- `dm.sessionScope: "per-user"` (predefinito) mantiene l'instradamento dei DM Matrix con ambito mittente, così più stanze DM possono condividere una sessione quando vengono risolte verso lo stesso peer.
- `dm.sessionScope: "per-room"` isola ogni stanza DM Matrix nella propria chiave di sessione pur continuando a usare i normali controlli di autenticazione e allowlist dei DM.
- I binding espliciti delle conversazioni Matrix hanno comunque la precedenza su `dm.sessionScope`, quindi le stanze e i thread associati mantengono la sessione di destinazione scelta.
- `threadReplies: "off"` mantiene le risposte al livello superiore e conserva i messaggi in ingresso con thread sulla sessione padre.
- `threadReplies: "inbound"` risponde dentro un thread solo quando il messaggio in ingresso era già in quel thread.
- `threadReplies: "always"` mantiene le risposte della stanza in un thread radicato nel messaggio che ha attivato il trigger e instrada quella conversazione tramite la sessione con ambito thread corrispondente dal primo messaggio che ha attivato il trigger.
- `dm.threadReplies` sovrascrive l'impostazione di livello superiore solo per i DM. Per esempio, puoi mantenere isolati i thread delle stanze lasciando piatti i DM.
- I messaggi in ingresso con thread includono il messaggio radice del thread come contesto aggiuntivo per l'agent.
- Gli invii tramite message-tool ora ereditano automaticamente il thread Matrix corrente quando la destinazione è la stessa stanza, o lo stesso target utente DM, a meno che non venga fornito un `threadId` esplicito.
- Il riutilizzo della stessa sessione sul target utente DM si attiva solo quando i metadati della sessione corrente dimostrano lo stesso peer DM sullo stesso account Matrix; altrimenti OpenClaw torna al normale instradamento con ambito utente.
- Quando OpenClaw vede una stanza DM Matrix entrare in conflitto con un'altra stanza DM sulla stessa sessione DM Matrix condivisa, pubblica in quella stanza un `m.notice` una sola volta con la via di fuga `/focus` quando i binding dei thread sono abilitati e con l'indicazione `dm.sessionScope`.
- I binding di thread a runtime sono supportati per Matrix. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` e `/acp spawn` con binding thread ora funzionano in stanze e DM Matrix.
- `/focus` in una stanza/DM Matrix di livello superiore crea un nuovo thread Matrix e lo associa alla sessione di destinazione quando `threadBindings.spawnSubagentSessions=true`.
- Eseguire `/focus` o `/acp spawn --thread here` all'interno di un thread Matrix esistente associa invece quel thread corrente.

## Binding di conversazione ACP

Le stanze, i DM e i thread Matrix esistenti possono essere trasformati in workspace ACP durevoli senza cambiare la superficie di chat.

Flusso rapido per l'operatore:

- Esegui `/acp spawn codex --bind here` all'interno del DM, della stanza o del thread esistente Matrix che vuoi continuare a usare.
- In un DM o una stanza Matrix di livello superiore, il DM/la stanza corrente resta la superficie di chat e i messaggi futuri vengono instradati alla sessione ACP generata.
- All'interno di un thread Matrix esistente, `--bind here` associa quel thread corrente sul posto.
- `/new` e `/reset` reimpostano sul posto la stessa sessione ACP associata.
- `/acp close` chiude la sessione ACP e rimuove il binding.

Note:

- `--bind here` non crea un thread Matrix figlio.
- `threadBindings.spawnAcpSessions` è richiesto solo per `/acp spawn --thread auto|here`, dove OpenClaw deve creare o associare un thread Matrix figlio.

### Configurazione Thread Binding

Matrix eredita i valori predefiniti globali da `session.threadBindings` e supporta anche override per canale:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

I flag di generazione con thread associato di Matrix sono facoltativi:

- Imposta `threadBindings.spawnSubagentSessions: true` per consentire a `/focus` di livello superiore di creare e associare nuovi thread Matrix.
- Imposta `threadBindings.spawnAcpSessions: true` per consentire a `/acp spawn --thread auto|here` di associare sessioni ACP a thread Matrix.

## Reazioni

Matrix supporta azioni di reazione in uscita, notifiche di reazione in ingresso e reazioni di ack in ingresso.

- Lo strumento di reazione in uscita è controllato da `channels["matrix"].actions.reactions`.
- `react` aggiunge una reazione a uno specifico evento Matrix.
- `reactions` elenca il riepilogo corrente delle reazioni per uno specifico evento Matrix.
- `emoji=""` rimuove le reazioni dell'account bot su quell'evento.
- `remove: true` rimuove solo la reazione dell'emoji specificata dall'account bot.

L'ambito delle reazioni di ack viene risolto in questo ordine:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- fallback all'emoji dell'identità agent

L'ambito delle reazioni di ack viene risolto in questo ordine:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

La modalità di notifica delle reazioni viene risolta in questo ordine:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- predefinito: `own`

Comportamento attuale:

- `reactionNotifications: "own"` inoltra gli eventi `m.reaction` aggiunti quando prendono di mira messaggi Matrix scritti dal bot.
- `reactionNotifications: "off"` disabilita gli eventi di sistema delle reazioni.
- Le rimozioni delle reazioni non vengono ancora sintetizzate in eventi di sistema perché Matrix le espone come redazioni, non come rimozioni `m.reaction` autonome.

## Contesto della cronologia

- `channels.matrix.historyLimit` controlla quanti messaggi recenti della stanza vengono inclusi come `InboundHistory` quando un messaggio di stanza Matrix attiva l'agent.
- Usa come fallback `messages.groupChat.historyLimit`. Se entrambi non sono impostati, il valore effettivo predefinito è `0`, quindi i messaggi di stanza con gating tramite menzione non vengono bufferizzati. Imposta `0` per disabilitare.
- La cronologia delle stanze Matrix riguarda solo la stanza. I DM continuano a usare la normale cronologia di sessione.
- La cronologia delle stanze Matrix è solo pending: OpenClaw mette in buffer i messaggi della stanza che non hanno ancora attivato una risposta, poi cattura uno snapshot di quella finestra quando arriva una menzione o un altro trigger.
- Il messaggio trigger corrente non è incluso in `InboundHistory`; resta nel corpo principale in ingresso per quel turno.
- I nuovi tentativi dello stesso evento Matrix riutilizzano lo snapshot originale della cronologia invece di spostarsi in avanti verso messaggi della stanza più recenti.

## Visibilità del contesto

Matrix supporta il controllo condiviso `contextVisibility` per il contesto supplementare della stanza come testo di risposta recuperato, radici dei thread e cronologia pending.

- `contextVisibility: "all"` è il valore predefinito. Il contesto supplementare viene mantenuto così come ricevuto.
- `contextVisibility: "allowlist"` filtra il contesto supplementare ai mittenti consentiti dai controlli attivi di allowlist stanza/utente.
- `contextVisibility: "allowlist_quote"` si comporta come `allowlist`, ma mantiene comunque una citazione esplicita.

Questa impostazione influisce sulla visibilità del contesto supplementare, non sul fatto che il messaggio in ingresso stesso possa attivare una risposta.
L'autorizzazione al trigger continua a dipendere da `groupPolicy`, `groups`, `groupAllowFrom` e dalle impostazioni della policy DM.

## Esempio di policy DM e stanza

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

Vedi [Groups](/it/channels/groups) per il comportamento di gating tramite menzione e allowlist.

Esempio di pairing per i DM Matrix:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Se un utente Matrix non approvato continua a scriverti prima dell'approvazione, OpenClaw riutilizza lo stesso codice di pairing in sospeso e può inviare di nuovo una risposta di promemoria dopo un breve cooldown invece di generarne uno nuovo.

Vedi [Pairing](/it/channels/pairing) per il flusso condiviso di pairing DM e il layout dello storage.

## Approvazioni exec

Matrix può agire come client di approvazione nativo per un account Matrix. I normali
controlli di instradamento DM/canale restano sotto la configurazione delle approvazioni exec:

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (facoltativo; usa come fallback `channels.matrix.dm.allowFrom`)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, predefinito: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Gli approvatori devono essere ID utente Matrix come `@owner:example.org`. Matrix abilita automaticamente le approvazioni native quando `enabled` non è impostato oppure è `"auto"` e può essere risolto almeno un approvatore. Le approvazioni exec usano prima `execApprovals.approvers` e possono usare come fallback `channels.matrix.dm.allowFrom`. Le approvazioni plugin autorizzano tramite `channels.matrix.dm.allowFrom`. Imposta `enabled: false` per disabilitare esplicitamente Matrix come client di approvazione nativo. In caso contrario, le richieste di approvazione usano come fallback altre route di approvazione configurate o la policy di fallback delle approvazioni.

L'instradamento nativo Matrix ora supporta entrambi i tipi di approvazione:

- `channels.matrix.execApprovals.*` controlla la modalità di fanout DM/canale nativa per i prompt di approvazione Matrix.
- Le approvazioni exec usano l'insieme di approvatori exec da `execApprovals.approvers` oppure `channels.matrix.dm.allowFrom`.
- Le approvazioni plugin usano la allowlist DM Matrix da `channels.matrix.dm.allowFrom`.
- Le scorciatoie tramite reazione Matrix e gli aggiornamenti dei messaggi si applicano sia alle approvazioni exec sia a quelle plugin.

Regole di consegna:

- `target: "dm"` invia i prompt di approvazione ai DM degli approvatori
- `target: "channel"` rimanda il prompt alla stanza o al DM Matrix di origine
- `target: "both"` invia ai DM degli approvatori e alla stanza o al DM Matrix di origine

I prompt di approvazione Matrix inizializzano scorciatoie di reazione sul messaggio di approvazione principale:

- `✅` = consenti una volta
- `❌` = nega
- `♾️` = consenti sempre quando quella decisione è permessa dalla policy exec effettiva

Gli approvatori possono reagire a quel messaggio o usare i comandi slash di fallback: `/approve <id> allow-once`, `/approve <id> allow-always` oppure `/approve <id> deny`.

Solo gli approvatori risolti possono approvare o negare. Per le approvazioni exec, la consegna sul canale include il testo del comando, quindi abilita `channel` o `both` solo in stanze fidate.

I prompt di approvazione Matrix riutilizzano il planner di approvazione condiviso del core. La superficie nativa specifica di Matrix gestisce instradamento stanza/DM, reazioni e comportamento di invio/aggiornamento/eliminazione dei messaggi sia per le approvazioni exec sia per quelle plugin.

Override per account:

- `channels.matrix.accounts.<account>.execApprovals`

Documentazione correlata: [Approvazioni exec](/it/tools/exec-approvals)

## Esempio multi-account

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

I valori di livello superiore `channels.matrix` fungono da predefiniti per gli account con nome a meno che un account non li sovrascriva.
Puoi assegnare una voce stanza ereditata a un solo account Matrix con `groups.<room>.account` (o il legacy `rooms.<room>.account`).
Le voci senza `account` restano condivise tra tutti gli account Matrix, e le voci con `account: "default"` continuano a funzionare quando l'account predefinito è configurato direttamente nel livello superiore `channels.matrix.*`.
I predefiniti di autenticazione condivisi parziali non creano da soli un account predefinito implicito separato. OpenClaw sintetizza l'account di livello superiore `default` solo quando quel predefinito ha autenticazione aggiornata (`homeserver` più `accessToken`, oppure `homeserver` più `userId` e `password`); gli account con nome possono comunque restare rilevabili da `homeserver` più `userId` quando le credenziali in cache soddisfano l'autenticazione in seguito.
Se Matrix ha già esattamente un account con nome, oppure `defaultAccount` punta a una chiave account con nome esistente, la promozione di riparazione/setup da account singolo a multi-account preserva quell'account invece di creare una nuova voce `accounts.default`. Solo le chiavi di autenticazione/bootstrap Matrix vengono spostate in quell'account promosso; le chiavi condivise di policy di consegna restano al livello superiore.
Imposta `defaultAccount` quando vuoi che OpenClaw preferisca un account Matrix con nome per instradamento implicito, probing e operazioni CLI.
Se configuri più account con nome, imposta `defaultAccount` o passa `--account <id>` per i comandi CLI che si basano sulla selezione implicita dell'account.
Passa `--account <id>` a `openclaw matrix verify ...` e `openclaw matrix devices ...` quando vuoi sovrascrivere quella selezione implicita per un comando.

## Homeserver privati/LAN

Per impostazione predefinita, OpenClaw blocca gli homeserver Matrix privati/interni per la protezione SSRF a meno che tu non
faccia esplicitamente opt-in per account.

Se il tuo homeserver gira su localhost, un IP LAN/Tailscale o un hostname interno, abilita
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

Esempio di configurazione CLI:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

Questo opt-in consente solo destinazioni private/interne fidate. Homeserver pubblici in chiaro come
`http://matrix.example.org:8008` restano bloccati. Preferisci `https://` quando possibile.

## Instradamento del traffico Matrix tramite proxy

Se la tua distribuzione Matrix richiede un proxy HTTP(S) in uscita esplicito, imposta `channels.matrix.proxy`:

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
OpenClaw usa la stessa impostazione proxy per il traffico Matrix a runtime e per i probe di stato dell'account.

## Risoluzione della destinazione

Matrix accetta questi formati di destinazione ovunque OpenClaw ti chieda una stanza o un utente:

- Utenti: `@user:server`, `user:@user:server`, oppure `matrix:user:@user:server`
- Stanze: `!room:server`, `room:!room:server`, oppure `matrix:room:!room:server`
- Alias: `#alias:server`, `channel:#alias:server`, oppure `matrix:channel:#alias:server`

La ricerca live nella directory usa l'account Matrix autenticato:

- Le ricerche utente interrogano la directory utenti Matrix su quell'homeserver.
- Le ricerche stanza accettano direttamente ID stanza espliciti e alias, poi usano come fallback la ricerca dei nomi delle stanze unite per quell'account.
- La ricerca per nome della stanza unita è best-effort. Se un nome stanza non può essere risolto in un ID o alias, viene ignorato dalla risoluzione della allowlist a runtime.

## Riferimento configurazione

- `enabled`: abilita o disabilita il canale.
- `name`: etichetta facoltativa per l'account.
- `defaultAccount`: ID account preferito quando sono configurati più account Matrix.
- `homeserver`: URL dell'homeserver, per esempio `https://matrix.example.org`.
- `network.dangerouslyAllowPrivateNetwork`: consente a questo account Matrix di connettersi a homeserver privati/interni. Abilitalo quando l'homeserver si risolve in `localhost`, un IP LAN/Tailscale o un host interno come `matrix-synapse`.
- `proxy`: URL facoltativo di proxy HTTP(S) per il traffico Matrix. Gli account con nome possono sovrascrivere il valore predefinito di livello superiore con il proprio `proxy`.
- `userId`: ID utente Matrix completo, per esempio `@bot:example.org`.
- `accessToken`: access token per l'autenticazione basata su token. Sono supportati valori in chiaro e valori SecretRef per `channels.matrix.accessToken` e `channels.matrix.accounts.<id>.accessToken` tramite provider env/file/exec. Vedi [Gestione dei segreti](/it/gateway/secrets).
- `password`: password per il login basato su password. Sono supportati valori in chiaro e valori SecretRef.
- `deviceId`: ID dispositivo Matrix esplicito.
- `deviceName`: nome visualizzato del dispositivo per il login con password.
- `avatarUrl`: URL dell'avatar personale memorizzato per la sincronizzazione del profilo e gli aggiornamenti `set-profile`.
- `initialSyncLimit`: limite di eventi della sincronizzazione all'avvio.
- `encryption`: abilita E2EE.
- `allowlistOnly`: forza un comportamento solo allowlist per DM e stanze.
- `allowBots`: consente messaggi da altri account Matrix OpenClaw configurati (`true` oppure `"mentions"`).
- `groupPolicy`: `open`, `allowlist` oppure `disabled`.
- `contextVisibility`: modalità di visibilità del contesto supplementare della stanza (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: allowlist di ID utente per il traffico nelle stanze.
- Le voci di `groupAllowFrom` dovrebbero essere ID utente Matrix completi. I nomi non risolti vengono ignorati a runtime.
- `historyLimit`: numero massimo di messaggi della stanza da includere come contesto della cronologia del gruppo. Usa come fallback `messages.groupChat.historyLimit`; se entrambi non sono impostati, il valore effettivo predefinito è `0`. Imposta `0` per disabilitare.
- `replyToMode`: `off`, `first`, `all` oppure `batched`.
- `markdown`: configurazione facoltativa del rendering Markdown per il testo Matrix in uscita.
- `streaming`: `off` (predefinito), `partial`, `quiet`, `true` oppure `false`. `partial` e `true` abilitano aggiornamenti della bozza con anteprima iniziale tramite normali messaggi di testo Matrix. `quiet` usa avvisi di anteprima senza notifica per configurazioni self-hosted con regole push.
- `blockStreaming`: `true` abilita messaggi di avanzamento separati per i blocchi dell'assistente completati mentre è attivo lo streaming delle bozze di anteprima.
- `threadReplies`: `off`, `inbound` oppure `always`.
- `threadBindings`: override per canale per instradamento e ciclo di vita delle sessioni associate a thread.
- `startupVerification`: modalità automatica di richiesta di autoverifica all'avvio (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: cooldown prima di ritentare le richieste automatiche di verifica all'avvio.
- `textChunkLimit`: dimensione dei chunk dei messaggi in uscita.
- `chunkMode`: `length` oppure `newline`.
- `responsePrefix`: prefisso facoltativo del messaggio per le risposte in uscita.
- `ackReaction`: override facoltativo della reazione di ack per questo canale/account.
- `ackReactionScope`: override facoltativo dell'ambito della reazione di ack (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: modalità di notifica delle reazioni in ingresso (`own`, `off`).
- `mediaMaxMb`: limite dimensionale dei contenuti multimediali in MB per la gestione dei media Matrix. Si applica agli invii in uscita e all'elaborazione dei media in ingresso.
- `autoJoin`: policy di accesso automatico agli inviti (`always`, `allowlist`, `off`). Predefinito: `off`. Si applica agli inviti Matrix in generale, inclusi gli inviti in stile DM, non solo agli inviti di stanze/gruppi. OpenClaw prende questa decisione al momento dell'invito, prima di poter classificare in modo affidabile la stanza unita come DM o gruppo.
- `autoJoinAllowlist`: stanze/alias consentiti quando `autoJoin` è `allowlist`. Le voci alias vengono risolte in ID stanza durante la gestione dell'invito; OpenClaw non si fida dello stato alias dichiarato dalla stanza invitata.
- `dm`: blocco di policy DM (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.policy`: controlla l'accesso DM dopo che OpenClaw si è unito alla stanza e l'ha classificata come DM. Non modifica se un invito viene accettato automaticamente.
- Le voci di `dm.allowFrom` dovrebbero essere ID utente Matrix completi, a meno che tu non le abbia già risolte tramite ricerca live nella directory.
- `dm.sessionScope`: `per-user` (predefinito) oppure `per-room`. Usa `per-room` quando vuoi che ogni stanza DM Matrix mantenga un contesto separato anche se il peer è lo stesso.
- `dm.threadReplies`: override della policy dei thread solo per DM (`off`, `inbound`, `always`). Sovrascrive l'impostazione `threadReplies` di livello superiore sia per il posizionamento delle risposte sia per l'isolamento della sessione nei DM.
- `execApprovals`: consegna nativa Matrix delle approvazioni exec (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: ID utente Matrix autorizzati ad approvare richieste exec. Facoltativo quando `dm.allowFrom` identifica già gli approvatori.
- `execApprovals.target`: `dm | channel | both` (predefinito: `dm`).
- `accounts`: override nominati per account. I valori di livello superiore `channels.matrix` fungono da predefiniti per queste voci.
- `groups`: mappa delle policy per stanza. Preferisci ID stanza o alias; i nomi stanza non risolti vengono ignorati a runtime. L'identità di sessione/gruppo usa l'ID stanza stabile dopo la risoluzione, mentre le etichette leggibili continuano a provenire dai nomi delle stanze.
- `groups.<room>.account`: limita una voce stanza ereditata a uno specifico account Matrix in configurazioni multi-account.
- `groups.<room>.allowBots`: override a livello stanza per mittenti bot configurati (`true` oppure `"mentions"`).
- `groups.<room>.users`: allowlist dei mittenti per stanza.
- `groups.<room>.tools`: override per stanza di autorizzazione/negazione degli strumenti.
- `groups.<room>.autoReply`: override a livello stanza del gating tramite menzione. `true` disabilita i requisiti di menzione per quella stanza; `false` li forza di nuovo.
- `groups.<room>.skills`: filtro facoltativo delle Skills a livello stanza.
- `groups.<room>.systemPrompt`: snippet facoltativo di system prompt a livello stanza.
- `rooms`: alias legacy di `groups`.
- `actions`: controllo per azione degli strumenti (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## Correlati

- [Panoramica dei canali](/it/channels) — tutti i canali supportati
- [Pairing](/it/channels/pairing) — autenticazione DM e flusso di pairing
- [Groups](/it/channels/groups) — comportamento della chat di gruppo e gating tramite menzione
- [Instradamento dei canali](/it/channels/channel-routing) — instradamento di sessione per i messaggi
- [Sicurezza](/it/gateway/security) — modello di accesso e hardening
