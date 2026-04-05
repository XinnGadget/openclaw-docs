---
read_when:
    - '`web_search`에 Grok를 사용하려는 경우'
    - 웹 검색용 `XAI_API_KEY`가 필요한 경우
summary: xAI 웹 기반 응답을 통한 Grok 웹 검색
title: Grok 검색
x-i18n:
    generated_at: "2026-04-05T12:56:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: ae2343012eebbe75d3ecdde3cb4470415c3275b694d0339bc26c46675a652054
    source_path: tools/grok-search.md
    workflow: 15
---

# Grok 검색

OpenClaw는 Grok를 `web_search` 제공자로 지원하며, xAI의 웹 기반
응답을 사용해 실시간 검색 결과와 인용을 바탕으로 한 AI 합성 답변을
생성합니다.

같은 `XAI_API_KEY`는 X
(이전 Twitter) 게시물 검색용 내장 `x_search` 도구에도 사용할 수 있습니다. 키를
`plugins.entries.xai.config.webSearch.apiKey` 아래에 저장하면 OpenClaw는 이제 이를
번들 xAI 모델 제공자에도 폴백으로 재사용합니다.

리포스트, 답글, 북마크, 조회수 같은 게시물 수준 X 지표가 필요하면
넓은 검색 쿼리 대신 정확한 게시물 URL 또는 상태 ID와 함께
`x_search`를 사용하는 것이 좋습니다.

## 온보딩 및 설정

다음 중 하나에서 **Grok**를 선택하면:

- `openclaw onboard`
- `openclaw configure --section web`

OpenClaw는 같은
`XAI_API_KEY`로 `x_search`를 활성화하는 별도의 후속 단계를 표시할 수 있습니다. 이 후속 단계는 다음과 같습니다:

- `web_search`에 Grok를 선택한 뒤에만 표시됩니다
- 별도의 최상위 웹 검색 제공자 선택지는 아닙니다
- 같은 흐름에서 `x_search` 모델을 선택적으로 설정할 수 있습니다

이를 건너뛰면 나중에 config에서 `x_search`를 활성화하거나 변경할 수 있습니다.

## API 키 받기

<Steps>
  <Step title="키 만들기">
    [xAI](https://console.x.ai/)에서 API 키를 발급받으세요.
  </Step>
  <Step title="키 저장하기">
    Gateway 환경에 `XAI_API_KEY`를 설정하거나 다음으로 구성하세요:

    ```bash
    openclaw configure --section web
    ```

  </Step>
</Steps>

## 설정

```json5
{
  plugins: {
    entries: {
      xai: {
        config: {
          webSearch: {
            apiKey: "xai-...", // XAI_API_KEY가 설정된 경우 선택 사항
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "grok",
      },
    },
  },
}
```

**환경 변수 대안:** Gateway 환경에 `XAI_API_KEY`를 설정하세요.
gateway 설치의 경우 `~/.openclaw/.env`에 넣으세요.

## 작동 방식

Grok는 xAI 웹 기반 응답을 사용해
Gemini의 Google Search grounding 방식과 유사하게 인라인
인용이 포함된 답변을 합성합니다.

## 지원되는 매개변수

Grok 검색은 `query`를 지원합니다.

`count`도 공유 `web_search` 호환성을 위해 허용되지만, Grok는 여전히
N개 결과 목록이 아니라 인용이 포함된 하나의 합성 답변을 반환합니다.

제공자별 필터는 현재 지원되지 않습니다.

## 관련 문서

- [웹 검색 개요](/tools/web) -- 모든 제공자와 자동 감지
- [웹 검색의 x_search](/tools/web#x_search) -- xAI를 통한 일급 X 검색
- [Gemini 검색](/tools/gemini-search) -- Google grounding을 통한 AI 합성 답변
