---
read_when:
    - Ollama 経由でクラウドモデルまたはローカルモデルと一緒に OpenClaw を実行したい場合
    - Ollama のセットアップと設定ガイダンスが必要な場合
summary: Ollama を使って OpenClaw を実行する（クラウドモデルとローカルモデル）
title: Ollama
x-i18n:
    generated_at: "2026-04-08T02:19:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 222ec68f7d4bb29cc7796559ddef1d5059f5159e7a51e2baa3a271ddb3abb716
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

Ollama は、オープンソースモデルを手元のマシンで簡単に実行できるローカル LLM ランタイムです。OpenClaw は Ollama のネイティブ API（`/api/chat`）と統合されており、ストリーミングとツール呼び出しをサポートし、`OLLAMA_API_KEY`（または auth profile）で明示的に有効化し、かつ明示的な `models.providers.ollama` エントリーを定義していない場合には、ローカルの Ollama モデルを自動検出できます。

<Warning>
**リモート Ollama 利用者向け**: OpenClaw では `/v1` の OpenAI-compatible URL（`http://host:11434/v1`）を使わないでください。これはツール呼び出しを壊し、モデルが生のツール JSON をプレーンテキストとして出力することがあります。代わりに、ネイティブ Ollama API URL を使ってください: `baseUrl: "http://host:11434"`（`/v1` なし）。
</Warning>

## クイックスタート

### オンボーディング（推奨）

Ollama をセットアップする最速の方法は、オンボーディングを使うことです。

```bash
openclaw onboard
```

provider 一覧から **Ollama** を選択します。オンボーディングでは次を行います。

1. 到達可能な Ollama の base URL を尋ねます（デフォルトは `http://127.0.0.1:11434`）。
2. **Cloud + Local**（クラウドモデルとローカルモデル）または **Local**（ローカルモデルのみ）を選べます。
3. **Cloud + Local** を選び、かつ ollama.com にサインインしていない場合は、ブラウザーのサインインフローを開きます。
4. 利用可能なモデルを検出し、デフォルト候補を提案します。
5. 選択したモデルがローカルにない場合は自動で pull します。

非対話モードもサポートされています。

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --accept-risk
```

必要に応じて、カスタム base URL やモデルも指定できます。

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --custom-base-url "http://ollama-host:11434" \
  --custom-model-id "qwen3.5:27b" \
  --accept-risk
```

### 手動セットアップ

1. Ollama をインストールします: [https://ollama.com/download](https://ollama.com/download)

2. ローカル推論を使いたい場合は、ローカルモデルを pull します。

```bash
ollama pull gemma4
# または
ollama pull gpt-oss:20b
# または
ollama pull llama3.3
```

3. クラウドモデルも使いたい場合は、サインインします。

```bash
ollama signin
```

4. オンボーディングを実行して `Ollama` を選択します。

```bash
openclaw onboard
```

- `Local`: ローカルモデルのみ
- `Cloud + Local`: ローカルモデルに加えてクラウドモデル
- `kimi-k2.5:cloud`、`minimax-m2.7:cloud`、`glm-5.1:cloud` のようなクラウドモデルは、ローカルで `ollama pull` する必要は**ありません**

OpenClaw が現在提案するもの:

- ローカルのデフォルト: `gemma4`
- クラウドのデフォルト: `kimi-k2.5:cloud`、`minimax-m2.7:cloud`、`glm-5.1:cloud`

5. 手動セットアップを好む場合は、OpenClaw 用に Ollama を直接有効化します（どの値でも動作します。Ollama は実際のキーを必要としません）。

```bash
# 環境変数を設定
export OLLAMA_API_KEY="ollama-local"

# または config file に設定
openclaw config set models.providers.ollama.apiKey "ollama-local"
```

6. モデルを確認または切り替えます。

```bash
openclaw models list
openclaw models set ollama/gemma4
```

7. または、config でデフォルトを設定します。

```json5
{
  agents: {
    defaults: {
      model: { primary: "ollama/gemma4" },
    },
  },
}
```

## モデル検出（implicit provider）

`OLLAMA_API_KEY`（または auth profile）を設定し、かつ **`models.providers.ollama` を定義していない** 場合、OpenClaw は `http://127.0.0.1:11434` にあるローカル Ollama インスタンスからモデルを検出します。

- `/api/tags` を問い合わせる
- 利用可能な場合は、ベストエフォートで `/api/show` を参照して `contextWindow` を読む
- モデル名ベースのヒューリスティック（`r1`、`reasoning`、`think`）で `reasoning` を判定する
- `maxTokens` を、OpenClaw が使用する Ollama デフォルトの max-token 上限に設定する
- すべてのコストを `0` に設定する

これにより、ローカル Ollama インスタンスと catalog の整合性を保ちながら、手動のモデルエントリーを避けられます。

利用可能なモデルを確認するには:

```bash
ollama list
openclaw models list
```

新しいモデルを追加するには、Ollama で pull するだけです。

```bash
ollama pull mistral
```

新しいモデルは自動的に検出され、利用可能になります。

`models.providers.ollama` を明示的に設定した場合、自動検出はスキップされるため、モデルは手動で定義する必要があります（下記参照）。

## 設定

### 基本セットアップ（implicit discovery）

Ollama を有効にする最も簡単な方法は、環境変数を使うことです。

```bash
export OLLAMA_API_KEY="ollama-local"
```

### 明示的セットアップ（手動モデル）

次の場合は明示的な設定を使います。

- Ollama が別のホスト/ポートで動いている。
- 特定の context window や model list を強制したい。
- モデル定義を完全に手動管理したい。

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434",
        apiKey: "ollama-local",
        api: "ollama",
        models: [
          {
            id: "gpt-oss:20b",
            name: "GPT-OSS 20B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 8192,
            maxTokens: 8192 * 10
          }
        ]
      }
    }
  }
}
```

`OLLAMA_API_KEY` が設定されている場合、provider エントリー内の `apiKey` は省略できます。その場合、OpenClaw が可用性チェック用に補完します。

### カスタム base URL（明示的設定）

Ollama が別のホストまたはポートで動作している場合（明示的設定では自動検出が無効になるため、モデルは手動定義してください）:

```json5
{
  models: {
    providers: {
      ollama: {
        apiKey: "ollama-local",
        baseUrl: "http://ollama-host:11434", // No /v1 - use native Ollama API URL
        api: "ollama", // Set explicitly to guarantee native tool-calling behavior
      },
    },
  },
}
```

<Warning>
URL に `/v1` を追加しないでください。`/v1` パスは OpenAI-compatible モードを使うため、ツール呼び出しの信頼性がありません。パスサフィックスなしの Ollama ベース URL を使用してください。
</Warning>

### モデル選択

設定が完了すると、すべての Ollama モデルが利用可能になります。

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## クラウドモデル

クラウドモデルを使うと、ローカルモデルと並行してクラウドホスト型モデル（たとえば `kimi-k2.5:cloud`、`minimax-m2.7:cloud`、`glm-5.1:cloud`）を実行できます。

クラウドモデルを使うには、セットアップ時に **Cloud + Local** モードを選択してください。ウィザードはサインイン状態を確認し、必要に応じてブラウザーのサインインフローを開きます。認証を確認できない場合、ウィザードはローカルモデルのデフォルトにフォールバックします。

[ollama.com/signin](https://ollama.com/signin) で直接サインインすることもできます。

## Ollama Web Search

OpenClaw は、バンドルされた `web_search`
provider として **Ollama Web Search** もサポートしています。

- 設定済みの Ollama ホスト（設定されている場合は `models.providers.ollama.baseUrl`、そうでない場合は `http://127.0.0.1:11434`）を使います。
- キー不要です。
- Ollama が起動していて、`ollama signin` でサインイン済みである必要があります。

`openclaw onboard` または
`openclaw configure --section web` の際に **Ollama Web Search** を選ぶか、次を設定してください。

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

完全なセットアップと動作の詳細は、[Ollama Web Search](/ja-JP/tools/ollama-search) を参照してください。

## 高度な設定

### Reasoning モデル

OpenClaw は、`deepseek-r1`、`reasoning`、`think` のような名前を持つモデルを、デフォルトで reasoning 対応として扱います。

```bash
ollama pull deepseek-r1:32b
```

### モデルコスト

Ollama は無料でローカル実行されるため、すべてのモデルコストは $0 に設定されています。

### ストリーミング設定

OpenClaw の Ollama 統合は、デフォルトで **ネイティブ Ollama API**（`/api/chat`）を使用しており、ストリーミングとツール呼び出しの同時利用を完全にサポートしています。特別な設定は不要です。

#### レガシー OpenAI-Compatible モード

<Warning>
**OpenAI-compatible モードでは、ツール呼び出しの信頼性はありません。** このモードは、プロキシのために OpenAI 形式が必要で、かつネイティブなツール呼び出し動作に依存しない場合にのみ使用してください。
</Warning>

どうしても OpenAI-compatible endpoint を使う必要がある場合（たとえば OpenAI 形式だけをサポートするプロキシの背後にある場合）は、`api: "openai-completions"` を明示的に設定してください。

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: true, // default: true
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

このモードでは、ストリーミング + ツール呼び出しの同時利用がサポートされない場合があります。モデル設定で `params: { streaming: false }` としてストリーミングを無効にする必要があることがあります。

Ollama で `api: "openai-completions"` を使用すると、OpenClaw はデフォルトで `options.num_ctx` を注入します。これにより、Ollama が黙って 4096 の context window にフォールバックするのを防ぎます。プロキシ/上流が未知の `options` フィールドを拒否する場合は、この動作を無効にしてください。

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: false,
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

### Context window

自動検出されたモデルについては、OpenClaw は利用可能な場合に Ollama が報告する context window を使い、利用できない場合は OpenClaw が使用する Ollama のデフォルト context window にフォールバックします。明示的な provider 設定で `contextWindow` と `maxTokens` を上書きできます。

## トラブルシューティング

### Ollama が検出されない

Ollama が起動していること、`OLLAMA_API_KEY`（または auth profile）を設定していること、そして **明示的な `models.providers.ollama` エントリーを定義していない** ことを確認してください。

```bash
ollama serve
```

また、API にアクセスできることも確認してください。

```bash
curl http://localhost:11434/api/tags
```

### 利用可能なモデルがない

モデルが一覧に出てこない場合は、次のいずれかです。

- モデルをローカルで pull する
- `models.providers.ollama` でモデルを明示的に定義する

モデルを追加するには:

```bash
ollama list  # インストール済みを確認
ollama pull gemma4
ollama pull gpt-oss:20b
ollama pull llama3.3     # または別のモデル
```

### Connection refused

Ollama が正しいポートで動作していることを確認してください。

```bash
# Ollama が動作中か確認
ps aux | grep ollama

# または Ollama を再起動
ollama serve
```

## 関連項目

- [Model Providers](/ja-JP/concepts/model-providers) - すべての provider の概要
- [Model Selection](/ja-JP/concepts/models) - モデルの選び方
- [Configuration](/ja-JP/gateway/configuration) - 完全な設定リファレンス
