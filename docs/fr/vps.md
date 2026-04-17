---
read_when:
    - Vous souhaitez exécuter la Gateway sur un serveur Linux ou un VPS cloud
    - Vous avez besoin d’un aperçu rapide des guides d’hébergement
    - Vous souhaitez un réglage générique d’un serveur Linux pour OpenClaw
sidebarTitle: Linux Server
summary: Exécuter OpenClaw sur un serveur Linux ou un VPS cloud — sélecteur de fournisseur, architecture et réglage
title: Serveur Linux
x-i18n:
    generated_at: "2026-04-14T02:08:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: e623f4c770132e01628d66bfb8cd273bbef6dad633b812496c90da5e3e0f1383
    source_path: vps.md
    workflow: 15
---

# Serveur Linux

Exécutez la Gateway OpenClaw sur n’importe quel serveur Linux ou VPS cloud. Cette page vous aide à
choisir un fournisseur, explique le fonctionnement des déploiements cloud et couvre le réglage Linux
générique qui s’applique partout.

## Choisir un fournisseur

<CardGroup cols={2}>
  <Card title="Railway" href="/fr/install/railway">Configuration en un clic, dans le navigateur</Card>
  <Card title="Northflank" href="/fr/install/northflank">Configuration en un clic, dans le navigateur</Card>
  <Card title="DigitalOcean" href="/fr/install/digitalocean">VPS payant simple</Card>
  <Card title="Oracle Cloud" href="/fr/install/oracle">Offre ARM Always Free</Card>
  <Card title="Fly.io" href="/fr/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/fr/install/hetzner">Docker sur VPS Hetzner</Card>
  <Card title="Hostinger" href="/fr/install/hostinger">VPS avec configuration en un clic</Card>
  <Card title="GCP" href="/fr/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/fr/install/azure">VM Linux</Card>
  <Card title="exe.dev" href="/fr/install/exe-dev">VM avec proxy HTTPS</Card>
  <Card title="Raspberry Pi" href="/fr/install/raspberry-pi">ARM auto-hébergé</Card>
</CardGroup>

**AWS (EC2 / Lightsail / niveau gratuit)** fonctionne également très bien.
Une vidéo explicative de la communauté est disponible à l’adresse
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
(ressource communautaire -- peut devenir indisponible).

## Fonctionnement des configurations cloud

- La **Gateway s’exécute sur le VPS** et gère l’état + l’espace de travail.
- Vous vous connectez depuis votre ordinateur portable ou votre téléphone via la **Control UI** ou **Tailscale/SSH**.
- Considérez le VPS comme la source de vérité et **sauvegardez** régulièrement l’état + l’espace de travail.
- Configuration sécurisée par défaut : gardez la Gateway sur loopback et accédez-y via un tunnel SSH ou Tailscale Serve.
  Si vous la liez à `lan` ou `tailnet`, exigez `gateway.auth.token` ou `gateway.auth.password`.

Pages connexes : [Accès distant à la Gateway](/fr/gateway/remote), [Hub des plateformes](/fr/platforms).

## Agent d’entreprise partagé sur un VPS

Exécuter un seul agent pour une équipe est une configuration valable lorsque tous les utilisateurs se trouvent dans le même périmètre de confiance et que l’agent est réservé à un usage professionnel.

- Conservez-le sur un runtime dédié (VPS/VM/conteneur + utilisateur/comptes OS dédiés).
- Ne connectez pas ce runtime à des comptes Apple/Google personnels ni à des profils personnels de navigateur/gestionnaire de mots de passe.
- Si les utilisateurs sont adversaires les uns des autres, séparez par Gateway/hôte/utilisateur OS.

Détails du modèle de sécurité : [Sécurité](/fr/gateway/security).

## Utiliser des Nodes avec un VPS

Vous pouvez conserver la Gateway dans le cloud et appairer des **Nodes** sur vos appareils locaux
(Mac/iOS/Android/headless). Les Nodes fournissent les capacités locales d’écran/caméra/canvas et `system.run`
tandis que la Gateway reste dans le cloud.

Documentation : [Nodes](/fr/nodes), [CLI des Nodes](/cli/nodes).

## Réglage du démarrage pour les petites VM et les hôtes ARM

Si les commandes CLI semblent lentes sur des VM peu puissantes (ou des hôtes ARM), activez le cache de compilation des modules de Node :

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` améliore les temps de démarrage répétés des commandes.
- `OPENCLAW_NO_RESPAWN=1` évite le surcoût de démarrage supplémentaire d’un chemin d’auto-relance.
- La première exécution d’une commande réchauffe le cache ; les exécutions suivantes sont plus rapides.
- Pour les spécificités du Raspberry Pi, voir [Raspberry Pi](/fr/install/raspberry-pi).

### Liste de contrôle de réglage `systemd` (facultatif)

Pour les hôtes VM utilisant `systemd`, envisagez ce qui suit :

- Ajoutez des variables d’environnement du service pour un chemin de démarrage stable :
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- Gardez un comportement de redémarrage explicite :
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- Préférez des disques basés sur SSD pour les chemins d’état/cache afin de réduire les pénalités de démarrage à froid liées aux E/S aléatoires.

Pour le chemin standard `openclaw onboard --install-daemon`, modifiez l’unité utilisateur :

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

Si vous avez délibérément installé une unité système à la place, modifiez
`openclaw-gateway.service` via `sudo systemctl edit openclaw-gateway.service`.

Comment les politiques `Restart=` aident à la récupération automatisée :
[systemd peut automatiser la récupération des services](https://www.redhat.com/en/blog/systemd-automate-recovery).
