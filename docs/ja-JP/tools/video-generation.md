---
read_when:
    - agent経由で動画を生成する場合
    - 動画生成プロバイダーとモデルを設定する場合
    - '`video_generate` toolのパラメーターを理解する必要がある場合'
summary: 12種類のプロバイダーバックエンドを使って、テキスト、画像、既存の動画から動画を生成する方法
title: 動画生成
x-i18n:
    generated_at: "2026-04-07T04:47:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: bf1224c59a5f1217f56cf2001870aca710a09268677dcd12aad2efbe476e47b7
    source_path: tools/video-generation.md
    workflow: 15
---

# 動画生成

OpenClawエージェントは、テキストプロンプト、参照画像、または既存の動画から動画を生成できます。12種類のプロバイダーバックエンドがサポートされており、それぞれ異なるモデルオプション、入力モード、機能セットを備えています。エージェントは、設定内容と利用可能なAPIキーに基づいて、適切なプロバイダーを自動的に選択します。

<Note>
`video_generate` toolは、少なくとも1つの動画生成プロバイダーが利用可能な場合にのみ表示されます。agent toolsに表示されない場合は、provider API keyを設定するか、`agents.defaults.videoGenerationModel`を設定してください。
</Note>

OpenClawは動画生成を3つのruntime modesとして扱います:

- 参照メディアなしのテキストから動画へのリクエストには`generate`
- 1つ以上の参照画像を含むリクエストには`imageToVideo`
- 1つ以上の参照動画を含むリクエストには`videoToVideo`

プロバイダーは、これらのモードの任意の部分集合をサポートできます。toolは送信前にアクティブな
modeを検証し、`action=list`でサポートされるモードを報告します。

## クイックスタート

1. サポートされているいずれかのプロバイダーに対してAPIキーを設定します:

```bash
export GEMINI_API_KEY="your-key"
```

2. 必要に応じてデフォルトモデルを固定します:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. agentに依頼します:

> 夕焼けの中でフレンドリーなロブスターがサーフィンしている、5秒のシネマティックな動画を生成して。

agentは自動的に`video_generate`を呼び出します。tool allowlistingは不要です。

## 動画を生成すると何が起こるか

動画生成は非同期です。セッション内でagentが`video_generate`を呼び出すと:

1. OpenClawはリクエストをプロバイダーに送信し、即座にtask IDを返します。
2. プロバイダーはバックグラウンドでジョブを処理します（通常はプロバイダーと解像度に応じて30秒から5分）。
3. 動画の準備ができると、OpenClawは内部完了イベントで同じセッションを再開します。
4. agentは完成した動画を元の会話に投稿します。

ジョブの処理中に、同じセッションで重複した`video_generate`呼び出しがあると、新しい生成を開始する代わりに現在のtask statusを返します。CLIから進行状況を確認するには、`openclaw tasks list`または`openclaw tasks show <taskId>`を使用してください。

セッションに紐づくagent実行の外部（たとえば直接のtool呼び出し）では、toolはインライン生成にフォールバックし、同じターンで最終メディアパスを返します。

### タスクライフサイクル

各`video_generate`リクエストは、4つの状態を経由します:

1. **queued** -- taskが作成され、プロバイダーが受け付けるのを待っている状態です。
2. **running** -- プロバイダーが処理中です（通常はプロバイダーと解像度に応じて30秒から5分）。
3. **succeeded** -- 動画の準備完了。agentが再開し、会話に投稿します。
4. **failed** -- プロバイダーエラーまたはタイムアウト。agentがエラー詳細付きで再開します。

CLIから状態を確認するには:

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

重複防止: 現在のセッションですでに動画taskが`queued`または`running`の場合、`video_generate`は新しいtaskを開始する代わりに既存taskのstatusを返します。新しい生成をトリガーせず明示的に確認したい場合は、`action: "status"`を使用してください。

## サポートされているプロバイダー

| Provider | デフォルトモデル                   | テキスト | 画像参照           | 動画参照         | API key                                  |
| -------- | ------------------------------- | ---- | ----------------- | ---------------- | ---------------------------------------- |
| Alibaba  | `wan2.6-t2v`                    | はい  | はい（リモートURL）  | はい（リモートURL） | `MODELSTUDIO_API_KEY`                    |
| BytePlus | `seedance-1-0-lite-t2v-250428`  | はい  | 画像1枚           | いいえ               | `BYTEPLUS_API_KEY`                       |
| ComfyUI  | `workflow`                      | はい  | 画像1枚           | いいえ               | `COMFY_API_KEY` または `COMFY_CLOUD_API_KEY` |
| fal      | `fal-ai/minimax/video-01-live`  | はい  | 画像1枚           | いいえ               | `FAL_KEY`                                |
| Google   | `veo-3.1-fast-generate-preview` | はい  | 画像1枚           | 動画1本          | `GEMINI_API_KEY`                         |
| MiniMax  | `MiniMax-Hailuo-2.3`            | はい  | 画像1枚           | いいえ               | `MINIMAX_API_KEY`                        |
| OpenAI   | `sora-2`                        | はい  | 画像1枚           | 動画1本          | `OPENAI_API_KEY`                         |
| Qwen     | `wan2.6-t2v`                    | はい  | はい（リモートURL）  | はい（リモートURL） | `QWEN_API_KEY`                           |
| Runway   | `gen4.5`                        | はい  | 画像1枚           | 動画1本          | `RUNWAYML_API_SECRET`                    |
| Together | `Wan-AI/Wan2.2-T2V-A14B`        | はい  | 画像1枚           | いいえ               | `TOGETHER_API_KEY`                       |
| Vydra    | `veo3`                          | はい  | 画像1枚（`kling`） | いいえ               | `VYDRA_API_KEY`                          |
| xAI      | `grok-imagine-video`            | はい  | 画像1枚           | 動画1本          | `XAI_API_KEY`                            |

一部のプロバイダーは追加または代替のAPI key env varsを受け付けます。詳細は各[provider pages](#related)を参照してください。

実行時に利用可能なプロバイダー、モデル、
runtime modesを確認するには、`video_generate action=list`を実行してください。

### 宣言された機能マトリクス

これは、`video_generate`、contract tests、
および共有live sweepで使用される明示的なmode contractです。

| Provider | `generate` | `imageToVideo` | `videoToVideo` | 現在の共有live lanes                                                                                                                  |
| -------- | ---------- | -------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | はい        | はい            | はい            | `generate`、`imageToVideo`。`videoToVideo`は、このproviderがリモート`http(s)`動画URLを必要とするためスキップ                               |
| BytePlus | はい        | はい            | いいえ             | `generate`、`imageToVideo`                                                                                                               |
| ComfyUI  | はい        | はい            | いいえ             | 共有sweepには含まれません。workflow固有のカバレッジはComfy tests側にあります                                                               |
| fal      | はい        | はい            | いいえ             | `generate`、`imageToVideo`                                                                                                               |
| Google   | はい        | はい            | はい            | `generate`、`imageToVideo`。共有`videoToVideo`は、現在のbuffer-backed Gemini/Veo sweepがその入力を受け付けないためスキップ  |
| MiniMax  | はい        | はい            | いいえ             | `generate`、`imageToVideo`                                                                                                               |
| OpenAI   | はい        | はい            | はい            | `generate`、`imageToVideo`。共有`videoToVideo`は、このorg/input pathが現在provider側のinpaint/remixアクセスを必要とするためスキップ |
| Qwen     | はい        | はい            | はい            | `generate`、`imageToVideo`。`videoToVideo`は、このproviderがリモート`http(s)`動画URLを必要とするためスキップ                               |
| Runway   | はい        | はい            | はい            | `generate`、`imageToVideo`。`videoToVideo`は、選択したモデルが`runway/gen4_aleph`の場合にのみ実行されます                                      |
| Together | はい        | はい            | いいえ             | `generate`、`imageToVideo`                                                                                                               |
| Vydra    | はい        | はい            | いいえ             | `generate`。共有`imageToVideo`は、バンドル済み`veo3`がテキスト専用で、バンドル済み`kling`がリモート画像URLを必要とするためスキップ            |
| xAI      | はい        | はい            | はい            | `generate`、`imageToVideo`。`videoToVideo`は、このproviderが現在リモートMP4 URLを必要とするためスキップ                                |

## Tool parameters

### 必須

| Parameter | Type   | 説明                                                                   |
| --------- | ------ | ----------------------------------------------------------------------------- |
| `prompt`  | string | 生成する動画のテキスト説明（`action: "generate"`では必須） |

### コンテンツ入力

| Parameter | Type     | 説明                          |
| --------- | -------- | ------------------------------------ |
| `image`   | string   | 単一の参照画像（パスまたはURL） |
| `images`  | string[] | 複数の参照画像（最大5枚）  |
| `video`   | string   | 単一の参照動画（パスまたはURL） |
| `videos`  | string[] | 複数の参照動画（最大4本）  |

### スタイル制御

| Parameter         | Type    | 説明                                                              |
| ----------------- | ------- | ------------------------------------------------------------------------ |
| `aspectRatio`     | string  | `1:1`、`2:3`、`3:2`、`3:4`、`4:3`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9`  |
| `resolution`      | string  | `480P`、`720P`、`768P`、または`1080P`                                       |
| `durationSeconds` | number  | 目標の長さ（秒、最も近いprovider対応値に丸められます） |
| `size`            | string  | providerが対応している場合のサイズヒント                                  |
| `audio`           | boolean | 対応している場合に生成音声を有効化                                    |
| `watermark`       | boolean | 対応している場合にproviderの透かしを切り替え                              |

### 高度な項目

| Parameter  | Type   | 説明                                     |
| ---------- | ------ | ----------------------------------------------- |
| `action`   | string | `"generate"`（デフォルト）、`"status"`、または`"list"` |
| `model`    | string | provider/model上書き（例: `runway/gen4.5`）  |
| `filename` | string | 出力ファイル名のヒント                            |

すべてのプロバイダーがすべてのパラメーターをサポートしているわけではありません。OpenClawはすでにdurationを最も近いprovider対応値に正規化しており、フォールバック先providerが異なるcontrol surfaceを公開している場合には、size-to-aspect-ratioのような翻訳済みgeometry hintsも再マッピングします。本当に未対応の上書きはベストエフォートで無視され、tool result内で警告として報告されます。厳格な機能制限（参照入力が多すぎる場合など）は送信前に失敗します。

tool resultには適用された設定が報告されます。providerフォールバック中にOpenClawがdurationやgeometryを再マッピングした場合、返される`durationSeconds`、`size`、`aspectRatio`、`resolution`の値には実際に送信された内容が反映され、`details.normalization`には要求値から適用値への変換が記録されます。

参照入力はruntime modeも選択します:

- 参照メディアなし: `generate`
- 画像参照がある場合: `imageToVideo`
- 動画参照がある場合: `videoToVideo`

画像参照と動画参照の混在は、安定した共有機能表面ではありません。
1リクエストにつき1種類の参照タイプを推奨します。

## Actions

- **generate**（デフォルト） -- 与えられたプロンプトと任意の参照入力から動画を作成します。
- **status** -- 新しい生成を開始せず、現在のセッションで処理中の動画taskの状態を確認します。
- **list** -- 利用可能なプロバイダー、モデル、およびそれらの機能を表示します。

## モデル選択

動画生成時、OpenClawは次の順でモデルを解決します:

1. **`model` tool parameter** -- agentが呼び出し時に指定した場合。
2. **`videoGenerationModel.primary`** -- configから。
3. **`videoGenerationModel.fallbacks`** -- 順番に試行されます。
4. **自動検出** -- 有効なauthを持つプロバイダーを使用し、まず現在のデフォルトproviderから、次に残りのプロバイダーをアルファベット順で試します。

プロバイダーが失敗した場合、次の候補が自動的に試されます。すべての候補が失敗した場合、エラーには各試行の詳細が含まれます。

動画生成で明示的な`model`、`primary`、`fallbacks`
エントリのみを使用したい場合は、`agents.defaults.mediaGenerationAutoProviderFallback: false`を設定してください。

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

## プロバイダーノート

| Provider | Notes                                                                                                                                                       |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | DashScope/Model Studioの非同期endpointを使用します。参照画像と動画はリモート`http(s)` URLである必要があります。                                                      |
| BytePlus | 単一の参照画像のみです。                                                                                                                                |
| ComfyUI  | workflow駆動のローカルまたはクラウド実行です。設定済みgraphを通じてtext-to-videoとimage-to-videoをサポートします。                                           |
| fal      | 長時間実行ジョブにqueue-backed flowを使用します。単一の参照画像のみです。                                                                                  |
| Google   | Gemini/Veoを使用します。1枚の画像または1本の動画参照をサポートします。                                                                                                 |
| MiniMax  | 単一の参照画像のみです。                                                                                                                                |
| OpenAI   | `size`上書きのみが転送されます。他のスタイル上書き（`aspectRatio`、`resolution`、`audio`、`watermark`）は警告付きで無視されます。                    |
| Qwen     | Alibabaと同じDashScopeバックエンドです。参照入力はリモート`http(s)` URLである必要があり、ローカルファイルは事前に拒否されます。                                        |
| Runway   | data URI経由でローカルファイルをサポートします。video-to-videoには`runway/gen4_aleph`が必要です。テキスト専用実行では`16:9`と`9:16`のaspect ratiosを公開します。                     |
| Together | 単一の参照画像のみです。                                                                                                                                |
| Vydra    | 認証が落ちるリダイレクトを避けるため、`https://www.vydra.ai/api/v1`を直接使用します。`veo3`はバンドル済みでtext-to-video専用、`kling`はリモート画像URLが必要です。 |
| xAI      | text-to-video、image-to-video、およびリモート動画の編集/拡張フローをサポートします。                                                                                 |

## プロバイダー機能モード

共有の動画生成contractでは、プロバイダーが単なるフラットな集約制限ではなく、
モード固有のcapabilitiesを宣言できるようになりました。新しいprovider
実装では、明示的なmode blocksを優先してください:

```typescript
capabilities: {
  generate: {
    maxVideos: 1,
    maxDurationSeconds: 10,
    supportsResolution: true,
  },
  imageToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputImages: 1,
    maxDurationSeconds: 5,
  },
  videoToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputVideos: 1,
    maxDurationSeconds: 5,
  },
}
```

`maxInputImages`や`maxInputVideos`のようなフラットな集約フィールドだけでは、
transform-mode supportを示すには不十分です。プロバイダーは
`generate`、`imageToVideo`、`videoToVideo`を明示的に宣言し、live tests、
contract tests、および共有の`video_generate` toolがmode supportを
決定的に検証できるようにする必要があります。

## Live tests

共有バンドル済みプロバイダー向けのオプトインlive coverage:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts
```

リポジトリラッパー:

```bash
pnpm test:live:media video
```

このliveファイルは、欠けているprovider env varsを`~/.profile`から読み込み、
デフォルトでは保存済みauth profilesよりlive/env API keysを優先し、ローカルメディアで安全に実行できる宣言済みモードを実行します:

- sweep内のすべてのプロバイダーに対する`generate`
- `capabilities.imageToVideo.enabled`のときの`imageToVideo`
- `capabilities.videoToVideo.enabled`であり、provider/model
  が共有sweep内でbuffer-backedローカル動画入力を受け付けるときの`videoToVideo`

現在、共有の`videoToVideo` live laneが対象としているのは:

- `runway`（`runway/gen4_aleph`を選択した場合のみ）

## 設定

OpenClaw configでデフォルトの動画生成モデルを設定します:

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

またはCLIから:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "qwen/wan2.6-t2v"
```

## 関連

- [Tools Overview](/ja-JP/tools)
- [Background Tasks](/ja-JP/automation/tasks) -- 非同期動画生成のtask追跡
- [Alibaba Model Studio](/ja-JP/providers/alibaba)
- [BytePlus](/ja-JP/concepts/model-providers#byteplus-international)
- [ComfyUI](/ja-JP/providers/comfy)
- [fal](/ja-JP/providers/fal)
- [Google (Gemini)](/ja-JP/providers/google)
- [MiniMax](/ja-JP/providers/minimax)
- [OpenAI](/ja-JP/providers/openai)
- [Qwen](/ja-JP/providers/qwen)
- [Runway](/ja-JP/providers/runway)
- [Together AI](/ja-JP/providers/together)
- [Vydra](/ja-JP/providers/vydra)
- [xAI](/ja-JP/providers/xai)
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults)
- [Models](/ja-JP/concepts/models)
