---
read_when:
    - Aggiungere automazione del browser controllata dall'agente
    - Debug di perché openclaw interferisce con il tuo Chrome
    - Implementare impostazioni + ciclo di vita del browser nell'app macOS
summary: Servizio integrato di controllo del browser + comandi di azione
title: Browser (gestito da OpenClaw)
x-i18n:
    generated_at: "2026-04-11T02:47:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: da6fed36a6f40a50e825f90e5616778954545bd7e52397f7e088b85251ee024f
    source_path: tools/browser.md
    workflow: 15
---

# Browser (gestito da openclaw)

OpenClaw può eseguire un **profilo dedicato Chrome/Brave/Edge/Chromium** controllato dall'agente.
È isolato dal tuo browser personale ed è gestito tramite un piccolo servizio di
controllo locale all'interno del Gateway (solo loopback).

Vista per principianti:

- Consideralo come un **browser separato, solo per l'agente**.
- Il profilo `openclaw` **non** tocca il tuo profilo browser personale.
- L'agente può **aprire schede, leggere pagine, fare clic e digitare** in un ambiente sicuro.
- Il profilo integrato `user` si collega alla tua vera sessione Chrome con accesso effettuato tramite Chrome MCP.

## Cosa ottieni

- Un profilo browser separato chiamato **openclaw** (accento arancione per impostazione predefinita).
- Controllo deterministico delle schede (elenca/apri/metti a fuoco/chiudi).
- Azioni dell'agente (clic/digitazione/trascinamento/selezione), snapshot, screenshot, PDF.
- Supporto opzionale per più profili (`openclaw`, `work`, `remote`, ...).

Questo browser **non** è il tuo browser quotidiano. È una superficie sicura e isolata per
automazione e verifica dell'agente.

## Guida rapida

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

Se ricevi “Browser disabled”, abilitalo nella configurazione (vedi sotto) e riavvia il
Gateway.

Se `openclaw browser` manca del tutto, oppure l'agente dice che lo strumento browser
non è disponibile, vai a [Comando o strumento browser mancante](/it/tools/browser#missing-browser-command-or-tool).

## Controllo del plugin

Lo strumento `browser` predefinito ora è un plugin incluso distribuito abilitato per
impostazione predefinita. Questo significa che puoi disabilitarlo o sostituirlo senza rimuovere il resto del
sistema di plugin di OpenClaw:

```json5
{
  plugins: {
    entries: {
      browser: {
        enabled: false,
      },
    },
  },
}
```

Disabilita il plugin incluso prima di installare un altro plugin che fornisce lo
stesso nome di strumento `browser`. L'esperienza browser predefinita richiede entrambi:

- `plugins.entries.browser.enabled` non disabilitato
- `browser.enabled=true`

Se disattivi solo il plugin, la CLI browser inclusa (`openclaw browser`),
il metodo gateway (`browser.request`), lo strumento agente e il servizio predefinito di controllo browser scompaiono tutti insieme. La tua configurazione `browser.*` rimane intatta perché un plugin sostitutivo possa riutilizzarla.

Il plugin browser incluso ora gestisce anche l'implementazione runtime del browser.
Il core mantiene solo helper condivisi del Plugin SDK più re-export di compatibilità per i vecchi percorsi di import interni. In pratica, rimuovere o sostituire il pacchetto plugin browser elimina l'insieme di funzionalità browser invece di lasciare dietro un secondo runtime gestito dal core.

Le modifiche alla configurazione browser richiedono comunque un riavvio del Gateway affinché il plugin incluso
possa registrare di nuovo il suo servizio browser con le nuove impostazioni.

## Comando o strumento browser mancante

Se `openclaw browser` diventa improvvisamente un comando sconosciuto dopo un aggiornamento, oppure
l'agente segnala che lo strumento browser manca, la causa più comune è una lista `plugins.allow`
restrittiva che non include `browser`.

Esempio di configurazione errata:

```json5
{
  plugins: {
    allow: ["telegram"],
  },
}
```

Correggila aggiungendo `browser` alla allowlist dei plugin:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

Note importanti:

- `browser.enabled=true` da solo non basta quando `plugins.allow` è impostato.
- Anche `plugins.entries.browser.enabled=true` da solo non basta quando `plugins.allow` è impostato.
- `tools.alsoAllow: ["browser"]` **non** carica il plugin browser incluso. Regola solo la policy dello strumento dopo che il plugin è già stato caricato.
- Se non hai bisogno di una allowlist restrittiva dei plugin, rimuovere `plugins.allow` ripristina anche il comportamento browser incluso predefinito.

Sintomi tipici:

- `openclaw browser` è un comando sconosciuto.
- `browser.request` manca.
- L'agente segnala che lo strumento browser non è disponibile o manca.

## Profili: `openclaw` vs `user`

- `openclaw`: browser gestito e isolato (nessuna estensione richiesta).
- `user`: profilo integrato di collegamento Chrome MCP per la tua **vera sessione Chrome con accesso effettuato**.

Per le chiamate allo strumento browser dell'agente:

- Predefinito: usa il browser isolato `openclaw`.
- Preferisci `profile="user"` quando contano le sessioni già con accesso effettuato e l'utente
  è al computer per fare clic/approvare eventuali prompt di collegamento.
- `profile` è l'override esplicito quando vuoi una modalità browser specifica.

Imposta `browser.defaultProfile: "openclaw"` se vuoi la modalità gestita come predefinita.

## Configurazione

Le impostazioni browser si trovano in `~/.openclaw/openclaw.json`.

```json5
{
  browser: {
    enabled: true, // predefinito: true
    ssrfPolicy: {
      // dangerouslyAllowPrivateNetwork: true, // attiva solo per accesso fidato a reti private
      // allowPrivateNetwork: true, // alias legacy
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // override legacy a profilo singolo
    remoteCdpTimeoutMs: 1500, // timeout HTTP CDP remoto (ms)
    remoteCdpHandshakeTimeoutMs: 3000, // timeout handshake WebSocket CDP remoto (ms)
    defaultProfile: "openclaw",
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: {
        driver: "existing-session",
        attachOnly: true,
        color: "#00AA00",
      },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
  },
}
```

Note:

- Il servizio di controllo browser si collega a loopback su una porta derivata da `gateway.port`
  (predefinita: `18791`, cioè gateway + 2).
- Se fai override della porta del Gateway (`gateway.port` o `OPENCLAW_GATEWAY_PORT`),
  le porte browser derivate si spostano per restare nella stessa “famiglia”.
- `cdpUrl` usa per impostazione predefinita la porta CDP locale gestita quando non è impostato.
- `remoteCdpTimeoutMs` si applica ai controlli di raggiungibilità CDP remota (non loopback).
- `remoteCdpHandshakeTimeoutMs` si applica ai controlli di raggiungibilità WebSocket CDP remota.
- La navigazione/apertura scheda del browser è protetta da SSRF prima della navigazione e ricontrollata al meglio sull'URL finale `http(s)` dopo la navigazione.
- In modalità SSRF strict, anche discovery/probe degli endpoint CDP remoti (`cdpUrl`, incluse le ricerche `/json/version`) vengono controllati.
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` è disabilitato per impostazione predefinita. Impostalo su `true` solo quando ti fidi intenzionalmente dell'accesso browser alla rete privata.
- `browser.ssrfPolicy.allowPrivateNetwork` resta supportato come alias legacy per compatibilità.
- `attachOnly: true` significa “non avviare mai un browser locale; collegati solo se è già in esecuzione.”
- `color` + `color` per profilo colorano l'interfaccia del browser così puoi vedere quale profilo è attivo.
- Il profilo predefinito è `openclaw` (browser standalone gestito da OpenClaw). Usa `defaultProfile: "user"` per scegliere il browser utente con accesso effettuato.
- Ordine di rilevamento automatico: browser predefinito del sistema se basato su Chromium; altrimenti Chrome → Brave → Edge → Chromium → Chrome Canary.
- I profili locali `openclaw` assegnano automaticamente `cdpPort`/`cdpUrl` — impostali solo per CDP remota.
- `driver: "existing-session"` usa Chrome DevTools MCP invece di CDP raw. Non
  impostare `cdpUrl` per quel driver.
- Imposta `browser.profiles.<name>.userDataDir` quando un profilo existing-session
  deve collegarsi a un profilo utente Chromium non predefinito come Brave o Edge.

## Usa Brave (o un altro browser basato su Chromium)

Se il tuo browser **predefinito di sistema** è basato su Chromium (Chrome/Brave/Edge/ecc),
OpenClaw lo usa automaticamente. Imposta `browser.executablePath` per fare override del
rilevamento automatico:

Esempio CLI:

```bash
openclaw config set browser.executablePath "/usr/bin/google-chrome"
```

```json5
// macOS
{
  browser: {
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
  }
}

// Windows
{
  browser: {
    executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
  }
}

// Linux
{
  browser: {
    executablePath: "/usr/bin/brave-browser"
  }
}
```

## Controllo locale vs remoto

- **Controllo locale (predefinito):** il Gateway avvia il servizio di controllo loopback e può avviare un browser locale.
- **Controllo remoto (host del nodo):** esegui un host del nodo sulla macchina che ha il browser; il Gateway inoltra a esso le azioni del browser.
- **CDP remoto:** imposta `browser.profiles.<name>.cdpUrl` (o `browser.cdpUrl`) per
  collegarti a un browser remoto basato su Chromium. In questo caso, OpenClaw non avvierà un browser locale.

Il comportamento di arresto varia in base alla modalità del profilo:

- profili locali gestiti: `openclaw browser stop` arresta il processo browser che
  OpenClaw ha avviato
- profili solo-attach e CDP remoti: `openclaw browser stop` chiude la sessione di
  controllo attiva e rilascia gli override di emulazione Playwright/CDP (viewport,
  schema colori, impostazioni locali, fuso orario, modalità offline e stato simile), anche
  se nessun processo browser è stato avviato da OpenClaw

Gli URL CDP remoti possono includere auth:

- Token di query (ad es. `https://provider.example?token=<token>`)
- Auth HTTP Basic (ad es. `https://user:pass@provider.example`)

OpenClaw conserva l'auth quando chiama gli endpoint `/json/*` e quando si collega
al WebSocket CDP. Preferisci variabili di ambiente o gestori di secret per i
token invece di salvarli nei file di configurazione.

## Proxy browser del nodo (predefinito zero-config)

Se esegui un **host del nodo** sulla macchina che ha il browser, OpenClaw può
instradare automaticamente le chiamate allo strumento browser verso quel nodo senza configurazione browser aggiuntiva.
Questo è il percorso predefinito per i gateway remoti.

Note:

- L'host del nodo espone il proprio server locale di controllo browser tramite un **comando proxy**.
- I profili provengono dalla configurazione `browser.profiles` del nodo stesso (uguale a quella locale).
- `nodeHost.browserProxy.allowProfiles` è facoltativo. Lascialo vuoto per il comportamento legacy/predefinito: tutti i profili configurati restano raggiungibili tramite il proxy, incluse le route di creazione/eliminazione profilo.
- Se imposti `nodeHost.browserProxy.allowProfiles`, OpenClaw lo tratta come un confine di minimo privilegio: solo i profili nella allowlist possono essere destinati, e le route persistenti di creazione/eliminazione profilo vengono bloccate sulla superficie del proxy.
- Disabilitalo se non lo vuoi:
  - Sul nodo: `nodeHost.browserProxy.enabled=false`
  - Sul gateway: `gateway.nodes.browser.mode="off"`

## Browserless (CDP remoto ospitato)

[Browserless](https://browserless.io) è un servizio Chromium ospitato che espone
URL di connessione CDP tramite HTTPS e WebSocket. OpenClaw può usare entrambe le forme, ma
per un profilo browser remoto l'opzione più semplice è l'URL WebSocket diretto
dalla documentazione di connessione di Browserless.

Esempio:

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserless",
    remoteCdpTimeoutMs: 2000,
    remoteCdpHandshakeTimeoutMs: 4000,
    profiles: {
      browserless: {
        cdpUrl: "wss://production-sfo.browserless.io?token=<BROWSERLESS_API_KEY>",
        color: "#00AA00",
      },
    },
  },
}
```

Note:

- Sostituisci `<BROWSERLESS_API_KEY>` con il tuo vero token Browserless.
- Scegli l'endpoint regionale che corrisponde al tuo account Browserless (vedi la loro documentazione).
- Se Browserless ti fornisce un URL base HTTPS, puoi convertirlo in
  `wss://` per una connessione CDP diretta oppure mantenere l'URL HTTPS e lasciare che OpenClaw
  scopra `/json/version`.

## Provider WebSocket CDP diretti

Alcuni servizi browser ospitati espongono un endpoint **WebSocket** diretto invece
della discovery CDP standard basata su HTTP (`/json/version`). OpenClaw supporta entrambe le modalità:

- **Endpoint HTTP(S)** — OpenClaw chiama `/json/version` per individuare l'URL
  WebSocket del debugger, quindi si connette.
- **Endpoint WebSocket** (`ws://` / `wss://`) — OpenClaw si connette direttamente,
  saltando `/json/version`. Usa questa modalità per servizi come
  [Browserless](https://browserless.io),
  [Browserbase](https://www.browserbase.com) o qualsiasi provider che ti fornisce un
  URL WebSocket.

### Browserbase

[Browserbase](https://www.browserbase.com) è una piattaforma cloud per eseguire
browser headless con risoluzione CAPTCHA integrata, modalità stealth e proxy
residenziali.

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserbase",
    remoteCdpTimeoutMs: 3000,
    remoteCdpHandshakeTimeoutMs: 5000,
    profiles: {
      browserbase: {
        cdpUrl: "wss://connect.browserbase.com?apiKey=<BROWSERBASE_API_KEY>",
        color: "#F97316",
      },
    },
  },
}
```

Note:

- [Registrati](https://www.browserbase.com/sign-up) e copia la tua **API Key**
  dalla [dashboard Overview](https://www.browserbase.com/overview).
- Sostituisci `<BROWSERBASE_API_KEY>` con la tua vera chiave API Browserbase.
- Browserbase crea automaticamente una sessione browser alla connessione WebSocket, quindi non
  è necessario alcun passaggio manuale di creazione della sessione.
- Il piano gratuito consente una sessione concorrente e un'ora di browser al mese.
  Vedi i [prezzi](https://www.browserbase.com/pricing) per i limiti dei piani a pagamento.
- Vedi la [documentazione Browserbase](https://docs.browserbase.com) per il riferimento completo
  dell'API, le guide SDK e gli esempi di integrazione.

## Sicurezza

Concetti chiave:

- Il controllo del browser è solo loopback; l'accesso passa tramite auth del Gateway o pairing del nodo.
- L'API HTTP browser loopback standalone usa **solo auth con secret condiviso**:
  auth bearer con token gateway, `x-openclaw-password`, oppure auth HTTP Basic con la
  password del gateway configurata.
- Gli header di identità Tailscale Serve e `gateway.auth.mode: "trusted-proxy"` **non**
  autenticano questa API browser loopback standalone.
- Se il controllo browser è abilitato e non è configurata alcuna auth con secret condiviso, OpenClaw
  genera automaticamente `gateway.auth.token` all'avvio e lo salva nella configurazione.
- OpenClaw **non** genera automaticamente quel token quando `gateway.auth.mode` è
  già `password`, `none` o `trusted-proxy`.
- Mantieni il Gateway e gli eventuali host del nodo su una rete privata (Tailscale); evita l'esposizione pubblica.
- Tratta come secret gli URL/token CDP remoti; preferisci variabili di ambiente o un secrets manager.

Suggerimenti per CDP remoto:

- Preferisci endpoint cifrati (HTTPS o WSS) e token a breve durata quando possibile.
- Evita di incorporare token a lunga durata direttamente nei file di configurazione.

## Profili (multi-browser)

OpenClaw supporta più profili nominati (configurazioni di instradamento). I profili possono essere:

- **gestiti da openclaw**: un'istanza dedicata di browser basato su Chromium con la propria directory dati utente + porta CDP
- **remoti**: un URL CDP esplicito (browser basato su Chromium in esecuzione altrove)
- **sessione esistente**: il tuo profilo Chrome esistente tramite collegamento automatico Chrome DevTools MCP

Valori predefiniti:

- Il profilo `openclaw` viene creato automaticamente se manca.
- Il profilo `user` è integrato per il collegamento existing-session di Chrome MCP.
- I profili existing-session oltre a `user` sono opt-in; creali con `--driver existing-session`.
- Le porte CDP locali vengono allocate da **18800–18899** per impostazione predefinita.
- Eliminare un profilo sposta la sua directory dati locale nel Cestino.

Tutti gli endpoint di controllo accettano `?profile=<name>`; la CLI usa `--browser-profile`.

## Existing-session tramite Chrome DevTools MCP

OpenClaw può anche collegarsi a un profilo browser basato su Chromium già in esecuzione tramite il
server ufficiale Chrome DevTools MCP. Questo riutilizza le schede e lo stato di accesso
già aperti in quel profilo browser.

Riferimenti ufficiali di contesto e configurazione:

- [Chrome for Developers: Use Chrome DevTools MCP with your browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Profilo integrato:

- `user`

Facoltativo: crea un tuo profilo existing-session personalizzato se vuoi un
nome, colore o directory dati browser diversi.

Comportamento predefinito:

- Il profilo integrato `user` usa il collegamento automatico Chrome MCP, che punta al
  profilo locale predefinito di Google Chrome.

Usa `userDataDir` per Brave, Edge, Chromium o un profilo Chrome non predefinito:

```json5
{
  browser: {
    profiles: {
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
    },
  },
}
```

Poi, nel browser corrispondente:

1. Apri la pagina inspect di quel browser per il debug remoto.
2. Abilita il debug remoto.
3. Mantieni il browser in esecuzione e approva il prompt di connessione quando OpenClaw si collega.

Pagine inspect comuni:

- Chrome: `chrome://inspect/#remote-debugging`
- Brave: `brave://inspect/#remote-debugging`
- Edge: `edge://inspect/#remote-debugging`

Smoke test di collegamento live:

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

Aspetto di un risultato corretto:

- `status` mostra `driver: existing-session`
- `status` mostra `transport: chrome-mcp`
- `status` mostra `running: true`
- `tabs` elenca le schede browser già aperte
- `snapshot` restituisce ref dalla scheda live selezionata

Cosa controllare se il collegamento non funziona:

- il browser di destinazione basato su Chromium è versione `144+`
- il debug remoto è abilitato nella pagina inspect di quel browser
- il browser ha mostrato il prompt di consenso al collegamento e tu l'hai accettato
- `openclaw doctor` migra la vecchia configurazione browser basata su estensione e verifica che
  Chrome sia installato localmente per i profili predefiniti di collegamento automatico, ma non può
  abilitare per te il debug remoto lato browser

Uso da parte dell'agente:

- Usa `profile="user"` quando hai bisogno dello stato del browser utente con accesso effettuato.
- Se usi un profilo existing-session personalizzato, passa quel nome profilo esplicito.
- Scegli questa modalità solo quando l'utente è al computer per approvare il prompt
  di collegamento.
- il Gateway o l'host del nodo possono avviare `npx chrome-devtools-mcp@latest --autoConnect`

Note:

- Questo percorso è a rischio più elevato rispetto al profilo isolato `openclaw` perché può
  agire all'interno della tua sessione browser con accesso effettuato.
- OpenClaw non avvia il browser per questo driver; si collega solo a una
  sessione esistente.
- OpenClaw usa qui il flusso ufficiale Chrome DevTools MCP `--autoConnect`. Se
  `userDataDir` è impostato, OpenClaw lo passa per puntare a quella esplicita
  directory dati utente Chromium.
- Gli screenshot existing-session supportano catture della pagina e catture di elementi `--ref`
  da snapshot, ma non selettori CSS `--element`.
- Gli screenshot della pagina existing-session funzionano senza Playwright tramite Chrome MCP.
  Anche gli screenshot di elementi basati su ref (`--ref`) funzionano lì, ma `--full-page`
  non può essere combinato con `--ref` o `--element`.
- Le azioni existing-session sono ancora più limitate rispetto al percorso browser gestito:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag` e `select` richiedono
    ref snapshot invece di selettori CSS
  - `click` supporta solo il pulsante sinistro (nessun override di pulsante o modificatore)
  - `type` non supporta `slowly=true`; usa `fill` o `press`
  - `press` non supporta `delayMs`
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill` ed `evaluate` non
    supportano override di timeout per chiamata
  - `select` attualmente supporta un solo valore
- Existing-session `wait --url` supporta pattern esatti, substring e glob
  come gli altri driver browser. `wait --load networkidle` non è ancora supportato.
- Gli hook di upload existing-session richiedono `ref` o `inputRef`, supportano un file
  alla volta e non supportano il targeting CSS `element`.
- Gli hook di dialogo existing-session non supportano override di timeout.
- Alcune funzionalità richiedono ancora il percorso browser gestito, incluse
  batch actions, esportazione PDF, intercettazione dei download e `responsebody`.
- Existing-session è locale all'host. Se Chrome si trova su un'altra macchina o in un
  namespace di rete diverso, usa invece CDP remoto o un host del nodo.

## Garanzie di isolamento

- **Directory dati utente dedicata**: non tocca mai il tuo profilo browser personale.
- **Porte dedicate**: evita `9222` per prevenire collisioni con i flussi di lavoro di sviluppo.
- **Controllo deterministico delle schede**: punta alle schede tramite `targetId`, non “ultima scheda”.

## Selezione del browser

Quando avvia localmente, OpenClaw sceglie il primo disponibile:

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

Puoi fare override con `browser.executablePath`.

Piattaforme:

- macOS: controlla `/Applications` e `~/Applications`.
- Linux: cerca `google-chrome`, `brave`, `microsoft-edge`, `chromium`, ecc.
- Windows: controlla i percorsi di installazione comuni.

## API di controllo (facoltativa)

Solo per integrazioni locali, il Gateway espone una piccola API HTTP loopback:

- Stato/avvio/arresto: `GET /`, `POST /start`, `POST /stop`
- Schede: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- Snapshot/screenshot: `GET /snapshot`, `POST /screenshot`
- Azioni: `POST /navigate`, `POST /act`
- Hook: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- Download: `POST /download`, `POST /wait/download`
- Debug: `GET /console`, `POST /pdf`
- Debug: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- Rete: `POST /response/body`
- Stato: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- Stato: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- Impostazioni: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

Tutti gli endpoint accettano `?profile=<name>`.

Se è configurata l'auth gateway con secret condiviso, anche le route HTTP browser richiedono auth:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` oppure auth HTTP Basic con quella password

Note:

- Questa API browser loopback standalone **non** usa header di identità trusted-proxy o
  Tailscale Serve.
- Se `gateway.auth.mode` è `none` o `trusted-proxy`, queste route browser loopback
  non ereditano quelle modalità che trasportano identità; mantienile solo loopback.

### Contratto di errore di `/act`

`POST /act` usa una risposta di errore strutturata per errori di validazione a livello route e
fallimenti di policy:

```json
{ "error": "<message>", "code": "ACT_*" }
```

Valori `code` attuali:

- `ACT_KIND_REQUIRED` (HTTP 400): `kind` manca o non è riconosciuto.
- `ACT_INVALID_REQUEST` (HTTP 400): il payload dell'azione non ha superato normalizzazione o validazione.
- `ACT_SELECTOR_UNSUPPORTED` (HTTP 400): è stato usato `selector` con un tipo di azione non supportato.
- `ACT_EVALUATE_DISABLED` (HTTP 403): `evaluate` (o `wait --fn`) è disabilitato dalla configurazione.
- `ACT_TARGET_ID_MISMATCH` (HTTP 403): `targetId` di primo livello o in batch è in conflitto con il target della richiesta.
- `ACT_EXISTING_SESSION_UNSUPPORTED` (HTTP 501): l'azione non è supportata per i profili existing-session.

Altri errori runtime possono ancora restituire `{ "error": "<message>" }` senza un campo
`code`.

### Requisito Playwright

Alcune funzionalità (navigate/act/snapshot AI/snapshot role, screenshot di elementi,
PDF) richiedono Playwright. Se Playwright non è installato, quegli endpoint restituiscono
un chiaro errore 501.

Cosa funziona ancora senza Playwright:

- Snapshot ARIA
- Screenshot di pagina per il browser gestito `openclaw` quando è disponibile un WebSocket
  CDP per scheda
- Screenshot di pagina per i profili `existing-session` / Chrome MCP
- Screenshot existing-session basati su `--ref` dall'output snapshot

Cosa richiede ancora Playwright:

- `navigate`
- `act`
- snapshot AI / snapshot role
- screenshot di elementi con selettori CSS (`--element`)
- esportazione PDF completa del browser

Gli screenshot di elementi rifiutano anche `--full-page`; la route restituisce `fullPage is
not supported for element screenshots`.

Se vedi `Playwright is not available in this gateway build`, installa il pacchetto
completo Playwright (non `playwright-core`) e riavvia il gateway, oppure reinstalla
OpenClaw con supporto browser.

#### Installazione di Playwright in Docker

Se il tuo Gateway viene eseguito in Docker, evita `npx playwright` (conflitti con gli override npm).
Usa invece la CLI inclusa:

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

Per rendere persistenti i download del browser, imposta `PLAYWRIGHT_BROWSERS_PATH` (per esempio,
`/home/node/.cache/ms-playwright`) e assicurati che `/home/node` sia persistente tramite
`OPENCLAW_HOME_VOLUME` o un bind mount. Vedi [Docker](/it/install/docker).

## Come funziona (internamente)

Flusso di alto livello:

- Un piccolo **server di controllo** accetta richieste HTTP.
- Si collega ai browser basati su Chromium (Chrome/Brave/Edge/Chromium) tramite **CDP**.
- Per azioni avanzate (clic/digitazione/snapshot/PDF), usa **Playwright** sopra
  CDP.
- Quando Playwright manca, sono disponibili solo le operazioni che non dipendono da Playwright.

Questo design mantiene l'agente su un'interfaccia stabile e deterministica consentendoti
al tempo stesso di cambiare browser e profili locali/remoti.

## Riferimento rapido CLI

Tutti i comandi accettano `--browser-profile <name>` per puntare a un profilo specifico.
Tutti i comandi accettano anche `--json` per output leggibili da macchina (payload stabili).

Elementari:

- `openclaw browser status`
- `openclaw browser start`
- `openclaw browser stop`
- `openclaw browser tabs`
- `openclaw browser tab`
- `openclaw browser tab new`
- `openclaw browser tab select 2`
- `openclaw browser tab close 2`
- `openclaw browser open https://example.com`
- `openclaw browser focus abcd1234`
- `openclaw browser close abcd1234`

Ispezione:

- `openclaw browser screenshot`
- `openclaw browser screenshot --full-page`
- `openclaw browser screenshot --ref 12`
- `openclaw browser screenshot --ref e12`
- `openclaw browser snapshot`
- `openclaw browser snapshot --format aria --limit 200`
- `openclaw browser snapshot --interactive --compact --depth 6`
- `openclaw browser snapshot --efficient`
- `openclaw browser snapshot --labels`
- `openclaw browser snapshot --selector "#main" --interactive`
- `openclaw browser snapshot --frame "iframe#main" --interactive`
- `openclaw browser console --level error`

Nota sul ciclo di vita:

- Per i profili solo-attach e CDP remoti, `openclaw browser stop` è comunque il
  comando corretto di pulizia dopo i test. Chiude la sessione di controllo attiva e
  cancella gli override temporanei di emulazione invece di terminare il browser
  sottostante.
- `openclaw browser errors --clear`
- `openclaw browser requests --filter api --clear`
- `openclaw browser pdf`
- `openclaw browser responsebody "**/api" --max-chars 5000`

Azioni:

- `openclaw browser navigate https://example.com`
- `openclaw browser resize 1280 720`
- `openclaw browser click 12 --double`
- `openclaw browser click e12 --double`
- `openclaw browser type 23 "hello" --submit`
- `openclaw browser press Enter`
- `openclaw browser hover 44`
- `openclaw browser scrollintoview e12`
- `openclaw browser drag 10 11`
- `openclaw browser select 9 OptionA OptionB`
- `openclaw browser download e12 report.pdf`
- `openclaw browser waitfordownload report.pdf`
- `openclaw browser upload /tmp/openclaw/uploads/file.pdf`
- `openclaw browser fill --fields '[{"ref":"1","type":"text","value":"Ada"}]'`
- `openclaw browser dialog --accept`
- `openclaw browser wait --text "Done"`
- `openclaw browser wait "#main" --url "**/dash" --load networkidle --fn "window.ready===true"`
- `openclaw browser evaluate --fn '(el) => el.textContent' --ref 7`
- `openclaw browser highlight e12`
- `openclaw browser trace start`
- `openclaw browser trace stop`

Stato:

- `openclaw browser cookies`
- `openclaw browser cookies set session abc123 --url "https://example.com"`
- `openclaw browser cookies clear`
- `openclaw browser storage local get`
- `openclaw browser storage local set theme dark`
- `openclaw browser storage session clear`
- `openclaw browser set offline on`
- `openclaw browser set headers --headers-json '{"X-Debug":"1"}'`
- `openclaw browser set credentials user pass`
- `openclaw browser set credentials --clear`
- `openclaw browser set geo 37.7749 -122.4194 --origin "https://example.com"`
- `openclaw browser set geo --clear`
- `openclaw browser set media dark`
- `openclaw browser set timezone America/New_York`
- `openclaw browser set locale en-US`
- `openclaw browser set device "iPhone 14"`

Note:

- `upload` e `dialog` sono chiamate di **arming**; eseguirle prima del clic/pressione
  che attiva il file chooser/dialog.
- I percorsi di output di download e trace sono vincolati alle radici temporanee OpenClaw:
  - trace: `/tmp/openclaw` (fallback: `${os.tmpdir()}/openclaw`)
  - download: `/tmp/openclaw/downloads` (fallback: `${os.tmpdir()}/openclaw/downloads`)
- I percorsi di upload sono vincolati a una radice temporanea uploads di OpenClaw:
  - uploads: `/tmp/openclaw/uploads` (fallback: `${os.tmpdir()}/openclaw/uploads`)
- `upload` può anche impostare direttamente input file tramite `--input-ref` o `--element`.
- `snapshot`:
  - `--format ai` (predefinito quando Playwright è installato): restituisce uno snapshot AI con ref numerici (`aria-ref="<n>"`).
  - `--format aria`: restituisce l'albero di accessibilità (nessun ref; solo ispezione).
  - `--efficient` (o `--mode efficient`): preset compatto di role snapshot (interactive + compact + depth + maxChars inferiore).
  - Predefinito di configurazione (solo strumento/CLI): imposta `browser.snapshotDefaults.mode: "efficient"` per usare snapshot efficient quando il chiamante non passa una modalità (vedi [Configurazione Gateway](/it/gateway/configuration-reference#browser)).
  - Le opzioni di role snapshot (`--interactive`, `--compact`, `--depth`, `--selector`) forzano uno snapshot basato su ruoli con ref come `ref=e12`.
  - `--frame "<iframe selector>"` limita i role snapshot a un iframe (da usare insieme a ref di ruolo come `e12`).
  - `--interactive` produce un elenco piatto e facile da scegliere degli elementi interattivi (ideale per guidare le azioni).
  - `--labels` aggiunge uno screenshot della viewport con etichette ref sovrapposte (stampa `MEDIA:<path>`).
- `click`/`type`/ecc richiedono un `ref` da `snapshot` (numerico `12` o ref di ruolo `e12`).
  I selettori CSS non sono intenzionalmente supportati per le azioni.

## Snapshot e ref

OpenClaw supporta due stili di “snapshot”:

- **Snapshot AI (ref numerici)**: `openclaw browser snapshot` (predefinito; `--format ai`)
  - Output: uno snapshot testuale che include ref numerici.
  - Azioni: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Internamente, il ref viene risolto tramite `aria-ref` di Playwright.

- **Role snapshot (ref di ruolo come `e12`)**: `openclaw browser snapshot --interactive` (oppure `--compact`, `--depth`, `--selector`, `--frame`)
  - Output: un elenco/albero basato sui ruoli con `[ref=e12]` (e facoltativamente `[nth=1]`).
  - Azioni: `openclaw browser click e12`, `openclaw browser highlight e12`.
  - Internamente, il ref viene risolto tramite `getByRole(...)` (più `nth()` per i duplicati).
  - Aggiungi `--labels` per includere uno screenshot della viewport con etichette `e12` sovrapposte.

Comportamento dei ref:

- I ref **non sono stabili tra navigazioni**; se qualcosa fallisce, riesegui `snapshot` e usa un ref aggiornato.
- Se il role snapshot è stato acquisito con `--frame`, i ref di ruolo sono limitati a quell'iframe fino al role snapshot successivo.

## Potenziamenti di wait

Puoi aspettare più di semplice tempo/testo:

- Attendere un URL (glob supportati da Playwright):
  - `openclaw browser wait --url "**/dash"`
- Attendere uno stato di caricamento:
  - `openclaw browser wait --load networkidle`
- Attendere un predicato JS:
  - `openclaw browser wait --fn "window.ready===true"`
- Attendere che un selettore diventi visibile:
  - `openclaw browser wait "#main"`

Queste opzioni possono essere combinate:

```bash
openclaw browser wait "#main" \
  --url "**/dash" \
  --load networkidle \
  --fn "window.ready===true" \
  --timeout-ms 15000
```

## Flussi di debug

Quando un'azione fallisce (per es. “not visible”, “strict mode violation”, “covered”):

1. `openclaw browser snapshot --interactive`
2. Usa `click <ref>` / `type <ref>` (preferisci i ref di ruolo in modalità interactive)
3. Se fallisce ancora: `openclaw browser highlight <ref>` per vedere cosa Playwright sta puntando
4. Se la pagina si comporta in modo strano:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. Per un debug approfondito: registra una trace:
   - `openclaw browser trace start`
   - riproduci il problema
   - `openclaw browser trace stop` (stampa `TRACE:<path>`)

## Output JSON

`--json` serve per scripting e strumenti strutturati.

Esempi:

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

I role snapshot in JSON includono `refs` più un piccolo blocco `stats` (righe/caratteri/ref/interattivi) così gli strumenti possono ragionare su dimensione e densità del payload.

## Manopole di stato e ambiente

Sono utili per flussi del tipo “fai comportare il sito come X”:

- Cookie: `cookies`, `cookies set`, `cookies clear`
- Storage: `storage local|session get|set|clear`
- Offline: `set offline on|off`
- Header: `set headers --headers-json '{"X-Debug":"1"}'` (l'uso legacy `set headers --json '{"X-Debug":"1"}'` resta supportato)
- Auth HTTP Basic: `set credentials user pass` (oppure `--clear`)
- Geolocalizzazione: `set geo <lat> <lon> --origin "https://example.com"` (oppure `--clear`)
- Media: `set media dark|light|no-preference|none`
- Fuso orario / impostazioni locali: `set timezone ...`, `set locale ...`
- Dispositivo / viewport:
  - `set device "iPhone 14"` (preset dispositivo Playwright)
  - `set viewport 1280 720`

## Sicurezza e privacy

- Il profilo browser openclaw può contenere sessioni con accesso effettuato; trattalo come sensibile.
- `browser act kind=evaluate` / `openclaw browser evaluate` e `wait --fn`
  eseguono JavaScript arbitrario nel contesto della pagina. Il prompt injection può orientare
  questo comportamento. Disabilitalo con `browser.evaluateEnabled=false` se non ti serve.
- Per login e note anti-bot (X/Twitter, ecc.), vedi [Login browser + pubblicazione su X/Twitter](/it/tools/browser-login).
- Mantieni privati il Gateway/l'host del nodo (solo loopback o tailnet).
- Gli endpoint CDP remoti sono potenti; incanalali in tunnel e proteggili.

Esempio in modalità strict (blocca per impostazione predefinita destinazioni private/interne):

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"], // allow esatto facoltativo
    },
  },
}
```

## Risoluzione dei problemi

Per problemi specifici Linux (specialmente Chromium snap), vedi
[Risoluzione dei problemi del browser](/it/tools/browser-linux-troubleshooting).

Per configurazioni split-host WSL2 Gateway + Chrome Windows, vedi
[Risoluzione dei problemi WSL2 + Windows + remote Chrome CDP](/it/tools/browser-wsl2-windows-remote-cdp-troubleshooting).

## Strumenti dell'agente + funzionamento del controllo

L'agente ottiene **uno strumento** per l'automazione del browser:

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

Come viene mappato:

- `browser snapshot` restituisce un albero UI stabile (AI o ARIA).
- `browser act` usa gli ID `ref` di `snapshot` per fare clic/digitare/trascinare/selezionare.
- `browser screenshot` cattura i pixel (pagina intera o elemento).
- `browser` accetta:
  - `profile` per scegliere un profilo browser nominato (openclaw, chrome o remote CDP).
  - `target` (`sandbox` | `host` | `node`) per selezionare dove vive il browser.
  - Nelle sessioni sandboxed, `target: "host"` richiede `agents.defaults.sandbox.browser.allowHostControl=true`.
  - Se `target` è omesso: le sessioni sandboxed usano per impostazione predefinita `sandbox`, le sessioni non sandbox usano per impostazione predefinita `host`.
  - Se è connesso un nodo con capacità browser, lo strumento può instradarsi automaticamente verso di esso a meno che tu non fissi `target="host"` o `target="node"`.

Questo mantiene l'agente deterministico ed evita selettori fragili.

## Correlati

- [Panoramica degli strumenti](/it/tools) — tutti gli strumenti disponibili per l'agente
- [Sandboxing](/it/gateway/sandboxing) — controllo browser in ambienti sandboxed
- [Sicurezza](/it/gateway/security) — rischi e hardening del controllo browser
