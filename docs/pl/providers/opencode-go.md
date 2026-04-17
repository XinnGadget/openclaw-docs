---
read_when:
    - Chcesz używać katalogu OpenCode Go
    - Potrzebujesz referencji modeli runtime dla modeli hostowanych przez Go
summary: Używanie katalogu OpenCode Go ze współdzieloną konfiguracją OpenCode
title: OpenCode Go
x-i18n:
    generated_at: "2026-04-12T23:32:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: d1f0f182de81729616ccc19125d93ba0445de2349daf7067b52e8c15b9d3539c
    source_path: providers/opencode-go.md
    workflow: 15
---

# OpenCode Go

OpenCode Go to katalog Go w ramach [OpenCode](/pl/providers/opencode).
Używa tego samego `OPENCODE_API_KEY` co katalog Zen, ale zachowuje identyfikator
dostawcy runtime `opencode-go`, aby routing upstream per model pozostawał poprawny.

| Właściwość      | Wartość                        |
| --------------- | ------------------------------ |
| Dostawca runtime | `opencode-go`                  |
| Uwierzytelnianie | `OPENCODE_API_KEY`             |
| Konfiguracja nadrzędna | [OpenCode](/pl/providers/opencode) |

## Obsługiwane modele

| Model ref                  | Nazwa         |
| -------------------------- | ------------- |
| `opencode-go/kimi-k2.5`    | Kimi K2.5     |
| `opencode-go/glm-5`        | GLM 5         |
| `opencode-go/minimax-m2.5` | MiniMax M2.5  |

## Pierwsze kroki

<Tabs>
  <Tab title="Interaktywnie">
    <Steps>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```
      </Step>
      <Step title="Ustaw model Go jako domyślny">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode-go/kimi-k2.5"
        ```
      </Step>
      <Step title="Sprawdź, czy modele są dostępne">
        ```bash
        openclaw models list --provider opencode-go
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="Nieinteraktywnie">
    <Steps>
      <Step title="Przekaż klucz bezpośrednio">
        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Sprawdź, czy modele są dostępne">
        ```bash
        openclaw models list --provider opencode-go
        ```
      </Step>
    </Steps>
  </Tab>
</Tabs>

## Przykład konfiguracji

```json5
{
  env: { OPENCODE_API_KEY: "YOUR_API_KEY_HERE" }, // pragma: allowlist secret
  agents: { defaults: { model: { primary: "opencode-go/kimi-k2.5" } } },
}
```

## Uwagi zaawansowane

<AccordionGroup>
  <Accordion title="Zachowanie routingu">
    OpenClaw automatycznie obsługuje routing per model, gdy referencja modelu używa
    `opencode-go/...`. Nie jest wymagana żadna dodatkowa konfiguracja dostawcy.
  </Accordion>

  <Accordion title="Konwencja referencji runtime">
    Referencje runtime pozostają jawne: `opencode/...` dla Zen, `opencode-go/...` dla Go.
    Dzięki temu routing upstream per model pozostaje poprawny w obu katalogach.
  </Accordion>

  <Accordion title="Współdzielone poświadczenia">
    To samo `OPENCODE_API_KEY` jest używane zarówno przez katalog Zen, jak i Go. Wprowadzenie
    klucza podczas konfiguracji zapisuje poświadczenia dla obu dostawców runtime.
  </Accordion>
</AccordionGroup>

<Tip>
Zobacz [OpenCode](/pl/providers/opencode), aby poznać wspólny przegląd onboardingu oraz pełną
dokumentację katalogów Zen + Go.
</Tip>

## Powiązane

<CardGroup cols={2}>
  <Card title="OpenCode (nadrzędne)" href="/pl/providers/opencode" icon="server">
    Wspólny onboarding, przegląd katalogu i uwagi zaawansowane.
  </Card>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, referencji modeli i zachowania failover.
  </Card>
</CardGroup>
