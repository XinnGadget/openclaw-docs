---
read_when:
    - Widzisz ostrzeżenie OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Widzisz ostrzeżenie OPENCLAW_EXTENSION_API_DEPRECATED
    - Aktualizujesz plugin do nowoczesnej architektury pluginów OpenClaw
    - Utrzymujesz zewnętrzny plugin OpenClaw
sidebarTitle: Migrate to SDK
summary: Migracja ze starszej warstwy zgodności wstecznej do nowoczesnego Plugin SDK
title: Migracja Plugin SDK
x-i18n:
    generated_at: "2026-04-06T03:10:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: b71ce69b30c3bb02da1b263b1d11dc3214deae5f6fc708515e23b5a1c7bb7c8f
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Migracja Plugin SDK

OpenClaw przeszedł od szerokiej warstwy zgodności wstecznej do nowoczesnej
architektury pluginów z ukierunkowanymi, udokumentowanymi importami. Jeśli Twój plugin został zbudowany przed
wprowadzeniem nowej architektury, ten przewodnik pomoże Ci przeprowadzić migrację.

## Co się zmienia

Stary system pluginów udostępniał dwie szerokie powierzchnie, które pozwalały pluginom importować
wszystko, czego potrzebowały, z jednego punktu wejścia:

- **`openclaw/plugin-sdk/compat`** — pojedynczy import, który re-eksportował dziesiątki
  helperów. Został wprowadzony, aby utrzymać działanie starszych pluginów opartych na hookach, podczas gdy
  budowano nową architekturę pluginów.
- **`openclaw/extension-api`** — most, który dawał pluginom bezpośredni dostęp do
  helperów po stronie hosta, takich jak osadzony runner agenta.

Obie powierzchnie są teraz **przestarzałe**. Nadal działają w runtime, ale nowe
pluginy nie mogą ich używać, a istniejące pluginy powinny przeprowadzić migrację przed kolejnym
dużym wydaniem, które je usunie.

<Warning>
  Warstwa zgodności wstecznej zostanie usunięta w jednym z przyszłych dużych wydań.
  Pluginy, które nadal importują z tych powierzchni, przestaną działać, gdy to nastąpi.
</Warning>

## Dlaczego to się zmieniło

Stare podejście powodowało problemy:

- **Powolny start** — zaimportowanie jednego helpera ładowało dziesiątki niepowiązanych modułów
- **Zależności cykliczne** — szerokie re-eksporty ułatwiały tworzenie cykli importów
- **Niejasna powierzchnia API** — nie było sposobu, aby rozróżnić, które eksporty są stabilne, a które wewnętrzne

Nowoczesne Plugin SDK to naprawia: każda ścieżka importu (`openclaw/plugin-sdk/\<subpath\>`)
jest małym, samodzielnym modułem z jasnym przeznaczeniem i udokumentowanym kontraktem.

Starsze wygodne powierzchnie providerów dla wbudowanych kanałów również zniknęły. Importy
takie jak `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
powierzchnie helperów oznaczone marką kanału oraz
`openclaw/plugin-sdk/telegram-core` były prywatnymi skrótami mono-repo, a nie
stabilnymi kontraktami pluginów. Zamiast tego używaj wąskich, ogólnych subpath Plugin SDK. Wewnątrz
workspace wbudowanych pluginów trzymaj helpery należące do providera we własnym
`api.ts` lub `runtime-api.ts` tego pluginu.

Bieżące przykłady wbudowanych providerów:

- Anthropic trzyma helpery strumieni specyficzne dla Claude we własnej powierzchni `api.ts` /
  `contract-api.ts`
- OpenAI trzyma konstruktory providerów, helpery modeli domyślnych i konstruktory providerów realtime
  we własnym `api.ts`
- OpenRouter trzyma konstruktor providera oraz helpery onboardingowe/konfiguracyjne
  we własnym `api.ts`

## Jak przeprowadzić migrację

<Steps>
  <Step title="Przeprowadź audyt zachowania fallbacku wrappera Windows">
    Jeśli Twój plugin używa `openclaw/plugin-sdk/windows-spawn`, nierozwiązane wrappery Windows
    `.cmd`/`.bat` teraz blokują się domyślnie, chyba że jawnie przekażesz
    `allowShellFallback: true`.

    ```typescript
    // Before
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // After
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Only set this for trusted compatibility callers that intentionally
      // accept shell-mediated fallback.
      allowShellFallback: true,
    });
    ```

    Jeśli wywołanie nie polega celowo na fallbacku powłoki, nie ustawiaj
    `allowShellFallback`; zamiast tego obsłuż zgłaszany błąd.

  </Step>

  <Step title="Znajdź przestarzałe importy">
    Wyszukaj w swoim pluginie importy z którejkolwiek z przestarzałych powierzchni:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Zastąp je ukierunkowanymi importami">
    Każdy eksport ze starej powierzchni odpowiada konkretnej nowoczesnej ścieżce importu:

    ```typescript
    // Before (deprecated backwards-compatibility layer)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // After (modern focused imports)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    W przypadku helperów po stronie hosta używaj wstrzykniętego runtime pluginu zamiast importować
    je bezpośrednio:

    ```typescript
    // Before (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After (injected runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Ten sam wzorzec dotyczy innych starszych helperów mostu:

    | Old import | Modern equivalent |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | session store helpers | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Zbuduj i przetestuj">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## Dokumentacja ścieżek importu

<Accordion title="Tabela najczęstszych ścieżek importu">
  | Import path | Purpose | Key exports |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Kanoniczny helper punktu wejścia pluginu | `definePluginEntry` |
  | `plugin-sdk/core` | Starszy parasolowy re-eksport definicji/builderów wejścia kanału | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Eksport głównego schematu konfiguracji | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Helper punktu wejścia dla pojedynczego providera | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Ukierunkowane definicje i buildery wejścia kanału | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Współdzielone helpery kreatora konfiguracji | Monity allowlisty, buildery stanu konfiguracji |
  | `plugin-sdk/setup-runtime` | Helpery runtime na potrzeby konfiguracji | Bezpieczne przy imporcie adaptery patch konfiguracji, helpery notatek lookup, `promptResolvedAllowFrom`, `splitSetupEntries`, delegowane proxy konfiguracji |
  | `plugin-sdk/setup-adapter-runtime` | Helpery adaptera konfiguracji | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Helpery narzędzi konfiguracji | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Helpery wielu kont | Helpery listy kont/konfiguracji/bramek działań |
  | `plugin-sdk/account-id` | Helpery identyfikatora konta | `DEFAULT_ACCOUNT_ID`, normalizacja identyfikatora konta |
  | `plugin-sdk/account-resolution` | Helpery wyszukiwania kont | Helpery wyszukiwania kont + domyślnego fallbacku |
  | `plugin-sdk/account-helpers` | Wąskie helpery kont | Helpery listy kont/działań na kontach |
  | `plugin-sdk/channel-setup` | Adaptery kreatora konfiguracji | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, a także `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Prymitywy parowania DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Obsługa prefiksu odpowiedzi + wpisywania | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Fabryki adapterów konfiguracji | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Buildery schematu konfiguracji | Typy schematu konfiguracji kanału |
  | `plugin-sdk/telegram-command-config` | Helpery konfiguracji poleceń Telegram | Normalizacja nazw poleceń, przycinanie opisów, walidacja duplikatów/konfliktów |
  | `plugin-sdk/channel-policy` | Rozwiązywanie zasad grup/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Śledzenie stanu kont | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Helpery kopert przychodzących | Współdzielone helpery routingu + buildera kopert |
  | `plugin-sdk/inbound-reply-dispatch` | Helpery odpowiedzi przychodzących | Współdzielone helpery rejestrowania i dyspozycji |
  | `plugin-sdk/messaging-targets` | Parsowanie celów wiadomości | Helpery parsowania/dopasowywania celów |
  | `plugin-sdk/outbound-media` | Helpery mediów wychodzących | Współdzielone ładowanie mediów wychodzących |
  | `plugin-sdk/outbound-runtime` | Helpery runtime dla wiadomości wychodzących | Helpery tożsamości wychodzącej/delegowania wysyłki |
  | `plugin-sdk/thread-bindings-runtime` | Helpery powiązań wątków | Cykl życia powiązań wątków i helpery adapterów |
  | `plugin-sdk/agent-media-payload` | Starsze helpery payloadu mediów | Builder payloadu mediów agenta dla starszych układów pól |
  | `plugin-sdk/channel-runtime` | Przestarzały shim zgodności | Tylko starsze narzędzia runtime kanałów |
  | `plugin-sdk/channel-send-result` | Typy wyniku wysyłki | Typy wyniku odpowiedzi |
  | `plugin-sdk/runtime-store` | Trwałe przechowywanie pluginu | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Szerokie helpery runtime | Helpery runtime/logowania/kopii zapasowej/instalacji pluginów |
  | `plugin-sdk/runtime-env` | Wąskie helpery środowiska runtime | Logger/środowisko runtime, helpery timeout, retry i backoff |
  | `plugin-sdk/plugin-runtime` | Współdzielone helpery runtime pluginów | Helpery poleceń/hooków/http/interaktywności pluginów |
  | `plugin-sdk/hook-runtime` | Helpery pipeline hooków | Współdzielone helpery pipeline webhooków/wewnętrznych hooków |
  | `plugin-sdk/lazy-runtime` | Helpery lazy runtime | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Helpery procesów | Współdzielone helpery exec |
  | `plugin-sdk/cli-runtime` | Helpery runtime CLI | Formatowanie poleceń, oczekiwanie, helpery wersji |
  | `plugin-sdk/gateway-runtime` | Helpery gatewaya | Klient gatewaya i helpery patch stanu kanałów |
  | `plugin-sdk/config-runtime` | Helpery konfiguracji | Helpery ładowania/zapisu konfiguracji |
  | `plugin-sdk/telegram-command-config` | Helpery poleceń Telegram | Stabilne helpery walidacji poleceń Telegram jako fallback, gdy powierzchnia kontraktu wbudowanego Telegram jest niedostępna |
  | `plugin-sdk/approval-runtime` | Helpery promptów zatwierdzeń | Payload zatwierdzeń exec/pluginów, helpery możliwości/profilu zatwierdzeń, natywne helpery routingu/runtime zatwierdzeń |
  | `plugin-sdk/approval-auth-runtime` | Helpery auth zatwierdzeń | Rozwiązywanie zatwierdzających, auth działań w tym samym czacie |
  | `plugin-sdk/approval-client-runtime` | Helpery klienta zatwierdzeń | Helpery profilu/filtrowania natywnych zatwierdzeń exec |
  | `plugin-sdk/approval-delivery-runtime` | Helpery dostarczania zatwierdzeń | Natywne adaptery możliwości/dostarczania zatwierdzeń |
  | `plugin-sdk/approval-native-runtime` | Helpery celu zatwierdzeń | Helpery celu/powiązania konta dla natywnych zatwierdzeń |
  | `plugin-sdk/approval-reply-runtime` | Helpery odpowiedzi zatwierdzeń | Helpery payloadu odpowiedzi zatwierdzeń exec/pluginów |
  | `plugin-sdk/security-runtime` | Helpery bezpieczeństwa | Współdzielone helpery zaufania, bramkowania DM, treści zewnętrznej i zbierania sekretów |
  | `plugin-sdk/ssrf-policy` | Helpery zasad SSRF | Helpery allowlisty hostów i zasad sieci prywatnych |
  | `plugin-sdk/ssrf-runtime` | Helpery runtime SSRF | Pinned-dispatcher, guarded fetch, helpery zasad SSRF |
  | `plugin-sdk/collection-runtime` | Helpery ograniczonego cache | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Helpery bramkowania diagnostyki | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Helpery formatowania błędów | `formatUncaughtError`, `isApprovalNotFoundError`, helpery grafu błędów |
  | `plugin-sdk/fetch-runtime` | Helpery opakowanego fetch/proxy | `resolveFetch`, helpery proxy |
  | `plugin-sdk/host-runtime` | Helpery normalizacji hosta | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Helpery retry | `RetryConfig`, `retryAsync`, uruchamiacze zasad |
  | `plugin-sdk/allow-from` | Formatowanie allowlisty | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Mapowanie wejścia allowlisty | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Bramkowanie poleceń i helpery powierzchni poleceń | `resolveControlCommandGate`, helpery autoryzacji nadawcy, helpery rejestru poleceń |
  | `plugin-sdk/secret-input` | Parsowanie danych wejściowych sekretów | Helpery danych wejściowych sekretów |
  | `plugin-sdk/webhook-ingress` | Helpery żądań webhooków | Narzędzia celu webhooka |
  | `plugin-sdk/webhook-request-guards` | Helpery strażników body webhooka | Helpery odczytu/limitu body żądania |
  | `plugin-sdk/reply-runtime` | Współdzielony runtime odpowiedzi | Dyspozycja przychodząca, heartbeat, planner odpowiedzi, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Wąskie helpery dyspozycji odpowiedzi | Helpery finalizacji + dyspozycji providera |
  | `plugin-sdk/reply-history` | Helpery historii odpowiedzi | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Planowanie referencji odpowiedzi | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Helpery chunków odpowiedzi | Helpery chunkingu tekstu/markdown |
  | `plugin-sdk/session-store-runtime` | Helpery magazynu sesji | Helpery ścieżek magazynu + updated-at |
  | `plugin-sdk/state-paths` | Helpery ścieżek stanu | Helpery katalogu stanu i OAuth |
  | `plugin-sdk/routing` | Helpery routingu/kluczy sesji | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, helpery normalizacji kluczy sesji |
  | `plugin-sdk/status-helpers` | Helpery stanu kanałów | Buildery podsumowania stanu kanału/konta, domyślne wartości runtime-state, helpery metadanych problemów |
  | `plugin-sdk/target-resolver-runtime` | Helpery rozwiązywania celów | Współdzielone helpery rozwiązywania celów |
  | `plugin-sdk/string-normalization-runtime` | Helpery normalizacji ciągów | Helpery normalizacji slugów/ciągów |
  | `plugin-sdk/request-url` | Helpery URL żądania | Wyodrębnianie URL typu string z wejść podobnych do żądania |
  | `plugin-sdk/run-command` | Helpery poleceń z pomiarem czasu | Uruchamianie poleceń z pomiarem czasu i znormalizowanym stdout/stderr |
  | `plugin-sdk/param-readers` | Odczyt parametrów | Wspólne czytniki parametrów narzędzi/CLI |
  | `plugin-sdk/tool-send` | Wyodrębnianie wysyłki narzędzia | Wyodrębnianie kanonicznych pól celu wysyłki z argumentów narzędzia |
  | `plugin-sdk/temp-path` | Helpery ścieżek tymczasowych | Współdzielone helpery ścieżek tymczasowego pobierania |
  | `plugin-sdk/logging-core` | Helpery logowania | Logger podsystemu i helpery redakcji |
  | `plugin-sdk/markdown-table-runtime` | Helpery tabel markdown | Helpery trybu tabel markdown |
  | `plugin-sdk/reply-payload` | Typy odpowiedzi wiadomości | Typy payloadu odpowiedzi |
  | `plugin-sdk/provider-setup` | Kuratorowane helpery konfiguracji providerów lokalnych/self-hosted | Helpery wykrywania/konfiguracji providerów self-hosted |
  | `plugin-sdk/self-hosted-provider-setup` | Ukierunkowane helpery konfiguracji providerów self-hosted zgodnych z OpenAI | Te same helpery wykrywania/konfiguracji providerów self-hosted |
  | `plugin-sdk/provider-auth-runtime` | Helpery auth providera w runtime | Helpery rozwiązywania klucza API w runtime |
  | `plugin-sdk/provider-auth-api-key` | Helpery konfiguracji klucza API providera | Helpery onboardingu/zapisu profilu klucza API |
  | `plugin-sdk/provider-auth-result` | Helpery wyniku auth providera | Standardowy builder wyniku auth OAuth |
  | `plugin-sdk/provider-auth-login` | Helpery interaktywnego logowania providera | Współdzielone helpery interaktywnego logowania |
  | `plugin-sdk/provider-env-vars` | Helpery zmiennych środowiskowych providera | Helpery wyszukiwania zmiennych środowiskowych auth providera |
  | `plugin-sdk/provider-model-shared` | Współdzielone helpery modeli/replay providera | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, współdzielone buildery zasad replay, helpery endpointów providera oraz helpery normalizacji identyfikatora modelu |
  | `plugin-sdk/provider-catalog-shared` | Współdzielone helpery katalogu providera | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Patche onboardingu providera | Helpery konfiguracji onboardingu |
  | `plugin-sdk/provider-http` | Helpery HTTP providera | Ogólne helpery HTTP/endpoint/capability providera |
  | `plugin-sdk/provider-web-fetch` | Helpery web-fetch providera | Helpery rejestracji/cache providera web-fetch |
  | `plugin-sdk/provider-web-search` | Helpery web-search providera | Helpery rejestracji/cache/konfiguracji providera web-search |
  | `plugin-sdk/provider-tools` | Helpery zgodności narzędzi/schematów providera | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, czyszczenie schematu Gemini + diagnostyka oraz helpery zgodności xAI, takie jak `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Helpery użycia providera | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` i inne helpery użycia providera |
  | `plugin-sdk/provider-stream` | Helpery wrapperów strumieni providera | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, typy wrapperów strumieni oraz współdzielone helpery wrapperów Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Uporządkowana kolejka async | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Współdzielone helpery mediów | Helpery pobierania/przekształcania/przechowywania mediów oraz buildery payloadów mediów |
  | `plugin-sdk/media-understanding` | Helpery media-understanding | Typy providerów media understanding oraz eksporty helperów obraz/audio dla providerów |
  | `plugin-sdk/text-runtime` | Współdzielone helpery tekstu | Usuwanie tekstu widocznego dla asystenta, helpery renderowania/chunkingu/tabel markdown, helpery redakcji, helpery tagów dyrektyw, narzędzia bezpiecznego tekstu i powiązane helpery tekstu/logowania |
  | `plugin-sdk/text-chunking` | Helpery chunkingu tekstu | Helper chunkingu tekstu wychodzącego |
  | `plugin-sdk/speech` | Helpery speech | Typy providerów speech oraz eksporty helperów dyrektyw, rejestru i walidacji dla providerów |
  | `plugin-sdk/speech-core` | Współdzielony rdzeń speech | Typy providerów speech, rejestr, dyrektywy, normalizacja |
  | `plugin-sdk/realtime-transcription` | Helpery realtime transcription | Typy providerów i helpery rejestru |
  | `plugin-sdk/realtime-voice` | Helpery realtime voice | Typy providerów i helpery rejestru |
  | `plugin-sdk/image-generation-core` | Współdzielony rdzeń image generation | Typy image generation, failover, auth i helpery rejestru |
  | `plugin-sdk/music-generation` | Helpery music generation | Typy providerów/żądań/wyników music generation |
  | `plugin-sdk/music-generation-core` | Współdzielony rdzeń music generation | Typy music generation, helpery failover, wyszukiwanie providera i parsowanie odwołań do modeli |
  | `plugin-sdk/video-generation` | Helpery video generation | Typy providerów/żądań/wyników video generation |
  | `plugin-sdk/video-generation-core` | Współdzielony rdzeń video generation | Typy video generation, helpery failover, wyszukiwanie providera i parsowanie odwołań do modeli |
  | `plugin-sdk/interactive-runtime` | Helpery odpowiedzi interaktywnych | Normalizacja/redukcja payloadów odpowiedzi interaktywnych |
  | `plugin-sdk/channel-config-primitives` | Prymitywy konfiguracji kanału | Wąskie prymitywy channel config-schema |
  | `plugin-sdk/channel-config-writes` | Helpery zapisu konfiguracji kanału | Helpery autoryzacji zapisu konfiguracji kanału |
  | `plugin-sdk/channel-plugin-common` | Wspólne preludium kanału | Eksporty wspólnego preludium pluginów kanałów |
  | `plugin-sdk/channel-status` | Helpery stanu kanału | Współdzielone helpery migawki/podsumowania stanu kanału |
  | `plugin-sdk/allowlist-config-edit` | Helpery konfiguracji allowlisty | Helpery edycji/odczytu konfiguracji allowlisty |
  | `plugin-sdk/group-access` | Helpery dostępu do grup | Współdzielone helpery decyzji dostępu do grup |
  | `plugin-sdk/direct-dm` | Helpery direct-DM | Współdzielone helpery auth/guard direct-DM |
  | `plugin-sdk/extension-shared` | Współdzielone helpery rozszerzeń | Prymitywy helperów kanałów pasywnych/stanu |
  | `plugin-sdk/webhook-targets` | Helpery celów webhooków | Rejestr celów webhooków i helpery instalacji tras |
  | `plugin-sdk/webhook-path` | Helpery ścieżek webhooków | Helpery normalizacji ścieżek webhooków |
  | `plugin-sdk/web-media` | Współdzielone helpery web media | Helpery ładowania mediów zdalnych/lokalnych |
  | `plugin-sdk/zod` | Re-eksport Zod | Re-eksportowane `zod` dla użytkowników Plugin SDK |
  | `plugin-sdk/memory-core` | Helpery wbudowanego memory-core | Powierzchnia helperów menedżera pamięci/konfiguracji/plików/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | Fasada runtime silnika pamięci | Fasada runtime indeksu/wyszukiwania pamięci |
  | `plugin-sdk/memory-core-host-engine-foundation` | Bazowy silnik hosta pamięci | Eksporty bazowego silnika hosta pamięci |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Silnik embeddingów hosta pamięci | Eksporty silnika embeddingów hosta pamięci |
  | `plugin-sdk/memory-core-host-engine-qmd` | Silnik QMD hosta pamięci | Eksporty silnika QMD hosta pamięci |
  | `plugin-sdk/memory-core-host-engine-storage` | Silnik storage hosta pamięci | Eksporty silnika storage hosta pamięci |
  | `plugin-sdk/memory-core-host-multimodal` | Helpery multimodalne hosta pamięci | Helpery multimodalne hosta pamięci |
  | `plugin-sdk/memory-core-host-query` | Helpery zapytań hosta pamięci | Helpery zapytań hosta pamięci |
  | `plugin-sdk/memory-core-host-secret` | Helpery sekretów hosta pamięci | Helpery sekretów hosta pamięci |
  | `plugin-sdk/memory-core-host-status` | Helpery stanu hosta pamięci | Helpery stanu hosta pamięci |
  | `plugin-sdk/memory-core-host-runtime-cli` | Runtime CLI hosta pamięci | Helpery runtime CLI hosta pamięci |
  | `plugin-sdk/memory-core-host-runtime-core` | Główny runtime hosta pamięci | Helpery głównego runtime hosta pamięci |
  | `plugin-sdk/memory-core-host-runtime-files` | Helpery plików/runtime hosta pamięci | Helpery plików/runtime hosta pamięci |
  | `plugin-sdk/memory-lancedb` | Helpery wbudowanego memory-lancedb | Powierzchnia helperów memory-lancedb |
  | `plugin-sdk/testing` | Narzędzia testowe | Helpery testowe i mocki |
</Accordion>

Ta tabela celowo obejmuje wspólny podzbiór migracyjny, a nie pełną
powierzchnię SDK. Pełna lista ponad 200 punktów wejścia znajduje się w
`scripts/lib/plugin-sdk-entrypoints.json`.

Ta lista nadal zawiera niektóre powierzchnie helperów wbudowanych pluginów, takie jak
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` i `plugin-sdk/matrix*`. Nadal są eksportowane na potrzeby
utrzymania i zgodności wbudowanych pluginów, ale celowo
pominięto je we wspólnej tabeli migracji i nie są zalecanym celem dla
nowego kodu pluginów.

Ta sama zasada dotyczy innych rodzin helperów wbudowanych, takich jak:

- helpery obsługi przeglądarki: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- powierzchnie helperów/wbudowanych pluginów, takie jak `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` i `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` obecnie udostępnia wąską
powierzchnię helperów tokena: `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` oraz `resolveCopilotApiToken`.

Używaj najwęższego importu pasującego do zadania. Jeśli nie możesz znaleźć eksportu,
sprawdź źródło w `src/plugin-sdk/` lub zapytaj na Discord.

## Harmonogram usunięcia

| When                   | What happens                                                            |
| ---------------------- | ----------------------------------------------------------------------- |
| **Now**                | Przestarzałe powierzchnie emitują ostrzeżenia runtime                   |
| **Next major release** | Przestarzałe powierzchnie zostaną usunięte; pluginy nadal ich używające przestaną działać |

Wszystkie pluginy core zostały już zmigrowane. Zewnętrzne pluginy powinny przeprowadzić migrację
przed następnym dużym wydaniem.

## Tymczasowe wyciszenie ostrzeżeń

Ustaw te zmienne środowiskowe podczas pracy nad migracją:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

To tymczasowa furtka awaryjna, a nie trwałe rozwiązanie.

## Powiązane

- [Pierwsze kroki](/pl/plugins/building-plugins) — zbuduj swój pierwszy plugin
- [Przegląd SDK](/pl/plugins/sdk-overview) — pełna dokumentacja importów subpath
- [Pluginy kanałów](/pl/plugins/sdk-channel-plugins) — tworzenie pluginów kanałów
- [Pluginy providerów](/pl/plugins/sdk-provider-plugins) — tworzenie pluginów providerów
- [Wnętrze pluginów](/pl/plugins/architecture) — szczegółowe omówienie architektury
- [Manifest pluginu](/pl/plugins/manifest) — dokumentacja schematu manifestu
