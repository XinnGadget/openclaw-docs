---
read_when:
    - Perplexity を Web 検索 provider として設定したい場合
    - Perplexity API key または OpenRouter プロキシのセットアップが必要です
summary: Perplexity Web 検索 provider のセットアップ（API key、検索モード、フィルタリング）
title: Perplexity
x-i18n:
    generated_at: "2026-04-12T23:33:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 55c089e96601ebe05480d305364272c7f0ac721caa79746297c73002a9f20f55
    source_path: providers/perplexity-provider.md
    workflow: 15
---

# Perplexity（Web 検索 provider）

Perplexity Plugin は、Perplexity
Search API または OpenRouter 経由の Perplexity Sonar を通じて Web 検索機能を提供します。

<Note>
このページでは Perplexity **provider** のセットアップを扱います。Perplexity
**tool**（エージェントがこれをどう使うか）については、[Perplexity tool](/ja-JP/tools/perplexity-search) を参照してください。
</Note>

| Property    | Value                                                                  |
| ----------- | ---------------------------------------------------------------------- |
| Type        | Web 検索 provider（model provider ではない）                           |
| Auth        | `PERPLEXITY_API_KEY`（直接）または `OPENROUTER_API_KEY`（OpenRouter 経由） |
| Config path | `plugins.entries.perplexity.config.webSearch.apiKey`                   |

## はじめに

<Steps>
  <Step title="API key を設定">
    対話型の Web 検索設定フローを実行します。

    ```bash
    openclaw configure --section web
    ```

    または、キーを直接設定します。

    ```bash
    openclaw config set plugins.entries.perplexity.config.webSearch.apiKey "pplx-xxxxxxxxxxxx"
    ```

  </Step>
  <Step title="検索を開始">
    キーが設定されると、エージェントは Web 検索に自動的に Perplexity を使用します。
    追加の手順は不要です。
  </Step>
</Steps>

## 検索モード

Plugin は、API key のプレフィックスに基づいてトランスポートを自動選択します。

<Tabs>
  <Tab title="ネイティブ Perplexity API（pplx-）">
    キーが `pplx-` で始まる場合、OpenClaw はネイティブの Perplexity Search
    API を使用します。このトランスポートは構造化結果を返し、ドメイン、言語、
    日付フィルターをサポートします（以下のフィルタリングオプションを参照）。
  </Tab>
  <Tab title="OpenRouter / Sonar（sk-or-）">
    キーが `sk-or-` で始まる場合、OpenClaw は
    Perplexity Sonar model を使用して OpenRouter 経由でルーティングします。このトランスポートは、
    引用付きの AI 合成回答を返します。
  </Tab>
</Tabs>

| キーのプレフィックス | トランスポート                    | 機能                                           |
| ---------- | ---------------------------- | ------------------------------------------------ |
| `pplx-`    | ネイティブ Perplexity Search API | 構造化結果、ドメイン/言語/日付フィルター         |
| `sk-or-`   | OpenRouter（Sonar）           | 引用付きの AI 合成回答                            |

## ネイティブ API のフィルタリング

<Note>
フィルタリングオプションは、ネイティブ Perplexity API
（`pplx-` キー）を使う場合にのみ利用できます。OpenRouter/Sonar の検索では、これらのパラメータはサポートされません。
</Note>

ネイティブ Perplexity API を使う場合、検索は次のフィルターをサポートします。

| Filter         | 説明                                 | 例                                  |
| -------------- | ------------------------------------ | ----------------------------------- |
| Country        | 2 文字の国コード                     | `us`、`de`、`jp`                    |
| Language       | ISO 639-1 言語コード                 | `en`、`fr`、`zh`                    |
| Date range     | 新しさの範囲                         | `day`、`week`、`month`、`year`      |
| Domain filters | allowlist または denylist（最大 20 ドメイン） | `example.com`                       |
| Content budget | 応答ごと / ページごとのトークン上限  | `max_tokens`、`max_tokens_per_page` |

## 高度な注記

<AccordionGroup>
  <Accordion title="デーモンプロセス用の環境変数">
    OpenClaw Gateway がデーモン（launchd/systemd）として実行される場合は、
    `PERPLEXITY_API_KEY` がそのプロセスで利用可能であることを確認してください。

    <Warning>
    `~/.profile` にのみ設定されたキーは、その環境が明示的に取り込まれない限り、
    launchd/systemd デーモンからは見えません。Gateway プロセスが
    読み取れるようにするには、キーを `~/.openclaw/.env` または `env.shellEnv` に設定してください。
    </Warning>

  </Accordion>

  <Accordion title="OpenRouter プロキシのセットアップ">
    Perplexity 検索を OpenRouter 経由でルーティングしたい場合は、
    ネイティブの Perplexity キーの代わりに `OPENROUTER_API_KEY`（プレフィックス `sk-or-`）を設定してください。
    OpenClaw はプレフィックスを検出し、自動的に Sonar トランスポートへ切り替えます。

    <Tip>
    OpenRouter トランスポートは、すでに OpenRouter アカウントを持っていて、
    複数 provider にまたがる課金を一元化したい場合に便利です。
    </Tip>

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Perplexity 検索 tool" href="/ja-JP/tools/perplexity-search" icon="magnifying-glass">
    エージェントが Perplexity 検索を呼び出し、結果をどう解釈するか。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference" icon="gear">
    Plugin エントリを含む完全な設定リファレンス。
  </Card>
</CardGroup>
