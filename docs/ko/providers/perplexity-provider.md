---
read_when:
    - 웹 검색 공급자로 Perplexity를 구성하려는 경우
    - Perplexity API 키 또는 OpenRouter 프록시 설정이 필요한 경우
summary: Perplexity 웹 검색 공급자 설정(API 키, 검색 모드, 필터링)
title: Perplexity (공급자)
x-i18n:
    generated_at: "2026-04-05T12:52:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: df9082d15d6a36a096e21efe8cee78e4b8643252225520f5b96a0b99cf5a7a4b
    source_path: providers/perplexity-provider.md
    workflow: 15
---

# Perplexity (웹 검색 공급자)

Perplexity plugin은 Perplexity Search API 또는 OpenRouter를 통한 Perplexity Sonar를 통해 웹 검색 기능을 제공합니다.

<Note>
이 페이지는 Perplexity **공급자** 설정을 다룹니다. Perplexity **도구**(에이전트가 이를 사용하는 방법)에 대해서는 [Perplexity 도구](/tools/perplexity-search)를 참조하세요.
</Note>

- 유형: 웹 검색 공급자(모델 공급자가 아님)
- 인증: `PERPLEXITY_API_KEY`(직접) 또는 `OPENROUTER_API_KEY`(OpenRouter 경유)
- 구성 경로: `plugins.entries.perplexity.config.webSearch.apiKey`

## 빠른 시작

1. API 키를 설정합니다:

```bash
openclaw configure --section web
```

또는 직접 설정합니다:

```bash
openclaw config set plugins.entries.perplexity.config.webSearch.apiKey "pplx-xxxxxxxxxxxx"
```

2. 구성되면 에이전트가 웹 검색에 Perplexity를 자동으로 사용합니다.

## 검색 모드

plugin은 API 키 접두사를 기준으로 전송 방식을 자동 선택합니다:

| 키 접두사 | 전송 방식 | 기능 |
| ---------- | ---------------------------- | ------------------------------------------------ |
| `pplx-`    | 기본 Perplexity Search API | 구조화된 결과, 도메인/언어/날짜 필터 |
| `sk-or-`   | OpenRouter (Sonar) | 인용이 포함된 AI 합성 답변 |

## 기본 API 필터링

기본 Perplexity API(`pplx-` 키)를 사용하는 경우 검색은 다음을 지원합니다:

- **국가**: 2자리 국가 코드
- **언어**: ISO 639-1 언어 코드
- **날짜 범위**: 일, 주, 월, 년
- **도메인 필터**: 허용 목록/차단 목록(최대 20개 도메인)
- **콘텐츠 예산**: `max_tokens`, `max_tokens_per_page`

## 환경 참고 사항

Gateway가 데몬(launchd/systemd)으로 실행되는 경우
`PERPLEXITY_API_KEY`가 해당 프로세스에서 사용할 수 있도록 해야 합니다(예: `~/.openclaw/.env` 또는 `env.shellEnv`를 통해).
