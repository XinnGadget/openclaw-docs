---
read_when:
    - よくあるセットアップ、インストール、オンボーディング、またはランタイムサポートの質問に回答するとき
    - ユーザーから報告された問題を、より深いデバッグの前にトリアージするとき
summary: OpenClaw のセットアップ、設定、使用方法に関するよくある質問
title: FAQ
x-i18n:
    generated_at: "2026-04-08T02:21:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: 001b4605966b45b08108606f76ae937ec348c2179b04cf6fb34fef94833705e6
    source_path: help/faq.md
    workflow: 15
---

# FAQ

実運用のセットアップ（ローカル開発、VPS、マルチエージェント、OAuth/API キー、モデルフェイルオーバー）向けの簡単な回答と、より詳しいトラブルシューティングです。ランタイム診断については [トラブルシューティング](/ja-JP/gateway/troubleshooting) を参照してください。完全な設定リファレンスについては [Configuration](/ja-JP/gateway/configuration) を参照してください。

## 何か壊れているときの最初の 60 秒

1. **クイックステータス（最初の確認）**

   ```bash
   openclaw status
   ```

   高速なローカル要約: OS と更新、Gateway / サービス到達性、エージェント / セッション、プロバイダー設定 + ランタイム問題（Gateway に到達できる場合）。

2. **共有しやすいレポート（安全に共有可能）**

   ```bash
   openclaw status --all
   ```

   ログ末尾付きの読み取り専用診断です（トークンは伏せ字になります）。

3. **デーモン + ポート状態**

   ```bash
   openclaw gateway status
   ```

   スーパーバイザー上のランタイムと RPC 到達性、プローブ対象 URL、およびサービスが使用した可能性が高い設定を表示します。

4. **詳細プローブ**

   ```bash
   openclaw status --deep
   ```

   ライブの Gateway ヘルスプローブを実行し、サポートされる場合はチャンネルプローブも含みます
   （到達可能な Gateway が必要です）。[Health](/ja-JP/gateway/health) を参照してください。

5. **最新ログを追跡**

   ```bash
   openclaw logs --follow
   ```

   RPC がダウンしている場合は、代わりに次を使います:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   ファイルログはサービスログとは別です。[Logging](/ja-JP/logging) と [トラブルシューティング](/ja-JP/gateway/troubleshooting) を参照してください。

6. **doctor を実行（修復）**

   ```bash
   openclaw doctor
   ```

   設定 / 状態を修復・移行し、ヘルスチェックを実行します。[Doctor](/ja-JP/gateway/doctor) を参照してください。

7. **Gateway スナップショット**

   ```bash
   openclaw health --json
   openclaw health --verbose   # shows the target URL + config path on errors
   ```

   実行中の Gateway に完全なスナップショットを問い合わせます（WS のみ）。[Health](/ja-JP/gateway/health) を参照してください。

## クイックスタートと初回セットアップ

<AccordionGroup>
  <Accordion title="行き詰まりました。最速で抜け出す方法は？">
    **自分のマシンを見られる** ローカル AI エージェントを使ってください。これは Discord で質問するよりはるかに効果的です。なぜなら、「行き詰まった」というケースの大半は、リモートの支援者が調査できない **ローカル設定や環境の問題** だからです。

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    これらのツールは、リポジトリを読み、コマンドを実行し、ログを確認し、マシンレベルの
    セットアップ（PATH、サービス、権限、認証ファイル）を修正するのに役立ちます。ハッカブルな（git）インストールを使って、
    **完全なソースチェックアウト** を渡してください:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    これにより、OpenClaw は **git チェックアウトから** インストールされるため、エージェントがコード + ドキュメントを読んで、
    実行中の正確なバージョンを推論できます。後から
    `--install-method git` なしでインストーラーを再実行すれば、いつでも stable に戻せます。

    ヒント: エージェントには修正を **計画して監督** させ（段階的に）、必要な
    コマンドだけを実行させてください。これにより変更が小さくなり、監査しやすくなります。

    実際のバグや修正を見つけた場合は、GitHub issue を作成するか PR を送ってください:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    次のコマンドから始めてください（助けを求めるときは出力を共有してください）:

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    それぞれの役割:

    - `openclaw status`: Gateway / エージェントの健全性 + 基本設定のクイックスナップショット。
    - `openclaw models status`: プロバイダー認証 + モデルの利用可否を確認。
    - `openclaw doctor`: よくある設定 / 状態の問題を検証して修復。

    その他の有用な CLI チェック: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`。

    クイックデバッグループ: [何か壊れているときの最初の 60 秒](#何か壊れているときの最初の-60-秒)。
    インストールドキュメント: [Install](/ja-JP/install), [Installer flags](/ja-JP/install/installer), [Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="Heartbeat がスキップされ続けます。スキップ理由は何を意味しますか？">
    よくある heartbeat スキップ理由:

    - `quiet-hours`: 設定された active-hours の時間帯外
    - `empty-heartbeat-file`: `HEARTBEAT.md` は存在するが、空白 / ヘッダーだけの足場しか含まない
    - `no-tasks-due`: `HEARTBEAT.md` のタスクモードが有効だが、どのタスク間隔もまだ到来していない
    - `alerts-disabled`: heartbeat の可視化がすべて無効（`showOk`, `showAlerts`, `useIndicator` がすべてオフ）

    タスクモードでは、期限タイムスタンプは実際の heartbeat 実行が
    完了した後にのみ進みます。スキップされた実行ではタスクは完了扱いになりません。

    ドキュメント: [Heartbeat](/ja-JP/gateway/heartbeat), [Automation & Tasks](/ja-JP/automation)。

  </Accordion>

  <Accordion title="OpenClaw をインストールしてセットアップする推奨方法は？">
    リポジトリでは、ソースから実行し、オンボーディングを使うことを推奨しています:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    ウィザードは UI アセットを自動的にビルドすることもできます。オンボーディング後は、通常 Gateway を **18789** 番ポートで実行します。

    ソースから（コントリビューター / 開発者向け）:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # auto-installs UI deps on first run
    openclaw onboard
    ```

    まだグローバルインストールがない場合は、`pnpm openclaw onboard` で実行してください。

  </Accordion>

  <Accordion title="オンボーディング後にダッシュボードを開くにはどうすればよいですか？">
    ウィザードはオンボーディング直後に、クリーンな（トークンなしの）ダッシュボード URL をブラウザで開き、概要にもリンクを表示します。そのタブは開いたままにしてください。起動しなかった場合は、同じマシン上で表示された URL をコピーして貼り付けてください。
  </Accordion>

  <Accordion title="localhost とリモートでダッシュボードを認証するにはどうすればよいですか？">
    **localhost（同じマシン）:**

    - `http://127.0.0.1:18789/` を開きます。
    - 共有シークレット認証を求められた場合は、設定済みのトークンまたはパスワードを Control UI 設定に貼り付けます。
    - トークンの取得元: `gateway.auth.token`（または `OPENCLAW_GATEWAY_TOKEN`）。
    - パスワードの取得元: `gateway.auth.password`（または `OPENCLAW_GATEWAY_PASSWORD`）。
    - まだ共有シークレットが設定されていない場合は、`openclaw doctor --generate-gateway-token` でトークンを生成します。

    **localhost ではない場合:**

    - **Tailscale Serve**（推奨）: bind は loopback のままにし、`openclaw gateway --tailscale serve` を実行して、`https://<magicdns>/` を開きます。`gateway.auth.allowTailscale` が `true` の場合、ID ヘッダーが Control UI / WebSocket 認証を満たします（共有シークレットの貼り付け不要、信頼された gateway host を前提）。HTTP API では、明示的に private-ingress の `none` または trusted-proxy HTTP auth を使わない限り、依然として共有シークレット認証が必要です。
      同じクライアントから同時に行われた不正な Serve 認証試行は、失敗認証リミッターが記録する前に直列化されるため、2 回目の不正再試行ではすでに `retry later` が表示されることがあります。
    - **Tailnet bind**: `openclaw gateway --bind tailnet --token "<token>"` を実行し（またはパスワード認証を設定し）、`http://<tailscale-ip>:18789/` を開いてから、対応する共有シークレットをダッシュボード設定に貼り付けます。
    - **ID 認識リバースプロキシ**: Gateway を非 loopback の trusted proxy の背後に置き、`gateway.auth.mode: "trusted-proxy"` を設定してから、その proxy URL を開きます。
    - **SSH トンネル**: `ssh -N -L 18789:127.0.0.1:18789 user@host` の後で `http://127.0.0.1:18789/` を開きます。トンネル越しでも共有シークレット認証は適用されるため、求められたら設定済みのトークンまたはパスワードを貼り付けてください。

    bind モードと認証の詳細については [Dashboard](/web/dashboard) と [Web surfaces](/web) を参照してください。

  </Accordion>

  <Accordion title="チャット承認に exec approval の設定が 2 つあるのはなぜですか？">
    これは異なる層を制御しています:

    - `approvals.exec`: 承認プロンプトをチャット宛先へ転送する
    - `channels.<channel>.execApprovals`: そのチャンネルを exec approvals 用のネイティブ承認クライアントとして動作させる

    ホストの exec ポリシーは依然として実際の承認ゲートです。チャット設定は、承認
    プロンプトがどこに表示され、ユーザーがどう応答できるかだけを制御します。

    多くのセットアップでは、**両方** は不要です:

    - そのチャットがすでにコマンドと返信をサポートしているなら、同一チャットの `/approve` は共有パスを通じて機能します。
    - サポートされているネイティブチャンネルが approver を安全に推定できる場合、OpenClaw は `channels.<channel>.execApprovals.enabled` が未設定または `"auto"` のとき、自動で DM 優先のネイティブ承認を有効にします。
    - ネイティブの承認カード / ボタンが利用可能な場合、そのネイティブ UI が主要経路になります。エージェントは、ツール結果がチャット承認を利用できない、または手動承認しか方法がないと示した場合にのみ、手動 `/approve` コマンドを含めるべきです。
    - `approvals.exec` は、プロンプトを他のチャットや明示的な ops room にも転送する必要がある場合にのみ使用してください。
    - `channels.<channel>.execApprovals.target: "channel"` または `"both"` は、承認プロンプトを元の room / topic に明示的に投稿したい場合にのみ使用してください。
    - プラグイン承認はさらに別です。デフォルトでは同一チャット `/approve` を使用し、オプションの `approvals.plugin` 転送を行い、一部のネイティブチャンネルのみがその上に plugin-approval-native 処理を保持します。

    要するに、転送はルーティングのため、ネイティブクライアント設定はより豊かなチャンネル固有 UX のためです。
    [Exec Approvals](/ja-JP/tools/exec-approvals) を参照してください。

  </Accordion>

  <Accordion title="必要なランタイムは何ですか？">
    Node **>= 22** が必要です。`pnpm` を推奨します。Gateway には Bun は **推奨されません**。
  </Accordion>

  <Accordion title="Raspberry Pi で動きますか？">
    はい。Gateway は軽量です。ドキュメントでは、個人利用なら **512MB-1GB RAM**、**1 コア**、約 **500MB** の
    ディスクで十分とされており、**Raspberry Pi 4 で動作可能** と記載されています。

    余裕（ログ、メディア、他のサービス）が欲しい場合は **2GB を推奨** しますが、
    これは必須の最小値ではありません。

    ヒント: 小型の Pi / VPS で Gateway をホストし、ローカル画面 / カメラ / Canvas や
    コマンド実行のために、ノート PC / スマートフォン上の **nodes** をペアリングできます。[Nodes](/ja-JP/nodes) を参照してください。

  </Accordion>

  <Accordion title="Raspberry Pi へのインストールのコツはありますか？">
    短く言うと、動きますが、粗さはあります。

    - **64-bit** OS を使い、Node は 22 以上を維持してください。
    - ログ確認や高速更新のため、**ハッカブルな（git）インストール** を推奨します。
    - チャンネル / Skills なしで始めて、1 つずつ追加してください。
    - 変なバイナリ問題に当たった場合、通常は **ARM 互換性** の問題です。

    ドキュメント: [Linux](/ja-JP/platforms/linux), [Install](/ja-JP/install)。

  </Accordion>

  <Accordion title="wake up my friend で止まる / オンボーディングが進みません。どうすればいいですか？">
    その画面は、Gateway に到達できて認証されていることに依存します。TUI も
    初回 hatch 時に自動で 「Wake up, my friend!」 を送信します。その行が表示されているのに **返信がなく**
    トークンも 0 のままなら、エージェントは実行されていません。

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

    3. まだ止まる場合は、次を実行します:

    ```bash
    openclaw doctor
    ```

    Gateway がリモートの場合は、トンネル / Tailscale 接続が有効で、UI が
    正しい Gateway を向いていることを確認してください。[Remote access](/ja-JP/gateway/remote) を参照してください。

  </Accordion>

  <Accordion title="セットアップを新しいマシン（Mac mini）へ、オンボーディングをやり直さずに移行できますか？">
    はい。**state ディレクトリ** と **workspace** をコピーしてから、Doctor を 1 回実行してください。これにより
    **両方** の場所をコピーする限り、ボットを「まったく同じ状態」（メモリ、セッション履歴、認証、チャンネル
    状態）で維持できます:

    1. 新しいマシンに OpenClaw をインストールします。
    2. 古いマシンから `$OPENCLAW_STATE_DIR`（デフォルト: `~/.openclaw`）をコピーします。
    3. workspace（デフォルト: `~/.openclaw/workspace`）をコピーします。
    4. `openclaw doctor` を実行し、Gateway サービスを再起動します。

    これにより設定、認証プロファイル、WhatsApp 資格情報、セッション、メモリが保持されます。
    remote mode の場合は、セッションストアと workspace を所有しているのは gateway host であることを忘れないでください。

    **重要:** workspace を GitHub に commit / push するだけでは、
    バックアップされるのは **メモリ + ブートストラップファイル** であり、**セッション履歴や認証** ではありません。それらは
    `~/.openclaw/` 配下にあります（例: `~/.openclaw/agents/<agentId>/sessions/`）。

    関連: [Migrating](/ja-JP/install/migrating), [ディスク上の保存場所](#ディスク上の保存場所),
    [Agent workspace](/ja-JP/concepts/agent-workspace), [Doctor](/ja-JP/gateway/doctor),
    [Remote mode](/ja-JP/gateway/remote)。

  </Accordion>

  <Accordion title="最新バージョンの新機能はどこで見られますか？">
    GitHub changelog を確認してください:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    最新の項目は先頭にあります。先頭セクションが **Unreleased** の場合、
    次の日付付きセクションが最新のリリース版です。項目は **Highlights**、**Changes**、**Fixes** ごとに
    グループ化されています（必要に応じて docs / その他のセクションもあります）。

  </Accordion>

  <Accordion title="docs.openclaw.ai にアクセスできません（SSL エラー）">
    一部の Comcast/Xfinity 回線では、Xfinity
    Advanced Security によって `docs.openclaw.ai` が誤ってブロックされます。
    それを無効にするか、`docs.openclaw.ai` を許可リストに追加してから再試行してください。
    解除にご協力いただける場合は、こちらから報告してください: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status)。

    それでもサイトに到達できない場合、ドキュメントは GitHub にミラーされています:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="stable と beta の違い">
    **Stable** と **beta** は別々のコードラインではなく、**npm dist-tag** です:

    - `latest` = stable
    - `beta` = テスト用の早期ビルド

    通常、stable リリースはまず **beta** に入り、その後明示的な
    promotion ステップで同じバージョンが `latest` に移されます。メンテナーは必要に応じて
    直接 `latest` に publish することもできます。そのため、beta と stable は
    promotion 後に **同じバージョン** を指すことがあります。

    変更内容の確認:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    インストール用ワンライナーと beta と dev の違いについては、下のアコーディオンを参照してください。

  </Accordion>

  <Accordion title="beta 版をインストールするには？ また beta と dev の違いは何ですか？">
    **Beta** は npm dist-tag の `beta` です（promotion 後は `latest` と一致する場合があります）。
    **Dev** は `main` の移動する先端（git）で、publish される場合は npm dist-tag の `dev` を使います。

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

  <Accordion title="最新のものを試すにはどうすればよいですか？">
    方法は 2 つあります:

    1. **Dev channel（git checkout）:**

    ```bash
    openclaw update --channel dev
    ```

    これにより `main` ブランチに切り替わり、ソースから更新されます。

    2. **ハッカブルインストール（インストーラーサイトから）:**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    これにより編集可能なローカルリポジトリが得られ、その後は git で更新できます。

    手動でクリーンな clone をしたい場合は、次を使ってください:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    ドキュメント: [Update](/cli/update), [Development channels](/ja-JP/install/development-channels),
    [Install](/ja-JP/install)。

  </Accordion>

  <Accordion title="インストールとオンボーディングには通常どれくらい時間がかかりますか？">
    目安:

    - **インストール:** 2-5 分
    - **オンボーディング:** 設定するチャンネル / モデル数に応じて 5-15 分

    止まる場合は、[Installer stuck](#クイックスタートと初回セットアップ)
    と [行き詰まりました](#クイックスタートと初回セットアップ) の高速デバッグループを使ってください。

  </Accordion>

  <Accordion title="インストーラーで止まりました。もっと詳細なフィードバックを得るには？">
    **verbose 出力** 付きでインストーラーを再実行してください:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    verbose 付き beta インストール:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    ハッカブルな（git）インストールの場合:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Windows（PowerShell）の同等手順:

    ```powershell
    # install.ps1 has no dedicated -Verbose flag yet.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    その他のオプション: [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="Windows インストールで git not found または openclaw not recognized と表示されます">
    Windows でよくある問題は 2 つあります:

    **1) npm error spawn git / git not found**

    - **Git for Windows** をインストールし、`git` が PATH 上にあることを確認してください。
    - PowerShell を閉じて開き直し、インストーラーを再実行してください。

    **2) インストール後に openclaw is not recognized と表示される**

    - npm のグローバル bin フォルダーが PATH にありません。
    - パスを確認します:

      ```powershell
      npm config get prefix
      ```

    - そのディレクトリをユーザー PATH に追加してください（Windows では `\bin` サフィックスは不要です。ほとんどのシステムでは `%AppData%\npm` です）。
    - PATH 更新後、PowerShell を閉じて開き直してください。

    最もスムーズな Windows セットアップにしたい場合は、ネイティブ Windows ではなく **WSL2** を使ってください。
    ドキュメント: [Windows](/ja-JP/platforms/windows)。

  </Accordion>

  <Accordion title="Windows の exec 出力で中国語が文字化けします。どうすればよいですか？">
    これは通常、ネイティブ Windows シェルのコンソールコードページ不一致です。

    症状:

    - `system.run` / `exec` 出力で中国語が文字化けする
    - 同じコマンドが別のターミナルプロファイルでは正しく見える

    PowerShell でのクイック回避策:

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

    最新の OpenClaw でも再現する場合は、こちらで追跡 / 報告してください:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="ドキュメントに答えがありませんでした。より良い回答を得るにはどうすればよいですか？">
    **ハッカブルな（git）インストール** を使って、ソースとドキュメントをローカルに完全に持ち、その
    フォルダー内から自分のボット（または Claude / Codex）に尋ねてください。そうすればリポジトリを読んで正確に答えられます。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    詳細: [Install](/ja-JP/install) と [Installer flags](/ja-JP/install/installer)。

  </Accordion>

  <Accordion title="Linux に OpenClaw をインストールするにはどうすればよいですか？">
    短い答え: Linux ガイドに従ってから、オンボーディングを実行してください。

    - Linux のクイックパス + サービスインストール: [Linux](/ja-JP/platforms/linux)。
    - 完全な手順: [はじめに](/ja-JP/start/getting-started)。
    - インストーラー + 更新: [Install & updates](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="VPS に OpenClaw をインストールするにはどうすればよいですか？">
    どの Linux VPS でも動作します。サーバーにインストールし、その後 SSH / Tailscale で Gateway にアクセスしてください。

    ガイド: [exe.dev](/ja-JP/install/exe-dev), [Hetzner](/ja-JP/install/hetzner), [Fly.io](/ja-JP/install/fly)。
    リモートアクセス: [Gateway remote](/ja-JP/gateway/remote)。

  </Accordion>

  <Accordion title="クラウド / VPS のインストールガイドはどこにありますか？">
    一般的なプロバイダーをまとめた **hosting hub** があります。1 つ選んでガイドに従ってください:

    - [VPS hosting](/ja-JP/vps)（すべてのプロバイダーを 1 か所に集約）
    - [Fly.io](/ja-JP/install/fly)
    - [Hetzner](/ja-JP/install/hetzner)
    - [exe.dev](/ja-JP/install/exe-dev)

    クラウドでの動作: **Gateway はサーバー上で動作し**、あなたは
    ノート PC / スマートフォンから Control UI（または Tailscale / SSH）でアクセスします。state + workspace は
    サーバー上にあるため、ホストを信頼できる唯一の情報源として扱い、バックアップしてください。

    そのクラウド Gateway に **nodes**（Mac / iOS / Android / headless）をペアリングして、
    ローカルの screen / camera / canvas にアクセスしたり、Gateway をクラウドに置いたまま
    ノート PC 上でコマンドを実行したりできます。

    ハブ: [Platforms](/ja-JP/platforms)。リモートアクセス: [Gateway remote](/ja-JP/gateway/remote)。
    Nodes: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="OpenClaw に自分自身を更新させることはできますか？">
    短い答え: **可能ですが、推奨はしません**。更新フローでは
    Gateway が再起動することがあり（アクティブセッションが切れます）、クリーンな git checkout が必要になったり、
    確認を求められたりする場合があります。より安全なのは、オペレーターとしてシェルから更新を実行することです。

    CLI を使用:

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

    ドキュメント: [Update](/cli/update), [Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="オンボーディングは実際に何をしますか？">
    `openclaw onboard` は推奨セットアップ経路です。**local mode** では次を案内します:

    - **モデル / 認証セットアップ**（provider OAuth、API キー、Anthropic setup-token、LM Studio などのローカルモデルオプション）
    - **Workspace** の場所 + bootstrap ファイル
    - **Gateway 設定**（bind / port / auth / tailscale）
    - **Channels**（WhatsApp、Telegram、Discord、Mattermost、Signal、iMessage、および QQ Bot のようなバンドル済みチャンネルプラグイン）
    - **Daemon インストール**（macOS の LaunchAgent、Linux / WSL2 の systemd user unit）
    - **ヘルスチェック** と **Skills** の選択

    また、設定されたモデルが不明または認証不足の場合は警告します。

  </Accordion>

  <Accordion title="これを動かすのに Claude や OpenAI のサブスクリプションは必要ですか？">
    いいえ。OpenClaw は **API キー**（Anthropic / OpenAI / その他）でも、
    **ローカル専用モデル** でも動作するため、データを自分のデバイス上に残せます。サブスクリプション（Claude
    Pro / Max または OpenAI Codex）は、それらのプロバイダーを認証するための任意の方法です。

    OpenClaw における Anthropic では、実用上の区分は次のとおりです:

    - **Anthropic API key**: 通常の Anthropic API 課金
    - **Claude CLI / Claude subscription auth in OpenClaw**: Anthropic スタッフから
      この利用は再び許可されていると伝えられており、Anthropic が新しい
      ポリシーを公開しない限り、OpenClaw はこの統合における `claude -p`
      利用を認可済みとして扱っています

    長時間稼働する gateway host では、Anthropic API キーの方が依然として
    より予測しやすいセットアップです。OpenAI Codex OAuth は、OpenClaw のような外部
    ツールに対して明示的にサポートされています。

    OpenClaw は、他のホスト型サブスクリプション系オプションもサポートしています。たとえば
    **Qwen Cloud Coding Plan**、**MiniMax Coding Plan**、および
    **Z.AI / GLM Coding Plan** です。

    ドキュメント: [Anthropic](/ja-JP/providers/anthropic), [OpenAI](/ja-JP/providers/openai),
    [Qwen Cloud](/ja-JP/providers/qwen),
    [MiniMax](/ja-JP/providers/minimax), [GLM Models](/ja-JP/providers/glm),
    [Local models](/ja-JP/gateway/local-models), [Models](/ja-JP/concepts/models)。

  </Accordion>

  <Accordion title="API キーなしで Claude Max サブスクリプションを使えますか？">
    はい。

    Anthropic スタッフから、OpenClaw 形式の Claude CLI 利用は再び許可されていると伝えられているため、
    Anthropic が新しいポリシーを公開しない限り、OpenClaw は Claude subscription auth と `claude -p` の利用を
    この統合に対して認可済みとして扱います。より予測しやすいサーバー側セットアップが必要な場合は、
    代わりに Anthropic API キーを使用してください。

  </Accordion>

  <Accordion title="Claude subscription auth（Claude Pro または Max）をサポートしていますか？">
    はい。

    Anthropic スタッフからこの利用は再び許可されていると伝えられているため、OpenClaw は
    Anthropic が新しいポリシーを公開しない限り、
    Claude CLI の再利用と `claude -p` の利用をこの統合に対して認可済みとして扱います。

    Anthropic setup-token は引き続きサポートされる OpenClaw のトークン経路として利用可能ですが、OpenClaw は現在、利用可能な場合は Claude CLI の再利用と `claude -p` を優先します。
    本番環境または複数ユーザーのワークロードでは、Anthropic API キー認証が依然として
    より安全で予測しやすい選択です。OpenClaw の他のサブスクリプション系ホスト型
    オプションについては、[OpenAI](/ja-JP/providers/openai), [Qwen / Model
    Cloud](/ja-JP/providers/qwen), [MiniMax](/ja-JP/providers/minimax), および [GLM
    Models](/ja-JP/providers/glm) を参照してください。

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Anthropic から HTTP 429 rate_limit_error が出るのはなぜですか？">
これは、現在の時間枠における **Anthropic のクォータ / レート制限** を使い切ったことを意味します。
**Claude CLI** を使っている場合は、時間枠がリセットされるのを待つか、プランを
アップグレードしてください。**Anthropic API key** を使っている場合は、Anthropic Console で
使用量 / 請求を確認し、必要に応じて制限を引き上げてください。

    メッセージが具体的に次の場合:
    `Extra usage is required for long context requests`
    リクエストは Anthropic の 1M context beta（`context1m: true`）を使おうとしています。これは
    資格情報が long-context 課金の対象である場合にのみ動作します（API key 課金、または Extra Usage が有効な
    OpenClaw Claude-login 経路）。

    ヒント: プロバイダーが rate limit 中でも OpenClaw が応答を続けられるように、
    **fallback model** を設定してください。
    [Models](/cli/models), [OAuth](/ja-JP/concepts/oauth), および
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/ja-JP/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context) を参照してください。

  </Accordion>

  <Accordion title="AWS Bedrock はサポートされていますか？">
    はい。OpenClaw にはバンドル済みの **Amazon Bedrock (Converse)** プロバイダーがあります。AWS の env マーカーが存在する場合、OpenClaw は streaming / text Bedrock カタログを自動検出し、暗黙の `amazon-bedrock` プロバイダーとしてマージできます。それ以外の場合は、`plugins.entries.amazon-bedrock.config.discovery.enabled` を明示的に有効にするか、手動の provider エントリーを追加できます。[Amazon Bedrock](/ja-JP/providers/bedrock) と [Model providers](/ja-JP/providers/models) を参照してください。マネージドな key フローを好む場合は、Bedrock の前に OpenAI 互換プロキシを置くのも有効な選択肢です。
  </Accordion>

  <Accordion title="Codex の認証はどのように機能しますか？">
    OpenClaw は OAuth（ChatGPT サインイン）経由の **OpenAI Code (Codex)** をサポートしています。オンボーディングは OAuth フローを実行でき、適切な場合はデフォルトモデルを `openai-codex/gpt-5.4` に設定します。[Model providers](/ja-JP/concepts/model-providers) と [Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。
  </Accordion>

  <Accordion title="なぜ ChatGPT GPT-5.4 で openai/gpt-5.4 が OpenClaw で使えるようにならないのですか？">
    OpenClaw では、この 2 つの経路を別々に扱います:

    - `openai-codex/gpt-5.4` = ChatGPT / Codex OAuth
    - `openai/gpt-5.4` = 直接の OpenAI Platform API

    OpenClaw では、ChatGPT / Codex サインインは
    直接の `openai/*` 経路ではなく、`openai-codex/*` 経路に接続されています。OpenClaw で
    直接 API 経路を使いたい場合は、
    `OPENAI_API_KEY`（または同等の OpenAI provider config）を設定してください。
    OpenClaw で ChatGPT / Codex サインインを使いたい場合は、`openai-codex/*` を使用してください。

  </Accordion>

  <Accordion title="Codex OAuth の制限が ChatGPT web と異なることがあるのはなぜですか？">
    `openai-codex/*` は Codex OAuth 経路を使用しており、その利用可能なクォータ時間枠は
    OpenAI によって管理され、プラン依存です。実際には、それらの制限は
    同じアカウントに紐付いていても、ChatGPT Web / アプリの体験と異なることがあります。

    OpenClaw は現在見えている provider の使用量 / クォータ時間枠を
    `openclaw models status` に表示できますが、ChatGPT web の
    エンタイトルメントを直接 API アクセスへ作り変えたり正規化したりはしません。直接の OpenAI Platform
    課金 / 制限経路が必要なら、API キー付きの `openai/*` を使ってください。

  </Accordion>

  <Accordion title="OpenAI subscription auth（Codex OAuth）をサポートしていますか？">
    はい。OpenClaw は **OpenAI Code (Codex) subscription OAuth** を完全にサポートしています。
    OpenAI は、OpenClaw のような外部ツール / ワークフローでの
    subscription OAuth 利用を明示的に許可しています。オンボーディングで OAuth フローを実行できます。

    [OAuth](/ja-JP/concepts/oauth), [Model providers](/ja-JP/concepts/model-providers), および [Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。

  </Accordion>

  <Accordion title="Gemini CLI OAuth をセットアップするにはどうすればよいですか？">
    Gemini CLI は、`openclaw.json` 内の client id や secret ではなく、**plugin auth flow** を使用します。

    手順:

    1. `gemini` が `PATH` に入るように、Gemini CLI をローカルにインストールします
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. プラグインを有効化します: `openclaw plugins enable google`
    3. ログインします: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. ログイン後のデフォルトモデル: `google-gemini-cli/gemini-3-flash-preview`
    5. リクエストが失敗する場合は、gateway host に `GOOGLE_CLOUD_PROJECT` または `GOOGLE_CLOUD_PROJECT_ID` を設定してください

    これにより OAuth トークンは gateway host 上の auth profiles に保存されます。詳細: [Model providers](/ja-JP/concepts/model-providers)。

  </Accordion>

  <Accordion title="雑談用途ならローカルモデルでも大丈夫ですか？">
    通常はいいえ。OpenClaw には大きなコンテキストと強い安全性が必要であり、小さなカードでは切り詰めや情報漏れが起こります。どうしても使うなら、ローカルで実行可能な **最大** のモデルビルド（LM Studio）を使い、[/gateway/local-models](/ja-JP/gateway/local-models) を参照してください。小型 / 量子化モデルはプロンプトインジェクションのリスクを高めます。[Security](/ja-JP/gateway/security) を参照してください。
  </Accordion>

  <Accordion title="ホスト型モデルのトラフィックを特定のリージョンに留めるにはどうすればよいですか？">
    リージョン固定のエンドポイントを選択してください。OpenRouter は MiniMax、Kimi、GLM の US ホスト版オプションを提供しています。US ホスト版を選べば、データをそのリージョン内に留められます。`models.mode: "merge"` を使えば、選択したリージョン固定プロバイダーを尊重しつつ、Anthropic / OpenAI もフォールバックとして併記できます。
  </Accordion>

  <Accordion title="これをインストールするのに Mac Mini を買う必要がありますか？">
    いいえ。OpenClaw は macOS または Linux（Windows は WSL2 経由）で動作します。Mac mini は任意です。
    常時稼働ホストとして購入する人もいますが、小型の VPS、ホームサーバー、または Raspberry Pi クラスのマシンでも動作します。

    Mac が必要なのは **macOS 専用ツール** の場合だけです。iMessage には
    [BlueBubbles](/ja-JP/channels/bluebubbles)（推奨）を使ってください。BlueBubbles サーバーは任意の Mac 上で動作し、
    Gateway は Linux その他で動かせます。他の macOS 専用ツールが必要なら、
    Gateway を Mac 上で動かすか、macOS node をペアリングしてください。

    ドキュメント: [BlueBubbles](/ja-JP/channels/bluebubbles), [Nodes](/ja-JP/nodes), [Mac remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="iMessage サポートには Mac mini が必要ですか？">
    Messages にサインインした **何らかの macOS デバイス** が必要です。**Mac mini である必要はありません**。
    iMessage には **[BlueBubbles](/ja-JP/channels/bluebubbles)**（推奨）を使ってください。BlueBubbles サーバーは macOS 上で動作し、Gateway は Linux その他で動かせます。

    よくあるセットアップ:

    - Linux / VPS で Gateway を動かし、Messages にサインインした任意の Mac 上で BlueBubbles サーバーを動かす。
    - 最も簡単な単一マシン構成がよければ、すべてをその Mac 上で動かす。

    ドキュメント: [BlueBubbles](/ja-JP/channels/bluebubbles), [Nodes](/ja-JP/nodes),
    [Mac remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="OpenClaw を動かすために Mac mini を買った場合、それを MacBook Pro から接続できますか？">
    はい。**Mac mini は Gateway を動かせ**、MacBook Pro は
    **node**（コンパニオンデバイス）として接続できます。Nodes は Gateway を実行しません。
    そのデバイス上で screen / camera / canvas や `system.run` のような追加機能を提供します。

    よくある構成:

    - 常時稼働の Gateway を Mac mini 上で実行。
    - MacBook Pro で macOS アプリまたは node host を実行し、Gateway にペアリング。
    - `openclaw nodes status` / `openclaw nodes list` で確認。

    ドキュメント: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="Bun は使えますか？">
    Bun は **推奨されません**。特に WhatsApp と Telegram でランタイムバグが見られます。
    安定した Gateway には **Node** を使ってください。

    それでも Bun を試したい場合は、WhatsApp / Telegram なしの
    非本番 Gateway で行ってください。

  </Accordion>

  <Accordion title="Telegram: allowFrom には何を入れますか？">
    `channels.telegram.allowFrom` は **人間の送信者の Telegram user ID**（数値）です。ボットの username ではありません。

    オンボーディングでは `@username` 入力を受け付けて数値 ID に解決しますが、OpenClaw の認可は数値 ID のみを使います。

    より安全な方法（サードパーティボット不要）:

    - ボットに DM し、`openclaw logs --follow` を実行して `from.id` を読み取ります。

    公式 Bot API:

    - ボットに DM し、`https://api.telegram.org/bot<bot_token>/getUpdates` を呼び出して `message.from.id` を読み取ります。

    サードパーティ（プライバシー性は低い）:

    - `@userinfobot` または `@getidsbot` に DM します。

    [/channels/telegram](/ja-JP/channels/telegram#access-control-and-activation) を参照してください。

  </Accordion>

  <Accordion title="複数の人が 1 つの WhatsApp 番号を使って、別々の OpenClaw インスタンスを使えますか？">
    はい。**マルチエージェントルーティング** を通じて可能です。各送信者の WhatsApp **DM**（peer `kind: "direct"`、送信者 E.164 形式 `+15551234567` など）を異なる `agentId` にバインドすれば、各人が自分専用の workspace と session store を持てます。返信は引き続き **同じ WhatsApp アカウント** から送られ、DM アクセス制御（`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`）は WhatsApp アカウントごとにグローバルです。[Multi-Agent Routing](/ja-JP/concepts/multi-agent) と [WhatsApp](/ja-JP/channels/whatsapp) を参照してください。
  </Accordion>

  <Accordion title='「高速チャット」用のエージェントと「コーディングは Opus」用のエージェントを分けられますか？'>
    はい。マルチエージェントルーティングを使ってください。各エージェントに独自のデフォルトモデルを与え、その後、受信ルート（provider account または特定の peer）を各エージェントにバインドします。設定例は [Multi-Agent Routing](/ja-JP/concepts/multi-agent) にあります。[Models](/ja-JP/concepts/models) と [Configuration](/ja-JP/gateway/configuration) も参照してください。
  </Accordion>

  <Accordion title="Homebrew は Linux で動きますか？">
    はい。Homebrew は Linux（Linuxbrew）をサポートしています。クイックセットアップ:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    OpenClaw を systemd 経由で実行する場合は、サービスの PATH に `/home/linuxbrew/.linuxbrew/bin`（または自分の brew prefix）が含まれていることを確認し、非ログインシェルでも `brew` でインストールしたツールが解決されるようにしてください。
    最近のビルドでは、Linux の systemd サービスで一般的なユーザー bin ディレクトリ（例: `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`）も先頭に追加し、`PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR`, `FNM_DIR` が設定されている場合はそれらも尊重します。

  </Accordion>

  <Accordion title="ハッカブルな git install と npm install の違いは何ですか？">
    - **ハッカブルな（git）インストール:** 完全なソースチェックアウトで、編集可能、コントリビューターに最適です。
      ビルドはローカルで実行し、コード / ドキュメントにパッチを当てられます。
    - **npm install:** グローバル CLI インストールで、リポジトリはなし、「とにかく動かしたい」用途に最適です。
      更新は npm dist-tag から取得されます。

    ドキュメント: [はじめに](/ja-JP/start/getting-started), [Updating](/ja-JP/install/updating)。

  </Accordion>

  <Accordion title="後から npm インストールと git インストールを切り替えられますか？">
    はい。別の方式をインストールしてから、Doctor を実行して gateway service が新しい entrypoint を指すようにしてください。
    これで **データが削除されることはありません**。変更されるのは OpenClaw のコードインストールだけです。state
    （`~/.openclaw`）と workspace（`~/.openclaw/workspace`）はそのまま維持されます。

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

    Doctor は gateway service の entrypoint 不一致を検出し、現在のインストールに合わせて service config を書き換える提案をします（自動化では `--repair` を使用）。

    バックアップのヒント: [バックアップ戦略](#ディスク上の保存場所) を参照してください。

  </Accordion>

  <Accordion title="Gateway はノート PC 上で動かすべきですか、それとも VPS 上ですか？">
    短い答え: **24/7 の信頼性が欲しいなら VPS を使ってください**。最も手軽さを優先し、
    スリープ / 再起動を許容できるならローカルで動かしてください。

    **ノート PC（ローカル Gateway）**

    - **長所:** サーバー費用不要、ローカルファイルへ直接アクセス、ライブのブラウザウィンドウ。
    - **短所:** スリープ / ネットワーク切断 = 切断、OS 更新 / 再起動で中断、起動状態を維持する必要あり。

    **VPS / クラウド**

    - **長所:** 常時稼働、安定したネットワーク、ノート PC のスリープ問題なし、稼働維持が容易。
    - **短所:** headless で動かすことが多い（スクリーンショットを使用）、ファイルアクセスはリモートのみ、更新には SSH が必要。

    **OpenClaw 固有の注意:** WhatsApp / Telegram / Slack / Mattermost / Discord はどれも VPS で問題なく動作します。本当のトレードオフは **headless browser** と可視ウィンドウの違いだけです。[Browser](/ja-JP/tools/browser) を参照してください。

    **推奨デフォルト:** 以前に gateway の切断があったなら VPS。ローカルは、Mac をアクティブに使っていて、ローカルファイルアクセスや
    可視ブラウザ付きの UI 自動化が欲しい場合に最適です。

  </Accordion>

  <Accordion title="OpenClaw を専用マシンで動かすことはどれくらい重要ですか？">
    必須ではありませんが、**信頼性と分離のために推奨** します。

    - **専用ホスト（VPS / Mac mini / Pi）:** 常時稼働、スリープ / 再起動の中断が少ない、権限がクリーン、運用維持が容易。
    - **共有ノート PC / デスクトップ:** テストや能動的な利用にはまったく問題ありませんが、スリープや更新時の停止は発生します。

    両方の利点が欲しいなら、Gateway は専用ホストに置き、ノート PC はローカル screen / camera / exec ツール用の **node** としてペアリングしてください。[Nodes](/ja-JP/nodes) を参照してください。
    セキュリティガイダンスは [Security](/ja-JP/gateway/security) を参照してください。

  </Accordion>

  <Accordion title="最小 VPS 要件と推奨 OS は何ですか？">
    OpenClaw は軽量です。基本的な Gateway + 1 つのチャットチャンネルなら:

    - **絶対最小:** 1 vCPU、1GB RAM、約 500MB ディスク。
    - **推奨:** 1-2 vCPU、2GB RAM 以上で余裕を確保（ログ、メディア、複数チャンネル）。Node tools や browser automation はリソースを多く使うことがあります。

    OS: **Ubuntu LTS**（または現代的な Debian / Ubuntu）を使ってください。Linux インストール経路はそこで最もよくテストされています。

    ドキュメント: [Linux](/ja-JP/platforms/linux), [VPS hosting](/ja-JP/vps)。

  </Accordion>

  <Accordion title="VM で OpenClaw を動かせますか？ 必要要件は何ですか？">
    はい。VM は VPS と同じように扱ってください。常時稼働で、到達可能であり、
    Gateway と有効化したチャンネルに十分な RAM が必要です。

    基本ガイダンス:

    - **絶対最小:** 1 vCPU、1GB RAM。
    - **推奨:** 複数チャンネル、browser automation、media tools を動かすなら 2GB RAM 以上。
    - **OS:** Ubuntu LTS または他の現代的な Debian / Ubuntu。

    Windows を使っている場合、**WSL2 が最も簡単な VM 風セットアップ** で、ツール互換性も最良です。
    [Windows](/ja-JP/platforms/windows), [VPS hosting](/ja-JP/vps) を参照してください。
    macOS を VM で動かしている場合は、[macOS VM](/ja-JP/install/macos-vm) を参照してください。

  </Accordion>
</AccordionGroup>

## OpenClaw とは何ですか？

<AccordionGroup>
  <Accordion title="OpenClaw を 1 段落で言うと？">
    OpenClaw は、自分のデバイス上で動かす個人用 AI アシスタントです。すでに使っているメッセージング面（WhatsApp、Telegram、Slack、Mattermost、Discord、Google Chat、Signal、iMessage、WebChat、および QQ Bot のようなバンドル済みチャンネルプラグイン）で返信でき、対応プラットフォームでは音声 + ライブ Canvas も利用できます。**Gateway** は常時稼働のコントロールプレーンであり、アシスタントそのものが製品です。
  </Accordion>

  <Accordion title="価値提案">
    OpenClaw は「単なる Claude ラッパー」ではありません。これは **ローカルファーストの control plane** であり、
    すでに使っているチャットアプリからアクセス可能な
    有能なアシスタントを **自分のハードウェア上** で動かし、状態を持つセッション、メモリ、ツールを使いつつ、
    ワークフローの制御をホスト型 SaaS に渡さずに済むようにします。

    特長:

    - **あなたのデバイス、あなたのデータ:** Gateway は好きな場所（Mac、Linux、VPS）で動かし、
      workspace + セッション履歴をローカルに保持できます。
    - **Web サンドボックスではなく実際のチャンネル:** WhatsApp / Telegram / Slack / Discord / Signal / iMessage など、
      さらに対応プラットフォームではモバイル音声と Canvas。
    - **モデル非依存:** Anthropic、OpenAI、MiniMax、OpenRouter などを、エージェントごとのルーティング
      とフェイルオーバー付きで利用できます。
    - **ローカル専用オプション:** ローカルモデルを動かせば、必要に応じて **すべてのデータを自分のデバイスに残せます**。
    - **マルチエージェントルーティング:** チャンネル、アカウント、またはタスクごとにエージェントを分け、
      それぞれ独自の workspace とデフォルトを持たせられます。
    - **オープンソースでハック可能:** 調査、拡張、セルフホストができ、ベンダーロックインもありません。

    ドキュメント: [Gateway](/ja-JP/gateway), [Channels](/ja-JP/channels), [Multi-agent](/ja-JP/concepts/multi-agent),
    [Memory](/ja-JP/concepts/memory)。

  </Accordion>

  <Accordion title="セットアップしたばかりです。最初に何をすべきですか？">
    最初のプロジェクト候補:

    - Web サイトを作る（WordPress、Shopify、またはシンプルな静的サイト）。
    - モバイルアプリを試作する（概要、画面、API 計画）。
    - ファイルやフォルダーを整理する（クリーンアップ、命名、タグ付け）。
    - Gmail を接続し、要約やフォローアップを自動化する。

    大きなタスクも扱えますが、フェーズに分けて
    サブエージェントで並列作業すると、最もよく機能します。

  </Accordion>

  <Accordion title="OpenClaw の日常的なユースケース上位 5 つは何ですか？">
    日常での効果が大きい使い方は、通常次のようなものです:

    - **個人向けブリーフィング:** 受信箱、カレンダー、気になるニュースの要約。
    - **調査とドラフト作成:** メールやドキュメントのための素早い調査、要約、初稿作成。
    - **リマインダーとフォローアップ:** cron や heartbeat 駆動の通知やチェックリスト。
    - **ブラウザ自動化:** フォーム入力、データ収集、反復的な Web 作業。
    - **クロスデバイス連携:** スマートフォンからタスクを送り、Gateway がサーバー上で実行し、結果をチャットに返す。

  </Accordion>

  <Accordion title="OpenClaw は SaaS 向けのリード獲得、アウトリーチ、広告、ブログに役立ちますか？">
    **調査、選別、ドラフト作成** には有効です。サイトを走査し、候補リストを作り、
    見込み客を要約し、アウトリーチ文や広告コピーの下書きを作れます。

    **アウトリーチや広告運用** については、人をループ内に残してください。スパムを避け、地域法と
    プラットフォームポリシーに従い、送信前に必ず確認してください。最も安全なのは、
    OpenClaw に下書きさせ、あなたが承認するパターンです。

    ドキュメント: [Security](/ja-JP/gateway/security)。

  </Accordion>

  <Accordion title="Web 開発では Claude Code と比べてどんな利点がありますか？">
    OpenClaw は **個人アシスタント** かつ連携レイヤーであり、IDE の置き換えではありません。リポジトリ内で最速の直接コーディングループが必要なら
    Claude Code や Codex を使ってください。永続メモリ、クロスデバイスアクセス、
    ツールオーケストレーションが必要なら OpenClaw を使ってください。

    利点:

    - セッションをまたぐ **永続メモリ + workspace**
    - **マルチプラットフォームアクセス**（WhatsApp、Telegram、TUI、WebChat）
    - **ツールオーケストレーション**（ブラウザ、ファイル、スケジューリング、フック）
    - **常時稼働の Gateway**（VPS で動かし、どこからでも操作）
    - ローカル browser / screen / camera / exec 用の **Nodes**

    ショーケース: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills と自動化

<AccordionGroup>
  <Accordion title="リポジトリを汚さずに Skills をカスタマイズするにはどうすればよいですか？">
    リポジトリ内のコピーを編集する代わりに、管理された override を使ってください。変更は `~/.openclaw/skills/<name>/SKILL.md` に置くか、`~/.openclaw/openclaw.json` の `skills.load.extraDirs` 経由でフォルダーを追加してください。優先順位は `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` なので、管理された override は git に触れずに bundled skills より優先されます。グローバルにはインストールしたいが一部のエージェントにだけ見せたい場合は、共有コピーを `~/.openclaw/skills` に置き、可視性は `agents.defaults.skills` と `agents.list[].skills` で制御してください。upstream に価値のある編集だけをリポジトリに置き、PR として出してください。
  </Accordion>

  <Accordion title="カスタムフォルダーから Skills を読み込めますか？">
    はい。`~/.openclaw/openclaw.json` の `skills.load.extraDirs` で追加ディレクトリを指定できます（最も低い優先順位）。デフォルトの優先順位は `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` です。`clawhub` はデフォルトで `./skills` にインストールし、OpenClaw は次のセッションでそれを `<workspace>/skills` として扱います。その skill を特定のエージェントにだけ見せたい場合は、`agents.defaults.skills` または `agents.list[].skills` と組み合わせてください。
  </Accordion>

  <Accordion title="タスクごとに異なるモデルを使うにはどうすればよいですか？">
    現在サポートされているパターンは次のとおりです:

    - **Cron jobs**: 独立したジョブごとに `model` override を設定できます。
    - **Sub-agents**: 異なるデフォルトモデルを持つ別エージェントにタスクをルーティングします。
    - **On-demand switch**: `/model` を使って現在のセッションモデルをいつでも切り替えます。

    [Cron jobs](/ja-JP/automation/cron-jobs), [Multi-Agent Routing](/ja-JP/concepts/multi-agent), [Slash commands](/ja-JP/tools/slash-commands) を参照してください。

  </Accordion>

  <Accordion title="重い作業中にボットが固まります。どうやってオフロードすればよいですか？">
    長いタスクや並列タスクには **sub-agents** を使ってください。Sub-agents は独自のセッションで動作し、
    要約を返し、メインチャットの応答性を維持します。

    ボットに「このタスクのために sub-agent を spawn して」と頼むか、`/subagents` を使ってください。
    チャット内の `/status` で、Gateway が今何をしているか（そして busy かどうか）を確認できます。

    トークンのヒント: 長いタスクも sub-agents もトークンを消費します。コストが気になる場合は、
    `agents.defaults.subagents.model` で sub-agents により安価なモデルを設定してください。

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents), [Background Tasks](/ja-JP/automation/tasks)。

  </Accordion>

  <Accordion title="Discord で thread に結び付いた subagent session はどのように機能しますか？">
    thread binding を使ってください。Discord thread を subagent または session target にバインドできるため、その thread 内の後続メッセージは、そのバインドされた session に留まります。

    基本フロー:

    - `sessions_spawn` を `thread: true` 付きで呼び出します（持続的な follow-up が必要なら `mode: "session"` も指定）。
    - または `/focus <target>` で手動バインドします。
    - `/agents` で binding 状態を確認します。
    - `/session idle <duration|off>` と `/session max-age <duration|off>` で自動 unfocus を制御します。
    - `/unfocus` で thread を切り離します。

    必須設定:

    - グローバルデフォルト: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`。
    - Discord override: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`。
    - spawn 時の自動バインド: `channels.discord.threadBindings.spawnSubagentSessions: true` を設定します。

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents), [Discord](/ja-JP/channels/discord), [Configuration Reference](/ja-JP/gateway/configuration-reference), [Slash commands](/ja-JP/tools/slash-commands)。

  </Accordion>

  <Accordion title="subagent が完了したのに、完了通知が間違った場所に行った、または投稿されませんでした。何を確認すべきですか？">
    まず解決された requester route を確認してください:

    - 完了モードの subagent 配信は、存在する場合はバインドされた thread または conversation route を優先します。
    - 完了元に channel しか含まれていない場合、OpenClaw は requester session に保存された route（`lastChannel` / `lastTo` / `lastAccountId`）へフォールバックし、direct 配信が引き続き成功できるようにします。
    - バインド済み route も使用可能な保存 route も存在しない場合、direct 配信は失敗し、結果はチャットへ即時投稿されず queued session delivery にフォールバックします。
    - 無効または古い target は、queue fallback や最終的な配信失敗を引き起こすことがあります。
    - child の最後に表示された assistant reply が、完全にサイレントトークン `NO_REPLY` / `no_reply` またはちょうど `ANNOUNCE_SKIP` の場合、OpenClaw は古い進捗を投稿しないよう意図的に announce を抑制します。
    - child が tool call だけで timeout した場合、announce は生の tool output を再生せず、短い partial-progress summary にまとめることがあります。

    デバッグ:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Sub-agents](/ja-JP/tools/subagents), [Background Tasks](/ja-JP/automation/tasks), [Session Tools](/ja-JP/concepts/session-tool)。

  </Accordion>

  <Accordion title="Cron や reminder が発火しません。何を確認すべきですか？">
    Cron は Gateway プロセス内で実行されます。Gateway が継続的に動作していないと、
    スケジュール済みジョブは実行されません。

    チェックリスト:

    - cron が有効か（`cron.enabled`）、そして `OPENCLAW_SKIP_CRON` が設定されていないかを確認します。
    - Gateway が 24/7 稼働しているか（スリープ / 再起動がないか）確認します。
    - ジョブのタイムゾーン設定（`--tz` とホストタイムゾーン）を確認します。

    デバッグ:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [Automation & Tasks](/ja-JP/automation)。

  </Accordion>

  <Accordion title="Cron は発火したのに、チャンネルに何も送られませんでした。なぜですか？">
    まず配信モードを確認してください:

    - `--no-deliver` / `delivery.mode: "none"` は、外部メッセージが送られないことを意味します。
    - announce target（`channel` / `to`）がない、または無効な場合、runner は outbound delivery をスキップします。
    - channel auth failure（`unauthorized`, `Forbidden`）は、runner が配信を試みたが資格情報に阻まれたことを意味します。
    - サイレントな isolated result（`NO_REPLY` / `no_reply` のみ）は意図的に配信不可として扱われるため、runner も queued fallback delivery を抑制します。

    isolated cron jobs では、runner が最終配信を担当します。エージェントには、
    runner が送信できるプレーンテキスト要約を返すことが期待されます。`--no-deliver` は
    その結果を内部に留めるだけであり、代わりに
    message tool で直接送信できるようにはしません。

    デバッグ:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [Background Tasks](/ja-JP/automation/tasks)。

  </Accordion>

  <Accordion title="isolated cron run がモデルを切り替えたり 1 回再試行したりしたのはなぜですか？">
    それは通常、重複スケジューリングではなく live model-switch path です。

    isolated cron は、アクティブな
    実行が `LiveSessionModelSwitchError` を投げたとき、ランタイムの model handoff を永続化して再試行できます。再試行では切り替え後の
    provider / model を維持し、切り替えに新しい auth profile override が含まれていた場合は、cron はそれも永続化してから再試行します。

    関連する選択ルール:

    - Gmail hook の model override が該当する場合、最初に優先されます。
    - 次にジョブごとの `model`。
    - 次に保存されている cron-session model override。
    - その後、通常の agent / default model selection。

    再試行ループには上限があります。初回試行 + 2 回の switch retry の後、
    cron は無限にループせず中止します。

    デバッグ:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [cron CLI](/cli/cron)。

  </Accordion>

  <Accordion title="Linux に Skills をインストールするにはどうすればよいですか？">
    ネイティブの `openclaw skills` コマンドを使うか、skill を workspace に直接配置してください。macOS の Skills UI は Linux では利用できません。
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
    ディレクトリに書き込みます。自分の Skills を publish または
    sync したい場合にのみ、別個の `clawhub` CLI をインストールしてください。エージェント間で共有するインストールには、skill を
    `~/.openclaw/skills` 配下に置き、見えるエージェントを限定したい場合は
    `agents.defaults.skills` または
    `agents.list[].skills` を使ってください。

  </Accordion>

  <Accordion title="OpenClaw はスケジュール実行や継続的なバックグラウンドタスクを実行できますか？">
    はい。Gateway scheduler を使用します:

    - **Cron jobs**: スケジュール済みまたは繰り返しタスク（再起動後も保持）。
    - **Heartbeat**: 「メインセッション」の定期チェック。
    - **Isolated jobs**: 要約を投稿したりチャットへ配信したりする自律エージェント用。

    ドキュメント: [Cron jobs](/ja-JP/automation/cron-jobs), [Automation & Tasks](/ja-JP/automation),
    [Heartbeat](/ja-JP/gateway/heartbeat)。

  </Accordion>

  <Accordion title="Linux から Apple の macOS 専用 Skills を実行できますか？">
    直接はできません。macOS skills は `metadata.openclaw.os` と必要なバイナリでゲートされており、skills は **Gateway host** 上で適格な場合にのみ system prompt に現れます。Linux では、`darwin` 専用 skills（`apple-notes`, `apple-reminders`, `things-mac` など）は、ゲーティングを override しない限りロードされません。

    サポートされているパターンは 3 つあります:

    **Option A - Gateway を Mac 上で動かす（最も簡単）。**
    Gateway を macOS バイナリが存在する場所で動かし、Linux からは [remote mode](#gateway-ポートがすでに動作している場合と-remote-mode) または Tailscale 経由で接続します。Gateway host が macOS なので skills は通常どおりロードされます。

    **Option B - macOS node を使う（SSH 不要）。**
    Gateway は Linux 上で動かし、macOS node（メニューバーアプリ）をペアリングし、Mac 側で **Node Run Commands** を 「Always Ask」 または 「Always Allow」 に設定します。必要なバイナリが node 上に存在する場合、OpenClaw は macOS 専用 skills を適格として扱えます。エージェントは `nodes` tool 経由でそれらの skills を実行します。「Always Ask」を選んだ場合、プロンプトで 「Always Allow」 を承認すると、そのコマンドが allowlist に追加されます。

    **Option C - macOS バイナリを SSH 越しにプロキシする（上級者向け）。**
    Gateway は Linux 上に置いたまま、必要な CLI バイナリを Mac 上で実行する SSH wrapper として解決させます。その後、skill を override して Linux を許可し、適格なままにします。

    1. バイナリ用の SSH wrapper を作成します（例: Apple Notes 用の `memo`）:

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

    4. 新しいセッションを開始して skills snapshot を更新します。

  </Accordion>

  <Accordion title="Notion や HeyGen との統合はありますか？">
    現時点では組み込みではありません。

    選択肢:

    - **Custom skill / plugin:** 信頼できる API アクセスには最適です（Notion / HeyGen はどちらも API があります）。
    - **Browser automation:** コード不要で動きますが、遅く壊れやすいです。

    クライアントごとにコンテキストを保持したい場合（代理店ワークフローなど）、単純なパターンは次のとおりです:

    - クライアントごとに 1 つの Notion ページ（コンテキスト + 好み + 進行中の作業）。
    - セッション開始時にそのページを取得するようエージェントに依頼する。

    ネイティブ統合が欲しい場合は、機能リクエストを出すか、
    それらの API を対象とする skill を構築してください。

    Skills のインストール:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    ネイティブインストールはアクティブな workspace の `skills/` ディレクトリに入ります。エージェント間で共有する Skills には、`~/.openclaw/skills/<name>/SKILL.md` に配置してください。共有インストールを一部のエージェントにだけ見せたい場合は、`agents.defaults.skills` または `agents.list[].skills` を設定してください。Homebrew でインストールしたバイナリを期待する Skills もあり、Linux では Linuxbrew を意味します（上の Homebrew Linux FAQ 項目を参照）。[Skills](/ja-JP/tools/skills), [Skills config](/ja-JP/tools/skills-config), [ClawHub](/ja-JP/tools/clawhub) を参照してください。

  </Accordion>

  <Accordion title="既存のサインイン済み Chrome を OpenClaw で使うにはどうすればよいですか？">
    Chrome DevTools MCP を通じて接続する、組み込みの `user` browser profile を使ってください:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    カスタム名が欲しい場合は、明示的な MCP profile を作成します:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    この経路は host-local です。Gateway が別の場所で動作している場合は、browser マシン上で node host を動かすか、代わりに remote CDP を使ってください。

    現在の `existing-session` / `user` の制限:

    - アクションは CSS selector 駆動ではなく ref 駆動です
    - アップロードには `ref` / `inputRef` が必要で、現時点では一度に 1 ファイルのみ対応です
    - `responsebody`、PDF export、download interception、batch actions には、依然として managed browser または raw CDP profile が必要です

  </Accordion>
</AccordionGroup>

## サンドボックスとメモリ

<AccordionGroup>
  <Accordion title="専用の sandboxing ドキュメントはありますか？">
    はい。[Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。Docker 固有のセットアップ（Docker 内の full gateway または sandbox image）については、[Docker](/ja-JP/install/docker) を参照してください。
  </Accordion>

  <Accordion title="Docker は制限が多く感じます。フル機能を有効にするにはどうすればよいですか？">
    デフォルトイメージはセキュリティ優先で、`node` ユーザーとして動作するため、
    system package、Homebrew、bundled browser は含まれていません。より充実したセットアップには:

    - `/home/node` を `OPENCLAW_HOME_VOLUME` で永続化し、キャッシュを維持する。
    - `OPENCLAW_DOCKER_APT_PACKAGES` で system deps をイメージに焼き込む。
    - バンドルされた CLI で Playwright browser をインストールする:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - `PLAYWRIGHT_BROWSERS_PATH` を設定し、そのパスが永続化されるようにする。

    ドキュメント: [Docker](/ja-JP/install/docker), [Browser](/ja-JP/tools/browser)。

  </Accordion>

  <Accordion title="1 つのエージェントで DM は個人的に、グループは公開 / sandboxed にできますか？">
    はい。あなたの private traffic が **DM** で、public traffic が **group** なら可能です。

    `agents.defaults.sandbox.mode: "non-main"` を使うと、group / channel session（non-main key）は Docker 内で動作し、メイン DM session はホスト上に残ります。その後、sandboxed session で利用できる tool を `tools.sandbox.tools` で制限してください。

    設定手順 + 例: [Groups: personal DMs + public groups](/ja-JP/channels/groups#pattern-personal-dms-public-groups-single-agent)

    主な設定リファレンス: [Gateway configuration](/ja-JP/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="ホストフォルダーを sandbox に bind するにはどうすればよいですか？">
    `agents.defaults.sandbox.docker.binds` を `["host:path:mode"]`（例: `"/home/user/src:/src:ro"`）に設定してください。グローバル + エージェントごとの bind はマージされます。`scope: "shared"` の場合、エージェントごとの bind は無視されます。機密性の高いものには `:ro` を使い、bind は sandbox のファイルシステム境界を迂回することを忘れないでください。

    OpenClaw は bind source を、正規化パスと、最も深い既存 ancestor を通じて解決された canonical path の両方に対して検証します。つまり、最後の path segment がまだ存在しなくても symlink 親からの escape は fail closed し、symlink 解決後も allowed-root チェックが適用されます。

    例と安全上の注意については、[Sandboxing](/ja-JP/gateway/sandboxing#custom-bind-mounts) と [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) を参照してください。

  </Accordion>

  <Accordion title="メモリはどのように機能しますか？">
    OpenClaw のメモリは、エージェント workspace 内の Markdown ファイルです:

    - `memory/YYYY-MM-DD.md` の daily notes
    - `MEMORY.md` の curated long-term notes（main / private session のみ）

    OpenClaw は、モデルに durable notes を書くよう促すために、
    **サイレントな pre-compaction memory flush** も実行します。これは workspace が
    書き込み可能な場合にのみ動作し（read-only sandbox ではスキップされます）、[Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>

  <Accordion title="メモリが物事を忘れ続けます。定着させるにはどうすればよいですか？">
    その事実を **メモリに書き込む** ようボットに頼んでください。長期的なメモは `MEMORY.md` に、
    短期的なコンテキストは `memory/YYYY-MM-DD.md` に入ります。

    これはまだ改善中の領域です。モデルにメモリ保存を促すと役立ちます。
    モデルは何をすべきか理解しています。それでも忘れ続ける場合は、Gateway が毎回
    同じ workspace を使っているか確認してください。

    ドキュメント: [Memory](/ja-JP/concepts/memory), [Agent workspace](/ja-JP/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="メモリは永続しますか？ 制限は何ですか？">
    メモリファイルはディスク上にあり、自分で削除するまで保持されます。制限は
    モデルではなくストレージです。ただし **session context** は依然としてモデルの
    context window に制限されるため、長い会話では compact や truncate が発生します。そのため、
    memory search が存在します。これは関連部分だけをコンテキストに戻します。

    ドキュメント: [Memory](/ja-JP/concepts/memory), [Context](/ja-JP/concepts/context)。

  </Accordion>

  <Accordion title="semantic memory search には OpenAI API key が必要ですか？">
    **OpenAI embeddings** を使う場合のみ必要です。Codex OAuth は chat / completions を対象としており、
    embeddings アクセスは付与しません。したがって、**Codex でサインインしても（OAuth または
    Codex CLI login） semantic memory search には役立ちません**。OpenAI embeddings には
    依然として本物の API キー（`OPENAI_API_KEY` または `models.providers.openai.apiKey`）が必要です。

    provider を明示的に設定しない場合、OpenClaw は API key を解決できるときに
    自動で provider を選択します（auth profiles、`models.providers.*.apiKey`、または env vars）。
    OpenAI key が解決できれば OpenAI を優先し、そうでなければ Gemini、
    次に Voyage、その次に Mistral を優先します。remote key が利用できない場合、
    設定するまで memory search は無効のままです。ローカルモデル経路が
    設定済みで存在する場合、OpenClaw は
    `local` を優先します。Ollama は `memorySearch.provider = "ollama"` を明示的に設定した場合にサポートされます。

    ローカルのままにしたい場合は、`memorySearch.provider = "local"`（必要に応じて
    `memorySearch.fallback = "none"` も）を設定してください。Gemini embeddings を使いたい場合は、
    `memorySearch.provider = "gemini"` を設定し、`GEMINI_API_KEY`（または
    `memorySearch.remote.apiKey`）を指定してください。**OpenAI、Gemini、Voyage、Mistral、Ollama、または local** の embedding
    モデルをサポートしています。設定詳細は [Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>
</AccordionGroup>

## ディスク上の保存場所

<AccordionGroup>
  <Accordion title="OpenClaw で使われるデータはすべてローカルに保存されますか？">
    いいえ。**OpenClaw の state はローカル** ですが、**外部サービスは送信されたものを見ます**。

    - **デフォルトでローカル:** sessions、memory files、config、workspace は Gateway host 上にあります
      （`~/.openclaw` + あなたの workspace ディレクトリ）。
    - **必然的にリモート:** model providers（Anthropic / OpenAI など）へ送るメッセージは
      それらの API に届き、chat platforms（WhatsApp / Telegram / Slack など）はメッセージデータを
      それぞれのサーバーに保存します。
    - **フットプリントは自分で制御可能:** ローカルモデルを使えばプロンプトは自分のマシン上に留まりますが、channel
      traffic は依然としてそのチャンネルのサーバーを通ります。

    関連: [Agent workspace](/ja-JP/concepts/agent-workspace), [Memory](/ja-JP/concepts/memory)。

  </Accordion>

  <Accordion title="OpenClaw はデータをどこに保存しますか？">
    すべては `$OPENCLAW_STATE_DIR`（デフォルト: `~/.openclaw`）配下にあります:

    | Path                                                            | Purpose                                                            |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | メイン設定（JSON5）                                                |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | レガシー OAuth import（初回利用時に auth profiles にコピーされる）       |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Auth profiles（OAuth、API keys、およびオプションの `keyRef` / `tokenRef`）  |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef providers 用のオプションの file-backed secret payload |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | レガシー互換ファイル（静的な `api_key` エントリは除去済み）      |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Provider state（例: `whatsapp/<accountId>/creds.json`）            |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | エージェントごとの state（agentDir + sessions）                              |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 会話履歴と state（agent ごと）                           |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Session metadata（agent ごと）                                       |

    レガシーの single-agent パス: `~/.openclaw/agent/*`（`openclaw doctor` によって移行されます）。

    **Workspace**（AGENTS.md、memory files、skills など）は別で、`agents.defaults.workspace`（デフォルト: `~/.openclaw/workspace`）経由で設定されます。

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md はどこに置くべきですか？">
    これらのファイルは `~/.openclaw` ではなく、**agent workspace** に置きます。

    - **Workspace（agent ごと）**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md`（`MEMORY.md` がない場合はレガシーフォールバックの `memory.md`）、
      `memory/YYYY-MM-DD.md`, オプションの `HEARTBEAT.md`。
    - **State dir（`~/.openclaw`）**: config、channel / provider state、auth profiles、sessions、logs、
      および共有 skills（`~/.openclaw/skills`）。

    デフォルト workspace は `~/.openclaw/workspace` で、次で設定可能です:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    再起動後にボットが「忘れる」場合は、Gateway が毎回同じ
    workspace を使って起動しているか確認してください（そして remote mode では、使われるのは **gateway host 側の**
    workspace であり、ローカルのノート PC ではないことを忘れないでください）。

    ヒント: 永続的な振る舞いや好みが欲しい場合は、
    チャット履歴に頼るのではなく、**AGENTS.md や MEMORY.md に書き込む** ようボットに頼んでください。

    [Agent workspace](/ja-JP/concepts/agent-workspace) と [Memory](/ja-JP/concepts/memory) を参照してください。

  </Accordion>

  <Accordion title="推奨バックアップ戦略">
    **agent workspace** を **private** な git リポジトリに入れ、どこか
    private な場所（例: GitHub private）にバックアップしてください。これにより memory + AGENTS / SOUL / USER
    ファイルが保存され、後からアシスタントの「心」を復元できます。

    `~/.openclaw` 配下のもの（credentials、sessions、tokens、または暗号化 secret payload）は
    commit しないでください。
    完全な復元が必要な場合は、workspace と state directory の
    両方を別々にバックアップしてください（上の移行に関する質問を参照）。

    ドキュメント: [Agent workspace](/ja-JP/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="OpenClaw を完全にアンインストールするにはどうすればよいですか？">
    専用ガイドを参照してください: [Uninstall](/ja-JP/install/uninstall)。
  </Accordion>

  <Accordion title="エージェントは workspace の外で作業できますか？">
    はい。workspace は **デフォルト cwd** とメモリアンカーであって、厳格な sandbox ではありません。
    相対パスは workspace 内で解決されますが、sandboxing が有効でなければ
    絶対パスはホスト上の他の場所にアクセスできます。分離が必要なら、
    [`agents.defaults.sandbox`](/ja-JP/gateway/sandboxing) またはエージェントごとの sandbox 設定を使用してください。リポジトリをデフォルト作業ディレクトリにしたい場合は、その
    エージェントの `workspace` をリポジトリルートに向けてください。OpenClaw リポジトリは単なるソースコードなので、
    意図的にその中でエージェントに作業させたい場合を除き、workspace は分けてください。

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
    Session state を所有するのは **gateway host** です。remote mode の場合、気にすべき session store はローカルのノート PC ではなくリモートマシン上にあります。[Session management](/ja-JP/concepts/session) を参照してください。
  </Accordion>
</AccordionGroup>

## 設定の基本

<AccordionGroup>
  <Accordion title="設定ファイルの形式は何ですか？ どこにありますか？">
    OpenClaw は `$OPENCLAW_CONFIG_PATH`（デフォルト: `~/.openclaw/openclaw.json`）からオプションの **JSON5** 設定を読み込みます:

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    ファイルが存在しない場合は、比較的安全なデフォルト（`~/.openclaw/workspace` をデフォルト workspace に含む）が使われます。

  </Accordion>

  <Accordion title='gateway.bind: "lan"（または "tailnet"）を設定したら、何も listen しなくなった / UI に unauthorized と表示される'>
    non-loopback bind には **有効な gateway auth path** が必要です。実際には次のいずれかです:

    - shared-secret auth: token または password
    - 正しく設定された non-loopback の ID 認識リバースプロキシの背後にある `gateway.auth.mode: "trusted-proxy"`

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

    注記:

    - `gateway.remote.token` / `.password` だけではローカル gateway auth は有効になりません。
    - ローカル call path では、`gateway.auth.*` が未設定の場合にのみ `gateway.remote.*` を fallback として使えます。
    - password auth には、代わりに `gateway.auth.mode: "password"` と `gateway.auth.password`（または `OPENCLAW_GATEWAY_PASSWORD`）を設定してください。
    - `gateway.auth.token` / `gateway.auth.password` が SecretRef 経由で明示的に設定され、未解決の場合、解決は fail closed します（remote fallback によるマスキングはありません）。
    - shared-secret の Control UI セットアップでは、`connect.params.auth.token` または `connect.params.auth.password`（アプリ / UI 設定に保存）で認証します。Tailscale Serve や `trusted-proxy` のような ID 付きモードでは代わりに request headers を使います。共有シークレットを URL に入れないでください。
    - `gateway.auth.mode: "trusted-proxy"` の場合、同一ホストの loopback リバースプロキシは依然として trusted-proxy auth を満たしません。trusted proxy は設定された non-loopback source である必要があります。

  </Accordion>

  <Accordion title="なぜ今は localhost でも token が必要なのですか？">
    OpenClaw は、loopback を含めデフォルトで gateway auth を強制します。通常のデフォルト経路では token auth を意味します。明示的な auth path が設定されていない場合、gateway 起動時に token mode に解決されて自動生成され、`gateway.auth.token` に保存されるため、**ローカル WS クライアントも認証が必要** です。これにより、他のローカルプロセスが Gateway を呼び出すのを防ぎます。

    別の auth path がよければ、password mode（または non-loopback の ID 認識リバースプロキシでは `trusted-proxy`）を明示的に選べます。**本当に** open loopback が欲しい場合は、config に `gateway.auth.mode: "none"` を明示的に設定してください。Doctor はいつでもトークンを生成できます: `openclaw doctor --generate-gateway-token`。

  </Accordion>

  <Accordion title="設定変更後に再起動は必要ですか？">
    Gateway は設定を監視しており、hot-reload をサポートしています:

    - `gateway.reload.mode: "hybrid"`（デフォルト）: 安全な変更は hot-apply、重要な変更は restart
    - `hot`, `restart`, `off` もサポートされます

  </Accordion>

  <Accordion title="CLI の変なキャッチフレーズを無効にするにはどうすればよいですか？">
    config で `cli.banner.taglineMode` を設定します:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: tagline テキストを隠しますが、banner の title / version 行は維持します。
    - `default`: 常に `All your chats, one OpenClaw.` を使います。
    - `random`: 季節ものを含むローテーションの面白い tagline（デフォルト動作）。
    - banner 自体を消したい場合は、env `OPENCLAW_HIDE_BANNER=1` を設定してください。

  </Accordion>

  <Accordion title="web search（と web fetch）を有効にするにはどうすればよいですか？">
    `web_fetch` は API key なしで動作します。`web_search` は選択した
    provider に依存します:

    - Brave、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Perplexity、Tavily のような API ベース provider には、通常どおりの API key 設定が必要です。
    - Ollama Web Search は key 不要ですが、設定済み Ollama host を使用し、`ollama signin` が必要です。
    - DuckDuckGo は key 不要ですが、非公式の HTML ベース統合です。
    - SearXNG は key 不要 / self-hosted です。`SEARXNG_BASE_URL` または `plugins.entries.searxng.config.webSearch.baseUrl` を設定してください。

    **推奨:** `openclaw configure --section web` を実行して provider を選択してください。
    env の代替設定:

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
              provider: "firecrawl", // optional; omit for auto-detect
            },
          },
        },
    }
    ```

    provider 固有の web-search 設定は、現在 `plugins.entries.<plugin>.config.webSearch.*` 配下にあります。
    旧来の `tools.web.search.*` provider path も一時的には互換性のため読み込まれますが、新しい設定では使うべきではありません。
    Firecrawl の web-fetch fallback 設定は `plugins.entries.firecrawl.config.webFetch.*` 配下にあります。

    注記:

    - allowlist を使っている場合は、`web_search` / `web_fetch` / `x_search` または `group:web` を追加してください。
    - `web_fetch` はデフォルトで有効です（明示的に無効にしない限り）。
    - `tools.web.fetch.provider` を省略すると、OpenClaw は利用可能な資格情報から最初に準備できた fetch fallback provider を自動検出します。現在の bundled provider は Firecrawl です。
    - daemon は `~/.openclaw/.env`（または service environment）から env vars を読み取ります。

    ドキュメント: [Web tools](/ja-JP/tools/web)。

  </Accordion>

  <Accordion title="config.apply で設定が消えました。どうやって復旧し、どう避ければよいですか？">
    `config.apply` は **設定全体** を置き換えます。部分オブジェクトを送ると、
    それ以外はすべて削除されます。

    復旧方法:

    - バックアップから復元する（git またはコピーしておいた `~/.openclaw/openclaw.json`）。
    - バックアップがない場合は、`openclaw doctor` を再実行し、channels / models を再設定する。
    - 想定外だった場合は、バグ報告し、最後に分かっている設定やバックアップがあれば含めてください。
    - ローカルの coding agent であれば、ログや履歴から動く設定を再構築できることがよくあります。

    回避方法:

    - 小さな変更には `openclaw config set` を使う。
    - 対話編集には `openclaw configure` を使う。
    - 正確な path や field 形状が不明なときは、まず `config.schema.lookup` を使う。浅い schema node と直下の child summaries を返し、段階的に掘り下げられます。
    - 部分的な RPC 編集には `config.patch` を使い、`config.apply` は full-config replacement 専用にする。
    - エージェント実行から owner-only の `gateway` tool を使っている場合でも、`tools.exec.ask` / `tools.exec.security` への書き込み（同じ protected exec paths に正規化される旧 `tools.bash.*` alias を含む）は拒否されます。

    ドキュメント: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/ja-JP/gateway/doctor)。

  </Accordion>

  <Accordion title="中央 Gateway と、各デバイス上の specialized worker をどう構成すればよいですか？">
    一般的なパターンは **1 つの Gateway**（例: Raspberry Pi）と **nodes** および **agents** です:

    - **Gateway（中央）:** channels（Signal / WhatsApp）、routing、sessions を所有。
    - **Nodes（デバイス）:** Mac / iOS / Android が peripheral として接続し、ローカル tool（`system.run`, `canvas`, `camera`）を公開。
    - **Agents（workers）:** 特化した役割のための別々の brain / workspace（例: 「Hetzner ops」「Personal data」）。
    - **Sub-agents:** メインエージェントから background work を spawn して並列化したいときに使用。
    - **TUI:** Gateway に接続し、agents / sessions を切り替える。

    ドキュメント: [Nodes](/ja-JP/nodes), [Remote access](/ja-JP/gateway/remote), [Multi-Agent Routing](/ja-JP/concepts/multi-agent), [Sub-agents](/ja-JP/tools/subagents), [TUI](/web/tui)。

  </Accordion>

  <Accordion title="OpenClaw の browser は headless で動作しますか？">
    はい。設定オプションです:

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

    デフォルトは `false`（headful）です。Headless は一部のサイトで anti-bot チェックを引き起こしやすくなります。[Browser](/ja-JP/tools/browser) を参照してください。

    Headless は **同じ Chromium engine** を使い、多くの自動化（フォーム、クリック、スクレイピング、ログイン）に対応します。主な違いは:

    - 可視の browser window がない（視覚確認が必要ならスクリーンショットを使う）。
    - 一部のサイトは headless mode での自動化により厳しい（CAPTCHA、anti-bot）。
      例えば、X / Twitter は headless session をよくブロックします。

  </Accordion>

  <Accordion title="ブラウザ制御に Brave を使うにはどうすればよいですか？">
    `browser.executablePath` を Brave バイナリ（または任意の Chromium ベース browser）に設定し、Gateway を再起動してください。
    完全な設定例は [Browser](/ja-JP/tools/browser#use-brave-or-another-chromium-based-browser) を参照してください。
  </Accordion>
</AccordionGroup>

## リモート Gateway と nodes

<AccordionGroup>
  <Accordion title="Telegram、gateway、nodes の間でコマンドはどう伝播しますか？">
    Telegram メッセージは **gateway** によって処理されます。gateway がエージェントを実行し、
    node tool が必要な場合にのみ **Gateway WebSocket** 経由で nodes を呼び出します:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Nodes は受信した provider traffic を見ません。受け取るのは node RPC 呼び出しだけです。

  </Accordion>

  <Accordion title="Gateway がリモートでホストされているとき、エージェントはどうやって自分のコンピューターにアクセスしますか？">
    短い答え: **自分のコンピューターを node としてペアリング** してください。Gateway は別の場所で動作していても、
    Gateway WebSocket 経由でローカルマシン上の `node.*` tools（screen、camera、system）を呼び出せます。

    典型的なセットアップ:

    1. 常時稼働ホスト（VPS / home server）で Gateway を動かす。
    2. Gateway host と自分のコンピューターを同じ tailnet に入れる。
    3. Gateway WS に到達できることを確認する（tailnet bind または SSH tunnel）。
    4. ローカルで macOS アプリを開き、**Remote over SSH** モード（または direct tailnet）
       で接続し、node として登録できるようにする。
    5. Gateway 上で node を承認する:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    別個の TCP bridge は不要です。nodes は Gateway WebSocket 経由で接続します。

    セキュリティ注意: macOS node をペアリングすると、そのマシン上で `system.run` を許可することになります。信頼できるデバイスだけを
    ペアリングし、[Security](/ja-JP/gateway/security) を確認してください。

    ドキュメント: [Nodes](/ja-JP/nodes), [Gateway protocol](/ja-JP/gateway/protocol), [macOS remote mode](/ja-JP/platforms/mac/remote), [Security](/ja-JP/gateway/security)。

  </Accordion>

  <Accordion title="Tailscale は接続されているのに返信がありません。どうすればよいですか？">
    基本を確認してください:

    - Gateway が動作中か: `openclaw gateway status`
    - Gateway の健全性: `openclaw status`
    - Channel の健全性: `openclaw channels status`

    次に認証とルーティングを確認します:

    - Tailscale Serve を使っている場合は、`gateway.auth.allowTailscale` が正しく設定されていることを確認してください。
    - SSH tunnel 経由で接続している場合は、ローカルトンネルが有効で正しいポートを指していることを確認してください。
    - allowlist（DM または group）に自分のアカウントが含まれていることを確認してください。

    ドキュメント: [Tailscale](/ja-JP/gateway/tailscale), [Remote access](/ja-JP/gateway/remote), [Channels](/ja-JP/channels)。

  </Accordion>

  <Accordion title="2 つの OpenClaw インスタンスは相互に会話できますか（local + VPS）？">
    はい。組み込みの「bot-to-bot」bridge はありませんが、いくつかの
    信頼できる方法で接続できます:

    **最も簡単:** 両方の bot がアクセスできる通常の chat channel（Telegram / Slack / WhatsApp）を使います。
    Bot A が Bot B にメッセージを送り、その後 Bot B が通常どおり返信します。

    **CLI bridge（汎用）:** スクリプトを実行して、他方の Gateway を
    `openclaw agent --message ... --deliver` で呼び出し、相手 bot が
    監視しているチャットを対象にします。1 つの bot がリモート VPS 上にある場合は、
    SSH / Tailscale 経由でその remote Gateway を指すよう CLI を設定してください（[Remote access](/ja-JP/gateway/remote) を参照）。

    例のパターン（対象 Gateway に到達可能なマシンから実行）:

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    ヒント: 2 つの bot が無限ループしないようガードレールを追加してください（mention-only、channel
    allowlist、または「bot メッセージには返信しない」ルール）。

    ドキュメント: [Remote access](/ja-JP/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/ja-JP/tools/agent-send)。

  </Accordion>

  <Accordion title="複数エージェントのために別々の VPS が必要ですか？">
    いいえ。1 つの Gateway で複数の agents をホストでき、それぞれ独自の workspace、model defaults、
    routing を持てます。これは通常のセットアップであり、
    エージェントごとに VPS を動かすよりずっと安価で簡単です。

    別々の VPS が必要なのは、ハードな分離（セキュリティ境界）や、
    共有したくない大きく異なる設定が必要な場合だけです。それ以外は、1 つの Gateway を維持し、
    複数の agents または sub-agents を使ってください。

  </Accordion>

  <Accordion title="VPS から SSH する代わりに、個人のノート PC 上で node を使う利点はありますか？">
    はい。nodes は、remote Gateway からノート PC に到達するための第一級の方法であり、
    シェルアクセス以上のことができます。Gateway は macOS / Linux（Windows は WSL2 経由）で動作し、
    軽量です（小型の VPS や Raspberry Pi クラスのマシンで十分、4 GB RAM で余裕があります）。そのため、一般的な
    セットアップは常時稼働ホスト + ノート PC を node とする構成です。

    - **インバウンド SSH 不要。** Nodes は Gateway WebSocket へ outbound 接続し、device pairing を使用します。
    - **より安全な実行制御。** `system.run` はそのノート PC 上の node allowlists / approvals によって制御されます。
    - **より多くのデバイスツール。** Nodes は `system.run` に加えて `canvas`, `camera`, `screen` を公開します。
    - **ローカル browser automation。** Gateway は VPS に置きつつ、ノート PC 上の node host 経由で Chrome をローカル実行するか、ホスト上の Chrome MCP 経由でローカル Chrome に接続できます。

    SSH はアドホックな shell access には問題ありませんが、継続的な agent workflow や
    デバイス自動化には nodes の方が簡単です。

    ドキュメント: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes), [Browser](/ja-JP/tools/browser)。

  </Accordion>

  <Accordion title="nodes は gateway service を実行しますか？">
    いいえ。意図的に分離した profile を動かす場合（[Multiple gateways](/ja-JP/gateway/multiple-gateways) を参照）を除き、ホストごとに **gateway は 1 つだけ** 実行すべきです。nodes は gateway に接続する peripheral です
    （iOS / Android nodes、またはメニューバーアプリ内の macOS 「node mode」）。headless node
    hosts と CLI 制御については [Node host CLI](/cli/node) を参照してください。

    `gateway`, `discovery`, `canvasHost` の変更には完全再起動が必要です。

  </Accordion>

  <Accordion title="config を適用する API / RPC 方法はありますか？">
    はい。

    - `config.schema.lookup`: 1 つの config subtree を、その浅い schema node、対応する UI hint、直下の child summaries とともに確認してから書き込む
    - `config.get`: 現在の snapshot + hash を取得する
    - `config.patch`: 安全な部分更新（ほとんどの RPC 編集で推奨）。可能なら hot-reload、必要なら restart
    - `config.apply`: full config を検証して置換。可能なら hot-reload、必要なら restart
    - owner-only の `gateway` runtime tool は、依然として `tools.exec.ask` / `tools.exec.security` の書き換えを拒否します。旧 `tools.bash.*` alias は同じ protected exec paths に正規化されます

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

  <Accordion title="VPS に Tailscale を設定し、Mac から接続するにはどうすればよいですか？">
    最小手順:

    1. **VPS でインストール + ログイン**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Mac にインストール + ログイン**
       - Tailscale アプリを使い、同じ tailnet にサインインします。
    3. **MagicDNS を有効化（推奨）**
       - Tailscale 管理コンソールで MagicDNS を有効にし、VPS に安定した名前を付けます。
    4. **tailnet hostname を使う**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    SSH なしで Control UI を使いたい場合は、VPS で Tailscale Serve を使ってください:

    ```bash
    openclaw gateway --tailscale serve
    ```

    これにより gateway は loopback に bind されたまま、Tailscale 経由で HTTPS が公開されます。[Tailscale](/ja-JP/gateway/tailscale) を参照してください。

  </Accordion>

  <Accordion title="Mac node を remote Gateway（Tailscale Serve）に接続するにはどうすればよいですか？">
    Serve は **Gateway Control UI + WS** を公開します。Nodes は同じ Gateway WS endpoint 経由で接続します。

    推奨セットアップ:

    1. **VPS と Mac が同じ tailnet にあることを確認** します。
    2. **macOS アプリを Remote mode** で使います（SSH target は tailnet hostname でかまいません）。
       アプリは Gateway port をトンネルし、node として接続します。
    3. Gateway で node を承認します:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    ドキュメント: [Gateway protocol](/ja-JP/gateway/protocol), [Discovery](/ja-JP/gateway/discovery), [macOS remote mode](/ja-JP/platforms/mac/remote)。

  </Accordion>

  <Accordion title="2 台目のノート PC にインストールすべきですか、それとも node を追加すべきですか？">
    2 台目のノート PC で必要なのが **ローカル tools**（screen / camera / exec）だけなら、**node** として追加してください。
    これにより Gateway は 1 つのままで、設定重複を避けられます。ローカル node tools は
    現在 macOS 専用ですが、将来的には他の OS にも拡張する予定です。

    2 台目の Gateway をインストールすべきなのは、**強い分離** や 2 つの完全に独立した bot が必要な場合だけです。

    ドキュメント: [Nodes](/ja-JP/nodes), [Nodes CLI](/cli/nodes), [Multiple gateways](/ja-JP/gateway/multiple-gateways)。

  </Accordion>
</AccordionGroup>

## 環境変数と .env 読み込み

<AccordionGroup>
  <Accordion title="OpenClaw は環境変数をどう読み込みますか？">
    OpenClaw は親プロセス（shell、launchd / systemd、CI など）から env vars を読み込み、さらに次も読み込みます:

    - カレントワーキングディレクトリの `.env`
    - `~/.openclaw/.env`（別名 `$OPENCLAW_STATE_DIR/.env`）のグローバル fallback `.env`

    どちらの `.env` も既存の env vars を上書きしません。

    config でインライン env vars を定義することもできます（process env にない場合のみ適用）:

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

  <Accordion title="サービス経由で Gateway を起動したら env vars が消えました。どうすればよいですか？">
    よくある修正は 2 つあります:

    1. 不足しているキーを `~/.openclaw/.env` に入れる。そうすれば service が shell env を継承しなくても取り込まれます。
    2. shell import を有効にする（便利機能、opt-in）:

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

    これにより login shell を実行し、期待される不足キーだけを取り込みます（決して上書きしません）。env var 相当:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`。

  </Accordion>

  <Accordion title='COPILOT_GITHUB_TOKEN を設定したのに、models status に "Shell env: off." と表示されるのはなぜですか？'>
    `openclaw models status` は **shell env import** が有効かどうかを示しています。"Shell env: off" は、
    env vars がないことを意味する **わけではなく**、OpenClaw が
    login shell を自動読み込みしないことを意味するだけです。

    Gateway を service として動かしている場合（launchd / systemd）、shell
    environment は継承されません。次のいずれかで修正してください:

    1. トークンを `~/.openclaw/.env` に入れる:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. または shell import を有効にする（`env.shellEnv.enabled: true`）。
    3. または config の `env` ブロックに追加する（不足時のみ適用）。

    その後、gateway を再起動して再確認します:

    ```bash
    openclaw models status
    ```

    Copilot トークンは `COPILOT_GITHUB_TOKEN`（また `GH_TOKEN` / `GITHUB_TOKEN`）から読み取られます。
    [/concepts/model-providers](/ja-JP/concepts/model-providers) と [/environment](/ja-JP/help/environment) を参照してください。

  </Accordion>
</AccordionGroup>

## セッションと複数チャット

<AccordionGroup>
  <Accordion title="新しい会話を開始するにはどうすればよいですか？">
    `/new` または `/reset` を単独メッセージで送信してください。[Session management](/ja-JP/concepts/session) を参照してください。
  </Accordion>

  <Accordion title="/new を送らなければセッションは自動でリセットされますか？">
    セッションは `session.idleMinutes` の後に期限切れにできますが、これは **デフォルトでは無効** です（デフォルト **0**）。
    idle expiry を有効にするには正の値に設定してください。有効な場合、アイドル期間の **次の**
    メッセージで、その chat key に新しい session id が開始されます。
    これは transcript を削除するわけではなく、新しい session を開始するだけです。

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="OpenClaw インスタンスのチーム（CEO 1 人と多くの agents のようなもの）を作れますか？">
    はい。**multi-agent routing** と **sub-agents** を通じて可能です。1 人の coordinator
    agent と、独自の workspace とモデルを持つ複数の worker agents を作れます。

    ただし、これは **楽しい実験** として見るのがよいでしょう。トークン消費が大きく、
    1 つの bot をセッション分割して使うより効率が悪いことが多いです。私たちが通常想定しているのは、
    1 つの bot と会話し、並列作業には別セッションを使う形です。その
    bot は必要に応じて sub-agents も spawn できます。

    ドキュメント: [Multi-agent routing](/ja-JP/concepts/multi-agent), [Sub-agents](/ja-JP/tools/subagents), [Agents CLI](/cli/agents)。

  </Accordion>

  <Accordion title="タスク途中でコンテキストが切り詰められたのはなぜですか？ どう防げますか？">
    Session context はモデル window に制限されます。長いチャット、大きな tool output、多数の
    ファイルは compaction や truncation を引き起こすことがあります。

    役立つこと:

    - 現在の状態を要約してファイルに書くようボットに頼む。
    - 長いタスクの前に `/compact` を使い、話題を切り替えるときは `/new` を使う。
    - 重要なコンテキストは workspace に置き、ボットに読み返させる。
    - main chat を小さく保つため、長い作業や並列作業には sub-agents を使う。
    - これが頻発するなら、より大きな context window を持つモデルを選ぶ。

  </Accordion>

  <Accordion title="OpenClaw を完全にリセットしつつ、インストールだけは残すにはどうすればよいですか？">
    reset コマンドを使ってください:

    ```bash
    openclaw reset
    ```

    非対話の完全リセット:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    その後、セットアップを再実行します:

    ```bash
    openclaw onboard --install-daemon
    ```

    注記:

    - 既存設定が見つかった場合、オンボーディングも **Reset** を提示します。[Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。
    - profile（`--profile` / `OPENCLAW_PROFILE`）を使っていた場合は、各 state dir をリセットしてください（デフォルトは `~/.openclaw-<profile>`）。
    - Dev reset: `openclaw gateway --dev --reset`（dev 専用。dev config + credentials + sessions + workspace を消去）。

  </Accordion>

  <Accordion title='「context too large」エラーが出ます。リセットまたは compact するにはどうすればよいですか？'>
    次のいずれかを使ってください:

    - **Compact**（会話は維持しつつ、古いターンを要約する）:

      ```
      /compact
      ```

      または `/compact <instructions>` で要約を誘導します。

    - **Reset**（同じ chat key に対して新しい session ID を作る）:

      ```
      /new
      /reset
      ```

    これが続く場合:

    - **session pruning**（`agents.defaults.contextPruning`）を有効化または調整し、古い tool output を削減する。
    - より大きな context window を持つモデルを使う。

    ドキュメント: [Compaction](/ja-JP/concepts/compaction), [Session pruning](/ja-JP/concepts/session-pruning), [Session management](/ja-JP/concepts/session)。

  </Accordion>

  <Accordion title='「LLM request rejected: messages.content.tool_use.input field required」と表示されるのはなぜですか？'>
    これは provider validation error です。モデルが必要な
    `input` なしで `tool_use` ブロックを出力しました。通常は、session history が古いか壊れていることを意味します（長い thread や tool / schema 変更の後によく起きます）。

    修正: `/new`（単独メッセージ）で新しい session を始めてください。

  </Accordion>

  <Accordion title="なぜ 30 分ごとに heartbeat メッセージが届くのですか？">
    Heartbeat はデフォルトで **30m** ごと（OAuth auth 使用時は **1h** ごと）に実行されます。調整または無効化するには:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // or "0m" to disable
          },
        },
      },
    }
    ```

    `HEARTBEAT.md` が存在しても実質的に空（空行と
    `# Heading` のような markdown headers のみ）の場合、OpenClaw は API 呼び出しを節約するため
    heartbeat 実行をスキップします。
    ファイルが存在しない場合は heartbeat は引き続き実行され、モデルが何をするかを判断します。

    エージェントごとの override は `agents.list[].heartbeat` を使います。ドキュメント: [Heartbeat](/ja-JP/gateway/heartbeat)。

  </Accordion>

  <Accordion title='WhatsApp グループに「bot account」を追加する必要がありますか？'>
    いいえ。OpenClaw は **自分のアカウント** 上で動作するため、そのグループに自分がいれば、OpenClaw もそのグループを見られます。
    デフォルトでは、送信者を許可するまではグループ返信はブロックされます（`groupPolicy: "allowlist"`）。

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

  <Accordion title="WhatsApp グループの JID はどう取得しますか？">
    Option 1（最速）: ログを追跡し、そのグループでテストメッセージを送る:

    ```bash
    openclaw logs --follow --json
    ```

    `@g.us` で終わる `chatId`（または `from`）を探します。例:
    `1234567890-1234567890@g.us`。

    Option 2（すでに設定済み / allowlisted の場合）: config から groups を一覧する:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    ドキュメント: [WhatsApp](/ja-JP/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/log