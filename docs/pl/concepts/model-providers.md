---
read_when:
    - Potrzebujesz dokumentacji konfiguracji modeli dla każdego dostawcy z osobna
    - Chcesz przykładowych konfiguracji lub poleceń wdrażania w CLI dla dostawców modeli
summary: Przegląd dostawcy modeli z przykładowymi konfiguracjami + przepływami CLI
title: Dostawcy modeli
x-i18n:
    generated_at: "2026-04-13T08:50:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66ba688c4b4366eec07667571e835d4cfeee684896e2ffae11d601b5fa0a4b98
    source_path: concepts/model-providers.md
    workflow: 15
---

# Dostawcy modeli

Ta strona dotyczy **dostawców LLM/modeli** (a nie kanałów czatu, takich jak WhatsApp/Telegram).
Reguły wyboru modeli znajdziesz tutaj: [/concepts/models](/pl/concepts/models).

## Szybkie zasady

- Referencje modeli używają formatu `provider/model` (przykład: `opencode/claude-opus-4-6`).
- Jeśli ustawisz `agents.defaults.models`, stanie się to listą dozwolonych modeli.
- Pomocnicze polecenia CLI: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Zasady awaryjnego działania w runtime, sondy cooldown oraz trwałość nadpisań sesji są
  udokumentowane w [/concepts/model-failover](/pl/concepts/model-failover).
- `models.providers.*.models[].contextWindow` to natywne metadane modelu;
  `models.providers.*.models[].contextTokens` to skuteczny limit runtime.
- Provider plugins mogą wstrzykiwać katalogi modeli przez `registerProvider({ catalog })`;
  OpenClaw scala to wyjście z `models.providers` przed zapisaniem
  `models.json`.
- Manifesty dostawców mogą deklarować `providerAuthEnvVars` oraz
  `providerAuthAliases`, aby ogólne sondy uwierzytelniania oparte na zmiennych środowiskowych i warianty dostawców
  nie musiały ładować runtime Plugin.
  Pozostała mapa zmiennych środowiskowych w rdzeniu służy teraz
  wyłącznie dostawcom spoza pluginów/rdzenia oraz kilku przypadkom ogólnego priorytetu, takim
  jak wdrażanie Anthropic z priorytetem klucza API.
- Provider plugins mogą też zarządzać zachowaniem dostawcy w runtime przez
  `normalizeModelId`, `normalizeTransport`, `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`,
  `normalizeResolvedModel`, `contributeResolvedModelCompat`,
  `capabilities`, `normalizeToolSchemas`,
  `inspectToolSchemas`, `resolveReasoningOutputMode`,
  `prepareExtraParams`, `createStreamFn`, `wrapStreamFn`,
  `resolveTransportTurnState`, `resolveWebSocketSessionPolicy`,
  `createEmbeddingProvider`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`,
  `matchesContextOverflowError`, `classifyFailoverReason`,
  `isCacheTtlEligible`, `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot`, oraz
  `onModelSelected`.
- Uwaga: `capabilities` dostawcy w runtime to współdzielone metadane wykonawcze (rodzina dostawcy,
  specyfika transkryptu/narzędzi, wskazówki dotyczące transportu/cache). To nie to samo co [publiczny model możliwości](/pl/plugins/architecture#public-capability-model),
  który opisuje, co rejestruje Plugin (wnioskowanie tekstowe, mowa itd.).
- Dołączony dostawca `codex` jest sparowany z dołączoną uprzężą agenta Codex.
  Używaj `codex/gpt-*`, gdy chcesz korzystać z logowania zarządzanego przez Codex, wykrywania modeli,
  natywnego wznawiania wątków i wykonywania na serwerze aplikacji. Zwykłe referencje `openai/gpt-*` nadal
  używają dostawcy OpenAI i standardowego transportu dostawcy OpenClaw.
  Wdrożenia wyłącznie z Codex mogą wyłączyć automatyczny fallback do PI przez
  `agents.defaults.embeddedHarness.fallback: "none"`; zobacz
  [Codex Harness](/pl/plugins/codex-harness).

## Zachowanie dostawcy zarządzane przez Plugin

Provider plugins mogą teraz zarządzać większością logiki specyficznej dla dostawcy, podczas gdy OpenClaw zachowuje
ogólną pętlę wnioskowania.

Typowy podział:

- `auth[].run` / `auth[].runNonInteractive`: dostawca zarządza przepływami onboarding/logowania
  dla `openclaw onboard`, `openclaw models auth` i konfiguracji bezobsługowej
- `wizard.setup` / `wizard.modelPicker`: dostawca zarządza etykietami wyboru uwierzytelniania,
  starszymi aliasami, wskazówkami listy dozwolonych modeli dla onboardingu oraz wpisami konfiguracji w selektorach onboardingu/modeli
- `catalog`: dostawca pojawia się w `models.providers`
- `normalizeModelId`: dostawca normalizuje starsze/poglądowe identyfikatory modeli przed
  wyszukiwaniem lub kanonikalizacją
- `normalizeTransport`: dostawca normalizuje `api` / `baseUrl` rodziny transportu
  przed ogólnym składaniem modelu; OpenClaw najpierw sprawdza dopasowanego dostawcę,
  następnie inne provider plugins obsługujące hooki, aż któryś faktycznie zmieni
  transport
- `normalizeConfig`: dostawca normalizuje konfigurację `models.providers.<id>` przed
  użyciem jej przez runtime; OpenClaw najpierw sprawdza dopasowanego dostawcę, a potem inne
  provider plugins obsługujące hooki, aż któryś faktycznie zmieni konfigurację. Jeśli żaden
  hook dostawcy nie przepisze konfiguracji, dołączone pomocnicze funkcje rodziny Google nadal
  normalizują obsługiwane wpisy dostawców Google.
- `applyNativeStreamingUsageCompat`: dostawca stosuje zgodnościowe przepisania natywnego użycia streamingu sterowane przez endpoint dla dostawców konfiguracyjnych
- `resolveConfigApiKey`: dostawca rozwiązuje uwierzytelnianie znacznikami środowiskowymi dla dostawców konfiguracyjnych
  bez wymuszania pełnego ładowania uwierzytelniania runtime. `amazon-bedrock` ma tu również
  wbudowany mechanizm rozwiązywania znaczników środowiskowych AWS, mimo że uwierzytelnianie Bedrock w runtime używa
  domyślnego łańcucha AWS SDK.
- `resolveSyntheticAuth`: dostawca może ujawniać dostępność uwierzytelniania lokalnego/self-hosted lub innego
  opartego na konfiguracji bez utrwalania sekretów w postaci jawnego tekstu
- `shouldDeferSyntheticProfileAuth`: dostawca może oznaczać zapisane syntetyczne placeholdery profili
  jako mające niższy priorytet niż uwierzytelnianie oparte na środowisku/konfiguracji
- `resolveDynamicModel`: dostawca akceptuje identyfikatory modeli, które nie są jeszcze obecne w lokalnym
  statycznym katalogu
- `prepareDynamicModel`: dostawca wymaga odświeżenia metadanych przed ponowną próbą
  dynamicznego rozpoznania
- `normalizeResolvedModel`: dostawca wymaga przepisania transportu lub podstawowego URL
- `contributeResolvedModelCompat`: dostawca wnosi flagi zgodności dla swoich
  modeli dostawcy, nawet gdy docierają one przez inny kompatybilny transport
- `capabilities`: dostawca publikuje specyfikę transkryptu/narzędzi/rodziny dostawcy
- `normalizeToolSchemas`: dostawca czyści schematy narzędzi, zanim zobaczy je osadzony
  runner
- `inspectToolSchemas`: dostawca udostępnia ostrzeżenia dotyczące schematów specyficzne dla transportu
  po normalizacji
- `resolveReasoningOutputMode`: dostawca wybiera natywne lub oznaczane tagami
  kontrakty wyjścia rozumowania
- `prepareExtraParams`: dostawca ustawia wartości domyślne lub normalizuje parametry żądania dla poszczególnych modeli
- `createStreamFn`: dostawca zastępuje standardową ścieżkę strumieniowania całkowicie
  niestandardowym transportem
- `wrapStreamFn`: dostawca stosuje opakowania zgodności nagłówków/ciała/modelu żądania
- `resolveTransportTurnState`: dostawca dostarcza natywne nagłówki lub metadane transportu
  dla każdej tury
- `resolveWebSocketSessionPolicy`: dostawca dostarcza natywne nagłówki sesji WebSocket
  lub zasady cooldown sesji
- `createEmbeddingProvider`: dostawca zarządza zachowaniem osadzeń pamięci, gdy
  powinno ono należeć do Plugin dostawcy zamiast do głównego przełącznika osadzeń rdzenia
- `formatApiKey`: dostawca formatuje zapisane profile uwierzytelniania do postaci
  ciągu `apiKey` oczekiwanego przez transport w runtime
- `refreshOAuth`: dostawca zarządza odświeżaniem OAuth, gdy współdzielone mechanizmy odświeżania `pi-ai`
  nie są wystarczające
- `buildAuthDoctorHint`: dostawca dodaje wskazówki naprawcze, gdy odświeżenie OAuth
  się nie powiedzie
- `matchesContextOverflowError`: dostawca rozpoznaje specyficzne dla dostawcy
  błędy przepełnienia okna kontekstu, których ogólne heurystyki by nie wykryły
- `classifyFailoverReason`: dostawca mapuje surowe błędy transportu/API specyficzne dla dostawcy
  na powody przełączenia awaryjnego, takie jak limit szybkości lub przeciążenie
- `isCacheTtlEligible`: dostawca decyduje, które nadrzędne identyfikatory modeli obsługują TTL cache promptów
- `buildMissingAuthMessage`: dostawca zastępuje ogólny błąd magazynu uwierzytelniania
  wskazówką odzyskiwania specyficzną dla dostawcy
- `suppressBuiltInModel`: dostawca ukrywa nieaktualne wiersze upstream i może zwracać
  błąd zarządzany przez dostawcę przy bezpośrednich niepowodzeniach rozpoznania
- `augmentModelCatalog`: dostawca dopisuje syntetyczne/końcowe wiersze katalogu po
  wykryciu i scaleniu konfiguracji
- `isBinaryThinking`: dostawca zarządza binarnym UX myślenia włącz/wyłącz
- `supportsXHighThinking`: dostawca włącza `xhigh` dla wybranych modeli
- `resolveDefaultThinkingLevel`: dostawca zarządza domyślną polityką `/think` dla
  rodziny modeli
- `applyConfigDefaults`: dostawca stosuje globalne wartości domyślne specyficzne dla dostawcy
  podczas materializacji konfiguracji na podstawie trybu uwierzytelniania, środowiska lub rodziny modeli
- `isModernModelRef`: dostawca zarządza dopasowaniem preferowanych modeli dla testów live/smoke
- `prepareRuntimeAuth`: dostawca przekształca skonfigurowane poświadczenie w krótkotrwały
  token runtime
- `resolveUsageAuth`: dostawca rozwiązuje poświadczenia użycia/limitu dla `/usage`
  oraz powiązanych powierzchni statusu/raportowania
- `fetchUsageSnapshot`: dostawca zarządza pobieraniem/parsingiem endpointu użycia, podczas gdy
  rdzeń nadal zarządza powłoką podsumowania i formatowaniem
- `onModelSelected`: dostawca wykonuje działania uboczne po wyborze modelu, takie jak
  telemetria lub zarządzane przez dostawcę prowadzenie księgowości sesji

Aktualne dołączone przykłady:

- `anthropic`: fallback zgodności do przodu dla Claude 4.6, wskazówki naprawy uwierzytelniania, pobieranie
  endpointu użycia, metadane cache-TTL/rodziny dostawcy oraz globalne
  domyślne ustawienia konfiguracji zależne od uwierzytelniania
- `amazon-bedrock`: zarządzane przez dostawcę dopasowywanie przepełnienia kontekstu i klasyfikacja
  powodów failover dla błędów throttlingu/not-ready specyficznych dla Bedrock, a także
  współdzielona rodzina odtwarzania `anthropic-by-model` dla ochrony polityki odtwarzania
  tylko dla Claude na ruchu Anthropic
- `anthropic-vertex`: zabezpieczenia polityki odtwarzania tylko dla Claude na ruchu
  `anthropic-message`
- `openrouter`: identyfikatory modeli pass-through, opakowania żądań, wskazówki dotyczące możliwości dostawcy,
  sanityzacja sygnatur myśli Gemini na proxy ruchu Gemini, wstrzykiwanie rozumowania przez proxy
  przez rodzinę strumieni `openrouter-thinking`, przekazywanie metadanych routingu
  oraz polityka cache-TTL
- `github-copilot`: onboarding/logowanie urządzenia, fallback zgodności do przodu modeli,
  wskazówki transkryptu Claude-thinking, wymiana tokenu runtime oraz pobieranie endpointu
  użycia
- `openai`: fallback zgodności do przodu dla GPT-5.4, bezpośrednia normalizacja
  transportu OpenAI, wskazówki brakującego uwierzytelniania uwzględniające Codex, wyciszenie Spark, syntetyczne
  wiersze katalogu OpenAI/Codex, polityka thinking/live-model, normalizacja aliasów tokenów użycia
  (`input` / `output` oraz rodziny `prompt` / `completion`), współdzielona
  rodzina strumieni `openai-responses-defaults` dla natywnych opakowań OpenAI/Codex,
  metadane rodziny dostawcy, rejestracja dołączonego dostawcy generowania obrazów
  dla `gpt-image-1` oraz rejestracja dołączonego dostawcy generowania wideo
  dla `sora-2`
- `google` i `google-gemini-cli`: fallback zgodności do przodu dla Gemini 3.1,
  natywna walidacja odtwarzania Gemini, sanityzacja odtwarzania bootstrap,
  tryb wyjścia rozumowania oznaczanego tagami, dopasowanie nowoczesnych modeli, rejestracja dołączonego dostawcy generowania obrazów
  dla modeli Gemini image-preview oraz dołączona
  rejestracja dostawcy generowania wideo dla modeli Veo; OAuth Gemini CLI zarządza też
  formatowaniem tokenów profilu uwierzytelniania, parsowaniem tokenów użycia oraz pobieraniem endpointu limitów
  dla powierzchni użycia
- `moonshot`: współdzielony transport, zarządzana przez Plugin normalizacja payloadu thinking
- `kilocode`: współdzielony transport, zarządzane przez Plugin nagłówki żądań, normalizacja payloadu rozumowania,
  sanityzacja sygnatur myśli proxy-Gemini oraz polityka cache-TTL
- `zai`: fallback zgodności do przodu dla GLM-5, domyślne `tool_stream`, polityka cache-TTL,
  polityka binary-thinking/live-model oraz uwierzytelnianie użycia + pobieranie limitów;
  nieznane identyfikatory `glm-5*` są syntetyzowane z dołączonego szablonu `glm-4.7`
- `xai`: natywna normalizacja transportu Responses, przepisania aliasów `/fast` dla
  szybkich wariantów Grok, domyślne `tool_stream`, czyszczenie schematów narzędzi / payloadów rozumowania
  specyficzne dla xAI oraz dołączona rejestracja dostawcy generowania wideo
  dla `grok-imagine-video`
- `mistral`: metadane możliwości zarządzane przez Plugin
- `opencode` i `opencode-go`: metadane możliwości zarządzane przez Plugin oraz
  sanityzacja sygnatur myśli proxy-Gemini
- `alibaba`: zarządzany przez Plugin katalog generowania wideo dla bezpośrednich referencji modeli Wan
  takich jak `alibaba/wan2.6-t2v`
- `byteplus`: katalogi zarządzane przez Plugin oraz dołączona rejestracja dostawcy generowania wideo
  dla modeli Seedance text-to-video/image-to-video
- `fal`: dołączona rejestracja dostawcy generowania wideo dla hostowanych zewnętrznych modeli
  oraz rejestracja dostawcy generowania obrazów dla modeli obrazów FLUX, a także dołączona
  rejestracja dostawcy generowania wideo dla hostowanych zewnętrznych modeli wideo
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway` i `volcengine`:
  wyłącznie katalogi zarządzane przez Plugin
- `qwen`: katalogi zarządzane przez Plugin dla modeli tekstowych oraz współdzielone
  rejestracje dostawców rozumienia mediów i generowania wideo dla ich
  multimodalnych powierzchni; generowanie wideo Qwen używa standardowych endpointów wideo DashScope
  z dołączonymi modelami Wan, takimi jak `wan2.6-t2v` i `wan2.7-r2v`
- `runway`: zarządzana przez Plugin rejestracja dostawcy generowania wideo dla natywnych
  modeli Runway opartych na zadaniach, takich jak `gen4.5`
- `minimax`: katalogi zarządzane przez Plugin, dołączona rejestracja dostawcy generowania wideo
  dla modeli wideo Hailuo, dołączona rejestracja dostawcy generowania obrazów
  dla `image-01`, hybrydowy wybór polityki odtwarzania Anthropic/OpenAI
  oraz logika uwierzytelniania/migawek użycia
- `together`: katalogi zarządzane przez Plugin oraz dołączona rejestracja dostawcy generowania wideo
  dla modeli wideo Wan
- `xiaomi`: katalogi zarządzane przez Plugin oraz logika uwierzytelniania/migawek użycia

Dołączony Plugin `openai` obsługuje teraz oba identyfikatory dostawców: `openai` i
`openai-codex`.

To obejmuje dostawców, którzy nadal mieszczą się w standardowych transportach OpenClaw. Dostawca,
który wymaga całkowicie niestandardowego wykonawcy żądań, to osobna, głębsza powierzchnia rozszerzeń.

## Rotacja kluczy API

- Obsługuje ogólną rotację dostawców dla wybranych dostawców.
- Skonfiguruj wiele kluczy przez:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (pojedyncze nadpisanie live, najwyższy priorytet)
  - `<PROVIDER>_API_KEYS` (lista rozdzielana przecinkami lub średnikami)
  - `<PROVIDER>_API_KEY` (klucz główny)
  - `<PROVIDER>_API_KEY_*` (lista numerowana, np. `<PROVIDER>_API_KEY_1`)
- Dla dostawców Google jako fallback uwzględniany jest także `GOOGLE_API_KEY`.
- Kolejność wyboru kluczy zachowuje priorytet i usuwa duplikaty wartości.
- Żądania są ponawiane z następnym kluczem tylko przy odpowiedziach z limitem szybkości (na
  przykład `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded` lub okresowe komunikaty o limicie użycia).
- Błędy inne niż związane z limitem szybkości kończą się od razu niepowodzeniem; rotacja kluczy nie jest podejmowana.
- Gdy wszystkie klucze kandydackie zawiodą, zwracany jest końcowy błąd z ostatniej próby.

## Wbudowani dostawcy (katalog pi-ai)

OpenClaw jest dostarczany z katalogiem pi-ai. Ci dostawcy nie wymagają
konfiguracji `models.providers`; wystarczy ustawić uwierzytelnianie i wybrać model.

### OpenAI

- Dostawca: `openai`
- Uwierzytelnianie: `OPENAI_API_KEY`
- Opcjonalna rotacja: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, oraz `OPENCLAW_LIVE_OPENAI_KEY` (pojedyncze nadpisanie)
- Przykładowe modele: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- Domyślny transport to `auto` (najpierw WebSocket, fallback do SSE)
- Nadpisanie dla konkretnego modelu przez `agents.defaults.models["openai/<model>"].params.transport` (`"sse"`, `"websocket"` lub `"auto"`)
- Rozgrzewanie WebSocket OpenAI Responses jest domyślnie włączone przez `params.openaiWsWarmup` (`true`/`false`)
- Priorytetowe przetwarzanie OpenAI można włączyć przez `agents.defaults.models["openai/<model>"].params.serviceTier`
- `/fast` oraz `params.fastMode` mapują bezpośrednie żądania Responses `openai/*` na `service_tier=priority` na `api.openai.com`
- Używaj `params.serviceTier`, gdy chcesz jawnego poziomu zamiast współdzielonego przełącznika `/fast`
- Ukryte nagłówki atrybucji OpenClaw (`originator`, `version`,
  `User-Agent`) są stosowane tylko w natywnym ruchu OpenAI do `api.openai.com`, a nie
  do ogólnych proxy zgodnych z OpenAI
- Natywne trasy OpenAI zachowują też `store` dla Responses, wskazówki cache promptów oraz
  kształtowanie payloadu zgodności rozumowania OpenAI; trasy proxy tego nie robią
- `openai/gpt-5.3-codex-spark` jest celowo wyciszony w OpenClaw, ponieważ aktywne API OpenAI go odrzuca; Spark jest traktowany wyłącznie jako Codex

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Dostawca: `anthropic`
- Uwierzytelnianie: `ANTHROPIC_API_KEY`
- Opcjonalna rotacja: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, oraz `OPENCLAW_LIVE_ANTHROPIC_KEY` (pojedyncze nadpisanie)
- Przykładowy model: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- Bezpośrednie publiczne żądania Anthropic obsługują też współdzielony przełącznik `/fast` i `params.fastMode`, w tym ruch uwierzytelniany kluczem API i OAuth wysyłany do `api.anthropic.com`; OpenClaw mapuje to na Anthropic `service_tier` (`auto` vs `standard_only`)
- Uwaga Anthropic: pracownicy Anthropic przekazali nam, że użycie Claude CLI w stylu OpenClaw jest znów dozwolone, więc OpenClaw traktuje ponowne użycie Claude CLI i użycie `claude -p` jako zatwierdzone dla tej integracji, chyba że Anthropic opublikuje nową politykę.
- Token konfiguracji Anthropic pozostaje dostępny jako obsługiwana ścieżka tokenu OpenClaw, ale OpenClaw preferuje teraz ponowne użycie Claude CLI i `claude -p`, gdy są dostępne.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- Dostawca: `openai-codex`
- Uwierzytelnianie: OAuth (ChatGPT)
- Przykładowy model: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` lub `openclaw models auth login --provider openai-codex`
- Domyślny transport to `auto` (najpierw WebSocket, fallback do SSE)
- Nadpisanie dla konkretnego modelu przez `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"`, `"websocket"` lub `"auto"`)
- `params.serviceTier` jest też przekazywane w natywnych żądaniach Codex Responses (`chatgpt.com/backend-api`)
- Ukryte nagłówki atrybucji OpenClaw (`originator`, `version`,
  `User-Agent`) są dołączane tylko w natywnym ruchu Codex do
  `chatgpt.com/backend-api`, a nie do ogólnych proxy zgodnych z OpenAI
- Współdzieli ten sam przełącznik `/fast` i konfigurację `params.fastMode` co bezpośrednie `openai/*`; OpenClaw mapuje to na `service_tier=priority`
- `openai-codex/gpt-5.3-codex-spark` pozostaje dostępny, gdy katalog OAuth Codex go udostępnia; zależne od uprawnień
- `openai-codex/gpt-5.4` zachowuje natywne `contextWindow = 1050000` oraz domyślne runtime `contextTokens = 272000`; nadpisz limit runtime przez `models.providers.openai-codex.models[].contextTokens`
- Uwaga dotycząca polityki: OAuth OpenAI Codex jest oficjalnie obsługiwany dla zewnętrznych narzędzi/przepływów pracy, takich jak OpenClaw.

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

### Inne hostowane opcje w stylu subskrypcyjnym

- [Qwen Cloud](/pl/providers/qwen): powierzchnia dostawcy Qwen Cloud oraz mapowanie endpointów Alibaba DashScope i Coding Plan
- [MiniMax](/pl/providers/minimax): OAuth MiniMax Coding Plan lub dostęp przez klucz API
- [GLM Models](/pl/providers/glm): Z.AI Coding Plan lub ogólne endpointy API

### OpenCode

- Uwierzytelnianie: `OPENCODE_API_KEY` (lub `OPENCODE_ZEN_API_KEY`)
- Dostawca runtime Zen: `opencode`
- Dostawca runtime Go: `opencode-go`
- Przykładowe modele: `opencode/claude-opus-4-6`, `opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` lub `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (klucz API)

- Dostawca: `google`
- Uwierzytelnianie: `GEMINI_API_KEY`
- Opcjonalna rotacja: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, fallback `GOOGLE_API_KEY` oraz `OPENCLAW_LIVE_GEMINI_KEY` (pojedyncze nadpisanie)
- Przykładowe modele: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- Zgodność: starsza konfiguracja OpenClaw używająca `google/gemini-3.1-flash-preview` jest normalizowana do `google/gemini-3-flash-preview`
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- Bezpośrednie uruchomienia Gemini akceptują też `agents.defaults.models["google/<model>"].params.cachedContent`
  (lub starsze `cached_content`) do przekazania natywnego dla dostawcy
  uchwytu `cachedContents/...`; trafienia cache Gemini są ujawniane jako OpenClaw `cacheRead`

### Google Vertex i Gemini CLI

- Dostawcy: `google-vertex`, `google-gemini-cli`
- Uwierzytelnianie: Vertex używa gcloud ADC; Gemini CLI używa własnego przepływu OAuth
- Uwaga: OAuth Gemini CLI w OpenClaw jest nieoficjalną integracją. Niektórzy użytkownicy zgłaszali ograniczenia kont Google po użyciu klientów zewnętrznych. Zapoznaj się z warunkami Google i użyj niekrytycznego konta, jeśli zdecydujesz się kontynuować.
- OAuth Gemini CLI jest dostarczany jako część dołączonego Plugin `google`.
  - Najpierw zainstaluj Gemini CLI:
    - `brew install gemini-cli`
    - lub `npm install -g @google/gemini-cli`
  - Włącz: `openclaw plugins enable google`
  - Zaloguj się: `openclaw models auth login --provider google-gemini-cli --set-default`
  - Domyślny model: `google-gemini-cli/gemini-3-flash-preview`
  - Uwaga: **nie** wklejasz identyfikatora klienta ani sekretu do `openclaw.json`. Przepływ logowania CLI zapisuje
    tokeny w profilach uwierzytelniania na hoście Gateway.
  - Jeśli żądania kończą się niepowodzeniem po zalogowaniu, ustaw `GOOGLE_CLOUD_PROJECT` lub `GOOGLE_CLOUD_PROJECT_ID` na hoście Gateway.
  - Odpowiedzi JSON Gemini CLI są parsowane z `response`; użycie przechodzi awaryjnie do
    `stats`, a `stats.cached` jest normalizowane do OpenClaw `cacheRead`.

### Z.AI (GLM)

- Dostawca: `zai`
- Uwierzytelnianie: `ZAI_API_KEY`
- Przykładowy model: `zai/glm-5.1`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - Aliasy: `z.ai/*` i `z-ai/*` są normalizowane do `zai/*`
  - `zai-api-key` automatycznie wykrywa pasujący endpoint Z.AI; `zai-coding-global`, `zai-coding-cn`, `zai-global` i `zai-cn` wymuszają określoną powierzchnię

### Vercel AI Gateway

- Dostawca: `vercel-ai-gateway`
- Uwierzytelnianie: `AI_GATEWAY_API_KEY`
- Przykładowy model: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- Dostawca: `kilocode`
- Uwierzytelnianie: `KILOCODE_API_KEY`
- Przykładowy model: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- Bazowy URL: `https://api.kilo.ai/api/gateway/`
- Statyczny katalog fallback zawiera `kilocode/kilo/auto`; aktywne
  wykrywanie `https://api.kilo.ai/api/gateway/models` może dalej rozszerzać
  katalog runtime.
- Dokładny routing upstream za `kilocode/kilo/auto` jest zarządzany przez Kilo Gateway,
  a nie zakodowany na sztywno w OpenClaw.

Szczegóły konfiguracji znajdziesz w [/providers/kilocode](/pl/providers/kilocode).

### Inne dołączone provider plugins

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- Przykładowy model: `openrouter/auto`
- OpenClaw stosuje udokumentowane przez OpenRouter nagłówki atrybucji aplikacji tylko wtedy, gdy
  żądanie faktycznie trafia do `openrouter.ai`
- Specyficzne dla OpenRouter znaczniki Anthropic `cache_control` są podobnie ograniczone do
  zweryfikowanych tras OpenRouter, a nie dowolnych adresów proxy
- OpenRouter pozostaje na ścieżce proxy w stylu kompatybilnym z OpenAI, więc natywne
  kształtowanie żądań tylko dla OpenAI (`serviceTier`, `store` dla Responses,
  wskazówki cache promptów, payloady zgodności rozumowania OpenAI) nie jest przekazywane
- Referencje OpenRouter oparte na Gemini zachowują tylko sanityzację sygnatur myśli proxy-Gemini;
  natywna walidacja odtwarzania Gemini i przepisania bootstrap pozostają wyłączone
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- Przykładowy model: `kilocode/kilo/auto`
- Referencje Kilo oparte na Gemini zachowują tę samą ścieżkę sanityzacji sygnatur myśli
  proxy-Gemini; `kilocode/kilo/auto` i inne wskazówki proxy bez obsługi rozumowania
  pomijają wstrzykiwanie rozumowania przez proxy
- MiniMax: `minimax` (klucz API) i `minimax-portal` (OAuth)
- Uwierzytelnianie: `MINIMAX_API_KEY` dla `minimax`; `MINIMAX_OAUTH_TOKEN` lub `MINIMAX_API_KEY` dla `minimax-portal`
- Przykładowy model: `minimax/MiniMax-M2.7` lub `minimax-portal/MiniMax-M2.7`
- Onboarding MiniMax/konfiguracja klucza API zapisuje jawne definicje modeli M2.7 z
  `input: ["text", "image"]`; dołączony katalog dostawcy zachowuje referencje czatu
  jako tylko tekstowe, dopóki konfiguracja tego dostawcy nie zostanie zmaterializowana
- Moonshot: `moonshot` (`MOONSHOT_API_KEY`)
- Przykładowy model: `moonshot/kimi-k2.5`
- Kimi Coding: `kimi` (`KIMI_API_KEY` lub `KIMICODE_API_KEY`)
- Przykładowy model: `kimi/kimi-code`
- Qianfan: `qianfan` (`QIANFAN_API_KEY`)
- Przykładowy model: `qianfan/deepseek-v3.2`
- Qwen Cloud: `qwen` (`QWEN_API_KEY`, `MODELSTUDIO_API_KEY` lub `DASHSCOPE_API_KEY`)
- Przykładowy model: `qwen/qwen3.5-plus`
- NVIDIA: `nvidia` (`NVIDIA_API_KEY`)
- Przykładowy model: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: `stepfun` / `stepfun-plan` (`STEPFUN_API_KEY`)
- Przykładowe modele: `stepfun/step-3.5-flash`, `stepfun-plan/step-3.5-flash-2603`
- Together: `together` (`TOGETHER_API_KEY`)
- Przykładowy model: `together/moonshotai/Kimi-K2.5`
- Venice: `venice` (`VENICE_API_KEY`)
- Xiaomi: `xiaomi` (`XIAOMI_API_KEY`)
- Przykładowy model: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: `vercel-ai-gateway` (`AI_GATEWAY_API_KEY`)
- Hugging Face Inference: `huggingface` (`HUGGINGFACE_HUB_TOKEN` lub `HF_TOKEN`)
- Cloudflare AI Gateway: `cloudflare-ai-gateway` (`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine: `volcengine` (`VOLCANO_ENGINE_API_KEY`)
- Przykładowy model: `volcengine-plan/ark-code-latest`
- BytePlus: `byteplus` (`BYTEPLUS_API_KEY`)
- Przykładowy model: `byteplus-plan/ark-code-latest`
- xAI: `xai` (`XAI_API_KEY`)
  - Natywne dołączone żądania xAI używają ścieżki xAI Responses
  - `/fast` lub `params.fastMode: true` przepisują `grok-3`, `grok-3-mini`,
    `grok-4` i `grok-4-0709` na ich warianty `*-fast`
  - `tool_stream` jest domyślnie włączone; ustaw
    `agents.defaults.models["xai/<model>"].params.tool_stream` na `false`, aby
    to wyłączyć
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- Przykładowy model: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - Modele GLM w Cerebras używają identyfikatorów `zai-glm-4.7` i `zai-glm-4.6`.
  - Bazowy URL kompatybilny z OpenAI: `https://api.cerebras.ai/v1`.
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Przykładowy model Hugging Face Inference: `huggingface/deepseek-ai/DeepSeek-R1`; CLI: `openclaw onboard --auth-choice huggingface-api-key`. Zobacz [Hugging Face (Inference)](/pl/providers/huggingface).

## Dostawcy przez `models.providers` (niestandardowy/bazowy URL)

Użyj `models.providers` (lub `models.json`), aby dodać **niestandardowych** dostawców albo
proxy kompatybilne z OpenAI/Anthropic.

Wiele z dołączonych poniżej provider plugins publikuje już domyślny katalog.
Używaj jawnych wpisów `models.providers.<id>` tylko wtedy, gdy chcesz nadpisać
domyślny bazowy URL, nagłówki lub listę modeli.

### Moonshot AI (Kimi)

Moonshot jest dostarczany jako dołączony Plugin dostawcy. Domyślnie używaj wbudowanego dostawcy,
a jawny wpis `models.providers.moonshot` dodawaj tylko wtedy, gdy
musisz nadpisać bazowy URL lub metadane modelu:

- Dostawca: `moonshot`
- Uwierzytelnianie: `MOONSHOT_API_KEY`
- Przykładowy model: `moonshot/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice moonshot-api-key` lub `openclaw onboard --auth-choice moonshot-api-key-cn`

Identyfikatory modeli Kimi K2:

[//]: # "moonshot-kimi-k2-model-refs:start"

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
- `moonshot/kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-model-refs:end"

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

Kimi Coding używa endpointu Anthropic-compatible od Moonshot AI:

- Dostawca: `kimi`
- Uwierzytelnianie: `KIMI_API_KEY`
- Przykładowy model: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

Starsze `kimi/k2p5` pozostaje akceptowanym identyfikatorem modelu zgodności.

### Volcano Engine (Doubao)

Volcano Engine (火山引擎) zapewnia dostęp do Doubao i innych modeli w Chinach.

- Dostawca: `volcengine` (coding: `volcengine-plan`)
- Uwierzytelnianie: `VOLCANO_ENGINE_API_KEY`
- Przykładowy model: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

Onboarding domyślnie używa powierzchni coding, ale ogólny katalog `volcengine/*`
jest rejestrowany w tym samym czasie.

W selektorach modeli onboarding/configure wybór uwierzytelniania Volcengine preferuje zarówno
wiersze `volcengine/*`, jak i `volcengine-plan/*`. Jeśli te modele nie są jeszcze załadowane,
OpenClaw przechodzi awaryjnie do niefiltrowanego katalogu zamiast pokazywać pusty
selektor ograniczony do dostawcy.

Dostępne modele:

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

Modele coding (`volcengine-plan`):

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus (międzynarodowy)

BytePlus ARK zapewnia międzynarodowym użytkownikom dostęp do tych samych modeli co Volcano Engine.

- Dostawca: `byteplus` (coding: `byteplus-plan`)
- Uwierzytelnianie: `BYTEPLUS_API_KEY`
- Przykładowy model: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

Onboarding domyślnie używa powierzchni coding, ale ogólny katalog `byteplus/*`
jest rejestrowany w tym samym czasie.

W selektorach modeli onboarding/configure wybór uwierzytelniania BytePlus preferuje zarówno
wiersze `byteplus/*`, jak i `byteplus-plan/*`. Jeśli te modele nie są jeszcze załadowane,
OpenClaw przechodzi awaryjnie do niefiltrowanego katalogu zamiast pokazywać pusty
selektor ograniczony do dostawcy.

Dostępne modele:

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

Modele coding (`byteplus-plan`):

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic udostępnia modele kompatybilne z Anthropic za dostawcą `synthetic`:

- Dostawca: `synthetic`
- Uwierzytelnianie: `SYNTHETIC_API_KEY`
- Przykładowy model: `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI: `openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

MiniMax jest konfigurowany przez `models.providers`, ponieważ używa niestandardowych endpointów:

- MiniMax OAuth (Global): `--auth-choice minimax-global-oauth`
- MiniMax OAuth (CN): `--auth-choice minimax-cn-oauth`
- Klucz API MiniMax (Global): `--auth-choice minimax-global-api`
- Klucz API MiniMax (CN): `--auth-choice minimax-cn-api`
- Uwierzytelnianie: `MINIMAX_API_KEY` dla `minimax`; `MINIMAX_OAUTH_TOKEN` lub
  `MINIMAX_API_KEY` dla `minimax-portal`

Szczegóły konfiguracji, opcje modeli i fragmenty konfiguracji znajdziesz w [/providers/minimax](/pl/providers/minimax).

Na ścieżce streamingu kompatybilnej z Anthropic w MiniMax OpenClaw domyślnie wyłącza thinking,
chyba że ustawisz je jawnie, a `/fast on` przepisuje
`MiniMax-M2.7` na `MiniMax-M2.7-highspeed`.

Podział możliwości zarządzanych przez Plugin:

- Domyślne ustawienia tekst/czat pozostają przy `minimax/MiniMax-M2.7`
- Generowanie obrazów to `minimax/image-01` lub `minimax-portal/image-01`
- Rozumienie obrazów to zarządzany przez Plugin `MiniMax-VL-01` w obu ścieżkach uwierzytelniania MiniMax
- Wyszukiwanie w sieci pozostaje przy identyfikatorze dostawcy `minimax`

### LM Studio

LM Studio jest dostarczane jako dołączony Plugin dostawcy, który używa natywnego API:

- Dostawca: `lmstudio`
- Uwierzytelnianie: `LM_API_TOKEN`
- Domyślny bazowy URL wnioskowania: `http://localhost:1234/v1`

Następnie ustaw model (zastąp jednym z identyfikatorów zwróconych przez `http://localhost:1234/api/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "lmstudio/openai/gpt-oss-20b" } },
  },
}
```

OpenClaw używa natywnych endpointów LM Studio `/api/v1/models` i `/api/v1/models/load`
do wykrywania + automatycznego ładowania, a domyślnie do wnioskowania używa `/v1/chat/completions`.
Konfigurację i rozwiązywanie problemów znajdziesz w [/providers/lmstudio](/pl/providers/lmstudio).

### Ollama

Ollama jest dostarczana jako dołączony Plugin dostawcy i używa natywnego API Ollama:

- Dostawca: `ollama`
- Uwierzytelnianie: niewymagane (serwer lokalny)
- Przykładowy model: `ollama/llama3.3`
- Instalacja: [https://ollama.com/download](https://ollama.com/download)

```bash
# Zainstaluj Ollama, a następnie pobierz model:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

Ollama jest wykrywana lokalnie pod adresem `http://127.0.0.1:11434`, gdy włączysz ją przez
`OLLAMA_API_KEY`, a dołączony Plugin dostawcy dodaje Ollama bezpośrednio do
`openclaw onboard` oraz selektora modeli. Zobacz [/providers/ollama](/pl/providers/ollama),
aby poznać onboarding, tryb cloud/local oraz konfigurację niestandardową.

### vLLM

vLLM jest dostarczany jako dołączony Plugin dostawcy dla lokalnych/self-hosted serwerów
kompatybilnych z OpenAI:

- Dostawca: `vllm`
- Uwierzytelnianie: opcjonalne (zależy od Twojego serwera)
- Domyślny bazowy URL: `http://127.0.0.1:8000/v1`

Aby włączyć lokalne automatyczne wykrywanie (dowolna wartość działa, jeśli serwer nie wymusza uwierzytelniania):

```bash
export VLLM_API_KEY="vllm-local"
```

Następnie ustaw model (zastąp jednym z identyfikatorów zwróconych przez `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

Szczegóły znajdziesz w [/providers/vllm](/pl/providers/vllm).

### SGLang

SGLang jest dostarczany jako dołączony Plugin dostawcy dla szybkich samodzielnie hostowanych
serwerów kompatybilnych z OpenAI:

- Dostawca: `sglang`
- Uwierzytelnianie: opcjonalne (zależy od Twojego serwera)
- Domyślny bazowy URL: `http://127.0.0.1:30000/v1`

Aby włączyć lokalne automatyczne wykrywanie (dowolna wartość działa, jeśli serwer nie
wymusza uwierzytelniania):

```bash
export SGLANG_API_KEY="sglang-local"
```

Następnie ustaw model (zastąp jednym z identyfikatorów zwróconych przez `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

Szczegóły znajdziesz w [/providers/sglang](/pl/providers/sglang).

### Lokalne proxy (LM Studio, vLLM, LiteLLM itp.)

Przykład (kompatybilny z OpenAI):

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Lokalny" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "${LM_API_TOKEN}",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Model lokalny",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Uwagi:

- Dla niestandardowych dostawców `reasoning`, `input`, `cost`, `contextWindow` i `maxTokens` są opcjonalne.
  Jeśli zostaną pominięte, OpenClaw domyślnie przyjmuje:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- Zalecane: ustaw jawne wartości zgodne z limitami Twojego proxy/modelu.
- Dla `api: "openai-completions"` na nienatywnych endpointach (dowolny niepusty `baseUrl`, którego host nie jest `api.openai.com`) OpenClaw wymusza `compat.supportsDeveloperRole: false`, aby uniknąć błędów 400 od dostawcy dla nieobsługiwanych ról `developer`.
- Trasy proxy w stylu kompatybilnym z OpenAI pomijają też natywne kształtowanie żądań tylko dla OpenAI:
  bez `service_tier`, bez `store` dla Responses, bez wskazówek cache promptów, bez
  kształtowania payloadu zgodności rozumowania OpenAI i bez ukrytych nagłówków atrybucji OpenClaw.
- Jeśli `baseUrl` jest pusty/pominięty, OpenClaw zachowuje domyślne zachowanie OpenAI (które wskazuje na `api.openai.com`).
- Dla bezpieczeństwa jawne `compat.supportsDeveloperRole: true` jest nadal nadpisywane na nienatywnych endpointach `openai-completions`.

## Przykłady CLI

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

Zobacz też: [/gateway/configuration](/pl/gateway/configuration), aby poznać pełne przykłady konfiguracji.

## Powiązane

- [Models](/pl/concepts/models) — konfiguracja modeli i aliasy
- [Model Failover](/pl/concepts/model-failover) — łańcuchy fallback i zachowanie ponawiania
- [Configuration Reference](/pl/gateway/configuration-reference#agent-defaults) — klucze konfiguracji modeli
- [Providers](/pl/providers) — przewodniki konfiguracji dla poszczególnych dostawców
