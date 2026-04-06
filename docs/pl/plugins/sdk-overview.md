---
read_when:
    - Musisz wiedzieć, z której ścieżki podrzędnej SDK importować
    - Chcesz mieć dokumentację wszystkich metod rejestracji w OpenClawPluginApi
    - Szukasz konkretnego eksportu SDK
sidebarTitle: SDK Overview
summary: Mapa importów, dokumentacja API rejestracji i architektura SDK
title: Przegląd Plugin SDK
x-i18n:
    generated_at: "2026-04-06T03:11:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: d801641f26f39dc21490d2a69a337ff1affb147141360916b8b58a267e9f822a
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Przegląd Plugin SDK

Plugin SDK to typowany kontrakt między pluginami a rdzeniem. Ta strona jest
dokumentacją tego, **co importować** i **co można rejestrować**.

<Tip>
  **Szukasz przewodnika krok po kroku?**
  - Pierwszy plugin? Zacznij od [Pierwsze kroki](/pl/plugins/building-plugins)
  - Plugin kanału? Zobacz [Pluginy kanałów](/pl/plugins/sdk-channel-plugins)
  - Plugin providera? Zobacz [Pluginy providerów](/pl/plugins/sdk-provider-plugins)
</Tip>

## Konwencja importu

Zawsze importuj z konkretnej ścieżki podrzędnej:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Każda ścieżka podrzędna to mały, samowystarczalny moduł. Dzięki temu start jest szybki i
zapobiega to problemom z zależnościami cyklicznymi. W przypadku pomocników wejścia/builda specyficznych dla kanału
preferuj `openclaw/plugin-sdk/channel-core`; `openclaw/plugin-sdk/core` zachowaj dla
szerszej powierzchni zbiorczej i współdzielonych helperów, takich jak
`buildChannelConfigSchema`.

Nie dodawaj ani nie polegaj na wygodnych warstwach nazwanych od providerów, takich jak
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` ani
warstwach helperów oznaczonych marką kanału. Bundled plugins powinny składać generyczne
ścieżki podrzędne SDK we własnych barrelach `api.ts` lub `runtime-api.ts`, a rdzeń
powinien albo używać tych lokalnych barreli pluginu, albo dodać wąski generyczny kontrakt SDK,
gdy potrzeba jest rzeczywiście międzykanałowa.

Wygenerowana mapa eksportów nadal zawiera niewielki zestaw warstw helperów bundled plugins,
takich jak `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` i `plugin-sdk/matrix*`. Te
ścieżki podrzędne istnieją wyłącznie dla utrzymania bundled plugins i zgodności; są
celowo pominięte w typowej tabeli poniżej i nie są zalecaną ścieżką
importu dla nowych pluginów zewnętrznych.

## Dokumentacja ścieżek podrzędnych

Najczęściej używane ścieżki podrzędne, pogrupowane według przeznaczenia. Wygenerowana pełna lista
ponad 200 ścieżek podrzędnych znajduje się w `scripts/lib/plugin-sdk-entrypoints.json`.

Zarezerwowane ścieżki helperów bundled plugins nadal pojawiają się w tej wygenerowanej liście.
Traktuj je jako szczegół implementacyjny/powierzchnie zgodności, chyba że strona dokumentacji
jawnie promuje którąś z nich jako publiczną.

### Wejście pluginu

| Ścieżka podrzędna          | Kluczowe eksporty                                                                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                   |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                      |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                     |

<AccordionGroup>
  <Accordion title="Ścieżki podrzędne kanałów">
    | Ścieżka podrzędna | Kluczowe eksporty |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Eksport głównego schematu Zod `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, a także `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Współdzielone helpery kreatora konfiguracji, prompty list dozwolonych, konstruktory statusu konfiguracji |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Helpery konfiguracji i action-gate dla wielu kont oraz helpery fallbacku do konta domyślnego |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, helpery normalizacji account-id |
    | `plugin-sdk/account-resolution` | Wyszukiwanie konta + helpery fallbacku do wartości domyślnej |
    | `plugin-sdk/account-helpers` | Wąskie helpery list kont/działań na kontach |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Typy schematu konfiguracji kanału |
    | `plugin-sdk/telegram-command-config` | Helpery normalizacji/walidacji poleceń niestandardowych Telegram z fallbackiem do bundled contract |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Współdzielone helpery tras przychodzących + budowania envelope |
    | `plugin-sdk/inbound-reply-dispatch` | Współdzielone helpery rejestrowania i dispatchu danych przychodzących |
    | `plugin-sdk/messaging-targets` | Helpery parsowania/dopasowywania targetów |
    | `plugin-sdk/outbound-media` | Współdzielone helpery ładowania mediów wychodzących |
    | `plugin-sdk/outbound-runtime` | Helpery tożsamości wychodzącej/delegatów wysyłania |
    | `plugin-sdk/thread-bindings-runtime` | Helpery cyklu życia thread-binding i adapterów |
    | `plugin-sdk/agent-media-payload` | Starszy konstruktor payloadu mediów agenta |
    | `plugin-sdk/conversation-runtime` | Helpery conversation/thread binding, pairingu i configured-binding |
    | `plugin-sdk/runtime-config-snapshot` | Helper snapshotu konfiguracji runtime |
    | `plugin-sdk/runtime-group-policy` | Helpery rozwiązywania polityki grup w runtime |
    | `plugin-sdk/channel-status` | Współdzielone helpery snapshotu/podsumowania statusu kanału |
    | `plugin-sdk/channel-config-primitives` | Wąskie prymitywy schematu konfiguracji kanału |
    | `plugin-sdk/channel-config-writes` | Helpery autoryzacji zapisu konfiguracji kanału |
    | `plugin-sdk/channel-plugin-common` | Współdzielone eksporty prelude dla pluginów kanałów |
    | `plugin-sdk/allowlist-config-edit` | Helpery edycji/odczytu konfiguracji list dozwolonych |
    | `plugin-sdk/group-access` | Współdzielone helpery decyzji dostępu do grup |
    | `plugin-sdk/direct-dm` | Współdzielone helpery auth/guard dla bezpośrednich DM |
    | `plugin-sdk/interactive-runtime` | Helpery normalizacji/redukcji payloadów odpowiedzi interaktywnych |
    | `plugin-sdk/channel-inbound` | Helpery debounce, dopasowywania wzmianek i envelope |
    | `plugin-sdk/channel-send-result` | Typy wyniku odpowiedzi |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Helpery parsowania/dopasowywania targetów |
    | `plugin-sdk/channel-contract` | Typy kontraktu kanału |
    | `plugin-sdk/channel-feedback` | Integracja feedbacku/reakcji |
  </Accordion>

  <Accordion title="Ścieżki podrzędne providerów">
    | Ścieżka podrzędna | Kluczowe eksporty |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Kuratorowane helpery konfiguracji providerów lokalnych/self-hosted |
    | `plugin-sdk/self-hosted-provider-setup` | Skupione helpery konfiguracji self-hosted providerów zgodnych z OpenAI |
    | `plugin-sdk/provider-auth-runtime` | Helpery rozwiązywania kluczy API w runtime dla pluginów providerów |
    | `plugin-sdk/provider-auth-api-key` | Helpery onboardingu/zapisu profilu dla klucza API |
    | `plugin-sdk/provider-auth-result` | Standardowy konstruktor wyniku auth OAuth |
    | `plugin-sdk/provider-auth-login` | Współdzielone helpery interaktywnego logowania dla pluginów providerów |
    | `plugin-sdk/provider-env-vars` | Helpery wyszukiwania zmiennych env auth providera |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, współdzielone konstruktory polityki replay, helpery endpointów providerów i helpery normalizacji model-id, takie jak `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Generyczne helpery HTTP/endpoints/capabilities providera |
    | `plugin-sdk/provider-web-fetch` | Helpery rejestracji/cache konfiguracji web-fetch providerów |
    | `plugin-sdk/provider-web-search` | Helpery rejestracji/cache/config dla providerów web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, czyszczenie schematów Gemini + diagnostyka oraz helpery zgodności xAI, takie jak `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` i podobne |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, typy opakowań strumieni i współdzielone helpery opakowań Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Helpery poprawek konfiguracji onboardingu |
    | `plugin-sdk/global-singleton` | Pomocniki singletonów/map/cache lokalnych dla procesu |
  </Accordion>

  <Accordion title="Ścieżki podrzędne auth i bezpieczeństwa">
    | Ścieżka podrzędna | Kluczowe eksporty |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, helpery rejestru poleceń, helpery autoryzacji nadawcy |
    | `plugin-sdk/approval-auth-runtime` | Helpery rozwiązywania approvera i auth działań w tym samym czacie |
    | `plugin-sdk/approval-client-runtime` | Helpery profilu/filtra natywnych zgód na exec |
    | `plugin-sdk/approval-delivery-runtime` | Adaptery możliwości/dostarczania natywnych zgód |
    | `plugin-sdk/approval-native-runtime` | Helpery targetów natywnych zgód + account-binding |
    | `plugin-sdk/approval-reply-runtime` | Helpery payloadów odpowiedzi dla zgód exec/plugin |
    | `plugin-sdk/command-auth-native` | Natywne helpery auth poleceń + helpery natywnego session-target |
    | `plugin-sdk/command-detection` | Współdzielone helpery wykrywania poleceń |
    | `plugin-sdk/command-surface` | Normalizacja treści poleceń i helpery command-surface |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/security-runtime` | Współdzielone helpery zaufania, bramkowania DM, treści zewnętrznych i zbierania sekretów |
    | `plugin-sdk/ssrf-policy` | Helpery polityki SSRF dla listy dozwolonych hostów i sieci prywatnych |
    | `plugin-sdk/ssrf-runtime` | Helpery pinned-dispatcher, fetch z ochroną SSRF i polityki SSRF |
    | `plugin-sdk/secret-input` | Helpery parsowania wejścia sekretów |
    | `plugin-sdk/webhook-ingress` | Helpery żądań/targetów webhooków |
    | `plugin-sdk/webhook-request-guards` | Helpery rozmiaru body/timeoutu żądań |
  </Accordion>

  <Accordion title="Ścieżki podrzędne runtime i storage">
    | Ścieżka podrzędna | Kluczowe eksporty |
    | --- | --- |
    | `plugin-sdk/runtime` | Szerokie helpery runtime/logowania/backupu/instalacji pluginów |
    | `plugin-sdk/runtime-env` | Wąskie helpery env runtime, loggera, timeoutu, retry i backoff |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Współdzielone helpery poleceń/hooków/http/interakcji pluginów |
    | `plugin-sdk/hook-runtime` | Współdzielone helpery pipeline webhooków i hooków wewnętrznych |
    | `plugin-sdk/lazy-runtime` | Helpery leniwego importu/bindings runtime, takie jak `createLazyRuntimeModule`, `createLazyRuntimeMethod` i `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Helpery wykonywania procesów |
    | `plugin-sdk/cli-runtime` | Helpery formatowania CLI, oczekiwania i wersji |
    | `plugin-sdk/gateway-runtime` | Helpery klienta Gateway i łatek statusu kanałów |
    | `plugin-sdk/config-runtime` | Helpery ładowania/zapisu konfiguracji |
    | `plugin-sdk/telegram-command-config` | Helpery normalizacji nazw/opisów poleceń Telegram oraz sprawdzania duplikatów/konfliktów, nawet gdy powierzchnia bundled Telegram contract jest niedostępna |
    | `plugin-sdk/approval-runtime` | Helpery zgód exec/plugin, konstruktory możliwości zgód, helpery auth/profili, helpery natywnego routingu/runtime |
    | `plugin-sdk/reply-runtime` | Współdzielone helpery runtime przychodzących/odpowiedzi, chunking, dispatch, heartbeat, planner odpowiedzi |
    | `plugin-sdk/reply-dispatch-runtime` | Wąskie helpery dispatchu/finalizacji odpowiedzi |
    | `plugin-sdk/reply-history` | Współdzielone helpery krótkookresowej historii odpowiedzi, takie jak `buildHistoryContext`, `recordPendingHistoryEntry` i `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Wąskie helpery chunkingu tekstu/Markdown |
    | `plugin-sdk/session-store-runtime` | Helpery ścieżek magazynu sesji + updated-at |
    | `plugin-sdk/state-paths` | Helpery ścieżek katalogów stanu/OAuth |
    | `plugin-sdk/routing` | Helpery route/session-key/account-binding, takie jak `resolveAgentRoute`, `buildAgentSessionKey` i `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Współdzielone helpery podsumowania statusu kanału/konta, wartości domyślne stanu runtime i helpery metadanych problemów |
    | `plugin-sdk/target-resolver-runtime` | Współdzielone helpery rozwiązywania targetów |
    | `plugin-sdk/string-normalization-runtime` | Helpery normalizacji slug/string |
    | `plugin-sdk/request-url` | Wyodrębnianie stringowych URL z wejść podobnych do fetch/request |
    | `plugin-sdk/run-command` | Uruchamianie poleceń z limitem czasu i znormalizowanymi wynikami stdout/stderr |
    | `plugin-sdk/param-readers` | Wspólni czytelnicy parametrów dla narzędzi/CLI |
    | `plugin-sdk/tool-send` | Wyodrębnianie kanonicznych pól celu wysyłki z argumentów narzędzia |
    | `plugin-sdk/temp-path` | Współdzielone helpery ścieżek tymczasowego pobierania |
    | `plugin-sdk/logging-core` | Helpery loggera podsystemu i redakcji |
    | `plugin-sdk/markdown-table-runtime` | Helpery trybu tabel Markdown |
    | `plugin-sdk/json-store` | Małe helpery odczytu/zapisu stanu JSON |
    | `plugin-sdk/file-lock` | Re-entrant helpery blokady pliku |
    | `plugin-sdk/persistent-dedupe` | Helpery cache deduplikacji opartego na dysku |
    | `plugin-sdk/acp-runtime` | Helpery runtime/sesji ACP i dispatchu odpowiedzi |
    | `plugin-sdk/agent-config-primitives` | Wąskie prymitywy schematu konfiguracji runtime agenta |
    | `plugin-sdk/boolean-param` | Tolerancyjny czytnik parametrów boolean |
    | `plugin-sdk/dangerous-name-runtime` | Helpery rozwiązywania dopasowań niebezpiecznych nazw |
    | `plugin-sdk/device-bootstrap` | Helpery bootstrapu urządzeń i tokenów pairingu |
    | `plugin-sdk/extension-shared` | Współdzielone prymitywy helperów kanałów pasywnych i statusu |
    | `plugin-sdk/models-provider-runtime` | Helpery odpowiedzi polecenia `/models`/providerów |
    | `plugin-sdk/skill-commands-runtime` | Helpery listowania poleceń Skills |
    | `plugin-sdk/native-command-registry` | Helpery rejestru/build/serializacji natywnych poleceń |
    | `plugin-sdk/provider-zai-endpoint` | Helpery wykrywania endpointów Z.AI |
    | `plugin-sdk/infra-runtime` | Helpery zdarzeń systemowych/heartbeat |
    | `plugin-sdk/collection-runtime` | Małe helpery ograniczonych cache |
    | `plugin-sdk/diagnostic-runtime` | Helpery flag diagnostycznych i zdarzeń |
    | `plugin-sdk/error-runtime` | Graf błędów, formatowanie, współdzielone helpery klasyfikacji błędów, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Opakowany fetch, proxy i helpery pinned lookup |
    | `plugin-sdk/host-runtime` | Helpery normalizacji hostname i hostów SCP |
    | `plugin-sdk/retry-runtime` | Helpery konfiguracji retry i runnera retry |
    | `plugin-sdk/agent-runtime` | Helpery agent dir/identity/workspace |
    | `plugin-sdk/directory-runtime` | Zapytania/deduplikacja katalogów oparte na konfiguracji |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Ścieżki podrzędne capabilities i testowania">
    | Ścieżka podrzędna | Kluczowe eksporty |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Współdzielone helpery pobierania/przekształcania/przechowywania mediów oraz konstruktory payloadów mediów |
    | `plugin-sdk/media-understanding` | Typy providerów rozumienia mediów oraz eksporty helperów obrazów/audio skierowane do providerów |
    | `plugin-sdk/text-runtime` | Współdzielone helpery tekstu/Markdown/logowania, takie jak usuwanie tekstu widocznego dla asystenta, renderowanie/chunking/tabele Markdown, helpery redakcji, helpery tagów dyrektyw i bezpieczne utility tekstowe |
    | `plugin-sdk/text-chunking` | Helper chunkingu tekstu wychodzącego |
    | `plugin-sdk/speech` | Typy providerów mowy oraz helpery dyrektyw, rejestru i walidacji skierowane do providerów |
    | `plugin-sdk/speech-core` | Współdzielone typy providerów mowy, registry, dyrektywy i helpery normalizacji |
    | `plugin-sdk/realtime-transcription` | Typy providerów transkrypcji realtime i helpery rejestru |
    | `plugin-sdk/realtime-voice` | Typy providerów głosu realtime i helpery rejestru |
    | `plugin-sdk/image-generation` | Typy providerów generowania obrazów |
    | `plugin-sdk/image-generation-core` | Współdzielone typy generowania obrazów, helpery failover, auth i rejestru |
    | `plugin-sdk/music-generation` | Typy providerów/żądań/wyników generowania muzyki |
    | `plugin-sdk/music-generation-core` | Współdzielone typy generowania muzyki, helpery failover, lookup providera i parsowanie model-ref |
    | `plugin-sdk/video-generation` | Typy providerów/żądań/wyników generowania wideo |
    | `plugin-sdk/video-generation-core` | Współdzielone typy generowania wideo, helpery failover, lookup providera i parsowanie model-ref |
    | `plugin-sdk/webhook-targets` | Rejestr targetów webhooków i helpery instalacji tras |
    | `plugin-sdk/webhook-path` | Helpery normalizacji ścieżek webhooków |
    | `plugin-sdk/web-media` | Współdzielone helpery ładowania mediów zdalnych/lokalnych |
    | `plugin-sdk/zod` | Re-eksport `zod` dla konsumentów plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Ścieżki podrzędne pamięci">
    | Ścieżka podrzędna | Kluczowe eksporty |
    | --- | --- |
    | `plugin-sdk/memory-core` | Powierzchnia helperów bundled memory-core dla helperów manager/config/file/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Fasada runtime indeksowania/wyszukiwania pamięci |
    | `plugin-sdk/memory-core-host-engine-foundation` | Eksporty foundation engine hosta pamięci |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Eksporty embedding engine hosta pamięci |
    | `plugin-sdk/memory-core-host-engine-qmd` | Eksporty QMD engine hosta pamięci |
    | `plugin-sdk/memory-core-host-engine-storage` | Eksporty storage engine hosta pamięci |
    | `plugin-sdk/memory-core-host-multimodal` | Multimodalne helpery hosta pamięci |
    | `plugin-sdk/memory-core-host-query` | Helpery zapytań hosta pamięci |
    | `plugin-sdk/memory-core-host-secret` | Helpery sekretów hosta pamięci |
    | `plugin-sdk/memory-core-host-status` | Helpery statusu hosta pamięci |
    | `plugin-sdk/memory-core-host-runtime-cli` | Helpery runtime CLI hosta pamięci |
    | `plugin-sdk/memory-core-host-runtime-core` | Helpery głównego runtime hosta pamięci |
    | `plugin-sdk/memory-core-host-runtime-files` | Helpery plików/runtime hosta pamięci |
    | `plugin-sdk/memory-lancedb` | Powierzchnia helperów bundled memory-lancedb |
  </Accordion>

  <Accordion title="Zarezerwowane ścieżki podrzędne helperów bundled">
    | Rodzina | Obecne ścieżki podrzędne | Zamierzone użycie |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Helpery wsparcia bundled browser plugin (`browser-support` pozostaje barrelem zgodności) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Powierzchnia helperów/runtime bundled Matrix |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Powierzchnia helperów/runtime bundled LINE |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Powierzchnia helperów bundled IRC |
    | Helpery specyficzne dla kanału | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Warstwy zgodności/helperów bundled kanałów |
    | Helpery auth/specyficzne dla pluginu | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Warstwy helperów bundled funkcji/pluginów; `plugin-sdk/github-copilot-token` eksportuje obecnie `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` i `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API rejestracji

Callback `register(api)` otrzymuje obiekt `OpenClawPluginApi` z następującymi
metodami:

### Rejestracja capabilities

| Metoda                                           | Co rejestruje                    |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | Wnioskowanie tekstowe (LLM)      |
| `api.registerChannel(...)`                       | Kanał wiadomości                 |
| `api.registerSpeechProvider(...)`                | Syntezę text-to-speech / STT     |
| `api.registerRealtimeTranscriptionProvider(...)` | Strumieniową transkrypcję realtime |
| `api.registerRealtimeVoiceProvider(...)`         | Dwukierunkowe sesje głosowe realtime |
| `api.registerMediaUnderstandingProvider(...)`    | Analizę obrazów/audio/wideo      |
| `api.registerImageGenerationProvider(...)`       | Generowanie obrazów              |
| `api.registerMusicGenerationProvider(...)`       | Generowanie muzyki               |
| `api.registerVideoGenerationProvider(...)`       | Generowanie wideo                |
| `api.registerWebFetchProvider(...)`              | Provider web fetch / scrape      |
| `api.registerWebSearchProvider(...)`             | Wyszukiwanie w sieci             |

### Narzędzia i polecenia

| Metoda                          | Co rejestruje                                 |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | Narzędzie agenta (wymagane lub `{ optional: true }`) |
| `api.registerCommand(def)`      | Niestandardowe polecenie (omija LLM)          |

### Infrastruktura

| Metoda                                         | Co rejestruje       |
| ---------------------------------------------- | ------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook zdarzeń        |
| `api.registerHttpRoute(params)`                | Endpoint HTTP Gateway |
| `api.registerGatewayMethod(name, handler)`     | Metodę RPC Gateway  |
| `api.registerCli(registrar, opts?)`            | Podpolecenie CLI    |
| `api.registerService(service)`                 | Usługę działającą w tle |
| `api.registerInteractiveHandler(registration)` | Handler interaktywny |

Zarezerwowane przestrzenie nazw admina rdzenia (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) zawsze pozostają `operator.admin`, nawet jeśli plugin próbuje przypisać
węższy zakres metody gatewaya. Dla metod należących do pluginu preferuj prefiksy specyficzne dla pluginu.

### Metadane rejestracji CLI

`api.registerCli(registrar, opts?)` akceptuje dwa rodzaje metadanych najwyższego poziomu:

- `commands`: jawne korzenie poleceń należące do rejestratora
- `descriptors`: deskryptory poleceń używane podczas parsowania dla głównej pomocy CLI,
  routingu i leniwej rejestracji CLI pluginu

Jeśli chcesz, aby polecenie pluginu pozostało ładowane leniwie w zwykłej ścieżce głównego CLI,
podaj `descriptors`, które obejmą każdy korzeń polecenia najwyższego poziomu udostępniany przez tego
rejestratora.

```typescript
api.registerCli(
  async ({ program }) => {
    const { registerMatrixCli } = await import("./src/cli.js");
    registerMatrixCli({ program });
  },
  {
    descriptors: [
      {
        name: "matrix",
        description: "Manage Matrix accounts, verification, devices, and profile state",
        hasSubcommands: true,
      },
    ],
  },
);
```

Używaj samego `commands` tylko wtedy, gdy nie potrzebujesz leniwej rejestracji głównego CLI.
Ta zgodnościowa ścieżka eager nadal jest wspierana, ale nie instaluje
placeholderów opartych na deskryptorach do leniwego ładowania podczas parsowania.

### Wyłączne sloty

| Metoda                                     | Co rejestruje                         |
| ------------------------------------------ | ------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Silnik kontekstu (aktywny tylko jeden naraz) |
| `api.registerMemoryPromptSection(builder)` | Konstruktor sekcji promptu pamięci    |
| `api.registerMemoryFlushPlan(resolver)`    | Resolver planu flush pamięci          |
| `api.registerMemoryRuntime(runtime)`       | Adapter runtime pamięci               |

### Adaptery embeddingów pamięci

| Metoda                                         | Co rejestruje                                  |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Adapter embeddingów pamięci dla aktywnego pluginu |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan` i
  `registerMemoryRuntime` są zarezerwowane wyłącznie dla pluginów pamięci.
- `registerMemoryEmbeddingProvider` pozwala aktywnemu pluginowi pamięci zarejestrować jeden
  lub więcej identyfikatorów adapterów embeddingów (na przykład `openai`, `gemini` albo własny identyfikator zdefiniowany przez plugin).
- Konfiguracja użytkownika, taka jak `agents.defaults.memorySearch.provider` i
  `agents.defaults.memorySearch.fallback`, jest rozwiązywana względem tych zarejestrowanych
  identyfikatorów adapterów.

### Zdarzenia i cykl życia

| Metoda                                       | Co robi                        |
| -------------------------------------------- | ------------------------------ |
| `api.on(hookName, handler, opts?)`           | Typowany hook cyklu życia      |
| `api.onConversationBindingResolved(handler)` | Callback resolution conversation binding |

### Semantyka decyzji hooków

- `before_tool_call`: zwrócenie `{ block: true }` jest rozstrzygające. Gdy którykolwiek handler to ustawi, handlery o niższym priorytecie są pomijane.
- `before_tool_call`: zwrócenie `{ block: false }` jest traktowane jako brak decyzji (tak samo jak pominięcie `block`), a nie jako nadpisanie.
- `before_install`: zwrócenie `{ block: true }` jest rozstrzygające. Gdy którykolwiek handler to ustawi, handlery o niższym priorytecie są pomijane.
- `before_install`: zwrócenie `{ block: false }` jest traktowane jako brak decyzji (tak samo jak pominięcie `block`), a nie jako nadpisanie.
- `reply_dispatch`: zwrócenie `{ handled: true, ... }` jest rozstrzygające. Gdy którykolwiek handler przejmie dispatch, handlery o niższym priorytecie i domyślna ścieżka dispatchu modelu są pomijane.
- `message_sending`: zwrócenie `{ cancel: true }` jest rozstrzygające. Gdy którykolwiek handler to ustawi, handlery o niższym priorytecie są pomijane.
- `message_sending`: zwrócenie `{ cancel: false }` jest traktowane jako brak decyzji (tak samo jak pominięcie `cancel`), a nie jako nadpisanie.

### Pola obiektu API

| Pole                    | Typ                       | Opis                                                                                         |
| ----------------------- | ------------------------- | -------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | Identyfikator pluginu                                                                        |
| `api.name`               | `string`                  | Wyświetlana nazwa                                                                            |
| `api.version`            | `string?`                 | Wersja pluginu (opcjonalnie)                                                                 |
| `api.description`        | `string?`                 | Opis pluginu (opcjonalnie)                                                                   |
| `api.source`             | `string`                  | Ścieżka źródłowa pluginu                                                                     |
| `api.rootDir`            | `string?`                 | Katalog główny pluginu (opcjonalnie)                                                         |
| `api.config`             | `OpenClawConfig`          | Bieżący snapshot konfiguracji (aktywny snapshot runtime w pamięci, gdy jest dostępny)       |
| `api.pluginConfig`       | `Record<string, unknown>` | Konfiguracja specyficzna dla pluginu z `plugins.entries.<id>.config`                         |
| `api.runtime`            | `PluginRuntime`           | [Helpery runtime](/pl/plugins/sdk-runtime)                                                      |
| `api.logger`             | `PluginLogger`            | Logger o zawężonym zakresie (`debug`, `info`, `warn`, `error`)                               |
| `api.registrationMode`   | `PluginRegistrationMode`  | Bieżący tryb ładowania; `"setup-runtime"` to lekki etap uruchamiania/konfiguracji przed pełnym wejściem |
| `api.resolvePath(input)` | `(string) => string`      | Rozwiąż ścieżkę względem katalogu głównego pluginu                                           |

## Konwencja modułów wewnętrznych

Wewnątrz pluginu używaj lokalnych plików barrel do importów wewnętrznych:

```
my-plugin/
  api.ts            # Publiczne eksporty dla zewnętrznych konsumentów
  runtime-api.ts    # Eksporty runtime tylko do użytku wewnętrznego
  index.ts          # Punkt wejścia pluginu
  setup-entry.ts    # Lekki punkt wejścia tylko do konfiguracji (opcjonalnie)
```

<Warning>
  Nigdy nie importuj własnego pluginu przez `openclaw/plugin-sdk/<your-plugin>`
  z kodu produkcyjnego. Kieruj importy wewnętrzne przez `./api.ts` lub
  `./runtime-api.ts`. Ścieżka SDK jest wyłącznie kontraktem zewnętrznym.
</Warning>

Ładowane przez fasadę publiczne powierzchnie bundled plugins (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` i podobne publiczne pliki wejściowe) preferują teraz
aktywny snapshot konfiguracji runtime, gdy OpenClaw już działa. Jeśli snapshot runtime
jeszcze nie istnieje, wracają do konfiguracji rozwiązanej z pliku na dysku.

Pluginy providerów mogą również udostępniać wąski barrel kontraktowy lokalny dla pluginu, gdy
helper jest celowo specyficzny dla providera i jeszcze nie należy do generycznej ścieżki podrzędnej SDK.
Obecny przykład bundled: provider Anthropic trzyma swoje helpery strumienia Claude
we własnej publicznej warstwie `api.ts` / `contract-api.ts`, zamiast promować logikę nagłówków beta Anthropic i `service_tier` do generycznego
kontraktu `plugin-sdk/*`.

Inne obecne przykłady bundled:

- `@openclaw/openai-provider`: `api.ts` eksportuje konstruktory providerów,
  helpery modeli domyślnych i konstruktory providerów realtime
- `@openclaw/openrouter-provider`: `api.ts` eksportuje konstruktor providera oraz
  helpery onboardingu/konfiguracji

<Warning>
  Kod produkcyjny rozszerzeń powinien również unikać importów `openclaw/plugin-sdk/<other-plugin>`.
  Jeśli helper jest naprawdę współdzielony, promuj go do neutralnej ścieżki podrzędnej SDK,
  takiej jak `openclaw/plugin-sdk/speech`, `.../provider-model-shared` lub innej
  powierzchni zorientowanej na capability, zamiast sprzęgać ze sobą dwa pluginy.
</Warning>

## Powiązane

- [Punkty wejścia](/pl/plugins/sdk-entrypoints) — opcje `definePluginEntry` i `defineChannelPluginEntry`
- [Helpery runtime](/pl/plugins/sdk-runtime) — pełna dokumentacja przestrzeni nazw `api.runtime`
- [Setup i konfiguracja](/pl/plugins/sdk-setup) — pakowanie, manifesty, schematy konfiguracji
- [Testowanie](/pl/plugins/sdk-testing) — narzędzia testowe i reguły lint
- [Migracja SDK](/pl/plugins/sdk-migration) — migracja z przestarzałych powierzchni
- [Wnętrze pluginów](/pl/plugins/architecture) — szczegółowa architektura i model capabilities
