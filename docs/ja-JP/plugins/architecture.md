---
read_when:
    - ネイティブ OpenClaw plugin を構築またはデバッグしている
    - plugin の capability モデルや所有権の境界を理解したい
    - plugin のロードパイプラインやレジストリに取り組んでいる
    - provider ランタイムフックや channel plugin を実装している
sidebarTitle: Internals
summary: 'plugin の内部: capability モデル、所有権、コントラクト、ロードパイプライン、ランタイムヘルパー'
title: Plugin の内部
x-i18n:
    generated_at: "2026-04-06T03:13:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: d39158455701dedfb75f6c20b8c69fd36ed9841f1d92bed1915f448df57fd47b
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin の内部

<Info>
  これは**詳細なアーキテクチャリファレンス**です。実践的なガイドについては、以下を参照してください。
  - [plugin のインストールと使用](/ja-JP/tools/plugin) — ユーザーガイド
  - [はじめに](/ja-JP/plugins/building-plugins) — 最初の plugin チュートリアル
  - [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — メッセージングチャンネルを構築する
  - [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — モデル provider を構築する
  - [SDK Overview](/ja-JP/plugins/sdk-overview) — import map と登録 API
</Info>

このページでは、OpenClaw plugin システムの内部アーキテクチャを扱います。

## 公開 capability モデル

Capabilities は、OpenClaw 内部における公開された**ネイティブ plugin** モデルです。すべての
ネイティブ OpenClaw plugin は、1 つ以上の capability type に対して登録されます。

| Capability             | 登録方法                                         | plugin の例                         |
| ---------------------- | ------------------------------------------------ | ------------------------------------ |
| テキスト推論           | `api.registerProvider(...)`                      | `openai`, `anthropic`                |
| 音声                   | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`            |
| リアルタイム文字起こし | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| リアルタイム音声       | `api.registerRealtimeVoiceProvider(...)`         | `openai`                             |
| メディア理解           | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| 画像生成               | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| 音楽生成               | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                  |
| 動画生成               | `api.registerVideoGenerationProvider(...)`       | `qwen`                               |
| Web 取得               | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| Web 検索               | `api.registerWebSearchProvider(...)`             | `google`                             |
| Channel / メッセージング | `api.registerChannel(...)`                     | `msteams`, `matrix`                  |

capability を 1 つも登録せず、hooks、tools、services を提供する
plugin は、**レガシーな hook-only** plugin です。このパターンも引き続き完全にサポートされています。

### 外部互換性に関する方針

capability モデルはすでに core に導入されており、現在 bundled/native plugins
で使用されていますが、外部 plugin の互換性には「export されているので固定されている」
より厳しい基準が依然として必要です。

現在のガイダンス:

- **既存の外部 plugins:** hook ベースの統合を動作させ続ける。これを互換性のベースラインとして扱う
- **新しい bundled/native plugins:** vendor 固有の内部参照や新しい hook-only 設計よりも、明示的な capability 登録を優先する
- **capability 登録を採用する外部 plugins:** 使用は許可されるが、docs で明示的に安定コントラクトとして示されない限り、capability 固有の helper surface は進化中のものとして扱う

実践的なルール:

- capability 登録 API は意図された方向性である
- 移行期間中、レガシー hooks は外部 plugins にとって最も安全で破壊の少ない経路である
- export されている helper subpath はすべて同等ではない。偶発的な helper export ではなく、文書化された狭いコントラクトを優先する

### Plugin の形

OpenClaw は、読み込まれた各 plugin を、実際の登録動作に基づいて
形として分類します（静的メタデータだけではありません）。

- **plain-capability** -- ちょうど 1 種類の capability type を登録する（例: `mistral` のような provider-only plugin）
- **hybrid-capability** -- 複数種類の capability type を登録する（例:
  `openai` は text inference、speech、media understanding、image
  generation を所有する）
- **hook-only** -- hooks（型付きまたは custom）のみを登録し、capabilities、
  tools、commands、services は登録しない
- **non-capability** -- tools、commands、services、routes は登録するが
  capabilities は登録しない

`openclaw plugins inspect <id>` を使用すると、plugin の shape と capability
の内訳を確認できます。詳細は [CLI リファレンス](/cli/plugins#inspect) を参照してください。

### レガシー hooks

`before_agent_start` hook は、hook-only plugins の互換経路として引き続きサポートされています。実際のレガシー plugin は今もこれに依存しています。

方向性:

- 動作を維持する
- レガシーとして文書化する
- model/provider の上書き処理には `before_model_resolve` を優先する
- prompt の変更処理には `before_prompt_build` を優先する
- 実使用が減少し、fixture coverage が安全な移行を証明した後にのみ削除する

### 互換性シグナル

`openclaw doctor` または `openclaw plugins inspect <id>` を実行すると、
以下のラベルのいずれかが表示されることがあります。

| シグナル                 | 意味 |
| ------------------------ | ------------------------------------------------------------ |
| **config valid**         | 設定は正しく解析され、plugins は解決されている |
| **compatibility advisory** | plugin はサポートされているが古いパターン（例: `hook-only`）を使用している |
| **legacy warning**       | plugin は非推奨の `before_agent_start` を使用している |
| **hard error**           | 設定が不正、または plugin のロードに失敗した |

`hook-only` も `before_agent_start` も、現時点で plugin を壊すことはありません --
`hook-only` は助言レベルであり、`before_agent_start` は警告を出すだけです。これらの
シグナルは `openclaw status --all` と `openclaw plugins doctor` にも表示されます。

## アーキテクチャ概要

OpenClaw の plugin システムには 4 つのレイヤーがあります。

1. **manifest + discovery**
   OpenClaw は、設定されたパス、workspace roots、
   グローバル extension roots、bundled extensions から候補 plugin を検出します。
   Discovery は、ネイティブの `openclaw.plugin.json` manifests と、サポートされる bundle manifests を最初に読み取ります。
2. **有効化 + 検証**
   Core は、検出された plugin が有効、無効、ブロック済み、または memory のような排他的スロットに選択されているかを判断します。
3. **ランタイムロード**
   ネイティブ OpenClaw plugins は jiti を通じてプロセス内でロードされ、
   capabilities を中央レジストリへ登録します。互換 bundle は、ランタイムコードを import せずにレジストリレコードへ正規化されます。
4. **surface の消費**
   OpenClaw の他の部分はレジストリを読み取り、tools、channels、provider
   setup、hooks、HTTP routes、CLI commands、services を公開します。

特に plugin CLI では、ルートコマンドの discovery は 2 段階に分かれています。

- parse-time の metadata は `registerCli(..., { descriptors: [...] })` から取得される
- 実際の plugin CLI module は lazy のままでよく、最初の呼び出し時に登録される

これにより、plugin 所有の CLI コードを plugin 内に保ちつつ、
OpenClaw は解析前にルートコマンド名を予約できます。

重要な設計上の境界:

- discovery + config validation は、plugin コードを実行せずに**manifest/schema metadata**
  から動作できるべきである
- ネイティブランタイムの動作は、plugin module の `register(api)` パスから来る

この分離により、OpenClaw は完全なランタイムが有効になる前に、config を検証し、
欠落/無効な plugins を説明し、UI/schema のヒントを構築できます。

### Channel plugins と共有 message tool

通常のチャットアクションのために、channel plugins は個別の送信/編集/リアクション
tool を登録する必要はありません。OpenClaw は core に 1 つの共有 `message` tool を保ち、
channel plugins はその背後にある channel 固有の discovery と execution を所有します。

現在の境界は次のとおりです。

- core は共有 `message` tool host、prompt wiring、session/thread
  bookkeeping、および execution dispatch を所有する
- channel plugins は scoped action discovery、capability discovery、および channel 固有の schema fragment を所有する
- channel plugins は、会話 ID が thread ID をどのように encode するか、
  または親会話から継承するかといった、provider 固有の session conversation grammar を所有する
- channel plugins は action adapter を通じて最終アクションを実行する

channel plugins に対する SDK surface は
`ChannelMessageActionAdapter.describeMessageTool(...)` です。この統一された discovery
call により、plugin は visible actions、capabilities、schema
contributions をまとめて返せるため、これらがずれません。

Core はその discovery ステップにランタイムスコープを渡します。重要なフィールドには次が含まれます。

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- 信頼された inbound `requesterSenderId`

これは、コンテキスト依存の plugins にとって重要です。channel は、core の `message` tool
に channel 固有の分岐をハードコードすることなく、アクティブアカウント、
現在の room/thread/message、または信頼された requester identity に基づいて、
message actions を隠したり公開したりできます。

このため、embedded-runner の routing 変更は引き続き plugin 側の作業です。runner は、
共有 `message` tool が現在のターンに対して正しい channel 所有の
surface を公開できるよう、現在の chat/session identity を plugin
discovery 境界へ転送する責任があります。

channel 所有の execution helpers については、bundled plugins は execution
runtime を自分たちの extension modules 内に保つべきです。Core はもはや Discord、
Slack、Telegram、WhatsApp の message-action runtimes を `src/agents/tools`
配下に所有していません。別個の `plugin-sdk/*-action-runtime` subpath は公開しておらず、
bundled plugins は自分たちの extension 所有 modules からローカルランタイムコードを
直接 import するべきです。

同じ境界は一般に provider 名付き SDK seams にも適用されます。core は Slack、Discord、Signal、
WhatsApp、または類似の extensions 向け channel 固有 convenience barrels を
import すべきではありません。core が何らかの動作を必要とする場合は、
bundled plugin 自身の `api.ts` / `runtime-api.ts` barrel を利用するか、
その必要性を共有 SDK の狭い汎用 capability に昇格させてください。

polls に関しては、2 つの execution path があります。

- `outbound.sendPoll` は、共通の poll モデルに適合する channels 向けの共有ベースライン
- `actions.handleAction("poll")` は、channel 固有の poll semantics や追加 poll パラメーターに対する推奨経路

Core は現在、plugin poll dispatch がアクションを拒否した後まで共有 poll
parsing を延期するため、plugin 所有の poll handlers は generic poll
parser に先にブロックされることなく、channel 固有の poll fields を受け取れます。

完全な起動シーケンスについては [Load pipeline](#load-pipeline) を参照してください。

## Capability 所有権モデル

OpenClaw はネイティブ plugin を、無関係な統合を詰め込んだ寄せ集めではなく、
**会社** または **機能** の所有権境界として扱います。

これは次を意味します。

- company plugin は通常、その会社に関する OpenClaw surface をすべて所有すべきである
- feature plugin は通常、自身が導入する機能 surface 全体を所有すべきである
- channels は provider の動作を場当たり的に再実装するのではなく、共有 core capability を消費すべきである

例:

- bundled の `openai` plugin は OpenAI の model-provider 動作と OpenAI の
  speech + realtime-voice + media-understanding + image-generation 動作を所有する
- bundled の `elevenlabs` plugin は ElevenLabs の speech 動作を所有する
- bundled の `microsoft` plugin は Microsoft の speech 動作を所有する
- bundled の `google` plugin は Google の model-provider 動作に加え、Google の
  media-understanding + image-generation + web-search 動作を所有する
- bundled の `firecrawl` plugin は Firecrawl の web-fetch 動作を所有する
- bundled の `minimax`, `mistral`, `moonshot`, `zai` plugins は
  それぞれの media-understanding backend を所有する
- bundled の `qwen` plugin は Qwen の text-provider 動作に加え、
  media-understanding と video-generation 動作を所有する
- `voice-call` plugin は feature plugin であり、call transport、tools、
  CLI、routes、Twilio media-stream bridging を所有するが、vendor
  plugins を直接 import するのではなく、共有 speech と realtime-transcription、
  realtime-voice capabilities を消費する

意図されている最終状態は次のとおりです。

- OpenAI は、text models、speech、images、将来の video にまたがっていても 1 つの plugin に存在する
- 他の vendor も、自分たちの surface area に対して同じことができる
- channels は、どの vendor plugin が provider を所有しているかを気にせず、
  core が公開する共有 capability contract を消費する

ここで重要な区別は次です。

- **plugin** = 所有権境界
- **capability** = 複数の plugins が実装または消費できる core contract

したがって、OpenClaw が video のような新しいドメインを追加する場合、最初の問いは
「どの provider が video handling をハードコードすべきか」ではありません。最初の問いは
「core の video capability contract は何か」です。その contract が存在すれば、
vendor plugins はそれに対して登録でき、channel/feature plugins はそれを消費できます。

capability がまだ存在しない場合、通常の正しい手順は次です。

1. core で欠けている capability を定義する
2. それを plugin API/runtime を通じて型付きで公開する
3. channels/features をその capability に対して配線する
4. vendor plugins に実装を登録させる

これにより、所有権を明確に保ちつつ、単一 vendor や一度限りの plugin 固有コードパスに依存する
core の動作を避けられます。

### Capability のレイヤリング

コードの所属先を判断するときは、以下の考え方を使ってください。

- **core capability layer**: 共有 orchestration、policy、fallback、config
  merge rules、delivery semantics、型付きコントラクト
- **vendor plugin layer**: vendor 固有 API、auth、model catalogs、speech
  synthesis、image generation、将来の video backends、usage endpoints
- **channel/feature plugin layer**: Slack/Discord/voice-call などの統合で、
  core capabilities を消費して何らかの surface 上に提示するもの

たとえば、TTS は次の形になります。

- core は reply-time の TTS policy、fallback 順序、prefs、channel delivery を所有する
- `openai`, `elevenlabs`, `microsoft` は synthesis 実装を所有する
- `voice-call` は telephony TTS runtime helper を消費する

このパターンは将来の capabilities に対しても優先されるべきです。

### 複数 capability を持つ company plugin の例

company plugin は外から見て一貫性があるべきです。OpenClaw が models、speech、
realtime transcription、realtime voice、media understanding、
image generation、video generation、web fetch、web search に対する共有
contract を持つなら、vendor は自分の surface を 1 か所で所有できます。

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

重要なのは helper 名そのものではありません。形が重要です。

- 1 つの plugin が vendor surface を所有する
- core は引き続き capability contracts を所有する
- channels と feature plugins は vendor code ではなく `api.runtime.*` helpers を消費する
- contract tests は、その plugin が自ら所有を主張する capabilities を登録したことを検証できる

### Capability の例: video understanding

OpenClaw はすでに image/audio/video understanding を 1 つの共有
capability として扱っています。同じ所有権モデルがここにも適用されます。

1. core が media-understanding contract を定義する
2. vendor plugins は該当するものとして `describeImage`, `transcribeAudio`,
   `describeVideo` を登録する
3. channels と feature plugins は vendor code に直接つなぐのではなく、
   共有 core の動作を消費する

これにより、ある provider の video に関する前提を core に焼き付けることを避けられます。plugin は
vendor surface を所有し、core は capability contract と fallback behavior を所有します。

video generation もすでに同じ順序を使っています。core が型付き
capability contract と runtime helper を所有し、vendor plugins が
`api.registerVideoGenerationProvider(...)` の実装を登録します。

具体的な展開用チェックリストが必要ですか。参照先:
[Capability Cookbook](/ja-JP/plugins/architecture)。

## コントラクトと強制

plugin API surface は意図的に型付きであり、`OpenClawPluginApi` に集中しています。
この contract は、サポートされる登録ポイントと、plugin が依存できる
runtime helpers を定義します。

これが重要な理由:

- plugin authors は 1 つの安定した内部標準を得られる
- core は、2 つの plugin が同じ provider id を登録するような重複所有を拒否できる
- 起動時に、不正な登録に対する実用的な diagnostics を表示できる
- contract tests により、bundled-plugin の所有権を強制し、静かな drift を防げる

強制には 2 つのレイヤーがあります。

1. **ランタイム登録の強制**
   plugin registry は plugins のロード時に登録を検証します。例:
   重複 provider ids、重複 speech provider ids、不正な
   registrations は未定義動作ではなく plugin diagnostics を生成します。
2. **contract tests**
   Bundled plugins は test 実行中に contract registries へ取り込まれるため、
   OpenClaw は所有権を明示的に検証できます。現在これは model
   providers、speech providers、web search providers、bundled registration
   ownership に対して使われています。

実際の効果は、OpenClaw があらかじめ「どの plugin がどの surface を所有するか」を
把握していることです。これにより、所有権が暗黙ではなく宣言され、型付けされ、
テスト可能になっているため、core と channels が自然に組み合わせられます。

### コントラクトに含めるべきもの

良い plugin contracts は次の特性を持ちます。

- 型付き
- 小さい
- capability 固有
- core が所有する
- 複数の plugins で再利用できる
- vendor 知識なしで channels/features から消費できる

悪い plugin contracts は次のようなものです。

- core に隠された vendor 固有 policy
- registry を回避する一度限りの plugin escape hatch
- vendor 実装へ直接入り込む channel code
- `OpenClawPluginApi` や `api.runtime` の一部ではない場当たり的な runtime objects

迷ったら抽象度を上げてください。まず capability を定義し、その後で
plugins を接続させます。

## 実行モデル

ネイティブ OpenClaw plugins は Gateway と**同一プロセス内**で実行されます。
サンドボックス化はされません。ロードされたネイティブ plugin は、core code と同じ
プロセスレベルの信頼境界を持ちます。

含意:

- ネイティブ plugin は tools、network handlers、hooks、services を登録できる
- ネイティブ plugin のバグは gateway をクラッシュさせたり不安定化させたりできる
- 悪意あるネイティブ plugin は、OpenClaw プロセス内での任意コード実行と同等である

互換 bundle は、OpenClaw が現在それらを metadata/content packs として扱うため、
デフォルトではより安全です。現行リリースでは、これは主に bundled
skills を意味します。

非 bundled plugins には allowlists と明示的な install/load paths を使用してください。
workspace plugins は本番デフォルトではなく、開発時コードとして扱ってください。

bundled workspace package names については、plugin id を npm
name に固定してください。デフォルトでは `@openclaw/<id>`、または
意図的により狭い plugin role を公開する場合は
`-provider`, `-plugin`, `-speech`, `-sandbox`, `-media-understanding`
のような承認済み型付き suffix を使用します。

重要な信頼に関する注記:

- `plugins.allow` は source provenance ではなく**plugin ids**を信頼する
- bundled plugin と同じ id を持つ workspace plugin は、その workspace plugin が有効/allowlisted の場合、意図的に bundled copy を shadow する
- これは正常かつ有用であり、ローカル開発、patch testing、hotfixes に適している

## Export 境界

OpenClaw が export するのは implementation convenience ではなく capabilities です。

capability registration は公開のままにしつつ、非 contract な helper exports は削減します。

- bundled-plugin 固有 helper subpaths
- 公開 API として意図されていない runtime plumbing subpaths
- vendor 固有 convenience helpers
- 実装詳細である setup/onboarding helpers

一部の bundled-plugin helper subpaths は、互換性と bundled-plugin
maintenance のために、生成される SDK export map にまだ残っています。現在の例には
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup`, およびいくつかの `plugin-sdk/matrix*` seams が含まれます。これらは
新しいサードパーティ plugins 向けの推奨 SDK パターンではなく、予約された
implementation-detail exports として扱ってください。

## Load pipeline

起動時、OpenClaw は概ね次のことを行います。

1. 候補 plugin roots を検出する
2. ネイティブまたは互換 bundle の manifests と package metadata を読む
3. 安全でない候補を拒否する
4. plugin config（`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`）を正規化する
5. 各候補の有効化を決定する
6. 有効なネイティブ modules を jiti でロードする
7. ネイティブの `register(api)`（またはレガシー別名である `activate(api)`）hooks を呼び、
   plugin registry に registrations を収集する
8. registry を commands/runtime surfaces に公開する

<Note>
`activate` は `register` のレガシー別名です — loader は存在する方（`def.register ?? def.activate`）を解決して同じ地点で呼び出します。すべての bundled plugins は `register` を使用します。新しい plugins では `register` を優先してください。
</Note>

安全ゲートはランタイム実行**前**に発生します。候補は、entry が plugin
root を脱出している場合、パスが world-writable である場合、または
非 bundled plugins に対して path ownership が疑わしい場合にブロックされます。

### Manifest-first の動作

manifest は control-plane における真実のソースです。OpenClaw はこれを使って次を行います。

- plugin を識別する
- 宣言された channels/skills/config schema または bundle capabilities を検出する
- `plugins.entries.<id>.config` を検証する
- Control UI の labels/placeholders を補強する
- install/catalog metadata を表示する

ネイティブ plugins に対しては、runtime module が data-plane 部分です。これが
hooks、tools、commands、provider flows などの実際の動作を登録します。

### Loader がキャッシュするもの

OpenClaw は短命な in-process cache を次の対象に対して保持します。

- discovery results
- manifest registry data
- loaded plugin registries

これらの cache は、起動時の急増やコマンド繰り返し実行の overhead を減らします。これらは
永続化ではなく、短命な performance cache と考えるのが安全です。

パフォーマンスに関する注記:

- これらの cache を無効にするには、`OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` または
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` を設定してください。
- cache window は `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` と
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` で調整できます。

## Registry モデル

読み込まれた plugins は、ランダムな core globals を直接変更しません。代わりに、
中央の plugin registry に登録します。

registry は次を追跡します。

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

その後、core features は plugin modules と直接やりとりする代わりに、この registry から読み取ります。
これによりロードは一方向になります。

- plugin module -> registry registration
- core runtime -> registry consumption

この分離は保守性のために重要です。つまり、ほとんどの core surface は
「registry を読む」という 1 つの統合ポイントだけで済み、
「各 plugin module を個別特別扱いする」必要がありません。

## Conversation binding callbacks

会話を bind する plugins は、承認が解決されたときに反応できます。

bind request が承認または拒否された後に callback を受け取るには、
`api.onConversationBindingResolved(...)` を使用します。

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // この plugin + conversation に対して binding が作成された。
        console.log(event.binding?.conversationId);
        return;
      }

      // request は拒否された。ローカルの pending state を消去する。
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

callback payload fields:

- `status`: `"approved"` または `"denied"`
- `decision`: `"allow-once"`, `"allow-always"`, または `"deny"`
- `binding`: 承認された request に対する解決済み binding
- `request`: 元の request summary、detach hint、sender id、および
  conversation metadata

この callback は通知専用です。誰に conversation を bind
する権限があるかは変更せず、core の approval handling が完了した後に実行されます。

## Provider ランタイムフック

provider plugins には現在 2 つのレイヤーがあります。

- manifest metadata: ランタイムロード前に安価な env-auth lookup を行うための `providerAuthEnvVars`、およびランタイムロード前に安価な onboarding/auth-choice
  labels と CLI flag metadata を提供するための `providerAuthChoices`
- config-time hooks: `catalog` / レガシーな `discovery`、および `applyConfigDefaults`
- runtime hooks: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
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

OpenClaw は引き続き generic agent loop、failover、transcript handling、
tool policy を所有します。これらの hooks は、provider 固有の動作を拡張するための
surface であり、完全な custom inference transport を必要としません。

provider が env ベースの credentials を持ち、generic auth/status/model-picker
path が provider runtime をロードせずにそれを認識すべき場合は、manifest の
`providerAuthEnvVars` を使ってください。onboarding/auth-choice CLI
surface が provider の choice id、group labels、簡易な
one-flag auth wiring を provider runtime のロードなしで知るべき場合は、
manifest の `providerAuthChoices` を使ってください。provider runtime の
`envVars` は、onboarding labels や OAuth
client-id/client-secret setup vars のような operator 向けヒントに使い続けてください。

### Hook の順序と用途

model/provider plugins に対して、OpenClaw はおおむね次の順序で hooks を呼び出します。
「When to use」列は、素早い判断ガイドです。

| #   | Hook                              | 役割                                                                                     | 使用する場面                                                                                                                               |
| --- | --------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | `models.json` 生成時に provider config を `models.providers` へ公開する                 | provider が catalog または base URL defaults を所有する場合                                                                                |
| 2   | `applyConfigDefaults`             | config materialization 中に provider 所有の global config defaults を適用する            | defaults が auth mode、env、または provider model-family semantics に依存する場合                                                          |
| --  | _(built-in model lookup)_         | OpenClaw はまず通常の registry/catalog path を試す                                       | _(plugin hook ではない)_                                                                                                                    |
| 3   | `normalizeModelId`                | lookup 前に legacy または preview の model-id aliases を正規化する                       | provider が canonical model resolution 前の alias cleanup を所有する場合                                                                   |
| 4   | `normalizeTransport`              | generic model assembly 前に provider-family の `api` / `baseUrl` を正規化する            | provider が同じ transport family 内の custom provider ids の transport cleanup を所有する場合                                               |
| 5   | `normalizeConfig`                 | runtime/provider resolution 前に `models.providers.<id>` を正規化する                    | provider が plugin と一緒にあるべき config cleanup を必要とする場合。bundled Google-family helpers はサポートされる Google config entries も補完する |
| 6   | `applyNativeStreamingUsageCompat` | config providers に native streaming-usage compat rewrites を適用する                    | provider が endpoint 駆動の native streaming usage metadata 修正を必要とする場合                                                           |
| 7   | `resolveConfigApiKey`             | runtime auth loading 前に config providers の env-marker auth を解決する                 | provider が provider 所有の env-marker API-key resolution を持つ場合。`amazon-bedrock` にはここで built-in の AWS env-marker resolver もある |
| 8   | `resolveSyntheticAuth`            | plaintext を永続化せずに local/self-hosted または config-backed auth を公開する          | provider が synthetic/local credential marker で動作可能な場合                                                                              |
| 9   | `shouldDeferSyntheticProfileAuth` | env/config-backed auth より下位に保存済み synthetic profile placeholders を置く          | provider が precedence を取るべきでない synthetic placeholder profiles を保存する場合                                                      |
| 10  | `resolveDynamicModel`             | まだローカル registry にない provider 所有 model ids の同期 fallback                     | provider が任意の upstream model ids を受け付ける場合                                                                                       |
| 11  | `prepareDynamicModel`             | 非同期 warm-up の後、`resolveDynamicModel` を再実行する                                  | provider が未知 ID 解決前に network metadata を必要とする場合                                                                              |
| 12  | `normalizeResolvedModel`          | embedded runner が resolved model を使う前の最終書き換え                                 | provider が transport rewrites を必要とするが、引き続き core transport を使う場合                                                          |
| 13  | `contributeResolvedModelCompat`   | 別の互換 transport 配下の vendor models に compat flags を付与する                       | provider が provider を引き受けずに proxy transports 上で自分の models を認識する場合                                                     |
| 14  | `capabilities`                    | 共有 core logic が使う provider 所有 transcript/tooling metadata                         | provider が transcript/provider-family quirks を必要とする場合                                                                              |
| 15  | `normalizeToolSchemas`            | embedded runner が見る前に tool schemas を正規化する                                     | provider が transport-family schema cleanup を必要とする場合                                                                                |
| 16  | `inspectToolSchemas`              | 正規化後に provider 所有 schema diagnostics を公開する                                   | provider 固有ルールを core に教えずに keyword warnings を出したい場合                                                                      |
| 17  | `resolveReasoningOutputMode`      | native と tagged の reasoning-output contract を選択する                                 | provider が native fields ではなく tagged reasoning/final output を必要とする場合                                                         |
| 18  | `prepareExtraParams`              | generic stream option wrappers 前に request params を正規化する                          | provider が default request params または provider ごとの param cleanup を必要とする場合                                                   |
| 19  | `createStreamFn`                  | 通常の stream path を完全に custom transport に置き換える                                | provider が wrapper ではなく custom wire protocol を必要とする場合                                                                         |
| 20  | `wrapStreamFn`                    | generic wrappers 適用後に stream wrapper を適用する                                      | provider が custom transport なしで request headers/body/model compat wrappers を必要とする場合                                             |
| 21  | `resolveTransportTurnState`       | native な per-turn transport headers または metadata を付加する                          | provider が generic transports に provider-native turn identity を送らせたい場合                                                           |
| 22  | `resolveWebSocketSessionPolicy`   | native な WebSocket headers または session cool-down policy を付加する                   | provider が generic WS transports に session headers または fallback policy を調整させたい場合                                             |
| 23  | `formatApiKey`                    | auth-profile formatter: 保存済み profile を runtime `apiKey` 文字列に変換する            | provider が追加 auth metadata を保存し、custom runtime token shape を必要とする場合                                                       |
| 24  | `refreshOAuth`                    | custom refresh endpoints または refresh-failure policy のための OAuth refresh override   | provider が共有 `pi-ai` refreshers に適合しない場合                                                                                        |
| 25  | `buildAuthDoctorHint`             | OAuth refresh 失敗時に付与される修復ヒントを構築する                                     | provider が refresh failure 後の provider 所有 auth repair guidance を必要とする場合                                                      |
| 26  | `matchesContextOverflowError`     | provider 所有の context-window overflow matcher                                          | provider に generic heuristics では見逃す raw overflow errors がある場合                                                                   |
| 27  | `classifyFailoverReason`          | provider 所有の failover reason classification                                           | provider が raw API/transport errors を rate-limit/overload などに分類できる場合                                                          |
| 28  | `isCacheTtlEligible`              | proxy/backhaul providers 向け prompt-cache policy                                        | provider が proxy 固有 cache TTL gating を必要とする場合                                                                                   |
| 29  | `buildMissingAuthMessage`         | generic な missing-auth recovery message の代替                                          | provider が provider 固有の missing-auth recovery hint を必要とする場合                                                                    |
| 30  | `suppressBuiltInModel`            | stale upstream model の抑制と、必要なら user-facing error hint                           | provider が stale upstream rows を隠すか vendor hint に置き換える必要がある場合                                                            |
| 31  | `augmentModelCatalog`             | discovery 後に synthetic/final catalog rows を追加する                                   | provider が `models list` と pickers に synthetic forward-compat rows を必要とする場合                                                    |
| 32  | `isBinaryThinking`                | binary-thinking providers の on/off reasoning toggle                                     | provider が binary thinking の on/off のみを公開する場合                                                                                   |
| 33  | `supportsXHighThinking`           | 選択された models に対する `xhigh` reasoning support                                     | provider が一部の models だけで `xhigh` を使いたい場合                                                                                     |
| 34  | `resolveDefaultThinkingLevel`     | 特定 model family のデフォルト `/think` レベル                                          | provider が model family のデフォルト `/think` policy を所有する場合                                                                       |
| 35  | `isModernModelRef`                | live profile filters と smoke selection 向け modern-model matcher                        | provider が live/smoke preferred-model matching を所有する場合                                                                             |
| 36  | `prepareRuntimeAuth`              | 推論直前に設定済み credential を実際の runtime token/key に交換する                      | provider が token exchange または短命な request credential を必要とする場合                                                                |
| 37  | `resolveUsageAuth`                | `/usage` と関連 status surfaces 向けの usage/billing credentials を解決する              | provider が custom usage/quota token parsing または別の usage credential を必要とする場合                                                  |
| 38  | `fetchUsageSnapshot`              | auth 解決後に provider 固有の usage/quota snapshot を取得・正規化する                    | provider が provider 固有の usage endpoint または payload parser を必要とする場合                                                          |
| 39  | `createEmbeddingProvider`         | memory/search 用の provider 所有 embedding adapter を構築する                            | memory embedding behavior が provider plugin とともにあるべき場合                                                                          |
| 40  | `buildReplayPolicy`               | provider 向け transcript handling を制御する replay policy を返す                        | provider が custom transcript policy（例: thinking-block stripping）を必要とする場合                                                      |
| 41  | `sanitizeReplayHistory`           | generic transcript cleanup 後に replay history を書き換える                              | provider が共有 compaction helpers を超える provider 固有 replay rewrites を必要とする場合                                                 |
| 42  | `validateReplayTurns`             | embedded runner 前の最終 replay-turn validation または整形                               | provider transport が generic sanitation 後により厳しい turn validation を必要とする場合                                                  |
| 43  | `onModelSelected`                 | model が有効になったとき provider 所有の post-selection side effects を実行する          | provider が telemetry または provider 所有 state を必要とする場合                                                                          |

`normalizeModelId`, `normalizeTransport`, `normalizeConfig` はまず一致した
provider plugin を確認し、その後、実際に model id や
transport/config を変更した hook-capable provider plugins へ順にフォールスルーします。これにより、
caller がどの bundled plugin が rewrite を所有しているか知らなくても、
alias/compat provider shims が機能します。もし provider hook のどれも
サポートされた Google-family config entry を書き換えなければ、
bundled Google config normalizer が引き続きその互換 cleanup を適用します。

provider が完全な custom wire protocol または custom request executor を必要とする場合、
それは別クラスの extension です。これらの hooks は、OpenClaw の通常の
inference loop 上で動作する provider behavior のためのものです。

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
  `wrapStreamFn` を使用します。これは Claude 4.6 の forward-compat、
  provider-family hints、auth repair guidance、usage endpoint integration、
  prompt-cache eligibility、auth-aware config defaults、Claude の
  default/adaptive thinking policy、および beta headers、`/fast` /
  `serviceTier`、`context1m` のための Anthropic 固有 stream shaping を所有するためです。
- Anthropic の Claude 固有 stream helpers は、今のところ bundled plugin 自身の
  公開 `api.ts` / `contract-api.ts` seam に残っています。その package surface は
  `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier`、
  そしてより低レベルな Anthropic wrapper builders を export し、
  1 つの provider の beta-header ルールに合わせて generic SDK を広げすぎないようにしています。
- OpenAI は `resolveDynamicModel`, `normalizeResolvedModel`, `capabilities`
  に加えて `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking`, `isModernModelRef`
  を使います。これは GPT-5.4 の forward-compat、直接 OpenAI の
  `openai-completions` -> `openai-responses` 正規化、Codex-aware auth
  hints、Spark suppression、synthetic OpenAI list rows、GPT-5 の thinking /
  live-model policy を所有するためです。`openai-responses-defaults` stream family は、
  attribution headers、`/fast`/`serviceTier`、text verbosity、
  native Codex web search、reasoning-compat payload shaping、
  Responses context management のための共有 native OpenAI Responses wrappers を所有します。
- OpenRouter は `catalog` に加えて `resolveDynamicModel` と
  `prepareDynamicModel` を使います。provider が pass-through であり、
  OpenClaw の静的 catalog が更新される前に新しい model ids を公開することがあるためです。
  また、provider 固有 request headers、routing metadata、reasoning patches、
  prompt-cache policy を core の外に保つために
  `capabilities`, `wrapStreamFn`, `isCacheTtlEligible` も使用します。その replay policy は
  `passthrough-gemini` family から来ており、`openrouter-thinking` stream family は
  proxy reasoning injection と unsupported-model / `auto` スキップを所有します。
- GitHub Copilot は `catalog`, `auth`, `resolveDynamicModel`, `capabilities`
  に加えて `prepareRuntimeAuth` と `fetchUsageSnapshot` を使います。provider 所有の device login、
  model fallback behavior、Claude transcript quirks、GitHub token -> Copilot token
  exchange、provider 所有の usage endpoint を必要とするためです。
- OpenAI Codex は `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth`, `augmentModelCatalog`
  に加えて `prepareExtraParams`, `resolveUsageAuth`, `fetchUsageSnapshot`
  を使います。core OpenAI transports 上で動作しつつも、
  transport/base URL の正規化、OAuth refresh fallback policy、default transport choice、
  synthetic Codex catalog rows、ChatGPT usage endpoint integration を所有するためです。
  direct OpenAI と同じ `openai-responses-defaults` stream family を共有します。
- Google AI Studio と Gemini CLI OAuth は `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn`, `isModernModelRef` を使います。
  これは `google-gemini` replay family が Gemini 3.1 の forward-compat fallback、
  native Gemini replay validation、bootstrap replay sanitation、tagged
  reasoning-output mode、modern-model matching を所有し、
  `google-thinking` stream family が Gemini thinking payload normalization を所有するためです。
  Gemini CLI OAuth はさらに token formatting、token parsing、quota endpoint
  wiring のために `formatApiKey`, `resolveUsageAuth`, `fetchUsageSnapshot` も使います。
- Anthropic Vertex は `anthropic-by-model` replay family を通じて
  `buildReplayPolicy` を使います。これにより Claude 固有 replay cleanup が
  `anthropic-messages` transport 全体ではなく Claude ids のみに限定されます。
- Amazon Bedrock は `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `resolveDefaultThinkingLevel` を使います。
  これは Anthropic-on-Bedrock traffic に対する Bedrock 固有の
  throttle/not-ready/context-overflow error classification を所有するためです。
  その replay policy は引き続き Claude 専用の `anthropic-by-model` guard を共有します。
- OpenRouter、Kilocode、Opencode、Opencode Go は
  `passthrough-gemini` replay family を通じて `buildReplayPolicy` を使います。
  Gemini models を OpenAI-compatible transports 経由で proxy し、
  native Gemini replay validation や bootstrap rewrites なしで Gemini の
  thought-signature sanitation を必要とするためです。
- MiniMax は `hybrid-anthropic-openai` replay family を通じて
  `buildReplayPolicy` を使います。1 つの provider が Anthropic-message と
  OpenAI-compatible の両方の semantics を所有するためです。Anthropic 側では Claude 専用の
  thinking-block dropping を維持しつつ、reasoning output mode は native に戻し、
  `minimax-fast-mode` stream family は共有 stream path 上の fast-mode model rewrites を所有します。
- Moonshot は `catalog` と `wrapStreamFn` を使います。共有 OpenAI transport を使用しつつも、
  provider 所有の thinking payload normalization が必要なためです。
  `moonshot-thinking` stream family は config と `/think` state を native な
  binary thinking payload にマップします。
- Kilocode は `catalog`, `capabilities`, `wrapStreamFn`,
  `isCacheTtlEligible` を使います。provider 所有の request headers、
  reasoning payload normalization、Gemini transcript hints、Anthropic
  cache-TTL gating を必要とするためです。`kilocode-thinking` stream family は
  `kilo/auto` や、明示的 reasoning payloads をサポートしない他の proxy model ids を
  スキップしつつ、共有 proxy stream path 上で Kilo thinking injection を保ちます。
- Z.AI は `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth`, `fetchUsageSnapshot` を使います。GLM-5 fallback、
  `tool_stream` defaults、binary thinking UX、modern-model matching、
  usage auth と quota fetching の両方を所有するためです。
  `tool-stream-default-on` stream family は、default-on の `tool_stream` wrapper を
  provider ごとの手書き glue から切り離します。
- xAI は `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel`, `isModernModelRef`
  を使います。native xAI Responses transport normalization、Grok fast-mode
  alias rewrites、default `tool_stream`、strict-tool / reasoning-payload
  cleanup、plugin 所有 tools 向け fallback auth reuse、forward-compat Grok
  model resolution、xAI tool-schema profile、unsupported schema keywords、
  native `web_search`、HTML-entity の tool-call argument decoding などの
  provider 所有 compat patches を所有するためです。
- Mistral、OpenCode Zen、OpenCode Go は `capabilities` のみを使い、
  transcript/tooling quirks を core から切り離します。
- `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway`, `volcengine`
  のような catalog-only bundled providers は `catalog` のみを使います。
- Qwen は text provider 向けに `catalog` を使用し、
  multimodal surfaces 向けに shared media-understanding と
  video-generation registrations も持ちます。
- MiniMax と Xiaomi は `catalog` に加えて usage hooks も使います。
  inference は shared transports を通る一方で、`/usage` behavior は plugin 所有であるためです。

## ランタイムヘルパー

plugins は `api.runtime` を通じて選択された core helpers にアクセスできます。TTS の場合:

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

注記:

- `textToSpeech` は、file/voice-note surfaces 向けの通常の core TTS output payload を返します。
- core の `messages.tts` configuration と provider selection を使用します。
- PCM audio buffer + sample rate を返します。plugins 側で provider 向けに resample/encode する必要があります。
- `listVoices` は provider ごとに任意です。vendor 所有 voice pickers や setup flows に使用してください。
- voice listings には、provider-aware pickers 向けに locale、gender、personality tags などのより豊富な metadata を含められます。
- telephony は現在 OpenAI と ElevenLabs がサポートしています。Microsoft は未対応です。

plugins は `api.registerSpeechProvider(...)` を通じて speech providers も登録できます。

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

注記:

- TTS policy、fallback、reply delivery は core に残してください。
- vendor 所有の synthesis behavior には speech providers を使ってください。
- レガシーな Microsoft `edge` input は `microsoft` provider id に正規化されます。
- 推奨される所有権モデルは company 指向です。OpenClaw が capability
  contract を追加していく中で、1 つの vendor plugin が text、speech、image、
  将来の media providers を所有できます。

image/audio/video understanding に対しては、plugins は generic な key/value bag
ではなく、1 つの型付き media-understanding provider を登録します。

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

注記:

- orchestration、fallback、config、channel wiring は core に残してください。
- vendor behavior は provider plugin 内に保ってください。
- 追加拡張は型付きのままにしてください。新しい optional methods、新しい optional
  result fields、新しい optional capabilities。
- video generation もすでに同じパターンに従っています。
  - core が capability contract と runtime helper を所有する
  - vendor plugins が `api.registerVideoGenerationProvider(...)` を登録する
  - feature/channel plugins が `api.runtime.videoGeneration.*` を消費する

media-understanding の runtime helpers として、plugins は次を呼び出せます。

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

audio transcription には、plugins は media-understanding runtime または
古い STT alias のどちらも使えます。

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // MIME を確実に推定できない場合は任意:
  mime: "audio/ogg",
});
```

注記:

- `api.runtime.mediaUnderstanding.*` は image/audio/video understanding に対する推奨共有 surface です。
- core の media-understanding audio configuration（`tools.media.audio`）と provider fallback order を使用します。
- transcription output が生成されない場合（例: skipped/unsupported input）は `{ text: undefined }` を返します。
- `api.runtime.stt.transcribeAudioFile(...)` は互換 alias として残ります。

plugins は `api.runtime.subagent` を通じて background subagent runs も起動できます。

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

注記:

- `provider` と `model` は run ごとの任意の override であり、永続的な session 変更ではありません。
- OpenClaw は、信頼された callers に対してのみこれらの override fields を尊重します。
- plugin 所有の fallback runs に対しては、operator は `plugins.entries.<id>.subagent.allowModelOverride: true` でオプトインする必要があります。
- trusted plugins を特定の canonical `provider/model` targets に制限するには
  `plugins.entries.<id>.subagent.allowedModels` を使用し、任意 target を明示許可する場合は `"*"` を使います。
- 信頼されていない plugin subagent runs も動作しますが、override requests は静かに fallback されるのではなく拒否されます。

web search については、plugins は agent tool wiring に入り込む代わりに
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

plugins は `api.registerWebSearchProvider(...)` を通じて web-search providers を登録することもできます。

注記:

- provider selection、credential resolution、shared request semantics は core に保ってください。
- vendor 固有 search transports には web-search providers を使用してください。
- `api.runtime.webSearch.*` は、agent tool wrapper に依存せず search behavior を必要とする feature/channel plugins 向けの推奨共有 surface です。

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

- `generate(...)`: 設定済みの image-generation provider chain を使用して画像を生成する
- `listProviders(...)`: 利用可能な image-generation providers とその capabilities を一覧表示する

## Gateway HTTP routes

plugins は `api.registerHttpRoute(...)` を使って HTTP endpoints を公開できます。

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

route fields:

- `path`: gateway HTTP server 配下の route path
- `auth`: 必須。通常の gateway auth を要求するには `"gateway"`、plugin 管理の auth/webhook verification には `"plugin"` を使用します。
- `match`: 任意。`"exact"`（デフォルト）または `"prefix"`。
- `replaceExisting`: 任意。同じ plugin が自分自身の既存 route registration を置き換えることを許可します。
- `handler`: route が request を処理した場合は `true` を返します。

注記:

- `api.registerHttpHandler(...)` は削除されており、plugin-load error になります。代わりに `api.registerHttpRoute(...)` を使用してください。
- plugin routes は `auth` を明示的に宣言しなければなりません。
- 完全一致する `path + match` の衝突は `replaceExisting: true` でない限り拒否され、ある plugin が別 plugin の route を置き換えることはできません。
- 異なる `auth` レベルを持つ重複 route は拒否されます。`exact`/`prefix` の fallthrough chain は同じ auth レベル内に保ってください。
- `auth: "plugin"` routes は operator runtime scopes を自動的には受け取りません。これは privileged Gateway helper calls ではなく、plugin 管理の webhooks/signature verification のためのものです。
- `auth: "gateway"` routes は Gateway request runtime scope 内で実行されますが、その scope は意図的に保守的です。
  - shared-secret bearer auth（`gateway.auth.mode = "token"` / `"password"`）では、caller が `x-openclaw-scopes` を送っても、plugin-route runtime scopes は `operator.write` に固定されます
  - trusted identity-bearing HTTP modes（例: `trusted-proxy` や private ingress 上の `gateway.auth.mode = "none"`）では、`x-openclaw-scopes` header が明示的に存在する場合にのみそれを尊重します
  - それらの identity-bearing plugin-route requests で `x-openclaw-scopes` が存在しない場合、runtime scope は `operator.write` にフォールバックします
- 実践ルール: gateway-auth plugin route を暗黙の admin surface だと想定しないでください。route に admin-only behavior が必要な場合は、identity-bearing auth mode を要求し、明示的な `x-openclaw-scopes` header contract を文書化してください。

## Plugin SDK import paths

plugin を作成するときは、巨大な `openclaw/plugin-sdk` import ではなく、
SDK subpaths を使ってください。

- plugin 登録 primitives には `openclaw/plugin-sdk/plugin-entry`
- generic shared plugin-facing contract には `openclaw/plugin-sdk/core`
- root `openclaw.json` Zod schema export（`OpenClawSchema`）には `openclaw/plugin-sdk/config-schema`
- 共有 setup/auth/reply/webhook
  wiring には、`openclaw/plugin-sdk/channel-setup`,
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
  `openclaw/plugin-sdk/secret-input`,
  `openclaw/plugin-sdk/webhook-ingress` のような stable channel primitives を使用します。
  `channel-inbound` は debounce、mention matching、
  envelope formatting、inbound envelope context helpers の共有ホームです。
  `channel-setup` は狭い optional-install setup seam です。
  `setup-runtime` は `setupEntry` /
  deferred startup で使われる runtime-safe setup surface であり、
  import-safe な setup patch adapters を含みます。
  `setup-adapter-runtime` は env-aware account-setup adapter seam です。
  `setup-tools` は小さな CLI/archive/docs helper seam
  （`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`）です。
- 共有 runtime/config helpers には、
  `openclaw/plugin-sdk/channel-config-helpers`,
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
  `openclaw/plugin-sdk/runtime-store`,
  `openclaw/plugin-sdk/directory-runtime` のような domain subpaths を使用します。
  `telegram-command-config` は Telegram custom
  command normalization/validation 向けの狭い public seam であり、
  bundled Telegram contract surface が一時的に利用できない場合でも利用可能です。
  `text-runtime` は shared text/markdown/logging seam であり、
  assistant-visible-text stripping、markdown render/chunking helpers、redaction
  helpers、directive-tag helpers、安全な text utilities を含みます。
- approval 固有の channel seams は、plugin 上の 1 つの `approvalCapability`
  contract を優先すべきです。これにより core は、approval behavior を無関係な plugin fields に混在させず、
  auth、delivery、render、native-routing behavior をその 1 つの capability を通じて読み取れます。
- `openclaw/plugin-sdk/channel-runtime` は非推奨であり、古い plugins 用の互換 shim としてのみ残っています。新しい code はより狭い generic primitives を import し、repo code でもこの shim の新規 import を追加しないでください。
- bundled extension internals は private のままです。外部 plugins は
  `openclaw/plugin-sdk/*` subpaths のみを使用してください。OpenClaw core/test code は、
  `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js`, `login-qr-api.js` のような plugin package root 配下の
  repo public entry points を使ってよく、plugin package の
  `src/*` を core や別 extension から import してはいけません。
- Repo entry point の分割:
  `<plugin-package-root>/api.js` は helper/types barrel、
  `<plugin-package-root>/runtime-api.js` は runtime-only barrel、
  `<plugin-package-root>/index.js` は bundled plugin entry、
  `<plugin-package-root>/setup-entry.js` は setup plugin entry です。
- 現在の bundled provider examples:
  - Anthropic は `api.js` / `contract-api.js` を、`wrapAnthropicProviderStream`、
    beta-header helpers、`service_tier`
    parsing のような Claude stream helpers に使います。
  - OpenAI は provider builders、default-model helpers、
    realtime provider builders のために `api.js` を使います。
  - OpenRouter は provider builder に加え onboarding/config
    helpers のために `api.js` を使い、`register.runtime.js` は
    repo-local use のために generic `plugin-sdk/provider-stream` helpers を引き続き re-export できます。
- facade-loaded public entry points は、アクティブな runtime config snapshot がある場合はそれを優先し、
  OpenClaw がまだ runtime snapshot を提供していないときはディスク上の解決済み config file にフォールバックします。
- generic shared primitives は引き続き推奨 public SDK contract です。bundled channel-branded helper seams の
  小さな予約済み互換セットはまだ存在します。これらは新しいサードパーティ import targets ではなく、
  bundled-maintenance/compatibility seams として扱ってください。新しい cross-channel contracts は引き続き
  generic `plugin-sdk/*` subpaths または plugin-local `api.js` /
  `runtime-api.js` barrels に置くべきです。

互換性に関する注記:

- 新しい code では root の `openclaw/plugin-sdk` barrel を避けてください。
- まず狭く安定した primitives を優先してください。新しい
  setup/pairing/reply/feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool subpaths は、新しい bundled および外部 plugin 作業向けの意図された contract です。
  Target parsing/matching は `openclaw/plugin-sdk/channel-targets` に置きます。
  Message action gates と reaction message-id helpers は
  `openclaw/plugin-sdk/channel-actions` に置きます。
- bundled extension 固有 helper barrels は、デフォルトでは stable ではありません。
  helper が bundled extension にしか必要ないなら、
  `openclaw/plugin-sdk/<extension>` に昇格させるのではなく、その extension のローカル
  `api.js` または `runtime-api.js` seam の背後に置いてください。
- 新しい shared helper seams は channel-branded ではなく generic であるべきです。共有 target
  parsing は `openclaw/plugin-sdk/channel-targets` に属し、channel 固有 internals は
  所有 plugin のローカル `api.js` または `runtime-api.js` seam の背後に残します。
- `image-generation`,
  `media-understanding`, `speech` のような capability-specific subpaths は、
  bundled/native plugins が今日それらを使用しているため存在します。それが存在するからといって、
  export されているすべての helper が長期固定の外部 contract であることを意味するわけではありません。

## Message tool schemas

plugins は channel 固有の `describeMessageTool(...)` schema
contributions を所有すべきです。provider 固有 fields は共有 core ではなく plugin 内に保ってください。

共有して持ち運べる schema fragments には、
`openclaw/plugin-sdk/channel-actions` から export される generic helpers を再利用してください。

- button-grid style payloads には `createMessageToolButtonsSchema()`
- structured card payloads には `createMessageToolCardSchema()`

schema shape が 1 つの provider にしか意味を持たない場合は、共有 SDK に昇格させるのではなく、
その plugin 自身の source 内で定義してください。

## Channel target resolution

channel plugins は channel 固有の target semantics を所有すべきです。
共有 outbound host は generic に保ち、provider ルールは messaging adapter
surface を使ってください。

- `messaging.inferTargetChatType({ to })` は、directory lookup 前に
  正規化された target を `direct`, `group`, `channel` のどれとして扱うかを決定します。
- `messaging.targetResolver.looksLikeId(raw, normalized)` は、directory search ではなく
  id-like resolution に直接進むべき入力かどうかを core に伝えます。
- `messaging.targetResolver.resolveTarget(...)` は、正規化後または
  directory miss 後に最終的な provider 所有 resolution が必要なときの plugin fallback です。
- `messaging.resolveOutboundSessionRoute(...)` は、target が解決された後の
  provider 固有 session route construction を所有します。

推奨される分割:

- peers/groups の search 前に起こるべきカテゴリ判定には `inferTargetChatType` を使う
- 「これを明示的/native target id として扱う」判定には `looksLikeId` を使う
- `resolveTarget` は broad directory search ではなく、provider 固有の normalization fallback に使う
- chat ids、thread ids、JIDs、handles、room ids のような provider-native ids は、
  generic SDK fields ではなく `target` values または provider 固有 params の中に保つ

## Config-backed directories

config から directory entries を導出する plugins は、そのロジックを plugin 内に保ち、
`openclaw/plugin-sdk/directory-runtime` の共有 helpers を再利用すべきです。

これは、channel が以下のような config-backed peers/groups を必要とする場合に使用します。

- allowlist 駆動の DM peers
- 設定済みの channel/group maps
- account-scoped の静的 directory fallbacks

`directory-runtime` の共有 helpers は generic operations のみを扱います。

- query filtering
- limit application
- deduping/normalization helpers
- `ChannelDirectoryEntry[]` の構築

channel 固有の account inspection と id normalization は、
plugin 実装側に残すべきです。

## Provider catalogs

provider plugins は `registerProvider({ catalog: { run(...) { ... } } })` を使って、
推論用の model catalogs を定義できます。

`catalog.run(...)` は、OpenClaw が `models.providers` に書き込むのと同じ shape を返します。

- 1 つの provider entry に対しては `{ provider }`
- 複数の provider entries に対しては `{ providers }`

provider 固有の model ids、base URL defaults、または auth-gated model metadata を
plugin が所有する場合は `catalog` を使用してください。

`catalog.order` は、plugin の catalog が OpenClaw の組み込み implicit providers に対して
どのタイミングで merge されるかを制御します。

- `simple`: plain API-key または env-driven providers
- `profile`: auth profiles が存在するときに現れる providers
- `paired`: 複数の関連 provider entries を synthetic に生成する providers
- `late`: 最後のパス。他の implicit providers の後

後の providers が key collision で勝つため、plugins は
同じ provider id を持つ built-in provider entry を意図的に上書きできます。

互換性:

- `discovery` はレガシー別名として引き続き動作します
- `catalog` と `discovery` の両方が登録されている場合、OpenClaw は `catalog` を使用します

## 読み取り専用の channel inspection

plugin が channel を登録する場合、`resolveAccount(...)` とあわせて
`plugin.config.inspectAccount(cfg, accountId)` の実装を優先してください。

理由:

- `resolveAccount(...)` はランタイムパスです。credentials が完全に materialize されている前提を持ち、
  必要な secrets がない場合に即座に失敗してよいものです。
- `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve`、および doctor/config
  repair flows のような読み取り専用 command paths は、設定を説明するだけのために
  runtime credentials を materialize する必要があってはなりません。

推奨される `inspectAccount(...)` の動作:

- 記述的な account state のみを返す
- `enabled` と `configured` を保持する
- relevant な場合は credential source/status fields を含める。例:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- 読み取り専用の可用性を報告するだけなら raw token values を返す必要はありません。
  `tokenStatus: "available"`（および対応する source field）を返せば十分です。
- SecretRef 経由で credential が設定されているが現在の command path では利用できない場合は、
  `configured_unavailable` を使用します。

これにより、読み取り専用 commands はクラッシュしたり account を未設定と誤報する代わりに、
「設定されているが、この command path では利用できない」と報告できます。

## Package packs

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

各 entry は 1 つの plugin になります。pack に複数 extension が列挙されている場合、
plugin id は `name/<fileBase>` になります。

plugin が npm deps を import する場合は、その directory 内に
`node_modules` が使えるよう依存関係をインストールしてください（`npm install` / `pnpm install`）。

セキュリティガードレール: すべての `openclaw.extensions` entry は、symlink 解決後も
plugin directory 内に留まらなければなりません。package directory を脱出する
entries は拒否されます。

セキュリティに関する注記: `openclaw plugins install` は plugin dependencies を
`npm install --omit=dev --ignore-scripts` でインストールします
（lifecycle scripts なし、本番時に dev dependencies なし）。plugin dependency
trees は「pure JS/TS」に保ち、`postinstall` builds を要求する package は避けてください。

任意: `openclaw.setupEntry` は軽量な setup-only module を指せます。
OpenClaw が無効な channel plugin の setup surfaces を必要とする場合、または
channel plugin が有効だが未設定の場合、完全な plugin entry の代わりに `setupEntry` をロードします。
これにより、メイン plugin entry が tools、hooks、その他 runtime-only
code を配線していても、起動と setup を軽く保てます。

任意: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
を使うと、channel plugin は gateway の pre-listen startup
phase 中、channel がすでに設定済みでも、同じ `setupEntry` path に opt-in できます。

これは、gateway が listen を開始する前に存在しなければならない startup
surface を `setupEntry` が完全にカバーしている場合にのみ使用してください。
実際には、setup entry は startup が依存する
channel 所有 capability をすべて登録する必要があります。たとえば:

- channel registration 自体
- gateway が listen を開始する前に利用可能でなければならない HTTP routes
- 同じ window 中に存在しなければならない gateway methods、tools、services

full entry が依然として何らかの必要 startup capability を所有しているなら、
この flag を有効にしないでください。デフォルト動作のままにして、OpenClaw に起動中に
full entry をロードさせてください。

bundled channels は、full channel runtime がロードされる前に core が参照できる
setup-only contract-surface helpers を公開することもできます。現在の setup
promotion surface は次のとおりです。

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Core は、full plugin entry をロードせずに legacy single-account channel
config を `channels.<id>.accounts.*` に昇格する必要があるとき、この surface を使います。
現在の bundled の例は Matrix です。named accounts がすでに存在する場合、
auth/bootstrap keys のみを named promoted account に移動し、
常に `accounts.default` を作るのではなく、設定済みの非 canonical default-account
key を保持できます。

これらの setup patch adapters は、bundled contract-surface discovery を lazy に保ちます。
import 時間は軽いままで、promotion surface は module import 時に bundled channel startup に
再突入する代わりに、最初の使用時にのみロードされます。

それらの startup surfaces に gateway RPC methods が含まれる場合は、
plugin 固有 prefix に置いてください。Core admin namespaces（`config.*`,
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

channel plugins は `openclaw.channel` によって setup/discovery metadata を、
`openclaw.install` によって install hints を広告できます。これにより core に catalog data を
持たせずに済みます。

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

- `detailLabel`: より豊かな catalog/status surfaces 向けの副ラベル
- `docsLabel`: docs link のリンクテキストを上書きする
- `preferOver`: この catalog entry が優先して上回るべき低優先度 plugin/channel ids
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: selection-surface 用 copy controls
- `markdownCapable`: outbound formatting decisions のため、その channel が markdown 対応であることを示す
- `exposure.configured`: `false` の場合、configured-channel listing surfaces からその channel を隠す
- `exposure.setup`: `false` の場合、interactive setup/configure pickers からその channel を隠す
- `exposure.docs`: docs navigation surfaces に対してその channel を internal/private としてマークする
- `showConfigured` / `showInSetup`: 互換性のため引き続き受け付けられるレガシー別名。`exposure` を優先してください
- `quickstartAllowFrom`: 標準 quickstart `allowFrom` flow にその channel を opt-in する
- `forceAccountBinding`: account が 1 つしかない場合でも明示的な account binding を必須にする
- `preferSessionLookupForAnnounceTarget`: announce target 解決時に session lookup を優先する

OpenClaw は **外部 channel catalogs**（例: MPM
registry export）も merge できます。以下のいずれかに JSON file を置いてください。

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

または `OPENCLAW_PLUGIN_CATALOG_PATHS`（または `OPENCLAW_MPM_CATALOG_PATHS`）で、
1 つ以上の JSON files を指定します（comma/semicolon/`PATH` 区切り）。各 file は
`{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`
を含むべきです。parser は `"entries"` key のレガシー別名として `"packages"` または `"plugins"` も受け付けます。

## Context engine plugins

context engine plugins は、ingest、assembly、compaction に対する session context
orchestration を所有します。plugin から
`api.registerContextEngine(id, factory)` で登録し、アクティブな engine は
`plugins.slots.contextEngine` で選択します。

これは、default context
pipeline を単に memory search や hooks で拡張するのではなく、置き換えるまたは拡張する必要がある場合に使います。

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

engine が compaction algorithm を**所有しない**場合でも、`compact()`
は実装したうえで、明示的に委譲してください。

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

plugin が現在の API に収まらない動作を必要とする場合、private reach-in で
plugin システムを回避しないでください。不足している capability を追加してください。

推奨される順序:

1. core contract を定義する
   core が所有すべき共有動作を決めます。policy、fallback、config merge、
   lifecycle、channel-facing semantics、runtime helper shape。
2. 型付きの plugin registration/runtime surfaces を追加する
   `OpenClawPluginApi` および/または `api.runtime` を、最小限で有用な
   型付き capability surface で拡張します。
3. core + channel/feature consumers を配線する
   channels と feature plugins は、新しい capability を core 経由で消費し、
   vendor 実装を直接 import しないようにします。
4. vendor implementations を登録する
   vendor plugins がその capability に対して backends を登録します。
5. contract coverage を追加する
   所有権と registration shape が時間とともに明確に保たれるよう tests を追加します。

これにより、OpenClaw はある provider の worldview にハードコードされることなく、
意見を持ったままでいられます。具体的な file チェックリストと worked example については
[Capability Cookbook](/ja-JP/plugins/architecture) を参照してください。

### Capability チェックリスト

新しい capability を追加するとき、実装は通常次の surface 群をまとめて触れるべきです。

- `src/<capability>/types.ts` の core contract types
- `src/<capability>/runtime.ts` の core runner/runtime helper
- `src/plugins/types.ts` の plugin API registration surface
- `src/plugins/registry.ts` の plugin registry wiring
- feature/channel
  plugins が消費する必要がある場合の `src/plugins/runtime/*` における plugin runtime exposure
- `src/test-utils/plugin-registration.ts` の capture/test helpers
- `src/plugins/contracts/registry.ts` の ownership/contract assertions
- `docs/` の operator/plugin docs

これらのいずれかの surface が欠けている場合、それは通常その capability が
まだ完全には統合されていない兆候です。

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

// feature/channel plugins 用の共有 runtime helper
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

contract test パターン:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

これによりルールは単純になります。

- core が capability contract + orchestration を所有する
- vendor plugins が vendor implementations を所有する
- feature/channel plugins が runtime helpers を消費する
- contract tests が所有権を明示的に保つ
