---
read_when:
    - OpenClaw와 함께 Vercel AI Gateway를 사용하려는 경우
    - API 키 env var 또는 CLI 인증 선택이 필요한 경우
summary: Vercel AI Gateway 설정(인증 + 모델 선택)
title: Vercel AI Gateway
x-i18n:
    generated_at: "2026-04-05T12:53:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: f30768dc3db49708b25042d317906f7ad9a2c72b0fa03263bc04f5eefbf7a507
    source_path: providers/vercel-ai-gateway.md
    workflow: 15
---

# Vercel AI Gateway

[Vercel AI Gateway](https://vercel.com/ai-gateway)는 단일 엔드포인트를 통해 수백 개의 모델에 접근할 수 있는 통합 API를 제공합니다.

- 프로바이더: `vercel-ai-gateway`
- 인증: `AI_GATEWAY_API_KEY`
- API: Anthropic Messages 호환
- OpenClaw는 Gateway `/v1/models` 카탈로그를 자동으로 검색하므로 `/models vercel-ai-gateway`에는
  `vercel-ai-gateway/openai/gpt-5.4`와 같은 현재 모델 ref가 포함됩니다.

## 빠른 시작

1. API 키를 설정합니다(권장: Gateway용으로 저장):

```bash
openclaw onboard --auth-choice ai-gateway-api-key
```

2. 기본 모델을 설정합니다:

```json5
{
  agents: {
    defaults: {
      model: { primary: "vercel-ai-gateway/anthropic/claude-opus-4.6" },
    },
  },
}
```

## 비대화형 예시

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice ai-gateway-api-key \
  --ai-gateway-api-key "$AI_GATEWAY_API_KEY"
```

## 환경 참고

Gateway가 데몬(launchd/systemd)으로 실행되는 경우 `AI_GATEWAY_API_KEY`가
해당 프로세스에서 사용 가능하도록 해야 합니다(예: `~/.openclaw/.env` 또는
`env.shellEnv`를 통해).

## 모델 ID 축약형

OpenClaw는 Vercel Claude 축약형 모델 ref를 허용하며 런타임에 이를 정규화합니다:

- `vercel-ai-gateway/claude-opus-4.6` -> `vercel-ai-gateway/anthropic/claude-opus-4.6`
- `vercel-ai-gateway/opus-4.6` -> `vercel-ai-gateway/anthropic/claude-opus-4-6`
