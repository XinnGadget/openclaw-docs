---
read_when:
    - Chcesz uruchamiać OpenClaw z lokalnym serwerem inferrs
    - Udostępniasz Gemma lub inny model przez inferrs
    - Potrzebujesz dokładnych flag zgodności OpenClaw dla inferrs
summary: Uruchamiaj OpenClaw przez inferrs (lokalny serwer zgodny z OpenAI)
title: inferrs
x-i18n:
    generated_at: "2026-04-12T23:31:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: 847dcc131fe51dfe163dcd60075dbfaa664662ea2a5c3986ccb08ddd37e8c31f
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) może udostępniać modele lokalne za
zgodnym z OpenAI API `/v1`. OpenClaw współpracuje z `inferrs` przez ogólną
ścieżkę `openai-completions`.

`inferrs` obecnie najlepiej traktować jako niestandardowy samohostowany backend
zgodny z OpenAI, a nie jako dedykowany Plugin dostawcy OpenClaw.

## Pierwsze kroki

<Steps>
  <Step title="Uruchom inferrs z modelem">
    ```bash
    inferrs serve google/gemma-4-E2B-it \
      --host 127.0.0.1 \
      --port 8080 \
      --device metal
    ```
  </Step>
  <Step title="Sprawdź, czy serwer jest osiągalny">
    ```bash
    curl http://127.0.0.1:8080/health
    curl http://127.0.0.1:8080/v1/models
    ```
  </Step>
  <Step title="Dodaj wpis dostawcy OpenClaw">
    Dodaj jawny wpis dostawcy i skieruj na niego swój model domyślny. Zobacz pełny przykład konfiguracji poniżej.
  </Step>
</Steps>

## Pełny przykład konfiguracji

Ten przykład używa Gemma 4 na lokalnym serwerze `inferrs`.

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/google/gemma-4-E2B-it" },
      models: {
        "inferrs/google/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "google/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## Zaawansowane

<AccordionGroup>
  <Accordion title="Dlaczego requiresStringContent ma znaczenie">
    Niektóre trasy `inferrs` Chat Completions akceptują tylko ciąg znaków w
    `messages[].content`, a nie ustrukturyzowane tablice części treści.

    <Warning>
    Jeśli uruchomienia OpenClaw kończą się błędem takim jak:

    ```text
    messages[1].content: invalid type: sequence, expected a string
    ```

    ustaw `compat.requiresStringContent: true` we wpisie modelu.
    </Warning>

    ```json5
    compat: {
      requiresStringContent: true
    }
    ```

    OpenClaw spłaszczy części treści zawierające wyłącznie tekst do zwykłych ciągów znaków przed wysłaniem
    żądania.

  </Accordion>

  <Accordion title="Zastrzeżenie dotyczące Gemma i schematu narzędzi">
    Niektóre obecne kombinacje `inferrs` + Gemma akceptują małe bezpośrednie
    żądania `/v1/chat/completions`, ale nadal zawodzą przy pełnych turach środowiska uruchomieniowego agenta OpenClaw.

    Jeśli tak się stanie, najpierw spróbuj tego:

    ```json5
    compat: {
      requiresStringContent: true,
      supportsTools: false
    }
    ```

    To wyłącza powierzchnię schematu narzędzi OpenClaw dla modelu i może zmniejszyć obciążenie promptu
    w bardziej rygorystycznych lokalnych backendach.

    Jeśli małe bezpośrednie żądania nadal działają, ale zwykłe tury agenta OpenClaw dalej
    powodują awarie w `inferrs`, pozostały problem zwykle leży po stronie zachowania modelu/serwera
    wyżej w stosie, a nie warstwy transportowej OpenClaw.

  </Accordion>

  <Accordion title="Ręczny test smoke">
    Po skonfigurowaniu przetestuj obie warstwy:

    ```bash
    curl http://127.0.0.1:8080/v1/chat/completions \
      -H 'content-type: application/json' \
      -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'
    ```

    ```bash
    openclaw infer model run \
      --model inferrs/google/gemma-4-E2B-it \
      --prompt "What is 2 + 2? Reply with one short sentence." \
      --json
    ```

    Jeśli pierwsze polecenie działa, ale drugie kończy się niepowodzeniem, sprawdź sekcję rozwiązywania problemów poniżej.

  </Accordion>

  <Accordion title="Zachowanie w stylu proxy">
    `inferrs` jest traktowany jako backend `/v1` zgodny z OpenAI w stylu proxy, a nie
    natywny endpoint OpenAI.

    - Natywne kształtowanie żądań tylko dla OpenAI nie ma tu zastosowania
    - Brak `service_tier`, brak `store` w Responses, brak wskazówek prompt-cache i brak
      kształtowania ładunku zgodności rozumowania OpenAI
    - Ukryte nagłówki atrybucji OpenClaw (`originator`, `version`, `User-Agent`)
      nie są wstrzykiwane do niestandardowych `baseUrl` inferrs

  </Accordion>
</AccordionGroup>

## Rozwiązywanie problemów

<AccordionGroup>
  <Accordion title="curl /v1/models kończy się niepowodzeniem">
    `inferrs` nie działa, nie jest osiągalny lub nie jest powiązany z oczekiwanym
    hostem/portem. Upewnij się, że serwer został uruchomiony i nasłuchuje na adresie, który
    skonfigurowałeś.
  </Accordion>

  <Accordion title="messages[].content oczekuje ciągu znaków">
    Ustaw `compat.requiresStringContent: true` we wpisie modelu. Zobacz sekcję
    `requiresStringContent` powyżej, aby poznać szczegóły.
  </Accordion>

  <Accordion title="Bezpośrednie wywołania /v1/chat/completions przechodzą, ale openclaw infer model run kończy się niepowodzeniem">
    Spróbuj ustawić `compat.supportsTools: false`, aby wyłączyć powierzchnię schematu narzędzi.
    Zobacz zastrzeżenie dotyczące schematu narzędzi Gemma powyżej.
  </Accordion>

  <Accordion title="inferrs nadal ulega awarii przy większych turach agenta">
    Jeśli OpenClaw nie otrzymuje już błędów schematu, ale `inferrs` nadal ulega awarii przy większych
    turach agenta, potraktuj to jako ograniczenie `inferrs` lub modelu wyżej w stosie. Zmniejsz
    obciążenie promptu albo przełącz się na inny lokalny backend lub model.
  </Accordion>
</AccordionGroup>

<Tip>
Aby uzyskać ogólną pomoc, zobacz [Rozwiązywanie problemów](/pl/help/troubleshooting) i [FAQ](/pl/help/faq).
</Tip>

## Zobacz także

<CardGroup cols={2}>
  <Card title="Modele lokalne" href="/pl/gateway/local-models" icon="server">
    Uruchamianie OpenClaw z lokalnymi serwerami modeli.
  </Card>
  <Card title="Rozwiązywanie problemów z Gateway" href="/pl/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail" icon="wrench">
    Debugowanie lokalnych backendów zgodnych z OpenAI, które przechodzą sondy bezpośrednie, ale kończą niepowodzeniem przy uruchomieniach agentów.
  </Card>
  <Card title="Dostawcy modeli" href="/pl/concepts/model-providers" icon="layers">
    Omówienie wszystkich dostawców, odwołań do modeli i zachowania failover.
  </Card>
</CardGroup>
