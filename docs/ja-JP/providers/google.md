---
read_when:
    - OpenClaw で Google Gemini モデルを使いたい場合
    - API キーの認証フローが必要な場合
summary: Google Gemini のセットアップ（API キー、画像生成、media understanding、web search）
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-06T03:11:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 358d33a68275b01ebd916a3621dd651619cb9a1d062e2fb6196a7f3c501c015a
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Google plugin は、Google AI Studio を通じた Gemini モデルへのアクセスに加えて、
画像生成、media understanding（画像/音声/動画）、および Gemini Grounding による web search を提供します。

- Provider: `google`
- 認証: `GEMINI_API_KEY` または `GOOGLE_API_KEY`
- API: Google Gemini API

## クイックスタート

1. API キーを設定します:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. デフォルトモデルを設定します:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## 非対話の例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## Capabilities

| Capability             | Supported |
| ---------------------- | --------- |
| Chat completions       | はい      |
| Image generation       | はい      |
| Music generation       | はい      |
| Image understanding    | はい      |
| Audio transcription    | はい      |
| Video understanding    | はい      |
| Web search (Grounding) | はい      |
| Thinking/reasoning     | はい（Gemini 3.1+） |

## 直接 Gemini キャッシュ再利用

直接 Gemini API 実行（`api: "google-generative-ai"`）では、OpenClaw は現在、
設定済みの `cachedContent` ハンドルを Gemini リクエストに渡します。

- モデルごとまたはグローバルの params に `cachedContent` または旧式の `cached_content` のいずれかを設定します
- 両方が存在する場合は `cachedContent` が優先されます
- 値の例: `cachedContents/prebuilt-context`
- Gemini のキャッシュヒット使用量は、上流の `cachedContentTokenCount` から OpenClaw の `cacheRead` に正規化されます

例:

```json5
{
  agents: {
    defaults: {
      models: {
        "google/gemini-2.5-pro": {
          params: {
            cachedContent: "cachedContents/prebuilt-context",
          },
        },
      },
    },
  },
}
```

## 画像生成

バンドル `google` image-generation provider のデフォルトは
`google/gemini-3.1-flash-image-preview` です。

- `google/gemini-3-pro-image-preview` にも対応しています
- Generate: リクエストごとに最大 4 枚の画像
- Edit mode: 有効、最大 5 枚の入力画像
- ジオメトリ制御: `size`、`aspectRatio`、`resolution`

画像生成、media understanding、Gemini Grounding はすべて
`google` provider id 上にとどまります。

Google をデフォルトの画像 provider として使うには:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "google/gemini-3.1-flash-image-preview",
      },
    },
  },
}
```

共有 tool の
パラメーター、provider 選択、failover 動作については [Image Generation](/ja-JP/tools/image-generation) を参照してください。

## 動画生成

バンドル `google` plugin は、共有の
`video_generate` tool を通じて動画生成も登録します。

- デフォルト動画モデル: `google/veo-3.1-fast-generate-preview`
- モード: text-to-video、image-to-video、単一動画参照フロー
- `aspectRatio`、`resolution`、`audio` をサポート
- 現在の duration 制限: **4〜8 秒**

Google をデフォルトの動画 provider として使うには:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
      },
    },
  },
}
```

共有 tool の
パラメーター、provider 選択、failover 動作については [Video Generation](/tools/video-generation) を参照してください。

## 音楽生成

バンドル `google` plugin は、共有の
`music_generate` tool を通じて音楽生成も登録します。

- デフォルト音楽モデル: `google/lyria-3-clip-preview`
- `google/lyria-3-pro-preview` にも対応しています
- プロンプト制御: `lyrics` と `instrumental`
- 出力形式: デフォルトは `mp3`、さらに `google/lyria-3-pro-preview` では `wav`
- 参照入力: 最大 10 枚の画像
- セッションベースの実行は、`action: "status"` を含む共有 task/status フローを通じてデタッチされます

Google をデフォルトの音楽 provider として使うには:

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

共有 tool の
パラメーター、provider 選択、failover 動作については [Music Generation](/tools/music-generation) を参照してください。

## 環境に関する注意

Gateway がデーモン（launchd/systemd）として動作している場合は、`GEMINI_API_KEY`
がそのプロセスから利用可能であることを確認してください（たとえば `~/.openclaw/.env` または
`env.shellEnv` 経由）。
