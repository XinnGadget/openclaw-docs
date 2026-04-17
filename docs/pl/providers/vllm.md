---
read_when:
    - Chcesz uruchomić OpenClaw z lokalnym serwerem vLLM
    - Chcesz używać endpointów `/v1` zgodnych z OpenAI z własnymi modelami
summary: Uruchamiaj OpenClaw z vLLM (lokalny serwer zgodny z OpenAI)
title: vLLM
x-i18n:
    generated_at: "2026-04-12T23:33:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: a43be9ae879158fcd69d50fb3a47616fd560e3c6fe4ecb3a109bdda6a63a6a80
    source_path: providers/vllm.md
    workflow: 15
---

# vLLM

vLLM może udostępniać modele open source (oraz niektóre niestandardowe) przez **API HTTP zgodne z OpenAI**. OpenClaw łączy się z vLLM przy użyciu API `openai-completions`.

OpenClaw może także **automatycznie wykrywać** dostępne modele z vLLM, gdy jawnie to włączysz przez `VLLM_API_KEY` (dowolna wartość działa, jeśli Twój serwer nie wymusza auth) i nie zdefiniujesz jawnego wpisu `models.providers.vllm`.

| Właściwość      | Wartość                                  |
| --------------- | ---------------------------------------- |
| ID dostawcy     | `vllm`                                   |
| API             | `openai-completions` (zgodne z OpenAI)   |
| Auth            | zmienna środowiskowa `VLLM_API_KEY`      |
| Domyślny bazowy URL | `http://127.0.0.1:8000/v1`           |

## Pierwsze kroki

<Steps>
  <Step title="Uruchom vLLM z serwerem zgodnym z OpenAI">
    Twój bazowy URL powinien udostępniać endpointy `/v1` (np. `/v1/models`, `/v1/chat/completions`). vLLM często działa pod adresem:

    ```
    http://127.0.0.1:8000/v1
    ```

  </Step>
  <Step title="Ustaw zmienną środowiskową klucza API">
    Dowolna wartość działa, jeśli Twój serwer nie wymusza auth:

    ```bash
    export VLLM_API_KEY="vllm-local"
    ```

  </Step>
  <Step title="Wybierz model">
    Zastąp jedną z wartości identyfikatorem modelu z vLLM:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vllm/your-model-id" },
        },
      },
    }
    ```

  </Step>
  <Step title="Sprawdź, czy model jest dostępny">
    ```bash
    openclaw models list --provider vllm
    ```
  </Step>
</Steps>

## Wykrywanie modeli (niejawny dostawca)

Gdy `VLLM_API_KEY` jest ustawione (albo istnieje profil auth) i **nie** zdefiniujesz `models.providers.vllm`, OpenClaw wykonuje zapytanie:

```
GET http://127.0.0.1:8000/v1/models
```

i przekształca zwrócone identyfikatory w wpisy modeli.

<Note>
Jeśli jawnie ustawisz `models.providers.vllm`, automatyczne wykrywanie zostanie pominięte i musisz ręcznie zdefiniować modele.
</Note>

## Jawna konfiguracja (modele ręczne)

Użyj jawnej konfiguracji, gdy:

- vLLM działa na innym hoście lub porcie
- Chcesz przypiąć wartości `contextWindow` lub `maxTokens`
- Twój serwer wymaga prawdziwego klucza API (albo chcesz kontrolować nagłówki)

```json5
{
  models: {
    providers: {
      vllm: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "${VLLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "Lokalny model vLLM",
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

## Uwagi zaawansowane

<AccordionGroup>
  <Accordion title="Zachowanie w stylu proxy">
    vLLM jest traktowany jako backend `/v1` zgodny z OpenAI w stylu proxy, a nie natywny
    endpoint OpenAI. Oznacza to, że:

    | Zachowanie | Stosowane? |
    |----------|----------|
    | Natywne kształtowanie żądań OpenAI | Nie |
    | `service_tier` | Nie jest wysyłane |
    | `store` w Responses | Nie jest wysyłane |
    | Wskazówki prompt-cache | Nie są wysyłane |
    | Kształtowanie payloadów zgodności reasoning OpenAI | Nie jest stosowane |
    | Ukryte nagłówki atrybucji OpenClaw | Nie są wstrzykiwane przy niestandardowych bazowych URL-ach |

  </Accordion>

  <Accordion title="Niestandardowy bazowy URL">
    Jeśli Twój serwer vLLM działa na niestandardowym hoście lub porcie, ustaw `baseUrl` w jawnej konfiguracji dostawcy:

    ```json5
    {
      models: {
        providers: {
          vllm: {
            baseUrl: "http://192.168.1.50:9000/v1",
            apiKey: "${VLLM_API_KEY}",
            api: "openai-completions",
            models: [
              {
                id: "my-custom-model",
                name: "Zdalny model vLLM",
                reasoning: false,
                input: ["text"],
                contextWindow: 64000,
                maxTokens: 4096,
              },
            ],
          },
        },
      },
    }
    ```

  </Accordion>
</AccordionGroup>

## Rozwiązywanie problemów

<AccordionGroup>
  <Accordion title="Nie można połączyć się z serwerem">
    Sprawdź, czy serwer vLLM działa i jest dostępny:

    ```bash
    curl http://127.0.0.1:8000/v1/models
    ```

    Jeśli widzisz błąd połączenia, sprawdź host, port oraz czy vLLM uruchomiono w trybie serwera zgodnego z OpenAI.

  </Accordion>

  <Accordion title="Błędy auth przy żądaniach">
    Jeśli żądania kończą się błędami auth, ustaw prawdziwe `VLLM_API_KEY`, które odpowiada konfiguracji serwera, albo skonfiguruj dostawcę jawnie pod `models.providers.vllm`.

    <Tip>
    Jeśli Twój serwer vLLM nie wymusza auth, dowolna niepusta wartość `VLLM_API_KEY` działa jako sygnał jawnego włączenia dla OpenClaw.
    </Tip>

  </Accordion>

  <Accordion title="Nie wykryto modeli">
    Automatyczne wykrywanie wymaga, aby `VLLM_API_KEY` było ustawione **oraz** żeby nie istniał jawny wpis konfiguracji `models.providers.vllm`. Jeśli dostawcę zdefiniowano ręcznie, OpenClaw pomija wykrywanie i używa tylko zadeklarowanych modeli.
  </Accordion>
</AccordionGroup>

<Warning>
Więcej pomocy: [Rozwiązywanie problemów](/pl/help/troubleshooting) i [FAQ](/pl/help/faq).
</Warning>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="OpenAI" href="/pl/providers/openai" icon="bolt">
    Natywny dostawca OpenAI i zachowanie tras zgodnych z OpenAI.
  </Card>
  <Card title="OAuth i auth" href="/pl/gateway/authentication" icon="key">
    Szczegóły auth i zasady ponownego użycia poświadczeń.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Typowe problemy i sposoby ich rozwiązania.
  </Card>
</CardGroup>
