---
read_when:
    - メモリの仕組みを理解したい
    - どのメモリファイルに書き込むべきか知りたい
summary: OpenClaw がセッションをまたいで物事を記憶する仕組み
title: メモリの概要
x-i18n:
    generated_at: "2026-04-08T04:42:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3bb8552341b0b651609edaaae826a22fdc535d240aed4fad4af4b069454004af
    source_path: concepts/memory.md
    workflow: 15
---

# メモリの概要

OpenClaw は、エージェントのワークスペース内に**プレーンな Markdown ファイル**を書き込むことで物事を記憶します。モデルが「記憶」するのはディスクに保存された内容だけであり、隠れた状態はありません。

## 仕組み

エージェントには、メモリに関連する 3 つのファイルがあります。

- **`MEMORY.md`** -- 長期メモリ。永続的な事実、設定、判断を保存します。すべての DM セッションの開始時に読み込まれます。
- **`memory/YYYY-MM-DD.md`** -- 日次ノート。継続中のコンテキストと観察内容を保存します。今日と昨日のノートは自動的に読み込まれます。
- **`DREAMS.md`** (実験的、任意) -- 人間が確認するための Dream Diary と dreaming sweep の要約です。

これらのファイルはエージェントのワークスペース（デフォルトは `~/.openclaw/workspace`）にあります。

<Tip>
エージェントに何かを覚えておいてほしい場合は、単にこう頼んでください: 「TypeScript を好むことを覚えておいて。」すると、適切なファイルに書き込まれます。
</Tip>

## メモリツール

エージェントには、メモリを扱うための 2 つのツールがあります。

- **`memory_search`** -- 元の表現と語句が異なる場合でも、セマンティック検索を使って関連するノートを見つけます。
- **`memory_get`** -- 特定のメモリファイルまたは行範囲を読み取ります。

どちらのツールも、アクティブなメモリ plugin（デフォルト: `memory-core`）によって提供されます。

## Memory Wiki コンパニオン plugin

永続メモリを単なる生のノートではなく、維持管理されたナレッジベースのように扱いたい場合は、同梱の `memory-wiki` plugin を使用してください。

`memory-wiki` は、永続的な知識を次の要素を持つ wiki vault にコンパイルします。

- 決定論的なページ構造
- 構造化された主張と根拠
- 矛盾と鮮度の追跡
- 生成されるダッシュボード
- エージェント/ランタイム利用者向けにコンパイルされたダイジェスト
- `wiki_search`、`wiki_get`、`wiki_apply`、`wiki_lint` などの wiki ネイティブなツール

これはアクティブなメモリ plugin を置き換えるものではありません。アクティブなメモリ plugin は引き続き、想起、昇格、dreaming を管理します。`memory-wiki` は、その横に出所情報が豊富な知識レイヤーを追加します。

詳しくは [Memory Wiki](/ja-JP/plugins/memory-wiki) を参照してください。

## メモリ検索

埋め込みプロバイダーが設定されている場合、`memory_search` は**ハイブリッド検索**を使用します。これは、ベクトル類似度（意味的な近さ）とキーワード一致（ID やコードシンボルのような正確な用語）を組み合わせるものです。対応プロバイダーのいずれかの API キーがあれば、そのまま利用できます。

<Info>
OpenClaw は、利用可能な API キーから埋め込みプロバイダーを自動検出します。OpenAI、Gemini、Voyage、または Mistral のキーが設定されていれば、メモリ検索は自動的に有効になります。
</Info>

検索の仕組み、調整オプション、プロバイダーの設定について詳しくは、[Memory Search](/ja-JP/concepts/memory-search) を参照してください。

## メモリバックエンド

<CardGroup cols={3}>
<Card title="内蔵（デフォルト）" icon="database" href="/ja-JP/concepts/memory-builtin">
SQLite ベース。キーワード検索、ベクトル類似度、ハイブリッド検索がそのまま使えます。追加の依存関係は不要です。
</Card>
<Card title="QMD" icon="search" href="/ja-JP/concepts/memory-qmd">
ローカルファーストのサイドカー。再ランキング、クエリ拡張、ワークスペース外のディレクトリのインデックス化に対応します。
</Card>
<Card title="Honcho" icon="brain" href="/ja-JP/concepts/memory-honcho">
ユーザーモデリング、セマンティック検索、マルチエージェント認識を備えた、AI ネイティブなクロスセッションメモリ。plugin のインストールが必要です。
</Card>
</CardGroup>

## ナレッジ wiki レイヤー

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/ja-JP/plugins/memory-wiki">
永続メモリを、主張、ダッシュボード、bridge mode、Obsidian に適したワークフローを備えた、出所情報が豊富な wiki vault にコンパイルします。
</Card>
</CardGroup>

## 自動メモリフラッシュ

[compaction](/ja-JP/concepts/compaction) が会話を要約する前に、OpenClaw はエージェントに重要なコンテキストをメモリファイルへ保存するよう促すサイレントターンを実行します。これはデフォルトで有効で、設定は不要です。

<Tip>
メモリフラッシュは、compaction 中のコンテキスト損失を防ぎます。会話の中に重要な事実があり、まだファイルに書き込まれていない場合は、要約が行われる前に自動的に保存されます。
</Tip>

## Dreaming（実験的）

Dreaming は、メモリのための任意のバックグラウンド統合処理です。短期的なシグナルを収集し、候補をスコアリングし、基準を満たした項目だけを長期メモリ（`MEMORY.md`）に昇格させます。

これは、長期メモリのシグナル品質を高く保つよう設計されています。

- **オプトイン**: デフォルトでは無効です。
- **スケジュール実行**: 有効にすると、`memory-core` が完全な dreaming sweep 用の定期 cron ジョブを 1 つ自動管理します。
- **しきい値判定**: 昇格には、スコア、想起頻度、クエリ多様性のゲートを通過する必要があります。
- **レビュー可能**: フェーズ要約と日記エントリは、人間が確認できるよう `DREAMS.md` に書き込まれます。

フェーズの挙動、スコアリングシグナル、Dream Diary の詳細については、[Dreaming (experimental)](/ja-JP/concepts/dreaming) を参照してください。

## CLI

```bash
openclaw memory status          # インデックスの状態とプロバイダーを確認
openclaw memory search "query"  # コマンドラインから検索
openclaw memory index --force   # インデックスを再構築
```

## さらに読む

- [Builtin Memory Engine](/ja-JP/concepts/memory-builtin) -- デフォルトの SQLite バックエンド
- [QMD Memory Engine](/ja-JP/concepts/memory-qmd) -- 高度なローカルファーストのサイドカー
- [Honcho Memory](/ja-JP/concepts/memory-honcho) -- AI ネイティブなクロスセッションメモリ
- [Memory Wiki](/ja-JP/plugins/memory-wiki) -- コンパイル済みナレッジ vault と wiki ネイティブなツール
- [Memory Search](/ja-JP/concepts/memory-search) -- 検索パイプライン、プロバイダー、調整
- [Dreaming (experimental)](/ja-JP/concepts/dreaming) -- 短期的な想起から長期メモリへのバックグラウンド昇格
- [Memory configuration reference](/ja-JP/reference/memory-config) -- すべての設定項目
- [Compaction](/ja-JP/concepts/compaction) -- compaction がメモリとどう相互作用するか
