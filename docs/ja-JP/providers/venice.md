---
read_when:
    - OpenClaw でプライバシー重視の推論を使いたい
    - Venice AI のセットアップ ガイダンスが必要です
summary: OpenClaw で Venice AI のプライバシー重視モデルを使う
title: Venice AI
x-i18n:
    generated_at: "2026-04-12T23:33:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6f8005edb1d7781316ce8b5432bf4f9375c16113594a2a588912dce82234a9e5
    source_path: providers/venice.md
    workflow: 15
---

# Venice AI

Venice AI は、無修正モデルのサポートと、匿名化プロキシ経由で主要なプロプライエタリ モデルへのアクセスを備えた、**プライバシー重視の AI 推論**を提供します。すべての推論はデフォルトでプライベートです。データは学習に使われず、ログも保存されません。

## OpenClaw で Venice を使う理由

- オープンソース モデル向けの**プライベート推論**（ログなし）。
- 必要なときに使える**無修正モデル**。
- 品質が重要な場合の、プロプライエタリ モデル（Opus/GPT/Gemini）への**匿名化アクセス**。
- OpenAI 互換の `/v1` エンドポイント。

## プライバシー モード

Venice は 2 段階のプライバシー レベルを提供します。どのモデルを選ぶかを決めるうえで、これを理解することが重要です:

| Mode | Description | Models |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Private** | 完全にプライベート。プロンプト/レスポンスは**保存もログ記録もされません**。エフェメラルです。 | Llama、Qwen、DeepSeek、Kimi、MiniMax、Venice Uncensored など |
| **Anonymized** | メタデータを削除して Venice 経由でプロキシされます。基盤プロバイダー（OpenAI、Anthropic、Google、xAI）には匿名化されたリクエストが渡されます。 | Claude、GPT、Gemini、Grok |

<Warning>
Anonymized モデルは**完全にプライベートではありません**。Venice は転送前にメタデータを削除しますが、基盤プロバイダー（OpenAI、Anthropic、Google、xAI）は引き続きリクエストを処理します。完全なプライバシーが必要な場合は **Private** モデルを選んでください。
</Warning>

## 機能

- **プライバシー重視**: 「private」（完全プライベート）と「anonymized」（プロキシ）のモードから選択
- **無修正モデル**: コンテンツ制限のないモデルにアクセス
- **主要モデルへのアクセス**: Venice の匿名化プロキシ経由で Claude、GPT、Gemini、Grok を利用可能
- **OpenAI 互換 API**: 簡単に統合できる標準の `/v1` エンドポイント
- **ストリーミング**: すべてのモデルでサポート
- **関数呼び出し**: 一部のモデルでサポート（モデル機能を確認）
- **Vision**: Vision 対応モデルでサポート
- **厳格なレート制限なし**: 極端な利用ではフェアユースのスロットリングが適用される場合があります

## はじめに

<Steps>
  <Step title="API キーを取得する">
    1. [venice.ai](https://venice.ai) でサインアップします
    2. **Settings > API Keys > Create new key** に移動します
    3. API キー（形式: `vapi_xxxxxxxxxxxx`）をコピーします
  </Step>
  <Step title="OpenClaw を設定する">
    希望するセットアップ方法を選んでください:

    <Tabs>
      <Tab title="Interactive（推奨）">
        ```bash
        openclaw onboard --auth-choice venice-api-key
        ```

        これにより次が行われます:
        1. API キーの入力を求める（または既存の `VENICE_API_KEY` を使用）
        2. 利用可能な Venice モデルをすべて表示
        3. デフォルト モデルを選択可能
        4. プロバイダーを自動設定
      </Tab>
      <Tab title="環境変数">
        ```bash
        export VENICE_API_KEY="vapi_xxxxxxxxxxxx"
        ```
      </Tab>
      <Tab title="Non-interactive">
        ```bash
        openclaw onboard --non-interactive \
          --auth-choice venice-api-key \
          --venice-api-key "vapi_xxxxxxxxxxxx"
        ```
      </Tab>
    </Tabs>

  </Step>
  <Step title="セットアップを確認する">
    ```bash
    openclaw agent --model venice/kimi-k2-5 --message "Hello, are you working?"
    ```
  </Step>
</Steps>

## モデル選択

セットアップ後、OpenClaw は利用可能な Venice モデルをすべて表示します。ニーズに応じて選んでください:

- **デフォルト モデル**: 強力なプライベート reasoning と vision を備えた `venice/kimi-k2-5`。
- **高機能オプション**: 最も強力な匿名化 Venice 経路である `venice/claude-opus-4-6`。
- **プライバシー**: 完全にプライベートな推論には「private」モデルを選択します。
- **機能性**: Venice のプロキシ経由で Claude、GPT、Gemini にアクセスするには「anonymized」モデルを選択します。

デフォルト モデルはいつでも変更できます:

```bash
openclaw models set venice/kimi-k2-5
openclaw models set venice/claude-opus-4-6
```

利用可能なモデルをすべて一覧表示するには:

```bash
openclaw models list | grep venice
```

`openclaw configure` を実行して **Model/auth** を選び、**Venice AI** を選択することもできます。

<Tip>
ユースケースに合ったモデルを選ぶには、以下の表を使ってください。

| Use Case | Recommended Model | Why |
| -------------------------- | -------------------------------- | -------------------------------------------- |
| **一般チャット（デフォルト）** | `kimi-k2-5` | 強力なプライベート reasoning と vision |
| **全体品質を最優先** | `claude-opus-4-6` | 最も強力な匿名化 Venice オプション |
| **プライバシー + コーディング** | `qwen3-coder-480b-a35b-instruct` | 大きなコンテキストを持つプライベート コーディング モデル |
| **プライベート Vision** | `kimi-k2-5` | private モードのまま Vision を利用可能 |
| **高速 + 低コスト** | `qwen3-4b` | 軽量な reasoning モデル |
| **複雑なプライベート タスク** | `deepseek-v3.2` | 強力な reasoning、ただし Venice tool サポートなし |
| **無修正** | `venice-uncensored` | コンテンツ制限なし |

</Tip>

## 利用可能なモデル（全 41）

<AccordionGroup>
  <Accordion title="Private モデル（26）— 完全にプライベート、ログなし">
    | Model ID | Name | Context | Features |
    | -------------------------------------- | ----------------------------------- | ------- | -------------------------- |
    | `kimi-k2-5` | Kimi K2.5 | 256k | デフォルト、reasoning、vision |
    | `kimi-k2-thinking` | Kimi K2 Thinking | 256k | Reasoning |
    | `llama-3.3-70b` | Llama 3.3 70B | 128k | 一般用途 |
    | `llama-3.2-3b` | Llama 3.2 3B | 128k | 一般用途 |
    | `hermes-3-llama-3.1-405b` | Hermes 3 Llama 3.1 405B | 128k | 一般用途、tools 無効 |
    | `qwen3-235b-a22b-thinking-2507` | Qwen3 235B Thinking | 128k | Reasoning |
    | `qwen3-235b-a22b-instruct-2507` | Qwen3 235B Instruct | 128k | 一般用途 |
    | `qwen3-coder-480b-a35b-instruct` | Qwen3 Coder 480B | 256k | コーディング |
    | `qwen3-coder-480b-a35b-instruct-turbo` | Qwen3 Coder 480B Turbo | 256k | コーディング |
    | `qwen3-5-35b-a3b` | Qwen3.5 35B A3B | 256k | Reasoning、vision |
    | `qwen3-next-80b` | Qwen3 Next 80B | 256k | 一般用途 |
    | `qwen3-vl-235b-a22b` | Qwen3 VL 235B (Vision) | 256k | Vision |
    | `qwen3-4b` | Venice Small (Qwen3 4B) | 32k | 高速、reasoning |
    | `deepseek-v3.2` | DeepSeek V3.2 | 160k | Reasoning、tools 無効 |
    | `venice-uncensored` | Venice Uncensored (Dolphin-Mistral) | 32k | 無修正、tools 無効 |
    | `mistral-31-24b` | Venice Medium (Mistral) | 128k | Vision |
    | `google-gemma-3-27b-it` | Google Gemma 3 27B Instruct | 198k | Vision |
    | `openai-gpt-oss-120b` | OpenAI GPT OSS 120B | 128k | 一般用途 |
    | `nvidia-nemotron-3-nano-30b-a3b` | NVIDIA Nemotron 3 Nano 30B | 128k | 一般用途 |
    | `olafangensan-glm-4.7-flash-heretic` | GLM 4.7 Flash Heretic | 128k | Reasoning |
    | `zai-org-glm-4.6` | GLM 4.6 | 198k | 一般用途 |
    | `zai-org-glm-4.7` | GLM 4.7 | 198k | Reasoning |
    | `zai-org-glm-4.7-flash` | GLM 4.7 Flash | 128k | Reasoning |
    | `zai-org-glm-5` | GLM 5 | 198k | Reasoning |
    | `minimax-m21` | MiniMax M2.1 | 198k | Reasoning |
    | `minimax-m25` | MiniMax M2.5 | 198k | Reasoning |
  </Accordion>

  <Accordion title="Anonymized モデル（15）— Venice プロキシ経由">
    | Model ID | Name | Context | Features |
    | ------------------------------- | ------------------------------ | ------- | ------------------------- |
    | `claude-opus-4-6` | Claude Opus 4.6 (via Venice) | 1M | Reasoning、vision |
    | `claude-opus-4-5` | Claude Opus 4.5 (via Venice) | 198k | Reasoning、vision |
    | `claude-sonnet-4-6` | Claude Sonnet 4.6 (via Venice) | 1M | Reasoning、vision |
    | `claude-sonnet-4-5` | Claude Sonnet 4.5 (via Venice) | 198k | Reasoning、vision |
    | `openai-gpt-54` | GPT-5.4 (via Venice) | 1M | Reasoning、vision |
    | `openai-gpt-53-codex` | GPT-5.3 Codex (via Venice) | 400k | Reasoning、vision、コーディング |
    | `openai-gpt-52` | GPT-5.2 (via Venice) | 256k | Reasoning |
    | `openai-gpt-52-codex` | GPT-5.2 Codex (via Venice) | 256k | Reasoning、vision、コーディング |
    | `openai-gpt-4o-2024-11-20` | GPT-4o (via Venice) | 128k | Vision |
    | `openai-gpt-4o-mini-2024-07-18` | GPT-4o Mini (via Venice) | 128k | Vision |
    | `gemini-3-1-pro-preview` | Gemini 3.1 Pro (via Venice) | 1M | Reasoning、vision |
    | `gemini-3-pro-preview` | Gemini 3 Pro (via Venice) | 198k | Reasoning、vision |
    | `gemini-3-flash-preview` | Gemini 3 Flash (via Venice) | 256k | Reasoning、vision |
    | `grok-41-fast` | Grok 4.1 Fast (via Venice) | 1M | Reasoning、vision |
    | `grok-code-fast-1` | Grok Code Fast 1 (via Venice) | 256k | Reasoning、コーディング |
  </Accordion>
</AccordionGroup>

## モデル検出

`VENICE_API_KEY` が設定されている場合、OpenClaw は Venice API からモデルを自動検出します。API に到達できない場合は、静的カタログにフォールバックします。

`/models` エンドポイントは公開されています（一覧表示には認証不要）が、推論には有効な API キーが必要です。

## ストリーミングと tool サポート

| Feature | Support |
| -------------------- | ---------------------------------------------------- |
| **ストリーミング** | すべてのモデル |
| **関数呼び出し** | ほとんどのモデル（API の `supportsFunctionCalling` を確認） |
| **Vision/画像** | 「Vision」機能が付いたモデル |
| **JSON モード** | `response_format` 経由でサポート |

## 価格

Venice はクレジット ベースのシステムを使用します。現在の料金は [venice.ai/pricing](https://venice.ai/pricing) を確認してください:

- **Private モデル**: 一般に低コスト
- **Anonymized モデル**: 直接 API の価格 + 小額の Venice 手数料に近い

### Venice（Anonymized）と直接 API の比較

| Aspect | Venice（Anonymized） | 直接 API |
| ------------ | ----------------------------- | ------------------- |
| **プライバシー** | メタデータを削除して匿名化 | アカウントに紐付く |
| **レイテンシ** | +10〜50ms（プロキシ） | 直接 |
| **機能** | ほとんどの機能をサポート | すべての機能 |
| **課金** | Venice クレジット | プロバイダー課金 |

## 使用例

```bash
# デフォルトの private モデルを使う
openclaw agent --model venice/kimi-k2-5 --message "Quick health check"

# Venice 経由で Claude Opus を使う（anonymized）
openclaw agent --model venice/claude-opus-4-6 --message "Summarize this task"

# 無修正モデルを使う
openclaw agent --model venice/venice-uncensored --message "Draft options"

# 画像付きで vision モデルを使う
openclaw agent --model venice/qwen3-vl-235b-a22b --message "Review attached image"

# コーディング モデルを使う
openclaw agent --model venice/qwen3-coder-480b-a35b-instruct --message "Refactor this function"
```

## トラブルシューティング

<AccordionGroup>
  <Accordion title="API キーが認識されない">
    ```bash
    echo $VENICE_API_KEY
    openclaw models list | grep venice
    ```

    キーが `vapi_` で始まっていることを確認してください。

  </Accordion>

  <Accordion title="モデルが利用できない">
    Venice のモデル カタログは動的に更新されます。現在利用可能なモデルを確認するには `openclaw models list` を実行してください。一部のモデルは一時的にオフラインの場合があります。
  </Accordion>

  <Accordion title="接続の問題">
    Venice API は `https://api.venice.ai/api/v1` にあります。ネットワークで HTTPS 接続が許可されていることを確認してください。
  </Accordion>
</AccordionGroup>

<Note>
さらにヘルプが必要な場合: [トラブルシューティング](/ja-JP/help/troubleshooting) と [FAQ](/ja-JP/help/faq) を参照してください。
</Note>

## 高度な設定

<AccordionGroup>
  <Accordion title="設定ファイル例">
    ```json5
    {
      env: { VENICE_API_KEY: "vapi_..." },
      agents: { defaults: { model: { primary: "venice/kimi-k2-5" } } },
      models: {
        mode: "merge",
        providers: {
          venice: {
            baseUrl: "https://api.venice.ai/api/v1",
            apiKey: "${VENICE_API_KEY}",
            api: "openai-completions",
            models: [
              {
                id: "kimi-k2-5",
                name: "Kimi K2.5",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 256000,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデル ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Venice AI" href="https://venice.ai" icon="globe">
    Venice AI のホームページとアカウント登録。
  </Card>
  <Card title="API ドキュメント" href="https://docs.venice.ai" icon="book">
    Venice API リファレンスと開発者向けドキュメント。
  </Card>
  <Card title="価格" href="https://venice.ai/pricing" icon="credit-card">
    現在の Venice クレジット料金とプラン。
  </Card>
</CardGroup>
