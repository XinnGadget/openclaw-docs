---
read_when:
    - OpenClaw non funziona e hai bisogno del percorso più rapido per una soluzione
    - Vuoi un flusso di triage prima di approfondire con runbook dettagliati
summary: Hub di risoluzione dei problemi di OpenClaw orientato ai sintomi
title: Risoluzione generale dei problemi
x-i18n:
    generated_at: "2026-04-11T02:45:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 16b38920dbfdc8d4a79bbb5d6fab2c67c9f218a97c36bb4695310d7db9c4614a
    source_path: help/troubleshooting.md
    workflow: 15
---

# Risoluzione dei problemi

Se hai solo 2 minuti, usa questa pagina come punto di ingresso per il triage.

## Primi 60 secondi

Esegui esattamente questa sequenza nell'ordine indicato:

```bash
openclaw status
openclaw status --all
openclaw gateway probe
openclaw gateway status
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```

Output corretto in una riga:

- `openclaw status` → mostra i canali configurati e nessun errore auth evidente.
- `openclaw status --all` → il report completo è presente e condivisibile.
- `openclaw gateway probe` → la destinazione gateway prevista è raggiungibile (`Reachable: yes`). `RPC: limited - missing scope: operator.read` indica diagnostica degradata, non un errore di connessione.
- `openclaw gateway status` → `Runtime: running` e `RPC probe: ok`.
- `openclaw doctor` → nessun errore bloccante di configurazione/servizio.
- `openclaw channels status --probe` → se il gateway è raggiungibile, restituisce lo stato di trasporto live per account più i risultati di probe/audit come `works` o `audit ok`; se il gateway non è raggiungibile, il comando torna a riepiloghi basati solo sulla configurazione.
- `openclaw logs --follow` → attività costante, nessun errore fatale ripetuto.

## Anthropic long context 429

Se vedi:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`,
vai a [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/it/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

## Il backend locale compatibile con OpenAI funziona direttamente ma fallisce in OpenClaw

Se il tuo backend locale o self-hosted `/v1` risponde a piccole probe dirette
`/v1/chat/completions` ma fallisce su `openclaw infer model run` o nei normali
turni dell'agente:

1. Se l'errore menziona `messages[].content` che si aspetta una stringa, imposta
   `models.providers.<provider>.models[].compat.requiresStringContent: true`.
2. Se il backend continua a fallire solo nei turni agente di OpenClaw, imposta
   `models.providers.<provider>.models[].compat.supportsTools: false` e riprova.
3. Se le chiamate dirette minime continuano a funzionare ma i prompt OpenClaw più grandi mandano in crash il
   backend, tratta il problema residuo come una limitazione upstream del modello/server e
   continua nel runbook approfondito:
   [/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail](/it/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)

## L'installazione del plugin fallisce con openclaw extensions mancanti

Se l'installazione fallisce con `package.json missing openclaw.extensions`, il pacchetto plugin
usa una struttura vecchia che OpenClaw non accetta più.

Correzione nel pacchetto plugin:

1. Aggiungi `openclaw.extensions` a `package.json`.
2. Punta le entry ai file runtime compilati (di solito `./dist/index.js`).
3. Ripubblica il plugin ed esegui di nuovo `openclaw plugins install <package>`.

Esempio:

```json
{
  "name": "@openclaw/my-plugin",
  "version": "1.2.3",
  "openclaw": {
    "extensions": ["./dist/index.js"]
  }
}
```

Riferimento: [Architettura dei plugin](/it/plugins/architecture)

## Albero decisionale

```mermaid
flowchart TD
  A[OpenClaw non funziona] --> B{Cosa si rompe per primo}
  B --> C[Nessuna risposta]
  B --> D[Dashboard o Control UI non si connette]
  B --> E[Il Gateway non si avvia o il servizio non è in esecuzione]
  B --> F[Il canale si connette ma i messaggi non passano]
  B --> G[Cron o heartbeat non si è attivato o non ha consegnato]
  B --> H[Il nodo è associato ma il comando exec per camera canvas screen fallisce]
  B --> I[Lo strumento browser fallisce]

  C --> C1[/Sezione Nessuna risposta/]
  D --> D1[/Sezione Control UI/]
  E --> E1[/Sezione Gateway/]
  F --> F1[/Sezione Flusso del canale/]
  G --> G1[/Sezione Automazione/]
  H --> H1[/Sezione Strumenti nodo/]
  I --> I1[/Sezione Browser/]
```

<AccordionGroup>
  <Accordion title="Nessuna risposta">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw channels status --probe
    openclaw pairing list --channel <channel> [--account <id>]
    openclaw logs --follow
    ```

    Un output corretto appare così:

    - `Runtime: running`
    - `RPC probe: ok`
    - Il tuo canale mostra il trasporto connesso e, dove supportato, `works` o `audit ok` in `channels status --probe`
    - Il mittente risulta approvato (oppure la policy DM è aperta/in allowlist)

    Firme di log comuni:

    - `drop guild message (mention required` → il gating per mention ha bloccato il messaggio in Discord.
    - `pairing request` → il mittente non è approvato ed è in attesa di approvazione dell'associazione DM.
    - `blocked` / `allowlist` nei log del canale → mittente, stanza o gruppo è filtrato.

    Pagine approfondite:

    - [/gateway/troubleshooting#no-replies](/it/gateway/troubleshooting#no-replies)
    - [/channels/troubleshooting](/it/channels/troubleshooting)
    - [/channels/pairing](/it/channels/pairing)

  </Accordion>

  <Accordion title="Dashboard o Control UI non si connette">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw logs --follow
    openclaw doctor
    openclaw channels status --probe
    ```

    Un output corretto appare così:

    - `Dashboard: http://...` è mostrato in `openclaw gateway status`
    - `RPC probe: ok`
    - Nessun loop auth nei log

    Firme di log comuni:

    - `device identity required` → il contesto HTTP/non sicuro non può completare l'auth del dispositivo.
    - `origin not allowed` → l'`Origin` del browser non è consentito per la destinazione gateway della Control UI.
    - `AUTH_TOKEN_MISMATCH` con suggerimenti di tentativo (`canRetryWithDeviceToken=true`) → può verificarsi automaticamente un tentativo con device token fidato.
    - Quel tentativo con token in cache riutilizza l'insieme di scope in cache memorizzato con il paired
      device token. I chiamanti con `deviceToken` esplicito / `scopes` espliciti mantengono
      invece l'insieme di scope richiesto.
    - Nel percorso asincrono Tailscale Serve Control UI, i tentativi falliti per lo stesso
      `{scope, ip}` vengono serializzati prima che il limiter registri l'errore, quindi un
      secondo tentativo errato concorrente può già mostrare `retry later`.
    - `too many failed authentication attempts (retry later)` da un'origine browser localhost → i fallimenti ripetuti dalla stessa `Origin` vengono temporaneamente bloccati; un'altra origine localhost usa un bucket separato.
    - `repeated unauthorized` dopo quel tentativo → token/password errati, mancata corrispondenza della modalità auth o paired device token obsoleto.
    - `gateway connect failed:` → la UI sta puntando all'URL/porta sbagliata o a un gateway non raggiungibile.

    Pagine approfondite:

    - [/gateway/troubleshooting#dashboard-control-ui-connectivity](/it/gateway/troubleshooting#dashboard-control-ui-connectivity)
    - [/web/control-ui](/web/control-ui)
    - [/gateway/authentication](/it/gateway/authentication)

  </Accordion>

  <Accordion title="Il Gateway non si avvia o il servizio è installato ma non è in esecuzione">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw logs --follow
    openclaw doctor
    openclaw channels status --probe
    ```

    Un output corretto appare così:

    - `Service: ... (loaded)`
    - `Runtime: running`
    - `RPC probe: ok`

    Firme di log comuni:

    - `Gateway start blocked: set gateway.mode=local` o `existing config is missing gateway.mode` → la modalità gateway è remote, oppure nel file di configurazione manca il contrassegno local-mode e deve essere riparato.
    - `refusing to bind gateway ... without auth` → bind non-loopback senza un percorso auth gateway valido (token/password, oppure trusted-proxy dove configurato).
    - `another gateway instance is already listening` o `EADDRINUSE` → porta già occupata.

    Pagine approfondite:

    - [/gateway/troubleshooting#gateway-service-not-running](/it/gateway/troubleshooting#gateway-service-not-running)
    - [/gateway/background-process](/it/gateway/background-process)
    - [/gateway/configuration](/it/gateway/configuration)

  </Accordion>

  <Accordion title="Il canale si connette ma i messaggi non passano">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw logs --follow
    openclaw doctor
    openclaw channels status --probe
    ```

    Un output corretto appare così:

    - Il trasporto del canale è connesso.
    - I controlli pairing/allowlist passano.
    - Le mention vengono rilevate dove richiesto.

    Firme di log comuni:

    - `mention required` → il gating per mention nel gruppo ha bloccato l'elaborazione.
    - `pairing` / `pending` → il mittente DM non è ancora approvato.
    - `not_in_channel`, `missing_scope`, `Forbidden`, `401/403` → problema di token o permessi del canale.

    Pagine approfondite:

    - [/gateway/troubleshooting#channel-connected-messages-not-flowing](/it/gateway/troubleshooting#channel-connected-messages-not-flowing)
    - [/channels/troubleshooting](/it/channels/troubleshooting)

  </Accordion>

  <Accordion title="Cron o heartbeat non si è attivato o non ha consegnato">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw cron status
    openclaw cron list
    openclaw cron runs --id <jobId> --limit 20
    openclaw logs --follow
    ```

    Un output corretto appare così:

    - `cron.status` mostra che è abilitato con una prossima riattivazione.
    - `cron runs` mostra voci `ok` recenti.
    - Heartbeat è abilitato e non è fuori dalle ore attive.

    Firme di log comuni:

    - `cron: scheduler disabled; jobs will not run automatically` → cron è disabilitato.
    - `heartbeat skipped` con `reason=quiet-hours` → fuori dalle ore attive configurate.
    - `heartbeat skipped` con `reason=empty-heartbeat-file` → `HEARTBEAT.md` esiste ma contiene solo struttura vuota o solo intestazioni.
    - `heartbeat skipped` con `reason=no-tasks-due` → la modalità attività di `HEARTBEAT.md` è attiva ma nessuno degli intervalli delle attività è ancora scaduto.
    - `heartbeat skipped` con `reason=alerts-disabled` → tutta la visibilità heartbeat è disabilitata (`showOk`, `showAlerts` e `useIndicator` sono tutti disattivati).
    - `requests-in-flight` → corsia principale occupata; la riattivazione heartbeat è stata rinviata.
    - `unknown accountId` → l'account di destinazione della consegna heartbeat non esiste.

    Pagine approfondite:

    - [/gateway/troubleshooting#cron-and-heartbeat-delivery](/it/gateway/troubleshooting#cron-and-heartbeat-delivery)
    - [/automation/cron-jobs#troubleshooting](/it/automation/cron-jobs#troubleshooting)
    - [/gateway/heartbeat](/it/gateway/heartbeat)

    </Accordion>

    <Accordion title="Il nodo è associato ma lo strumento fallisce per camera canvas screen exec">
      ```bash
      openclaw status
      openclaw gateway status
      openclaw nodes status
      openclaw nodes describe --node <idOrNameOrIp>
      openclaw logs --follow
      ```

      Un output corretto appare così:

      - Il nodo è elencato come connesso e associato per il ruolo `node`.
      - La capability esiste per il comando che stai invocando.
      - Lo stato del permesso è concesso per lo strumento.

      Firme di log comuni:

      - `NODE_BACKGROUND_UNAVAILABLE` → porta l'app del nodo in primo piano.
      - `*_PERMISSION_REQUIRED` → il permesso del sistema operativo è stato negato o manca.
      - `SYSTEM_RUN_DENIED: approval required` → l'approvazione exec è in sospeso.
      - `SYSTEM_RUN_DENIED: allowlist miss` → il comando non è nella allowlist exec.

      Pagine approfondite:

      - [/gateway/troubleshooting#node-paired-tool-fails](/it/gateway/troubleshooting#node-paired-tool-fails)
      - [/nodes/troubleshooting](/it/nodes/troubleshooting)
      - [/tools/exec-approvals](/it/tools/exec-approvals)

    </Accordion>

    <Accordion title="Exec chiede improvvisamente l'approvazione">
      ```bash
      openclaw config get tools.exec.host
      openclaw config get tools.exec.security
      openclaw config get tools.exec.ask
      openclaw gateway restart
      ```

      Cosa è cambiato:

      - Se `tools.exec.host` non è impostato, il valore predefinito è `auto`.
      - `host=auto` viene risolto in `sandbox` quando è attivo un runtime sandbox, altrimenti in `gateway`.
      - `host=auto` riguarda solo il routing; il comportamento "YOLO" senza prompt deriva da `security=full` più `ask=off` su gateway/node.
      - Su `gateway` e `node`, `tools.exec.security` non impostato usa come predefinito `full`.
      - `tools.exec.ask` non impostato usa come predefinito `off`.
      - Risultato: se stai vedendo richieste di approvazione, qualche policy locale dell'host o per sessione ha reso exec più restrittivo rispetto ai valori predefiniti attuali.

      Ripristina l'attuale comportamento predefinito senza approvazione:

      ```bash
      openclaw config set tools.exec.host gateway
      openclaw config set tools.exec.security full
      openclaw config set tools.exec.ask off
      openclaw gateway restart
      ```

      Alternative più sicure:

      - Imposta solo `tools.exec.host=gateway` se vuoi semplicemente un instradamento host stabile.
      - Usa `security=allowlist` con `ask=on-miss` se vuoi exec sull'host ma desideri comunque una revisione in caso di mancata corrispondenza con la allowlist.
      - Abilita la modalità sandbox se vuoi che `host=auto` torni a risolversi in `sandbox`.

      Firme di log comuni:

      - `Approval required.` → il comando è in attesa su `/approve ...`.
      - `SYSTEM_RUN_DENIED: approval required` → l'approvazione exec dell'host del nodo è in sospeso.
      - `exec host=sandbox requires a sandbox runtime for this session` → selezione sandbox implicita/esplicita ma la modalità sandbox è disattivata.

      Pagine approfondite:

      - [/tools/exec](/it/tools/exec)
      - [/tools/exec-approvals](/it/tools/exec-approvals)
      - [/gateway/security#what-the-audit-checks-high-level](/it/gateway/security#what-the-audit-checks-high-level)

    </Accordion>

    <Accordion title="Lo strumento browser fallisce">
      ```bash
      openclaw status
      openclaw gateway status
      openclaw browser status
      openclaw logs --follow
      openclaw doctor
      ```

      Un output corretto appare così:

      - Lo stato del browser mostra `running: true` e un browser/profilo selezionato.
      - `openclaw` si avvia, oppure `user` può vedere le schede Chrome locali.

      Firme di log comuni:

      - `unknown command "browser"` o `unknown command 'browser'` → `plugins.allow` è impostato e non include `browser`.
      - `Failed to start Chrome CDP on port` → l'avvio del browser locale non è riuscito.
      - `browser.executablePath not found` → il percorso del binario configurato è errato.
      - `browser.cdpUrl must be http(s) or ws(s)` → l'URL CDP configurato usa uno schema non supportato.
      - `browser.cdpUrl has invalid port` → l'URL CDP configurato ha una porta non valida o fuori intervallo.
      - `No Chrome tabs found for profile="user"` → il profilo di collegamento Chrome MCP non ha schede Chrome locali aperte.
      - `Remote CDP for profile "<name>" is not reachable` → l'endpoint CDP remoto configurato non è raggiungibile da questo host.
      - `Browser attachOnly is enabled ... not reachable` o `Browser attachOnly is enabled and CDP websocket ... is not reachable` → il profilo solo collegamento non ha una destinazione CDP live.
      - override obsoleti di viewport / dark mode / locale / offline su profili solo collegamento o CDP remoti → esegui `openclaw browser stop --browser-profile <name>` per chiudere la sessione di controllo attiva e rilasciare lo stato di emulazione senza riavviare il gateway.

      Pagine approfondite:

      - [/gateway/troubleshooting#browser-tool-fails](/it/gateway/troubleshooting#browser-tool-fails)
      - [/tools/browser#missing-browser-command-or-tool](/it/tools/browser#missing-browser-command-or-tool)
      - [/tools/browser-linux-troubleshooting](/it/tools/browser-linux-troubleshooting)
      - [/tools/browser-wsl2-windows-remote-cdp-troubleshooting](/it/tools/browser-wsl2-windows-remote-cdp-troubleshooting)

    </Accordion>

  </AccordionGroup>

## Correlati

- [FAQ](/it/help/faq) — domande frequenti
- [Risoluzione dei problemi del Gateway](/it/gateway/troubleshooting) — problemi specifici del gateway
- [Doctor](/it/gateway/doctor) — controlli di integrità automatizzati e riparazioni
- [Risoluzione dei problemi dei canali](/it/channels/troubleshooting) — problemi di connettività dei canali
- [Risoluzione dei problemi di automazione](/it/automation/cron-jobs#troubleshooting) — problemi di cron e heartbeat
