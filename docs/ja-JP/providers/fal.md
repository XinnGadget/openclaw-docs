---
read_when:
    - OpenClaw で fal の画像生成を使いたい場合
    - FAL_KEY の認証フローが必要な場合
    - image_generate または video_generate 向けの fal デフォルトを使いたい場合
summary: OpenClaw での fal 画像・動画生成のセットアップ
title: fal
x-i18n:
    generated_at: "2026-04-06T03:11:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1922907d2c8360c5877a56495323d54bd846d47c27a801155e3d11e3f5706fbd
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw には、ホスト型の画像生成および動画生成向けのバンドル `fal` provider が含まれています。

- Provider: `fal`
- 認証: `FAL_KEY`（正式。`FAL_API_KEY` もフォールバックとして動作します）
- API: fal model endpoint

## クイックスタート

1. API キーを設定します:

```bash
openclaw onboard --auth-choice fal-api-key
```

2. デフォルトの画像 model を設定します:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## 画像生成

バンドル `fal` image-generation provider のデフォルトは
`fal/fal-ai/flux/dev` です。

- Generate: リクエストごとに最大 4 枚の画像
- Edit mode: 有効、参照画像は 1 枚
- `size`、`aspectRatio`、`resolution` をサポート
- 現在の edit に関する注意点: fal の画像 edit endpoint は **`aspectRatio` の上書きに対応していません**

fal をデフォルトの画像 provider として使うには:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## 動画生成

バンドル `fal` video-generation provider のデフォルトは
`fal/fal-ai/minimax/video-01-live` です。

- モード: text-to-video と単一画像参照フロー
- 実行時: 長時間実行ジョブ向けの queue ベース submit/status/result フロー

fal をデフォルトの動画 provider として使うには:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "fal/fal-ai/minimax/video-01-live",
      },
    },
  },
}
```

## 関連

- [画像生成](/ja-JP/tools/image-generation)
- [動画生成](/tools/video-generation)
- [設定リファレンス](/ja-JP/gateway/configuration-reference#agent-defaults)
