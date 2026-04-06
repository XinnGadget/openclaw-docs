---
read_when:
    - 合成QAトランスポートをローカルまたはCIのテスト実行に組み込んでいる
    - バンドルされたqa-channelの設定サーフェスが必要である
    - エンドツーエンドのQA自動化を反復開発している
summary: 決定論的なOpenClaw QAシナリオ向けの、合成Slackクラスチャネルプラグイン
title: QAチャネル
x-i18n:
    generated_at: "2026-04-06T03:05:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3b88cd73df2f61b34ad1eb83c3450f8fe15a51ac69fbb5a9eca0097564d67a06
    source_path: channels/qa-channel.md
    workflow: 15
---

# QAチャネル

`qa-channel`は、自動化されたOpenClaw QA向けのバンドルされた合成メッセージトランスポートです。

これは本番用チャネルではありません。状態を決定論的かつ完全に検査可能に保ちながら、実際のトランスポートで使われるのと同じチャネルプラグイン境界を検証するために存在します。

## 現在できること

- Slackクラスのターゲット文法:
  - `dm:<user>`
  - `channel:<room>`
  - `thread:<room>/<thread>`
- HTTPベースの合成バスによる以下の機能:
  - 受信メッセージの注入
  - 送信トランスクリプトの取得
  - スレッドの作成
  - リアクション
  - 編集
  - 削除
  - 検索および読み取りアクション
- Markdownレポートを書き出す、バンドルされたホスト側セルフチェックランナー

## 設定

```json
{
  "channels": {
    "qa-channel": {
      "baseUrl": "http://127.0.0.1:43123",
      "botUserId": "openclaw",
      "botDisplayName": "OpenClaw QA",
      "allowFrom": ["*"],
      "pollTimeoutMs": 1000
    }
  }
}
```

サポートされているアカウントキー:

- `baseUrl`
- `botUserId`
- `botDisplayName`
- `pollTimeoutMs`
- `allowFrom`
- `defaultTo`
- `actions.messages`
- `actions.reactions`
- `actions.search`
- `actions.threads`

## ランナー

現在の垂直スライス:

```bash
pnpm qa:e2e
```

これは現在、バンドルされた`qa-lab`拡張機能を経由してルーティングされます。リポジトリ内のQAバスを起動し、バンドルされた`qa-channel`ランタイムスライスを立ち上げ、決定論的なセルフチェックを実行し、Markdownレポートを`.artifacts/qa-e2e/`配下に書き出します。

非公開デバッガーUI:

```bash
pnpm qa:lab:build
pnpm openclaw qa ui
```

完全なリポジトリ連携QAスイート:

```bash
pnpm openclaw qa suite
```

これにより、出荷されるControl UIバンドルとは別の、ローカルURL上の非公開QAデバッガーが起動します。

## スコープ

現在のスコープは意図的に限定されています:

- バス + プラグイントランスポート
- スレッド化されたルーティング文法
- チャネル所有のメッセージアクション
- Markdownレポート

今後の作業では、以下が追加される予定です:

- Docker化されたOpenClawオーケストレーション
- プロバイダー/モデルのマトリクス実行
- より豊富なシナリオ検出
- 後にOpenClawネイティブのオーケストレーション
