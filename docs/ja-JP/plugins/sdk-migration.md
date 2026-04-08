---
read_when:
    - OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED 警告が表示されている場合
    - OPENCLAW_EXTENSION_API_DEPRECATED 警告が表示されている場合
    - プラグインを最新のプラグインアーキテクチャに更新している場合
    - 外部 OpenClaw プラグインを保守している場合
sidebarTitle: Migrate to SDK
summary: レガシーな後方互換レイヤーから最新の Plugin SDK へ移行する
title: Plugin SDK 移行
x-i18n:
    generated_at: "2026-04-08T02:18:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 155a8b14bc345319c8516ebdb8a0ccdea2c5f7fa07dad343442996daee21ecad
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin SDK 移行

OpenClaw は、広範な後方互換レイヤーから、用途が絞られ文書化された import を備えた最新のプラグイン
アーキテクチャへ移行しました。新しいアーキテクチャ以前にプラグインを構築している場合、このガイドが移行に役立ちます。

## 何が変わるのか

旧プラグインシステムでは、プラグインが必要なものを単一のエントリーポイントから
何でも import できる、2 つの広く開かれたサーフェスが提供されていました。

- **`openclaw/plugin-sdk/compat`** — 数十の
  ヘルパーを再エクスポートする単一の import。新しいプラグインアーキテクチャが構築される間、
  古い hook ベースのプラグインを動作させ続けるために導入されました。
- **`openclaw/extension-api`** — 組み込み agent runner のような
  ホスト側ヘルパーへプラグインが直接アクセスできるようにするブリッジ。

これら 2 つのサーフェスは現在どちらも **非推奨** です。実行時にはまだ動作しますが、新しい
プラグインでは使ってはいけません。また既存プラグインも、次のメジャーリリースで削除される前に移行する必要があります。

<Warning>
  後方互換レイヤーは、将来のメジャーリリースで削除されます。
  これらのサーフェスから import しているプラグインは、その時点で壊れます。
</Warning>

## なぜ変わったのか

旧来のアプローチには問題がありました。

- **起動が遅い** — 1 つのヘルパーを import すると、無関係な数十のモジュールまで読み込まれる
- **循環依存** — 広範な再エクスポートにより、import cycle を簡単に作れてしまう
- **不明瞭な API サーフェス** — どの export が安定で、どれが内部実装なのか区別できない

最新の Plugin SDK はこれを解決します。各 import path（`openclaw/plugin-sdk/\<subpath\>`）
は、小さく自己完結したモジュールであり、明確な目的と文書化された契約を持ちます。

バンドル済みチャネル向けのレガシーな provider 利便性 seam も削除されています。
`openclaw/plugin-sdk/slack`、`openclaw/plugin-sdk/discord`、
`openclaw/plugin-sdk/signal`、`openclaw/plugin-sdk/whatsapp`、
チャネル名付きのヘルパー seam、および
`openclaw/plugin-sdk/telegram-core` のような import は、
安定したプラグイン契約ではなく、mono-repo 内部の非公開ショートカットでした。代わりに、より絞られた汎用 SDK subpath を使用してください。バンドル済みプラグインワークスペース内では、provider 所有のヘルパーはそのプラグイン自身の
`api.ts` または `runtime-api.ts` に置いてください。

現在のバンドル済み provider の例:

- Anthropic は Claude 固有の stream ヘルパーを自身の `api.ts` /
  `contract-api.ts` seam に保持しています
- OpenAI は provider builder、default-model ヘルパー、realtime provider
  builder を自身の `api.ts` に保持しています
- OpenRouter は provider builder と onboarding/config ヘルパーを自身の
  `api.ts` に保持しています

## 移行方法

<Steps>
  <Step title="approval-native handler を capability facts に移行する">
    approval 対応チャネルプラグインは、現在では
    `approvalCapability.nativeRuntime` と共有 runtime-context registry を通じて
    ネイティブ approval 動作を公開します。

    主な変更点:

    - `approvalCapability.handler.loadRuntime(...)` を
      `approvalCapability.nativeRuntime` に置き換える
    - approval 固有の auth/delivery を、レガシーな `plugin.auth` /
      `plugin.approvals` 配線から `approvalCapability` へ移動する
    - `ChannelPlugin.approvals` は公開チャネルプラグイン契約から削除された。
      `delivery` / `native` / `render` フィールドは `approvalCapability` に移動する
    - `plugin.auth` はチャネルの login/logout フロー専用として残る。そこにある approval auth
      hook は、もはや core では読み取られない
    - クライアント、token、Bolt
      app のようなチャネル所有ランタイムオブジェクトは `openclaw/plugin-sdk/channel-runtime-context`
      を通じて登録する
    - ネイティブ approval handler からプラグイン所有の reroute notice を送ってはいけない。
      実際の配信結果に基づく routed-elsewhere notice は現在 core が管理する
    - `channelRuntime` を `createChannelManager(...)` に渡すときは、実際の
      `createPluginRuntime().channel` サーフェスを提供すること。部分的な stub は拒否される

    現在の approval capability
    レイアウトは `/plugins/sdk-channel-plugins` を参照してください。

  </Step>

  <Step title="Windows wrapper fallback 動作を監査する">
    プラグインが `openclaw/plugin-sdk/windows-spawn` を使用している場合、
    解決できない Windows の `.cmd` / `.bat` wrapper は、明示的に
    `allowShellFallback: true` を渡さない限り、現在は fail-closed になります。

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

    呼び出し元が意図的に shell fallback に依存していない場合は、
    `allowShellFallback` を設定せず、代わりに発生したエラーを処理してください。

  </Step>

  <Step title="非推奨 import を見つける">
    プラグイン内で、どちらかの非推奨サーフェスからの import を検索してください。

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="用途が絞られた import に置き換える">
    旧サーフェスの各 export は、特定の最新 import path に対応しています。

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

    ホスト側ヘルパーについては、直接 import するのではなく、注入されたプラグインランタイムを使用してください。

    ```typescript
    // Before (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After (injected runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    同じパターンは、他のレガシーブリッジヘルパーにも当てはまります。

    | Old import | 最新の対応先 |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | session store helpers | `api.runtime.agent.session.*` |

  </Step>

  <Step title="ビルドとテスト">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## import path リファレンス

<Accordion title="一般的な import path テーブル">
  | Import path | 目的 | 主な export |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | 正式なプラグインエントリーヘルパー | `definePluginEntry` |
  | `plugin-sdk/core` | チャネルエントリー定義/ビルダー向けのレガシーな umbrella 再エクスポート | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | ルート設定スキーマ export | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | 単一 provider エントリーヘルパー | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | 用途が絞られたチャネルエントリー定義とビルダー | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | 共有 setup ウィザードヘルパー | Allowlist prompts, setup status builders |
  | `plugin-sdk/setup-runtime` | setup 時ランタイムヘルパー | Import-safe setup patch adapters, lookup-note helpers, `promptResolvedAllowFrom`, `splitSetupEntries`, delegated setup proxies |
  | `plugin-sdk/setup-adapter-runtime` | setup adapter ヘルパー | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | setup ツール群ヘルパー | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | 複数アカウントヘルパー | Account list/config/action-gate helpers |
  | `plugin-sdk/account-id` | account-id ヘルパー | `DEFAULT_ACCOUNT_ID`, account-id normalization |
  | `plugin-sdk/account-resolution` | アカウント参照ヘルパー | Account lookup + default-fallback helpers |
  | `plugin-sdk/account-helpers` | 用途が絞られたアカウントヘルパー | Account list/account-action helpers |
  | `plugin-sdk/channel-setup` | setup ウィザード adapter | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, plus `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DM pairing プリミティブ | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | 返信プレフィックス + typing 配線 | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | config adapter ファクトリー | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | config schema ビルダー | Channel config schema types |
  | `plugin-sdk/telegram-command-config` | Telegram command config ヘルパー | Command-name normalization, description trimming, duplicate/conflict validation |
  | `plugin-sdk/channel-policy` | グループ/DM ポリシー解決 | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | アカウント状態追跡 | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | 受信 envelope ヘルパー | Shared route + envelope builder helpers |
  | `plugin-sdk/inbound-reply-dispatch` | 受信 reply ヘルパー | Shared record-and-dispatch helpers |
  | `plugin-sdk/messaging-targets` | メッセージングターゲット解析 | Target parsing/matching helpers |
  | `plugin-sdk/outbound-media` | 送信 media ヘルパー | Shared outbound media loading |
  | `plugin-sdk/outbound-runtime` | 送信ランタイムヘルパー | Outbound identity/send delegate helpers |
  | `plugin-sdk/thread-bindings-runtime` | スレッドバインディングヘルパー | Thread-binding lifecycle and adapter helpers |
  | `plugin-sdk/agent-media-payload` | レガシー media payload ヘルパー | Agent media payload builder for legacy field layouts |
  | `plugin-sdk/channel-runtime` | 非推奨の互換 shim | Legacy channel runtime utilities only |
  | `plugin-sdk/channel-send-result` | 送信結果型 | Reply result types |
  | `plugin-sdk/runtime-store` | 永続的なプラグインストレージ | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | 広範なランタイムヘルパー | Runtime/logging/backup/plugin-install helpers |
  | `plugin-sdk/runtime-env` | 用途が絞られた runtime env ヘルパー | Logger/runtime env, timeout, retry, and backoff helpers |
  | `plugin-sdk/plugin-runtime` | 共有プラグインランタイムヘルパー | Plugin commands/hooks/http/interactive helpers |
  | `plugin-sdk/hook-runtime` | hook pipeline ヘルパー | Shared webhook/internal hook pipeline helpers |
  | `plugin-sdk/lazy-runtime` | 遅延ランタイムヘルパー | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | プロセスヘルパー | Shared exec helpers |
  | `plugin-sdk/cli-runtime` | CLI ランタイムヘルパー | Command formatting, waits, version helpers |
  | `plugin-sdk/gateway-runtime` | Gateway ヘルパー | Gateway client and channel-status patch helpers |
  | `plugin-sdk/config-runtime` | config ヘルパー | Config load/write helpers |
  | `plugin-sdk/telegram-command-config` | Telegram command ヘルパー | バンドル済み Telegram 契約サーフェスが利用できない場合の、フォールバックとして安定した Telegram command validation helpers |
  | `plugin-sdk/approval-runtime` | approval prompt ヘルパー | Exec/plugin approval payload, approval capability/profile helpers, native approval routing/runtime helpers |
  | `plugin-sdk/approval-auth-runtime` | approval auth ヘルパー | Approver resolution, same-chat action auth |
  | `plugin-sdk/approval-client-runtime` | approval client ヘルパー | Native exec approval profile/filter helpers |
  | `plugin-sdk/approval-delivery-runtime` | approval delivery ヘルパー | Native approval capability/delivery adapters |
  | `plugin-sdk/approval-gateway-runtime` | approval Gateway ヘルパー | Shared approval gateway-resolution helper |
  | `plugin-sdk/approval-handler-adapter-runtime` | approval adapter ヘルパー | hot channel entrypoint 向けの軽量な native approval adapter loading helpers |
  | `plugin-sdk/approval-handler-runtime` | approval handler ヘルパー | より広範な approval handler runtime helpers。adapter/gateway のより絞られた seam で足りる場合はそちらを優先 |
  | `plugin-sdk/approval-native-runtime` | approval target ヘルパー | Native approval target/account binding helpers |
  | `plugin-sdk/approval-reply-runtime` | approval reply ヘルパー | Exec/plugin approval reply payload helpers |
  | `plugin-sdk/channel-runtime-context` | チャネル runtime-context ヘルパー | 汎用チャネル runtime-context register/get/watch helpers |
  | `plugin-sdk/security-runtime` | セキュリティヘルパー | Shared trust, DM gating, external-content, and secret-collection helpers |
  | `plugin-sdk/ssrf-policy` | SSRF policy ヘルパー | Host allowlist and private-network policy helpers |
  | `plugin-sdk/ssrf-runtime` | SSRF ランタイムヘルパー | Pinned-dispatcher, guarded fetch, SSRF policy helpers |
  | `plugin-sdk/collection-runtime` | 境界付きキャッシュヘルパー | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | 診断ゲーティングヘルパー | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | エラー整形ヘルパー | `formatUncaughtError`, `isApprovalNotFoundError`, error graph helpers |
  | `plugin-sdk/fetch-runtime` | ラップ済み fetch/proxy ヘルパー | `resolveFetch`, proxy helpers |
  | `plugin-sdk/host-runtime` | ホスト正規化ヘルパー | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | retry ヘルパー | `RetryConfig`, `retryAsync`, policy runners |
  | `plugin-sdk/allow-from` | Allowlist 整形 | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Allowlist 入力マッピング | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | コマンドゲーティングとコマンドサーフェスヘルパー | `resolveControlCommandGate`, sender-authorization helpers, command registry helpers |
  | `plugin-sdk/secret-input` | secret 入力解析 | Secret input helpers |
  | `plugin-sdk/webhook-ingress` | webhook リクエストヘルパー | Webhook target utilities |
  | `plugin-sdk/webhook-request-guards` | webhook body guard ヘルパー | Request body read/limit helpers |
  | `plugin-sdk/reply-runtime` | 共有 reply ランタイム | Inbound dispatch, heartbeat, reply planner, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | 用途が絞られた reply dispatch ヘルパー | Finalize + provider dispatch helpers |
  | `plugin-sdk/reply-history` | reply-history ヘルパー | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | reply 参照計画 | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | reply chunk ヘルパー | Text/markdown chunking helpers |
  | `plugin-sdk/session-store-runtime` | session store ヘルパー | Store path + updated-at helpers |
  | `plugin-sdk/state-paths` | state path ヘルパー | State and OAuth dir helpers |
  | `plugin-sdk/routing` | ルーティング/セッションキーヘルパー | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, session-key normalization helpers |
  | `plugin-sdk/status-helpers` | チャネル status ヘルパー | Channel/account status summary builders, runtime-state defaults, issue metadata helpers |
  | `plugin-sdk/target-resolver-runtime` | target resolver ヘルパー | Shared target resolver helpers |
  | `plugin-sdk/string-normalization-runtime` | 文字列正規化ヘルパー | Slug/string normalization helpers |
  | `plugin-sdk/request-url` | リクエスト URL ヘルパー | request-like input から文字列 URL を抽出 |
  | `plugin-sdk/run-command` | 時間制限付きコマンドヘルパー | stdout/stderr を正規化した timed command runner |
  | `plugin-sdk/param-readers` | パラメータリーダー | Common tool/CLI param readers |
  | `plugin-sdk/tool-send` | ツール送信抽出 | ツール引数から正規の送信先フィールドを抽出 |
  | `plugin-sdk/temp-path` | 一時パスヘルパー | Shared temp-download path helpers |
  | `plugin-sdk/logging-core` | ロギングヘルパー | Subsystem logger and redaction helpers |
  | `plugin-sdk/markdown-table-runtime` | Markdown table ヘルパー | Markdown table mode helpers |
  | `plugin-sdk/reply-payload` | メッセージ reply 型 | Reply payload types |
  | `plugin-sdk/provider-setup` | 厳選されたローカル/セルフホスト型 provider setup ヘルパー | Self-hosted provider discovery/config helpers |
  | `plugin-sdk/self-hosted-provider-setup` | 用途が絞られた OpenAI-compatible セルフホスト provider setup ヘルパー | 同じ self-hosted provider discovery/config helpers |
  | `plugin-sdk/provider-auth-runtime` | provider ランタイム auth ヘルパー | Runtime API-key resolution helpers |
  | `plugin-sdk/provider-auth-api-key` | provider API-key setup ヘルパー | API-key onboarding/profile-write helpers |
  | `plugin-sdk/provider-auth-result` | provider auth-result ヘルパー | Standard OAuth auth-result builder |
  | `plugin-sdk/provider-auth-login` | provider 対話ログインヘルパー | Shared interactive login helpers |
  | `plugin-sdk/provider-env-vars` | provider env-var ヘルパー | Provider auth env-var lookup helpers |
  | `plugin-sdk/provider-model-shared` | 共有 provider model/replay ヘルパー | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, shared replay-policy builders, provider-endpoint helpers, and model-id normalization helpers |
  | `plugin-sdk/provider-catalog-shared` | 共有 provider catalog ヘルパー | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | provider onboarding patch | Onboarding config helpers |
  | `plugin-sdk/provider-http` | provider HTTP ヘルパー | Generic provider HTTP/endpoint capability helpers |
  | `plugin-sdk/provider-web-fetch` | provider web-fetch ヘルパー | Web-fetch provider registration/cache helpers |
  | `plugin-sdk/provider-web-search-contract` | provider web-search 契約ヘルパー | `enablePluginInConfig`、`resolveProviderWebSearchPluginConfig`、scoped credential setters/getters などの、用途が絞られた web-search config/credential contract helpers |
  | `plugin-sdk/provider-web-search` | provider web-search ヘルパー | Web-search provider registration/cache/runtime helpers |
  | `plugin-sdk/provider-tools` | provider tool/schema compat ヘルパー | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini schema cleanup + diagnostics, and xAI compat helpers such as `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | provider usage ヘルパー | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage`, and other provider usage helpers |
  | `plugin-sdk/provider-stream` | provider stream wrapper ヘルパー | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, stream wrapper types, and shared Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot wrapper helpers |
  | `plugin-sdk/keyed-async-queue` | 順序付き async queue | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | 共有 media ヘルパー | Media fetch/transform/store helpers plus media payload builders |
  | `plugin-sdk/media-generation-runtime` | 共有 media-generation ヘルパー | Shared failover helpers, candidate selection, and missing-model messaging for image/video/music generation |
  | `plugin-sdk/media-understanding` | media-understanding ヘルパー | Media understanding provider types plus provider-facing image/audio helper exports |
  | `plugin-sdk/text-runtime` | 共有 text ヘルパー | Assistant-visible-text stripping, markdown render/chunking/table helpers, redaction helpers, directive-tag helpers, safe-text utilities, and related text/logging helpers |
  | `plugin-sdk/text-chunking` | text chunking ヘルパー | Outbound text chunking helper |
  | `plugin-sdk/speech` | speech ヘルパー | Speech provider types plus provider-facing directive, registry, and validation helpers |
  | `plugin-sdk/speech-core` | 共有 speech core | Speech provider types, registry, directives, normalization |
  | `plugin-sdk/realtime-transcription` | realtime transcription ヘルパー | Provider types and registry helpers |
  | `plugin-sdk/realtime-voice` | realtime voice ヘルパー | Provider types and registry helpers |
  | `plugin-sdk/image-generation-core` | 共有 image-generation core | Image-generation types, failover, auth, and registry helpers |
  | `plugin-sdk/music-generation` | music-generation ヘルパー | Music-generation provider/request/result types |
  | `plugin-sdk/music-generation-core` | 共有 music-generation core | Music-generation types, failover helpers, provider lookup, and model-ref parsing |
  | `plugin-sdk/video-generation` | video-generation ヘルパー | Video-generation provider/request/result types |
  | `plugin-sdk/video-generation-core` | 共有 video-generation core | Video-generation types, failover helpers, provider lookup, and model-ref parsing |
  | `plugin-sdk/interactive-runtime` | 対話 reply ヘルパー | Interactive reply payload normalization/reduction |
  | `plugin-sdk/channel-config-primitives` | channel config プリミティブ | 用途が絞られた channel config-schema primitives |
  | `plugin-sdk/channel-config-writes` | channel config-write ヘルパー | Channel config-write authorization helpers |
  | `plugin-sdk/channel-plugin-common` | 共有チャネル前奏部 | Shared channel plugin prelude exports |
  | `plugin-sdk/channel-status` | channel status ヘルパー | Shared channel status snapshot/summary helpers |
  | `plugin-sdk/allowlist-config-edit` | Allowlist config ヘルパー | Allowlist config edit/read helpers |
  | `plugin-sdk/group-access` | グループアクセスヘルパー | Shared group-access decision helpers |
  | `plugin-sdk/direct-dm` | direct-DM ヘルパー | Shared direct-DM auth/guard helpers |
  | `plugin-sdk/extension-shared` | 共有 extension ヘルパー | Passive-channel/status and ambient proxy helper primitives |
  | `plugin-sdk/webhook-targets` | webhook target ヘルパー | Webhook target registry and route-install helpers |
  | `plugin-sdk/webhook-path` | webhook path ヘルパー | Webhook path normalization helpers |
  | `plugin-sdk/web-media` | 共有 web media ヘルパー | Remote/local media loading helpers |
  | `plugin-sdk/zod` | Zod 再エクスポート | Plugin SDK 利用者向けに再エクスポートされた `zod` |
  | `plugin-sdk/memory-core` | バンドル済み memory-core ヘルパー | Memory manager/config/file/CLI helper surface |
  | `plugin-sdk/memory-core-engine-runtime` | memory engine runtime facade | Memory index/search runtime facade |
  | `plugin-sdk/memory-core-host-engine-foundation` | memory host foundation engine | Memory host foundation engine exports |
  | `plugin-sdk/memory-core-host-engine-embeddings` | memory host embedding engine | Memory host embedding engine exports |
  | `plugin-sdk/memory-core-host-engine-qmd` | memory host QMD engine | Memory host QMD engine exports |
  | `plugin-sdk/memory-core-host-engine-storage` | memory host storage engine | Memory host storage engine exports |
  | `plugin-sdk/memory-core-host-multimodal` | memory host multimodal ヘルパー | Memory host multimodal helpers |
  | `plugin-sdk/memory-core-host-query` | memory host query ヘルパー | Memory host query helpers |
  | `plugin-sdk/memory-core-host-secret` | memory host secret ヘルパー | Memory host secret helpers |
  | `plugin-sdk/memory-core-host-events` | memory host event journal ヘルパー | Memory host event journal helpers |
  | `plugin-sdk/memory-core-host-status` | memory host status ヘルパー | Memory host status helpers |
  | `plugin-sdk/memory-core-host-runtime-cli` | memory host CLI runtime | Memory host CLI runtime helpers |
  | `plugin-sdk/memory-core-host-runtime-core` | memory host core runtime | Memory host core runtime helpers |
  | `plugin-sdk/memory-core-host-runtime-files` | memory host file/runtime ヘルパー | Memory host file/runtime helpers |
  | `plugin-sdk/memory-host-core` | memory host core runtime alias | Memory host core runtime helpers の vendor-neutral alias |
  | `plugin-sdk/memory-host-events` | memory host event journal alias | Memory host event journal helpers の vendor-neutral alias |
  | `plugin-sdk/memory-host-files` | memory host file/runtime alias | Memory host file/runtime helpers の vendor-neutral alias |
  | `plugin-sdk/memory-host-markdown` | managed markdown ヘルパー | memory 隣接プラグイン向けの shared managed-markdown helpers |
  | `plugin-sdk/memory-host-search` | active memory search facade | Lazy active-memory search-manager runtime facade |
  | `plugin-sdk/memory-host-status` | memory host status alias | Memory host status helpers の vendor-neutral alias |
  | `plugin-sdk/memory-lancedb` | バンドル済み memory-lancedb ヘルパー | Memory-lancedb helper surface |
  | `plugin-sdk/testing` | テストユーティリティ | Test helpers and mocks |
</Accordion>

このテーブルは、完全な SDK
サーフェスではなく、意図的に一般的な移行対象のサブセットだけを掲載しています。200 以上の entrypoint からなる完全な一覧は
`scripts/lib/plugin-sdk-entrypoints.json` にあります。

この一覧には、`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、`plugin-sdk/zalo`、
`plugin-sdk/zalo-setup`、`plugin-sdk/matrix*` のような
バンドル済みプラグイン用 helper seam も引き続き含まれています。これらは
バンドル済みプラグインの保守と互換性のために export されたままですが、一般的な移行テーブルからは意図的に除外されており、新しいプラグインコードの推奨先ではありません。

同じルールは、次のような他の bundled-helper ファミリーにも当てはまります。

- browser サポートヘルパー: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- `plugin-sdk/googlechat`、
  `plugin-sdk/zalouser`、`plugin-sdk/bluebubbles*`、
  `plugin-sdk/mattermost*`、`plugin-sdk/msteams`、
  `plugin-sdk/nextcloud-talk`、`plugin-sdk/nostr`、`plugin-sdk/tlon`、
  `plugin-sdk/twitch`、
  `plugin-sdk/github-copilot-login`、`plugin-sdk/github-copilot-token`、
  `plugin-sdk/diagnostics-otel`、`plugin-sdk/diffs`、`plugin-sdk/llm-task`、
  `plugin-sdk/thread-ownership`、`plugin-sdk/voice-call` のような
  バンドル済み helper/plugin サーフェス

`plugin-sdk/github-copilot-token` は現在、用途が絞られた token-helper
サーフェス `DEFAULT_COPILOT_API_BASE_URL`、
`deriveCopilotApiBaseUrlFromToken`、`resolveCopilotApiToken` を公開しています。

作業内容に合う、最も絞られた import を使用してください。export が見つからない場合は、
`src/plugin-sdk/` のソースを確認するか、Discord で質問してください。

## 削除タイムライン

| 時期 | 何が起こるか |
| ---------------------- | ----------------------------------------------------------------------- |
| **今**                | 非推奨サーフェスが実行時警告を出す                               |
| **次のメジャーリリース** | 非推奨サーフェスは削除される。引き続き使用しているプラグインは失敗する |

すべての core プラグインはすでに移行済みです。外部プラグインは、
次のメジャーリリース前に移行してください。

## 警告を一時的に抑制する

移行作業中は、これらの環境変数を設定してください。

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

これは一時的な逃げ道であり、恒久的な解決策ではありません。

## 関連

- [はじめに](/ja-JP/plugins/building-plugins) — 最初のプラグインを作成する
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全な subpath import リファレンス
- [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — チャネルプラグインの構築
- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — provider プラグインの構築
- [Plugin Internals](/ja-JP/plugins/architecture) — アーキテクチャの詳細解説
- [Plugin Manifest](/ja-JP/plugins/manifest) — manifest スキーマリファレンス
