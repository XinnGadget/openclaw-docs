---
read_when:
    - OpenClaw에서 Chutes를 사용하려고 함
    - OAuth 또는 API 키 설정 경로가 필요함
    - 기본 모델, aliases, 또는 검색 동작을 알고 싶음
summary: Chutes 설정(OAuth 또는 API 키, 모델 검색, aliases)
title: Chutes
x-i18n:
    generated_at: "2026-04-05T12:51:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: e275f32e7a19fa5b4c64ffabfb4bf116dd5c9ab95bfa25bd3b1a15d15e237674
    source_path: providers/chutes.md
    workflow: 15
---

# Chutes

[Chutes](https://chutes.ai)는
OpenAI 호환 API를 통해 오픈 소스 모델 카탈로그를 제공합니다. OpenClaw는 번들 `chutes` provider에 대해 브라우저 OAuth와 직접 API-key
인증을 모두 지원합니다.

- Provider: `chutes`
- API: OpenAI 호환
- Base URL: `https://llm.chutes.ai/v1`
- 인증:
  - OAuth: `openclaw onboard --auth-choice chutes`
  - API 키: `openclaw onboard --auth-choice chutes-api-key`
  - 런타임 env vars: `CHUTES_API_KEY`, `CHUTES_OAUTH_TOKEN`

## 빠른 시작

### OAuth

```bash
openclaw onboard --auth-choice chutes
```

OpenClaw는 로컬에서는 브라우저 흐름을 시작하고, 원격/headless 호스트에서는 URL + redirect-paste
흐름을 표시합니다. OAuth 토큰은 OpenClaw auth
profiles를 통해 자동으로 새로 고쳐집니다.

선택적 OAuth 재정의:

- `CHUTES_CLIENT_ID`
- `CHUTES_CLIENT_SECRET`
- `CHUTES_OAUTH_REDIRECT_URI`
- `CHUTES_OAUTH_SCOPES`

### API 키

```bash
openclaw onboard --auth-choice chutes-api-key
```

키는
[chutes.ai/settings/api-keys](https://chutes.ai/settings/api-keys)에서 얻을 수 있습니다.

두 인증 경로 모두 번들 Chutes 카탈로그를 등록하고 기본 모델을
`chutes/zai-org/GLM-4.7-TEE`로 설정합니다.

## 검색 동작

Chutes 인증을 사용할 수 있으면 OpenClaw는 해당
자격 증명으로 Chutes 카탈로그를 조회하고 검색된 모델을 사용합니다. 검색에 실패하면
온보딩과 시작이 계속 동작하도록 번들된 정적 카탈로그로 폴백합니다.

## 기본 aliases

OpenClaw는 번들 Chutes
카탈로그에 대해 다음 세 가지 편의 aliases도 등록합니다:

- `chutes-fast` -> `chutes/zai-org/GLM-4.7-FP8`
- `chutes-pro` -> `chutes/deepseek-ai/DeepSeek-V3.2-TEE`
- `chutes-vision` -> `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506`

## 내장 starter catalog

번들 fallback catalog에는 다음과 같은 현재 Chutes refs가 포함됩니다:

- `chutes/zai-org/GLM-4.7-TEE`
- `chutes/zai-org/GLM-5-TEE`
- `chutes/deepseek-ai/DeepSeek-V3.2-TEE`
- `chutes/deepseek-ai/DeepSeek-R1-0528-TEE`
- `chutes/moonshotai/Kimi-K2.5-TEE`
- `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506`
- `chutes/Qwen/Qwen3-Coder-Next-TEE`
- `chutes/openai/gpt-oss-120b-TEE`

## Config 예시

```json5
{
  agents: {
    defaults: {
      model: { primary: "chutes/zai-org/GLM-4.7-TEE" },
      models: {
        "chutes/zai-org/GLM-4.7-TEE": { alias: "Chutes GLM 4.7" },
        "chutes/deepseek-ai/DeepSeek-V3.2-TEE": { alias: "Chutes DeepSeek V3.2" },
      },
    },
  },
}
```

## 참고

- OAuth 도움말 및 redirect-app 요구 사항: [Chutes OAuth docs](https://chutes.ai/docs/sign-in-with-chutes/overview)
- API-key와 OAuth 검색은 모두 동일한 `chutes` provider id를 사용합니다.
- Chutes 모델은 `chutes/<model-id>` 형식으로 등록됩니다.
