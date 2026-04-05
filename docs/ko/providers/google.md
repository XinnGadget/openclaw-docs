---
read_when:
    - OpenClaw와 함께 Google Gemini 모델을 사용하려는 경우
    - API 키 또는 OAuth 인증 흐름이 필요한 경우
summary: Google Gemini 설정(API 키 + OAuth, 이미지 생성, 미디어 이해, 웹 검색)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-05T12:52:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: fa3c4326e83fad277ae4c2cb9501b6e89457afcfa7e3e1d57ae01c9c0c6846e2
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Google 플러그인은 Google AI Studio를 통해 Gemini 모델에 대한 액세스를 제공하며, 추가로
이미지 생성, 미디어 이해(이미지/오디오/비디오), 그리고
Gemini Grounding을 통한 웹 검색도 제공합니다.

- Provider: `google`
- 인증: `GEMINI_API_KEY` 또는 `GOOGLE_API_KEY`
- API: Google Gemini API
- 대체 provider: `google-gemini-cli` (OAuth)

## 빠른 시작

1. API 키를 설정합니다.

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. 기본 모델을 설정합니다.

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## 비대화형 예시

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## OAuth (Gemini CLI)

대체 provider인 `google-gemini-cli`는 API
키 대신 PKCE OAuth를 사용합니다. 이는 비공식 통합이며, 일부 사용자는 계정
제한을 보고했습니다. 사용에 따른 위험은 본인이 감수해야 합니다.

- 기본 모델: `google-gemini-cli/gemini-3.1-pro-preview`
- 별칭: `gemini-cli`
- 설치 전제 조건: 로컬 Gemini CLI를 `gemini`로 사용할 수 있어야 함
  - Homebrew: `brew install gemini-cli`
  - npm: `npm install -g @google/gemini-cli`
- 로그인:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

환경 변수:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

(`GEMINI_CLI_*` 변형도 사용할 수 있습니다.)

로그인 후 Gemini CLI OAuth 요청이 실패하면
게이트웨이 호스트에서 `GOOGLE_CLOUD_PROJECT` 또는 `GOOGLE_CLOUD_PROJECT_ID`를 설정한 뒤
다시 시도하세요.

브라우저 흐름이 시작되기 전에 로그인이 실패하면, 로컬 `gemini`
명령이 설치되어 있고 `PATH`에 포함되어 있는지 확인하세요. OpenClaw는 Homebrew 설치와
전역 npm 설치를 모두 지원하며, 일반적인 Windows/npm 레이아웃도 지원합니다.

Gemini CLI JSON 사용 참고 사항:

- 응답 텍스트는 CLI JSON `response` 필드에서 가져옵니다.
- CLI가 `usage`를 비워 둘 경우 사용량은 `stats`로 대체됩니다.
- `stats.cached`는 OpenClaw `cacheRead`로 정규화됩니다.
- `stats.input`이 없으면 OpenClaw는
  `stats.input_tokens - stats.cached`에서 입력 토큰 수를 계산합니다.

## 기능

| 기능                   | 지원 여부         |
| ---------------------- | ----------------- |
| 채팅 completions       | 예                |
| 이미지 생성            | 예                |
| 이미지 이해            | 예                |
| 오디오 전사            | 예                |
| 비디오 이해            | 예                |
| 웹 검색 (Grounding)    | 예                |
| 사고/추론              | 예 (Gemini 3.1+)  |

## 직접 Gemini 캐시 재사용

직접 Gemini API 실행(`api: "google-generative-ai"`)의 경우, OpenClaw는 이제
구성된 `cachedContent` 핸들을 Gemini 요청으로 그대로 전달합니다.

- 모델별 또는 전역 params는
  `cachedContent` 또는 레거시 `cached_content` 중 하나로 구성할 수 있습니다
- 둘 다 있으면 `cachedContent`가 우선합니다
- 예시 값: `cachedContents/prebuilt-context`
- Gemini 캐시 적중 사용량은
  업스트림 `cachedContentTokenCount`를 기준으로 OpenClaw `cacheRead`로 정규화됩니다

예시:

```json5
{
  agents: {
    defaults: {
      models: {
        "google/gemini-2.5-pro": {
          params: {
            cachedContent: "cachedContents/prebuilt-context",
          },
        },
      },
    },
  },
}
```

## 이미지 생성

번들된 `google` 이미지 생성 provider의 기본값은
`google/gemini-3.1-flash-image-preview`입니다.

- `google/gemini-3-pro-image-preview`도 지원합니다
- 생성: 요청당 최대 4개 이미지
- 편집 모드: 활성화됨, 입력 이미지 최대 5개
- 기하 제어: `size`, `aspectRatio`, `resolution`

OAuth 전용 `google-gemini-cli` provider는 별도의 텍스트 추론
표면입니다. 이미지 생성, 미디어 이해, Gemini Grounding은 계속
`google` provider id에 유지됩니다.

## 환경 참고 사항

Gateway가 데몬(launchd/systemd)으로 실행되는 경우, `GEMINI_API_KEY`가
해당 프로세스에서 사용 가능하도록 해야 합니다(예: `~/.openclaw/.env` 또는
`env.shellEnv`를 통해).
