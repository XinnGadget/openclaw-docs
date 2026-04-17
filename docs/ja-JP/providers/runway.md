---
read_when:
    - OpenClaw で Runway 動画生成を使いたい場合
    - Runway API key/env のセットアップが必要です
    - Runway をデフォルトの動画 provider にしたい場合
summary: OpenClaw での Runway 動画生成のセットアップ
title: Runway
x-i18n:
    generated_at: "2026-04-12T23:33:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb9a2d26687920544222b0769f314743af245629fd45b7f456c0161a47476176
    source_path: providers/runway.md
    workflow: 15
---

# Runway

OpenClaw には、ホスト型動画生成用のバンドル済み `runway` provider が含まれています。

| Property    | Value                                                             |
| ----------- | ----------------------------------------------------------------- |
| Provider id | `runway`                                                          |
| Auth        | `RUNWAYML_API_SECRET`（正規）または `RUNWAY_API_KEY`             |
| API         | Runway のタスクベース動画生成（`GET /v1/tasks/{id}` ポーリング） |

## はじめに

<Steps>
  <Step title="API key を設定">
    ```bash
    openclaw onboard --auth-choice runway-api-key
    ```
  </Step>
  <Step title="Runway をデフォルトの動画 provider に設定">
    ```bash
    openclaw config set agents.defaults.videoGenerationModel.primary "runway/gen4.5"
    ```
  </Step>
  <Step title="動画を生成">
    エージェントに動画生成を依頼してください。Runway が自動的に使用されます。
  </Step>
</Steps>

## サポートされるモード

| モード           | Model              | 参照入力                  |
| -------------- | ------------------ | ------------------------- |
| Text-to-video  | `gen4.5`（デフォルト） | なし                      |
| Image-to-video | `gen4.5`           | ローカルまたはリモート画像 1 枚 |
| Video-to-video | `gen4_aleph`       | ローカルまたはリモート動画 1 本 |

<Note>
ローカル画像および動画の参照は data URI 経由でサポートされます。テキストのみの実行では、
現在 `16:9` および `9:16` のアスペクト比が公開されています。
</Note>

<Warning>
Video-to-video は現在、特に `runway/gen4_aleph` を必要とします。
</Warning>

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

## 高度な注記

<AccordionGroup>
  <Accordion title="環境変数エイリアス">
    OpenClaw は `RUNWAYML_API_SECRET`（正規）と `RUNWAY_API_KEY` の両方を認識します。
    どちらの変数でも Runway provider を認証できます。
  </Accordion>

  <Accordion title="タスクポーリング">
    Runway はタスクベース API を使用します。生成リクエストを送信した後、OpenClaw は
    動画の準備ができるまで `GET /v1/tasks/{id}` をポーリングします。ポーリング動作に
    追加設定は不要です。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="動画生成" href="/ja-JP/tools/video-generation" icon="video">
    共有ツールパラメータ、provider 選択、および非同期挙動。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference#agent-defaults" icon="gear">
    動画生成 model を含むエージェントのデフォルト設定。
  </Card>
</CardGroup>
