---
x-i18n:
    generated_at: "2026-04-06T03:05:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6e1cf417b0c04d001bc494fbe03ac2fcb66866f759e21646dbfd1a9c3a968bff
    source_path: .i18n/README.md
    workflow: 15
---

# OpenClaw ドキュメント i18n アセット

このフォルダーには、ソースドキュメントリポジトリ用の翻訳設定が保存されています。

生成されたロケールページとライブのロケール翻訳メモリは、現在パブリッシュ用リポジトリ（`openclaw/docs`、ローカルの兄弟チェックアウト `~/Projects/openclaw-docs`）にあります。

## ファイル

- `glossary.<lang>.json` — 推奨用語のマッピング（プロンプトガイダンスで使用）。
- `<lang>.tm.jsonl` — ワークフロー + モデル + テキストハッシュをキーとする翻訳メモリ（キャッシュ）。このリポジトリでは、ロケール TM ファイルは必要に応じて生成されます。

## 用語集の形式

`glossary.<lang>.json` はエントリの配列です:

```json
{
  "source": "troubleshooting",
  "target": "故障排除",
  "ignore_case": true,
  "whole_word": false
}
```

フィールド:

- `source`: 優先する英語（またはソース）フレーズ。
- `target`: 推奨される翻訳出力。

## 注記

- 用語集エントリは、モデルに **プロンプトガイダンス** として渡されます（決定論的な書き換えは行いません）。
- `scripts/docs-i18n` は引き続き翻訳生成を担います。
- ソースリポジトリは英語ドキュメントをパブリッシュ用リポジトリに同期し、ロケール生成は push、スケジュール、およびリリースディスパッチごとに、そのリポジトリ側でロケールごとに実行されます。
