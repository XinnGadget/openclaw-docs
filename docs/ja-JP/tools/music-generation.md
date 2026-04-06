---
read_when:
    - agent 経由で音楽や音声を生成する
    - 音楽生成プロバイダーとモデルを設定する
    - '`music_generate` ツールのパラメーターを理解する'
summary: 共有プロバイダー（ワークフロー駆動プラグインを含む）で音楽を生成する
title: 音楽生成
x-i18n:
    generated_at: "2026-04-06T03:14:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: a03de8aa75cfb7248eb0c1d969fb2a6da06117967d097e6f6e95771d0f017ae1
    source_path: tools/music-generation.md
    workflow: 15
---

# 音楽生成

`music_generate` ツールを使うと、agent は Google、
MiniMax、およびワークフロー設定された ComfyUI など、設定済みプロバイダーの共有音楽生成機能を通じて
音楽や音声を作成できます。

共有プロバイダーバックの agent session では、OpenClaw は音楽生成を
バックグラウンドタスクとして開始し、task ledger で追跡し、その後
トラックの準備ができた時点で agent を再度起こして、完成した音声を元の
channel に投稿できるようにします。

<Note>
組み込みの共有ツールは、少なくとも 1 つの音楽生成プロバイダーが利用可能な場合にのみ表示されます。agent のツールに `music_generate` が表示されない場合は、`agents.defaults.musicGenerationModel` を設定するか、プロバイダーの API key を設定してください。
</Note>

## クイックスタート

### 共有プロバイダーバックの生成

1. 少なくとも 1 つのプロバイダーに API key を設定します。たとえば `GEMINI_API_KEY` または
   `MINIMAX_API_KEY`。
2. 必要に応じて、好みのモデルを設定します:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

3. agent にこう依頼します: _「ネオンの街を夜にドライブする情景について、アップビートな synthpop トラックを生成して。」_

agent は自動で `music_generate` を呼び出します。ツールの allow-list 指定は不要です。

session-backed agent run を伴わない直接の同期コンテキストでは、組み込み
ツールは引き続きインライン生成にフォールバックし、最終メディアパスをツール結果で返します。

プロンプト例:

```text
Generate a cinematic piano track with soft strings and no vocals.
```

```text
Generate an energetic chiptune loop about launching a rocket at sunrise.
```

### ワークフロー駆動の Comfy 生成

bundled の `comfy` プラグインは、音楽生成プロバイダーレジストリを通じて、
共有の `music_generate` ツールに接続されます。

1. `models.providers.comfy.music` に workflow JSON と
   prompt/output nodes を設定します。
2. Comfy Cloud を使う場合は、`COMFY_API_KEY` または `COMFY_CLOUD_API_KEY` を設定します。
3. agent に音楽生成を依頼するか、ツールを直接呼び出します。

例:

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

## 共有の bundled provider サポート

| Provider | デフォルトモデル       | 参照入力         | サポートされる制御                                        | API key                                |
| -------- | ---------------------- | ---------------- | --------------------------------------------------------- | -------------------------------------- |
| ComfyUI  | `workflow`             | 最大 1 枚の画像  | ワークフロー定義の音楽または音声                          | `COMFY_API_KEY`, `COMFY_CLOUD_API_KEY` |
| Google   | `lyria-3-clip-preview` | 最大 10 枚の画像 | `lyrics`, `instrumental`, `format`                        | `GEMINI_API_KEY`, `GOOGLE_API_KEY`     |
| MiniMax  | `music-2.5+`           | なし             | `lyrics`, `instrumental`, `durationSeconds`, `format=mp3` | `MINIMAX_API_KEY`                      |

実行時に利用可能な共有プロバイダーとモデルを確認するには、
`action: "list"` を使ってください:

```text
/tool music_generate action=list
```

現在の session-backed 音楽タスクを確認するには、
`action: "status"` を使ってください:

```text
/tool music_generate action=status
```

直接生成の例:

```text
/tool music_generate prompt="Dreamy lo-fi hip hop with vinyl texture and gentle rain" instrumental=true
```

## 組み込みツールのパラメーター

| パラメーター      | 型       | 説明                                                                                          |
| ----------------- | -------- | --------------------------------------------------------------------------------------------- |
| `prompt`          | string   | 音楽生成プロンプト（`action: "generate"` のとき必須）                                         |
| `action`          | string   | `"generate"`（デフォルト）、現在の session task 用の `"status"`、またはプロバイダー確認用の `"list"` |
| `model`           | string   | プロバイダー/モデルの override。例: `google/lyria-3-pro-preview` または `comfy/workflow`      |
| `lyrics`          | string   | プロバイダーが明示的な lyric 入力をサポートする場合の任意の歌詞                              |
| `instrumental`    | boolean  | プロバイダーがサポートする場合、インストゥルメンタルのみの出力を要求                         |
| `image`           | string   | 単一の参照画像パスまたは URL                                                                  |
| `images`          | string[] | 複数の参照画像（最大 10 枚）                                                                  |
| `durationSeconds` | number   | プロバイダーが長さのヒントをサポートする場合の目標秒数                                       |
| `format`          | string   | プロバイダーがサポートする場合の出力形式ヒント（`mp3` または `wav`）                         |
| `filename`        | string   | 出力ファイル名のヒント                                                                        |

すべてのプロバイダーがすべてのパラメーターをサポートするわけではありません。OpenClaw は、
送信前に入力数のような厳密な上限を検証しますが、選択されたプロバイダーまたはモデルで
反映できない未対応の任意ヒントは、警告付きで無視されます。

## 共有プロバイダーバック経路の非同期動作

- session-backed agent runs: `music_generate` はバックグラウンドタスクを作成し、started/task response をすぐ返し、完成したトラックは後続の agent message で後から投稿します。
- 重複防止: そのバックグラウンドタスクがまだ `queued` または `running` の間は、同じ session で後から行われた `music_generate` 呼び出しは、新しい生成を始めず task status を返します。
- ステータス確認: 新しい生成を開始せずに、現在の session-backed 音楽タスクを確認するには `action: "status"` を使ってください。
- タスク追跡: 生成の queued、running、terminal status を確認するには `openclaw tasks list` または `openclaw tasks show <taskId>` を使ってください。
- 完了 wake: OpenClaw は同じ session に内部完了イベントを注入し、model がユーザー向けの後続メッセージを自分で書けるようにします。
- プロンプトヒント: 同じ session で後の user/manual turns が行われた際、すでに音楽タスクが進行中なら、小さなランタイムヒントが付くため、model はやみくもに `music_generate` を再度呼び出しません。
- no-session fallback: 実際の agent session を伴わない direct/local contexts では、引き続きインライン実行され、同じ turn 内で最終音声結果を返します。

## 設定

### モデル選択

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
        fallbacks: ["minimax/music-2.5+"],
      },
    },
  },
}
```

### プロバイダー選択順序

音楽生成時、OpenClaw は次の順でプロバイダーを試します:

1. agent が指定した場合は、ツール呼び出しの `model` パラメーター
2. config の `musicGenerationModel.primary`
3. `musicGenerationModel.fallbacks` を順番に
4. auth-backed provider defaults のみを使った自動検出:
   - 現在の default provider を最初に
   - 残りの登録済み音楽生成プロバイダーを provider-id 順に

あるプロバイダーが失敗すると、次の候補が自動で試されます。すべて失敗した場合、
エラーには各試行の詳細が含まれます。

## プロバイダーに関する注意

- Google は Lyria 3 のバッチ生成を使います。現在の bundled フローでは
  prompt、任意の lyrics text、任意の reference images をサポートします。
- MiniMax はバッチの `music_generation` endpoint を使います。現在の bundled フローでは
  prompt、任意の lyrics、instrumental mode、duration steering、および
  mp3 出力をサポートします。
- ComfyUI サポートはワークフロー駆動であり、設定された graph と
  prompt/output fields の node mapping に依存します。

## 適切な経路の選び方

- モデル選択、provider failover、組み込みの async task/status flow が必要な場合は、共有プロバイダーバック経路を使ってください。
- カスタム workflow graph や、共有 bundled 音楽機能に含まれない provider が必要な場合は、ComfyUI のような plugin path を使ってください。
- ComfyUI 固有の動作をデバッグしている場合は [ComfyUI](/providers/comfy) を参照してください。共有プロバイダーの動作をデバッグしている場合は、まず [Google (Gemini)](/ja-JP/providers/google) または [MiniMax](/ja-JP/providers/minimax) から始めてください。

## Live tests

共有 bundled providers 向けの opt-in live coverage:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts
```

bundled ComfyUI 音楽経路向けの opt-in live coverage:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

Comfy の live file は、それらのセクションが設定されている場合、
comfy の image と video workflows もカバーします。

## 関連

- [Background Tasks](/ja-JP/automation/tasks) - 分離された `music_generate` 実行の task tracking
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults) - `musicGenerationModel` 設定
- [ComfyUI](/providers/comfy)
- [Google (Gemini)](/ja-JP/providers/google)
- [MiniMax](/ja-JP/providers/minimax)
- [Models](/ja-JP/concepts/models) - モデル設定と failover
- [Tools Overview](/ja-JP/tools)
