---
read_when:
    - Einführung von OpenClaw für Neulinge
summary: OpenClaw ist ein Multi-Channel-Gateway für KI-Agenten, das auf jedem Betriebssystem läuft.
title: OpenClaw
x-i18n:
    generated_at: "2026-04-05T10:50:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9c29a8d9fc41a94b650c524bb990106f134345560e6d615dac30e8815afff481
    source_path: index.md
    workflow: 15
---

# OpenClaw 🦞

<p align="center">
    <img
        src="/assets/openclaw-logo-text-dark.png"
        alt="OpenClaw"
        width="500"
        class="dark:hidden"
    />
    <img
        src="/assets/openclaw-logo-text.png"
        alt="OpenClaw"
        width="500"
        class="hidden dark:block"
    />
</p>

> _"EXFOLIATE! EXFOLIATE!"_ — Ein Weltraum-Hummer, vermutlich

<p align="center">
  <strong>Gateway für KI-Agenten auf jedem Betriebssystem über Discord, Google Chat, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo und mehr hinweg.</strong><br />
  Sende eine Nachricht und erhalte eine Agentenantwort direkt aus deiner Hosentasche. Betreibe ein Gateway für integrierte Channels, gebündelte Channel-Plugins, WebChat und mobile Nodes.
</p>

<Columns>
  <Card title="Erste Schritte" href="/start/getting-started" icon="rocket">
    Installiere OpenClaw und bringe das Gateway in wenigen Minuten zum Laufen.
  </Card>
  <Card title="Onboarding ausführen" href="/start/wizard" icon="sparkles">
    Geführte Einrichtung mit `openclaw onboard` und Pairing-Abläufen.
  </Card>
  <Card title="Die Control UI öffnen" href="/web/control-ui" icon="layout-dashboard">
    Starte das Browser-Dashboard für Chat, Konfiguration und Sitzungen.
  </Card>
</Columns>

## Was ist OpenClaw?

OpenClaw ist ein **selbstgehostetes Gateway**, das deine bevorzugten Chat-Apps und Channel-Oberflächen — integrierte Channels plus gebündelte oder externe Channel-Plugins wie Discord, Google Chat, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo und mehr — mit KI-Coding-Agenten wie Pi verbindet. Du betreibst einen einzelnen Gateway-Prozess auf deinem eigenen Rechner (oder Server), und er wird zur Brücke zwischen deinen Messaging-Apps und einem jederzeit verfügbaren KI-Assistenten.

**Für wen ist es gedacht?** Für Entwickler und Power-User, die einen persönlichen KI-Assistenten möchten, den sie von überall aus anschreiben können — ohne die Kontrolle über ihre Daten aufzugeben oder sich auf einen gehosteten Dienst zu verlassen.

**Was macht es anders?**

- **Selbstgehostet**: läuft auf deiner Hardware, nach deinen Regeln
- **Multi-Channel**: ein Gateway bedient gleichzeitig integrierte Channels sowie gebündelte oder externe Channel-Plugins
- **Agent-nativ**: entwickelt für Coding-Agenten mit Tool-Nutzung, Sitzungen, Speicher und Multi-Agent-Routing
- **Open Source**: MIT-lizenziert, von der Community getragen

**Was brauchst du?** Node 24 (empfohlen) oder Node 22 LTS (`22.14+`) für Kompatibilität, einen API-Schlüssel deines gewählten Providers und 5 Minuten. Für die beste Qualität und Sicherheit solltest du das stärkste verfügbare Modell der neuesten Generation verwenden.

## So funktioniert es

```mermaid
flowchart LR
  A["Chat-Apps + Plugins"] --> B["Gateway"]
  B --> C["Pi-Agent"]
  B --> D["CLI"]
  B --> E["Web-Control-UI"]
  B --> F["macOS-App"]
  B --> G["iOS- und Android-Nodes"]
```

Das Gateway ist die zentrale Quelle der Wahrheit für Sitzungen, Routing und Channel-Verbindungen.

## Wichtige Funktionen

<Columns>
  <Card title="Multi-Channel-Gateway" icon="network">
    Discord, iMessage, Signal, Slack, Telegram, WhatsApp, WebChat und mehr mit einem einzigen Gateway-Prozess.
  </Card>
  <Card title="Plugin-Channels" icon="plug">
    Gebündelte Plugins fügen in normalen aktuellen Releases Matrix, Nostr, Twitch, Zalo und mehr hinzu.
  </Card>
  <Card title="Multi-Agent-Routing" icon="route">
    Isolierte Sitzungen pro Agent, Workspace oder Absender.
  </Card>
  <Card title="Medienunterstützung" icon="image">
    Sende und empfange Bilder, Audio und Dokumente.
  </Card>
  <Card title="Web-Control-UI" icon="monitor">
    Browser-Dashboard für Chat, Konfiguration, Sitzungen und Nodes.
  </Card>
  <Card title="Mobile Nodes" icon="smartphone">
    Kopple iOS- und Android-Nodes für Canvas-, Kamera- und sprachgestützte Workflows.
  </Card>
</Columns>

## Schnellstart

<Steps>
  <Step title="OpenClaw installieren">
    ```bash
    npm install -g openclaw@latest
    ```
  </Step>
  <Step title="Onboarding durchführen und den Dienst installieren">
    ```bash
    openclaw onboard --install-daemon
    ```
  </Step>
  <Step title="Chatten">
    Öffne die Control UI in deinem Browser und sende eine Nachricht:

    ```bash
    openclaw dashboard
    ```

    Oder verbinde einen Channel ([Telegram](/channels/telegram) ist am schnellsten) und chatte von deinem Smartphone aus.

  </Step>
</Steps>

Brauchst du die vollständige Installations- und Entwicklungsumgebung? Siehe [Erste Schritte](/start/getting-started).

## Dashboard

Öffne die browserbasierte Control UI, nachdem das Gateway gestartet wurde.

- Lokaler Standard: [http://127.0.0.1:18789/](http://127.0.0.1:18789/)
- Remote-Zugriff: [Web-Oberflächen](/web) und [Tailscale](/gateway/tailscale)

<p align="center">
  <img src="/whatsapp-openclaw.jpg" alt="OpenClaw" width="420" />
</p>

## Konfiguration (optional)

Die Konfiguration befindet sich unter `~/.openclaw/openclaw.json`.

- Wenn du **nichts tust**, verwendet OpenClaw die gebündelte Pi-Binärdatei im RPC-Modus mit Sitzungen pro Absender.
- Wenn du es einschränken möchtest, beginne mit `channels.whatsapp.allowFrom` und (für Gruppen) Erwähnungsregeln.

Beispiel:

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  messages: { groupChat: { mentionPatterns: ["@openclaw"] } },
}
```

## Hier anfangen

<Columns>
  <Card title="Dokumentations-Hubs" href="/start/hubs" icon="book-open">
    Alle Dokumentationen und Anleitungen, nach Anwendungsfall geordnet.
  </Card>
  <Card title="Konfiguration" href="/gateway/configuration" icon="settings">
    Zentrale Gateway-Einstellungen, Tokens und Provider-Konfiguration.
  </Card>
  <Card title="Remote-Zugriff" href="/gateway/remote" icon="globe">
    SSH- und Tailnet-Zugriffsmuster.
  </Card>
  <Card title="Channels" href="/channels/telegram" icon="message-square">
    Channel-spezifische Einrichtung für Feishu, Microsoft Teams, WhatsApp, Telegram, Discord und mehr.
  </Card>
  <Card title="Nodes" href="/nodes" icon="smartphone">
    iOS- und Android-Nodes mit Pairing, Canvas, Kamera und Geräteaktionen.
  </Card>
  <Card title="Hilfe" href="/help" icon="life-buoy">
    Häufige Lösungen und zentraler Einstiegspunkt zur Fehlerbehebung.
  </Card>
</Columns>

## Mehr erfahren

<Columns>
  <Card title="Vollständige Funktionsliste" href="/concepts/features" icon="list">
    Vollständige Übersicht über Channel-, Routing- und Medienfunktionen.
  </Card>
  <Card title="Multi-Agent-Routing" href="/concepts/multi-agent" icon="route">
    Workspace-Isolierung und Sitzungen pro Agent.
  </Card>
  <Card title="Sicherheit" href="/gateway/security" icon="shield">
    Tokens, Zulassungslisten und Sicherheitskontrollen.
  </Card>
  <Card title="Fehlerbehebung" href="/gateway/troubleshooting" icon="wrench">
    Gateway-Diagnose und häufige Fehler.
  </Card>
  <Card title="Über das Projekt und Danksagungen" href="/reference/credits" icon="info">
    Projektursprünge, Mitwirkende und Lizenz.
  </Card>
</Columns>
