---
read_when:
    - cron 작업을 만들지 않고 시스템 이벤트를 대기열에 넣으려는 경우
    - heartbeat를 활성화하거나 비활성화해야 하는 경우
    - 시스템 presence 항목을 검사하려는 경우
summary: '`openclaw system`용 CLI 참조(시스템 이벤트, heartbeat, presence)'
title: system
x-i18n:
    generated_at: "2026-04-05T12:39:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: a7d19afde9d9cde8a79b0bb8cec6e5673466f4cb9b575fb40111fc32f4eee5d7
    source_path: cli/system.md
    workflow: 15
---

# `openclaw system`

Gateway를 위한 시스템 수준 도우미입니다. 시스템 이벤트를 대기열에 넣고, heartbeat를 제어하며, presence를 확인할 수 있습니다.

모든 `system` 하위 명령은 Gateway RPC를 사용하며 공통 클라이언트 플래그를 지원합니다.

- `--url <url>`
- `--token <token>`
- `--timeout <ms>`
- `--expect-final`

## 일반 명령

```bash
openclaw system event --text "긴급한 후속 조치가 있는지 확인해 줘" --mode now
openclaw system event --text "긴급한 후속 조치가 있는지 확인해 줘" --url ws://127.0.0.1:18789 --token "$OPENCLAW_GATEWAY_TOKEN"
openclaw system heartbeat enable
openclaw system heartbeat last
openclaw system presence
```

## `system event`

**메인** 세션에 시스템 이벤트를 대기열에 넣습니다. 다음 heartbeat가 이를 프롬프트의 `System:` 줄로 주입합니다. 즉시 heartbeat를 트리거하려면 `--mode now`를 사용하세요. `next-heartbeat`는 다음 예약 틱까지 기다립니다.

플래그:

- `--text <text>`: 필수 시스템 이벤트 텍스트
- `--mode <mode>`: `now` 또는 `next-heartbeat`(기본값)
- `--json`: 기계 판독 가능한 출력
- `--url`, `--token`, `--timeout`, `--expect-final`: 공통 Gateway RPC 플래그

## `system heartbeat last|enable|disable`

heartbeat 제어:

- `last`: 마지막 heartbeat 이벤트 표시
- `enable`: heartbeat를 다시 켭니다(비활성화된 경우 사용)
- `disable`: heartbeat 일시 중지

플래그:

- `--json`: 기계 판독 가능한 출력
- `--url`, `--token`, `--timeout`, `--expect-final`: 공통 Gateway RPC 플래그

## `system presence`

Gateway가 알고 있는 현재 시스템 presence 항목(노드, 인스턴스 및 유사한 상태 줄)을 나열합니다.

플래그:

- `--json`: 기계 판독 가능한 출력
- `--url`, `--token`, `--timeout`, `--expect-final`: 공통 Gateway RPC 플래그

## 참고

- 현재 config(로컬 또는 원격)를 통해 접근 가능한 실행 중인 Gateway가 필요합니다.
- 시스템 이벤트는 일시적이며 재시작 후에는 유지되지 않습니다.
