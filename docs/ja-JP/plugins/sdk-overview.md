---
read_when:
    - どのSDKサブパスからインポートするかを把握する必要があります
    - OpenClawPluginApi上のすべての登録メソッドのリファレンスが必要です
    - 特定のSDKエクスポートを調べています
sidebarTitle: SDK Overview
summary: インポートマップ、登録APIリファレンス、およびSDKアーキテクチャ
title: Plugin SDKの概要
x-i18n:
    generated_at: "2026-04-17T04:43:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: b177fdb6830f415d998a24812bc2c7db8124d3ba77b0174c9a67ac7d747f7e5a
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDKの概要

plugin SDKは、Pluginとcoreの間にある型付きコントラクトです。このページは、**何をインポートするか**と**何を登録できるか**のリファレンスです。

<Tip>
  **ハウツーガイドをお探しですか？**
  - 最初のPluginですか？ [はじめに](/ja-JP/plugins/building-plugins)から始めてください
  - Channel Pluginですか？ [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins)を参照してください
  - Provider Pluginですか？ [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins)を参照してください
</Tip>

## インポート規約

必ず特定のサブパスからインポートしてください。

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

各サブパスは、小さく自己完結したモジュールです。これにより起動を高速に保ち、循環依存の問題を防げます。channel固有のentry/buildヘルパーには、`openclaw/plugin-sdk/channel-core`を優先してください。`openclaw/plugin-sdk/core`は、より広いアンブレラサーフェスと、`buildChannelConfigSchema`のような共有ヘルパー向けに使ってください。

`openclaw/plugin-sdk/slack`、`openclaw/plugin-sdk/discord`、`openclaw/plugin-sdk/signal`、`openclaw/plugin-sdk/whatsapp`のようなprovider名ベースの便利用seamや、channelブランドのhelper seamを追加したり依存したりしないでください。bundled Pluginは、自身の`api.ts`または`runtime-api.ts` barrel内で汎用的なSDKサブパスを組み合わせるべきであり、coreはそれらのPluginローカルbarrelを使うか、本当にcross-channelな必要がある場合にのみ狭い汎用SDKコントラクトを追加すべきです。

生成されたexport mapには、`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、`plugin-sdk/zalo`、`plugin-sdk/zalo-setup`、`plugin-sdk/matrix*`のような、bundled Plugin用helper seamの小さなセットが依然として含まれています。これらのサブパスは、bundled Pluginの保守と互換性のためだけに存在します。意図的に以下の共通テーブルからは除外されており、新しいサードパーティPluginには推奨されるインポートパスではありません。

## サブパスリファレンス

目的別にグループ化した、最もよく使われるサブパスです。200以上あるサブパスの生成済み完全リストは`scripts/lib/plugin-sdk-entrypoints.json`にあります。

予約済みのbundled Plugin helper subpathも、その生成済みリストには引き続き表示されます。ドキュメントページで明示的に公開として案内されない限り、これらは実装詳細または互換性サーフェスとして扱ってください。

### Plugin entry

| Subpath                     | 主なexports                                                                                                                           |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Channel subpaths">
    | Subpath | 主なexports |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | ルート`openclaw.json` Zod schema export（`OpenClawSchema`） |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`、および`DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | 共有setupウィザードヘルパー、allowlistプロンプト、setup status builder |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | 複数アカウントconfig/action-gate helper、default-account fallback helper |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`、account-id正規化helper |
    | `plugin-sdk/account-resolution` | account lookup + default-fallback helper |
    | `plugin-sdk/account-helpers` | 狭いaccount-list/account-action helper |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | channel config schema type |
    | `plugin-sdk/telegram-command-config` | bundled-contract fallbackを備えたTelegram custom-command正規化/検証helper |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | 共有inbound route + envelope builder helper |
    | `plugin-sdk/inbound-reply-dispatch` | 共有inbound record-and-dispatch helper |
    | `plugin-sdk/messaging-targets` | target解析/マッチングhelper |
    | `plugin-sdk/outbound-media` | 共有outbound media読み込みhelper |
    | `plugin-sdk/outbound-runtime` | outbound identity/send delegate helper |
    | `plugin-sdk/thread-bindings-runtime` | thread-binding lifecycleおよびadapter helper |
    | `plugin-sdk/agent-media-payload` | legacy agent media payload builder |
    | `plugin-sdk/conversation-runtime` | conversation/thread binding、pairing、およびconfigured-binding helper |
    | `plugin-sdk/runtime-config-snapshot` | runtime config snapshot helper |
    | `plugin-sdk/runtime-group-policy` | runtime group-policy解決helper |
    | `plugin-sdk/channel-status` | 共有channel status snapshot/summary helper |
    | `plugin-sdk/channel-config-primitives` | 狭いchannel config-schema primitive |
    | `plugin-sdk/channel-config-writes` | channel config-write認可helper |
    | `plugin-sdk/channel-plugin-common` | 共有channel plugin prelude export |
    | `plugin-sdk/allowlist-config-edit` | allowlist config edit/read helper |
    | `plugin-sdk/group-access` | 共有group-access decision helper |
    | `plugin-sdk/direct-dm` | 共有direct-DM auth/guard helper |
    | `plugin-sdk/interactive-runtime` | interactive reply payload正規化/reduction helper |
    | `plugin-sdk/channel-inbound` | inbound debounce、mention matching、mention-policy helper、およびenvelope helper |
    | `plugin-sdk/channel-send-result` | reply result type |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | target解析/マッチングhelper |
    | `plugin-sdk/channel-contract` | channel contract type |
    | `plugin-sdk/channel-feedback` | feedback/reaction wiring |
    | `plugin-sdk/channel-secret-runtime` | `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment`、およびsecret target typeのような狭いsecret-contract helper |
  </Accordion>

  <Accordion title="Provider subpaths">
    | Subpath | 主なexports |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | 厳選されたlocal/self-hosted provider setup helper |
    | `plugin-sdk/self-hosted-provider-setup` | OpenAI互換のself-hosted provider setupに特化したhelper |
    | `plugin-sdk/cli-backend` | CLI backend default + watchdog定数 |
    | `plugin-sdk/provider-auth-runtime` | Provider Plugin向けruntime API key解決helper |
    | `plugin-sdk/provider-auth-api-key` | `upsertApiKeyProfile`などのAPI keyオンボーディング/profile-write helper |
    | `plugin-sdk/provider-auth-result` | 標準OAuth auth-result builder |
    | `plugin-sdk/provider-auth-login` | Provider Plugin向け共有interactive login helper |
    | `plugin-sdk/provider-env-vars` | provider auth env-var lookup helper |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`、共有replay-policy builder、provider-endpoint helper、および`normalizeNativeXaiModelId`のようなmodel-id正規化helper |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | 汎用provider HTTP/endpoint capability helper |
    | `plugin-sdk/provider-web-fetch-contract` | `enablePluginInConfig`や`WebFetchProviderPlugin`などの狭いweb-fetch config/selection contract helper |
    | `plugin-sdk/provider-web-fetch` | web-fetch provider registration/cache helper |
    | `plugin-sdk/provider-web-search-config-contract` | Plugin有効化wiringを必要としないprovider向けの狭いweb-search config/credential helper |
    | `plugin-sdk/provider-web-search-contract` | `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig`、およびスコープ付きcredential setter/getterなどの狭いweb-search config/credential contract helper |
    | `plugin-sdk/provider-web-search` | web-search provider registration/cache/runtime helper |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini schema cleanup + diagnostics、および`resolveXaiModelCompatPatch` / `applyXaiModelCompat`のようなxAI互換helper |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage`など |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`、stream wrapper type、および共有Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot wrapper helper |
    | `plugin-sdk/provider-onboard` | オンボーディングconfig patch helper |
    | `plugin-sdk/global-singleton` | process-local singleton/map/cache helper |
  </Accordion>

  <Accordion title="認証およびセキュリティのサブパス">
    | Subpath | 主なexports |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`、command registry helper、sender-authorization helper |
    | `plugin-sdk/command-status` | `buildCommandsMessagePaginated`や`buildHelpMessage`などのcommand/help message builder |
    | `plugin-sdk/approval-auth-runtime` | approver解決およびsame-chat action-auth helper |
    | `plugin-sdk/approval-client-runtime` | native exec approval profile/filter helper |
    | `plugin-sdk/approval-delivery-runtime` | native approval capability/delivery adapter |
    | `plugin-sdk/approval-gateway-runtime` | 共有approval gateway-resolution helper |
    | `plugin-sdk/approval-handler-adapter-runtime` | ホットなchannel entrypoint向けの軽量native approval adapter読み込みhelper |
    | `plugin-sdk/approval-handler-runtime` | より広範なapproval handler runtime helper。より狭いadapter/gateway seamで十分な場合はそちらを優先してください |
    | `plugin-sdk/approval-native-runtime` | native approval target + account-binding helper |
    | `plugin-sdk/approval-reply-runtime` | exec/plugin approval reply payload helper |
    | `plugin-sdk/command-auth-native` | native command auth + native session-target helper |
    | `plugin-sdk/command-detection` | 共有command detection helper |
    | `plugin-sdk/command-surface` | command-body正規化およびcommand-surface helper |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | channel/plugin secret surface向けの狭いsecret-contract collection helper |
    | `plugin-sdk/secret-ref-runtime` | secret-contract/config parsing向けの狭い`coerceSecretRef`およびSecretRef型付けhelper |
    | `plugin-sdk/security-runtime` | 共有trust、DM gating、external-content、およびsecret-collection helper |
    | `plugin-sdk/ssrf-policy` | host allowlistおよびprivate-network SSRF policy helper |
    | `plugin-sdk/ssrf-runtime` | pinned-dispatcher、SSRF-guarded fetch、およびSSRF policy helper |
    | `plugin-sdk/secret-input` | secret input parsing helper |
    | `plugin-sdk/webhook-ingress` | Webhook request/target helper |
    | `plugin-sdk/webhook-request-guards` | request body size/timeout helper |
  </Accordion>

  <Accordion title="ランタイムおよびストレージのサブパス">
    | Subpath | 主なexports |
    | --- | --- |
    | `plugin-sdk/runtime` | 広範なruntime/logging/backup/plugin-install helper |
    | `plugin-sdk/runtime-env` | 狭いruntime env、logger、timeout、retry、およびbackoff helper |
    | `plugin-sdk/channel-runtime-context` | 汎用channel runtime-context登録およびlookup helper |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | 共有plugin command/hook/http/interactive helper |
    | `plugin-sdk/hook-runtime` | 共有Webhook/internal hook pipeline helper |
    | `plugin-sdk/lazy-runtime` | `createLazyRuntimeModule`、`createLazyRuntimeMethod`、`createLazyRuntimeSurface`などのlazy runtime import/binding helper |
    | `plugin-sdk/process-runtime` | process exec helper |
    | `plugin-sdk/cli-runtime` | CLI formatting、wait、およびversion helper |
    | `plugin-sdk/gateway-runtime` | Gateway clientおよびchannel-status patch helper |
    | `plugin-sdk/config-runtime` | config load/write helper |
    | `plugin-sdk/telegram-command-config` | bundled Telegram contract surfaceが利用できない場合でも使える、Telegram command-name/description正規化およびduplicate/conflict check |
    | `plugin-sdk/approval-runtime` | exec/plugin approval helper、approval-capability builder、auth/profile helper、native routing/runtime helper |
    | `plugin-sdk/reply-runtime` | 共有inbound/reply runtime helper、chunking、dispatch、Heartbeat、reply planner |
    | `plugin-sdk/reply-dispatch-runtime` | 狭いreply dispatch/finalize helper |
    | `plugin-sdk/reply-history` | `buildHistoryContext`、`recordPendingHistoryEntry`、`clearHistoryEntriesIfEnabled`などの共有short-window reply-history helper |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | 狭いtext/markdown chunking helper |
    | `plugin-sdk/session-store-runtime` | session store path + updated-at helper |
    | `plugin-sdk/state-paths` | state/OAuth dir path helper |
    | `plugin-sdk/routing` | `resolveAgentRoute`、`buildAgentSessionKey`、`resolveDefaultAgentBoundAccountId`などのroute/session-key/account binding helper |
    | `plugin-sdk/status-helpers` | 共有channel/account status summary helper、runtime-state default、およびissue metadata helper |
    | `plugin-sdk/target-resolver-runtime` | 共有target resolver helper |
    | `plugin-sdk/string-normalization-runtime` | slug/string正規化helper |
    | `plugin-sdk/request-url` | fetch/requestライクな入力から文字列URLを抽出 |
    | `plugin-sdk/run-command` | 正規化されたstdout/stderr結果を返すtimed command runner |
    | `plugin-sdk/param-readers` | 共通tool/CLI param reader |
    | `plugin-sdk/tool-payload` | tool result objectから正規化済みpayloadを抽出 |
    | `plugin-sdk/tool-send` | tool argsからcanonical send target fieldを抽出 |
    | `plugin-sdk/temp-path` | 共有temp-download path helper |
    | `plugin-sdk/logging-core` | subsystem loggerおよびredaction helper |
    | `plugin-sdk/markdown-table-runtime` | Markdown table mode helper |
    | `plugin-sdk/json-store` | 小さなJSON state read/write helper |
    | `plugin-sdk/file-lock` | 再入可能なfile-lock helper |
    | `plugin-sdk/persistent-dedupe` | disk-backed dedupe cache helper |
    | `plugin-sdk/acp-runtime` | ACP runtime/sessionおよびreply-dispatch helper |
    | `plugin-sdk/agent-config-primitives` | 狭いagent runtime config-schema primitive |
    | `plugin-sdk/boolean-param` | 緩いboolean param reader |
    | `plugin-sdk/dangerous-name-runtime` | dangerous-name matching解決helper |
    | `plugin-sdk/device-bootstrap` | device bootstrapおよびpairing token helper |
    | `plugin-sdk/extension-shared` | 共有passive-channel、status、およびambient proxy helper primitive |
    | `plugin-sdk/models-provider-runtime` | `/models` command/provider reply helper |
    | `plugin-sdk/skill-commands-runtime` | Skills command listing helper |
    | `plugin-sdk/native-command-registry` | native command registry/build/serialize helper |
    | `plugin-sdk/agent-harness` | 低レベルagent harness向けの実験的trusted-plugin surface: harness type、active-run steer/abort helper、OpenClaw tool bridge helper、およびattempt result utility |
    | `plugin-sdk/provider-zai-endpoint` | Z.A.I endpoint detection helper |
    | `plugin-sdk/infra-runtime` | system event/Heartbeat helper |
    | `plugin-sdk/collection-runtime` | 小さなbounded cache helper |
    | `plugin-sdk/diagnostic-runtime` | diagnostic flagおよびevent helper |
    | `plugin-sdk/error-runtime` | error graph、formatting、共有error classification helper、`isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | wrapped fetch、proxy、およびpinned lookup helper |
    | `plugin-sdk/host-runtime` | hostnameおよびSCP host正規化helper |
    | `plugin-sdk/retry-runtime` | retry configおよびretry runner helper |
    | `plugin-sdk/agent-runtime` | agent dir/identity/workspace helper |
    | `plugin-sdk/directory-runtime` | config-backed directory query/dedup |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Capabilityおよびテストのサブパス">
    | Subpath | 主なexports |
    | --- | --- |
    | `plugin-sdk/media-runtime` | media payload builderに加え、共有media fetch/transform/store helper |
    | `plugin-sdk/media-generation-runtime` | 共有media-generation failover helper、candidate selection、およびmissing-model messaging |
    | `plugin-sdk/media-understanding` | media understanding provider typeおよびprovider向けimage/audio helper export |
    | `plugin-sdk/text-runtime` | assistant-visible-text stripping、markdown render/chunking/table helper、redaction helper、directive-tag helper、安全なtext utilityなどの共有text/markdown/logging helper |
    | `plugin-sdk/text-chunking` | outbound text chunking helper |
    | `plugin-sdk/speech` | speech provider typeおよびprovider向けdirective、registry、validation helper |
    | `plugin-sdk/speech-core` | 共有speech provider type、registry、directive、および正規化helper |
    | `plugin-sdk/realtime-transcription` | realtime transcription provider typeおよびregistry helper |
    | `plugin-sdk/realtime-voice` | realtime voice provider typeおよびregistry helper |
    | `plugin-sdk/image-generation` | image generation provider type |
    | `plugin-sdk/image-generation-core` | 共有image-generation type、failover、auth、およびregistry helper |
    | `plugin-sdk/music-generation` | music generation provider/request/result type |
    | `plugin-sdk/music-generation-core` | 共有music-generation type、failover helper、provider lookup、およびmodel-ref parsing |
    | `plugin-sdk/video-generation` | video generation provider/request/result type |
    | `plugin-sdk/video-generation-core` | 共有video-generation type、failover helper、provider lookup、およびmodel-ref parsing |
    | `plugin-sdk/webhook-targets` | Webhook target registryおよびroute-install helper |
    | `plugin-sdk/webhook-path` | Webhook path正規化helper |
    | `plugin-sdk/web-media` | 共有remote/local media読み込みhelper |
    | `plugin-sdk/zod` | Plugin SDK利用者向けにre-exportされた`zod` |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="メモリのサブパス">
    | Subpath | 主なexports |
    | --- | --- |
    | `plugin-sdk/memory-core` | manager/config/file/CLI helper向けのbundled memory-core helper surface |
    | `plugin-sdk/memory-core-engine-runtime` | memory index/search runtime facade |
    | `plugin-sdk/memory-core-host-engine-foundation` | memory host foundation engine export |
    | `plugin-sdk/memory-core-host-engine-embeddings` | memory host embedding contract、registry access、local provider、および汎用batch/remote helper |
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
    | `plugin-sdk/memory-host-core` | memory host core runtime helperのvendor-neutral alias |
    | `plugin-sdk/memory-host-events` | memory host event journal helperのvendor-neutral alias |
    | `plugin-sdk/memory-host-files` | memory host file/runtime helperのvendor-neutral alias |
    | `plugin-sdk/memory-host-markdown` | memory隣接Plugin向けの共有managed-markdown helper |
    | `plugin-sdk/memory-host-search` | search-manager access向けのActive Memory runtime facade |
    | `plugin-sdk/memory-host-status` | memory host status helperのvendor-neutral alias |
    | `plugin-sdk/memory-lancedb` | bundled memory-lancedb helper surface |
  </Accordion>

  <Accordion title="予約済みbundled-helperサブパス">
    | Family | 現在のサブパス | 想定用途 |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | bundled browser Pluginサポートhelper（`browser-support`は互換性barrelのままです） |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | bundled Matrix helper/runtime surface |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | bundled LINE helper/runtime surface |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | bundled IRC helper surface |
    | channel固有helper | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | bundled channel互換性/helper seam |
    | 認証/Plugin固有helper | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | bundled feature/Plugin helper seam。`plugin-sdk/github-copilot-token`は現在`DEFAULT_COPILOT_API_BASE_URL`、`deriveCopilotApiBaseUrlFromToken`、`resolveCopilotApiToken`をexportします |
  </Accordion>
</AccordionGroup>

## 登録API

`register(api)`コールバックは、次のメソッドを持つ`OpenClawPluginApi`オブジェクトを受け取ります。

### Capability登録

| Method                                           | 登録するもの                        |
| ------------------------------------------------ | ----------------------------------- |
| `api.registerProvider(...)`                      | テキスト推論（LLM）                 |
| `api.registerAgentHarness(...)`                  | 実験的な低レベルagent executor      |
| `api.registerCliBackend(...)`                    | ローカルCLI推論backend              |
| `api.registerChannel(...)`                       | メッセージングchannel               |
| `api.registerSpeechProvider(...)`                | text-to-speech / STT synthesis      |
| `api.registerRealtimeTranscriptionProvider(...)` | ストリーミングリアルタイム文字起こし |
| `api.registerRealtimeVoiceProvider(...)`         | 双方向リアルタイム音声セッション    |
| `api.registerMediaUnderstandingProvider(...)`    | 画像/音声/動画解析                  |
| `api.registerImageGenerationProvider(...)`       | 画像生成                            |
| `api.registerMusicGenerationProvider(...)`       | 音楽生成                            |
| `api.registerVideoGenerationProvider(...)`       | 動画生成                            |
| `api.registerWebFetchProvider(...)`              | Web fetch / scrape provider         |
| `api.registerWebSearchProvider(...)`             | Web検索                             |

### Toolsとcommands

| Method                          | 登録するもの                                |
| ------------------------------- | ------------------------------------------- |
| `api.registerTool(tool, opts?)` | agent tool（必須または`{ optional: true }`） |
| `api.registerCommand(def)`      | カスタムcommand（LLMをバイパス）            |

### インフラストラクチャ

| Method                                         | 登録するもの                          |
| ---------------------------------------------- | ------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | イベントhook                          |
| `api.registerHttpRoute(params)`                | Gateway HTTP endpoint                 |
| `api.registerGatewayMethod(name, handler)`     | Gateway RPC method                    |
| `api.registerCli(registrar, opts?)`            | CLIサブコマンド                       |
| `api.registerService(service)`                 | バックグラウンドサービス              |
| `api.registerInteractiveHandler(registration)` | interactive handler                   |
| `api.registerMemoryPromptSupplement(builder)`  | 加算的なmemory隣接prompt section      |
| `api.registerMemoryCorpusSupplement(adapter)`  | 加算的なmemory search/read corpus     |

予約済みのcore admin namespace（`config.*`、`exec.approvals.*`、`wizard.*`、`update.*`）は、Pluginがより狭いGateway method scopeを割り当てようとしても、常に`operator.admin`のままです。Plugin所有のmethodには、Plugin固有のprefixを優先してください。

### CLI登録メタデータ

`api.registerCli(registrar, opts?)`は、2種類のトップレベルメタデータを受け取ります。

- `commands`: registrarが所有する明示的なcommand root
- `descriptors`: ルートCLI help、routing、およびlazy Plugin CLI登録に使われるparse-time command descriptor

Plugin commandを通常のルートCLIパスでlazy-loadedのままにしたい場合は、そのregistrarが公開するすべてのトップレベルcommand rootをカバーする`descriptors`を指定してください。

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
        description: "Matrixアカウント、認証、デバイス、およびprofile stateを管理する",
        hasSubcommands: true,
      },
    ],
  },
);
```

`commands`単体を使うのは、lazyなルートCLI登録が不要な場合だけにしてください。そのeager互換パスは引き続きサポートされていますが、parse-time lazy loadingのためのdescriptor-backed placeholderはインストールされません。

### CLI backend登録

`api.registerCliBackend(...)`を使うと、Pluginが`codex-cli`のようなローカルAI CLI backendのdefault configを所有できます。

- backendの`id`は、`codex-cli/gpt-5`のようなmodel ref内のprovider prefixになります。
- backendの`config`は、`agents.defaults.cliBackends.<id>`と同じ形を使います。
- ユーザーconfigが引き続き優先されます。OpenClawは、CLIを実行する前に、Plugin defaultの上に`agents.defaults.cliBackends.<id>`をマージします。
- マージ後にbackendが互換性書き換えを必要とする場合（たとえば古いflag形状の正規化など）は、`normalizeConfig`を使ってください。

### 排他的スロット

| Method                                     | 登録するもの                                                                                                                                               |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Context engine（一度に1つだけ有効）。`assemble()`コールバックは`availableTools`と`citationsMode`を受け取るため、engineはそれに合わせてprompt追加を調整できます。 |
| `api.registerMemoryCapability(capability)` | 統一memory capability                                                                                                                                      |
| `api.registerMemoryPromptSection(builder)` | memory prompt section builder                                                                                                                              |
| `api.registerMemoryFlushPlan(resolver)`    | memory flush plan resolver                                                                                                                                 |
| `api.registerMemoryRuntime(runtime)`       | memory runtime adapter                                                                                                                                     |

### Memory embedding adapter

| Method                                         | 登録するもの                                 |
| ---------------------------------------------- | -------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | アクティブなPlugin向けmemory embedding adapter |

- `registerMemoryCapability`は、推奨される排他的memory-Plugin APIです。
- `registerMemoryCapability`は、companion Pluginが特定のmemory Pluginのprivate layoutに入り込む代わりに、`openclaw/plugin-sdk/memory-host-core`を通じてexportされたmemory artifactを利用できるよう、`publicArtifacts.listArtifacts(...)`を公開することもできます。
- `registerMemoryPromptSection`、`registerMemoryFlushPlan`、および`registerMemoryRuntime`は、legacy互換の排他的memory-Plugin APIです。
- `registerMemoryEmbeddingProvider`を使うと、アクティブmemory Pluginは1つ以上のembedding adapter id（たとえば`openai`、`gemini`、またはPlugin定義のカスタムid）を登録できます。
- `agents.defaults.memorySearch.provider`や`agents.defaults.memorySearch.fallback`のようなユーザーconfigは、それらの登録済みadapter idに対して解決されます。

### イベントとライフサイクル

| Method                                       | 動作内容                      |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | 型付きライフサイクルhook      |
| `api.onConversationBindingResolved(handler)` | conversation bindingコールバック |

### Hook決定セマンティクス

- `before_tool_call`: `{ block: true }`を返すと終端です。いずれかのhandlerがこれを設定すると、より低い優先度のhandlerはスキップされます。
- `before_tool_call`: `{ block: false }`を返しても決定なしとして扱われます（`block`を省略した場合と同じ）であり、オーバーライドではありません。
- `before_install`: `{ block: true }`を返すと終端です。いずれかのhandlerがこれを設定すると、より低い優先度のhandlerはスキップされます。
- `before_install`: `{ block: false }`を返しても決定なしとして扱われます（`block`を省略した場合と同じ）であり、オーバーライドではありません。
- `reply_dispatch`: `{ handled: true, ... }`を返すと終端です。いずれかのhandlerがdispatchを引き受けると、より低い優先度のhandlerとデフォルトのmodel dispatch pathはスキップされます。
- `message_sending`: `{ cancel: true }`を返すと終端です。いずれかのhandlerがこれを設定すると、より低い優先度のhandlerはスキップされます。
- `message_sending`: `{ cancel: false }`を返しても決定なしとして扱われます（`cancel`を省略した場合と同じ）であり、オーバーライドではありません。

### APIオブジェクトのフィールド

| Field                    | Type                      | 説明                                                                                         |
| ------------------------ | ------------------------- | -------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | Plugin id                                                                                    |
| `api.name`               | `string`                  | 表示名                                                                                       |
| `api.version`            | `string?`                 | Pluginバージョン（任意）                                                                     |
| `api.description`        | `string?`                 | Pluginの説明（任意）                                                                         |
| `api.source`             | `string`                  | Pluginソースパス                                                                             |
| `api.rootDir`            | `string?`                 | Pluginルートディレクトリ（任意）                                                             |
| `api.config`             | `OpenClawConfig`          | 現在のconfigスナップショット（利用可能な場合は、アクティブなインメモリruntimeスナップショット） |
| `api.pluginConfig`       | `Record<string, unknown>` | `plugins.entries.<id>.config`からのPlugin固有config                                          |
| `api.runtime`            | `PluginRuntime`           | [ランタイムヘルパー](/ja-JP/plugins/sdk-runtime)                                                   |
| `api.logger`             | `PluginLogger`            | スコープ付きlogger（`debug`、`info`、`warn`、`error`）                                       |
| `api.registrationMode`   | `PluginRegistrationMode`  | 現在のload mode。`"setup-runtime"`は、軽量なfull-entry前のstartup/setupウィンドウです         |
| `api.resolvePath(input)` | `(string) => string`      | Pluginルートからの相対パスを解決                                                             |

## 内部モジュール規約

Plugin内では、内部インポートにローカルbarrelファイルを使用してください。

```
my-plugin/
  api.ts            # 外部利用者向けの公開export
  runtime-api.ts    # 内部専用runtime export
  index.ts          # Plugin entry point
  setup-entry.ts    # 軽量なsetup専用entry（任意）
```

<Warning>
  本番コードから`openclaw/plugin-sdk/<your-plugin>`経由で自分自身のPluginを
  インポートしてはいけません。内部インポートは`./api.ts`または
  `./runtime-api.ts`を経由させてください。SDKパスは外部コントラクト専用です。
</Warning>

facade読み込みされたbundled Pluginの公開surface（`api.ts`、`runtime-api.ts`、`index.ts`、`setup-entry.ts`、および同様の公開entryファイル）は、OpenClawがすでに実行中であれば、現在はアクティブなruntime configスナップショットを優先します。まだruntimeスナップショットが存在しない場合は、ディスク上で解決されたconfigファイルにフォールバックします。

Provider Pluginは、helperが意図的にprovider固有で、まだ汎用SDKサブパスに属していない場合、狭いPluginローカルのcontract barrelを公開することもできます。現在のbundled例として、Anthropic providerは、Anthropic beta-headerや`service_tier`ロジックを汎用`plugin-sdk/*`コントラクトに昇格させる代わりに、Claude stream helperを自身の公開`api.ts` / `contract-api.ts` seamに保持しています。

その他の現在のbundled例:

- `@openclaw/openai-provider`: `api.ts`はprovider builder、default-model helper、およびrealtime provider builderをexportします
- `@openclaw/openrouter-provider`: `api.ts`はprovider builderに加えて、オンボーディング/config helperをexportします

<Warning>
  extensionの本番コードでも、`openclaw/plugin-sdk/<other-plugin>`の
  インポートは避けるべきです。helperが本当に共有されるべきなら、
  2つのPluginを結合させるのではなく、`openclaw/plugin-sdk/speech`、
  `.../provider-model-shared`、または別のcapability指向surfaceのような
  中立的なSDKサブパスに昇格させてください。
</Warning>

## 関連

- [Entry Points](/ja-JP/plugins/sdk-entrypoints) — `definePluginEntry`および`defineChannelPluginEntry`のオプション
- [ランタイムヘルパー](/ja-JP/plugins/sdk-runtime) — 完全な`api.runtime`名前空間リファレンス
- [Setup and Config](/ja-JP/plugins/sdk-setup) — パッケージング、manifest、config schema
- [Testing](/ja-JP/plugins/sdk-testing) — テストユーティリティとlintルール
- [SDK Migration](/ja-JP/plugins/sdk-migration) — 非推奨surfaceからの移行
- [Plugin Internals](/ja-JP/plugins/architecture) — 詳細なアーキテクチャとcapability model
