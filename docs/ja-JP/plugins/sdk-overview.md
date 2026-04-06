---
read_when:
    - どの SDK subpath から import するべきか知りたい場合
    - OpenClawPluginApi 上のすべての registration method のリファレンスが欲しい場合
    - 特定の SDK export を調べている場合
sidebarTitle: SDK Overview
summary: import map、registration API リファレンス、SDK アーキテクチャ
title: Plugin SDK の概要
x-i18n:
    generated_at: "2026-04-06T03:11:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: d801641f26f39dc21490d2a69a337ff1affb147141360916b8b58a267e9f822a
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDK の概要

plugin SDK は、plugins と core の間の型付き契約です。このページは、
**何を import するか** と **何を登録できるか** のリファレンスです。

<Tip>
  **ハウツーガイドを探していますか？**
  - 最初の plugin ですか？ [はじめに](/ja-JP/plugins/building-plugins) から始めてください
  - channel plugin ですか？ [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) を参照してください
  - provider plugin ですか？ [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) を参照してください
</Tip>

## import 規約

必ず特定の subpath から import してください:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

各 subpath は小さく自己完結した module です。これにより起動を高速に保ち、
循環依存の問題を防げます。channel 固有の entry/build helper には、
`openclaw/plugin-sdk/channel-core` を優先して使用してください。より広い umbrella surface と
`buildChannelConfigSchema` のような共有 helper には
`openclaw/plugin-sdk/core` を使ってください。

`openclaw/plugin-sdk/slack`、`openclaw/plugin-sdk/discord`、
`openclaw/plugin-sdk/signal`、`openclaw/plugin-sdk/whatsapp` のような
provider 名付き convenience seam や channel ブランド付き helper seam を追加したり、
依存したりしないでください。バンドル plugin は汎用的な
SDK subpath を自分自身の `api.ts` または `runtime-api.ts` barrel の中で構成すべきであり、core はそれらの plugin ローカル barrel を使うか、
必要が本当に channel 横断である場合のみ、狭く汎用的な SDK
契約を追加するべきです。

生成された export map には、`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、
`plugin-sdk/zalo`、`plugin-sdk/zalo-setup`、`plugin-sdk/matrix*` など、
少数のバンドル plugin helper seam がまだ含まれています。これらの
subpath は、バンドル plugin の保守と互換性のためだけに存在します。以下の一般的な表では意図的に省略されており、新しいサードパーティ plugin に推奨される import path ではありません。

## subpath リファレンス

目的別にグループ化した、最もよく使われる subpath です。200 を超える
subpath の生成済み完全一覧は `scripts/lib/plugin-sdk-entrypoints.json` にあります。

予約済みのバンドル plugin helper subpath は、その生成一覧には引き続き表示されます。
ドキュメントページで明示的に公開 API として案内されていない限り、これらは
実装詳細/互換性 surface として扱ってください。

### Plugin entry

| Subpath                     | 主な export                                                                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                   |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                      |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                     |

<AccordionGroup>
  <Accordion title="Channel subpaths">
    | Subpath | 主な export |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | ルート `openclaw.json` Zod スキーマ export（`OpenClawSchema`） |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`、および `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | 共有 setup wizard helper、allowlist prompt、setup status builder |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | マルチアカウント設定/アクションゲート helper、デフォルトアカウントフォールバック helper |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`、account-id 正規化 helper |
    | `plugin-sdk/account-resolution` | アカウント検索 + デフォルトフォールバック helper |
    | `plugin-sdk/account-helpers` | 狭い account-list/account-action helper |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | channel 設定スキーマ型 |
    | `plugin-sdk/telegram-command-config` | バンドル契約フォールバック付き Telegram カスタムコマンド正規化/検証 helper |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | 共有 inbound route + envelope builder helper |
    | `plugin-sdk/inbound-reply-dispatch` | 共有 inbound record-and-dispatch helper |
    | `plugin-sdk/messaging-targets` | ターゲット解析/一致 helper |
    | `plugin-sdk/outbound-media` | 共有 outbound media 読み込み helper |
    | `plugin-sdk/outbound-runtime` | outbound identity/send delegate helper |
    | `plugin-sdk/thread-bindings-runtime` | thread-binding lifecycle と adapter helper |
    | `plugin-sdk/agent-media-payload` | レガシー agent media payload builder |
    | `plugin-sdk/conversation-runtime` | 会話/thread binding、pairing、設定済み binding helper |
    | `plugin-sdk/runtime-config-snapshot` | runtime config snapshot helper |
    | `plugin-sdk/runtime-group-policy` | runtime group-policy 解決 helper |
    | `plugin-sdk/channel-status` | 共有 channel status snapshot/summary helper |
    | `plugin-sdk/channel-config-primitives` | 狭い channel config-schema primitives |
    | `plugin-sdk/channel-config-writes` | channel config-write 認可 helper |
    | `plugin-sdk/channel-plugin-common` | 共有 channel plugin prelude export |
    | `plugin-sdk/allowlist-config-edit` | allowlist 設定編集/読み取り helper |
    | `plugin-sdk/group-access` | 共有 group-access 決定 helper |
    | `plugin-sdk/direct-dm` | 共有 direct-DM auth/guard helper |
    | `plugin-sdk/interactive-runtime` | インタラクティブ reply payload 正規化/reduction helper |
    | `plugin-sdk/channel-inbound` | debounce、mention 一致、envelope helper |
    | `plugin-sdk/channel-send-result` | reply result 型 |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | ターゲット解析/一致 helper |
    | `plugin-sdk/channel-contract` | channel 契約型 |
    | `plugin-sdk/channel-feedback` | feedback/reaction 配線 |
  </Accordion>

  <Accordion title="Provider subpaths">
    | Subpath | 主な export |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | 厳選された local/self-hosted provider setup helper |
    | `plugin-sdk/self-hosted-provider-setup` | OpenAI 互換 self-hosted provider 向けの集中的な setup helper |
    | `plugin-sdk/provider-auth-runtime` | provider plugins 向け runtime API-key 解決 helper |
    | `plugin-sdk/provider-auth-api-key` | API-key オンボーディング/profile-write helper |
    | `plugin-sdk/provider-auth-result` | 標準 OAuth auth-result builder |
    | `plugin-sdk/provider-auth-login` | provider plugins 向け共有対話ログイン helper |
    | `plugin-sdk/provider-env-vars` | provider auth env-var 検索 helper |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`、共有 replay-policy builder、provider-endpoint helper、および `normalizeNativeXaiModelId` のような model-id 正規化 helper |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | 汎用 provider HTTP/endpoint capability helper |
    | `plugin-sdk/provider-web-fetch` | web-fetch provider 登録/cache helper |
    | `plugin-sdk/provider-web-search` | web-search provider 登録/cache/config helper |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini スキーマクリーンアップ + diagnostics、および `resolveXaiModelCompatPatch` / `applyXaiModelCompat` のような xAI compat helper |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` など |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`、stream wrapper 型、および共有 Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot wrapper helper |
    | `plugin-sdk/provider-onboard` | オンボーディング設定パッチ helper |
    | `plugin-sdk/global-singleton` | プロセスローカル singleton/map/cache helper |
  </Accordion>

  <Accordion title="認証とセキュリティの subpaths">
    | Subpath | 主な export |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, command registry helper, sender-authorization helper |
    | `plugin-sdk/approval-auth-runtime` | approver 解決と same-chat action-auth helper |
    | `plugin-sdk/approval-client-runtime` | ネイティブ exec approval profile/filter helper |
    | `plugin-sdk/approval-delivery-runtime` | ネイティブ approval capability/delivery adapter |
    | `plugin-sdk/approval-native-runtime` | ネイティブ approval target + account-binding helper |
    | `plugin-sdk/approval-reply-runtime` | exec/plugin approval reply payload helper |
    | `plugin-sdk/command-auth-native` | ネイティブ command auth + ネイティブ session-target helper |
    | `plugin-sdk/command-detection` | 共有 command 検出 helper |
    | `plugin-sdk/command-surface` | command-body 正規化と command-surface helper |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/security-runtime` | 共有 trust、DM gating、external-content、secret-collection helper |
    | `plugin-sdk/ssrf-policy` | ホスト allowlist とプライベートネットワーク SSRF policy helper |
    | `plugin-sdk/ssrf-runtime` | pinned-dispatcher、SSRF 保護付き fetch、および SSRF policy helper |
    | `plugin-sdk/secret-input` | secret input 解析 helper |
    | `plugin-sdk/webhook-ingress` | webhook request/target helper |
    | `plugin-sdk/webhook-request-guards` | request body サイズ/timeout helper |
  </Accordion>

  <Accordion title="Runtime とストレージの subpaths">
    | Subpath | 主な export |
    | --- | --- |
    | `plugin-sdk/runtime` | 広範な runtime/logging/backup/plugin-install helper |
    | `plugin-sdk/runtime-env` | 狭い runtime env、logger、timeout、retry、backoff helper |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | 共有 plugin command/hook/http/interactive helper |
    | `plugin-sdk/hook-runtime` | 共有 webhook/internal hook pipeline helper |
    | `plugin-sdk/lazy-runtime` | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeSurface` のような lazy runtime import/binding helper |
    | `plugin-sdk/process-runtime` | process exec helper |
    | `plugin-sdk/cli-runtime` | CLI formatting、wait、version helper |
    | `plugin-sdk/gateway-runtime` | Gateway client と channel-status patch helper |
    | `plugin-sdk/config-runtime` | 設定 load/write helper |
    | `plugin-sdk/telegram-command-config` | バンドル Telegram 契約 surface が利用できない場合でも、Telegram command-name/description の正規化と重複/競合チェック |
    | `plugin-sdk/approval-runtime` | exec/plugin approval helper、approval-capability builder、auth/profile helper、ネイティブルーティング/runtime helper |
    | `plugin-sdk/reply-runtime` | 共有 inbound/reply runtime helper、chunking、dispatch、heartbeat、reply planner |
    | `plugin-sdk/reply-dispatch-runtime` | 狭い reply dispatch/finalize helper |
    | `plugin-sdk/reply-history` | `buildHistoryContext`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` などの共有 short-window reply-history helper |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | 狭い text/markdown chunking helper |
    | `plugin-sdk/session-store-runtime` | session store path + updated-at helper |
    | `plugin-sdk/state-paths` | state/OAuth dir path helper |
    | `plugin-sdk/routing` | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId` などの route/session-key/account binding helper |
    | `plugin-sdk/status-helpers` | 共有 channel/account status summary helper、runtime-state defaults、issue metadata helper |
    | `plugin-sdk/target-resolver-runtime` | 共有 target resolver helper |
    | `plugin-sdk/string-normalization-runtime` | slug/string 正規化 helper |
    | `plugin-sdk/request-url` | fetch/request 風 input から文字列 URL を抽出 |
    | `plugin-sdk/run-command` | 正規化された stdout/stderr result を返す timed command runner |
    | `plugin-sdk/param-readers` | 共通 tool/CLI param reader |
    | `plugin-sdk/tool-send` | tool args から正規の send target field を抽出 |
    | `plugin-sdk/temp-path` | 共有 temp-download path helper |
    | `plugin-sdk/logging-core` | subsystem logger と redaction helper |
    | `plugin-sdk/markdown-table-runtime` | Markdown table mode helper |
    | `plugin-sdk/json-store` | 小規模 JSON state 読み書き helper |
    | `plugin-sdk/file-lock` | 再入可能な file-lock helper |
    | `plugin-sdk/persistent-dedupe` | ディスクバックの dedupe cache helper |
    | `plugin-sdk/acp-runtime` | ACP runtime/session と reply-dispatch helper |
    | `plugin-sdk/agent-config-primitives` | 狭い agent runtime config-schema primitives |
    | `plugin-sdk/boolean-param` | 緩い boolean param reader |
    | `plugin-sdk/dangerous-name-runtime` | dangerous-name 一致解決 helper |
    | `plugin-sdk/device-bootstrap` | デバイス bootstrap と pairing token helper |
    | `plugin-sdk/extension-shared` | 共有 passive-channel と status helper primitives |
    | `plugin-sdk/models-provider-runtime` | `/models` command/provider reply helper |
    | `plugin-sdk/skill-commands-runtime` | skill command 一覧 helper |
    | `plugin-sdk/native-command-registry` | ネイティブ command registry/build/serialize helper |
    | `plugin-sdk/provider-zai-endpoint` | Z.A.I endpoint 検出 helper |
    | `plugin-sdk/infra-runtime` | system event/heartbeat helper |
    | `plugin-sdk/collection-runtime` | 小規模な上限付き cache helper |
    | `plugin-sdk/diagnostic-runtime` | diagnostic flag と event helper |
    | `plugin-sdk/error-runtime` | error graph、formatting、共有 error 分類 helper、`isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | wrapped fetch、proxy、pinned lookup helper |
    | `plugin-sdk/host-runtime` | ホスト名と SCP ホスト正規化 helper |
    | `plugin-sdk/retry-runtime` | retry 設定と retry runner helper |
    | `plugin-sdk/agent-runtime` | agent dir/identity/workspace helper |
    | `plugin-sdk/directory-runtime` | 設定ベース directory query/dedup |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Capability とテストの subpaths">
    | Subpath | 主な export |
    | --- | --- |
    | `plugin-sdk/media-runtime` | 共有 media fetch/transform/store helper と media payload builder |
    | `plugin-sdk/media-understanding` | media understanding provider 型と provider 向け image/audio helper export |
    | `plugin-sdk/text-runtime` | assistant-visible-text の除去、markdown render/chunking/table helper、redaction helper、directive-tag helper、安全な text utility などの共有 text/markdown/logging helper |
    | `plugin-sdk/text-chunking` | outbound text chunking helper |
    | `plugin-sdk/speech` | speech provider 型と provider 向け directive、registry、validation helper |
    | `plugin-sdk/speech-core` | 共有 speech provider 型、registry、directive、正規化 helper |
    | `plugin-sdk/realtime-transcription` | realtime transcription provider 型と registry helper |
    | `plugin-sdk/realtime-voice` | realtime voice provider 型と registry helper |
    | `plugin-sdk/image-generation` | image generation provider 型 |
    | `plugin-sdk/image-generation-core` | 共有 image-generation 型、failover、auth、registry helper |
    | `plugin-sdk/music-generation` | music generation provider/request/result 型 |
    | `plugin-sdk/music-generation-core` | 共有 music-generation 型、failover helper、provider lookup、model-ref 解析 |
    | `plugin-sdk/video-generation` | video generation provider/request/result 型 |
    | `plugin-sdk/video-generation-core` | 共有 video-generation 型、failover helper、provider lookup、model-ref 解析 |
    | `plugin-sdk/webhook-targets` | webhook target registry と route-install helper |
    | `plugin-sdk/webhook-path` | webhook path 正規化 helper |
    | `plugin-sdk/web-media` | 共有 remote/local media 読み込み helper |
    | `plugin-sdk/zod` | plugin SDK 利用者向けに再 export された `zod` |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Memory subpaths">
    | Subpath | 主な export |
    | --- | --- |
    | `plugin-sdk/memory-core` | manager/config/file/CLI helper 向けバンドル memory-core helper surface |
    | `plugin-sdk/memory-core-engine-runtime` | memory index/search runtime facade |
    | `plugin-sdk/memory-core-host-engine-foundation` | memory host foundation engine export |
    | `plugin-sdk/memory-core-host-engine-embeddings` | memory host embedding engine export |
    | `plugin-sdk/memory-core-host-engine-qmd` | memory host QMD engine export |
    | `plugin-sdk/memory-core-host-engine-storage` | memory host storage engine export |
    | `plugin-sdk/memory-core-host-multimodal` | memory host multimodal helper |
    | `plugin-sdk/memory-core-host-query` | memory host query helper |
    | `plugin-sdk/memory-core-host-secret` | memory host secret helper |
    | `plugin-sdk/memory-core-host-status` | memory host status helper |
    | `plugin-sdk/memory-core-host-runtime-cli` | memory host CLI runtime helper |
    | `plugin-sdk/memory-core-host-runtime-core` | memory host core runtime helper |
    | `plugin-sdk/memory-core-host-runtime-files` | memory host file/runtime helper |
    | `plugin-sdk/memory-lancedb` | バンドル memory-lancedb helper surface |
  </Accordion>

  <Accordion title="予約済みバンドル helper subpaths">
    | Family | 現在の subpaths | 想定用途 |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | バンドル browser plugin サポート helper（`browser-support` は互換性 barrel のままです） |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | バンドル Matrix helper/runtime surface |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | バンドル LINE helper/runtime surface |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | バンドル IRC helper surface |
    | channel 固有 helper | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | バンドル channel の互換性/helper seam |
    | auth/plugin 固有 helper | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | バンドル機能/plugin helper seam。`plugin-sdk/github-copilot-token` は現在 `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken`, `resolveCopilotApiToken` を export します |
  </Accordion>
</AccordionGroup>

## Registration API

`register(api)` コールバックは、次の method を持つ `OpenClawPluginApi` オブジェクトを受け取ります:

### Capability の登録

| Method                                           | 登録するもの                    |
| ------------------------------------------------ | ------------------------------- |
| `api.registerProvider(...)`                      | text inference（LLM）           |
| `api.registerChannel(...)`                       | メッセージング channel          |
| `api.registerSpeechProvider(...)`                | text-to-speech / STT synthesis  |
| `api.registerRealtimeTranscriptionProvider(...)` | ストリーミング realtime transcription |
| `api.registerRealtimeVoiceProvider(...)`         | duplex realtime voice sessions  |
| `api.registerMediaUnderstandingProvider(...)`    | 画像/音声/動画の解析            |
| `api.registerImageGenerationProvider(...)`       | 画像生成                        |
| `api.registerMusicGenerationProvider(...)`       | 音楽生成                        |
| `api.registerVideoGenerationProvider(...)`       | 動画生成                        |
| `api.registerWebFetchProvider(...)`              | Web fetch / スクレイプ provider |
| `api.registerWebSearchProvider(...)`             | Web search                      |

### Tools と commands

| Method                          | 登録するもの                                   |
| ------------------------------- | ---------------------------------------------- |
| `api.registerTool(tool, opts?)` | agent tool（必須、または `{ optional: true }`） |
| `api.registerCommand(def)`      | カスタム command（LLM を経由しない）           |

### インフラ

| Method                                         | 登録するもの          |
| ---------------------------------------------- | --------------------- |
| `api.registerHook(events, handler, opts?)`     | event hook            |
| `api.registerHttpRoute(params)`                | Gateway HTTP endpoint |
| `api.registerGatewayMethod(name, handler)`     | Gateway RPC method    |
| `api.registerCli(registrar, opts?)`            | CLI subcommand        |
| `api.registerService(service)`                 | バックグラウンド service |
| `api.registerInteractiveHandler(registration)` | インタラクティブ handler |

予約済みコア管理 namespace（`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`）は、plugin がより狭い gateway method scope を割り当てようとしても、
常に `operator.admin` のままです。plugin 所有の method には
plugin 固有の prefix を優先してください。

### CLI 登録メタデータ

`api.registerCli(registrar, opts?)` は 2 種類のトップレベルメタデータを受け取ります:

- `commands`: registrar が所有する明示的な command root
- `descriptors`: ルート CLI ヘルプ、ルーティング、遅延 plugin CLI 登録に使う parse-time command descriptor

plugin command を通常のルート CLI パスで遅延ロードのまま保ちたい場合は、
その registrar が公開するすべてのトップレベル command root をカバーする
`descriptors` を指定してください。

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

通常のルート CLI 登録で遅延ロードが不要な場合にのみ、`commands` 単独を使ってください。
その eager 互換パスは引き続きサポートされますが、parse-time 遅延ロード用の
descriptor ベース placeholder はインストールされません。

### 排他的スロット

| Method                                     | 登録するもの                          |
| ------------------------------------------ | ------------------------------------- |
| `api.registerContextEngine(id, factory)`   | context engine（一度に 1 つだけ有効） |
| `api.registerMemoryPromptSection(builder)` | memory prompt section builder         |
| `api.registerMemoryFlushPlan(resolver)`    | memory flush plan resolver            |
| `api.registerMemoryRuntime(runtime)`       | memory runtime adapter                |

### Memory 埋め込み adapter

| Method                                         | 登録するもの                                  |
| ---------------------------------------------- | --------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | アクティブ plugin 用の memory embedding adapter |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan`,
  `registerMemoryRuntime` は memory plugins 専用です。
- `registerMemoryEmbeddingProvider` により、アクティブな memory plugin は 1 つ以上の embedding adapter id（たとえば `openai`、`gemini`、または plugin 定義のカスタム id）を登録できます。
- `agents.defaults.memorySearch.provider` や
  `agents.defaults.memorySearch.fallback` のようなユーザー設定は、
  それらの登録済み adapter id に対して解決されます。

### Events とライフサイクル

| Method                                       | 役割                          |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | 型付きライフサイクル hook     |
| `api.onConversationBindingResolved(handler)` | 会話 binding コールバック     |

### Hook decision の意味論

- `before_tool_call`: `{ block: true }` を返すと終端になります。いずれかの handler がこれを設定すると、より低優先度の handler はスキップされます。
- `before_tool_call`: `{ block: false }` を返すと、上書きではなく未決定（`block` を省略した場合と同じ）として扱われます。
- `before_install`: `{ block: true }` を返すと終端になります。いずれかの handler がこれを設定すると、より低優先度の handler はスキップされます。
- `before_install`: `{ block: false }` を返すと、上書きではなく未決定（`block` を省略した場合と同じ）として扱われます。
- `reply_dispatch`: `{ handled: true, ... }` を返すと終端になります。いずれかの handler が dispatch を引き受けると、より低優先度の handler とデフォルトの model dispatch パスはスキップされます。
- `message_sending`: `{ cancel: true }` を返すと終端になります。いずれかの handler がこれを設定すると、より低優先度の handler はスキップされます。
- `message_sending`: `{ cancel: false }` を返すと、上書きではなく未決定（`cancel` を省略した場合と同じ）として扱われます。

### API オブジェクトのフィールド

| Field                    | Type                      | 説明                                                                                       |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------ |
| `api.id`                 | `string`                  | plugin id                                                                                  |
| `api.name`               | `string`                  | 表示名                                                                                     |
| `api.version`            | `string?`                 | plugin バージョン（任意）                                                                  |
| `api.description`        | `string?`                 | plugin 説明（任意）                                                                        |
| `api.source`             | `string`                  | plugin ソースパス                                                                          |
| `api.rootDir`            | `string?`                 | plugin ルートディレクトリ（任意）                                                          |
| `api.config`             | `OpenClawConfig`          | 現在の設定スナップショット（利用可能な場合はアクティブなインメモリ runtime snapshot）      |
| `api.pluginConfig`       | `Record<string, unknown>` | `plugins.entries.<id>.config` からの plugin 固有設定                                      |
| `api.runtime`            | `PluginRuntime`           | [Runtime Helpers](/ja-JP/plugins/sdk-runtime)                                                    |
| `api.logger`             | `PluginLogger`            | スコープ付き logger（`debug`, `info`, `warn`, `error`）                                   |
| `api.registrationMode`   | `PluginRegistrationMode`  | 現在の load mode。`"setup-runtime"` は full-entry 前の軽量な起動/setup ウィンドウです      |
| `api.resolvePath(input)` | `(string) => string`      | plugin ルートからの相対パスを解決                                                          |

## 内部 module 規約

plugin 内では、内部 import にローカル barrel file を使ってください:

```
my-plugin/
  api.ts            # 外部 consumer 向け公開 export
  runtime-api.ts    # 内部専用 runtime export
  index.ts          # plugin entry point
  setup-entry.ts    # 軽量な setup 専用 entry（任意）
```

<Warning>
  本番コードから、自分自身の plugin を `openclaw/plugin-sdk/<your-plugin>`
  経由で import してはいけません。内部 import は `./api.ts` または
  `./runtime-api.ts` を通してください。SDK path は外部契約専用です。
</Warning>

facade 経由で読み込まれるバンドル plugin の公開 surface（`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts`、および類似の公開 entry file）は、
OpenClaw がすでに実行中であればアクティブな runtime config snapshot を優先するようになりました。まだ runtime snapshot が存在しない場合は、
ディスク上で解決された設定ファイルにフォールバックします。

provider plugins は、helper が意図的に provider 固有であり、
まだ汎用的な SDK subpath に属さない場合、狭い plugin ローカル契約 barrel を公開することもできます。現在のバンドル例: Anthropic provider は、
Anthropic の beta-header や `service_tier` ロジックを汎用
`plugin-sdk/*` 契約へ昇格させる代わりに、自身の公開 `api.ts` / `contract-api.ts`
seam に Claude stream helper を保持しています。

その他の現在のバンドル例:

- `@openclaw/openai-provider`: `api.ts` は provider builder、
  default-model helper、および realtime provider builder を export します
- `@openclaw/openrouter-provider`: `api.ts` は provider builder と
  onboarding/config helper を export します

<Warning>
  extension の本番コードでは、`openclaw/plugin-sdk/<other-plugin>`
  import も避けるべきです。helper が本当に共有されるべきなら、2 つの plugin を結合させるのではなく、
  `openclaw/plugin-sdk/speech`、`.../provider-model-shared`、または
  その他の capability 指向 surface のような中立な SDK subpath へ昇格させてください。
</Warning>

## 関連

- [Entry Points](/ja-JP/plugins/sdk-entrypoints) — `definePluginEntry` と `defineChannelPluginEntry` のオプション
- [Runtime Helpers](/ja-JP/plugins/sdk-runtime) — `api.runtime` namespace 全体のリファレンス
- [Setup and Config](/ja-JP/plugins/sdk-setup) — パッケージング、manifest、設定スキーマ
- [Testing](/ja-JP/plugins/sdk-testing) — テストユーティリティと lint ルール
- [SDK Migration](/ja-JP/plugins/sdk-migration) — 非推奨 surface からの移行
- [Plugin Internals](/ja-JP/plugins/architecture) — 詳細なアーキテクチャと capability モデル
