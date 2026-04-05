---
read_when:
    - 웹 검색에 Gemini를 사용하려고 합니다
    - '`GEMINI_API_KEY`가 필요합니다'
    - Google Search grounding을 사용하려고 합니다
summary: Google Search grounding을 사용하는 Gemini 웹 검색
title: Gemini Search
x-i18n:
    generated_at: "2026-04-05T12:56:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 42644176baca6b4b041142541618f6f68361d410d6f425cc4104cd88d9f7c480
    source_path: tools/gemini-search.md
    workflow: 15
---

# Gemini Search

OpenClaw는 내장된
[Google Search grounding](https://ai.google.dev/gemini-api/docs/grounding)을
지원하는 Gemini 모델을 지원합니다. 이 기능은 인용과 함께 실시간 Google Search 결과를 바탕으로 한 AI 합성 답변을 반환합니다.

## API 키 가져오기

<Steps>
  <Step title="키 만들기">
    [Google AI Studio](https://aistudio.google.com/apikey)로 이동해
    API 키를 만드세요.
  </Step>
  <Step title="키 저장하기">
    Gateway 환경에 `GEMINI_API_KEY`를 설정하거나, 다음을 통해 구성하세요:

    ```bash
    openclaw configure --section web
    ```

  </Step>
</Steps>

## config

```json5
{
  plugins: {
    entries: {
      google: {
        config: {
          webSearch: {
            apiKey: "AIza...", // GEMINI_API_KEY가 설정되어 있으면 선택 사항
            model: "gemini-2.5-flash", // 기본값
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "gemini",
      },
    },
  },
}
```

**환경 변수 대안:** Gateway 환경에 `GEMINI_API_KEY`를 설정하세요.
gateway 설치의 경우 `~/.openclaw/.env`에 넣으세요.

## 동작 방식

링크와 스니펫 목록을 반환하는 기존 검색 제공자와 달리,
Gemini는 Google Search grounding을 사용해 인라인 인용이 포함된
AI 합성 답변을 생성합니다. 결과에는 합성된 답변과 소스
URL이 모두 포함됩니다.

- Gemini grounding의 인용 URL은 Google
  리디렉션 URL에서 직접 URL로 자동 해석됩니다.
- 리디렉션 해석은 최종 인용 URL을 반환하기 전에 SSRF 가드 경로(HEAD + 리디렉션 확인 +
  http/https 검증)를 사용합니다.
- 리디렉션 해석은 엄격한 SSRF 기본값을 사용하므로
  비공개/내부 대상으로의 리디렉션은 차단됩니다.

## 지원되는 매개변수

Gemini 검색은 `query`를 지원합니다.

`count`는 공유 `web_search` 호환성을 위해 허용되지만, Gemini grounding은
여전히 N개 결과 목록이 아니라 인용이 포함된 하나의 합성 답변을 반환합니다.

`country`, `language`, `freshness`, `domain_filter` 같은
제공자별 필터는 지원되지 않습니다.

## 모델 선택

기본 모델은 `gemini-2.5-flash`입니다(빠르고 비용 효율적).
grounding을 지원하는 모든 Gemini 모델은
`plugins.entries.google.config.webSearch.model`을 통해 사용할 수 있습니다.

## 관련 문서

- [웹 검색 개요](/tools/web) -- 모든 제공자와 자동 감지
- [Brave Search](/tools/brave-search) -- 스니펫이 포함된 구조화된 결과
- [Perplexity Search](/tools/perplexity-search) -- 구조화된 결과 + 콘텐츠 추출
