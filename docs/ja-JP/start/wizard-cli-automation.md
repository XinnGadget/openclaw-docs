---
read_when:
    - スクリプトまたはCIでオンボーディングを自動化しているとき
    - 特定のprovider向けに非対話の例が必要なとき
sidebarTitle: CLI automation
summary: OpenClaw CLIのスクリプト化されたオンボーディングとagent設定
title: CLI Automation
x-i18n:
    generated_at: "2026-04-07T04:46:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: bca2dd6e482a16b27284fc76319e936e8df0ff5558134827c19f6875436cc652
    source_path: start/wizard-cli-automation.md
    workflow: 15
---

# CLI Automation

`openclaw onboard` を自動化するには `--non-interactive` を使用します。

<Note>
`--json` は非対話モードを意味しません。スクリプトでは `--non-interactive`（および `--workspace`）を使用してください。
</Note>

## 基本的な非対話の例

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

機械可読な要約が必要な場合は `--json` を追加します。

認証プロファイルにプレーンテキスト値ではなくenv参照のrefを保存するには `--secret-input-mode ref` を使用します。
env refと、設定済みprovider ref（`file` または `exec`）の間での対話的選択は、オンボーディングフローで利用できます。

非対話の `ref` モードでは、provider env varがプロセス環境に設定されている必要があります。
対応するenv varなしでインラインkeyフラグを渡すと、現在は即座に失敗します。

例:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

## Provider別の例

<AccordionGroup>
  <Accordion title="Anthropic API keyの例">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice apiKey \
      --anthropic-api-key "$ANTHROPIC_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Geminiの例">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice gemini-api-key \
      --gemini-api-key "$GEMINI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Z.AIの例">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice zai-api-key \
      --zai-api-key "$ZAI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Vercel AI Gatewayの例">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice ai-gateway-api-key \
      --ai-gateway-api-key "$AI_GATEWAY_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Cloudflare AI Gatewayの例">
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
  <Accordion title="Moonshotの例">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice moonshot-api-key \
      --moonshot-api-key "$MOONSHOT_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Mistralの例">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice mistral-api-key \
      --mistral-api-key "$MISTRAL_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Syntheticの例">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice synthetic-api-key \
      --synthetic-api-key "$SYNTHETIC_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="OpenCodeの例">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice opencode-zen \
      --opencode-zen-api-key "$OPENCODE_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
    Goカタログを使う場合は、`--auth-choice opencode-go --opencode-go-api-key "$OPENCODE_API_KEY"` に切り替えてください。
  </Accordion>
  <Accordion title="Ollamaの例">
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
  <Accordion title="Custom providerの例">
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

    `--custom-api-key` は任意です。省略した場合、オンボーディングは `CUSTOM_API_KEY` を確認します。

    refモードの例:

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

    このモードでは、オンボーディングは `apiKey` を `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }` として保存します。

  </Accordion>
</AccordionGroup>

Anthropic setup-tokenはサポートされるオンボーディングtoken経路として引き続き利用可能ですが、OpenClawは現在、利用可能であればClaude CLIの再利用を優先します。
本番運用では、Anthropic API keyを優先してください。

## 別のagentを追加する

独自のworkspace、
sessions、auth profilesを持つ別agentを作成するには `openclaw agents add <name>` を使用します。`--workspace` なしで実行するとウィザードが起動します。

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

設定される内容:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

注意:

- デフォルトworkspaceは `~/.openclaw/workspace-<agentId>` に従います。
- 受信メッセージをルーティングするには `bindings` を追加してください（ウィザードでも設定できます）。
- 非対話フラグ: `--model`, `--agent-dir`, `--bind`, `--non-interactive`。

## 関連ドキュメント

- オンボーディングハブ: [オンボーディング (CLI)](/ja-JP/start/wizard)
- 完全なリファレンス: [CLI Setup Reference](/ja-JP/start/wizard-cli-reference)
- コマンドリファレンス: [`openclaw onboard`](/cli/onboard)
