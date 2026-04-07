---
read_when:
    - agent経由で音楽または音声を生成している
    - 音楽生成providerとmodelを設定している
    - music_generate toolのパラメーターを理解したい
summary: workflowベースpluginを含む共有providerで音楽を生成する
title: 音楽生成
x-i18n:
    generated_at: "2026-04-07T04:47:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: ce8da8dfc188efe8593ca5cbec0927dd1d18d2861a1a828df89c8541ccf1cb25
    source_path: tools/music-generation.md
    workflow: 15
---

# 音楽生成

`music_generate` toolを使うと、agentはGoogle、
MiniMax、workflow設定されたComfyUIなどのproviderを通じて、共有music-generation capabilityで音楽または音声を作成できます。

共有provider対応のagent sessionでは、OpenClawは音楽生成を
バックグラウンドタスクとして開始し、それをtask ledgerで追跡し、その後
トラックの準備ができたときにagentを再度起こして、完成した音声を元の
channelに返せるようにします。

<Note>
少なくとも1つのmusic-generation providerが利用可能な場合にのみ、組み込みの共有toolが表示されます。agentのtoolsに `music_generate` が表示されない場合は、`agents.defaults.musicGenerationModel` を設定するか、provider APIキーを設定してください。
</Note>

## クイックスタート

### 共有provider対応の生成

1. 少なくとも1つのproviderにAPIキーを設定します。たとえば `GEMINI_API_KEY` または
   `MINIMAX_API_KEY` です。
2. 必要に応じて、好みのmodelを設定します:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

3. agentにこう依頼します: _「ネオンの街を夜にドライブすることをテーマにした、アップビートなシンセポップのトラックを生成して。」_

agentは自動的に `music_generate` を呼び出します。toolのallow-list登録は不要です。

sessionに紐づくagent実行がない直接の同期コンテキストでは、組み込み
toolは引き続きインライン生成にフォールバックし、最終的なmedia pathをtool結果として返します。

プロンプト例:

```text
Generate a cinematic piano track with soft strings and no vocals.
```

```text
Generate an energetic chiptune loop about launching a rocket at sunrise.
```

### Workflow駆動のComfy生成

バンドルされた `comfy` pluginは、
music-generation provider registryを通じて共有 `music_generate` toolに接続されます。

1. `models.providers.comfy.music` にworkflow JSONと
   prompt/output nodeを設定します。
2. Comfy Cloudを使う場合は、`COMFY_API_KEY` または `COMFY_CLOUD_API_KEY` を設定します。
3. agentに音楽生成を依頼するか、toolを直接呼び出します。

例:

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

## 共有バンドルproviderサポート

| Provider | デフォルトmodel       | 参照入力       | サポートされる制御                                      | APIキー                                |
| -------- | --------------------- | -------------- | ------------------------------------------------------- | -------------------------------------- |
| ComfyUI  | `workflow`            | 最大1枚の画像  | workflow定義の音楽または音声                            | `COMFY_API_KEY`, `COMFY_CLOUD_API_KEY` |
| Google   | `lyria-3-clip-preview` | 最大10枚の画像 | `lyrics`, `instrumental`, `format`                      | `GEMINI_API_KEY`, `GOOGLE_API_KEY`     |
| MiniMax  | `music-2.5+`          | なし           | `lyrics`, `instrumental`, `durationSeconds`, `format=mp3` | `MINIMAX_API_KEY`                      |

### 宣言されたcapabilityマトリクス

これは `music_generate`、contract test、
共有live sweepで使われる明示的なmode contractです。

| Provider | `generate` | `edit` | Edit上限 | 共有liveレーン                                                           |
| -------- | ---------- | ------ | -------- | ------------------------------------------------------------------------ |
| ComfyUI  | Yes        | Yes    | 1 image  | 共有sweepには含まれない。`extensions/comfy/comfy.live.test.ts` でカバー |
| Google   | Yes        | Yes    | 10 images | `generate`, `edit`                                                       |
| MiniMax  | Yes        | No     | None     | `generate`                                                               |

利用可能な共有providerとmodelを実行時に確認するには、
`action: "list"` を使用します:

```text
/tool music_generate action=list
```

現在のsessionに紐づく音楽タスクを確認するには、
`action: "status"` を使用します:

```text
/tool music_generate action=status
```

直接生成の例:

```text
/tool music_generate prompt="Dreamy lo-fi hip hop with vinyl texture and gentle rain" instrumental=true
```

## 組み込みtoolパラメーター

| パラメーター       | 型       | 説明                                                                                         |
| ------------------ | -------- | -------------------------------------------------------------------------------------------- |
| `prompt`           | string   | 音楽生成プロンプト（`action: "generate"` では必須）                                          |
| `action`           | string   | `"generate"`（デフォルト）、現在のsession task用の `"status"`、またはprovider確認用の `"list"` |
| `model`            | string   | provider/modelのオーバーライド。例: `google/lyria-3-pro-preview` または `comfy/workflow`      |
| `lyrics`           | string   | providerが明示的な歌詞入力をサポートしている場合の任意の歌詞                                 |
| `instrumental`     | boolean  | providerがサポートしている場合、インストゥルメンタルのみの出力を要求する                      |
| `image`            | string   | 単一の参照画像パスまたはURL                                                                   |
| `images`           | string[] | 複数の参照画像（最大10枚）                                                                    |
| `durationSeconds`  | number   | providerが長さヒントをサポートしている場合の目標秒数                                         |
| `format`           | string   | providerがサポートしている場合の出力形式ヒント（`mp3` または `wav`）                          |
| `filename`         | string   | 出力ファイル名ヒント                                                                           |

すべてのproviderがすべてのパラメーターをサポートするわけではありません。OpenClawはそれでも、
送信前に入力数などの厳格な制限を検証します。providerがdurationをサポートしていても、
要求値より短い最大値を使う場合、OpenClawは自動的に最も近いサポート値にクランプします。本当に未対応の任意ヒントは、選択されたproviderまたはmodelで適用できない場合、警告付きで無視されます。

tool結果には適用された設定が報告されます。providerフォールバック中にOpenClawがdurationをクランプした場合、返される `durationSeconds` は送信された値を反映し、`details.normalization.durationSeconds` には要求値から適用値への対応が表示されます。

## 共有provider対応経路の非同期動作

- sessionに紐づくagent実行: `music_generate` はバックグラウンドタスクを作成し、開始済み/task応答をすぐ返し、後でフォローアップagentメッセージとして完成したトラックを投稿します。
- 重複防止: そのバックグラウンドタスクがまだ `queued` または `running` の間は、同じsessionで後から呼ばれた `music_generate` は別の生成を開始せず、task statusを返します。
- status確認: 新しい生成を始めずに、アクティブなsession音楽タスクを確認するには `action: "status"` を使います。
- task追跡: 生成の `queued`、`running`、終了状態を確認するには `openclaw tasks list` または `openclaw tasks show <taskId>` を使います。
- 完了wake: OpenClawは同じsessionに内部完了イベントを注入し、model自身がユーザー向けのフォローアップを書けるようにします。
- プロンプトヒント: 同じsessionで後から行うユーザー/手動ターンには、音楽taskがすでに進行中であることを示す小さなruntime hintが付き、modelがむやみに `music_generate` を再度呼ばないようにします。
- no-sessionフォールバック: 実際のagent sessionがない直接/localコンテキストでは、引き続きインラインで実行し、同じターン内で最終音声結果を返します。

### Taskライフサイクル

各 `music_generate` リクエストは4つの状態を移動します:

1. **queued** -- taskが作成され、providerが受け付けるのを待っている。
2. **running** -- providerが処理中（通常はproviderとdurationに応じて30秒から3分）。
3. **succeeded** -- トラックの準備完了。agentが起きて会話に投稿する。
4. **failed** -- providerエラーまたはタイムアウト。agentがエラー詳細とともに起きる。

CLIからstatusを確認します:

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

重複防止: 現在のsessionですでに音楽taskが `queued` または `running` である場合、`music_generate` は新しいものを開始せずに既存taskのstatusを返します。新しい生成を発火せず明示的に確認するには `action: "status"` を使ってください。

## 設定

### Model選択

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
        fallbacks: ["minimax/music-2.5+"],
      },
    },
  },
}
```

### Provider選択順

音楽生成時、OpenClawは次の順でproviderを試します:

1. agentが指定した場合、tool callの `model` パラメーター
2. configの `musicGenerationModel.primary`
3. 順番どおりの `musicGenerationModel.fallbacks`
4. 認証済みproviderデフォルトのみを使う自動検出:
   - 現在のデフォルトproviderを最優先
   - 残りの登録済みmusic-generation providerをprovider-id順

providerが失敗した場合、次の候補が自動で試されます。すべて失敗した場合、
エラーには各試行の詳細が含まれます。

音楽生成で明示的な `model`、`primary`、`fallbacks`
エントリのみを使いたい場合は、`agents.defaults.mediaGenerationAutoProviderFallback: false` を設定してください。

## Providerに関する注記

- GoogleはLyria 3のバッチ生成を使用します。現在のバンドルフローは
  prompt、任意の歌詞テキスト、任意の参照画像をサポートします。
- MiniMaxはバッチ `music_generation` endpointを使用します。現在のバンドルフローは
  prompt、任意の歌詞、instrumental mode、duration調整、
  mp3出力をサポートします。
- ComfyUIサポートはworkflow駆動であり、設定されたgraphと
  prompt/output field向けnode mappingに依存します。

## Provider capability mode

共有music-generation contractは、明示的なmode宣言をサポートするようになりました:

- promptのみの生成に対する `generate`
- 1枚以上の参照画像を含むリクエストに対する `edit`

新しいprovider実装では、明示的なmode blockを優先してください:

```typescript
capabilities: {
  generate: {
    maxTracks: 1,
    supportsLyrics: true,
    supportsFormat: true,
  },
  edit: {
    enabled: true,
    maxTracks: 1,
    maxInputImages: 1,
    supportsFormat: true,
  },
}
```

従来のフラットfieldである `maxInputImages`、`supportsLyrics`、
`supportsFormat` だけでは、editサポートの告知には不十分です。providerは
`generate` と `edit` を明示的に宣言し、live test、contract test、
共有 `music_generate` toolがmodeサポートを決定的に検証できるようにする必要があります。

## 適切な経路の選び方

- model選択、provider failover、組み込みの非同期task/statusフローが必要なら、共有provider対応経路を使ってください。
- カスタムworkflow graphや、共有バンドル音楽capabilityに含まれないproviderが必要な場合は、ComfyUIのようなplugin経路を使ってください。
- ComfyUI固有の動作をデバッグする場合は [ComfyUI](/ja-JP/providers/comfy) を参照してください。共有provider動作をデバッグする場合は、[Google (Gemini)](/ja-JP/providers/google) または [MiniMax](/ja-JP/providers/minimax) から始めてください。

## Live test

共有バンドルprovider向けのオプトインliveカバレッジ:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts
```

リポジトリwrapper:

```bash
pnpm test:live:media music
```

このlive fileは、デフォルトで不足しているprovider env varsを `~/.profile` から読み込み、
通常は保存済みauth profileより先にlive/env APIキーを優先し、
providerがedit modeを有効にしている場合は `generate` と宣言された `edit` の両方を実行します。

現在の対象は:

- `google`: `generate` と `edit`
- `minimax`: `generate` のみ
- `comfy`: 別個のComfy liveカバレッジであり、共有provider sweepではない

バンドルComfyUI音楽経路向けのオプトインliveカバレッジ:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

Comfy live fileは、それらの
セクションが設定されている場合、comfy画像および動画workflowもカバーします。

## 関連

- [Background Tasks](/ja-JP/automation/tasks) - 分離された `music_generate` 実行のtask追跡
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults) - `musicGenerationModel` config
- [ComfyUI](/ja-JP/providers/comfy)
- [Google (Gemini)](/ja-JP/providers/google)
- [MiniMax](/ja-JP/providers/minimax)
- [Models](/ja-JP/concepts/models) - model設定とfailover
- [Tools Overview](/ja-JP/tools)
