---
read_when:
    - Stai rispondendo a domande comuni su configurazione, installazione, onboarding o supporto di runtime
    - Stai eseguendo il triage di problemi segnalati dagli utenti prima di un debug più approfondito
summary: Domande frequenti su configurazione, impostazioni e utilizzo di OpenClaw
title: FAQ
x-i18n:
    generated_at: "2026-04-08T02:20:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 001b4605966b45b08108606f76ae937ec348c2179b04cf6fb34fef94833705e6
    source_path: help/faq.md
    workflow: 15
---

# FAQ

Risposte rapide più risoluzione dei problemi approfondita per configurazioni reali (sviluppo locale, VPS, multi-agent, OAuth/chiavi API, failover del modello). Per la diagnostica di runtime, vedi [Troubleshooting](/it/gateway/troubleshooting). Per il riferimento completo della configurazione, vedi [Configuration](/it/gateway/configuration).

## Primi 60 secondi se qualcosa non funziona

1. **Stato rapido (primo controllo)**

   ```bash
   openclaw status
   ```

   Riepilogo locale rapido: sistema operativo + aggiornamento, raggiungibilità del gateway/servizio, agenti/sessioni, configurazione provider + problemi di runtime (quando il gateway è raggiungibile).

2. **Report copiabile (sicuro da condividere)**

   ```bash
   openclaw status --all
   ```

   Diagnosi in sola lettura con coda dei log (token oscurati).

3. **Stato del demone + della porta**

   ```bash
   openclaw gateway status
   ```

   Mostra il runtime del supervisore rispetto alla raggiungibilità RPC, l'URL di destinazione del probe e quale configurazione probabilmente ha usato il servizio.

4. **Probe approfonditi**

   ```bash
   openclaw status --deep
   ```

   Esegue un probe live dello stato di salute del gateway, inclusi i probe dei canali quando supportati
   (richiede un gateway raggiungibile). Vedi [Health](/it/gateway/health).

5. **Segui l'ultimo log**

   ```bash
   openclaw logs --follow
   ```

   Se l'RPC non è disponibile, usa in alternativa:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   I log su file sono separati dai log del servizio; vedi [Logging](/it/logging) e [Troubleshooting](/it/gateway/troubleshooting).

6. **Esegui Doctor (riparazioni)**

   ```bash
   openclaw doctor
   ```

   Ripara/migra configurazione e stato + esegue controlli di salute. Vedi [Doctor](/it/gateway/doctor).

7. **Snapshot del gateway**

   ```bash
   openclaw health --json
   openclaw health --verbose   # mostra URL di destinazione + percorso della configurazione in caso di errori
   ```

   Chiede al gateway in esecuzione uno snapshot completo (solo WS). Vedi [Health](/it/gateway/health).

## Avvio rapido e configurazione iniziale

<AccordionGroup>
  <Accordion title="Sono bloccato, qual è il modo più veloce per sbloccarmi?">
    Usa un agente AI locale che possa **vedere la tua macchina**. È molto più efficace che chiedere
    su Discord, perché la maggior parte dei casi di "sono bloccato" sono **problemi locali di configurazione o ambiente** che
    gli aiutanti remoti non possono ispezionare.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Questi strumenti possono leggere il repo, eseguire comandi, ispezionare i log e aiutarti a correggere la configurazione
    della tua macchina (PATH, servizi, permessi, file di autenticazione). Fornisci loro il **checkout completo del codice sorgente** tramite
    l'installazione hackable (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Questo installa OpenClaw **da un checkout git**, in modo che l'agente possa leggere codice + documentazione e
    ragionare sulla versione esatta che stai eseguendo. Potrai sempre tornare alla versione stabile in seguito
    rieseguendo l'installer senza `--install-method git`.

    Suggerimento: chiedi all'agente di **pianificare e supervisionare** la correzione (passo per passo), poi esegui solo i
    comandi necessari. In questo modo le modifiche restano piccole e più facili da verificare.

    Se scopri un vero bug o una correzione, apri un issue su GitHub o invia una PR:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Inizia con questi comandi (condividi gli output quando chiedi aiuto):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Cosa fanno:

    - `openclaw status`: snapshot rapido dello stato del gateway/agente + configurazione di base.
    - `openclaw models status`: controlla l'autenticazione del provider + la disponibilità del modello.
    - `openclaw doctor`: convalida e ripara problemi comuni di configurazione/stato.

    Altri controlli utili della CLI: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Ciclo di debug rapido: [Primi 60 secondi se qualcosa non funziona](#primi-60-secondi-se-qualcosa-non-funziona).
    Documentazione di installazione: [Install](/it/install), [Installer flags](/it/install/installer), [Updating](/it/install/updating).

  </Accordion>

  <Accordion title="Heartbeat continua a saltare. Cosa significano i motivi di salto?">
    Motivi comuni per cui heartbeat viene saltato:

    - `quiet-hours`: fuori dalla finestra configurata delle ore attive
    - `empty-heartbeat-file`: `HEARTBEAT.md` esiste ma contiene solo uno scheletro vuoto o soltanto intestazioni
    - `no-tasks-due`: la modalità attività di `HEARTBEAT.md` è attiva ma nessuno degli intervalli delle attività è ancora scaduto
    - `alerts-disabled`: tutta la visibilità di heartbeat è disabilitata (`showOk`, `showAlerts` e `useIndicator` sono tutti disattivati)

    In modalità attività, i timestamp di scadenza vengono avanzati solo dopo che una vera esecuzione di heartbeat
    viene completata. Le esecuzioni saltate non contrassegnano le attività come completate.

    Documentazione: [Heartbeat](/it/gateway/heartbeat), [Automation & Tasks](/it/automation).

  </Accordion>

  <Accordion title="Modo consigliato per installare e configurare OpenClaw">
    Il repo consiglia di eseguire dal sorgente e usare l'onboarding:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    La procedura guidata può anche compilare automaticamente le risorse dell'interfaccia. Dopo l'onboarding, in genere il Gateway viene eseguito sulla porta **18789**.

    Dal sorgente (contributori/dev):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # installa automaticamente le dipendenze UI al primo avvio
    openclaw onboard
    ```

    Se non hai ancora un'installazione globale, eseguilo tramite `pnpm openclaw onboard`.

  </Accordion>

  <Accordion title="Come apro la dashboard dopo l'onboarding?">
    La procedura guidata apre il browser con un URL pulito della dashboard (senza token) subito dopo l'onboarding e stampa anche il link nel riepilogo. Tieni aperta quella scheda; se non si è avviata, copia/incolla l'URL stampato sulla stessa macchina.
  </Accordion>

  <Accordion title="Come autentico la dashboard su localhost rispetto a un host remoto?">
    **Localhost (stessa macchina):**

    - Apri `http://127.0.0.1:18789/`.
    - Se richiede l'autenticazione con segreto condiviso, incolla il token o la password configurati nelle impostazioni della Control UI.
    - Origine del token: `gateway.auth.token` (oppure `OPENCLAW_GATEWAY_TOKEN`).
    - Origine della password: `gateway.auth.password` (oppure `OPENCLAW_GATEWAY_PASSWORD`).
    - Se non è ancora configurato alcun segreto condiviso, genera un token con `openclaw doctor --generate-gateway-token`.

    **Non su localhost:**

    - **Tailscale Serve** (consigliato): mantieni il bind su loopback, esegui `openclaw gateway --tailscale serve`, apri `https://<magicdns>/`. Se `gateway.auth.allowTailscale` è `true`, gli header di identità soddisfano l'autenticazione di Control UI/WebSocket (senza incollare un segreto condiviso, assumendo un host gateway attendibile); le API HTTP richiedono comunque l'autenticazione con segreto condiviso a meno che tu non usi deliberatamente `none` con private-ingress o l'autenticazione HTTP trusted-proxy.
      I tentativi errati concorrenti di autenticazione Serve dallo stesso client vengono serializzati prima che il limiter delle autenticazioni fallite li registri, quindi il secondo tentativo errato può già mostrare `retry later`.
    - **Bind tailnet**: esegui `openclaw gateway --bind tailnet --token "<token>"` (oppure configura l'autenticazione con password), apri `http://<tailscale-ip>:18789/`, quindi incolla il segreto condiviso corrispondente nelle impostazioni della dashboard.
    - **Proxy inverso identity-aware**: mantieni il Gateway dietro un proxy attendibile non-loopback, configura `gateway.auth.mode: "trusted-proxy"`, quindi apri l'URL del proxy.
    - **Tunnel SSH**: `ssh -N -L 18789:127.0.0.1:18789 user@host` poi apri `http://127.0.0.1:18789/`. L'autenticazione con segreto condiviso si applica comunque attraverso il tunnel; se richiesto, incolla il token o la password configurati.

    Vedi [Dashboard](/web/dashboard) e [Web surfaces](/web) per i dettagli su modalità di bind e autenticazione.

  </Accordion>

  <Accordion title="Perché esistono due configurazioni di approvazione exec per le approvazioni in chat?">
    Controllano livelli diversi:

    - `approvals.exec`: inoltra le richieste di approvazione verso le destinazioni di chat
    - `channels.<channel>.execApprovals`: fa sì che quel canale agisca come client di approvazione nativo per le approvazioni exec

    La policy exec dell'host resta comunque il vero gate di approvazione. La configurazione della chat controlla solo dove compaiono
    le richieste di approvazione e come le persone possono rispondere.

    Nella maggior parte delle configurazioni **non** servono entrambe:

    - Se la chat supporta già comandi e risposte, `/approve` nella stessa chat funziona tramite il percorso condiviso.
    - Se un canale nativo supportato può dedurre in sicurezza chi approva, OpenClaw ora abilita automaticamente le approvazioni native con priorità ai DM quando `channels.<channel>.execApprovals.enabled` non è impostato o vale `"auto"`.
    - Quando sono disponibili card/pulsanti di approvazione nativi, quell'interfaccia nativa è il percorso principale; l'agente dovrebbe includere un comando manuale `/approve` solo se il risultato dello strumento indica che le approvazioni in chat non sono disponibili o che l'approvazione manuale è l'unico percorso.
    - Usa `approvals.exec` solo quando le richieste devono essere inoltrate anche ad altre chat o a stanze operative esplicite.
    - Usa `channels.<channel>.execApprovals.target: "channel"` o `"both"` solo quando vuoi esplicitamente che le richieste di approvazione vengano pubblicate di nuovo nella stanza/topic di origine.
    - Le approvazioni dei plugin sono ancora separate: usano per impostazione predefinita `/approve` nella stessa chat, un inoltro facoltativo `approvals.plugin`, e solo alcuni canali nativi mantengono sopra anche la gestione nativa delle approvazioni del plugin.

    In breve: l'inoltro serve per l'instradamento, la configurazione del client nativo serve per una UX più ricca specifica per canale.
    Vedi [Exec Approvals](/it/tools/exec-approvals).

  </Accordion>

  <Accordion title="Di quale runtime ho bisogno?">
    È richiesto Node **>= 22**. `pnpm` è consigliato. Bun **non è consigliato** per il Gateway.
  </Accordion>

  <Accordion title="Funziona su Raspberry Pi?">
    Sì. Il Gateway è leggero - la documentazione indica **512MB-1GB di RAM**, **1 core** e circa **500MB**
    di disco come sufficienti per uso personale, e nota che **Raspberry Pi 4 può eseguirlo**.

    Se vuoi un po' più di margine (log, media, altri servizi), **2GB sono consigliati**, ma
    non è un minimo rigido.

    Suggerimento: un piccolo Pi/VPS può ospitare il Gateway, e puoi abbinare **nodi** sul tuo laptop/telefono per
    schermo/fotocamera/canvas locali o esecuzione di comandi. Vedi [Nodes](/it/nodes).

  </Accordion>

  <Accordion title="Ci sono consigli per le installazioni su Raspberry Pi?">
    In breve: funziona, ma aspettati qualche asperità.

    - Usa un sistema operativo **64-bit** e mantieni Node >= 22.
    - Preferisci l'**installazione hackable (git)** in modo da poter vedere i log e aggiornare rapidamente.
    - Inizia senza canali/Skills, poi aggiungili uno alla volta.
    - Se incontri strani problemi binari, di solito è un problema di **compatibilità ARM**.

    Documentazione: [Linux](/it/platforms/linux), [Install](/it/install).

  </Accordion>

  <Accordion title="È bloccato su wake up my friend / l'onboarding non si schiude. E adesso?">
    Quella schermata dipende dal fatto che il Gateway sia raggiungibile e autenticato. La TUI invia anche
    "Wake up, my friend!" automaticamente alla prima schiusa. Se vedi quella riga con **nessuna risposta**
    e i token restano a 0, l'agente non è mai stato eseguito.

    1. Riavvia il Gateway:

    ```bash
    openclaw gateway restart
    ```

    2. Controlla stato + autenticazione:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Se continua a bloccarsi, esegui:

    ```bash
    openclaw doctor
    ```

    Se il Gateway è remoto, assicurati che il tunnel/la connessione Tailscale sia attiva e che l'interfaccia
    punti al Gateway corretto. Vedi [Remote access](/it/gateway/remote).

  </Accordion>

  <Accordion title="Posso migrare la mia configurazione su una nuova macchina (Mac mini) senza rifare l'onboarding?">
    Sì. Copia la **directory di stato** e il **workspace**, poi esegui Doctor una volta. Questo
    mantiene il tuo bot "esattamente uguale" (memoria, cronologia delle sessioni, autenticazione e
    stato dei canali) purché tu copi **entrambe** le posizioni:

    1. Installa OpenClaw sulla nuova macchina.
    2. Copia `$OPENCLAW_STATE_DIR` (predefinito: `~/.openclaw`) dalla vecchia macchina.
    3. Copia il tuo workspace (predefinito: `~/.openclaw/workspace`).
    4. Esegui `openclaw doctor` e riavvia il servizio Gateway.

    In questo modo preservi configurazione, profili di autenticazione, credenziali WhatsApp, sessioni e memoria. Se sei in
    modalità remota, ricorda che l'host gateway possiede l'archivio delle sessioni e il workspace.

    **Importante:** se fai commit/push solo del tuo workspace su GitHub, stai eseguendo il backup
    di **memoria + file bootstrap**, ma **non** della cronologia delle sessioni o dell'autenticazione. Questi elementi vivono
    sotto `~/.openclaw/` (ad esempio `~/.openclaw/agents/<agentId>/sessions/`).

    Correlati: [Migrating](/it/install/migrating), [Dove si trovano le cose sul disco](#dove-si-trovano-le-cose-sul-disco),
    [Agent workspace](/it/concepts/agent-workspace), [Doctor](/it/gateway/doctor),
    [Remote mode](/it/gateway/remote).

  </Accordion>

  <Accordion title="Dove vedo le novità dell'ultima versione?">
    Controlla il changelog su GitHub:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Le voci più recenti sono in alto. Se la sezione superiore è contrassegnata come **Unreleased**, la sezione successiva con data
    è l'ultima versione rilasciata. Le voci sono raggruppate in **Highlights**, **Changes** e
    **Fixes** (più sezioni docs/altre quando necessario).

  </Accordion>

  <Accordion title="Impossibile accedere a docs.openclaw.ai (errore SSL)">
    Alcune connessioni Comcast/Xfinity bloccano erroneamente `docs.openclaw.ai` tramite Xfinity
    Advanced Security. Disabilitalo oppure aggiungi `docs.openclaw.ai` alla allowlist, poi riprova.
    Aiutaci a sbloccarlo segnalando qui: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Se continui a non riuscire a raggiungere il sito, la documentazione è replicata su GitHub:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Differenza tra stable e beta">
    **Stable** e **beta** sono **npm dist-tag**, non linee di codice separate:

    - `latest` = stable
    - `beta` = build anticipata per test

    Di solito, una release stable arriva prima su **beta**, poi un passaggio esplicito
    di promozione sposta quella stessa versione su `latest`. I maintainer possono anche
    pubblicare direttamente su `latest` quando necessario. Per questo beta e stable possono
    puntare alla **stessa versione** dopo la promozione.

    Vedi cosa è cambiato:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Per i comandi di installazione in una riga e la differenza tra beta e dev, vedi l'accordion qui sotto.

  </Accordion>

  <Accordion title="Come installo la versione beta e qual è la differenza tra beta e dev?">
    **Beta** è il npm dist-tag `beta` (può coincidere con `latest` dopo la promozione).
    **Dev** è l'head mobile di `main` (git); quando viene pubblicato, usa il npm dist-tag `dev`.

    Comandi in una riga (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Installer per Windows (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Più dettagli: [Development channels](/it/install/development-channels) e [Installer flags](/it/install/installer).

  </Accordion>

  <Accordion title="Come provo le ultimissime novità?">
    Due opzioni:

    1. **Canale dev (checkout git):**

    ```bash
    openclaw update --channel dev
    ```

    Questo passa al branch `main` e aggiorna dal sorgente.

    2. **Installazione hackable (dal sito dell'installer):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Questo ti fornisce un repo locale che puoi modificare, poi aggiornare tramite git.

    Se preferisci un clone pulito manualmente, usa:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Documentazione: [Update](/cli/update), [Development channels](/it/install/development-channels),
    [Install](/it/install).

  </Accordion>

  <Accordion title="Quanto tempo richiedono di solito installazione e onboarding?">
    Indicazione approssimativa:

    - **Installazione:** 2-5 minuti
    - **Onboarding:** 5-15 minuti a seconda di quanti canali/modelli configuri

    Se si blocca, usa [Installer stuck](#avvio-rapido-e-configurazione-iniziale)
    e il ciclo di debug rapido in [Sono bloccato](#avvio-rapido-e-configurazione-iniziale).

  </Accordion>

  <Accordion title="L'installer è bloccato? Come posso ottenere più informazioni?">
    Riesegui l'installer con **output dettagliato**:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    Installazione beta con verbose:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    Per un'installazione hackable (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Equivalente Windows (PowerShell):

    ```powershell
    # install.ps1 non ha ancora un flag -Verbose dedicato.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    Più opzioni: [Installer flags](/it/install/installer).

  </Accordion>

  <Accordion title="L'installazione su Windows dice git not found oppure openclaw non riconosciuto">
    Due problemi comuni su Windows:

    **1) errore npm spawn git / git not found**

    - Installa **Git for Windows** e assicurati che `git` sia nel tuo PATH.
    - Chiudi e riapri PowerShell, poi riesegui l'installer.

    **2) openclaw non è riconosciuto dopo l'installazione**

    - La cartella bin globale di npm non è nel PATH.
    - Controlla il percorso:

      ```powershell
      npm config get prefix
      ```

    - Aggiungi quella directory al PATH utente (su Windows non serve il suffisso `\bin`; nella maggior parte dei sistemi è `%AppData%\npm`).
    - Chiudi e riapri PowerShell dopo aver aggiornato il PATH.

    Se vuoi la configurazione Windows più fluida, usa **WSL2** invece di Windows nativo.
    Documentazione: [Windows](/it/platforms/windows).

  </Accordion>

  <Accordion title="L'output exec su Windows mostra testo cinese illeggibile: cosa devo fare?">
    Di solito si tratta di una mancata corrispondenza della code page della console nelle shell Windows native.

    Sintomi:

    - l'output di `system.run`/`exec` mostra il cinese come testo corrotto
    - lo stesso comando appare correttamente in un altro profilo di terminale

    Soluzione rapida in PowerShell:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Quindi riavvia il Gateway e riprova il comando:

    ```powershell
    openclaw gateway restart
    ```

    Se riesci ancora a riprodurlo sull'ultima versione di OpenClaw, tieni traccia/segnalalo in:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="La documentazione non ha risposto alla mia domanda: come ottengo una risposta migliore?">
    Usa l'**installazione hackable (git)** in modo da avere localmente sorgente e documentazione completi, poi chiedi
    al tuo bot (o a Claude/Codex) _da quella cartella_ così potrà leggere il repo e rispondere con precisione.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Più dettagli: [Install](/it/install) e [Installer flags](/it/install/installer).

  </Accordion>

  <Accordion title="Come installo OpenClaw su Linux?">
    Risposta breve: segui la guida Linux, poi esegui l'onboarding.

    - Percorso rapido Linux + installazione del servizio: [Linux](/it/platforms/linux).
    - Procedura completa: [Getting Started](/it/start/getting-started).
    - Installer + aggiornamenti: [Install & updates](/it/install/updating).

  </Accordion>

  <Accordion title="Come installo OpenClaw su un VPS?">
    Qualsiasi VPS Linux funziona. Installa sul server, poi usa SSH/Tailscale per raggiungere il Gateway.

    Guide: [exe.dev](/it/install/exe-dev), [Hetzner](/it/install/hetzner), [Fly.io](/it/install/fly).
    Accesso remoto: [Gateway remote](/it/gateway/remote).

  </Accordion>

  <Accordion title="Dove si trovano le guide di installazione cloud/VPS?">
    Manteniamo un **hub di hosting** con i provider più comuni. Scegline uno e segui la guida:

    - [VPS hosting](/it/vps) (tutti i provider in un unico posto)
    - [Fly.io](/it/install/fly)
    - [Hetzner](/it/install/hetzner)
    - [exe.dev](/it/install/exe-dev)

    Come funziona nel cloud: il **Gateway gira sul server**, e vi accedi
    dal tuo laptop/telefono tramite la Control UI (oppure Tailscale/SSH). Il tuo stato + workspace
    vivono sul server, quindi considera l'host come fonte di verità e fai backup.

    Puoi abbinare **nodi** (Mac/iOS/Android/headless) a quel Gateway cloud per accedere a
    schermo/fotocamera/canvas locali o eseguire comandi sul tuo laptop mantenendo il
    Gateway nel cloud.

    Hub: [Platforms](/it/platforms). Accesso remoto: [Gateway remote](/it/gateway/remote).
    Nodi: [Nodes](/it/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Posso chiedere a OpenClaw di aggiornarsi da solo?">
    Risposta breve: **possibile, non consigliato**. Il flusso di aggiornamento può riavviare il
    Gateway (interrompendo la sessione attiva), potrebbe richiedere un checkout git pulito e
    può chiedere conferma. Più sicuro: eseguire gli aggiornamenti da una shell come operatore.

    Usa la CLI:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    Se devi automatizzarlo da un agente:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    Documentazione: [Update](/cli/update), [Updating](/it/install/updating).

  </Accordion>

  <Accordion title="Che cosa fa davvero l'onboarding?">
    `openclaw onboard` è il percorso di configurazione consigliato. In **modalità locale** ti guida attraverso:

    - **Configurazione del modello/autenticazione** (OAuth del provider, chiavi API, setup-token Anthropic, più opzioni di modello locale come LM Studio)
    - Posizione del **workspace** + file bootstrap
    - **Impostazioni del Gateway** (bind/porta/autenticazione/tailscale)
    - **Canali** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage, più plugin di canale bundled come QQ Bot)
    - **Installazione del demone** (LaunchAgent su macOS; unità systemd utente su Linux/WSL2)
    - **Controlli di salute** e selezione delle **Skills**

    Inoltre avvisa se il modello configurato è sconosciuto o se manca l'autenticazione.

  </Accordion>

  <Accordion title="Ho bisogno di un abbonamento Claude o OpenAI per eseguirlo?">
    No. Puoi eseguire OpenClaw con **chiavi API** (Anthropic/OpenAI/altri) oppure con
    **modelli solo locali** così i tuoi dati restano sul tuo dispositivo. Gli abbonamenti (Claude
    Pro/Max o OpenAI Codex) sono modi facoltativi per autenticare quei provider.

    Per Anthropic in OpenClaw, la distinzione pratica è:

    - **Chiave API Anthropic**: normale fatturazione API Anthropic
    - **Autenticazione Claude CLI / abbonamento Claude in OpenClaw**: il personale Anthropic
      ci ha detto che questo utilizzo è di nuovo consentito, e OpenClaw tratta l'uso di `claude -p`
      come autorizzato per questa integrazione a meno che Anthropic non pubblichi una nuova
      policy

    Per host gateway di lunga durata, le chiavi API Anthropic restano comunque la configurazione
    più prevedibile. OpenAI Codex OAuth è esplicitamente supportato per strumenti esterni come OpenClaw.

    OpenClaw supporta anche altre opzioni hosted in stile abbonamento tra cui
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan** e
    **Z.AI / GLM Coding Plan**.

    Documentazione: [Anthropic](/it/providers/anthropic), [OpenAI](/it/providers/openai),
    [Qwen Cloud](/it/providers/qwen),
    [MiniMax](/it/providers/minimax), [GLM Models](/it/providers/glm),
    [Local models](/it/gateway/local-models), [Models](/it/concepts/models).

  </Accordion>

  <Accordion title="Posso usare l'abbonamento Claude Max senza una chiave API?">
    Sì.

    Il personale Anthropic ci ha detto che l'uso in stile Claude CLI di OpenClaw è di nuovo consentito, quindi
    OpenClaw tratta l'autenticazione tramite abbonamento Claude e l'uso di `claude -p` come autorizzati
    per questa integrazione a meno che Anthropic non pubblichi una nuova policy. Se desideri
    la configurazione lato server più prevedibile, usa invece una chiave API Anthropic.

  </Accordion>

  <Accordion title="Supportate l'autenticazione con abbonamento Claude (Claude Pro o Max)?">
    Sì.

    Il personale Anthropic ci ha detto che questo utilizzo è di nuovo consentito, quindi OpenClaw tratta
    il riutilizzo di Claude CLI e l'uso di `claude -p` come autorizzati per questa integrazione
    a meno che Anthropic non pubblichi una nuova policy.

    Anthropic setup-token è ancora disponibile come percorso di token supportato da OpenClaw, ma OpenClaw ora preferisce il riutilizzo di Claude CLI e `claude -p` quando disponibili.
    Per carichi di lavoro di produzione o multiutente, l'autenticazione con chiave API Anthropic resta la
    scelta più sicura e prevedibile. Se desideri altre opzioni hosted in stile abbonamento
    in OpenClaw, vedi [OpenAI](/it/providers/openai), [Qwen / Model
    Cloud](/it/providers/qwen), [MiniMax](/it/providers/minimax), e [GLM
    Models](/it/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Perché vedo HTTP 429 rate_limit_error da Anthropic?">
Significa che la tua **quota/limite di velocità Anthropic** è esaurita per la finestra corrente. Se
usi **Claude CLI**, attendi il reset della finestra o aggiorna il tuo piano. Se
usi una **chiave API Anthropic**, controlla la Anthropic Console
per utilizzo/fatturazione e aumenta i limiti se necessario.

    Se il messaggio è specificamente:
    `Extra usage is required for long context requests`, la richiesta sta cercando di usare
    la beta di contesto 1M di Anthropic (`context1m: true`). Funziona solo quando la tua
    credenziale è idonea alla fatturazione long-context (fatturazione con chiave API o il
    percorso OpenClaw Claude-login con Extra Usage abilitato).

    Suggerimento: imposta un **modello di fallback** in modo che OpenClaw possa continuare a rispondere mentre un provider è soggetto a rate limit.
    Vedi [Models](/cli/models), [OAuth](/it/concepts/oauth), e
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/it/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="AWS Bedrock è supportato?">
    Sì. OpenClaw ha un provider bundled **Amazon Bedrock (Converse)**. Con i marker env AWS presenti, OpenClaw può auto-rilevare il catalogo Bedrock streaming/testo e unirlo come provider implicito `amazon-bedrock`; altrimenti puoi abilitare esplicitamente `plugins.entries.amazon-bedrock.config.discovery.enabled` o aggiungere una voce provider manuale. Vedi [Amazon Bedrock](/it/providers/bedrock) e [Model providers](/it/providers/models). Se preferisci un flusso di chiavi gestito, anche un proxy compatibile con OpenAI davanti a Bedrock è un'opzione valida.
  </Accordion>

  <Accordion title="Come funziona l'autenticazione di Codex?">
    OpenClaw supporta **OpenAI Code (Codex)** tramite OAuth (accesso ChatGPT). L'onboarding può eseguire il flusso OAuth e imposterà il modello predefinito su `openai-codex/gpt-5.4` quando appropriato. Vedi [Model providers](/it/concepts/model-providers) e [Onboarding (CLI)](/it/start/wizard).
  </Accordion>

  <Accordion title="Perché ChatGPT GPT-5.4 non sblocca openai/gpt-5.4 in OpenClaw?">
    OpenClaw tratta i due percorsi separatamente:

    - `openai-codex/gpt-5.4` = OAuth ChatGPT/Codex
    - `openai/gpt-5.4` = API diretta OpenAI Platform

    In OpenClaw, l'accesso ChatGPT/Codex è collegato al percorso `openai-codex/*`,
    non al percorso diretto `openai/*`. Se vuoi il percorso API diretto in
    OpenClaw, imposta `OPENAI_API_KEY` (o la configurazione equivalente del provider OpenAI).
    Se vuoi l'accesso ChatGPT/Codex in OpenClaw, usa `openai-codex/*`.

  </Accordion>

  <Accordion title="Perché i limiti di Codex OAuth possono differire da quelli del web ChatGPT?">
    `openai-codex/*` usa il percorso Codex OAuth, e le sue finestre di quota utilizzabili sono
    gestite da OpenAI e dipendono dal piano. In pratica, questi limiti possono differire dall'esperienza
    del sito/app ChatGPT, anche quando entrambi sono collegati allo stesso account.

    OpenClaw può mostrare le attuali finestre visibili di utilizzo/quota del provider in
    `openclaw models status`, ma non inventa né normalizza i diritti del web ChatGPT
    in accesso API diretto. Se vuoi il percorso diretto di
    fatturazione/limiti OpenAI Platform, usa `openai/*` con una chiave API.

  </Accordion>

  <Accordion title="Supportate l'autenticazione con abbonamento OpenAI (Codex OAuth)?">
    Sì. OpenClaw supporta pienamente **l'OAuth di abbonamento OpenAI Code (Codex)**.
    OpenAI consente esplicitamente l'uso dell'OAuth di abbonamento in strumenti/workflow esterni
    come OpenClaw. L'onboarding può eseguire per te il flusso OAuth.

    Vedi [OAuth](/it/concepts/oauth), [Model providers](/it/concepts/model-providers), e [Onboarding (CLI)](/it/start/wizard).

  </Accordion>

  <Accordion title="Come configuro Gemini CLI OAuth?">
    Gemini CLI usa un **flusso di autenticazione del plugin**, non un client id o secret in `openclaw.json`.

    Passaggi:

    1. Installa Gemini CLI localmente in modo che `gemini` sia nel `PATH`
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. Abilita il plugin: `openclaw plugins enable google`
    3. Accedi: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. Modello predefinito dopo l'accesso: `google-gemini-cli/gemini-3-flash-preview`
    5. Se le richieste falliscono, imposta `GOOGLE_CLOUD_PROJECT` o `GOOGLE_CLOUD_PROJECT_ID` sull'host gateway

    Questo memorizza i token OAuth nei profili di autenticazione sull'host gateway. Dettagli: [Model providers](/it/concepts/model-providers).

  </Accordion>

  <Accordion title="Un modello locale va bene per chat informali?">
    Di solito no. OpenClaw ha bisogno di un contesto ampio + una sicurezza forte; le schede piccole troncano il contesto e perdono in sicurezza. Se proprio devi, esegui la build di modello **più grande** che puoi in locale (LM Studio) e vedi [/gateway/local-models](/it/gateway/local-models). I modelli più piccoli/quantizzati aumentano il rischio di prompt injection - vedi [Security](/it/gateway/security).
  </Accordion>

  <Accordion title="Come faccio a mantenere il traffico dei modelli hosted in una regione specifica?">
    Scegli endpoint vincolati alla regione. OpenRouter espone opzioni ospitate negli Stati Uniti per MiniMax, Kimi e GLM; scegli la variante ospitata negli Stati Uniti per mantenere i dati nella regione. Puoi comunque elencare Anthropic/OpenAI insieme a queste usando `models.mode: "merge"` in modo che i fallback restino disponibili pur rispettando il provider regionale selezionato.
  </Accordion>

  <Accordion title="Devo comprare un Mac Mini per installarlo?">
    No. OpenClaw gira su macOS o Linux (Windows tramite WSL2). Un Mac mini è facoltativo - alcune persone
    ne comprano uno come host sempre acceso, ma anche un piccolo VPS, home server o macchina tipo Raspberry Pi va bene.

    Hai bisogno di un Mac **solo per strumenti esclusivi di macOS**. Per iMessage, usa [BlueBubbles](/it/channels/bluebubbles) (consigliato) - il server BlueBubbles gira su qualsiasi Mac, e il Gateway può girare su Linux o altrove. Se vuoi altri strumenti esclusivi di macOS, esegui il Gateway su un Mac o abbina un nodo macOS.

    Documentazione: [BlueBubbles](/it/channels/bluebubbles), [Nodes](/it/nodes), [Mac remote mode](/it/platforms/mac/remote).

  </Accordion>

  <Accordion title="Ho bisogno di un Mac mini per il supporto iMessage?">
    Hai bisogno di **qualche dispositivo macOS** con accesso a Messages. **Non** deve essere per forza un Mac mini -
    va bene qualsiasi Mac. **Usa [BlueBubbles](/it/channels/bluebubbles)** (consigliato) per iMessage - il server BlueBubbles gira su macOS, mentre il Gateway può girare su Linux o altrove.

    Configurazioni comuni:

    - Esegui il Gateway su Linux/VPS e il server BlueBubbles su qualsiasi Mac con accesso a Messages.
    - Esegui tutto sul Mac se vuoi la configurazione più semplice su una singola macchina.

    Documentazione: [BlueBubbles](/it/channels/bluebubbles), [Nodes](/it/nodes),
    [Mac remote mode](/it/platforms/mac/remote).

  </Accordion>

  <Accordion title="Se compro un Mac mini per eseguire OpenClaw, posso collegarlo al mio MacBook Pro?">
    Sì. Il **Mac mini può eseguire il Gateway** e il tuo MacBook Pro può collegarsi come
    **nodo** (dispositivo companion). I nodi non eseguono il Gateway - forniscono capacità aggiuntive
    come schermo/fotocamera/canvas e `system.run` su quel dispositivo.

    Schema comune:

    - Gateway sul Mac mini (sempre acceso).
    - Il MacBook Pro esegue l'app macOS o un host nodo e si abbina al Gateway.
    - Usa `openclaw nodes status` / `openclaw nodes list` per vederlo.

    Documentazione: [Nodes](/it/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Posso usare Bun?">
    Bun **non è consigliato**. Vediamo bug di runtime, soprattutto con WhatsApp e Telegram.
    Usa **Node** per gateway stabili.

    Se vuoi comunque sperimentare con Bun, fallo su un gateway non di produzione
    senza WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram: cosa va in allowFrom?">
    `channels.telegram.allowFrom` è **l'ID utente Telegram del mittente umano** (numerico). Non è lo username del bot.

    L'onboarding accetta l'input `@username` e lo risolve in un ID numerico, ma l'autorizzazione di OpenClaw usa solo ID numerici.

    Più sicuro (senza bot di terze parti):

    - Invia un DM al tuo bot, poi esegui `openclaw logs --follow` e leggi `from.id`.

    API ufficiale Bot:

    - Invia un DM al tuo bot, poi chiama `https://api.telegram.org/bot<bot_token>/getUpdates` e leggi `message.from.id`.

    Terze parti (meno privato):

    - Invia un DM a `@userinfobot` o `@getidsbot`.

    Vedi [/channels/telegram](/it/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Più persone possono usare un numero WhatsApp con istanze OpenClaw diverse?">
    Sì, tramite **multi-agent routing**. Collega il **DM** WhatsApp di ciascun mittente (peer `kind: "direct"`, mittente E.164 come `+15551234567`) a un diverso `agentId`, così ogni persona ottiene il proprio workspace e il proprio archivio sessioni. Le risposte continueranno comunque a provenire dallo **stesso account WhatsApp**, e il controllo d'accesso ai DM (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) è globale per account WhatsApp. Vedi [Multi-Agent Routing](/it/concepts/multi-agent) e [WhatsApp](/it/channels/whatsapp).
  </Accordion>

  <Accordion title='Posso eseguire un agente "fast chat" e un agente "Opus per coding"?'>
    Sì. Usa il multi-agent routing: assegna a ciascun agente il proprio modello predefinito, poi collega i percorsi in ingresso (account provider o peer specifici) a ciascun agente. Un esempio di configurazione si trova in [Multi-Agent Routing](/it/concepts/multi-agent). Vedi anche [Models](/it/concepts/models) e [Configuration](/it/gateway/configuration).
  </Accordion>

  <Accordion title="Homebrew funziona su Linux?">
    Sì. Homebrew supporta Linux (Linuxbrew). Configurazione rapida:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    Se esegui OpenClaw tramite systemd, assicurati che il PATH del servizio includa `/home/linuxbrew/.linuxbrew/bin` (o il tuo prefisso brew) in modo che gli strumenti installati con `brew` vengano risolti nelle shell non-login.
    Le build recenti inoltre antepongono le comuni directory bin dell'utente nei servizi Linux systemd (ad esempio `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) e rispettano `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR` e `FNM_DIR` quando impostati.

  </Accordion>

  <Accordion title="Differenza tra installazione git hackable e installazione npm">
    - **Installazione git hackable:** checkout completo del sorgente, modificabile, ideale per contributori.
      Esegui le build localmente e puoi correggere codice/documentazione.
    - **Installazione npm:** installazione globale della CLI, senza repo, ideale per "basta eseguirlo."
      Gli aggiornamenti arrivano dai npm dist-tag.

    Documentazione: [Getting started](/it/start/getting-started), [Updating](/it/install/updating).

  </Accordion>

  <Accordion title="Posso passare in seguito tra installazioni npm e git?">
    Sì. Installa l'altro tipo, poi esegui Doctor affinché il servizio gateway punti al nuovo entrypoint.
    Questo **non elimina i tuoi dati** - cambia solo l'installazione del codice OpenClaw. Il tuo stato
    (`~/.openclaw`) e il workspace (`~/.openclaw/workspace`) restano intatti.

    Da npm a git:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    Da git a npm:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor rileva una mancata corrispondenza dell'entrypoint del servizio gateway e si offre di riscrivere la configurazione del servizio per allinearla all'installazione corrente (usa `--repair` in automazione).

    Suggerimenti di backup: vedi [Strategia di backup](#dove-si-trovano-le-cose-sul-disco).

  </Accordion>

  <Accordion title="Dovrei eseguire il Gateway sul mio laptop o su un VPS?">
    Risposta breve: **se vuoi affidabilità 24/7, usa un VPS**. Se vuoi il
    minimo attrito e ti vanno bene sospensioni/riavvii, eseguilo in locale.

    **Laptop (Gateway locale)**

    - **Pro:** nessun costo di server, accesso diretto ai file locali, finestra del browser visibile.
    - **Contro:** sospensione/interruzioni di rete = disconnessioni, aggiornamenti/rivii del sistema operativo interrompono, deve restare sveglio.

    **VPS / cloud**

    - **Pro:** sempre acceso, rete stabile, nessun problema di sospensione del laptop, più facile da mantenere in esecuzione.
    - **Contro:** spesso eseguito headless (usa screenshot), accesso ai file solo remoto, devi usare SSH per gli aggiornamenti.

    **Nota specifica di OpenClaw:** WhatsApp/Telegram/Slack/Mattermost/Discord funzionano tutti bene da un VPS. L'unico vero compromesso è **browser headless** rispetto a una finestra visibile. Vedi [Browser](/it/tools/browser).

    **Impostazione predefinita consigliata:** VPS se in passato hai avuto disconnessioni del gateway. Il locale è ottimo quando stai usando attivamente il Mac e vuoi accesso ai file locali o automazione UI con un browser visibile.

  </Accordion>

  <Accordion title="Quanto è importante eseguire OpenClaw su una macchina dedicata?">
    Non è obbligatorio, ma **consigliato per affidabilità e isolamento**.

    - **Host dedicato (VPS/Mac mini/Pi):** sempre acceso, meno interruzioni per sospensione/riavvio, permessi più puliti, più facile mantenerlo in esecuzione.
    - **Laptop/desktop condiviso:** va benissimo per test e uso attivo, ma aspettati pause quando la macchina va in stop o si aggiorna.

    Se vuoi il meglio di entrambi i mondi, mantieni il Gateway su un host dedicato e abbina il tuo laptop come **nodo** per strumenti locali di schermo/fotocamera/exec. Vedi [Nodes](/it/nodes).
    Per indicazioni sulla sicurezza, leggi [Security](/it/gateway/security).

  </Accordion>

  <Accordion title="Quali sono i requisiti minimi per un VPS e il sistema operativo consigliato?">
    OpenClaw è leggero. Per un Gateway di base + un canale chat:

    - **Minimo assoluto:** 1 vCPU, 1GB di RAM, ~500MB di disco.
    - **Consigliato:** 1-2 vCPU, 2GB di RAM o più per margine (log, media, più canali). Gli strumenti nodo e l'automazione del browser possono richiedere molte risorse.

    Sistema operativo: usa **Ubuntu LTS** (o qualunque Debian/Ubuntu moderno). Il percorso di installazione Linux è testato meglio lì.

    Documentazione: [Linux](/it/platforms/linux), [VPS hosting](/it/vps).

  </Accordion>

  <Accordion title="Posso eseguire OpenClaw in una VM e quali sono i requisiti?">
    Sì. Tratta una VM come un VPS: deve essere sempre accesa, raggiungibile e avere abbastanza
    RAM per il Gateway e per gli eventuali canali che abiliti.

    Indicazioni di base:

    - **Minimo assoluto:** 1 vCPU, 1GB di RAM.
    - **Consigliato:** 2GB di RAM o più se esegui più canali, automazione del browser o strumenti media.
    - **Sistema operativo:** Ubuntu LTS o un altro Debian/Ubuntu moderno.

    Se sei su Windows, **WSL2 è la configurazione in stile VM più semplice** e offre la miglior
    compatibilità degli strumenti. Vedi [Windows](/it/platforms/windows), [VPS hosting](/it/vps).
    Se stai eseguendo macOS in una VM, vedi [macOS VM](/it/install/macos-vm).

  </Accordion>
</AccordionGroup>

## Cos'è OpenClaw?

<AccordionGroup>
  <Accordion title="Cos'è OpenClaw, in un paragrafo?">
    OpenClaw è un assistente AI personale che esegui sui tuoi dispositivi. Risponde sulle superfici di messaggistica che già usi (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat e plugin di canale bundled come QQ Bot) e può anche gestire voce + un Canvas live sulle piattaforme supportate. Il **Gateway** è il piano di controllo sempre attivo; l'assistente è il prodotto.
  </Accordion>

  <Accordion title="Proposta di valore">
    OpenClaw non è "solo un wrapper di Claude". È un **piano di controllo local-first** che ti consente di eseguire un
    assistente capace su **hardware tuo**, raggiungibile dalle app di chat che già usi, con
    sessioni stateful, memoria e strumenti, senza cedere il controllo dei tuoi workflow a un
    SaaS hosted.

    Punti salienti:

    - **I tuoi dispositivi, i tuoi dati:** esegui il Gateway dove vuoi (Mac, Linux, VPS) e mantieni
      locali workspace + cronologia delle sessioni.
    - **Canali reali, non una sandbox web:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage/ecc.,
      più voce mobile e Canvas sulle piattaforme supportate.
    - **Model-agnostic:** usa Anthropic, OpenAI, MiniMax, OpenRouter, ecc., con routing
      per agente e failover.
    - **Opzione solo locale:** esegui modelli locali così **tutti i dati possono restare sul tuo dispositivo** se vuoi.
    - **Multi-agent routing:** agenti separati per canale, account o attività, ciascuno con il proprio
      workspace e i propri valori predefiniti.
    - **Open source e modificabile:** ispeziona, estendi e fai self-host senza vendor lock-in.

    Documentazione: [Gateway](/it/gateway), [Channels](/it/channels), [Multi-agent](/it/concepts/multi-agent),
    [Memory](/it/concepts/memory).

  </Accordion>

  <Accordion title="L'ho appena configurato - cosa dovrei fare per prima cosa?">
    Buoni primi progetti:

    - Costruire un sito web (WordPress, Shopify o un semplice sito statico).
    - Prototipare un'app mobile (struttura, schermate, piano API).
    - Organizzare file e cartelle (pulizia, naming, etichette).
    - Collegare Gmail e automatizzare riepiloghi o follow up.

    Può gestire attività grandi, ma funziona meglio se le dividi in fasi e
    usi sub agent per lavoro in parallelo.

  </Accordion>

  <Accordion title="Quali sono i cinque casi d'uso quotidiani principali di OpenClaw?">
    I vantaggi quotidiani di solito sono:

    - **Briefing personali:** riepiloghi di inbox, calendario e notizie che ti interessano.
    - **Ricerca e stesura:** ricerche rapide, riepiloghi e prime bozze per email o documenti.
    - **Promemoria e follow up:** solleciti e checklist guidati da cron o heartbeat.
    - **Automazione del browser:** compilazione di moduli, raccolta dati e ripetizione di attività web.
    - **Coordinamento tra dispositivi:** invia un'attività dal telefono, lascia che il Gateway la esegua su un server e ricevi il risultato di nuovo in chat.

  </Accordion>

  <Accordion title="OpenClaw può aiutare con lead gen, outreach, ads e blog per un SaaS?">
    Sì per **ricerca, qualificazione e stesura**. Può analizzare siti, creare shortlist,
    riassumere potenziali clienti e scrivere bozze di outreach o copy per annunci.

    Per **outreach o campagne pubblicitarie**, mantieni una persona nel loop. Evita spam, rispetta
    le leggi locali e le policy delle piattaforme, e rivedi tutto prima che venga inviato.
    Il modello più sicuro è lasciare che OpenClaw prepari la bozza e che tu approvi.

    Documentazione: [Security](/it/gateway/security).

  </Accordion>

  <Accordion title="Quali sono i vantaggi rispetto a Claude Code per lo sviluppo web?">
    OpenClaw è un **assistente personale** e un livello di coordinamento, non un sostituto dell'IDE. Usa
    Claude Code o Codex per il ciclo di coding diretto più rapido dentro un repo. Usa OpenClaw quando
    vuoi memoria durevole, accesso cross-device e orchestrazione degli strumenti.

    Vantaggi:

    - **Memoria + workspace persistenti** tra sessioni
    - **Accesso multipiattaforma** (WhatsApp, Telegram, TUI, WebChat)
    - **Orchestrazione degli strumenti** (browser, file, scheduling, hook)
    - **Gateway sempre attivo** (eseguilo su un VPS, interagisci da ovunque)
    - **Nodi** per browser/schermo/fotocamera/exec locali

    Showcase: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills e automazione

<AccordionGroup>
  <Accordion title="Come personalizzo le Skills senza mantenere il repo sporco?">
    Usa override gestiti invece di modificare la copia del repo. Inserisci le tue modifiche in `~/.openclaw/skills/<name>/SKILL.md` (oppure aggiungi una cartella tramite `skills.load.extraDirs` in `~/.openclaw/openclaw.json`). La precedenza è `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs`, quindi gli override gestiti continuano a prevalere sulle Skills bundled senza toccare git. Se hai bisogno che la skill sia installata globalmente ma visibile solo ad alcuni agenti, mantieni la copia condivisa in `~/.openclaw/skills` e controlla la visibilità con `agents.defaults.skills` e `agents.list[].skills`. Solo le modifiche degne di upstream dovrebbero vivere nel repo ed essere inviate come PR.
  </Accordion>

  <Accordion title="Posso caricare Skills da una cartella personalizzata?">
    Sì. Aggiungi directory extra tramite `skills.load.extraDirs` in `~/.openclaw/openclaw.json` (precedenza più bassa). La precedenza predefinita è `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs`. `clawhub` installa in `./skills` per impostazione predefinita, che OpenClaw tratta come `<workspace>/skills` alla sessione successiva. Se la skill deve essere visibile solo a determinati agenti, abbinala a `agents.defaults.skills` o `agents.list[].skills`.
  </Accordion>

  <Accordion title="Come posso usare modelli diversi per attività diverse?">
    Oggi i modelli supportati sono:

    - **Cron jobs**: i job isolati possono impostare un override `model` per job.
    - **Sub-agents**: instrada le attività verso agenti separati con modelli predefiniti diversi.
    - **Cambio on-demand**: usa `/model` per cambiare il modello della sessione corrente in qualsiasi momento.

    Vedi [Cron jobs](/it/automation/cron-jobs), [Multi-Agent Routing](/it/concepts/multi-agent) e [Slash commands](/it/tools/slash-commands).

  </Accordion>

  <Accordion title="Il bot si blocca mentre svolge lavoro pesante. Come posso scaricarlo altrove?">
    Usa **sub-agents** per attività lunghe o parallele. I sub-agents vengono eseguiti nella propria sessione,
    restituiscono un riepilogo e mantengono reattiva la tua chat principale.

    Chiedi al tuo bot di "generare un sub-agent per questa attività" oppure usa `/subagents`.
    Usa `/status` in chat per vedere cosa sta facendo il Gateway in questo momento (e se è occupato).

    Suggerimento sui token: attività lunghe e sub-agents consumano entrambi token. Se il costo ti preoccupa, imposta un
    modello più economico per i sub-agents tramite `agents.defaults.subagents.model`.

    Documentazione: [Sub-agents](/it/tools/subagents), [Background Tasks](/it/automation/tasks).

  </Accordion>

  <Accordion title="Come funzionano le sessioni di subagent legate ai thread su Discord?">
    Usa i binding dei thread. Puoi collegare un thread Discord a un subagent o a una destinazione di sessione, in modo che i messaggi successivi in quel thread restino su quella sessione collegata.

    Flusso di base:

    - Genera con `sessions_spawn` usando `thread: true` (e facoltativamente `mode: "session"` per un follow-up persistente).
    - Oppure collega manualmente con `/focus <target>`.
    - Usa `/agents` per ispezionare lo stato del binding.
    - Usa `/session idle <duration|off>` e `/session max-age <duration|off>` per controllare l'auto-unfocus.
    - Usa `/unfocus` per scollegare il thread.

    Configurazione richiesta:

    - Valori predefiniti globali: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Override Discord: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Auto-bind alla generazione: imposta `channels.discord.threadBindings.spawnSubagentSessions: true`.

    Documentazione: [Sub-agents](/it/tools/subagents), [Discord](/it/channels/discord), [Configuration Reference](/it/gateway/configuration-reference), [Slash commands](/it/tools/slash-commands).

  </Accordion>

  <Accordion title="Un subagent ha terminato, ma l'aggiornamento di completamento è andato nel posto sbagliato o non è mai stato pubblicato. Cosa devo controllare?">
    Controlla prima il percorso del richiedente risolto:

    - La consegna del subagent in modalità completamento preferisce qualsiasi thread collegato o percorso di conversazione quando esiste.
    - Se l'origine del completamento riporta solo un canale, OpenClaw ricade sul percorso memorizzato della sessione del richiedente (`lastChannel` / `lastTo` / `lastAccountId`) così la consegna diretta può comunque riuscire.
    - Se non esiste né un percorso collegato né un percorso memorizzato utilizzabile, la consegna diretta può fallire e il risultato ripiega sulla consegna in coda alla sessione invece di pubblicare immediatamente in chat.
    - Destinazioni non valide o stale possono ancora forzare il fallback in coda o il fallimento finale della consegna.
    - Se l'ultima risposta visibile dell'assistente nel figlio è l'esatto token silenzioso `NO_REPLY` / `no_reply`, oppure esattamente `ANNOUNCE_SKIP`, OpenClaw sopprime intenzionalmente l'annuncio invece di pubblicare vecchi progressi stantii.
    - Se il figlio è andato in timeout dopo sole chiamate agli strumenti, l'annuncio può comprimere il tutto in un breve riepilogo dei progressi parziali invece di riprodurre l'output grezzo degli strumenti.

    Debug:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Documentazione: [Sub-agents](/it/tools/subagents), [Background Tasks](/it/automation/tasks), [Session Tools](/it/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron o i promemoria non si attivano. Cosa devo controllare?">
    Cron viene eseguito all'interno del processo Gateway. Se il Gateway non è in esecuzione continua,
    i job pianificati non verranno eseguiti.

    Checklist:

    - Conferma che cron sia abilitato (`cron.enabled`) e che `OPENCLAW_SKIP_CRON` non sia impostato.
    - Controlla che il Gateway sia in esecuzione 24/7 (senza stop/riavvii).
    - Verifica le impostazioni del fuso orario per il job (`--tz` rispetto al fuso orario dell'host).

    Debug:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Documentazione: [Cron jobs](/it/automation/cron-jobs), [Automation & Tasks](/it/automation).

  </Accordion>

  <Accordion title="Cron si è attivato, ma non è stato inviato nulla al canale. Perché?">
    Controlla prima la modalità di consegna:

    - `--no-deliver` / `delivery.mode: "none"` significa che non è previsto alcun messaggio esterno.
    - Destinazione di annuncio mancante o non valida (`channel` / `to`) significa che il runner ha saltato la consegna in uscita.
    - Errori di autenticazione del canale (`unauthorized`, `Forbidden`) significano che il runner ha provato a consegnare ma le credenziali lo hanno bloccato.
    - Un risultato isolato silenzioso (`NO_REPLY` / `no_reply` soltanto) viene trattato come intenzionalmente non consegnabile, quindi il runner sopprime anche la consegna di fallback in coda.

    Per i cron job isolati, il runner possiede la consegna finale. Ci si aspetta che l'agente
    restituisca un riepilogo in testo semplice che il runner invierà. `--no-deliver` mantiene
    quel risultato interno; non consente invece all'agente di inviare direttamente con lo
    strumento message.

    Debug:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Documentazione: [Cron jobs](/it/automation/cron-jobs), [Background Tasks](/it/automation/tasks).

  </Accordion>

  <Accordion title="Perché un'esecuzione cron isolata ha cambiato modello o ritentato una volta?">
    Di solito è il percorso live di cambio modello, non una schedulazione duplicata.

    Un cron isolato può persistere un handoff di modello a runtime e riprovare quando l'esecuzione attiva
    genera `LiveSessionModelSwitchError`. Il retry mantiene il provider/modello cambiato
    e, se il cambio includeva un nuovo override del profilo di autenticazione, cron
    persiste anche quello prima del retry.

    Regole di selezione correlate:

    - L'override del modello per l'hook Gmail vince per primo quando applicabile.
    - Poi il `model` per job.
    - Poi qualsiasi override del modello della cron-session memorizzato.
    - Poi la normale selezione del modello predefinito/dell'agente.

    Il ciclo di retry è limitato. Dopo il tentativo iniziale più 2 retry di cambio,
    cron interrompe invece di continuare all'infinito.

    Debug:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Documentazione: [Cron jobs](/it/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Come installo le Skills su Linux?">
    Usa i comandi nativi `openclaw skills` oppure inserisci le Skills nel tuo workspace. La UI delle Skills di macOS non è disponibile su Linux.
    Sfoglia le Skills su [https://clawhub.ai](https://clawhub.ai).

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    Il comando nativo `openclaw skills install` scrive nella directory `skills/`
    del workspace attivo. Installa la CLI separata `clawhub` solo se vuoi pubblicare o
    sincronizzare le tue Skills. Per installazioni condivise tra agenti, inserisci la skill in
    `~/.openclaw/skills` e usa `agents.defaults.skills` o
    `agents.list[].skills` se vuoi limitare quali agenti possono vederla.

  </Accordion>

  <Accordion title="OpenClaw può eseguire attività su pianificazione o continuamente in background?">
    Sì. Usa lo scheduler del Gateway:

    - **Cron jobs** per attività pianificate o ricorrenti (persistono tra riavvii).
    - **Heartbeat** per controlli periodici della "sessione principale".
    - **Job isolati** per agenti autonomi che pubblicano riepiloghi o consegnano alle chat.

    Documentazione: [Cron jobs](/it/automation/cron-jobs), [Automation & Tasks](/it/automation),
    [Heartbeat](/it/gateway/heartbeat).

  </Accordion>

  <Accordion title="Posso eseguire da Linux Skills Apple esclusive di macOS?">
    Non direttamente. Le Skills macOS sono regolate da `metadata.openclaw.os` più i binari richiesti, e le Skills appaiono nel prompt di sistema solo quando sono idonee sull'**host Gateway**. Su Linux, le Skills solo `darwin` (come `apple-notes`, `apple-reminders`, `things-mac`) non verranno caricate a meno che tu non sovrascriva il gate.

    Hai tre modelli supportati:

    **Opzione A - eseguire il Gateway su un Mac (più semplice).**
    Esegui il Gateway dove esistono i binari macOS, poi collegati da Linux in [modalità remota](#gateway-porte-già-in-esecuzione-e-modalità-remota) o tramite Tailscale. Le Skills vengono caricate normalmente perché l'host Gateway è macOS.

    **Opzione B - usare un nodo macOS (senza SSH).**
    Esegui il Gateway su Linux, abbina un nodo macOS (app menu bar) e imposta **Node Run Commands** su "Always Ask" o "Always Allow" sul Mac. OpenClaw può trattare le Skills solo macOS come idonee quando i binari richiesti esistono sul nodo. L'agente esegue quelle Skills tramite lo strumento `nodes`. Se scegli "Always Ask", approvare "Always Allow" nel prompt aggiunge quel comando alla allowlist.

    **Opzione C - fare proxy dei binari macOS via SSH (avanzato).**
    Mantieni il Gateway su Linux, ma fai sì che i binari CLI richiesti vengano risolti in wrapper SSH che girano su un Mac. Poi sovrascrivi la skill per consentire Linux così rimane idonea.

    1. Crea un wrapper SSH per il binario (esempio: `memo` per Apple Notes):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Inserisci il wrapper nel `PATH` sull'host Linux (ad esempio `~/bin/memo`).
    3. Sovrascrivi i metadati della skill (workspace o `~/.openclaw/skills`) per consentire Linux:

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Avvia una nuova sessione affinché lo snapshot delle Skills venga aggiornato.

  </Accordion>

  <Accordion title="Avete un'integrazione Notion o HeyGen?">
    Non built-in al momento.

    Opzioni:

    - **Skill / plugin personalizzato:** ideale per accesso API affidabile (sia Notion sia HeyGen hanno API).
    - **Automazione del browser:** funziona senza codice ma è più lenta e fragile.

    Se vuoi mantenere il contesto per cliente (workflow di agenzia), un modello semplice è:

    - Una pagina Notion per cliente (contesto + preferenze + lavoro attivo).
    - Chiedere all'agente di recuperare quella pagina all'inizio della sessione.

    Se vuoi un'integrazione nativa, apri una richiesta di funzionalità o crea una skill
    che usi quelle API.

    Installa le Skills:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Le installazioni native finiscono nella directory `skills/` del workspace attivo. Per Skills condivise tra agenti, posizionale in `~/.openclaw/skills/<name>/SKILL.md`. Se solo alcuni agenti devono vedere un'installazione condivisa, configura `agents.defaults.skills` o `agents.list[].skills`. Alcune Skills si aspettano binari installati tramite Homebrew; su Linux questo significa Linuxbrew (vedi la voce FAQ Homebrew Linux sopra). Vedi [Skills](/it/tools/skills), [Skills config](/it/tools/skills-config), e [ClawHub](/it/tools/clawhub).

  </Accordion>

  <Accordion title="Come uso il mio Chrome già autenticato con OpenClaw?">
    Usa il profilo browser built-in `user`, che si collega tramite Chrome DevTools MCP:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Se vuoi un nome personalizzato, crea un profilo MCP esplicito:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Questo percorso è locale all'host. Se il Gateway gira altrove, esegui un host nodo sulla macchina del browser oppure usa CDP remoto.

    Limiti attuali di `existing-session` / `user`:

    - le azioni si basano sui ref, non su selettori CSS
    - gli upload richiedono `ref` / `inputRef` e al momento supportano un file alla volta
    - `responsebody`, esportazione PDF, intercettazione dei download e azioni batch richiedono ancora un browser gestito o un profilo CDP raw

  </Accordion>
</AccordionGroup>

## Sandboxing e memoria

<AccordionGroup>
  <Accordion title="Esiste una documentazione dedicata al sandboxing?">
    Sì. Vedi [Sandboxing](/it/gateway/sandboxing). Per configurazioni specifiche Docker (gateway completo in Docker o immagini sandbox), vedi [Docker](/it/install/docker).
  </Accordion>

  <Accordion title="Docker sembra limitato - come abilito tutte le funzionalità?">
    L'immagine predefinita è orientata alla sicurezza e gira come utente `node`, quindi non
    include pacchetti di sistema, Homebrew o browser bundled. Per una configurazione più completa:

    - Rendi persistente `/home/node` con `OPENCLAW_HOME_VOLUME` così le cache sopravvivono.
    - Inserisci nell'immagine le dipendenze di sistema con `OPENCLAW_DOCKER_APT_PACKAGES`.
    - Installa i browser Playwright tramite la CLI bundled:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - Imposta `PLAYWRIGHT_BROWSERS_PATH` e assicurati che il percorso sia persistente.

    Documentazione: [Docker](/it/install/docker), [Browser](/it/tools/browser).

  </Accordion>

  <Accordion title="Posso mantenere i DM personali ma rendere pubblici/in sandbox i gruppi con un solo agente?">
    Sì - se il traffico privato è in **DM** e il traffico pubblico è in **gruppi**.

    Usa `agents.defaults.sandbox.mode: "non-main"` così le sessioni di gruppo/canale (chiavi non-main) girano in Docker, mentre la sessione DM principale resta sull'host. Poi limita quali strumenti sono disponibili nelle sessioni sandbox tramite `tools.sandbox.tools`.

    Procedura completa + esempio di configurazione: [Groups: personal DMs + public groups](/it/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Riferimento chiave della configurazione: [Gateway configuration](/it/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Come collego una cartella host alla sandbox?">
    Imposta `agents.defaults.sandbox.docker.binds` su `["host:path:mode"]` (ad es. `"/home/user/src:/src:ro"`). I bind globali + per-agente vengono uniti; i bind per-agente vengono ignorati quando `scope: "shared"`. Usa `:ro` per tutto ciò che è sensibile e ricorda che i bind aggirano i muri del filesystem della sandbox.

    OpenClaw convalida le sorgenti dei bind sia rispetto al percorso normalizzato sia al percorso canonico risolto attraverso l'antenato esistente più profondo. Ciò significa che le fughe tramite parent symlink falliscono comunque in modo chiuso anche quando l'ultimo segmento del percorso non esiste ancora, e i controlli delle radici consentite continuano ad applicarsi dopo la risoluzione dei symlink.

    Vedi [Sandboxing](/it/gateway/sandboxing#custom-bind-mounts) e [Sandbox vs Tool Policy vs Elevated](/it/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) per esempi e note sulla sicurezza.

  </Accordion>

  <Accordion title="Come funziona la memoria?">
    La memoria di OpenClaw è semplicemente costituita da file Markdown nel workspace dell'agente:

    - Note giornaliere in `memory/YYYY-MM-DD.md`
    - Note curate a lungo termine in `MEMORY.md` (solo sessioni principali/private)

    OpenClaw esegue anche un **silent pre-compaction memory flush** per ricordare al modello
    di scrivere note durevoli prima della compattazione automatica. Questo avviene solo quando il workspace
    è scrivibile (le sandbox in sola lettura lo saltano). Vedi [Memory](/it/concepts/memory).

  </Accordion>

  <Accordion title="La memoria continua a dimenticare cose. Come faccio a farle restare?">
    Chiedi al bot di **scrivere il fatto nella memoria**. Le note a lungo termine vanno in `MEMORY.md`,
    il contesto a breve termine in `memory/YYYY-MM-DD.md`.

    Questa è ancora un'area che stiamo migliorando. Aiuta ricordare al modello di archiviare memorie;
    saprà cosa fare. Se continua a dimenticare, verifica che il Gateway stia usando lo stesso
    workspace a ogni esecuzione.

    Documentazione: [Memory](/it/concepts/memory), [Agent workspace](/it/concepts/agent-workspace).

  </Accordion>

  <Accordion title="La memoria persiste per sempre? Quali sono i limiti?">
    I file di memoria vivono su disco e persistono finché non li elimini. Il limite è il tuo
    spazio di archiviazione, non il modello. Il **contesto di sessione** resta comunque limitato dalla finestra
    di contesto del modello, quindi conversazioni lunghe possono essere compattate o troncate. Per questo
    esiste la ricerca nella memoria: riporta nel contesto solo le parti rilevanti.

    Documentazione: [Memory](/it/concepts/memory), [Context](/it/concepts/context).

  </Accordion>

  <Accordion title="La ricerca semantica della memoria richiede una chiave API OpenAI?">
    Solo se usi **embedding OpenAI**. Codex OAuth copre chat/completions e
    **non** concede accesso agli embedding, quindi **accedere con Codex (OAuth o tramite
    login della Codex CLI)** non aiuta per la ricerca semantica della memoria. Gli embedding OpenAI
    richiedono comunque una vera chiave API (`OPENAI_API_KEY` o `models.providers.openai.apiKey`).

    Se non imposti esplicitamente un provider, OpenClaw seleziona automaticamente un provider quando
    riesce a risolvere una chiave API (profili auth, `models.providers.*.apiKey` o env var).
    Preferisce OpenAI se viene risolta una chiave OpenAI, altrimenti Gemini se viene risolta una chiave Gemini,
    poi Voyage, poi Mistral. Se nessuna chiave remota è disponibile, la ricerca nella memoria
    resta disabilitata finché non la configuri. Se hai configurato e reso disponibile un percorso di modello locale, OpenClaw
    preferisce `local`. Ollama è supportato quando imposti esplicitamente
    `memorySearch.provider = "ollama"`.

    Se preferisci restare in locale, imposta `memorySearch.provider = "local"` (e facoltativamente
    `memorySearch.fallback = "none"`). Se vuoi embedding Gemini, imposta
    `memorySearch.provider = "gemini"` e fornisci `GEMINI_API_KEY` (oppure
    `memorySearch.remote.apiKey`). Supportiamo modelli di embedding **OpenAI, Gemini, Voyage, Mistral, Ollama o local** -
    vedi [Memory](/it/concepts/memory) per i dettagli della configurazione.

  </Accordion>
</AccordionGroup>

## Dove si trovano le cose sul disco

<AccordionGroup>
  <Accordion title="Tutti i dati usati con OpenClaw vengono salvati localmente?">
    No - **lo stato di OpenClaw è locale**, ma **i servizi esterni vedono comunque ciò che invii loro**.

    - **Locale per impostazione predefinita:** sessioni, file di memoria, configurazione e workspace vivono sull'host Gateway
      (`~/.openclaw` + la tua directory workspace).
    - **Remoto per necessità:** i messaggi che invii ai provider di modelli (Anthropic/OpenAI/ecc.) vanno alle
      loro API, e le piattaforme di chat (WhatsApp/Telegram/Slack/ecc.) memorizzano i dati dei messaggi sui
      propri server.
    - **Sei tu a controllare l'impronta:** usare modelli locali mantiene i prompt sulla tua macchina, ma il
      traffico dei canali passa comunque dai server del canale.

    Correlati: [Agent workspace](/it/concepts/agent-workspace), [Memory](/it/concepts/memory).

  </Accordion>

  <Accordion title="Dove memorizza i dati OpenClaw?">
    Tutto vive sotto `$OPENCLAW_STATE_DIR` (predefinito: `~/.openclaw`):

    | Path                                                            | Scopo                                                              |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Configurazione principale (JSON5)                                  |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Importazione OAuth legacy (copiata nei profili auth al primo utilizzo) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Profili auth (OAuth, chiavi API e `keyRef`/`tokenRef` facoltativi) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | Payload segreto opzionale su file per provider `file` SecretRef    |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | File di compatibilità legacy (voci statiche `api_key` ripulite)    |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Stato provider (es. `whatsapp/<accountId>/creds.json`)             |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | Stato per agente (agentDir + sessioni)                             |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Cronologia e stato delle conversazioni (per agente)                |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Metadati delle sessioni (per agente)                               |

    Percorso legacy single-agent: `~/.openclaw/agent/*` (migrato da `openclaw doctor`).

    Il tuo **workspace** (`AGENTS.md`, file di memoria, Skills, ecc.) è separato ed è configurato tramite `agents.defaults.workspace` (predefinito: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="Dove dovrebbero trovarsi AGENTS.md / SOUL.md / USER.md / MEMORY.md?">
    Questi file vivono nel **workspace dell'agente**, non in `~/.openclaw`.

    - **Workspace (per agente)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (o il fallback legacy `memory.md` quando `MEMORY.md` è assente),
      `memory/YYYY-MM-DD.md`, `HEARTBEAT.md` facoltativo.
    - **Directory di stato (`~/.openclaw`)**: configurazione, stato dei canali/provider, profili auth, sessioni, log
      e Skills condivise (`~/.openclaw/skills`).

    Il workspace predefinito è `~/.openclaw/workspace`, configurabile tramite:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Se il bot "dimentica" dopo un riavvio, conferma che il Gateway stia usando lo stesso
    workspace a ogni avvio (e ricorda: la modalità remota usa il workspace dell'**host gateway**,
    non quello del tuo laptop locale).

    Suggerimento: se vuoi un comportamento o una preferenza duraturi, chiedi al bot di **scriverli in
    AGENTS.md o MEMORY.md** invece di affidarti alla cronologia della chat.

    Vedi [Agent workspace](/it/concepts/agent-workspace) e [Memory](/it/concepts/memory).

  </Accordion>

  <Accordion title="Strategia di backup consigliata">
    Metti il tuo **workspace dell'agente** in un repo git **privato** e fai il backup in un luogo
    privato (ad esempio GitHub privato). In questo modo acquisisci memoria + file AGENTS/SOUL/USER
    e puoi ripristinare in seguito la "mente" dell'assistente.

    **Non** fare commit di nulla sotto `~/.openclaw` (credenziali, sessioni, token o payload di segreti cifrati).
    Se hai bisogno di un ripristino completo, esegui backup separati sia del workspace sia della directory di stato
    (vedi la domanda sulla migrazione qui sopra).

    Documentazione: [Agent workspace](/it/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Come disinstallo completamente OpenClaw?">
    Vedi la guida dedicata: [Uninstall](/it/install/uninstall).
  </Accordion>

  <Accordion title="Gli agenti possono lavorare fuori dal workspace?">
    Sì. Il workspace è la **cwd predefinita** e l'ancora della memoria, non una sandbox rigida.
    I percorsi relativi vengono risolti all'interno del workspace, ma i percorsi assoluti possono accedere ad altre
    posizioni dell'host a meno che il sandboxing non sia abilitato. Se hai bisogno di isolamento, usa
    [`agents.defaults.sandbox`](/it/gateway/sandboxing) o impostazioni sandbox per agente. Se
    vuoi che un repo sia la directory di lavoro predefinita, imposta il `workspace`
    di quell'agente alla root del repo. Il repo OpenClaw è solo codice sorgente; tieni il
    workspace separato a meno che tu non voglia intenzionalmente far lavorare l'agente al suo interno.

    Esempio (repo come cwd predefinita):

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Modalità remota: dov'è l'archivio delle sessioni?">
    Lo stato delle sessioni è di proprietà dell'**host gateway**. Se sei in modalità remota, l'archivio delle sessioni che ti interessa è sulla macchina remota, non sul tuo laptop locale. Vedi [Session management](/it/concepts/session).
  </Accordion>
</AccordionGroup>

## Nozioni di base sulla configurazione

<AccordionGroup>
  <Accordion title="Che formato ha la configurazione? Dov'è?">
    OpenClaw legge una configurazione facoltativa **JSON5** da `$OPENCLAW_CONFIG_PATH` (predefinito: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Se il file manca, usa valori predefiniti ragionevolmente sicuri (incluso un workspace predefinito di `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='Ho impostato gateway.bind: "lan" (o "tailnet") e ora niente ascolta / la UI dice unauthorized'>
    I bind non-loopback **richiedono un percorso di autenticazione gateway valido**. In pratica significa:

    - autenticazione con segreto condiviso: token o password
    - `gateway.auth.mode: "trusted-proxy"` dietro un proxy inverso identity-aware non-loopback correttamente configurato

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    Note:

    - `gateway.remote.token` / `.password` **non** abilitano da soli l'autenticazione del gateway locale.
    - I percorsi di chiamata locale possono usare `gateway.remote.*` come fallback solo quando `gateway.auth.*` non è impostato.
    - Per l'autenticazione con password, imposta invece `gateway.auth.mode: "password"` più `gateway.auth.password` (oppure `OPENCLAW_GATEWAY_PASSWORD`).
    - Se `gateway.auth.token` / `gateway.auth.password` è configurato esplicitamente tramite SecretRef e non viene risolto, la risoluzione fallisce in modo chiuso (nessun fallback remoto che mascheri il problema).
    - Le configurazioni Control UI con segreto condiviso si autenticano tramite `connect.params.auth.token` o `connect.params.auth.password` (memorizzati nelle impostazioni dell'app/UI). Le modalità che trasmettono identità come Tailscale Serve o `trusted-proxy` usano invece gli header della richiesta. Evita di inserire segreti condivisi negli URL.
    - Con `gateway.auth.mode: "trusted-proxy"`, i proxy inversi loopback sullo stesso host **non** soddisfano comunque l'autenticazione trusted-proxy. Il trusted proxy deve essere una sorgente non-loopback configurata.

  </Accordion>

  <Accordion title="Perché adesso ho bisogno di un token anche su localhost?">
    OpenClaw impone l'autenticazione del gateway per impostazione predefinita, incluso loopback. Nel normale percorso predefinito questo significa autenticazione con token: se non è configurato alcun percorso auth esplicito, l'avvio del gateway risolve in modalità token e ne genera automaticamente uno, salvandolo in `gateway.auth.token`, quindi i **client WS locali devono autenticarsi**. Questo impedisce ad altri processi locali di chiamare il Gateway.

    Se preferisci un percorso auth diverso, puoi scegliere esplicitamente la modalità password (oppure, per proxy inversi identity-aware non-loopback, `trusted-proxy`). Se **vuoi davvero** il loopback aperto, imposta esplicitamente `gateway.auth.mode: "none"` nella tua configurazione. Doctor può generarti un token in qualsiasi momento: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Devo riavviare dopo aver modificato la configurazione?">
    Il Gateway osserva la configurazione e supporta l'hot-reload:

    - `gateway.reload.mode: "hybrid"` (predefinito): applica a caldo le modifiche sicure, riavvia per quelle critiche
    - Sono supportati anche `hot`, `restart`, `off`

  </Accordion>

  <Accordion title="Come disabilito i tagline divertenti della CLI?">
    Imposta `cli.banner.taglineMode` nella configurazione:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: nasconde il testo del tagline ma mantiene la riga del titolo/versione del banner.
    - `default`: usa ogni volta `All your chats, one OpenClaw.`.
    - `random`: tagline divertenti/stagionali a rotazione (comportamento predefinito).
    - Se non vuoi alcun banner, imposta l'env `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="Come abilito web search (e web fetch)?">
    `web_fetch` funziona senza chiave API. `web_search` dipende dal
    provider selezionato:

    - I provider basati su API come Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity e Tavily richiedono la normale configurazione della chiave API.
    - Ollama Web Search non richiede chiavi, ma usa l'host Ollama configurato e richiede `ollama signin`.
    - DuckDuckGo non richiede chiavi, ma è un'integrazione non ufficiale basata su HTML.
    - SearXNG non richiede chiavi/è self-hosted; configura `SEARXNG_BASE_URL` o `plugins.entries.searxng.config.webSearch.baseUrl`.

    **Consigliato:** esegui `openclaw configure --section web` e scegli un provider.
    Alternative tramite variabili d'ambiente:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` o `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, o `MINIMAX_API_KEY`
    - Perplexity: `PERPLEXITY_API_KEY` o `OPENROUTER_API_KEY`
    - SearXNG: `SEARXNG_BASE_URL`
    - Tavily: `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // facoltativo; ometti per il rilevamento automatico
            },
          },
        },
    }
    ```

    La configurazione specifica del provider per web-search ora si trova sotto `plugins.entries.<plugin>.config.webSearch.*`.
    I vecchi percorsi provider `tools.web.search.*` continuano temporaneamente a essere caricati per compatibilità, ma non dovrebbero essere usati per nuove configurazioni.
    La configurazione fallback di Firecrawl per web-fetch vive sotto `plugins.entries.firecrawl.config.webFetch.*`.

    Note:

    - Se usi allowlist, aggiungi `web_search`/`web_fetch`/`x_search` o `group:web`.
    - `web_fetch` è abilitato per impostazione predefinita (a meno che non venga esplicitamente disabilitato).
    - Se `tools.web.fetch.provider` viene omesso, OpenClaw rileva automaticamente il primo provider fallback di fetch pronto tra le credenziali disponibili. Oggi il provider bundled è Firecrawl.
    - I demoni leggono le env var da `~/.openclaw/.env` (o dall'ambiente del servizio).

    Documentazione: [Web tools](/it/tools/web).

  </Accordion>

  <Accordion title="config.apply ha cancellato la mia configurazione. Come recupero e come lo evito?">
    `config.apply` sostituisce l'**intera configurazione**. Se invii un oggetto parziale, tutto il resto
    viene rimosso.

    Recupero:

    - Ripristina da backup (git o una copia di `~/.openclaw/openclaw.json`).
    - Se non hai backup, riesegui `openclaw doctor` e riconfigura canali/modelli.
    - Se non te lo aspettavi, segnala un bug e includi l'ultima configurazione nota o qualunque backup.
    - Un agente di coding locale può spesso ricostruire una configurazione funzionante da log o cronologia.

    Evitalo:

    - Usa `openclaw config set` per piccole modifiche.
    - Usa `openclaw configure` per modifiche interattive.
    - Usa prima `config.schema.lookup` quando non sei sicuro di un percorso esatto o della forma di un campo; restituisce un nodo di schema superficiale più riepiloghi dei figli immediati per approfondire.
    - Usa `config.patch` per modifiche RPC parziali; riserva `config.apply` solo alla sostituzione completa della configurazione.
    - Se stai usando lo strumento `gateway` riservato al proprietario dall'interno di un'esecuzione di agente, continuerà a rifiutare le scritture su `tools.exec.ask` / `tools.exec.security` (incluse le vecchie alias `tools.bash.*` che vengono normalizzate agli stessi percorsi protetti di exec).

    Documentazione: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/it/gateway/doctor).

  </Accordion>

  <Accordion title="Come eseguo un Gateway centrale con worker specializzati su più dispositivi?">
    Il modello comune è **un Gateway** (ad es. Raspberry Pi) più **nodi** e **agenti**:

    - **Gateway (centrale):** possiede canali (Signal/WhatsApp), routing e sessioni.
    - **Nodi (dispositivi):** Mac/iOS/Android si collegano come periferiche ed espongono strumenti locali (`system.run`, `canvas`, `camera`).
    - **Agenti (worker):** cervelli/workspace separati per ruoli specializzati (es. "Hetzner ops", "Dati personali").
    - **Sub-agents:** avviano lavoro in background da un agente principale quando desideri parallelismo.
    - **TUI:** si collega al Gateway e cambia agenti/sessioni.

    Documentazione: [Nodes](/it/nodes), [Remote access](/it/gateway/remote), [Multi-Agent Routing](/it/concepts/multi-agent), [Sub-agents](/it/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="Il browser di OpenClaw può funzionare headless?">
    Sì. È un'opzione di configurazione:

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    Il valore predefinito è `false` (headful). La modalità headless ha più probabilità di attivare controlli anti-bot su alcuni siti. Vedi [Browser](/it/tools/browser).

    La modalità headless usa lo **stesso motore Chromium** e funziona per la maggior parte delle automazioni (moduli, clic, scraping, login). Le differenze principali:

    - Nessuna finestra del browser visibile (usa screenshot se hai bisogno di elementi visivi).
    - Alcuni siti sono più rigidi riguardo all'automazione in modalità headless (CAPTCHA, anti-bot).
      Ad esempio, X/Twitter spesso blocca le sessioni headless.

  </Accordion>

  <Accordion title="Come uso Brave per il controllo del browser?">
    Imposta `browser.executablePath` sul tuo binario Brave (o qualsiasi browser basato su Chromium) e riavvia il Gateway.
    Vedi gli esempi completi di configurazione in [Browser](/it/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Gateway remoti e nodi

<AccordionGroup>
  <Accordion title="Come si propagano i comandi tra Telegram, il gateway e i nodi?">
    I messaggi Telegram sono gestiti dal **gateway**. Il gateway esegue l'agente e
    solo dopo chiama i nodi tramite il **Gateway WebSocket** quando serve uno strumento nodo:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    I nodi non vedono il traffico provider in ingresso; ricevono solo chiamate RPC dei nodi.

  </Accordion>

  <Accordion title="Come può il mio agente accedere al mio computer se il Gateway è ospitato da remoto?">
    Risposta breve: **abbina il tuo computer come nodo**. Il Gateway gira altrove, ma può
    chiamare strumenti `node.*` (schermo, fotocamera, sistema) sulla tua macchina locale tramite il Gateway WebSocket.

    Configurazione tipica:

    1. Esegui il Gateway sull'host sempre acceso (VPS/home server).
    2. Metti l'host Gateway + il tuo computer sulla stessa tailnet.
    3. Assicurati che il Gateway WS sia raggiungibile (bind tailnet o tunnel SSH).
    4. Apri localmente l'app macOS e collegati in modalità **Remote over SSH** (o tailnet diretta)
       così può registrarsi come nodo.
    5. Approva il nodo sul Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Non è richiesto alcun bridge TCP separato; i nodi si collegano tramite il Gateway WebSocket.

    Promemoria di sicurezza: abbinare un nodo macOS consente `system.run` su quella macchina. Abbina
    solo dispositivi di cui ti fidi e leggi [Security](/it/gateway/security).

    Documentazione: [Nodes](/it/nodes), [Gateway protocol](/it/gateway/protocol), [macOS remote mode](/it/platforms/mac/remote), [Security](/it/gateway/security).

  </Accordion>

  <Accordion title="Tailscale è connesso ma non ricevo risposte. E adesso?">
    Controlla le basi:

    - Gateway in esecuzione: `openclaw gateway status`
    - Stato di salute del Gateway: `openclaw status`
    - Stato di salute dei canali: `openclaw channels status`

    Poi verifica autenticazione e routing:

    - Se usi Tailscale Serve, assicurati che `gateway.auth.allowTailscale` sia impostato correttamente.
    - Se ti connetti tramite tunnel SSH, conferma che il tunnel locale sia attivo e punti alla porta corretta.
    - Conferma che le tue allowlist (DM o gruppo) includano il tuo account.

    Documentazione: [Tailscale](/it/gateway/tailscale), [Remote access](/it/gateway/remote), [Channels](/it/channels).

  </Accordion>

  <Accordion title="Due istanze OpenClaw possono parlare tra loro (locale + VPS)?">
    Sì. Non esiste un bridge built-in "bot-to-bot", ma puoi collegarlo in alcuni
    modi affidabili:

    **Più semplice:** usa un normale canale chat a cui entrambi i bot possono accedere (Telegram/Slack/WhatsApp).
    Fai inviare al Bot A un messaggio al Bot B, poi lascia che il Bot B risponda normalmente.

    **Bridge CLI (generico):** esegui uno script che chiama l'altro Gateway con
    `openclaw agent --message ... --deliver`, puntando a una chat dove l'altro bot
    ascolta. Se un bot si trova su un VPS remoto, punta la tua CLI a quel Gateway remoto
    tramite SSH/Tailscale (vedi [Remote access](/it/gateway/remote)).

    Modello di esempio (eseguito da una macchina che può raggiungere il Gateway di destinazione):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    Suggerimento: aggiungi una guardrail in modo che i due bot non entrino in un loop infinito (solo menzione,
    allowlist del canale, o una regola "non rispondere ai messaggi dei bot").

    Documentazione: [Remote access](/it/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/it/tools/agent-send).

  </Accordion>

  <Accordion title="Ho bisogno di VPS separati per più agenti?">
    No. Un Gateway può ospitare più agenti, ciascuno con il proprio workspace, i propri modelli predefiniti
    e il proprio routing. È la configurazione normale ed è molto più economica e semplice che eseguire
    un VPS per agente.

    Usa VPS separati solo quando hai bisogno di isolamento rigido (confini di sicurezza) o di
    configurazioni molto diverse che non vuoi condividere. Altrimenti, mantieni un solo Gateway e
    usa più agenti o sub-agents.

  </Accordion>

  <Accordion title="C'è un vantaggio nell'usare un nodo sul mio laptop personale invece di SSH da un VPS?">
    Sì - i nodi sono il modo di prima classe per raggiungere il tuo laptop da un Gateway remoto, e
    sbloccano più del semplice accesso shell. Il Gateway gira su macOS/Linux (Windows via WSL2) ed è
    leggero (va bene un piccolo VPS o una macchina tipo Raspberry Pi; 4 GB di RAM bastano), quindi una configurazione
    comune è un host sempre acceso più il tuo laptop come nodo.

    - **Nessun SSH in ingresso richiesto.** I nodi si collegano verso l'esterno al Gateway WebSocket e usano il pairing dei dispositivi.
    - **Controlli di esecuzione più sicuri.** `system.run` è protetto da allowlist/approvazioni del nodo su quel laptop.
    - **Più strumenti del dispositivo.** I nodi espongono `canvas`, `camera` e `screen` oltre a `system.run`.
    - **Automazione del browser locale.** Mantieni il Gateway su un VPS, ma esegui Chrome localmente tramite un host nodo sul laptop, o collegati a Chrome locale sull'host tramite Chrome MCP.

    SSH va bene per accesso shell ad hoc, ma i nodi sono più semplici per workflow continui dell'agente e
    automazione del dispositivo.

    Documentazione: [Nodes](/it/nodes), [Nodes CLI](/cli/nodes), [Browser](/it/tools/browser).

  </Accordion>

  <Accordion title="I nodi eseguono un servizio gateway?">
    No. Solo **un gateway** dovrebbe essere eseguito per host, a meno che tu non esegua intenzionalmente profili isolati (vedi [Multiple gateways](/it/gateway/multiple-gateways)). I nodi sono periferiche che si collegano
    al gateway (nodi iOS/Android o "node mode" macOS nell'app menu bar). Per host nodo headless e controllo CLI, vedi [Node host CLI](/cli/node).

    Per le modifiche a `gateway`, `discovery` e `canvasHost` è richiesto un riavvio completo.

  </Accordion>

  <Accordion title="Esiste un modo API / RPC per applicare la configurazione?">
    Sì.

    - `config.schema.lookup`: ispeziona un sottoalbero di configurazione con il relativo nodo di schema superficiale, il suggerimento UI corrispondente e i riepiloghi dei figli immediati prima di scrivere
    - `config.get`: recupera lo snapshot corrente + hash
    - `config.patch`: aggiornamento parziale sicuro (preferito per la maggior parte delle modifiche RPC); ricarica a caldo quando possibile e riavvia quando necessario
    - `config.apply`: convalida + sostituisce l'intera configurazione; ricarica a caldo quando possibile e riavvia quando necessario
    - Lo strumento runtime `gateway` riservato al proprietario continua a rifiutare la riscrittura di `tools.exec.ask` / `tools.exec.security`; le vecchie alias `tools.bash.*` vengono normalizzate agli stessi percorsi protetti di exec

  </Accordion>

  <Accordion title="Configurazione minima sensata per una prima installazione">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    Questo imposta il tuo workspace e limita chi può attivare il bot.

  </Accordion>

  <Accordion title="Come configuro Tailscale su un VPS e mi collego dal mio Mac?">
    Passaggi minimi:

    1. **Installa + accedi sul VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Installa + accedi sul tuo Mac**
       - Usa l'app Tailscale e accedi alla stessa tailnet.
    3. **Abilita MagicDNS (consigliato)**
       - Nella console amministrativa Tailscale, abilita MagicDNS in modo che il VPS abbia un nome stabile.
    4. **Usa il nome host tailnet**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    Se vuoi la Control UI senza SSH, usa Tailscale Serve sul VPS:

    ```bash
    openclaw gateway --tailscale serve
    ```

    Questo mantiene il gateway collegato a loopback ed espone HTTPS tramite Tailscale. Vedi [Tailscale](/it/gateway/tailscale).

  </Accordion>

  <Accordion title="Come collego un nodo Mac a un Gateway remoto (Tailscale Serve)?">
    Serve espone la **Gateway Control UI + WS**. I nodi si collegano tramite lo stesso endpoint Gateway WS.

    Configurazione consigliata:

    1. **Assicurati che VPS + Mac siano sulla stessa tailnet**.
    2. **Usa l'app macOS in modalità Remote** (la destinazione SSH può essere il nome host tailnet).
       L'app aprirà un tunnel sulla porta del Gateway e si collegherà come nodo.
    3. **Approva il nodo** sul gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Documentazione: [Gateway protocol](/it/gateway/protocol), [Discovery](/it/gateway/discovery), [macOS remote mode](/it/platforms/mac/remote).

  </Accordion>

  <Accordion title="Dovrei installare su un secondo laptop o semplicemente aggiungere un nodo?">
    Se ti servono solo **strumenti locali** (schermo/fotocamera/exec) sul secondo laptop, aggiungilo come
    **nodo**. In questo modo mantieni un solo Gateway ed eviti configurazioni duplicate. Gli strumenti nodo locali sono
    attualmente solo macOS, ma prevediamo di estenderli ad altri sistemi operativi.

    Installa un secondo Gateway solo quando hai bisogno di **isolamento rigido** o di due bot completamente separati.

    Documentazione: [Nodes](/it/nodes), [Nodes CLI](/cli/nodes), [Multiple gateways](/it/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Variabili d'ambiente e caricamento .env

<AccordionGroup>
  <Accordion title="Come carica OpenClaw le variabili d'ambiente?">
    OpenClaw legge le env var dal processo padre (shell, launchd/systemd, CI, ecc.) e in aggiunta carica:

    - `.env` dalla directory di lavoro corrente
    - un fallback globale `.env` da `~/.openclaw/.env` (alias `$OPENCLAW_STATE_DIR/.env`)

    Nessuno dei due file `.env` sovrascrive env var esistenti.

    Puoi anche definire env var inline nella configurazione (applicate solo se mancanti nell'env del processo):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Vedi [/environment](/it/help/environment) per la precedenza completa e le sorgenti.

  </Accordion>

  <Accordion title="Ho avviato il Gateway tramite il servizio e le mie env var sono scomparse. E adesso?">
    Due correzioni comuni:

    1. Inserisci le chiavi mancanti in `~/.openclaw/.env` così verranno lette anche se il servizio non eredita l'env della tua shell.
    2. Abilita l'importazione della shell (comodità opt-in):

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    Questo esegue la tua shell di login e importa solo le chiavi attese mancanti (senza sovrascrivere mai). Equivalenti env var:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='Ho impostato COPILOT_GITHUB_TOKEN, ma models status mostra "Shell env: off." Perché?'>
    `openclaw models status` riporta se **l'importazione delle env della shell** è abilitata. "Shell env: off"
    **non** significa che le tue env var manchino - significa solo che OpenClaw non caricherà
    automaticamente la tua shell di login.

    Se il Gateway gira come servizio (launchd/systemd), non erediterà il tuo ambiente
    shell. Correggi in uno di questi modi:

    1. Inserisci il token in `~/.openclaw/.env`:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Oppure abilita l'importazione shell (`env.shellEnv.enabled: true`).
    3. Oppure aggiungilo al blocco `env` della configurazione (si applica solo se manca).

    Poi riavvia il gateway e ricontrolla:

    ```bash
    openclaw models status
    ```

    I token Copilot vengono letti da `COPILOT_GITHUB_TOKEN` (anche `GH_TOKEN` / `GITHUB_TOKEN`).
    Vedi [/concepts/model-providers](/it/concepts/model-providers) e [/environment](/it/help/environment).

  </Accordion>
</AccordionGroup>

## Sessioni e più chat

<AccordionGroup>
  <Accordion title="Come avvio una conversazione nuova?">
    Invia `/new` o `/reset` come messaggio autonomo. Vedi [Session management](/it/concepts/session).
  </Accordion>

  <Accordion title="Le sessioni si reimpostano automaticamente se non invio mai /new?">
    Le sessioni possono scadere dopo `session.idleMinutes`, ma questo è **disabilitato per impostazione predefinita** (valore predefinito **0**).
    Impostalo a un valore positivo per abilitare la scadenza per inattività. Quando è attiva, il
    messaggio **successivo** dopo il periodo di inattività avvia un nuovo ID sessione per quella chiave chat.
    Questo non elimina le trascrizioni - avvia semplicemente una nuova sessione.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="Esiste un modo per creare un team di istanze OpenClaw (un CEO e molti agenti)?">
    Sì, tramite **multi-agent routing** e **sub-agents**. Puoi creare un agente coordinatore
    e diversi agenti worker con i propri workspace e modelli.

    Detto questo, è meglio vederlo come un **esperimento divertente**. Consuma molti token e spesso
    è meno efficiente che usare un solo bot con sessioni separate. Il modello tipico che
    immaginiamo è un solo bot con cui parlare, con sessioni diverse per lavoro in parallelo. Quel
    bot può anche generare sub-agents quando necessario.

    Documentazione: [Multi-agent routing](/it/concepts/multi-agent), [Sub-agents](/it/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="Perché il contesto è stato troncato a metà attività? Come posso evitarlo?">
    Il contesto della sessione è limitato dalla finestra del modello. Chat lunghe, output degli strumenti molto grandi o molti
    file possono attivare compattazione o troncamento.

    Cosa aiuta:

    - Chiedi al bot di riassumere lo stato corrente e scriverlo in un file.
    - Usa `/compact` prima di attività lunghe, e `/new` quando cambi argomento.
    - Mantieni il contesto importante nel workspace e chiedi al bot di rileggerlo.
    - Usa sub-agents per attività lunghe o parallele così la chat principale resta più piccola.
    - Scegli un modello con una finestra di contesto più ampia se succede spesso.

  </Accordion>

  <Accordion title="Come reimposto completamente OpenClaw ma lo tengo installato?">
    Usa il comando di reset:

    ```bash
    openclaw reset
    ```

    Reset completo non interattivo:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    Poi riesegui la configurazione:

    ```bash
    openclaw onboard --install-daemon
    ```

    Note:

    - Anche l'onboarding offre **Reset** se rileva una configurazione esistente. Vedi [Onboarding (CLI)](/it/start/wizard).
    - Se hai usato profili (`--profile` / `OPENCLAW_PROFILE`), reimposta ogni directory di stato (i valori predefiniti sono `~/.openclaw-<profile>`).
    - Reset dev: `openclaw gateway --dev --reset` (solo dev; cancella configurazione dev + credenziali + sessioni + workspace).

  </Accordion>

  <Accordion title='Ricevo errori "context too large" - come faccio a reimpostare o compattare?'>
    Usa uno di questi:

    - **Compatta** (mantiene la conversazione ma riassume i turni meno recenti):

      ```
      /compact
      ```

      oppure `/compact <instructions>` per guidare il riepilogo.

    - **Reset** (nuovo ID sessione per la stessa chiave chat):

      ```
      /new
      /reset
      ```

    Se continua a succedere:

    - Abilita o regola il **session pruning** (`agents.defaults.contextPruning`) per ridurre il vecchio output degli strumenti.
    - Usa un modello con una finestra di contesto più grande.

    Documentazione: [Compaction](/it/concepts/compaction), [Session pruning](/it/concepts/session-pruning), [Session management](/it/concepts/session).

  </Accordion>

  <Accordion title='Perché vedo "LLM request rejected: messages.content.tool_use.input field required"?'>
    Questo è un errore di validazione del provider: il modello ha emesso un blocco `tool_use` senza il campo
    `input` richiesto. Di solito significa che la cronologia della sessione è stale o corrotta (spesso dopo thread lunghi
    o una modifica di strumento/schema).

    Correzione: avvia una sessione nuova con `/new` (messaggio autonomo).

  </Accordion>

  <Accordion title="Perché ricevo messaggi heartbeat ogni 30 minuti?">
    Heartbeat viene eseguito ogni **30m** per impostazione predefinita (**1h** quando si usa autenticazione OAuth). Regolalo o disabilitalo:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // oppure "0m" per disabilitare
          },
        },
      },
    }
    ```

    Se `HEARTBEAT.md` esiste ma è di fatto vuoto (solo righe vuote e intestazioni markdown
    come `# Heading`), OpenClaw salta l'esecuzione di heartbeat per risparmiare chiamate API.
    Se il file manca, heartbeat viene comunque eseguito e il modello decide cosa fare.

    Gli override per agente usano `agents.list[].heartbeat`. Documentazione: [Heartbeat](/it/gateway/heartbeat).

  </Accordion>

  <Accordion title='Devo aggiungere un "account bot" a un gruppo WhatsApp?'>
    No. OpenClaw gira sul **tuo account**, quindi se sei nel gruppo, OpenClaw può vederlo.
    Per impostazione predefinita, le risposte ai gruppi sono bloccate finché non consenti i mittenti (`groupPolicy: "allowlist"`).

    Se vuoi che solo **tu** possa attivare risposte nel gruppo:

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Come ottengo il JID di un gruppo WhatsApp?">
    Opzione 1 (più veloce): segui i log e invia un messaggio di test nel gruppo:

    ```bash
    openclaw logs --follow --json
    ```

    Cerca `chatId` (o `from`) che termina con `@g.us`, ad esempio:
    `1234567890-1234567890@g.us`.

    Opzione 2 (se già configurato/in allowlist): elenca i gruppi dalla configurazione:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Documentazione: [WhatsApp](/it/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="Perché OpenClaw non risponde in un gruppo?">
    Due cause comuni:

    - Il gating per menzione è attivo (predefinito). Devi @menzionare il bot (o corrispondere a `mentionPatterns`).
    - Hai configurato `channels.whatsapp.groups` senza `"*"` e il gruppo non è in allowlist.

    Vedi [Groups](/it/channels/groups) e [Group messages](/it/channels/group-messages).

  </Accordion>

  <Accordion title="Gruppi/thread condividono il contesto con i DM?">
    Le chat dirette collassano nella sessione principale per impostazione predefinita. Gruppi/canali hanno le proprie chiavi di sessione, e topic Telegram / thread Discord sono sessioni separate. Vedi [Groups](/it/channels/groups) e [Group messages](/it/channels/group-messages).
  </Accordion>

  <Accordion title="Quanti workspace e agenti posso creare?">
    Nessun limite rigido. Decine (anche centinaia) vanno bene, ma fai attenzione a:

    - **Crescita del disco:** sessioni + trascrizioni vivono sotto `~/.openclaw/agents/<agentId>/sessions/`.
    - **Costo dei token:** più agenti significa più utilizzo concorrente del modello.
    - **Overhead operativo:** profili auth per agente, workspace e routing dei canali.

    Suggerimenti:

    - Mantieni un workspace **attivo** per agente (`agents.defaults.workspace`).
    - Pota le vecchie sessioni (elimina JSONL o voci di archivio) se il disco cresce.
    - Usa `openclaw doctor` per individuare workspace vaganti e mismatch dei profili.

  </Accordion>

  <Accordion title="Posso eseguire più bot o chat contemporaneamente (Slack), e come dovrei configurarlo?">
    Sì. Usa **Multi-Agent Routing** per eseguire più agenti isolati e instradare i messaggi in ingresso in base a
    canale/account/peer. Slack è supportato come canale e può essere collegato ad agenti specifici.

    L'accesso al browser è potente ma non equivale a "fare tutto ciò che può fare un umano" - anti-bot, CAPTCHA e MFA possono
    comunque bloccare l'automazione. Per il controllo del browser più affidabile, usa Chrome MCP locale sull'host,
    oppure usa CDP sulla macchina che esegue davvero il browser.

    Configurazione di best practice:

    - Host Gateway sempre acceso (VPS/Mac mini).
    - Un agente per ruolo (binding).
    - Canali Slack collegati a quegli agenti.
    - Browser locale tramite Chrome MCP o un nodo quando necessario.

    Documentazione: [Multi-Agent Routing](/it/concepts/multi-agent), [Slack](/it/channels/slack),
    [Browser](/it/tools/browser), [Nodes](/it/nodes).

  </Accordion>
</AccordionGroup>

## Modelli: predefiniti, selezione, alias, cambio

<AccordionGroup>
  <Accordion title='Che cos'è il "modello predefinito"?'>
    Il modello predefinito di OpenClaw è quello che imposti come:

    ```
    agents.defaults.model.primary
    ```

    I modelli sono referenziati come `provider/model` (esempio: `openai/gpt-5.4`). Se ometti il provider, OpenClaw prova prima un alias, poi una corrispondenza univoca del provider configurato per quell'esatto model id, e solo dopo ricade sul provider predefinito configurato come percorso di compatibilità deprecato. Se quel provider non espone più il modello predefinito configurato, OpenClaw ricade sul primo provider/modello configurato invece di mostrare un predefinito stale di un provider rimosso. Dovresti comunque impostare **esplicitamente** `provider/model`.

  </Accordion>

  <Accordion title="Quale modello consigliate?">
    **Predefinito consigliato:** usa il modello latest-generation più forte disponibile nel tuo stack di provider.
    **Per agenti con strumenti abilitati o input non attendibili:** dai priorità alla forza del modello rispetto al costo.
    **Per chat di routine/a basso rischio:** usa modelli fallback più economici e instrada per ruolo dell'agente.

    MiniMax ha una documentazione dedicata: [MiniMax](/it/providers/minimax) e
    [Local models](/it/gateway/local-models).

    Regola pratica: usa il **miglior modello che puoi permetterti** per lavori ad alto rischio, e un modello più economico
    per chat di routine o riepiloghi. Puoi instradare i modelli per agente e usare sub-agents per
    parallelizzare attività lunghe (ogni sub-agent consuma token). Vedi [Models](/it/concepts/models) e
    [Sub-agents](/it/tools/subagents).

    Avvertenza importante: i modelli più deboli/overtly quantizzati sono più vulnerabili al prompt
    injection e a comportamenti non sicuri. Vedi [Security](/it/gateway/security).

    Più contesto: [Models](/it/concepts/models).

  </Accordion>

  <Accordion title="Come cambio modello senza cancellare la configurazione?">
    Usa i **comandi del modello** oppure modifica solo i campi **model**. Evita sostituzioni complete della configurazione.

    Opzioni sicure:

    - `/model` in chat (rapido, per sessione)
    - `openclaw models set ...` (aggiorna solo la configurazione del modello)
    - `openclaw configure --section model` (interattivo)
    - modifica `agents.defaults.model` in `~/.openclaw/openclaw.json`

    Evita `config.apply` con un oggetto parziale a meno che tu non voglia sostituire l'intera configurazione.
    Per modifiche RPC, ispeziona prima con `config.schema.lookup` e preferisci `config.patch`. Il payload lookup ti fornisce il percorso normalizzato, la documentazione/vincoli dello schema superficiale e i riepiloghi dei figli immediati
    per aggiornamenti parziali.
    Se hai sovrascritto la configurazione, ripristina da backup o riesegui `openclaw doctor` per ripararla.

    Documentazione: [Models](/it/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/it/gateway/doctor).

  </Accordion>

  <Accordion title="Posso usare modelli self-hosted (llama.cpp, vLLM, Ollama)?">
    Sì. Ollama è il percorso più semplice per i modelli locali.

    Configurazione più rapida:

    1. Installa Ollama da `https://ollama.com/download`
    2. Scarica un modello locale come `ollama pull gemma4`
    3. Se vuoi anche modelli cloud, esegui `ollama signin`
    4. Esegui `openclaw onboard` e scegli `Ollama`
    5. Scegli `Local` o `Cloud + Local`

    Note:

    - `Cloud + Local` ti offre modelli cloud più i tuoi modelli Ollama locali
    - i modelli cloud come `kimi-k2.5:cloud` non richiedono un pull locale
    - per il cambio manuale, usa `openclaw models list` e `openclaw models set ollama/<model>`

    Nota sulla sicurezza: i modelli più piccoli o fortemente quantizzati sono più vulnerabili al prompt
    injection. Raccomandiamo con forza **modelli grandi** per qualsiasi bot che possa usare strumenti.
    Se vuoi comunque modelli piccoli, abilita sandboxing e allowlist strette per gli strumenti.

    Documentazione: [Ollama](/it/providers/ollama), [Local models](/it/gateway/local-models),
    [Model providers](/it/concepts/model-providers), [Security](/it/gateway/security),
    [Sandboxing](/it/gateway/sandboxing).

  </Accordion>

  <Accordion title="Quali modelli usano OpenClaw, Flawd e Krill?">
    - Queste distribuzioni possono differire e cambiare nel tempo; non esiste una raccomandazione fissa sul provider.
    - Controlla l'impostazione di runtime corrente su ogni gateway con `openclaw models status`.
    - Per agenti sensibili alla sicurezza/con strumenti abilitati, usa il modello latest-generation più forte disponibile.
  </Accordion>

  <Accordion title="Come cambio modello al volo (senza riavviare)?">
    Usa il comando `/model` come messaggio autonomo:

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    Questi sono gli alias built-in. Puoi aggiungere alias personalizzati tramite `agents.defaults.models`.

    Puoi elencare i modelli disponibili con `/model`, `/model list`, o `/model status`.

    `/model` (e `/model list`) mostra un selettore compatto numerato. Seleziona per numero:

    ```
    /model 3
    ```

    Puoi anche forzare uno specifico profilo auth per il provider (per sessione):

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    Suggerimento: `/model status` mostra quale agente è attivo, quale file `auth-profiles.json` viene usato e quale profilo auth verrà tentato successivamente.
    Mostra anche l'endpoint del provider configurato (`baseUrl`) e la modalità API (`api`) quando disponibili.

    **Come rimuovo il pin di un profilo impostato con @profile?**

    Riesegui `/model` **senza** il suffisso `@profile`:

    ```
    /model anthropic/claude-opus-4-6
    ```

    Se vuoi tornare al valore predefinito, sceglilo da `/model` (oppure invia `/model <default provider/model>`).
    Usa `/model status` per confermare quale profilo auth è attivo.

  </Accordion>

  <Accordion title="Posso usare GPT 5.2 per attività quotidiane e Codex 5.3 per il coding?">
    Sì. Impostane uno come predefinito e cambia quando necessario:

    - **Cambio rapido (per sessione):** `/model gpt-5.4` per attività quotidiane, `/model openai-codex/gpt-5.4` per il coding con Codex OAuth.
    - **Predefinito + cambio:** imposta `agents.defaults.model.primary` su `openai/gpt-5.4`, poi passa a `openai-codex/gpt-5.4` quando fai coding (o viceversa).
    - **Sub-agents:** instrada le attività di coding a sub-agents con un modello predefinito diverso.

    Vedi [Models](/it/concepts/models) e [Slash commands](/it/tools/slash-commands).

  </Accordion>

  <Accordion title="Come configuro la fast mode per GPT 5.4?">
    Usa un toggle di sessione o un valore predefinito di configurazione:

    - **Per sessione:** invia `/fast on` mentre la sessione usa `openai/gpt-5.4` o `openai-codex/gpt-5.4`.
    - **Predefinito per modello:** imposta `agents.defaults.models["openai/gpt-5.4"].params.fastMode` su `true`.
    - **Anche Codex OAuth:** se usi anche `openai-codex/gpt-5.4`, imposta lì lo stesso flag.

    Esempio:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    Per OpenAI, la fast mode corrisponde a `service_tier = "priority"` nelle richieste Responses native supportate. Le override di sessione `/fast` hanno precedenza sui valori predefiniti di configurazione.

    Vedi [Thinking and fast mode](/it/tools/thinking) e [OpenAI fast mode](/it/providers/openai#openai-fast-mode).

  </Accordion>

  <Accordion title='Perché vedo "Model ... is not allowed" e poi nessuna risposta?'>
    Se `agents.defaults.models` è impostato, diventa la **allowlist** per `/model` e per qualunque
    override di sessione. Scegliere un modello che non è in quell'elenco restituisce:

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    Questo errore viene restituito **al posto** di una risposta normale. Correzione: aggiungi il modello a
    `agents.defaults.models`, rimuovi la allowlist oppure scegli un modello da `/model list`.

  </Accordion>

  <Accordion title='Perché vedo "Unknown model: minimax/MiniMax-M2.7"?'>
    Questo significa che il **provider non è configurato** (non è stata trovata alcuna configurazione provider MiniMax o alcun
    profilo auth), quindi il modello non può essere risolto.

    Checklist di correzione:

    1. Aggiorna a una release corrente di OpenClaw (oppure esegui dal sorgente `main`), poi riavvia il gateway.
    2. Assicurati che MiniMax sia configurato (wizard o JSON), o che l'autenticazione MiniMax
       esista in env/profili auth così il provider corrispondente possa essere iniettato
       (`MINIMAX_API_KEY` per `minimax`, `MINIMAX_OAUTH_TOKEN` o OAuth MiniMax memorizzato
       per `minimax-portal`).
    3. Usa l'esatto model id (case-sensitive) per il tuo percorso auth:
       `minimax/MiniMax-M2.7` o `minimax/MiniMax-M2.7-highspeed` per configurazioni con chiave API,
       oppure `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed` per configurazioni OAuth.
    4. Esegui:

       ```bash
       openclaw models list
       ```

       e scegli dall'elenco (oppure `/model list` in chat).

    Vedi [MiniMax](/it/providers/minimax) e [Models](/it/concepts/models).

  </Accordion>

  <Accordion title="Posso usare MiniMax come predefinito e OpenAI per attività complesse?">
    Sì. Usa **MiniMax come predefinito** e cambia modello **per sessione** quando necessario.
    I fallback servono per gli **errori**, non per le "attività difficili", quindi usa `/model` o un agente separato.

    **Opzione A: cambio per sessione**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    Poi:

    ```
    /model gpt
    ```

    **Opzione B: agenti separati**

    - Agente A predefinito: MiniMax
    - Agente B predefinito: OpenAI
    - Instrada per agente o usa `/agent` per cambiare

    Documentazione: [Models](/it/concepts/models), [Multi-Agent Routing](/it/concepts/multi-agent), [MiniMax](/it/providers/minimax), [OpenAI](/it/providers/openai).

  </Accordion>

  <Accordion title="opus / sonnet / gpt sono scorciatoie built-in?">
    Sì. OpenClaw include alcune abbreviazioni predefinite (applicate solo quando il modello esiste in `agents.defaults.models`):

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    Se imposti un tuo alias con lo stesso nome, il tuo valore prevale.

  </Accordion>

  <Accordion title="Come definisco/sovrascrivo scorciatoie del modello (alias)?">
    Gli alias provengono da `agents.defaults.models.<modelId>.alias`. Esempio:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    Poi `/model sonnet` (o `/<alias>` quando supportato) viene risolto in quel model ID.

  </Accordion>

  <Accordion title="Come aggiungo modelli da altri provider come OpenRouter o Z.AI?">
    OpenRouter (pay-per-token; molti modelli):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    Z.AI (modelli GLM):

    ```json5
    {
      agents: {
        defaults: {
          model