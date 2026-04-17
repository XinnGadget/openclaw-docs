---
read_when:
    - OpenClaw で Qwen を使いたい場合
    - 以前 Qwen OAuth を使っていた場合
summary: OpenClaw にバンドルされた qwen provider を使って Qwen Cloud を利用する
title: Qwen
x-i18n:
    generated_at: "2026-04-12T23:33:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5247f851ef891645df6572d748ea15deeea47cd1d75858bc0d044a2930065106
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**Qwen OAuth は削除されました。** `portal.qwen.ai` エンドポイントを使用していた無料枠の OAuth 統合
（`qwen-portal`）は、もう利用できません。背景については
[Issue #49557](https://github.com/openclaw/openclaw/issues/49557) を参照してください。

</Warning>

OpenClaw は現在、Qwen を正式な ID
`qwen` を持つ一級のバンドル provider として扱います。バンドル provider は Qwen Cloud / Alibaba DashScope および
Coding Plan エンドポイントを対象とし、互換性エイリアスとして従来の `modelstudio` ID も引き続き動作させます。

- Provider: `qwen`
- 推奨 env var: `QWEN_API_KEY`
- 互換性のために受け付けられるもの: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- API スタイル: OpenAI 互換

<Tip>
`qwen3.6-plus` を使いたい場合は、**Standard（従量課金）**エンドポイントを推奨します。
Coding Plan のサポートは公開カタログより遅れることがあります。
</Tip>

## はじめに

プラン種別を選び、セットアップ手順に従ってください。

<Tabs>
  <Tab title="Coding Plan（サブスクリプション）">
    **最適な用途:** Qwen Coding Plan を通じたサブスクリプションベースのアクセス。

    <Steps>
      <Step title="API キーを取得する">
        [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys) で API キーを作成またはコピーします。
      </Step>
      <Step title="オンボーディングを実行する">
        **Global** エンドポイントの場合:

        ```bash
        openclaw onboard --auth-choice qwen-api-key
        ```

        **China** エンドポイントの場合:

        ```bash
        openclaw onboard --auth-choice qwen-api-key-cn
        ```
      </Step>
      <Step title="デフォルトモデルを設定する">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="モデルが利用可能であることを確認する">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    従来の `modelstudio-*` 認証選択肢 ID と `modelstudio/...` モデル参照も
    互換性エイリアスとして引き続き動作しますが、新しいセットアップフローでは正式な
    `qwen-*` 認証選択肢 ID と `qwen/...` モデル参照を使うことを推奨します。
    </Note>

  </Tab>

  <Tab title="Standard（従量課金）">
    **最適な用途:** `qwen3.6-plus` のように Coding Plan では利用できない可能性があるモデルを含む、Standard Model Studio エンドポイント経由の従量課金アクセス。

    <Steps>
      <Step title="API キーを取得する">
        [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys) で API キーを作成またはコピーします。
      </Step>
      <Step title="オンボーディングを実行する">
        **Global** エンドポイントの場合:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key
        ```

        **China** エンドポイントの場合:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key-cn
        ```
      </Step>
      <Step title="デフォルトモデルを設定する">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="モデルが利用可能であることを確認する">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    従来の `modelstudio-*` 認証選択肢 ID と `modelstudio/...` モデル参照も
    互換性エイリアスとして引き続き動作しますが、新しいセットアップフローでは正式な
    `qwen-*` 認証選択肢 ID と `qwen/...` モデル参照を使うことを推奨します。
    </Note>

  </Tab>
</Tabs>

## プラン種別とエンドポイント

| プラン | リージョン | 認証選択肢 | エンドポイント |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard（従量課金） | China | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1` |
| Standard（従量課金） | Global | `qwen-standard-api-key` | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan（サブスクリプション） | China | `qwen-api-key-cn` | `coding.dashscope.aliyuncs.com/v1` |
| Coding Plan（サブスクリプション） | Global | `qwen-api-key` | `coding-intl.dashscope.aliyuncs.com/v1` |

provider は認証選択肢に基づいてエンドポイントを自動選択します。正式な
選択肢は `qwen-*` 系列を使用し、`modelstudio-*` は互換性専用です。
設定のカスタム `baseUrl` で上書きすることもできます。

<Tip>
**キー管理:** [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys) |
**ドキュメント:** [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)
</Tip>

## 組み込みカタログ

OpenClaw は現在、このバンドルされた Qwen カタログを同梱しています。設定されたカタログは
エンドポイント対応で、Coding Plan 設定では Standard エンドポイントでのみ動作が確認されているモデルは省略されます。

| モデル参照 | 入力 | コンテキスト | 注記 |
| --------------------------- | ----------- | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus` | text, image | 1,000,000 | デフォルトモデル |
| `qwen/qwen3.6-plus` | text, image | 1,000,000 | このモデルが必要な場合は Standard エンドポイントを推奨 |
| `qwen/qwen3-max-2026-01-23` | text | 262,144 | Qwen Max 系統 |
| `qwen/qwen3-coder-next` | text | 262,144 | Coding |
| `qwen/qwen3-coder-plus` | text | 1,000,000 | Coding |
| `qwen/MiniMax-M2.5` | text | 1,000,000 | 推論有効 |
| `qwen/glm-5` | text | 202,752 | GLM |
| `qwen/glm-4.7` | text | 202,752 | GLM |
| `qwen/kimi-k2.5` | text, image | 262,144 | Alibaba 経由の Moonshot AI |

<Note>
モデルがバンドルカタログに存在していても、利用可否はエンドポイントと課金プランによって変わる場合があります。
</Note>

## マルチモーダル拡張

`qwen` 拡張機能は、**Standard**
DashScope エンドポイント（Coding Plan エンドポイントではありません）で、マルチモーダル capability も公開します。

- **動画理解** は `qwen-vl-max-latest` 経由
- **Wan 動画生成** は `wan2.6-t2v`（デフォルト）、`wan2.6-i2v`、`wan2.6-r2v`、`wan2.6-r2v-flash`、`wan2.7-r2v` 経由

Qwen をデフォルトの動画 provider として使用するには:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

<Note>
共有ツールパラメーター、provider 選択、およびフェイルオーバー動作については、[Video Generation](/ja-JP/tools/video-generation) を参照してください。
</Note>

## 高度な内容

<AccordionGroup>
  <Accordion title="画像と動画の理解">
    バンドルされた Qwen Plugin は、**Standard** DashScope エンドポイント
    （Coding Plan エンドポイントではありません）で、画像と動画の
    media understanding を登録します。

    | 項目 | 値 |
    | ------------- | --------------------- |
    | モデル | `qwen-vl-max-latest` |
    | 対応入力 | Images, video |

    media understanding は、設定済みの Qwen 認証から自動解決されるため、
    追加設定は不要です。media understanding サポートには、必ず Standard（従量課金）
    エンドポイントを使用してください。

  </Accordion>

  <Accordion title="Qwen 3.6 Plus の利用可否">
    `qwen3.6-plus` は、Standard（従量課金）Model Studio
    エンドポイントで利用できます。

    - China: `dashscope.aliyuncs.com/compatible-mode/v1`
    - Global: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

    `qwen3.6-plus` に対して Coding Plan エンドポイントが
    「unsupported model」エラーを返す場合は、Coding Plan の
    エンドポイント/キーペアではなく、Standard（従量課金）に切り替えてください。

  </Accordion>

  <Accordion title="capability 計画">
    `qwen` 拡張機能は、単なる coding/text モデルではなく、Qwen
    Cloud 全体のベンダーホームとして位置付けられつつあります。

    - **Text/chat models:** 現在同梱
    - **Tool calling, structured output, thinking:** OpenAI 互換トランスポートから継承
    - **Image generation:** provider Plugin 層で対応予定
    - **Image/video understanding:** Standard エンドポイントで現在同梱
    - **Speech/audio:** provider Plugin 層で対応予定
    - **Memory embeddings/reranking:** 埋め込みアダプターサーフェス経由で対応予定
    - **Video generation:** 共有 video-generation capability を通じて現在同梱

  </Accordion>

  <Accordion title="動画生成の詳細">
    動画生成では、OpenClaw はジョブ送信前に、設定済みの Qwen リージョンを対応する
    DashScope AIGC ホストにマッピングします。

    - Global/Intl: `https://dashscope-intl.aliyuncs.com`
    - China: `https://dashscope.aliyuncs.com`

    つまり、Coding Plan または Standard の Qwen ホストを指す通常の
    `models.providers.qwen.baseUrl` を使っていても、動画生成は正しい
    リージョンの DashScope 動画エンドポイントに送られます。

    現在バンドルされている Qwen 動画生成の制限:

    - リクエストごとに最大 **1** 本の出力動画
    - 最大 **1** 枚の入力画像
    - 最大 **4** 本の入力動画
    - 最大 **10 秒** の長さ
    - `size`、`aspectRatio`、`resolution`、`audio`、`watermark` をサポート
    - 参照画像/動画モードは現在 **リモート http(s) URL** が必要です。DashScope 動画エンドポイントはそれらの参照に対するローカルバッファのアップロードを受け付けないため、ローカルファイルパスは事前に拒否されます。

  </Accordion>

  <Accordion title="ストリーミング usage 互換性">
    ネイティブ Model Studio エンドポイントは、共有の
    `openai-completions` トランスポートでストリーミング usage 互換性を公開します。OpenClaw
    は現在それをエンドポイント capability に基づいて判断するため、同じネイティブホストを対象とする DashScope 互換のカスタム provider ID も、
    組み込みの `qwen` provider ID を特に必要とせず、同じ streaming-usage 動作を引き継ぎます。

    ネイティブストリーミング usage 互換性は、Coding Plan ホストと
    Standard DashScope 互換ホストの両方に適用されます。

    - `https://coding.dashscope.aliyuncs.com/v1`
    - `https://coding-intl.dashscope.aliyuncs.com/v1`
    - `https://dashscope.aliyuncs.com/compatible-mode/v1`
    - `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="マルチモーダルのエンドポイントリージョン">
    マルチモーダルサーフェス（動画理解および Wan 動画生成）は、
    Coding Plan エンドポイントではなく **Standard** DashScope エンドポイントを使用します。

    - Global/Intl Standard base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
    - China Standard base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="環境とデーモンセットアップ">
    Gateway がデーモン（launchd/systemd）として実行される場合は、`QWEN_API_KEY` が
    そのプロセスで利用可能であることを確認してください（たとえば `~/.openclaw/.env` または
    `env.shellEnv` 経由）。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、モデル参照、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Video generation" href="/ja-JP/tools/video-generation" icon="video">
    共有動画ツールパラメーターと provider 選択。
  </Card>
  <Card title="Alibaba (ModelStudio)" href="/ja-JP/providers/alibaba" icon="cloud">
    レガシーな ModelStudio provider と移行メモ。
  </Card>
  <Card title="Troubleshooting" href="/ja-JP/help/troubleshooting" icon="wrench">
    一般的なトラブルシューティングと FAQ。
  </Card>
</CardGroup>
