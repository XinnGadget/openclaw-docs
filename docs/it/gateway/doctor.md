---
read_when:
    - Stai aggiungendo o modificando migrazioni di doctor
    - Stai introducendo modifiche incompatibili alla configurazione
summary: 'Comando Doctor: controlli di integrità, migrazioni della configurazione e passaggi di riparazione'
title: Doctor
x-i18n:
    generated_at: "2026-04-09T01:29:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 75d321bd1ad0e16c29f2382e249c51edfc3a8d33b55bdceea39e7dbcd4901fce
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor` è lo strumento di riparazione + migrazione di OpenClaw. Corregge
configurazioni/stati obsoleti, controlla l'integrità e fornisce passaggi di
riparazione concreti.

## Avvio rapido

```bash
openclaw doctor
```

### Headless / automazione

```bash
openclaw doctor --yes
```

Accetta le impostazioni predefinite senza richiedere conferma (inclusi i passaggi di ripristino di riavvio/servizio/sandbox quando applicabili).

```bash
openclaw doctor --repair
```

Applica le riparazioni consigliate senza richiedere conferma (riparazioni + riavvii dove sicuro).

```bash
openclaw doctor --repair --force
```

Applica anche riparazioni aggressive (sovrascrive configurazioni del supervisor personalizzate).

```bash
openclaw doctor --non-interactive
```

Esegue senza richieste e applica solo migrazioni sicure (normalizzazione della configurazione + spostamenti dello stato su disco). Salta le azioni di riavvio/servizio/sandbox che richiedono conferma umana.
Le migrazioni dello stato legacy vengono eseguite automaticamente quando rilevate.

```bash
openclaw doctor --deep
```

Analizza i servizi di sistema per installazioni gateway aggiuntive (launchd/systemd/schtasks).

Se vuoi rivedere le modifiche prima di scrivere, apri prima il file di configurazione:

```bash
cat ~/.openclaw/openclaw.json
```

## Cosa fa (riepilogo)

- Aggiornamento pre-flight facoltativo per installazioni git (solo interattivo).
- Controllo dell'aggiornamento del protocollo UI (ricostruisce la Control UI quando lo schema del protocollo è più recente).
- Controllo di integrità + richiesta di riavvio.
- Riepilogo dello stato delle Skills (idonee/mancanti/bloccate) e stato dei plugin.
- Normalizzazione della configurazione per valori legacy.
- Migrazione della configurazione Talk dai campi legacy piatti `talk.*` a `talk.provider` + `talk.providers.<provider>`.
- Controlli di migrazione del browser per configurazioni legacy dell'estensione Chrome e preparazione di Chrome MCP.
- Avvisi sulle sostituzioni del provider OpenCode (`models.providers.opencode` / `models.providers.opencode-go`).
- Avvisi sull'oscuramento di Codex OAuth (`models.providers.openai-codex`).
- Controllo dei prerequisiti OAuth TLS per i profili OAuth OpenAI Codex.
- Migrazione legacy dello stato su disco (sessioni/dir agente/autenticazione WhatsApp).
- Migrazione legacy della chiave del contratto del manifest del plugin (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- Migrazione legacy dell'archivio cron (`jobId`, `schedule.cron`, campi delivery/payload di primo livello, `provider` nel payload, semplici job di fallback webhook `notify: true`).
- Ispezione dei file di lock della sessione e pulizia dei lock obsoleti.
- Controlli di integrità e permessi dello stato (sessioni, trascrizioni, directory di stato).
- Controlli dei permessi del file di configurazione (chmod 600) quando eseguito in locale.
- Integrità dell'autenticazione del modello: controlla la scadenza OAuth, può aggiornare token in scadenza e segnala stati di cooldown/disabilitazione del profilo auth.
- Rilevamento di directory workspace aggiuntive (`~/openclaw`).
- Riparazione dell'immagine sandbox quando la sandbox è abilitata.
- Migrazione di servizi legacy e rilevamento di gateway aggiuntivi.
- Migrazione dello stato legacy del canale Matrix (in modalità `--fix` / `--repair`).
- Controlli del runtime del gateway (servizio installato ma non in esecuzione; etichetta launchd in cache).
- Avvisi sullo stato dei canali (rilevati dal gateway in esecuzione).
- Audit della configurazione del supervisor (launchd/systemd/schtasks) con riparazione facoltativa.
- Controlli delle best practice del runtime del gateway (Node vs Bun, percorsi dei version manager).
- Diagnostica dei conflitti di porta del gateway (predefinita `18789`).
- Avvisi di sicurezza per policy DM aperte.
- Controlli di autenticazione del gateway per la modalità token locale (offre la generazione del token quando non esiste una sorgente token; non sovrascrive configurazioni token SecretRef).
- Controllo di `linger` per systemd su Linux.
- Controllo della dimensione dei file bootstrap del workspace (avvisi per troncamento/quasi limite dei file di contesto).
- Controllo dello stato del completamento della shell e installazione/aggiornamento automatici.
- Controllo di preparazione del provider di embedding per la ricerca nella memoria (modello locale, chiave API remota o binario QMD).
- Controlli dell'installazione da sorgente (mismatch del workspace pnpm, asset UI mancanti, binario tsx mancante).
- Scrive la configurazione aggiornata + i metadati del wizard.

## Backfill e reset Dreams UI

La scena Dreams della Control UI include le azioni **Backfill**, **Reset** e **Clear Grounded**
per il flusso di lavoro di grounded dreaming. Queste azioni usano metodi RPC
in stile doctor del gateway, ma **non** fanno parte della riparazione/migrazione
della CLI `openclaw doctor`.

Cosa fanno:

- **Backfill** analizza i file storici `memory/YYYY-MM-DD.md` nel workspace
  attivo, esegue il passaggio grounded REM diary e scrive voci di backfill
  reversibili in `DREAMS.md`.
- **Reset** rimuove da `DREAMS.md` solo le voci del diario di backfill contrassegnate.
- **Clear Grounded** rimuove solo le voci staged grounded-only a breve termine
  provenienti dal replay storico e che non hanno ancora accumulato richiamo live
  o supporto giornaliero.

Cosa **non** fanno da sole:

- non modificano `MEMORY.md`
- non eseguono migrazioni complete di doctor
- non mettono automaticamente in staging i candidati grounded nell'archivio live
  di promozione a breve termine, a meno che tu non esegua prima esplicitamente il percorso CLI staged

Se vuoi che il replay storico grounded influenzi il normale percorso di
promozione profonda, usa invece il flusso CLI:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

Questo mette in staging i candidati durevoli grounded nell'archivio di dreaming a breve termine mantenendo `DREAMS.md` come superficie di revisione.

## Comportamento dettagliato e motivazione

### 0) Aggiornamento facoltativo (installazioni git)

Se si tratta di un checkout git e doctor viene eseguito in modo interattivo, offre di
aggiornare (fetch/rebase/build) prima di eseguire doctor.

### 1) Normalizzazione della configurazione

Se la configurazione contiene forme di valori legacy (ad esempio `messages.ackReaction`
senza una sostituzione specifica per canale), doctor le normalizza nello schema attuale.

Questo include i campi legacy piatti di Talk. La configurazione pubblica attuale di Talk è
`talk.provider` + `talk.providers.<provider>`. Doctor riscrive le vecchie forme
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` nella mappa dei provider.

### 2) Migrazioni delle chiavi di configurazione legacy

Quando la configurazione contiene chiavi deprecate, gli altri comandi si rifiutano di essere eseguiti e ti chiedono
di eseguire `openclaw doctor`.

Doctor eseguirà queste operazioni:

- Spiegare quali chiavi legacy sono state trovate.
- Mostrare la migrazione applicata.
- Riscrivere `~/.openclaw/openclaw.json` con lo schema aggiornato.

Il Gateway esegue automaticamente anche le migrazioni doctor all'avvio quando rileva un
formato di configurazione legacy, quindi le configurazioni obsolete vengono riparate senza intervento manuale.
Le migrazioni dell'archivio dei job cron sono gestite da `openclaw doctor --fix`.

Migrazioni attuali:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → `bindings` di primo livello
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- legacy `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `messages.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `messages.tts.providers.<provider>`
- `channels.discord.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.voice.tts.providers.<provider>`
- `channels.discord.accounts.<id>.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.accounts.<id>.voice.tts.providers.<provider>`
- `plugins.entries.voice-call.config.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `plugins.entries.voice-call.config.tts.providers.<provider>`
- `plugins.entries.voice-call.config.provider: "log"` → `"mock"`
- `plugins.entries.voice-call.config.twilio.from` → `plugins.entries.voice-call.config.fromNumber`
- `plugins.entries.voice-call.config.streaming.sttProvider` → `plugins.entries.voice-call.config.streaming.provider`
- `plugins.entries.voice-call.config.streaming.openaiApiKey|sttModel|silenceDurationMs|vadThreshold`
  → `plugins.entries.voice-call.config.streaming.providers.openai.*`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- Per i canali con `accounts` nominati ma con ancora valori di canale di primo livello per account singolo, sposta quei valori con ambito account nell'account promosso scelto per quel canale (`accounts.default` per la maggior parte dei canali; Matrix può preservare un target nominato/predefinito corrispondente esistente)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- rimuove `browser.relayBindHost` (impostazione legacy del relay dell'estensione)

Gli avvisi di doctor includono anche indicazioni sul default account per i canali multi-account:

- Se sono configurate due o più voci `channels.<channel>.accounts` senza `channels.<channel>.defaultAccount` o `accounts.default`, doctor avvisa che il routing di fallback può selezionare un account imprevisto.
- Se `channels.<channel>.defaultAccount` è impostato su un ID account sconosciuto, doctor avvisa ed elenca gli ID account configurati.

### 2b) Sostituzioni del provider OpenCode

Se hai aggiunto manualmente `models.providers.opencode`, `opencode-zen` o `opencode-go`,
questo sostituisce il catalogo OpenCode integrato da `@mariozechner/pi-ai`.
Può forzare i modelli sull'API sbagliata o azzerare i costi. Doctor avvisa in modo che tu
possa rimuovere la sostituzione e ripristinare il routing API + i costi per modello.

### 2c) Migrazione del browser e preparazione di Chrome MCP

Se la tua configurazione del browser punta ancora al percorso rimosso dell'estensione Chrome, doctor
la normalizza nell'attuale modello di collegamento Chrome MCP host-local:

- `browser.profiles.*.driver: "extension"` diventa `"existing-session"`
- `browser.relayBindHost` viene rimosso

Doctor controlla anche il percorso Chrome MCP host-local quando usi `defaultProfile:
"user"` o un profilo `existing-session` configurato:

- verifica se Google Chrome è installato sullo stesso host per i profili di
  connessione automatica predefiniti
- controlla la versione di Chrome rilevata e avvisa quando è inferiore a Chrome 144
- ricorda di abilitare il debug remoto nella pagina inspect del browser (ad
  esempio `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`,
  o `edge://inspect/#remote-debugging`)

Doctor non può abilitare per te l'impostazione lato Chrome. Chrome MCP host-local
richiede comunque:

- un browser basato su Chromium 144+ sull'host gateway/node
- il browser in esecuzione localmente
- il debug remoto abilitato in quel browser
- l'approvazione del primo prompt di consenso al collegamento nel browser

La preparazione qui riguarda solo i prerequisiti per il collegamento locale. Existing-session mantiene
gli attuali limiti di routing di Chrome MCP; percorsi avanzati come `responsebody`, esportazione PDF,
intercettazione dei download e azioni batch richiedono ancora un browser gestito
o un profilo CDP raw.

Questo controllo **non** si applica a Docker, sandbox, remote-browser o altri
flussi headless. Questi continuano a usare raw CDP.

### 2d) Prerequisiti OAuth TLS

Quando è configurato un profilo OAuth OpenAI Codex, doctor verifica l'endpoint di
autorizzazione OpenAI per controllare che lo stack TLS locale Node/OpenSSL possa
validare la catena di certificati. Se la verifica fallisce con un errore di certificato (ad
esempio `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, certificato scaduto o certificato autofirmato),
doctor stampa indicazioni di correzione specifiche per piattaforma. Su macOS con un Node Homebrew, la
correzione è di solito `brew postinstall ca-certificates`. Con `--deep`, la verifica viene eseguita
anche se il gateway è integro.

### 2c) Sostituzioni del provider Codex OAuth

Se in precedenza hai aggiunto impostazioni legacy del trasporto OpenAI sotto
`models.providers.openai-codex`, queste possono oscurare il percorso del
provider Codex OAuth integrato che le versioni più recenti usano automaticamente. Doctor avvisa quando vede
quelle vecchie impostazioni di trasporto insieme a Codex OAuth in modo che tu possa rimuovere o riscrivere
la sostituzione del trasporto obsoleta e recuperare il comportamento integrato di routing/fallback.
I proxy personalizzati e le sostituzioni solo-header sono ancora supportati e non
attivano questo avviso.

### 3) Migrazioni dello stato legacy (layout su disco)

Doctor può migrare vecchi layout su disco nella struttura attuale:

- Archivio sessioni + trascrizioni:
  - da `~/.openclaw/sessions/` a `~/.openclaw/agents/<agentId>/sessions/`
- Directory agente:
  - da `~/.openclaw/agent/` a `~/.openclaw/agents/<agentId>/agent/`
- Stato auth WhatsApp (Baileys):
  - da `~/.openclaw/credentials/*.json` legacy (eccetto `oauth.json`)
  - a `~/.openclaw/credentials/whatsapp/<accountId>/...` (ID account predefinito: `default`)

Queste migrazioni sono best-effort e idempotenti; doctor emetterà avvisi quando
lascia eventuali cartelle legacy come backup. Anche Gateway/CLI migrano automaticamente
all'avvio le sessioni legacy + la directory agente, quindi cronologia/auth/modelli finiscono nel
percorso per agente senza eseguire manualmente doctor. L'auth WhatsApp viene intenzionalmente
migrata solo tramite `openclaw doctor`. La normalizzazione di provider/mappa provider di Talk ora
confronta per uguaglianza strutturale, quindi differenze solo nell'ordine delle chiavi non attivano più
modifiche ripetute e inutili di `doctor --fix`.

### 3a) Migrazioni legacy del manifest dei plugin

Doctor analizza tutti i manifest dei plugin installati per trovare chiavi di capability
di primo livello deprecate (`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`). Quando le trova, propone di spostarle nell'oggetto `contracts`
e di riscrivere il file del manifest sul posto. Questa migrazione è idempotente;
se la chiave `contracts` contiene già gli stessi valori, la chiave legacy viene rimossa
senza duplicare i dati.

### 3b) Migrazioni legacy dell'archivio cron

Doctor controlla anche l'archivio dei job cron (`~/.openclaw/cron/jobs.json` per impostazione predefinita,
o `cron.store` quando sostituito) per trovare forme di job vecchie che lo scheduler accetta ancora
per compatibilità.

Le pulizie cron correnti includono:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- campi payload di primo livello (`message`, `model`, `thinking`, ...) → `payload`
- campi delivery di primo livello (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- alias delivery `provider` nel payload → `delivery.channel` esplicito
- semplici job legacy di fallback webhook `notify: true` → `delivery.mode="webhook"` esplicito con `delivery.to=cron.webhook`

Doctor migra automaticamente i job `notify: true` solo quando può farlo senza
cambiare comportamento. Se un job combina il fallback legacy di notify con una modalità
delivery non-webhook esistente, doctor avvisa e lascia quel job per una revisione manuale.

### 3c) Pulizia dei lock di sessione

Doctor analizza ogni directory di sessione dell'agente per trovare file di lock di scrittura obsoleti — file lasciati
indietro quando una sessione è terminata in modo anomalo. Per ogni file di lock trovato segnala:
il percorso, il PID, se il PID è ancora attivo, l'età del lock e se è
considerato obsoleto (PID morto o più vecchio di 30 minuti). In modalità `--fix` / `--repair`
rimuove automaticamente i file di lock obsoleti; altrimenti stampa una nota e
ti dice di rieseguire con `--fix`.

### 4) Controlli di integrità dello stato (persistenza della sessione, routing e sicurezza)

La directory di stato è il tronco encefalico operativo. Se scompare, perdi
sessioni, credenziali, log e configurazione (a meno che tu non abbia backup altrove).

Doctor controlla:

- **Directory di stato mancante**: avvisa della perdita catastrofica dello stato, chiede di ricreare
  la directory e ricorda che non può recuperare i dati mancanti.
- **Permessi della directory di stato**: verifica la scrivibilità; offre di riparare i permessi
  (ed emette un suggerimento `chown` quando rileva una mancata corrispondenza tra proprietario/gruppo).
- **Directory di stato macOS sincronizzata con il cloud**: avvisa quando lo stato si risolve sotto iCloud Drive
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) o
  `~/Library/CloudStorage/...` perché i percorsi supportati dalla sincronizzazione possono causare I/O più lenti
  e race di lock/sincronizzazione.
- **Directory di stato Linux su SD o eMMC**: avvisa quando lo stato si risolve in una sorgente di mount `mmcblk*`,
  perché l'I/O casuale supportato da SD o eMMC può essere più lento e usurarsi più
  rapidamente con scritture di sessione e credenziali.
- **Directory di sessione mancanti**: `sessions/` e la directory dell'archivio sessioni sono
  necessarie per mantenere la cronologia ed evitare crash `ENOENT`.
- **Mismatch della trascrizione**: avvisa quando voci di sessione recenti hanno file di
  trascrizione mancanti.
- **Sessione principale “JSONL a 1 riga”**: segnala quando la trascrizione principale ha una sola
  riga (la cronologia non si sta accumulando).
- **Più directory di stato**: avvisa quando esistono più cartelle `~/.openclaw` in diverse
  home directory o quando `OPENCLAW_STATE_DIR` punta altrove (la cronologia può
  dividersi tra installazioni).
- **Promemoria modalità remota**: se `gateway.mode=remote`, doctor ricorda di eseguirlo
  sull'host remoto (lo stato si trova lì).
- **Permessi del file di configurazione**: avvisa se `~/.openclaw/openclaw.json` è
  leggibile da gruppo/altri e offre di restringerlo a `600`.

### 5) Integrità auth del modello (scadenza OAuth)

Doctor ispeziona i profili OAuth nell'archivio auth, avvisa quando i token
stanno per scadere o sono scaduti e può aggiornarli quando è sicuro. Se il profilo
OAuth/token Anthropic è obsoleto, suggerisce una chiave API Anthropic o il
percorso setup-token Anthropic.
Le richieste di refresh compaiono solo in esecuzione interattiva (TTY); `--non-interactive`
salta i tentativi di refresh.

Quando un refresh OAuth fallisce in modo permanente (ad esempio `refresh_token_reused`,
`invalid_grant`, o un provider che ti dice di accedere di nuovo), doctor segnala
che è richiesta una nuova autenticazione e stampa il comando esatto `openclaw models auth login --provider ...`
da eseguire.

Doctor segnala anche i profili auth temporaneamente inutilizzabili a causa di:

- brevi cooldown (limiti di frequenza/timeout/errori auth)
- disabilitazioni più lunghe (errori di fatturazione/credito)

### 6) Validazione del modello Hooks

Se `hooks.gmail.model` è impostato, doctor valida il riferimento al modello rispetto al
catalogo e alla allowlist e avvisa quando non verrà risolto o non è consentito.

### 7) Riparazione dell'immagine sandbox

Quando la sandbox è abilitata, doctor controlla le immagini Docker e offre di compilare o
passare a nomi legacy se l'immagine attuale manca.

### 7b) Dipendenze runtime dei plugin integrati

Doctor verifica che le dipendenze runtime dei plugin integrati (ad esempio i
pacchetti runtime del plugin Discord) siano presenti nella root di installazione di OpenClaw.
Se ne manca qualcuna, doctor segnala i pacchetti e li installa in modalità
`openclaw doctor --fix` / `openclaw doctor --repair`.

### 8) Migrazioni del servizio gateway e suggerimenti di pulizia

Doctor rileva i servizi gateway legacy (launchd/systemd/schtasks) e
offre di rimuoverli e installare il servizio OpenClaw usando la porta gateway attuale.
Può anche cercare servizi aggiuntivi simili a gateway e stampare suggerimenti di pulizia.
I servizi gateway OpenClaw con nome del profilo sono considerati di prima classe e non vengono
contrassegnati come "aggiuntivi".

### 8b) Migrazione Matrix all'avvio

Quando un account del canale Matrix ha una migrazione dello stato legacy in sospeso o applicabile,
doctor (in modalità `--fix` / `--repair`) crea uno snapshot pre-migrazione e poi
esegue i passaggi di migrazione best-effort: migrazione dello stato Matrix legacy e preparazione
legacy dello stato cifrato. Entrambi i passaggi non sono fatali; gli errori vengono registrati e
l'avvio continua. In modalità sola lettura (`openclaw doctor` senza `--fix`) questo controllo
viene saltato completamente.

### 9) Avvisi di sicurezza

Doctor emette avvisi quando un provider è aperto ai DM senza una allowlist, o
quando una policy è configurata in modo pericoloso.

### 10) systemd linger (Linux)

Se è in esecuzione come servizio utente systemd, doctor assicura che lingering sia abilitato in modo che il
gateway resti attivo dopo il logout.

### 11) Stato del workspace (Skills, plugin e directory legacy)

Doctor stampa un riepilogo dello stato del workspace per l'agente predefinito:

- **Stato delle Skills**: conta le Skills idonee, con requisiti mancanti e bloccate dalla allowlist.
- **Directory workspace legacy**: avvisa quando `~/openclaw` o altre directory workspace legacy
  esistono accanto al workspace attuale.
- **Stato dei plugin**: conta i plugin caricati/disabilitati/in errore; elenca gli ID plugin per eventuali
  errori; segnala le capability dei plugin bundle.
- **Avvisi di compatibilità dei plugin**: segnala i plugin che hanno problemi di compatibilità con
  il runtime attuale.
- **Diagnostica dei plugin**: mostra eventuali avvisi o errori di caricamento emessi dal
  registro plugin.

### 11b) Dimensione del file bootstrap

Doctor controlla se i file bootstrap del workspace (ad esempio `AGENTS.md`,
`CLAUDE.md` o altri file di contesto iniettati) sono vicini o oltre il budget
di caratteri configurato. Riporta per file il numero di caratteri raw rispetto a quelli iniettati, la percentuale
di troncamento, la causa del troncamento (`max/file` o `max/total`) e il totale dei caratteri
iniettati come frazione del budget totale. Quando i file sono troncati o vicini
al limite, doctor stampa suggerimenti per regolare `agents.defaults.bootstrapMaxChars`
e `agents.defaults.bootstrapTotalMaxChars`.

### 11c) Completamento della shell

Doctor controlla se il completamento tramite tab è installato per la shell attuale
(zsh, bash, fish o PowerShell):

- Se il profilo della shell usa un pattern di completamento dinamico lento
  (`source <(openclaw completion ...)`), doctor lo aggiorna alla variante più veloce
  con file in cache.
- Se il completamento è configurato nel profilo ma il file cache manca,
  doctor rigenera automaticamente la cache.
- Se non è configurato alcun completamento, doctor propone di installarlo
  (solo modalità interattiva; saltato con `--non-interactive`).

Esegui `openclaw completion --write-state` per rigenerare manualmente la cache.

### 12) Controlli auth del gateway (token locale)

Doctor controlla la preparazione dell'autenticazione token del gateway locale.

- Se la modalità token richiede un token e non esiste alcuna sorgente token, doctor propone di generarne uno.
- Se `gateway.auth.token` è gestito da SecretRef ma non disponibile, doctor avvisa e non lo sovrascrive con testo in chiaro.
- `openclaw doctor --generate-gateway-token` forza la generazione solo quando non è configurato alcun token SecretRef.

### 12b) Riparazioni in sola lettura consapevoli di SecretRef

Alcuni flussi di riparazione devono ispezionare le credenziali configurate senza indebolire il comportamento runtime fail-fast.

- `openclaw doctor --fix` ora usa lo stesso modello riassuntivo SecretRef in sola lettura dei comandi della famiglia status per riparazioni di configurazione mirate.
- Esempio: la riparazione Telegram `allowFrom` / `groupAllowFrom` con `@username` prova a usare le credenziali del bot configurate quando disponibili.
- Se il token del bot Telegram è configurato tramite SecretRef ma non disponibile nel percorso del comando corrente, doctor segnala che la credenziale è configurata-ma-non-disponibile e salta la risoluzione automatica invece di andare in crash o segnalare erroneamente che il token manca.

### 13) Controllo di integrità del gateway + riavvio

Doctor esegue un controllo di integrità e offre di riavviare il gateway quando
sembra non integro.

### 13b) Preparazione della ricerca nella memoria

Doctor controlla se il provider di embedding configurato per la ricerca nella memoria è pronto
per l'agente predefinito. Il comportamento dipende dal backend e dal provider configurati:

- **Backend QMD**: verifica se il binario `qmd` è disponibile e avviabile.
  In caso contrario, stampa indicazioni di correzione incluse il pacchetto npm e un'opzione manuale per il percorso del binario.
- **Provider locale esplicito**: controlla la presenza di un file modello locale o di un URL modello remoto/scaricabile riconosciuto. Se manca, suggerisce di passare a un provider remoto.
- **Provider remoto esplicito** (`openai`, `voyage`, ecc.): verifica che una chiave API sia
  presente nell'ambiente o nell'archivio auth. Stampa suggerimenti di correzione concreti se manca.
- **Provider automatico**: controlla prima la disponibilità del modello locale, poi prova ciascun provider remoto
  nell'ordine di selezione automatica.

Quando è disponibile un risultato della verifica del gateway (il gateway era integro al momento del
controllo), doctor lo confronta con la configurazione visibile dalla CLI e annota
qualsiasi discrepanza.

Usa `openclaw memory status --deep` per verificare la preparazione dell'embedding a runtime.

### 14) Avvisi sullo stato dei canali

Se il gateway è integro, doctor esegue una verifica dello stato dei canali e segnala
avvisi con le correzioni suggerite.

### 15) Audit + riparazione della configurazione del supervisor

Doctor controlla la configurazione del supervisor installata (launchd/systemd/schtasks) per
individuare valori predefiniti mancanti o obsoleti (ad esempio dipendenze systemd network-online e
ritardo di riavvio). Quando trova una mancata corrispondenza, consiglia un aggiornamento e può
riscrivere il file di servizio/task con i valori predefiniti attuali.

Note:

- `openclaw doctor` richiede conferma prima di riscrivere la configurazione del supervisor.
- `openclaw doctor --yes` accetta le richieste di riparazione predefinite.
- `openclaw doctor --repair` applica le correzioni consigliate senza richieste.
- `openclaw doctor --repair --force` sovrascrive configurazioni del supervisor personalizzate.
- Se l'autenticazione token richiede un token e `gateway.auth.token` è gestito da SecretRef, doctor durante installazione/riparazione del servizio valida il SecretRef ma non rende persistenti i valori del token risolti in chiaro nei metadati dell'ambiente del servizio supervisor.
- Se l'autenticazione token richiede un token e il token SecretRef configurato non è risolto, doctor blocca il percorso di installazione/riparazione con indicazioni concrete.
- Se sia `gateway.auth.token` sia `gateway.auth.password` sono configurati e `gateway.auth.mode` non è impostato, doctor blocca installazione/riparazione finché la modalità non viene impostata esplicitamente.
- Per le unità user-systemd Linux, i controlli di deriva del token di doctor ora includono sia le sorgenti `Environment=` sia `EnvironmentFile=` quando confrontano i metadati auth del servizio.
- Puoi sempre forzare una riscrittura completa tramite `openclaw gateway install --force`.

### 16) Diagnostica del runtime gateway + della porta

Doctor ispeziona il runtime del servizio (PID, ultimo stato di uscita) e avvisa quando il
servizio è installato ma non è realmente in esecuzione. Controlla anche i conflitti
sulla porta gateway (predefinita `18789`) e riporta le cause probabili (gateway già
in esecuzione, tunnel SSH).

### 17) Best practice del runtime gateway

Doctor avvisa quando il servizio gateway viene eseguito su Bun o su un percorso Node gestito da version manager
(`nvm`, `fnm`, `volta`, `asdf`, ecc.). I canali WhatsApp + Telegram richiedono Node,
e i percorsi dei version manager possono interrompersi dopo gli aggiornamenti perché il servizio non
carica l'inizializzazione della tua shell. Doctor propone di migrare a un'installazione Node di sistema quando
disponibile (Homebrew/apt/choco).

### 18) Scrittura della configurazione + metadati wizard

Doctor rende persistenti eventuali modifiche alla configurazione e appone i metadati wizard per registrare
l'esecuzione di doctor.

### 19) Suggerimenti per il workspace (backup + sistema di memoria)

Doctor suggerisce un sistema di memoria del workspace quando manca e stampa un suggerimento sul backup
se il workspace non è già sotto git.

Vedi [/concepts/agent-workspace](/it/concepts/agent-workspace) per una guida completa alla
struttura del workspace e al backup git (consigliati GitHub o GitLab privati).
