---
read_when:
    - 세션 라우팅과 격리를 이해하려는 경우
    - 다중 사용자 구성에서 DM 범위를 설정하려는 경우
summary: OpenClaw가 대화 세션을 관리하는 방법
title: 세션 관리
x-i18n:
    generated_at: "2026-04-05T12:40:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab985781e54b22a034489dafa4b52cc204b1a5da22ee9b62edc7f6697512cea1
    source_path: concepts/session.md
    workflow: 15
---

# 세션 관리

OpenClaw는 대화를 **세션**으로 구성합니다. 각 메시지는 DM, 그룹 채팅, cron 작업 등 메시지가 들어온 위치를 기준으로 세션으로 라우팅됩니다.

## 메시지 라우팅 방식

| 소스 | 동작 |
| --------------- | ------------------------- |
| 다이렉트 메시지 | 기본적으로 공유 세션 |
| 그룹 채팅 | 그룹별로 격리 |
| 룸/채널 | 룸별로 격리 |
| cron 작업 | 실행마다 새 세션 |
| 웹훅 | hook별로 격리 |

## DM 격리

기본적으로 모든 DM은 연속성을 위해 하나의 세션을 공유합니다. 이는 단일 사용자 구성에서는 괜찮습니다.

<Warning>
여러 사람이 에이전트에 메시지를 보낼 수 있다면 DM 격리를 활성화하세요. 그렇지 않으면 모든 사용자가 동일한 대화 컨텍스트를 공유하게 되며, Alice의 비공개 메시지가 Bob에게 보이게 됩니다.
</Warning>

**해결 방법:**

```json5
{
  session: {
    dmScope: "per-channel-peer", // 채널 + 발신자 기준으로 격리
  },
}
```

다른 옵션:

- `main` (기본값) -- 모든 DM이 하나의 세션을 공유
- `per-peer` -- 발신자별로 격리(채널 간)
- `per-channel-peer` -- 채널 + 발신자별로 격리(권장)
- `per-account-channel-peer` -- 계정 + 채널 + 발신자별로 격리

<Tip>
같은 사람이 여러 채널에서 연락하는 경우 `session.identityLinks`를 사용해 해당 신원을 연결하면 하나의 세션을 공유할 수 있습니다.
</Tip>

`openclaw security audit`로 구성을 확인하세요.

## 세션 수명 주기

세션은 만료될 때까지 재사용됩니다.

- **일일 재설정** (기본값) -- gateway 호스트의 현지 시간 오전 4:00에 새 세션 생성
- **유휴 재설정** (선택 사항) -- 일정 기간 활동이 없으면 새 세션 생성. `session.reset.idleMinutes` 설정
- **수동 재설정** -- 채팅에서 `/new` 또는 `/reset` 입력. `/new <model>`은 모델도 함께 전환

일일 재설정과 유휴 재설정이 모두 구성된 경우 먼저 만료되는 쪽이 적용됩니다.

## 상태가 저장되는 위치

모든 세션 상태는 **gateway**가 소유합니다. UI 클라이언트는 세션 데이터를 위해 gateway에 질의합니다.

- **저장소:** `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- **트랜스크립트:** `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`

## 세션 유지 관리

OpenClaw는 시간이 지나면서 세션 저장소 크기를 자동으로 제한합니다. 기본적으로 `warn` 모드로 실행되며(정리될 내용을 보고만 함), 자동 정리를 하려면 `session.maintenance.mode`를 `"enforce"`로 설정하세요.

```json5
{
  session: {
    maintenance: {
      mode: "enforce",
      pruneAfter: "30d",
      maxEntries: 500,
    },
  },
}
```

`openclaw sessions cleanup --dry-run`으로 미리 확인하세요.

## 세션 검사

- `openclaw status` -- 세션 저장소 경로 및 최근 활동
- `openclaw sessions --json` -- 모든 세션(`--active <minutes>`로 필터링)
- 채팅의 `/status` -- 컨텍스트 사용량, 모델, 토글
- `/context list` -- 시스템 프롬프트에 포함된 내용

## 추가 읽기

- [세션 프루닝](/concepts/session-pruning) -- tool 결과 다듬기
- [압축](/concepts/compaction) -- 긴 대화 요약
- [세션 도구](/concepts/session-tool) -- 세션 간 작업을 위한 에이전트 도구
- [세션 관리 심층 분석](/reference/session-management-compaction) -- 저장소 스키마, 트랜스크립트, 전송 정책, 원본 메타데이터, 고급 config
- [다중 에이전트](/concepts/multi-agent) — 에이전트 간 라우팅 및 세션 격리
- [백그라운드 작업](/automation/tasks) — 분리된 작업이 세션 참조와 함께 작업 레코드를 생성하는 방식
- [채널 라우팅](/channels/channel-routing) — 인바운드 메시지가 세션으로 라우팅되는 방식
