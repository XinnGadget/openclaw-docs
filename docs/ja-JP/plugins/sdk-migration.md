---
read_when:
    - '`OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED` の警告が表示される場合があります'
    - '`OPENCLAW_EXTENSION_API_DEPRECATED` の警告が表示される場合があります'
    - 最新のpluginアーキテクチャにpluginを更新しています
    - 外部のOpenClaw pluginをメンテナンスしています
sidebarTitle: Migrate to SDK
summary: 従来の後方互換レイヤーから最新のPlugin SDKへ移行する
title: Plugin SDK移行
x-i18n:
    generated_at: "2026-04-17T04:43:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: f0283f949eec358a12a0709db846cde2a1509f28e5c60db6e563cb8a540b979d
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin SDK移行

OpenClawは、幅広い後方互換レイヤーから、用途を絞って文書化されたインポートを備えた最新のpluginアーキテクチャへ移行しました。あなたのpluginがこの新しいアーキテクチャ以前に作られたものであれば、このガイドが移行の助けになります。

## 何が変わるのか

古いpluginシステムは、単一のエントリーポイントから必要なものを何でもインポートできる、2つの非常に広い公開面を提供していました。

- **`openclaw/plugin-sdk/compat`** — 数十個のヘルパーを再エクスポートする単一のインポートです。新しいpluginアーキテクチャの構築中に、古いフックベースのpluginを動作させ続けるために導入されました。
- **`openclaw/extension-api`** — 埋め込みエージェントランナーのようなホスト側ヘルパーへpluginが直接アクセスできるようにするブリッジです。

これら2つの公開面は現在どちらも**非推奨**です。実行時には引き続き動作しますが、新しいpluginでは使用してはいけません。また、既存のpluginも次のメジャーリリースで削除される前に移行する必要があります。

<Warning>
  後方互換レイヤーは将来のメジャーリリースで削除されます。これらの公開面からまだインポートしているpluginは、その時点で動作しなくなります。
</Warning>

## なぜ変更されたのか

古いアプローチには問題がありました。

- **起動が遅い** — 1つのヘルパーをインポートすると、無関係な数十個のモジュールまで読み込まれていました
- **循環依存** — 幅広い再エクスポートによって、インポートサイクルが簡単に発生していました
- **不明確なAPI公開面** — どのエクスポートが安定していて、どれが内部用なのかを判別する方法がありませんでした

最新のPlugin SDKはこれを解決します。各インポートパス（`openclaw/plugin-sdk/\<subpath\>`）は、明確な目的と文書化された契約を持つ、小さく自己完結したモジュールです。

同梱チャネル向けの従来のprovider利便性シームも廃止されました。`openclaw/plugin-sdk/slack`、`openclaw/plugin-sdk/discord`、`openclaw/plugin-sdk/signal`、`openclaw/plugin-sdk/whatsapp`、チャネル名付きのヘルパーシーム、および `openclaw/plugin-sdk/telegram-core` のようなインポートは、安定したplugin契約ではなく、mono-repo内部用のショートカットでした。代わりに、より狭い汎用的なSDKサブパスを使用してください。同梱pluginワークスペース内では、providerが所有するヘルパーはそのplugin自身の `api.ts` または `runtime-api.ts` に置いてください。

現在の同梱providerの例:

- Anthropicは、Claude固有のストリームヘルパーを自身の `api.ts` / `contract-api.ts` シーム内に保持しています
- OpenAIは、providerビルダー、デフォルトモデルヘルパー、リアルタイムproviderビルダーを自身の `api.ts` に保持しています
- OpenRouterは、providerビルダーとオンボーディング/設定ヘルパーを自身の `api.ts` に保持しています

## 移行方法

<Steps>
  <Step title="承認ネイティブハンドラーを capability facts に移行する">
    承認対応のchannel pluginは、`approvalCapability.nativeRuntime` と共有runtime-contextレジストリを通じて、ネイティブ承認動作を公開するようになりました。

    主な変更点:

    - `approvalCapability.handler.loadRuntime(...)` を `approvalCapability.nativeRuntime` に置き換える
    - 承認固有の認証/配信を従来の `plugin.auth` / `plugin.approvals` 配線から `approvalCapability` に移す
    - `ChannelPlugin.approvals` は公開channel-plugin契約から削除されました。delivery/native/render フィールドは `approvalCapability` に移してください
    - `plugin.auth` はchannelのログイン/ログアウトフロー専用として残ります。そこにある承認認証フックは、もはやcoreから読み取られません
    - クライアント、トークン、Boltアプリなど、channelが所有するruntimeオブジェクトは `openclaw/plugin-sdk/channel-runtime-context` を通じて登録する
    - ネイティブ承認ハンドラーからplugin所有のリルート通知を送信しないでください。実際の配信結果に基づく「別の場所へルーティングされた」通知は、現在はcoreが管理します
    - `channelRuntime` を `createChannelManager(...)` に渡す場合は、実際の `createPluginRuntime().channel` 公開面を提供してください。不完全なスタブは拒否されます

    現在の承認capabilityレイアウトについては `/plugins/sdk-channel-plugins` を参照してください。

  </Step>

  <Step title="Windowsラッパーのフォールバック動作を確認する">
    あなたのpluginが `openclaw/plugin-sdk/windows-spawn` を使用している場合、解決できないWindowsの `.cmd` / `.bat` ラッパーは、`allowShellFallback: true` を明示的に渡さない限り、失敗時に閉じる動作になりました。

    ```typescript
    // Before
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // After
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // シェル経由のフォールバックを意図的に許容する、信頼済みの互換性呼び出し元に対してのみ設定します。
      allowShellFallback: true,
    });
    ```

    呼び出し元が意図的にシェルフォールバックへ依存していない場合は、`allowShellFallback` を設定せず、代わりにスローされるエラーを処理してください。

  </Step>

  <Step title="非推奨インポートを探す">
    あなたのplugin内で、いずれかの非推奨公開面からのインポートを検索してください。

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="用途を絞ったインポートに置き換える">
    古い公開面からの各エクスポートは、特定の最新インポートパスに対応しています。

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

    ホスト側ヘルパーについては、直接インポートする代わりに注入されたplugin runtimeを使用してください。

    ```typescript
    // Before (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After (injected runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    同じパターンは他の従来のブリッジヘルパーにも当てはまります。

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

## インポートパスリファレンス

  <Accordion title="一般的なインポートパステーブル">
  | Import path | 用途 | 主なエクスポート |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | 正式なpluginエントリーヘルパー | `definePluginEntry` |
  | `plugin-sdk/core` | channelエントリー定義/ビルダー向けの従来の包括的再エクスポート | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | ルート設定スキーマのエクスポート | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | 単一provider用エントリーヘルパー | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | 用途を絞ったchannelエントリー定義とビルダー | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | 共有セットアップウィザードヘルパー | Allowlistプロンプト、セットアップステータスビルダー |
  | `plugin-sdk/setup-runtime` | セットアップ時runtimeヘルパー | import-safeなセットアップパッチアダプター、lookup-noteヘルパー、`promptResolvedAllowFrom`, `splitSetupEntries`, 委譲セットアッププロキシ |
  | `plugin-sdk/setup-adapter-runtime` | セットアップアダプターヘルパー | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | セットアップツーリングヘルパー | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | マルチアカウントヘルパー | アカウント一覧/設定/アクションゲートヘルパー |
  | `plugin-sdk/account-id` | account-idヘルパー | `DEFAULT_ACCOUNT_ID`、account-id正規化 |
  | `plugin-sdk/account-resolution` | アカウント検索ヘルパー | アカウント検索 + デフォルトフォールバックヘルパー |
  | `plugin-sdk/account-helpers` | 用途を絞ったアカウントヘルパー | アカウント一覧/アカウントアクションヘルパー |
  | `plugin-sdk/channel-setup` | セットアップウィザードアダプター | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, および `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DMペアリングの基本機能 | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | 返信プレフィックス + typingの配線 | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | 設定アダプターファクトリー | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | 設定スキーマビルダー | channel設定スキーマ型 |
  | `plugin-sdk/telegram-command-config` | Telegramコマンド設定ヘルパー | コマンド名正規化、説明文トリミング、重複/競合検証 |
  | `plugin-sdk/channel-policy` | グループ/DMポリシー解決 | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | アカウントステータス追跡 | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | 受信エンベロープヘルパー | 共有ルート + エンベロープビルダーヘルパー |
  | `plugin-sdk/inbound-reply-dispatch` | 受信返信ヘルパー | 共有record-and-dispatchヘルパー |
  | `plugin-sdk/messaging-targets` | メッセージングターゲット解析 | ターゲット解析/マッチングヘルパー |
  | `plugin-sdk/outbound-media` | 送信メディアヘルパー | 共有送信メディア読み込み |
  | `plugin-sdk/outbound-runtime` | 送信runtimeヘルパー | 送信アイデンティティ/送信デリゲートヘルパー |
  | `plugin-sdk/thread-bindings-runtime` | スレッドバインディングヘルパー | スレッドバインディングのライフサイクルとアダプターヘルパー |
  | `plugin-sdk/agent-media-payload` | 従来のメディアペイロードヘルパー | 従来のフィールドレイアウト向けエージェントメディアペイロードビルダー |
  | `plugin-sdk/channel-runtime` | 非推奨の互換性シム | 従来のchannel runtimeユーティリティのみ |
  | `plugin-sdk/channel-send-result` | 送信結果型 | 返信結果型 |
  | `plugin-sdk/runtime-store` | 永続pluginストレージ | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | 幅広いruntimeヘルパー | runtime/ロギング/バックアップ/plugin-installヘルパー |
  | `plugin-sdk/runtime-env` | 用途を絞ったruntime envヘルパー | ロガー/runtime env、タイムアウト、リトライ、バックオフヘルパー |
  | `plugin-sdk/plugin-runtime` | 共有plugin runtimeヘルパー | pluginコマンド/フック/http/インタラクティブヘルパー |
  | `plugin-sdk/hook-runtime` | フックパイプラインヘルパー | 共有Webhook/internal hookパイプラインヘルパー |
  | `plugin-sdk/lazy-runtime` | 遅延runtimeヘルパー | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | プロセスヘルパー | 共有execヘルパー |
  | `plugin-sdk/cli-runtime` | CLI runtimeヘルパー | コマンド整形、待機、バージョンヘルパー |
  | `plugin-sdk/gateway-runtime` | Gatewayヘルパー | Gatewayクライアントおよびchannel-statusパッチヘルパー |
  | `plugin-sdk/config-runtime` | 設定ヘルパー | 設定読み込み/書き込みヘルパー |
  | `plugin-sdk/telegram-command-config` | Telegramコマンドヘルパー | 同梱Telegram契約surfaceが利用できない場合の、フォールバック安定なTelegramコマンド検証ヘルパー |
  | `plugin-sdk/approval-runtime` | 承認プロンプトヘルパー | exec/plugin承認ペイロード、承認capability/profileヘルパー、ネイティブ承認ルーティング/runtimeヘルパー |
  | `plugin-sdk/approval-auth-runtime` | 承認認証ヘルパー | approver解決、同一チャットアクション認証 |
  | `plugin-sdk/approval-client-runtime` | 承認クライアントヘルパー | ネイティブexec承認profile/filterヘルパー |
  | `plugin-sdk/approval-delivery-runtime` | 承認配信ヘルパー | ネイティブ承認capability/配信アダプター |
  | `plugin-sdk/approval-gateway-runtime` | 承認Gatewayヘルパー | 共有承認gateway解決ヘルパー |
  | `plugin-sdk/approval-handler-adapter-runtime` | 承認アダプターヘルパー | ホットなchannelエントリーポイント向けの軽量ネイティブ承認アダプターロードヘルパー |
  | `plugin-sdk/approval-handler-runtime` | 承認ハンドラーヘルパー | より広範な承認ハンドラーruntimeヘルパー。より狭いadapter/gatewayシームで十分な場合はそちらを優先してください |
  | `plugin-sdk/approval-native-runtime` | 承認ターゲットヘルパー | ネイティブ承認ターゲット/アカウントバインディングヘルパー |
  | `plugin-sdk/approval-reply-runtime` | 承認返信ヘルパー | exec/plugin承認返信ペイロードヘルパー |
  | `plugin-sdk/channel-runtime-context` | channel runtime-contextヘルパー | 汎用channel runtime-context register/get/watchヘルパー |
  | `plugin-sdk/security-runtime` | セキュリティヘルパー | 共有trust、DMゲーティング、外部コンテンツ、secret収集ヘルパー |
  | `plugin-sdk/ssrf-policy` | SSRFポリシーヘルパー | ホストallowlistおよびプライベートネットワークポリシーヘルパー |
  | `plugin-sdk/ssrf-runtime` | SSRF runtimeヘルパー | pinned-dispatcher、guarded fetch、SSRFポリシーヘルパー |
  | `plugin-sdk/collection-runtime` | 上限付きキャッシュヘルパー | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | 診断ゲーティングヘルパー | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | エラー整形ヘルパー | `formatUncaughtError`, `isApprovalNotFoundError`, エラーグラフヘルパー |
  | `plugin-sdk/fetch-runtime` | ラップされたfetch/proxyヘルパー | `resolveFetch`, proxyヘルパー |
  | `plugin-sdk/host-runtime` | ホスト正規化ヘルパー | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | リトライヘルパー | `RetryConfig`, `retryAsync`, ポリシーランナー |
  | `plugin-sdk/allow-from` | Allowlist整形 | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Allowlist入力マッピング | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | コマンドゲーティングおよびcommand-surfaceヘルパー | `resolveControlCommandGate`, 送信者認可ヘルパー、コマンドレジストリヘルパー |
  | `plugin-sdk/command-status` | コマンドステータス/ヘルプレンダラー | `buildCommandsMessage`, `buildCommandsMessagePaginated`, `buildHelpMessage` |
  | `plugin-sdk/secret-input` | secret入力解析 | secret入力ヘルパー |
  | `plugin-sdk/webhook-ingress` | Webhookリクエストヘルパー | Webhookターゲットユーティリティ |
  | `plugin-sdk/webhook-request-guards` | Webhookボディガードヘルパー | リクエストボディ読み取り/上限ヘルパー |
  | `plugin-sdk/reply-runtime` | 共有reply runtime | 受信dispatch、Heartbeat、返信プランナー、チャンク化 |
  | `plugin-sdk/reply-dispatch-runtime` | 用途を絞ったreply dispatchヘルパー | finalize + provider dispatchヘルパー |
  | `plugin-sdk/reply-history` | reply-historyヘルパー | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | reply referenceプランニング | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | reply chunkヘルパー | テキスト/markdownチャンク化ヘルパー |
  | `plugin-sdk/session-store-runtime` | セッションストアヘルパー | ストアパス + updated-atヘルパー |
  | `plugin-sdk/state-paths` | 状態パスヘルパー | stateおよびOAuthディレクトリヘルパー |
  | `plugin-sdk/routing` | ルーティング/セッションキー ヘルパー | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, セッションキー正規化ヘルパー |
  | `plugin-sdk/status-helpers` | channelステータスヘルパー | channel/アカウントステータス要約ビルダー、runtime-stateデフォルト、issueメタデータヘルパー |
  | `plugin-sdk/target-resolver-runtime` | ターゲットリゾルバーヘルパー | 共有ターゲットリゾルバーヘルパー |
  | `plugin-sdk/string-normalization-runtime` | 文字列正規化ヘルパー | slug/文字列正規化ヘルパー |
  | `plugin-sdk/request-url` | リクエストURLヘルパー | request風入力から文字列URLを抽出 |
  | `plugin-sdk/run-command` | 時間計測付きコマンドヘルパー | stdout/stderrを正規化した時間計測付きコマンドランナー |
  | `plugin-sdk/param-readers` | パラメーターリーダー | 一般的なtool/CLIパラメーターリーダー |
  | `plugin-sdk/tool-payload` | toolペイロード抽出 | tool結果オブジェクトから正規化されたペイロードを抽出 |
  | `plugin-sdk/tool-send` | tool送信抽出 | tool引数から正式な送信ターゲットフィールドを抽出 |
  | `plugin-sdk/temp-path` | 一時パスヘルパー | 共有一時ダウンロードパスヘルパー |
  | `plugin-sdk/logging-core` | ロギングヘルパー | subsystemロガーおよびリダクションヘルパー |
  | `plugin-sdk/markdown-table-runtime` | markdown-tableヘルパー | markdown tableモードヘルパー |
  | `plugin-sdk/reply-payload` | メッセージ返信型 | reply payload型 |
  | `plugin-sdk/provider-setup` | 厳選されたローカル/セルフホストproviderセットアップヘルパー | セルフホストproviderの検出/設定ヘルパー |
  | `plugin-sdk/self-hosted-provider-setup` | 用途を絞ったOpenAI互換セルフホストproviderセットアップヘルパー | 同じセルフホストproviderの検出/設定ヘルパー |
  | `plugin-sdk/provider-auth-runtime` | provider runtime認証ヘルパー | runtime API-key解決ヘルパー |
  | `plugin-sdk/provider-auth-api-key` | provider API-keyセットアップヘルパー | API-keyオンボーディング/profile書き込みヘルパー |
  | `plugin-sdk/provider-auth-result` | provider auth-resultヘルパー | 標準OAuth auth-resultビルダー |
  | `plugin-sdk/provider-auth-login` | provider対話型ログインヘルパー | 共有対話型ログインヘルパー |
  | `plugin-sdk/provider-env-vars` | provider env-varヘルパー | provider認証env-var検索ヘルパー |
  | `plugin-sdk/provider-model-shared` | 共有provider model/replayヘルパー | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, 共有replay-policyビルダー、provider-endpointヘルパー、およびmodel-id正規化ヘルパー |
  | `plugin-sdk/provider-catalog-shared` | 共有provider catalogヘルパー | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | providerオンボーディングパッチ | オンボーディング設定ヘルパー |
  | `plugin-sdk/provider-http` | provider HTTPヘルパー | 汎用provider HTTP/endpoint capabilityヘルパー |
  | `plugin-sdk/provider-web-fetch` | provider web-fetchヘルパー | Web-fetch provider登録/キャッシュヘルパー |
  | `plugin-sdk/provider-web-search-config-contract` | provider web-search設定ヘルパー | plugin-enable配線を必要としないprovider向けの、用途を絞ったweb-search設定/credentialヘルパー |
  | `plugin-sdk/provider-web-search-contract` | provider web-search契約ヘルパー | `createWebSearchProviderContractFields`、`enablePluginInConfig`、`resolveProviderWebSearchPluginConfig`、およびスコープ付きcredential setter/getter などの、用途を絞ったweb-search設定/credential契約ヘルパー |
  | `plugin-sdk/provider-web-search` | provider web-searchヘルパー | Web-search provider登録/キャッシュ/runtimeヘルパー |
  | `plugin-sdk/provider-tools` | provider tool/schema互換ヘルパー | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Geminiスキーマのクリーンアップ + 診断、および `resolveXaiModelCompatPatch` / `applyXaiModelCompat` などのxAI互換ヘルパー |
  | `plugin-sdk/provider-usage` | provider使用状況ヘルパー | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage`、およびその他のprovider使用状況ヘルパー |
  | `plugin-sdk/provider-stream` | providerストリームラッパーヘルパー | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, ストリームラッパー型、および共有のAnthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilotラッパーヘルパー |
  | `plugin-sdk/keyed-async-queue` | 順序付き非同期キュー | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | 共有メディアヘルパー | メディアfetch/transform/storeヘルパーとメディアペイロードビルダー |
  | `plugin-sdk/media-generation-runtime` | 共有メディア生成ヘルパー | 画像/動画/音楽生成向けの共有フェイルオーバーヘルパー、候補選択、モデル欠如時メッセージ |
  | `plugin-sdk/media-understanding` | メディア理解ヘルパー | メディア理解provider型と、provider向けの画像/音声ヘルパーエクスポート |
  | `plugin-sdk/text-runtime` | 共有テキストヘルパー | アシスタント可視テキストの除去、markdownレンダー/チャンク化/テーブルヘルパー、リダクションヘルパー、directive-tagヘルパー、安全なテキストユーティリティ、および関連するテキスト/ロギングヘルパー |
  | `plugin-sdk/text-chunking` | テキストチャンク化ヘルパー | 送信テキストチャンク化ヘルパー |
  | `plugin-sdk/speech` | 音声ヘルパー | 音声provider型と、provider向けのdirective、レジストリ、検証ヘルパー |
  | `plugin-sdk/speech-core` | 共有音声コア | 音声provider型、レジストリ、directive、正規化 |
  | `plugin-sdk/realtime-transcription` | リアルタイム文字起こしヘルパー | provider型とレジストリヘルパー |
  | `plugin-sdk/realtime-voice` | リアルタイム音声ヘルパー | provider型とレジストリヘルパー |
  | `plugin-sdk/image-generation-core` | 共有画像生成コア | 画像生成型、フェイルオーバー、認証、レジストリヘルパー |
  | `plugin-sdk/music-generation` | 音楽生成ヘルパー | 音楽生成provider/request/result型 |
  | `plugin-sdk/music-generation-core` | 共有音楽生成コア | 音楽生成型、フェイルオーバーヘルパー、provider検索、およびmodel-ref解析 |
  | `plugin-sdk/video-generation` | 動画生成ヘルパー | 動画生成provider/request/result型 |
  | `plugin-sdk/video-generation-core` | 共有動画生成コア | 動画生成型、フェイルオーバーヘルパー、provider検索、およびmodel-ref解析 |
  | `plugin-sdk/interactive-runtime` | 対話型返信ヘルパー | 対話型返信ペイロードの正規化/縮約 |
  | `plugin-sdk/channel-config-primitives` | channel設定プリミティブ | 用途を絞ったchannel config-schemaプリミティブ |
  | `plugin-sdk/channel-config-writes` | channel設定書き込みヘルパー | channel設定書き込み認可ヘルパー |
  | `plugin-sdk/channel-plugin-common` | 共有channelプレリュード | 共有channel pluginプレリュードエクスポート |
  | `plugin-sdk/channel-status` | channelステータスヘルパー | 共有channelステータスのスナップショット/サマリーヘルパー |
  | `plugin-sdk/allowlist-config-edit` | Allowlist設定ヘルパー | Allowlist設定の編集/読み取りヘルパー |
  | `plugin-sdk/group-access` | グループアクセスヘルパー | 共有group-access判定ヘルパー |
  | `plugin-sdk/direct-dm` | ダイレクトDMヘルパー | 共有ダイレクトDM認証/ガードヘルパー |
  | `plugin-sdk/extension-shared` | 共有extensionヘルパー | passive-channel/statusおよびambient proxyヘルパープリミティブ |
  | `plugin-sdk/webhook-targets` | Webhookターゲットヘルパー | Webhookターゲットレジストリおよびroute-installヘルパー |
  | `plugin-sdk/webhook-path` | Webhookパスヘルパー | Webhookパス正規化ヘルパー |
  | `plugin-sdk/web-media` | 共有webメディアヘルパー | リモート/ローカルメディア読み込みヘルパー |
  | `plugin-sdk/zod` | zod再エクスポート | Plugin SDK利用者向けに再エクスポートされた `zod` |
  | `plugin-sdk/memory-core` | 同梱memory-coreヘルパー | メモリマネージャー/設定/ファイル/CLIヘルパーsurface |
  | `plugin-sdk/memory-core-engine-runtime` | メモリエンジンruntimeファサード | メモリインデックス/検索runtimeファサード |
  | `plugin-sdk/memory-core-host-engine-foundation` | メモリホスト基盤エンジン | メモリホスト基盤エンジンのエクスポート |
  | `plugin-sdk/memory-core-host-engine-embeddings` | メモリホスト埋め込みエンジン | メモリ埋め込み契約、レジストリアクセス、ローカルprovider、および汎用バッチ/リモートヘルパー。具体的なリモートproviderは各所有pluginにあります |
  | `plugin-sdk/memory-core-host-engine-qmd` | メモリホストQMDエンジン | メモリホストQMDエンジンのエクスポート |
  | `plugin-sdk/memory-core-host-engine-storage` | メモリホストストレージエンジン | メモリホストストレージエンジンのエクスポート |
  | `plugin-sdk/memory-core-host-multimodal` | メモリホストマルチモーダルヘルパー | メモリホストマルチモーダルヘルパー |
  | `plugin-sdk/memory-core-host-query` | メモリホストクエリヘルパー | メモリホストクエリヘルパー |
  | `plugin-sdk/memory-core-host-secret` | メモリホストsecretヘルパー | メモリホストsecretヘルパー |
  | `plugin-sdk/memory-core-host-events` | メモリホストイベントジャーナルヘルパー | メモリホストイベントジャーナルヘルパー |
  | `plugin-sdk/memory-core-host-status` | メモリホストステータスヘルパー | メモリホストステータスヘルパー |
  | `plugin-sdk/memory-core-host-runtime-cli` | メモリホストCLI runtime | メモリホストCLI runtimeヘルパー |
  | `plugin-sdk/memory-core-host-runtime-core` | メモリホストコアruntime | メモリホストコアruntimeヘルパー |
  | `plugin-sdk/memory-core-host-runtime-files` | メモリホストファイル/runtimeヘルパー | メモリホストファイル/runtimeヘルパー |
  | `plugin-sdk/memory-host-core` | メモリホストコアruntimeエイリアス | メモリホストコアruntimeヘルパーのベンダーニュートラルなエイリアス |
  | `plugin-sdk/memory-host-events` | メモリホストイベントジャーナルエイリアス | メモリホストイベントジャーナルヘルパーのベンダーニュートラルなエイリアス |
  | `plugin-sdk/memory-host-files` | メモリホストファイル/runtimeエイリアス | メモリホストファイル/runtimeヘルパーのベンダーニュートラルなエイリアス |
  | `plugin-sdk/memory-host-markdown` | 管理対象markdownヘルパー | memory隣接plugin向けの共有managed-markdownヘルパー |
  | `plugin-sdk/memory-host-search` | Active Memory検索ファサード | 遅延active-memory search-manager runtimeファサード |
  | `plugin-sdk/memory-host-status` | メモリホストステータスエイリアス | メモリホストステータスヘルパーのベンダーニュートラルなエイリアス |
  | `plugin-sdk/memory-lancedb` | 同梱memory-lancedbヘルパー | Memory-lancedbヘルパーsurface |
  | `plugin-sdk/testing` | テストユーティリティ | テストヘルパーとモック |
</Accordion>

このテーブルは、完全なSDK surfaceではなく、意図的に一般的な移行用サブセットに絞っています。200以上あるエントリーポイントの完全な一覧は `scripts/lib/plugin-sdk-entrypoints.json` にあります。

その一覧には、`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、`plugin-sdk/zalo`、`plugin-sdk/zalo-setup`、`plugin-sdk/matrix*` のような同梱pluginヘルパーシームも引き続き含まれています。これらは同梱pluginの保守と互換性のために引き続きエクスポートされていますが、一般的な移行テーブルからは意図的に除外されており、新しいpluginコードの推奨移行先ではありません。

同じルールは、次のような他の同梱ヘルパーファミリーにも適用されます。

- ブラウザーサポートヘルパー: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- `plugin-sdk/googlechat`、`plugin-sdk/zalouser`、`plugin-sdk/bluebubbles*`、`plugin-sdk/mattermost*`、`plugin-sdk/msteams`、`plugin-sdk/nextcloud-talk`、`plugin-sdk/nostr`、`plugin-sdk/tlon`、`plugin-sdk/twitch`、`plugin-sdk/github-copilot-login`、`plugin-sdk/github-copilot-token`、`plugin-sdk/diagnostics-otel`、`plugin-sdk/diffs`、`plugin-sdk/llm-task`、`plugin-sdk/thread-ownership`、`plugin-sdk/voice-call` のような同梱ヘルパー/plugin surface

`plugin-sdk/github-copilot-token` は現在、用途を絞ったトークンヘルパーsurfaceである `DEFAULT_COPILOT_API_BASE_URL`、`deriveCopilotApiBaseUrlFromToken`、`resolveCopilotApiToken` を公開しています。

用途に合った最も狭いインポートを使用してください。エクスポートが見つからない場合は、`src/plugin-sdk/` のソースを確認するか、Discordで質問してください。

## 削除タイムライン

| 時期 | 何が起きるか |
| ---------------------- | ----------------------------------------------------------------------- |
| **現在** | 非推奨surfaceは実行時警告を出力します |
| **次のメジャーリリース** | 非推奨surfaceは削除され、それらをまだ使用しているpluginは動作しなくなります |

すべてのcore pluginはすでに移行済みです。外部pluginは次のメジャーリリース前に移行する必要があります。

## 警告を一時的に抑制する

移行作業中は、これらの環境変数を設定してください。

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

これは一時的な回避策であり、恒久的な解決策ではありません。

## 関連

- [はじめに](/ja-JP/plugins/building-plugins) — 最初のpluginを作成する
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全なサブパスインポートリファレンス
- [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — channel pluginの作成
- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — provider pluginの作成
- [Plugin Internals](/ja-JP/plugins/architecture) — アーキテクチャの詳細
- [Plugin Manifest](/ja-JP/plugins/manifest) — マニフェストスキーマリファレンス
