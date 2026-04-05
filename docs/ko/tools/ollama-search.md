---
read_when:
    - '`web_search`에 Ollama를 사용하려는 경우'
    - API 키가 필요 없는 `web_search` 프로바이더를 원하는 경우
    - Ollama Web Search 설정 가이드가 필요한 경우
summary: 구성된 Ollama 호스트를 통한 Ollama Web Search
title: Ollama Web Search
x-i18n:
    generated_at: "2026-04-05T12:57:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3c1d0765594e0eb368c25cca21a712c054e71cf43e7bfb385d10feddd990f4fd
    source_path: tools/ollama-search.md
    workflow: 15
---

# Ollama Web Search

OpenClaw는 **Ollama Web Search**를 번들 `web_search` 프로바이더로 지원합니다.
이 프로바이더는 Ollama의 실험적 웹 검색 API를 사용하며 제목, URL, 스니펫이 포함된 구조화된 결과를 반환합니다.

Ollama 모델 프로바이더와 달리, 이 설정에는 기본적으로 API 키가 필요하지 않습니다.
하지만 다음은 필요합니다:

- OpenClaw에서 접근 가능한 Ollama 호스트
- `ollama signin`

## 설정

<Steps>
  <Step title="Ollama 시작">
    Ollama가 설치되어 실행 중인지 확인하세요.
  </Step>
  <Step title="로그인">
    다음을 실행하세요:

    ```bash
    ollama signin
    ```

  </Step>
  <Step title="Ollama Web Search 선택">
    다음을 실행하세요:

    ```bash
    openclaw configure --section web
    ```

    그런 다음 프로바이더로 **Ollama Web Search**를 선택하세요.

  </Step>
</Steps>

이미 모델에 Ollama를 사용하고 있다면, Ollama Web Search는 동일한
구성된 호스트를 재사용합니다.

## Config

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

선택적 Ollama 호스트 재정의:

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434",
      },
    },
  },
}
```

명시적인 Ollama base URL이 설정되지 않은 경우 OpenClaw는 `http://127.0.0.1:11434`를 사용합니다.

Ollama 호스트가 bearer 인증을 기대하는 경우, OpenClaw는 웹 검색 요청에도
`models.providers.ollama.apiKey`(또는 일치하는 env 기반 프로바이더 인증)를 재사용합니다.

## 참고

- 이 프로바이더에는 웹 검색 전용 API 키 필드가 필요하지 않습니다.
- Ollama 호스트가 인증으로 보호되는 경우 OpenClaw는 존재할 때 일반 Ollama
  프로바이더 API 키를 재사용합니다.
- OpenClaw는 설정 중 Ollama에 접근할 수 없거나 로그인되지 않은 경우 경고하지만,
  선택 자체를 막지는 않습니다.
- 더 높은 우선순위의 자격 증명 기반 프로바이더가 구성되지 않은 경우, 런타임 자동 감지는 Ollama Web Search로 폴백할 수 있습니다.
- 이 프로바이더는 Ollama의 실험적 `/api/experimental/web_search`
  엔드포인트를 사용합니다.

## 관련

- [웹 검색 개요](/tools/web) -- 모든 프로바이더와 자동 감지
- [Ollama](/providers/ollama) -- Ollama 모델 설정 및 cloud/local 모드
