---
x-i18n:
    generated_at: "2026-04-05T12:53:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 895b701d3a3950ea7482e5e870663ed93e0355e679199ed4622718d588ef18fa
    source_path: providers/qwen.md
    workflow: 15
---

summary: "OpenClaw의 번들된 qwen provider를 통해 Qwen Cloud를 사용합니다"
read_when:

- OpenClaw에서 Qwen을 사용하려는 경우
- 이전에 Qwen OAuth를 사용한 경우
  title: "Qwen"

---

# Qwen

<Warning>

**Qwen OAuth는 제거되었습니다.** `portal.qwen.ai` 엔드포인트를 사용하던
무료 등급 OAuth 통합(`qwen-portal`)은 더 이상 사용할 수 없습니다.
배경 정보는 [Issue #49557](https://github.com/openclaw/openclaw/issues/49557)를
참조하세요.

</Warning>

## 권장: Qwen Cloud

OpenClaw는 이제 Qwen을 정식 번들 provider로 취급하며, 표준 id는
`qwen`입니다. 번들 provider는 Qwen Cloud / Alibaba DashScope 및
Coding Plan 엔드포인트를 대상으로 하며, 기존 `modelstudio` id도
호환성 별칭으로 계속 작동합니다.

- Provider: `qwen`
- 권장 env var: `QWEN_API_KEY`
- 호환성을 위해 함께 허용됨: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- API 스타일: OpenAI 호환

`qwen3.6-plus`를 사용하려면 **Standard (사용량 기반 과금)** 엔드포인트를
권장합니다. Coding Plan 지원은 공개 카탈로그보다 뒤처질 수 있습니다.

```bash
# Global Coding Plan endpoint
openclaw onboard --auth-choice qwen-api-key

# China Coding Plan endpoint
openclaw onboard --auth-choice qwen-api-key-cn

# Global Standard (pay-as-you-go) endpoint
openclaw onboard --auth-choice qwen-standard-api-key

# China Standard (pay-as-you-go) endpoint
openclaw onboard --auth-choice qwen-standard-api-key-cn
```

기존 `modelstudio-*` auth-choice id와 `modelstudio/...` 모델 참조도
호환성 별칭으로 계속 작동하지만, 새로운 설정 흐름에서는 표준
`qwen-*` auth-choice id와 `qwen/...` 모델 참조를 사용하는 것이 좋습니다.

onboarding 후 기본 모델을 설정하세요:

```json5
{
  agents: {
    defaults: {
      model: { primary: "qwen/qwen3.5-plus" },
    },
  },
}
```

## 기능 계획

`qwen` extension은 단순한 코딩/텍스트 모델만이 아니라 전체 Qwen
Cloud 표면을 위한 벤더 홈으로 자리잡고 있습니다.

- 텍스트/채팅 모델: 현재 번들 포함
- tool calling, structured output, thinking: OpenAI 호환 전송 계층에서 상속
- 이미지 생성: provider-plugin 계층에서 지원 예정
- 이미지/비디오 이해: 현재 Standard 엔드포인트에서 번들 포함
- 음성/오디오: provider-plugin 계층에서 지원 예정
- 메모리 임베딩/리랭킹: 임베딩 어댑터 표면을 통해 지원 예정
- 비디오 생성: 공유 비디오 생성 기능을 통해 현재 번들 포함

## 멀티모달 추가 기능

`qwen` extension은 이제 다음도 제공합니다:

- `qwen-vl-max-latest`를 통한 비디오 이해
- 다음을 통한 Wan 비디오 생성:
  - `wan2.6-t2v` (기본값)
  - `wan2.6-i2v`
  - `wan2.6-r2v`
  - `wan2.6-r2v-flash`
  - `wan2.7-r2v`

이 멀티모달 표면은 Coding Plan 엔드포인트가 아니라 **Standard**
DashScope 엔드포인트를 사용합니다.

- Global/Intl Standard 기본 URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- China Standard 기본 URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`

비디오 생성의 경우, OpenClaw는 작업 제출 전에 구성된 Qwen 리전을 해당하는
DashScope AIGC 호스트에 매핑합니다:

- Global/Intl: `https://dashscope-intl.aliyuncs.com`
- China: `https://dashscope.aliyuncs.com`

즉, Coding Plan 또는 Standard Qwen 호스트를 가리키는 일반적인
`models.providers.qwen.baseUrl`을 사용해도 비디오 생성은 올바른 지역의
DashScope 비디오 엔드포인트를 계속 사용합니다.

비디오 생성의 경우, 기본 모델을 명시적으로 설정하세요:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

현재 번들된 Qwen 비디오 생성 제한:

- 요청당 최대 **1개** 출력 비디오
- 최대 **1개** 입력 이미지
- 최대 **4개** 입력 비디오
- 최대 **10초** 길이
- `size`, `aspectRatio`, `resolution`, `audio`, `watermark` 지원

엔드포인트 수준의 세부 정보 및 호환성 참고 사항은
[Qwen / Model Studio](/providers/qwen_modelstudio)를 참조하세요.
