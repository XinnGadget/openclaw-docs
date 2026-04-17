---
read_when:
    - Chcesz udostępniać modele z własnej maszyny GPU
    - Konfigurujesz LM Studio lub serwer proxy zgodny z OpenAI
    - Potrzebujesz najbezpieczniejszych wskazówek dotyczących modeli lokalnych
summary: Uruchamiaj OpenClaw na lokalnych modelach LLM (LM Studio, vLLM, LiteLLM, niestandardowe endpointy OpenAI)
title: Modele lokalne
x-i18n:
    generated_at: "2026-04-15T14:40:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7a506ff83e4c2870d3878339f646c906584454a156ecd618c360f592cf3b0011
    source_path: gateway/local-models.md
    workflow: 15
---

# Modele lokalne

Uruchamianie lokalnie jest możliwe, ale OpenClaw oczekuje dużego kontekstu + silnych zabezpieczeń przed prompt injection. Małe karty obcinają kontekst i osłabiają bezpieczeństwo. Celuj wysoko: **≥2 w pełni wyposażone Mac Studio lub równoważny zestaw GPU (~30 tys. USD+)**. Pojedynczy procesor graficzny **24 GB** sprawdza się tylko przy lżejszych promptach i wyższym opóźnieniu. Używaj **największego / pełnowymiarowego wariantu modelu, jaki możesz uruchomić**; agresywnie skwantyzowane lub „small” checkpointy zwiększają ryzyko prompt injection (zobacz [Bezpieczeństwo](/pl/gateway/security)).

Jeśli chcesz skonfigurować lokalne środowisko z najmniejszym tarciem, zacznij od [LM Studio](/pl/providers/lmstudio) lub [Ollama](/pl/providers/ollama) i `openclaw onboard`. Ta strona to praktyczny przewodnik po bardziej zaawansowanych lokalnych stosach oraz niestandardowych lokalnych serwerach zgodnych z OpenAI.

## Zalecane: LM Studio + duży lokalny model (API Responses)

Obecnie najlepszy lokalny stos. Załaduj duży model do LM Studio (na przykład pełnowymiarową wersję Qwen, DeepSeek lub Llama), włącz lokalny serwer (domyślnie `http://127.0.0.1:1234`) i używaj API Responses, aby oddzielić rozumowanie od końcowego tekstu.

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
- W LM Studio pobierz **największą dostępną wersję modelu** (unikaj wariantów „small” / mocno skwantyzowanych), uruchom serwer i potwierdź, że `http://127.0.0.1:1234/v1/models` go wyświetla.
- Zastąp `my-local-model` rzeczywistym identyfikatorem modelu widocznym w LM Studio.
- Utrzymuj model załadowany; zimne ładowanie zwiększa opóźnienie startu.
- Dostosuj `contextWindow`/`maxTokens`, jeśli Twoja wersja LM Studio różni się od tej opisanej tutaj.
- W przypadku WhatsApp trzymaj się API Responses, aby wysyłany był tylko końcowy tekst.

Nawet przy pracy lokalnej zachowaj konfigurację modeli hostowanych; użyj `models.mode: "merge"`, aby fallbacki nadal były dostępne.

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

Zamień kolejność modelu głównego i fallbacków; pozostaw ten sam blok providers oraz `models.mode: "merge"`, aby móc przełączyć się na Sonnet lub Opus, gdy lokalna maszyna będzie niedostępna.

### Hosting regionalny / routing danych

- Hostowane warianty MiniMax/Kimi/GLM są też dostępne w OpenRouter z endpointami przypisanymi do regionu (np. hostowanymi w USA). Wybierz tam wariant regionalny, aby utrzymać ruch w wybranej jurysdykcji, nadal używając `models.mode: "merge"` dla fallbacków Anthropic/OpenAI.
- Tylko lokalnie to nadal najmocniejsza ścieżka prywatności; hostowany routing regionalny to rozwiązanie pośrednie, gdy potrzebujesz funkcji dostawcy, ale chcesz zachować kontrolę nad przepływem danych.

## Inne lokalne serwery proxy zgodne z OpenAI

vLLM, LiteLLM, OAI-proxy lub niestandardowe Gateway działają, jeśli udostępniają endpoint `/v1` w stylu OpenAI. Zastąp powyższy blok provider swoim endpointem i identyfikatorem modelu:

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

Zachowaj `models.mode: "merge"`, aby modele hostowane nadal były dostępne jako fallbacki.

Uwaga dotycząca zachowania lokalnych/proxy backendów `/v1`:

- OpenClaw traktuje je jako routy proxy zgodne z OpenAI, a nie natywne endpointy OpenAI
- natywne dla OpenAI kształtowanie żądań nie ma tu zastosowania: brak
  `service_tier`, brak Responses `store`, brak kształtowania payloadu zgodności z rozumowaniem OpenAI
  oraz brak podpowiedzi prompt cache
- ukryte nagłówki atrybucji OpenClaw (`originator`, `version`, `User-Agent`)
  nie są wstrzykiwane do tych niestandardowych adresów URL proxy

Uwagi dotyczące zgodności z bardziej rygorystycznymi backendami zgodnymi z OpenAI:

- Niektóre serwery akceptują w Chat Completions wyłącznie string `messages[].content`, a nie
  ustrukturyzowane tablice części treści. Ustaw
  `models.providers.<provider>.models[].compat.requiresStringContent: true` dla
  takich endpointów.
- Niektóre mniejsze lub bardziej restrykcyjne lokalne backendy działają niestabilnie z pełnym
  kształtem promptu środowiska agentowego OpenClaw, zwłaszcza gdy dołączone są schematy narzędzi. Jeśli
  backend działa dla małych bezpośrednich wywołań `/v1/chat/completions`, ale nie działa przy zwykłych
  turach agenta OpenClaw, najpierw spróbuj ustawić
  `agents.defaults.experimental.localModelLean: true`, aby usunąć cięższe
  domyślne narzędzia, takie jak `browser`, `cron` i `message`; to flaga eksperymentalna,
  a nie stabilne ustawienie trybu domyślnego. Zobacz
  [Funkcje eksperymentalne](/pl/concepts/experimental-features). Jeśli to nadal nie pomoże, spróbuj
  `models.providers.<provider>.models[].compat.supportsTools: false`.
- Jeśli backend nadal zawodzi tylko przy większych uruchomieniach OpenClaw, pozostały problem
  zwykle leży po stronie wydajności modelu/serwera lub błędu backendu, a nie warstwy
  transportowej OpenClaw.

## Rozwiązywanie problemów

- Gateway może połączyć się z proxy? `curl http://127.0.0.1:1234/v1/models`.
- Model LM Studio został wyładowany? Załaduj go ponownie; zimny start to częsta przyczyna „zawieszania się”.
- OpenClaw ostrzega, gdy wykryte okno kontekstu jest mniejsze niż **32k**, i blokuje działanie poniżej **16k**. Jeśli trafisz na ten preflight, zwiększ limit kontekstu serwera/modelu albo wybierz większy model.
- Błędy kontekstu? Zmniejsz `contextWindow` albo zwiększ limit serwera.
- Serwer zgodny z OpenAI zwraca `messages[].content ... expected a string`?
  Dodaj `compat.requiresStringContent: true` do wpisu tego modelu.
- Małe bezpośrednie wywołania `/v1/chat/completions` działają, ale `openclaw infer model run`
  nie działa na Gemma lub innym modelu lokalnym? Najpierw wyłącz schematy narzędzi przez
  `compat.supportsTools: false`, a następnie przetestuj ponownie. Jeśli serwer nadal się zawiesza tylko
  przy większych promptach OpenClaw, traktuj to jako ograniczenie modelu/serwera po stronie upstream.
- Bezpieczeństwo: modele lokalne pomijają filtry po stronie dostawcy; ogranicz zakres agentów i pozostaw włączony Compaction, aby zmniejszyć promień rażenia prompt injection.
