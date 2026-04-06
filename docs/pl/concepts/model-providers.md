---
read_when:
    - Potrzebujesz odniesienia konfiguracji modeli dla każdego dostawcy
    - Chcesz zobaczyć przykładowe konfiguracje lub polecenia wdrożeniowe CLI dla dostawców modeli
summary: Przegląd dostawców modeli z przykładowymi konfiguracjami i przepływami CLI
title: Dostawcy modeli
x-i18n:
    generated_at: "2026-04-06T03:08:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 15e4b82e07221018a723279d309e245bb4023bc06e64b3c910ef2cae3dfa2599
    source_path: concepts/model-providers.md
    workflow: 15
---

# Dostawcy modeli

Ta strona dotyczy **dostawców LLM/modeli** (a nie kanałów czatu, takich jak WhatsApp/Telegram).
Zasady wyboru modeli znajdziesz w [/concepts/models](/pl/concepts/models).

## Szybkie zasady

- Odwołania do modeli używają formatu `provider/model` (przykład: `opencode/claude-opus-4-6`).
- Jeśli ustawisz `agents.defaults.models`, stanie się to listą dozwolonych modeli.
- Pomocniki CLI: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Zasady awaryjnego działania w runtime, sondy czasu odnowienia i utrwalanie
  nadpisań sesji są udokumentowane w
  [/concepts/model-failover](/pl/concepts/model-failover).
- `models.providers.*.models[].contextWindow` to natywne metadane modelu;
  `models.providers.*.models[].contextTokens` to efektywny limit runtime.
- Pluginy dostawców mogą wstrzykiwać katalogi modeli przez `registerProvider({ catalog })`;
  OpenClaw scala te dane do `models.providers` przed zapisaniem
  `models.json`.
- Manifesty dostawców mogą deklarować `providerAuthEnvVars`, aby ogólne sondy
  uwierzytelniania oparte na zmiennych środowiskowych nie musiały ładować
  runtime pluginu. Pozostała mapa zmiennych środowiskowych w rdzeniu dotyczy
  teraz tylko dostawców niebędących pluginami / dostawców rdzeniowych oraz kilku
  przypadków ogólnego pierwszeństwa, takich jak wdrożenie Anthropic z
  priorytetem klucza API.
- Pluginy dostawców mogą też zarządzać zachowaniem runtime dostawcy przez
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
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot` oraz
  `onModelSelected`.
- Uwaga: runtime `capabilities` dostawcy to współdzielone metadane runnera (rodzina dostawcy,
  niuanse transkrypcji/narzędzi, wskazówki transportu/cache). To nie jest to
  samo co [publiczny model capabilities](/pl/plugins/architecture#public-capability-model),
  który opisuje, co rejestruje plugin (wnioskowanie tekstowe, mowa itd.).

## Zachowanie dostawcy zarządzane przez plugin

Pluginy dostawców mogą teraz zarządzać większością logiki specyficznej dla dostawcy, podczas gdy OpenClaw zachowuje
ogólną pętlę wnioskowania.

Typowy podział:

- `auth[].run` / `auth[].runNonInteractive`: dostawca zarządza przepływami
  wdrożenia/logowania dla `openclaw onboard`, `openclaw models auth` oraz konfiguracji bez interfejsu
- `wizard.setup` / `wizard.modelPicker`: dostawca zarządza etykietami wyboru uwierzytelniania,
  aliasami legacy, wskazówkami listy dozwolonych podczas wdrożenia oraz wpisami konfiguracji w selektorach wdrożenia/modeli
- `catalog`: dostawca pojawia się w `models.providers`
- `normalizeModelId`: dostawca normalizuje identyfikatory modeli legacy/podglądowych przed
  wyszukaniem lub kanonizacją
- `normalizeTransport`: dostawca normalizuje rodzinę transportu `api` / `baseUrl`
  przed ogólnym składaniem modelu; OpenClaw najpierw sprawdza dopasowanego dostawcę,
  a potem inne pluginy dostawców obsługujące hooki, aż któryś faktycznie zmieni
  transport
- `normalizeConfig`: dostawca normalizuje konfigurację `models.providers.<id>` przed
  użyciem przez runtime; OpenClaw najpierw sprawdza dopasowanego dostawcę, a potem inne
  pluginy dostawców obsługujące hooki, aż któryś faktycznie zmieni konfigurację. Jeśli żaden
  hook dostawcy nie przepisze konfiguracji, dołączone helpery rodziny Google nadal
  normalizują obsługiwane wpisy dostawców Google.
- `applyNativeStreamingUsageCompat`: dostawca stosuje przepisania zgodności natywnego użycia przesyłania strumieniowego sterowane przez endpoint dla dostawców konfiguracyjnych
- `resolveConfigApiKey`: dostawca rozwiązuje uwierzytelnianie typu env-marker dla dostawców konfiguracyjnych
  bez wymuszania pełnego ładowania runtime uwierzytelniania. `amazon-bedrock` ma tu też
  wbudowany resolver env-markerów AWS, mimo że uwierzytelnianie runtime Bedrock używa
  domyślnego łańcucha AWS SDK.
- `resolveSyntheticAuth`: dostawca może ujawniać dostępność uwierzytelniania
  lokalnego/self-hosted lub innego opartego na konfiguracji bez utrwalania jawnych sekretów
- `shouldDeferSyntheticProfileAuth`: dostawca może oznaczać zapisane syntetyczne placeholdery profili
  jako mające niższy priorytet niż uwierzytelnianie oparte na env/konfiguracji
- `resolveDynamicModel`: dostawca akceptuje identyfikatory modeli, których nie ma jeszcze w lokalnym
  statycznym katalogu
- `prepareDynamicModel`: dostawca wymaga odświeżenia metadanych przed ponowną próbą
  dynamicznego rozpoznania
- `normalizeResolvedModel`: dostawca wymaga przepisania transportu lub base URL
- `contributeResolvedModelCompat`: dostawca wnosi flagi zgodności dla swoich
  modeli dostawcy nawet wtedy, gdy docierają przez inny zgodny transport
- `capabilities`: dostawca publikuje niuanse transkrypcji/narzędzi/rodziny dostawcy
- `normalizeToolSchemas`: dostawca czyści schematy narzędzi, zanim zobaczy je
  osadzony runner
- `inspectToolSchemas`: dostawca ujawnia ostrzeżenia o schematach specyficznych dla transportu
  po normalizacji
- `resolveReasoningOutputMode`: dostawca wybiera natywne vs oznaczone
  kontrakty wyjścia reasoning
- `prepareExtraParams`: dostawca ustawia domyślne wartości lub normalizuje parametry żądań dla danego modelu
- `createStreamFn`: dostawca zastępuje normalną ścieżkę strumienia w pełni
  niestandardowym transportem
- `wrapStreamFn`: dostawca stosuje opakowania zgodności żądań nagłówków/ciała/modelu
- `resolveTransportTurnState`: dostawca dostarcza natywne nagłówki transportu
  lub metadane dla każdej tury
- `resolveWebSocketSessionPolicy`: dostawca dostarcza natywne nagłówki sesji WebSocket
  lub politykę czasu odnowienia sesji
- `createEmbeddingProvider`: dostawca zarządza zachowaniem embeddingów pamięci, gdy
  powinno ono należeć do pluginu dostawcy zamiast do rdzeniowego przełącznika embeddingów
- `formatApiKey`: dostawca formatuje zapisane profile uwierzytelniania do
  ciągu `apiKey` oczekiwanego przez runtime
- `refreshOAuth`: dostawca zarządza odświeżaniem OAuth, gdy współdzielone mechanizmy odświeżania `pi-ai`
  nie wystarczają
- `buildAuthDoctorHint`: dostawca dopisuje wskazówki naprawy, gdy odświeżanie OAuth
  się nie powiedzie
- `matchesContextOverflowError`: dostawca rozpoznaje błędy przepełnienia
  okna kontekstu specyficzne dla dostawcy, których ogólna heurystyka by nie wykryła
- `classifyFailoverReason`: dostawca mapuje surowe błędy transportu/API specyficzne dla dostawcy
  do powodów failover, takich jak limit szybkości lub przeciążenie
- `isCacheTtlEligible`: dostawca decyduje, które identyfikatory modeli upstream obsługują TTL cache promptów
- `buildMissingAuthMessage`: dostawca zastępuje ogólny błąd magazynu uwierzytelniania
  wskazówką odzyskiwania specyficzną dla dostawcy
- `suppressBuiltInModel`: dostawca ukrywa przestarzałe wiersze upstream i może zwrócić
  błąd zarządzany przez dostawcę dla bezpośrednich niepowodzeń rozpoznania
- `augmentModelCatalog`: dostawca dopisuje syntetyczne/końcowe wiersze katalogu po
  wykryciu i scaleniu konfiguracji
- `isBinaryThinking`: dostawca zarządza interfejsem włącz/wyłącz dla thinking
- `supportsXHighThinking`: dostawca dopuszcza wybrane modele do `xhigh`
- `resolveDefaultThinkingLevel`: dostawca zarządza domyślną polityką `/think` dla
  rodziny modeli
- `applyConfigDefaults`: dostawca stosuje globalne domyślne wartości specyficzne dla dostawcy
  podczas materializacji konfiguracji na podstawie trybu uwierzytelniania, env lub rodziny modeli
- `isModernModelRef`: dostawca zarządza dopasowaniem preferowanych modeli live/smoke
- `prepareRuntimeAuth`: dostawca zamienia skonfigurowane poświadczenie na krótkożyciowy
  token runtime
- `resolveUsageAuth`: dostawca rozwiązuje poświadczenia użycia/limitu dla `/usage`
  i powiązanych powierzchni statusu/raportowania
- `fetchUsageSnapshot`: dostawca zarządza pobraniem/parsowaniem endpointu użycia, podczas gdy
  rdzeń nadal odpowiada za powłokę podsumowania i formatowanie
- `onModelSelected`: dostawca uruchamia skutki uboczne po wyborze modelu, takie jak
  telemetria lub księgowanie sesji zarządzane przez dostawcę

Aktualne dołączone przykłady:

- `anthropic`: fallback zgodny do przodu dla Claude 4.6, wskazówki naprawy uwierzytelniania, pobieranie
  endpointu użycia, metadane cache-TTL/rodziny dostawcy oraz globalne
  domyślne wartości konfiguracji zależne od uwierzytelniania
- `amazon-bedrock`: zarządzane przez dostawcę dopasowanie przepełnienia kontekstu i klasyfikacja
  powodów failover dla błędów Bedrock specyficznych dla throttlingu / gotowości, plus
  współdzielona rodzina replay `anthropic-by-model` dla reguł ochrony polityki replay wyłącznie dla Claude
  na ruchu Anthropic
- `anthropic-vertex`: reguły ochrony polityki replay wyłącznie dla Claude na ruchu
  Anthropic-message
- `openrouter`: identyfikatory modeli pass-through, opakowania żądań, wskazówki capabilities dostawcy,
  sanityzacja sygnatur thought Gemini na ruchu proxy Gemini, wstrzykiwanie reasoning proxy przez rodzinę strumieni
  `openrouter-thinking`, przekazywanie metadanych routingu oraz polityka cache-TTL
- `github-copilot`: wdrożenie/logowanie urządzenia, fallback modeli zgodny do przodu,
  wskazówki transkrypcji Claude-thinking, wymiana tokenów runtime oraz pobieranie
  endpointu użycia
- `openai`: fallback zgodny do przodu dla GPT-5.4, bezpośrednia normalizacja transportu OpenAI,
  wskazówki brakującego uwierzytelniania świadome Codex, ukrywanie Spark, syntetyczne
  wiersze katalogu OpenAI/Codex, polityka thinking/live-model, normalizacja aliasów tokenów użycia
  (`input` / `output` oraz rodziny `prompt` / `completion`), współdzielona rodzina strumieni
  `openai-responses-defaults` dla natywnych opakowań OpenAI/Codex, metadane rodziny dostawcy,
  dołączona rejestracja dostawcy generowania obrazów dla `gpt-image-1` oraz dołączona rejestracja dostawcy
  generowania wideo dla `sora-2`
- `google`: fallback zgodny do przodu dla Gemini 3.1, natywna walidacja replay Gemini,
  sanityzacja replay bootstrap, oznaczony tryb wyjścia reasoning,
  dopasowanie nowoczesnych modeli, dołączona rejestracja dostawcy generowania obrazów dla
  modeli Gemini image-preview oraz dołączona rejestracja dostawcy
  generowania wideo dla modeli Veo
- `moonshot`: współdzielony transport, normalizacja ładunku thinking zarządzana przez plugin
- `kilocode`: współdzielony transport, nagłówki żądań zarządzane przez plugin, normalizacja ładunku reasoning,
  sanityzacja sygnatur thought proxy-Gemini oraz polityka cache-TTL
- `zai`: fallback zgodny do przodu dla GLM-5, domyślne `tool_stream`, polityka cache-TTL,
  polityka binary-thinking/live-model oraz użycie auth + pobieranie limitów;
  nieznane identyfikatory `glm-5*` są syntetyzowane z dołączonego szablonu `glm-4.7`
- `xai`: natywna normalizacja transportu Responses, przepisywanie aliasów `/fast` dla
  szybkich wariantów Grok, domyślne `tool_stream`, czyszczenie schematów narzędzi /
  ładunku reasoning specyficzne dla xAI oraz dołączona rejestracja dostawcy
  generowania wideo dla `grok-imagine-video`
- `mistral`: metadane capabilities zarządzane przez plugin
- `opencode` i `opencode-go`: metadane capabilities zarządzane przez plugin oraz
  sanityzacja sygnatur thought proxy-Gemini
- `alibaba`: katalog generowania wideo zarządzany przez plugin dla bezpośrednich odwołań do modeli Wan,
  takich jak `alibaba/wan2.6-t2v`
- `byteplus`: katalogi zarządzane przez plugin oraz dołączona rejestracja dostawcy generowania wideo
  dla modeli Seedance text-to-video/image-to-video
- `fal`: dołączona rejestracja dostawcy generowania wideo dla hostowanych modeli wideo innych firm
  oraz rejestracja dostawcy generowania obrazów dla modeli FLUX plus dołączona
  rejestracja dostawcy generowania wideo dla hostowanych modeli wideo innych firm
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway` i `volcengine`:
  tylko katalogi zarządzane przez plugin
- `qwen`: katalogi modeli tekstowych zarządzane przez plugin oraz współdzielone
  rejestracje dostawców media-understanding i generowania wideo dla jego
  powierzchni multimodalnych; generowanie wideo Qwen używa standardowych endpointów wideo DashScope
  z dołączonymi modelami Wan, takimi jak `wan2.6-t2v` i `wan2.7-r2v`
- `runway`: rejestracja dostawcy generowania wideo zarządzana przez plugin dla natywnych
  modeli opartych na zadaniach Runway, takich jak `gen4.5`
- `minimax`: katalogi zarządzane przez plugin, dołączona rejestracja dostawcy generowania wideo
  dla modeli wideo Hailuo, dołączona rejestracja dostawcy generowania obrazów
  dla `image-01`, hybrydowy wybór polityki replay Anthropic/OpenAI oraz
  logika użycia auth/snapshot
- `together`: katalogi zarządzane przez plugin oraz dołączona rejestracja dostawcy generowania wideo
  dla modeli wideo Wan
- `xiaomi`: katalogi zarządzane przez plugin oraz logika użycia auth/snapshot

Dołączony plugin `openai` zarządza teraz oboma identyfikatorami dostawcy: `openai` i
`openai-codex`.

To obejmuje dostawców, którzy nadal mieszczą się w normalnych transportach OpenClaw. Dostawca,
który wymaga całkowicie niestandardowego wykonawcy żądań, to osobna, głębsza
powierzchnia rozszerzeń.

## Rotacja kluczy API

- Obsługuje ogólną rotację dostawców dla wybranych dostawców.
- Skonfiguruj wiele kluczy przez:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (pojedyncze nadpisanie live, najwyższy priorytet)
  - `<PROVIDER>_API_KEYS` (lista rozdzielona przecinkami lub średnikami)
  - `<PROVIDER>_API_KEY` (klucz główny)
  - `<PROVIDER>_API_KEY_*` (lista numerowana, np. `<PROVIDER>_API_KEY_1`)
- Dla dostawców Google `GOOGLE_API_KEY` jest również uwzględniany jako fallback.
- Kolejność wyboru kluczy zachowuje priorytet i usuwa duplikaty wartości.
- Żądania są ponawiane z następnym kluczem tylko przy odpowiedziach z limitem szybkości (na
  przykład `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded` lub okresowych komunikatach o limicie użycia).
- Błędy niezwiązane z limitem szybkości kończą się natychmiast niepowodzeniem; rotacja kluczy nie jest podejmowana.
- Gdy wszystkie klucze kandydackie zawiodą, zwracany jest ostatni błąd z ostatniej próby.

## Wbudowani dostawcy (katalog pi-ai)

OpenClaw jest dostarczany z katalogiem pi‑ai. Ci dostawcy nie wymagają
konfiguracji `models.providers`; wystarczy ustawić uwierzytelnianie i wybrać model.

### OpenAI

- Dostawca: `openai`
- Uwierzytelnianie: `OPENAI_API_KEY`
- Opcjonalna rotacja: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, plus `OPENCLAW_LIVE_OPENAI_KEY` (pojedyncze nadpisanie)
- Przykładowe modele: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- Domyślny transport to `auto` (najpierw WebSocket, fallback do SSE)
- Nadpisanie dla modelu przez `agents.defaults.models["openai/<model>"].params.transport` (`"sse"`, `"websocket"` lub `"auto"`)
- Rozgrzewanie OpenAI Responses WebSocket jest domyślnie włączone przez `params.openaiWsWarmup` (`true`/`false`)
- Przetwarzanie priorytetowe OpenAI można włączyć przez `agents.defaults.models["openai/<model>"].params.serviceTier`
- `/fast` i `params.fastMode` mapują bezpośrednie żądania Responses `openai/*` do `service_tier=priority` na `api.openai.com`
- Użyj `params.serviceTier`, jeśli chcesz jawnie ustawić poziom zamiast współdzielonego przełącznika `/fast`
- Ukryte nagłówki atrybucji OpenClaw (`originator`, `version`,
  `User-Agent`) są stosowane tylko do natywnego ruchu OpenAI do `api.openai.com`, a nie
  do ogólnych proxy zgodnych z OpenAI
- Natywne trasy OpenAI zachowują również `store` dla Responses, wskazówki cache promptów oraz
  formatowanie ładunku zgodności reasoning OpenAI; trasy proxy tego nie robią
- `openai/gpt-5.3-codex-spark` jest celowo ukryty w OpenClaw, ponieważ aktywne API OpenAI go odrzuca; Spark jest traktowany jako wyłącznie Codex

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Dostawca: `anthropic`
- Uwierzytelnianie: `ANTHROPIC_API_KEY`
- Opcjonalna rotacja: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, plus `OPENCLAW_LIVE_ANTHROPIC_KEY` (pojedyncze nadpisanie)
- Przykładowy model: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- Bezpośrednie publiczne żądania Anthropic obsługują także współdzielony przełącznik `/fast` i `params.fastMode`, w tym ruch uwierzytelniony kluczem API i OAuth wysyłany do `api.anthropic.com`; OpenClaw mapuje to do Anthropic `service_tier` (`auto` vs `standard_only`)
- Uwaga rozliczeniowa: dla Anthropic w OpenClaw praktyczny podział to **klucz API** albo **subskrypcja Claude z Extra Usage**. Anthropic poinformował użytkowników OpenClaw **4 kwietnia 2026 o 12:00 PT / 20:00 BST**, że ścieżka logowania Claude w **OpenClaw** liczy się jako użycie zewnętrznego harnessa i wymaga **Extra Usage** rozliczanego osobno od subskrypcji. Nasze lokalne reprodukcje pokazują również, że ciąg promptu identyfikujący OpenClaw nie odtwarza się na ścieżce Anthropic SDK + klucz API.
- Token konfiguracji Anthropic jest ponownie dostępny jako legacy/ręczna ścieżka OpenClaw. Używaj go z założeniem, że Anthropic poinformował użytkowników OpenClaw, że ta ścieżka wymaga **Extra Usage**.

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
- Nadpisanie dla modelu przez `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"`, `"websocket"` lub `"auto"`)
- `params.serviceTier` jest również przekazywane w natywnych żądaniach Codex Responses (`chatgpt.com/backend-api`)
- Ukryte nagłówki atrybucji OpenClaw (`originator`, `version`,
  `User-Agent`) są dołączane tylko do natywnego ruchu Codex do
  `chatgpt.com/backend-api`, a nie do ogólnych proxy zgodnych z OpenAI
- Współdzieli ten sam przełącznik `/fast` i konfigurację `params.fastMode`, co bezpośrednie `openai/*`; OpenClaw mapuje to na `service_tier=priority`
- `openai-codex/gpt-5.3-codex-spark` pozostaje dostępny, gdy katalog OAuth Codex go ujawnia; zależy od uprawnień
- `openai-codex/gpt-5.4` zachowuje natywne `contextWindow = 1050000` i domyślne runtime `contextTokens = 272000`; nadpisz limit runtime przez `models.providers.openai-codex.models[].contextTokens`
- Uwaga dotycząca polityki: OpenAI Codex OAuth jest jawnie wspierany dla zewnętrznych narzędzi/przepływów pracy, takich jak OpenClaw.

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
- [MiniMax](/pl/providers/minimax): dostęp OAuth lub przez klucz API w planie MiniMax Coding
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
  (lub legacy `cached_content`) do przekazania natywnego dla dostawcy
  uchwytu `cachedContents/...`; trafienia cache Gemini są ujawniane jako OpenClaw `cacheRead`

### Google Vertex

- Dostawca: `google-vertex`
- Uwierzytelnianie: gcloud ADC
  - Odpowiedzi JSON z Gemini CLI są parsowane z `response`; użycie przechodzi awaryjnie do
    `stats`, przy czym `stats.cached` jest normalizowane do OpenClaw `cacheRead`.

### Z.AI (GLM)

- Dostawca: `zai`
- Uwierzytelnianie: `ZAI_API_KEY`
- Przykładowy model: `zai/glm-5`
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
- Base URL: `https://api.kilo.ai/api/gateway/`
- Statyczny katalog awaryjny zawiera `kilocode/kilo/auto`; aktywne
  wykrywanie `https://api.kilo.ai/api/gateway/models` może dalej rozszerzać katalog
  runtime.
- Dokładny routing upstream za `kilocode/kilo/auto` należy do Kilo Gateway
  i nie jest zakodowany na stałe w OpenClaw.

Szczegóły konfiguracji znajdziesz w [/providers/kilocode](/pl/providers/kilocode).

### Inne dołączone pluginy dostawców

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- Przykładowy model: `openrouter/auto`
- OpenClaw stosuje udokumentowane nagłówki atrybucji aplikacji OpenRouter tylko wtedy, gdy
  żądanie rzeczywiście trafia do `openrouter.ai`
- Znaczniki `cache_control` specyficzne dla OpenRouter Anthropic są podobnie ograniczone do
  zweryfikowanych tras OpenRouter, a nie dowolnych adresów proxy
- OpenRouter pozostaje na ścieżce proxy w stylu zgodnym z OpenAI, więc natywne formatowanie żądań wyłącznie dla OpenAI (`serviceTier`, `store` dla Responses,
  wskazówki cache promptów, ładunki zgodności reasoning OpenAI) nie jest przekazywane
- Odwołania OpenRouter oparte na Gemini zachowują tylko sanityzację sygnatur thought proxy-Gemini;
  natywna walidacja replay Gemini i przepisywanie bootstrap pozostają wyłączone
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- Przykładowy model: `kilocode/kilo/auto`
- Odwołania Kilo oparte na Gemini zachowują tę samą ścieżkę sanityzacji sygnatur thought
  proxy-Gemini; `kilocode/kilo/auto` i inne wskazówki proxy bez obsługi reasoning
  pomijają wstrzykiwanie reasoning proxy
- MiniMax: `minimax` (klucz API) i `minimax-portal` (OAuth)
- Uwierzytelnianie: `MINIMAX_API_KEY` dla `minimax`; `MINIMAX_OAUTH_TOKEN` lub `MINIMAX_API_KEY` dla `minimax-portal`
- Przykładowy model: `minimax/MiniMax-M2.7` lub `minimax-portal/MiniMax-M2.7`
- Wdrożenie MiniMax / konfiguracja klucza API zapisuje jawne definicje modeli M2.7 z
  `input: ["text", "image"]`; dołączony katalog dostawcy utrzymuje odwołania czatu jako
  tylko tekstowe, dopóki konfiguracja dostawcy nie zostanie zmaterializowana
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
  - `/fast` lub `params.fastMode: true` przepisuje `grok-3`, `grok-3-mini`,
    `grok-4` i `grok-4-0709` na ich warianty `*-fast`
  - `tool_stream` jest domyślnie włączone; ustaw
    `agents.defaults.models["xai/<model>"].params.tool_stream` na `false`, aby
    je wyłączyć
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- Przykładowy model: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - Modele GLM w Cerebras używają identyfikatorów `zai-glm-4.7` i `zai-glm-4.6`.
  - Base URL zgodny z OpenAI: `https://api.cerebras.ai/v1`.
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Przykładowy model Hugging Face Inference: `huggingface/deepseek-ai/DeepSeek-R1`; CLI: `openclaw onboard --auth-choice huggingface-api-key`. Zobacz [Hugging Face (Inference)](/pl/providers/huggingface).

## Dostawcy przez `models.providers` (custom/base URL)

Użyj `models.providers` (lub `models.json`), aby dodać **niestandardowych** dostawców lub
proxy zgodne z OpenAI/Anthropic.

Wiele z poniższych dołączonych pluginów dostawców publikuje już domyślny katalog.
Używaj jawnych wpisów `models.providers.<id>` tylko wtedy, gdy chcesz nadpisać
domyślny base URL, nagłówki lub listę modeli.

### Moonshot AI (Kimi)

Moonshot jest dostarczany jako dołączony plugin dostawcy. Domyślnie używaj
wbudowanego dostawcy, a jawny wpis `models.providers.moonshot` dodawaj tylko wtedy, gdy
musisz nadpisać base URL lub metadane modelu:

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

Kimi Coding używa endpointu zgodnego z Anthropic od Moonshot AI:

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

Starszy `kimi/k2p5` nadal jest akceptowany jako identyfikator modelu zgodności.

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

Wdrożenie domyślnie używa powierzchni coding, ale ogólny katalog `volcengine/*`
jest rejestrowany w tym samym czasie.

W selektorach modeli wdrożenia/konfiguracji wybór uwierzytelniania Volcengine
preferuje zarówno wiersze `volcengine/*`, jak i `volcengine-plan/*`. Jeśli te modele nie są jeszcze załadowane,
OpenClaw przechodzi awaryjnie do nieprzefiltrowanego katalogu zamiast pokazywać pusty
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

BytePlus ARK zapewnia użytkownikom międzynarodowym dostęp do tych samych modeli co Volcano Engine.

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

Wdrożenie domyślnie używa powierzchni coding, ale ogólny katalog `byteplus/*`
jest rejestrowany w tym samym czasie.

W selektorach modeli wdrożenia/konfiguracji wybór uwierzytelniania BytePlus
preferuje zarówno wiersze `byteplus/*`, jak i `byteplus-plan/*`. Jeśli te modele nie są jeszcze załadowane,
OpenClaw przechodzi awaryjnie do nieprzefiltrowanego katalogu zamiast pokazywać pusty
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

Synthetic udostępnia modele zgodne z Anthropic za dostawcą `synthetic`:

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

Na ścieżce strumieniowania zgodnej z Anthropic w MiniMax OpenClaw domyślnie wyłącza thinking,
chyba że jawnie go ustawisz, a `/fast on` przepisuje
`MiniMax-M2.7` na `MiniMax-M2.7-highspeed`.

Podział capabilities zarządzany przez plugin:

- Domyślne tekst/czat pozostają na `minimax/MiniMax-M2.7`
- Generowanie obrazów to `minimax/image-01` lub `minimax-portal/image-01`
- Rozumienie obrazów to zarządzany przez plugin `MiniMax-VL-01` na obu ścieżkach uwierzytelniania MiniMax
- Wyszukiwanie w sieci pozostaje na identyfikatorze dostawcy `minimax`

### Ollama

Ollama jest dostarczany jako dołączony plugin dostawcy i używa natywnego API Ollama:

- Dostawca: `ollama`
- Uwierzytelnianie: nie jest wymagane (serwer lokalny)
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

Ollama jest wykrywany lokalnie pod adresem `http://127.0.0.1:11434`, gdy zdecydujesz się
na opt-in przez `OLLAMA_API_KEY`, a dołączony plugin dostawcy dodaje Ollama bezpośrednio do
`openclaw onboard` i selektora modeli. Zobacz [/providers/ollama](/pl/providers/ollama),
aby poznać wdrożenie, tryb cloud/local i konfigurację niestandardową.

### vLLM

vLLM jest dostarczany jako dołączony plugin dostawcy dla lokalnych / self-hosted serwerów
zgodnych z OpenAI:

- Dostawca: `vllm`
- Uwierzytelnianie: opcjonalne (zależy od Twojego serwera)
- Domyślny base URL: `http://127.0.0.1:8000/v1`

Aby włączyć lokalne auto-wykrywanie (dowolna wartość działa, jeśli Twój serwer nie wymusza uwierzytelniania):

```bash
export VLLM_API_KEY="vllm-local"
```

Następnie ustaw model (zamień na jeden z identyfikatorów zwróconych przez `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

Szczegóły znajdziesz w [/providers/vllm](/pl/providers/vllm).

### SGLang

SGLang jest dostarczany jako dołączony plugin dostawcy dla szybkich serwerów self-hosted
zgodnych z OpenAI:

- Dostawca: `sglang`
- Uwierzytelnianie: opcjonalne (zależy od Twojego serwera)
- Domyślny base URL: `http://127.0.0.1:30000/v1`

Aby włączyć lokalne auto-wykrywanie (dowolna wartość działa, jeśli Twój serwer nie
wymusza uwierzytelniania):

```bash
export SGLANG_API_KEY="sglang-local"
```

Następnie ustaw model (zamień na jeden z identyfikatorów zwróconych przez `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

Szczegóły znajdziesz w [/providers/sglang](/pl/providers/sglang).

### Lokalne proxy (LM Studio, vLLM, LiteLLM itd.)

Przykład (zgodny z OpenAI):

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Local" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "LMSTUDIO_KEY",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
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

- Dla dostawców custom `reasoning`, `input`, `cost`, `contextWindow` i `maxTokens` są opcjonalne.
  Po pominięciu OpenClaw przyjmuje domyślnie:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- Zalecenie: ustaw jawne wartości zgodne z limitami Twojego proxy/modelu.
- Dla `api: "openai-completions"` na nienatywnych endpointach (dowolny niepusty `baseUrl`, którego host nie jest `api.openai.com`) OpenClaw wymusza `compat.supportsDeveloperRole: false`, aby uniknąć błędów 400 od dostawcy dla nieobsługiwanych ról `developer`.
- Trasy proxy zgodne z OpenAI również pomijają natywne formatowanie żądań wyłącznie dla OpenAI: brak `service_tier`, brak `store` dla Responses, brak wskazówek cache promptów, brak
  formatowania ładunku zgodności reasoning OpenAI i brak ukrytych nagłówków
  atrybucji OpenClaw.
- Jeśli `baseUrl` jest pusty lub pominięty, OpenClaw zachowuje domyślne zachowanie OpenAI (które wskazuje na `api.openai.com`).
- Dla bezpieczeństwa jawne `compat.supportsDeveloperRole: true` nadal jest nadpisywane na nienatywnych endpointach `openai-completions`.

## Przykłady CLI

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

Zobacz też: [/gateway/configuration](/pl/gateway/configuration), aby zobaczyć pełne przykłady konfiguracji.

## Powiązane

- [Modele](/pl/concepts/models) — konfiguracja modeli i aliasy
- [Failover modeli](/pl/concepts/model-failover) — łańcuchy fallback i zachowanie ponawiania
- [Dokumentacja konfiguracji](/pl/gateway/configuration-reference#agent-defaults) — klucze konfiguracji modeli
- [Dostawcy](/pl/providers) — przewodniki konfiguracji dla poszczególnych dostawców
