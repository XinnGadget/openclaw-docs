---
read_when:
    - ACP 기반 IDE 통합을 설정할 때
    - Gateway로의 ACP 세션 라우팅을 디버깅할 때
summary: IDE 통합용 ACP 브리지 실행
title: acp
x-i18n:
    generated_at: "2026-04-05T12:37:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2461b181e4a97dd84580581e9436ca1947a224decce8044132dbcf7fb2b7502c
    source_path: cli/acp.md
    workflow: 15
---

# acp

OpenClaw Gateway와 통신하는 [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) 브리지를 실행합니다.

이 명령은 IDE를 위해 stdio를 통해 ACP를 사용하고 프롬프트를 WebSocket을 통해 Gateway로 전달합니다. ACP 세션이 Gateway 세션 키에 매핑되도록 유지합니다.

`openclaw acp`는 Gateway 기반 ACP 브리지이며, 완전한 ACP 네이티브 편집기 런타임은 아닙니다. 세션 라우팅, 프롬프트 전달, 기본 스트리밍 업데이트에 중점을 둡니다.

외부 MCP 클라이언트가 ACP 하니스 세션을 호스팅하는 대신 OpenClaw 채널 대화에 직접 연결되게 하려면 [`openclaw mcp serve`](/cli/mcp)를 대신 사용하세요.

## 이것이 아닌 것

이 페이지는 종종 ACP 하니스 세션과 혼동됩니다.

`openclaw acp`의 의미는 다음과 같습니다.

- OpenClaw가 ACP 서버로 동작함
- IDE 또는 ACP 클라이언트가 OpenClaw에 연결함
- OpenClaw가 해당 작업을 Gateway 세션으로 전달함

이는 OpenClaw가 `acpx`를 통해 Codex 또는 Claude Code 같은 외부 하니스를 실행하는 [ACP 에이전트](/tools/acp-agents)와는 다릅니다.

간단한 기준:

- 편집기/클라이언트가 ACP로 OpenClaw와 통신하려는 경우: `openclaw acp` 사용
- OpenClaw가 Codex/Claude/Gemini를 ACP 하니스로 실행해야 하는 경우: `/acp spawn` 및 [ACP 에이전트](/tools/acp-agents) 사용

## 호환성 매트릭스

| ACP 영역 | 상태 | 참고 |
| --------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `initialize`, `newSession`, `prompt`, `cancel` | 구현됨 | stdio에서 Gateway chat/send + abort로 이어지는 핵심 브리지 흐름입니다. |
| `listSessions`, 슬래시 명령 | 구현됨 | 세션 목록은 Gateway 세션 상태를 기준으로 동작하며, 명령은 `available_commands_update`를 통해 광고됩니다. |
| `loadSession` | 부분 지원 | ACP 세션을 Gateway 세션 키에 다시 바인딩하고 저장된 사용자/assistant 텍스트 기록을 재생합니다. 도구/시스템 기록은 아직 재구성되지 않습니다. |
| 프롬프트 콘텐츠(`text`, 내장 `resource`, 이미지) | 부분 지원 | 텍스트/리소스는 채팅 입력으로 평탄화되고, 이미지는 Gateway 첨부 파일이 됩니다. |
| 세션 모드 | 부분 지원 | `session/set_mode`가 지원되며 브리지는 thought level, tool verbosity, reasoning, usage detail, elevated actions에 대한 초기 Gateway 기반 세션 제어를 노출합니다. 더 광범위한 ACP 네이티브 모드/config 표면은 아직 범위 밖입니다. |
| 세션 정보 및 사용량 업데이트 | 부분 지원 | 브리지는 캐시된 Gateway 세션 스냅샷에서 `session_info_update` 및 최선의 노력 방식의 `usage_update` 알림을 내보냅니다. 사용량은 근사치이며 Gateway 토큰 총계가 최신으로 표시될 때만 전송됩니다. |
| 도구 스트리밍 | 부분 지원 | `tool_call` / `tool_call_update` 이벤트에는 원시 I/O, 텍스트 콘텐츠, 그리고 Gateway 도구 인자/결과가 이를 노출할 경우 최선의 노력 방식의 파일 위치가 포함됩니다. 내장 터미널과 더 풍부한 diff 네이티브 출력은 아직 노출되지 않습니다. |
| 세션별 MCP 서버(`mcpServers`) | 지원되지 않음 | 브리지 모드는 세션별 MCP 서버 요청을 거부합니다. 대신 OpenClaw gateway 또는 agent에서 MCP를 구성하세요. |
| 클라이언트 파일시스템 메서드(`fs/read_text_file`, `fs/write_text_file`) | 지원되지 않음 | 브리지는 ACP 클라이언트 파일시스템 메서드를 호출하지 않습니다. |
| 클라이언트 터미널 메서드(`terminal/*`) | 지원되지 않음 | 브리지는 ACP 클라이언트 터미널을 생성하거나 tool call을 통해 터미널 ID를 스트리밍하지 않습니다. |
| 세션 계획 / thought 스트리밍 | 지원되지 않음 | 브리지는 현재 ACP 계획 또는 thought 업데이트가 아니라 출력 텍스트와 도구 상태를 내보냅니다. |

## 알려진 제한 사항

- `loadSession`은 저장된 사용자 및 assistant 텍스트 기록을 재생하지만, 과거 도구 호출, 시스템 알림 또는 더 풍부한 ACP 네이티브 이벤트 유형은 재구성하지 않습니다.
- 여러 ACP 클라이언트가 동일한 Gateway 세션 키를 공유하는 경우, 이벤트 및 취소 라우팅은 클라이언트별로 엄격히 격리되지 않고 최선의 노력 방식으로 동작합니다. 편집기 로컬 턴을 깔끔하게 유지해야 한다면 기본 격리된 `acp:<uuid>` 세션을 사용하는 것이 좋습니다.
- Gateway 중지 상태는 ACP 중지 사유로 변환되지만, 이 매핑은 완전한 ACP 네이티브 런타임보다 표현력이 떨어집니다.
- 초기 세션 제어는 현재 Gateway 노브의 일부에만 집중해 노출합니다: thought level, tool verbosity, reasoning, usage detail, elevated actions. 모델 선택과 exec-host 제어는 아직 ACP config 옵션으로 노출되지 않습니다.
- `session_info_update`와 `usage_update`는 실시간 ACP 네이티브 런타임 계정이 아니라 Gateway 세션 스냅샷에서 파생됩니다. 사용량은 근사치이며 비용 데이터는 포함하지 않고, Gateway가 총 토큰 데이터를 최신으로 표시할 때만 전송됩니다.
- 도구 추적 데이터는 최선의 노력 방식입니다. 브리지는 알려진 도구 인자/결과에 나타나는 파일 경로를 노출할 수 있지만, ACP 터미널이나 구조화된 파일 diff는 아직 내보내지 않습니다.

## 사용법

```bash
openclaw acp

# 원격 Gateway
openclaw acp --url wss://gateway-host:18789 --token <token>

# 원격 Gateway (파일에서 토큰 읽기)
openclaw acp --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token

# 기존 세션 키에 연결
openclaw acp --session agent:main:main

# 라벨로 연결(이미 존재해야 함)
openclaw acp --session-label "support inbox"

# 첫 번째 프롬프트 전에 세션 키 재설정
openclaw acp --session agent:main:main --reset-session
```

## ACP 클라이언트(디버그)

내장 ACP 클라이언트를 사용하면 IDE 없이 브리지를 기본 점검할 수 있습니다.
이 클라이언트는 ACP 브리지를 실행하고 프롬프트를 대화형으로 입력할 수 있게 합니다.

```bash
openclaw acp client

# 실행된 브리지를 원격 Gateway로 연결
openclaw acp client --server-args --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token

# 서버 명령 재정의(기본값: openclaw)
openclaw acp client --server "node" --server-args openclaw.mjs acp --url ws://127.0.0.1:19001
```

권한 모델(클라이언트 디버그 모드):

- 자동 승인은 허용 목록 기반이며 신뢰된 핵심 도구 ID에만 적용됩니다.
- `read` 자동 승인은 현재 작업 디렉터리(`--cwd`가 설정된 경우) 범위로 제한됩니다.
- ACP는 현재 작업 디렉터리 아래의 범위 제한 `read` 호출과 읽기 전용 검색 도구(`search`, `web_search`, `memory_search`) 같은 좁은 읽기 전용 범주만 자동 승인합니다. 알 수 없거나 비핵심 도구, 범위 밖 읽기, 실행 가능한 도구, 컨트롤 플레인 도구, 변경 도구, 대화형 흐름은 항상 명시적인 프롬프트 승인이 필요합니다.
- 서버가 제공하는 `toolCall.kind`는 신뢰할 수 없는 메타데이터로 취급되며(권한 부여의 근거가 아님).
- 이 ACP 브리지 정책은 ACPX 하니스 권한과 별개입니다. OpenClaw를 `acpx` 백엔드를 통해 실행하는 경우, `plugins.entries.acpx.config.permissionMode=approve-all`이 해당 하니스 세션의 비상 시 “yolo” 스위치입니다.

## 사용 방법

IDE(또는 다른 클라이언트)가 Agent Client Protocol을 사용하고, 이를 통해 OpenClaw Gateway 세션을 구동하고 싶을 때 ACP를 사용합니다.

1. Gateway가 실행 중인지 확인합니다(로컬 또는 원격).
2. Gateway 대상(config 또는 플래그)을 구성합니다.
3. IDE가 stdio를 통해 `openclaw acp`를 실행하도록 지정합니다.

예시 config(영구 저장):

```bash
openclaw config set gateway.remote.url wss://gateway-host:18789
openclaw config set gateway.remote.token <token>
```

예시 직접 실행(config 쓰기 없음):

```bash
openclaw acp --url wss://gateway-host:18789 --token <token>
# 로컬 프로세스 안전 측면에서 권장
openclaw acp --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token
```

## 에이전트 선택

ACP는 에이전트를 직접 선택하지 않습니다. Gateway 세션 키를 기준으로 라우팅합니다.

특정 에이전트를 대상으로 하려면 에이전트 범위 세션 키를 사용하세요.

```bash
openclaw acp --session agent:main:main
openclaw acp --session agent:design:main
openclaw acp --session agent:qa:bug-123
```

각 ACP 세션은 하나의 Gateway 세션 키에 매핑됩니다. 하나의 에이전트는 여러 세션을 가질 수 있으며, ACP는 키나 라벨을 재정의하지 않으면 기본적으로 격리된 `acp:<uuid>` 세션을 사용합니다.

세션별 `mcpServers`는 브리지 모드에서 지원되지 않습니다. ACP 클라이언트가 `newSession` 또는 `loadSession` 중 이를 보내면, 브리지는 조용히 무시하는 대신 명확한 오류를 반환합니다.

ACPX 기반 세션이 OpenClaw plugin 도구를 보도록 하려면, 세션별 `mcpServers`를 전달하려 하지 말고 gateway 측 ACPX plugin 브리지를 활성화하세요. 자세한 내용은 [ACP 에이전트](/tools/acp-agents#plugin-tools-mcp-bridge)를 참조하세요.

## `acpx`에서 사용하기(Codex, Claude, 기타 ACP 클라이언트)

Codex 또는 Claude Code 같은 코딩 에이전트가 ACP를 통해 OpenClaw bot과 통신하게 하려면, 내장 `openclaw` 대상을 갖춘 `acpx`를 사용하세요.

일반적인 흐름:

1. Gateway를 실행하고 ACP 브리지가 여기에 도달할 수 있는지 확인합니다.
2. `acpx openclaw`가 `openclaw acp`를 가리키도록 설정합니다.
3. 코딩 에이전트가 사용할 OpenClaw 세션 키를 대상으로 지정합니다.

예시:

```bash
# 기본 OpenClaw ACP 세션으로 단발성 요청 보내기
acpx openclaw exec "활성 OpenClaw 세션 상태를 요약해 줘."

# 후속 턴을 위한 지속적 이름 세션
acpx openclaw sessions ensure --name codex-bridge
acpx openclaw -s codex-bridge --cwd /path/to/repo \
  "이 리포지토리와 관련된 최근 컨텍스트를 내 OpenClaw 작업 에이전트에 물어봐."
```

`acpx openclaw`가 항상 특정 Gateway와 세션 키를 대상으로 하도록 하려면, `~/.acpx/config.json`에서 `openclaw` agent 명령을 재정의하세요.

```json
{
  "agents": {
    "openclaw": {
      "command": "env OPENCLAW_HIDE_BANNER=1 OPENCLAW_SUPPRESS_NOTES=1 openclaw acp --url ws://127.0.0.1:18789 --token-file ~/.openclaw/gateway.token --session agent:main:main"
    }
  }
}
```

리포지토리 로컬 OpenClaw 체크아웃의 경우, ACP 스트림을 깨끗하게 유지하기 위해 dev runner 대신 직접 CLI 엔트리포인트를 사용하세요. 예:

```bash
env OPENCLAW_HIDE_BANNER=1 OPENCLAW_SUPPRESS_NOTES=1 node openclaw.mjs acp ...
```

이것이 Codex, Claude Code 또는 다른 ACP 지원 클라이언트가 터미널을 스크래핑하지 않고 OpenClaw 에이전트에서 컨텍스트 정보를 가져오게 하는 가장 쉬운 방법입니다.

## Zed 편집기 설정

`~/.config/zed/settings.json`에 사용자 지정 ACP 에이전트를 추가하세요(또는 Zed의 Settings UI 사용):

```json
{
  "agent_servers": {
    "OpenClaw ACP": {
      "type": "custom",
      "command": "openclaw",
      "args": ["acp"],
      "env": {}
    }
  }
}
```

특정 Gateway 또는 에이전트를 대상으로 지정하려면:

```json
{
  "agent_servers": {
    "OpenClaw ACP": {
      "type": "custom",
      "command": "openclaw",
      "args": [
        "acp",
        "--url",
        "wss://gateway-host:18789",
        "--token",
        "<token>",
        "--session",
        "agent:design:main"
      ],
      "env": {}
    }
  }
}
```

Zed에서 Agent 패널을 열고 “OpenClaw ACP”를 선택해 스레드를 시작하세요.

## 세션 매핑

기본적으로 ACP 세션은 `acp:` 접두사가 있는 격리된 Gateway 세션 키를 받습니다.
알려진 세션을 재사용하려면 세션 키 또는 라벨을 전달하세요.

- `--session <key>`: 특정 Gateway 세션 키 사용
- `--session-label <label>`: 기존 세션을 라벨로 해석
- `--reset-session`: 해당 키에 대해 새 세션 ID 발급(같은 키, 새 트랜스크립트)

ACP 클라이언트가 메타데이터를 지원하면 세션별로 재정의할 수 있습니다.

```json
{
  "_meta": {
    "sessionKey": "agent:main:main",
    "sessionLabel": "support inbox",
    "resetSession": true
  }
}
```

세션 키에 대한 자세한 내용은 [/concepts/session](/concepts/session)을 참조하세요.

## 옵션

- `--url <url>`: Gateway WebSocket URL(configured 시 기본값은 gateway.remote.url)
- `--token <token>`: Gateway 인증 토큰
- `--token-file <path>`: 파일에서 Gateway 인증 토큰 읽기
- `--password <password>`: Gateway 인증 비밀번호
- `--password-file <path>`: 파일에서 Gateway 인증 비밀번호 읽기
- `--session <key>`: 기본 세션 키
- `--session-label <label>`: 해석할 기본 세션 라벨
- `--require-existing`: 세션 키/라벨이 존재하지 않으면 실패
- `--reset-session`: 첫 사용 전에 세션 키 재설정
- `--no-prefix-cwd`: 프롬프트 앞에 작업 디렉터리를 접두사로 붙이지 않음
- `--provenance <off|meta|meta+receipt>`: ACP provenance 메타데이터 또는 영수증 포함
- `--verbose, -v`: stderr에 상세 로그 출력

보안 참고:

- 일부 시스템에서는 `--token`과 `--password`가 로컬 프로세스 목록에 표시될 수 있습니다.
- `--token-file`/`--password-file` 또는 환경 변수(`OPENCLAW_GATEWAY_TOKEN`, `OPENCLAW_GATEWAY_PASSWORD`) 사용을 권장합니다.
- Gateway 인증 해석은 다른 Gateway 클라이언트가 사용하는 공통 계약을 따릅니다.
  - 로컬 모드: env (`OPENCLAW_GATEWAY_*`) -> `gateway.auth.*` -> `gateway.remote.*` 폴백은 `gateway.auth.*`가 설정되지 않은 경우에만 적용(설정되었지만 해석되지 않은 로컬 SecretRef는 fail closed)
  - 원격 모드: 원격 우선순위 규칙에 따른 env/config 폴백과 함께 `gateway.remote.*`
  - `--url`은 override-safe이며 암시적 config/env 자격 증명을 재사용하지 않습니다. 명시적인 `--token`/`--password`(또는 파일 변형)를 전달하세요.
- ACP 런타임 백엔드 자식 프로세스는 `OPENCLAW_SHELL=acp`를 받으며, 이는 컨텍스트별 셸/프로필 규칙에 사용할 수 있습니다.
- `openclaw acp client`는 실행된 브리지 프로세스에 `OPENCLAW_SHELL=acp-client`를 설정합니다.

### `acp client` 옵션

- `--cwd <dir>`: ACP 세션의 작업 디렉터리
- `--server <command>`: ACP 서버 명령(기본값: `openclaw`)
- `--server-args <args...>`: ACP 서버에 전달할 추가 인수
- `--server-verbose`: ACP 서버에서 상세 로그 활성화
- `--verbose, -v`: 상세 클라이언트 로그
