---
read_when:
    - 플러그인을 설치하거나 구성하는 경우
    - 플러그인 검색 및 로드 규칙을 이해하려는 경우
    - Codex/Claude 호환 플러그인 번들을 다루는 경우
sidebarTitle: Install and Configure
summary: OpenClaw 플러그인 설치, 구성 및 관리
title: 플러그인
x-i18n:
    generated_at: "2026-04-05T12:58:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 707bd3625596f290322aeac9fecb7f4c6f45d595fdfb82ded7cbc8e04457ac7f
    source_path: tools/plugin.md
    workflow: 15
---

# 플러그인

플러그인은 새로운 기능으로 OpenClaw를 확장합니다: 채널, 모델 프로바이더,
도구, Skills, 음성, 실시간 전사, 실시간 음성,
미디어 이해, 이미지 생성, 비디오 생성, 웹 fetch, 웹
검색 등. 일부 플러그인은 **코어**(OpenClaw와 함께 제공)이고, 다른 일부는
**외부**(커뮤니티가 npm에 게시)입니다.

## 빠른 시작

<Steps>
  <Step title="로드된 항목 보기">
    ```bash
    openclaw plugins list
    ```
  </Step>

  <Step title="플러그인 설치">
    ```bash
    # npm에서
    openclaw plugins install @openclaw/voice-call

    # 로컬 디렉터리 또는 아카이브에서
    openclaw plugins install ./my-plugin
    openclaw plugins install ./my-plugin.tgz
    ```

  </Step>

  <Step title="Gateway 재시작">
    ```bash
    openclaw gateway restart
    ```

    그런 다음 config 파일에서 `plugins.entries.\<id\>.config` 아래에 구성하세요.

  </Step>
</Steps>

채팅 네이티브 제어를 선호한다면 `commands.plugins: true`를 활성화하고 다음을 사용하세요:

```text
/plugin install clawhub:@openclaw/voice-call
/plugin show voice-call
/plugin enable voice-call
```

설치 경로는 CLI와 동일한 해결기를 사용합니다: 로컬 경로/아카이브, 명시적
`clawhub:<pkg>`, 또는 일반 패키지 사양(먼저 ClawHub, 그다음 npm 폴백).

config가 유효하지 않으면 설치는 일반적으로 실패 시 닫히며
`openclaw doctor --fix`를 가리킵니다. 유일한 복구 예외는
`openclaw.install.allowInvalidConfigRecovery`에 opt-in한 플러그인을 위한
좁은 범위의 번들 플러그인 재설치 경로입니다.

## 플러그인 유형

OpenClaw는 두 가지 플러그인 형식을 인식합니다:

| 형식       | 동작 방식                                                       | 예시                                                   |
| ---------- | --------------------------------------------------------------- | ------------------------------------------------------ |
| **네이티브** | `openclaw.plugin.json` + 런타임 모듈; 프로세스 내부에서 실행       | 공식 플러그인, 커뮤니티 npm 패키지                     |
| **번들**   | Codex/Claude/Cursor 호환 레이아웃; OpenClaw 기능으로 매핑됨      | `.codex-plugin/`, `.claude-plugin/`, `.cursor-plugin/` |

둘 다 `openclaw plugins list`에 표시됩니다. 번들에 대한 자세한 내용은 [플러그인 번들](/ko/plugins/bundles)을 참고하세요.

네이티브 플러그인을 작성하는 경우 [플러그인 만들기](/ko/plugins/building-plugins)
및 [Plugin SDK 개요](/plugins/sdk-overview)부터 시작하세요.

## 공식 플러그인

### 설치 가능(npm)

| 플러그인         | 패키지                | 문서                                 |
| --------------- | ---------------------- | ------------------------------------ |
| Matrix          | `@openclaw/matrix`     | [Matrix](/ko/channels/matrix)           |
| Microsoft Teams | `@openclaw/msteams`    | [Microsoft Teams](/ko/channels/msteams) |
| Nostr           | `@openclaw/nostr`      | [Nostr](/ko/channels/nostr)             |
| Voice Call      | `@openclaw/voice-call` | [Voice Call](/ko/plugins/voice-call)    |
| Zalo            | `@openclaw/zalo`       | [Zalo](/ko/channels/zalo)               |
| Zalo Personal   | `@openclaw/zalouser`   | [Zalo Personal](/ko/plugins/zalouser)   |

### 코어(OpenClaw와 함께 제공)

<AccordionGroup>
  <Accordion title="모델 프로바이더(기본적으로 활성화)">
    `anthropic`, `byteplus`, `cloudflare-ai-gateway`, `github-copilot`, `google`,
    `huggingface`, `kilocode`, `kimi-coding`, `minimax`, `mistral`, `qwen`,
    `moonshot`, `nvidia`, `openai`, `opencode`, `opencode-go`, `openrouter`,
    `qianfan`, `synthetic`, `together`, `venice`,
    `vercel-ai-gateway`, `volcengine`, `xiaomi`, `zai`
  </Accordion>

  <Accordion title="메모리 플러그인">
    - `memory-core` — 번들 메모리 검색(`plugins.slots.memory`를 통한 기본값)
    - `memory-lancedb` — 자동 리콜/캡처가 포함된 주문형 설치 장기 메모리(`plugins.slots.memory = "memory-lancedb"`로 설정)
  </Accordion>

  <Accordion title="음성 프로바이더(기본적으로 활성화)">
    `elevenlabs`, `microsoft`
  </Accordion>

  <Accordion title="기타">
    - `browser` — 브라우저 도구, `openclaw browser` CLI, `browser.request` gateway 메서드, 브라우저 런타임, 기본 브라우저 제어 서비스를 위한 번들 browser 플러그인(기본적으로 활성화됨; 교체하기 전에 비활성화하세요)
    - `copilot-proxy` — VS Code Copilot Proxy 브리지(기본적으로 비활성화)
  </Accordion>
</AccordionGroup>

서드파티 플러그인을 찾고 있나요? [커뮤니티 플러그인](/ko/plugins/community)을 참고하세요.

## 구성

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: ["untrusted-plugin"],
    load: { paths: ["~/Projects/oss/voice-call-extension"] },
    entries: {
      "voice-call": { enabled: true, config: { provider: "twilio" } },
    },
  },
}
```

| 필드             | 설명                                                      |
| ---------------- | --------------------------------------------------------- |
| `enabled`        | 마스터 토글(기본값: `true`)                               |
| `allow`          | 플러그인 allowlist(선택 사항)                             |
| `deny`           | 플러그인 denylist(선택 사항, deny가 우선)                 |
| `load.paths`     | 추가 플러그인 파일/디렉터리                               |
| `slots`          | 배타적 슬롯 선택기(예: `memory`, `contextEngine`)         |
| `entries.\<id\>` | 플러그인별 토글 + config                                  |

config 변경에는 **Gateway 재시작이 필요합니다**. Gateway가 config 감시 + 프로세스 내부 재시작을 활성화한 상태(기본 `openclaw gateway` 경로)로 실행 중이면, 해당 재시작은 보통 config 쓰기가 완료된 직후 자동으로 수행됩니다.

<Accordion title="플러그인 상태: 비활성화 vs 누락 vs 유효하지 않음">
  - **비활성화됨**: 플러그인은 존재하지만 활성화 규칙에 의해 꺼져 있습니다. config는 유지됩니다.
  - **누락됨**: config가 플러그인 id를 참조하지만 검색에서 찾지 못했습니다.
  - **유효하지 않음**: 플러그인은 존재하지만 해당 config가 선언된 스키마와 일치하지 않습니다.
</Accordion>

## 검색 및 우선순위

OpenClaw는 다음 순서로 플러그인을 검사합니다(첫 번째 일치 항목이 우선):

<Steps>
  <Step title="Config 경로">
    `plugins.load.paths` — 명시적 파일 또는 디렉터리 경로.
  </Step>

  <Step title="워크스페이스 확장">
    `\<workspace\>/.openclaw/<plugin-root>/*.ts` 및 `\<workspace\>/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="전역 확장">
    `~/.openclaw/<plugin-root>/*.ts` 및 `~/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="번들 플러그인">
    OpenClaw와 함께 제공됩니다. 많은 항목이 기본적으로 활성화됩니다(모델 프로바이더, 음성 등).
    그 외에는 명시적으로 활성화해야 합니다.
  </Step>
</Steps>

### 활성화 규칙

- `plugins.enabled: false`는 모든 플러그인을 비활성화합니다
- `plugins.deny`는 항상 allow보다 우선합니다
- `plugins.entries.\<id\>.enabled: false`는 해당 플러그인을 비활성화합니다
- 워크스페이스 출처 플러그인은 **기본적으로 비활성화**됩니다(명시적으로 활성화해야 함)
- 번들 플러그인은 재정의되지 않는 한 내장 기본 활성 세트를 따릅니다
- 배타적 슬롯은 해당 슬롯에 선택된 플러그인을 강제로 활성화할 수 있습니다

## 플러그인 슬롯(배타적 범주)

일부 범주는 배타적입니다(한 번에 하나만 활성):

```json5
{
  plugins: {
    slots: {
      memory: "memory-core", // 또는 비활성화하려면 "none"
      contextEngine: "legacy", // 또는 플러그인 id
    },
  },
}
```

| 슬롯            | 제어 대상              | 기본값             |
| --------------- | --------------------- | ------------------ |
| `memory`        | 활성 메모리 플러그인   | `memory-core`      |
| `contextEngine` | 활성 컨텍스트 엔진     | `legacy`(내장)     |

## CLI 참조

```bash
openclaw plugins list                       # 간단한 인벤토리
openclaw plugins list --enabled            # 로드된 플러그인만
openclaw plugins list --verbose            # 플러그인별 상세 줄
openclaw plugins list --json               # 기계가 읽을 수 있는 인벤토리
openclaw plugins inspect <id>              # 상세 정보
openclaw plugins inspect <id> --json       # 기계가 읽을 수 있는 형식
openclaw plugins inspect --all             # 전체 테이블
openclaw plugins info <id>                 # inspect 별칭
openclaw plugins doctor                    # 진단

openclaw plugins install <package>         # 설치(먼저 ClawHub, 그다음 npm)
openclaw plugins install clawhub:<pkg>     # ClawHub에서만 설치
openclaw plugins install <spec> --force    # 기존 설치 덮어쓰기
openclaw plugins install <path>            # 로컬 경로에서 설치
openclaw plugins install -l <path>         # 개발용 링크(복사 없음)
openclaw plugins install <plugin> --marketplace <source>
openclaw plugins install <plugin> --marketplace https://github.com/<owner>/<repo>
openclaw plugins install <spec> --pin      # 정확히 해결된 npm 사양 기록
openclaw plugins install <spec> --dangerously-force-unsafe-install
openclaw plugins update <id>             # 플러그인 하나 업데이트
openclaw plugins update <id> --dangerously-force-unsafe-install
openclaw plugins update --all            # 모두 업데이트
openclaw plugins uninstall <id>          # config/설치 기록 제거
openclaw plugins uninstall <id> --keep-files
openclaw plugins marketplace list <source>
openclaw plugins marketplace list <source> --json

openclaw plugins enable <id>
openclaw plugins disable <id>
```

번들 플러그인은 OpenClaw와 함께 제공됩니다. 많은 항목이 기본적으로 활성화됩니다(예:
번들 모델 프로바이더, 번들 음성 프로바이더, 번들 browser
플러그인). 다른 번들 플러그인은 여전히 `openclaw plugins enable <id>`가 필요합니다.

`--force`는 기존에 설치된 플러그인 또는 hook pack을 제자리에서 덮어씁니다.
소스 경로를 재사용하고 관리되는 설치 대상을 덮어쓰지 않는 `--link`와는
함께 지원되지 않습니다.

`--pin`은 npm 전용입니다. marketplace 설치는 npm 사양 대신
marketplace 소스 메타데이터를 유지하므로 `--marketplace`와 함께 지원되지 않습니다.

`--dangerously-force-unsafe-install`은 내장 위험 코드 스캐너의 오탐에 대한 비상
재정의입니다. 플러그인 설치 및 플러그인 업데이트가 내장 `critical` 결과를 넘어서 계속 진행되도록 허용하지만,
플러그인 `before_install` 정책 차단이나 스캔 실패 차단까지 우회하지는 않습니다.

이 CLI 플래그는 플러그인 설치/업데이트 흐름에만 적용됩니다. Gateway 기반 Skills
의존성 설치는 대신 일치하는 `dangerouslyForceUnsafeInstall` 요청 재정의를 사용하며,
`openclaw skills install`은 별도의 ClawHub Skills 다운로드/설치 흐름으로 유지됩니다.

호환 번들은 동일한 플러그인 목록/검사/활성화/비활성화 흐름에 참여합니다.
현재 런타임 지원에는 번들 Skills, Claude command-skills,
Claude `settings.json` 기본값, Claude `.lsp.json` 및 매니페스트에 선언된
`lspServers` 기본값, Cursor command-skills, 호환되는 Codex hook
디렉터리가 포함됩니다.

`openclaw plugins inspect <id>`는 감지된 번들 기능과 함께,
번들 기반 플러그인에 대해 지원되는 MCP 및 LSP 서버 항목과 지원되지 않는 항목도 보고합니다.

Marketplace 소스는
`~/.claude/plugins/known_marketplaces.json`의 Claude known-marketplace 이름,
로컬 marketplace 루트 또는 `marketplace.json` 경로, `owner/repo` 같은 GitHub 축약형, GitHub 저장소
URL 또는 git URL일 수 있습니다. 원격 marketplace의 경우 플러그인 항목은
클론된 marketplace 저장소 내부에 있어야 하며 상대 경로 소스만 사용해야 합니다.

전체 세부 정보는 [`openclaw plugins` CLI 참조](/cli/plugins)를 참고하세요.

## 플러그인 API 개요

네이티브 플러그인은 `register(api)`를 노출하는 엔트리 객체를 export합니다. 이전
플러그인은 레거시 별칭으로 `activate(api)`를 여전히 사용할 수 있지만, 새 플러그인은
`register`를 사용해야 합니다.

```typescript
export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
    api.registerChannel({
      /* ... */
    });
  },
});
```

OpenClaw는 엔트리 객체를 로드하고 플러그인
활성화 중 `register(api)`를 호출합니다. 로더는 여전히 이전 플러그인을 위해
`activate(api)`로 폴백하지만, 번들 플러그인과 새로운 외부 플러그인은
`register`를 공개 계약으로 취급해야 합니다.

일반적인 등록 메서드:

| 메서드                                  | 등록하는 항목               |
| --------------------------------------- | --------------------------- |
| `registerProvider`                      | 모델 프로바이더(LLM)        |
| `registerChannel`                       | 채팅 채널                   |
| `registerTool`                          | 에이전트 도구               |
| `registerHook` / `on(...)`              | 수명 주기 hook              |
| `registerSpeechProvider`                | 텍스트 음성 변환 / STT      |
| `registerRealtimeTranscriptionProvider` | 스트리밍 STT                |
| `registerRealtimeVoiceProvider`         | 양방향 실시간 음성          |
| `registerMediaUnderstandingProvider`    | 이미지/오디오 분석          |
| `registerImageGenerationProvider`       | 이미지 생성                 |
| `registerVideoGenerationProvider`       | 비디오 생성                 |
| `registerWebFetchProvider`              | 웹 fetch / 스크래핑 프로바이더 |
| `registerWebSearchProvider`             | 웹 검색                     |
| `registerHttpRoute`                     | HTTP 엔드포인트             |
| `registerCommand` / `registerCli`       | CLI 명령                    |
| `registerContextEngine`                 | 컨텍스트 엔진               |
| `registerService`                       | 백그라운드 서비스           |

타입 지정 수명 주기 hook의 가드 동작:

- `before_tool_call`: `{ block: true }`는 최종 결정이며, 더 낮은 우선순위 핸들러는 건너뜁니다.
- `before_tool_call`: `{ block: false }`는 no-op이며 이전 block을 해제하지 않습니다.
- `before_install`: `{ block: true }`는 최종 결정이며, 더 낮은 우선순위 핸들러는 건너뜁니다.
- `before_install`: `{ block: false }`는 no-op이며 이전 block을 해제하지 않습니다.
- `message_sending`: `{ cancel: true }`는 최종 결정이며, 더 낮은 우선순위 핸들러는 건너뜁니다.
- `message_sending`: `{ cancel: false }`는 no-op이며 이전 cancel을 해제하지 않습니다.

전체 타입 지정 hook 동작은 [SDK 개요](/plugins/sdk-overview#hook-decision-semantics)를 참고하세요.

## 관련

- [플러그인 만들기](/ko/plugins/building-plugins) — 직접 플러그인 만들기
- [플러그인 번들](/ko/plugins/bundles) — Codex/Claude/Cursor 번들 호환성
- [플러그인 매니페스트](/ko/plugins/manifest) — 매니페스트 스키마
- [도구 등록하기](/ko/plugins/building-plugins#registering-agent-tools) — 플러그인에 에이전트 도구 추가
- [플러그인 내부 구조](/plugins/architecture) — 기능 모델과 로드 파이프라인
- [커뮤니티 플러그인](/ko/plugins/community) — 서드파티 목록
