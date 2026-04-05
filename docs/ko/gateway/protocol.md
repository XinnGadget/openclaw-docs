---
read_when:
    - gateway WS 클라이언트를 구현하거나 업데이트하는 중
    - 프로토콜 불일치 또는 연결 실패를 디버그해야 함
    - 프로토콜 스키마/모델을 다시 생성하는 중
summary: 'Gateway WebSocket 프로토콜: 핸드셰이크, 프레임, 버전 관리'
title: Gateway Protocol
x-i18n:
    generated_at: "2026-04-05T12:44:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: c37f5b686562dda3ba3516ac6982ad87b2f01d8148233284e9917099c6e96d87
    source_path: gateway/protocol.md
    workflow: 15
---

# Gateway 프로토콜 (WebSocket)

Gateway WS 프로토콜은 OpenClaw의 **단일 컨트롤 플레인 + 노드 전송 계층**입니다. 모든 클라이언트(CLI, 웹 UI, macOS 앱, iOS/Android 노드, 헤드리스 노드)는 WebSocket으로 연결하고 핸드셰이크 시점에 자신의 **역할** + **범위**를 선언합니다.

## 전송

- WebSocket, JSON 페이로드를 담은 텍스트 프레임.
- 첫 번째 프레임은 **반드시** `connect` 요청이어야 합니다.

## 핸드셰이크 (connect)

Gateway → Client (연결 전 챌린지):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

Client → Gateway:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Gateway → Client:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
}
```

기기 토큰이 발급되면 `hello-ok`에는 다음도 포함됩니다.

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

신뢰된 bootstrap 핸드오프 중에는 `hello-ok.auth`에 `deviceTokens` 아래 추가적인 제한된 역할 항목이 포함될 수도 있습니다.

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

내장된 node/operator bootstrap 흐름에서는 기본 node 토큰은 계속
`scopes: []`를 유지하며, 전달된 operator 토큰은 bootstrap
operator allowlist(`operator.approvals`, `operator.read`,
`operator.talk.secrets`, `operator.write`) 범위 내로만 제한됩니다. Bootstrap 범위 검사는
역할 접두사 기준을 유지합니다. operator 항목은 operator 요청에만 적용되며, operator가 아닌
역할은 여전히 자신 역할 접두사 아래의 scopes가 필요합니다.

### 노드 예시

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## 프레이밍

- **요청**: `{type:"req", id, method, params}`
- **응답**: `{type:"res", id, ok, payload|error}`
- **이벤트**: `{type:"event", event, payload, seq?, stateVersion?}`

부작용이 있는 메서드는 **멱등성 키**가 필요합니다(스키마 참조).

## 역할 + 범위

### 역할

- `operator` = 컨트롤 플레인 클라이언트(CLI/UI/자동화).
- `node` = 기능 호스트(camera/screen/canvas/system.run).

### 범위 (operator)

일반적인 scopes:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

`talk.config`에서 `includeSecrets: true`를 사용하려면 `operator.talk.secrets`
(또는 `operator.admin`)가 필요합니다.

plugin에 등록된 gateway RPC 메서드는 자체 operator scope를 요청할 수 있지만,
예약된 코어 admin 접두사(`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`)는 항상 `operator.admin`으로 확인됩니다.

메서드 scope는 첫 번째 게이트일 뿐입니다. 일부 slash command는
`chat.send`를 통해 도달하더라도 그 위에 더 엄격한 명령 수준 검사를 적용합니다. 예를 들어 영구적인
`/config set` 및 `/config unset` 쓰기는 `operator.admin`이 필요합니다.

`node.pair.approve`도 기본 메서드 scope 외에 추가 승인 시 scope 검사를 가집니다.

- 명령 없는 요청: `operator.pairing`
- exec가 아닌 노드 명령이 있는 요청: `operator.pairing` + `operator.write`
- `system.run`, `system.run.prepare`, 또는 `system.which`가 포함된 요청:
  `operator.pairing` + `operator.admin`

### Caps/commands/permissions (node)

노드는 연결 시 기능 클레임을 선언합니다.

- `caps`: 상위 수준 기능 범주.
- `commands`: invoke용 명령 allowlist.
- `permissions`: 세부 토글(예: `screen.record`, `camera.capture`).

Gateway는 이를 **클레임**으로 취급하고 서버 측 allowlist를 강제합니다.

## Presence

- `system-presence`는 기기 identity를 키로 하는 항목을 반환합니다.
- Presence 항목에는 `deviceId`, `roles`, `scopes`가 포함되므로 UI는 하나의 기기가 **operator**와 **node**로 모두 연결되어 있어도 단일 행으로 표시할 수 있습니다.

## 일반적인 RPC 메서드 계열

이 페이지는 생성된 전체 덤프는 아니지만, 공개 WS 표면은
위의 핸드셰이크/인증 예시보다 더 넓습니다. 아래는 오늘날 Gateway가 노출하는 주요 메서드 계열입니다.

`hello-ok.features.methods`는
`src/gateway/server-methods-list.ts`와 로드된 plugin/channel 메서드 export를 기반으로 한 보수적인 발견 목록입니다.
이를 기능 발견용으로 취급하고, `src/gateway/server-methods/*.ts`에 구현된 모든 호출 가능 helper의 생성된 덤프로 보지는 마세요.

### 시스템 및 identity

- `health`는 캐시되었거나 새로 프로브된 gateway 상태 스냅샷을 반환합니다.
- `status`는 `/status` 스타일의 gateway 요약을 반환합니다. 민감한 필드는
  admin scope가 있는 operator 클라이언트에만 포함됩니다.
- `gateway.identity.get`은 relay 및
  pairing 흐름에서 사용되는 gateway 기기 identity를 반환합니다.
- `system-presence`는 현재 연결된
  operator/node 기기의 presence 스냅샷을 반환합니다.
- `system-event`는 시스템 이벤트를 추가하고 presence
  컨텍스트를 갱신/브로드캐스트할 수 있습니다.
- `last-heartbeat`는 가장 최근에 저장된 heartbeat 이벤트를 반환합니다.
- `set-heartbeats`는 gateway의 heartbeat 처리를 토글합니다.

### 모델 및 사용량

- `models.list`는 런타임에서 허용된 모델 카탈로그를 반환합니다.
- `usage.status`는 provider 사용량 기간/남은 할당량 요약을 반환합니다.
- `usage.cost`는 날짜 범위에 대한 집계된 비용 사용량 요약을 반환합니다.
- `doctor.memory.status`는
  활성 기본 에이전트 workspace의 벡터 메모리 / 임베딩 준비 상태를 반환합니다.
- `sessions.usage`는 세션별 사용량 요약을 반환합니다.
- `sessions.usage.timeseries`는 한 세션의 시계열 사용량을 반환합니다.
- `sessions.usage.logs`는 한 세션의 사용량 로그 항목을 반환합니다.

### 채널 및 login helper

- `channels.status`는 내장 + 번들 channel/plugin 상태 요약을 반환합니다.
- `channels.logout`은 해당 채널이
  logout을 지원하는 경우 특정 채널/account에서 로그아웃합니다.
- `web.login.start`는 현재 QR 지원 웹
  채널 provider에 대한 QR/web login 흐름을 시작합니다.
- `web.login.wait`는 해당 QR/web login 흐름이 완료될 때까지 기다리고 성공 시
  채널을 시작합니다.
- `push.test`는 등록된 iOS 노드에 테스트 APNs push를 보냅니다.
- `voicewake.get`은 저장된 wake-word 트리거를 반환합니다.
- `voicewake.set`은 wake-word 트리거를 업데이트하고 변경 사항을 브로드캐스트합니다.

### 메시징 및 로그

- `send`는 채팅 러너 외부에서 채널/account/thread 대상을 지정한
  발신 전달용 직접 RPC입니다.
- `logs.tail`은 커서/limit 및
  최대 바이트 제어와 함께 구성된 gateway 파일 로그 tail을 반환합니다.

### Talk 및 TTS

- `talk.config`는 유효한 Talk config 페이로드를 반환하며, `includeSecrets`에는
  `operator.talk.secrets`(또는 `operator.admin`)가 필요합니다.
- `talk.mode`는 WebChat/Control UI
  클라이언트를 위한 현재 Talk mode 상태를 설정/브로드캐스트합니다.
- `talk.speak`는 활성 Talk speech provider를 통해 음성을 합성합니다.
- `tts.status`는 TTS 활성 상태, 활성 provider, fallback providers,
  provider config 상태를 반환합니다.
- `tts.providers`는 표시 가능한 TTS provider 인벤토리를 반환합니다.
- `tts.enable` 및 `tts.disable`은 TTS 환경설정 상태를 토글합니다.
- `tts.setProvider`는 선호 TTS provider를 업데이트합니다.
- `tts.convert`는 일회성 텍스트 음성 변환을 실행합니다.

### 비밀, config, 업데이트 및 마법사

- `secrets.reload`는 활성 SecretRefs를 다시 확인하고 전체 성공 시에만
  런타임 secret 상태를 교체합니다.
- `secrets.resolve`는 특정
  명령/대상 집합에 대한 명령 대상 secret 할당을 확인합니다.
- `config.get`은 현재 config 스냅샷과 해시를 반환합니다.
- `config.set`은 검증된 config 페이로드를 기록합니다.
- `config.patch`는 부분 config 업데이트를 병합합니다.
- `config.apply`는 전체 config 페이로드를 검증 + 교체합니다.
- `config.schema`는 Control UI와
  CLI 도구에서 사용하는 라이브 config 스키마 페이로드를 반환합니다. 스키마,
  `uiHints`, 버전, 생성 메타데이터가 포함되며, 런타임이 로드할 수 있을 때는
  plugin + channel 스키마 메타데이터도 포함됩니다. 스키마에는 UI에서 사용하는 것과 동일한 라벨
  및 도움말 텍스트에서 파생된 field `title` / `description` 메타데이터가 포함되며,
  일치하는 field 문서가 존재할 경우 중첩 객체, 와일드카드, 배열 항목,
  `anyOf` / `oneOf` / `allOf` 구성 분기도 포함됩니다.
- `config.schema.lookup`은 하나의 config
  경로에 대한 경로 범위 lookup 페이로드를 반환합니다. 정규화된 경로, 얕은 스키마 노드,
  일치하는 힌트 + `hintPath`, UI/CLI 드릴다운을 위한 직접 자식 요약이 포함됩니다.
  - Lookup 스키마 노드는 사용자 대상 문서와 공통 검증 필드를 유지합니다:
    `title`, `description`, `type`, `enum`, `const`, `format`, `pattern`,
    숫자/문자열/배열/객체 경계, 그리고
    `additionalProperties`, `deprecated`, `readOnly`, `writeOnly` 같은 boolean 플래그.
  - 자식 요약은 `key`, 정규화된 `path`, `type`, `required`,
    `hasChildren`, 일치한 `hint` / `hintPath`를 노출합니다.
- `update.run`은 gateway 업데이트 흐름을 실행하고
  업데이트 자체가 성공했을 때만 재시작을 예약합니다.
- `wizard.start`, `wizard.next`, `wizard.status`, `wizard.cancel`은
  온보딩 마법사를 WS RPC로 노출합니다.

### 기존 주요 계열

#### 에이전트 및 workspace helper

- `agents.list`는 구성된 에이전트 항목을 반환합니다.
- `agents.create`, `agents.update`, `agents.delete`는 에이전트 레코드와
  workspace 연결을 관리합니다.
- `agents.files.list`, `agents.files.get`, `agents.files.set`은
  에이전트에 노출된 bootstrap workspace 파일을 관리합니다.
- `agent.identity.get`은 에이전트 또는
  세션의 유효 assistant identity를 반환합니다.
- `agent.wait`는 실행이 끝날 때까지 기다리고
  가능하면 최종 스냅샷을 반환합니다.

#### 세션 제어

- `sessions.list`는 현재 세션 인덱스를 반환합니다.
- `sessions.subscribe` 및 `sessions.unsubscribe`는 현재 WS 클라이언트에 대한
  세션 변경 이벤트 구독을 토글합니다.
- `sessions.messages.subscribe` 및 `sessions.messages.unsubscribe`는
  한 세션의 기록/메시지 이벤트 구독을 토글합니다.
- `sessions.preview`는 특정 세션
  키의 제한된 기록 미리보기를 반환합니다.
- `sessions.resolve`는 세션 대상을 확인하거나 정규화합니다.
- `sessions.create`는 새 세션 항목을 생성합니다.
- `sessions.send`는 기존 세션으로 메시지를 보냅니다.
- `sessions.steer`는 활성 세션에 대한 중단 후 방향 전환 변형입니다.
- `sessions.abort`는 세션의 활성 작업을 중단합니다.
- `sessions.patch`는 세션 메타데이터/재정의를 업데이트합니다.
- `sessions.reset`, `sessions.delete`, `sessions.compact`는 세션 유지보수를 수행합니다.
- `sessions.get`은 저장된 전체 세션 행을 반환합니다.
- 채팅 실행은 여전히 `chat.history`, `chat.send`, `chat.abort`, `chat.inject`를 사용합니다.
- `chat.history`는 UI 클라이언트용으로 표시 정규화가 적용됩니다. 인라인 지시문 태그는 보이는 텍스트에서 제거되고, 일반 텍스트 도구 호출 XML 페이로드(` <tool_call>...</tool_call>`, `<function_call>...</function_call>`,
  `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>`,
  잘린 도구 호출 블록 포함)와 유출된 ASCII/전각 모델 제어 토큰은 제거되며,
  정확히 `NO_REPLY` / `no_reply`인 순수 무응답 assistant 행은 생략되고,
  지나치게 큰 행은 플레이스홀더로 대체될 수 있습니다.

#### 기기 페어링 및 기기 토큰

- `device.pair.list`는 대기 중 및 승인된 페어링 기기를 반환합니다.
- `device.pair.approve`, `device.pair.reject`, `device.pair.remove`는
  기기 페어링 레코드를 관리합니다.
- `device.token.rotate`는 승인된 역할
  및 scope 범위 내에서 페어링된 기기 토큰을 교체합니다.
- `device.token.revoke`는 페어링된 기기 토큰을 폐기합니다.

#### 노드 페어링, invoke, 대기 작업

- `node.pair.request`, `node.pair.list`, `node.pair.approve`,
  `node.pair.reject`, `node.pair.verify`는 노드 페어링 및 bootstrap
  검증을 다룹니다.
- `node.list` 및 `node.describe`는 알려진/연결된 노드 상태를 반환합니다.
- `node.rename`은 페어링된 노드 레이블을 업데이트합니다.
- `node.invoke`는 연결된 노드로 명령을 전달합니다.
- `node.invoke.result`는 invoke 요청의 결과를 반환합니다.
- `node.event`는 노드에서 시작된 이벤트를 gateway로 다시 전달합니다.
- `node.canvas.capability.refresh`는 범위가 지정된 canvas 기능 토큰을 새로 고칩니다.
- `node.pending.pull` 및 `node.pending.ack`는 연결된 노드 큐 API입니다.
- `node.pending.enqueue` 및 `node.pending.drain`은
  오프라인/연결 해제된 노드용 영속 대기 작업을 관리합니다.

#### 승인 계열

- `exec.approval.request` 및 `exec.approval.resolve`는 일회성 exec
  승인 요청을 다룹니다.
- `exec.approval.waitDecision`은 하나의 대기 중 exec 승인을 기다리고
  최종 결정(또는 타임아웃 시 `null`)을 반환합니다.
- `exec.approvals.get` 및 `exec.approvals.set`은 gateway exec 승인
  정책 스냅샷을 관리합니다.
- `exec.approvals.node.get` 및 `exec.approvals.node.set`은 노드 릴레이 명령을 통해
  노드 로컬 exec 승인 정책을 관리합니다.
- `plugin.approval.request`, `plugin.approval.waitDecision`,
  `plugin.approval.resolve`는 plugin 정의 승인 흐름을 다룹니다.

#### 기타 주요 계열

- 자동화:
  - `wake`는 즉시 또는 다음 heartbeat 시 텍스트 주입 wake를 예약합니다
  - `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`,
    `cron.run`, `cron.runs`
- skills/tools: `skills.*`, `tools.catalog`, `tools.effective`

### 일반적인 이벤트 계열

- `chat`: `chat.inject` 및 기타 기록 전용 chat
  이벤트 같은 UI chat 업데이트.
- `session.message` 및 `session.tool`: 구독된 세션에 대한 기록/이벤트 스트림 업데이트.
- `sessions.changed`: 세션 인덱스 또는 메타데이터가 변경됨.
- `presence`: 시스템 presence 스냅샷 업데이트.
- `tick`: 주기적 keepalive / 생존 이벤트.
- `health`: gateway 상태 스냅샷 업데이트.
- `heartbeat`: heartbeat 이벤트 스트림 업데이트.
- `cron`: cron 실행/작업 변경 이벤트.
- `shutdown`: gateway 종료 알림.
- `node.pair.requested` / `node.pair.resolved`: 노드 페어링 수명 주기.
- `node.invoke.request`: 노드 invoke 요청 브로드캐스트.
- `device.pair.requested` / `device.pair.resolved`: 페어링 기기 수명 주기.
- `voicewake.changed`: wake-word 트리거 config가 변경됨.
- `exec.approval.requested` / `exec.approval.resolved`: exec 승인
  수명 주기.
- `plugin.approval.requested` / `plugin.approval.resolved`: plugin 승인
  수명 주기.

### 노드 helper 메서드

- 노드는 자동 허용 검사를 위한 현재 skill 실행 파일 목록을 가져오기 위해 `skills.bins`를 호출할 수 있습니다.

### operator helper 메서드

- operator는 에이전트의 런타임 도구 카탈로그를 가져오기 위해 `tools.catalog` (`operator.read`)를 호출할 수 있습니다. 응답에는 그룹화된 도구와 출처 메타데이터가 포함됩니다:
  - `source`: `core` 또는 `plugin`
  - `pluginId`: `source="plugin"`일 때 plugin 소유자
  - `optional`: plugin 도구가 선택 사항인지 여부
- operator는 세션의 런타임 유효 도구 인벤토리를 가져오기 위해 `tools.effective` (`operator.read`)를 호출할 수 있습니다.
  - `sessionKey`는 필수입니다.
  - gateway는 호출자가 제공한 인증 또는 전달 컨텍스트를 받아들이는 대신
    서버 측 세션에서 신뢰된 런타임 컨텍스트를 파생합니다.
  - 응답은 세션 범위이며 현재 활성 대화가 지금 사용할 수 있는 내용을 반영합니다.
    코어, plugin, 채널 도구가 포함됩니다.
- operator는 에이전트의 표시 가능한
  skill 인벤토리를 가져오기 위해 `skills.status` (`operator.read`)를 호출할 수 있습니다.
  - `agentId`는 선택 사항이며, 생략하면 기본 에이전트 workspace를 읽습니다.
  - 응답에는 원시 secret 값을 노출하지 않고
    적격성, 누락 요구 사항, config 검사, 정리된 설치 옵션이 포함됩니다.
- operator는
  ClawHub 발견 메타데이터를 위해 `skills.search` 및 `skills.detail` (`operator.read`)를 호출할 수 있습니다.
- operator는 `skills.install` (`operator.admin`)을 두 가지 모드로 호출할 수 있습니다:
  - ClawHub 모드: `{ source: "clawhub", slug, version?, force? }`는
    기본 에이전트 workspace `skills/` 디렉터리에 skill 폴더를 설치합니다.
  - Gateway 설치 모드: `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    는 gateway 호스트에서 선언된 `metadata.openclaw.install` 동작을 실행합니다.
- operator는 `skills.update` (`operator.admin`)를 두 가지 모드로 호출할 수 있습니다:
  - ClawHub 모드는 추적된 slug 하나 또는 기본 에이전트 workspace의
    모든 추적된 ClawHub 설치를 업데이트합니다.
  - Config 모드는 `skills.entries.<skillKey>` 값(예: `enabled`,
    `apiKey`, `env`)을 patch합니다.

## Exec 승인

- exec 요청에 승인이 필요하면 gateway는 `exec.approval.requested`를 브로드캐스트합니다.
- operator 클라이언트는 `exec.approval.resolve`를 호출해 이를 처리합니다(`operator.approvals` scope 필요).
- `host=node`의 경우 `exec.approval.request`에는 반드시 `systemRunPlan`(정규화된 `argv`/`cwd`/`rawCommand`/세션 메타데이터)이 포함되어야 합니다. `systemRunPlan`이 없는 요청은 거부됩니다.
- 승인 후 전달되는 `node.invoke system.run` 호출은 해당 정규
  `systemRunPlan`을 권위 있는 명령/cwd/세션 컨텍스트로 재사용합니다.
- 호출자가 prepare와 최종 승인된 `system.run` 전달 사이에서
  `command`, `rawCommand`, `cwd`, `agentId`, 또는
  `sessionKey`를 변경하면, gateway는 변경된 페이로드를 신뢰하는 대신
  실행을 거부합니다.

## 에이전트 전달 폴백

- `agent` 요청에는 아웃바운드 전달을 요청하기 위해 `deliver=true`를 포함할 수 있습니다.
- `bestEffortDeliver=false`는 엄격한 동작을 유지합니다. 확인되지 않았거나 내부 전용 전달 대상은 `INVALID_REQUEST`를 반환합니다.
- `bestEffortDeliver=true`는 외부 전달 가능한 경로를 확인할 수 없을 때
  세션 전용 실행으로 폴백할 수 있게 합니다(예: internal/webchat 세션 또는 모호한 다중 채널 config).

## 버전 관리

- `PROTOCOL_VERSION`은 `src/gateway/protocol/schema.ts`에 있습니다.
- 클라이언트는 `minProtocol` + `maxProtocol`을 보내며, 서버는 불일치를 거부합니다.
- 스키마 + 모델은 TypeBox 정의에서 생성됩니다:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

## 인증

- 공유 비밀 gateway 인증은 구성된 인증 모드에 따라
  `connect.params.auth.token` 또는
  `connect.params.auth.password`를 사용합니다.
- Tailscale Serve 같은 identity 기반 모드
  (`gateway.auth.allowTailscale: true`) 또는 비-loopback
  `gateway.auth.mode: "trusted-proxy"`는 `connect.params.auth.*` 대신
  요청 헤더에서 connect 인증 검사를 충족합니다.
- private-ingress `gateway.auth.mode: "none"`은 공유 비밀 connect 인증을
  완전히 건너뜁니다. 이 모드를 공개/비신뢰 유입에 노출하지 마세요.
- 페어링 후 Gateway는 연결
  역할 + scopes에 범위가 지정된 **기기 토큰**을 발급합니다. 이 토큰은 `hello-ok.auth.deviceToken`에 반환되며 클라이언트는 향후 연결을 위해 이를 저장해야 합니다.
- 클라이언트는 성공적으로 연결할 때마다 기본 `hello-ok.auth.deviceToken`을 저장해야 합니다.
- 저장된 기기 토큰으로 다시 연결할 때는 해당
  토큰에 대해 저장된 승인 scope 집합도 재사용해야 합니다. 이렇게 하면 이미 승인된
  읽기/프로브/상태 접근을 유지하고 재연결이 암묵적으로 더 좁은
  admin 전용 scope로 축소되는 일을 방지할 수 있습니다.
- 일반 연결 인증 우선순위는 명시적 공유 토큰/비밀번호 우선, 다음은 명시적
  `deviceToken`, 그다음 저장된 기기별 토큰, 마지막으로 bootstrap 토큰입니다.
- 추가 `hello-ok.auth.deviceTokens` 항목은 bootstrap 핸드오프 토큰입니다.
  `wss://` 또는 loopback/local pairing 같은 신뢰된 전송에서 bootstrap 인증을 사용해 연결한 경우에만 이를 저장하세요.
- 클라이언트가 명시적인 `deviceToken` 또는 명시적인 `scopes`를 제공하면,
  그 호출자 요청 scope 집합이 권위 있는 값으로 유지됩니다. 캐시된 scopes는
  클라이언트가 저장된 기기별 토큰을 재사용할 때만 재사용됩니다.
- 기기 토큰은 `device.token.rotate` 및
  `device.token.revoke`를 통해 교체/폐기할 수 있습니다(`operator.pairing` scope 필요).
- 토큰 발급/교체는 해당 기기의 페어링 항목에 기록된 승인 역할 집합 범위 내에
  유지됩니다. 토큰 교체로 페어링 승인이 한 번도 부여하지 않은
  역할로 기기의 권한을 확장할 수는 없습니다.
- 페어링 기기 토큰 세션에서는 호출자에게
  `operator.admin`이 없는 한 기기 관리가 자기 자신 범위로 제한됩니다. 비관리자 호출자는
  **자신의** 기기 항목만 제거/폐기/교체할 수 있습니다.
- `device.token.rotate`는 요청된 operator scope 집합도
  호출자의 현재 세션 scopes와 비교해 검사합니다. 비관리자 호출자는 자신이 이미 가진 것보다 더 넓은 operator scope 집합으로
  토큰을 교체할 수 없습니다.
- 인증 실패에는 `error.details.code`와 복구 힌트가 포함됩니다:
  - `error.details.canRetryWithDeviceToken` (boolean)
  - `error.details.recommendedNextStep` (`retry_with_device_token`, `update_auth_configuration`, `update_auth_credentials`, `wait_then_retry`, `review_auth_configuration`)
- `AUTH_TOKEN_MISMATCH`에 대한 클라이언트 동작:
  - 신뢰된 클라이언트는 캐시된 기기별 토큰으로 한 번의 제한된 재시도를 할 수 있습니다.
  - 해당 재시도가 실패하면 클라이언트는 자동 재연결 루프를 중단하고 운영자 조치 안내를 표시해야 합니다.

## 기기 identity + 페어링

- 노드는 키쌍 fingerprint에서 파생된
  안정적인 기기 identity (`device.id`)를 포함해야 합니다.
- Gateways는 기기 + 역할별 토큰을 발급합니다.
- 로컬 자동 승인이 활성화되지 않은 한 새 device ID에는 페어링 승인이 필요합니다.
- 페어링 자동 승인은 직접 로컬 loopback 연결을 중심으로 동작합니다.
- OpenClaw에는 신뢰된 공유 비밀 helper 흐름을 위한
  좁은 backend/container-local self-connect 경로도 있습니다.
- 같은 호스트 tailnet 또는 LAN 연결은 여전히 원격으로 취급되며
  페어링 승인이 필요합니다.
- 모든 WS 클라이언트는 `connect` 중에 `device` identity를 포함해야 합니다(operator + node).
  Control UI는 다음 모드에서만 이를 생략할 수 있습니다:
  - localhost 전용 비보안 HTTP 호환성을 위한 `gateway.controlUi.allowInsecureAuth=true`.
  - 성공적인 `gateway.auth.mode: "trusted-proxy"` operator Control UI 인증.
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true` (긴급 우회, 심각한 보안 저하).
- 모든 연결은 서버가 제공한 `connect.challenge` nonce에 서명해야 합니다.

### 기기 인증 마이그레이션 진단

여전히 챌린지 이전 서명 동작을 사용하는 레거시 클라이언트를 위해, `connect`는 이제
`error.details.reason`과 함께 `error.details.code` 아래
`DEVICE_AUTH_*` 세부 코드를 반환합니다.

일반적인 마이그레이션 실패:

| 메시지                      | details.code                     | details.reason           | 의미                                                |
| --------------------------- | -------------------------------- | ------------------------ | --------------------------------------------------- |
| `device nonce required`     | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | 클라이언트가 `device.nonce`를 생략했거나 빈 값으로 보냈습니다. |
| `device nonce mismatch`     | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | 클라이언트가 오래되었거나 잘못된 nonce로 서명했습니다. |
| `device signature invalid`  | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | 서명 페이로드가 v2 페이로드와 일치하지 않습니다.       |
| `device signature expired`  | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | 서명된 타임스탬프가 허용된 시차 범위를 벗어났습니다.   |
| `device identity mismatch`  | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id`가 공개 키 fingerprint와 일치하지 않습니다. |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | 공개 키 형식/정규화에 실패했습니다.                  |

마이그레이션 목표:

- 항상 `connect.challenge`를 기다리세요.
- 서버 nonce를 포함한 v2 페이로드에 서명하세요.
- 동일한 nonce를 `connect.params.device.nonce`에 보내세요.
- 권장 서명 페이로드는 `v3`이며, device/client/role/scopes/token/nonce 필드에 더해 `platform`과 `deviceFamily`도 바인딩합니다.
- 레거시 `v2` 서명은 호환성을 위해 계속 허용되지만, 페어링된 기기
  메타데이터 고정은 재연결 시 명령 정책을 계속 제어합니다.

## TLS + 핀닝

- WS 연결에 TLS를 지원합니다.
- 클라이언트는 선택적으로 gateway 인증서 fingerprint를 pin할 수 있습니다(`gateway.tls`
  config와 `gateway.remote.tlsFingerprint` 또는 CLI `--tls-fingerprint` 참조).

## 범위

이 프로토콜은 **전체 gateway API**(status, channels, models, chat,
agent, sessions, nodes, approvals 등)를 노출합니다. 정확한 표면은 `src/gateway/protocol/schema.ts`의 TypeBox 스키마로 정의됩니다.
