---
read_when:
    - Chcesz mieć jeden klucz API do wielu LLM-ów
    - Chcesz uruchamiać modele przez Gateway Kilo w OpenClaw
summary: Użyj ujednoliconego API Gateway Kilo, aby uzyskać dostęp do wielu modeli w OpenClaw
title: Kilocode
x-i18n:
    generated_at: "2026-04-12T23:31:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 32946f2187f3933115341cbe81006718b10583abc4deea7440b5e56366025f4a
    source_path: providers/kilocode.md
    workflow: 15
---

# Gateway Kilo

Gateway Kilo udostępnia **ujednolicone API**, które kieruje żądania do wielu modeli za pojedynczym
endpointem i kluczem API. Jest zgodne z OpenAI, więc większość SDK OpenAI działa po zmianie bazowego URL.

| Właściwość | Wartość                            |
| ---------- | ---------------------------------- |
| Dostawca   | `kilocode`                         |
| Auth       | `KILOCODE_API_KEY`                 |
| API        | zgodne z OpenAI                    |
| Bazowy URL | `https://api.kilo.ai/api/gateway/` |

## Pierwsze kroki

<Steps>
  <Step title="Utwórz konto">
    Przejdź do [app.kilo.ai](https://app.kilo.ai), zaloguj się lub utwórz konto, a następnie przejdź do API Keys i wygeneruj nowy klucz.
  </Step>
  <Step title="Uruchom onboarding">
    ```bash
    openclaw onboard --auth-choice kilocode-api-key
    ```

    Albo ustaw zmienną środowiskową bezpośrednio:

    ```bash
    export KILOCODE_API_KEY="<your-kilocode-api-key>" # pragma: allowlist secret
    ```

  </Step>
  <Step title="Sprawdź, czy model jest dostępny">
    ```bash
    openclaw models list --provider kilocode
    ```
  </Step>
</Steps>

## Model domyślny

Domyślnym modelem jest `kilocode/kilo/auto`, inteligentny model routingu należący do dostawcy,
zarządzany przez Gateway Kilo.

<Note>
OpenClaw traktuje `kilocode/kilo/auto` jako stabilne domyślne odwołanie, ale nie
publikuje mapowania zadanie → model upstream opartego na źródle dla tej trasy. Dokładne
routowanie upstream za `kilocode/kilo/auto` należy do Gateway Kilo, a nie jest
zakodowane na sztywno w OpenClaw.
</Note>

## Dostępne modele

OpenClaw dynamicznie wykrywa dostępne modele z Gateway Kilo przy uruchamianiu. Użyj
`/models kilocode`, aby zobaczyć pełną listę modeli dostępnych na Twoim koncie.

Każdy model dostępny w Gateway można użyć z prefiksem `kilocode/`:

| Odwołanie do modelu                    | Uwagi                             |
| -------------------------------------- | --------------------------------- |
| `kilocode/kilo/auto`                   | Domyślny — inteligentne routowanie |
| `kilocode/anthropic/claude-sonnet-4`   | Anthropic przez Kilo              |
| `kilocode/openai/gpt-5.4`              | OpenAI przez Kilo                 |
| `kilocode/google/gemini-3-pro-preview` | Google przez Kilo                 |
| ...i wiele innych                      | Użyj `/models kilocode`, aby wyświetlić wszystkie |

<Tip>
Przy uruchamianiu OpenClaw wykonuje zapytanie `GET https://api.kilo.ai/api/gateway/models` i scala
wykryte modele przed statycznym katalogiem awaryjnym. Bundlowy fallback zawsze
zawiera `kilocode/kilo/auto` (`Kilo Auto`) z `input: ["text", "image"]`,
`reasoning: true`, `contextWindow: 1000000` i `maxTokens: 128000`.
</Tip>

## Przykład konfiguracji

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" }, // pragma: allowlist secret
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Transport i zgodność">
    Gateway Kilo jest opisany w kodzie źródłowym jako zgodny z OpenRouter, więc pozostaje na
    ścieżce zgodnej z OpenAI w stylu proxy, zamiast natywnego kształtowania żądań OpenAI.

    - Odwołania Kilo oparte na Gemini pozostają na ścieżce proxy-Gemini, więc OpenClaw zachowuje
      tam sanityzację thought signature Gemini bez włączania natywnej walidacji replay Gemini
      ani przepisywania bootstrap.
    - Gateway Kilo wewnętrznie używa tokenu Bearer z Twoim kluczem API.

  </Accordion>

  <Accordion title="Wrapper strumienia i rozumowanie">
    Wspólny wrapper strumienia Kilo dodaje nagłówek aplikacji dostawcy i normalizuje
    payloady rozumowania proxy dla obsługiwanych konkretnych odwołań do modeli.

    <Warning>
    `kilocode/kilo/auto` i inne wskazówki bez obsługi proxy reasoning pomijają wstrzykiwanie rozumowania.
    Jeśli potrzebujesz obsługi rozumowania, użyj konkretnego odwołania do modelu, takiego jak
    `kilocode/anthropic/claude-sonnet-4`.
    </Warning>

  </Accordion>

  <Accordion title="Rozwiązywanie problemów">
    - Jeśli wykrywanie modeli nie powiedzie się przy uruchamianiu, OpenClaw wraca do bundlowego statycznego katalogu zawierającego `kilocode/kilo/auto`.
    - Potwierdź, że Twój klucz API jest prawidłowy i że na koncie Kilo włączono żądane modele.
    - Gdy Gateway działa jako demon, upewnij się, że `KILOCODE_API_KEY` jest dostępny dla tego procesu (na przykład w `~/.openclaw/.env` albo przez `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Informacje o konfiguracji" href="/pl/gateway/configuration" icon="gear">
    Pełne informacje o konfiguracji OpenClaw.
  </Card>
  <Card title="Gateway Kilo" href="https://app.kilo.ai" icon="arrow-up-right-from-square">
    Panel Gateway Kilo, klucze API i zarządzanie kontem.
  </Card>
</CardGroup>
