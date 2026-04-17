---
read_when:
    - OpenClaw で OpenAI モデルを使用したい場合
    - API キーではなく Codex subscription 認証を使用したい場合
    - より厳格な GPT-5 agent 実行動作が必要な場合
summary: OpenClaw で API キーまたは Codex subscription を使って OpenAI を使用する
title: OpenAI
x-i18n:
    generated_at: "2026-04-12T23:32:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6aeb756618c5611fed56e4bf89015a2304ff2e21596104b470ec6e7cb459d1c9
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI は GPT モデル向けの開発者 API を提供します。OpenClaw は 2 つの認証経路をサポートしています:

- **API key** — 従量課金の direct OpenAI Platform access（`openai/*` モデル）
- **Codex subscription** — subscription access を使う ChatGPT/Codex サインイン（`openai-codex/*` モデル）

OpenAI は、OpenClaw のような外部ツールやワークフローでの subscription OAuth 利用を明示的にサポートしています。

## はじめに

希望する認証方法を選び、セットアップ手順に従ってください。

<Tabs>
  <Tab title="API key (OpenAI Platform)">
    **最適な用途:** direct API access と従量課金。

    <Steps>
      <Step title="Get your API key">
        [OpenAI Platform dashboard](https://platform.openai.com/api-keys) で API キーを作成またはコピーします。
      </Step>
      <Step title="Run onboarding">
        ```bash
        openclaw onboard --auth-choice openai-api-key
        ```

        または、キーを直接渡します:

        ```bash
        openclaw onboard --openai-api-key "$OPENAI_API_KEY"
        ```
      </Step>
      <Step title="Verify the model is available">
        ```bash
        openclaw models list --provider openai
        ```
      </Step>
    </Steps>

    ### 経路の概要

    | Model ref | Route | Auth |
    |-----------|-------|------|
    | `openai/gpt-5.4` | direct OpenAI Platform API | `OPENAI_API_KEY` |
    | `openai/gpt-5.4-pro` | direct OpenAI Platform API | `OPENAI_API_KEY` |

    <Note>
    ChatGPT/Codex サインインは `openai/*` ではなく `openai-codex/*` を通ります。
    </Note>

    ### 設定例

    ```json5
    {
      env: { OPENAI_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
    }
    ```

    <Warning>
    OpenClaw は direct API 経路では `openai/gpt-5.3-codex-spark` を公開しません。live OpenAI API リクエストはこのモデルを拒否します。Spark は Codex 専用です。
    </Warning>

  </Tab>

  <Tab title="Codex subscription">
    **最適な用途:** 別の API キーではなく、ChatGPT/Codex subscription を使用する場合。Codex cloud には ChatGPT サインインが必要です。

    <Steps>
      <Step title="Run Codex OAuth">
        ```bash
        openclaw onboard --auth-choice openai-codex
        ```

        または、OAuth を直接実行します:

        ```bash
        openclaw models auth login --provider openai-codex
        ```
      </Step>
      <Step title="Set the default model">
        ```bash
        openclaw config set agents.defaults.model.primary openai-codex/gpt-5.4
        ```
      </Step>
      <Step title="Verify the model is available">
        ```bash
        openclaw models list --provider openai-codex
        ```
      </Step>
    </Steps>

    ### 経路の概要

    | Model ref | Route | Auth |
    |-----------|-------|------|
    | `openai-codex/gpt-5.4` | ChatGPT/Codex OAuth | Codex サインイン |
    | `openai-codex/gpt-5.3-codex-spark` | ChatGPT/Codex OAuth | Codex サインイン（entitlement 依存） |

    <Note>
    この経路は `openai/gpt-5.4` とは意図的に分離されています。direct Platform access には API キー付きの `openai/*` を使い、Codex subscription access には `openai-codex/*` を使ってください。
    </Note>

    ### 設定例

    ```json5
    {
      agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
    }
    ```

    <Tip>
    オンボーディングが既存の Codex CLI ログインを再利用する場合、その資格情報は Codex CLI によって管理されたままになります。有効期限が切れた際、OpenClaw はまず外部の Codex ソースを再読込し、更新された資格情報を Codex ストレージに書き戻します。
    </Tip>

    ### context window 上限

    OpenClaw は model metadata と runtime context 上限を別の値として扱います。

    `openai-codex/gpt-5.4` の場合:

    - ネイティブの `contextWindow`: `1050000`
    - デフォルトの runtime `contextTokens` 上限: `272000`

    より小さいデフォルト上限の方が、実運用ではレイテンシと品質の特性が良好です。`contextTokens` で上書きできます:

    ```json5
    {
      models: {
        providers: {
          "openai-codex": {
            models: [{ id: "gpt-5.4", contextTokens: 160000 }],
          },
        },
      },
    }
    ```

    <Note>
    ネイティブ model metadata の宣言には `contextWindow` を使います。runtime context budget の制限には `contextTokens` を使います。
    </Note>

  </Tab>
</Tabs>

## 画像生成

バンドルされた `openai` Plugin は、`image_generate` tool を通じて画像生成を登録します。

| Capability                | Value                              |
| ------------------------- | ---------------------------------- |
| Default model             | `openai/gpt-image-1`               |
| 1 リクエストあたりの最大画像数 | 4                              |
| 編集モード                | 有効（最大 5 枚の参照画像）        |
| サイズの上書き            | サポート                           |
| Aspect ratio / resolution | OpenAI Images API には転送されない |

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "openai/gpt-image-1" },
    },
  },
}
```

<Note>
共有 tool パラメーター、provider 選択、フェイルオーバー動作については、[Image Generation](/ja-JP/tools/image-generation) を参照してください。
</Note>

## 動画生成

バンドルされた `openai` Plugin は、`video_generate` tool を通じて動画生成を登録します。

| Capability       | Value                                                                             |
| ---------------- | --------------------------------------------------------------------------------- |
| Default model    | `openai/sora-2`                                                                   |
| Modes            | Text-to-video、image-to-video、single-video edit                                  |
| Reference inputs | 1 枚の画像または 1 本の動画                                                       |
| Size overrides   | サポート                                                                         |
| Other overrides  | `aspectRatio`、`resolution`、`audio`、`watermark` は tool warning とともに無視されます |

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "openai/sora-2" },
    },
  },
}
```

<Note>
共有 tool パラメーター、provider 選択、フェイルオーバー動作については、[Video Generation](/ja-JP/tools/video-generation) を参照してください。
</Note>

## Personality overlay

OpenClaw は、`openai/*` および `openai-codex/*` の実行向けに、OpenAI 固有の小さな prompt overlay を追加します。この overlay は、ベースのシステム prompt を置き換えることなく、アシスタントを温かく、協調的で、簡潔、かつ少し感情表現豊かに保ちます。

| Value                  | Effect                               |
| ---------------------- | ------------------------------------ |
| `"friendly"` (default) | OpenAI 固有の overlay を有効にする   |
| `"on"`                 | `"friendly"` の別名                  |
| `"off"`                | ベースの OpenClaw prompt のみを使用  |

<Tabs>
  <Tab title="Config">
    ```json5
    {
      plugins: {
        entries: {
          openai: { config: { personality: "friendly" } },
        },
      },
    }
    ```
  </Tab>
  <Tab title="CLI">
    ```bash
    openclaw config set plugins.entries.openai.config.personality off
    ```
  </Tab>
</Tabs>

<Tip>
値は実行時には大文字小文字を区別しないため、`"Off"` と `"off"` はどちらも overlay を無効にします。
</Tip>

## 音声とスピーチ

<AccordionGroup>
  <Accordion title="Speech synthesis (TTS)">
    バンドルされた `openai` Plugin は、`messages.tts` サーフェス向けに speech synthesis を登録します。

    | Setting | Config path | Default |
    |---------|------------|---------|
    | Model | `messages.tts.providers.openai.model` | `gpt-4o-mini-tts` |
    | Voice | `messages.tts.providers.openai.voice` | `coral` |
    | Speed | `messages.tts.providers.openai.speed` | （未設定） |
    | Instructions | `messages.tts.providers.openai.instructions` | （未設定、`gpt-4o-mini-tts` のみ） |
    | Format | `messages.tts.providers.openai.responseFormat` | voice note では `opus`、ファイルでは `mp3` |
    | API key | `messages.tts.providers.openai.apiKey` | `OPENAI_API_KEY` にフォールバック |
    | Base URL | `messages.tts.providers.openai.baseUrl` | `https://api.openai.com/v1` |

    利用可能なモデル: `gpt-4o-mini-tts`、`tts-1`、`tts-1-hd`。利用可能な voice: `alloy`、`ash`、`ballad`、`cedar`、`coral`、`echo`、`fable`、`juniper`、`marin`、`onyx`、`nova`、`sage`、`shimmer`、`verse`。

    ```json5
    {
      messages: {
        tts: {
          providers: {
            openai: { model: "gpt-4o-mini-tts", voice: "coral" },
          },
        },
      },
    }
    ```

    <Note>
    chat API エンドポイントに影響を与えずに TTS の base URL を上書きするには、`OPENAI_TTS_BASE_URL` を設定してください。
    </Note>

  </Accordion>

  <Accordion title="Realtime transcription">
    バンドルされた `openai` Plugin は、Voice Call Plugin 向けに realtime transcription を登録します。

    | Setting | Config path | Default |
    |---------|------------|---------|
    | Model | `plugins.entries.voice-call.config.streaming.providers.openai.model` | `gpt-4o-transcribe` |
    | Silence duration | `...openai.silenceDurationMs` | `800` |
    | VAD threshold | `...openai.vadThreshold` | `0.5` |
    | API key | `...openai.apiKey` | `OPENAI_API_KEY` にフォールバック |

    <Note>
    `wss://api.openai.com/v1/realtime` への WebSocket 接続を、G.711 u-law audio とともに使用します。
    </Note>

  </Accordion>

  <Accordion title="Realtime voice">
    バンドルされた `openai` Plugin は、Voice Call Plugin 向けに realtime voice を登録します。

    | Setting | Config path | Default |
    |---------|------------|---------|
    | Model | `plugins.entries.voice-call.config.realtime.providers.openai.model` | `gpt-realtime` |
    | Voice | `...openai.voice` | `alloy` |
    | Temperature | `...openai.temperature` | `0.8` |
    | VAD threshold | `...openai.vadThreshold` | `0.5` |
    | Silence duration | `...openai.silenceDurationMs` | `500` |
    | API key | `...openai.apiKey` | `OPENAI_API_KEY` にフォールバック |

    <Note>
    `azureEndpoint` および `azureDeployment` config key により Azure OpenAI をサポートします。双方向の tool calling をサポートします。G.711 u-law audio format を使用します。
    </Note>

  </Accordion>
</AccordionGroup>

## 詳細設定

<AccordionGroup>
  <Accordion title="Transport (WebSocket vs SSE)">
    OpenClaw は、`openai/*` と `openai-codex/*` の両方で、WebSocket 優先かつ SSE フォールバック（`"auto"`）を使用します。

    `"auto"` mode では、OpenClaw は次のように動作します:
    - 初期の WebSocket 失敗を 1 回再試行してから SSE にフォールバックする
    - 失敗後、WebSocket を約 60 秒間 degraded とマークし、cool-down 中は SSE を使用する
    - 再試行と再接続のために安定した session と turn の identity header を付与する
    - transport の種類をまたいで usage counter（`input_tokens` / `prompt_tokens`）を正規化する

    | Value | Behavior |
    |-------|----------|
    | `"auto"` (default) | WebSocket 優先、SSE フォールバック |
    | `"sse"` | SSE のみを強制 |
    | `"websocket"` | WebSocket のみを強制 |

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai-codex/gpt-5.4": {
              params: { transport: "auto" },
            },
          },
        },
      },
    }
    ```

    関連する OpenAI ドキュメント:
    - [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
    - [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

  </Accordion>

  <Accordion title="WebSocket warm-up">
    OpenClaw は、初回 turn のレイテンシを減らすために、`openai/*` 向けでデフォルトで WebSocket warm-up を有効にしています。

    ```json5
    // warm-up を無効化
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: { openaiWsWarmup: false },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Fast mode">
    OpenClaw は、`openai/*` と `openai-codex/*` の両方に対して共有の fast-mode 切り替えを提供します:

    - **Chat/UI:** `/fast status|on|off`
    - **Config:** `agents.defaults.models["<provider>/<model>"].params.fastMode`

    有効にすると、OpenClaw は fast mode を OpenAI の priority processing（`service_tier = "priority"`）にマッピングします。既存の `service_tier` 値は保持され、fast mode は `reasoning` や `text.verbosity` を書き換えません。

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": { params: { fastMode: true } },
            "openai-codex/gpt-5.4": { params: { fastMode: true } },
          },
        },
      },
    }
    ```

    <Note>
    セッション上書きは config より優先されます。Sessions UI でセッション上書きをクリアすると、そのセッションは設定済みのデフォルトに戻ります。
    </Note>

  </Accordion>

  <Accordion title="Priority processing (service_tier)">
    OpenAI の API は、`service_tier` によって priority processing を公開しています。OpenClaw ではモデルごとに設定できます:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": { params: { serviceTier: "priority" } },
            "openai-codex/gpt-5.4": { params: { serviceTier: "priority" } },
          },
        },
      },
    }
    ```

    サポートされる値: `auto`、`default`、`flex`、`priority`。

    <Warning>
    `serviceTier` は、ネイティブ OpenAI エンドポイント（`api.openai.com`）およびネイティブ Codex エンドポイント（`chatgpt.com/backend-api`）にのみ転送されます。いずれかの provider をプロキシ経由でルーティングしている場合、OpenClaw は `service_tier` を変更しません。
    </Warning>

  </Accordion>

  <Accordion title="Server-side compaction (Responses API)">
    direct OpenAI Responses モデル（`api.openai.com` 上の `openai/*`）では、OpenClaw は server-side Compaction を自動で有効化します:

    - `store: true` を強制する（モデル互換性で `supportsStore: false` が設定されている場合を除く）
    - `context_management: [{ type: "compaction", compact_threshold: ... }]` を注入する
    - デフォルトの `compact_threshold`: `contextWindow` の 70%（利用できない場合は `80000`）

    <Tabs>
      <Tab title="Enable explicitly">
        Azure OpenAI Responses のような互換エンドポイントで有用です:

        ```json5
        {
          agents: {
            defaults: {
              models: {
                "azure-openai-responses/gpt-5.4": {
                  params: { responsesServerCompaction: true },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="Custom threshold">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: {
                    responsesServerCompaction: true,
                    responsesCompactThreshold: 120000,
                  },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="Disable">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: { responsesServerCompaction: false },
                },
              },
            },
          },
        }
        ```
      </Tab>
    </Tabs>

    <Note>
    `responsesServerCompaction` は `context_management` の注入だけを制御します。direct OpenAI Responses モデルは、互換性で `supportsStore: false` が設定されていない限り、引き続き `store: true` を強制します。
    </Note>

  </Accordion>

  <Accordion title="Strict-agentic GPT mode">
    `openai/*` および `openai-codex/*` 上の GPT-5 ファミリーの実行では、OpenClaw はより厳格な埋め込み実行 contract を使用できます:

    ```json5
    {
      agents: {
        defaults: {
          embeddedPi: { executionContract: "strict-agentic" },
        },
      },
    }
    ```

    `strict-agentic` では、OpenClaw は次のように動作します:
    - tool action が利用可能な場合、plan のみの turn を成功した進捗として扱わなくなる
    - act-now の steer を付けて turn を再試行する
    - 大きな作業では `update_plan` を自動で有効にする
    - モデルが行動せず計画を続ける場合は、明示的な blocked state を表示する

    <Note>
    OpenAI と Codex の GPT-5 ファミリーの実行にのみ適用されます。他の provider と古いモデルファミリーはデフォルトの動作を維持します。
    </Note>

  </Accordion>

  <Accordion title="Native vs OpenAI-compatible routes">
    OpenClaw は、direct OpenAI、Codex、Azure OpenAI エンドポイントを、汎用の OpenAI 互換 `/v1` プロキシとは異なるものとして扱います:

    **ネイティブルート**（`openai/*`、`openai-codex/*`、Azure OpenAI）:
    - reasoning が明示的に無効化されている場合、`reasoning: { effort: "none" }` をそのまま維持する
    - tool schema をデフォルトで strict mode にする
    - 検証済みのネイティブ host にのみ隠し attribution header を付与する
    - OpenAI 専用のリクエスト整形（`service_tier`、`store`、reasoning 互換性、prompt-cache ヒント）を維持する

    **プロキシ/互換ルート:**
    - より緩い互換動作を使用する
    - strict な tool schema やネイティブ専用 header を強制しない

    Azure OpenAI はネイティブの transport と互換動作を使用しますが、隠し attribution header は受け取りません。

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Image generation" href="/ja-JP/tools/image-generation" icon="image">
    共有画像 tool パラメーターと provider 選択。
  </Card>
  <Card title="Video generation" href="/ja-JP/tools/video-generation" icon="video">
    共有 video tool パラメーターと provider 選択。
  </Card>
  <Card title="OAuth and auth" href="/ja-JP/gateway/authentication" icon="key">
    認証の詳細と資格情報の再利用ルール。
  </Card>
</CardGroup>
