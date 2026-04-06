---
read_when:
    - メモリの仕組みを理解したい
    - どのメモリファイルに書けばよいか知りたい
summary: OpenClaw がセッションをまたいでどのように記憶するか
title: メモリの概要
x-i18n:
    generated_at: "2026-04-06T03:06:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: d19d4fa9c4b3232b7a97f7a382311d2a375b562040de15e9fe4a0b1990b825e7
    source_path: concepts/memory.md
    workflow: 15
---

# メモリの概要

OpenClaw は、エージェントのワークスペース内に**プレーンな Markdown ファイル**を書き込むことで物事を記憶します。モデルが「記憶」できるのはディスクに保存されたものだけであり、隠れた状態はありません。

## 仕組み

エージェントには、メモリに関連する 3 つのファイルがあります。

- **`MEMORY.md`** -- 長期記憶。永続的な事実、好み、決定事項。すべての DM セッションの開始時に読み込まれます。
- **`memory/YYYY-MM-DD.md`** -- デイリーノート。継続中の文脈と観察事項。今日と昨日のノートは自動的に読み込まれます。
- **`DREAMS.md`**（実験的、任意） -- 人間が確認するための Dream Diary と dreaming sweep の要約。

これらのファイルはエージェントのワークスペース（デフォルトは `~/.openclaw/workspace`）にあります。

<Tip>
エージェントに何かを覚えていてほしい場合は、単にそう頼んでください: 「TypeScript を好むことを覚えておいて」。すると適切なファイルに書き込まれます。
</Tip>

## メモリツール

エージェントには、メモリを扱うための 2 つのツールがあります。

- **`memory_search`** -- 元の表現と語句が異なっていても、意味検索を使って関連するメモを見つけます。
- **`memory_get`** -- 特定のメモリファイルまたは行範囲を読み取ります。

どちらのツールも、アクティブなメモリプラグイン（デフォルト: `memory-core`）によって提供されます。

## メモリ検索

埋め込みプロバイダーが設定されている場合、`memory_search` は**ハイブリッド検索**を使います。これはベクトル類似度（意味的な近さ）とキーワード一致（ID やコードシンボルのような正確な語）を組み合わせるものです。サポートされている任意のプロバイダーの API キーがあれば、追加設定なしで動作します。

<Info>
OpenClaw は、利用可能な API キーから埋め込みプロバイダーを自動検出します。OpenAI、Gemini、Voyage、または Mistral のキーが設定されていれば、メモリ検索は自動的に有効になります。
</Info>

検索の仕組み、チューニングオプション、プロバイダー設定の詳細は、[メモリ検索](/ja-JP/concepts/memory-search) を参照してください。

## メモリバックエンド

<CardGroup cols={3}>
<Card title="Builtin（デフォルト）" icon="database" href="/ja-JP/concepts/memory-builtin">
SQLite ベース。キーワード検索、ベクトル類似度、ハイブリッド検索がそのまま使えます。追加の依存関係は不要です。
</Card>
<Card title="QMD" icon="search" href="/ja-JP/concepts/memory-qmd">
ローカルファーストのサイドカーで、再ランキング、クエリ拡張、ワークスペース外のディレクトリをインデックス化する機能を備えています。
</Card>
<Card title="Honcho" icon="brain" href="/ja-JP/concepts/memory-honcho">
ユーザーモデリング、意味検索、複数エージェント認識を備えた、AI ネイティブなクロスセッションメモリ。プラグインのインストールが必要です。
</Card>
</CardGroup>

## 自動メモリフラッシュ

[compaction](/ja-JP/concepts/compaction) が会話を要約する前に、OpenClaw は重要な文脈をメモリファイルに保存するようエージェントへ思い出させるサイレントターンを実行します。これはデフォルトで有効で、設定は不要です。

<Tip>
メモリフラッシュは、compaction 中のコンテキスト損失を防ぎます。会話の中に、まだファイルへ書き込まれていない重要な事実がある場合、要約が行われる前に自動的に保存されます。
</Tip>

## Dreaming（実験的）

Dreaming は、メモリのための任意のバックグラウンド統合処理です。短期的なシグナルを収集し、候補をスコアリングし、条件を満たした項目だけを長期記憶（`MEMORY.md`）へ昇格させます。

これは、長期記憶のシグナル対ノイズ比を高く保つよう設計されています。

- **オプトイン**: デフォルトでは無効です。
- **スケジュール実行**: 有効にすると、`memory-core` が完全な dreaming sweep のための定期 cron ジョブを 1 つ自動管理します。
- **しきい値あり**: 昇格は、スコア、想起頻度、クエリ多様性の各ゲートを通過する必要があります。
- **レビュー可能**: フェーズ要約と日誌エントリは、人間が確認できるよう `DREAMS.md` に書き込まれます。

フェーズの動作、スコアリングシグナル、Dream Diary の詳細は、[Dreaming（実験的）](/concepts/dreaming) を参照してください。

## CLI

```bash
openclaw memory status          # インデックスの状態とプロバイダーを確認
openclaw memory search "query"  # コマンドラインから検索
openclaw memory index --force   # インデックスを再構築
```

## さらに読む

- [Builtin Memory Engine](/ja-JP/concepts/memory-builtin) -- デフォルトの SQLite バックエンド
- [QMD Memory Engine](/ja-JP/concepts/memory-qmd) -- 高度なローカルファーストサイドカー
- [Honcho Memory](/ja-JP/concepts/memory-honcho) -- AI ネイティブなクロスセッションメモリ
- [Memory Search](/ja-JP/concepts/memory-search) -- 検索パイプライン、プロバイダー、チューニング
- [Dreaming（実験的）](/concepts/dreaming) -- 短期想起から長期記憶へのバックグラウンド昇格
- [メモリ設定リファレンス](/ja-JP/reference/memory-config) -- すべての設定項目
- [Compaction](/ja-JP/concepts/compaction) -- compaction がメモリとどう相互作用するか
