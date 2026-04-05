---
read_when:
    - 기기 페어링 요청을 승인하는 중
    - 기기 토큰을 교체하거나 폐기해야 함
summary: '`openclaw devices`용 CLI 참조(기기 페어링 + 토큰 교체/폐기)'
title: devices
x-i18n:
    generated_at: "2026-04-05T12:38:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: e2f9fcb8e3508a703590f87caaafd953a5d3557e11c958cbb2be1d67bb8720f4
    source_path: cli/devices.md
    workflow: 15
---

# `openclaw devices`

기기 페어링 요청과 기기 범위 토큰을 관리합니다.

## 명령

### `openclaw devices list`

대기 중인 페어링 요청과 페어링된 기기를 나열합니다.

```
openclaw devices list
openclaw devices list --json
```

대기 요청 출력에는 요청된 역할과 scopes가 포함되므로 승인 전에
검토할 수 있습니다.

### `openclaw devices remove <deviceId>`

페어링된 기기 항목 하나를 제거합니다.

페어링된 기기 토큰으로 인증된 경우, 비관리자 호출자는
**자신의** 기기 항목만 제거할 수 있습니다. 다른 기기를 제거하려면
`operator.admin`이 필요합니다.

```
openclaw devices remove <deviceId>
openclaw devices remove <deviceId> --json
```

### `openclaw devices clear --yes [--pending]`

페어링된 기기를 일괄 제거합니다.

```
openclaw devices clear --yes
openclaw devices clear --yes --pending
openclaw devices clear --yes --pending --json
```

### `openclaw devices approve [requestId] [--latest]`

대기 중인 기기 페어링 요청을 승인합니다. `requestId`를 생략하면 OpenClaw가
가장 최근의 대기 요청을 자동으로 승인합니다.

참고: 기기가 변경된 인증 세부 정보(역할/scopes/public
key)로 페어링을 다시 시도하면, OpenClaw는 이전 대기 항목을 대체하고 새
`requestId`를 발급합니다. 현재 ID를 사용하려면 승인 직전에
`openclaw devices list`를 실행하세요.

```
openclaw devices approve
openclaw devices approve <requestId>
openclaw devices approve --latest
```

### `openclaw devices reject <requestId>`

대기 중인 기기 페어링 요청을 거부합니다.

```
openclaw devices reject <requestId>
```

### `openclaw devices rotate --device <id> --role <role> [--scope <scope...>]`

특정 역할의 기기 토큰을 교체합니다(선택적으로 scopes도 업데이트).
대상 역할은 해당 기기의 승인된 페어링 계약에 이미 존재해야 하며,
교체로 새 미승인 역할을 발급할 수는 없습니다.
`--scope`를 생략하면, 저장된 교체 토큰으로 나중에 다시 연결할 때 그
토큰의 캐시된 승인 scopes를 재사용합니다. 명시적인 `--scope` 값을 전달하면,
그 값이 이후 캐시 토큰 재연결을 위한 저장된 scope 집합이 됩니다.
비관리자 페어링 기기 호출자는 **자신의** 기기 토큰만 교체할 수 있습니다.
또한 명시적인 `--scope` 값은 호출자 세션 자체의
operator scopes 범위 내에 있어야 하며, 교체로 호출자가 이미 가진 것보다 더 넓은 operator 토큰을 발급할 수는 없습니다.

```
openclaw devices rotate --device <deviceId> --role operator --scope operator.read --scope operator.write
```

새 토큰 페이로드를 JSON으로 반환합니다.

### `openclaw devices revoke --device <id> --role <role>`

특정 역할의 기기 토큰을 폐기합니다.

비관리자 페어링 기기 호출자는 **자신의** 기기 토큰만 폐기할 수 있습니다.
다른 기기의 토큰을 폐기하려면 `operator.admin`이 필요합니다.

```
openclaw devices revoke --device <deviceId> --role node
```

폐기 결과를 JSON으로 반환합니다.

## 공통 옵션

- `--url <url>`: Gateway WebSocket URL (`gateway.remote.url`이 구성된 경우 기본값으로 사용).
- `--token <token>`: Gateway 토큰(필요한 경우).
- `--password <password>`: Gateway 비밀번호(비밀번호 인증).
- `--timeout <ms>`: RPC 타임아웃.
- `--json`: JSON 출력(스크립팅에 권장).

참고: `--url`을 설정하면 CLI는 config 또는 환경 자격 증명으로 폴백하지 않습니다.
`--token` 또는 `--password`를 명시적으로 전달하세요. 명시적 자격 증명이 없으면 오류입니다.

## 참고

- 토큰 교체는 새 토큰을 반환합니다(민감 정보). 비밀처럼 취급하세요.
- 이 명령들은 `operator.pairing`(또는 `operator.admin`) scope가 필요합니다.
- 토큰 교체는 해당 기기의 승인된 페어링 역할 집합과 승인된 scope
  기준선 내에서만 이루어집니다. 잘못된 캐시 토큰 항목이 새
  교체 대상을 부여하지는 않습니다.
- 페어링 기기 토큰 세션에서는 기기 간 관리가 관리자 전용입니다.
  `remove`, `rotate`, `revoke`는 호출자에게
  `operator.admin`이 없는 한 자기 자신만 가능합니다.
- `devices clear`는 의도적으로 `--yes`로 보호됩니다.
- local loopback에서 페어링 scope를 사용할 수 없는 경우(`--url`을 명시적으로 전달하지 않았을 때), list/approve는 로컬 페어링 폴백을 사용할 수 있습니다.
- `devices approve`는 `requestId`를 생략하거나 `--latest`를 전달하면 가장 최근의 대기 요청을 자동으로 선택합니다.

## 토큰 드리프트 복구 체크리스트

Control UI 또는 다른 클라이언트에서 `AUTH_TOKEN_MISMATCH` 또는 `AUTH_DEVICE_TOKEN_MISMATCH`로 계속 실패할 때 사용하세요.

1. 현재 gateway 토큰 소스를 확인합니다.

```bash
openclaw config get gateway.auth.token
```

2. 페어링된 기기를 나열하고 영향을 받은 기기 ID를 식별합니다.

```bash
openclaw devices list
```

3. 영향을 받은 기기의 operator 토큰을 교체합니다.

```bash
openclaw devices rotate --device <deviceId> --role operator
```

4. 교체만으로 충분하지 않다면 오래된 페어링을 제거하고 다시 승인합니다.

```bash
openclaw devices remove <deviceId>
openclaw devices list
openclaw devices approve <requestId>
```

5. 현재 공유 토큰/비밀번호로 클라이언트 연결을 다시 시도합니다.

참고:

- 일반 재연결 인증 우선순위는 명시적 공유 토큰/비밀번호 우선, 그다음 명시적 `deviceToken`, 그다음 저장된 기기 토큰, 마지막으로 bootstrap 토큰입니다.
- 신뢰된 `AUTH_TOKEN_MISMATCH` 복구에서는 제한된 한 번의 재시도를 위해 공유 토큰과 저장된 기기 토큰을 함께 임시 전송할 수 있습니다.

관련 문서:

- [Dashboard auth troubleshooting](/web/dashboard#if-you-see-unauthorized-1008)
- [Gateway troubleshooting](/gateway/troubleshooting#dashboard-control-ui-connectivity)
