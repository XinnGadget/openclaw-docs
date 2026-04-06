---
read_when:
    - ローカルインストールの代わりにコンテナ化された Gateway を使いたい
    - Docker フローを検証している
summary: OpenClaw のオプションの Docker ベースセットアップとオンボーディング
title: Docker
x-i18n:
    generated_at: "2026-04-06T03:08:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: d6aa0453340d7683b4954316274ba6dd1aa7c0ce2483e9bd8ae137ff4efd4c3c
    source_path: install/docker.md
    workflow: 15
---

# Docker（オプション）

Docker は **オプション** です。コンテナ化された Gateway を使いたい場合、または Docker フローを検証したい場合にのみ使用してください。

## Docker は自分に合っているか？

- **はい**: 分離された使い捨ての Gateway 環境が欲しい、またはローカルインストールなしで OpenClaw をホスト上で実行したい。
- **いいえ**: 自分のマシン上で実行していて、最速の開発ループが欲しいだけである。代わりに通常のインストールフローを使用してください。
- **サンドボックスに関する注記**: エージェントのサンドボックス化にも Docker を使用しますが、Gateway 全体を Docker で実行する必要は**ありません**。[Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。

## 前提条件

- Docker Desktop（または Docker Engine）+ Docker Compose v2
- イメージビルド用に少なくとも 2 GB の RAM（1 GB ホストでは `pnpm install` が exit 137 で OOM kill されることがあります）
- イメージとログのための十分なディスク容量
- VPS/パブリックホストで実行する場合は、[ネットワーク公開向けのセキュリティ強化](/ja-JP/gateway/security)、特に Docker の `DOCKER-USER` ファイアウォールポリシーを確認してください。

## コンテナ化された Gateway

<Steps>
  <Step title="イメージをビルドする">
    リポジトリルートでセットアップスクリプトを実行します:

    ```bash
    ./scripts/docker/setup.sh
    ```

    これにより Gateway イメージがローカルでビルドされます。代わりにビルド済みイメージを使うには:

    ```bash
    export OPENCLAW_IMAGE="ghcr.io/openclaw/openclaw:latest"
    ./scripts/docker/setup.sh
    ```

    ビルド済みイメージは
    [GitHub Container Registry](https://github.com/openclaw/openclaw/pkgs/container/openclaw)
    で公開されています。
    一般的なタグ: `main`、`latest`、`<version>`（例: `2026.2.26`）。

  </Step>

  <Step title="オンボーディングを完了する">
    セットアップスクリプトは自動的にオンボーディングを実行します。実行内容:

    - プロバイダー API キーの入力を促す
    - Gateway トークンを生成し、`.env` に書き込む
    - Docker Compose 経由で Gateway を起動する

    セットアップ中、起動前のオンボーディングと設定書き込みは
    `openclaw-gateway` を直接通して実行されます。`openclaw-cli` は
    Gateway コンテナがすでに存在した後に実行するコマンド用です。

  </Step>

  <Step title="Control UI を開く">
    ブラウザーで `http://127.0.0.1:18789/` を開き、設定済みの共有シークレットを Settings に貼り付けます。セットアップスクリプトはデフォルトで `.env` にトークンを書き込みます。コンテナ設定をパスワード認証に切り替えた場合は、代わりにそのパスワードを使用してください。

    URL をもう一度確認したい場合:

    ```bash
    docker compose run --rm openclaw-cli dashboard --no-open
    ```

  </Step>

  <Step title="チャンネルを設定する（オプション）">
    CLI コンテナを使ってメッセージングチャンネルを追加します:

    ```bash
    # WhatsApp (QR)
    docker compose run --rm openclaw-cli channels login

    # Telegram
    docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"

    # Discord
    docker compose run --rm openclaw-cli channels add --channel discord --token "<token>"
    ```

    ドキュメント: [WhatsApp](/ja-JP/channels/whatsapp)、[Telegram](/ja-JP/channels/telegram)、[Discord](/ja-JP/channels/discord)

  </Step>
</Steps>

### 手動フロー

セットアップスクリプトを使わず、各ステップを自分で実行したい場合:

```bash
docker build -t openclaw:local -f Dockerfile .
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js onboard --mode local --no-install-daemon
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js config set --batch-json '[{"path":"gateway.mode","value":"local"},{"path":"gateway.bind","value":"lan"},{"path":"gateway.controlUi.allowedOrigins","value":["http://localhost:18789","http://127.0.0.1:18789"]}]'
docker compose up -d openclaw-gateway
```

<Note>
`docker compose` はリポジトリルートから実行してください。`OPENCLAW_EXTRA_MOUNTS`
または `OPENCLAW_HOME_VOLUME` を有効にした場合、セットアップスクリプトは `docker-compose.extra.yml` を書き込みます。`-f docker-compose.yml -f docker-compose.extra.yml` を付けて含めてください。
</Note>

<Note>
`openclaw-cli` は `openclaw-gateway` のネットワーク名前空間を共有するため、起動後のツールです。`docker compose up -d openclaw-gateway` より前は、オンボーディングとセットアップ時の設定書き込みを `openclaw-gateway` 経由で `--no-deps --entrypoint node` を使って実行してください。
</Note>

### 環境変数

セットアップスクリプトは、以下のオプション環境変数を受け付けます:

| 変数 | 用途 |
| ------------------------------ | ---------------------------------------------------------------- |
| `OPENCLAW_IMAGE`               | ローカルビルドの代わりにリモートイメージを使う |
| `OPENCLAW_DOCKER_APT_PACKAGES` | ビルド中に追加の apt パッケージをインストールする（空白区切り） |
| `OPENCLAW_EXTENSIONS`          | ビルド時に extension 依存関係を事前インストールする（空白区切りの名前） |
| `OPENCLAW_EXTRA_MOUNTS`        | 追加のホストバインドマウント（カンマ区切り `source:target[:opts]`） |
| `OPENCLAW_HOME_VOLUME`         | `/home/node` を名前付き Docker ボリュームに永続化する |
| `OPENCLAW_SANDBOX`             | サンドボックスブートストラップをオプトインする（`1`、`true`、`yes`、`on`） |
| `OPENCLAW_DOCKER_SOCKET`       | Docker ソケットパスを上書きする |

### ヘルスチェック

コンテナのプローブエンドポイント（認証不要）:

```bash
curl -fsS http://127.0.0.1:18789/healthz   # liveness
curl -fsS http://127.0.0.1:18789/readyz     # readiness
```

Docker イメージには、`/healthz` を ping する組み込みの `HEALTHCHECK` が含まれています。
チェックが失敗し続けると、Docker はコンテナを `unhealthy` とマークし、
オーケストレーションシステムが再起動または置き換えを行えるようになります。

認証付きの詳細ヘルススナップショット:

```bash
docker compose exec openclaw-gateway node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"
```

### LAN と loopback

`scripts/docker/setup.sh` は、Docker のポート公開でホストから
`http://127.0.0.1:18789` にアクセスできるように、デフォルトで `OPENCLAW_GATEWAY_BIND=lan` を設定します。

- `lan`（デフォルト）: ホストブラウザーとホスト CLI は、公開された Gateway ポートに到達できます。
- `loopback`: コンテナのネットワーク名前空間内のプロセスだけが Gateway に直接到達できます。

<Note>
`gateway.bind` には、ホストエイリアスの `0.0.0.0` や `127.0.0.1` ではなく、bind mode 値（`lan` / `loopback` / `custom` / `tailnet` / `auto`）を使用してください。
</Note>

### ストレージと永続化

Docker Compose は `OPENCLAW_CONFIG_DIR` を `/home/node/.openclaw` に、
`OPENCLAW_WORKSPACE_DIR` を `/home/node/.openclaw/workspace` にバインドマウントするため、これらのパスはコンテナの置き換え後も維持されます。

そのマウントされた設定ディレクトリには、OpenClaw の以下が保存されます:

- 動作設定用の `openclaw.json`
- 保存されたプロバイダー OAuth/API キー認証用の `agents/<agentId>/agent/auth-profiles.json`
- `OPENCLAW_GATEWAY_TOKEN` のような環境変数ベースのランタイムシークレット用の `.env`

VM デプロイでの永続化の詳細については、
[Docker VM Runtime - What persists where](/ja-JP/install/docker-vm-runtime#what-persists-where)
を参照してください。

**ディスク増加のホットスポット:** `media/`、セッション JSONL ファイル、`cron/runs/*.jsonl`、
および `/tmp/openclaw/` 配下のローテートファイルログに注意してください。

### シェルヘルパー（オプション）

日常的な Docker 管理を簡単にするには、`ClawDock` をインストールしてください:

```bash
mkdir -p ~/.clawdock && curl -sL https://raw.githubusercontent.com/openclaw/openclaw/main/scripts/clawdock/clawdock-helpers.sh -o ~/.clawdock/clawdock-helpers.sh
echo 'source ~/.clawdock/clawdock-helpers.sh' >> ~/.zshrc && source ~/.zshrc
```

古い `scripts/shell-helpers/clawdock-helpers.sh` の raw パスから ClawDock をインストールしていた場合は、ローカルのヘルパーファイルが新しい場所を追従するように、上のインストールコマンドを再実行してください。

その後、`clawdock-start`、`clawdock-stop`、`clawdock-dashboard` などを使用できます。すべてのコマンドは `clawdock-help` を実行してください。
完全なヘルパーガイドについては [ClawDock](/ja-JP/install/clawdock) を参照してください。

<AccordionGroup>
  <Accordion title="Docker Gateway 用に agent sandbox を有効にする">
    ```bash
    export OPENCLAW_SANDBOX=1
    ./scripts/docker/setup.sh
    ```

    カスタムソケットパス（例: rootless Docker）:

    ```bash
    export OPENCLAW_SANDBOX=1
    export OPENCLAW_DOCKER_SOCKET=/run/user/1000/docker.sock
    ./scripts/docker/setup.sh
    ```

    スクリプトは、サンドボックスの前提条件を満たした後にのみ `docker.sock` をマウントします。サンドボックスセットアップを完了できない場合、スクリプトは `agents.defaults.sandbox.mode` を `off` に戻します。

  </Accordion>

  <Accordion title="自動化 / CI（非対話）">
    `-T` で Compose の擬似 TTY 割り当てを無効にします:

    ```bash
    docker compose run -T --rm openclaw-cli gateway probe
    docker compose run -T --rm openclaw-cli devices list --json
    ```

  </Accordion>

  <Accordion title="共有ネットワークのセキュリティに関する注記">
    `openclaw-cli` は `network_mode: "service:openclaw-gateway"` を使用するため、CLI コマンドは `127.0.0.1` 経由で Gateway に到達できます。これは共有された信頼境界として扱ってください。compose 設定では、`openclaw-cli` に対して `NET_RAW`/`NET_ADMIN` を削除し、`no-new-privileges` を有効にしています。
  </Accordion>

  <Accordion title="権限と EACCES">
    イメージは `node`（uid 1000）として実行されます。`/home/node/.openclaw` で権限エラーが発生する場合は、ホストのバインドマウントが uid 1000 の所有であることを確認してください:

    ```bash
    sudo chown -R 1000:1000 /path/to/openclaw-config /path/to/openclaw-workspace
    ```

  </Accordion>

  <Accordion title="より高速な再ビルド">
    Dockerfile は依存関係レイヤーがキャッシュされるように順序を工夫してください。これにより、lockfile が変わらない限り `pnpm install` の再実行を避けられます:

    ```dockerfile
    FROM node:24-bookworm
    RUN curl -fsSL https://bun.sh/install | bash
    ENV PATH="/root/.bun/bin:${PATH}"
    RUN corepack enable
    WORKDIR /app
    COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
    COPY ui/package.json ./ui/package.json
    COPY scripts ./scripts
    RUN pnpm install --frozen-lockfile
    COPY . .
    RUN pnpm build
    RUN pnpm ui:install
    RUN pnpm ui:build
    ENV NODE_ENV=production
    CMD ["node","dist/index.js"]
    ```

  </Accordion>

  <Accordion title="上級者向けコンテナオプション">
    デフォルトイメージはセキュリティ優先で、非 root の `node` として実行されます。より多機能なコンテナにするには:

    1. **`/home/node` を永続化する**: `export OPENCLAW_HOME_VOLUME="openclaw_home"`
    2. **システム依存関係を組み込む**: `export OPENCLAW_DOCKER_APT_PACKAGES="git curl jq"`
    3. **Playwright ブラウザーをインストールする**:
       ```bash
       docker compose run --rm openclaw-cli \
         node /app/node_modules/playwright-core/cli.js install chromium
       ```
    4. **ブラウザーダウンロードを永続化する**: `PLAYWRIGHT_BROWSERS_PATH=/home/node/.cache/ms-playwright` を設定し、
       `OPENCLAW_HOME_VOLUME` または `OPENCLAW_EXTRA_MOUNTS` を使用します。

  </Accordion>

  <Accordion title="OpenAI Codex OAuth（ヘッドレス Docker）">
    ウィザードで OpenAI Codex OAuth を選ぶと、ブラウザー URL が開きます。Docker やヘッドレス環境では、遷移先の完全なリダイレクト URL をコピーし、認証を完了するためにウィザードへ貼り戻してください。
  </Accordion>

  <Accordion title="ベースイメージメタデータ">
    メインの Docker イメージは `node:24-bookworm` を使用し、`org.opencontainers.image.base.name`、
    `org.opencontainers.image.source` などを含む OCI ベースイメージアノテーションを公開します。詳しくは
    [OCI image annotations](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
    を参照してください。
  </Accordion>
</AccordionGroup>

### VPS で実行する場合

共有 VM デプロイ手順（バイナリの焼き込み、永続化、更新を含む）については、
[Hetzner (Docker VPS)](/ja-JP/install/hetzner) と
[Docker VM Runtime](/ja-JP/install/docker-vm-runtime) を参照してください。

## Agent Sandbox

`agents.defaults.sandbox` を有効にすると、Gateway 自体はホストに残したまま、Gateway はエージェントのツール実行（シェル、ファイル読み書きなど）を分離された Docker コンテナ内で実行します。これにより、信頼できない、またはマルチテナントのエージェントセッションに対して、Gateway 全体をコンテナ化することなく強固な分離を提供できます。

サンドボックスのスコープは、エージェント単位（デフォルト）、セッション単位、または共有にできます。各スコープには、それぞれ独自のワークスペースが `/workspace` にマウントされます。ツールの allow/deny policy、ネットワーク分離、リソース制限、ブラウザーコンテナも設定できます。

完全な設定、イメージ、セキュリティに関する注記、マルチエージェントプロファイルについては、以下を参照してください。

- [Sandboxing](/ja-JP/gateway/sandboxing) -- サンドボックスの完全なリファレンス
- [OpenShell](/ja-JP/gateway/openshell) -- サンドボックスコンテナへの対話型シェルアクセス
- [Multi-Agent Sandbox and Tools](/ja-JP/tools/multi-agent-sandbox-tools) -- エージェント単位の上書き

### クイック有効化

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        scope: "agent", // session | agent | shared
      },
    },
  },
}
```

デフォルトのサンドボックスイメージをビルドする:

```bash
scripts/sandbox-setup.sh
```

## トラブルシューティング

<AccordionGroup>
  <Accordion title="イメージがない、または sandbox コンテナが起動しない">
    [`scripts/sandbox-setup.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/sandbox-setup.sh)
    でサンドボックスイメージをビルドするか、
    `agents.defaults.sandbox.docker.image` にカスタムイメージを設定してください。
    コンテナはセッションごとに必要に応じて自動作成されます。
  </Accordion>

  <Accordion title="sandbox 内で権限エラーが出る">
    `docker.user` をマウントされたワークスペース所有権に一致する UID:GID に設定するか、
    ワークスペースフォルダーを chown してください。
  </Accordion>

  <Accordion title="sandbox 内でカスタムツールが見つからない">
    OpenClaw は `sh -lc`（ログインシェル）でコマンドを実行するため、
    `/etc/profile` を読み込み、PATH をリセットすることがあります。
    カスタムツールのパスを先頭に追加するよう `docker.env.PATH` を設定するか、
    Dockerfile の `/etc/profile.d/` 配下にスクリプトを追加してください。
  </Accordion>

  <Accordion title="イメージビルド中に OOM kill される（exit 137）">
    VM には少なくとも 2 GB の RAM が必要です。より大きなマシンクラスを使用して再試行してください。
  </Accordion>

  <Accordion title="Control UI で Unauthorized または pairing required が表示される">
    新しいダッシュボードリンクを取得し、ブラウザーデバイスを承認してください:

    ```bash
    docker compose run --rm openclaw-cli dashboard --no-open
    docker compose run --rm openclaw-cli devices list
    docker compose run --rm openclaw-cli devices approve <requestId>
    ```

    詳細: [Dashboard](/web/dashboard)、[Devices](/cli/devices)。

  </Accordion>

  <Accordion title="Gateway ターゲットが ws://172.x.x.x と表示される、または Docker CLI から pairing エラーが出る">
    Gateway モードと bind をリセットしてください:

    ```bash
    docker compose run --rm openclaw-cli config set --batch-json '[{"path":"gateway.mode","value":"local"},{"path":"gateway.bind","value":"lan"}]'
    docker compose run --rm openclaw-cli devices list --url ws://127.0.0.1:18789
    ```

  </Accordion>
</AccordionGroup>

## 関連

- [インストール概要](/ja-JP/install) — すべてのインストール方法
- [Podman](/ja-JP/install/podman) — Docker の代替となる Podman
- [ClawDock](/ja-JP/install/clawdock) — Docker Compose のコミュニティセットアップ
- [Updating](/ja-JP/install/updating) — OpenClaw を最新に保つ
- [Configuration](/ja-JP/gateway/configuration) — インストール後の Gateway 設定
