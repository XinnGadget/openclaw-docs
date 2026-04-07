---
read_when:
    - iOSノードをペアリングまたは再接続している
    - ソースからiOSアプリを実行している
    - Gateway検出またはcanvasコマンドをデバッグしている
summary: 'iOSノードアプリ: Gatewayへの接続、ペアリング、canvas、トラブルシューティング'
title: iOSアプリ
x-i18n:
    generated_at: "2026-04-07T04:43:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: f3e0a6e33e72d4c9f1f17ef70a1b67bae9ebe4a2dca16677ea6b28d0ddac1b4e
    source_path: platforms/ios.md
    workflow: 15
---

# iOSアプリ（ノード）

提供状況: 内部プレビュー。iOSアプリはまだ一般公開されていません。

## できること

- WebSocket経由でGatewayに接続する（LANまたはtailnet）。
- ノード機能を提供する: Canvas、画面スナップショット、カメラキャプチャ、位置情報、Talk mode、Voice wake。
- `node.invoke` コマンドを受信し、ノード状態イベントを報告する。

## 要件

- 別のデバイス上で動作しているGateway（macOS、Linux、またはWSL2経由のWindows）。
- ネットワーク経路:
  - 同じLAN上でBonjourを使用、**または**
  - ユニキャストDNS-SD経由のtailnet（ドメイン例: `openclaw.internal.`）、**または**
  - 手動のホスト/ポート指定（フォールバック）。

## クイックスタート（ペアリング + 接続）

1. Gatewayを起動します:

```bash
openclaw gateway --port 18789
```

2. iOSアプリでSettingsを開き、検出されたgatewayを選択します（またはManual Hostを有効にしてhost/portを入力します）。

3. Gatewayホスト上でペアリングリクエストを承認します:

```bash
openclaw devices list
openclaw devices approve <requestId>
```

アプリが変更された認証詳細（role/scopes/public key）でペアリングを再試行すると、
以前の保留リクエストは置き換えられ、新しい `requestId` が作成されます。
承認前にもう一度 `openclaw devices list` を実行してください。

4. 接続を確認します:

```bash
openclaw nodes status
openclaw gateway call node.list --params "{}"
```

## 公式ビルド向けのrelayベースpush

公式に配布されるiOSビルドでは、生のAPNs
トークンをgatewayへ公開する代わりに、外部push relayを使用します。

Gateway側の要件:

```json5
{
  gateway: {
    push: {
      apns: {
        relay: {
          baseUrl: "https://relay.example.com",
        },
      },
    },
  },
}
```

フローの仕組み:

- iOSアプリはApp Attestとアプリレシートを使用してrelayに登録します。
- relayは、不透明なrelay handleと、登録スコープのsend grantを返します。
- iOSアプリはペアリング済みgateway identityを取得し、それをrelay登録に含めることで、そのrelayベース登録をその特定のgatewayに委譲します。
- アプリは、そのrelayベース登録を `push.apns.register` でペアリング済みGatewayへ転送します。
- Gatewayは、`push.test`、バックグラウンドwake、wake nudgeに対して、その保存されたrelay handleを使用します。
- Gateway relay base URLは、公式/TestFlight iOSビルドに組み込まれたrelay URLと一致している必要があります。
- 後でアプリが別のGatewayや、異なるrelay base URLを持つビルドに接続した場合、古い紐付けを再利用するのではなく、relay登録を更新します。

この経路でgatewayに**不要**なもの:

- デプロイ全体で共通のrelayトークンは不要。
- 公式/TestFlightのrelayベース送信に直接のAPNsキーは不要。

想定されるオペレーターフロー:

1. 公式/TestFlight iOSビルドをインストールします。
2. gatewayで `gateway.push.apns.relay.baseUrl` を設定します。
3. アプリをgatewayにペアリングし、接続完了まで待ちます。
4. APNsトークンがあり、operatorセッションが接続済みで、relay登録が成功した後、アプリは自動的に `push.apns.register` を公開します。
5. その後、`push.test`、再接続wake、wake nudgeで、保存されたrelayベース登録を使用できます。

互換性に関する注記:

- `OPENCLAW_APNS_RELAY_BASE_URL` は、gatewayの一時的なenvオーバーライドとして引き続き使用できます。

## 認証と信頼のフロー

relayが存在するのは、公式iOSビルドに対して直接APNs-on-gatewayでは提供できない2つの制約を
強制するためです:

- Apple経由で配布された真正なOpenClaw iOSビルドだけがホスト型relayを使用できる。
- Gatewayは、その特定の
  gatewayとペアリングしたiOSデバイスに対してのみrelayベースpushを送信できる。

ホップごとの流れ:

1. `iOS app -> gateway`
   - アプリはまず通常のGateway認証フローを通じてgatewayとペアリングします。
   - これにより、アプリは認証済みノードセッションと認証済みoperatorセッションを取得します。
   - operatorセッションは `gateway.identity.get` の呼び出しに使用されます。

2. `iOS app -> relay`
   - アプリはHTTPS経由でrelay登録エンドポイントを呼び出します。
   - 登録にはApp Attestの証明とアプリレシートが含まれます。
   - relayはbundle ID、App Attest証明、Appleレシートを検証し、
     公式/本番の配布経路を要求します。
   - これにより、ローカルのXcode/devビルドはホスト型relayを使用できません。ローカルビルドは
     署名されている場合がありますが、relayが要求する公式なApple配布証明を満たしません。

3. `gateway identity delegation`
   - relay登録前に、アプリは
     `gateway.identity.get` からペアリング済みgateway identityを取得します。
   - アプリはそのgateway identityをrelay登録ペイロードに含めます。
   - relayは、そのgateway identityに委譲されたrelay handleと登録スコープのsend grantを返します。

4. `gateway -> relay`
   - Gatewayは、`push.apns.register` からrelay handleとsend grantを保存します。
   - `push.test`、再接続wake、wake nudgeでは、Gatewayは
     自身のdevice identityで送信リクエストに署名します。
   - relayは、保存済みsend grantとGateway署名の両方を、登録時に委譲された
     gateway identityに対して検証します。
   - たとえ別のGatewayがそのhandleを何らかの形で取得したとしても、その保存済み登録を再利用することはできません。

5. `relay -> APNs`
   - relayは、本番APNs認証情報と、公式ビルド用の生のAPNsトークンを保持します。
   - Gatewayは、relayベースの公式ビルドに対して生のAPNsトークンを保存しません。
   - relayは、ペアリング済みGatewayを代理して最終的なpushをAPNsへ送信します。

この設計が作られた理由:

- 本番APNs認証情報をユーザーのgatewayから切り離すため。
- 公式ビルドの生のAPNsトークンをgatewayに保存しないようにするため。
- 公式/TestFlightのOpenClawビルドに対してのみホスト型relay利用を許可するため。
- あるgatewayが、別のgatewayに属するiOSデバイスへwake pushを送れないようにするため。

ローカル/手動ビルドは直接APNsのままです。relayを使わずにそれらの
ビルドをテストする場合、gatewayには引き続き直接APNs認証情報が必要です:

```bash
export OPENCLAW_APNS_TEAM_ID="TEAMID"
export OPENCLAW_APNS_KEY_ID="KEYID"
export OPENCLAW_APNS_PRIVATE_KEY_P8="$(cat /path/to/AuthKey_KEYID.p8)"
```

これらはgateway-hostのランタイムenv varsであり、Fastlane設定ではありません。`apps/ios/fastlane/.env` には
`ASC_KEY_ID` や `ASC_ISSUER_ID` のようなApp Store Connect / TestFlight認証のみが保存され、
ローカルiOSビルド向けの直接APNs配信は設定しません。

推奨されるgateway-hostでの保存方法:

```bash
mkdir -p ~/.openclaw/credentials/apns
chmod 700 ~/.openclaw/credentials/apns
mv /path/to/AuthKey_KEYID.p8 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
chmod 600 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
export OPENCLAW_APNS_PRIVATE_KEY_PATH="$HOME/.openclaw/credentials/apns/AuthKey_KEYID.p8"
```

`.p8` ファイルをコミットしたり、リポジトリのチェックアウト配下に置いたりしないでください。

## 検出経路

### Bonjour（LAN）

iOSアプリは `local.` 上の `_openclaw-gw._tcp` をブラウズし、設定されている場合は同じ
広域DNS-SD検出ドメインもブラウズします。同じLAN上のGatewayは `local.` から自動的に表示されます。
ネットワークをまたぐ検出では、ビーコン種別を変更せずに、設定済みの広域ドメインを使用できます。

### tailnet（ネットワークをまたぐ場合）

mDNSがブロックされている場合は、ユニキャストDNS-SDゾーン（ドメインを選択。例:
`openclaw.internal.`）とTailscale split DNSを使用します。
CoreDNSの例については [Bonjour](/ja-JP/gateway/bonjour) を参照してください。

### 手動host/port

Settingsで **Manual Host** を有効にし、gatewayのhost + port（デフォルト `18789`）を入力します。

## Canvas + A2UI

iOSノードはWKWebView canvasをレンダリングします。これを操作するには `node.invoke` を使います:

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.navigate --params '{"url":"http://<gateway-host>:18789/__openclaw__/canvas/"}'
```

注記:

- Gateway canvas hostは `/__openclaw__/canvas/` と `/__openclaw__/a2ui/` を提供します。
- これはGateway HTTPサーバーから配信されます（`gateway.port` と同じポート。デフォルト `18789`）。
- iOSノードは、canvas host URLが通知されると接続時に自動でA2UIへ移動します。
- `canvas.navigate` と `{"url":""}` で組み込みscaffoldに戻れます。

### Canvas eval / snapshot

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.eval --params '{"javaScript":"(() => { const {ctx} = window.__openclaw; ctx.clearRect(0,0,innerWidth,innerHeight); ctx.lineWidth=6; ctx.strokeStyle=\"#ff2d55\"; ctx.beginPath(); ctx.moveTo(40,40); ctx.lineTo(innerWidth-40, innerHeight-40); ctx.stroke(); return \"ok\"; })()"}'
```

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.snapshot --params '{"maxWidth":900,"format":"jpeg"}'
```

## Voice wake + Talk mode

- Voice wakeとTalk modeはSettingsで利用できます。
- iOSではバックグラウンド音声が中断される場合があるため、アプリがアクティブでないときの音声機能はベストエフォートとして扱ってください。

## よくあるエラー

- `NODE_BACKGROUND_UNAVAILABLE`: iOSアプリをフォアグラウンドにしてください（canvas/camera/screenコマンドには必要です）。
- `A2UI_HOST_NOT_CONFIGURED`: Gatewayがcanvas host URLを通知していません。 [Gateway configuration](/ja-JP/gateway/configuration) の `canvasHost` を確認してください。
- ペアリングプロンプトが表示されない: `openclaw devices list` を実行して手動で承認してください。
- 再インストール後に再接続できない: Keychainのペアリングトークンが消去されています。ノードを再ペアリングしてください。

## 関連ドキュメント

- [Pairing](/ja-JP/channels/pairing)
- [Discovery](/ja-JP/gateway/discovery)
- [Bonjour](/ja-JP/gateway/bonjour)
