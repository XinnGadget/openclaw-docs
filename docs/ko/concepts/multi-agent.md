---
read_when: You want multiple isolated agents (workspaces + auth) in one gateway process.
status: active
summary: '다중 에이전트 라우팅: 격리된 에이전트, 채널 accounts, bindings'
title: 다중 에이전트 라우팅
x-i18n:
    generated_at: "2026-04-05T12:41:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7e8bc48f229d01aa793ca4137e5a59f2a5ceb0ba65841710aaf69f53a672be60
    source_path: concepts/multi-agent.md
    workflow: 15
---

# 다중 에이전트 라우팅

목표: 하나의 실행 중인 Gateway 안에서 여러 개의 _격리된_ 에이전트(별도 workspace + `agentDir` + 세션)와 여러 채널 accounts(예: WhatsApp 두 개)를 함께 운영하는 것입니다. 수신 메시지는 bindings를 통해 에이전트로 라우팅됩니다.

## "하나의 에이전트"란 무엇인가요?

**에이전트**는 다음을 각각 독립적으로 갖는 완전히 범위화된 두뇌입니다.

- **Workspace** (`AGENTS.md`/`SOUL.md`/`USER.md`, 파일, 로컬 노트, persona 규칙 포함).
- 인증 프로필, 모델 레지스트리, 에이전트별 config를 위한 **상태 디렉터리** (`agentDir`).
- `~/.openclaw/agents/<agentId>/sessions` 아래의 **세션 저장소** (채팅 기록 + 라우팅 상태).

인증 프로필은 **에이전트별**입니다. 각 에이전트는 다음의 자체 파일을 읽습니다.

```text
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

여기서도 `sessions_history`는 더 안전한 세션 간 회상 경로입니다. 원시 기록 전체를 덤프하지 않고,
제한되고 정리된 뷰를 반환합니다. Assistant 회상은
thinking 태그, `<relevant-memories>` 스캐폴딩, 일반 텍스트 도구 호출 XML
페이로드(` <tool_call>...</tool_call>`,
`<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`,
`<function_calls>...</function_calls>`, 잘린 도구 호출 블록 포함),
격하된 도구 호출 스캐폴딩, 유출된 ASCII/전각 모델 제어
토큰, 잘못된 MiniMax 도구 호출 XML을 redaction/truncation 전에 제거합니다.

메인 에이전트 자격 증명은 자동으로 **공유되지 않습니다**. 절대로 에이전트 간에 `agentDir`를 재사용하지 마세요
(인증/세션 충돌이 발생합니다). 자격 증명을 공유하고 싶다면
다른 에이전트의 `agentDir`로 `auth-profiles.json`을 복사하세요.

Skills는 각 에이전트 workspace와 `~/.openclaw/skills` 같은
공유 루트에서 로드된 뒤, 설정된 경우 유효 에이전트 skill allowlist에 따라 필터링됩니다.
공유 기준선에는 `agents.defaults.skills`를 사용하고,
에이전트별 대체에는 `agents.list[].skills`를 사용하세요. 자세한 내용은
[Skills: per-agent vs shared](/tools/skills#per-agent-vs-shared-skills) 및
[Skills: agent skill allowlists](/tools/skills#agent-skill-allowlists)를 참조하세요.

Gateway는 **하나의 에이전트**(기본값) 또는 **여러 에이전트**를 나란히 호스팅할 수 있습니다.

**Workspace 참고:** 각 에이전트의 workspace는 하드
샌드박스가 아니라 **기본 cwd**입니다. 상대 경로는 workspace 내부에서 해석되지만,
샌드박싱이 활성화되지 않으면 절대 경로는 호스트의 다른 위치에
접근할 수 있습니다. 자세한 내용은 [Sandboxing](/gateway/sandboxing)을 참조하세요.

## 경로(빠른 개요)

- Config: `~/.openclaw/openclaw.json` (또는 `OPENCLAW_CONFIG_PATH`)
- 상태 디렉터리: `~/.openclaw` (또는 `OPENCLAW_STATE_DIR`)
- Workspace: `~/.openclaw/workspace` (또는 `~/.openclaw/workspace-<agentId>`)
- Agent 디렉터리: `~/.openclaw/agents/<agentId>/agent` (또는 `agents.list[].agentDir`)
- 세션: `~/.openclaw/agents/<agentId>/sessions`

### 단일 에이전트 모드(기본값)

아무 설정도 하지 않으면 OpenClaw는 단일 에이전트로 실행됩니다.

- `agentId` 기본값은 **`main`**입니다.
- 세션 키는 `agent:main:<mainKey>` 형태입니다.
- Workspace 기본값은 `~/.openclaw/workspace`입니다(`OPENCLAW_PROFILE`이 설정된 경우 `~/.openclaw/workspace-<profile>`).
- 상태 기본값은 `~/.openclaw/agents/main/agent`입니다.

## 에이전트 도우미

에이전트 마법사를 사용해 새 격리 에이전트를 추가하세요.

```bash
openclaw agents add work
```

그런 다음 bindings를 추가해(또는 마법사에 맡겨) 수신 메시지를 라우팅합니다.

다음으로 확인하세요.

```bash
openclaw agents list --bindings
```

## 빠른 시작

<Steps>
  <Step title="각 에이전트 workspace 만들기">

마법사를 사용하거나 수동으로 workspaces를 만드세요.

```bash
openclaw agents add coding
openclaw agents add social
```

각 에이전트는 `SOUL.md`, `AGENTS.md`, 선택적 `USER.md`가 있는 자체 workspace와,
전용 `agentDir`, 그리고 `~/.openclaw/agents/<agentId>` 아래의 세션 저장소를 갖게 됩니다.

  </Step>

  <Step title="채널 account 만들기">

선호하는 채널에서 에이전트당 하나의 account를 만드세요.

- Discord: 에이전트당 봇 하나, Message Content Intent 활성화, 각 토큰 복사.
- Telegram: BotFather로 에이전트당 봇 하나 생성, 각 토큰 복사.
- WhatsApp: account별로 각 전화번호 연결.

```bash
openclaw channels login --channel whatsapp --account work
```

채널 가이드 참조: [Discord](/channels/discord), [Telegram](/channels/telegram), [WhatsApp](/channels/whatsapp).

  </Step>

  <Step title="에이전트, accounts, bindings 추가">

`agents.list` 아래에 에이전트를, `channels.<channel>.accounts` 아래에 채널 accounts를 추가하고, `bindings`로 이들을 연결하세요(예시는 아래 참조).

  </Step>

  <Step title="재시작 및 확인">

```bash
openclaw gateway restart
openclaw agents list --bindings
openclaw channels status --probe
```

  </Step>
</Steps>

## 여러 에이전트 = 여러 사람, 여러 성격

**여러 에이전트**를 사용하면 각 `agentId`는 **완전히 격리된 persona**가 됩니다.

- **서로 다른 전화번호/accounts** (채널별 `accountId` 기준).
- **서로 다른 성격** (예: `AGENTS.md`, `SOUL.md` 같은 에이전트별 workspace 파일 기준).
- **분리된 인증 + 세션** (명시적으로 활성화하지 않으면 상호 간섭 없음).

이를 통해 **여러 사람**이 하나의 Gateway 서버를 공유하면서도 자신의 AI “두뇌”와 데이터를 격리할 수 있습니다.

## 에이전트 간 QMD 메모리 검색

한 에이전트가 다른 에이전트의 QMD 세션 기록을 검색해야 한다면,
`agents.list[].memorySearch.qmd.extraCollections` 아래에
추가 컬렉션을 넣으세요.
모든 에이전트가 동일한 공유 기록 컬렉션을 상속해야 할 때만
`agents.defaults.memorySearch.qmd.extraCollections`를 사용하세요.

```json5
{
  agents: {
    defaults: {
      workspace: "~/workspaces/main",
      memorySearch: {
        qmd: {
          extraCollections: [{ path: "~/agents/family/sessions", name: "family-sessions" }],
        },
      },
    },
    list: [
      {
        id: "main",
        workspace: "~/workspaces/main",
        memorySearch: {
          qmd: {
            extraCollections: [{ path: "notes" }], // workspace 내부에서 해석 -> 컬렉션 이름은 "notes-main"
          },
        },
      },
      { id: "family", workspace: "~/workspaces/family" },
    ],
  },
  memory: {
    backend: "qmd",
    qmd: { includeDefaultMemory: false },
  },
}
```

추가 컬렉션 경로는 에이전트 간 공유할 수 있지만,
경로가 에이전트 workspace 밖에 있으면 컬렉션 이름은 명시적으로 유지됩니다. workspace 내부 경로는
여전히 에이전트 범위로 유지되므로 각 에이전트는 자체 기록 검색 집합을 갖습니다.

## 하나의 WhatsApp 번호, 여러 사람(DM 분리)

**하나의 WhatsApp account**를 유지하면서 **서로 다른 WhatsApp DM**을 서로 다른 에이전트로 라우팅할 수 있습니다.
발신자 E.164(예: `+15551234567`) 기준으로 `peer.kind: "direct"`를 매칭하세요. 응답은 여전히 동일한 WhatsApp 번호에서 오며(에이전트별 발신자 identity는 없음),
직접 채팅은 에이전트의 **메인 세션 키**로 축약되기 때문에, 진정한 격리를 위해서는 **사람당 하나의 에이전트**가 필요합니다.

예시:

```json5
{
  agents: {
    list: [
      { id: "alex", workspace: "~/.openclaw/workspace-alex" },
      { id: "mia", workspace: "~/.openclaw/workspace-mia" },
    ],
  },
  bindings: [
    {
      agentId: "alex",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230001" } },
    },
    {
      agentId: "mia",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230002" } },
    },
  ],
  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15551230001", "+15551230002"],
    },
  },
}
```

참고:

- DM 액세스 제어는 에이전트별이 아니라 **WhatsApp account 전체에 대해 전역적**입니다(pairing/allowlist).
- 공유 그룹의 경우 그룹을 하나의 에이전트에 바인딩하거나 [Broadcast groups](/channels/broadcast-groups)를 사용하세요.

## 라우팅 규칙(메시지가 에이전트를 선택하는 방식)

Bindings는 **결정적**이며 **가장 구체적인 것이 우선**합니다.

1. `peer` 매치(정확한 DM/group/channel id)
2. `parentPeer` 매치(스레드 상속)
3. `guildId + roles` (Discord 역할 라우팅)
4. `guildId` (Discord)
5. `teamId` (Slack)
6. 채널의 `accountId` 매치
7. 채널 수준 매치(`accountId: "*"`)
8. 기본 에이전트로 폴백(`agents.list[].default`, 없으면 목록의 첫 번째 항목, 기본값: `main`)

같은 단계에서 여러 bindings가 일치하면 config 순서상 첫 번째 항목이 우선합니다.
binding이 여러 match 필드(예: `peer` + `guildId`)를 설정하면 지정된 모든 필드가 필요합니다(`AND` 의미론).

중요한 account 범위 세부 사항:

- `accountId`를 생략한 binding은 기본 account에만 매치됩니다.
- 모든 accounts에 대한 채널 전체 폴백에는 `accountId: "*"`를 사용하세요.
- 이후 같은 에이전트에 대해 명시적인 account id를 가진 동일한 binding을 추가하면, OpenClaw는 기존 채널 전용 binding을 중복 생성하는 대신 account 범위로 승격합니다.

## 여러 accounts / 전화번호

**여러 accounts**를 지원하는 채널(예: WhatsApp)은 각 로그인 인스턴스를 식별하기 위해 `accountId`를 사용합니다.
각 `accountId`는 서로 다른 에이전트로 라우팅될 수 있으므로, 하나의 서버에서
세션을 섞지 않고 여러 전화번호를 호스팅할 수 있습니다.

`accountId`가 생략되었을 때 채널 전체 기본 account를 지정하려면
`channels.<channel>.defaultAccount`를 설정하세요(선택 사항). 설정되지 않으면 OpenClaw는
`default`가 있으면 이를 사용하고, 없으면 첫 번째로 구성된 account id(정렬 기준)로 폴백합니다.

이 패턴을 지원하는 일반적인 채널은 다음과 같습니다.

- `whatsapp`, `telegram`, `discord`, `slack`, `signal`, `imessage`
- `irc`, `line`, `googlechat`, `mattermost`, `matrix`, `nextcloud-talk`
- `bluebubbles`, `zalo`, `zalouser`, `nostr`, `feishu`

## 개념

- `agentId`: 하나의 “두뇌”(workspace, 에이전트별 인증, 에이전트별 세션 저장소).
- `accountId`: 하나의 채널 account 인스턴스(예: WhatsApp account `"personal"` 대 `"biz"`).
- `binding`: `(channel, accountId, peer)` 및 선택적 guild/team ids를 기준으로 수신 메시지를 `agentId`로 라우팅합니다.
- 직접 채팅은 `agent:<agentId>:<mainKey>`로 축약됩니다(에이전트별 “main”; `session.mainKey`).

## 플랫폼 예시

### 에이전트별 Discord 봇

각 Discord 봇 account는 고유한 `accountId`에 매핑됩니다. 각 account를 에이전트에 바인딩하고 봇별 allowlist를 유지하세요.

```json5
{
  agents: {
    list: [
      { id: "main", workspace: "~/.openclaw/workspace-main" },
      { id: "coding", workspace: "~/.openclaw/workspace-coding" },
    ],
  },
  bindings: [
    { agentId: "main", match: { channel: "discord", accountId: "default" } },
    { agentId: "coding", match: { channel: "discord", accountId: "coding" } },
  ],
  channels: {
    discord: {
      groupPolicy: "allowlist",
      accounts: {
        default: {
          token: "DISCORD_BOT_TOKEN_MAIN",
          guilds: {
            "123456789012345678": {
              channels: {
                "222222222222222222": { allow: true, requireMention: false },
              },
            },
          },
        },
        coding: {
          token: "DISCORD_BOT_TOKEN_CODING",
          guilds: {
            "123456789012345678": {
              channels: {
                "333333333333333333": { allow: true, requireMention: false },
              },
            },
          },
        },
      },
    },
  },
}
```

참고:

- 각 봇을 길드에 초대하고 Message Content Intent를 활성화하세요.
- 토큰은 `channels.discord.accounts.<id>.token`에 저장됩니다(기본 account는 `DISCORD_BOT_TOKEN` 사용 가능).

### 에이전트별 Telegram 봇

```json5
{
  agents: {
    list: [
      { id: "main", workspace: "~/.openclaw/workspace-main" },
      { id: "alerts", workspace: "~/.openclaw/workspace-alerts" },
    ],
  },
  bindings: [
    { agentId: "main", match: { channel: "telegram", accountId: "default" } },
    { agentId: "alerts", match: { channel: "telegram", accountId: "alerts" } },
  ],
  channels: {
    telegram: {
      accounts: {
        default: {
          botToken: "123456:ABC...",
          dmPolicy: "pairing",
        },
        alerts: {
          botToken: "987654:XYZ...",
          dmPolicy: "allowlist",
          allowFrom: ["tg:123456789"],
        },
      },
    },
  },
}
```

참고:

- BotFather로 에이전트당 하나의 봇을 만들고 각 토큰을 복사하세요.
- 토큰은 `channels.telegram.accounts.<id>.botToken`에 저장됩니다(기본 account는 `TELEGRAM_BOT_TOKEN` 사용 가능).

### 에이전트별 WhatsApp 번호

Gateway를 시작하기 전에 각 account를 연결하세요.

```bash
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account biz
```

`~/.openclaw/openclaw.json` (JSON5):

```js
{
  agents: {
    list: [
      {
        id: "home",
        default: true,
        name: "Home",
        workspace: "~/.openclaw/workspace-home",
        agentDir: "~/.openclaw/agents/home/agent",
      },
      {
        id: "work",
        name: "Work",
        workspace: "~/.openclaw/workspace-work",
        agentDir: "~/.openclaw/agents/work/agent",
      },
    ],
  },

  // 결정적 라우팅: 첫 번째 일치 항목이 우선(가장 구체적인 항목을 먼저).
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },

    // 선택적 peer별 재정의(예: 특정 그룹을 work 에이전트로 보냄).
    {
      agentId: "work",
      match: {
        channel: "whatsapp",
        accountId: "personal",
        peer: { kind: "group", id: "1203630...@g.us" },
      },
    },
  ],

  // 기본값은 꺼짐: agent-to-agent 메시징은 명시적으로 활성화하고 allowlist에 넣어야 함.
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },

  channels: {
    whatsapp: {
      accounts: {
        personal: {
          // 선택적 재정의. 기본값: ~/.openclaw/credentials/whatsapp/personal
          // authDir: "~/.openclaw/credentials/whatsapp/personal",
        },
        biz: {
          // 선택적 재정의. 기본값: ~/.openclaw/credentials/whatsapp/biz
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

## 예시: WhatsApp 일상 대화 + Telegram 딥 워크

채널 기준으로 분리: WhatsApp은 빠른 일상용 에이전트로, Telegram은 Opus 에이전트로 라우팅합니다.

```json5
{
  agents: {
    list: [
      {
        id: "chat",
        name: "Everyday",
        workspace: "~/.openclaw/workspace-chat",
        model: "anthropic/claude-sonnet-4-6",
      },
      {
        id: "opus",
        name: "Deep Work",
        workspace: "~/.openclaw/workspace-opus",
        model: "anthropic/claude-opus-4-6",
      },
    ],
  },
  bindings: [
    { agentId: "chat", match: { channel: "whatsapp" } },
    { agentId: "opus", match: { channel: "telegram" } },
  ],
}
```

참고:

- 채널에 여러 accounts가 있다면 binding에 `accountId`를 추가하세요(예: `{ channel: "whatsapp", accountId: "personal" }`).
- 나머지는 chat에 두고 하나의 DM/group만 Opus로 라우팅하려면 해당 peer에 대한 `match.peer` binding을 추가하세요. peer 매치는 항상 채널 전체 규칙보다 우선합니다.

## 예시: 같은 채널, 하나의 peer만 Opus로

WhatsApp은 빠른 에이전트에 두되, 하나의 DM만 Opus로 라우팅합니다.

```json5
{
  agents: {
    list: [
      {
        id: "chat",
        name: "Everyday",
        workspace: "~/.openclaw/workspace-chat",
        model: "anthropic/claude-sonnet-4-6",
      },
      {
        id: "opus",
        name: "Deep Work",
        workspace: "~/.openclaw/workspace-opus",
        model: "anthropic/claude-opus-4-6",
      },
    ],
  },
  bindings: [
    {
      agentId: "opus",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551234567" } },
    },
    { agentId: "chat", match: { channel: "whatsapp" } },
  ],
}
```

peer bindings는 항상 우선하므로 채널 전체 규칙 위에 두세요.

## WhatsApp 그룹에 바인딩된 가족 에이전트

mention 게이팅과 더 엄격한 도구 정책을 사용해,
전용 가족 에이전트를 하나의 WhatsApp 그룹에 바인딩합니다.

```json5
{
  agents: {
    list: [
      {
        id: "family",
        name: "Family",
        workspace: "~/.openclaw/workspace-family",
        identity: { name: "Family Bot" },
        groupChat: {
          mentionPatterns: ["@family", "@familybot", "@Family Bot"],
        },
        sandbox: {
          mode: "all",
          scope: "agent",
        },
        tools: {
          allow: [
            "exec",
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "browser", "canvas", "nodes", "cron"],
        },
      },
    ],
  },
  bindings: [
    {
      agentId: "family",
      match: {
        channel: "whatsapp",
        peer: { kind: "group", id: "120363999999999999@g.us" },
      },
    },
  ],
}
```

참고:

- 도구 allow/deny 목록은 **Skills가 아니라 tools**입니다. skill이
  바이너리를 실행해야 한다면 `exec`가 허용되어 있고 해당 바이너리가 샌드박스 안에 존재하는지 확인하세요.
- 더 엄격한 게이팅을 위해 `agents.list[].groupChat.mentionPatterns`를 설정하고,
  채널에 대해 그룹 allowlist를 계속 활성화하세요.

## 에이전트별 샌드박스 및 도구 구성

각 에이전트는 자체 샌드박스와 도구 제한을 가질 수 있습니다.

```js
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: {
          mode: "off",  // 개인 에이전트에는 샌드박스 없음
        },
        // 도구 제한 없음 - 모든 도구 사용 가능
      },
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: {
          mode: "all",     // 항상 샌드박스 적용
          scope: "agent",  // 에이전트당 하나의 컨테이너
          docker: {
            // 컨테이너 생성 후 선택적으로 한 번만 수행하는 설정
            setupCommand: "apt-get update && apt-get install -y git curl",
          },
        },
        tools: {
          allow: ["read"],                    // read 도구만 허용
          deny: ["exec", "write", "edit", "apply_patch"],    // 나머지는 거부
        },
      },
    ],
  },
}
```

참고: `setupCommand`는 `sandbox.docker` 아래에 있으며 컨테이너 생성 시 한 번 실행됩니다.
해결된 범위가 `"shared"`이면 에이전트별 `sandbox.docker.*` 재정의는 무시됩니다.

**장점:**

- **보안 격리**: 신뢰되지 않는 에이전트의 도구 제한
- **리소스 제어**: 일부 에이전트만 샌드박스에 넣고 다른 에이전트는 호스트에 유지
- **유연한 정책**: 에이전트별로 다른 권한 설정

참고: `tools.elevated`는 **전역**이며 발신자 기반입니다. 에이전트별로 구성할 수 없습니다.
에이전트별 경계가 필요하다면 `agents.list[].tools`를 사용해 `exec`를 거부하세요.
그룹 대상을 지정하려면 `agents.list[].groupChat.mentionPatterns`를 사용해
@mentions가 의도한 에이전트에 명확하게 매핑되도록 하세요.

자세한 예시는 [Multi-Agent Sandbox & Tools](/tools/multi-agent-sandbox-tools)를 참조하세요.

## 관련 문서

- [Channel Routing](/channels/channel-routing) — 메시지가 에이전트로 라우팅되는 방식
- [Sub-Agents](/tools/subagents) — 백그라운드 에이전트 실행 생성
- [ACP Agents](/tools/acp-agents) — 외부 코딩 하네스 실행
- [Presence](/concepts/presence) — 에이전트 상태 및 가용성
- [Session](/concepts/session) — 세션 격리 및 라우팅
