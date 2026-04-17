---
read_when:
    - 単なる `MEMORY.md` メモを超える永続的な知識が必要な場合
    - バンドルされた memory-wiki Plugin を設定している場合
    - '`wiki_search`、`wiki_get`、または bridge mode を理解したい場合'
summary: 'memory-wiki: 出典、主張、ダッシュボード、bridge mode を備えたコンパイル済みナレッジボールト'
title: Memory Wiki
x-i18n:
    generated_at: "2026-04-12T23:28:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 44d168a7096f744c56566ecac57499192eb101b4dd8a78e1b92f3aa0d6da3ad1
    source_path: plugins/memory-wiki.md
    workflow: 15
---

# Memory Wiki

`memory-wiki` は、永続的なメモリをコンパイル済みの
ナレッジボールトに変換するバンドルされた Plugin です。

これは active memory Plugin を置き換えるものでは**ありません**。active memory Plugin は引き続き、
recall、promotion、indexing、Dreaming を担当します。`memory-wiki` はそれと並んで動作し、
永続的な知識を、決定論的なページ、構造化された claims、出典、
ダッシュボード、機械可読な digest を備えた、たどれる wiki にコンパイルします。

メモリを Markdown ファイルの山のようにではなく、
保守された知識レイヤーのように振る舞わせたい場合に使ってください。

## 追加されるもの

- 決定論的なページレイアウトを持つ専用の wiki ボールト
- 単なる散文ではなく、構造化された claim と evidence のメタデータ
- ページ単位の出典、信頼度、矛盾、未解決の質問
- agent/runtime コンシューマー向けのコンパイル済み digest
- wiki ネイティブの search/get/apply/lint ツール
- active memory Plugin から公開 artifact を取り込む任意の bridge mode
- 任意の Obsidian フレンドリーな render mode と CLI 統合

## メモリとの関係

この分割は次のように考えてください:

| レイヤー                                                | 担当                                                                                       |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Active Memory Plugin (`memory-core`、QMD、Honcho など) | Recall、semantic search、promotion、Dreaming、memory runtime                               |
| `memory-wiki`                                           | コンパイル済み wiki ページ、出典が豊富な syntheses、ダッシュボード、wiki 固有の search/get/apply |

active memory Plugin が共有 recall artifact を公開している場合、OpenClaw は
`memory_search corpus=all` で両方のレイヤーを 1 回で検索できます。

wiki 固有の ranking、出典、または直接的なページアクセスが必要な場合は、
代わりに wiki ネイティブのツールを使用してください。

## 推奨ハイブリッドパターン

local-first セットアップ向けの強力なデフォルトは次のとおりです:

- recall と広範な semantic search 用の active memory backend としての QMD
- 永続的に統合された知識ページ用に `bridge` mode で動かす `memory-wiki`

この分割がうまく機能するのは、各レイヤーがそれぞれの役割に集中できるからです:

- QMD は raw note、session export、追加 collection を検索可能に保つ
- `memory-wiki` は安定した entity、claim、dashboard、source page をコンパイルする

実用上のルール:

- memory 全体に対して広く 1 回 recall したい場合は `memory_search` を使う
- 出典を意識した wiki 結果が欲しい場合は `wiki_search` と `wiki_get` を使う
- 共有検索で両方のレイヤーを横断したい場合は `memory_search corpus=all` を使う

bridge mode がエクスポートされた artifact を 0 件と報告する場合、active memory Plugin は
現時点ではまだ公開 bridge input を公開していません。まず `openclaw wiki doctor` を実行し、
その後 active memory Plugin が公開 artifact をサポートしていることを確認してください。

## ボールトモード

`memory-wiki` は 3 つのボールトモードをサポートしています:

### `isolated`

独自のボールト、独自のソース、`memory-core` への依存なし。

wiki を独自にキュレーションされた知識ストアとして使いたい場合に使用します。

### `bridge`

active memory Plugin から、公開された Plugin SDK seam を通じて
公開 memory artifact と memory event を読み取ります。

private な Plugin 内部実装に踏み込まずに、
memory Plugin がエクスポートした artifact を wiki でコンパイルして整理したい場合に使用します。

bridge mode では次を index 化できます:

- エクスポートされた memory artifact
- dream report
- daily note
- memory root file
- memory event log

### `unsafe-local`

ローカルの private path 向けの、明示的な同一マシン escape hatch。

このモードは意図的に実験的かつ非ポータブルです。trust boundary を理解しており、
bridge mode では提供できないローカル filesystem アクセスが特に必要な場合にのみ使用してください。

## ボールトレイアウト

Plugin は次のようなボールトを初期化します:

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

管理対象コンテンツは生成ブロック内に保持されます。人間の note ブロックは保持されます。

主なページグループは次のとおりです:

- `sources/`: 取り込まれた raw material と bridge ベースのページ
- `entities/`: 永続的な物、人、システム、プロジェクト、オブジェクト
- `concepts/`: アイデア、抽象概念、パターン、ポリシー
- `syntheses/`: コンパイル済み summary と保守された rollup
- `reports/`: 生成されたダッシュボード

## 構造化された claims と evidence

ページには自由形式の本文だけでなく、構造化された `claims` frontmatter を持たせることができます。

各 claim には次を含められます:

- `id`
- `text`
- `status`
- `confidence`
- `evidence[]`
- `updatedAt`

evidence エントリには次を含められます:

- `sourceId`
- `path`
- `lines`
- `weight`
- `note`
- `updatedAt`

これにより wiki は受動的なメモの集積ではなく、belief layer のように振る舞います。
claim は追跡、採点、異議申し立て、ソースへの解決が可能です。

## Compile pipeline

compile ステップは wiki ページを読み取り、summary を正規化し、
次の場所に安定した machine-facing artifact を出力します:

- `.openclaw-wiki/cache/agent-digest.json`
- `.openclaw-wiki/cache/claims.jsonl`

これらの digest が存在するのは、agent や runtime code が Markdown ページを
スクレイプしなくて済むようにするためです。

コンパイル済み出力は次にも使われます:

- search/get フロー向けの初回 wiki indexing
- claim id から所有ページへのルックアップ
- コンパクトな prompt supplement
- report/dashboard 生成

## ダッシュボードとヘルスレポート

`render.createDashboards` が有効な場合、compile は `reports/` 配下に
ダッシュボードを保守します。

組み込みレポートには次が含まれます:

- `reports/open-questions.md`
- `reports/contradictions.md`
- `reports/low-confidence.md`
- `reports/claim-health.md`
- `reports/stale-pages.md`

これらのレポートは次のようなものを追跡します:

- contradiction note cluster
- 競合する claim cluster
- 構造化された evidence が欠けている claim
- 信頼度が低いページと claim
- 古い、または鮮度不明のページ
- 未解決の質問があるページ

## Search と retrieval

`memory-wiki` は 2 つの search backend をサポートしています:

- `shared`: 利用可能な場合は共有 memory search フローを使う
- `local`: wiki をローカルで検索する

また、3 つの corpus をサポートしています:

- `wiki`
- `memory`
- `all`

重要な動作:

- `wiki_search` と `wiki_get` は、可能な場合はコンパイル済み digest を初回検索に使います
- claim id は所有ページへ解決できます
- contested/stale/fresh な claim は ranking に影響します
- provenance label は結果に残せます

実用上のルール:

- 広く 1 回 recall したい場合は `memory_search corpus=all` を使う
- wiki 固有の ranking、出典、またはページレベルの belief structure を重視する場合は `wiki_search` + `wiki_get` を使う

## agent ツール

Plugin は次のツールを登録します:

- `wiki_status`
- `wiki_search`
- `wiki_get`
- `wiki_apply`
- `wiki_lint`

それぞれの役割:

- `wiki_status`: 現在のボールトモード、ヘルス、Obsidian CLI の利用可否
- `wiki_search`: wiki ページを検索し、設定されている場合は共有 memory corpus も検索する
- `wiki_get`: id/path で wiki ページを読み取り、必要に応じて共有 memory corpus にフォールバックする
- `wiki_apply`: 自由形式のページ編集ではなく、限定的な synthesis/metadata 変更を行う
- `wiki_lint`: 構造チェック、出典の欠落、矛盾、未解決の質問を確認する

Plugin はさらに、非排他的な memory corpus supplement を登録するため、
active memory Plugin が corpus selection をサポートしていれば、
共有の `memory_search` と `memory_get` から wiki に到達できます。

## prompt と context の動作

`context.includeCompiledDigestPrompt` が有効な場合、memory prompt セクションには
`agent-digest.json` からのコンパクトなコンパイル済みスナップショットが追加されます。

このスナップショットは意図的に小さく、高シグナルです:

- 上位ページのみ
- 上位 claim のみ
- contradiction 件数
- question 件数
- confidence/freshness 修飾子

これは prompt の形状を変えるためオプトインであり、主に
memory supplement を明示的に消費する context engine や
従来の prompt assembly に役立ちます。

## 設定

設定は `plugins.entries.memory-wiki.config` 配下に置きます:

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
- `bridge.readMemoryArtifacts`: active memory Plugin の公開 artifact を取り込む
- `bridge.followMemoryEvents`: bridge mode で event log を含める
- `search.backend`: `shared` または `local`
- `search.corpus`: `wiki`、`memory`、または `all`
- `context.includeCompiledDigestPrompt`: memory prompt セクションにコンパクトな digest スナップショットを追加する
- `render.createBacklinks`: 決定論的な related block を生成する
- `render.createDashboards`: ダッシュボードページを生成する

### 例: QMD + bridge mode

recall には QMD を使い、保守された知識レイヤーには `memory-wiki` を使いたい場合に使用します:

```json5
{
  memory: {
    backend: "qmd",
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "bridge",
          bridge: {
            enabled: true,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          search: {
            backend: "shared",
            corpus: "all",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
        },
      },
    },
  },
}
```

これにより次の状態が保たれます:

- active memory recall は QMD が担当する
- `memory-wiki` はコンパイル済みページとダッシュボードに集中する
- 明示的にコンパイル済み digest prompt を有効にするまで prompt の形状は変わらない

## CLI

`memory-wiki` はトップレベルの CLI サーフェスも公開します:

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

`vault.renderMode` が `obsidian` の場合、Plugin は Obsidian フレンドリーな
Markdown を書き出し、任意で公式の `obsidian` CLI を使用できます。

サポートされるワークフローには次が含まれます:

- status の確認
- ボールト検索
- ページを開く
- Obsidian コマンドを呼び出す
- daily note へ移動する

これは任意です。wiki は Obsidian なしでも native mode で動作します。

## 推奨ワークフロー

1. recall/promotion/Dreaming には active memory Plugin を維持する。
2. `memory-wiki` を有効にする。
3. 明示的に bridge mode が必要でない限り、`isolated` mode から始める。
4. 出典が重要な場合は `wiki_search` / `wiki_get` を使う。
5. 限定的な synthesis または metadata 更新には `wiki_apply` を使う。
6. 意味のある変更の後には `wiki_lint` を実行する。
7. stale/contradiction の可視性が必要ならダッシュボードを有効にする。

## 関連ドキュメント

- [Memory Overview](/ja-JP/concepts/memory)
- [CLI: memory](/cli/memory)
- [CLI: wiki](/cli/wiki)
- [Plugin SDK overview](/ja-JP/plugins/sdk-overview)
