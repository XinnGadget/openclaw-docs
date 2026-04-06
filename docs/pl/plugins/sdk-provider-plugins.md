---
read_when:
    - Tworzysz nowy plugin dostawcy modeli
    - Chcesz dodać proxy zgodne z OpenAI lub niestandardowy LLM do OpenClaw
    - Musisz zrozumieć uwierzytelnianie dostawcy, katalogi i hooki runtime
sidebarTitle: Provider Plugins
summary: Przewodnik krok po kroku po tworzeniu pluginu dostawcy modeli dla OpenClaw
title: Tworzenie pluginów dostawców
x-i18n:
    generated_at: "2026-04-06T03:11:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 69500f46aa2cfdfe16e85b0ed9ee3c0032074be46f2d9c9d2940d18ae1095f47
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Tworzenie pluginów dostawców

Ten przewodnik pokazuje, jak zbudować plugin dostawcy, który dodaje dostawcę modeli
(LLM) do OpenClaw. Na końcu będziesz mieć dostawcę z katalogiem modeli,
uwierzytelnianiem kluczem API i dynamicznym rozpoznawaniem modeli.

<Info>
  Jeśli nie zbudowano jeszcze żadnego pluginu OpenClaw, najpierw przeczytaj
  [Pierwsze kroki](/pl/plugins/building-plugins), aby poznać podstawową strukturę
  pakietu i konfigurację manifestu.
</Info>

## Przewodnik krok po kroku

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Pakiet i manifest">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-ai",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "providers": ["acme-ai"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-ai",
      "name": "Acme AI",
      "description": "Acme AI model provider",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthChoices": [
        {
          "provider": "acme-ai",
          "method": "api-key",
          "choiceId": "acme-ai-api-key",
          "choiceLabel": "Acme AI API key",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "Acme AI API key"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Manifest deklaruje `providerAuthEnvVars`, aby OpenClaw mógł wykrywać
    poświadczenia bez ładowania runtime Twojego pluginu. `modelSupport` jest opcjonalne
    i pozwala OpenClaw automatycznie ładować plugin dostawcy na podstawie skróconych identyfikatorów modeli,
    takich jak `acme-large`, zanim hooki runtime będą dostępne. Jeśli publikujesz
    dostawcę w ClawHub, pola `openclaw.compat` i `openclaw.build`
    są wymagane w `package.json`.

  </Step>

  <Step title="Zarejestruj dostawcę">
    Minimalny dostawca potrzebuje `id`, `label`, `auth` i `catalog`:

    ```typescript index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { createProviderApiKeyAuthMethod } from "openclaw/plugin-sdk/provider-auth";

    export default definePluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      register(api) {
        api.registerProvider({
          id: "acme-ai",
          label: "Acme AI",
          docsPath: "/providers/acme-ai",
          envVars: ["ACME_AI_API_KEY"],

          auth: [
            createProviderApiKeyAuthMethod({
              providerId: "acme-ai",
              methodId: "api-key",
              label: "Acme AI API key",
              hint: "API key from your Acme AI dashboard",
              optionKey: "acmeAiApiKey",
              flagName: "--acme-ai-api-key",
              envVar: "ACME_AI_API_KEY",
              promptMessage: "Enter your Acme AI API key",
              defaultModel: "acme-ai/acme-large",
            }),
          ],

          catalog: {
            order: "simple",
            run: async (ctx) => {
              const apiKey =
                ctx.resolveProviderApiKey("acme-ai").apiKey;
              if (!apiKey) return null;
              return {
                provider: {
                  baseUrl: "https://api.acme-ai.com/v1",
                  apiKey,
                  api: "openai-completions",
                  models: [
                    {
                      id: "acme-large",
                      name: "Acme Large",
                      reasoning: true,
                      input: ["text", "image"],
                      cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 },
                      contextWindow: 200000,
                      maxTokens: 32768,
                    },
                    {
                      id: "acme-small",
                      name: "Acme Small",
                      reasoning: false,
                      input: ["text"],
                      cost: { input: 1, output: 5, cacheRead: 0.1, cacheWrite: 1.25 },
                      contextWindow: 128000,
                      maxTokens: 8192,
                    },
                  ],
                },
              };
            },
          },
        });
      },
    });
    ```

    To jest działający dostawca. Użytkownicy mogą teraz
    `openclaw onboard --acme-ai-api-key <key>` i wybrać
    `acme-ai/acme-large` jako swój model.

    Dla dołączonych dostawców, którzy rejestrują tylko jednego dostawcę tekstowego z
    uwierzytelnianiem kluczem API oraz pojedynczym runtime opartym na katalogu, preferuj węższy
    helper `defineSingleProviderPluginEntry(...)`:

    ```typescript
    import { defineSingleProviderPluginEntry } from "openclaw/plugin-sdk/provider-entry";

    export default defineSingleProviderPluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      provider: {
        label: "Acme AI",
        docsPath: "/providers/acme-ai",
        auth: [
          {
            methodId: "api-key",
            label: "Acme AI API key",
            hint: "API key from your Acme AI dashboard",
            optionKey: "acmeAiApiKey",
            flagName: "--acme-ai-api-key",
            envVar: "ACME_AI_API_KEY",
            promptMessage: "Enter your Acme AI API key",
            defaultModel: "acme-ai/acme-large",
          },
        ],
        catalog: {
          buildProvider: () => ({
            api: "openai-completions",
            baseUrl: "https://api.acme-ai.com/v1",
            models: [{ id: "acme-large", name: "Acme Large" }],
          }),
        },
      },
    });
    ```

    Jeśli Twój przepływ uwierzytelniania musi również łatać `models.providers.*`, aliasy oraz
    domyślny model agenta podczas onboardingu, użyj gotowych helperów z
    `openclaw/plugin-sdk/provider-onboard`. Najwęższe helpery to
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` oraz
    `createModelCatalogPresetAppliers(...)`.

    Gdy natywny endpoint dostawcy obsługuje strumieniowane bloki użycia na
    zwykłym transporcie `openai-completions`, preferuj współdzielone helpery katalogów z
    `openclaw/plugin-sdk/provider-catalog-shared` zamiast kodowania na sztywno
    sprawdzeń identyfikatorów dostawców. `supportsNativeStreamingUsageCompat(...)` oraz
    `applyProviderNativeStreamingUsageCompat(...)` wykrywają obsługę na podstawie mapy capabilities endpointu,
    więc natywne endpointy w stylu Moonshot/DashScope nadal
    włączają tę funkcję nawet wtedy, gdy plugin używa niestandardowego identyfikatora dostawcy.

  </Step>

  <Step title="Dodaj dynamiczne rozpoznawanie modeli">
    Jeśli Twój dostawca akceptuje dowolne identyfikatory modeli (jak proxy lub router),
    dodaj `resolveDynamicModel`:

    ```typescript
    api.registerProvider({
      // ... id, label, auth, catalog from above

      resolveDynamicModel: (ctx) => ({
        id: ctx.modelId,
        name: ctx.modelId,
        provider: "acme-ai",
        api: "openai-completions",
        baseUrl: "https://api.acme-ai.com/v1",
        reasoning: false,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 128000,
        maxTokens: 8192,
      }),
    });
    ```

    Jeśli rozpoznanie wymaga wywołania sieciowego, użyj `prepareDynamicModel` do
    asynchronicznego przygotowania — `resolveDynamicModel` zostanie uruchomione ponownie po jego zakończeniu.

  </Step>

  <Step title="Dodaj hooki runtime (w razie potrzeby)">
    Większość dostawców potrzebuje tylko `catalog` + `resolveDynamicModel`. Dodawaj hooki
    stopniowo, zgodnie z potrzebami Twojego dostawcy.

    Współdzielone buildery helperów obejmują teraz najczęstsze rodziny zgodności replay/narzędzi,
    więc pluginy zwykle nie muszą ręcznie podłączać każdego hooka osobno:

    ```typescript
    import { buildProviderReplayFamilyHooks } from "openclaw/plugin-sdk/provider-model-shared";
    import { buildProviderStreamFamilyHooks } from "openclaw/plugin-sdk/provider-stream";
    import { buildProviderToolCompatFamilyHooks } from "openclaw/plugin-sdk/provider-tools";

    const GOOGLE_FAMILY_HOOKS = {
      ...buildProviderReplayFamilyHooks({ family: "google-gemini" }),
      ...buildProviderStreamFamilyHooks("google-thinking"),
      ...buildProviderToolCompatFamilyHooks("gemini"),
    };

    api.registerProvider({
      id: "acme-gemini-compatible",
      // ...
      ...GOOGLE_FAMILY_HOOKS,
    });
    ```

    Dostępne dziś rodziny replay:

    | Family | Co jest podłączane |
    | --- | --- |
    | `openai-compatible` | Współdzielona polityka replay w stylu OpenAI dla transportów zgodnych z OpenAI, w tym sanityzacja identyfikatorów wywołań narzędzi, poprawki kolejności assistant-first oraz ogólna walidacja tur Gemini tam, gdzie wymaga tego transport |
    | `anthropic-by-model` | Polityka replay świadoma Claude wybierana przez `modelId`, dzięki czemu transporty Anthropic-message otrzymują czyszczenie bloków thinking specyficzne dla Claude tylko wtedy, gdy rozpoznany model jest rzeczywiście identyfikatorem Claude |
    | `google-gemini` | Natywna polityka replay Gemini oraz sanityzacja replay bootstrap i oznaczony tryb wyjścia reasoning |
    | `passthrough-gemini` | Sanityzacja sygnatur thought Gemini dla modeli Gemini uruchamianych przez transporty proxy zgodne z OpenAI; nie włącza natywnej walidacji replay Gemini ani przepisywania bootstrap |
    | `hybrid-anthropic-openai` | Polityka hybrydowa dla dostawców, którzy mieszają powierzchnie modeli Anthropic-message i zgodnych z OpenAI w jednym pluginie; opcjonalne usuwanie bloków thinking wyłącznie dla Claude pozostaje ograniczone do strony Anthropic |

    Rzeczywiste dołączone przykłady:

    - `google`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode` i `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` i `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` i `zai`: `openai-compatible`

    Dostępne dziś rodziny strumieni:

    | Family | Co jest podłączane |
    | --- | --- |
    | `google-thinking` | Normalizacja payloadu thinking Gemini na współdzielonej ścieżce strumienia |
    | `kilocode-thinking` | Opakowanie reasoning Kilo na współdzielonej ścieżce strumienia proxy, przy czym `kilo/auto` i identyfikatory proxy bez obsługi reasoning pomijają wstrzykiwany thinking |
    | `moonshot-thinking` | Mapowanie payloadu binarnego natywnego thinking Moonshot z config + poziomu `/think` |
    | `minimax-fast-mode` | Przepisywanie modelu fast-mode MiniMax na współdzielonej ścieżce strumienia |
    | `openai-responses-defaults` | Współdzielone natywne opakowania OpenAI/Codex Responses: nagłówki atrybucji, `/fast`/`serviceTier`, szczegółowość tekstu, natywne wyszukiwanie w sieci Codex, formatowanie payloadu zgodności reasoning oraz zarządzanie kontekstem Responses |
    | `openrouter-thinking` | Opakowanie reasoning OpenRouter dla tras proxy, z centralnie obsługiwanym pomijaniem modeli nieobsługiwanych/`auto` |
    | `tool-stream-default-on` | Opakowanie `tool_stream` domyślnie włączone dla dostawców takich jak Z.AI, którzy chcą strumieniowania narzędzi, o ile nie zostanie ono jawnie wyłączone |

    Rzeczywiste dołączone przykłady:

    - `google`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` i `minimax-portal`: `minimax-fast-mode`
    - `openai` i `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` eksportuje również enum rodziny replay
    oraz współdzielone helpery, z których te rodziny są budowane. Typowe publiczne eksporty
    obejmują:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - współdzielone buildery replay, takie jak `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)` oraz
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - helpery replay Gemini, takie jak `sanitizeGoogleGeminiReplayHistory(...)`
      i `resolveTaggedReasoningOutputMode()`
    - helpery endpointów/modeli, takie jak `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)` oraz
      `normalizeNativeXaiModelId(...)`

    `openclaw/plugin-sdk/provider-stream` udostępnia zarówno builder rodziny, jak i
    publiczne helpery opakowań, które te rodziny ponownie wykorzystują. Typowe publiczne eksporty
    obejmują:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - współdzielone opakowania OpenAI/Codex, takie jak
      `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)` oraz
      `createCodexNativeWebSearchWrapper(...)`
    - współdzielone opakowania proxy/dostawców, takie jak `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` oraz `createMinimaxFastModeWrapper(...)`

    Niektóre helpery strumieni celowo pozostają lokalne dla dostawcy. Aktualny dołączony
    przykład: `@openclaw/anthropic-provider` eksportuje
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` oraz
    niskopoziomowe buildery opakowań Anthropic ze swojej publicznej powierzchni `api.ts` /
    `contract-api.ts`. Te helpery pozostają specyficzne dla Anthropic, ponieważ
    kodują również obsługę beta Claude OAuth i bramkowanie `context1m`.

    Inni dołączeni dostawcy również utrzymują lokalne opakowania specyficzne dla transportu, gdy
    zachowanie nie daje się czysto współdzielić między rodzinami. Aktualny przykład: dołączony
    plugin xAI utrzymuje natywne formatowanie xAI Responses we własnym
    `wrapStreamFn`, w tym przepisywanie aliasów `/fast`, domyślne `tool_stream`,
    czyszczenie nieobsługiwanych ścisłych narzędzi oraz usuwanie payloadu reasoning
    specyficznego dla xAI.

    `openclaw/plugin-sdk/provider-tools` obecnie udostępnia jedną współdzieloną
    rodzinę schematów narzędzi oraz współdzielone helpery schematów/zgodności:

    - `ProviderToolCompatFamily` dokumentuje bieżący zestaw współdzielonych rodzin.
    - `buildProviderToolCompatFamilyHooks("gemini")` podłącza czyszczenie schematów
      Gemini + diagnostykę dla dostawców, którzy potrzebują bezpiecznych dla Gemini schematów narzędzi.
    - `normalizeGeminiToolSchemas(...)` i `inspectGeminiToolSchemas(...)`
      to bazowe publiczne helpery schematów Gemini.
    - `resolveXaiModelCompatPatch()` zwraca dołączoną łatkę zgodności xAI:
      `toolSchemaProfile: "xai"`, nieobsługiwane słowa kluczowe schematów, natywne
      wsparcie `web_search` oraz dekodowanie argumentów wywołań narzędzi z encji HTML.
    - `applyXaiModelCompat(model)` stosuje tę samą łatkę zgodności xAI do
      rozpoznanego modelu, zanim trafi on do runnera.

    Rzeczywisty dołączony przykład: plugin xAI używa `normalizeResolvedModel` oraz
    `contributeResolvedModelCompat`, aby te metadane zgodności pozostawały zarządzane przez
    dostawcę zamiast kodować reguły xAI na sztywno w rdzeniu.

    Ten sam wzorzec katalogu głównego pakietu wspiera także innych dołączonych dostawców:

    - `@openclaw/openai-provider`: `api.ts` eksportuje buildery dostawcy,
      helpery modeli domyślnych i buildery dostawców realtime
    - `@openclaw/openrouter-provider`: `api.ts` eksportuje builder
      dostawcy oraz helpery onboardingu/config

    <Tabs>
      <Tab title="Wymiana tokenów">
        Dla dostawców, którzy potrzebują wymiany tokena przed każdym wywołaniem inferencji:

        ```typescript
        prepareRuntimeAuth: async (ctx) => {
          const exchanged = await exchangeToken(ctx.apiKey);
          return {
            apiKey: exchanged.token,
            baseUrl: exchanged.baseUrl,
            expiresAt: exchanged.expiresAt,
          };
        },
        ```
      </Tab>
      <Tab title="Niestandardowe nagłówki">
        Dla dostawców, którzy potrzebują niestandardowych nagłówków żądań lub modyfikacji ciała:

        ```typescript
        // wrapStreamFn returns a StreamFn derived from ctx.streamFn
        wrapStreamFn: (ctx) => {
          if (!ctx.streamFn) return undefined;
          const inner = ctx.streamFn;
          return async (params) => {
            params.headers = {
              ...params.headers,
              "X-Acme-Version": "2",
            };
            return inner(params);
          };
        },
        ```
      </Tab>
      <Tab title="Tożsamość natywnego transportu">
        Dla dostawców, którzy potrzebują natywnych nagłówków lub metadanych żądania/sesji na
        ogólnych transportach HTTP lub WebSocket:

        ```typescript
        resolveTransportTurnState: (ctx) => ({
          headers: {
            "x-request-id": ctx.turnId,
          },
          metadata: {
            session_id: ctx.sessionId ?? "",
            turn_id: ctx.turnId,
          },
        }),
        resolveWebSocketSessionPolicy: (ctx) => ({
          headers: {
            "x-session-id": ctx.sessionId ?? "",
          },
          degradeCooldownMs: 60_000,
        }),
        ```
      </Tab>
      <Tab title="Użycie i rozliczenia">
        Dla dostawców, którzy udostępniają dane użycia/rozliczeń:

        ```typescript
        resolveUsageAuth: async (ctx) => {
          const auth = await ctx.resolveOAuthToken();
          return auth ? { token: auth.token } : null;
        },
        fetchUsageSnapshot: async (ctx) => {
          return await fetchAcmeUsage(ctx.token, ctx.timeoutMs);
        },
        ```
      </Tab>
    </Tabs>

    <Accordion title="Wszystkie dostępne hooki dostawców">
      OpenClaw wywołuje hooki w tej kolejności. Większość dostawców używa tylko 2–3:

      | # | Hook | Kiedy używać |
      | --- | --- | --- |
      | 1 | `catalog` | Katalog modeli lub domyślne wartości base URL |
      | 2 | `applyConfigDefaults` | Globalne domyślne wartości zarządzane przez dostawcę podczas materializacji config |
      | 3 | `normalizeModelId` | Czyszczenie aliasów identyfikatorów modeli legacy/podglądowych przed wyszukaniem |
      | 4 | `normalizeTransport` | Czyszczenie rodziny dostawcy `api` / `baseUrl` przed ogólnym składaniem modelu |
      | 5 | `normalizeConfig` | Normalizacja config `models.providers.<id>` |
      | 6 | `applyNativeStreamingUsageCompat` | Przepisania zgodności natywnego strumieniowania użycia dla dostawców konfiguracyjnych |
      | 7 | `resolveConfigApiKey` | Rozpoznawanie uwierzytelniania env-marker zarządzane przez dostawcę |
      | 8 | `resolveSyntheticAuth` | Syntetyczne uwierzytelnianie lokalne/self-hosted lub oparte na config |
      | 9 | `shouldDeferSyntheticProfileAuth` | Obniżanie priorytetu syntetycznych placeholderów zapisanych profili względem uwierzytelniania env/config |
      | 10 | `resolveDynamicModel` | Akceptowanie dowolnych identyfikatorów modeli upstream |
      | 11 | `prepareDynamicModel` | Asynchroniczne pobranie metadanych przed rozpoznaniem |
      | 12 | `normalizeResolvedModel` | Przepisania transportu przed runnerem |

    Uwagi dotyczące fallbacku runtime:

    - `normalizeConfig` najpierw sprawdza dopasowanego dostawcę, a następnie inne
      pluginy dostawców obsługujące hooki, aż któryś faktycznie zmieni config.
      Jeśli żaden hook dostawcy nie przepisze obsługiwanego wpisu config rodziny Google,
      nadal zostanie zastosowany dołączony normalizator config Google.
    - `resolveConfigApiKey` używa hooka dostawcy, gdy jest udostępniony. Dołączona
      ścieżka `amazon-bedrock` ma tu także wbudowany resolver env-markerów AWS,
      mimo że samo uwierzytelnianie runtime Bedrock nadal korzysta z domyślnego
      łańcucha AWS SDK.
      | 13 | `contributeResolvedModelCompat` | Flagi zgodności dla modeli dostawcy za innym zgodnym transportem |
      | 14 | `capabilities` | Starszy statyczny zbiór capabilities; tylko dla zgodności |
      | 15 | `normalizeToolSchemas` | Czyszczenie schematów narzędzi zarządzane przez dostawcę przed rejestracją |
      | 16 | `inspectToolSchemas` | Diagnostyka schematów narzędzi zarządzana przez dostawcę |
      | 17 | `resolveReasoningOutputMode` | Oznaczony vs natywny kontrakt wyjścia reasoning |
      | 18 | `prepareExtraParams` | Domyślne parametry żądania |
      | 19 | `createStreamFn` | W pełni niestandardowy transport StreamFn |
      | 20 | `wrapStreamFn` | Opakowania niestandardowych nagłówków/ciała na zwykłej ścieżce strumienia |
      | 21 | `resolveTransportTurnState` | Natywne nagłówki/metadane dla każdej tury |
      | 22 | `resolveWebSocketSessionPolicy` | Natywne nagłówki sesji WS / czas odnowienia |
      | 23 | `formatApiKey` | Niestandardowy kształt tokena runtime |
      | 24 | `refreshOAuth` | Niestandardowe odświeżanie OAuth |
      | 25 | `buildAuthDoctorHint` | Wskazówki naprawy auth |
      | 26 | `matchesContextOverflowError` | Wykrywanie przepełnienia zarządzane przez dostawcę |
      | 27 | `classifyFailoverReason` | Klasyfikacja limitu szybkości / przeciążenia zarządzana przez dostawcę |
      | 28 | `isCacheTtlEligible` | Bramka TTL cache promptów |
      | 29 | `buildMissingAuthMessage` | Niestandardowa wskazówka braku auth |
      | 30 | `suppressBuiltInModel` | Ukrywanie przestarzałych wierszy upstream |
      | 31 | `augmentModelCatalog` | Syntetyczne wiersze zgodności do przodu |
      | 32 | `isBinaryThinking` | Binarne włączanie/wyłączanie thinking |
      | 33 | `supportsXHighThinking` | Obsługa reasoning `xhigh` |
      | 34 | `resolveDefaultThinkingLevel` | Domyślna polityka `/think` |
      | 35 | `isModernModelRef` | Dopasowanie modeli live/smoke |
      | 36 | `prepareRuntimeAuth` | Wymiana tokena przed inferencją |
      | 37 | `resolveUsageAuth` | Niestandardowe parsowanie poświadczeń użycia |
      | 38 | `fetchUsageSnapshot` | Niestandardowy endpoint użycia |
      | 39 | `createEmbeddingProvider` | Adapter embeddingów zarządzany przez dostawcę dla pamięci/wyszukiwania |
      | 40 | `buildReplayPolicy` | Niestandardowa polityka replay/kompaktacji transkryptu |
      | 41 | `sanitizeReplayHistory` | Przepisania replay specyficzne dla dostawcy po ogólnym czyszczeniu |
      | 42 | `validateReplayTurns` | Ścisła walidacja tur replay przed osadzonym runnerem |
      | 43 | `onModelSelected` | Callback po wyborze (np. telemetria) |

      Uwaga dotycząca dostrajania promptów:

      - `resolveSystemPromptContribution` pozwala dostawcy wstrzykiwać
        wskazówki system promptu świadome cache dla rodziny modeli. Preferuj to zamiast
        `before_prompt_build`, gdy zachowanie należy do jednej rodziny dostawcy/modeli
        i powinno zachować stabilny/dynamiczny podział cache.

      Szczegółowe opisy i przykłady z praktyki znajdziesz w
      [Wewnętrzne: hooki runtime dostawców](/pl/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Dodaj dodatkowe capabilities (opcjonalnie)">
    <a id="step-5-add-extra-capabilities"></a>
    Plugin dostawcy może rejestrować mowę, transkrypcję realtime, głos realtime,
    rozumienie multimediów, generowanie obrazów, generowanie wideo, pobieranie z sieci
    i wyszukiwanie w sieci obok inferencji tekstu:

    ```typescript
    register(api) {
      api.registerProvider({ id: "acme-ai", /* ... */ });

      api.registerSpeechProvider({
        id: "acme-ai",
        label: "Acme Speech",
        isConfigured: ({ config }) => Boolean(config.messages?.tts),
        synthesize: async (req) => ({
          audioBuffer: Buffer.from(/* PCM data */),
          outputFormat: "mp3",
          fileExtension: ".mp3",
          voiceCompatible: false,
        }),
      });

      api.registerRealtimeTranscriptionProvider({
        id: "acme-ai",
        label: "Acme Realtime Transcription",
        isConfigured: () => true,
        createSession: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerRealtimeVoiceProvider({
        id: "acme-ai",
        label: "Acme Realtime Voice",
        isConfigured: ({ providerConfig }) => Boolean(providerConfig.apiKey),
        createBridge: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          setMediaTimestamp: () => {},
          submitToolResult: () => {},
          acknowledgeMark: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerMediaUnderstandingProvider({
        id: "acme-ai",
        capabilities: ["image", "audio"],
        describeImage: async (req) => ({ text: "A photo of..." }),
        transcribeAudio: async (req) => ({ text: "Transcript..." }),
      });

      api.registerImageGenerationProvider({
        id: "acme-ai",
        label: "Acme Images",
        generate: async (req) => ({ /* image result */ }),
      });

      api.registerVideoGenerationProvider({
        id: "acme-ai",
        label: "Acme Video",
        capabilities: {
          maxVideos: 1,
          maxDurationSeconds: 10,
          supportsResolution: true,
        },
        generateVideo: async (req) => ({ videos: [] }),
      });

      api.registerWebFetchProvider({
        id: "acme-ai-fetch",
        label: "Acme Fetch",
        hint: "Fetch pages through Acme's rendering backend.",
        envVars: ["ACME_FETCH_API_KEY"],
        placeholder: "acme-...",
        signupUrl: "https://acme.example.com/fetch",
        credentialPath: "plugins.entries.acme.config.webFetch.apiKey",
        getCredentialValue: (fetchConfig) => fetchConfig?.acme?.apiKey,
        setCredentialValue: (fetchConfigTarget, value) => {
          const acme = (fetchConfigTarget.acme ??= {});
          acme.apiKey = value;
        },
        createTool: () => ({
          description: "Fetch a page through Acme Fetch.",
          parameters: {},
          execute: async (args) => ({ content: [] }),
        }),
      });

      api.registerWebSearchProvider({
        id: "acme-ai-search",
        label: "Acme Search",
        search: async (req) => ({ content: [] }),
      });
    }
    ```

    OpenClaw klasyfikuje to jako plugin **hybrid-capability**. To jest
    zalecany wzorzec dla pluginów firmowych (jeden plugin na dostawcę). Zobacz
    [Wewnętrzne: własność capability](/pl/plugins/architecture#capability-ownership-model).

  </Step>

  <Step title="Testowanie">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Export your provider config object from index.ts or a dedicated file
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("resolves dynamic models", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("returns catalog when key is available", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("returns null catalog when no key", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## Publikowanie w ClawHub

Pluginy dostawców publikuje się tak samo jak każdy inny zewnętrzny plugin kodu:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Nie używaj tutaj starszego aliasu publikacji tylko dla Skills; pakiety pluginów powinny używać
`clawhub package publish`.

## Struktura plików

```
<bundled-plugin-root>/acme-ai/
├── package.json              # metadane openclaw.providers
├── openclaw.plugin.json      # Manifest z providerAuthEnvVars
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Testy
    └── usage.ts              # Endpoint użycia (opcjonalnie)
```

## Dokumentacja kolejności katalogów

`catalog.order` określa, kiedy Twój katalog jest scalany względem wbudowanych
dostawców:

| Order     | Kiedy         | Zastosowanie                                   |
| --------- | ------------- | ---------------------------------------------- |
| `simple`  | Pierwszy przebieg | Prości dostawcy z kluczem API                |
| `profile` | Po simple     | Dostawcy zależni od profili auth               |
| `paired`  | Po profile    | Syntezowanie wielu powiązanych wpisów          |
| `late`    | Ostatni przebieg | Nadpisywanie istniejących dostawców (wygrywa przy kolizji) |

## Następne kroki

- [Pluginy kanałów](/pl/plugins/sdk-channel-plugins) — jeśli Twój plugin udostępnia też kanał
- [SDK Runtime](/pl/plugins/sdk-runtime) — helpery `api.runtime` (TTS, wyszukiwanie, subagent)
- [Przegląd SDK](/pl/plugins/sdk-overview) — pełne odniesienie do importów subścieżek
- [Wewnętrzne działanie pluginów](/pl/plugins/architecture#provider-runtime-hooks) — szczegóły hooków i dołączone przykłady
