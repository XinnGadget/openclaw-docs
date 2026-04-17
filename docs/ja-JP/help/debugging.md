---
read_when:
    - 推論漏えいを調査するために、生のモデル出力を確認する必要がある場合
    - 反復作業中に Gateway をウォッチモードで実行したい場合
    - 再現可能なデバッグワークフローが必要な場合
summary: 'デバッグツール: ウォッチモード、生のモデルストリーム、推論漏えいのトレース'
title: デバッグ
x-i18n:
    generated_at: "2026-04-12T23:28:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: bc31ce9b41e92a14c4309f32df569b7050b18024f83280930e53714d3bfcd5cc
    source_path: help/debugging.md
    workflow: 15
---

# デバッグ

このページでは、特にプロバイダーが通常のテキストに推論を混在させる場合の、ストリーミング出力向けデバッグヘルパーについて説明します。

## ランタイムデバッグオーバーライド

チャット内で `/debug` を使うと、**ランタイムのみ**の設定オーバーライド（ディスクではなくメモリ上）を設定できます。`/debug` はデフォルトで無効です。`commands.debug: true` で有効にしてください。
これは、`openclaw.json` を編集せずに、あまり使わない設定を切り替える必要がある場合に便利です。

例:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset` はすべてのオーバーライドをクリアし、ディスク上の設定に戻します。

## セッショントレース出力

1 つのセッション内でプラグイン所有のトレース/デバッグ行を確認したいが、完全な verbose モードは有効にしたくない場合は、`/trace` を使ってください。

例:

```text
/trace
/trace on
/trace off
```

`/trace` は、Active Memory のデバッグサマリーのような Plugin 診断に使用してください。
通常の verbose 状態/ツール出力には引き続き `/verbose` を使い、ランタイムのみの設定オーバーライドには引き続き `/debug` を使ってください。

## Gateway ウォッチモード

素早く反復作業するには、ファイルウォッチャーの下で gateway を実行します。

```bash
pnpm gateway:watch
```

これは次に対応します。

```bash
node scripts/watch-node.mjs gateway --force
```

ウォッチャーは、`src/` 配下のビルド関連ファイル、拡張機能のソースファイル、拡張機能の `package.json` と `openclaw.plugin.json` メタデータ、`tsconfig.json`、`package.json`、および `tsdown.config.ts` の変更時に再起動します。拡張機能メタデータの変更では `tsdown` の再ビルドを強制せずに gateway を再起動し、ソースと設定の変更では引き続き最初に `dist` を再ビルドします。

`gateway:watch` の後ろに任意の gateway CLI フラグを追加すると、再起動のたびにそれらが引き継がれます。同じリポジトリ/フラグセットに対して同じ watch コマンドを再実行すると、古いウォッチャーを残したままにせず、新しいものが以前のウォッチャーを置き換えるようになりました。

## 開発プロファイル + 開発 gateway (`--dev`)

状態を分離し、安全で使い捨て可能なデバッグ用セットアップを起動するには、dev プロファイルを使ってください。`--dev` フラグは **2 種類**あります。

- **グローバル `--dev`（プロファイル）:** `~/.openclaw-dev` 配下に状態を分離し、gateway ポートのデフォルトを `19001` にします（派生ポートもそれに応じて変わります）。
- **`gateway --dev`:** 必要な場合に、Gateway にデフォルト設定 + ワークスペースを自動作成させます（`BOOTSTRAP.md` はスキップ）。

推奨フロー（dev プロファイル + dev ブートストラップ）:

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

まだグローバルインストールがない場合は、`pnpm openclaw ...` で CLI を実行してください。

これにより次のことが行われます。

1. **プロファイル分離**（グローバル `--dev`）
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001`（browser/canvas もそれに応じて変わる）

2. **Dev ブートストラップ**（`gateway --dev`）
   - 必要な場合に最小構成の設定を書き込みます（`gateway.mode=local`、bind は loopback）。
   - `agent.workspace` を dev ワークスペースに設定します。
   - `agent.skipBootstrap=true` を設定します（`BOOTSTRAP.md` なし）。
   - 必要な場合にワークスペースファイルを投入します:
     `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`。
   - デフォルトの identity: **C3‑PO**（プロトコルドロイド）。
   - dev モードではチャネルプロバイダーをスキップします（`OPENCLAW_SKIP_CHANNELS=1`）。

リセットフロー（新規開始）:

```bash
pnpm gateway:dev:reset
```

注意: `--dev` は**グローバル**プロファイルフラグであり、一部のランナーでは消費されます。
明示的に指定する必要がある場合は、環境変数形式を使ってください。

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset` は、設定、認証情報、セッション、および dev ワークスペースを（`rm` ではなく `trash` を使って）消去し、その後デフォルトの dev セットアップを再作成します。

ヒント: すでに非 dev の gateway が実行中の場合（`launchd`/`systemd`）、まず停止してください。

```bash
openclaw gateway stop
```

## 生ストリームログ（OpenClaw）

OpenClaw は、フィルタリング/整形の前の**生のアシスタントストリーム**をログに記録できます。
これは、推論がプレーンテキストの delta として届いているのか（または別個の thinking ブロックとして届いているのか）を確認するための最良の方法です。

CLI で有効化するには:

```bash
pnpm gateway:watch --raw-stream
```

任意のパス上書き:

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

同等の環境変数:

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

デフォルトファイル:

`~/.openclaw/logs/raw-stream.jsonl`

## 生チャンクログ（pi-mono）

ブロックに解析される前の**生の OpenAI 互換チャンク**をキャプチャするために、pi-mono は別のロガーを公開しています。

```bash
PI_RAW_STREAM=1
```

任意のパス:

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

デフォルトファイル:

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> 注意: これは pi-mono の
> `openai-completions` プロバイダーを使うプロセスでのみ出力されます。

## 安全上の注意

- 生ストリームログには、完全なプロンプト、ツール出力、ユーザーデータが含まれる場合があります。
- ログはローカルに保持し、デバッグ後に削除してください。
- ログを共有する場合は、まずシークレットと PII をマスクしてください。
