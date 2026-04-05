---
read_when:
    - 노드가 연결되어 있지만 camera/canvas/screen/exec 도구가 실패하는 경우
    - 노드 페어링과 approvals의 개념 차이를 이해해야 하는 경우
summary: 노드 페어링, 포그라운드 요구 사항, 권한, 도구 실패 문제 해결
title: 노드 문제 해결
x-i18n:
    generated_at: "2026-04-05T12:47:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: c2e431e6a35c482a655e01460bef9fab5d5a5ae7dc46f8f992ee51100f5c937e
    source_path: nodes/troubleshooting.md
    workflow: 15
---

# 노드 문제 해결

노드가 status에는 보이지만 노드 도구가 실패할 때 이 페이지를 사용하세요.

## 명령 순서

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

그런 다음 노드 전용 확인을 실행하세요.

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
```

정상 신호:

- 노드가 연결되어 있고 `node` 역할로 페어링되어 있음
- `nodes describe`에 호출하려는 capability가 포함되어 있음
- Exec approvals에 예상한 mode/허용 목록이 표시됨

## 포그라운드 요구 사항

`canvas.*`, `camera.*`, `screen.*`는 iOS/Android 노드에서 포그라운드 전용입니다.

빠른 확인 및 해결:

```bash
openclaw nodes describe --node <idOrNameOrIp>
openclaw nodes canvas snapshot --node <idOrNameOrIp>
openclaw logs --follow
```

`NODE_BACKGROUND_UNAVAILABLE`가 보이면 노드 앱을 포그라운드로 가져온 뒤 다시 시도하세요.

## 권한 매트릭스

| Capability | iOS | Android | macOS node app | 일반적인 실패 코드 |
| ---------------------------- | --------------------------------------- | -------------------------------------------- | ----------------------------- | ------------------------------ |
| `camera.snap`, `camera.clip` | Camera (+ clip 오디오용 mic) | Camera (+ clip 오디오용 mic) | Camera (+ clip 오디오용 mic) | `*_PERMISSION_REQUIRED` |
| `screen.record` | Screen Recording (+ mic 선택 사항) | 화면 캡처 프롬프트 (+ mic 선택 사항) | Screen Recording | `*_PERMISSION_REQUIRED` |
| `location.get` | While Using 또는 Always (모드에 따라 다름) | 모드에 따라 Foreground/Background 위치 | Location permission | `LOCATION_PERMISSION_REQUIRED` |
| `system.run` | 해당 없음 (node host 경로) | 해당 없음 (node host 경로) | Exec approvals 필요 | `SYSTEM_RUN_DENIED` |

## 페어링과 approvals의 차이

이 둘은 서로 다른 게이트입니다.

1. **디바이스 페어링**: 이 노드가 gateway에 연결할 수 있는가?
2. **Gateway 노드 명령 정책**: RPC 명령 ID가 `gateway.nodes.allowCommands` / `denyCommands` 및 플랫폼 기본값에서 허용되는가?
3. **Exec approvals**: 이 노드가 특정 셸 명령을 로컬에서 실행할 수 있는가?

빠른 확인:

```bash
openclaw devices list
openclaw nodes status
openclaw approvals get --node <idOrNameOrIp>
openclaw approvals allowlist add --node <idOrNameOrIp> "/usr/bin/uname"
```

페어링이 누락되었다면 먼저 노드 디바이스를 승인하세요.
`nodes describe`에 명령이 없다면 gateway 노드 명령 정책과 노드가 연결 시 실제로 해당 명령을 선언했는지 확인하세요.
페어링은 정상인데 `system.run`이 실패한다면 해당 노드의 exec approvals/허용 목록을 수정하세요.

노드 페어링은 정체성/신뢰 게이트이지 명령별 승인 표면이 아닙니다. `system.run`의 노드별 정책은 gateway 페어링 레코드가 아니라 해당 노드의 exec approvals 파일에 있습니다(`openclaw approvals get --node ...`).

승인 기반 `host=node` 실행의 경우 gateway는 준비된 정규 `systemRunPlan`에도 실행을 바인딩합니다. 나중의 호출자가 승인된 실행이 전달되기 전에 명령/cwd 또는 세션 메타데이터를 바꾸면, gateway는 편집된 payload를 신뢰하는 대신 승인 불일치로 실행을 거부합니다.

## 일반적인 노드 오류 코드

- `NODE_BACKGROUND_UNAVAILABLE` → 앱이 백그라운드 상태임; 포그라운드로 가져오기
- `CAMERA_DISABLED` → 노드 설정에서 카메라 토글이 비활성화됨
- `*_PERMISSION_REQUIRED` → OS 권한이 없거나 거부됨
- `LOCATION_DISABLED` → 위치 모드가 꺼져 있음
- `LOCATION_PERMISSION_REQUIRED` → 요청된 위치 모드가 허용되지 않음
- `LOCATION_BACKGROUND_UNAVAILABLE` → 앱이 백그라운드 상태인데 While Using 권한만 있음
- `SYSTEM_RUN_DENIED: approval required` → exec 요청에 명시적 승인이 필요함
- `SYSTEM_RUN_DENIED: allowlist miss` → 허용 목록 모드에서 명령이 차단됨  
  Windows node hosts에서는 `cmd.exe /c ...` 같은 셸 래퍼 형식은 ask 흐름으로 승인되지 않는 한 허용 목록 모드에서 allowlist miss로 처리됩니다.

## 빠른 복구 루프

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
```

그래도 해결되지 않으면:

- 디바이스 페어링 다시 승인
- 노드 앱 다시 열기(포그라운드)
- OS 권한 다시 부여
- Exec 승인 정책 재생성/조정

관련 문서:

- [/nodes/index](/nodes/index)
- [/nodes/camera](/nodes/camera)
- [/nodes/location-command](/nodes/location-command)
- [/tools/exec-approvals](/tools/exec-approvals)
- [/gateway/pairing](/gateway/pairing)
