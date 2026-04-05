---
read_when:
    - 유료 API를 호출할 수 있는 기능이 무엇인지 이해하려는 경우
    - 키, 비용, 사용량 가시성을 감사해야 하는 경우
    - /status 또는 /usage 비용 보고를 설명하는 경우
summary: 무엇이 비용을 발생시킬 수 있는지, 어떤 키가 사용되는지, 사용량을 보는 방법 감사하기
title: API 사용량 및 비용
x-i18n:
    generated_at: "2026-04-05T12:53:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 71789950fe54dcdcd3e34c8ad6e3143f749cdfff5bbc2f14be4b85aaa467b14c
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# API 사용량 및 비용

이 문서는 **API 키를 호출할 수 있는 기능**과 해당 비용이 어디에 표시되는지를 나열합니다. 주로
제공자 사용량 또는 유료 API 호출을 생성할 수 있는 OpenClaw 기능에 초점을 맞춥니다.

## 비용이 표시되는 위치(chat + CLI)

**세션별 비용 스냅샷**

- `/status`는 현재 세션 모델, 컨텍스트 사용량, 마지막 응답 토큰을 표시합니다.
- 모델이 **API 키 인증**을 사용하는 경우 `/status`는 마지막 응답에 대한 **예상 비용**도 표시합니다.
- 라이브 세션 메타데이터가 부족한 경우 `/status`는 최신 전사 사용량
  항목에서 토큰/캐시 카운터와 활성 런타임 모델 레이블을 복구할 수 있습니다. 기존의 0이 아닌 라이브 값은 여전히 우선하며,
  저장된 총계가 없거나 더 작은 경우 프롬프트 크기의 전사 총계가 우선할 수 있습니다.

**메시지별 비용 바닥글**

- `/usage full`은 모든 응답에 사용량 바닥글을 추가하며, 여기에는 **예상 비용**이 포함됩니다(API 키 전용).
- `/usage tokens`는 토큰만 표시합니다. 구독형 OAuth/토큰 및 CLI 흐름은 달러 비용을 숨깁니다.
- Gemini CLI 참고: CLI가 JSON 출력을 반환하면 OpenClaw는
  `stats`에서 사용량을 읽고 `stats.cached`를 `cacheRead`로 정규화하며 필요할 때
  `stats.input_tokens - stats.cached`에서 입력 토큰을 도출합니다.

Anthropic 참고: Anthropic의 공개 Claude Code 문서에는 여전히 Claude
Code 터미널 직접 사용이 Claude 플랜 한도에 포함되어 있습니다. 별도로 Anthropic은 OpenClaw
사용자에게 **2026년 4월 4일 오후 12:00 PT / 오후 8:00 BST**부터
**OpenClaw** Claude 로그인 경로가 서드파티 하니스 사용으로 계산되며
구독과 별도로 청구되는 **Extra Usage**가 필요하다고 알렸습니다. Anthropic은
OpenClaw가 `/usage full`에 표시할 수 있는 메시지별 달러 예상치를 제공하지 않습니다.

**CLI 사용량 창(제공자 할당량)**

- `openclaw status --usage` 및 `openclaw channels list`는 제공자 **사용량 창**을 표시합니다
  (메시지별 비용이 아니라 할당량 스냅샷).
- 사람이 읽는 출력은 제공자 전반에서 `X% left` 형식으로 정규화됩니다.
- 현재 사용량 창을 지원하는 제공자: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi, z.ai.
- MiniMax 참고: 원시 `usage_percent` / `usagePercent` 필드는 남은
  할당량을 의미하므로 OpenClaw는 표시 전에 이를 반전합니다. 개수 기반 필드는 여전히 존재할 경우 우선합니다.
  제공자가 `model_remains`를 반환하면 OpenClaw는 chat 모델 항목을 우선하고,
  필요할 때 타임스탬프에서 창 레이블을 도출하며, 플랜 레이블에 모델 이름을 포함합니다.
- 이러한 할당량 창의 사용량 인증은 가능할 때 제공자별 훅에서 가져오며,
  그렇지 않으면 OpenClaw는 auth 프로필, env 또는 config의 일치하는 OAuth/API 키
  자격 증명으로 폴백합니다.

자세한 내용과 예시는 [토큰 사용량 및 비용](/reference/token-use)을 참고하세요.

## 키를 탐색하는 방법

OpenClaw는 다음 위치에서 자격 증명을 가져올 수 있습니다:

- **Auth 프로필**(에이전트별, `auth-profiles.json`에 저장).
- **환경 변수**(예: `OPENAI_API_KEY`, `BRAVE_API_KEY`, `FIRECRAWL_API_KEY`).
- **Config**(`models.providers.*.apiKey`, `plugins.entries.*.config.webSearch.apiKey`,
  `plugins.entries.firecrawl.config.webFetch.apiKey`, `memorySearch.*`,
  `talk.providers.*.apiKey`).
- **Skills**(`skills.entries.<name>.apiKey`)는 키를 skill 프로세스 환경으로 내보낼 수 있습니다.

## 키 비용을 발생시킬 수 있는 기능

### 1) 코어 모델 응답(chat + 도구)

모든 응답 또는 도구 호출은 **현재 모델 제공자**(OpenAI, Anthropic 등)를 사용합니다. 이것이
사용량과 비용의 주요 원천입니다.

여기에는 OpenClaw의 로컬 UI 외부에서 여전히 청구되는 구독형 호스팅 제공자도 포함됩니다.
예: **OpenAI Codex**, **Alibaba Cloud Model Studio
Coding Plan**, **MiniMax Coding Plan**, **Z.AI / GLM Coding Plan**,
그리고 **Extra Usage**가 활성화된 Anthropic의 OpenClaw Claude 로그인 경로.

가격 설정은 [모델](/providers/models), 표시 방법은 [토큰 사용량 및 비용](/reference/token-use)을 참고하세요.

### 2) 미디어 이해(오디오/이미지/비디오)

들어오는 미디어는 응답 실행 전에 요약되거나 전사될 수 있습니다. 이는 모델/제공자 API를 사용합니다.

- 오디오: OpenAI / Groq / Deepgram / Google / Mistral
- 이미지: OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.AI
- 비디오: Google / Qwen / Moonshot

[미디어 이해](/ko/nodes/media-understanding)를 참고하세요.

### 3) 이미지 및 비디오 생성

공유 생성 기능도 제공자 키 비용을 발생시킬 수 있습니다:

- 이미지 생성: OpenAI / Google / fal / MiniMax
- 비디오 생성: Qwen

이미지 생성은
`agents.defaults.imageGenerationModel`이 설정되지 않은 경우 인증 기반 제공자 기본값을 추론할 수 있습니다. 비디오 생성은 현재
`qwen/wan2.6-t2v` 같은 명시적인 `agents.defaults.videoGenerationModel`이 필요합니다.

[이미지 생성](/tools/image-generation), [Qwen Cloud](/providers/qwen),
[모델](/ko/concepts/models)을 참고하세요.

### 4) 메모리 임베딩 + 시맨틱 검색

시맨틱 메모리 검색은 원격 제공자로 설정된 경우 **임베딩 API**를 사용합니다:

- `memorySearch.provider = "openai"` → OpenAI 임베딩
- `memorySearch.provider = "gemini"` → Gemini 임베딩
- `memorySearch.provider = "voyage"` → Voyage 임베딩
- `memorySearch.provider = "mistral"` → Mistral 임베딩
- `memorySearch.provider = "ollama"` → Ollama 임베딩(로컬/자체 호스팅, 일반적으로 호스팅 API 과금 없음)
- 로컬 임베딩 실패 시 원격 제공자로 선택적 폴백

`memorySearch.provider = "local"`로 설정하면 로컬로 유지할 수 있습니다(API 사용 없음).

[메모리](/ko/concepts/memory)를 참고하세요.

### 5) 웹 검색 도구

`web_search`는 제공자에 따라 사용량 비용이 발생할 수 있습니다:

- **Brave Search API**: `BRAVE_API_KEY` 또는 `plugins.entries.brave.config.webSearch.apiKey`
- **Exa**: `EXA_API_KEY` 또는 `plugins.entries.exa.config.webSearch.apiKey`
- **Firecrawl**: `FIRECRAWL_API_KEY` 또는 `plugins.entries.firecrawl.config.webSearch.apiKey`
- **Gemini (Google Search)**: `GEMINI_API_KEY` 또는 `plugins.entries.google.config.webSearch.apiKey`
- **Grok (xAI)**: `XAI_API_KEY` 또는 `plugins.entries.xai.config.webSearch.apiKey`
- **Kimi (Moonshot)**: `KIMI_API_KEY`, `MOONSHOT_API_KEY`, 또는 `plugins.entries.moonshot.config.webSearch.apiKey`
- **MiniMax Search**: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, `MINIMAX_API_KEY`, 또는 `plugins.entries.minimax.config.webSearch.apiKey`
- **Ollama Web Search**: 기본적으로 키가 필요 없지만, 접근 가능한 Ollama 호스트와 `ollama signin`이 필요합니다. 호스트에서 요구하는 경우 일반 Ollama 제공자 bearer auth도 재사용할 수 있습니다
- **Perplexity Search API**: `PERPLEXITY_API_KEY`, `OPENROUTER_API_KEY`, 또는 `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily**: `TAVILY_API_KEY` 또는 `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo**: 키 없는 폴백(API 과금 없음, 하지만 비공식이며 HTML 기반)
- **SearXNG**: `SEARXNG_BASE_URL` 또는 `plugins.entries.searxng.config.webSearch.baseUrl`(키 없음/자체 호스팅, 호스팅 API 과금 없음)

레거시 `tools.web.search.*` 제공자 경로도 임시 호환성 shim을 통해 여전히 로드되지만,
더 이상 권장되는 config 표면은 아닙니다.

**Brave Search 무료 크레딧:** 각 Brave 플랜에는 매월 갱신되는
무료 크레딧 \$5가 포함됩니다. Search 플랜의 비용은 요청 1,000건당 \$5이므로, 이 크레딧으로
월 1,000건 요청을 무료로 처리할 수 있습니다. 예상치 못한 비용을 피하려면 Brave 대시보드에서 사용량 한도를 설정하세요.

[웹 도구](/tools/web)를 참고하세요.

### 5) 웹 가져오기 도구(Firecrawl)

API 키가 있으면 `web_fetch`가 **Firecrawl**을 호출할 수 있습니다:

- `FIRECRAWL_API_KEY` 또는 `plugins.entries.firecrawl.config.webFetch.apiKey`

Firecrawl이 설정되지 않은 경우 도구는 직접 fetch + readability로 폴백합니다(유료 API 없음).

[웹 도구](/tools/web)를 참고하세요.

### 6) 제공자 사용량 스냅샷(status/health)

일부 상태 명령은 할당량 창 또는 인증 상태를 표시하기 위해 **제공자 사용량 엔드포인트**를 호출합니다.
일반적으로 호출량은 적지만 여전히 제공자 API에 도달합니다:

- `openclaw status --usage`
- `openclaw models status --json`

[Models CLI](/cli/models)를 참고하세요.

### 7) 압축 보호 요약

압축 보호 기능은 **현재 모델**을 사용해 세션 기록을 요약할 수 있으며,
실행 시 제공자 API를 호출합니다.

[세션 관리 + 압축](/reference/session-management-compaction)을 참고하세요.

### 8) 모델 스캔 / 프로브

`openclaw models scan`은 OpenRouter 모델을 프로브할 수 있으며, 프로브가 활성화된 경우
`OPENROUTER_API_KEY`를 사용합니다.

[Models CLI](/cli/models)를 참고하세요.

### 9) Talk(음성)

Talk 모드는 설정된 경우 **ElevenLabs**를 호출할 수 있습니다:

- `ELEVENLABS_API_KEY` 또는 `talk.providers.elevenlabs.apiKey`

[Talk 모드](/ko/nodes/talk)를 참고하세요.

### 10) Skills(서드파티 API)

Skills는 `skills.entries.<name>.apiKey`에 `apiKey`를 저장할 수 있습니다. skill이 외부
API에 이 키를 사용하면 해당 skill의 제공자에 따라 비용이 발생할 수 있습니다.

[Skills](/tools/skills)를 참고하세요.
