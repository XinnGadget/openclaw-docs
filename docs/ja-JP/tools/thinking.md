---
read_when:
    - 思考、fast-mode、または verbose ディレクティブの解析やデフォルトの調整
summary: '`/think`、`/fast`、`/verbose`、`/trace` のディレクティブ構文と推論の可視性'
title: 思考レベル
x-i18n:
    generated_at: "2026-04-17T04:43:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1cb44a7bf75546e5a8c3204e12f3297221449b881161d173dea4983da3921649
    source_path: tools/thinking.md
    workflow: 15
---

# 思考レベル（`/think` ディレクティブ）

## 機能

- 任意の受信本文内で使えるインラインディレクティブ: `/t <level>`、`/think:<level>`、または `/thinking <level>`。
- レベル（エイリアス）: `off | minimal | low | medium | high | xhigh | adaptive`
  - minimal → 「think」
  - low → 「think hard」
  - medium → 「think harder」
  - high → 「ultrathink」（最大予算）
  - xhigh → 「ultrathink+」（GPT-5.2 + Codex モデルと Anthropic Claude Opus 4.7 effort）
  - adaptive → プロバイダー管理の適応的思考（Anthropic Claude 4.6 と Opus 4.7 でサポート）
  - `x-high`、`x_high`、`extra-high`、`extra high`、`extra_high` は `xhigh` にマッピングされます。
  - `highest`、`max` は `high` にマッピングされます。
- プロバイダーに関する注意:
  - Anthropic Claude 4.6 モデルは、明示的な思考レベルが設定されていない場合、デフォルトで `adaptive` になります。
  - Anthropic Claude Opus 4.7 は adaptive thinking をデフォルトにしません。その API effort のデフォルトは、思考レベルを明示的に設定しない限りプロバイダー側で管理されます。
  - Anthropic Claude Opus 4.7 では、`/think xhigh` は adaptive thinking と `output_config.effort: "xhigh"` にマッピングされます。これは `/think` が思考ディレクティブであり、`xhigh` が Opus 4.7 の effort 設定だからです。
  - Anthropic 互換ストリーミングパス上の MiniMax（`minimax/*`）は、モデル params または request params で thinking を明示的に設定しない限り、デフォルトで `thinking: { type: "disabled" }` になります。これにより、MiniMax の非ネイティブな Anthropic ストリーム形式から `reasoning_content` のデルタが漏れるのを防ぎます。
  - Z.AI（`zai/*`）は二値の thinking（`on`/`off`）のみをサポートします。`off` 以外のレベルはすべて `on` として扱われます（`low` にマッピング）。
  - Moonshot（`moonshot/*`）は `/think off` を `thinking: { type: "disabled" }` に、`off` 以外のレベルを `thinking: { type: "enabled" }` にマッピングします。thinking が有効な場合、Moonshot は `tool_choice` として `auto|none` しか受け付けないため、OpenClaw は非互換の値を `auto` に正規化します。

## 解決順序

1. メッセージ上のインラインディレクティブ（そのメッセージにのみ適用）。
2. セッションオーバーライド（ディレクティブのみのメッセージを送ることで設定）。
3. エージェントごとのデフォルト（設定内の `agents.list[].thinkingDefault`）。
4. グローバルデフォルト（設定内の `agents.defaults.thinkingDefault`）。
5. フォールバック: Anthropic Claude 4.6 モデルでは `adaptive`、Anthropic Claude Opus 4.7 では明示設定がない限り `off`、その他の reasoning 対応モデルでは `low`、それ以外では `off`。

## セッションのデフォルトを設定する

- **ディレクティブだけ**のメッセージを送信します（空白は可）。例: `/think:medium` または `/t high`。
- これは現在のセッションに保持されます（デフォルトでは送信者単位）。`/think:off` またはセッションのアイドルリセットで解除されます。
- 確認の返信が送られます（`Thinking level set to high.` / `Thinking disabled.`）。レベルが無効な場合（例: `/thinking big`）、コマンドは拒否され、ヒントが返され、セッション状態は変更されません。
- 引数なしで `/think`（または `/think:`）を送ると、現在の思考レベルを確認できます。

## エージェントごとの適用

- **Embedded Pi**: 解決されたレベルは、プロセス内の Pi エージェントランタイムに渡されます。

## Fast mode（`/fast`）

- レベル: `on|off`。
- ディレクティブのみのメッセージでセッションの fast-mode オーバーライドを切り替え、`Fast mode enabled.` / `Fast mode disabled.` と返信します。
- モード指定なしで `/fast`（または `/fast status`）を送ると、現在有効な fast-mode 状態を確認できます。
- OpenClaw は fast mode を次の順序で解決します:
  1. インライン／ディレクティブのみの `/fast on|off`
  2. セッションオーバーライド
  3. エージェントごとのデフォルト（`agents.list[].fastModeDefault`）
  4. モデルごとの設定: `agents.defaults.models["<provider>/<model>"].params.fastMode`
  5. フォールバック: `off`
- `openai/*` では、fast mode はサポートされる Responses リクエストで `service_tier=priority` を送信することで OpenAI の priority processing にマッピングされます。
- `openai-codex/*` では、fast mode は Codex Responses に同じ `service_tier=priority` フラグを送信します。OpenClaw は両方の認証パスで 1 つの共有 `/fast` トグルを維持します。
- `api.anthropic.com` に送信される OAuth 認証トラフィックを含む直接の公開 `anthropic/*` リクエストでは、fast mode は Anthropic の service tiers にマッピングされます: `/fast on` は `service_tier=auto`、`/fast off` は `service_tier=standard_only` を設定します。
- Anthropic 互換パス上の `minimax/*` では、`/fast on`（または `params.fastMode: true`）は `MiniMax-M2.7` を `MiniMax-M2.7-highspeed` に書き換えます。
- 明示的な Anthropic `serviceTier` / `service_tier` モデル params は、両方が設定されている場合、fast-mode のデフォルトより優先されます。OpenClaw は引き続き、Anthropic 以外のプロキシ base URL には Anthropic service-tier の注入を行いません。

## Verbose ディレクティブ（`/verbose` または `/v`）

- レベル: `on`（最小）| `full` | `off`（デフォルト）。
- ディレクティブのみのメッセージでセッション verbose を切り替え、`Verbose logging enabled.` / `Verbose logging disabled.` と返信します。無効なレベルでは、状態を変更せずにヒントを返します。
- `/verbose off` は明示的なセッションオーバーライドとして保存されます。Sessions UI で `inherit` を選ぶと解除できます。
- インラインディレクティブはそのメッセージにのみ影響します。それ以外では、セッション／グローバルのデフォルトが適用されます。
- 引数なしで `/verbose`（または `/verbose:`）を送ると、現在の verbose レベルを確認できます。
- verbose が on の場合、構造化されたツール結果を出力するエージェント（Pi、その他の JSON エージェント）は、各ツール呼び出しをそれぞれ独立したメタデータ専用メッセージとして返し、利用可能な場合は `<emoji> <tool-name>: <arg>`（path/command）を接頭辞として付けます。これらのツール要約は、各ツールの開始時に送信されます（ストリーミングデルタではなく、別バブル）。
- ツール失敗の要約は通常モードでも表示されますが、生のエラー詳細の接尾辞は verbose が `on` または `full` の場合にのみ表示されます。
- verbose が `full` の場合、ツール出力も完了後に転送されます（別バブル、安全な長さに切り詰め）。実行中に `/verbose on|full|off` を切り替えると、その後のツールバブルには新しい設定が反映されます。

## Plugin trace ディレクティブ（`/trace`）

- レベル: `on` | `off`（デフォルト）。
- ディレクティブのみのメッセージでセッションの plugin trace 出力を切り替え、`Plugin trace enabled.` / `Plugin trace disabled.` と返信します。
- インラインディレクティブはそのメッセージにのみ影響します。それ以外では、セッション／グローバルのデフォルトが適用されます。
- 引数なしで `/trace`（または `/trace:`）を送ると、現在の trace レベルを確認できます。
- `/trace` は `/verbose` よりも限定的で、Active Memory のデバッグ要約のような plugin 所有の trace/debug 行だけを公開します。
- trace 行は `/status` に表示されることもあり、通常のアシスタント返信の後に続く診断メッセージとして現れることもあります。

## 推論の可視性（`/reasoning`）

- レベル: `on|off|stream`。
- ディレクティブのみのメッセージで、返信内に thinking ブロックを表示するかどうかを切り替えます。
- 有効にすると、推論は `Reasoning:` を接頭辞とする**別メッセージ**として送信されます。
- `stream`（Telegram のみ）: 返信生成中に Telegram の下書きバブルへ推論をストリーミングし、その後、推論を含まない最終回答を送信します。
- エイリアス: `/reason`。
- 引数なしで `/reasoning`（または `/reasoning:`）を送ると、現在の推論レベルを確認できます。
- 解決順序: インラインディレクティブ、次にセッションオーバーライド、次にエージェントごとのデフォルト（`agents.list[].reasoningDefault`）、最後にフォールバック（`off`）。

## 関連

- Elevated mode のドキュメントは [Elevated mode](/ja-JP/tools/elevated) にあります。

## Heartbeat

- Heartbeat プローブ本文は、設定された heartbeat プロンプトです（デフォルト: `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`）。heartbeat メッセージ内のインラインディレクティブは通常どおり適用されます（ただし、heartbeat からセッションデフォルトを変更するのは避けてください）。
- Heartbeat 配信はデフォルトで最終ペイロードのみです。別個の `Reasoning:` メッセージも送信するには（利用可能な場合）、`agents.defaults.heartbeat.includeReasoning: true` またはエージェントごとの `agents.list[].heartbeat.includeReasoning: true` を設定します。

## Web チャット UI

- Web チャットの thinking セレクターは、ページ読み込み時に受信セッションストア／設定に保存されているセッションレベルを反映します。
- 別のレベルを選ぶと、`sessions.patch` を通じてセッションオーバーライドが即座に書き込まれます。次の送信までは待たず、1 回限りの `thinkingOnce` オーバーライドでもありません。
- 最初のオプションは常に `Default (<resolved level>)` で、この解決済みデフォルトはアクティブなセッションモデルから決まります: Anthropic 上の Claude 4.6 では `adaptive`、設定がない限り Anthropic Claude Opus 4.7 では `off`、その他の reasoning 対応モデルでは `low`、それ以外では `off`。
- ピッカーはプロバイダーを認識したままです:
  - ほとんどのプロバイダーでは `off | minimal | low | medium | high | adaptive` を表示
  - Anthropic Claude Opus 4.7 では `off | minimal | low | medium | high | xhigh | adaptive` を表示
  - Z.AI では二値の `off | on` を表示
- `/think:<level>` も引き続き動作し、同じ保存済みセッションレベルを更新するため、チャットディレクティブとピッカーは同期されたままになります。
