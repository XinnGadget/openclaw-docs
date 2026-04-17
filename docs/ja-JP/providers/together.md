---
read_when:
    - Together AI を OpenClaw で使用したい場合
    - API キーの env var または CLI の認証方法を選択する必要があります
summary: Together AI のセットアップ（認証 + モデル選択）
title: Together AI
x-i18n:
    generated_at: "2026-04-12T23:33:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 33531a1646443ac2e46ee1fbfbb60ec71093611b022618106e8e5435641680ac
    source_path: providers/together.md
    workflow: 15
---

# Together AI

[Together AI](https://together.ai) は、Llama、DeepSeek、Kimi などを含む主要なオープンソース
モデルへのアクセスを、統一された API を通じて提供します。

| Property | Value                         |
| -------- | ----------------------------- |
| プロバイダー | `together`                    |
| 認証     | `TOGETHER_API_KEY`            |
| API      | OpenAI互換             |
| Base URL | `https://api.together.xyz/v1` |

## はじめに

<Steps>
  <Step title="API キーを取得する">
    API キーを
    [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys) で作成します。
  </Step>
  <Step title="オンボーディングを実行する">
    ```bash
    openclaw onboard --auth-choice together-api-key
    ```
  </Step>
  <Step title="デフォルトモデルを設定する">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "together/moonshotai/Kimi-K2.5" },
        },
      },
    }
    ```
  </Step>
</Steps>

### 非対話型の例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

<Note>
オンボーディングプリセットでは、デフォルト
モデルとして `together/moonshotai/Kimi-K2.5` が設定されます。
</Note>

## 組み込みカタログ

OpenClaw には、このバンドルされた Together カタログが含まれています。

| Model ref                                                    | Name                                   | Input       | Context    | Notes                            |
| ------------------------------------------------------------ | -------------------------------------- | ----------- | ---------- | -------------------------------- |
| `together/moonshotai/Kimi-K2.5`                              | Kimi K2.5                              | テキスト、画像 | 262,144    | デフォルトモデル、reasoning 有効 |
| `together/zai-org/GLM-4.7`                                   | GLM 4.7 Fp8                            | テキスト        | 202,752    | 汎用テキストモデル       |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`           | Llama 3.3 70B Instruct Turbo           | テキスト        | 131,072    | 高速な instruction モデル           |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`         | Llama 4 Scout 17B 16E Instruct         | テキスト、画像 | 10,000,000 | マルチモーダル                       |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | テキスト、画像 | 20,000,000 | マルチモーダル                       |
| `together/deepseek-ai/DeepSeek-V3.1`                         | DeepSeek V3.1                          | テキスト        | 131,072    | 汎用テキストモデル               |
| `together/deepseek-ai/DeepSeek-R1`                           | DeepSeek R1                            | テキスト        | 131,072    | reasoning モデル                  |
| `together/moonshotai/Kimi-K2-Instruct-0905`                  | Kimi K2-Instruct 0905                  | テキスト        | 262,144    | 補助的な Kimi テキストモデル        |

## 動画生成

バンドルされた `together` Plugin は、
共有 `video_generate` ツールを通じた動画生成も登録します。

| Property             | Value                                 |
| -------------------- | ------------------------------------- |
| デフォルト動画モデル  | `together/Wan-AI/Wan2.2-T2V-A14B`     |
| モード                | テキストから動画、単一画像参照 |
| 対応パラメーター | `aspectRatio`, `resolution`           |

Together をデフォルトの動画プロバイダーとして使用するには、次のようにします。

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "together/Wan-AI/Wan2.2-T2V-A14B",
      },
    },
  },
}
```

<Tip>
共有ツールパラメーター、
プロバイダー選択、フェイルオーバー動作については [Video Generation](/ja-JP/tools/video-generation) を参照してください。
</Tip>

<AccordionGroup>
  <Accordion title="環境に関する注記">
    Gateway がデーモン（launchd/systemd）として実行される場合は、
    `TOGETHER_API_KEY` がそのプロセスから利用できることを確認してください（たとえば
    `~/.openclaw/.env` または `env.shellEnv` 経由）。

    <Warning>
    対話シェルでのみ設定されたキーは、デーモン管理された
    Gateway プロセスからは見えません。永続的に利用できるようにするには、
    `~/.openclaw/.env` または `env.shellEnv` config を使用してください。
    </Warning>

  </Accordion>

  <Accordion title="トラブルシューティング">
    - キーが機能することを確認する: `openclaw models list --provider together`
    - モデルが表示されない場合は、API キーが Gateway プロセスに対して正しい
      環境に設定されていることを確認してください。
    - モデル参照は `together/<model-id>` 形式を使用します。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="モデルプロバイダー" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダールール、モデル参照、フェイルオーバー動作。
  </Card>
  <Card title="動画生成" href="/ja-JP/tools/video-generation" icon="video">
    共有動画生成ツールのパラメーターとプロバイダー選択。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference" icon="gear">
    プロバイダー設定を含む完全な config schema。
  </Card>
  <Card title="Together AI" href="https://together.ai" icon="arrow-up-right-from-square">
    Together AI ダッシュボード、API ドキュメント、料金。
  </Card>
</CardGroup>
