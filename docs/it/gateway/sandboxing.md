---
read_when: You want a dedicated explanation of sandboxing or need to tune agents.defaults.sandbox.
status: active
summary: 'Come funziona il sandboxing di OpenClaw: modalità, ambiti, accesso all’area di lavoro e immagini'
title: Sandboxing
x-i18n:
    generated_at: "2026-04-14T02:08:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2573d0d7462f63a68eb1750e5432211522ff5b42989a17379d3e188468bbce52
    source_path: gateway/sandboxing.md
    workflow: 15
---

# Sandboxing

OpenClaw può eseguire **strumenti all’interno di backend sandbox** per ridurre il raggio d’impatto.
Questo è **opzionale** ed è controllato dalla configurazione (`agents.defaults.sandbox` o
`agents.list[].sandbox`). Se il sandboxing è disattivato, gli strumenti vengono eseguiti sull’host.
Il Gateway rimane sull’host; l’esecuzione degli strumenti avviene in una sandbox isolata
quando è abilitata.

Questa non è una barriera di sicurezza perfetta, ma limita in modo significativo l’accesso
al filesystem e ai processi quando il modello fa qualcosa di stupido.

## Cosa viene messo in sandbox

- Esecuzione degli strumenti (`exec`, `read`, `write`, `edit`, `apply_patch`, `process`, ecc.).
- Browser sandbox opzionale (`agents.defaults.sandbox.browser`).
  - Per impostazione predefinita, il browser della sandbox si avvia automaticamente (garantendo che il CDP sia raggiungibile) quando lo strumento browser ne ha bisogno.
    Configura tramite `agents.defaults.sandbox.browser.autoStart` e `agents.defaults.sandbox.browser.autoStartTimeoutMs`.
  - Per impostazione predefinita, i container del browser sandbox usano una rete Docker dedicata (`openclaw-sandbox-browser`) invece della rete globale `bridge`.
    Configura con `agents.defaults.sandbox.browser.network`.
  - Il valore facoltativo `agents.defaults.sandbox.browser.cdpSourceRange` limita l’ingresso CDP al bordo del container con una allowlist CIDR (ad esempio `172.21.0.1/32`).
  - L’accesso osservatore noVNC è protetto da password per impostazione predefinita; OpenClaw emette un URL con token a breve durata che serve una pagina bootstrap locale e apre noVNC con la password nel frammento dell’URL (non nei log di query/header).
  - `agents.defaults.sandbox.browser.allowHostControl` consente alle sessioni sandbox di puntare esplicitamente al browser dell’host.
  - Allowlist facoltative controllano `target: "custom"`: `allowedControlUrls`, `allowedControlHosts`, `allowedControlPorts`.

Non messi in sandbox:

- Il processo Gateway stesso.
- Qualsiasi strumento esplicitamente autorizzato a essere eseguito fuori dalla sandbox (ad esempio `tools.elevated`).
  - **L’exec elevato aggira il sandboxing e usa il percorso di escape configurato (`gateway` per impostazione predefinita, oppure `node` quando il target exec è `node`).**
  - Se il sandboxing è disattivato, `tools.elevated` non cambia l’esecuzione (già sull’host). Vedi [Elevated Mode](/it/tools/elevated).

## Modalità

`agents.defaults.sandbox.mode` controlla **quando** viene usato il sandboxing:

- `"off"`: nessun sandboxing.
- `"non-main"`: sandbox solo per le sessioni **non principali** (impostazione predefinita se vuoi le chat normali sull’host).
- `"all"`: ogni sessione viene eseguita in una sandbox.
  Nota: `"non-main"` si basa su `session.mainKey` (predefinito `"main"`), non sull’id dell’agente.
  Le sessioni di gruppo/canale usano le proprie chiavi, quindi vengono considerate non principali e saranno messe in sandbox.

## Ambito

`agents.defaults.sandbox.scope` controlla **quanti container** vengono creati:

- `"agent"` (predefinito): un container per agente.
- `"session"`: un container per sessione.
- `"shared"`: un container condiviso da tutte le sessioni sandbox.

## Backend

`agents.defaults.sandbox.backend` controlla **quale runtime** fornisce la sandbox:

- `"docker"` (predefinito): runtime sandbox locale basato su Docker.
- `"ssh"`: runtime sandbox remoto generico basato su SSH.
- `"openshell"`: runtime sandbox basato su OpenShell.

La configurazione specifica per SSH si trova in `agents.defaults.sandbox.ssh`.
La configurazione specifica per OpenShell si trova in `plugins.entries.openshell.config`.

### Scegliere un backend

|                     | Docker                           | SSH                            | OpenShell                                                    |
| ------------------- | -------------------------------- | ------------------------------ | ------------------------------------------------------------ |
| **Dove viene eseguito** | Container locale                 | Qualsiasi host accessibile via SSH | Sandbox gestita da OpenShell                                 |
| **Configurazione**  | `scripts/sandbox-setup.sh`       | Chiave SSH + host di destinazione | Plugin OpenShell abilitato                                   |
| **Modello workspace** | Bind-mount o copia               | Canonico remoto (seed una volta) | `mirror` o `remote`                                          |
| **Controllo rete**  | `docker.network` (predefinito: none) | Dipende dall’host remoto       | Dipende da OpenShell                                         |
| **Browser sandbox** | Supportato                       | Non supportato                 | Non ancora supportato                                        |
| **Bind mount**      | `docker.binds`                   | N/D                            | N/D                                                          |
| **Ideale per**      | Sviluppo locale, isolamento completo | Spostare il carico su una macchina remota | Sandbox remote gestite con sincronizzazione bidirezionale facoltativa |

### Backend Docker

Il backend Docker è il runtime predefinito, che esegue strumenti e browser sandbox localmente tramite il socket del demone Docker (`/var/run/docker.sock`). L’isolamento dei container sandbox è determinato dai namespace Docker.

**Vincoli Docker-out-of-Docker (DooD)**:
Se distribuisci il Gateway OpenClaw stesso come container Docker, esso orchestra container sandbox fratelli usando il socket Docker dell’host (DooD). Questo introduce un vincolo specifico di mappatura dei percorsi:

- **La configurazione richiede percorsi host**: la configurazione `workspace` in `openclaw.json` DEVE contenere il **percorso assoluto dell’host** (ad esempio `/home/user/.openclaw/workspaces`), non il percorso interno del container Gateway. Quando OpenClaw chiede al demone Docker di avviare una sandbox, il demone valuta i percorsi rispetto al namespace del sistema operativo host, non al namespace del Gateway.
- **Parità del bridge FS (mappa volumi identica)**: il processo nativo del Gateway OpenClaw scrive anche file heartbeat e bridge nella directory `workspace`. Poiché il Gateway valuta la stessa identica stringa (il percorso host) dall’interno del proprio ambiente containerizzato, la distribuzione del Gateway DEVE includere una mappa volumi identica che colleghi il namespace host in modo nativo (`-v /home/user/.openclaw:/home/user/.openclaw`).

Se mappi i percorsi internamente senza una parità assoluta con l’host, OpenClaw genera nativamente un errore di permesso `EACCES` quando tenta di scrivere il proprio heartbeat all’interno dell’ambiente del container, perché la stringa del percorso completamente qualificato non esiste in modo nativo.

### Backend SSH

Usa `backend: "ssh"` quando vuoi che OpenClaw isoli in sandbox `exec`, gli strumenti file e le letture dei media
su una macchina arbitraria accessibile via SSH.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "ssh",
        scope: "session",
        workspaceAccess: "rw",
        ssh: {
          target: "user@gateway-host:22",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // Oppure usa SecretRefs / contenuti inline invece di file locali:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
      },
    },
  },
}
```

Come funziona:

- OpenClaw crea una root remota per ambito sotto `sandbox.ssh.workspaceRoot`.
- Al primo utilizzo dopo la creazione o la ricreazione, OpenClaw inizializza quella workspace remota dalla workspace locale una sola volta.
- Dopo questo, `exec`, `read`, `write`, `edit`, `apply_patch`, le letture dei media nei prompt e la preparazione dei media in ingresso vengono eseguiti direttamente sulla workspace remota via SSH.
- OpenClaw non sincronizza automaticamente le modifiche remote di nuovo nella workspace locale.

Materiale di autenticazione:

- `identityFile`, `certificateFile`, `knownHostsFile`: usano file locali esistenti e li passano tramite la configurazione OpenSSH.
- `identityData`, `certificateData`, `knownHostsData`: usano stringhe inline o SecretRefs. OpenClaw li risolve tramite il normale snapshot runtime dei segreti, li scrive in file temporanei con `0600` e li elimina quando la sessione SSH termina.
- Se per lo stesso elemento sono impostati sia `*File` sia `*Data`, `*Data` ha priorità per quella sessione SSH.

Questo è un modello **remote-canonical**. Dopo il seed iniziale, la workspace SSH remota diventa il vero stato della sandbox.

Conseguenze importanti:

- Le modifiche locali sull’host effettuate fuori da OpenClaw dopo il passaggio di seed non sono visibili da remoto finché non ricrei la sandbox.
- `openclaw sandbox recreate` elimina la root remota per ambito e la inizializza di nuovo dalla copia locale al successivo utilizzo.
- Il browser sandbox non è supportato sul backend SSH.
- Le impostazioni `sandbox.docker.*` non si applicano al backend SSH.

### Backend OpenShell

Usa `backend: "openshell"` quando vuoi che OpenClaw isoli gli strumenti in
un ambiente remoto gestito da OpenShell. Per la guida completa all’installazione, il riferimento
di configurazione e il confronto tra le modalità workspace, vedi la
[pagina OpenShell](/it/gateway/openshell).

OpenShell riusa lo stesso trasporto SSH di base e lo stesso bridge del filesystem remoto del
backend SSH generico, e aggiunge il ciclo di vita specifico di OpenShell
(`sandbox create/get/delete`, `sandbox ssh-config`) più la modalità workspace
facoltativa `mirror`.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "openshell",
        scope: "session",
        workspaceAccess: "rw",
      },
    },
  },
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          from: "openclaw",
          mode: "remote", // mirror | remote
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
        },
      },
    },
  },
}
```

Modalità OpenShell:

- `mirror` (predefinita): la workspace locale rimane canonica. OpenClaw sincronizza i file locali in OpenShell prima di `exec` e sincronizza di nuovo la workspace remota dopo `exec`.
- `remote`: la workspace OpenShell diventa canonica dopo la creazione della sandbox. OpenClaw inizializza la workspace remota una sola volta dalla workspace locale, poi gli strumenti file e `exec` vengono eseguiti direttamente sulla sandbox remota senza sincronizzare indietro le modifiche.

Dettagli del trasporto remoto:

- OpenClaw chiede a OpenShell la configurazione SSH specifica della sandbox tramite `openshell sandbox ssh-config <name>`.
- Il core scrive quella configurazione SSH in un file temporaneo, apre la sessione SSH e riusa lo stesso bridge del filesystem remoto usato da `backend: "ssh"`.
- In modalità `mirror` cambia solo il ciclo di vita: sincronizzazione da locale a remoto prima di `exec`, poi sincronizzazione di ritorno dopo `exec`.

Limitazioni attuali di OpenShell:

- il browser sandbox non è ancora supportato
- `sandbox.docker.binds` non è supportato sul backend OpenShell
- i parametri runtime specifici di Docker sotto `sandbox.docker.*` continuano ad applicarsi solo al backend Docker

#### Modalità workspace

OpenShell ha due modelli di workspace. Questa è la parte che conta di più nella pratica.

##### `mirror`

Usa `plugins.entries.openshell.config.mode: "mirror"` quando vuoi che la **workspace locale rimanga canonica**.

Comportamento:

- Prima di `exec`, OpenClaw sincronizza la workspace locale nella sandbox OpenShell.
- Dopo `exec`, OpenClaw sincronizza la workspace remota di nuovo nella workspace locale.
- Gli strumenti file continuano a operare tramite il bridge della sandbox, ma la workspace locale rimane la fonte di verità tra un turno e l’altro.

Usa questa modalità quando:

- modifichi file localmente fuori da OpenClaw e vuoi che tali modifiche compaiano automaticamente nella sandbox
- vuoi che la sandbox OpenShell si comporti il più possibile come il backend Docker
- vuoi che la workspace host rifletta le scritture della sandbox dopo ogni turno `exec`

Compromesso:

- costo aggiuntivo di sincronizzazione prima e dopo `exec`

##### `remote`

Usa `plugins.entries.openshell.config.mode: "remote"` quando vuoi che la **workspace OpenShell diventi canonica**.

Comportamento:

- Quando la sandbox viene creata per la prima volta, OpenClaw inizializza la workspace remota dalla workspace locale una sola volta.
- Dopo questo, `exec`, `read`, `write`, `edit` e `apply_patch` operano direttamente sulla workspace OpenShell remota.
- OpenClaw **non** sincronizza le modifiche remote di nuovo nella workspace locale dopo `exec`.
- Le letture dei media in fase di prompt continuano a funzionare perché gli strumenti file e media leggono tramite il bridge della sandbox invece di assumere un percorso host locale.
- Il trasporto avviene via SSH nella sandbox OpenShell restituita da `openshell sandbox ssh-config`.

Conseguenze importanti:

- Se modifichi file sull’host fuori da OpenClaw dopo il passaggio di seed, la sandbox remota **non** vedrà automaticamente tali modifiche.
- Se la sandbox viene ricreata, la workspace remota viene inizializzata di nuovo dalla workspace locale.
- Con `scope: "agent"` o `scope: "shared"`, quella workspace remota viene condivisa a quello stesso ambito.

Usa questa modalità quando:

- la sandbox deve vivere principalmente sul lato remoto di OpenShell
- vuoi un overhead di sincronizzazione inferiore per turno
- non vuoi che modifiche locali sull’host sovrascrivano silenziosamente lo stato della sandbox remota

Scegli `mirror` se consideri la sandbox come un ambiente di esecuzione temporaneo.
Scegli `remote` se consideri la sandbox come la workspace reale.

#### Ciclo di vita di OpenShell

Le sandbox OpenShell sono ancora gestite tramite il normale ciclo di vita della sandbox:

- `openclaw sandbox list` mostra i runtime OpenShell oltre ai runtime Docker
- `openclaw sandbox recreate` elimina il runtime corrente e lascia che OpenClaw lo ricrei al successivo utilizzo
- anche la logica di prune è consapevole del backend

Per la modalità `remote`, la ricreazione è particolarmente importante:

- la ricreazione elimina la workspace remota canonica per quell’ambito
- al successivo utilizzo viene inizializzata una nuova workspace remota dalla workspace locale

Per la modalità `mirror`, la ricreazione reimposta principalmente l’ambiente di esecuzione remoto
perché la workspace locale rimane comunque canonica.

## Accesso alla workspace

`agents.defaults.sandbox.workspaceAccess` controlla **cosa la sandbox può vedere**:

- `"none"` (predefinito): gli strumenti vedono una workspace sandbox sotto `~/.openclaw/sandboxes`.
- `"ro"`: monta la workspace dell’agente in sola lettura su `/agent` (disabilita `write`/`edit`/`apply_patch`).
- `"rw"`: monta la workspace dell’agente in lettura/scrittura su `/workspace`.

Con il backend OpenShell:

- la modalità `mirror` continua a usare la workspace locale come sorgente canonica tra i turni `exec`
- la modalità `remote` usa la workspace remota OpenShell come sorgente canonica dopo il seed iniziale
- `workspaceAccess: "ro"` e `"none"` continuano a limitare il comportamento di scrittura nello stesso modo

I media in ingresso vengono copiati nella workspace della sandbox attiva (`media/inbound/*`).
Nota per le Skills: lo strumento `read` è radicato nella sandbox. Con `workspaceAccess: "none"`,
OpenClaw rispecchia le Skills idonee nella workspace della sandbox (`.../skills`) in modo
che possano essere lette. Con `"rw"`, le Skills della workspace sono leggibili da
`/workspace/skills`.

## Bind mount personalizzati

`agents.defaults.sandbox.docker.binds` monta directory host aggiuntive nel container.
Formato: `host:container:mode` (ad esempio `"/home/user/source:/source:rw"`).

I bind globali e per agente vengono **uniti** (non sostituiti). Con `scope: "shared"`, i bind per agente vengono ignorati.

`agents.defaults.sandbox.browser.binds` monta directory host aggiuntive solo nel container del **browser sandbox**.

- Quando è impostato (incluso `[]`), sostituisce `agents.defaults.sandbox.docker.binds` per il container browser.
- Quando è omesso, il container browser usa come fallback `agents.defaults.sandbox.docker.binds` (retrocompatibile).

Esempio (sorgente in sola lettura + una directory dati aggiuntiva):

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          binds: ["/home/user/source:/source:ro", "/var/data/myapp:/data:ro"],
        },
      },
    },
    list: [
      {
        id: "build",
        sandbox: {
          docker: {
            binds: ["/mnt/cache:/cache:rw"],
          },
        },
      },
    ],
  },
}
```

Note di sicurezza:

- I bind aggirano il filesystem sandbox: espongono percorsi host con la modalità che imposti (`:ro` o `:rw`).
- OpenClaw blocca sorgenti bind pericolose (ad esempio: `docker.sock`, `/etc`, `/proc`, `/sys`, `/dev` e mount genitori che le esporrebbero).
- OpenClaw blocca anche radici comuni di credenziali nella home directory come `~/.aws`, `~/.cargo`, `~/.config`, `~/.docker`, `~/.gnupg`, `~/.netrc`, `~/.npm` e `~/.ssh`.
- La validazione dei bind non si limita alla corrispondenza di stringhe. OpenClaw normalizza il percorso sorgente, poi lo risolve di nuovo tramite l’antenato esistente più profondo prima di ricontrollare i percorsi bloccati e le radici consentite.
- Ciò significa che anche le evasioni tramite symlink genitore falliscono in chiusura anche quando il nodo finale non esiste ancora. Esempio: `/workspace/run-link/new-file` viene comunque risolto come `/var/run/...` se `run-link` punta lì.
- Le radici sorgente consentite vengono canonicalizzate nello stesso modo, quindi un percorso che sembra rientrare nella allowlist solo prima della risoluzione dei symlink viene comunque rifiutato come `outside allowed roots`.
- I mount sensibili (segreti, chiavi SSH, credenziali di servizio) dovrebbero essere `:ro` salvo necessità assoluta.
- Combina con `workspaceAccess: "ro"` se ti serve solo accesso in lettura alla workspace; le modalità bind restano indipendenti.
- Vedi [Sandbox vs Tool Policy vs Elevated](/it/gateway/sandbox-vs-tool-policy-vs-elevated) per capire come i bind interagiscono con la policy degli strumenti e con exec elevato.

## Immagini + setup

Immagine Docker predefinita: `openclaw-sandbox:bookworm-slim`

Compilala una volta:

```bash
scripts/sandbox-setup.sh
```

Nota: l’immagine predefinita **non** include Node. Se una skill ha bisogno di Node (o
di altri runtime), o crei un’immagine personalizzata oppure installi tramite
`sandbox.docker.setupCommand` (richiede egress di rete + root scrivibile +
utente root).

Se vuoi un’immagine sandbox più funzionale con strumenti comuni (ad esempio
`curl`, `jq`, `nodejs`, `python3`, `git`), compila:

```bash
scripts/sandbox-common-setup.sh
```

Poi imposta `agents.defaults.sandbox.docker.image` su
`openclaw-sandbox-common:bookworm-slim`.

Immagine browser sandbox:

```bash
scripts/sandbox-browser-setup.sh
```

Per impostazione predefinita, i container sandbox Docker vengono eseguiti **senza rete**.
Sostituisci questo comportamento con `agents.defaults.sandbox.docker.network`.

L’immagine browser sandbox inclusa applica anche impostazioni predefinite conservative di avvio Chromium
per carichi di lavoro containerizzati. Le impostazioni predefinite correnti del container includono:

- `--remote-debugging-address=127.0.0.1`
- `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
- `--user-data-dir=${HOME}/.chrome`
- `--no-first-run`
- `--no-default-browser-check`
- `--disable-3d-apis`
- `--disable-gpu`
- `--disable-dev-shm-usage`
- `--disable-background-networking`
- `--disable-extensions`
- `--disable-features=TranslateUI`
- `--disable-breakpad`
- `--disable-crash-reporter`
- `--disable-software-rasterizer`
- `--no-zygote`
- `--metrics-recording-only`
- `--renderer-process-limit=2`
- `--no-sandbox` e `--disable-setuid-sandbox` quando `noSandbox` è abilitato.
- I tre flag di hardening grafico (`--disable-3d-apis`,
  `--disable-software-rasterizer`, `--disable-gpu`) sono facoltativi e sono utili
  quando i container non hanno supporto GPU. Imposta `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`
  se il tuo carico di lavoro richiede WebGL o altre funzionalità 3D/del browser.
- `--disable-extensions` è abilitato per impostazione predefinita e può essere disabilitato con
  `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` per flussi che dipendono da estensioni.
- `--renderer-process-limit=2` è controllato da
  `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`, dove `0` mantiene il valore predefinito di Chromium.

Se ti serve un profilo runtime diverso, usa un’immagine browser personalizzata e fornisci
il tuo entrypoint. Per profili Chromium locali (non containerizzati), usa
`browser.extraArgs` per aggiungere flag di avvio supplementari.

Impostazioni predefinite di sicurezza:

- `network: "host"` è bloccato.
- `network: "container:<id>"` è bloccato per impostazione predefinita (rischio di bypass tramite join del namespace).
- Override break-glass: `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`.

Le installazioni Docker e il gateway containerizzato si trovano qui:
[Docker](/it/install/docker)

Per le distribuzioni del Gateway Docker, `scripts/docker/setup.sh` può inizializzare la configurazione sandbox.
Imposta `OPENCLAW_SANDBOX=1` (o `true`/`yes`/`on`) per abilitare quel percorso. Puoi
sostituire il percorso del socket con `OPENCLAW_DOCKER_SOCKET`. Configurazione completa e riferimento
delle variabili d’ambiente: [Docker](/it/install/docker#agent-sandbox).

## setupCommand (configurazione container una tantum)

`setupCommand` viene eseguito **una sola volta** dopo la creazione del container sandbox (non a ogni esecuzione).
Viene eseguito all’interno del container tramite `sh -lc`.

Percorsi:

- Globale: `agents.defaults.sandbox.docker.setupCommand`
- Per agente: `agents.list[].sandbox.docker.setupCommand`

Problemi comuni:

- Il valore predefinito di `docker.network` è `"none"` (nessun egress), quindi le installazioni di pacchetti falliranno.
- `docker.network: "container:<id>"` richiede `dangerouslyAllowContainerNamespaceJoin: true` ed è solo break-glass.
- `readOnlyRoot: true` impedisce le scritture; imposta `readOnlyRoot: false` oppure crea un’immagine personalizzata.
- Per installare pacchetti `user` deve essere root (omettI `user` oppure imposta `user: "0:0"`).
- L’exec sandbox **non** eredita `process.env` dell’host. Usa
  `agents.defaults.sandbox.docker.env` (o un’immagine personalizzata) per le chiavi API delle skill.

## Policy degli strumenti + vie di fuga

Le policy allow/deny degli strumenti continuano ad applicarsi prima delle regole della sandbox. Se uno strumento è negato
globalmente o per agente, il sandboxing non lo ripristina.

`tools.elevated` è una via di fuga esplicita che esegue `exec` fuori dalla sandbox (`gateway` per impostazione predefinita, oppure `node` quando il target exec è `node`).
Le direttive `/exec` si applicano solo ai mittenti autorizzati e persistono per sessione; per disabilitare in modo permanente
`exec`, usa il deny della policy strumenti (vedi [Sandbox vs Tool Policy vs Elevated](/it/gateway/sandbox-vs-tool-policy-vs-elevated)).

Debug:

- Usa `openclaw sandbox explain` per ispezionare la modalità sandbox effettiva, la policy degli strumenti e le chiavi di configurazione per la correzione.
- Vedi [Sandbox vs Tool Policy vs Elevated](/it/gateway/sandbox-vs-tool-policy-vs-elevated) per il modello mentale del tipo “perché questo è bloccato?”.
  Mantienilo bloccato.

## Override multi-agent

Ogni agente può sovrascrivere sandbox + strumenti:
`agents.list[].sandbox` e `agents.list[].tools` (più `agents.list[].tools.sandbox.tools` per la policy degli strumenti sandbox).
Vedi [Multi-Agent Sandbox & Tools](/it/tools/multi-agent-sandbox-tools) per la precedenza.

## Esempio minimo di abilitazione

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
      },
    },
  },
}
```

## Documentazione correlata

- [OpenShell](/it/gateway/openshell) -- configurazione del backend sandbox gestito, modalità workspace e riferimento di configurazione
- [Sandbox Configuration](/it/gateway/configuration-reference#agentsdefaultssandbox)
- [Sandbox vs Tool Policy vs Elevated](/it/gateway/sandbox-vs-tool-policy-vs-elevated) -- debug di “perché questo è bloccato?”
- [Multi-Agent Sandbox & Tools](/it/tools/multi-agent-sandbox-tools) -- override per agente e precedenza
- [Security](/it/gateway/security)
