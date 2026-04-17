---
read_when:
    - メモリ昇格を自動的に実行したい
    - 各Dreamingフェーズが何をするのか理解したい
    - '`MEMORY.md`を汚さずに統合を調整したい'
summary: Dream Diaryを備えた、light、deep、REMフェーズによるバックグラウンドのメモリ統合
title: Dreaming
x-i18n:
    generated_at: "2026-04-15T14:40:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5bcaec80f62e7611ed533094ef1917bd72c885f57252824db910e1f0496adc6
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming

Dreamingは、`memory-core`におけるバックグラウンドのメモリ統合システムです。  
これは、プロセスを説明可能かつレビュー可能に保ちながら、OpenClawが強い短期シグナルを永続的なメモリへ移すのを支援します。

Dreamingは**オプトイン**で、デフォルトでは無効です。

## Dreamingが書き込むもの

Dreamingは2種類の出力を保持します。

- `memory/.dreams/`内の**マシン状態**（リコールストア、フェーズシグナル、取り込みチェックポイント、ロック）
- `DREAMS.md`（または既存の`dreams.md`）内の**人間が読める出力**と、`memory/dreaming/<phase>/YYYY-MM-DD.md`配下の任意のフェーズレポートファイル

長期昇格は引き続き`MEMORY.md`にのみ書き込みます。

## フェーズモデル

Dreamingは3つの協調フェーズを使用します。

| Phase | Purpose | Durable write |
| ----- | ------- | ------------- |
| Light | 最近の短期マテリアルを整理して段階化する | いいえ |
| Deep  | 永続化候補をスコア化して昇格する | はい (`MEMORY.md`) |
| REM   | テーマと繰り返し現れるアイデアを振り返る | いいえ |

これらのフェーズは内部実装の詳細であり、ユーザーが個別に設定する「モード」ではありません。

### Lightフェーズ

Lightフェーズは、最近の日次メモリシグナルとリコールトレースを取り込み、重複排除し、候補行を段階化します。

- 短期リコール状態、最近の日次メモリファイル、利用可能な場合は匿名化されたセッショントランスクリプトから読み取ります。
- ストレージにインライン出力が含まれる場合、管理された`## Light Sleep`ブロックを書き込みます。
- 後のDeepランク付けのために強化シグナルを記録します。
- `MEMORY.md`には決して書き込みません。

### Deepフェーズ

Deepフェーズは、何が長期メモリになるかを決定します。

- 重み付きスコアリングとしきい値ゲートを使って候補をランク付けします。
- 通過には`minScore`、`minRecallCount`、`minUniqueQueries`が必要です。
- 書き込み前にライブの日次ファイルからスニペットを再取得するため、古いスニペットや削除済みスニペットはスキップされます。
- 昇格したエントリを`MEMORY.md`に追記します。
- `DREAMS.md`に`## Deep Sleep`サマリーを書き込み、必要に応じて`memory/dreaming/deep/YYYY-MM-DD.md`にも書き込みます。

### REMフェーズ

REMフェーズは、パターンと内省的シグナルを抽出します。

- 最近の短期トレースからテーマと振り返りサマリーを構築します。
- ストレージにインライン出力が含まれる場合、管理された`## REM Sleep`ブロックを書き込みます。
- Deepランク付けで使用されるREM強化シグナルを記録します。
- `MEMORY.md`には決して書き込みません。

## セッショントランスクリプトの取り込み

Dreamingは、匿名化されたセッショントランスクリプトをDreamingコーパスに取り込むことができます。トランスクリプトが利用可能な場合、それらは日次メモリシグナルやリコールトレースとともにLightフェーズへ渡されます。個人的かつ機微な内容は、取り込み前に匿名化されます。

## Dream Diary

Dreamingはまた、`DREAMS.md`内に物語形式の**Dream Diary**を保持します。  
各フェーズに十分なマテリアルが集まると、`memory-core`はベストエフォートのバックグラウンドサブエージェントターン（デフォルトのランタイムモデルを使用）を実行し、短い日記エントリを追記します。

この日記はDreams UIで人間が読むためのものであり、昇格元ではありません。  
Dreamingによって生成された日記やレポートのアーティファクトは、短期昇格の対象から除外されます。`MEMORY.md`に昇格できるのは、根拠のあるメモリスニペットだけです。

レビューや復旧作業のために、根拠付きの履歴バックフィル経路もあります。

- `memory rem-harness --path ... --grounded`は、過去の`YYYY-MM-DD.md`ノートから根拠付きの日記出力をプレビューします。
- `memory rem-backfill --path ...`は、可逆的な根拠付き日記エントリを`DREAMS.md`に書き込みます。
- `memory rem-backfill --path ... --stage-short-term`は、根拠付きの永続候補を、通常のDeepフェーズがすでに使用している同じ短期エビデンスストアに段階化します。
- `memory rem-backfill --rollback`および`--rollback-short-term`は、通常の日記エントリやライブ短期リコールには触れずに、それらの段階化されたバックフィルアーティファクトを削除します。

Control UIは同じ日記バックフィル／リセットフローを公開しているため、根拠付き候補が昇格に値するかを判断する前に、Dreamsシーンで結果を確認できます。Sceneには明確に区別された根拠付きレーンも表示されるため、どの段階化済み短期エントリが履歴リプレイ由来か、どの昇格アイテムが根拠主導だったかを確認でき、通常のライブ短期状態には触れずに根拠付き専用の段階化エントリだけを消去できます。

## Deepランク付けシグナル

Deepランク付けでは、6つの重み付き基本シグナルに加えてフェーズ強化を使用します。

| Signal | Weight | Description |
| ------ | ------ | ----------- |
| Frequency | 0.24 | エントリが蓄積した短期シグナルの数 |
| Relevance | 0.30 | エントリの平均取得品質 |
| Query diversity | 0.15 | そのエントリを浮上させた異なるクエリ／日コンテキスト |
| Recency | 0.15 | 時間減衰された鮮度スコア |
| Consolidation | 0.10 | 複数日にわたる再出現の強さ |
| Conceptual richness | 0.06 | スニペット／パス由来のコンセプトタグ密度 |

LightフェーズとREMフェーズでのヒットは、`memory/.dreams/phase-signals.json`から小さな時間減衰付きブーストを加えます。

## スケジューリング

有効にすると、`memory-core`は完全なDreamingスイープ用のCronジョブを1つ自動管理します。各スイープでは、フェーズが順に実行されます: light -> REM -> deep。

デフォルトの実行間隔の動作:

| Setting | Default |
| ------- | ------- |
| `dreaming.frequency` | `0 3 * * *` |

## クイックスタート

Dreamingを有効にする:

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

カスタムスイープ間隔でDreamingを有効にする:

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

## CLIワークフロー

プレビューまたは手動適用には、CLI昇格を使用します。

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

手動の`memory promote`は、CLIフラグで上書きしない限り、デフォルトでDeepフェーズのしきい値を使用します。

特定の候補が昇格する、または昇格しない理由を説明する:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

何も書き込まずにREMの振り返り、候補の事実、Deep昇格出力をプレビューする:

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## 主なデフォルト値

すべての設定は`plugins.entries.memory-core.config.dreaming`の下にあります。

| Key | Default |
| --- | ------- |
| `enabled` | `false` |
| `frequency` | `0 3 * * *` |

フェーズポリシー、しきい値、ストレージ動作は内部実装の詳細であり、ユーザー向け設定ではありません。

完全なキー一覧については、[メモリ設定リファレンス](/ja-JP/reference/memory-config#dreaming)を参照してください。

## Dreams UI

有効にすると、Gatewayの**Dreams**タブには以下が表示されます。

- 現在のDreaming有効状態
- フェーズレベルの状態と管理対象スイープの有無
- 短期、根拠付き、シグナル、および本日昇格済みの件数
- 次回スケジュール実行の時刻
- 段階化された履歴リプレイエントリ用の、明確に区別された根拠付きSceneレーン
- `doctor.memory.dreamDiary`をバックエンドにした、展開可能なDream Diaryリーダー

## 関連

- [メモリ](/ja-JP/concepts/memory)
- [メモリ検索](/ja-JP/concepts/memory-search)
- [memory CLI](/cli/memory)
- [メモリ設定リファレンス](/ja-JP/reference/memory-config)
