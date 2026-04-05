---
read_when:
    - '`web_search`를 활성화하거나 구성하려는 경우'
    - '`x_search`를 활성화하거나 구성하려는 경우'
    - 검색 프로바이더를 선택해야 하는 경우
    - 자동 감지와 프로바이더 폴백을 이해하려는 경우
sidebarTitle: Web Search
summary: web_search, x_search, 및 web_fetch -- 웹 검색, X 게시물 검색, 또는 페이지 콘텐츠 가져오기
title: 웹 검색
x-i18n:
    generated_at: "2026-04-05T12:59:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: b8b9a5d641dcdcbe7c099c8862898f12646f43151b6c4152d69c26af9b17e0fa
    source_path: tools/web.md
    workflow: 15
---

# 웹 검색

`web_search` 도구는 구성된 프로바이더를 사용해 웹을 검색하고
결과를 반환합니다. 결과는 쿼리별로 15분 동안 캐시됩니다(구성 가능).

OpenClaw에는 X(구 Twitter) 게시물을 위한 `x_search`와
경량 URL 가져오기를 위한 `web_fetch`도 포함되어 있습니다. 이 단계에서 `web_fetch`는
로컬로 유지되며, `web_search`와 `x_search`는 내부적으로 xAI Responses를 사용할 수 있습니다.

<Info>
  `web_search`는 브라우저 자동화가 아니라 경량 HTTP 도구입니다. JS 비중이 높은 사이트나 로그인에는 [웹 브라우저](/tools/browser)를 사용하세요. 특정 URL을 가져오려면 [Web Fetch](/tools/web-fetch)를 사용하세요.
</Info>

## 빠른 시작

<Steps>
  <Step title="프로바이더 선택">
    프로바이더를 선택하고 필요한 설정을 완료하세요. 일부 프로바이더는
    키 없이 사용할 수 있고, 다른 프로바이더는 API 키를 사용합니다. 자세한 내용은
    아래 프로바이더 페이지를 참고하세요.
  </Step>
  <Step title="구성">
    ```bash
    openclaw configure --section web
    ```
    이렇게 하면 프로바이더와 필요한 자격 증명이 저장됩니다. API 기반
    프로바이더의 경우 env var(예: `BRAVE_API_KEY`)를 설정하고 이 단계를 건너뛸 수도 있습니다.
  </Step>
  <Step title="사용">
    이제 에이전트가 `web_search`를 호출할 수 있습니다:

    ```javascript
    await web_search({ query: "OpenClaw plugin SDK" });
    ```

    X 게시물에는 다음을 사용하세요:

    ```javascript
    await x_search({ query: "dinner recipes" });
    ```

  </Step>
</Steps>

## 프로바이더 선택

<CardGroup cols={2}>
  <Card title="Brave Search" icon="shield" href="/tools/brave-search">
    스니펫이 포함된 구조화된 결과입니다. `llm-context` 모드, 국가/언어 필터를 지원합니다. 무료 티어를 사용할 수 있습니다.
  </Card>
  <Card title="DuckDuckGo" icon="bird" href="/tools/duckduckgo-search">
    키 없는 폴백입니다. API 키가 필요 없습니다. 비공식 HTML 기반 통합입니다.
  </Card>
  <Card title="Exa" icon="brain" href="/tools/exa-search">
    콘텐츠 추출(하이라이트, 텍스트, 요약)이 포함된 뉴럴 + 키워드 검색입니다.
  </Card>
  <Card title="Firecrawl" icon="flame" href="/tools/firecrawl">
    구조화된 결과입니다. 심층 추출에는 `firecrawl_search` 및 `firecrawl_scrape`와 함께 사용하는 것이 가장 좋습니다.
  </Card>
  <Card title="Gemini" icon="sparkles" href="/tools/gemini-search">
    Google Search grounding을 통한 인용 포함 AI 합성 답변입니다.
  </Card>
  <Card title="Grok" icon="zap" href="/tools/grok-search">
    xAI 웹 grounding을 통한 인용 포함 AI 합성 답변입니다.
  </Card>
  <Card title="Kimi" icon="moon" href="/tools/kimi-search">
    Moonshot 웹 검색을 통한 인용 포함 AI 합성 답변입니다.
  </Card>
  <Card title="MiniMax Search" icon="globe" href="/tools/minimax-search">
    MiniMax Coding Plan 검색 API를 통한 구조화된 결과입니다.
  </Card>
  <Card title="Ollama Web Search" icon="globe" href="/tools/ollama-search">
    구성된 Ollama 호스트를 통한 키 없는 검색입니다. `ollama signin`이 필요합니다.
  </Card>
  <Card title="Perplexity" icon="search" href="/tools/perplexity-search">
    콘텐츠 추출 제어 및 도메인 필터링이 포함된 구조화된 결과입니다.
  </Card>
  <Card title="SearXNG" icon="server" href="/tools/searxng-search">
    셀프 호스팅 메타 검색입니다. API 키가 필요 없습니다. Google, Bing, DuckDuckGo 등을 집계합니다.
  </Card>
  <Card title="Tavily" icon="globe" href="/tools/tavily">
    검색 깊이, 주제 필터링, URL 추출을 위한 `tavily_extract`가 포함된 구조화된 결과입니다.
  </Card>
</CardGroup>

### 프로바이더 비교

| 프로바이더                                  | 결과 형식                  | 필터                                            | API 키                                                                           |
| ----------------------------------------- | -------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------- |
| [Brave](/tools/brave-search)              | 구조화된 스니펫            | 국가, 언어, 시간, `llm-context` 모드             | `BRAVE_API_KEY`                                                                  |
| [DuckDuckGo](/tools/duckduckgo-search)    | 구조화된 스니펫            | --                                               | 없음(키 없음)                                                                    |
| [Exa](/tools/exa-search)                  | 구조화 + 추출              | 뉴럴/키워드 모드, 날짜, 콘텐츠 추출              | `EXA_API_KEY`                                                                    |
| [Firecrawl](/tools/firecrawl)             | 구조화된 스니펫            | `firecrawl_search` 도구를 통해                   | `FIRECRAWL_API_KEY`                                                              |
| [Gemini](/tools/gemini-search)            | AI 합성 + 인용             | --                                               | `GEMINI_API_KEY`                                                                 |
| [Grok](/tools/grok-search)                | AI 합성 + 인용             | --                                               | `XAI_API_KEY`                                                                    |
| [Kimi](/tools/kimi-search)                | AI 합성 + 인용             | --                                               | `KIMI_API_KEY` / `MOONSHOT_API_KEY`                                              |
| [MiniMax Search](/tools/minimax-search)   | 구조화된 스니펫            | 지역 (`global` / `cn`)                           | `MINIMAX_CODE_PLAN_KEY` / `MINIMAX_CODING_API_KEY`                               |
| [Ollama Web Search](/tools/ollama-search) | 구조화된 스니펫            | --                                               | 기본적으로 없음; `ollama signin` 필요, Ollama 프로바이더 bearer auth 재사용 가능 |
| [Perplexity](/tools/perplexity-search)    | 구조화된 스니펫            | 국가, 언어, 시간, 도메인, 콘텐츠 제한            | `PERPLEXITY_API_KEY` / `OPENROUTER_API_KEY`                                      |
| [SearXNG](/tools/searxng-search)          | 구조화된 스니펫            | 카테고리, 언어                                   | 없음(셀프 호스팅)                                                                |
| [Tavily](/tools/tavily)                   | 구조화된 스니펫            | `tavily_search` 도구를 통해                      | `TAVILY_API_KEY`                                                                 |

## 자동 감지

## 네이티브 Codex 웹 검색

Codex 지원 모델은 선택적으로 OpenClaw가 관리하는 `web_search` 함수 대신 프로바이더 네이티브 Responses `web_search` 도구를 사용할 수 있습니다.

- `tools.web.search.openaiCodex` 아래에서 구성합니다
- Codex 지원 모델에서만 활성화됩니다(`openai-codex/*` 또는 `api: "openai-codex-responses"`를 사용하는 프로바이더)
- 관리형 `web_search`는 Codex가 아닌 모델에 계속 적용됩니다
- `mode: "cached"`가 기본값이며 권장 설정입니다
- `tools.web.search.enabled: false`는 관리형 검색과 네이티브 검색을 모두 비활성화합니다

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        openaiCodex: {
          enabled: true,
          mode: "cached",
          allowedDomains: ["example.com"],
          contextSize: "high",
          userLocation: {
            country: "US",
            city: "New York",
            timezone: "America/New_York",
          },
        },
      },
    },
  },
}
```

네이티브 Codex 검색이 활성화되어 있어도 현재 모델이 Codex를 지원하지 않으면, OpenClaw는 일반적인 관리형 `web_search` 동작을 유지합니다.

## 웹 검색 설정

문서와 설정 흐름의 프로바이더 목록은 알파벳순입니다. 자동 감지는
별도의 우선순위 순서를 유지합니다.

`provider`가 설정되지 않은 경우, OpenClaw는 다음 순서로 프로바이더를 확인하고 준비된 첫 번째 것을 사용합니다:

먼저 API 기반 프로바이더:

1. **Brave** -- `BRAVE_API_KEY` 또는 `plugins.entries.brave.config.webSearch.apiKey` (순서 10)
2. **MiniMax Search** -- `MINIMAX_CODE_PLAN_KEY` / `MINIMAX_CODING_API_KEY` 또는 `plugins.entries.minimax.config.webSearch.apiKey` (순서 15)
3. **Gemini** -- `GEMINI_API_KEY` 또는 `plugins.entries.google.config.webSearch.apiKey` (순서 20)
4. **Grok** -- `XAI_API_KEY` 또는 `plugins.entries.xai.config.webSearch.apiKey` (순서 30)
5. **Kimi** -- `KIMI_API_KEY` / `MOONSHOT_API_KEY` 또는 `plugins.entries.moonshot.config.webSearch.apiKey` (순서 40)
6. **Perplexity** -- `PERPLEXITY_API_KEY` / `OPENROUTER_API_KEY` 또는 `plugins.entries.perplexity.config.webSearch.apiKey` (순서 50)
7. **Firecrawl** -- `FIRECRAWL_API_KEY` 또는 `plugins.entries.firecrawl.config.webSearch.apiKey` (순서 60)
8. **Exa** -- `EXA_API_KEY` 또는 `plugins.entries.exa.config.webSearch.apiKey` (순서 65)
9. **Tavily** -- `TAVILY_API_KEY` 또는 `plugins.entries.tavily.config.webSearch.apiKey` (순서 70)

그다음 키 없는 폴백:

10. **DuckDuckGo** -- 계정이나 API 키가 필요 없는 키 없는 HTML 폴백 (순서 100)
11. **Ollama Web Search** -- 구성된 Ollama 호스트를 통한 키 없는 폴백; Ollama에 접근 가능해야 하고 `ollama signin`으로 로그인되어 있어야 하며, 호스트에 필요할 경우 Ollama 프로바이더 bearer auth를 재사용할 수 있음 (순서 110)
12. **SearXNG** -- `SEARXNG_BASE_URL` 또는 `plugins.entries.searxng.config.webSearch.baseUrl` (순서 200)

감지된 프로바이더가 없으면 Brave로 폴백합니다(구성하라는 누락 키
오류가 표시됩니다).

<Note>
  모든 프로바이더 키 필드는 SecretRef 객체를 지원합니다. 자동 감지 모드에서는
  OpenClaw가 선택된 프로바이더 키만 해결하며, 선택되지 않은 SecretRef는
  비활성 상태로 유지됩니다.
</Note>

## Config

```json5
{
  tools: {
    web: {
      search: {
        enabled: true, // 기본값: true
        provider: "brave", // 또는 자동 감지를 위해 생략
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
    },
  },
}
```

프로바이더별 config(API 키, base URL, 모드)는
`plugins.entries.<plugin>.config.webSearch.*` 아래에 있습니다. 예시는
프로바이더 페이지를 참고하세요.

`web_fetch` 폴백 프로바이더 선택은 별도입니다:

- `tools.web.fetch.provider`로 선택
- 또는 해당 필드를 생략하고 사용 가능한 자격 증명에서 준비된 첫 번째 web-fetch
  프로바이더를 OpenClaw가 자동 감지하도록 할 수 있습니다
- 현재 번들 web-fetch 프로바이더는 Firecrawl이며,
  `plugins.entries.firecrawl.config.webFetch.*` 아래에서 구성합니다

`openclaw onboard` 또는
`openclaw configure --section web` 중 **Kimi**를 선택하면, OpenClaw는 다음도 물을 수 있습니다:

- Moonshot API 지역 (`https://api.moonshot.ai/v1` 또는 `https://api.moonshot.cn/v1`)
- 기본 Kimi 웹 검색 모델(기본값 `kimi-k2.5`)

`x_search`의 경우 `plugins.entries.xai.config.xSearch.*`를 구성하세요. 이 기능은
Grok 웹 검색과 동일한 `XAI_API_KEY` 폴백을 사용합니다.
레거시 `tools.web.x_search.*` config는 `openclaw doctor --fix`로 자동 마이그레이션됩니다.
`openclaw onboard` 또는 `openclaw configure --section web` 중 Grok을 선택하면,
OpenClaw는 동일한 키로 선택적 `x_search` 설정도 제공할 수 있습니다.
이는 Grok 경로 내부의 별도 후속 단계이며, 별도의 최상위
웹 검색 프로바이더 선택이 아닙니다. 다른 프로바이더를 선택하면 OpenClaw는 `x_search` 프롬프트를 표시하지 않습니다.

### API 키 저장

<Tabs>
  <Tab title="Config 파일">
    `openclaw configure --section web`를 실행하거나 키를 직접 설정하세요:

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "YOUR_KEY", // pragma: allowlist secret
              },
            },
          },
        },
      },
    }
    ```

  </Tab>
  <Tab title="환경 변수">
    Gateway 프로세스 환경에 프로바이더 env var를 설정하세요:

    ```bash
    export BRAVE_API_KEY="YOUR_KEY"
    ```

    게이트웨이 설치의 경우 `~/.openclaw/.env`에 넣으세요.
    [환경 변수](/ko/help/faq#env-vars-and-env-loading)를 참고하세요.

  </Tab>
</Tabs>

## 도구 매개변수

| 매개변수             | 설명                                                  |
| --------------------- | ----------------------------------------------------- |
| `query`               | 검색어(필수)                                          |
| `count`               | 반환할 결과 수(1-10, 기본값: 5)                       |
| `country`             | 2자리 ISO 국가 코드(예: "US", "DE")                   |
| `language`            | ISO 639-1 언어 코드(예: "en", "de")                   |
| `search_lang`         | 검색 언어 코드(Brave 전용)                            |
| `freshness`           | 시간 필터: `day`, `week`, `month`, 또는 `year`        |
| `date_after`          | 이 날짜 이후 결과(YYYY-MM-DD)                         |
| `date_before`         | 이 날짜 이전 결과(YYYY-MM-DD)                         |
| `ui_lang`             | UI 언어 코드(Brave 전용)                              |
| `domain_filter`       | 도메인 allowlist/denylist 배열(Perplexity 전용)       |
| `max_tokens`          | 총 콘텐츠 예산, 기본값 25000(Perplexity 전용)         |
| `max_tokens_per_page` | 페이지당 토큰 한도, 기본값 2048(Perplexity 전용)      |

<Warning>
  모든 매개변수가 모든 프로바이더에서 동작하는 것은 아닙니다. Brave `llm-context` 모드는
  `ui_lang`, `freshness`, `date_after`, `date_before`를 거부합니다.
  Gemini, Grok, Kimi는 인용이 포함된 하나의 합성 답변을 반환합니다. 이들은
  공유 도구 호환성을 위해 `count`를 받지만, grounded 답변의 형식은 바꾸지 않습니다.
  Sonar/OpenRouter 호환 경로(`plugins.entries.perplexity.config.webSearch.baseUrl` /
  `model` 또는 `OPENROUTER_API_KEY`)를 사용할 때 Perplexity도 같은 방식으로 동작합니다.
  SearXNG는 신뢰할 수 있는 사설 네트워크 또는 loopback 호스트에 대해서만 `http://`를 허용합니다.
  공개 SearXNG 엔드포인트는 `https://`를 사용해야 합니다.
  Firecrawl과 Tavily는 `web_search`를 통해서는 `query`와 `count`만 지원합니다.
  고급 옵션에는 전용 도구를 사용하세요.
</Warning>

## x_search

`x_search`는 xAI를 사용해 X(구 Twitter) 게시물을 질의하고
인용이 포함된 AI 합성 답변을 반환합니다. 자연어 쿼리와
선택적 구조화 필터를 받습니다. OpenClaw는 이 도구 호출을 처리하는 요청에서만 내장 xAI `x_search`
도구를 활성화합니다.

<Note>
  xAI 문서에 따르면 `x_search`는 키워드 검색, 의미 검색, 사용자
  검색 및 스레드 가져오기를 지원합니다. 리포스트, 답글, 북마크, 조회수 같은 게시물별 참여 통계는
  정확한 게시물 URL 또는 status ID에 대한 표적 조회를 우선 사용하세요.
  광범위한 키워드 검색으로도 올바른 게시물을 찾을 수는 있지만, 게시물별 메타데이터가 덜 완전할 수 있습니다.
  좋은 패턴은 먼저 게시물을 찾고, 그런 다음 해당 정확한 게시물에 초점을 맞춘 두 번째 `x_search` 쿼리를 실행하는 것입니다.
</Note>

### x_search config

```json5
{
  plugins: {
    entries: {
      xai: {
        config: {
          xSearch: {
            enabled: true,
            model: "grok-4-1-fast-non-reasoning",
            inlineCitations: false,
            maxTurns: 2,
            timeoutSeconds: 30,
            cacheTtlMinutes: 15,
          },
          webSearch: {
            apiKey: "xai-...", // XAI_API_KEY가 설정된 경우 선택 사항
          },
        },
      },
    },
  },
}
```

### x_search 매개변수

| 매개변수                    | 설명                                                 |
| ---------------------------- | --------------------------------------------------- |
| `query`                      | 검색어(필수)                                        |
| `allowed_x_handles`          | 결과를 특정 X 핸들로 제한                           |
| `excluded_x_handles`         | 특정 X 핸들 제외                                    |
| `from_date`                  | 이 날짜(YYYY-MM-DD) 이후 게시물만 포함              |
| `to_date`                    | 이 날짜(YYYY-MM-DD) 이전 게시물만 포함              |
| `enable_image_understanding` | xAI가 일치하는 게시물에 첨부된 이미지를 검사하도록 허용 |
| `enable_video_understanding` | xAI가 일치하는 게시물에 첨부된 비디오를 검사하도록 허용 |

### x_search 예시

```javascript
await x_search({
  query: "dinner recipes",
  allowed_x_handles: ["nytfood"],
  from_date: "2026-03-01",
});
```

```javascript
// 가능하면 정확한 status URL 또는 status ID를 사용해 게시물별 통계를 조회하세요
await x_search({
  query: "https://x.com/huntharo/status/1905678901234567890",
});
```

## 예시

```javascript
// 기본 검색
await web_search({ query: "OpenClaw plugin SDK" });

// 독일 대상 검색
await web_search({ query: "TV online schauen", country: "DE", language: "de" });

// 최신 결과(지난 1주)
await web_search({ query: "AI developments", freshness: "week" });

// 날짜 범위
await web_search({
  query: "climate research",
  date_after: "2024-01-01",
  date_before: "2024-06-30",
});

// 도메인 필터링(Perplexity 전용)
await web_search({
  query: "product reviews",
  domain_filter: ["-reddit.com", "-pinterest.com"],
});
```

## 도구 프로필

도구 프로필이나 allowlist를 사용하는 경우 `web_search`, `x_search`, 또는 `group:web`를 추가하세요:

```json5
{
  tools: {
    allow: ["web_search", "x_search"],
    // 또는: allow: ["group:web"]  (web_search, x_search, web_fetch 포함)
  },
}
```

## 관련

- [Web Fetch](/tools/web-fetch) -- URL을 가져와 읽기 쉬운 콘텐츠 추출
- [웹 브라우저](/tools/browser) -- JS 비중이 높은 사이트를 위한 전체 브라우저 자동화
- [Grok Search](/tools/grok-search) -- `web_search` 프로바이더로서의 Grok
- [Ollama Web Search](/tools/ollama-search) -- Ollama 호스트를 통한 키 없는 웹 검색
