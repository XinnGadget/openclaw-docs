---
read_when:
    - iOS node를 페어링하거나 다시 연결하는 경우
    - 소스에서 iOS 앱을 실행하는 경우
    - gateway discovery 또는 canvas 명령을 디버깅하는 경우
summary: 'iOS node 앱: Gateway 연결, 페어링, canvas 및 문제 해결'
title: iOS 앱
x-i18n:
    generated_at: "2026-04-05T12:48:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1e9d9cec58afd4003dff81d3e367bfbc6a634c1b229e433e08fd78fbb5f2e5a9
    source_path: platforms/ios.md
    workflow: 15
---

# iOS 앱(Node)

제공 상태: 내부 프리뷰. iOS 앱은 아직 공개 배포되지 않았습니다.

## 기능

- WebSocket(LAN 또는 tailnet)을 통해 Gateway에 연결합니다.
- node 기능을 노출합니다: Canvas, Screen snapshot, Camera capture, Location, Talk mode, Voice wake.
- `node.invoke` 명령을 수신하고 node 상태 이벤트를 보고합니다.

## 요구 사항

- 다른 장치(macOS, Linux 또는 WSL2를 통한 Windows)에서 실행 중인 Gateway.
- 네트워크 경로:
  - Bonjour를 통한 동일 LAN, **또는**
  - 유니캐스트 DNS-SD를 통한 tailnet(예시 도메인: `openclaw.internal.`), **또는**
  - 수동 호스트/포트(대체 수단).

## 빠른 시작(페어링 + 연결)

1. Gateway를 시작합니다:

```bash
openclaw gateway --port 18789
```

2. iOS 앱에서 Settings를 열고 발견된 gateway를 선택합니다(또는 Manual Host를 활성화하고 host/port를 입력합니다).

3. gateway 호스트에서 페어링 요청을 승인합니다:

```bash
openclaw devices list
openclaw devices approve <requestId>
```

앱이 변경된 인증 세부 정보(role/scopes/public key)로 페어링을 재시도하면,
이전 대기 요청은 대체되고 새 `requestId`가 생성됩니다.
승인 전에 `openclaw devices list`를 다시 실행하세요.

4. 연결을 확인합니다:

```bash
openclaw nodes status
openclaw gateway call node.list --params "{}"
```

## 공식 빌드용 relay 기반 push

공식 배포 iOS 빌드는 원시 APNs
토큰을 gateway에 게시하는 대신 외부 push relay를 사용합니다.

Gateway 측 요구 사항:

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

흐름 작동 방식:

- iOS 앱은 App Attest와 앱 영수증을 사용해 relay에 등록합니다.
- relay는 불투명한 relay handle과 등록 범위의 send grant를 반환합니다.
- iOS 앱은 페어링된 gateway identity를 가져와 relay 등록에 포함하므로 relay 기반 등록이 해당 특정 gateway에 위임됩니다.
- 앱은 그 relay 기반 등록을 `push.apns.register`로 페어링된 gateway에 전달합니다.
- gateway는 저장된 relay handle을 `push.test`, 백그라운드 wake, wake nudge에 사용합니다.
- gateway relay base URL은 공식/TestFlight iOS 빌드에 내장된 relay URL과 일치해야 합니다.
- 앱이 나중에 다른 gateway 또는 다른 relay base URL을 가진 빌드에 연결되면 이전 바인딩을 재사용하는 대신 relay 등록을 새로 고칩니다.

이 경로에서 gateway에 **필요하지 않은 것**:

- 배포 전체에 공통인 relay 토큰 불필요.
- 공식/TestFlight relay 기반 전송을 위한 직접 APNs 키 불필요.

예상 운영자 흐름:

1. 공식/TestFlight iOS 빌드를 설치합니다.
2. gateway에서 `gateway.push.apns.relay.baseUrl`을 설정합니다.
3. 앱을 gateway에 페어링하고 연결이 완료되도록 둡니다.
4. 앱은 APNs 토큰이 있고, operator 세션이 연결되어 있으며, relay 등록이 성공하면 자동으로 `push.apns.register`를 게시합니다.
5. 그 후 `push.test`, 재연결 wake, wake nudge는 저장된 relay 기반 등록을 사용할 수 있습니다.

호환성 참고:

- `OPENCLAW_APNS_RELAY_BASE_URL`은 여전히 gateway용 임시 환경 변수 재정의로 동작합니다.

## 인증 및 신뢰 흐름

relay는 직접 APNs-on-gateway로는 제공할 수 없는 두 가지 제약을 강제하기 위해 존재합니다.
공식 iOS 빌드에서:

- Apple을 통해 배포된 진짜 OpenClaw iOS 빌드만 호스팅된 relay를 사용할 수 있습니다.
- gateway는 해당 특정 gateway와 페어링된 iOS 장치에 대해서만 relay 기반 push를 보낼 수 있습니다.

홉별 동작:

1. `iOS app -> gateway`
   - 앱은 먼저 일반 Gateway 인증 흐름을 통해 gateway와 페어링합니다.
   - 그러면 앱은 인증된 node 세션과 인증된 operator 세션을 얻게 됩니다.
   - operator 세션은 `gateway.identity.get` 호출에 사용됩니다.

2. `iOS app -> relay`
   - 앱은 HTTPS를 통해 relay 등록 엔드포인트를 호출합니다.
   - 등록에는 App Attest 증명과 앱 영수증이 포함됩니다.
   - relay는 bundle ID, App Attest 증명, Apple 영수증을 검증하고
     공식/프로덕션 배포 경로를 요구합니다.
   - 이것이 로컬 Xcode/dev 빌드가 호스팅 relay를 사용할 수 없도록 막는 장치입니다. 로컬 빌드는
     서명되어 있을 수는 있지만 relay가 기대하는 공식 Apple 배포 증명을 충족하지는 않습니다.

3. `gateway identity delegation`
   - relay 등록 전에 앱은
     `gateway.identity.get`에서 페어링된 gateway identity를 가져옵니다.
   - 앱은 그 gateway identity를 relay 등록 payload에 포함합니다.
   - relay는 해당 gateway identity에 위임된 relay handle과 등록 범위 send grant를 반환합니다.

4. `gateway -> relay`
   - gateway는 `push.apns.register`에서 relay handle과 send grant를 저장합니다.
   - `push.test`, 재연결 wake, wake nudge 시 gateway는 자체 장치 identity로 전송 요청에 서명합니다.
   - relay는 저장된 send grant와 gateway 서명을 모두 등록 시 위임된 gateway identity에 대해 검증합니다.
   - 다른 gateway는 handle을 somehow 획득하더라도 저장된 등록을 재사용할 수 없습니다.

5. `relay -> APNs`
   - relay는 공식 빌드용 프로덕션 APNs 자격 증명과 원시 APNs 토큰을 소유합니다.
   - gateway는 relay 기반 공식 빌드에 대해 원시 APNs 토큰을 저장하지 않습니다.
   - relay는 페어링된 gateway를 대신해 APNs로 최종 push를 보냅니다.

이 설계가 만들어진 이유:

- 프로덕션 APNs 자격 증명을 사용자 gateway 밖에 두기 위해.
- 공식 빌드의 원시 APNs 토큰을 gateway에 저장하지 않기 위해.
- 공식/TestFlight OpenClaw 빌드에 대해서만 호스팅 relay 사용을 허용하기 위해.
- 한 gateway가 다른 gateway에 속한 iOS 장치로 wake push를 보내지 못하게 하기 위해.

로컬/수동 빌드는 직접 APNs를 계속 사용합니다. relay 없이 그
빌드를 테스트하는 경우 gateway에는 여전히 직접 APNs 자격 증명이 필요합니다:

```bash
export OPENCLAW_APNS_TEAM_ID="TEAMID"
export OPENCLAW_APNS_KEY_ID="KEYID"
export OPENCLAW_APNS_PRIVATE_KEY_P8="$(cat /path/to/AuthKey_KEYID.p8)"
```

## Discovery 경로

### Bonjour (LAN)

iOS 앱은 `local.`의 `_openclaw-gw._tcp`를 탐색하며, 구성된 경우 동일한
광역 DNS-SD discovery 도메인도 탐색합니다. 동일 LAN의 gateway는 `local.`에서 자동으로 나타납니다.
네트워크 간 discovery는 beacon 유형을 변경하지 않고 구성된 광역 도메인을 사용할 수 있습니다.

### Tailnet (네트워크 간)

mDNS가 차단되어 있으면 유니캐스트 DNS-SD 존(도메인을 선택하세요. 예:
`openclaw.internal.`)과 Tailscale split DNS를 사용하세요.
CoreDNS 예시는 [Bonjour](/gateway/bonjour)를 참조하세요.

### 수동 호스트/포트

Settings에서 **Manual Host**를 활성화하고 gateway host + port(기본값 `18789`)를 입력하세요.

## Canvas + A2UI

iOS node는 WKWebView canvas를 렌더링합니다. 이를 구동하려면 `node.invoke`를 사용하세요:

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.navigate --params '{"url":"http://<gateway-host>:18789/__openclaw__/canvas/"}'
```

참고:

- Gateway canvas host는 `/__openclaw__/canvas/` 및 `/__openclaw__/a2ui/`를 제공합니다.
- 이는 Gateway HTTP 서버에서 제공됩니다(`gateway.port`와 동일한 포트, 기본값 `18789`).
- iOS node는 canvas host URL이 광고되면 연결 시 자동으로 A2UI로 이동합니다.
- `canvas.navigate`와 `{"url":""}`로 내장 scaffold로 돌아갈 수 있습니다.

### Canvas eval / snapshot

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.eval --params '{"javaScript":"(() => { const {ctx} = window.__openclaw; ctx.clearRect(0,0,innerWidth,innerHeight); ctx.lineWidth=6; ctx.strokeStyle=\"#ff2d55\"; ctx.beginPath(); ctx.moveTo(40,40); ctx.lineTo(innerWidth-40, innerHeight-40); ctx.stroke(); return \"ok\"; })()"}'
```

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.snapshot --params '{"maxWidth":900,"format":"jpeg"}'
```

## Voice wake + Talk mode

- Voice wake와 Talk mode는 Settings에서 사용할 수 있습니다.
- iOS는 백그라운드 오디오를 중단할 수 있으므로, 앱이 활성 상태가 아닐 때 음성 기능은 최선 시도 수준으로 간주하세요.

## 일반적인 오류

- `NODE_BACKGROUND_UNAVAILABLE`: iOS 앱을 포그라운드로 가져오세요(canvas/camera/screen 명령에는 필요).
- `A2UI_HOST_NOT_CONFIGURED`: Gateway가 canvas host URL을 광고하지 않았습니다. [Gateway configuration](/gateway/configuration)의 `canvasHost`를 확인하세요.
- 페어링 프롬프트가 전혀 나타나지 않음: `openclaw devices list`를 실행하고 수동으로 승인하세요.
- 재설치 후 재연결 실패: Keychain 페어링 토큰이 지워졌습니다. node를 다시 페어링하세요.

## 관련 문서

- [페어링](/channels/pairing)
- [Discovery](/gateway/discovery)
- [Bonjour](/gateway/bonjour)
