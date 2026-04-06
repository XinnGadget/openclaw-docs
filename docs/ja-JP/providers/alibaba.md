---
read_when:
    - OpenClaw で Alibaba Wan 動画生成を使いたい
    - 動画生成のために Model Studio または DashScope API キーのセットアップが必要である
summary: OpenClaw における Alibaba Model Studio の Wan 動画生成
title: Alibaba Model Studio
x-i18n:
    generated_at: "2026-04-06T03:10:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 97a1eddc7cbd816776b9368f2a926b5ef9ee543f08d151a490023736f67dc635
    source_path: providers/alibaba.md
    workflow: 15
---

# Alibaba Model Studio

OpenClaw には、Alibaba Model Studio / DashScope 上の Wan モデル向けの、バンドル済み `alibaba` 動画生成プロバイダーが含まれています。

- プロバイダー: `alibaba`
- 推奨認証: `MODELSTUDIO_API_KEY`
- 使用可能: `DASHSCOPE_API_KEY`、`QWEN_API_KEY`
- API: DashScope / Model Studio 非同期動画生成

## クイックスタート

1. API キーを設定します:

```bash
openclaw onboard --auth-choice qwen-standard-api-key
```

2. デフォルトの動画モデルを設定します:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "alibaba/wan2.6-t2v",
      },
    },
  },
}
```

## 組み込みの Wan モデル

バンドル済み `alibaba` プロバイダーは現在、次を登録しています。

- `alibaba/wan2.6-t2v`
- `alibaba/wan2.6-i2v`
- `alibaba/wan2.6-r2v`
- `alibaba/wan2.6-r2v-flash`
- `alibaba/wan2.7-r2v`

## 現在の制限

- リクエストごとの出力動画は最大 **1** 本
- 入力画像は最大 **1** 枚
- 入力動画は最大 **4** 本
- 長さは最大 **10秒**
- `size`、`aspectRatio`、`resolution`、`audio`、`watermark` をサポート
- 参照画像/動画モードは現在 **リモート http(s) URL** を必要とします

## Qwen との関係

バンドル済みの `qwen` プロバイダーも、Wan 動画生成のために Alibaba がホストする DashScope エンドポイントを使用します。用途に応じて次を使い分けてください。

- 正式な Qwen プロバイダーサーフェスを使いたい場合は `qwen/...`
- ベンダー直轄の Wan 動画サーフェスを使いたい場合は `alibaba/...`

## 関連

- [Video Generation](/tools/video-generation)
- [Qwen](/ja-JP/providers/qwen)
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults)
