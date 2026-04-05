---
read_when:
    - OpenClaw와 함께 Cloudflare AI Gateway를 사용하려는 경우
    - account ID, gateway ID 또는 API key 환경 변수가 필요한 경우
summary: Cloudflare AI Gateway 설정(인증 + 모델 선택)
title: Cloudflare AI Gateway
x-i18n:
    generated_at: "2026-04-05T12:51:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: db77652c37652ca20f7c50f32382dbaeaeb50ea5bdeaf1d4fd17dc394e58950c
    source_path: providers/cloudflare-ai-gateway.md
    workflow: 15
---

# Cloudflare AI Gateway

Cloudflare AI Gateway는 provider API 앞단에 위치하며 분석, 캐싱, 제어 기능을 추가할 수 있게 해줍니다. Anthropic의 경우 OpenClaw는 Gateway 엔드포인트를 통해 Anthropic Messages API를 사용합니다.

- Provider: `cloudflare-ai-gateway`
- Base URL: `https://gateway.ai.cloudflare.com/v1/<account_id>/<gateway_id>/anthropic`
- 기본 모델: `cloudflare-ai-gateway/claude-sonnet-4-5`
- API key: `CLOUDFLARE_AI_GATEWAY_API_KEY` (Gateway를 통한 요청에 사용하는 provider API key)

Anthropic 모델의 경우 Anthropic API key를 사용하세요.

## 빠른 시작

1. provider API key와 Gateway 세부 정보를 설정합니다.

```bash
openclaw onboard --auth-choice cloudflare-ai-gateway-api-key
```

2. 기본 모델을 설정합니다.

```json5
{
  agents: {
    defaults: {
      model: { primary: "cloudflare-ai-gateway/claude-sonnet-4-5" },
    },
  },
}
```

## 비대화형 예시

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice cloudflare-ai-gateway-api-key \
  --cloudflare-ai-gateway-account-id "your-account-id" \
  --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
  --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY"
```

## 인증된 게이트웨이

Cloudflare에서 Gateway 인증을 활성화했다면 `cf-aig-authorization` 헤더를 추가하세요(이는 provider API key 외에 추가로 필요함).

```json5
{
  models: {
    providers: {
      "cloudflare-ai-gateway": {
        headers: {
          "cf-aig-authorization": "Bearer <cloudflare-ai-gateway-token>",
        },
      },
    },
  },
}
```

## 환경 참고

Gateway가 daemon(launchd/systemd)으로 실행되는 경우 `CLOUDFLARE_AI_GATEWAY_API_KEY`가 해당 프로세스에서 사용 가능하도록 해야 합니다(예: `~/.openclaw/.env` 또는 `env.shellEnv`를 통해).
