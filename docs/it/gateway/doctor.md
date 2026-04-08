---
read_when:
    - Aggiunta o modifica delle migrazioni di doctor
    - Introduzione di modifiche incompatibili alla configurazione
summary: 'Comando Doctor: controlli di integrità, migrazioni della configurazione e passaggi di riparazione'
title: Doctor
x-i18n:
    generated_at: "2026-04-08T02:15:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3761a222d9db7088f78215575fa84e5896794ad701aa716e8bf9039a4424dca6
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor` è lo strumento di riparazione + migrazione per OpenClaw. Corregge configurazioni/stati obsoleti, controlla l'integrità e fornisce passaggi di riparazione concreti.

## Avvio rapido

```bash
openclaw doctor
```

### Headless / automazione

```bash
openclaw doctor --yes
```

Accetta i valori predefiniti senza chiedere conferma (inclusi i passaggi di ripristino di riavvio/servizio/sandbox quando applicabili).

```bash
openclaw doctor --repair
```

Applica le riparazioni consigliate senza chiedere conferma (riparazioni + riavvii dove sicuro).

```bash
openclaw doctor --repair --force
```

Applica anche riparazioni aggressive (sovrascrive configurazioni supervisor personalizzate).

```bash
openclaw doctor --non-interactive
```

Esegue senza prompt e applica solo le migrazioni sicure (normalizzazione della configurazione + spostamenti dello stato su disco). Salta le azioni di riavvio/servizio/sandbox che richiedono conferma umana.
Le migrazioni dello stato legacy vengono eseguite automaticamente quando rilevate.

```bash
openclaw doctor --deep
```

Analizza i servizi di sistema alla ricerca di installazioni gateway aggiuntive (launchd/systemd/schtasks).

Se vuoi esaminare le modifiche prima della scrittura, apri prima il file di configurazione:

```bash
cat ~/.openclaw/openclaw.json
```

## Cosa fa (riepilogo)

- Aggiornamento pre-volo facoltativo per installazioni git (solo interattivo).
- Controllo dell'aggiornamento del protocollo UI (ricompila la Control UI quando lo schema del protocollo è più recente).
- Controllo integrità + prompt di riavvio.
- Riepilogo stato Skills (idonee/mancanti/bloccate) e stato dei plugin.
- Normalizzazione della configurazione per valori legacy.
- Migrazione della configurazione Talk dai campi legacy piatti `talk.*` a `talk.provider` + `talk.providers.<provider>`.
- Controlli di migrazione browser per configurazioni legacy dell'estensione Chrome e disponibilità di Chrome MCP.
- Avvisi di override del provider OpenCode (`models.providers.opencode` / `models.providers.opencode-go`).
- Avvisi di shadowing OAuth Codex (`models.providers.openai-codex`).
- Controllo dei prerequisiti TLS OAuth per i profili OAuth di OpenAI Codex.
- Migrazione dello stato legacy su disco (sessions/agent dir/auth WhatsApp).
- Migrazione delle chiavi legacy del contratto del manifest del plugin (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- Migrazione del datastore cron legacy (`jobId`, `schedule.cron`, campi delivery/payload di primo livello, `provider` nel payload, job di fallback webhook semplici con `notify: true`).
- Ispezione dei file di lock delle sessioni e pulizia dei lock obsoleti.
- Controlli di integrità e permessi dello stato (sessions, trascrizioni, directory dello stato).
- Controlli sui permessi del file di configurazione (chmod 600) quando eseguito localmente.
- Integrità dell'autenticazione dei modelli: controlla la scadenza OAuth, può aggiornare token in scadenza e segnala stati di cooldown/disabilitazione dei profili auth.
- Rilevamento di directory workspace aggiuntive (`~/openclaw`).
- Riparazione dell'immagine sandbox quando il sandboxing è abilitato.
- Migrazione dei servizi legacy e rilevamento di gateway aggiuntivi.
- Migrazione dello stato legacy del canale Matrix (in modalità `--fix` / `--repair`).
- Controlli runtime del gateway (servizio installato ma non in esecuzione; etichetta launchd in cache).
- Avvisi sullo stato dei canali (sondati dal gateway in esecuzione).
- Audit della configurazione supervisor (launchd/systemd/schtasks) con riparazione facoltativa.
- Controlli delle best practice per il runtime del gateway (Node vs Bun, percorsi dei gestori di versione).
- Diagnostica delle collisioni sulla porta del gateway (predefinita `18789`).
- Avvisi di sicurezza per policy DM aperte.
- Controlli dell'autenticazione del gateway in modalità token locale (offre la generazione del token quando non esiste una sorgente token; non sovrascrive configurazioni token SecretRef).
- Controllo di linger systemd su Linux.
- Controllo della dimensione dei file bootstrap del workspace (avvisi di troncamento/prossimità al limite per i file di contesto).
- Controllo dello stato del completamento della shell e installazione/aggiornamento automatici.
- Controllo della disponibilità del provider di embedding per la ricerca in memoria (modello locale, chiave API remota o binario QMD).
- Controlli dell'installazione sorgente (mismatch del workspace pnpm, asset UI mancanti, binario tsx mancante).
- Scrive la configurazione aggiornata + i metadati del wizard.

## Comportamento dettagliato e motivazione

### 0) Aggiornamento facoltativo (installazioni git)

Se si tratta di un checkout git e doctor è in esecuzione in modalità interattiva, offre di aggiornare (fetch/rebase/build) prima di eseguire doctor.

### 1) Normalizzazione della configurazione

Se la configurazione contiene forme di valori legacy (ad esempio `messages.ackReaction`
senza un override specifico per canale), doctor le normalizza nello schema
corrente.

Questo include i campi piatti legacy di Talk. La configurazione pubblica attuale di Talk è
`talk.provider` + `talk.providers.<provider>`. Doctor riscrive le vecchie forme
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` nella mappa provider.

### 2) Migrazioni delle chiavi di configurazione legacy

Quando la configurazione contiene chiavi deprecate, altri comandi si rifiutano di essere eseguiti e chiedono
di eseguire `openclaw doctor`.

Doctor farà quanto segue:

- Spiegare quali chiavi legacy sono state trovate.
- Mostrare la migrazione applicata.
- Riscrivere `~/.openclaw/openclaw.json` con lo schema aggiornato.

Il Gateway esegue automaticamente anche le migrazioni doctor all'avvio quando rileva un
formato di configurazione legacy, così le configurazioni obsolete vengono riparate senza intervento manuale.
Le migrazioni del datastore dei job cron sono gestite da `openclaw doctor --fix`.

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
- Per i canali con `accounts` nominati ma con persistenti valori di canale di primo livello per account singolo, sposta quei valori con ambito account nell'account promosso scelto per quel canale (`accounts.default` per la maggior parte dei canali; Matrix può mantenere una destinazione nominata/predefinita corrispondente esistente)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- rimuove `browser.relayBindHost` (impostazione relay legacy dell'estensione)

Gli avvisi di doctor includono anche indicazioni sui valori predefiniti degli account per i canali multi-account:

- Se sono configurate due o più voci `channels.<channel>.accounts` senza `channels.<channel>.defaultAccount` o `accounts.default`, doctor avvisa che il routing di fallback può scegliere un account inatteso.
- Se `channels.<channel>.defaultAccount` è impostato su un ID account sconosciuto, doctor avvisa ed elenca gli ID account configurati.

### 2b) Override del provider OpenCode

Se hai aggiunto manualmente `models.providers.opencode`, `opencode-zen` o `opencode-go`,
questo sovrascrive il catalogo OpenCode integrato da `@mariozechner/pi-ai`.
Ciò può forzare i modelli sull'API sbagliata o azzerare i costi. Doctor avvisa così
puoi rimuovere l'override e ripristinare il routing API + i costi per modello.

### 2c) Migrazione browser e disponibilità di Chrome MCP

Se la configurazione del browser punta ancora al percorso dell'estensione Chrome rimossa, doctor
la normalizza all'attuale modello di collegamento Chrome MCP locale all'host:

- `browser.profiles.*.driver: "extension"` diventa `"existing-session"`
- `browser.relayBindHost` viene rimosso

Doctor controlla anche il percorso Chrome MCP locale all'host quando usi `defaultProfile:
"user"` o un profilo `existing-session` configurato:

- controlla se Google Chrome è installato sullo stesso host per i profili predefiniti
  con connessione automatica
- controlla la versione di Chrome rilevata e avvisa quando è inferiore a Chrome 144
- ricorda di abilitare il debug remoto nella pagina inspect del browser (ad
  esempio `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`,
  o `edge://inspect/#remote-debugging`)

Doctor non può abilitare per te l'impostazione lato Chrome. Chrome MCP locale all'host
richiede comunque:

- un browser basato su Chromium 144+ sull'host gateway/node
- il browser in esecuzione localmente
- il debug remoto abilitato in quel browser
- l'approvazione del primo prompt di consenso all'attach nel browser

La disponibilità qui riguarda solo i prerequisiti per l'attach locale. Existing-session mantiene
gli attuali limiti di instradamento Chrome MCP; percorsi avanzati come `responsebody`, esportazione PDF,
intercettazione dei download e azioni batch richiedono ancora un browser
gestito o un profilo CDP grezzo.

Questo controllo **non** si applica a Docker, sandbox, remote-browser o ad altri
flussi headless. Questi continuano a usare CDP grezzo.

### 2d) Prerequisiti OAuth TLS

Quando è configurato un profilo OAuth OpenAI Codex, doctor sonda l'endpoint di
autorizzazione OpenAI per verificare che lo stack TLS locale Node/OpenSSL possa
convalidare la catena di certificati. Se la sonda fallisce con un errore di certificato (ad
esempio `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, certificato scaduto o autofirmato),
doctor stampa indicazioni di correzione specifiche per piattaforma. Su macOS con Node Homebrew, la
correzione è di solito `brew postinstall ca-certificates`. Con `--deep`, la sonda viene eseguita
anche se il gateway è integro.

### 2c) Override del provider OAuth Codex

Se in precedenza hai aggiunto impostazioni legacy del trasporto OpenAI sotto
`models.providers.openai-codex`, queste possono oscurare il percorso del
provider Codex OAuth integrato che le versioni più recenti usano automaticamente. Doctor avvisa quando vede
quelle vecchie impostazioni di trasporto insieme a Codex OAuth così puoi rimuovere o riscrivere
l'override di trasporto obsoleto e riottenere il comportamento integrato di routing/fallback.
Proxy personalizzati e override di sole intestazioni sono ancora supportati e non
attivano questo avviso.

### 3) Migrazioni dello stato legacy (layout su disco)

Doctor può migrare layout su disco più vecchi nella struttura corrente:

- Archivio sessions + trascrizioni:
  - da `~/.openclaw/sessions/` a `~/.openclaw/agents/<agentId>/sessions/`
- Directory agent:
  - da `~/.openclaw/agent/` a `~/.openclaw/agents/<agentId>/agent/`
- Stato auth WhatsApp (Baileys):
  - da `~/.openclaw/credentials/*.json` legacy (eccetto `oauth.json`)
  - a `~/.openclaw/credentials/whatsapp/<accountId>/...` (ID account predefinito: `default`)

Queste migrazioni sono best-effort e idempotenti; doctor emetterà avvisi quando
lascia cartelle legacy come backup. Anche Gateway/CLI migrano automaticamente
sessions legacy + directory agent all'avvio così cronologia/auth/modelli finiscono nel
percorso per agente senza un'esecuzione manuale di doctor. L'auth WhatsApp viene intenzionalmente migrata
solo tramite `openclaw doctor`. La normalizzazione di provider/provider-map di Talk ora
confronta per uguaglianza strutturale, quindi differenze solo nell'ordine delle chiavi non attivano più
modifiche ripetute senza effetto da `doctor --fix`.

### 3a) Migrazioni legacy del manifest del plugin

Doctor analizza tutti i manifest dei plugin installati alla ricerca di chiavi di capacità di primo livello
deprecate (`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`). Quando vengono trovate, propone di spostarle nell'oggetto `contracts`
e riscrivere il file del manifest sul posto. Questa migrazione è idempotente;
se la chiave `contracts` contiene già gli stessi valori, la chiave legacy viene rimossa
senza duplicare i dati.

### 3b) Migrazioni legacy del datastore cron

Doctor controlla anche il datastore dei job cron (`~/.openclaw/cron/jobs.json` per impostazione predefinita,
o `cron.store` se ridefinito) alla ricerca di vecchie forme di job che lo scheduler accetta ancora
per compatibilità.

Le pulizie cron correnti includono:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- campi payload di primo livello (`message`, `model`, `thinking`, ...) → `payload`
- campi delivery di primo livello (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- alias delivery `provider` nel payload → `delivery.channel` esplicito
- semplici job legacy di fallback webhook con `notify: true` → `delivery.mode="webhook"` esplicito con `delivery.to=cron.webhook`

Doctor migra automaticamente i job `notify: true` solo quando può farlo senza
cambiare il comportamento. Se un job combina il fallback notify legacy con una modalità
delivery non-webhook esistente, doctor avvisa e lascia quel job alla revisione manuale.

### 3c) Pulizia dei lock di sessione

Doctor analizza ogni directory di sessione dell'agente alla ricerca di file di lock di scrittura obsoleti —
file lasciati indietro quando una sessione è terminata in modo anomalo. Per ogni file di lock trovato segnala:
il percorso, il PID, se il PID è ancora attivo, l'età del lock e se è
considerato obsoleto (PID morto o più vecchio di 30 minuti). In modalità `--fix` / `--repair`
rimuove automaticamente i file di lock obsoleti; altrimenti stampa una nota e
ti istruisce a rieseguire con `--fix`.

### 4) Controlli di integrità dello stato (persistenza della sessione, routing e sicurezza)

La directory dello stato è il tronco encefalico operativo. Se scompare, perdi
sessioni, credenziali, log e configurazione (a meno che tu non abbia backup altrove).

Doctor controlla:

- **Directory dello stato mancante**: avvisa di una perdita catastrofica dello stato, propone di ricreare
  la directory e ricorda che non può recuperare i dati mancanti.
- **Permessi della directory dello stato**: verifica la scrivibilità; offre di riparare i permessi
  (ed emette un suggerimento `chown` quando rileva una mancata corrispondenza di proprietario/gruppo).
- **Directory dello stato macOS sincronizzata nel cloud**: avvisa quando lo stato si risolve sotto iCloud Drive
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) o
  `~/Library/CloudStorage/...` perché i percorsi supportati dalla sincronizzazione possono causare I/O più lenti
  e gare di lock/sincronizzazione.
- **Directory dello stato Linux su SD o eMMC**: avvisa quando lo stato si risolve su una sorgente di mount `mmcblk*`,
  perché l'I/O casuale su supporto SD o eMMC può essere più lento e usurarsi più rapidamente
  con le scritture di sessioni e credenziali.
- **Directory sessioni mancanti**: `sessions/` e la directory dell'archivio sessioni sono
  necessarie per persistere la cronologia ed evitare crash `ENOENT`.
- **Mancata corrispondenza delle trascrizioni**: avvisa quando le voci di sessione recenti hanno file
  di trascrizione mancanti.
- **Sessione principale “JSONL a 1 riga”**: segnala quando la trascrizione principale ha una sola
  riga (la cronologia non si sta accumulando).
- **Più directory di stato**: avvisa quando esistono più cartelle `~/.openclaw` in
  directory home diverse o quando `OPENCLAW_STATE_DIR` punta altrove (la cronologia può
  dividersi tra installazioni).
- **Promemoria modalità remota**: se `gateway.mode=remote`, doctor ricorda di eseguirlo
  sull'host remoto (lo stato vive lì).
- **Permessi del file di configurazione**: avvisa se `~/.openclaw/openclaw.json` è
  leggibile da gruppo/altri e offre di restringerlo a `600`.

### 5) Integrità auth del modello (scadenza OAuth)

Doctor ispeziona i profili OAuth nell'archivio auth, avvisa quando i token stanno
per scadere/sono scaduti e può aggiornarli quando è sicuro. Se il
profilo OAuth/token Anthropic è obsoleto, suggerisce una chiave API Anthropic o il
percorso setup-token Anthropic.
I prompt di aggiornamento compaiono solo in esecuzione interattiva (TTY); `--non-interactive`
salta i tentativi di aggiornamento.

Doctor segnala anche i profili auth temporaneamente inutilizzabili a causa di:

- brevi cooldown (limiti di frequenza/timeout/errori auth)
- disabilitazioni più lunghe (errori di fatturazione/credito)

### 6) Convalida del modello hooks

Se `hooks.gmail.model` è impostato, doctor convalida il riferimento al modello rispetto al
catalogo e alla allowlist e avvisa quando non viene risolto o non è consentito.

### 7) Riparazione dell'immagine sandbox

Quando il sandboxing è abilitato, doctor controlla le immagini Docker e propone di compilare o
passare ai nomi legacy se l'immagine corrente manca.

### 7b) Dipendenze runtime dei plugin inclusi

Doctor verifica che le dipendenze runtime dei plugin inclusi (ad esempio i
pacchetti runtime del plugin Discord) siano presenti nella root di installazione di OpenClaw.
Se ne manca qualcuna, doctor segnala i pacchetti e li installa in
modalità `openclaw doctor --fix` / `openclaw doctor --repair`.

### 8) Migrazioni dei servizi gateway e suggerimenti di pulizia

Doctor rileva i servizi gateway legacy (launchd/systemd/schtasks) e
offre di rimuoverli e installare il servizio OpenClaw usando la porta gateway
corrente. Può anche cercare servizi aggiuntivi simili a gateway e stampare suggerimenti di pulizia.
I servizi gateway OpenClaw con nome del profilo sono considerati di prima classe e non vengono
contrassegnati come "aggiuntivi".

### 8b) Migrazione Matrix all'avvio

Quando un account del canale Matrix ha una migrazione dello stato legacy in sospeso o attuabile,
doctor (in modalità `--fix` / `--repair`) crea uno snapshot pre-migrazione e poi
esegue i passaggi di migrazione best-effort: migrazione dello stato Matrix legacy e preparazione
legacy dello stato crittografato. Entrambi i passaggi non sono fatali; gli errori vengono registrati e
l'avvio continua. In modalità sola lettura (`openclaw doctor` senza `--fix`) questo controllo
viene saltato completamente.

### 9) Avvisi di sicurezza

Doctor emette avvisi quando un provider è aperto ai DM senza una allowlist, oppure
quando una policy è configurata in modo pericoloso.

### 10) systemd linger (Linux)

Se è in esecuzione come servizio utente systemd, doctor si assicura che il lingering sia abilitato in modo che il
gateway resti attivo dopo il logout.

### 11) Stato del workspace (Skills, plugin e directory legacy)

Doctor stampa un riepilogo dello stato del workspace per l'agente predefinito:

- **Stato Skills**: conta Skills idonee, con requisiti mancanti e bloccate dalla allowlist.
- **Directory workspace legacy**: avvisa quando `~/openclaw` o altre directory workspace legacy
  esistono insieme al workspace corrente.
- **Stato plugin**: conta plugin caricati/disabilitati/in errore; elenca gli ID plugin per eventuali
  errori; segnala le capacità dei plugin bundle.
- **Avvisi di compatibilità dei plugin**: evidenzia i plugin che hanno problemi di compatibilità con
  il runtime corrente.
- **Diagnostica plugin**: mostra eventuali avvisi o errori in fase di caricamento emessi dal
  registro plugin.

### 11b) Dimensione del file bootstrap

Doctor controlla se i file bootstrap del workspace (ad esempio `AGENTS.md`,
`CLAUDE.md` o altri file di contesto iniettati) sono vicini o oltre il budget
di caratteri configurato. Riporta per file il numero di caratteri grezzi vs. iniettati, la percentuale
di troncamento, la causa del troncamento (`max/file` o `max/total`) e il totale dei
caratteri iniettati come frazione del budget totale. Quando i file sono troncati o vicini
al limite, doctor stampa suggerimenti per regolare `agents.defaults.bootstrapMaxChars`
e `agents.defaults.bootstrapTotalMaxChars`.

### 11c) Completamento della shell

Doctor controlla se il completamento tramite tabulazione è installato per la shell
corrente (zsh, bash, fish o PowerShell):

- Se il profilo della shell usa un modello di completamento dinamico lento
  (`source <(openclaw completion ...)`), doctor lo aggiorna alla variante più veloce
  con file in cache.
- Se il completamento è configurato nel profilo ma il file cache manca,
  doctor rigenera automaticamente la cache.
- Se non è configurato alcun completamento, doctor propone di installarlo
  (solo modalità interattiva; saltato con `--non-interactive`).

Esegui `openclaw completion --write-state` per rigenerare manualmente la cache.

### 12) Controlli auth del gateway (token locale)

Doctor controlla la disponibilità dell'autenticazione token del gateway locale.

- Se la modalità token richiede un token e non esiste alcuna sorgente token, doctor offre di generarne uno.
- Se `gateway.auth.token` è gestito da SecretRef ma non disponibile, doctor avvisa e non lo sovrascrive con testo in chiaro.
- `openclaw doctor --generate-gateway-token` forza la generazione solo quando non è configurato alcun token SecretRef.

### 12b) Riparazioni in sola lettura con riconoscimento di SecretRef

Alcuni flussi di riparazione devono ispezionare le credenziali configurate senza indebolire il comportamento fail-fast del runtime.

- `openclaw doctor --fix` ora usa lo stesso modello di riepilogo SecretRef in sola lettura dei comandi della famiglia status per riparazioni mirate della configurazione.
- Esempio: la riparazione `@username` di Telegram `allowFrom` / `groupAllowFrom` prova a usare le credenziali bot configurate quando disponibili.
- Se il token del bot Telegram è configurato tramite SecretRef ma non disponibile nel percorso del comando corrente, doctor segnala che la credenziale è configurata-ma-non-disponibile e salta la risoluzione automatica invece di bloccarsi o segnalare erroneamente il token come mancante.

### 13) Controllo integrità del gateway + riavvio

Doctor esegue un controllo di integrità e propone di riavviare il gateway quando sembra
non integro.

### 13b) Disponibilità della ricerca in memoria

Doctor controlla se il provider di embedding per la ricerca in memoria configurato è pronto
per l'agente predefinito. Il comportamento dipende dal backend e dal provider configurati:

- **Backend QMD**: verifica se il binario `qmd` è disponibile e avviabile.
  In caso contrario, stampa indicazioni di correzione incluse il pacchetto npm e un'opzione manuale per il percorso del binario.
- **Provider locale esplicito**: controlla la presenza di un file modello locale o di un URL modello remoto/scaricabile
  riconosciuto. Se manca, suggerisce di passare a un provider remoto.
- **Provider remoto esplicito** (`openai`, `voyage`, ecc.): verifica che una chiave API sia
  presente nell'ambiente o nell'archivio auth. Stampa suggerimenti di correzione concreti se manca.
- **Provider automatico**: controlla prima la disponibilità del modello locale, poi prova ogni provider remoto
  nell'ordine di selezione automatica.

Quando è disponibile un risultato di sonda del gateway (il gateway era integro al momento del
controllo), doctor confronta il risultato con la configurazione visibile dalla CLI e annota
qualsiasi discrepanza.

Usa `openclaw memory status --deep` per verificare la disponibilità degli embedding a runtime.

### 14) Avvisi sullo stato dei canali

Se il gateway è integro, doctor esegue una sonda sullo stato dei canali e segnala
gli avvisi con le correzioni suggerite.

### 15) Audit + riparazione della configurazione supervisor

Doctor controlla la configurazione supervisor installata (launchd/systemd/schtasks) per
valori predefiniti mancanti o obsoleti (ad es. dipendenze systemd da network-online e
ritardo di riavvio). Quando trova una mancata corrispondenza, consiglia un aggiornamento e può
riscrivere il file di servizio/task ai valori predefiniti correnti.

Note:

- `openclaw doctor` chiede conferma prima di riscrivere la configurazione supervisor.
- `openclaw doctor --yes` accetta i prompt di riparazione predefiniti.
- `openclaw doctor --repair` applica le correzioni consigliate senza prompt.
- `openclaw doctor --repair --force` sovrascrive configurazioni supervisor personalizzate.
- Se l'autenticazione token richiede un token e `gateway.auth.token` è gestito da SecretRef, il percorso di installazione/riparazione del servizio doctor convalida il SecretRef ma non rende persistenti valori token in chiaro risolti nei metadati dell'ambiente del servizio supervisor.
- Se l'autenticazione token richiede un token e il token SecretRef configurato non è risolto, doctor blocca il percorso di installazione/riparazione con indicazioni operative.
- Se sia `gateway.auth.token` sia `gateway.auth.password` sono configurati e `gateway.auth.mode` non è impostato, doctor blocca installazione/riparazione finché la modalità non viene impostata esplicitamente.
- Per le unità Linux user-systemd, i controlli di deriva del token doctor ora includono sia le sorgenti `Environment=` sia `EnvironmentFile=` quando confrontano i metadati auth del servizio.
- Puoi sempre forzare una riscrittura completa tramite `openclaw gateway install --force`.

### 16) Diagnostica runtime + porta del gateway

Doctor ispeziona il runtime del servizio (PID, ultimo stato di uscita) e avvisa quando il
servizio è installato ma non è effettivamente in esecuzione. Controlla anche le collisioni di porta
sulla porta del gateway (predefinita `18789`) e riporta le cause probabili (gateway già
in esecuzione, tunnel SSH).

### 17) Best practice del runtime del gateway

Doctor avvisa quando il servizio gateway viene eseguito con Bun o con un percorso Node gestito da un version manager
(`nvm`, `fnm`, `volta`, `asdf`, ecc.). I canali WhatsApp + Telegram richiedono Node,
e i percorsi dei version manager possono interrompersi dopo gli aggiornamenti perché il servizio non
carica l'inizializzazione della tua shell. Doctor propone di migrare a un'installazione Node di sistema quando
disponibile (Homebrew/apt/choco).

### 18) Scrittura della configurazione + metadati del wizard

Doctor rende persistenti tutte le modifiche alla configurazione e registra i metadati del wizard per annotare l'esecuzione
di doctor.

### 19) Suggerimenti per il workspace (backup + sistema di memoria)

Doctor suggerisce un sistema di memoria del workspace quando manca e stampa un suggerimento di backup
se il workspace non è già sotto git.

Vedi [/concepts/agent-workspace](/it/concepts/agent-workspace) per una guida completa alla
struttura del workspace e al backup git (consigliato GitHub o GitLab privato).
