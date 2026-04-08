---
read_when:
    - トラブルシューティングハブから、より詳細な診断のためにここへ案内された場合
    - 正確なコマンド付きの、安定した症状ベースの手順セクションが必要な場合
summary: Gateway、チャネル、自動化、ノード、ブラウザー向けの詳細なトラブルシューティング手順書
title: トラブルシューティング
x-i18n:
    generated_at: "2026-04-08T02:16:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 02c9537845248db0c9d315bf581338a93215fe6fe3688ed96c7105cbb19fe6ba
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# Gateway のトラブルシューティング

このページは詳細な手順書です。
まず簡易トリアージフローを確認したい場合は、[/help/troubleshooting](/ja-JP/help/troubleshooting) から始めてください。

## コマンドの段階的実行

まずはこの順番で実行してください:

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

正常時に期待されるシグナル:

- `openclaw gateway status` に `Runtime: running` と `RPC probe: ok` が表示される。
- `openclaw doctor` で、設定やサービスに関するブロッキングな問題が報告されない。
- `openclaw channels status --probe` で、アカウントごとのライブなトランスポート状態と、
  サポートされている場合は `works` や `audit ok` のような probe/audit 結果が表示される。

## 長いコンテキストに対して Anthropic 429 extra usage required が出る

ログやエラーに次が含まれている場合に使用してください:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

確認する点:

- 選択された Anthropic Opus/Sonnet モデルで `params.context1m: true` になっている。
- 現在の Anthropic 認証情報が long-context 利用の対象ではない。
- リクエストが失敗するのは、1M ベータパスが必要な長いセッション/モデル実行時のみである。

修正方法:

1. そのモデルの `context1m` を無効にして、通常のコンテキストウィンドウにフォールバックする。
2. long-context リクエスト対象の Anthropic 認証情報を使うか、Anthropic API キーに切り替える。
3. Anthropic の long-context リクエストが拒否されたときも実行が継続するように、フォールバックモデルを設定する。

関連:

- [/providers/anthropic](/ja-JP/providers/anthropic)
- [/reference/token-use](/ja-JP/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/ja-JP/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## ローカルの OpenAI-compatible バックエンドでは直接 probe は通るが、エージェント実行は失敗する

次の場合に使用してください:

- `curl ... /v1/models` は動作する
- 小さな直接 `/v1/chat/completions` 呼び出しは動作する
- OpenClaw のモデル実行が失敗するのは通常のエージェントターンのみ

```bash
curl http://127.0.0.1:1234/v1/models
curl http://127.0.0.1:1234/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"<id>","messages":[{"role":"user","content":"hi"}],"stream":false}'
openclaw infer model run --model <provider/model> --prompt "hi" --json
openclaw logs --follow
```

確認する点:

- 直接の小さな呼び出しは成功するが、OpenClaw 実行はより大きなプロンプトのときだけ失敗する
- バックエンドエラーで、`messages[].content` が文字列を期待している
- より大きな prompt token 数や、完全なエージェントランタイムプロンプトでのみバックエンドがクラッシュする

よくあるシグネチャ:

- `messages[...].content: invalid type: sequence, expected a string` → バックエンドが構造化された Chat Completions の content parts を拒否している。修正: `models.providers.<provider>.models[].compat.requiresStringContent: true` を設定する。
- 直接の小さなリクエストは成功するが、OpenClaw のエージェント実行はバックエンド/モデルのクラッシュで失敗する（たとえば一部の `inferrs` ビルド上の Gemma） → OpenClaw のトランスポートはすでに正しい可能性が高く、バックエンドがより大きいエージェントランタイムのプロンプト形状で失敗している。
- ツールを無効にすると失敗は減るが消えない → ツールスキーマが負荷の一因ではあったが、残っている問題は依然として上流のモデル/サーバー容量かバックエンドバグである。

修正方法:

1. 文字列のみの Chat Completions バックエンドに対して `compat.requiresStringContent: true` を設定する。
2. OpenClaw のツールスキーマ面を安定して処理できないモデル/バックエンドには `compat.supportsTools: false` を設定する。
3. 可能な範囲でプロンプト負荷を下げる: より小さい workspace bootstrap、より短いセッション履歴、より軽いローカルモデル、または long-context サポートがより強いバックエンドを使う。
4. 直接の小さなリクエストが引き続き成功する一方で、OpenClaw のエージェントターンがバックエンド内部で依然としてクラッシュする場合は、上流のサーバー/モデルの制限として扱い、受け入れられたペイロード形状を添えてそこで再現報告を出す。

関連:

- [/gateway/local-models](/ja-JP/gateway/local-models)
- [/gateway/configuration#models](/ja-JP/gateway/configuration#models)
- [/gateway/configuration-reference#openai-compatible-endpoints](/ja-JP/gateway/configuration-reference#openai-compatible-endpoints)

## 返信がない

チャネルは稼働しているのに何も応答しない場合は、何かを再接続する前に、ルーティングとポリシーを確認してください。

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

確認する点:

- DM 送信者に対してペアリングが保留中になっている。
- グループのメンションゲーティング（`requireMention`、`mentionPatterns`）。
- チャネル/グループの allowlist 不一致。

よくあるシグネチャ:

- `drop guild message (mention required` → メンションされるまでグループメッセージは無視される。
- `pairing request` → 送信者に承認が必要。
- `blocked` / `allowlist` → 送信者/チャネルがポリシーによってフィルタリングされた。

関連:

- [/channels/troubleshooting](/ja-JP/channels/troubleshooting)
- [/channels/pairing](/ja-JP/channels/pairing)
- [/channels/groups](/ja-JP/channels/groups)

## Dashboard control ui の接続性

dashboard/control UI が接続できない場合は、URL、認証モード、安全なコンテキスト前提を確認してください。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

確認する点:

- probe URL と dashboard URL が正しい。
- クライアントと Gateway の認証モード/トークンが一致している。
- デバイス ID が必要な場面で HTTP を使用していない。

よくあるシグネチャ:

- `device identity required` → 安全でないコンテキスト、または device auth が不足している。
- `origin not allowed` → ブラウザーの `Origin` が `gateway.controlUi.allowedOrigins`
  に入っていない（または、明示的な allowlist なしで非 loopback のブラウザー origin から接続している）。
- `device nonce required` / `device nonce mismatch` → クライアントが challenge ベースの device auth フロー（`connect.challenge` + `device.nonce`）を完了していない。
- `device signature invalid` / `device signature expired` → クライアントが現在のハンドシェイクに対して誤ったペイロード（または古いタイムスタンプ）に署名した。
- `AUTH_TOKEN_MISMATCH` と `canRetryWithDeviceToken=true` → クライアントはキャッシュされた device token で 1 回だけ信頼された再試行ができる。
- そのキャッシュトークン再試行では、ペアリング済み device token に保存されているキャッシュ済み scope セットが再利用される。明示的な `deviceToken` / 明示的な `scopes` 呼び出し元は、代わりに要求した scope セットを維持する。
- その再試行パス以外では、接続認証の優先順位は、明示的な共有
  token/password が最初、その次に明示的な `deviceToken`、その次に保存済み device token、最後に bootstrap token。
- 非同期の Tailscale Serve Control UI パスでは、同じ `{scope, ip}` に対する失敗試行は、リミッターが失敗を記録する前に直列化される。したがって、同じクライアントからの不正な同時再試行 2 件では、単純に 2 件の不一致になるのではなく、2 件目で `retry later` が出ることがある。
- ブラウザー origin の loopback クライアントから `too many failed authentication attempts (retry later)` → 同じ正規化済み `Origin` からの繰り返し失敗は一時的にロックアウトされる。別の localhost origin は別バケットを使う。
- その再試行後も `unauthorized` が繰り返される → 共有 token/device token のずれ。トークン設定を更新し、必要に応じて device token を再承認/ローテーションする。
- `gateway connect failed:` → ホスト/ポート/url の接続先が間違っている。

### 認証詳細コードのクイックマップ

失敗した `connect` レスポンスの `error.details.code` を使って、次の対応を選んでください:

| Detail code                  | 意味 | 推奨対応 |
| ---------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AUTH_TOKEN_MISSING`         | クライアントが必要な共有トークンを送信していない。             | クライアントにトークンを貼り付け/設定して再試行する。dashboard パスでは: `openclaw config get gateway.auth.token` を実行し、その値を Control UI の設定に貼り付ける。                                                                                                                                              |
| `AUTH_TOKEN_MISMATCH`        | 共有トークンが Gateway の認証トークンと一致しなかった。           | `canRetryWithDeviceToken=true` の場合は、信頼された再試行を 1 回許可する。キャッシュトークン再試行では保存済みの承認済み scope が再利用される。明示的な `deviceToken` / `scopes` 呼び出し元は要求した scope を維持する。それでも失敗する場合は、[token drift recovery checklist](/cli/devices#token-drift-recovery-checklist) を実行する。 |
| `AUTH_DEVICE_TOKEN_MISMATCH` | デバイスごとにキャッシュされたトークンが古いか失効している。             | [devices CLI](/cli/devices) を使って device token をローテーション/再承認してから再接続する。                                                                                                                                                                                                        |
| `PAIRING_REQUIRED`           | デバイス ID は認識されているが、このロールでは承認されていない。 | 保留中の要求を承認する: `openclaw devices list` を実行し、その後 `openclaw devices approve <requestId>` を実行する。                                                                                                                                                                                            |

Device auth v2 の移行確認:

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

ログに nonce/signature エラーが出ている場合は、接続元クライアントを更新し、次を確認してください:

1. `connect.challenge` を待つ
2. challenge に束縛されたペイロードに署名する
3. 同じ challenge nonce を使って `connect.params.device.nonce` を送る

`openclaw devices rotate` / `revoke` / `remove` が予期せず拒否される場合:

- paired-device token セッションは、呼び出し元が
  `operator.admin` も持っていない限り、**自分自身** のデバイスしか管理できない
- `openclaw devices rotate --scope ...` は、呼び出し元セッションがすでに保有している
  operator scope しか要求できない

関連:

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/ja-JP/gateway/configuration)（Gateway の認証モード）
- [/gateway/trusted-proxy-auth](/ja-JP/gateway/trusted-proxy-auth)
- [/gateway/remote](/ja-JP/gateway/remote)
- [/cli/devices](/cli/devices)

## Gateway サービスが動作していない

サービスはインストールされているが、プロセスが起動し続けない場合に使用してください。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # also scan system-level services
```

確認する点:

- `Runtime: stopped` と終了ヒント。
- サービス設定の不一致（`Config (cli)` と `Config (service)`）。
- ポート/リスナー競合。
- `--deep` 使用時の追加の launchd/systemd/schtasks インストール。
- `Other gateway-like services detected (best effort)` のクリーンアップヒント。

よくあるシグネチャ:

- `Gateway start blocked: set gateway.mode=local` または `existing config is missing gateway.mode` → local Gateway モードが有効ではない、または設定ファイルが上書きされて `gateway.mode` が失われた。修正: 設定で `gateway.mode="local"` を設定するか、`openclaw onboard --mode local` / `openclaw setup` を再実行して、想定される local-mode 設定を再作成する。Podman 経由で OpenClaw を実行している場合、デフォルトの設定パスは `~/.openclaw/openclaw.json` です。
- `refusing to bind gateway ... without auth` → 有効な Gateway 認証経路（token/password、または設定された trusted-proxy）がない非 loopback bind。
- `another gateway instance is already listening` / `EADDRINUSE` → ポート競合。
- `Other gateway-like services detected (best effort)` → 古い、または並行する launchd/systemd/schtasks ユニットが存在する。ほとんどのセットアップでは、1 台のマシンにつき 1 つの Gateway を維持するべきです。複数必要な場合は、ポート + config/state/workspace を分離してください。[/gateway#multiple-gateways-same-host](/ja-JP/gateway#multiple-gateways-same-host) を参照してください。

関連:

- [/gateway/background-process](/ja-JP/gateway/background-process)
- [/gateway/configuration](/ja-JP/gateway/configuration)
- [/gateway/doctor](/ja-JP/gateway/doctor)

## Gateway probe の警告

`openclaw gateway probe` が何かには到達するが、警告ブロックも表示する場合に使用してください。

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

確認する点:

- JSON 出力の `warnings[].code` と `primaryTargetId`。
- 警告が SSH フォールバック、複数 Gateway、不足している scope、未解決の auth ref のどれに関するものか。

よくあるシグネチャ:

- `SSH tunnel failed to start; falling back to direct probes.` → SSH セットアップは失敗したが、コマンドは引き続き設定済み/loopback の直接ターゲットを試行した。
- `multiple reachable gateways detected` → 複数のターゲットが応答した。通常、これは意図的な複数 Gateway セットアップか、古い/重複したリスナーを意味する。
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → 接続自体は成功したが、詳細 RPC は scope により制限されている。device identity をペアリングするか、`operator.read` を持つ認証情報を使用する。
- 未解決の `gateway.auth.*` / `gateway.remote.*` SecretRef 警告テキスト → 失敗したターゲットに対するこのコマンド経路では認証情報が利用できなかった。

関連:

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/ja-JP/gateway#multiple-gateways-same-host)
- [/gateway/remote](/ja-JP/gateway/remote)

## チャネルは接続済みだがメッセージが流れない

チャネル状態は connected だがメッセージフローが止まっている場合は、ポリシー、権限、チャネル固有の配信ルールに集中してください。

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

確認する点:

- DM ポリシー（`pairing`、`allowlist`、`open`、`disabled`）。
- グループ allowlist とメンション要件。
- チャネル API の権限/scope 不足。

よくあるシグネチャ:

- `mention required` → グループのメンションポリシーによりメッセージが無視された。
- `pairing` / 保留中の承認トレース → 送信者が承認されていない。
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → チャネル認証/権限の問題。

関連:

- [/channels/troubleshooting](/ja-JP/channels/troubleshooting)
- [/channels/whatsapp](/ja-JP/channels/whatsapp)
- [/channels/telegram](/ja-JP/channels/telegram)
- [/channels/discord](/ja-JP/channels/discord)

## Cron と heartbeat の配信

cron または heartbeat が実行されなかった、あるいは配信されなかった場合は、まず scheduler の状態、その次に配信先を確認してください。

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

確認する点:

- Cron が有効で、次回 wake が存在する。
- ジョブ実行履歴の状態（`ok`、`skipped`、`error`）。
- heartbeat のスキップ理由（`quiet-hours`、`requests-in-flight`、`alerts-disabled`、`empty-heartbeat-file`、`no-tasks-due`）。

よくあるシグネチャ:

- `cron: scheduler disabled; jobs will not run automatically` → cron が無効。
- `cron: timer tick failed` → scheduler tick に失敗。ファイル/ログ/ランタイムエラーを確認する。
- `heartbeat skipped` と `reason=quiet-hours` → アクティブ時間帯の外側。
- `heartbeat skipped` と `reason=empty-heartbeat-file` → `HEARTBEAT.md` は存在するが、空行または markdown ヘッダーしか含まれていないため、OpenClaw はモデル呼び出しをスキップする。
- `heartbeat skipped` と `reason=no-tasks-due` → `HEARTBEAT.md` に `tasks:` ブロックはあるが、この tick で期限の来ているタスクがない。
- `heartbeat: unknown accountId` → heartbeat 配信先の account id が無効。
- `heartbeat skipped` と `reason=dm-blocked` → heartbeat の宛先が DM 形式の送信先に解決されたが、`agents.defaults.heartbeat.directPolicy`（またはエージェントごとの上書き）が `block` に設定されている。

関連:

- [/automation/cron-jobs#troubleshooting](/ja-JP/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/ja-JP/automation/cron-jobs)
- [/gateway/heartbeat](/ja-JP/gateway/heartbeat)

## ノードのペアリング済みツールが失敗する

ノードはペアリング済みだがツールが失敗する場合は、フォアグラウンド、権限、承認状態を切り分けてください。

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

確認する点:

- ノードがオンラインで、期待する capabilities を持っている。
- camera/mic/location/screen に対する OS 権限が付与されている。
- exec 承認と allowlist の状態。

よくあるシグネチャ:

- `NODE_BACKGROUND_UNAVAILABLE` → ノードアプリをフォアグラウンドに置く必要がある。
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → OS 権限が不足している。
- `SYSTEM_RUN_DENIED: approval required` → exec 承認が保留中。
- `SYSTEM_RUN_DENIED: allowlist miss` → コマンドが allowlist によりブロックされた。

関連:

- [/nodes/troubleshooting](/ja-JP/nodes/troubleshooting)
- [/nodes/index](/ja-JP/nodes/index)
- [/tools/exec-approvals](/ja-JP/tools/exec-approvals)

## Browser ツールが失敗する

Gateway 自体は正常なのに browser ツールのアクションが失敗する場合に使用してください。

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

確認する点:

- `plugins.allow` が設定されており、`browser` を含んでいるか。
- browser executable path が有効か。
- CDP profile に到達できるか。
- `existing-session` / `user` profile でローカル Chrome が利用可能か。

よくあるシグネチャ:

- `unknown command "browser"` または `unknown command 'browser'` → バンドルされた browser plugin が `plugins.allow` によって除外されている。
- `browser.enabled=true` なのに browser ツールが見つからない / 利用不可 → `plugins.allow` が `browser` を除外しているため、plugin が読み込まれていない。
- `Failed to start Chrome CDP on port` → browser プロセスの起動に失敗した。
- `browser.executablePath not found` → 設定されたパスが無効。
- `browser.cdpUrl must be http(s) or ws(s)` → 設定された CDP URL が `file:` や `ftp:` など未対応のスキームを使用している。
- `browser.cdpUrl has invalid port` → 設定された CDP URL のポートが不正または範囲外。
- `No Chrome tabs found for profile="user"` → Chrome MCP attach profile にローカルの開いている Chrome タブがない。
- `Remote CDP for profile "<name>" is not reachable` → 設定されたリモート CDP エンドポイントに Gateway ホストから到達できない。
- `Browser attachOnly is enabled ... not reachable` または `Browser attachOnly is enabled and CDP websocket ... is not reachable` → attach-only profile に到達可能なターゲットがない、または HTTP エンドポイントは応答しても CDP WebSocket を依然として開けない。
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → 現在の Gateway インストールには完全な Playwright パッケージが含まれていない。ARIA スナップショットや基本的なページスクリーンショットは動作する場合があるが、ナビゲーション、AI スナップショット、CSS セレクターによる要素スクリーンショット、PDF エクスポートは利用できない。
- `fullPage is not supported for element screenshots` → スクリーンショット要求で `--full-page` と `--ref` または `--element` を混在させている。
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → Chrome MCP / `existing-session` のスクリーンショット呼び出しでは、CSS の `--element` ではなくページキャプチャまたはスナップショットの `--ref` を使う必要がある。
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → Chrome MCP のアップロードフックには CSS セレクターではなくスナップショット ref が必要。
- `existing-session file uploads currently support one file at a time.` → Chrome MCP profile では、アップロードは 1 回の呼び出しにつき 1 ファイルだけ送信する。
- `existing-session dialog handling does not support timeoutMs.` → Chrome MCP profile のダイアログフックでは timeout の上書きがサポートされていない。
- `response body is not supported for existing-session profiles yet.` → `responsebody` は依然として managed browser または raw CDP profile が必要。
- attach-only または remote CDP profile で viewport / dark-mode / locale / offline の上書きが古い状態のまま残っている → `openclaw browser stop --browser-profile <name>` を実行し、アクティブな制御セッションを閉じて、Gateway 全体を再起動せずに Playwright/CDP のエミュレーション状態を解放する。

関連:

- [/tools/browser-linux-troubleshooting](/ja-JP/tools/browser-linux-troubleshooting)
- [/tools/browser](/ja-JP/tools/browser)

## アップグレード後に突然何かが壊れた場合

アップグレード後の破損の多くは、設定のずれか、より厳格なデフォルトが適用されるようになったことが原因です。

### 1) 認証と URL 上書き動作が変わった

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

確認する点:

- `gateway.mode=remote` の場合、CLI 呼び出しがリモートを対象にしている一方で、ローカルサービス自体は正常なことがある。
- 明示的な `--url` 呼び出しは保存済み認証情報にフォールバックしない。

よくあるシグネチャ:

- `gateway connect failed:` → URL の接続先が間違っている。
- `unauthorized` → エンドポイントには到達しているが認証が間違っている。

### 2) bind と auth のガードレールがより厳格になった

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

確認する点:

- 非 loopback bind（`lan`、`tailnet`、`custom`）には、有効な Gateway 認証経路が必要: 共有 token/password 認証、または正しく設定された非 loopback の `trusted-proxy` デプロイメント。
- `gateway.token` のような古いキーは `gateway.auth.token` の代わりにはならない。

よくあるシグネチャ:

- `refusing to bind gateway ... without auth` → 有効な Gateway 認証経路がない非 loopback bind。
- ランタイムは動作中なのに `RPC probe: failed` → Gateway は生きているが、現在の auth/url ではアクセスできない。

### 3) ペアリングと device identity の状態が変わった

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

確認する点:

- dashboard/nodes の保留中 device 承認。
- ポリシーまたは identity の変更後に保留中になっている DM pairing 承認。

よくあるシグネチャ:

- `device identity required` → device auth 要件が満たされていない。
- `pairing required` → 送信者/デバイスの承認が必要。

確認後もサービス設定とランタイムが一致しない場合は、同じ profile/state ディレクトリーからサービスメタデータを再インストールしてください。

```bash
openclaw gateway install --force
openclaw gateway restart
```

関連:

- [/gateway/pairing](/ja-JP/gateway/pairing)
- [/gateway/authentication](/ja-JP/gateway/authentication)
- [/gateway/background-process](/ja-JP/gateway/background-process)
