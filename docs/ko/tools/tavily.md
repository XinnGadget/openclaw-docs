---
read_when:
    - Tavily 기반 웹 검색을 원하는 경우
    - Tavily API 키가 필요한 경우
    - Tavily를 `web_search` 제공자로 사용하려는 경우
    - URL에서 콘텐츠를 추출하려는 경우
summary: Tavily 검색 및 추출 도구
title: Tavily
x-i18n:
    generated_at: "2026-04-05T12:58:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: db530cc101dc930611e4ca54e3d5972140f116bfe168adc939dc5752322d205e
    source_path: tools/tavily.md
    workflow: 15
---

# Tavily

OpenClaw는 **Tavily**를 두 가지 방식으로 사용할 수 있습니다:

- `web_search` 제공자로 사용
- 명시적인 plugin 도구인 `tavily_search` 및 `tavily_extract`로 사용

Tavily는 AI 애플리케이션을 위해 설계된 검색 API로, LLM 소비에 최적화된
구조화된 결과를 반환합니다. 구성 가능한 검색 깊이, 주제
필터링, 도메인 필터, AI 생성 답변 요약, URL에서의 콘텐츠 추출
(JavaScript로 렌더링된 페이지 포함)을 지원합니다.

## API 키 받기

1. [tavily.com](https://tavily.com/)에서 Tavily 계정을 만드세요.
2. 대시보드에서 API 키를 생성하세요.
3. 이를 config에 저장하거나 gateway 환경에 `TAVILY_API_KEY`를 설정하세요.

## Tavily 검색 구성

```json5
{
  plugins: {
    entries: {
      tavily: {
        enabled: true,
        config: {
          webSearch: {
            apiKey: "tvly-...", // TAVILY_API_KEY가 설정된 경우 선택 사항
            baseUrl: "https://api.tavily.com",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "tavily",
      },
    },
  },
}
```

참고:

- 온보딩 또는 `openclaw configure --section web`에서 Tavily를 선택하면
  번들된 Tavily plugin이 자동으로 활성화됩니다.
- Tavily 설정은 `plugins.entries.tavily.config.webSearch.*` 아래에 저장하세요.
- Tavily를 사용하는 `web_search`는 `query`와 `count`를 지원합니다(최대 20개 결과).
- `search_depth`, `topic`, `include_answer`,
  또는 도메인 필터 같은 Tavily 전용 제어가 필요하면 `tavily_search`를 사용하세요.

## Tavily plugin 도구

### `tavily_search`

일반적인
`web_search` 대신 Tavily 전용 검색 제어가 필요할 때 이것을 사용하세요.

| 매개변수         | 설명                                                           |
| ----------------- | --------------------------------------------------------------------- |
| `query`           | 검색 쿼리 문자열(400자 미만 권장)                       |
| `search_depth`    | `basic`(기본값, 균형형) 또는 `advanced`(가장 높은 관련성, 더 느림) |
| `topic`           | `general`(기본값), `news`(실시간 업데이트), 또는 `finance`         |
| `max_results`     | 결과 수, 1-20(기본값: 5)                                  |
| `include_answer`  | AI 생성 답변 요약 포함(기본값: false)               |
| `time_range`      | 최신성 기준 필터: `day`, `week`, `month`, 또는 `year`                  |
| `include_domains` | 결과를 제한할 도메인 배열                               |
| `exclude_domains` | 결과에서 제외할 도메인 배열                              |

**검색 깊이:**

| 깊이      | 속도  | 관련성 | 가장 적합한 용도                            |
| ---------- | ------ | --------- | ----------------------------------- |
| `basic`    | 더 빠름 | 높음      | 범용 쿼리(기본값)   |
| `advanced` | 더 느림 | 가장 높음   | 정밀성, 특정 사실, 조사 |

### `tavily_extract`

하나 이상의 URL에서 깔끔한 콘텐츠를 추출할 때 사용하세요.
JavaScript로 렌더링된 페이지를 처리하며, 대상 추출을 위해
쿼리 중심 청킹도 지원합니다.

| 매개변수           | 설명                                                |
| ------------------- | ---------------------------------------------------------- |
| `urls`              | 추출할 URL 배열(요청당 1-20개)                |
| `query`             | 이 쿼리와의 관련성 기준으로 추출된 청크 재정렬         |
| `extract_depth`     | `basic`(기본값, 빠름) 또는 `advanced`(JS가 많은 페이지용) |
| `chunks_per_source` | URL당 청크 수, 1-5(`query` 필요)                     |
| `include_images`    | 결과에 이미지 URL 포함(기본값: false)             |

**추출 깊이:**

| 깊이      | 사용 시점                               |
| ---------- | ----------------------------------------- |
| `basic`    | 단순한 페이지 - 먼저 이것을 시도             |
| `advanced` | JS 렌더링 SPA, 동적 콘텐츠, 표 |

팁:

- 요청당 최대 20개 URL. 더 큰 목록은 여러 호출로 나누세요.
- 전체 페이지 대신 관련 콘텐츠만 얻으려면 `query` + `chunks_per_source`를 사용하세요.
- 먼저 `basic`을 시도하고, 콘텐츠가 없거나 불완전하면 `advanced`로 폴백하세요.

## 적절한 도구 선택

| 필요                                 | 도구             |
| ------------------------------------ | ---------------- |
| 빠른 웹 검색, 특별한 옵션 없음 | `web_search`     |
| 깊이, 주제, AI 답변이 있는 검색 | `tavily_search`  |
| 특정 URL에서 콘텐츠 추출   | `tavily_extract` |

## 관련 문서

- [웹 검색 개요](/tools/web) -- 모든 제공자와 자동 감지
- [Firecrawl](/tools/firecrawl) -- 콘텐츠 추출이 포함된 검색 + 스크래핑
- [Exa Search](/tools/exa-search) -- 콘텐츠 추출이 포함된 신경망 검색
