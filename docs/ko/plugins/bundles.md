---
read_when:
    - Codex, Claude 또는 Cursor 호환 번들을 설치하려는 경우
    - OpenClaw가 번들 콘텐츠를 네이티브 기능으로 어떻게 매핑하는지 이해해야 하는 경우
    - 번들 감지 또는 누락된 기능을 디버깅하는 경우
summary: Codex, Claude, Cursor 번들을 OpenClaw plugins로 설치하고 사용하기
title: Plugin Bundles
x-i18n:
    generated_at: "2026-04-05T12:49:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: a8b1eb4633bdff75425d8c2e29be352e11a4cdad7f420c0c66ae5ef07bf9bdcc
    source_path: plugins/bundles.md
    workflow: 15
---

# Plugin Bundles

OpenClaw는 **Codex**, **Claude**,
**Cursor**의 세 가지 외부 생태계에서 plugins를 설치할 수 있습니다. 이를 **bundles**라고 하며 —
OpenClaw가 이를 Skills, hooks, MCP tools 같은 네이티브 기능으로 매핑하는
콘텐츠 및 메타데이터 팩입니다.

<Info>
  Bundles는 네이티브 OpenClaw plugins와 **같지 않습니다**. 네이티브 plugins는
  인프로세스로 실행되며 어떤 기능이든 등록할 수 있습니다. Bundles는
  선택적 기능 매핑과 더 좁은 신뢰 경계를 가진 콘텐츠 팩입니다.
</Info>

## bundles가 존재하는 이유

유용한 plugin 중 다수는 Codex, Claude 또는 Cursor 형식으로 게시됩니다. 작성자가 이를 네이티브 OpenClaw plugin으로 다시 작성해야 하도록 하는 대신, OpenClaw는
이 형식을 감지하고 지원되는 콘텐츠를 네이티브 기능 집합으로 매핑합니다. 즉, Claude 명령 팩이나 Codex skill bundle을
설치하고 즉시 사용할 수 있습니다.

## bundle 설치

<Steps>
  <Step title="디렉터리, 아카이브 또는 마켓플레이스에서 설치">
    ```bash
    # 로컬 디렉터리
    openclaw plugins install ./my-bundle

    # 아카이브
    openclaw plugins install ./my-bundle.tgz

    # Claude 마켓플레이스
    openclaw plugins marketplace list <marketplace-name>
    openclaw plugins install <plugin-name>@<marketplace-name>
    ```

  </Step>

  <Step title="감지 확인">
    ```bash
    openclaw plugins list
    openclaw plugins inspect <id>
    ```

    Bundles는 `Format: bundle`로 표시되며, `codex`, `claude`, `cursor` 중 하나의 subtype을 가집니다.

  </Step>

  <Step title="재시작 후 사용">
    ```bash
    openclaw gateway restart
    ```

    매핑된 기능(Skills, hooks, MCP tools, LSP 기본값)은 다음 세션에서 사용할 수 있습니다.

  </Step>
</Steps>

## OpenClaw가 bundles에서 매핑하는 항목

현재 OpenClaw에서 모든 bundle 기능이 실행되는 것은 아닙니다. 다음은 현재 동작하는 항목과
감지되지만 아직 연결되지 않은 항목입니다.

### 현재 지원됨

| 기능          | 매핑 방식                                                                                  | 적용 대상      |
| ------------- | ------------------------------------------------------------------------------------------ | -------------- |
| Skill 콘텐츠  | Bundle skill 루트가 일반 OpenClaw Skills로 로드됨                                          | 모든 형식      |
| Commands      | `commands/` 및 `.cursor/commands/`가 skill 루트로 처리됨                                   | Claude, Cursor |
| Hook packs    | OpenClaw 스타일 `HOOK.md` + `handler.ts` 레이아웃                                          | Codex          |
| MCP tools     | Bundle MCP config가 내장 Pi 설정에 병합되고, 지원되는 stdio 및 HTTP 서버가 로드됨          | 모든 형식      |
| LSP 서버      | Claude `.lsp.json` 및 manifest에 선언된 `lspServers`가 내장 Pi LSP 기본값에 병합됨         | Claude         |
| Settings      | Claude `settings.json`이 내장 Pi 기본값으로 가져와짐                                       | Claude         |

#### Skill 콘텐츠

- bundle skill 루트는 일반 OpenClaw skill 루트로 로드됩니다
- Claude `commands` 루트는 추가 skill 루트로 처리됩니다
- Cursor `.cursor/commands` 루트는 추가 skill 루트로 처리됩니다

즉, Claude markdown 명령 파일은 일반 OpenClaw skill
로더를 통해 동작합니다. Cursor 명령 markdown도 같은 경로를 통해 동작합니다.

#### Hook packs

- bundle hook 루트는 일반 OpenClaw hook-pack
  레이아웃을 사용할 때만 동작합니다. 현재는 주로 Codex 호환 사례입니다:
  - `HOOK.md`
  - `handler.ts` 또는 `handler.js`

#### Pi용 MCP

- 활성화된 bundles는 MCP 서버 config를 제공할 수 있습니다
- OpenClaw는 bundle MCP config를 유효한 내장 Pi 설정의
  `mcpServers`로 병합합니다
- OpenClaw는 지원되는 bundle MCP tools를 내장 Pi agent 턴 동안 노출하며,
  이를 위해 stdio 서버를 실행하거나 HTTP 서버에 연결합니다
- 프로젝트 로컬 Pi 설정은 여전히 bundle 기본값 이후에 적용되므로,
  필요할 경우 워크스페이스 설정이 bundle MCP 항목을 재정의할 수 있습니다
- bundle MCP tool 카탈로그는 등록 전에 결정론적으로 정렬되므로,
  업스트림 `listTools()` 순서 변경이 prompt-cache tool 블록을 불필요하게 흔들지 않습니다

##### 전송 방식

MCP 서버는 stdio 또는 HTTP 전송을 사용할 수 있습니다:

**Stdio**는 자식 프로세스를 실행합니다:

```json
{
  "mcp": {
    "servers": {
      "my-server": {
        "command": "node",
        "args": ["server.js"],
        "env": { "PORT": "3000" }
      }
    }
  }
}
```

**HTTP**는 기본적으로 `sse`를 통해 실행 중인 MCP 서버에 연결하며, 요청된 경우 `streamable-http`를 사용합니다:

```json
{
  "mcp": {
    "servers": {
      "my-server": {
        "url": "http://localhost:3100/mcp",
        "transport": "streamable-http",
        "headers": {
          "Authorization": "Bearer ${MY_SECRET_TOKEN}"
        },
        "connectionTimeoutMs": 30000
      }
    }
  }
}
```

- `transport`는 `"streamable-http"` 또는 `"sse"`로 설정할 수 있으며, 생략하면 OpenClaw는 `sse`를 사용합니다
- `http:` 및 `https:` URL 스킴만 허용됩니다
- `headers` 값은 `${ENV_VAR}` 보간을 지원합니다
- `command`와 `url`을 모두 가진 서버 항목은 거부됩니다
- URL 자격 증명(userinfo 및 쿼리 파라미터)은 tool
  설명과 로그에서 마스킹됩니다
- `connectionTimeoutMs`는
  stdio 및 HTTP 전송 모두의 기본 30초 연결 시간 초과를 재정의합니다

##### Tool 이름 지정

OpenClaw는 bundle MCP tools를
`serverName__toolName` 형식의 provider-safe 이름으로 등록합니다. 예를 들어, `"vigil-harbor"`라는 키의 서버가
`memory_search` tool을 노출하면 `vigil-harbor__memory_search`로 등록됩니다.

- `A-Za-z0-9_-` 외의 문자는 `-`로 대체됩니다
- 서버 접두사는 최대 30자로 제한됩니다
- 전체 tool 이름은 최대 64자로 제한됩니다
- 빈 서버 이름은 `mcp`로 대체됩니다
- 정규화 후 이름이 충돌하면 숫자 접미사로 구분됩니다
- 최종 노출되는 tool 순서는 safe name 기준으로 결정론적으로 정렬되어 반복되는 Pi
  턴의 캐시 안정성을 유지합니다

#### 내장 Pi 설정

- Claude `settings.json`은 bundle이 활성화되면 기본 내장 Pi 설정으로 가져와집니다
- OpenClaw는 적용 전에 shell override 키를 정리합니다

정리되는 키:

- `shellPath`
- `shellCommandPrefix`

#### 내장 Pi LSP

- 활성화된 Claude bundles는 LSP 서버 config를 제공할 수 있습니다
- OpenClaw는 `.lsp.json`과 manifest에 선언된 모든 `lspServers` 경로를 로드합니다
- bundle LSP config는 유효한 내장 Pi LSP 기본값에 병합됩니다
- 현재 실행 가능한 것은 지원되는 stdio 기반 LSP 서버뿐이며, 지원되지 않는
  전송은 여전히 `openclaw plugins inspect <id>`에 표시됩니다

### 감지되지만 실행되지는 않음

다음 항목은 인식되어 진단에는 표시되지만, OpenClaw는 실행하지 않습니다:

- Claude `agents`, `hooks.json` 자동화, `outputStyles`
- Cursor `.cursor/agents`, `.cursor/hooks.json`, `.cursor/rules`
- 기능 보고를 넘어서는 Codex 인라인/app 메타데이터

## Bundle 형식

<AccordionGroup>
  <Accordion title="Codex bundles">
    마커: `.codex-plugin/plugin.json`

    선택적 콘텐츠: `skills/`, `hooks/`, `.mcp.json`, `.app.json`

    Codex bundles는 skill 루트와 OpenClaw 스타일
    hook-pack 디렉터리(`HOOK.md` + `handler.ts`)를 사용할 때 OpenClaw와 가장 잘 맞습니다.

  </Accordion>

  <Accordion title="Claude bundles">
    두 가지 감지 모드:

    - **Manifest 기반:** `.claude-plugin/plugin.json`
    - **Manifest 없음:** 기본 Claude 레이아웃 (`skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json`, `.lsp.json`, `settings.json`)

    Claude 전용 동작:

    - `commands/`는 skill 콘텐츠로 처리됩니다
    - `settings.json`은 내장 Pi 설정으로 가져와집니다(shell override 키는 정리됨)
    - `.mcp.json`은 지원되는 stdio tools를 내장 Pi에 노출합니다
    - `.lsp.json`과 manifest에 선언된 `lspServers` 경로는 내장 Pi LSP 기본값으로 로드됩니다
    - `hooks/hooks.json`은 감지만 되며 실행되지는 않습니다
    - manifest의 사용자 지정 component 경로는 추가 방식입니다(기본값을 대체하지 않고 확장함)

  </Accordion>

  <Accordion title="Cursor bundles">
    마커: `.cursor-plugin/plugin.json`

    선택적 콘텐츠: `skills/`, `.cursor/commands/`, `.cursor/agents/`, `.cursor/rules/`, `.cursor/hooks.json`, `.mcp.json`

    - `.cursor/commands/`는 skill 콘텐츠로 처리됩니다
    - `.cursor/rules/`, `.cursor/agents/`, `.cursor/hooks.json`은 감지 전용입니다

  </Accordion>
</AccordionGroup>

## 감지 우선순위

OpenClaw는 먼저 네이티브 plugin 형식을 확인합니다:

1. `openclaw.plugin.json` 또는 `openclaw.extensions`가 있는 유효한 `package.json` — **네이티브 plugin**으로 처리
2. Bundle 마커(`.codex-plugin/`, `.claude-plugin/`, 또는 기본 Claude/Cursor 레이아웃) — **bundle**로 처리

디렉터리에 둘 다 존재하면 OpenClaw는 네이티브 경로를 사용합니다. 이는
이중 형식 패키지가 부분적으로 bundle로 설치되는 일을 방지합니다.

## 보안

Bundles는 네이티브 plugins보다 더 좁은 신뢰 경계를 가집니다:

- OpenClaw는 임의의 bundle 런타임 모듈을 인프로세스로 로드하지 않습니다
- Skills 및 hook-pack 경로는 plugin 루트 내부에 있어야 합니다(경계 검사됨)
- Settings 파일도 동일한 경계 검사로 읽습니다
- 지원되는 stdio MCP 서버는 하위 프로세스로 실행될 수 있습니다

이로 인해 bundles는 기본적으로 더 안전하지만, 그래도 노출하는 기능에 대해서는
서드파티 bundles를 신뢰된 콘텐츠로 취급해야 합니다.

## 문제 해결

<AccordionGroup>
  <Accordion title="Bundle은 감지되지만 기능이 실행되지 않음">
    `openclaw plugins inspect <id>`를 실행하세요. 기능이 나열되어 있지만
    연결되지 않은 것으로 표시된다면, 이는 제품의 제한이지 설치 오류가 아닙니다.
  </Accordion>

  <Accordion title="Claude 명령 파일이 나타나지 않음">
    bundle이 활성화되어 있고 markdown 파일이 감지된
    `commands/` 또는 `skills/` 루트 안에 있는지 확인하세요.
  </Accordion>

  <Accordion title="Claude settings가 적용되지 않음">
    `settings.json`의 내장 Pi 설정만 지원됩니다. OpenClaw는
    bundle settings를 원시 config 패치로 취급하지 않습니다.
  </Accordion>

  <Accordion title="Claude hooks가 실행되지 않음">
    `hooks/hooks.json`은 감지 전용입니다. 실행 가능한 hooks가 필요하면
    OpenClaw hook-pack 레이아웃을 사용하거나 네이티브 plugin을 제공하세요.
  </Accordion>
</AccordionGroup>

## 관련 항목

- [Plugins 설치 및 구성](/tools/plugin)
- [Plugins 빌드](/plugins/building-plugins) — 네이티브 plugin 만들기
- [Plugin Manifest](/plugins/manifest) — 네이티브 manifest 스키마
