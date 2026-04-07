---
read_when:
    - ローカルまたはCIのテスト実行に合成QAトランスポートを組み込んでいる
    - バンドルされたqa-channelの設定サーフェスが必要である
    - エンドツーエンドのQA自動化を反復改善している
summary: 決定論的なOpenClaw QAシナリオ向けの、Slackクラスの合成チャネルプラグイン
title: QAチャネル
x-i18n:
    generated_at: "2026-04-07T04:41:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 65c2c908d3ec27c827087616c4ea278f10686810091058321ff26f68296a1782
    source_path: channels/qa-channel.md
    workflow: 15
---

# QAチャネル

`qa-channel` は、自動化されたOpenClaw QA向けのバンドル済み合成メッセージトランスポートです。

これは本番用チャネルではありません。実際のトランスポートで使われるものと同じチャネルプラグイン境界を検証しつつ、状態を決定論的かつ完全に検査可能なまま保つために存在します。

## 現在できること

- Slackクラスのターゲット文法:
  - `dm:<user>`
  - `channel:<room>`
  - `thread:<room>/<thread>`
- 次のためのHTTPベースの合成バス:
  - 受信メッセージの注入
  - 送信トランスクリプトの記録
  - スレッド作成
  - リアクション
  - 編集
  - 削除
  - 検索および読み取りアクション
- Markdownレポートを書き出す、バンドル済みのホスト側セルフチェッカーランナー

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

これは現在、バンドルされた `qa-lab` 拡張機能を経由してルーティングされます。リポジトリ内のQAバスを起動し、バンドルされた `qa-channel` ランタイムスライスを立ち上げ、決定論的なセルフチェックを実行し、`.artifacts/qa-e2e/` 以下にMarkdownレポートを書き出します。

非公開デバッガUI:

```bash
pnpm qa:lab:up
```

この1つのコマンドでQAサイトをビルドし、DockerベースのGateway + QA Labスタックを起動し、QA LabのURLを表示します。そのサイトからシナリオを選択し、モデルレーンを選び、個別の実行を開始し、結果をライブで確認できます。

リポジトリ完全連携のQAスイート全体:

```bash
pnpm openclaw qa suite
```

これにより、出荷されるControl UIバンドルとは別に、ローカルURLで非公開QAデバッガが起動します。

## スコープ

現在のスコープは意図的に狭くしています:

- バス + プラグイントランスポート
- スレッド付きルーティング文法
- チャネル所有のメッセージアクション
- Markdownレポート
- 実行コントロール付きのDockerベースQAサイト

今後の作業で追加予定のもの:

- プロバイダー/モデルマトリクス実行
- より豊富なシナリオ検出
- 後にOpenClawネイティブのオーケストレーション
