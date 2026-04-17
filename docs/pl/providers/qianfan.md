---
read_when:
    - Chcesz używać jednego klucza API do wielu LLM-ów
    - Potrzebujesz wskazówek dotyczących konfiguracji Baidu Qianfan
summary: Używaj ujednoliconego API Qianfan, aby uzyskać dostęp do wielu modeli w OpenClaw
title: Qianfan
x-i18n:
    generated_at: "2026-04-12T23:32:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1d0eeee9ec24b335c2fb8ac5e985a9edc35cfc5b2641c545cb295dd2de619f50
    source_path: providers/qianfan.md
    workflow: 15
---

# Qianfan

Qianfan to platforma MaaS firmy Baidu, zapewniająca **ujednolicone API**, które kieruje żądania do wielu modeli za jednym
endpointem i kluczem API. Jest zgodne z OpenAI, więc większość SDK OpenAI działa po zmianie bazowego URL.

| Właściwość | Wartość                          |
| ---------- | -------------------------------- |
| Dostawca   | `qianfan`                        |
| Uwierzytelnianie | `QIANFAN_API_KEY`          |
| API        | Zgodne z OpenAI                  |
| Bazowy URL | `https://qianfan.baidubce.com/v2` |

## Pierwsze kroki

<Steps>
  <Step title="Utwórz konto Baidu Cloud">
    Zarejestruj się lub zaloguj w [Qianfan Console](https://console.bce.baidu.com/qianfan/ais/console/apiKey) i upewnij się, że masz włączony dostęp do API Qianfan.
  </Step>
  <Step title="Wygeneruj klucz API">
    Utwórz nową aplikację albo wybierz istniejącą, a następnie wygeneruj klucz API. Format klucza to `bce-v3/ALTAK-...`.
  </Step>
  <Step title="Uruchom onboarding">
    ```bash
    openclaw onboard --auth-choice qianfan-api-key
    ```
  </Step>
  <Step title="Sprawdź, czy model jest dostępny">
    ```bash
    openclaw models list --provider qianfan
    ```
  </Step>
</Steps>

## Dostępne modele

| Odwołanie modelu                    | Wejście     | Kontekst | Maks. wyjście | Reasoning | Uwagi            |
| ----------------------------------- | ----------- | -------- | ------------- | --------- | ---------------- |
| `qianfan/deepseek-v3.2`             | text        | 98,304   | 32,768        | Tak       | Model domyślny   |
| `qianfan/ernie-5.0-thinking-preview`| text, image | 119,000  | 64,000        | Tak       | Multimodalny     |

<Tip>
Domyślnym dołączonym odwołaniem do modelu jest `qianfan/deepseek-v3.2`. `models.providers.qianfan` trzeba nadpisywać tylko wtedy, gdy potrzebujesz niestandardowego bazowego URL albo metadanych modelu.
</Tip>

## Przykład konfiguracji

```json5
{
  env: { QIANFAN_API_KEY: "bce-v3/ALTAK-..." },
  agents: {
    defaults: {
      model: { primary: "qianfan/deepseek-v3.2" },
      models: {
        "qianfan/deepseek-v3.2": { alias: "QIANFAN" },
      },
    },
  },
  models: {
    providers: {
      qianfan: {
        baseUrl: "https://qianfan.baidubce.com/v2",
        api: "openai-completions",
        models: [
          {
            id: "deepseek-v3.2",
            name: "DEEPSEEK V3.2",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 98304,
            maxTokens: 32768,
          },
          {
            id: "ernie-5.0-thinking-preview",
            name: "ERNIE-5.0-Thinking-Preview",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 119000,
            maxTokens: 64000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Transport i zgodność">
    Qianfan działa przez ścieżkę transportu zgodną z OpenAI, a nie przez natywne formatowanie żądań OpenAI. Oznacza to, że standardowe funkcje SDK OpenAI działają, ale parametry specyficzne dla dostawcy mogą nie być przekazywane dalej.
  </Accordion>

  <Accordion title="Katalog i nadpisania">
    Dołączony katalog zawiera obecnie `deepseek-v3.2` i `ernie-5.0-thinking-preview`. Dodawaj lub nadpisuj `models.providers.qianfan` tylko wtedy, gdy potrzebujesz niestandardowego bazowego URL albo metadanych modelu.

    <Note>
    Odwołania do modeli używają prefiksu `qianfan/` (na przykład `qianfan/deepseek-v3.2`).
    </Note>

  </Accordion>

  <Accordion title="Rozwiązywanie problemów">
    - Upewnij się, że Twój klucz API zaczyna się od `bce-v3/ALTAK-` i ma włączony dostęp do API Qianfan w konsoli Baidu Cloud.
    - Jeśli modele nie są wyświetlane, potwierdź, że na Twoim koncie usługa Qianfan jest aktywna.
    - Domyślny bazowy URL to `https://qianfan.baidubce.com/v2`. Zmieniaj go tylko wtedy, gdy używasz niestandardowego endpointu albo proxy.
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Referencja konfiguracji" href="/pl/gateway/configuration" icon="gear">
    Pełna referencja konfiguracji OpenClaw.
  </Card>
  <Card title="Konfiguracja agenta" href="/pl/concepts/agent" icon="robot">
    Konfigurowanie domyślnych ustawień agenta i przypisań modeli.
  </Card>
  <Card title="Dokumentacja API Qianfan" href="https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb" icon="arrow-up-right-from-square">
    Oficjalna dokumentacja API Qianfan.
  </Card>
</CardGroup>
