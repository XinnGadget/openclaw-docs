---
x-i18n:
    generated_at: "2026-04-08T04:42:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4a9066b2a939c5a9ba69141d75405f0e8097997b523164340e2f0e9a0d5060dd
    source_path: refactor/qa.md
    workflow: 15
---

# QA リファクタリング

ステータス: 基盤となる移行は着地済み。

## 目標

OpenClaw QA を分割定義モデルから単一の信頼できる情報源へ移行する:

- シナリオメタデータ
- モデルに送信されるプロンプト
- セットアップとティアダウン
- ハーネスロジック
- アサーションと成功条件
- アーティファクトとレポートのヒント

望ましい最終状態は、TypeScript にほとんどの動作をハードコードするのではなく、強力なシナリオ定義ファイルを読み込む汎用 QA ハーネスです。

## 現在の状態

現在の主要な信頼できる情報源は `qa/scenarios/index.md` と、`qa/scenarios/*.md` 配下のシナリオごとの 1 ファイルにあります。

実装済み:

- `qa/scenarios/index.md`
  - 正式な QA パックメタデータ
  - オペレーター ID
  - キックオフミッション
- `qa/scenarios/*.md`
  - シナリオごとに 1 つの markdown ファイル
  - シナリオメタデータ
  - ハンドラーバインディング
  - シナリオ固有の実行設定
- `extensions/qa-lab/src/scenario-catalog.ts`
  - markdown パックパーサー + zod バリデーション
- `extensions/qa-lab/src/qa-agent-bootstrap.ts`
  - markdown パックからのプラン描画
- `extensions/qa-lab/src/qa-agent-workspace.ts`
  - 互換性ファイル群に加えて `QA_SCENARIOS.md` を生成して配置
- `extensions/qa-lab/src/suite.ts`
  - markdown 定義のハンドラーバインディングを通じて実行可能なシナリオを選択
- QA バスプロトコル + UI
  - 画像/動画/音声/ファイル描画用の汎用インライン添付ファイル

分割されたまま残っている面:

- `extensions/qa-lab/src/suite.ts`
  - 依然として実行可能なカスタムハンドラーロジックの大半を保持
- `extensions/qa-lab/src/report.ts`
  - 依然として実行時出力からレポート構造を導出

つまり、信頼できる情報源の分割は修正されたものの、実行はまだ完全な宣言型ではなく、主にハンドラーバックのままです。

## 実際のシナリオ面はどう見えるか

現在のスイートを読むと、いくつかの異なるシナリオクラスが見えてきます。

### シンプルなインタラクション

- チャネルベースライン
- DM ベースライン
- スレッド化されたフォローアップ
- モデル切り替え
- 承認の継続実行
- リアクション/編集/削除

### 設定とランタイムの変更

- 設定パッチによる Skill 無効化
- 設定適用後の再起動ウェイクアップ
- 再起動時の設定機能切り替え
- ランタイムインベントリドリフトチェック

### ファイルシステムとリポジトリアサーション

- ソース/ドキュメント検出レポート
- Lobster Invaders をビルド
- 生成画像アーティファクトの検索

### メモリオーケストレーション

- メモリリコール
- チャネルコンテキストでのメモリツール
- メモリ失敗フォールバック
- セッションメモリランキング
- スレッドメモリ分離
- メモリ dreaming sweep

### ツールと plugin 連携

- MCP plugin-tools 呼び出し
- Skill の可視性
- Skill のホットインストール
- ネイティブ画像生成
- 画像ラウンドトリップ
- 添付ファイルからの画像理解

### マルチターンとマルチアクター

- サブエージェントのハンドオフ
- サブエージェントのファンアウト統合
- 再起動リカバリ系フロー

これらのカテゴリは DSL 要件を左右するため重要です。プロンプト + 期待されるテキストの単純な一覧だけでは不十分です。

## 方向性

### 単一の信頼できる情報源

`qa/scenarios/index.md` と `qa/scenarios/*.md` を、作成時の信頼できる情報源として使います。

パックは次を維持するべきです:

- レビューで人が読みやすい
- 機械解析可能
- 次を駆動できるだけの豊かさを持つ:
  - スイート実行
  - QA ワークスペースのブートストラップ
  - QA Lab UI メタデータ
  - ドキュメント/検出プロンプト
  - レポート生成

### 推奨する記述フォーマット

トップレベルのフォーマットとして markdown を使い、その中に構造化 YAML を入れます。

推奨形状:

- YAML frontmatter
  - id
  - title
  - surface
  - tags
  - docs refs
  - code refs
  - model/provider overrides
  - prerequisites
- 説明文セクション
  - objective
  - notes
  - debugging hints
- フェンス付き YAML ブロック
  - setup
  - steps
  - assertions
  - cleanup

これにより次が得られます:

- 巨大な JSON よりも優れた PR 可読性
- 純粋な YAML よりも豊かなコンテキスト
- 厳密なパースと zod バリデーション

生の JSON は、中間的な生成形式としてのみ許容されます。

## 提案されるシナリオファイル形状

例:

````md
---
id: image-generation-roundtrip
title: Image generation roundtrip
surface: image
tags: [media, image, roundtrip]
models:
  primary: openai/gpt-5.4
requires:
  tools: [image_generate]
  plugins: [openai, qa-channel]
docsRefs:
  - docs/help/testing.md
  - docs/concepts/model-providers.md
codeRefs:
  - extensions/qa-lab/src/suite.ts
  - src/gateway/chat-attachments.ts
---

# Objective

生成されたメディアがフォローアップターンで再添付されることを確認する。

# Setup

```yaml scenario.setup
- action: config.patch
  patch:
    agents:
      defaults:
        imageGenerationModel:
          primary: openai/gpt-image-1
- action: session.create
  key: agent:qa:image-roundtrip
```

# Steps

```yaml scenario.steps
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    画像生成チェック: QA 用の灯台画像を生成し、それを 1 文の短い文で要約してください。
- action: artifact.capture
  kind: generated-image
  promptSnippet: Image generation check
  saveAs: lighthouseImage
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    ラウンドトリップ画像検査チェック: 生成された灯台の添付画像を 1 文の短い文で説明してください。
  attachments:
    - fromArtifact: lighthouseImage
```

# Expect

```yaml scenario.expect
- assert: outbound.textIncludes
  value: lighthouse
- assert: requestLog.matches
  where:
    promptIncludes: Roundtrip image inspection check
  imageInputCountGte: 1
- assert: artifact.exists
  ref: lighthouseImage
```
````

## DSL がカバーすべきランナー機能

現在のスイートに基づくと、汎用ランナーにはプロンプト実行以上のものが必要です。

### 環境およびセットアップアクション

- `bus.reset`
- `gateway.waitHealthy`
- `channel.waitReady`
- `session.create`
- `thread.create`
- `workspace.writeSkill`

### エージェントターンアクション

- `agent.send`
- `agent.wait`
- `bus.injectInbound`
- `bus.injectOutbound`

### 設定およびランタイムアクション

- `config.get`
- `config.patch`
- `config.apply`
- `gateway.restart`
- `tools.effective`
- `skills.status`

### ファイルおよびアーティファクトアクション

- `file.write`
- `file.read`
- `file.delete`
- `file.touchTime`
- `artifact.captureGeneratedImage`
- `artifact.capturePath`

### メモリおよび cron アクション

- `memory.indexForce`
- `memory.searchCli`
- `doctor.memory.status`
- `cron.list`
- `cron.run`
- `cron.waitCompletion`
- `sessionTranscript.write`

### MCP アクション

- `mcp.callTool`

### アサーション

- `outbound.textIncludes`
- `outbound.inThread`
- `outbound.notInRoot`
- `tool.called`
- `tool.notPresent`
- `skill.visible`
- `skill.disabled`
- `file.contains`
- `memory.contains`
- `requestLog.matches`
- `sessionStore.matches`
- `cron.managedPresent`
- `artifact.exists`

## 変数とアーティファクト参照

DSL は、保存された出力と後続参照をサポートする必要があります。

現在のスイートの例:

- スレッドを作成し、その後 `threadId` を再利用する
- セッションを作成し、その後 `sessionKey` を再利用する
- 画像を生成し、次のターンでそのファイルを添付する
- ウェイクマーカー文字列を生成し、それが後で現れることをアサートする

必要な機能:

- `saveAs`
- `${vars.name}`
- `${artifacts.name}`
- パス、セッションキー、スレッド ID、マーカー、ツール出力の型付き参照

変数サポートがなければ、ハーネスはシナリオロジックを TypeScript に逆流させ続けることになります。

## エスケープハッチとして残すべきもの

フェーズ 1 で完全に純粋な宣言型ランナーを実現するのは現実的ではありません。

一部のシナリオは本質的にオーケストレーション負荷が高いです:

- memory dreaming sweep
- 設定適用後の再起動ウェイクアップ
- 再起動時の設定機能切り替え
- タイムスタンプ/パスによる生成画像アーティファクト解決
- discovery-report 評価

これらは、当面は明示的なカスタムハンドラーを使うべきです。

推奨ルール:

- 85-90% は宣言型
- 残りの難しい部分には明示的な `customHandler` ステップ
- 名前付きで文書化されたカスタムハンドラーのみ
- シナリオファイル内に匿名のインラインコードは禁止

これにより、進捗を維持しつつ汎用エンジンをクリーンに保てます。

## アーキテクチャ変更

### 現在

シナリオ markdown はすでに次の信頼できる情報源です:

- スイート実行
- ワークスペースブートストラップファイル
- QA Lab UI シナリオカタログ
- レポートメタデータ
- discovery prompts

生成される互換性要素:

- シードされたワークスペースには依然として `QA_KICKOFF_TASK.md` が含まれる
- シードされたワークスペースには依然として `QA_SCENARIO_PLAN.md` が含まれる
- シードされたワークスペースには теперь `QA_SCENARIOS.md` も含まれる

## リファクタリング計画

### フェーズ 1: ローダーとスキーマ

完了。

- `qa/scenarios/index.md` を追加
- シナリオを `qa/scenarios/*.md` に分割
- 名前付き markdown YAML パック内容用のパーサーを追加
- zod でバリデーション
- パース済みパックを使うようコンシューマーを切り替え
- リポジトリレベルの `qa/seed-scenarios.json` と `qa/QA_KICKOFF_TASK.md` を削除

### フェーズ 2: 汎用エンジン

- `extensions/qa-lab/src/suite.ts` を次に分割:
  - loader
  - engine
  - action registry
  - assertion registry
  - custom handlers
- 既存のヘルパー関数はエンジン操作として維持

成果物:

- エンジンがシンプルな宣言型シナリオを実行する

まずは主に prompt + wait + assert で構成されるシナリオから始める:

- スレッド化されたフォローアップ
- 添付ファイルからの画像理解
- Skill の可視性と呼び出し
- チャネルベースライン

成果物:

- 汎用エンジン経由で出荷される、最初の実際の markdown 定義シナリオ

### フェーズ 4: 中程度のシナリオを移行

- 画像生成ラウンドトリップ
- チャネルコンテキストでのメモリツール
- セッションメモリランキング
- サブエージェントのハンドオフ
- サブエージェントのファンアウト統合

成果物:

- 変数、アーティファクト、ツールアサーション、request-log アサーションが実証される

### フェーズ 5: 難しいシナリオはカスタムハンドラーに残す

- memory dreaming sweep
- 設定適用後の再起動ウェイクアップ
- 再起動時の設定機能切り替え
- ランタイムインベントリドリフト

成果物:

- 同じ記述フォーマットだが、必要な箇所に明示的な custom-step ブロックを使う

### フェーズ 6: ハードコードされたシナリオマップを削除

パックのカバレッジが十分になったら:

- `extensions/qa-lab/src/suite.ts` からシナリオ固有の TypeScript 分岐の大半を削除

## Fake Slack / リッチメディア対応

現在の QA バスは text-first です。

関連ファイル:

- `extensions/qa-channel/src/protocol.ts`
- `extensions/qa-lab/src/bus-state.ts`
- `extensions/qa-lab/src/bus-queries.ts`
- `extensions/qa-lab/src/bus-server.ts`
- `extensions/qa-lab/web/src/ui-render.ts`

今日の QA バスが対応しているもの:

- テキスト
- リアクション
- スレッド

まだインラインメディア添付ファイルはモデル化されていません。

### 必要なトランスポート契約

汎用的な QA バス添付ファイルモデルを追加します:

```ts
type QaBusAttachment = {
  id: string;
  kind: "image" | "video" | "audio" | "file";
  mimeType: string;
  fileName?: string;
  inline?: boolean;
  url?: string;
  contentBase64?: string;
  width?: number;
  height?: number;
  durationMs?: number;
  altText?: string;
  transcript?: string;
};
```

そのうえで `attachments?: QaBusAttachment[]` を次に追加します:

- `QaBusMessage`
- `QaBusInboundMessageInput`
- `QaBusOutboundMessageInput`

### なぜまず汎用化なのか

Slack 専用のメディアモデルを作らないでください。

代わりに:

- 1 つの汎用 QA トランスポートモデル
- その上に複数のレンダラー
  - 現在の QA Lab チャット
  - 将来の fake Slack web
  - その他の fake transport views

これによりロジックの重複を防ぎ、メディアシナリオをトランスポート非依存に保てます。

### 必要な UI 作業

QA UI を更新して次を描画します:

- インライン画像プレビュー
- インライン音声プレーヤー
- インライン動画プレーヤー
- ファイル添付チップ

現在の UI はすでにスレッドとリアクションを描画できるため、添付ファイル描画は同じメッセージカードモデルに積み重ねられるはずです。

### メディアトランスポートによって可能になるシナリオ作業

添付ファイルが QA バスを流れるようになれば、より豊かな fake-chat シナリオを追加できます:

- fake Slack でのインライン画像返信
- 音声添付ファイルの理解
- 動画添付ファイルの理解
- 混在添付ファイルの順序
- メディアを保持したスレッド返信

## 推奨事項

次の実装チャンクは、次にするべきです:

1. markdown シナリオローダー + zod スキーマを追加
2. markdown から現在のカタログを生成
3. まずいくつかのシンプルなシナリオを移行
4. 汎用 QA バス添付ファイル対応を追加
5. QA UI でインライン画像を描画
6. その後、音声と動画へ拡張

これは、両方の目標を実証する最小の道筋です:

- 汎用的な markdown 定義 QA
- より豊かな fake messaging surfaces

## 未解決の質問

- シナリオファイルで、変数補間付きの埋め込み markdown プロンプトテンプレートを許可するかどうか
- setup/cleanup を名前付きセクションにするか、単なる順序付きアクションリストにするか
- アーティファクト参照をスキーマ上で強く型付けするか、文字列ベースにするか
- カスタムハンドラーを 1 つのレジストリに置くか、surface ごとのレジストリにするか
- 移行期間中、生成される JSON 互換性ファイルを引き続きチェックインしておくべきかどうか
