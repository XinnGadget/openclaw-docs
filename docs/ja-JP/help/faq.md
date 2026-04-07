---
read_when:
    - 一般的なセットアップ、インストール、オンボーディング、またはランタイムのサポート質問に回答している
    - より深いデバッグの前に、ユーザーから報告された問題をトリアージしている
summary: OpenClawのセットアップ、設定、使用方法に関するよくある質問
title: FAQ
x-i18n:
    generated_at: "2026-04-07T04:47:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: bddcde55cf4bcec4913aadab4c665b235538104010e445e4c99915a1672b1148
    source_path: help/faq.md
    workflow: 15
---

# FAQ

実際のセットアップ（ローカル開発、VPS、マルチエージェント、OAuth/API keys、モデルフェイルオーバー）向けの簡潔な回答と、より深いトラブルシューティング。ランタイム診断については [Troubleshooting](/ja-JP/gateway/troubleshooting) を参照してください。完全な設定リファレンスについては [Configuration](/ja-JP/gateway/configuration) を参照してください。

## 何か壊れているときの最初の60秒

1. **クイックステータス（最初の確認）**

   ```bash
   openclaw status
   ```

   高速なローカル要約: OS + 更新状況、gateway/serviceの到達可能性、agents/sessions、provider設定 + ランタイムの問題（Gatewayに到達できる場合）。

2. **貼り付け可能なレポート（安全に共有可能）**

   ```bash
   openclaw status --all
   ```

   読み取り専用の診断とログ末尾表示（トークンは伏せ字化されます）。

3. **デーモン + ポート状態**

   ```bash
   openclaw gateway status
   ```

   supervisorランタイムとRPC到達可能性、probe対象URL、そしてserviceが使用した可能性が高い設定を表示します。

4. **詳細probe**

   ```bash
   openclaw status --deep
   ```

   ライブのGatewayヘルスprobeを実行します。サポートされている場合はチャネルprobeも含まれます
   （到達可能なGatewayが必要です）。[Health](/ja-JP/gateway/health) を参照してください。

5. **最新ログの末尾を追う**

   ```bash
   openclaw logs --follow
   ```

   RPCが停止している場合は、代わりに次を使ってください:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   ファイルログはserviceログとは別です。[Logging](/ja-JP/logging) と [Troubleshooting](/ja-JP/gateway/troubleshooting) を参照してください。

6. **Doctorを実行する（修復）**

   ```bash
   openclaw doctor
   ```

   config/stateを修復または移行し、ヘルスチェックを実行します。[Doctor](/ja-JP/gateway/doctor) を参照してください。

7. **Gatewayスナップショット**

   ```bash
   openclaw health --json
   openclaw health --verbose   # エラー時に対象URL + configパスを表示
   ```

   実行中のGatewayに完全なスナップショットを問い合わせます（WSのみ）。[Health](/ja-JP/gateway/health) を参照してください。

## クイックスタートと初回セットアップ

<AccordionGroup>
  <Accordion title="行き詰まりました。最速で抜け出す方法は？">
    **あなたのマシンを見られる**ローカルAI agentを使ってください。これはDiscordで尋ねるよりはるかに効果的です。多くの「行き詰まった」ケースは、リモートの支援者が調べられない**ローカルのconfigや環境の問題**だからです。

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    これらのツールは、リポジトリを読み、コマンドを実行し、ログを調べ、マシンレベルのセットアップ（PATH、services、権限、authファイル）の修正を手伝えます。ハッカブルな（git）インストールで**完全なソースチェックアウト**を渡してください:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    これにより、OpenClawが**git checkoutから**インストールされるため、agentはコード + ドキュメントを読み、あなたが実行している正確なバージョンに基づいて推論できます。あとで `--install-method git` なしでインストーラーを再実行すれば、いつでもstableに戻せます。

    ヒント: agentには、必要なコマンドだけを段階的に実行するよう、修正の**計画と監督**を頼んでください。そうすると変更が小さくなり、監査しやすくなります。

    本当のバグや修正を見つけたら、GitHub issueを登録するかPRを送ってください:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    まずは次のコマンドから始めてください（助けを求めるときは出力を共有してください）:

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    これらが行うこと:

    - `openclaw status`: gateway/agentの健全性 + 基本設定のクイックスナップショット。
    - `openclaw models status`: provider auth + modelの可用性を確認します。
    - `openclaw doctor`: よくあるconfig/stateの問題を検証して修復します。

    その他の便利なCLI確認: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`。

    クイックデバッグループ: [何か壊れているときの最初の60秒](#何か壊れているときの最初の60秒)。
    インストールドキュメント: [Install](/ja-JP/install), [Installer flags](/ja-JP/install/installer), [Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="Heartbeatがスキップされ続けます。スキップ理由は何を意味しますか？">
    一般的なheartbeatのスキップ理由:

    - `quiet-hours`: 設定されたactive-hoursの時間帯外
    - `empty-heartbeat-file`: `HEARTBEAT.md` は存在するが、空白またはヘッダーだけのひな形しか含まれていない
    - `no-tasks-due`: `HEARTBEAT.md` のタスクモードが有効だが、どのタスク間隔もまだ到来していない
    - `alerts-disabled`: heartbeatの可視性がすべて無効（`showOk`, `showAlerts`, `useIndicator` がすべてオフ）

    タスクモードでは、到来時刻のタイムスタンプは実際のheartbeat実行が
    完了したあとにだけ進められます。スキップされた実行はタスク完了として扱われません。

    ドキュメント: [Heartbeat](/ja-JP/gateway/heartbeat), [Automation & Tasks](/ja-JP/automation)。

  </Accordion>

  <Accordion title="OpenClawをインストールしてセットアップする推奨方法">
    このリポジトリでは、ソースから実行し、オンボーディングを使うことを推奨しています:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    ウィザードはUIアセットも自動でビルドできます。オンボーディング後は、通常 **18789** 番ポートでGatewayを実行します。

    ソースから（コントリビューター/開発者向け）:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # 初回実行時にUI依存関係を自動インストール
    openclaw onboard
    ```

    まだグローバルインストールがない場合は、`pnpm openclaw onboard` で実行してください。

  </Accordion>

  <Accordion title="オンボーディング後にダッシュボードを開くには？">
    ウィザードはオンボーディング直後に、クリーンな（トークンを含まない）ダッシュボードURLでブラウザを開き、サマリーにもリンクを表示します。そのタブを開いたままにしてください。起動しなかった場合は、表示されたURLを同じマシン上でコピー＆ペーストしてください。
  </Accordion>

  <Accordion title="localhostでのダッシュボード認証とリモートでのダッシュボード認証はどう違いますか？">
    **Localhost（同じマシン）:**

    - `http://127.0.0.1:18789/` を開きます。
    - 共有シークレット認証を求められたら、設定済みのトークンまたはパスワードをControl UI settingsに貼り付けます。
    - トークンの取得元: `gateway.auth.token`（または `OPENCLAW_GATEWAY_TOKEN`）。
    - パスワードの取得元: `gateway.auth.password`（または `OPENCLAW_GATEWAY_PASSWORD`）。
    - 共有シークレットがまだ設定されていない場合は、`openclaw doctor --generate-gateway-token` でトークンを生成します。

    **localhostではない場合:**

    - **Tailscale Serve**（推奨）: bind loopbackのままにし、`openclaw gateway --tailscale serve` を実行して、`https://<magicdns>/` を開きます。`gateway.auth.allowTailscale` が `true` なら、identity headersがControl UI/WebSocket authを満たします（共有シークレットの貼り付け不要。gateway hostを信頼している前提です）。ただしHTTP APIsには、private-ingressの `none` または trusted-proxy HTTP auth を意図的に使わない限り、依然として共有シークレット認証が必要です。
      同一クライアントからの誤ったServe認証の同時試行は、failed-auth limiterが記録する前に直列化されるため、2回目の誤った再試行で既に `retry later` が表示されることがあります。
    - **Tailnet bind**: `openclaw gateway --bind tailnet --token "<token>"` を実行するか（またはpassword authを設定して）、`http://<tailscale-ip>:18789/` を開き、ダッシュボードsettingsに一致する共有シークレットを貼り付けます。
    - **Identity-aware reverse proxy**: Gatewayを非loopbackのtrusted proxyの背後に置き、`gateway.auth.mode: "trusted-proxy"` を設定し、そのあとproxy URLを開きます。
    - **SSH tunnel**: `ssh -N -L 18789:127.0.0.1:18789 user@host` のあとで `http://127.0.0.1:18789/` を開きます。トンネル経由でも共有シークレット認証は有効なので、求められたら設定済みのトークンまたはパスワードを貼り付けてください。

    bindモードと認証の詳細は [Dashboard](/web/dashboard) と [Web surfaces](/web) を参照してください。

  </Accordion>

  <Accordion title="チャット承認にexec approval configが2つあるのはなぜですか？">
    それぞれ別のレイヤーを制御しています:

    - `approvals.exec`: approval promptをチャット宛先へ転送する
    - `channels.<channel>.execApprovals`: そのチャネルをexec approvalsのネイティブapproval clientとして機能させる

    hostのexec policy自体が、依然として本当のapproval gateです。チャット設定は、approval
    promptをどこに表示するか、および人がどのように応答できるかだけを制御します。

    ほとんどのセットアップでは、**両方は不要**です:

    - チャットがすでにcommandsとrepliesをサポートしている場合、同じチャット内の `/approve` は共有パス経由で動作します。
    - サポートされるネイティブチャネルが承認者を安全に推定できる場合、OpenClawは現在、`channels.<channel>.execApprovals.enabled` が未設定または `"auto"` のときに、DM優先のネイティブ承認を自動で有効化します。
    - ネイティブapproval cards/buttonsが利用可能な場合、そのネイティブUIが主要経路になります。エージェントは、tool resultがチャット承認が使えない、または手動承認だけが唯一の経路だと示す場合にのみ、手動の `/approve` コマンドを含めるべきです。
    - promptも他のチャットや明示的なops roomへ転送する必要がある場合だけ、`approvals.exec` を使ってください。
    - 承認promptを元のroom/topicにも投稿したい場合だけ、`channels.<channel>.execApprovals.target: "channel"` または `"both"` を使ってください。
    - plugin approvalsはさらに別です。デフォルトでは同じチャット内の `/approve` を使い、必要に応じて `approvals.plugin` 転送を使います。ネイティブplugin approval handlingを上に重ねて維持するのは一部のネイティブチャネルだけです。

    要するに、転送はルーティングのため、ネイティブclient configはより豊かなチャネル固有UXのためです。
    [Exec Approvals](/ja-JP/tools/exec-approvals) を参照してください。

  </Accordion>

  <Accordion title="必要なランタイムは何ですか？">
    Node **>= 22** が必要です。`pnpm` を推奨します。BunはGatewayには**推奨されません**。
  </Accordion>

  <Accordion title="Raspberry Piで動きますか？">
    はい。Gatewayは軽量です。ドキュメントには、個人利用なら **512MB-1GB RAM**、**1 core**、約 **500MB**
    のディスクで十分とあり、**Raspberry Pi 4でも動作する**と記載されています。

    さらに余裕が欲しい場合（ログ、メディア、他のservices）、**2GBを推奨**しますが、
    これは厳密な最小条件ではありません。

    ヒント: 小型のPi/VPSでGatewayをホストし、ノートPC/スマートフォンの
    **nodes** をペアリングして、ローカルscreen/camera/canvasやコマンド実行に使えます。[Nodes](/ja-JP/nodes) を参照してください。

  </Accordion>

  <Accordion title="Raspberry Piへのインストールのコツはありますか？">
    短く言うと、動作はしますが、粗い部分はあると考えてください。

    - **64-bit** OSを使い、Node >= 22 を維持してください。
    - ログ確認や素早い更新ができるよう、**ハッカブルな（git）インストール**を推奨します。
    - channels/Skillsなしで始めて、ひとつずつ追加してください。
    - 奇妙なバイナリ問題にぶつかった場合、たいていは**ARM互換性**の問題です。

    ドキュメント: [Linux](/ja-JP/platforms/linux), [Install](/ja-JP/install)。

  </Accordion>

  <Accordion title="wake up my friend で止まります / オンボーディングが進みません。どうすればよいですか？">
    その画面はGatewayに到達でき、認証されていることに依存します。TUIも初回hatch時に
    「Wake up, my friend!」を自動送信します。その行が表示されているのに**返信がなく**
    tokensが0のままなら、agentは一度も実行されていません。

    1. Gatewayを再起動してください:

    ```bash
    openclaw gateway restart
    ```

    2. ステータス + authを確認してください:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. それでも止まる場合は、次を実行してください:

    ```bash
    openclaw doctor
    ```

    Gatewayがリモートの場合、tunnel/Tailscale接続が有効で、UIが
    正しいGatewayを指していることを確認してください。[Remote access](/ja-JP/gateway/remote) を参照してください。

  </Accordion>

  <Accordion title="オンボーディングをやり直さずにセットアップを新しいマシン（Mac mini）へ移行できますか？">
    はい。**state directory** と **workspace** をコピーし、そのあと一度Doctorを実行してください。これにより
    **両方**の場所をコピーする限り、botを「まったく同じ状態」（memory、session history、auth、channel
    state）で維持できます:

    1. 新しいマシンにOpenClawをインストールします。
    2. 古いマシンから `$OPENCLAW_STATE_DIR`（デフォルト: `~/.openclaw`）をコピーします。
    3. workspace（デフォルト: `~/.openclaw/workspace`）をコピーします。
    4. `openclaw doctor` を実行してGateway serviceを再起動します。

    これでconfig、auth profiles、WhatsApp creds、sessions、memoryが保持されます。
    remote modeでは、gateway hostがsession storeとworkspaceを所有することに注意してください。

    **重要:** workspaceだけをGitHubにcommit/pushしている場合、バックアップしているのは
    **memory + bootstrap files** であって、**session historyやauthではありません**。それらは
    `~/.openclaw/` 配下にあります（例: `~/.openclaw/agents/<agentId>/sessions/`）。

    関連: [Migrating](/ja-JP/install/migrating), [ディスク上の場所](#ディスク上の場所),
    [Agent workspace](/ja-JP/concepts/agent-workspace), [Doctor](/ja-JP/gateway/doctor),
    [Remote mode](/ja-JP/gateway/remote)。

  </Accordion>

  <Accordion title="最新バージョンで何が新しいかはどこで見られますか？">
    GitHub changelogを確認してください:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    最新のエントリーは先頭にあります。先頭セクションが **Unreleased** の場合、
    次の日付付きセクションが最新の出荷バージョンです。エントリーは **Highlights**, **Changes**, **Fixes**
    （必要に応じてdocs/other sectionsも）でグループ化されています。

  </Accordion>

  <Accordion title="docs.openclaw.ai にアクセスできません（SSL error）">
    一部のComcast/Xfinity接続では、Xfinity
    Advanced Securityによって `docs.openclaw.ai` が誤ってブロックされます。無効化するか、`docs.openclaw.ai` を許可リストに追加して再試行してください。
    解除の助けとして、こちらから報告してください: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status)。

    それでもサイトに到達できない場合、docsはGitHubにもミラーされています:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="stableとbetaの違い">
    **Stable** と **beta** は、別のコードラインではなく **npm dist-tags** です:

    - `latest` = stable
    - `beta` = テスト向けの早期ビルド

    通常、stableリリースはまず **beta** に入り、その後明示的な
    promotionステップで同じバージョンが `latest` に移されます。maintainersは
    必要に応じて直接 `latest` に公開することもできます。そのため、promotion後はbetaとstableが
    **同じバージョン** を指すことがあります。

    変更点を確認する:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    インストール用ワンライナーとbetaとdevの違いについては、下のaccordionを参照してください。

  </Accordion>

  <Accordion title="beta版はどうインストールしますか？ betaとdevの違いは何ですか？">
    **Beta** はnpm dist-tagの `beta` です（promotion後は `latest` と一致する場合があります）。
    **Dev** は `main` の移動する先頭（git）で、公開される場合はnpm dist-tag `dev` を使います。

    ワンライナー（macOS/Linux）:

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windowsインストーラー（PowerShell）:
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    詳細: [Development channels](/ja-JP/install/development-channels) と [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="最新のものを試すには？">
    2つの方法があります:

    1. **Devチャネル（git checkout）:**

    ```bash
    openclaw update --channel dev
    ```

    これにより `main` ブランチへ切り替わり、ソースから更新されます。

    2. **ハッカブルインストール（インストーラーサイトから）:**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    これでローカルrepoが手に入り、編集したあとgit経由で更新できます。

    手動でクリーンなcloneを使いたい場合は、次を実行してください:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    ドキュメント: [Update](/cli/update), [Development channels](/ja-JP/install/development-channels),
    [Install](/ja-JP/install)。

  </Accordion>

  <Accordion title="インストールとオンボーディングには普通どれくらいかかりますか？">
    おおよその目安:

    - **Install:** 2-5分
    - **Onboarding:** 設定するchannels/modelsの数にもよりますが5-15分

    止まった場合は、[Installer stuck](#クイックスタートと初回セットアップ)
    と [行き詰まりました](#クイックスタートと初回セットアップ) の高速デバッグループを使ってください。

  </Accordion>

  <Accordion title="Installerが止まります。もっと詳細な情報を出すには？">
    **verbose output** を付けてinstallerを再実行してください:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    verbose付きbeta install:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    ハッカブルな（git）インストールの場合:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Windows（PowerShell）相当:

    ```powershell
    # install.ps1 にはまだ専用の -Verbose フラグはありません。
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    追加オプション: [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="Windowsインストールで git not found または openclaw not recognized と表示される">
    Windowsでよくある2つの問題があります:

    **1) npm error spawn git / git not found**

    - **Git for Windows** をインストールし、`git` がPATHにあることを確認してください。
    - PowerShellを閉じて再度開き、installerを再実行してください。

    **2) インストール後に openclaw is not recognized と表示される**

    - npm global bin folder がPATHに入っていません。
    - パスを確認してください:

      ```powershell
      npm config get prefix
      ```

    - そのディレクトリをユーザーPATHに追加してください（Windowsでは `\bin` 接尾辞は不要です。多くのシステムでは `%AppData%\npm` です）。
    - PATH更新後にPowerShellを閉じて再度開いてください。

    最もスムーズなWindowsセットアップを望むなら、ネイティブWindowsではなく **WSL2** を使ってください。
    ドキュメント: [Windows](/ja-JP/platforms/windows)。

  </Accordion>

  <Accordion title="Windowsのexec出力で中国語が文字化けします。どうすればよいですか？">
    これは通常、ネイティブWindows shellでのconsole code page不一致です。

    症状:

    - `system.run`/`exec` の出力で中国語が文字化けする
    - 同じコマンドが別のterminal profileでは正常に見える

    PowerShellでのクイック回避策:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    その後、Gatewayを再起動してコマンドを再試行してください:

    ```powershell
    openclaw gateway restart
    ```

    最新のOpenClawでも再現する場合は、次で追跡/報告してください:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="docsを見ても答えが見つかりません。よりよい答えを得るには？">
    **ハッカブルな（git）インストール**を使って、完全なソースとdocsをローカルに置き、その
    フォルダーからbot（またはClaude/Codex）に質問してください。そうすればrepoを読み、正確に答えられます。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    詳細: [Install](/ja-JP/install) と [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="OpenClawをLinuxにインストールするには？">
    短い答え: Linuxガイドに従い、そのあとオンボーディングを実行してください。

    - Linuxのクイックパス + service install: [Linux](/ja-JP/platforms/linux)。
    - 完全な手順: [はじめに](/ja-JP/start/getting-started)。
    - インストーラー + 更新: [Install & updates](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="OpenClawをVPSにインストールするには？">
    どのLinux VPSでも動作します。サーバーにインストールし、そのあとSSH/Tailscale経由でGatewayへアクセスしてください。

    ガイド: [exe.dev](/ja-JP/install/exe-dev), [Hetzner](/ja-JP/install/hetzner), [Fly.io](/ja-JP/install/fly)。
    リモートアクセス: [Gateway remote](/ja-JP/gateway/remote)。

  </Accordion>

  <Accordion title="cloud/VPS install guidesはどこにありますか？">
    一般的なproviderをまとめた**hosting hub**があります。ひとつ選んでガイドに従ってください:

    - [VPS hosting](/ja-JP/vps)（すべてのproviderを1か所に集約）
    - [Fly.io](/ja-JP/install/fly)
    - [Hetzner](/ja-JP/install/hetzner)
    - [exe.dev](/ja-JP/install/exe-dev)

    cloudでの動作: **Gatewayはサーバー上で動作**し、Control UI（またはTailscale/SSH）を介して
    ノートPC/スマートフォンからアクセスします。state + workspace はサーバー上に
    あるため、hostを正本として扱い、バックアップしてください。

    そのcloud Gatewayに **nodes**（Mac/iOS/Android/headless）をペアリングして、
    Gatewayをcloudに置いたままローカルscreen/camera/canvasにアクセスしたり、
    ノートPC上でコマンドを実行したりできます。

    ハブ: [Platforms](/ja-JP/platforms)。リモートアクセス: [Gateway remote](/ja-JP/gateway/remote)。
    Nodes: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="OpenClaw自身に自己更新させられますか？">
    短い答え: **可能ですが、推奨しません**。更新フローは
    Gatewayを再起動することがあり（アクティブセッションが切れます）、クリーンなgit checkoutが
    必要になる場合があり、確認を求めることもあります。より安全なのは、オペレーターとしてshellから更新を実行することです。

    CLIを使ってください:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    agentから自動化する必要がある場合:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    ドキュメント: [Update](/cli/update), [Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="オンボーディングでは実際に何をしますか？">
    `openclaw onboard` は推奨セットアップ経路です。**local mode** では、次を案内します:

    - **Model/auth setup**（provider OAuth、API keys、Anthropic setup-token、LM Studioのようなローカルモデルオプションを含む）
    - **Workspace** の場所 + bootstrap files
    - **Gateway settings**（bind/port/auth/tailscale）
    - **Channels**（WhatsApp、Telegram、Discord、Mattermost、Signal、iMessage、およびQQ Botのようなバンドル済みchannel plugins）
    - **Daemon install**（macOSではLaunchAgent、Linux/WSL2ではsystemd user unit）
    - **Health checks** と **Skills** の選択

    また、設定したmodelが不明またはauth不足の場合は警告します。

  </Accordion>

  <Accordion title="これを動かすにはClaudeまたはOpenAIのサブスクリプションが必要ですか？">
    いいえ。OpenClawは **API keys**（Anthropic/OpenAI/others）でも、
    **ローカル専用モデル**でも動作するため、データをデバイス上にとどめられます。サブスクリプション（Claude
    Pro/Max または OpenAI Codex）は、それらproviderを認証するための任意の方法です。

    OpenClawでのAnthropicについて、実質的な区分は次のとおりです:

    - **Anthropic API key**: 通常のAnthropic API課金
    - **Claude CLI / OpenClaw内のClaude subscription auth**: Anthropic staff
      はこの利用が再び許可されていると案内しており、OpenClawは `claude -p`
      の使用を、この連携に対してAnthropicが新しい
      policyを公開しない限り認められたものとして扱っています

    長期間稼働するgateway hostsでは、Anthropic API keysのほうが依然として
    より予測しやすいセットアップです。OpenAI Codex OAuthは、OpenClawのような外部
    tools向けに明示的にサポートされています。

    OpenClawは他のサブスクリプション形式のホステッドオプションもサポートしており、
    **Qwen Cloud Coding Plan**、**MiniMax Coding Plan**、および
    **Z.AI / GLM Coding Plan** が含まれます。

    ドキュメント: [Anthropic](/ja-JP/providers/anthropic), [OpenAI](/ja-JP/providers/openai),
    [Qwen Cloud](/ja-JP/providers/qwen),
    [MiniMax](/ja-JP/providers/minimax), [GLM Models](/ja-JP/providers/glm),
    [Local models](/ja-JP/gateway/local-models), [Models](/ja-JP/concepts/models)。

  </Accordion>

  <Accordion title="API keyなしでClaude Max subscriptionを使えますか？">
    はい。

    Anthropic staffは、OpenClawスタイルのClaude CLI使用が再び許可されていると伝えているため、
    OpenClawはClaude subscription authと `claude -p` の使用を、この連携に対して
    Anthropicが新しいpolicyを公開しない限り認められたものとして扱います。最も予測しやすい
    サーバー側セットアップが欲しい場合は、代わりにAnthropic API keyを使ってください。

  </Accordion>

  <Accordion title="Claude subscription auth（Claude Pro or Max）をサポートしていますか？">
    はい。

    Anthropic staffはこの利用が再び許可されていると案内しているため、OpenClawは
    Claude CLIの再利用と `claude -p` の使用を、この連携に対して
    Anthropicが新しいpolicyを公開しない限り認められたものとして扱います。

    Anthropic setup-tokenは依然としてサポートされるOpenClaw token pathとして利用可能ですが、OpenClawは現在、利用可能な場合にClaude CLIの再利用と `claude -p` を優先します。
    本番環境やマルチユーザーワークロードでは、Anthropic API key authのほうが依然として
    より安全で予測しやすい選択肢です。OpenClawで他のサブスクリプション形式のホステッド
    オプションを使いたい場合は、[OpenAI](/ja-JP/providers/openai), [Qwen / Model
    Cloud](/ja-JP/providers/qwen), [MiniMax](/ja-JP/providers/minimax), および [GLM
    Models](/ja-JP/providers/glm) を参照してください。

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Anthropic から HTTP 429 rate_limit_error が表示されるのはなぜですか？">
これは、現在のウィンドウで **Anthropic quota/rate limit** を使い切ったことを意味します。
**Claude CLI** を使っている場合は、ウィンドウがリセットされるのを待つか、プランをアップグレードしてください。
**Anthropic API key** を使っている場合は、Anthropic Console
で usage/billing を確認し、必要に応じて上限を引き上げてください。

    メッセージが具体的に次の場合:
    `Extra usage is required for long context requests`、そのリクエストは
    Anthropicの1M context beta（`context1m: true`）を使おうとしています。これは、
    そのcredentialが長文脈課金に適格な場合にのみ機能します（API key billing または
    Extra Usageが有効なOpenClaw Claude-login path）。

    ヒント: providerがrate-limitedの間もOpenClawが応答を続けられるよう、
    **fallback model** を設定してください。
    [Models](/cli/models), [OAuth](/ja-JP/concepts/oauth), および
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/ja-JP/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context) を参照してください。

  </Accordion>

  <Accordion title="AWS Bedrockはサポートされていますか？">
    はい。OpenClawにはバンドルされた **Amazon Bedrock (Converse)** providerがあります。AWS env markersが存在する場合、OpenClawはストリーミング/テキスト対応のBedrock catalogを自動検出し、暗黙の `amazon-bedrock` providerとしてマージできます。そうでない場合は、`plugins.entries.amazon-bedrock.config.discovery.enabled` を明示的に有効化するか、手動でprovider entryを追加できます。[Amazon Bedrock](/ja-JP/providers/bedrock) と [Model providers](/ja-JP/providers/models) を参照してください。managed key flowを好む場合は、Bedrockの前段にOpenAI互換proxyを置くのも引き続き有効な選択肢です。
  </Accordion>

  <Accordion title="Codex authはどのように動作しますか？">
    OpenClawは、OAuth（ChatGPT sign-in）経由で **OpenAI Code (Codex)** をサポートしています。オンボーディングでOAuthフローを実行でき、適切な場合はデフォルトmodelを `openai-codex/gpt-5.4` に設定します。[Model providers](/ja-JP/concepts/model-providers) と [Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。
  </Accordion>

  <Accordion title="なぜChatGPT GPT-5.4では OpenClaw の openai/gpt-5.4 が使えるようにならないのですか？">
    OpenClawでは、この2つの経路を別々に扱います:

    - `openai-codex/gpt-5.4` = ChatGPT/Codex OAuth
    - `openai/gpt-5.4` = 直接のOpenAI Platform API

    OpenClawでは、ChatGPT/Codex sign-in は `openai-codex/*` 経路に接続され、
    直接の `openai/*` 経路には接続されません。OpenClawで直接API経路を使いたい場合は、
    `OPENAI_API_KEY`（または同等のOpenAI provider config）を設定してください。
    OpenClawでChatGPT/Codex sign-in を使いたい場合は、`openai-codex/*` を使ってください。

  </Accordion>

  <Accordion title="Codex OAuthの制限がChatGPT webと異なることがあるのはなぜですか？">
    `openai-codex/*` はCodex OAuth経路を使い、その利用可能なquota windowsは
    OpenAIが管理し、planに依存します。実際には、両方が同じアカウントに紐づいていても、
    その制限はChatGPT website/appの体験と異なることがあります。

    OpenClawは、現在見えているproviderのusage/quota windowsを
    `openclaw models status` に表示できますが、ChatGPT webの
    entitlementを直接API accessに作り替えたり正規化したりはしません。直接のOpenAI Platform
    billing/limit pathが欲しい場合は、API key付きの `openai/*` を使ってください。

  </Accordion>

  <Accordion title="OpenAI subscription auth（Codex OAuth）をサポートしていますか？">
    はい。OpenClawは **OpenAI Code (Codex) subscription OAuth** を完全にサポートしています。
    OpenAIは、OpenClawのような外部tools/workflowsでのsubscription OAuth利用を
    明示的に許可しています。オンボーディングでOAuthフローを実行できます。

    [OAuth](/ja-JP/concepts/oauth), [Model providers](/ja-JP/concepts/model-providers), および [Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。

  </Accordion>

  <Accordion title="Gemini CLI OAuthはどうセットアップしますか？">
    Gemini CLIは **plugin auth flow** を使い、`openclaw.json` 内のclient idやsecretは使いません。

    手順:

    1. `gemini` が `PATH` 上に来るようにGemini CLIをローカルにインストールします
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. pluginを有効化します: `openclaw plugins enable google`
    3. ログインします: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. ログイン後のデフォルトmodel: `google-gemini-cli/gemini-3.1-pro-preview`
    5. リクエストが失敗する場合は、gateway hostで `GOOGLE_CLOUD_PROJECT` または `GOOGLE_CLOUD_PROJECT_ID` を設定してください

    これにより、OAuth tokensはgateway host上のauth profilesに保存されます。詳細: [Model providers](/ja-JP/concepts/model-providers)。

  </Accordion>

  <Accordion title="ローカルモデルはカジュアルなチャットに適していますか？">
    通常は適していません。OpenClawには大きなcontextと強い安全性が必要で、小さなカードでは切り詰めや漏洩が起きます。それでも使うなら、ローカルで動かせる**最大の**モデルビルド（LM Studio）を使い、[/gateway/local-models](/ja-JP/gateway/local-models) を参照してください。小さい/量子化されたモデルはprompt injectionのリスクを高めます。詳細は [Security](/ja-JP/gateway/security) を参照してください。
  </Accordion>

  <Accordion title="ホステッドモデルのトラフィックを特定リージョン内に保つには？">
    リージョン固定エンドポイントを選んでください。OpenRouterはMiniMax、Kimi、GLM向けにUS-hostedオプションを提供しているため、リージョン内にデータを保つにはUS-hosted variantを選択してください。`models.mode: "merge"` を使えば、選択したリージョンproviderを尊重しつつ、Anthropic/OpenAIも併記してフォールバック可能にできます。
  </Accordion>

  <Accordion title="これをインストールするのにMac Miniを買う必要がありますか？">
    いいえ。OpenClawはmacOSまたはLinuxで動作します（WindowsはWSL2経由）。Mac miniは任意です。
    常時稼働ホストとして購入する人もいますが、小さなVPS、ホームサーバー、またはRaspberry Pi級のマシンでも十分です。

    Macが必要なのは **macOS専用tools** のためだけです。iMessageには [BlueBubbles](/ja-JP/channels/bluebubbles) を使ってください（推奨） -
    BlueBubbles serverは任意のMacで動き、GatewayはLinuxや他の場所で動かせます。その他のmacOS専用toolsを使いたい場合は、GatewayをMac上で動かすか、macOS nodeをペアリングしてください。

    ドキュメント: [BlueBubbles](/ja-JP/channels/bluebubbles), [Nodes](/ja-JP/nodes), [Mac remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="iMessage supportにはMac miniが必要ですか？">
    Messagesにサインインした **何らかのmacOSデバイス** が必要です。**Mac miniである必要はありません** -
    どんなMacでもかまいません。iMessageには **[BlueBubbles](/ja-JP/channels/bluebubbles)** を使ってください（推奨） -
    BlueBubbles serverはmacOS上で動作し、GatewayはLinuxや他の場所で動かせます。

    一般的なセットアップ:

    - GatewayをLinux/VPSで実行し、Messagesにサインインした任意のMacでBlueBubbles serverを実行する。
    - 最も単純な単一マシン構成にしたい場合は、すべてをMac上で実行する。

    ドキュメント: [BlueBubbles](/ja-JP/channels/bluebubbles), [Nodes](/ja-JP/nodes),
    [Mac remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="OpenClawを動かすためにMac miniを買った場合、MacBook Proと接続できますか？">
    はい。**Mac miniはGatewayを実行**でき、MacBook Proは
    **node**（companion device）として接続できます。NodesはGatewayを実行しません -
    そのデバイス上のscreen/camera/canvasや `system.run` のような追加機能を提供します。

    一般的なパターン:

    - GatewayはMac mini上（常時稼働）。
    - MacBook ProはmacOS appまたはnode hostを実行してGatewayにペアリング。
    - 確認には `openclaw nodes status` / `openclaw nodes list` を使用。

    ドキュメント: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="Bunは使えますか？">
    Bunは**推奨されません**。特にWhatsAppやTelegramでランタイムバグが見られます。
    安定したGatewayには **Node** を使ってください。

    それでもBunを試したい場合は、WhatsApp/Telegramなしの非本番Gatewayで
    試してください。

  </Accordion>

  <Accordion title="Telegram: allowFrom には何を入れますか？">
    `channels.telegram.allowFrom` は **人間の送信者のTelegram user ID**（数値）です。bot usernameではありません。

    オンボーディングでは `@username` 入力を受け付けて数値IDへ解決しますが、OpenClawの認可は数値IDだけを使います。

    より安全な方法（サードパーティbot不要）:

    - botにDMを送信し、そのあと `openclaw logs --follow` を実行して `from.id` を読みます。

    公式Bot API:

    - botにDMを送信し、そのあと `https://api.telegram.org/bot<bot_token>/getUpdates` を呼び、`message.from.id` を読みます。

    サードパーティ（プライバシーは低い）:

    - `@userinfobot` または `@getidsbot` にDMを送ります。

    [/channels/telegram](/ja-JP/channels/telegram#access-control-and-activation) を参照してください。

  </Accordion>

  <Accordion title="1つのWhatsApp番号を複数のOpenClawインスタンスで、使う人ごとに分けられますか？">
    はい。**multi-agent routing** で可能です。各送信者のWhatsApp **DM**（peer `kind: "direct"`、送信者のE.164 例 `+15551234567`）を別の `agentId` にバインドすれば、各人ごとに独自のworkspaceとsession storeを持てます。返信は依然として**同じWhatsAppアカウント**から送信され、DM access control（`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`）はWhatsAppアカウント単位でグローバルです。[Multi-Agent Routing](/ja-JP/concepts/multi-agent) と [WhatsApp](/ja-JP/channels/whatsapp) を参照してください。
  </Accordion>

  <Accordion title='「高速チャット」agentと「コーディング用Opus」agentを分けて実行できますか？'>
    はい。multi-agent routingを使ってください。各agentに独自のデフォルトmodelを設定し、受信ルート（provider accountや特定のpeer）をそれぞれのagentにバインドします。設定例は [Multi-Agent Routing](/ja-JP/concepts/multi-agent) にあります。[Models](/ja-JP/concepts/models) と [Configuration](/ja-JP/gateway/configuration) も参照してください。
  </Accordion>

  <Accordion title="HomebrewはLinuxで動きますか？">
    はい。HomebrewはLinux（Linuxbrew）をサポートしています。クイックセットアップ:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    OpenClawをsystemd経由で実行する場合は、service PATHに `/home/linuxbrew/.linuxbrew/bin`（またはあなたのbrew prefix）を含め、`brew` でインストールしたtoolsが非ログインshellでも解決できるようにしてください。
    最近のビルドでは、Linux systemd services上で一般的なuser bin dirs（例 `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`）も先頭に追加し、`PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR`, `FNM_DIR` が設定されていればそれらも尊重します。

  </Accordion>

  <Accordion title="ハッカブルな git install と npm install の違い">
    - **ハッカブルな（git）インストール:** 完全なソースcheckoutで、編集可能、contributors向けに最適です。
      ローカルでビルドを行い、コードやdocsを修正できます。
    - **npm install:** グローバルCLIインストールで、repoはなく、「とにかく動かしたい」用途に最適です。
      更新はnpm dist-tagsから来ます。

    ドキュメント: [はじめに](/ja-JP/start/getting-started), [Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="あとから npm install と git install を切り替えられますか？">
    はい。もう一方の方式をインストールしたあと、Doctorを実行してgateway serviceが新しいentrypointを指すようにしてください。
    これは**データを削除しません** - 変わるのはOpenClawのコードインストールだけです。state
    （`~/.openclaw`）とworkspace（`~/.openclaw/workspace`）はそのままです。

    npmからgitへ:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    gitからnpmへ:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctorはgateway service entrypointの不一致を検出し、現在のインストールに合わせてservice configを書き換えることを提案します（自動化では `--repair` を使用）。

    バックアップのヒント: [Backup strategy](#ディスク上の場所) を参照してください。

  </Accordion>

  <Accordion title="GatewayはノートPCで動かすべきですか？ それともVPSですか？">
    短い答え: **24時間365日の信頼性が欲しいならVPSを使ってください**。摩擦を最小にしたく、
    スリープや再起動を許容できるならローカルで実行してください。

    **Laptop（local Gateway）**

    - **Pros:** サーバー費用なし、ローカルファイルへ直接アクセス、可視ブラウザウィンドウ。
    - **Cons:** スリープ/ネットワーク断 = 切断、OS更新/再起動で中断、起動し続ける必要あり。

    **VPS / cloud**

    - **Pros:** 常時稼働、安定ネットワーク、ノートPCのスリープ問題なし、稼働を維持しやすい。
    - **Cons:** 多くはheadlessで動作（スクリーンショットを使う）、リモートファイルアクセスのみ、更新にはSSHが必要。

    **OpenClaw固有の注意:** WhatsApp/Telegram/Slack/Mattermost/Discord はすべてVPSから問題なく動作します。実際のトレードオフは **headless browser** か可視ウィンドウかだけです。[Browser](/ja-JP/tools/browser) を参照してください。

    **推奨デフォルト:** 以前にgateway切断があったならVPS。ローカルは、Macを積極的に使っていて、ローカルファイルアクセスや可視ブラウザによるUI automationが欲しいときに最適です。

  </Accordion>

  <Accordion title="OpenClawを専用マシンで動かす重要性はどれくらいですか？">
    必須ではありませんが、**信頼性と分離のため推奨**します。

    - **専用host（VPS/Mac mini/Pi）:** 常時稼働、スリープ/再起動の中断が少ない、権限が整理しやすい、稼働維持が容易。
    - **共有ノートPC/デスクトップ:** テストや日常利用にはまったく問題ありませんが、マシンがスリープしたり更新したりすると停止が発生します。

    両方の利点が欲しい場合は、Gatewayは専用hostに置き、ノートPCを**node**として
    ペアリングしてローカルscreen/camera/exec toolsに使ってください。[Nodes](/ja-JP/nodes) を参照してください。
    セキュリティガイダンスについては [Security](/ja-JP/gateway/security) を読んでください。

  </Accordion>

  <Accordion title="最小VPS要件と推奨OSは何ですか？">
    OpenClawは軽量です。基本的なGateway + 1つのチャットチャネルであれば:

    - **絶対最小:** 1 vCPU、1GB RAM、約500MB disk。
    - **推奨:** 1-2 vCPU、2GB RAM以上で余裕を確保（ログ、メディア、複数チャネル）。Node toolsやbrowser automationはリソースを多く使う場合があります。

    OS: **Ubuntu LTS**（または任意の現代的なDebian/Ubuntu）を使ってください。Linux install pathはそこで最もよくテストされています。

    ドキュメント: [Linux](/ja-JP/platforms/linux), [VPS hosting](/ja-JP/vps)。

  </Accordion>

  <Accordion title="OpenClawをVMで動かせますか？ 要件は何ですか？">
    はい。VMはVPSと同じように扱ってください。常時稼働し、到達可能で、
    Gatewayと有効化するchannelsを支える十分なRAMが必要です。

    基本ガイダンス:

    - **絶対最小:** 1 vCPU、1GB RAM。
    - **推奨:** 複数チャネル、browser automation、media toolsを使う場合は2GB RAM以上。
    - **OS:** Ubuntu LTS または他の現代的なDebian/Ubuntu。

    Windowsなら、**WSL2が最も簡単なVM風セットアップ**で、tooling互換性も最良です。
    [Windows](/ja-JP/platforms/windows), [VPS hosting](/ja-JP/vps) を参照してください。
    macOSをVMで動かしている場合は [macOS VM](/ja-JP/install/macos-vm) を参照してください。

  </Accordion>
</AccordionGroup>

## OpenClawとは何ですか？

<AccordionGroup>
  <Accordion title="OpenClawを1段落でいうと？">
    OpenClawは、自分のデバイス上で動かす個人用AI assistantです。すでに使っているメッセージング面（WhatsApp、Telegram、Slack、Mattermost、Discord、Google Chat、Signal、iMessage、WebChat、およびQQ Botのようなバンドル済みchannel plugins）で応答でき、対応プラットフォームでは音声 + ライブCanvasも利用できます。常時稼働の制御プレーンが **Gateway** であり、製品自体はassistantです。
  </Accordion>

  <Accordion title="価値提案">
    OpenClawは「単なるClaude wrapper」ではありません。**ローカルファーストの制御プレーン**であり、
    すでに使っているチャットアプリから到達可能な、有能なassistantを**自分のハードウェア上**で動かせます。
    stateful sessions、memory、toolsを備えつつ、ワークフローの制御をホステッド
    SaaSに渡さずに済みます。

    主なポイント:

    - **自分のデバイス、自分のデータ:** Gatewayを好きな場所（Mac、Linux、VPS）で動かし、
      workspace + session historyをローカルに保持できます。
    - **Webサンドボックスではなく実際のchannels:** WhatsApp/Telegram/Slack/Discord/Signal/iMessageなど、
      加えて対応プラットフォームではモバイル音声とCanvasも利用可能です。
    - **モデル非依存:** Anthropic、OpenAI、MiniMax、OpenRouterなどを、agentごとのrouting
      とfailoverで使えます。
    - **ローカル専用オプション:** ローカルモデルを使えば、望むなら **すべてのデータをデバイス上に保てます**。
    - **Multi-agent routing:** チャネル、アカウント、タスクごとにagentを分けられ、それぞれが独自の
      workspaceとdefaultsを持ちます。
    - **オープンソースでハッカブル:** ベンダーロックインなしで調べ、拡張し、セルフホストできます。

    ドキュメント: [Gateway](/ja-JP/gateway), [Channels](/ja-JP/channels), [Multi-agent](/ja-JP/concepts/multi-agent),
    [Memory](/ja-JP/concepts/memory)。

  </Accordion>

  <Accordion title="セットアップしたばかりです。最初に何をすべきですか？">
    最初のプロジェクト候補:

    - Webサイトを作る（WordPress、Shopify、またはシンプルな静的サイト）。
    - モバイルアプリを試作する（構成、画面、API plan）。
    - ファイルやフォルダーを整理する（クリーンアップ、命名、タグ付け）。
    - Gmailを接続して要約やフォローアップを自動化する。

    大きなタスクも処理できますが、段階に分けて、
    並列作業にはsub agentsを使うと最も効果的です。

  </Accordion>

  <Accordion title="OpenClawの日常的な上位5つのユースケースは何ですか？">
    日常的に便利なのは、たいてい次のようなものです:

    - **個人ブリーフィング:** inbox、calendar、気になるニュースの要約。
    - **調査と下書き:** メールやドキュメント向けの素早い調査、要約、初稿作成。
    - **リマインダーとフォローアップ:** cronやheartbeatによるリマインドとチェックリスト。
    - **Browser automation:** フォーム入力、データ収集、Webタスクの繰り返し。
    - **デバイス横断の連携:** スマートフォンからタスクを送り、Gatewayにサーバーで実行させ、結果をチャットで受け取る。

  </Accordion>

  <Accordion title="OpenClawはSaaS向けのリード獲得、アウトリーチ、広告、ブログ作成を手伝えますか？">
    **調査、適格性評価、下書き** には使えます。サイトを調べ、候補リストを作り、
    見込み客を要約し、アウトリーチや広告コピーの下書きを書けます。

    **アウトリーチや広告配信** では、人間を必ずループに残してください。スパムは避け、地域の法律と
    プラットフォームポリシーに従い、送信前に必ず見直してください。最も安全なパターンは、
    OpenClawに下書きを作らせて、あなたが承認することです。

    ドキュメント: [Security](/ja-JP/gateway/security)。

  </Accordion>

  <Accordion title="Web開発におけるClaude Codeとの違い・利点は何ですか？">
    OpenClawは、IDEの置き換えではなく、**個人assistant** であり調整レイヤーです。repo内で最速の直接コーディングループが欲しいなら
    Claude CodeやCodexを使ってください。持続的なmemory、デバイス横断アクセス、tool orchestrationが
    欲しいならOpenClawを使ってください。

    利点:

    - セッションをまたぐ**永続的なmemory + workspace**
    - **マルチプラットフォームアクセス**（WhatsApp、Telegram、TUI、WebChat）
    - **Tool orchestration**（browser、files、scheduling、hooks）
    - **常時稼働Gateway**（VPSで動かし、どこからでも操作）
    - ローカルbrowser/screen/camera/exec用の **Nodes**

    紹介: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skillsと自動化

<AccordionGroup>
  <Accordion title="repoを汚さずにSkillsをカスタマイズするには？">
    repo内のコピーを編集する代わりに、managed overridesを使ってください。変更は `~/.openclaw/skills/<name>/SKILL.md` に置くか、`~/.openclaw/openclaw.json` の `skills.load.extraDirs` でフォルダーを追加してください。優先順位は `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` なので、managed overridesはgitに触れずにbundled skillsより優先されます。skillをグローバルにインストールしつつ一部のagentsにだけ見せたい場合は、共有コピーを `~/.openclaw/skills` に置き、`agents.defaults.skills` と `agents.list[].skills` で可視性を制御してください。上流に送る価値のある編集だけをrepoに置き、PRとして送ってください。
  </Accordion>

  <Accordion title="カスタムフォルダーからSkillsを読み込めますか？">
    はい。`~/.openclaw/openclaw.json` の `skills.load.extraDirs` で追加ディレクトリを指定してください（最も低い優先順位）。デフォルトの優先順位は `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` です。`clawhub` はデフォルトで `./skills` にインストールします。OpenClawは次のセッションでこれを `<workspace>/skills` として扱います。skillを特定のagentsにだけ見せたい場合は、`agents.defaults.skills` または `agents.list[].skills` と組み合わせてください。
  </Accordion>

  <Accordion title="タスクごとに異なるモデルを使うには？">
    現在サポートされているパターンは次のとおりです:

    - **Cron jobs**: 分離されたjobごとに `model` override を設定できます。
    - **Sub-agents**: 異なるデフォルトmodelを持つ別agentにタスクをルーティングします。
    - **オンデマンド切り替え**: `/model` を使って現在のsession modelをいつでも切り替えます。

    [Cron jobs](/ja-JP/automation/cron-jobs), [Multi-Agent Routing](/ja-JP/concepts/multi-agent), および [Slash commands](/ja-JP/tools/slash-commands) を参照してください。

  </Accordion>

  <Accordion title="重い作業をしているとbotが止まります。どうオフロードすればよいですか？">
    長いタスクや並列タスクには **sub-agents** を使ってください。sub-agentsは独自のsessionで実行され、
    要約を返し、メインチャットの応答性を維持します。

    botに「このタスク用にsub-agentをspawnして」と頼むか、`/subagents` を使ってください。
    `/status` をチャットで使うと、Gatewayが今何をしているか（そして忙しいかどうか）を確認できます。

    トークンのヒント: 長いタスクもsub-agentsもトークンを消費します。コストが気になるなら、
    `agents.defaults.subagents.model` でsub-agents用により安価なmodelを設定してください。

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents), [Background Tasks](/ja-JP/automation/tasks)。

  </Accordion>

  <Accordion title="Discordでthreadに紐づくsubagent sessionはどう動きますか？">
    thread bindingsを使ってください。Discord threadをsubagentまたはsession targetにバインドすると、そのthread内の後続メッセージがそのバインドされたsession上に留まります。

    基本フロー:

    - `sessions_spawn` を `thread: true` で使う（永続的な後続のために必要なら `mode: "session"` も）。
    - または `/focus <target>` で手動バインド。
    - `/agents` でbinding stateを確認。
    - `/session idle <duration|off>` と `/session max-age <duration|off>` でauto-unfocusを制御。
    - `/unfocus` でthreadを切り離す。

    必要なconfig:

    - グローバルdefaults: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`。
    - Discord overrides: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`。
    - spawn時のauto-bind: `channels.discord.threadBindings.spawnSubagentSessions: true` を設定。

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents), [Discord](/ja-JP/channels/discord), [Configuration Reference](/ja-JP/gateway/configuration-reference), [Slash commands](/ja-JP/tools/slash-commands)。

  </Accordion>

  <Accordion title="subagentが完了したのに、完了通知が間違った場所に行った、または投稿されませんでした。何を確認すべきですか？">
    まず解決されたrequester routeを確認してください:

    - completion-modeのsubagent配信は、bound threadまたはconversation routeが存在する場合、それを優先します。
    - completion originがchannelしか持っていない場合でも、OpenClawはrequester sessionの保存済みroute（`lastChannel` / `lastTo` / `lastAccountId`）にフォールバックするため、直接配信がまだ成功する可能性があります。
    - bound routeも利用可能な保存済みrouteもない場合、直接配信は失敗し、結果はチャットへ即時投稿されず、queued session deliveryへフォールバックします。
    - 無効または古いtargetは、依然としてqueue fallbackまたは最終配信失敗を引き起こす可能性があります。
    - 子の最後に見えたassistant replyが、正確にサイレントトークン `NO_REPLY` / `no_reply`、または正確に `ANNOUNCE_SKIP` の場合、OpenClawは古い進捗を投稿せず、意図的にannounceを抑制します。
    - 子がtool callsだけを行った状態でタイムアウトした場合、announceは生のtool outputを再生せず、それを短い部分進捗サマリーへ要約することがあります。

    デバッグ:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents), [Background Tasks](/ja-JP/automation/tasks), [Session Tools](/ja-JP/concepts/session-tool)。

  </Accordion>

  <Accordion title="Cronやremindersが発火しません。何を確認すべきですか？">
    CronはGatewayプロセス内で動作します。Gatewayが連続稼働していなければ、
    スケジュール済みjobは実行されません。

    チェックリスト:

    - cronが有効（`cron.enabled`）であり、`OPENCLAW_SKIP_CRON` が設定されていないことを確認。
    - Gatewayが24時間365日稼働していることを確認（スリープ/再起動なし）。
    - jobのtimezone設定（`--tz` とhost timezone）を確認。

    デバッグ:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [Automation & Tasks](/ja-JP/automation)。

  </Accordion>

  <Accordion title="Cronは発火したのに、channelへ何も送られませんでした。なぜですか？">
    まずdelivery modeを確認してください:

    - `--no-deliver` / `delivery.mode: "none"` は、外部メッセージが送られないことを意味します。
    - announce target（`channel` / `to`）が欠けているか無効だと、runnerはoutbound deliveryをスキップします。
    - channel auth failures（`unauthorized`, `Forbidden`）は、runnerが配信を試みたがcredentialsに阻まれたことを意味します。
    - サイレントなisolated result（`NO_REPLY` / `no_reply` のみ）は意図的に配信不可として扱われるため、runnerはqueued fallback deliveryも抑制します。

    isolated cron jobsでは、最終配信はrunnerが担当します。agentは
    runnerが送るためのプレーンテキストの要約を返すことが期待されます。`--no-deliver` は
    その結果を内部に留めるものであり、message toolでagentが直接送れるようにする
    ものではありません。

    デバッグ:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [Background Tasks](/ja-JP/automation/tasks)。

  </Accordion>

  <Accordion title="なぜisolated cron runがモデルを切り替えたり、一度再試行したりしたのですか？">
    それは通常、重複スケジューリングではなくライブmodel-switch pathです。

    isolated cronは、アクティブな
    実行が `LiveSessionModelSwitchError` を投げたときに、ランタイムmodel handoffを保存して再試行できます。再試行では切り替え後の
    provider/modelが維持され、その切り替えに新しいauth profile overrideが含まれていた場合、cronは
    再試行前にそれも保存します。

    関連する選択ルール:

    - 適用される場合、Gmail hook model overrideが最優先。
    - 次にjobごとの `model`。
    - 次に保存済みcron-session model override。
    - 最後に通常のagent/default model selection。

    再試行ループには上限があります。初回試行 + 2回のswitch retriesの後は、
    無限ループせずcronは中止します。

    デバッグ:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [cron CLI](/cli/cron)。

  </Accordion>

  <Accordion title="LinuxでSkillsをインストールするには？">
    ネイティブの `openclaw skills` コマンドを使うか、skillsをworkspaceに配置してください。macOSのSkills UIはLinuxでは利用できません。
    Skillsは [https://clawhub.ai](https://clawhub.ai) で閲覧できます。

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

    ネイティブの `openclaw skills install` は、アクティブworkspaceの `skills/`
    ディレクトリに書き込みます。自分のskillsを公開または
    syncしたい場合だけ、別途 `clawhub` CLIをインストールしてください。agents間で共有したい場合は、skillを
    `~/.openclaw/skills` に置き、見えるagentを絞りたければ `agents.defaults.skills` または
    `agents.list[].skills` を使ってください。

  </Accordion>

  <Accordion title="OpenClawはスケジュール実行や継続的なバックグラウンド動作ができますか？">
    はい。Gateway schedulerを使ってください:

    - **Cron jobs** でスケジュール済みまたは繰り返しタスク（再起動をまたいで保持）。
    - **Heartbeat** で「メインsession」の定期チェック。
    - **Isolated jobs** で、自律agentが要約を投稿したりチャットへ配信したりできます。

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [Automation & Tasks](/ja-JP/automation),
    [Heartbeat](/ja-JP/gateway/heartbeat)。

  </Accordion>

  <Accordion title="LinuxからApple macOS専用Skillsを実行できますか？">
    直接はできません。macOS skillsは `metadata.openclaw.os` と必要バイナリでゲートされており、skillsは **Gateway host** 上で適格な場合にのみsystem promptに現れます。Linuxでは、`darwin` 専用skills（`apple-notes`, `apple-reminders`, `things-mac` など）は、ゲーティングを上書きしない限り読み込まれません。

    サポートされるパターンは3つあります:

    **Option A - Mac上でGatewayを実行する（最も簡単）。**
    macOSバイナリが存在する場所でGatewayを実行し、そのあとLinuxから [remote mode](#gateway-ポートが既に使われている-リモートモード) やTailscale経由で接続してください。Gateway hostがmacOSなので、skillsは通常どおり読み込まれます。

    **Option B - macOS nodeを使う（SSH不要）。**
    LinuxでGatewayを実行し、macOS node（menubar app）をペアリングして、Mac上で **Node Run Commands** を「Always Ask」または「Always Allow」に設定します。必要バイナリがnode上に存在すれば、OpenClawはmacOS専用skillsを適格として扱えます。agentはそれらのskillsを `nodes` tool経由で実行します。「Always Ask」を選んでいて、prompt内で「Always Allow」を承認すると、そのコマンドはallowlistに追加されます。

    **Option C - macOSバイナリをSSH経由でプロキシする（上級者向け）。**
    GatewayはLinuxに置いたまま、必要なCLIバイナリをMac上で実行するSSH wrapperに解決させます。そのうえでskillを上書きしてLinuxでも適格にしてください。

    1. バイナリ用のSSH wrapperを作成します（例: Apple Notes用の `memo`）:

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. そのwrapperをLinux host上の `PATH` に置きます（例 `~/bin/memo`）。
    3. skill metadataを上書きしてLinuxを許可します（workspaceまたは `~/.openclaw/skills`）:

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. skills snapshotが更新されるよう、新しいsessionを開始します。

  </Accordion>

  <Accordion title="NotionやHeyGen integrationはありますか？">
    現時点では組み込みではありません。

    選択肢:

    - **Custom skill / plugin:** 信頼性の高いAPI accessには最適です（Notion/HeyGenはどちらもAPIがあります）。
    - **Browser automation:** コード不要で動きますが、遅く、壊れやすくなります。

    クライアントごとにコンテキストを維持したい場合（agencyワークフロー）は、次のようなシンプルなパターンがあります:

    - クライアントごとに1つのNotionページ（context + preferences + active work）。
    - session開始時に、そのページを取得するようagentに依頼する。

    ネイティブintegrationが欲しい場合は、feature requestを出すか、それらのAPIを対象にしたskillを作ってください。

    Skillsのインストール:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    ネイティブインストールはアクティブworkspaceの `skills/` ディレクトリに入ります。agents間で共有するskillsは `~/.openclaw/skills/<name>/SKILL.md` に配置してください。共有インストールを一部のagentsにだけ見せたい場合は、`agents.defaults.skills` または `agents.list[].skills` を設定してください。一部のskillsはHomebrew経由でインストールしたバイナリを前提とします。LinuxではLinuxbrewを意味します（上のHomebrew Linux FAQ項目を参照）。[Skills](/ja-JP/tools/skills), [Skills config](/ja-JP/tools/skills-config), [ClawHub](/ja-JP/tools/clawhub) を参照してください。

  </Accordion>

  <Accordion title="既にサインイン済みのChromeをOpenClawで使うには？">
    組み込みの `user` browser profileを使ってください。これはChrome DevTools MCP経由で接続します:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    カスタム名を使いたい場合は、明示的なMCP profileを作成してください:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    この経路はhost-localです。Gatewayが別の場所で動作している場合は、browserマシンでnode hostを動かすか、代わりにremote CDPを使ってください。

    `existing-session` / `user` の現在の制限:

    - actionsはCSS-selector駆動ではなくref駆動
    - uploadsは `ref` / `inputRef` が必要で、現在は一度に1ファイルだけサポート
    - `responsebody`、PDF export、download interception、batch actions は依然としてmanaged browserまたはraw CDP profileが必要

  </Accordion>
</AccordionGroup>

## サンドボックスとメモリ

<AccordionGroup>
  <Accordion title="専用のsandboxingドキュメントはありますか？">
    はい。[Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。Docker固有のセットアップ（Docker内での完全なgatewayやsandbox images）については [Docker](/ja-JP/install/docker) を参照してください。
  </Accordion>

  <Accordion title="Dockerが制限されているように感じます。完全機能を有効にするには？">
    デフォルトimageはセキュリティ優先で `node` userとして実行されるため、
    system packages、Homebrew、bundled browsersは含まれません。より完全なセットアップにするには:

    - `/home/node` を `OPENCLAW_HOME_VOLUME` で永続化してcacheを保持する。
    - `OPENCLAW_DOCKER_APT_PACKAGES` でsystem depsをimageに焼き込む。
    - bundled CLI経由でPlaywright browsersをインストールする:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - `PLAYWRIGHT_BROWSERS_PATH` を設定し、そのパスが永続化されるようにする。

    ドキュメント: [Docker](/ja-JP/install/docker), [Browser](/ja-JP/tools/browser)。

  </Accordion>

  <Accordion title="1つのagentでDMは個人的に保ちつつ、groupは公開/サンドボックス化できますか？">
    はい。プライベートなトラフィックが **DMs** で、公開トラフィックが **groups** なら可能です。

    `agents.defaults.sandbox.mode: "non-main"` を使うと、group/channel sessions（non-main keys）はDocker内で実行され、メインDM sessionはhost上に残ります。そのうえで、sandbox化されたsessionsで利用可能なtoolsを `tools.sandbox.tools` で制限してください。

    セットアップ手順 + 設定例: [Groups: personal DMs + public groups](/ja-JP/channels/groups#pattern-personal-dms-public-groups-single-agent)

    主なconfig reference: [Gateway configuration](/ja-JP/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="host folderをsandboxにbindするには？">
    `agents.defaults.sandbox.docker.binds` に `["host:path:mode"]`（例 `"/home/user/src:/src:ro"`）を設定してください。グローバル + agentごとのbindはマージされます。`scope: "shared"` の場合、agentごとのbindは無視されます。機密性の高いものには `:ro` を使い、bindはsandbox filesystemの壁を迂回することを忘れないでください。

    OpenClawはbind sourceを、正規化パスと、最も深い既存祖先を通して解決されたcanonical pathの両方に対して検証します。つまり、最後のパスセグメントがまだ存在しなくても、親symlink経由の脱出は安全側に閉じたまま失敗し、symlink解決後にもallowed-root checksが適用されます。

    例と安全上の注意は [Sandboxing](/ja-JP/gateway/sandboxing#custom-bind-mounts) と [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) を参照してください。

  </Accordion>

  <Accordion title="メモリはどのように動作しますか？">
    OpenClawのメモリは、agent workspace内のMarkdown filesにすぎません:

    - 日次ノートは `memory/YYYY-MM-DD.md`
    - 長期ノートは `MEMORY.md`（main/private sessionsのみ）

    OpenClawはまた、auto-compaction前にモデルへ
    持続的なノートを書かせるための、**silent pre-compaction memory flush** も実行します。
    これはworkspaceが書き込み可能な場合にのみ動作します（read-only sandboxesではスキップされます）。[Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>

  <Accordion title="メモリがすぐ忘れます。定着させるには？">
    botに**その事実をメモリへ書き込む**よう頼んでください。長期ノートは `MEMORY.md` に、
    短期コンテキストは `memory/YYYY-MM-DD.md` に入ります。

    これはまだ改善中の領域です。モデルにメモリ保存を促すと役立ちます。
    モデルは何をすべきか理解しています。それでも忘れる場合は、Gatewayが毎回同じ
    workspaceを使っていることを確認してください。

    ドキュメント: [Memory](/ja-JP/concepts/memory), [Agent workspace](/ja-JP/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="メモリは永続しますか？ 制限は何ですか？">
    メモリファイルはディスク上に保存され、削除するまで残ります。制限は
    モデルではなくストレージです。ただし **session context** は依然としてモデルの
    context windowに制約されるため、長い会話ではcompactやtruncateが発生します。そのため
    memory searchが存在します。必要な部分だけをcontextへ戻します。

    ドキュメント: [Memory](/ja-JP/concepts/memory), [Context](/ja-JP/concepts/context)。

  </Accordion>

  <Accordion title="semantic memory searchにはOpenAI API keyが必要ですか？">
    **OpenAI embeddings** を使う場合だけ必要です。Codex OAuthはchat/completionsのみを対象とし、
    embeddings accessは提供しません。したがって **Codexでサインインしても（OAuthでも
    Codex CLI loginでも）** semantic memory searchには役立ちません。OpenAI embeddings
    には依然として本物のAPI key（`OPENAI_API_KEY` または `models.providers.openai.apiKey`）が必要です。

    providerを明示的に設定しない場合、OpenClawはAPI keyを解決できれば
    providerを自動選択します（auth profiles、`models.providers.*.apiKey`、またはenv vars）。
    OpenAI keyが解決できればOpenAIを優先し、そうでなければGemini、次にVoyage、
    次にMistralを選びます。リモートkeyが利用できない場合、
    設定するまでmemory searchは無効のままです。ローカルモデル経路が
    設定済みで存在する場合、OpenClawは
    `local` を優先します。Ollamaは、明示的に
    `memorySearch.provider = "ollama"` を設定した場合にサポートされます。

    ローカルに留めたい場合は、`memorySearch.provider = "local"`（必要なら
    `memorySearch.fallback = "none"`）を設定してください。Gemini embeddingsを使いたい場合は、
    `memorySearch.provider = "gemini"` を設定し、`GEMINI_API_KEY`（または
    `memorySearch.remote.apiKey`）を指定してください。**OpenAI, Gemini, Voyage, Mistral, Ollama, または local** のembedding
    modelsをサポートしています。セットアップ詳細は [Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>
</AccordionGroup>

## ディスク上の場所

<AccordionGroup>
  <Accordion title="OpenClawで使われるすべてのデータはローカルに保存されますか？">
    いいえ。**OpenClawのstateはローカル** ですが、**外部servicesは送信した内容を見る** ことができます。

    - **デフォルトでローカル:** sessions、memory files、config、workspace はGateway host上にあります
      （`~/.openclaw` + あなたのworkspace directory）。
    - **必然的にリモート:** model providers（Anthropic/OpenAIなど）へ送るメッセージは
      それらのAPIへ送られ、チャットプラットフォーム（WhatsApp/Telegram/Slackなど）はメッセージデータを
      それぞれのサーバーに保存します。
    - **足跡は自分で制御可能:** ローカルモデルを使えばpromptはマシン上に留められますが、channel
      trafficは依然としてそのchannelのサーバーを通ります。

    関連: [Agent workspace](/ja-JP/concepts/agent-workspace), [Memory](/ja-JP/concepts/memory)。

  </Accordion>

  <Accordion title="OpenClawはデータをどこに保存しますか？">
    すべては `$OPENCLAW_STATE_DIR`（デフォルト: `~/.openclaw`）配下にあります:

    | Path                                                            | Purpose                                                            |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | メイン設定（JSON5）                                                |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | レガシーOAuthインポート（初回使用時にauth profilesへコピー）       |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Auth profiles（OAuth、API keys、任意の `keyRef`/`tokenRef`）       |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef providers用の任意のfile-backed secret payload     |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | レガシー互換ファイル（静的な `api_key` エントリーは除去される）    |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Provider state（例 `whatsapp/<accountId>/creds.json`）             |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | agentごとのstate（agentDir + sessions）                            |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 会話履歴 & state（agentごと）                                      |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Session metadata（agentごと）                                      |

    レガシーsingle-agent path: `~/.openclaw/agent/*`（`openclaw doctor` により移行）。

    **Workspace**（AGENTS.md、memory files、skillsなど）は別で、`agents.defaults.workspace` で設定します（デフォルト: `~/.openclaw/workspace`）。

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md はどこに置くべきですか？">
    これらのファイルは `~/.openclaw` ではなく、**agent workspace** に置きます。

    - **Workspace（agentごと）**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md`（`MEMORY.md` がない場合はレガシーfallbackの `memory.md`）、
      `memory/YYYY-MM-DD.md`, 任意で `HEARTBEAT.md`。
    - **State dir（`~/.openclaw`）**: config、channel/provider state、auth profiles、sessions、logs、
      および共有skills（`~/.openclaw/skills`）。

    デフォルトworkspaceは `~/.openclaw/workspace` で、次で設定できます:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    再起動後にbotが「忘れる」場合は、Gatewayが毎回同じ
    workspaceを使って起動していることを確認してください（また、remote modeでは **gateway host側の**
    workspaceが使われ、ローカルノートPCのものではないことに注意してください）。

    ヒント: 持続的な挙動や好みを残したい場合は、チャット履歴に頼るのではなく、
    **AGENTS.md または MEMORY.md に書き込む**ようbotに頼んでください。

    [Agent workspace](/ja-JP/concepts/agent-workspace) と [Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>

  <Accordion title="推奨バックアップ戦略">
    **agent workspace** を**private** git repoに置き、
    privateな場所（例 GitHub private）へバックアップしてください。これによりmemory + AGENTS/SOUL/USER
    filesが保存され、あとでassistantの「mind」を復元できます。

    `~/.openclaw` 配下（credentials、sessions、tokens、または暗号化されたsecrets payloads）は **commitしないでください**。
    完全な復元が必要なら、workspaceとstate directoryの
    両方を別々にバックアップしてください（上の移行の質問を参照）。

    ドキュメント: [Agent workspace](/ja-JP/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="OpenClawを完全にアンインストールするには？">
    専用ガイドを参照してください: [Uninstall](/ja-JP/install/uninstall)。
  </Accordion>

  <Accordion title="agentsはworkspace外でも作業できますか？">
    はい。workspaceは**デフォルトcwd** とmemoryの基点であり、厳格なsandboxではありません。
    相対パスはworkspace内で解決されますが、sandboxingが無効なら絶対パスで他の
    host locationsにもアクセスできます。分離が必要なら
    [`agents.defaults.sandbox`](/ja-JP/gateway/sandboxing) またはagentごとのsandbox settingsを使ってください。repoをデフォルト作業ディレクトリにしたいなら、そのagentの
    `workspace` をrepo rootに向けてください。OpenClaw repoは単なるソースコードなので、
    意図的にagentにその中で作業させたいのでなければworkspaceは分けてください。

    例（repoをデフォルトcwdにする）:

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

  <Accordion title="Remote mode: session store はどこですか？">
    Session stateは **gateway host** が所有します。remote modeでは、重要なのはローカルノートPCではなく、リモートマシン上のsession storeです。[Session management](/ja-JP/concepts/session) を参照してください。
  </Accordion>
</AccordionGroup>

## Configの基本

<AccordionGroup>
  <Accordion title="configの形式は？ どこにありますか？">
    OpenClawは `$OPENCLAW_CONFIG_PATH`（デフォルト: `~/.openclaw/openclaw.json`）から任意の **JSON5** config を読み込みます:

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    ファイルが存在しない場合は、安全寄りのdefaults（デフォルトworkspace `~/.openclaw/workspace` を含む）を使います。

  </Accordion>

  <Accordion title='gateway.bind: "lan"（または "tailnet"）を設定したら、何もlistenしない / UIで unauthorized になる'>
    non-loopback bindでは **有効なgateway auth path** が必要です。実際には次を意味します:

    - 共有シークレット認証: tokenまたはpassword
    - 正しく設定されたnon-loopback identity-aware reverse proxyの背後での `gateway.auth.mode: "trusted-proxy"`

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

    注意:

    - `gateway.remote.token` / `.password` だけではローカルgateway authは有効になりません。
    - ローカルcall pathsでは、`gateway.auth.*` が未設定のときに限り `gateway.remote.*` をfallbackとして使えます。
    - password authでは、代わりに `gateway.auth.mode: "password"` と `gateway.auth.password`（または `OPENCLAW_GATEWAY_PASSWORD`）を設定してください。
    - `gateway.auth.token` / `gateway.auth.password` がSecretRef経由で明示設定されていて未解決の場合、解決は安全側に閉じて失敗します（remote fallbackで隠されません）。
    - 共有シークレットのControl UIセットアップは `connect.params.auth.token` または `connect.params.auth.password`（app/UI settingsに保存）で認証します。Tailscale Serveや `trusted-proxy` のようなidentity付きモードは代わりにrequest headersを使います。共有シークレットをURLへ入れないでください。
    - `gateway.auth.mode: "trusted-proxy"` では、同一hostのloopback reverse proxiesは依然としてtrusted-proxy authを満たしません。trusted proxyは設定済みのnon-loopback sourceである必要があります。

  </Accordion>

  <Accordion title="localhostでも今はtokenが必要なのはなぜですか？">
    OpenClawは、loopbackを含めてデフォルトでgateway authを強制します。通常のデフォルト経路では、これはtoken authを意味します。明示的なauth pathが設定されていない場合、gateway起動時にtoken modeへ解決され、自動生成されたtokenを `gateway.auth.token` に保存するため、**ローカルWS clientsも認証が必要**です。これにより他のローカルprocessがGatewayを呼び出すことを防ぎます。

    別のauth pathを好む場合は、password mode（またはnon-loopback identity-aware reverse proxies用の `trusted-proxy`）を明示的に選べます。本当にloopbackを開放したいなら、configで `gateway.auth.mode: "none"` を明示設定してください。Doctorはいつでもtokenを生成できます: `openclaw doctor --generate-gateway-token`。

  </Accordion>

  <Accordion title="configを変更したあと再起動は必要ですか？">
    Gatewayはconfigを監視し、hot-reloadをサポートしています:

    - `gateway.reload.mode: "hybrid"`（デフォルト）: 安全な変更はhot-apply、重要なものはrestart
    - `hot`, `restart`, `off` もサポートされています

  </Accordion>

  <Accordion title="面白いCLI taglineを無効にするには？">
    configで `cli.banner.taglineMode` を設定してください:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: tagline textを非表示にしますが、bannerのtitle/version lineは残します。
    - `default`: 毎回 `All your chats, one OpenClaw.` を使います。
    - `random`: 季節ネタを含むローテーションtaglines（デフォルト挙動）。
    - banner自体を消したい場合は、env `OPENCLAW_HIDE_BANNER=1` を設定してください。

  </Accordion>

  <Accordion title="web search（および web fetch）を有効にするには？">
    `web_fetch` はAPI keyなしで動作します。`web_search` は選択した
    providerに依存します:

    - Brave、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Perplexity、TavilyのようなAPIベースproviderには通常どおりのAPI key設定が必要です。
    - Ollama Web Searchはkey不要ですが、設定済みのOllama hostを使い、`ollama signin` が必要です。
    - DuckDuckGoはkey不要ですが、非公式のHTMLベースintegrationです。
    - SearXNGはkey不要/セルフホスト型です。`SEARXNG_BASE_URL` または `plugins.entries.searxng.config.webSearch.baseUrl` を設定してください。

    **推奨:** `openclaw configure --section web` を実行してproviderを選択してください。
    環境変数による代替手段:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` または `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, または `MINIMAX_API_KEY`
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
              provider: "firecrawl", // 任意。自動検出するなら省略
            },
          },
        },
    }
    ```

    provider固有のweb-search configは現在 `plugins.entries.<plugin>.config.webSearch.*` 配下にあります。
    レガシーの `tools.web.search.*` provider pathsも一時的に互換性のため読み込まれますが、新しいconfigには使わないでください。
    Firecrawl web-fetch fallback configは `plugins.entries.firecrawl.config.webFetch.*` 配下にあります。

    注意:

    - allowlistsを使う場合は、`web_search`/`web_fetch`/`x_search` または `group:web` を追加してください。
    - `web_fetch` はデフォルトで有効です（明示的に無効化しない限り）。
    - `tools.web.fetch.provider` を省略した場合、OpenClawは利用可能なcredentialsから最初に準備が整ったfetch fallback providerを自動検出します。現在のbundled providerはFirecrawlです。
    - daemonsは `~/.openclaw/.env`（またはservice environment）からenv varsを読み込みます。

    ドキュメント: [Web tools](/ja-JP/tools/web)。

  </Accordion>

  <Accordion title="config.apply でconfigが消えました。どう復旧し、どう防げますか？">
    `config.apply` は**設定全体**を置き換えます。部分オブジェクトを送ると、それ以外の
    すべてが削除されます。

    復旧方法:

    - バックアップ（gitまたはコピーした `~/.openclaw/openclaw.json`）から復元する。
    - バックアップがなければ、`openclaw doctor` を再実行してchannels/modelsを再設定する。
    - 予期しない動作だった場合は、bug報告を行い、最後に分かっているconfigまたはバックアップを含める。
    - ローカルcoding agentなら、ログや履歴から動作するconfigを再構築できることがよくあります。

    防止方法:

    - 小さな変更には `openclaw config set` を使う。
    - 対話編集には `openclaw configure` を使う。
    - 正確なpathやfield shapeに自信がないときは、まず `config.schema.lookup` を使う。浅いschema nodeと即時child summariesを返してくれるので掘り下げに使えます。
    - 部分的なRPC editsには `config.patch` を使い、`config.apply` は完全なconfig置換にだけ使う。
    - agent runからowner-onlyの `gateway` toolを使っている場合でも、`tools.exec.ask` / `tools.exec.security` への書き込みは引き続き拒否されます（同じ保護されたexec pathsに正規化されるレガシー `tools.bash.*` aliasesを含む）。

    ドキュメント: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/ja-JP/gateway/doctor)。

  </Accordion>

  <Accordion title="中央Gatewayを使い、デバイスごとに専門化したworkerを持つには？">
    一般的なパターンは **1つのGateway**（例 Raspberry Pi） + **nodes** + **agents** です:

    - **Gateway（中央）:** channels（Signal/WhatsApp）、routing、sessionsを所有。
    - **Nodes（デバイス）:** Mac/iOS/Androidが周辺機器として接続し、ローカルtools（`system.run`, `canvas`, `camera`）を公開。
    - **Agents（workers）:** 特定の役割（例「Hetzner ops」「Personal data」）のための別々のbrain/workspace。
    - **Sub-agents:** 並列作業が必要なとき、main agentからバックグラウンド作業をspawn。
    - **TUI:** Gatewayへ接続し、agents/sessionsを切り替え。

    ドキュメント: [Nodes](/ja-JP/nodes), [Remote access](/ja-JP/gateway/remote), [Multi-Agent Routing](/ja-JP/concepts/multi-agent), [Sub-agents](/ja-JP/tools/subagents), [TUI](/web/tui)。

  </Accordion>

  <Accordion title="OpenClaw browserはheadlessで動かせますか？">
    はい。config optionです:

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

    デフォルトは `false`（headful）です。headlessのほうが一部サイトではanti-bot checksを
    引き起こしやすくなります。[Browser](/ja-JP/tools/browser) を参照してください。

    Headlessは**同じChromium engine** を使い、大半のautomation（フォーム、クリック、スクレイピング、ログイン）で動作します。主な違いは:

    - 可視ブラウザウィンドウがない（視覚が必要ならスクリーンショットを使用）。
    - 一部サイトはheadless modeでのautomationにより厳しい（CAPTCHAs、anti-bot）。
      例えばX/Twitterはheadless sessionsをよくブロックします。

  </Accordion>

  <Accordion title="Braveをbrowser controlに使うには？">
    `browser.executablePath` をBraveバイナリ（または任意のChromiumベースbrowser）に設定し、Gatewayを再起動してください。
    完全な設定例は [Browser](/ja-JP/tools/browser#use-brave-or-another-chromium-based-browser) を参照してください。
  </Accordion>
</AccordionGroup>

## リモートGatewayとnodes

<AccordionGroup>
  <Accordion title="Telegram、gateway、nodesの間でcommandsはどう伝播しますか？">
    Telegramメッセージは **gateway** によって処理されます。gatewayがagentを実行し、
    node toolが必要な場合にのみ **Gateway WebSocket** 経由でnodesを呼び出します:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Nodesは受信provider trafficを見ません。受け取るのはnode RPC callsだけです。

  </Accordion>

  <Accordion title="Gatewayがリモートにホストされている場合、agentが自分のコンピューターへアクセスするには？">
    短い答え: **コンピューターをnodeとしてペアリング**してください。Gatewayは別の場所で動きますが、
    Gateway WebSocket経由で、ローカルマシン上の `node.*` tools（screen、camera、system）を
    呼び出せます。

    典型的なセットアップ:

    1. 常時稼働host（VPS/ホームサーバー）でGatewayを動かす。
    2. Gateway hostと自分のコンピューターを同じtailnetに置く。
    3. Gateway WSに到達できることを確認する（tailnet bindまたはSSH tunnel）。
    4. macOS appをローカルで開き、**Remote over SSH** モード（またはdirect tailnet）
       で接続して、nodeとして登録できるようにする。
    5. Gateway上でnodeを承認する:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    別個のTCP bridgeは不要です。nodesはGateway WebSocket経由で接続します。

    セキュリティ注意: macOS nodeをペアリングすると、そのマシン上で `system.run` が可能になります。信頼できるデバイスだけを
    ペアリングし、[Security](/ja-JP/gateway/security) を確認してください。

    ドキュメント: [Nodes](/ja-JP/nodes), [Gateway protocol](/ja-JP/gateway/protocol), [macOS remote mode](/ja-JP/platforms/mac/remote), [Security](/ja-JP/gateway/security)。

  </Accordion>

  <Accordion title="Tailscaleは接続済みなのに返信が来ません。どうすればよいですか？">
    基本を確認してください:

    - Gatewayが動作中か: `openclaw gateway status`
    - Gateway health: `openclaw status`
    - Channel health: `openclaw channels status`

    次にauthとroutingを確認してください:

    - Tailscale Serveを使う場合は、`gateway.auth.allowTailscale` が正しく設定されているか確認。
    - SSH tunnel経由で接続する場合は、ローカルトンネルが起動していて正しいポートを指しているか確認。
    - allowlists（DMまたはgroup）に自分のaccountが含まれていることを確認。

    ドキュメント: [Tailscale](/ja-JP/gateway/tailscale), [Remote access](/ja-JP/gateway/remote), [Channels](/ja-JP/channels)。

  </Accordion>

  <Accordion title="2つのOpenClawインスタンス（local + VPS）を相互に会話させられますか？">
    はい。組み込みの「bot-to-bot」bridgeはありませんが、いくつかの
    信頼性の高い方法で接続できます:

    **最も簡単:** 両方のbotがアクセスできる通常のchat channel（Telegram/Slack/WhatsApp）を使います。
    Bot AからBot Bへメッセージを送り、Bot Bに通常どおり返信させてください。

    **CLI bridge（汎用）:** スクリプトを実行して、もう一方のGatewayを
    `openclaw agent --message ... --deliver` で呼び出し、相手のbotが
    監視しているチャットをtargetにします。片方がリモートVPS上にある場合、そのCLIを
    SSH/Tailscale経由でそのremote Gatewayへ向けてください（[Remote access](/ja-JP/gateway/remote) 参照）。

    例のパターン（target Gatewayへ到達できるマシン上で実行）:

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    ヒント: 2つのbotが無限ループしないよう、mention-only、channel
    allowlists、または「botメッセージには返信しない」ルールを追加してください。

    ドキュメント: [Remote access](/ja-JP/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/ja-JP/tools/agent-send)。

  </Accordion>

  <Accordion title="複数agentのために別々のVPSが必要ですか？">
    いいえ。1つのGatewayで複数agentsをホストでき、それぞれが独自のworkspace、model defaults、
    routingを持てます。これは通常のセットアップであり、agentごとにVPSを動かすより
    はるかに安価で簡単です。

    別々のVPSが必要なのは、厳格な分離（セキュリティ境界）や、共有したくない非常に
    異なるconfigsが必要な場合だけです。そうでなければ、1つのGatewayを保ち、
    複数agentsまたはsub-agentsを使ってください。

  </Accordion>

  <Accordion title="VPSからSSHする代わりに、個人ノートPC上でnodeを使う利点はありますか？">
    はい。リモートGatewayからノートPCへ到達する第一級の方法がnodesであり、
    shell access以上のことができます。GatewayはmacOS/Linux（WindowsはWSL2経由）で動作し、
    軽量です（小さなVPSやRaspberry Pi級マシンで十分です。4 GB RAMあれば余裕があります）ので、一般的な
    セットアップは常時稼働host + ノートPCをnodeにする形です。

    - **受信SSH不要。** NodesはGateway WebSocketへ外向き接続し、device pairingを使います。
    - **より安全な実行制御。** `system.run` はそのノートPC上のnode allowlists/approvalsで制御されます。
    - **より多くのデバイスtools。** Nodesは `system.run` に加えて `canvas`, `camera`, `screen` を公開します。
    - **ローカルbrowser automation。** GatewayはVPS上に置いたまま、ノートPC上のnode host経由でローカルChromeを実行するか、host上のローカルChromeへChrome MCP経由で接続できます。

    SSHは一時的なshell accessには問題ありませんが、継続的なagent workflowsや
    デバイスautomationにはnodesのほうが単純です。

    ドキュメント: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes), [Browser](/ja-JP/tools/browser)。

  </Accordion>

  <Accordion title="nodesはgateway serviceを実行しますか？">
    いいえ。**1 hostにつき1つのgateway** を実行するのが原則です。意図的に分離されたprofilesを動かす場合を除きます（[Multiple gateways](/ja-JP/gateway/multiple-gateways) 参照）。Nodesはgatewayに接続する周辺機器です
    （iOS/Android nodes、またはmenubar appのmacOS「node mode」）。headless node
    hostsやCLI制御については [Node host CLI](/cli/node) を参照してください。

    `gateway`, `discovery`, `canvasHost` の変更には完全な再起動が必要です。

  </Accordion>

  <Accordion title="configを適用するAPI / RPC手段はありますか？">
    はい。

    - `config.schema.lookup`: 書き込む前に、浅いschema node、対応するUI hint、即時child summaries付きで1つのconfig subtreeを調べる
    - `config.get`: 現在のsnapshot + hashを取得する
    - `config.patch`: 安全な部分更新（多くのRPC editsで推奨）
    - `config.apply`: config全体を検証して置換し、その後restart
    - owner-onlyの `gateway` runtime toolは、依然として `tools.exec.ask` / `tools.exec.security` の書き換えを拒否します。レガシーの `tools.bash.*` aliasesは同じ保護されたexec pathsに正規化されます

  </Accordion>

  <Accordion title="初回インストール向けの最小限まともなconfig">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    これでworkspaceを設定し、botを起動できる相手を制限します。

  </Accordion>

  <Accordion title="VPSにTailscaleを設定し、Macから接続するには？">
    最小手順:

    1. **VPSでinstall + login**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Macでinstall + login**
       - Tailscale appを使い、同じtailnetにサインインします。
    3. **MagicDNSを有効化（推奨）**
       - Tailscale admin consoleでMagicDNSを有効化し、VPSに安定した名前を付けます。
    4. **tailnet hostnameを使う**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    SSHなしでControl UIを使いたい場合は、VPSでTailscale Serveを使ってください:

    ```bash
    openclaw gateway --tailscale serve
    ```

    これによりgatewayはloopback bindのまま、Tailscale経由でHTTPS公開されます。[Tailscale](/ja-JP/gateway/tailscale) を参照してください。

  </Accordion>

  <Accordion title="Mac nodeをリモートGateway（Tailscale Serve）へ接続するには？">
    Serveは **Gateway Control UI + WS** を公開します。nodesも同じGateway WS endpoint経由で接続します。

    推奨セットアップ:

    1. **VPS + Macが同じtailnetにあることを確認**。
    2. **macOS appをRemote modeで使用**（SSH targetにはtailnet hostnameを使えます）。
       appがGateway portをトンネルし、nodeとして接続します。
    3. gateway上で**nodeを承認**:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    ドキュメント: [Gateway protocol](/ja-JP/gateway/protocol), [Discovery](/ja-JP/gateway/discovery), [macOS remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="2台目のノートPCにはインストールすべきですか？ それともnode追加だけでよいですか？">
    2台目のノートPCで必要なのが **ローカルtools**（screen/camera/exec）だけなら、**node** として追加してください。これなら単一のGatewayを維持でき、configの重複を避けられます。ローカルnode toolsは現在macOSのみですが、今後他OSにも拡張予定です。

    2つ目のGatewayをインストールするのは、**厳格な分離** や完全に独立した2つのbotが必要な場合だけです。

    ドキュメント: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes), [Multiple gateways](/ja-JP/gateway/multiple-gateways)。

  </Accordion>
</AccordionGroup>

## Env varsと .env 読み込み

<AccordionGroup>
  <Accordion title="OpenClawは環境変数をどう読み込みますか？">
    OpenClawは親process（shell、launchd/systemd、CIなど）からenv varsを読み取り、さらに次も読み込みます:

    - 現在の作業ディレクトリの `.env`
    - `~/.openclaw/.env`（別名 `$OPENCLAW_STATE_DIR/.env`）のグローバルfallback `.env`

    どちらの `.env` ファイルも、既存のenv varsを上書きしません。

    configでinline env varsを定義することもできます（process envに存在しない場合にのみ適用）:

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    完全な優先順位と取得元については [/environment](/ja-JP/help/environment) を参照してください。

  </Accordion>

  <Accordion title="Gatewayをservice経由で起動したらenv varsが消えました。どうすればよいですか？">
    よくある修正は2つあります:

    1. 欠けているkeysを `~/.openclaw/.env` に入れる。そうすればserviceがshell envを継承しなくても拾われます。
    2. shell importを有効化する（利便性のためのオプトイン）:

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

    これによりlogin shellを実行し、期待される不足キーだけを取り込みます（上書きはしません）。環境変数相当:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`。

  </Accordion>

  <Accordion title='COPILOT_GITHUB_TOKEN を設定したのに、models status に "Shell env: off." と表示されるのはなぜですか？'>
    `openclaw models status` は、**shell env import** が有効かどうかを報告します。"Shell env: off"
    はenv varsが不足していることを意味しません。OpenClawが
    login shellを自動読み込みしない、という意味です。

    Gatewayがservice（launchd/systemd）として動いている場合、shell
    environmentを継承しません。次のいずれかで修正してください:

    1. tokenを `~/.openclaw/.env` に入れる:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. またはshell import（`env.shellEnv.enabled: true`）を有効化する。
    3. またはconfigの `env` blockに追加する（不足時のみ適用）。

    その後gatewayを再起動して再確認してください:

    ```bash
    openclaw models status
    ```

    Copilot tokensは `COPILOT_GITHUB_TOKEN`（加えて `GH_TOKEN` / `GITHUB_TOKEN`）から読み取られます。
    [/concepts/model-providers](/ja-JP/concepts/model-providers) と [/environment](/ja-JP/help/environment) を参照してください。

  </Accordion>
</AccordionGroup>

## Sessionsと複数チャット

<AccordionGroup>
  <Accordion title="新しい会話を始めるには？">
    `/new` または `/reset` を単独メッセージとして送ってください。[Session management](/ja-JP/concepts/session) を参照してください。
  </Accordion>

  <Accordion title="/new を送らないとsessionは自動的にリセットされますか？">
    Sessionsは `session.idleMinutes` のあと失効できますが、これは**デフォルトで無効**です（デフォルト **0**）。
    idle expiryを有効にするには正の値を設定してください。有効な場合、アイドル期間後の**次の**
    メッセージで、そのchat keyに対して新しいsession idが始まります。
    これはtranscriptsを削除しません。新しいsessionを始めるだけです。

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="OpenClawインスタンスのチーム（1人のCEOと多数のagents）を作れますか？">
    はい。**multi-agent routing** と **sub-agents** により可能です。1つの調整役
    agentと、独自のworkspacesとmodelsを持つ複数のworker agentsを作れます。

    ただし、これは**楽しい実験**と見るのが最善です。トークン消費が大きく、
    ひとつのbotを別々のsessionsで使うより効率が低いことも多いです。私たちが
    想定している典型モデルは、ひとつのbotと会話し、並列作業には異なるsessionsを使う形です。その
    botは必要に応じてsub-agentsもspawnできます。

    ドキュメント: [Multi-agent routing](/ja-JP/concepts/multi-agent), [Sub-agents](/ja-JP/tools/subagents), [Agents CLI](/cli/agents)。

  </Accordion>

  <Accordion title="なぜ作業途中でcontextが切り詰められたのですか？ 防ぐには？">
    Session contextはモデルのwindowに制限されます。長いチャット、大きなtool outputs、多数の
    filesによって、compactionやtruncationが発生することがあります。

    役立つ対策:

    - 現在の状態を要約し、ファイルへ書くようbotに依頼する。
    - 長いタスクの前に `/compact` を使い、話題を変えるときは `/new` を使う。
    - 重要なcontextはworkspaceに置き、botに読み戻させる。
    - 長い作業や並列作業にはsub-agentsを使い、メインチャットを小さく保つ。
    - 頻繁に起こるなら、より大きなcontext windowのモデルを選ぶ。

  </Accordion>

  <Accordion title="OpenClawを完全にリセットしつつ、インストールは残すには？">
    resetコマンドを使ってください:

    ```bash
    openclaw reset
    ```

    非対話型の完全リセット:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    そのあとセットアップを再実行してください:

    ```bash
    openclaw onboard --install-daemon
    ```

    注意:

    - 既存configがある場合、オンボーディングでも **Reset** を提案します。[Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。
    - profiles（`--profile` / `OPENCLAW_PROFILE`）を使っていた場合は、各state dirをリセットしてください（デフォルトは `~/.openclaw-<profile>`）。
    - Dev reset: `openclaw gateway --dev --reset`（dev専用。dev config + credentials + sessions + workspaceを消去）。

  </Accordion>

  <Accordion title='"context too large" errors が出ます。どうリセットまたはcompactすればよいですか？'>
    次のいずれかを使ってください:

    - **Compact**（会話は維持しつつ古いターンを要約）:

      ```
      /compact
      ```

      または、要約の方針を指定する `/compact <instructions>`。

    - **Reset**（同じchat keyに対して新しいsession ID）:

      ```
      /new
      /reset
      ```

    それでも繰り返す場合:

    - **session pruning**（`agents.defaults.contextPruning`）を有効化または調整して古いtool outputを削減する。
    - より大きなcontext windowを持つモデルを使う。

    ドキュメント: [Compaction](/ja-JP/concepts/compaction), [Session pruning](/ja-JP/concepts/session-pruning), [Session management](/ja-JP/concepts/session)。

  </Accordion>

  <Accordion title='"LLM request rejected: messages.content.tool_use.input field required" と表示されるのはなぜですか？'>
    これはproviderの検証エラーです。モデルが必須の
    `input` なしで `tool_use` blockを出力しました。通常はsession historyが古いか壊れていることを意味します（長いthreadの後やtool/schema変更後によく起こります）。

    修正: `/new`（単独メッセージ）で新しいsessionを開始してください。

  </Accordion>

  <Accordion title="なぜ30分ごとにheartbeatメッセージが来るのですか？">
    Heartbeatsはデフォルトで **30m** ごと（OAuth auth使用時は **1h** ごと）に実行されます。調整または無効化できます:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // または無効化するなら "0m"
          },
        },
      },
    }
    ```

    `HEARTBEAT.md` が存在しても実質的に空（空行と `# Heading` のようなmarkdown
    headersのみ）なら、OpenClawはAPI calls節約のためheartbeat実行をスキップします。
    ファイルが存在しない場合、heartbeatは依然として実行され、モデルが何をするか決めます。

    agentごとのoverrideは `agents.list[].heartbeat` を使います。ドキュメント: [Heartbeat](/ja-JP/gateway/heartbeat)。

  </Accordion>

  <Accordion title='WhatsApp groupに「bot account」を追加する必要がありますか？'>
    いいえ。OpenClawは**あなた自身のアカウント**で動作するため、そのgroupにあなたがいればOpenClawも見えます。
    デフォルトでは、送信者を許可するまでgroup repliesはブロックされます（`groupPolicy: "allowlist"`）。

    group repliesをトリガーできるのを**自分だけ**にしたい場合:

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

  <Accordion title="WhatsApp groupのJIDはどう取得しますか？">
    Option 1（最速）: ログを追いながら、そのgroupでテストメッセージを送ってください:

    ```bash
    openclaw logs --follow --json
    ```

    `@g.us` で終わる `chatId`（または `from`）を探してください。例:
    `1234567890-1234567890@g.us`。

    Option 2（既に設定済み/allowlistedの場合）: configからgroupsを一覧表示:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    ドキュメント: [WhatsApp](/ja-JP/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs)。

  </Accordion>

  <Accordion title="OpenClawがgroupで返信しないのはなぜですか？">
    よくある原因は2つです:

    - mention gatingがオン（デフォルト）。botを@mentionする必要があります（または `mentionPatterns` に一致させる）。
    - `channels.whatsapp.groups` を `"*"` なしで設定しており、そのgroupがallowlistに入っていない。

    [Groups](/ja-JP/channels/groups) と [Group messages](/ja-JP/channels/group-messages) を参照してください。

  </Accordion>

  <Accordion title="groups/threadsはDMsとcontextを共有しますか？">
    direct chatsはデフォルトでmain sessionにまとめられます。groups/channelsは独自のsession keysを持ち、Telegram topics / Discord threadsも別セッションです。[Groups](/ja-JP/channels/groups) と [Group messages](/ja-JP/channels/group-messages) を参照してください。
  </Accordion>

  <Accordion title="workspacesとagentsはいくつ作成できますか？">
    厳密な上限はありません。数十（場合によっては数百）でも問題ありませんが、次に注意してください:

    - **ディスク増加:** sessions + transcripts は `~/.openclaw/agents/<agentId>/sessions/` 配下に保存されます。
    - **トークンコスト:** agentが増えるほど同時モデル使用量が増えます。
    - **運用負荷:** agentごとのauth profiles、workspaces、channel routing。

    ヒント:

    - agentごとに1つの**アクティブ**workspaceを維持する（`agents.defaults.workspace`）。
    - ディスクが増えたら古いsessionsを整理する（JSONLやstore entriesを削除）。
    - `openclaw doctor` を使って迷子のworkspacesやprofile mismatchを見つける。

  </Accordion>

  <Accordion title="複数のbotsやチャットを同時に動かせますか（Slack）？ どうセットアップすべきですか？">
    はい。**Multi-Agent Routing** を使えば、複数の分離されたagentsを実行し、
    受信メッセージをchannel/account/peerごとにルーティングできます。Slackはchannelとしてサポートされ、特定agentsへバインドできます。

    Browser accessは強力ですが、「人間ができることを何でもできる」わけではありません。anti-bot、CAPTCHAs、MFAは依然として
    automationを妨げることがあります。最も信頼性の高いbrowser controlには、host上のローカルChrome MCPを使うか、
    実際にbrowserが動作しているマシン上でCDPを使ってください。

    ベストプラクティスのセットアップ:

    - 常時稼働のGateway host（VPS/Mac mini）。
    - 役割ごとに1 agent（bindings）。
    - それらのagentsにバインドされたSlack channel(s)。
    - 必要に応じてChrome MCPまたはnode経由のローカルbrowser。

    ドキュメント: [Multi-Agent Routing](/ja-JP/concepts/multi-agent), [Slack](/ja-JP/channels/slack),
    [Browser](/ja-JP/tools/browser), [Nodes](/ja-JP/nodes)。

  </Accordion>
</AccordionGroup>

## Models: defaults、selection、aliases、switching

<AccordionGroup>
  <Accordion title='「default model」とは何ですか？'>
    OpenClawのdefault modelは、次で設定したものです:

    ```
    agents.defaults.model.primary
    ```

    Modelsは `provider/model` として参照されます（例: `openai/gpt-5.4`）。providerを省略すると、OpenClawはまずaliasを試し、次にその正確なmodel idに対する一意のconfigured-provider matchを試し、その後でのみ非推奨の互換性経路としてconfigured default providerへフォールバックします。そのproviderが設定済みdefault modelをもう公開していない場合、OpenClawは古い削除済みprovider defaultを出す代わりに、最初のconfigured provider/modelへフォールバックします。それでも、**明示的に** `provider/model` を設定するべきです。

  </Accordion>

  <Accordion title="おすすめのmodelは何ですか？">
    **推奨デフォルト:** provider stackで使える最新世代の最も強いmodelを使ってください。
    **tools有効または信頼できない入力を扱うagents向け:** コストよりモデル性能を優先してください。
    **日常/低リスクのチャット向け:** より安価なfallback modelsを使い、agent roleごとにルーティングしてください。

    MiniMaxには専用ドキュメントがあります: [MiniMax](/ja-JP/providers/minimax) と
    [Local models](/ja-JP/gateway/local-models)。

    目安として、高リスクの作業には**払える範囲で最良のmodel** を使い、日常チャットや要約には
    安価なmodelを使ってください。agentごとにmodelsをルーティングし、長いタスクはsub-agentsで
    並列化できます（sub-agentごとにトークンを消費します）。[Models](/ja-JP/concepts/models) と
    [Sub-agents](/ja-JP/tools/subagents) を参照してください。

    強い警告: 弱い/過度に量子化されたmodelsは、prompt
    injectionや危険な挙動により脆弱です。[Security](/ja-JP/gateway/security) を参照してください。

    追加情報: [Models](/ja-JP/concepts/models)。

  </Accordion>

  <Accordion title="configを壊さずにmodelsを切り替えるには？">
    **model commands** を使うか、**model** fieldsだけを編集してください。config全体の置換は避けてください。

    安全な方法:

    - チャット内の `/model`（高速、sessionごと）
    - `openclaw models set ...`（model configだけを更新）
    - `openclaw configure --section model`（対話的）
    - `~/.openclaw/opencl