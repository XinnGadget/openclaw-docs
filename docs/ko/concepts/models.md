---
read_when:
    - models CLI(models list/set/scan/aliases/fallbacks)를 추가하거나 수정하는 경우
    - 모델 폴백 동작이나 선택 UX를 변경하는 경우
    - 모델 스캔 프로브(tools/images)를 업데이트하는 경우
summary: 'Models CLI: 나열, 설정, 별칭, 폴백, 스캔, 상태'
title: Models CLI
x-i18n:
    generated_at: "2026-04-05T12:40:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: e08f7e50da263895dae2bd2b8dc327972ea322615f8d1918ddbd26bb0fb24840
    source_path: concepts/models.md
    workflow: 15
---

# Models CLI

인증 프로필 순환, 쿨다운, 그리고 이것이 폴백과 어떻게 상호작용하는지는 [/concepts/model-failover](/concepts/model-failover)를 참조하세요.
간단한 provider 개요 및 예시는 [/concepts/model-providers](/concepts/model-providers)를 참조하세요.

## 모델 선택 방식

OpenClaw는 다음 순서로 모델을 선택합니다.

1. **기본(primary)** 모델 (`agents.defaults.model.primary` 또는 `agents.defaults.model`)
2. `agents.defaults.model.fallbacks`의 **폴백**(순서대로)
3. **Provider 인증 폴백**은 다음 모델로 이동하기 전에 provider 내부에서 발생

관련 항목:

- `agents.defaults.models`는 OpenClaw가 사용할 수 있는 모델의 허용 목록/카탈로그입니다(별칭 포함).
- `agents.defaults.imageModel`은 **기본 모델이 이미지를 받을 수 없을 때만** 사용됩니다.
- `agents.defaults.pdfModel`은 `pdf` 도구에서 사용됩니다. 생략하면 이 도구는 `agents.defaults.imageModel`, 그다음 해석된 세션/기본 모델로 폴백합니다.
- `agents.defaults.imageGenerationModel`은 공통 이미지 생성 기능에서 사용됩니다. 생략해도 `image_generate`는 여전히 인증이 연결된 provider 기본값을 추론할 수 있습니다. 먼저 현재 기본 provider를 시도한 다음, 나머지 등록된 이미지 생성 providers를 provider-id 순서로 시도합니다. 특정 provider/model을 설정하는 경우 해당 provider의 인증/API 키도 함께 구성하세요.
- `agents.defaults.videoGenerationModel`은 공통 비디오 생성 기능에서 사용됩니다. 이미지 생성과 달리 현재는 provider 기본값을 추론하지 않습니다. `qwen/wan2.6-t2v` 같은 명시적인 `provider/model`을 설정하고 해당 provider의 인증/API 키도 함께 구성하세요.
- 에이전트별 기본값은 `agents.list[].model`과 bindings를 통해 `agents.defaults.model`을 재정의할 수 있습니다([/concepts/multi-agent](/concepts/multi-agent) 참조).

## 빠른 모델 정책

- 사용할 수 있는 최신 세대의 가장 강력한 모델을 기본 모델로 설정하세요.
- 비용/지연 시간에 민감한 작업과 중요도가 낮은 채팅에는 폴백을 사용하세요.
- tools가 활성화된 에이전트나 신뢰할 수 없는 입력에는 오래되거나 약한 모델 계층을 피하세요.

## 온보딩(권장)

config를 직접 수정하고 싶지 않다면 온보딩을 실행하세요.

```bash
openclaw onboard
```

이 명령은 **OpenAI Code (Codex) 구독**(OAuth)과 **Anthropic**(API 키 또는 Claude CLI)을 포함한 일반적인 providers의 모델 + 인증을 설정할 수 있습니다.

## Config 키(개요)

- `agents.defaults.model.primary` 및 `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel.primary` 및 `agents.defaults.imageModel.fallbacks`
- `agents.defaults.pdfModel.primary` 및 `agents.defaults.pdfModel.fallbacks`
- `agents.defaults.imageGenerationModel.primary` 및 `agents.defaults.imageGenerationModel.fallbacks`
- `agents.defaults.videoGenerationModel.primary` 및 `agents.defaults.videoGenerationModel.fallbacks`
- `agents.defaults.models` (허용 목록 + 별칭 + provider params)
- `models.providers` (`models.json`에 기록되는 사용자 지정 providers)

모델 ref는 소문자로 정규화됩니다. `z.ai/*` 같은 provider 별칭은 `zai/*`로 정규화됩니다.

Provider 구성 예시(OpenCode 포함)는 [/providers/opencode](/providers/opencode)에 있습니다.

## "Model is not allowed"가 표시되고 응답이 멈추는 이유

`agents.defaults.models`가 설정되어 있으면 `/model` 및 세션 재정의에 대한 **허용 목록**이 됩니다. 사용자가 이 허용 목록에 없는 모델을 선택하면 OpenClaw는 다음을 반환합니다.

```
Model "provider/model" is not allowed. Use /model to list available models.
```

이것은 일반 응답이 생성되기 **이전**에 발생하므로, 메시지에 “응답하지 않은” 것처럼 느껴질 수 있습니다. 해결 방법은 다음 중 하나입니다.

- 모델을 `agents.defaults.models`에 추가
- 허용 목록 비우기(`agents.defaults.models` 제거)
- `/model list`에서 모델 선택

허용 목록 config 예시:

```json5
{
  agent: {
    model: { primary: "anthropic/claude-sonnet-4-6" },
    models: {
      "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
      "anthropic/claude-opus-4-6": { alias: "Opus" },
    },
  },
}
```

## 채팅에서 모델 전환(` /model`)

재시작하지 않고 현재 세션의 모델을 전환할 수 있습니다.

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model status
```

참고:

- `/model`(및 `/model list`)은 간결한 번호 기반 선택기입니다(모델 패밀리 + 사용 가능한 providers).
- Discord에서는 `/model`과 `/models`가 provider 및 모델 드롭다운과 Submit 단계가 있는 대화형 선택기를 엽니다.
- `/model <#>`는 해당 선택기에서 선택합니다.
- `/model`은 새 세션 선택을 즉시 저장합니다.
- 에이전트가 유휴 상태라면 다음 실행에서 즉시 새 모델을 사용합니다.
- 이미 실행이 활성 상태라면 OpenClaw는 실시간 전환을 보류 상태로 표시하고, 깔끔한 재시도 지점에서만 새 모델로 재시작합니다.
- tool 활동이나 응답 출력이 이미 시작된 경우, 보류 중인 전환은 이후 재시도 기회나 다음 사용자 턴까지 대기할 수 있습니다.
- `/model status`는 자세한 보기입니다(인증 후보, 그리고 구성된 경우 provider 엔드포인트 `baseUrl` + `api` 모드).
- 모델 ref는 **첫 번째** `/`를 기준으로 분리하여 파싱합니다. `/model <ref>`를 입력할 때는 `provider/model`을 사용하세요.
- 모델 ID 자체에 `/`가 포함되어 있는 경우(OpenRouter 스타일) provider 접두사를 반드시 포함해야 합니다(예: `/model openrouter/moonshotai/kimi-k2`).
- provider를 생략하면 OpenClaw는 다음 순서로 입력을 해석합니다.
  1. 별칭 일치
  2. 해당 정확한 접두사 없는 모델 ID에 대한 고유한 configured-provider 일치
  3. 더 이상 사용되지 않는, 구성된 기본 provider로의 폴백  
     해당 provider가 더 이상 구성된 기본 모델을 노출하지 않는다면, OpenClaw는 오래된 제거된-provider 기본값이 드러나는 것을 피하기 위해 첫 번째 구성된 provider/model로 대신 폴백합니다.

전체 명령 동작/config: [슬래시 명령](/tools/slash-commands).

## CLI 명령

```bash
openclaw models list
openclaw models status
openclaw models set <provider/model>
openclaw models set-image <provider/model>

openclaw models aliases list
openclaw models aliases add <alias> <provider/model>
openclaw models aliases remove <alias>

openclaw models fallbacks list
openclaw models fallbacks add <provider/model>
openclaw models fallbacks remove <provider/model>
openclaw models fallbacks clear

openclaw models image-fallbacks list
openclaw models image-fallbacks add <provider/model>
openclaw models image-fallbacks remove <provider/model>
openclaw models image-fallbacks clear
```

`openclaw models`(하위 명령 없음)는 `models status`의 바로가기입니다.

### `models list`

기본적으로 구성된 모델을 표시합니다. 유용한 플래그:

- `--all`: 전체 카탈로그
- `--local`: 로컬 providers만
- `--provider <name>`: provider로 필터링
- `--plain`: 한 줄에 하나의 모델
- `--json`: 기계 판독 가능한 출력

### `models status`

해석된 기본 모델, 폴백, 이미지 모델, 그리고 구성된 providers의 인증 개요를 표시합니다. 또한 인증 저장소에서 찾은 프로필의 OAuth 만료 상태도 표시합니다(기본적으로 24시간 이내에 경고). `--plain`은 해석된 기본 모델만 출력합니다.
OAuth 상태는 항상 표시되며(`--json` 출력에도 포함됨), 구성된 provider에 자격 증명이 없으면 `models status`는 **Missing auth** 섹션을 출력합니다.
JSON에는 `auth.oauth`(경고 창 + 프로필)와 `auth.providers`(provider별 유효 인증)가 포함됩니다.
자동화에는 `--check`를 사용하세요(누락/만료 시 종료 코드 `1`, 곧 만료 시 `2`).
실시간 인증 검사에는 `--probe`를 사용하세요. 프로브 행은 인증 프로필, env 자격 증명 또는 `models.json`에서 올 수 있습니다.
명시적인 `auth.order.<provider>`가 저장된 프로필을 생략한 경우, 프로브는 이를 시도하는 대신 `excluded_by_auth_order`를 보고합니다. 인증은 있지만 해당 provider에 대해 프로브 가능한 모델을 해석할 수 없으면 프로브는 `status: no_model`을 보고합니다.

인증 선택은 provider/계정에 따라 달라집니다. 항상 켜져 있는 gateway 호스트에는 보통 API 키가 가장 예측 가능하며, Claude CLI 재사용과 기존 Anthropic OAuth/토큰 프로필도 지원됩니다.

예시(Claude CLI):

```bash
claude auth login
openclaw models status
```

## 스캔(OpenRouter 무료 모델)

`openclaw models scan`은 OpenRouter의 **무료 모델 카탈로그**를 검사하며, 선택적으로 tool 및 이미지 지원 여부를 프로브할 수 있습니다.

주요 플래그:

- `--no-probe`: 실시간 프로브 건너뛰기(메타데이터만)
- `--min-params <b>`: 최소 파라미터 크기(십억 단위)
- `--max-age-days <days>`: 오래된 모델 건너뛰기
- `--provider <name>`: provider 접두사 필터
- `--max-candidates <n>`: 폴백 목록 크기
- `--set-default`: `agents.defaults.model.primary`를 첫 번째 선택 항목으로 설정
- `--set-image`: `agents.defaults.imageModel.primary`를 첫 번째 이미지 선택 항목으로 설정

프로브에는 OpenRouter API 키(인증 프로필 또는 `OPENROUTER_API_KEY`)가 필요합니다. 키가 없는 경우 `--no-probe`를 사용해 후보만 나열하세요.

스캔 결과는 다음 기준으로 순위가 매겨집니다.

1. 이미지 지원
2. tool 지연 시간
3. 컨텍스트 크기
4. 파라미터 수

입력

- OpenRouter `/models` 목록(`:free` 필터)
- 인증 프로필 또는 `OPENROUTER_API_KEY`의 OpenRouter API 키 필요([/environment](/help/environment) 참조)
- 선택적 필터: `--max-age-days`, `--min-params`, `--provider`, `--max-candidates`
- 프로브 제어: `--timeout`, `--concurrency`

TTY에서 실행하면 대화형으로 폴백을 선택할 수 있습니다. 비대화형 모드에서는 기본값을 수락하려면 `--yes`를 전달하세요.

## 모델 레지스트리(`models.json`)

`models.providers`의 사용자 지정 providers는 에이전트 디렉터리 아래(기본값 `~/.openclaw/agents/<agentId>/agent/models.json`)의 `models.json`에 기록됩니다. 이 파일은 `models.mode`가 `replace`로 설정되지 않는 한 기본적으로 병합됩니다.

일치하는 provider ID에 대한 병합 모드 우선순위:

- 에이전트 `models.json`에 이미 존재하는 비어 있지 않은 `baseUrl`이 우선합니다.
- 에이전트 `models.json`의 비어 있지 않은 `apiKey`는 현재 config/인증 프로필 컨텍스트에서 해당 provider가 SecretRef로 관리되지 않을 때만 우선합니다.
- SecretRef로 관리되는 provider `apiKey` 값은 해석된 시크릿을 유지하는 대신 소스 마커(env ref의 경우 `ENV_VAR_NAME`, file/exec ref의 경우 `secretref-managed`)에서 새로 고쳐집니다.
- SecretRef로 관리되는 provider 헤더 값은 소스 마커(env ref의 경우 `secretref-env:ENV_VAR_NAME`, file/exec ref의 경우 `secretref-managed`)에서 새로 고쳐집니다.
- 비어 있거나 누락된 에이전트 `apiKey`/`baseUrl`은 config `models.providers`로 폴백합니다.
- 다른 provider 필드는 config와 정규화된 카탈로그 데이터에서 새로 고쳐집니다.

마커 지속성은 소스를 권위 있는 기준으로 삼습니다. OpenClaw는 해석된 런타임 시크릿 값이 아니라 활성 소스 config 스냅샷(해석 전)에서 마커를 기록합니다.
이는 `openclaw agent` 같은 명령 기반 경로를 포함해 OpenClaw가 `models.json`을 재생성할 때마다 적용됩니다.

## 관련 문서

- [모델 providers](/concepts/model-providers) — provider 라우팅 및 인증
- [모델 폴백](/concepts/model-failover) — 폴백 체인
- [이미지 생성](/tools/image-generation) — 이미지 모델 구성
- [구성 참조](/gateway/configuration-reference#agent-defaults) — 모델 config 키
