---
read_when:
    - OpenClawでVydraのメディア生成を使いたいとき
    - Vydra APIキー設定のガイダンスが必要なとき
summary: OpenClawでVydraの画像、動画、音声を使う
title: Vydra
x-i18n:
    generated_at: "2026-04-06T03:12:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0fe999e8a5414b8a31a6d7d127bc6bcfc3b4492b8f438ab17dfa9680c5b079b7
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

バンドル済みのVydraプラグインは、次を追加します。

- `vydra/grok-imagine` による画像生成
- `vydra/veo3` と `vydra/kling` による動画生成
- VydraのElevenLabsベースTTSルートによる音声合成

OpenClawは、この3つの機能すべてで同じ `VYDRA_API_KEY` を使用します。

## 重要なbase URL

`https://www.vydra.ai/api/v1` を使用してください。

Vydraのapex host（`https://vydra.ai/api/v1`）は現在 `www` にリダイレクトします。一部のHTTPクライアントは、このホスト跨ぎのリダイレクト時に `Authorization` を落とすため、有効なAPIキーが誤解を招く認証失敗に変わってしまいます。バンドル済みプラグインは、これを避けるために `www` のbase URLを直接使用します。

## セットアップ

対話型オンボーディング:

```bash
openclaw onboard --auth-choice vydra-api-key
```

または、env var を直接設定します。

```bash
export VYDRA_API_KEY="vydra_live_..."
```

## 画像生成

デフォルトの画像model:

- `vydra/grok-imagine`

これをデフォルトの画像providerとして設定するには:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "vydra/grok-imagine",
      },
    },
  },
}
```

現在のバンドル済みサポートはテキストから画像のみです。Vydraのホスト型編集ルートはリモート画像URLを前提としており、OpenClawはまだバンドル済みプラグイン内でVydra専用のアップロードブリッジを追加していません。

共通のtool動作については、[Image Generation](/ja-JP/tools/image-generation) を参照してください。

## 動画生成

登録されている動画model:

- テキストから動画用の `vydra/veo3`
- 画像から動画用の `vydra/kling`

Vydraをデフォルトの動画providerとして設定するには:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "vydra/veo3",
      },
    },
  },
}
```

メモ:

- `vydra/veo3` は、バンドル版ではテキストから動画専用です。
- `vydra/kling` は現在、リモート画像URL参照が必要です。ローカルファイルアップロードは事前に拒否されます。
- バンドル済みプラグインは保守的な方針を取り、アスペクト比、解像度、透かし、生成音声などの文書化されていないスタイルノブは転送しません。

共通のtool動作については、[Video Generation](/tools/video-generation) を参照してください。

## 音声合成

Vydraをspeech providerとして設定します。

```json5
{
  messages: {
    tts: {
      provider: "vydra",
      providers: {
        vydra: {
          apiKey: "${VYDRA_API_KEY}",
          voiceId: "21m00Tcm4TlvDq8ikWAM",
        },
      },
    },
  },
}
```

デフォルト:

- model: `elevenlabs/tts`
- voice id: `21m00Tcm4TlvDq8ikWAM`

バンドル済みプラグインは現在、既知の正常動作するデフォルト音声を1つ公開しており、MP3音声ファイルを返します。

## 関連

- [Provider Directory](/ja-JP/providers/index)
- [Image Generation](/ja-JP/tools/image-generation)
- [Video Generation](/tools/video-generation)
