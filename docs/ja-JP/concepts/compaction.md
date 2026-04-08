---
read_when:
    - 自動コンパクションと /compact を理解したい
    - コンテキスト制限に達する長いセッションをデバッグしている
summary: OpenClawがモデルの制限内に収めるために長い会話をどのように要約するか
title: コンパクション
x-i18n:
    generated_at: "2026-04-08T02:14:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: e6590b82a8c3a9c310998d653459ca4d8612495703ca0a8d8d306d7643142fd1
    source_path: concepts/compaction.md
    workflow: 15
---

# コンパクション

すべてのモデルにはコンテキストウィンドウがあります。これは、処理できるトークン数の上限です。
会話がその上限に近づくと、OpenClawは古いメッセージを要約して**コンパクト化**し、
チャットを継続できるようにします。

## 仕組み

1. 古い会話ターンはコンパクトなエントリに要約されます。
2. 要約はセッショントランスクリプトに保存されます。
3. 最近のメッセージはそのまま保持されます。

OpenClawが履歴をコンパクションチャンクに分割するとき、assistantのツール呼び出しは
対応する `toolResult` エントリと組み合わせたまま保持されます。分割点が
ツールブロックの途中に来る場合、OpenClawはそのペアが一緒に保たれ、
現在の未要約の末尾が維持されるように境界を移動します。

会話履歴全体はディスク上に残ります。コンパクションで変わるのは、
次のターンでモデルが見る内容だけです。

## 自動コンパクション

自動コンパクションはデフォルトでオンです。セッションがコンテキスト制限に近づくと実行されるか、
モデルがコンテキスト超過エラーを返したときに実行されます（この場合、
OpenClawはコンパクト化して再試行します）。一般的な超過シグネチャには
`request_too_large`、`context length exceeded`、`input exceeds the maximum
number of tokens`、`input token count exceeds the maximum number of input
tokens`、`input is too long for the model`、`ollama error: context length
exceeded` があります。

<Info>
コンパクト化の前に、OpenClawは重要なメモを [memory](/ja-JP/concepts/memory) ファイルに保存するよう
エージェントに自動で通知します。これにより、コンテキストの喪失を防ぎます。
</Info>

`openclaw.json` の `agents.defaults.compaction` 設定を使用して、コンパクションの動作（モード、目標トークン数など）を設定します。
コンパクション要約では、デフォルトで不透明な識別子が保持されます（`identifierPolicy: "strict"`）。これは `identifierPolicy: "off"` で上書きするか、`identifierPolicy: "custom"` と `identifierInstructions` を使ってカスタムテキストを指定できます。

必要に応じて、`agents.defaults.compaction.model` でコンパクション要約用に別のモデルを指定することもできます。これは、プライマリモデルがローカルモデルまたは小規模モデルで、より高性能なモデルにコンパクション要約を生成させたい場合に便利です。この上書きは任意の `provider/model-id` 文字列を受け付けます。

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "model": "openrouter/anthropic/claude-sonnet-4-6"
      }
    }
  }
}
```

これはローカルモデルでも機能します。たとえば、要約専用の2つ目のOllamaモデルや、コンパクション専用にファインチューニングされたモデルを指定できます。

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "model": "ollama/llama3.1:8b"
      }
    }
  }
}
```

未設定の場合、コンパクションはエージェントのプライマリモデルを使用します。

## プラガブルなコンパクションプロバイダー

プラグインは、プラグインAPIの `registerCompactionProvider()` を介してカスタムのコンパクションプロバイダーを登録できます。プロバイダーが登録されて設定されている場合、OpenClawは組み込みのLLMパイプラインの代わりにそのプロバイダーへ要約を委譲します。

登録済みプロバイダーを使用するには、設定でプロバイダーIDを指定します。

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "provider": "my-provider"
      }
    }
  }
}
```

`provider` を設定すると、自動的に `mode: "safeguard"` が強制されます。プロバイダーは、組み込み経路と同じコンパクション命令および識別子保持ポリシーを受け取り、OpenClawはプロバイダー出力の後でも最近のターンおよび分割ターンのサフィックスコンテキストを保持します。プロバイダーが失敗するか空の結果を返した場合、OpenClawは組み込みのLLM要約にフォールバックします。

## 自動コンパクション（デフォルトでオン）

セッションがモデルのコンテキストウィンドウに近づくか、それを超えると、OpenClawは自動コンパクションをトリガーし、コンパクト化されたコンテキストを使って元のリクエストを再試行することがあります。

表示される内容:

- 詳細モードでは `🧹 Auto-compaction complete`
- `/status` に `🧹 Compactions: <count>` が表示されます

コンパクションの前に、OpenClawは**サイレントメモリフラッシュ**ターンを実行して、
永続的なメモをディスクに保存できます。詳細と設定については [Memory](/ja-JP/concepts/memory) を参照してください。

## 手動コンパクション

任意のチャットで `/compact` と入力すると、コンパクションを強制実行できます。要約を
誘導するための指示を追加することもできます。

```
/compact Focus on the API design decisions
```

## 別のモデルを使う

デフォルトでは、コンパクションはエージェントのプライマリモデルを使用します。より高性能な
モデルを使って、より良い要約を得ることができます。

```json5
{
  agents: {
    defaults: {
      compaction: {
        model: "openrouter/anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

## コンパクション開始通知

デフォルトでは、コンパクションは通知なしで実行されます。コンパクション開始時に短い通知を
表示するには、`notifyUser` を有効にします。

```json5
{
  agents: {
    defaults: {
      compaction: {
        notifyUser: true,
      },
    },
  },
}
```

有効にすると、ユーザーには各コンパクション実行の開始時に短いメッセージ（たとえば「Compacting
context...」）が表示されます。

## コンパクションと剪定の違い

|                  | コンパクション               | 剪定                               |
| ---------------- | ---------------------------- | ---------------------------------- |
| **何をするか**   | 古い会話を要約する           | 古いツール結果を削減する           |
| **保存されるか** | はい（セッショントランスクリプト内） | いいえ（メモリ内のみ、リクエストごと） |
| **対象範囲**     | 会話全体                     | ツール結果のみ                     |

[Session pruning](/ja-JP/concepts/session-pruning) は、要約せずにツール出力を
削減する、より軽量な補完機能です。

## トラブルシューティング

**コンパクト化が多すぎる？** モデルのコンテキストウィンドウが小さいか、ツール出力が
大きい可能性があります。[session pruning](/ja-JP/concepts/session-pruning) を
有効にしてみてください。

**コンパクション後にコンテキストが古く感じる？** `/compact Focus on <topic>` を使って
要約を誘導するか、[memory flush](/ja-JP/concepts/memory) を有効にしてメモが
保持されるようにしてください。

**まっさらな状態から始めたい？** `/new` はコンパクト化せずに新しいセッションを開始します。

高度な設定（予約トークン数、識別子保持、カスタムコンテキストエンジン、
OpenAIのサーバー側コンパクション）については、
[Session Management Deep Dive](/ja-JP/reference/session-management-compaction) を参照してください。

## 関連

- [Session](/ja-JP/concepts/session) — セッション管理とライフサイクル
- [Session Pruning](/ja-JP/concepts/session-pruning) — ツール結果の削減
- [Context](/ja-JP/concepts/context) — エージェントターン用のコンテキストがどのように構築されるか
- [Hooks](/ja-JP/automation/hooks) — コンパクションライフサイクルフック（before_compaction, after_compaction）
