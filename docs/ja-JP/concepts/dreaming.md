---
read_when:
    - メモリ昇格を自動的に実行したい
    - 各 Dreaming フェーズの役割を理解したい
    - MEMORY.md を汚さずに統合を調整したい
summary: ライト、ディープ、REM フェーズと Dream Diary によるバックグラウンドメモリ統合
title: Dreaming（実験的）
x-i18n:
    generated_at: "2026-04-06T03:06:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: f27da718176bebf59fe8a80fddd4fb5b6d814ac5647f6c1e8344bcfb328db9de
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming（実験的）

Dreaming は `memory-core` のバックグラウンドメモリ統合システムです。
これにより OpenClaw は、強い短期シグナルを耐久性のあるメモリへ移しつつ、
そのプロセスを説明可能かつレビュー可能な状態に保てます。

Dreaming は **オプトイン** で、デフォルトでは無効です。

## Dreaming が書き込むもの

Dreaming は 2 種類の出力を保持します。

- `memory/.dreams/` 内の **マシン状態**（リコールストア、フェーズシグナル、取り込みチェックポイント、ロック）。
- `DREAMS.md`（または既存の `dreams.md`）内の **人が読める出力** と、`memory/dreaming/<phase>/YYYY-MM-DD.md` 配下の任意のフェーズレポートファイル。

長期昇格は引き続き `MEMORY.md` にのみ書き込まれます。

## フェーズモデル

Dreaming は協調して動作する 3 つのフェーズを使用します。

| フェーズ | 目的 | 永続的な書き込み |
| ----- | ----------------------------------------- | ----------------- |
| Light | 最近の短期マテリアルを整理してステージングする | いいえ |
| Deep  | 耐久性のある候補をスコアリングして昇格する | はい（`MEMORY.md`） |
| REM   | テーマと繰り返し現れるアイデアを振り返る | いいえ |

これらのフェーズは内部実装の詳細であり、ユーザーが個別に設定する
「モード」ではありません。

### Light フェーズ

Light フェーズは、最近のデイリーメモリシグナルとリコールトレースを取り込み、
重複排除し、候補行をステージングします。

- 短期リコール状態と最近のデイリーメモリファイルから読み取ります。
- ストレージにインライン出力が含まれる場合、管理された `## Light Sleep` ブロックを書き込みます。
- 後続の Deep ランキング用に強化シグナルを記録します。
- `MEMORY.md` には決して書き込みません。

### Deep フェーズ

Deep フェーズは、何を長期メモリにするかを決定します。

- 重み付きスコアリングとしきい値ゲートを使って候補をランク付けします。
- `minScore`、`minRecallCount`、`minUniqueQueries` を満たす必要があります。
- 書き込み前にライブのデイリーファイルからスニペットを再取得するため、古くなったスニペットや削除されたスニペットはスキップされます。
- 昇格されたエントリを `MEMORY.md` に追記します。
- `DREAMS.md` に `## Deep Sleep` の要約を書き込み、必要に応じて `memory/dreaming/deep/YYYY-MM-DD.md` にも書き込みます。

### REM フェーズ

REM フェーズは、パターンと内省的シグナルを抽出します。

- 最近の短期トレースからテーマと内省の要約を構築します。
- ストレージにインライン出力が含まれる場合、管理された `## REM Sleep` ブロックを書き込みます。
- Deep ランキングで使用される REM 強化シグナルを記録します。
- `MEMORY.md` には決して書き込みません。

## Dream Diary

Dreaming は `DREAMS.md` に物語風の **Dream Diary** も保持します。
各フェーズに十分なマテリアルが集まると、`memory-core` はベストエフォートのバックグラウンド
サブエージェントターン（デフォルトのランタイムモデルを使用）を実行し、短い日記エントリを追記します。

この日記は Dreams UI で人が読むためのものであり、昇格元ではありません。

## Deep ランキングシグナル

Deep ランキングは、6 つの重み付き基本シグナルとフェーズ強化を使用します。

| シグナル | 重み | 説明 |
| ------------------- | ------ | ------------------------------------------------- |
| 頻度 | 0.24   | そのエントリが蓄積した短期シグナルの数 |
| 関連性 | 0.30   | そのエントリの平均取得品質 |
| クエリ多様性 | 0.15   | そのエントリが現れた個別のクエリ/日コンテキスト |
| 新しさ | 0.15   | 時間減衰する鮮度スコア |
| 統合 | 0.10   | 複数日にわたる再出現の強さ |
| 概念的豊かさ | 0.06   | スニペット/パス由来の概念タグ密度 |

Light と REM フェーズでのヒットは、
`memory/.dreams/phase-signals.json` から時間減衰する小さなブーストを追加します。

## スケジューリング

有効にすると、`memory-core` は完全な Dreaming
スイープ用の cron ジョブを 1 つ自動管理します。各スイープでは、フェーズが light -> REM -> deep の順で実行されます。

デフォルトの実行間隔の動作:

| 設定 | デフォルト |
| -------------------- | ----------- |
| `dreaming.frequency` | `0 3 * * *` |

## クイックスタート

Dreaming を有効にする:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true
          }
        }
      }
    }
  }
}
```

カスタムスイープ間隔で Dreaming を有効にする:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true,
            "timezone": "America/Los_Angeles",
            "frequency": "0 */6 * * *"
          }
        }
      }
    }
  }
}
```

## スラッシュコマンド

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## CLI ワークフロー

プレビューまたは手動適用には CLI 昇格を使用します。

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

手動の `memory promote` は、CLI フラグで上書きしない限り、デフォルトで Deep フェーズのしきい値を使用します。

## 主なデフォルト値

すべての設定は `plugins.entries.memory-core.config.dreaming` 配下にあります。

| キー | デフォルト |
| ----------- | ----------- |
| `enabled`   | `false`     |
| `frequency` | `0 3 * * *` |

フェーズポリシー、しきい値、ストレージ動作は内部実装の詳細
であり、ユーザー向け設定ではありません。

完全なキー一覧については、
[メモリ設定リファレンス](/ja-JP/reference/memory-config#dreaming-experimental)
を参照してください。

## Dreams UI

有効にすると、Gateway の **Dreams** タブには次が表示されます。

- 現在の Dreaming 有効状態
- フェーズレベルの状態と管理対象スイープの有無
- 短期、長期、および今日昇格された件数
- 次回のスケジュール実行時刻
- `doctor.memory.dreamDiary` をバックエンドに持つ、展開可能な Dream Diary リーダー

## 関連

- [メモリ](/ja-JP/concepts/memory)
- [メモリ検索](/ja-JP/concepts/memory-search)
- [memory CLI](/cli/memory)
- [メモリ設定リファレンス](/ja-JP/reference/memory-config)
