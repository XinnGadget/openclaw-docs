---
read_when:
    - OpenClaw plugin을 빌드하는 경우
    - plugin config 스키마를 제공하거나 plugin 검증 오류를 디버그해야 하는 경우
summary: 플러그인 manifest + JSON 스키마 요구 사항(엄격한 config 검증)
title: 플러그인 매니페스트
x-i18n:
    generated_at: "2026-04-05T12:50:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: 702447ad39f295cfffd4214c3e389bee667d2f9850754f2e02e325dde8e4ac00
    source_path: plugins/manifest.md
    workflow: 15
---

# 플러그인 매니페스트 (openclaw.plugin.json)

이 페이지는 **네이티브 OpenClaw plugin manifest** 전용입니다.

호환 번들 레이아웃은 [Plugin bundles](/plugins/bundles)를 참조하세요.

호환 번들 형식은 다른 manifest 파일을 사용합니다.

- Codex 번들: `.codex-plugin/plugin.json`
- Claude 번들: `.claude-plugin/plugin.json` 또는 manifest가 없는 기본 Claude component
  레이아웃
- Cursor 번들: `.cursor-plugin/plugin.json`

OpenClaw는 이러한 번들 레이아웃도 자동 감지하지만, 여기서 설명하는
`openclaw.plugin.json` 스키마에 대해 검증되지는 않습니다.

호환 번들의 경우 OpenClaw는 현재 번들 메타데이터와 선언된
skill 루트, Claude command 루트, Claude 번들 `settings.json` 기본값,
Claude 번들 LSP 기본값, 그리고 레이아웃이
OpenClaw 런타임 기대사항과 일치할 때 지원되는 hook pack을 읽습니다.

모든 네이티브 OpenClaw plugin은 **plugin 루트**에 반드시 `openclaw.plugin.json` 파일을 포함해야 합니다.
OpenClaw는 이 manifest를 사용해 plugin 코드를 **실행하지 않고도**
구성을 검증합니다. 누락되었거나 유효하지 않은 manifest는
plugin 오류로 처리되며 config 검증을 차단합니다.

전체 plugin 시스템 가이드는 [Plugins](/tools/plugin)를 참조하세요.
네이티브 기능 모델과 현재 외부 호환성 지침은
[Capability model](/plugins/architecture#public-capability-model)을 참조하세요.

## 이 파일의 역할

`openclaw.plugin.json`은 OpenClaw가 plugin 코드를 로드하기 전에 읽는
메타데이터입니다.

용도:

- plugin 식별
- config 검증
- plugin 런타임을 부팅하지 않고도 사용할 수 있어야 하는 auth 및 onboarding 메타데이터
- plugin 런타임이 로드되기 전에 해석되어야 하는 alias 및 자동 활성화 메타데이터
- plugin 런타임이 로드되기 전에 plugin을 자동 활성화해야 하는 shorthand model-family 소유권 메타데이터
- 번들 호환 연결 및 계약 커버리지에 사용되는 정적 기능 소유권 스냅샷
- 런타임을 로드하지 않고 카탈로그 및 검증 표면에 병합되어야 하는 채널별 config 메타데이터
- config UI 힌트

다음 용도로는 사용하지 마세요.

- 런타임 동작 등록
- 코드 entrypoint 선언
- npm 설치 메타데이터

이것들은 plugin 코드와 `package.json`에 속합니다.

## 최소 예시

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## 확장 예시

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "OpenRouter provider plugin",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "OpenRouter API 키",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API 키",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API 키",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## 최상위 필드 참조

| Field                               | 필수 여부 | Type                             | 의미                                                                                                                                                                              |
| ----------------------------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | 예      | `string`                         | 정규 plugin ID입니다. 이 ID는 `plugins.entries.<id>`에서 사용됩니다.                                                                                                                        |
| `configSchema`                      | 예      | `object`                         | 이 plugin config에 대한 인라인 JSON Schema입니다.                                                                                                                                               |
| `enabledByDefault`                  | 아니요       | `true`                           | 번들 plugin이 기본적으로 활성화됨을 표시합니다. 기본적으로 비활성화된 상태로 두려면 생략하거나 `true`가 아닌 값을 설정하세요.                                                               |
| `legacyPluginIds`                   | 아니요       | `string[]`                       | 이 정규 plugin ID로 정규화되는 레거시 ID입니다.                                                                                                                                     |
| `autoEnableWhenConfiguredProviders` | 아니요       | `string[]`                       | auth, config 또는 model ref가 이를 언급할 때 이 plugin을 자동 활성화해야 하는 provider ID입니다.                                                                                            |
| `kind`                              | 아니요       | `"memory"` \| `"context-engine"` | `plugins.slots.*`에서 사용되는 배타적 plugin 종류를 선언합니다.                                                                                                                               |
| `channels`                          | 아니요       | `string[]`                       | 이 plugin이 소유하는 채널 ID입니다. discovery 및 config 검증에 사용됩니다.                                                                                                                |
| `providers`                         | 아니요       | `string[]`                       | 이 plugin이 소유하는 provider ID입니다.                                                                                                                                                         |
| `modelSupport`                      | 아니요       | `object`                         | 런타임 전에 plugin을 자동 로드하는 데 사용되는 manifest 소유 shorthand model-family 메타데이터입니다.                                                                                                |
| `cliBackends`                       | 아니요       | `string[]`                       | 이 plugin이 소유하는 CLI 추론 backend ID입니다. 명시적 config ref로부터 시작 시 자동 활성화하는 데 사용됩니다.                                                                                |
| `providerAuthEnvVars`               | 아니요       | `Record<string, string[]>`       | OpenClaw가 plugin 코드를 로드하지 않고도 검사할 수 있는 가벼운 provider-auth env 메타데이터입니다.                                                                                                    |
| `providerAuthChoices`               | 아니요       | `object[]`                       | onboarding picker, preferred-provider 해석, 단순 CLI flag 연결을 위한 가벼운 auth-choice 메타데이터입니다.                                                                              |
| `contracts`                         | 아니요       | `object`                         | speech, realtime transcription, realtime voice, media-understanding, image-generation, video-generation, web-fetch, web search 및 tool ownership에 대한 정적 번들 기능 스냅샷입니다. |
| `channelConfigs`                    | 아니요       | `Record<string, object>`         | 런타임 로드 전에 discovery 및 검증 표면에 병합되는 manifest 소유 채널 config 메타데이터입니다.                                                                                 |
| `skills`                            | 아니요       | `string[]`                       | plugin 루트 기준 상대 경로인 skill 디렉터리입니다.                                                                                                                                    |
| `name`                              | 아니요       | `string`                         | 사람이 읽기 쉬운 plugin 이름입니다.                                                                                                                                                                |
| `description`                       | 아니요       | `string`                         | plugin 표면에 표시되는 짧은 요약입니다.                                                                                                                                                    |
| `version`                           | 아니요       | `string`                         | 정보용 plugin 버전입니다.                                                                                                                                                              |
| `uiHints`                           | 아니요       | `Record<string, object>`         | config 필드용 UI 라벨, placeholder 및 민감도 힌트입니다.                                                                                                                          |

## providerAuthChoices 참조

각 `providerAuthChoices` 항목은 하나의 onboarding 또는 auth 선택지를 설명합니다.
OpenClaw는 provider 런타임이 로드되기 전에 이를 읽습니다.

| Field                 | 필수 여부 | Type                                            | 의미                                                                                            |
| --------------------- | -------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `provider`            | 예      | `string`                                        | 이 선택지가 속한 provider ID입니다.                                                                      |
| `method`              | 예      | `string`                                        | 디스패치할 auth method ID입니다.                                                                           |
| `choiceId`            | 예      | `string`                                        | onboarding 및 CLI 흐름에서 사용되는 안정적인 auth-choice ID입니다.                                                  |
| `choiceLabel`         | 아니요       | `string`                                        | 사용자에게 표시되는 라벨입니다. 생략하면 OpenClaw는 `choiceId`로 대체합니다.                                        |
| `choiceHint`          | 아니요       | `string`                                        | picker용 짧은 도움말 텍스트입니다.                                                                        |
| `assistantPriority`   | 아니요       | `number`                                        | 값이 낮을수록 assistant 주도 대화형 picker에서 더 앞에 정렬됩니다.                                       |
| `assistantVisibility` | 아니요       | `"visible"` \| `"manual-only"`                  | assistant picker에서는 숨기되 수동 CLI 선택은 계속 허용합니다.                        |
| `deprecatedChoiceIds` | 아니요       | `string[]`                                      | 사용자를 이 대체 선택지로 리디렉션해야 하는 레거시 choice ID입니다.                                 |
| `groupId`             | 아니요       | `string`                                        | 관련 선택지를 그룹화하기 위한 선택적 group ID입니다.                                                          |
| `groupLabel`          | 아니요       | `string`                                        | 해당 그룹의 사용자용 라벨입니다.                                                                        |
| `groupHint`           | 아니요       | `string`                                        | 그룹용 짧은 도움말 텍스트입니다.                                                                         |
| `optionKey`           | 아니요       | `string`                                        | 단일 flag auth 흐름용 내부 옵션 키입니다.                                                      |
| `cliFlag`             | 아니요       | `string`                                        | `--openrouter-api-key` 같은 CLI flag 이름입니다.                                                           |
| `cliOption`           | 아니요       | `string`                                        | `--openrouter-api-key <key>` 같은 전체 CLI 옵션 형태입니다.                                             |
| `cliDescription`      | 아니요       | `string`                                        | CLI 도움말에 사용되는 설명입니다.                                                                            |
| `onboardingScopes`    | 아니요       | `Array<"text-inference" \| "image-generation">` | 이 선택지가 표시되어야 하는 onboarding 표면입니다. 생략하면 기본값은 `["text-inference"]`입니다. |

## uiHints 참조

`uiHints`는 config 필드 이름에서 작은 렌더링 힌트로의 맵입니다.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API 키",
      "help": "OpenRouter 요청에 사용됨",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

각 필드 힌트에는 다음이 포함될 수 있습니다.

| Field         | Type       | 의미                           |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | 사용자용 필드 라벨입니다.                |
| `help`        | `string`   | 짧은 도움말 텍스트입니다.                      |
| `tags`        | `string[]` | 선택적 UI 태그입니다.                       |
| `advanced`    | `boolean`  | 필드를 고급 항목으로 표시합니다.            |
| `sensitive`   | `boolean`  | 필드를 시크릿 또는 민감 항목으로 표시합니다. |
| `placeholder` | `string`   | 폼 입력용 placeholder 텍스트입니다.       |

## contracts 참조

`contracts`는 OpenClaw가
plugin 런타임을 import하지 않고도 읽을 수 있는 정적 기능 소유권 메타데이터에만 사용하세요.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

각 목록은 선택 사항입니다.

| Field                            | Type       | 의미                                                  |
| -------------------------------- | ---------- | -------------------------------------------------------------- |
| `speechProviders`                | `string[]` | 이 plugin이 소유하는 speech provider ID입니다.                          |
| `realtimeTranscriptionProviders` | `string[]` | 이 plugin이 소유하는 realtime-transcription provider ID입니다.          |
| `realtimeVoiceProviders`         | `string[]` | 이 plugin이 소유하는 realtime-voice provider ID입니다.                  |
| `mediaUnderstandingProviders`    | `string[]` | 이 plugin이 소유하는 media-understanding provider ID입니다.             |
| `imageGenerationProviders`       | `string[]` | 이 plugin이 소유하는 image-generation provider ID입니다.                |
| `videoGenerationProviders`       | `string[]` | 이 plugin이 소유하는 video-generation provider ID입니다.                |
| `webFetchProviders`              | `string[]` | 이 plugin이 소유하는 web-fetch provider ID입니다.                       |
| `webSearchProviders`             | `string[]` | 이 plugin이 소유하는 web-search provider ID입니다.                      |
| `tools`                          | `string[]` | 번들 계약 검사에서 이 plugin이 소유하는 agent tool 이름입니다. |

## channelConfigs 참조

채널 plugin이 런타임 로드 전에 가벼운 config 메타데이터가 필요할 때
`channelConfigs`를 사용하세요.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "Homeserver URL",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Matrix homeserver connection",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

각 채널 항목에는 다음이 포함될 수 있습니다.

| Field         | Type                     | 의미                                                                             |
| ------------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | `channels.<id>`용 JSON Schema입니다. 선언된 각 채널 config 항목에 필요합니다.         |
| `uiHints`     | `Record<string, object>` | 해당 채널 config 섹션용 선택적 UI 라벨/placeholder/민감도 힌트입니다.          |
| `label`       | `string`                 | 런타임 메타데이터가 준비되지 않았을 때 picker 및 inspect 표면에 병합되는 채널 라벨입니다. |
| `description` | `string`                 | inspect 및 카탈로그 표면용 짧은 채널 설명입니다.                               |
| `preferOver`  | `string[]`               | 선택 표면에서 이 채널이 우선해야 하는 레거시 또는 낮은 우선순위 plugin ID입니다.    |

## modelSupport 참조

OpenClaw가 plugin 런타임 로드 전에 `gpt-5.4` 또는 `claude-sonnet-4.6` 같은
shorthand model ID로부터 provider plugin을 추론해야 한다면
`modelSupport`를 사용하세요.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw는 다음 우선순위를 적용합니다.

- 명시적 `provider/model` ref는 소유 `providers` manifest 메타데이터를 사용합니다
- `modelPatterns`가 `modelPrefixes`보다 우선합니다
- 하나의 비번들 plugin과 하나의 번들 plugin이 모두 일치하면 비번들
  plugin이 우선합니다
- 남은 모호성은 사용자 또는 config가 provider를 지정할 때까지 무시됩니다

필드:

| Field           | Type       | 의미                                                                   |
| --------------- | ---------- | ------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | shorthand model ID에 대해 `startsWith`로 일치시키는 접두사입니다.                 |
| `modelPatterns` | `string[]` | profile 접미사를 제거한 후 shorthand model ID에 대해 일치시키는 regex 소스입니다. |

레거시 최상위 capability 키는 더 이상 권장되지 않습니다. `openclaw doctor --fix`를 사용해
`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders`, `webSearchProviders`를 `contracts` 아래로 이동하세요. 일반
manifest 로딩은 더 이상 이러한 최상위 필드를 capability
ownership으로 취급하지 않습니다.

## Manifest와 package.json의 차이

두 파일은 서로 다른 역할을 수행합니다.

| File                   | 용도                                                                                                                       |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | plugin 코드가 실행되기 전에 존재해야 하는 discovery, config 검증, auth-choice 메타데이터, UI 힌트                         |
| `package.json`         | npm 메타데이터, 종속성 설치, 그리고 entrypoint, 설치 게이팅, setup 또는 카탈로그 메타데이터에 사용되는 `openclaw` 블록 |

어떤 메타데이터를 어디에 둬야 할지 확실하지 않다면 다음 규칙을 사용하세요.

- OpenClaw가 plugin 코드를 로드하기 전에 알아야 한다면 `openclaw.plugin.json`에 두세요
- 패키징, 엔트리 파일 또는 npm 설치 동작에 관한 것이라면 `package.json`에 두세요

### discovery에 영향을 주는 package.json 필드

일부 사전 런타임 plugin 메타데이터는 의도적으로 `openclaw.plugin.json`이 아니라
`package.json`의 `openclaw` 블록에 위치합니다.

중요한 예시:

| Field                                                             | 의미                                                                          |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | 네이티브 plugin entrypoint를 선언합니다.                                                    |
| `openclaw.setupEntry`                                             | onboarding 및 지연 채널 시작 시 사용하는 가벼운 setup 전용 entrypoint입니다. |
| `openclaw.channel`                                                | 라벨, 문서 경로, alias, 선택용 문구 같은 가벼운 채널 카탈로그 메타데이터입니다.   |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | 번들 및 외부 게시 plugin용 설치/업데이트 힌트입니다.                     |
| `openclaw.install.defaultChoice`                                  | 여러 설치 소스가 있을 때 선호되는 설치 경로입니다.                    |
| `openclaw.install.minHostVersion`                                 | `>=2026.3.22` 같은 semver 하한을 사용하는 최소 지원 OpenClaw 호스트 버전입니다.      |
| `openclaw.install.allowInvalidConfigRecovery`                     | config가 유효하지 않을 때 제한적인 번들 plugin 재설치 복구 경로를 허용합니다.         |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | 시작 중 전체 채널 plugin 이전에 setup 전용 채널 표면을 로드하도록 합니다.   |

`openclaw.install.minHostVersion`은 설치와 manifest
레지스트리 로딩 중 강제됩니다. 유효하지 않은 값은 거부되며, 더 새롭지만 유효한 값은
오래된 호스트에서 plugin을 건너뜁니다.

`openclaw.install.allowInvalidConfigRecovery`는 의도적으로 제한적입니다. 이것이
임의의 잘못된 config를 설치 가능하게 만들지는 않습니다. 현재는 누락된 번들 plugin 경로 또는 같은
번들 plugin에 대한 오래된 `channels.<id>` 항목 같은 특정한 오래된 번들 plugin 업그레이드 실패로부터만 설치
흐름이 복구되도록 허용합니다. 관련 없는 config 오류는 여전히 설치를 차단하고
운영자에게 `openclaw doctor --fix`를 안내합니다.

## JSON Schema 요구 사항

- **모든 plugin은 JSON Schema를 포함해야 하며**, config를 받지 않더라도 예외는 없습니다.
- 빈 스키마도 허용됩니다(예: `{ "type": "object", "additionalProperties": false }`).
- 스키마는 런타임이 아니라 config 읽기/쓰기 시점에 검증됩니다.

## 검증 동작

- plugin manifest에서 채널 ID를 선언하지 않은 한, 알 수 없는 `channels.*` 키는 **오류**입니다.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny`, `plugins.slots.*`는
  반드시 **발견 가능한** plugin ID를 참조해야 합니다. 알 수 없는 ID는 **오류**입니다.
- plugin이 설치되어 있지만 manifest 또는 schema가 깨졌거나 누락된 경우,
  검증은 실패하고 Doctor가 plugin 오류를 보고합니다.
- plugin config가 존재하지만 plugin이 **비활성화**된 경우, config는 유지되며
  Doctor + 로그에 **경고**가 표시됩니다.

전체 `plugins.*` 스키마는 [Configuration reference](/gateway/configuration)를 참조하세요.

## 참고

- manifest는 로컬 파일시스템 로드를 포함한 **네이티브 OpenClaw plugins에 필수**입니다.
- 런타임은 여전히 plugin 모듈을 별도로 로드합니다. manifest는
  discovery + validation 전용입니다.
- 네이티브 manifest는 JSON5로 파싱되므로 주석, 후행 쉼표,
  따옴표 없는 키도 최종 값이 여전히 객체인 한 허용됩니다.
- manifest 로더는 문서화된 manifest 필드만 읽습니다. 여기에
  사용자 지정 최상위 키를 추가하지 마세요.
- `providerAuthEnvVars`는 auth probe, env-marker
  검증 및 이와 유사한 provider-auth 표면을 위해 plugin
  런타임을 부팅하지 않고 env 이름만 검사해야 할 때 사용하는 가벼운 메타데이터 경로입니다.
- `providerAuthChoices`는 auth-choice picker,
  `--auth-choice` 해석, preferred-provider 매핑, 그리고 provider 런타임이 로드되기 전의 단순 onboarding
  CLI flag 등록을 위한 가벼운 메타데이터 경로입니다. provider 코드가 필요한 런타임 wizard
  메타데이터는
  [Provider runtime hooks](/plugins/architecture#provider-runtime-hooks)를 참조하세요.
- 배타적 plugin 종류는 `plugins.slots.*`를 통해 선택됩니다.
  - `kind: "memory"`는 `plugins.slots.memory`로 선택됩니다.
  - `kind: "context-engine"`는 `plugins.slots.contextEngine`으로 선택됩니다
    (기본값: 내장 `legacy`).
- plugin에 필요 없으면 `channels`, `providers`, `cliBackends`, `skills`는 생략할 수 있습니다.
- plugin이 네이티브 모듈에 의존한다면 빌드 단계와
  패키지 관리자 allowlist 요구 사항(예: pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`)을 문서화하세요.

## 관련

- [Building Plugins](/plugins/building-plugins) — plugin 시작하기
- [Plugin Architecture](/plugins/architecture) — 내부 아키텍처
- [SDK Overview](/plugins/sdk-overview) — Plugin SDK 참조
