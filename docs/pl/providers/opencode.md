---
read_when:
    - Chcesz uzyskać dostęp do modeli hostowanych przez OpenCode
    - Chcesz wybierać między katalogami Zen i Go
summary: Używanie katalogów OpenCode Zen i Go w OpenClaw
title: OpenCode
x-i18n:
    generated_at: "2026-04-12T23:32:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: a68444d8c403c3caba4a18ea47f078c7a4c163f874560e1fad0e818afb6e0e60
    source_path: providers/opencode.md
    workflow: 15
---

# OpenCode

OpenCode udostępnia dwa hostowane katalogi w OpenClaw:

| Katalog | Prefiks           | Dostawca runtime |
| ------- | ----------------- | ---------------- |
| **Zen** | `opencode/...`    | `opencode`       |
| **Go**  | `opencode-go/...` | `opencode-go`    |

Oba katalogi używają tego samego klucza API OpenCode. OpenClaw zachowuje rozdzielone identyfikatory
dostawców runtime, aby routing upstream per model pozostawał poprawny, ale onboarding i dokumentacja traktują je
jako jedną konfigurację OpenCode.

## Pierwsze kroki

<Tabs>
  <Tab title="Katalog Zen">
    **Najlepszy do:** wyselekcjonowanego wielomodelowego proxy OpenCode (Claude, GPT, Gemini).

    <Steps>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-zen
        ```

        Lub przekaż klucz bezpośrednio:

        ```bash
        openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Ustaw model Zen jako domyślny">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode/claude-opus-4-6"
        ```
      </Step>
      <Step title="Sprawdź, czy modele są dostępne">
        ```bash
        openclaw models list --provider opencode
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Katalog Go">
    **Najlepszy do:** linii modeli Kimi, GLM i MiniMax hostowanych przez OpenCode.

    <Steps>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```

        Lub przekaż klucz bezpośrednio:

        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
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
</Tabs>

## Przykład konfiguracji

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

## Katalogi

### Zen

| Właściwość      | Wartość                                                                  |
| --------------- | ------------------------------------------------------------------------ |
| Dostawca runtime | `opencode`                                                               |
| Przykładowe modele | `opencode/claude-opus-4-6`, `opencode/gpt-5.4`, `opencode/gemini-3-pro` |

### Go

| Właściwość      | Wartość                                                                   |
| --------------- | ------------------------------------------------------------------------- |
| Dostawca runtime | `opencode-go`                                                             |
| Przykładowe modele | `opencode-go/kimi-k2.5`, `opencode-go/glm-5`, `opencode-go/minimax-m2.5` |

## Uwagi zaawansowane

<AccordionGroup>
  <Accordion title="Aliasy klucza API">
    `OPENCODE_ZEN_API_KEY` jest także obsługiwany jako alias dla `OPENCODE_API_KEY`.
  </Accordion>

  <Accordion title="Współdzielone poświadczenia">
    Wprowadzenie jednego klucza OpenCode podczas konfiguracji zapisuje poświadczenia dla obu
    dostawców runtime. Nie musisz przechodzić onboardingu dla każdego katalogu osobno.
  </Accordion>

  <Accordion title="Rozliczenia i panel">
    Logujesz się do OpenCode, dodajesz dane rozliczeniowe i kopiujesz swój klucz API. Rozliczenia
    i dostępność katalogów są zarządzane z panelu OpenCode.
  </Accordion>

  <Accordion title="Zachowanie odtwarzania Gemini">
    Referencje OpenCode oparte na Gemini pozostają na ścieżce proxy-Gemini, więc OpenClaw zachowuje tam
    sanityzację thought-signature Gemini bez włączania natywnej walidacji odtwarzania Gemini
    ani przepisywania bootstrapu.
  </Accordion>

  <Accordion title="Zachowanie odtwarzania inne niż Gemini">
    Referencje OpenCode inne niż Gemini zachowują minimalną politykę odtwarzania zgodną z OpenAI.
  </Accordion>
</AccordionGroup>

<Tip>
Wprowadzenie jednego klucza OpenCode podczas konfiguracji zapisuje poświadczenia dla dostawców runtime Zen i
Go, więc onboarding wystarczy przejść tylko raz.
</Tip>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, referencji modeli i zachowania failover.
  </Card>
  <Card title="Dokumentacja konfiguracji" href="/pl/gateway/configuration-reference" icon="gear">
    Pełna dokumentacja konfiguracji agentów, modeli i dostawców.
  </Card>
</CardGroup>
