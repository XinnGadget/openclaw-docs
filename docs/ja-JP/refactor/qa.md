---
x-i18n:
    generated_at: "2026-04-08T02:19:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0e156cc8e2fe946a0423862f937754a7caa1fe7e6863b50a80bff49a1c86e1e8
    source_path: refactor/qa.md
    workflow: 15
---

# QAリファクタリング

ステータス: 基盤となる移行は完了しました。

## 目標

OpenClawのQAを分割定義モデルから単一の信頼できる情報源へ移行します:

- シナリオメタデータ
- モデルに送信されるプロンプト
- セットアップとクリーンアップ
- ハーネスロジック
- アサーションと成功条件
- アーティファクトとレポートのヒント

目指す最終状態は、TypeScriptに大半の動作をハードコードするのではなく、
強力なシナリオ定義ファイルを読み込む汎用QAハーネスです。

## 現在の状態

現在の主要な信頼できる情報源は `qa/scenarios.md` にあります。

実装済み:

- `qa/scenarios.md`
  - 正規のQAパック
  - operator identity
  - キックオフミッション
  - シナリオメタデータ
  - ハンドラーバインディング
- `extensions/qa-lab/src/scenario-catalog.ts`
  - Markdownパックパーサー + zod検証
- `extensions/qa-lab/src/qa-agent-bootstrap.ts`
  - Markdownパックからのプラン描画
- `extensions/qa-lab/src/qa-agent-workspace.ts`
  - 互換ファイルと `QA_SCENARIOS.md` を生成するシード
- `extensions/qa-lab/src/suite.ts`
  - Markdownで定義されたハンドラーバインディングを通じて実行可能なシナリオを選択
- QAバスプロトコル + UI
  - 画像/動画/音声/ファイル表示向けの汎用インライン添付ファイル

残っている分割サーフェス:

- `extensions/qa-lab/src/suite.ts`
  - 依然として実行可能なカスタムハンドラーロジックの大半を所有
- `extensions/qa-lab/src/report.ts`
  - 依然としてランタイム出力からレポート構造を導出

そのため、信頼できる情報源の分割は修正されましたが、実行は依然として完全に宣言的というより、
主にハンドラーバックです。

## 実際のシナリオサーフェスの姿

現在のsuiteを読むと、いくつかの異なるシナリオクラスがあります。

### 単純なインタラクション

- チャネルベースライン
- DMベースライン
- スレッド化されたフォローアップ
- モデル切り替え
- 承認の完遂
- reaction/edit/delete

### 設定とランタイムの変更

- config patch によるskill無効化
- config apply による再起動ウェイクアップ
- config再起動による機能切り替え
- ランタイムインベントリ差分チェック

### ファイルシステムとリポジトリアサーション

- ソース/ドキュメント探索レポート
- Lobster Invaders のビルド
- 生成画像アーティファクトの検索

### メモリオーケストレーション

- メモリ再呼び出し
- チャネルコンテキストでのメモリツール
- メモリ失敗フォールバック
- セッションメモリランキング
- スレッドメモリ分離
- メモリdreaming sweep

### ツールとプラグイン統合

- MCP plugin-tools 呼び出し
- skill可視性
- skillホットインストール
- ネイティブ画像生成
- 画像ラウンドトリップ
- 添付ファイルからの画像理解

### マルチターンとマルチアクター

- subagent handoff
- subagent fanout synthesis
- 再起動復旧スタイルのフロー

これらのカテゴリはDSL要件を左右するため重要です。プロンプト + 期待テキストの
フラットな一覧だけでは不十分です。

## 方向性

### 単一の信頼できる情報源

作成対象の信頼できる情報源として `qa/scenarios.md` を使います。

このパックは次の状態を維持する必要があります:

- レビューで人間が読みやすい
- 機械が解析できる
- 次を駆動できるだけの十分な情報量がある:
  - suite実行
  - QA workspaceブートストラップ
  - QA Lab UIメタデータ
  - ドキュメント/探索プロンプト
  - レポート生成

### 推奨する作成形式

トップレベル形式としてMarkdownを使い、その中に構造化YAMLを入れます。

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
- 散文セクション
  - objective
  - notes
  - debugging hints
- フェンス付きYAMLブロック
  - setup
  - steps
  - assertions
  - cleanup

これにより次が得られます:

- 巨大なJSONより優れたPR可読性
- 純粋なYAMLより豊かなコンテキスト
- 厳密な解析とzod検証

生のJSONは、中間生成形式としてのみ許容されます。

## 提案するシナリオファイル形状

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

Verify generated media is reattached on the follow-up turn.

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
    Image generation check: generate a QA lighthouse image and summarize it in one short sentence.
- action: artifact.capture
  kind: generated-image
  promptSnippet: Image generation check
  saveAs: lighthouseImage
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Roundtrip image inspection check: describe the generated lighthouse attachment in one short sentence.
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

## DSLがカバーすべきランナー機能

現在のsuiteに基づくと、汎用ランナーはプロンプト実行以上のものを必要とします。

### 環境およびセットアップアクション

- `bus.reset`
- `gateway.waitHealthy`
- `channel.waitReady`
- `session.create`
- `thread.create`
- `workspace.writeSkill`

### agentターンアクション

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

### メモリおよびcronアクション

- `memory.indexForce`
- `memory.searchCli`
- `doctor.memory.status`
- `cron.list`
- `cron.run`
- `cron.waitCompletion`
- `sessionTranscript.write`

### MCPアクション

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

DSLは、保存された出力とその後の参照をサポートする必要があります。

現在のsuiteからの例:

- スレッドを作成し、その後 `threadId` を再利用する
- セッションを作成し、その後 `sessionKey` を再利用する
- 画像を生成し、次のターンでそのファイルを添付する
- wake marker文字列を生成し、それが後で現れることをアサートする

必要な機能:

- `saveAs`
- `${vars.name}`
- `${artifacts.name}`
- パス、セッションキー、thread id、marker、ツール出力向けの型付き参照

変数サポートがなければ、ハーネスはシナリオロジックをTypeScriptへ逆流させ続けます。

## エスケープハッチとして残すべきもの

フェーズ1で完全に純粋な宣言的ランナーを実現するのは現実的ではありません。

一部のシナリオは本質的にオーケストレーション負荷が高いです:

- メモリdreaming sweep
- config apply による再起動ウェイクアップ
- config再起動による機能切り替え
- タイムスタンプ/パスによる生成画像アーティファクト解決
- discovery-report 評価

これらは当面、明示的なカスタムハンドラーを使うべきです。

推奨ルール:

- 85〜90%は宣言的
- 残りの難しい部分には明示的な `customHandler` ステップ
- カスタムハンドラーは名前付きかつ文書化されたもののみ
- シナリオファイル内に匿名インラインコードは置かない

これにより、汎用エンジンをクリーンに保ちながら進展も可能になります。

## アーキテクチャ変更

### 現在

シナリオMarkdownはすでに次の信頼できる情報源です:

- suite実行
- workspaceブートストラップファイル
- QA Lab UIシナリオカタログ
- レポートメタデータ
- 探索プロンプト

生成される互換性:

- シード済みworkspaceには依然として `QA_KICKOFF_TASK.md` が含まれる
- シード済みworkspaceには依然として `QA_SCENARIO_PLAN.md` が含まれる
- シード済みworkspaceには現在 `QA_SCENARIOS.md` も含まれる

## リファクタリング計画

### フェーズ1: ローダーとスキーマ

完了。

- `qa/scenarios.md` を追加
- 名前付きMarkdown YAMLパック内容向けパーサーを追加
- zodで検証
- 利用側を解析済みパックへ切り替え
- リポジトリレベルの `qa/seed-scenarios.json` と `qa/QA_KICKOFF_TASK.md` を削除

### フェーズ2: 汎用エンジン

- `extensions/qa-lab/src/suite.ts` を次のように分割:
  - ローダー
  - エンジン
  - アクションレジストリ
  - アサーションレジストリ
  - カスタムハンドラー
- 既存のヘルパー関数はエンジン操作として維持

成果物:

- エンジンが単純な宣言的シナリオを実行する

まずは、主にプロンプト + 待機 + アサートで構成されるシナリオから始めます:

- スレッド化されたフォローアップ
- 添付ファイルからの画像理解
- skill可視性と呼び出し
- チャネルベースライン

成果物:

- 汎用エンジン経由で提供される、最初の実際のMarkdown定義シナリオ

### フェーズ4: 中程度のシナリオを移行

- 画像生成ラウンドトリップ
- チャネルコンテキストでのメモリツール
- セッションメモリランキング
- subagent handoff
- subagent fanout synthesis

成果物:

- 変数、アーティファクト、ツールアサーション、request-logアサーションが実証される

### フェーズ5: 難しいシナリオはカスタムハンドラーのまま維持

- メモリdreaming sweep
- config apply による再起動ウェイクアップ
- config再起動による機能切り替え
- ランタイムインベントリ差分

成果物:

- 同じ作成形式だが、必要に応じて明示的なカスタムステップブロックを使用

### フェーズ6: ハードコードされたシナリオマップを削除

パックのカバレッジが十分になったら:

- `extensions/qa-lab/src/suite.ts` から、シナリオ固有のTypeScript分岐の大半を削除

## Fake Slack / リッチメディア対応

現在のQAバスはテキスト優先です。

関連ファイル:

- `extensions/qa-channel/src/protocol.ts`
- `extensions/qa-lab/src/bus-state.ts`
- `extensions/qa-lab/src/bus-queries.ts`
- `extensions/qa-lab/src/bus-server.ts`
- `extensions/qa-lab/web/src/ui-render.ts`

現在のQAバスがサポートしているもの:

- テキスト
- reaction
- thread

まだインラインメディア添付はモデル化していません。

### 必要な転送コントラクト

汎用QAバス添付モデルを追加します:

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

その後、次に `attachments?: QaBusAttachment[]` を追加します:

- `QaBusMessage`
- `QaBusInboundMessageInput`
- `QaBusOutboundMessageInput`

### なぜ最初に汎用化するのか

Slack専用のメディアモデルを作らないでください。

代わりに:

- 1つの汎用QA転送モデル
- その上に複数のレンダラー
  - 現在のQA Labチャット
  - 将来のfake Slack web
  - その他のfake転送ビュー

これによりロジックの重複を防ぎ、メディアシナリオを転送非依存に保てます。

### 必要なUI作業

QA UIを更新して次を描画します:

- インライン画像プレビュー
- インライン音声プレーヤー
- インライン動画プレーヤー
- ファイル添付チップ

現在のUIはすでにthreadとreactionを描画できるため、添付描画は同じメッセージカードモデルの上に重ねられるはずです。

### メディア転送によって可能になるシナリオ作業

添付ファイルがQAバスを通って流れるようになれば、より豊かなfake-chatシナリオを追加できます:

- fake Slackでのインライン画像返信
- 音声添付理解
- 動画添付理解
- 混在する添付順序
- メディアを保持したスレッド返信

## 推奨

次の実装チャンクは次の順にするべきです:

1. Markdownシナリオローダー + zodスキーマを追加
2. Markdownから現在のカタログを生成
3. まずいくつかの単純なシナリオを移行
4. 汎用QAバス添付サポートを追加
5. QA UIでインライン画像を描画
6. その後、音声と動画へ拡張

これは、両方の目標を実証する最小の道筋です:

- 汎用のMarkdown定義QA
- より豊かなfakeメッセージングサーフェス

## 未解決の質問

- シナリオファイルで、変数補間付きの埋め込みMarkdownプロンプトテンプレートを許可するべきか
- setup/cleanup は名前付きセクションにするべきか、それとも単なる順序付きアクション一覧にするべきか
- アーティファクト参照はスキーマで強く型付けするべきか、それとも文字列ベースにするべきか
- カスタムハンドラーは1つのレジストリに置くべきか、それともサーフェスごとのレジストリにするべきか
- 移行中、生成されるJSON互換ファイルを引き続きチェックインしておくべきか
