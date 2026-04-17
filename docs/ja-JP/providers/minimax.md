---
read_when:
    - OpenClaw で MiniMax model を使いたい場合
    - MiniMax のセットアップガイダンスが必要です
summary: OpenClaw で MiniMax model を使う
title: MiniMax
x-i18n:
    generated_at: "2026-04-12T23:32:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: ee9c89faf57384feb66cda30934000e5746996f24b59122db309318f42c22389
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

OpenClaw の MiniMax provider は、デフォルトで **MiniMax M2.7** を使用します。

MiniMax は次も提供します。

- T2A v2 によるバンドル済み音声合成
- `MiniMax-VL-01` によるバンドル済み画像理解
- `music-2.5+` によるバンドル済み音楽生成
- MiniMax Coding Plan 検索 API を通じたバンドル済み `web_search`

provider の分割:

| Provider ID      | 認証    | 機能                                                           |
| ---------------- | ------- | -------------------------------------------------------------- |
| `minimax`        | API key | テキスト、画像生成、画像理解、音声、Web 検索                  |
| `minimax-portal` | OAuth   | テキスト、画像生成、画像理解                                   |

## model ラインナップ

| Model                    | 種類             | 説明                                      |
| ------------------------ | ---------------- | ----------------------------------------- |
| `MiniMax-M2.7`           | Chat（reasoning） | デフォルトのホスト型 reasoning model      |
| `MiniMax-M2.7-highspeed` | Chat（reasoning） | より高速な M2.7 reasoning tier            |
| `MiniMax-VL-01`          | Vision           | 画像理解 model                            |
| `image-01`               | 画像生成         | text-to-image および image-to-image 編集  |
| `music-2.5+`             | 音楽生成         | デフォルトの音楽 model                    |
| `music-2.5`              | 音楽生成         | 以前の音楽生成 tier                       |
| `music-2.0`              | 音楽生成         | レガシー音楽生成 tier                     |
| `MiniMax-Hailuo-2.3`     | 動画生成         | text-to-video および画像参照フロー        |

## はじめに

希望する認証方法を選び、セットアップ手順に従ってください。

<Tabs>
  <Tab title="OAuth (Coding Plan)">
    **最適な用途:** OAuth 経由の MiniMax Coding Plan を使ったクイックセットアップ。API key は不要です。

    <Tabs>
      <Tab title="International">
        <Steps>
          <Step title="オンボーディングを実行">
            ```bash
            openclaw onboard --auth-choice minimax-global-oauth
            ```

            これにより `api.minimax.io` に対して認証します。
          </Step>
          <Step title="model が利用可能であることを確認">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="China">
        <Steps>
          <Step title="オンボーディングを実行">
            ```bash
            openclaw onboard --auth-choice minimax-cn-oauth
            ```

            これにより `api.minimaxi.com` に対して認証します。
          </Step>
          <Step title="model が利用可能であることを確認">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    <Note>
    OAuth セットアップでは `minimax-portal` provider id を使用します。model 参照は `minimax-portal/MiniMax-M2.7` の形式に従います。
    </Note>

    <Tip>
    MiniMax Coding Plan の紹介リンク（10% オフ）: [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
    </Tip>

  </Tab>

  <Tab title="API key">
    **最適な用途:** Anthropic 互換 API を使うホスト型 MiniMax。

    <Tabs>
      <Tab title="International">
        <Steps>
          <Step title="オンボーディングを実行">
            ```bash
            openclaw onboard --auth-choice minimax-global-api
            ```

            これによりベース URL として `api.minimax.io` が設定されます。
          </Step>
          <Step title="model が利用可能であることを確認">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="China">
        <Steps>
          <Step title="オンボーディングを実行">
            ```bash
            openclaw onboard --auth-choice minimax-cn-api
            ```

            これによりベース URL として `api.minimaxi.com` が設定されます。
          </Step>
          <Step title="model が利用可能であることを確認">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    ### 設定例

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "minimax/MiniMax-M2.7" } } },
      models: {
        mode: "merge",
        providers: {
          minimax: {
            baseUrl: "https://api.minimax.io/anthropic",
            apiKey: "${MINIMAX_API_KEY}",
            api: "anthropic-messages",
            models: [
              {
                id: "MiniMax-M2.7",
                name: "MiniMax M2.7",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
                contextWindow: 204800,
                maxTokens: 131072,
              },
              {
                id: "MiniMax-M2.7-highspeed",
                name: "MiniMax M2.7 Highspeed",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0.6, output: 2.4, cacheRead: 0.06, cacheWrite: 0.375 },
                contextWindow: 204800,
                maxTokens: 131072,
              },
            ],
          },
        },
      },
    }
    ```

    <Warning>
    Anthropic 互換のストリーミングパスでは、明示的に `thinking` を自分で設定しない限り、OpenClaw はデフォルトで MiniMax thinking を無効にします。MiniMax のストリーミングエンドポイントは、ネイティブな Anthropic thinking ブロックではなく OpenAI 形式の delta チャンクで `reasoning_content` を出力するため、暗黙的に有効なままにしておくと内部 reasoning が可視出力に漏れる可能性があります。
    </Warning>

    <Note>
    API-key セットアップでは `minimax` provider id を使用します。model 参照は `minimax/MiniMax-M2.7` の形式に従います。
    </Note>

  </Tab>
</Tabs>

## `openclaw configure` で設定する

JSON を編集せずに、対話型設定ウィザードを使って MiniMax を設定します。

<Steps>
  <Step title="ウィザードを起動">
    ```bash
    openclaw configure
    ```
  </Step>
  <Step title="Model/auth を選択">
    メニューから **Model/auth** を選択します。
  </Step>
  <Step title="MiniMax の認証オプションを選ぶ">
    利用可能な MiniMax オプションのいずれかを選択します。

    | Auth choice | 説明 |
    | --- | --- |
    | `minimax-global-oauth` | International OAuth（Coding Plan） |
    | `minimax-cn-oauth` | China OAuth（Coding Plan） |
    | `minimax-global-api` | International API key |
    | `minimax-cn-api` | China API key |

  </Step>
  <Step title="デフォルト model を選ぶ">
    プロンプトが表示されたら、デフォルト model を選択します。
  </Step>
</Steps>

## 機能

### 画像生成

MiniMax Plugin は、`image_generate` ツール用に `image-01` model を登録します。対応内容:

- アスペクト比制御付きの **text-to-image 生成**
- アスペクト比制御付きの **image-to-image 編集**（被写体参照）
- リクエストごとに最大 **9 枚の出力画像**
- 編集リクエストごとに最大 **1 枚の参照画像**
- 対応アスペクト比: `1:1`、`16:9`、`4:3`、`3:2`、`2:3`、`3:4`、`9:16`、`21:9`

画像生成に MiniMax を使うには、画像生成 provider として設定してください。

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

Plugin は、テキスト model と同じ `MINIMAX_API_KEY` または OAuth 認証を使います。MiniMax がすでにセットアップ済みであれば、追加設定は不要です。

`minimax` と `minimax-portal` はどちらも、同じ
`image-01` model で `image_generate` を登録します。API-key セットアップでは `MINIMAX_API_KEY` を使い、OAuth セットアップでは
バンドル済みの `minimax-portal` 認証パスを代わりに使えます。

オンボーディングまたは API-key セットアップで明示的な `models.providers.minimax`
エントリが書き込まれると、OpenClaw は `MiniMax-M2.7` と
`MiniMax-M2.7-highspeed` を `input: ["text", "image"]` 付きで具体化します。

組み込みのバンドル済み MiniMax テキスト catalog 自体は、
その明示的な provider 設定が存在するまではテキスト専用メタデータのままです。
画像理解は、Plugin 所有の `MiniMax-VL-01` メディア provider を通じて別途公開されます。

<Note>
共有ツールパラメータ、provider 選択、およびフェイルオーバーの挙動については、[Image Generation](/ja-JP/tools/image-generation) を参照してください。
</Note>

### 音楽生成

バンドル済みの `minimax` Plugin は、共有
`music_generate` ツールを通じて音楽生成も登録します。

- デフォルトの音楽 model: `minimax/music-2.5+`
- `minimax/music-2.5` および `minimax/music-2.0` もサポート
- プロンプト制御: `lyrics`、`instrumental`、`durationSeconds`
- 出力形式: `mp3`
- セッションバック実行は、`action: "status"` を含む共有 task/status フローを通じて分離実行される

MiniMax をデフォルトの音楽 provider として使うには:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "minimax/music-2.5+",
      },
    },
  },
}
```

<Note>
共有ツールパラメータ、provider 選択、およびフェイルオーバーの挙動については、[Music Generation](/ja-JP/tools/music-generation) を参照してください。
</Note>

### 動画生成

バンドル済みの `minimax` Plugin は、共有
`video_generate` ツールを通じて動画生成も登録します。

- デフォルトの動画 model: `minimax/MiniMax-Hailuo-2.3`
- モード: text-to-video および単一画像参照フロー
- `aspectRatio` と `resolution` をサポート

MiniMax をデフォルトの動画 provider として使うには:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "minimax/MiniMax-Hailuo-2.3",
      },
    },
  },
}
```

<Note>
共有ツールパラメータ、provider 選択、およびフェイルオーバーの挙動については、[Video Generation](/ja-JP/tools/video-generation) を参照してください。
</Note>

### 画像理解

MiniMax Plugin は、テキスト
catalog とは別に画像理解を登録します。

| Provider ID      | デフォルトの画像 model |
| ---------------- | ------------------- |
| `minimax`        | `MiniMax-VL-01`     |
| `minimax-portal` | `MiniMax-VL-01`     |

そのため、バンドル済みテキスト provider catalog にテキスト専用の M2.7 chat 参照しか表示されていない場合でも、
自動メディアルーティングは MiniMax の画像理解を利用できます。

### Web 検索

MiniMax Plugin は、MiniMax Coding Plan
検索 API を通じて `web_search` も登録します。

- provider id: `minimax`
- 構造化結果: タイトル、URL、スニペット、関連クエリ
- 推奨される環境変数: `MINIMAX_CODE_PLAN_KEY`
- 受け入れられる環境変数エイリアス: `MINIMAX_CODING_API_KEY`
- 互換性フォールバック: すでに coding-plan トークンを指している場合の `MINIMAX_API_KEY`
- リージョン再利用: `plugins.entries.minimax.config.webSearch.region`、次に `MINIMAX_API_HOST`、その後 MiniMax provider base URL
- 検索は provider id `minimax` のまま維持されるため、OAuth の CN/global セットアップでも `models.providers.minimax-portal.baseUrl` を通じて間接的にリージョンを制御できます

設定は `plugins.entries.minimax.config.webSearch.*` 配下にあります。

<Note>
Web 検索の完全な設定と使用方法については、[MiniMax Search](/ja-JP/tools/minimax-search) を参照してください。
</Note>

## 高度な設定

<AccordionGroup>
  <Accordion title="設定オプション">
    | Option | 説明 |
    | --- | --- |
    | `models.providers.minimax.baseUrl` | `https://api.minimax.io/anthropic` を推奨（Anthropic 互換）。`https://api.minimax.io/v1` は OpenAI 互換ペイロード用の任意設定 |
    | `models.providers.minimax.api` | `anthropic-messages` を推奨。`openai-completions` は OpenAI 互換ペイロード用の任意設定 |
    | `models.providers.minimax.apiKey` | MiniMax API key（`MINIMAX_API_KEY`） |
    | `models.providers.minimax.models` | `id`、`name`、`reasoning`、`contextWindow`、`maxTokens`、`cost` を定義 |
    | `agents.defaults.models` | allowlist に入れたい model のエイリアス |
    | `models.mode` | 組み込み model と並べて MiniMax を追加したい場合は `merge` を維持 |
  </Accordion>

  <Accordion title="thinking のデフォルト">
    `api: "anthropic-messages"` では、パラメータ/設定で thinking がすでに明示的に設定されていない限り、OpenClaw は `thinking: { type: "disabled" }` を注入します。

    これにより、MiniMax のストリーミングエンドポイントが OpenAI 形式の delta チャンクで `reasoning_content` を出力し、内部 reasoning が可視出力に漏れるのを防ぎます。

  </Accordion>

  <Accordion title="高速モード">
    `/fast on` または `params.fastMode: true` は、Anthropic 互換ストリームパス上で `MiniMax-M2.7` を `MiniMax-M2.7-highspeed` に書き換えます。
  </Accordion>

  <Accordion title="フォールバック例">
    **最適な用途:** 最新世代の最も強力な model を primary として維持しつつ、MiniMax M2.7 にフェイルオーバーすること。以下の例では具体的な primary として Opus を使っていますが、好みの最新世代 primary model に置き換えてください。

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-..." },
      agents: {
        defaults: {
          models: {
            "anthropic/claude-opus-4-6": { alias: "primary" },
            "minimax/MiniMax-M2.7": { alias: "minimax" },
          },
          model: {
            primary: "anthropic/claude-opus-4-6",
            fallbacks: ["minimax/MiniMax-M2.7"],
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Coding Plan 使用状況の詳細">
    - Coding Plan 使用状況 API: `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains`（coding plan キーが必要）。
    - OpenClaw は MiniMax coding-plan の使用状況を、他の provider と同じ `% left` 表示に正規化します。MiniMax の生の `usage_percent` / `usagePercent` フィールドは消費済みクォータではなく残りクォータを表すため、OpenClaw はそれらを反転します。件数ベースのフィールドが存在する場合はそちらが優先されます。
    - API が `model_remains` を返す場合、OpenClaw は chat-model エントリを優先し、必要に応じて `start_time` / `end_time` からウィンドウラベルを導出し、選択された model 名をプランラベルに含めることで、coding-plan ウィンドウをより区別しやすくします。
    - 使用状況スナップショットでは、`minimax`、`minimax-cn`、`minimax-portal` を同じ MiniMax クォータサーフェスとして扱い、Coding Plan キーの環境変数にフォールバックする前に、保存済みの MiniMax OAuth を優先します。
  </Accordion>
</AccordionGroup>

## 注記

- model 参照は認証パスに従います:
  - API-key セットアップ: `minimax/<model>`
  - OAuth セットアップ: `minimax-portal/<model>`
- デフォルトの chat model: `MiniMax-M2.7`
- 代替 chat model: `MiniMax-M2.7-highspeed`
- オンボーディングおよび直接の API-key セットアップでは、両方の M2.7 バリアントに対して `input: ["text", "image"]` を含む明示的な model 定義が書き込まれます
- バンドル済み provider catalog は現在、明示的な MiniMax provider 設定が存在するまで、chat 参照をテキスト専用メタデータとして公開します
- 正確なコスト追跡が必要な場合は、`models.json` の料金値を更新してください
- 現在の provider id を確認するには `openclaw models list` を使い、その後 `openclaw models set minimax/MiniMax-M2.7` または `openclaw models set minimax-portal/MiniMax-M2.7` で切り替えてください

<Tip>
MiniMax Coding Plan の紹介リンク（10% オフ）: [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
</Tip>

<Note>
provider ルールについては、[Model providers](/ja-JP/concepts/model-providers) を参照してください。
</Note>

## トラブルシューティング

<AccordionGroup>
  <Accordion title='"Unknown model: minimax/MiniMax-M2.7"'>
    これは通常、**MiniMax provider が設定されていない** ことを意味します（対応する provider エントリがなく、MiniMax の認証 profile/env キーも見つからない）。この検出の修正は **2026.1.12** に入っています。次のいずれかで修正してください。

    - **2026.1.12** にアップグレードする（またはソースの `main` から実行する）、その後 Gateway を再起動する。
    - `openclaw configure` を実行して **MiniMax** の認証オプションを選択する、または
    - 対応する `models.providers.minimax` または `models.providers.minimax-portal` ブロックを手動で追加する、または
    - 対応する provider を注入できるように、`MINIMAX_API_KEY`、`MINIMAX_OAUTH_TOKEN`、または MiniMax 認証 profile を設定する。

    model id は **大文字小文字を区別する** 点に注意してください。

    - API-key パス: `minimax/MiniMax-M2.7` または `minimax/MiniMax-M2.7-highspeed`
    - OAuth パス: `minimax-portal/MiniMax-M2.7` または `minimax-portal/MiniMax-M2.7-highspeed`

    その後、次で再確認してください。

    ```bash
    openclaw models list
    ```

  </Accordion>
</AccordionGroup>

<Note>
さらにヘルプが必要な場合: [Troubleshooting](/ja-JP/help/troubleshooting) と [FAQ](/ja-JP/help/faq)。
</Note>

## 関連

<CardGroup cols={2}>
  <Card title="model 選択" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model 参照、およびフェイルオーバーの挙動を選択します。
  </Card>
  <Card title="画像生成" href="/ja-JP/tools/image-generation" icon="image">
    共有画像ツールパラメータと provider 選択。
  </Card>
  <Card title="音楽生成" href="/ja-JP/tools/music-generation" icon="music">
    共有音楽ツールパラメータと provider 選択。
  </Card>
  <Card title="動画生成" href="/ja-JP/tools/video-generation" icon="video">
    共有動画ツールパラメータと provider 選択。
  </Card>
  <Card title="MiniMax Search" href="/ja-JP/tools/minimax-search" icon="magnifying-glass">
    MiniMax Coding Plan 経由の Web 検索設定。
  </Card>
  <Card title="トラブルシューティング" href="/ja-JP/help/troubleshooting" icon="wrench">
    一般的なトラブルシューティングと FAQ。
  </Card>
</CardGroup>
