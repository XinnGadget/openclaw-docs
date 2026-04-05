---
read_when:
    - 테스트를 실행하거나 수정하고 있습니다
summary: 로컬에서 테스트(vitest)를 실행하는 방법과 force/coverage 모드를 사용해야 하는 경우
title: 테스트
x-i18n:
    generated_at: "2026-04-05T12:54:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 78390107a9ac2bdc4294d4d0204467c5efdd98faebaf308f3a4597ab966a6d26
    source_path: reference/test.md
    workflow: 15
---

# 테스트

- 전체 테스트 키트(스위트, 라이브, Docker): [테스트](/ko/help/testing)

- `pnpm test:force`: 기본 control 포트를 점유하고 있는 남아 있는 gateway 프로세스를 종료한 다음, 격리된 gateway 포트로 전체 Vitest 스위트를 실행하여 서버 테스트가 실행 중인 인스턴스와 충돌하지 않게 합니다. 이전 gateway 실행으로 포트 18789가 점유된 상태로 남았을 때 사용하세요.
- `pnpm test:coverage`: V8 커버리지와 함께 유닛 스위트를 실행합니다(`vitest.unit.config.ts` 사용). 전역 기준치는 lines/branches/functions/statements 모두 70%입니다. 목표를 유닛 테스트 가능한 로직에 집중시키기 위해 커버리지에서 통합 비중이 큰 엔트리포인트(CLI wiring, gateway/telegram 브리지, webchat 정적 서버)는 제외됩니다.
- `pnpm test:coverage:changed`: `origin/main` 이후 변경된 파일에 대해서만 유닛 커버리지를 실행합니다.
- `pnpm test:changed`: `--changed origin/main`과 함께 네이티브 Vitest projects config를 실행합니다. 기본 config는 projects/config 파일을 `forceRerunTriggers`로 취급하므로, wiring 변경이 있을 때도 필요하면 폭넓게 다시 실행됩니다.
- `pnpm test`: 네이티브 Vitest 루트 projects config를 직접 실행합니다. 파일 필터는 구성된 프로젝트 전체에서 네이티브하게 동작합니다.
- 기본 Vitest config는 이제 `pool: "threads"`와 `isolate: false`를 기본값으로 사용하며, 공유 비격리 runner가 저장소 config 전반에서 활성화됩니다.
- `pnpm test:channels`는 `vitest.channels.config.ts`를 실행합니다.
- `pnpm test:extensions`는 `vitest.extensions.config.ts`를 실행합니다.
- `pnpm test:extensions`: extension/plugin 스위트를 실행합니다.
- `pnpm test:perf:imports`: 네이티브 루트 projects 실행에 대해 Vitest import-duration + import-breakdown 리포팅을 활성화합니다.
- `pnpm test:perf:imports:changed`: 동일한 import 프로파일링이지만, `origin/main` 이후 변경된 파일에 대해서만 실행합니다.
- `pnpm test:perf:profile:main`: Vitest 메인 스레드에 대한 CPU 프로파일을 기록합니다(`.artifacts/vitest-main-profile`).
- `pnpm test:perf:profile:runner`: 유닛 runner에 대한 CPU + 힙 프로파일을 기록합니다(`.artifacts/vitest-runner-profile`).
- Gateway 통합: `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` 또는 `pnpm test:gateway`로 옵트인합니다.
- `pnpm test:e2e`: gateway 엔드투엔드 스모크 테스트(멀티 인스턴스 WS/HTTP/node 페어링)를 실행합니다. 기본값은 `vitest.e2e.config.ts`의 적응형 워커와 함께 `threads` + `isolate: false`이며, `OPENCLAW_E2E_WORKERS=<n>`으로 조정하고 자세한 로그가 필요하면 `OPENCLAW_E2E_VERBOSE=1`을 설정하세요.
- `pnpm test:live`: 제공자 라이브 테스트(minimax/zai)를 실행합니다. 건너뛰지 않으려면 API 키와 `LIVE=1`(또는 제공자별 `*_LIVE_TEST=1`)이 필요합니다.
- `pnpm test:docker:openwebui`: Docker로 OpenClaw + Open WebUI를 시작하고, Open WebUI를 통해 로그인하고, `/api/models`를 확인한 다음, `/api/chat/completions`를 통해 실제 프록시 채팅을 실행합니다. 사용 가능한 라이브 모델 키(예: `~/.profile`의 OpenAI)가 필요하고, 외부 Open WebUI 이미지를 pull하며, 일반 유닛/e2e 스위트처럼 CI에서 안정적일 것으로 기대되지는 않습니다.
- `pnpm test:docker:mcp-channels`: 시드된 Gateway 컨테이너와 `openclaw mcp serve`를 실행하는 두 번째 클라이언트 컨테이너를 시작한 다음, 실제 stdio 브리지를 통해 라우팅된 대화 검색, transcript 읽기, 첨부파일 메타데이터, 라이브 이벤트 큐 동작, 아웃바운드 전송 라우팅, Claude 스타일 채널 + 권한 알림을 검증합니다. Claude 알림 검증은 원시 stdio MCP 프레임을 직접 읽으므로, 이 스모크는 브리지가 실제로 내보내는 내용을 반영합니다.

## 로컬 PR 게이트

로컬 PR land/gate 확인을 위해 다음을 실행하세요:

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

로드가 높은 호스트에서 `pnpm test`가 불안정하면, 회귀로 판단하기 전에 한 번 더 실행한 다음 `pnpm test <path/to/test>`로 범위를 좁히세요. 메모리가 제한된 호스트에서는 다음을 사용하세요:

- `OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test`
- `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/tmp/openclaw-vitest-cache pnpm test:changed`

## 모델 지연 시간 벤치(로컬 키)

스크립트: [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

사용법:

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- 선택적 env: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`, `ANTHROPIC_API_KEY`
- 기본 프롬프트: “한 단어로 답하세요: ok. 구두점이나 추가 텍스트는 없습니다.”

마지막 실행(2025-12-31, 20회):

- minimax 중앙값 1279ms(최소 1114, 최대 2431)
- opus 중앙값 2454ms(최소 1224, 최대 3170)

## CLI 시작 벤치

스크립트: [`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

사용법:

- `pnpm test:startup:bench`
- `pnpm test:startup:bench:smoke`
- `pnpm test:startup:bench:save`
- `pnpm test:startup:bench:update`
- `pnpm test:startup:bench:check`
- `pnpm tsx scripts/bench-cli-startup.ts`
- `pnpm tsx scripts/bench-cli-startup.ts --runs 12`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case status --case gatewayStatus --runs 3`
- `pnpm tsx scripts/bench-cli-startup.ts --entry openclaw.mjs --entry-secondary dist/entry.js --preset all`
- `pnpm tsx scripts/bench-cli-startup.ts --preset all --output .artifacts/cli-startup-bench-all.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case gatewayStatusJson --output .artifacts/cli-startup-bench-smoke.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --cpu-prof-dir .artifacts/cli-cpu`
- `pnpm tsx scripts/bench-cli-startup.ts --json`

프리셋:

- `startup`: `--version`, `--help`, `health`, `health --json`, `status --json`, `status`
- `real`: `health`, `status`, `status --json`, `sessions`, `sessions --json`, `agents list --json`, `gateway status`, `gateway status --json`, `gateway health --json`, `config get gateway.port`
- `all`: 두 프리셋 모두

출력에는 각 명령에 대한 `sampleCount`, avg, p50, p95, min/max, exit-code/signal 분포, 최대 RSS 요약이 포함됩니다. 선택적인 `--cpu-prof-dir` / `--heap-prof-dir`은 실행별 V8 프로파일을 기록하므로, 타이밍과 프로파일 캡처가 동일한 하네스를 사용합니다.

저장된 출력 규칙:

- `pnpm test:startup:bench:smoke`는 대상 스모크 아티팩트를 `.artifacts/cli-startup-bench-smoke.json`에 기록합니다
- `pnpm test:startup:bench:save`는 `runs=5`와 `warmup=1`을 사용해 전체 스위트 아티팩트를 `.artifacts/cli-startup-bench-all.json`에 기록합니다
- `pnpm test:startup:bench:update`는 `runs=5`와 `warmup=1`을 사용해 체크인된 기준 fixture `test/fixtures/cli-startup-bench.json`을 갱신합니다

체크인된 fixture:

- `test/fixtures/cli-startup-bench.json`
- `pnpm test:startup:bench:update`로 갱신
- `pnpm test:startup:bench:check`로 현재 결과를 fixture와 비교

## 온보딩 E2E(Docker)

Docker는 선택 사항이며, 이는 컨테이너화된 온보딩 스모크 테스트에만 필요합니다.

깨끗한 Linux 컨테이너에서의 전체 콜드 스타트 흐름:

```bash
scripts/e2e/onboard-docker.sh
```

이 스크립트는 pseudo-tty를 통해 대화형 마법사를 구동하고, config/workspace/session 파일을 검증한 다음, gateway를 시작하고 `openclaw health`를 실행합니다.

## QR import 스모크(Docker)

지원되는 Docker Node 런타임(Node 24 기본, Node 22 호환)에서 `qrcode-terminal`이 로드되는지 확인합니다:

```bash
pnpm test:docker:qr
```
