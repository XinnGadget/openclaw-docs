---
read_when:
    - プラグインをインストールまたは設定するとき
    - プラグインの検出と読み込みルールを理解したいとき
    - Codex/Claude互換のプラグインバンドルを扱うとき
sidebarTitle: Install and Configure
summary: OpenClawプラグインをインストール、設定、管理する
title: プラグイン
x-i18n:
    generated_at: "2026-04-06T03:14:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e2472a3023f3c1c6ee05b0cdc228f6b713cc226a08695b327de8a3ad6973c83
    source_path: tools/plugin.md
    workflow: 15
---

# プラグイン

プラグインは、OpenClawに新しい機能を追加します。チャンネル、モデルprovider、
tools、Skills、speech、realtime transcription、realtime voice、
media-understanding、画像生成、動画生成、web fetch、web
search などです。一部のプラグインは **core**（OpenClawに同梱）で、その他は
**external**（コミュニティがnpmで公開）です。

## クイックスタート

<Steps>
  <Step title="読み込まれているものを確認する">
    ```bash
    openclaw plugins list
    ```
  </Step>

  <Step title="プラグインをインストールする">
    ```bash
    # npm から
    openclaw plugins install @openclaw/voice-call

    # ローカルディレクトリまたはアーカイブから
    openclaw plugins install ./my-plugin
    openclaw plugins install ./my-plugin.tgz
    ```

  </Step>

  <Step title="Gatewayを再起動する">
    ```bash
    openclaw gateway restart
    ```

    その後、設定ファイル内の `plugins.entries.\<id\>.config` 配下で設定します。

  </Step>
</Steps>

チャットネイティブな操作を好む場合は、`commands.plugins: true` を有効にして、次を使ってください。

```text
/plugin install clawhub:@openclaw/voice-call
/plugin show voice-call
/plugin enable voice-call
```

インストールパスはCLIと同じリゾルバーを使います。ローカルパス/アーカイブ、明示的な
`clawhub:<pkg>`、または素のパッケージ指定（まずClawHub、その後npmへフォールバック）です。

configが無効な場合、通常インストールはfail closedし、
`openclaw doctor --fix` を案内します。唯一の回復例外は、次にオプトインしているプラグイン向けの狭い範囲のバンドルプラグイン
再インストールパスです。
`openclaw.install.allowInvalidConfigRecovery`

## プラグインの種類

OpenClawは2つのプラグイン形式を認識します。

| Format     | 動作の仕組み | 例 |
| ---------- | ------------ | --- |
| **Native** | `openclaw.plugin.json` + ランタイムモジュール。インプロセスで実行 | 公式プラグイン、コミュニティのnpmパッケージ |
| **Bundle** | Codex/Claude/Cursor互換レイアウト。OpenClaw機能にマッピングされる | `.codex-plugin/`, `.claude-plugin/`, `.cursor-plugin/` |

どちらも `openclaw plugins list` に表示されます。バンドルの詳細は [Plugin Bundles](/ja-JP/plugins/bundles) を参照してください。

Nativeプラグインを書く場合は、[Building Plugins](/ja-JP/plugins/building-plugins)
と [Plugin SDK Overview](/ja-JP/plugins/sdk-overview) から始めてください。

## 公式プラグイン

### インストール可能（npm）

| Plugin          | Package                | Docs                                 |
| --------------- | ---------------------- | ------------------------------------ |
| Matrix          | `@openclaw/matrix`     | [Matrix](/ja-JP/channels/matrix)           |
| Microsoft Teams | `@openclaw/msteams`    | [Microsoft Teams](/ja-JP/channels/msteams) |
| Nostr           | `@openclaw/nostr`      | [Nostr](/ja-JP/channels/nostr)             |
| Voice Call      | `@openclaw/voice-call` | [Voice Call](/ja-JP/plugins/voice-call)    |
| Zalo            | `@openclaw/zalo`       | [Zalo](/ja-JP/channels/zalo)               |
| Zalo Personal   | `@openclaw/zalouser`   | [Zalo Personal](/ja-JP/plugins/zalouser)   |

### Core（OpenClawに同梱）

<AccordionGroup>
  <Accordion title="モデルprovider（デフォルトで有効）">
    `anthropic`, `byteplus`, `cloudflare-ai-gateway`, `github-copilot`, `google`,
    `huggingface`, `kilocode`, `kimi-coding`, `minimax`, `mistral`, `qwen`,
    `moonshot`, `nvidia`, `openai`, `opencode`, `opencode-go`, `openrouter`,
    `qianfan`, `synthetic`, `together`, `venice`,
    `vercel-ai-gateway`, `volcengine`, `xiaomi`, `zai`
  </Accordion>

  <Accordion title="Memoryプラグイン">
    - `memory-core` — バンドル済みmemory search（デフォルトは `plugins.slots.memory` 経由）
    - `memory-lancedb` — オンデマンドインストール型の長期メモリー。auto-recall/capture付き（`plugins.slots.memory = "memory-lancedb"` を設定）
  </Accordion>

  <Accordion title="speech provider（デフォルトで有効）">
    `elevenlabs`, `microsoft`
  </Accordion>

  <Accordion title="その他">
    - `browser` — browser tool、`openclaw browser` CLI、`browser.request` Gatewayメソッド、browser runtime、およびデフォルトbrowser control service 用のバンドル済みbrowserプラグイン（デフォルトで有効。置き換える前に無効化してください）
    - `copilot-proxy` — VS Code Copilot Proxyブリッジ（デフォルトで無効）
  </Accordion>
</AccordionGroup>

サードパーティプラグインを探していますか？ [Community Plugins](/ja-JP/plugins/community) を参照してください。

## 設定

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: ["untrusted-plugin"],
    load: { paths: ["~/Projects/oss/voice-call-extension"] },
    entries: {
      "voice-call": { enabled: true, config: { provider: "twilio" } },
    },
  },
}
```

| Field            | 説明 |
| ---------------- | ---- |
| `enabled`        | マスタートグル（デフォルト: `true`） |
| `allow`          | プラグイン許可リスト（任意） |
| `deny`           | プラグイン拒否リスト（任意。denyが優先） |
| `load.paths`     | 追加のプラグインファイル/ディレクトリ |
| `slots`          | 排他的スロットセレクター（例: `memory`, `contextEngine`） |
| `entries.\<id\>` | プラグインごとのトグル + config |

config変更には **Gatewayの再起動が必要** です。Gatewayがconfig
watch + インプロセス再起動有効で動作している場合（デフォルトの `openclaw gateway` パス）、
その再起動は通常、config書き込み反映の少し後に自動で実行されます。

<Accordion title="プラグイン状態: disabled vs missing vs invalid">
  - **Disabled**: プラグインは存在するが、有効化ルールによってオフになっている。configは保持される。
  - **Missing**: configがプラグインidを参照しているが、検出で見つからなかった。
  - **Invalid**: プラグインは存在するが、そのconfigが宣言されたスキーマと一致しない。
</Accordion>

## 検出と優先順位

OpenClawは次の順序でプラグインをスキャンします（最初に一致したものが優先）。

<Steps>
  <Step title="Configパス">
    `plugins.load.paths` — 明示的なファイルまたはディレクトリパス。
  </Step>

  <Step title="Workspace拡張">
    `\<workspace\>/.openclaw/<plugin-root>/*.ts` および `\<workspace\>/.openclaw/<plugin-root>/*/index.ts`。
  </Step>

  <Step title="グローバル拡張">
    `~/.openclaw/<plugin-root>/*.ts` および `~/.openclaw/<plugin-root>/*/index.ts`。
  </Step>

  <Step title="バンドル済みプラグイン">
    OpenClawに同梱。多くはデフォルトで有効です（モデルprovider、speech など）。
    その他は明示的な有効化が必要です。
  </Step>
</Steps>

### 有効化ルール

- `plugins.enabled: false` はすべてのプラグインを無効にします
- `plugins.deny` は常にallowより優先します
- `plugins.entries.\<id\>.enabled: false` はそのプラグインを無効にします
- Workspace由来のプラグインは **デフォルトで無効** です（明示的に有効化する必要があります）
- バンドル済みプラグインは、上書きされない限り組み込みのデフォルトオン集合に従います
- 排他的スロットは、そのスロット用に選択されたプラグインを強制有効化できます

## プラグインスロット（排他的カテゴリ）

一部のカテゴリは排他的です（一度に1つだけ有効）。

```json5
{
  plugins: {
    slots: {
      memory: "memory-core", // または "none" で無効化
      contextEngine: "legacy", // またはプラグインid
    },
  },
}
```

| Slot            | 制御対象 | Default             |
| --------------- | -------- | ------------------- |
| `memory`        | 有効なmemoryプラグイン | `memory-core`       |
| `contextEngine` | 有効なcontext engine | `legacy`（組み込み） |

## CLIリファレンス

```bash
openclaw plugins list                       # コンパクトなインベントリ
openclaw plugins list --enabled            # 読み込まれたプラグインのみ
openclaw plugins list --verbose            # プラグインごとの詳細行
openclaw plugins list --json               # 機械可読インベントリ
openclaw plugins inspect <id>              # 詳細表示
openclaw plugins inspect <id> --json       # 機械可読
openclaw plugins inspect --all             # 全体テーブル
openclaw plugins info <id>                 # inspect のエイリアス
openclaw plugins doctor                    # 診断

openclaw plugins install <package>         # インストール（まずClawHub、その後npm）
openclaw plugins install clawhub:<pkg>     # ClawHubのみからインストール
openclaw plugins install <spec> --force    # 既存インストールを上書き
openclaw plugins install <path>            # ローカルパスからインストール
openclaw plugins install -l <path>         # 開発用にリンク（コピーしない）
openclaw plugins install <plugin> --marketplace <source>
openclaw plugins install <plugin> --marketplace https://github.com/<owner>/<repo>
openclaw plugins install <spec> --pin      # 解決済みの正確なnpm specを記録
openclaw plugins install <spec> --dangerously-force-unsafe-install
openclaw plugins update <id>             # 1つのプラグインを更新
openclaw plugins update <id> --dangerously-force-unsafe-install
openclaw plugins update --all            # すべて更新
openclaw plugins uninstall <id>          # config/インストール記録を削除
openclaw plugins uninstall <id> --keep-files
openclaw plugins marketplace list <source>
openclaw plugins marketplace list <source> --json

openclaw plugins enable <id>
openclaw plugins disable <id>
```

バンドル済みプラグインはOpenClawに同梱されています。多くはデフォルトで有効です（たとえば
バンドル済みモデルprovider、バンドル済みspeech provider、バンドル済みbrowser
プラグイン）。その他のバンドル済みプラグインは、依然として `openclaw plugins enable <id>` が必要です。

`--force` は、既存のインストール済みプラグインまたはフックパックをその場で上書きします。
これは `--link` とは併用できません。`--link` は、管理されたインストール先に
コピーする代わりにソースパスを再利用するためです。

`--pin` はnpm専用です。`--marketplace` とは併用できません。これは、
marketplaceインストールがnpm specではなくmarketplaceソースメタデータを保持するためです。

`--dangerously-force-unsafe-install` は、組み込みの危険コードスキャナーによる誤検知への
緊急用上書きです。これにより、組み込みの `critical` 検出結果が出てもプラグインのインストール
および更新を継続できますが、プラグインの `before_install` ポリシーブロックや
スキャン失敗によるブロックは依然として回避できません。

このCLIフラグは、プラグインのインストール/更新フローにのみ適用されます。GatewayベースのSkill
依存関係インストールでは、代わりに対応する `dangerouslyForceUnsafeInstall` リクエスト
上書きを使います。一方、`openclaw skills install` は別個のClawHub
skill ダウンロード/インストールフローのままです。

互換バンドルは、同じプラグインの list/inspect/enable/disable フローに参加します。現在のランタイムサポートには、bundle Skills、Claude command-skills、
Claude `settings.json` デフォルト、Claude `.lsp.json` とmanifest宣言の
`lspServers` デフォルト、Cursor command-skills、互換性のあるCodex hook
ディレクトリが含まれます。

`openclaw plugins inspect <id>` は、bundleベースのプラグインについて、検出されたbundle機能に加えて、サポートされる/されないMCPおよびLSP server エントリも報告します。

Marketplaceソースには、`~/.claude/plugins/known_marketplaces.json`
にあるClaudeの既知marketplace名、ローカルmarketplaceルートまたは
`marketplace.json` パス、`owner/repo` のようなGitHub短縮形、GitHub repo
URL、またはgit URLを指定できます。リモートmarketplaceについては、プラグインエントリは
クローンされたmarketplace repo 内に留まり、相対パスソースのみを使用する必要があります。

完全な詳細は [`openclaw plugins` CLI reference](/cli/plugins) を参照してください。

## プラグインAPI概要

Nativeプラグインは `register(api)` を公開するエントリオブジェクトをexportします。古い
プラグインでは、レガシーなエイリアスとしてまだ `activate(api)` を使っている場合がありますが、新しいプラグインでは
`register` を使うべきです。

```typescript
export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
    api.registerChannel({
      /* ... */
    });
  },
});
```

OpenClawはエントリオブジェクトを読み込み、プラグイン有効化時に `register(api)` を呼び出します。ローダーは古いプラグイン向けに引き続き `activate(api)` へフォールバックしますが、バンドル済みプラグインと新しい外部プラグインは、`register` を公開契約として扱うべきです。

一般的な登録メソッド:

| Method                                  | 登録するもの |
| --------------------------------------- | ------------ |
| `registerProvider`                      | モデルprovider（LLM） |
| `registerChannel`                       | チャットチャンネル |
| `registerTool`                          | エージェントtool |
| `registerHook` / `on(...)`              | ライフサイクルフック |
| `registerSpeechProvider`                | Text-to-speech / STT |
| `registerRealtimeTranscriptionProvider` | ストリーミングSTT |
| `registerRealtimeVoiceProvider`         | 双方向realtime voice |
| `registerMediaUnderstandingProvider`    | 画像/音声解析 |
| `registerImageGenerationProvider`       | 画像生成 |
| `registerMusicGenerationProvider`       | 音楽生成 |
| `registerVideoGenerationProvider`       | 動画生成 |
| `registerWebFetchProvider`              | Web fetch / scrape provider |
| `registerWebSearchProvider`             | Web search |
| `registerHttpRoute`                     | HTTPエンドポイント |
| `registerCommand` / `registerCli`       | CLIコマンド |
| `registerContextEngine`                 | Context engine |
| `registerService`                       | バックグラウンドサービス |

型付きライフサイクルフックのガード動作:

- `before_tool_call`: `{ block: true }` は終端です。より低優先度のハンドラーはスキップされます。
- `before_tool_call`: `{ block: false }` はno-opで、先行するblockを解除しません。
- `before_install`: `{ block: true }` は終端です。より低優先度のハンドラーはスキップされます。
- `before_install`: `{ block: false }` はno-opで、先行するblockを解除しません。
- `message_sending`: `{ cancel: true }` は終端です。より低優先度のハンドラーはスキップされます。
- `message_sending`: `{ cancel: false }` はno-opで、先行するcancelを解除しません。

完全な型付きフック動作については、[SDK Overview](/ja-JP/plugins/sdk-overview#hook-decision-semantics) を参照してください。

## 関連

- [Building Plugins](/ja-JP/plugins/building-plugins) — 独自プラグインを作成する
- [Plugin Bundles](/ja-JP/plugins/bundles) — Codex/Claude/Cursorバンドル互換性
- [Plugin Manifest](/ja-JP/plugins/manifest) — manifestスキーマ
- [Registering Tools](/ja-JP/plugins/building-plugins#registering-agent-tools) — プラグインでエージェントtoolsを追加する
- [Plugin Internals](/ja-JP/plugins/architecture) — capabilityモデルと読み込みパイプライン
- [Community Plugins](/ja-JP/plugins/community) — サードパーティ一覧
