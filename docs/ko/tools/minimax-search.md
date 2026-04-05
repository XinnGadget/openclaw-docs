---
read_when:
    - '`web_search`에 MiniMax를 사용하려는 경우'
    - MiniMax Coding Plan 키가 필요한 경우
    - MiniMax CN/글로벌 검색 호스트 안내가 필요한 경우
summary: Coding Plan 검색 API를 통한 MiniMax 검색
title: MiniMax 검색
x-i18n:
    generated_at: "2026-04-05T12:57:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: b8c3767790f428fc7e239590a97e9dbee0d3bd6550ca3299ae22da0f5a57231a
    source_path: tools/minimax-search.md
    workflow: 15
---

# MiniMax 검색

OpenClaw는 MiniMax를 `web_search` 제공자로 지원하며, MiniMax
Coding Plan 검색 API를 통해 동작합니다. 제목, URL,
스니펫, 관련 쿼리가 포함된 구조화된 검색 결과를 반환합니다.

## Coding Plan 키 받기

<Steps>
  <Step title="키 만들기">
    [MiniMax Platform](https://platform.minimax.io/user-center/basic-information/interface-key)에서
    MiniMax Coding Plan 키를 생성하거나 복사하세요.
  </Step>
  <Step title="키 저장하기">
    Gateway 환경에 `MINIMAX_CODE_PLAN_KEY`를 설정하거나 다음으로 구성하세요:

    ```bash
    openclaw configure --section web
    ```

  </Step>
</Steps>

OpenClaw는 환경 변수 별칭으로 `MINIMAX_CODING_API_KEY`도 허용합니다. `MINIMAX_API_KEY`는
이미 coding-plan 토큰을 가리키는 경우 호환성 폴백으로 계속 읽습니다.

## 설정

```json5
{
  plugins: {
    entries: {
      minimax: {
        config: {
          webSearch: {
            apiKey: "sk-cp-...", // MINIMAX_CODE_PLAN_KEY가 설정된 경우 선택 사항
            region: "global", // 또는 "cn"
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "minimax",
      },
    },
  },
}
```

**환경 변수 대안:** Gateway 환경에 `MINIMAX_CODE_PLAN_KEY`를 설정하세요.
gateway 설치의 경우 `~/.openclaw/.env`에 넣으세요.

## 리전 선택

MiniMax 검색은 다음 엔드포인트를 사용합니다:

- 글로벌: `https://api.minimax.io/v1/coding_plan/search`
- CN: `https://api.minimaxi.com/v1/coding_plan/search`

`plugins.entries.minimax.config.webSearch.region`이 설정되지 않은 경우 OpenClaw는
다음 순서로 리전을 결정합니다:

1. `tools.web.search.minimax.region` / plugin 소유 `webSearch.region`
2. `MINIMAX_API_HOST`
3. `models.providers.minimax.baseUrl`
4. `models.providers.minimax-portal.baseUrl`

즉, CN 온보딩 또는 `MINIMAX_API_HOST=https://api.minimaxi.com/...`를 사용하면
MiniMax 검색도 자동으로 CN 호스트를 유지합니다.

OAuth `minimax-portal` 경로를 통해 MiniMax를 인증했더라도,
웹 검색은 여전히 제공자 ID `minimax`로 등록됩니다. OAuth 제공자 기본 URL은
CN/글로벌 호스트 선택을 위한 리전 힌트로만 사용됩니다.

## 지원되는 매개변수

MiniMax 검색은 다음을 지원합니다:

- `query`
- `count`(OpenClaw가 반환된 결과 목록을 요청한 개수에 맞게 잘라냄)

제공자별 필터는 현재 지원되지 않습니다.

## 관련 문서

- [웹 검색 개요](/tools/web) -- 모든 제공자와 자동 감지
- [MiniMax](/providers/minimax) -- 모델, 이미지, 음성, 인증 설정
