---
read_when:
    - Implementazione delle funzionalità dell'app macOS
    - Modifica del ciclo di vita del Gateway o del bridging del Node su macOS
summary: App companion per macOS di OpenClaw (barra dei menu + broker Gateway)
title: App macOS
x-i18n:
    generated_at: "2026-04-17T08:17:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: d637df2f73ced110223c48ea3c934045d782e150a46495f434cf924a6a00baf0
    source_path: platforms/macos.md
    workflow: 15
---

# Companion macOS di OpenClaw (barra dei menu + broker Gateway)

L'app macOS è il **companion nella barra dei menu** per OpenClaw. Gestisce le autorizzazioni,
gestisce/si collega al Gateway localmente (launchd o manuale) ed espone le capacità macOS
all'agente come Node.

## Cosa fa

- Mostra notifiche native e stato nella barra dei menu.
- Gestisce i prompt TCC (Notifiche, Accessibilità, Registrazione schermo, Microfono,
  Riconoscimento vocale, Automazione/AppleScript).
- Avvia o si collega al Gateway (locale o remoto).
- Espone strumenti solo macOS (Canvas, Fotocamera, Registrazione schermo, `system.run`).
- Avvia il servizio host Node locale in modalità **remote** (launchd) e lo arresta in modalità **local**.
- Può opzionalmente ospitare **PeekabooBridge** per l'automazione dell'interfaccia.
- Installa la CLI globale (`openclaw`) su richiesta tramite npm, pnpm o bun (l'app preferisce npm, poi pnpm, poi bun; Node rimane il runtime consigliato per il Gateway).

## Modalità locale vs remota

- **Local** (predefinita): l'app si collega a un Gateway locale in esecuzione, se presente;
  altrimenti abilita il servizio launchd tramite `openclaw gateway install`.
- **Remote**: l'app si collega a un Gateway tramite SSH/Tailscale e non avvia mai
  un processo locale.
  L'app avvia il **servizio host Node** locale affinché il Gateway remoto possa raggiungere questo Mac.
  L'app non avvia il Gateway come processo figlio.
  Il rilevamento del Gateway ora preferisce i nomi Tailscale MagicDNS agli IP tailnet grezzi,
  quindi l'app Mac si ripristina in modo più affidabile quando gli IP tailnet cambiano.

## Controllo launchd

L'app gestisce un LaunchAgent per utente etichettato `ai.openclaw.gateway`
(o `ai.openclaw.<profile>` quando si usa `--profile`/`OPENCLAW_PROFILE`; il legacy `com.openclaw.*` viene comunque scaricato).

```bash
launchctl kickstart -k gui/$UID/ai.openclaw.gateway
launchctl bootout gui/$UID/ai.openclaw.gateway
```

Sostituisci l'etichetta con `ai.openclaw.<profile>` quando esegui un profilo con nome.

Se il LaunchAgent non è installato, abilitalo dall'app oppure esegui
`openclaw gateway install`.

## Capacità del Node (mac)

L'app macOS si presenta come un Node. Comandi comuni:

- Canvas: `canvas.present`, `canvas.navigate`, `canvas.eval`, `canvas.snapshot`, `canvas.a2ui.*`
- Fotocamera: `camera.snap`, `camera.clip`
- Schermo: `screen.snapshot`, `screen.record`
- Sistema: `system.run`, `system.notify`

Il Node riporta una mappa `permissions` così che gli agenti possano decidere cosa è consentito.

Servizio Node + IPC dell'app:

- Quando il servizio host Node headless è in esecuzione (modalità remote), si collega al Gateway WS come Node.
- `system.run` viene eseguito nell'app macOS (contesto UI/TCC) tramite un socket Unix locale; prompt e output restano nell'app.

Diagramma (SCI):

```
Gateway -> Node Service (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac App (UI + TCC + system.run)
```

## Approvazioni exec (`system.run`)

`system.run` è controllato da **Approvazioni exec** nell'app macOS (Impostazioni → Approvazioni exec).
Security + ask + allowlist sono memorizzati localmente sul Mac in:

```
~/.openclaw/exec-approvals.json
```

Esempio:

```json
{
  "version": 1,
  "defaults": {
    "security": "deny",
    "ask": "on-miss"
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "allowlist": [{ "pattern": "/opt/homebrew/bin/rg" }]
    }
  }
}
```

Note:

- Le voci `allowlist` sono pattern glob per i percorsi binari risolti.
- Il testo grezzo del comando shell che contiene sintassi di controllo o espansione della shell (`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) viene trattato come mancata corrispondenza con l'allowlist e richiede approvazione esplicita (oppure l'inserimento del binario shell nell'allowlist).
- Scegliere “Consenti sempre” nel prompt aggiunge quel comando all'allowlist.
- Gli override dell'ambiente di `system.run` vengono filtrati (rimuovono `PATH`, `DYLD_*`, `LD_*`, `NODE_OPTIONS`, `PYTHON*`, `PERL*`, `RUBYOPT`, `SHELLOPTS`, `PS4`) e poi uniti all'ambiente dell'app.
- Per i wrapper shell (`bash|sh|zsh ... -c/-lc`), gli override dell'ambiente con ambito richiesta vengono ridotti a una piccola allowlist esplicita (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
- Per le decisioni consenti-sempre in modalità allowlist, i wrapper di dispatch noti (`env`, `nice`, `nohup`, `stdbuf`, `timeout`) mantengono i percorsi dell'eseguibile interno invece dei percorsi del wrapper. Se l'unwrapping non è sicuro, nessuna voce allowlist viene mantenuta automaticamente.

## Deep link

L'app registra lo schema URL `openclaw://` per azioni locali.

### `openclaw://agent`

Attiva una richiesta `agent` del Gateway.
__OC_I18N_900004__
Parametri di query:

- `message` (obbligatorio)
- `sessionKey` (facoltativo)
- `thinking` (facoltativo)
- `deliver` / `to` / `channel` (facoltativo)
- `timeoutSeconds` (facoltativo)
- `key` (facoltativo, chiave per modalità non presidiata)

Sicurezza:

- Senza `key`, l'app richiede conferma.
- Senza `key`, l'app applica un limite breve al messaggio per il prompt di conferma e ignora `deliver` / `to` / `channel`.
- Con una `key` valida, l'esecuzione non è presidiata (pensata per automazioni personali).

## Flusso di onboarding (tipico)

1. Installa e avvia **OpenClaw.app**.
2. Completa la checklist delle autorizzazioni (prompt TCC).
3. Assicurati che la modalità **Local** sia attiva e che il Gateway sia in esecuzione.
4. Installa la CLI se desideri l'accesso dal terminale.

## Posizionamento della directory di stato (macOS)

Evita di collocare la directory di stato di OpenClaw in iCloud o in altre cartelle sincronizzate nel cloud.
I percorsi supportati dalla sincronizzazione possono aggiungere latenza e occasionalmente causare race di blocco file/sincronizzazione per
sessioni e credenziali.

Preferisci un percorso di stato locale non sincronizzato come:
__OC_I18N_900005__
Se `openclaw doctor` rileva lo stato sotto:

- `~/Library/Mobile Documents/com~apple~CloudDocs/...`
- `~/Library/CloudStorage/...`

emetterà un avviso e consiglierà di tornare a un percorso locale.

## Build e flusso di sviluppo (nativo)

- `cd apps/macos && swift build`
- `swift run OpenClaw` (oppure Xcode)
- Crea il pacchetto dell'app: `scripts/package-mac-app.sh`

## Debug della connettività Gateway (CLI macOS)

Usa la CLI di debug per esercitare la stessa logica di handshake WebSocket del Gateway e di rilevamento
usata dall'app macOS, senza avviare l'app.
__OC_I18N_900006__
Opzioni di connessione:

- `--url <ws://host:port>`: override della configurazione
- `--mode <local|remote>`: risolvi dalla configurazione (predefinito: configurazione o local)
- `--probe`: forza un probe di integrità aggiornato
- `--timeout <ms>`: timeout della richiesta (predefinito: `15000`)
- `--json`: output strutturato per il confronto

Opzioni di rilevamento:

- `--include-local`: include i Gateway che verrebbero filtrati come “locali”
- `--timeout <ms>`: finestra complessiva di rilevamento (predefinito: `2000`)
- `--json`: output strutturato per il confronto

Suggerimento: confronta con `openclaw gateway discover --json` per verificare se la
pipeline di rilevamento dell'app macOS (`local.` più il dominio wide-area configurato, con
fallback wide-area e Tailscale Serve) differisce da
quella della CLI Node basata su `dns-sd`.

## Infrastruttura di connessione remota (tunnel SSH)

Quando l'app macOS viene eseguita in modalità **Remote**, apre un tunnel SSH affinché i componenti UI locali
possano comunicare con un Gateway remoto come se fosse su localhost.

### Tunnel di controllo (porta WebSocket Gateway)

- **Scopo:** controlli di integrità, stato, Chat Web, configurazione e altre chiamate del control plane.
- **Porta locale:** la porta del Gateway (predefinita `18789`), sempre stabile.
- **Porta remota:** la stessa porta del Gateway sull'host remoto.
- **Comportamento:** nessuna porta locale casuale; l'app riutilizza un tunnel integro esistente
  oppure lo riavvia se necessario.
- **Forma SSH:** `ssh -N -L <local>:127.0.0.1:<remote>` con BatchMode +
  ExitOnForwardFailure + opzioni keepalive.
- **Segnalazione IP:** il tunnel SSH usa il loopback, quindi il Gateway vedrà l'IP del Node
  come `127.0.0.1`. Usa il trasporto **Direct (ws/wss)** se vuoi che venga mostrato il vero IP
  del client (vedi [accesso remoto macOS](/it/platforms/mac/remote)).

Per i passaggi di configurazione, vedi [accesso remoto macOS](/it/platforms/mac/remote). Per i dettagli
del protocollo, vedi [protocollo Gateway](/it/gateway/protocol).

## Documentazione correlata

- [Runbook Gateway](/it/gateway)
- [Gateway (macOS)](/it/platforms/mac/bundled-gateway)
- [Autorizzazioni macOS](/it/platforms/mac/permissions)
- [Canvas](/it/platforms/mac/canvas)
