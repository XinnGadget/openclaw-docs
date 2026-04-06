---
read_when:
    - OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED 警告が表示されたとき
    - OPENCLAW_EXTENSION_API_DEPRECATED 警告が表示されたとき
    - プラグインを最新のプラグインアーキテクチャへ更新しているとき
    - 外部のOpenClawプラグインを保守しているとき
sidebarTitle: Migrate to SDK
summary: レガシーな後方互換レイヤーから最新のプラグインSDKへ移行する
title: プラグインSDK移行
x-i18n:
    generated_at: "2026-04-06T03:10:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: b71ce69b30c3bb02da1b263b1d11dc3214deae5f6fc708515e23b5a1c7bb7c8f
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# プラグインSDK移行

OpenClawは、広範な後方互換レイヤーから、焦点を絞った文書化済みのimportを持つ最新のプラグイン
アーキテクチャへ移行しました。新しいアーキテクチャ以前にプラグインを構築した場合、このガイドが移行に役立ちます。

## 何が変わるのか

古いプラグインシステムでは、プラグインが単一のエントリポイントから必要なものを何でもimportできる、
非常に広い2つのサーフェスが提供されていました。

- **`openclaw/plugin-sdk/compat`** — 数十個の
  ヘルパーを再エクスポートする単一import。新しい
  プラグインアーキテクチャの構築中に、古いフックベースのプラグインを動作させ続けるために導入されました。
- **`openclaw/extension-api`** — 埋め込みエージェントランナーのような
  ホスト側ヘルパーへプラグインが直接アクセスできるようにするブリッジ。

これら2つのサーフェスは現在 **非推奨** です。ランタイムではまだ動作しますが、新しい
プラグインは使用してはいけません。また既存のプラグインも、次のメジャーリリースで削除される前に移行する必要があります。

<Warning>
  この後方互換レイヤーは、将来のメジャーリリースで削除されます。
  これらのサーフェスからまだimportしているプラグインは、その時点で壊れます。
</Warning>

## なぜ変更されたのか

古いアプローチには問題がありました。

- **起動が遅い** — 1つのヘルパーをimportするだけで、無関係な数十のモジュールが読み込まれていました
- **循環依存** — 広範な再エクスポートによってimportサイクルが簡単に生じていました
- **不明確なAPIサーフェス** — どのexportが安定していて、どれが内部実装なのか判別する方法がありませんでした

最新のプラグインSDKはこれを解決します。各importパス（`openclaw/plugin-sdk/\<subpath\>`）
は、小さく自己完結したモジュールであり、明確な目的と文書化された契約を持ちます。

バンドルされたチャンネル向けのレガシーprovider便宜シームもなくなりました。  
`openclaw/plugin-sdk/slack`、`openclaw/plugin-sdk/discord`、  
`openclaw/plugin-sdk/signal`、`openclaw/plugin-sdk/whatsapp`、  
チャンネル名付きのヘルパーシーム、および  
`openclaw/plugin-sdk/telegram-core` のようなimportは、安定した
プラグイン契約ではなく、プライベートなモノレポ用ショートカットでした。代わりに、細い汎用SDK subpathを使ってください。バンドルされたプラグインworkspace内では、provider所有ヘルパーはそのプラグイン自身の
`api.ts` または `runtime-api.ts` に置いてください。

現在のバンドルproviderの例:

- Anthropicは、Claude固有のstreamヘルパーを自身の `api.ts` /
  `contract-api.ts` シームに保持しています
- OpenAIは、providerビルダー、デフォルトモデルヘルパー、realtime provider
  ビルダーを自身の `api.ts` に保持しています
- OpenRouterは、providerビルダーとオンボーディング/configヘルパーを自身の
  `api.ts` に保持しています

## 移行方法

<Steps>
  <Step title="Windowsラッパーのフォールバック動作を監査する">
    プラグインが `openclaw/plugin-sdk/windows-spawn` を使っている場合、解決できないWindows
    `.cmd`/`.bat` ラッパーは、明示的に
    `allowShellFallback: true` を渡さない限り、現在はfail closedになります。

    ```typescript
    // Before
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // After
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // シェル経由のフォールバックを意図的に受け入れる、信頼された互換呼び出し元にのみ設定します。
      allowShellFallback: true,
    });
    ```

    呼び出し元が意図的にシェルフォールバックへ依存していない場合は、
    `allowShellFallback` を設定せず、代わりに投げられるエラーを処理してください。

  </Step>

  <Step title="非推奨importを見つける">
    プラグイン内で、いずれかの非推奨サーフェスからのimportを検索します。

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="焦点を絞ったimportに置き換える">
    古いサーフェスの各exportは、特定の最新importパスへ対応しています。

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

    ホスト側ヘルパーについては、直接importする代わりに注入されたプラグインランタイムを使用します。

    ```typescript
    // Before (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After (injected runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    同じパターンは、他のレガシーブリッジヘルパーにも適用されます。

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

  <Step title="ビルドしてテストする">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## importパスリファレンス

<Accordion title="よく使うimportパステーブル">
  | Import path | 目的 | 主なexport |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | 正式なプラグインエントリヘルパー | `definePluginEntry` |
  | `plugin-sdk/core` | チャンネルエントリ定義/ビルダー向けのレガシーなアンブレラ再エクスポート | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | ルートconfigスキーマexport | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | 単一providerエントリヘルパー | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | 焦点を絞ったチャンネルエントリ定義とビルダー | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | 共通セットアップウィザードヘルパー | Allowlistプロンプト、セットアップステータスビルダー |
  | `plugin-sdk/setup-runtime` | セットアップ時ランタイムヘルパー | import-safeなセットアップpatchアダプター、lookup-noteヘルパー、`promptResolvedAllowFrom`, `splitSetupEntries`, 委譲セットアッププロキシ |
  | `plugin-sdk/setup-adapter-runtime` | セットアップアダプターヘルパー | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | セットアップtoolingヘルパー | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | マルチアカウントヘルパー | アカウント一覧/config/アクションゲートヘルパー |
  | `plugin-sdk/account-id` | account-id ヘルパー | `DEFAULT_ACCOUNT_ID`, account-id 正規化 |
  | `plugin-sdk/account-resolution` | アカウント参照ヘルパー | アカウント参照 + デフォルトフォールバックヘルパー |
  | `plugin-sdk/account-helpers` | 細いアカウントヘルパー | アカウント一覧/アカウントアクションヘルパー |
  | `plugin-sdk/channel-setup` | セットアップウィザードアダプター | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, および `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DMペアリング基本要素 | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | 返信プレフィックス + typing 配線 | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Configアダプターファクトリー | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Configスキーマビルダー | チャンネルconfigスキーマ型 |
  | `plugin-sdk/telegram-command-config` | Telegramコマンドconfigヘルパー | コマンド名正規化、説明トリミング、重複/競合検証 |
  | `plugin-sdk/channel-policy` | グループ/DMポリシー解決 | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | アカウントステータス追跡 | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | 受信envelopeヘルパー | 共通ルート + envelopeビルダーヘルパー |
  | `plugin-sdk/inbound-reply-dispatch` | 受信返信ヘルパー | 共通の記録とディスパッチヘルパー |
  | `plugin-sdk/messaging-targets` | メッセージングターゲット解析 | ターゲット解析/照合ヘルパー |
  | `plugin-sdk/outbound-media` | 送信メディアヘルパー | 共通の送信メディア読み込み |
  | `plugin-sdk/outbound-runtime` | 送信ランタイムヘルパー | 送信アイデンティティ/送信delegateヘルパー |
  | `plugin-sdk/thread-bindings-runtime` | スレッドbindingヘルパー | スレッドbindingライフサイクルとアダプターヘルパー |
  | `plugin-sdk/agent-media-payload` | レガシーメディアペイロードヘルパー | レガシーフィールドレイアウト向けエージェントメディアペイロードビルダー |
  | `plugin-sdk/channel-runtime` | 非推奨の互換shim | レガシーチャンネルランタイムユーティリティのみ |
  | `plugin-sdk/channel-send-result` | 送信結果型 | 返信結果型 |
  | `plugin-sdk/runtime-store` | 永続プラグインストレージ | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | 広範なランタイムヘルパー | ランタイム/ロギング/バックアップ/プラグインインストールヘルパー |
  | `plugin-sdk/runtime-env` | 細いランタイムenvヘルパー | ロガー/ランタイムenv、タイムアウト、再試行、バックオフヘルパー |
  | `plugin-sdk/plugin-runtime` | 共通プラグインランタイムヘルパー | プラグインコマンド/フック/http/インタラクティブヘルパー |
  | `plugin-sdk/hook-runtime` | フックパイプラインヘルパー | 共通webhook/internal hookパイプラインヘルパー |
  | `plugin-sdk/lazy-runtime` | 遅延ランタイムヘルパー | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | processヘルパー | 共通execヘルパー |
  | `plugin-sdk/cli-runtime` | CLIランタイムヘルパー | コマンド整形、待機、バージョンヘルパー |
  | `plugin-sdk/gateway-runtime` | Gatewayヘルパー | Gatewayクライアントとchannel-status patchヘルパー |
  | `plugin-sdk/config-runtime` | Configヘルパー | Config読み込み/書き込みヘルパー |
  | `plugin-sdk/telegram-command-config` | Telegramコマンドヘルパー | バンドルされたTelegram契約サーフェスが使えない場合の、フォールバックで安定したTelegramコマンド検証ヘルパー |
  | `plugin-sdk/approval-runtime` | 承認プロンプトヘルパー | Exec/plugin 承認ペイロード、承認capability/profileヘルパー、ネイティブ承認ルーティング/ランタイムヘルパー |
  | `plugin-sdk/approval-auth-runtime` | 承認authヘルパー | 承認者解決、同一チャットアクションauth |
  | `plugin-sdk/approval-client-runtime` | 承認クライアントヘルパー | ネイティブexec承認profile/filterヘルパー |
  | `plugin-sdk/approval-delivery-runtime` | 承認配信ヘルパー | ネイティブ承認capability/配信アダプター |
  | `plugin-sdk/approval-native-runtime` | 承認ターゲットヘルパー | ネイティブ承認ターゲット/アカウントbindingヘルパー |
  | `plugin-sdk/approval-reply-runtime` | 承認返信ヘルパー | Exec/plugin 承認返信ペイロードヘルパー |
  | `plugin-sdk/security-runtime` | セキュリティヘルパー | 共通の信頼、DMゲート、外部コンテンツ、secret収集ヘルパー |
  | `plugin-sdk/ssrf-policy` | SSRFポリシーヘルパー | ホストallowlistとプライベートネットワークポリシーヘルパー |
  | `plugin-sdk/ssrf-runtime` | SSRFランタイムヘルパー | pinned-dispatcher、guarded fetch、SSRFポリシーヘルパー |
  | `plugin-sdk/collection-runtime` | 境界付きキャッシュヘルパー | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | 診断ゲートヘルパー | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | エラー整形ヘルパー | `formatUncaughtError`, `isApprovalNotFoundError`, エラーグラフヘルパー |
  | `plugin-sdk/fetch-runtime` | ラップ済みfetch/プロキシヘルパー | `resolveFetch`, プロキシヘルパー |
  | `plugin-sdk/host-runtime` | ホスト正規化ヘルパー | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | 再試行ヘルパー | `RetryConfig`, `retryAsync`, ポリシーランナー |
  | `plugin-sdk/allow-from` | Allowlist整形 | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Allowlist入力マッピング | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | コマンドゲートとコマンドサーフェスヘルパー | `resolveControlCommandGate`, 送信者認可ヘルパー, コマンドレジストリヘルパー |
  | `plugin-sdk/secret-input` | secret入力解析 | secret入力ヘルパー |
  | `plugin-sdk/webhook-ingress` | webhookリクエストヘルパー | webhookターゲットユーティリティ |
  | `plugin-sdk/webhook-request-guards` | webhook本文ガードヘルパー | リクエスト本文読み取り/制限ヘルパー |
  | `plugin-sdk/reply-runtime` | 共通返信ランタイム | 受信ディスパッチ、heartbeat、返信プランナー、チャンク化 |
  | `plugin-sdk/reply-dispatch-runtime` | 細い返信ディスパッチヘルパー | finalize + provider dispatchヘルパー |
  | `plugin-sdk/reply-history` | 返信履歴ヘルパー | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | 返信参照プランニング | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | 返信チャンクヘルパー | テキスト/markdown チャンクヘルパー |
  | `plugin-sdk/session-store-runtime` | セッションストアヘルパー | ストアパス + updated-at ヘルパー |
  | `plugin-sdk/state-paths` | 状態パスヘルパー | 状態ディレクトリとOAuthディレクトリヘルパー |
  | `plugin-sdk/routing` | ルーティング/セッションキーヘルパー | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, セッションキー正規化ヘルパー |
  | `plugin-sdk/status-helpers` | チャンネルstatusヘルパー | チャンネル/アカウントstatusサマリービルダー、runtime-state デフォルト、issueメタデータヘルパー |
  | `plugin-sdk/target-resolver-runtime` | ターゲットリゾルバーヘルパー | 共通ターゲットリゾルバーヘルパー |
  | `plugin-sdk/string-normalization-runtime` | 文字列正規化ヘルパー | slug/文字列正規化ヘルパー |
  | `plugin-sdk/request-url` | リクエストURLヘルパー | リクエスト風入力から文字列URLを抽出 |
  | `plugin-sdk/run-command` | 時間付きコマンドヘルパー | stdout/stderr を正規化した時間付きコマンドランナー |
  | `plugin-sdk/param-readers` | パラメーターリーダー | 共通tool/CLIパラメーターリーダー |
  | `plugin-sdk/tool-send` | tool送信抽出 | tool引数から正規の送信ターゲットフィールドを抽出 |
  | `plugin-sdk/temp-path` | 一時パスヘルパー | 共通一時ダウンロードパスヘルパー |
  | `plugin-sdk/logging-core` | ロギングヘルパー | サブシステムロガーとredactionヘルパー |
  | `plugin-sdk/markdown-table-runtime` | Markdownテーブルヘルパー | Markdownテーブルモードヘルパー |
  | `plugin-sdk/reply-payload` | メッセージ返信型 | 返信ペイロード型 |
  | `plugin-sdk/provider-setup` | 厳選されたローカル/セルフホストproviderセットアップヘルパー | セルフホストprovider検出/configヘルパー |
  | `plugin-sdk/self-hosted-provider-setup` | 焦点を絞ったOpenAI互換セルフホストproviderセットアップヘルパー | 同じセルフホストprovider検出/configヘルパー |
  | `plugin-sdk/provider-auth-runtime` | providerランタイムauthヘルパー | ランタイムAPIキー解決ヘルパー |
  | `plugin-sdk/provider-auth-api-key` | provider APIキーセットアップヘルパー | APIキーオンボーディング/profile書き込みヘルパー |
  | `plugin-sdk/provider-auth-result` | provider auth-result ヘルパー | 標準OAuth auth-result ビルダー |
  | `plugin-sdk/provider-auth-login` | providerインタラクティブログインヘルパー | 共通インタラクティブログインヘルパー |
  | `plugin-sdk/provider-env-vars` | provider環境変数ヘルパー | provider auth環境変数参照ヘルパー |
  | `plugin-sdk/provider-model-shared` | 共通provider model/replay ヘルパー | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, 共通replay-policyビルダー、provider endpointヘルパー、model-id 正規化ヘルパー |
  | `plugin-sdk/provider-catalog-shared` | 共通providerカタログヘルパー | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | providerオンボーディングpatch | オンボーディングconfigヘルパー |
  | `plugin-sdk/provider-http` | provider HTTPヘルパー | 汎用provider HTTP/endpoint capabilityヘルパー |
  | `plugin-sdk/provider-web-fetch` | provider web-fetch ヘルパー | web-fetch provider登録/キャッシュヘルパー |
  | `plugin-sdk/provider-web-search` | provider web-search ヘルパー | web-search provider登録/キャッシュ/configヘルパー |
  | `plugin-sdk/provider-tools` | provider tool/スキーマ互換ヘルパー | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Geminiスキーマクリーンアップ + diagnostics、および `resolveXaiModelCompatPatch` / `applyXaiModelCompat` などのxAI互換ヘルパー |
  | `plugin-sdk/provider-usage` | provider使用量ヘルパー | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` などのprovider使用量ヘルパー |
  | `plugin-sdk/provider-stream` | provider streamラッパーヘルパー | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, streamラッパー型、および共通Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot ラッパーヘルパー |
  | `plugin-sdk/keyed-async-queue` | 順序付きasyncキュー | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | 共通メディアヘルパー | メディア取得/変換/保存ヘルパー、およびメディアペイロードビルダー |
  | `plugin-sdk/media-understanding` | media-understanding ヘルパー | media-understanding provider型、およびprovider向け画像/音声ヘルパーexport |
  | `plugin-sdk/text-runtime` | 共通テキストヘルパー | アシスタント可視テキストの除去、markdown描画/チャンク化/テーブルヘルパー、redactionヘルパー、directive-tagヘルパー、安全なテキストユーティリティ、および関連するテキスト/ロギングヘルパー |
  | `plugin-sdk/text-chunking` | テキストチャンク化ヘルパー | 送信テキストチャンク化ヘルパー |
  | `plugin-sdk/speech` | Speechヘルパー | Speech provider型、およびprovider向けdirective、registry、検証ヘルパー |
  | `plugin-sdk/speech-core` | 共通Speechコア | Speech provider型、registry、directive、正規化 |
  | `plugin-sdk/realtime-transcription` | realtime transcription ヘルパー | provider型とregistryヘルパー |
  | `plugin-sdk/realtime-voice` | realtime voice ヘルパー | provider型とregistryヘルパー |
  | `plugin-sdk/image-generation-core` | 共通image-generation コア | image-generation 型、フェイルオーバー、auth、registryヘルパー |
  | `plugin-sdk/music-generation` | music-generation ヘルパー | music-generation provider/request/result 型 |
  | `plugin-sdk/music-generation-core` | 共通music-generation コア | music-generation 型、フェイルオーバーヘルパー、provider参照、model-ref解析 |
  | `plugin-sdk/video-generation` | video-generation ヘルパー | video-generation provider/request/result 型 |
  | `plugin-sdk/video-generation-core` | 共通video-generation コア | video-generation 型、フェイルオーバーヘルパー、provider参照、model-ref解析 |
  | `plugin-sdk/interactive-runtime` | インタラクティブ返信ヘルパー | インタラクティブ返信ペイロード正規化/縮約 |
  | `plugin-sdk/channel-config-primitives` | チャンネルconfig基本要素 | 細いチャンネルconfig-schema 基本要素 |
  | `plugin-sdk/channel-config-writes` | チャンネルconfig書き込みヘルパー | チャンネルconfig書き込み認可ヘルパー |
  | `plugin-sdk/channel-plugin-common` | 共通チャンネルプレリュード | 共通チャンネルプラグインプレリュードexport |
  | `plugin-sdk/channel-status` | チャンネルstatusヘルパー | 共通チャンネルstatusスナップショット/サマリーヘルパー |
  | `plugin-sdk/allowlist-config-edit` | Allowlist configヘルパー | Allowlist config編集/読み取りヘルパー |
  | `plugin-sdk/group-access` | グループアクセスヘルパー | 共通グループアクセス判定ヘルパー |
  | `plugin-sdk/direct-dm` | ダイレクトDMヘルパー | 共通ダイレクトDM auth/ガードヘルパー |
  | `plugin-sdk/extension-shared` | 共通拡張ヘルパー | passive-channel/status ヘルパー基本要素 |
  | `plugin-sdk/webhook-targets` | webhookターゲットヘルパー | webhookターゲットregistryとroute-installヘルパー |
  | `plugin-sdk/webhook-path` | webhookパスヘルパー | webhookパス正規化ヘルパー |
  | `plugin-sdk/web-media` | 共通webメディアヘルパー | リモート/ローカルメディア読み込みヘルパー |
  | `plugin-sdk/zod` | Zod再エクスポート | プラグインSDK利用者向けに再エクスポートされた `zod` |
  | `plugin-sdk/memory-core` | バンドルされたmemory-core ヘルパー | Memory manager/config/file/CLI ヘルパーサーフェス |
  | `plugin-sdk/memory-core-engine-runtime` | Memory engine ランタイムファサード | Memory index/search ランタイムファサード |
  | `plugin-sdk/memory-core-host-engine-foundation` | Memory host foundation engine | Memory host foundation engine export |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Memory host embedding engine | Memory host embedding engine export |
  | `plugin-sdk/memory-core-host-engine-qmd` | Memory host QMD engine | Memory host QMD engine export |
  | `plugin-sdk/memory-core-host-engine-storage` | Memory host storage engine | Memory host storage engine export |
  | `plugin-sdk/memory-core-host-multimodal` | Memory host multimodal ヘルパー | Memory host multimodal ヘルパー |
  | `plugin-sdk/memory-core-host-query` | Memory host query ヘルパー | Memory host query ヘルパー |
  | `plugin-sdk/memory-core-host-secret` | Memory host secret ヘルパー | Memory host secret ヘルパー |
  | `plugin-sdk/memory-core-host-status` | Memory host status ヘルパー | Memory host status ヘルパー |
  | `plugin-sdk/memory-core-host-runtime-cli` | Memory host CLIランタイム | Memory host CLIランタイムヘルパー |
  | `plugin-sdk/memory-core-host-runtime-core` | Memory host coreランタイム | Memory host coreランタイムヘルパー |
  | `plugin-sdk/memory-core-host-runtime-files` | Memory host file/runtime ヘルパー | Memory host file/runtime ヘルパー |
  | `plugin-sdk/memory-lancedb` | バンドルされたmemory-lancedb ヘルパー | Memory-lancedb ヘルパーサーフェス |
  | `plugin-sdk/testing` | テストユーティリティ | テストヘルパーとモック |
</Accordion>

この表は意図的に、完全なSDK
サーフェスではなく、一般的な移行向けサブセットです。200以上のエントリポイントを含む完全な一覧は
`scripts/lib/plugin-sdk-entrypoints.json` にあります。

その一覧には、`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、`plugin-sdk/zalo`、
`plugin-sdk/zalo-setup`、`plugin-sdk/matrix*` のような、バンドルプラグイン用ヘルパーシームもまだ含まれています。これらはバンドルプラグイン保守と互換性のために引き続きexportされていますが、一般的な移行テーブルからは意図的に省かれており、新しいプラグインコードの推奨ターゲットではありません。

同じルールは、他のバンドルヘルパーファミリーにも適用されます。たとえば:

- browserサポートヘルパー: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- `plugin-sdk/googlechat`、
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` のような
  バンドルヘルパー/プラグインサーフェス

`plugin-sdk/github-copilot-token` は現在、細いトークンヘルパー
サーフェス `DEFAULT_COPILOT_API_BASE_URL`、
`deriveCopilotApiBaseUrlFromToken`、`resolveCopilotApiToken` を公開しています。

用途に合う最も細いimportを使用してください。exportが見つからない場合は、
`src/plugin-sdk/` のソースを確認するか、Discordで質問してください。

## 削除タイムライン

| いつ | 何が起きるか |
| ---------------------- | ----------------------------------------------------------------------- |
| **現在**                | 非推奨サーフェスはランタイム警告を出します |
| **次のメジャーリリース** | 非推奨サーフェスは削除され、それらをまだ使っているプラグインは動作しなくなります |

すべてのコアプラグインはすでに移行済みです。外部プラグインは、
次のメジャーリリース前に移行する必要があります。

## 一時的に警告を抑制する

移行作業中は、これらの環境変数を設定してください。

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

これは一時的な回避策であり、恒久的な解決策ではありません。

## 関連

- [はじめに](/ja-JP/plugins/building-plugins) — 最初のプラグインを作る
- [SDK Overview](/ja-JP/plugins/sdk-overview) — subpath importの完全なリファレンス
- [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — チャンネルプラグインの構築
- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — providerプラグインの構築
- [Plugin Internals](/ja-JP/plugins/architecture) — アーキテクチャの詳細
- [Plugin Manifest](/ja-JP/plugins/manifest) — manifestスキーマリファレンス
