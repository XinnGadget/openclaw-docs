---
read_when:
    - 一般的なセットアップ、インストール、オンボーディング、またはランタイムサポートに関する質問への回答
    - より深いデバッグに進む前に、ユーザーから報告された問題をトリアージすること
summary: OpenClaw のセットアップ、設定、使用方法に関するよくある質問
title: よくある質問
x-i18n:
    generated_at: "2026-04-12T23:28:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: d2a78d0fea9596625cc2753e6dc8cc42c2379a3a0c91729265eee0261fe53eaa
    source_path: help/faq.md
    workflow: 15
---

# よくある質問

実環境でのセットアップに関する簡潔な回答と、より詳しいトラブルシューティング（ローカル開発、VPS、マルチエージェント、OAuth/API キー、モデルフェイルオーバー）。ランタイム診断については [トラブルシューティング](/ja-JP/gateway/troubleshooting) を参照してください。完全な設定リファレンスについては [設定](/ja-JP/gateway/configuration) を参照してください。

## 何か壊れているときの最初の 60 秒

1. **クイックステータス（最初の確認）**

   ```bash
   openclaw status
   ```

   高速なローカル要約: OS + 更新、gateway/service の到達性、agents/sessions、provider 設定 + ランタイムの問題（gateway に到達できる場合）。

2. **共有しやすいレポート（安全に共有可能）**

   ```bash
   openclaw status --all
   ```

   ログ末尾付きの読み取り専用診断（トークンはマスク済み）。

3. **デーモン + ポート状態**

   ```bash
   openclaw gateway status
   ```

   supervisor ランタイムと RPC 到達性、プローブ対象 URL、サービスが使用した可能性の高い設定を表示します。

4. **詳細プローブ**

   ```bash
   openclaw status --deep
   ```

   サポートされている場合はチャネルプローブを含む、ライブの gateway ヘルスプローブを実行します
   （到達可能な gateway が必要です）。[Health](/ja-JP/gateway/health) を参照してください。

5. **最新ログを追跡**

   ```bash
   openclaw logs --follow
   ```

   RPC がダウンしている場合は、代わりに次を使用します。

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   ファイルログは service ログとは別です。[Logging](/ja-JP/logging) と [トラブルシューティング](/ja-JP/gateway/troubleshooting) を参照してください。

6. **Doctor を実行（修復）**

   ```bash
   openclaw doctor
   ```

   設定/状態を修復・移行し、ヘルスチェックを実行します。[Doctor](/ja-JP/gateway/doctor) を参照してください。

7. **Gateway スナップショット**

   ```bash
   openclaw health --json
   openclaw health --verbose   # エラー時に対象 URL + 設定パスを表示
   ```

   実行中の gateway に完全なスナップショットを要求します（WS 専用）。[Health](/ja-JP/gateway/health) を参照してください。

## クイックスタートと初回セットアップ

<AccordionGroup>
  <Accordion title="行き詰まりました。最速で抜け出す方法は？">
    **あなたのマシンを見られる** ローカル AI エージェントを使ってください。これは Discord で質問するよりはるかに効果的です。なぜなら、「行き詰まった」というケースの多くは、リモートの支援者には確認できない **ローカルの設定や環境の問題** だからです。

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    これらのツールは、リポジトリの読み取り、コマンド実行、ログ確認、そしてマシンレベルのセットアップ（PATH、services、permissions、auth files）の修正支援ができます。ハッカブルな（git）インストールを使って、**完全なソースチェックアウト** を渡してください。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    これにより OpenClaw は **git チェックアウトから** インストールされるため、エージェントがコードとドキュメントを読み、実行中の正確なバージョンをもとに判断できます。後でインストーラーを `--install-method git` なしで再実行すれば、いつでも stable に戻せます。

    ヒント: エージェントには、必要なコマンドだけを実行する前提で、修正を **計画して監督**（ステップごと）してもらってください。そうすれば変更を小さく保てて、監査もしやすくなります。

    実際のバグや修正を見つけたら、GitHub issue を作成するか PR を送ってください:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    助けを求めるときは、まず次のコマンドから始めてください（出力を共有してください）:

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    それぞれの役割:

    - `openclaw status`: gateway/agent の健全性 + 基本設定のクイックスナップショット。
    - `openclaw models status`: provider 認証 + モデルの利用可能性を確認します。
    - `openclaw doctor`: よくある設定/状態の問題を検証し、修復します。

    その他の便利な CLI 確認コマンド: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`。

    クイックデバッグループ: [何か壊れているときの最初の 60 秒](#何か壊れているときの最初の-60-秒)。
    インストールドキュメント: [Install](/ja-JP/install), [Installer flags](/ja-JP/install/installer), [Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="Heartbeat がスキップされ続けます。スキップ理由は何を意味しますか？">
    よくある Heartbeat のスキップ理由:

    - `quiet-hours`: 設定された active-hours の時間帯外
    - `empty-heartbeat-file`: `HEARTBEAT.md` は存在するが、空白またはヘッダーだけのひな形しか含まれていない
    - `no-tasks-due`: `HEARTBEAT.md` の task モードが有効だが、どのタスク間隔もまだ期限に達していない
    - `alerts-disabled`: heartbeat の可視性がすべて無効（`showOk`、`showAlerts`、`useIndicator` がすべてオフ）

    task モードでは、期限タイムスタンプは実際の heartbeat 実行が完了した後にのみ進みます。
    スキップされた実行ではタスクは完了扱いになりません。

    ドキュメント: [Heartbeat](/ja-JP/gateway/heartbeat), [Automation & Tasks](/ja-JP/automation)。

  </Accordion>

  <Accordion title="OpenClaw をインストールしてセットアップする推奨方法は？">
    リポジトリでは、ソースから実行し、オンボーディングを使うことを推奨しています。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    ウィザードは UI アセットも自動でビルドできます。オンボーディング後は、通常 port **18789** で Gateway を実行します。

    ソースから（コントリビューター/開発者向け）:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # 初回実行時に UI の依存関係を自動インストール
    openclaw onboard
    ```

    まだグローバルインストールしていない場合は、`pnpm openclaw onboard` で実行してください。

  </Accordion>

  <Accordion title="オンボーディング後にダッシュボードを開くにはどうすればよいですか？">
    ウィザードは、オンボーディング直後にクリーンな（トークン化されていない）ダッシュボード URL でブラウザを開き、概要にもそのリンクを表示します。そのタブは開いたままにしてください。起動しなかった場合は、同じマシン上で表示された URL をコピーして貼り付けてください。
  </Accordion>

  <Accordion title="localhost とリモートで、ダッシュボードの認証方法はどう違いますか？">
    **Localhost（同じマシン）:**

    - `http://127.0.0.1:18789/` を開きます。
    - shared-secret auth を求められた場合は、設定済みの token または password を Control UI の設定に貼り付けます。
    - token の取得元: `gateway.auth.token`（または `OPENCLAW_GATEWAY_TOKEN`）。
    - password の取得元: `gateway.auth.password`（または `OPENCLAW_GATEWAY_PASSWORD`）。
    - まだ shared secret が設定されていない場合は、`openclaw doctor --generate-gateway-token` で token を生成します。

    **localhost ではない場合:**

    - **Tailscale Serve**（推奨）: bind loopback のまま `openclaw gateway --tailscale serve` を実行し、`https://<magicdns>/` を開きます。`gateway.auth.allowTailscale` が `true` なら、identity headers が Control UI/WebSocket auth を満たします（shared secret を貼り付ける必要はありません。信頼された gateway host を前提とします）。ただし、HTTP API は private-ingress `none` または trusted-proxy HTTP auth を意図的に使わない限り、引き続き shared-secret auth が必要です。
      同じクライアントからの不正な同時 Serve 認証試行は、failed-auth limiter が記録する前に直列化されるため、2 回目の不正な再試行ではすでに `retry later` が表示されることがあります。
    - **Tailnet bind**: `openclaw gateway --bind tailnet --token "<token>"` を実行する（または password auth を設定する）→ `http://<tailscale-ip>:18789/` を開く → ダッシュボード設定に対応する shared secret を貼り付ける。
    - **Identity-aware reverse proxy**: Gateway を非 loopback の trusted proxy の背後に置いたまま、`gateway.auth.mode: "trusted-proxy"` を設定してから、proxy URL を開きます。
    - **SSH トンネル**: `ssh -N -L 18789:127.0.0.1:18789 user@host` の後に `http://127.0.0.1:18789/` を開きます。トンネル経由でも shared-secret auth は適用されるので、求められたら設定済みの token または password を貼り付けてください。

    bind モードと認証の詳細は [Dashboard](/web/dashboard) と [Web surfaces](/web) を参照してください。

  </Accordion>

  <Accordion title="チャット承認に exec approval 設定が 2 つあるのはなぜですか？">
    それぞれ制御する層が異なります。

    - `approvals.exec`: 承認プロンプトをチャット宛先へ転送します
    - `channels.<channel>.execApprovals`: そのチャネルを exec approvals 用のネイティブ承認クライアントとして動作させます

    ホストの exec policy が引き続き実際の承認ゲートです。チャット設定は、承認プロンプトをどこに表示するか、そして人がどう応答できるかを制御するだけです。

    多くのセットアップでは、**両方は不要** です。

    - チャットがすでに commands と replies をサポートしているなら、同じチャットでの `/approve` は共有パスを通じて機能します。
    - サポートされたネイティブチャネルが approver を安全に推測できる場合、OpenClaw は `channels.<channel>.execApprovals.enabled` が未設定または `"auto"` のときに、DM-first のネイティブ承認を自動有効化します。
    - ネイティブの承認カード/ボタンが利用可能な場合、そのネイティブ UI が主要な経路です。ツール結果がチャット承認を利用できない、または手動承認だけが唯一の手段だと示した場合にのみ、エージェントは手動の `/approve` コマンドを含めるべきです。
    - `approvals.exec` は、プロンプトを他のチャットや明示的な運用ルームにも転送する必要がある場合にのみ使用してください。
    - `channels.<channel>.execApprovals.target: "channel"` または `"both"` は、承認プロンプトを元のルーム/トピックにも明示的に投稿したい場合にのみ使用してください。
    - Plugin approvals はさらに別です。デフォルトでは同じチャットでの `/approve` を使い、任意で `approvals.plugin` 転送があり、一部のネイティブチャネルだけがその上に plugin-approval-native の処理を維持します。

    要するに、転送はルーティング用、ネイティブクライアント設定はチャネル固有のより豊かな UX 用です。
    [Exec Approvals](/ja-JP/tools/exec-approvals) を参照してください。

  </Accordion>

  <Accordion title="必要なランタイムは何ですか？">
    Node **>= 22** が必要です。`pnpm` を推奨します。Gateway には Bun は **推奨されません**。
  </Accordion>

  <Accordion title="Raspberry Pi で動きますか？">
    はい。Gateway は軽量です。ドキュメントでは、個人利用なら **512MB-1GB RAM**、**1 core**、約 **500MB** のディスクで十分とされており、**Raspberry Pi 4 で動作可能** と明記されています。

    もう少し余裕がほしい場合（ログ、メディア、他のサービス）、**2GB を推奨** しますが、
    これは厳密な最小要件ではありません。

    ヒント: 小型の Pi/VPS で Gateway をホストし、ノート PC やスマートフォン上の **Node** をペアリングして、
    ローカルの screen/camera/canvas やコマンド実行を行えます。[Nodes](/ja-JP/nodes) を参照してください。

  </Accordion>

  <Accordion title="Raspberry Pi へのインストールのコツはありますか？">
    短く言うと、動きますが、多少の粗さはあります。

    - **64-bit** OS を使い、Node >= 22 を維持してください。
    - ログを確認しやすく、すばやく更新できるように、**ハッカブルな（git）インストール** を優先してください。
    - channels/Skills なしで始め、1 つずつ追加してください。
    - 変なバイナリ問題に当たった場合、通常は **ARM compatibility** の問題です。

    ドキュメント: [Linux](/ja-JP/platforms/linux), [Install](/ja-JP/install)。

  </Accordion>

  <Accordion title="「wake up my friend」で止まる / オンボーディングが hatch しません。どうすればよいですか？">
    この画面は、Gateway に到達できて認証済みであることに依存します。TUI は初回 hatch 時に
    「Wake up, my friend!」も自動送信します。この行が表示されて **応答がなく**、
    トークンが 0 のままなら、agent は一度も実行されていません。

    1. Gateway を再起動します:

    ```bash
    openclaw gateway restart
    ```

    2. ステータス + 認証を確認します:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. それでも止まる場合は、次を実行します:

    ```bash
    openclaw doctor
    ```

    Gateway がリモートにある場合は、トンネル/Tailscale 接続が有効であり、
    UI が正しい Gateway を指していることを確認してください。[Remote access](/ja-JP/gateway/remote) を参照してください。

  </Accordion>

  <Accordion title="セットアップを新しいマシン（Mac mini）に移行し、オンボーディングをやり直さずに済ませられますか？">
    はい。**state directory** と **workspace** をコピーしてから、Doctor を 1 回実行してください。これにより、
    **両方の場所** をコピーする限り、ボットを「まったく同じ状態」（memory、session history、auth、channel
    state）に保てます。

    1. 新しいマシンに OpenClaw をインストールします。
    2. 古いマシンから `$OPENCLAW_STATE_DIR`（デフォルト: `~/.openclaw`）をコピーします。
    3. workspace（デフォルト: `~/.openclaw/workspace`）をコピーします。
    4. `openclaw doctor` を実行し、Gateway service を再起動します。

    これにより、設定、認証プロファイル、WhatsApp の認証情報、セッション、メモリが保持されます。remote mode の場合は、gateway host がセッションストアとワークスペースを保持することを忘れないでください。

    **重要:** workspace だけを GitHub に commit/push している場合、バックアップしているのは **memory + bootstrap files** だけであり、**セッション履歴や認証** は含まれません。これらは `~/.openclaw/` 配下にあります（たとえば `~/.openclaw/agents/<agentId>/sessions/`）。

    関連: [Migrating](/ja-JP/install/migrating), [ディスク上の保存場所](#ディスク上の保存場所),
    [Agent workspace](/ja-JP/concepts/agent-workspace), [Doctor](/ja-JP/gateway/doctor),
    [Remote mode](/ja-JP/gateway/remote)。

  </Accordion>

  <Accordion title="最新バージョンの新機能はどこで確認できますか？">
    GitHub changelog を確認してください:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    最新の項目は先頭にあります。先頭のセクションに **Unreleased** とある場合、その次の日付付き
    セクションが最新のリリース版です。項目は **Highlights**、**Changes**、および
    **Fixes** ごとに分類されています（必要に応じて docs/other セクションもあります）。

  </Accordion>

  <Accordion title="docs.openclaw.ai にアクセスできません（SSL エラー）">
    一部の Comcast/Xfinity 接続では、Xfinity
    Advanced Security により `docs.openclaw.ai` が誤ってブロックされます。無効化するか `docs.openclaw.ai` を許可リストに追加してから再試行してください。
    解除に協力するには、こちらから報告してください: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status)。

    それでもサイトにアクセスできない場合、ドキュメントは GitHub にもミラーされています:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="stable と beta の違い">
    **Stable** と **beta** は別のコードラインではなく、**npm dist-tags** です。

    - `latest` = stable
    - `beta` = テスト用の早期ビルド

    通常、stable リリースはまず **beta** に入り、その後、明示的な
    昇格ステップによって同じバージョンが `latest` に移されます。メンテナーは必要に応じて
    直接 `latest` に公開することもできます。そのため、昇格後は beta と stable が
    **同じバージョン** を指すことがあります。

    変更内容はこちらで確認できます:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    インストール用ワンライナーと beta と dev の違いについては、下のアコーディオンを参照してください。

  </Accordion>

  <Accordion title="beta 版をインストールする方法と、beta と dev の違いは何ですか？">
    **Beta** は npm dist-tag の `beta` です（昇格後は `latest` と同じになる場合があります）。
    **Dev** は `main` の先頭が移動し続けるもの（git）で、公開時には npm dist-tag の `dev` が使われます。

    ワンライナー（macOS/Linux）:

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windows インストーラー（PowerShell）:
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    詳細: [Development channels](/ja-JP/install/development-channels) と [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="最新の変更を試すにはどうすればよいですか？">
    方法は 2 つあります。

    1. **Dev channel（git checkout）:**

    ```bash
    openclaw update --channel dev
    ```

    これにより `main` ブランチに切り替わり、ソースから更新されます。

    2. **Hackable install（インストーラーサイトから）:**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    これにより編集可能なローカルリポジトリが手に入り、その後は git 経由で更新できます。

    手動でクリーンに clone したい場合は、次を使ってください:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    ドキュメント: [Update](/cli/update), [Development channels](/ja-JP/install/development-channels),
    [Install](/ja-JP/install)。

  </Accordion>

  <Accordion title="インストールとオンボーディングには通常どれくらいかかりますか？">
    おおよその目安:

    - **Install:** 2〜5 分
    - **Onboarding:** 設定する channels/models の数に応じて 5〜15 分

    固まる場合は [Installer stuck](#クイックスタートと初回セットアップ)
    と [行き詰まりました。最速で抜け出す方法は？](#クイックスタートと初回セットアップ) の高速デバッグループを参照してください。

  </Accordion>

  <Accordion title="インストーラーが止まります。より多くの情報を出すにはどうすればよいですか？">
    **詳細出力** 付きでインストーラーを再実行してください:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    verbose 付きの beta インストール:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    ハッカブルな（git）インストールの場合:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Windows（PowerShell）での相当手順:

    ```powershell
    # install.ps1 にはまだ専用の -Verbose フラグはありません。
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    その他のオプション: [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="Windows で git not found または openclaw not recognized と表示されます">
    Windows でよくある問題は 2 つあります。

    **1) npm error spawn git / git not found**

    - **Git for Windows** をインストールし、`git` が PATH 上にあることを確認してください。
    - PowerShell を閉じて再度開き、インストーラーを再実行してください。

    **2) インストール後に openclaw is not recognized と表示される**

    - npm のグローバル bin フォルダーが PATH にありません。
    - パスを確認します:

      ```powershell
      npm config get prefix
      ```

    - そのディレクトリをユーザー PATH に追加してください（Windows では `\bin` サフィックスは不要です。多くの環境では `%AppData%\npm` です）。
    - PATH 更新後に PowerShell を閉じて再度開いてください。

    最もスムーズな Windows セットアップを望む場合は、ネイティブ Windows ではなく **WSL2** を使ってください。
    ドキュメント: [Windows](/ja-JP/platforms/windows)。

  </Accordion>

  <Accordion title="Windows の exec 出力で中国語が文字化けします。どうすればよいですか？">
    これは通常、ネイティブ Windows シェルでのコンソールコードページ不一致です。

    症状:

    - `system.run`/`exec` の出力で中国語が文字化けする
    - 同じコマンドが別のターミナルプロファイルでは正しく表示される

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

  <Accordion title="ドキュメントでは疑問が解決しませんでした。どうすればより良い回答を得られますか？">
    **ハッカブルな（git）インストール** を使って、完全なソースとドキュメントをローカルに置いてから、
    そのフォルダー内でボット（または Claude/Codex）に質問してください。そうすればリポジトリを読み、
    正確に回答できます。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    詳細: [Install](/ja-JP/install) と [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="Linux に OpenClaw をインストールするにはどうすればよいですか？">
    簡単に言うと、Linux ガイドに従ってからオンボーディングを実行してください。

    - Linux の最短手順 + service インストール: [Linux](/ja-JP/platforms/linux)。
    - 完全な手順: [はじめに](/ja-JP/start/getting-started)。
    - インストーラー + 更新: [Install & updates](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="VPS に OpenClaw をインストールするにはどうすればよいですか？">
    どの Linux VPS でも動作します。サーバーにインストールし、その後 SSH/Tailscale で Gateway にアクセスしてください。

    ガイド: [exe.dev](/ja-JP/install/exe-dev), [Hetzner](/ja-JP/install/hetzner), [Fly.io](/ja-JP/install/fly)。
    リモートアクセス: [Gateway remote](/ja-JP/gateway/remote)。

  </Accordion>

  <Accordion title="クラウド/VPS のインストールガイドはどこにありますか？">
    よく使われるプロバイダーをまとめた **hosting hub** があります。1 つ選んでガイドに従ってください。

    - [VPS hosting](/ja-JP/vps)（すべてのプロバイダーを 1 か所に集約）
    - [Fly.io](/ja-JP/install/fly)
    - [Hetzner](/ja-JP/install/hetzner)
    - [exe.dev](/ja-JP/install/exe-dev)

    クラウドでの動作方法: **Gateway はサーバー上で実行され**、Control UI（または Tailscale/SSH）を通じて
    ノート PC やスマートフォンからアクセスします。state + workspace はサーバー上に
    あるため、ホストを信頼できる保存元として扱い、バックアップしてください。

    そのクラウド Gateway に **Node**（Mac/iOS/Android/headless）をペアリングして、
    Gateway はクラウドに置いたまま、ノート PC 上のローカル screen/camera/canvas へのアクセスや
    コマンド実行を行うこともできます。

    ハブ: [Platforms](/ja-JP/platforms)。リモートアクセス: [Gateway remote](/ja-JP/gateway/remote)。
    Nodes: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="OpenClaw 自身に自分を更新させられますか？">
    簡単に言うと、**可能ですが推奨はしません**。更新フローでは
    Gateway が再起動されることがあり（アクティブセッションが切断されます）、クリーンな git checkout が必要になる場合があり、
    確認を求めることもあります。より安全なのは、オペレーターとしてシェルから更新を実行することです。

    CLI を使用します:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    どうしてもエージェントから自動化する必要がある場合:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    ドキュメント: [Update](/cli/update), [Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="オンボーディングは実際に何をしますか？">
    `openclaw onboard` は推奨されるセットアップ手順です。**local mode** では次の項目を案内します。

    - **モデル/認証設定**（provider OAuth、API keys、Anthropic setup-token、LM Studio などのローカルモデルオプション）
    - **Workspace** の場所 + bootstrap files
    - **Gateway settings**（bind/port/auth/tailscale）
    - **Channels**（WhatsApp、Telegram、Discord、Mattermost、Signal、iMessage、および QQ Bot のようなバンドル済み channel plugins）
    - **デーモンのインストール**（macOS の LaunchAgent、Linux/WSL2 の systemd user unit）
    - **ヘルスチェック** と **Skills** の選択

    また、設定されたモデルが不明または認証不足の場合に警告も表示します。

  </Accordion>

  <Accordion title="これを実行するには Claude や OpenAI のサブスクリプションが必要ですか？">
    いいえ。OpenClaw は **API keys**（Anthropic/OpenAI/others）でも、
    **ローカル専用モデル** でも実行できるため、データをデバイス上に保持できます。サブスクリプション（Claude
    Pro/Max または OpenAI Codex）は、それらの provider を認証するための任意の方法です。

    OpenClaw における Anthropic では、実用上の区分は次のとおりです。

    - **Anthropic API key**: 通常の Anthropic API 課金
    - **OpenClaw における Claude CLI / Claude subscription auth**: Anthropic のスタッフから、
      この利用方法は再び許可されていると伝えられており、Anthropic が新しい
      ポリシーを公開しない限り、OpenClaw はこの統合における `claude -p`
      の利用を認可されたものとして扱っています

    長期間動作する gateway host では、Anthropic API keys の方が依然として
    より予測しやすいセットアップです。OpenAI Codex OAuth は、OpenClaw のような外部
    ツール向けに明示的にサポートされています。

    OpenClaw はそのほかに、次のようなホスト型のサブスクリプション方式もサポートしています。
    **Qwen Cloud Coding Plan**、**MiniMax Coding Plan**、および
    **Z.AI / GLM Coding Plan**。

    ドキュメント: [Anthropic](/ja-JP/providers/anthropic), [OpenAI](/ja-JP/providers/openai),
    [Qwen Cloud](/ja-JP/providers/qwen),
    [MiniMax](/ja-JP/providers/minimax), [GLM Models](/ja-JP/providers/glm),
    [Local models](/ja-JP/gateway/local-models), [Models](/ja-JP/concepts/models)。

  </Accordion>

  <Accordion title="API key なしで Claude Max subscription を使えますか？">
    はい。

    Anthropic のスタッフから、OpenClaw 形式の Claude CLI 利用は再び許可されていると伝えられているため、Anthropic が新しいポリシーを公開しない限り、OpenClaw は Claude subscription auth と `claude -p` の利用をこの統合で認可されたものとして扱います。最も予測しやすいサーバー側セットアップを望む場合は、代わりに Anthropic API key を使ってください。

  </Accordion>

  <Accordion title="Claude subscription auth（Claude Pro または Max）をサポートしていますか？">
    はい。

    Anthropic のスタッフから、この利用方法は再び許可されていると伝えられているため、Anthropic が新しいポリシーを公開しない限り、OpenClaw は
    Claude CLI の再利用と `claude -p` の利用をこの統合で認可されたものとして扱います。

    Anthropic setup-token も引き続き OpenClaw でサポートされるトークン経路として利用できますが、OpenClaw は現在、利用可能な場合は Claude CLI の再利用と `claude -p` を優先します。
    本番環境やマルチユーザーワークロードでは、Anthropic API key auth の方が依然として
    より安全で予測しやすい選択です。OpenClaw の他のサブスクリプション方式のホスト型
    オプションについては、[OpenAI](/ja-JP/providers/openai)、[Qwen / Model
    Cloud](/ja-JP/providers/qwen)、[MiniMax](/ja-JP/providers/minimax)、および [GLM
    Models](/ja-JP/providers/glm) を参照してください。

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Anthropic から HTTP 429 rate_limit_error が表示されるのはなぜですか？">
これは、現在のウィンドウで **Anthropic の quota/rate limit** を使い切っていることを意味します。**Claude CLI** を使用している場合は、ウィンドウがリセットされるまで待つか、プランをアップグレードしてください。**Anthropic API key** を使用している場合は、Anthropic Console で使用量/課金を確認し、必要に応じて上限を引き上げてください。

    メッセージが具体的に次の場合:
    `Extra usage is required for long context requests`、そのリクエストは
    Anthropic の 1M context beta（`context1m: true`）を使おうとしています。これは、あなたの
    認証情報が long-context 課金の対象である場合にのみ動作します（API key 課金、または
    Extra Usage を有効にした OpenClaw Claude-login 経路）。

    ヒント: **fallback model** を設定すると、provider が rate-limited でも OpenClaw が応答を続けられます。
    [Models](/cli/models)、[OAuth](/ja-JP/concepts/oauth)、および
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/ja-JP/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context) を参照してください。

  </Accordion>

  <Accordion title="AWS Bedrock はサポートされていますか？">
    はい。OpenClaw にはバンドル済みの **Amazon Bedrock (Converse)** provider があります。AWS の env マーカーが存在する場合、OpenClaw はストリーミング/テキスト Bedrock カタログを自動検出し、それを暗黙的な `amazon-bedrock` provider としてマージできます。そうでない場合は、`plugins.entries.amazon-bedrock.config.discovery.enabled` を明示的に有効にするか、手動で provider エントリを追加できます。[Amazon Bedrock](/ja-JP/providers/bedrock) と [Model providers](/ja-JP/providers/models) を参照してください。管理されたキーのフローを好む場合は、Bedrock の前段に OpenAI 互換プロキシを置く方法も引き続き有効です。
  </Accordion>

  <Accordion title="Codex auth はどのように動作しますか？">
    OpenClaw は **OpenAI Code (Codex)** を OAuth（ChatGPT サインイン）経由でサポートします。オンボーディングは OAuth フローを実行でき、適切な場合はデフォルトモデルを `openai-codex/gpt-5.4` に設定します。[Model providers](/ja-JP/concepts/model-providers) と [Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。
  </Accordion>

  <Accordion title="ChatGPT GPT-5.4 で openai/gpt-5.4 が OpenClaw で使えるようにならないのはなぜですか？">
    OpenClaw はこの 2 つの経路を別々に扱います。

    - `openai-codex/gpt-5.4` = ChatGPT/Codex OAuth
    - `openai/gpt-5.4` = 直接の OpenAI Platform API

    OpenClaw では、ChatGPT/Codex サインインは `openai-codex/*` 経路に接続されており、
    直接の `openai/*` 経路には接続されていません。OpenClaw で直接 API 経路を使いたい場合は、
    `OPENAI_API_KEY`（または同等の OpenAI provider 設定）を設定してください。
    OpenClaw で ChatGPT/Codex サインインを使いたい場合は、`openai-codex/*` を使ってください。

  </Accordion>

  <Accordion title="Codex OAuth の上限が ChatGPT Web と異なることがあるのはなぜですか？">
    `openai-codex/*` は Codex OAuth 経路を使用しており、利用可能な quota window は
    OpenAI によって管理され、プランに依存します。実際には、両方が同じアカウントに紐づいていても、
    その上限は ChatGPT の Web サイト/アプリでの体験と異なることがあります。

    OpenClaw は現在見えている provider の usage/quota window を
    `openclaw models status` に表示できますが、ChatGPT Web の
    entitlement を直接 API アクセスに変換したり正規化したりはしません。OpenAI Platform の直接
    課金/上限経路を使いたい場合は、API key とともに `openai/*` を使用してください。

  </Accordion>

  <Accordion title="OpenAI subscription auth（Codex OAuth）をサポートしていますか？">
    はい。OpenClaw は **OpenAI Code (Codex) subscription OAuth** を完全にサポートしています。
    OpenAI は、OpenClaw のような外部ツール/ワークフローでの subscription OAuth 利用を
    明示的に許可しています。オンボーディングで OAuth フローを実行できます。

    [OAuth](/ja-JP/concepts/oauth)、[Model providers](/ja-JP/concepts/model-providers)、および [Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。

  </Accordion>

  <Accordion title="Gemini CLI OAuth はどう設定すればよいですか？">
    Gemini CLI は、`openclaw.json` 内の client id や secret ではなく、**plugin auth flow** を使います。

    手順:

    1. `gemini` が `PATH` 上に来るように Gemini CLI をローカルにインストールします
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. Plugin を有効にします: `openclaw plugins enable google`
    3. ログインします: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. ログイン後のデフォルトモデル: `google-gemini-cli/gemini-3-flash-preview`
    5. リクエストが失敗する場合は、gateway host に `GOOGLE_CLOUD_PROJECT` または `GOOGLE_CLOUD_PROJECT_ID` を設定します

    これにより、OAuth トークンは gateway host 上の auth profiles に保存されます。詳細: [Model providers](/ja-JP/concepts/model-providers)。

  </Accordion>

  <Accordion title="カジュアルなチャットにローカルモデルは適していますか？">
    通常は適していません。OpenClaw には大きなコンテキストと強い安全性が必要であり、小さなモデルでは切り詰めや漏れが発生します。どうしても使う場合は、ローカルで実行できる **できるだけ大きな** モデルビルド（LM Studio）を使用し、[/gateway/local-models](/ja-JP/gateway/local-models) を参照してください。より小さい/量子化されたモデルは prompt-injection リスクを高めます。詳細は [Security](/ja-JP/gateway/security) を参照してください。
  </Accordion>

  <Accordion title="ホスト型モデルのトラフィックを特定リージョン内に維持するにはどうすればよいですか？">
    リージョン固定のエンドポイントを選んでください。OpenRouter は MiniMax、Kimi、GLM 向けに米国内ホストのオプションを提供しているため、データをそのリージョン内に保持したい場合は米国内ホスト版を選択してください。`models.mode: "merge"` を使えば、Anthropic/OpenAI をこれらと並べて一覧表示できるため、選択したリージョン固定 provider を尊重しつつ fallback も利用できます。
  </Accordion>

  <Accordion title="これをインストールするには Mac Mini を買う必要がありますか？">
    いいえ。OpenClaw は macOS または Linux で動作します（Windows は WSL2 経由）。Mac mini は任意です。常時稼働ホストとして購入する人もいますが、小型の VPS、ホームサーバー、または Raspberry Pi クラスのマシンでも動作します。

    Mac が必要なのは **macOS 専用ツール** の場合だけです。iMessage には [BlueBubbles](/ja-JP/channels/bluebubbles)（推奨）を使ってください。BlueBubbles サーバーは任意の Mac で動作し、Gateway は Linux など別の場所で動作できます。ほかの macOS 専用ツールを使いたい場合は、Gateway を Mac 上で動かすか、macOS の Node をペアリングしてください。

    ドキュメント: [BlueBubbles](/ja-JP/channels/bluebubbles), [Nodes](/ja-JP/nodes), [Mac remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="iMessage サポートには Mac mini が必要ですか？">
    Messages にサインインした **何らかの macOS デバイス** が必要です。Mac mini である必要は **ありません**。iMessage には **[BlueBubbles](/ja-JP/channels/bluebubbles)**（推奨）を使ってください。BlueBubbles サーバーは macOS 上で動作し、Gateway は Linux など別の場所で動かせます。

    よくある構成:

    - Gateway は Linux/VPS で動かし、BlueBubbles サーバーは Messages にサインインした任意の Mac で動かす。
    - 最もシンプルな 1 台構成を望むなら、すべてをその Mac 上で動かす。

    ドキュメント: [BlueBubbles](/ja-JP/channels/bluebubbles), [Nodes](/ja-JP/nodes),
    [Mac remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="OpenClaw を動かすために Mac mini を買った場合、MacBook Pro から接続できますか？">
    はい。**Mac mini が Gateway を実行** し、MacBook Pro は
    **Node**（コンパニオンデバイス）として接続できます。Node は Gateway を実行せず、
    そのデバイス上の screen/camera/canvas や `system.run` などの追加機能を提供します。

    よくあるパターン:

    - Gateway は Mac mini 上（常時稼働）。
    - MacBook Pro では macOS アプリまたは Node ホストを実行し、Gateway にペアリングする。
    - 確認には `openclaw nodes status` / `openclaw nodes list` を使う。

    ドキュメント: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="Bun は使えますか？">
    Bun は **推奨されません**。特に WhatsApp と Telegram でランタイムバグが見られます。
    安定した gateway には **Node** を使ってください。

    それでも Bun を試したい場合は、WhatsApp/Telegram なしの非本番 gateway で行ってください。

  </Accordion>

  <Accordion title="Telegram: allowFrom には何を入れますか？">
    `channels.telegram.allowFrom` は **人間の送信者の Telegram user ID**（数値）です。ボットのユーザー名ではありません。

    オンボーディングでは `@username` 入力を受け付けて数値 ID に解決しますが、OpenClaw の認可では数値 ID のみを使用します。

    より安全な方法（サードパーティ bot なし）:

    - bot に DM を送り、その後 `openclaw logs --follow` を実行して `from.id` を確認します。

    公式 Bot API:

    - bot に DM を送り、その後 `https://api.telegram.org/bot<bot_token>/getUpdates` を呼び出して `message.from.id` を確認します。

    サードパーティ（プライバシー性は低い）:

    - `@userinfobot` または `@getidsbot` に DM を送ります。

    [/channels/telegram](/ja-JP/channels/telegram#access-control-and-activation) を参照してください。

  </Accordion>

  <Accordion title="1 つの WhatsApp 番号を複数の OpenClaw インスタンスで、別々の人が使えますか？">
    はい。**マルチエージェントルーティング** を使います。各送信者の WhatsApp **DM**（peer `kind: "direct"`、送信者 E.164 形式 `+15551234567` のようなもの）を別々の `agentId` にバインドすれば、各人が専用の workspace と session store を持てます。返信は引き続き **同じ WhatsApp アカウント** から送られ、DM アクセス制御（`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`）は WhatsApp アカウントごとにグローバルです。[Multi-Agent Routing](/ja-JP/concepts/multi-agent) と [WhatsApp](/ja-JP/channels/whatsapp) を参照してください。
  </Accordion>

  <Accordion title='「高速チャット」エージェントと「コーディング用 Opus」エージェントを実行できますか？'>
    はい。マルチエージェントルーティングを使います。各エージェントに独自のデフォルトモデルを割り当て、その後、受信ルート（provider アカウントまたは特定の peer）を各エージェントにバインドしてください。設定例は [Multi-Agent Routing](/ja-JP/concepts/multi-agent) にあります。あわせて [Models](/ja-JP/concepts/models) と [Configuration](/ja-JP/gateway/configuration) も参照してください。
  </Accordion>

  <Accordion title="Homebrew は Linux でも動きますか？">
    はい。Homebrew は Linux（Linuxbrew）をサポートしています。簡単なセットアップ:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    OpenClaw を systemd 経由で実行する場合は、service の PATH に `/home/linuxbrew/.linuxbrew/bin`（またはあなたの brew prefix）が含まれていることを確認し、非ログインシェルでも `brew` でインストールしたツールが解決されるようにしてください。
    最近のビルドでは、Linux の systemd services で一般的なユーザー bin ディレクトリ（たとえば `~/.local/bin`、`~/.npm-global/bin`、`~/.local/share/pnpm`、`~/.bun/bin`）も先頭に追加され、`PNPM_HOME`、`NPM_CONFIG_PREFIX`、`BUN_INSTALL`、`VOLTA_HOME`、`ASDF_DATA_DIR`、`NVM_DIR`、`FNM_DIR` が設定されている場合はそれらも尊重されます。

  </Accordion>

  <Accordion title="ハッカブルな git install と npm install の違い">
    - **ハッカブルな（git）インストール:** 完全なソースチェックアウトで、編集可能、コントリビューターに最適です。
      ローカルでビルドを実行でき、コードやドキュメントにパッチを当てられます。
    - **npm install:** グローバル CLI インストールで、リポジトリはなく、「とにかく動かしたい」場合に最適です。
      更新は npm dist-tags から取得されます。

    ドキュメント: [はじめに](/ja-JP/start/getting-started), [Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="後から npm インストールと git インストールを切り替えられますか？">
    はい。もう一方の方式をインストールしてから、gateway service が新しい entrypoint を指すように Doctor を実行してください。
    これで **データは削除されません**。変更されるのは OpenClaw のコードインストールだけです。state
    （`~/.openclaw`）と workspace（`~/.openclaw/workspace`）はそのまま残ります。

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

    Doctor は gateway service の entrypoint の不一致を検出し、現在のインストールに合うように service 設定の書き換えを提案します（自動化では `--repair` を使用）。

    バックアップのヒント: [バックアップ戦略](#ディスク上の保存場所) を参照してください。

  </Accordion>

  <Accordion title="Gateway はノート PC で実行すべきですか、それとも VPS ですか？">
    簡単に言うと、**24 時間 365 日の信頼性が欲しいなら VPS を使ってください**。最小限の手間を求め、スリープや再起動を許容できるなら、ローカルで実行してください。

    **ノート PC（ローカル Gateway）**

    - **長所:** サーバー費用が不要、ローカルファイルへ直接アクセスできる、ブラウザー画面が見える。
    - **短所:** スリープ/ネットワーク切断 = 切断、OS 更新/再起動で中断、常に起動状態を保つ必要がある。

    **VPS / クラウド**

    - **長所:** 常時稼働、安定したネットワーク、ノート PC のスリープ問題がない、稼働し続けやすい。
    - **短所:** 多くは headless で動く（スクリーンショットを使用）、ファイルアクセスはリモートのみ、更新には SSH が必要。

    **OpenClaw 固有の注意:** WhatsApp/Telegram/Slack/Mattermost/Discord はいずれも VPS で問題なく動作します。実際のトレードオフは **headless browser** か可視ブラウザー画面か、という点です。[Browser](/ja-JP/tools/browser) を参照してください。

    **推奨デフォルト:** 以前に gateway の切断を経験したなら VPS。Mac を積極的に使っていて、ローカルファイルアクセスや可視ブラウザーでの UI 自動化が欲しいときはローカルが最適です。

  </Accordion>

  <Accordion title="OpenClaw を専用マシンで実行することはどれくらい重要ですか？">
    必須ではありませんが、**信頼性と分離のために推奨** します。

    - **専用ホスト（VPS/Mac mini/Pi）:** 常時稼働、スリープ/再起動による中断が少ない、権限がクリーン、稼働し続けやすい。
    - **共有ノート PC/デスクトップ:** テストやアクティブな利用にはまったく問題ありませんが、マシンがスリープしたり更新したりすると一時停止が発生します。

    両方の利点を取りたい場合は、Gateway を専用ホストに置き、ノート PC をローカルの screen/camera/exec ツール用 **Node** としてペアリングしてください。[Nodes](/ja-JP/nodes) を参照してください。
    セキュリティガイダンスについては [Security](/ja-JP/gateway/security) を読んでください。

  </Accordion>

  <Accordion title="最小限の VPS 要件と推奨 OS は何ですか？">
    OpenClaw は軽量です。基本的な Gateway + 1 つのチャットチャネルなら:

    - **絶対的な最小要件:** 1 vCPU、1GB RAM、約 500MB のディスク。
    - **推奨:** 1〜2 vCPU、2GB RAM 以上で余裕を確保（ログ、メディア、複数チャネル）。Node ツールやブラウザー自動化はリソースを多く消費することがあります。

    OS: **Ubuntu LTS**（または最近の Debian/Ubuntu）を使ってください。Linux のインストール手順はそこで最もよくテストされています。

    ドキュメント: [Linux](/ja-JP/platforms/linux), [VPS hosting](/ja-JP/vps)。

  </Accordion>

  <Accordion title="VM で OpenClaw を実行できますか？ 要件は何ですか？">
    はい。VM は VPS と同じように扱ってください。常時稼働し、到達可能で、Gateway と有効化するチャネルに十分な
    RAM が必要です。

    基本的な目安:

    - **絶対的な最小要件:** 1 vCPU、1GB RAM。
    - **推奨:** 複数チャネル、ブラウザー自動化、またはメディアツールを実行するなら 2GB RAM 以上。
    - **OS:** Ubuntu LTS または最近の Debian/Ubuntu。

    Windows の場合、**WSL2 が最も簡単な VM スタイルのセットアップ** であり、ツール互換性も最も高いです。[Windows](/ja-JP/platforms/windows), [VPS hosting](/ja-JP/vps) を参照してください。
    VM で macOS を実行する場合は、[macOS VM](/ja-JP/install/macos-vm) を参照してください。

  </Accordion>
</AccordionGroup>

## OpenClaw とは？

<AccordionGroup>
  <Accordion title="OpenClaw を 1 段落で説明すると？">
    OpenClaw は、自分のデバイス上で実行するパーソナル AI アシスタントです。すでに使っているメッセージング画面（WhatsApp、Telegram、Slack、Mattermost、Discord、Google Chat、Signal、iMessage、WebChat、および QQ Bot のようなバンドル済み channel plugins）で応答でき、対応プラットフォームでは音声 + ライブ Canvas も利用できます。**Gateway** は常時稼働のコントロールプレーンであり、アシスタントが製品そのものです。
  </Accordion>

  <Accordion title="価値提案">
    OpenClaw は「単なる Claude ラッパー」ではありません。これは、**自分のハードウェア** 上で
    高機能なアシスタントを動かし、すでに使っているチャットアプリからアクセスでき、状態を持つ
    セッション、メモリ、ツールを備えつつ、ワークフローの制御をホスト型
    SaaS に委ねなくて済む **ローカルファーストのコントロールプレーン** です。

    主な特徴:

    - **あなたのデバイス、あなたのデータ:** Gateway を好きな場所（Mac、Linux、VPS）で動かし、
      workspace + session history をローカルに保持できます。
    - **Web サンドボックスではなく実際のチャネル:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage など、
      加えて対応プラットフォームではモバイル音声と Canvas。
    - **モデル非依存:** Anthropic、OpenAI、MiniMax、OpenRouter などを、エージェントごとのルーティング
      とフェイルオーバー付きで利用できます。
    - **ローカル専用オプション:** ローカルモデルを実行して、必要なら **すべてのデータをデバイス上に保持** できます。
    - **マルチエージェントルーティング:** チャネル、アカウント、またはタスクごとに個別の
      エージェントを分け、それぞれ独自の workspace とデフォルト設定を持てます。
    - **オープンソースでハック可能:** ベンダーロックインなしで、調査、拡張、セルフホストができます。

    ドキュメント: [Gateway](/ja-JP/gateway), [Channels](/ja-JP/channels), [Multi-agent](/ja-JP/concepts/multi-agent),
    [Memory](/ja-JP/concepts/memory)。

  </Accordion>

  <Accordion title="今セットアップしたところですが、最初に何をすべきですか？">
    最初のプロジェクトとしておすすめなのは:

    - Web サイトを作る（WordPress、Shopify、またはシンプルな静的サイト）。
    - モバイルアプリを試作する（概要、画面、API 計画）。
    - ファイルとフォルダーを整理する（クリーンアップ、命名、タグ付け）。
    - Gmail を接続して要約やフォローアップを自動化する。

    大きなタスクにも対応できますが、フェーズに分けて
    サブエージェントで並列作業すると最もうまく機能します。

  </Accordion>

  <Accordion title="OpenClaw の日常的な上位 5 つのユースケースは何ですか？">
    日常で効果を感じやすい使い方は、たいてい次のようなものです。

    - **個人向けブリーフィング:** 受信箱、カレンダー、気になるニュースの要約。
    - **調査と下書き作成:** すばやい調査、要約、メールや文書の初稿作成。
    - **リマインダーとフォローアップ:** Cron や Heartbeat による通知やチェックリスト。
    - **ブラウザー自動化:** フォーム入力、データ収集、Web タスクの繰り返し。
    - **デバイス横断の連携:** スマートフォンからタスクを送り、Gateway にサーバー上で実行させ、結果をチャットで受け取る。

  </Accordion>

  <Accordion title="OpenClaw は SaaS 向けのリード獲得、アウトリーチ、広告、ブログ作成に役立ちますか？">
    **調査、選別、下書き作成** には役立ちます。サイトをスキャンし、ショートリストを作り、
    見込み客を要約し、アウトリーチ文面や広告コピーの下書きを書けます。

    **アウトリーチや広告配信** については、人を必ず関与させてください。スパムを避け、現地の法律や
    プラットフォームポリシーに従い、送信前に必ず内容を確認してください。最も安全なパターンは、
    OpenClaw に下書きさせてあなたが承認することです。

    ドキュメント: [Security](/ja-JP/gateway/security)。

  </Accordion>

  <Accordion title="Web 開発において Claude Code と比べた利点は何ですか？">
    OpenClaw は IDE の置き換えではなく、**パーソナルアシスタント** および連携レイヤーです。リポジトリ内で
    最速の直接コーディングループが必要なら Claude Code や Codex を使ってください。永続的なメモリ、
    デバイス横断アクセス、ツールオーケストレーションが欲しいなら OpenClaw を使ってください。

    利点:

    - セッションをまたいだ **永続的なメモリ + workspace**
    - **マルチプラットフォームアクセス**（WhatsApp、Telegram、TUI、WebChat）
    - **ツールオーケストレーション**（browser、files、scheduling、hooks）
    - **常時稼働 Gateway**（VPS 上で動かし、どこからでも操作可能）
    - ローカル browser/screen/camera/exec 用の **Nodes**

    紹介ページ: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills と自動化

<AccordionGroup>
  <Accordion title="リポジトリを汚さずに Skills をカスタマイズするにはどうすればよいですか？">
    リポジトリ内のコピーを直接編集するのではなく、管理された override を使ってください。変更内容は `~/.openclaw/skills/<name>/SKILL.md` に置くか、`~/.openclaw/openclaw.json` の `skills.load.extraDirs` でフォルダーを追加します。優先順位は `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` なので、git に触れなくても管理 override が bundled Skills より優先されます。Skills をグローバルにインストールしつつ一部のエージェントにだけ見せたい場合は、共有コピーを `~/.openclaw/skills` に置き、`agents.defaults.skills` と `agents.list[].skills` で表示範囲を制御してください。上流に入れる価値のある変更だけをリポジトリに入れ、PR として送ってください。
  </Accordion>

  <Accordion title="カスタムフォルダーから Skills を読み込めますか？">
    はい。`~/.openclaw/openclaw.json` の `skills.load.extraDirs` で追加ディレクトリを指定できます（最も低い優先順位）。デフォルトの優先順位は `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` です。`clawhub` はデフォルトで `./skills` にインストールし、OpenClaw は次のセッションでこれを `<workspace>/skills` として扱います。Skills を特定のエージェントにだけ見せたい場合は、`agents.defaults.skills` または `agents.list[].skills` と組み合わせてください。
  </Accordion>

  <Accordion title="タスクごとに異なるモデルを使うにはどうすればよいですか？">
    現在サポートされているパターンは次のとおりです。

    - **Cron jobs**: 分離されたジョブごとに `model` override を設定できます。
    - **サブエージェント**: 異なるデフォルトモデルを持つ別エージェントにタスクをルーティングします。
    - **オンデマンド切り替え**: `/model` を使って現在のセッションモデルをいつでも切り替えます。

    [Cron jobs](/ja-JP/automation/cron-jobs)、[Multi-Agent Routing](/ja-JP/concepts/multi-agent)、[Slash commands](/ja-JP/tools/slash-commands) を参照してください。

  </Accordion>

  <Accordion title="重い処理をするとボットが固まります。どうやってオフロードすればよいですか？">
    長時間または並列のタスクには **サブエージェント** を使ってください。サブエージェントは独自のセッションで動作し、
    要約を返し、メインチャットの応答性を保ちます。

    ボットに「このタスク用にサブエージェントを起動して」と頼むか、`/subagents` を使ってください。
    チャット内で `/status` を使うと、Gateway が今何をしているか（そしてビジーかどうか）を確認できます。

    トークンのヒント: 長時間タスクもサブエージェントもトークンを消費します。コストが気になる場合は、
    `agents.defaults.subagents.model` でサブエージェント用により安価なモデルを設定してください。

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents), [Background Tasks](/ja-JP/automation/tasks)。

  </Accordion>

  <Accordion title="Discord でスレッドに紐づくサブエージェントセッションはどのように動作しますか？">
    スレッドバインディングを使います。Discord スレッドをサブエージェントまたはセッションターゲットにバインドすると、そのスレッド内の後続メッセージは、そのバインドされたセッション上で継続されます。

    基本フロー:

    - `sessions_spawn` を `thread: true` 付きで実行して起動します（永続的なフォローアップには任意で `mode: "session"` も指定）。
    - または `/focus <target>` で手動バインドします。
    - `/agents` でバインディング状態を確認します。
    - `/session idle <duration|off>` と `/session max-age <duration|off>` で自動 unfocus を制御します。
    - `/unfocus` でスレッドを切り離します。

    必要な設定:

    - グローバルデフォルト: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`。
    - Discord override: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`。
    - 起動時に自動バインド: `channels.discord.threadBindings.spawnSubagentSessions: true` を設定します。

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents), [Discord](/ja-JP/channels/discord), [Configuration Reference](/ja-JP/gateway/configuration-reference), [Slash commands](/ja-JP/tools/slash-commands)。

  </Accordion>

  <Accordion title="サブエージェントは完了したのに、完了通知が違う場所に送られた、または投稿されませんでした。何を確認すべきですか？">
    まず解決済みの requester route を確認してください。

    - 完了モードのサブエージェント配信では、バインドされたスレッドまたは会話ルートが存在する場合、それが優先されます。
    - 完了元がチャネル情報しか持っていない場合、OpenClaw は requester セッションに保存されたルート（`lastChannel` / `lastTo` / `lastAccountId`）にフォールバックするため、ダイレクト配信が引き続き成功することがあります。
    - バインド済みルートも使用可能な保存ルートも存在しない場合、ダイレクト配信は失敗する可能性があり、その結果はチャットに即時投稿される代わりに、キューされたセッション配信へフォールバックします。
    - 無効または古いターゲットでは、引き続きキューフォールバックや最終配信失敗が発生することがあります。
    - 子の最後に見える assistant 応答が正確に無音トークン `NO_REPLY` / `no_reply`、または正確に `ANNOUNCE_SKIP` である場合、OpenClaw は古い進捗を投稿しないよう、通知を意図的に抑制します。
    - 子がツール呼び出しだけの状態でタイムアウトした場合、通知では生のツール出力を再表示する代わりに、それを短い部分進捗サマリーにまとめることがあります。

    デバッグ:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents), [Background Tasks](/ja-JP/automation/tasks), [Session Tools](/ja-JP/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron やリマインダーが発火しません。何を確認すべきですか？">
    Cron は Gateway プロセス内で実行されます。Gateway が継続的に実行されていない場合、
    スケジュールされたジョブは実行されません。

    チェックリスト:

    - cron が有効（`cron.enabled`）で、`OPENCLAW_SKIP_CRON` が設定されていないことを確認してください。
    - Gateway が 24 時間 365 日稼働していることを確認してください（スリープ/再起動なし）。
    - ジョブのタイムゾーン設定（`--tz` とホストのタイムゾーン）を確認してください。

    デバッグ:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [Automation & Tasks](/ja-JP/automation).

  </Accordion>

  <Accordion title="Cron は発火したのに、チャネルに何も送られませんでした。なぜですか？">
    まず配信モードを確認してください。

    - `--no-deliver` / `delivery.mode: "none"` は、外部メッセージが送られないことを意味します。
    - 通知ターゲット（`channel` / `to`）が欠落している、または無効な場合、runner は外部配信をスキップします。
    - チャネル認証の失敗（`unauthorized`、`Forbidden`）は、runner が配信を試みたが資格情報によってブロックされたことを意味します。
    - 無音の isolated 結果（`NO_REPLY` / `no_reply` のみ）は、意図的に配信不可として扱われるため、runner はキューフォールバック配信も抑制します。

    isolated cron jobs では、runner が最終配信を担当します。agent は
    runner が送信するためのプレーンテキストの要約を返すことが期待されています。`--no-deliver` は
    その結果を内部に留めるものであり、代わりに agent が
    message tool で直接送信できるようにするものではありません。

    デバッグ:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [Background Tasks](/ja-JP/automation/tasks).

  </Accordion>

  <Accordion title="isolated cron 実行でモデルが切り替わったり 1 回再試行されたりしたのはなぜですか？">
    これは通常、重複スケジューリングではなく、ライブのモデル切り替え経路です。

    isolated cron は、アクティブな実行が `LiveSessionModelSwitchError` を投げたときに、
    ランタイムのモデル引き継ぎを永続化して再試行できます。再試行では切り替えられた
    provider/model が維持され、その切り替えに新しい auth profile override が含まれていた場合は、
    cron は再試行前にそれも永続化します。

    関連する選択ルール:

    - 該当する場合、まず Gmail hook model override が優先されます。
    - 次にジョブごとの `model`。
    - 次に保存済みの cron-session model override。
    - その後で通常の agent/default model selection。

    再試行ループには上限があります。初回試行 + 2 回の切り替え再試行の後は、
    cron は無限ループせず中止します。

    デバッグ:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Linux で Skills をインストールするにはどうすればよいですか？">
    ネイティブの `openclaw skills` コマンドを使うか、Skills を workspace に配置してください。macOS の Skills UI は Linux では利用できません。
    Skills は [https://clawhub.ai](https://clawhub.ai) で探せます。

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
    ディレクトリに書き込みます。別個の `clawhub` CLI は、自分の Skills を公開または
    同期したい場合にのみインストールしてください。エージェント間で共有インストールしたい場合は、Skills を
    `~/.openclaw/skills` 配下に置き、どのエージェントに見せるかを絞りたい場合は
    `agents.defaults.skills` または `agents.list[].skills` を使ってください。

  </Accordion>

  <Accordion title="OpenClaw はタスクをスケジュール実行したり、バックグラウンドで継続実行したりできますか？">
    はい。Gateway scheduler を使ってください。

    - **Cron jobs**: スケジュール実行または繰り返しタスク用（再起動後も保持されます）。
    - **Heartbeat**: 「メインセッション」の定期チェック用。
    - **Isolated jobs**: 要約を投稿したりチャットに配信したりする自律エージェント用。

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [Automation & Tasks](/ja-JP/automation),
    [Heartbeat](/ja-JP/gateway/heartbeat).

  </Accordion>

  <Accordion title="Linux から Apple の macOS 専用 Skills を実行できますか？">
    直接にはできません。macOS Skills は `metadata.openclaw.os` と必要なバイナリによって制御され、Skills は **Gateway host** 上で適格な場合にのみ system prompt に表示されます。Linux では、`darwin` 専用の Skills（`apple-notes`、`apple-reminders`、`things-mac` など）は、その制御を上書きしない限りロードされません。

    サポートされるパターンは 3 つあります。

    **オプション A - Gateway を Mac 上で実行する（最も簡単）。**
    macOS のバイナリが存在する場所で Gateway を実行し、その後 [remote mode](#gateway-ports-already-running-and-remote-mode) または Tailscale 経由で Linux から接続します。Gateway host が macOS なので、Skills は通常どおりロードされます。

    **オプション B - macOS Node を使う（SSH なし）。**
    Gateway を Linux 上で実行し、macOS Node（メニューバーアプリ）をペアリングして、Mac 上の **Node Run Commands** を「Always Ask」または「Always Allow」に設定します。必要なバイナリが Node 上に存在する場合、OpenClaw は macOS 専用 Skills を適格として扱えます。agent はそれらの Skills を `nodes` tool 経由で実行します。「Always Ask」を選んだ場合、プロンプトで「Always Allow」を承認すると、そのコマンドが allowlist に追加されます。

    **オプション C - SSH 経由で macOS バイナリをプロキシする（上級者向け）。**
    Gateway は Linux 上のままにしつつ、必要な CLI バイナリが Mac 上で実行される SSH ラッパーに解決されるようにします。その後、Skill を上書きして Linux を許可し、適格なままにします。

    1. バイナリ用の SSH ラッパーを作成します（例: Apple Notes 用の `memo`）:

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. ラッパーを Linux ホストの `PATH` 上に置きます（例 `~/bin/memo`）。
    3. Skill metadata を上書きして Linux を許可します（workspace または `~/.openclaw/skills`）:

       ```markdown
       ---
       name: apple-notes
       description: memo CLI を介して macOS 上の Apple Notes を管理します。
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Skills snapshot が更新されるように、新しいセッションを開始します。

  </Accordion>

  <Accordion title="Notion や HeyGen との連携はありますか？">
    現時点では組み込みではありません。

    選択肢:

    - **カスタム Skill / Plugin:** 信頼性の高い API アクセスに最適です（Notion/HeyGen はどちらも API を持っています）。
    - **ブラウザー自動化:** コード不要で動きますが、遅くて壊れやすくなります。

    クライアントごとにコンテキストを維持したい場合（代理店ワークフローなど）のシンプルなパターンは次のとおりです。

    - クライアントごとに 1 つの Notion ページ（コンテキスト + 設定 + 進行中の作業）。
    - セッション開始時にそのページを取得するよう agent に指示します。

    ネイティブ連携が欲しい場合は、機能リクエストを作成するか、それらの API を対象とした Skill
    を作成してください。

    Skills をインストール:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    ネイティブインストール先はアクティブな workspace の `skills/` ディレクトリです。エージェント間で共有する Skills は `~/.openclaw/skills/<name>/SKILL.md` に配置してください。共有インストールを一部のエージェントにだけ見せたい場合は、`agents.defaults.skills` または `agents.list[].skills` を設定します。一部の Skills では Homebrew 経由でインストールされたバイナリが必要であり、Linux では Linuxbrew を意味します（上の Homebrew Linux FAQ 項目を参照）。[Skills](/ja-JP/tools/skills), [Skills config](/ja-JP/tools/skills-config), [ClawHub](/ja-JP/tools/clawhub) を参照してください。

  </Accordion>

  <Accordion title="既存のサインイン済み Chrome を OpenClaw で使うにはどうすればよいですか？">
    Chrome DevTools MCP 経由で接続する組み込みの `user` browser profile を使ってください。

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    カスタム名を使いたい場合は、明示的な MCP profile を作成します。

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    この経路はホストローカルです。Gateway が別の場所で動作している場合は、browser マシン上で Node host を動かすか、代わりにリモート CDP を使ってください。

    `existing-session` / `user` の現在の制限:

    - アクションは CSS selector ベースではなく ref ベースです
    - アップロードには `ref` / `inputRef` が必要で、現在は 1 回に 1 ファイルのみサポートします
    - `responsebody`、PDF エクスポート、ダウンロードのインターセプト、バッチアクションは、引き続き managed browser または生の CDP profile が必要です

  </Accordion>
</AccordionGroup>

## サンドボックス化とメモリ

<AccordionGroup>
  <Accordion title="専用のサンドボックス化ドキュメントはありますか？">
    はい。[Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。Docker 固有のセットアップ（Docker 上での完全な gateway、または sandbox イメージ）については、[Docker](/ja-JP/install/docker) を参照してください。
  </Accordion>

  <Accordion title="Docker では制限が多く感じます。完全な機能を有効にするにはどうすればよいですか？">
    デフォルトイメージはセキュリティ優先で `node` ユーザーとして実行されるため、
    system packages、Homebrew、バンドル済みブラウザーは含まれていません。より完全なセットアップにするには:

    - キャッシュが維持されるように `/home/node` を `OPENCLAW_HOME_VOLUME` で永続化します。
    - `OPENCLAW_DOCKER_APT_PACKAGES` で system deps をイメージに組み込みます。
    - バンドル済み CLI で Playwright ブラウザーをインストールします:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - `PLAYWRIGHT_BROWSERS_PATH` を設定し、そのパスが永続化されるようにします。

    ドキュメント: [Docker](/ja-JP/install/docker), [Browser](/ja-JP/tools/browser).

  </Accordion>

  <Accordion title="1 つのエージェントで DM は個人的に保ちつつ、グループは公開/サンドボックス化できますか？">
    はい。プライベートな通信が **DM** で、公開の通信が **グループ** である場合に可能です。

    `agents.defaults.sandbox.mode: "non-main"` を使うと、グループ/チャネルセッション（non-main keys）は Docker 内で実行され、メインの DM セッションはホスト上に残ります。その後、サンドボックス化されたセッションで利用可能なツールを `tools.sandbox.tools` で制限してください。

    セットアップ手順 + 設定例: [Groups: personal DMs + public groups](/ja-JP/channels/groups#pattern-personal-dms-public-groups-single-agent)

    主要な設定リファレンス: [Gateway configuration](/ja-JP/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="ホストのフォルダーをサンドボックスにバインドするにはどうすればよいですか？">
    `agents.defaults.sandbox.docker.binds` を `["host:path:mode"]` に設定してください（例: `"/home/user/src:/src:ro"`）。グローバル + エージェント単位の bind はマージされます。`scope: "shared"` の場合、エージェント単位の bind は無視されます。機密性の高いものには `:ro` を使い、bind はサンドボックスのファイルシステム境界を迂回することを忘れないでください。

    OpenClaw は、正規化されたパスと、最も深い既存の祖先を通じて解決された canonical path の両方に対して bind source を検証します。つまり、最後のパスセグメントがまだ存在しない場合でも symlink-parent escape は安全側で失敗し、許可されたルートのチェックも symlink 解決後に引き続き適用されます。

    例と安全上の注意については [Sandboxing](/ja-JP/gateway/sandboxing#custom-bind-mounts) と [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) を参照してください。

  </Accordion>

  <Accordion title="メモリはどのように動作しますか？">
    OpenClaw のメモリは、agent workspace 内の Markdown ファイルにすぎません。

    - `memory/YYYY-MM-DD.md` の日次ノート
    - `MEMORY.md` の整理された長期ノート（main/private sessions のみ）

    OpenClaw はまた、**無音の pre-Compaction メモリフラッシュ** を実行し、
    auto-Compaction の前に永続的なノートを書き込むようモデルに促します。これは workspace が
    書き込み可能な場合にのみ実行されます（読み取り専用サンドボックスではスキップされます）。[Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>

  <Accordion title="メモリが物事を忘れ続けます。どうすれば定着しますか？">
    ボットに **その事実をメモリに書く** よう依頼してください。長期ノートは `MEMORY.md` に、
    短期コンテキストは `memory/YYYY-MM-DD.md` に入ります。

    これはまだ改善を進めている領域です。モデルにメモリを保存するよう促すと効果があります。
    モデルは何をすべきか理解しています。それでも忘れ続ける場合は、Gateway が毎回同じ
    workspace を使っていることを確認してください。

    ドキュメント: [Memory](/ja-JP/concepts/memory), [Agent workspace](/ja-JP/concepts/agent-workspace).

  </Accordion>

  <Accordion title="メモリは永久に保持されますか？ 制限は何ですか？">
    メモリファイルはディスク上に保存され、削除するまで保持されます。制限は
    モデルではなくストレージです。ただし **session context** は依然としてモデルの
    context window に制限されるため、長い会話では Compaction や切り詰めが起こることがあります。だからこそ
    memory search が存在します。関連する部分だけを再びコンテキストに戻します。

    ドキュメント: [Memory](/ja-JP/concepts/memory), [Context](/ja-JP/concepts/context).

  </Accordion>

  <Accordion title="セマンティックメモリ検索には OpenAI API key が必要ですか？">
    **OpenAI embeddings** を使う場合にのみ必要です。Codex OAuth は chat/completions を対象としており、
    embeddings へのアクセスは **付与しません**。そのため、**Codex でサインインしても（OAuth または
    Codex CLI login でも）** セマンティックメモリ検索の助けにはなりません。OpenAI embeddings には
    引き続き実際の API key（`OPENAI_API_KEY` または `models.providers.openai.apiKey`）が必要です。

    provider を明示的に設定しない場合、OpenClaw は API key を解決できたときに
    自動的に provider を選択します（auth profiles、`models.providers.*.apiKey`、または env vars）。
    OpenAI key が解決できれば OpenAI を優先し、そうでなければ Gemini、次に
    Voyage、次に Mistral を優先します。利用可能なリモートキーがない場合、
    memory search は設定するまで無効のままです。ローカルモデルのパスが
    設定済みで存在する場合、OpenClaw は
    `local` を優先します。Ollama は
    `memorySearch.provider = "ollama"` を明示的に設定した場合にサポートされます。

    ローカルのままにしたい場合は、`memorySearch.provider = "local"` を設定してください（必要に応じて
    `memorySearch.fallback = "none"` も指定できます）。Gemini embeddings を使いたい場合は、
    `memorySearch.provider = "gemini"` を設定し、`GEMINI_API_KEY`（または
    `memorySearch.remote.apiKey`）を指定してください。サポートしている embedding
    モデルは **OpenAI、Gemini、Voyage、Mistral、Ollama、または local** です。セットアップの詳細は [Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>
</AccordionGroup>

## ディスク上の保存場所

<AccordionGroup>
  <Accordion title="OpenClaw で使用されるデータはすべてローカルに保存されますか？">
    いいえ。**OpenClaw の state はローカル** ですが、**外部サービスは依然として送信した内容を受け取ります**。

    - **デフォルトでローカル:** sessions、メモリファイル、config、workspace は Gateway host 上に保存されます
      （`~/.openclaw` + あなたの workspace ディレクトリ）。
    - **必要上リモート:** model providers（Anthropic/OpenAI など）に送るメッセージは
      それらの API に送信され、chat platforms（WhatsApp/Telegram/Slack など）はメッセージデータを
      自身のサーバーに保存します。
    - **フットプリントは自分で制御可能:** ローカルモデルを使えばプロンプトは自分のマシン上に残りますが、channel
      トラフィックは依然としてそのチャネルのサーバーを経由します。

    関連: [Agent workspace](/ja-JP/concepts/agent-workspace), [Memory](/ja-JP/concepts/memory).

  </Accordion>

  <Accordion title="OpenClaw はどこにデータを保存しますか？">
    すべては `$OPENCLAW_STATE_DIR`（デフォルト: `~/.openclaw`）配下にあります。

    | Path                                                            | 用途                                                                 |
    | --------------------------------------------------------------- | -------------------------------------------------------------------- |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | メイン設定（JSON5）                                                   |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | レガシー OAuth インポート（初回使用時に auth profiles へコピー）      |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Auth profiles（OAuth、API keys、および任意の `keyRef`/`tokenRef`）   |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef provider 用の任意のファイルベース secret payload    |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | レガシー互換ファイル（静的な `api_key` エントリは除去済み）          |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Provider state（例: `whatsapp/<accountId>/creds.json`）              |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | エージェントごとの state（agentDir + sessions）                      |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 会話履歴と state（エージェントごと）                                 |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Session metadata（エージェントごと）                                 |

    レガシーの単一エージェントパス: `~/.openclaw/agent/*`（`openclaw doctor` により移行）。

    **workspace**（AGENTS.md、メモリファイル、skills など）は別で、`agents.defaults.workspace` 経由で設定します（デフォルト: `~/.openclaw/workspace`）。

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md はどこに置くべきですか？">
    これらのファイルは `~/.openclaw` ではなく、**agent workspace** に置きます。

    - **Workspace（エージェントごと）**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md`（`MEMORY.md` がない場合はレガシーフォールバックの `memory.md`）、
      `memory/YYYY-MM-DD.md`, 任意の `HEARTBEAT.md`。
    - **State dir（`~/.openclaw`）**: config、channel/provider state、auth profiles、sessions、logs、
      および共有 skills（`~/.openclaw/skills`）。

    デフォルトの workspace は `~/.openclaw/workspace` で、以下で設定できます。

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    再起動後にボットが「忘れる」場合は、Gateway が起動のたびに同じ
    workspace を使っていることを確認してください（そして忘れないでください: remote mode では **gateway host の**
    workspace が使われ、ローカルのノート PC のものではありません）。

    ヒント: 永続的なふるまいや設定を残したい場合は、チャット履歴に頼るのではなく、
    ボットに **AGENTS.md または MEMORY.md に書き込む** よう依頼してください。

    [Agent workspace](/ja-JP/concepts/agent-workspace) と [Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>

  <Accordion title="推奨バックアップ戦略">
    **agent workspace** を **private** git repo に入れ、どこか非公開の場所
    （たとえば GitHub private）にバックアップしてください。これにより memory + AGENTS/SOUL/USER
    ファイルが保存され、後でアシスタントの「心」を復元できます。

    `~/.openclaw` 配下のもの（credentials、sessions、tokens、または暗号化された secrets payload）は **絶対に** commit しないでください。
    完全な復元が必要な場合は、workspace と state directory の両方を
    別々にバックアップしてください（上の移行に関する質問を参照）。

    ドキュメント: [Agent workspace](/ja-JP/concepts/agent-workspace).

  </Accordion>

  <Accordion title="OpenClaw を完全にアンインストールするにはどうすればよいですか？">
    専用ガイドを参照してください: [Uninstall](/ja-JP/install/uninstall)。
  </Accordion>

  <Accordion title="エージェントは workspace 外で作業できますか？">
    はい。workspace は **デフォルトの cwd** およびメモリアンカーであり、厳密なサンドボックスではありません。
    相対パスは workspace 内で解決されますが、absolute paths は他の
    ホスト上の場所にもアクセスできます。ただしサンドボックス化が有効な場合は除きます。分離が必要なら、
    [`agents.defaults.sandbox`](/ja-JP/gateway/sandboxing) またはエージェント単位のサンドボックス設定を使ってください。repo を
    デフォルトの作業ディレクトリにしたい場合は、そのエージェントの
    `workspace` を repo root に向けてください。OpenClaw repo は単なるソースコードです。意図的にその中でエージェントを作業させたいのでない限り、
    workspace は分けておいてください。

    例（repo をデフォルトの cwd にする）:

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

  <Accordion title="remote mode: session store はどこですか？">
    Session state は **gateway host** が保持します。remote mode の場合、重要な session store はローカルのノート PC ではなくリモートマシン上にあります。[Session management](/ja-JP/concepts/session) を参照してください。
  </Accordion>
</AccordionGroup>

## 設定の基本

<AccordionGroup>
  <Accordion title="設定ファイルの形式は何ですか？ どこにありますか？">
    OpenClaw は `$OPENCLAW_CONFIG_PATH`（デフォルト: `~/.openclaw/openclaw.json`）から、任意の **JSON5** 設定を読み込みます。

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    ファイルが存在しない場合は、安全寄りのデフォルト値が使われます（デフォルト workspace は `~/.openclaw/workspace`）。

  </Accordion>

  <Accordion title='`gateway.bind: "lan"`（または `"tailnet"`）を設定したら、何も listen しなくなった / UI に unauthorized と表示される'>
    non-loopback bind では **有効な gateway auth 経路が必須** です。実際には次のいずれかを意味します。

    - shared-secret auth: token または password
    - `gateway.auth.mode: "trusted-proxy"` を、正しく設定された non-loopback の identity-aware reverse proxy の背後で使う

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

    - `gateway.remote.token` / `.password` だけではローカル gateway auth は有効になりません。
    - ローカルの呼び出し経路では、`gateway.auth.*` が未設定の場合に限り `gateway.remote.*` をフォールバックとして使えます。
    - password auth では、代わりに `gateway.auth.mode: "password"` と `gateway.auth.password`（または `OPENCLAW_GATEWAY_PASSWORD`）を設定してください。
    - `gateway.auth.token` / `gateway.auth.password` が SecretRef 経由で明示的に設定されていて未解決の場合、解決は安全側で失敗します（remote フォールバックで隠蔽されることはありません）。
    - shared-secret の Control UI セットアップでは、`connect.params.auth.token` または `connect.params.auth.password`（app/UI 設定に保存）で認証します。Tailscale Serve や `trusted-proxy` のような identity-bearing モードでは、代わりに request headers を使います。shared secrets を URL に入れないでください。
    - `gateway.auth.mode: "trusted-proxy"` では、同一ホストの loopback reverse proxy は依然として trusted-proxy auth を満たしません。trusted proxy は、設定済みの non-loopback source である必要があります。

  </Accordion>

  <Accordion title="なぜ localhost でも token が必要になったのですか？">
    OpenClaw はデフォルトで gateway auth を強制しており、loopback も含まれます。通常のデフォルト経路では token auth を意味します。明示的な auth 経路が設定されていない場合、gateway 起動時に token mode に解決されて自動生成され、それが `gateway.auth.token` に保存されるため、**ローカルの WS クライアントも認証が必要** になります。これにより、他のローカルプロセスが Gateway を呼び出すのを防ぎます。

    別の auth 経路を望む場合は、password mode（または non-loopback の identity-aware reverse proxies 向けに `trusted-proxy`）を明示的に選べます。**本当に** open loopback にしたい場合は、設定で `gateway.auth.mode: "none"` を明示的に指定してください。Doctor はいつでも token を生成できます: `openclaw doctor --generate-gateway-token`。

  </Accordion>

  <Accordion title="設定変更後に再起動は必要ですか？">
    Gateway は設定を監視しており、ホットリロードをサポートしています。

    - `gateway.reload.mode: "hybrid"`（デフォルト）: 安全な変更はホット適用し、重要な変更では再起動します
    - `hot`、`restart`、`off` もサポートされています

  </Accordion>

  <Accordion title="面白い CLI タグラインを無効にするにはどうすればよいですか？">
    設定で `cli.banner.taglineMode` を設定します。

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: タグラインのテキストを非表示にしますが、バナーのタイトル/バージョン行は残します。
    - `default`: 毎回 `All your chats, one OpenClaw.` を使用します。
    - `random`: 面白い/季節もののタグラインをローテーションします（デフォルト動作）。
    - バナー自体を完全に消したい場合は、env `OPENCLAW_HIDE_BANNER=1` を設定してください。

  </Accordion>

  <Accordion title="Web search（および web fetch）を有効にするにはどうすればよいですか？">
    `web_fetch` は API key なしで動作します。`web_search` は、選択した
    provider に依存します。

    - Brave、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Perplexity、Tavily のような API ベースの provider では、通常どおり API key の設定が必要です。
    - Ollama Web Search はキー不要ですが、設定済みの Ollama host を使い、`ollama signin` が必要です。
    - DuckDuckGo はキー不要ですが、非公式の HTML ベース統合です。
    - SearXNG はキー不要/セルフホスト型です。`SEARXNG_BASE_URL` または `plugins.entries.searxng.config.webSearch.baseUrl` を設定してください。

    **推奨:** `openclaw configure --section web` を実行して provider を選択してください。
    環境変数での代替設定:

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

    provider 固有の web-search 設定は現在 `plugins.entries.<plugin>.config.webSearch.*` 配下にあります。
    レガシーの `tools.web.search.*` provider パスも互換性のため一時的に読み込まれますが、新しい設定では使わないでください。
    Firecrawl の web-fetch フォールバック設定は `plugins.entries.firecrawl.config.webFetch.*` 配下にあります。

    注意:

    - allowlist を使っている場合は、`web_search`/`web_fetch`/`x_search` または `group:web` を追加してください。
    - `web_fetch` はデフォルトで有効です（明示的に無効化していない限り）。
    - `tools.web.fetch.provider` を省略すると、OpenClaw は利用可能な資格情報から最初に準備できた fetch フォールバック provider を自動検出します。現時点でのバンドル済み provider は Firecrawl です。
    - デーモンは `~/.openclaw/.env`（または service environment）から env vars を読み込みます。

    ドキュメント: [Web tools](/ja-JP/tools/web)。

  </Accordion>

  <Accordion title="config.apply で設定が消えました。どう復旧し、どう防げばよいですか？">
    `config.apply` は **設定全体** を置き換えます。部分オブジェクトを送ると、それ以外の
    すべてが削除されます。

    復旧方法:

    - バックアップ（git またはコピーしておいた `~/.openclaw/openclaw.json`）から復元してください。
    - バックアップがない場合は、`openclaw doctor` を再実行して channels/models を再設定してください。
    - 想定外だった場合は、バグを報告し、最後に分かっている設定またはバックアップを添えてください。
    - ローカルのコーディングエージェントなら、ログや履歴から動作する設定を再構築できることがよくあります。

    防ぐ方法:

    - 小さな変更には `openclaw config set` を使ってください。
    - 対話的な編集には `openclaw configure` を使ってください。
    - 正確なパスやフィールド形状に自信がない場合は、まず `config.schema.lookup` を使ってください。浅いスキーマノードと直下の子要約が返るので、段階的に掘り下げられます。
    - 部分的な RPC 編集には `config.patch` を使い、`config.apply` は完全な設定置換にだけ使ってください。
    - エージェント実行から owner-only の `gateway` tool を使っている場合でも、`tools.exec.ask` / `tools.exec.security` への書き込みは引き続き拒否されます（同じ保護された exec パスに正規化されるレガシー `tools.bash.*` エイリアスを含みます）。

    ドキュメント: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/ja-JP/gateway/doctor)。

  </Accordion>

  <Accordion title="デバイス間で specialized workers を持つ中央 Gateway を実行するにはどうすればよいですか？">
    一般的なパターンは **1 つの Gateway**（例: Raspberry Pi）と **Nodes**、**agents** の組み合わせです。

    - **Gateway（中央）:** channels（Signal/WhatsApp）とルーティング、sessions を管理します。
    - **Nodes（デバイス）:** Mac/iOS/Android が周辺機器として接続し、ローカルツール（`system.run`、`canvas`、`camera`）を公開します。
    - **Agents（worker）:** 特殊な役割（例: 「Hetzner ops」「個人データ」）向けの別々の頭脳/workspaces です。
    - **サブエージェント:** 並列性が欲しいときに、メインエージェントからバックグラウンド作業を起動します。
    - **TUI:** Gateway に接続し、agents/sessions を切り替えます。

    ドキュメント: [Nodes](/ja-JP/nodes), [Remote access](/ja-JP/gateway/remote), [Multi-Agent Routing](/ja-JP/concepts/multi-agent), [Sub-agents](/ja-JP/tools/subagents), [TUI](/web/tui)。

  </Accordion>

  <Accordion title="OpenClaw browser は headless で実行できますか？">
    はい。設定オプションです。

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

    デフォルトは `false`（headful）です。headless は一部のサイトで bot 対策チェックを引き起こしやすくなります。[Browser](/ja-JP/tools/browser) を参照してください。

    headless でも **同じ Chromium エンジン** を使い、ほとんどの自動化（フォーム、クリック、スクレイピング、ログイン）で動作します。主な違いは次のとおりです。

    - ブラウザーウィンドウが表示されない（視覚情報が必要な場合はスクリーンショットを使用）。
    - 一部のサイトは headless モードでの自動化により厳格です（CAPTCHA、bot 対策）。
      たとえば、X/Twitter は headless セッションをブロックすることがよくあります。

  </Accordion>

  <Accordion title="ブラウザー制御に Brave を使うにはどうすればよいですか？">
    `browser.executablePath` を Brave のバイナリ（または任意の Chromium ベースブラウザー）に設定し、Gateway を再起動してください。
    完全な設定例は [Browser](/ja-JP/tools/browser#use-brave-or-another-chromium-based-browser) を参照してください。
  </Accordion>
</AccordionGroup>

## リモート Gateway と Nodes

<AccordionGroup>
  <Accordion title="Telegram、gateway、Nodes の間でコマンドはどのように伝播しますか？">
    Telegram メッセージは **gateway** によって処理されます。gateway は agent を実行し、
    Node tool が必要なときにだけ **Gateway WebSocket** 経由で Nodes を呼び出します。

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Nodes は受信した provider トラフィックを見ることはなく、受け取るのは node RPC 呼び出しだけです。

  </Accordion>

  <Accordion title="Gateway がリモートでホストされている場合、agent はどうやって自分のコンピューターにアクセスできますか？">
    簡単に言うと、**自分のコンピューターを Node としてペアリング** してください。Gateway は別の場所で動作しますが、
    Gateway WebSocket 経由でローカルマシン上の `node.*` tools（screen、camera、system）を
    呼び出せます。

    一般的なセットアップ:

    1. 常時稼働ホスト（VPS/ホームサーバー）で Gateway を実行します。
    2. Gateway host と自分のコンピューターを同じ tailnet に入れます。
    3. Gateway WS に到達できることを確認します（tailnet bind または SSH tunnel）。
    4. ローカルで macOS アプリを開き、**Remote over SSH** モード（または direct tailnet）
       で接続し、Node として登録できるようにします。
    5. Gateway 上で Node を承認します:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    別個の TCP bridge は不要です。Nodes は Gateway WebSocket 経由で接続します。

    セキュリティの注意: macOS Node をペアリングすると、そのマシンで `system.run` が可能になります。信頼できるデバイスだけを
    ペアリングし、[Security](/ja-JP/gateway/security) を確認してください。

    ドキュメント: [Nodes](/ja-JP/nodes), [Gateway protocol](/ja-JP/gateway/protocol), [macOS remote mode](/ja-JP/platforms/mac/remote), [Security](/ja-JP/gateway/security)。

  </Accordion>

  <Accordion title="Tailscale は接続済みなのに返信がありません。どうすればよいですか？">
    まず基本を確認してください。

    - Gateway が動作している: `openclaw gateway status`
    - Gateway の健全性: `openclaw status`
    - Channel の健全性: `openclaw channels status`

    次に認証とルーティングを確認します。

    - Tailscale Serve を使っている場合は、`gateway.auth.allowTailscale` が正しく設定されていることを確認してください。
    - SSH tunnel 経由で接続している場合は、ローカル tunnel が有効で、正しいポートを指していることを確認してください。
    - allowlist（DM または group）に自分のアカウントが含まれていることを確認してください。

    ドキュメント: [Tailscale](/ja-JP/gateway/tailscale), [Remote access](/ja-JP/gateway/remote), [Channels](/ja-JP/channels)。

  </Accordion>

  <Accordion title="2 つの OpenClaw インスタンス（ローカル + VPS）が互いに通信できますか？">
    はい。組み込みの「bot-to-bot」bridge はありませんが、いくつかの
    信頼できる方法で接続できます。

    **最も簡単:** 両方のボットがアクセスできる通常の chat channel（Telegram/Slack/WhatsApp）を使います。
    Bot A が Bot B にメッセージを送り、その後は Bot B が通常どおり返信するようにします。

    **CLI bridge（汎用）:** スクリプトを実行して、他方の Gateway に
    `openclaw agent --message ... --deliver` を呼び出し、相手のボットが
    listen しているチャットをターゲットにします。片方のボットがリモート VPS 上にある場合は、そのリモート Gateway に届くよう
    SSH/Tailscale 経由で CLI を向けてください（[Remote access](/ja-JP/gateway/remote) を参照）。

    例のパターン（対象 Gateway に到達できるマシンから実行）:

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    ヒント: 2 つのボットが無限ループしないようガードレールを入れてください（メンション時のみ、channel
    allowlists、または「bot メッセージには返信しない」ルール）。

    ドキュメント: [Remote access](/ja-JP/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/ja-JP/tools/agent-send)。

  </Accordion>

  <Accordion title="複数エージェントに複数の VPS は必要ですか？">
    いいえ。1 つの Gateway で複数の agents をホストでき、それぞれが独自の workspace、モデルのデフォルト、
    ルーティングを持てます。これが通常の構成であり、エージェントごとに
    1 台ずつ VPS を動かすよりもずっと安価で簡単です。

    別々の VPS を使うのは、厳格な分離（セキュリティ境界）や、
    共有したくない大きく異なる設定が必要な場合だけです。それ以外は、1 つの Gateway にして、
    複数の agents またはサブエージェントを使ってください。

  </Accordion>

  <Accordion title="VPS から SSH する代わりに、個人のノート PC 上で Node を使う利点はありますか？">
    はい。リモート Gateway からノート PC に到達する第一級の方法が Nodes であり、
    シェルアクセス以上のことができます。Gateway は macOS/Linux（Windows は WSL2 経由）で動作し、
    軽量です（小型の VPS や Raspberry Pi クラスのマシンで十分で、4 GB RAM あれば余裕があります）。そのため、常時稼働ホスト + ノート PC を Node にする構成が一般的です。

    - **受信 SSH が不要。** Nodes は Gateway WebSocket に対して外向き接続し、デバイスペアリングを使います。
    - **より安全な実行制御。** `system.run` はそのノート PC 上の Node allowlists/approvals によって制御されます。
    - **より多くのデバイスツール。** Nodes は `system.run` に加えて `canvas`、`camera`、`screen` を公開します。
    - **ローカルブラウザー自動化。** Gateway は VPS 上に置きつつ、Chrome はノート PC 上の Node host 経由でローカル実行するか、Chrome MCP 経由でホスト上のローカル Chrome に接続できます。

    SSH は臨時のシェルアクセスには問題ありませんが、継続的な agent ワークフローや
    デバイス自動化には Nodes の方が簡単です。

    ドキュメント: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes), [Browser](/ja-JP/tools/browser)。

  </Accordion>

  <Accordion title="Nodes は gateway service を実行しますか？">
    いいえ。意図的に分離されたプロファイルを実行する場合（[Multiple gateways](/ja-JP/gateway/multiple-gateways) を参照）を除き、ホストごとに実行すべき gateway は **1 つだけ** です。Nodes は gateway に接続する周辺機器です
    （iOS/Android Nodes、またはメニューバーアプリの macOS「node mode」）。headless の node
    host と CLI 制御については、[Node host CLI](/cli/node) を参照してください。

    `gateway`、`discovery`、`canvasHost` の変更には完全な再起動が必要です。

  </Accordion>

  <Accordion title="設定を適用する API / RPC の方法はありますか？">
    はい。

    - `config.schema.lookup`: 書き込む前に、1 つの設定サブツリーについて、浅いスキーマノード、一致した UI ヒント、直下の子要約を確認します
    - `config.get`: 現在のスナップショット + hash を取得します
    - `config.patch`: 安全な部分更新（ほとんどの RPC 編集で推奨）。可能ならホットリロードし、必要なら再起動します
    - `config.apply`: 検証して完全な設定を置換します。可能ならホットリロードし、必要なら再起動します
    - owner-only の `gateway` runtime tool は、引き続き `tools.exec.ask` / `tools.exec.security` の書き換えを拒否します。レガシーの `tools.bash.*` エイリアスは同じ保護された exec パスに正規化されます

  </Accordion>

  <Accordion title="初回インストール向けの最小限で妥当な設定">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    これで workspace を設定し、誰がボットをトリガーできるかを制限します。

  </Accordion>

  <Accordion title="VPS に Tailscale を設定して Mac から接続するにはどうすればよいですか？">
    最小手順:

    1. **VPS でインストールしてログイン**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Mac でインストールしてログイン**
       - Tailscale アプリを使い、同じ tailnet にサインインします。
    3. **MagicDNS を有効化（推奨）**
       - Tailscale 管理コンソールで MagicDNS を有効にし、VPS に安定した名前を付けます。
    4. **tailnet のホスト名を使う**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    SSH なしで Control UI を使いたい場合は、VPS で Tailscale Serve を使います。

    ```bash
    openclaw gateway --tailscale serve
    ```

    これにより gateway は loopback に bind したままになり、Tailscale 経由で HTTPS が公開されます。[Tailscale](/ja-JP/gateway/tailscale) を参照してください。

  </Accordion>

  <Accordion title="Mac Node をリモート Gateway（Tailscale Serve）に接続するにはどうすればよいですか？">
    Serve は **Gateway Control UI + WS** を公開します。Nodes は同じ Gateway WS エンドポイント経由で接続します。

    推奨セットアップ:

    1. **VPS と Mac が同じ tailnet にあることを確認** します。
    2. **macOS アプリを Remote mode で使います**（SSH ターゲットには tailnet のホスト名を使えます）。
       アプリは Gateway ポートをトンネルし、Node として接続します。
    3. gateway 上で Node を承認します:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    ドキュメント: [Gateway protocol](/ja-JP/gateway/protocol), [Discovery](/ja-JP/gateway/discovery), [macOS remote mode](/ja-JP/platforms/mac/remote).

  </Accordion>

  <Accordion title="2 台目のノート PC にインストールすべきですか、それとも Node を追加するだけでよいですか？">
    2 台目のノート PC で必要なのが **ローカルツール**（screen/camera/exec）だけなら、
    **Node** として追加してください。これなら Gateway を 1 つに保てて、設定の重複も避けられます。ローカルの Node tools は
    現在 macOS 専用ですが、今後ほかの OS にも拡張する予定です。

    2 台目の Gateway をインストールするのは、**厳格な分離** または完全に別々のボットが必要な場合だけです。

    ドキュメント: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes), [Multiple gateways](/ja-JP/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## 環境変数と .env の読み込み

<AccordionGroup>
  <Accordion title="OpenClaw は環境変数をどのように読み込みますか？">
    OpenClaw は親プロセス（shell、launchd/systemd、CI など）から env vars を読み取り、さらに次も読み込みます。

    - 現在の作業ディレクトリの `.env`
    - `~/.openclaw/.env`（別名 `$OPENCLAW_STATE_DIR/.env`）のグローバルフォールバック `.env`

    どちらの `.env` ファイルも、既存の env vars を上書きしません。

    設定内でインライン env vars を定義することもできます（プロセス env に存在しない場合のみ適用）。

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    完全な優先順位と読み込み元については [/environment](/ja-JP/help/environment) を参照してください。

  </Accordion>

  <Accordion title="service 経由で Gateway を起動したら env vars が消えました。どうすればよいですか？">
    よくある修正方法は 2 つあります。

    1. `~/.openclaw/.env` に不足しているキーを入れてください。そうすれば、service がシェルの env を継承しなくても読み込まれます。
    2. shell import を有効にします（任意の利便機能）。

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

    これにより login shell が実行され、想定される不足キーだけが取り込まれます（上書きはしません）。環境変数での同等設定:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`。

  </Accordion>

  <Accordion title='`COPILOT_GITHUB_TOKEN` を設定したのに、models status に「Shell env: off」と表示されるのはなぜですか？'>
    `openclaw models status` は **shell env import** が有効かどうかを報告します。「Shell env: off」は、
    env vars が不足していることを意味するのではなく、OpenClaw が
    login shell を自動読み込みしないことを意味します。

    Gateway が service（launchd/systemd）として動いている場合、シェルの
    環境は継承されません。次のいずれかで修正してください。

    1. token を `~/.openclaw/.env` に入れる:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. または shell import（`env.shellEnv.enabled: true`）を有効にする。
    3. または設定の `env` ブロックに追加する（不足時のみ適用）。

    その後、gateway を再起動して再確認してください。

    ```bash
    openclaw models status
    ```

    Copilot token は `COPILOT_GITHUB_TOKEN` から読み取られます（`GH_TOKEN` / `GITHUB_TOKEN` も可）。
    [/concepts/model-providers](/ja-JP/concepts/model-providers) と [/environment](/ja-JP/help/environment) を参照してください。

  </Accordion>
</AccordionGroup>

## セッションと複数チャット

<AccordionGroup>
  <Accordion title="新しい会話を始めるにはどうすればよいですか？">
    `/new` または `/reset` を単独のメッセージとして送信してください。[Session management](/ja-JP/concepts/session) を参照してください。
  </Accordion>

  <Accordion title="`/new` を一度も送らなければ、セッションは自動でリセットされますか？">
    セッションは `session.idleMinutes` 経過後に期限切れにできますが、これは **デフォルトでは無効** です（デフォルト **0**）。
    アイドル期限切れを有効にするには正の値を設定してください。有効時は、アイドル期間後の **次の**
    メッセージで、その chat key に対する新しい session id が開始されます。
    これは transcript を削除するのではなく、新しいセッションを開始するだけです。

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="OpenClaw インスタンスのチーム（CEO 1 人と多くのエージェント）を作る方法はありますか？">
    はい。**マルチエージェントルーティング** と **サブエージェント** を使います。1 つのコーディネーター
    agent と、独自の workspaces とモデルを持つ複数の worker agents を作れます。

    とはいえ、これは **楽しい実験** として捉えるのが最適です。トークン消費が大きく、
    多くの場合、セッションを分けた 1 つのボットを使うより非効率です。私たちが
    想定している一般的なモデルは、1 つのボットに話しかけ、並列作業には異なるセッションを使うことです。その
    ボットは必要に応じてサブエージェントも起動できます。

    ドキュメント: [Multi-agent routing](/ja-JP/concepts/multi-agent), [Sub-agents](/ja-JP/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="タスクの途中でコンテキストが切り詰められたのはなぜですか？ どう防げますか？">
    Session context はモデルの window に制限されます。長いチャット、大きなツール出力、または多数の
    ファイルによって Compaction や切り詰めが発生することがあります。

    効果のある方法:

    - ボットに現在の状態を要約してファイルに書くよう頼む。
    - 長いタスクの前に `/compact` を使い、話題を切り替えるときは `/new` を使う。
    - 重要なコンテキストは workspace に保持し、ボットにそれを再読させる。
    - 長時間または並列の作業にはサブエージェントを使い、メインチャットを小さく保つ。
    - これが頻繁に起きるなら、より大きい context window を持つモデルを選ぶ。

  </Accordion>

  <Accordion title="OpenClaw を完全にリセットしつつインストールは残すにはどうすればよいですか？">
    reset コマンドを使ってください。

    ```bash
    openclaw reset
    ```

    非対話の完全リセット:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    その後、セットアップを再実行します。

    ```bash
    openclaw onboard --install-daemon
    ```

    注意:

    - 既存の設定を検出すると、オンボーディングでも **Reset** を提案します。[Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。
    - profiles（`--profile` / `OPENCLAW_PROFILE`）を使っていた場合は、各 state dir をリセットしてください（デフォルトは `~/.openclaw-<profile>`）。
    - dev reset: `openclaw gateway --dev --reset`（dev 専用。dev config + credentials + sessions + workspace を消去します）。

  </Accordion>

  <Accordion title='「context too large」エラーが出ます。どうやってリセットまたは compact すればよいですか？'>
    次のいずれかを使ってください。

    - **Compact**（会話は維持しつつ、古いターンを要約します）:

      ```
      /compact
      ```

      または、要約内容を指定するには `/compact <instructions>`。

    - **Reset**（同じ chat key に対して新しい session ID を開始）:

      ```
      /new
      /reset
      ```

    それでも繰り返し起きる場合:

    - **session pruning**（`agents.defaults.contextPruning`）を有効化または調整して、古いツール出力を削減してください。
    - より大きい context window を持つモデルを使ってください。

    ドキュメント: [Compaction](/ja-JP/concepts/compaction), [Session pruning](/ja-JP/concepts/session-pruning), [Session management](/ja-JP/concepts/session).

  </Accordion>

  <Accordion title='「LLM request rejected: messages.content.tool_use.input field required」と表示されるのはなぜですか？'>
    これは provider のバリデーションエラーです。モデルが必要な
    `input` なしで `tool_use` ブロックを出力しました。通常はセッション履歴が古いか壊れていることを意味し（長いスレッドや
    tool/schema 変更の後によく起こります）。

    修正方法: `/new`（単独メッセージ）で新しいセッションを開始してください。

  </Accordion>

  <Accordion title="30 分ごとに heartbeat メッセージが届くのはなぜですか？">
    Heartbeat はデフォルトで **30m** ごとに実行されます（OAuth auth 使用時は **1h**）。調整または無効化するには:

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

    `HEARTBEAT.md` が存在していても、実質的に空（空行と `# Heading` のような markdown
    ヘッダーのみ）の場合、OpenClaw は API 呼び出しを節約するため heartbeat 実行をスキップします。
    ファイルが存在しない場合、heartbeat は引き続き実行され、モデルが何をするかを判断します。

    エージェント単位の override には `agents.list[].heartbeat` を使います。ドキュメント: [Heartbeat](/ja-JP/gateway/heartbeat)。

  </Accordion>

  <Accordion title='WhatsApp グループに「bot account」を追加する必要がありますか？'>
    いいえ。OpenClaw は **自分自身のアカウント** で動作するため、自分がそのグループにいれば、OpenClaw はそれを見られます。
    デフォルトでは、送信者を許可するまでグループ返信はブロックされます（`groupPolicy: "allowlist"`）。

    グループ返信を **自分だけ** がトリガーできるようにしたい場合:

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

  <Accordion title="WhatsApp グループの JID を取得するにはどうすればよいですか？">
    方法 1（最速）: ログを追いながら、グループにテストメッセージを送信します。

    ```bash
    openclaw logs --follow --json
    ```

    `@g.us` で終わる `chatId`（または `from`）を探してください。例:
    `1234567890-1234567890@g.us`。

    方法 2（すでに設定/allowlist 済みの場合）: 設定からグループを一覧表示します。

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    ドキュメント: [WhatsApp](/ja-JP/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs)。

  </Accordion>

  <Accordion title="OpenClaw がグループで返信しないのはなぜですか？">
    よくある原因は 2 つあります。

    - mention gating がオンです（デフォルト）。ボットを @mention する必要があります（または `mentionPatterns` に一致させる必要があります）。
    - `channels.whatsapp.groups` を `"*"` なしで設定していて、そのグループが allowlist に入っていません。

    [Groups](/ja-JP/channels/groups) と [Group messages](/ja-JP/channels/group-messages) を参照してください。

  </Accordion>

  <Accordion title="グループ/スレッドは DM とコンテキストを共有しますか？">
    ダイレクトチャットはデフォルトでメインセッションに集約されます。グループ/チャネルは独自の session key を持ち、Telegram topics / Discord threads も別セッションです。[Groups](/ja-JP/channels/groups) と [Group messages](/ja-JP/channels/group-messages) を参照してください。
  </Accordion>

  <Accordion title="workspace とエージェントは何個まで作成できますか？">
    厳密な上限はありません。数十個（場合によっては数百個）でも問題ありませんが、次の点には注意してください。

    - **ディスク使用量の増加:** sessions + transcripts は `~/.openclaw/agents/<agentId>/sessions/` 配下に保存されます。
    - **トークンコスト:** エージェントが増えるほど、同時モデル利用も増えます。
    - **運用負荷:** エージェントごとの auth profiles、workspaces、channel routing が必要です。

    ヒント:

    - エージェントごとに **アクティブな** workspace を 1 つ保ちます（`agents.defaults.workspace`）。
    - ディスクが増えてきたら、古い sessions を整理してください（JSONL や store entries を削除）。
    - `openclaw doctor` を使って、不要な workspaces や profile の不一致を見つけてください。

  </Accordion>

  <Accordion title="複数のボットやチャットを同時に実行できますか（Slack など）？ どう設定すればよいですか？">
    はい。**Multi-Agent Routing** を使って複数の分離されたエージェントを実行し、
    channel/account/peer ごとに受信メッセージをルーティングしてください。Slack はチャネルとしてサポートされており、特定のエージェントにバインドできます。

    browser アクセスは強力ですが、「人間にできることは何でもできる」わけではありません。bot 対策、CAPTCHA、MFA によって
    自動化がブロックされることはあります。最も信頼性の高い browser 制御を行うには、ホスト上でローカル Chrome MCP を使うか、
    実際に browser を実行しているマシン上で CDP を使ってください。

    ベストプラクティスのセットアップ:

    - 常時稼働の Gateway host（VPS/Mac mini）。
    - 役割ごとに 1 つのエージェント（bindings）。
    - それらのエージェントにバインドされた Slack channel。
    - 必要に応じて、Chrome MCP または Node を介したローカル browser。

    ドキュメント: [Multi-Agent Routing](/ja-JP/concepts/multi-agent), [Slack](/ja-JP/channels/slack),
    [Browser](/ja-JP/tools/browser), [Nodes](/ja-JP/nodes).

  </Accordion>
</AccordionGroup>

## モデル: デフォルト、選択、エイリアス、切り替え

<AccordionGroup>
  <Accordion title='「デフォルトモデル」とは何ですか？'>
    OpenClaw のデフォルトモデルは、次で設定したものです。

    ```
    agents.defaults.model.primary
    ```

    モデルは `provider/model` として参照されます（例: `openai/gpt-5.4`）。provider を省略した場合、OpenClaw はまずエイリアスを試し、次にその正確な model id に対する一意の設定済み provider 一致を試し、それでもだめなら非推奨の互換経路として設定済みのデフォルト provider にフォールバックします。その provider が設定済みのデフォルトモデルをもはや提供していない場合、OpenClaw は古い削除済み provider のデフォルトを表示する代わりに、最初の設定済み provider/model にフォールバックします。それでも、**明示的に** `provider/model` を設定するべきです。

  </Accordion>

  <Accordion title="おすすめのモデルは何ですか？">
    **推奨デフォルト:** 利用中の provider スタックで使える、最新世代の最も強力なモデルを使ってください。
    **tool 対応または信頼できない入力を扱うエージェント向け:** コストよりモデル性能を優先してください。
    **日常的/低リスクのチャット向け:** より安価な fallback models を使い、エージェントの役割ごとにルーティングしてください。

    MiniMax には専用ドキュメントがあります: [MiniMax](/ja-JP/providers/minimax) と
    [Local models](/ja-JP/gateway/local-models)。

    経験則として、高リスクな作業には **払える範囲で最高のモデル** を使い、日常チャットや要約にはより安価な
    モデルを使ってください。モデルはエージェントごとにルーティングでき、長いタスクはサブエージェントで
    並列化できます（各サブエージェントはトークンを消費します）。[Models](/ja-JP/concepts/models) と
    [Sub-agents](/ja-JP/tools/subagents) を参照してください。

    強い警告: 弱いモデルや過度に量子化されたモデルは、prompt
    injection や危険な挙動に対してより脆弱です。[Security](/ja-JP/gateway/security) を参照してください。

    詳しくは: [Models](/ja-JP/concepts/models)。

  </Accordion>

  <Accordion title="設定を消さずにモデルを切り替えるにはどうすればよいですか？">
    **モデルコマンド** を使うか、**model** フィールドだけを編集してください。設定全体の置換は避けてください。

    安全な方法:

    - チャット内で `/model`（簡単、セッション単位）
    - `openclaw models set ...`（モデル設定だけを更新）
    - `openclaw configure --section model`（対話式）
    - `~/.openclaw/openclaw.json` の `agents.defaults.model` を編集

    設定全体を置き換える意図がない限り、部分オブジェクトで `config.apply` を使わないでください。
    RPC 編集では、まず `config.schema.lookup` で確認し、`config.patch` を優先してください。lookup のペイロードには、正規化されたパス、浅いスキーマのドキュメント/制約、直下の子要約が含まれます。
    部分更新用です。
    もし設定を上書きしてしまった場合は、バックアップから復元するか、`openclaw doctor` を再実行して修復してください。

    ドキュメント: [Models](/ja-JP/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/ja-JP/gateway/doctor).

  </Accordion>

  <Accordion title="セルフホストモデル（llama.cpp、vLLM、Ollama）を使えますか？">
    はい。ローカルモデルへの最も簡単な経路は Ollama です。

    最短セットアップ:

    1. `https://ollama.com/download` から Ollama をインストール
    2. `ollama pull gemma4` のようにローカルモデルを取得
    3. クラウドモデルも使いたい場合は `ollama signin` を実行
    4. `openclaw onboard` を実行して `Ollama` を選択
    5. `Local` または `Cloud + Local` を選択

    注意:

    - `Cloud + Local` ではクラウドモデルに加えてローカルの Ollama モデルも使えます
    - `kimi-k2.5:cloud` のようなクラウドモデルはローカルでの pull は不要です
    - 手動で切り替える場合は、`openclaw models list` と `openclaw models set ollama/<model>` を使ってください

    セキュリティ注意: 小さいモデルや大きく量子化されたモデルは、prompt
    injection に対してより脆弱です。tools を使えるボットには **大きなモデル** を強く推奨します。
    それでも小さなモデルを使いたい場合は、サンドボックス化と厳格な tool allowlists を有効にしてください。

    ドキュメント: [Ollama](/ja-JP/providers/ollama), [Local models](/ja-JP/gateway/local-models),
    [Model providers](/ja-JP/concepts/model-providers), [Security](/ja-JP/gateway/security),
    [Sandboxing](/ja-JP/gateway/sandboxing).

  </Accordion>

  <Accordion title="OpenClaw、Flawd、Krill ではどのモデルを使っていますか？">
    - これらのデプロイは異なる場合があり、時間とともに変わることがあります。固定の provider 推奨はありません。
    - 各 gateway の現在のランタイム設定は `openclaw models status` で確認してください。
    - セキュリティ重視/tool 対応エージェントには、利用可能な最新世代で最も強力なモデルを使ってください。
  </Accordion>

  <Accordion title="再起動せずにその場でモデルを切り替えるにはどうすればよいですか？">
    単独メッセージとして `/model` コマンドを使ってください。

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    これらは組み込みのエイリアスです。カスタムエイリアスは `agents.defaults.models` で追加できます。

    利用可能なモデルは `/model`、`/model list`、または `/model status` で一覧表示できます。

    `/model`（および `/model list`）は、コンパクトな番号付きピッカーを表示します。番号で選択します。

    ```
    /model 3
    ```

    provider に対して特定の auth profile を強制することもできます（セッション単位）。

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    ヒント: `/model status` では、どのエージェントが有効か、どの `auth-profiles.json` ファイルが使われているか、次にどの auth profile が試されるかが表示されます。
    また、利用可能な場合は設定済み provider endpoint（`baseUrl`）と API mode（`api`）も表示されます。

    **`@profile` で設定した profile の固定を解除するにはどうすればよいですか？**

    `@profile` サフィックス **なし** で `/model` を再実行してください。

    ```
    /model anthropic/claude-opus-4-6
    ```

    デフォルトに戻したい場合は、`/model` から選ぶか（または `/model <default provider/model>` を送ってください）。
    どの auth profile が有効かは `/model status` で確認してください。

  </Accordion>

  <Accordion title="日常タスクに GPT 5.2、コーディングに Codex 5.3 を使えますか？">
    はい。1 つをデフォルトに設定し、必要に応じて切り替えてください。

    - **簡単な切り替え（セッション単位）:** 日常タスクには `/model gpt-5.4`、Codex OAuth でのコーディングには `/model openai-codex/gpt-5.4`。
    - **デフォルト + 切り替え:** `agents.defaults.model.primary` を `openai/gpt-5.4` に設定し、コーディング時に `openai-codex/gpt-5.4` に切り替えます（またはその逆）。
    - **サブエージェント:** コーディングタスクを、別のデフォルトモデルを持つサブエージェントにルーティングします。

    [Models](/ja-JP/concepts/models) と [Slash commands](/ja-JP/tools/slash-commands) を参照してください。

  </Accordion>

  <Accordion title="GPT 5.4 で fast mode を設定するにはどうすればよいですか？">
    セッショントグルまたは設定デフォルトのどちらかを使います。

    - **セッション単位:** セッションが `openai/gpt-5.4` または `openai-codex/gpt-5.4` を使っている間に `/fast on` を送信します。
    - **モデル単位のデフォルト:** `agents.defaults.models["openai/gpt-5.4"].params.fastMode` を `true` に設定します。
    - **Codex OAuth にも:** `openai-codex/gpt-5.4` も使う場合は、そちらにも同じフラグを設定します。

    例:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    OpenAI では、fast mode はサポートされているネイティブ Responses リクエスト上で `service_tier = "priority"` に対応します。セッションの `/fast` override は設定デフォルトより優先されます。

    [Thinking and fast mode](/ja-JP/tools/thinking) と [OpenAI fast mode](/ja-JP/providers/openai#openai-fast-mode) を参照してください。

  </Accordion>

  <Accordion title='「Model ... is not allowed」と表示されたあと返信がないのはなぜですか？'>
    `agents.defaults.models` が設定されている場合、それは `/model` とあらゆる
    セッション override の **allowlist** になります。その一覧にないモデルを選ぶと、次が返されます。

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    このエラーは通常の返信の **代わりに** 返されます。修正方法: そのモデルを
    `agents.defaults.models` に追加するか、allowlist を削除するか、`/model list` からモデルを選んでください。

  </Accordion>

  <Accordion title='「Unknown model: minimax/MiniMax-M2.7」と表示されるのはなぜですか？'>
    これは **provider が設定されていない** ことを意味します（MiniMax provider 設定または auth
    profile が見つからなかったため）、そのモデルを解決できません。

    修正チェックリスト:

    1. 現在の OpenClaw リリースに更新する（またはソースの `main` から実行する）その後 gateway を再起動する。
    2. MiniMax が設定されていること（ウィザードまたは JSON）、または一致する provider を注入できるよう
       env/auth profiles に MiniMax auth が存在することを確認する
       （`minimax` には `MINIMAX_API_KEY`、`minimax-portal` には `MINIMAX_OAUTH_TOKEN` または保存済み MiniMax
       OAuth）。
    3. 自分の auth 経路に対して正確な model id（大文字小文字を区別）を使う:
       API key 構成なら `minimax/MiniMax-M2.7` または `minimax/MiniMax-M2.7-highspeed`、
       OAuth 構成なら `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed`。
    4. 次を実行します:

       ```bash
       openclaw models list
       ```

       そして一覧から選んでください（またはチャット内で `/model list`）。

    [MiniMax](/ja-JP/providers/minimax) と [Models](/ja-JP/concepts/models) を参照してください。

  </Accordion>

  <Accordion title="MiniMax をデフォルトにして、複雑なタスクでは OpenAI を使えますか？">
    はい。**MiniMax をデフォルト** にして、必要なときに **セッション単位** でモデルを切り替えてください。
    fallbacks は **エラー** 用であり、「難しいタスク」用ではないため、`/model` または別エージェントを使ってください。

    **オプション A: セッション単位で切り替え**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    その後:

    ```
    /model gpt
    ```

    **オプション B: 別エージェント**

    - Agent A のデフォルト: MiniMax
    - Agent B のデフォルト: OpenAI
    - エージェントごとにルーティングするか、`/agent` で切り替える

    ドキュメント: [Models](/ja-JP/concepts/models), [Multi-Agent Routing](/ja-JP/concepts/multi-agent), [MiniMax](/ja-JP/providers/minimax), [OpenAI](/ja-JP/providers/openai).

  </Accordion>

  <Accordion title="opus / sonnet / gpt は組み込みショートカットですか？">
    はい。OpenClaw にはいくつかのデフォルト shorthand が含まれています（`agents.defaults.models` にそのモデルが存在する場合にのみ適用されます）。

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    同じ名前で独自の alias を設定した場合は、あなたの値が優先されます。

  </Accordion>

  <Accordion title="モデルショートカット（エイリアス）を定義/上書きするにはどうすればよいですか？">
    エイリアスは `agents.defaults.models.<modelId>.alias` から取得されます。例:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    その後、`/model sonnet`（またはサポートされている場合は `/<alias>`）でその model ID に解決されます。

  </Accordion>

  <Accordion title="OpenRouter や Z.AI のような他の provider のモデルを追加するにはどうすればよいですか？">
    OpenRouter（従量課金、多数のモデル）:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    Z.AI（GLM models）:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "zai/glm-5" },
          models: { "zai/glm-5": {} },
        },
      },
      env: { ZAI_API_KEY: "..." },
    }
    ```

    provider/model を参照していても、必要な provider key がない場合は、ランタイム認証エラーになります（例: `No API key found for provider "zai"`）。

    **新しいエージェントを追加したあとに「No API key found for provider」が表示される**

    これは通常、**新しいエージェント** の auth store が空であることを意味します。auth はエージェントごとで、
    次に保存されます。

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    修正方法:

    - `openclaw agents add <id>` を実行し、ウィザード中に auth を設定する。
    - または、メインエージェントの `agentDir` から `auth-profiles.json` を新しいエージェントの `agentDir` にコピーする。

    エージェント間で `agentDir` を使い回しては **いけません**。auth/session の衝突が発生します。

  </Accordion>
</AccordionGroup>

## モデルのフェイルオーバーと「All models failed」

<AccordionGroup>
  <Accordion title="フェイルオーバーはどのように動作しますか？">
    フェイルオーバーは 2 段階で発生します。

    1. 同じ provider 内での **auth profile rotation**。
    2. `agents.defaults.model.fallbacks` 内の次のモデルへの **model fallback**。

    失敗した profiles にはクールダウンが適用されます（指数バックオフ）。そのため、provider がレート制限中または一時的に失敗していても、OpenClaw は応答を継続できます。

    rate-limit bucket には単純な `429` レスポンス以上のものが含まれます。OpenClaw は
    `Too many concurrent requests`、
    `ThrottlingException`、`concurrency limit reached`、
    `workers_ai ... quota limit exceeded`、`resource exhausted`、および定期的な
    usage-window 制限（`weekly/monthly limit reached`）のようなメッセージも
    フェイルオーバーに値するレート制限として扱います。

    一見課金関連に見える応答でも `402` ではないことがあり、HTTP `402`
    応答の一部もこの一時的 bucket に留まります。provider が
    `401` または `403` で明示的な課金テキストを返した場合、OpenClaw はそれを
    課金レーンに維持できますが、provider 固有のテキストマッチャーはその
    provider に限定されたままです（たとえば OpenRouter の `Key limit exceeded`）。`402`
    メッセージが、代わりに再試行可能な usage-window や
    organization/workspace の利用上限（`daily limit reached, resets tomorrow`、
    `organization spending limit exceeded`）のように見える場合、OpenClaw はそれを
    長期の課金停止ではなく `rate_limit` として扱います。

    context overflow エラーは異なります。たとえば
    `request_too_large`、`input exceeds the maximum number of tokens`、
    `input token count exceeds the maximum number of input tokens`、
    `input is too long for the model`、または `ollama error: context length
    exceeded` といったシグネチャは、model
    fallback を進めるのではなく、Compaction/retry 経路に留まります。

    汎用的な server error テキストは、「unknown/error を含むものすべて」よりも意図的に狭くされています。
    OpenClaw は、Anthropic の素の `An unknown error occurred`、OpenRouter の素の
    `Provider returned error`、`Unhandled stop reason:
    error` のような stop-reason エラー、JSON の `api_error` ペイロードと一時的なサーバーテキスト
    （`internal server error`、`unknown error, 520`、`upstream error`、`backend
    error`）、および `ModelNotReadyException` のような provider-busy エラーを、
    provider コンテキストが一致する場合にはフェイルオーバーに値する timeout/overloaded シグナルとして扱います。
    `LLM request failed with an unknown
    error.` のような汎用内部 fallback テキストは慎重に扱われ、それ単体では model fallback を引き起こしません。

  </Accordion>

  <Accordion title='「No credentials found for profile anthropic:default」とはどういう意味ですか？'>
    これは、システムが auth profile ID `anthropic:default` を使おうとしたが、想定される auth store 内でその資格情報を見つけられなかったことを意味します。

    **修正チェックリスト:**

    - **auth profiles の保存場所を確認する**（新旧パス）
      - 現行: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - レガシー: `~/.openclaw/agent/*`（`openclaw doctor` により移行）
    - **env var が Gateway に読み込まれていることを確認する**
      - `ANTHROPIC_API_KEY` をシェルに設定していても、Gateway を systemd/launchd 経由で動かしている場合は継承されないことがあります。`~/.openclaw/.env` に入れるか、`env.shellEnv` を有効にしてください。
    - **正しいエージェントを編集していることを確認する**
      - マルチエージェント構成では、複数の `auth-profiles.json` ファイルが存在し得ます。
    - **model/auth status を健全性確認する**
      - `openclaw models status` を使って、設定済みモデルと provider の認証状態を確認してください。

    **「No credentials found for profile anthropic」の修正チェックリスト**

    これは、その実行が Anthropic auth profile に固定されているが、Gateway が
    自分の auth store でそれを見つけられないことを意味します。

    - **Claude CLI を使う**
      - gateway host 上で `openclaw models auth login --provider anthropic --method cli --set-default` を実行してください。
    - **代わりに API key を使いたい場合**
      - **gateway host** 上の `~/.openclaw/.env` に `ANTHROPIC_API_KEY` を入れてください。
      - 不足している profile を強制する固定順序をクリアします:

        ```bash
        openclaw models auth order clear --provider anthropic
        ```

    - **gateway host 上でコマンドを実行していることを確認する**
      - remote mode では、auth profiles はローカルノート PC ではなく gateway マシン上にあります。

  </Accordion>

  <Accordion title="なぜ Google Gemini も試されて失敗したのですか？">
    モデル設定に Google Gemini が fallback として含まれている場合（または Gemini の shorthand に切り替えた場合）、OpenClaw は model fallback 中にそれも試します。Google の資格情報を設定していないと、`No API key found for provider "google"` が表示されます。

    修正方法: Google auth を提供するか、fallback がそこへルーティングしないように `agents.defaults.model.fallbacks` / aliases から Google モデルを削除または回避してください。

    **LLM request rejected: thinking signature required（Google Antigravity）**

    原因: セッション履歴に **署名のない thinking blocks** が含まれています（中断された/部分的な stream に由来することが多いです）。Google Antigravity は thinking blocks に署名を要求します。

    修正方法: OpenClaw は現在、Google Antigravity Claude 用に署名のない thinking blocks を除去します。それでも表示される場合は、**新しいセッション** を開始するか、そのエージェントで `/thinking off` を設定してください。

  </Accordion>
</AccordionGroup>

## Auth profiles: それが何かと管理方法

関連: [/concepts/oauth](/ja-JP/concepts/oauth)（OAuth フロー、トークン保存、マルチアカウントのパターン）

<AccordionGroup>
  <Accordion title="auth profile とは何ですか？">
    auth profile は、provider に紐づく名前付きの資格情報レコード（OAuth または API key）です。profiles は次に保存されます。

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

  </Accordion>

  <Accordion title="一般的な profile ID にはどのようなものがありますか？">
    OpenClaw は、次のような provider 接頭辞付き ID を使います。

    - `anthropic:default`（メールアドレスの識別情報がない場合によく使われる）
    - OAuth アイデンティティ用の `anthropic:<email>`
    - 自分で選ぶカスタム ID（例: `anthropic:work`）

  </Accordion>

  <Accordion title="どの auth profile を最初に試すか制御できますか？">
    はい。設定では、profiles 用の任意メタデータと provider ごとの順序（`auth.order.<provider>`）をサポートしています。これは secrets を保存するものではなく、ID を provider/mode に対応付け、rotation 順序を設定します。

    OpenClaw は、その profile が短い **cooldown**（rate limits/timeouts/auth failures）またはより長い **disabled** 状態（billing/insufficient credits）にある場合、一時的にスキップすることがあります。これを確認するには、`openclaw models status --json` を実行して `auth.unusableProfiles` を確認してください。調整項目: `auth.cooldowns.billingBackoffHours*`。

    rate-limit cooldowns はモデル単位になることがあります。あるモデルで cooldown 中の profile でも、同じ provider の兄弟モデルでは利用可能なことがありますが、billing/disabled の期間は profile 全体をブロックします。

    CLI では、**エージェント単位** の順序 override（そのエージェントの `auth-state.json` に保存）も設定できます。

    ```bash
    # 設定済みデフォルトエージェントを対象にします（--agent を省略）
    openclaw models auth order get --provider anthropic

    # rotation を 1 つの profile に固定（これだけを試す）
    openclaw models auth order set --provider anthropic anthropic:default

    # または明示的な順序を設定（provider 内で fallback）
    openclaw models auth order set --provider anthropic anthropic:work anthropic:default

    # override をクリア（config auth.order / round-robin に戻す）
    openclaw models auth order clear --provider anthropic
    ```

    特定のエージェントを対象にするには:

    ```bash
    openclaw models auth order set --provider anthropic --agent main anthropic:default
    ```

    実際に何が試されるかを確認するには、次を使ってください。

    ```bash
    openclaw models status --probe
    ```

    保存済み profile が明示的な順序から省かれている場合、probe は
    その profile を黙って試す代わりに `excluded_by_auth_order` を報告します。

  </Accordion>

  <Accordion title="OAuth と API key の違いは何ですか？">
    OpenClaw は両方をサポートしています。

    - **OAuth** は、多くの場合サブスクリプションアクセスを活用します（該当する場合）。
    - **API keys** は従量課金を使います。

    ウィザードは Anthropic Claude CLI、OpenAI Codex OAuth、API keys を明示的にサポートしています。

  </Accordion>
</AccordionGroup>

## Gateway: ポート、「already running」、remote mode

<AccordionGroup>
  <Accordion title="Gateway はどのポートを使いますか？">
    `gateway.port` は、WebSocket + HTTP（Control UI、hooks など）の単一多重化ポートを制御します。

    優先順位:

    ```
    --port > OPENCLAW_GATEWAY_PORT > gateway.port > デフォルト 18789
    ```

  </Accordion>

  <Accordion title='`openclaw gateway status` に「Runtime: running」と出るのに「RPC probe: failed」と出るのはなぜですか？'>
    これは、「running」が **supervisor**（launchd/systemd/schtasks）の視点だからです。一方、RPC probe は CLI が実際に gateway WebSocket に接続して `status` を呼び出している結果です。

    `openclaw gateway status` を使い、次の行を信頼してください。

    - `Probe target:`（probe が実際に使った URL）
    - `Listening:`（実際にそのポートで bind されているもの）
    - `Last gateway error:`（プロセスは生きているがポートが listen していないときの一般的な根本原因）

  </Accordion>

  <Accordion title='`openclaw gateway status` で「Config (cli)」と「Config (service)」が異なるのはなぜですか？'>
    編集している設定ファイルと、service が実行している設定ファイルが異なっています（多くは `--profile` / `OPENCLAW_STATE_DIR` の不一致です）。

    修正:

    ```bash
    openclaw gateway install --force
    ```

    これを、service に使わせたい同じ `--profile` / 環境で実行してください。

  </Accordion>

  <Accordion title='「another gateway instance is already listening」とはどういう意味ですか？'>
    OpenClaw は、起動時に即座に WebSocket listener を bind することでランタイムロックを強制します（デフォルト `ws://127.0.0.1:18789`）。`EADDRINUSE` で bind に失敗した場合、別のインスタンスがすでに listen していることを示す `GatewayLockError` を投げます。

    修正: 他のインスタンスを停止する、ポートを解放する、または `openclaw gateway --port <port>` で実行してください。

  </Accordion>

  <Accordion title="OpenClaw を remote mode（別の場所の Gateway にクライアント接続）で実行するにはどうすればよいですか？">
    `gateway.mode: "remote"` を設定し、リモートの WebSocket URL を指定します。必要に応じて shared-secret のリモート資格情報も指定できます。

    ```json5
    {
      gateway: {
        mode: "remote",
        remote: {
          url: "ws://gateway.tailnet:18789",
          token: "your-token",
          password: "your-password",
        },
      },
    }
    ```

    注意:

    - `openclaw gateway` は `gateway.mode` が `local` のときにのみ起動します（または override フラグを渡した場合）。
    - macOS アプリは設定ファイルを監視しており、これらの値が変わるとモードをライブで切り替えます。
    - `gateway.remote.token` / `.password` はクライアント側のリモート資格情報専用であり、それ自体でローカル gateway auth を有効にするものではありません。

  </Accordion>

  <Accordion title='Control UI に「unauthorized」と表示される（または再接続し続ける）のはどういうことですか？'>
    gateway の auth 経路と UI の auth 方法が一致していません。

    事実（コード上の挙動）:

    - Control UI は、現在のブラウザータブセッションと選択中の gateway URL に対して token を `sessionStorage` に保持するため、同一タブ内の再読み込みは長期的な `localStorage` token 永続化を復元しなくても動作し続けます。
    - `AUTH_TOKEN_MISMATCH` 時には、gateway が再試行ヒント（`canRetryWithDeviceToken=true`, `recommendedNextStep=retry_with_device_token`）を返した場合、信頼済みクライアントはキャッシュ済み device token で 1 回だけ制限付き再試行を行えます。
    - そのキャッシュトークン再試行では、device token とともに保存されたキャッシュ済みの承認 scopes も再利用されます。明示的な `deviceToken` / 明示的な `scopes` 呼び出し元は、キャッシュ scope を継承せず、要求した scope セットを維持します。
    - その再試行経路以外では、connect auth の優先順位は、明示的な shared token/password が最優先で、その次に明示的な `deviceToken`、次に保存済み device token、最後に bootstrap token です。
    - bootstrap token の scope チェックは role 接頭辞付きです。組み込みの bootstrap operator allowlist は operator 要求にしか対応せず、Node やその他の非 operator ロールでは、それぞれの role 接頭辞配下の scopes が依然として必要です。

    修正方法:

    - 最速: `openclaw dashboard`（ダッシュボード URL を表示 + コピーし、開こうとします。headless なら SSH ヒントも表示）。
    - まだ token がない場合: `openclaw doctor --generate-gateway-token`。
    - remote の場合は、まずトンネルします: `ssh -N -L 18789:127.0.0.1:18789 user@host` のあと `http://127.0.0.1:18789/` を開いてください。
    - shared-secret mode: `gateway.auth.token` / `OPENCLAW_GATEWAY_TOKEN` または `gateway.auth.password` / `OPENCLAW_GATEWAY_PASSWORD` を設定し、その一致する secret を Control UI 設定に貼り付けてください。
    - Tailscale Serve mode: `gateway.auth.allowTailscale` が有効であること、そして Tailscale の identity headers を迂回する生の loopback/tailnet URL ではなく Serve URL を開いていることを確認してください。
    - trusted-proxy mode: 同一ホストの loopback proxy や生の gateway URL ではなく、設定済みの non-loopback identity-aware proxy を経由していることを確認してください。
    - 1 回の再試行後も不一致が続く場合は、ペアリング済み device token をローテーション/再承認します:
      - `openclaw devices list`
      - `openclaw devices rotate --device <id> --role operator`
    - その rotate 呼び出しが拒否されたと言う場合は、次の 2 点を確認してください:
      - ペアリング済みデバイスセッションは、自分自身のデバイスだけをローテーションできます（`operator.admin` も持っている場合を除く）
      - 明示的な `--scope` 値は、呼び出し元の現在の operator scopes を超えられません
    - それでもだめなら、`openclaw status --all` を実行して [Troubleshooting](/ja-JP/gateway/troubleshooting) に従ってください。auth の詳細は [Dashboard](/web/dashboard) を参照してください。

  </Accordion>

  <Accordion title="`gateway.bind tailnet` を設定したら bind できず、何も listen しません">
    `tailnet` bind は、ネットワークインターフェースから Tailscale IP（100.64.0.0/10）を選びます。マシンが Tailscale に参加していない（またはインターフェースがダウンしている）場合、bind 先がありません。

    修正:

    - そのホストで Tailscale を起動する（100.x アドレスを持つようにする）、または
    - `gateway.bind: "loopback"` / `"lan"` に切り替える。

    注意: `tailnet` は明示指定です。`auto` は loopback を優先します。tailnet のみに bind したい場合は `gateway.bind: "tailnet"` を使ってください。

  </Accordion>

  <Accordion title="同じホストで複数の Gateways を実行できますか？">
    通常はできません。1 つの Gateway で複数のメッセージングチャネルとエージェントを実行できます。複数の Gateways を使うのは、冗長性（例: rescue bot）や厳格な分離が必要な場合だけです。

    可能ではありますが、次を分離する必要があります。

    - `OPENCLAW_CONFIG_PATH`（インスタンスごとの設定）
    - `OPENCLAW_STATE_DIR`（インスタンスごとの state）
    - `agents.defaults.workspace`（workspace の分離）
    - `gateway.port`（一意のポート）

    クイックセットアップ（推奨）:

    - インスタンスごとに `openclaw --profile <name> ...` を使う（`~/.openclaw-<name>` を自動作成）。
    - 各 profile 設定で一意の `gateway.port` を設定する（または手動実行なら `--port` を渡す）。
    - profile ごとの service をインストールする: `openclaw --profile <name> gateway install`。

    Profiles は service 名にも suffix を付けます（`ai.openclaw.<profile>`、レガシーの `com.openclaw.*`、`openclaw-gateway-<profile>.service`、`OpenClaw Gateway (<profile>)`）。
    完全なガイド: [Multiple gateways](/ja-JP/gateway/multiple-gateways)。

  </Accordion>

  <Accordion title='「invalid handshake」/ code 1008 とはどういう意味ですか？'>
    Gateway は **WebSocket サーバー** であり、最初のメッセージが
    `connect` フレームであることを期待しています。これ以外を受け取ると、接続を
    **code 1008**（ポリシー違反）で閉じます。

    よくある原因:

    - ブラウザーで **HTTP** URL（`http://...`）を開いた。WS クライアントではない。
    - ポートまたはパスが間違っている。
    - proxy や tunnel が auth headers を削除した、または非 Gateway リクエストを送信した。

    すぐできる修正:

    1. WS URL を使う: `ws://<host>:18789`（HTTPS なら `wss://...`）。
    2. WS ポートを通常のブラウザータブで開かない。
    3. auth が有効なら、`connect` フレームに token/password を含める。

    CLI または TUI を使っている場合、URL は次のようになります。

    ```
    openclaw tui --url ws://<host>:18789 --token <token>
    ```

    プロトコル詳細: [Gateway protocol](/ja-JP/gateway/protocol)。

  </Accordion>
</AccordionGroup>

## ログとデバッグ

<AccordionGroup>
  <Accordion title="ログはどこにありますか？">
    ファイルログ（構造化）:

    ```
    /tmp/openclaw/openclaw-YYYY-MM-DD.log
    ```

    安定したパスは `logging.file` で設定できます。ファイルログレベルは `logging.level` で制御します。コンソールの詳細度は `--verbose` と `logging.consoleLevel` で制御します。

    最速のログ追跡:

    ```bash
    openclaw logs --follow
    ```

    service/supervisor ログ（gateway が launchd/systemd 経由で動いている場合）:

    - macOS: `$OPENCLAW_STATE_DIR/logs/gateway.log` と `gateway.err.log`（デフォルト: `~/.openclaw/logs/...`、profiles では `~/.openclaw-<profile>/logs/...`）
    - Linux: `journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
    - Windows: `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

    詳しくは [Troubleshooting](/ja-JP/gateway/troubleshooting) を参照してください。

  </Accordion>

  <Accordion title="Gateway service を開始/停止/再起動するにはどうすればよいですか？">
    gateway ヘルパーを使ってください。

    ```bash
    openclaw gateway status
    openclaw gateway restart
    ```

    gateway を手動で実行している場合、`openclaw gateway --force` でポートを再取得できます。[Gateway](/ja-JP/gateway) を参照してください。

  </Accordion>

  <Accordion title="Windows でターミナルを閉じてしまいました。OpenClaw を再起動するにはどうすればよいですか？">
    Windows には **2 つのインストールモード** があります。

    **1) WSL2（推奨）:** Gateway は Linux 内で動作します。

    PowerShell を開いて WSL に入り、その後再起動します:

    ```powershell
    wsl
    openclaw gateway status
    openclaw gateway restart
    ```

    service をインストールしていない場合は、フォアグラウンドで起動します。

    ```bash
    openclaw gateway run
    ```

    **2) ネイティブ Windows（非推奨）:** Gateway は Windows 上で直接動作します。

    PowerShell を開いて次を実行します:

    ```powershell
    openclaw gateway status
    openclaw gateway restart
    ```

    手動で実行している場合（service なし）は、次を使います。

    ```powershell
    openclaw gateway run
    ```

    ドキュメント: [Windows (WSL2)](/ja-JP/platforms/windows), [Gateway service runbook](/ja-JP/gateway)。

  </Accordion>

  <Accordion title="Gateway は動いているのに返信が届きません。何を確認すべきですか？">
    まず簡単な健全性チェックから始めてください。

    ```bash
    openclaw status
    openclaw models status
    openclaw channels status
    openclaw logs --follow
    ```

    よくある原因:

    - **gateway host** 上で model auth が読み込まれていない（`models status` を確認）。
    - channel pairing/allowlist により返信がブロックされている（channel 設定 + ログを確認）。
    - WebChat/Dashboard が正しい token なしで開かれている。

    remote の場合は、tunnel/Tailscale 接続が有効であり、
    Gateway WebSocket に到達できることを確認してください。

    ドキュメント: [Channels](/ja-JP/channels), [Troubleshooting](/ja-JP/gateway/troubleshooting), [Remote access](/ja-JP/gateway/remote)。

  </Accordion>

  <Accordion title='「Disconnected from gateway: no reason」と表示されたらどうすればよいですか？'>
    これは通常、UI が WebSocket 接続を失ったことを意味します。次を確認してください。

    1. Gateway は動作していますか？ `openclaw gateway status`
    2. Gateway は健全ですか？ `openclaw status`
    3. UI は正しい token を持っていますか？ `openclaw dashboard`
    4. remote の場合、tunnel/Tailscale 接続は有効ですか？

    その後、ログを追跡してください。

    ```bash
    openclaw logs --follow
    ```

    ドキュメント: [Dashboard](/web/dashboard), [Remote access](/ja-JP/gateway/remote), [Troubleshooting](/ja-JP/gateway/troubleshooting)。

  </Accordion>

  <Accordion title="Telegram の setMyCommands が失敗します。何を確認すべきですか？">
    まずログと channel status を確認してください。

    ```bash
    openclaw channels status
    openclaw channels logs --channel telegram
    ```

    その後、エラーに応じて確認します。

    - `BOT_COMMANDS_TOO_MUCH`: Telegram メニューのエントリが多すぎます。OpenClaw はすでに Telegram の上限まで削って少ないコマンドで再試行しますが、それでも一部のメニュー項目は削除が必要です。plugin/skill/custom commands を減らすか、メニューが不要なら `channels.telegram.commands.native` を無効にしてください。
    - `TypeError: fetch failed`、`Network request for 'setMyCommands' failed!`、または類似のネットワークエラー: VPS 上または proxy の背後にいる場合は、外向き HTTPS が許可されていて `api.telegram.org` の DNS が正しく動くことを確認してください。

    Gateway がリモートにある場合は、Gateway host 上のログを見ていることを確認してください。

    ドキュメント: [Telegram](/ja-JP/channels/telegram), [Channel troubleshooting](/ja-JP/channels/troubleshooting)。

  </Accordion>

  <Accordion title="TUI に何も表示されません。何を確認すべきですか？">
    まず Gateway に到達でき、agent が実行できることを確認してください。

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    TUI では `/status` を使って現在の状態を確認します。chat
    channel で返信を期待している場合は、配信が有効になっていること（`/deliver on`）を確認してください。

    ドキュメント: [TUI](/web/tui), [Slash commands](/ja-JP/tools/slash-commands)。

  </Accordion>

  <Accordion title="Gateway を完全に停止してから開始するにはどうすればよいですか？">
    service をインストールしている場合:

    ```bash
    openclaw gateway stop
    openclaw gateway start
    ```

    これは **監視付き service**（macOS では launchd、Linux では systemd）を停止/開始します。
    Gateway がデーモンとしてバックグラウンド実行されている場合に使ってください。

    フォアグラウンドで実行している場合は、Ctrl-C で停止してから次を実行します。

    ```bash
    openclaw gateway run
    ```

    ドキュメント: [Gateway service runbook](/ja-JP/gateway)。

  </Accordion>

  <Accordion title="ELI5: `openclaw gateway restart` と `openclaw gateway` の違い">
    - `openclaw gateway restart`: **バックグラウンド service**（launchd/systemd）を再起動します。
    - `openclaw gateway`: このターミナルセッションで gateway を **フォアグラウンド** 実行します。

    service をインストールしている場合は gateway コマンド群を使ってください。`openclaw gateway` は
    一時的にフォアグラウンド実行したいときに使います。

  </Accordion>

  <Accordion title="失敗時に詳細を増やす最速の方法">
    より詳しいコンソール出力を得るには、Gateway を `--verbose` 付きで起動してください。その後、ログファイルを確認して channel auth、model routing、RPC エラーを調べてください。
  </Accordion>
</AccordionGroup>

## メディアと添付ファイル

<AccordionGroup>
  <Accordion title="Skill が画像/PDF を生成したのに、何も送信されませんでした">
    agent からの送信添付ファイルには、`MEDIA:<path-or-url>` 行（単独行）が必要です。[OpenClaw assistant setup](/ja-JP/start/openclaw) と [Agent send](/ja-JP/tools/agent-send) を参照してください。

    CLI で送信する場合:

    ```bash
    openclaw message send --target +15555550123 --message "Here you go" --media /path/to/file.png
    ```

    あわせて次も確認してください。

    - 対象 channel が送信メディアをサポートしており、allowlist によってブロックされていないこと。
    - ファイルが provider のサイズ上限内であること（画像は最大 2048px にリサイズされます）。
    - `tools.fs.workspaceOnly=true` の場合、ローカルパス送信は workspace、temp/media-store、および sandbox 検証済みファイルに制限されます。
    - `tools.fs.workspaceOnly=false` の場合、agent がすでに読めるホストローカルファイルを `MEDIA:` で送信できますが、対象はメディア + 安全な文書タイプ（画像、音声、動画、PDF、Office 文書）に限られます。プレーンテキストや secret のようなファイルは引き続きブロックされます。

    [Images](/ja-JP/nodes/images) を参照してください。

  </Accordion>
</AccordionGroup>

## セキュリティとアクセス制御

<AccordionGroup>
  <Accordion title="OpenClaw を受信 DM に公開しても安全ですか？">
    受信 DM は信頼できない入力として扱ってください。デフォルトはリスク低減を意図したものです。

    - DM 対応チャネルでのデフォルト動作は **pairing** です:
      - 未知の送信者には pairing code が送られ、ボットはそのメッセージを処理しません。
      - 承認方法: `openclaw pairing approve --channel <channel> [--account <id>] <code>`
      - 保留中リクエストは **チャネルごとに 3 件** までです。コードが届かない場合は `openclaw pairing list --channel <channel> [--account <id>]` を確認してください。
    - DM を公開で開放するには、明示的な opt-in（`dmPolicy: "open"` と allowlist `"*"`）が必要です。

    危険な DM ポリシーを見つけるには `openclaw doctor` を実行してください。

  </Accordion>

  <Accordion title="prompt injection は公開ボットだけの問題ですか？">
    いいえ。prompt injection は、誰がボットに DM できるかではなく、**信頼できないコンテンツ** の問題です。
    アシスタントが外部コンテンツ（web search/fetch、browser ページ、メール、
    ドキュメント、添付ファイル、貼り付けられたログ）を読む場合、その内容には
    モデルを乗っ取ろうとする指示が含まれている可能性があります。これは **送信者が自分だけ** の場合でも起こり得ます。

    最大のリスクは tools が有効なときです。モデルがだまされて
    コンテキストを流出させたり、自分の代わりに tools を呼び出したりする可能性があります。影響範囲を減らすには:

    - 信頼できないコンテンツを要約するために、読み取り専用または tool 無効の「reader」agent を使う
    - tool 対応エージェントでは `web_search` / `web_fetch` / `browser` をオフに保つ
    - デコードされたファイル/文書テキストも信頼しないこと: OpenResponses の
      `input_file` とメディア添付の抽出はどちらも、生のファイルテキストを渡す代わりに、
      抽出テキストを明示的な外部コンテンツ境界マーカーで囲みます
    - サンドボックス化と厳格な tool allowlists

    詳細: [Security](/ja-JP/gateway/security)。

  </Accordion>

  <Accordion title="ボット専用のメール、GitHub アカウント、または電話番号を持たせるべきですか？">
    はい。ほとんどのセットアップではそうすべきです。ボットを別アカウントや別番号で分離すると、
    何か問題が起きたときの影響範囲を減らせます。また、個人アカウントに影響を与えずに
    資格情報のローテーションやアクセス取り消しもしやすくなります。

    まずは小さく始めてください。実際に必要な tools とアカウントにだけアクセスを与え、
    必要に応じて後から拡張してください。

    ドキュメント: [Security](/ja-JP/gateway/security), [Pairing](/ja-JP/channels/pairing)。

  </Accordion>

  <Accordion title="自分のテキストメッセージに自律性を持たせても安全ですか？">
    個人メッセージに対する完全な自律性は **推奨しません**。最も安全なパターンは次のとおりです。

    - DM は **pairing mode** または厳しい allowlist に保つ。
    - 代わりに送信させたいなら、**別の番号またはアカウント** を使う。
    - 下書きさせてから、**送信前に承認する**。

    試したい場合は、専用アカウントで行い、分離を保ってください。[Security](/ja-JP/gateway/security) を参照してください。

  </Accordion>

  <Accordion title="個人アシスタント用途なら安いモデルを使えますか？">
    はい。ただし、エージェントがチャット専用で、入力が信頼できる場合に限ります。小さいティアは
    指示の乗っ取りを受けやすいため、tool 対応エージェントや
    信頼できないコンテンツを読む場合には避けてください。どうしても小さいモデルを使うなら、
    tools を厳しく制限し、サンドボックス内で実行してください。[Security](/ja-JP/gateway/security) を参照してください。
  </Accordion>

  <Accordion title="Telegram で /start を実行したのに pairing code が届きません">
    pairing code は、未知の送信者がボットにメッセージを送り、
    `dmPolicy: "pairing"` が有効な場合に **のみ** 送られます。`/start` だけではコードは生成されません。

    保留中リクエストを確認してください:

    ```bash
    openclaw pairing list telegram
    ```

    すぐにアクセスしたい場合は、自分の sender id を allowlist に入れるか、そのアカウントの `dmPolicy: "open"`
    を設定してください。

  </Accordion>

  <Accordion title="WhatsApp: 連絡先に勝手にメッセージを送りますか？ pairing はどう動作しますか？">
    いいえ。WhatsApp DM のデフォルトポリシーは **pairing** です。未知の送信者には pairing code だけが送られ、そのメッセージは **処理されません**。OpenClaw は、受信したチャットか、自分が明示的にトリガーした送信にしか返信しません。

    pairing の承認方法:

    ```bash
    openclaw pairing approve whatsapp <code>
    ```

    保留中リクエストの一覧:

    ```bash
    openclaw pairing list whatsapp
    ```

    ウィザードの電話番号プロンプトは、自分自身の **allowlist/owner** を設定するために使われます。自動送信用ではありません。個人の WhatsApp 番号で動かす場合は、その番号を使い、`channels.whatsapp.selfChatMode` を有効にしてください。

  </Accordion>
</AccordionGroup>

## チャットコマンド、タスク中断、「止まらない」

<AccordionGroup>
  <Accordion title="内部システムメッセージがチャットに表示されないようにするにはどうすればよいですか？">
    内部メッセージや tool メッセージのほとんどは、そのセッションで **verbose**、**trace**、または **reasoning** が有効な場合にのみ表示されます。

    表示されているチャットで次を実行してください:

    ```
    /verbose off
    /trace off
    /reasoning off
    ```

    それでもうるさい場合は、Control UI のセッション設定を確認して verbose を
    **inherit** にしてください。また、設定で `verboseDefault` が
    `on` に設定された bot profile を使っていないことも確認してください。

    ドキュメント: [Thinking and verbose](/ja-JP/tools/thinking), [Security](/ja-JP/gateway/security#reasoning-verbose-output-in-groups).

  </Accordion>

  <Accordion title="実行中のタスクを停止/キャンセルするにはどうすればよいですか？">
    次のいずれかを **単独メッセージとして** 送信してください（スラッシュなし）。

    ```
    stop
    stop action
    stop current action
    stop run
    stop current run
    stop agent
    stop the agent
    stop openclaw
    openclaw stop
    stop don't do anything
    stop do not do anything
    stop doing anything
    please stop
    stop please
    abort
    esc
    wait
    exit
    interrupt
    ```

    これらは中断トリガーです（スラッシュコマンドではありません）。

    バックグラウンドプロセス（exec tool 由来）の場合、agent に次の実行を依頼できます。

    ```
    process action:kill sessionId:XXX
    ```

    スラッシュコマンド概要: [Slash commands](/ja-JP/tools/slash-commands) を参照してください。

    多くのコマンドは `/` で始まる **単独メッセージ** として送信する必要がありますが、一部のショートカット（`/status` など）は allowlist 済み送信者なら文中でも機能します。

  </Accordion>

  <Accordion title='Telegram から Discord にメッセージを送るにはどうすればよいですか？（「Cross-context messaging denied」）'>
    OpenClaw はデフォルトで **クロスプロバイダ** メッセージングをブロックします。tool 呼び出しが
    Telegram にバインドされている場合、明示的に許可しない限り Discord には送信されません。

    エージェントでクロスプロバイダメッセージングを有効にします。

    ```json5
    {
      tools: {
        message: {
          crossContext: {
            allowAcrossProviders: true,
            marker: { enabled: true, prefix: "[from {channel}] " },
          },
        },
      },
    }
    ```

    設定編集後に gateway を再起動してください。

  </Accordion>

  <Accordion title='ボットが連投メッセージを「無視」しているように感じるのはなぜですか？'>
    queue mode は、新しいメッセージが進行中の実行とどう相互作用するかを制御します。モード変更には `/queue` を使ってください。

    - `steer` - 新しいメッセージが現在のタスクを方向転換する
    - `followup` - メッセージを 1 つずつ順に実行する
    - `collect` - メッセージをまとめて 1 回だけ返信する（デフォルト）
    - `steer-backlog` - 今すぐ方向転換し、その後バックログを処理する
    - `interrupt` - 現在の実行を中断して新規開始する

    followup モードでは `debounce:2s cap:25 drop:summarize` のようなオプションも追加できます。

  </Accordion>
</AccordionGroup>

## その他

<AccordionGroup>
  <Accordion title='Anthropic の API key 使用時のデフォルトモデルは何ですか？'>
    OpenClaw では、資格情報とモデル選択は別です。`ANTHROPIC_API_KEY` を設定する（または auth profiles に Anthropic API key を保存する）と認証は有効になりますが、実際のデフォルトモデルは `agents.defaults.model.primary` に設定したものです（たとえば `anthropic/claude-sonnet-4-6` または `anthropic/claude-opus-4-6`）。`No credentials found for profile "anthropic:default"` と表示される場合、それは実行中のエージェントに対する想定 `auth-profiles.json` に Anthropic 資格情報を Gateway が見つけられなかったことを意味します。
  </Accordion>
</AccordionGroup>

---

まだ解決しませんか？ [Discord](https://discord.com/invite/clawd) で質問するか、[GitHub discussion](https://github.com/openclaw/openclaw/discussions) を開いてください。
