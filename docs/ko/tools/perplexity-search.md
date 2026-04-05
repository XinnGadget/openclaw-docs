---
read_when:
    - 웹 검색에 Perplexity Search를 사용하려는 경우
    - '`PERPLEXITY_API_KEY` 또는 `OPENROUTER_API_KEY` 설정이 필요한 경우'
summary: web_search를 위한 Perplexity Search API 및 Sonar/OpenRouter 호환성
title: Perplexity Search
x-i18n:
    generated_at: "2026-04-05T12:57:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06d97498e26e5570364e1486cb75584ed53b40a0091bf0210e1ea62f62d562ea
    source_path: tools/perplexity-search.md
    workflow: 15
---

# Perplexity Search API

OpenClaw는 Perplexity Search API를 `web_search` provider로 지원합니다.
이 API는 `title`, `url`, `snippet` 필드를 가진 구조화된 결과를 반환합니다.

호환성을 위해 OpenClaw는 레거시 Perplexity Sonar/OpenRouter 설정도 지원합니다.
`OPENROUTER_API_KEY`를 사용하거나, `plugins.entries.perplexity.config.webSearch.apiKey`에 `sk-or-...` 키를 넣거나, `plugins.entries.perplexity.config.webSearch.baseUrl` / `model`을 설정하면 provider는 chat-completions 경로로 전환되며 구조화된 Search API 결과 대신 인용이 포함된 AI 합성 답변을 반환합니다.

## Perplexity API 키 받기

1. [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)에서 Perplexity 계정을 생성합니다
2. 대시보드에서 API 키를 생성합니다
3. 키를 구성에 저장하거나 Gateway 환경에서 `PERPLEXITY_API_KEY`를 설정합니다.

## OpenRouter 호환성

이미 OpenRouter로 Perplexity Sonar를 사용 중이라면 `provider: "perplexity"`를 그대로 유지하고 Gateway 환경에서 `OPENROUTER_API_KEY`를 설정하거나, `plugins.entries.perplexity.config.webSearch.apiKey`에 `sk-or-...` 키를 저장하세요.

선택적 호환성 제어:

- `plugins.entries.perplexity.config.webSearch.baseUrl`
- `plugins.entries.perplexity.config.webSearch.model`

## 구성 예시

### 네이티브 Perplexity Search API

```json5
{
  plugins: {
    entries: {
      perplexity: {
        config: {
          webSearch: {
            apiKey: "pplx-...",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "perplexity",
      },
    },
  },
}
```

### OpenRouter / Sonar 호환성

```json5
{
  plugins: {
    entries: {
      perplexity: {
        config: {
          webSearch: {
            apiKey: "<openrouter-api-key>",
            baseUrl: "https://openrouter.ai/api/v1",
            model: "perplexity/sonar-pro",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "perplexity",
      },
    },
  },
}
```

## 키를 설정하는 위치

**구성을 통한 방법:** `openclaw configure --section web`을 실행하세요. 키는
`~/.openclaw/openclaw.json`의 `plugins.entries.perplexity.config.webSearch.apiKey` 아래에 저장됩니다.
이 필드는 SecretRef 객체도 허용합니다.

**환경을 통한 방법:** Gateway 프로세스 환경에서 `PERPLEXITY_API_KEY` 또는 `OPENROUTER_API_KEY`를
설정하세요. gateway 설치의 경우에는
`~/.openclaw/.env`(또는 서비스 환경)에 넣으세요. 자세한 내용은 [Env vars](/ko/help/faq#env-vars-and-env-loading)를 참조하세요.

`provider: "perplexity"`가 구성되어 있고 Perplexity 키 SecretRef가 확인되지 않았으며 환경 대체값도 없으면, 시작/재로드는 즉시 실패합니다.

## 도구 매개변수

이 매개변수들은 네이티브 Perplexity Search API 경로에 적용됩니다.

| 매개변수              | 설명                                                     |
| --------------------- | -------------------------------------------------------- |
| `query`               | 검색어(필수)                                             |
| `count`               | 반환할 결과 수(1-10, 기본값: 5)                          |
| `country`             | 2자리 ISO 국가 코드(예: `"US"`, `"DE"`)                  |
| `language`            | ISO 639-1 언어 코드(예: `"en"`, `"de"`, `"fr"`)          |
| `freshness`           | 시간 필터: `day` (24시간), `week`, `month`, 또는 `year`  |
| `date_after`          | 이 날짜 이후에 게시된 결과만 포함(YYYY-MM-DD)            |
| `date_before`         | 이 날짜 이전에 게시된 결과만 포함(YYYY-MM-DD)            |
| `domain_filter`       | 도메인 허용 목록/차단 목록 배열(최대 20개)               |
| `max_tokens`          | 총 콘텐츠 예산(기본값: 25000, 최대값: 1000000)           |
| `max_tokens_per_page` | 페이지당 토큰 제한(기본값: 2048)                         |

레거시 Sonar/OpenRouter 호환 경로의 경우:

- `query`, `count`, `freshness`가 허용됩니다
- `count`는 그 경로에서는 호환성 전용이며, 응답은 여전히 N개 결과 목록이 아니라
  인용이 포함된 하나의 합성 답변입니다
- `country`, `language`, `date_after`,
  `date_before`, `domain_filter`, `max_tokens`, `max_tokens_per_page`와 같은 Search API 전용 필드는
  명시적인 오류를 반환합니다

**예시:**

```javascript
// Country and language-specific search
await web_search({
  query: "renewable energy",
  country: "DE",
  language: "de",
});

// Recent results (past week)
await web_search({
  query: "AI news",
  freshness: "week",
});

// Date range search
await web_search({
  query: "AI developments",
  date_after: "2024-01-01",
  date_before: "2024-06-30",
});

// Domain filtering (allowlist)
await web_search({
  query: "climate research",
  domain_filter: ["nature.com", "science.org", ".edu"],
});

// Domain filtering (denylist - prefix with -)
await web_search({
  query: "product reviews",
  domain_filter: ["-reddit.com", "-pinterest.com"],
});

// More content extraction
await web_search({
  query: "detailed AI research",
  max_tokens: 50000,
  max_tokens_per_page: 4096,
});
```

### 도메인 필터 규칙

- 필터당 최대 20개 도메인
- 하나의 요청에서 허용 목록과 차단 목록을 혼합할 수 없음
- 차단 목록 항목에는 `-` 접두사를 사용합니다(예: `["-reddit.com"]`)

## 참고 사항

- Perplexity Search API는 구조화된 웹 검색 결과(`title`, `url`, `snippet`)를 반환합니다
- OpenRouter 또는 명시적 `plugins.entries.perplexity.config.webSearch.baseUrl` / `model`을 사용하면 호환성을 위해 Perplexity는 다시 Sonar chat completions로 전환됩니다
- Sonar/OpenRouter 호환성은 구조화된 결과 행이 아니라 인용이 포함된 하나의 합성 답변을 반환합니다
- 결과는 기본적으로 15분 동안 캐시됩니다(`cacheTtlMinutes`로 구성 가능)

## 관련 문서

- [웹 검색 개요](/tools/web) -- 모든 provider 및 자동 감지
- [Perplexity Search API docs](https://docs.perplexity.ai/docs/search/quickstart) -- 공식 Perplexity 문서
- [Brave Search](/tools/brave-search) -- 국가/언어 필터가 포함된 구조화된 결과
- [Exa Search](/tools/exa-search) -- 콘텐츠 추출이 포함된 신경망 검색
