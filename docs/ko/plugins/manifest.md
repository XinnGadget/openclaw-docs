---
read_when:
    - OpenClaw 플러그인을 빌드하고 있습니다
    - 플러그인 구성 스키마를 제공하거나 플러그인 유효성 검사 오류를 디버그해야 합니다
summary: 플러그인 매니페스트 + JSON 스키마 요구사항(엄격한 구성 유효성 검사)
title: 플러그인 매니페스트
x-i18n:
    generated_at: "2026-04-11T15:15:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 42d454b560a8f6bf714c5d782f34216be1216d83d0a319d08d7349332c91a9e4
    source_path: plugins/manifest.md
    workflow: 15
---

# 플러그인 매니페스트 (`openclaw.plugin.json`)

이 페이지는 **네이티브 OpenClaw 플러그인 매니페스트**만을 다룹니다.

호환 가능한 번들 레이아웃은 [플러그인 번들](/ko/plugins/bundles)을 참고하세요.

호환 번들 형식은 서로 다른 매니페스트 파일을 사용합니다.

- Codex 번들: `.codex-plugin/plugin.json`
- Claude 번들: `.claude-plugin/plugin.json` 또는 매니페스트가 없는 기본 Claude 컴포넌트
  레이아웃
- Cursor 번들: `.cursor-plugin/plugin.json`

OpenClaw는 이러한 번들 레이아웃도 자동 감지하지만, 여기에서 설명하는 `openclaw.plugin.json` 스키마를 기준으로 유효성 검사를 하지는 않습니다.

호환 번들의 경우, OpenClaw는 현재 레이아웃이 OpenClaw 런타임 기대사항과 일치할 때 번들 메타데이터와 선언된 Skills 루트, Claude 명령 루트, Claude 번들 `settings.json` 기본값, Claude 번들 LSP 기본값, 지원되는 hook pack을 읽습니다.

모든 네이티브 OpenClaw 플러그인은 **반드시** **플러그인 루트**에 `openclaw.plugin.json` 파일을 포함해야 합니다. OpenClaw는 이 매니페스트를 사용해 **플러그인 코드를 실행하지 않고도** 구성을 검증합니다. 매니페스트가 없거나 유효하지 않으면 플러그인 오류로 처리되며 구성 유효성 검사가 차단됩니다.

전체 플러그인 시스템 가이드는 [플러그인](/ko/tools/plugin)을 참고하세요.
네이티브 capability 모델과 현재 외부 호환성 가이드는
[Capability model](/ko/plugins/architecture#public-capability-model)을 참고하세요.

## 이 파일의 역할

`openclaw.plugin.json`은 OpenClaw가 플러그인 코드를 로드하기 전에 읽는 메타데이터입니다.

다음 용도로 사용하세요.

- 플러그인 식별 정보
- 구성 유효성 검사
- 플러그인 런타임을 부팅하지 않고도 사용할 수 있어야 하는 인증 및 온보딩 메타데이터
- 런타임이 로드되기 전에 컨트롤 플레인 표면에서 확인할 수 있는 가벼운 활성화 힌트
- 런타임이 로드되기 전에 설정/온보딩 표면에서 확인할 수 있는 가벼운 설정 설명자
- 플러그인 런타임이 로드되기 전에 확인되어야 하는 별칭 및 자동 활성화 메타데이터
- 플러그인 런타임이 로드되기 전에 플러그인을 자동 활성화해야 하는 축약형 모델 패밀리 소유 메타데이터
- 번들 호환 wiring 및 계약 범위 검증에 사용되는 정적 capability 소유 스냅샷
- 런타임을 로드하지 않고 카탈로그 및 유효성 검사 표면에 병합되어야 하는 채널별 구성 메타데이터
- 구성 UI 힌트

다음 용도로는 사용하지 마세요.

- 런타임 동작 등록
- 코드 진입점 선언
- npm 설치 메타데이터

이 항목들은 플러그인 코드와 `package.json`에 속합니다.

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

## 상세 예시

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
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "OpenRouter API key",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API key",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API key",
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

| 필드                                | 필수 여부 | 유형                             | 의미                                                                                                                                                                                                         |
| ----------------------------------- | --------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | 예        | `string`                         | 정식 플러그인 id입니다. 이 id는 `plugins.entries.<id>`에서 사용됩니다.                                                                                                                                       |
| `configSchema`                      | 예        | `object`                         | 이 플러그인 구성에 대한 인라인 JSON 스키마입니다.                                                                                                                                                            |
| `enabledByDefault`                  | 아니요    | `true`                           | 번들 플러그인을 기본적으로 활성화된 상태로 표시합니다. 기본적으로 비활성화된 상태로 두려면 이 값을 생략하거나 `true`가 아닌 값을 설정하세요.                                                               |
| `legacyPluginIds`                   | 아니요    | `string[]`                       | 이 정식 플러그인 id로 정규화되는 레거시 id입니다.                                                                                                                                                            |
| `autoEnableWhenConfiguredProviders` | 아니요    | `string[]`                       | 인증, 구성 또는 모델 참조에서 이 provider id들이 언급되면 이 플러그인을 자동 활성화해야 함을 나타냅니다.                                                                                                   |
| `kind`                              | 아니요    | `"memory"` \| `"context-engine"` | `plugins.slots.*`에서 사용되는 배타적 플러그인 종류를 선언합니다.                                                                                                                                            |
| `channels`                          | 아니요    | `string[]`                       | 이 플러그인이 소유하는 채널 id입니다. 검색 및 구성 유효성 검사에 사용됩니다.                                                                                                                                 |
| `providers`                         | 아니요    | `string[]`                       | 이 플러그인이 소유하는 provider id입니다.                                                                                                                                                                    |
| `modelSupport`                      | 아니요    | `object`                         | 런타임 전에 플러그인을 자동 로드하는 데 사용되는, 매니페스트가 소유하는 축약형 모델 패밀리 메타데이터입니다.                                                                                                |
| `cliBackends`                       | 아니요    | `string[]`                       | 이 플러그인이 소유하는 CLI 추론 백엔드 id입니다. 명시적 구성 참조로부터 시작 시 자동 활성화하는 데 사용됩니다.                                                                                              |
| `commandAliases`                    | 아니요    | `object[]`                       | 런타임이 로드되기 전에 플러그인 인식 구성 및 CLI 진단을 생성해야 하는, 이 플러그인이 소유하는 명령 이름입니다.                                                                                              |
| `providerAuthEnvVars`               | 아니요    | `Record<string, string[]>`       | 플러그인 코드를 로드하지 않고도 OpenClaw가 확인할 수 있는 가벼운 provider 인증 환경 변수 메타데이터입니다.                                                                                                  |
| `providerAuthAliases`               | 아니요    | `Record<string, string>`         | 인증 조회를 위해 다른 provider id를 재사용해야 하는 provider id입니다. 예를 들어 기본 provider API 키 및 인증 프로필을 공유하는 코딩 provider가 이에 해당합니다.                                          |
| `channelEnvVars`                    | 아니요    | `Record<string, string[]>`       | 플러그인 코드를 로드하지 않고도 OpenClaw가 확인할 수 있는 가벼운 채널 환경 변수 메타데이터입니다. 일반적인 시작/구성 도우미가 볼 수 있어야 하는 환경 변수 기반 채널 설정 또는 인증 표면에 사용하세요.      |
| `providerAuthChoices`               | 아니요    | `object[]`                       | 온보딩 선택기, 선호 provider 확인, 간단한 CLI 플래그 연결에 사용하는 가벼운 인증 선택 메타데이터입니다.                                                                                                     |
| `activation`                        | 아니요    | `object`                         | provider, 명령, 채널, route, capability 트리거 로드를 위한 가벼운 활성화 힌트입니다. 메타데이터 전용이며, 실제 동작은 여전히 플러그인 런타임이 소유합니다.                                                 |
| `setup`                             | 아니요    | `object`                         | 검색 및 설정 표면이 플러그인 런타임을 로드하지 않고도 확인할 수 있는 가벼운 설정/온보딩 설명자입니다.                                                                                                       |
| `contracts`                         | 아니요    | `object`                         | speech, 실시간 전사, 실시간 음성, media-understanding, image-generation, music-generation, video-generation, web-fetch, 웹 검색, 도구 소유권을 위한 정적 번들 capability 스냅샷입니다.                     |
| `channelConfigs`                    | 아니요    | `Record<string, object>`         | 런타임이 로드되기 전에 검색 및 유효성 검사 표면에 병합되는, 매니페스트가 소유하는 채널 구성 메타데이터입니다.                                                                                               |
| `skills`                            | 아니요    | `string[]`                       | 플러그인 루트를 기준으로 로드할 Skills 디렉터리입니다.                                                                                                                                                      |
| `name`                              | 아니요    | `string`                         | 사람이 읽을 수 있는 플러그인 이름입니다.                                                                                                                                                                     |
| `description`                       | 아니요    | `string`                         | 플러그인 표면에 표시되는 짧은 요약입니다.                                                                                                                                                                    |
| `version`                           | 아니요    | `string`                         | 정보 제공용 플러그인 버전입니다.                                                                                                                                                                             |
| `uiHints`                           | 아니요    | `Record<string, object>`         | 구성 필드에 대한 UI 레이블, 플레이스홀더, 민감도 힌트입니다.                                                                                                                                                |

## `providerAuthChoices` 참조

각 `providerAuthChoices` 항목은 하나의 온보딩 또는 인증 선택 항목을 설명합니다.
OpenClaw는 provider 런타임이 로드되기 전에 이를 읽습니다.

| 필드                  | 필수 여부 | 유형                                            | 의미                                                                                                   |
| --------------------- | --------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `provider`            | 예        | `string`                                        | 이 선택 항목이 속한 provider id입니다.                                                                 |
| `method`              | 예        | `string`                                        | 디스패치할 인증 방식 id입니다.                                                                         |
| `choiceId`            | 예        | `string`                                        | 온보딩 및 CLI 흐름에서 사용하는 안정적인 인증 선택 id입니다.                                          |
| `choiceLabel`         | 아니요    | `string`                                        | 사용자 대상 레이블입니다. 생략하면 OpenClaw는 `choiceId`를 대체값으로 사용합니다.                     |
| `choiceHint`          | 아니요    | `string`                                        | 선택기용 짧은 도움말 텍스트입니다.                                                                     |
| `assistantPriority`   | 아니요    | `number`                                        | assistant 주도 대화형 선택기에서 값이 낮을수록 먼저 정렬됩니다.                                       |
| `assistantVisibility` | 아니요    | `"visible"` \| `"manual-only"`                  | assistant 선택기에서는 이 선택 항목을 숨기되, 수동 CLI 선택은 계속 허용합니다.                        |
| `deprecatedChoiceIds` | 아니요    | `string[]`                                      | 사용자를 이 대체 선택 항목으로 리디렉션해야 하는 레거시 선택 id입니다.                                |
| `groupId`             | 아니요    | `string`                                        | 관련 선택 항목을 그룹화하기 위한 선택적 그룹 id입니다.                                                 |
| `groupLabel`          | 아니요    | `string`                                        | 해당 그룹의 사용자 대상 레이블입니다.                                                                  |
| `groupHint`           | 아니요    | `string`                                        | 그룹용 짧은 도움말 텍스트입니다.                                                                       |
| `optionKey`           | 아니요    | `string`                                        | 단일 플래그 기반의 간단한 인증 흐름에서 사용하는 내부 옵션 키입니다.                                  |
| `cliFlag`             | 아니요    | `string`                                        | `--openrouter-api-key`와 같은 CLI 플래그 이름입니다.                                                   |
| `cliOption`           | 아니요    | `string`                                        | `--openrouter-api-key <key>`와 같은 전체 CLI 옵션 형태입니다.                                          |
| `cliDescription`      | 아니요    | `string`                                        | CLI 도움말에 사용되는 설명입니다.                                                                      |
| `onboardingScopes`    | 아니요    | `Array<"text-inference" \| "image-generation">` | 이 선택 항목이 표시되어야 하는 온보딩 표면입니다. 생략하면 기본값은 `["text-inference"]`입니다.       |

## `commandAliases` 참조

사용자가 `plugins.allow`에 잘못 넣거나 루트 CLI 명령으로 실행하려고 할 수 있는 런타임 명령 이름을 플러그인이 소유하는 경우 `commandAliases`를 사용하세요. OpenClaw는 플러그인 런타임 코드를 import하지 않고 이 메타데이터를 진단에 사용합니다.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| 필드         | 필수 여부 | 유형              | 의미                                                                     |
| ------------ | --------- | ----------------- | ------------------------------------------------------------------------ |
| `name`       | 예        | `string`          | 이 플러그인에 속한 명령 이름입니다.                                      |
| `kind`       | 아니요    | `"runtime-slash"` | 이 별칭이 루트 CLI 명령이 아니라 채팅 슬래시 명령임을 나타냅니다.        |
| `cliCommand` | 아니요    | `string`          | 존재하는 경우, CLI 작업에 대해 제안할 관련 루트 CLI 명령입니다.          |

## `activation` 참조

플러그인이 어떤 컨트롤 플레인 이벤트에 의해 나중에 활성화되어야 하는지를 가볍게 선언할 수 있을 때 `activation`을 사용하세요.

이 블록은 메타데이터 전용입니다. 런타임 동작을 등록하지 않으며, `register(...)`, `setupEntry` 또는 기타 런타임/플러그인 진입점을 대체하지도 않습니다.

```json
{
  "activation": {
    "onProviders": ["openai"],
    "onCommands": ["models"],
    "onChannels": ["web"],
    "onRoutes": ["gateway-webhook"],
    "onCapabilities": ["provider", "tool"]
  }
}
```

| 필드             | 필수 여부 | 유형                                                 | 의미                                                              |
| ---------------- | --------- | ---------------------------------------------------- | ----------------------------------------------------------------- |
| `onProviders`    | 아니요    | `string[]`                                           | 요청되었을 때 이 플러그인을 활성화해야 하는 provider id입니다.    |
| `onCommands`     | 아니요    | `string[]`                                           | 이 플러그인을 활성화해야 하는 명령 id입니다.                      |
| `onChannels`     | 아니요    | `string[]`                                           | 이 플러그인을 활성화해야 하는 채널 id입니다.                      |
| `onRoutes`       | 아니요    | `string[]`                                           | 이 플러그인을 활성화해야 하는 route 종류입니다.                   |
| `onCapabilities` | 아니요    | `Array<"provider" \| "channel" \| "tool" \| "hook">` | 컨트롤 플레인 활성화 계획에 사용되는 광범위한 capability 힌트입니다. |

## `setup` 참조

설정 및 온보딩 표면에서 런타임이 로드되기 전에 플러그인이 소유한 가벼운 메타데이터가 필요할 때 `setup`을 사용하세요.

```json
{
  "setup": {
    "providers": [
      {
        "id": "openai",
        "authMethods": ["api-key"],
        "envVars": ["OPENAI_API_KEY"]
      }
    ],
    "cliBackends": ["openai-cli"],
    "configMigrations": ["legacy-openai-auth"],
    "requiresRuntime": false
  }
}
```

최상위 `cliBackends`는 계속 유효하며 계속해서 CLI 추론 백엔드를 설명합니다. `setup.cliBackends`는 메타데이터 전용으로 유지되어야 하는 컨트롤 플레인/설정 흐름을 위한 설정 전용 설명자 표면입니다.

### `setup.providers` 참조

| 필드          | 필수 여부 | 유형       | 의미                                                                                 |
| ------------- | --------- | ---------- | ------------------------------------------------------------------------------------ |
| `id`          | 예        | `string`   | 설정 또는 온보딩 중에 노출되는 provider id입니다.                                    |
| `authMethods` | 아니요    | `string[]` | 전체 런타임을 로드하지 않고도 이 provider가 지원하는 설정/인증 방식 id입니다.        |
| `envVars`     | 아니요    | `string[]` | 플러그인 런타임이 로드되기 전에 일반 설정/상태 표면에서 확인할 수 있는 환경 변수입니다. |

### `setup` 필드

| 필드               | 필수 여부 | 유형       | 의미                                                                        |
| ------------------ | --------- | ---------- | --------------------------------------------------------------------------- |
| `providers`        | 아니요    | `object[]` | 설정 및 온보딩 중에 노출되는 provider 설정 설명자입니다.                    |
| `cliBackends`      | 아니요    | `string[]` | 전체 런타임 활성화 없이 사용할 수 있는 설정 시점 백엔드 id입니다.           |
| `configMigrations` | 아니요    | `string[]` | 이 플러그인의 설정 표면이 소유하는 구성 마이그레이션 id입니다.              |
| `requiresRuntime`  | 아니요    | `boolean`  | 설명자 조회 후에도 설정에 플러그인 런타임 실행이 필요한지 여부입니다.       |

## `uiHints` 참조

`uiHints`는 구성 필드 이름을 작은 렌더링 힌트에 매핑한 맵입니다.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "help": "Used for OpenRouter requests",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

각 필드 힌트에는 다음이 포함될 수 있습니다.

| 필드          | 유형       | 의미                                    |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | 사용자 대상 필드 레이블입니다.          |
| `help`        | `string`   | 짧은 도움말 텍스트입니다.               |
| `tags`        | `string[]` | 선택적 UI 태그입니다.                   |
| `advanced`    | `boolean`  | 이 필드를 고급 항목으로 표시합니다.     |
| `sensitive`   | `boolean`  | 이 필드를 비밀값 또는 민감 정보로 표시합니다. |
| `placeholder` | `string`   | 폼 입력용 플레이스홀더 텍스트입니다.    |

## `contracts` 참조

OpenClaw가 플러그인 런타임을 import하지 않고 읽을 수 있는 정적 capability 소유 메타데이터에만 `contracts`를 사용하세요.

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

| 필드                             | 유형       | 의미                                                            |
| -------------------------------- | ---------- | --------------------------------------------------------------- |
| `speechProviders`                | `string[]` | 이 플러그인이 소유하는 speech provider id입니다.                |
| `realtimeTranscriptionProviders` | `string[]` | 이 플러그인이 소유하는 실시간 전사 provider id입니다.           |
| `realtimeVoiceProviders`         | `string[]` | 이 플러그인이 소유하는 실시간 음성 provider id입니다.           |
| `mediaUnderstandingProviders`    | `string[]` | 이 플러그인이 소유하는 media-understanding provider id입니다.   |
| `imageGenerationProviders`       | `string[]` | 이 플러그인이 소유하는 image-generation provider id입니다.      |
| `videoGenerationProviders`       | `string[]` | 이 플러그인이 소유하는 video-generation provider id입니다.      |
| `webFetchProviders`              | `string[]` | 이 플러그인이 소유하는 web-fetch provider id입니다.             |
| `webSearchProviders`             | `string[]` | 이 플러그인이 소유하는 웹 검색 provider id입니다.               |
| `tools`                          | `string[]` | 번들 계약 검사에서 이 플러그인이 소유하는 에이전트 도구 이름입니다. |

## `channelConfigs` 참조

채널 플러그인이 런타임이 로드되기 전에 가벼운 구성 메타데이터를 필요로 할 때 `channelConfigs`를 사용하세요.

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

| 필드          | 유형                     | 의미                                                                                  |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | `channels.<id>`에 대한 JSON 스키마입니다. 선언된 각 채널 구성 항목에 필수입니다.      |
| `uiHints`     | `Record<string, object>` | 해당 채널 구성 섹션에 대한 선택적 UI 레이블/플레이스홀더/민감도 힌트입니다.           |
| `label`       | `string`                 | 런타임 메타데이터가 준비되지 않았을 때 선택기 및 검사 표면에 병합되는 채널 레이블입니다. |
| `description` | `string`                 | 검사 및 카탈로그 표면용 짧은 채널 설명입니다.                                         |
| `preferOver`  | `string[]`               | 선택 표면에서 이 채널이 우선해야 하는 레거시 또는 우선순위가 낮은 플러그인 id입니다.   |

## `modelSupport` 참조

플러그인 런타임이 로드되기 전에 OpenClaw가 `gpt-5.4` 또는 `claude-sonnet-4.6` 같은 축약형 모델 id로부터 provider 플러그인을 추론해야 할 때 `modelSupport`를 사용하세요.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw는 다음 우선순위를 적용합니다.

- 명시적 `provider/model` 참조는 소유 `providers` 매니페스트 메타데이터를 사용합니다
- `modelPatterns`가 `modelPrefixes`보다 우선합니다
- 번들되지 않은 플러그인과 번들 플러그인이 둘 다 일치하면 번들되지 않은 플러그인이 우선합니다
- 나머지 모호성은 사용자 또는 구성에서 provider를 지정할 때까지 무시됩니다

필드:

| 필드            | 유형       | 의미                                                                           |
| --------------- | ---------- | ------------------------------------------------------------------------------ |
| `modelPrefixes` | `string[]` | 축약형 모델 id에 대해 `startsWith`로 일치시키는 접두사입니다.                  |
| `modelPatterns` | `string[]` | 프로필 접미사 제거 후 축약형 모델 id에 대해 일치시키는 정규식 소스입니다.      |

레거시 최상위 capability 키는 더 이상 권장되지 않습니다. `openclaw doctor --fix`를 사용해 `speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders`를 `contracts` 아래로 이동하세요. 일반 매니페스트 로딩은 더 이상 이러한 최상위 필드를 capability 소유권으로 처리하지 않습니다.

## 매니페스트와 package.json 비교

두 파일은 서로 다른 역할을 합니다.

| 파일                   | 용도                                                                                                                                   |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | 플러그인 코드가 실행되기 전에 반드시 존재해야 하는 검색, 구성 유효성 검사, 인증 선택 메타데이터, UI 힌트                              |
| `package.json`         | npm 메타데이터, 의존성 설치, 진입점, 설치 게이트, 설정 또는 카탈로그 메타데이터에 사용되는 `openclaw` 블록                           |

어떤 메타데이터를 어디에 넣어야 할지 확실하지 않다면 다음 규칙을 따르세요.

- OpenClaw가 플러그인 코드를 로드하기 전에 알아야 한다면 `openclaw.plugin.json`에 넣으세요
- 패키징, 진입 파일, npm 설치 동작에 관한 것이라면 `package.json`에 넣으세요

### 검색에 영향을 주는 `package.json` 필드

일부 사전 런타임 플러그인 메타데이터는 의도적으로 `openclaw.plugin.json`이 아니라 `package.json`의 `openclaw` 블록에 있습니다.

중요한 예시는 다음과 같습니다.

| 필드                                                              | 의미                                                                                                                                         |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | 네이티브 플러그인 진입점을 선언합니다.                                                                                                       |
| `openclaw.setupEntry`                                             | 온보딩 및 지연된 채널 시작 중 사용되는 경량 설정 전용 진입점입니다.                                                                          |
| `openclaw.channel`                                                | 레이블, 문서 경로, 별칭, 선택용 문구 같은 가벼운 채널 카탈로그 메타데이터입니다.                                                            |
| `openclaw.channel.configuredState`                                | 전체 채널 런타임을 로드하지 않고도 "환경 변수 전용 설정이 이미 존재하는가?"에 답할 수 있는 가벼운 configured-state 검사기 메타데이터입니다. |
| `openclaw.channel.persistedAuthState`                             | 전체 채널 런타임을 로드하지 않고도 "이미 로그인된 항목이 있는가?"에 답할 수 있는 가벼운 persisted-auth 검사기 메타데이터입니다.            |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | 번들 플러그인 및 외부 배포 플러그인을 위한 설치/업데이트 힌트입니다.                                                                        |
| `openclaw.install.defaultChoice`                                  | 여러 설치 소스를 사용할 수 있을 때 선호되는 설치 경로입니다.                                                                                |
| `openclaw.install.minHostVersion`                                 | `>=2026.3.22` 같은 semver 하한을 사용하는, 지원되는 최소 OpenClaw 호스트 버전입니다.                                                        |
| `openclaw.install.allowInvalidConfigRecovery`                     | 구성이 유효하지 않을 때 제한된 범위의 번들 플러그인 재설치 복구 경로를 허용합니다.                                                          |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | 시작 중 전체 채널 플러그인보다 먼저 설정 전용 채널 표면을 로드할 수 있게 합니다.                                                            |

`openclaw.install.minHostVersion`은 설치 및 매니페스트 레지스트리 로딩 중에 적용됩니다. 유효하지 않은 값은 거부되며, 더 새롭지만 유효한 값은 오래된 호스트에서 해당 플러그인을 건너뜁니다.

`openclaw.install.allowInvalidConfigRecovery`는 의도적으로 범위가 좁습니다. 임의로 깨진 구성을 설치 가능하게 만들지는 않습니다. 현재는 번들 플러그인 경로 누락 또는 같은 번들 플러그인에 대한 오래된 `channels.<id>` 항목처럼, 특정 오래된 번들 플러그인 업그레이드 실패에서 설치 흐름이 복구되도록 허용하는 용도로만 사용됩니다. 관련 없는 구성 오류는 여전히 설치를 차단하고 운영자를 `openclaw doctor --fix`로 안내합니다.

`openclaw.channel.persistedAuthState`는 작은 검사기 모듈을 위한 패키지 메타데이터입니다.

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

설정, doctor 또는 configured-state 흐름이 전체 채널 플러그인이 로드되기 전에 가벼운 예/아니오 인증 확인을 필요로 할 때 사용하세요. 대상 export는 저장된 상태만 읽는 작은 함수여야 하며, 전체 채널 런타임 barrel을 통해 연결하지 마세요.

`openclaw.channel.configuredState`도 가벼운 환경 변수 전용 configured 확인을 위해 동일한 형태를 따릅니다.

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

채널이 환경 변수 또는 기타 작은 비런타임 입력만으로 configured-state에 답할 수 있을 때 사용하세요. 확인에 전체 구성 해석 또는 실제 채널 런타임이 필요하다면, 그 로직은 대신 플러그인 `config.hasConfiguredState` hook에 두세요.

## JSON 스키마 요구사항

- **모든 플러그인은 반드시 JSON 스키마를 포함해야 하며**, 구성을 전혀 받지 않는 경우도 예외가 아닙니다.
- 빈 스키마도 허용됩니다(예: `{ "type": "object", "additionalProperties": false }`).
- 스키마는 런타임이 아니라 구성 읽기/쓰기 시점에 유효성 검사됩니다.

## 유효성 검사 동작

- 알 수 없는 `channels.*` 키는 **오류**입니다. 단, 해당 채널 id가 플러그인 매니페스트에 선언되어 있는 경우는 예외입니다.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny`, `plugins.slots.*`는 **검색 가능한** 플러그인 id를 참조해야 합니다. 알 수 없는 id는 **오류**입니다.
- 플러그인이 설치되어 있지만 매니페스트 또는 스키마가 깨졌거나 누락된 경우, 유효성 검사가 실패하고 Doctor가 플러그인 오류를 보고합니다.
- 플러그인 구성이 존재하지만 플러그인이 **비활성화**되어 있으면, 구성은 유지되며 Doctor + 로그에 **경고**가 표시됩니다.

전체 `plugins.*` 스키마는 [구성 참조](/ko/gateway/configuration)를 참고하세요.

## 참고

- 매니페스트는 로컬 파일 시스템 로드를 포함해 **네이티브 OpenClaw 플러그인에 필수**입니다.
- 런타임은 여전히 플러그인 모듈을 별도로 로드합니다. 매니페스트는 검색 + 유효성 검사 전용입니다.
- 네이티브 매니페스트는 JSON5로 파싱되므로, 최종 값이 여전히 객체이기만 하면 주석, 후행 쉼표, 따옴표 없는 키를 허용합니다.
- 매니페스트 로더는 문서화된 매니페스트 필드만 읽습니다. 여기에 사용자 정의 최상위 키를 추가하지 마세요.
- `providerAuthEnvVars`는 인증 확인, 환경 변수 마커 유효성 검사 및 이와 유사하게 환경 변수 이름을 확인하기 위해 플러그인 런타임을 부팅하면 안 되는 provider 인증 표면을 위한 가벼운 메타데이터 경로입니다.
- `providerAuthAliases`는 provider 변형이 다른 provider의 인증 환경 변수, 인증 프로필, 구성 기반 인증, API 키 온보딩 선택 항목을 재사용하도록 해 주며, 이 관계를 코어에 하드코딩할 필요가 없습니다.
- `channelEnvVars`는 셸 환경 변수 대체, 설정 프롬프트 및 이와 유사하게 환경 변수 이름을 확인하기 위해 플러그인 런타임을 부팅하면 안 되는 채널 표면을 위한 가벼운 메타데이터 경로입니다.
- `providerAuthChoices`는 인증 선택 선택기, `--auth-choice` 확인, 선호 provider 매핑, provider 런타임이 로드되기 전의 간단한 온보딩 CLI 플래그 등록을 위한 가벼운 메타데이터 경로입니다. provider 코드가 필요한 런타임 wizard 메타데이터는 [Provider runtime hooks](/ko/plugins/architecture#provider-runtime-hooks)를 참고하세요.
- 배타적 플러그인 종류는 `plugins.slots.*`를 통해 선택됩니다.
  - `kind: "memory"`는 `plugins.slots.memory`로 선택됩니다.
  - `kind: "context-engine"`는 `plugins.slots.contextEngine`으로 선택됩니다
    (기본값: 내장 `legacy`).
- 플러그인에 필요하지 않다면 `channels`, `providers`, `cliBackends`, `skills`는 생략할 수 있습니다.
- 플러그인이 네이티브 모듈에 의존한다면, 빌드 단계와 패키지 관리자 allowlist 요구사항(예: pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`)을 문서화하세요.

## 관련 항목

- [플러그인 빌드](/ko/plugins/building-plugins) — 플러그인 시작하기
- [플러그인 아키텍처](/ko/plugins/architecture) — 내부 아키텍처
- [SDK 개요](/ko/plugins/sdk-overview) — Plugin SDK 참조
