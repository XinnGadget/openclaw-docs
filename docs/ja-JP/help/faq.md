---
read_when:
    - 一般的なセットアップ、インストール、オンボーディング、またはランタイムのサポート質問に答える
    - より深いデバッグに入る前に、ユーザーから報告された問題を切り分ける
summary: OpenClaw のセットアップ、設定、使用方法に関するよくある質問
title: FAQ
x-i18n:
    generated_at: "2026-04-06T03:13:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4d6d09621c6033d580cbcf1ff46f81587d69404d6f64c8d8fd8c3f09185bb920
    source_path: help/faq.md
    workflow: 15
---

# FAQ

実際のセットアップで役立つ簡潔な回答と、より詳しいトラブルシューティングです（ローカル開発、VPS、マルチエージェント、OAuth/API キー、モデルフェイルオーバー）。ランタイム診断については [Troubleshooting](/ja-JP/gateway/troubleshooting) を参照してください。完全な設定リファレンスについては [Configuration](/ja-JP/gateway/configuration) を参照してください。

## 何か壊れているときの最初の 60 秒

1. **クイックステータス（最初の確認）**

   ```bash
   openclaw status
   ```

   高速なローカル概要: OS + 更新、Gateway/サービスの到達性、agents/sessions、プロバイダー設定 + ランタイムの問題（Gateway に到達できる場合）。

2. **共有しやすいレポート（安全に共有可能）**

   ```bash
   openclaw status --all
   ```

   ログ末尾付きの読み取り専用診断（トークンはマスクされます）。

3. **デーモン + ポートの状態**

   ```bash
   openclaw gateway status
   ```

   supervisor のランタイムと RPC 到達性、probe の対象 URL、およびサービスが使用した可能性が高い設定を表示します。

4. **詳細 probe**

   ```bash
   openclaw status --deep
   ```

   サポートされている場合はチャネル probe を含む、実際の Gateway ヘルス probe を実行します
   （到達可能な Gateway が必要です）。[Health](/ja-JP/gateway/health) を参照してください。

5. **最新ログを追う**

   ```bash
   openclaw logs --follow
   ```

   RPC が落ちている場合は、代わりに以下を使ってください。

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   ファイルログはサービスログとは別です。[Logging](/ja-JP/logging) と [Troubleshooting](/ja-JP/gateway/troubleshooting) を参照してください。

6. **doctor を実行する（修復）**

   ```bash
   openclaw doctor
   ```

   設定/状態を修復・移行し、ヘルスチェックを実行します。[Doctor](/ja-JP/gateway/doctor) を参照してください。

7. **Gateway スナップショット**

   ```bash
   openclaw health --json
   openclaw health --verbose   # エラー時に対象 URL + config path を表示
   ```

   実行中の Gateway に完全なスナップショットを問い合わせます（WS のみ）。[Health](/ja-JP/gateway/health) を参照してください。

## クイックスタートと初回セットアップ

<AccordionGroup>
  <Accordion title="行き詰まりました。最速で抜け出す方法は？">
    **自分のマシンを見られる**ローカル AI エージェントを使ってください。Discord で聞くよりずっと効果的です。というのも、「行き詰まった」ケースの多くは、リモートの手助けでは確認できない**ローカルの設定や環境の問題**だからです。

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    これらのツールは、リポジトリを読み、コマンドを実行し、ログを確認し、マシンレベルのセットアップ（PATH、services、permissions、auth files）の修正を助けてくれます。hackable（git）インストールで**完全なソースチェックアウト**を渡してください。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    これにより、OpenClaw は**git checkout から**インストールされるので、エージェントはコード + ドキュメントを読み、実行中の正確なバージョンについて推論できます。後からいつでも `--install-method git` を付けずにインストーラーを再実行して stable に戻せます。

    ヒント: エージェントには、修正を**計画して監督**するよう依頼してください（ステップごと）。そのうえで必要なコマンドだけを実行します。そうすると変更が小さく保たれ、監査しやすくなります。

    実際のバグや修正を見つけた場合は、ぜひ GitHub issue を作成するか PR を送ってください:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    まずは次のコマンドから始めてください（助けを求めるときは出力を共有してください）。

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    それぞれの役割:

    - `openclaw status`: gateway/agent の健全性 + 基本設定のクイックスナップショット。
    - `openclaw models status`: provider auth + モデルの利用可否を確認。
    - `openclaw doctor`: よくある設定/状態の問題を検証し、修復します。

    ほかに役立つ CLI チェック: `openclaw status --all`、`openclaw logs --follow`、
    `openclaw gateway status`、`openclaw health --verbose`。

    すばやいデバッグループ: [何か壊れているときの最初の 60 秒](#何か壊れているときの最初の-60-秒)。
    インストールドキュメント: [Install](/ja-JP/install)、[Installer flags](/ja-JP/install/installer)、[Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="Heartbeat がスキップされ続けます。スキップ理由は何を意味しますか？">
    よくある heartbeat のスキップ理由:

    - `quiet-hours`: 設定された active-hours の時間帯外
    - `empty-heartbeat-file`: `HEARTBEAT.md` は存在するが、空行やヘッダーだけの雛形しか含まれていない
    - `no-tasks-due`: `HEARTBEAT.md` の task モードが有効だが、どのタスク間隔もまだ実行時刻になっていない
    - `alerts-disabled`: heartbeat の可視化がすべて無効（`showOk`、`showAlerts`、`useIndicator` がすべて off）

    task モードでは、実際の heartbeat 実行が完了した後にのみ due タイムスタンプが進みます。
    スキップされた実行では、タスク完了済みにはなりません。

    ドキュメント: [Heartbeat](/ja-JP/gateway/heartbeat)、[Automation & Tasks](/ja-JP/automation)。

  </Accordion>

  <Accordion title="OpenClaw の推奨インストール方法とセットアップ方法は？">
    リポジトリでは、ソースから実行し、オンボーディングを使うことを推奨しています。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    ウィザードは UI アセットも自動ビルドできます。オンボーディング後、通常は **18789** ポートで Gateway を実行します。

    ソースから（コントリビューター/開発者向け）:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # 初回実行時に UI 依存関係を自動インストール
    openclaw onboard
    ```

    まだグローバルインストールしていない場合は、`pnpm openclaw onboard` で実行してください。

  </Accordion>

  <Accordion title="オンボーディング後にダッシュボードを開くには？">
    ウィザードはオンボーディング直後に、クリーンな（トークンなしの）ダッシュボード URL でブラウザーを開き、概要にもリンクを表示します。そのタブは開いたままにしてください。起動しなかった場合は、同じマシンで表示された URL をコピーして開いてください。
  </Accordion>

  <Accordion title="localhost とリモートで、ダッシュボード認証はどう違いますか？">
    **localhost（同じマシン）:**

    - `http://127.0.0.1:18789/` を開きます。
    - shared-secret auth を求められたら、設定済みの token または password を Control UI の設定に貼り付けます。
    - token の取得元: `gateway.auth.token`（または `OPENCLAW_GATEWAY_TOKEN`）。
    - password の取得元: `gateway.auth.password`（または `OPENCLAW_GATEWAY_PASSWORD`）。
    - まだ shared secret が設定されていない場合は、`openclaw doctor --generate-gateway-token` で token を生成します。

    **localhost ではない場合:**

    - **Tailscale Serve**（推奨）: bind は loopback のままにし、`openclaw gateway --tailscale serve` を実行して `https://<magicdns>/` を開きます。`gateway.auth.allowTailscale` が `true` の場合、identity headers により Control UI/WebSocket auth を満たします（shared secret を貼り付ける必要はなく、trusted gateway host を前提とします）。HTTP APIs は、明示的に private-ingress `none` や trusted-proxy HTTP auth を使わない限り、引き続き shared-secret auth が必要です。
      同じクライアントからの誤った同時 Serve 認証試行は、failed-auth limiter に記録される前に直列化されるため、2 回目の誤試行でもすでに `retry later` が表示されることがあります。
    - **Tailnet bind**: `openclaw gateway --bind tailnet --token "<token>"` を実行するか（または password auth を設定し）、`http://<tailscale-ip>:18789/` を開いて、対応する shared secret をダッシュボード設定に貼り付けます。
    - **Identity-aware reverse proxy**: Gateway を non-loopback trusted proxy の背後に置き、`gateway.auth.mode: "trusted-proxy"` を設定してから proxy URL を開きます。
    - **SSH tunnel**: `ssh -N -L 18789:127.0.0.1:18789 user@host` を実行し、その後 `http://127.0.0.1:18789/` を開きます。トンネル越しでも shared-secret auth は有効なので、求められたら設定済みの token または password を貼り付けてください。

    bind モードと auth の詳細は [Dashboard](/web/dashboard) と [Web surfaces](/web) を参照してください。

  </Accordion>

  <Accordion title="チャット承認用の exec approval 設定が 2 つあるのはなぜですか？">
    それぞれ別のレイヤーを制御します。

    - `approvals.exec`: 承認プロンプトを chat 宛先へ転送する
    - `channels.<channel>.execApprovals`: そのチャネルを exec approvals 用のネイティブ承認クライアントとして機能させる

    ホスト側の exec policy が、依然として本当の承認ゲートです。チャット設定は、承認プロンプトをどこに表示するかと、人がどう応答できるかだけを制御します。

    多くのセットアップでは、**両方とも**必要ありません。

    - そのチャットがすでにコマンドと返信をサポートしている場合、同一チャットでの `/approve` は共通経路で機能します。
    - サポートされたネイティブチャネルが approver を安全に推定できる場合、OpenClaw は `channels.<channel>.execApprovals.enabled` が未設定または `"auto"` であれば、DM-first のネイティブ承認を自動で有効化します。
    - ネイティブ承認カード/ボタンが利用可能な場合、そのネイティブ UI が主経路です。ツール結果がチャット承認を利用できない、または手動承認しか手段がないと示した場合にのみ、エージェントは手動 `/approve` コマンドを含めるべきです。
    - `approvals.exec` は、プロンプトを他のチャットや明示的な ops room にも転送する必要がある場合にのみ使ってください。
    - `channels.<channel>.execApprovals.target: "channel"` または `"both"` は、承認プロンプトを元の room/topic にも投稿したい場合にのみ使ってください。
    - plugin approvals はさらに別です。デフォルトでは同一チャット `/approve` を使い、必要に応じて `approvals.plugin` 転送を行い、一部のネイティブチャネルのみがその上に plugin-approval-native 処理を持ちます。

    要するに: forwarding は経路制御、native client config はより豊かなチャネル固有 UX のためです。
    [Exec Approvals](/ja-JP/tools/exec-approvals) を参照してください。

  </Accordion>

  <Accordion title="必要なランタイムは？">
    Node **>= 22** が必要です。`pnpm` を推奨します。Gateway に Bun は**推奨されません**。
  </Accordion>

  <Accordion title="Raspberry Pi で動きますか？">
    はい。Gateway は軽量で、ドキュメントでは個人利用なら **512MB-1GB RAM**、**1 core**、約 **500MB** のディスクで十分とされており、**Raspberry Pi 4 で動作可能**と明記されています。

    もう少し余裕がほしい場合（ログ、メディア、他サービス）、**2GB を推奨**しますが、
    必須最低値ではありません。

    ヒント: 小さな Pi/VPS で Gateway を動かし、ローカルの screen/camera/canvas やコマンド実行のためにノート PC/スマホ上の **nodes** をペアリングできます。[Nodes](/ja-JP/nodes) を参照してください。

  </Accordion>

  <Accordion title="Raspberry Pi インストールのコツはありますか？">
    短く言うと: 動きますが、少し荒削りな部分はあります。

    - **64-bit** OS を使い、Node は 22 以上を保ってください。
    - ログ確認や素早い更新のため、**hackable（git）install** を推奨します。
    - channels/Skills なしで始め、あとから 1 つずつ追加してください。
    - 奇妙なバイナリ問題に遭遇した場合、たいていは **ARM compatibility** の問題です。

    ドキュメント: [Linux](/ja-JP/platforms/linux)、[Install](/ja-JP/install)。

  </Accordion>

  <Accordion title="wake up my friend で止まります / オンボーディングが hatch しません。どうすればよいですか？">
    その画面は、Gateway に到達でき、認証できることが前提です。TUI は最初の hatch 時に
    「Wake up, my friend!」も自動送信します。その行が**返信なし**のままで、
    トークン数が 0 のままなら、agent はまったく実行されていません。

    1. Gateway を再起動します:

    ```bash
    openclaw gateway restart
    ```

    2. ステータスと認証を確認します:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. それでも止まる場合は、次を実行します:

    ```bash
    openclaw doctor
    ```

    Gateway がリモートにある場合は、トンネル/Tailscale 接続が有効で、UI が正しい Gateway を向いていることを確認してください。[Remote access](/ja-JP/gateway/remote) を参照してください。

  </Accordion>

  <Accordion title="オンボーディングをやり直さずにセットアップを新しいマシン（Mac mini）へ移行できますか？">
    はい。**state directory** と **workspace** をコピーし、その後 doctor を 1 回実行してください。これにより
    **両方の場所**をコピーすれば、ボットを「まったく同じ状態」（memory、session history、auth、channel state）
    のまま保持できます。

    1. 新しいマシンに OpenClaw をインストールします。
    2. 古いマシンから `$OPENCLAW_STATE_DIR`（デフォルト: `~/.openclaw`）をコピーします。
    3. workspace（デフォルト: `~/.openclaw/workspace`）をコピーします。
    4. `openclaw doctor` を実行し、Gateway サービスを再起動します。

    これにより config、auth profiles、WhatsApp creds、sessions、memory が保持されます。
    remote mode の場合、session store と workspace を所有するのは gateway host である点に注意してください。

    **重要:** workspace だけを GitHub に commit/push しても、バックアップされるのは
    **memory + bootstrap files** だけで、**session history や auth** は含まれません。これらは
    `~/.openclaw/` 配下（たとえば `~/.openclaw/agents/<agentId>/sessions/`）にあります。

    関連: [Migrating](/ja-JP/install/migrating)、[Where things live on disk](#where-things-live-on-disk)、
    [Agent workspace](/ja-JP/concepts/agent-workspace)、[Doctor](/ja-JP/gateway/doctor)、
    [Remote mode](/ja-JP/gateway/remote)。

  </Accordion>

  <Accordion title="最新バージョンの新機能はどこで確認できますか？">
    GitHub changelog を確認してください:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    最新の項目は先頭にあります。最上部のセクションが **Unreleased** の場合、
    次の日付付きセクションが最新のリリース版です。項目は **Highlights**、**Changes**、**Fixes**
    （必要に応じて docs/other セクションも）に分かれています。

  </Accordion>

  <Accordion title="docs.openclaw.ai にアクセスできません（SSL エラー）">
    一部の Comcast/Xfinity 接続では、Xfinity Advanced Security により
    `docs.openclaw.ai` が誤ってブロックされます。これを無効化するか、
    `docs.openclaw.ai` を allowlist に追加してから再試行してください。
    解除の助けになるので、こちらにも報告してください: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status)。

    それでもサイトに到達できない場合、ドキュメントは GitHub にミラーされています:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="stable と beta の違いは？">
    **Stable** と **beta** は、別々のコードラインではなく **npm dist-tags** です。

    - `latest` = stable
    - `beta` = テスト用の早期ビルド

    通常、stable リリースは最初に **beta** に入り、その後、明示的な
    promotion ステップで同じバージョンが `latest` に移されます。必要に応じて maintainer が
    直接 `latest` に publish することもあります。そのため、promotion 後は beta と stable が
    **同じバージョン**を指すことがあります。

    変更内容の確認:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    beta と dev の違いやインストール用ワンライナーについては、下の accordion を参照してください。

  </Accordion>

  <Accordion title="beta 版はどうインストールしますか？ beta と dev の違いは？">
    **Beta** は npm dist-tag の `beta` です（promotion 後は `latest` と同じになることがあります）。
    **Dev** は `main` の最新 head（git）です。publish される場合は npm dist-tag `dev` を使います。

    ワンライナー（macOS/Linux）:

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windows installer（PowerShell）:
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    詳細: [Development channels](/ja-JP/install/development-channels) と [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="最新のものを試すには？">
    2 つの方法があります。

    1. **Dev channel（git checkout）:**

    ```bash
    openclaw update --channel dev
    ```

    これにより `main` ブランチへ切り替わり、ソースから更新されます。

    2. **Hackable install（installer site から）:**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    これで編集可能なローカル repo が手に入り、git 経由で更新できます。

    手動でクリーン clone したい場合は、以下を使ってください。

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    ドキュメント: [Update](/cli/update)、[Development channels](/ja-JP/install/development-channels)、
    [Install](/ja-JP/install)。

  </Accordion>

  <Accordion title="インストールとオンボーディングは通常どれくらいかかりますか？">
    おおよその目安:

    - **Install:** 2-5 分
    - **Onboarding:** 5-15 分（設定する channels/models の数によります）

    止まってしまう場合は、[Installer stuck](#quick-start-and-first-run-setup)
    と [I am stuck](#quick-start-and-first-run-setup) 内の高速デバッグループを使ってください。

  </Accordion>

  <Accordion title="インストーラーで止まります。もっと詳細を出すには？">
    インストーラーを **verbose output** 付きで再実行してください:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    verbose 付き beta install:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    hackable（git）install の場合:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Windows（PowerShell）の相当手順:

    ```powershell
    # install.ps1 にはまだ専用の -Verbose フラグはありません。
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    ほかのオプション: [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="Windows で install 時に git not found または openclaw not recognized と出ます">
    Windows でよくある 2 つの問題です。

    **1) npm error spawn git / git not found**

    - **Git for Windows** をインストールし、`git` が PATH に入っていることを確認してください。
    - PowerShell を閉じて再度開き、インストーラーを再実行してください。

    **2) インストール後に openclaw is not recognized と出る**

    - npm の global bin folder が PATH にありません。
    - パスを確認してください:

      ```powershell
      npm config get prefix
      ```

    - そのディレクトリをユーザー PATH に追加してください（Windows では `\bin` 接尾辞は不要で、多くのシステムでは `%AppData%\npm` です）。
    - PATH 更新後は PowerShell を閉じて再度開いてください。

    もっともスムーズな Windows セットアップを望む場合は、native Windows ではなく **WSL2** を使ってください。
    ドキュメント: [Windows](/ja-JP/platforms/windows)。

  </Accordion>

  <Accordion title="Windows の exec 出力で中国語が文字化けします。どうすればよいですか？">
    これは通常、native Windows shell での console code page の不一致です。

    症状:

    - `system.run`/`exec` の出力で中国語が文字化けする
    - 同じコマンドでも別の terminal profile では正しく見える

    PowerShell での簡単な回避策:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    その後、Gateway を再起動してコマンドを再試行してください:

    ```powershell
    openclaw gateway restart
    ```

    最新の OpenClaw でも再現する場合は、以下で追跡/報告してください:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="ドキュメントでは答えが見つかりませんでした。よりよい答えを得るには？">
    **hackable（git）install** を使って完全なソースとドキュメントをローカルに置き、
    そのフォルダーの中から bot（または Claude/Codex）に質問してください。そうすれば
    repo を読んで正確に答えられます。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    詳細: [Install](/ja-JP/install) と [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="Linux に OpenClaw をインストールするには？">
    短い答え: Linux ガイドに従い、その後オンボーディングを実行してください。

    - Linux の最短ルート + service install: [Linux](/ja-JP/platforms/linux)。
    - 完全な手順: [はじめに](/ja-JP/start/getting-started)。
    - Installer + updates: [Install & updates](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="VPS に OpenClaw をインストールするには？">
    どの Linux VPS でも動作します。サーバーにインストールし、SSH/Tailscale で Gateway にアクセスしてください。

    ガイド: [exe.dev](/ja-JP/install/exe-dev)、[Hetzner](/ja-JP/install/hetzner)、[Fly.io](/ja-JP/install/fly)。
    リモートアクセス: [Gateway remote](/ja-JP/gateway/remote)。

  </Accordion>

  <Accordion title="cloud/VPS のインストールガイドはどこにありますか？">
    一般的なプロバイダーをまとめた **hosting hub** があります。1 つ選んでガイドに従ってください。

    - [VPS hosting](/ja-JP/vps)（すべてのプロバイダーを 1 か所に集約）
    - [Fly.io](/ja-JP/install/fly)
    - [Hetzner](/ja-JP/install/hetzner)
    - [exe.dev](/ja-JP/install/exe-dev)

    cloud での動作: **Gateway はサーバー上で動作**し、あなたは
    ノート PC/スマホから Control UI（または Tailscale/SSH）経由でアクセスします。state + workspace は
    サーバー上にあるため、ホストを信頼できる唯一の情報源として扱い、バックアップしてください。

    その cloud Gateway に **nodes**（Mac/iOS/Android/headless）をペアリングすれば、
    Gateway は cloud に置いたまま、ローカルの screen/camera/canvas へのアクセスや
    ノート PC 上でのコマンド実行ができます。

    ハブ: [Platforms](/ja-JP/platforms)。リモートアクセス: [Gateway remote](/ja-JP/gateway/remote)。
    Nodes: [Nodes](/ja-JP/nodes)、[Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="OpenClaw に自分自身を更新させられますか？">
    短い答え: **可能ですが、推奨しません**。更新フローは Gateway を再起動する可能性があり
    （その結果アクティブ session が切断される）、クリーンな git checkout を必要とし、
    確認を求めることもあります。より安全なのは、operator として shell から更新することです。

    CLI を使ってください:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    エージェントから自動化する必要がある場合:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    ドキュメント: [Update](/cli/update)、[Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="オンボーディングは実際に何をするのですか？">
    `openclaw onboard` は推奨セットアップ経路です。**local mode** では次を案内します。

    - **Model/auth setup**（provider OAuth、API keys、Anthropic legacy setup-token、さらに LM Studio などの local model オプション）
    - **Workspace** の場所 + bootstrap files
    - **Gateway settings**（bind/port/auth/tailscale）
    - **Channels**（WhatsApp、Telegram、Discord、Mattermost、Signal、iMessage、および QQ Bot のような bundled channel plugins）
    - **Daemon install**（macOS の LaunchAgent、Linux/WSL2 の systemd user unit）
    - **Health checks** と **Skills** の選択

    また、設定した model が不明または auth 不足の場合は警告も出します。

  </Accordion>

  <Accordion title="これを動かすのに Claude や OpenAI のサブスクリプションは必要ですか？">
    いいえ。OpenClaw は **API keys**（Anthropic/OpenAI/その他）でも、
    **local-only models** でも実行できます。つまり、必要ならデータをデバイス上に保てます。サブスクリプション
    （Claude Pro/Max や OpenAI Codex）は、それらプロバイダーを認証するための任意の方法です。

    OpenClaw での Anthropic は、実務上次のように分かれます。

    - **Anthropic API key**: 通常の Anthropic API 課金
    - **OpenClaw での Claude subscription auth**: Anthropic は
      **2026 年 4 月 4 日 午後 12:00 PT / 午後 8:00 BST** に OpenClaw ユーザーへ、
      これにはサブスクリプションとは別課金の
      **Extra Usage** が必要だと伝えました

    ローカルでの再現でも、`claude -p --append-system-prompt ...` は
    追加されたプロンプトが OpenClaw を識別する場合、同じ Extra Usage guard に当たることがあります。
    一方で、同じプロンプト文字列でも Anthropic SDK + API-key 経路では
    そのブロックは再現しません。OpenAI Codex OAuth は、OpenClaw のような
    外部ツールでの利用を明示的にサポートしています。

    OpenClaw は、ほかにも次のような hosted の subscription-style オプションをサポートします:
    **Qwen Cloud Coding Plan**、**MiniMax Coding Plan**、および
    **Z.AI / GLM Coding Plan**。

    ドキュメント: [Anthropic](/ja-JP/providers/anthropic)、[OpenAI](/ja-JP/providers/openai)、
    [Qwen Cloud](/ja-JP/providers/qwen)、
    [MiniMax](/ja-JP/providers/minimax)、[GLM Models](/ja-JP/providers/glm)、
    [Local models](/ja-JP/gateway/local-models)、[Models](/ja-JP/concepts/models)。

  </Accordion>

  <Accordion title="API キーなしで Claude Max subscription を使えますか？">
    はい。ただし **Extra Usage 付きの Claude subscription auth** として扱ってください。

    Claude Pro/Max サブスクリプションには API key は含まれません。OpenClaw では、
    つまり Anthropic の OpenClaw 固有の課金通知が適用されます: subscription トラフィックには
    **Extra Usage** が必要です。Extra Usage 経路なしで Anthropic トラフィックを使いたい場合は、
    代わりに Anthropic API key を使ってください。

  </Accordion>

  <Accordion title="Claude subscription auth（Claude Pro または Max）をサポートしていますか？">
    はい。ただし、現在のサポートされる解釈は次のとおりです。

    - OpenClaw で subscription を使った Anthropic は **Extra Usage**
    - その経路を使わない Anthropic は **API key**

    Anthropic setup-token は引き続き legacy/manual な OpenClaw 経路として利用でき、
    そこにも Anthropic の OpenClaw 固有課金通知が適用されます。ローカルでも
    `claude -p --append-system-prompt ...` の直接利用で同じ課金 guard を再現しました。
    追加プロンプトが OpenClaw を識別する場合です。一方、同じプロンプト文字列は
    Anthropic SDK + API-key 経路では再現しませんでした。

    production または multi-user ワークロードでは、Anthropic API key auth のほうが
    より安全で、推奨されます。OpenClaw のほかの subscription-style hosted
    オプションについては、[OpenAI](/ja-JP/providers/openai)、[Qwen / Model
    Cloud](/ja-JP/providers/qwen)、[MiniMax](/ja-JP/providers/minimax)、および
    [GLM Models](/ja-JP/providers/glm) を参照してください。

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Anthropic から HTTP 429 rate_limit_error が出るのはなぜですか？">
これは、現在の時間枠で **Anthropic の quota/rate limit** を使い切ったことを意味します。
**Claude CLI** を使っている場合は、時間枠がリセットされるまで待つか、プランをアップグレードしてください。
**Anthropic API key** を使っている場合は、Anthropic Console で
usage/billing を確認し、必要に応じて上限を引き上げてください。

    メッセージが具体的に
    `Extra usage is required for long context requests` の場合、そのリクエストは
    Anthropic の 1M context beta（`context1m: true`）を使おうとしています。これは
    長文コンテキスト課金に対応した credential の場合にのみ動作します（API key 課金または、
    Extra Usage が有効な OpenClaw Claude-login 経路）。

    ヒント: **fallback model** を設定しておくと、provider が rate-limited でも OpenClaw は
    返信を継続できます。[Models](/cli/models)、[OAuth](/ja-JP/concepts/oauth)、および
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/ja-JP/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context) を参照してください。

  </Accordion>

  <Accordion title="AWS Bedrock はサポートされていますか？">
    はい。OpenClaw には bundled の **Amazon Bedrock (Converse)** provider があります。AWS env markers が存在する場合、OpenClaw は streaming/text の Bedrock catalog を自動検出し、暗黙の `amazon-bedrock` provider としてマージできます。そうでない場合でも、`plugins.entries.amazon-bedrock.config.discovery.enabled` を明示的に有効にするか、手動で provider entry を追加できます。[Amazon Bedrock](/ja-JP/providers/bedrock) と [Model providers](/ja-JP/providers/models) を参照してください。managed key flow を好む場合は、Bedrock の前段に OpenAI-compatible proxy を置く方法も有効です。
  </Accordion>

  <Accordion title="Codex auth はどのように動きますか？">
    OpenClaw は **OpenAI Code (Codex)** を OAuth（ChatGPT sign-in）でサポートします。Onboarding は OAuth フローを実行でき、適切な場合はデフォルト model を `openai-codex/gpt-5.4` に設定します。[Model providers](/ja-JP/concepts/model-providers) と [Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。
  </Accordion>

  <Accordion title="OpenAI subscription auth（Codex OAuth）をサポートしていますか？">
    はい。OpenClaw は **OpenAI Code (Codex) subscription OAuth** を完全にサポートしています。
    OpenAI は、OpenClaw のような外部ツール/ワークフローでの subscription OAuth 利用を
    明示的に許可しています。Onboarding がその OAuth フローを実行できます。

    [OAuth](/ja-JP/concepts/oauth)、[Model providers](/ja-JP/concepts/model-providers)、および [Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。

  </Accordion>

  <Accordion title="Gemini CLI OAuth はどう設定しますか？">
    Gemini CLI は **plugin auth flow** を使います。`openclaw.json` に client id や secret を入れる方式ではありません。

    代わりに Gemini API provider を使ってください:

    1. plugin を有効化します: `openclaw plugins enable google`
    2. `openclaw onboard --auth-choice gemini-api-key` を実行します
    3. `google/gemini-3.1-pro-preview` のような Google model を設定します

  </Accordion>

  <Accordion title="気軽な雑談用途なら local model で大丈夫ですか？">
    通常はいいえ。OpenClaw には広い context と強い安全性が必要です。小さなカードでは切り詰めや漏れが起きます。どうしても使うなら、ローカルで動かせる**できるだけ大きな** model build を使ってください（LM Studio）。[/gateway/local-models](/ja-JP/gateway/local-models) を参照してください。小型/量子化モデルほど prompt-injection のリスクが高くなります。[Security](/ja-JP/gateway/security) を参照してください。
  </Accordion>

  <Accordion title="ホスト型モデルのトラフィックを特定リージョンに留めるには？">
    リージョン固定の endpoint を選んでください。OpenRouter は MiniMax、Kimi、GLM 向けに米国内ホストのオプションを提供しているので、US-hosted のものを選べばデータをリージョン内に留められます。それでも `models.mode: "merge"` を使えば、選んだリージョン固定 provider を尊重しつつ Anthropic/OpenAI も並べて fallback を維持できます。
  </Accordion>

  <Accordion title="これをインストールするには Mac Mini を買う必要がありますか？">
    いいえ。OpenClaw は macOS または Linux（Windows は WSL2 経由）で動作します。Mac mini は任意です。
    常時稼働ホストとして購入する人もいますが、小さな VPS、ホームサーバー、または Raspberry Pi クラスのマシンでも動作します。

    Mac が必要なのは **macOS-only tools** の場合だけです。iMessage には [BlueBubbles](/ja-JP/channels/bluebubbles)（推奨）を使ってください。BlueBubbles server はどの Mac でも動作し、Gateway は Linux など別ホストでも動かせます。ほかの macOS-only tools が必要な場合は、Gateway を Mac 上で動かすか、macOS node をペアリングしてください。

    ドキュメント: [BlueBubbles](/ja-JP/channels/bluebubbles)、[Nodes](/ja-JP/nodes)、[Mac remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="iMessage を使うには Mac mini が必要ですか？">
    **Messages にサインインした macOS デバイス**が必要です。Mac mini である必要はなく、
    どんな Mac でも構いません。iMessage には **[BlueBubbles](/ja-JP/channels/bluebubbles)**（推奨）を使ってください。
    BlueBubbles server は macOS 上で動作し、Gateway は Linux や別ホストでも動かせます。

    よくあるセットアップ:

    - Gateway は Linux/VPS で動かし、BlueBubbles server は Messages にサインインした任意の Mac で動かす。
    - 最も簡単な単一マシン構成にしたいなら、すべてをその Mac 上で動かす。

    ドキュメント: [BlueBubbles](/ja-JP/channels/bluebubbles)、[Nodes](/ja-JP/nodes)、
    [Mac remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="OpenClaw 用に Mac mini を買ったら、MacBook Pro から接続できますか？">
    はい。**Mac mini で Gateway を動かし**、MacBook Pro は
    **node**（companion device）として接続できます。Nodes は Gateway 自体は動かさず、
    そのデバイス上の screen/camera/canvas や `system.run` のような追加機能を提供します。

    よくある構成:

    - Gateway は Mac mini 上（常時稼働）。
    - MacBook Pro は macOS app または node host を実行して Gateway とペアリング。
    - `openclaw nodes status` / `openclaw nodes list` で確認できます。

    ドキュメント: [Nodes](/ja-JP/nodes)、[Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="Bun は使えますか？">
    Bun は**推奨されません**。特に WhatsApp と Telegram でランタイムの不具合が見られます。
    安定した Gateway には **Node** を使ってください。

    それでも Bun を試したい場合は、WhatsApp/Telegram を使わない
    非 production Gateway で試してください。

  </Accordion>

  <Accordion title="Telegram の allowFrom には何を入れますか？">
    `channels.telegram.allowFrom` は**人間の送信者の Telegram user ID**（数値）です。bot username ではありません。

    Onboarding は `@username` 入力を受け取り、それを数値 ID に解決しますが、OpenClaw の認可は数値 ID のみを使います。

    より安全な方法（サードパーティ bot 不要）:

    - bot に DM を送り、その後 `openclaw logs --follow` を実行して `from.id` を確認します。

    公式 Bot API:

    - bot に DM を送り、その後 `https://api.telegram.org/bot<bot_token>/getUpdates` を呼び、`message.from.id` を確認します。

    サードパーティ（プライバシーはやや低い）:

    - `@userinfobot` または `@getidsbot` に DM を送る。

    [/channels/telegram](/ja-JP/channels/telegram#access-control-and-activation) を参照してください。

  </Accordion>

  <Accordion title="複数の人が、別々の OpenClaw instance で 1 つの WhatsApp 番号を使えますか？">
    はい。**multi-agent routing** によって可能です。各送信者の WhatsApp **DM**（peer `kind: "direct"`、送信者 E.164 形式 `+15551234567` など）を別々の `agentId` に紐付ければ、各人が自分専用の workspace と session store を持てます。返信は引き続き**同じ WhatsApp account**から送られ、DM access control（`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`）はその WhatsApp account 全体で共有されます。[Multi-Agent Routing](/ja-JP/concepts/multi-agent) と [WhatsApp](/ja-JP/channels/whatsapp) を参照してください。
  </Accordion>

  <Accordion title='「fast chat」agent と「Opus for coding」agent を動かせますか？'>
    はい。multi-agent routing を使って、各 agent に別々の default model を持たせ、受信ルート（provider account または特定 peer）をそれぞれの agent に bind してください。設定例は [Multi-Agent Routing](/ja-JP/concepts/multi-agent) にあります。[Models](/ja-JP/concepts/models) と [Configuration](/ja-JP/gateway/configuration) も参照してください。
  </Accordion>

  <Accordion title="Homebrew は Linux でも動きますか？">
    はい。Homebrew は Linux（Linuxbrew）をサポートしています。簡単なセットアップ:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    OpenClaw を systemd で実行する場合、サービスの PATH に `/home/linuxbrew/.linuxbrew/bin`（または自分の brew prefix）が含まれていることを確認してください。そうしないと、非ログインシェルで `brew` インストール済みツールが解決されません。
    最近のビルドでは、Linux の systemd services に一般的な user bin dirs（たとえば `~/.local/bin`、`~/.npm-global/bin`、`~/.local/share/pnpm`、`~/.bun/bin`）も前置され、`PNPM_HOME`、`NPM_CONFIG_PREFIX`、`BUN_INSTALL`、`VOLTA_HOME`、`ASDF_DATA_DIR`、`NVM_DIR`、`FNM_DIR` が設定されていればそれも考慮されます。

  </Accordion>

  <Accordion title="hackable git install と npm install の違いは？">
    - **Hackable（git）install:** 完全なソース checkout、編集可能、コントリビューターに最適。
      ビルドをローカルで行い、コード/ドキュメントを修正できます。
    - **npm install:** グローバル CLI install、repo なし、「とにかく動かしたい」用途に最適。
      更新は npm dist-tags から取得します。

    ドキュメント: [はじめに](/ja-JP/start/getting-started)、[Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="あとから npm install と git install を切り替えられますか？">
    はい。別の種類をインストールし、その後 Doctor を実行して gateway service が新しい entrypoint を向くようにしてください。
    これで**データが削除されることはありません**。変わるのは OpenClaw のコード install だけです。state
    （`~/.openclaw`）と workspace（`~/.openclaw/workspace`）はそのままです。

    npm から git へ:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    git から npm へ:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor は gateway service entrypoint の不一致を検出し、現在の install に合わせて service config の書き換えを提案します（自動化では `--repair` を使用）。

    バックアップのヒント: [Backup strategy](#where-things-live-on-disk) を参照してください。

  </Accordion>

  <Accordion title="Gateway はノート PC と VPS のどちらで動かすべきですか？">
    短い答え: **24/7 の信頼性が欲しいなら VPS**。手軽さ重視で、sleep/restart を許容できるならローカル実行です。

    **ノート PC（local Gateway）**

    - **長所:** サーバー費用不要、ローカルファイルへ直接アクセス、ブラウザーウィンドウをそのまま見られる。
    - **短所:** sleep/ネットワーク切断 = 切断、OS 更新/再起動で中断、起動し続ける必要がある。

    **VPS / cloud**

    - **長所:** 常時稼働、安定したネットワーク、ノート PC の sleep 問題なし、稼働維持が容易。
    - **短所:** headless で動くことが多い（スクリーンショットを使う）、ファイルアクセスはリモートのみ、更新には SSH が必要。

    **OpenClaw 固有の補足:** WhatsApp/Telegram/Slack/Mattermost/Discord はいずれも VPS で問題なく動きます。実質的な違いは **headless browser** か可視ウィンドウかです。[Browser](/ja-JP/tools/browser) を参照してください。

    **推奨デフォルト:** 以前 gateway の切断で困ったことがあるなら VPS。ローカルは、Mac を能動的に使っていて、ローカルファイルアクセスや可視ブラウザーによる UI automation が欲しいときに最適です。

  </Accordion>

  <Accordion title="専用マシンで OpenClaw を動かす重要性はどれくらいですか？">
    必須ではありませんが、**信頼性と分離の観点から推奨**です。

    - **専用ホスト（VPS/Mac mini/Pi）:** 常時稼働、sleep/reboot の中断が少ない、権限が整理しやすい、稼働維持が簡単。
    - **共用ノート PC/デスクトップ:** テストや能動的な利用にはまったく問題ありませんが、マシンの sleep や更新で一時停止しがちです。

    両方の利点が欲しいなら、Gateway は専用ホストに置き、ローカルの screen/camera/exec tools 用にノート PC を **node** としてペアリングしてください。[Nodes](/ja-JP/nodes) を参照してください。
    セキュリティ指針は [Security](/ja-JP/gateway/security) を参照してください。

  </Accordion>

  <Accordion title="最低限の VPS 要件と推奨 OS は？">
    OpenClaw は軽量です。基本的な Gateway + 1 つの chat channel なら:

    - **絶対的な最低構成:** 1 vCPU、1GB RAM、約 500MB ディスク。
    - **推奨:** 1-2 vCPU、2GB RAM 以上の余裕（ログ、メディア、複数 channels）。Node tools と browser automation はリソースを消費しやすいです。

    OS は **Ubuntu LTS**（または最新の Debian/Ubuntu 系）を使ってください。Linux install path はそこで最もよくテストされています。

    ドキュメント: [Linux](/ja-JP/platforms/linux)、[VPS hosting](/ja-JP/vps)。

  </Accordion>

  <Accordion title="VM で OpenClaw を動かせますか？要件は？">
    はい。VM も VPS と同様に扱ってください: 常時起動していて、到達可能で、
    有効にする channels に対して十分な RAM が必要です。

    基本的な目安:

    - **絶対的な最低構成:** 1 vCPU、1GB RAM。
    - **推奨:** 複数 channels、browser automation、media tools を使うなら 2GB RAM 以上。
    - **OS:** Ubuntu LTS または最新の Debian/Ubuntu 系。

    Windows の場合、**WSL2 が最も簡単な VM 風セットアップ**で、ツール互換性も最良です。
    [Windows](/ja-JP/platforms/windows)、[VPS hosting](/ja-JP/vps) を参照してください。
    macOS を VM 上で動かす場合は [macOS VM](/ja-JP/install/macos-vm) を参照してください。

  </Accordion>
</AccordionGroup>

## OpenClaw とは何ですか？

<AccordionGroup>
  <Accordion title="OpenClaw を 1 段落で説明すると？">
    OpenClaw は、自分のデバイス上で動かす個人用 AI assistant です。すでに使っているメッセージング面（WhatsApp、Telegram、Slack、Mattermost、Discord、Google Chat、Signal、iMessage、WebChat、および QQ Bot のような bundled channel plugins）で返信でき、対応プラットフォームでは音声 + live Canvas も使えます。**Gateway** は常時稼働する control plane であり、assistant こそが製品です。
  </Accordion>

  <Accordion title="価値提案">
    OpenClaw は「Claude wrapper にすぎない」ものではありません。**local-first control plane** であり、
    **自分のハードウェア上**で、すでに使っている chat apps から到達できる
    高機能 assistant を、stateful sessions、memory、tools とともに動かせます。しかも、
    ワークフローの制御をホスト型 SaaS に渡さずに済みます。

    ハイライト:

    - **自分のデバイス、自分のデータ:** Gateway を好きな場所（Mac、Linux、VPS）で動かし、
      workspace + session history をローカルに保持できます。
    - **Web sandbox ではなく実際の channels:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage などに加え、
      対応プラットフォームでは mobile voice と Canvas も利用可能。
    - **Model-agnostic:** Anthropic、OpenAI、MiniMax、OpenRouter などを、agent 単位の routing
      と failover 付きで使えます。
    - **Local-only option:** local models を使えば、必要に応じて **すべてのデータをデバイス上**に留められます。
    - **Multi-agent routing:** channel、account、task ごとに別々の agents を持て、それぞれ独自の
      workspace と defaults を持てます。
    - **オープンソースで hackable:** inspect、extend、self-host ができ、vendor lock-in がありません。

    ドキュメント: [Gateway](/ja-JP/gateway)、[Channels](/ja-JP/channels)、[Multi-agent](/ja-JP/concepts/multi-agent)、
    [Memory](/ja-JP/concepts/memory)。

  </Accordion>

  <Accordion title="セットアップしたばかりですが、最初に何をすればよいですか？">
    最初のプロジェクト候補:

    - Web サイトを作る（WordPress、Shopify、または単純な静的サイト）。
    - モバイルアプリを試作する（構成、画面、API プラン）。
    - ファイルとフォルダーを整理する（クリーンアップ、命名、タグ付け）。
    - Gmail を接続して要約やフォローアップを自動化する。

    大きなタスクも扱えますが、フェーズに分けて
    sub agents を使って並列化すると最も効果的です。

  </Accordion>

  <Accordion title="OpenClaw の日常的な利用用途トップ 5 は何ですか？">
    日常で役立つ使い方はたいてい次のようなものです。

    - **個人向けブリーフィング:** inbox、calendar、関心のあるニュースの要約。
    - **調査と下書き:** メールやドキュメントのための素早い調査、要約、初稿作成。
    - **リマインダーとフォローアップ:** cron や heartbeat による通知とチェックリスト。
    - **ブラウザー自動化:** フォーム入力、データ収集、繰り返しの web 作業。
    - **デバイス横断の調整:** スマホからタスクを送り、Gateway がサーバー上で実行し、結果を chat に返す。

  </Accordion>

  <Accordion title="SaaS 向けの lead gen、outreach、広告、ブログに OpenClaw を使えますか？">
    はい。**調査、選別、下書き**には向いています。サイトを巡回し、候補リストを作り、
    見込み客を要約し、outreach や広告文の下書きを書けます。

    **outreach や広告運用**については、人間を必ず介在させてください。スパムを避け、
    現地法やプラットフォームポリシーに従い、送信前に必ず確認してください。最も安全なのは、
    OpenClaw に下書きさせてあなたが承認する形です。

    ドキュメント: [Security](/ja-JP/gateway/security)。

  </Accordion>

  <Accordion title="Web 開発では Claude Code と比べて何が優れていますか？">
    OpenClaw は **個人 assistant** かつ coordination layer であり、IDE の置き換えではありません。repo 内で最速の直接コーディングループが必要なら
    Claude Code や Codex を使ってください。OpenClaw は、永続 memory、クロスデバイスアクセス、
    tool orchestration が必要なときに使ってください。

    利点:

    - セッションをまたぐ **永続 memory + workspace**
    - **マルチプラットフォームアクセス**（WhatsApp、Telegram、TUI、WebChat）
    - **Tool orchestration**（browser、files、scheduling、hooks）
    - **常時稼働 Gateway**（VPS 上で動かし、どこからでも利用可能）
    - ローカル browser/screen/camera/exec 用の **Nodes**

    紹介: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills と automation

<AccordionGroup>
  <Accordion title="repo を dirty にせず Skills をカスタマイズするには？">
    repo のコピーを直接編集する代わりに、managed overrides を使ってください。変更内容は `~/.openclaw/skills/<name>/SKILL.md` に置くか、`~/.openclaw/openclaw.json` の `skills.load.extraDirs` でフォルダーを追加してください。優先順位は `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` なので、managed overrides は git に触れず bundled skills より優先されます。skill をグローバルにインストールしつつ一部の agents にだけ見せたい場合は、共有コピーを `~/.openclaw/skills` に置き、表示制御には `agents.defaults.skills` と `agents.list[].skills` を使ってください。upstream に送る価値がある変更だけを repo に置き、PR として送ってください。
  </Accordion>

  <Accordion title="Skills をカスタムフォルダーから読み込めますか？">
    はい。`~/.openclaw/openclaw.json` の `skills.load.extraDirs` で追加ディレクトリを指定できます（最も低い優先順位）。デフォルトの優先順位は `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` です。`clawhub` はデフォルトで `./skills` にインストールし、OpenClaw はそれを次のセッションで `<workspace>/skills` として扱います。skill を一部の agents にだけ見せたい場合は、`agents.defaults.skills` または `agents.list[].skills` と組み合わせてください。
  </Accordion>

  <Accordion title="タスクごとに異なるモデルを使うには？">
    現時点でサポートされるパターンは次のとおりです。

    - **Cron jobs**: isolated jobs はジョブごとに `model` override を設定できます。
    - **Sub-agents**: デフォルト model の異なる別 agents にタスクを振り分けます。
    - **On-demand switch**: `/model` を使って現在の session model をいつでも切り替えます。

    [Cron jobs](/ja-JP/automation/cron-jobs)、[Multi-Agent Routing](/ja-JP/concepts/multi-agent)、[Slash commands](/ja-JP/tools/slash-commands) を参照してください。

  </Accordion>

  <Accordion title="重い作業中に bot が固まります。どうやってオフロードしますか？">
    長いタスクや並列タスクには **sub-agents** を使ってください。Sub-agents は独自の session で実行され、
    要約を返し、メインチャットを応答可能なまま保ちます。

    bot に「このタスク用に sub-agent を spawn して」と頼むか、`/subagents` を使ってください。
    Gateway が今何をしているか（および busy かどうか）を見るには、chat で `/status` を使います。

    トークンのヒント: 長いタスクも sub-agents もトークンを消費します。コストが気になる場合は、
    `agents.defaults.subagents.model` で sub-agents 用に安価な model を設定してください。

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents)、[Background Tasks](/ja-JP/automation/tasks)。

  </Accordion>

  <Accordion title="Discord で thread-bound subagent sessions はどう動きますか？">
    thread bindings を使います。Discord thread を subagent または session target に bind できるので、その thread 内の follow-up messages はその bound session に留まります。

    基本フロー:

    - `sessions_spawn` を `thread: true`（必要なら `mode: "session"` も）付きで使って spawn します。
    - または `/focus <target>` で手動 bind。
    - `/agents` で binding 状態を確認。
    - `/session idle <duration|off>` と `/session max-age <duration|off>` で auto-unfocus を制御。
    - `/unfocus` で thread を切り離します。

    必要な設定:

    - グローバルデフォルト: `session.threadBindings.enabled`、`session.threadBindings.idleHours`、`session.threadBindings.maxAgeHours`。
    - Discord overrides: `channels.discord.threadBindings.enabled`、`channels.discord.threadBindings.idleHours`、`channels.discord.threadBindings.maxAgeHours`。
    - spawn 時に自動 bind: `channels.discord.threadBindings.spawnSubagentSessions: true` を設定。

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents)、[Discord](/ja-JP/channels/discord)、[Configuration Reference](/ja-JP/gateway/configuration-reference)、[Slash commands](/ja-JP/tools/slash-commands)。

  </Accordion>

  <Accordion title="subagent は完了したのに、completion update が別の場所へ行った、または投稿されませんでした。何を確認すべきですか？">
    まず解決された requester route を確認してください。

    - completion-mode の subagent delivery は、bound された thread または conversation route があればそれを優先します。
    - completion origin が channel しか持たない場合、OpenClaw は requester session に保存された route（`lastChannel` / `lastTo` / `lastAccountId`）へフォールバックするため、直接配信が依然として成功することがあります。
    - bound route も usable な stored route もない場合、直接配信に失敗し、結果は即時投稿ではなく queued session delivery にフォールバックすることがあります。
    - 無効または古い target により、queue fallback や最終配信失敗が起きることもあります。
    - child の最後の可視 assistant reply が厳密にサイレントトークン `NO_REPLY` / `no_reply`、または厳密に `ANNOUNCE_SKIP` の場合、OpenClaw は古い進捗を投稿しないよう、announce を意図的に抑制します。
    - child が tool calls だけで timeout した場合、announce は生の tool output を再生する代わりに、それを短い partial-progress summary へまとめることがあります。

    デバッグ:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents)、[Background Tasks](/ja-JP/automation/tasks)、[Session Tools](/ja-JP/concepts/session-tool)。

  </Accordion>

  <Accordion title="Cron や reminders が発火しません。何を確認すべきですか？">
    Cron は Gateway process 内で動作します。Gateway が継続的に動いていないと、
    scheduled jobs は実行されません。

    チェックリスト:

    - cron が有効か（`cron.enabled`）、`OPENCLAW_SKIP_CRON` が設定されていないか確認。
    - Gateway が 24/7 稼働しているか確認（sleep/restart なし）。
    - ジョブの timezone 設定を確認（`--tz` と host timezone）。

    デバッグ:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs)、[Automation & Tasks](/ja-JP/automation)。

  </Accordion>

  <Accordion title="Cron は発火したのに、何も channel に送信されませんでした。なぜですか？">
    まず delivery mode を確認してください。

    - `--no-deliver` / `delivery.mode: "none"` の場合、外部メッセージは送られません。
    - announce target（`channel` / `to`）が欠落または無効だと、runner は outbound delivery をスキップします。
    - channel auth failures（`unauthorized`、`Forbidden`）は、runner が配信を試みたが credentials によりブロックされたことを意味します。
    - サイレントな isolated result（`NO_REPLY` / `no_reply` のみ）は意図的に非配信と見なされるため、runner は queued fallback delivery も抑制します。

    isolated cron jobs では、最終 delivery は runner が担当します。agent は
    runner が送るための plain-text summary を返すことが期待されます。`--no-deliver` は
    その結果を内部に留めるだけであり、agent が message tool で直接送ってよいという意味ではありません。

    デバッグ:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs)、[Background Tasks](/ja-JP/automation/tasks)。

  </Accordion>

  <Accordion title="isolated cron run がモデルを切り替えたり 1 回再試行したりしたのはなぜですか？">
    それは通常、重複スケジューリングではなく live model-switch path です。

    isolated cron は、アクティブ実行が `LiveSessionModelSwitchError` を投げたときに、
    ランタイム model handoff を永続化して再試行できます。再試行では切り替え後の
    provider/model を保持し、その切り替えが新しい auth profile override を伴っていた場合、
    cron はそれも永続化してから再試行します。

    関連する選択ルール:

    - 該当する場合は Gmail hook model override が最優先。
    - 次にジョブごとの `model`。
    - 次に保存済みの cron-session model override。
    - 最後に通常の agent/default model selection。

    再試行ループには上限があります。初回試行に加えて 2 回の switch retry の後、
    cron は無限ループせず中断します。

    デバッグ:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs)、[cron CLI](/cli/cron)。

  </Accordion>

  <Accordion title="Linux で Skills をインストールするには？">
    ネイティブの `openclaw skills` コマンドを使うか、workspace に skills を置いてください。macOS の Skills UI は Linux では利用できません。
    Skills は [https://clawhub.ai](https://clawhub.ai) で閲覧できます。

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    ネイティブの `openclaw skills install` は、アクティブな workspace の `skills/`
    ディレクトリに書き込みます。自分の skills を publish または sync したい場合にのみ、
    別途 `clawhub` CLI をインストールしてください。agents 間で共有する install には、skill を `~/.openclaw/skills` 配下に置き、
    一部の agents にだけ見せたい場合は `agents.defaults.skills` または
    `agents.list[].skills` を使ってください。

  </Accordion>

  <Accordion title="OpenClaw は、スケジュール実行や継続的なバックグラウンド実行ができますか？">
    はい。Gateway scheduler を使います。

    - **Cron jobs**: scheduled または recurring tasks 用（再起動をまたいで持続）。
    - **Heartbeat**: 「main session」の定期チェック用。
    - **Isolated jobs**: 要約を投稿したり chat へ配信したりする autonomous agents 用。

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs)、[Automation & Tasks](/ja-JP/automation)、
    [Heartbeat](/ja-JP/gateway/heartbeat)。

  </Accordion>

  <Accordion title="Linux から Apple の macOS-only skills を実行できますか？">
    直接はできません。macOS skills は `metadata.openclaw.os` と必要なバイナリで gate されており、skills は **Gateway host** 上で条件を満たす場合にのみシステムプロンプトへ表示されます。Linux では、`darwin` 専用 skills（`apple-notes`、`apple-reminders`、`things-mac` など）は gating を override しない限り読み込まれません。

    サポートされる方法は 3 つあります。

    **Option A - Gateway を Mac 上で動かす（最も簡単）。**
    macOS バイナリが存在する場所で Gateway を動かし、その後 Linux から [remote mode](#gateway-ports-already-running-and-remote-mode) または Tailscale 経由で接続します。Gateway host が macOS なので、skills は通常どおり読み込まれます。

    **Option B - macOS node を使う（SSH なし）。**
    Gateway は Linux 上で動かし、macOS node（menubar app）をペアリングして、Mac 上で **Node Run Commands** を「Always Ask」または「Always Allow」に設定します。必要なバイナリが node 上に存在する場合、OpenClaw は macOS-only skills を eligible と見なせます。agent はそれらの skills を `nodes` tool 経由で実行します。「Always Ask」を選んだ場合、プロンプトで「Always Allow」を承認すると、そのコマンドが allowlist に追加されます。

    **Option C - macOS バイナリを SSH 越しにプロキシする（上級者向け）。**
    Gateway は Linux 上に置いたまま、必要な CLI バイナリが Mac 上で実行される SSH wrapper に解決されるようにします。そのうえで、Linux を許可するよう skill を override し、eligible のままにします。

    1. バイナリ用の SSH wrapper を作ります（例: Apple Notes 用の `memo`）:

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. その wrapper を Linux host の `PATH` に置きます（例: `~/bin/memo`）。
    3. skill metadata を override して Linux を許可します（workspace または `~/.openclaw/skills`）:

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. 新しい session を開始して skills snapshot を更新します。

  </Accordion>

  <Accordion title="Notion や HeyGen との統合はありますか？">
    現時点で built-in はありません。

    選択肢:

    - **Custom skill / plugin:** 信頼性の高い API アクセスに最適（Notion/HeyGen はどちらも API あり）。
    - **Browser automation:** コード不要で動きますが、遅く壊れやすいです。

    client ごとの context を保ちたい場合（agency ワークフローなど）の単純なパターン:

    - client ごとに 1 つの Notion page（context + preferences + active work）。
    - session 開始時に、その page を取得するよう agent に依頼する。

    ネイティブ統合が欲しい場合は、feature request を作成するか、
    それらの API を対象にした skill を作ってください。

    Skills のインストール:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    ネイティブ install は、アクティブ workspace の `skills/` ディレクトリに配置されます。agents 間で共有する skills には `~/.openclaw/skills/<name>/SKILL.md` に置いてください。共有 install を一部の agents にだけ見せたい場合は、`agents.defaults.skills` または `agents.list[].skills` を設定してください。一部の skills は Homebrew でインストールしたバイナリを前提とします。Linux では Linuxbrew を意味します（上の Homebrew Linux FAQ 項目を参照）。[Skills](/ja-JP/tools/skills)、[Skills config](/ja-JP/tools/skills-config)、および [ClawHub](/ja-JP/tools/clawhub) を参照してください。

  </Accordion>

  <Accordion title="既存のサインイン済み Chrome を OpenClaw で使うには？">
    Chrome DevTools MCP 経由で接続する、built-in の `user` browser profile を使ってください。

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    カスタム名を使いたい場合は、明示的な MCP profile を作成します。

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    この経路は host-local です。Gateway が別ホストで動いている場合は、browser マシン上で node host を動かすか、remote CDP を使ってください。

    `existing-session` / `user` の現在の制限:

    - actions は CSS-selector ベースではなく ref ベース
    - uploads には `ref` / `inputRef` が必要で、現在は 1 回に 1 ファイルのみサポート
    - `responsebody`、PDF export、download interception、batch actions は引き続き managed browser または raw CDP profile が必要

  </Accordion>
</AccordionGroup>

## Sandboxing と memory

<AccordionGroup>
  <Accordion title="sandboxing 専用のドキュメントはありますか？">
    はい。[Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。Docker 固有のセットアップ（Gateway 全体を Docker で動かす場合や sandbox images）については [Docker](/ja-JP/install/docker) を参照してください。
  </Accordion>

  <Accordion title="Docker だと機能が制限されているように感じます。フル機能を有効にするには？">
    デフォルトの image は security-first で `node` user として動作するため、
    system packages、Homebrew、bundled browsers は含まれていません。より充実したセットアップにするには:

    - `OPENCLAW_HOME_VOLUME` で `/home/node` を永続化し、cache を保持する。
    - `OPENCLAW_DOCKER_APT_PACKAGES` で system deps を image に焼き込む。
    - bundled CLI で Playwright browsers をインストールする:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - `PLAYWRIGHT_BROWSERS_PATH` を設定し、そのパスが永続化されるようにする。

    ドキュメント: [Docker](/ja-JP/install/docker)、[Browser](/ja-JP/tools/browser)。

  </Accordion>

  <Accordion title="1 つの agent で、DM は個人的に、groups は public/sandboxed にできますか？">
    はい。プライベートのトラフィックが **DMs** で、公開トラフィックが **groups** なら可能です。

    `agents.defaults.sandbox.mode: "non-main"` を使って、group/channel sessions（non-main keys）を Docker 内で実行し、main DM session はホスト上のままにします。そのうえで `tools.sandbox.tools` を使って、sandboxed sessions で利用可能な tools を制限してください。

    セットアップ手順 + 設定例: [Groups: personal DMs + public groups](/ja-JP/channels/groups#pattern-personal-dms-public-groups-single-agent)

    主な設定リファレンス: [Gateway configuration](/ja-JP/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="ホストのフォルダーを sandbox に bind するには？">
    `agents.defaults.sandbox.docker.binds` を `["host:path:mode"]`（例: `"/home/user/src:/src:ro"`）に設定してください。global と per-agent の binds はマージされ、`scope: "shared"` の場合は per-agent binds は無視されます。機密性の高いものには `:ro` を使い、binds は sandbox のファイルシステム壁を迂回することを忘れないでください。

    OpenClaw は bind の source を、正規化パスと最も深い既存 ancestor を通して解決した canonical path の両方に対して検証します。つまり、最後のパスセグメントがまだ存在しない場合でも symlink-parent による escape は fail closed となり、allowed-root チェックも symlink 解決後に適用されます。

    例と安全上の注意については [Sandboxing](/ja-JP/gateway/sandboxing#custom-bind-mounts) と [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) を参照してください。

  </Accordion>

  <Accordion title="memory はどのように動きますか？">
    OpenClaw の memory は、agent workspace 内の Markdown files にすぎません。

    - `memory/YYYY-MM-DD.md` に daily notes
    - `MEMORY.md` に curated な long-term notes（main/private sessions のみ）

    OpenClaw は **silent pre-compaction memory flush** も実行し、
    auto-compaction の前に durable notes を書くよう model に促します。これは workspace が
    writable な場合にのみ動作します（read-only sandboxes ではスキップされます）。[Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>

  <Accordion title="memory が物事を忘れ続けます。どうすれば定着しますか？">
    bot に **その事実を memory に書くよう**依頼してください。長期的なメモは `MEMORY.md` に、
    短期的な文脈は `memory/YYYY-MM-DD.md` に入れます。

    この領域はまだ改善中です。model に memories を保存するようリマインドすると役立ちます。
    やるべきことは理解しています。それでも忘れる場合は、Gateway が毎回同じ
    workspace を使っているか確認してください。

    ドキュメント: [Memory](/ja-JP/concepts/memory)、[Agent workspace](/ja-JP/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="memory は永久に保持されますか？制限はありますか？">
    Memory files はディスク上に存在し、削除するまで保持されます。制限は
    model ではなくストレージです。ただし **session context** は依然として model の
    context window に制約されるため、長い会話では compact または truncate が起きます。それが
    memory search が存在する理由です。関連する部分だけを context に戻します。

    ドキュメント: [Memory](/ja-JP/concepts/memory)、[Context](/ja-JP/concepts/context)。

  </Accordion>

  <Accordion title="semantic memory search には OpenAI API key が必要ですか？">
    **OpenAI embeddings** を使う場合に限ります。Codex OAuth は chat/completions を対象とし、
    embeddings へのアクセスは付与しません。したがって、**Codex にサインインしても（OAuth でも
    Codex CLI login でも）** semantic memory search には役立ちません。OpenAI embeddings には
    引き続き実際の API key（`OPENAI_API_KEY` または `models.providers.openai.apiKey`）が必要です。

    provider を明示設定しない場合、OpenClaw は API key を解決できたときに
    provider を自動選択します（auth profiles、`models.providers.*.apiKey`、または env vars）。
    OpenAI key が解決できるなら OpenAI を優先し、そうでなければ Gemini、
    次に Voyage、次に Mistral を優先します。remote key がない場合は、
    設定するまで memory search は無効のままです。local model path が設定され、
    存在する場合、OpenClaw は
    `local` を優先します。Ollama は、`memorySearch.provider = "ollama"` を明示的に設定した場合にサポートされます。

    完全にローカルにしたい場合は、`memorySearch.provider = "local"`（必要なら
    `memorySearch.fallback = "none"` も）を設定してください。Gemini embeddings を使う場合は、
    `memorySearch.provider = "gemini"` を設定し、`GEMINI_API_KEY`（または
    `memorySearch.remote.apiKey`）を指定してください。埋め込みモデルとして **OpenAI、Gemini、Voyage、Mistral、Ollama、または local** をサポートしています。セットアップ詳細は [Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>
</AccordionGroup>

## ディスク上の配置場所

<AccordionGroup>
  <Accordion title="OpenClaw で使われるデータはすべてローカルに保存されますか？">
    いいえ。**OpenClaw の state はローカル**ですが、**外部サービスは送信した内容を見ます**。

    - **デフォルトではローカル:** sessions、memory files、config、workspace は Gateway host 上にあります
      （`~/.openclaw` + workspace directory）。
    - **必然的にリモート:** model providers（Anthropic/OpenAI など）へ送るメッセージは
      その API に送られ、chat platforms（WhatsApp/Telegram/Slack など）はメッセージデータを
      自分たちのサーバーに保存します。
    - **フットプリントは自分で制御可能:** local models を使えば prompts は自分のマシン上に留まりますが、
      channel traffic は依然としてその channel のサーバーを経由します。

    関連: [Agent workspace](/ja-JP/concepts/agent-workspace)、[Memory](/ja-JP/concepts/memory)。

  </Accordion>

  <Accordion title="OpenClaw はどこにデータを保存しますか？">
    すべては `$OPENCLAW_STATE_DIR`（デフォルト: `~/.openclaw`）配下にあります:

    | Path                                                            | 用途                                                               |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | メイン設定（JSON5）                                                |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | legacy OAuth import（初回使用時に auth profiles にコピー）         |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Auth profiles（OAuth、API keys、および任意の `keyRef`/`tokenRef`） |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef provider 用の任意の file-backed secret payload    |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | legacy 互換ファイル（静的 `api_key` entries は scrub 済み）        |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Provider state（例: `whatsapp/<accountId>/creds.json`）            |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | agent ごとの state（agentDir + sessions）                          |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 会話履歴と state（agent ごと）                                     |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Session metadata（agent ごと）                                     |

    旧 single-agent path: `~/.openclaw/agent/*`（`openclaw doctor` により移行）。

    **workspace**（AGENTS.md、memory files、skills など）は別であり、`agents.defaults.workspace`（デフォルト: `~/.openclaw/workspace`）で設定されます。

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md はどこに置くべきですか？">
    これらのファイルは `~/.openclaw` ではなく、**agent workspace** にあります。

    - **Workspace（agent ごと）**: `AGENTS.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`、
      `MEMORY.md`（`MEMORY.md` がない場合は legacy fallback の `memory.md`）、
      `memory/YYYY-MM-DD.md`、任意で `HEARTBEAT.md`。
    - **State dir（`~/.openclaw`）**: config、channel/provider state、auth profiles、sessions、logs、
      および共有 skills（`~/.openclaw/skills`）。

    デフォルト workspace は `~/.openclaw/workspace` で、以下により設定できます:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    再起動後に bot が「忘れる」場合は、Gateway が起動のたびに同じ
    workspace を使っているか確認してください（さらに remote mode では、使われるのは**gateway host 側の**
    workspace であり、ローカル laptop 側ではありません）。

    ヒント: 永続的な振る舞いや好みを持たせたいなら、chat history に頼るのではなく、
    **AGENTS.md または MEMORY.md に書くよう** bot に依頼してください。

    [Agent workspace](/ja-JP/concepts/agent-workspace) と [Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>

  <Accordion title="推奨バックアップ戦略">
    **agent workspace** を**private** な git repo に入れ、どこか private な場所
    （たとえば GitHub private）にバックアップしてください。これにより memory + AGENTS/SOUL/USER
    files が保存され、あとで assistant の「心」を復元できます。

    `~/.openclaw` 配下（credentials、sessions、tokens、encrypted secrets payloads）は
    commit しないでください。
    完全復元が必要なら、workspace と state directory の両方を
    別々にバックアップしてください（上の migration の質問を参照）。

    ドキュメント: [Agent workspace](/ja-JP/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="OpenClaw を完全にアンインストールするには？">
    専用ガイドを参照してください: [Uninstall](/ja-JP/install/uninstall)。
  </Accordion>

  <Accordion title="agents は workspace の外でも動けますか？">
    はい。workspace は**デフォルト cwd** と memory のアンカーであり、厳格な sandbox ではありません。
    相対パスは workspace 内で解決されますが、sandboxing が無効な限り、絶対パスは
    他の host の場所にもアクセスできます。分離が必要なら、
    [`agents.defaults.sandbox`](/ja-JP/gateway/sandboxing) または per-agent sandbox settings を使ってください。repo を
    デフォルト working directory にしたい場合は、その agent の
    `workspace` を repo root に向けてください。OpenClaw repo は単なるソースコードです。意図的にそこで作業させたいのでない限り、
    workspace は別に保ってください。

    例（repo をデフォルト cwd にする）:

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Remote mode では session store はどこにありますか？">
    Session state を所有するのは **gateway host** です。remote mode では、あなたが気にすべき session store はローカル laptop ではなくリモートマシン上にあります。[Session management](/ja-JP/concepts/session) を参照してください。
  </Accordion>
</AccordionGroup>

## 設定の基本

<AccordionGroup>
  <Accordion title="設定はどんな形式で、どこにありますか？">
    OpenClaw は `$OPENCLAW_CONFIG_PATH`（デフォルト: `~/.openclaw/openclaw.json`）から
    任意の **JSON5** config を読み込みます:

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    ファイルが存在しない場合は、安全寄りのデフォルト値（デフォルト workspace `~/.openclaw/workspace` を含む）を使います。

  </Accordion>

  <Accordion title='gateway.bind: "lan"（または "tailnet"）にしたら何も listen せず / UI が unauthorized と言います'>
    non-loopback bind には**有効な gateway auth path**が必要です。実際には次のいずれかです。

    - shared-secret auth: token または password
    - 正しく設定された non-loopback の identity-aware reverse proxy の背後での `gateway.auth.mode: "trusted-proxy"`

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    注意点:

    - `gateway.remote.token` / `.password` だけでは local gateway auth は有効になりません。
    - local call paths では、`gateway.auth.*` が未設定の場合に限り `gateway.remote.*` を fallback として使えます。
    - password auth には `gateway.auth.mode: "password"` と `gateway.auth.password`（または `OPENCLAW_GATEWAY_PASSWORD`）を設定してください。
    - `gateway.auth.token` / `gateway.auth.password` が SecretRef 経由で明示設定されていて解決できない場合、解決は fail closed します（remote fallback で隠れません）。
    - shared-secret の Control UI セットアップは、`connect.params.auth.token` または `connect.params.auth.password`（app/UI settings に保存）で認証します。Tailscale Serve や `trusted-proxy` のような identity-bearing モードは代わりに request headers を使います。shared secrets を URL に入れないでください。
    - `gateway.auth.mode: "trusted-proxy"` では、同一ホスト上の loopback reverse proxy は trusted-proxy auth を満たしません。trusted proxy は設定済みの non-loopback source である必要があります。

  </Accordion>

  <Accordion title="localhost でも token が必要になったのはなぜですか？">
    OpenClaw は loopback を含め、デフォルトで gateway auth を強制します。通常のデフォルト経路では token auth になり、明示的な auth path が設定されていない場合、gateway 起動時に token mode へ解決され、自動生成された token が `gateway.auth.token` に保存されるため、**local WS clients は認証が必要**です。これにより、他のローカルプロセスが Gateway を呼び出すのを防ぎます。

    別の auth path を好む場合は、password mode（または non-loopback identity-aware reverse proxies 用の `trusted-proxy`）を明示的に選べます。**本当に** open loopback にしたい場合は、config に `gateway.auth.mode: "none"` を明示設定してください。Doctor はいつでも token を生成できます: `openclaw doctor --generate-gateway-token`。

  </Accordion>

  <Accordion title="config を変えたあと再起動は必要ですか？">
    Gateway は config を監視しており、hot-reload をサポートします。

    - `gateway.reload.mode: "hybrid"`（デフォルト）: 安全な変更は hot-apply、重要なものは restart
    - `hot`、`restart`、`off` もサポートされています

  </Accordion>

  <Accordion title="CLI の面白い tagline を無効にするには？">
    config の `cli.banner.taglineMode` を設定します:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: tagline text を隠し、banner の title/version line は残します。
    - `default`: 毎回 `All your chats, one OpenClaw.` を使います。
    - `random`: 面白い/季節ごとの rotating taglines（デフォルト動作）。
    - banner 自体も消したい場合は env `OPENCLAW_HIDE_BANNER=1` を設定してください。

  </Accordion>

  <Accordion title="web search（と web fetch）はどう有効にしますか？">
    `web_fetch` は API key なしで動作します。`web_search` は選択した
    provider に依存します:

    - Brave、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Perplexity、Tavily のような API-backed providers では通常どおり API key の設定が必要です。
    - Ollama Web Search は key-free ですが、設定済みの Ollama host を使い、`ollama signin` が必要です。
    - DuckDuckGo は key-free ですが、非公式の HTML ベース統合です。
    - SearXNG は key-free/self-hosted です。`SEARXNG_BASE_URL` または `plugins.entries.searxng.config.webSearch.baseUrl` を設定してください。

    **推奨:** `openclaw configure --section web` を実行して provider を選択してください。
    環境変数による代替:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` または `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY`、`MINIMAX_CODING_API_KEY`、または `MINIMAX_API_KEY`
    - Perplexity: `PERPLEXITY_API_KEY` または `OPENROUTER_API_KEY`
    - SearXNG: `SEARXNG_BASE_URL`
    - Tavily: `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // 任意。auto-detect にするなら省略
            },
          },
        },
    }
    ```

    provider 固有の web-search config は現在 `plugins.entries.<plugin>.config.webSearch.*` 配下にあります。
    legacy の `tools.web.search.*` provider paths も互換性のため一時的には読み込まれますが、新しい config には使わないでください。
    Firecrawl の web-fetch fallback config は `plugins.entries.firecrawl.config.webFetch.*` 配下にあります。

    注意点:

    - allowlists を使っている場合は、`web_search`/`web_fetch`/`x_search` または `group:web` を追加してください。
    - `web_fetch` はデフォルトで有効です（明示的に無効化していない限り）。
    - `tools.web.fetch.provider` を省略した場合、OpenClaw は利用可能な credentials から、最初に準備済みの fetch fallback provider を自動検出します。現在の bundled provider は Firecrawl です。
    - daemons は `~/.openclaw/.env`（または service environment）から env vars を読み込みます。

    ドキュメント: [Web tools](/ja-JP/tools/web)。

  </Accordion>

  <Accordion title="config.apply で config が消えました。どう復旧し、どう防げますか？">
    `config.apply` は**設定全体**を置き換えます。partial object を送ると、ほかのものは
    すべて削除されます。

    復旧方法:

    - バックアップから復元する（git またはコピーした `~/.openclaw/openclaw.json`）。
    - バックアップがない場合は、`openclaw doctor` を再実行し、channels/models を再設定してください。
    - 想定外だった場合は、bug を報告し、最後に分かっていた config またはバックアップを添えてください。
    - ローカルの coding agent なら、ログや履歴から動く config を復元できることがよくあります。

    防止方法:

    - 小さな変更には `openclaw config set` を使う。
    - 対話的編集には `openclaw configure` を使う。
    - 正確な path や field shape に自信がないときは、先に `config.schema.lookup` を使う。浅い schema node と immediate child summaries が返るので drill-down できます。
    - partial RPC edits には `config.patch` を使い、`config.apply` は full-config replacement にのみ使ってください。
    - agent run から owner-only の `gateway` tool を使っている場合でも、`tools.exec.ask` / `tools.exec.security` への書き込みは引き続き拒否されます（同じ protected exec paths に正規化される legacy の `tools.bash.*` aliases を含む）。

    ドキュメント: [Config](/cli/config)、[Configure](/cli/configure)、[Doctor](/ja-JP/gateway/doctor)。

  </Accordion>

  <Accordion title="中央 Gateway と、デバイスをまたぐ専門 worker はどう構成しますか？">
    一般的なパターンは **1 つの Gateway**（例: Raspberry Pi）+ **nodes** + **agents** です。

    - **Gateway（中央）:** channels（Signal/WhatsApp）、routing、sessions を所有。
    - **Nodes（デバイス）:** Macs/iOS/Android が周辺機器として接続し、ローカル tools（`system.run`、`canvas`、`camera`）を公開。
    - **Agents（workers）:** 特殊な役割（例: 「Hetzner ops」「Personal data」）のための独立した頭脳/workspaces。
    - **Sub-agents:** 並列化したいときに、main agent から background work を spawn。
    - **TUI:** Gateway に接続して agents/sessions を切り替える。

    ドキュメント: [Nodes](/ja-JP/nodes)、[Remote access](/ja-JP/gateway/remote)、[Multi-Agent Routing](/ja-JP/concepts/multi-agent)、[Sub-agents](/ja-JP/tools/subagents)、[TUI](/web/tui)。

  </Accordion>

  <Accordion title="OpenClaw browser は headless で動かせますか？">
    はい。config option です:

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    デフォルトは `false`（headful）です。headless は一部サイトで anti-bot checks を誘発しやすいです。[Browser](/ja-JP/tools/browser) を参照してください。

    Headless でも **同じ Chromium engine** を使い、大半の automation（forms、clicks、scraping、logins）には対応します。主な違いは:

    - 可視ブラウザーウィンドウがない（視覚確認には screenshots を使う）。
    - 一部サイトでは headless automation により厳しい対応をします（CAPTCHAs、anti-bot）。
      たとえば X/Twitter は headless sessions をブロックすることがよくあります。

  </Accordion>

  <Accordion title="Brave を browser control に使うには？">
    `browser.executablePath` を Brave のバイナリ（または任意の Chromium-based browser）に設定し、Gateway を再起動してください。
    完全な config 例は [Browser](/ja-JP/tools/browser#use-brave-or-another-chromium-based-browser) を参照してください。
  </Accordion>
</AccordionGroup>

## Remote gateways と nodes

<AccordionGroup>
  <Accordion title="Telegram、gateway、nodes の間でコマンドはどう伝播しますか？">
    Telegram messages は **gateway** が処理します。gateway が agent を実行し、
    node tool が必要なときにだけ **Gateway WebSocket** 経由で nodes を呼び出します:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Nodes は受信 provider traffic を見ることはなく、node RPC calls だけを受け取ります。

  </Accordion>

  <Accordion title="Gateway がリモートでホストされている場合、agent はどうやって自分のコンピューターにアクセスできますか？">
    短い答え: **自分のコンピューターを node としてペアリングしてください**。Gateway は別ホストで動きますが、
    Gateway WebSocket 経由で、ローカルマシン上の `node.*` tools（screen、camera、system）を呼び出せます。

    一般的なセットアップ:

    1. 常時稼働ホスト（VPS/ホームサーバー）で Gateway を動かす。
    2. Gateway host と自分のコンピューターを同じ tailnet に入れる。
    3. Gateway WS に到達できることを確認する（tailnet bind または SSH tunnel）。
    4. ローカルで macOS app を開き、**Remote over SSH** mode（または直接 tailnet）
       で接続して、node として登録させる。
    5. Gateway 上で node を承認する:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    別個の TCP bridge は不要です。nodes は Gateway WebSocket 経由で接続します。

    セキュリティ上の注意: macOS node をペアリングすると、そのマシン上で `system.run` が可能になります。信頼できるデバイスだけをペアリングし、[Security](/ja-JP/gateway/security) を確認してください。

    ドキュメント: [Nodes](/ja-JP/nodes)、[Gateway protocol](/ja-JP/gateway/protocol)、[macOS remote mode](/ja-JP/platforms/mac/remote)、[Security](/ja-JP/gateway/security)。

  </Accordion>

  <Accordion title="Tailscale は接続できているのに返信がありません。どうすればよいですか？">
    基本を確認してください:

    - Gateway が動作中か: `openclaw gateway status`
    - Gateway health: `openclaw status`
    - Channel health: `openclaw channels status`

    その後、auth と routing を確認します:

    - Tailscale Serve を使っているなら、`gateway.auth.allowTailscale` が正しく設定されているか確認。
    - SSH tunnel 経由で接続しているなら、ローカルトンネルが生きていて正しいポートを向いているか確認。
    - allowlists（DM または group）に自分の account が含まれているか確認。

    ドキュメント: [Tailscale](/ja-JP/gateway/tailscale)、[Remote access](/ja-JP/gateway/remote)、[Channels](/ja-JP/channels)。

  </Accordion>

  <Accordion title="2 つの OpenClaw instance（local + VPS）同士で会話できますか？">
    はい。built-in の「bot-to-bot」bridge はありませんが、いくつかの
    信頼できる方法で接続できます。

    **最も簡単:** 両方の bot がアクセスできる通常の chat channel（Telegram/Slack/WhatsApp）を使います。
    Bot A に Bot B 宛てのメッセージを送らせ、その後 Bot B が通常どおり返信します。

    **CLI bridge（汎用）:** スクリプトから別の Gateway を
    `openclaw agent --message ... --deliver` で呼び出し、相手 bot が
    監視している chat を target にします。片方が remote VPS 上にある場合は、
    その remote Gateway を SSH/Tailscale 経由で指定してください（[Remote access](/ja-JP/gateway/remote) を参照）。

    例（target Gateway に到達できるマシンで実行）:

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    ヒント: 2 つの bot が無限ループしないようガードレールを入れてください（mention-only、
    channel allowlists、または「bot messages には返信しない」ルール）。

    ドキュメント: [Remote access](/ja-JP/gateway/remote)、[Agent CLI](/cli/agent)、[Agent send](/ja-JP/tools/agent-send)。

  </Accordion>

  <Accordion title="複数 agent のために VPS も複数必要ですか？">
    いいえ。1 つの Gateway で複数 agents をホストでき、それぞれ独自の workspace、model defaults、
    routing を持てます。これが通常のセットアップであり、agent ごとに VPS を立てるより
    はるかに安価で簡単です。

    複数の VPS が必要なのは、hard isolation（security boundaries）や、
    共有したくないほど大きく異なる config が必要な場合だけです。それ以外は、
    1 つの Gateway に複数 agents または sub-agents を使ってください。

  </Accordion>

  <Accordion title="VPS から SSH する代わりに、個人用 laptop で node を使う利点はありますか？">
    はい。nodes は remote Gateway から laptop に到達するための第一級の方法であり、
    shell access 以上のものを提供します。Gateway は macOS/Linux（Windows は WSL2）で動作し、
    軽量です（小さな VPS や Raspberry Pi クラスのマシンで十分、4 GB RAM あれば余裕があります）。そのため、
    常時稼働ホスト + laptop を node にする構成が一般的です。

    - **inbound SSH 不要。** Nodes は Gateway WebSocket へ outward 接続し、device pairing を使います。
    - **より安全な実行制御。** `system.run` はその laptop 上の node allowlists/approvals で制御されます。
    - **より多くの device tools。** Nodes は `system.run` に加えて `canvas`、`camera`、`screen` を公開します。
    - **ローカル browser automation。** Gateway は VPS に置きつつ、laptop 上の node host 経由でローカル Chrome を使ったり、host 上の Chrome に Chrome MCP 経由で接続できます。

    SSH は一時的な shell access には問題ありませんが、継続的な agent workflows や
    device automation には nodes の方が簡単です。

    ドキュメント: [Nodes](/ja-JP/nodes)、[Nodes CLI](/cli/nodes)、[Browser](/ja-JP/tools/browser)。

  </Accordion>

  <Accordion title="nodes は gateway service を動かしますか？">
    いいえ。意図的に isolated profiles を使うのでない限り、ホストごとに **1 つの gateway** だけを動かすべきです（[Multiple gateways](/ja-JP/gateway/multiple-gateways) を参照）。Nodes は gateway に接続する周辺機器です
    （iOS/Android nodes、または menubar app の macOS「node mode」）。headless node
    hosts と CLI 制御については [Node host CLI](/cli/node) を参照してください。

    `gateway`、`discovery`、`canvasHost` の変更には完全な再起動が必要です。

  </Accordion>

  <Accordion title="config を適用する API / RPC の方法はありますか？">
    はい。

    - `config.schema.lookup`: 書き込む前に、1 つの config subtree を shallow schema node、matched UI hint、immediate child summaries とともに確認
    - `config.get`: 現在の snapshot + hash を取得
    - `config.patch`: 安全な partial update（多くの RPC edits では推奨）
    - `config.apply`: validate したうえで full config を置き換え、その後 restart
    - owner-only の `gateway` runtime tool は引き続き `tools.exec.ask` / `tools.exec.security` の書き換えを拒否します。legacy の `tools.bash.*` aliases も同じ protected exec paths に正規化されます

  </Accordion>

  <Accordion title="初回 install 用の最小限で妥当な config">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    これで workspace が設定され、bot を起動できる人を制限できます。

  </Accordion>

  <Accordion title="VPS に Tailscale を設定して Mac から接続するには？">
    最小手順:

    1. **VPS に install + login**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Mac に install + login**
       - Tailscale app を使い、同じ tailnet にサインインします。
    3. **MagicDNS を有効化（推奨）**
       - Tailscale admin console で MagicDNS を有効化し、VPS に安定した名前を付けます。
    4. **tailnet hostname を使う**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    SSH なしで Control UI を使いたい場合は、VPS で Tailscale Serve を使ってください:

    ```bash
    openclaw gateway --tailscale serve
    ```

    これにより gateway は loopback に bind したまま、Tailscale 経由で HTTPS を公開します。[Tailscale](/ja-JP/gateway/tailscale) を参照してください。

  </Accordion>

  <Accordion title="Mac node を remote Gateway（Tailscale Serve）に接続するには？">
    Serve は **Gateway Control UI + WS** を公開します。nodes も同じ Gateway WS endpoint に接続します。

    推奨セットアップ:

    1. **VPS と Mac が同じ tailnet にあることを確認**します。
    2. **macOS app を Remote mode で使います**（SSH target は tailnet hostname でも可）。
       app が Gateway port をトンネルし、node として接続します。
    3. Gateway で **node を承認**します:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    ドキュメント: [Gateway protocol](/ja-JP/gateway/protocol)、[Discovery](/ja-JP/gateway/discovery)、[macOS remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="2 台目の laptop に install すべきですか？それとも node を追加するだけでよいですか？">
    2 台目の laptop 上で必要なのが **local tools**（screen/camera/exec）だけなら、
    **node** として追加してください。そうすれば Gateway を 1 つに保てて、config の重複も避けられます。local node tools は
    現在 macOS 専用ですが、今後ほかの OS にも拡張予定です。

    2 台目の Gateway を install するのは、**hard isolation** が必要な場合、または完全に独立した bot が 2 つ必要な場合だけです。

    ドキュメント: [Nodes](/ja-JP/nodes)、[Nodes CLI](/cli/nodes)、[Multiple gateways](/ja-JP/gateway/multiple-gateways)。

  </Accordion>
</AccordionGroup>

## Env vars と .env 読み込み

<AccordionGroup>
  <Accordion title="OpenClaw は environment variables をどう読み込みますか？">
    OpenClaw は parent process（shell、launchd/systemd、CI など）から env vars を受け取り、さらに次も読み込みます:

    - current working directory の `.env`
    - `~/.openclaw/.env`（別名 `$OPENCLAW_STATE_DIR/.env`）の global fallback `.env`

    どちらの `.env` ファイルも既存の env vars を上書きしません。

    config に inline env vars を定義することもできます（process env に存在しない場合のみ適用）:

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    完全な優先順位とソースについては [/environment](/ja-JP/help/environment) を参照してください。

  </Accordion>

  <Accordion title="Gateway を service 経由で起動したら env vars が消えました。どうすればよいですか？">
    よくある修正は 2 つあります。

    1. 足りないキーを `~/.openclaw/.env` に入れる。そうすれば service が shell env を引き継がなくても読み込まれます。
    2. shell import を有効化する（opt-in の利便機能）:

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    これにより login shell を実行し、不足している想定キーだけを import します（上書きはしません）。対応する env vars:
    `OPENCLAW_LOAD_SHELL_ENV=1`、`OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`。

  </Accordion>

  <Accordion title='COPILOT_GITHUB_TOKEN を設定したのに、models status に "Shell env: off." と表示されます'>
    `openclaw models status` は **shell env import** が有効かどうかを報告します。`Shell env: off`
    は env vars が欠けているという意味ではなく、OpenClaw が
    login shell を自動読み込みしないという意味です。

    Gateway を service（launchd/systemd）として実行している場合、shell
    environment を引き継ぎません。次のいずれかで修正してください:

    1. token を `~/.openclaw/.env` に入れる:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. または shell import を有効化する（`env.shellEnv.enabled: true`）。
    3. または config の `env` block に追加する（足りない場合のみ適用）。

    その後、gateway を再起動して再確認してください:

    ```bash
    openclaw models status
    ```

    Copilot tokens は `COPILOT_GITHUB_TOKEN`（`GH_TOKEN` / `GITHUB_TOKEN` も可）から読み取られます。
    [/concepts/model-providers](/ja-JP/concepts/model-providers) と [/environment](/ja-JP/help/environment) を参照してください。

  </Accordion>
</AccordionGroup>

## Sessions と複数 chat

<AccordionGroup>
  <Accordion title="新しい会話を始めるには？">
    `/new` または `/reset` を単独メッセージとして送信してください。[Session management](/ja-JP/concepts/session) を参照してください。
  </Accordion>

  <Accordion title="/new を送らなければ sessions は自動でリセットされますか？">
    Sessions は `session.idleMinutes` 経過後に失効できますが、これは**デフォルトでは無効**です（デフォルト **0**）。
    正の値を設定すると idle expiry が有効になります。有効時は、idle 期間の**次の**
    メッセージでその chat key の新しい session id が開始されます。
    これは transcripts を削除するのではなく、新しい session を始めるだけです。

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="OpenClaw instances のチーム（CEO 1 人と多数の agents）を作れますか？">
    はい。**multi-agent routing** と **sub-agents** によって可能です。1 つの coordinator
    agent と、独自の workspaces と models を持つ複数の worker agents を作れます。

    ただし、これは**楽しい実験**として捉えるのが適切です。トークン消費が大きく、
    多くの場合は 1 つの bot を別々の sessions で使うより非効率です。私たちが一般に想定しているのは、
    1 つの bot と会話し、並列作業には異なる sessions を使う形です。その
    bot は必要に応じて sub-agents も spawn できます。

    ドキュメント: [Multi-agent routing](/ja-JP/concepts/multi-agent)、[Sub-agents](/ja-JP/tools/subagents)、[Agents CLI](/cli/agents)。

  </Accordion>

  <Accordion title="タスクの途中で context が切り詰められたのはなぜですか？防ぐには？">
    Session context は model の window に制限されます。長い chat、大きな tool outputs、多数の
    files により compaction や truncation が発生することがあります。

    役立つこと:

    - 現在の状態を要約して file に書くよう bot に依頼する。
    - 長いタスクの前に `/compact` を使い、話題を切り替えるときは `/new` を使う。
    - 重要な context は workspace に置き、それを bot に読み返させる。
    - 長い作業や並列作業には sub-agents を使い、main chat を小さく保つ。
    - これが頻繁に起こるなら、より大きな context window を持つ model を選ぶ。

  </Accordion>

  <Accordion title="OpenClaw を完全にリセットしつつ install は残すには？">
    reset コマンドを使います:

    ```bash
    openclaw reset
    ```

    非対話の full reset:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    その後、セットアップをやり直します:

    ```bash
    openclaw onboard --install-daemon
    ```

    注意点:

    - Onboarding は既存 config を見つけた場合、**Reset** も提案します。[Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。
    - profiles（`--profile` / `OPENCLAW_PROFILE`）を使っていた場合は、それぞれの state dir を reset してください（デフォルトは `~/.openclaw-<profile>`）。
    - Dev reset: `openclaw gateway --dev --reset`（dev 専用。dev の config + credentials + sessions + workspace を消去）。

  </Accordion>

  <Accordion title='"context too large" エラーが出ます。どうやって reset または compact しますか？'>
    次のいずれかを使ってください:

    - **Compact**（会話は保持しつつ古い turn を要約）:

      ```
      /compact
      ```

      または、要約を誘導するために `/compact <instructions>`。

    - **Reset**（同じ chat key で新しい session ID）:

      ```
      /new
      /reset
      ```

    何度も起きる場合:

    - **session pruning**（`agents.defaults.contextPruning`）を有効化または調整して、古い tool output を削る。
    - より大きな context window を持つ model を使う。

    ドキュメント: [Compaction](/ja-JP/concepts/compaction)、[Session pruning](/ja-JP/concepts/session-pruning)、[Session management](/ja-JP/concepts/session)。

  </Accordion>

  <Accordion title='なぜ "LLM request rejected: messages.content.tool_use.input field required" と出るのですか？'>
    これは provider validation error です。model が、必須の
    `input` を持たない `tool_use` block を出力しました。多くの場合、session history が古いか破損しています
    （長い thread の後や tool/schema change の後によくあります）。

    修正: `/new`（単独メッセージ）で新しい session を開始してください。

  </Accordion>

  <Accordion title="30 分ごとに heartbeat messages が来るのはなぜですか？">
    Heartbeats はデフォルトで **30m** ごと（OAuth auth 使用時は **1h** ごと）に実行されます。調整または無効化するには:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // または "0m" で無効化
          },
        },
      },
    }
    ```

    `HEARTBEAT.md` が存在しても実質的に空（空行と `# Heading` のような markdown
    headers のみ）の場合、OpenClaw は API calls を節約するため heartbeat run をスキップします。
    ファイルがない場合、heartbeat 自体は実行され、何をするかは model が決めます。

    per-agent overrides には `agents.list[].heartbeat` を使います。ドキュメント: [Heartbeat](/ja-JP/gateway/heartbeat)。

  </Accordion>

  <Accordion title='WhatsApp group に「bot account」を追加する必要はありますか？'>
    いいえ。OpenClaw は**自分の account**上で動作するため、あなたがその group にいれば OpenClaw も見えます。
    デフォルトでは、送信者を許可するまで group replies はブロックされます（`groupPolicy: "allowlist"`）。

    group replies をトリガーできるのを**自分だけ**にしたい場合:

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="WhatsApp group の JID を取得するには？">
    Option 1（最速）: ログを追い、その group に test message を送ります:

    ```bash
    openclaw logs --follow --json
    ```

    `@g.us` で終わる `chatId`（または `from`）を探してください。例:
    `1234567890-1234567890@g.us`。

    Option 2（すでに設定/allowlist 済みの場合）: config から groups を一覧表示:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    ドキュメント: [WhatsApp](/ja-JP/channels/whatsapp)、[Directory](/cli/directory)、[Logs](/cli/logs)。

  </Accordion>

  <Accordion title="OpenClaw が group で返信しないのはなぜですか？">
    よくある原因は 2 つあります。

    - mention gating が有効（デフォルト）。bot を @mention する必要があります（または `mentionPatterns` に一致させる）。
    - `channels.whatsapp.groups` を `"*"` なしで設定しており、その group が allowlist に入っていない。

    [Groups](/ja-JP/channels/groups) と [Group messages](/ja-JP/channels/group-messages) を参照してください。

  </Accordion>

  <Accordion title="groups/threads は DMs と context を共有しますか？">
    direct chats はデフォルトで main session に集約されます。groups/channels には独自の session keys があり、Telegram topics / Discord threads も別 sessions です。[Groups](/ja-JP/channels/groups) と [Group messages](/ja-JP/channels/group-messages) を参照してください。
  </Accordion>

  <Accordion title="workspaces と agents はいくつ作れますか？">
    ハードな上限はありません。数十個（あるいは数百個）でも問題ありませんが、次に注意してください。

    - **ディスク増加:** sessions + transcripts は `~/.openclaw/agents/<agentId>/sessions/` 配下にあります。
    - **トークンコスト:** agents が増えるほど同時 model usage も増えます。
    - **運用負荷:** agent ごとの auth profiles、workspaces、channel routing。

    ヒント:

    - agent ごとに **1 つの active workspace** を保つ（`agents.defaults.workspace`）。
    - ディスクが増えたら古い sessions を prune する（JSONL または store entries を削除）。
    - `openclaw doctor` を使うと stray workspaces や profile mismatch を見つけられます。

  </Accordion>

  <Accordion title="複数の bots や chats（Slack など）を同時に動かせますか？どう設定すべきですか？">
    はい。**Multi-Agent Routing** を使って、複数の独立した agents を動かし、
    受信 messages を channel/account/peer ごとに routing してください。Slack は channel としてサポートされ、
    特定の agents に bind できます。

    Browser access は強力ですが、「人間ができることをすべてできる」わけではありません。anti-bot、CAPTCHAs、MFA は
    automation を依然として妨げます。最も信頼性の高い browser control には、host 上の local Chrome MCP を使うか、
    実際に browser を動かしているマシン上で CDP を使ってください。

    ベストプラクティスのセットアップ:

    - 常時稼働 Gateway host（VPS/Mac mini）。
    - 役割ごとに 1 つの agent（bindings）。
    - それら agents に bind された Slack channels。
    - 必要に応じて Chrome MCP または node 経由の local browser。

    ドキュメント: [Multi-Agent Routing](/ja-JP/concepts/multi-agent)、[Slack](/ja-JP/channels/slack)、
    [Browser](/ja-JP/tools/browser)、[Nodes](/ja-JP/nodes)。

  </Accordion>
</AccordionGroup>

## Models: defaults、selection、aliases、switching

<AccordionGroup>
  <Accordion title='「default model」とは何ですか？'>
    OpenClaw の default model は、次に設定したものです:

    ```
    agents.defaults.model.primary
    ```

    Models は `provider/model` 形式で参照します（例: `openai/gpt-5.4`）。provider を省略すると、OpenClaw はまず alias を試し、次にその正確な model id に対して一意に設定済み provider があればそれに一致させ、それでもなければ非推奨の互換経路として設定済み default provider にフォールバックします。その provider が設定済み default model をもはや公開していない場合、古くなった removed-provider default を表に出す代わりに、最初の設定済み provider/model にフォールバックします。それでも、`provider/model` を**明示的に**設定するべきです。

  </Accordion>

  <Accordion title="おすすめの model は？">
    **推奨デフォルト:** 利用中の provider stack で使える、最も強力な最新世代 model を使ってください。
    **tool-enabled または untrusted-input の agents:** コストより model の強さを優先してください。
    **日常的/低リスクの chat:** 安価な fallback models を使い、agent の役割ごとに routing してください。

    MiniMax には専用ドキュメントがあります: [MiniMax](/ja-JP/providers/minimax) と
    [Local models](/ja-JP/gateway/local-models)。

    目安: 高リスクな作業には**払える範囲で最高の model**を使い、日常的な chat や要約には
    より安価な model を使ってください。agent ごとに models を routing でき、sub-agents を使って
    長いタスクを並列化できます（各 sub-agent はトークンを消費します）。[Models](/ja-JP/concepts/models) と
    [Sub-agents](/ja-JP/tools/subagents) を参照してください。

    強い警告: 弱いモデルや量子化が強すぎるモデルは、prompt
    injection や危険な挙動に対して脆弱です。[Security](/ja-JP/gateway/security) を参照してください。

    詳細: [Models](/ja-JP/concepts/models)。

  </Accordion>

  <Accordion title="config を消さずに models を切り替えるには？">
    **model commands** を使うか、**model** fields だけを編集してください。full config replace は避けてください。

    安全な方法:

    - chat で `/model`（手軽、session ごと）
    - `openclaw models set ...`（model config だけを更新）
    - `openclaw configure --section model`（対話式）
    - `~/.openclaw/openclaw.json` の `agents.defaults.model` を編集

    全設定を置き換える意図がない限り、partial object で `config.apply` を使わないでください。
    RPC edits では、先に `config.schema.lookup` で確認し、`config.patch` を優先してください。lookup payload には normalized path、浅い schema docs/constraints、immediate child summaries が含まれるので、
    partial updates に使えます。
    上書きしてしまった場合は、バックアップから復元するか、`openclaw doctor` を再実行して修復してください。

    ドキュメント: [Models](/ja-JP/concepts/models)、[Configure](/cli/configure)、[Config](/cli/config)、[Doctor](/ja-JP/gateway/doctor)。

  </Accordion>

  <Accordion title="self-hosted models（llama.cpp、vLLM、Ollama）は使えますか？">
    はい。local models には Ollama が最も簡単です。

    最も簡単なセットアップ:

    1. `https://ollama.com/download` から Ollama をインストール
    2. `ollama pull glm-4.7-flash` のような local model を pull
    3. cloud models も使いたい場合は `ollama signin` を実行
    4. `openclaw onboard` を実行して `Ollama` を選択
    5. `Local` または `Cloud + Local` を選択

    注意点:

    - `Cloud + Local` では cloud models と local Ollama models の両方が使える
    - `kimi-k2.5:cloud` のような cloud models はローカル pull 不要
    - 手動切り替えには `openclaw models list` と `openclaw models set ollama/<model>` を使う

    セキュリティ上の注意: 小さなモデルや強く量子化されたモデルは prompt
    injection に対して脆弱です。tools を使える bot には**大きな models**を強く推奨します。
    それでも小さな models を使いたい場合は、sandboxing と厳格な tool allowlists を有効にしてください。

    ドキュメント: [Ollama](/ja-JP/providers/ollama)、[Local models](/ja-JP/gateway/local-models)、
    [Model providers](/ja-JP/concepts/model-providers)、[Security](/ja-JP/gateway/security)、
    [Sandboxing](/ja-JP/gateway/sandboxing)。

  </Accordion>

  <Accordion title="OpenClaw、Flawd、Krill ではどの models を使っていますか？">
    - これらのデプロイは異なることがあり、時間とともに変わる可能性があります。固定の provider 推奨はありません。
    - 各 gateway の現在の