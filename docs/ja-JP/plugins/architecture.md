---
read_when:
    - ネイティブ OpenClaw プラグインを構築またはデバッグしている場合
    - プラグインの capability model や所有権の境界を理解したい場合
    - プラグインのロードパイプラインやレジストリに取り組んでいる場合
    - プロバイダーのランタイムフックやチャネルプラグインを実装している場合
sidebarTitle: Internals
summary: 'プラグイン内部: capability model、所有権、コントラクト、ロードパイプライン、ランタイムヘルパー'
title: プラグイン内部
x-i18n:
    generated_at: "2026-04-08T02:20:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: c40ecf14e2a0b2b8d332027aed939cd61fb4289a489f4cd4c076c96d707d1138
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
  - [SDK Overview](/ja-JP/plugins/sdk-overview) — import map と登録 API
</Info>

このページでは、OpenClaw プラグインシステムの内部アーキテクチャを扱います。

## public capability model

Capabilities は、OpenClaw 内部における公開された**ネイティブプラグイン**モデルです。すべての
ネイティブ OpenClaw プラグインは、1 つ以上の capability type に対して登録されます。

| Capability             | 登録メソッド                                     | プラグイン例                           |
| ---------------------- | ------------------------------------------------ | -------------------------------------- |
| テキスト推論           | `api.registerProvider(...)`                      | `openai`, `anthropic`                  |
| CLI 推論バックエンド   | `api.registerCliBackend(...)`                    | `openai`, `anthropic`                  |
| 音声                   | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`              |
| リアルタイム文字起こし | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                               |
| リアルタイム音声       | `api.registerRealtimeVoiceProvider(...)`         | `openai`                               |
| メディア理解           | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                     |
| 画像生成               | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax`   |
| 音楽生成               | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                    |
| 動画生成               | `api.registerVideoGenerationProvider(...)`       | `qwen`                                 |
| Web 取得               | `api.registerWebFetchProvider(...)`              | `firecrawl`                            |
| Web 検索               | `api.registerWebSearchProvider(...)`             | `google`                               |
| チャネル / メッセージング | `api.registerChannel(...)`                    | `msteams`, `matrix`                    |

capability を 1 つも登録せず、フック、ツール、サービスを提供する
プラグインは、**legacy hook-only** プラグインです。このパターンも引き続き完全にサポートされています。

### 外部互換性に関する方針

capability model はすでにコアに導入されており、現在はバンドル済み/ネイティブプラグインで
使われていますが、外部プラグインの互換性には、「export されているので固定されている」と言える以上の、より厳密な基準がまだ必要です。

現在のガイダンス:

- **既存の外部プラグイン:** フックベースの統合が動作し続けることを維持し、これを互換性の基準とみなす
- **新しいバンドル済み/ネイティブプラグイン:** ベンダー固有の直接参照や新しい hook-only 設計より、明示的な capability 登録を優先する
- **capability 登録を採用する外部プラグイン:** 許容されるが、ドキュメントでコントラクトが安定と明示されるまでは、capability 固有のヘルパーサーフェスは進化中とみなす

実践的なルール:

- capability 登録 API は意図された方向性です
- 移行期間中、legacy フックは外部プラグインにとって最も破壊的変更の少ない安全な経路です
- export された helper subpath はすべて同等ではありません。偶発的な helper export ではなく、狭く文書化されたコントラクトを優先してください

### プラグイン形状

OpenClaw は、読み込まれたすべてのプラグインを、静的メタデータだけではなく実際の登録動作に基づいて形状分類します。

- **plain-capability** -- ちょうど 1 種類の capability type を登録する（例: `mistral` のような provider-only プラグイン）
- **hybrid-capability** -- 複数の capability type を登録する（例:
  `openai` はテキスト推論、音声、メディア理解、画像生成を所有）
- **hook-only** -- フック（型付きまたはカスタム）のみを登録し、capabilities、
  tools、commands、services は登録しない
- **non-capability** -- tools、commands、services、routes は登録するが、
  capabilities は登録しない

`openclaw plugins inspect <id>` を使うと、プラグインの形状と capability の
内訳を確認できます。詳細は [CLI reference](/cli/plugins#inspect) を参照してください。

### legacy hooks

`before_agent_start` フックは、hook-only プラグイン向けの互換経路として引き続きサポートされます。現実の legacy プラグインは今でもこれに依存しています。

方向性:

- 動作し続けるよう維持する
- legacy として文書化する
- モデル/プロバイダー上書き作業には `before_model_resolve` を優先する
- プロンプト変更作業には `before_prompt_build` を優先する
- 実利用が減り、fixture coverage によって移行の安全性が証明されるまでは削除しない

### 互換性シグナル

`openclaw doctor` または `openclaw plugins inspect <id>` を実行すると、
以下のいずれかのラベルが表示されることがあります。

| シグナル                  | 意味                                                       |
| ------------------------- | ---------------------------------------------------------- |
| **config valid**          | 設定が正常に解析され、プラグインも解決される               |
| **compatibility advisory** | プラグインがサポート済みだが古いパターンを使っている（例: `hook-only`） |
| **legacy warning**        | プラグインが非推奨の `before_agent_start` を使っている     |
| **hard error**            | 設定が不正、またはプラグインの読み込みに失敗した           |

`hook-only` も `before_agent_start` も、現時点でプラグインを壊すことはありません --
`hook-only` は助言であり、`before_agent_start` は警告を出すだけです。これらの
シグナルは `openclaw status --all` と `openclaw plugins doctor` にも表示されます。

## アーキテクチャ概要

OpenClaw のプラグインシステムは 4 層あります。

1. **manifest + discovery**
   OpenClaw は、設定済みパス、workspace root、グローバル extension root、
   バンドル済み extension から候補プラグインを見つけます。discovery はまずネイティブな
   `openclaw.plugin.json` manifest と、サポートされる bundle manifest を読み取ります。
2. **enablement + validation**
   コアは、発見されたプラグインが有効、無効、ブロック済みか、あるいは memory のような排他的スロットに選択されるかを決定します。
3. **runtime loading**
   ネイティブ OpenClaw プラグインは jiti を通じてプロセス内で読み込まれ、
   capabilities を中央レジストリに登録します。互換 bundle はランタイムコードを import せずに
   レジストリレコードへ正規化されます。
4. **surface consumption**
   OpenClaw の残りの部分は、ツール、チャネル、プロバイダー設定、
   フック、HTTP routes、CLI commands、services を公開するためにレジストリを読み取ります。

特に plugin CLI では、ルートコマンドの discovery は 2 段階に分かれています。

- parse-time metadata は `registerCli(..., { descriptors: [...] })` から取得される
- 実際の plugin CLI module は lazy のままにでき、最初の呼び出し時に登録される

これにより、OpenClaw は解析前にルートコマンド名を予約しつつ、plugin 所有の CLI コードをプラグイン内部に保てます。

重要な設計境界:

- discovery + config validation は、プラグインコードを実行せずに
  **manifest/schema metadata** から動作すべき
- ネイティブのランタイム動作は、プラグインモジュールの `register(api)` 経路から来る

この分離により、OpenClaw は完全なランタイムがアクティブになる前に、設定を検証し、不足/無効なプラグインを説明し、UI/schema のヒントを構築できます。

### チャネルプラグインと共有 message tool

チャネルプラグインは、通常のチャット操作のために、別個の send/edit/react tool を登録する必要はありません。OpenClaw はコアに 1 つの共有 `message` tool を保持し、その背後のチャネル固有 discovery と実行をチャネルプラグインが所有します。

現在の境界は次のとおりです。

- コアは共有 `message` tool host、prompt wiring、session/thread
  bookkeeping、および execution dispatch を所有
- チャネルプラグインは scoped action discovery、capability discovery、
  およびチャネル固有の schema fragment を所有
- チャネルプラグインは、conversation id が thread id をどのようにエンコードするか、または親 conversation から継承するかといった、プロバイダー固有の session conversation grammar を所有
- チャネルプラグインは action adapter を通じて最終 action を実行する

チャネルプラグイン向けの SDK surface は
`ChannelMessageActionAdapter.describeMessageTool(...)` です。この統合された discovery 呼び出しにより、プラグインは可視 action、capabilities、schema への寄与をまとめて返せるため、これらが乖離しません。

コアは、その discovery ステップに runtime scope を渡します。重要なフィールドには以下が含まれます。

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- 信頼された受信 `requesterSenderId`

これはコンテキスト依存のプラグインにとって重要です。チャネルは、
アクティブな account、現在の room/thread/message、または信頼された requester identity に基づいて message action を隠したり公開したりできますが、コア `message` tool にチャネル固有の分岐をハードコードする必要はありません。

そのため、embedded-runner のルーティング変更は依然としてプラグイン作業です。runner は、共有 `message` tool が現在のターンに適したチャネル所有 surface を公開できるよう、現在の chat/session identity を plugin discovery 境界へ渡す責任があります。

チャネル所有の execution helper については、バンドル済みプラグインは execution
runtime を自分自身の extension module 内に保持すべきです。コアはもはや Discord、
Slack、Telegram、WhatsApp の message-action runtime を `src/agents/tools` 配下で所有しません。
`plugin-sdk/*-action-runtime` のような個別 subpath は公開しておらず、バンドル済み
プラグインは extension 所有 module から自分自身の local runtime code を直接 import すべきです。

この同じ境界は、一般的な provider 名付き SDK seam にも適用されます。コアは Slack、Discord、Signal、
WhatsApp、その他類似 extension 向けのチャネル固有 convenience barrel を import すべきではありません。コアがある動作を必要とする場合は、そのバンドル済みプラグイン自身の `api.ts` / `runtime-api.ts` barrel を使うか、その必要性を共有 SDK の狭い汎用 capability に昇格させるべきです。

特に poll には 2 つの実行経路があります。

- `outbound.sendPoll` は、共通の poll model に適合するチャネル向けの共有ベースライン
- `actions.handleAction("poll")` は、チャネル固有の poll semantics や追加 poll parameter に対する推奨経路

コアは現在、プラグインによる poll dispatch が action を拒否した後まで共有 poll parsing を延期するため、プラグイン所有の poll handler は汎用 poll parser に先にブロックされることなく、チャネル固有の poll field を受け入れられます。

完全な起動シーケンスについては [Load pipeline](#load-pipeline) を参照してください。

## capability ownership model

OpenClaw は、ネイティブプラグインを、無関係な統合の寄せ集めではなく、**会社**または
**機能**の所有境界として扱います。

つまり:

- 会社プラグインは通常、その会社の OpenClaw 向け surface 全体を所有すべき
- 機能プラグインは通常、それが導入する機能 surface 全体を所有すべき
- チャネルは、プロバイダー動作を場当たり的に再実装するのではなく、共有コア capability を利用すべき

例:

- バンドル済み `openai` プラグインは OpenAI モデルプロバイダー動作と、OpenAI の
  speech + realtime-voice + media-understanding + image-generation 動作を所有
- バンドル済み `elevenlabs` プラグインは ElevenLabs の音声動作を所有
- バンドル済み `microsoft` プラグインは Microsoft の音声動作を所有
- バンドル済み `google` プラグインは Google モデルプロバイダー動作に加え、Google の
  media-understanding + image-generation + web-search 動作を所有
- バンドル済み `firecrawl` プラグインは Firecrawl の web-fetch 動作を所有
- バンドル済み `minimax`, `mistral`, `moonshot`, `zai` プラグインは、それぞれの
  media-understanding backend を所有
- バンドル済み `qwen` プラグインは Qwen のテキストプロバイダー動作に加え、
  media-understanding と video-generation 動作を所有
- `voice-call` プラグインは機能プラグインです。call transport、tools、
  CLI、routes、Twilio media-stream bridging を所有しますが、ベンダープラグインを直接 import する代わりに、共有の speech +
  realtime-transcription および realtime-voice capability を利用します

意図された最終状態:

- OpenAI は、テキストモデル、音声、画像、将来の動画にまたがっていても 1 つのプラグインに存在する
- 別のベンダーも、自身の surface area に対して同じことができる
- チャネルはどのベンダープラグインがプロバイダーを所有しているかを気にせず、コアが公開する共有 capability contract を利用する

これが重要な違いです。

- **plugin** = 所有境界
- **capability** = 複数のプラグインが実装または利用できるコア contract

したがって、OpenClaw が動画のような新しいドメインを追加する場合、最初の問いは
「どのプロバイダーが動画処理をハードコードすべきか」ではありません。最初の問いは
「コア動画 capability contract は何か」です。その contract が存在すれば、ベンダープラグインはそれに登録でき、チャネル/機能プラグインはそれを利用できます。

capability がまだ存在しない場合、通常は次のように進めるのが正しいです。

1. コアで欠けている capability を定義する
2. それを型付きで plugin API/runtime 経由に公開する
3. チャネル/機能をその capability に対して配線する
4. ベンダープラグインに実装を登録させる

これにより、コアの動作が単一ベンダーや一回限りの plugin 固有コードパスに依存することを避けつつ、所有権を明確に保てます。

### capability layering

コードの置き場所を決めるときは、次のメンタルモデルを使ってください。

- **core capability layer**: 共有 orchestration、policy、fallback、config
  merge rules、delivery semantics、型付き contract
- **vendor plugin layer**: ベンダー固有 API、auth、model catalog、speech
  synthesis、image generation、将来の video backend、usage endpoint
- **channel/feature plugin layer**: Slack/Discord/voice-call などの統合。
  コア capability を利用して surface 上に提供する

たとえば TTS は次の形に従います。

- コアは reply-time TTS policy、fallback order、prefs、channel delivery を所有
- `openai`, `elevenlabs`, `microsoft` は synthesis 実装を所有
- `voice-call` は telephony TTS runtime helper を利用

将来の capability についても、同じパターンを優先すべきです。

### multi-capability company plugin の例

会社プラグインは、外から見て一貫性があるべきです。OpenClaw に models、speech、realtime transcription、realtime voice、media
understanding、image generation、video generation、web fetch、web search 向けの共有 contract があるなら、
ベンダーはそのすべての surface を 1 か所で所有できます。

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

重要なのは正確な helper 名ではありません。形が重要です。

- 1 つのプラグインがベンダー surface を所有する
- コアは引き続き capability contract を所有する
- チャネルと機能プラグインはベンダーコードではなく `api.runtime.*` helper を利用する
- contract test で、そのプラグインが所有すると主張する capability を登録していることを検証できる

### capability の例: video understanding

OpenClaw はすでに image/audio/video understanding を 1 つの共有
capability として扱っています。そこにも同じ ownership model が適用されます。

1. コアが media-understanding contract を定義する
2. ベンダープラグインが、該当するものとして `describeImage`, `transcribeAudio`,
   `describeVideo` を登録する
3. チャネルと機能プラグインは、ベンダーコードへ直接配線するのではなく、共有コア動作を利用する

これにより、ある 1 つのプロバイダーの動画前提をコアに焼き込むことを避けられます。プラグインがベンダー surface を所有し、コアが capability contract と fallback behavior を所有します。

動画生成もすでに同じ流れに従っています。コアが型付き capability contract と runtime helper を所有し、ベンダープラグインが
`api.registerVideoGenerationProvider(...)` 実装をそれに登録します。

具体的なロールアウトチェックリストが必要ですか。参照:
[Capability Cookbook](/ja-JP/plugins/architecture)。

## コントラクトと強制

plugin API surface は、意図的に型付けされており、
`OpenClawPluginApi` に集約されています。この contract は、サポートされる登録ポイントと、プラグインが依存できる runtime helper を定義します。

これが重要な理由:

- プラグイン作者は、1 つの安定した内部標準を得られる
- コアは、2 つのプラグインが同じ provider id を登録するような重複所有を拒否できる
- 起動時に、不正な登録に対する実用的な診断を表示できる
- contract test で、バンドル済みプラグインの所有権を強制し、静かなドリフトを防げる

強制には 2 つの層があります。

1. **runtime registration enforcement**
   プラグイン読み込み時に、plugin registry が登録内容を検証します。例:
   duplicate provider id、duplicate speech provider id、不正な
   registration は未定義動作ではなく plugin diagnostics を生成します。
2. **contract tests**
   テスト実行中にバンドル済みプラグインを contract registry に記録することで、
   OpenClaw は所有権を明示的に検証できます。現在は model
   providers、speech providers、web search providers、および bundled registration
   ownership に使われています。

実際の効果として、OpenClaw はどのプラグインがどの surface を所有しているかを事前に把握できます。これにより所有権が暗黙ではなく、宣言され、型付けされ、テスト可能になるため、コアとチャネルは自然に組み合わさります。

### コントラクトに含めるべきもの

良い plugin contract は次のようなものです。

- 型付き
- 小さい
- capability 固有
- コア所有
- 複数プラグインで再利用可能
- ベンダー知識なしでチャネル/機能から利用可能

悪い plugin contract は次のようなものです。

- コアに隠されたベンダー固有 policy
- レジストリを回避する一回限りの plugin escape hatch
- ベンダー実装へ直接到達するチャネルコード
- `OpenClawPluginApi` や `api.runtime` の一部ではない、場当たり的な runtime object

迷ったら抽象化レベルを上げてください。まず capability を定義し、その後でプラグインにそれを差し込ませます。

## 実行モデル

ネイティブ OpenClaw プラグインは、Gateway と**同一プロセス内**で動作します。
sandbox 化されていません。読み込まれたネイティブプラグインは、コアコードと同じプロセスレベルの trust boundary を持ちます。

影響:

- ネイティブプラグインは tools、network handlers、hooks、services を登録できる
- ネイティブプラグインのバグは gateway をクラッシュまたは不安定化させうる
- 悪意あるネイティブプラグインは、OpenClaw プロセス内での任意コード実行と等価

互換 bundle は、OpenClaw が現在それらを metadata/content pack として扱うため、デフォルトではより安全です。現在のリリースでは、これは主に bundled
skills を意味します。

バンドルされていないプラグインには allowlist と明示的な install/load path を使ってください。workspace plugin は production のデフォルトではなく、開発時コードとして扱ってください。

バンドル済み workspace package 名では、plugin id を npm
name に固定してください。デフォルトは `@openclaw/<id>`、または
より狭い plugin role を意図的に公開する場合は、承認された型付き suffix（
`-provider`, `-plugin`, `-speech`, `-sandbox`, `-media-understanding`）を使います。

重要な trust に関する注意:

- `plugins.allow` が信頼するのは**plugin id**であり、ソースの由来ではありません。
- バンドル済みプラグインと同じ id を持つ workspace plugin は、その workspace plugin が有効化/allowlist されている場合、意図的にバンドル済みコピーを上書きします。
- これは正常であり、ローカル開発、patch テスト、hotfix に有用です。

## export 境界

OpenClaw が export するのは capability であり、実装 convenience ではありません。

capability registration は public のままにし、コントラクトではない helper export は削減してください。

- bundled-plugin 固有の helper subpath
- public API を意図しない runtime plumbing subpath
- ベンダー固有 convenience helper
- 実装詳細である setup/onboarding helper

一部の bundled-plugin helper subpath は、互換性と bundled-plugin
保守のために、生成された SDK export map にまだ残っています。現在の例には
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup`、および複数の `plugin-sdk/matrix*` seam が含まれます。これらは、新しいサードパーティープラグイン向けの推奨 SDK パターンではなく、予約された実装詳細 export として扱ってください。

## Load pipeline

起動時、OpenClaw はおおむね次のことを行います。

1. 候補 plugin root を発見する
2. ネイティブまたは互換 bundle manifest と package metadata を読み取る
3. 安全でない候補を拒否する
4. plugin config（`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`）を正規化する
5. 各候補の enablement を決定する
6. 有効なネイティブ module を jiti で読み込む
7. ネイティブの `register(api)`（または legacy alias の `activate(api)`）フックを呼び出し、plugin registry に登録を収集する
8. その registry を commands/runtime surface に公開する

<Note>
`activate` は `register` の legacy alias です — loader は存在する方（`def.register ?? def.activate`）を解決し、同じタイミングで呼び出します。すべてのバンドル済みプラグインは `register` を使っています。新しいプラグインでは `register` を優先してください。
</Note>

安全性ゲートは、runtime 実行の**前に**発生します。entry が plugin root から外へ出る場合、path が world-writable な場合、またはバンドルされていない plugin に対して path ownership が疑わしい場合、候補はブロックされます。

### manifest-first の動作

manifest は control-plane の source of truth です。OpenClaw はこれを使って次を行います。

- プラグインを識別する
- 宣言された channels/skills/config schema または bundle capability を発見する
- `plugins.entries.<id>.config` を検証する
- Control UI の labels/placeholders を拡張する
- install/catalog metadata を表示する

ネイティブプラグインでは、runtime module は data-plane 部分です。フック、ツール、コマンド、プロバイダーフローなどの実際の動作を登録します。

### loader がキャッシュするもの

OpenClaw は短命なインプロセスキャッシュを次に対して保持します。

- discovery 結果
- manifest registry data
- 読み込まれた plugin registry

これらのキャッシュは、突発的な起動コストと繰り返しコマンドのオーバーヘッドを減らします。これらは永続化ではなく、短命な performance cache と考えて問題ありません。

パフォーマンスに関する注記:

- `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` または
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` を設定すると、これらのキャッシュを無効化できます。
- キャッシュ時間は `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` と
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` で調整します。

## registry model

読み込まれたプラグインは、ランダムなコア global を直接変更しません。中央の
plugin registry に登録します。

registry が追跡するもの:

- plugin records（identity, source, origin, status, diagnostics）
- tools
- legacy hooks と typed hooks
- channels
- providers
- gateway RPC handlers
- HTTP routes
- CLI registrars
- background services
- plugin 所有 commands

その後、コア機能は plugin module と直接やり取りするのではなく、その registry を読み取ります。これにより loading は一方向に保たれます。

- plugin module -> registry registration
- core runtime -> registry consumption

この分離は保守性にとって重要です。つまり、多くのコア surface は
「registry を読む」という 1 つの統合ポイントだけを必要とし、
「すべての plugin module を個別特別扱いする」必要がありません。

## conversation binding callbacks

conversation を bind するプラグインは、承認が解決されたときに反応できます。

bind request が承認または拒否された後にコールバックを受け取るには、
`api.onConversationBindingResolved(...)` を使います。

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // この plugin + conversation に対する binding が存在するようになった。
        console.log(event.binding?.conversationId);
        return;
      }

      // リクエストは拒否された。ローカルの pending state をクリアする。
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

コールバック payload のフィールド:

- `status`: `"approved"` または `"denied"`
- `decision`: `"allow-once"`, `"allow-always"`, または `"deny"`
- `binding`: 承認された request に対する解決済み binding
- `request`: 元の request summary、detach hint、sender id、および
  conversation metadata

このコールバックは通知専用です。誰が conversation を bind できるかを変更するものではなく、コアの承認処理が完了した後に実行されます。

## プロバイダーランタイムフック

プロバイダープラグインには現在 2 つの層があります。

- manifest metadata: runtime load 前に安価な provider env-auth lookup を行う
  `providerAuthEnvVars`、runtime load 前に安価な channel env/setup lookup を行う `channelEnvVars`、
  および runtime load 前に安価な onboarding/auth-choice label と CLI flag metadata を提供する `providerAuthChoices`
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

OpenClaw は引き続き、汎用 agent loop、failover、transcript handling、tool policy を所有します。これらのフックは、完全にカスタムな inference transport を必要とせずに、プロバイダー固有動作を拡張するためのサーフェスです。

プロバイダーに env ベースの credential があり、plugin runtime を読み込まずに汎用の auth/status/model-picker 経路から見える必要がある場合は、manifest の `providerAuthEnvVars` を使ってください。onboarding/auth-choice CLI
surface が、provider runtime を読み込まずに provider の choice id、group label、単純な one-flag auth wiring を知る必要がある場合は、manifest の `providerAuthChoices` を使ってください。provider runtime の `envVars` は、onboarding label や OAuth
client-id/client-secret setup vars など、operator 向けヒントに保持してください。

チャネルに env 駆動の auth または setup があり、チャネル runtime を読み込まずに汎用 shell-env fallback、config/status check、setup prompt から見える必要がある場合は、manifest の `channelEnvVars` を使ってください。

### フック順序と使い方

モデル/プロバイダープラグインについて、OpenClaw はおおむね次の順序でフックを呼び出します。
「When to use」列は、素早く判断するためのガイドです。

| #   | フック                            | 役割                                                                                                           | 使うべき場面                                                                                                                                |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | `models.json` 生成中に provider config を `models.providers` に公開する                                      | プロバイダーが catalog または base URL defaults を所有している                                                                              |
| 2   | `applyConfigDefaults`             | config materialization 中に provider 所有の global config defaults を適用する                                 | defaults が auth mode、env、または provider の model-family semantics に依存する                                                            |
| --  | _(built-in model lookup)_         | OpenClaw は最初に通常の registry/catalog path を試す                                                          | _(plugin hook ではない)_                                                                                                                    |
| 3   | `normalizeModelId`                | lookup 前に legacy または preview model-id alias を正規化する                                                | プロバイダーが canonical model resolution 前の alias cleanup を所有している                                                                  |
| 4   | `normalizeTransport`              | 汎用モデル組み立て前に provider-family の `api` / `baseUrl` を正規化する                                      | 同じ transport family の custom provider id に対する transport cleanup をプロバイダーが所有している                                        |
| 5   | `normalizeConfig`                 | runtime/provider resolution 前に `models.providers.<id>` を正規化する                                         | plugin に属すべき config cleanup が必要。bundled Google-family helper は、対応する Google config entry の後方互換 cleanup も補完する      |
| 6   | `applyNativeStreamingUsageCompat` | config provider に native streaming-usage compat rewrite を適用する                                           | endpoint 駆動の native streaming usage metadata 修正が必要                                                                                  |
| 7   | `resolveConfigApiKey`             | runtime auth load 前に config provider の env-marker auth を解決する                                          | provider 所有の env-marker API key 解決が必要。`amazon-bedrock` には組み込み AWS env-marker resolver もここにある                         |
| 8   | `resolveSyntheticAuth`            | 平文を永続化せずに local/self-hosted または config-backed auth を表面化する                                  | synthetic/local credential marker で動作できる                                                                                              |
| 9   | `resolveExternalAuthProfiles`     | provider 所有の external auth profile を上書きする。CLI/app 所有 credential のデフォルト `persistence` は `runtime-only` | copied refresh token を永続化せず、external auth credential を再利用したい                                                                  |
| 10  | `shouldDeferSyntheticProfileAuth` | 保存済み synthetic profile placeholder を env/config-backed auth より低くする                                | 優先されるべきでない synthetic placeholder profile を保存する                                                                                |
| 11  | `resolveDynamicModel`             | まだ local registry にない provider 所有 model id の同期 fallback                                             | 任意の upstream model id を受け入れる                                                                                                       |
| 12  | `prepareDynamicModel`             | 非同期 warm-up を行い、その後 `resolveDynamicModel` を再実行する                                              | 未知 id の解決前に network metadata が必要                                                                                                  |
| 13  | `normalizeResolvedModel`          | embedded runner が resolved model を使う前の最終書き換え                                                      | core transport を使いつつ transport rewrite が必要                                                                                          |
| 14  | `contributeResolvedModelCompat`   | 別の互換 transport 背後にある vendor model の compat flag を提供する                                          | プロバイダー自体を乗っ取らずに、proxy transport 上で自社 model を認識したい                                                                 |
| 15  | `capabilities`                    | 共有 core logic が使う、provider 所有の transcript/tooling metadata                                           | transcript/provider-family の癖が必要                                                                                                       |
| 16  | `normalizeToolSchemas`            | embedded runner が見る前に tool schema を正規化する                                                           | transport-family の schema cleanup が必要                                                                                                   |
| 17  | `inspectToolSchemas`              | 正規化後に provider 所有の schema diagnostic を表示する                                                       | core に provider 固有ルールを教えず、keyword warning を出したい                                                                             |
| 18  | `resolveReasoningOutputMode`      | native と tagged の reasoning-output contract を選択する                                                      | native field ではなく tagged reasoning/final output が必要                                                                                  |
| 19  | `prepareExtraParams`              | 汎用 stream option wrapper 前に request param を正規化する                                                    | default request param または provider ごとの param cleanup が必要                                                                           |
| 20  | `createStreamFn`                  | 通常の stream path を完全に custom transport に置き換える                                                     | wrapper ではなく custom wire protocol が必要                                                                                                |
| 21  | `wrapStreamFn`                    | 汎用 wrapper 適用後に stream wrapper を適用する                                                               | custom transport なしで request header/body/model compat wrapper が必要                                                                     |
| 22  | `resolveTransportTurnState`       | native のターン単位 transport header または metadata を付加する                                               | 汎用 transport に provider-native の turn identity を送らせたい                                                                             |
| 23  | `resolveWebSocketSessionPolicy`   | native WebSocket header または session cool-down policy を付加する                                            | 汎用 WS transport で session header または fallback policy を調整したい                                                                     |
| 24  | `formatApiKey`                    | auth-profile formatter: 保存済み profile を runtime `apiKey` 文字列に変換                                     | 追加 auth metadata を保存し、custom runtime token shape が必要                                                                              |
| 25  | `refreshOAuth`                    | custom refresh endpoint または refresh-failure policy のための OAuth refresh override                         | 共有 `pi-ai` refresher では対応できない                                                                                                     |
| 26  | `buildAuthDoctorHint`             | OAuth refresh 失敗時に修復ヒントを追加する                                                                    | provider 所有の auth repair guidance が必要                                                                                                 |
| 27  | `matchesContextOverflowError`     | provider 所有の context-window overflow matcher                                                               | 汎用 heuristic が見逃す raw overflow error がある                                                                                            |
| 28  | `classifyFailoverReason`          | provider 所有の failover reason classification                                                                | raw API/transport error を rate-limit/overload などにマッピングできる                                                                       |
| 29  | `isCacheTtlEligible`              | proxy/backhaul provider 向けの prompt-cache policy                                                            | proxy 固有の cache TTL gating が必要                                                                                                        |
| 30  | `buildMissingAuthMessage`         | 汎用 missing-auth recovery message の置き換え                                                                 | provider 固有の missing-auth recovery hint が必要                                                                                           |
| 31  | `suppressBuiltInModel`            | stale upstream model の抑制と、オプションの user-facing error hint                                            | stale upstream row を隠す、または vendor hint で置き換えたい                                                                                |
| 32  | `augmentModelCatalog`             | discovery 後に synthetic/final catalog row を追加する                                                        | `models list` や picker に synthetic な forward-compat row が必要                                                                           |
| 33  | `isBinaryThinking`                | binary-thinking provider 向けの on/off reasoning toggle                                                      | binary な thinking on/off のみを公開する                                                                                                    |
| 34  | `supportsXHighThinking`           | 選択モデルに対する `xhigh` reasoning support                                                                  | 一部の model にのみ `xhigh` を提供したい                                                                                                    |
| 35  | `resolveDefaultThinkingLevel`     | 特定 model family のデフォルト `/think` level                                                                 | model family のデフォルト `/think` policy を所有している                                                                                    |
| 36  | `isModernModelRef`                | live profile filter と smoke selection 向け modern-model matcher                                             | live/smoke の preferred-model matching を所有している                                                                                       |
| 37  | `prepareRuntimeAuth`              | inference 直前に設定済み credential を実際の runtime token/key に交換する                                    | token exchange または短命な request credential が必要                                                                                       |
| 38  | `resolveUsageAuth`                | `/usage` と関連 status surface 向けに usage/billing credential を解決する                                     | custom usage/quota token parsing または別の usage credential が必要                                                                         |
| 39  | `fetchUsageSnapshot`              | auth 解決後に provider 固有の usage/quota snapshot を取得・正規化する                                         | provider 固有の usage endpoint または payload parser が必要                                                                                 |
| 40  | `createEmbeddingProvider`         | memory/search 向けの provider 所有 embedding adapter を構築する                                              | memory embedding behavior が provider plugin 側に属する                                                                                     |
| 41  | `buildReplayPolicy`               | provider の transcript handling を制御する replay policy を返す                                               | custom transcript policy（例: thinking-block stripping）が必要                                                                              |
| 42  | `sanitizeReplayHistory`           | 汎用 transcript cleanup 後に replay history を書き換える                                                     | 共有 compaction helper を超える provider 固有 replay rewrite が必要                                                                         |
| 43  | `validateReplayTurns`             | embedded runner 前の最終 replay-turn validation または再整形                                                | 汎用 sanitize 後により厳格な turn validation が必要                                                                                         |
| 44  | `onModelSelected`                 | provider 所有の選択後副作用を実行する                                                                        | model が有効になったときに telemetry または provider 所有 state が必要                                                                     |

`normalizeModelId`, `normalizeTransport`, `normalizeConfig` は最初に
一致した provider plugin を確認し、その後、model id または transport/config を実際に変更するものが現れるまで、他の hook 対応 provider plugin にフォールスルーします。これにより、caller がどの bundled plugin が rewrite を所有しているかを知らなくても、alias/compat provider shim が動作します。どの provider hook も対応する
Google-family config entry を書き換えない場合、bundled Google config normalizer がその互換 cleanup を適用します。

プロバイダーに完全な custom wire protocol または custom request executor が必要な場合、それは別種の extension です。これらのフックは、OpenClaw の通常の inference loop 上で動作する provider behavior 向けです。

### Provider の例

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

- Anthropic は `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `wrapStreamFn` を使います。これは Claude 4.6 の forward-compat、
  provider-family hint、auth repair guidance、usage endpoint integration、
  prompt-cache eligibility、auth-aware config defaults、Claude の
  default/adaptive thinking policy、および beta
  header、`/fast` / `serviceTier`、`context1m` 向けの Anthropic 固有 stream shaping を所有しているためです。
- Anthropic の Claude 固有 stream helper は、今のところ bundled plugin 自身の
  public `api.ts` / `contract-api.ts` seam に残されています。その package surface は、
  generic SDK を 1 つの provider の beta-header rule のために広げるのではなく、
  `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier`、および下位の
  Anthropic wrapper builder を export します。
- OpenAI は `resolveDynamicModel`, `normalizeResolvedModel`,
  `capabilities` に加え、`buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking`, `isModernModelRef`
  を使います。これは GPT-5.4 の forward-compat、直接 OpenAI の
  `openai-completions` -> `openai-responses` 正規化、Codex-aware auth
  hint、Spark suppression、synthetic OpenAI list row、GPT-5 thinking /
  live-model policy を所有しているためです。`openai-responses-defaults` stream family は、帰属 header、
  `/fast`/`serviceTier`、text verbosity、native Codex web search、
  reasoning-compat payload shaping、Responses context management 向けの共有 native OpenAI Responses wrapper を所有します。
- OpenRouter は `catalog` に加え `resolveDynamicModel` と
  `prepareDynamicModel` を使います。これは provider が pass-through であり、
  OpenClaw の static catalog が更新される前に新しい model id を公開することがあるためです。さらに、
  provider 固有 request header、routing metadata、reasoning patch、
  prompt-cache policy をコアの外に保つために `capabilities`, `wrapStreamFn`, `isCacheTtlEligible` も使います。replay policy は
  `passthrough-gemini` family から来ており、`openrouter-thinking` stream family が
  proxy reasoning injection と unsupported-model / `auto` skip を所有します。
- GitHub Copilot は `catalog`, `auth`, `resolveDynamicModel`,
  `capabilities` に加えて `prepareRuntimeAuth` と `fetchUsageSnapshot` を使います。
  これは provider 所有の device login、model fallback behavior、Claude transcript
  quirks、GitHub token -> Copilot token exchange、および provider 所有の usage endpoint が必要だからです。
- OpenAI Codex は `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth`, `augmentModelCatalog` に加え
  `prepareExtraParams`, `resolveUsageAuth`, `fetchUsageSnapshot` を使います。
  これは core OpenAI transport 上で動作しつつ、transport/base URL
  normalization、OAuth refresh fallback policy、default transport choice、
  synthetic Codex catalog row、ChatGPT usage endpoint integration を所有しているためです。直接 OpenAI と同じ `openai-responses-defaults` stream family を共有します。
- Google AI Studio と Gemini CLI OAuth は `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn`, `isModernModelRef` を使います。これは
  `google-gemini` replay family が Gemini 3.1 の forward-compat fallback、
  native Gemini replay validation、bootstrap replay sanitation、tagged
  reasoning-output mode、modern-model matching を所有し、
  `google-thinking` stream family が Gemini thinking payload normalization を所有するためです。
  Gemini CLI OAuth はさらに、token formatting、token parsing、quota endpoint
  wiring のために `formatApiKey`, `resolveUsageAuth`,
  `fetchUsageSnapshot` も使います。
- Anthropic Vertex は、`anthropic-by-model` replay family を通じて
  `buildReplayPolicy` を使います。これにより Claude 固有 replay cleanup が、
  すべての `anthropic-messages` transport ではなく Claude id に限定されます。
- Amazon Bedrock は `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `resolveDefaultThinkingLevel` を使います。これは
  Anthropic-on-Bedrock traffic 向けの Bedrock 固有 throttle/not-ready/context-overflow error classification を所有しているためです。replay policy は依然として同じ Claude 専用
  `anthropic-by-model` guard を共有します。
- OpenRouter, Kilocode, Opencode, Opencode Go は、`passthrough-gemini`
  replay family を通じて `buildReplayPolicy` を使います。これは Gemini
  model を OpenAI-compatible transport 経由で proxy しており、native Gemini
  replay validation や bootstrap rewrite なしで Gemini
  thought-signature sanitation が必要なためです。
- MiniMax は、`hybrid-anthropic-openai` replay family を通じて
  `buildReplayPolicy` を使います。これは 1 つの provider が Anthropic-message と OpenAI-compatible semantics の両方を所有しているためです。Anthropic 側では Claude 専用の
  thinking-block dropping を維持しつつ、reasoning output mode を native に上書きし、
  `minimax-fast-mode` stream family が共有 stream path 上で fast-mode model rewrite を所有します。
- Moonshot は `catalog` に加えて `wrapStreamFn` を使います。共有
  OpenAI transport を使いつつ provider 所有の thinking payload normalization が必要なためです。
  `moonshot-thinking` stream family は config と `/think` state をその
  native binary thinking payload にマッピングします。
- Kilocode は `catalog`, `capabilities`, `wrapStreamFn`,
  `isCacheTtlEligible` を使います。provider 所有 request header、
  reasoning payload normalization、Gemini transcript hint、Anthropic
  cache-TTL gating が必要なためです。`kilocode-thinking` stream family は、
  明示的 reasoning payload をサポートしない `kilo/auto` やその他 proxy model id をスキップしつつ、共有 proxy stream path 上で Kilo thinking injection を維持します。
- Z.AI は `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth`, `fetchUsageSnapshot` を使います。これは GLM-5 fallback、
  `tool_stream` defaults、binary thinking UX、modern-model matching、および
  usage auth + quota fetching の両方を所有しているためです。`tool-stream-default-on`
  stream family は、デフォルトオンの `tool_stream` wrapper を provider ごとの手書き glue から切り離します。
- xAI は `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel`, `isModernModelRef`
  を使います。これは native xAI Responses transport normalization、Grok fast-mode
  alias rewrite、default `tool_stream`、strict-tool / reasoning-payload
  cleanup、plugin 所有 tool の fallback auth reuse、forward-compat Grok
  model resolution、および xAI tool-schema
  profile、unsupported schema keyword、native `web_search`、HTML-entity
  tool-call argument decoding などの provider 所有 compat patch を所有しているためです。
- Mistral, OpenCode Zen, OpenCode Go は `capabilities` のみを使い、
  transcript/tooling quirks をコアから切り離しています。
- `byteplus`, `cloudflare-ai-gateway`, `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway`, `volcengine` のような
  catalog-only の bundled provider は `catalog` のみを使います。
- Qwen は、テキスト provider 向けに `catalog` を使い、その multimodal surface 向けに共有 media-understanding と
  video-generation registration も使います。
- MiniMax と Xiaomi は `catalog` に加えて usage hook も使います。これは、
  inference 自体は共有 transport で動作する一方で、`/usage`
  behavior は plugin 所有だからです。

## ランタイムヘルパー

プラグインは `api.runtime` を通じて、選択されたコア helper にアクセスできます。TTS の場合:

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

- `textToSpeech` は file/voice-note surface 向けの通常のコア TTS output payload を返します。
- コアの `messages.tts` 設定と provider selection を使用します。
- PCM audio buffer + sample rate を返します。プラグイン側で provider 向けに resample/encode する必要があります。
- `listVoices` は provider ごとに任意です。ベンダー所有 voice picker や setup flow に使ってください。
- voice listing には、provider-aware picker 向けに locale、gender、personality tag などのより豊富な metadata を含められます。
- 現在 telephony をサポートするのは OpenAI と ElevenLabs です。Microsoft はサポートしません。

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

- TTS policy、fallback、reply delivery はコアに保持してください。
- ベンダー所有の synthesis behavior には speech provider を使ってください。
- legacy Microsoft `edge` input は `microsoft` provider id に正規化されます。
- 推奨される ownership model は company-oriented です。OpenClaw がそれらの
  capability contract を追加していくにつれて、1 つの vendor plugin が
  text、speech、image、将来の media provider を所有できます。

画像/音声/動画理解では、プラグインは generic な key/value bag ではなく、1 つの型付き
media-understanding provider を登録します。

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

- orchestration、fallback、config、channel wiring はコアに保持してください。
- ベンダー behavior は provider plugin に保持してください。
- 追加拡張は型付きのままにすべきです。新しい optional method、新しい optional
  result field、新しい optional capability といった形です。
- 動画生成もすでに同じパターンに従っています:
  - コアが capability contract と runtime helper を所有
  - ベンダープラグインが `api.registerVideoGenerationProvider(...)` を登録
  - 機能/チャネルプラグインが `api.runtime.videoGeneration.*` を利用

media-understanding runtime helper については、プラグインは次を呼び出せます。

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

音声文字起こしについては、プラグインは media-understanding runtime か、
古い STT alias のどちらかを使えます。

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // MIME を確実に推定できない場合は任意:
  mime: "audio/ogg",
});
```

注:

- `api.runtime.mediaUnderstanding.*` は、画像/音声/動画理解に対する推奨共有 surface です。
- コアの media-understanding 音声設定（`tools.media.audio`）と provider fallback order を使用します。
- 文字起こし出力が生成されない場合（例: skipped/unsupported input）には `{ text: undefined }` を返します。
- `api.runtime.stt.transcribeAudioFile(...)` は互換 alias として残っています。

プラグインは `api.runtime.subagent` を通じてバックグラウンド subagent run も起動できます。

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

- `provider` と `model` は、永続的な session 変更ではなく、run ごとの任意の override です。
- OpenClaw は、信頼された caller に対してのみそれらの override field を受け付けます。
- plugin 所有 fallback run では、operator が `plugins.entries.<id>.subagent.allowModelOverride: true` でオプトインする必要があります。
- 信頼されたプラグインを特定の canonical `provider/model` target に制限するには `plugins.entries.<id>.subagent.allowedModels` を使い、任意 target を明示的に許可するには `"*"` を使います。
- 信頼されていない plugin subagent run も動作はしますが、override request は黙って fallback されるのではなく拒否されます。

Web 検索について、プラグインは agent tool wiring に直接到達するのではなく、
共有 runtime helper を利用できます。

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

プラグインは `api.registerWebSearchProvider(...)` を通じて web-search provider も登録できます。

注:

- provider selection、credential resolution、共有 request semantics はコアに保持してください。
- ベンダー固有の search transport には web-search provider を使ってください。
- `api.runtime.webSearch.*` は、agent tool wrapper に依存せず search behavior が必要な feature/channel plugin に対する推奨共有 surface です。

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

- `generate(...)`: 設定された画像生成 provider chain を使って画像を生成します。
- `listProviders(...)`: 利用可能な画像生成 provider とその capability を一覧表示します。

## Gateway HTTP routes

プラグインは `api.registerHttpRoute(...)` によって HTTP endpoint を公開できます。

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

route field:

- `path`: gateway HTTP server 配下の route path
- `auth`: 必須。通常の gateway auth を要求するには `"gateway"`、plugin 管理 auth/webhook verification には `"plugin"` を使います。
- `match`: 任意。`"exact"`（デフォルト）または `"prefix"`。
- `replaceExisting`: 任意。同じ plugin が自分自身の既存 route registration を置き換えることを許可します。
- `handler`: route が request を処理した場合に `true` を返します。

注:

- `api.registerHttpHandler(...)` は削除されており、plugin-load error になります。代わりに `api.registerHttpRoute(...)` を使ってください。
- plugin route は `auth` を明示的に宣言する必要があります。
- 完全に一致する `path + match` の競合は `replaceExisting: true` がない限り拒否され、ある plugin が別の plugin の route を置き換えることはできません。
- `auth` level が異なる重複 route は拒否されます。`exact`/`prefix` のフォールスルーチェーンは同じ auth level に限定してください。
- `auth: "plugin"` route は operator runtime scope を自動では受け取りません。これらは privileged Gateway helper call 用ではなく、plugin 管理 webhook/signature verification 用です。
- `auth: "gateway"` route は Gateway request runtime scope 内で実行されますが、その scope は意図的に保守的です:
  - shared-secret bearer auth（`gateway.auth.mode = "token"` / `"password"`）では、
    caller が `x-openclaw-scopes` を送っても plugin-route runtime scope は `operator.write` に固定されます
  - trusted identity-bearing HTTP mode（例: `trusted-proxy` または private ingress 上の `gateway.auth.mode = "none"`）では、
    header が明示的に存在する場合にのみ `x-openclaw-scopes` を尊重します
  - それらの identity-bearing plugin-route request に `x-openclaw-scopes` がない場合、
    runtime scope は `operator.write` にフォールバックします
- 実践的なルール: gateway-auth の plugin route が暗黙の admin surface だと思い込まないでください。route が admin-only behavior を必要とする場合は、identity-bearing auth mode を要求し、明示的な `x-openclaw-scopes` header contract を文書化してください。

## Plugin SDK import path

プラグインを作成するときは、単一の `openclaw/plugin-sdk` import ではなく、
SDK の subpath を使ってください。

- plugin registration primitives には `openclaw/plugin-sdk/plugin-entry`
- generic な共有 plugin-facing contract には `openclaw/plugin-sdk/core`
- root `openclaw.json` Zod schema
  export（`OpenClawSchema`）には `openclaw/plugin-sdk/config-schema`
- `openclaw/plugin-sdk/channel-setup`、
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
  `openclaw/plugin-sdk/webhook-ingress` のような stable channel primitive は、
  共有 setup/auth/reply/webhook wiring 向けです。`channel-inbound` は debounce、mention matching、
  inbound mention-policy helper、envelope formatting、inbound envelope
  context helper の共有ホームです。
  `channel-setup` は狭い optional-install setup seam です。
  `setup-runtime` は、`setupEntry` /
  deferred startup が使う runtime-safe setup surface で、import-safe な setup patch adapter を含みます。
  `setup-adapter-runtime` は env-aware な account-setup adapter seam です。
  `setup-tools` は小さな CLI/archive/docs helper seam（`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`）です。
- `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-gateway-runtime`,
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`,
  `openclaw/plugin-sdk/approval-handler-runtime`,
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
  `openclaw/plugin-sdk/directory-runtime` のような domain subpath は、
  共有 runtime/config helper 向けです。
  `telegram-command-config` は Telegram custom
  command normalization/validation 向けの狭い public seam であり、bundled
  Telegram contract surface が一時的に利用できなくても引き続き利用可能です。
  `text-runtime` は共有の text/markdown/logging seam で、
  assistant-visible-text stripping、markdown render/chunking helper、redaction
  helper、directive-tag helper、安全なテキスト utility を含みます。
- 承認固有チャネル seam は、plugin 上の 1 つの `approvalCapability`
  contract を優先すべきです。その 1 つの capability を通じて、コアは approval auth、delivery、render、
  native-routing、lazy native-handler behavior を読み取ります。approval behavior を無関係な plugin field に混在させるべきではありません。
- `openclaw/plugin-sdk/channel-runtime` は非推奨であり、古いプラグイン向けの互換 shim としてのみ残っています。新しいコードは、より狭い generic primitive を import すべきであり、repo コードでもこの shim の新規 import を追加すべきではありません。
- bundled extension internals は private のままです。外部プラグインは
  `openclaw/plugin-sdk/*` subpath のみを使うべきです。OpenClaw の core/test コードは、
  `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js`、および `login-qr-api.js` のような狭い file など、
  plugin package root 配下の repo public entry point を使ってよいです。
  コアや別 extension から plugin package の `src/*` を import してはいけません。
- Repo entry point の分割:
  `<plugin-package-root>/api.js` は helper/types barrel、
  `<plugin-package-root>/runtime-api.js` は runtime-only barrel、
  `<plugin-package-root>/index.js` は bundled plugin entry、
  `<plugin-package-root>/setup-entry.js` は setup plugin entry です。
- 現在の bundled provider の例:
  - Anthropic は Claude stream helper（`wrapAnthropicProviderStream`,
    beta-header helper、`service_tier`
    parsing など）のために `api.js` / `contract-api.js` を使います。
  - OpenAI は provider builder、default-model helper、realtime provider builder に `api.js` を使います。
  - OpenRouter は provider builder と onboarding/config
    helper に `api.js` を使い、`register.runtime.js` は repo-local 用に generic
    `plugin-sdk/provider-stream` helper を引き続き re-export できます。
- facade でロードされる public entry point は、利用可能であれば active runtime config snapshot を優先し、
  OpenClaw がまだ runtime snapshot を提供していない場合はディスク上の resolved config file にフォールバックします。
- generic shared primitive は引き続き推奨 public SDK contract です。
  bundled channel ブランドの helper seam には、互換性のための小さな予約セットがまだ残っています。これらは bundled
  maintenance/compatibility seam として扱い、新しいサードパーティー import target にはしないでください。新しい cross-channel contract は引き続き generic な `plugin-sdk/*` subpath か、plugin-local の `api.js` /
  `runtime-api.js` barrel に追加すべきです。

互換性に関する注記:

- 新しいコードでは root の `openclaw/plugin-sdk` barrel は避けてください。
- まず狭く安定した primitive を優先してください。新しい
  setup/pairing/reply/feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool subpath は、新しい bundled および外部 plugin 作業向けの意図された contract です。
  target parsing/matching は `openclaw/plugin-sdk/channel-targets` に置くべきです。
  message action gate と reaction の message-id helper は
  `openclaw/plugin-sdk/channel-actions` に置くべきです。
- bundled extension 固有 helper barrel はデフォルトでは安定ではありません。helper が bundled extension のみに必要なら、
  `openclaw/plugin-sdk/<extension>` に昇格させるのではなく、その extension の local
  `api.js` または `runtime-api.js` seam の背後に保持してください。
- 新しい共有 helper seam は channel-branded ではなく generic にすべきです。共有 target
  parsing は `openclaw/plugin-sdk/channel-targets` に置き、channel 固有
  internals は所有する plugin の local `api.js` または `runtime-api.js`
  seam の背後に置いてください。
- `image-generation`,
  `media-understanding`, `speech` のような capability 固有 subpath は、bundled/native プラグインが現在それらを使っているため存在します。その存在自体は、export されているすべての helper が長期固定された外部 contract であることを意味しません。

## Message tool schema

プラグインは、チャネル固有の `describeMessageTool(...)` schema
contribution を所有すべきです。provider 固有 field は共有コアではなく plugin 側に置いてください。

共有の移植可能な schema fragment には、
`openclaw/plugin-sdk/channel-actions` から export される generic helper を再利用してください。

- button-grid 形式 payload 用の `createMessageToolButtonsSchema()`
- structured card payload 用の `createMessageToolCardSchema()`

ある schema shape が 1 つの provider にしか意味を持たないなら、共有 SDK に昇格させるのではなく、その plugin 自身の source に定義してください。

## Channel target resolution

チャネルプラグインは、チャネル固有の target semantics を所有すべきです。共有 outbound host は generic のままにし、provider ルールには messaging adapter surface を使ってください。

- `messaging.inferTargetChatType({ to })` は、正規化された target を
  directory lookup 前に `direct`, `group`, `channel` のどれとして扱うかを決定します。
- `messaging.targetResolver.looksLikeId(raw, normalized)` は、
  core が directory search の代わりに直ちに id-like resolution に進むべき input かどうかを伝えます。
- `messaging.targetResolver.resolveTarget(...)` は、正規化後または
  directory miss 後に core が最終的な provider 所有 resolution を必要とするときの plugin fallback です。
- `messaging.resolveOutboundSessionRoute(...)` は、target 解決後の provider 固有 session
  route construction を所有します。

推奨される分担:

- peer/group 検索前に行うべきカテゴリ判断には `inferTargetChatType` を使う
- 「明示的/native target id として扱う」判定には `looksLikeId` を使う
- `resolveTarget` は broad directory search ではなく、provider 固有の normalization fallback に使う
- chat id、thread id、JID、handle、room
  id のような provider-native id は、generic SDK field ではなく `target` value または provider-specific params の内部に保持する

## Config-backed directory

config から directory entry を導出するプラグインは、そのロジックを plugin 側に保持し、
`openclaw/plugin-sdk/directory-runtime` の共有 helper を再利用すべきです。

これは、チャネルが以下のような config-backed peer/group を必要とする場合に使います。

- allowlist 駆動の DM peer
- 設定済み channel/group map
- account-scoped な静的 directory fallback

`directory-runtime` の共有 helper は、generic operation のみを扱います。

- query filtering
- limit application
- deduping/normalization helper
- `ChannelDirectoryEntry[]` の構築

チャネル固有の account inspection と id normalization は plugin 実装側に残すべきです。

## Provider catalog

プロバイダープラグインは、`registerProvider({ catalog: { run(...) { ... } } })` によって
推論用 model catalog を定義できます。

`catalog.run(...)` は、OpenClaw が `models.providers` に書き込むのと同じ shape を返します。

- 1 つの provider entry なら `{ provider }`
- 複数の provider entry なら `{ providers }`

plugin が provider 固有の model id、base URL
default、または auth-gated model metadata を所有する場合は `catalog` を使ってください。

`catalog.order` は、OpenClaw の built-in implicit provider に対して plugin の catalog をいつ merge するかを制御します。

- `simple`: plain な API-key または env 駆動 provider
- `profile`: auth profile が存在すると現れる provider
- `paired`: 複数の関連 provider entry を合成する provider
- `late`: 最後のパス。他の implicit provider の後

後に来る provider が key collision で勝つため、plugin は同じ provider id を持つ built-in provider entry を意図的に上書きできます。

互換性:

- `discovery` は legacy alias として引き続き動作します
- `catalog` と `discovery` の両方が登録されている場合、OpenClaw は `catalog` を使います

## 読み取り専用チャネル inspection

plugin が channel を登録する場合、`resolveAccount(...)` と並行して
`plugin.config.inspectAccount(cfg, accountId)` を実装することを推奨します。

理由:

- `resolveAccount(...)` は runtime path です。credential が完全に materialize されていることを前提にでき、必要な secret が不足していれば即座に失敗して構いません。
- `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve`、および doctor/config
  repair flow のような読み取り専用 command path は、設定を説明するだけのために runtime credential を materialize する必要があるべきではありません。

推奨される `inspectAccount(...)` の動作:

- 説明的な account state のみを返す
- `enabled` と `configured` を保持する
- relevant な場合は credential source/status field を含める:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- 読み取り専用 availability を報告するだけなら、生の token value を返す必要はありません。
  `tokenStatus: "available"`（および対応する source field）を返せば、status 系 command には十分です。
- credential が SecretRef 経由で設定されているが現在の command path では利用不可な場合は `configured_unavailable` を使う

これにより、読み取り専用 command は、クラッシュしたり未設定と誤報したりする代わりに、
「設定済みだが、この command path では利用不可」と報告できます。

## Package pack

plugin directory には `openclaw.extensions` を含む `package.json` を置けます。

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

各 entry は 1 つの plugin になります。pack が複数 extension を列挙する場合、plugin id
は `name/<fileBase>` になります。

plugin が npm dependency を import する場合は、その directory に install して
`node_modules` を利用可能にしてください（`npm install` / `pnpm install`）。

セキュリティガードレール: すべての `openclaw.extensions` entry は、symlink 解決後も plugin
directory 内にとどまる必要があります。package directory から外へ出る entry は拒否されます。

セキュリティに関する注記: `openclaw plugins install` は plugin dependency を
`npm install --omit=dev --ignore-scripts` でインストールします
（lifecycle script なし、runtime では dev dependency なし）。plugin dependency
tree は「pure JS/TS」に保ち、`postinstall` build を必要とする package は避けてください。

任意: `openclaw.setupEntry` は、軽量な setup-only module を指せます。
OpenClaw が無効化された channel plugin の setup surface を必要とする場合、または
channel plugin が有効でもまだ未設定の場合、完全な plugin entry の代わりに
`setupEntry` を読み込みます。これにより、main plugin entry が tools、hooks、
その他 runtime-only code も配線している場合に、startup と setup を軽く保てます。

任意: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
を使うと、channel plugin がすでに設定済みであっても、gateway の
pre-listen startup phase 中に同じ `setupEntry` path へオプトインできます。

これは、gateway が listen を開始する前に存在しなければならない startup surface を `setupEntry` が完全にカバーしている場合にのみ使ってください。実際には、setup entry は startup が依存するすべての channel 所有 capability を登録していなければなりません。たとえば:

- channel registration 自体
- gateway が listen を開始する前に利用可能である必要がある HTTP route
- 同じウィンドウ中に存在しなければならない gateway method、tool、service

full entry がまだ必須 startup capability を所有している場合は、この flag を有効にしないでください。デフォルト動作のままにし、OpenClaw が startup 中に full entry を読み込むようにしてください。

バンドル済み channel は、full channel runtime が読み込まれる前にコアが参照できる
setup-only の contract-surface helper も公開できます。現在の setup
promotion surface は次のとおりです。

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

コアは、full plugin entry を読み込まずに legacy な single-account channel
config を `channels.<id>.accounts.*` に昇格させる必要がある場合にこの surface を使います。
Matrix が現在の bundled 例です。named account がすでに存在する場合、auth/bootstrap key のみを named promoted account に移動し、常に
`accounts.default` を作成するのではなく、設定済みの non-canonical default-account key を保持できます。

これらの setup patch adapter は、bundled contract-surface discovery を lazy に保ちます。
import 時間は軽いままで、promotion surface は module import 時に bundled channel startup を再突入する代わりに、最初の使用時にのみ読み込まれます。

これらの startup surface に gateway RPC method が含まれる場合は、
plugin 固有 prefix に置いてください。core admin namespace（`config.*`,
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

### Channel catalog metadata

チャネルプラグインは `openclaw.channel` で setup/discovery metadata を、
`openclaw.install` で install hint を宣伝できます。これによりコア catalog を data-free に保てます。

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

最小例以外で有用な `openclaw.channel` field:

- `detailLabel`: より豊かな catalog/status surface 用の補助ラベル
- `docsLabel`: docs link の link text を上書き
- `preferOver`: この catalog entry が優先すべき、より低優先の plugin/channel id
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: selection-surface の copy 制御
- `markdownCapable`: outbound formatting 判断用に、その channel が markdown 対応であることを示す
- `exposure.configured`: `false` の場合、configured-channel listing surface から隠す
- `exposure.setup`: `false` の場合、interactive setup/configure picker から隠す
- `exposure.docs`: docs navigation surface で channel を internal/private として扱う
- `showConfigured` / `showInSetup`: legacy alias として引き続き受理される。`exposure` を優先する
- `quickstartAllowFrom`: channel を標準 quickstart `allowFrom` flow にオプトインする
- `forceAccountBinding`: account が 1 つしかない場合でも明示的 account binding を必須にする
- `preferSessionLookupForAnnounceTarget`: announce target 解決時に session lookup を優先する

OpenClaw は**外部 channel catalog**（たとえば MPM registry export）もマージできます。
JSON file を以下のいずれかに置いてください。

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

または `OPENCLAW_PLUGIN_CATALOG_PATHS`（または `OPENCLAW_MPM_CATALOG_PATHS`）で、
1 つ以上の JSON file を指してください（カンマ/セミコロン/`PATH` 区切り）。
各 file には `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }` を含める必要があります。parser は `"entries"` key の legacy alias として `"packages"` または `"plugins"` も受け付けます。

## Context engine プラグイン

Context engine プラグインは、ingest、assembly、
compaction のセッションコンテキスト orchestration を所有します。plugin から
`api.registerContextEngine(id, factory)` で登録し、
`plugins.slots.contextEngine` で active engine を選択します。

default context
pipeline を単に拡張するのではなく、置き換えまたは拡張する必要がある場合に使います。

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

engine が compaction algorithm を**所有しない**場合でも、`compact()`
は実装し、明示的に委譲してください。

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

## 新しい capability の追加

プラグインが現在の API に収まらない動作を必要とする場合、private な reach-in で
plugin system を回避しないでください。欠けている capability を追加してください。

推奨シーケンス:

1. コア contract を定義する
   コアが所有すべき共有動作を決めます。policy、fallback、config merge、
   lifecycle、channel-facing semantics、runtime helper shape です。
2. 型付き plugin registration/runtime surface を追加する
   最小限で有用な型付き capability surface を `OpenClawPluginApi` や
   `api.runtime` に拡張します。
3. コア + チャネル/機能 consumer を配線する
   チャネルと機能プラグインは、ベンダー実装を直接 import するのではなく、
   コア経由で新しい capability を利用すべきです。
4. ベンダー実装を登録する
   その後、ベンダープラグインがその capability に backend を登録します。
5. contract coverage を追加する
   ownership と registration shape が時間とともに明示的に保たれるよう、テストを追加します。

これが、OpenClaw が 1 つの provider の worldview にハードコードされることなく、
意見を持った設計を維持する方法です。具体的な file checklist と worked example については
[Capability Cookbook](/ja-JP/plugins/architecture) を参照してください。

### capability checklist

新しい capability を追加するとき、実装では通常、以下の surface をまとめて変更する必要があります。

- `src/<capability>/types.ts` の core contract types
- `src/<capability>/runtime.ts` の core runner/runtime helper
- `src/plugins/types.ts` の plugin API registration surface
- `src/plugins/registry.ts` の plugin registry wiring
- feature/channel plugin が利用する必要がある場合は `src/plugins/runtime/*` の plugin runtime exposure
- `src/test-utils/plugin-registration.ts` の capture/test helper
- `src/plugins/contracts/registry.ts` の ownership/contract assertion
- `docs/` の operator/plugin docs

これらのどれかが欠けているなら、その capability はまだ完全には統合されていない兆候であることが多いです。

### capability template

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

これでルールは単純に保たれます。

- コアが capability contract + orchestration を所有
- ベンダープラグインがベンダー実装を所有
- 機能/チャネルプラグインが runtime helper を利用
- contract test が ownership を明示的に保つ
