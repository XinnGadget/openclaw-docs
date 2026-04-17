---
read_when:
    - QMD をメモリバックエンドとして設定したい場合
    - 再ランキングや追加のインデックス対象パスなどの高度なメモリ機能を使いたい場合
summary: BM25、ベクトル、再ランキング、クエリ拡張を備えたローカルファーストの検索サイドカー
title: QMD メモリエンジン
x-i18n:
    generated_at: "2026-04-12T23:27:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27afc996b959d71caed964a3cae437e0e29721728b30ebe7f014db124c88da04
    source_path: concepts/memory-qmd.md
    workflow: 15
---

# QMD メモリエンジン

[QMD](https://github.com/tobi/qmd) は、OpenClaw と並行して動作するローカルファーストの検索サイドカーです。単一のバイナリで BM25、ベクトル検索、再ランキングを組み合わせ、ワークスペースのメモリファイルを超えたコンテンツもインデックスできます。

## 組み込み機能に追加されるもの

- **再ランキングとクエリ拡張** により、より高い再現率を実現します。
- **追加のディレクトリをインデックス** -- プロジェクトのドキュメント、チームノート、ディスク上のあらゆるもの。
- **セッショントランスクリプトをインデックス** -- 以前の会話を想起できます。
- **完全にローカル** -- Bun + node-llama-cpp 経由で動作し、GGUF モデルを自動ダウンロードします。
- **自動フォールバック** -- QMD が利用できない場合、OpenClaw はシームレスに組み込みエンジンへフォールバックします。

## はじめに

### 前提条件

- QMD をインストールします: `npm install -g @tobilu/qmd` または `bun install -g @tobilu/qmd`
- 拡張を許可する SQLite ビルド (`brew install sqlite` を macOS で実行)。
- QMD が Gateway の `PATH` 上に存在している必要があります。
- macOS と Linux はそのままで動作します。Windows は WSL2 経由でのサポートが最も充実しています。

### 有効化

```json5
{
  memory: {
    backend: "qmd",
  },
}
```

OpenClaw は `~/.openclaw/agents/<agentId>/qmd/` 配下に自己完結型の QMD ホームを作成し、サイドカーのライフサイクルを自動的に管理します -- コレクション、更新、埋め込み実行は自動で処理されます。現在の QMD コレクションと MCP クエリ形状を優先しますが、必要に応じて従来の `--mask` コレクションフラグや古い MCP ツール名にもフォールバックします。

## サイドカーの仕組み

- OpenClaw はワークスペースのメモリファイルと設定された `memory.qmd.paths` からコレクションを作成し、起動時および定期的に（デフォルトでは 5 分ごと）`qmd update` と `qmd embed` を実行します。
- デフォルトのワークスペースコレクションは `MEMORY.md` と `memory/` ツリーを追跡します。小文字の `memory.md` はブートストラップ用のフォールバックのままであり、個別の QMD コレクションではありません。
- 起動時の更新はバックグラウンドで実行されるため、チャット起動はブロックされません。
- 検索では設定された `searchMode`（デフォルト: `search`。`vsearch` と `query` もサポート）を使用します。あるモードが失敗した場合、OpenClaw は `qmd query` で再試行します。
- QMD が完全に失敗した場合、OpenClaw は組み込みの SQLite エンジンにフォールバックします。

<Info>
最初の検索は遅い場合があります -- QMD は最初の `qmd query` 実行時に、再ランキングとクエリ拡張のための GGUF モデル（約 2 GB）を自動ダウンロードします。
</Info>

## モデルの上書き

QMD のモデル環境変数は Gateway プロセスから変更なしでそのまま渡されるため、新しい OpenClaw 設定を追加しなくてもグローバルに QMD を調整できます。

```bash
export QMD_EMBED_MODEL="hf:Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf"
export QMD_RERANK_MODEL="/absolute/path/to/reranker.gguf"
export QMD_GENERATE_MODEL="/absolute/path/to/generator.gguf"
```

埋め込みモデルを変更した後は、インデックスが新しいベクトル空間と一致するように埋め込みを再実行してください。

## 追加パスのインデックス

追加のディレクトリを検索可能にするには、QMD にそれらを指定します。

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

追加パスからのスニペットは、検索結果で `qmd/<collection>/<relative-path>` として表示されます。`memory_get` はこのプレフィックスを理解し、正しいコレクションルートから読み取ります。

## セッショントランスクリプトのインデックス

以前の会話を想起するには、セッションインデックスを有効にします。

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      sessions: { enabled: true },
    },
  },
}
```

トランスクリプトはサニタイズ済みの User/Assistant ターンとして、`~/.openclaw/agents/<id>/qmd/sessions/` 配下の専用 QMD コレクションにエクスポートされます。

## 検索スコープ

デフォルトでは、QMD の検索結果はダイレクトセッションとチャネルセッションで表示されます（グループは除く）。これを変更するには `memory.qmd.scope` を設定します。

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

スコープによって検索が拒否された場合、OpenClaw は導出されたチャネルとチャットタイプを含む警告をログ出力するため、空の結果のデバッグがしやすくなります。

## 引用

`memory.citations` が `auto` または `on` の場合、検索スニペットには `Source: <path#line>` のフッターが含まれます。フッターを省略しつつ内部的には引き続きパスをエージェントに渡すには、`memory.citations = "off"` を設定します。

## 使用するタイミング

次のような場合は QMD を選択してください。

- より高品質な結果のために再ランキングが必要な場合。
- ワークスペース外のプロジェクトドキュメントやノートを検索したい場合。
- 過去のセッション会話を想起したい場合。
- API キー不要の完全ローカル検索が必要な場合。

よりシンプルな構成では、[組み込みエンジン](/ja-JP/concepts/memory-builtin) が追加の依存関係なしで十分に機能します。

## トラブルシューティング

**QMD が見つからない場合は？** バイナリが Gateway の `PATH` 上にあることを確認してください。OpenClaw がサービスとして動作している場合は、シンボリックリンクを作成してください:
`sudo ln -s ~/.bun/bin/qmd /usr/local/bin/qmd`。

**最初の検索が非常に遅い場合は？** QMD は初回使用時に GGUF モデルをダウンロードします。OpenClaw が使用するのと同じ XDG ディレクトリで `qmd query "test"` を使って事前ウォームアップしてください。

**検索がタイムアウトする場合は？** `memory.qmd.limits.timeoutMs`（デフォルト: 4000ms）を増やしてください。低速なハードウェアでは `120000` に設定してください。

**グループチャットで結果が空の場合は？** `memory.qmd.scope` を確認してください -- デフォルトではダイレクトセッションとチャネルセッションのみ許可されます。

**ワークスペースから見える一時リポジトリによって `ENAMETOOLONG` やインデックス破損が発生する場合は？**  
QMD の走査は現在、OpenClaw 組み込みのシンボリックリンク規則ではなく、基盤となる QMD スキャナーの動作に従います。QMD が安全な循環回避走査や明示的な除外制御を提供するまでは、一時的なモノレポのチェックアウトを `.tmp/` のような隠しディレクトリ配下、またはインデックス対象の QMD ルート外に置いてください。

## 設定

完全な設定項目（`memory.qmd.*`）、検索モード、更新間隔、スコープルール、そのほかすべての調整項目については、[メモリ設定リファレンス](/ja-JP/reference/memory-config) を参照してください。
