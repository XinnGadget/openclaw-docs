---
read_when:
    - 기본 OpenClaw Plugin 빌드 또는 디버깅
    - Plugin 기능 모델 또는 소유권 경계 이해하기
    - Plugin 로드 파이프라인 또는 레지스트리 작업하기
    - 프로바이더 런타임 훅 또는 채널 Plugin 구현하기
sidebarTitle: Internals
summary: 'Plugin 내부: 기능 모델, 소유권, 계약, 로드 파이프라인 및 런타임 헬퍼'
title: Plugin 내부 구조
x-i18n:
    generated_at: "2026-04-15T06:00:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: f86798b5d2b0ad82d2397a52a6c21ed37fe6eee1dd3d124a9e4150c4f630b841
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin 내부 구조

<Info>
  이 문서는 **심층 아키텍처 참고 자료**입니다. 실용적인 가이드는 다음을 참고하세요:
  - [플러그인 설치 및 사용](/ko/tools/plugin) — 사용자 가이드
  - [시작하기](/ko/plugins/building-plugins) — 첫 번째 플러그인 튜토리얼
  - [채널 Plugin](/ko/plugins/sdk-channel-plugins) — 메시징 채널 빌드
  - [프로바이더 Plugin](/ko/plugins/sdk-provider-plugins) — 모델 프로바이더 빌드
  - [SDK 개요](/ko/plugins/sdk-overview) — import 맵 및 등록 API
</Info>

이 페이지에서는 OpenClaw Plugin 시스템의 내부 아키텍처를 다룹니다.

## 공개 기능 모델

기능은 OpenClaw 내부의 공개 **기본 Plugin** 모델입니다. 모든 기본 OpenClaw Plugin은 하나 이상의 기능 유형에 대해 등록됩니다:

| 기능                   | 등록 방법                                        | 예시 Plugin                           |
| ---------------------- | ------------------------------------------------ | ------------------------------------- |
| 텍스트 추론            | `api.registerProvider(...)`                      | `openai`, `anthropic`                 |
| CLI 추론 백엔드        | `api.registerCliBackend(...)`                    | `openai`, `anthropic`                 |
| 음성                   | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`             |
| 실시간 전사            | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                              |
| 실시간 음성            | `api.registerRealtimeVoiceProvider(...)`         | `openai`                              |
| 미디어 이해            | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                    |
| 이미지 생성            | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax`  |
| 음악 생성              | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                   |
| 비디오 생성            | `api.registerVideoGenerationProvider(...)`       | `qwen`                                |
| 웹 가져오기            | `api.registerWebFetchProvider(...)`              | `firecrawl`                           |
| 웹 검색                | `api.registerWebSearchProvider(...)`             | `google`                              |
| 채널 / 메시징          | `api.registerChannel(...)`                       | `msteams`, `matrix`                   |

기능을 하나도 등록하지 않지만 훅, 도구 또는 서비스를 제공하는 플러그인은 **레거시 hook-only** Plugin입니다. 이 패턴은 여전히 완전히 지원됩니다.

### 외부 호환성 입장

기능 모델은 이미 코어에 반영되어 있으며 오늘날 번들/기본 플러그인에서 사용되고 있지만, 외부 플러그인 호환성에는 여전히 "내보내졌으니 곧 고정된 것"보다 더 엄격한 기준이 필요합니다.

현재 지침:

- **기존 외부 플러그인:** 훅 기반 통합이 계속 동작하도록 유지하고, 이를 호환성 기준선으로 취급합니다
- **새 번들/기본 플러그인:** 벤더별 직접 연동이나 새로운 hook-only 설계보다 명시적인 기능 등록을 우선합니다
- **기능 등록을 도입하는 외부 플러그인:** 허용되지만, 문서에서 계약이 안정적이라고 명시적으로 표시하지 않는 한 기능별 헬퍼 표면은 계속 발전하는 것으로 간주합니다

실용적인 규칙:

- 기능 등록 API가 의도된 방향입니다
- 전환 기간 동안 레거시 훅은 외부 플러그인에 대해 가장 안전한 비호환성 없는 경로로 남습니다
- 내보낸 헬퍼 하위 경로가 모두 같은 것은 아닙니다. 우연히 노출된 헬퍼 export가 아니라, 문서화된 좁은 계약을 우선하세요

### Plugin 형태

OpenClaw는 로드된 각 플러그인을 정적 메타데이터만이 아니라 실제 등록 동작을 기준으로 형태를 분류합니다:

- **plain-capability** -- 정확히 하나의 기능 유형만 등록합니다(예: `mistral` 같은 provider-only 플러그인)
- **hybrid-capability** -- 여러 기능 유형을 등록합니다(예: `openai`는 텍스트 추론, 음성, 미디어 이해, 이미지 생성을 담당함)
- **hook-only** -- 기능, 도구, 명령, 서비스 없이 훅만 등록합니다(타입드 훅 또는 커스텀 훅)
- **non-capability** -- 기능 없이 도구, 명령, 서비스 또는 라우트를 등록합니다

플러그인의 형태와 기능 세부 내역은 `openclaw plugins inspect <id>`로 확인할 수 있습니다. 자세한 내용은 [CLI 참고 문서](/cli/plugins#inspect)를 참고하세요.

### 레거시 훅

`before_agent_start` 훅은 hook-only 플러그인을 위한 호환성 경로로 계속 지원됩니다. 실제 레거시 플러그인들이 여전히 이에 의존하고 있습니다.

방향:

- 계속 동작하도록 유지합니다
- 레거시로 문서화합니다
- 모델/프로바이더 재정의 작업에는 `before_model_resolve`를 우선합니다
- 프롬프트 변경 작업에는 `before_prompt_build`를 우선합니다
- 실제 사용이 줄고 fixture 커버리지가 마이그레이션 안전성을 입증한 후에만 제거합니다

### 호환성 신호

`openclaw doctor` 또는 `openclaw plugins inspect <id>`를 실행하면 다음 라벨 중 하나가 표시될 수 있습니다:

| 신호                       | 의미                                                           |
| -------------------------- | -------------------------------------------------------------- |
| **config valid**           | 설정이 정상적으로 파싱되고 플러그인이 해결됨                   |
| **compatibility advisory** | 플러그인이 지원되지만 오래된 패턴(예: `hook-only`)을 사용함    |
| **legacy warning**         | 플러그인이 더 이상 권장되지 않는 `before_agent_start`를 사용함 |
| **hard error**             | 설정이 잘못되었거나 플러그인 로드에 실패함                     |

`hook-only`도 `before_agent_start`도 현재 여러분의 플러그인을 망가뜨리지는 않습니다 -- `hook-only`는 권고 사항이며, `before_agent_start`는 경고만 발생시킵니다. 이러한 신호는 `openclaw status --all`과 `openclaw plugins doctor`에도 표시됩니다.

## 아키텍처 개요

OpenClaw의 Plugin 시스템은 네 개의 계층으로 구성됩니다:

1. **매니페스트 + 탐색**
   OpenClaw는 구성된 경로, 워크스페이스 루트, 전역 확장 루트, 번들 확장에서 후보 플러그인을 찾습니다. 탐색은 먼저 기본 `openclaw.plugin.json` 매니페스트와 지원되는 번들 매니페스트를 읽습니다.
2. **활성화 + 검증**
   코어는 탐지된 플러그인이 활성화, 비활성화, 차단되었는지 또는 메모리와 같은 독점 슬롯에 선택되었는지를 결정합니다.
3. **런타임 로드**
   기본 OpenClaw Plugin은 jiti를 통해 프로세스 내에서 로드되고, 중앙 레지스트리에 기능을 등록합니다. 호환되는 번들은 런타임 코드를 import하지 않고 레지스트리 레코드로 정규화됩니다.
4. **표면 사용**
   OpenClaw의 나머지 부분은 레지스트리를 읽어 도구, 채널, 프로바이더 설정, 훅, HTTP 라우트, CLI 명령, 서비스를 노출합니다.

특히 plugin CLI의 경우, 루트 명령 탐색은 두 단계로 나뉩니다:

- 구문 분석 시점 메타데이터는 `registerCli(..., { descriptors: [...] })`에서 가져옵니다
- 실제 plugin CLI 모듈은 지연 로드된 상태를 유지하다가 첫 호출 시 등록될 수 있습니다

이렇게 하면 OpenClaw가 구문 분석 전에 루트 명령 이름을 예약할 수 있으면서도 plugin 소유 CLI 코드는 플러그인 내부에 유지할 수 있습니다.

중요한 설계 경계는 다음과 같습니다:

- 탐색 + 설정 검증은 plugin 코드를 실행하지 않고 **매니페스트/스키마 메타데이터**만으로 동작해야 합니다
- 기본 런타임 동작은 plugin 모듈의 `register(api)` 경로에서 나옵니다

이 분리는 OpenClaw가 전체 런타임이 활성화되기 전에 설정을 검증하고, 누락되거나 비활성화된 플러그인을 설명하며, UI/스키마 힌트를 구성할 수 있게 해줍니다.

### 채널 Plugin과 공유 message 도구

채널 Plugin은 일반적인 채팅 작업을 위해 별도의 send/edit/react 도구를 따로 등록할 필요가 없습니다. OpenClaw는 코어에 하나의 공유 `message` 도구를 유지하고, 채널 Plugin은 그 뒤에서 채널별 탐색과 실행을 담당합니다.

현재 경계는 다음과 같습니다:

- 코어는 공유 `message` 도구 호스트, 프롬프트 연결, 세션/스레드 기록 관리, 실행 디스패치를 담당합니다
- 채널 Plugin은 범위가 지정된 작업 탐색, 기능 탐색, 채널별 스키마 조각을 담당합니다
- 채널 Plugin은 대화 ID가 스레드 ID를 인코딩하거나 상위 대화에서 상속되는 방식처럼, 프로바이더별 세션 대화 문법을 담당합니다
- 채널 Plugin은 자신의 action adapter를 통해 최종 작업을 실행합니다

채널 Plugin에서 SDK 표면은 `ChannelMessageActionAdapter.describeMessageTool(...)`입니다. 이 통합 탐색 호출을 통해 플러그인은 표시 가능한 작업, 기능, 스키마 기여를 함께 반환할 수 있으므로 이 요소들이 서로 어긋나지 않습니다.

채널별 message-tool 파라미터가 로컬 경로나 원격 미디어 URL 같은 미디어 소스를 포함하는 경우, 플러그인은 `describeMessageTool(...)`에서 `mediaSourceParams`도 반환해야 합니다. 코어는 이 명시적 목록을 사용해 plugin 소유 파라미터 이름을 하드코딩하지 않고 샌드박스 경로 정규화와 outbound 미디어 액세스 힌트를 적용합니다.
여기서는 채널 전체에 대한 하나의 평면 목록보다 작업 범위별 맵을 우선하세요. 그래야 프로필 전용 미디어 파라미터가 `send` 같은 관련 없는 작업에서 정규화되지 않습니다.

코어는 런타임 범위를 그 탐색 단계에 전달합니다. 중요한 필드는 다음과 같습니다:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- 신뢰된 인바운드 `requesterSenderId`

이것은 컨텍스트에 민감한 플러그인에 중요합니다. 채널은 코어 `message` 도구에 채널별 분기를 하드코딩하지 않고도, 활성 계정, 현재 방/스레드/메시지, 신뢰된 요청자 ID에 따라 메시지 작업을 숨기거나 노출할 수 있습니다.

이 때문에 embedded-runner 라우팅 변경은 여전히 플러그인 작업입니다. 러너는 현재 채팅/세션 ID를 plugin 탐색 경계로 전달해 공유 `message` 도구가 현재 턴에 맞는 채널 소유 표면을 노출하도록 해야 합니다.

채널 소유 실행 헬퍼의 경우, 번들 플러그인은 실행 런타임을 자체 확장 모듈 안에 유지해야 합니다. 코어는 더 이상 `src/agents/tools` 아래의 Discord, Slack, Telegram, WhatsApp 메시지 작업 런타임을 소유하지 않습니다.
우리는 별도의 `plugin-sdk/*-action-runtime` 하위 경로를 공개하지 않으며, 번들 플러그인은 자체 로컬 런타임 코드를 확장 소유 모듈에서 직접 import해야 합니다.

동일한 경계는 일반적인 프로바이더 명명 SDK seam에도 적용됩니다. 코어는 Slack, Discord, Signal, WhatsApp 또는 유사한 확장을 위한 채널별 편의 barrel을 import해서는 안 됩니다. 코어에 어떤 동작이 필요하면, 번들 플러그인의 자체 `api.ts` / `runtime-api.ts` barrel을 사용하거나 그 요구를 공유 SDK의 좁고 일반적인 기능으로 승격해야 합니다.

특히 poll의 경우 실행 경로는 두 가지입니다:

- `outbound.sendPoll`은 공통 poll 모델에 맞는 채널을 위한 공유 기준선입니다
- `actions.handleAction("poll")`은 채널별 poll 의미론이나 추가 poll 파라미터를 위한 선호 경로입니다

코어는 이제 plugin poll 디스패치가 작업을 거절한 뒤에야 공유 poll 파싱을 수행하므로, plugin 소유 poll 핸들러가 먼저 일반 poll 파서에 막히지 않고 채널별 poll 필드를 받을 수 있습니다.

전체 시작 시퀀스는 [로드 파이프라인](#load-pipeline)을 참고하세요.

## 기능 소유권 모델

OpenClaw는 기본 플러그인을 관련 없는 통합을 모아둔 잡동사니가 아니라, **회사** 또는 **기능**의 소유권 경계로 취급합니다.

이는 다음을 의미합니다:

- 회사 플러그인은 보통 그 회사의 OpenClaw 관련 표면 전체를 소유해야 합니다
- 기능 플러그인은 보통 자신이 도입하는 전체 기능 표면을 소유해야 합니다
- 채널은 프로바이더 동작을 그때그때 다시 구현하는 대신 공유 코어 기능을 사용해야 합니다

예시:

- 번들된 `openai` 플러그인은 OpenAI 모델 프로바이더 동작과 OpenAI
  음성 + 실시간 음성 + 미디어 이해 + 이미지 생성 동작을 소유합니다
- 번들된 `elevenlabs` 플러그인은 ElevenLabs 음성 동작을 소유합니다
- 번들된 `microsoft` 플러그인은 Microsoft 음성 동작을 소유합니다
- 번들된 `google` 플러그인은 Google 모델 프로바이더 동작과 Google
  미디어 이해 + 이미지 생성 + 웹 검색 동작을 소유합니다
- 번들된 `firecrawl` 플러그인은 Firecrawl 웹 가져오기 동작을 소유합니다
- 번들된 `minimax`, `mistral`, `moonshot`, `zai` 플러그인은 각각의
  미디어 이해 백엔드를 소유합니다
- 번들된 `qwen` 플러그인은 Qwen 텍스트 프로바이더 동작과
  미디어 이해 및 비디오 생성 동작을 소유합니다
- `voice-call` 플러그인은 기능 플러그인입니다. 통화 전송, 도구,
  CLI, 라우트, Twilio 미디어 스트림 브리징을 소유하지만, 벤더 플러그인을 직접 import하는 대신
  공유 음성 기능과 실시간 전사 및 실시간 음성 기능을 사용합니다

의도된 최종 상태는 다음과 같습니다:

- OpenAI는 텍스트 모델, 음성, 이미지, 미래의 비디오까지 아우르더라도 하나의 플러그인에 존재합니다
- 다른 벤더도 자체 표면 영역에 대해 동일하게 할 수 있습니다
- 채널은 어느 벤더 플러그인이 프로바이더를 소유하는지 신경 쓰지 않고, 코어가 노출하는 공유 기능 계약을 사용합니다

이것이 핵심 구분입니다:

- **plugin** = 소유권 경계
- **capability** = 여러 플러그인이 구현하거나 사용할 수 있는 코어 계약

따라서 OpenClaw가 비디오 같은 새 도메인을 추가할 때, 첫 번째 질문은
"어느 프로바이더가 비디오 처리를 하드코딩해야 하지?"가 아닙니다. 첫 번째 질문은 "코어 비디오 기능 계약은 무엇인가?"입니다.
그 계약이 존재하면, 벤더 플러그인은 그것에 대해 등록할 수 있고 채널/기능 플러그인은 이를 사용할 수 있습니다.

기능이 아직 존재하지 않는다면, 보통 올바른 접근은 다음과 같습니다:

1. 코어에서 누락된 기능을 정의합니다
2. 타입이 지정된 방식으로 plugin API/런타임을 통해 이를 노출합니다
3. 채널/기능을 그 기능에 맞게 연결합니다
4. 벤더 플러그인이 구현을 등록하도록 합니다

이렇게 하면 소유권을 명확하게 유지하면서도 단일 벤더나 일회성 플러그인별 코드 경로에 의존하는 코어 동작을 피할 수 있습니다.

### 기능 계층화

코드가 어디에 속해야 하는지 결정할 때 다음 사고 모델을 사용하세요:

- **코어 기능 계층**: 공유 오케스트레이션, 정책, 폴백, 설정
  병합 규칙, 전달 의미론, 타입 계약
- **벤더 플러그인 계층**: 벤더별 API, 인증, 모델 카탈로그, 음성
  합성, 이미지 생성, 미래의 비디오 백엔드, 사용량 엔드포인트
- **채널/기능 플러그인 계층**: 코어 기능을 사용하여 이를 표면에 제공하는
  Slack/Discord/voice-call 등의 통합

예를 들어, TTS는 다음 구조를 따릅니다:

- 코어는 응답 시점 TTS 정책, 폴백 순서, 기본 설정, 채널 전달을 소유합니다
- `openai`, `elevenlabs`, `microsoft`는 합성 구현을 소유합니다
- `voice-call`은 전화 통신 TTS 런타임 헬퍼를 사용합니다

같은 패턴을 미래의 기능에도 우선 적용해야 합니다.

### 다중 기능 회사 플러그인 예시

회사 플러그인은 외부에서 봤을 때 일관된 하나의 단위처럼 느껴져야 합니다. OpenClaw에 모델, 음성, 실시간 전사, 실시간 음성, 미디어 이해, 이미지 생성, 비디오 생성, 웹 가져오기, 웹 검색에 대한 공유 계약이 있다면,
벤더는 자신의 모든 표면을 한 곳에서 소유할 수 있습니다:

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

정확한 헬퍼 이름이 무엇인지는 중요하지 않습니다. 중요한 것은 구조입니다:

- 하나의 플러그인이 벤더 표면을 소유합니다
- 코어는 여전히 기능 계약을 소유합니다
- 채널과 기능 플러그인은 벤더 코드가 아니라 `api.runtime.*` 헬퍼를 사용합니다
- 계약 테스트는 플러그인이 자신이 소유한다고 주장하는 기능을 등록했는지 검증할 수 있습니다

### 기능 예시: 비디오 이해

OpenClaw는 이미 이미지/오디오/비디오 이해를 하나의 공유 기능으로 취급합니다. 동일한 소유권 모델이 여기에도 적용됩니다:

1. 코어가 미디어 이해 계약을 정의합니다
2. 벤더 플러그인은 해당하는 경우 `describeImage`, `transcribeAudio`,
   `describeVideo`를 등록합니다
3. 채널과 기능 플러그인은 벤더 코드에 직접 연결하는 대신 공유 코어 동작을 사용합니다

이렇게 하면 특정 프로바이더의 비디오 가정을 코어에 내장하지 않게 됩니다. 플러그인은 벤더 표면을 소유하고, 코어는 기능 계약과 폴백 동작을 소유합니다.

비디오 생성도 이미 같은 순서를 따릅니다. 코어가 타입이 지정된
기능 계약과 런타임 헬퍼를 소유하고, 벤더 플러그인은 이에 대해
`api.registerVideoGenerationProvider(...)` 구현을 등록합니다.

구체적인 출시 체크리스트가 필요하신가요? [기능 Cookbook](/ko/plugins/architecture)을
참고하세요.

## 계약 및 적용

플러그인 API 표면은 의도적으로 `OpenClawPluginApi`에 타입을 지정하고 중앙화되어 있습니다.
이 계약은 지원되는 등록 지점과 플러그인이 의존할 수 있는 런타임 헬퍼를 정의합니다.

이것이 중요한 이유:

- 플러그인 작성자는 하나의 안정적인 내부 표준을 갖게 됩니다
- 코어는 두 플러그인이 동일한 프로바이더 ID를 등록하는 것과 같은 중복 소유를 거부할 수 있습니다
- 시작 시 잘못된 등록에 대해 실행 가능한 진단을 표시할 수 있습니다
- 계약 테스트는 번들 플러그인 소유권을 강제하고 조용한 드리프트를 방지할 수 있습니다

적용에는 두 계층이 있습니다:

1. **런타임 등록 적용**
   플러그인 레지스트리는 플러그인이 로드될 때 등록을 검증합니다. 예:
   중복 프로바이더 ID, 중복 음성 프로바이더 ID, 잘못된
   등록은 정의되지 않은 동작 대신 플러그인 진단을 생성합니다.
2. **계약 테스트**
   번들 플러그인은 테스트 실행 중 계약 레지스트리에 캡처되므로
   OpenClaw는 소유권을 명시적으로 검증할 수 있습니다. 현재 이는 모델
   프로바이더, 음성 프로바이더, 웹 검색 프로바이더, 번들 등록
   소유권에 사용됩니다.

실질적인 효과는 OpenClaw가 어떤 플러그인이 어떤 표면을 소유하는지를
사전에 알고 있다는 점입니다. 덕분에 소유권이 암묵적이지 않고 선언되고, 타입이 지정되며, 테스트 가능하기 때문에 코어와 채널이 자연스럽게 조합될 수 있습니다.

### 계약에 포함되어야 하는 것

좋은 플러그인 계약은 다음과 같습니다:

- 타입이 지정되어 있음
- 작음
- 기능별로 구체적임
- 코어가 소유함
- 여러 플러그인이 재사용 가능함
- 채널/기능이 벤더 지식 없이 사용할 수 있음

나쁜 플러그인 계약은 다음과 같습니다:

- 코어에 숨겨진 벤더별 정책
- 레지스트리를 우회하는 일회성 플러그인 탈출구
- 채널 코드가 벤더 구현에 직접 접근함
- `OpenClawPluginApi` 또는
  `api.runtime`의 일부가 아닌 임시 런타임 객체

확신이 서지 않으면 추상화 수준을 높이세요. 먼저 기능을 정의한 다음,
플러그인이 여기에 연결되도록 하세요.

## 실행 모델

기본 OpenClaw 플러그인은 Gateway와 **프로세스 내부에서** 실행됩니다. 샌드박스 처리되지 않습니다.
로드된 기본 플러그인은 코어 코드와 동일한 프로세스 수준 신뢰 경계를 가집니다.

의미하는 바는 다음과 같습니다:

- 기본 플러그인은 도구, 네트워크 핸들러, 훅, 서비스를 등록할 수 있습니다
- 기본 플러그인 버그는 gateway를 크래시시키거나 불안정하게 만들 수 있습니다
- 악의적인 기본 플러그인은 OpenClaw 프로세스 내부에서의 임의 코드 실행과 동일합니다

호환 가능한 번들은 OpenClaw가 현재 이를 메타데이터/콘텐츠 팩으로 취급하기 때문에 기본적으로 더 안전합니다.
현재 릴리스에서 이것은 주로 번들된
Skills를 의미합니다.

번들되지 않은 플러그인에는 허용 목록과 명시적인 설치/로드 경로를 사용하세요. 워크스페이스 플러그인은 프로덕션 기본값이 아니라 개발 시점 코드로 취급하세요.

번들된 워크스페이스 패키지 이름의 경우, 플러그인 ID가 npm
이름에 고정되도록 유지하세요: 기본적으로 `@openclaw/<id>`, 또는
패키지가 의도적으로 더 좁은 플러그인 역할을 노출하는 경우
`-provider`, `-plugin`, `-speech`, `-sandbox`, `-media-understanding` 같은 승인된 타입 접미사를 사용합니다.

중요한 신뢰 참고 사항:

- `plugins.allow`는 소스 출처가 아니라 **plugin id**를 신뢰합니다.
- 번들 플러그인과 동일한 ID를 가진 워크스페이스 플러그인은 그 워크스페이스 플러그인이 활성화/허용 목록에 있으면 의도적으로 번들 사본을 가립니다.
- 이는 정상적이며 로컬 개발, 패치 테스트, 핫픽스에 유용합니다.

## export 경계

OpenClaw는 구현 편의성이 아니라 기능을 export합니다.

기능 등록은 공개 상태로 유지하세요. 계약이 아닌 헬퍼 export는 줄이세요:

- 번들 플러그인 전용 헬퍼 하위 경로
- 공개 API로 의도되지 않은 런타임 플러밍 하위 경로
- 벤더별 편의 헬퍼
- 구현 세부 사항인 설정/온보딩 헬퍼

일부 번들 플러그인 헬퍼 하위 경로는 호환성과 번들 플러그인 유지보수를 위해
생성된 SDK export 맵에 여전히 남아 있습니다. 현재 예로는
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup`, 그리고 여러 `plugin-sdk/matrix*` seam이 있습니다. 이를
새로운 서드파티 플러그인에 권장되는 SDK 패턴이 아니라 예약된 구현 세부 export로 취급하세요.

## 로드 파이프라인

시작 시 OpenClaw는 대략 다음을 수행합니다:

1. 후보 플러그인 루트를 탐색합니다
2. 기본 또는 호환 가능한 번들 매니페스트와 패키지 메타데이터를 읽습니다
3. 안전하지 않은 후보를 거부합니다
4. plugin 설정을 정규화합니다 (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. 각 후보의 활성화 여부를 결정합니다
6. 활성화된 기본 모듈을 jiti로 로드합니다
7. 기본 `register(api)`(또는 레거시 별칭인 `activate(api)`) 훅을 호출하고 플러그인 레지스트리에 등록 항목을 수집합니다
8. 명령/런타임 표면에 레지스트리를 노출합니다

<Note>
`activate`는 `register`의 레거시 별칭입니다 — 로더는 존재하는 것을 해석하여 (`def.register ?? def.activate`) 같은 지점에서 호출합니다. 모든 번들 플러그인은 `register`를 사용합니다. 새 플러그인에는 `register`를 우선 사용하세요.
</Note>

안전 게이트는 런타임 실행 **이전**에 발생합니다. 다음과 같은 경우 후보는 차단됩니다.
엔트리가 플러그인 루트를 벗어나는 경우, 경로가 world-writable인 경우, 또는 번들되지 않은 플러그인에 대해 경로 소유권이 의심스러워 보이는 경우입니다.

### 매니페스트 우선 동작

매니페스트는 제어 평면의 단일 진실 공급원입니다. OpenClaw는 이를 사용해 다음을 수행합니다:

- 플러그인 식별
- 선언된 채널/Skills/설정 스키마 또는 번들 기능 탐색
- `plugins.entries.<id>.config` 검증
- Control UI 라벨/플레이스홀더 보강
- 설치/카탈로그 메타데이터 표시
- plugin 런타임을 로드하지 않고도 가벼운 활성화 및 설정 descriptor 유지

기본 플러그인의 경우, 런타임 모듈은 데이터 평면 부분입니다. 실제 동작인 훅, 도구, 명령, 프로바이더 흐름 등을 등록합니다.

선택적 매니페스트 `activation` 및 `setup` 블록은 제어 평면에 남습니다.
이들은 활성화 계획 및 설정 탐색을 위한 메타데이터 전용 descriptor이며,
런타임 등록, `register(...)`, `setupEntry`를 대체하지 않습니다.
최초의 실제 활성화 소비자는 이제 매니페스트 명령, 채널, 프로바이더 힌트를 사용해
더 넓은 레지스트리 구체화 전에 플러그인 로드를 좁힙니다:

- CLI 로드는 요청된 기본 명령을 소유한 플러그인으로 좁혀집니다
- 채널 설정/플러그인 해결은 요청된
  채널 ID를 소유한 플러그인으로 좁혀집니다
- 명시적 프로바이더 설정/런타임 해결은 요청된 프로바이더 ID를 소유한 플러그인으로 좁혀집니다

설정 탐색은 이제 먼저 `setup.providers` 및 `setup.cliBackends` 같은 descriptor 소유 ID를 우선 사용해 후보 플러그인을 좁히고, 여전히 설정 시점 런타임 훅이 필요한 플러그인에 대해서만 `setup-api`로 폴백합니다. 둘 이상의 탐지된 플러그인이 동일한 정규화된 설정 프로바이더 또는 CLI 백엔드 ID를 주장하면, 설정 조회는 탐색 순서에 의존하지 않고 모호한 소유자를 거부합니다.

### 로더가 캐시하는 것

OpenClaw는 다음에 대해 짧은 수명의 프로세스 내 캐시를 유지합니다:

- 탐색 결과
- 매니페스트 레지스트리 데이터
- 로드된 플러그인 레지스트리

이 캐시는 급격한 시작 부하와 반복 명령 오버헤드를 줄여줍니다. 이를 영속 저장소가 아니라 수명이 짧은 성능 캐시로 생각하는 것이 안전합니다.

성능 참고 사항:

- 이 캐시를 비활성화하려면 `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` 또는
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1`을 설정하세요.
- 캐시 기간은 `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` 및
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`로 조정할 수 있습니다.

## 레지스트리 모델

로드된 플러그인은 임의의 코어 전역 상태를 직접 변경하지 않습니다. 대신 중앙 플러그인 레지스트리에 등록합니다.

레지스트리는 다음을 추적합니다:

- 플러그인 레코드(정체성, 소스, 출처, 상태, 진단)
- 도구
- 레거시 훅 및 타입 지정 훅
- 채널
- 프로바이더
- Gateway RPC 핸들러
- HTTP 라우트
- CLI 등록기
- 백그라운드 서비스
- 플러그인 소유 명령

그런 다음 코어 기능은 플러그인 모듈과 직접 통신하는 대신 이 레지스트리에서 읽습니다. 이렇게 하면 로딩 방향이 한쪽으로 유지됩니다:

- 플러그인 모듈 -> 레지스트리 등록
- 코어 런타임 -> 레지스트리 소비

이 분리는 유지보수성 측면에서 중요합니다. 이는 대부분의 코어 표면이 "플러그인 모듈마다 특수 처리"가 아니라 "레지스트리를 읽기"라는 하나의 통합 지점만 필요하다는 뜻입니다.

## 대화 바인딩 콜백

대화를 바인딩하는 플러그인은 승인이 해결되었을 때 반응할 수 있습니다.

바인드 요청이 승인되거나 거부된 후 콜백을 받으려면 `api.onConversationBindingResolved(...)`를 사용하세요:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // 이제 이 plugin + 대화에 대한 바인딩이 존재합니다.
        console.log(event.binding?.conversationId);
        return;
      }

      // 요청이 거부되었습니다. 로컬 대기 상태를 모두 정리합니다.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

콜백 페이로드 필드:

- `status`: `"approved"` 또는 `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` 또는 `"deny"`
- `binding`: 승인된 요청에 대한 해결된 바인딩
- `request`: 원본 요청 요약, 분리 힌트, 발신자 ID 및
  대화 메타데이터

이 콜백은 알림 전용입니다. 누가 대화를 바인딩할 수 있는지는 바꾸지 않으며, 코어 승인 처리가 끝난 뒤에 실행됩니다.

## 프로바이더 런타임 훅

이제 프로바이더 플러그인에는 두 개의 계층이 있습니다:

- 매니페스트 메타데이터: 런타임 로드 전에 가벼운 프로바이더 환경 인증 조회를 위한 `providerAuthEnvVars`, 인증을 공유하는 프로바이더 변형을 위한 `providerAuthAliases`, 런타임 로드 전에 가벼운 채널 환경/설정 조회를 위한 `channelEnvVars`, 그리고 런타임 로드 전에 가벼운 온보딩/인증 선택 라벨 및 CLI 플래그 메타데이터를 위한 `providerAuthChoices`
- 설정 시점 훅: `catalog` / 레거시 `discovery` 및 `applyConfigDefaults`
- 런타임 훅: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw는 여전히 일반적인 에이전트 루프, 장애 조치, 전사 처리, 도구 정책을 소유합니다. 이러한 훅은 전체 커스텀 추론 전송이 없어도 프로바이더별 동작을 확장할 수 있는 표면입니다.

프로바이더에 런타임을 로드하지 않고도 일반 인증/상태/모델 선택기 경로에서 확인해야 하는 환경 기반 자격 증명이 있다면 매니페스트 `providerAuthEnvVars`를 사용하세요. 하나의 프로바이더 ID가 다른 프로바이더 ID의 환경 변수, 인증 프로필, 설정 기반 인증, API 키 온보딩 선택을 재사용해야 한다면 매니페스트 `providerAuthAliases`를 사용하세요. 온보딩/인증 선택 CLI 표면이 프로바이더 런타임을 로드하지 않고도 프로바이더의 선택 ID, 그룹 라벨, 단일 플래그 인증 연결을 알아야 한다면 매니페스트 `providerAuthChoices`를 사용하세요. 프로바이더 런타임의 `envVars`는 온보딩 라벨 또는 OAuth client-id/client-secret 설정 변수 같은 운영자 대상 힌트에 유지하세요.

채널에 런타임을 로드하지 않고도 일반 셸 환경 폴백, config/status 검사, 설정 프롬프트에서 확인해야 하는 환경 기반 인증 또는 설정이 있다면 매니페스트 `channelEnvVars`를 사용하세요.

### 훅 순서 및 사용법

모델/프로바이더 플러그인의 경우, OpenClaw는 대략 다음 순서로 훅을 호출합니다.
"사용 시점" 열은 빠른 판단 가이드입니다.

| #   | 훅                                | 수행하는 일                                                                                                    | 사용 시점                                                                                                                                   |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | `models.json` 생성 중 프로바이더 설정을 `models.providers`에 게시                                             | 프로바이더가 카탈로그 또는 기본 base URL을 소유하는 경우                                                                                    |
| 2   | `applyConfigDefaults`             | 설정 구체화 중 프로바이더 소유 전역 설정 기본값 적용                                                          | 기본값이 인증 모드, 환경 또는 프로바이더 모델 계열 의미론에 따라 달라지는 경우                                                             |
| --  | _(내장 모델 조회)_                | OpenClaw가 먼저 일반 레지스트리/카탈로그 경로를 시도함                                                        | _(플러그인 훅 아님)_                                                                                                                        |
| 3   | `normalizeModelId`                | 조회 전에 레거시 또는 프리뷰 모델 ID 별칭을 정규화                                                            | 프로바이더가 정식 모델 해석 전에 별칭 정리를 소유하는 경우                                                                                 |
| 4   | `normalizeTransport`              | 일반 모델 조립 전에 프로바이더 계열의 `api` / `baseUrl`을 정규화                                              | 프로바이더가 동일한 전송 계열 내 커스텀 프로바이더 ID에 대한 전송 정리를 소유하는 경우                                                     |
| 5   | `normalizeConfig`                 | 런타임/프로바이더 해석 전에 `models.providers.<id>` 정규화                                                    | 프로바이더에 플러그인과 함께 있어야 하는 설정 정리가 필요한 경우; 번들된 Google 계열 헬퍼는 지원되는 Google 설정 항목도 보완합니다        |
| 6   | `applyNativeStreamingUsageCompat` | 설정 프로바이더에 기본 스트리밍 사용량 호환성 재작성 적용                                                     | 프로바이더가 엔드포인트 기반 기본 스트리밍 사용량 메타데이터 수정이 필요한 경우                                                             |
| 7   | `resolveConfigApiKey`             | 런타임 인증 로드 전에 설정 프로바이더의 env-marker 인증 해석                                                  | 프로바이더가 프로바이더 소유 env-marker API 키 해석을 가지는 경우; `amazon-bedrock`도 여기서 내장 AWS env-marker 해석기를 가집니다       |
| 8   | `resolveSyntheticAuth`            | 평문을 저장하지 않고 로컬/셀프 호스팅 또는 설정 기반 인증 노출                                                | 프로바이더가 합성/로컬 자격 증명 마커로 동작할 수 있는 경우                                                                                 |
| 9   | `resolveExternalAuthProfiles`     | 프로바이더 소유 외부 인증 프로필을 오버레이함; 기본 `persistence`는 CLI/앱 소유 자격 증명에 대해 `runtime-only` | 프로바이더가 복사된 리프레시 토큰을 저장하지 않고 외부 인증 자격 증명을 재사용하는 경우                                                     |
| 10  | `shouldDeferSyntheticProfileAuth` | 저장된 합성 프로필 플레이스홀더의 우선순위를 env/config 기반 인증보다 낮춤                                    | 프로바이더가 우선권을 가져서는 안 되는 합성 플레이스홀더 프로필을 저장하는 경우                                                             |
| 11  | `resolveDynamicModel`             | 아직 로컬 레지스트리에 없는 프로바이더 소유 모델 ID에 대한 동기 폴백                                          | 프로바이더가 임의의 업스트림 모델 ID를 허용하는 경우                                                                                        |
| 12  | `prepareDynamicModel`             | 비동기 워밍업 후 `resolveDynamicModel`을 다시 실행                                                            | 프로바이더가 알 수 없는 ID를 해석하기 전에 네트워크 메타데이터가 필요한 경우                                                                |
| 13  | `normalizeResolvedModel`          | embedded runner가 해석된 모델을 사용하기 전 마지막 재작성                                                     | 프로바이더가 전송 재작성이 필요하지만 여전히 코어 전송을 사용하는 경우                                                                      |
| 14  | `contributeResolvedModelCompat`   | 다른 호환 가능한 전송 뒤에 있는 벤더 모델에 대한 호환성 플래그 기여                                           | 프로바이더를 직접 가져오지 않으면서 프록시 전송에서 자체 모델을 인식하는 경우                                                               |
| 15  | `capabilities`                    | 공유 코어 로직에서 사용하는 프로바이더 소유 전사/도구 메타데이터                                              | 프로바이더가 전사/프로바이더 계열별 특수 동작을 필요로 하는 경우                                                                             |
| 16  | `normalizeToolSchemas`            | embedded runner가 도구 스키마를 보기 전에 정규화                                                              | 프로바이더가 전송 계열별 스키마 정리가 필요한 경우                                                                                          |
| 17  | `inspectToolSchemas`              | 정규화 후 프로바이더 소유 스키마 진단 노출                                                                    | 코어에 프로바이더별 규칙을 가르치지 않고도 프로바이더가 키워드 경고를 제공하려는 경우                                                       |
| 18  | `resolveReasoningOutputMode`      | 기본 vs 태그 기반 추론 출력 계약 선택                                                                         | 프로바이더가 기본 필드 대신 태그 기반 추론/최종 출력을 필요로 하는 경우                                                                     |
| 19  | `prepareExtraParams`              | 일반 스트림 옵션 래퍼 전에 요청 파라미터 정규화                                                               | 프로바이더가 기본 요청 파라미터 또는 프로바이더별 파라미터 정리가 필요한 경우                                                               |
| 20  | `createStreamFn`                  | 일반 스트림 경로를 커스텀 전송으로 완전히 대체                                                                | 프로바이더가 단순 래퍼가 아닌 커스텀 와이어 프로토콜을 필요로 하는 경우                                                                     |
| 21  | `wrapStreamFn`                    | 일반 래퍼가 적용된 후의 스트림 래퍼                                                                            | 프로바이더가 커스텀 전송 없이 요청 헤더/본문/모델 호환성 래퍼를 필요로 하는 경우                                                            |
| 22  | `resolveTransportTurnState`       | 기본 turn별 전송 헤더 또는 메타데이터 첨부                                                                    | 프로바이더가 일반 전송이 프로바이더 기본 turn 식별자를 보내도록 하려는 경우                                                                 |
| 23  | `resolveWebSocketSessionPolicy`   | 기본 WebSocket 헤더 또는 세션 쿨다운 정책 첨부                                                                | 프로바이더가 일반 WS 전송에서 세션 헤더 또는 폴백 정책을 조정하려는 경우                                                                    |
| 24  | `formatApiKey`                    | 인증 프로필 포매터: 저장된 프로필이 런타임 `apiKey` 문자열이 됨                                               | 프로바이더가 추가 인증 메타데이터를 저장하고 커스텀 런타임 토큰 형태가 필요한 경우                                                          |
| 25  | `refreshOAuth`                    | 커스텀 리프레시 엔드포인트 또는 리프레시 실패 정책을 위한 OAuth 리프레시 재정의                              | 프로바이더가 공유 `pi-ai` 리프레셔에 맞지 않는 경우                                                                                         |
| 26  | `buildAuthDoctorHint`             | OAuth 리프레시 실패 시 추가되는 복구 힌트                                                                     | 프로바이더가 리프레시 실패 후 프로바이더 소유 인증 복구 가이드를 필요로 하는 경우                                                           |
| 27  | `matchesContextOverflowError`     | 프로바이더 소유 컨텍스트 창 초과 매처                                                                         | 프로바이더가 일반 휴리스틱으로는 놓치는 원시 overflow 오류를 가지는 경우                                                                    |
| 28  | `classifyFailoverReason`          | 프로바이더 소유 장애 조치 이유 분류                                                                           | 프로바이더가 원시 API/전송 오류를 rate-limit/overload 등으로 매핑할 수 있는 경우                                                            |
| 29  | `isCacheTtlEligible`              | 프록시/백홀 프로바이더용 프롬프트 캐시 정책                                                                   | 프로바이더가 프록시별 캐시 TTL 게이팅을 필요로 하는 경우                                                                                    |
| 30  | `buildMissingAuthMessage`         | 일반 인증 누락 복구 메시지 대체                                                                               | 프로바이더가 프로바이더별 인증 누락 복구 힌트를 필요로 하는 경우                                                                            |
| 31  | `suppressBuiltInModel`            | 오래된 업스트림 모델 숨김 및 선택적 사용자 대상 오류 힌트                                                     | 프로바이더가 오래된 업스트림 행을 숨기거나 벤더 힌트로 대체해야 하는 경우                                                                   |
| 32  | `augmentModelCatalog`             | 탐색 후 추가되는 합성/최종 카탈로그 행                                                                        | 프로바이더가 `models list` 및 선택기에서 합성 forward-compat 행을 필요로 하는 경우                                                         |
| 33  | `isBinaryThinking`                | 이진 사고 프로바이더용 on/off 추론 토글                                                                       | 프로바이더가 이진 사고 on/off만 노출하는 경우                                                                                               |
| 34  | `supportsXHighThinking`           | 선택된 모델에 대한 `xhigh` 추론 지원                                                                          | 프로바이더가 일부 모델에서만 `xhigh`를 제공하려는 경우                                                                                      |
| 35  | `resolveDefaultThinkingLevel`     | 특정 모델 계열에 대한 기본 `/think` 수준                                                                      | 프로바이더가 모델 계열의 기본 `/think` 정책을 소유하는 경우                                                                                 |
| 36  | `isModernModelRef`                | 라이브 프로필 필터 및 스모크 선택을 위한 최신 모델 매처                                                       | 프로바이더가 라이브/스모크 선호 모델 매칭을 소유하는 경우                                                                                   |
| 37  | `prepareRuntimeAuth`              | 추론 직전에 구성된 자격 증명을 실제 런타임 토큰/키로 교환                                                     | 프로바이더가 토큰 교환 또는 수명이 짧은 요청 자격 증명을 필요로 하는 경우                                                                   |
| 38  | `resolveUsageAuth`                | `/usage` 및 관련 상태 표면에 대한 사용량/청구 자격 증명 해석                                                  | 프로바이더가 커스텀 사용량/할당량 토큰 파싱 또는 다른 사용량 자격 증명을 필요로 하는 경우                                                  |
| 39  | `fetchUsageSnapshot`              | 인증이 해석된 후 프로바이더별 사용량/할당량 스냅샷을 가져오고 정규화                                           | 프로바이더가 프로바이더별 사용량 엔드포인트 또는 페이로드 파서를 필요로 하는 경우                                                          |
| 40  | `createEmbeddingProvider`         | 메모리/검색을 위한 프로바이더 소유 임베딩 어댑터 구성                                                          | 메모리 임베딩 동작이 프로바이더 플러그인에 속하는 경우                                                                                     |
| 41  | `buildReplayPolicy`               | 프로바이더의 전사 처리를 제어하는 리플레이 정책 반환                                                           | 프로바이더가 커스텀 전사 정책(예: thinking 블록 제거)을 필요로 하는 경우                                                                    |
| 42  | `sanitizeReplayHistory`           | 일반 전사 정리 후 리플레이 이력 재작성                                                                         | 프로바이더가 공유 Compaction 헬퍼를 넘어서는 프로바이더별 리플레이 재작성을 필요로 하는 경우                                               |
| 43  | `validateReplayTurns`             | embedded runner 이전의 최종 리플레이 turn 검증 또는 형태 재구성                                                | 프로바이더 전송이 일반 정리 후 더 엄격한 turn 검증을 필요로 하는 경우                                                                       |
| 44  | `onModelSelected`                 | 프로바이더 소유 후처리 선택 부작용 실행                                                                        | 모델이 활성화될 때 프로바이더가 텔레메트리 또는 프로바이더 소유 상태를 필요로 하는 경우                                                     |

`normalizeModelId`, `normalizeTransport`, `normalizeConfig`는 먼저
일치하는 프로바이더 플러그인을 확인한 뒤, 실제로 모델 ID나 전송/설정을 변경하는 훅 가능 프로바이더 플러그인이 나올 때까지 다른 플러그인으로 순차적으로 넘어갑니다. 이렇게 하면 호출자가 어떤 번들 플러그인이 재작성을 소유하는지 알 필요 없이 별칭/호환성 프로바이더 shim이 계속 동작합니다. 어떤 프로바이더 훅도 지원되는 Google 계열 설정 항목을 재작성하지 않으면, 번들된 Google 설정 정규화기가 여전히 해당 호환성 정리를 적용합니다.

프로바이더에 완전히 커스텀 와이어 프로토콜이나 커스텀 요청 실행기가 필요하다면, 그것은 다른 종류의 확장입니다. 이러한 훅은 OpenClaw의 일반 추론 루프에서 계속 실행되는 프로바이더 동작을 위한 것입니다.

### 프로바이더 예시

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### 내장 예시

- Anthropic은 `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `wrapStreamFn`을 사용합니다. 이는 Claude 4.6 forward-compat,
  프로바이더 계열 힌트, 인증 복구 가이드, 사용량 엔드포인트 통합,
  프롬프트 캐시 적격성, 인증 인지 설정 기본값, Claude
  기본/적응형 thinking 정책, 베타 헤더,
  `/fast` / `serviceTier`, `context1m`을 위한 Anthropic 전용 스트림 형태 조정을 소유하기 때문입니다.
- Anthropic의 Claude 전용 스트림 헬퍼는 현재 번들 플러그인의 자체
  공개 `api.ts` / `contract-api.ts` seam에 남아 있습니다. 해당 패키지 표면은
  하나의 프로바이더 베타 헤더 규칙을 기준으로 일반 SDK를 넓히는 대신
  `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier`, 그리고 하위 수준
  Anthropic 래퍼 빌더를 export합니다.
- OpenAI는 `resolveDynamicModel`, `normalizeResolvedModel`,
  `capabilities`와 함께 `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking`, `isModernModelRef`를 사용합니다.
  이는 GPT-5.4 forward-compat, 직접 OpenAI
  `openai-completions` -> `openai-responses` 정규화, Codex 인지 인증
  힌트, Spark 억제, 합성 OpenAI 목록 행, GPT-5 thinking /
  라이브 모델 정책을 소유하기 때문입니다. `openai-responses-defaults` 스트림 계열은
  attribution 헤더,
  `/fast`/`serviceTier`, 텍스트 verbosity, 기본 Codex 웹 검색,
  reasoning-compat 페이로드 형태 조정, Responses 컨텍스트 관리를 위한
  공유 기본 OpenAI Responses 래퍼를 소유합니다.
- OpenRouter는 `catalog`와 함께 `resolveDynamicModel`,
  `prepareDynamicModel`을 사용합니다. 이 프로바이더는 패스스루이므로
  OpenClaw의 정적 카탈로그가 업데이트되기 전에 새 모델 ID를 노출할 수 있기 때문입니다. 또한
  프로바이더별 요청 헤더, 라우팅 메타데이터, reasoning 패치,
  프롬프트 캐시 정책이 코어로 들어오지 않도록 `capabilities`, `wrapStreamFn`,
  `isCacheTtlEligible`도 사용합니다. 리플레이 정책은
  `passthrough-gemini` 계열에서 오며, `openrouter-thinking` 스트림 계열은
  프록시 reasoning 주입과 지원되지 않는 모델 / `auto` 건너뛰기를 소유합니다.
- GitHub Copilot은 `catalog`, `auth`, `resolveDynamicModel`,
  `capabilities`와 함께 `prepareRuntimeAuth`, `fetchUsageSnapshot`을 사용합니다.
  이는 프로바이더 소유 장치 로그인, 모델 폴백 동작, Claude 전사 특수 동작,
  GitHub 토큰 -> Copilot 토큰 교환, 프로바이더 소유 사용량 엔드포인트가 필요하기 때문입니다.
- OpenAI Codex는 `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth`, `augmentModelCatalog`와 함께
  `prepareExtraParams`, `resolveUsageAuth`, `fetchUsageSnapshot`을 사용합니다.
  이는 여전히 코어 OpenAI 전송에서 실행되지만 전송/base URL
  정규화, OAuth 리프레시 폴백 정책, 기본 전송 선택,
  합성 Codex 카탈로그 행, ChatGPT 사용량 엔드포인트 통합을 소유하기 때문입니다.
  이 프로바이더는 직접 OpenAI와 동일한 `openai-responses-defaults` 스트림 계열을 공유합니다.
- Google AI Studio와 Gemini CLI OAuth는 `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn`, `isModernModelRef`를 사용합니다. 이는
  `google-gemini` 리플레이 계열이 Gemini 3.1 forward-compat 폴백,
  기본 Gemini 리플레이 검증, bootstrap 리플레이 정리, 태그 기반
  reasoning-output 모드, 최신 모델 매칭을 소유하고,
  `google-thinking` 스트림 계열이 Gemini thinking 페이로드 정규화를 소유하기 때문입니다.
  Gemini CLI OAuth는 토큰 형식화, 토큰 파싱, 할당량 엔드포인트
  연결을 위해 `formatApiKey`, `resolveUsageAuth`,
  `fetchUsageSnapshot`도 사용합니다.
- Anthropic Vertex는
  `anthropic-by-model` 리플레이 계열을 통해 `buildReplayPolicy`를 사용하므로
  Claude 전용 리플레이 정리가 모든 `anthropic-messages` 전송이 아니라 Claude ID에만 범위가 제한됩니다.
- Amazon Bedrock은 `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `resolveDefaultThinkingLevel`을 사용합니다. 이는
  Anthropic-on-Bedrock 트래픽에 대한 Bedrock 전용 throttle/not-ready/context-overflow 오류 분류를 소유하기 때문입니다.
  리플레이 정책은 여전히 동일한 Claude 전용 `anthropic-by-model` 가드를 공유합니다.
- OpenRouter, Kilocode, Opencode, Opencode Go는 `buildReplayPolicy`를
  `passthrough-gemini` 리플레이 계열을 통해 사용합니다. 이는 이들이 Gemini
  모델을 OpenAI 호환 전송을 통해 프록시하고, 기본 Gemini 리플레이 검증이나
  bootstrap 재작성 없이 Gemini thought-signature 정리가 필요하기 때문입니다.
- MiniMax는 `buildReplayPolicy`를
  `hybrid-anthropic-openai` 리플레이 계열을 통해 사용합니다. 이는 하나의 프로바이더가 Anthropic-message와 OpenAI 호환 의미론을 모두 소유하기 때문입니다.
  Anthropic 쪽에서는 Claude 전용 thinking 블록 제거를 유지하면서 reasoning
  출력 모드를 다시 기본값으로 재정의하고, `minimax-fast-mode` 스트림 계열은
  공유 스트림 경로에서 fast-mode 모델 재작성을 소유합니다.
- Moonshot은 `catalog`와 `wrapStreamFn`을 사용합니다. 여전히 공유
  OpenAI 전송을 사용하지만 프로바이더 소유 thinking 페이로드 정규화가 필요하기 때문입니다.
  `moonshot-thinking` 스트림 계열은 설정과 `/think` 상태를 해당 프로바이더의
  기본 이진 thinking 페이로드에 매핑합니다.
- Kilocode는 `catalog`, `capabilities`, `wrapStreamFn`,
  `isCacheTtlEligible`를 사용합니다. 이는 프로바이더 소유 요청 헤더,
  reasoning 페이로드 정규화, Gemini 전사 힌트, Anthropic
  캐시 TTL 게이팅이 필요하기 때문입니다. `kilocode-thinking` 스트림 계열은
  `kilo/auto` 및 명시적 reasoning 페이로드를 지원하지 않는 기타 프록시 모델 ID를 건너뛰면서
  공유 프록시 스트림 경로에서 Kilo thinking 주입을 유지합니다.
- Z.AI는 `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth`, `fetchUsageSnapshot`을 사용합니다. 이는 GLM-5 폴백,
  `tool_stream` 기본값, 이진 thinking UX, 최신 모델 매칭,
  사용량 인증 + 할당량 조회를 모두 소유하기 때문입니다. `tool-stream-default-on` 스트림 계열은
  기본 활성 `tool_stream` 래퍼가 프로바이더별 수작업 glue에 들어가지 않도록 유지합니다.
- xAI는 `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel`, `isModernModelRef`를 사용합니다.
  이는 기본 xAI Responses 전송 정규화, Grok fast-mode
  별칭 재작성, 기본 `tool_stream`, strict-tool / reasoning-payload
  정리, 플러그인 소유 도구를 위한 폴백 인증 재사용, forward-compat Grok
  모델 해석, xAI 도구 스키마
  프로필, 지원되지 않는 스키마 키워드, 기본 `web_search`, HTML 엔티티
  도구 호출 인자 디코딩과 같은 프로바이더 소유 호환성 패치를 소유하기 때문입니다.
- Mistral, OpenCode Zen, OpenCode Go는 전사/도구 특수 동작이 코어로 들어오지 않도록
  `capabilities`만 사용합니다.
- `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway`, `volcengine` 같은
  카탈로그 전용 번들 프로바이더는 `catalog`만 사용합니다.
- Qwen은 텍스트 프로바이더용 `catalog`와 멀티모달 표면용 공유
  미디어 이해 및 비디오 생성 등록을 사용합니다.
- MiniMax와 Xiaomi는 추론이 여전히 공유 전송을 통해 실행되더라도 `/usage`
  동작이 플러그인 소유이기 때문에 `catalog`와 사용량 훅을 함께 사용합니다.

## 런타임 헬퍼

플러그인은 `api.runtime`를 통해 선택된 코어 헬퍼에 접근할 수 있습니다. TTS의 경우:

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

참고:

- `textToSpeech`는 파일/음성 메모 표면용 일반 코어 TTS 출력 페이로드를 반환합니다.
- 코어 `messages.tts` 설정과 프로바이더 선택을 사용합니다.
- PCM 오디오 버퍼 + 샘플레이트를 반환합니다. 플러그인은 프로바이더에 맞게 재샘플링/인코딩해야 합니다.
- `listVoices`는 프로바이더별 선택 사항입니다. 벤더 소유 음성 선택기나 설정 흐름에 사용하세요.
- 음성 목록은 프로바이더 인식 선택기를 위한 locale, gender, personality 태그 같은 더 풍부한 메타데이터를 포함할 수 있습니다.
- 현재 전화 통신은 OpenAI와 ElevenLabs가 지원합니다. Microsoft는 지원하지 않습니다.

플러그인은 `api.registerSpeechProvider(...)`를 통해 음성 프로바이더를 등록할 수도 있습니다.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

참고:

- TTS 정책, 폴백, 응답 전달은 코어에 유지하세요.
- 벤더 소유 합성 동작에는 음성 프로바이더를 사용하세요.
- 레거시 Microsoft `edge` 입력은 `microsoft` 프로바이더 ID로 정규화됩니다.
- 선호되는 소유권 모델은 회사 중심입니다. OpenClaw가 이러한
  기능 계약을 추가함에 따라 하나의 벤더 플러그인이 텍스트, 음성, 이미지, 미래의 미디어 프로바이더를 함께 소유할 수 있습니다.

이미지/오디오/비디오 이해의 경우, 플러그인은 일반적인 키/값 bag 대신
타입이 지정된 하나의 미디어 이해 프로바이더를 등록합니다:

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

참고:

- 오케스트레이션, 폴백, 설정, 채널 연결은 코어에 유지하세요.
- 벤더 동작은 프로바이더 플러그인에 유지하세요.
- 점진적 확장은 타입을 유지해야 합니다: 새로운 선택적 메서드, 새로운 선택적
  결과 필드, 새로운 선택적 기능.
- 비디오 생성도 이미 같은 패턴을 따릅니다:
  - 코어가 기능 계약과 런타임 헬퍼를 소유합니다
  - 벤더 플러그인은 `api.registerVideoGenerationProvider(...)`를 등록합니다
  - 기능/채널 플러그인은 `api.runtime.videoGeneration.*`를 사용합니다

미디어 이해 런타임 헬퍼의 경우, 플러그인은 다음을 호출할 수 있습니다:

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

오디오 전사의 경우, 플러그인은 미디어 이해 런타임 또는
이전 STT 별칭 중 하나를 사용할 수 있습니다:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // MIME을 신뢰성 있게 추론할 수 없을 때는 선택 사항:
  mime: "audio/ogg",
});
```

참고:

- `api.runtime.mediaUnderstanding.*`는
  이미지/오디오/비디오 이해를 위한 선호되는 공유 표면입니다.
- 코어 미디어 이해 오디오 설정(`tools.media.audio`)과 프로바이더 폴백 순서를 사용합니다.
- 전사 출력이 생성되지 않으면 `{ text: undefined }`를 반환합니다(예: 입력이 건너뛰어지거나 지원되지 않는 경우).
- `api.runtime.stt.transcribeAudioFile(...)`는 호환성 별칭으로 남아 있습니다.

플러그인은 `api.runtime.subagent`를 통해 백그라운드 서브에이전트 실행도 시작할 수 있습니다:

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

참고:

- `provider`와 `model`은 영구 세션 변경이 아니라 실행별 선택적 재정의입니다.
- OpenClaw는 신뢰된 호출자에 대해서만 이러한 재정의 필드를 적용합니다.
- 플러그인 소유 폴백 실행의 경우, 운영자는 `plugins.entries.<id>.subagent.allowModelOverride: true`로 명시적으로 동의해야 합니다.
- 신뢰된 플러그인을 특정 정식 `provider/model` 대상으로 제한하려면 `plugins.entries.<id>.subagent.allowedModels`를 사용하고, 모든 대상을 명시적으로 허용하려면 `"*"`를 사용하세요.
- 신뢰되지 않은 플러그인 서브에이전트 실행도 여전히 동작하지만, 재정의 요청은 조용히 폴백되는 대신 거부됩니다.

웹 검색의 경우, 플러그인은 에이전트 도구 연결을 직접 건드리는 대신
공유 런타임 헬퍼를 사용할 수 있습니다:

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

플러그인은
`api.registerWebSearchProvider(...)`를 통해 웹 검색 프로바이더를 등록할 수도 있습니다.

참고:

- 프로바이더 선택, 자격 증명 해석, 공유 요청 의미론은 코어에 유지하세요.
- 벤더별 검색 전송에는 웹 검색 프로바이더를 사용하세요.
- `api.runtime.webSearch.*`는 에이전트 도구 래퍼에 의존하지 않고 검색 동작이 필요한 기능/채널 플러그인을 위한 선호되는 공유 표면입니다.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: 구성된 이미지 생성 프로바이더 체인을 사용해 이미지를 생성합니다.
- `listProviders(...)`: 사용 가능한 이미지 생성 프로바이더와 해당 기능을 나열합니다.

## Gateway HTTP 라우트

플러그인은 `api.registerHttpRoute(...)`로 HTTP 엔드포인트를 노출할 수 있습니다.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

라우트 필드:

- `path`: gateway HTTP 서버 아래의 라우트 경로.
- `auth`: 필수. 일반 gateway 인증이 필요하면 `"gateway"`를, plugin 관리 인증/Webhook 검증에는 `"plugin"`을 사용합니다.
- `match`: 선택 사항. `"exact"`(기본값) 또는 `"prefix"`.
- `replaceExisting`: 선택 사항. 같은 플러그인이 기존 라우트 등록을 자체적으로 교체할 수 있게 합니다.
- `handler`: 라우트가 요청을 처리했을 때 `true`를 반환합니다.

참고:

- `api.registerHttpHandler(...)`는 제거되었으며 플러그인 로드 오류를 발생시킵니다. 대신 `api.registerHttpRoute(...)`를 사용하세요.
- 플러그인 라우트는 `auth`를 명시적으로 선언해야 합니다.
- 정확히 같은 `path + match` 충돌은 `replaceExisting: true`가 없는 한 거부되며, 한 플러그인이 다른 플러그인의 라우트를 교체할 수는 없습니다.
- `auth` 수준이 다른 중첩 라우트는 거부됩니다. `exact`/`prefix` 폴스루 체인은 같은 인증 수준에서만 유지하세요.
- `auth: "plugin"` 라우트는 운영자 런타임 범위를 자동으로 받지 **않습니다**. 이는 권한 있는 Gateway 헬퍼 호출이 아니라 플러그인 관리 Webhook/서명 검증용입니다.
- `auth: "gateway"` 라우트는 Gateway 요청 런타임 범위 내부에서 실행되지만, 그 범위는 의도적으로 보수적입니다:
  - 공유 시크릿 bearer 인증(`gateway.auth.mode = "token"` / `"password"`)에서는 호출자가 `x-openclaw-scopes`를 보내더라도 플러그인 라우트 런타임 범위가 `operator.write`에 고정됩니다
  - 신뢰된 ID 기반 HTTP 모드(예: `trusted-proxy` 또는 사설 인그레스에서의 `gateway.auth.mode = "none"`)는 헤더가 명시적으로 존재할 때만 `x-openclaw-scopes`를 적용합니다
  - 그런 ID 기반 플러그인 라우트 요청에 `x-openclaw-scopes`가 없으면 런타임 범위는 `operator.write`로 폴백됩니다
- 실용적인 규칙: gateway 인증 플러그인 라우트가 암묵적인 관리자 표면이라고 가정하지 마세요. 라우트에 관리자 전용 동작이 필요하다면, ID 기반 인증 모드를 요구하고 명시적인 `x-openclaw-scopes` 헤더 계약을 문서화하세요.

## Plugin SDK import 경로

플러그인을 작성할 때는 단일 `openclaw/plugin-sdk` import 대신
SDK 하위 경로를 사용하세요:

- 플러그인 등록 프리미티브에는 `openclaw/plugin-sdk/plugin-entry`.
- 일반 공유 플러그인 대상 계약에는 `openclaw/plugin-sdk/core`.
- 루트 `openclaw.json` Zod 스키마
  export(`OpenClawSchema`)에는 `openclaw/plugin-sdk/config-schema`.
- `openclaw/plugin-sdk/channel-setup` 같은 안정적인 채널 프리미티브,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input`, 그리고
  `openclaw/plugin-sdk/webhook-ingress`는 공유 설정/인증/응답/Webhook
  연결을 위한 경로입니다. `channel-inbound`는 디바운스, 멘션 매칭,
  인바운드 멘션 정책 헬퍼, envelope 포맷팅, 인바운드 envelope
  컨텍스트 헬퍼의 공유 홈입니다.
  `channel-setup`은 좁은 선택적 설치 설정 seam입니다.
  `setup-runtime`은 `setupEntry` /
  지연 시작에서 사용하는 런타임 안전 설정 표면이며, import 안전 설정 패치 어댑터를 포함합니다.
  `setup-adapter-runtime`은 환경 인식 계정 설정 어댑터 seam입니다.
  `setup-tools`는 작은 CLI/archive/docs 헬퍼 seam입니다(`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- `openclaw/plugin-sdk/channel-config-helpers` 같은 도메인 하위 경로,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-gateway-runtime`,
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`,
  `openclaw/plugin-sdk/approval-handler-runtime`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store`, 그리고
  `openclaw/plugin-sdk/directory-runtime`은 공유 런타임/설정 헬퍼를 위한 경로입니다.
  `telegram-command-config`는 Telegram 커스텀
  명령 정규화/검증을 위한 좁은 공개 seam이며, 번들된
  Telegram 계약 표면을 일시적으로 사용할 수 없더라도 계속 제공됩니다.
  `text-runtime`은
  assistant-visible-text 제거, markdown 렌더링/청킹 헬퍼, redaction
  헬퍼, directive-tag 헬퍼, safe-text 유틸리티를 포함한 공유 텍스트/markdown/로깅 seam입니다.
- 승인 전용 채널 seam은 플러그인에서 하나의 `approvalCapability`
  계약을 우선 사용해야 합니다. 그러면 코어는 승인 동작을 관련 없는 플러그인 필드에 섞는 대신
  그 하나의 기능을 통해 승인 인증, 전달, 렌더링,
  기본 라우팅, 지연 기본 핸들러 동작을 읽습니다.
- `openclaw/plugin-sdk/channel-runtime`은 더 이상 권장되지 않으며
  이전 플러그인을 위한 호환성 shim으로만 남아 있습니다. 새 코드는 대신 더 좁은
  일반 프리미티브를 import해야 하며, 저장소 코드에는 shim에 대한 새 import를 추가해서는 안 됩니다.
- 번들 확장 내부 구조는 비공개로 유지됩니다. 외부 플러그인은
  `openclaw/plugin-sdk/*` 하위 경로만 사용해야 합니다. OpenClaw 코어/테스트 코드는
  `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js`, `login-qr-api.js` 같은
  좁은 범위 파일처럼 플러그인 패키지 루트 아래의 저장소 공개 진입점을 사용할 수 있습니다.
  코어나 다른 확장에서 플러그인 패키지의 `src/*`를 import하지 마세요.
- 저장소 진입점 분리:
  `<plugin-package-root>/api.js`는 헬퍼/타입 barrel,
  `<plugin-package-root>/runtime-api.js`는 런타임 전용 barrel,
  `<plugin-package-root>/index.js`는 번들 플러그인 진입점,
  `<plugin-package-root>/setup-entry.js`는 설정 플러그인 진입점입니다.
- 현재 번들 프로바이더 예시:
  - Anthropic은 `wrapAnthropicProviderStream`, 베타 헤더 헬퍼,
    `service_tier` 파싱 같은 Claude 스트림 헬퍼를 위해 `api.js` / `contract-api.js`를 사용합니다.
  - OpenAI는 프로바이더 빌더, 기본 모델 헬퍼,
    실시간 프로바이더 빌더를 위해 `api.js`를 사용합니다.
  - OpenRouter는 프로바이더 빌더와 온보딩/설정
    헬퍼를 위해 `api.js`를 사용하고, `register.runtime.js`는 여전히 저장소 로컬 사용을 위해
    일반 `plugin-sdk/provider-stream` 헬퍼를 다시 export할 수 있습니다.
- 파사드로 로드된 공개 진입점은 활성 런타임 설정 스냅샷이 있을 경우 이를 우선 사용하고, OpenClaw가 아직 런타임 스냅샷을 제공하지 않을 때는 디스크의 해석된 설정 파일로 폴백합니다.
- 일반 공유 프리미티브는 여전히 선호되는 공개 SDK 계약입니다. 번들 채널 브랜드 헬퍼 seam의 작은 예약 호환성 집합은 여전히 존재합니다. 이를 새로운 서드파티 import 대상이 아니라 번들 유지보수/호환성 seam으로 취급하세요. 새로운 크로스채널 계약은 여전히 일반 `plugin-sdk/*` 하위 경로 또는 플러그인 로컬 `api.js` /
  `runtime-api.js` barrel에 추가되어야 합니다.

호환성 참고 사항:

- 새 코드에서는 루트 `openclaw/plugin-sdk` barrel을 피하세요.
- 먼저 좁고 안정적인 프리미티브를 우선 사용하세요. 더 새로운 setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool 하위 경로가 새로운
  번들 및 외부 플러그인 작업을 위한 의도된 계약입니다.
  대상 파싱/매칭은 `openclaw/plugin-sdk/channel-targets`에 두어야 합니다.
  메시지 작업 게이트와 반응 message-id 헬퍼는
  `openclaw/plugin-sdk/channel-actions`에 두어야 합니다.
- 번들 확장 전용 헬퍼 barrel은 기본적으로 안정적이지 않습니다. 어떤
  헬퍼가 번들 확장에만 필요하다면, 이를
  `openclaw/plugin-sdk/<extension>`으로 승격하는 대신 확장의 로컬 `api.js` 또는 `runtime-api.js` seam 뒤에 두세요.
- 새로운 공유 헬퍼 seam은 채널 브랜드형이 아니라 일반적이어야 합니다. 공유 대상
  파싱은 `openclaw/plugin-sdk/channel-targets`에 두고, 채널별
  내부 구조는 소유 플러그인의 로컬 `api.js` 또는 `runtime-api.js`
  seam 뒤에 유지하세요.
- `image-generation`,
  `media-understanding`, `speech` 같은 기능별 하위 경로가 존재하는 이유는 오늘날 번들/기본 플러그인이 이를 사용하기 때문입니다.
  그렇다고 해서 export된 모든 헬퍼가 장기적으로 고정된 외부 계약이라는 뜻은 아닙니다.

## message 도구 스키마

플러그인은 채널별 `describeMessageTool(...)` 스키마
기여를 소유해야 합니다. 프로바이더별 필드는 공유 코어가 아니라 플러그인 안에 두세요.

공유 가능한 이식형 스키마 조각에는
`openclaw/plugin-sdk/channel-actions`를 통해 export되는 일반 헬퍼를 재사용하세요:

- 버튼 그리드 스타일 페이로드에는 `createMessageToolButtonsSchema()`
- 구조화된 카드 페이로드에는 `createMessageToolCardSchema()`

어떤 스키마 형태가 특정 프로바이더 하나에만 의미가 있다면, 이를 공유 SDK로 승격하지 말고 해당 플러그인의
자체 소스에 정의하세요.

## 채널 대상 해석

채널 Plugin은 채널별 대상 의미론을 소유해야 합니다. 공유
아웃바운드 호스트는 일반적으로 유지하고 프로바이더 규칙에는 메시징 어댑터 표면을 사용하세요:

- `messaging.inferTargetChatType({ to })`는 정규화된 대상이
  디렉터리 조회 전에 `direct`, `group`, `channel` 중 무엇으로 취급되어야 하는지 결정합니다.
- `messaging.targetResolver.looksLikeId(raw, normalized)`는 어떤
  입력이 디렉터리 검색 대신 곧바로 ID 유사 해석으로 넘어가야 하는지를 코어에 알려줍니다.
- `messaging.targetResolver.resolveTarget(...)`는 정규화 후 또는
  디렉터리 검색 실패 후 코어에 최종 프로바이더 소유 해석이 필요할 때 사용하는 plugin 폴백입니다.
- `messaging.resolveOutboundSessionRoute(...)`는 대상이 해석된 뒤 프로바이더별 세션
  라우트 구성을 소유합니다.

권장 분리 방식:

- 피어/그룹 검색 전에 일어나야 하는 범주 결정에는 `inferTargetChatType`을 사용하세요.
- "이것을 명시적/기본 대상 ID로 취급" 검사에는 `looksLikeId`를 사용하세요.
- 광범위한 디렉터리 검색이 아니라 프로바이더별 정규화 폴백에는 `resolveTarget`을 사용하세요.
- chat ID, thread ID, JID, handle, room ID 같은 프로바이더 기본 ID는
  일반 SDK 필드가 아니라 `target` 값 또는 프로바이더별 파라미터 안에 두세요.

## 설정 기반 디렉터리

설정에서 디렉터리 항목을 파생하는 플러그인은 해당 로직을
플러그인 안에 유지하고
`openclaw/plugin-sdk/directory-runtime`의 공유 헬퍼를 재사용해야 합니다.

다음과 같은 설정 기반 피어/그룹이 채널에 필요할 때 사용하세요:

- allowlist 기반 DM 피어
- 구성된 채널/그룹 맵
- 계정 범위 정적 디렉터리 폴백

`directory-runtime`의 공유 헬퍼는 일반 작업만 처리합니다:

- 쿼리 필터링
- 제한 적용
- 중복 제거/정규화 헬퍼
- `ChannelDirectoryEntry[]` 구성

채널별 계정 검사와 ID 정규화는 플러그인 구현에 남겨두어야 합니다.

## 프로바이더 카탈로그

프로바이더 플러그인은
`registerProvider({ catalog: { run(...) { ... } } })`로 추론용 모델 카탈로그를 정의할 수 있습니다.

`catalog.run(...)`은 OpenClaw가
`models.providers`에 기록하는 것과 동일한 형태를 반환합니다:

- 하나의 프로바이더 항목에는 `{ provider }`
- 여러 프로바이더 항목에는 `{ providers }`

플러그인이 프로바이더별 모델 ID, 기본 base URL 또는 인증 기반 모델 메타데이터를 소유할 때는
`catalog`를 사용하세요.

`catalog.order`는 플러그인의 카탈로그가 OpenClaw의
내장 암시적 프로바이더에 상대적으로 언제 병합되는지 제어합니다:

- `simple`: 일반 API 키 또는 환경 기반 프로바이더
- `profile`: 인증 프로필이 있을 때 나타나는 프로바이더
- `paired`: 여러 관련 프로바이더 항목을 합성하는 프로바이더
- `late`: 다른 암시적 프로바이더 뒤의 마지막 단계

나중에 오는 프로바이더가 키 충돌에서 이기므로, 플러그인은 동일한 프로바이더 ID를 가진
내장 프로바이더 항목을 의도적으로 재정의할 수 있습니다.

호환성:

- `discovery`는 레거시 별칭으로 여전히 동작합니다
- `catalog`와 `discovery`가 모두 등록되면 OpenClaw는 `catalog`를 사용합니다

## 읽기 전용 채널 검사

플러그인이 채널을 등록한다면,
`resolveAccount(...)`와 함께 `plugin.config.inspectAccount(cfg, accountId)` 구현을 우선하세요.

이유:

- `resolveAccount(...)`는 런타임 경로입니다. 자격 증명이
  완전히 구체화되었다고 가정할 수 있으며, 필요한 시크릿이 없을 때 빠르게 실패해도 됩니다.
- `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve`, doctor/config
  복구 흐름 같은 읽기 전용 명령 경로는 설정을 설명하기 위해
  런타임 자격 증명을 구체화할 필요가 없어야 합니다.

권장 `inspectAccount(...)` 동작:

- 설명적인 계정 상태만 반환하세요.
- `enabled`와 `configured`를 유지하세요.
- 관련이 있다면 다음과 같은 자격 증명 소스/상태 필드를 포함하세요:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- 읽기 전용 가용성을 보고하기 위해 원시 토큰 값을 반환할 필요는 없습니다.
  상태 스타일 명령에는 `tokenStatus: "available"`(및 일치하는 소스 필드)만 반환해도 충분합니다.
- 자격 증명이 SecretRef를 통해 구성되었지만
  현재 명령 경로에서 사용할 수 없는 경우 `configured_unavailable`을 사용하세요.

이렇게 하면 읽기 전용 명령이 크래시하거나 계정을 미구성으로 잘못 보고하는 대신 "구성되었지만 이 명령 경로에서는 사용할 수 없음"을 보고할 수 있습니다.

## 패키지 팩

플러그인 디렉터리는 `openclaw.extensions`가 포함된 `package.json`을 가질 수 있습니다:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

각 항목은 하나의 플러그인이 됩니다. 팩에 여러 확장이 나열되면 플러그인 ID는
`name/<fileBase>`가 됩니다.

플러그인이 npm 의존성을 import한다면, 해당 디렉터리에
`node_modules`가 사용 가능하도록 그 디렉터리 안에 설치하세요(`npm install` / `pnpm install`).

보안 가드레일: 모든 `openclaw.extensions` 항목은 심볼릭 링크 해석 후에도 플러그인
디렉터리 내부에 있어야 합니다. 패키지 디렉터리를 벗어나는 항목은
거부됩니다.

보안 참고: `openclaw plugins install`은 플러그인 의존성을
`npm install --omit=dev --ignore-scripts`로 설치합니다(라이프사이클 스크립트 없음, 런타임 시 dev dependency 없음). 플러그인 의존성
트리는 "순수 JS/TS"로 유지하고 `postinstall` 빌드가 필요한 패키지는 피하세요.

선택 사항: `openclaw.setupEntry`는 가벼운 설정 전용 모듈을 가리킬 수 있습니다.
OpenClaw가 비활성화된 채널 플러그인에 대한 설정 표면이 필요할 때, 또는
채널 플러그인이 활성화되어 있지만 아직 구성되지 않았을 때는 전체 플러그인 진입점 대신 `setupEntry`를 로드합니다. 이렇게 하면 메인 플러그인 진입점이 도구, 훅 또는 다른 런타임 전용
코드도 연결하는 경우 시작과 설정이 더 가벼워집니다.

선택 사항: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`은
채널이 이미 구성된 경우에도 gateway의
pre-listen 시작 단계 동안 채널 플러그인이 동일한 `setupEntry` 경로를 선택하도록 할 수 있습니다.

이 옵션은 `setupEntry`가 gateway가 리슨을 시작하기 전에 반드시 존재해야 하는 시작 표면을
완전히 포괄하는 경우에만 사용하세요. 실제로 이는 setup entry가
시작이 의존하는 모든 채널 소유 기능을 등록해야 함을 의미합니다. 예를 들면:

- 채널 등록 자체
- gateway가 리슨을 시작하기 전에 반드시 사용 가능해야 하는 모든 HTTP 라우트
- 같은 시점에 반드시 존재해야 하는 모든 gateway 메서드, 도구 또는 서비스

전체 엔트리가 여전히 필요한 시작 기능을 소유하고 있다면 이 플래그를 활성화하지 마세요.
기본 동작을 유지하고 OpenClaw가 시작 중에
전체 엔트리를 로드하도록 하세요.

번들 채널은 전체 채널 런타임이 로드되기 전에 코어가 참조할 수 있는 설정 전용 계약 표면 헬퍼도 게시할 수 있습니다. 현재 설정
승격 표면은 다음과 같습니다:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

코어는 레거시 단일 계정 채널
설정을 전체 플러그인 엔트리를 로드하지 않고 `channels.<id>.accounts.*`로 승격해야 할 때 이 표면을 사용합니다.
현재 번들 예시는 Matrix입니다. 이름 있는 계정이 이미 존재할 때 인증/bootstrap 키만
이름이 지정된 승격 계정으로 이동하고,
항상 `accounts.default`를 만드는 대신 구성된 비정규 기본 계정 키를 보존할 수 있습니다.

이러한 설정 패치 어댑터는 번들 계약 표면 탐색을 지연 상태로 유지합니다. import
시점은 가볍게 유지되고, 승격 표면은 모듈 import 시 번들 채널 시작을 다시 진입하는 대신 첫 사용 시에만 로드됩니다.

그러한 시작 표면에 gateway RPC 메서드가 포함되는 경우,
플러그인별 접두사에 유지하세요. 코어 관리자 네임스페이스(`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`)는 예약되어 있으며, 플러그인이 더 좁은 범위를 요청하더라도 항상 `operator.admin`으로 해석됩니다.

예시:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### 채널 카탈로그 메타데이터

채널 플러그인은 `openclaw.channel`을 통해 설정/탐색 메타데이터를 광고하고
`openclaw.install`을 통해 설치 힌트를 제공할 수 있습니다. 이렇게 하면 코어 카탈로그를 데이터 프리 상태로 유지할 수 있습니다.

예시:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Nextcloud Talk Webhook bot을 통한 셀프 호스팅 채팅.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

최소 예시 외에 유용한 `openclaw.channel` 필드는 다음과 같습니다:

- `detailLabel`: 더 풍부한 카탈로그/상태 표면을 위한 보조 라벨
- `docsLabel`: 문서 링크의 링크 텍스트 재정의
- `preferOver`: 이 카탈로그 항목이 우선해야 하는 낮은 우선순위 플러그인/채널 ID
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: 선택 표면 복사 제어
- `markdownCapable`: 아웃바운드 포맷팅 결정에서 채널을 markdown 지원 가능으로 표시
- `exposure.configured`: `false`로 설정하면 구성된 채널 목록 표면에서 채널 숨김
- `exposure.setup`: `false`로 설정하면 대화형 설정/구성 선택기에서 채널 숨김
- `exposure.docs`: 문서 탐색 표면에서 채널을 내부/비공개로 표시
- `showConfigured` / `showInSetup`: 호환성을 위해 레거시 별칭도 여전히 허용되지만 `exposure`를 우선하세요
- `quickstartAllowFrom`: 채널을 표준 빠른 시작 `allowFrom` 흐름에 포함
- `forceAccountBinding`: 계정이 하나만 존재하더라도 명시적인 계정 바인딩 요구
- `preferSessionLookupForAnnounceTarget`: announce 대상 해석 시 세션 조회를 우선

OpenClaw는 **외부 채널 카탈로그**(예: MPM
레지스트리 export)도 병합할 수 있습니다. 다음 위치 중 하나에 JSON 파일을 두세요:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

또는 하나 이상의 JSON 파일(쉼표/세미콜론/`PATH` 구분자 사용)을 가리키도록 `OPENCLAW_PLUGIN_CATALOG_PATHS`(또는 `OPENCLAW_MPM_CATALOG_PATHS`)를 설정하세요. 각 파일은 `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`를 포함해야 합니다. 파서는 `"entries"` 키의 레거시 별칭으로 `"packages"` 또는 `"plugins"`도 허용합니다.

## 컨텍스트 엔진 플러그인

컨텍스트 엔진 플러그인은 수집, 조립, Compaction을 위한 세션 컨텍스트 오케스트레이션을 소유합니다. 플러그인에서
`api.registerContextEngine(id, factory)`로 이를 등록한 다음, `plugins.slots.contextEngine`으로 활성 엔진을 선택하세요.

기본 컨텍스트
파이프라인에 메모리 검색이나 훅만 추가하는 것이 아니라 이를 교체하거나 확장해야 할 때 사용하세요.

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

엔진이 Compaction 알고리즘을 **소유하지 않는다면**, `compact()`를
구현한 상태로 유지하고 이를 명시적으로 위임하세요:

```ts
import {
  buildMemorySystemPromptAddition,
  delegateCompactionToRuntime,
} from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## 새 기능 추가하기

플러그인에 현재 API에 맞지 않는 동작이 필요할 때는, 비공개 직접 접근으로
플러그인 시스템을 우회하지 마세요. 누락된 기능을 추가하세요.

권장 순서:

1. 코어 계약 정의
   코어가 소유해야 하는 공유 동작을 결정합니다: 정책, 폴백, 설정 병합,
   수명 주기, 채널 대상 의미론, 런타임 헬퍼 형태.
2. 타입이 지정된 플러그인 등록/런타임 표면 추가
   가장 작지만 유용한 타입 지정 기능 표면으로 `OpenClawPluginApi` 및/또는 `api.runtime`를 확장합니다.
3. 코어 + 채널/기능 소비자 연결
   채널과 기능 플러그인은 벤더 구현을 직접 import하는 대신,
   코어를 통해 새 기능을 사용해야 합니다.
4. 벤더 구현 등록
   그런 다음 벤더 플러그인이 해당 기능에 대해 백엔드를 등록합니다.
5. 계약 커버리지 추가
   시간이 지나도 소유권과 등록 형태가 명시적으로 유지되도록 테스트를 추가합니다.

이것이 OpenClaw가 하나의
프로바이더 관점에 하드코딩되지 않으면서도 뚜렷한 방향성을 유지하는 방식입니다. 구체적인 파일 체크리스트와 예시는 [기능 Cookbook](/ko/plugins/architecture)을
참고하세요.

### 기능 체크리스트

새 기능을 추가할 때는 구현이 보통 다음 표면을 함께 다뤄야 합니다:

- `src/<capability>/types.ts`의 코어 계약 타입
- `src/<capability>/runtime.ts`의 코어 러너/런타임 헬퍼
- `src/plugins/types.ts`의 플러그인 API 등록 표면
- `src/plugins/registry.ts`의 플러그인 레지스트리 연결
- 기능/채널 플러그인이 이를 사용해야 할 때 `src/plugins/runtime/*`의
  플러그인 런타임 노출
- `src/test-utils/plugin-registration.ts`의 캡처/테스트 헬퍼
- `src/plugins/contracts/registry.ts`의 소유권/계약 검증
- `docs/`의 운영자/플러그인 문서

이 표면 중 하나가 빠져 있다면, 보통 그 기능이
아직 완전히 통합되지 않았다는 신호입니다.

### 기능 템플릿

최소 패턴:

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// feature/channel plugin을 위한 공유 런타임 헬퍼
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

계약 테스트 패턴:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

이렇게 하면 규칙이 단순해집니다:

- 코어는 기능 계약 + 오케스트레이션을 소유합니다
- 벤더 플러그인은 벤더 구현을 소유합니다
- 기능/채널 플러그인은 런타임 헬퍼를 사용합니다
- 계약 테스트는 소유권을 명시적으로 유지합니다
