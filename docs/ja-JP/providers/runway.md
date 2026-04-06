---
read_when:
    - OpenClawでRunwayの動画生成を使いたいとき
    - Runway APIキー/env の設定が必要なとき
    - Runwayをデフォルトの動画providerにしたいとき
summary: OpenClawでのRunway動画生成セットアップ
title: Runway
x-i18n:
    generated_at: "2026-04-06T03:11:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: bc615d1a26f7a4b890d29461e756690c858ecb05024cf3c4d508218022da6e76
    source_path: providers/runway.md
    workflow: 15
---

# Runway

OpenClawには、ホスト型動画生成向けのバンドル済み `runway` provider が含まれています。

- Provider id: `runway`
- Auth: `RUNWAYML_API_SECRET`（正式）または `RUNWAY_API_KEY`
- API: Runwayのタスクベース動画生成（`GET /v1/tasks/{id}` ポーリング）

## クイックスタート

1. APIキーを設定します。

```bash
openclaw onboard --auth-choice runway-api-key
```

2. Runwayをデフォルトの動画providerに設定します。

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "runway/gen4.5"
```

3. エージェントに動画生成を依頼します。Runwayが自動的に使用されます。

## サポートされるモード

| Mode | Model | 参照入力 |
| -------------- | ------------------ | ----------------------- |
| テキストから動画 | `gen4.5`（デフォルト） | なし |
| 画像から動画 | `gen4.5` | ローカルまたはリモート画像1枚 |
| 動画から動画 | `gen4_aleph` | ローカルまたはリモート動画1本 |

- ローカル画像および動画参照は、data URI 経由でサポートされます。
- 動画から動画は現在、特に `runway/gen4_aleph` が必要です。
- テキストのみの実行では、現在 `16:9` と `9:16` のアスペクト比を利用できます。

## 設定

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## 関連

- [Video Generation](/tools/video-generation) -- 共通toolパラメーター、provider選択、非同期動作
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults)
