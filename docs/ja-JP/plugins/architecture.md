---
read_when:
    - ネイティブな OpenClaw プラグインの構築またはデバッグ
    - プラグインの機能モデルや所有権の境界を理解すること
    - プラグインの読み込みパイプラインまたはレジストリに取り組むこと
    - プロバイダーのランタイムフックまたはチャネルプラグインを実装すること
sidebarTitle: Internals
summary: 'プラグイン内部: 機能モデル、所有権、コントラクト、読み込みパイプライン、およびランタイムヘルパー'
title: プラグイン内部
x-i18n:
    generated_at: "2026-04-12T04:43:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6165a9da8b40de3bb7334fcb16023da5515deb83c4897ca1df1726f4a97db9e0
    source_path: plugins/architecture.md
    workflow: 15
---

# プラグイン内部

<Info>
  これは**詳細なアーキテクチャリファレンス**です。実践的なガイドについては、以下を参照してください。
  - [Install and use plugins](/ja-JP/tools/plugin) — ユーザーガイド
  - [はじめに](/ja-JP/plugins/building-plugins) — 最初のプラグインチュートリアル
  - [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — メッセージングチャネルを構築する
  - [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — モデルプロバイダーを構築する
  - [SDK Overview](/ja-JP/plugins/sdk-overview) — import マップと登録 API
</Info>

このページでは、OpenClaw プラグインシステムの内部アーキテクチャを説明します。

## 公開機能モデル

機能は、OpenClaw 内部における公開された**ネイティブプラグイン**モデルです。すべての
ネイティブ OpenClaw プラグインは、1 つ以上の機能タイプに対して登録されます。

| 機能                   | 登録方法                                         | プラグイン例                         |
| ---------------------- | ------------------------------------------------ | ------------------------------------ |
| テキスト推論           | `api.registerProvider(...)`                      | `openai`, `anthropic`                |
| CLI 推論バックエンド   | `api.registerCliBackend(...)`                    | `openai`, `anthropic`                |
| 音声                   | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`            |
| リアルタイム文字起こし | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| リアルタイム音声       | `api.registerRealtimeVoiceProvider(...)`         | `openai`                             |
| メディア理解           | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| 画像生成               | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| 音楽生成               | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                  |
| 動画生成               | `api.registerVideoGenerationProvider(...)`       | `qwen`                               |
| Web フェッチ           | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| Web 検索               | `api.registerWebSearchProvider(...)`             | `google`                             |
| チャネル / メッセージング | `api.registerChannel(...)`                    | `msteams`, `matrix`                  |

機能を 1 つも登録せず、フック、ツール、または
サービスを提供するプラグインは、**従来の hook-only** プラグインです。このパターンも現在
完全にサポートされています。

### 外部互換性の方針

機能モデルはすでに core に導入されており、現在はバンドル済み / ネイティブプラグインで
使用されていますが、外部プラグインの互換性については「エクスポートされているのだから
凍結済みである」という基準よりも、さらに厳密な基準が必要です。

現在のガイダンス:

- **既存の外部プラグイン:** フックベースの統合が動作し続けるようにすること。これを
  互換性の基準線として扱います
- **新しいバンドル済み / ネイティブプラグイン:** ベンダー固有の直接的な依存や、新しい
  hook-only 設計よりも、明示的な機能登録を優先します
- **機能登録を採用する外部プラグイン:** 許可されています。ただし、docs がコントラクトを
  安定していると明示的に示していない限り、機能固有のヘルパーサーフェスは進化中であると
  考えてください

実務上のルール:

- 機能登録 API は意図された方向性です
- 移行期間中、従来のフックは外部プラグインにとって最も安全で破壊的変更のない経路のままです
- エクスポートされたヘルパーのサブパスはすべて同等ではありません。偶発的に露出した
  ヘルパーではなく、文書化された限定的なコントラクトを優先してください

### プラグインの形態

OpenClaw は、読み込まれたすべてのプラグインを、静的メタデータだけでなく、実際の
登録動作に基づいて形態ごとに分類します。

- **plain-capability** -- 機能タイプをちょうど 1 つ登録するもの（たとえば `mistral` の
  ような provider 専用プラグイン）
- **hybrid-capability** -- 複数の機能タイプを登録するもの（たとえば `openai` は
  テキスト推論、音声、メディア理解、画像生成を所有します）
- **hook-only** -- フック（型付きまたはカスタム）のみを登録し、機能、ツール、コマンド、
  サービスは登録しないもの
- **non-capability** -- ツール、コマンド、サービス、またはルートを登録するが、機能は
  登録しないもの

プラグインの形態と機能の内訳を確認するには、
`openclaw plugins inspect <id>` を使用してください。詳細は
[CLI reference](/cli/plugins#inspect) を参照してください。

### 従来のフック

`before_agent_start` フックは、hook-only プラグイン向けの互換性経路として引き続き
サポートされています。現実の従来プラグインは、今もこれに依存しています。

方向性:

- 動作し続けるようにする
- 従来方式として文書化する
- モデル / プロバイダーの上書きには `before_model_resolve` を優先する
- プロンプト変更には `before_prompt_build` を優先する
- 実際の使用量が減少し、フィクスチャカバレッジによって移行の安全性が証明されるまでは
  削除しない

### 互換性シグナル

`openclaw doctor` または `openclaw plugins inspect <id>` を実行すると、
次のいずれかのラベルが表示されることがあります。

| シグナル                 | 意味                                                         |
| ------------------------ | ------------------------------------------------------------ |
| **config valid**         | 設定は問題なく解析され、プラグインも解決されている          |
| **compatibility advisory** | プラグインがサポートされているが古いパターン（例: `hook-only`）を使用している |
| **legacy warning**       | プラグインが非推奨の `before_agent_start` を使用している     |
| **hard error**           | 設定が無効、またはプラグインの読み込みに失敗した            |

`hook-only` も `before_agent_start` も、現在あなたのプラグインを壊すことはありません --
`hook-only` は助言的なものにすぎず、`before_agent_start` も警告を出すだけです。これらの
シグナルは `openclaw status --all` と `openclaw plugins doctor` にも表示されます。

## アーキテクチャ概要

OpenClaw のプラグインシステムには 4 つのレイヤーがあります。

1. **マニフェスト + 検出**
   OpenClaw は、設定されたパス、workspace ルート、
   グローバル拡張ルート、およびバンドル済み拡張から候補プラグインを見つけます。検出では、
   ネイティブの `openclaw.plugin.json` マニフェストと、サポートされている bundle
   マニフェストを最初に読み取ります。
2. **有効化 + 検証**
   core は、検出されたプラグインが有効、無効、ブロック済み、または
   memory のような排他的スロットに選択されているかどうかを判断します。
3. **ランタイム読み込み**
   ネイティブ OpenClaw プラグインは jiti を通じてプロセス内で読み込まれ、
   中央レジストリに機能を登録します。互換性のある bundle は、ランタイムコードを import
   せずにレジストリレコードへ正規化されます。
4. **サーフェス消費**
   OpenClaw の残りの部分は、レジストリを読み取って、ツール、チャネル、
   プロバイダー設定、フック、HTTP ルート、CLI コマンド、およびサービスを公開します。

特にプラグイン CLI については、ルートコマンドの検出は 2 段階に分かれます。

- 解析時メタデータは `registerCli(..., { descriptors: [...] })` から取得されます
- 実際のプラグイン CLI モジュールは遅延読み込みのままとし、最初の呼び出し時に登録できます

これにより、プラグイン所有の CLI コードをプラグイン内に留めつつ、OpenClaw は解析前に
ルートコマンド名を予約できます。

重要な設計境界:

- 検出 + 設定検証は、プラグインコードを実行せずに、
  **マニフェスト / スキーマメタデータ** から動作できるべきです
- ネイティブのランタイム動作は、プラグインモジュールの `register(api)` パスから得られます

この分離により、OpenClaw は、完全なランタイムが有効になる前に、設定を検証し、
存在しない / 無効なプラグインを説明し、UI / スキーマのヒントを構築できます。

### Channel Plugins と共有 message ツール

Channel Plugins は、通常のチャット操作のために、送信 / 編集 / リアクション用の
個別ツールを別途登録する必要はありません。OpenClaw は 1 つの共有 `message`
ツールを core に保持し、チャネルプラグインはその背後にあるチャネル固有の検出と実行を
所有します。

現在の境界は次のとおりです。

- core は、共有 `message` ツールホスト、プロンプト配線、セッション / スレッドの
  管理、および実行ディスパッチを所有します
- チャネルプラグインは、スコープ付きアクション検出、機能検出、および任意の
  チャネル固有スキーマ断片を所有します
- チャネルプラグインは、会話 ID がどのようにスレッド ID をエンコードするか、
  または親会話から継承するかといった、プロバイダー固有のセッション会話文法を所有します
- チャネルプラグインは、自身のアクションアダプターを通じて最終アクションを実行します

チャネルプラグインに対する SDK サーフェスは
`ChannelMessageActionAdapter.describeMessageTool(...)` です。この統合された検出呼び出しにより、
プラグインは表示されるアクション、機能、スキーマへの寄与をまとめて返せるため、
それらの要素が食い違わなくなります。

core はランタイムスコープをこの検出ステップに渡します。重要なフィールドは以下です。

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- 信頼された受信元の `requesterSenderId`

これは、コンテキスト依存のプラグインにとって重要です。チャネルは、アクティブな
アカウント、現在のルーム / スレッド / メッセージ、または信頼されたリクエスター ID に
基づいて、message アクションを隠したり公開したりできます。しかも、core の `message`
ツールにチャネル固有の分岐をハードコードする必要はありません。

このため、embedded-runner ルーティングの変更も依然としてプラグイン側の作業です。runner は、
現在のチャット / セッション ID をプラグイン検出境界へ転送し、共有 `message`
ツールが現在のターンに適したチャネル所有のサーフェスを公開できるようにする責任があります。

チャネル所有の実行ヘルパーについては、バンドル済みプラグインは実行ランタイムを
自分自身の拡張モジュール内に保持する必要があります。core は、`src/agents/tools`
配下で Discord、Slack、Telegram、WhatsApp の message-action ランタイムを
もはや所有していません。個別の `plugin-sdk/*-action-runtime` サブパスは公開しておらず、
バンドル済みプラグインは、自分たちの拡張所有モジュールからローカルのランタイムコードを
直接 import する必要があります。

同じ境界は、一般にプロバイダー名付き SDK シームにも適用されます。core は Slack、
Discord、Signal、WhatsApp、または類似の拡張向けのチャネル固有 convenience barrel を
import すべきではありません。core が何らかの振る舞いを必要とする場合は、
バンドル済みプラグイン自身の `api.ts` / `runtime-api.ts` barrel を使用するか、
その必要性を共有 SDK 内の限定的な汎用機能へ昇格させてください。

poll については、特に 2 つの実行経路があります。

- `outbound.sendPoll` は、共通の poll モデルに適合するチャネル向けの共有ベースラインです
- `actions.handleAction("poll")` は、チャネル固有の poll セマンティクスや追加の poll
  パラメーターに対する推奨経路です

core は現在、プラグインの poll ディスパッチがアクションを拒否したあとにのみ、共有
poll 解析へ委譲します。そのため、プラグイン所有の poll ハンドラーは、汎用 poll
パーサーに先に妨げられることなく、チャネル固有の poll フィールドを受け取れます。

完全な起動シーケンスについては、[Load pipeline](#load-pipeline) を参照してください。

## 機能所有権モデル

OpenClaw は、ネイティブプラグインを、無関係な統合の寄せ集めではなく、
**会社** または **機能** の所有権境界として扱います。

これは次を意味します。

- 会社プラグインは通常、その会社に関する OpenClaw 向けサーフェスをすべて所有するべきです
- 機能プラグインは通常、自らが導入する機能サーフェス全体を所有するべきです
- チャネルは、プロバイダーの振る舞いを場当たり的に再実装するのではなく、
  共有された core 機能を利用するべきです

例:

- バンドル済みの `openai` プラグインは、OpenAI のモデルプロバイダー動作、および
  OpenAI の音声 + リアルタイム音声 + メディア理解 + 画像生成の動作を所有します
- バンドル済みの `elevenlabs` プラグインは、ElevenLabs の音声動作を所有します
- バンドル済みの `microsoft` プラグインは、Microsoft の音声動作を所有します
- バンドル済みの `google` プラグインは、Google のモデルプロバイダー動作に加えて、
  Google のメディア理解 + 画像生成 + Web 検索の動作を所有します
- バンドル済みの `firecrawl` プラグインは、Firecrawl の Web フェッチ動作を所有します
- バンドル済みの `minimax`、`mistral`、`moonshot`、`zai` プラグインは、
  それぞれのメディア理解バックエンドを所有します
- バンドル済みの `qwen` プラグインは、Qwen のテキストプロバイダー動作に加えて、
  メディア理解および動画生成の動作を所有します
- `voice-call` プラグインは機能プラグインです。これは通話トランスポート、ツール、CLI、
  ルート、および Twilio の media-stream bridge を所有しますが、ベンダープラグインを
  直接 import するのではなく、共有された音声機能、およびリアルタイム文字起こし /
  リアルタイム音声機能を利用します

意図された最終状態は次のとおりです:

- OpenAI は、テキストモデル、音声、画像、そして将来の動画にまたがるとしても、1 つのプラグインに存在します
- 別のベンダーも、自身のサーフェス領域について同じことができます
- チャネルは、どのベンダープラグインがそのプロバイダーを所有しているかを気にしません。core が公開する共有機能コントラクトを利用します

これが重要な区別です。

- **plugin** = 所有権境界
- **capability** = 複数のプラグインが実装または利用できる core コントラクト

したがって、OpenClaw が動画のような新しいドメインを追加する場合、最初の問いは
「どのプロバイダーが動画処理をハードコードすべきか」ではありません。最初の問いは
「core の動画機能コントラクトは何か」です。そのコントラクトが存在すれば、
ベンダープラグインはそれに対して登録でき、チャネル / 機能プラグインはそれを利用できます。

機能がまだ存在しない場合、通常は次の進め方が適切です。

1. core に不足している機能を定義する
2. それを型付きで plugin API / ランタイムを通じて公開する
3. その機能に対してチャネル / 機能を接続する
4. ベンダープラグインに実装を登録させる

これにより、所有権を明示したまま、単一ベンダーや一回限りのプラグイン固有コードパスに
依存する core の振る舞いを避けられます。

### 機能レイヤリング

コードをどこに置くべきかを判断する際は、次のメンタルモデルを使ってください。

- **core capability layer**: 共有オーケストレーション、ポリシー、フォールバック、設定の
  マージルール、配信セマンティクス、および型付きコントラクト
- **vendor plugin layer**: ベンダー固有 API、認証、モデルカタログ、音声合成、画像生成、
  将来の動画バックエンド、使用量エンドポイント
- **channel/feature plugin layer**: core の機能を利用し、それをサーフェス上に提示する
  Slack / Discord / voice-call などの統合

たとえば、TTS は次の形になります。

- core は、返信時の TTS ポリシー、フォールバック順序、設定、およびチャネル配信を所有します
- `openai`、`elevenlabs`、`microsoft` は、音声合成の実装を所有します
- `voice-call` は、電話向け TTS ランタイムヘルパーを利用します

将来の機能でも、同じパターンを優先すべきです。

### 複数機能を持つ会社プラグインの例

会社プラグインは、外から見て一貫性のあるものに感じられるべきです。OpenClaw に、
モデル、音声、リアルタイム文字起こし、リアルタイム音声、メディア理解、画像生成、
動画生成、Web フェッチ、Web 検索に対する共有コントラクトがあるなら、ベンダーは
それらすべてのサーフェスを 1 か所で所有できます。

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

重要なのは、ヘルパー名が正確に何であるかではありません。重要なのは形です。

- 1 つのプラグインがベンダーのサーフェスを所有する
- それでも core は機能コントラクトを所有する
- チャネルと機能プラグインは、ベンダーコードではなく `api.runtime.*` ヘルパーを利用する
- コントラクトテストでは、プラグインが自ら所有すると主張する機能を登録したことを
  検証できる

### 機能の例: 動画理解

OpenClaw は、すでに画像 / 音声 / 動画の理解を 1 つの共有機能として扱っています。
同じ所有権モデルがそこにも適用されます。

1. core が media-understanding コントラクトを定義する
2. ベンダープラグインが、該当するものとして `describeImage`、`transcribeAudio`、
   `describeVideo` を登録する
3. チャネルと機能プラグインは、ベンダーコードに直接接続するのではなく、
   共有された core の振る舞いを利用する

これにより、ある 1 つのプロバイダーの動画前提を core に埋め込まずに済みます。
プラグインはベンダーサーフェスを所有し、core は機能コントラクトとフォールバック動作を
所有します。

動画生成もすでに同じ流れを使っています。core が型付き機能コントラクトとランタイム
ヘルパーを所有し、ベンダープラグインが
`api.registerVideoGenerationProvider(...)` の実装をそれに対して登録します。

具体的なロールアウトチェックリストが必要ですか。以下を参照してください。
[Capability Cookbook](/ja-JP/plugins/architecture)。

## コントラクトと強制

プラグイン API サーフェスは、意図的に `OpenClawPluginApi` に型付けされ、
集約されています。このコントラクトは、サポートされる登録ポイントと、プラグインが
依存できるランタイムヘルパーを定義します。

これが重要な理由:

- プラグイン作者は、1 つの安定した内部標準を得られます
- core は、2 つのプラグインが同じ provider id を登録するような重複所有権を拒否できます
- 起動時に、不正な登録に対して実用的な診断を表示できます
- コントラクトテストは、バンドル済みプラグインの所有権を強制し、
  目に見えないドリフトを防げます

強制には 2 つのレイヤーがあります。

1. **ランタイム登録の強制**
   プラグインレジストリは、プラグイン読み込み時に登録を検証します。たとえば、
   重複した provider id、重複した speech provider id、および不正な登録は、
   未定義動作ではなくプラグイン診断を生みます。
2. **コントラクトテスト**
   バンドル済みプラグインは、テスト実行中にコントラクトレジストリへ記録されるため、
   OpenClaw は所有権を明示的に検証できます。現在これは、モデルプロバイダー、
   音声プロバイダー、Web 検索プロバイダー、およびバンドル済み登録の所有権に
   使用されています。

実際の効果として、OpenClaw は、どのプラグインがどのサーフェスを所有しているかを
事前に把握できます。これにより、所有権が暗黙ではなく、宣言され、型付けされ、
テスト可能になるため、core とチャネルはシームレスに合成できます。

### コントラクトに含めるべきもの

良いプラグインコントラクトは、次の特性を持ちます。

- 型付き
- 小さい
- 機能固有
- core が所有する
- 複数のプラグインで再利用できる
- ベンダー知識なしでチャネル / 機能が利用できる

悪いプラグインコントラクトは、次のようなものです。

- core に隠されたベンダー固有ポリシー
- レジストリを迂回する一回限りのプラグイン用 escape hatch
- ベンダー実装へ直接入り込むチャネルコード
- `OpenClawPluginApi` または `api.runtime` の一部ではない場当たり的なランタイムオブジェクト

迷ったら、抽象度を 1 段上げてください。まず機能を定義し、その後でプラグインを
そこへ接続させてください。

## 実行モデル

ネイティブ OpenClaw プラグインは、Gateway と**同一プロセス内**で実行されます。
サンドボックス化されていません。読み込まれたネイティブプラグインは、core コードと
同じプロセスレベルの信頼境界を持ちます。

意味すること:

- ネイティブプラグインは、ツール、ネットワークハンドラー、フック、サービスを登録できます
- ネイティブプラグインのバグは、gateway をクラッシュさせたり不安定化させたりできます
- 悪意あるネイティブプラグインは、OpenClaw プロセス内での任意コード実行と同等です

互換 bundle は、OpenClaw が現在それらをメタデータ / コンテンツパックとして扱うため、
デフォルトではより安全です。現在のリリースでは、これは主にバンドル済み Skills を意味します。

バンドルされていないプラグインには、allowlist と明示的な install / load パスを
使用してください。workspace プラグインは本番のデフォルトではなく、
開発時コードとして扱ってください。

バンドル済み workspace パッケージ名については、プラグイン id を npm 名に固定して
ください。デフォルトは `@openclaw/<id>` で、パッケージが意図的により限定的な
プラグインロールを公開する場合にのみ、承認済みの型付き接尾辞
`-provider`、`-plugin`、`-speech`、`-sandbox`、`-media-understanding`
を使用します。

重要な信頼に関する注意:

- `plugins.allow` は **plugin ids** を信頼し、ソースの来歴は信頼しません。
- バンドル済みプラグインと同じ id を持つ workspace プラグインは、その workspace
  プラグインが有効化 / allowlist されると、意図的にバンドル済みコピーを上書きします。
- これは通常のことであり、ローカル開発、パッチテスト、ホットフィックスに便利です。

## エクスポート境界

OpenClaw は実装上の convenience ではなく、機能をエクスポートします。

機能登録は公開のままにしつつ、コントラクトではないヘルパーエクスポートは削減します。

- バンドル済みプラグイン固有のヘルパーサブパス
- 公開 API を意図していないランタイム配線サブパス
- ベンダー固有の convenience helper
- 実装詳細である setup / オンボーディングヘルパー

一部のバンドル済みプラグインヘルパーサブパスは、互換性とバンドル済みプラグイン保守のため、
生成された SDK export map に依然として残っています。現在の例には
`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、`plugin-sdk/zalo`、
`plugin-sdk/zalo-setup`、および複数の `plugin-sdk/matrix*` シームが含まれます。
これらは、新しいサードパーティプラグイン向けの推奨 SDK パターンではなく、
予約された実装詳細エクスポートとして扱ってください。

## 読み込みパイプライン

起動時、OpenClaw はおおむね次の処理を行います。

1. 候補プラグインルートを検出する
2. ネイティブまたは互換 bundle のマニフェストと package メタデータを読み取る
3. 安全でない候補を拒否する
4. プラグイン設定（`plugins.enabled`、`allow`、`deny`、`entries`、
   `slots`、`load.paths`）を正規化する
5. 各候補の有効化状態を決定する
6. 有効なネイティブモジュールを jiti 経由で読み込む
7. ネイティブの `register(api)`（または従来の別名である `activate(api)`）フックを呼び出し、
   登録内容をプラグインレジストリに収集する
8. そのレジストリをコマンド / ランタイムサーフェスに公開する

<Note>
`activate` は `register` の従来の別名です。ローダーは、存在する方
（`def.register ?? def.activate`）を解決し、同じタイミングで呼び出します。
すべてのバンドル済みプラグインは `register` を使用しています。新しいプラグインでは
`register` を優先してください。
</Note>

安全ゲートは、ランタイム実行**前**に行われます。エントリがプラグインルート外に
逃げている場合、パスが world-writable な場合、またはバンドルされていないプラグインで
パス所有権が不審に見える場合、候補はブロックされます。

### Manifest-first の振る舞い

マニフェストは、コントロールプレーンにおける真実の情報源です。OpenClaw はこれを使って
次を行います。

- プラグインを識別する
- 宣言されたチャネル / Skills / 設定スキーマ、または bundle の機能を検出する
- `plugins.entries.<id>.config` を検証する
- Control UI のラベル / プレースホルダーを拡張する
- install / catalog メタデータを表示する
- プラグインランタイムを読み込まずに、軽量な activation および setup descriptor を保持する

ネイティブプラグインでは、ランタイムモジュールがデータプレーン部分です。これは、
フック、ツール、コマンド、またはプロバイダーフローのような実際の振る舞いを登録します。

オプションの manifest `activation` および `setup` ブロックは、コントロールプレーンに
留まります。これらは activation 計画と setup 検出のためのメタデータのみの descriptor であり、
ランタイム登録、`register(...)`、または `setupEntry` を置き換えるものではありません。

setup 検出では現在、`setup-api` にフォールバックする前に、`setup.providers` や
`setup.cliBackends` のような descriptor 所有 id を優先して候補プラグインを絞り込みます。
これは、setup 時ランタイムフックをまだ必要とするプラグインに対応するためです。
複数の検出済みプラグインが同じ正規化済み setup provider または CLI backend id を
主張した場合、setup lookup は検出順序に依存せず、曖昧な所有者を拒否します。

### ローダーがキャッシュするもの

OpenClaw は、短期間のプロセス内キャッシュを保持します。

- 検出結果
- manifest レジストリデータ
- 読み込まれたプラグインレジストリ

これらのキャッシュは、バースト的な起動や繰り返しコマンドのオーバーヘッドを軽減します。
これらは永続化ではなく、短命なパフォーマンスキャッシュとして考えるのが安全です。

パフォーマンスに関する注意:

- これらのキャッシュを無効にするには、
  `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` または
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` を設定してください。
- キャッシュ時間は `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` および
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` で調整できます。

## レジストリモデル

読み込まれたプラグインは、無作為な core グローバルを直接変更しません。代わりに、
中央のプラグインレジストリへ登録されます。

このレジストリは次を追跡します。

- プラグインレコード（識別情報、ソース、オリジン、状態、診断）
- ツール
- 従来のフックと型付きフック
- チャネル
- プロバイダー
- Gateway RPC ハンドラー
- HTTP ルート
- CLI レジストラ
- バックグラウンドサービス
- プラグイン所有コマンド

その後、core 機能はプラグインモジュールと直接やり取りするのではなく、このレジストリから
読み取ります。これにより、読み込みは一方向に保たれます。

- プラグインモジュール -> レジストリ登録
- core ランタイム -> レジストリ消費

この分離は、保守性にとって重要です。つまり、ほとんどの core サーフェスは
「すべてのプラグインモジュールを特別扱いする」必要はなく、
「レジストリを読む」という 1 つの統合ポイントだけを必要とします。

## 会話バインディングコールバック

会話をバインドするプラグインは、承認が解決されたときに反応できます。

バインド要求が承認または拒否されたあとにコールバックを受け取るには、
`api.onConversationBindingResolved(...)` を使用します。

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // A binding now exists for this plugin + conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // The request was denied; clear any local pending state.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

コールバックペイロードのフィールド:

- `status`: `"approved"` または `"denied"`
- `decision`: `"allow-once"`、`"allow-always"`、または `"deny"`
- `binding`: 承認された要求に対する解決済みバインディング
- `request`: 元の要求の要約、detach ヒント、送信者 id、および
  会話メタデータ

このコールバックは通知専用です。誰が会話をバインドできるかを変更するものではなく、
core の承認処理が完了したあとに実行されます。

## プロバイダーランタイムフック

プロバイダープラグインには、現在 2 つのレイヤーがあります。

- manifest メタデータ: ランタイム読み込み前に軽量なプロバイダー env 認証参照を行うための
  `providerAuthEnvVars`、認証を共有するプロバイダーバリアント向けの
  `providerAuthAliases`、ランタイム読み込み前に軽量なチャネル env / setup
  参照を行うための `channelEnvVars`、およびランタイム読み込み前に軽量な
  オンボーディング / auth-choice ラベルと CLI フラグメタデータを提供する
  `providerAuthChoices`
- 設定時フック: `catalog` / 従来の `discovery`、および `applyConfigDefaults`
- ランタイムフック: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw は引き続き、汎用エージェントループ、フェイルオーバー、transcript 処理、
およびツールポリシーを所有します。これらのフックは、プロバイダー固有の振る舞いのための
拡張サーフェスであり、推論トランスポート全体を丸ごとカスタム実装する必要はありません。

プロバイダーに env ベースの認証情報があり、汎用の auth / status / model-picker
パスがプラグインランタイムを読み込まずにそれを認識する必要がある場合は、
manifest の `providerAuthEnvVars` を使用してください。1 つの provider id が、
別の provider id の env vars、auth profiles、config ベース認証、および
API キーオンボーディング選択肢を再利用すべき場合は、manifest の
`providerAuthAliases` を使用してください。オンボーディング / auth-choice の CLI
サーフェスが、プロバイダーの choice id、グループラベル、および単純な 1 フラグ認証配線を、
プロバイダーランタイムを読み込まずに把握する必要がある場合は、manifest の
`providerAuthChoices` を使用してください。プロバイダーランタイムの `envVars` は、
オンボーディングラベルや OAuth client-id / client-secret の設定変数のような、
オペレーター向けヒントに使い続けてください。

チャネルに env 駆動の認証または setup があり、汎用 shell-env フォールバック、
config / status チェック、または setup プロンプトがチャネルランタイムを読み込まずに
それを認識する必要がある場合は、manifest の `channelEnvVars` を使用してください。

### フック順序と使い方

モデル / プロバイダープラグインについて、OpenClaw はおおむね次の順序でフックを呼び出します。
「When to use」列は、簡易的な判断ガイドです。

| #   | フック                            | 役割                                                                                                           | 使用するタイミング                                                                                                                          |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | `models.json` 生成時に、プロバイダー設定を `models.providers` に公開する                                      | プロバイダーがカタログまたは base URL のデフォルトを所有している                                                                            |
| 2   | `applyConfigDefaults`             | 設定の具体化中に、プロバイダー所有のグローバル設定デフォルトを適用する                                        | デフォルトが auth モード、env、またはプロバイダーのモデルファミリーのセマンティクスに依存する                                             |
| --  | _(built-in model lookup)_         | OpenClaw はまず通常のレジストリ / カタログ経路を試す                                                         | _(プラグインフックではない)_                                                                                                                |
| 3   | `normalizeModelId`                | 検索前に、従来または preview の model-id エイリアスを正規化する                                               | 正式なモデル解決の前に、エイリアスの整理をプロバイダーが所有している                                                                        |
| 4   | `normalizeTransport`              | 汎用モデル組み立て前に、同じトランスポートファミリー内のプロバイダー系 `api` / `baseUrl` を正規化する        | 同じトランスポートファミリー内のカスタム provider id に対するトランスポート整理をプロバイダーが所有している                              |
| 5   | `normalizeConfig`                 | ランタイム / プロバイダー解決前に `models.providers.<id>` を正規化する                                        | プラグインと共に配置すべき設定整理がプロバイダーに必要な場合。バンドル済み Google 系ヘルパーは、サポートされる Google 設定エントリも補完する |
| 6   | `applyNativeStreamingUsageCompat` | 設定プロバイダーに対して、ネイティブ streaming-usage 互換の書き換えを適用する                                 | エンドポイント駆動のネイティブ streaming usage メタデータ修正がプロバイダーに必要な場合                                                   |
| 7   | `resolveConfigApiKey`             | ランタイム auth 読み込み前に、設定プロバイダー向けの env-marker 認証を解決する                                | プロバイダー所有の env-marker API キー解決がある場合。`amazon-bedrock` には、ここに組み込みの AWS env-marker resolver もある             |
| 8   | `resolveSyntheticAuth`            | 平文を永続化せずに、local / self-hosted または設定ベースの認証を公開する                                      | プロバイダーが synthetic / local な認証マーカーで動作できる                                                                                |
| 9   | `resolveExternalAuthProfiles`     | プロバイダー所有の外部 auth profile をオーバーレイする。CLI / アプリ所有の認証情報では、デフォルトの `persistence` は `runtime-only` | リフレッシュトークンのコピーを永続化せずに、外部 auth 認証情報をプロバイダーが再利用する                                                   |
| 10  | `shouldDeferSyntheticProfileAuth` | 保存済み synthetic profile プレースホルダーを、env / 設定ベース認証より後順位にする                           | 優先順位を勝ち取るべきでない synthetic プレースホルダープロファイルをプロバイダーが保存している                                            |
| 11  | `resolveDynamicModel`             | まだローカルレジストリにないプロバイダー所有 model id に対する同期フォールバック                               | プロバイダーが任意の上流 model id を受け入れる                                                                                              |
| 12  | `prepareDynamicModel`             | 非同期ウォームアップを行い、その後 `resolveDynamicModel` を再実行する                                          | 未知 id の解決前にネットワークメタデータがプロバイダーに必要な場合                                                                          |
| 13  | `normalizeResolvedModel`          | embedded runner が解決済みモデルを使用する前の最終書き換え                                                     | トランスポートの書き換えは必要だが、依然として core トランスポートを使う場合                                                                |
| 14  | `contributeResolvedModelCompat`   | 別の互換トランスポートの背後にあるベンダーモデル向けの compat フラグを提供する                                 | プロバイダーが、プロバイダー自体を引き継がずに proxy トランスポート上の自分のモデルを認識する場合                                         |
| 15  | `capabilities`                    | 共有 core ロジックで使われる、プロバイダー所有の transcript / tooling メタデータ                              | transcript またはプロバイダーファミリー固有の癖をプロバイダーが扱う必要がある                                                              |
| 16  | `normalizeToolSchemas`            | embedded runner が参照する前に、ツールスキーマを正規化する                                                     | トランスポートファミリーのスキーマ整理がプロバイダーに必要な場合                                                                            |
| 17  | `inspectToolSchemas`              | 正規化後に、プロバイダー所有のスキーマ診断を表示する                                                           | core にプロバイダー固有ルールを教え込むことなく、キーワード警告を出したい場合                                                              |
| 18  | `resolveReasoningOutputMode`      | ネイティブかタグ付きかの reasoning-output コントラクトを選択する                                               | ネイティブフィールドではなく、タグ付きの reasoning / final 出力がプロバイダーに必要な場合                                                  |
| 19  | `prepareExtraParams`              | 汎用 stream オプションラッパーの前に、リクエストパラメーターを正規化する                                       | デフォルトのリクエストパラメーター、またはプロバイダーごとのパラメーター整理が必要な場合                                                   |
| 20  | `createStreamFn`                  | 通常の stream 経路を、カスタムトランスポートで完全に置き換える                                                 | プロバイダーがラッパーではなく、独自の wire protocol を必要とする場合                                                                       |
| 21  | `wrapStreamFn`                    | 汎用ラッパー適用後に stream ラッパーを適用する                                                                 | カスタムトランスポートなしで、リクエストヘッダー / 本文 / モデル互換ラッパーが必要な場合                                                    |
| 22  | `resolveTransportTurnState`       | ネイティブなターン単位のトランスポートヘッダーまたはメタデータを付与する                                       | 汎用トランスポートから、プロバイダーネイティブのターン識別情報を送信したい場合                                                              |
| 23  | `resolveWebSocketSessionPolicy`   | ネイティブ WebSocket ヘッダーまたはセッションクールダウンポリシーを付与する                                    | 汎用 WS トランスポートに対して、セッションヘッダーやフォールバックポリシーを調整したい場合                                                 |
| 24  | `formatApiKey`                    | auth-profile フォーマッター: 保存済み profile をランタイム `apiKey` 文字列に変換する                          | プロバイダーが追加の auth メタデータを保存し、カスタムなランタイムトークン形状を必要とする場合                                             |
| 25  | `refreshOAuth`                    | カスタム refresh endpoint または refresh 失敗ポリシー向けの OAuth refresh 上書き                              | プロバイダーが共有 `pi-ai` refresher に適合しない場合                                                                                       |
| 26  | `buildAuthDoctorHint`             | OAuth refresh 失敗時に付加される修復ヒントを構築する                                                           | refresh 失敗後のプロバイダー所有 auth 修復ガイダンスが必要な場合                                                                            |
| 27  | `matchesContextOverflowError`     | プロバイダー所有のコンテキストウィンドウ超過マッチャー                                                         | 汎用ヒューリスティクスでは見逃す生の overflow error をプロバイダーが持つ場合                                                                |
| 28  | `classifyFailoverReason`          | プロバイダー所有のフェイルオーバー理由分類                                                                     | 生の API / トランスポートエラーを、rate-limit / overload などへマップできる場合                                                             |
| 29  | `isCacheTtlEligible`              | proxy / backhaul プロバイダー向けの prompt-cache ポリシー                                                      | proxy 固有の cache TTL ゲーティングが必要な場合                                                                                             |
| 30  | `buildMissingAuthMessage`         | 汎用の認証欠如リカバリーメッセージの置き換え                                                                   | プロバイダー固有の認証欠如リカバリーヒントが必要な場合                                                                                      |
| 31  | `suppressBuiltInModel`            | 古くなった上流モデルの抑制と、任意のユーザー向けエラーヒント                                                   | 古い上流行を隠す、またはベンダーヒントに置き換える必要がある場合                                                                            |
| 32  | `augmentModelCatalog`             | discovery 後に synthetic / 最終カタログ行を追加する                                                            | `models list` や picker に、synthetic な forward-compat 行がプロバイダーに必要な場合                                                       |
| 33  | `isBinaryThinking`                | binary-thinking プロバイダー向けのオン / オフ推論トグル                                                        | プロバイダーが二値の thinking オン / オフのみを公開する場合                                                                                 |
| 34  | `supportsXHighThinking`           | 選択されたモデルにおける `xhigh` 推論サポート                                                                   | 一部のモデルだけで `xhigh` を有効にしたい場合                                                                                                |
| 35  | `resolveDefaultThinkingLevel`     | 特定のモデルファミリーに対するデフォルトの `/think` レベル                                                     | モデルファミリー向けのデフォルト `/think` ポリシーをプロバイダーが所有する場合                                                              |
| 36  | `isModernModelRef`                | live profile フィルターと smoke 選択のための modern-model マッチャー                                           | live / smoke の優先モデルマッチングをプロバイダーが所有する場合                                                                             |
| 37  | `prepareRuntimeAuth`              | 推論直前に、設定済み認証情報を実際のランタイムトークン / キーへ交換する                                        | プロバイダーがトークン交換または短命なリクエスト認証情報を必要とする場合                                                                    |
| 38  | `resolveUsageAuth`                | `/usage` および関連する status サーフェス向けの使用量 / 課金認証情報を解決する                                 | プロバイダーがカスタムの使用量 / クォータトークン解析、または異なる使用量認証情報を必要とする場合                                         |
| 39  | `fetchUsageSnapshot`              | auth 解決後に、プロバイダー固有の使用量 / クォータスナップショットを取得して正規化する                        | プロバイダー固有の使用量エンドポイントまたはペイロードパーサーが必要な場合                                                                 |
| 40  | `createEmbeddingProvider`         | memory / search 向けのプロバイダー所有 embedding アダプターを構築する                                         | memory embedding の振る舞いがプロバイダープラグインに属する場合                                                                            |
| 41  | `buildReplayPolicy`               | そのプロバイダー向けの transcript 処理を制御する replay policy を返す                                          | プロバイダーがカスタム transcript ポリシー（たとえば thinking ブロックの除去）を必要とする場合                                            |
| 42  | `sanitizeReplayHistory`           | 汎用 transcript クリーンアップ後に replay history を書き換える                                                 | 共有 compaction helper を超える、プロバイダー固有の replay 書き換えが必要な場合                                                           |
| 43  | `validateReplayTurns`             | embedded runner の前に、最終的な replay turn の検証または再整形を行う                                         | 汎用 sanitization のあとで、プロバイダートランスポートにより厳密な turn 検証が必要な場合                                                  |
| 44  | `onModelSelected`                 | モデルがアクティブになったときに、プロバイダー所有の選択後副作用を実行する                                    | モデルがアクティブになった際に、プロバイダーがテレメトリーまたはプロバイダー所有状態を必要とする場合                                      |

`normalizeModelId`、`normalizeTransport`、`normalizeConfig` は、まず一致した
プロバイダープラグインを確認し、その後、model id や transport / config を実際に変更する
フック対応プロバイダープラグインが見つかるまで、ほかのプラグインへフォールスルーします。
これにより、呼び出し元がどのバンドル済みプラグインが書き換えを所有しているかを知らなくても、
エイリアス / 互換プロバイダー shim を機能させられます。どのプロバイダーフックも、
サポート対象の Google 系 config エントリを書き換えなかった場合でも、バンドル済みの
Google config normalizer がその互換性クリーンアップを適用します。

プロバイダーに完全にカスタムの wire protocol やカスタムのリクエスト実行器が必要な場合、
それは別種の拡張です。これらのフックは、OpenClaw の通常の推論ループ上で引き続き動作する
プロバイダーの振る舞いのためのものです。

### プロバイダーの例

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### 組み込みの例

- Anthropic は `resolveDynamicModel`、`capabilities`、`buildAuthDoctorHint`、
  `resolveUsageAuth`、`fetchUsageSnapshot`、`isCacheTtlEligible`、
  `resolveDefaultThinkingLevel`、`applyConfigDefaults`、`isModernModelRef`、
  `wrapStreamFn` を使用します。これは、Claude 4.6 の forward-compat、
  プロバイダーファミリーのヒント、auth 修復ガイダンス、使用量エンドポイント統合、
  prompt-cache 適格性、auth 対応 config デフォルト、Claude の
  デフォルト / 適応的 thinking ポリシー、および beta ヘッダー、
  `/fast` / `serviceTier`、`context1m` に対する Anthropic 固有の
  stream shaping を所有しているためです。
- Anthropic の Claude 固有 stream helper は、現時点ではバンドル済みプラグイン自身の
  公開 `api.ts` / `contract-api.ts` シームに留まっています。そのパッケージサーフェスは、
  ある 1 つのプロバイダーの beta-header ルールに合わせて汎用 SDK を広げるのではなく、
  `wrapAnthropicProviderStream`、`resolveAnthropicBetas`、
  `resolveAnthropicFastMode`、`resolveAnthropicServiceTier`、
  およびより低レベルの Anthropic wrapper builder をエクスポートします。
- OpenAI は `resolveDynamicModel`、`normalizeResolvedModel`、
  `capabilities` に加えて `buildMissingAuthMessage`、`suppressBuiltInModel`、
  `augmentModelCatalog`、`supportsXHighThinking`、`isModernModelRef`
  を使用します。これは、GPT-5.4 の forward-compat、直接的な OpenAI の
  `openai-completions` -> `openai-responses` 正規化、Codex 対応 auth ヒント、
  Spark 抑制、synthetic な OpenAI list 行、および GPT-5 の thinking /
  live-model ポリシーを所有しているためです。`openai-responses-defaults`
  stream family は、attribution ヘッダー、`/fast` / `serviceTier`、
  テキスト verbosity、ネイティブ Codex web search、
  reasoning-compat ペイロード整形、および Responses のコンテキスト管理のための、
  共有ネイティブ OpenAI Responses wrapper を所有します。
- OpenRouter は `catalog` に加えて `resolveDynamicModel` と
  `prepareDynamicModel` を使います。これは、このプロバイダーが pass-through であり、
  OpenClaw の静的 catalog 更新前に新しい model id を公開することがあるためです。
  また、プロバイダー固有のリクエストヘッダー、ルーティングメタデータ、
  reasoning patch、prompt-cache ポリシーを core の外に保つために、
  `capabilities`、`wrapStreamFn`、`isCacheTtlEligible` も使います。
  その replay policy は `passthrough-gemini` family から来ており、
  `openrouter-thinking` stream family は、proxy reasoning 注入と、
  未対応モデル / `auto` のスキップを所有します。
- GitHub Copilot は `catalog`、`auth`、`resolveDynamicModel`、
  `capabilities` に加えて `prepareRuntimeAuth` と `fetchUsageSnapshot`
  を使います。これは、プロバイダー所有のデバイスログイン、モデルのフォールバック動作、
  Claude transcript の癖、GitHub token -> Copilot token 交換、
  およびプロバイダー所有の使用量エンドポイントが必要なためです。
- OpenAI Codex は `catalog`、`resolveDynamicModel`、
  `normalizeResolvedModel`、`refreshOAuth`、`augmentModelCatalog`
  に加えて `prepareExtraParams`、`resolveUsageAuth`、`fetchUsageSnapshot`
  を使います。これは、依然として core の OpenAI transport 上で動作しつつも、
  transport / base URL の正規化、OAuth refresh のフォールバックポリシー、
  デフォルト transport 選択、synthetic な Codex catalog 行、および
  ChatGPT の使用量エンドポイント統合を所有しているためです。
  直接の OpenAI と同じ `openai-responses-defaults` stream family を共有します。
- Google AI Studio と Gemini CLI OAuth は `resolveDynamicModel`、
  `buildReplayPolicy`、`sanitizeReplayHistory`、
  `resolveReasoningOutputMode`、`wrapStreamFn`、`isModernModelRef`
  を使います。これは、`google-gemini` replay family が Gemini 3.1 の
  forward-compat フォールバック、ネイティブ Gemini replay 検証、
  bootstrap replay sanitation、タグ付き reasoning-output mode、
  modern-model マッチングを所有し、`google-thinking` stream family が
  Gemini thinking ペイロード正規化を所有するためです。
  Gemini CLI OAuth はさらに、トークン整形、トークン解析、quota エンドポイント配線のために
  `formatApiKey`、`resolveUsageAuth`、`fetchUsageSnapshot` も使用します。
- Anthropic Vertex は `anthropic-by-model` replay family を通じて
  `buildReplayPolicy` を使用します。これにより、Claude 固有の replay cleanup は、
  すべての `anthropic-messages` transport ではなく、Claude id に限定されます。
- Amazon Bedrock は `buildReplayPolicy`、`matchesContextOverflowError`、
  `classifyFailoverReason`、`resolveDefaultThinkingLevel` を使います。
  これは、Anthropic-on-Bedrock トラフィックに対する Bedrock 固有の
  throttle / not-ready / context-overflow エラー分類を所有しているためです。
  その replay policy は引き続き同じ Claude 専用の `anthropic-by-model` ガードを共有します。
- OpenRouter、Kilocode、Opencode、Opencode Go は、
  `passthrough-gemini` replay family を通じて `buildReplayPolicy`
  を使用します。これは、Gemini モデルを OpenAI 互換 transport 経由で
  proxy し、ネイティブ Gemini replay 検証や bootstrap 書き換えなしで
  Gemini thought-signature sanitation を必要とするためです。
- MiniMax は `hybrid-anthropic-openai` replay family を通じて
  `buildReplayPolicy` を使用します。これは、1 つのプロバイダーが
  Anthropic-message と OpenAI 互換の両方のセマンティクスを所有するためです。
  Anthropic 側では Claude 専用の thinking-block drop を維持しつつ、
  reasoning output mode をネイティブへ上書きします。また、
  `minimax-fast-mode` stream family は、共有 stream path 上での
  fast-mode モデル書き換えを所有します。
- Moonshot は `catalog` に加えて `wrapStreamFn` を使います。
  これは、共有 OpenAI transport を依然として使用しつつ、
  プロバイダー所有の thinking ペイロード正規化が必要なためです。
  `moonshot-thinking` stream family は、config と `/think` 状態を
  そのネイティブな binary thinking ペイロードへマップします。
- Kilocode は `catalog`、`capabilities`、`wrapStreamFn`、
  `isCacheTtlEligible` を使います。これは、プロバイダー所有のリクエストヘッダー、
  reasoning ペイロード正規化、Gemini transcript ヒント、
  Anthropic cache-TTL ゲーティングが必要なためです。
  `kilocode-thinking` stream family は、共有 proxy stream path 上で
  Kilo thinking 注入を維持しつつ、`kilo/auto` や、明示的な reasoning
  ペイロードをサポートしないほかの proxy model id をスキップします。
- Z.AI は `resolveDynamicModel`、`prepareExtraParams`、`wrapStreamFn`、
  `isCacheTtlEligible`、`isBinaryThinking`、`isModernModelRef`、
  `resolveUsageAuth`、`fetchUsageSnapshot` を使います。これは、
  GLM-5 フォールバック、`tool_stream` デフォルト、binary thinking UX、
  modern-model マッチング、および使用量 auth と quota 取得の両方を
  所有しているためです。`tool-stream-default-on` stream family は、
  デフォルトで有効な `tool_stream` wrapper を、プロバイダーごとの手書き glue
  から切り離します。
- xAI は `normalizeResolvedModel`、`normalizeTransport`、
  `contributeResolvedModelCompat`、`prepareExtraParams`、`wrapStreamFn`、
  `resolveSyntheticAuth`、`resolveDynamicModel`、`isModernModelRef`
  を使います。これは、ネイティブ xAI Responses transport 正規化、
  Grok fast-mode エイリアス書き換え、デフォルト `tool_stream`、
  strict-tool / reasoning-payload のクリーンアップ、プラグイン所有ツール向けの
  フォールバック auth 再利用、forward-compat な Grok モデル解決、
  および xAI の tool-schema profile、未対応スキーマキーワード、
  ネイティブ `web_search`、HTML entity 化された tool-call 引数のデコードといった、
  プロバイダー所有の compat patch を所有しているためです。
- Mistral、OpenCode Zen、OpenCode Go は、transcript / tooling の癖を
  core の外に保つために `capabilities` のみを使います。
- `byteplus`、`cloudflare-ai-gateway`、`huggingface`、`kimi-coding`、
  `nvidia`、`qianfan`、`synthetic`、`together`、`venice`、
  `vercel-ai-gateway`、`volcengine` のような catalog のみの
  バンドル済みプロバイダーは、`catalog` のみを使います。
- Qwen はテキストプロバイダー向けに `catalog` を使い、マルチモーダルな
  サーフェス向けに共有の media-understanding と video-generation 登録も行います。
- MiniMax と Xiaomi は `catalog` に加えて usage フックを使います。
  これは、推論自体は共有 transport を通じて実行される一方で、
  `/usage` の振る舞いはプラグイン所有だからです。

## ランタイムヘルパー

プラグインは、`api.runtime` を介して選択された core ヘルパーにアクセスできます。
TTS の場合は次のとおりです。

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

注意:

- `textToSpeech` は、ファイル / ボイスノート向けサーフェスに対する通常の core TTS
  出力ペイロードを返します。
- core の `messages.tts` 設定とプロバイダー選択を使用します。
- PCM 音声バッファー + サンプルレートを返します。プラグイン側で
  プロバイダー向けに再サンプリング / エンコードする必要があります。
- `listVoices` はプロバイダーごとに任意です。ベンダー所有の voice picker
  または setup フローに使ってください。
- 音声一覧には、locale、gender、personality tag のような、プロバイダー対応
  picker 向けのより豊富なメタデータを含めることができます。
- 現時点で電話向けに対応しているのは OpenAI と ElevenLabs です。Microsoft は対応していません。

プラグインは `api.registerSpeechProvider(...)` を介して speech provider を登録することもできます。

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

注意:

- TTS ポリシー、フォールバック、および返信配信は core に保持してください。
- ベンダー所有の音声合成の振る舞いには speech provider を使ってください。
- 従来の Microsoft `edge` 入力は、`microsoft` provider id に正規化されます。
- 推奨される所有権モデルは会社指向です。OpenClaw がそれらの機能コントラクトを追加するにつれ、
  1 つのベンダープラグインがテキスト、音声、画像、将来のメディアプロバイダーを
  所有できます。

画像 / 音声 / 動画理解については、プラグインは汎用のキー / 値 bag ではなく、
1 つの型付き media-understanding provider を登録します。

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

注意:

- オーケストレーション、フォールバック、設定、チャネル配線は core に保持してください。
- ベンダーの振る舞いはプロバイダープラグインに保持してください。
- 加算的な拡張は、型付きのままにしてください。新しい任意メソッド、新しい任意の
  結果フィールド、新しい任意の機能、という形です。
- 動画生成もすでに同じパターンに従っています。
  - core が機能コントラクトとランタイムヘルパーを所有する
  - ベンダープラグインが `api.registerVideoGenerationProvider(...)` を登録する
  - 機能 / チャネルプラグインが `api.runtime.videoGeneration.*` を利用する

media-understanding のランタイムヘルパーについては、プラグインは次のように呼び出せます。

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

音声文字起こしについては、プラグインは media-understanding ランタイムか、
古い STT エイリアスのどちらかを使えます。

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

注意:

- `api.runtime.mediaUnderstanding.*` は、画像 / 音声 / 動画理解のための
  推奨される共有サーフェスです。
- core の media-understanding 音声設定（`tools.media.audio`）と
  プロバイダーフォールバック順序を使用します。
- 文字起こし結果が生成されなかった場合（たとえばスキップされた入力 /
  未対応入力）は `{ text: undefined }` を返します。
- `api.runtime.stt.transcribeAudioFile(...)` は互換性エイリアスとして残っています。

プラグインは `api.runtime.subagent` を通じて、バックグラウンドの subagent 実行を
起動することもできます。

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

注意:

- `provider` と `model` は、永続的なセッション変更ではなく、実行ごとの任意の上書きです。
- OpenClaw は、それらの上書きフィールドを信頼された呼び出し元に対してのみ有効にします。
- プラグイン所有のフォールバック実行では、オペレーターが
  `plugins.entries.<id>.subagent.allowModelOverride: true` で明示的に
  オプトインする必要があります。
- 信頼されたプラグインを特定の正規 `provider/model` ターゲットに制限するには
  `plugins.entries.<id>.subagent.allowedModels` を使い、任意のターゲットを
  明示的に許可するには `"*"` を使います。
- 信頼されていないプラグインの subagent 実行も動作しますが、上書き要求は
  暗黙にフォールバックされるのではなく拒否されます。

Web 検索については、プラグインはエージェントツール配線へ入り込む代わりに、
共有ランタイムヘルパーを利用できます。

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

プラグインは `api.registerWebSearchProvider(...)` を介して
Web 検索プロバイダーを登録することもできます。

注意:

- プロバイダー選択、認証情報解決、および共有リクエストセマンティクスは core に保持してください。
- ベンダー固有の検索トランスポートには Web 検索プロバイダーを使ってください。
- `api.runtime.webSearch.*` は、エージェントツールラッパーに依存せずに
  検索機能を必要とする機能 / チャネルプラグイン向けの推奨共有サーフェスです。

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: 設定された画像生成プロバイダーチェーンを使って画像を生成します。
- `listProviders(...)`: 利用可能な画像生成プロバイダーとその機能を一覧表示します。

## Gateway HTTP ルート

プラグインは `api.registerHttpRoute(...)` を使って HTTP エンドポイントを公開できます。

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

ルートフィールド:

- `path`: Gateway HTTP サーバー配下のルートパス
- `auth`: 必須。通常の Gateway 認証を要求するには `"gateway"` を使用し、
  プラグイン管理の認証 / webhook 検証には `"plugin"` を使用します。
- `match`: 任意。`"exact"`（デフォルト）または `"prefix"`。
- `replaceExisting`: 任意。同じプラグインが自分自身の既存ルート登録を置き換えることを許可します。
- `handler`: ルートがリクエストを処理した場合は `true` を返します。

注意:

- `api.registerHttpHandler(...)` は削除されており、使うとプラグイン読み込みエラーになります。
  代わりに `api.registerHttpRoute(...)` を使ってください。
- プラグインルートは `auth` を明示的に宣言しなければなりません。
- 完全に同一の `path + match` 競合は、`replaceExisting: true` でない限り拒否され、
  1 つのプラグインが別のプラグインのルートを置き換えることもできません。
- `auth` レベルが異なる重複ルートは拒否されます。`exact` / `prefix` の
  フォールスルーチェーンは、同じ auth レベル内だけにしてください。
- `auth: "plugin"` ルートは、オペレーターのランタイムスコープを自動的には受け取りません。
  これは特権付き Gateway helper 呼び出しではなく、プラグイン管理 webhook /
  署名検証のためのものです。
- `auth: "gateway"` ルートは Gateway リクエストランタイムスコープ内で実行されますが、
  そのスコープは意図的に保守的です。
  - 共有シークレット bearer 認証（`gateway.auth.mode = "token"` /
    `"password"`）では、呼び出し元が `x-openclaw-scopes` を送信しても、
    プラグインルートのランタイムスコープは `operator.write` に固定されます
  - 信頼された ID 付き HTTP モード（たとえば `trusted-proxy` や、
    プライベート ingress 上の `gateway.auth.mode = "none"`）では、
    `x-openclaw-scopes` ヘッダーが明示的に存在する場合にのみ、それを尊重します
  - そのような ID 付きプラグインルート要求で `x-openclaw-scopes` が存在しない場合、
    ランタイムスコープは `operator.write` にフォールバックします
- 実務上のルール: gateway 認証付きプラグインルートを暗黙の管理者サーフェスだと
  想定しないでください。ルートで管理者専用の振る舞いが必要なら、ID 付き認証モードを
  必須にし、明示的な `x-openclaw-scopes` ヘッダー契約を文書化してください。

## Plugin SDK の import パス

プラグイン作成時には、巨大な `openclaw/plugin-sdk` import ではなく、
SDK サブパスを使用してください。

- プラグイン登録プリミティブには `openclaw/plugin-sdk/plugin-entry`。
- 汎用の共有プラグイン向けコントラクトには `openclaw/plugin-sdk/core`。
- ルート `openclaw.json` Zod スキーマエクスポート（`OpenClawSchema`）には
  `openclaw/plugin-sdk/config-schema`。
- 共有 setup / auth / reply / webhook 配線には、
  `openclaw/plugin-sdk/channel-setup`、
  `openclaw/plugin-sdk/setup-runtime`、
  `openclaw/plugin-sdk/setup-adapter-runtime`、
  `openclaw/plugin-sdk/setup-tools`、
  `openclaw/plugin-sdk/channel-pairing`、
  `openclaw/plugin-sdk/channel-contract`、
  `openclaw/plugin-sdk/channel-feedback`、
  `openclaw/plugin-sdk/channel-inbound`、
  `openclaw/plugin-sdk/channel-lifecycle`、
  `openclaw/plugin-sdk/channel-reply-pipeline`、
  `openclaw/plugin-sdk/command-auth`、
  `openclaw/plugin-sdk/secret-input`、
  `openclaw/plugin-sdk/webhook-ingress`
  のような安定したチャネルプリミティブを使用します。`channel-inbound` は、
  debounce、mention マッチング、受信 mention-policy helper、
  envelope 整形、受信 envelope コンテキスト helper の共有ホームです。
  `channel-setup` は限定的な optional-install setup シームです。
  `setup-runtime` は、`setupEntry` / 遅延起動で使われるランタイム安全な setup
  サーフェスであり、import-safe な setup patch adapter を含みます。
  `setup-adapter-runtime` は env 対応の account-setup adapter シームです。
  `setup-tools` は、小さな CLI / archive / docs helper シーム
  （`formatCliCommand`、`detectBinary`、`extractArchive`、
  `resolveBrewExecutable`、`formatDocsLink`、`CONFIG_DIR`）です。
- 共有ランタイム / 設定 helper には、
  `openclaw/plugin-sdk/channel-config-helpers`、
  `openclaw/plugin-sdk/allow-from`、
  `openclaw/plugin-sdk/channel-config-schema`、
  `openclaw/plugin-sdk/telegram-command-config`、
  `openclaw/plugin-sdk/channel-policy`、
  `openclaw/plugin-sdk/approval-gateway-runtime`、
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`、
  `openclaw/plugin-sdk/approval-handler-runtime`、
  `openclaw/plugin-sdk/approval-runtime`、
  `openclaw/plugin-sdk/config-runtime`、
  `openclaw/plugin-sdk/infra-runtime`、
  `openclaw/plugin-sdk/agent-runtime`、
  `openclaw/plugin-sdk/lazy-runtime`、
  `openclaw/plugin-sdk/reply-history`、
  `openclaw/plugin-sdk/routing`、
  `openclaw/plugin-sdk/status-helpers`、
  `openclaw/plugin-sdk/text-runtime`、
  `openclaw/plugin-sdk/runtime-store`、
  `openclaw/plugin-sdk/directory-runtime`
  のようなドメインサブパスを使用します。
  `telegram-command-config` は Telegram カスタムコマンドの正規化 / 検証のための
  限定的な公開シームであり、バンドル済み Telegram コントラクトサーフェスが一時的に
  利用できない場合でも利用可能です。
  `text-runtime` は、assistant-visible-text の除去、markdown の
  レンダリング / 分割 helper、redaction helper、directive-tag helper、
  safe-text utility を含む、共有の text / markdown / logging シームです。
- 承認固有のチャネルシームでは、プラグイン上の 1 つの `approvalCapability`
  コントラクトを優先してください。すると core は、承認 auth、配信、レンダリング、
  ネイティブルーティング、遅延ネイティブハンドラーの振る舞いを、無関係な
  プラグインフィールドへ混在させるのではなく、その単一の機能を通じて読み取れます。
- `openclaw/plugin-sdk/channel-runtime` は非推奨であり、古いプラグイン向けの
  互換 shim としてのみ残されています。新しいコードは、より限定的な汎用プリミティブを
  import すべきであり、repo コードもこの shim への新しい import を追加すべきではありません。
- バンドル済み拡張の内部実装は非公開のままです。外部プラグインは
  `openclaw/plugin-sdk/*` サブパスのみを使用してください。OpenClaw の core / test
  コードは、プラグインパッケージルート配下の repo 公開エントリポイント
  `index.js`、`api.js`、`runtime-api.js`、`setup-entry.js`、
  `login-qr-api.js` のような限定ファイルを使用できます。core からも、
  ほかの拡張からも、プラグインパッケージの `src/*` を import してはいけません。
- repo エントリポイント分割:
  `<plugin-package-root>/api.js` は helper / types barrel、
  `<plugin-package-root>/runtime-api.js` はランタイム専用 barrel、
  `<plugin-package-root>/index.js` はバンドル済みプラグインエントリ、
  `<plugin-package-root>/setup-entry.js` は setup プラグインエントリです。
- 現在のバンドル済みプロバイダー例:
  - Anthropic は `api.js` / `contract-api.js` を使って、
    `wrapAnthropicProviderStream`、beta-header helper、
    `service_tier` 解析のような Claude stream helper を提供します。
  - OpenAI は `api.js` を使って、provider builder、default-model helper、
    realtime provider builder を提供します。
  - OpenRouter は `api.js` を使って、その provider builder と
    onboarding / config helper を提供し、一方で `register.runtime.js` は、
    repo ローカル用途として汎用の `plugin-sdk/provider-stream` helper を
    再エクスポートし続けることができます。
- facade によって読み込まれる公開エントリポイントは、アクティブなランタイム設定
  スナップショットが存在する場合はそれを優先し、OpenClaw がまだランタイム
  スナップショットを提供していない場合は、ディスク上の解決済み設定ファイルへ
  フォールバックします。
- 汎用の共有プリミティブは、引き続き推奨される公開 SDK コントラクトです。
  バンドル済みチャネルにブランド化された helper シームの小規模な予約済み互換セットは
  依然として存在します。これらは、バンドル保守 / 互換性シームとして扱ってください。
  新しいサードパーティ import 対象ではありません。新しいクロスチャネルコントラクトは、
  引き続き汎用 `plugin-sdk/*` サブパス、またはプラグインローカルの
  `api.js` / `runtime-api.js` barrel に配置すべきです。

互換性に関する注意:

- 新しいコードでは、ルートの `openclaw/plugin-sdk` barrel は避けてください。
- まず、限定的で安定したプリミティブを優先してください。新しい
  setup / pairing / reply / feedback / contract / inbound / threading /
  command / secret-input / webhook / infra / allowlist / status / message-tool
  サブパスは、新しいバンドル済みおよび外部プラグイン作業向けの意図された
  コントラクトです。
  ターゲットの解析 / マッチングは `openclaw/plugin-sdk/channel-targets` に
  属します。message action gate と reaction message-id helper は
  `openclaw/plugin-sdk/channel-actions` に属します。
- バンドル済み拡張固有の helper barrel は、デフォルトでは安定していません。
  ある helper がバンドル済み拡張にのみ必要なら、それを
  `openclaw/plugin-sdk/<extension>` に昇格させるのではなく、その拡張の
  ローカル `api.js` または `runtime-api.js` シームの背後に置いてください。
- 新しい共有 helper シームは、チャネルブランド付きではなく、汎用であるべきです。
  共有ターゲット解析は `openclaw/plugin-sdk/channel-targets` に属し、
  チャネル固有の内部実装は、所有するプラグインのローカル `api.js` または
  `runtime-api.js` シームの背後に留めてください。
- `image-generation`、`media-understanding`、`speech` のような
  機能固有サブパスが存在するのは、現在それらをバンドル済み / ネイティブプラグインが
  使用しているためです。だからといって、エクスポートされたすべての helper が
  長期的に凍結された外部コントラクトであることを意味するわけではありません。

## Message tool スキーマ

プラグインは、チャネル固有の `describeMessageTool(...)` スキーマ寄与を所有するべきです。
プロバイダー固有のフィールドは、共有 core ではなく、プラグイン内に置いてください。

共有可能なポータブルスキーマ断片には、
`openclaw/plugin-sdk/channel-actions` を通じてエクスポートされる汎用 helper を
再利用してください。

- ボタングリッド形式のペイロードには `createMessageToolButtonsSchema()`
- 構造化 card ペイロードには `createMessageToolCardSchema()`

あるスキーマ形状が 1 つのプロバイダーにしか意味を持たない場合は、それを共有 SDK に
昇格させるのではなく、そのプラグイン自身のソース内で定義してください。

## チャネルターゲット解決

チャネルプラグインは、チャネル固有のターゲットセマンティクスを所有するべきです。
共有の outbound host は汎用のまま保ち、プロバイダールールには messaging adapter
サーフェスを使ってください。

- `messaging.inferTargetChatType({ to })` は、正規化されたターゲットを
  ディレクトリ参照前に `direct`、`group`、`channel` のどれとして扱うべきかを決定します。
- `messaging.targetResolver.looksLikeId(raw, normalized)` は、ある入力が
  ディレクトリ検索ではなく id 風の解決へ直行すべきかを core に伝えます。
- `messaging.targetResolver.resolveTarget(...)` は、正規化後または
  ディレクトリ未検出後に、core が最終的なプロバイダー所有の解決を必要とする場合の
  プラグイン側フォールバックです。
- `messaging.resolveOutboundSessionRoute(...)` は、ターゲットが解決された後の
  プロバイダー固有セッションルート構築を所有します。

推奨される分割:

- peer / group 検索前に行うべきカテゴリ判断には `inferTargetChatType` を使う
- 「これを明示的 / ネイティブな target id として扱う」判定には `looksLikeId` を使う
- プロバイダー固有の正規化フォールバックには `resolveTarget` を使い、
  広範なディレクトリ検索には使わない
- chat id、thread id、JID、handle、room id のようなプロバイダーネイティブ id は、
  汎用 SDK フィールドではなく、`target` 値またはプロバイダー固有パラメーター内に
  保持する

## 設定ベースのディレクトリ

設定からディレクトリエントリを導出するプラグインは、そのロジックをプラグイン内に保持し、
`openclaw/plugin-sdk/directory-runtime` の共有 helper を再利用するべきです。

これは、チャネルが次のような設定ベースの peer / group を必要とする場合に使います。

- allowlist 駆動の DM peer
- 設定済み channel / group マップ
- アカウントスコープの静的ディレクトリフォールバック

`directory-runtime` の共有 helper は、汎用操作のみを扱います。

- クエリフィルタリング
- limit の適用
- deduping / 正規化 helper
- `ChannelDirectoryEntry[]` の構築

チャネル固有のアカウント検査と id 正規化は、プラグイン実装側に留めてください。

## プロバイダーカタログ

プロバイダープラグインは、
`registerProvider({ catalog: { run(...) { ... } } })` を使って、
推論用のモデルカタログを定義できます。

`catalog.run(...)` は、OpenClaw が `models.providers` に書き込むものと同じ形を返します。

- 1 つの provider エントリに対して `{ provider }`
- 複数の provider エントリに対して `{ providers }`

プラグインがプロバイダー固有の model id、base URL デフォルト、
または auth 制御のモデルメタデータを所有している場合は `catalog` を使ってください。

`catalog.order` は、OpenClaw の組み込み暗黙プロバイダーに対して、
プラグインの catalog がどのタイミングでマージされるかを制御します。

- `simple`: プレーンな API キーまたは env 駆動プロバイダー
- `profile`: auth profile が存在する場合に現れるプロバイダー
- `paired`: 複数の関連 provider エントリを合成するプロバイダー
- `late`: ほかの暗黙プロバイダーの後、最後のパス

後のプロバイダーがキー競合時に優先されるため、プラグインは同じ provider id を持つ
組み込み provider エントリを意図的に上書きできます。

互換性:

- `discovery` は従来の別名として引き続き動作します
- `catalog` と `discovery` の両方が登録された場合、OpenClaw は `catalog` を使います

## 読み取り専用のチャネル検査

プラグインがチャネルを登録する場合は、
`resolveAccount(...)` とあわせて `plugin.config.inspectAccount(cfg, accountId)` の
実装を優先してください。

理由:

- `resolveAccount(...)` はランタイム経路です。認証情報が完全に具体化されていることを
  前提にでき、必要な secret が欠けている場合は即座に失敗して構いません。
- `openclaw status`、`openclaw status --all`、
  `openclaw channels status`、`openclaw channels resolve`、
  doctor / config 修復フローのような読み取り専用コマンド経路では、設定内容を記述するためだけに
  ランタイム認証情報を具体化する必要があるべきではありません。

推奨される `inspectAccount(...)` の振る舞い:

- 説明的なアカウント状態のみを返す
- `enabled` と `configured` を保持する
- relevant な場合は、認証情報の source / status フィールドを含める。たとえば:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- 読み取り専用の可用性を報告するためだけに、生のトークン値を返す必要はありません。
  status 系コマンドには `tokenStatus: "available"`（および対応する source フィールド）で十分です。
- 認証情報が SecretRef 経由で設定されているが、現在のコマンド経路では利用できない場合は
  `configured_unavailable` を使う

これにより、読み取り専用コマンドは、クラッシュしたりアカウントを未設定だと誤報したりせず、
「設定済みだがこのコマンド経路では利用不可」と報告できます。

## パッケージパック

プラグインディレクトリには、`openclaw.extensions` を含む `package.json` を置けます。

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

各エントリは 1 つのプラグインになります。パックに複数の拡張が列挙されている場合、
プラグイン id は `name/<fileBase>` になります。

プラグインが npm 依存関係を import する場合は、そのディレクトリ内にインストールして
`node_modules` が利用可能になるようにしてください（`npm install` / `pnpm install`）。

セキュリティガードレール: すべての `openclaw.extensions` エントリは、symlink 解決後も
プラグインディレクトリ内に留まらなければなりません。パッケージディレクトリの外へ
逃げるエントリは拒否されます。

セキュリティに関する注意: `openclaw plugins install` は、プラグイン依存関係を
`npm install --omit=dev --ignore-scripts` でインストールします
（ライフサイクルスクリプトなし、ランタイムで dev dependencies なし）。
プラグイン依存ツリーは「pure JS/TS」に保ち、`postinstall` ビルドを必要とする
パッケージは避けてください。

任意: `openclaw.setupEntry` は、軽量な setup 専用モジュールを指せます。
OpenClaw が無効なチャネルプラグインの setup サーフェスを必要とする場合や、
チャネルプラグインが有効だが未設定の場合には、完全なプラグインエントリの代わりに
`setupEntry` を読み込みます。これにより、メインプラグインエントリがツール、フック、
またはほかのランタイム専用コードも配線している場合に、起動と setup を軽量化できます。

任意: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
を使うと、チャネルがすでに設定済みであっても、gateway の pre-listen 起動フェーズ中に
同じ `setupEntry` パスへチャネルプラグインをオプトインできます。

これを使うのは、gateway が listen を開始する前に存在しなければならない起動サーフェスを
`setupEntry` が完全にカバーしている場合だけにしてください。実務上、これは setup entry が
起動時に依存するすべてのチャネル所有機能を登録しなければならないことを意味します。たとえば:

- チャネル登録そのもの
- gateway が listen を開始する前に利用可能でなければならない HTTP ルート
- 同じ時間枠に存在しなければならない gateway method、tool、service

完全エントリが依然として何らかの必須起動機能を所有している場合は、このフラグを
有効にしないでください。デフォルト動作のままにし、起動時に OpenClaw が完全エントリを
読み込むようにしてください。

バンドル済みチャネルは、完全なチャネルランタイムが読み込まれる前に core が参照できる
setup 専用コントラクトサーフェス helper を公開することもできます。
現在の setup promotion サーフェスは次のとおりです。

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

core は、完全なプラグインエントリを読み込まずに、従来の単一アカウントチャネル設定を
`channels.<id>.accounts.*` に昇格する必要がある場合に、このサーフェスを使用します。
現在のバンドル済み例は Matrix です。名前付きアカウントがすでに存在する場合は、
認証 / bootstrap キーだけを名前付き昇格アカウントへ移動し、
常に `accounts.default` を作成するのではなく、設定済みの非正規な
デフォルトアカウントキーを保持できます。

これらの setup patch adapter により、バンドル済みコントラクトサーフェスの検出は遅延のままです。
import 時間は軽いままで、promotion サーフェスはモジュール import 時に
バンドル済みチャネル起動へ再突入するのではなく、最初の使用時にのみ読み込まれます。

それらの起動サーフェスに gateway RPC method が含まれる場合は、
プラグイン固有のプレフィックス上に置いてください。core 管理者名前空間
（`config.*`、`exec.approvals.*`、`wizard.*`、`update.*`）は予約済みであり、
プラグインがより狭いスコープを要求したとしても、常に `operator.admin` に解決されます。

例:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### チャネルカタログメタデータ

チャネルプラグインは、`openclaw.channel` を通じて setup / discovery メタデータを、
`openclaw.install` を通じて install ヒントを公開できます。これにより、core の
catalog をデータフリーに保てます。

例:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

最小例を超えて有用な `openclaw.channel` フィールド:

- `detailLabel`: より豊かな catalog / status サーフェス向けの補助ラベル
- `docsLabel`: docs リンクのリンクテキストを上書きする
- `preferOver`: この catalog エントリが上位に来るべき、より低優先度の
  plugin / channel id
- `selectionDocsPrefix`、`selectionDocsOmitLabel`、`selectionExtras`:
  選択サーフェス用コピー制御
- `markdownCapable`: outbound 整形判断のために、そのチャネルが
  markdown 対応であることを示す
- `exposure.configured`: `false` に設定すると、設定済みチャネル一覧サーフェスから
  そのチャネルを隠す
- `exposure.setup`: `false` に設定すると、対話型 setup / configure picker から
  そのチャネルを隠す
- `exposure.docs`: docs ナビゲーションサーフェスにおいて、そのチャネルを
  internal / private として示す
- `showConfigured` / `showInSetup`: 互換性のために引き続き受け付ける従来の別名です。
  `exposure` を優先してください
- `quickstartAllowFrom`: そのチャネルを標準のクイックスタート `allowFrom`
  フローにオプトインする
- `forceAccountBinding`: アカウントが 1 つしか存在しない場合でも、
  明示的なアカウントバインディングを必須にする
- `preferSessionLookupForAnnounceTarget`: announce ターゲット解決時に
  セッション検索を優先する

OpenClaw は、**外部チャネルカタログ**（たとえば MPM レジストリエクスポート）も
マージできます。次のいずれかに JSON ファイルを配置してください。

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

または、`OPENCLAW_PLUGIN_CATALOG_PATHS`（または `OPENCLAW_MPM_CATALOG_PATHS`）で、
1 つ以上の JSON ファイルを指定してください
（カンマ / セミコロン / `PATH` 区切り）。各ファイルは
`{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`
を含む必要があります。パーサーは、`"entries"` キーに対する従来の別名として
`"packages"` または `"plugins"` も受け付けます。

## コンテキストエンジンプラグイン

コンテキストエンジンプラグインは、取り込み、組み立て、圧縮のためのセッション
コンテキストオーケストレーションを所有します。プラグインから
`api.registerContextEngine(id, factory)` を使って登録し、アクティブなエンジンは
`plugins.slots.contextEngine` で選択します。

これは、プラグインが memory search やフックを追加するだけでなく、デフォルトの
コンテキストパイプライン自体を置き換える、または拡張する必要がある場合に使います。

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

エンジンが圧縮アルゴリズムを**所有しない**場合でも、`compact()` は実装し、
明示的に委譲してください。

```ts
import {
  buildMemorySystemPromptAddition,
  delegateCompactionToRuntime,
} from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## 新しい機能を追加する

プラグインが現在の API に収まらない振る舞いを必要とする場合は、
プライベートな直接依存でプラグインシステムを迂回しないでください。
不足している機能を追加してください。

推奨される手順:

1. core コントラクトを定義する
   core が所有すべき共有動作を決めます。ポリシー、フォールバック、設定マージ、
   ライフサイクル、チャネル向けセマンティクス、およびランタイムヘルパーの形です。
2. 型付きのプラグイン登録 / ランタイムサーフェスを追加する
   最小限で有用な型付き機能サーフェスを、`OpenClawPluginApi` や
   `api.runtime` に拡張します。
3. core + チャネル / 機能コンシューマーを接続する
   チャネルと機能プラグインは、ベンダー実装を直接 import するのではなく、
   core を通じて新しい機能を利用するべきです。
4. ベンダー実装を登録する
   その後、ベンダープラグインがその機能に対して自分たちのバックエンドを登録します。
5. コントラクトカバレッジを追加する
   所有権と登録形状が時間とともに明示的に保たれるよう、テストを追加します。

これが、OpenClaw が 1 つのプロバイダーの世界観にハードコードされることなく、
明確な方針を保てる理由です。具体的なファイルチェックリストと実例については、
[Capability Cookbook](/ja-JP/plugins/architecture) を参照してください。

### 機能チェックリスト

新しい機能を追加する場合、実装では通常、次のサーフェスをまとめて変更する必要があります。

- `src/<capability>/types.ts` の core コントラクト型
- `src/<capability>/runtime.ts` の core runner / ランタイムヘルパー
- `src/plugins/types.ts` のプラグイン API 登録サーフェス
- `src/plugins/registry.ts` のプラグインレジストリ配線
- 機能 / チャネルプラグインがそれを利用する必要がある場合は
  `src/plugins/runtime/*` のプラグインランタイム公開
- `src/test-utils/plugin-registration.ts` の capture / test helper
- `src/plugins/contracts/registry.ts` の所有権 / コントラクト検証
- `docs/` のオペレーター / プラグイン docs

これらのサーフェスのどれかが欠けている場合は、通常、その機能がまだ完全には
統合されていない兆候です。

### 機能テンプレート

最小パターン:

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// shared runtime helper for feature/channel plugins
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

コントラクトテストパターン:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

これにより、ルールは単純に保たれます。

- core が機能コントラクト + オーケストレーションを所有する
- ベンダープラグインがベンダー実装を所有する
- 機能 / チャネルプラグインがランタイムヘルパーを利用する
- コントラクトテストが所有権を明示的に保つ
