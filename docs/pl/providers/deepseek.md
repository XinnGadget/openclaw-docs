---
read_when:
    - Chcesz używać DeepSeek z OpenClaw
    - Potrzebujesz zmiennej środowiskowej klucza API lub wyboru uwierzytelniania w CLI
summary: Konfiguracja DeepSeek (uwierzytelnianie + wybór modelu)
title: DeepSeek
x-i18n:
    generated_at: "2026-04-12T23:30:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad06880bd1ab89f72f9e31f4927e2c099dcf6b4e0ff2b3fcc91a24468fbc089d
    source_path: providers/deepseek.md
    workflow: 15
---

# DeepSeek

[DeepSeek](https://www.deepseek.com) oferuje zaawansowane modele AI z API zgodnym z OpenAI.

| Właściwość | Wartość                   |
| ---------- | ------------------------- |
| Dostawca   | `deepseek`                |
| Uwierzytelnianie | `DEEPSEEK_API_KEY` |
| API        | zgodne z OpenAI           |
| Base URL   | `https://api.deepseek.com` |

## Pierwsze kroki

<Steps>
  <Step title="Pobierz swój klucz API">
    Utwórz klucz API na stronie [platform.deepseek.com](https://platform.deepseek.com/api_keys).
  </Step>
  <Step title="Uruchom onboarding">
    ```bash
    openclaw onboard --auth-choice deepseek-api-key
    ```

    To poprosi o Twój klucz API i ustawi `deepseek/deepseek-chat` jako model domyślny.

  </Step>
  <Step title="Sprawdź, czy modele są dostępne">
    ```bash
    openclaw models list --provider deepseek
    ```
  </Step>
</Steps>

<AccordionGroup>
  <Accordion title="Konfiguracja nieinteraktywna">
    W przypadku instalacji skryptowych lub bezobsługowych przekaż wszystkie flagi bezpośrednio:

    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice deepseek-api-key \
      --deepseek-api-key "$DEEPSEEK_API_KEY" \
      --skip-health \
      --accept-risk
    ```

  </Accordion>
</AccordionGroup>

<Warning>
Jeśli Gateway działa jako demon (launchd/systemd), upewnij się, że `DEEPSEEK_API_KEY`
jest dostępne dla tego procesu (na przykład w `~/.openclaw/.env` lub przez
`env.shellEnv`).
</Warning>

## Wbudowany katalog

| Odwołanie do modelu          | Nazwa             | Wejście | Kontekst | Maks. wyjście | Uwagi                                            |
| ---------------------------- | ----------------- | ------- | -------- | ------------- | ------------------------------------------------ |
| `deepseek/deepseek-chat`     | DeepSeek Chat     | text    | 131,072  | 8,192         | Model domyślny; powierzchnia DeepSeek V3.2 bez myślenia |
| `deepseek/deepseek-reasoner` | DeepSeek Reasoner | text    | 131,072  | 65,536        | Powierzchnia V3.2 z obsługą rozumowania          |

<Tip>
Oba dołączone modele obecnie deklarują w źródle zgodność z użyciem strumieniowym.
</Tip>

## Przykład konfiguracji

```json5
{
  env: { DEEPSEEK_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "deepseek/deepseek-chat" },
    },
  },
}
```

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Dokumentacja konfiguracji" href="/pl/gateway/configuration-reference" icon="gear">
    Pełna dokumentacja konfiguracji agentów, modeli i dostawców.
  </Card>
</CardGroup>
