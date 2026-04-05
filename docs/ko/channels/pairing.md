---
read_when:
    - DM 접근 제어를 설정할 때
    - 새 iOS/Android 노드를 페어링할 때
    - OpenClaw 보안 상태를 검토할 때
summary: '페어링 개요: 누가 나에게 DM을 보낼 수 있는지와 어떤 노드가 참여할 수 있는지 승인'
title: 페어링
x-i18n:
    generated_at: "2026-04-05T12:35:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2bd99240b3530def23c05a26915d07cf8b730565c2822c6338437f8fb3f285c9
    source_path: channels/pairing.md
    workflow: 15
---

# 페어링

“페어링”은 OpenClaw의 명시적인 **소유자 승인** 단계입니다.
이는 두 곳에서 사용됩니다.

1. **DM 페어링**(누가 봇과 대화할 수 있는지)
2. **노드 페어링**(어떤 장치/노드가 게이트웨이 네트워크에 참여할 수 있는지)

보안 맥락: [Security](/gateway/security)

## 1) DM 페어링(인바운드 채팅 접근)

채널이 DM 정책 `pairing`으로 구성되면, 알 수 없는 발신자는 짧은 코드를 받게 되며 승인이 이루어질 때까지 해당 메시지는 **처리되지 않습니다**.

기본 DM 정책은 다음 문서에 설명되어 있습니다: [Security](/gateway/security)

페어링 코드:

- 8자, 대문자, 혼동하기 쉬운 문자 없음(`0O1I`).
- **1시간 후 만료**됩니다. 봇은 새 요청이 생성될 때만 페어링 메시지를 보냅니다(발신자당 대략 1시간에 한 번).
- 대기 중인 DM 페어링 요청은 기본적으로 **채널당 3개**로 제한되며, 하나가 만료되거나 승인될 때까지 추가 요청은 무시됩니다.

### 발신자 승인

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

지원 채널: `bluebubbles`, `discord`, `feishu`, `googlechat`, `imessage`, `irc`, `line`, `matrix`, `mattermost`, `msteams`, `nextcloud-talk`, `nostr`, `openclaw-weixin`, `signal`, `slack`, `synology-chat`, `telegram`, `twitch`, `whatsapp`, `zalo`, `zalouser`.

### 상태가 저장되는 위치

`~/.openclaw/credentials/` 아래에 저장됩니다.

- 대기 중 요청: `<channel>-pairing.json`
- 승인된 allowlist 저장소:
  - 기본 계정: `<channel>-allowFrom.json`
  - 비기본 계정: `<channel>-<accountId>-allowFrom.json`

계정 범위 지정 동작:

- 비기본 계정은 자신의 범위가 지정된 allowlist 파일만 읽고 씁니다.
- 기본 계정은 채널 범위의 범위 미지정 allowlist 파일을 사용합니다.

이 파일들은 민감한 정보로 취급하세요(assistant에 대한 접근을 제어합니다).

중요: 이 저장소는 DM 접근용입니다. 그룹 권한 부여는 별개입니다.
DM 페어링 코드를 승인한다고 해서 해당 발신자가 자동으로 그룹 명령을 실행하거나 그룹에서 봇을 제어할 수 있게 되는 것은 아닙니다. 그룹 접근의 경우 채널의 명시적인 그룹 allowlist를 구성해야 합니다(예: `groupAllowFrom`, `groups`, 또는 채널에 따라 그룹별/토픽별 재정의).

## 2) 노드 장치 페어링(iOS/Android/macOS/헤드리스 노드)

노드는 `role: node`를 가진 **장치**로 게이트웨이에 연결됩니다. 게이트웨이는 승인되어야 하는 장치 페어링 요청을 생성합니다.

### Telegram으로 페어링(iOS 권장)

`device-pair` plugin을 사용하면 최초 장치 페어링을 전부 Telegram에서 진행할 수 있습니다.

1. Telegram에서 봇에게 메시지를 보냅니다: `/pair`
2. 봇이 두 개의 메시지로 응답합니다. 하나는 안내 메시지이고, 다른 하나는 Telegram에서 쉽게 복사/붙여넣기할 수 있는 별도의 **설정 코드** 메시지입니다.
3. 휴대폰에서 OpenClaw iOS 앱 → Settings → Gateway를 엽니다.
4. 설정 코드를 붙여넣고 연결합니다.
5. Telegram으로 돌아가 `/pair pending`을 실행한 뒤(요청 ID, 역할, 범위를 검토), 승인합니다.

설정 코드는 다음을 포함하는 base64 인코딩 JSON 페이로드입니다.

- `url`: 게이트웨이 WebSocket URL(`ws://...` 또는 `wss://...`)
- `bootstrapToken`: 초기 페어링 핸드셰이크에 사용되는, 단일 장치용 단기 bootstrap 토큰

그 bootstrap 토큰은 내장된 페어링 bootstrap 프로필을 포함합니다.

- 기본적으로 넘겨지는 `node` 토큰은 `scopes: []`로 유지됩니다
- 넘겨지는 `operator` 토큰은 bootstrap allowlist로 계속 제한됩니다:
  `operator.approvals`, `operator.read`, `operator.talk.secrets`, `operator.write`
- bootstrap 범위 검사는 하나의 평면 범위 풀이 아니라 역할 접두사 기반입니다.
  operator 범위 항목은 operator 요청만 충족하며, 비-operator 역할도 여전히 자신의 역할 접두사 아래에서 범위를 요청해야 합니다

설정 코드가 유효한 동안에는 비밀번호처럼 취급하세요.

### 노드 장치 승인

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
```

동일한 장치가 다른 인증 세부 정보(예: 다른 역할/범위/공개 키)로 다시 시도하면, 이전 대기 요청은 대체되고 새 `requestId`가 생성됩니다.

### 노드 페어링 상태 저장소

`~/.openclaw/devices/` 아래에 저장됩니다.

- `pending.json`(단기 보관; 대기 요청은 만료됨)
- `paired.json`(페어링된 장치 + 토큰)

### 참고

- 레거시 `node.pair.*` API(CLI: `openclaw nodes pending|approve|reject|rename`)는
  게이트웨이가 소유하는 별도의 페어링 저장소입니다. WS 노드는 여전히 장치 페어링이 필요합니다.
- 페어링 기록은 승인된 역할에 대한 내구성 있는 source of truth입니다. 활성
  장치 토큰은 해당 승인된 역할 집합으로 계속 제한되며, 승인된 역할 밖에 있는
  우발적인 토큰 항목이 새 접근 권한을 만들지는 않습니다.

## 관련 문서

- 보안 모델 + 프롬프트 인젝션: [Security](/gateway/security)
- 안전한 업데이트(doctor 실행): [Updating](/install/updating)
- 채널 구성:
  - Telegram: [Telegram](/channels/telegram)
  - WhatsApp: [WhatsApp](/channels/whatsapp)
  - Signal: [Signal](/channels/signal)
  - BlueBubbles(iMessage): [BlueBubbles](/channels/bluebubbles)
  - iMessage(레거시): [iMessage](/channels/imessage)
  - Discord: [Discord](/channels/discord)
  - Slack: [Slack](/channels/slack)
