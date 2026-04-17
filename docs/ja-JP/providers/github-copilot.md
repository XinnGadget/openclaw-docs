---
read_when:
    - GitHub Copilotをモデルプロバイダーとして使用したい場合
    - '`openclaw models auth login-github-copilot`フローが必要です'
summary: デバイスフローを使用してOpenClawからGitHub Copilotにサインインする
title: GitHub Copilot
x-i18n:
    generated_at: "2026-04-15T14:40:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: b8258fecff22fb73b057de878462941f6eb86d0c5f775c5eac4840e95ba5eccf
    source_path: providers/github-copilot.md
    workflow: 15
---

# GitHub Copilot

GitHub CopilotはGitHubのAIコーディングアシスタントです。GitHubアカウントとプランに対してCopilotモデルへのアクセスを提供します。OpenClawは、2つの異なる方法でCopilotをモデルプロバイダーとして使用できます。

## OpenClawでCopilotを使う2つの方法

<Tabs>
  <Tab title="Built-in provider (github-copilot)">
    ネイティブのデバイスログインフローを使用してGitHubトークンを取得し、その後OpenClawの実行時にそれをCopilot APIトークンへ交換します。これは**デフォルト**かつ最も簡単な方法で、VS Codeは必要ありません。

    <Steps>
      <Step title="ログインコマンドを実行する">
        ```bash
        openclaw models auth login-github-copilot
        ```

        URLにアクセスして1回限りのコードを入力するよう求められます。完了するまでターミナルを開いたままにしてください。
      </Step>
      <Step title="デフォルトモデルを設定する">
        ```bash
        openclaw models set github-copilot/gpt-4o
        ```

        または、configで設定します:

        ```json5
        {
          agents: { defaults: { model: { primary: "github-copilot/gpt-4o" } } },
        }
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Copilot Proxy plugin (copilot-proxy)">
    **Copilot Proxy** VS Code拡張機能をローカルブリッジとして使用します。OpenClawはプロキシの`/v1`エンドポイントと通信し、そこで設定したモデルリストを使用します。

    <Note>
    すでにVS CodeでCopilot Proxyを実行している場合や、それを経由してルーティングする必要がある場合はこちらを選んでください。Pluginを有効にし、VS Code拡張機能を実行したままにする必要があります。
    </Note>

  </Tab>
</Tabs>

## オプションフラグ

| Flag            | 説明                                           |
| --------------- | ---------------------------------------------- |
| `--yes`         | 確認プロンプトをスキップする                   |
| `--set-default` | プロバイダー推奨のデフォルトモデルも適用する |

```bash
# 確認をスキップ
openclaw models auth login-github-copilot --yes

# ログインしてデフォルトモデルも1ステップで設定
openclaw models auth login --provider github-copilot --method device --set-default
```

<AccordionGroup>
  <Accordion title="対話型TTYが必要">
    デバイスログインフローには対話型TTYが必要です。非対話型スクリプトやCIパイプラインではなく、ターミナルで直接実行してください。
  </Accordion>

  <Accordion title="利用できるモデルはプランによって異なる">
    Copilotで利用できるモデルはGitHubのプランによって異なります。モデルが拒否された場合は、別のID（たとえば`github-copilot/gpt-4.1`）を試してください。
  </Accordion>

  <Accordion title="トランスポートの選択">
    ClaudeのモデルIDは自動的にAnthropic Messagesトランスポートを使用します。GPT、o-series、GeminiモデルはOpenAI Responsesトランスポートを引き続き使用します。OpenClawはモデルrefに基づいて正しいトランスポートを選択します。
  </Accordion>

  <Accordion title="環境変数の解決順序">
    OpenClawは、次の優先順位で環境変数からCopilot認証を解決します:

    | Priority | Variable              | Notes                              |
    | -------- | --------------------- | ---------------------------------- |
    | 1        | `COPILOT_GITHUB_TOKEN` | 最優先、Copilot専用                 |
    | 2        | `GH_TOKEN`            | GitHub CLIトークン（フォールバック） |
    | 3        | `GITHUB_TOKEN`        | 標準のGitHubトークン（最低優先）     |

    複数の変数が設定されている場合、OpenClawは最も優先度の高いものを使用します。デバイスログインフロー（`openclaw models auth login-github-copilot`）はそのトークンを認証プロファイルストアに保存し、すべての環境変数よりも優先されます。

  </Accordion>

  <Accordion title="トークンの保存">
    ログインにより、GitHubトークンが認証プロファイルストアに保存され、OpenClawの実行時にそれがCopilot APIトークンへ交換されます。トークンを手動で管理する必要はありません。
  </Accordion>
</AccordionGroup>

<Warning>
対話型TTYが必要です。ヘッドレススクリプトやCIジョブ内ではなく、ログインコマンドをターミナルで直接実行してください。
</Warning>

## メモリ検索埋め込み

GitHub Copilotは、[メモリ検索](/ja-JP/concepts/memory-search)の埋め込みプロバイダーとしても利用できます。Copilotのサブスクリプションがあり、すでにログインしていれば、OpenClawは別個のAPIキーなしで埋め込みにそれを使用できます。

### 自動検出

`memorySearch.provider`が`"auto"`（デフォルト）の場合、GitHub Copilotは優先度15で試されます。これはローカル埋め込みの後、OpenAIやその他の有料プロバイダーの前です。GitHubトークンが利用可能であれば、OpenClawはCopilot APIから利用可能な埋め込みモデルを検出し、最適なものを自動的に選択します。

### 明示的な設定

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "github-copilot",
        // 任意: 自動検出されたモデルを上書き
        model: "text-embedding-3-small",
      },
    },
  },
}
```

### 仕組み

1. OpenClawがGitHubトークンを解決します（環境変数または認証プロファイルから）。
2. それを短命なCopilot APIトークンに交換します。
3. Copilotの`/models`エンドポイントに問い合わせて、利用可能な埋め込みモデルを検出します。
4. 最適なモデルを選択します（`text-embedding-3-small`を優先）。
5. Copilotの`/embeddings`エンドポイントに埋め込みリクエストを送信します。

利用できるモデルはGitHubのプランによって異なります。利用可能な埋め込みモデルがない場合、OpenClawはCopilotをスキップして次のプロバイダーを試します。

## 関連

<CardGroup cols={2}>
  <Card title="モデルの選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデルref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="OAuthと認証" href="/ja-JP/gateway/authentication" icon="key">
    認証の詳細と認証情報の再利用ルール。
  </Card>
</CardGroup>
