---
read_when:
    - 単なる MEMORY.md ノートを超える永続的な知識が必要な場合
    - バンドルされた memory-wiki plugin を設定している場合
    - wiki_search、wiki_get、または bridge モードを理解したい場合
summary: 'memory-wiki: 出典、主張、ダッシュボード、bridge モードを備えたコンパイル済みナレッジボールト'
title: Memory Wiki
x-i18n:
    generated_at: "2026-04-08T04:42:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: b78dd6a4ef4451dae6b53197bf0c7c2a2ba846b08e4a3a93c1026366b1598d82
    source_path: plugins/memory-wiki.md
    workflow: 15
---

# Memory Wiki

`memory-wiki` は、永続メモリをコンパイル済みのナレッジボールトに変換するバンドルされた plugin です。

これはアクティブな memory plugin を**置き換えるものではありません**。アクティブな memory plugin は引き続き、想起、昇格、インデックス作成、dreaming を担います。`memory-wiki` はその隣に位置し、永続的な知識を、決定論的なページ、構造化された主張、出典、ダッシュボード、機械可読なダイジェストを備えた、たどれる wiki にコンパイルします。

メモリを Markdown ファイルの山というより、維持管理された知識レイヤーのように扱いたい場合に使います。

## 追加されるもの

- 決定論的なページレイアウトを持つ専用 wiki ボールト
- 単なる散文ではない、構造化された主張と証拠のメタデータ
- ページ単位の出典、信頼度、矛盾、未解決の疑問
- agent/runtime コンシューマー向けのコンパイル済みダイジェスト
- wiki ネイティブな search/get/apply/lint ツール
- アクティブな memory plugin から公開アーティファクトを取り込むオプションの bridge モード
- オプションの Obsidian 対応レンダーモードと CLI 統合

## メモリとの関係

分担は次のように考えるとわかりやすいです。

| レイヤー                                                | 担当                                                                                       |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| アクティブな memory plugin (`memory-core`, QMD, Honcho など) | 想起、セマンティック検索、昇格、dreaming、メモリ runtime                               |
| `memory-wiki`                                           | コンパイル済み wiki ページ、出典が豊富な統合、ダッシュボード、wiki 固有の search/get/apply |

アクティブな memory plugin が共有想起アーティファクトを公開している場合、OpenClaw は `memory_search corpus=all` で両レイヤーを一度に検索できます。

wiki 固有のランキング、出典、またはページへの直接アクセスが必要な場合は、代わりに wiki ネイティブのツールを使ってください。

## ボールトモード

`memory-wiki` は 3 つのボールトモードをサポートします。

### `isolated`

独自のボールト、独自のソース、`memory-core` への依存なし。

wiki をそれ自体でキュレートされた知識ストアにしたい場合に使います。

### `bridge`

公開された plugin SDK の継ぎ目を通じて、アクティブな memory plugin から公開メモリアーティファクトと memory event を読み取ります。

非公開の plugin 内部実装に踏み込まずに、memory plugin がエクスポートしたアーティファクトを wiki でコンパイルして整理したい場合に使います。

bridge モードでは次をインデックスできます。

- エクスポートされたメモリアーティファクト
- dream レポート
- daily note
- memory ルートファイル
- memory event ログ

### `unsafe-local`

ローカルの非公開パスに対する、同一マシン専用の明示的なエスケープハッチです。

このモードは意図的に実験的で、移植性がありません。信頼境界を理解しており、bridge モードでは提供できないローカルファイルシステムアクセスが明確に必要な場合にのみ使ってください。

## ボールトレイアウト

plugin は次のようなボールトを初期化します。

```text
<vault>/
  AGENTS.md
  WIKI.md
  index.md
  inbox.md
  entities/
  concepts/
  syntheses/
  sources/
  reports/
  _attachments/
  _views/
  .openclaw-wiki/
```

管理対象のコンテンツは生成ブロック内に保持されます。人間が書いたノートブロックは保持されます。

主なページグループは次のとおりです。

- `sources/`: 取り込んだ原資料と bridge に支えられたページ
- `entities/`: 永続的なもの、人、システム、プロジェクト、オブジェクト
- `concepts/`: アイデア、抽象概念、パターン、ポリシー
- `syntheses/`: コンパイル済みの要約と保守されたロールアップ
- `reports/`: 生成されたダッシュボード

## 構造化された主張と証拠

ページには、自由形式のテキストだけでなく、構造化された `claims` frontmatter を持たせることができます。

各主張には次を含めることができます。

- `id`
- `text`
- `status`
- `confidence`
- `evidence[]`
- `updatedAt`

証拠エントリには次を含めることができます。

- `sourceId`
- `path`
- `lines`
- `weight`
- `note`
- `updatedAt`

これにより、wiki は受動的なノート置き場というより、信念レイヤーのように振る舞います。主張は追跡、採点、異議申し立て、そしてソースへの解決ができます。

## コンパイルパイプライン

コンパイルステップでは wiki ページを読み取り、要約を正規化し、安定した機械向けアーティファクトを次に出力します。

- `.openclaw-wiki/cache/agent-digest.json`
- `.openclaw-wiki/cache/claims.jsonl`

これらのダイジェストがあることで、agents や runtime コードは Markdown ページをスクレイプしなくて済みます。

コンパイル済み出力は、次にも利用されます。

- search/get フロー向けの初回 wiki インデックス作成
- claim id から所有ページへの逆引き
- コンパクトなプロンプト補足
- レポート/ダッシュボード生成

## ダッシュボードとヘルスレポート

`render.createDashboards` が有効な場合、コンパイルは `reports/` 配下でダッシュボードを維持します。

組み込みレポートは次のとおりです。

- `reports/open-questions.md`
- `reports/contradictions.md`
- `reports/low-confidence.md`
- `reports/claim-health.md`
- `reports/stale-pages.md`

これらのレポートは、次のようなものを追跡します。

- 矛盾メモのクラスター
- 競合する主張のクラスター
- 構造化された証拠が不足している主張
- 低信頼度のページと主張
- 古い、または鮮度不明の情報
- 未解決の疑問があるページ

## 検索と取得

`memory-wiki` は 2 つの検索バックエンドをサポートします。

- `shared`: 利用可能な場合は共有メモリ検索フローを使う
- `local`: wiki をローカルで検索する

また、3 つの corpus をサポートします。

- `wiki`
- `memory`
- `all`

重要な動作:

- `wiki_search` と `wiki_get` は、可能な場合はコンパイル済みダイジェストを最初のパスとして使います
- claim id は所有ページへ解決できます
- 異議あり / 古い / 新しい主張がランキングに影響します
- 出典ラベルは結果に引き継がれる場合があります

実用的なルール:

- 広く想起したい場合は `memory_search corpus=all` を使う
- wiki 固有のランキング、出典、またはページ単位の信念構造を重視する場合は `wiki_search` + `wiki_get` を使う

## Agent ツール

plugin は次のツールを登録します。

- `wiki_status`
- `wiki_search`
- `wiki_get`
- `wiki_apply`
- `wiki_lint`

それぞれの役割:

- `wiki_status`: 現在のボールトモード、健全性、Obsidian CLI の利用可否
- `wiki_search`: wiki ページを検索し、設定されていれば共有メモリ corpus も検索する
- `wiki_get`: id/path で wiki ページを読み取り、失敗した場合は共有メモリ corpus にフォールバックする
- `wiki_apply`: 自由形式のページ編集なしで、限定的な統合/メタデータ変更を行う
- `wiki_lint`: 構造チェック、出典の欠落、矛盾、未解決の疑問

plugin はさらに、非排他的な memory corpus supplement も登録するため、アクティブな memory plugin が corpus 選択をサポートしていれば、共有の `memory_search` と `memory_get` から wiki にアクセスできます。

## プロンプトとコンテキストの動作

`context.includeCompiledDigestPrompt` が有効な場合、メモリプロンプトセクションには `agent-digest.json` からのコンパクトなコンパイル済みスナップショットが追加されます。

そのスナップショットは意図的に小さく、高シグナルです。

- 上位ページのみ
- 上位主張のみ
- 矛盾数
- 疑問数
- 信頼度 / 鮮度の修飾子

これはプロンプト形状を変えるためオプトインです。主に、メモリ補足を明示的に利用する context engine やレガシーなプロンプト組み立てで役立ちます。

## 設定

設定は `plugins.entries.memory-wiki.config` に置きます。

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "isolated",
          vault: {
            path: "~/.openclaw/wiki/main",
            renderMode: "obsidian",
          },
          obsidian: {
            enabled: true,
            useOfficialCli: true,
            vaultName: "OpenClaw Wiki",
            openAfterWrites: false,
          },
          bridge: {
            enabled: false,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          ingest: {
            autoCompile: true,
            maxConcurrentJobs: 1,
            allowUrlIngest: true,
          },
          search: {
            backend: "shared",
            corpus: "wiki",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
          render: {
            preserveHumanBlocks: true,
            createBacklinks: true,
            createDashboards: true,
          },
        },
      },
    },
  },
}
```

主な切り替え項目:

- `vaultMode`: `isolated`、`bridge`、`unsafe-local`
- `vault.renderMode`: `native` または `obsidian`
- `bridge.readMemoryArtifacts`: アクティブな memory plugin の公開アーティファクトを取り込む
- `bridge.followMemoryEvents`: bridge モードで event ログを含める
- `search.backend`: `shared` または `local`
- `search.corpus`: `wiki`、`memory`、または `all`
- `context.includeCompiledDigestPrompt`: コンパクトなダイジェストスナップショットをメモリプロンプトセクションに追加する
- `render.createBacklinks`: 決定論的な関連ブロックを生成する
- `render.createDashboards`: ダッシュボードページを生成する

## CLI

`memory-wiki` はトップレベルの CLI surface も公開します。

```bash
openclaw wiki status
openclaw wiki doctor
openclaw wiki init
openclaw wiki ingest ./notes/alpha.md
openclaw wiki compile
openclaw wiki lint
openclaw wiki search "alpha"
openclaw wiki get entity.alpha
openclaw wiki apply synthesis "Alpha Summary" --body "..." --source-id source.alpha
openclaw wiki bridge import
openclaw wiki obsidian status
```

完全なコマンドリファレンスは [CLI: wiki](/cli/wiki) を参照してください。

## Obsidian サポート

`vault.renderMode` が `obsidian` の場合、plugin は Obsidian 対応の Markdown を書き出し、オプションで公式の `obsidian` CLI を使用できます。

サポートされるワークフローには次が含まれます。

- ステータスの確認
- ボールト検索
- ページを開く
- Obsidian コマンドを呼び出す
- daily note に移動する

これはオプションです。wiki は Obsidian なしでも native モードで引き続き動作します。

## 推奨ワークフロー

1. 想起 / 昇格 / dreaming には既存のアクティブな memory plugin を使い続けます。
2. `memory-wiki` を有効にします。
3. bridge モードを明確に必要としない限り、`isolated` モードから始めます。
4. 出典が重要なときは `wiki_search` / `wiki_get` を使います。
5. 限定的な統合やメタデータ更新には `wiki_apply` を使います。
6. 意味のある変更の後には `wiki_lint` を実行します。
7. 古さや矛盾の可視性が必要ならダッシュボードを有効にします。

## 関連ドキュメント

- [Memory Overview](/ja-JP/concepts/memory)
- [CLI: memory](/cli/memory)
- [CLI: wiki](/cli/wiki)
- [Plugin SDK overview](/ja-JP/plugins/sdk-overview)
