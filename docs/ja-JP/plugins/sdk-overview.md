---
read_when:
    - どのSDK subpathからimportすべきか知る必要がある
    - OpenClawPluginApi上のすべての登録メソッドのリファレンスが欲しい
    - 特定のSDK exportを調べている
sidebarTitle: SDK Overview
summary: import map、登録APIリファレンス、SDKアーキテクチャ
title: Plugin SDK概要
x-i18n:
    generated_at: "2026-04-07T04:45:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: fe1fe41beaf73a7bdf807e281d181df7a5da5819343823c4011651fb234b0905
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDK概要

plugin SDKは、pluginsとcoreの間にある型付き契約です。このページは、
**何をimportするか** と **何を登録できるか** のリファレンスです。

<Tip>
  **ハウツーガイドを探していますか？**
  - 最初のpluginですか？ [はじめに](/ja-JP/plugins/building-plugins) から始めてください
  - channel pluginですか？ [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) を参照してください
  - provider pluginですか？ [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) を参照してください
</Tip>

## Import規約

必ず特定のsubpathからimportしてください:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

各subpathは、小さく自己完結したmoduleです。これにより起動を高速に保ち、
循環依存の問題を防げます。channel固有のentry/build helperについては、
`openclaw/plugin-sdk/channel-core` を優先し、
より広いumbrella surfaceと
`buildChannelConfigSchema` のような共有helperには `openclaw/plugin-sdk/core` を使ってください。

`openclaw/plugin-sdk/slack`、`openclaw/plugin-sdk/discord`、
`openclaw/plugin-sdk/signal`、`openclaw/plugin-sdk/whatsapp` のような
provider名ベースのconvenience seamや、
channelブランドのhelper seamを追加したり依存したりしないでください。バンドルされたpluginsは、
汎用的なSDK subpathを自分自身の `api.ts` または `runtime-api.ts` barrel内で組み合わせるべきであり、coreは
それらのpluginローカルbarrelを使うか、必要性が本当にcross-channelな場合にのみ狭い汎用SDK
contractを追加すべきです。

生成されたexport mapには、`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、
`plugin-sdk/zalo`、`plugin-sdk/zalo-setup`、`plugin-sdk/matrix*` のような、
少数のバンドルplugin helper seamがまだ含まれています。これらの
subpathはバンドルpluginの保守と互換性のためだけに存在しており、
下の一般的な表からは意図的に省かれていて、新しいサードパーティpluginsに推奨される
import pathではありません。

## Subpathリファレンス

目的ごとにグループ化した、最もよく使われるsubpathです。完全な200以上のsubpathからなる生成済み一覧は
`scripts/lib/plugin-sdk-entrypoints.json` にあります。

予約済みのバンドルplugin helper subpathは、この生成済み一覧にも引き続き表示されます。
docページで明示的にpublicとして推奨されていない限り、これらは実装詳細/互換性surfaceとして扱ってください。

### Plugin entry

| Subpath                     | 主要export                                                                                                                            |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Channel subpaths">
    | Subpath | 主要export |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | ルート `openclaw.json` Zodスキーマexport（`OpenClawSchema`） |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, および `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | 共有setupウィザードhelper、allowlist prompt、setup status builder |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | マルチアカウントconfig/action-gate helper、default-accountフォールバックhelper |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`、account-id正規化helper |
    | `plugin-sdk/account-resolution` | account lookup + defaultフォールバックhelper |
    | `plugin-sdk/account-helpers` | 狭いaccount-list/account-action helper |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | channel config schema型 |
    | `plugin-sdk/telegram-command-config` | バンドルcontractフォールバック付きのTelegram custom-command正規化/検証helper |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | 共有inbound route + envelope builder helper |
    | `plugin-sdk/inbound-reply-dispatch` | 共有inbound記録/dispatch helper |
    | `plugin-sdk/messaging-targets` | target解析/一致helper |
    | `plugin-sdk/outbound-media` | 共有outbound media読み込みhelper |
    | `plugin-sdk/outbound-runtime` | outbound identity/send delegate helper |
    | `plugin-sdk/thread-bindings-runtime` | thread-bindingライフサイクルとadapter helper |
    | `plugin-sdk/agent-media-payload` | 旧式agent media payload builder |
    | `plugin-sdk/conversation-runtime` | conversation/thread binding、pairing、configured-binding helper |
    | `plugin-sdk/runtime-config-snapshot` | runtime config snapshot helper |
    | `plugin-sdk/runtime-group-policy` | runtime group-policy解決helper |
    | `plugin-sdk/channel-status` | 共有channel status snapshot/summary helper |
    | `plugin-sdk/channel-config-primitives` | 狭いchannel config-schema primitive |
    | `plugin-sdk/channel-config-writes` | channel config-write認可helper |
    | `plugin-sdk/channel-plugin-common` | 共有channel plugin prelude export |
    | `plugin-sdk/allowlist-config-edit` | allowlist config編集/読み取りhelper |
    | `plugin-sdk/group-access` | 共有group-access判定helper |
    | `plugin-sdk/direct-dm` | 共有direct-DM auth/guard helper |
    | `plugin-sdk/interactive-runtime` | interactive reply payload正規化/縮約helper |
    | `plugin-sdk/channel-inbound` | debounce、mention一致、envelope helper |
    | `plugin-sdk/channel-send-result` | reply result型 |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | target解析/一致helper |
    | `plugin-sdk/channel-contract` | channel contract型 |
    | `plugin-sdk/channel-feedback` | feedback/reaction配線 |
    | `plugin-sdk/channel-secret-runtime` | `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment`、およびsecret target型のような狭いsecret-contract helper |
  </Accordion>

  <Accordion title="Provider subpaths">
    | Subpath | 主要export |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | 厳選されたlocal/self-hosted provider setup helper |
    | `plugin-sdk/self-hosted-provider-setup` | 焦点を絞ったOpenAI互換self-hosted provider setup helper |
    | `plugin-sdk/cli-backend` | CLI backend defaults + watchdog定数 |
    | `plugin-sdk/provider-auth-runtime` | provider plugins向けランタイムAPIキー解決helper |
    | `plugin-sdk/provider-auth-api-key` | `upsertApiKeyProfile` などのAPIキーonboarding/profile-write helper |
    | `plugin-sdk/provider-auth-result` | 標準OAuth auth-result builder |
    | `plugin-sdk/provider-auth-login` | provider plugins向け共有interactive login helper |
    | `plugin-sdk/provider-env-vars` | provider auth env-var lookup helper |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`、共有replay-policy builder、provider endpoint helper、`normalizeNativeXaiModelId` などのmodel-id正規化helper |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | 汎用provider HTTP/endpoint capability helper |
    | `plugin-sdk/provider-web-fetch` | web-fetch provider登録/cache helper |
    | `plugin-sdk/provider-web-search-contract` | `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig`、scoped credential setter/getterなどの狭いweb-search config/credential contract helper |
    | `plugin-sdk/provider-web-search` | web-search provider登録/cache/runtime helper |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini schema cleanup + diagnostics、`resolveXaiModelCompatPatch` / `applyXaiModelCompat` などのxAI compat helper |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` など |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, stream wrapper型、および共有Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot wrapper helper |
    | `plugin-sdk/provider-onboard` | onboarding config patch helper |
    | `plugin-sdk/global-singleton` | process-local singleton/map/cache helper |
  </Accordion>

  <Accordion title="認証とセキュリティのsubpaths">
    | Subpath | 主要export |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`、command registry helper、sender認可helper |
    | `plugin-sdk/approval-auth-runtime` | approver解決とsame-chat action-auth helper |
    | `plugin-sdk/approval-client-runtime` | native exec approval profile/filter helper |
    | `plugin-sdk/approval-delivery-runtime` | native approval capability/delivery adapter |
    | `plugin-sdk/approval-native-runtime` | native approval target + account-binding helper |
    | `plugin-sdk/approval-reply-runtime` | exec/plugin approval reply payload helper |
    | `plugin-sdk/command-auth-native` | native command auth + native session-target helper |
    | `plugin-sdk/command-detection` | 共有command検出helper |
    | `plugin-sdk/command-surface` | command-body正規化とcommand-surface helper |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | channel/plugin secret surface向けの狭いsecret-contract collection helper |
    | `plugin-sdk/security-runtime` | 共有trust、DM gating、external-content、secret collection helper |
    | `plugin-sdk/ssrf-policy` | host allowlistとprivate-network SSRF policy helper |
    | `plugin-sdk/ssrf-runtime` | pinned-dispatcher、SSRF保護fetch、SSRF policy helper |
    | `plugin-sdk/secret-input` | secret input解析helper |
    | `plugin-sdk/webhook-ingress` | webhook request/target helper |
    | `plugin-sdk/webhook-request-guards` | request body size/timeout helper |
  </Accordion>

  <Accordion title="ランタイムとストレージのsubpaths">
    | Subpath | 主要export |
    | --- | --- |
    | `plugin-sdk/runtime` | 広範なruntime/logging/backup/plugin-install helper |
    | `plugin-sdk/runtime-env` | 狭いruntime env、logger、timeout、retry、backoff helper |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | 共有plugin command/hook/http/interactive helper |
    | `plugin-sdk/hook-runtime` | 共有webhook/internal hook pipeline helper |
    | `plugin-sdk/lazy-runtime` | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeSurface` などのlazy runtime import/binding helper |
    | `plugin-sdk/process-runtime` | process exec helper |
    | `plugin-sdk/cli-runtime` | CLI formatting、wait、version helper |
    | `plugin-sdk/gateway-runtime` | Gateway clientとchannel-status patch helper |
    | `plugin-sdk/config-runtime` | config load/write helper |
    | `plugin-sdk/telegram-command-config` | バンドルされたTelegram contract surfaceが利用できない場合でも、Telegram command-name/description正規化と重複/競合チェックを行う |
    | `plugin-sdk/approval-runtime` | exec/plugin approval helper、approval-capability builder、auth/profile helper、native routing/runtime helper |
    | `plugin-sdk/reply-runtime` | 共有inbound/reply runtime helper、chunking、dispatch、heartbeat、reply planner |
    | `plugin-sdk/reply-dispatch-runtime` | 狭いreply dispatch/finalize helper |
    | `plugin-sdk/reply-history` | `buildHistoryContext`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` などの共有short-window reply-history helper |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | 狭いtext/markdown chunking helper |
    | `plugin-sdk/session-store-runtime` | session store path + updated-at helper |
    | `plugin-sdk/state-paths` | state/OAuthディレクトリpath helper |
    | `plugin-sdk/routing` | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId` などのroute/session-key/account binding helper |
    | `plugin-sdk/status-helpers` | 共有channel/account status summary helper、runtime-state defaults、issue metadata helper |
    | `plugin-sdk/target-resolver-runtime` | 共有target resolver helper |
    | `plugin-sdk/string-normalization-runtime` | slug/string正規化helper |
    | `plugin-sdk/request-url` | fetch/request風inputから文字列URLを抽出 |
    | `plugin-sdk/run-command` | 正規化されたstdout/stderr結果を伴う時間制限付きcommand runner |
    | `plugin-sdk/param-readers` | 一般的なtool/CLI param reader |
    | `plugin-sdk/tool-send` | tool argsからcanonicalなsend target fieldを抽出 |
    | `plugin-sdk/temp-path` | 共有temp-download path helper |
    | `plugin-sdk/logging-core` | subsystem loggerとredaction helper |
    | `plugin-sdk/markdown-table-runtime` | Markdown table mode helper |
    | `plugin-sdk/json-store` | 小さなJSON state読み書きhelper |
    | `plugin-sdk/file-lock` | 再入可能file-lock helper |
    | `plugin-sdk/persistent-dedupe` | disk-backed dedupe cache helper |
    | `plugin-sdk/acp-runtime` | ACP runtime/sessionとreply-dispatch helper |
    | `plugin-sdk/agent-config-primitives` | 狭いagent runtime config-schema primitive |
    | `plugin-sdk/boolean-param` | 緩いboolean param reader |
    | `plugin-sdk/dangerous-name-runtime` | dangerous-name一致解決helper |
    | `plugin-sdk/device-bootstrap` | device bootstrapとpairing token helper |
    | `plugin-sdk/extension-shared` | 共有passive-channel、status、ambient proxy helper primitive |
    | `plugin-sdk/models-provider-runtime` | `/models` command/provider reply helper |
    | `plugin-sdk/skill-commands-runtime` | skill command listing helper |
    | `plugin-sdk/native-command-registry` | native command registry/build/serialize helper |
    | `plugin-sdk/provider-zai-endpoint` | Z.A.I endpoint検出helper |
    | `plugin-sdk/infra-runtime` | system event/heartbeat helper |
    | `plugin-sdk/collection-runtime` | 小さなbounded cache helper |
    | `plugin-sdk/diagnostic-runtime` | diagnostic flagとevent helper |
    | `plugin-sdk/error-runtime` | error graph、formatting、共有error分類helper、`isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | wrapped fetch、proxy、pinned lookup helper |
    | `plugin-sdk/host-runtime` | hostnameとSCP host正規化helper |
    | `plugin-sdk/retry-runtime` | retry configとretry runner helper |
    | `plugin-sdk/agent-runtime` | agentディレクトリ/identity/workspace helper |
    | `plugin-sdk/directory-runtime` | configベースのdirectory問い合わせ/dedup |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Capabilityとテストのsubpaths">
    | Subpath | 主要export |
    | --- | --- |
    | `plugin-sdk/media-runtime` | media payload builderに加えて、共有media fetch/transform/store helper |
    | `plugin-sdk/media-generation-runtime` | 共有media-generation failover helper、candidate selection、missing-model messaging |
    | `plugin-sdk/media-understanding` | media understanding provider型、およびprovider向けimage/audio helper export |
    | `plugin-sdk/text-runtime` | assistant-visible-text除去、markdown render/chunking/table helper、redaction helper、directive-tag helper、safe-text utilitiesなどの共有text/markdown/logging helper |
    | `plugin-sdk/text-chunking` | outbound text chunking helper |
    | `plugin-sdk/speech` | speech provider型、およびprovider向けdirective、registry、validation helper |
    | `plugin-sdk/speech-core` | 共有speech provider型、registry、directive、正規化helper |
    | `plugin-sdk/realtime-transcription` | realtime transcription provider型とregistry helper |
    | `plugin-sdk/realtime-voice` | realtime voice provider型とregistry helper |
    | `plugin-sdk/image-generation` | image generation provider型 |
    | `plugin-sdk/image-generation-core` | 共有image-generation型、failover、auth、registry helper |
    | `plugin-sdk/music-generation` | music generation provider/request/result型 |
    | `plugin-sdk/music-generation-core` | 共有music-generation型、failover helper、provider lookup、model-ref解析 |
    | `plugin-sdk/video-generation` | video generation provider/request/result型 |
    | `plugin-sdk/video-generation-core` | 共有video-generation型、failover helper、provider lookup、model-ref解析 |
    | `plugin-sdk/webhook-targets` | webhook target registryとroute-install helper |
    | `plugin-sdk/webhook-path` | webhook path正規化helper |
    | `plugin-sdk/web-media` | 共有remote/local media読み込みhelper |
    | `plugin-sdk/zod` | plugin SDK利用者向けに再exportされた `zod` |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Memory subpaths">
    | Subpath | 主要export |
    | --- | --- |
    | `plugin-sdk/memory-core` | manager/config/file/CLI helper向けのバンドルされたmemory-core helper surface |
    | `plugin-sdk/memory-core-engine-runtime` | memory index/search runtime facade |
    | `plugin-sdk/memory-core-host-engine-foundation` | memory host foundation engine export |
    | `plugin-sdk/memory-core-host-engine-embeddings` | memory host embedding engine export |
    | `plugin-sdk/memory-core-host-engine-qmd` | memory host QMD engine export |
    | `plugin-sdk/memory-core-host-engine-storage` | memory host storage engine export |
    | `plugin-sdk/memory-core-host-multimodal` | memory host multimodal helper |
    | `plugin-sdk/memory-core-host-query` | memory host query helper |
    | `plugin-sdk/memory-core-host-secret` | memory host secret helper |
    | `plugin-sdk/memory-core-host-events` | memory host event journal helper |
    | `plugin-sdk/memory-core-host-status` | memory host status helper |
    | `plugin-sdk/memory-core-host-runtime-cli` | memory host CLI runtime helper |
    | `plugin-sdk/memory-core-host-runtime-core` | memory host core runtime helper |
    | `plugin-sdk/memory-core-host-runtime-files` | memory host file/runtime helper |
    | `plugin-sdk/memory-host-core` | memory host core runtime helperへのvendor-neutral alias |
    | `plugin-sdk/memory-host-events` | memory host event journal helperへのvendor-neutral alias |
    | `plugin-sdk/memory-host-files` | memory host file/runtime helperへのvendor-neutral alias |
    | `plugin-sdk/memory-host-markdown` | memory隣接plugin向けの共有managed-markdown helper |
    | `plugin-sdk/memory-host-search` | search-managerアクセス向けのactive memory runtime facade |
    | `plugin-sdk/memory-host-status` | memory host status helperへのvendor-neutral alias |
    | `plugin-sdk/memory-lancedb` | バンドルされたmemory-lancedb helper surface |
  </Accordion>

  <Accordion title="予約済みバンドルhelper subpaths">
    | Family | 現在のsubpaths | 意図された用途 |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | バンドルbrowser pluginサポートhelper（`browser-support` は互換性barrelのまま） |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | バンドルMatrix helper/runtime surface |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | バンドルLINE helper/runtime surface |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | バンドルIRC helper surface |
    | Channel固有helper | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | バンドルchannel互換性/helper seam |
    | Auth/plugin固有helper | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | バンドルfeature/plugin helper seam; `plugin-sdk/github-copilot-token` は現在 `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken`, `resolveCopilotApiToken` をexport |
  </Accordion>
</AccordionGroup>

## 登録API

`register(api)` コールバックは、次の
メソッドを持つ `OpenClawPluginApi` オブジェクトを受け取ります。

### Capability登録

| Method                                           | 登録するもの                     |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | Text inference（LLM）            |
| `api.registerCliBackend(...)`                    | local CLI inference backend      |
| `api.registerChannel(...)`                       | messaging channel                |
| `api.registerSpeechProvider(...)`                | text-to-speech / STT synthesis   |
| `api.registerRealtimeTranscriptionProvider(...)` | streaming realtime transcription |
| `api.registerRealtimeVoiceProvider(...)`         | duplex realtime voice sessions   |
| `api.registerMediaUnderstandingProvider(...)`    | image/audio/video analysis       |
| `api.registerImageGenerationProvider(...)`       | image generation                 |
| `api.registerMusicGenerationProvider(...)`       | music generation                 |
| `api.registerVideoGenerationProvider(...)`       | video generation                 |
| `api.registerWebFetchProvider(...)`              | web fetch / scrape provider      |
| `api.registerWebSearchProvider(...)`             | web search                       |

### Toolsとcommands

| Method                          | 登録するもの                                  |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | agent tool（必須、または `{ optional: true }`） |
| `api.registerCommand(def)`      | カスタムcommand（LLMをバイパス）               |

### Infrastructure

| Method                                         | 登録するもの                        |
| ---------------------------------------------- | ----------------------------------- |
| `api.registerHook(events, handler, opts?)`     | event hook                          |
| `api.registerHttpRoute(params)`                | Gateway HTTP endpoint               |
| `api.registerGatewayMethod(name, handler)`     | Gateway RPC method                  |
| `api.registerCli(registrar, opts?)`            | CLI subcommand                      |
| `api.registerService(service)`                 | background service                  |
| `api.registerInteractiveHandler(registration)` | interactive handler                 |
| `api.registerMemoryPromptSupplement(builder)`  | 追加型のmemory隣接prompt section    |
| `api.registerMemoryCorpusSupplement(adapter)`  | 追加型のmemory search/read corpus   |

予約済みcore admin namespace（`config.*`、`exec.approvals.*`、`wizard.*`、
`update.*`）は、pluginがより狭い
gateway method scopeを割り当てようとしても、常に `operator.admin` のままです。pluginが所有するmethodには、
plugin固有のprefixを優先してください。

### CLI登録メタデータ

`api.registerCli(registrar, opts?)` は、2種類のトップレベルメタデータを受け取ります:

- `commands`: registrarが所有する明示的なcommand root
- `descriptors`: ルートCLI help、
  routing、lazy plugin CLI登録に使われるparse時のcommand descriptor

通常のルートCLI経路でplugin commandをlazy-loadのままにしたい場合は、
そのregistrarが公開するすべてのトップレベルcommand rootをカバーする `descriptors`
を指定してください。

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

ルートCLI登録のlazy loadingが不要な場合にのみ、`commands` 単独を使用してください。
このeager互換経路は引き続きサポートされていますが、parse時lazy loading用の
descriptor-backed placeholderはインストールしません。

### CLI backend登録

`api.registerCliBackend(...)` を使うと、`codex-cli` のようなlocal
AI CLI backendのデフォルトconfigをpluginが所有できます。

- backendの `id` は、`codex-cli/gpt-5` のようなmodel refにおけるprovider prefixになります。
- backendの `config` は `agents.defaults.cliBackends.<id>` と同じ形を使います。
- ユーザーconfigが常に優先されます。OpenClawはCLI実行前に、plugin defaultの上に `agents.defaults.cliBackends.<id>` をマージします。
- マージ後にbackendで互換性書き換えが必要な場合は、`normalizeConfig`
  を使用してください
  （たとえば古いflag形状の正規化）。

### 排他的slot

| Method                                     | 登録するもの                       |
| ------------------------------------------ | ---------------------------------- |
| `api.registerContextEngine(id, factory)`   | context engine（一度に1つだけ有効） |
| `api.registerMemoryPromptSection(builder)` | memory prompt section builder      |
| `api.registerMemoryFlushPlan(resolver)`    | memory flush plan resolver         |
| `api.registerMemoryRuntime(runtime)`       | memory runtime adapter             |

### Memory embedding adapter

| Method                                         | 登録するもの                                |
| ---------------------------------------------- | ------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | アクティブplugin用のmemory embedding adapter |

- `registerMemoryPromptSection`、`registerMemoryFlushPlan`、および
  `registerMemoryRuntime` はmemory plugins専用です。
- `registerMemoryEmbeddingProvider` により、アクティブなmemory pluginは
  1つ以上のembedding adapter id（たとえば `openai`、`gemini`、またはカスタムの
  plugin定義id）を登録できます。
- `agents.defaults.memorySearch.provider` や
  `agents.defaults.memorySearch.fallback` のようなユーザーconfigは、
  登録されたそれらのadapter idに対して解決されます。

### Eventsとライフサイクル

| Method                                       | 役割                         |
| -------------------------------------------- | ---------------------------- |
| `api.on(hookName, handler, opts?)`           | 型付きライフサイクルhook      |
| `api.onConversationBindingResolved(handler)` | conversation binding callback |

### Hook判定セマンティクス

- `before_tool_call`: `{ block: true }` を返すと終端です。どれかのhandlerがこれを設定すると、それより低い優先度のhandlerはスキップされます。
- `before_tool_call`: `{ block: false }` を返すと、上書きではなく未決定として扱われます（`block` を省略した場合と同じ）。
- `before_install`: `{ block: true }` を返すと終端です。どれかのhandlerがこれを設定すると、それより低い優先度のhandlerはスキップされます。
- `before_install`: `{ block: false }` を返すと、上書きではなく未決定として扱われます（`block` を省略した場合と同じ）。
- `reply_dispatch`: `{ handled: true, ... }` を返すと終端です。どれかのhandlerがdispatchを引き受けると、それより低い優先度のhandlerとデフォルトのmodel dispatch経路はスキップされます。
- `message_sending`: `{ cancel: true }` を返すと終端です。どれかのhandlerがこれを設定すると、それより低い優先度のhandlerはスキップされます。
- `message_sending`: `{ cancel: false }` を返すと、上書きではなく未決定として扱われます（`cancel` を省略した場合と同じ）。

### APIオブジェクトのfield

| Field                    | Type                      | 説明                                                                                   |
| ------------------------ | ------------------------- | -------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | plugin id                                                                              |
| `api.name`               | `string`                  | 表示名                                                                                 |
| `api.version`            | `string?`                 | plugin version（任意）                                                                  |
| `api.description`        | `string?`                 | plugin説明（任意）                                                                      |
| `api.source`             | `string`                  | plugin source path                                                                     |
| `api.rootDir`            | `string?`                 | plugin rootディレクトリ（任意）                                                         |
| `api.config`             | `OpenClawConfig`          | 現在のconfig snapshot（利用可能な場合は、アクティブなインメモリruntime snapshot）       |
| `api.pluginConfig`       | `Record<string, unknown>` | `plugins.entries.<id>.config` から取得したplugin固有config                              |
| `api.runtime`            | `PluginRuntime`           | [Runtime Helpers](/ja-JP/plugins/sdk-runtime)                                                |
| `api.logger`             | `PluginLogger`            | スコープ付きlogger（`debug`、`info`、`warn`、`error`）                                  |
| `api.registrationMode`   | `PluginRegistrationMode`  | 現在のload mode。`"setup-runtime"` は完全なentry前の軽量な起動/setup期間です            |
| `api.resolvePath(input)` | `(string) => string`      | plugin root基準でpathを解決                                                             |

## 内部module規約

plugin内では、内部importにローカルbarrelファイルを使用してください:

```
my-plugin/
  api.ts            # 外部利用者向けpublic export
  runtime-api.ts    # 内部専用runtime export
  index.ts          # Plugin entry point
  setup-entry.ts    # 軽量なsetup専用entry（任意）
```

<Warning>
  production codeから `openclaw/plugin-sdk/<your-plugin>` を通じて
  自分自身のpluginをimportしてはいけません。内部importは `./api.ts` または
  `./runtime-api.ts` を経由させてください。SDK pathは外部契約専用です。
</Warning>

facade読み込みのバンドルplugin public surface（`api.ts`、`runtime-api.ts`、
`index.ts`、`setup-entry.ts`、および類似のpublic entry file）は、OpenClawがすでに動作中なら
アクティブなruntime config snapshotを優先するようになっています。
まだruntime snapshotが存在しない場合は、ディスク上で解決されたconfig fileへフォールバックします。

provider pluginsは、helperが意図的にprovider固有であり、
まだ汎用的なSDK subpathに属していない場合に、
狭いpluginローカルcontract barrelを公開することもできます。現在のバンドル例:
Anthropic providerは、Anthropicのbeta-headerや `service_tier`
ロジックを汎用 `plugin-sdk/*` contractへ昇格させる代わりに、
Claude stream helperを自身のpublic `api.ts` / `contract-api.ts` seamに保持しています。

その他の現在のバンドル例:

- `@openclaw/openai-provider`: `api.ts` はprovider builder、
  default-model helper、realtime provider builderをexport
- `@openclaw/openrouter-provider`: `api.ts` はprovider builderと
  onboarding/config helperをexport

<Warning>
  extensionのproduction codeも、`openclaw/plugin-sdk/<other-plugin>` の
  importを避けるべきです。helperが本当に共有されるべきなら、2つのpluginを結合するのではなく、
  `openclaw/plugin-sdk/speech`、`.../provider-model-shared`、または他の
  capability指向surfaceのような中立的なSDK subpathへ昇格させてください。
</Warning>

## 関連

- [Entry Points](/ja-JP/plugins/sdk-entrypoints) — `definePluginEntry` と `defineChannelPluginEntry` のオプション
- [Runtime Helpers](/ja-JP/plugins/sdk-runtime) — 完全な `api.runtime` namespaceリファレンス
- [Setup and Config](/ja-JP/plugins/sdk-setup) — packaging、manifest、config schema
- [Testing](/ja-JP/plugins/sdk-testing) — テストユーティリティとlint rule
- [SDK Migration](/ja-JP/plugins/sdk-migration) — 非推奨surfaceからの移行
- [Plugin Internals](/ja-JP/plugins/architecture) — 詳細なアーキテクチャとcapability model
