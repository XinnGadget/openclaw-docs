---
read_when:
    - API provider가 실패할 때 신뢰할 수 있는 대체 경로를 원할 때
    - Claude CLI 또는 다른 로컬 AI CLI를 실행 중이며 이를 재사용하고 싶을 때
    - CLI 백엔드 도구 접근을 위한 MCP loopback 브리지를 이해하고 싶을 때
summary: 'CLI 백엔드: 선택적 MCP 도구 브리지를 포함한 로컬 AI CLI 대체 경로'
title: CLI 백엔드
x-i18n:
    generated_at: "2026-04-05T12:42:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 823f3aeea6be50e5aa15b587e0944e79e862cecb7045f9dd44c93c544024bce1
    source_path: gateway/cli-backends.md
    workflow: 15
---

# CLI 백엔드(대체 런타임)

OpenClaw는 API provider가 중단되었거나,
속도 제한에 걸렸거나, 일시적으로 오동작할 때 **텍스트 전용 대체 경로**로 **로컬 AI CLI**를 실행할 수 있습니다. 이는 의도적으로 보수적으로 설계되었습니다:

- **OpenClaw 도구는 직접 주입되지 않지만**, `bundleMcp: true`
  인 백엔드(Claude CLI 기본값)는 loopback MCP 브리지를 통해 gateway 도구를 받을 수 있습니다.
- **JSONL 스트리밍**(Claude CLI는 `--output-format stream-json`을
  `--include-partial-messages`와 함께 사용하며, 프롬프트는 stdin으로 전송됨).
- **세션이 지원됩니다**(후속 턴이 일관성을 유지하도록).
- CLI가 이미지 경로를 허용한다면 **이미지를 전달할 수 있습니다**.

이 기능은 주 경로라기보다 **안전망**으로 설계되었습니다. 외부 API에 의존하지 않고
“항상 동작하는” 텍스트 응답을 원할 때 사용하세요.

ACP 세션 제어, 백그라운드 작업,
스레드/대화 바인딩, 지속적인 외부 코딩 세션을 갖춘 전체 하네스 런타임이 필요하다면
대신 [ACP Agents](/tools/acp-agents)를 사용하세요. CLI 백엔드는 ACP가 아닙니다.

## 초보자용 빠른 시작

아무 config 없이도 Claude CLI를 사용할 수 있습니다(번들 Anthropic plugin이
기본 백엔드를 등록합니다):

```bash
openclaw agent --message "hi" --model claude-cli/claude-sonnet-4-6
```

Codex CLI도 즉시 사용할 수 있습니다(번들 OpenAI plugin 경유):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

gateway가 launchd/systemd 아래에서 실행되고 PATH가 최소한으로 설정되어 있다면
명령 경로만 추가하세요:

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "claude-cli": {
          command: "/opt/homebrew/bin/claude",
        },
      },
    },
  },
}
```

이것으로 끝입니다. CLI 자체 외에는 키도, 추가 인증 config도 필요하지 않습니다.

번들 CLI 백엔드를 gateway 호스트에서 **기본 메시지 provider**로
사용하는 경우, 이제 OpenClaw는 config가 모델 ref 또는
`agents.defaults.cliBackends` 아래에서 해당 백엔드를 명시적으로 참조하면
소유 번들 plugin을 자동 로드합니다.

## 대체 경로로 사용하기

기본 모델이 실패할 때만 실행되도록 대체 목록에 CLI 백엔드를 추가하세요:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["claude-cli/claude-sonnet-4-6", "claude-cli/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "claude-cli/claude-sonnet-4-6": {},
        "claude-cli/claude-opus-4-6": {},
      },
    },
  },
}
```

참고:

- `agents.defaults.models`(허용 목록)을 사용한다면 `claude-cli/...`도 포함해야 합니다.
- 기본 provider가 실패하면(인증, 속도 제한, 시간 초과) OpenClaw가
  다음으로 CLI 백엔드를 시도합니다.
- 번들 Claude CLI 백엔드는 여전히
  `claude-cli/opus`, `claude-cli/opus-4.6`, `claude-cli/sonnet` 같은 짧은 별칭을 허용하지만, 문서와 config 예시는 정식 `claude-cli/claude-*` ref를 사용합니다.

## 구성 개요

모든 CLI 백엔드는 다음 아래에 있습니다:

```
agents.defaults.cliBackends
```

각 항목은 **provider id**(예: `claude-cli`, `my-cli`)로 키 지정됩니다.
provider id는 모델 ref의 왼쪽 부분이 됩니다:

```
<provider>/<model>
```

### 예시 config

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "claude-cli": {
          command: "/opt/homebrew/bin/claude",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## 작동 방식

1. provider 접두사(`claude-cli/...`)를 기준으로 **백엔드를 선택합니다**.
2. 동일한 OpenClaw 프롬프트 + 워크스페이스 context를 사용해 **시스템 프롬프트를 구성합니다**.
3. 기록이 일관되게 유지되도록 세션 id(지원되는 경우)와 함께 **CLI를 실행합니다**.
4. **출력을 파싱**하고(JSON 또는 일반 텍스트) 최종 텍스트를 반환합니다.
5. 백엔드별로 **세션 id를 유지**하므로 후속 턴이 같은 CLI 세션을 재사용합니다.

## 세션

- CLI가 세션을 지원한다면 `sessionArg`(예: `--session-id`) 또는
  ID를 여러 플래그에 삽입해야 하는 경우 `sessionArgs`(플레이스홀더 `{sessionId}`)를 설정하세요.
- CLI가 다른 플래그를 가진 **resume 하위 명령**을 사용한다면
  `resumeArgs`(`args`를 대체함)를 설정하고, 필요하면
  `resumeOutput`(JSON이 아닌 resume용)도 설정하세요.
- `sessionMode`:
  - `always`: 항상 세션 id를 보냅니다(저장된 값이 없으면 새 UUID).
  - `existing`: 이전에 저장된 세션 id가 있을 때만 보냅니다.
  - `none`: 세션 id를 보내지 않습니다.

직렬화 참고 사항:

- `serialize: true`는 같은 lane 실행의 순서를 유지합니다.
- 대부분의 CLI는 하나의 provider lane에서 직렬화합니다.
- `claude-cli`는 더 좁습니다. 재개된 실행은 Claude 세션 id별로 직렬화되고, 새 실행은 워크스페이스 경로별로 직렬화됩니다. 독립적인 워크스페이스는 병렬 실행할 수 있습니다.
- OpenClaw는 백엔드 인증 상태가 변경되면 저장된 CLI 세션 재사용을 버립니다. 여기에는 재로그인, 토큰 교체, 변경된 auth profile 자격 증명이 포함됩니다.

## 이미지(전달)

CLI가 이미지 경로를 허용한다면 `imageArg`를 설정하세요:

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw는 base64 이미지를 임시 파일에 기록합니다. `imageArg`가 설정되어 있으면 해당
경로가 CLI 인수로 전달됩니다. `imageArg`가 없으면 OpenClaw는
파일 경로를 프롬프트에 추가합니다(경로 주입). 이것만으로도 일반 경로에서 로컬 파일을 자동 로드하는
CLI에는 충분합니다(Claude CLI 동작).

## 입력 / 출력

- `output: "json"`(기본값)은 JSON을 파싱하여 텍스트 + 세션 id를 추출하려고 시도합니다.
- Gemini CLI JSON 출력의 경우 OpenClaw는 `usage`가 없거나 비어 있으면
  `response`에서 응답 텍스트를, `stats`에서 사용량을 읽습니다.
- `output: "jsonl"`은 JSONL 스트림(예: Claude CLI `stream-json`
  및 Codex CLI `--json`)을 파싱하고 최종 agent 메시지와 존재하는 경우 세션
  식별자를 추출합니다.
- `output: "text"`는 stdout을 최종 응답으로 취급합니다.

입력 모드:

- `input: "arg"`(기본값)는 프롬프트를 마지막 CLI 인수로 전달합니다.
- `input: "stdin"`은 프롬프트를 stdin으로 보냅니다.
- 프롬프트가 매우 길고 `maxPromptArgChars`가 설정되어 있으면 stdin이 사용됩니다.

## 기본값(plugin 소유)

번들 Anthropic plugin은 `claude-cli`에 대한 기본값을 등록합니다:

- `command: "claude"`
- `args: ["-p", "--output-format", "stream-json", "--include-partial-messages", "--verbose", "--permission-mode", "bypassPermissions"]`
- `resumeArgs: ["-p", "--output-format", "stream-json", "--include-partial-messages", "--verbose", "--permission-mode", "bypassPermissions", "--resume", "{sessionId}"]`
- `output: "jsonl"`
- `input: "stdin"`
- `modelArg: "--model"`
- `systemPromptArg: "--append-system-prompt"`
- `sessionArg: "--session-id"`
- `systemPromptWhen: "first"`
- `sessionMode: "always"`

번들 OpenAI plugin도 `codex-cli`에 대한 기본값을 등록합니다:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

번들 Google plugin도 `google-gemini-cli`에 대한 기본값을 등록합니다:

- `command: "gemini"`
- `args: ["--prompt", "--output-format", "json"]`
- `resumeArgs: ["--resume", "{sessionId}", "--prompt", "--output-format", "json"]`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

전제 조건: 로컬 Gemini CLI가 설치되어 있어야 하며
PATH에서 `gemini`로 사용할 수 있어야 합니다(`brew install gemini-cli` 또는
`npm install -g @google/gemini-cli`).

Gemini CLI JSON 참고 사항:

- 응답 텍스트는 JSON `response` 필드에서 읽습니다.
- `usage`가 없거나 비어 있으면 사용량은 `stats`로 대체됩니다.
- `stats.cached`는 OpenClaw `cacheRead`로 정규화됩니다.
- `stats.input`이 없으면 OpenClaw는
  `stats.input_tokens - stats.cached`에서 입력 토큰을 계산합니다.

필요한 경우에만 재정의하세요(일반적인 예: 절대 `command` 경로).

## plugin 소유 기본값

CLI 백엔드 기본값은 이제 plugin 표면의 일부입니다:

- plugin은 `api.registerCliBackend(...)`로 이를 등록합니다.
- 백엔드 `id`는 모델 ref의 provider 접두사가 됩니다.
- `agents.defaults.cliBackends.<id>` 아래의 사용자 config는 여전히 plugin 기본값을 재정의합니다.
- 백엔드별 config 정리는 선택적
  `normalizeConfig` 훅을 통해 plugin 소유로 유지됩니다.

## Bundle MCP 오버레이

CLI 백엔드는 **OpenClaw 도구 호출을 직접 받지 않지만**, 백엔드는
`bundleMcp: true`로 생성된 MCP config 오버레이를 선택적으로 사용할 수 있습니다.

현재 번들 동작:

- `claude-cli`: `bundleMcp: true`(기본값)
- `codex-cli`: bundle MCP 오버레이 없음
- `google-gemini-cli`: bundle MCP 오버레이 없음

bundle MCP가 활성화되면 OpenClaw는:

- gateway 도구를 CLI 프로세스에 노출하는 loopback HTTP MCP 서버를 실행합니다
- 세션별 토큰(`OPENCLAW_MCP_TOKEN`)으로 브리지를 인증합니다
- 도구 접근을 현재 세션, 계정, 채널 context로 제한합니다
- 현재 워크스페이스에 대해 활성화된 bundle-MCP 서버를 로드합니다
- 이를 기존 백엔드 `--mcp-config`와 병합합니다
- 생성된 파일을 전달하도록 CLI 인수를 `--strict-mcp-config --mcp-config <generated-file>`로 다시 작성합니다

`--strict-mcp-config` 플래그는 Claude CLI가 주변
사용자 수준 또는 전역 MCP 서버를 상속하지 못하게 합니다. MCP 서버가 활성화되어 있지 않더라도 OpenClaw는 백그라운드 실행이 격리된 상태를 유지하도록 엄격한 빈 config를 계속 주입합니다.

## 제한 사항

- **직접적인 OpenClaw 도구 호출은 없습니다.** OpenClaw는
  CLI 백엔드 프로토콜에 도구 호출을 주입하지 않습니다. 그러나 `bundleMcp: true`인 백엔드(기본값인
  Claude CLI)는 loopback MCP 브리지를 통해 gateway 도구를 받으므로,
  Claude CLI는 자체 native MCP 지원을 통해 OpenClaw 도구를 호출할 수 있습니다.
- **스트리밍은 백엔드별입니다.** Claude CLI는 JSONL 스트리밍
  (`stream-json` + `--include-partial-messages`)을 사용합니다. 다른 CLI 백엔드는
  종료 시점까지 버퍼링될 수 있습니다.
- **구조화된 출력**은 CLI의 JSON 형식에 따라 달라집니다.
- **Codex CLI 세션**은 텍스트 출력으로 resume하므로(JSONL 아님),
  초기 `--json` 실행보다 구조화 정도가 낮습니다. OpenClaw 세션은 여전히
  정상적으로 동작합니다.

## 문제 해결

- **CLI를 찾을 수 없음**: `command`를 전체 경로로 설정하세요.
- **잘못된 모델 이름**: `modelAliases`를 사용해 `provider/model` → CLI 모델로 매핑하세요.
- **세션 연속성이 없음**: `sessionArg`가 설정되어 있고 `sessionMode`가
  `none`이 아닌지 확인하세요(Codex CLI는 현재 JSON 출력으로 resume할 수 없음).
- **이미지가 무시됨**: `imageArg`를 설정하고(그리고 CLI가 파일 경로를 지원하는지 확인하세요).
