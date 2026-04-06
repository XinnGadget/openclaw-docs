---
read_when:
    - スクリプトまたはCIでオンボーディングを自動化している
    - 特定のプロバイダー向けの非対話型例が必要である
sidebarTitle: CLI automation
summary: OpenClaw CLI向けのスクリプト化されたオンボーディングとエージェント設定
title: CLI自動化
x-i18n:
    generated_at: "2026-04-06T03:12:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 878ea3fa9f2a75cff9f1a803ccb8a52a1219102e2970883ad18e3aaec5967fd2
    source_path: start/wizard-cli-automation.md
    workflow: 15
---

# CLI自動化

`openclaw onboard`を自動化するには`--non-interactive`を使用します。

<Note>
`--json`は非対話型モードを意味しません。スクリプトでは`--non-interactive`（および`--workspace`）を使用してください。
</Note>

## ベースラインの非対話型例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

機械可読な要約が必要な場合は`--json`を追加してください。

認証プロファイルに平文値の代わりに環境変数ベースの参照を保存するには、`--secret-input-mode ref`を使用します。
環境変数参照と、設定済みプロバイダー参照（`file`または`exec`）の間の対話的選択は、オンボーディングフローで利用できます。

非対話型の`ref`モードでは、プロバイダー環境変数がプロセス環境に設定されている必要があります。
対応する環境変数なしでインラインのキーフラグを渡すと、現在は即座に失敗します。

例:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

## プロバイダー固有の例

<AccordionGroup>
  <Accordion title="Anthropic API key example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice apiKey \
      --anthropic-api-key "$ANTHROPIC_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Gemini example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice gemini-api-key \
      --gemini-api-key "$GEMINI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Z.AI example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice zai-api-key \
      --zai-api-key "$ZAI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Vercel AI Gateway example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice ai-gateway-api-key \
      --ai-gateway-api-key "$AI_GATEWAY_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Cloudflare AI Gateway example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice cloudflare-ai-gateway-api-key \
      --cloudflare-ai-gateway-account-id "your-account-id" \
      --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
      --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Moonshot example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice moonshot-api-key \
      --moonshot-api-key "$MOONSHOT_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Mistral example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice mistral-api-key \
      --mistral-api-key "$MISTRAL_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Synthetic example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice synthetic-api-key \
      --synthetic-api-key "$SYNTHETIC_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="OpenCode example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice opencode-zen \
      --opencode-zen-api-key "$OPENCODE_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
    Goカタログには`--auth-choice opencode-go --opencode-go-api-key "$OPENCODE_API_KEY"`へ切り替えてください。
  </Accordion>
  <Accordion title="Ollama example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice ollama \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Custom provider example">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice custom-api-key \
      --custom-base-url "https://llm.example.com/v1" \
      --custom-model-id "foo-large" \
      --custom-api-key "$CUSTOM_API_KEY" \
      --custom-provider-id "my-custom" \
      --custom-compatibility anthropic \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```

    `--custom-api-key`は任意です。省略した場合、オンボーディングは`CUSTOM_API_KEY`を確認します。

    refモードのバリアント:

    ```bash
    export CUSTOM_API_KEY="your-key"
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice custom-api-key \
      --custom-base-url "https://llm.example.com/v1" \
      --custom-model-id "foo-large" \
      --secret-input-mode ref \
      --custom-provider-id "my-custom" \
      --custom-compatibility anthropic \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```

    このモードでは、オンボーディングは`apiKey`を`{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`として保存します。

  </Accordion>
</AccordionGroup>

Anthropic setup-tokenは、レガシー/手動のオンボーディング経路として再び利用可能です。
AnthropicがOpenClawユーザーに対し、OpenClawの
Claudeログイン経路には**Extra Usage**が必要であると伝えている前提で使用してください。本番用途では、Anthropic APIキーを推奨します。

## 別のエージェントを追加する

独自のワークスペース、セッション、および認証プロファイルを持つ別のエージェントを作成するには、`openclaw agents add <name>`を使用します。`--workspace`なしで実行すると、ウィザードが起動します。

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

これで設定されるもの:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

メモ:

- デフォルトのワークスペースは`~/.openclaw/workspace-<agentId>`に従います。
- 受信メッセージをルーティングするには`bindings`を追加してください（ウィザードでも実行できます）。
- 非対話型フラグ: `--model`, `--agent-dir`, `--bind`, `--non-interactive`。

## 関連ドキュメント

- オンボーディングハブ: [Onboarding (CLI)](/ja-JP/start/wizard)
- 完全なリファレンス: [CLI Setup Reference](/ja-JP/start/wizard-cli-reference)
- コマンドリファレンス: [`openclaw onboard`](/cli/onboard)
