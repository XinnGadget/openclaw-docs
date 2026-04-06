---
read_when:
    - OpenClaw で MiniMax モデルを使いたい
    - MiniMax のセットアップガイダンスが必要である
summary: OpenClaw で MiniMax モデルを使用する
title: MiniMax
x-i18n:
    generated_at: "2026-04-06T03:12:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ca35c43cdde53f6f09d9e12d48ce09e4c099cf8cbe1407ac6dbb45b1422507e
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

OpenClaw の MiniMax プロバイダーは、デフォルトで **MiniMax M2.7** を使用します。

MiniMax はさらに次も提供します。

- T2A v2 によるバンドル済み音声合成
- `MiniMax-VL-01` によるバンドル済み画像理解
- `music-2.5+` によるバンドル済み音楽生成
- MiniMax Coding Plan 検索 API を通じた、バンドル済み `web_search`

プロバイダーの分割:

- `minimax`: APIキーのテキストプロバイダー。加えて、バンドル済みの画像生成、画像理解、音声、web search
- `minimax-portal`: OAuth のテキストプロバイダー。加えて、バンドル済みの画像生成と画像理解

## モデルラインアップ

- `MiniMax-M2.7`: デフォルトのホスト型 reasoning モデル。
- `MiniMax-M2.7-highspeed`: より高速な M2.7 reasoning tier。
- `image-01`: 画像生成モデル（生成および image-to-image 編集）。

## 画像生成

MiniMax plugin は、`image_generate` ツール向けに `image-01` モデルを登録します。サポート内容:

- アスペクト比制御付きの **Text-to-image 生成**。
- アスペクト比制御付きの **Image-to-image 編集**（被写体参照）。
- リクエストごとに最大 **9枚** の出力画像。
- 編集リクエストごとに最大 **1枚** の参照画像。
- サポートされるアスペクト比: `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9`。

MiniMax を画像生成に使用するには、画像生成プロバイダーとして設定します。

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

この plugin は、テキストモデルと同じ `MINIMAX_API_KEY` または OAuth 認証を使用します。MiniMax がすでにセットアップ済みであれば、追加設定は不要です。

`minimax` と `minimax-portal` の両方が、同じ
`image-01` モデルで `image_generate` を登録します。APIキー のセットアップは `MINIMAX_API_KEY` を使用し、OAuth のセットアップでは
代わりにバンドル済みの `minimax-portal` 認証経路を使用できます。

オンボーディングまたは APIキー セットアップで明示的な `models.providers.minimax`
エントリが書き込まれると、OpenClaw は `MiniMax-M2.7` と
`MiniMax-M2.7-highspeed` を `input: ["text", "image"]` 付きで具体化します。

組み込みのバンドル済み MiniMax テキストカタログ自体は、その明示的な provider 設定が存在するまでは、テキスト専用メタデータのままです。画像理解は、plugin 所有の `MiniMax-VL-01` メディアプロバイダーを通じて別途公開されます。

共有ツールの
パラメーター、プロバイダー選択、フェイルオーバー動作については [Image Generation](/ja-JP/tools/image-generation) を参照してください。

## 音楽生成

バンドル済みの `minimax` plugin は、共有
`music_generate` ツールを通じて音楽生成も登録します。

- デフォルトの音楽モデル: `minimax/music-2.5+`
- `minimax/music-2.5` と `minimax/music-2.0` もサポート
- プロンプト制御: `lyrics`、`instrumental`、`durationSeconds`
- 出力形式: `mp3`
- セッションに紐づく実行は、`action: "status"` を含む共有タスク/ステータスフローを通じて切り離されます

MiniMax をデフォルトの音楽プロバイダーとして使うには:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "minimax/music-2.5+",
      },
    },
  },
}
```

共有ツールの
パラメーター、プロバイダー選択、フェイルオーバー動作については [Music Generation](/tools/music-generation) を参照してください。

## 動画生成

バンドル済みの `minimax` plugin は、共有
`video_generate` ツールを通じて動画生成も登録します。

- デフォルトの動画モデル: `minimax/MiniMax-Hailuo-2.3`
- モード: text-to-video と単一画像参照フロー
- `aspectRatio` と `resolution` をサポート

MiniMax をデフォルトの動画プロバイダーとして使うには:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "minimax/MiniMax-Hailuo-2.3",
      },
    },
  },
}
```

共有ツールの
パラメーター、プロバイダー選択、フェイルオーバー動作については [Video Generation](/tools/video-generation) を参照してください。

## 画像理解

MiniMax plugin は、テキスト
カタログとは別に画像理解を登録します。

- `minimax`: デフォルトの画像モデル `MiniMax-VL-01`
- `minimax-portal`: デフォルトの画像モデル `MiniMax-VL-01`

このため、自動メディアルーティングでは、バンドル済みテキストプロバイダーカタログが依然としてテキスト専用の M2.7 チャット参照を示していても、MiniMax の画像理解を利用できます。

## Web search

MiniMax plugin は、MiniMax Coding Plan
検索 API を通じて `web_search` も登録します。

- プロバイダー id: `minimax`
- 構造化結果: タイトル、URL、スニペット、関連クエリ
- 推奨 env var: `MINIMAX_CODE_PLAN_KEY`
- 受け付ける env エイリアス: `MINIMAX_CODING_API_KEY`
- 互換性フォールバック: すでに coding-plan token を指している場合の `MINIMAX_API_KEY`
- リージョン再利用: `plugins.entries.minimax.config.webSearch.region`、次に `MINIMAX_API_HOST`、その後 MiniMax provider base URL
- 検索は provider id `minimax` のままです。OAuth CN/global セットアップでも、`models.providers.minimax-portal.baseUrl` を通じて間接的にリージョンを誘導できます

設定は `plugins.entries.minimax.config.webSearch.*` 配下にあります。
詳細は [MiniMax Search](/ja-JP/tools/minimax-search) を参照してください。

## セットアップを選ぶ

### MiniMax OAuth（Coding Plan） - 推奨

**最適な用途:** APIキー 不要で、MiniMax Coding Plan を OAuth ですばやくセットアップ。

明示的なリージョン別 OAuth 選択で認証します。

```bash
openclaw onboard --auth-choice minimax-global-oauth
# or
openclaw onboard --auth-choice minimax-cn-oauth
```

選択の対応:

- `minimax-global-oauth`: 海外ユーザー向け（`api.minimax.io`）
- `minimax-cn-oauth`: 中国のユーザー向け（`api.minimaxi.com`）

詳細は OpenClaw リポジトリ内の MiniMax plugin パッケージ README を参照してください。

### MiniMax M2.7（APIキー）

**最適な用途:** Anthropic 互換 API を備えたホスト型 MiniMax。

CLI で設定します。

- 対話式オンボーディング:

```bash
openclaw onboard --auth-choice minimax-global-api
# or
openclaw onboard --auth-choice minimax-cn-api
```

- `minimax-global-api`: 海外ユーザー向け（`api.minimax.io`）
- `minimax-cn-api`: 中国のユーザー向け（`api.minimaxi.com`）

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "minimax/MiniMax-M2.7" } } },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
          {
            id: "MiniMax-M2.7-highspeed",
            name: "MiniMax M2.7 Highspeed",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.6, output: 2.4, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

Anthropic 互換のストリーミング経路では、OpenClaw は現在、明示的に `thinking` を自分で設定しない限り、MiniMax
thinking をデフォルトで無効化します。MiniMax の
ストリーミングエンドポイントは、ネイティブな Anthropic thinking ブロックではなく、OpenAI 風の delta chunk に `reasoning_content` を出力するため、
暗黙に有効のままだと内部 reasoning が可視出力へ漏れる可能性があります。

### フォールバックとしての MiniMax M2.7（例）

**最適な用途:** 最強の最新世代モデルを primary に保ちつつ、MiniMax M2.7 にフェイルオーバーする。
以下の例では具体的な primary として Opus を使っています。好みの最新世代 primary モデルに置き換えてください。

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "primary" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
    },
  },
}
```

## `openclaw configure` で設定する

対話式設定ウィザードを使って、JSON を編集せずに MiniMax を設定します。

1. `openclaw configure` を実行します。
2. **Model/auth** を選択します。
3. **MiniMax** の認証オプションを選びます。
4. プロンプトが表示されたら、デフォルトモデルを選択します。

現在、ウィザード/CLI にある MiniMax 認証の選択肢:

- `minimax-global-oauth`
- `minimax-cn-oauth`
- `minimax-global-api`
- `minimax-cn-api`

## 設定オプション

- `models.providers.minimax.baseUrl`: `https://api.minimax.io/anthropic`（Anthropic 互換）を推奨。`https://api.minimax.io/v1` は OpenAI 互換 payload 向けの任意設定です。
- `models.providers.minimax.api`: `anthropic-messages` を推奨。`openai-completions` は OpenAI 互換 payload 向けの任意設定です。
- `models.providers.minimax.apiKey`: MiniMax APIキー（`MINIMAX_API_KEY`）。
- `models.providers.minimax.models`: `id`、`name`、`reasoning`、`contextWindow`、`maxTokens`、`cost` を定義します。
- `agents.defaults.models`: allowlist に入れたいモデルへ alias を付けます。
- `models.mode`: 組み込みプロバイダーと並べて MiniMax を追加したい場合は `merge` のままにします。

## 注記

- モデル参照は認証経路に従います:
  - APIキー セットアップ: `minimax/<model>`
  - OAuth セットアップ: `minimax-portal/<model>`
- デフォルトのチャットモデル: `MiniMax-M2.7`
- 代替チャットモデル: `MiniMax-M2.7-highspeed`
- `api: "anthropic-messages"` では、thinking が params/config で
  すでに明示設定されていない限り、OpenClaw は
  `thinking: { type: "disabled" }` を注入します。
- `/fast on` または `params.fastMode: true` は、Anthropic 互換ストリーム経路では `MiniMax-M2.7` を
  `MiniMax-M2.7-highspeed` に書き換えます。
- オンボーディングと直接 APIキー セットアップでは、両方の M2.7 バリアントに対して
  `input: ["text", "image"]` を持つ明示的なモデル定義を書き込みます
- バンドル済み provider カタログは現在、明示的な MiniMax provider 設定が存在するまでは、チャット参照をテキスト専用メタデータとして公開します
- Coding Plan 使用量 API: `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains`（coding plan key が必要）。
- OpenClaw は、MiniMax coding-plan の使用量を、他のプロバイダーと同じ `% left` 表示へ正規化します。MiniMax の生の `usage_percent` / `usagePercent`
  フィールドは消費済みクォータではなく残量クォータなので、OpenClaw はこれを反転します。
  件数ベースのフィールドが存在する場合はそちらが優先されます。API が `model_remains` を返した場合、
  OpenClaw はチャットモデルのエントリを優先し、必要に応じて
  `start_time` / `end_time` から window ラベルを導出し、coding-plan の window を区別しやすくするため
  plan ラベルに選択されたモデル名を含めます。
- 使用量スナップショットは、`minimax`、`minimax-cn`、`minimax-portal` を同じ
  MiniMax クォータサーフェスとして扱い、Coding Plan key env vars にフォールバックする前に保存済みの MiniMax OAuth を優先します。
- 正確なコスト追跡が必要な場合は `models.json` の価格値を更新してください。
- MiniMax Coding Plan の紹介リンク（10%オフ）: [https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
- プロバイダーのルールについては [/concepts/model-providers](/ja-JP/concepts/model-providers) を参照してください。
- 現在の provider id を確認するには `openclaw models list` を使い、その後
  `openclaw models set minimax/MiniMax-M2.7` または
  `openclaw models set minimax-portal/MiniMax-M2.7` で切り替えてください。

## トラブルシューティング

### 「Unknown model: minimax/MiniMax-M2.7」

これは通常、**MiniMax provider が設定されていない**ことを意味します（対応する
provider エントリがなく、MiniMax 認証プロファイル/env key も見つからない）。この検出に対する修正は **2026.1.12** に入っています。次のいずれかで修正してください。

- **2026.1.12** へアップグレードする（またはソースの `main` から実行する）、その後 gateway を再起動する。
- `openclaw configure` を実行して **MiniMax** の認証オプションを選ぶ、または
- 対応する `models.providers.minimax` または
  `models.providers.minimax-portal` ブロックを手動追加する、または
- `MINIMAX_API_KEY`、`MINIMAX_OAUTH_TOKEN`、または MiniMax 認証プロファイルを設定して、
  対応する provider が注入されるようにする。

モデル id は**大文字小文字を区別する**ことを確認してください。

- APIキー 経路: `minimax/MiniMax-M2.7` または `minimax/MiniMax-M2.7-highspeed`
- OAuth 経路: `minimax-portal/MiniMax-M2.7` または
  `minimax-portal/MiniMax-M2.7-highspeed`

その後、次で再確認します。

```bash
openclaw models list
```
