---
read_when:
    - OpenClaw에서 Groq를 사용하려는 경우
    - API 키 환경 변수 또는 CLI 인증 선택 방법이 필요한 경우
summary: Groq 설정(인증 + 모델 선택)
title: Groq
x-i18n:
    generated_at: "2026-04-05T12:51:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7e27532cafcdaf1ac336fa310e08e4e3245d2d0eb0e94e0bcf42c532c6a9a80b
    source_path: providers/groq.md
    workflow: 15
---

# Groq

[Groq](https://groq.com)은 맞춤형 LPU 하드웨어를 사용해 오픈 소스 모델(Llama, Gemma, Mistral 등)에서 초고속 추론을 제공합니다. OpenClaw는 OpenAI 호환 API를 통해 Groq에 연결합니다.

- 공급자: `groq`
- 인증: `GROQ_API_KEY`
- API: OpenAI 호환

## 빠른 시작

1. [console.groq.com/keys](https://console.groq.com/keys)에서 API 키를 받습니다.

2. API 키를 설정합니다:

```bash
export GROQ_API_KEY="gsk_..."
```

3. 기본 모델을 설정합니다:

```json5
{
  agents: {
    defaults: {
      model: { primary: "groq/llama-3.3-70b-versatile" },
    },
  },
}
```

## 구성 파일 예시

```json5
{
  env: { GROQ_API_KEY: "gsk_..." },
  agents: {
    defaults: {
      model: { primary: "groq/llama-3.3-70b-versatile" },
    },
  },
}
```

## 오디오 전사

Groq는 빠른 Whisper 기반 오디오 전사도 제공합니다. 미디어 이해 공급자로 구성하면 OpenClaw는 공유 `tools.media.audio` 표면을 통해 Groq의 `whisper-large-v3-turbo` 모델을 사용하여 음성 메시지를 전사합니다.

```json5
{
  tools: {
    media: {
      audio: {
        models: [{ provider: "groq" }],
      },
    },
  },
}
```

## 환경 참고 사항

Gateway가 데몬(launchd/systemd)으로 실행되는 경우 `GROQ_API_KEY`가 해당 프로세스에서 사용할 수 있도록 해야 합니다(예: `~/.openclaw/.env` 또는 `env.shellEnv`를 통해).

## 오디오 참고 사항

- 공유 구성 경로: `tools.media.audio`
- 기본 Groq 오디오 base URL: `https://api.groq.com/openai/v1`
- 기본 Groq 오디오 모델: `whisper-large-v3-turbo`
- Groq 오디오 전사는 OpenAI 호환 `/audio/transcriptions` 경로를 사용합니다

## 사용 가능한 모델

Groq의 모델 카탈로그는 자주 변경됩니다. 현재 사용 가능한 모델을 보려면 `openclaw models list | grep groq`를 실행하거나 [console.groq.com/docs/models](https://console.groq.com/docs/models)을 확인하세요.

인기 있는 선택지는 다음과 같습니다:

- **Llama 3.3 70B Versatile** - 범용, 대규모 컨텍스트
- **Llama 3.1 8B Instant** - 빠르고 가벼움
- **Gemma 2 9B** - 작고 효율적
- **Mixtral 8x7B** - MoE 아키텍처, 뛰어난 추론 성능

## 링크

- [Groq Console](https://console.groq.com)
- [API 문서](https://console.groq.com/docs)
- [모델 목록](https://console.groq.com/docs/models)
- [요금](https://groq.com/pricing)
