---
read_when:
    - OpenClaw non funziona e ti serve il percorso più rapido verso una soluzione
    - Vuoi un flusso di triage prima di passare a runbook approfonditi
summary: Hub di risoluzione dei problemi di OpenClaw orientato ai sintomi
title: Risoluzione generale dei problemi
x-i18n:
    generated_at: "2026-04-08T02:16:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8abda90ef80234c2f91a51c5e1f2c004d4a4da12a5d5631b5927762550c6d5e3
    source_path: help/troubleshooting.md
    workflow: 15
---

# Risoluzione dei problemi

Se hai solo 2 minuti, usa questa pagina come punto di ingresso per il triage.

## Primi 60 secondi

Esegui questa sequenza esatta nell'ordine indicato:

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
- `openclaw gateway probe` → la destinazione gateway prevista è raggiungibile (`Reachable: yes`). `RPC: limited - missing scope: operator.read` indica una diagnostica degradata, non un errore di connessione.
- `openclaw gateway status` → `Runtime: running` e `RPC probe: ok`.
- `openclaw doctor` → nessun errore bloccante di configurazione/servizio.
- `openclaw channels status --probe` → se il gateway è raggiungibile restituisce lo stato live del trasporto per account
  più i risultati di probe/audit come `works` o `audit ok`; se il
  gateway non è raggiungibile, il comando torna a riepiloghi basati solo sulla configurazione.
- `openclaw logs --follow` → attività regolare, nessun errore fatale ripetuto.

## Anthropic long context 429

Se vedi:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`,
vai a [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/it/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

## Il backend locale compatibile con OpenAI funziona direttamente ma fallisce in OpenClaw

Se il tuo backend `/v1` locale o self-hosted risponde a piccole probe dirette
`/v1/chat/completions` ma fallisce su `openclaw infer model run` o nei normali
turni dell'agente:

1. Se l'errore menziona `messages[].content` che si aspetta una stringa, imposta
   `models.providers.<provider>.models[].compat.requiresStringContent: true`.
2. Se il backend continua a fallire solo durante i turni agente di OpenClaw, imposta
   `models.providers.<provider>.models[].compat.supportsTools: false` e riprova.
3. Se chiamate dirette minime continuano a funzionare ma prompt OpenClaw più grandi mandano in crash il
   backend, tratta il problema residuo come una limitazione upstream del modello/server e
   continua nel runbook approfondito:
   [/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail](/it/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)

## L'installazione del plugin fallisce con openclaw extensions mancanti

Se l'installazione fallisce con `package.json missing openclaw.extensions`, il pacchetto plugin
sta usando una forma vecchia che OpenClaw non accetta più.

Correzione nel pacchetto plugin:

1. Aggiungi `openclaw.extensions` a `package.json`.
2. Punta le voci ai file runtime compilati (di solito `./dist/index.js`).
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
  A[OpenClaw non funziona] --> B{Che cosa si rompe per primo}
  B --> C[Nessuna risposta]
  B --> D[Dashboard o Control UI non si connettono]
  B --> E[Il gateway non si avvia o il servizio non è in esecuzione]
  B --> F[Il canale si connette ma i messaggi non fluiscono]
  B --> G[Cron o heartbeat non è partito o non ha consegnato]
  B --> H[Il nodo è associato ma lo strumento camera canvas screen exec fallisce]
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
    - Il mittente risulta approvato (oppure la policy DM è aperta/allowlist)

    Firme di log comuni:

    - `drop guild message (mention required` → il blocco per menzione obbligatoria ha impedito l'elaborazione del messaggio in Discord.
    - `pairing request` → il mittente non è approvato ed è in attesa dell'approvazione di pairing via DM.
    - `blocked` / `allowlist` nei log del canale → il mittente, la stanza o il gruppo è filtrato.

    Pagine approfondite:

    - [/gateway/troubleshooting#no-replies](/it/gateway/troubleshooting#no-replies)
    - [/channels/troubleshooting](/it/channels/troubleshooting)
    - [/channels/pairing](/it/channels/pairing)

  </Accordion>

  <Accordion title="Dashboard o Control UI non si connettono">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw logs --follow
    openclaw doctor
    openclaw channels status --probe
    ```

    Un output corretto appare così:

    - `Dashboard: http://...` viene mostrato in `openclaw gateway status`
    - `RPC probe: ok`
    - Nessun loop auth nei log

    Firme di log comuni:

    - `device identity required` → il contesto HTTP/non sicuro non può completare l'auth del dispositivo.
    - `origin not allowed` → l'`Origin` del browser non è consentito per la destinazione gateway della Control UI.
    - `AUTH_TOKEN_MISMATCH` con suggerimenti di retry (`canRetryWithDeviceToken=true`) → può verificarsi automaticamente un solo retry con device token attendibile.
    - Quel retry con token in cache riutilizza l'insieme di scope in cache memorizzato con il
      device token associato. I chiamanti con `deviceToken` esplicito / `scopes` espliciti mantengono
      invece l'insieme di scope richiesto.
    - Nel percorso asincrono Tailscale Serve della Control UI, i tentativi falliti per lo stesso
      `{scope, ip}` vengono serializzati prima che il limitatore registri il fallimento, quindi un
      secondo retry errato concorrente può già mostrare `retry later`.
    - `too many failed authentication attempts (retry later)` da un'origine browser localhost
      → fallimenti ripetuti da quello stesso `Origin` vengono temporaneamente
      bloccati; un'altra origine localhost usa un bucket separato.
    - `repeated unauthorized` dopo quel retry → token/password errati, mismatch della modalità auth o device token associato obsoleto.
    - `gateway connect failed:` → la UI punta all'URL/porta sbagliati oppure il gateway non è raggiungibile.

    Pagine approfondite:

    - [/gateway/troubleshooting#dashboard-control-ui-connectivity](/it/gateway/troubleshooting#dashboard-control-ui-connectivity)
    - [/web/control-ui](/web/control-ui)
    - [/gateway/authentication](/it/gateway/authentication)

  </Accordion>

  <Accordion title="Il gateway non si avvia o il servizio installato non è in esecuzione">
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

    - `Gateway start blocked: set gateway.mode=local` o `existing config is missing gateway.mode` → la modalità gateway è remota, oppure nel file di configurazione manca l'indicazione della modalità locale e dovrebbe essere riparato.
    - `refusing to bind gateway ... without auth` → bind non-loopback senza un percorso auth gateway valido (token/password, o trusted-proxy dove configurato).
    - `another gateway instance is already listening` o `EADDRINUSE` → la porta è già occupata.

    Pagine approfondite:

    - [/gateway/troubleshooting#gateway-service-not-running](/it/gateway/troubleshooting#gateway-service-not-running)
    - [/gateway/background-process](/it/gateway/background-process)
    - [/gateway/configuration](/it/gateway/configuration)

  </Accordion>

  <Accordion title="Il canale si connette ma i messaggi non fluiscono">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw logs --follow
    openclaw doctor
    openclaw channels status --probe
    ```

    Un output corretto appare così:

    - Il trasporto del canale è connesso.
    - I controlli pairing/allowlist vengono superati.
    - Le menzioni vengono rilevate dove richiesto.

    Firme di log comuni:

    - `mention required` → il blocco per menzione nei gruppi ha impedito l'elaborazione.
    - `pairing` / `pending` → il mittente DM non è ancora approvato.
    - `not_in_channel`, `missing_scope`, `Forbidden`, `401/403` → problema di permessi del canale o del token.

    Pagine approfondite:

    - [/gateway/troubleshooting#channel-connected-messages-not-flowing](/it/gateway/troubleshooting#channel-connected-messages-not-flowing)
    - [/channels/troubleshooting](/it/channels/troubleshooting)

  </Accordion>

  <Accordion title="Cron o heartbeat non è partito o non ha consegnato">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw cron status
    openclaw cron list
    openclaw cron runs --id <jobId> --limit 20
    openclaw logs --follow
    ```

    Un output corretto appare così:

    - `cron.status` mostra che è abilitato con un prossimo risveglio.
    - `cron runs` mostra voci `ok` recenti.
    - Heartbeat è abilitato e non è fuori dall'orario attivo.

    Firme di log comuni:

- `cron: scheduler disabled; jobs will not run automatically` → cron è disabilitato.
- `heartbeat skipped` con `reason=quiet-hours` → fuori dalle ore attive configurate.
- `heartbeat skipped` con `reason=empty-heartbeat-file` → `HEARTBEAT.md` esiste ma contiene solo struttura vuota/intestazioni.
- `heartbeat skipped` con `reason=no-tasks-due` → la modalità task di `HEARTBEAT.md` è attiva ma nessuno degli intervalli dei task è ancora in scadenza.
- `heartbeat skipped` con `reason=alerts-disabled` → tutta la visibilità heartbeat è disabilitata (`showOk`, `showAlerts` e `useIndicator` sono tutti disattivati).
- `requests-in-flight` → il canale principale è occupato; il risveglio heartbeat è stato rinviato. - `unknown accountId` → l'account di destinazione per la consegna heartbeat non esiste.

      Pagine approfondite:

      - [/gateway/troubleshooting#cron-and-heartbeat-delivery](/it/gateway/troubleshooting#cron-and-heartbeat-delivery)
      - [/automation/cron-jobs#troubleshooting](/it/automation/cron-jobs#troubleshooting)
      - [/gateway/heartbeat](/it/gateway/heartbeat)

    </Accordion>

    <Accordion title="Il nodo è associato ma lo strumento camera canvas screen exec fallisce">
      ```bash
      openclaw status
      openclaw gateway status
      openclaw nodes status
      openclaw nodes describe --node <idOrNameOrIp>
      openclaw logs --follow
      ```

      Un output corretto appare così:

      - Il nodo è elencato come connesso e associato per il ruolo `node`.
      - La capacità esiste per il comando che stai invocando.
      - Lo stato dei permessi è concesso per lo strumento.

      Firme di log comuni:

      - `NODE_BACKGROUND_UNAVAILABLE` → porta l'app node in primo piano.
      - `*_PERMISSION_REQUIRED` → il permesso OS è stato negato o manca.
      - `SYSTEM_RUN_DENIED: approval required` → l'approvazione exec è in attesa.
      - `SYSTEM_RUN_DENIED: allowlist miss` → il comando non è nella allowlist exec.

      Pagine approfondite:

      - [/gateway/troubleshooting#node-paired-tool-fails](/it/gateway/troubleshooting#node-paired-tool-fails)
      - [/nodes/troubleshooting](/it/nodes/troubleshooting)
      - [/tools/exec-approvals](/it/tools/exec-approvals)

    </Accordion>

    <Accordion title="Exec chiede improvvisamente approvazione">
      ```bash
      openclaw config get tools.exec.host
      openclaw config get tools.exec.security
      openclaw config get tools.exec.ask
      openclaw gateway restart
      ```

      Cosa è cambiato:

      - Se `tools.exec.host` non è impostato, il valore predefinito è `auto`.
      - `host=auto` si risolve in `sandbox` quando un runtime sandbox è attivo, altrimenti in `gateway`.
      - `host=auto` riguarda solo l'instradamento; il comportamento "YOLO" senza prompt deriva da `security=full` più `ask=off` su gateway/node.
      - Su `gateway` e `node`, `tools.exec.security` non impostato ha come valore predefinito `full`.
      - `tools.exec.ask` non impostato ha come valore predefinito `off`.
      - Risultato: se stai vedendo richieste di approvazione, qualche policy locale all'host o per sessione ha irrigidito exec rispetto ai valori predefiniti correnti.

      Ripristina l'attuale comportamento predefinito senza approvazione:

      ```bash
      openclaw config set tools.exec.host gateway
      openclaw config set tools.exec.security full
      openclaw config set tools.exec.ask off
      openclaw gateway restart
      ```

      Alternative più sicure:

      - Imposta solo `tools.exec.host=gateway` se vuoi semplicemente un instradamento host stabile.
      - Usa `security=allowlist` con `ask=on-miss` se vuoi exec sull'host ma vuoi comunque revisione in caso di mancata allowlist.
      - Abilita la modalità sandbox se vuoi che `host=auto` torni a risolversi in `sandbox`.

      Firme di log comuni:

      - `Approval required.` → il comando è in attesa di `/approve ...`.
      - `SYSTEM_RUN_DENIED: approval required` → l'approvazione exec su host node è in attesa.
      - `exec host=sandbox requires a sandbox runtime for this session` → selezione sandbox implicita/esplicita ma la modalità sandbox è disattivata.

      Pagine approfondite:

      - [/tools/exec](/it/tools/exec)
      - [/tools/exec-approvals](/it/tools/exec-approvals)
      - [/gateway/security#runtime-expectation-drift](/it/gateway/security#runtime-expectation-drift)

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

      - Lo stato browser mostra `running: true` e un browser/profilo scelto.
      - `openclaw` si avvia, oppure `user` può vedere le schede Chrome locali.

      Firme di log comuni:

      - `unknown command "browser"` o `unknown command 'browser'` → `plugins.allow` è impostato e non include `browser`.
      - `Failed to start Chrome CDP on port` → l'avvio del browser locale è fallito.
      - `browser.executablePath not found` → il percorso binario configurato è errato.
      - `browser.cdpUrl must be http(s) or ws(s)` → l'URL CDP configurato usa uno schema non supportato.
      - `browser.cdpUrl has invalid port` → l'URL CDP configurato ha una porta non valida o fuori intervallo.
      - `No Chrome tabs found for profile="user"` → il profilo di attach Chrome MCP non ha schede Chrome locali aperte.
      - `Remote CDP for profile "<name>" is not reachable` → l'endpoint CDP remoto configurato non è raggiungibile da questo host.
      - `Browser attachOnly is enabled ... not reachable` o `Browser attachOnly is enabled and CDP websocket ... is not reachable` → il profilo solo-attach non ha una destinazione CDP live.
      - override obsoleti di viewport / dark-mode / locale / offline su profili solo-attach o CDP remoto → esegui `openclaw browser stop --browser-profile <name>` per chiudere la sessione di controllo attiva e rilasciare lo stato di emulazione senza riavviare il gateway.

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
- [Doctor](/it/gateway/doctor) — controlli di integrità e riparazioni automatici
- [Risoluzione dei problemi dei canali](/it/channels/troubleshooting) — problemi di connettività dei canali
- [Risoluzione dei problemi di automazione](/it/automation/cron-jobs#troubleshooting) — problemi di cron e heartbeat
