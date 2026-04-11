---
read_when:
    - 에이전트를 통한 비디오 생성
    - 비디오 생성 제공업체 및 모델 구성
    - '`video_generate` 도구 매개변수 이해하기'
summary: 14개의 제공업체 백엔드를 사용해 텍스트, 이미지 또는 기존 비디오로부터 비디오를 생성합니다
title: 비디오 생성
x-i18n:
    generated_at: "2026-04-11T15:15:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0ec159a0bbb6b8a030e68828c0a8bcaf40c8538ecf98bc8ff609dab9d0068263
    source_path: tools/video-generation.md
    workflow: 15
---

# 비디오 생성

OpenClaw 에이전트는 텍스트 프롬프트, 참조 이미지 또는 기존 비디오로부터 비디오를 생성할 수 있습니다. 서로 다른 모델 옵션, 입력 모드, 기능 집합을 제공하는 14개의 제공업체 백엔드가 지원됩니다. 에이전트는 구성과 사용 가능한 API 키를 바탕으로 적절한 제공업체를 자동으로 선택합니다.

<Note>
`video_generate` 도구는 최소 하나의 비디오 생성 제공업체를 사용할 수 있을 때만 표시됩니다. 에이전트 도구에 이 항목이 보이지 않으면 제공업체 API 키를 설정하거나 `agents.defaults.videoGenerationModel`을 구성하세요.
</Note>

OpenClaw는 비디오 생성을 세 가지 런타임 모드로 처리합니다.

- 참조 미디어가 없는 텍스트-비디오 요청용 `generate`
- 요청에 하나 이상의 참조 이미지가 포함된 경우의 `imageToVideo`
- 요청에 하나 이상의 참조 비디오가 포함된 경우의 `videoToVideo`

제공업체는 이러한 모드 중 일부만 지원할 수 있습니다. 도구는 제출 전에 현재
모드를 검증하고, `action=list`에서 지원되는 모드를 보고합니다.

## 빠른 시작

1. 지원되는 아무 제공업체의 API 키나 설정합니다.

```bash
export GEMINI_API_KEY="your-key"
```

2. 필요하면 기본 모델을 고정합니다.

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. 에이전트에게 요청합니다.

> 해질녘에 서핑하는 친근한 랍스터의 5초짜리 영화 같은 비디오를 생성해 줘.

에이전트가 `video_generate`를 자동으로 호출합니다. 도구 허용 목록 구성은 필요하지 않습니다.

## 비디오를 생성하면 어떤 일이 일어나는가

비디오 생성은 비동기식입니다. 세션에서 에이전트가 `video_generate`를 호출하면 다음과 같이 진행됩니다.

1. OpenClaw가 요청을 제공업체에 제출하고 즉시 작업 ID를 반환합니다.
2. 제공업체가 백그라운드에서 작업을 처리합니다(일반적으로 제공업체와 해상도에 따라 30초에서 5분).
3. 비디오가 준비되면 OpenClaw가 내부 완료 이벤트로 같은 세션을 다시 깨웁니다.
4. 에이전트가 완성된 비디오를 원래 대화에 다시 게시합니다.

작업이 진행 중인 동안 같은 세션에서 중복된 `video_generate` 호출이 들어오면 새 생성을 시작하는 대신 현재 작업 상태를 반환합니다. CLI에서 진행 상황을 확인하려면 `openclaw tasks list` 또는 `openclaw tasks show <taskId>`를 사용하세요.

세션 기반 에이전트 실행 외부에서(예: 직접 도구 호출) 이 도구는 인라인 생성으로 대체되며 같은 턴에서 최종 미디어 경로를 반환합니다.

### 작업 수명 주기

각 `video_generate` 요청은 네 가지 상태를 거칩니다.

1. **queued** -- 작업이 생성되었고, 제공업체가 수락하기를 기다리는 중입니다.
2. **running** -- 제공업체가 처리 중입니다(일반적으로 제공업체와 해상도에 따라 30초에서 5분).
3. **succeeded** -- 비디오가 준비되었으며, 에이전트가 다시 깨어나 대화에 게시합니다.
4. **failed** -- 제공업체 오류 또는 시간 초과가 발생했으며, 에이전트가 오류 세부 정보와 함께 다시 깨어납니다.

CLI에서 상태를 확인하세요.

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

중복 방지: 현재 세션에 대해 비디오 작업이 이미 `queued` 또는 `running` 상태이면 `video_generate`는 새 작업을 시작하는 대신 기존 작업 상태를 반환합니다. 새 생성을 유발하지 않고 명시적으로 확인하려면 `action: "status"`를 사용하세요.

## 지원되는 제공업체

| 제공업체              | 기본 모델                        | 텍스트 | 이미지 참조                                          | 비디오 참조      | API 키                                   |
| --------------------- | -------------------------------- | ------ | ---------------------------------------------------- | ---------------- | ---------------------------------------- |
| Alibaba               | `wan2.6-t2v`                     | 예     | 예 (원격 URL)                                        | 예 (원격 URL)    | `MODELSTUDIO_API_KEY`                    |
| BytePlus (1.0)        | `seedance-1-0-pro-250528`        | 예     | 최대 이미지 2개 (I2V 모델 전용; 첫 프레임 + 마지막 프레임) | 아니요           | `BYTEPLUS_API_KEY`                       |
| BytePlus Seedance 1.5 | `seedance-1-5-pro-251215`        | 예     | 최대 이미지 2개 (역할 기반 첫 프레임 + 마지막 프레임)     | 아니요           | `BYTEPLUS_API_KEY`                       |
| BytePlus Seedance 2.0 | `dreamina-seedance-2-0-260128`   | 예     | 최대 참조 이미지 9개                                  | 최대 비디오 3개  | `BYTEPLUS_API_KEY`                       |
| ComfyUI               | `workflow`                       | 예     | 이미지 1개                                           | 아니요           | `COMFY_API_KEY` 또는 `COMFY_CLOUD_API_KEY` |
| fal                   | `fal-ai/minimax/video-01-live`   | 예     | 이미지 1개                                           | 아니요           | `FAL_KEY`                                |
| Google                | `veo-3.1-fast-generate-preview`  | 예     | 이미지 1개                                           | 비디오 1개       | `GEMINI_API_KEY`                         |
| MiniMax               | `MiniMax-Hailuo-2.3`             | 예     | 이미지 1개                                           | 아니요           | `MINIMAX_API_KEY`                        |
| OpenAI                | `sora-2`                         | 예     | 이미지 1개                                           | 비디오 1개       | `OPENAI_API_KEY`                         |
| Qwen                  | `wan2.6-t2v`                     | 예     | 예 (원격 URL)                                        | 예 (원격 URL)    | `QWEN_API_KEY`                           |
| Runway                | `gen4.5`                         | 예     | 이미지 1개                                           | 비디오 1개       | `RUNWAYML_API_SECRET`                    |
| Together              | `Wan-AI/Wan2.2-T2V-A14B`         | 예     | 이미지 1개                                           | 아니요           | `TOGETHER_API_KEY`                       |
| Vydra                 | `veo3`                           | 예     | 이미지 1개 (`kling`)                                 | 아니요           | `VYDRA_API_KEY`                          |
| xAI                   | `grok-imagine-video`             | 예     | 이미지 1개                                           | 비디오 1개       | `XAI_API_KEY`                            |

일부 제공업체는 추가 또는 대체 API 키 환경 변수를 받습니다. 자세한 내용은 개별 [제공업체 페이지](#related)를 참조하세요.

런타임에 사용 가능한 제공업체, 모델, 런타임 모드를 확인하려면 `video_generate action=list`를 실행하세요.

### 선언된 기능 매트릭스

이 표는 `video_generate`, 계약 테스트,
공유 라이브 스윕에서 사용하는 명시적 모드 계약입니다.

| 제공업체 | `generate` | `imageToVideo` | `videoToVideo` | 현재의 공유 라이브 레인                                                                                                                    |
| -------- | ---------- | -------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | 예         | 예             | 예             | `generate`, `imageToVideo`; 이 제공업체는 원격 `http(s)` 비디오 URL이 필요하므로 `videoToVideo`는 건너뜀                                  |
| BytePlus | 예         | 예             | 아니요         | `generate`, `imageToVideo`                                                                                                                |
| ComfyUI  | 예         | 예             | 아니요         | 공유 스윕에는 포함되지 않음; 워크플로별 커버리지는 Comfy 테스트에 있음                                                                    |
| fal      | 예         | 예             | 아니요         | `generate`, `imageToVideo`                                                                                                                |
| Google   | 예         | 예             | 예             | `generate`, `imageToVideo`; 현재 버퍼 기반 Gemini/Veo 스윕은 해당 입력을 받지 않으므로 공유 `videoToVideo`는 건너뜀                      |
| MiniMax  | 예         | 예             | 아니요         | `generate`, `imageToVideo`                                                                                                                |
| OpenAI   | 예         | 예             | 예             | `generate`, `imageToVideo`; 현재 이 조직/입력 경로는 제공업체 측 인페인트/리믹스 접근이 필요하므로 공유 `videoToVideo`는 건너뜀           |
| Qwen     | 예         | 예             | 예             | `generate`, `imageToVideo`; 이 제공업체는 원격 `http(s)` 비디오 URL이 필요하므로 `videoToVideo`는 건너뜀                                  |
| Runway   | 예         | 예             | 예             | `generate`, `imageToVideo`; `videoToVideo`는 선택된 모델이 `runway/gen4_aleph`일 때만 실행됨                                              |
| Together | 예         | 예             | 아니요         | `generate`, `imageToVideo`                                                                                                                |
| Vydra    | 예         | 예             | 아니요         | `generate`; 번들된 `veo3`는 텍스트 전용이고 번들된 `kling`은 원격 이미지 URL이 필요하므로 공유 `imageToVideo`는 건너뜀                    |
| xAI      | 예         | 예             | 예             | `generate`, `imageToVideo`; 이 제공업체는 현재 원격 MP4 URL이 필요하므로 `videoToVideo`는 건너뜀                                          |

## 도구 매개변수

### 필수

| 매개변수 | 유형   | 설명                                                                        |
| -------- | ------ | --------------------------------------------------------------------------- |
| `prompt` | string | 생성할 비디오의 텍스트 설명 (`action: "generate"`에 필수)                   |

### 콘텐츠 입력

| 매개변수    | 유형     | 설명                                                                                                                              |
| ----------- | -------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `image`     | string   | 단일 참조 이미지(경로 또는 URL)                                                                                                   |
| `images`    | string[] | 여러 참조 이미지(최대 9개)                                                                                                        |
| `imageRoles`| string[] | 결합된 이미지 목록과 병렬인 위치별 선택적 역할 힌트입니다. 표준값: `first_frame`, `last_frame`, `reference_image`                 |
| `video`     | string   | 단일 참조 비디오(경로 또는 URL)                                                                                                   |
| `videos`    | string[] | 여러 참조 비디오(최대 4개)                                                                                                        |
| `videoRoles`| string[] | 결합된 비디오 목록과 병렬인 위치별 선택적 역할 힌트입니다. 표준값: `reference_video`                                              |
| `audioRef`  | string   | 단일 참조 오디오(경로 또는 URL). 제공업체가 오디오 입력을 지원할 때 배경 음악 또는 음성 참조 등에 사용됩니다                     |
| `audioRefs` | string[] | 여러 참조 오디오(최대 3개)                                                                                                        |
| `audioRoles`| string[] | 결합된 오디오 목록과 병렬인 위치별 선택적 역할 힌트입니다. 표준값: `reference_audio`                                              |

역할 힌트는 제공업체에 그대로 전달됩니다. 표준값은
`VideoGenerationAssetRole` 유니언에서 오지만, 제공업체는 추가
역할 문자열도 허용할 수 있습니다. `*Roles` 배열은 해당하는
참조 목록보다 더 많은 항목을 가질 수 없으며, 하나 차이 나는 실수는 명확한 오류와 함께 실패합니다.
슬롯을 설정하지 않으려면 빈 문자열을 사용하세요.

### 스타일 제어

| 매개변수         | 유형    | 설명                                                                                  |
| ---------------- | ------- | ------------------------------------------------------------------------------------- |
| `aspectRatio`    | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`, 또는 `adaptive` |
| `resolution`     | string  | `480P`, `720P`, `768P`, 또는 `1080P`                                                  |
| `durationSeconds`| number  | 목표 길이(초)이며, 가장 가까운 제공업체 지원 값으로 반올림됩니다                     |
| `size`           | string  | 제공업체가 지원할 때 사용하는 크기 힌트                                              |
| `audio`          | boolean | 지원될 때 출력에 생성 오디오를 활성화합니다. `audioRef*`(입력)와는 구분됩니다        |
| `watermark`      | boolean | 지원될 때 제공업체 워터마크 적용을 전환합니다                                        |

`adaptive`는 제공업체별 특수 센티널 값입니다. 이 값은
기능에 `adaptive`를 선언한 제공업체에 그대로 전달됩니다(예: BytePlus
Seedance는 이를 사용해 입력 이미지
크기에서 비율을 자동 감지합니다). 이를 선언하지 않은 제공업체는
드롭된 값이 보이도록 도구 결과의
`details.ignoredOverrides`를 통해 해당 값을 노출합니다.

### 고급

| 매개변수         | 유형   | 설명                                                                                                                                                                                                                                                                                                                                                  |
| ---------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `action`         | string | `"generate"`(기본값), `"status"`, 또는 `"list"`                                                                                                                                                                                                                                                                                                      |
| `model`          | string | 제공업체/모델 재정의(예: `runway/gen4.5`)                                                                                                                                                                                                                                                                                                            |
| `filename`       | string | 출력 파일명 힌트                                                                                                                                                                                                                                                                                                                                     |
| `providerOptions`| object | JSON 객체 형식의 제공업체별 옵션(예: `{"seed": 42, "draft": true}`). 타입이 지정된 스키마를 선언한 제공업체는 키와 타입을 검증하며, 알 수 없는 키나 타입 불일치가 있으면 폴백 중 해당 후보를 건너뜁니다. 선언된 스키마가 없는 제공업체는 옵션을 그대로 받습니다. 각 제공업체가 허용하는 항목은 `video_generate action=list`로 확인하세요 |

모든 제공업체가 모든 매개변수를 지원하는 것은 아닙니다. OpenClaw는 이미 길이를 가장 가까운 제공업체 지원 값으로 정규화하며, 폴백 제공업체가 다른 제어 표면을 노출할 때 size-to-aspect-ratio 같은 변환된 기하 힌트도 다시 매핑합니다. 실제로 지원되지 않는 재정의는 최선의 노력 기준으로 무시되며 도구 결과에 경고로 보고됩니다. 참조 입력이 너무 많은 경우처럼 엄격한 기능 한계는 제출 전에 실패합니다.

도구 결과는 적용된 설정을 보고합니다. 제공업체 폴백 중 OpenClaw가 길이나 기하를 재매핑하면, 반환되는 `durationSeconds`, `size`, `aspectRatio`, `resolution` 값은 실제 제출된 값을 반영하고, `details.normalization`에는 요청값에서 적용값으로의 변환이 기록됩니다.

참조 입력은 런타임 모드도 선택합니다.

- 참조 미디어 없음: `generate`
- 이미지 참조가 하나라도 있음: `imageToVideo`
- 비디오 참조가 하나라도 있음: `videoToVideo`
- 참조 오디오 입력은 결정된 모드를 바꾸지 않습니다. 대신 이미지/비디오 참조가 선택한 모드 위에 적용되며, `maxInputAudios`를 선언한 제공업체에서만 작동합니다.

이미지와 비디오 참조를 혼합하는 것은 안정적인 공유 기능 표면이 아닙니다.
요청당 하나의 참조 유형을 사용하는 것을 권장합니다.

#### 폴백과 타입 지정 옵션

일부 기능 검사는 도구 경계가 아니라 폴백 계층에서 적용되므로,
기본 제공업체의 한도를 초과하는 요청도
해당 기능을 지원하는 폴백에서 계속 실행될 수 있습니다.

- 활성 후보가 `maxInputAudios`를 선언하지 않았거나(`0`으로
  선언한 경우 포함), 요청에 오디오 참조가 포함되어 있으면
  해당 후보를 건너뛰고 다음 후보를 시도합니다.
- 활성 후보의 `maxDurationSeconds`가 요청된
  `durationSeconds`보다 낮고, 후보가
  `supportedDurationSeconds` 목록을 선언하지 않은 경우에는 건너뜁니다.
- 요청에 `providerOptions`가 포함되어 있고 활성 후보가
  타입 지정된 `providerOptions` 스키마를 명시적으로 선언한 경우,
  제공된 키가 스키마에 없거나 값 타입이
  일치하지 않으면 해당 후보를 건너뜁니다. 아직 스키마를 선언하지 않은
  제공업체는 옵션을 그대로 받습니다(하위 호환 패스스루). 제공업체는
  빈 스키마를 선언해(`capabilities.providerOptions: {}`)
  모든 제공업체 옵션을 명시적으로 거부할 수 있으며, 이 경우에도
  타입 불일치와 같은 방식으로 건너뜁니다.

요청에서 첫 번째 건너뛰기 사유는 운영자가
기본 제공업체가 왜 제외되었는지 볼 수 있도록 `warn`에 기록됩니다.
이후 건너뛰기는 긴 폴백 체인을 조용히 유지하기 위해
`debug`에 기록됩니다. 모든 후보가 건너뛰어지면,
집계된 오류에 각 후보의 건너뛰기 사유가 포함됩니다.

## 작업

- **generate** (기본값) -- 주어진 프롬프트와 선택적 참조 입력으로 비디오를 생성합니다.
- **status** -- 현재 세션에서 진행 중인 비디오 작업의 상태를 확인하며, 새 생성을 시작하지 않습니다.
- **list** -- 사용 가능한 제공업체, 모델, 그리고 각 기능을 표시합니다.

## 모델 선택

비디오를 생성할 때 OpenClaw는 다음 순서로 모델을 결정합니다.

1. **`model` 도구 매개변수** -- 에이전트가 호출에서 이를 지정한 경우
2. **`videoGenerationModel.primary`** -- config에서 가져옴
3. **`videoGenerationModel.fallbacks`** -- 순서대로 시도
4. **자동 감지** -- 유효한 인증이 있는 제공업체를 사용하며, 현재 기본 제공업체부터 시작한 뒤 나머지 제공업체를 알파벳순으로 시도

제공업체가 실패하면 다음 후보를 자동으로 시도합니다. 모든 후보가 실패하면 오류에 각 시도의 세부 정보가 포함됩니다.

비디오 생성이 명시적인 `model`, `primary`, `fallbacks`
항목만 사용하도록 하려면
`agents.defaults.mediaGenerationAutoProviderFallback: false`를 설정하세요.

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["runway/gen4.5", "qwen/wan2.6-t2v"],
      },
    },
  },
}
```

## 제공업체 참고 사항

| 제공업체              | 참고 사항                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Alibaba               | DashScope/Model Studio 비동기 엔드포인트를 사용합니다. 참조 이미지와 비디오는 원격 `http(s)` URL이어야 합니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| BytePlus (1.0)        | 제공업체 ID는 `byteplus`입니다. 모델: `seedance-1-0-pro-250528`(기본값), `seedance-1-0-pro-t2v-250528`, `seedance-1-0-pro-fast-251015`, `seedance-1-0-lite-t2v-250428`, `seedance-1-0-lite-i2v-250428`. T2V 모델(`*-t2v-*`)은 이미지 입력을 받을 수 없습니다. I2V 모델과 일반 `*-pro-*` 모델은 단일 참조 이미지(첫 프레임)를 지원합니다. 이미지를 위치 기반으로 전달하거나 `role: "first_frame"`을 설정하세요. 이미지가 제공되면 T2V 모델 ID는 대응하는 I2V 변형으로 자동 전환됩니다. 지원되는 `providerOptions` 키: `seed`(number), `draft`(boolean, 480p 강제), `camera_fixed`(boolean). |
| BytePlus Seedance 1.5 | [`@openclaw/byteplus-modelark`](https://www.npmjs.com/package/@openclaw/byteplus-modelark) 플러그인이 필요합니다. 제공업체 ID는 `byteplus-seedance15`입니다. 모델: `seedance-1-5-pro-251215`. 통합 `content[]` API를 사용합니다. 최대 2개의 입력 이미지(first_frame + last_frame)를 지원합니다. 모든 입력은 원격 `https://` URL이어야 합니다. 각 이미지에 `role: "first_frame"` / `"last_frame"`를 설정하거나, 이미지를 위치 기반으로 전달하세요. `aspectRatio: "adaptive"`는 입력 이미지에서 비율을 자동 감지합니다. `audio: true`는 `generate_audio`로 매핑됩니다. `providerOptions.seed`(number)가 전달됩니다.                                                                 |
| BytePlus Seedance 2.0 | [`@openclaw/byteplus-modelark`](https://www.npmjs.com/package/@openclaw/byteplus-modelark) 플러그인이 필요합니다. 제공업체 ID는 `byteplus-seedance2`입니다. 모델: `dreamina-seedance-2-0-260128`, `dreamina-seedance-2-0-fast-260128`. 통합 `content[]` API를 사용합니다. 최대 9개의 참조 이미지, 3개의 참조 비디오, 3개의 참조 오디오를 지원합니다. 모든 입력은 원격 `https://` URL이어야 합니다. 각 자산에 `role`을 설정하세요 — 지원 값: `"first_frame"`, `"last_frame"`, `"reference_image"`, `"reference_video"`, `"reference_audio"`. `aspectRatio: "adaptive"`는 입력 이미지에서 비율을 자동 감지합니다. `audio: true`는 `generate_audio`로 매핑됩니다. `providerOptions.seed`(number)가 전달됩니다. |
| ComfyUI               | 워크플로 기반의 로컬 또는 클라우드 실행을 사용합니다. 구성된 그래프를 통해 텍스트-비디오와 이미지-비디오를 지원합니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| fal                   | 장시간 실행 작업에 큐 기반 흐름을 사용합니다. 단일 이미지 참조만 지원합니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Google                | Gemini/Veo를 사용합니다. 이미지 또는 비디오 참조를 각각 하나씩 지원합니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| MiniMax               | 단일 이미지 참조만 지원합니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| OpenAI                | `size` 재정의만 전달됩니다. 다른 스타일 재정의(`aspectRatio`, `resolution`, `audio`, `watermark`)는 경고와 함께 무시됩니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Qwen                  | Alibaba와 동일한 DashScope 백엔드를 사용합니다. 참조 입력은 원격 `http(s)` URL이어야 하며, 로컬 파일은 사전에 거부됩니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Runway                | 데이터 URI를 통해 로컬 파일을 지원합니다. 비디오-투-비디오에는 `runway/gen4_aleph`가 필요합니다. 텍스트 전용 실행은 `16:9`와 `9:16` 화면비를 제공합니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Together              | 단일 이미지 참조만 지원합니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Vydra                 | 인증이 빠지는 리디렉션을 피하기 위해 `https://www.vydra.ai/api/v1`를 직접 사용합니다. `veo3`는 텍스트-비디오 전용으로 번들되며, `kling`은 원격 이미지 URL이 필요합니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| xAI                   | 텍스트-비디오, 이미지-비디오, 원격 비디오 편집/확장 흐름을 지원합니다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

## 제공업체 기능 모드

이제 공유 비디오 생성 계약은 제공업체가
단순한 평면 집계 한도만이 아니라 모드별 기능도 선언할 수 있게 합니다. 새 제공업체
구현에서는 명시적인 모드 블록을 사용하는 것이 좋습니다.

```typescript
capabilities: {
  generate: {
    maxVideos: 1,
    maxDurationSeconds: 10,
    supportsResolution: true,
  },
  imageToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputImages: 1,
    maxDurationSeconds: 5,
  },
  videoToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputVideos: 1,
    maxDurationSeconds: 5,
  },
}
```

`maxInputImages`와 `maxInputVideos` 같은 평면 집계 필드만으로는
변환 모드 지원을 광고하기에 충분하지 않습니다. 제공업체는 라이브 테스트,
계약 테스트, 공유 `video_generate` 도구가 모드 지원을
결정적으로 검증할 수 있도록 `generate`, `imageToVideo`, `videoToVideo`를
명시적으로 선언해야 합니다.

## 라이브 테스트

공유 번들 제공업체에 대한 옵트인 라이브 커버리지:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts
```

리포지토리 래퍼:

```bash
pnpm test:live:media video
```

이 라이브 파일은 `~/.profile`에서 누락된 제공업체 환경 변수를 로드하고, 기본적으로 저장된 인증 프로필보다
라이브/환경 API 키를 우선하며, 로컬 미디어로 안전하게 실행할 수 있는
선언된 모드를 실행합니다.

- 스윕에 포함된 모든 제공업체에 대해 `generate`
- `capabilities.imageToVideo.enabled`일 때 `imageToVideo`
- `capabilities.videoToVideo.enabled`이고 제공업체/모델이 공유 스윕에서
  버퍼 기반 로컬 비디오 입력을 받을 수 있을 때 `videoToVideo`

현재 공유 `videoToVideo` 라이브 레인은 다음을 커버합니다.

- `runway/gen4_aleph`를 선택한 경우에만 `runway`

## 구성

OpenClaw config에서 기본 비디오 생성 모델을 설정하세요.

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-r2v-flash"],
      },
    },
  },
}
```

또는 CLI를 통해 설정할 수 있습니다.

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "qwen/wan2.6-t2v"
```

## 관련 문서

- [도구 개요](/ko/tools)
- [백그라운드 작업](/ko/automation/tasks) -- 비동기 비디오 생성을 위한 작업 추적
- [Alibaba Model Studio](/ko/providers/alibaba)
- [BytePlus](/ko/concepts/model-providers#byteplus-international)
- [ComfyUI](/ko/providers/comfy)
- [fal](/ko/providers/fal)
- [Google (Gemini)](/ko/providers/google)
- [MiniMax](/ko/providers/minimax)
- [OpenAI](/ko/providers/openai)
- [Qwen](/ko/providers/qwen)
- [Runway](/ko/providers/runway)
- [Together AI](/ko/providers/together)
- [Vydra](/ko/providers/vydra)
- [xAI](/ko/providers/xai)
- [구성 참조](/ko/gateway/configuration-reference#agent-defaults)
- [모델](/ko/concepts/models)
