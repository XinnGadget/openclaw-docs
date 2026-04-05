---
read_when:
    - Erstmalige Einrichtung von Grund auf
    - Du möchtest den schnellsten Weg zu einem funktionierenden Chat
summary: Installiere OpenClaw und starte deinen ersten Chat in wenigen Minuten.
title: Erste Schritte
x-i18n:
    generated_at: "2026-04-05T10:50:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: c43eee6f0d3f593e3cf0767bfacb3e0ae38f51a2615d594303786ae1d4a6d2c3
    source_path: start/getting-started.md
    workflow: 15
---

# Erste Schritte

Installiere OpenClaw, führe das Onboarding aus und chatte mit deinem KI-Assistenten — alles in
etwa 5 Minuten. Am Ende hast du ein laufendes Gateway, konfigurierte
Authentifizierung und eine funktionierende Chat-Sitzung.

## Was du brauchst

- **Node.js** — Node 24 empfohlen (Node 22.14+ wird ebenfalls unterstützt)
- **Einen API-Schlüssel** von einem Modell-Provider (Anthropic, OpenAI, Google usw.) — das Onboarding wird dich danach fragen

<Tip>
Prüfe deine Node-Version mit `node --version`.
**Windows-Nutzer:** Sowohl natives Windows als auch WSL2 werden unterstützt. WSL2 ist stabiler
und wird für die vollständige Nutzung empfohlen. Siehe [Windows](/platforms/windows).
Musst du Node installieren? Siehe [Node-Einrichtung](/install/node).
</Tip>

## Schnelleinrichtung

<Steps>
  <Step title="OpenClaw installieren">
    <Tabs>
      <Tab title="macOS / Linux">
        ```bash
        curl -fsSL https://openclaw.ai/install.sh | bash
        ```
        <img
  src="/assets/install-script.svg"
  alt="Installationsskript-Prozess"
  className="rounded-lg"
/>
      </Tab>
      <Tab title="Windows (PowerShell)">
        ```powershell
        iwr -useb https://openclaw.ai/install.ps1 | iex
        ```
      </Tab>
    </Tabs>

    <Note>
    Andere Installationsmethoden (Docker, Nix, npm): [Installation](/install).
    </Note>

  </Step>
  <Step title="Onboarding ausführen">
    ```bash
    openclaw onboard --install-daemon
    ```

    Der Assistent führt dich durch die Auswahl eines Modell-Providers, das Setzen eines API-Schlüssels
    und die Konfiguration des Gateways. Das dauert etwa 2 Minuten.

    Siehe [Onboarding (CLI)](/start/wizard) für die vollständige Referenz.

  </Step>
  <Step title="Prüfen, ob das Gateway läuft">
    ```bash
    openclaw gateway status
    ```

    Du solltest sehen, dass das Gateway auf Port 18789 lauscht.

  </Step>
  <Step title="Das Dashboard öffnen">
    ```bash
    openclaw dashboard
    ```

    Dadurch wird die Control UI in deinem Browser geöffnet. Wenn sie lädt, funktioniert alles.

  </Step>
  <Step title="Deine erste Nachricht senden">
    Gib eine Nachricht im Chat der Control UI ein, und du solltest eine KI-Antwort erhalten.

    Möchtest du stattdessen von deinem Smartphone aus chatten? Der am schnellsten einzurichtende Channel ist
    [Telegram](/channels/telegram) (nur ein Bot-Token). Siehe [Channels](/channels)
    für alle Optionen.

  </Step>
</Steps>

<Accordion title="Erweitert: einen benutzerdefinierten Build der Control UI einbinden">
  Wenn du einen lokalisierten oder angepassten Dashboard-Build pflegst, setze
  `gateway.controlUi.root` auf ein Verzeichnis, das deine gebauten statischen
  Assets und `index.html` enthält.

```bash
mkdir -p "$HOME/.openclaw/control-ui-custom"
# Kopiere deine gebauten statischen Dateien in dieses Verzeichnis.
```

Setze dann:

```json
{
  "gateway": {
    "controlUi": {
      "enabled": true,
      "root": "$HOME/.openclaw/control-ui-custom"
    }
  }
}
```

Starte das Gateway neu und öffne das Dashboard erneut:

```bash
openclaw gateway restart
openclaw dashboard
```

</Accordion>

## Was du als Nächstes tun kannst

<Columns>
  <Card title="Einen Channel verbinden" href="/channels" icon="message-square">
    Discord, Feishu, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo und mehr.
  </Card>
  <Card title="Pairing und Sicherheit" href="/channels/pairing" icon="shield">
    Lege fest, wer deinem Agenten Nachrichten senden kann.
  </Card>
  <Card title="Das Gateway konfigurieren" href="/gateway/configuration" icon="settings">
    Modelle, Tools, Sandbox und erweiterte Einstellungen.
  </Card>
  <Card title="Tools durchsuchen" href="/tools" icon="wrench">
    Browser, exec, Websuche, Skills und Plugins.
  </Card>
</Columns>

<Accordion title="Erweitert: Umgebungsvariablen">
  Wenn du OpenClaw als Dienstkonto ausführst oder benutzerdefinierte Pfade verwenden möchtest:

- `OPENCLAW_HOME` — Home-Verzeichnis für die interne Pfadauflösung
- `OPENCLAW_STATE_DIR` — überschreibt das Statusverzeichnis
- `OPENCLAW_CONFIG_PATH` — überschreibt den Pfad zur Konfigurationsdatei

Vollständige Referenz: [Umgebungsvariablen](/help/environment).
</Accordion>
