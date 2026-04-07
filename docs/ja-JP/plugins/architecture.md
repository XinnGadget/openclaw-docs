---
read_when:
    - ネイティブ OpenClaw プラグインを構築またはデバッグする場合
    - プラグインの capability モデルや所有権の境界を理解したい場合
    - プラグインのロードパイプラインやレジストリに取り組んでいる場合
    - プロバイダーのランタイムフックやチャネルプラグインを実装する場合
sidebarTitle: Internals
summary: 'プラグイン内部: capability モデル、所有権、コントラクト、ロードパイプライン、ランタイムヘルパー'
title: プラグイン内部
x-i18n:
    generated_at: "2026-04-07T04:47:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9c4b0602df12965a29881eab33b0885f991aeefa2a3fdf3cefc1a7770d6dabe0
    source_path: plugins/architecture.md
    workflow: 15
---

# プラグイン内部

<Info>
  これは**詳細なアーキテクチャリファレンス**です。実践的なガイドについては、以下を参照してください:
  - [Install and use plugins](/ja-JP/tools/plugin) — ユーザーガイド
  - [はじめに](/ja-JP/plugins/building-plugins) — 最初のプラグインチュートリアル
  - [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — メッセージングチャネルを構築する
  - [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — モデルプロバイダーを構築する
  - [SDK Overview](/ja-JP/plugins/sdk-overview) — インポートマップと登録 API
</Info>

このページでは、OpenClaw プラグインシステムの内部アーキテクチャを扱います。

## 公開 capability モデル

Capabilities は、OpenClaw 内部における公開の**ネイティブプラグイン**モデルです。すべての
ネイティブ OpenClaw プラグインは、1 つ以上の capability タイプに対して登録されます。

| Capability             | 登録メソッド                                     | プラグイン例                          |
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
| Web 取得               | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| Web 検索               | `api.registerWebSearchProvider(...)`             | `google`                             |
| チャネル / メッセージング | `api.registerChannel(...)`                    | `msteams`, `matrix`                  |

capability を 1 つも登録せず、フック、ツール、または
サービスを提供するプラグインは、**legacy hook-only** プラグインです。このパターンも引き続き完全にサポートされています。

### 外部互換性の方針

capability モデルはすでにコアに導入されており、現在
バンドル済み/ネイティブプラグインで使用されていますが、外部プラグインの互換性には
「export されているので固定されている」というだけでは不十分で、より厳格な基準が必要です。

現在のガイダンス:

- **既存の外部プラグイン:** フックベースの統合を動作させ続けること。
  これを互換性の基準線として扱います
- **新しいバンドル済み/ネイティブプラグイン:** ベンダー固有の深い依存や
  新しい hook-only 設計ではなく、明示的な capability 登録を優先します
- **capability 登録を採用する外部プラグイン:** 許可されますが、
  capability 固有のヘルパーサーフェスは、ドキュメントで安定コントラクトとして明示されない限り、
  進化中のものとして扱ってください

実務上のルール:

- capability 登録 API は意図された方向です
- 移行中の外部プラグインにとって、legacy hooks は依然として
  破壊的変更を避ける最も安全な経路です
- export された helper subpath はすべて同じではありません。偶発的な
  helper export ではなく、文書化された狭いコントラクトを優先してください

### プラグイン形状

OpenClaw は、ロードされたすべてのプラグインを、静的メタデータではなく
実際の登録動作に基づいて形状分類します。

- **plain-capability** -- ちょうど 1 種類の capability だけを登録します（例:
  `mistral` のような provider-only プラグイン）
- **hybrid-capability** -- 複数の capability タイプを登録します（例:
  `openai` はテキスト推論、音声、メディア理解、画像生成を管理します）
- **hook-only** -- フック（型付きまたはカスタム）のみを登録し、
  capabilities、tools、commands、services は登録しません
- **non-capability** -- tools、commands、services、または routes を登録しますが、
  capabilities は登録しません

プラグインの形状と capability の内訳を確認するには、`openclaw plugins inspect <id>` を使用してください。
詳細は [CLI reference](/cli/plugins#inspect) を参照してください。

### 旧式フック

`before_agent_start` フックは、hook-only プラグイン向けの互換経路として引き続きサポートされています。
現実の旧来プラグインが依然としてこれに依存しています。

方針:

- 動作を維持する
- legacy として文書化する
- モデル/プロバイダー上書き作業には `before_model_resolve` を優先する
- プロンプト変更作業には `before_prompt_build` を優先する
- 実際の利用が減少し、フィクスチャカバレッジで移行の安全性が証明されるまで削除しない

### 互換性シグナル

`openclaw doctor` または `openclaw plugins inspect <id>` を実行すると、
次のいずれかのラベルが表示されることがあります。

| シグナル                  | 意味                                                         |
| ------------------------- | ------------------------------------------------------------ |
| **config valid**          | 設定は正常に解析され、プラグインも正常に解決される           |
| **compatibility advisory** | プラグインがサポートされているが古いパターンを使用している（例: `hook-only`） |
| **legacy warning**        | プラグインが非推奨の `before_agent_start` を使用している     |
| **hard error**            | 設定が不正、またはプラグインのロードに失敗した               |

`hook-only` も `before_agent_start` も、現時点であなたのプラグインを壊すことはありません --
`hook-only` は助言であり、`before_agent_start` は警告を出すだけです。これらの
シグナルは `openclaw status --all` と `openclaw plugins doctor` にも表示されます。

## アーキテクチャ概要

OpenClaw のプラグインシステムは 4 つの層を持ちます。

1. **マニフェスト + 検出**
   OpenClaw は、設定されたパス、ワークスペースルート、
   グローバル拡張ルート、およびバンドル済み拡張から候補プラグインを探します。
   検出では、まずネイティブの `openclaw.plugin.json` マニフェストと、
   サポートされる bundle manifest を読み取ります。
2. **有効化 + 検証**
   コアは、検出されたプラグインが有効、無効、ブロック対象、
   またはメモリのような排他的スロットに選択されるかどうかを決定します。
3. **ランタイムロード**
   ネイティブ OpenClaw プラグインは jiti によりプロセス内でロードされ、
   中央レジストリに capabilities を登録します。互換 bundle は
   ランタイムコードを import せずにレジストリレコードへ正規化されます。
4. **サーフェス消費**
   OpenClaw のその他の部分は、レジストリを読み取って tools、channels、provider
   setup、hooks、HTTP routes、CLI commands、および services を公開します。

特にプラグイン CLI では、ルートコマンド検出は 2 段階に分かれます。

- 解析時メタデータは `registerCli(..., { descriptors: [...] })` から取得されます
- 実際のプラグイン CLI モジュールは遅延のままにでき、最初の呼び出し時に登録されます

これにより、プラグイン所有の CLI コードをプラグイン内に保持しながら、
OpenClaw は解析前にルートコマンド名を予約できます。

重要な設計境界:

- 検出 + 設定検証は、プラグインコードを実行せずに
  **manifest/schema metadata** から動作するべきです
- ネイティブのランタイム動作は、プラグインモジュールの `register(api)` 経路から生じます

この分離により、OpenClaw は設定を検証し、不足/無効なプラグインを説明し、
完全なランタイムが有効になる前に UI/schema ヒントを構築できます。

### チャネルプラグインと共有 message tool

チャネルプラグインは、通常のチャット操作のために別個の送信/編集/リアクション tool を
登録する必要はありません。OpenClaw は 1 つの共有 `message` tool をコアに保持し、
チャネルプラグインはその背後にあるチャネル固有の検出と実行を管理します。

現在の境界:

- コアは共有 `message` tool ホスト、プロンプト配線、session/thread
  管理、および実行ディスパッチを管理します
- チャネルプラグインはスコープ付きアクション検出、capability 検出、および
  チャネル固有の schema fragment を管理します
- チャネルプラグインは、conversation id が thread id をどうエンコードするか、
  あるいは親 conversation からどう継承するかのような、
  プロバイダー固有の session conversation 文法を管理します
- チャネルプラグインは action adapter を通じて最終アクションを実行します

チャネルプラグイン向けの SDK サーフェスは
`ChannelMessageActionAdapter.describeMessageTool(...)` です。この統一された検出呼び出しにより、
プラグインは可視アクション、capabilities、および schema
contribution をまとめて返せるため、これらが互いに乖離しません。

コアはその検出ステップにランタイムスコープを渡します。重要なフィールドは次のとおりです。

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- 信頼済み受信元の `requesterSenderId`

これはコンテキスト依存プラグインにとって重要です。チャネルは、
アクティブなアカウント、現在の room/thread/message、または
信頼済み requester identity に基づいて、message action を非表示または公開できます。
コアの `message` tool にチャネル固有の分岐をハードコードする必要はありません。

これが、embedded-runner のルーティング変更が依然としてプラグイン作業である理由です。ランナーは、
共有 `message` tool が現在のターンに対して適切なチャネル所有サーフェスを公開できるよう、
現在の chat/session identity をプラグイン検出境界へ転送する責任を負います。

チャネル所有の実行ヘルパーについては、バンドル済みプラグインは実行
ランタイムを自分の拡張モジュール内に保持するべきです。コアはもはや Discord、
Slack、Telegram、または WhatsApp の message-action ランタイムを
`src/agents/tools` 配下で管理しません。
別個の `plugin-sdk/*-action-runtime` subpath は公開しておらず、
バンドル済みプラグインはそのローカル runtime code を
自身の拡張所有モジュールから直接 import するべきです。

同じ境界は、一般に provider 名付き SDK seam にも適用されます。コアは
Slack、Discord、Signal、
WhatsApp、または類似の拡張向けチャネル固有 convenience barrel を import するべきではありません。
コアが動作を必要とする場合は、バンドル済みプラグイン自身の `api.ts` / `runtime-api.ts` barrel を
利用するか、その必要性を共有 SDK 内の狭い汎用 capability へ昇格させてください。

特に polls には、2 つの実行経路があります。

- `outbound.sendPoll` は、共通の
  poll モデルに適合するチャネル向けの共有ベースラインです
- `actions.handleAction("poll")` は、チャネル固有の
  poll セマンティクスや追加 poll パラメータ向けの推奨経路です

コアは現在、プラグイン poll ディスパッチがアクションを拒否した後まで共有 poll 解析を遅延させるため、
プラグイン所有の poll ハンドラーは、汎用 poll parser に先にブロックされることなく、
チャネル固有の poll フィールドを受け付けられます。

完全な起動シーケンスについては [Load pipeline](#load-pipeline) を参照してください。

## Capability 所有権モデル

OpenClaw は、ネイティブプラグインを、無関係な統合の寄せ集めとしてではなく、
**会社** または **機能** の所有権境界として扱います。

つまり:

- 会社プラグインは通常、その会社の OpenClaw 向け
  サーフェスをすべて管理するべきです
- 機能プラグインは通常、導入する機能サーフェス全体を管理するべきです
- チャネルは、プロバイダー動作を場当たり的に再実装するのではなく、
  共有コア capability を消費するべきです

例:

- バンドルされた `openai` プラグインは、OpenAI のモデルプロバイダー動作と、OpenAI の
  speech + realtime-voice + media-understanding + image-generation 動作を管理します
- バンドルされた `elevenlabs` プラグインは ElevenLabs の speech 動作を管理します
- バンドルされた `microsoft` プラグインは Microsoft の speech 動作を管理します
- バンドルされた `google` プラグインは、Google のモデルプロバイダー動作に加えて、Google の
  media-understanding + image-generation + web-search 動作を管理します
- バンドルされた `firecrawl` プラグインは Firecrawl の web-fetch 動作を管理します
- バンドルされた `minimax`, `mistral`, `moonshot`, `zai` プラグインは、それぞれの
  media-understanding バックエンドを管理します
- バンドルされた `qwen` プラグインは、Qwen の text-provider 動作に加えて
  media-understanding と video-generation 動作を管理します
- `voice-call` プラグインは機能プラグインです。通話トランスポート、tools、
  CLI、routes、および Twilio media-stream ブリッジを管理しますが、
  ベンダープラグインを直接 import する代わりに、共有の speech、
  realtime-transcription、および realtime-voice capabilities を消費します

目指す最終状態は次のとおりです。

- OpenAI は、テキストモデル、speech、images、そして
  将来の video にまたがっても、1 つのプラグインに存在する
- 他のベンダーも、自身のサーフェス領域について同じことを行える
- チャネルは、どのベンダープラグインがプロバイダーを管理しているかを気にせず、
  コアが公開する共有 capability コントラクトを消費する

ここでの重要な区別:

- **plugin** = 所有権境界
- **capability** = 複数のプラグインが実装または消費できるコアコントラクト

したがって、OpenClaw が video のような新しいドメインを追加する場合、
最初の問いは
「どのプロバイダーが video handling をハードコードするべきか」ではありません。最初の問いは
「コアの video capability コントラクトは何か」です。そのコントラクトが存在すれば、
ベンダープラグインはそれに対して登録でき、チャネル/機能プラグインはそれを消費できます。

capability がまだ存在しない場合、通常は次の手順が正しい動きです。

1. コアで不足している capability を定義する
2. それを型付きでプラグイン API/ランタイムを通じて公開する
3. チャネル/機能をその capability に対して配線する
4. ベンダープラグインに実装を登録させる

これにより、所有権を明示したまま、単一ベンダーや単発のプラグイン固有コードパスに
依存するコア動作を避けられます。

### Capability レイヤリング

コードの配置を判断するときは、次のメンタルモデルを使ってください。

- **core capability layer**: 共有オーケストレーション、ポリシー、フォールバック、config
  merge rules、delivery semantics、および型付きコントラクト
- **vendor plugin layer**: ベンダー固有 API、auth、model catalogs、speech
  synthesis、image generation、将来の video backends、usage endpoints
- **channel/feature plugin layer**: Slack/Discord/voice-call などの統合。
  コア capability を消費し、それをあるサーフェス上に提示します

たとえば、TTS は次の形に従います。

- コアは reply-time TTS policy、fallback order、prefs、および channel delivery を管理します
- `openai`, `elevenlabs`, `microsoft` は synthesis 実装を管理します
- `voice-call` は telephony TTS runtime helper を消費します

将来の capabilities に対しても、同じパターンを優先するべきです。

### マルチ capability の会社プラグイン例

会社プラグインは、外から見て一貫性があるべきです。OpenClaw が
models、speech、realtime transcription、realtime voice、media
understanding、image generation、video generation、web fetch、web search の共有
コントラクトを持っている場合、ベンダーは自分のサーフェスを 1 か所で管理できます。

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

重要なのは、正確な helper 名ではありません。重要なのは形です。

- 1 つのプラグインがベンダーサーフェスを管理する
- コアは引き続き capability コントラクトを管理する
- チャネルと機能プラグインは vendor code ではなく `api.runtime.*` helpers を消費する
- contract tests は、そのプラグインが管理すると主張する capabilities を
  実際に登録したことを検証できる

### Capability 例: 動画理解

OpenClaw はすでに image/audio/video understanding を 1 つの共有
capability として扱っています。同じ所有権モデルがここにも適用されます。

1. コアが media-understanding コントラクトを定義する
2. ベンダープラグインが、適用可能に応じて `describeImage`, `transcribeAudio`,
   `describeVideo` を登録する
3. チャネルと機能プラグインは、vendor code に直接配線するのではなく、
   共有コア動作を消費する

これにより、特定プロバイダーの video 前提をコアに焼き込むことを避けられます。プラグインが
ベンダーサーフェスを管理し、コアが capability コントラクトとフォールバック動作を管理します。

video generation もすでに同じ流れを使っています。コアが型付きの
capability コントラクトとランタイム helper を管理し、ベンダープラグインが
`api.registerVideoGenerationProvider(...)` 実装をそれに対して登録します。

具体的なロールアウトチェックリストが必要ですか。参照:
[Capability Cookbook](/ja-JP/plugins/architecture)。

## コントラクトと強制

プラグイン API サーフェスは、意図的に型付きであり、
`OpenClawPluginApi` に集約されています。このコントラクトが、サポートされる登録ポイントと、
プラグインが依存できるランタイムヘルパーを定義します。

これが重要な理由:

- プラグイン作者は 1 つの安定した内部標準を得られる
- コアは、同じ provider id を 2 つのプラグインが登録するような
  重複所有権を拒否できる
- 起動時に、誤った登録に対する実用的な診断を表示できる
- contract tests は、バンドル済みプラグインの所有権を強制し、
  暗黙のドリフトを防げる

強制には 2 つの層があります。

1. **ランタイム登録強制**
   プラグインレジストリは、プラグインのロード時に登録を検証します。例:
   重複した provider id、重複した speech provider id、誤った
   registration は、未定義動作ではなくプラグイン診断になります。
2. **contract tests**
   バンドル済みプラグインは、テスト実行時に contract registry に取り込まれるため、
   OpenClaw は所有権を明示的に検証できます。現在これは、model
   providers、speech providers、web search providers、およびバンドル済み registration
   ownership に対して使われています。

実際の効果として、OpenClaw は、どのプラグインがどのサーフェスを管理しているかを
前もって把握できます。これにより、所有権が暗黙ではなく宣言的、型付き、テスト可能になるため、
コアとチャネルをシームレスに構成できます。

### 何がコントラクトに属するか

良いプラグインコントラクトは次の性質を持ちます。

- 型付き
- 小さい
- capability 固有
- コアが所有
- 複数のプラグインで再利用可能
- ベンダー知識なしにチャネル/機能から消費可能

悪いプラグインコントラクトは次のようなものです。

- コアに隠されたベンダー固有ポリシー
- レジストリを迂回する単発のプラグイン escape hatch
- ベンダー実装に直接 reach するチャネルコード
- `OpenClawPluginApi` や
  `api.runtime` の一部ではない場当たり的な runtime object

迷ったら抽象度を上げてください。まず capability を定義し、それから
プラグインにそれへ接続させます。

## 実行モデル

ネイティブ OpenClaw プラグインは、Gateway と**同一プロセス内**で実行されます。サンドボックス化は
されません。ロード済みネイティブプラグインは、コアコードと同じプロセスレベルの
信頼境界を持ちます。

影響:

- ネイティブプラグインは tools、network handlers、hooks、services を登録できます
- ネイティブプラグインのバグは gateway をクラッシュまたは不安定化させる可能性があります
- 悪意あるネイティブプラグインは、OpenClaw プロセス内での任意コード実行と同等です

互換 bundle は、OpenClaw が現在それらを
metadata/content pack として扱うため、デフォルトではより安全です。現行リリースでは、これは主に
バンドル済み Skills を意味します。

非バンドルプラグインには allowlist と明示的な install/load path を使用してください。
workspace plugins は、本番デフォルトではなく開発時コードとして扱ってください。

バンドル済み workspace package 名では、plugin id を npm
名に固定してください。デフォルトでは `@openclaw/<id>`、または
パッケージが意図的により狭いプラグイン役割を公開する場合は、
`-provider`, `-plugin`, `-speech`, `-sandbox`, `-media-understanding` のような
承認済み型付きサフィックスを使用します。

重要な信頼メモ:

- `plugins.allow` は**plugin id** を信頼し、ソースの来歴は信頼しません。
- バンドル済みプラグインと同じ id を持つ workspace plugin は、
  その workspace plugin が有効化/allowlist された場合、意図的にバンドル版を上書きします。
- これは通常の挙動であり、ローカル開発、パッチテスト、ホットフィックスに有用です。

## Export 境界

OpenClaw が export するのは capabilities であり、実装 convenience ではありません。

capability 登録は公開のままにし、コントラクトではない helper export は削減してください。

- バンドル済みプラグイン固有の helper subpath
- 公開 API を意図していない runtime plumbing subpath
- ベンダー固有の convenience helpers
- 実装詳細である setup/onboarding helpers

いくつかのバンドル済みプラグイン helper subpath は、互換性と
バンドル済みプラグイン保守のため、生成された SDK export
map にまだ残っています。現在の例には
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup`, および複数の `plugin-sdk/matrix*` seam が含まれます。これらは
新しいサードパーティプラグイン向けの推奨 SDK パターンではなく、
予約済みの実装詳細 export として扱ってください。

## Load pipeline

起動時に、OpenClaw はおおむね次のことを行います。

1. 候補プラグインルートを検出する
2. ネイティブまたは互換 bundle の manifest と package metadata を読み取る
3. 安全でない候補を拒否する
4. plugin config（`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`）を正規化する
5. 各候補の有効化状態を決定する
6. 有効なネイティブモジュールを jiti でロードする
7. ネイティブの `register(api)`（または legacy alias の `activate(api)`）フックを呼び出し、登録内容を plugin registry に収集する
8. そのレジストリを commands/runtime surfaces に公開する

<Note>
`activate` は `register` の legacy alias です — ローダーは存在する方（`def.register ?? def.activate`）を解決し、同じタイミングで呼び出します。すべてのバンドル済みプラグインは `register` を使っています。新しいプラグインでは `register` を優先してください。
</Note>

安全ゲートは、ランタイム実行**前**に発生します。候補は、
entry が plugin root を逸脱する場合、path が world-writable の場合、
または非バンドルプラグインに対して path ownership が不審に見える場合にブロックされます。

### Manifest-first 動作

manifest は control-plane の正本です。OpenClaw はこれを使って次のことを行います。

- プラグインを識別する
- 宣言された channels/skills/config schema や bundle capabilities を検出する
- `plugins.entries.<id>.config` を検証する
- Control UI の labels/placeholders を補強する
- install/catalog metadata を表示する

ネイティブプラグインでは、ランタイムモジュールが data-plane 部分です。
hooks、tools、commands、provider flows のような実際の動作を登録します。

### ローダーがキャッシュするもの

OpenClaw は短命なプロセス内キャッシュを保持します。

- discovery results
- manifest registry data
- loaded plugin registries

これらのキャッシュは、起動時の突発的負荷や繰り返しの command overhead を減らします。これらは
永続化ではなく、短命なパフォーマンスキャッシュと考えて差し支えありません。

パフォーマンスメモ:

- `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` または
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` を設定すると、これらのキャッシュを無効化できます。
- キャッシュウィンドウは `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` と
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` で調整できます。

## Registry モデル

ロード済みプラグインは、ランダムなコアグローバルを直接変更しません。中央の
plugin registry に登録されます。

レジストリが追跡するもの:

- plugin records（identity, source, origin, status, diagnostics）
- tools
- legacy hooks と typed hooks
- channels
- providers
- Gateway RPC handlers
- HTTP routes
- CLI registrars
- background services
- plugin-owned commands

その後、コア機能はプラグインモジュールと直接会話するのではなく、このレジストリから読み取ります。
これによりロードは一方向に保たれます。

- plugin module -> registry registration
- core runtime -> registry consumption

この分離は保守性のために重要です。つまり、ほとんどのコアサーフェスは
「すべての plugin module を特別扱いする」必要はなく、
「registry を読む」という 1 つの統合点だけを必要とします。

## Conversation binding コールバック

conversation を bind するプラグインは、承認が解決されたときに反応できます。

承認または拒否の後にコールバックを受け取るには、
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

コールバック payload のフィールド:

- `status`: `"approved"` または `"denied"`
- `decision`: `"allow-once"`, `"allow-always"`, または `"deny"`
- `binding`: 承認されたリクエストに対する解決済み binding
- `request`: 元の request summary、detach hint、sender id、および
  conversation metadata

このコールバックは通知専用です。誰が conversation を bind できるかは変更せず、
コアの承認処理が完了した後に実行されます。

## プロバイダーのランタイムフック

現在、プロバイダープラグインには 2 つの層があります。

- manifest metadata: ランタイムロード前に安価な provider env-auth lookup を行う `providerAuthEnvVars`、
  ランタイムロード前に安価な channel env/setup lookup を行う `channelEnvVars`、
  さらにランタイムロード前に安価な onboarding/auth-choice
  label と CLI flag metadata を行う `providerAuthChoices`
- config-time hooks: `catalog` / legacy `discovery` と `applyConfigDefaults`
- runtime hooks: `normalizeModelId`, `normalizeTransport`,
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

OpenClaw は引き続き、汎用 agent loop、failover、transcript handling、および
tool policy を管理します。これらのフックは、provider 固有動作のための拡張サーフェスであり、
完全なカスタム inference transport を必要としません。

プロバイダーが env ベース資格情報を持ち、汎用 auth/status/model-picker 経路が
plugin runtime をロードせずにそれを認識すべき場合は、manifest の `providerAuthEnvVars` を使ってください。
オンボーディング/auth-choice CLI
サーフェスが、provider runtime をロードせずに provider の choice id、group labels、
単純な one-flag auth wiring を知る必要がある場合は、manifest の `providerAuthChoices` を使ってください。
provider runtime の `envVars` は、onboarding label や OAuth
client-id/client-secret setup vars のような operator 向けヒントに保持してください。

チャネルが env 駆動の auth または setup を持ち、汎用 shell-env fallback、
config/status checks、または setup prompts が channel runtime をロードせずにそれを認識すべき場合は、
manifest の `channelEnvVars` を使ってください。

### フック順序と使い分け

モデル/プロバイダープラグインについて、OpenClaw はおおむね次の順序でフックを呼び出します。
「When to use」列は、すばやい判断ガイドです。

| #   | フック                            | 役割                                                                                                           | 使用する場面                                                                                                                               |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | `catalog`                         | `models.json` 生成中に provider config を `models.providers` に公開する                                       | provider が catalog または base URL defaults を管理する場合                                                                                |
| 2   | `applyConfigDefaults`             | config materialization 中に provider 所有の global config defaults を適用する                                 | defaults が auth mode、env、または provider model-family semantics に依存する場合                                                          |
| --  | _(built-in model lookup)_         | OpenClaw がまず通常の registry/catalog 経路を試す                                                              | _(plugin hook ではない)_                                                                                                                    |
| 3   | `normalizeModelId`                | lookup 前に legacy または preview の model-id alias を正規化する                                               | provider が canonical な model resolution 前の alias cleanup を管理する場合                                                                |
| 4   | `normalizeTransport`              | 汎用 model assembly 前に provider-family の `api` / `baseUrl` を正規化する                                     | provider が、同じ transport family 内の custom provider id 向け transport cleanup を管理する場合                                          |
| 5   | `normalizeConfig`                 | runtime/provider resolution 前に `models.providers.<id>` を正規化する                                          | plugin 側に置くべき config cleanup が必要な場合。バンドルされた Google-family helpers は、対応する Google config entries の補完にもなる |
| 6   | `applyNativeStreamingUsageCompat` | config providers にネイティブな streaming-usage compat rewrites を適用する                                     | provider が endpoint 駆動の native streaming usage metadata 修正を必要とする場合                                                           |
| 7   | `resolveConfigApiKey`             | runtime auth loading 前に config providers 向け env-marker auth を解決する                                     | provider が env-marker API-key resolution を管理する場合。`amazon-bedrock` には組み込みの AWS env-marker resolver もある                |
| 8   | `resolveSyntheticAuth`            | 平文を永続化せずに local/self-hosted または config-backed auth を表面化する                                    | provider が synthetic/local credential marker で動作できる場合                                                                             |
| 9   | `resolveExternalAuthProfiles`     | provider 所有の external auth profiles を overlay する。CLI/app-owned creds の既定 `persistence` は `runtime-only` | copied refresh tokens を永続化せずに external auth credentials を再利用する場合                                                           |
| 10  | `shouldDeferSyntheticProfileAuth` | 保存済み synthetic profile placeholder を env/config-backed auth より後順位にする                              | provider が precedence を取るべきでない synthetic placeholder profiles を保存する場合                                                      |
| 11  | `resolveDynamicModel`             | まだローカル registry にない provider 所有 model id の同期 fallback                                            | provider が任意の upstream model ids を受け付ける場合                                                                                      |
| 12  | `prepareDynamicModel`             | 非同期 warm-up の後、`resolveDynamicModel` を再実行する                                                        | unknown ids を解決する前に network metadata が必要な場合                                                                                   |
| 13  | `normalizeResolvedModel`          | embedded runner が resolved model を使う前の最終リライト                                                       | provider が transport rewrites を必要とするが、引き続き core transport を使う場合                                                          |
| 14  | `contributeResolvedModelCompat`   | 別の互換 transport の背後にある vendor model 向け compat flags を提供する                                      | provider が provider を引き継がずに proxy transport 上で自分の model を認識する場合                                                       |
| 15  | `capabilities`                    | shared core logic が使用する provider 所有の transcript/tooling metadata                                       | provider が transcript/provider-family quirks を必要とする場合                                                                              |
| 16  | `normalizeToolSchemas`            | embedded runner が見る前に tool schemas を正規化する                                                           | provider が transport-family schema cleanup を必要とする場合                                                                                |
| 17  | `inspectToolSchemas`              | 正規化後に provider 所有の schema diagnostics を表面化する                                                     | core に provider-specific rules を教えずに keyword warnings を出したい場合                                                                 |
| 18  | `resolveReasoningOutputMode`      | native と tagged の reasoning-output contract を選択する                                                       | provider が native fields ではなく tagged reasoning/final output を必要とする場合                                                          |
| 19  | `prepareExtraParams`              | 汎用 stream option wrapper 前の request-param 正規化                                                           | provider が default request params または per-provider param cleanup を必要とする場合                                                      |
| 20  | `createStreamFn`                  | 通常の stream path を custom transport で完全に置き換える                                                      | wrapper ではなく custom wire protocol が必要な場合                                                                                         |
| 21  | `wrapStreamFn`                    | 汎用 wrapper 適用後の stream wrapper                                                                            | custom transport なしで request headers/body/model compat wrappers が必要な場合                                                            |
| 22  | `resolveTransportTurnState`       | ネイティブな per-turn transport headers または metadata を付加する                                              | provider が generic transports に provider-native turn identity を送らせたい場合                                                           |
| 23  | `resolveWebSocketSessionPolicy`   | ネイティブな WebSocket headers または session cool-down policy を付加する                                      | provider が generic WS transports で session headers または fallback policy を調整したい場合                                               |
| 24  | `formatApiKey`                    | auth-profile formatter: 保存済み profile を runtime `apiKey` string に変換する                                 | provider が追加 auth metadata を保存し、custom runtime token shape を必要とする場合                                                        |
| 25  | `refreshOAuth`                    | custom refresh endpoints または refresh-failure policy 向け OAuth refresh override                              | provider が共有 `pi-ai` refreshers に適合しない場合                                                                                        |
| 26  | `buildAuthDoctorHint`             | OAuth refresh failure 時に修復ヒントを追加する                                                                 | provider が refresh failure 後の provider-owned auth repair guidance を必要とする場合                                                       |
| 27  | `matchesContextOverflowError`     | provider 所有の context-window overflow matcher                                                                | provider に、汎用 heuristics が見逃す raw overflow errors がある場合                                                                        |
| 28  | `classifyFailoverReason`          | provider 所有の failover reason classification                                                                 | provider が raw API/transport errors を rate-limit/overload などにマップできる場合                                                         |
| 29  | `isCacheTtlEligible`              | proxy/backhaul providers 向け prompt-cache policy                                                               | provider が proxy-specific cache TTL gating を必要とする場合                                                                                |
| 30  | `buildMissingAuthMessage`         | 汎用 missing-auth recovery message の置き換え                                                                   | provider が provider-specific missing-auth recovery hint を必要とする場合                                                                   |
| 31  | `suppressBuiltInModel`            | stale upstream model の抑制と、任意の user-facing error hint                                                   | provider が stale upstream rows を隠すか、それを vendor hint に置き換えたい場合                                                            |
| 32  | `augmentModelCatalog`             | discovery 後に synthetic/final catalog rows を追加する                                                         | provider が `models list` や picker で synthetic forward-compat rows を必要とする場合                                                      |
| 33  | `isBinaryThinking`                | binary-thinking providers 向け on/off reasoning toggle                                                         | provider が binary thinking on/off しか公開しない場合                                                                                       |
| 34  | `supportsXHighThinking`           | 選択モデルに対する `xhigh` reasoning サポート                                                                   | provider が一部モデルにのみ `xhigh` を提供したい場合                                                                                       |
| 35  | `resolveDefaultThinkingLevel`     | 特定 model family 向けの既定 `/think` レベル                                                                   | provider が model family の既定 `/think` policy を管理する場合                                                                              |
| 36  | `isModernModelRef`                | live profile filters と smoke selection 向け modern-model matcher                                               | provider が live/smoke preferred-model matching を管理する場合                                                                              |
| 37  | `prepareRuntimeAuth`              | inference 直前に、設定済み credential を実際の runtime token/key に交換する                                    | provider が token exchange または短命 request credential を必要とする場合                                                                   |
| 38  | `resolveUsageAuth`                | `/usage` および関連 status surfaces 向け usage/billing credentials を解決する                                  | provider が custom usage/quota token parsing または別の usage credential を必要とする場合                                                  |
| 39  | `fetchUsageSnapshot`              | auth 解決後に provider-specific usage/quota snapshot を取得・正規化する                                         | provider が provider-specific usage endpoint または payload parser を必要とする場合                                                        |
| 40  | `createEmbeddingProvider`         | memory/search 向け provider-owned embedding adapter を構築する                                                  | memory embedding behavior が provider plugin に属する場合                                                                                   |
| 41  | `buildReplayPolicy`               | provider の transcript handling を制御する replay policy を返す                                                 | provider が custom transcript policy（例: thinking-block stripping）を必要とする場合                                                       |
| 42  | `sanitizeReplayHistory`           | 汎用 transcript cleanup 後に replay history を書き換える                                                       | provider が shared compaction helpers を超える provider-specific replay rewrites を必要とする場合                                          |
| 43  | `validateReplayTurns`             | embedded runner 前の最終 replay-turn validation または reshaping                                                | provider transport が汎用 sanitation 後により厳密な turn validation を必要とする場合                                                       |
| 44  | `onModelSelected`                 | provider 所有の model 選択後副作用を実行する                                                                   | provider が model 有効化時に telemetry または provider-owned state を必要とする場合                                                        |

`normalizeModelId`, `normalizeTransport`, `normalizeConfig` は、まず
一致した provider plugin を確認し、その後、model id または transport/config を
実際に変更するものが見つかるまで、他の hook-capable provider plugins にフォールスルーします。これにより、
caller がどの bundled plugin が rewrite を所有しているか知らなくても、
alias/compat provider shim が動作し続けます。どの provider hook も
サポート対象の Google-family config entry を書き換えない場合、バンドルされた
Google config normalizer が引き続きその互換 cleanup を適用します。

provider が完全に custom な wire protocol または custom request executor を必要とする場合、
それは別種の拡張です。これらのフックは、
OpenClaw の通常 inference loop 上で動作し続ける provider behavior のためのものです。

### プロバイダー例

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

### 組み込み例

- Anthropic は `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `wrapStreamFn` を使います。これは、Claude 4.6 の forward-compat、
  provider-family hints、auth repair guidance、usage endpoint integration、
  prompt-cache eligibility、auth-aware config defaults、Claude の
  default/adaptive thinking policy、および beta headers、`/fast` / `serviceTier`、
  `context1m` に対する Anthropic 固有の stream shaping を管理するためです。
- Anthropic の Claude 固有 stream helpers は、現時点ではバンドルされたプラグイン自身の
  公開 `api.ts` / `contract-api.ts` seam に残っています。その package surface は、
  generic SDK を 1 つの provider の beta-header rules に合わせて広げる代わりに、
  `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier`、および低レベルの
  Anthropic wrapper builders を export します。
- OpenAI は `resolveDynamicModel`, `normalizeResolvedModel`,
  `capabilities` に加えて `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking`, `isModernModelRef`
  を使います。これは、GPT-5.4 forward-compat、直接の OpenAI
  `openai-completions` -> `openai-responses` 正規化、Codex-aware auth
  hints、Spark suppression、synthetic OpenAI list rows、そして GPT-5 thinking /
  live-model policy を管理するためです。`openai-responses-defaults` stream family は、
  attribution headers、
  `/fast`/`serviceTier`、text verbosity、native Codex web search、
  reasoning-compat payload shaping、および Responses context management のための共有 native OpenAI Responses wrappers を管理します。
- OpenRouter は `catalog` に加えて `resolveDynamicModel` と
  `prepareDynamicModel` を使います。これは provider が pass-through であり、
  OpenClaw の static catalog 更新前に新しい model ids を公開する可能性があるためです。さらに
  `capabilities`, `wrapStreamFn`, `isCacheTtlEligible` も使い、
  provider-specific request headers、routing metadata、reasoning patches、および
  prompt-cache policy をコア外に保ちます。その replay policy は
  `passthrough-gemini` family から来ており、`openrouter-thinking` stream family が
  proxy reasoning injection と unsupported-model / `auto` skip を管理します。
- GitHub Copilot は `catalog`, `auth`, `resolveDynamicModel`,
  `capabilities` に加えて `prepareRuntimeAuth` と `fetchUsageSnapshot` を使います。これは、
  provider 所有の device login、model fallback behavior、Claude transcript
  quirks、GitHub token -> Copilot token exchange、および provider-owned usage
  endpoint を必要とするためです。
- OpenAI Codex は `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth`, `augmentModelCatalog` に加えて
  `prepareExtraParams`, `resolveUsageAuth`, `fetchUsageSnapshot` を使います。これは、
  引き続きコアの OpenAI transports 上で動作しながらも、その transport/base URL
  normalization、OAuth refresh fallback policy、default transport choice、
  synthetic Codex catalog rows、および ChatGPT usage endpoint integration を管理するためです。
  direct OpenAI と同じ `openai-responses-defaults` stream family を共有します。
- Google AI Studio と Gemini CLI OAuth は `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn`, `isModernModelRef` を使います。これは
  `google-gemini` replay family が Gemini 3.1 forward-compat fallback、
  native Gemini replay validation、bootstrap replay sanitation、tagged
  reasoning-output mode、および modern-model matching を管理し、
  `google-thinking` stream family が Gemini thinking payload normalization を
  管理するためです。Gemini CLI OAuth はさらに `formatApiKey`, `resolveUsageAuth`,
  `fetchUsageSnapshot` も使い、token formatting、token parsing、quota endpoint
  wiring を行います。
- Anthropic Vertex は
  `anthropic-by-model` replay family を通じて `buildReplayPolicy` を使い、
  Claude 固有 replay cleanup を、すべての `anthropic-messages` transport ではなく、
  Claude ids に限定します。
- Amazon Bedrock は `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `resolveDefaultThinkingLevel` を使います。これは、
  Anthropic-on-Bedrock traffic に対する Bedrock 固有の
  throttle/not-ready/context-overflow error classification を管理するためです。
  replay policy は引き続き同じ Claude-only `anthropic-by-model` guard を共有します。
- OpenRouter, Kilocode, Opencode, Opencode Go は `buildReplayPolicy`
  を `passthrough-gemini` replay family 経由で使います。これは、
  Gemini models を OpenAI-compatible transports 経由で proxy し、
  native Gemini replay validation や bootstrap rewrites なしで
  Gemini thought-signature sanitation を必要とするためです。
- MiniMax は `buildReplayPolicy` を
  `hybrid-anthropic-openai` replay family 経由で使います。これは、1 つの provider が
  Anthropic-message と OpenAI-compatible semantics の両方を管理するためです。
  Anthropic 側では Claude-only
  thinking-block dropping を維持しつつ、reasoning output mode を native に戻し、
  `minimax-fast-mode` stream family が共有 stream path 上の
  fast-mode model rewrites を管理します。
- Moonshot は `catalog` に加えて `wrapStreamFn` を使います。これは、引き続き共有の
  OpenAI transport を使いながらも、provider 所有の thinking payload normalization を必要とするためです。
  `moonshot-thinking` stream family は config と `/think` state を
  native binary thinking payload にマップします。
- Kilocode は `catalog`, `capabilities`, `wrapStreamFn`,
  `isCacheTtlEligible` を使います。これは、provider 所有の request headers、
  reasoning payload normalization、Gemini transcript hints、および Anthropic
  cache-TTL gating を必要とするためです。`kilocode-thinking` stream family は、
  explicit reasoning payload をサポートしない `kilo/auto` やその他の
  proxy model ids をスキップしつつ、共有 proxy stream path 上に Kilo thinking injection を保持します。
- Z.AI は `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth`, `fetchUsageSnapshot` を使います。これは GLM-5 fallback、
  `tool_stream` defaults、binary thinking UX、modern-model matching、および
  usage auth + quota fetching の両方を管理するためです。`tool-stream-default-on` stream family は、
  既定で有効な `tool_stream` wrapper を provider ごとの手書き glue から切り離します。
- xAI は `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel`, `isModernModelRef`
  を使います。これは native xAI Responses transport normalization、Grok fast-mode
  alias rewrites、default `tool_stream`、strict-tool / reasoning-payload
  cleanup、plugin-owned tools 向け fallback auth reuse、forward-compat Grok
  model resolution、および xAI tool-schema
  profile、unsupported schema keywords、native `web_search`、HTML-entity
  tool-call argument decoding のような provider-owned compat patches を管理するためです。
- Mistral, OpenCode Zen, OpenCode Go は、transcript/tooling quirks を
  コア外に保つため `capabilities` のみを使います。
- `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway`, `volcengine` のような
  catalog-only bundled providers は
  `catalog` のみを使います。
- Qwen は、text provider 向けに `catalog` を使い、その
  multimodal surfaces 向けに shared media-understanding と
  video-generation registrations を使います。
- MiniMax と Xiaomi は `catalog` に加えて usage hooks を使います。これは、
  inference は共有 transports を通る一方で、その `/usage`
  behavior が plugin-owned だからです。

## ランタイムヘルパー

プラグインは `api.runtime` を通じて選択されたコア helper にアクセスできます。TTS の例:

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

注:

- `textToSpeech` は、file/voice-note surfaces 向けの通常の core TTS output payload を返します。
- core の `messages.tts` configuration と provider selection を使用します。
- PCM audio buffer + sample rate を返します。プラグイン側で provider 向けに resample/encode する必要があります。
- `listVoices` は provider ごとに任意です。vendor-owned voice picker や setup flow に使用してください。
- voice listing には、provider-aware picker 向けに locale、gender、personality tags のような
  より豊富な metadata を含めることができます。
- telephony を現在サポートしているのは OpenAI と ElevenLabs です。Microsoft はサポートしていません。

プラグインは `api.registerSpeechProvider(...)` を通じて speech provider も登録できます。

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

注:

- TTS の policy、fallback、および reply delivery はコアに保持してください。
- ベンダー所有の synthesis behavior には speech providers を使用してください。
- 旧式の Microsoft `edge` input は `microsoft` provider id に正規化されます。
- 推奨される所有権モデルは company-oriented です。OpenClaw が
  それらの capability contract を追加するにつれて、1 つの vendor plugin が
  text、speech、image、および将来の media providers を管理できます。

画像/音声/動画理解については、プラグインは generic key/value bag ではなく、
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

注:

- orchestration、fallback、config、および channel wiring はコアに保持してください。
- vendor behavior は provider plugin に保持してください。
- 加法的拡張は型付きのままにしてください。新しい optional methods、
  新しい optional result fields、新しい optional capabilities。
- video generation もすでに同じパターンに従っています:
  - コアが capability contract と runtime helper を管理する
  - vendor plugins が `api.registerVideoGenerationProvider(...)` を登録する
  - feature/channel plugins が `api.runtime.videoGeneration.*` を消費する

media-understanding の runtime helpers として、プラグインは次を呼び出せます。

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

音声文字起こしについては、プラグインは media-understanding runtime
または古い STT alias を使えます。

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

注:

- `api.runtime.mediaUnderstanding.*` は、image/audio/video understanding 向けの
  推奨共有サーフェスです。
- core の media-understanding audio configuration（`tools.media.audio`）と provider fallback order を使います。
- 文字起こし結果が生成されない場合（例: skipped/unsupported input）には `{ text: undefined }` を返します。
- `api.runtime.stt.transcribeAudioFile(...)` は互換 alias として残っています。

プラグインは `api.runtime.subagent` を通じてバックグラウンド subagent 実行も開始できます。

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

注:

- `provider` と `model` は、永続セッション変更ではなく run ごとの任意 override です。
- OpenClaw は、信頼された caller に対してのみそれらの override fields を尊重します。
- plugin-owned fallback runs では、operators は `plugins.entries.<id>.subagent.allowModelOverride: true` で
  オプトインする必要があります。
- 信頼された plugins を特定の canonical `provider/model` target に制限するには
  `plugins.entries.<id>.subagent.allowedModels` を使ってください。明示的に任意ターゲットを許可するには `"*"` を使います。
- 信頼されていない plugin subagent runs も動作しますが、
  override request は暗黙に fallback されず拒否されます。

Web 検索については、プラグインは agent tool wiring に reach する代わりに、
共有 runtime helper を消費できます。

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

プラグインは
`api.registerWebSearchProvider(...)` で web-search providers も登録できます。

注:

- provider selection、credential resolution、および shared request semantics はコアに保持してください。
- vendor-specific search transports には web-search providers を使用してください。
- `api.runtime.webSearch.*` は、agent tool wrapper に依存せずに search behavior を必要とする
  feature/channel plugins 向けの推奨共有サーフェスです。

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

- `generate(...)`: 設定された image-generation provider chain を使って画像を生成します。
- `listProviders(...)`: 利用可能な image-generation providers とその capabilities を一覧表示します。

## Gateway HTTP routes

プラグインは `api.registerHttpRoute(...)` で HTTP endpoint を公開できます。

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

route フィールド:

- `path`: gateway HTTP server 配下の route path。
- `auth`: 必須。通常の gateway auth を要求するには `"gateway"`、
  plugin 管理 auth/webhook verification には `"plugin"` を使います。
- `match`: 任意。`"exact"`（既定）または `"prefix"`。
- `replaceExisting`: 任意。同じ plugin が自分の既存 route registration を置き換えることを許可します。
- `handler`: route が request を処理したら `true` を返します。

注:

- `api.registerHttpHandler(...)` は削除されており、plugin-load error の原因になります。代わりに `api.registerHttpRoute(...)` を使ってください。
- plugin routes は `auth` を明示的に宣言する必要があります。
- 完全一致の `path + match` 競合は、`replaceExisting: true` でない限り拒否され、ある plugin が別 plugin の route を置き換えることはできません。
- `auth` レベルが異なる重複 route は拒否されます。`exact`/`prefix` のフォールスルーチェーンは同じ auth レベル内に保ってください。
- `auth: "plugin"` routes は operator runtime scopes を自動では受け取りません。これらは
  plugin 管理 webhook/signature verification 用であり、特権的な Gateway helper calls 用ではありません。
- `auth: "gateway"` routes は Gateway request runtime scope 内で動作しますが、
  その scope は意図的に保守的です:
  - shared-secret bearer auth（`gateway.auth.mode = "token"` / `"password"`）では、
    caller が `x-openclaw-scopes` を送っても、plugin-route runtime scope は `operator.write` に固定されます
  - 信頼された identity-bearing HTTP modes（たとえば `trusted-proxy` や、private ingress 上の `gateway.auth.mode = "none"`）では、
    `x-openclaw-scopes` ヘッダーが明示的に存在する場合にのみそれを尊重します
  - そのような identity-bearing plugin-route requests で `x-openclaw-scopes` が存在しない場合、
    runtime scope は `operator.write` にフォールバックします
- 実務上のルール: gateway-auth plugin route を暗黙の admin サーフェスだと想定しないでください。route に admin-only behavior が必要なら、
  identity-bearing auth mode を要求し、明示的な `x-openclaw-scopes` header contract を文書化してください。

## Plugin SDK の import paths

プラグインを作成するときは、単一の `openclaw/plugin-sdk` import ではなく
SDK subpath を使用してください。

- プラグイン登録プリミティブには `openclaw/plugin-sdk/plugin-entry`。
- 汎用の共有 plugin-facing contract には `openclaw/plugin-sdk/core`。
- ルート `openclaw.json` Zod schema
  export（`OpenClawSchema`）には `openclaw/plugin-sdk/config-schema`。
- `openclaw/plugin-sdk/channel-setup` のような安定した channel primitives、
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input`, および
  `openclaw/plugin-sdk/webhook-ingress` は、共有 setup/auth/reply/webhook
  wiring のためのものです。`channel-inbound` は debounce、mention matching、
  envelope formatting、および inbound envelope context helpers の共有ホームです。
  `channel-setup` は狭い optional-install setup seam です。
  `setup-runtime` は `setupEntry` /
  deferred startup で使われる runtime-safe setup surface で、import-safe な setup patch adapters を含みます。
  `setup-adapter-runtime` は env-aware な account-setup adapter seam です。
  `setup-tools` は小さな CLI/archive/docs helper seam（`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`）です。
- `openclaw/plugin-sdk/channel-config-helpers` のような domain subpaths、
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store`, および
  `openclaw/plugin-sdk/directory-runtime` は、共有 runtime/config helpers 用です。
  `telegram-command-config` は Telegram custom
  command normalization/validation 向けの狭い公開 seam であり、バンドルされた
  Telegram contract surface が一時的に利用不能でも引き続き利用できます。
  `text-runtime` は assistant-visible-text stripping、
  markdown render/chunking helpers、redaction
  helpers、directive-tag helpers、および safe-text utilities を含む共有 text/markdown/logging seam です。
- Approval-specific channel seams では、plugin 上に 1 つの `approvalCapability`
  contract を優先してください。その後、コアは approval auth、delivery、render、および
  native-routing behavior を、その 1 つの capability を通じて読み取ります。
  unrelated plugin fields に approval behavior を混在させないでください。
- `openclaw/plugin-sdk/channel-runtime` は非推奨であり、旧プラグイン向けの
  compatibility shim としてのみ残っています。新しいコードでは、より狭い
  generic primitives を import してください。repo code でも shim への新規 import は追加しないでください。
- バンドル済み拡張の内部は private のままです。外部プラグインは
  `openclaw/plugin-sdk/*` subpath のみを使用するべきです。OpenClaw の core/test code は、
  `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js`, および `login-qr-api.js` のような狭いファイルなど、
  plugin package root 配下の repo public entry points を使用できます。
  コアや他の拡張から plugin package の `src/*` を import してはいけません。
- Repo entry point の分割:
  `<plugin-package-root>/api.js` は helper/types barrel、
  `<plugin-package-root>/runtime-api.js` は runtime-only barrel、
  `<plugin-package-root>/index.js` は bundled plugin entry、
  `<plugin-package-root>/setup-entry.js` は setup plugin entry です。
- 現在の bundled provider 例:
  - Anthropic は `api.js` / `contract-api.js` を使い、`wrapAnthropicProviderStream`、
    beta-header helpers、`service_tier`
    parsing などの Claude stream helpers を提供します。
  - OpenAI は `api.js` を使い、provider builders、default-model helpers、および
    realtime provider builders を提供します。
  - OpenRouter は `api.js` を provider builder と onboarding/config
    helpers に使用し、`register.runtime.js` では引き続き generic
    `plugin-sdk/provider-stream` helpers を repo-local use 向けに再 export できます。
- Facade-loaded public entry points は、存在する場合は active runtime config snapshot を優先し、
  OpenClaw がまだ runtime snapshot を提供していない場合は、ディスク上で解決された config file にフォールバックします。
- 汎用共有 primitives は、依然として推奨される public SDK contract です。
  バンドル済み channel-branded helper seams の小さな予約済み互換セットはまだ存在します。
  それらは bundled-maintenance/compatibility seams として扱ってください。
  新しい cross-channel contract は、引き続き generic `plugin-sdk/*` subpaths または
  plugin-local `api.js` / `runtime-api.js` barrels に配置するべきです。

互換性メモ:

- 新しいコードで root の `openclaw/plugin-sdk` barrel は避けてください。
- まず狭く安定した primitives を優先してください。新しい
  setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool subpaths は、
  新しい bundled/external plugin work 向けの意図された contract です。
  Target parsing/matching は `openclaw/plugin-sdk/channel-targets` に属します。
  Message action gates と reaction message-id helpers は
  `openclaw/plugin-sdk/channel-actions` に属します。
- バンドル済み拡張固有 helper barrels は、デフォルトでは安定していません。
  helper がバンドル済み拡張だけに必要な場合は、
  `openclaw/plugin-sdk/<extension>` に昇格させるのではなく、その拡張のローカル
  `api.js` または `runtime-api.js` seam の背後に置いてください。
- 新しい共有 helper seams は、channel-branded ではなく generic であるべきです。共有 target
  parsing は `openclaw/plugin-sdk/channel-targets` に属し、channel-specific
  internals は所有プラグインのローカル `api.js` または `runtime-api.js`
  seam の背後に留めてください。
- `image-generation`,
  `media-understanding`, `speech` のような capability-specific subpaths は、
  バンドル済み/ネイティブプラグインが現在それらを使っているため存在します。
  それが存在すること自体は、export されたすべての helper が
  長期的に固定された外部コントラクトであることを意味しません。

## Message tool schemas

プラグインは、チャネル固有の `describeMessageTool(...)` schema
contribution を所有するべきです。provider-specific fields は shared core ではなく
plugin 側に置いてください。

共有で持ち運び可能な schema fragments には、
`openclaw/plugin-sdk/channel-actions` を通じて export される generic helpers を再利用してください。

- button-grid style payloads には `createMessageToolButtonsSchema()`
- structured card payloads には `createMessageToolCardSchema()`

ある schema shape が 1 つの provider にしか意味を持たない場合は、
共有 SDK に昇格させるのではなく、その plugin 自身の source で定義してください。

## Channel target resolution

チャネルプラグインは、チャネル固有の target semantics を所有するべきです。共有
outbound host は generic のままにし、provider rules には messaging adapter surface を使用してください。

- `messaging.inferTargetChatType({ to })` は、正規化された target を
  directory lookup 前に `direct`, `group`, `channel` のどれとして扱うかを決定します。
- `messaging.targetResolver.looksLikeId(raw, normalized)` は、ある input が
  directory search ではなく id-like resolution に直接進むべきかどうかをコアに伝えます。
- `messaging.targetResolver.resolveTarget(...)` は、core が
  正規化後または directory miss 後に最終的な provider-owned resolution を必要とするときの
  plugin fallback です。
- `messaging.resolveOutboundSessionRoute(...)` は、target 解決後の
  provider-specific session route construction を所有します。

推奨される分担:

- peers/groups の検索前に行うべきカテゴリ判断には `inferTargetChatType` を使う
- 「これを明示的/ネイティブ target id として扱う」判定には `looksLikeId` を使う
- `resolveTarget` は broad directory search ではなく、
  provider-specific normalization fallback に使う
- chat ids、thread ids、JIDs、handles、room
  ids のような provider-native ids は、generic SDK fields ではなく `target` 値または provider-specific params に保持する

## Config-backed directories

config から directory entries を導出するプラグインは、そのロジックを plugin 内に保持し、
`openclaw/plugin-sdk/directory-runtime` の共有 helpers を再利用するべきです。

これは、チャネルが次のような config-backed peers/groups を必要とするときに使います。

- allowlist 駆動の DM peers
- 設定された channel/group maps
- account-scoped の static directory fallbacks

`directory-runtime` の共有 helpers は、汎用操作のみを扱います。

- query filtering
- limit application
- deduping/normalization helpers
- `ChannelDirectoryEntry[]` の構築

チャネル固有の account inspection と id normalization は、
plugin 実装側に残してください。

## プロバイダーカタログ

プロバイダープラグインは
`registerProvider({ catalog: { run(...) { ... } } })` を使って、inference 用の model catalogs を定義できます。

`catalog.run(...)` は、OpenClaw が `models.providers` に書き込むのと同じ形を返します。

- 1 つの provider entry には `{ provider }`
- 複数 provider entries には `{ providers }`

plugin が provider-specific model ids、base URL
defaults、または auth-gated model metadata を所有する場合は、`catalog` を使ってください。

`catalog.order` は、plugin の catalog が OpenClaw の
built-in implicit providers に対してどのタイミングでマージされるかを制御します。

- `simple`: plain API-key または env-driven providers
- `profile`: auth profiles が存在すると現れる providers
- `paired`: 複数の関連 provider entries を合成する providers
- `late`: 他の implicit providers の後の最終パス

後から来る provider が key collision で勝つため、
plugin は同じ provider id を持つ built-in provider entry を意図的に上書きできます。

互換性:

- `discovery` は引き続き legacy alias として動作します
- `catalog` と `discovery` の両方が登録されている場合、OpenClaw は `catalog` を使用します

## 読み取り専用のチャネル検査

plugin が channel を登録する場合、`resolveAccount(...)` とあわせて
`plugin.config.inspectAccount(cfg, accountId)` を実装することを推奨します。

理由:

- `resolveAccount(...)` は runtime path です。credentials が
  完全に materialize 済みである前提を置いてよく、必要な secret がない場合は即失敗して構いません。
- `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve`、および doctor/config
  repair flows のような読み取り専用コマンド経路では、
  構成内容を説明するためだけに runtime credentials を materialize する必要はありません。

推奨される `inspectAccount(...)` の振る舞い:

- 説明的な account state のみを返す
- `enabled` と `configured` を保持する
- relevant な場合は credential source/status fields を含める。たとえば:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- 読み取り専用の可用性を報告するためだけに raw token values を返す必要はありません。
  `tokenStatus: "available"`（および対応する source field）を返せば、status-style commands には十分です。
- credential が SecretRef 経由で設定されているが、
  現在の command path では利用不能な場合は `configured_unavailable` を使用する

これにより、読み取り専用コマンドは
「この command path では利用不能だが設定済み」と報告でき、
クラッシュしたり、account が未設定だと誤報告したりせずに済みます。

## Package packs

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

各 entry は 1 つのプラグインになります。pack が複数の extensions を列挙する場合、
plugin id は `name/<fileBase>` になります。

plugin が npm dependencies を import する場合は、そのディレクトリ内に
`node_modules` が利用可能になるようにインストールしてください（`npm install` / `pnpm install`）。

セキュリティガードレール: すべての `openclaw.extensions` entry は、symlink 解決後も
plugin directory 内に留まっている必要があります。package directory を逸脱する entries は
拒否されます。

セキュリティメモ: `openclaw plugins install` は、plugin dependencies を
`npm install --omit=dev --ignore-scripts` でインストールします
（lifecycle scripts なし、本番ランタイムに dev dependencies なし）。plugin dependency
tree は「pure JS/TS」に保ち、`postinstall` build を必要とする package は避けてください。

任意: `openclaw.setupEntry` は軽量な setup-only module を指せます。
OpenClaw が無効な channel plugin の setup surface を必要とする場合、または
channel plugin が有効でも未設定の場合、OpenClaw は完全な plugin entry の代わりに `setupEntry` をロードします。
これにより、メイン plugin entry が tools、hooks、またはその他の runtime-only
code も配線している場合に、startup と setup を軽く保てます。

任意: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
を使うと、channel plugin がすでに設定済みであっても、Gateway の
pre-listen startup phase 中に同じ `setupEntry` path へオプトインできます。

これを使うのは、`setupEntry` が、
Gateway が listen を開始する前に存在していなければならない startup surface を完全にカバーしている場合だけにしてください。
実際には、setup entry は、startup が依存するすべての channel-owned capability を登録している必要があります。たとえば:

- channel registration 自体
- Gateway が listen を開始する前に利用可能でなければならない HTTP routes
- 同じ時間帯に存在していなければならない gateway methods、tools、services

full entry が依然として必要な startup capability を所有している場合は、
このフラグを有効にしないでください。既定の挙動のままにし、
OpenClaw に startup 中に full entry をロードさせてください。

バンドル済み channels は、full channel runtime がロードされる前に
コアが参照できる setup-only contract-surface helpers も公開できます。現在の setup
promotion surface は次のとおりです。

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

コアは、full plugin entry をロードせずに、legacy single-account channel
config を `channels.<id>.accounts.*` に昇格させる必要があるとき、
このサーフェスを使います。Matrix が現在の bundled example です。named accounts がすでに存在する場合、
auth/bootstrap keys だけを named promoted account に移動し、
常に `accounts.default` を作成するのではなく、
設定済みの non-canonical default-account key を保持できます。

これらの setup patch adapters は、bundled contract-surface discovery を lazy に保ちます。
import 時間は軽いままで、promotion surface は module import 時に bundled channel startup に再入するのではなく、
最初の使用時にのみロードされます。

これらの startup surfaces に gateway RPC methods が含まれる場合は、
plugin-specific prefix に置いてください。コア admin namespaces（`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`）は予約済みであり、
plugin がより狭い scope を要求しても常に `operator.admin` に解決されます。

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

### チャネルカタログ metadata

チャネルプラグインは、`openclaw.channel` で setup/discovery metadata を、
`openclaw.install` で install hints を広告できます。これによりコアは catalog data-free に保たれます。

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

最小例以外で有用な `openclaw.channel` fields:

- `detailLabel`: より豊かな catalog/status surfaces 向けの secondary label
- `docsLabel`: docs link の link text を上書き
- `preferOver`: この catalog entry が優先的に上回るべき低優先度 plugin/channel ids
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: selection-surface copy controls
- `markdownCapable`: outbound formatting decisions 用に、その channel が markdown-capable であることを示す
- `exposure.configured`: `false` にすると configured-channel listing surfaces から channel を隠す
- `exposure.setup`: `false` にすると interactive setup/configure pickers から channel を隠す
- `exposure.docs`: docs navigation surfaces で channel を internal/private として扱う
- `showConfigured` / `showInSetup`: 互換性のため legacy aliases も引き続き受理されます。`exposure` を優先してください
- `quickstartAllowFrom`: channel を標準 quickstart `allowFrom` flow にオプトインさせる
- `forceAccountBinding`: account が 1 つしかなくても explicit account binding を要求する
- `preferSessionLookupForAnnounceTarget`: announce target 解決時に session lookup を優先する

OpenClaw は**外部チャネルカタログ**（例: MPM
registry export）もマージできます。JSON ファイルを次のいずれかに配置してください。

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

または `OPENCLAW_PLUGIN_CATALOG_PATHS`（または `OPENCLAW_MPM_CATALOG_PATHS`）で、
1 つ以上の JSON ファイルを指定してください
（カンマ/セミコロン/`PATH` 区切り）。各ファイルには
`{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`
を含めてください。パーサーは `"entries"` キーに対する legacy alias として
`"packages"` または `"plugins"` も受け付けます。

## Context engine plugins

Context engine plugins は、ingest、assembly、
compaction の session context orchestration を管理します。
plugin から `api.registerContextEngine(id, factory)` で登録し、
`plugins.slots.contextEngine` で active engine を選択します。

これは、plugin が default context
pipeline を置き換えたり拡張したりする必要があり、memory search や hooks を追加するだけではない場合に使います。

```ts
export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

engine が compaction algorithm を**所有しない**場合でも、
`compact()` は実装し、明示的に委譲してください。

```ts
import { delegateCompactionToRuntime } from "openclaw/plugin-sdk/core";

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
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## 新しい capability の追加

plugin が現在の API に適合しない動作を必要とする場合、
private reach-in によって plugin system を迂回しないでください。不足している capability を追加してください。

推奨される手順:

1. コアコントラクトを定義する
   コアが何を管理すべきかを決めます。policy、fallback、config merge、
   lifecycle、channel-facing semantics、および runtime helper shape。
2. 型付きの plugin registration/runtime surfaces を追加する
   `OpenClawPluginApi` および/または `api.runtime` を、
   最小限有用な型付き capability surface で拡張します。
3. コア + channel/feature consumers を配線する
   チャネルと機能プラグインは、新 capability を vendor implementation を直接 import するのではなく、
   コアを通じて消費するべきです。
4. vendor implementations を登録する
   その後、vendor plugins がその capability に対して backends を登録します。
5. contract coverage を追加する
   テストを追加して、ownership と registration shape が時間とともに明示的なまま保たれるようにします。

これが、OpenClaw が意見を持ちつつも、1 つの
provider の worldview にハードコードされない方法です。具体的なファイルチェックリストと worked example については、
[Capability Cookbook](/ja-JP/plugins/architecture) を参照してください。

### Capability チェックリスト

新しい capability を追加するとき、実装は通常、これらの
サーフェスをまとめて変更するべきです。

- `src/<capability>/types.ts` の core contract types
- `src/<capability>/runtime.ts` の core runner/runtime helper
- `src/plugins/types.ts` の plugin API registration surface
- `src/plugins/registry.ts` の plugin registry wiring
- feature/channel
  plugins がそれを消費する必要がある場合の `src/plugins/runtime/*` の plugin runtime exposure
- `src/test-utils/plugin-registration.ts` の capture/test helpers
- `src/plugins/contracts/registry.ts` の ownership/contract assertions
- `docs/` の operator/plugin docs

これらのサーフェスのいずれかが欠けている場合、通常は
その capability がまだ完全に統合されていない兆候です。

### Capability テンプレート

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

contract test パターン:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

これにより、ルールはシンプルになります。

- コアが capability contract + orchestration を管理する
- vendor plugins が vendor implementations を管理する
- feature/channel plugins が runtime helpers を消費する
- contract tests が ownership を明示的に保つ
