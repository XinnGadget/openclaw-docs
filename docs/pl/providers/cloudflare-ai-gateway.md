---
read_when:
    - Chcesz używać Cloudflare AI Gateway z OpenClaw
    - Potrzebujesz identyfikatora konta, identyfikatora Gateway lub zmiennej środowiskowej klucza API
summary: Konfiguracja Cloudflare AI Gateway (uwierzytelnianie + wybór modelu)
title: Cloudflare AI Gateway
x-i18n:
    generated_at: "2026-04-12T23:30:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 12e9589fe74e6a6335370b9cf2361a464876a392a33f8317d7fd30c3f163b2e5
    source_path: providers/cloudflare-ai-gateway.md
    workflow: 15
---

# Cloudflare AI Gateway

Cloudflare AI Gateway znajduje się przed API dostawców i umożliwia dodanie analityki, cache oraz mechanizmów kontrolnych. W przypadku Anthropic OpenClaw używa Anthropic Messages API przez endpoint Twojego Gateway.

| Właściwość   | Wartość                                                                                 |
| ------------ | --------------------------------------------------------------------------------------- |
| Dostawca     | `cloudflare-ai-gateway`                                                                 |
| Bazowy URL   | `https://gateway.ai.cloudflare.com/v1/<account_id>/<gateway_id>/anthropic`             |
| Model domyślny | `cloudflare-ai-gateway/claude-sonnet-4-5`                                             |
| Klucz API    | `CLOUDFLARE_AI_GATEWAY_API_KEY` (Twój klucz API dostawcy dla żądań przez Gateway)      |

<Note>
W przypadku modeli Anthropic routowanych przez Cloudflare AI Gateway używaj swojego **klucza API Anthropic** jako klucza dostawcy.
</Note>

## Pierwsze kroki

<Steps>
  <Step title="Ustaw klucz API dostawcy i szczegóły Gateway">
    Uruchom onboarding i wybierz opcję uwierzytelniania Cloudflare AI Gateway:

    ```bash
    openclaw onboard --auth-choice cloudflare-ai-gateway-api-key
    ```

    To poprosi o identyfikator konta, identyfikator Gateway i klucz API.

  </Step>
  <Step title="Ustaw model domyślny">
    Dodaj model do swojej konfiguracji OpenClaw:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "cloudflare-ai-gateway/claude-sonnet-4-5" },
        },
      },
    }
    ```

  </Step>
  <Step title="Sprawdź, czy model jest dostępny">
    ```bash
    openclaw models list --provider cloudflare-ai-gateway
    ```
  </Step>
</Steps>

## Przykład nieinteraktywny

W przypadku konfiguracji skryptowych lub CI przekaż wszystkie wartości w wierszu poleceń:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice cloudflare-ai-gateway-api-key \
  --cloudflare-ai-gateway-account-id "your-account-id" \
  --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
  --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY"
```

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Gateway z uwierzytelnianiem">
    Jeśli włączyłeś uwierzytelnianie Gateway w Cloudflare, dodaj nagłówek `cf-aig-authorization`. Jest to **dodatkowe** względem klucza API dostawcy.

    ```json5
    {
      models: {
        providers: {
          "cloudflare-ai-gateway": {
            headers: {
              "cf-aig-authorization": "Bearer <cloudflare-ai-gateway-token>",
            },
          },
        },
      },
    }
    ```

    <Tip>
    Nagłówek `cf-aig-authorization` uwierzytelnia wobec samego Cloudflare Gateway, podczas gdy klucz API dostawcy (na przykład Twój klucz Anthropic) uwierzytelnia wobec dostawcy upstream.
    </Tip>

  </Accordion>

  <Accordion title="Uwaga dotycząca środowiska">
    Jeśli Gateway działa jako demon (launchd/systemd), upewnij się, że `CLOUDFLARE_AI_GATEWAY_API_KEY` jest dostępny dla tego procesu.

    <Warning>
    Klucz znajdujący się wyłącznie w `~/.profile` nie pomoże demonowi launchd/systemd, chyba że to środowisko również zostanie tam zaimportowane. Ustaw klucz w `~/.openclaw/.env` lub przez `env.shellEnv`, aby mieć pewność, że proces gateway może go odczytać.
    </Warning>

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, referencji modeli i zachowania failover.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Ogólne rozwiązywanie problemów i FAQ.
  </Card>
</CardGroup>
