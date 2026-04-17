---
read_when:
    - OpenClaw で Hugging Face Inference を使いたい場合
    - HF トークンの環境変数または CLI の認証選択肢が必要な場合
summary: Hugging Face Inference のセットアップ（認証 + モデル選択）
title: Hugging Face（Inference）
x-i18n:
    generated_at: "2026-04-12T23:31:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7787fce1acfe81adb5380ab1c7441d661d03c574da07149c037d3b6ba3c8e52a
    source_path: providers/huggingface.md
    workflow: 15
---

# Hugging Face（Inference）

[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) は、単一のルーター API を通じて OpenAI 互換のチャット補完を提供します。1 つのトークンで、多数のモデル（DeepSeek、Llama など）を利用できます。OpenClaw は **OpenAI 互換エンドポイント**（チャット補完のみ）を使用します。text-to-image、埋め込み、speech については、[HF inference clients](https://huggingface.co/docs/api-inference/quicktour) を直接使用してください。

- Provider: `huggingface`
- Auth: `HUGGINGFACE_HUB_TOKEN` または `HF_TOKEN`（**Make calls to Inference Providers** 権限を持つ fine-grained token）
- API: OpenAI 互換（`https://router.huggingface.co/v1`）
- 課金: 単一の HF トークン。[pricing](https://huggingface.co/docs/inference-providers/pricing) は provider の料金に従い、無料枠があります。

## はじめに

<Steps>
  <Step title="fine-grained token を作成する">
    [Hugging Face Settings Tokens](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained) に移動し、新しい fine-grained token を作成します。

    <Warning>
    そのトークンでは **Make calls to Inference Providers** 権限を有効にする必要があります。そうしないと API リクエストは拒否されます。
    </Warning>

  </Step>
  <Step title="オンボーディングを実行する">
    provider ドロップダウンで **Hugging Face** を選択し、プロンプトが表示されたら API キーを入力します。

    ```bash
    openclaw onboard --auth-choice huggingface-api-key
    ```

  </Step>
  <Step title="デフォルトモデルを選択する">
    **Default Hugging Face model** ドロップダウンで、使用したいモデルを選択します。有効なトークンがある場合、一覧は Inference API から読み込まれます。そうでない場合は組み込みの一覧が表示されます。選択内容はデフォルトモデルとして保存されます。

    後から設定でデフォルトモデルを設定または変更することもできます。

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/deepseek-ai/DeepSeek-R1" },
        },
      },
    }
    ```

  </Step>
  <Step title="モデルが利用可能であることを確認する">
    ```bash
    openclaw models list --provider huggingface
    ```
  </Step>
</Steps>

### 非対話セットアップ

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice huggingface-api-key \
  --huggingface-api-key "$HF_TOKEN"
```

これにより `huggingface/deepseek-ai/DeepSeek-R1` がデフォルトモデルとして設定されます。

## モデル ID

モデル参照は `huggingface/<org>/<model>` 形式（Hub スタイル ID）を使用します。以下の一覧は **GET** `https://router.huggingface.co/v1/models` に基づいています。利用できるカタログにはさらに多くのモデルが含まれる場合があります。

| モデル | 参照（`huggingface/` を先頭に付ける） |
| ---------------------- | ----------------------------------- |
| DeepSeek R1 | `deepseek-ai/DeepSeek-R1` |
| DeepSeek V3.2 | `deepseek-ai/DeepSeek-V3.2` |
| Qwen3 8B | `Qwen/Qwen3-8B` |
| Qwen2.5 7B Instruct | `Qwen/Qwen2.5-7B-Instruct` |
| Qwen3 32B | `Qwen/Qwen3-32B` |
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct` |
| Llama 3.1 8B Instruct | `meta-llama/Llama-3.1-8B-Instruct` |
| GPT-OSS 120B | `openai/gpt-oss-120b` |
| GLM 4.7 | `zai-org/GLM-4.7` |
| Kimi K2.5 | `moonshotai/Kimi-K2.5` |

<Tip>
任意のモデル ID に `:fastest` または `:cheapest` を付けることができます。デフォルト順序は [Inference Provider settings](https://hf.co/settings/inference-providers) で設定してください。完全な一覧については [Inference Providers](https://huggingface.co/docs/inference-providers) および **GET** `https://router.huggingface.co/v1/models` を参照してください。
</Tip>

## 高度な詳細

<AccordionGroup>
  <Accordion title="モデル検出とオンボーディングのドロップダウン">
    OpenClaw は、**Inference エンドポイントを直接呼び出して**モデルを検出します。

    ```bash
    GET https://router.huggingface.co/v1/models
    ```

    （任意: 完全な一覧を取得するには `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` または `$HF_TOKEN` を送信します。認証なしでは一部のエンドポイントがサブセットのみを返すことがあります。）レスポンスは OpenAI スタイルの `{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }` です。

    Hugging Face API キー（オンボーディング、`HUGGINGFACE_HUB_TOKEN`、または `HF_TOKEN` 経由）が設定されている場合、OpenClaw はこの GET を使って利用可能な chat-completion モデルを検出します。**対話セットアップ**中は、トークンを入力した後に、この一覧（またはリクエストに失敗した場合は組み込みカタログ）から生成された **Default Hugging Face model** ドロップダウンが表示されます。ランタイム時（たとえば Gateway 起動時）も、キーが存在する場合、OpenClaw は再度 **GET** `https://router.huggingface.co/v1/models` を呼び出してカタログを更新します。この一覧は、組み込みカタログ（コンテキストウィンドウやコストなどのメタデータ用）とマージされます。リクエストが失敗した場合、またはキーが設定されていない場合は、組み込みカタログのみが使用されます。

  </Accordion>

  <Accordion title="モデル名、エイリアス、およびポリシー接尾辞">
    - **API からの名前:** モデル表示名は、API が `name`、`title`、または `display_name` を返す場合、**GET /v1/models から補完されます**。それ以外の場合は、モデル ID から導出されます（例: `deepseek-ai/DeepSeek-R1` は「DeepSeek R1」になります）。
    - **表示名を上書きする:** モデルごとに設定でカスタムラベルを設定でき、CLI や UI で好みの表示にできます。

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1 (fast)" },
            "huggingface/deepseek-ai/DeepSeek-R1:cheapest": { alias: "DeepSeek R1 (cheap)" },
          },
        },
      },
    }
    ```

    - **ポリシー接尾辞:** OpenClaw の組み込み Hugging Face ドキュメントとヘルパーは、現在これら 2 つの接尾辞を組み込みのポリシーバリアントとして扱います。
      - **`:fastest`** — 最高スループット。
      - **`:cheapest`** — 出力トークンあたりの最低コスト。

      これらは `models.providers.huggingface.models` に個別のエントリとして追加することも、接尾辞付きで `model.primary` に設定することもできます。また、デフォルトの provider 順序は [Inference Provider settings](https://hf.co/settings/inference-providers) で設定できます（接尾辞なし = その順序を使用）。

    - **設定マージ:** `models.providers.huggingface.models` 内の既存エントリ（たとえば `models.json` 内）は、設定マージ時に保持されます。そのため、そこに設定したカスタムの `name`、`alias`、またはモデルオプションは維持されます。

  </Accordion>

  <Accordion title="環境とデーモンセットアップ">
    Gateway がデーモン（launchd/systemd）として実行される場合は、`HUGGINGFACE_HUB_TOKEN` または `HF_TOKEN` がそのプロセスで利用可能であることを確認してください（たとえば `~/.openclaw/.env` または `env.shellEnv` 経由）。

    <Note>
    OpenClaw は `HUGGINGFACE_HUB_TOKEN` と `HF_TOKEN` の両方を env var エイリアスとして受け付けます。どちらでも機能します。両方が設定されている場合は、`HUGGINGFACE_HUB_TOKEN` が優先されます。
    </Note>

  </Accordion>

  <Accordion title="設定: Qwen をフォールバックにした DeepSeek R1">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-R1",
            fallbacks: ["huggingface/Qwen/Qwen3-8B"],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1" },
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="設定: cheapest と fastest バリアントを使う Qwen">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen3-8B" },
          models: {
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
            "huggingface/Qwen/Qwen3-8B:cheapest": { alias: "Qwen3 8B (cheapest)" },
            "huggingface/Qwen/Qwen3-8B:fastest": { alias: "Qwen3 8B (fastest)" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="設定: エイリアス付きの DeepSeek + Llama + GPT-OSS">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-V3.2",
            fallbacks: [
              "huggingface/meta-llama/Llama-3.3-70B-Instruct",
              "huggingface/openai/gpt-oss-120b",
            ],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-V3.2": { alias: "DeepSeek V3.2" },
            "huggingface/meta-llama/Llama-3.3-70B-Instruct": { alias: "Llama 3.3 70B" },
            "huggingface/openai/gpt-oss-120b": { alias: "GPT-OSS 120B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="設定: ポリシー接尾辞付きの複数の Qwen と DeepSeek">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest" },
          models: {
            "huggingface/Qwen/Qwen2.5-7B-Instruct": { alias: "Qwen2.5 7B" },
            "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest": { alias: "Qwen2.5 7B (cheap)" },
            "huggingface/deepseek-ai/DeepSeek-R1:fastest": { alias: "DeepSeek R1 (fast)" },
            "huggingface/meta-llama/Llama-3.1-8B-Instruct": { alias: "Llama 3.1 8B" },
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Model providers" href="/ja-JP/concepts/model-providers" icon="layers">
    すべての provider、モデル参照、フェイルオーバー動作の概要。
  </Card>
  <Card title="Model selection" href="/ja-JP/concepts/models" icon="brain">
    モデルの選び方と設定方法。
  </Card>
  <Card title="Inference Providers docs" href="https://huggingface.co/docs/inference-providers" icon="book">
    Hugging Face Inference Providers の公式ドキュメント。
  </Card>
  <Card title="Configuration" href="/ja-JP/gateway/configuration" icon="gear">
    完全な設定リファレンス。
  </Card>
</CardGroup>
