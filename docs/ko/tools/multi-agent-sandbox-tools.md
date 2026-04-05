---
read_when: “You want per-agent sandboxing or per-agent tool allow/deny policies in a multi-agent gateway.”
status: active
summary: 에이전트별 샌드박스 + 도구 제한, 우선순위, 예시
title: 멀티 에이전트 샌드박스 및 도구
x-i18n:
    generated_at: "2026-04-05T12:57:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 07985f7c8fae860a7b9bf685904903a4a8f90249e95e4179cf0775a1208c0597
    source_path: tools/multi-agent-sandbox-tools.md
    workflow: 15
---

# 멀티 에이전트 샌드박스 및 도구 구성

멀티 에이전트 설정에서는 각 에이전트가 전역 샌드박스 및 도구 정책을 재정의할 수 있습니다. 이 페이지에서는 에이전트별 구성, 우선순위 규칙, 예시를 다룹니다.

- **샌드박스 백엔드 및 모드**: [샌드박싱](/ko/gateway/sandboxing)을 참조하세요.
- **차단된 도구 디버깅**: [샌드박스 vs 도구 정책 vs Elevated](/ko/gateway/sandbox-vs-tool-policy-vs-elevated) 및 `openclaw sandbox explain`을 참조하세요.
- **Elevated exec**: [Elevated 모드](/tools/elevated)를 참조하세요.

인증은 에이전트별입니다. 각 에이전트는 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`에 있는 자체 `agentDir` 인증 저장소를 읽습니다.
자격 증명은 에이전트 간에 **공유되지 않습니다**. 에이전트 간에 `agentDir`를 재사용하지 마세요.
자격 증명을 공유하려면 `auth-profiles.json`을 다른 에이전트의 `agentDir`로 복사하세요.

---

## 구성 예시

### 예시 1: 개인용 + 제한된 가족용 에이전트

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "name": "Personal Assistant",
        "workspace": "~/.openclaw/workspace",
        "sandbox": { "mode": "off" }
      },
      {
        "id": "family",
        "name": "Family Bot",
        "workspace": "~/.openclaw/workspace-family",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["exec", "write", "edit", "apply_patch", "process", "browser"]
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "family",
      "match": {
        "provider": "whatsapp",
        "accountId": "*",
        "peer": {
          "kind": "group",
          "id": "120363424282127706@g.us"
        }
      }
    }
  ]
}
```

**결과:**

- `main` 에이전트: 호스트에서 실행, 전체 도구 액세스
- `family` 에이전트: Docker에서 실행(에이전트당 하나의 컨테이너), `read` 도구만 사용 가능

---

### 예시 2: 공유 샌드박스를 사용하는 업무용 에이전트

```json
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "workspace": "~/.openclaw/workspace-personal",
        "sandbox": { "mode": "off" }
      },
      {
        "id": "work",
        "workspace": "~/.openclaw/workspace-work",
        "sandbox": {
          "mode": "all",
          "scope": "shared",
          "workspaceRoot": "/tmp/work-sandboxes"
        },
        "tools": {
          "allow": ["read", "write", "apply_patch", "exec"],
          "deny": ["browser", "gateway", "discord"]
        }
      }
    ]
  }
}
```

---

### 예시 2b: 전역 coding 프로필 + 메시징 전용 에이전트

```json
{
  "tools": { "profile": "coding" },
  "agents": {
    "list": [
      {
        "id": "support",
        "tools": { "profile": "messaging", "allow": ["slack"] }
      }
    ]
  }
}
```

**결과:**

- 기본 에이전트는 coding 도구를 받습니다
- `support` 에이전트는 메시징 전용입니다(+ Slack 도구)

---

### 예시 3: 에이전트별로 다른 샌드박스 모드

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main", // 전역 기본값
        "scope": "session"
      }
    },
    "list": [
      {
        "id": "main",
        "workspace": "~/.openclaw/workspace",
        "sandbox": {
          "mode": "off" // 재정의: main은 절대 샌드박스되지 않음
        }
      },
      {
        "id": "public",
        "workspace": "~/.openclaw/workspace-public",
        "sandbox": {
          "mode": "all", // 재정의: public은 항상 샌드박스됨
          "scope": "agent"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["exec", "write", "edit", "apply_patch"]
        }
      }
    ]
  }
}
```

---

## 구성 우선순위

전역(`agents.defaults.*`) 및 에이전트별(`agents.list[].*`) 구성이 모두 존재할 때:

### 샌드박스 구성

에이전트별 설정이 전역 설정보다 우선합니다:

```
agents.list[].sandbox.mode > agents.defaults.sandbox.mode
agents.list[].sandbox.scope > agents.defaults.sandbox.scope
agents.list[].sandbox.workspaceRoot > agents.defaults.sandbox.workspaceRoot
agents.list[].sandbox.workspaceAccess > agents.defaults.sandbox.workspaceAccess
agents.list[].sandbox.docker.* > agents.defaults.sandbox.docker.*
agents.list[].sandbox.browser.* > agents.defaults.sandbox.browser.*
agents.list[].sandbox.prune.* > agents.defaults.sandbox.prune.*
```

**참고:**

- `agents.list[].sandbox.{docker,browser,prune}.*`는 해당 에이전트에 대해 `agents.defaults.sandbox.{docker,browser,prune}.*`를 재정의합니다(샌드박스 범위가 `"shared"`로 해석되면 무시됨).

### 도구 제한

필터링 순서는 다음과 같습니다:

1. **도구 프로필** (`tools.profile` 또는 `agents.list[].tools.profile`)
2. **공급자 도구 프로필** (`tools.byProvider[provider].profile` 또는 `agents.list[].tools.byProvider[provider].profile`)
3. **전역 도구 정책** (`tools.allow` / `tools.deny`)
4. **공급자 도구 정책** (`tools.byProvider[provider].allow/deny`)
5. **에이전트별 도구 정책** (`agents.list[].tools.allow/deny`)
6. **에이전트 공급자 정책** (`agents.list[].tools.byProvider[provider].allow/deny`)
7. **샌드박스 도구 정책** (`tools.sandbox.tools` 또는 `agents.list[].tools.sandbox.tools`)
8. **하위 에이전트 도구 정책** (`tools.subagents.tools`, 해당하는 경우)

각 단계는 도구를 더 제한할 수는 있지만, 앞선 단계에서 거부된 도구를 다시 허용할 수는 없습니다.
`agents.list[].tools.sandbox.tools`가 설정되면 해당 에이전트에 대해 `tools.sandbox.tools`를 대체합니다.
`agents.list[].tools.profile`이 설정되면 해당 에이전트에 대해 `tools.profile`을 재정의합니다.
공급자 도구 키는 `provider`(예: `google-antigravity`) 또는 `provider/model`(예: `openai/gpt-5.4`)을 사용할 수 있습니다.

도구 정책은 여러 도구로 확장되는 `group:*` 축약형을 지원합니다. 전체 목록은 [도구 그룹](/ko/gateway/sandbox-vs-tool-policy-vs-elevated#tool-groups-shorthands)를 참조하세요.

에이전트별 Elevated 재정의(`agents.list[].tools.elevated`)는 특정 에이전트에 대한 elevated exec를 추가로 제한할 수 있습니다. 자세한 내용은 [Elevated 모드](/tools/elevated)를 참조하세요.

---

## 단일 에이전트에서 마이그레이션

**이전(단일 에이전트):**

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.openclaw/workspace",
      "sandbox": {
        "mode": "non-main"
      }
    }
  },
  "tools": {
    "sandbox": {
      "tools": {
        "allow": ["read", "write", "apply_patch", "exec"],
        "deny": []
      }
    }
  }
}
```

**이후(서로 다른 프로필을 사용하는 멀티 에이전트):**

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "workspace": "~/.openclaw/workspace",
        "sandbox": { "mode": "off" }
      }
    ]
  }
}
```

레거시 `agent.*` 구성은 `openclaw doctor`로 마이그레이션됩니다. 앞으로는 `agents.defaults` + `agents.list`를 사용하는 것이 좋습니다.

---

## 도구 제한 예시

### 읽기 전용 에이전트

```json
{
  "tools": {
    "allow": ["read"],
    "deny": ["exec", "write", "edit", "apply_patch", "process"]
  }
}
```

### 안전한 실행 에이전트(파일 수정 없음)

```json
{
  "tools": {
    "allow": ["read", "exec", "process"],
    "deny": ["write", "edit", "apply_patch", "browser", "gateway"]
  }
}
```

### 통신 전용 에이전트

```json
{
  "tools": {
    "sessions": { "visibility": "tree" },
    "allow": ["sessions_list", "sessions_send", "sessions_history", "session_status"],
    "deny": ["exec", "write", "edit", "apply_patch", "read", "browser"]
  }
}
```

이 프로필의 `sessions_history`는 여전히 원시 전사 덤프가 아니라 제한되고 정제된 회상 보기를 반환합니다. 어시스턴트 회상에서는 thinking 태그, `<relevant-memories>` 스캐폴딩, 일반 텍스트 도구 호출 XML 페이로드(` <tool_call>...</tool_call>`,
`<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`,
`<function_calls>...</function_calls>`, 잘린 도구 호출 블록 포함),
축소된 도구 호출 스캐폴딩, 유출된 ASCII/전각 모델 제어 토큰,
잘못된 MiniMax 도구 호출 XML을 제거한 후 마스킹/잘라내기를 적용합니다.

---

## 흔한 함정: `"non-main"`

`agents.defaults.sandbox.mode: "non-main"`은 에이전트 ID가 아니라 `session.mainKey`(기본값 `"main"`)를 기준으로 합니다.
그룹/채널 세션은 항상 자체 키를 가지므로 non-main으로 처리되어 샌드박스됩니다.
에이전트를 절대 샌드박스하지 않으려면 `agents.list[].sandbox.mode: "off"`를 설정하세요.

---

## 테스트

멀티 에이전트 샌드박스 및 도구를 구성한 후:

1. **에이전트 해석 확인:**

   ```exec
   openclaw agents list --bindings
   ```

2. **샌드박스 컨테이너 확인:**

   ```exec
   docker ps --filter "name=openclaw-sbx-"
   ```

3. **도구 제한 테스트:**
   - 제한된 도구가 필요한 메시지를 보냅니다
   - 에이전트가 거부된 도구를 사용할 수 없는지 확인합니다

4. **로그 모니터링:**

   ```exec
   tail -f "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/logs/gateway.log" | grep -E "routing|sandbox|tools"
   ```

---

## 문제 해결

### `mode: "all"`인데도 에이전트가 샌드박스되지 않음

- 이를 재정의하는 전역 `agents.defaults.sandbox.mode`가 있는지 확인하세요
- 에이전트별 구성이 우선하므로 `agents.list[].sandbox.mode: "all"`을 설정하세요

### 거부 목록이 있는데도 도구를 계속 사용할 수 있음

- 도구 필터링 순서를 확인하세요: 전역 → 에이전트 → 샌드박스 → 하위 에이전트
- 각 단계는 더 제한할 수만 있고, 다시 허용할 수는 없습니다
- 로그로 확인하세요: `[tools] filtering tools for agent:${agentId}`

### 컨테이너가 에이전트별로 격리되지 않음

- 에이전트별 샌드박스 구성에서 `scope: "agent"`를 설정하세요
- 기본값은 `"session"`이며 세션당 하나의 컨테이너를 생성합니다

---

## 함께 보기

- [샌드박싱](/ko/gateway/sandboxing) -- 전체 샌드박스 참조(모드, 범위, 백엔드, 이미지)
- [샌드박스 vs 도구 정책 vs Elevated](/ko/gateway/sandbox-vs-tool-policy-vs-elevated) -- "왜 이것이 차단되나요?" 디버깅
- [Elevated 모드](/tools/elevated)
- [멀티 에이전트 라우팅](/ko/concepts/multi-agent)
- [샌드박스 구성](/ko/gateway/configuration-reference#agentsdefaultssandbox)
- [세션 관리](/ko/concepts/session)
