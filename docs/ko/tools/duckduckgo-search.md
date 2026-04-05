---
read_when:
    - API 키가 필요 없는 웹 검색 프로바이더를 원하는 경우
    - '`web_search`에 DuckDuckGo를 사용하려는 경우'
    - 무설정 검색 폴백이 필요한 경우
summary: DuckDuckGo 웹 검색 -- 키 없이 사용하는 폴백 프로바이더(실험적, HTML 기반)
title: DuckDuckGo Search
x-i18n:
    generated_at: "2026-04-05T12:56:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 31f8e3883584534396c247c3d8069ea4c5b6399e0ff13a9dd0c8ee0c3da02096
    source_path: tools/duckduckgo-search.md
    workflow: 15
---

# DuckDuckGo Search

OpenClaw는 DuckDuckGo를 **키 없이 사용하는** `web_search` 프로바이더로 지원합니다. API
키나 계정이 필요하지 않습니다.

<Warning>
  DuckDuckGo는 DuckDuckGo의 비자바스크립트 검색 페이지에서 결과를 가져오는
  **실험적이고 비공식적인** 통합이며, 공식 API가 아닙니다. 봇 챌린지 페이지나
  HTML 변경으로 인해 간헐적으로 깨질 수 있습니다.
</Warning>

## 설정

API 키는 필요 없습니다. DuckDuckGo를 프로바이더로 설정하기만 하면 됩니다:

<Steps>
  <Step title="구성">
    ```bash
    openclaw configure --section web
    # 프로바이더로 "duckduckgo" 선택
    ```
  </Step>
</Steps>

## Config

```json5
{
  tools: {
    web: {
      search: {
        provider: "duckduckgo",
      },
    },
  },
}
```

지역 및 SafeSearch를 위한 선택적 플러그인 수준 설정:

```json5
{
  plugins: {
    entries: {
      duckduckgo: {
        config: {
          webSearch: {
            region: "us-en", // DuckDuckGo 지역 코드
            safeSearch: "moderate", // "strict", "moderate", 또는 "off"
          },
        },
      },
    },
  },
}
```

## 도구 매개변수

| 매개변수     | 설명                                                         |
| ------------ | ------------------------------------------------------------ |
| `query`      | 검색어(필수)                                                 |
| `count`      | 반환할 결과 수(1-10, 기본값: 5)                              |
| `region`     | DuckDuckGo 지역 코드(예: `us-en`, `uk-en`, `de-de`)          |
| `safeSearch` | SafeSearch 수준: `strict`, `moderate`(기본값), 또는 `off`    |

지역 및 SafeSearch는 플러그인 config에서도 설정할 수 있습니다(위 참조). 도구
매개변수는 쿼리별로 config 값을 재정의합니다.

## 참고

- **API 키 없음** — 즉시 사용 가능하며, 설정이 필요 없습니다
- **실험적** — DuckDuckGo의 비자바스크립트 HTML 검색 페이지에서 결과를 수집하며,
  공식 API나 SDK가 아닙니다
- **봇 챌린지 위험** — 사용량이 많거나 자동화된 사용에서는 DuckDuckGo가 CAPTCHA를
  제공하거나 요청을 차단할 수 있습니다
- **HTML 파싱** — 결과는 예고 없이 변경될 수 있는 페이지 구조에 따라 달라집니다
- **자동 감지 순서** — DuckDuckGo는 자동 감지에서 첫 번째 키 없는 폴백
  (순서 100)입니다. 키가 구성된 API 기반 프로바이더가 먼저 실행되고,
  그다음 Ollama Web Search(순서 110), 그다음 SearXNG(순서 200)가 실행됩니다
- 구성되지 않은 경우 **SafeSearch 기본값은 moderate**입니다

<Tip>
  프로덕션 용도로는 [Brave Search](/tools/brave-search)(무료 티어 사용 가능) 또는
  다른 API 기반 프로바이더를 고려하세요.
</Tip>

## 관련

- [웹 검색 개요](/tools/web) -- 모든 프로바이더와 자동 감지
- [Brave Search](/tools/brave-search) -- 무료 티어가 있는 구조화된 결과
- [Exa Search](/tools/exa-search) -- 콘텐츠 추출이 포함된 뉴럴 검색
