---
read_when:
    - 상승 모드 기본값, 허용 목록 또는 슬래시 명령 동작을 조정하고 있습니다
    - 샌드박스된 에이전트가 어떻게 호스트에 접근할 수 있는지 이해하고 있습니다
summary: '상승된 exec 모드: 샌드박스된 에이전트에서 샌드박스 밖으로 명령 실행'
title: Elevated Mode
x-i18n:
    generated_at: "2026-04-05T12:56:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: f6f0ca0a7c03c94554a70fee775aa92085f15015850c3abaa2c1c46ced9d3c2e
    source_path: tools/elevated.md
    workflow: 15
---

# Elevated Mode

에이전트가 샌드박스 안에서 실행될 때 `exec` 명령은 샌드박스 환경 안으로
제한됩니다. **Elevated mode**를 사용하면 에이전트가 샌드박스를 벗어나
대신 샌드박스 밖에서 명령을 실행할 수 있으며, 승인 게이트를 구성할 수
있습니다.

<Info>
  Elevated mode는 에이전트가 **샌드박스된 경우에만** 동작을 변경합니다.
  샌드박스되지 않은 에이전트에서는 `exec`가 이미 호스트에서 실행됩니다.
</Info>

## 지시어

슬래시 명령으로 세션별 Elevated mode를 제어합니다:

| Directive | 동작 |
| ---------------- | ---------------------------------------------------------------------- |
| `/elevated on` | 구성된 호스트 경로에서 샌드박스 밖으로 실행하고, 승인은 유지 |
| `/elevated ask` | `on`과 동일(별칭) |
| `/elevated full` | 구성된 호스트 경로에서 샌드박스 밖으로 실행하고 승인 건너뜀 |
| `/elevated off` | 샌드박스 내부 실행으로 복귀 |

`/elev on|off|ask|full`로도 사용할 수 있습니다.

현재 수준을 보려면 인자 없이 `/elevated`를 보내세요.

## 동작 방식

<Steps>
  <Step title="사용 가능 여부 확인">
    config에서 Elevated가 활성화되어 있어야 하고 발신자가 허용 목록에 있어야
    합니다:

    ```json5
    {
      tools: {
        elevated: {
          enabled: true,
          allowFrom: {
            discord: ["user-id-123"],
            whatsapp: ["+15555550123"],
          },
        },
      },
    }
    ```

  </Step>

  <Step title="수준 설정">
    지시어만 있는 메시지를 보내 세션 기본값을 설정합니다:

    ```
    /elevated full
    ```

    또는 인라인으로 사용할 수 있습니다(해당 메시지에만 적용):

    ```
    /elevated on run the deployment script
    ```

  </Step>

  <Step title="명령은 샌드박스 밖에서 실행됨">
    Elevated가 활성화되면 `exec` 호출은 샌드박스를 벗어납니다. 실효
    호스트는 기본적으로 `gateway`이며, 구성되었거나 세션의 exec 대상이
    `node`일 때는 `node`가 됩니다. `full` 모드에서는 exec 승인이
    건너뛰어집니다. `on`/`ask` 모드에서는 구성된 승인 규칙이 계속
    적용됩니다.
  </Step>
</Steps>

## 해석 순서

1. 메시지의 **인라인 지시어**(해당 메시지에만 적용)
2. **세션 재정의**(지시어만 있는 메시지를 보내 설정)
3. **전역 기본값**(config의 `agents.defaults.elevatedDefault`)

## 사용 가능 여부 및 허용 목록

- **전역 게이트**: `tools.elevated.enabled`(`true`여야 함)
- **발신자 허용 목록**: 채널별 목록이 있는 `tools.elevated.allowFrom`
- **에이전트별 게이트**: `agents.list[].tools.elevated.enabled`(추가 제한만 가능)
- **에이전트별 허용 목록**: `agents.list[].tools.elevated.allowFrom`(발신자는 전역 + 에이전트별 둘 다 일치해야 함)
- **Discord 폴백**: `tools.elevated.allowFrom.discord`가 생략되면 `channels.discord.allowFrom`을 폴백으로 사용
- **모든 게이트를 통과해야** 하며, 그렇지 않으면 elevated는 사용할 수 없는 것으로 처리됩니다

허용 목록 항목 형식:

| Prefix | 일치 대상 |
| ----------------------- | ------------------------------- |
| (없음) | 발신자 ID, E.164 또는 From 필드 |
| `name:` | 발신자 표시 이름 |
| `username:` | 발신자 사용자 이름 |
| `tag:` | 발신자 태그 |
| `id:`, `from:`, `e164:` | 명시적 신원 대상 지정 |

## elevated가 제어하지 않는 것

- **도구 정책**: 도구 정책에 의해 `exec`가 거부되면 elevated로도 이를 재정의할 수 없습니다
- **호스트 선택 정책**: elevated는 `auto`를 자유로운 교차 호스트 재정의로 바꾸지 않습니다. 구성되었거나 세션의 exec 대상 규칙을 사용하며, 대상이 이미 `node`일 때만 `node`를 선택합니다.
- **`/exec`와는 별개**: `/exec` 지시어는 권한 있는 발신자를 위한 세션별 exec 기본값을 조정하며 elevated mode를 요구하지 않습니다

## 관련 문서

- [Exec tool](/tools/exec) — 셸 명령 실행
- [Exec approvals](/tools/exec-approvals) — 승인 및 허용 목록 시스템
- [샌드박싱](/ko/gateway/sandboxing) — 샌드박스 구성
- [샌드박스 vs 도구 정책 vs Elevated](/ko/gateway/sandbox-vs-tool-policy-vs-elevated)
