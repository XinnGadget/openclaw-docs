---
read_when:
    - OpenClaw를 처음 설정하는 중
    - 일반적인 구성 패턴을 찾는 중
    - 특정 config 섹션으로 이동하는 중
summary: '구성 개요: 일반적인 작업, 빠른 설정, 전체 참조 링크'
title: Configuration
x-i18n:
    generated_at: "2026-04-05T12:42:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: a39a7de09c5f9540785ec67f37d435a7a86201f0f5f640dae663054f35976712
    source_path: gateway/configuration.md
    workflow: 15
---

# Configuration

OpenClaw는 `~/.openclaw/openclaw.json`에서 선택적 <Tooltip tip="JSON5는 주석과 후행 쉼표를 지원합니다">**JSON5**</Tooltip> config를 읽습니다.

파일이 없으면 OpenClaw는 안전한 기본값을 사용합니다. config를 추가하는 일반적인 이유는 다음과 같습니다.

- 채널을 연결하고 누가 봇에 메시지를 보낼 수 있는지 제어
- 모델, 도구, 샌드박싱 또는 자동화(cron, hooks) 설정
- 세션, 미디어, 네트워킹 또는 UI 조정

사용 가능한 모든 필드는 [full reference](/gateway/configuration-reference)를 참조하세요.

<Tip>
**구성이 처음이신가요?** 대화형 설정에는 `openclaw onboard`로 시작하거나, 완전한 복사-붙여넣기 config는 [Configuration Examples](/gateway/configuration-examples) 가이드를 확인하세요.
</Tip>

## 최소 config

```json5
// ~/.openclaw/openclaw.json
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

## config 편집

<Tabs>
  <Tab title="대화형 마법사">
    ```bash
    openclaw onboard       # 전체 온보딩 흐름
    openclaw configure     # config 마법사
    ```
  </Tab>
  <Tab title="CLI (원라이너)">
    ```bash
    openclaw config get agents.defaults.workspace
    openclaw config set agents.defaults.heartbeat.every "2h"
    openclaw config unset plugins.entries.brave.config.webSearch.apiKey
    ```
  </Tab>
  <Tab title="Control UI">
    [http://127.0.0.1:18789](http://127.0.0.1:18789)을 열고 **Config** 탭을 사용하세요.
    Control UI는 사용 가능한 경우 field
    `title` / `description` 문서 메타데이터와 plugin 및 channel 스키마를 포함해 라이브 config 스키마에서 폼을 렌더링하며,
    탈출구로 **Raw JSON** 편집기도 제공합니다. 드릴다운
    UI 및 기타 도구용으로 gateway는
    `config.schema.lookup`도 노출하여 경로 범위 스키마 노드 하나와 직접 자식 요약을 가져올 수 있습니다.
  </Tab>
  <Tab title="직접 편집">
    `~/.openclaw/openclaw.json`을 직접 편집하세요. Gateway는 파일을 감시하며 변경 사항을 자동으로 적용합니다([hot reload](#config-hot-reload) 참조).
  </Tab>
</Tabs>

## 엄격한 검증

<Warning>
OpenClaw는 스키마와 완전히 일치하는 구성만 허용합니다. 알 수 없는 키, 잘못된 타입, 또는 유효하지 않은 값이 있으면 Gateway는 **시작을 거부**합니다. 루트 수준의 유일한 예외는 편집기가 JSON Schema 메타데이터를 붙일 수 있도록 하는 `$schema`(문자열)입니다.
</Warning>

스키마 도구 참고:

- `openclaw config schema`는 Control UI와
  config 검증에서 사용하는 동일한 JSON Schema 계열을 출력합니다.
- Field `title` 및 `description` 값은 편집기 및 폼 도구를 위해
  스키마 출력에도 포함됩니다.
- 중첩 객체, 와일드카드(`*`), 배열 항목(`[]`) 항목도
  일치하는 field 문서가 있는 경우 동일한 문서 메타데이터를 상속합니다.
- `anyOf` / `oneOf` / `allOf` 구성 분기도 동일한 문서
  메타데이터를 상속하므로 union/intersection 변형에서도 같은 field 도움말을 유지합니다.
- `config.schema.lookup`은 정규화된 config 경로 하나와 얕은
  스키마 노드(`title`, `description`, `type`, `enum`, `const`, 공통 경계값,
  및 유사한 검증 필드), 일치하는 UI 힌트 메타데이터, 드릴다운 도구용 즉시 자식
  요약을 반환합니다.
- 런타임 plugin/channel 스키마는 gateway가 현재
  manifest 레지스트리를 로드할 수 있을 때 병합됩니다.

검증 실패 시:

- Gateway는 부팅되지 않습니다
- 진단 명령만 동작합니다(`openclaw doctor`, `openclaw logs`, `openclaw health`, `openclaw status`)
- 정확한 문제를 보려면 `openclaw doctor`를 실행하세요
- 수정을 적용하려면 `openclaw doctor --fix`(또는 `--yes`)를 실행하세요

## 일반적인 작업

<AccordionGroup>
  <Accordion title="채널 설정하기(WhatsApp, Telegram, Discord 등)">
    각 채널은 `channels.<provider>` 아래에 자체 config 섹션을 가집니다. 설정 단계는 전용 채널 페이지를 참조하세요.

    - [WhatsApp](/channels/whatsapp) — `channels.whatsapp`
    - [Telegram](/channels/telegram) — `channels.telegram`
    - [Discord](/channels/discord) — `channels.discord`
    - [Feishu](/channels/feishu) — `channels.feishu`
    - [Google Chat](/channels/googlechat) — `channels.googlechat`
    - [Microsoft Teams](/channels/msteams) — `channels.msteams`
    - [Slack](/channels/slack) — `channels.slack`
    - [Signal](/channels/signal) — `channels.signal`
    - [iMessage](/channels/imessage) — `channels.imessage`
    - [Mattermost](/channels/mattermost) — `channels.mattermost`

    모든 채널은 동일한 DM 정책 패턴을 공유합니다.

    ```json5
    {
      channels: {
        telegram: {
          enabled: true,
          botToken: "123:abc",
          dmPolicy: "pairing",   // pairing | allowlist | open | disabled
          allowFrom: ["tg:123"], // allowlist/open에서만 사용
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="모델 선택 및 구성">
    기본 모델과 선택적 폴백을 설정하세요.

    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "anthropic/claude-sonnet-4-6",
            fallbacks: ["openai/gpt-5.4"],
          },
          models: {
            "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
            "openai/gpt-5.4": { alias: "GPT" },
          },
        },
      },
    }
    ```

    - `agents.defaults.models`는 모델 카탈로그를 정의하며 `/model`의 allowlist 역할도 합니다.
    - 모델 참조는 `provider/model` 형식을 사용합니다(예: `anthropic/claude-opus-4-6`).
    - `agents.defaults.imageMaxDimensionPx`는 기록/도구 이미지 다운스케일링을 제어합니다(기본값 `1200`). 값이 낮을수록 스크린샷이 많은 실행에서 비전 토큰 사용량이 줄어드는 경우가 많습니다.
    - 채팅에서 모델 전환은 [Models CLI](/concepts/models)를, 인증 회전 및 폴백 동작은 [Model Failover](/concepts/model-failover)를 참조하세요.
    - 커스텀/self-hosted providers는 참조 문서의 [Custom providers](/gateway/configuration-reference#custom-providers-and-base-urls)를 참조하세요.

  </Accordion>

  <Accordion title="누가 봇에 메시지를 보낼 수 있는지 제어">
    DM 액세스는 채널별 `dmPolicy`로 제어됩니다.

    - `"pairing"` (기본값): 알 수 없는 발신자는 승인할 일회용 페어링 코드를 받습니다
    - `"allowlist"`: `allowFrom`(또는 페어링 allow 저장소)에 있는 발신자만 허용
    - `"open"`: 모든 수신 DM 허용(`allowFrom: ["*"]` 필요)
    - `"disabled"`: 모든 DM 무시

    그룹의 경우 `groupPolicy` + `groupAllowFrom` 또는 채널별 allowlist를 사용하세요.

    채널별 세부 사항은 [full reference](/gateway/configuration-reference#dm-and-group-access)를 참조하세요.

  </Accordion>

  <Accordion title="그룹 채팅 mention 게이팅 설정">
    그룹 메시지는 기본적으로 **mention 필요**입니다. 에이전트별로 패턴을 구성하세요.

    ```json5
    {
      agents: {
        list: [
          {
            id: "main",
            groupChat: {
              mentionPatterns: ["@openclaw", "openclaw"],
            },
          },
        ],
      },
      channels: {
        whatsapp: {
          groups: { "*": { requireMention: true } },
        },
      },
    }
    ```

    - **메타데이터 mention**: 네이티브 @mention(WhatsApp 탭-투-멘션, Telegram @bot 등)
    - **텍스트 패턴**: `mentionPatterns`의 안전한 정규식 패턴
    - 채널별 재정의 및 self-chat mode는 [full reference](/gateway/configuration-reference#group-chat-mention-gating)를 참조하세요.

  </Accordion>

  <Accordion title="에이전트별 Skills 제한">
    공유 기준선에는 `agents.defaults.skills`를 사용하고, 특정
    에이전트 재정의에는 `agents.list[].skills`를 사용하세요.

    ```json5
    {
      agents: {
        defaults: {
          skills: ["github", "weather"],
        },
        list: [
          { id: "writer" }, // github, weather 상속
          { id: "docs", skills: ["docs-search"] }, // 기본값 대체
          { id: "locked-down", skills: [] }, // Skills 없음
        ],
      },
    }
    ```

    - 기본적으로 Skills를 제한하지 않으려면 `agents.defaults.skills`를 생략하세요.
    - 기본값을 상속하려면 `agents.list[].skills`를 생략하세요.
    - Skills를 사용하지 않으려면 `agents.list[].skills: []`를 설정하세요.
    - [Skills](/tools/skills), [Skills config](/tools/skills-config), 그리고
      [Configuration Reference](/gateway/configuration-reference#agentsdefaultsskills)를 참조하세요.

  </Accordion>

  <Accordion title="gateway 채널 상태 모니터링 조정">
    gateway가 오래된 것으로 보이는 채널을 얼마나 적극적으로 재시작할지 제어합니다.

    ```json5
    {
      gateway: {
        channelHealthCheckMinutes: 5,
        channelStaleEventThresholdMinutes: 30,
        channelMaxRestartsPerHour: 10,
      },
      channels: {
        telegram: {
          healthMonitor: { enabled: false },
          accounts: {
            alerts: {
              healthMonitor: { enabled: true },
            },
          },
        },
      },
    }
    ```

    - 전역적으로 상태 모니터 재시작을 비활성화하려면 `gateway.channelHealthCheckMinutes: 0`을 설정하세요.
    - `channelStaleEventThresholdMinutes`는 검사 간격보다 크거나 같아야 합니다.
    - 전역 모니터를 끄지 않고 특정 채널 또는 account의 자동 재시작을 비활성화하려면 `channels.<provider>.healthMonitor.enabled` 또는 `channels.<provider>.accounts.<id>.healthMonitor.enabled`를 사용하세요.
    - 운영 디버깅은 [Health Checks](/gateway/health), 모든 field는 [full reference](/gateway/configuration-reference#gateway)를 참조하세요.

  </Accordion>

  <Accordion title="세션 및 리셋 구성">
    세션은 대화 연속성과 격리를 제어합니다.

    ```json5
    {
      session: {
        dmScope: "per-channel-peer",  // 다중 사용자에 권장
        threadBindings: {
          enabled: true,
          idleHours: 24,
          maxAgeHours: 0,
        },
        reset: {
          mode: "daily",
          atHour: 4,
          idleMinutes: 120,
        },
      },
    }
    ```

    - `dmScope`: `main` (공유) | `per-peer` | `per-channel-peer` | `per-account-channel-peer`
    - `threadBindings`: 스레드 바인딩 세션 라우팅용 전역 기본값(Discord는 `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` 지원).
    - 범위, identity 링크, 전송 정책은 [Session Management](/concepts/session)를 참조하세요.
    - 모든 field는 [full reference](/gateway/configuration-reference#session)를 참조하세요.

  </Accordion>

  <Accordion title="샌드박싱 활성화">
    격리된 Docker 컨테이너에서 에이전트 세션을 실행합니다.

    ```json5
    {
      agents: {
        defaults: {
          sandbox: {
            mode: "non-main",  // off | non-main | all
            scope: "agent",    // session | agent | shared
          },
        },
      },
    }
    ```

    먼저 이미지를 빌드하세요: `scripts/sandbox-setup.sh`

    전체 가이드는 [Sandboxing](/gateway/sandboxing), 모든 옵션은 [full reference](/gateway/configuration-reference#agentsdefaultssandbox)를 참조하세요.

  </Accordion>

  <Accordion title="공식 iOS 빌드를 위한 relay 기반 push 활성화">
    Relay 기반 push는 `openclaw.json`에서 구성합니다.

    gateway config에 다음을 설정하세요.

    ```json5
    {
      gateway: {
        push: {
          apns: {
            relay: {
              baseUrl: "https://relay.example.com",
              // 선택 사항. 기본값: 10000
              timeoutMs: 10000,
            },
          },
        },
      },
    }
    ```

    동등한 CLI:

    ```bash
    openclaw config set gateway.push.apns.relay.baseUrl https://relay.example.com
    ```

    이것이 하는 일:

    - gateway가 외부 relay를 통해 `push.test`, wake nudges, reconnect wakes를 보낼 수 있게 합니다.
    - 페어링된 iOS 앱이 전달한 registration 범위 send grant를 사용합니다. gateway에는 배포 전역 relay 토큰이 필요하지 않습니다.
    - 각 relay 기반 registration을 iOS 앱이 페어링한 gateway identity에 바인딩하므로 다른 gateway가 저장된 registration을 재사용할 수 없습니다.
    - 로컬/수동 iOS 빌드는 direct APNs를 계속 사용합니다. Relay 기반 전송은 relay를 통해 등록한 공식 배포 빌드에만 적용됩니다.
    - registration과 send 트래픽이 동일한 relay 배포에 도달하도록, 공식/TestFlight iOS 빌드에 내장된 relay base URL과 일치해야 합니다.

    엔드투엔드 흐름:

    1. 동일한 relay base URL로 컴파일된 공식/TestFlight iOS 빌드를 설치합니다.
    2. gateway에 `gateway.push.apns.relay.baseUrl`을 구성합니다.
    3. iOS 앱을 gateway에 페어링하고 node 및 operator 세션이 모두 연결되도록 합니다.
    4. iOS 앱은 gateway identity를 가져오고, App Attest와 앱 영수증을 사용해 relay에 등록한 뒤, relay 기반 `push.apns.register` 페이로드를 페어링된 gateway에 게시합니다.
    5. gateway는 relay handle과 send grant를 저장한 뒤, 이를 `push.test`, wake nudges, reconnect wakes에 사용합니다.

    운영 참고:

    - iOS 앱을 다른 gateway로 전환하면 앱을 다시 연결하여 새 gateway에 바인딩된 새 relay registration을 게시하게 하세요.
    - 다른 relay 배포를 가리키는 새 iOS 빌드를 배포하면, 앱은 이전 relay origin을 재사용하는 대신 캐시된 relay registration을 새로 고칩니다.

    호환성 참고:

    - `OPENCLAW_APNS_RELAY_BASE_URL`과 `OPENCLAW_APNS_RELAY_TIMEOUT_MS`는 여전히 임시 env 재정의로 작동합니다.
    - `OPENCLAW_APNS_RELAY_ALLOW_HTTP=true`는 loopback 전용 개발용 탈출구로 유지됩니다. HTTP relay URL을 config에 영구 저장하지 마세요.

    엔드투엔드 흐름은 [iOS App](/platforms/ios#relay-backed-push-for-official-builds), relay 보안 모델은 [Authentication and trust flow](/platforms/ios#authentication-and-trust-flow)를 참조하세요.

  </Accordion>

  <Accordion title="heartbeat 설정(주기적 체크인)">
    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "30m",
            target: "last",
          },
        },
      },
    }
    ```

    - `every`: 기간 문자열(`30m`, `2h`). 비활성화하려면 `0m` 설정.
    - `target`: `last` | `none` | `<channel-id>` (예: `discord`, `matrix`, `telegram`, `whatsapp`)
    - `directPolicy`: `allow` (기본값) 또는 DM 스타일 heartbeat 대상에는 `block`
    - 전체 가이드는 [Heartbeat](/gateway/heartbeat)를 참조하세요.

  </Accordion>

  <Accordion title="cron 작업 구성">
    ```json5
    {
      cron: {
        enabled: true,
        maxConcurrentRuns: 2,
        sessionRetention: "24h",
        runLog: {
          maxBytes: "2mb",
          keepLines: 2000,
        },
      },
    }
    ```

    - `sessionRetention`: 완료된 격리 실행 세션을 `sessions.json`에서 정리합니다(기본값 `24h`; 비활성화하려면 `false`).
    - `runLog`: 크기와 보존 줄 수를 기준으로 `cron/runs/<jobId>.jsonl` 정리.
    - 기능 개요와 CLI 예시는 [Cron jobs](/automation/cron-jobs)를 참조하세요.

  </Accordion>

  <Accordion title="웹훅 설정(hooks)">
    Gateway에서 HTTP webhook 엔드포인트를 활성화합니다.

    ```json5
    {
      hooks: {
        enabled: true,
        token: "shared-secret",
        path: "/hooks",
        defaultSessionKey: "hook:ingress",
        allowRequestSessionKey: false,
        allowedSessionKeyPrefixes: ["hook:"],
        mappings: [
          {
            match: { path: "gmail" },
            action: "agent",
            agentId: "main",
            deliver: true,
          },
        ],
      },
    }
    ```

    보안 참고:
    - 모든 hook/webhook 페이로드 콘텐츠는 신뢰되지 않은 입력으로 취급하세요.
    - 전용 `hooks.token`을 사용하세요. 공유 Gateway 토큰을 재사용하지 마세요.
    - Hook 인증은 헤더 전용입니다(`Authorization: Bearer ...` 또는 `x-openclaw-token`). 쿼리 문자열 토큰은 거부됩니다.
    - `hooks.path`는 `/`가 될 수 없습니다. webhook 유입은 `/hooks` 같은 전용 하위 경로에 두세요.
    - tightly scoped debugging이 아닌 한, 안전하지 않은 콘텐츠 우회 플래그(`hooks.gmail.allowUnsafeExternalContent`, `hooks.mappings[].allowUnsafeExternalContent`)는 비활성화 상태로 유지하세요.
    - `hooks.allowRequestSessionKey`를 활성화한다면 `hooks.allowedSessionKeyPrefixes`도 함께 설정해 호출자가 선택한 session key 범위를 제한하세요.
    - hook 기반 에이전트에는 강한 최신 모델 티어와 엄격한 도구 정책(예: 가능한 경우 메시징 전용 + 샌드박싱)을 권장합니다.

    모든 매핑 옵션과 Gmail 통합은 [full reference](/gateway/configuration-reference#hooks)를 참조하세요.

  </Accordion>

  <Accordion title="다중 에이전트 라우팅 구성">
    별도의 workspaces와 세션을 가진 여러 격리 에이전트를 실행합니다.

    ```json5
    {
      agents: {
        list: [
          { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
          { id: "work", workspace: "~/.openclaw/workspace-work" },
        ],
      },
      bindings: [
        { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
        { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
      ],
    }
    ```

    바인딩 규칙과 에이전트별 액세스 프로필은 [Multi-Agent](/concepts/multi-agent) 및 [full reference](/gateway/configuration-reference#multi-agent-routing)를 참조하세요.

  </Accordion>

  <Accordion title="config를 여러 파일로 분리($include)">
    큰 configs를 정리하려면 `$include`를 사용하세요.

    ```json5
    // ~/.openclaw/openclaw.json
    {
      gateway: { port: 18789 },
      agents: { $include: "./agents.json5" },
      broadcast: {
        $include: ["./clients/a.json5", "./clients/b.json5"],
      },
    }
    ```

    - **단일 파일**: 포함하는 객체를 대체
    - **파일 배열**: 순서대로 깊은 병합(나중 항목 우선)
    - **형제 키**: include 뒤에 병합됨(포함된 값 재정의)
    - **중첩 include**: 최대 10단계까지 지원
    - **상대 경로**: 포함하는 파일 기준으로 해석
    - **오류 처리**: 누락 파일, 파싱 오류, 순환 include에 대해 명확한 오류 제공

  </Accordion>
</AccordionGroup>

## Config 핫 리로드

Gateway는 `~/.openclaw/openclaw.json`을 감시하고 변경 사항을 자동 적용합니다 — 대부분의 설정에는 수동 재시작이 필요하지 않습니다.

### 리로드 모드

| 모드                   | 동작                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------ |
| **`hybrid`** (기본값) | 안전한 변경은 즉시 핫 적용합니다. 중요한 변경은 자동으로 재시작합니다.               |
| **`hot`**              | 안전한 변경만 핫 적용합니다. 재시작이 필요할 때 경고를 기록하며 직접 처리해야 합니다. |
| **`restart`**          | 안전 여부와 관계없이 모든 config 변경 시 Gateway를 재시작합니다.                     |
| **`off`**              | 파일 감시를 비활성화합니다. 변경은 다음 수동 재시작 때 적용됩니다.                   |

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

### 핫 적용되는 항목과 재시작이 필요한 항목

대부분의 필드는 다운타임 없이 핫 적용됩니다. `hybrid` 모드에서는 재시작이 필요한 변경도 자동 처리됩니다.

| 범주                | 필드                                                                 | 재시작 필요? |
| ------------------- | -------------------------------------------------------------------- | ------------ |
| Channels            | `channels.*`, `web` (WhatsApp) — 모든 내장 및 extension 채널         | 아니요       |
| Agent & models      | `agent`, `agents`, `models`, `routing`                               | 아니요       |
| Automation          | `hooks`, `cron`, `agent.heartbeat`                                   | 아니요       |
| Sessions & messages | `session`, `messages`                                                | 아니요       |
| Tools & media       | `tools`, `browser`, `skills`, `audio`, `talk`                        | 아니요       |
| UI & misc           | `ui`, `logging`, `identity`, `bindings`                              | 아니요       |
| Gateway server      | `gateway.*` (port, bind, auth, tailscale, TLS, HTTP)                 | **예**       |
| Infrastructure      | `discovery`, `canvasHost`, `plugins`                                 | **예**       |

<Note>
`gateway.reload`와 `gateway.remote`는 예외입니다 — 이를 변경해도 **재시작이 트리거되지 않습니다**.
</Note>

## Config RPC (프로그래밍 방식 업데이트)

<Note>
컨트롤 플레인 쓰기 RPC(`config.apply`, `config.patch`, `update.run`)는 `deviceId+clientIp` 기준으로 **60초당 3요청**으로 속도 제한됩니다. 제한되면 RPC는 `retryAfterMs`와 함께 `UNAVAILABLE`을 반환합니다.
</Note>

안전한/기본 흐름:

- `config.schema.lookup`: 얕은
  스키마 노드, 일치하는 힌트 메타데이터, 즉시 자식 요약이 포함된 하나의 경로 범위 config 서브트리를 검사
- `config.get`: 현재 스냅샷 + 해시 가져오기
- `config.patch`: 권장되는 부분 업데이트 경로
- `config.apply`: 전체 config 교체 전용
- `update.run`: 명시적인 self-update + 재시작

전체 config를 교체하는 것이 아니라면 `config.schema.lookup`
다음 `config.patch`를 우선 사용하세요.

<AccordionGroup>
  <Accordion title="config.apply (전체 교체)">
    전체 config를 검증 + 기록하고 한 번에 Gateway를 재시작합니다.

    <Warning>
    `config.apply`는 **전체 config**를 교체합니다. 부분 업데이트에는 `config.patch`, 단일 키에는 `openclaw config set`을 사용하세요.
    </Warning>

    매개변수:

    - `raw` (string) — 전체 config용 JSON5 페이로드
    - `baseHash` (선택 사항) — `config.get`의 config 해시(config가 존재하면 필수)
    - `sessionKey` (선택 사항) — 재시작 후 wake-up ping용 세션 키
    - `note` (선택 사항) — restart sentinel용 메모
    - `restartDelayMs` (선택 사항) — 재시작 전 지연(기본값 2000)

    이미 재시작이 보류/진행 중인 동안의 재시작 요청은 병합되며, 재시작 주기 사이에는 30초 쿨다운이 적용됩니다.

    ```bash
    openclaw gateway call config.get --params '{}'  # payload.hash 캡처
    openclaw gateway call config.apply --params '{
      "raw": "{ agents: { defaults: { workspace: \"~/.openclaw/workspace\" } } }",
      "baseHash": "<hash>",
      "sessionKey": "agent:main:whatsapp:direct:+15555550123"
    }'
    ```

  </Accordion>

  <Accordion title="config.patch (부분 업데이트)">
    기존 config에 부분 업데이트를 병합합니다(JSON merge patch 의미론).

    - 객체는 재귀적으로 병합
    - `null`은 키 삭제
    - 배열은 교체

    매개변수:

    - `raw` (string) — 변경할 키만 포함한 JSON5
    - `baseHash` (필수) — `config.get`의 config 해시
    - `sessionKey`, `note`, `restartDelayMs` — `config.apply`와 동일

    재시작 동작은 `config.apply`와 동일합니다: 보류 중 재시작 병합 + 재시작 주기 간 30초 쿨다운.

    ```bash
    openclaw gateway call config.patch --params '{
      "raw": "{ channels: { telegram: { groups: { \"*\": { requireMention: false } } } } }",
      "baseHash": "<hash>"
    }'
    ```

  </Accordion>
</AccordionGroup>

## 환경 변수

OpenClaw는 부모 프로세스의 env와 다음 위치를 읽습니다.

- 현재 작업 디렉터리의 `.env`(있을 경우)
- `~/.openclaw/.env` (전역 폴백)

어느 파일도 기존 env vars를 재정의하지 않습니다. config에서 인라인 env vars를 설정할 수도 있습니다.

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

<Accordion title="셸 env 가져오기(선택 사항)">
  활성화되어 있고 예상 키가 설정되지 않은 경우, OpenClaw는 로그인 셸을 실행해 누락된 키만 가져옵니다.

```json5
{
  env: {
    shellEnv: { enabled: true, timeoutMs: 15000 },
  },
}
```

Env var 동등값: `OPENCLAW_LOAD_SHELL_ENV=1`
</Accordion>

<Accordion title="config 값에서 Env var 치환">
  `${VAR_NAME}`을 사용해 모든 config 문자열 값에서 env vars를 참조할 수 있습니다.

```json5
{
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } },
  models: { providers: { custom: { apiKey: "${CUSTOM_API_KEY}" } } },
}
```

규칙:

- 대문자 이름만 매칭됨: `[A-Z_][A-Z0-9_]*`
- 누락되었거나 비어 있는 vars는 로드 시 오류를 발생시킴
- 리터럴 출력은 `$${VAR}`로 이스케이프
- `$include` 파일 내부에서도 동작
- 인라인 치환: `"${BASE}/v1"` → `"https://api.example.com/v1"`

</Accordion>

<Accordion title="Secret refs (env, file, exec)">
  SecretRef 객체를 지원하는 필드에는 다음을 사용할 수 있습니다.

```json5
{
  models: {
    providers: {
      openai: { apiKey: { source: "env", provider: "default", id: "OPENAI_API_KEY" } },
    },
  },
  skills: {
    entries: {
      "image-lab": {
        apiKey: {
          source: "file",
          provider: "filemain",
          id: "/skills/entries/image-lab/apiKey",
        },
      },
    },
  },
  channels: {
    googlechat: {
      serviceAccountRef: {
        source: "exec",
        provider: "vault",
        id: "channels/googlechat/serviceAccount",
      },
    },
  },
}
```

SecretRef 세부 사항(`env`/`file`/`exec`용 `secrets.providers` 포함)은 [Secrets Management](/gateway/secrets)에 있습니다.
지원되는 자격 증명 경로는 [SecretRef Credential Surface](/reference/secretref-credential-surface)에 나열되어 있습니다.
</Accordion>

전체 우선순위와 소스는 [Environment](/help/environment)를 참조하세요.

## 전체 참조

필드별 완전한 참조는 **[Configuration Reference](/gateway/configuration-reference)**를 참조하세요.

---

_관련 문서: [Configuration Examples](/gateway/configuration-examples) · [Configuration Reference](/gateway/configuration-reference) · [Doctor](/gateway/doctor)_
