---
x-i18n:
    generated_at: "2026-04-05T12:53:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1066a1d0acebe4ae3500d18c21f7de07f43b9766daf3d13b098936734e9e7a2b
    source_path: providers/qwen_modelstudio.md
    workflow: 15
---

title: "Qwen / Model Studio"
summary: "번들 qwen 제공자와 레거시 modelstudio 호환 표면의 엔드포인트 세부 정보"
read_when:

- Qwen Cloud / Alibaba DashScope의 엔드포인트 수준 세부 정보가 필요합니다
- qwen 제공자의 env var 호환성 구성이 필요합니다
- Standard(종량제) 또는 Coding Plan 엔드포인트를 사용하려고 합니다

---

# Qwen / Model Studio (Alibaba Cloud)

이 페이지는 OpenClaw의 번들 `qwen` 제공자 뒤에 있는 엔드포인트 매핑을
문서화합니다. `qwen`이 표준 표면이 되더라도, 이 제공자는 호환성 별칭으로
`modelstudio` 제공자 ID, auth-choice ID, 모델 ref가 계속 작동하도록
유지합니다.

<Info>

**`qwen3.6-plus`**가 필요하다면 **Standard(종량제)**를 우선 사용하세요.
Coding Plan 사용 가능 여부는 공개 Model Studio 카탈로그보다 늦을 수 있으며,
Coding Plan API는 해당 모델이 플랜의 지원 모델 목록에 나타날 때까지
모델을 거부할 수 있습니다.

</Info>

- 제공자: `qwen` (레거시 별칭: `modelstudio`)
- 인증: `QWEN_API_KEY`
- 함께 허용됨: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- API: OpenAI 호환

## 빠른 시작

### Standard(종량제)

```bash
# China endpoint
openclaw onboard --auth-choice qwen-standard-api-key-cn

# Global/Intl endpoint
openclaw onboard --auth-choice qwen-standard-api-key
```

### Coding Plan(구독)

```bash
# China endpoint
openclaw onboard --auth-choice qwen-api-key-cn

# Global/Intl endpoint
openclaw onboard --auth-choice qwen-api-key
```

레거시 `modelstudio-*` auth-choice ID도 호환성 별칭으로 계속 작동하지만,
표준 온보딩 ID는 위에 표시된 `qwen-*` 선택지입니다.

온보딩 후 기본 모델을 설정하세요:

```json5
{
  agents: {
    defaults: {
      model: { primary: "qwen/qwen3.5-plus" },
    },
  },
}
```

## 플랜 유형 및 엔드포인트

| 플랜 | 지역 | Auth choice | 엔드포인트 |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard(종량제) | China | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1` |
| Standard(종량제) | Global | `qwen-standard-api-key` | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan(구독) | China | `qwen-api-key-cn` | `coding.dashscope.aliyuncs.com/v1` |
| Coding Plan(구독) | Global | `qwen-api-key` | `coding-intl.dashscope.aliyuncs.com/v1` |

이 제공자는 auth choice를 기준으로 엔드포인트를 자동 선택합니다. 표준
선택지는 `qwen-*` 계열을 사용하며, `modelstudio-*`는 호환성 전용으로
유지됩니다. config에서 커스텀 `baseUrl`로
재정의할 수 있습니다.

네이티브 Model Studio 엔드포인트는 공유 `openai-completions` 전송에서
스트리밍 usage 호환성을 광고합니다. OpenClaw는 이제 이를 엔드포인트 기능을
기준으로 판단하므로, 동일한 네이티브 호스트를 대상으로 하는 DashScope 호환
커스텀 제공자 ID도 내장 `qwen` 제공자 ID를 특별히 요구하지 않고
동일한 스트리밍 usage 동작을 상속받습니다.

## API 키 가져오기

- **키 관리**: [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys)
- **문서**: [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)

## 내장 카탈로그

현재 OpenClaw는 다음 번들 Qwen 카탈로그를 제공합니다:

| 모델 ref | 입력 | 컨텍스트 | 참고 |
| --------------------------- | ----------- | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus` | text, image | 1,000,000 | 기본 모델 |
| `qwen/qwen3.6-plus` | text, image | 1,000,000 | 이 모델이 필요하면 Standard 엔드포인트를 우선 사용 |
| `qwen/qwen3-max-2026-01-23` | text | 262,144 | Qwen Max 계열 |
| `qwen/qwen3-coder-next` | text | 262,144 | 코딩 |
| `qwen/qwen3-coder-plus` | text | 1,000,000 | 코딩 |
| `qwen/MiniMax-M2.5` | text | 1,000,000 | reasoning 활성화 |
| `qwen/glm-5` | text | 202,752 | GLM |
| `qwen/glm-4.7` | text | 202,752 | GLM |
| `qwen/kimi-k2.5` | text, image | 262,144 | Alibaba를 통한 Moonshot AI |

모델이 번들 카탈로그에 있더라도 엔드포인트와 과금 플랜에 따라 사용 가능 여부는
여전히 달라질 수 있습니다.

네이티브 스트리밍 usage 호환성은 Coding Plan 호스트와
Standard DashScope 호환 호스트 모두에 적용됩니다:

- `https://coding.dashscope.aliyuncs.com/v1`
- `https://coding-intl.dashscope.aliyuncs.com/v1`
- `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## Qwen 3.6 Plus 사용 가능 여부

`qwen3.6-plus`는 Standard(종량제) Model Studio 엔드포인트에서
사용할 수 있습니다:

- China: `dashscope.aliyuncs.com/compatible-mode/v1`
- Global: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

Coding Plan 엔드포인트가 `qwen3.6-plus`에 대해
"unsupported model" 오류를 반환하면, Coding Plan 엔드포인트/키 쌍 대신
Standard(종량제)로 전환하세요.

## 환경 참고

Gateway가 데몬(launchd/systemd)으로 실행되는 경우,
`QWEN_API_KEY`가 해당 프로세스에서 사용 가능하도록
설정되어 있는지 확인하세요(예: `~/.openclaw/.env` 또는
`env.shellEnv`를 통해).
