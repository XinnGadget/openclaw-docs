---
read_when:
    - Volcano Engine または Doubao モデルを OpenClaw で使用したい場合
    - Volcengine API キーのセットアップが必要です
summary: Volcano Engine のセットアップ（Doubao モデル、汎用 + コーディングエンドポイント）
title: Volcengine（Doubao）
x-i18n:
    generated_at: "2026-04-12T23:34:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: a21f390da719f79c88c6d55a7d952d35c2ce5ff26d910c9f10020132cd7d2f4c
    source_path: providers/volcengine.md
    workflow: 15
---

# Volcengine（Doubao）

Volcengine プロバイダーは、Volcano Engine 上でホストされる Doubao モデルおよびサードパーティモデルへのアクセスを提供し、一般用途とコーディング用途で別々のエンドポイントを備えています。

| Detail    | Value                                               |
| --------- | --------------------------------------------------- |
| プロバイダー | `volcengine`（一般） + `volcengine-plan`（コーディング） |
| 認証      | `VOLCANO_ENGINE_API_KEY`                            |
| API       | OpenAI互換                                   |

## はじめに

<Steps>
  <Step title="API キーを設定する">
    対話型オンボーディングを実行します。

    ```bash
    openclaw onboard --auth-choice volcengine-api-key
    ```

    これにより、1 つの API キーから一般向け (`volcengine`) とコーディング向け (`volcengine-plan`) の両方のプロバイダーが登録されます。

  </Step>
  <Step title="デフォルトモデルを設定する">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "volcengine-plan/ark-code-latest" },
        },
      },
    }
    ```
  </Step>
  <Step title="モデルが利用可能であることを確認する">
    ```bash
    openclaw models list --provider volcengine
    openclaw models list --provider volcengine-plan
    ```
  </Step>
</Steps>

<Tip>
非対話型セットアップ（CI、スクリプト）では、キーを直接渡してください。

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice volcengine-api-key \
  --volcengine-api-key "$VOLCANO_ENGINE_API_KEY"
```

</Tip>

## プロバイダーとエンドポイント

| Provider          | Endpoint                                  | Use case       |
| ----------------- | ----------------------------------------- | -------------- |
| `volcengine`      | `ark.cn-beijing.volces.com/api/v3`        | 一般モデル |
| `volcengine-plan` | `ark.cn-beijing.volces.com/api/coding/v3` | コーディングモデル  |

<Note>
両方のプロバイダーは 1 つの API キーから設定されます。セットアップ時に両方が自動的に登録されます。
</Note>

## 利用可能なモデル

<Tabs>
  <Tab title="一般 (`volcengine`)">
    | Model ref                                    | Name                            | Input       | Context |
    | -------------------------------------------- | ------------------------------- | ----------- | ------- |
    | `volcengine/doubao-seed-1-8-251228`          | Doubao Seed 1.8                 | テキスト、画像 | 256,000 |
    | `volcengine/doubao-seed-code-preview-251028` | doubao-seed-code-preview-251028 | テキスト、画像 | 256,000 |
    | `volcengine/kimi-k2-5-260127`                | Kimi K2.5                       | テキスト、画像 | 256,000 |
    | `volcengine/glm-4-7-251222`                  | GLM 4.7                         | テキスト、画像 | 200,000 |
    | `volcengine/deepseek-v3-2-251201`            | DeepSeek V3.2                   | テキスト、画像 | 128,000 |
  </Tab>
  <Tab title="コーディング (`volcengine-plan`)">
    | Model ref                                         | Name                     | Input | Context |
    | ------------------------------------------------- | ------------------------ | ----- | ------- |
    | `volcengine-plan/ark-code-latest`                 | Ark Coding Plan          | テキスト  | 256,000 |
    | `volcengine-plan/doubao-seed-code`                | Doubao Seed Code         | テキスト  | 256,000 |
    | `volcengine-plan/glm-4.7`                         | GLM 4.7 Coding           | テキスト  | 200,000 |
    | `volcengine-plan/kimi-k2-thinking`                | Kimi K2 Thinking         | テキスト  | 256,000 |
    | `volcengine-plan/kimi-k2.5`                       | Kimi K2.5 Coding         | テキスト  | 256,000 |
    | `volcengine-plan/doubao-seed-code-preview-251028` | Doubao Seed Code Preview | テキスト  | 256,000 |
  </Tab>
</Tabs>

## 高度な注記

<AccordionGroup>
  <Accordion title="オンボーディング後のデフォルトモデル">
    `openclaw onboard --auth-choice volcengine-api-key` は現在、
    `volcengine-plan/ark-code-latest` をデフォルトモデルに設定しつつ、
    一般向けの `volcengine` カタログも登録します。
  </Accordion>

  <Accordion title="モデルピッカーのフォールバック動作">
    オンボーディング / 設定時のモデル選択では、Volcengine の認証方法は
    `volcengine/*` と `volcengine-plan/*` の両方の行を優先します。これらのモデルが
    まだ読み込まれていない場合、OpenClaw は空のプロバイダースコープ付きピッカーを表示するのではなく、
    フィルターなしカタログにフォールバックします。
  </Accordion>

  <Accordion title="デーモンプロセス向けの環境変数">
    Gateway がデーモン（launchd/systemd）として実行される場合は、
    `VOLCANO_ENGINE_API_KEY` がそのプロセスから利用可能であることを確認してください（たとえば
    `~/.openclaw/.env` または `env.shellEnv` 経由）。
  </Accordion>
</AccordionGroup>

<Warning>
OpenClaw をバックグラウンドサービスとして実行する場合、対話シェルで設定した環境変数は
自動的には引き継がれません。上記のデーモンに関する注記を参照してください。
</Warning>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデル参照、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Configuration" href="/ja-JP/gateway/configuration" icon="gear">
    エージェント、モデル、プロバイダーに関する完全な config リファレンス。
  </Card>
  <Card title="トラブルシューティング" href="/ja-JP/help/troubleshooting" icon="wrench">
    一般的な問題とデバッグ手順。
  </Card>
  <Card title="FAQ" href="/ja-JP/help/faq" icon="circle-question">
    OpenClaw のセットアップに関するよくある質問。
  </Card>
</CardGroup>
