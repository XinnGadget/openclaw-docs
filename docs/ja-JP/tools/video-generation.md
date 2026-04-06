---
read_when:
    - エージェント経由で動画を生成している
    - 動画生成プロバイダーとモデルを設定している
    - video_generate ツールのパラメーターを理解している
summary: 12個のプロバイダーバックエンドを使って、テキスト、画像、既存動画から動画を生成する
title: 動画生成
x-i18n:
    generated_at: "2026-04-06T03:14:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4afec87368232221db1aa5a3980254093d6a961b17271b2dcbf724e6bd455b16
    source_path: tools/video-generation.md
    workflow: 15
---

# 動画生成

OpenClaw エージェントは、テキストプロンプト、参照画像、または既存動画から動画を生成できます。12個のプロバイダーバックエンドがサポートされており、それぞれ異なるモデルオプション、入力モード、機能セットを持っています。エージェントは、設定と利用可能なAPIキーに基づいて適切なプロバイダーを自動的に選択します。

<Note>
`video_generate` ツールは、少なくとも1つの動画生成プロバイダーが利用可能な場合にのみ表示されます。エージェントツールに表示されない場合は、プロバイダーのAPIキーを設定するか、`agents.defaults.videoGenerationModel` を構成してください。
</Note>

## クイックスタート

1. サポートされているいずれかのプロバイダーのAPIキーを設定します:

```bash
export GEMINI_API_KEY="your-key"
```

2. 必要に応じてデフォルトモデルを固定します:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. エージェントに依頼します:

> 夕焼けの中でフレンドリーなロブスターがサーフィンする、5秒のシネマティックな動画を生成して。

エージェントは自動的に `video_generate` を呼び出します。ツールの allowlist 設定は不要です。

## 動画を生成するときに何が起こるか

動画生成は非同期です。セッション内でエージェントが `video_generate` を呼び出すと、次のように動作します。

1. OpenClaw はリクエストをプロバイダーに送信し、すぐにタスクIDを返します。
2. プロバイダーはバックグラウンドでジョブを処理します（通常はプロバイダーと解像度に応じて30秒から5分）。
3. 動画の準備ができると、OpenClaw は同じセッションを内部完了イベントで起こします。
4. エージェントは完成した動画を元の会話に投稿します。

ジョブの実行中は、同じセッションで重複する `video_generate` 呼び出しを行っても、新しい生成は開始されず、現在のタスク状態が返されます。CLI から進行状況を確認するには、`openclaw tasks list` または `openclaw tasks show <taskId>` を使用してください。

セッションに紐づくエージェント実行の外側では（たとえば直接のツール呼び出しなど）、ツールはインライン生成にフォールバックし、同じターン内で最終的なメディアパスを返します。

## サポートされているプロバイダー

| Provider | デフォルトモデル                | テキスト | 画像参照         | 動画参照         | APIキー                                  |
| -------- | ------------------------------- | -------- | ---------------- | ---------------- | ---------------------------------------- |
| Alibaba  | `wan2.6-t2v`                    | Yes      | Yes（リモートURL） | Yes（リモートURL） | `MODELSTUDIO_API_KEY`                    |
| BytePlus | `seedance-1-0-lite-t2v-250428`  | Yes      | 画像1枚          | No               | `BYTEPLUS_API_KEY`                       |
| ComfyUI  | `workflow`                      | Yes      | 画像1枚          | No               | `COMFY_API_KEY` または `COMFY_CLOUD_API_KEY` |
| fal      | `fal-ai/minimax/video-01-live`  | Yes      | 画像1枚          | No               | `FAL_KEY`                                |
| Google   | `veo-3.1-fast-generate-preview` | Yes      | 画像1枚          | 動画1本          | `GEMINI_API_KEY`                         |
| MiniMax  | `MiniMax-Hailuo-2.3`            | Yes      | 画像1枚          | No               | `MINIMAX_API_KEY`                        |
| OpenAI   | `sora-2`                        | Yes      | 画像1枚          | 動画1本          | `OPENAI_API_KEY`                         |
| Qwen     | `wan2.6-t2v`                    | Yes      | Yes（リモートURL） | Yes（リモートURL） | `QWEN_API_KEY`                           |
| Runway   | `gen4.5`                        | Yes      | 画像1枚          | 動画1本          | `RUNWAYML_API_SECRET`                    |
| Together | `Wan-AI/Wan2.2-T2V-A14B`        | Yes      | 画像1枚          | No               | `TOGETHER_API_KEY`                       |
| Vydra    | `veo3`                          | Yes      | 画像1枚（`kling`） | No             | `VYDRA_API_KEY`                          |
| xAI      | `grok-imagine-video`            | Yes      | 画像1枚          | 動画1本          | `XAI_API_KEY`                            |

一部のプロバイダーは、追加または代替のAPIキー環境変数を受け付けます。詳細は各 [provider pages](#related) を参照してください。

ランタイム時に利用可能なプロバイダーとモデルを確認するには、`video_generate action=list` を実行してください。

## ツールパラメーター

### 必須

| Parameter | Type   | 説明                                                                          |
| --------- | ------ | ----------------------------------------------------------------------------- |
| `prompt`  | string | 生成する動画のテキスト説明（`action: "generate"` では必須）                   |

### コンテンツ入力

| Parameter | Type     | 説明                                 |
| --------- | -------- | ------------------------------------ |
| `image`   | string   | 単一の参照画像（パスまたはURL）      |
| `images`  | string[] | 複数の参照画像（最大5枚）            |
| `video`   | string   | 単一の参照動画（パスまたはURL）      |
| `videos`  | string[] | 複数の参照動画（最大4本）            |

### スタイル制御

| Parameter         | Type    | 説明                                                                        |
| ----------------- | ------- | --------------------------------------------------------------------------- |
| `aspectRatio`     | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`    |
| `resolution`      | string  | `480P`、`720P`、または `1080P`                                              |
| `durationSeconds` | number  | 目標の長さ（秒）。最も近いプロバイダー対応値に丸められます                 |
| `size`            | string  | プロバイダーが対応している場合のサイズヒント                                |
| `audio`           | boolean | 対応している場合に生成音声を有効化                                          |
| `watermark`       | boolean | 対応している場合にプロバイダーの透かしを切り替え                            |

### 高度な設定

| Parameter  | Type   | 説明                                            |
| ---------- | ------ | ----------------------------------------------- |
| `action`   | string | `"generate"`（デフォルト）、`"status"`、または `"list"` |
| `model`    | string | プロバイダー/モデルの上書き（例: `runway/gen4.5`） |
| `filename` | string | 出力ファイル名のヒント                          |

すべてのプロバイダーがすべてのパラメーターに対応しているわけではありません。未対応の上書きはベストエフォートで無視され、その旨がツール結果に警告として報告されます。厳密な機能制限（参照入力が多すぎるなど）は、送信前に失敗します。

## アクション

- **generate**（デフォルト） -- 指定したプロンプトと任意の参照入力から動画を生成します。
- **status** -- 現在のセッションで実行中の動画タスクの状態を、新しい生成を開始せずに確認します。
- **list** -- 利用可能なプロバイダー、モデル、およびその機能を表示します。

## モデル選択

動画を生成するとき、OpenClaw は次の順序でモデルを解決します。

1. **`model` ツールパラメーター** -- エージェントが呼び出し内で指定した場合。
2. **`videoGenerationModel.primary`** -- 設定から取得。
3. **`videoGenerationModel.fallbacks`** -- 順番に試行。
4. **自動検出** -- 現在のデフォルトプロバイダーから始め、続いて残りのプロバイダーをアルファベット順で使用します。対象は有効な認証があるプロバイダーです。

プロバイダーが失敗した場合、次の候補が自動的に試されます。すべての候補が失敗した場合、エラーには各試行の詳細が含まれます。

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["runway/gen4.5", "qwen/wan2.6-t2v"],
      },
    },
  },
}
```

## プロバイダーに関する注記

| Provider | 注記                                                                                                                                         |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | DashScope/Model Studio の非同期エンドポイントを使用します。参照画像と動画はリモートの `http(s)` URL である必要があります。                 |
| BytePlus | 単一の参照画像のみ対応。                                                                                                                     |
| ComfyUI  | ワークフロー駆動のローカルまたはクラウド実行。設定されたグラフを通じて text-to-video と image-to-video をサポートします。                  |
| fal      | 長時間実行ジョブにはキューベースのフローを使用します。単一の参照画像のみ対応。                                                             |
| Google   | Gemini/Veo を使用します。画像1枚または動画1本の参照に対応します。                                                                           |
| MiniMax  | 単一の参照画像のみ対応。                                                                                                                     |
| OpenAI   | `size` 上書きのみ転送されます。他のスタイル上書き（`aspectRatio`、`resolution`、`audio`、`watermark`）は無視され、警告が出ます。           |
| Qwen     | Alibaba と同じ DashScope バックエンドです。参照入力はリモートの `http(s)` URL である必要があり、ローカルファイルは事前に拒否されます。    |
| Runway   | data URI 経由でローカルファイルをサポートします。video-to-video には `runway/gen4_aleph` が必要です。テキストのみの実行では `16:9` と `9:16` のアスペクト比が公開されます。 |
| Together | 単一の参照画像のみ対応。                                                                                                                     |
| Vydra    | 認証が落ちるリダイレクトを避けるため、`https://www.vydra.ai/api/v1` を直接使用します。`veo3` は text-to-video 専用として同梱され、`kling` にはリモート画像URLが必要です。 |
| xAI      | text-to-video、image-to-video、リモート動画の編集/延長フローをサポートします。                                                              |

## 設定

OpenClaw 設定でデフォルトの動画生成モデルを設定します。

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-r2v-flash"],
      },
    },
  },
}
```

またはCLI経由で設定します。

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "qwen/wan2.6-t2v"
```

## 関連

- [Tools Overview](/ja-JP/tools)
- [Background Tasks](/ja-JP/automation/tasks) -- 非同期動画生成のためのタスク追跡
- [Alibaba Model Studio](/providers/alibaba)
- [BytePlus](/providers/byteplus)
- [ComfyUI](/providers/comfy)
- [fal](/providers/fal)
- [Google (Gemini)](/ja-JP/providers/google)
- [MiniMax](/ja-JP/providers/minimax)
- [OpenAI](/ja-JP/providers/openai)
- [Qwen](/ja-JP/providers/qwen)
- [Runway](/providers/runway)
- [Together AI](/ja-JP/providers/together)
- [Vydra](/providers/vydra)
- [xAI](/ja-JP/providers/xai)
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults)
- [Models](/ja-JP/concepts/models)
