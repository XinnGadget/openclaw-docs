---
read_when:
    - Gatewayプロセスを実行またはデバッグする場合
summary: Gatewayサービス、ライフサイクル、運用のためのランブック
title: Gatewayランブック
x-i18n:
    generated_at: "2026-04-07T04:42:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: fd2c21036e88612861ef2195b8ff7205aca31386bb11558614ade8d1a54fdebd
    source_path: gateway/index.md
    workflow: 15
---

# Gatewayランブック

このページは、Gatewayサービスの初日セットアップと継続運用のために使用します。

<CardGroup cols={2}>
  <Card title="詳細なトラブルシューティング" icon="siren" href="/ja-JP/gateway/troubleshooting">
    症状から始める診断と、正確なコマンド手順およびログシグネチャ。
  </Card>
  <Card title="設定" icon="sliders" href="/ja-JP/gateway/configuration">
    タスク指向のセットアップガイドと完全な設定リファレンス。
  </Card>
  <Card title="シークレット管理" icon="key-round" href="/ja-JP/gateway/secrets">
    SecretRefの契約、ランタイムスナップショットの挙動、移行/再読み込み操作。
  </Card>
  <Card title="シークレットプラン契約" icon="shield-check" href="/ja-JP/gateway/secrets-plan-contract">
    正確な`secrets apply`のターゲット/パスルールと、ref専用認証プロファイルの挙動。
  </Card>
</CardGroup>

## 5分でできるローカル起動

<Steps>
  <Step title="Gatewayを起動する">

```bash
openclaw gateway --port 18789
# debug/trace を stdio にミラー出力
openclaw gateway --port 18789 --verbose
# 選択したポートのリスナーを強制終了してから起動
openclaw gateway --force
```

  </Step>

  <Step title="サービスの健全性を確認する">

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
```

正常なベースライン: `Runtime: running` と `RPC probe: ok`。

  </Step>

  <Step title="チャネルの準備状態を検証する">

```bash
openclaw channels status --probe
```

到達可能なGatewayがある場合、これはアカウントごとのライブチャネルプローブと任意の監査を実行します。
Gatewayに到達できない場合、CLIはライブプローブ出力の代わりに、設定のみのチャネルサマリーへフォールバックします。

  </Step>
</Steps>

<Note>
Gateway設定の再読み込みは、アクティブな設定ファイルパスを監視します（プロファイル/状態のデフォルトから解決されるか、設定されている場合は`OPENCLAW_CONFIG_PATH`）。
デフォルトモードは`gateway.reload.mode="hybrid"`です。
最初の読み込みが成功した後、実行中のプロセスはアクティブなインメモリ設定スナップショットを提供し、再読み込みに成功するとそのスナップショットをアトミックに入れ替えます。
</Note>

## ランタイムモデル

- ルーティング、コントロールプレーン、チャネル接続のための常時稼働プロセスが1つ。
- 以下のための単一の多重化ポート:
  - WebSocket control/RPC
  - HTTP APIs、OpenAI互換（`/v1/models`, `/v1/embeddings`, `/v1/chat/completions`, `/v1/responses`, `/tools/invoke`）
  - Control UI とフック
- デフォルトのバインドモード: `loopback`。
- デフォルトで認証が必要です。共有シークレット構成では
  `gateway.auth.token` / `gateway.auth.password`（または
  `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`）を使用し、非loopbackの
  リバースプロキシ構成では`gateway.auth.mode: "trusted-proxy"`を使用できます。

## OpenAI互換エンドポイント

OpenClawの現在最も効果の高い互換サーフェスは次のとおりです。

- `GET /v1/models`
- `GET /v1/models/{id}`
- `POST /v1/embeddings`
- `POST /v1/chat/completions`
- `POST /v1/responses`

このセットが重要な理由:

- ほとんどのOpen WebUI、LobeChat、LibreChat連携は最初に`/v1/models`をプローブします。
- 多くのRAGおよびメモリパイプラインは`/v1/embeddings`を想定しています。
- エージェントネイティブのクライアントはますます`/v1/responses`を好むようになっています。

計画メモ:

- `/v1/models`はagent-firstです。`openclaw`、`openclaw/default`、`openclaw/<agentId>`を返します。
- `openclaw/default`は、常に設定済みのデフォルトエージェントにマップされる安定したエイリアスです。
- バックエンドのプロバイダー/モデルオーバーライドを行いたい場合は`x-openclaw-model`を使用してください。それ以外では、選択されたエージェントの通常のモデルと埋め込み設定がそのまま制御を保持します。

これらはすべてメインのGatewayポートで動作し、Gateway HTTP APIの他の部分と同じ信頼されたオペレーター認証境界を使用します。

### ポートとバインドの優先順位

| 設定 | 解決順序 |
| ------------ | ------------------------------------------------------------- |
| Gatewayポート | `--port` → `OPENCLAW_GATEWAY_PORT` → `gateway.port` → `18789` |
| バインドモード | CLI/override → `gateway.bind` → `loopback` |

### ホットリロードモード

| `gateway.reload.mode` | 挙動 |
| --------------------- | ------------------------------------------ |
| `off`                 | 設定の再読み込みなし |
| `hot`                 | ホットセーフな変更のみ適用 |
| `restart`             | 再読み込みが必要な変更時に再起動 |
| `hybrid` (default)    | 安全ならホット適用し、必要なら再起動 |

## オペレーターコマンドセット

```bash
openclaw gateway status
openclaw gateway status --deep   # システムレベルのサービススキャンを追加
openclaw gateway status --json
openclaw gateway install
openclaw gateway restart
openclaw gateway stop
openclaw secrets reload
openclaw logs --follow
openclaw doctor
```

`gateway status --deep`は追加のサービス検出（LaunchDaemons/systemd system
units/schtasks）のためのものであり、より深いRPCヘルスプローブではありません。

## 複数のGateway（同一ホスト）

ほとんどのインストールでは、マシンごとにGatewayは1つで十分です。1つのGatewayで複数の
agentsとchannelsをホストできます。

複数のGatewayが必要なのは、意図的に分離またはレスキューボットを使いたい場合だけです。

便利な確認:

```bash
openclaw gateway status --deep
openclaw gateway probe
```

期待されること:

- `gateway status --deep`は`Other gateway-like services detected (best effort)`を報告し、
  古いlaunchd/systemd/schtasksインストールがまだ残っている場合にクリーンアップのヒントを表示することがあります。
- `gateway probe`は、複数のターゲットが応答した場合に`multiple reachable gateways`を警告することがあります。
- それが意図的な場合は、Gatewayごとにポート、設定/状態、ワークスペースルートを分離してください。

詳細なセットアップ: [/gateway/multiple-gateways](/ja-JP/gateway/multiple-gateways)。

## リモートアクセス

推奨: Tailscale/VPN。
代替: SSHトンネル。

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

その後、クライアントをローカルで`ws://127.0.0.1:18789`に接続します。

<Warning>
SSHトンネルはGateway認証を回避しません。共有シークレット認証では、クライアントは
トンネル経由でも引き続き`token`/`password`を送る必要があります。IDを伴うモードでは、
リクエストは引き続きその認証パスを満たす必要があります。
</Warning>

参照: [Remote Gateway](/ja-JP/gateway/remote), [Authentication](/ja-JP/gateway/authentication), [Tailscale](/ja-JP/gateway/tailscale)。

## 監督実行とサービスライフサイクル

本番に近い信頼性のためには、監督付き実行を使用してください。

<Tabs>
  <Tab title="macOS (launchd)">

```bash
openclaw gateway install
openclaw gateway status
openclaw gateway restart
openclaw gateway stop
```

LaunchAgentラベルは`ai.openclaw.gateway`（デフォルト）または`ai.openclaw.<profile>`（名前付きプロファイル）です。`openclaw doctor`はサービス設定のドリフトを監査および修復します。

  </Tab>

  <Tab title="Linux (systemd user)">

```bash
openclaw gateway install
systemctl --user enable --now openclaw-gateway[-<profile>].service
openclaw gateway status
```

ログアウト後も維持するには、lingeringを有効にします。

```bash
sudo loginctl enable-linger <user>
```

カスタムインストールパスが必要な場合の手動ユーザーユニット例:

```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group

[Install]
WantedBy=default.target
```

  </Tab>

  <Tab title="Windows (native)">

```powershell
openclaw gateway install
openclaw gateway status --json
openclaw gateway restart
openclaw gateway stop
```

ネイティブWindowsの管理対象起動では、`OpenClaw Gateway`
（または名前付きプロファイルでは`OpenClaw Gateway (<profile>)`）という名前のタスク スケジューラを使用します。タスク スケジューラの
作成が拒否された場合、OpenClawは状態ディレクトリ内の`gateway.cmd`を指すユーザーごとのスタートアップフォルダーランチャーへフォールバックします。

  </Tab>

  <Tab title="Linux (system service)">

マルチユーザー/常時稼働ホストにはシステムユニットを使用します。

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-gateway[-<profile>].service
```

ユーザーユニットと同じサービス本体を使用しますが、
`/etc/systemd/system/openclaw-gateway[-<profile>].service`の下にインストールし、
`openclaw`バイナリが別の場所にある場合は`ExecStart=`を調整してください。

  </Tab>
</Tabs>

## 1台のホスト上での複数のGateway

ほとんどの構成では**Gatewayは1つ**で十分です。
複数使うのは、厳格な分離/冗長化のためだけにしてください（たとえばレスキュープロファイル）。

インスタンスごとのチェックリスト:

- 一意の`gateway.port`
- 一意の`OPENCLAW_CONFIG_PATH`
- 一意の`OPENCLAW_STATE_DIR`
- 一意の`agents.defaults.workspace`

例:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json OPENCLAW_STATE_DIR=~/.openclaw-a openclaw gateway --port 19001
OPENCLAW_CONFIG_PATH=~/.openclaw/b.json OPENCLAW_STATE_DIR=~/.openclaw-b openclaw gateway --port 19002
```

参照: [Multiple gateways](/ja-JP/gateway/multiple-gateways)。

### 開発プロファイルのクイックパス

```bash
openclaw --dev setup
openclaw --dev gateway --allow-unconfigured
openclaw --dev status
```

デフォルトでは、分離された状態/設定とベースGatewayポート`19001`が含まれます。

## プロトコルのクイックリファレンス（オペレータービュー）

- 最初のクライアントフレームは`connect`でなければなりません。
- Gatewayは`hello-ok`スナップショット（`presence`, `health`, `stateVersion`, `uptimeMs`, limits/policy）を返します。
- `hello-ok.features.methods` / `events`は保守的な検出リストであり、
  呼び出し可能なすべてのヘルパールートの自動生成ダンプではありません。
- リクエスト: `req(method, params)` → `res(ok/payload|error)`。
- 一般的なイベントには`connect.challenge`、`agent`、`chat`、
  `session.message`、`session.tool`、`sessions.changed`、`presence`、`tick`、
  `health`、`heartbeat`、pairing/approvalライフサイクルイベント、および`shutdown`が含まれます。

agent実行は2段階です。

1. 即時の受理ack（`status:"accepted"`）
2. 最終完了レスポンス（`status:"ok"|"error"`）。その間に`agent`イベントがストリームされます。

完全なプロトコルドキュメント: [Gateway Protocol](/ja-JP/gateway/protocol)。

## 運用チェック

### ライブネス

- WSを開いて`connect`を送信する。
- `hello-ok`レスポンスとスナップショットを期待する。

### レディネス

```bash
openclaw gateway status
openclaw channels status --probe
openclaw health
```

### ギャップ回復

イベントは再送されません。シーケンスギャップがある場合は、続行前に状態（`health`, `system-presence`）を更新してください。

## 一般的な障害シグネチャ

| シグネチャ | 想定される問題 |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `refusing to bind gateway ... without auth`                    | 有効なGateway認証パスなしでの非loopbackバインド |
| `another gateway instance is already listening` / `EADDRINUSE` | ポート競合 |
| `Gateway start blocked: set gateway.mode=local`                | 設定がremote modeになっている、または破損した設定からlocal-modeスタンプが欠落している |
| `unauthorized` during connect                                  | クライアントとGatewayの間の認証不一致 |

完全な診断手順については、[Gateway Troubleshooting](/ja-JP/gateway/troubleshooting)を使用してください。

## 安全性の保証

- Gatewayプロトコルクライアントは、Gatewayが利用できない場合に即座に失敗します（暗黙の直接チャネルフォールバックはありません）。
- 無効な/`connect`でない最初のフレームは拒否され、接続が閉じられます。
- 正常なシャットダウンでは、ソケットを閉じる前に`shutdown`イベントが発行されます。

---

関連:

- [Troubleshooting](/ja-JP/gateway/troubleshooting)
- [Background Process](/ja-JP/gateway/background-process)
- [Configuration](/ja-JP/gateway/configuration)
- [Health](/ja-JP/gateway/health)
- [Doctor](/ja-JP/gateway/doctor)
- [Authentication](/ja-JP/gateway/authentication)
