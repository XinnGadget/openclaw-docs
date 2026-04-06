---
read_when:
    - reasoning leakage を確認するために生のモデル出力を調べる必要がある
    - 反復しながらGatewayをwatchモードで実行したい
    - 再現可能なデバッグワークフローが必要である
summary: 'デバッグツール: watchモード、生のモデルストリーム、reasoning leakage の追跡'
title: デバッグ
x-i18n:
    generated_at: "2026-04-06T03:07:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4bc72e8d6cad3a1acaad066f381c82309583fabf304c589e63885f2685dc704e
    source_path: help/debugging.md
    workflow: 15
---

# デバッグ

このページでは、特にプロバイダーが reasoning を通常のテキストに混在させる場合の、ストリーミング出力向けデバッグ支援を扱います。

## ランタイムデバッグオーバーライド

チャットで `/debug` を使うと、**ランタイムのみ**の設定オーバーライド（ディスクではなくメモリ）を設定できます。
`/debug` はデフォルトで無効です。`commands.debug: true` で有効にします。
これは、`openclaw.json` を編集せずにわかりにくい設定を切り替えたいときに便利です。

例:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset` はすべてのオーバーライドを消去し、ディスク上の設定に戻します。

## Gateway watchモード

素早く反復するには、ファイルウォッチャー配下でgatewayを実行します。

```bash
pnpm gateway:watch
```

これは次に対応します。

```bash
node scripts/watch-node.mjs gateway --force
```

ウォッチャーは、`src/` 配下のビルド関連ファイル、拡張機能のソースファイル、
拡張機能の `package.json` と `openclaw.plugin.json` メタデータ、`tsconfig.json`、
`package.json`、`tsdown.config.ts` に変更があると再起動します。拡張機能メタデータの変更では
`tsdown` の再ビルドを強制せずにgatewayを再起動し、ソースと設定の変更では引き続き最初に `dist` を再ビルドします。

`gateway:watch` の後ろにgateway CLIフラグを追加すると、
再起動のたびにそれらが引き渡されます。同じリポジトリ/フラグセットに対して同じwatchコマンドを再実行すると、
重複するウォッチャー親プロセスを残すのではなく、古いウォッチャーを置き換えるようになりました。

## devプロファイル + dev gateway（`--dev`）

状態を分離し、安全で破棄可能なデバッグ用セットアップを起動するには、devプロファイルを使用します。`--dev` フラグは **2種類** あります。

- **グローバル `--dev`（プロファイル）:** `~/.openclaw-dev` 配下に状態を分離し、
  Gatewayポートをデフォルトで `19001` にします（派生ポートもそれに合わせてずれます）。
- **`gateway --dev`:** 不足している場合に、デフォルト設定 +
  ワークスペースをGatewayが自動作成します（BOOTSTRAP.md はスキップ）。

推奨フロー（devプロファイル + devブートストラップ）:

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

まだグローバルインストールがない場合は、`pnpm openclaw ...` でCLIを実行してください。

これが行うこと:

1. **プロファイル分離**（グローバル `--dev`）
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001`（browser/canvas もそれに応じてずれます）

2. **devブートストラップ**（`gateway --dev`）
   - 不足している場合は最小構成の設定を書き込みます（`gateway.mode=local`、bind loopback）。
   - `agent.workspace` をdevワークスペースに設定します。
   - `agent.skipBootstrap=true` を設定します（BOOTSTRAP.md なし）。
   - 不足している場合は次のワークスペースファイルをシードします:
     `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`。
   - デフォルトのidentity: **C3‑PO**（プロトコルドロイド）。
   - devモードではチャネルプロバイダーをスキップします（`OPENCLAW_SKIP_CHANNELS=1`）。

リセットフロー（新規開始）:

```bash
pnpm gateway:dev:reset
```

注意: `--dev` は**グローバル**なプロファイルフラグであり、一部のランナーでは吸収されます。
明示的に指定する必要がある場合は、環境変数形式を使ってください。

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset` は設定、認証情報、セッション、devワークスペースを（`rm` ではなく
`trash` を使って）消去し、その後デフォルトのdevセットアップを再作成します。

ヒント: すでに非devのgatewayが実行中（launchd/systemd）であれば、先に停止してください。

```bash
openclaw gateway stop
```

## 生ストリームログ（OpenClaw）

OpenClaw は、フィルタリング/整形の前の**生のassistantストリーム**を記録できます。
これにより、reasoning がプレーンテキストのdeltaとして到着しているのか
（あるいは別個のthinkingブロックとして到着しているのか）を確認するのに最適です。

CLIで有効にします。

```bash
pnpm gateway:watch --raw-stream
```

任意のパス上書き:

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

等価な環境変数:

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

デフォルトファイル:

`~/.openclaw/logs/raw-stream.jsonl`

## 生チャンクログ（pi-mono）

ブロックへ解析される前の**生のOpenAI互換チャンク**を取得するために、
pi-mono は別個のロガーを公開しています。

```bash
PI_RAW_STREAM=1
```

任意のパス:

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

デフォルトファイル:

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> 注意: これは、pi-mono の
> `openai-completions` プロバイダーを使用するプロセスでのみ出力されます。

## 安全性に関する注意

- 生ストリームログには、完全なプロンプト、ツール出力、ユーザーデータが含まれることがあります。
- ログはローカルに保持し、デバッグ後に削除してください。
- ログを共有する場合は、まずシークレットとPIIを除去してください。
