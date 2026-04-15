---
read_when:
    - Ricerca di un passaggio o di una flag di onboarding specifici
    - Automatizzare l'onboarding con la modalità non interattiva
    - Debug del comportamento di onboarding
sidebarTitle: Onboarding Reference
summary: 'Riferimento completo per l''onboarding della CLI: ogni passaggio, flag e campo di configurazione'
title: Riferimento per l'onboarding
x-i18n:
    generated_at: "2026-04-15T14:40:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1db3ff789422617634e6624f9d12c18b6a6c573721226b9c0fa6f6b7956ef33d
    source_path: reference/wizard.md
    workflow: 15
---

# Riferimento per l'onboarding

Questo è il riferimento completo per `openclaw onboard`.
Per una panoramica di alto livello, vedi [Onboarding (CLI)](/it/start/wizard).

## Dettagli del flusso (modalità locale)

<Steps>
  <Step title="Rilevamento della configurazione esistente">
    - Se `~/.openclaw/openclaw.json` esiste, scegli **Mantieni / Modifica / Reimposta**.
    - Eseguire di nuovo l'onboarding **non** cancella nulla a meno che tu non scelga esplicitamente **Reimposta**
      (o passi `--reset`).
    - L'opzione CLI `--reset` usa per impostazione predefinita `config+creds+sessions`; usa `--reset-scope full`
      per rimuovere anche il workspace.
    - Se la configurazione non è valida o contiene chiavi legacy, la procedura guidata si interrompe e ti chiede
      di eseguire `openclaw doctor` prima di continuare.
    - La reimpostazione usa `trash` (mai `rm`) e offre questi ambiti:
      - Solo configurazione
      - Configurazione + credenziali + sessioni
      - Reimpostazione completa (rimuove anche il workspace)
  </Step>
  <Step title="Modello/Autenticazione">
    - **Chiave API Anthropic**: usa `ANTHROPIC_API_KEY` se presente oppure richiede una chiave, quindi la salva per l'uso del daemon.
    - **Chiave API Anthropic**: scelta preferita dell'assistente Anthropic in onboarding/configurazione.
    - **Setup-token Anthropic**: ancora disponibile in onboarding/configurazione, anche se OpenClaw ora preferisce il riutilizzo della CLI Claude quando disponibile.
    - **Abbonamento OpenAI Code (Codex) (Codex CLI)**: se `~/.codex/auth.json` esiste, l'onboarding può riutilizzarlo. Le credenziali Codex CLI riutilizzate restano gestite da Codex CLI; alla scadenza OpenClaw rilegge prima quella fonte e, quando il provider può aggiornarla, scrive di nuovo la credenziale aggiornata nello storage di Codex invece di assumerne direttamente la gestione.
    - **Abbonamento OpenAI Code (Codex) (OAuth)**: flusso via browser; incolla `code#state`.
      - Imposta `agents.defaults.model` su `openai-codex/gpt-5.4` quando il modello non è impostato o è `openai/*`.
    - **Chiave API OpenAI**: usa `OPENAI_API_KEY` se presente oppure richiede una chiave, quindi la memorizza nei profili di autenticazione.
      - Imposta `agents.defaults.model` su `openai/gpt-5.4` quando il modello non è impostato, è `openai/*` oppure `openai-codex/*`.
    - **Chiave API xAI (Grok)**: richiede `XAI_API_KEY` e configura xAI come provider di modelli.
    - **OpenCode**: richiede `OPENCODE_API_KEY` (oppure `OPENCODE_ZEN_API_KEY`, ottienila su https://opencode.ai/auth) e ti consente di scegliere il catalogo Zen o Go.
    - **Ollama**: propone prima **Cloud + Local**, **Solo cloud** oppure **Solo locale**. `Solo cloud` richiede `OLLAMA_API_KEY` e usa `https://ollama.com`; le modalità con host richiedono l'URL di base di Ollama, rilevano i modelli disponibili e scaricano automaticamente il modello locale selezionato quando necessario; `Cloud + Local` controlla anche se quell'host Ollama ha effettuato l'accesso per l'accesso cloud.
    - Maggiori dettagli: [Ollama](/it/providers/ollama)
    - **Chiave API**: memorizza la chiave per te.
    - **Vercel AI Gateway (proxy multi-modello)**: richiede `AI_GATEWAY_API_KEY`.
    - Maggiori dettagli: [Vercel AI Gateway](/it/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: richiede Account ID, Gateway ID e `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    - Maggiori dettagli: [Cloudflare AI Gateway](/it/providers/cloudflare-ai-gateway)
    - **MiniMax**: la configurazione viene scritta automaticamente; il valore predefinito ospitato è `MiniMax-M2.7`.
      La configurazione con chiave API usa `minimax/...`, mentre la configurazione OAuth usa
      `minimax-portal/...`.
    - Maggiori dettagli: [MiniMax](/it/providers/minimax)
    - **StepFun**: la configurazione viene scritta automaticamente per StepFun standard o Step Plan su endpoint Cina o globali.
    - Standard include attualmente `step-3.5-flash`, e Step Plan include anche `step-3.5-flash-2603`.
    - Maggiori dettagli: [StepFun](/it/providers/stepfun)
    - **Synthetic (compatibile con Anthropic)**: richiede `SYNTHETIC_API_KEY`.
    - Maggiori dettagli: [Synthetic](/it/providers/synthetic)
    - **Moonshot (Kimi K2)**: la configurazione viene scritta automaticamente.
    - **Kimi Coding**: la configurazione viene scritta automaticamente.
    - Maggiori dettagli: [Moonshot AI (Kimi + Kimi Coding)](/it/providers/moonshot)
    - **Salta**: nessuna autenticazione configurata al momento.
    - Scegli un modello predefinito tra le opzioni rilevate (oppure inserisci manualmente provider/modello). Per la migliore qualità e un rischio inferiore di prompt injection, scegli il modello più forte e di ultima generazione disponibile nel tuo stack di provider.
    - L'onboarding esegue un controllo del modello e avvisa se il modello configurato è sconosciuto o se manca l'autenticazione.
    - La modalità di archiviazione della chiave API usa per impostazione predefinita valori in chiaro nei profili di autenticazione. Usa `--secret-input-mode ref` per memorizzare invece riferimenti basati su variabili di ambiente (ad esempio `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - I profili di autenticazione si trovano in `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (chiavi API + OAuth). `~/.openclaw/credentials/oauth.json` è legacy e serve solo per l'importazione.
    - Maggiori dettagli: [/concepts/oauth](/it/concepts/oauth)
    <Note>
    Suggerimento per headless/server: completa OAuth su una macchina con browser, poi copia
    `auth-profiles.json` di quell'agente (ad esempio
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`, oppure il percorso
    corrispondente `$OPENCLAW_STATE_DIR/...`) sull'host del gateway. `credentials/oauth.json`
    è solo una fonte legacy per l'importazione.
    </Note>
  </Step>
  <Step title="Workspace">
    - Valore predefinito `~/.openclaw/workspace` (configurabile).
    - Inizializza i file del workspace necessari per il rituale bootstrap dell'agente.
    - Layout completo del workspace + guida al backup: [Workspace dell'agente](/it/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - Porta, bind, modalità di autenticazione, esposizione Tailscale.
    - Raccomandazione per l'autenticazione: mantieni **Token** anche per loopback, così i client WS locali devono autenticarsi.
    - In modalità token, la configurazione interattiva offre:
      - **Genera/memorizza token in chiaro** (predefinito)
      - **Usa SecretRef** (facoltativo)
      - Quickstart riutilizza i SecretRef esistenti di `gateway.auth.token` nei provider `env`, `file` ed `exec` per la probe/dashboard bootstrap dell'onboarding.
      - Se quel SecretRef è configurato ma non può essere risolto, l'onboarding fallisce subito con un chiaro messaggio di correzione invece di degradare silenziosamente l'autenticazione a runtime.
    - In modalità password, la configurazione interattiva supporta anch'essa l'archiviazione in chiaro o SecretRef.
    - Percorso SecretRef del token non interattivo: `--gateway-token-ref-env <ENV_VAR>`.
      - Richiede una variabile di ambiente non vuota nell'ambiente del processo di onboarding.
      - Non può essere combinato con `--gateway-token`.
    - Disabilita l'autenticazione solo se ti fidi completamente di ogni processo locale.
    - I bind non loopback richiedono comunque l'autenticazione.
  </Step>
  <Step title="Canali">
    - [WhatsApp](/it/channels/whatsapp): accesso QR facoltativo.
    - [Telegram](/it/channels/telegram): token del bot.
    - [Discord](/it/channels/discord): token del bot.
    - [Google Chat](/it/channels/googlechat): JSON dell'account di servizio + audience del Webhook.
    - [Mattermost](/it/channels/mattermost) (Plugin): token del bot + URL di base.
    - [Signal](/it/channels/signal): installazione facoltativa di `signal-cli` + configurazione dell'account.
    - [BlueBubbles](/it/channels/bluebubbles): **consigliato per iMessage**; URL del server + password + Webhook.
    - [iMessage](/it/channels/imessage): percorso della CLI `imsg` legacy + accesso DB.
    - Sicurezza dei DM: il valore predefinito è l'abbinamento. Il primo DM invia un codice; approvalo con `openclaw pairing approve <channel> <code>` oppure usa allowlist.
  </Step>
  <Step title="Ricerca web">
    - Scegli un provider supportato come Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG o Tavily (oppure salta).
    - I provider basati su API possono usare variabili di ambiente o configurazione esistente per una configurazione rapida; i provider senza chiave usano invece i prerequisiti specifici del provider.
    - Salta con `--skip-search`.
    - Configura in seguito: `openclaw configure --section web`.
  </Step>
  <Step title="Installazione del daemon">
    - macOS: LaunchAgent
      - Richiede una sessione utente con accesso effettuato; per ambienti headless, usa un LaunchDaemon personalizzato (non fornito).
    - Linux (e Windows tramite WSL2): unità utente systemd
      - L'onboarding tenta di abilitare lingering tramite `loginctl enable-linger <user>` in modo che il Gateway resti attivo dopo il logout.
      - Può richiedere sudo (scrive in `/var/lib/systemd/linger`); prima prova senza sudo.
    - **Selezione del runtime:** Node (consigliato; richiesto per WhatsApp/Telegram). Bun **non è consigliato**.
    - Se l'autenticazione token richiede un token e `gateway.auth.token` è gestito da SecretRef, l'installazione del daemon lo convalida ma non persiste i valori del token in chiaro risolti nei metadati dell'ambiente del servizio supervisor.
    - Se l'autenticazione token richiede un token e il SecretRef del token configurato non è risolto, l'installazione del daemon viene bloccata con indicazioni operative.
    - Se sia `gateway.auth.token` sia `gateway.auth.password` sono configurati e `gateway.auth.mode` non è impostato, l'installazione del daemon viene bloccata finché la modalità non viene impostata esplicitamente.
  </Step>
  <Step title="Controllo integrità">
    - Avvia il Gateway (se necessario) ed esegue `openclaw health`.
    - Suggerimento: `openclaw status --deep` aggiunge l'health probe del gateway live all'output di stato, comprese le probe dei canali quando supportate (richiede un gateway raggiungibile).
  </Step>
  <Step title="Skills (consigliato)">
    - Legge le Skills disponibili e controlla i requisiti.
    - Ti consente di scegliere un gestore Node: **npm / pnpm** (bun non consigliato).
    - Installa dipendenze facoltative (alcune usano Homebrew su macOS).
  </Step>
  <Step title="Fine">
    - Riepilogo + passaggi successivi, incluse le app iOS/Android/macOS per funzionalità aggiuntive.
  </Step>
</Steps>

<Note>
Se non viene rilevata alcuna GUI, l'onboarding stampa le istruzioni per il port-forward SSH della Control UI invece di aprire un browser.
Se mancano le risorse della Control UI, l'onboarding tenta di compilarle; il fallback è `pnpm ui:build` (installa automaticamente le dipendenze della UI).
</Note>

## Modalità non interattiva

Usa `--non-interactive` per automatizzare o creare script per l'onboarding:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

Aggiungi `--json` per un riepilogo leggibile da una macchina.

SecretRef del token Gateway in modalità non interattiva:

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token` e `--gateway-token-ref-env` si escludono a vicenda.

<Note>
`--json` **non** implica la modalità non interattiva. Usa `--non-interactive` (e `--workspace`) per gli script.
</Note>

Esempi di comandi specifici per provider si trovano in [Automazione CLI](/it/start/wizard-cli-automation#provider-specific-examples).
Usa questa pagina di riferimento per la semantica delle flag e l'ordine dei passaggi.

### Aggiungere un agente (non interattivo)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## RPC della procedura guidata Gateway

Il Gateway espone il flusso di onboarding tramite RPC (`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`).
I client (app macOS, Control UI) possono visualizzare i passaggi senza reimplementare la logica di onboarding.

## Configurazione di Signal (signal-cli)

L'onboarding può installare `signal-cli` dalle release GitHub:

- Scarica l'asset di release appropriato.
- Lo archivia in `~/.openclaw/tools/signal-cli/<version>/`.
- Scrive `channels.signal.cliPath` nella tua configurazione.

Note:

- Le build JVM richiedono **Java 21**.
- Le build native vengono usate quando disponibili.
- Windows usa WSL2; l'installazione di signal-cli segue il flusso Linux all'interno di WSL.

## Cosa scrive la procedura guidata

Campi tipici in `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (se viene scelto Minimax)
- `tools.profile` (l'onboarding locale usa per impostazione predefinita `"coding"` se non impostato; i valori espliciti esistenti vengono mantenuti)
- `gateway.*` (modalità, bind, autenticazione, Tailscale)
- `session.dmScope` (dettagli sul comportamento: [Riferimento configurazione CLI](/it/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Allowlist dei canali (Slack/Discord/Matrix/Microsoft Teams) quando scegli questa opzione durante i prompt (i nomi vengono risolti in ID quando possibile).
- `skills.install.nodeManager`
  - `setup --node-manager` accetta `npm`, `pnpm` o `bun`.
  - La configurazione manuale può ancora usare `yarn` impostando direttamente `skills.install.nodeManager`.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` scrive `agents.list[]` e `bindings` facoltativi.

Le credenziali WhatsApp vengono salvate in `~/.openclaw/credentials/whatsapp/<accountId>/`.
Le sessioni vengono archiviate in `~/.openclaw/agents/<agentId>/sessions/`.

Alcuni canali vengono distribuiti come Plugin. Quando ne scegli uno durante la configurazione, l'onboarding
ti chiederà di installarlo (npm o un percorso locale) prima che possa essere configurato.

## Documentazione correlata

- Panoramica dell'onboarding: [Onboarding (CLI)](/it/start/wizard)
- Onboarding dell'app macOS: [Onboarding](/it/start/onboarding)
- Riferimento configurazione: [Configurazione del Gateway](/it/gateway/configuration)
- Provider: [WhatsApp](/it/channels/whatsapp), [Telegram](/it/channels/telegram), [Discord](/it/channels/discord), [Google Chat](/it/channels/googlechat), [Signal](/it/channels/signal), [BlueBubbles](/it/channels/bluebubbles) (iMessage), [iMessage](/it/channels/imessage) (legacy)
- Skills: [Skills](/it/tools/skills), [Configurazione Skills](/it/tools/skills-config)
