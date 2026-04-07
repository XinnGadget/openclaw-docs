---
read_when:
    - OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED警告が表示された場合
    - OPENCLAW_EXTENSION_API_DEPRECATED警告が表示された場合
    - pluginを最新のpluginアーキテクチャへ更新している場合
    - 外部のOpenClaw pluginを保守している場合
sidebarTitle: Migrate to SDK
summary: レガシーな後方互換レイヤーから最新のplugin SDKへ移行する
title: Plugin SDK移行
x-i18n:
    generated_at: "2026-04-07T04:45:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3691060e9dc00ca8bee49240a047f0479398691bd14fb96e9204cc9243fdb32c
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin SDK移行

OpenClawは、広範な後方互換レイヤーから、焦点が絞られ文書化されたインポートを持つ最新のplugin
アーキテクチャへ移行しました。あなたのpluginが新しいアーキテクチャ以前に作られたものであれば、
このガイドが移行を支援します。

## 何が変わるのか

旧pluginシステムは、pluginが単一のエントリーポイントから必要なものを何でもインポートできる、
大きく開かれた2つのサーフェスを提供していました。

- **`openclaw/plugin-sdk/compat`** — 数十の
  ヘルパーを再エクスポートする単一インポート。新しいpluginアーキテクチャの構築中に、
  古いフックベースのpluginを動作させ続けるために導入されました。
- **`openclaw/extension-api`** — pluginに、埋め込みagent runnerのような
  ホスト側ヘルパーへの直接アクセスを与えるブリッジ。

これら2つのサーフェスは現在、どちらも**非推奨**です。ランタイムではまだ動作しますが、新しい
pluginはそれらを使ってはならず、既存のpluginも次のメジャーリリースで削除される前に移行すべきです。

<Warning>
  この後方互換レイヤーは、将来のメジャーリリースで削除されます。
  引き続きこれらのサーフェスからインポートしているpluginは、その時点で壊れます。
</Warning>

## なぜこれが変わったのか

旧アプローチには問題がありました。

- **起動が遅い** — 1つのヘルパーをインポートすると、無関係な多数のモジュールまで読み込まれる
- **循環依存** — 広範な再エクスポートにより、インポートサイクルが簡単に作れてしまう
- **不明瞭なAPIサーフェス** — どのエクスポートが安定していて、どれが内部用かを区別できない

最新のplugin SDKはこれを改善します。各インポートパス（`openclaw/plugin-sdk/\<subpath\>`）
は、明確な目的と文書化された契約を持つ、小さく自己完結したモジュールです。

バンドル済みchannel向けのレガシーなprovider便利シームも廃止されました。
`openclaw/plugin-sdk/slack`、`openclaw/plugin-sdk/discord`、
`openclaw/plugin-sdk/signal`、`openclaw/plugin-sdk/whatsapp`、
channelブランドのヘルパーシーム、および
`openclaw/plugin-sdk/telegram-core`のようなインポートは、安定したplugin契約ではなく、
プライベートなmono-repoショートカットでした。代わりに、より狭い汎用SDKサブパスを使ってください。バンドル済みpluginワークスペース内では、
providerが所有するヘルパーは、そのplugin自身の
`api.ts`または`runtime-api.ts`に保持してください。

現在のバンドル済みproviderの例:

- Anthropicは、Claude固有のストリームヘルパーを自身の`api.ts` /
  `contract-api.ts`シームに保持している
- OpenAIは、provider builder、デフォルトモデルヘルパー、realtime provider
  builderを自身の`api.ts`に保持している
- OpenRouterは、provider builderとオンボーディング/設定ヘルパーを自身の
  `api.ts`に保持している

## 移行方法

<Steps>
  <Step title="Windowsラッパーのフォールバック動作を監査する">
    あなたのpluginが`openclaw/plugin-sdk/windows-spawn`を使っている場合、解決できないWindowsの
    `.cmd`/`.bat`ラッパーは、明示的に
    `allowShellFallback: true`を渡さない限り、フェイルクローズするようになりました。

    ```typescript
    // Before
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // After
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // 信頼された互換性呼び出し元で、意図的に
      // シェル経由のフォールバックを受け入れる場合にのみ設定します。
      allowShellFallback: true,
    });
    ```

    呼び出し元が意図的にシェルフォールバックに依存していない場合は、
    `allowShellFallback`を設定せず、代わりに投げられたエラーを処理してください。

  </Step>

  <Step title="非推奨インポートを見つける">
    あなたのpluginで、どちらかの非推奨サーフェスからのインポートを検索してください。

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="用途を絞ったインポートに置き換える">
    旧サーフェスからの各エクスポートは、対応する最新のインポートパスにマップされます。

    ```typescript
    // Before（非推奨の後方互換レイヤー）
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // After（最新の用途を絞ったインポート）
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    ホスト側ヘルパーについては、直接インポートする代わりに、注入されたplugin runtimeを使用してください。

    ```typescript
    // Before（非推奨のextension-apiブリッジ）
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After（注入されたruntime）
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    同じパターンは、他のレガシーブリッジヘルパーにも適用されます。

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

  <Step title="ビルドとテスト">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## インポートパス リファレンス

<Accordion title="一般的なインポートパステーブル">
  | Import path | Purpose | Key exports |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | 正規のpluginエントリーヘルパー | `definePluginEntry` |
  | `plugin-sdk/core` | channelエントリー定義/ビルダー向けのレガシーなアンブレラ再エクスポート | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | ルート設定スキーマのエクスポート | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | 単一providerエントリーヘルパー | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | 用途を絞ったchannelエントリー定義とビルダー | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | 共通のセットアップウィザードヘルパー | allowlistプロンプト、セットアップステータスビルダー |
  | `plugin-sdk/setup-runtime` | セットアップ時ランタイムヘルパー | インポートセーフなsetup patch adapter、lookup-noteヘルパー、`promptResolvedAllowFrom`、`splitSetupEntries`、委譲されたセットアッププロキシ |
  | `plugin-sdk/setup-adapter-runtime` | Setup adapterヘルパー | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | セットアップツール用ヘルパー | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | マルチアカウントヘルパー | アカウント一覧/設定/アクションゲートのヘルパー |
  | `plugin-sdk/account-id` | account-idヘルパー | `DEFAULT_ACCOUNT_ID`、account-id正規化 |
  | `plugin-sdk/account-resolution` | アカウントlookupヘルパー | アカウントlookup + デフォルトフォールバックヘルパー |
  | `plugin-sdk/account-helpers` | 狭い範囲のアカウントヘルパー | アカウント一覧/アカウントアクションヘルパー |
  | `plugin-sdk/channel-setup` | セットアップウィザードadapter | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`、および`DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DMペアリングの基本要素 | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | 返信プレフィックス + typing配線 | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | 設定adapterファクトリー | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | 設定スキーマビルダー | channel config schema型 |
  | `plugin-sdk/telegram-command-config` | Telegramコマンド設定ヘルパー | コマンド名正規化、説明のトリミング、重複/競合の検証 |
  | `plugin-sdk/channel-policy` | グループ/DMポリシー解決 | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | アカウント状態追跡 | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | inbound envelopeヘルパー | 共通のルート + envelope builderヘルパー |
  | `plugin-sdk/inbound-reply-dispatch` | inbound replyヘルパー | 共通のrecord-and-dispatchヘルパー |
  | `plugin-sdk/messaging-targets` | メッセージ送信先解析 | 送信先解析/照合ヘルパー |
  | `plugin-sdk/outbound-media` | outbound mediaヘルパー | 共通のoutbound media読み込み |
  | `plugin-sdk/outbound-runtime` | outbound runtimeヘルパー | outbound identity/send delegateヘルパー |
  | `plugin-sdk/thread-bindings-runtime` | thread-bindingヘルパー | thread-bindingライフサイクルとadapterヘルパー |
  | `plugin-sdk/agent-media-payload` | レガシーmedia payloadヘルパー | レガシーフィールドレイアウト向けagent media payload builder |
  | `plugin-sdk/channel-runtime` | 非推奨の互換シム | レガシーchannel runtimeユーティリティのみ |
  | `plugin-sdk/channel-send-result` | send result型 | reply result型 |
  | `plugin-sdk/runtime-store` | 永続pluginストレージ | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | 広範なruntimeヘルパー | runtime/logging/backup/plugin-installヘルパー |
  | `plugin-sdk/runtime-env` | 狭い範囲のruntime envヘルパー | Logger/runtime env、timeout、retry、backoffヘルパー |
  | `plugin-sdk/plugin-runtime` | 共通plugin runtimeヘルパー | plugin commands/hooks/http/interactiveヘルパー |
  | `plugin-sdk/hook-runtime` | フックパイプラインヘルパー | 共通のwebhook/internal hook pipelineヘルパー |
  | `plugin-sdk/lazy-runtime` | lazy runtimeヘルパー | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | プロセスヘルパー | 共通のexecヘルパー |
  | `plugin-sdk/cli-runtime` | CLI runtimeヘルパー | コマンド整形、待機、バージョンヘルパー |
  | `plugin-sdk/gateway-runtime` | Gatewayヘルパー | Gatewayクライアントとchannel-status patchヘルパー |
  | `plugin-sdk/config-runtime` | 設定ヘルパー | 設定の読み込み/書き込みヘルパー |
  | `plugin-sdk/telegram-command-config` | Telegramコマンドヘルパー | バンドル済みTelegram contract surfaceが利用できない場合の、フォールバックで安定したTelegramコマンド検証ヘルパー |
  | `plugin-sdk/approval-runtime` | 承認プロンプトヘルパー | exec/plugin承認payload、承認capability/profileヘルパー、ネイティブ承認ルーティング/runtimeヘルパー |
  | `plugin-sdk/approval-auth-runtime` | 承認authヘルパー | approver解決、同一チャットアクション認証 |
  | `plugin-sdk/approval-client-runtime` | 承認クライアントヘルパー | ネイティブexec承認profile/filterヘルパー |
  | `plugin-sdk/approval-delivery-runtime` | 承認配信ヘルパー | ネイティブ承認capability/delivery adapter |
  | `plugin-sdk/approval-native-runtime` | 承認ターゲットヘルパー | ネイティブ承認target/account bindingヘルパー |
  | `plugin-sdk/approval-reply-runtime` | 承認返信ヘルパー | exec/plugin承認reply payloadヘルパー |
  | `plugin-sdk/security-runtime` | セキュリティヘルパー | 共通のtrust、DM gating、external-content、secret collectionヘルパー |
  | `plugin-sdk/ssrf-policy` | SSRFポリシーヘルパー | ホストallowlistとprivate-networkポリシーヘルパー |
  | `plugin-sdk/ssrf-runtime` | SSRF runtimeヘルパー | pinned-dispatcher、guarded fetch、SSRFポリシーヘルパー |
  | `plugin-sdk/collection-runtime` | 制限付きキャッシュヘルパー | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | 診断ゲーティングヘルパー | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | エラー整形ヘルパー | `formatUncaughtError`, `isApprovalNotFoundError`, error graphヘルパー |
  | `plugin-sdk/fetch-runtime` | ラップされたfetch/proxyヘルパー | `resolveFetch`, proxyヘルパー |
  | `plugin-sdk/host-runtime` | ホスト正規化ヘルパー | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | retryヘルパー | `RetryConfig`, `retryAsync`, policy runner |
  | `plugin-sdk/allow-from` | allowlist整形 | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | allowlist入力マッピング | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | コマンドゲーティングとコマンドサーフェスヘルパー | `resolveControlCommandGate`, sender authorizationヘルパー、command registryヘルパー |
  | `plugin-sdk/secret-input` | シークレット入力解析 | シークレット入力ヘルパー |
  | `plugin-sdk/webhook-ingress` | webhookリクエストヘルパー | webhook targetユーティリティ |
  | `plugin-sdk/webhook-request-guards` | webhook body guardヘルパー | リクエストボディの読み取り/制限ヘルパー |
  | `plugin-sdk/reply-runtime` | 共通reply runtime | inbound dispatch、heartbeat、reply planner、chunking |
  | `plugin-sdk/reply-dispatch-runtime` | 狭い範囲のreply dispatchヘルパー | finalize + provider dispatchヘルパー |
  | `plugin-sdk/reply-history` | reply-historyヘルパー | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | reply reference計画 | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | reply chunkヘルパー | テキスト/markdown chunkingヘルパー |
  | `plugin-sdk/session-store-runtime` | セッションストアヘルパー | store path + updated-atヘルパー |
  | `plugin-sdk/state-paths` | state pathヘルパー | stateおよびOAuth dirヘルパー |
  | `plugin-sdk/routing` | ルーティング/セッションキー ヘルパー | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, session-key正規化ヘルパー |
  | `plugin-sdk/status-helpers` | channel statusヘルパー | channel/account statusサマリービルダー、runtime-stateデフォルト、issue metadataヘルパー |
  | `plugin-sdk/target-resolver-runtime` | target resolverヘルパー | 共通のtarget resolverヘルパー |
  | `plugin-sdk/string-normalization-runtime` | 文字列正規化ヘルパー | slug/文字列正規化ヘルパー |
  | `plugin-sdk/request-url` | リクエストURLヘルパー | request風入力から文字列URLを抽出 |
  | `plugin-sdk/run-command` | 時間制限付きコマンドヘルパー | 正規化されたstdout/stderrを持つ時間制限付きコマンドrunner |
  | `plugin-sdk/param-readers` | パラメータリーダー | 共通のtool/CLIパラメータリーダー |
  | `plugin-sdk/tool-send` | tool送信抽出 | tool引数から正規の送信先フィールドを抽出 |
  | `plugin-sdk/temp-path` | 一時パスヘルパー | 共通の一時ダウンロードパスヘルパー |
  | `plugin-sdk/logging-core` | loggingヘルパー | subsystem loggerとredactionヘルパー |
  | `plugin-sdk/markdown-table-runtime` | markdown-tableヘルパー | markdown tableモードヘルパー |
  | `plugin-sdk/reply-payload` | メッセージ返信型 | reply payload型 |
  | `plugin-sdk/provider-setup` | 厳選されたlocal/self-hosted providerセットアップヘルパー | self-hosted provider discovery/configヘルパー |
  | `plugin-sdk/self-hosted-provider-setup` | 用途を絞ったOpenAI互換self-hosted providerセットアップヘルパー | 同じself-hosted provider discovery/configヘルパー |
  | `plugin-sdk/provider-auth-runtime` | provider runtime authヘルパー | runtime API-key解決ヘルパー |
  | `plugin-sdk/provider-auth-api-key` | provider API-keyセットアップヘルパー | API-keyオンボーディング/profile-writeヘルパー |
  | `plugin-sdk/provider-auth-result` | provider auth-resultヘルパー | 標準OAuth auth-result builder |
  | `plugin-sdk/provider-auth-login` | provider対話型ログインヘルパー | 共通の対話型ログインヘルパー |
  | `plugin-sdk/provider-env-vars` | provider env-varヘルパー | provider auth env-var lookupヘルパー |
  | `plugin-sdk/provider-model-shared` | 共通provider model/replayヘルパー | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, 共通replay-policy builder、provider-endpointヘルパー、model-id正規化ヘルパー |
  | `plugin-sdk/provider-catalog-shared` | 共通provider catalogヘルパー | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | providerオンボーディングパッチ | オンボーディング設定ヘルパー |
  | `plugin-sdk/provider-http` | provider HTTPヘルパー | 汎用provider HTTP/endpoint capabilityヘルパー |
  | `plugin-sdk/provider-web-fetch` | provider web-fetchヘルパー | web-fetch provider登録/キャッシュヘルパー |
  | `plugin-sdk/provider-web-search-contract` | provider web-search契約ヘルパー | `enablePluginInConfig`、`resolveProviderWebSearchPluginConfig`、スコープ付きcredential setter/getterなどの、狭い範囲のweb-search config/credential contractヘルパー |
  | `plugin-sdk/provider-web-search` | provider web-searchヘルパー | web-search provider登録/キャッシュ/runtimeヘルパー |
  | `plugin-sdk/provider-tools` | provider tool/schema互換ヘルパー | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini schemaクリーンアップ + diagnostics、および`resolveXaiModelCompatPatch` / `applyXaiModelCompat`のようなxAI互換ヘルパー |
  | `plugin-sdk/provider-usage` | provider使用量ヘルパー | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage`、その他のprovider使用量ヘルパー |
  | `plugin-sdk/provider-stream` | provider streamラッパーヘルパー | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, stream wrapper型、および共通のAnthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilotラッパーヘルパー |
  | `plugin-sdk/keyed-async-queue` | 順序付きasyncキュー | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | 共通mediaヘルパー | media fetch/transform/storeヘルパーとmedia payload builder |
  | `plugin-sdk/media-generation-runtime` | 共通media-generationヘルパー | image/video/music generation向けの共通フェイルオーバーヘルパー、候補選択、missing-modelメッセージング |
  | `plugin-sdk/media-understanding` | media-understandingヘルパー | media understanding provider型とprovider向けimage/audioヘルパーエクスポート |
  | `plugin-sdk/text-runtime` | 共通textヘルパー | assistant-visible-text除去、markdown render/chunking/tableヘルパー、redactionヘルパー、directive-tagヘルパー、安全なtextユーティリティ、関連するtext/loggingヘルパー |
  | `plugin-sdk/text-chunking` | text chunkingヘルパー | outbound text chunkingヘルパー |
  | `plugin-sdk/speech` | speechヘルパー | speech provider型とprovider向けdirective、registry、validationヘルパー |
  | `plugin-sdk/speech-core` | 共通speech core | speech provider型、registry、directive、正規化 |
  | `plugin-sdk/realtime-transcription` | realtime transcriptionヘルパー | provider型とregistryヘルパー |
  | `plugin-sdk/realtime-voice` | realtime voiceヘルパー | provider型とregistryヘルパー |
  | `plugin-sdk/image-generation-core` | 共通image-generation core | image-generation型、フェイルオーバー、auth、registryヘルパー |
  | `plugin-sdk/music-generation` | music-generationヘルパー | music-generation provider/request/result型 |
  | `plugin-sdk/music-generation-core` | 共通music-generation core | music-generation型、フェイルオーバーヘルパー、provider lookup、model-ref解析 |
  | `plugin-sdk/video-generation` | video-generationヘルパー | video-generation provider/request/result型 |
  | `plugin-sdk/video-generation-core` | 共通video-generation core | video-generation型、フェイルオーバーヘルパー、provider lookup、model-ref解析 |
  | `plugin-sdk/interactive-runtime` | interactive replyヘルパー | interactive reply payload正規化/削減 |
  | `plugin-sdk/channel-config-primitives` | channel configの基本要素 | 狭い範囲のchannel config-schema基本要素 |
  | `plugin-sdk/channel-config-writes` | channel config書き込みヘルパー | channel config書き込み認可ヘルパー |
  | `plugin-sdk/channel-plugin-common` | 共通channel prelude | 共通channel plugin preludeエクスポート |
  | `plugin-sdk/channel-status` | channel statusヘルパー | 共通channel statusスナップショット/サマリーヘルパー |
  | `plugin-sdk/allowlist-config-edit` | allowlist設定ヘルパー | allowlist設定の編集/読み取りヘルパー |
  | `plugin-sdk/group-access` | グループアクセスヘルパー | 共通group-access判定ヘルパー |
  | `plugin-sdk/direct-dm` | direct-DMヘルパー | 共通direct-DM auth/guardヘルパー |
  | `plugin-sdk/extension-shared` | 共通extensionヘルパー | passive-channel/statusとambient proxyヘルパーの基本要素 |
  | `plugin-sdk/webhook-targets` | webhook targetヘルパー | webhook target registryとroute-installヘルパー |
  | `plugin-sdk/webhook-path` | webhook pathヘルパー | webhook path正規化ヘルパー |
  | `plugin-sdk/web-media` | 共通web mediaヘルパー | remote/local media読み込みヘルパー |
  | `plugin-sdk/zod` | Zod再エクスポート | plugin SDKコンシューマー向けに再エクスポートされた`zod` |
  | `plugin-sdk/memory-core` | バンドル済みmemory-coreヘルパー | Memory manager/config/file/CLIヘルパーサーフェス |
  | `plugin-sdk/memory-core-engine-runtime` | Memory engine runtimeファサード | Memory index/search runtimeファサード |
  | `plugin-sdk/memory-core-host-engine-foundation` | Memory host foundation engine | Memory host foundation engineエクスポート |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Memory host embedding engine | Memory host embedding engineエクスポート |
  | `plugin-sdk/memory-core-host-engine-qmd` | Memory host QMD engine | Memory host QMD engineエクスポート |
  | `plugin-sdk/memory-core-host-engine-storage` | Memory host storage engine | Memory host storage engineエクスポート |
  | `plugin-sdk/memory-core-host-multimodal` | Memory host multimodalヘルパー | Memory host multimodalヘルパー |
  | `plugin-sdk/memory-core-host-query` | Memory host queryヘルパー | Memory host queryヘルパー |
  | `plugin-sdk/memory-core-host-secret` | Memory host secretヘルパー | Memory host secretヘルパー |
  | `plugin-sdk/memory-core-host-events` | Memory host event journalヘルパー | Memory host event journalヘルパー |
  | `plugin-sdk/memory-core-host-status` | Memory host statusヘルパー | Memory host statusヘルパー |
  | `plugin-sdk/memory-core-host-runtime-cli` | Memory host CLI runtime | Memory host CLI runtimeヘルパー |
  | `plugin-sdk/memory-core-host-runtime-core` | Memory host core runtime | Memory host core runtimeヘルパー |
  | `plugin-sdk/memory-core-host-runtime-files` | Memory host file/runtimeヘルパー | Memory host file/runtimeヘルパー |
  | `plugin-sdk/memory-host-core` | Memory host core runtimeエイリアス | Memory host core runtimeヘルパー向けのvendor-neutralエイリアス |
  | `plugin-sdk/memory-host-events` | Memory host event journalエイリアス | Memory host event journalヘルパー向けのvendor-neutralエイリアス |
  | `plugin-sdk/memory-host-files` | Memory host file/runtimeエイリアス | Memory host file/runtimeヘルパー向けのvendor-neutralエイリアス |
  | `plugin-sdk/memory-host-markdown` | 管理対象markdownヘルパー | memory隣接plugin向けの共通managed-markdownヘルパー |
  | `plugin-sdk/memory-host-search` | アクティブmemory searchファサード | lazy active-memory search-manager runtimeファサード |
  | `plugin-sdk/memory-host-status` | Memory host statusエイリアス | Memory host statusヘルパー向けのvendor-neutralエイリアス |
  | `plugin-sdk/memory-lancedb` | バンドル済みmemory-lancedbヘルパー | Memory-lancedbヘルパーサーフェス |
  | `plugin-sdk/testing` | テストユーティリティ | テストヘルパーとモック |
</Accordion>

このテーブルは、意図的に一般的な移行対象のサブセットであり、SDK
サーフェス全体ではありません。200以上のエントリーポイントからなる完全な一覧は、
`scripts/lib/plugin-sdk-entrypoints.json`にあります。

その一覧には、依然として
`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、`plugin-sdk/zalo`、
`plugin-sdk/zalo-setup`、`plugin-sdk/matrix*`のような
一部のバンドル済みpluginヘルパーシームが含まれています。これらはバンドル済みpluginの保守と互換性のために引き続きエクスポートされていますが、
一般的な移行テーブルからは意図的に除外されており、新しい
pluginコードの推奨ターゲットではありません。

同じルールは、他のバンドル済みヘルパーファミリーにも適用されます。たとえば:

- browserサポートヘルパー: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- `plugin-sdk/googlechat`のようなバンドル済みヘルパー/pluginサーフェス、
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership`, および `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token`は現在、狭い範囲のtoken-helper
サーフェス`DEFAULT_COPILOT_API_BASE_URL`、
`deriveCopilotApiBaseUrlFromToken`、`resolveCopilotApiToken`を公開しています。

作業に一致する最も狭いインポートを使ってください。エクスポートが見つからない場合は、
`src/plugin-sdk/`のソースを確認するか、Discordで質問してください。

## 削除タイムライン

| When | What happens |
| ---------------------- | ----------------------------------------------------------------------- |
| **現在**                | 非推奨サーフェスはランタイム警告を出す |
| **次のメジャーリリース** | 非推奨サーフェスは削除され、それらを使い続けるpluginは失敗する |

すべてのコアpluginはすでに移行済みです。外部pluginは、次のメジャーリリース前に移行すべきです。

## 一時的に警告を抑制する

移行作業中は、これらの環境変数を設定してください。

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

これは一時的な回避手段であり、恒久的な解決策ではありません。

## 関連

- [はじめに](/ja-JP/plugins/building-plugins) — 最初のpluginを作成する
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全なサブパスインポートリファレンス
- [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — channel pluginの作成
- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — provider pluginの作成
- [Plugin Internals](/ja-JP/plugins/architecture) — アーキテクチャの詳細
- [Plugin Manifest](/ja-JP/plugins/manifest) — manifestスキーマリファレンス
