---
read_when:
    - メモリの仕組みを理解したい場合
    - どのメモリファイルに書き込むべきかを知りたい場合
summary: OpenClawがセッションをまたいで物事を記憶する仕組み
title: メモリの概要
x-i18n:
    generated_at: "2026-04-15T14:40:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# メモリの概要

OpenClawは、エージェントのワークスペース内に**プレーンなMarkdownファイル**を書き込むことで物事を記憶します。モデルが「記憶」するのは、ディスクに保存された内容だけです。隠れた状態はありません。

## 仕組み

エージェントには、メモリに関連する3つのファイルがあります。

- **`MEMORY.md`** -- 長期メモリ。永続的な事実、設定、決定事項。すべてのDMセッションの開始時に読み込まれます。
- **`memory/YYYY-MM-DD.md`** -- 日次ノート。継続中のコンテキストと観察結果。今日と昨日のノートは自動的に読み込まれます。
- **`DREAMS.md`** (任意) -- 人間が確認するためのDream DiaryとDreamingスイープの要約。根拠のある履歴バックフィルのエントリも含まれます。

これらのファイルはエージェントのワークスペース内にあります（デフォルトは`~/.openclaw/workspace`）。

<Tip>
エージェントに何かを覚えてほしい場合は、単にこう頼んでください: 「TypeScriptを好むことを覚えておいて。」すると、適切なファイルに書き込まれます。
</Tip>

## メモリツール

エージェントには、メモリを扱うための2つのツールがあります。

- **`memory_search`** -- 元の表現と異なっていても、セマンティック検索を使って関連ノートを見つけます。
- **`memory_get`** -- 特定のメモリファイルまたは行範囲を読み取ります。

どちらのツールも、アクティブなメモリPlugin（デフォルト: `memory-core`）によって提供されます。

## Memory WikiコンパニオンPlugin

永続メモリを単なる生ノートではなく、保守されたナレッジベースのように振る舞わせたい場合は、バンドルされている`memory-wiki` Pluginを使ってください。

`memory-wiki`は、永続的な知識を次の要素を備えたwiki vaultにコンパイルします。

- 決定論的なページ構造
- 構造化された主張と証拠
- 矛盾と鮮度の追跡
- 生成されるダッシュボード
- エージェント/ランタイム利用者向けのコンパイル済みダイジェスト
- `wiki_search`、`wiki_get`、`wiki_apply`、`wiki_lint`のようなwikiネイティブツール

これはアクティブなメモリPluginを置き換えるものではありません。アクティブなメモリPluginは引き続き想起、昇格、Dreamingを担います。`memory-wiki`は、その隣に来歴情報が豊富な知識レイヤーを追加します。

詳しくは[Memory Wiki](/ja-JP/plugins/memory-wiki)を参照してください。

## メモリ検索

埋め込みプロバイダーが設定されている場合、`memory_search`は**ハイブリッド検索**を使用します。これは、ベクトル類似性（意味的な近さ）とキーワード一致（IDやコードシンボルのような正確な用語）を組み合わせる方式です。サポートされている任意のプロバイダーのAPIキーがあれば、すぐに利用できます。

<Info>
OpenClawは、利用可能なAPIキーから埋め込みプロバイダーを自動検出します。OpenAI、Gemini、Voyage、またはMistralのキーが設定されていれば、メモリ検索は自動的に有効になります。
</Info>

検索の仕組み、調整オプション、プロバイダー設定の詳細については、[Memory Search](/ja-JP/concepts/memory-search)を参照してください。

## メモリバックエンド

<CardGroup cols={3}>
<Card title="組み込み（デフォルト）" icon="database" href="/ja-JP/concepts/memory-builtin">
SQLiteベース。キーワード検索、ベクトル類似性、ハイブリッド検索がそのまま使えます。追加の依存関係はありません。
</Card>
<Card title="QMD" icon="search" href="/ja-JP/concepts/memory-qmd">
ローカルファーストのサイドカーで、再ランキング、クエリ拡張、ワークスペース外のディレクトリをインデックスできる機能を備えています。
</Card>
<Card title="Honcho" icon="brain" href="/ja-JP/concepts/memory-honcho">
ユーザーモデリング、セマンティック検索、マルチエージェント認識を備えた、AIネイティブなセッション横断メモリ。Pluginをインストールします。
</Card>
</CardGroup>

## ナレッジwikiレイヤー

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/ja-JP/plugins/memory-wiki">
永続メモリを、主張、ダッシュボード、ブリッジモード、Obsidian互換ワークフローを備えた、来歴情報が豊富なwiki vaultにコンパイルします。
</Card>
</CardGroup>

## 自動メモリフラッシュ

[Compaction](/ja-JP/concepts/compaction)が会話を要約する前に、OpenClawは重要なコンテキストをメモリファイルに保存するようエージェントに促すサイレントターンを実行します。これはデフォルトで有効になっており、何か設定する必要はありません。

<Tip>
メモリフラッシュは、Compaction中のコンテキスト喪失を防ぎます。会話内にまだファイルへ書き込まれていない重要な事実がある場合、それらは要約が行われる前に自動的に保存されます。
</Tip>

## Dreaming

Dreamingは、メモリのための任意のバックグラウンド統合パスです。短期シグナルを収集し、候補をスコアリングし、適格な項目だけを長期メモリ（`MEMORY.md`）へ昇格させます。

これは、長期メモリのシグナル密度を高く保つよう設計されています。

- **オプトイン**: デフォルトでは無効です。
- **スケジュール実行**: 有効にすると、`memory-core`は完全なDreamingスイープ用の定期的なCronジョブを1つ自動管理します。
- **しきい値判定**: 昇格には、スコア、想起頻度、クエリ多様性の各ゲートを通過する必要があります。
- **レビュー可能**: フェーズ要約と日誌エントリは、人間が確認できるよう`DREAMS.md`に書き込まれます。

フェーズの動作、スコアリングシグナル、Dream Diaryの詳細については、[Dreaming](/ja-JP/concepts/dreaming)を参照してください。

## 根拠のあるバックフィルとライブ昇格

Dreamingシステムには、現在2つの密接に関連したレビュー経路があります。

- **ライブDreaming**は、`memory/.dreams/`配下の短期Dreamingストアを使って動作し、通常のディープフェーズが何を`MEMORY.md`へ昇格できるか判断する際に使われます。
- **根拠のあるバックフィル**は、過去の`memory/YYYY-MM-DD.md`ノートを独立した日次ファイルとして読み取り、構造化されたレビュー出力を`DREAMS.md`に書き込みます。

根拠のあるバックフィルは、古いノートを再生して、システムが何を永続的と見なすかを`MEMORY.md`を手動編集せずに確認したい場合に便利です。

次のように使用した場合:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

根拠のある永続候補は直接昇格されません。代わりに、通常のディープフェーズがすでに使用している同じ短期Dreamingストアにステージされます。つまり、次のことを意味します。

- `DREAMS.md`は引き続き人間向けのレビュー画面です。
- 短期ストアは引き続きマシン向けのランキング画面です。
- `MEMORY.md`には引き続きディープ昇格によってのみ書き込まれます。

再生が有用でなかったと判断した場合は、通常の日誌エントリや通常の想起状態に触れることなく、ステージされたアーティファクトを削除できます。

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # インデックスの状態とプロバイダーを確認
openclaw memory search "query"  # コマンドラインから検索
openclaw memory index --force   # インデックスを再構築
```

## さらに読む

- [Builtin Memory Engine](/ja-JP/concepts/memory-builtin) -- デフォルトのSQLiteバックエンド
- [QMD Memory Engine](/ja-JP/concepts/memory-qmd) -- 高度なローカルファーストのサイドカー
- [Honcho Memory](/ja-JP/concepts/memory-honcho) -- AIネイティブなセッション横断メモリ
- [Memory Wiki](/ja-JP/plugins/memory-wiki) -- コンパイル済みナレッジvaultとwikiネイティブツール
- [Memory Search](/ja-JP/concepts/memory-search) -- 検索パイプライン、プロバイダー、調整
- [Dreaming](/ja-JP/concepts/dreaming) -- 短期想起から長期メモリへのバックグラウンド昇格
- [Memory configuration reference](/ja-JP/reference/memory-config) -- すべての設定項目
- [Compaction](/ja-JP/concepts/compaction) -- Compactionがメモリとどう相互作用するか
