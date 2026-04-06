---
read_when:
    - QMDをメモリバックエンドとして設定したい
    - 再ランキングや追加のインデックス対象パスなどの高度なメモリ機能が必要である
summary: BM25、ベクトル、再ランキング、クエリ拡張を備えたローカルファーストの検索サイドカー
title: QMD Memory Engine
x-i18n:
    generated_at: "2026-04-06T03:06:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 36642c7df94b88f562745dd2270334379f2aeeef4b363a8c13ef6be42dadbe5c
    source_path: concepts/memory-qmd.md
    workflow: 15
---

# QMD Memory Engine

[QMD](https://github.com/tobi/qmd)は、OpenClawと並行して動作するローカルファーストの検索サイドカーです。BM25、ベクトル検索、再ランキングを単一のバイナリに組み合わせており、ワークスペースのメモリファイルを超えるコンテンツもインデックス化できます。

## builtinに追加されるもの

- **より高い再現率のための再ランキングとクエリ拡張**。
- **追加ディレクトリのインデックス化** -- プロジェクトドキュメント、チームノート、ディスク上のあらゆるもの。
- **セッショントランスクリプトのインデックス化** -- 以前の会話を想起。
- **完全にローカル** -- Bun + node-llama-cpp経由で動作し、GGUFモデルを自動ダウンロードします。
- **自動フォールバック** -- QMDが利用できない場合、OpenClawはシームレスにbuiltinエンジンへフォールバックします。

## はじめに

### 前提条件

- QMDをインストール: `npm install -g @tobilu/qmd` または `bun install -g @tobilu/qmd`
- 拡張を許可するSQLiteビルド（macOSでは`brew install sqlite`）。
- QMDがGatewayの`PATH`上にある必要があります。
- macOSとLinuxはそのままで動作します。WindowsはWSL2経由でのサポートが最も充実しています。

### 有効化

```json5
{
  memory: {
    backend: "qmd",
  },
}
```

OpenClawは`~/.openclaw/agents/<agentId>/qmd/`配下に自己完結型のQMDホームを作成し、サイドカーのライフサイクルを自動的に管理します。コレクション、更新、埋め込みの実行は自動で処理されます。現在のQMDコレクションおよびMCPクエリ形式を優先しますが、必要に応じてレガシーな`--mask`コレクションフラグや古いMCPツール名にもフォールバックします。

## サイドカーの仕組み

- OpenClawはワークスペースのメモリファイルと設定された`memory.qmd.paths`からコレクションを作成し、起動時および定期的に（デフォルトでは5分ごとに）`qmd update`と`qmd embed`を実行します。
- 起動時の更新はバックグラウンドで実行されるため、チャットの起動はブロックされません。
- 検索では設定された`searchMode`（デフォルト: `search`。`vsearch`と`query`もサポート）を使用します。あるモードが失敗した場合、OpenClawは`qmd query`で再試行します。
- QMDが完全に失敗した場合、OpenClawはbuiltinのSQLiteエンジンへフォールバックします。

<Info>
最初の検索は遅いことがあります -- QMDは最初の`qmd query`実行時に、再ランキングとクエリ拡張のためのGGUFモデル（約2 GB）を自動ダウンロードします。
</Info>

## モデルのオーバーライド

QMDのモデル環境変数はGatewayプロセスからそのまま引き継がれるため、新しいOpenClaw設定を追加せずにQMDをグローバルに調整できます。

```bash
export QMD_EMBED_MODEL="hf:Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf"
export QMD_RERANK_MODEL="/absolute/path/to/reranker.gguf"
export QMD_GENERATE_MODEL="/absolute/path/to/generator.gguf"
```

埋め込みモデルを変更した後は、インデックスが新しいベクトル空間に一致するよう、埋め込みを再実行してください。

## 追加パスのインデックス化

QMDに追加ディレクトリを指定して検索可能にします。

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

追加パスからのスニペットは、検索結果で`qmd/<collection>/<relative-path>`として表示されます。`memory_get`はこの接頭辞を理解し、正しいコレクションルートから読み取ります。

## セッショントランスクリプトのインデックス化

以前の会話を想起するために、セッションのインデックス化を有効にします。

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

トランスクリプトは、サニタイズされたUser/Assistantターンとして、`~/.openclaw/agents/<id>/qmd/sessions/`配下の専用QMDコレクションにエクスポートされます。

## 検索スコープ

デフォルトでは、QMDの検索結果はDMセッションでのみ表示されます（グループやチャネルでは表示されません）。これを変更するには`memory.qmd.scope`を設定します。

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

スコープによって検索が拒否された場合、OpenClawは導出されたチャネルとチャット種別を含む警告をログに出力するため、空の結果をデバッグしやすくなります。

## 出典

`memory.citations`が`auto`または`on`の場合、検索スニペットには`Source: <path#line>`フッターが含まれます。フッターを省略しつつパスを内部的にはエージェントへ渡し続けるには、`memory.citations = "off"`を設定します。

## 使うべき場面

次のような場合はQMDを選んでください。

- より高品質な結果のために再ランキングが必要である。
- ワークスペース外のプロジェクトドキュメントやノートを検索したい。
- 過去のセッション会話を想起したい。
- APIキー不要の完全ローカル検索が必要である。

よりシンプルなセットアップでは、追加の依存関係なしで[builtin engine](/ja-JP/concepts/memory-builtin)が十分に機能します。

## トラブルシューティング

**QMDが見つからない?** バイナリがGatewayの`PATH`上にあることを確認してください。OpenClawがサービスとして実行されている場合は、次のようにシンボリックリンクを作成します:
`sudo ln -s ~/.bun/bin/qmd /usr/local/bin/qmd`。

**最初の検索が非常に遅い?** QMDは初回使用時にGGUFモデルをダウンロードします。OpenClawが使うのと同じXDGディレクトリで`qmd query "test"`を実行して事前ウォームアップしてください。

**検索がタイムアウトする?** `memory.qmd.limits.timeoutMs`（デフォルト: 4000ms）を増やしてください。低速なハードウェアでは`120000`に設定してください。

**グループチャットで結果が空になる?** `memory.qmd.scope`を確認してください -- デフォルトではDMセッションのみが許可されています。

**ワークスペースから見える一時リポジトリが`ENAMETOOLONG`やインデックス破損を引き起こす?** QMDの走査は現在、OpenClaw builtinのシンボリックリンク規則ではなく、基盤となるQMDスキャナーの動作に従います。QMDがサイクル安全な走査や明示的な除外制御を提供するまでは、一時的なモノレポのチェックアウトは`.tmp/`のような隠しディレクトリ配下、またはインデックス対象のQMDルート外に置いてください。

## 設定

完全な設定サーフェス（`memory.qmd.*`）、検索モード、更新間隔、スコープルール、およびその他すべての調整項目については、[Memory configuration reference](/ja-JP/reference/memory-config)を参照してください。
