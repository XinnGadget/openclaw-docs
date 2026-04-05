---
read_when:
    - OpenClaw에서 Mistral 모델을 사용하려는 경우
    - Mistral API 키 온보딩 및 모델 ref가 필요한 경우
summary: OpenClaw와 함께 Mistral 모델 및 Voxtral 전사를 사용합니다
title: Mistral
x-i18n:
    generated_at: "2026-04-05T12:52:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8f61b9e0656dd7e0243861ddf14b1b41a07c38bff27cef9ad0815d14c8e34408
    source_path: providers/mistral.md
    workflow: 15
---

# Mistral

OpenClaw는 텍스트/이미지 모델 라우팅(`mistral/...`)과
미디어 이해에서의 Voxtral 오디오 전사를 위해 Mistral을 지원합니다.
Mistral은 메모리 임베딩에도 사용할 수 있습니다(`memorySearch.provider = "mistral"`).

## CLI 설정

```bash
openclaw onboard --auth-choice mistral-api-key
# or non-interactive
openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
```

## 설정 스니펫 (LLM provider)

```json5
{
  env: { MISTRAL_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
}
```

## 내장 LLM 카탈로그

현재 OpenClaw에는 다음과 같은 번들된 Mistral 카탈로그가 포함되어 있습니다.

| Model ref                        | 입력        | 컨텍스트 | 최대 출력 | 참고 사항                |
| -------------------------------- | ----------- | -------- | --------- | ------------------------ |
| `mistral/mistral-large-latest`   | text, image | 262,144  | 16,384    | 기본 모델                |
| `mistral/mistral-medium-2508`    | text, image | 262,144  | 8,192     | Mistral Medium 3.1       |
| `mistral/mistral-small-latest`   | text, image | 128,000  | 16,384    | 더 작은 멀티모달 모델    |
| `mistral/pixtral-large-latest`   | text, image | 128,000  | 32,768    | Pixtral                  |
| `mistral/codestral-latest`       | text        | 256,000  | 4,096     | 코딩                     |
| `mistral/devstral-medium-latest` | text        | 262,144  | 32,768    | Devstral 2               |
| `mistral/magistral-small`        | text        | 128,000  | 40,000    | 추론 지원                |

## 설정 스니펫 (Voxtral 오디오 전사)

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

## 참고 사항

- Mistral 인증은 `MISTRAL_API_KEY`를 사용합니다.
- provider 기본 URL은 `https://api.mistral.ai/v1`입니다.
- 온보딩 기본 모델은 `mistral/mistral-large-latest`입니다.
- Mistral용 미디어 이해 기본 오디오 모델은 `voxtral-mini-latest`입니다.
- 미디어 전사 경로는 `/v1/audio/transcriptions`를 사용합니다.
- 메모리 임베딩 경로는 `/v1/embeddings`를 사용합니다(기본 모델: `mistral-embed`).
