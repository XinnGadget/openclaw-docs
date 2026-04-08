---
read_when:
    - どの SDK サブパスからインポートすべきか知る必要がある場合
    - OpenClawPluginApi のすべての登録メソッドのリファレンスが必要な場合
    - 特定の SDK エクスポートを調べる場合
sidebarTitle: SDK Overview
summary: インポートマップ、登録 API リファレンス、SDK アーキテクチャ
title: Plugin SDK 概要
x-i18n:
    generated_at: "2026-04-08T02:18:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: c5a41bd82d165dfbb7fbd6e4528cf322e9133a51efe55fa8518a7a0a626d9d30
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDK 概要

Plugin SDK は、プラグインとコアの間にある型付きコントラクトです。このページは、
**何をインポートするか** と **何を登録できるか** のリファレンスです。

<Tip>
  **ハウツーガイドを探していますか？**
  - 最初のプラグインなら: [はじめに](/ja-JP/plugins/building-plugins)
  - チャネルプラグインなら: [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins)
  - プロバイダープラグインなら: [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins)
</Tip>

## インポート規約

必ず特定のサブパスからインポートしてください。

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

各サブパスは小さく自己完結したモジュールです。これにより起動が高速に保たれ、
循環依存の問題を防げます。チャネル固有のエントリ / ビルドヘルパーでは、
`openclaw/plugin-sdk/channel-core` を優先してください。`openclaw/plugin-sdk/core` は、
より広い包括的サーフェスと、`buildChannelConfigSchema` のような共有ヘルパー向けに使ってください。

`openclaw/plugin-sdk/slack`、`openclaw/plugin-sdk/discord`、
`openclaw/plugin-sdk/signal`、`openclaw/plugin-sdk/whatsapp` のような、
プロバイダー名付きの便利用シームや、チャネルブランド付きヘルパーシームを追加したり、
依存したりしないでください。バンドル済みプラグインは、自分自身の `api.ts` または `runtime-api.ts`
バレル内で汎用的な SDK サブパスを組み合わせるべきであり、コアはそれらのプラグインローカルバレルを使うか、
本当にクロスチャネルな必要があるときだけ狭い汎用 SDK コントラクトを追加すべきです。

生成されたエクスポートマップには、`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、
`plugin-sdk/zalo`、`plugin-sdk/zalo-setup`、`plugin-sdk/matrix*` などの
少数のバンドル済みプラグイン向けヘルパーシームもまだ含まれています。これらの
サブパスは、バンドル済みプラグインの保守と互換性のためだけに存在しており、
下の共通テーブルからは意図的に省かれています。新しいサードパーティプラグインに
推奨されるインポートパスではありません。

## サブパスリファレンス

用途ごとにまとめた、最もよく使われるサブパスです。生成済みの完全な 200 以上の
サブパス一覧は `scripts/lib/plugin-sdk-entrypoints.json` にあります。

予約済みのバンドル済みプラグイン向けヘルパーサブパスも、この生成済み一覧には引き続き表示されます。
ドキュメントページで明示的に公開扱いされていない限り、これらは実装詳細 / 互換性用サーフェスとして扱ってください。

### プラグインエントリ

| サブパス | 主なエクスポート |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="チャネルのサブパス">
    | サブパス | 主なエクスポート |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | ルート `openclaw.json` の Zod スキーマエクスポート（`OpenClawSchema`） |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, および `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | 共有セットアップウィザードヘルパー、allowlist プロンプト、セットアップステータスビルダー |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | マルチアカウントの設定 / アクションゲートヘルパー、デフォルトアカウントのフォールバックヘルパー |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`、account-id 正規化ヘルパー |
    | `plugin-sdk/account-resolution` | アカウント検索 + デフォルトフォールバックヘルパー |
    | `plugin-sdk/account-helpers` | 狭い範囲のアカウント一覧 / アカウントアクションヘルパー |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | チャネル設定スキーマ型 |
    | `plugin-sdk/telegram-command-config` | バンドル済みコントラクトのフォールバック付き Telegram カスタムコマンド正規化 / バリデーションヘルパー |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | 共有インバウンドルート + エンベロープビルダーヘルパー |
    | `plugin-sdk/inbound-reply-dispatch` | 共有インバウンド記録 / ディスパッチヘルパー |
    | `plugin-sdk/messaging-targets` | ターゲット解析 / マッチングヘルパー |
    | `plugin-sdk/outbound-media` | 共有アウトバウンドメディア読み込みヘルパー |
    | `plugin-sdk/outbound-runtime` | アウトバウンド ID / 送信デリゲートヘルパー |
    | `plugin-sdk/thread-bindings-runtime` | スレッドバインディングのライフサイクルとアダプターヘルパー |
    | `plugin-sdk/agent-media-payload` | 旧来のエージェントメディアペイロードビルダー |
    | `plugin-sdk/conversation-runtime` | 会話 / スレッドバインディング、pairing、設定済みバインディングヘルパー |
    | `plugin-sdk/runtime-config-snapshot` | ランタイム設定スナップショットヘルパー |
    | `plugin-sdk/runtime-group-policy` | ランタイム group-policy 解決ヘルパー |
    | `plugin-sdk/channel-status` | 共有チャネルステータスのスナップショット / サマリーヘルパー |
    | `plugin-sdk/channel-config-primitives` | 狭い範囲のチャネル config-schema プリミティブ |
    | `plugin-sdk/channel-config-writes` | チャネル config-write 認可ヘルパー |
    | `plugin-sdk/channel-plugin-common` | 共有チャネルプラグイン prelude エクスポート |
    | `plugin-sdk/allowlist-config-edit` | allowlist 設定の編集 / 読み取りヘルパー |
    | `plugin-sdk/group-access` | 共有 group-access 判定ヘルパー |
    | `plugin-sdk/direct-dm` | 共有 direct-DM 認証 / ガードヘルパー |
    | `plugin-sdk/interactive-runtime` | インタラクティブ返信ペイロードの正規化 / 簡約ヘルパー |
    | `plugin-sdk/channel-inbound` | インバウンド debounce、mention マッチング、mention-policy ヘルパー、およびエンベロープヘルパー |
    | `plugin-sdk/channel-send-result` | 返信結果型 |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | ターゲット解析 / マッチングヘルパー |
    | `plugin-sdk/channel-contract` | チャネルコントラクト型 |
    | `plugin-sdk/channel-feedback` | フィードバック / リアクション配線 |
    | `plugin-sdk/channel-secret-runtime` | `collectSimpleChannelFieldAssignments`、`getChannelSurface`、`pushAssignment`、secret target 型などの狭い secret-contract ヘルパー |
  </Accordion>

  <Accordion title="プロバイダーのサブパス">
    | サブパス | 主なエクスポート |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | ローカル / セルフホスト型プロバイダー向けの厳選されたセットアップヘルパー |
    | `plugin-sdk/self-hosted-provider-setup` | OpenAI 互換セルフホスト型プロバイダー向けの特化セットアップヘルパー |
    | `plugin-sdk/cli-backend` | CLI バックエンドのデフォルト + watchdog 定数 |
    | `plugin-sdk/provider-auth-runtime` | プロバイダープラグイン向けランタイム API キー解決ヘルパー |
    | `plugin-sdk/provider-auth-api-key` | `upsertApiKeyProfile` などの API キーオンボーディング / プロファイル書き込みヘルパー |
    | `plugin-sdk/provider-auth-result` | 標準 OAuth auth-result ビルダー |
    | `plugin-sdk/provider-auth-login` | プロバイダープラグイン向け共有インタラクティブログインヘルパー |
    | `plugin-sdk/provider-env-vars` | プロバイダー認証用 env var 参照ヘルパー |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`、共有 replay-policy ビルダー、provider-endpoint ヘルパー、および `normalizeNativeXaiModelId` などの model-id 正規化ヘルパー |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | 汎用プロバイダー HTTP / endpoint capability ヘルパー |
    | `plugin-sdk/provider-web-fetch-contract` | `enablePluginInConfig` や `WebFetchProviderPlugin` などの狭い web-fetch 設定 / 選択コントラクトヘルパー |
    | `plugin-sdk/provider-web-fetch` | web-fetch プロバイダーの登録 / キャッシュヘルパー |
    | `plugin-sdk/provider-web-search-contract` | `enablePluginInConfig`、`resolveProviderWebSearchPluginConfig`、スコープ付き資格情報 setter/getter などの狭い web-search 設定 / credential コントラクトヘルパー |
    | `plugin-sdk/provider-web-search` | web-search プロバイダーの登録 / キャッシュ / ランタイムヘルパー |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini スキーマクリーンアップ + diagnostics、および `resolveXaiModelCompatPatch` / `applyXaiModelCompat` などの xAI 互換ヘルパー |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` など |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`、ストリームラッパー型、および共有 Anthropic / Bedrock / Google / Kilocode / Moonshot / OpenAI / OpenRouter / Z.A.I / MiniMax / Copilot ラッパーヘルパー |
    | `plugin-sdk/provider-onboard` | オンボーディング設定パッチヘルパー |
    | `plugin-sdk/global-singleton` | プロセスローカル singleton / map / cache ヘルパー |
  </Accordion>

  <Accordion title="認証とセキュリティのサブパス">
    | サブパス | 主なエクスポート |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`、コマンドレジストリヘルパー、送信者認可ヘルパー |
    | `plugin-sdk/approval-auth-runtime` | approver 解決と same-chat action-auth ヘルパー |
    | `plugin-sdk/approval-client-runtime` | ネイティブ exec 承認のプロファイル / フィルターヘルパー |
    | `plugin-sdk/approval-delivery-runtime` | ネイティブ承認の capability / delivery アダプター |
    | `plugin-sdk/approval-gateway-runtime` | 共有承認 gateway 解決ヘルパー |
    | `plugin-sdk/approval-handler-adapter-runtime` | hot なチャネルエントリポイント向けの軽量ネイティブ承認アダプターロードヘルパー |
    | `plugin-sdk/approval-handler-runtime` | より広い承認ハンドラーランタイムヘルパー。狭い adapter / gateway シームで足りる場合はそちらを優先してください |
    | `plugin-sdk/approval-native-runtime` | ネイティブ承認ターゲット + account-binding ヘルパー |
    | `plugin-sdk/approval-reply-runtime` | exec / plugin 承認返信ペイロードヘルパー |
    | `plugin-sdk/command-auth-native` | ネイティブコマンド認証 + ネイティブ session-target ヘルパー |
    | `plugin-sdk/command-detection` | 共有コマンド検出ヘルパー |
    | `plugin-sdk/command-surface` | コマンド本文の正規化と command-surface ヘルパー |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | チャネル / プラグインの secret サーフェス向けの狭い secret-contract 収集ヘルパー |
    | `plugin-sdk/secret-ref-runtime` | secret-contract / config 解析向けの狭い `coerceSecretRef` と SecretRef 型ヘルパー |
    | `plugin-sdk/security-runtime` | 共有の trust、DM gating、external-content、secret-collection ヘルパー |
    | `plugin-sdk/ssrf-policy` | ホスト allowlist と private-network SSRF policy ヘルパー |
    | `plugin-sdk/ssrf-runtime` | pinned-dispatcher、SSRF ガード付き fetch、SSRF policy ヘルパー |
    | `plugin-sdk/secret-input` | secret input 解析ヘルパー |
    | `plugin-sdk/webhook-ingress` | webhook リクエスト / ターゲットヘルパー |
    | `plugin-sdk/webhook-request-guards` | リクエスト本文サイズ / timeout ヘルパー |
  </Accordion>

  <Accordion title="ランタイムとストレージのサブパス">
    | サブパス | 主なエクスポート |
    | --- | --- |
    | `plugin-sdk/runtime` | 広範なランタイム / logging / backup / plugin-install ヘルパー |
    | `plugin-sdk/runtime-env` | 狭いランタイム env、logger、timeout、retry、backoff ヘルパー |
    | `plugin-sdk/channel-runtime-context` | 汎用チャネル runtime-context の登録 / 検索ヘルパー |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | 共有プラグイン command / hook / http / interactive ヘルパー |
    | `plugin-sdk/hook-runtime` | 共有 webhook / internal hook パイプラインヘルパー |
    | `plugin-sdk/lazy-runtime` | `createLazyRuntimeModule`、`createLazyRuntimeMethod`、`createLazyRuntimeSurface` などの lazy runtime import / binding ヘルパー |
    | `plugin-sdk/process-runtime` | プロセス exec ヘルパー |
    | `plugin-sdk/cli-runtime` | CLI の整形、wait、version ヘルパー |
    | `plugin-sdk/gateway-runtime` | Gateway クライアントと channel-status パッチヘルパー |
    | `plugin-sdk/config-runtime` | 設定の読み込み / 書き込みヘルパー |
    | `plugin-sdk/telegram-command-config` | バンドル済み Telegram コントラクトサーフェスが使えない場合でも機能する、Telegram コマンド名 / 説明の正規化と重複 / 競合チェック |
    | `plugin-sdk/approval-runtime` | exec / plugin 承認ヘルパー、承認 capability ビルダー、auth / profile ヘルパー、ネイティブルーティング / ランタイムヘルパー |
    | `plugin-sdk/reply-runtime` | 共有インバウンド / reply ランタイムヘルパー、chunking、dispatch、heartbeat、reply planner |
    | `plugin-sdk/reply-dispatch-runtime` | 狭い reply dispatch / finalize ヘルパー |
    | `plugin-sdk/reply-history` | `buildHistoryContext`、`recordPendingHistoryEntry`、`clearHistoryEntriesIfEnabled` などの共有 short-window reply-history ヘルパー |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | 狭い text / markdown chunking ヘルパー |
    | `plugin-sdk/session-store-runtime` | セッションストアの path + updated-at ヘルパー |
    | `plugin-sdk/state-paths` | state / OAuth ディレクトリパスヘルパー |
    | `plugin-sdk/routing` | `resolveAgentRoute`、`buildAgentSessionKey`、`resolveDefaultAgentBoundAccountId` などの route / session-key / account binding ヘルパー |
    | `plugin-sdk/status-helpers` | 共有チャネル / アカウントステータスサマリーヘルパー、ランタイム状態デフォルト、issue metadata ヘルパー |
    | `plugin-sdk/target-resolver-runtime` | 共有 target resolver ヘルパー |
    | `plugin-sdk/string-normalization-runtime` | slug / string 正規化ヘルパー |
    | `plugin-sdk/request-url` | fetch / request 風入力から文字列 URL を抽出 |
    | `plugin-sdk/run-command` | 正規化された stdout / stderr 結果を返す timed command runner |
    | `plugin-sdk/param-readers` | 共通 tool / CLI param reader |
    | `plugin-sdk/tool-send` | tool 引数から canonical な送信ターゲットフィールドを抽出 |
    | `plugin-sdk/temp-path` | 共有一時ダウンロードパスヘルパー |
    | `plugin-sdk/logging-core` | subsystem logger と redaction ヘルパー |
    | `plugin-sdk/markdown-table-runtime` | Markdown table モードヘルパー |
    | `plugin-sdk/json-store` | 小規模 JSON state 読み書きヘルパー |
    | `plugin-sdk/file-lock` | 再入可能な file-lock ヘルパー |
    | `plugin-sdk/persistent-dedupe` | ディスクバックな dedupe cache ヘルパー |
    | `plugin-sdk/acp-runtime` | ACP ランタイム / セッションと reply-dispatch ヘルパー |
    | `plugin-sdk/agent-config-primitives` | 狭い agent runtime config-schema プリミティブ |
    | `plugin-sdk/boolean-param` | 緩い boolean param reader |
    | `plugin-sdk/dangerous-name-runtime` | dangerous-name マッチング解決ヘルパー |
    | `plugin-sdk/device-bootstrap` | device bootstrap と pairing token ヘルパー |
    | `plugin-sdk/extension-shared` | 共有 passive-channel、status、および ambient proxy ヘルパープリミティブ |
    | `plugin-sdk/models-provider-runtime` | `/models` コマンド / provider reply ヘルパー |
    | `plugin-sdk/skill-commands-runtime` | Skills コマンド一覧ヘルパー |
    | `plugin-sdk/native-command-registry` | ネイティブコマンド registry / build / serialize ヘルパー |
    | `plugin-sdk/provider-zai-endpoint` | Z.A.I endpoint 検出ヘルパー |
    | `plugin-sdk/infra-runtime` | システムイベント / heartbeat ヘルパー |
    | `plugin-sdk/collection-runtime` | 小規模 bounded cache ヘルパー |
    | `plugin-sdk/diagnostic-runtime` | diagnostic flag と event ヘルパー |
    | `plugin-sdk/error-runtime` | エラーグラフ、整形、共有エラー分類ヘルパー、`isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | ラップされた fetch、proxy、pinned lookup ヘルパー |
    | `plugin-sdk/host-runtime` | ホスト名と SCP ホスト正規化ヘルパー |
    | `plugin-sdk/retry-runtime` | retry 設定と retry runner ヘルパー |
    | `plugin-sdk/agent-runtime` | agent ディレクトリ / ID / workspace ヘルパー |
    | `plugin-sdk/directory-runtime` | config ベースのディレクトリ問い合わせ / dedup |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="capability とテストのサブパス">
    | サブパス | 主なエクスポート |
    | --- | --- |
    | `plugin-sdk/media-runtime` | 共有メディア fetch / transform / store ヘルパーに加え、メディアペイロードビルダー |
    | `plugin-sdk/media-generation-runtime` | 共有メディア生成 failover ヘルパー、候補選択、missing-model メッセージング |
    | `plugin-sdk/media-understanding` | メディア理解プロバイダー型に加え、プロバイダー向け image / audio ヘルパーエクスポート |
    | `plugin-sdk/text-runtime` | assistant-visible-text の除去、markdown render / chunking / table ヘルパー、redaction ヘルパー、directive-tag ヘルパー、安全な text ユーティリティなどの共有 text / markdown / logging ヘルパー |
    | `plugin-sdk/text-chunking` | アウトバウンド text chunking ヘルパー |
    | `plugin-sdk/speech` | 音声プロバイダー型に加え、プロバイダー向け directive、registry、validation ヘルパー |
    | `plugin-sdk/speech-core` | 共有音声プロバイダー型、registry、directive、normalization ヘルパー |
    | `plugin-sdk/realtime-transcription` | realtime transcription プロバイダー型と registry ヘルパー |
    | `plugin-sdk/realtime-voice` | realtime voice プロバイダー型と registry ヘルパー |
    | `plugin-sdk/image-generation` | 画像生成プロバイダー型 |
    | `plugin-sdk/image-generation-core` | 共有画像生成型、failover、auth、registry ヘルパー |
    | `plugin-sdk/music-generation` | 音楽生成プロバイダー / リクエスト / 結果型 |
    | `plugin-sdk/music-generation-core` | 共有音楽生成型、failover ヘルパー、プロバイダー検索、model-ref 解析 |
    | `plugin-sdk/video-generation` | 動画生成プロバイダー / リクエスト / 結果型 |
    | `plugin-sdk/video-generation-core` | 共有動画生成型、failover ヘルパー、プロバイダー検索、model-ref 解析 |
    | `plugin-sdk/webhook-targets` | webhook ターゲット registry と route-install ヘルパー |
    | `plugin-sdk/webhook-path` | webhook path 正規化ヘルパー |
    | `plugin-sdk/web-media` | 共有リモート / ローカルメディア読み込みヘルパー |
    | `plugin-sdk/zod` | Plugin SDK 利用者向けに再エクスポートされた `zod` |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="メモリのサブパス">
    | サブパス | 主なエクスポート |
    | --- | --- |
    | `plugin-sdk/memory-core` | manager / config / file / CLI ヘルパー向けのバンドル済み memory-core ヘルパーサーフェス |
    | `plugin-sdk/memory-core-engine-runtime` | メモリ index / search ランタイムファサード |
    | `plugin-sdk/memory-core-host-engine-foundation` | メモリ host foundation engine エクスポート |
    | `plugin-sdk/memory-core-host-engine-embeddings` | メモリ host embedding engine エクスポート |
    | `plugin-sdk/memory-core-host-engine-qmd` | メモリ host QMD engine エクスポート |
    | `plugin-sdk/memory-core-host-engine-storage` | メモリ host storage engine エクスポート |
    | `plugin-sdk/memory-core-host-multimodal` | メモリ host multimodal ヘルパー |
    | `plugin-sdk/memory-core-host-query` | メモリ host query ヘルパー |
    | `plugin-sdk/memory-core-host-secret` | メモリ host secret ヘルパー |
    | `plugin-sdk/memory-core-host-events` | メモリ host event journal ヘルパー |
    | `plugin-sdk/memory-core-host-status` | メモリ host status ヘルパー |
    | `plugin-sdk/memory-core-host-runtime-cli` | メモリ host CLI ランタイムヘルパー |
    | `plugin-sdk/memory-core-host-runtime-core` | メモリ host core ランタイムヘルパー |
    | `plugin-sdk/memory-core-host-runtime-files` | メモリ host file / runtime ヘルパー |
    | `plugin-sdk/memory-host-core` | メモリ host core ランタイムヘルパーの vendor-neutral エイリアス |
    | `plugin-sdk/memory-host-events` | メモリ host event journal ヘルパーの vendor-neutral エイリアス |
    | `plugin-sdk/memory-host-files` | メモリ host file / runtime ヘルパーの vendor-neutral エイリアス |
    | `plugin-sdk/memory-host-markdown` | memory 周辺プラグイン向けの共有 managed-markdown ヘルパー |
    | `plugin-sdk/memory-host-search` | search-manager アクセス向けのアクティブメモリランタイムファサード |
    | `plugin-sdk/memory-host-status` | メモリ host status ヘルパーの vendor-neutral エイリアス |
    | `plugin-sdk/memory-lancedb` | バンドル済み memory-lancedb ヘルパーサーフェス |
  </Accordion>

  <Accordion title="予約済みバンドルヘルパーサブパス">
    | ファミリー | 現在のサブパス | 想定用途 |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | バンドル済み browser プラグイン向けサポートヘルパー（`browser-support` は互換性バレルとして残されています） |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | バンドル済み Matrix ヘルパー / ランタイムサーフェス |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | バンドル済み LINE ヘルパー / ランタイムサーフェス |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | バンドル済み IRC ヘルパーサーフェス |
    | チャネル固有ヘルパー | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | バンドル済みチャネル互換 / ヘルパーシーム |
    | 認証 / プラグイン固有ヘルパー | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | バンドル済み機能 / プラグインヘルパーシーム。`plugin-sdk/github-copilot-token` は現在 `DEFAULT_COPILOT_API_BASE_URL`、`deriveCopilotApiBaseUrlFromToken`、`resolveCopilotApiToken` をエクスポートします |
  </Accordion>
</AccordionGroup>

## 登録 API

`register(api)` コールバックは、次のメソッドを持つ `OpenClawPluginApi` オブジェクトを受け取ります。

### capability の登録

| メソッド | 登録されるもの |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | テキスト推論（LLM） |
| `api.registerCliBackend(...)`                    | ローカル CLI 推論バックエンド |
| `api.registerChannel(...)`                       | メッセージングチャネル |
| `api.registerSpeechProvider(...)`                | Text-to-speech / STT 合成 |
| `api.registerRealtimeTranscriptionProvider(...)` | ストリーミング realtime transcription |
| `api.registerRealtimeVoiceProvider(...)`         | duplex realtime voice セッション |
| `api.registerMediaUnderstandingProvider(...)`    | 画像 / 音声 / 動画解析 |
| `api.registerImageGenerationProvider(...)`       | 画像生成 |
| `api.registerMusicGenerationProvider(...)`       | 音楽生成 |
| `api.registerVideoGenerationProvider(...)`       | 動画生成 |
| `api.registerWebFetchProvider(...)`              | Web fetch / scrape プロバイダー |
| `api.registerWebSearchProvider(...)`             | Web search |

### ツールとコマンド

| メソッド | 登録されるもの |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | エージェントツール（必須、または `{ optional: true }`） |
| `api.registerCommand(def)`      | カスタムコマンド（LLM をバイパス） |

### インフラ

| メソッド | 登録されるもの |
| ---------------------------------------------- | --------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | イベントフック |
| `api.registerHttpRoute(params)`                | Gateway HTTP エンドポイント |
| `api.registerGatewayMethod(name, handler)`     | Gateway RPC メソッド |
| `api.registerCli(registrar, opts?)`            | CLI サブコマンド |
| `api.registerService(service)`                 | バックグラウンドサービス |
| `api.registerInteractiveHandler(registration)` | インタラクティブハンドラー |
| `api.registerMemoryPromptSupplement(builder)`  | 加算型の memory 隣接プロンプトセクション |
| `api.registerMemoryCorpusSupplement(adapter)`  | 加算型の memory search / read コーパス |

予約済みのコア管理名前空間（`config.*`、`exec.approvals.*`、`wizard.*`、
`update.*`）は、プラグインがより狭い Gateway メソッドスコープを割り当てようとしても、
常に `operator.admin` のままです。プラグイン所有のメソッドには、プラグイン固有のプレフィックスを優先してください。

### CLI 登録メタデータ

`api.registerCli(registrar, opts?)` は、2 種類のトップレベルメタデータを受け付けます。

- `commands`: registrar が所有する明示的なコマンドルート
- `descriptors`: ルート CLI ヘルプ、ルーティング、および lazy なプラグイン CLI 登録で使われる、parse 時のコマンド descriptor

プラグインコマンドを通常のルート CLI 経路で lazy-load のままにしたい場合は、
その registrar が公開するすべてのトップレベルコマンドルートをカバーする
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

通常のルート CLI で lazy 登録が不要な場合にのみ、`commands` 単独を使ってください。
その eager な互換パスは引き続きサポートされていますが、parse 時の lazy loading 用の
descriptor ベースのプレースホルダーはインストールされません。

### CLI バックエンド登録

`api.registerCliBackend(...)` を使うと、`codex-cli` のようなローカル
AI CLI バックエンドのデフォルト設定をプラグインが所有できます。

- バックエンドの `id` は、`codex-cli/gpt-5` のような model ref でのプロバイダープレフィックスになります。
- バックエンドの `config` は `agents.defaults.cliBackends.<id>` と同じ形を使います。
- ユーザー設定が優先されます。OpenClaw は CLI 実行前に、プラグインのデフォルトに対して `agents.defaults.cliBackends.<id>` をマージします。
- バックエンドで、マージ後に互換性のための書き換えが必要な場合は `normalizeConfig` を使ってください
  （たとえば古い flag 形式の正規化など）。

### 排他的スロット

| メソッド | 登録されるもの |
| ------------------------------------------ | ------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Context engine（一度に 1 つだけ有効） |
| `api.registerMemoryCapability(capability)` | 統合メモリ capability |
| `api.registerMemoryPromptSection(builder)` | メモリプロンプトセクションビルダー |
| `api.registerMemoryFlushPlan(resolver)`    | メモリ flush plan resolver |
| `api.registerMemoryRuntime(runtime)`       | メモリランタイムアダプター |

### メモリ埋め込みアダプター

| メソッド | 登録されるもの |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | アクティブなプラグイン向けのメモリ埋め込みアダプター |

- `registerMemoryCapability` が、推奨される排他的メモリプラグイン API です。
- `registerMemoryCapability` は `publicArtifacts.listArtifacts(...)` を公開することもでき、
  これによりコンパニオンプラグインは、特定のメモリプラグインのプライベートレイアウトに触れずに
  `openclaw/plugin-sdk/memory-host-core` を通してエクスポート済みメモリアーティファクトを利用できます。
- `registerMemoryPromptSection`、`registerMemoryFlushPlan`、および
  `registerMemoryRuntime` は、旧来互換の排他的メモリプラグイン API です。
- `registerMemoryEmbeddingProvider` により、アクティブなメモリプラグインは 1 つ以上の
  埋め込みアダプター ID（たとえば `openai`、`gemini`、またはプラグイン定義の独自 ID）を登録できます。
- `agents.defaults.memorySearch.provider` や
  `agents.defaults.memorySearch.fallback` のようなユーザー設定は、
  これらの登録済みアダプター ID に対して解決されます。

### イベントとライフサイクル

| メソッド | 役割 |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | 型付きライフサイクルフック |
| `api.onConversationBindingResolved(handler)` | 会話バインディングコールバック |

### フック決定セマンティクス

- `before_tool_call`: `{ block: true }` を返すと終端です。いずれかのハンドラーがこれを設定した時点で、より低優先度のハンドラーはスキップされます。
- `before_tool_call`: `{ block: false }` を返しても、上書きではなく決定なしとして扱われます（`block` を省略した場合と同じ）。
- `before_install`: `{ block: true }` を返すと終端です。いずれかのハンドラーがこれを設定した時点で、より低優先度のハンドラーはスキップされます。
- `before_install`: `{ block: false }` を返しても、上書きではなく決定なしとして扱われます（`block` を省略した場合と同じ）。
- `reply_dispatch`: `{ handled: true, ... }` を返すと終端です。いずれかのハンドラーがディスパッチを引き受けた時点で、より低優先度のハンドラーとデフォルトのモデルディスパッチ経路はスキップされます。
- `message_sending`: `{ cancel: true }` を返すと終端です。いずれかのハンドラーがこれを設定した時点で、より低優先度のハンドラーはスキップされます。
- `message_sending`: `{ cancel: false }` を返しても、上書きではなく決定なしとして扱われます（`cancel` を省略した場合と同じ）。

### API オブジェクトのフィールド

| フィールド | 型 | 説明 |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | プラグイン ID |
| `api.name`               | `string`                  | 表示名 |
| `api.version`            | `string?`                 | プラグインバージョン（任意） |
| `api.description`        | `string?`                 | プラグイン説明（任意） |
| `api.source`             | `string`                  | プラグインのソースパス |
| `api.rootDir`            | `string?`                 | プラグインのルートディレクトリ（任意） |
| `api.config`             | `OpenClawConfig`          | 現在の設定スナップショット（利用可能な場合は、アクティブなインメモリランタイムスナップショット） |
| `api.pluginConfig`       | `Record<string, unknown>` | `plugins.entries.<id>.config` から取得したプラグイン固有設定 |
| `api.runtime`            | `PluginRuntime`           | [ランタイムヘルパー](/ja-JP/plugins/sdk-runtime) |
| `api.logger`             | `PluginLogger`            | スコープ付きロガー（`debug`、`info`、`warn`、`error`） |
| `api.registrationMode`   | `PluginRegistrationMode`  | 現在のロードモード。`"setup-runtime"` は、完全エントリ前の軽量な起動 / セットアップウィンドウです |
| `api.resolvePath(input)` | `(string) => string`      | プラグインルート相対でパスを解決 |

## 内部モジュール規約

プラグイン内部では、内部インポートにローカルのバレルファイルを使ってください。

```
my-plugin/
  api.ts            # 外部利用者向け公開エクスポート
  runtime-api.ts    # 内部専用ランタイムエクスポート
  index.ts          # プラグインエントリポイント
  setup-entry.ts    # 軽量な setup 専用エントリ（任意）
```

<Warning>
  本番コードから、自分自身のプラグインを `openclaw/plugin-sdk/<your-plugin>`
  経由でインポートしてはいけません。内部インポートは `./api.ts` または
  `./runtime-api.ts` を経由させてください。SDK パスは外部コントラクト専用です。
</Warning>

ファサード経由で読み込まれるバンドル済みプラグインの公開サーフェス（`api.ts`、`runtime-api.ts`、
`index.ts`、`setup-entry.ts`、および同様の公開エントリファイル）は、OpenClaw がすでに動作中であれば、
アクティブなランタイム設定スナップショットを優先するようになっています。
まだランタイムスナップショットが存在しない場合は、ディスク上の解決済み設定ファイルにフォールバックします。

プロバイダープラグインは、ヘルパーが意図的にプロバイダー固有で、まだ汎用 SDK
サブパスに属していない場合、狭い範囲のプラグインローカルコントラクトバレルを公開することもできます。
現在のバンドル例では、Anthropic プロバイダーは Claude のストリームヘルパーを、
汎用の `plugin-sdk/*` コントラクトに Anthropic beta-header や `service_tier`
ロジックを昇格させる代わりに、自身の公開 `api.ts` / `contract-api.ts` シームに保持しています。

その他の現在のバンドル例:

- `@openclaw/openai-provider`: `api.ts` は provider builder、
  default-model ヘルパー、および realtime provider builder をエクスポート
- `@openclaw/openrouter-provider`: `api.ts` は provider builder に加えて
  オンボーディング / 設定ヘルパーをエクスポート

<Warning>
  拡張機能の本番コードでも、`openclaw/plugin-sdk/<other-plugin>` の
  インポートは避けてください。ヘルパーが本当に共有対象であれば、2 つのプラグインを結合させるのではなく、
  `openclaw/plugin-sdk/speech`、`.../provider-model-shared`、または他の
  capability 指向サーフェスのような中立的な SDK サブパスへ昇格させてください。
</Warning>

## 関連

- [Entry Points](/ja-JP/plugins/sdk-entrypoints) — `definePluginEntry` と `defineChannelPluginEntry` のオプション
- [Runtime Helpers](/ja-JP/plugins/sdk-runtime) — 完全な `api.runtime` 名前空間リファレンス
- [Setup and Config](/ja-JP/plugins/sdk-setup) — パッケージング、マニフェスト、設定スキーマ
- [Testing](/ja-JP/plugins/sdk-testing) — テストユーティリティと lint ルール
- [SDK Migration](/ja-JP/plugins/sdk-migration) — 非推奨サーフェスからの移行
- [Plugin Internals](/ja-JP/plugins/architecture) — 詳細なアーキテクチャと capability モデル
