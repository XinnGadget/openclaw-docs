---
read_when:
    - OpenClawを更新するとき
    - 更新後に何かが壊れたとき
summary: OpenClawを安全に更新する方法（グローバルインストールまたはソース）、およびロールバック戦略
title: 更新
x-i18n:
    generated_at: "2026-04-06T03:08:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: ca9fff0776b9f5977988b649e58a5d169e5fa3539261cb02779d724d4ca92877
    source_path: install/updating.md
    workflow: 15
---

# 更新

OpenClawを最新の状態に保ってください。

## 推奨: `openclaw update`

最も速い更新方法です。インストール種別（npm または git）を検出し、最新バージョンを取得して、`openclaw doctor` を実行し、Gatewayを再起動します。

```bash
openclaw update
```

チャンネルを切り替えるか、特定のバージョンを対象にするには:

```bash
openclaw update --channel beta
openclaw update --tag main
openclaw update --dry-run   # 適用せずにプレビュー
```

`--channel beta` はbetaを優先しますが、betaタグが存在しない場合や最新の安定版リリースより古い場合、ランタイムは stable/latest にフォールバックします。単発のパッケージ更新でnpmの生のbeta dist-tagを使いたい場合は、`--tag beta` を使用してください。

チャンネルの意味については、[Development channels](/ja-JP/install/development-channels) を参照してください。

## 代替: インストーラーを再実行する

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

オンボーディングをスキップするには `--no-onboard` を追加します。ソースインストールの場合は、`--install-method git --no-onboard` を渡してください。

## 代替: 手動で npm、pnpm、または bun を使う

```bash
npm i -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

```bash
bun add -g openclaw@latest
```

## 自動アップデーター

自動アップデーターはデフォルトでオフです。`~/.openclaw/openclaw.json` で有効にします。

```json5
{
  update: {
    channel: "stable",
    auto: {
      enabled: true,
      stableDelayHours: 6,
      stableJitterHours: 12,
      betaCheckIntervalHours: 1,
    },
  },
}
```

| Channel  | 動作 |
| -------- | ---- |
| `stable` | `stableDelayHours` 待機した後、`stableJitterHours` 全体にわたる決定的なジッターで適用されます（段階的ロールアウト）。 |
| `beta`   | `betaCheckIntervalHours` ごとにチェックし（デフォルト: 1時間ごと）、即座に適用します。 |
| `dev`    | 自動適用は行いません。手動で `openclaw update` を使ってください。 |

Gatewayは起動時にも更新ヒントをログ出力します（`update.checkOnStart: false` で無効化）。

## 更新後

<Steps>

### doctorを実行する

```bash
openclaw doctor
```

configを移行し、DMポリシーを監査し、Gatewayの健全性を確認します。詳細: [Doctor](/ja-JP/gateway/doctor)

### Gatewayを再起動する

```bash
openclaw gateway restart
```

### 確認する

```bash
openclaw health
```

</Steps>

## ロールバック

### バージョンを固定する（npm）

```bash
npm i -g openclaw@<version>
openclaw doctor
openclaw gateway restart
```

ヒント: `npm view openclaw version` で現在公開されているバージョンを表示できます。

### コミットを固定する（ソース）

```bash
git fetch origin
git checkout "$(git rev-list -n 1 --before=\"2026-01-01\" origin/main)"
pnpm install && pnpm build
openclaw gateway restart
```

最新に戻すには: `git checkout main && git pull`。

## 行き詰まった場合

- もう一度 `openclaw doctor` を実行し、出力を注意深く読んでください。
- ソースチェックアウトで `openclaw update --channel dev` を使う場合、必要に応じてアップデーターは自動的に `pnpm` をブートストラップします。pnpm/corepack のブートストラップエラーが表示された場合は、`pnpm` を手動でインストールするか、`corepack` を再度有効にしてから更新を再実行してください。
- 確認: [Troubleshooting](/ja-JP/gateway/troubleshooting)
- Discordで質問する: [https://discord.gg/clawd](https://discord.gg/clawd)

## 関連

- [Install Overview](/ja-JP/install) — すべてのインストール方法
- [Doctor](/ja-JP/gateway/doctor) — 更新後のヘルスチェック
- [Migrating](/ja-JP/install/migrating) — メジャーバージョン移行ガイド
