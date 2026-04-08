---
read_when:
    - OpenClawでGLMモデルを使いたい
    - モデルの命名規則と設定方法が必要
summary: GLMモデルファミリーの概要と、OpenClawでの使い方
title: GLMモデル
x-i18n:
    generated_at: "2026-04-08T04:41:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 79a55acfa139847b4b85dbc09f1068cbd2febb1e49f984a23ea9e3b43bc910eb
    source_path: providers/glm.md
    workflow: 15
---

# GLMモデル

GLMは、Z.AIプラットフォームで利用できる**モデルファミリー**（企業ではありません）です。OpenClawでは、GLM
モデルは`zai`プロバイダーと、`zai/glm-5`のようなモデルIDを通じて利用します。

## CLIセットアップ

```bash
# エンドポイント自動検出を使った汎用APIキー設定
openclaw onboard --auth-choice zai-api-key

# Coding Plan Global。Coding Planユーザーに推奨
openclaw onboard --auth-choice zai-coding-global

# Coding Plan CN（中国リージョン）。Coding Planユーザーに推奨
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
正しいベースURLを自動的に適用できます。特定のCoding PlanまたはGeneral APIの利用先を
明示的に固定したい場合は、リージョンを明示した選択肢を使用してください。

## 現在バンドルされているGLMモデル

OpenClawは現在、バンドルされた`zai`プロバイダーに以下のGLM参照を初期登録しています。

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

- GLMのバージョンと提供状況は変更されることがあります。最新情報はZ.AIのドキュメントを確認してください。
- デフォルトでバンドルされているモデル参照は`zai/glm-5.1`です。
- プロバイダーの詳細は[/providers/zai](/ja-JP/providers/zai)を参照してください。
