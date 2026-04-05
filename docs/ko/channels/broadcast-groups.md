---
read_when:
    - 브로드캐스트 그룹을 구성할 때
    - WhatsApp에서 다중 에이전트 응답을 디버깅할 때
status: experimental
summary: WhatsApp 메시지를 여러 에이전트에 브로드캐스트합니다
title: 브로드캐스트 그룹
x-i18n:
    generated_at: "2026-04-05T12:34:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1d117ae65ec3b63c2bd4b3c215d96f32d7eafa0f99a9cd7378e502c15e56ca56
    source_path: channels/broadcast-groups.md
    workflow: 15
---

# 브로드캐스트 그룹

**상태:** 실험적  
**버전:** 2026.1.9에 추가됨

## 개요

브로드캐스트 그룹을 사용하면 여러 에이전트가 동일한 메시지를 동시에 처리하고 응답할 수 있습니다. 이를 통해 하나의 WhatsApp 그룹 또는 DM에서 함께 작업하는 전문화된 에이전트 팀을 만들 수 있으며, 모두 하나의 전화번호를 사용합니다.

현재 범위: **WhatsApp 전용** (web 채널).

브로드캐스트 그룹은 채널 허용 목록과 그룹 활성화 규칙 이후에 평가됩니다. WhatsApp 그룹에서는 OpenClaw가 일반적으로 응답하는 경우(예: 그룹 설정에 따라 멘션이 있을 때) 브로드캐스트가 발생한다는 뜻입니다.

## 사용 사례

### 1. 전문화된 에이전트 팀

원자적이고 집중된 책임을 가진 여러 에이전트를 배포합니다:

```
Group: "Development Team"
Agents:
  - CodeReviewer (코드 스니펫 검토)
  - DocumentationBot (문서 생성)
  - SecurityAuditor (취약점 검사)
  - TestGenerator (테스트 케이스 제안)
```

각 에이전트는 동일한 메시지를 처리하고 자신의 전문 관점을 제공합니다.

### 2. 다국어 지원

```
Group: "International Support"
Agents:
  - Agent_EN (영어로 응답)
  - Agent_DE (독일어로 응답)
  - Agent_ES (스페인어로 응답)
```

### 3. 품질 보증 워크플로

```
Group: "Customer Support"
Agents:
  - SupportAgent (답변 제공)
  - QAAgent (품질 검토, 문제를 발견한 경우에만 응답)
```

### 4. 작업 자동화

```
Group: "Project Management"
Agents:
  - TaskTracker (작업 데이터베이스 업데이트)
  - TimeLogger (소요 시간 기록)
  - ReportGenerator (요약 생성)
```

## 구성

### 기본 설정

최상위 `broadcast` 섹션을 추가합니다(`bindings` 옆). 키는 WhatsApp 피어 ID입니다:

- 그룹 채팅: 그룹 JID(예: `120363403215116621@g.us`)
- DM: E.164 전화번호(예: `+15551234567`)

```json
{
  "broadcast": {
    "120363403215116621@g.us": ["alfred", "baerbel", "assistant3"]
  }
}
```

**결과:** OpenClaw가 이 채팅에 응답해야 할 때 세 에이전트가 모두 실행됩니다.

### 처리 전략

에이전트가 메시지를 처리하는 방식을 제어합니다:

#### 병렬(기본값)

모든 에이전트가 동시에 처리합니다:

```json
{
  "broadcast": {
    "strategy": "parallel",
    "120363403215116621@g.us": ["alfred", "baerbel"]
  }
}
```

#### 순차

에이전트가 순서대로 처리합니다(이전 에이전트가 끝날 때까지 다음 에이전트가 대기):

```json
{
  "broadcast": {
    "strategy": "sequential",
    "120363403215116621@g.us": ["alfred", "baerbel"]
  }
}
```

### 전체 예제

```json
{
  "agents": {
    "list": [
      {
        "id": "code-reviewer",
        "name": "Code Reviewer",
        "workspace": "/path/to/code-reviewer",
        "sandbox": { "mode": "all" }
      },
      {
        "id": "security-auditor",
        "name": "Security Auditor",
        "workspace": "/path/to/security-auditor",
        "sandbox": { "mode": "all" }
      },
      {
        "id": "docs-generator",
        "name": "Documentation Generator",
        "workspace": "/path/to/docs-generator",
        "sandbox": { "mode": "all" }
      }
    ]
  },
  "broadcast": {
    "strategy": "parallel",
    "120363403215116621@g.us": ["code-reviewer", "security-auditor", "docs-generator"],
    "120363424282127706@g.us": ["support-en", "support-de"],
    "+15555550123": ["assistant", "logger"]
  }
}
```

## 작동 방식

### 메시지 흐름

1. **수신 메시지**가 WhatsApp 그룹에 도착합니다
2. **브로드캐스트 확인**: 시스템이 피어 ID가 `broadcast`에 있는지 확인합니다
3. **브로드캐스트 목록에 있으면**:
   - 나열된 모든 에이전트가 메시지를 처리합니다
   - 각 에이전트는 자체 세션 키와 격리된 컨텍스트를 가집니다
   - 에이전트는 병렬(기본값) 또는 순차적으로 처리합니다
4. **브로드캐스트 목록에 없으면**:
   - 일반 라우팅이 적용됩니다(처음 일치하는 binding)

참고: 브로드캐스트 그룹은 채널 허용 목록이나 그룹 활성화 규칙(멘션/명령 등)을 우회하지 않습니다. 메시지가 처리 대상이 될 때 _어떤 에이전트가 실행되는지_ 만 변경합니다.

### 세션 격리

브로드캐스트 그룹의 각 에이전트는 다음을 완전히 분리해서 유지합니다:

- **세션 키** (`agent:alfred:whatsapp:group:120363...` 대 `agent:baerbel:whatsapp:group:120363...`)
- **대화 기록** (에이전트는 다른 에이전트의 메시지를 보지 못함)
- **워크스페이스** (구성된 경우 별도 샌드박스)
- **도구 접근 권한** (서로 다른 허용/거부 목록)
- **메모리/컨텍스트** (별도 `IDENTITY.md`, `SOUL.md` 등)
- **그룹 컨텍스트 버퍼** (컨텍스트에 사용되는 최근 그룹 메시지)는 피어별로 공유되므로, 트리거될 때 모든 브로드캐스트 에이전트가 동일한 컨텍스트를 봅니다

이를 통해 각 에이전트는 다음을 가질 수 있습니다:

- 서로 다른 성격
- 서로 다른 도구 접근 권한(예: 읽기 전용 대 읽기-쓰기)
- 서로 다른 모델(예: opus 대 sonnet)
- 서로 다른 Skills 설치

### 예: 격리된 세션

그룹 `120363403215116621@g.us`에 에이전트 `["alfred", "baerbel"]`가 있는 경우:

**Alfred의 컨텍스트:**

```
Session: agent:alfred:whatsapp:group:120363403215116621@g.us
History: [사용자 메시지, alfred의 이전 응답]
Workspace: /Users/user/openclaw-alfred/
Tools: read, write, exec
```

**Bärbel의 컨텍스트:**

```
Session: agent:baerbel:whatsapp:group:120363403215116621@g.us
History: [사용자 메시지, baerbel의 이전 응답]
Workspace: /Users/user/openclaw-baerbel/
Tools: read only
```

## 모범 사례

### 1. 에이전트의 역할을 집중시키기

각 에이전트를 하나의 명확한 책임으로 설계합니다:

```json
{
  "broadcast": {
    "DEV_GROUP": ["formatter", "linter", "tester"]
  }
}
```

✅ **좋음:** 각 에이전트에 하나의 역할이 있음  
❌ **나쁨:** 범용 "dev-helper" 에이전트 하나

### 2. 설명적인 이름 사용

각 에이전트가 무엇을 하는지 명확하게 만드세요:

```json
{
  "agents": {
    "security-scanner": { "name": "Security Scanner" },
    "code-formatter": { "name": "Code Formatter" },
    "test-generator": { "name": "Test Generator" }
  }
}
```

### 3. 서로 다른 도구 접근 권한 구성

각 에이전트에 필요한 도구만 부여하세요:

```json
{
  "agents": {
    "reviewer": {
      "tools": { "allow": ["read", "exec"] } // 읽기 전용
    },
    "fixer": {
      "tools": { "allow": ["read", "write", "edit", "exec"] } // 읽기-쓰기
    }
  }
}
```

### 4. 성능 모니터링

에이전트가 많다면 다음을 고려하세요:

- 속도를 위해 `"strategy": "parallel"`(기본값) 사용
- 브로드캐스트 그룹을 5~10개 에이전트로 제한
- 더 단순한 에이전트에는 더 빠른 모델 사용

### 5. 실패를 우아하게 처리

에이전트는 독립적으로 실패합니다. 한 에이전트의 오류가 다른 에이전트를 막지 않습니다:

```
Message → [Agent A ✓, Agent B ✗ error, Agent C ✓]
Result: Agent A와 C는 응답, Agent B는 오류 기록
```

## 호환성

### 제공자

브로드캐스트 그룹은 현재 다음과 함께 작동합니다:

- ✅ WhatsApp (구현됨)
- 🚧 Telegram (계획됨)
- 🚧 Discord (계획됨)
- 🚧 Slack (계획됨)

### 라우팅

브로드캐스트 그룹은 기존 라우팅과 함께 작동합니다:

```json
{
  "bindings": [
    {
      "match": { "channel": "whatsapp", "peer": { "kind": "group", "id": "GROUP_A" } },
      "agentId": "alfred"
    }
  ],
  "broadcast": {
    "GROUP_B": ["agent1", "agent2"]
  }
}
```

- `GROUP_A`: alfred만 응답함(일반 라우팅)
- `GROUP_B`: agent1과 agent2가 모두 응답함(브로드캐스트)

**우선순위:** `broadcast`가 `bindings`보다 우선합니다.

## 문제 해결

### 에이전트가 응답하지 않음

**확인할 사항:**

1. 에이전트 ID가 `agents.list`에 존재하는지
2. 피어 ID 형식이 올바른지(예: `120363403215116621@g.us`)
3. 에이전트가 거부 목록에 없는지

**디버그:**

```bash
tail -f ~/.openclaw/logs/gateway.log | grep broadcast
```

### 하나의 에이전트만 응답함

**원인:** 피어 ID가 `bindings`에는 있지만 `broadcast`에는 없을 수 있습니다.

**해결:** 브로드캐스트 구성에 추가하거나 bindings에서 제거하세요.

### 성능 문제

**에이전트가 많아 느릴 때:**

- 그룹당 에이전트 수 줄이기
- 더 가벼운 모델 사용(opus 대신 sonnet)
- 샌드박스 시작 시간 확인

## 예제

### 예제 1: 코드 리뷰 팀

```json
{
  "broadcast": {
    "strategy": "parallel",
    "120363403215116621@g.us": [
      "code-formatter",
      "security-scanner",
      "test-coverage",
      "docs-checker"
    ]
  },
  "agents": {
    "list": [
      {
        "id": "code-formatter",
        "workspace": "~/agents/formatter",
        "tools": { "allow": ["read", "write"] }
      },
      {
        "id": "security-scanner",
        "workspace": "~/agents/security",
        "tools": { "allow": ["read", "exec"] }
      },
      {
        "id": "test-coverage",
        "workspace": "~/agents/testing",
        "tools": { "allow": ["read", "exec"] }
      },
      { "id": "docs-checker", "workspace": "~/agents/docs", "tools": { "allow": ["read"] } }
    ]
  }
}
```

**사용자 전송:** 코드 스니펫  
**응답:**

- code-formatter: "들여쓰기를 수정하고 타입 힌트를 추가했습니다"
- security-scanner: "⚠️ 12번째 줄에 SQL 인젝션 취약점이 있습니다"
- test-coverage: "커버리지는 45%이며 오류 사례에 대한 테스트가 누락되어 있습니다"
- docs-checker: "함수 `process_data`에 대한 docstring이 누락되어 있습니다"

### 예제 2: 다국어 지원

```json
{
  "broadcast": {
    "strategy": "sequential",
    "+15555550123": ["detect-language", "translator-en", "translator-de"]
  },
  "agents": {
    "list": [
      { "id": "detect-language", "workspace": "~/agents/lang-detect" },
      { "id": "translator-en", "workspace": "~/agents/translate-en" },
      { "id": "translator-de", "workspace": "~/agents/translate-de" }
    ]
  }
}
```

## API 참조

### 구성 스키마

```typescript
interface OpenClawConfig {
  broadcast?: {
    strategy?: "parallel" | "sequential";
    [peerId: string]: string[];
  };
}
```

### 필드

- `strategy` (선택 사항): 에이전트를 처리하는 방식
  - `"parallel"` (기본값): 모든 에이전트가 동시에 처리
  - `"sequential"`: 에이전트가 배열 순서대로 처리
- `[peerId]`: WhatsApp 그룹 JID, E.164 번호 또는 기타 피어 ID
  - 값: 메시지를 처리해야 하는 에이전트 ID 배열

## 제한 사항

1. **최대 에이전트 수:** 하드 제한은 없지만 10개 이상 에이전트는 느릴 수 있습니다
2. **공유 컨텍스트:** 에이전트는 서로의 응답을 보지 못합니다(의도된 동작)
3. **메시지 순서:** 병렬 응답은 어떤 순서로든 도착할 수 있습니다
4. **속도 제한:** 모든 에이전트가 WhatsApp 속도 제한에 포함됩니다

## 향후 개선 사항

계획된 기능:

- [ ] 공유 컨텍스트 모드(에이전트가 서로의 응답을 볼 수 있음)
- [ ] 에이전트 조정(에이전트가 서로에게 신호를 보낼 수 있음)
- [ ] 동적 에이전트 선택(메시지 내용에 따라 에이전트 선택)
- [ ] 에이전트 우선순위(일부 에이전트가 다른 에이전트보다 먼저 응답)

## 함께 보기

- [다중 에이전트 구성](/tools/multi-agent-sandbox-tools)
- [라우팅 구성](/channels/channel-routing)
- [세션 관리](/concepts/session)
