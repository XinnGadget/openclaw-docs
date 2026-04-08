---
read_when:
    - OpenClawでGoogle Geminiモデルを使いたい場合
    - APIキーまたはOAuth認証フローが必要な場合
summary: Google Geminiのセットアップ（APIキー + OAuth、画像生成、メディア理解、web検索）
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-08T02:18:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: e9e558f5ce35c853e0240350be9a1890460c5f7f7fd30b05813a656497dee516
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Googleプラグインは、Google AI Studioを通じたGeminiモデルへのアクセスに加えて、
Gemini Grounding経由の画像生成、メディア理解（画像/音声/動画）、web検索を提供します。

- プロバイダー: `google`
- 認証: `GEMINI_API_KEY` または `GOOGLE_API_KEY`
- API: Google Gemini API
- 代替プロバイダー: `google-gemini-cli`（OAuth）

## クイックスタート

1. APIキーを設定します:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. デフォルトモデルを設定します:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## 非対話の例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## OAuth（Gemini CLI）

代替プロバイダー `google-gemini-cli` は、API
キーの代わりにPKCE OAuthを使います。これは非公式の統合であり、一部のユーザーからは
アカウント制限が報告されています。自己責任で使用してください。

- デフォルトモデル: `google-gemini-cli/gemini-3-flash-preview`
- エイリアス: `gemini-cli`
- インストール前提条件: ローカルのGemini CLIが `gemini` として利用可能であること
  - Homebrew: `brew install gemini-cli`
  - npm: `npm install -g @google/gemini-cli`
- ログイン:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

環境変数:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

（または `GEMINI_CLI_*` バリアント。）

ログイン後にGemini CLI OAuthリクエストが失敗する場合は、
Gatewayホストで `GOOGLE_CLOUD_PROJECT` または `GOOGLE_CLOUD_PROJECT_ID` を設定して
再試行してください。

ブラウザフローが始まる前にログインが失敗する場合は、ローカルの `gemini`
コマンドがインストール済みで `PATH` 上にあることを確認してください。OpenClawは、
Homebrewインストールとグローバルnpmインストールの両方をサポートしており、
一般的なWindows/npm構成も含まれます。

Gemini CLIのJSON使用量に関する注意:

- 返信テキストはCLI JSONの `response` フィールドから取得されます。
- CLIが `usage` を空のままにした場合、使用量は `stats` にフォールバックします。
- `stats.cached` はOpenClawの `cacheRead` に正規化されます。
- `stats.input` がない場合、OpenClawは
  `stats.input_tokens - stats.cached` から入力トークン数を導出します。

## 機能

| 機能 | サポート |
| ---------------------- | ----------------- |
| Chat completions | はい |
| 画像生成 | はい |
| 音楽生成 | はい |
| 画像理解 | はい |
| 音声文字起こし | はい |
| 動画理解 | はい |
| Web検索（Grounding） | はい |
| Thinking/reasoning | はい（Gemini 3.1+） |

## 直接Geminiキャッシュ再利用

直接のGemini API実行（`api: "google-generative-ai"`）では、OpenClawは
設定済みの `cachedContent` ハンドルをGeminiリクエストに渡すようになりました。

- モデルごとまたはグローバルのparamsに、`cachedContent` またはレガシーな `cached_content`
  のいずれかを設定します
- 両方が存在する場合は `cachedContent` が優先されます
- 値の例: `cachedContents/prebuilt-context`
- Geminiのキャッシュヒット使用量は、上流の `cachedContentTokenCount` から
  OpenClawの `cacheRead` に正規化されます

例:

```json5
{
  agents: {
    defaults: {
      models: {
        "google/gemini-2.5-pro": {
          params: {
            cachedContent: "cachedContents/prebuilt-context",
          },
        },
      },
    },
  },
}
```

## 画像生成

バンドルされた `google` 画像生成プロバイダーのデフォルトは
`google/gemini-3.1-flash-image-preview` です。

- `google/gemini-3-pro-image-preview` もサポートしています
- 生成: 1リクエストあたり最大4枚
- 編集モード: 有効、最大5枚の入力画像
- ジオメトリ制御: `size`、`aspectRatio`、`resolution`

OAuth専用の `google-gemini-cli` プロバイダーは、別のテキスト推論
サーフェスです。画像生成、メディア理解、Gemini Groundingは引き続き
`google` provider id に残ります。

Googleをデフォルトの画像プロバイダーとして使うには:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "google/gemini-3.1-flash-image-preview",
      },
    },
  },
}
```

共有ツールのパラメーター、プロバイダー選択、フェイルオーバー動作については、
[画像生成](/ja-JP/tools/image-generation)を参照してください。

## 動画生成

バンドルされた `google` プラグインは、共有
`video_generate` ツールを通じて動画生成も登録します。

- デフォルト動画モデル: `google/veo-3.1-fast-generate-preview`
- モード: text-to-video、image-to-video、single-video reference フロー
- `aspectRatio`、`resolution`、`audio` をサポート
- 現在のduration制限: **4〜8秒**

Googleをデフォルトの動画プロバイダーとして使うには:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
      },
    },
  },
}
```

共有ツールのパラメーター、プロバイダー選択、フェイルオーバー動作については、
[動画生成](/ja-JP/tools/video-generation)を参照してください。

## 音楽生成

バンドルされた `google` プラグインは、共有
`music_generate` ツールを通じて音楽生成も登録します。

- デフォルト音楽モデル: `google/lyria-3-clip-preview`
- `google/lyria-3-pro-preview` もサポートしています
- プロンプト制御: `lyrics` と `instrumental`
- 出力形式: デフォルトは `mp3`、`google/lyria-3-pro-preview` では `wav` も対応
- 参照入力: 最大10枚の画像
- セッションに裏付けられた実行は、`action: "status"` を含む共有タスク/ステータスフローを通じてデタッチされます

Googleをデフォルトの音楽プロバイダーとして使うには:

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

共有ツールのパラメーター、プロバイダー選択、フェイルオーバー動作については、
[音楽生成](/ja-JP/tools/music-generation)を参照してください。

## 環境に関する注意

Gatewayがデーモン（launchd/systemd）として動作する場合は、`GEMINI_API_KEY`
がそのプロセスから利用可能であることを確認してください（たとえば `~/.openclaw/.env` または
`env.shellEnv` 経由）。
