---
read_when:
    - ローカルまたはCIでテストを実行している
    - モデル/プロバイダーのバグに対する回帰テストを追加している
    - gateway + agent の動作をデバッグしている
summary: 'テストキット: unit/e2e/liveスイート、Dockerランナー、それぞれのテストがカバーする内容'
title: Testing
x-i18n:
    generated_at: "2026-04-06T03:10:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfa174e565df5fdf957234b7909beaf1304aa026e731cc2c433ca7d931681b56
    source_path: help/testing.md
    workflow: 15
---

# Testing

OpenClaw には、3つのVitestスイート（unit/integration、e2e、live）と少数のDockerランナーがあります。

このドキュメントは「どのようにテストしているか」のガイドです。

- 各スイートが何をカバーするか（そして意図的に_カバーしない_もの）
- 一般的なワークフロー（ローカル、push前、デバッグ）でどのコマンドを実行するか
- liveテストがどのように認証情報を検出し、モデル/プロバイダーを選択するか
- 実際のモデル/プロバイダー問題に対する回帰テストをどう追加するか

## クイックスタート

ほとんどの日は次で十分です。

- フルゲート（push前に想定）: `pnpm build && pnpm check && pnpm test`
- 余裕のあるマシンでのより高速なローカル全スイート実行: `pnpm test:max`
- 直接のVitest watchループ（現代的なprojects設定）: `pnpm test:watch`
- 直接ファイル指定は拡張機能/チャネルのパスも対象になりました: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`

テストに触れたとき、または追加の確信が欲しいとき:

- カバレッジゲート: `pnpm test:coverage`
- E2Eスイート: `pnpm test:e2e`

実際のプロバイダー/モデルをデバッグするとき（実際の認証情報が必要）:

- liveスイート（モデル + gateway のツール/画像プローブ）: `pnpm test:live`
- 1つのliveファイルだけを静かに対象指定: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

ヒント: 失敗している1ケースだけが必要な場合は、以下で説明する allowlist 環境変数でliveテストを絞り込むことを優先してください。

## テストスイート（何がどこで実行されるか）

スイートは「現実性が増すほど、flakiness とコストも増える」と考えてください。

### Unit / integration（デフォルト）

- コマンド: `pnpm test`
- 設定: `vitest.config.ts` 経由のネイティブVitest `projects`
- ファイル: `src/**/*.test.ts`、`packages/**/*.test.ts`、`test/**/*.test.ts` 配下のコア/unitインベントリと、`vitest.unit.config.ts` でカバーされる許可済みの `ui` node テスト
- 対象範囲:
  - 純粋なunitテスト
  - インプロセスのintegrationテスト（gateway認証、ルーティング、tooling、パース、設定）
  - 既知バグに対する決定論的回帰テスト
- 期待される性質:
  - CIで実行される
  - 実際のキーは不要
  - 高速かつ安定しているべき
- Projectsに関する注記:
  - `pnpm test`、`pnpm test:watch`、`pnpm test:changed` はすべて、同じネイティブVitestルート `projects` 設定を使うようになりました。
  - 直接ファイルフィルターはルートのプロジェクトグラフをネイティブにたどるため、`pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` はカスタムラッパーなしで動作します。
- Embedded runnerに関する注記:
  - メッセージツール検出入力または compaction ランタイムコンテキストを変更するときは、
    両レベルのカバレッジを維持してください。
  - 純粋なルーティング/正規化境界に対して、焦点を絞ったヘルパー回帰テストを追加してください。
  - さらに、embedded runner のintegrationスイートも健全に保ってください:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`、
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`、および
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`。
  - これらのスイートは、スコープ付きIDと compaction の動作が
    実際の `run.ts` / `compact.ts` の経路を通って流れ続けることを検証します。ヘルパーのみのテストは、
    これらのintegration経路の十分な代替にはなりません。
- Poolに関する注記:
  - ベースのVitest設定は現在 `threads` をデフォルトにしています。
  - 共有Vitest設定では `isolate: false` も固定され、ルートprojects、e2e、live設定全体で非分離ランナーを使用します。
  - ルートUIレーンは `jsdom` セットアップと optimizer を維持しますが、現在は共有の非分離ランナーでも動作します。
  - `pnpm test` は、ルート `vitest.config.ts` の projects 設定から同じ `threads` + `isolate: false` のデフォルトを継承します。
  - 共有の `scripts/run-vitest.mjs` ランチャーは、Vitest 子Nodeプロセスに対してデフォルトで `--no-maglev` も追加するようになり、大規模なローカル実行時のV8コンパイルの揺れを減らします。標準のV8動作と比較したい場合は `OPENCLAW_VITEST_ENABLE_MAGLEV=1` を設定してください。
- 高速ローカル反復に関する注記:
  - `pnpm test:changed` は、ネイティブprojects設定を `--changed origin/main` とともに実行します。
  - `pnpm test:max` と `pnpm test:changed:max` は、同じネイティブprojects設定を維持しつつ、worker上限だけを高くします。
  - ローカルworkerの自動スケーリングは現在意図的に保守的で、ホストの負荷平均がすでに高いときにも抑制されるため、複数のVitest実行を同時に走らせてもデフォルトで被害が少なくなります。
  - ベースのVitest設定では、プロジェクト/設定ファイルを `forceRerunTriggers` としてマークしているため、テスト配線が変わったときでも changed-mode の再実行が正しく保たれます。
  - この設定は、対応ホストでは `OPENCLAW_VITEST_FS_MODULE_CACHE` を有効のままにします。直接プロファイリング用に明示的なキャッシュ場所を1つ指定したい場合は `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` を設定してください。
- Perf-debugに関する注記:
  - `pnpm test:perf:imports` は、Vitest の import-duration レポートと import-breakdown 出力を有効にします。
  - `pnpm test:perf:imports:changed` は、同じプロファイリング表示を `origin/main` 以降に変更されたファイルへ絞り込みます。
  - `pnpm test:perf:profile:main` は、Vitest/Vite の起動と transform オーバーヘッドに対するメインスレッドCPUプロファイルを書き出します。
  - `pnpm test:perf:profile:runner` は、ファイル並列を無効化したunitスイート向けに、runner のCPU+heapプロファイルを書き出します。

### E2E（gatewayスモーク）

- コマンド: `pnpm test:e2e`
- 設定: `vitest.e2e.config.ts`
- ファイル: `src/**/*.e2e.test.ts`、`test/**/*.e2e.test.ts`
- ランタイムのデフォルト:
  - リポジトリの他と同様に、Vitest `threads` と `isolate: false` を使用します。
  - 適応型workerを使用します（CI: 最大2、ローカル: デフォルト1）。
  - コンソールI/Oオーバーヘッドを減らすため、デフォルトでsilentモードで実行されます。
- 便利なオーバーライド:
  - `OPENCLAW_E2E_WORKERS=<n>` でworker数を強制指定（上限16）。
  - `OPENCLAW_E2E_VERBOSE=1` で詳細なコンソール出力を再有効化。
- 対象範囲:
  - 複数インスタンスのgateway end-to-end 動作
  - WebSocket/HTTPサーフェス、ノードペアリング、より重いネットワーキング
- 期待される性質:
  - CIで実行される（パイプラインで有効な場合）
  - 実際のキーは不要
  - unitテストより可動部が多い（遅くなることがある）

### E2E: OpenShellバックエンドスモーク

- コマンド: `pnpm test:e2e:openshell`
- ファイル: `test/openshell-sandbox.e2e.test.ts`
- 対象範囲:
  - Docker経由でホスト上に分離されたOpenShell gatewayを起動
  - 一時的なローカルDockerfileからsandboxを作成
  - 実際の `sandbox ssh-config` + SSH exec を介して、OpenClaw の OpenShell バックエンドを実行
  - sandbox fs bridge を通じてリモート正準のファイルシステム動作を検証
- 期待される性質:
  - オプトイン専用。デフォルトの `pnpm test:e2e` 実行には含まれない
  - ローカルの `openshell` CLI と動作中のDocker daemon が必要
  - 分離された `HOME` / `XDG_CONFIG_HOME` を使用し、その後テスト用gatewayとsandboxを破棄
- 便利なオーバーライド:
  - `OPENCLAW_E2E_OPENSHELL=1` で、広いe2eスイートを手動実行するときにこのテストを有効化
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell` で、デフォルト以外のCLIバイナリまたはラッパースクリプトを指定

### Live（実際のプロバイダー + 実際のモデル）

- コマンド: `pnpm test:live`
- 設定: `vitest.live.config.ts`
- ファイル: `src/**/*.live.test.ts`
- デフォルト: `pnpm test:live` により**有効**（`OPENCLAW_LIVE_TEST=1` を設定）
- 対象範囲:
  - 「このプロバイダー/モデルは、今日、実際の認証情報で本当に動くか？」
  - プロバイダーの形式変更、tool-calling の癖、認証問題、レート制限の挙動を捕捉
- 期待される性質:
  - 設計上CIで安定しない（実ネットワーク、実プロバイダーポリシー、クォータ、障害）
  - 費用がかかる / レート制限を消費する
  - 「全部」を回すより、絞った部分集合の実行を推奨
- live実行では、不足するAPIキーを拾うために `~/.profile` を読み込みます。
- デフォルトでは、live実行は引き続き `HOME` を分離し、設定/認証情報素材を一時的なテスト用 home にコピーするため、unitフィクスチャが実際の `~/.openclaw` を変更することはありません。
- liveテストに実際の home ディレクトリを使わせる必要が意図的にある場合のみ、`OPENCLAW_LIVE_USE_REAL_HOME=1` を設定してください。
- `pnpm test:live` は現在、より静かなモードがデフォルトです。`[live] ...` の進捗出力は維持されますが、追加の `~/.profile` 通知を抑制し、gateway bootstrap ログ/Bonjour の雑音をミュートします。完全な起動ログを戻したい場合は `OPENCLAW_LIVE_TEST_QUIET=0` を設定してください。
- APIキーローテーション（プロバイダー固有）: `*_API_KEYS` をカンマ/セミコロン形式、または `*_API_KEY_1`、`*_API_KEY_2` 形式で設定します（例: `OPENAI_API_KEYS`、`ANTHROPIC_API_KEYS`、`GEMINI_API_KEYS`）。または live専用オーバーライドとして `OPENCLAW_LIVE_*_KEY` を使います。テストはレート制限応答時に再試行します。
- 進捗/heartbeat出力:
  - liveスイートは現在、進捗行を stderr に出力するため、Vitest のコンソールキャプチャが静かな場合でも、長いプロバイダー呼び出しが動作中であることが視認できます。
  - `vitest.live.config.ts` は Vitest のコンソールインターセプトを無効にしているため、プロバイダー/gateway の進捗行が live実行中に即時ストリーミングされます。
  - 直接モデルの heartbeat は `OPENCLAW_LIVE_HEARTBEAT_MS` で調整します。
  - gateway/probe の heartbeat は `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` で調整します。

## どのスイートを実行すべきか？

この判断表を使ってください。

- ロジック/テストを編集した: `pnpm test` を実行（大きく変更したなら `pnpm test:coverage` も）
- gateway のネットワーキング / WSプロトコル / ペアリングに触れた: `pnpm test:e2e` を追加
- 「botが落ちている」/ プロバイダー固有の失敗 / tool calling をデバッグしたい: 絞り込んだ `pnpm test:live` を実行

## Live: Androidノード機能スイープ

- テスト: `src/gateway/android-node.capabilities.live.test.ts`
- スクリプト: `pnpm android:test:integration`
- 目標: 接続済みのAndroidノードが**現在広告しているすべてのコマンド**を呼び出し、コマンド契約動作を検証する。
- 対象範囲:
  - 前提条件付き / 手動セットアップ（このスイートはアプリのインストール/実行/ペアリングは行わない）。
  - 選択されたAndroidノードに対する、コマンドごとの gateway `node.invoke` 検証。
- 必須の事前セットアップ:
  - Androidアプリがすでにgatewayへ接続・ペアリング済みであること。
  - アプリをフォアグラウンドで維持すること。
  - 通過させたい機能に対して、権限/キャプチャ同意が付与されていること。
- 任意のターゲットオーバーライド:
  - `OPENCLAW_ANDROID_NODE_ID` または `OPENCLAW_ANDROID_NODE_NAME`。
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`。
- 完全なAndroidセットアップの詳細: [Android App](/ja-JP/platforms/android)

## Live: モデルスモーク（プロファイルキー）

liveテストは、失敗を切り分けられるよう2層に分かれています。

- 「Direct model」は、そのプロバイダー/モデルが指定キーでそもそも応答できるかを示します。
- 「Gateway smoke」は、そのモデルに対して gateway+agent の全パイプラインが機能するか（sessions、history、tools、sandbox policy など）を示します。

### レイヤー1: 直接モデル補完（gatewayなし）

- テスト: `src/agents/models.profiles.live.test.ts`
- 目標:
  - 発見されたモデルを列挙
  - `getApiKeyForModel` を使って、認証情報を持つモデルを選択
  - モデルごとに小さな補完を1回実行（必要に応じて対象を絞った回帰も）
- 有効化方法:
  - `pnpm test:live`（または Vitest を直接呼ぶなら `OPENCLAW_LIVE_TEST=1`）
- このスイートを実際に実行するには `OPENCLAW_LIVE_MODELS=modern`（または modern の別名である `all`）を設定します。そうしないと、`pnpm test:live` の焦点を gateway smoke に保つためスキップされます。
- モデルの選択方法:
  - `OPENCLAW_LIVE_MODELS=modern` で modern allowlist を実行（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_MODELS=all` は modern allowlist の別名
  - または `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."`（カンマ区切りallowlist）
- プロバイダーの選択方法:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity"`（カンマ区切りallowlist）
- キーの取得元:
  - デフォルト: profile store と env フォールバック
  - **profile store のみ**を強制するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` を設定
- これが存在する理由:
  - 「provider API が壊れている / キーが無効」と「gateway agent pipeline が壊れている」を分離する
  - 小さく分離された回帰を含める（例: OpenAI Responses/Codex Responses の reasoning replay + tool-call フロー）

### レイヤー2: Gateway + dev agent スモーク（`@openclaw` が実際に行うこと）

- テスト: `src/gateway/gateway-models.profiles.live.test.ts`
- 目標:
  - インプロセスgatewayを起動
  - `agent:dev:*` セッションを作成/パッチ適用（実行ごとにモデルをオーバーライド）
  - キーのあるモデル群を反復し、次を検証:
    - 「意味のある」応答（toolsなし）
    - 実際のツール呼び出しが動作すること（read probe）
    - 任意の追加ツールプローブ（exec+read probe）
    - OpenAIの回帰経路（tool-call-only → フォローアップ）が動作し続けること
- プローブの詳細（失敗をすばやく説明できるように）:
  - `read` probe: テストはワークスペースに nonce ファイルを書き込み、agent にそれを `read` して nonce を返答するよう依頼します。
  - `exec+read` probe: テストは agent に、nonce を一時ファイルへ `exec` で書き込み、その後 `read` で読み戻すよう依頼します。
  - image probe: テストは生成したPNG（猫 + ランダムコード）を添付し、モデルが `cat <CODE>` を返すことを期待します。
  - 実装参照: `src/gateway/gateway-models.profiles.live.test.ts` および `src/gateway/live-image-probe.ts`。
- 有効化方法:
  - `pnpm test:live`（または Vitest を直接呼ぶなら `OPENCLAW_LIVE_TEST=1`）
- モデルの選択方法:
  - デフォルト: modern allowlist（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` は modern allowlist の別名
  - または `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（またはカンマ区切りリスト）で絞り込み
- プロバイダーの選択方法（「OpenRouter全部」を避ける）:
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,openai,anthropic,zai,minimax"`（カンマ区切りallowlist）
- ツール + 画像プローブは、このliveテストでは常に有効です:
  - `read` probe + `exec+read` probe（ツール負荷）
  - モデルが画像入力サポートを広告している場合、image probe を実行
  - フロー（高レベル）:
    - テストは「CAT」+ ランダムコードを含む小さなPNGを生成します（`src/gateway/live-image-probe.ts`）
    - それを `agent` の `attachments: [{ mimeType: "image/png", content: "<base64>" }]` 経由で送信します
    - Gateway は添付を `images[]` にパースします（`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`）
    - Embedded agent はマルチモーダルなユーザーメッセージをモデルへ転送します
    - アサーション: 返信に `cat` + そのコードが含まれること（OCR許容: 軽微な誤りは許可）

ヒント: 自分のマシンで何をテストできるか（および正確な `provider/model` ID）を見るには、次を実行してください。

```bash
openclaw models list
openclaw models list --json
```

## Live: ACP bind スモーク（`/acp spawn ... --bind here`）

- テスト: `src/gateway/gateway-acp-bind.live.test.ts`
- 目標: live ACP agent を使った実際のACP会話bindフローを検証する:
  - `/acp spawn <agent> --bind here` を送る
  - 合成メッセージチャネルの会話コンテキストをその場で bind する
  - 同じ会話で通常のフォローアップを送る
  - そのフォローアップが bind されたACPセッションのトランスクリプトへ届くことを検証する
- 有効化:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- デフォルト:
  - ACP agent: `claude`
  - 合成チャネル: Slack DM風の会話コンテキスト
  - ACPバックエンド: `acpx`
- オーバーライド:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- 注記:
  - このレーンは、admin専用の合成 originating-route フィールド付きの gateway `chat.send` サーフェスを使うため、外部配信を装わずにテストがメッセージチャネルコンテキストを付与できます。
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` が未設定の場合、テストは選択されたACP harness agent に対して、埋め込みの `acpx` plugin が持つ組み込みagent registryを使用します。

例:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Dockerレシピ:

```bash
pnpm test:docker:live-acp-bind
```

Dockerに関する注記:

- Dockerランナーは `scripts/test-live-acp-bind-docker.sh` にあります。
- `~/.profile` を読み込み、一致するCLI認証素材をコンテナへステージし、書き込み可能なnpm prefix に `acpx` をインストールし、その後、要求されたlive CLI（`@anthropic-ai/claude-code` または `@openai/codex`）がなければインストールします。
- Docker内部では、ランナーは `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` を設定するため、acpx は読み込まれたprofile由来のプロバイダーenv vars を子harness CLI に対して利用可能なまま維持します。

### 推奨liveレシピ

狭く明示的なallowlistが最速で、flakiness も最小です。

- 単一モデル、direct（gatewayなし）:
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- 単一モデル、gateway smoke:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 複数プロバイダーにまたがる tool calling:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Googleに集中（Gemini APIキー + Antigravity）:
  - Gemini（APIキー）: `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity（OAuth）: `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

注記:

- `google/...` は Gemini API（APIキー）を使用します。
- `google-antigravity/...` は Antigravity OAuth bridge（Cloud Code Assist風のagent endpoint）を使用します。

## Live: モデルマトリクス（何をカバーするか）

固定の「CIモデル一覧」はありません（liveはオプトイン）が、これらはキーのある開発マシンで定期的にカバーすることを**推奨する**モデルです。

### Modernスモークセット（tool calling + image）

これは、動作し続けることを期待する「一般的なモデル」実行です。

- OpenAI（非Codex）: `openai/gpt-5.4`（任意: `openai/gpt-5.4-mini`）
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6`（または `anthropic/claude-sonnet-4-6`）
- Google（Gemini API）: `google/gemini-3.1-pro-preview` および `google/gemini-3-flash-preview`（古い Gemini 2.x モデルは避ける）
- Google（Antigravity）: `google-antigravity/claude-opus-4-6-thinking` および `google-antigravity/gemini-3-flash`
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

tools + image 付きでgateway smokeを実行:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### ベースライン: tool calling（Read + 任意のExec）

プロバイダーファミリーごとに少なくとも1つを選びます。

- OpenAI: `openai/gpt-5.4`（または `openai/gpt-5.4-mini`）
- Anthropic: `anthropic/claude-opus-4-6`（または `anthropic/claude-sonnet-4-6`）
- Google: `google/gemini-3-flash-preview`（または `google/gemini-3.1-pro-preview`）
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

追加の任意カバレッジ（あれば望ましい）:

- xAI: `xai/grok-4`（または利用可能な最新）
- Mistral: `mistral/`…（有効化されている「tools」対応モデルを1つ選ぶ）
- Cerebras: `cerebras/`…（アクセスがある場合）
- LM Studio: `lmstudio/`…（ローカル。tool calling はAPIモードに依存）

### Vision: 画像送信（添付 → マルチモーダルメッセージ）

少なくとも1つ、画像対応モデルを `OPENCLAW_LIVE_GATEWAY_MODELS` に含めて、image probe を実行してください（Claude/Gemini/OpenAI の画像対応バリアントなど）。

### Aggregators / 代替gateway

キーが有効であれば、次を介したテストもサポートしています。

- OpenRouter: `openrouter/...`（数百のモデル。tools+image 対応候補の発見には `openclaw models scan` を使ってください）
- OpenCode: Zen 用に `opencode/...`、Go 用に `opencode-go/...`（認証は `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`）

liveマトリクスに含められる他のプロバイダー（認証情報/設定がある場合）:

- 組み込み: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- `models.providers` 経由（カスタムエンドポイント）: `minimax`（cloud/API）、および任意の OpenAI/Anthropic 互換プロキシ（LM Studio、vLLM、LiteLLM など）

ヒント: ドキュメントに「全モデル」をハードコードしようとしないでください。権威ある一覧は、そのマシン上で `discoverModels(...)` が返すものと、利用可能なキーがあるものです。

## 認証情報（絶対にコミットしない）

liveテストは、CLI と同じ方法で認証情報を検出します。実際上の意味は次のとおりです。

- CLI が動くなら、liveテストも同じキーを見つけられるはずです。
- liveテストで「認証情報なし」と言われたら、`openclaw models list` / モデル選択をデバッグするときと同じように調べてください。

- エージェント単位の認証プロファイル: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（liveテストでいう「プロファイルキー」とはこれです）
- 設定: `~/.openclaw/openclaw.json`（または `OPENCLAW_CONFIG_PATH`）
- 旧式のstate dir: `~/.openclaw/credentials/`（存在する場合はステージされたlive用homeへコピーされますが、メインのプロファイルキーストアではありません）
- ローカルのlive実行は、デフォルトでアクティブな設定、エージェント単位の `auth-profiles.json` ファイル、旧式の `credentials/`、サポートされる外部CLI認証ディレクトリを一時的なテスト用homeへコピーします。このステージされた設定では `agents.*.workspace` / `agentDir` のパスオーバーライドが削除されるため、プローブが実際のホストワークスペースへ出ないようになっています。

envキー（例: `~/.profile` で export されたもの）に依存したい場合は、`source ~/.profile` の後にローカルテストを実行するか、以下のDockerランナーを使ってください（これらは `~/.profile` をコンテナへマウントできます）。

## Deepgram live（音声文字起こし）

- テスト: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- 有効化: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- テスト: `src/agents/byteplus.live.test.ts`
- 有効化: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- 任意のモデルオーバーライド: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media live

- テスト: `extensions/comfy/comfy.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- 対象範囲:
  - バンドルされた comfy 画像、動画、`music_generate` 経路を実行
  - `models.providers.comfy.<capability>` が設定されていない限り、各機能をスキップ
  - comfy workflow の送信、ポーリング、ダウンロード、または plugin 登録を変更した後に有用

## 画像生成 live

- テスト: `src/image-generation/runtime.live.test.ts`
- コマンド: `pnpm test:live src/image-generation/runtime.live.test.ts`
- 対象範囲:
  - 登録済みのすべての画像生成プロバイダーpluginを列挙
  - プローブ前に、ログインシェル（`~/.profile`）から不足しているプロバイダーenv vars を読み込む
  - デフォルトでは、保存済み認証プロファイルより先に live/env APIキーを使用するため、`auth-profiles.json` 内の古いテストキーが実際のシェル認証情報を隠すことはない
  - 利用可能な認証/プロファイル/モデルがないプロバイダーはスキップ
  - 共有ランタイム機能を通して、標準の画像生成バリアントを実行:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- 現在カバーされているバンドル済みプロバイダー:
  - `openai`
  - `google`
- 任意の絞り込み:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- 任意の認証挙動:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` で、profile-store 認証を強制し env-only オーバーライドを無視

## 音楽生成 live

- テスト: `extensions/music-generation-providers.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- 対象範囲:
  - 共有されたバンドル済み音楽生成プロバイダー経路を実行
  - 現在は Google と MiniMax をカバー
  - プローブ前に、ログインシェル（`~/.profile`）からプロバイダーenv vars を読み込む
  - 利用可能な認証/プロファイル/モデルがないプロバイダーはスキップ
- 任意の絞り込み:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`

## Dockerランナー（任意の「Linuxで動く」チェック）

これらのDockerランナーは2つのカテゴリに分かれます。

- live-model ランナー: `test:docker:live-models` と `test:docker:live-gateway` は、対応するプロファイルキーliveファイルだけをリポジトリのDockerイメージ内で実行します（`src/agents/models.profiles.live.test.ts` と `src/gateway/gateway-models.profiles.live.test.ts`）。ローカル設定ディレクトリとワークスペースをマウントし（マウントされていれば `~/.profile` も読み込みます）。対応するローカルエントリポイントは `test:live:models-profiles` と `test:live:gateway-profiles` です。
- Docker liveランナーは、完全なDockerスイープが現実的であるよう、より小さなスモーク上限をデフォルトにしています:
  `test:docker:live-models` はデフォルトで `OPENCLAW_LIVE_MAX_MODELS=12`、
  `test:docker:live-gateway` はデフォルトで `OPENCLAW_LIVE_GATEWAY_SMOKE=1`、
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`、
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`、および
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000` を使用します。より大きな網羅的スキャンを明示的に行いたい場合は、
  これらのenv vars を上書きしてください。
- `test:docker:all` は、まず `test:docker:live-build` でlive Dockerイメージを1回ビルドし、その後2つのlive Dockerレーンで再利用します。
- コンテナスモークランナー: `test:docker:openwebui`、`test:docker:onboard`、`test:docker:gateway-network`、`test:docker:mcp-channels`、`test:docker:plugins` は、1つ以上の実コンテナを起動し、より高レベルのintegration経路を検証します。

live-model Dockerランナーはまた、必要なCLI認証homeだけを bind-mount し（または実行が絞り込まれていない場合はサポートされるものをすべて）、実行前にそれらをコンテナhomeへコピーすることで、外部CLI OAuth がホスト認証ストアを変更せずにトークン更新できるようにしています。

- Direct models: `pnpm test:docker:live-models`（スクリプト: `scripts/test-live-models-docker.sh`）
- ACP bind スモーク: `pnpm test:docker:live-acp-bind`（スクリプト: `scripts/test-live-acp-bind-docker.sh`）
- Gateway + dev agent: `pnpm test:docker:live-gateway`（スクリプト: `scripts/test-live-gateway-models-docker.sh`）
- Open WebUI liveスモーク: `pnpm test:docker:openwebui`（スクリプト: `scripts/e2e/openwebui-docker.sh`）
- オンボーディングウィザード（TTY、完全な足場作成）: `pnpm test:docker:onboard`（スクリプト: `scripts/e2e/onboard-docker.sh`）
- Gatewayネットワーキング（2コンテナ、WS認証 + health）: `pnpm test:docker:gateway-network`（スクリプト: `scripts/e2e/gateway-network-docker.sh`）
- MCPチャネルbridge（シード済みGateway + stdio bridge + 生のClaude通知フレームスモーク）: `pnpm test:docker:mcp-channels`（スクリプト: `scripts/e2e/mcp-channels-docker.sh`）
- Plugins（installスモーク + `/plugin` エイリアス + Claude-bundle 再起動セマンティクス）: `pnpm test:docker:plugins`（スクリプト: `scripts/e2e/plugins-docker.sh`）

live-model Dockerランナーは、現在のcheckoutを読み取り専用で bind-mount し、
コンテナ内の一時 workdir にステージもします。これにより、ランタイム
イメージをスリムに保ちつつ、正確にローカルのソース/設定に対して Vitest を実行できます。
ステージ処理では `.pnpm-store`、`.worktrees`、`__openclaw_vitest__`、
アプリローカルの `.build` や Gradle 出力ディレクトリなどの大きなローカル専用キャッシュやアプリビルド出力を除外するため、Docker live実行で
マシン固有の成果物コピーに何分も費やすことはありません。
また、`OPENCLAW_SKIP_CHANNELS=1` も設定するため、gateway liveプローブ時に
実際の Telegram/Discord などのチャネルworkerをコンテナ内で起動しません。
`test:docker:live-models` は引き続き `pnpm test:live` を実行するため、
そのDockerレーンで gateway liveカバレッジを絞り込みまたは除外する必要がある場合は
`OPENCLAW_LIVE_GATEWAY_*` も渡してください。
`test:docker:openwebui` は、より高レベルの互換性スモークです。OpenAI互換HTTPエンドポイントを有効化した
OpenClaw gateway コンテナを起動し、そのgatewayに対して固定された Open WebUI コンテナを起動し、
Open WebUI 経由でサインインし、`/api/models` が `openclaw/default` を公開していることを確認し、
その後 Open WebUI の `/api/chat/completions` プロキシ経由で実際のチャット要求を送信します。
初回実行は、Docker が
Open WebUI イメージを pull する必要があったり、Open WebUI 自体のコールドスタート設定完了を待つ必要があったりするため、かなり遅くなることがあります。
このレーンは利用可能なliveモデルキーを期待し、Docker化された実行では
`OPENCLAW_PROFILE_FILE`（デフォルトは `~/.profile`）がそれを提供する主な手段です。
成功した実行では `{ "ok": true, "model":
"openclaw/default", ... }` のような小さなJSONペイロードが出力されます。
`test:docker:mcp-channels` は意図的に決定論的であり、実際の
Telegram、Discord、または iMessage アカウントを必要としません。シード済みGateway
コンテナを起動し、次に `openclaw mcp serve` を起動する第2のコンテナを開始し、
ルーティングされた会話検出、トランスクリプト読み取り、添付メタデータ、
liveイベントキューの挙動、送信ルーティング、Claude風のチャネル +
権限通知を、実際の stdio MCP bridge 上で検証します。通知チェックは
生の stdio MCP フレームを直接検査するため、このスモークは特定のクライアントSDKがたまたま露出するものだけでなく、
bridge が実際に何を出力するかを検証します。

手動ACP平文スレッドスモーク（CIではない）:

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- このスクリプトは回帰/デバッグワークフロー用に維持してください。ACPスレッドルーティング検証のために再び必要になる可能性があるため、削除しないでください。

便利なenv vars:

- `OPENCLAW_CONFIG_DIR=...`（デフォルト: `~/.openclaw`）を `/home/node/.openclaw` にマウント
- `OPENCLAW_WORKSPACE_DIR=...`（デフォルト: `~/.openclaw/workspace`）を `/home/node/.openclaw/workspace` にマウント
- `OPENCLAW_PROFILE_FILE=...`（デフォルト: `~/.profile`）を `/home/node/.profile` にマウントし、テスト実行前に読み込む
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...`（デフォルト: `~/.cache/openclaw/docker-cli-tools`）を `/home/node/.npm-global` にマウントし、Docker内CLIインストールのキャッシュに使う
- `$HOME` 配下の外部CLI認証ディレクトリ/ファイルは `/host-auth...` 配下に読み取り専用でマウントされ、その後テスト開始前に `/home/node/...` へコピーされます
  - デフォルトディレクトリ: `.minimax`
  - デフォルトファイル: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - 絞り込まれたプロバイダー実行では、`OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` から推定された必要なディレクトリ/ファイルのみをマウント
  - 手動上書きは `OPENCLAW_DOCKER_AUTH_DIRS=all`、`OPENCLAW_DOCKER_AUTH_DIRS=none`、または `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex` のようなカンマ区切りリストで可能
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` で実行を絞り込み
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` でコンテナ内のプロバイダーをフィルタ
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` で、認証情報が profile store 由来であることを保証（env由来ではない）
- `OPENCLAW_OPENWEBUI_MODEL=...` で、Open WebUI スモーク向けにgatewayが公開するモデルを選択
- `OPENCLAW_OPENWEBUI_PROMPT=...` で、Open WebUI スモークが使う nonce チェックプロンプトを上書き
- `OPENWEBUI_IMAGE=...` で、固定された Open WebUI イメージタグを上書き

## ドキュメント健全性チェック

ドキュメント編集後は docsチェックを実行してください: `pnpm check:docs`。
ページ内見出しチェックも必要な場合は、完全なMintlifyアンカー検証を実行してください: `pnpm docs:check-links:anchors`。

## オフライン回帰（CI安全）

これらは、実際のプロバイダーなしでの「実パイプライン」回帰です。

- Gateway tool calling（mock OpenAI、実gateway + agent loop）: `src/gateway/gateway.test.ts`（ケース: "runs a mock OpenAI tool call end-to-end via gateway agent loop"）
- Gateway wizard（WS `wizard.start`/`wizard.next`、設定 + auth の書き込みを強制）: `src/gateway/gateway.test.ts`（ケース: "runs wizard over ws and writes auth token config"）

## Agent reliability evals（Skills）

すでに、いくつかのCI安全なテストが「agent reliability evals」のように動作しています。

- 実際のgateway + agent loop を通る mock tool-calling（`src/gateway/gateway.test.ts`）。
- セッション配線と設定効果を検証する end-to-end のウィザードフロー（`src/gateway/gateway.test.ts`）。

Skills についてまだ不足しているもの（[Skills](/ja-JP/tools/skills) を参照）:

- **意思決定:** Skills がプロンプトに列挙されているとき、agent は正しい skill を選ぶか（または無関係なものを避けるか）？
- **準拠:** agent は使用前に `SKILL.md` を読み、必要な手順/引数に従うか？
- **ワークフロー契約:** ツール順序、セッション履歴の引き継ぎ、sandbox境界を検証するマルチターンシナリオ。

将来の eval は、まず決定論的であるべきです。

- mockプロバイダーを使い、ツール呼び出し + 順序、skillファイル読み取り、セッション配線を検証するシナリオランナー。
- skill に焦点を当てた小規模シナリオスイート（使う vs 避ける、ゲーティング、プロンプトインジェクション）。
- CI安全なスイートが整ってからのみにする、任意のlive eval（オプトイン、envゲート付き）。

## 契約テスト（plugin と channel の形状）

契約テストは、登録されたすべてのplugin と channel がその
インターフェース契約に準拠していることを検証します。検出されたすべてのplugin を反復し、
形状と挙動のアサーションスイートを実行します。デフォルトの `pnpm test` unitレーンは、
これらの共有シームおよびスモークファイルを意図的にスキップします。共有のchannel または provider サーフェスに触れた場合は、
契約コマンドを明示的に実行してください。

### コマンド

- すべての契約: `pnpm test:contracts`
- channel 契約のみ: `pnpm test:contracts:channels`
- provider 契約のみ: `pnpm test:contracts:plugins`

### Channel契約

`src/channels/plugins/contracts/*.contract.test.ts` にあります。

- **plugin** - 基本的なplugin形状（id、name、capabilities）
- **setup** - セットアップウィザード契約
- **session-binding** - セッションbind動作
- **outbound-payload** - メッセージpayload構造
- **inbound** - 受信メッセージ処理
- **actions** - channel action ハンドラー
- **threading** - thread ID 処理
- **directory** - ディレクトリ/roster API
- **group-policy** - グループポリシー強制

### Provider status契約

`src/plugins/contracts/*.contract.test.ts` にあります。

- **status** - channel status プローブ
- **registry** - plugin registry 形状

### Provider契約

`src/plugins/contracts/*.contract.test.ts` にあります。

- **auth** - 認証フロー契約
- **auth-choice** - 認証の選択/選定
- **catalog** - モデルcatalog API
- **discovery** - plugin 検出
- **loader** - plugin 読み込み
- **runtime** - provider ランタイム
- **shape** - plugin の形状/インターフェース
- **wizard** - セットアップウィザード

### 実行するタイミング

- plugin-sdk のエクスポートまたは subpath を変更した後
- channel または provider plugin を追加または変更した後
- plugin 登録または検出をリファクタリングした後

契約テストはCIで実行され、実際のAPIキーは不要です。

## 回帰の追加（ガイダンス）

liveで発見された provider/model 問題を修正するとき:

- 可能であればCI安全な回帰を追加する（mock/stub provider、または正確な request-shape 変換を捕捉）
- 本質的に live専用（レート制限、認証ポリシー）である場合は、liveテストを狭く保ち、env vars でオプトインにする
- バグを捕まえる最小レイヤーを狙う:
  - provider の request conversion/replay バグ → direct models テスト
  - gateway の session/history/tool pipeline バグ → gateway liveスモークまたはCI安全なgateway mockテスト
- SecretRef traversal ガードレール:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` は、registry metadata（`listSecretTargetRegistryEntries()`）から SecretRef クラスごとにサンプル対象を1つ導出し、その後 traversal-segment exec id が拒否されることを検証します。
  - `src/secrets/target-registry-data.ts` に新しい `includeInPlan` SecretRef 対象ファミリーを追加した場合は、そのテストの `classifyTargetClass` を更新してください。このテストは、未分類の対象idで意図的に失敗するため、新しいクラスが黙ってスキップされることはありません。
