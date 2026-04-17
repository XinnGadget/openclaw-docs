---
read_when:
    - Chcesz używać subskrypcji Claude Max z narzędziami zgodnymi z OpenAI
    - Chcesz lokalnego serwera API, który opakowuje CLI Claude Code
    - Chcesz ocenić dostęp do Anthropic oparty na subskrypcji w porównaniu z dostępem opartym na kluczu API
summary: Społecznościowy serwer proxy do udostępniania poświadczeń subskrypcji Claude jako endpointu zgodnego z OpenAI
title: Serwer proxy API Claude Max
x-i18n:
    generated_at: "2026-04-12T23:30:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 534bc3d189e68529fb090258eb0d6db6d367eb7e027ad04b1f0be55f6aa7d889
    source_path: providers/claude-max-api-proxy.md
    workflow: 15
---

# Serwer proxy API Claude Max

**claude-max-api-proxy** to narzędzie społecznościowe, które udostępnia Twoją subskrypcję Claude Max/Pro jako endpoint API zgodny z OpenAI. Dzięki temu możesz używać swojej subskrypcji z dowolnym narzędziem obsługującym format API OpenAI.

<Warning>
Ta ścieżka zapewnia wyłącznie zgodność techniczną. Anthropic w przeszłości blokował część użycia subskrypcji
poza Claude Code. Musisz samodzielnie zdecydować, czy chcesz z niej korzystać,
i sprawdzić aktualne warunki Anthropic, zanim zaczniesz na niej polegać.
</Warning>

## Dlaczego warto z tego korzystać?

| Podejście                | Koszt                                               | Najlepsze dla                              |
| ------------------------ | --------------------------------------------------- | ------------------------------------------ |
| API Anthropic            | Płatność za token (~15 USD/M wejścia, 75 USD/M wyjścia dla Opus) | Aplikacje produkcyjne, duży wolumen        |
| Subskrypcja Claude Max   | Stała opłata 200 USD/miesiąc                        | Użytek osobisty, rozwój, nieograniczone użycie |

Jeśli masz subskrypcję Claude Max i chcesz używać jej z narzędziami zgodnymi z OpenAI, ten serwer proxy może obniżyć koszty w niektórych przepływach pracy. Klucze API pozostają wyraźniej zgodną z zasadami ścieżką dla zastosowań produkcyjnych.

## Jak to działa

```
Twoja aplikacja → claude-max-api-proxy → CLI Claude Code → Anthropic (przez subskrypcję)
   (format OpenAI)         (konwersja formatu)         (używa Twojego logowania)
```

Serwer proxy:

1. Przyjmuje żądania w formacie OpenAI pod adresem `http://localhost:3456/v1/chat/completions`
2. Konwertuje je na polecenia CLI Claude Code
3. Zwraca odpowiedzi w formacie OpenAI (obsługiwane jest przesyłanie strumieniowe)

## Pierwsze kroki

<Steps>
  <Step title="Zainstaluj serwer proxy">
    Wymaga Node.js 20+ oraz CLI Claude Code.

    ```bash
    npm install -g claude-max-api-proxy

    # Sprawdź, czy CLI Claude jest uwierzytelnione
    claude --version
    ```

  </Step>
  <Step title="Uruchom serwer">
    ```bash
    claude-max-api
    # Serwer działa pod adresem http://localhost:3456
    ```
  </Step>
  <Step title="Przetestuj serwer proxy">
    ```bash
    # Kontrola stanu
    curl http://localhost:3456/health

    # Lista modeli
    curl http://localhost:3456/v1/models

    # Uzupełnianie czatu
    curl http://localhost:3456/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "claude-opus-4",
        "messages": [{"role": "user", "content": "Hello!"}]
      }'
    ```

  </Step>
  <Step title="Skonfiguruj OpenClaw">
    Skieruj OpenClaw na serwer proxy jako niestandardowy endpoint zgodny z OpenAI:

    ```json5
    {
      env: {
        OPENAI_API_KEY: "not-needed",
        OPENAI_BASE_URL: "http://localhost:3456/v1",
      },
      agents: {
        defaults: {
          model: { primary: "openai/claude-opus-4" },
        },
      },
    }
    ```

  </Step>
</Steps>

## Dostępne modele

| Identyfikator modelu | Mapowanie do     |
| -------------------- | ---------------- |
| `claude-opus-4`      | Claude Opus 4    |
| `claude-sonnet-4`    | Claude Sonnet 4  |
| `claude-haiku-4`     | Claude Haiku 4   |

## Zaawansowane

<AccordionGroup>
  <Accordion title="Uwagi o stylu proxy zgodnym z OpenAI">
    Ta ścieżka używa tej samej trasy proxy zgodnej z OpenAI co inne niestandardowe
    backendy `/v1`:

    - Natywne kształtowanie żądań tylko dla OpenAI nie ma tu zastosowania
    - Brak `service_tier`, brak `store` w Responses, brak wskazówek prompt-cache i brak
      kształtowania ładunku zgodności rozumowania OpenAI
    - Ukryte nagłówki atrybucji OpenClaw (`originator`, `version`, `User-Agent`)
      nie są wstrzykiwane do adresu URL serwera proxy

  </Accordion>

  <Accordion title="Automatyczne uruchamianie na macOS za pomocą LaunchAgent">
    Utwórz LaunchAgent, aby automatycznie uruchamiać serwer proxy:

    ```bash
    cat > ~/Library/LaunchAgents/com.claude-max-api.plist << 'EOF'
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
      <key>Label</key>
      <string>com.claude-max-api</string>
      <key>RunAtLoad</key>
      <true/>
      <key>KeepAlive</key>
      <true/>
      <key>ProgramArguments</key>
      <array>
        <string>/usr/local/bin/node</string>
        <string>/usr/local/lib/node_modules/claude-max-api-proxy/dist/server/standalone.js</string>
      </array>
      <key>EnvironmentVariables</key>
      <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:~/.local/bin:/usr/bin:/bin</string>
      </dict>
    </dict>
    </plist>
    EOF

    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude-max-api.plist
    ```

  </Accordion>
</AccordionGroup>

## Linki

- **npm:** [https://www.npmjs.com/package/claude-max-api-proxy](https://www.npmjs.com/package/claude-max-api-proxy)
- **GitHub:** [https://github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)
- **Zgłoszenia:** [https://github.com/atalovesyou/claude-max-api-proxy/issues](https://github.com/atalovesyou/claude-max-api-proxy/issues)

## Uwagi

- To **narzędzie społecznościowe**, nie jest oficjalnie wspierane przez Anthropic ani OpenClaw
- Wymaga aktywnej subskrypcji Claude Max/Pro z uwierzytelnionym CLI Claude Code
- Serwer proxy działa lokalnie i nie wysyła danych do żadnych serwerów zewnętrznych
- Odpowiedzi strumieniowe są w pełni obsługiwane

<Note>
Aby używać natywnej integracji Anthropic z CLI Claude lub kluczami API, zobacz [dostawca Anthropic](/pl/providers/anthropic). W przypadku subskrypcji OpenAI/Codex zobacz [dostawca OpenAI](/pl/providers/openai).
</Note>

## Powiązane

<CardGroup cols={2}>
  <Card title="Anthropic provider" href="/pl/providers/anthropic" icon="bolt">
    Natywna integracja OpenClaw z CLI Claude lub kluczami API.
  </Card>
  <Card title="OpenAI provider" href="/pl/providers/openai" icon="robot">
    Dla subskrypcji OpenAI/Codex.
  </Card>
  <Card title="Model providers" href="/pl/concepts/model-providers" icon="layers">
    Omówienie wszystkich dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Configuration" href="/pl/gateway/configuration" icon="gear">
    Pełna dokumentacja konfiguracji.
  </Card>
</CardGroup>
