---
read_when:
    - OpenClaw で Chutes を使いたい
    - OAuth または API キーのセットアップ手順が必要です
    - デフォルト モデル、エイリアス、または検出の挙動を知りたい
summary: Chutes のセットアップ（OAuth または API キー、モデル検出、エイリアス）
title: Chutes
x-i18n:
    generated_at: "2026-04-12T23:30:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 07c52b1d1d2792412e6daabc92df5310434b3520116d9e0fd2ad26bfa5297e1c
    source_path: providers/chutes.md
    workflow: 15
---

# Chutes

[Chutes](https://chutes.ai) は、OpenAI 互換 API を通じてオープンソース モデル カタログを提供します。OpenClaw は、バンドルされた `chutes` プロバイダーに対して、ブラウザー OAuth と直接 API キー認証の両方をサポートしています。

| Property | Value |
| -------- | ----- |
| プロバイダー | `chutes` |
| API | OpenAI 互換 |
| ベース URL | `https://llm.chutes.ai/v1` |
| 認証 | OAuth または API キー（以下を参照） |

## はじめに

<Tabs>
  <Tab title="OAuth">
    <Steps>
      <Step title="OAuth オンボーディング フローを実行する">
        ```bash
        openclaw onboard --auth-choice chutes
        ```
        OpenClaw はローカルでブラウザー フローを起動し、リモート/ヘッドレス ホストでは URL + リダイレクト貼り付けフローを表示します。OAuth トークンは OpenClaw の認証プロファイルを通じて自動更新されます。
      </Step>
      <Step title="デフォルト モデルを確認する">
        オンボーディング後、デフォルト モデルは
        `chutes/zai-org/GLM-4.7-TEE` に設定され、バンドルされた Chutes カタログが登録されます。
      </Step>
    </Steps>
  </Tab>
  <Tab title="API キー">
    <Steps>
      <Step title="API キーを取得する">
        キーは
        [chutes.ai/settings/api-keys](https://chutes.ai/settings/api-keys) で作成します。
      </Step>
      <Step title="API キーのオンボーディング フローを実行する">
        ```bash
        openclaw onboard --auth-choice chutes-api-key
        ```
      </Step>
      <Step title="デフォルト モデルを確認する">
        オンボーディング後、デフォルト モデルは
        `chutes/zai-org/GLM-4.7-TEE` に設定され、バンドルされた Chutes カタログが登録されます。
      </Step>
    </Steps>
  </Tab>
</Tabs>

<Note>
どちらの認証経路でも、バンドルされた Chutes カタログが登録され、デフォルト モデルは
`chutes/zai-org/GLM-4.7-TEE` に設定されます。実行時環境変数: `CHUTES_API_KEY`、
`CHUTES_OAUTH_TOKEN`。
</Note>

## 検出の挙動

Chutes 認証が利用可能な場合、OpenClaw はその認証情報で Chutes カタログを問い合わせ、検出されたモデルを使用します。検出に失敗した場合でも、オンボーディングと起動が引き続き動作するよう、OpenClaw はバンドルされた静的カタログにフォールバックします。

## デフォルト エイリアス

OpenClaw は、バンドルされた Chutes カタログに対して 3 つの便利なエイリアスを登録します:

| Alias | Target model |
| ----- | ------------ |
| `chutes-fast` | `chutes/zai-org/GLM-4.7-FP8` |
| `chutes-pro` | `chutes/deepseek-ai/DeepSeek-V3.2-TEE` |
| `chutes-vision` | `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |

## 組み込みスターター カタログ

バンドルされたフォールバック カタログには、現在の Chutes ref が含まれます:

| Model ref |
| --------- |
| `chutes/zai-org/GLM-4.7-TEE` |
| `chutes/zai-org/GLM-5-TEE` |
| `chutes/deepseek-ai/DeepSeek-V3.2-TEE` |
| `chutes/deepseek-ai/DeepSeek-R1-0528-TEE` |
| `chutes/moonshotai/Kimi-K2.5-TEE` |
| `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |
| `chutes/Qwen/Qwen3-Coder-Next-TEE` |
| `chutes/openai/gpt-oss-120b-TEE` |

## 設定例

```json5
{
  agents: {
    defaults: {
      model: { primary: "chutes/zai-org/GLM-4.7-TEE" },
      models: {
        "chutes/zai-org/GLM-4.7-TEE": { alias: "Chutes GLM 4.7" },
        "chutes/deepseek-ai/DeepSeek-V3.2-TEE": { alias: "Chutes DeepSeek V3.2" },
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="OAuth のオーバーライド">
    オプションの環境変数で OAuth フローをカスタマイズできます:

    | Variable | Purpose |
    | -------- | ------- |
    | `CHUTES_CLIENT_ID` | カスタム OAuth クライアント ID |
    | `CHUTES_CLIENT_SECRET` | カスタム OAuth クライアント シークレット |
    | `CHUTES_OAUTH_REDIRECT_URI` | カスタム リダイレクト URI |
    | `CHUTES_OAUTH_SCOPES` | カスタム OAuth スコープ |

    リダイレクト アプリの要件やヘルプについては、[Chutes OAuth docs](https://chutes.ai/docs/sign-in-with-chutes/overview)
    を参照してください。

  </Accordion>

  <Accordion title="注意">
    - API キーと OAuth の検出はどちらも同じ `chutes` プロバイダー ID を使用します。
    - Chutes モデルは `chutes/<model-id>` として登録されます。
    - 起動時に検出が失敗した場合、バンドルされた静的カタログが自動的に使用されます。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="モデル プロバイダー" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー ルール、モデル ref、フェイルオーバー動作。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference" icon="gear">
    プロバイダー設定を含む完全な設定スキーマ。
  </Card>
  <Card title="Chutes" href="https://chutes.ai" icon="arrow-up-right-from-square">
    Chutes ダッシュボードと API ドキュメント。
  </Card>
  <Card title="Chutes API キー" href="https://chutes.ai/settings/api-keys" icon="key">
    Chutes API キーを作成および管理します。
  </Card>
</CardGroup>
