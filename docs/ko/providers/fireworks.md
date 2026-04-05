---
read_when:
    - OpenClaw와 함께 Fireworks를 사용하려는 경우
    - Fireworks API 키 환경 변수 또는 기본 모델 ID가 필요한 경우
summary: Fireworks 설정(인증 + 모델 선택)
x-i18n:
    generated_at: "2026-04-05T12:51:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 20083d5c248abd9a7223e6d188f0265ae27381940ee0067dff6d1d46d908c552
    source_path: providers/fireworks.md
    workflow: 15
---

# Fireworks

[Fireworks](https://fireworks.ai)는 OpenAI 호환 API를 통해 오픈 웨이트 모델과 라우팅된 모델을 제공합니다. OpenClaw에는 이제 번들된 Fireworks 제공자 플러그인이 포함됩니다.

- 제공자: `fireworks`
- 인증: `FIREWORKS_API_KEY`
- API: OpenAI 호환 chat/completions
- 기본 URL: `https://api.fireworks.ai/inference/v1`
- 기본 모델: `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo`

## 빠른 시작

온보딩을 통해 Fireworks 인증을 설정합니다:

```bash
openclaw onboard --auth-choice fireworks-api-key
```

이렇게 하면 Fireworks 키가 OpenClaw 설정에 저장되고 Fire Pass 시작 모델이 기본값으로 설정됩니다.

## 비대화형 예시

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice fireworks-api-key \
  --fireworks-api-key "$FIREWORKS_API_KEY" \
  --skip-health \
  --accept-risk
```

## 환경 참고

Gateway가 대화형 셸 외부에서 실행되는 경우, `FIREWORKS_API_KEY`도 해당 프로세스에서 사용할 수 있어야 합니다. 키가 `~/.profile`에만 있으면 그 환경이 거기에도 함께 가져와지지 않는 한 launchd/systemd 데몬에는 도움이 되지 않습니다.

## 내장 카탈로그

| 모델 참조                                              | 이름                        | 입력       | 컨텍스트 | 최대 출력 | 참고                                      |
| ------------------------------------------------------ | --------------------------- | ---------- | ------- | ---------- | ------------------------------------------ |
| `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` | Kimi K2.5 Turbo (Fire Pass) | text,image | 256,000 | 256,000    | Fireworks의 기본 번들 시작 모델 |

## 사용자 지정 Fireworks 모델 ID

OpenClaw는 동적 Fireworks 모델 ID도 허용합니다. Fireworks에 표시된 정확한 모델 또는 라우터 ID를 사용하고 앞에 `fireworks/`를 붙이세요.

예시:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "fireworks/accounts/fireworks/routers/kimi-k2p5-turbo",
      },
    },
  },
}
```

Fireworks가 최신 Qwen 또는 Gemma 릴리스 같은 더 새로운 모델을 게시하면, 번들 카탈로그 업데이트를 기다리지 않고 해당 Fireworks 모델 ID를 사용해 바로 전환할 수 있습니다.
