---
read_when:
    - 認証プロファイルのローテーション、クールダウン、またはモデルのフォールバック動作を診断する場合
    - 認証プロファイルまたはモデルのフェイルオーバールールを更新する場合
    - セッションのモデルオーバーライドがフォールバック再試行とどのように相互作用するかを理解する場合
summary: OpenClawが認証プロファイルをローテーションし、モデル間でフォールバックする方法
title: モデルフェイルオーバー
x-i18n:
    generated_at: "2026-04-07T04:41:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: d88821e229610f236bdab3f798d5e8c173f61a77c01017cc87431126bf465e32
    source_path: concepts/model-failover.md
    workflow: 15
---

# モデルフェイルオーバー

OpenClawは失敗を2段階で処理します。

1. 現在のプロバイダー内での**認証プロファイルのローテーション**。
2. `agents.defaults.model.fallbacks`内の次のモデルへの**モデルフォールバック**。

このドキュメントでは、ランタイムのルールとそれを支えるデータについて説明します。

## ランタイムフロー

通常のテキスト実行では、OpenClawは候補を次の順序で評価します。

1. 現在選択されているセッションモデル。
2. 設定された`agents.defaults.model.fallbacks`を順番に。
3. 実行がオーバーライドから開始された場合は、最後に設定済みのプライマリモデル。

各候補の内部では、OpenClawは次のモデル候補に進む前に、認証プロファイルのフェイルオーバーを試します。

大まかな流れ:

1. アクティブなセッションモデルと認証プロファイルの優先設定を解決する。
2. モデル候補チェーンを構築する。
3. 現在のプロバイダーを、認証プロファイルのローテーション/クールダウンルールとともに試す。
4. そのプロバイダーがフェイルオーバー対象のエラーで尽きた場合、次のモデル候補へ移る。
5. 再試行が始まる前に、選択されたフォールバックオーバーライドを永続化し、他のセッションリーダーがランナーがこれから使うのと同じプロバイダー/モデルを見られるようにする。
6. フォールバック候補が失敗した場合、その失敗した候補とまだ一致しているときに限り、フォールバック所有のセッションオーバーライドフィールドだけをロールバックする。
7. すべての候補が失敗した場合、各試行の詳細と、わかっている場合は最も早いクールダウン満了時刻を含む`FallbackSummaryError`を投げる。

これは意図的に「セッション全体を保存して復元する」よりも狭い範囲です。返信ランナーは、フォールバックのために自身が所有するモデル選択フィールドだけを永続化します。

- `providerOverride`
- `modelOverride`
- `authProfileOverride`
- `authProfileOverrideSource`
- `authProfileOverrideCompactionCount`

これにより、失敗したフォールバック再試行が、試行の実行中に発生した手動の`/model`変更やセッションローテーション更新など、新しい無関係のセッション変更を上書きするのを防ぎます。

## 認証ストレージ（キー + OAuth）

OpenClawは、APIキーとOAuthトークンの両方に**認証プロファイル**を使用します。

- シークレットは`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`に保存されます（レガシー: `~/.openclaw/agent/auth-profiles.json`）。
- ランタイムの認証ルーティング状態は`~/.openclaw/agents/<agentId>/agent/auth-state.json`に保存されます。
- 設定`auth.profiles` / `auth.order`は**メタデータ + ルーティング専用**です（シークレットは含みません）。
- レガシーのインポート専用OAuthファイル: `~/.openclaw/credentials/oauth.json`（初回使用時に`auth-profiles.json`へインポートされます）。

詳細: [/concepts/oauth](/ja-JP/concepts/oauth)

認証情報の種類:

- `type: "api_key"` → `{ provider, key }`
- `type: "oauth"` → `{ provider, access, refresh, expires, email? }`（一部のプロバイダーでは`projectId`/`enterpriseUrl`を追加）

## プロファイルID

OAuthログインは、複数アカウントが共存できるように個別のプロファイルを作成します。

- デフォルト: メールアドレスが利用できない場合は`provider:default`
- メールアドレス付きOAuth: `provider:<email>`（例: `google-antigravity:user@gmail.com`）

プロファイルは`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`の`profiles`配下に保存されます。

## ローテーション順序

プロバイダーに複数のプロファイルがある場合、OpenClawは次のような順序を選びます。

1. **明示的な設定**: `auth.order[provider]`（設定されている場合）。
2. **設定済みプロファイル**: プロバイダーでフィルタした`auth.profiles`。
3. **保存済みプロファイル**: そのプロバイダー向けの`auth-profiles.json`内エントリ。

明示的な順序が設定されていない場合、OpenClawはラウンドロビン順序を使用します。

- **主キー:** プロファイル種別（**APIキーよりOAuthを優先**）
- **副キー:** `usageStats.lastUsed`（各種別内で最も古いものが先）
- **クールダウン中/無効化されたプロファイル**は末尾へ移動し、最も早く期限切れになる順に並べられます。

### セッションのスティッキネス（キャッシュにやさしい）

OpenClawは、プロバイダーキャッシュを温かい状態に保つため、**選択した認証プロファイルをセッションごとに固定**します。
毎リクエストごとにローテーションするわけでは**ありません**。固定されたプロファイルは次の場合まで再利用されます。

- セッションがリセットされたとき（`/new` / `/reset`）
- compactionが完了したとき（compaction countが増加）
- プロファイルがクールダウン中/無効化されているとき

`/model …@<profileId>`による手動選択は、そのセッションに対する**ユーザーオーバーライド**を設定し、
新しいセッションが始まるまで自動ローテーションされません。

自動固定されたプロファイル（セッションルーターが選択したもの）は、**優先設定**として扱われます。
最初に試されますが、レート制限やタイムアウト時にはOpenClawが別のプロファイルへローテーションする場合があります。
ユーザー固定のプロファイルはそのプロファイルにロックされたままです。そのプロファイルが失敗し、モデルフォールバックが設定されている場合、
OpenClawはプロファイルを切り替える代わりに次のモデルへ移動します。

### OAuthが「消えたように見える」理由

同じプロバイダーにOAuthプロファイルとAPIキープロファイルの両方がある場合、固定されていなければ、ラウンドロビンによってメッセージ間でそれらが切り替わることがあります。単一プロファイルを強制するには:

- `auth.order[provider] = ["provider:profileId"]`で固定する、または
- `/model …`でプロファイルオーバーライド付きのセッション単位オーバーライドを使う（UI/チャット面が対応している場合）。

## クールダウン

プロファイルが認証/レート制限エラー（またはレート制限のように見えるタイムアウト）で失敗すると、
OpenClawはそのプロファイルをクールダウン状態にし、次のプロファイルへ移動します。
このレート制限バケットは単純な`429`より広く、`Too many concurrent requests`、`ThrottlingException`、
`concurrency limit reached`、`workers_ai ... quota limit exceeded`、
`throttled`、`resource exhausted`、`weekly/monthly limit reached`のような
定期的な使用量ウィンドウ制限などのプロバイダーメッセージも含みます。
フォーマット/無効リクエストエラー（たとえばCloud Code AssistのツールコールID
検証失敗）はフェイルオーバー対象として扱われ、同じクールダウンを使用します。
`Unhandled stop reason: error`、
`stop reason: error`、`reason: error`のようなOpenAI互換のstop-reasonエラーは、タイムアウト/フェイルオーバー
シグナルとして分類されます。
ソースが既知の一時的パターンに一致する場合、プロバイダースコープの汎用サーバーテキストもこのタイムアウトバケットに入ることがあります。たとえば、Anthropicの単体の
`An unknown error occurred`や、`internal server error`、`unknown error, 520`、`upstream error`、
`backend error`といった一時的サーバーテキストを含むJSON `api_error`ペイロードは、フェイルオーバー対象のタイムアウトとして扱われます。OpenRouter固有の
単体の`Provider returned error`のような汎用upstreamテキストも、プロバイダーコンテキストが実際にOpenRouterである場合に限って
タイムアウトとして扱われます。`LLM request failed with an unknown error.`のような汎用の内部
フォールバックテキストは保守的に扱われ、それ単体ではフェイルオーバーをトリガーしません。

レート制限クールダウンはモデルスコープになることもあります。

- 失敗したモデルIDがわかっている場合、OpenClawはレート制限失敗に対して`cooldownModel`を記録します。
- 同じプロバイダー上の兄弟モデルは、クールダウンが別モデルにスコープされていれば引き続き試行できます。
- 請求/無効化ウィンドウは、モデルをまたいでプロファイル全体を引き続きブロックします。

クールダウンには指数バックオフが使われます。

- 1分
- 5分
- 25分
- 1時間（上限）

状態は`auth-state.json`の`usageStats`配下に保存されます。

```json
{
  "usageStats": {
    "provider:profile": {
      "lastUsed": 1736160000000,
      "cooldownUntil": 1736160600000,
      "errorCount": 2
    }
  }
}
```

## 請求による無効化

請求/クレジット失敗（たとえば「insufficient credits」や「credit balance too low」）はフェイルオーバー対象として扱われますが、通常は一時的ではありません。短いクールダウンの代わりに、OpenClawはそのプロファイルを**無効化**済みとしてマークし（より長いバックオフ付き）、次のプロファイル/プロバイダーへローテーションします。

すべての請求っぽいレスポンスが`402`というわけではなく、すべてのHTTP `402`が
ここに入るわけでもありません。OpenClawは、プロバイダーが代わりに`401`や`403`を返した場合でも、
明示的な請求テキストを請求レーンに保持しますが、プロバイダー固有のマッチャーはそれを所有するプロバイダーにスコープされたままです（例: OpenRouterの`403 Key limit
exceeded`）。一方、一時的な`402`の使用量ウィンドウや
organization/workspaceのspend-limitエラーは、メッセージが再試行可能に見える場合、`rate_limit`として分類されます
（例: `weekly usage limit exhausted`、`daily
limit reached, resets tomorrow`、`organization spending limit exceeded`）。
これらは長い
請求無効化パスではなく、短いクールダウン/フェイルオーバーパスに留まります。

状態は`auth-state.json`に保存されます。

```json
{
  "usageStats": {
    "provider:profile": {
      "disabledUntil": 1736178000000,
      "disabledReason": "billing"
    }
  }
}
```

デフォルト:

- 請求バックオフは**5時間**から始まり、請求失敗ごとに倍増し、**24時間**で上限になります。
- バックオフカウンターは、そのプロファイルが**24時間**失敗しなければリセットされます（設定可能）。
- 過負荷時の再試行では、モデルフォールバックの前に**同一プロバイダー内で1回の認証プロファイルローテーション**を許可します。
- 過負荷時の再試行はデフォルトで**0 msバックオフ**を使用します。

## モデルフォールバック

あるプロバイダーのすべてのプロファイルが失敗した場合、OpenClawは
`agents.defaults.model.fallbacks`内の次のモデルへ移動します。これは認証失敗、レート制限、および
プロファイルローテーションを使い切ったタイムアウトに適用されます（それ以外のエラーではフォールバックは進みません）。

過負荷エラーとレート制限エラーは、請求クールダウンよりも積極的に処理されます。デフォルトでは、OpenClawは同一プロバイダー内で1回の認証プロファイル再試行を許可し、その後待機せずに次に設定されたモデルフォールバックへ切り替えます。
`ModelNotReadyException`のようなプロバイダー多忙シグナルはその過負荷バケットに入ります。
これは`auth.cooldowns.overloadedProfileRotations`、
`auth.cooldowns.overloadedBackoffMs`、および
`auth.cooldowns.rateLimitedProfileRotations`で調整できます。

実行がモデルオーバーライド（フックまたはCLI）で始まった場合でも、フォールバックは設定されたフォールバックを試したあと、
最後は`agents.defaults.model.primary`に到達します。

### 候補チェーンのルール

OpenClawは、現在要求されている`provider/model`と設定済みフォールバックから候補リストを構築します。

ルール:

- 要求されたモデルは常に最初です。
- 明示的に設定されたフォールバックは重複排除されますが、モデル
  allowlistではフィルタされません。これらは明示的なオペレーター意図として扱われます。
- 現在の実行が同じプロバイダーファミリー内の設定済みフォールバック上にすでにある場合、OpenClawは設定済みチェーン全体を使い続けます。
- 現在の実行が設定とは異なるプロバイダー上にあり、その現在の
  モデルが設定済みフォールバックチェーンの一部でない場合、OpenClawは別プロバイダーの無関係な設定済みフォールバックを追加しません。
- 実行がオーバーライドから始まった場合、設定済みプライマリが
  最後に追加されるため、先行する候補が尽きたあとにチェーンを通常のデフォルトへ戻せます。

### どのエラーでフォールバックが進むか

モデルフォールバックは次の場合に継続します。

- 認証失敗
- レート制限とクールダウン枯渇
- 過負荷/プロバイダー多忙エラー
- タイムアウト系のフェイルオーバーエラー
- 請求による無効化
- `LiveSessionModelSwitchError`。これはフェイルオーバーパスに正規化されるため、
  古い永続化モデルが外側の再試行ループを作りません
- 他の未認識エラーで、まだ候補が残っている場合

モデルフォールバックが継続しないのは次の場合です。

- タイムアウト/フェイルオーバー系ではない明示的な中断
- compaction/再試行ロジック内に留めるべきコンテキストオーバーフローエラー
  （例: `request_too_large`、`INVALID_ARGUMENT: input exceeds the maximum
number of tokens`、`input token count exceeds the maximum number of input
tokens`、`The input is too long for the model`、`ollama error: context
length exceeded`）
- 候補が残っていないときの最終的な未知のエラー

### クールダウンのスキップとプローブ動作

あるプロバイダーのすべての認証プロファイルがすでにクールダウン中の場合でも、OpenClawは
そのプロバイダーを永続的に自動スキップするわけではありません。候補ごとに判断します。

- 永続的な認証失敗では、プロバイダー全体を即座にスキップします。
- 請求による無効化は通常スキップしますが、再起動なしで回復できるよう、
  プライマリ候補はスロットル付きで引き続きプローブされることがあります。
- プライマリ候補は、クールダウン満了が近い場合に、プロバイダーごとの
  スロットル付きでプローブされることがあります。
- 同一プロバイダー内のフォールバック兄弟は、失敗が一時的に見える場合（`rate_limit`、`overloaded`、またはunknown）、
  クールダウン中でも試行されることがあります。これは特に、レート制限がモデルスコープであり、兄弟モデルが
  すぐ回復する可能性がある場合に重要です。
- 一時的クールダウンのプローブは、1回のフォールバック実行につきプロバイダーごとに1回に制限されるため、
  単一のプロバイダーがクロスプロバイダーのフォールバックを停滞させることはありません。

## セッションオーバーライドとライブモデル切り替え

セッションモデルの変更は共有状態です。アクティブなランナー、`/model`コマンド、
compaction/セッション更新、およびライブセッション再調整はすべて、同じセッションエントリの
一部を読み書きします。

つまり、フォールバック再試行はライブモデル切り替えと協調する必要があります。

- 保留中のライブ切り替えをマークするのは、明示的なユーザー主導のモデル変更だけです。これには
  `/model`、`session_status(model=...)`、および`sessions.patch`が含まれます。
- フォールバックローテーション、heartbeatオーバーライド、
  compactionのようなシステム主導のモデル変更は、それ自体では保留中のライブ切り替えをマークしません。
- フォールバック再試行が始まる前に、返信ランナーは選択された
  フォールバックオーバーライドフィールドをセッションエントリへ永続化します。
- ライブセッション再調整は、古いランタイムモデルフィールドよりも永続化されたセッションオーバーライドを優先します。
- フォールバック試行が失敗した場合、ランナーは自分が書き込んだオーバーライドフィールドだけを、
  それらがまだその失敗した候補と一致している場合に限ってロールバックします。

これにより、典型的な競合を防ぎます。

1. プライマリが失敗する。
2. フォールバック候補がメモリ上で選択される。
3. セッションストアはまだ古いプライマリを示している。
4. ライブセッション再調整がその古いセッション状態を読み取る。
5. フォールバック試行が始まる前に、再試行が古いモデルへ戻されてしまう。

永続化されたフォールバックオーバーライドがその隙間を埋め、狭い範囲のロールバックが
より新しい手動またはランタイムのセッション変更を保護します。

## 可観測性と失敗サマリー

`runWithModelFallback(...)`は、ログと
ユーザー向けクールダウンメッセージに使われる試行ごとの詳細を記録します。

- 試行したprovider/model
- reason（`rate_limit`、`overloaded`、`billing`、`auth`、`model_not_found`、および
  類似のフェイルオーバー理由）
- 任意のstatus/code
- 人が読めるエラーサマリー

すべての候補が失敗すると、OpenClawは`FallbackSummaryError`を投げます。外側の
返信ランナーはそれを使って、「すべてのモデルが一時的にレート制限されている」のような、より具体的なメッセージを構築し、
わかっている場合は最も早いクールダウン満了時刻を含めることができます。

そのクールダウンサマリーはモデルを考慮します。

- 試行された
  provider/modelチェーンに無関係なモデルスコープのレート制限は無視されます
- 残っているブロックがそのモデルに一致するモデルスコープのレート制限である場合、OpenClawは
  そのモデルを引き続きブロックしている最後の一致満了時刻を報告します

## 関連する設定

以下については[Gateway configuration](/ja-JP/gateway/configuration)を参照してください。

- `auth.profiles` / `auth.order`
- `auth.cooldowns.billingBackoffHours` / `auth.cooldowns.billingBackoffHoursByProvider`
- `auth.cooldowns.billingMaxHours` / `auth.cooldowns.failureWindowHours`
- `auth.cooldowns.overloadedProfileRotations` / `auth.cooldowns.overloadedBackoffMs`
- `auth.cooldowns.rateLimitedProfileRotations`
- `agents.defaults.model.primary` / `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel`のルーティング

より広いモデル選択とフォールバックの概要については、[Models](/ja-JP/concepts/models)を参照してください。
