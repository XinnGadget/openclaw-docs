---
read_when:
    - models CLI（models list/set/scan/aliases/fallbacks）を追加または変更する
    - モデルのフォールバック動作や選択 UX を変更する
    - モデルスキャンのプローブ（tools/images）を更新する
summary: 'Models CLI: 一覧、設定、エイリアス、フォールバック、スキャン、ステータス'
title: モデル CLI
x-i18n:
    generated_at: "2026-04-06T03:07:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 299602ccbe0c3d6bbdb2deab22bc60e1300ef6843ed0b8b36be574cc0213c155
    source_path: concepts/models.md
    workflow: 15
---

# モデル CLI

認証プロファイルの
ローテーション、クールダウン、およびそれがフォールバックとどう相互作用するかについては、[/concepts/model-failover](/ja-JP/concepts/model-failover) を参照してください。
プロバイダーの概要と例については、[/concepts/model-providers](/ja-JP/concepts/model-providers) を参照してください。

## モデル選択の仕組み

OpenClaw は、次の順序でモデルを選択します。

1. **Primary** モデル（`agents.defaults.model.primary` または `agents.defaults.model`）。
2. `agents.defaults.model.fallbacks` 内の **Fallbacks**（順番どおり）。
3. **プロバイダー認証フェイルオーバー** は、次のモデルへ移る前にプロバイダー内部で発生します。

関連項目:

- `agents.defaults.models` は、OpenClaw が使用できるモデルの許可リスト/カタログです（エイリアスも含む）。
- `agents.defaults.imageModel` は、Primary モデルが画像を受け付けられない場合に**のみ**使用されます。
- `agents.defaults.pdfModel` は `pdf` ツールで使用されます。省略した場合、ツールは `agents.defaults.imageModel`、その次に解決済みのセッション/デフォルトモデルへフォールバックします。
- `agents.defaults.imageGenerationModel` は共有画像生成機能で使用されます。省略した場合でも、`image_generate` は認証済みプロバイダーのデフォルトを推測できます。まず現在のデフォルトプロバイダーを試し、その後、残りの登録済み画像生成プロバイダーをプロバイダー ID 順で試します。特定のプロバイダー/モデルを設定する場合は、そのプロバイダーの認証/API キーも設定してください。
- `agents.defaults.musicGenerationModel` は共有音楽生成機能で使用されます。省略した場合でも、`music_generate` は認証済みプロバイダーのデフォルトを推測できます。まず現在のデフォルトプロバイダーを試し、その後、残りの登録済み音楽生成プロバイダーをプロバイダー ID 順で試します。特定のプロバイダー/モデルを設定する場合は、そのプロバイダーの認証/API キーも設定してください。
- `agents.defaults.videoGenerationModel` は共有動画生成機能で使用されます。省略した場合でも、`video_generate` は認証済みプロバイダーのデフォルトを推測できます。まず現在のデフォルトプロバイダーを試し、その後、残りの登録済み動画生成プロバイダーをプロバイダー ID 順で試します。特定のプロバイダー/モデルを設定する場合は、そのプロバイダーの認証/API キーも設定してください。
- エージェント単位のデフォルトは、`agents.list[].model` とバインディングによって `agents.defaults.model` を上書きできます（[/concepts/multi-agent](/ja-JP/concepts/multi-agent) を参照）。

## クイックモデルポリシー

- 利用可能な中で最も強力な最新世代モデルを Primary に設定してください。
- コストやレイテンシに敏感なタスクや、重要度の低いチャットには Fallbacks を使用してください。
- ツール有効エージェントや信頼できない入力では、古い/弱いモデル階層は避けてください。

## オンボーディング（推奨）

設定を手で編集したくない場合は、オンボーディングを実行してください。

```bash
openclaw onboard
```

これにより、**OpenAI Code (Codex) subscription**（OAuth）や **Anthropic**（API キーまたは Claude CLI）を含む一般的なプロバイダーのモデルと認証を設定できます。

## 設定キー（概要）

- `agents.defaults.model.primary` と `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel.primary` と `agents.defaults.imageModel.fallbacks`
- `agents.defaults.pdfModel.primary` と `agents.defaults.pdfModel.fallbacks`
- `agents.defaults.imageGenerationModel.primary` と `agents.defaults.imageGenerationModel.fallbacks`
- `agents.defaults.videoGenerationModel.primary` と `agents.defaults.videoGenerationModel.fallbacks`
- `agents.defaults.models`（許可リスト + エイリアス + プロバイダーパラメーター）
- `models.providers`（`models.json` に書き込まれるカスタムプロバイダー）

モデル参照は小文字に正規化されます。`z.ai/*` のようなプロバイダーエイリアスは `zai/*` に正規化されます。

プロバイダー設定例（OpenCode を含む）は
[/providers/opencode](/ja-JP/providers/opencode) にあります。

## 「Model is not allowed」（および応答が止まる理由）

`agents.defaults.models` が設定されている場合、それは `/model` とセッション上書きの**許可リスト**になります。ユーザーがその許可リストにないモデルを選択すると、OpenClaw は次を返します。

```
Model "provider/model" is not allowed. Use /model to list available models.
```

これは通常の応答が生成される**前**に発生するため、メッセージに「応答しなかった」ように感じられることがあります。修正方法は次のいずれかです。

- モデルを `agents.defaults.models` に追加する
- 許可リストをクリアする（`agents.defaults.models` を削除する）
- `/model list` からモデルを選ぶ

許可リスト設定の例:

```json5
{
  agent: {
    model: { primary: "anthropic/claude-sonnet-4-6" },
    models: {
      "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
      "anthropic/claude-opus-4-6": { alias: "Opus" },
    },
  },
}
```

## チャットでモデルを切り替える（`/model`）

再起動せずに、現在のセッションのモデルを切り替えられます。

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model status
```

注記:

- `/model`（および `/model list`）は、コンパクトな番号付きピッカーです（モデルファミリー + 利用可能なプロバイダー）。
- Discord では、`/model` と `/models` を実行すると、プロバイダーとモデルのドロップダウン、および Submit ステップを備えたインタラクティブピッカーが開きます。
- `/model <#>` はそのピッカーから選択します。
- `/model` は新しいセッション選択を即座に永続化します。
- エージェントがアイドル状態であれば、次の実行ですぐに新しいモデルが使用されます。
- すでに実行中の場合、OpenClaw はライブ切り替えを保留としてマークし、適切なリトライポイントでのみ新しいモデルへ再始動します。
- ツールアクティビティまたは応答出力がすでに始まっている場合、保留中の切り替えは、後続のリトライ機会または次のユーザーターンまでキューに残ることがあります。
- `/model status` は詳細ビューです（認証候補と、設定されている場合はプロバイダーエンドポイントの `baseUrl` + `api` モード）。
- モデル参照は**最初の** `/` で分割して解析されます。`/model <ref>` を入力する場合は `provider/model` を使用してください。
- モデル ID 自体に `/` が含まれる場合（OpenRouter スタイル）は、プロバイダープレフィックスを含める必要があります（例: `/model openrouter/moonshotai/kimi-k2`）。
- プロバイダーを省略した場合、OpenClaw は入力を次の順で解決します。
  1. エイリアス一致
  2. そのプレフィックスなしモデル ID に対する、一意の設定済みプロバイダー一致
  3. 設定済みデフォルトプロバイダーへの非推奨フォールバック
     そのプロバイダーが設定済みデフォルトモデルを提供しなくなっている場合、OpenClaw は古い削除済みプロバイダーデフォルトを見せないように、代わりに最初の設定済みプロバイダー/モデルへフォールバックします。

完全なコマンド動作/設定: [スラッシュコマンド](/ja-JP/tools/slash-commands)。

## CLI コマンド

```bash
openclaw models list
openclaw models status
openclaw models set <provider/model>
openclaw models set-image <provider/model>

openclaw models aliases list
openclaw models aliases add <alias> <provider/model>
openclaw models aliases remove <alias>

openclaw models fallbacks list
openclaw models fallbacks add <provider/model>
openclaw models fallbacks remove <provider/model>
openclaw models fallbacks clear

openclaw models image-fallbacks list
openclaw models image-fallbacks add <provider/model>
openclaw models image-fallbacks remove <provider/model>
openclaw models image-fallbacks clear
```

`openclaw models`（サブコマンドなし）は `models status` のショートカットです。

### `models list`

デフォルトでは設定済みモデルを表示します。便利なフラグ:

- `--all`: 完全なカタログ
- `--local`: ローカルプロバイダーのみ
- `--provider <name>`: プロバイダーでフィルター
- `--plain`: 1 行に 1 モデル
- `--json`: 機械可読な出力

### `models status`

解決済みの Primary モデル、Fallbacks、画像モデル、および設定済みプロバイダーの認証概要を表示します。また、認証ストア内で見つかったプロファイルの OAuth 有効期限状態も表示します（デフォルトでは 24 時間以内に警告）。`--plain` は解決済みの Primary モデルのみを出力します。
OAuth 状態は常に表示され（`--json` 出力にも含まれます）、設定済みプロバイダーに認証情報がない場合、`models status` は **Missing auth** セクションを表示します。
JSON には `auth.oauth`（警告ウィンドウ + プロファイル）と `auth.providers`（プロバイダーごとの有効な認証。環境変数ベースの認証情報を含む）が含まれます。`auth.oauth` は認証ストア内プロファイルの健全性のみであり、環境変数のみのプロバイダーはそこには表示されません。
自動化には `--check` を使用してください（不足/期限切れで終了コード `1`、期限切れ間近で `2`）。
ライブ認証チェックには `--probe` を使用してください。プローブ行は認証プロファイル、環境変数認証情報、または `models.json` から来ることがあります。
明示的な `auth.order.<provider>` が保存済みプロファイルを省略している場合、プローブはそれを試す代わりに `excluded_by_auth_order` を報告します。認証が存在しても、そのプロバイダーに対してプローブ可能なモデルを解決できない場合、プローブは `status: no_model` を報告します。

認証の選択はプロバイダー/アカウント依存です。常時稼働する Gateway ホストでは、通常 API キーが最も予測しやすい選択肢です。Claude CLI の再利用や、既存の Anthropic OAuth/トークンプロファイルもサポートされています。

例（Claude CLI）:

```bash
claude auth login
openclaw models status
```

## スキャン（OpenRouter の無料モデル）

`openclaw models scan` は OpenRouter の**無料モデルカタログ**を調べ、必要に応じてツール対応と画像対応をモデルにプローブできます。

主なフラグ:

- `--no-probe`: ライブプローブをスキップする（メタデータのみ）
- `--min-params <b>`: 最小パラメーターサイズ（十億単位）
- `--max-age-days <days>`: 古いモデルをスキップする
- `--provider <name>`: プロバイダープレフィックスフィルター
- `--max-candidates <n>`: フォールバックリストのサイズ
- `--set-default`: `agents.defaults.model.primary` を最初の選択に設定する
- `--set-image`: `agents.defaults.imageModel.primary` を最初の画像選択に設定する

プローブには OpenRouter API キー（認証プロファイルまたは `OPENROUTER_API_KEY`）が必要です。キーがない場合は、候補のみを一覧表示するために `--no-probe` を使用してください。

スキャン結果は次の順でランク付けされます。

1. 画像対応
2. ツールレイテンシ
3. コンテキストサイズ
4. パラメーター数

入力

- OpenRouter の `/models` 一覧（`:free` でフィルター）
- 認証プロファイルまたは `OPENROUTER_API_KEY` からの OpenRouter API キーが必要（[/environment](/ja-JP/help/environment) を参照）
- 任意フィルター: `--max-age-days`、`--min-params`、`--provider`、`--max-candidates`
- プローブ制御: `--timeout`、`--concurrency`

TTY で実行すると、対話的にフォールバックを選択できます。非対話モードでは、デフォルトを受け入れるために `--yes` を渡してください。

## モデルレジストリ（`models.json`）

`models.providers` のカスタムプロバイダーは、エージェントディレクトリ（デフォルトは `~/.openclaw/agents/<agentId>/agent/models.json`）配下の `models.json` に書き込まれます。`models.mode` が `replace` に設定されていない限り、このファイルはデフォルトでマージされます。

一致するプロバイダー ID に対するマージモードの優先順位:

- エージェントの `models.json` にすでに存在する空でない `baseUrl` が優先されます。
- エージェントの `models.json` 内の空でない `apiKey` は、そのプロバイダーが現在の設定/認証プロファイル文脈で SecretRef 管理されていない場合にのみ優先されます。
- SecretRef 管理のプロバイダー `apiKey` 値は、解決済みシークレットを永続化する代わりに、ソースマーカー（環境変数参照の `ENV_VAR_NAME`、file/exec 参照の `secretref-managed`）から更新されます。
- SecretRef 管理のプロバイダーヘッダー値は、ソースマーカー（環境変数参照の `secretref-env:ENV_VAR_NAME`、file/exec 参照の `secretref-managed`）から更新されます。
- 空または欠落しているエージェントの `apiKey`/`baseUrl` は、設定の `models.providers` にフォールバックします。
- その他のプロバイダーフィールドは、設定および正規化されたカタログデータから更新されます。

マーカーの永続化はソース優先です。OpenClaw は、解決済みランタイムシークレット値からではなく、アクティブなソース設定スナップショット（解決前）からマーカーを書き込みます。
これは、`openclaw agent` のようなコマンド駆動パスを含め、OpenClaw が `models.json` を再生成するたびに適用されます。

## 関連

- [モデルプロバイダー](/ja-JP/concepts/model-providers) — プロバイダールーティングと認証
- [モデルフェイルオーバー](/ja-JP/concepts/model-failover) — フォールバックチェーン
- [画像生成](/ja-JP/tools/image-generation) — 画像モデル設定
- [音楽生成](/tools/music-generation) — 音楽モデル設定
- [動画生成](/tools/video-generation) — 動画モデル設定
- [設定リファレンス](/ja-JP/gateway/configuration-reference#agent-defaults) — モデル設定キー
