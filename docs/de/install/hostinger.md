---
read_when:
    - OpenClaw auf Hostinger einrichten
    - Suche nach einem verwalteten VPS für OpenClaw
    - Hostinger 1-Klick-OpenClaw verwenden
summary: OpenClaw auf Hostinger hosten
title: Hostinger
x-i18n:
    generated_at: "2026-04-14T02:08:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: cf173cdcf6344f8ee22e839a27f4e063a3a102186f9acc07c4a33d4794e2c034
    source_path: install/hostinger.md
    workflow: 15
---

# Hostinger

Führen Sie ein dauerhaftes OpenClaw Gateway auf [Hostinger](https://www.hostinger.com/openclaw) aus – entweder über eine verwaltete **1-Klick**-Bereitstellung oder eine **VPS**-Installation.

## Voraussetzungen

- Hostinger-Konto ([Registrierung](https://www.hostinger.com/openclaw))
- Etwa 5–10 Minuten

## Option A: 1-Klick-OpenClaw

Der schnellste Weg für den Einstieg. Hostinger übernimmt Infrastruktur, Docker und automatische Updates.

<Steps>
  <Step title="Kaufen und starten">
    1. Wählen Sie auf der [Hostinger OpenClaw-Seite](https://www.hostinger.com/openclaw) einen Managed-OpenClaw-Tarif aus und schließen Sie den Kauf ab.

    <Note>
    Während des Bezahlvorgangs können Sie **Ready-to-Use AI**-Guthaben auswählen, die vorab gekauft und sofort in OpenClaw integriert werden – es sind keine externen Konten oder API-Schlüssel anderer Anbieter erforderlich. Sie können sofort mit dem Chatten beginnen. Alternativ können Sie während der Einrichtung Ihren eigenen Schlüssel von Anthropic, OpenAI, Google Gemini oder xAI angeben.
    </Note>

  </Step>

  <Step title="Einen Messaging-Kanal auswählen">
    Wählen Sie einen oder mehrere Kanäle zum Verbinden aus:

    - **WhatsApp** -- Scannen Sie den im Einrichtungsassistenten angezeigten QR-Code.
    - **Telegram** -- Fügen Sie das Bot-Token von [BotFather](https://t.me/BotFather) ein.

  </Step>

  <Step title="Installation abschließen">
    Klicken Sie auf **Finish**, um die Instanz bereitzustellen. Sobald alles bereit ist, greifen Sie über **OpenClaw Overview** in hPanel auf das OpenClaw-Dashboard zu.
  </Step>

</Steps>

## Option B: OpenClaw auf VPS

Mehr Kontrolle über Ihren Server. Hostinger stellt OpenClaw über Docker auf Ihrem VPS bereit, und Sie verwalten es über den **Docker Manager** in hPanel.

<Steps>
  <Step title="Einen VPS kaufen">
    1. Wählen Sie auf der [Hostinger OpenClaw-Seite](https://www.hostinger.com/openclaw) einen Tarif für OpenClaw auf VPS aus und schließen Sie den Kauf ab.

    <Note>
    Sie können während des Bezahlvorgangs **Ready-to-Use AI**-Guthaben auswählen – diese werden im Voraus gekauft und sofort in OpenClaw integriert, sodass Sie ohne externe Konten oder API-Schlüssel anderer Anbieter mit dem Chatten beginnen können.
    </Note>

  </Step>

  <Step title="OpenClaw konfigurieren">
    Sobald der VPS bereitgestellt ist, füllen Sie die Konfigurationsfelder aus:

    - **Gateway-Token** -- wird automatisch generiert; speichern Sie es für die spätere Verwendung.
    - **WhatsApp-Nummer** -- Ihre Nummer mit Ländervorwahl (optional).
    - **Telegram-Bot-Token** -- von [BotFather](https://t.me/BotFather) (optional).
    - **API-Schlüssel** -- nur erforderlich, wenn Sie während des Bezahlvorgangs keine Ready-to-Use AI-Guthaben ausgewählt haben.

  </Step>

  <Step title="OpenClaw starten">
    Klicken Sie auf **Deploy**. Sobald es läuft, öffnen Sie das OpenClaw-Dashboard in hPanel, indem Sie auf **Open** klicken.
  </Step>

</Steps>

Protokolle, Neustarts und Updates werden direkt über die Docker-Manager-Oberfläche in hPanel verwaltet. Um zu aktualisieren, klicken Sie im Docker Manager auf **Update**; dadurch wird das neueste Image geladen.

## Einrichtung überprüfen

Senden Sie „Hi“ an Ihren Assistenten auf dem Kanal, den Sie verbunden haben. OpenClaw antwortet und führt Sie durch die anfänglichen Einstellungen.

## Fehlerbehebung

**Dashboard lädt nicht** -- Warten Sie einige Minuten, bis der Container vollständig bereitgestellt ist. Prüfen Sie die Docker-Manager-Protokolle in hPanel.

**Docker-Container startet ständig neu** -- Öffnen Sie die Docker-Manager-Protokolle und suchen Sie nach Konfigurationsfehlern (fehlende Tokens, ungültige API-Schlüssel).

**Telegram-Bot antwortet nicht** -- Senden Sie Ihre Pairing-Code-Nachricht direkt aus Telegram als Nachricht in Ihrem OpenClaw-Chat, um die Verbindung abzuschließen.

## Nächste Schritte

- [Kanäle](/de/channels) -- Telegram, WhatsApp, Discord und mehr verbinden
- [Gateway-Konfiguration](/de/gateway/configuration) -- alle Konfigurationsoptionen
