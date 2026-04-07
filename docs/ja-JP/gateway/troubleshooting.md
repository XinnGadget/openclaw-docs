---
read_when:
    - トラブルシューティングハブから、より深い診断のためにここを案内された
    - 正確なコマンド付きの、安定した症状ベースの手順書セクションが必要
summary: Gateway、チャネル、自動化、ノード、ブラウザーに関する詳細なトラブルシューティング手順書
title: トラブルシューティング
x-i18n:
    generated_at: "2026-04-07T04:42:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0202e8858310a0bfc1c994cd37b01c3b2d6c73c8a74740094e92dc3c4c36729
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# Gatewayのトラブルシューティング

このページは詳細な手順書です。
まず高速なトリアージフローを見たい場合は [/help/troubleshooting](/ja-JP/help/troubleshooting) から始めてください。

## コマンド手順

まず次のコマンドを、この順番で実行してください。

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

正常時に期待されるシグナル:

- `openclaw gateway status` に `Runtime: running` と `RPC probe: ok` が表示される。
- `openclaw doctor` が、ブロッキングな設定/サービス問題がないことを報告する。
- `openclaw channels status --probe` が、アカウントごとのライブなトランスポート状態と、
  サポートされている場合は `works` や `audit ok` などのプローブ/監査結果を表示する。

## 長いコンテキストに追加利用量が必要なAnthropic 429

ログ/エラーに次が含まれている場合に使用します:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

確認ポイント:

- 選択されているAnthropic Opus/Sonnetモデルで `params.context1m: true` になっている。
- 現在のAnthropic認証情報が長コンテキスト利用の対象外になっている。
- リクエストが、1Mベータ経路を必要とする長いセッション/モデル実行でのみ失敗している。

修正方法:

1. そのモデルの `context1m` を無効にして、通常のコンテキストウィンドウへフォールバックする。
2. 長コンテキストリクエストの対象となるAnthropic認証情報を使うか、Anthropic APIキーへ切り替える。
3. Anthropicの長コンテキストリクエストが拒否されたときにも実行が継続するよう、フォールバックモデルを設定する。

関連:

- [/providers/anthropic](/ja-JP/providers/anthropic)
- [/reference/token-use](/ja-JP/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/ja-JP/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## 返信がない

チャネルは稼働しているのに何も応答しない場合は、何かを再接続する前にルーティングとポリシーを確認してください。

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

確認ポイント:

- DM送信者に対してペアリングが保留中になっている。
- グループでのメンション制御（`requireMention`、`mentionPatterns`）。
- チャネル/グループの許可リスト不一致。

よくあるシグネチャ:

- `drop guild message (mention required` → メンションされるまでグループメッセージは無視される。
- `pairing request` → 送信者に承認が必要。
- `blocked` / `allowlist` → 送信者/チャネルがポリシーによってフィルタされた。

関連:

- [/channels/troubleshooting](/ja-JP/channels/troubleshooting)
- [/channels/pairing](/ja-JP/channels/pairing)
- [/channels/groups](/ja-JP/channels/groups)

## ダッシュボードControl UI接続

dashboard/control UI が接続できない場合は、URL、認証モード、セキュアコンテキスト前提を確認してください。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

確認ポイント:

- 正しいプローブURLとダッシュボードURL。
- クライアントとGateway間の認証モード/トークン不一致。
- デバイスIDが必要な場面でHTTPを使っている。

よくあるシグネチャ:

- `device identity required` → 非セキュアコンテキスト、またはデバイス認証の欠如。
- `origin not allowed` → ブラウザーの `Origin` が `gateway.controlUi.allowedOrigins`
  に含まれていない
  （または明示的な許可リストなしで、非loopbackのブラウザーoriginから接続している）。
- `device nonce required` / `device nonce mismatch` → クライアントが
  チャレンジベースのデバイス認証フロー（`connect.challenge` + `device.nonce`）を完了していない。
- `device signature invalid` / `device signature expired` → クライアントが現在のハンドシェイクに対して誤った
  ペイロード（または古いタイムスタンプ）に署名した。
- `AUTH_TOKEN_MISMATCH` と `canRetryWithDeviceToken=true` → クライアントはキャッシュされたデバイストークンで1回だけ信頼済み再試行ができる。
- そのキャッシュトークン再試行では、ペアリング済み
  デバイストークンとともに保存されたキャッシュ済みスコープセットが再利用される。明示的な `deviceToken` / 明示的な `scopes` 呼び出し側は、要求したスコープセットをそのまま保持する。
- その再試行経路以外では、接続認証の優先順位は、明示的な共有
  トークン/パスワードが先で、その後に明示的な `deviceToken`、保存済みデバイストークン、
  ブートストラップトークンの順になる。
- 非同期のTailscale Serve Control UI経路では、同じ `{scope, ip}` に対する失敗した試行は
  リミッターが失敗を記録する前に直列化される。そのため、同じクライアントからの2件の不正な同時再試行では、2件とも単純な不一致になる代わりに、2件目で `retry later`
  が表面化することがある。
- ブラウザーoriginのloopbackクライアントから `too many failed authentication attempts (retry later)` → 同じ正規化済み `Origin` からの繰り返し失敗は一時的にロックアウトされる。別のlocalhost originは別バケットを使う。
- その再試行後も `unauthorized` が繰り返される → 共有トークン/デバイストークンのずれ。トークン設定を更新し、必要ならデバイストークンを再承認/ローテーションする。
- `gateway connect failed:` → ホスト/ポート/URLターゲットが間違っている。

### 認証詳細コードのクイックマップ

失敗した `connect` レスポンスの `error.details.code` を使って、次のアクションを選んでください:

| Detail code                  | 意味                                                   | 推奨アクション                                                                                                                                                                                                                                                                           |
| ---------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AUTH_TOKEN_MISSING`         | クライアントが必要な共有トークンを送信しなかった。     | クライアントにトークンを貼り付け/設定して再試行してください。ダッシュボード経路では: `openclaw config get gateway.auth.token` を実行し、それをControl UI設定に貼り付けます。                                                                                                        |
| `AUTH_TOKEN_MISMATCH`        | 共有トークンがGateway認証トークンと一致しなかった。    | `canRetryWithDeviceToken=true` の場合は、1回だけ信頼済み再試行を許可してください。キャッシュトークン再試行では保存済みの承認スコープが再利用されます。明示的な `deviceToken` / `scopes` 呼び出し側は要求したスコープを保持します。それでも失敗する場合は、[token drift recovery checklist](/cli/devices#token-drift-recovery-checklist) を実行してください。 |
| `AUTH_DEVICE_TOKEN_MISMATCH` | デバイスごとにキャッシュされたトークンが古いか失効している。 | [devices CLI](/cli/devices) を使ってデバイストークンをローテーション/再承認してから再接続してください。                                                                                                                                                                               |
| `PAIRING_REQUIRED`           | デバイスIDは認識されているが、このロールでは承認されていない。 | 保留中のリクエストを承認してください: `openclaw devices list` の後に `openclaw devices approve <requestId>` を実行します。                                                                                                                                                             |

デバイス認証v2の移行確認:

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

ログにnonce/signatureエラーが表示される場合は、接続クライアントを更新し、次を確認してください:

1. `connect.challenge` を待機する
2. チャレンジに束縛されたペイロードに署名する
3. 同じチャレンジnonceを使って `connect.params.device.nonce` を送信する

`openclaw devices rotate` / `revoke` / `remove` が予期せず拒否される場合:

- ペアリング済みデバイストークンセッションが管理できるのは、呼び出し元が
  `operator.admin` も持っていない限り**自分自身の**デバイスだけ
- `openclaw devices rotate --scope ...` は、呼び出し元セッションがすでに保持している
  operatorスコープだけを要求できる

関連:

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/ja-JP/gateway/configuration) （Gateway認証モード）
- [/gateway/trusted-proxy-auth](/ja-JP/gateway/trusted-proxy-auth)
- [/gateway/remote](/ja-JP/gateway/remote)
- [/cli/devices](/cli/devices)

## Gatewayサービスが動作していない

サービスはインストールされているが、プロセスが起動したままにならない場合に使用します。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # システムレベルのサービスもスキャン
```

確認ポイント:

- 終了ヒント付きの `Runtime: stopped`。
- サービス設定の不一致（`Config (cli)` vs `Config (service)`）。
- ポート/リスナーの競合。
- `--deep` 使用時の追加のlaunchd/systemd/schtasksインストール。
- `Other gateway-like services detected (best effort)` のクリーンアップヒント。

よくあるシグネチャ:

- `Gateway start blocked: set gateway.mode=local` または `existing config is missing gateway.mode` → local Gatewayモードが有効になっていない、または設定ファイルが壊れて `gateway.mode` が失われた。修正: 設定で `gateway.mode="local"` を設定するか、`openclaw onboard --mode local` / `openclaw setup` を再実行して想定されるlocal-mode設定を再作成する。Podman経由でOpenClawを実行している場合、デフォルトの設定パスは `~/.openclaw/openclaw.json`。
- `refusing to bind gateway ... without auth` → 有効なGateway認証経路（トークン/パスワード、または設定されている場合はtrusted-proxy）なしで非loopback bindをしようとしている。
- `another gateway instance is already listening` / `EADDRINUSE` → ポート競合。
- `Other gateway-like services detected (best effort)` → 古い、または並行するlaunchd/systemd/schtasksユニットが存在する。ほとんどのセットアップでは1台のマシンに1つのGatewayを保つべきです。複数必要な場合は、ポート + config/state/workspace を分離してください。[/gateway#multiple-gateways-same-host](/ja-JP/gateway#multiple-gateways-same-host) を参照してください。

関連:

- [/gateway/background-process](/ja-JP/gateway/background-process)
- [/gateway/configuration](/ja-JP/gateway/configuration)
- [/gateway/doctor](/ja-JP/gateway/doctor)

## Gatewayプローブ警告

`openclaw gateway probe` が何かには到達しているが、それでも警告ブロックを表示する場合に使用します。

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

確認ポイント:

- JSON出力の `warnings[].code` と `primaryTargetId`。
- 警告がSSHフォールバック、複数Gateway、スコープ不足、または未解決の認証参照に関するものか。

よくあるシグネチャ:

- `SSH tunnel failed to start; falling back to direct probes.` → SSHセットアップに失敗したが、コマンドは引き続き設定済み/loopbackターゲットへの直接プローブを試みた。
- `multiple reachable gateways detected` → 複数のターゲットが応答した。通常、これは意図的な複数Gatewayセットアップか、古い/重複したリスナーを意味する。
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → 接続は成功したが、詳細RPCがスコープ制限されている。デバイスIDをペアリングするか、`operator.read` を持つ認証情報を使用する。
- 未解決の `gateway.auth.*` / `gateway.remote.*` SecretRef 警告テキスト → 失敗したターゲットに対して、このコマンド経路では認証情報が利用できなかった。

関連:

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/ja-JP/gateway#multiple-gateways-same-host)
- [/gateway/remote](/ja-JP/gateway/remote)

## チャネルは接続済みだがメッセージが流れない

チャネル状態は接続済みなのにメッセージフローが死んでいる場合は、ポリシー、権限、チャネル固有の配信ルールに集中してください。

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

確認ポイント:

- DMポリシー（`pairing`、`allowlist`、`open`、`disabled`）。
- グループ許可リストとメンション要件。
- 欠けているチャネルAPI権限/スコープ。

よくあるシグネチャ:

- `mention required` → グループのメンションポリシーによりメッセージが無視された。
- `pairing` / 承認保留トレース → 送信者が未承認。
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → チャネル認証/権限の問題。

関連:

- [/channels/troubleshooting](/ja-JP/channels/troubleshooting)
- [/channels/whatsapp](/ja-JP/channels/whatsapp)
- [/channels/telegram](/ja-JP/channels/telegram)
- [/channels/discord](/ja-JP/channels/discord)

## Cronとheartbeat配信

cronまたはheartbeatが実行されなかった、または配信されなかった場合は、まずスケジューラー状態を確認し、その後に配信先を確認してください。

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

確認ポイント:

- Cronが有効で、次回起動時刻が存在する。
- ジョブ実行履歴の状態（`ok`、`skipped`、`error`）。
- Heartbeatスキップ理由（`quiet-hours`、`requests-in-flight`、`alerts-disabled`、`empty-heartbeat-file`、`no-tasks-due`）。

よくあるシグネチャ:

- `cron: scheduler disabled; jobs will not run automatically` → cronが無効。
- `cron: timer tick failed` → スケジューラーティックが失敗。ファイル/ログ/ランタイムエラーを確認。
- `heartbeat skipped` と `reason=quiet-hours` → アクティブ時間帯の外。
- `heartbeat skipped` と `reason=empty-heartbeat-file` → `HEARTBEAT.md` は存在するが空行/Markdownヘッダーしか含まれていないため、OpenClawがモデル呼び出しをスキップした。
- `heartbeat skipped` と `reason=no-tasks-due` → `HEARTBEAT.md` に `tasks:` ブロックはあるが、このティックで期限の来ているタスクがない。
- `heartbeat: unknown accountId` → heartbeat配信先の無効なaccount id。
- `heartbeat skipped` と `reason=dm-blocked` → heartbeatターゲットがDM形式の宛先に解決されたが、`agents.defaults.heartbeat.directPolicy`（またはエージェントごとのオーバーライド）が `block` に設定されている。

関連:

- [/automation/cron-jobs#troubleshooting](/ja-JP/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/ja-JP/automation/cron-jobs)
- [/gateway/heartbeat](/ja-JP/gateway/heartbeat)

## ペアリング済みノードでツールが失敗する

ノードはペアリング済みだがツールが失敗する場合は、フォアグラウンド、権限、承認状態を切り分けてください。

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

確認ポイント:

- ノードがオンラインで、想定される機能を持っている。
- カメラ/マイク/位置情報/画面に対するOS権限が付与されている。
- exec承認と許可リスト状態。

よくあるシグネチャ:

- `NODE_BACKGROUND_UNAVAILABLE` → ノードアプリをフォアグラウンドにする必要がある。
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → OS権限が不足している。
- `SYSTEM_RUN_DENIED: approval required` → exec承認が保留中。
- `SYSTEM_RUN_DENIED: allowlist miss` → コマンドが許可リストによってブロックされた。

関連:

- [/nodes/troubleshooting](/ja-JP/nodes/troubleshooting)
- [/nodes/index](/ja-JP/nodes/index)
- [/tools/exec-approvals](/ja-JP/tools/exec-approvals)

## browserツールが失敗する

Gateway自体は正常なのにbrowserツール操作が失敗する場合に使用します。

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

確認ポイント:

- `plugins.allow` が設定されており、`browser` を含んでいるか。
- 有効なブラウザー実行ファイルパス。
- CDPプロファイルに到達可能か。
- `existing-session` / `user` プロファイル向けのローカルChromeが利用可能か。

よくあるシグネチャ:

- `unknown command "browser"` または `unknown command 'browser'` → バンドルされたbrowserプラグインが `plugins.allow` によって除外されている。
- `browser.enabled=true` なのにbrowserツールが欠如/利用不可 → `plugins.allow` が `browser` を除外しているため、プラグインが読み込まれていない。
- `Failed to start Chrome CDP on port` → ブラウザープロセスの起動に失敗した。
- `browser.executablePath not found` → 設定されたパスが無効。
- `browser.cdpUrl must be http(s) or ws(s)` → 設定されたCDP URLが `file:` や `ftp:` など未対応のスキームを使用している。
- `browser.cdpUrl has invalid port` → 設定されたCDP URLのポートが不正、または範囲外。
- `No Chrome tabs found for profile="user"` → Chrome MCP attachプロファイルに開いているローカルChromeタブがない。
- `Remote CDP for profile "<name>" is not reachable` → 設定されたリモートCDPエンドポイントにGatewayホストから到達できない。
- `Browser attachOnly is enabled ... not reachable` または `Browser attachOnly is enabled and CDP websocket ... is not reachable` → attach-onlyプロファイルに到達可能なターゲットがない、またはHTTPエンドポイントは応答したがCDP WebSocketをまだ開けなかった。
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → 現在のGatewayインストールには完全なPlaywrightパッケージが含まれていない。ARIAスナップショットと基本的なページスクリーンショットは依然として動作するが、ナビゲーション、AIスナップショット、CSSセレクターによる要素スクリーンショット、PDFエクスポートは利用できないまま。
- `fullPage is not supported for element screenshots` → スクリーンショット要求で `--full-page` と `--ref` または `--element` を混在させている。
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → Chrome MCP / `existing-session` のスクリーンショット呼び出しでは、CSS `--element` ではなく、ページキャプチャまたはスナップショット `--ref` を使用する必要がある。
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → Chrome MCPのアップロードフックではCSSセレクターではなくスナップショット参照が必要。
- `existing-session file uploads currently support one file at a time.` → Chrome MCPプロファイルでは、呼び出しごとに1ファイルずつアップロードする。
- `existing-session dialog handling does not support timeoutMs.` → Chrome MCPプロファイルのダイアログフックはtimeoutのオーバーライドをサポートしない。
- `response body is not supported for existing-session profiles yet.` → `responsebody` は依然として管理対象ブラウザーまたは生のCDPプロファイルが必要。
- attach-onlyまたはリモートCDPプロファイルで古いviewport / dark-mode / locale / offlineオーバーライドが残る → アクティブな制御セッションを閉じ、Gateway全体を再起動せずにPlaywright/CDPエミュレーション状態を解放するには `openclaw browser stop --browser-profile <name>` を実行する。

関連:

- [/tools/browser-linux-troubleshooting](/ja-JP/tools/browser-linux-troubleshooting)
- [/tools/browser](/ja-JP/tools/browser)

## アップグレード後に突然壊れた場合

アップグレード後の不具合の多くは、設定のずれか、より厳格なデフォルトが適用されるようになったことが原因です。

### 1) 認証とURLオーバーライドの挙動が変わった

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

確認事項:

- `gateway.mode=remote` の場合、CLI呼び出しがremoteを対象にしており、ローカルサービス自体は正常な可能性がある。
- 明示的な `--url` 呼び出しは、保存済み認証情報にフォールバックしない。

よくあるシグネチャ:

- `gateway connect failed:` → URLターゲットが間違っている。
- `unauthorized` → エンドポイントには到達しているが認証が間違っている。

### 2) Bindと認証のガードレールがより厳格になった

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

確認事項:

- 非loopback bind（`lan`、`tailnet`、`custom`）には、有効なGateway認証経路が必要: 共有トークン/パスワード認証、または正しく設定された非loopbackの `trusted-proxy` デプロイ。
- `gateway.token` のような古いキーは `gateway.auth.token` の代わりにはならない。

よくあるシグネチャ:

- `refusing to bind gateway ... without auth` → 有効なGateway認証経路なしで非loopback bindしている。
- ランタイムは動作中なのに `RPC probe: failed` → Gatewayは生きているが、現在の認証/URLではアクセスできない。

### 3) ペアリングとデバイスID状態が変わった

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

確認事項:

- dashboard/nodes 向けの保留中デバイス承認。
- ポリシーやID変更後の、保留中DMペアリング承認。

よくあるシグネチャ:

- `device identity required` → デバイス認証が満たされていない。
- `pairing required` → 送信者/デバイスに承認が必要。

確認後もサービス設定とランタイムの不一致が続く場合は、同じプロファイル/状態ディレクトリからサービスメタデータを再インストールしてください。

```bash
openclaw gateway install --force
openclaw gateway restart
```

関連:

- [/gateway/pairing](/ja-JP/gateway/pairing)
- [/gateway/authentication](/ja-JP/gateway/authentication)
- [/gateway/background-process](/ja-JP/gateway/background-process)
