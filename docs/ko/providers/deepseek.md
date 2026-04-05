---
read_when:
    - OpenClaw와 함께 DeepSeek를 사용하려는 경우
    - API 키 환경 변수 또는 CLI 인증 선택이 필요한 경우
summary: DeepSeek 설정(인증 + 모델 선택)
x-i18n:
    generated_at: "2026-04-05T12:51:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 35f339ca206399496ce094eb8350e0870029ce9605121bcf86c4e9b94f3366c6
    source_path: providers/deepseek.md
    workflow: 15
---

# DeepSeek

[DeepSeek](https://www.deepseek.com)는 OpenAI 호환 API와 함께 강력한 AI 모델을 제공합니다.

- 제공자: `deepseek`
- 인증: `DEEPSEEK_API_KEY`
- API: OpenAI 호환
- 기본 URL: `https://api.deepseek.com`

## 빠른 시작

API 키를 설정합니다(권장: Gateway용으로 저장):

```bash
openclaw onboard --auth-choice deepseek-api-key
```

이 명령은 API 키 입력을 요청하고 `deepseek/deepseek-chat`을 기본 모델로 설정합니다.

## 비대화형 예시

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice deepseek-api-key \
  --deepseek-api-key "$DEEPSEEK_API_KEY" \
  --skip-health \
  --accept-risk
```

## 환경 참고

Gateway가 데몬(launchd/systemd)으로 실행되는 경우, `DEEPSEEK_API_KEY`가
해당 프로세스에서 사용 가능하도록 해야 합니다(예: `~/.openclaw/.env` 또는
`env.shellEnv`를 통해).

## 내장 카탈로그

| Model ref                    | Name              | Input | Context | Max output | Notes                                             |
| ---------------------------- | ----------------- | ----- | ------- | ---------- | ------------------------------------------------- |
| `deepseek/deepseek-chat`     | DeepSeek Chat     | text  | 131,072 | 8,192      | 기본 모델; DeepSeek V3.2 비사고 표면 |
| `deepseek/deepseek-reasoner` | DeepSeek Reasoner | text  | 131,072 | 65,536     | 추론 지원 V3.2 표면                    |

번들된 두 모델은 현재 소스에서 스트리밍 사용 호환성을 지원하는 것으로 표시됩니다.

API 키는 [platform.deepseek.com](https://platform.deepseek.com/api_keys)에서 발급받을 수 있습니다.
