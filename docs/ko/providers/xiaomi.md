---
read_when:
    - OpenClaw에서 Xiaomi MiMo 모델을 사용하려는 경우
    - '`XIAOMI_API_KEY` 설정이 필요한 경우'
summary: OpenClaw에서 Xiaomi MiMo 모델 사용하기
title: Xiaomi MiMo
x-i18n:
    generated_at: "2026-04-05T12:53:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: a2533fa99b29070e26e0e1fbde924e1291c89b1fbc2537451bcc0eb677ea6949
    source_path: providers/xiaomi.md
    workflow: 15
---

# Xiaomi MiMo

Xiaomi MiMo는 **MiMo** 모델용 API 플랫폼입니다. OpenClaw는 API 키 인증이 있는
Xiaomi의 OpenAI 호환 엔드포인트를 사용합니다.
[Xiaomi MiMo 콘솔](https://platform.xiaomimimo.com/#/console/api-keys)에서 API 키를 생성한 다음,
해당 키로 번들된 `xiaomi` 프로바이더를 구성하세요.

## 기본 제공 카탈로그

- 기본 URL: `https://api.xiaomimimo.com/v1`
- API: `openai-completions`
- 인증: `Bearer $XIAOMI_API_KEY`

| 모델 ref              | 입력        | 컨텍스트  | 최대 출력 | 참고                         |
| --------------------- | ----------- | --------- | --------- | ---------------------------- |
| `xiaomi/mimo-v2-flash` | text        | 262,144   | 8,192     | 기본 모델                    |
| `xiaomi/mimo-v2-pro`   | text        | 1,048,576 | 32,000    | 추론 기능 활성화             |
| `xiaomi/mimo-v2-omni`  | text, image | 262,144   | 32,000    | 추론 기능 활성화 멀티모달    |

## CLI 설정

```bash
openclaw onboard --auth-choice xiaomi-api-key
# 또는 비대화형
openclaw onboard --auth-choice xiaomi-api-key --xiaomi-api-key "$XIAOMI_API_KEY"
```

## Config 스니펫

```json5
{
  env: { XIAOMI_API_KEY: "your-key" },
  agents: { defaults: { model: { primary: "xiaomi/mimo-v2-flash" } } },
  models: {
    mode: "merge",
    providers: {
      xiaomi: {
        baseUrl: "https://api.xiaomimimo.com/v1",
        api: "openai-completions",
        apiKey: "XIAOMI_API_KEY",
        models: [
          {
            id: "mimo-v2-flash",
            name: "Xiaomi MiMo V2 Flash",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 8192,
          },
          {
            id: "mimo-v2-pro",
            name: "Xiaomi MiMo V2 Pro",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 1048576,
            maxTokens: 32000,
          },
          {
            id: "mimo-v2-omni",
            name: "Xiaomi MiMo V2 Omni",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

## 참고

- 기본 모델 ref: `xiaomi/mimo-v2-flash`.
- 추가 기본 제공 모델: `xiaomi/mimo-v2-pro`, `xiaomi/mimo-v2-omni`.
- `XIAOMI_API_KEY`가 설정되어 있거나(또는 인증 프로필이 존재하면) 프로바이더가 자동으로 주입됩니다.
- 프로바이더 규칙은 [/concepts/model-providers](/ko/concepts/model-providers)를 참고하세요.
