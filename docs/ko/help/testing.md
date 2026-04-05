---
read_when:
    - 로컬 또는 CI에서 테스트를 실행할 때
    - 모델/provider 버그에 대한 회귀 테스트를 추가할 때
    - gateway + agent 동작을 디버깅할 때
summary: '테스트 키트: unit/e2e/live 스위트, Docker 실행기, 그리고 각 테스트가 무엇을 다루는지'
title: 테스트
x-i18n:
    generated_at: "2026-04-05T12:46:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 854a39ae261d8749b8d8d82097b97a7c52cf2216d1fe622e302d830a888866ab
    source_path: help/testing.md
    workflow: 15
---

# 테스트

OpenClaw에는 세 가지 Vitest 스위트(unit/integration, e2e, live)와 소규모 Docker 실행기 세트가 있습니다.

이 문서는 “OpenClaw가 어떻게 테스트되는지”에 대한 가이드입니다:

- 각 스위트가 무엇을 다루는지(그리고 의도적으로 _무엇을 다루지 않는지_)
- 일반적인 워크플로(로컬, push 전, 디버깅)에 어떤 명령을 실행해야 하는지
- live 테스트가 자격 증명을 어떻게 찾고 모델/provider를 어떻게 선택하는지
- 실제 모델/provider 문제에 대한 회귀 테스트를 어떻게 추가하는지

## 빠른 시작

대부분의 날에는 다음이면 충분합니다:

- 전체 게이트(push 전에 기대되는 기준): `pnpm build && pnpm check && pnpm test`
- 여유 있는 머신에서 더 빠른 로컬 전체 스위트 실행: `pnpm test:max`
- 직접 Vitest watch 루프(현대식 projects config): `pnpm test:watch`
- 직접 파일 타기팅은 이제 extension/channel 경로도 라우팅합니다: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`

테스트를 수정했거나 추가 신뢰가 필요할 때:

- 커버리지 게이트: `pnpm test:coverage`
- E2E 스위트: `pnpm test:e2e`

실제 provider/모델을 디버깅할 때(실제 자격 증명 필요):

- Live 스위트(모델 + gateway tool/image probe): `pnpm test:live`
- 하나의 live 파일만 조용히 타기팅: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

팁: 하나의 실패 사례만 필요하다면 아래 설명된 allowlist env var를 사용해 live 테스트 범위를 좁히는 것이 좋습니다.

## 테스트 스위트(무엇이 어디서 실행되는가)

스위트를 “현실성이 점점 높아지고” 그에 따라 “불안정성/비용도 점점 높아지는” 것으로 생각하세요.

### Unit / integration(기본값)

- 명령: `pnpm test`
- config: `vitest.config.ts`를 통한 native Vitest `projects`
- 파일: `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` 아래의 core/unit 인벤토리와 `vitest.unit.config.ts`에서 다루는 허용된 `ui` node 테스트
- 범위:
  - 순수 unit 테스트
  - 인프로세스 integration 테스트(gateway 인증, 라우팅, 도구, 파싱, config)
  - 알려진 버그에 대한 결정적 회귀 테스트
- 기대 사항:
  - CI에서 실행됨
  - 실제 키 불필요
  - 빠르고 안정적이어야 함
- Projects 참고:
  - `pnpm test`, `pnpm test:watch`, `pnpm test:changed`는 이제 모두 동일한 native Vitest 루트 `projects` config를 사용합니다.
  - 직접 파일 필터도 루트 project 그래프를 통해 네이티브하게 라우팅되므로 `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`가 사용자 지정 래퍼 없이 동작합니다.
- Embedded runner 참고:
  - 메시지 도구 검색 입력이나 압축 런타임 컨텍스트를 변경할 때는 두 수준의 커버리지를 모두 유지하세요.
  - 순수 라우팅/정규화 경계를 위한 집중된 helper 회귀 테스트를 추가하세요.
  - 또한 embedded runner integration 스위트도 건강하게 유지하세요:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`, 및
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - 이 스위트들은 범위 지정된 id와 압축 동작이 실제 `run.ts` / `compact.ts` 경로를 통해 여전히 흐르는지 검증합니다. helper 전용 테스트만으로는 이러한 integration 경로를 충분히 대체할 수 없습니다.
- Pool 참고:
  - 기본 Vitest config는 이제 `threads`를 기본값으로 사용합니다.
  - 공유 Vitest config는 또한 `isolate: false`를 고정하고 루트 projects, e2e, live config 전반에서 비격리 runner를 사용합니다.
  - 루트 UI 레인은 여전히 자체 `jsdom` 설정과 optimizer를 유지하지만, 이제 공유 비격리 runner에서도 실행됩니다.
  - `pnpm test`는 루트 `vitest.config.ts` projects config에서 동일한 `threads` + `isolate: false` 기본값을 상속합니다.
  - 공유 `scripts/run-vitest.mjs` 실행기는 이제 큰 로컬 실행 중 V8 컴파일 churn을 줄이기 위해 기본적으로 Vitest child Node 프로세스에 `--no-maglev`도 추가합니다. 기본 V8 동작과 비교해야 한다면 `OPENCLAW_VITEST_ENABLE_MAGLEV=1`을 설정하세요.
- 빠른 로컬 반복 참고:
  - `pnpm test:changed`는 native projects config를 `--changed origin/main`과 함께 실행합니다.
  - `pnpm test:max` 및 `pnpm test:changed:max`는 동일한 native projects config를 유지하되 더 높은 worker cap만 사용합니다.
  - 로컬 worker 자동 스케일링은 이제 의도적으로 보수적이며, 호스트 load average가 이미 높을 때도 물러나도록 되어 있으므로 여러 개의 동시 Vitest 실행이 기본적으로 덜 큰 피해를 줍니다.
  - 기본 Vitest config는 projects/config 파일을 `forceRerunTriggers`로 표시하여 테스트 wiring이 바뀔 때 changed-mode 재실행이 올바르게 유지되도록 합니다.
  - config는 지원되는 호스트에서 `OPENCLAW_VITEST_FS_MODULE_CACHE`를 활성화한 상태로 유지합니다. 직접 프로파일링을 위해 명시적 캐시 위치 하나를 사용하고 싶다면 `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path`를 설정하세요.
- 성능 디버그 참고:
  - `pnpm test:perf:imports`는 Vitest import-duration 보고와 import-breakdown 출력을 활성화합니다.
  - `pnpm test:perf:imports:changed`는 동일한 프로파일링 보기를 `origin/main` 이후 변경된 파일로 제한합니다.
  - `pnpm test:perf:profile:main`은 Vitest/Vite 시작 및 transform 오버헤드에 대한 메인 스레드 CPU 프로파일을 기록합니다.
  - `pnpm test:perf:profile:runner`는 unit 스위트에 대해 파일 병렬화를 비활성화한 상태로 runner CPU+heap 프로파일을 기록합니다.

### E2E(gateway 스모크)

- 명령: `pnpm test:e2e`
- config: `vitest.e2e.config.ts`
- 파일: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- 런타임 기본값:
  - 나머지 저장소와 마찬가지로 Vitest `threads`와 `isolate: false`를 사용합니다.
  - 적응형 workers 사용(CI: 최대 2, 로컬: 기본 1).
  - 콘솔 I/O 오버헤드를 줄이기 위해 기본적으로 silent mode로 실행됩니다.
- 유용한 재정의:
  - worker 수를 강제로 지정하려면 `OPENCLAW_E2E_WORKERS=<n>`(최대 16).
  - 자세한 콘솔 출력을 다시 활성화하려면 `OPENCLAW_E2E_VERBOSE=1`.
- 범위:
  - 다중 인스턴스 gateway 종단간 동작
  - WebSocket/HTTP 표면, 노드 페어링, 더 무거운 네트워킹
- 기대 사항:
  - 활성화된 파이프라인에서는 CI에서 실행됨
  - 실제 키 불필요
  - unit 테스트보다 움직이는 부품이 많음(더 느릴 수 있음)

### E2E: OpenShell backend 스모크

- 명령: `pnpm test:e2e:openshell`
- 파일: `test/openshell-sandbox.e2e.test.ts`
- 범위:
  - Docker를 통해 호스트에서 격리된 OpenShell gateway를 시작
  - 임시 로컬 Dockerfile에서 sandbox 생성
  - 실제 `sandbox ssh-config` + SSH exec를 통해 OpenClaw의 OpenShell backend를 실행
  - sandbox fs bridge를 통한 원격 정규 파일 시스템 동작 검증
- 기대 사항:
  - 옵트인 전용이며 기본 `pnpm test:e2e` 실행에는 포함되지 않음
  - 로컬 `openshell` CLI 및 동작하는 Docker daemon 필요
  - 격리된 `HOME` / `XDG_CONFIG_HOME` 사용 후 테스트 gateway와 sandbox를 제거
- 유용한 재정의:
  - 더 넓은 e2e 스위트를 수동 실행할 때 테스트를 활성화하려면 `OPENCLAW_E2E_OPENSHELL=1`
  - 기본값이 아닌 CLI 바이너리나 래퍼 스크립트를 지정하려면 `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`

### Live(실제 provider + 실제 모델)

- 명령: `pnpm test:live`
- config: `vitest.live.config.ts`
- 파일: `src/**/*.live.test.ts`
- 기본값: `pnpm test:live`로 **활성화됨** (`OPENCLAW_LIVE_TEST=1` 설정)
- 범위:
  - “이 provider/모델이 _오늘_ 실제 자격 증명으로 실제로 동작하는가?”
  - provider 포맷 변경, tool-calling 특이점, 인증 문제, 속도 제한 동작 포착
- 기대 사항:
  - 설계상 CI에서 안정적이지 않음(실제 네트워크, 실제 provider 정책, quota, 장애)
  - 비용이 들고 속도 제한을 소모함
  - “전부”보다 범위를 좁힌 부분집합 실행을 선호
- Live 실행은 누락된 API 키를 가져오기 위해 `~/.profile`을 source합니다.
- 기본적으로 live 실행도 여전히 `HOME`을 격리하고 config/auth 자료를 임시 테스트 home으로 복사하므로 unit 픽스처가 실제 `~/.openclaw`를 변경할 수 없습니다.
- live 테스트가 실제 홈 디렉터리를 사용해야 하는 경우에만 `OPENCLAW_LIVE_USE_REAL_HOME=1`을 설정하세요.
- `pnpm test:live`는 이제 더 조용한 모드를 기본값으로 사용합니다. `[live] ...` 진행 출력은 유지하지만 추가 `~/.profile` 알림과 gateway bootstrap 로그/Bonjour chatter는 억제합니다. 전체 시작 로그가 필요하면 `OPENCLAW_LIVE_TEST_QUIET=0`을 설정하세요.
- API 키 교체(provider별): 쉼표/세미콜론 형식의 `*_API_KEYS` 또는 `*_API_KEY_1`, `*_API_KEY_2`(예: `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`)를 설정하거나, live 전용 재정의로 `OPENCLAW_LIVE_*_KEY`를 사용하세요. 테스트는 rate limit 응답 시 재시도합니다.
- 진행/heartbeat 출력:
  - Live 스위트는 이제 긴 provider 호출이 Vitest 콘솔 캡처가 조용한 상황에서도 눈에 보이도록 stderr에 진행 줄을 출력합니다.
  - `vitest.live.config.ts`는 Vitest 콘솔 가로채기를 비활성화하여 live 실행 중 provider/gateway 진행 줄이 즉시 스트리밍되도록 합니다.
  - 직접 모델 heartbeat는 `OPENCLAW_LIVE_HEARTBEAT_MS`로 조정합니다.
  - gateway/probe heartbeat는 `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`로 조정합니다.

## 어떤 스위트를 실행해야 하나요?

다음 결정표를 사용하세요:

- 로직/테스트 편집: `pnpm test` 실행(많이 바꿨다면 `pnpm test:coverage`도)
- gateway 네트워킹 / WS 프로토콜 / 페어링 수정: `pnpm test:e2e` 추가
- “내 봇이 죽었다” / provider별 실패 / tool calling 디버깅: 범위를 좁힌 `pnpm test:live` 실행

## Live: Android node capability 스윕

- 테스트: `src/gateway/android-node.capabilities.live.test.ts`
- 스크립트: `pnpm android:test:integration`
- 목표: 연결된 Android node가 현재 광고하는 **모든 명령**을 호출하고 명령 계약 동작을 검증
- 범위:
  - 사전 조건/수동 설정 필요(스위트가 앱을 설치/실행/페어링하지는 않음)
  - 선택된 Android node에 대한 명령별 gateway `node.invoke` 검증
- 필요한 사전 설정:
  - Android 앱이 이미 gateway에 연결 + 페어링되어 있어야 함
  - 앱이 포그라운드 상태로 유지되어야 함
  - 통과를 기대하는 capability에 필요한 권한/캡처 동의가 부여되어야 함
- 선택적 대상 재정의:
  - `OPENCLAW_ANDROID_NODE_ID` 또는 `OPENCLAW_ANDROID_NODE_NAME`
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`
- 전체 Android 설정 세부 사항: [Android App](/platforms/android)

## Live: 모델 스모크(profile keys)

Live 테스트는 실패를 분리할 수 있도록 두 계층으로 나뉩니다:

- “Direct model”은 주어진 키로 provider/모델이 최소한 응답할 수 있는지 알려줍니다.
- “Gateway smoke”는 전체 gateway+agent 파이프라인이 해당 모델에서 동작하는지(세션, 기록, 도구, sandbox 정책 등) 알려줍니다.

### 계층 1: 직접 모델 completion(gateway 없음)

- 테스트: `src/agents/models.profiles.live.test.ts`
- 목표:
  - 발견된 모델 열거
  - `getApiKeyForModel`을 사용해 자격 증명이 있는 모델 선택
  - 모델별로 작은 completion 실행(필요 시 표적 회귀 포함)
- 활성화 방법:
  - `pnpm test:live`(또는 Vitest를 직접 호출하는 경우 `OPENCLAW_LIVE_TEST=1`)
- 이 스위트를 실제로 실행하려면 `OPENCLAW_LIVE_MODELS=modern`(또는 modern의 별칭인 `all`)을 설정하세요. 그렇지 않으면 `pnpm test:live`가 gateway 스모크에 집중되도록 건너뜁니다.
- 모델 선택 방법:
  - 현대적 allowlist를 실행하려면 `OPENCLAW_LIVE_MODELS=modern`(Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all`은 modern allowlist의 별칭
  - 또는 `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."`(쉼표 allowlist)
- provider 선택 방법:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`(쉼표 allowlist)
- 키의 출처:
  - 기본값: profile store와 env fallback
  - **profile store만** 강제하려면 `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`
- 존재 이유:
  - “provider API가 깨졌는가 / 키가 유효하지 않은가”와 “gateway agent 파이프라인이 깨졌는가”를 분리
  - 작고 고립된 회귀를 담음(예: OpenAI Responses/Codex Responses reasoning replay + tool-call 흐름)

### 계층 2: Gateway + 개발 agent 스모크(실제 "@openclaw"가 하는 일)

- 테스트: `src/gateway/gateway-models.profiles.live.test.ts`
- 목표:
  - 인프로세스 gateway 시작
  - `agent:dev:*` 세션 생성/패치(실행별 모델 재정의)
  - 키가 있는 모델을 순회하며 다음을 검증:
    - “의미 있는” 응답(도구 없음)
    - 실제 도구 호출이 동작함(read probe)
    - 선택적 추가 도구 probe(exec+read probe)
    - OpenAI 회귀 경로(tool-call-only → follow-up)가 계속 동작함
- Probe 세부 사항(실패를 빠르게 설명하기 위해):
  - `read` probe: 테스트가 워크스페이스에 nonce 파일을 쓰고, agent에게 이를 `read`해서 nonce를 다시 말하라고 요청합니다.
  - `exec+read` probe: 테스트가 agent에게 `exec`로 temp 파일에 nonce를 쓰고, 다시 `read`하게 요청합니다.
  - image probe: 테스트가 생성한 PNG(cat + randomized code)를 첨부하고 모델이 `cat <CODE>`를 반환하길 기대합니다.
  - 구현 참조: `src/gateway/gateway-models.profiles.live.test.ts` 및 `src/gateway/live-image-probe.ts`.
- 활성화 방법:
  - `pnpm test:live`(또는 Vitest를 직접 호출하는 경우 `OPENCLAW_LIVE_TEST=1`)
- 모델 선택 방법:
  - 기본값: modern allowlist(Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all`은 modern allowlist의 별칭
  - 또는 `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`(또는 쉼표 목록)로 범위 축소
- provider 선택 방법(“OpenRouter 전부” 방지):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"`(쉼표 allowlist)
- 도구 + image probe는 이 live 테스트에서 항상 활성화됨:
  - `read` probe + `exec+read` probe(도구 스트레스)
  - image probe는 모델이 image input 지원을 광고할 때 실행
  - 흐름(상위 수준):
    - 테스트가 “CAT” + 랜덤 코드를 가진 작은 PNG를 생성 (`src/gateway/live-image-probe.ts`)
    - 이를 `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]`로 전송
    - Gateway가 첨부 파일을 `images[]`로 파싱 (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - Embedded agent가 멀티모달 사용자 메시지를 모델로 전달
    - 검증: 응답에 `cat` + 코드가 포함됨(OCR 허용 오차: 약간의 오류는 허용)

팁: 현재 머신에서 무엇을 테스트할 수 있는지(그리고 정확한 `provider/model` id)를 보려면 다음을 실행하세요:

```bash
openclaw models list
openclaw models list --json
```

## Live: CLI backend 스모크(Claude CLI 또는 기타 로컬 CLI)

- 테스트: `src/gateway/gateway-cli-backend.live.test.ts`
- 목표: 기본 config를 건드리지 않고 로컬 CLI backend를 사용해 Gateway + agent 파이프라인 검증
- 활성화:
  - `pnpm test:live`(또는 Vitest를 직접 호출하는 경우 `OPENCLAW_LIVE_TEST=1`)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- 기본값:
  - 모델: `claude-cli/claude-sonnet-4-6`
  - 명령: `claude`
  - 인수: `["-p","--output-format","stream-json","--include-partial-messages","--verbose","--permission-mode","bypassPermissions"]`
- 재정의(선택 사항):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-opus-4-6"`
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/claude"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["-p","--output-format","stream-json","--include-partial-messages","--verbose","--permission-mode","bypassPermissions"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_CLEAR_ENV='["ANTHROPIC_API_KEY","ANTHROPIC_API_KEY_OLD"]'`
  - 실제 이미지 첨부 파일을 보내려면 `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1`(경로가 프롬프트에 주입됨)
  - 프롬프트 주입 대신 이미지 파일 경로를 CLI 인수로 전달하려면 `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`
  - `IMAGE_ARG`가 설정된 경우 이미지 인수 전달 방식을 제어하려면 `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"`(또는 `"list"`)
  - 두 번째 턴을 보내고 resume 흐름을 검증하려면 `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`
- Claude CLI MCP config를 활성 상태로 유지하려면 `OPENCLAW_LIVE_CLI_BACKEND_DISABLE_MCP_CONFIG=0`(기본값은 일시적인 엄격한 빈 `--mcp-config`를 주입하여 스모크 중 ambient/global MCP 서버를 비활성화)

예시:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-sonnet-4-6" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Docker 레시피:

```bash
pnpm test:docker:live-cli-backend
```

참고:

- Docker 실행기는 `scripts/test-live-cli-backend-docker.sh`에 있습니다.
- Claude CLI는 root로 실행될 때 `bypassPermissions`를 거부하므로, 저장소 Docker 이미지 안에서 비root `node` 사용자로 live CLI-backend 스모크를 실행합니다.
- `claude-cli`의 경우 Linux `@anthropic-ai/claude-code` 패키지를 `OPENCLAW_DOCKER_CLI_TOOLS_DIR`(기본값: `~/.cache/openclaw/docker-cli-tools`)의 캐시 가능한 쓰기 가능 prefix에 설치합니다.
- `claude-cli`의 경우 `OPENCLAW_LIVE_CLI_BACKEND_DISABLE_MCP_CONFIG=0`을 설정하지 않으면 live 스모크는 엄격한 빈 MCP config를 주입합니다.
- 가능하면 `~/.claude`를 컨테이너에 복사하지만, Claude 인증이 `ANTHROPIC_API_KEY` 기반인 머신에서는 child Claude CLI를 위해 `OPENCLAW_LIVE_CLI_BACKEND_PRESERVE_ENV`를 통해 `ANTHROPIC_API_KEY` / `ANTHROPIC_API_KEY_OLD`도 보존합니다.

## Live: ACP bind 스모크(`/acp spawn ... --bind here`)

- 테스트: `src/gateway/gateway-acp-bind.live.test.ts`
- 목표: live ACP agent로 실제 ACP 대화 바인드 흐름 검증:
  - `/acp spawn <agent> --bind here` 전송
  - synthetic message-channel 대화를 제자리에서 바인드
  - 같은 대화에서 일반 follow-up 전송
  - follow-up이 바인드된 ACP 세션 transcript에 들어가는지 검증
- 활성화:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- 기본값:
  - ACP agent: `claude`
  - synthetic channel: Slack DM 스타일 대화 컨텍스트
  - ACP backend: `acpx`
- 재정의:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=/full/path/to/acpx`
- 참고:
  - 이 레인은 테스트가 외부 전달을 가장하지 않고 message-channel 컨텍스트를 붙일 수 있도록 admin 전용 synthetic originating-route 필드와 함께 gateway `chat.send` 표면을 사용합니다.
  - `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND`이 설정되지 않으면 테스트는 구성된/번들 acpx 명령을 사용합니다. 하네스 인증이 `~/.profile`의 env var에 의존한다면, provider env를 보존하는 사용자 지정 `acpx` 명령을 선호하세요.

예시:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Docker 레시피:

```bash
pnpm test:docker:live-acp-bind
```

Docker 참고:

- Docker 실행기는 `scripts/test-live-acp-bind-docker.sh`에 있습니다.
- `~/.profile`을 source하고, 일치하는 CLI auth 홈(`~/.claude` 또는 `~/.codex`)을 컨테이너에 복사하며, `acpx`를 쓰기 가능한 npm prefix에 설치한 다음, 누락된 경우 요청된 live CLI(`@anthropic-ai/claude-code` 또는 `@openai/codex`)를 설치합니다.
- Docker 내부에서는 실행기가 `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx`를 설정하여 source된 profile의 provider env var가 child harness CLI에 계속 사용 가능하도록 합니다.

### 권장 live 레시피

범위가 좁고 명시적인 allowlist가 가장 빠르고 가장 덜 불안정합니다:

- 단일 모델, 직접 실행(gateway 없음):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- 단일 모델, gateway 스모크:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 여러 provider에 걸친 tool calling:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google 집중(Gemini API 키 + Antigravity):
  - Gemini(API 키): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity(OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

참고:

- `google/...`는 Gemini API(API 키)를 사용합니다.
- `google-antigravity/...`는 Antigravity OAuth 브리지(Cloud Code Assist 스타일 agent endpoint)를 사용합니다.
- `google-gemini-cli/...`는 사용자의 머신에 있는 로컬 Gemini CLI를 사용합니다(별도 인증 + 도구 특이점).
- Gemini API 대 Gemini CLI:
  - API: OpenClaw가 HTTP를 통해 Google의 호스팅된 Gemini API를 호출함(API 키 / profile 인증). 대부분의 사용자가 “Gemini”라고 할 때 뜻하는 것이 이것입니다.
  - CLI: OpenClaw가 로컬 `gemini` 바이너리를 셸로 실행함. 자체 인증을 가지며 동작이 다를 수 있습니다(스트리밍/도구 지원/버전 차이).

## Live: 모델 매트릭스(무엇을 다루는가)

고정된 “CI 모델 목록”은 없습니다(live는 옵트인). 하지만 실제 키가 있는 개발 머신에서 정기적으로 다루길 권장하는 모델은 다음과 같습니다.

### 현대적 스모크 세트(tool calling + image)

계속 동작해야 하는 것으로 기대하는 “일반 모델” 실행입니다:

- OpenAI(비-Codex): `openai/gpt-5.4` (선택 사항: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (또는 `anthropic/claude-sonnet-4-6`)
- Google(Gemini API): `google/gemini-3.1-pro-preview` 및 `google/gemini-3-flash-preview` (이전 Gemini 2.x 모델은 피하세요)
- Google(Antigravity): `google-antigravity/claude-opus-4-6-thinking` 및 `google-antigravity/gemini-3-flash`
- Z.AI(GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

도구 + image 포함 gateway 스모크 실행:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### 기준선: tool calling(Read + 선택적 Exec)

provider 계열별로 적어도 하나는 선택하세요:

- OpenAI: `openai/gpt-5.4` (또는 `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (또는 `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (또는 `google/gemini-3.1-pro-preview`)
- Z.AI(GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

선택적 추가 커버리지(있으면 좋음):

- xAI: `xai/grok-4` (또는 최신 사용 가능 버전)
- Mistral: `mistral/`… (활성화된 “tools” 가능 모델 하나 선택)
- Cerebras: `cerebras/`… (접근 권한이 있다면)
- LM Studio: `lmstudio/`… (로컬, tool calling은 API mode에 따라 다름)

### Vision: 이미지 전송(첨부 파일 → 멀티모달 메시지)

image probe를 실행하려면 `OPENCLAW_LIVE_GATEWAY_MODELS`에 적어도 하나의 image-capable 모델(Claude/Gemini/OpenAI의 vision-capable 변형 등)을 포함하세요.

### Aggregator / 대체 gateway

키가 활성화되어 있다면 다음을 통한 테스트도 지원합니다:

- OpenRouter: `openrouter/...` (수백 개 모델, `openclaw models scan`으로 tool+image 가능한 후보 찾기)
- OpenCode: Zen용 `opencode/...`, Go용 `opencode-go/...` (`OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`로 인증)

live 매트릭스에 포함할 수 있는 더 많은 provider(자격 증명/config이 있다면):

- 내장: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- `models.providers`를 통해(사용자 지정 엔드포인트): `minimax`(cloud/API) 및 모든 OpenAI/Anthropic 호환 프록시(LM Studio, vLLM, LiteLLM 등)

팁: 문서에 “모든 모델”을 하드코딩하려 하지 마세요. 권위 있는 목록은 사용자의 머신에서 `discoverModels(...)`가 반환하는 것과 사용 가능한 키가 무엇인지입니다.

## 자격 증명(절대 커밋 금지)

Live 테스트는 CLI와 동일한 방식으로 자격 증명을 찾습니다. 실질적 의미는 다음과 같습니다:

- CLI가 동작하면 live 테스트도 같은 키를 찾아야 합니다.
- live 테스트가 “자격 증명 없음”이라고 하면, `openclaw models list` / 모델 선택을 디버깅하는 것과 같은 방식으로 디버깅하세요.

- agent별 auth profile: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (live 테스트에서 말하는 “profile keys”가 이것입니다)
- Config: `~/.openclaw/openclaw.json` (또는 `OPENCLAW_CONFIG_PATH`)
- 레거시 상태 디렉터리: `~/.openclaw/credentials/` (존재하면 staged live home에 복사되지만, 주된 profile-key 저장소는 아님)
- Live 로컬 실행은 기본적으로 활성 config, agent별 `auth-profiles.json` 파일, 레거시 `credentials/`, 지원되는 외부 CLI auth 디렉터리를 임시 테스트 home에 복사합니다. 이때 staged config에서는 `agents.*.workspace` / `agentDir` 경로 재정의가 제거되어 probe가 실제 호스트 워크스페이스를 건드리지 않도록 합니다.

env 키(예: `~/.profile`에서 export된 것)에 의존하고 싶다면, 로컬 테스트를 `source ~/.profile` 후 실행하거나 아래 Docker 실행기를 사용하세요(컨테이너에 `~/.profile`을 마운트할 수 있음).

## Deepgram live(오디오 전사)

- 테스트: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- 활성화: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- 테스트: `src/agents/byteplus.live.test.ts`
- 활성화: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- 선택적 모델 재정의: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## 이미지 생성 live

- 테스트: `src/image-generation/runtime.live.test.ts`
- 명령: `pnpm test:live src/image-generation/runtime.live.test.ts`
- 범위:
  - 등록된 모든 이미지 생성 provider plugin 열거
  - probe 전에 로그인 셸(`~/.profile`)에서 누락된 provider env var 로드
  - 기본적으로 저장된 auth profile보다 live/env API 키를 우선 사용하므로 `auth-profiles.json`의 오래된 테스트 키가 실제 셸 자격 증명을 가리지 않음
  - 사용 가능한 auth/profile/model이 없는 provider는 건너뜀
  - 공유 런타임 capability를 통해 기본 이미지 생성 변형 실행:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- 현재 번들 provider 커버리지:
  - `openai`
  - `google`
- 선택적 범위 축소:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- 선택적 인증 동작:
  - profile-store auth를 강제하고 env 전용 재정의를 무시하려면 `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Docker 실행기(선택적 "Linux에서도 동작하는가" 점검)

이 Docker 실행기는 두 가지 범주로 나뉩니다:

- Live-model 실행기: `test:docker:live-models` 및 `test:docker:live-gateway`는 저장소 Docker 이미지 안에서 해당 profile-key live 파일(`src/agents/models.profiles.live.test.ts` 및 `src/gateway/gateway-models.profiles.live.test.ts`)만 실행하며, 로컬 config dir와 workspace를 마운트하고(마운트된 경우 `~/.profile`도 source) 실행합니다. 대응하는 로컬 엔트리포인트는 `test:live:models-profiles` 및 `test:live:gateway-profiles`입니다.
- Docker live 실행기는 전체 Docker 스윕이 실용적으로 유지되도록 더 작은 스모크 cap을 기본값으로 사용합니다:
  `test:docker:live-models`는 기본적으로 `OPENCLAW_LIVE_MAX_MODELS=12`,
  `test:docker:live-gateway`는 기본적으로 `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`, 및
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`를 설정합니다. 더 큰 exhaustive scan을 명시적으로 원할 때는 해당 env var를 재정의하세요.
- `test:docker:all`은 먼저 `test:docker:live-build`를 통해 live Docker 이미지를 한 번 빌드한 뒤 두 live Docker 레인에서 이를 재사용합니다.
- Container 스모크 실행기: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels`, `test:docker:plugins`는 하나 이상의 실제 컨테이너를 부팅하고 더 높은 수준의 integration 경로를 검증합니다.

live-model Docker 실행기는 또한 필요한 CLI auth 홈만 bind-mount하거나(실행이 좁혀지지 않은 경우 지원되는 모든 것), 실행 전에 이를 컨테이너 홈으로 복사하여 외부 CLI OAuth가 호스트 auth store를 변경하지 않고도 토큰을 갱신할 수 있도록 합니다:

- 직접 모델: `pnpm test:docker:live-models` (스크립트: `scripts/test-live-models-docker.sh`)
- ACP bind 스모크: `pnpm test:docker:live-acp-bind` (스크립트: `scripts/test-live-acp-bind-docker.sh`)
- CLI backend 스모크: `pnpm test:docker:live-cli-backend` (스크립트: `scripts/test-live-cli-backend-docker.sh`)
- Gateway + 개발 agent: `pnpm test:docker:live-gateway` (스크립트: `scripts/test-live-gateway-models-docker.sh`)
- Open WebUI live 스모크: `pnpm test:docker:openwebui` (스크립트: `scripts/e2e/openwebui-docker.sh`)
- Onboarding 마법사(TTY, 전체 scaffolding): `pnpm test:docker:onboard` (스크립트: `scripts/e2e/onboard-docker.sh`)
- Gateway 네트워킹(두 컨테이너, WS auth + health): `pnpm test:docker:gateway-network` (스크립트: `scripts/e2e/gateway-network-docker.sh`)
- MCP 채널 브리지(시드된 Gateway + stdio 브리지 + 원시 Claude notification-frame 스모크): `pnpm test:docker:mcp-channels` (스크립트: `scripts/e2e/mcp-channels-docker.sh`)
- Plugins(설치 스모크 + `/plugin` 별칭 + Claude 번들 재시작 의미 체계): `pnpm test:docker:plugins` (스크립트: `scripts/e2e/plugins-docker.sh`)

live-model Docker 실행기는 현재 체크아웃도 읽기 전용으로 bind-mount하고 컨테이너 내부의 임시 workdir에 stage합니다. 이렇게 하면 런타임 이미지는 슬림하게 유지하면서도 정확히 사용자의 로컬 소스/config에 대해 Vitest를 실행할 수 있습니다.
또한 `OPENCLAW_SKIP_CHANNELS=1`을 설정하여 gateway live probe가 컨테이너 내부에서 실제 Telegram/Discord 등 채널 worker를 시작하지 않도록 합니다.
`test:docker:live-models`는 여전히 `pnpm test:live`를 실행하므로 해당 Docker 레인에서 gateway live 커버리지를 좁히거나 제외해야 할 때는 `OPENCLAW_LIVE_GATEWAY_*`도 함께 전달하세요.
`test:docker:openwebui`는 더 높은 수준의 호환성 스모크입니다. OpenAI 호환 HTTP 엔드포인트가 활성화된 OpenClaw gateway 컨테이너를 시작하고,
그 gateway를 대상으로 고정된 Open WebUI 컨테이너를 시작하며, Open WebUI를 통해 로그인하고,
`/api/models`가 `openclaw/default`를 노출하는지 검증한 다음 Open WebUI의 `/api/chat/completions` 프록시를 통해
실제 chat 요청을 보냅니다.
첫 실행은 Docker가 Open WebUI 이미지를 pull해야 하거나 Open WebUI 자체의 cold-start 설정을 마쳐야 할 수 있으므로 눈에 띄게 느릴 수 있습니다.
이 레인은 사용 가능한 live 모델 키를 기대하며, Dockerized 실행에서 이를 제공하는 기본 수단은 `OPENCLAW_PROFILE_FILE`
(기본값 `~/.profile`)입니다.
성공한 실행은 `{ "ok": true, "model":
"openclaw/default", ... }` 같은 작은 JSON 페이로드를 출력합니다.
`test:docker:mcp-channels`는 의도적으로 결정적이며 실제 Telegram, Discord, iMessage 계정이 필요하지 않습니다.
시드된 Gateway 컨테이너를 부팅하고,
`openclaw mcp serve`를 실행하는 두 번째 컨테이너를 시작한 뒤,
실제 stdio MCP 브리지를 통해 라우팅된 대화 검색, transcript 읽기, 첨부 파일 메타데이터,
live 이벤트 큐 동작, 아웃바운드 전송 라우팅, Claude 스타일 채널 +
권한 알림을 검증합니다. 알림 검사는 원시 stdio MCP 프레임을 직접 검사하므로,
이 스모크는 특정 클라이언트 SDK가 표면에 노출하는 내용이 아니라
브리지가 실제로 무엇을 내보내는지를 검증합니다.

수동 ACP 평문 스레드 스모크(CI 아님):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- 이 스크립트는 회귀/디버깅 워크플로를 위해 유지하세요. ACP 스레드 라우팅 검증에 다시 필요할 수 있으므로 삭제하지 마세요.

유용한 env var:

- `OPENCLAW_CONFIG_DIR=...` (기본값: `~/.openclaw`) → `/home/node/.openclaw`에 마운트
- `OPENCLAW_WORKSPACE_DIR=...` (기본값: `~/.openclaw/workspace`) → `/home/node/.openclaw/workspace`에 마운트
- `OPENCLAW_PROFILE_FILE=...` (기본값: `~/.profile`) → `/home/node/.profile`에 마운트되고 테스트 실행 전 source됨
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (기본값: `~/.cache/openclaw/docker-cli-tools`) → Docker 내부 캐시된 CLI 설치를 위해 `/home/node/.npm-global`에 마운트
- `$HOME` 아래의 외부 CLI auth dir는 `/host-auth/...` 아래에 읽기 전용으로 마운트된 뒤 테스트 시작 전 `/home/node/...`로 복사됨
  - 기본값: 지원되는 모든 dir 마운트(`.codex`, `.claude`, `.minimax`)
  - 좁혀진 provider 실행은 `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`에서 추론된 필요한 dir만 마운트
  - 수동 재정의: `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none`, 또는 `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex` 같은 쉼표 목록
- 실행 범위 축소용 `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`
- 컨테이너 내부 provider 필터용 `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`
- 자격 증명이 profile store에서 오도록 보장하려면 `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`
- Open WebUI 스모크에서 gateway가 노출할 모델을 선택하려면 `OPENCLAW_OPENWEBUI_MODEL=...`
- Open WebUI 스모크에서 사용하는 nonce-check 프롬프트를 재정의하려면 `OPENCLAW_OPENWEBUI_PROMPT=...`
- 고정된 Open WebUI 이미지 태그를 재정의하려면 `OPENWEBUI_IMAGE=...`

## Docs sanity

문서 수정 후 docs 검사 실행: `pnpm check:docs`.
페이지 내 heading 검사까지 필요할 때는 전체 Mintlify anchor 검증 실행: `pnpm docs:check-links:anchors`.

## 오프라인 회귀(CI 안전)

다음은 실제 provider 없이도 “실제 파이프라인” 회귀를 다루는 테스트입니다:

- Gateway tool calling(mock OpenAI, 실제 gateway + agent loop): `src/gateway/gateway.test.ts` (사례: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Gateway 마법사(WS `wizard.start`/`wizard.next`, config 작성 + auth 강제): `src/gateway/gateway.test.ts` (사례: "runs wizard over ws and writes auth token config")

## Agent 신뢰성 평가(Skills)

이미 CI 안전한 몇몇 테스트가 “agent 신뢰성 평가”처럼 동작합니다:

- 실제 gateway + agent loop를 통한 mock tool-calling (`src/gateway/gateway.test.ts`)
- 세션 wiring과 config 효과를 검증하는 종단간 마법사 흐름 (`src/gateway/gateway.test.ts`)

Skills 측면에서 아직 부족한 것(참조: [Skills](/tools/skills)):

- **의사결정:** 프롬프트에 skills가 나열되어 있을 때 agent가 올바른 skill을 선택하는가(또는 관련 없는 것은 피하는가)?
- **준수성:** agent가 사용 전에 `SKILL.md`를 읽고 필수 단계/인수를 따르는가?
- **워크플로 계약:** 도구 순서, 세션 기록 유지, sandbox 경계를 단언하는 다중 턴 시나리오

향후 평가는 우선 결정적이어야 합니다:

- mock provider를 사용해 도구 호출 + 순서, skill 파일 읽기, 세션 wiring을 단언하는 시나리오 runner
- skill 중심 시나리오의 소규모 스위트(사용 vs 회피, 게이팅, 프롬프트 주입)
- CI 안전 스위트가 자리 잡은 뒤에만 선택적 live 평가(env gated)

## 계약 테스트(plugin 및 channel 형태)

계약 테스트는 등록된 모든 plugin과 channel이
해당 인터페이스 계약을 준수하는지 검증합니다. 발견된 모든 plugin을 순회하며
형태 및 동작 단언 스위트를 실행합니다. 기본 `pnpm test` unit 레인은 의도적으로
이러한 공유 seam 및 스모크 파일을 건너뛰므로, 공유 channel 또는 provider 표면을 수정했다면 계약 명령을 명시적으로 실행하세요.

### 명령

- 모든 계약 테스트: `pnpm test:contracts`
- Channel 계약만: `pnpm test:contracts:channels`
- Provider 계약만: `pnpm test:contracts:plugins`

### Channel 계약

`src/channels/plugins/contracts/*.contract.test.ts`에 위치:

- **plugin** - 기본 plugin 형태(id, name, capabilities)
- **setup** - setup wizard 계약
- **session-binding** - 세션 바인딩 동작
- **outbound-payload** - 메시지 페이로드 구조
- **inbound** - 수신 메시지 처리
- **actions** - channel action handler
- **threading** - thread ID 처리
- **directory** - 디렉터리/roster API
- **group-policy** - 그룹 정책 강제

### Provider 상태 계약

`src/plugins/contracts/*.contract.test.ts`에 위치.

- **status** - channel status probe
- **registry** - plugin registry 형태

### Provider 계약

`src/plugins/contracts/*.contract.test.ts`에 위치:

- **auth** - auth 흐름 계약
- **auth-choice** - auth 선택/선정
- **catalog** - 모델 카탈로그 API
- **discovery** - plugin 검색
- **loader** - plugin 로딩
- **runtime** - provider 런타임
- **shape** - plugin 형태/인터페이스
- **wizard** - setup wizard

### 언제 실행해야 하나요?

- plugin-sdk export나 subpath를 변경한 후
- channel 또는 provider plugin을 추가하거나 수정한 후
- plugin 등록 또는 검색을 리팩터링한 후

계약 테스트는 CI에서 실행되며 실제 API 키가 필요하지 않습니다.

## 회귀 추가(가이드)

live에서 발견된 provider/모델 문제를 수정할 때:

- 가능하면 CI 안전 회귀를 추가하세요(mock/stub provider 또는 정확한 요청 형태 변환 캡처)
- 본질적으로 live 전용이라면(속도 제한, 인증 정책) live 테스트를 좁게 유지하고 env var를 통해 옵트인하도록 하세요
- 버그를 잡는 가장 작은 계층을 타기팅하세요:
  - provider 요청 변환/replay 버그 → 직접 모델 테스트
  - gateway 세션/기록/도구 파이프라인 버그 → gateway live 스모크 또는 CI 안전 gateway mock 테스트
- SecretRef traversal 가드레일:
  - `src/secrets/exec-secret-ref-id-parity.test.ts`는 레지스트리 메타데이터(`listSecretTargetRegistryEntries()`)에서 SecretRef 클래스별 샘플 대상 하나를 도출하고, traversal-segment exec id가 거부되는지 단언합니다.
  - `src/secrets/target-registry-data.ts`에 새로운 `includeInPlan` SecretRef 대상 계열을 추가한다면 해당 테스트의 `classifyTargetClass`를 업데이트하세요. 이 테스트는 분류되지 않은 target id에 대해 의도적으로 실패하므로 새로운 클래스가 조용히 빠지는 일을 막습니다.
