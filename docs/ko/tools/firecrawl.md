---
read_when:
    - Firecrawl 기반 웹 추출을 사용하려는 경우
    - Firecrawl API 키가 필요한 경우
    - 웹 검색 공급자로 Firecrawl을 사용하려는 경우
    - '`web_fetch`에 안티봇 추출을 사용하려는 경우'
summary: Firecrawl 검색, 스크래핑 및 `web_fetch` 폴백
title: Firecrawl
x-i18n:
    generated_at: "2026-04-05T12:56:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 45f17fc4b8e81e1bfe25f510b0a64ab0d50c4cc95bcf88d6ba7c62cece26162e
    source_path: tools/firecrawl.md
    workflow: 15
---

# Firecrawl

OpenClaw는 **Firecrawl**을 세 가지 방식으로 사용할 수 있습니다:

- `web_search` 공급자로 사용
- 명시적 plugin 도구인 `firecrawl_search` 및 `firecrawl_scrape`로 사용
- `web_fetch`용 폴백 추출기로 사용

이는 봇 우회 및 캐싱을 지원하는 호스팅 추출/검색 서비스로, JS가 많은 사이트나 일반 HTTP 가져오기를 차단하는 페이지에 도움이 됩니다.

## API 키 받기

1. Firecrawl 계정을 만들고 API 키를 생성합니다.
2. 구성에 저장하거나 gateway 환경에 `FIRECRAWL_API_KEY`를 설정합니다.

## Firecrawl 검색 구성

```json5
{
  tools: {
    web: {
      search: {
        provider: "firecrawl",
      },
    },
  },
  plugins: {
    entries: {
      firecrawl: {
        enabled: true,
        config: {
          webSearch: {
            apiKey: "FIRECRAWL_API_KEY_HERE",
            baseUrl: "https://api.firecrawl.dev",
          },
        },
      },
    },
  },
}
```

참고:

- 온보딩 또는 `openclaw configure --section web`에서 Firecrawl을 선택하면 번들 Firecrawl plugin이 자동으로 활성화됩니다.
- Firecrawl을 사용하는 `web_search`는 `query`와 `count`를 지원합니다.
- `sources`, `categories`, 결과 스크래핑과 같은 Firecrawl 전용 제어가 필요하면 `firecrawl_search`를 사용하세요.
- `baseUrl` 재정의는 `https://api.firecrawl.dev`에 유지되어야 합니다.
- `FIRECRAWL_BASE_URL`은 Firecrawl 검색 및 스크래핑 base URL에 대한 공통 환경 변수 폴백입니다.

## Firecrawl 스크래핑 + `web_fetch` 폴백 구성

```json5
{
  plugins: {
    entries: {
      firecrawl: {
        enabled: true,
        config: {
          webFetch: {
            apiKey: "FIRECRAWL_API_KEY_HERE",
            baseUrl: "https://api.firecrawl.dev",
            onlyMainContent: true,
            maxAgeMs: 172800000,
            timeoutSeconds: 60,
          },
        },
      },
    },
  },
}
```

참고:

- Firecrawl 폴백 시도는 API 키(`plugins.entries.firecrawl.config.webFetch.apiKey` 또는 `FIRECRAWL_API_KEY`)가 있을 때만 실행됩니다.
- `maxAgeMs`는 캐시된 결과의 허용 최대 경과 시간(ms)을 제어합니다. 기본값은 2일입니다.
- 레거시 `tools.web.fetch.firecrawl.*` 구성은 `openclaw doctor --fix`로 자동 마이그레이션됩니다.
- Firecrawl 스크래핑/base URL 재정의는 `https://api.firecrawl.dev`로 제한됩니다.

`firecrawl_scrape`는 동일한 `plugins.entries.firecrawl.config.webFetch.*` 설정 및 환경 변수를 재사용합니다.

## Firecrawl plugin 도구

### `firecrawl_search`

일반 `web_search` 대신 Firecrawl 전용 검색 제어가 필요할 때 사용하세요.

핵심 매개변수:

- `query`
- `count`
- `sources`
- `categories`
- `scrapeResults`
- `timeoutSeconds`

### `firecrawl_scrape`

일반 `web_fetch`가 약한 JS 중심 또는 봇 보호 페이지에 사용하세요.

핵심 매개변수:

- `url`
- `extractMode`
- `maxChars`
- `onlyMainContent`
- `maxAgeMs`
- `proxy`
- `storeInCache`
- `timeoutSeconds`

## Stealth / 봇 우회

Firecrawl은 봇 우회를 위한 **프록시 모드** 매개변수(`basic`, `stealth`, `auto`)를 제공합니다.
OpenClaw는 Firecrawl 요청에 대해 항상 `proxy: "auto"`와 `storeInCache: true`를 사용합니다.
프록시가 생략되면 Firecrawl은 기본적으로 `auto`를 사용합니다. `auto`는 기본 시도가 실패하면 stealth 프록시로 재시도하므로 basic 전용 스크래핑보다 더 많은 크레딧을 사용할 수 있습니다.

## `web_fetch`가 Firecrawl을 사용하는 방식

`web_fetch` 추출 순서:

1. Readability(로컬)
2. Firecrawl(선택되었거나 활성 `web_fetch` 폴백으로 자동 감지된 경우)
3. 기본 HTML 정리(마지막 폴백)

선택 설정 항목은 `tools.web.fetch.provider`입니다. 이를 생략하면 OpenClaw는 사용 가능한 자격 증명에서 준비된 첫 번째 `web_fetch` 공급자를 자동 감지합니다.
현재 번들 공급자는 Firecrawl입니다.

## 관련 문서

- [웹 검색 개요](/tools/web) -- 모든 공급자 및 자동 감지
- [Web Fetch](/tools/web-fetch) -- Firecrawl 폴백이 있는 `web_fetch` 도구
- [Tavily](/tools/tavily) -- 검색 + 추출 도구
