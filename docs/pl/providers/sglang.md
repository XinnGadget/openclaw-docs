---
read_when:
    - Chcesz uruchomić OpenClaw z lokalnym serwerem SGLang
    - Chcesz używać endpointów `/v1` zgodnych z OpenAI z własnymi modelami
summary: Uruchamiaj OpenClaw z SGLang (samodzielnie hostowany serwer zgodny z OpenAI)
title: SGLang
x-i18n:
    generated_at: "2026-04-12T23:33:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0a2e50a499c3d25dcdc3af425fb023c6e3f19ed88f533ecf0eb8a2cb7ec8b0d
    source_path: providers/sglang.md
    workflow: 15
---

# SGLang

SGLang może udostępniać modele open source przez **API HTTP zgodne z OpenAI**.
OpenClaw może łączyć się z SGLang przy użyciu API `openai-completions`.

OpenClaw może także **automatycznie wykrywać** dostępne modele z SGLang, gdy
jawnie to włączysz przez `SGLANG_API_KEY` (dowolna wartość działa, jeśli Twój serwer nie wymusza auth)
i nie zdefiniujesz jawnego wpisu `models.providers.sglang`.

## Pierwsze kroki

<Steps>
  <Step title="Uruchom SGLang">
    Uruchom SGLang z serwerem zgodnym z OpenAI. Twój bazowy URL powinien udostępniać
    endpointy `/v1` (na przykład `/v1/models`, `/v1/chat/completions`). SGLang
    często działa pod adresem:

    - `http://127.0.0.1:30000/v1`

  </Step>
  <Step title="Ustaw klucz API">
    Dowolna wartość działa, jeśli na serwerze nie skonfigurowano auth:

    ```bash
    export SGLANG_API_KEY="sglang-local"
    ```

  </Step>
  <Step title="Uruchom onboarding albo ustaw model bezpośrednio">
    ```bash
    openclaw onboard
    ```

    Albo skonfiguruj model ręcznie:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "sglang/your-model-id" },
        },
      },
    }
    ```

  </Step>
</Steps>

## Wykrywanie modeli (niejawny dostawca)

Gdy `SGLANG_API_KEY` jest ustawione (albo istnieje profil auth) i **nie**
zdefiniujesz `models.providers.sglang`, OpenClaw wykona zapytanie:

- `GET http://127.0.0.1:30000/v1/models`

i przekształci zwrócone identyfikatory w wpisy modeli.

<Note>
Jeśli jawnie ustawisz `models.providers.sglang`, automatyczne wykrywanie zostanie pominięte i
musisz ręcznie zdefiniować modele.
</Note>

## Jawna konfiguracja (modele ręczne)

Użyj jawnej konfiguracji, gdy:

- SGLang działa na innym hoście/porcie.
- Chcesz przypiąć wartości `contextWindow`/`maxTokens`.
- Twój serwer wymaga prawdziwego klucza API (albo chcesz kontrolować nagłówki).

```json5
{
  models: {
    providers: {
      sglang: {
        baseUrl: "http://127.0.0.1:30000/v1",
        apiKey: "${SGLANG_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "Lokalny model SGLang",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Zachowanie w stylu proxy">
    SGLang jest traktowany jako backend `/v1` zgodny z OpenAI w stylu proxy, a nie
    natywny endpoint OpenAI.

    | Zachowanie | SGLang |
    |----------|--------|
    | Kształtowanie żądań tylko dla OpenAI | Nie jest stosowane |
    | `service_tier`, `store` w Responses, wskazówki prompt-cache | Nie są wysyłane |
    | Kształtowanie payloadów zgodności reasoning | Nie jest stosowane |
    | Ukryte nagłówki atrybucji (`originator`, `version`, `User-Agent`) | Nie są wstrzykiwane przy niestandardowych bazowych URL-ach SGLang |

  </Accordion>

  <Accordion title="Rozwiązywanie problemów">
    **Nie można połączyć się z serwerem**

    Sprawdź, czy serwer działa i odpowiada:

    ```bash
    curl http://127.0.0.1:30000/v1/models
    ```

    **Błędy auth**

    Jeśli żądania kończą się błędami auth, ustaw prawdziwe `SGLANG_API_KEY`, które odpowiada
    konfiguracji serwera, albo skonfiguruj dostawcę jawnie pod
    `models.providers.sglang`.

    <Tip>
    Jeśli uruchamiasz SGLang bez uwierzytelniania, dowolna niepusta wartość
    `SGLANG_API_KEY` wystarczy, aby włączyć wykrywanie modeli.
    </Tip>

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Informacje o konfiguracji" href="/pl/gateway/configuration-reference" icon="gear">
    Pełny schemat konfiguracji, w tym wpisy dostawców.
  </Card>
</CardGroup>
