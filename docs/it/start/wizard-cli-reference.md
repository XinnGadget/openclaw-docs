---
read_when:
    - Hai bisogno di informazioni dettagliate sul comportamento di `openclaw onboard`
    - Stai eseguendo il debug dei risultati di onboarding o stai integrando client di onboarding
sidebarTitle: CLI reference
summary: Riferimento completo per il flusso di configurazione della CLI, la configurazione di autenticazione/modello, gli output e gli aspetti interni
title: Riferimento per la configurazione della CLI
x-i18n:
    generated_at: "2026-04-15T14:41:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 61ca679caca3b43fa02388294007f89db22d343e49e10b61d8d118cd8fbb7369
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# Riferimento per la configurazione della CLI

Questa pagina è il riferimento completo per `openclaw onboard`.
Per la guida breve, vedi [Onboarding (CLI)](/it/start/wizard).

## Cosa fa la procedura guidata

La modalità locale (predefinita) ti guida attraverso:

- Configurazione del modello e dell'autenticazione (OAuth dell'abbonamento OpenAI Code, Anthropic Claude CLI o chiave API, oltre a opzioni MiniMax, GLM, Ollama, Moonshot, StepFun e AI Gateway)
- Posizione del workspace e file di bootstrap
- Impostazioni del Gateway (porta, bind, auth, tailscale)
- Canali e provider (Telegram, WhatsApp, Discord, Google Chat, Mattermost, Signal, BlueBubbles e altri plugin di canale inclusi)
- Installazione del daemon (LaunchAgent, unità utente systemd o attività pianificata nativa di Windows con fallback nella cartella Startup)
- Controllo dello stato di salute
- Configurazione di Skills

La modalità remota configura questa macchina per connettersi a un Gateway altrove.
Non installa né modifica nulla sull'host remoto.

## Dettagli del flusso locale

<Steps>
  <Step title="Rilevamento della configurazione esistente">
    - Se esiste `~/.openclaw/openclaw.json`, scegli Mantieni, Modifica o Reimposta.
    - Eseguire di nuovo la procedura guidata non cancella nulla a meno che tu non scelga esplicitamente Reimposta (o passi `--reset`).
    - La CLI `--reset` usa come predefinito `config+creds+sessions`; usa `--reset-scope full` per rimuovere anche il workspace.
    - Se la configurazione non è valida o contiene chiavi legacy, la procedura guidata si interrompe e ti chiede di eseguire `openclaw doctor` prima di continuare.
    - Reimposta usa `trash` e offre questi ambiti:
      - Solo configurazione
      - Configurazione + credenziali + sessioni
      - Reimpostazione completa (rimuove anche il workspace)
  </Step>
  <Step title="Modello e autenticazione">
    - La matrice completa delle opzioni è in [Opzioni di autenticazione e modello](#auth-and-model-options).
  </Step>
  <Step title="Workspace">
    - Predefinito `~/.openclaw/workspace` (configurabile).
    - Inizializza i file del workspace necessari per il rituale di bootstrap della prima esecuzione.
    - Layout del workspace: [Workspace dell'agente](/it/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Chiede porta, bind, modalità auth ed esposizione Tailscale.
    - Consigliato: mantieni abilitata l'autenticazione tramite token anche per loopback, così i client WS locali devono autenticarsi.
    - In modalità token, la configurazione interattiva offre:
      - **Genera/memorizza token in chiaro** (predefinito)
      - **Usa SecretRef** (opt-in)
    - In modalità password, la configurazione interattiva supporta anche la memorizzazione in chiaro o con SecretRef.
    - Percorso SecretRef del token non interattivo: `--gateway-token-ref-env <ENV_VAR>`.
      - Richiede una variabile d'ambiente non vuota nell'ambiente del processo di onboarding.
      - Non può essere combinato con `--gateway-token`.
    - Disabilita l'autenticazione solo se ti fidi completamente di ogni processo locale.
    - I bind non-loopback richiedono comunque l'autenticazione.
  </Step>
  <Step title="Canali">
    - [WhatsApp](/it/channels/whatsapp): accesso QR opzionale
    - [Telegram](/it/channels/telegram): token del bot
    - [Discord](/it/channels/discord): token del bot
    - [Google Chat](/it/channels/googlechat): JSON dell'account di servizio + audience del webhook
    - [Mattermost](/it/channels/mattermost): token del bot + URL di base
    - [Signal](/it/channels/signal): installazione opzionale di `signal-cli` + configurazione dell'account
    - [BlueBubbles](/it/channels/bluebubbles): consigliato per iMessage; URL del server + password + webhook
    - [iMessage](/it/channels/imessage): percorso legacy della CLI `imsg` + accesso al DB
    - Sicurezza dei DM: il predefinito è l'abbinamento. Il primo DM invia un codice; approvalo tramite
      `openclaw pairing approve <channel> <code>` oppure usa allowlist.
  </Step>
  <Step title="Installazione del daemon">
    - macOS: LaunchAgent
      - Richiede una sessione utente con accesso effettuato; per ambienti headless usa un LaunchDaemon personalizzato (non incluso).
    - Linux e Windows tramite WSL2: unità utente systemd
      - La procedura guidata tenta `loginctl enable-linger <user>` così il Gateway resta attivo dopo il logout.
      - Potrebbe richiedere sudo (scrive in `/var/lib/systemd/linger`); prova prima senza sudo.
    - Windows nativo: prima attività pianificata
      - Se la creazione dell'attività viene negata, OpenClaw ripiega su un elemento di accesso nella cartella Startup per utente e avvia immediatamente il Gateway.
      - Le attività pianificate restano preferibili perché forniscono uno stato del supervisore migliore.
    - Selezione del runtime: Node (consigliato; richiesto per WhatsApp e Telegram). Bun non è consigliato.
  </Step>
  <Step title="Controllo dello stato di salute">
    - Avvia il Gateway (se necessario) ed esegue `openclaw health`.
    - `openclaw status --deep` aggiunge il probe di stato di salute del Gateway attivo all'output di stato, inclusi i probe dei canali quando supportati.
  </Step>
  <Step title="Skills">
    - Legge le Skills disponibili e verifica i requisiti.
    - Ti permette di scegliere il gestore Node: npm, pnpm o bun.
    - Installa dipendenze opzionali (alcune usano Homebrew su macOS).
  </Step>
  <Step title="Fine">
    - Riepilogo e passaggi successivi, incluse le opzioni app per iOS, Android e macOS.
  </Step>
</Steps>

<Note>
Se non viene rilevata alcuna GUI, la procedura guidata stampa le istruzioni di port forwarding SSH per la UI di controllo invece di aprire un browser.
Se mancano le risorse della UI di controllo, la procedura guidata tenta di compilarle; il fallback è `pnpm ui:build` (installa automaticamente le dipendenze della UI).
</Note>

## Dettagli della modalità remota

La modalità remota configura questa macchina per connettersi a un Gateway altrove.

<Info>
La modalità remota non installa né modifica nulla sull'host remoto.
</Info>

Cosa imposti:

- URL del Gateway remoto (`ws://...`)
- Token se è richiesta l'autenticazione del Gateway remoto (consigliato)

<Note>
- Se il Gateway è solo loopback, usa tunneling SSH o una tailnet.
- Suggerimenti per il rilevamento:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## Opzioni di autenticazione e modello

<AccordionGroup>
  <Accordion title="Chiave API Anthropic">
    Usa `ANTHROPIC_API_KEY` se presente oppure richiede una chiave, quindi la salva per l'uso del daemon.
  </Accordion>
  <Accordion title="Abbonamento OpenAI Code (riuso di Codex CLI)">
    Se esiste `~/.codex/auth.json`, la procedura guidata può riutilizzarlo.
    Le credenziali di Codex CLI riutilizzate restano gestite da Codex CLI; alla scadenza OpenClaw
    rilegge prima quella sorgente e, quando il provider può aggiornarle, scrive
    la credenziale aggiornata di nuovo nell'archivio di Codex invece di assumerne direttamente
    la gestione.
  </Accordion>
  <Accordion title="Abbonamento OpenAI Code (OAuth)">
    Flusso nel browser; incolla `code#state`.

    Imposta `agents.defaults.model` su `openai-codex/gpt-5.4` quando il modello non è impostato oppure è `openai/*`.

  </Accordion>
  <Accordion title="Chiave API OpenAI">
    Usa `OPENAI_API_KEY` se presente oppure richiede una chiave, quindi memorizza la credenziale nei profili auth.

    Imposta `agents.defaults.model` su `openai/gpt-5.4` quando il modello non è impostato, è `openai/*` oppure `openai-codex/*`.

  </Accordion>
  <Accordion title="Chiave API xAI (Grok)">
    Richiede `XAI_API_KEY` e configura xAI come provider di modelli.
  </Accordion>
  <Accordion title="OpenCode">
    Richiede `OPENCODE_API_KEY` (oppure `OPENCODE_ZEN_API_KEY`) e ti consente di scegliere il catalogo Zen o Go.
    URL di configurazione: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="Chiave API (generica)">
    Memorizza la chiave per te.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    Richiede `AI_GATEWAY_API_KEY`.
    Maggiori dettagli: [Vercel AI Gateway](/it/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    Richiede account ID, gateway ID e `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    Maggiori dettagli: [Cloudflare AI Gateway](/it/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax">
    La configurazione viene scritta automaticamente. L'hosted predefinito è `MiniMax-M2.7`; la configurazione con chiave API usa
    `minimax/...`, mentre la configurazione OAuth usa `minimax-portal/...`.
    Maggiori dettagli: [MiniMax](/it/providers/minimax).
  </Accordion>
  <Accordion title="StepFun">
    La configurazione viene scritta automaticamente per StepFun standard o Step Plan su endpoint China o global.
    Standard include attualmente `step-3.5-flash`, e Step Plan include anche `step-3.5-flash-2603`.
    Maggiori dettagli: [StepFun](/it/providers/stepfun).
  </Accordion>
  <Accordion title="Synthetic (compatibile con Anthropic)">
    Richiede `SYNTHETIC_API_KEY`.
    Maggiori dettagli: [Synthetic](/it/providers/synthetic).
  </Accordion>
  <Accordion title="Ollama (Cloud e modelli aperti locali)">
    Richiede prima `Cloud + Local`, `Solo Cloud` oppure `Solo Local`.
    `Solo Cloud` usa `OLLAMA_API_KEY` con `https://ollama.com`.
    Le modalità basate su host richiedono l'URL di base (predefinito `http://127.0.0.1:11434`), rilevano i modelli disponibili e suggeriscono i predefiniti.
    `Cloud + Local` controlla anche se quell'host Ollama ha effettuato l'accesso per l'accesso cloud.
    Maggiori dettagli: [Ollama](/it/providers/ollama).
  </Accordion>
  <Accordion title="Moonshot e Kimi Coding">
    Le configurazioni Moonshot (Kimi K2) e Kimi Coding vengono scritte automaticamente.
    Maggiori dettagli: [Moonshot AI (Kimi + Kimi Coding)](/it/providers/moonshot).
  </Accordion>
  <Accordion title="Provider personalizzato">
    Funziona con endpoint compatibili con OpenAI e compatibili con Anthropic.

    L'onboarding interattivo supporta le stesse scelte di memorizzazione della chiave API degli altri flussi con chiave API del provider:
    - **Incolla ora la chiave API** (in chiaro)
    - **Usa riferimento segreto** (riferimento env o riferimento del provider configurato, con validazione preliminare)

    Flag non interattivi:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key` (opzionale; usa come fallback `CUSTOM_API_KEY`)
    - `--custom-provider-id` (opzionale)
    - `--custom-compatibility <openai|anthropic>` (opzionale; predefinito `openai`)

  </Accordion>
  <Accordion title="Salta">
    Lascia l'autenticazione non configurata.
  </Accordion>
</AccordionGroup>

Comportamento del modello:

- Scegli il modello predefinito dalle opzioni rilevate, oppure inserisci manualmente provider e modello.
- Quando l'onboarding inizia da una scelta di autenticazione del provider, il selettore del modello preferisce
  automaticamente quel provider. Per Volcengine e BytePlus, la stessa preferenza
  corrisponde anche alle loro varianti coding-plan (`volcengine-plan/*`,
  `byteplus-plan/*`).
- Se quel filtro del provider preferito sarebbe vuoto, il selettore torna al
  catalogo completo invece di non mostrare alcun modello.
- La procedura guidata esegue un controllo del modello e avvisa se il modello configurato è sconosciuto o manca l'autenticazione.

Percorsi di credenziali e profili:

- Profili auth (chiavi API + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Importazione OAuth legacy: `~/.openclaw/credentials/oauth.json`

Modalità di memorizzazione delle credenziali:

- Il comportamento predefinito dell'onboarding salva le chiavi API come valori in chiaro nei profili auth.
- `--secret-input-mode ref` abilita la modalità riferimento invece della memorizzazione della chiave in chiaro.
  Nella configurazione interattiva, puoi scegliere:
  - riferimento a variabile d'ambiente (ad esempio `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`)
  - riferimento a provider configurato (`file` o `exec`) con alias del provider + id
- La modalità riferimento interattiva esegue una rapida validazione preliminare prima del salvataggio.
  - Riferimenti env: valida il nome della variabile e il valore non vuoto nell'ambiente di onboarding corrente.
  - Riferimenti provider: valida la configurazione del provider e risolve l'id richiesto.
  - Se la validazione preliminare fallisce, l'onboarding mostra l'errore e ti consente di riprovare.
- In modalità non interattiva, `--secret-input-mode ref` è supportato solo tramite env.
  - Imposta la variabile d'ambiente del provider nell'ambiente del processo di onboarding.
  - I flag con chiave inline (ad esempio `--openai-api-key`) richiedono che quella variabile env sia impostata; altrimenti l'onboarding fallisce rapidamente.
  - Per i provider personalizzati, la modalità `ref` non interattiva salva `models.providers.<id>.apiKey` come `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`.
  - In quel caso del provider personalizzato, `--custom-api-key` richiede che `CUSTOM_API_KEY` sia impostato; altrimenti l'onboarding fallisce rapidamente.
- Le credenziali auth del Gateway supportano la scelta tra testo in chiaro e SecretRef nella configurazione interattiva:
  - Modalità token: **Genera/memorizza token in chiaro** (predefinito) oppure **Usa SecretRef**.
  - Modalità password: testo in chiaro oppure SecretRef.
- Percorso SecretRef del token non interattivo: `--gateway-token-ref-env <ENV_VAR>`.
- Le configurazioni esistenti in chiaro continuano a funzionare senza modifiche.

<Note>
Suggerimento per ambienti headless e server: completa l'OAuth su una macchina con browser, poi copia
l'`auth-profiles.json` di quell'agente (ad esempio
`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`, oppure il percorso corrispondente
`$OPENCLAW_STATE_DIR/...`) sull'host del Gateway. `credentials/oauth.json`
è solo una sorgente di importazione legacy.
</Note>

## Output e aspetti interni

Campi tipici in `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (se viene scelto MiniMax)
- `tools.profile` (l'onboarding locale usa come predefinito `"coding"` se non impostato; i valori espliciti esistenti vengono preservati)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (l'onboarding locale usa come predefinito `per-channel-peer` se non impostato; i valori espliciti esistenti vengono preservati)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Allowlist dei canali (Slack, Discord, Matrix, Microsoft Teams) quando scegli di abilitarle durante i prompt (i nomi vengono risolti in ID quando possibile)
- `skills.install.nodeManager`
  - Il flag `setup --node-manager` accetta `npm`, `pnpm` o `bun`.
  - La configurazione manuale può comunque impostare successivamente `skills.install.nodeManager: "yarn"`.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` scrive `agents.list[]` e `bindings` opzionali.

Le credenziali di WhatsApp vengono salvate in `~/.openclaw/credentials/whatsapp/<accountId>/`.
Le sessioni vengono archiviate in `~/.openclaw/agents/<agentId>/sessions/`.

<Note>
Alcuni canali sono distribuiti come plugin. Quando vengono selezionati durante la configurazione, la procedura guidata
chiede di installare il Plugin (npm o percorso locale) prima della configurazione del canale.
</Note>

RPC della procedura guidata del Gateway:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

I client (app macOS e UI di controllo) possono eseguire il rendering dei passaggi senza reimplementare la logica di onboarding.

Comportamento della configurazione di Signal:

- Scarica l'asset di rilascio appropriato
- Lo salva in `~/.openclaw/tools/signal-cli/<version>/`
- Scrive `channels.signal.cliPath` nella configurazione
- Le build JVM richiedono Java 21
- Le build native vengono usate quando disponibili
- Windows usa WSL2 e segue il flusso Linux di signal-cli all'interno di WSL

## Documentazione correlata

- Hub di onboarding: [Onboarding (CLI)](/it/start/wizard)
- Automazione e script: [Automazione CLI](/it/start/wizard-cli-automation)
- Riferimento dei comandi: [`openclaw onboard`](/cli/onboard)
