---
read_when:
    - OpenClaw で StepFun model を使いたい場合
    - StepFun のセットアップガイダンスが必要です
summary: OpenClaw で StepFun model を使う
title: StepFun
x-i18n:
    generated_at: "2026-04-12T23:33:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: a463bed0951d33802dcdb3a7784406272ee206b731e9864ea020323e67b4d159
    source_path: providers/stepfun.md
    workflow: 15
---

# StepFun

OpenClaw には、2 つの provider id を持つバンドル済み StepFun provider Plugin が含まれています。

- 標準エンドポイント用の `stepfun`
- Step Plan エンドポイント用の `stepfun-plan`

<Warning>
Standard と Step Plan は、エンドポイントと model 参照プレフィックス（`stepfun/...` と `stepfun-plan/...`）が異なる**別々の provider**です。China キーには `.com` エンドポイントを使い、global キーには `.ai` エンドポイントを使ってください。
</Warning>

## リージョンとエンドポイントの概要

| Endpoint  | China (`.com`)                         | Global (`.ai`)                        |
| --------- | -------------------------------------- | ------------------------------------- |
| Standard  | `https://api.stepfun.com/v1`           | `https://api.stepfun.ai/v1`           |
| Step Plan | `https://api.stepfun.com/step_plan/v1` | `https://api.stepfun.ai/step_plan/v1` |

認証環境変数: `STEPFUN_API_KEY`

## 組み込み catalog

Standard（`stepfun`）:

| Model ref                | コンテキスト | 最大出力 | 注記                   |
| ------------------------ | ------- | ---------- | ---------------------- |
| `stepfun/step-3.5-flash` | 262,144 | 65,536     | デフォルトの standard model |

Step Plan（`stepfun-plan`）:

| Model ref                          | コンテキスト | 最大出力 | 注記                         |
| ---------------------------------- | ------- | ---------- | ---------------------------- |
| `stepfun-plan/step-3.5-flash`      | 262,144 | 65,536     | デフォルトの Step Plan model   |
| `stepfun-plan/step-3.5-flash-2603` | 262,144 | 65,536     | 追加の Step Plan model       |

## はじめに

使いたい provider サーフェスを選び、セットアップ手順に従ってください。

<Tabs>
  <Tab title="Standard">
    **最適な用途:** standard StepFun エンドポイント経由の汎用利用。

    <Steps>
      <Step title="エンドポイントのリージョンを選ぶ">
        | Auth choice                      | Endpoint                         | Region        |
        | -------------------------------- | -------------------------------- | ------------- |
        | `stepfun-standard-api-key-intl`  | `https://api.stepfun.ai/v1`     | International |
        | `stepfun-standard-api-key-cn`    | `https://api.stepfun.com/v1`    | China         |
      </Step>
      <Step title="オンボーディングを実行">
        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-intl
        ```

        または China エンドポイントの場合:

        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-cn
        ```
      </Step>
      <Step title="非対話型の代替手段">
        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-intl \
          --stepfun-api-key "$STEPFUN_API_KEY"
        ```
      </Step>
      <Step title="model が利用可能であることを確認">
        ```bash
        openclaw models list --provider stepfun
        ```
      </Step>
    </Steps>

    ### model 参照

    - デフォルト model: `stepfun/step-3.5-flash`

  </Tab>

  <Tab title="Step Plan">
    **最適な用途:** Step Plan reasoning エンドポイント。

    <Steps>
      <Step title="エンドポイントのリージョンを選ぶ">
        | Auth choice                  | Endpoint                                | Region        |
        | ---------------------------- | --------------------------------------- | ------------- |
        | `stepfun-plan-api-key-intl`  | `https://api.stepfun.ai/step_plan/v1`  | International |
        | `stepfun-plan-api-key-cn`    | `https://api.stepfun.com/step_plan/v1` | China         |
      </Step>
      <Step title="オンボーディングを実行">
        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-intl
        ```

        または China エンドポイントの場合:

        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-cn
        ```
      </Step>
      <Step title="非対話型の代替手段">
        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-intl \
          --stepfun-api-key "$STEPFUN_API_KEY"
        ```
      </Step>
      <Step title="model が利用可能であることを確認">
        ```bash
        openclaw models list --provider stepfun-plan
        ```
      </Step>
    </Steps>

    ### model 参照

    - デフォルト model: `stepfun-plan/step-3.5-flash`
    - 代替 model: `stepfun-plan/step-3.5-flash-2603`

  </Tab>
</Tabs>

## 高度な設定

<AccordionGroup>
  <Accordion title="完全な設定: Standard provider">
    ```json5
    {
      env: { STEPFUN_API_KEY: "your-key" },
      agents: { defaults: { model: { primary: "stepfun/step-3.5-flash" } } },
      models: {
        mode: "merge",
        providers: {
          stepfun: {
            baseUrl: "https://api.stepfun.ai/v1",
            api: "openai-completions",
            apiKey: "${STEPFUN_API_KEY}",
            models: [
              {
                id: "step-3.5-flash",
                name: "Step 3.5 Flash",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="完全な設定: Step Plan provider">
    ```json5
    {
      env: { STEPFUN_API_KEY: "your-key" },
      agents: { defaults: { model: { primary: "stepfun-plan/step-3.5-flash" } } },
      models: {
        mode: "merge",
        providers: {
          "stepfun-plan": {
            baseUrl: "https://api.stepfun.ai/step_plan/v1",
            api: "openai-completions",
            apiKey: "${STEPFUN_API_KEY}",
            models: [
              {
                id: "step-3.5-flash",
                name: "Step 3.5 Flash",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
              {
                id: "step-3.5-flash-2603",
                name: "Step 3.5 Flash 2603",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="注記">
    - この provider は OpenClaw にバンドルされているため、別途 Plugin をインストールする手順はありません。
    - `step-3.5-flash-2603` は現在 `stepfun-plan` でのみ公開されています。
    - 単一の認証フローで、`stepfun` と `stepfun-plan` の両方にリージョン一致の profile が書き込まれるため、両方のサーフェスをまとめて検出できます。
    - model の確認や切り替えには `openclaw models list` と `openclaw models set <provider/model>` を使ってください。
  </Accordion>
</AccordionGroup>

<Note>
より広い provider の概要については、[Model providers](/ja-JP/concepts/model-providers) を参照してください。
</Note>

## 関連

<CardGroup cols={2}>
  <Card title="Model providers" href="/ja-JP/concepts/model-providers" icon="layers">
    すべての provider、model 参照、およびフェイルオーバー挙動の概要。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference" icon="gear">
    provider、model、および Plugins の完全な設定スキーマ。
  </Card>
  <Card title="model 選択" href="/ja-JP/concepts/models" icon="brain">
    model の選び方と設定方法。
  </Card>
  <Card title="StepFun Platform" href="https://platform.stepfun.com" icon="globe">
    StepFun API key 管理とドキュメント。
  </Card>
</CardGroup>
