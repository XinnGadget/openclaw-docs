---
read_when:
    - OpenClawでArcee AIを使いたいとき
    - API keyの環境変数またはCLIの認証選択が必要なとき
summary: Arcee AIのセットアップ（認証 + model選択）
title: Arcee AI
x-i18n:
    generated_at: "2026-04-07T04:45:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb04909a708fec08dd2c8c863501b178f098bc4818eaebad38aea264157969d8
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai) は、OpenAI互換APIを通じてTrinityファミリーのmixture-of-experts modelへのアクセスを提供します。すべてのTrinity modelはApache 2.0ライセンスです。

Arcee AI modelsは、Arcee platformから直接、または [OpenRouter](/ja-JP/providers/openrouter) 経由で利用できます。

- Provider: `arcee`
- Auth: `ARCEEAI_API_KEY`（直接）または `OPENROUTER_API_KEY`（OpenRouter経由）
- API: OpenAI互換
- Base URL: `https://api.arcee.ai/api/v1`（直接）または `https://openrouter.ai/api/v1`（OpenRouter）

## クイックスタート

1. [Arcee AI](https://chat.arcee.ai/) または [OpenRouter](https://openrouter.ai/keys) でAPI keyを取得します。

2. API keyを設定します（推奨: Gateway用に保存）:

```bash
# Direct (Arcee platform)
openclaw onboard --auth-choice arceeai-api-key

# Via OpenRouter
openclaw onboard --auth-choice arceeai-openrouter
```

3. デフォルトmodelを設定します:

```json5
{
  agents: {
    defaults: {
      model: { primary: "arcee/trinity-large-thinking" },
    },
  },
}
```

## 非対話の例

```bash
# Direct (Arcee platform)
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-api-key \
  --arceeai-api-key "$ARCEEAI_API_KEY"

# Via OpenRouter
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-openrouter \
  --openrouter-api-key "$OPENROUTER_API_KEY"
```

## 環境に関する注意

Gatewayがdaemon（launchd/systemd）として動作している場合は、`ARCEEAI_API_KEY`
（または `OPENROUTER_API_KEY`）がそのプロセスから利用できることを確認してください（たとえば
`~/.openclaw/.env` または `env.shellEnv` 経由）。

## 組み込みカタログ

OpenClawには現在、このバンドル済みArcee catalogが含まれています:

| Model ref                      | Name                   | Input | Context | Cost (in/out per 1M) | Notes                                     |
| ------------------------------ | ---------------------- | ----- | ------- | -------------------- | ----------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text  | 256K    | $0.25 / $0.90        | デフォルトmodel; reasoning有効          |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text  | 128K    | $0.25 / $1.00        | 汎用; 400B params、13B active  |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text  | 128K    | $0.045 / $0.15       | 高速でコスト効率が高い; function calling |

同じmodel refは、直接設定とOpenRouter設定の両方で使えます（例: `arcee/trinity-large-thinking`）。

オンボーディングpresetは、`arcee/trinity-large-thinking` をデフォルトmodelとして設定します。

## サポートされる機能

- Streaming
- Tool use / function calling
- Structured output（JSON modeおよびJSON schema）
- Extended thinking（Trinity Large Thinking）
