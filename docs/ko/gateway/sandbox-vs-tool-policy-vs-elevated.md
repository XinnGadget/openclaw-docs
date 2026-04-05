---
read_when: You hit 'sandbox jail' or see a tool/elevated refusal and want the exact config key to change.
status: active
summary: '도구가 차단되는 이유: sandbox 런타임, 도구 허용/거부 정책, 그리고 elevated exec 게이트'
title: Sandbox vs Tool Policy vs Elevated
x-i18n:
    generated_at: "2026-04-05T12:43:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8d5ddc1dbf02b89f18d46e5473ff0a29b8a984426fe2db7270c170f2de0cdeac
    source_path: gateway/sandbox-vs-tool-policy-vs-elevated.md
    workflow: 15
---

# Sandbox vs Tool Policy vs Elevated

OpenClaw에는 서로 관련은 있지만 서로 다른 세 가지 제어가 있습니다:

1. **Sandbox** (`agents.defaults.sandbox.*` / `agents.list[].sandbox.*`)는 **도구가 어디에서 실행되는지**를 결정합니다(Docker 대 호스트).
2. **Tool policy** (`tools.*`, `tools.sandbox.tools.*`, `agents.list[].tools.*`)는 **어떤 도구를 사용할 수 있고 허용할지**를 결정합니다.
3. **Elevated** (`tools.elevated.*`, `agents.list[].tools.elevated.*`)는 샌드박스 상태일 때 **샌드박스 밖에서 실행하기 위한 exec 전용 탈출구**입니다(기본값은 `gateway`, 또는 exec 대상이 `node`로 구성된 경우 `node`).

## 빠른 디버그

OpenClaw가 _실제로_ 무엇을 하고 있는지 확인하려면 inspector를 사용하세요:

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

다음이 출력됩니다:

- 유효한 sandbox 모드/범위/워크스페이스 접근
- 현재 세션이 실제로 sandbox 상태인지 여부(main vs non-main)
- 유효한 sandbox 도구 허용/거부(그리고 그것이 agent/global/default 중 어디에서 왔는지)
- elevated 게이트 및 수정용 키 경로

## Sandbox: 도구가 실행되는 위치

샌드박싱은 `agents.defaults.sandbox.mode`로 제어됩니다:

- `"off"`: 모든 것이 호스트에서 실행됩니다.
- `"non-main"`: non-main 세션만 샌드박스 처리됩니다(그룹/채널에서 흔히 발생하는 “놀라움”).
- `"all"`: 모든 것이 샌드박스 처리됩니다.

전체 매트릭스(범위, 워크스페이스 마운트, 이미지)는 [Sandboxing](/gateway/sandboxing)을 참조하세요.

### 바인드 마운트(보안 빠른 점검)

- `docker.binds`는 샌드박스 파일 시스템을 _관통_ 합니다. 마운트한 것은 무엇이든 설정한 모드(`:ro` 또는 `:rw`)로 컨테이너 내부에서 보입니다.
- 모드를 생략하면 기본값은 읽기-쓰기이며, 소스/비밀 정보에는 `:ro`를 권장합니다.
- `scope: "shared"`는 agent별 바인드를 무시합니다(전역 바인드만 적용됨).
- OpenClaw는 바인드 소스를 두 번 검증합니다. 먼저 정규화된 소스 경로에서, 그다음 가장 깊은 기존 상위를 통해 확인된 경로를 다시 해석한 뒤 한 번 더 검증합니다. 심볼릭 링크 상위 경로를 통한 탈출은 차단 경로나 허용 루트 검사를 우회할 수 없습니다.
- 존재하지 않는 리프 경로도 여전히 안전하게 검사됩니다. `/workspace/alias-out/new-file`가 심볼릭 링크된 상위를 통해 차단된 경로나 구성된 허용 루트 밖으로 해석되면 해당 바인드는 거부됩니다.
- `/var/run/docker.sock`를 바인드하면 사실상 샌드박스에 호스트 제어권을 넘기게 됩니다. 의도적인 경우에만 이렇게 하세요.
- 워크스페이스 접근(`workspaceAccess: "ro"`/`"rw"`)은 바인드 모드와 별개입니다.

## Tool policy: 어떤 도구가 존재하고 호출 가능한가

중요한 레이어는 두 가지입니다:

- **Tool profile**: `tools.profile` 및 `agents.list[].tools.profile` (기본 허용 목록)
- **Provider tool profile**: `tools.byProvider[provider].profile` 및 `agents.list[].tools.byProvider[provider].profile`
- **Global/per-agent tool policy**: `tools.allow`/`tools.deny` 및 `agents.list[].tools.allow`/`agents.list[].tools.deny`
- **Provider tool policy**: `tools.byProvider[provider].allow/deny` 및 `agents.list[].tools.byProvider[provider].allow/deny`
- **Sandbox tool policy** (샌드박스 상태일 때만 적용): `tools.sandbox.tools.allow`/`tools.sandbox.tools.deny` 및 `agents.list[].tools.sandbox.tools.*`

경험 법칙:

- `deny`가 항상 우선합니다.
- `allow`가 비어 있지 않으면, 그 외 모든 것은 차단된 것으로 처리됩니다.
- Tool policy는 최종 차단 지점입니다. `/exec`로도 거부된 `exec` 도구를 재정의할 수 없습니다.
- `/exec`는 권한 있는 발신자에 대해서만 세션 기본값을 변경하며, 도구 접근 권한을 부여하지는 않습니다.
  Provider tool 키는 `provider`(예: `google-antigravity`) 또는 `provider/model`(예: `openai/gpt-5.4`) 중 어느 쪽이든 사용할 수 있습니다.

### Tool groups(축약형)

도구 정책(global, agent, sandbox)은 여러 도구로 확장되는 `group:*` 항목을 지원합니다:

```json5
{
  tools: {
    sandbox: {
      tools: {
        allow: ["group:runtime", "group:fs", "group:sessions", "group:memory"],
      },
    },
  },
}
```

사용 가능한 그룹:

- `group:runtime`: `exec`, `process`, `code_execution` (`bash`는 `exec`의 별칭으로 허용됨)
- `group:fs`: `read`, `write`, `edit`, `apply_patch`
- `group:sessions`: `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status`
- `group:memory`: `memory_search`, `memory_get`
- `group:web`: `web_search`, `x_search`, `web_fetch`
- `group:ui`: `browser`, `canvas`
- `group:automation`: `cron`, `gateway`
- `group:messaging`: `message`
- `group:nodes`: `nodes`
- `group:agents`: `agents_list`
- `group:media`: `image`, `image_generate`, `tts`
- `group:openclaw`: 모든 내장 OpenClaw 도구(provider plugin 제외)

## Elevated: exec 전용 "호스트에서 실행"

Elevated는 추가 도구를 부여하지 않으며, `exec`에만 영향을 줍니다.

- 샌드박스 상태라면 `/elevated on`(또는 `elevated: true`인 `exec`)은 샌드박스 밖에서 실행됩니다(여전히 승인이 필요할 수 있음).
- 세션에 대해 exec 승인을 건너뛰려면 `/elevated full`을 사용하세요.
- 이미 직접 실행 중이라면 elevated는 사실상 no-op입니다(여전히 게이트가 적용됨).
- Elevated는 **skill 범위가 아니며** 도구 허용/거부를 재정의하지도 않습니다.
- Elevated는 `host=auto`에서 임의의 교차 호스트 재정의를 부여하지 않습니다. 정상적인 exec 대상 규칙을 따르며, 구성된/세션 대상이 이미 `node`인 경우에만 `node`를 유지합니다.
- `/exec`는 elevated와 별개입니다. 이것은 권한 있는 발신자에 대해 세션별 exec 기본값만 조정합니다.

게이트:

- 활성화: `tools.elevated.enabled` (및 선택적으로 `agents.list[].tools.elevated.enabled`)
- 발신자 허용 목록: `tools.elevated.allowFrom.<provider>` (및 선택적으로 `agents.list[].tools.elevated.allowFrom.<provider>`)

자세한 내용은 [Elevated Mode](/tools/elevated)를 참조하세요.

## 흔한 "sandbox 감옥" 해결 방법

### "도구 X가 sandbox tool policy에 의해 차단됨"

수정용 키(하나 선택):

- 샌드박스 비활성화: `agents.defaults.sandbox.mode=off` (또는 agent별 `agents.list[].sandbox.mode=off`)
- 샌드박스 내부에서 해당 도구 허용:
  - `tools.sandbox.tools.deny`(또는 agent별 `agents.list[].tools.sandbox.tools.deny`)에서 제거
  - 또는 `tools.sandbox.tools.allow`(또는 agent별 allow)에 추가

### "이게 main인 줄 알았는데, 왜 샌드박스 상태죠?"

`"non-main"` 모드에서는 그룹/채널 키가 _main_ 이 아닙니다. main 세션 키(`sandbox explain`에 표시됨)를 사용하거나 모드를 `"off"`로 전환하세요.

## 함께 보기

- [Sandboxing](/gateway/sandboxing) -- 전체 sandbox 참조(모드, 범위, 백엔드, 이미지)
- [다중 에이전트 Sandbox 및 Tools](/tools/multi-agent-sandbox-tools) -- agent별 재정의 및 우선순위
- [Elevated Mode](/tools/elevated)
