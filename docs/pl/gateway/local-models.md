---
read_when:
    - Chcesz udostępniać modele z własnej maszyny z GPU
    - Konfigurujesz LM Studio lub proxy zgodne z OpenAI
    - Potrzebujesz najbezpieczniejszych wskazówek dotyczących modeli lokalnych
summary: Uruchom OpenClaw na lokalnych LLM-ach (LM Studio, vLLM, LiteLLM, niestandardowe endpointy OpenAI)
title: Modele lokalne
x-i18n:
    generated_at: "2026-04-13T08:50:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3ecb61b3e6e34d3666f9b688cd694d92c5fb211cf8c420fa876f7ccf5789154a
    source_path: gateway/local-models.md
    workflow: 15
---

# Modele lokalne

Środowisko lokalne jest wykonalne, ale OpenClaw oczekuje dużego kontekstu + silnej ochrony przed prompt injection. Małe karty obcinają kontekst i osłabiają bezpieczeństwo. Celuj wysoko: **≥2 w pełni wyposażone Mac Studio lub równoważny zestaw GPU (~30 tys. USD+)**. Pojedynczy procesor graficzny **24 GB** działa tylko przy lżejszych promptach i z większym opóźnieniem. Używaj **największego / pełnowymiarowego wariantu modelu, jaki możesz uruchomić**; agresywnie kwantyzowane lub „małe” checkpointy zwiększają ryzyko prompt injection (zobacz [Bezpieczeństwo](/pl/gateway/security)).

Jeśli chcesz uzyskać lokalną konfigurację z najmniejszym tarciem, zacznij od [LM Studio](/pl/providers/lmstudio) lub [Ollama](/pl/providers/ollama) i `openclaw onboard`. Ta strona to praktyczny przewodnik dla bardziej zaawansowanych lokalnych stosów oraz niestandardowych lokalnych serwerów zgodnych z OpenAI.

## Zalecane: LM Studio + duży model lokalny (Responses API)

Obecnie najlepszy lokalny stos. Załaduj duży model w LM Studio (na przykład pełnowymiarową kompilację Qwen, DeepSeek lub Llama), włącz lokalny serwer (domyślnie `http://127.0.0.1:1234`), a następnie użyj Responses API, aby oddzielić rozumowanie od końcowego tekstu.

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Local Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**Lista kontrolna konfiguracji**

- Zainstaluj LM Studio: [https://lmstudio.ai](https://lmstudio.ai)
- W LM Studio pobierz **największą dostępną kompilację modelu** (unikaj wariantów „small” / mocno kwantyzowanych), uruchom serwer i potwierdź, że `http://127.0.0.1:1234/v1/models` go wyświetla.
- Zastąp `my-local-model` rzeczywistym identyfikatorem modelu widocznym w LM Studio.
- Utrzymuj model załadowany; zimne ładowanie zwiększa opóźnienie uruchamiania.
- Dostosuj `contextWindow`/`maxTokens`, jeśli Twoja kompilacja LM Studio różni się od tej przykładowej.
- W przypadku WhatsApp trzymaj się Responses API, aby wysyłany był tylko końcowy tekst.

Utrzymuj skonfigurowane także modele hostowane, nawet jeśli działasz lokalnie; używaj `models.mode: "merge"`, aby fallbacki pozostawały dostępne.

### Konfiguracja hybrydowa: hostowany model główny, lokalny fallback

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### Najpierw lokalnie, z hostowaną siatką bezpieczeństwa

Zamień kolejność modelu głównego i fallbacku; pozostaw ten sam blok providers oraz `models.mode: "merge"`, aby w razie awarii lokalnej maszyny można było przełączyć się na Sonnet lub Opus.

### Hosting regionalny / routing danych

- Hostowane warianty MiniMax/Kimi/GLM są także dostępne w OpenRouter z endpointami przypisanymi do regionu (np. hostowane w USA). Wybierz tam wariant regionalny, aby utrzymać ruch w wybranej jurysdykcji, nadal używając `models.mode: "merge"` dla fallbacków Anthropic/OpenAI.
- Tryb wyłącznie lokalny pozostaje najmocniejszą ścieżką prywatności; hostowany routing regionalny to rozwiązanie pośrednie, gdy potrzebujesz funkcji dostawcy, ale chcesz zachować kontrolę nad przepływem danych.

## Inne lokalne proxy zgodne z OpenAI

vLLM, LiteLLM, OAI-proxy lub niestandardowe Gateway działają, jeśli udostępniają endpoint `/v1` w stylu OpenAI. Zastąp powyższy blok provider własnym endpointem i identyfikatorem modelu:

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Utrzymuj `models.mode: "merge"`, aby hostowane modele nadal były dostępne jako fallbacki.

Uwaga dotycząca działania lokalnych / proxy backendów `/v1`:

- OpenClaw traktuje je jako trasy proxy zgodne z OpenAI, a nie natywne
  endpointy OpenAI
- natywne formatowanie żądań przeznaczone wyłącznie dla OpenAI nie ma tu
  zastosowania: brak `service_tier`, brak `store` dla Responses, brak
  formatowania ładunku zgodności rozumowania OpenAI i brak wskazówek
  dotyczących cache promptów
- ukryte nagłówki atrybucji OpenClaw (`originator`, `version`, `User-Agent`)
  nie są wstrzykiwane do tych niestandardowych URL-i proxy

Uwagi o zgodności dla bardziej restrykcyjnych backendów zgodnych z OpenAI:

- Niektóre serwery akceptują w Chat Completions tylko ciąg znaków w `messages[].content`, a nie
  ustrukturyzowane tablice części treści. Ustaw
  `models.providers.<provider>.models[].compat.requiresStringContent: true` dla
  takich endpointów.
- Niektóre mniejsze lub bardziej restrykcyjne lokalne backendy są niestabilne przy pełnym
  kształcie promptu środowiska uruchomieniowego agenta OpenClaw, zwłaszcza gdy dołączone są
  schematy narzędzi. Jeśli backend działa dla małych bezpośrednich wywołań `/v1/chat/completions`,
  ale zawodzi przy normalnych turach agenta OpenClaw, najpierw spróbuj
  `models.providers.<provider>.models[].compat.supportsTools: false`.
- Jeśli backend nadal zawodzi tylko przy większych uruchomieniach OpenClaw, pozostały problem
  zwykle leży po stronie pojemności modelu/serwera albo błędu backendu, a nie warstwy
  transportowej OpenClaw.

## Rozwiązywanie problemów

- Gateway może połączyć się z proxy? `curl http://127.0.0.1:1234/v1/models`.
- Model LM Studio został wyładowany? Załaduj go ponownie; zimny start to częsta przyczyna „zawieszania się”.
- Błędy kontekstu? Zmniejsz `contextWindow` lub zwiększ limit serwera.
- Serwer zgodny z OpenAI zwraca `messages[].content ... expected a string`?
  Dodaj `compat.requiresStringContent: true` do tego wpisu modelu.
- Małe bezpośrednie wywołania `/v1/chat/completions` działają, ale `openclaw infer model run`
  zawodzi na Gemma lub innym modelu lokalnym? Najpierw wyłącz schematy narzędzi przez
  `compat.supportsTools: false`, a następnie przetestuj ponownie. Jeśli serwer nadal ulega awarii tylko
  przy większych promptach OpenClaw, traktuj to jako ograniczenie modelu/serwera po stronie upstream.
- Bezpieczeństwo: modele lokalne pomijają filtry po stronie dostawcy; utrzymuj wąski zakres działania agentów i włączoną Compaction, aby ograniczyć promień rażenia prompt injection.
