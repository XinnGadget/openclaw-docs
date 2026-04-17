---
read_when:
    - Ollama 経由でクラウドモデルまたはローカルモデルを使って OpenClaw を実行したい。
    - Ollama のセットアップと設定のガイダンスが必要です。
summary: Ollama を使って OpenClaw を実行する（クラウドモデルとローカルモデル）
title: Ollama
x-i18n:
    generated_at: "2026-04-15T14:41:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 098e083e0fc484bddb5270eb630c55d7832039b462d1710372b6afece5cefcdf
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

OpenClaw は、ホストされたクラウドモデルとローカル/セルフホストの Ollama サーバー向けに、Ollama のネイティブ API（`/api/chat`）と統合されています。Ollama は 3 つのモードで使用できます。到達可能な Ollama ホストを介する `Cloud + Local`、`https://ollama.com` に対する `Cloud only`、到達可能な Ollama ホストに対する `Local only` です。

<Warning>
**リモート Ollama ユーザー向け**: OpenClaw で `/v1` の OpenAI 互換 URL（`http://host:11434/v1`）を使用しないでください。これによりツール呼び出しが壊れ、モデルが生のツール JSON をプレーンテキストとして出力することがあります。代わりにネイティブ Ollama API URL を使用してください: `baseUrl: "http://host:11434"`（`/v1` なし）。
</Warning>

## はじめに

好みのセットアップ方法とモードを選んでください。

<Tabs>
  <Tab title="オンボーディング（推奨）">
    **最適な対象:** 動作する Ollama クラウドまたはローカル環境を最短でセットアップしたい場合。

    <Steps>
      <Step title="オンボーディングを実行する">
        ```bash
        openclaw onboard
        ```

        プロバイダー一覧から **Ollama** を選択します。
      </Step>
      <Step title="モードを選ぶ">
        - **Cloud + Local** — ローカル Ollama ホストに加えて、そのホスト経由でルーティングされるクラウドモデル
        - **Cloud only** — `https://ollama.com` 経由のホスト型 Ollama モデル
        - **Local only** — ローカルモデルのみ
      </Step>
      <Step title="モデルを選択する">
        `Cloud only` では `OLLAMA_API_KEY` の入力を求められ、ホストされたクラウドのデフォルト候補が提示されます。`Cloud + Local` と `Local only` では Ollama のベース URL を求められ、利用可能なモデルを検出し、選択したローカルモデルがまだ利用できない場合は自動で pull します。`Cloud + Local` では、その Ollama ホストがクラウドアクセス用にサインイン済みかどうかも確認します。
      </Step>
      <Step title="モデルが利用可能であることを確認する">
        ```bash
        openclaw models list --provider ollama
        ```
      </Step>
    </Steps>

    ### 非対話モード

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --accept-risk
    ```

    必要に応じて、カスタムのベース URL やモデルを指定できます。

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --custom-base-url "http://ollama-host:11434" \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk
    ```

  </Tab>

  <Tab title="手動セットアップ">
    **最適な対象:** クラウドまたはローカルセットアップを完全に制御したい場合。

    <Steps>
      <Step title="クラウドかローカルかを選ぶ">
        - **Cloud + Local**: Ollama をインストールし、`ollama signin` でサインインして、そのホスト経由でクラウドリクエストをルーティングする
        - **Cloud only**: `OLLAMA_API_KEY` とともに `https://ollama.com` を使用する
        - **Local only**: [ollama.com/download](https://ollama.com/download) から Ollama をインストールする
      </Step>
      <Step title="ローカルモデルを pull する（Local only）">
        ```bash
        ollama pull gemma4
        # または
        ollama pull gpt-oss:20b
        # または
        ollama pull llama3.3
        ```
      </Step>
      <Step title="OpenClaw で Ollama を有効にする">
        `Cloud only` では実際の `OLLAMA_API_KEY` を使用してください。ホストベースのセットアップでは、任意のプレースホルダー値で動作します。

        ```bash
        # Cloud
        export OLLAMA_API_KEY="your-ollama-api-key"

        # Local-only
        export OLLAMA_API_KEY="ollama-local"

        # または設定ファイルに構成する
        openclaw config set models.providers.ollama.apiKey "OLLAMA_API_KEY"
        ```
      </Step>
      <Step title="モデルを確認して設定する">
        ```bash
        openclaw models list
        openclaw models set ollama/gemma4
        ```

        または、設定でデフォルトを指定します。

        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "ollama/gemma4" },
            },
          },
        }
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## クラウドモデル

<Tabs>
  <Tab title="Cloud + Local">
    `Cloud + Local` は、ローカルモデルとクラウドモデルの両方の制御ポイントとして、到達可能な Ollama ホストを使用します。これは Ollama が推奨するハイブリッドフローです。

    セットアップ時に **Cloud + Local** を使用してください。OpenClaw は Ollama のベース URL を求め、そこからローカルモデルを検出し、そのホストが `ollama signin` でクラウドアクセス用にサインイン済みかどうかを確認します。ホストがサインイン済みの場合、OpenClaw は `kimi-k2.5:cloud`、`minimax-m2.7:cloud`、`glm-5.1:cloud` などのホスト型クラウドのデフォルト候補も提示します。

    ホストがまだサインインされていない場合、OpenClaw は `ollama signin` を実行するまでセットアップをローカル専用のままにします。

  </Tab>

  <Tab title="Cloud only">
    `Cloud only` は、`https://ollama.com` にある Ollama のホスト型 API を使用します。

    セットアップ時に **Cloud only** を使用してください。OpenClaw は `OLLAMA_API_KEY` の入力を求め、`baseUrl: "https://ollama.com"` を設定し、ホストされたクラウドモデル一覧を初期化します。この経路では、ローカルの Ollama サーバーや `ollama signin` は不要です。

  </Tab>

  <Tab title="Local only">
    ローカル専用モードでは、OpenClaw は設定済みの Ollama インスタンスからモデルを検出します。この経路は、ローカルまたはセルフホストの Ollama サーバー向けです。

    現在、OpenClaw はローカルのデフォルトとして `gemma4` を提案します。

  </Tab>
</Tabs>

## モデル検出（暗黙的プロバイダー）

`OLLAMA_API_KEY`（または認証プロファイル）を設定し、**`models.providers.ollama` を定義しない**場合、OpenClaw は `http://127.0.0.1:11434` のローカル Ollama インスタンスからモデルを検出します。

| 動作                 | 詳細                                                                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| カタログ照会         | `/api/tags` を照会します                                                                                                                                           |
| 機能検出             | `/api/show` の最善努力によるルックアップを使って `contextWindow` を読み取り、機能（vision を含む）を検出します                                                  |
| Vision モデル        | `/api/show` により `vision` 機能が報告されたモデルは、画像対応（`input: ["text", "image"]`）としてマークされるため、OpenClaw は画像を自動的にプロンプトへ挿入します |
| 推論検出             | モデル名のヒューリスティック（`r1`、`reasoning`、`think`）で `reasoning` をマークします                                                                          |
| トークン制限         | `maxTokens` を OpenClaw が使用するデフォルトの Ollama 最大トークン上限に設定します                                                                               |
| コスト               | すべてのコストを `0` に設定します                                                                                                                                  |

これにより、カタログをローカル Ollama インスタンスに合わせたまま、手動でモデルエントリを作成せずに済みます。

```bash
# 利用可能なモデルを確認する
ollama list
openclaw models list
```

新しいモデルを追加するには、Ollama で単に pull してください。

```bash
ollama pull mistral
```

新しいモデルは自動的に検出され、利用可能になります。

<Note>
`models.providers.ollama` を明示的に設定すると、自動検出はスキップされ、モデルを手動で定義する必要があります。以下の明示的設定セクションを参照してください。
</Note>

## 設定

<Tabs>
  <Tab title="基本（暗黙的検出）">
    ローカル専用を有効にする最も簡単な方法は、環境変数を使うことです。

    ```bash
    export OLLAMA_API_KEY="ollama-local"
    ```

    <Tip>
    `OLLAMA_API_KEY` が設定されている場合、プロバイダーエントリ内の `apiKey` は省略でき、OpenClaw が可用性チェック用に補完します。
    </Tip>

  </Tab>

  <Tab title="明示的設定（手動モデル）">
    ホスト型クラウドセットアップを使いたい場合、Ollama が別のホスト/ポートで動作している場合、特定のコンテキストウィンドウやモデル一覧を強制したい場合、または完全に手動でモデル定義したい場合は、明示的設定を使用します。

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "https://ollama.com",
            apiKey: "OLLAMA_API_KEY",
            api: "ollama",
            models: [
              {
                id: "kimi-k2.5:cloud",
                name: "kimi-k2.5:cloud",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 128000,
                maxTokens: 8192
              }
            ]
          }
        }
      }
    }
    ```

  </Tab>

  <Tab title="カスタムベース URL">
    Ollama が別のホストまたはポートで動作している場合（明示的設定では自動検出が無効になるため、モデルを手動で定義してください）:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            apiKey: "ollama-local",
            baseUrl: "http://ollama-host:11434", // /v1 なし - ネイティブ Ollama API URL を使用
            api: "ollama", // ネイティブのツール呼び出し動作を確実にするため明示的に設定
          },
        },
      },
    }
    ```

    <Warning>
    URL に `/v1` を追加しないでください。`/v1` パスは OpenAI 互換モードを使用するため、ツール呼び出しが信頼できません。パス接尾辞のないベース Ollama URL を使用してください。
    </Warning>

  </Tab>
</Tabs>

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

## Ollama Web Search

OpenClaw は、バンドルされた `web_search` プロバイダーとして **Ollama Web Search** をサポートしています。

| Property    | Detail                                                                                                               |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| Host        | 設定済みの Ollama ホストを使用します（`models.providers.ollama.baseUrl` が設定されている場合はそれ、そうでない場合は `http://127.0.0.1:11434`） |
| Auth        | キー不要                                                                                                             |
| Requirement | Ollama が起動しており、`ollama signin` でサインイン済みである必要があります                                          |

`openclaw onboard` または `openclaw configure --section web` 実行中に **Ollama Web Search** を選択するか、次のように設定してください。

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

<Note>
セットアップと動作の詳細については、[Ollama Web Search](/ja-JP/tools/ollama-search) を参照してください。
</Note>

## 高度な設定

<AccordionGroup>
  <Accordion title="従来の OpenAI 互換モード">
    <Warning>
    **OpenAI 互換モードでは、ツール呼び出しは信頼できません。** このモードは、プロキシのために OpenAI 形式が必要で、ネイティブのツール呼び出し動作に依存しない場合にのみ使用してください。
    </Warning>

    代わりに OpenAI 互換エンドポイントを使用する必要がある場合（たとえば、OpenAI 形式のみをサポートするプロキシの背後にある場合）、`api: "openai-completions"` を明示的に設定してください。

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

    このモードでは、ストリーミングとツール呼び出しを同時にサポートしない場合があります。モデル設定で `params: { streaming: false }` を指定して、ストリーミングを無効にする必要があるかもしれません。

    `api: "openai-completions"` を Ollama とともに使用する場合、OpenClaw はデフォルトで `options.num_ctx` を注入するため、Ollama が暗黙のうちに 4096 のコンテキストウィンドウへフォールバックすることを防ぎます。プロキシまたは上流が未知の `options` フィールドを拒否する場合は、この動作を無効にしてください。

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

  </Accordion>

  <Accordion title="コンテキストウィンドウ">
    自動検出されたモデルについては、OpenClaw は利用可能な場合は Ollama によって報告されたコンテキストウィンドウを使用し、そうでない場合は OpenClaw が使用するデフォルトの Ollama コンテキストウィンドウにフォールバックします。

    明示的なプロバイダー設定で `contextWindow` と `maxTokens` を上書きできます。

    ```json5
    {
      models: {
        providers: {
          ollama: {
            models: [
              {
                id: "llama3.3",
                contextWindow: 131072,
                maxTokens: 65536,
              }
            ]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Reasoning モデル">
    OpenClaw は、`deepseek-r1`、`reasoning`、`think` などの名前を持つモデルを、デフォルトで reasoning 対応として扱います。

    ```bash
    ollama pull deepseek-r1:32b
    ```

    追加の設定は不要です。OpenClaw が自動的にマークします。

  </Accordion>

  <Accordion title="モデルコスト">
    Ollama は無料でローカル実行されるため、すべてのモデルコストは $0 に設定されます。これは、自動検出されたモデルにも手動定義されたモデルにも適用されます。
  </Accordion>

  <Accordion title="メモリ埋め込み">
    バンドルされた Ollama Plugin は、
    [メモリ検索](/ja-JP/concepts/memory) 用のメモリ埋め込みプロバイダーを登録します。設定された Ollama のベース URL
    と API キーを使用します。

    | Property      | Value                                            |
    | ------------- | ------------------------------------------------ |
    | デフォルトモデル | `nomic-embed-text`                             |
    | 自動 pull     | はい — 埋め込みモデルがローカルに存在しない場合は自動的に pull されます |

    メモリ検索の埋め込みプロバイダーとして Ollama を選択するには、次のようにします。

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: { provider: "ollama" },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="ストリーミング設定">
    OpenClaw の Ollama 統合は、デフォルトで **ネイティブ Ollama API**（`/api/chat`）を使用し、ストリーミングとツール呼び出しを同時に完全サポートします。特別な設定は不要です。

    <Tip>
    OpenAI 互換エンドポイントを使用する必要がある場合は、上記の「従来の OpenAI 互換モード」セクションを参照してください。そのモードでは、ストリーミングとツール呼び出しが同時に動作しない可能性があります。
    </Tip>

  </Accordion>
</AccordionGroup>

## トラブルシューティング

<AccordionGroup>
  <Accordion title="Ollama が検出されない">
    Ollama が実行中であること、`OLLAMA_API_KEY`（または認証プロファイル）を設定していること、そして明示的な `models.providers.ollama` エントリを**定義していない**ことを確認してください。

    ```bash
    ollama serve
    ```

    API にアクセスできることを確認します。

    ```bash
    curl http://localhost:11434/api/tags
    ```

  </Accordion>

  <Accordion title="利用可能なモデルがない">
    モデルが一覧に表示されない場合は、ローカルでそのモデルを pull するか、`models.providers.ollama` で明示的に定義してください。

    ```bash
    ollama list  # インストール済みモデルを確認
    ollama pull gemma4
    ollama pull gpt-oss:20b
    ollama pull llama3.3     # または別のモデル
    ```

  </Accordion>

  <Accordion title="接続が拒否される">
    Ollama が正しいポートで実行されていることを確認してください。

    ```bash
    # Ollama が動作中か確認
    ps aux | grep ollama

    # または Ollama を再起動
    ollama serve
    ```

  </Accordion>
</AccordionGroup>

<Note>
詳細なヘルプ: [トラブルシューティング](/ja-JP/help/troubleshooting) と [FAQ](/ja-JP/help/faq)。
</Note>

## 関連

<CardGroup cols={2}>
  <Card title="モデルプロバイダー" href="/ja-JP/concepts/model-providers" icon="layers">
    すべてのプロバイダー、モデル参照、フェイルオーバー動作の概要。
  </Card>
  <Card title="モデル選択" href="/ja-JP/concepts/models" icon="brain">
    モデルの選び方と設定方法。
  </Card>
  <Card title="Ollama Web Search" href="/ja-JP/tools/ollama-search" icon="magnifying-glass">
    Ollama を利用した Web 検索の完全なセットアップと動作の詳細。
  </Card>
  <Card title="設定" href="/ja-JP/gateway/configuration" icon="gear">
    完全な設定リファレンス。
  </Card>
</CardGroup>
