---
read_when:
    - リポジトリのスクリプトを実行する場合
    - '`./scripts` 配下のスクリプトを追加または変更する場合'
summary: リポジトリスクリプトの目的、範囲、安全上の注意
title: スクリプト
x-i18n:
    generated_at: "2026-04-08T02:15:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3ecf1e9327929948fb75f80e306963af49b353c0aa8d3b6fa532ca964ff8b975
    source_path: help/scripts.md
    workflow: 15
---

# スクリプト

`scripts/` ディレクトリには、ローカルワークフローや運用タスク向けの補助スクリプトが含まれています。
タスクが明確にスクリプトに結び付いている場合はこれらを使用し、それ以外では CLI を優先してください。

## 規約

- スクリプトは、ドキュメントやリリースチェックリストで参照されていない限り **任意** です。
- 利用可能な場合は CLI サーフェスを優先してください（例: 認証監視には `openclaw models status --check` を使用します）。
- スクリプトはホスト固有であることを前提とし、新しいマシンで実行する前に内容を確認してください。

## 認証監視スクリプト

認証監視については [Authentication](/ja-JP/gateway/authentication) で説明されています。`scripts/` 配下のスクリプトは、systemd / Termux の phone ワークフロー向けの任意の追加機能です。

## GitHub 読み取りヘルパー

通常の `gh` は書き込み操作で個人ログインのままにしつつ、リポジトリスコープの読み取り呼び出しに GitHub App の installation token を使いたい場合は `scripts/gh-read` を使用してください。

必須の環境変数:

- `OPENCLAW_GH_READ_APP_ID`
- `OPENCLAW_GH_READ_PRIVATE_KEY_FILE`

任意の環境変数:

- リポジトリベースの installation 検索をスキップしたい場合は `OPENCLAW_GH_READ_INSTALLATION_ID`
- 要求する読み取り権限サブセットをカンマ区切りで上書きしたい場合は `OPENCLAW_GH_READ_PERMISSIONS`

リポジトリ解決順序:

- `gh ... -R owner/repo`
- `GH_REPO`
- `git remote origin`

例:

- `scripts/gh-read pr view 123`
- `scripts/gh-read run list -R openclaw/openclaw`
- `scripts/gh-read api repos/openclaw/openclaw/pulls/123`

## スクリプトを追加する場合

- スクリプトは焦点を絞り、文書化してください。
- 関連するドキュメントに短い項目を追加してください（なければ新しく作成してください）。
