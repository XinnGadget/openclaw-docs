---
read_when:
    - OpenClaw でローカルの ComfyUI ワークフローを使いたい
    - 画像、動画、または音楽ワークフローで Comfy Cloud を使いたい
    - バンドル済み comfy plugin の設定キーが必要である
summary: OpenClaw における ComfyUI ワークフロー画像、動画、音楽生成のセットアップ
title: ComfyUI
x-i18n:
    generated_at: "2026-04-06T03:11:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: e645f32efdffdf4cd498684f1924bb953a014d3656b48f4b503d64e38c61ba9c
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw には、ワークフロー駆動の ComfyUI 実行向けに、バンドル済みの `comfy` plugin が含まれています。

- プロバイダー: `comfy`
- モデル: `comfy/workflow`
- 共有サーフェス: `image_generate`、`video_generate`、`music_generate`
- 認証: ローカル ComfyUI では不要。Comfy Cloud では `COMFY_API_KEY` または `COMFY_CLOUD_API_KEY`
- API: ComfyUI の `/prompt` / `/history` / `/view` と Comfy Cloud の `/api/*`

## サポート内容

- ワークフロー JSON からの画像生成
- 1枚のアップロード済み参照画像を使った画像編集
- ワークフロー JSON からの動画生成
- 1枚のアップロード済み参照画像を使った動画生成
- 共有 `music_generate` ツールを通じた音楽または音声生成
- 設定されたノード、または一致するすべての出力ノードからの出力ダウンロード

このバンドル済み plugin はワークフロー駆動であるため、OpenClaw は汎用的な
`size`、`aspectRatio`、`resolution`、`durationSeconds`、または TTS スタイルの制御を
グラフにマッピングしようとはしません。

## 設定レイアウト

Comfy は、共有のトップレベル接続設定と、機能ごとのワークフロー
セクションをサポートします。

```json5
{
  models: {
    providers: {
      comfy: {
        mode: "local",
        baseUrl: "http://127.0.0.1:8188",
        image: {
          workflowPath: "./workflows/flux-api.json",
          promptNodeId: "6",
          outputNodeId: "9",
        },
        video: {
          workflowPath: "./workflows/video-api.json",
          promptNodeId: "12",
          outputNodeId: "21",
        },
        music: {
          workflowPath: "./workflows/music-api.json",
          promptNodeId: "3",
          outputNodeId: "18",
        },
      },
    },
  },
}
```

共有キー:

- `mode`: `local` または `cloud`
- `baseUrl`: ローカルではデフォルトで `http://127.0.0.1:8188`、cloud では `https://cloud.comfy.org`
- `apiKey`: env vars の代替となる任意のインラインキー
- `allowPrivateNetwork`: cloud モードでプライベート/LAN の `baseUrl` を許可

`image`、`video`、または `music` 配下の機能ごとのキー:

- `workflow` または `workflowPath`: 必須
- `promptNodeId`: 必須
- `promptInputName`: デフォルトは `text`
- `outputNodeId`: 任意
- `pollIntervalMs`: 任意
- `timeoutMs`: 任意

画像と動画のセクションはさらに次もサポートします。

- `inputImageNodeId`: 参照画像を渡す場合は必須
- `inputImageInputName`: デフォルトは `image`

## 後方互換性

既存のトップレベル画像設定は引き続き動作します。

```json5
{
  models: {
    providers: {
      comfy: {
        workflowPath: "./workflows/flux-api.json",
        promptNodeId: "6",
        outputNodeId: "9",
      },
    },
  },
}
```

OpenClaw は、この旧式の形状を画像ワークフロー設定として扱います。

## 画像ワークフロー

デフォルトの画像モデルを設定します。

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "comfy/workflow",
      },
    },
  },
}
```

参照画像編集の例:

```json5
{
  models: {
    providers: {
      comfy: {
        image: {
          workflowPath: "./workflows/edit-api.json",
          promptNodeId: "6",
          inputImageNodeId: "7",
          inputImageInputName: "image",
          outputNodeId: "9",
        },
      },
    },
  },
}
```

## 動画ワークフロー

デフォルトの動画モデルを設定します。

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "comfy/workflow",
      },
    },
  },
}
```

Comfy の動画ワークフローは現在、設定されたグラフを通じて text-to-video と image-to-video をサポートします。OpenClaw は入力動画を Comfy ワークフローには渡しません。

## 音楽ワークフロー

このバンドル済み plugin は、ワークフロー定義の
音声または音楽出力向けの音楽生成プロバイダーを登録し、共有 `music_generate` ツールを通じて公開します。

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

`music` 設定セクションを使って、音声ワークフロー JSON と出力
ノードを指定してください。

## Comfy Cloud

`mode: "cloud"` と次のいずれかを使用します。

- `COMFY_API_KEY`
- `COMFY_CLOUD_API_KEY`
- `models.providers.comfy.apiKey`

cloud モードでも、同じ `image`、`video`、`music` ワークフローセクションを使用します。

## Liveテスト

このバンドル済み plugin にはオプトインの live カバレッジがあります。

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

一致する Comfy ワークフローセクションが設定されていない限り、live テストは個別の画像、動画、または音楽ケースをスキップします。

## 関連

- [Image Generation](/ja-JP/tools/image-generation)
- [Video Generation](/tools/video-generation)
- [Music Generation](/tools/music-generation)
- [Provider Directory](/ja-JP/providers/index)
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults)
