---
read_when:
    - '`web_search`에 Kimi를 사용하려는 경우'
    - '`KIMI_API_KEY` 또는 `MOONSHOT_API_KEY`가 필요한 경우'
summary: Moonshot 웹 검색을 통한 Kimi 웹 검색
title: Kimi 검색
x-i18n:
    generated_at: "2026-04-05T12:57:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 753757a5497a683c35b4509ed3709b9514dc14a45612675d0f729ae6668c82a5
    source_path: tools/kimi-search.md
    workflow: 15
---

# Kimi 검색

OpenClaw는 Kimi를 `web_search` 제공자로 지원하며, Moonshot 웹 검색을 사용해
인용이 포함된 AI 합성 답변을 생성합니다.

## API 키 받기

<Steps>
  <Step title="키 만들기">
    [Moonshot AI](https://platform.moonshot.cn/)에서 API 키를 발급받으세요.
  </Step>
  <Step title="키 저장하기">
    Gateway 환경에 `KIMI_API_KEY` 또는 `MOONSHOT_API_KEY`를 설정하거나
    다음으로 구성하세요:

    ```bash
    openclaw configure --section web
    ```

  </Step>
</Steps>

`openclaw onboard` 또는
`openclaw configure --section web` 중에 **Kimi**를 선택하면 OpenClaw는 다음도 요청할 수 있습니다:

- Moonshot API 리전:
  - `https://api.moonshot.ai/v1`
  - `https://api.moonshot.cn/v1`
- 기본 Kimi 웹 검색 모델(기본값은 `kimi-k2.5`)

## 설정

```json5
{
  plugins: {
    entries: {
      moonshot: {
        config: {
          webSearch: {
            apiKey: "sk-...", // KIMI_API_KEY 또는 MOONSHOT_API_KEY가 설정된 경우 선택 사항
            baseUrl: "https://api.moonshot.ai/v1",
            model: "kimi-k2.5",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "kimi",
      },
    },
  },
}
```

채팅에 China API 호스트(`models.providers.moonshot.baseUrl`:
`https://api.moonshot.cn/v1`)를 사용하는 경우 OpenClaw는
`tools.web.search.kimi.baseUrl`이 생략되면 Kimi
`web_search`에도 같은 호스트를 재사용합니다. 따라서
[platform.moonshot.cn](https://platform.moonshot.cn/)의 키가 실수로
국제 엔드포인트로 가지 않게 됩니다(이 경우 자주 HTTP 401이 반환됩니다). 다른 검색 기본 URL이 필요하면
`tools.web.search.kimi.baseUrl`로 재정의하세요.

**환경 변수 대안:** Gateway 환경에 `KIMI_API_KEY` 또는 `MOONSHOT_API_KEY`를 설정하세요.
gateway 설치의 경우 `~/.openclaw/.env`에 넣으세요.

`baseUrl`을 생략하면 OpenClaw는 기본적으로 `https://api.moonshot.ai/v1`를 사용합니다.
`model`을 생략하면 OpenClaw는 기본적으로 `kimi-k2.5`를 사용합니다.

## 작동 방식

Kimi는 Moonshot 웹 검색을 사용해
Gemini와 Grok의 grounding 응답 방식과 유사하게 인라인 인용이 포함된 답변을 합성합니다.

## 지원되는 매개변수

Kimi 검색은 `query`를 지원합니다.

`count`도 공유 `web_search` 호환성을 위해 허용되지만, Kimi는 여전히
N개 결과 목록이 아니라 인용이 포함된 하나의 합성 답변을 반환합니다.

제공자별 필터는 현재 지원되지 않습니다.

## 관련 문서

- [웹 검색 개요](/tools/web) -- 모든 제공자와 자동 감지
- [Moonshot AI](/providers/moonshot) -- Moonshot 모델 + Kimi Coding 제공자 문서
- [Gemini 검색](/tools/gemini-search) -- Google grounding을 통한 AI 합성 답변
- [Grok 검색](/tools/grok-search) -- xAI grounding을 통한 AI 합성 답변
