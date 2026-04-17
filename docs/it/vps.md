---
read_when:
    - Vuoi eseguire il Gateway su un server Linux o su un VPS cloud
    - Hai bisogno di una rapida panoramica delle guide di hosting
    - Vuoi un'ottimizzazione generica di un server Linux per OpenClaw
sidebarTitle: Linux Server
summary: Esegui OpenClaw su un server Linux o un VPS cloud — selettore del provider, architettura e ottimizzazione
title: Server Linux
x-i18n:
    generated_at: "2026-04-14T02:08:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: e623f4c770132e01628d66bfb8cd273bbef6dad633b812496c90da5e3e0f1383
    source_path: vps.md
    workflow: 15
---

# Server Linux

Esegui il Gateway di OpenClaw su qualsiasi server Linux o VPS cloud. Questa pagina ti aiuta a scegliere un provider, spiega come funzionano le distribuzioni cloud e copre l'ottimizzazione generica di Linux che si applica ovunque.

## Scegli un provider

<CardGroup cols={2}>
  <Card title="Railway" href="/it/install/railway">Configurazione nel browser con un clic</Card>
  <Card title="Northflank" href="/it/install/northflank">Configurazione nel browser con un clic</Card>
  <Card title="DigitalOcean" href="/it/install/digitalocean">VPS a pagamento semplice</Card>
  <Card title="Oracle Cloud" href="/it/install/oracle">Piano ARM Always Free</Card>
  <Card title="Fly.io" href="/it/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/it/install/hetzner">Docker su VPS Hetzner</Card>
  <Card title="Hostinger" href="/it/install/hostinger">VPS con configurazione con un clic</Card>
  <Card title="GCP" href="/it/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/it/install/azure">VM Linux</Card>
  <Card title="exe.dev" href="/it/install/exe-dev">VM con proxy HTTPS</Card>
  <Card title="Raspberry Pi" href="/it/install/raspberry-pi">Self-hosted ARM</Card>
</CardGroup>

Anche **AWS (EC2 / Lightsail / livello gratuito)** funziona bene.
È disponibile una video guida della community su
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
(risorsa della community -- potrebbe non essere più disponibile).

## Come funzionano le configurazioni cloud

- Il **Gateway viene eseguito sul VPS** e gestisce stato + workspace.
- Ti connetti dal laptop o dal telefono tramite la **Control UI** o **Tailscale/SSH**.
- Tratta il VPS come fonte di verità ed esegui regolarmente il **backup** di stato + workspace.
- Impostazione sicura predefinita: mantieni il Gateway su loopback e accedivi tramite tunnel SSH o Tailscale Serve.
  Se esegui il bind a `lan` o `tailnet`, richiedi `gateway.auth.token` o `gateway.auth.password`.

Pagine correlate: [Accesso remoto al Gateway](/it/gateway/remote), [Hub delle piattaforme](/it/platforms).

## Agente aziendale condiviso su un VPS

Eseguire un singolo agente per un team è una configurazione valida quando ogni utente si trova nello stesso confine di fiducia e l'agente è usato solo per attività aziendali.

- Mantienilo su un runtime dedicato (VPS/VM/container + utente/account OS dedicati).
- Non effettuare l'accesso su quel runtime con account Apple/Google personali o con profili personali del browser/gestore password.
- Se gli utenti sono avversariali tra loro, separa per gateway/host/utente OS.

Dettagli del modello di sicurezza: [Sicurezza](/it/gateway/security).

## Uso dei Node con un VPS

Puoi mantenere il Gateway nel cloud e associare **Node** sui tuoi dispositivi locali
(Mac/iOS/Android/headless). I Node forniscono funzionalità locali di schermo/fotocamera/canvas e `system.run`
mentre il Gateway rimane nel cloud.

Documentazione: [Node](/it/nodes), [CLI dei Node](/cli/nodes).

## Ottimizzazione dell'avvio per VM piccole e host ARM

Se i comandi CLI sembrano lenti su VM a bassa potenza (o host ARM), abilita la cache di compilazione dei moduli di Node:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` migliora i tempi di avvio dei comandi ripetuti.
- `OPENCLAW_NO_RESPAWN=1` evita l'overhead di avvio aggiuntivo dovuto a un percorso di auto-respawn.
- La prima esecuzione del comando riscalda la cache; le esecuzioni successive sono più veloci.
- Per dettagli specifici su Raspberry Pi, vedi [Raspberry Pi](/it/install/raspberry-pi).

### Checklist di ottimizzazione di systemd (opzionale)

Per gli host VM che usano `systemd`, valuta quanto segue:

- Aggiungi variabili d'ambiente del servizio per un percorso di avvio stabile:
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- Mantieni esplicito il comportamento di riavvio:
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- Preferisci dischi supportati da SSD per i percorsi di stato/cache, così da ridurre le penalità di avvio a freddo dovute all'I/O casuale.

Per il percorso standard `openclaw onboard --install-daemon`, modifica l'unità utente:

```bash
systemctl --user edit openclaw-gateway.service
```

```ini
[Service]
Environment=OPENCLAW_NO_RESPAWN=1
Environment=NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
Restart=always
RestartSec=2
TimeoutStartSec=90
```

Se invece hai installato deliberatamente un'unità di sistema, modifica
`openclaw-gateway.service` tramite `sudo systemctl edit openclaw-gateway.service`.

Come le policy `Restart=` aiutano il recupero automatico:
[systemd può automatizzare il recupero del servizio](https://www.redhat.com/en/blog/systemd-automate-recovery).
