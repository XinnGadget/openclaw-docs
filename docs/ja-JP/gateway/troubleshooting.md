---
read_when:
    - トラブルシューティングハブから、より深い診断のためにここへ案内されました
    - 正確なコマンドを含む、症状ベースの安定したランブックセクションが必要です
summary: Gateway、チャネル、自動化、ノード、ブラウザー向けの詳細なトラブルシューティングランブック
title: トラブルシューティング
x-i18n:
    generated_at: "2026-04-11T02:45:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7ef2faccba26ede307861504043a6415bc1f12dc64407771106f63ddc5b107f5
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# Gatewayトラブルシューティング

このページは詳細なランブックです。  
まず高速なトリアージ手順を見たい場合は[/help/troubleshooting](/ja-JP/help/troubleshooting)から始めてください。

## コマンドラダー

まず、次の順番でこれらを実行してください。

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

正常時に期待されるシグナル:

- `openclaw gateway status` に `Runtime: running` と `RPC probe: ok` が表示される。
- `openclaw doctor` が、ブロッキングする設定/サービスの問題なしと報告する。
- `openclaw channels status --probe` が、アカウントごとのライブなトランスポート状態と、対応している場合は `works` や `audit ok` のような probe/audit 結果を表示する。

## 長いコンテキストでAnthropic 429の追加使用量が必要

ログやエラーに次が含まれる場合に使用してください:  
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

確認ポイント:

- 選択されたAnthropic Opus/Sonnetモデルで `params.context1m: true` になっている。
- 現在のAnthropic認証情報が長いコンテキスト利用の対象外である。
- リクエストが、1Mベータ経路を必要とする長いセッション/モデル実行でのみ失敗する。

修正方法:

1. そのモデルの `context1m` を無効にして、通常のコンテキストウィンドウにフォールバックする。
2. 長いコンテキストリクエストの対象となるAnthropic認証情報を使うか、Anthropic APIキーに切り替える。
3. Anthropicの長いコンテキストリクエストが拒否されたときにも実行が継続するよう、フォールバックモデルを設定する。

関連:

- [/providers/anthropic](/ja-JP/providers/anthropic)
- [/reference/token-use](/ja-JP/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/ja-JP/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## ローカルのOpenAI互換バックエンドは直接probeには通るが、agent実行は失敗する

次の場合に使用してください:

- `curl ... /v1/models` は動作する
- 小さな直接 `/v1/chat/completions` 呼び出しは動作する
- OpenClawのモデル実行が通常のagentターンでのみ失敗する

```bash
curl http://127.0.0.1:1234/v1/models
curl http://127.0.0.1:1234/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"<id>","messages":[{"role":"user","content":"hi"}],"stream":false}'
openclaw infer model run --model <provider/model> --prompt "hi" --json
openclaw logs --follow
```

確認ポイント:

- 小さな直接呼び出しは成功するが、OpenClaw実行は大きなプロンプトでのみ失敗する
- バックエンドエラーで `messages[].content` が文字列を期待している
- より大きいプロンプトトークン数や完全なagentランタイムプロンプトでのみ現れるバックエンドクラッシュ

よくあるシグネチャ:

- `messages[...].content: invalid type: sequence, expected a string` → バックエンドが構造化されたChat Completionsのcontent partsを拒否している。修正: `models.providers.<provider>.models[].compat.requiresStringContent: true` を設定する。
- 小さな直接リクエストは成功するが、OpenClawのagent実行がバックエンド/モデルクラッシュで失敗する（例: 一部の`inferrs`ビルド上のGemma）→ OpenClawのトランスポートはすでに正しい可能性が高く、バックエンドがより大きなagentランタイムのプロンプト形状で失敗している。
- ツールを無効にすると失敗は減るが消えない → 圧力の一部はツールスキーマだったが、残っている問題は依然として上流のモデル/サーバー容量またはバックエンドバグ。

修正方法:

1. 文字列専用のChat Completionsバックエンドに対して `compat.requiresStringContent: true` を設定する。
2. OpenClawのツールスキーマサーフェスを安定して処理できないモデル/バックエンドに対して `compat.supportsTools: false` を設定する。
3. 可能な範囲でプロンプト圧力を下げる: より小さいワークスペースブートストラップ、より短いセッション履歴、より軽量なローカルモデル、または長いコンテキストのサポートがより強いバックエンドを使う。
4. 小さな直接リクエストが引き続き成功する一方で、OpenClawのagentターンがバックエンド内部でなおクラッシュする場合は、上流サーバー/モデルの制限として扱い、受け入れられるペイロード形状を添えてそこで再現報告を出す。

関連:

- [/gateway/local-models](/ja-JP/gateway/local-models)
- [/gateway/configuration](/ja-JP/gateway/configuration)
- [/gateway/configuration-reference#openai-compatible-endpoints](/ja-JP/gateway/configuration-reference#openai-compatible-endpoints)

## 返信がない

チャネルは起動しているのに何も応答しない場合は、何かを再接続する前にルーティングとポリシーを確認してください。

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

確認ポイント:

- DM送信者のペアリングが保留中。
- グループのメンションゲート（`requireMention`、`mentionPatterns`）。
- チャネル/グループの許可リスト不一致。

よくあるシグネチャ:

- `drop guild message (mention required` → メンションされるまでグループメッセージが無視される。
- `pairing request` → 送信者に承認が必要。
- `blocked` / `allowlist` → 送信者/チャネルがポリシーでフィルタされた。

関連:

- [/channels/troubleshooting](/ja-JP/channels/troubleshooting)
- [/channels/pairing](/ja-JP/channels/pairing)
- [/channels/groups](/ja-JP/channels/groups)

## Dashboard control ui接続

dashboard/control UIが接続できない場合は、URL、認証モード、セキュアコンテキスト前提を確認してください。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

確認ポイント:

- 正しいprobe URLとdashboard URL。
- クライアントとGateway間の認証モード/トークン不一致。
- デバイスIDが必要な場面でHTTPを使用している。

よくあるシグネチャ:

- `device identity required` → 非セキュアコンテキスト、またはデバイス認証の欠落。
- `origin not allowed` → ブラウザーの`Origin`が`gateway.controlUi.allowedOrigins`に含まれていない（または、明示的な許可リストなしでloopback以外のブラウザーoriginから接続している）。
- `device nonce required` / `device nonce mismatch` → クライアントがチャレンジベースのデバイス認証フロー（`connect.challenge` + `device.nonce`）を完了していない。
- `device signature invalid` / `device signature expired` → クライアントが現在のハンドシェイクに対して誤ったペイロード（または古いタイムスタンプ）に署名している。
- `AUTH_TOKEN_MISMATCH` と `canRetryWithDeviceToken=true` → クライアントはキャッシュ済みデバイストークンで1回だけ信頼されたリトライができる。
- そのキャッシュトークン再試行では、ペアリング済みデバイストークンとともに保存されたキャッシュ済みscopeセットを再利用する。明示的な`deviceToken` / 明示的な`scopes`呼び出し元は、要求したscopeセットをそのまま維持する。
- その再試行経路以外では、接続認証の優先順位は、まず明示的な共有トークン/パスワード、次に明示的な`deviceToken`、次に保存済みデバイストークン、最後にbootstrapトークン。
- 非同期のTailscale Serve Control UI経路では、同じ`{scope, ip}`に対する失敗試行は、リミッターが失敗を記録する前に直列化される。したがって、同じクライアントからの誤った並行リトライが2回あると、2回とも単純な不一致ではなく、2回目に`retry later`が出ることがある。
- ブラウザーoriginのloopbackクライアントからの `too many failed authentication attempts (retry later)` → 同じ正規化された`Origin`からの繰り返し失敗は一時的にロックアウトされる。別のlocalhost originは別バケットを使う。
- その再試行後も `unauthorized` が繰り返される → 共有トークン/デバイストークンのドリフト。必要に応じてトークン設定を更新し、デバイストークンを再承認/ローテーションする。
- `gateway connect failed:` → ホスト/ポート/URLターゲットが間違っている。

### 認証詳細コードのクイックマップ

失敗した`connect`レスポンスの`error.details.code`を使って、次の対応を選んでください。

| Detail code | 意味 | 推奨アクション |
| ---------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AUTH_TOKEN_MISSING` | クライアントが必要な共有トークンを送信しなかった。 | クライアントにトークンを貼り付け/設定して再試行する。dashboard経路では: `openclaw config get gateway.auth.token` を実行して、その値をControl UI設定に貼り付ける。 |
| `AUTH_TOKEN_MISMATCH` | 共有トークンがGateway認証トークンと一致しなかった。 | `canRetryWithDeviceToken=true` の場合は、1回だけ信頼された再試行を許可する。キャッシュトークン再試行では保存済みの承認済みscopeを再利用し、明示的な`deviceToken` / `scopes`呼び出し元は要求したscopeを維持する。それでも失敗する場合は、[token drift recovery checklist](/cli/devices#token-drift-recovery-checklist)を実行する。 |
| `AUTH_DEVICE_TOKEN_MISMATCH` | キャッシュされたデバイスごとのトークンが古いか、失効している。 | [devices CLI](/cli/devices)を使ってデバイストークンをローテーション/再承認してから再接続する。 |
| `PAIRING_REQUIRED` | デバイスIDは認識されているが、このロールでは未承認。 | 保留中のリクエストを承認する: `openclaw devices list` を実行し、次に `openclaw devices approve <requestId>` を実行する。 |

Device auth v2移行チェック:

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

ログにnonce/signatureエラーがある場合は、接続側クライアントを更新して、次を確認してください。

1. `connect.challenge` を待機する
2. challengeに紐づいたペイロードに署名する
3. 同じchallenge nonceを使って `connect.params.device.nonce` を送信する

`openclaw devices rotate` / `revoke` / `remove` が予期せず拒否される場合:

- ペアリング済みデバイストークンのセッションは、呼び出し元が`operator.admin`も持っていない限り、**自分自身の**デバイスしか管理できない
- `openclaw devices rotate --scope ...` は、呼び出し元セッションがすでに保持しているoperator scopeしか要求できない

関連:

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/ja-JP/gateway/configuration) （Gateway認証モード）
- [/gateway/trusted-proxy-auth](/ja-JP/gateway/trusted-proxy-auth)
- [/gateway/remote](/ja-JP/gateway/remote)
- [/cli/devices](/cli/devices)

## Gatewayサービスが実行されていない

サービスはインストールされているが、プロセスが起動し続けない場合に使用してください。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # システムレベルのサービスもスキャン
```

確認ポイント:

- 終了ヒント付きの `Runtime: stopped`。
- サービス設定の不一致（`Config (cli)` 対 `Config (service)`）。
- ポート/リスナーの競合。
- `--deep` 使用時の余分なlaunchd/systemd/schtasksインストール。
- `Other gateway-like services detected (best effort)` のクリーンアップヒント。

よくあるシグネチャ:

- `Gateway start blocked: set gateway.mode=local` または `existing config is missing gateway.mode` → local Gatewayモードが有効化されていない、または設定ファイルが壊れて `gateway.mode` が失われている。修正: 設定で `gateway.mode="local"` を設定するか、`openclaw onboard --mode local` / `openclaw setup` を再実行して期待されるlocal-mode設定を再作成する。Podman経由でOpenClawを実行している場合、デフォルトの設定パスは `~/.openclaw/openclaw.json`。
- `refusing to bind gateway ... without auth` → 有効なGateway認証経路（token/password、または設定されているtrusted-proxy）がないまま、非loopback bindをしようとしている。
- `another gateway instance is already listening` / `EADDRINUSE` → ポート競合。
- `Other gateway-like services detected (best effort)` → 古い、または並行するlaunchd/systemd/schtasksユニットが存在する。ほとんどのセットアップでは、1台のマシンにつき1つのGatewayにするべきです。複数必要な場合は、ポート + config/state/workspaceを分離してください。詳細は[/gateway#multiple-gateways-same-host](/ja-JP/gateway#multiple-gateways-same-host)を参照してください。

関連:

- [/gateway/background-process](/ja-JP/gateway/background-process)
- [/gateway/configuration](/ja-JP/gateway/configuration)
- [/gateway/doctor](/ja-JP/gateway/doctor)

## Gateway probeの警告

`openclaw gateway probe` が何かに到達しているのに、なお警告ブロックを表示する場合に使用してください。

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

確認ポイント:

- JSON出力内の `warnings[].code` と `primaryTargetId`。
- 警告がSSHフォールバック、複数Gateway、不足しているscope、または未解決のauth refに関するものかどうか。

よくあるシグネチャ:

- `SSH tunnel failed to start; falling back to direct probes.` → SSHセットアップに失敗したが、コマンドは引き続き設定済み/loopbackターゲットへの直接probeを試した。
- `multiple reachable gateways detected` → 複数のターゲットが応答した。通常、これは意図的なマルチGateway構成か、古い/重複したリスナーを意味する。
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → 接続は成功したが、詳細RPCがscope不足で制限されている。デバイスIDをペアリングするか、`operator.read` を持つ認証情報を使用する。
- 未解決の `gateway.auth.*` / `gateway.remote.*` SecretRef警告テキスト → 失敗したターゲットに対するこのコマンド経路では認証情報を利用できなかった。

関連:

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/ja-JP/gateway#multiple-gateways-same-host)
- [/gateway/remote](/ja-JP/gateway/remote)

## チャネルは接続済みだがメッセージが流れない

チャネル状態は接続済みなのにメッセージフローが止まっている場合は、ポリシー、権限、チャネル固有の配信ルールに注目してください。

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
- 不足しているチャネルAPI権限/scope。

よくあるシグネチャ:

- `mention required` → グループメンションポリシーによってメッセージが無視されている。
- `pairing` / 保留中の承認トレース → 送信者が未承認。
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → チャネル認証/権限の問題。

関連:

- [/channels/troubleshooting](/ja-JP/channels/troubleshooting)
- [/channels/whatsapp](/ja-JP/channels/whatsapp)
- [/channels/telegram](/ja-JP/channels/telegram)
- [/channels/discord](/ja-JP/channels/discord)

## Cronとheartbeatの配信

cronまたはheartbeatが実行されなかった、あるいは配信されなかった場合は、まずschedulerの状態を確認し、その後で配信先を確認してください。

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

確認ポイント:

- Cronが有効で、次回wakeが存在する。
- ジョブ実行履歴の状態（`ok`、`skipped`、`error`）。
- Heartbeatのskip理由（`quiet-hours`、`requests-in-flight`、`alerts-disabled`、`empty-heartbeat-file`、`no-tasks-due`）。

よくあるシグネチャ:

- `cron: scheduler disabled; jobs will not run automatically` → cronが無効。
- `cron: timer tick failed` → scheduler tickに失敗した。ファイル/ログ/ランタイムエラーを確認する。
- `heartbeat skipped` と `reason=quiet-hours` → アクティブ時間帯の外。
- `heartbeat skipped` と `reason=empty-heartbeat-file` → `HEARTBEAT.md` は存在するが、空行またはMarkdown見出ししか含まれていないため、OpenClawがモデル呼び出しをスキップしている。
- `heartbeat skipped` と `reason=no-tasks-due` → `HEARTBEAT.md` に `tasks:` ブロックはあるが、このtick時点で期限の来ているタスクがない。
- `heartbeat: unknown accountId` → heartbeat配信先として無効なaccount id。
- `heartbeat skipped` と `reason=dm-blocked` → heartbeatターゲットがDMスタイルの宛先に解決されたが、`agents.defaults.heartbeat.directPolicy`（またはagentごとの上書き）が `block` に設定されている。

関連:

- [/automation/cron-jobs#troubleshooting](/ja-JP/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/ja-JP/automation/cron-jobs)
- [/gateway/heartbeat](/ja-JP/gateway/heartbeat)

## ペアリング済みノードのツールが失敗する

ノードはペアリングされているのにツールが失敗する場合は、foreground、権限、承認状態を切り分けてください。

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

確認ポイント:

- ノードがオンラインで、期待どおりのcapabilityを持っている。
- camera/mic/location/screenに対するOS権限が付与されている。
- exec承認とallowlist状態。

よくあるシグネチャ:

- `NODE_BACKGROUND_UNAVAILABLE` → ノードアプリがforegroundにある必要がある。
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → OS権限が不足している。
- `SYSTEM_RUN_DENIED: approval required` → exec承認が保留中。
- `SYSTEM_RUN_DENIED: allowlist miss` → コマンドがallowlistによりブロックされている。

関連:

- [/nodes/troubleshooting](/ja-JP/nodes/troubleshooting)
- [/nodes/index](/ja-JP/nodes/index)
- [/tools/exec-approvals](/ja-JP/tools/exec-approvals)

## Browserツールが失敗する

Gateway自体は正常なのにbrowserツールのアクションが失敗する場合に使用してください。

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

確認ポイント:

- `plugins.allow` が設定されていて、`browser` を含んでいるかどうか。
- 有効なbrowser executable path。
- CDP profileへの到達可能性。
- `existing-session` / `user` profile向けのローカルChromeの可用性。

よくあるシグネチャ:

- `unknown command "browser"` または `unknown command 'browser'` → バンドルされたbrowserプラグインが `plugins.allow` によって除外されている。
- `browser.enabled=true` なのにbrowserツールが見つからない / 利用できない → `plugins.allow` が `browser` を除外しているため、プラグインが読み込まれていない。
- `Failed to start Chrome CDP on port` → browserプロセスの起動に失敗した。
- `browser.executablePath not found` → 設定されたパスが無効。
- `browser.cdpUrl must be http(s) or ws(s)` → 設定されたCDP URLが `file:` や `ftp:` のような未対応スキームを使用している。
- `browser.cdpUrl has invalid port` → 設定されたCDP URLのポートが不正、または範囲外。
- `No Chrome tabs found for profile="user"` → Chrome MCP attach profileに開いているローカルChromeタブがない。
- `Remote CDP for profile "<name>" is not reachable` → 設定されたリモートCDP endpointにGatewayホストから到達できない。
- `Browser attachOnly is enabled ... not reachable` または `Browser attachOnly is enabled and CDP websocket ... is not reachable` → attach-only profileに到達可能なターゲットがない、またはHTTP endpointは応答したがCDP WebSocketをまだ開けなかった。
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → 現在のGatewayインストールには完全なPlaywrightパッケージが含まれていない。ARIAスナップショットと基本的なページスクリーンショットは引き続き動作する可能性があるが、ナビゲーション、AIスナップショット、CSSセレクターの要素スクリーンショット、PDFエクスポートは利用できない。
- `fullPage is not supported for element screenshots` → スクリーンショット要求で `--full-page` と `--ref` または `--element` が混在していた。
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → Chrome MCP / `existing-session` のスクリーンショット呼び出しでは、CSS `--element` ではなくページキャプチャまたはスナップショット `--ref` を使う必要がある。
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → Chrome MCPアップロードフックでは、CSSセレクターではなくスナップショットrefが必要。
- `existing-session file uploads currently support one file at a time.` → Chrome MCP profileでは、1回の呼び出しにつき1つのアップロードだけを送信する。
- `existing-session dialog handling does not support timeoutMs.` → Chrome MCP profileのdialogフックはtimeout上書きをサポートしていない。
- `response body is not supported for existing-session profiles yet.` → `responsebody` はまだmanaged browserまたはraw CDP profileを必要とする。
- attach-onlyまたはremote CDP profileでviewport / dark-mode / locale / offline上書きが古いまま残っている → `openclaw browser stop --browser-profile <name>` を実行して、Gateway全体を再起動せずにアクティブなcontrol sessionを閉じ、Playwright/CDPエミュレーション状態を解放する。

関連:

- [/tools/browser-linux-troubleshooting](/ja-JP/tools/browser-linux-troubleshooting)
- [/tools/browser](/ja-JP/tools/browser)

## アップグレード後に突然何かが壊れた場合

アップグレード後の不具合の多くは、設定のドリフトか、より厳格なデフォルトが現在適用されていることが原因です。

### 1) 認証とURL上書きの動作が変わった

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

確認事項:

- `gateway.mode=remote` の場合、ローカルサービスは正常でもCLI呼び出しがremoteを対象にしている可能性がある。
- 明示的な `--url` 呼び出しは保存済み認証情報へフォールバックしない。

よくあるシグネチャ:

- `gateway connect failed:` → URLターゲットが間違っている。
- `unauthorized` → endpointには到達しているが認証が間違っている。

### 2) bindとauthのガードレールがより厳格になった

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

確認事項:

- 非loopback bind（`lan`、`tailnet`、`custom`）には、有効なGateway認証経路が必要: 共有token/password認証、または正しく設定された非loopbackの`trusted-proxy`デプロイ。
- `gateway.token` のような古いキーは `gateway.auth.token` の代わりにはならない。

よくあるシグネチャ:

- `refusing to bind gateway ... without auth` → 有効なGateway認証経路なしで非loopback bindしようとしている。
- ランタイムは実行中なのに `RPC probe: failed` → Gatewayは生きているが、現在のauth/urlではアクセスできない。

### 3) ペアリングとデバイスIDの状態が変わった

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

確認事項:

- dashboard/nodes向けの保留中デバイス承認。
- ポリシーまたはID変更後の保留中DMペアリング承認。

よくあるシグネチャ:

- `device identity required` → デバイス認証が満たされていない。
- `pairing required` → 送信者/デバイスの承認が必要。

確認後もサービス設定とランタイムが一致しない場合は、同じprofile/state directoryからサービスメタデータを再インストールしてください。

```bash
openclaw gateway install --force
openclaw gateway restart
```

関連:

- [/gateway/pairing](/ja-JP/gateway/pairing)
- [/gateway/authentication](/ja-JP/gateway/authentication)
- [/gateway/background-process](/ja-JP/gateway/background-process)
