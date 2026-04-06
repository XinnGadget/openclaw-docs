---
read_when:
    - Configurare Matrix in OpenClaw
    - Configurare Matrix E2EE e la verifica
summary: Stato del supporto Matrix, configurazione ed esempi di configurazione
title: Matrix
x-i18n:
    generated_at: "2026-04-06T08:17:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06f833bf0ede81bad69f140994c32e8cc5d1635764f95fc5db4fc5dc25f2b85e
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix è il plugin di canale Matrix incluso con OpenClaw.
Usa il pacchetto ufficiale `matrix-js-sdk` e supporta DM, stanze, thread, contenuti multimediali, reazioni, sondaggi, posizione ed E2EE.

## Plugin incluso

Matrix viene distribuito come plugin incluso nelle versioni attuali di OpenClaw, quindi le
build pacchettizzate normali non richiedono un'installazione separata.

Se usi una build meno recente o un'installazione personalizzata che esclude Matrix, installalo
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

## Configurazione

1. Assicurati che il plugin Matrix sia disponibile.
   - Le versioni pacchettizzate correnti di OpenClaw lo includono già.
   - Le installazioni meno recenti/personalizzate possono aggiungerlo manualmente con i comandi sopra.
2. Crea un account Matrix sul tuo homeserver.
3. Configura `channels.matrix` con una delle seguenti opzioni:
   - `homeserver` + `accessToken`, oppure
   - `homeserver` + `userId` + `password`.
4. Riavvia il gateway.
5. Avvia un DM con il bot oppure invitalo in una stanza.

Percorsi di configurazione interattiva:

```bash
openclaw channels add
openclaw configure --section channels
```

Cosa chiede effettivamente la procedura guidata di Matrix:

- URL dell'homeserver
- metodo di autenticazione: token di accesso o password
- ID utente solo se scegli l'autenticazione con password
- nome dispositivo facoltativo
- se abilitare E2EE
- se configurare ora l'accesso alle stanze Matrix

Comportamento della procedura guidata da tenere presente:

- Se le variabili d'ambiente di autenticazione Matrix esistono già per l'account selezionato e per quell'account l'autenticazione non è già salvata nella configurazione, la procedura guidata offre una scorciatoia tramite env e scrive solo `enabled: true` per quell'account.
- Quando aggiungi in modo interattivo un altro account Matrix, il nome account inserito viene normalizzato nell'ID account usato nella configurazione e nelle variabili d'ambiente. Ad esempio, `Ops Bot` diventa `ops-bot`.
- I prompt della allowlist DM accettano subito valori completi `@user:server`. I nomi visualizzati funzionano solo quando la ricerca live nella directory trova una sola corrispondenza esatta; altrimenti la procedura guidata ti chiede di riprovare con un ID Matrix completo.
- I prompt della allowlist delle stanze accettano direttamente ID stanza e alias. Possono anche risolvere in tempo reale i nomi delle stanze già unite, ma i nomi non risolti vengono mantenuti solo come digitati durante la configurazione e vengono ignorati più tardi dalla risoluzione runtime della allowlist. Preferisci `!room:server` o `#alias:server`.
- L'identità runtime di stanza/sessione usa l'ID stanza Matrix stabile. Gli alias dichiarati nella stanza vengono usati solo come input di ricerca, non come chiave di sessione a lungo termine o identità stabile del gruppo.
- Per risolvere i nomi delle stanze prima di salvarli, usa `openclaw channels resolve --channel matrix "Project Room"`.

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
Quando lì esistono credenziali in cache, OpenClaw considera Matrix configurato per setup, doctor e individuazione dello stato del canale anche se l'autenticazione corrente non è impostata direttamente nella configurazione.

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

Matrix esegue l'escape della punteggiatura negli ID account per evitare collisioni nelle variabili d'ambiente con ambito.
Ad esempio, `-` diventa `_X2D_`, quindi `ops-prod` corrisponde a `MATRIX_OPS_X2D_PROD_*`.

La procedura guidata interattiva offre la scorciatoia con variabili d'ambiente solo quando quelle variabili env di autenticazione sono già presenti e l'account selezionato non ha già l'autenticazione Matrix salvata nella configurazione.

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
Ciò include i nuovi inviti in stile DM. Al momento dell'invito, OpenClaw non sa in modo affidabile se la
stanza invitata verrà trattata come DM o come gruppo, quindi tutti gli inviti passano prima attraverso la stessa
decisione di `autoJoin`. `dm.policy` continua ad applicarsi dopo che il bot è entrato e la stanza è
classificata come DM, quindi `autoJoin` controlla il comportamento di ingresso mentre `dm.policy` controlla
il comportamento di risposta/accesso.

## Anteprime in streaming

Lo streaming delle risposte Matrix è opt-in.

Imposta `channels.matrix.streaming` su `"partial"` quando vuoi che OpenClaw invii una singola anteprima live
di risposta, modifichi quell'anteprima sul posto mentre il modello genera testo, e poi la finalizzi quando la
risposta è terminata:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` è il valore predefinito. OpenClaw aspetta la risposta finale e la invia una sola volta.
- `streaming: "partial"` crea un singolo messaggio di anteprima modificabile per il blocco corrente dell'assistente usando normali messaggi di testo Matrix. Questo preserva il comportamento legacy di Matrix con notifica sulla prima anteprima, quindi i client standard possono notificare sul primo testo dell'anteprima in streaming invece che sul blocco completato.
- `streaming: "quiet"` crea un singolo avviso di anteprima silenzioso e modificabile per il blocco corrente dell'assistente. Usalo solo quando configuri anche regole push per i destinatari sulle modifiche finalizzate dell'anteprima.
- `blockStreaming: true` abilita messaggi di avanzamento Matrix separati. Con l'anteprima in streaming abilitata, Matrix mantiene la bozza live per il blocco corrente e conserva i blocchi completati come messaggi separati.
- Quando l'anteprima in streaming è attiva e `blockStreaming` è disattivato, Matrix modifica la bozza live sul posto e finalizza quello stesso evento quando il blocco o il turno termina.
- Se l'anteprima non entra più in un singolo evento Matrix, OpenClaw interrompe lo streaming dell'anteprima e torna alla normale consegna finale.
- Le risposte multimediali continuano a inviare normalmente gli allegati. Se un'anteprima obsoleta non può più essere riutilizzata in sicurezza, OpenClaw la redige prima di inviare la risposta multimediale finale.
- Le modifiche all'anteprima comportano chiamate API Matrix aggiuntive. Lascia lo streaming disattivato se vuoi il comportamento più conservativo possibile rispetto ai limiti di velocità.

`blockStreaming` da solo non abilita le anteprime in bozza.
Usa `streaming: "partial"` o `streaming: "quiet"` per le modifiche di anteprima; poi aggiungi `blockStreaming: true` solo se vuoi anche che i blocchi dell'assistente completati restino visibili come messaggi di avanzamento separati.

Se ti servono notifiche Matrix standard senza regole push personalizzate, usa `streaming: "partial"` per il comportamento con anteprima iniziale oppure lascia `streaming` disattivato per la consegna solo finale. Con `streaming: "off"`:

- `blockStreaming: true` invia ogni blocco completato come normale messaggio Matrix con notifica.
- `blockStreaming: false` invia solo la risposta finale completata come normale messaggio Matrix con notifica.

### Regole push self-hosted per anteprime silenziose finalizzate

Se gestisci la tua infrastruttura Matrix e vuoi che le anteprime silenziose notifichino solo quando un blocco o la
risposta finale è pronta, imposta `streaming: "quiet"` e aggiungi una regola push per utente per le modifiche finalizzate dell'anteprima.

Di solito questa è una configurazione dell'utente destinatario, non una modifica di configurazione globale dell'homeserver:

Mappa rapida prima di iniziare:

- utente destinatario = la persona che deve ricevere la notifica
- utente bot = l'account Matrix OpenClaw che invia la risposta
- usa il token di accesso dell'utente destinatario per le chiamate API qui sotto
- fai corrispondere `sender` nella regola push al MXID completo dell'utente bot

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

2. Assicurati che l'account destinatario riceva già le normali notifiche push Matrix. Le regole per
   le anteprime silenziose funzionano solo se quell'utente ha già pusher/dispositivi funzionanti.

3. Ottieni il token di accesso dell'utente destinatario.
   - Usa il token dell'utente che riceve, non quello del bot.
   - Riutilizzare un token di sessione client esistente di solito è la soluzione più semplice.
   - Se devi generare un nuovo token, puoi accedere tramite la normale API Client-Server Matrix:

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

Se questo comando non restituisce pusher/dispositivi attivi, correggi prima le normali notifiche Matrix prima di aggiungere
la regola OpenClaw qui sotto.

OpenClaw contrassegna le modifiche finalizzate dell'anteprima solo testuale con:

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
- `$USER_ACCESS_TOKEN`: token di accesso dell'utente destinatario
- `openclaw-finalized-preview-botname`: un ID regola univoco per questo bot per questo utente destinatario
- `@bot:example.org`: il MXID del tuo bot Matrix OpenClaw, non il MXID dell'utente destinatario

Importante per configurazioni multi-bot:

- Le regole push sono indicizzate da `ruleId`. Rieseguire `PUT` sullo stesso ID regola aggiorna quella singola regola.
- Se un utente destinatario deve ricevere notifiche per più account bot Matrix OpenClaw, crea una regola per bot con un ID regola univoco per ogni corrispondenza del sender.
- Un modello semplice è `openclaw-finalized-preview-<botname>`, ad esempio `openclaw-finalized-preview-ops` o `openclaw-finalized-preview-support`.

La regola viene valutata rispetto al mittente dell'evento:

- autenticati con il token dell'utente destinatario
- fai corrispondere `sender` al MXID del bot OpenClaw

6. Verifica che la regola esista:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Prova una risposta in streaming. In modalità silenziosa, la stanza dovrebbe mostrare una bozza di anteprima silenziosa e la modifica finale
   sul posto dovrebbe inviare una notifica quando il blocco o il turno termina.

Se in seguito devi rimuovere la regola, elimina quello stesso ID regola con il token dell'utente destinatario:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Note:

- Crea la regola con il token di accesso dell'utente destinatario, non con quello del bot.
- Le nuove regole `override` definite dall'utente vengono inserite prima delle regole di soppressione predefinite, quindi non è necessario alcun parametro di ordinamento aggiuntivo.
- Questo influisce solo sulle modifiche di anteprima solo testuali che OpenClaw può finalizzare in sicurezza sul posto. I fallback per contenuti multimediali e per anteprime obsolete usano ancora la normale consegna Matrix.
- Se `GET /_matrix/client/v3/pushers` non mostra alcun pusher, l'utente non ha ancora una consegna push Matrix funzionante per questo account/dispositivo.

#### Synapse

Per Synapse, la configurazione sopra di solito è già sufficiente da sola:

- Non è richiesta alcuna modifica speciale a `homeserver.yaml` per le notifiche delle anteprime OpenClaw finalizzate.
- Se il tuo deployment Synapse invia già le normali notifiche push Matrix, il token utente + la chiamata `pushrules` sopra sono il passaggio principale della configurazione.
- Se esegui Synapse dietro un reverse proxy o dei worker, assicurati che `/_matrix/client/.../pushrules/` raggiunga correttamente Synapse.
- Se usi i worker Synapse, assicurati che i pusher siano in salute. La consegna push è gestita dal processo principale o da `synapse.app.pusher` / worker pusher configurati.

#### Tuwunel

Per Tuwunel, usa lo stesso flusso di configurazione e la stessa chiamata API `pushrules` mostrata sopra:

- Non è richiesta alcuna configurazione specifica di Tuwunel per il marcatore di anteprima finalizzata in sé.
- Se le normali notifiche Matrix funzionano già per quell'utente, il token utente + la chiamata `pushrules` sopra sono il passaggio principale della configurazione.
- Se le notifiche sembrano scomparire mentre l'utente è attivo su un altro dispositivo, controlla se `suppress_push_when_active` è abilitato. Tuwunel ha aggiunto questa opzione in Tuwunel 1.4.2 il 12 settembre 2025, e può sopprimere intenzionalmente le push verso altri dispositivi mentre un dispositivo è attivo.

## Cifratura e verifica

Nelle stanze cifrate (E2EE), gli eventi immagine in uscita usano `thumbnail_file` così che le anteprime immagine siano cifrate insieme all'allegato completo. Le stanze non cifrate continuano a usare `thumbnail_url` semplice. Non è necessaria alcuna configurazione: il plugin rileva automaticamente lo stato E2EE.

### Stanze bot-to-bot

Per impostazione predefinita, i messaggi Matrix provenienti da altri account Matrix OpenClaw configurati vengono ignorati.

Usa `allowBots` quando vuoi intenzionalmente traffico Matrix tra agenti:

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

- `allowBots: true` accetta messaggi da altri account bot Matrix configurati nelle stanze e nei DM consentiti.
- `allowBots: "mentions"` accetta quei messaggi solo quando menzionano visibilmente questo bot nelle stanze. I DM sono comunque consentiti.
- `groups.<room>.allowBots` sovrascrive l'impostazione a livello account per una singola stanza.
- OpenClaw continua a ignorare i messaggi provenienti dallo stesso ID utente Matrix per evitare cicli di autorisposta.
- Matrix qui non espone un flag bot nativo; OpenClaw considera "scritto da un bot" come "inviato da un altro account Matrix configurato su questo gateway OpenClaw".

Usa allowlist rigorose per le stanze e requisiti di menzione quando abiliti il traffico bot-to-bot in stanze condivise.

Abilita la cifratura:

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

Includi la chiave di ripristino memorizzata nell'output leggibile da macchina:

```bash
openclaw matrix verify status --include-recovery-key --json
```

Inizializza cross-signing e stato di verifica:

```bash
openclaw matrix verify bootstrap
```

Supporto multi-account: usa `channels.matrix.accounts` con credenziali per account e `name` facoltativo. Vedi [Configuration reference](/it/gateway/configuration-reference#multi-account-all-channels) per il modello condiviso.

Diagnostica dettagliata del bootstrap:

```bash
openclaw matrix verify bootstrap --verbose
```

Forza un reset di una nuova identità cross-signing prima del bootstrap:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

Verifica questo dispositivo con una chiave di ripristino:

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

Diagnostica dettagliata dello stato del backup:

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

Elimina il backup corrente sul server e crea una nuova baseline di backup. Se la chiave di
backup memorizzata non può essere caricata correttamente, questo reset può anche ricreare lo storage dei segreti così che
i futuri cold start possano caricare la nuova chiave di backup:

```bash
openclaw matrix verify backup reset --yes
```

Tutti i comandi `verify` sono sintetici per impostazione predefinita (incluso il logging SDK interno silenzioso) e mostrano diagnostica dettagliata solo con `--verbose`.
Usa `--json` per l'output completo leggibile da macchina negli script.

Nelle configurazioni multi-account, i comandi CLI Matrix usano l'account predefinito implicito di Matrix a meno che non passi `--account <id>`.
Se configuri più account con nome, imposta prima `channels.matrix.defaultAccount` altrimenti quelle operazioni CLI implicite si fermeranno e ti chiederanno di scegliere esplicitamente un account.
Usa `--account` ogni volta che vuoi che le operazioni di verifica o sui dispositivi prendano esplicitamente di mira un account con nome:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Quando la cifratura è disabilitata o non disponibile per un account con nome, gli avvisi Matrix e gli errori di verifica puntano alla chiave di configurazione di quell'account, per esempio `channels.matrix.accounts.assistant.encryption`.

### Cosa significa "verified"

OpenClaw considera questo dispositivo Matrix verificato solo quando è verificato dalla tua identità cross-signing.
In pratica, `openclaw matrix verify status --verbose` espone tre segnali di attendibilità:

- `Locally trusted`: questo dispositivo è attendibile solo per il client corrente
- `Cross-signing verified`: l'SDK segnala il dispositivo come verificato tramite cross-signing
- `Signed by owner`: il dispositivo è firmato dalla tua stessa chiave self-signing

`Verified by owner` diventa `yes` solo quando è presente la verifica tramite cross-signing o la firma del proprietario.
La fiducia locale da sola non basta perché OpenClaw tratti il dispositivo come completamente verificato.

### Cosa fa il bootstrap

`openclaw matrix verify bootstrap` è il comando di riparazione e configurazione per gli account Matrix cifrati.
Esegue tutto quanto segue in quest'ordine:

- inizializza lo storage dei segreti, riutilizzando una chiave di ripristino esistente quando possibile
- inizializza il cross-signing e carica le chiavi pubbliche cross-signing mancanti
- prova a contrassegnare e firmare tramite cross-signing il dispositivo corrente
- crea un nuovo backup lato server delle chiavi della stanza se non ne esiste già uno

Se l'homeserver richiede autenticazione interattiva per caricare chiavi cross-signing, OpenClaw prova prima il caricamento senza autenticazione, poi con `m.login.dummy`, poi con `m.login.password` quando `channels.matrix.password` è configurato.

Usa `--force-reset-cross-signing` solo quando vuoi intenzionalmente scartare l'identità cross-signing corrente e crearne una nuova.

Se vuoi intenzionalmente scartare il backup corrente delle chiavi della stanza e avviare una nuova
baseline di backup per i messaggi futuri, usa `openclaw matrix verify backup reset --yes`.
Fallo solo se accetti che la vecchia cronologia cifrata irrecuperabile resti
non disponibile e che OpenClaw possa ricreare lo storage dei segreti se l'attuale
segreto di backup non può essere caricato in sicurezza.

### Nuova baseline di backup

Se vuoi mantenere funzionanti i futuri messaggi cifrati e accetti di perdere la vecchia cronologia irrecuperabile, esegui questi comandi nell'ordine seguente:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Aggiungi `--account <id>` a ogni comando quando vuoi prendere esplicitamente di mira un account Matrix con nome.

### Comportamento all'avvio

Quando `encryption: true`, Matrix imposta `startupVerification` su `"if-unverified"` per impostazione predefinita.
All'avvio, se questo dispositivo non è ancora verificato, Matrix richiederà l'autoverifica in un altro client Matrix,
salterà le richieste duplicate quando una è già in sospeso e applicherà un cooldown locale prima di riprovare dopo i riavvii.
Per impostazione predefinita, i tentativi di richiesta falliti vengono ritentati prima rispetto alla creazione riuscita di una richiesta.
Imposta `startupVerification: "off"` per disabilitare le richieste automatiche all'avvio, oppure regola `startupVerificationCooldownHours`
se vuoi una finestra di ritentativo più breve o più lunga.

All'avvio viene inoltre eseguito automaticamente un passaggio conservativo di bootstrap crittografico.
Quel passaggio prova prima a riutilizzare lo storage dei segreti corrente e l'identità cross-signing corrente, ed evita di reimpostare il cross-signing a meno che tu non esegua un flusso esplicito di riparazione bootstrap.

Se all'avvio viene rilevato uno stato bootstrap danneggiato e `channels.matrix.password` è configurato, OpenClaw può provare un percorso di riparazione più rigoroso.
Se il dispositivo corrente è già firmato dal proprietario, OpenClaw preserva quell'identità invece di reimpostarla automaticamente.

Aggiornamento dal precedente plugin Matrix pubblico:

- OpenClaw riutilizza automaticamente lo stesso account Matrix, token di accesso e identità del dispositivo quando possibile.
- Prima di eseguire modifiche di migrazione Matrix applicabili, OpenClaw crea o riutilizza uno snapshot di recupero in `~/Backups/openclaw-migrations/`.
- Se usi più account Matrix, imposta `channels.matrix.defaultAccount` prima di aggiornare dal vecchio layout flat-store così OpenClaw saprà quale account deve ricevere quello stato legacy condiviso.
- Se il plugin precedente memorizzava localmente una chiave di decrittazione per il backup delle chiavi della stanza Matrix, l'avvio o `openclaw doctor --fix` la importeranno automaticamente nel nuovo flusso della chiave di ripristino.
- Se il token di accesso Matrix è cambiato dopo che la migrazione è stata preparata, l'avvio ora esegue la scansione delle radici di storage sibling hash del token alla ricerca di stato legacy di ripristino in sospeso prima di rinunciare al ripristino automatico del backup.
- Se il token di accesso Matrix cambia in seguito per lo stesso account, homeserver e utente, OpenClaw ora preferisce riutilizzare la radice di storage hash del token esistente più completa invece di partire da una directory di stato Matrix vuota.
- Al successivo avvio del gateway, le chiavi della stanza sottoposte a backup vengono ripristinate automaticamente nel nuovo crypto store.
- Se il vecchio plugin aveva chiavi di stanza solo locali che non erano mai state sottoposte a backup, OpenClaw mostrerà un avviso chiaro. Queste chiavi non possono essere esportate automaticamente dal precedente rust crypto store, quindi parte della vecchia cronologia cifrata potrebbe restare non disponibile finché non viene recuperata manualmente.
- Vedi [Matrix migration](/it/install/migrating-matrix) per il flusso completo di aggiornamento, limiti, comandi di recupero e messaggi di migrazione comuni.

Lo stato runtime cifrato è organizzato in radici per-account, per-utente con hash del token in
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`.
Quella directory contiene il sync store (`bot-storage.json`), il crypto store (`crypto/`),
il file della chiave di ripristino (`recovery-key.json`), lo snapshot IndexedDB (`crypto-idb-snapshot.json`),
i binding dei thread (`thread-bindings.json`) e lo stato della verifica all'avvio (`startup-verification.json`)
quando queste funzionalità sono in uso.
Quando il token cambia ma l'identità dell'account resta la stessa, OpenClaw riutilizza la migliore
radice esistente per quella tupla account/homeserver/utente così che lo stato di sync precedente, lo stato crittografico, i binding dei thread
e lo stato della verifica all'avvio restino visibili.

### Modello crypto store Node

Matrix E2EE in questo plugin usa il percorso Rust crypto ufficiale di `matrix-js-sdk` in Node.
Quel percorso richiede una persistenza basata su IndexedDB quando vuoi che lo stato crittografico sopravviva ai riavvii.

OpenClaw al momento fornisce questa funzionalità in Node in questo modo:

- usa `fake-indexeddb` come shim API IndexedDB atteso dall'SDK
- ripristina il contenuto IndexedDB del Rust crypto da `crypto-idb-snapshot.json` prima di `initRustCrypto`
- salva il contenuto IndexedDB aggiornato di nuovo in `crypto-idb-snapshot.json` dopo l'inizializzazione e durante il runtime
- serializza il ripristino e la persistenza dello snapshot rispetto a `crypto-idb-snapshot.json` con un lock file advisory così che la persistenza runtime del gateway e la manutenzione CLI non vadano in concorrenza sullo stesso file snapshot

Si tratta di infrastruttura di compatibilità/storage, non di un'implementazione crittografica personalizzata.
Il file snapshot è uno stato runtime sensibile ed è memorizzato con permessi file restrittivi.
Nel modello di sicurezza di OpenClaw, l'host del gateway e la directory di stato locale di OpenClaw sono già all'interno del confine dell'operatore fidato, quindi questo è principalmente un problema di durabilità operativa piuttosto che un confine di fiducia remoto separato.

Miglioramento pianificato:

- aggiungere il supporto SecretRef per il materiale chiave Matrix persistente così che le chiavi di ripristino e i relativi segreti di cifratura dello store possano essere ottenuti dai provider di segreti OpenClaw invece che solo da file locali

## Gestione del profilo

Aggiorna il profilo Matrix dell'account selezionato con:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Aggiungi `--account <id>` quando vuoi prendere esplicitamente di mira un account Matrix con nome.

Matrix accetta direttamente URL avatar `mxc://`. Quando passi un URL avatar `http://` o `https://`, OpenClaw lo carica prima su Matrix e memorizza l'URL `mxc://` risolto in `channels.matrix.avatarUrl` (o nella sovrascrittura dell'account selezionato).

## Avvisi automatici di verifica

Matrix ora pubblica gli avvisi del ciclo di vita della verifica direttamente nella stanza DM di verifica rigorosa come messaggi `m.notice`.
Ciò include:

- avvisi di richiesta di verifica
- avvisi di verifica pronta (con indicazioni esplicite "Verifica tramite emoji")
- avvisi di inizio e completamento della verifica
- dettagli SAS (emoji e decimali) quando disponibili

Le richieste di verifica in ingresso da un altro client Matrix vengono tracciate e accettate automaticamente da OpenClaw.
Per i flussi di autoverifica, OpenClaw avvia automaticamente anche il flusso SAS quando la verifica tramite emoji diventa disponibile e conferma il proprio lato.
Per le richieste di verifica da un altro utente/dispositivo Matrix, OpenClaw accetta automaticamente la richiesta e poi aspetta che il flusso SAS proceda normalmente.
Devi comunque confrontare l'emoji o il SAS decimale nel tuo client Matrix e confermare lì "Corrispondono" per completare la verifica.

OpenClaw non accetta automaticamente alla cieca i flussi duplicati avviati da sé. All'avvio salta la creazione di una nuova richiesta quando una richiesta di autoverifica è già in sospeso.

Gli avvisi di verifica di protocollo/sistema non vengono inoltrati alla pipeline della chat dell'agente, quindi non producono `NO_REPLY`.

### Igiene dei dispositivi

Sul tuo account possono accumularsi vecchi dispositivi Matrix gestiti da OpenClaw, rendendo più difficile interpretare l'affidabilità delle stanze cifrate.
Elencali con:

```bash
openclaw matrix devices list
```

Rimuovi i dispositivi OpenClaw obsoleti con:

```bash
openclaw matrix devices prune-stale
```

### Riparazione Direct Room

Se lo stato dei messaggi diretti va fuori sincrono, OpenClaw può ritrovarsi con mapping `m.direct` obsoleti che puntano a vecchie stanze singole invece che al DM live. Ispeziona il mapping corrente per un peer con:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Riparalo con:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

La riparazione mantiene la logica specifica di Matrix all'interno del plugin:

- preferisce un DM rigoroso 1:1 già mappato in `m.direct`
- altrimenti ripiega su qualunque DM rigoroso 1:1 attualmente unito con quell'utente
- se non esiste alcun DM sano, crea una nuova stanza diretta e riscrive `m.direct` in modo che punti a essa

Il flusso di riparazione non elimina automaticamente le vecchie stanze. Si limita a scegliere il DM sano e aggiornare il mapping così che i nuovi invii Matrix, gli avvisi di verifica e gli altri flussi di messaggi diretti tornino a prendere di mira la stanza corretta.

## Thread

Matrix supporta i thread Matrix nativi sia per le risposte automatiche sia per gli invii del message tool.

- `dm.sessionScope: "per-user"` (predefinito) mantiene il routing DM Matrix con ambito mittente, quindi più stanze DM possono condividere una sessione quando si risolvono allo stesso peer.
- `dm.sessionScope: "per-room"` isola ogni stanza DM Matrix nella propria chiave di sessione pur continuando a usare normali controlli di autenticazione e allowlist dei DM.
- I binding espliciti delle conversazioni Matrix continuano ad avere la precedenza su `dm.sessionScope`, quindi stanze e thread associati mantengono la sessione di destinazione scelta.
- `threadReplies: "off"` mantiene le risposte al livello superiore e conserva i messaggi in thread in ingresso sulla sessione padre.
- `threadReplies: "inbound"` risponde all'interno di un thread solo quando il messaggio in ingresso era già in quel thread.
- `threadReplies: "always"` mantiene le risposte della stanza in un thread radicato nel messaggio che ha attivato la risposta e instrada quella conversazione attraverso la sessione con ambito thread corrispondente fin dal primo messaggio che l'ha attivata.
- `dm.threadReplies` sovrascrive l'impostazione di livello superiore solo per i DM. Ad esempio, puoi mantenere isolati i thread delle stanze lasciando piatti i DM.
- I messaggi in thread in ingresso includono il messaggio radice del thread come contesto aggiuntivo per l'agente.
- Gli invii del message tool ora ereditano automaticamente il thread Matrix corrente quando la destinazione è la stessa stanza, o lo stesso target utente DM, a meno che non venga fornito un `threadId` esplicito.
- Il riuso della stessa sessione per destinazione utente DM scatta solo quando i metadati della sessione corrente dimostrano lo stesso peer DM sullo stesso account Matrix; altrimenti OpenClaw torna al normale routing con ambito utente.
- Quando OpenClaw vede una stanza DM Matrix entrare in collisione con un'altra stanza DM sulla stessa sessione DM Matrix condivisa, pubblica un unico `m.notice` in quella stanza con l'uscita di emergenza `/focus` quando i binding dei thread sono abilitati e con il suggerimento `dm.sessionScope`.
- I binding runtime dei thread sono supportati per Matrix. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` e `/acp spawn` associato a un thread ora funzionano in stanze e DM Matrix.
- `/focus` a livello superiore in una stanza/DM Matrix crea un nuovo thread Matrix e lo associa alla sessione di destinazione quando `threadBindings.spawnSubagentSessions=true`.
- Eseguire `/focus` o `/acp spawn --thread here` all'interno di un thread Matrix esistente associa invece quel thread corrente.

## Binding delle conversazioni ACP

Stanze Matrix, DM e thread Matrix esistenti possono essere trasformati in workspace ACP durevoli senza cambiare la superficie di chat.

Flusso rapido per l'operatore:

- Esegui `/acp spawn codex --bind here` nel DM Matrix, nella stanza o nel thread esistente che vuoi continuare a usare.
- In un DM o stanza Matrix di livello superiore, il DM/stanza corrente resta la superficie di chat e i messaggi futuri vengono instradati alla sessione ACP generata.
- All'interno di un thread Matrix esistente, `--bind here` associa sul posto quel thread corrente.
- `/new` e `/reset` reimpostano sul posto la stessa sessione ACP associata.
- `/acp close` chiude la sessione ACP e rimuove il binding.

Note:

- `--bind here` non crea un thread Matrix figlio.
- `threadBindings.spawnAcpSessions` è richiesto solo per `/acp spawn --thread auto|here`, quando OpenClaw deve creare o associare un thread Matrix figlio.

### Configurazione Thread Binding

Matrix eredita i valori predefiniti globali da `session.threadBindings` e supporta anche sovrascritture per canale:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

I flag di avvio associati ai thread Matrix sono opt-in:

- Imposta `threadBindings.spawnSubagentSessions: true` per consentire a `/focus` di livello superiore di creare e associare nuovi thread Matrix.
- Imposta `threadBindings.spawnAcpSessions: true` per consentire a `/acp spawn --thread auto|here` di associare sessioni ACP ai thread Matrix.

## Reazioni

Matrix supporta azioni di reazione in uscita, notifiche di reazione in ingresso e reazioni ack in ingresso.

- Il tooling delle reazioni in uscita è controllato da `channels["matrix"].actions.reactions`.
- `react` aggiunge una reazione a uno specifico evento Matrix.
- `reactions` elenca il riepilogo corrente delle reazioni per uno specifico evento Matrix.
- `emoji=""` rimuove le reazioni dell'account bot su quell'evento.
- `remove: true` rimuove solo la specifica reazione emoji dall'account bot.

L'ambito delle reazioni ack viene risolto in base a questo ordine:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- fallback all'emoji dell'identità dell'agente

L'ambito della reazione ack viene risolto in questo ordine:

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
- Le rimozioni di reazione non vengono ancora sintetizzate in eventi di sistema perché Matrix le espone come redazioni, non come rimozioni `m.reaction` autonome.

## Contesto della cronologia

- `channels.matrix.historyLimit` controlla quanti messaggi recenti della stanza vengono inclusi come `InboundHistory` quando un messaggio di una stanza Matrix attiva l'agente.
- Usa come fallback `messages.groupChat.historyLimit`. Se entrambi non sono impostati, il valore predefinito effettivo è `0`, quindi i messaggi di stanza con attivazione tramite menzione non vengono bufferizzati. Imposta `0` per disabilitare.
- La cronologia delle stanze Matrix è solo di stanza. I DM continuano a usare la normale cronologia della sessione.
- La cronologia delle stanze Matrix è solo pending: OpenClaw bufferizza i messaggi della stanza che non hanno ancora attivato una risposta, poi acquisisce uno snapshot di quella finestra quando arriva una menzione o un altro trigger.
- Il messaggio di attivazione corrente non è incluso in `InboundHistory`; resta nel corpo principale in ingresso per quel turno.
- I tentativi ripetuti dello stesso evento Matrix riutilizzano lo snapshot originale della cronologia invece di spostarsi in avanti verso messaggi di stanza più recenti.

## Visibilità del contesto

Matrix supporta il controllo condiviso `contextVisibility` per il contesto supplementare della stanza, come testo di risposta recuperato, radici dei thread e cronologia pending.

- `contextVisibility: "all"` è il valore predefinito. Il contesto supplementare viene mantenuto così come ricevuto.
- `contextVisibility: "allowlist"` filtra il contesto supplementare ai mittenti consentiti dai controlli attivi della allowlist di stanza/utente.
- `contextVisibility: "allowlist_quote"` si comporta come `allowlist`, ma mantiene comunque una risposta citata esplicita.

Questa impostazione influisce sulla visibilità del contesto supplementare, non sul fatto che il messaggio in ingresso stesso possa attivare una risposta.
L'autorizzazione del trigger continua a dipendere da `groupPolicy`, `groups`, `groupAllowFrom` e dalle impostazioni dei criteri DM.

## Esempio di policy per DM e stanze

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

Vedi [Groups](/it/channels/groups) per il comportamento della menzione obbligatoria e della allowlist.

Esempio di pairing per i DM Matrix:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Se un utente Matrix non approvato continua a inviarti messaggi prima dell'approvazione, OpenClaw riutilizza lo stesso codice di pairing in sospeso e può inviare di nuovo una risposta di promemoria dopo un breve cooldown invece di generarne uno nuovo.

Vedi [Pairing](/it/channels/pairing) per il flusso condiviso di pairing dei DM e il layout di storage.

## Approvazioni exec

Matrix può agire come client di approvazione exec per un account Matrix.

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (facoltativo; usa come fallback `channels.matrix.dm.allowFrom`)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, predefinito: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Gli approvatori devono essere ID utente Matrix come `@owner:example.org`. Matrix abilita automaticamente le approvazioni exec native quando `enabled` non è impostato oppure è `"auto"` e almeno un approvatore può essere risolto, sia da `execApprovals.approvers` sia da `channels.matrix.dm.allowFrom`. Imposta `enabled: false` per disabilitare esplicitamente Matrix come client di approvazione nativo. Altrimenti le richieste di approvazione usano come fallback altri percorsi di approvazione configurati o la policy di fallback per l'approvazione exec.

Il routing nativo Matrix oggi è solo per exec:

- `channels.matrix.execApprovals.*` controlla il routing DM/canale nativo solo per le approvazioni exec.
- Le approvazioni dei plugin usano ancora il comando condiviso `/approve` nella stessa chat più l'eventuale inoltro configurato in `approvals.plugin`.
- Matrix può ancora riutilizzare `channels.matrix.dm.allowFrom` per l'autorizzazione delle approvazioni dei plugin quando può dedurre in sicurezza gli approvatori, ma non espone un percorso nativo separato di fanout DM/canale per le approvazioni dei plugin.

Regole di consegna:

- `target: "dm"` invia i prompt di approvazione ai DM degli approvatori
- `target: "channel"` rimanda il prompt alla stanza o al DM Matrix di origine
- `target: "both"` invia ai DM degli approvatori e alla stanza o al DM Matrix di origine

I prompt di approvazione Matrix inizializzano scorciatoie tramite reazioni sul messaggio di approvazione principale:

- `✅` = consenti una volta
- `❌` = nega
- `♾️` = consenti sempre quando quella decisione è permessa dalla policy exec effettiva

Gli approvatori possono reagire a quel messaggio o usare i comandi slash di fallback: `/approve <id> allow-once`, `/approve <id> allow-always` oppure `/approve <id> deny`.

Solo gli approvatori risolti possono approvare o negare. La consegna sul canale include il testo del comando, quindi abilita `channel` o `both` solo in stanze fidate.

I prompt di approvazione Matrix riutilizzano il planner di approvazione condiviso del core. La superficie nativa specifica di Matrix è solo il trasporto per le approvazioni exec: routing stanza/DM e comportamento di invio/aggiornamento/eliminazione dei messaggi.

Sovrascrittura per account:

- `channels.matrix.accounts.<account>.execApprovals`

Documentazione correlata: [Exec approvals](/it/tools/exec-approvals)

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

I valori di livello superiore in `channels.matrix` fungono da predefiniti per gli account con nome, a meno che un account non li sovrascriva.
Puoi assegnare una voce stanza ereditata a un singolo account Matrix con `groups.<room>.account` (o il legacy `rooms.<room>.account`).
Le voci senza `account` restano condivise tra tutti gli account Matrix, e le voci con `account: "default"` continuano a funzionare quando l'account predefinito è configurato direttamente al livello superiore in `channels.matrix.*`.
I predefiniti di autenticazione condivisa parziale non creano da soli un account predefinito implicito separato. OpenClaw sintetizza l'account `default` di livello superiore solo quando quel predefinito ha autenticazione valida (`homeserver` più `accessToken`, oppure `homeserver` più `userId` e `password`); gli account con nome possono comunque restare individuabili da `homeserver` più `userId` quando in seguito le credenziali in cache soddisfano l'autenticazione.
Se Matrix ha già esattamente un account con nome, oppure `defaultAccount` punta a una chiave account con nome esistente, la promozione di riparazione/configurazione da account singolo a multi-account preserva quell'account invece di creare una nuova voce `accounts.default`. Solo le chiavi di autenticazione/bootstrap Matrix vengono spostate in quell'account promosso; le chiavi condivise della policy di consegna restano al livello superiore.
Imposta `defaultAccount` quando vuoi che OpenClaw preferisca un account Matrix con nome per routing implicito, probing e operazioni CLI.
Se configuri più account con nome, imposta `defaultAccount` oppure passa `--account <id>` per i comandi CLI che dipendono dalla selezione implicita dell'account.
Passa `--account <id>` a `openclaw matrix verify ...` e `openclaw matrix devices ...` quando vuoi sovrascrivere quella selezione implicita per un singolo comando.

## Homeserver privati/LAN

Per impostazione predefinita, OpenClaw blocca gli homeserver Matrix privati/interni per protezione SSRF, a meno che tu
non faccia esplicitamente opt-in per account.

Se il tuo homeserver gira su localhost, un IP LAN/Tailscale o un hostname interno, abilita
`allowPrivateNetwork` per quell'account Matrix:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      allowPrivateNetwork: true,
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

Questo opt-in consente solo target privati/interni fidati. Gli homeserver pubblici in chiaro come
`http://matrix.example.org:8008` restano bloccati. Preferisci `https://` quando possibile.

## Proxy del traffico Matrix

Se il tuo deployment Matrix richiede un proxy HTTP(S) esplicito in uscita, imposta `channels.matrix.proxy`:

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
OpenClaw usa la stessa impostazione proxy per il traffico Matrix runtime e per i probe dello stato dell'account.

## Risoluzione della destinazione

Matrix accetta questi formati di destinazione ovunque OpenClaw ti chieda una stanza o un target utente:

- Utenti: `@user:server`, `user:@user:server` o `matrix:user:@user:server`
- Stanze: `!room:server`, `room:!room:server` o `matrix:room:!room:server`
- Alias: `#alias:server`, `channel:#alias:server` o `matrix:channel:#alias:server`

La ricerca live nella directory usa l'account Matrix autenticato:

- Le ricerche utente interrogano la directory utenti Matrix su quell'homeserver.
- Le ricerche stanza accettano direttamente ID stanza e alias espliciti, poi ripiegano sulla ricerca dei nomi delle stanze unite per quell'account.
- La ricerca dei nomi delle stanze unite è best-effort. Se un nome stanza non può essere risolto in un ID o alias, viene ignorato dalla risoluzione runtime della allowlist.

## Riferimento configurazione

- `enabled`: abilita o disabilita il canale.
- `name`: etichetta facoltativa per l'account.
- `defaultAccount`: ID account preferito quando sono configurati più account Matrix.
- `homeserver`: URL dell'homeserver, ad esempio `https://matrix.example.org`.
- `allowPrivateNetwork`: consente a questo account Matrix di connettersi a homeserver privati/interni. Abilitalo quando l'homeserver si risolve in `localhost`, un IP LAN/Tailscale o un host interno come `matrix-synapse`.
- `proxy`: URL facoltativo del proxy HTTP(S) per il traffico Matrix. Gli account con nome possono sovrascrivere il valore predefinito di livello superiore con il proprio `proxy`.
- `userId`: ID utente Matrix completo, ad esempio `@bot:example.org`.
- `accessToken`: token di accesso per l'autenticazione basata su token. Sono supportati valori in chiaro e valori SecretRef per `channels.matrix.accessToken` e `channels.matrix.accounts.<id>.accessToken` tramite provider env/file/exec. Vedi [Secrets Management](/it/gateway/secrets).
- `password`: password per il login basato su password. Sono supportati valori in chiaro e valori SecretRef.
- `deviceId`: ID dispositivo Matrix esplicito.
- `deviceName`: nome visualizzato del dispositivo per il login con password.
- `avatarUrl`: URL avatar personale memorizzato per la sincronizzazione del profilo e gli aggiornamenti `set-profile`.
- `initialSyncLimit`: limite eventi della sincronizzazione all'avvio.
- `encryption`: abilita E2EE.
- `allowlistOnly`: forza un comportamento solo allowlist per DM e stanze.
- `allowBots`: consente messaggi da altri account Matrix OpenClaw configurati (`true` o `"mentions"`).
- `groupPolicy`: `open`, `allowlist` o `disabled`.
- `contextVisibility`: modalità di visibilità del contesto supplementare della stanza (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: allowlist di ID utente per il traffico delle stanze.
- Le voci di `groupAllowFrom` dovrebbero essere ID utente Matrix completi. I nomi non risolti vengono ignorati in fase runtime.
- `historyLimit`: numero massimo di messaggi della stanza da includere come contesto della cronologia del gruppo. Usa come fallback `messages.groupChat.historyLimit`; se entrambi non sono impostati, il valore predefinito effettivo è `0`. Imposta `0` per disabilitare.
- `replyToMode`: `off`, `first` o `all`.
- `markdown`: configurazione facoltativa di rendering Markdown per il testo Matrix in uscita.
- `streaming`: `off` (predefinito), `partial`, `quiet`, `true` o `false`. `partial` e `true` abilitano aggiornamenti della bozza con anteprima iniziale usando normali messaggi di testo Matrix. `quiet` usa avvisi di anteprima senza notifica per configurazioni self-hosted con regole push.
- `blockStreaming`: `true` abilita messaggi di avanzamento separati per i blocchi dell'assistente completati mentre l'anteprima in streaming della bozza è attiva.
- `threadReplies`: `off`, `inbound` o `always`.
- `threadBindings`: sovrascritture per canale per il routing e il ciclo di vita delle sessioni associate ai thread.
- `startupVerification`: modalità automatica della richiesta di autoverifica all'avvio (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: cooldown prima di ritentare richieste automatiche di verifica all'avvio.
- `textChunkLimit`: dimensione dei chunk dei messaggi in uscita.
- `chunkMode`: `length` o `newline`.
- `responsePrefix`: prefisso di messaggio facoltativo per le risposte in uscita.
- `ackReaction`: sovrascrittura facoltativa della reazione ack per questo canale/account.
- `ackReactionScope`: sovrascrittura facoltativa dell'ambito della reazione ack (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: modalità delle notifiche di reazione in ingresso (`own`, `off`).
- `mediaMaxMb`: limite di dimensione dei contenuti multimediali in MB per la gestione Matrix. Si applica agli invii in uscita e all'elaborazione dei contenuti multimediali in ingresso.
- `autoJoin`: policy di auto-join degli inviti (`always`, `allowlist`, `off`). Predefinito: `off`. Si applica agli inviti Matrix in generale, inclusi gli inviti in stile DM, non solo agli inviti di stanze/gruppi. OpenClaw prende questa decisione al momento dell'invito, prima di poter classificare in modo affidabile la stanza unita come DM o gruppo.
- `autoJoinAllowlist`: stanze/alias consentiti quando `autoJoin` è `allowlist`. Le voci alias vengono risolte in ID stanza durante la gestione dell'invito; OpenClaw non si fida dello stato alias dichiarato dalla stanza invitata.
- `dm`: blocco della policy DM (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.policy`: controlla l'accesso DM dopo che OpenClaw è entrato nella stanza e l'ha classificata come DM. Non modifica se un invito venga accettato automaticamente.
- Le voci di `dm.allowFrom` dovrebbero essere ID utente Matrix completi a meno che tu non le abbia già risolte tramite ricerca live nella directory.
- `dm.sessionScope`: `per-user` (predefinito) o `per-room`. Usa `per-room` quando vuoi che ogni stanza DM Matrix mantenga un contesto separato anche se il peer è lo stesso.
- `dm.threadReplies`: sovrascrittura della policy thread solo per i DM (`off`, `inbound`, `always`). Sovrascrive l'impostazione `threadReplies` di livello superiore sia per il posizionamento delle risposte sia per l'isolamento della sessione nei DM.
- `execApprovals`: consegna di approvazione exec nativa Matrix (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: ID utente Matrix autorizzati ad approvare richieste exec. Facoltativo quando `dm.allowFrom` identifica già gli approvatori.
- `execApprovals.target`: `dm | channel | both` (predefinito: `dm`).
- `accounts`: sovrascritture nominate per account. I valori di livello superiore in `channels.matrix` fungono da predefiniti per queste voci.
- `groups`: mappa delle policy per stanza. Preferisci ID stanza o alias; i nomi stanza non risolti vengono ignorati in fase runtime. L'identità di sessione/gruppo usa l'ID stanza stabile dopo la risoluzione, mentre le etichette leggibili restano derivate dai nomi delle stanze.
- `groups.<room>.account`: limita una voce stanza ereditata a uno specifico account Matrix nelle configurazioni multi-account.
- `groups.<room>.allowBots`: sovrascrittura a livello stanza per mittenti bot configurati (`true` o `"mentions"`).
- `groups.<room>.users`: allowlist dei mittenti per stanza.
- `groups.<room>.tools`: sovrascritture per stanza di allow/deny dei tool.
- `groups.<room>.autoReply`: sovrascrittura a livello stanza della menzione obbligatoria. `true` disabilita i requisiti di menzione per quella stanza; `false` li forza di nuovo.
- `groups.<room>.skills`: filtro facoltativo delle Skills a livello stanza.
- `groups.<room>.systemPrompt`: frammento facoltativo di system prompt a livello stanza.
- `rooms`: alias legacy di `groups`.
- `actions`: controllo per azione dei tool (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## Correlati

- [Channels Overview](/it/channels) — tutti i canali supportati
- [Pairing](/it/channels/pairing) — autenticazione DM e flusso di pairing
- [Groups](/it/channels/groups) — comportamento delle chat di gruppo e menzione obbligatoria
- [Channel Routing](/it/channels/channel-routing) — routing di sessione per i messaggi
- [Security](/it/gateway/security) — modello di accesso e hardening
