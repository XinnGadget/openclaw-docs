---
read_when:
    - Sie möchten das Gateway auf einem Linux-Server oder Cloud-VPS ausführen
    - Sie benötigen eine kurze Übersicht über Hosting-Anleitungen
    - Sie möchten allgemeine Linux-Server-Optimierung für OpenClaw】【。
sidebarTitle: Linux Server
summary: OpenClaw auf einem Linux-Server oder Cloud-VPS ausführen — Anbieterauswahl, Architektur und Optimierung
title: Linux-Server
x-i18n:
    generated_at: "2026-04-14T02:08:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: e623f4c770132e01628d66bfb8cd273bbef6dad633b812496c90da5e3e0f1383
    source_path: vps.md
    workflow: 15
---

# Linux-Server

Führen Sie das OpenClaw Gateway auf einem beliebigen Linux-Server oder Cloud-VPS aus. Diese Seite hilft Ihnen bei der Auswahl eines Anbieters, erklärt, wie Cloud-Bereitstellungen funktionieren, und behandelt allgemeine Linux-Optimierungen, die überall gelten.

## Anbieter auswählen

<CardGroup cols={2}>
  <Card title="Railway" href="/de/install/railway">Ein-Klick-, Browser-Einrichtung</Card>
  <Card title="Northflank" href="/de/install/northflank">Ein-Klick-, Browser-Einrichtung</Card>
  <Card title="DigitalOcean" href="/de/install/digitalocean">Einfacher kostenpflichtiger VPS</Card>
  <Card title="Oracle Cloud" href="/de/install/oracle">Always Free ARM-Stufe</Card>
  <Card title="Fly.io" href="/de/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/de/install/hetzner">Docker auf Hetzner-VPS</Card>
  <Card title="Hostinger" href="/de/install/hostinger">VPS mit Ein-Klick-Einrichtung</Card>
  <Card title="GCP" href="/de/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/de/install/azure">Linux-VM</Card>
  <Card title="exe.dev" href="/de/install/exe-dev">VM mit HTTPS-Proxy</Card>
  <Card title="Raspberry Pi" href="/de/install/raspberry-pi">ARM selbst gehostet</Card>
</CardGroup>

**AWS (EC2 / Lightsail / Free Tier)** funktioniert ebenfalls gut.
Eine von der Community erstellte Videoanleitung ist verfügbar unter
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
(Community-Ressource -- möglicherweise künftig nicht mehr verfügbar).

## So funktionieren Cloud-Setups

- Das **Gateway läuft auf dem VPS** und verwaltet Zustand + Workspace.
- Sie verbinden sich von Ihrem Laptop oder Smartphone über die **Control UI** oder **Tailscale/SSH**.
- Behandeln Sie den VPS als Source of Truth und erstellen Sie regelmäßig **Backups** von Zustand + Workspace.
- Sichere Standardeinstellung: Halten Sie das Gateway auf loopback und greifen Sie per SSH-Tunnel oder Tailscale Serve darauf zu.
  Wenn Sie an `lan` oder `tailnet` binden, verlangen Sie `gateway.auth.token` oder `gateway.auth.password`.

Verwandte Seiten: [Gateway-Fernzugriff](/de/gateway/remote), [Plattformen-Hub](/de/platforms).

## Gemeinsamer Unternehmens-Agent auf einem VPS

Das Ausführen eines einzelnen Agenten für ein Team ist ein gültiges Setup, wenn sich alle Benutzer innerhalb derselben Vertrauensgrenze befinden und der Agent ausschließlich geschäftlich genutzt wird.

- Halten Sie ihn auf einer dedizierten Laufzeitumgebung (VPS/VM/Container + dedizierter OS-Benutzer/Konten).
- Melden Sie diese Laufzeitumgebung nicht bei persönlichen Apple-/Google-Konten oder persönlichen Browser-/Passwortmanager-Profilen an.
- Wenn Benutzer einander gegenüber gegensätzlich agieren, trennen Sie nach Gateway/Host/OS-Benutzer.

Details zum Sicherheitsmodell: [Sicherheit](/de/gateway/security).

## Verwendung von Nodes mit einem VPS

Sie können das Gateway in der Cloud behalten und **Nodes** auf Ihren lokalen Geräten
(Mac/iOS/Android/headless) koppeln. Nodes stellen lokale Bildschirm-/Kamera-/Canvas- und `system.run`-
Funktionen bereit, während das Gateway in der Cloud bleibt.

Dokumentation: [Nodes](/de/nodes), [Nodes CLI](/cli/nodes).

## Startoptimierung für kleine VMs und ARM-Hosts

Wenn sich CLI-Befehle auf leistungsschwachen VMs (oder ARM-Hosts) langsam anfühlen, aktivieren Sie Nodes Modul-Kompilierungs-Cache:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` verbessert die Startzeiten bei wiederholter Befehlsausführung.
- `OPENCLAW_NO_RESPAWN=1` vermeidet zusätzlichen Start-Overhead durch einen Self-Respawn-Pfad.
- Der erste Befehlslauf wärmt den Cache auf; nachfolgende Läufe sind schneller.
- Einzelheiten für Raspberry Pi finden Sie unter [Raspberry Pi](/de/install/raspberry-pi).

### systemd-Optimierungs-Checkliste (optional)

Für VM-Hosts mit `systemd` sollten Sie Folgendes in Betracht ziehen:

- Fügen Sie Service-Umgebungsvariablen für einen stabilen Startpfad hinzu:
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- Halten Sie das Neustartverhalten explizit:
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- Bevorzugen Sie SSD-gestützte Datenträger für Zustand-/Cache-Pfade, um Cold-Start-Einbußen durch zufällige I/O zu verringern.

Für den standardmäßigen Pfad `openclaw onboard --install-daemon` bearbeiten Sie die User-Unit:

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

Wenn Sie stattdessen absichtlich eine System-Unit installiert haben, bearbeiten Sie
`openclaw-gateway.service` über `sudo systemctl edit openclaw-gateway.service`.

Wie `Restart=`-Richtlinien die automatische Wiederherstellung unterstützen:
[systemd kann die Dienstwiederherstellung automatisieren](https://www.redhat.com/en/blog/systemd-automate-recovery).
