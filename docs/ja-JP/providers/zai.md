---
read_when:
    - OpenClawでZ.AI / GLMモデルを使いたい
    - シンプルなZAI_API_KEYのセットアップが必要
summary: OpenClawでZ.AI（GLMモデル）を使う
title: Z.AI
x-i18n:
    generated_at: "2026-04-08T04:41:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66cbd9813ee28d202dcae34debab1b0cf9927793acb00743c1c62b48d9e381f9
    source_path: providers/zai.md
    workflow: 15
---

# Z.AI

Z.AIは**GLM**モデル向けのAPIプラットフォームです。GLM向けのREST APIを提供し、認証にはAPIキーを使用します。
APIキーはZ.AIコンソールで作成してください。OpenClawは、Z.AI APIキーとともに`zai`プロバイダーを使用します。

## CLIセットアップ

```bash
# エンドポイント自動検出を使った汎用APIキー設定
openclaw onboard --auth-choice zai-api-key

# Coding Plan Global、Coding Planユーザーに推奨
openclaw onboard --auth-choice zai-coding-global

# Coding Plan CN（中国リージョン）、Coding Planユーザーに推奨
openclaw onboard --auth-choice zai-coding-cn

# General API
openclaw onboard --auth-choice zai-global

# General API CN（中国リージョン）
openclaw onboard --auth-choice zai-cn
```

## 設定スニペット

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

`zai-api-key`を使うと、OpenClawはキーから対応するZ.AIエンドポイントを検出し、
正しいベースURLを自動的に適用できます。特定のCoding PlanまたはGeneral APIサーフェスを
強制したい場合は、明示的なリージョン選択を使用してください。

## バンドル済みGLMカタログ

OpenClawは現在、バンドル済みの`zai`プロバイダーに次をシードしています。

- `glm-5.1`
- `glm-5`
- `glm-5-turbo`
- `glm-5v-turbo`
- `glm-4.7`
- `glm-4.7-flash`
- `glm-4.7-flashx`
- `glm-4.6`
- `glm-4.6v`
- `glm-4.5`
- `glm-4.5-air`
- `glm-4.5-flash`
- `glm-4.5v`

## 注意

- GLMモデルは`zai/<model>`として利用できます（例: `zai/glm-5`）。
- デフォルトのバンドル済みモデル参照: `zai/glm-5.1`
- 不明な`glm-5*` IDも、IDが現在のGLM-5ファミリーの形式に一致する場合、
  `glm-4.7`テンプレートからプロバイダー所有のメタデータを合成することで、
  バンドル済みプロバイダーパス上で引き続き解決されます。
- Z.AIのツールコールストリーミングでは、`tool_stream`がデフォルトで有効です。無効にするには、
  `agents.defaults.models["zai/<model>"].params.tool_stream`を`false`に設定してください。
- モデルファミリーの概要は[/providers/glm](/ja-JP/providers/glm)を参照してください。
- Z.AIは、APIキーを使ったBearer認証を使用します。
