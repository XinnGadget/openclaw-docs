---
x-i18n:
    generated_at: "2026-04-08T05:56:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4a9066b2a939c5a9ba69141d75405f0e8097997b523164340e2f0e9a0d5060dd
    source_path: refactor/qa.md
    workflow: 15
---

# QA 리팩터링

상태: 기반 마이그레이션이 적용되었습니다.

## 목표

OpenClaw QA를 분리된 정의 모델에서 단일 진실 공급원으로 이동합니다:

- 시나리오 메타데이터
- 모델에 전송되는 프롬프트
- 설정 및 정리
- 하네스 로직
- 단언과 성공 기준
- 아티팩트 및 보고서 힌트

목표하는 최종 상태는 대부분의 동작을 TypeScript에 하드코딩하는 대신, 강력한 시나리오 정의 파일을 로드하는 범용 QA 하네스입니다.

## 현재 상태

이제 주된 진실 공급원은 `qa/scenarios/index.md`와 `qa/scenarios/*.md` 아래의 시나리오별 파일 하나씩입니다.

구현됨:

- `qa/scenarios/index.md`
  - 정식 QA 팩 메타데이터
  - 운영자 식별 정보
  - 시작 미션
- `qa/scenarios/*.md`
  - 시나리오별 Markdown 파일 하나
  - 시나리오 메타데이터
  - 핸들러 바인딩
  - 시나리오별 실행 설정
- `extensions/qa-lab/src/scenario-catalog.ts`
  - Markdown 팩 파서 + zod 검증
- `extensions/qa-lab/src/qa-agent-bootstrap.ts`
  - Markdown 팩에서 계획 렌더링
- `extensions/qa-lab/src/qa-agent-workspace.ts`
  - 생성된 호환성 파일과 `QA_SCENARIOS.md` 시드
- `extensions/qa-lab/src/suite.ts`
  - Markdown으로 정의된 핸들러 바인딩을 통해 실행 가능한 시나리오 선택
- QA 버스 프로토콜 + UI
  - 이미지/비디오/오디오/파일 렌더링을 위한 범용 인라인 첨부

남아 있는 분리된 표면:

- `extensions/qa-lab/src/suite.ts`
  - 여전히 대부분의 실행 가능한 커스텀 핸들러 로직을 소유
- `extensions/qa-lab/src/report.ts`
  - 여전히 런타임 출력에서 보고서 구조를 도출

즉, 진실 공급원 분리는 해결되었지만, 실행은 아직 완전한 선언형이 아니라 대부분 핸들러 기반입니다.

## 실제 시나리오 표면의 모습

현재 suite를 읽어 보면 몇 가지 뚜렷한 시나리오 클래스가 보입니다.

### 단순 상호작용

- 채널 베이스라인
- DM 베이스라인
- 스레드 후속 응답
- 모델 전환
- 승인 후속 진행
- 반응/수정/삭제

### 구성 및 런타임 변경

- config patch skill 비활성화
- config apply 재시작 웨이크업
- config 재시작 기능 전환
- 런타임 인벤토리 드리프트 확인

### 파일 시스템 및 리포지토리 단언

- source/docs 발견 보고서
- Lobster Invaders 빌드
- 생성된 이미지 아티팩트 조회

### 메모리 오케스트레이션

- 메모리 회상
- 채널 컨텍스트에서의 메모리 도구
- 메모리 실패 폴백
- 세션 메모리 랭킹
- 스레드 메모리 격리
- 메모리 dreaming sweep

### 도구 및 plugin 통합

- MCP plugin-tools 호출
- skill 가시성
- skill 핫 설치
- 네이티브 이미지 생성
- 이미지 왕복
- 첨부에서의 이미지 이해

### 멀티턴 및 멀티 액터

- 서브에이전트 핸드오프
- 서브에이전트 팬아웃 합성
- 재시작 복구 스타일 플로우

이 범주들은 DSL 요구사항을 결정하기 때문에 중요합니다. 프롬프트 + 기대 텍스트의 평면 목록만으로는 충분하지 않습니다.

## 방향

### 단일 진실 공급원

작성되는 진실 공급원으로 `qa/scenarios/index.md`와 `qa/scenarios/*.md`를 사용합니다.

팩은 다음 상태를 유지해야 합니다:

- 리뷰에서 사람이 읽기 쉬움
- 기계가 파싱 가능함
- 다음을 구동할 만큼 충분히 풍부함:
  - suite 실행
  - QA 작업 공간 부트스트랩
  - QA Lab UI 메타데이터
  - docs/discovery 프롬프트
  - 보고서 생성

### 선호되는 작성 형식

최상위 형식은 Markdown을 사용하고, 그 안에 구조화된 YAML을 둡니다.

권장 형태:

- YAML frontmatter
  - id
  - title
  - surface
  - tags
  - docs refs
  - code refs
  - model/provider 재정의
  - prerequisites
- 설명 섹션
  - objective
  - notes
  - debugging hints
- fenced YAML 블록
  - setup
  - steps
  - assertions
  - cleanup

이 방식의 장점:

- 거대한 JSON보다 더 나은 PR 가독성
- 순수 YAML보다 더 풍부한 컨텍스트
- 엄격한 파싱과 zod 검증

원시 JSON은 중간 생성 형태로만 허용됩니다.

## 제안하는 시나리오 파일 형태

예시:

````md
---
id: image-generation-roundtrip
title: Image generation roundtrip
surface: image
tags: [media, image, roundtrip]
models:
  primary: openai/gpt-5.4
requires:
  tools: [image_generate]
  plugins: [openai, qa-channel]
docsRefs:
  - docs/help/testing.md
  - docs/concepts/model-providers.md
codeRefs:
  - extensions/qa-lab/src/suite.ts
  - src/gateway/chat-attachments.ts
---

# Objective

Verify generated media is reattached on the follow-up turn.

# Setup

```yaml scenario.setup
- action: config.patch
  patch:
    agents:
      defaults:
        imageGenerationModel:
          primary: openai/gpt-image-1
- action: session.create
  key: agent:qa:image-roundtrip
```

# Steps

```yaml scenario.steps
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Image generation check: generate a QA lighthouse image and summarize it in one short sentence.
- action: artifact.capture
  kind: generated-image
  promptSnippet: Image generation check
  saveAs: lighthouseImage
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Roundtrip image inspection check: describe the generated lighthouse attachment in one short sentence.
  attachments:
    - fromArtifact: lighthouseImage
```

# Expect

```yaml scenario.expect
- assert: outbound.textIncludes
  value: lighthouse
- assert: requestLog.matches
  where:
    promptIncludes: Roundtrip image inspection check
  imageInputCountGte: 1
- assert: artifact.exists
  ref: lighthouseImage
```
````

## DSL이 다뤄야 하는 러너 기능

현재 suite를 기준으로 보면, 범용 러너는 단순한 프롬프트 실행 이상의 기능이 필요합니다.

### 환경 및 설정 작업

- `bus.reset`
- `gateway.waitHealthy`
- `channel.waitReady`
- `session.create`
- `thread.create`
- `workspace.writeSkill`

### 에이전트 턴 작업

- `agent.send`
- `agent.wait`
- `bus.injectInbound`
- `bus.injectOutbound`

### 구성 및 런타임 작업

- `config.get`
- `config.patch`
- `config.apply`
- `gateway.restart`
- `tools.effective`
- `skills.status`

### 파일 및 아티팩트 작업

- `file.write`
- `file.read`
- `file.delete`
- `file.touchTime`
- `artifact.captureGeneratedImage`
- `artifact.capturePath`

### 메모리 및 cron 작업

- `memory.indexForce`
- `memory.searchCli`
- `doctor.memory.status`
- `cron.list`
- `cron.run`
- `cron.waitCompletion`
- `sessionTranscript.write`

### MCP 작업

- `mcp.callTool`

### 단언

- `outbound.textIncludes`
- `outbound.inThread`
- `outbound.notInRoot`
- `tool.called`
- `tool.notPresent`
- `skill.visible`
- `skill.disabled`
- `file.contains`
- `memory.contains`
- `requestLog.matches`
- `sessionStore.matches`
- `cron.managedPresent`
- `artifact.exists`

## 변수 및 아티팩트 참조

DSL은 저장된 출력과 이후 참조를 지원해야 합니다.

현재 suite의 예시:

- 스레드를 만든 뒤 `threadId` 재사용
- 세션을 만든 뒤 `sessionKey` 재사용
- 이미지를 생성한 뒤 다음 턴에 해당 파일 첨부
- 웨이크 마커 문자열을 생성한 뒤 나중에 나타나는지 단언

필요한 기능:

- `saveAs`
- `${vars.name}`
- `${artifacts.name}`
- 경로, 세션 키, 스레드 id, 마커, 도구 출력을 위한 타입 지정 참조

변수 지원이 없으면 하네스는 계속해서 시나리오 로직을 TypeScript로 다시 새어 나가게 됩니다.

## 이스케이프 해치로 남겨야 할 것

1단계에서 완전히 순수한 선언형 러너는 현실적이지 않습니다.

일부 시나리오는 본질적으로 오케스트레이션 비중이 큽니다:

- memory dreaming sweep
- config apply 재시작 웨이크업
- config 재시작 기능 전환
- 타임스탬프/경로 기준 생성 이미지 아티팩트 해석
- discovery-report 평가

이들은 우선 명시적인 커스텀 핸들러를 사용해야 합니다.

권장 규칙:

- 85-90%는 선언형
- 어려운 나머지를 위해 명시적인 `customHandler` 단계 사용
- 이름이 있고 문서화된 커스텀 핸들러만 허용
- 시나리오 파일에 익명 인라인 코드는 허용하지 않음

이렇게 하면 범용 엔진을 깔끔하게 유지하면서도 계속 진전할 수 있습니다.

## 아키텍처 변경

### 현재

시나리오 Markdown은 이미 다음의 진실 공급원입니다:

- suite 실행
- 작업 공간 부트스트랩 파일
- QA Lab UI 시나리오 카탈로그
- 보고서 메타데이터
- discovery 프롬프트

생성된 호환성 항목:

- 시드된 작업 공간에는 여전히 `QA_KICKOFF_TASK.md`가 포함됨
- 시드된 작업 공간에는 여전히 `QA_SCENARIO_PLAN.md`가 포함됨
- 시드된 작업 공간에는 이제 `QA_SCENARIOS.md`도 포함됨

## 리팩터링 계획

### 1단계: 로더 및 스키마

완료.

- `qa/scenarios/index.md` 추가
- 시나리오를 `qa/scenarios/*.md`로 분리
- 이름 있는 Markdown YAML 팩 콘텐츠용 파서 추가
- zod로 검증
- 소비자를 파싱된 팩으로 전환
- 리포지토리 수준의 `qa/seed-scenarios.json` 및 `qa/QA_KICKOFF_TASK.md` 제거

### 2단계: 범용 엔진

- `extensions/qa-lab/src/suite.ts`를 다음으로 분리:
  - loader
  - engine
  - action registry
  - assertion registry
  - custom handlers
- 기존 헬퍼 함수를 엔진 작업으로 유지

결과물:

- 엔진이 단순한 선언형 시나리오를 실행함

우선 대부분 프롬프트 + 대기 + 단언으로 구성된 시나리오부터 시작:

- 스레드 후속 응답
- 첨부에서의 이미지 이해
- skill 가시성과 호출
- 채널 베이스라인

결과물:

- 최초의 실제 Markdown 정의 시나리오가 범용 엔진을 통해 제공됨

### 4단계: 중간 난이도 시나리오 마이그레이션

- 이미지 생성 왕복
- 채널 컨텍스트에서의 메모리 도구
- 세션 메모리 랭킹
- 서브에이전트 핸드오프
- 서브에이전트 팬아웃 합성

결과물:

- 변수, 아티팩트, 도구 단언, request-log 단언이 검증됨

### 5단계: 어려운 시나리오는 커스텀 핸들러에 유지

- memory dreaming sweep
- config apply 재시작 웨이크업
- config 재시작 기능 전환
- 런타임 인벤토리 드리프트

결과물:

- 동일한 작성 형식이지만, 필요 시 명시적인 custom-step 블록 사용

### 6단계: 하드코딩된 시나리오 맵 삭제

팩 커버리지가 충분히 좋아지면:

- `extensions/qa-lab/src/suite.ts`에서 대부분의 시나리오별 TypeScript 분기를 제거

## 가짜 Slack / 리치 미디어 지원

현재 QA 버스는 텍스트 우선입니다.

관련 파일:

- `extensions/qa-channel/src/protocol.ts`
- `extensions/qa-lab/src/bus-state.ts`
- `extensions/qa-lab/src/bus-queries.ts`
- `extensions/qa-lab/src/bus-server.ts`
- `extensions/qa-lab/web/src/ui-render.ts`

오늘날 QA 버스가 지원하는 항목:

- 텍스트
- 반응
- 스레드

아직 인라인 미디어 첨부는 모델링하지 않습니다.

### 필요한 전송 계약

범용 QA 버스 첨부 모델을 추가합니다:

```ts
type QaBusAttachment = {
  id: string;
  kind: "image" | "video" | "audio" | "file";
  mimeType: string;
  fileName?: string;
  inline?: boolean;
  url?: string;
  contentBase64?: string;
  width?: number;
  height?: number;
  durationMs?: number;
  altText?: string;
  transcript?: string;
};
```

그 다음 다음 항목들에 `attachments?: QaBusAttachment[]`를 추가합니다:

- `QaBusMessage`
- `QaBusInboundMessageInput`
- `QaBusOutboundMessageInput`

### 왜 먼저 범용으로 해야 하는가

Slack 전용 미디어 모델을 만들지 마세요.

대신:

- 하나의 범용 QA 전송 모델
- 그 위에 여러 렌더러를 구축
  - 현재 QA Lab 채팅
  - 향후 가짜 Slack 웹
  - 기타 다른 가짜 전송 뷰

이렇게 하면 로직 중복을 방지하고 미디어 시나리오가 전송 수단에 독립적으로 유지됩니다.

### 필요한 UI 작업

QA UI를 업데이트하여 다음을 렌더링합니다:

- 인라인 이미지 미리보기
- 인라인 오디오 플레이어
- 인라인 비디오 플레이어
- 파일 첨부 칩

현재 UI는 이미 스레드와 반응을 렌더링할 수 있으므로, 첨부 렌더링은 동일한 메시지 카드 모델 위에 계층화할 수 있어야 합니다.

### 미디어 전송으로 가능해지는 시나리오 작업

첨부가 QA 버스를 통해 흐르기 시작하면 더 풍부한 가짜 채팅 시나리오를 추가할 수 있습니다:

- 가짜 Slack에서의 인라인 이미지 응답
- 오디오 첨부 이해
- 비디오 첨부 이해
- 혼합 첨부 순서
- 미디어가 유지되는 스레드 응답

## 권장 사항

다음 구현 단위는 다음이어야 합니다:

1. Markdown 시나리오 로더 + zod 스키마 추가
2. 현재 카탈로그를 Markdown에서 생성
3. 먼저 몇 가지 단순한 시나리오 마이그레이션
4. 범용 QA 버스 첨부 지원 추가
5. QA UI에 인라인 이미지 렌더링
6. 그 다음 오디오와 비디오로 확장

이것이 두 목표를 모두 입증하는 가장 작은 경로입니다:

- 범용 Markdown 정의 QA
- 더 풍부한 가짜 메시징 표면

## 열린 질문

- 시나리오 파일에서 변수 보간이 포함된 내장 Markdown 프롬프트 템플릿을 허용해야 하는지 여부
- setup/cleanup을 이름 있는 섹션으로 둘지, 아니면 단순한 순서형 작업 목록으로 둘지 여부
- 아티팩트 참조를 스키마에서 강한 타입으로 둘지, 아니면 문자열 기반으로 둘지 여부
- 커스텀 핸들러를 하나의 레지스트리에 둘지, 아니면 surface별 레지스트리로 나눌지 여부
- 생성된 JSON 호환성 파일을 마이그레이션 중에도 계속 체크인 상태로 유지해야 하는지 여부
