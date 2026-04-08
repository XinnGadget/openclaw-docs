---
read_when:
    - 정확한 필드 수준의 구성 의미 또는 기본값이 필요할 때
    - 채널, 모델, gateway 또는 tool 구성 블록을 검증하고 있을 때
summary: 핵심 OpenClaw 키, 기본값, 그리고 전용 서브시스템 참조 링크를 위한 Gateway 구성 참조
title: 구성 참조
x-i18n:
    generated_at: "2026-04-08T06:01:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2f9ab34fb56897a77cb038d95bea21e8530d8f0402b66d1ee97c73822a1e8fd4
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# 구성 참조

`~/.openclaw/openclaw.json`에 대한 핵심 구성 참조입니다. 작업 중심 개요는 [Configuration](/ko/gateway/configuration)을 참고하세요.

이 페이지는 주요 OpenClaw 구성 표면을 다루며, 서브시스템에 별도의 더 깊은 참조가 있는 경우 해당 링크를 제공합니다. 이 페이지는 모든 채널/플러그인 소유 명령 카탈로그나 모든 심층 메모리/QMD 노브를 한 페이지에 인라인으로 넣으려는 것은 **아닙니다**.

코드 기준 진실:

- `openclaw config schema`는 검증과 Control UI에 사용되는 실제 JSON Schema를 출력하며, 사용 가능한 경우 번들/플러그인/채널 메타데이터가 병합됩니다
- `config.schema.lookup`는 드릴다운 도구용으로 경로 범위가 지정된 단일 스키마 노드를 반환합니다
- `pnpm config:docs:check` / `pnpm config:docs:gen`는 현재 스키마 표면과 구성 문서 기준 해시를 검증합니다

전용 심층 참조:

- `agents.defaults.memorySearch.*`, `memory.qmd.*`, `memory.citations`, 그리고 `plugins.entries.memory-core.config.dreaming` 아래의 dreaming 구성을 위한 [Memory configuration reference](/ko/reference/memory-config)
- 현재 내장 + 번들 명령 카탈로그를 위한 [Slash Commands](/ko/tools/slash-commands)
- 채널별 명령 표면에 대한 각 채널/플러그인 소유 페이지

구성 형식은 **JSON5**입니다(주석 + 후행 쉼표 허용). 모든 필드는 선택 사항이며, 생략되면 OpenClaw가 안전한 기본값을 사용합니다.

---

## 채널

각 채널은 해당 구성 섹션이 존재하면 자동으로 시작됩니다(`enabled: false`가 아닌 경우).

### DM 및 그룹 액세스

모든 채널은 DM 정책과 그룹 정책을 지원합니다:

| DM 정책            | 동작                                                            |
| ------------------ | --------------------------------------------------------------- |
| `pairing` (기본값) | 알 수 없는 발신자는 일회성 페어링 코드를 받으며, 소유자가 승인해야 함 |
| `allowlist`        | `allowFrom`(또는 페어링된 허용 저장소)에 있는 발신자만 허용         |
| `open`             | 모든 수신 DM 허용(`allowFrom: ["*"]` 필요)                         |
| `disabled`         | 모든 수신 DM 무시                                                 |

| 그룹 정책             | 동작                                                     |
| --------------------- | -------------------------------------------------------- |
| `allowlist` (기본값)  | 구성된 허용 목록과 일치하는 그룹만 허용                  |
| `open`                | 그룹 허용 목록 우회(멘션 게이팅은 계속 적용)             |
| `disabled`            | 모든 그룹/룸 메시지 차단                                 |

<Note>
`channels.defaults.groupPolicy`는 공급자의 `groupPolicy`가 설정되지 않았을 때 기본값을 설정합니다.
페어링 코드는 1시간 후 만료됩니다. 대기 중인 DM 페어링 요청은 **채널당 3개**로 제한됩니다.
공급자 블록이 완전히 누락된 경우(`channels.<provider>` 부재), 런타임 그룹 정책은 시작 경고와 함께 `allowlist`(fail-closed)로 대체됩니다.
</Note>

### 채널 모델 재정의

특정 채널 ID를 모델에 고정하려면 `channels.modelByChannel`을 사용하세요. 값은 `provider/model` 또는 구성된 모델 별칭을 받습니다. 이 채널 매핑은 세션에 이미 모델 재정의가 없는 경우(예: `/model`로 설정된 경우) 적용됩니다.

```json5
{
  channels: {
    modelByChannel: {
      discord: {
        "123456789012345678": "anthropic/claude-opus-4-6",
      },
      slack: {
        C1234567890: "openai/gpt-4.1",
      },
      telegram: {
        "-1001234567890": "openai/gpt-4.1-mini",
        "-1001234567890:topic:99": "anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

### 채널 기본값 및 heartbeat

공급자 간 공유 그룹 정책 및 heartbeat 동작에는 `channels.defaults`를 사용하세요:

```json5
{
  channels: {
    defaults: {
      groupPolicy: "allowlist", // open | allowlist | disabled
      contextVisibility: "all", // all | allowlist | allowlist_quote
      heartbeat: {
        showOk: false,
        showAlerts: true,
        useIndicator: true,
      },
    },
  },
}
```

- `channels.defaults.groupPolicy`: 공급자 수준 `groupPolicy`가 설정되지 않았을 때의 대체 그룹 정책입니다.
- `channels.defaults.contextVisibility`: 모든 채널의 기본 보조 컨텍스트 가시성 모드입니다. 값: `all`(기본값, 인용/스레드/기록 컨텍스트를 모두 포함), `allowlist`(허용 목록 발신자의 컨텍스트만 포함), `allowlist_quote`(allowlist와 동일하지만 명시적 인용/답글 컨텍스트는 유지). 채널별 재정의: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: heartbeat 출력에 정상 채널 상태를 포함합니다.
- `channels.defaults.heartbeat.showAlerts`: heartbeat 출력에 성능 저하/오류 상태를 포함합니다.
- `channels.defaults.heartbeat.useIndicator`: 압축된 표시기 스타일 heartbeat 출력을 렌더링합니다.

### WhatsApp

WhatsApp은 gateway의 웹 채널(Baileys Web)을 통해 실행됩니다. 연결된 세션이 존재하면 자동으로 시작됩니다.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // 파란 체크(셀프 채팅 모드에서는 false)
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
  web: {
    enabled: true,
    heartbeatSeconds: 60,
    reconnect: {
      initialMs: 2000,
      maxMs: 120000,
      factor: 1.4,
      jitter: 0.2,
      maxAttempts: 0,
    },
  },
}
```

<Accordion title="다중 계정 WhatsApp">

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {},
        personal: {},
        biz: {
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

- 아웃바운드 명령은 `default` 계정이 있으면 기본적으로 해당 계정을 사용하고, 그렇지 않으면 정렬된 첫 번째 구성 계정 ID를 사용합니다.
- 선택적 `channels.whatsapp.defaultAccount`는 구성된 계정 ID와 일치하는 경우 해당 대체 기본 계정 선택을 재정의합니다.
- 레거시 단일 계정 Baileys 인증 디렉터리는 `openclaw doctor`에 의해 `whatsapp/default`로 마이그레이션됩니다.
- 계정별 재정의: `channels.whatsapp.accounts.<id>.sendReadReceipts`, `channels.whatsapp.accounts.<id>.dmPolicy`, `channels.whatsapp.accounts.<id>.allowFrom`.

</Accordion>

### Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "응답은 짧게 유지하세요.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "주제를 벗어나지 마세요.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Git 백업" },
        { command: "generate", description: "이미지 생성" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all | batched
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (기본값: off; 미리보기-편집 속도 제한을 피하려면 명시적으로 opt in)
      actions: { reactions: true, sendMessage: true },
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 100,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: {
        autoSelectFamily: true,
        dnsResultOrder: "ipv4first",
      },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- 봇 토큰: `channels.telegram.botToken` 또는 `channels.telegram.tokenFile`(일반 파일만 허용, symlink는 거부), 기본 계정에는 `TELEGRAM_BOT_TOKEN`이 대체값으로 사용됩니다.
- 선택적 `channels.telegram.defaultAccount`는 구성된 계정 ID와 일치하는 경우 기본 계정 선택을 재정의합니다.
- 다중 계정 구성(계정 ID 2개 이상)에서는 대체 라우팅을 피하려면 명시적 기본값(`channels.telegram.defaultAccount` 또는 `channels.telegram.accounts.default`)을 설정하세요. 누락되거나 잘못된 경우 `openclaw doctor`가 경고합니다.
- `configWrites: false`는 Telegram에서 시작된 구성 쓰기(슈퍼그룹 ID 마이그레이션, `/config set|unset`)를 차단합니다.
- `type: "acp"`를 가진 최상위 `bindings[]` 항목은 포럼 주제에 대한 영구 ACP 바인딩을 구성합니다(`match.peer.id`에는 정규 `chatId:topic:topicId` 사용). 필드 의미는 [ACP Agents](/ko/tools/acp-agents#channel-specific-settings)에서 공유됩니다.
- Telegram 스트림 미리보기는 `sendMessage` + `editMessageText`를 사용합니다(직접 채팅과 그룹 채팅 모두에서 작동).
- 재시도 정책: [Retry policy](/ko/concepts/retry)를 참고하세요.

### Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 100,
      allowBots: false,
      actions: {
        reactions: true,
        stickers: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        voiceStatus: true,
        events: true,
        moderation: false,
      },
      replyToMode: "off", // off | first | all | batched
      dmPolicy: "pairing",
      allowFrom: ["1234567890", "123456789012345678"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["openclaw-dm"] },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          ignoreOtherMentions: true,
          reactionNotifications: "own",
          users: ["987654321098765432"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["docs"],
              systemPrompt: "짧게만 답하세요.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress는 Discord에서 partial로 매핑됨)
      maxLinesPerMessage: 17,
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // `sessions_spawn({ thread: true })`에 대한 opt-in
      },
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
        },
      },
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["987654321098765432"],
        agentFilter: ["default"],
        sessionFilter: ["discord:"],
        target: "dm", // dm | channel | both
        cleanupAfterResolve: false,
      },
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

- 토큰: `channels.discord.token`, 기본 계정에는 `DISCORD_BOT_TOKEN`이 대체값으로 사용됩니다.
- 명시적 Discord `token`을 제공하는 직접 아웃바운드 호출은 해당 토큰으로 호출을 수행합니다. 계정 재시도/정책 설정은 활성 런타임 스냅샷에서 선택된 계정에서 계속 가져옵니다.
- 선택적 `channels.discord.defaultAccount`는 구성된 계정 ID와 일치하는 경우 기본 계정 선택을 재정의합니다.
- 전달 대상에는 `user:<id>`(DM) 또는 `channel:<id>`(guild 채널)를 사용하세요. 숫자 ID만 있는 형식은 거부됩니다.
- Guild slug는 소문자이며 공백은 `-`로 대체됩니다. 채널 키는 slug 처리된 이름(`#` 없음)을 사용합니다. 가능하면 guild ID를 사용하세요.
- 봇이 작성한 메시지는 기본적으로 무시됩니다. `allowBots: true`는 이를 활성화합니다. `allowBots: "mentions"`를 사용하면 봇을 멘션한 봇 메시지만 허용합니다(자기 메시지는 여전히 필터링됨).
- `channels.discord.guilds.<id>.ignoreOtherMentions`(및 채널 재정의)는 봇은 멘션하지 않고 다른 사용자나 역할을 멘션한 메시지를 삭제합니다(@everyone/@here 제외).
- `maxLinesPerMessage`(기본값 17)는 2000자를 넘지 않아도 긴 메시지를 분할합니다.
- `channels.discord.threadBindings`는 Discord 스레드 바운드 라우팅을 제어합니다:
  - `enabled`: 스레드 바운드 세션 기능(`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`, 바운드 전달/라우팅)에 대한 Discord 재정의
  - `idleHours`: 비활성 자동 unfocus 시간 단위 재정의(`0`은 비활성화)
  - `maxAgeHours`: 하드 최대 사용 기간 시간 단위 재정의(`0`은 비활성화)
  - `spawnSubagentSessions`: `sessions_spawn({ thread: true })` 자동 스레드 생성/바인딩에 대한 opt-in 스위치
- `type: "acp"`를 가진 최상위 `bindings[]` 항목은 채널과 스레드에 대한 영구 ACP 바인딩을 구성합니다(`match.peer.id`에 채널/스레드 ID 사용). 필드 의미는 [ACP Agents](/ko/tools/acp-agents#channel-specific-settings)에서 공유됩니다.
- `channels.discord.ui.components.accentColor`는 Discord components v2 컨테이너의 강조 색상을 설정합니다.
- `channels.discord.voice`는 Discord 음성 채널 대화와 선택적 자동 참여 + TTS 재정의를 활성화합니다.
- `channels.discord.voice.daveEncryption` 및 `channels.discord.voice.decryptionFailureTolerance`는 `@discordjs/voice` DAVE 옵션으로 전달됩니다(기본값은 각각 `true`, `24`).
- OpenClaw는 반복적인 복호화 실패 후 음성 세션을 나갔다가 다시 참여하여 음성 수신 복구도 시도합니다.
- `channels.discord.streaming`은 정규 스트림 모드 키입니다. 레거시 `streamMode` 및 불리언 `streaming` 값은 자동 마이그레이션됩니다.
- `channels.discord.autoPresence`는 런타임 가용성을 봇 presence에 매핑합니다(정상 => online, 성능 저하 => idle, 소진 => dnd) 그리고 선택적 상태 텍스트 재정의를 허용합니다.
- `channels.discord.dangerouslyAllowNameMatching`는 변경 가능한 이름/태그 매칭을 다시 활성화합니다(비상 호환 모드).
- `channels.discord.execApprovals`: Discord 네이티브 exec 승인 전달 및 승인자 권한 부여.
  - `enabled`: `true`, `false`, 또는 `"auto"`(기본값). auto 모드에서는 승인자를 `approvers` 또는 `commands.ownerAllowFrom`에서 해석할 수 있을 때 exec 승인이 활성화됩니다.
  - `approvers`: exec 요청을 승인할 수 있는 Discord 사용자 ID입니다. 생략되면 `commands.ownerAllowFrom`을 대체값으로 사용합니다.
  - `agentFilter`: 선택적 에이전트 ID 허용 목록입니다. 생략하면 모든 에이전트에 대한 승인을 전달합니다.
  - `sessionFilter`: 선택적 세션 키 패턴(부분 문자열 또는 regex)입니다.
  - `target`: 승인 프롬프트를 보낼 위치입니다. `"dm"`(기본값)은 승인자 DM으로, `"channel"`은 원래 채널로, `"both"`는 둘 다로 보냅니다. target에 `"channel"`이 포함되면 버튼은 해석된 승인자만 사용할 수 있습니다.
  - `cleanupAfterResolve`: `true`이면 승인, 거부, 타임아웃 후 승인 DM을 삭제합니다.

**반응 알림 모드:** `off`(없음), `own`(봇의 메시지, 기본값), `all`(모든 메시지), `allowlist`(`guilds.<id>.users`의 모든 메시지).

### Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": { allow: true, requireMention: true },
      },
      actions: { reactions: true },
      typingIndicator: "message",
      mediaMaxMb: 20,
    },
  },
}
```

- 서비스 계정 JSON: 인라인(`serviceAccount`) 또는 파일 기반(`serviceAccountFile`)입니다.
- 서비스 계정 SecretRef도 지원됩니다(`serviceAccountRef`).
- env 대체값: `GOOGLE_CHAT_SERVICE_ACCOUNT` 또는 `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- 전달 대상에는 `spaces/<spaceId>` 또는 `users/<userId>`를 사용하세요.
- `channels.googlechat.dangerouslyAllowNameMatching`는 변경 가능한 이메일 principal 매칭을 다시 활성화합니다(비상 호환 모드).

### Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
      dmPolicy: "pairing",
      allowFrom: ["U123", "U456", "*"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["G123"] },
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          allowBots: false,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "짧게만 답하세요.",
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off", // off | first | all | batched
      thread: {
        historyScope: "thread", // thread | channel
        inheritParent: false,
      },
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },
      slashCommand: {
        enabled: true,
        name: "openclaw",
        sessionPrefix: "slack:slash",
        ephemeral: true,
      },
      typingReaction: "hourglass_flowing_sand",
      textChunkLimit: 4000,
      chunkMode: "length",
      streaming: {
        mode: "partial", // off | partial | block | progress
        nativeTransport: true, // mode=partial일 때 Slack 네이티브 스트리밍 API 사용
      },
      mediaMaxMb: 20,
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["U123"],
        agentFilter: ["default"],
        sessionFilter: ["slack:"],
        target: "dm", // dm | channel | both
      },
    },
  },
}
```

- **Socket mode**에는 `botToken`과 `appToken`이 모두 필요합니다(기본 계정 env 대체값은 `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN`).
- **HTTP mode**에는 `botToken`과 `signingSecret`(루트 또는 계정별)이 필요합니다.
- `botToken`, `appToken`, `signingSecret`, `userToken`은 일반 텍스트 문자열 또는 SecretRef 객체를 받을 수 있습니다.
- Slack 계정 스냅샷은 `botTokenSource`, `botTokenStatus`, `appTokenStatus`, 그리고 HTTP mode에서는 `signingSecretStatus`와 같은 자격 증명별 소스/상태 필드를 노출합니다. `configured_unavailable`은 해당 계정이 SecretRef를 통해 구성되었지만 현재 명령/런타임 경로에서 비밀 값을 해석할 수 없었음을 의미합니다.
- `configWrites: false`는 Slack에서 시작된 구성 쓰기를 차단합니다.
- 선택적 `channels.slack.defaultAccount`는 구성된 계정 ID와 일치하는 경우 기본 계정 선택을 재정의합니다.
- `channels.slack.streaming.mode`는 정규 Slack 스트림 모드 키입니다. `channels.slack.streaming.nativeTransport`는 Slack의 네이티브 스트리밍 전송을 제어합니다. 레거시 `streamMode`, 불리언 `streaming`, `nativeStreaming` 값은 자동 마이그레이션됩니다.
- 전달 대상에는 `user:<id>`(DM) 또는 `channel:<id>`를 사용하세요.

**반응 알림 모드:** `off`, `own`(기본값), `all`, `allowlist`(`reactionAllowlist`에서 가져옴).

**스레드 세션 격리:** `thread.historyScope`는 스레드별(기본값) 또는 채널 전체 공유입니다. `thread.inheritParent`는 부모 채널 대화 기록을 새 스레드로 복사합니다.

- Slack 네이티브 스트리밍과 Slack assistant 스타일의 "입력 중..." 스레드 상태는 답글 스레드 대상을 요구합니다. 최상위 DM은 기본적으로 스레드 밖으로 유지되므로, 스레드 스타일 미리보기 대신 `typingReaction` 또는 일반 전달을 사용합니다.
- `typingReaction`은 답글이 실행되는 동안 수신 Slack 메시지에 임시 반응을 추가하고, 완료 시 제거합니다. `"hourglass_flowing_sand"`와 같은 Slack 이모지 shortcode를 사용하세요.
- `channels.slack.execApprovals`: Slack 네이티브 exec 승인 전달 및 승인자 권한 부여. 스키마는 Discord와 동일합니다: `enabled` (`true`/`false`/`"auto"`), `approvers`(Slack 사용자 ID), `agentFilter`, `sessionFilter`, `target` (`"dm"`, `"channel"`, 또는 `"both"`).

| 작업 그룹   | 기본값  | 참고                   |
| ----------- | ------- | ---------------------- |
| reactions   | 활성화  | 반응 추가 + 반응 목록  |
| messages    | 활성화  | 읽기/보내기/편집/삭제  |
| pins        | 활성화  | 고정/해제/목록         |
| memberInfo  | 활성화  | 멤버 정보              |
| emojiList   | 활성화  | 커스텀 이모지 목록     |

### Mattermost

Mattermost는 플러그인으로 제공됩니다: `openclaw plugins install @openclaw/mattermost`.

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
      chatmode: "oncall", // oncall | onmessage | onchar
      oncharPrefixes: [">", "!"],
      groups: {
        "*": { requireMention: true },
        "team-channel-id": { requireMention: false },
      },
      commands: {
        native: true, // opt-in
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // 리버스 프록시/공개 배포를 위한 선택적 명시적 URL
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

채팅 모드: `oncall`(@-멘션 시 응답, 기본값), `onmessage`(모든 메시지), `onchar`(트리거 접두사로 시작하는 메시지).

Mattermost 네이티브 명령이 활성화되면:

- `commands.callbackPath`는 전체 URL이 아니라 경로여야 합니다(예: `/api/channels/mattermost/command`).
- `commands.callbackUrl`은 OpenClaw gateway 엔드포인트로 해석되어야 하며 Mattermost 서버에서 접근 가능해야 합니다.
- 네이티브 slash callback은 slash 명령 등록 중 Mattermost가 반환한 명령별 토큰으로 인증됩니다. 등록에 실패하거나 활성화된 명령이 없으면 OpenClaw는 `Unauthorized: invalid command token.`으로 callback을 거부합니다.
- 비공개/tailnet/내부 callback 호스트의 경우, Mattermost는 callback 호스트/도메인을 포함하도록 `ServiceSettings.AllowedUntrustedInternalConnections`가 필요할 수 있습니다.
  전체 URL이 아니라 호스트/도메인 값을 사용하세요.
- `channels.mattermost.configWrites`: Mattermost에서 시작된 구성 쓰기를 허용하거나 거부합니다.
- `channels.mattermost.requireMention`: 채널에서 응답하기 전에 `@mention`을 요구합니다.
- `channels.mattermost.groups.<channelId>.requireMention`: 채널별 멘션 게이팅 재정의(`"*"`는 기본값).
- 선택적 `channels.mattermost.defaultAccount`는 구성된 계정 ID와 일치하는 경우 기본 계정 선택을 재정의합니다.

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // 선택적 계정 바인딩
      dmPolicy: "pairing",
      allowFrom: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      configWrites: true,
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50,
    },
  },
}
```

**반응 알림 모드:** `off`, `own`(기본값), `all`, `allowlist`(`reactionAllowlist`에서 가져옴).

- `channels.signal.account`: 채널 시작을 특정 Signal 계정 식별자에 고정합니다.
- `channels.signal.configWrites`: Signal에서 시작된 구성 쓰기를 허용하거나 거부합니다.
- 선택적 `channels.signal.defaultAccount`는 구성된 계정 ID와 일치하는 경우 기본 계정 선택을 재정의합니다.

### BlueBubbles

BlueBubbles는 권장되는 iMessage 경로입니다(플러그인 기반, `channels.bluebubbles` 아래에서 구성).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, 그룹 제어 및 고급 작업:
      // /channels/bluebubbles 참고
    },
  },
}
```

- 여기에서 다루는 핵심 키 경로: `channels.bluebubbles`, `channels.bluebubbles.dmPolicy`.
- 선택적 `channels.bluebubbles.defaultAccount`는 구성된 계정 ID와 일치하는 경우 기본 계정 선택을 재정의합니다.
- `type: "acp"`를 가진 최상위 `bindings[]` 항목은 BlueBubbles 대화를 영구 ACP 세션에 바인딩할 수 있습니다. `match.peer.id`에는 BlueBubbles handle 또는 대상 문자열(`chat_id:*`, `chat_guid:*`, `chat_identifier:*`)을 사용하세요. 공유 필드 의미: [ACP Agents](/ko/tools/acp-agents#channel-specific-settings).
- 전체 BlueBubbles 채널 구성은 [BlueBubbles](/ko/channels/bluebubbles)에 문서화되어 있습니다.

### iMessage

OpenClaw는 `imsg rpc`(stdio를 통한 JSON-RPC)를 생성합니다. 데몬이나 포트는 필요하지 않습니다.

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host",
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],
      historyLimit: 50,
      includeAttachments: false,
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    },
  },
}
```

- 선택적 `channels.imessage.defaultAccount`는 구성된 계정 ID와 일치하는 경우 기본 계정 선택을 재정의합니다.

- Messages DB에 대한 Full Disk Access가 필요합니다.
- `chat_id:<id>` 대상을 선호하세요. 채팅을 나열하려면 `imsg chats --limit 20`을 사용하세요.
- `cliPath`는 SSH wrapper를 가리킬 수 있으며, SCP 첨부 파일 가져오기를 위해 `remoteHost`(`host` 또는 `user@host`)를 설정하세요.
- `attachmentRoots` 및 `remoteAttachmentRoots`는 수신 첨부 파일 경로를 제한합니다(기본값: `/Users/*/Library/Messages/Attachments`).
- SCP는 strict host-key checking을 사용하므로, 릴레이 호스트 키가 이미 `~/.ssh/known_hosts`에 존재하는지 확인하세요.
- `channels.imessage.configWrites`: iMessage에서 시작된 구성 쓰기를 허용하거나 거부합니다.
- `type: "acp"`를 가진 최상위 `bindings[]` 항목은 iMessage 대화를 영구 ACP 세션에 바인딩할 수 있습니다. `match.peer.id`에는 정규화된 handle 또는 명시적 채팅 대상(`chat_id:*`, `chat_guid:*`, `chat_identifier:*`)을 사용하세요. 공유 필드 의미: [ACP Agents](/ko/tools/acp-agents#channel-specific-settings).

<Accordion title="iMessage SSH wrapper 예제">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix는 확장 기반이며 `channels.matrix` 아래에서 구성됩니다.

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
      encryption: true,
      initialSyncLimit: 20,
      defaultAccount: "ops",
      accounts: {
        ops: {
          name: "Ops",
          userId: "@ops:example.org",
          accessToken: "syt_ops_xxx",
        },
        alerts: {
          userId: "@alerts:example.org",
          password: "secret",
          proxy: "http://127.0.0.1:7891",
        },
      },
    },
  },
}
```

- 토큰 인증은 `accessToken`을 사용하고, 비밀번호 인증은 `userId` + `password`를 사용합니다.
- `channels.matrix.proxy`는 Matrix HTTP 트래픽을 명시적 HTTP(S) 프록시를 통해 라우팅합니다. 명명된 계정은 `channels.matrix.accounts.<id>.proxy`로 이를 재정의할 수 있습니다.
- `channels.matrix.network.dangerouslyAllowPrivateNetwork`는 비공개/내부 homeserver를 허용합니다. `proxy`와 이 네트워크 opt-in은 서로 독립적인 제어입니다.
- `channels.matrix.defaultAccount`는 다중 계정 구성에서 선호 계정을 선택합니다.
- `channels.matrix.autoJoin`의 기본값은 `off`이므로, `autoJoin: "allowlist"`와 `autoJoinAllowlist`를 설정하거나 `autoJoin: "always"`를 설정하기 전까지 초대된 룸과 새 DM 스타일 초대는 무시됩니다.
- `channels.matrix.execApprovals`: Matrix 네이티브 exec 승인 전달 및 승인자 권한 부여.
  - `enabled`: `true`, `false`, 또는 `"auto"`(기본값). auto 모드에서는 승인자를 `approvers` 또는 `commands.ownerAllowFrom`에서 해석할 수 있을 때 exec 승인이 활성화됩니다.
  - `approvers`: exec 요청을 승인할 수 있는 Matrix 사용자 ID(예: `@owner:example.org`)입니다.
  - `agentFilter`: 선택적 에이전트 ID 허용 목록입니다. 생략하면 모든 에이전트에 대한 승인을 전달합니다.
  - `sessionFilter`: 선택적 세션 키 패턴(부분 문자열 또는 regex)입니다.
  - `target`: 승인 프롬프트를 보낼 위치입니다. `"dm"`(기본값), `"channel"`(원래 룸), 또는 `"both"`.
  - 계정별 재정의: `channels.matrix.accounts.<id>.execApprovals`.
- `channels.matrix.dm.sessionScope`는 Matrix DM이 세션으로 그룹화되는 방식을 제어합니다: `per-user`(기본값)는 라우팅된 peer 기준으로 공유하고, `per-room`은 각 DM 룸을 격리합니다.
- Matrix 상태 프로브와 라이브 디렉터리 조회는 런타임 트래픽과 동일한 프록시 정책을 사용합니다.
- 전체 Matrix 구성, 대상 지정 규칙, 설정 예시는 [Matrix](/ko/channels/matrix)에 문서화되어 있습니다.

### Microsoft Teams

Microsoft Teams는 확장 기반이며 `channels.msteams` 아래에서 구성됩니다.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, 팀/채널 정책:
      // /channels/msteams 참고
    },
  },
}
```

- 여기에서 다루는 핵심 키 경로: `channels.msteams`, `channels.msteams.configWrites`.
- 전체 Teams 구성(자격 증명, webhook, DM/그룹 정책, 팀별/채널별 재정의)은 [Microsoft Teams](/ko/channels/msteams)에 문서화되어 있습니다.

### IRC

IRC는 확장 기반이며 `channels.irc` 아래에서 구성됩니다.

```json5
{
  channels: {
    irc: {
      enabled: true,
      dmPolicy: "pairing",
      configWrites: true,
      nickserv: {
        enabled: true,
        service: "NickServ",
        password: "${IRC_NICKSERV_PASSWORD}",
        register: false,
        registerEmail: "bot@example.com",
      },
    },
  },
}
```

- 여기에서 다루는 핵심 키 경로: `channels.irc`, `channels.irc.dmPolicy`, `channels.irc.configWrites`, `channels.irc.nickserv.*`.
- 선택적 `channels.irc.defaultAccount`는 구성된 계정 ID와 일치하는 경우 기본 계정 선택을 재정의합니다.
- 전체 IRC 채널 구성(호스트/포트/TLS/채널/허용 목록/멘션 게이팅)은 [IRC](/ko/channels/irc)에 문서화되어 있습니다.

### 다중 계정(모든 채널)

채널별로 여러 계정을 실행합니다(각각 고유한 `accountId` 사용):

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "주 봇",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "알림 봇",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- `default`는 `accountId`가 생략되었을 때 사용됩니다(CLI + 라우팅).
- env 토큰은 **default** 계정에만 적용됩니다.
- 기본 채널 설정은 계정별로 재정의되지 않는 한 모든 계정에 적용됩니다.
- `bindings[].match.accountId`를 사용해 각 계정을 다른 에이전트로 라우팅하세요.
- 아직 단일 계정 최상위 채널 구성 상태에서 `openclaw channels add`(또는 채널 온보딩)를 통해 비기본 계정을 추가하면, OpenClaw는 먼저 계정 범위의 최상위 단일 계정 값을 채널 계정 맵으로 승격하여 원래 계정이 계속 작동하게 합니다. 대부분의 채널은 이를 `channels.<channel>.accounts.default`로 옮기며, Matrix는 기존의 일치하는 명명/default 대상을 대신 유지할 수 있습니다.
- 기존 채널 전용 바인딩(`accountId` 없음)은 기본 계정과 계속 일치하며, 계정 범위 바인딩은 여전히 선택 사항입니다.
- `openclaw doctor --fix`도 계정 범위의 최상위 단일 계정 값을 해당 채널에 대해 선택된 승격 계정으로 옮겨 혼합 형태를 복구합니다. 대부분의 채널은 `accounts.default`를 사용하고, Matrix는 기존의 일치하는 명명/default 대상을 유지할 수 있습니다.

### 기타 확장 채널

많은 확장 채널은 `channels.<id>`로 구성되며 전용 채널 페이지에 문서화되어 있습니다(예: Feishu, Matrix, LINE, Nostr, Zalo, Nextcloud Talk, Synology Chat, Twitch).
전체 채널 인덱스는 [Channels](/ko/channels)를 참고하세요.

### 그룹 채팅 멘션 게이팅

그룹 메시지는 기본적으로 **멘션 필요**(메타데이터 멘션 또는 안전한 regex 패턴)입니다. WhatsApp, Telegram, Discord, Google Chat, iMessage 그룹 채팅에 적용됩니다.

**멘션 유형:**

- **메타데이터 멘션**: 네이티브 플랫폼 @-멘션. WhatsApp 셀프 채팅 모드에서는 무시됩니다.
- **텍스트 패턴**: `agents.list[].groupChat.mentionPatterns`의 안전한 regex 패턴. 잘못된 패턴과 안전하지 않은 중첩 반복은 무시됩니다.
- 멘션 게이팅은 감지가 가능한 경우에만 적용됩니다(네이티브 멘션 또는 패턴이 최소 하나 이상).

```json5
{
  messages: {
    groupChat: { historyLimit: 50 },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw", "openclaw"] } }],
  },
}
```

`messages.groupChat.historyLimit`는 전역 기본값을 설정합니다. 채널은 `channels.<channel>.historyLimit`(또는 계정별)로 재정의할 수 있습니다. 비활성화하려면 `0`으로 설정하세요.

#### DM 기록 제한

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30,
      dms: {
        "123456789": { historyLimit: 50 },
      },
    },
  },
}
```

해석 순서: DM별 재정의 → 공급자 기본값 → 제한 없음(모두 유지).

지원 대상: `telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

#### 셀프 채팅 모드

자기 번호를 `allowFrom`에 포함해 셀프 채팅 모드를 활성화합니다(네이티브 @-멘션은 무시하고, 텍스트 패턴에만 응답함):

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: { mentionPatterns: ["reisponde", "@openclaw"] },
      },
    ],
  },
}
```

### 명령(채팅 명령 처리)

```json5
{
  commands: {
    native: "auto", // 지원될 때 네이티브 명령 등록
    nativeSkills: "auto", // 지원될 때 네이티브 skill 명령 등록
    text: true, // 채팅 메시지에서 /commands 구문 분석
    bash: false, // ! 허용(별칭: /bash)
    bashForegroundMs: 2000,
    config: false, // /config 허용
    mcp: false, // /mcp 허용
    plugins: false, // /plugins 허용
    debug: false, // /debug 허용
    restart: true, // /restart + gateway 재시작 tool 허용
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw", // raw | hash
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="명령 세부 정보">

- 이 블록은 명령 표면을 구성합니다. 현재 내장 + 번들 명령 카탈로그는 [Slash Commands](/ko/tools/slash-commands)를 참고하세요.
- 이 페이지는 전체 명령 카탈로그가 아니라 **구성 키 참조**입니다. QQ Bot `/bot-ping` `/bot-help` `/bot-logs`, LINE `/card`, device-pair `/pair`, memory `/dreaming`, phone-control `/phone`, Talk `/voice`와 같은 채널/플러그인 소유 명령은 해당 채널/플러그인 페이지와 [Slash Commands](/ko/tools/slash-commands)에 문서화되어 있습니다.
- 텍스트 명령은 선행 `/`가 있는 **독립 실행형** 메시지여야 합니다.
- `native: "auto"`는 Discord/Telegram에서 네이티브 명령을 켜고, Slack에서는 끕니다.
- `nativeSkills: "auto"`는 Discord/Telegram에서 네이티브 skill 명령을 켜고, Slack에서는 끕니다.
- 채널별 재정의: `channels.discord.commands.native`(bool 또는 `"auto"`). `false`는 이전에 등록된 명령을 지웁니다.
- 네이티브 skill 등록은 `channels.<provider>.commands.nativeSkills`로 채널별 재정의할 수 있습니다.
- `channels.telegram.customCommands`는 추가 Telegram 봇 메뉴 항목을 추가합니다.
- `bash: true`는 호스트 셸용 `! <cmd>`를 활성화합니다. `tools.elevated.enabled`가 필요하며 발신자가 `tools.elevated.allowFrom.<channel>`에 있어야 합니다.
- `config: true`는 `/config`를 활성화합니다(`openclaw.json` 읽기/쓰기). gateway `chat.send` 클라이언트의 경우, 영구 `/config set|unset` 쓰기에는 `operator.admin`도 필요하며, 읽기 전용 `/config show`는 일반 쓰기 범위 operator 클라이언트에도 계속 제공됩니다.
- `mcp: true`는 `mcp.servers` 아래 OpenClaw 관리 MCP 서버 구성을 위한 `/mcp`를 활성화합니다.
- `plugins: true`는 플러그인 검색, 설치, 활성화/비활성화 제어를 위한 `/plugins`를 활성화합니다.
- `channels.<provider>.configWrites`는 채널별 구성 변경을 제어합니다(기본값: true).
- 다중 계정 채널의 경우 `channels.<provider>.accounts.<id>.configWrites`도 해당 계정을 대상으로 하는 쓰기(예: `/allowlist --config --account <id>` 또는 `/config set channels.<provider>.accounts.<id>...`)를 제어합니다.
- `restart: false`는 `/restart`와 gateway 재시작 tool 작업을 비활성화합니다. 기본값: `true`.
- `ownerAllowFrom`은 소유자 전용 명령/tool을 위한 명시적 소유자 허용 목록입니다. `allowFrom`과는 별개입니다.
- `ownerDisplay: "hash"`는 시스템 프롬프트에서 소유자 ID를 해시합니다. 해싱을 제어하려면 `ownerDisplaySecret`을 설정하세요.
- `allowFrom`은 공급자별입니다. 설정되면 이것이 **유일한** 권한 부여 소스가 됩니다(채널 허용 목록/페어링 및 `useAccessGroups`는 무시됨).
- `useAccessGroups: false`는 `allowFrom`이 설정되지 않았을 때 명령이 액세스 그룹 정책을 우회하도록 허용합니다.
- 명령 문서 맵:
  - 내장 + 번들 카탈로그: [Slash Commands](/ko/tools/slash-commands)
  - 채널별 명령 표면: [Channels](/ko/channels)
  - QQ Bot 명령: [QQ Bot](/ko/channels/qqbot)
  - 페어링 명령: [Pairing](/ko/channels/pairing)
  - LINE 카드 명령: [LINE](/ko/channels/line)
  - memory dreaming: [Dreaming](/ko/concepts/dreaming)

</Accordion>

---

## 에이전트 기본값

### `agents.defaults.workspace`

기본값: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

시스템 프롬프트의 Runtime 줄에 표시되는 선택적 리포지토리 루트입니다. 설정되지 않으면 OpenClaw가 workspace에서 위쪽으로 이동하며 자동 감지합니다.

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

`agents.list[].skills`를 설정하지 않은 에이전트를 위한 선택적 기본 skill 허용 목록입니다.

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // github, weather 상속
      { id: "docs", skills: ["docs-search"] }, // 기본값 대체
      { id: "locked-down", skills: [] }, // skill 없음
    ],
  },
}
```

- 기본적으로 제한 없는 skill을 원하면 `agents.defaults.skills`를 생략하세요.
- 기본값을 상속하려면 `agents.list[].skills`를 생략하세요.
- skill이 없게 하려면 `agents.list[].skills: []`를 설정하세요.
- 비어 있지 않은 `agents.list[].skills` 목록은 해당 에이전트의 최종 집합이며, 기본값과 병합되지 않습니다.

### `agents.defaults.skipBootstrap`

workspace bootstrap 파일(`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`)의 자동 생성을 비활성화합니다.

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

workspace bootstrap 파일이 시스템 프롬프트에 삽입되는 시점을 제어합니다. 기본값은 `"always"`입니다.

- `"continuation-skip"`: 안전한 연속 턴(완료된 assistant 응답 이후)에서는 workspace bootstrap 재삽입을 건너뛰어 프롬프트 크기를 줄입니다. Heartbeat 실행과 compaction 이후 재시도는 여전히 컨텍스트를 다시 빌드합니다.

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

잘리기 전 workspace bootstrap 파일당 최대 문자 수입니다. 기본값: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

모든 workspace bootstrap 파일에 걸쳐 삽입되는 총 최대 문자 수입니다. 기본값: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

bootstrap 컨텍스트가 잘렸을 때 에이전트에게 보이는 경고 텍스트를 제어합니다.
기본값: `"once"`.

- `"off"`: 시스템 프롬프트에 경고 텍스트를 절대 삽입하지 않습니다.
- `"once"`: 고유한 잘림 시그니처당 한 번 경고를 삽입합니다(권장).
- `"always"`: 잘림이 존재하면 매 실행마다 경고를 삽입합니다.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

공급자 호출 전에 대화 기록/tool 이미지 블록에서 가장 긴 이미지 변의 최대 픽셀 크기입니다.
기본값: `1200`.

값을 낮추면 일반적으로 스크린샷이 많은 실행에서 vision 토큰 사용량과 요청 페이로드 크기가 줄어듭니다.
값을 높이면 더 많은 시각적 디테일이 보존됩니다.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

시스템 프롬프트 컨텍스트용 시간대입니다(메시지 타임스탬프용 아님). 호스트 시간대를 대체값으로 사용합니다.

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

시스템 프롬프트의 시간 형식입니다. 기본값: `auto`(OS 환경설정).

```json5
{
  agents: { defaults: { timeFormat: "auto" } }, // auto | 12 | 24
}
```

### `agents.defaults.model`

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview"],
      },
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-i2v"],
      },
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4-mini"],
      },
      params: { cacheRetention: "long" }, // 전역 기본 provider params
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

- `model`: 문자열(`"provider/model"`) 또는 객체(`{ primary, fallbacks }`)를 받을 수 있습니다.
  - 문자열 형식은 primary 모델만 설정합니다.
  - 객체 형식은 primary와 순서가 있는 failover 모델을 설정합니다.
- `imageModel`: 문자열(`"provider/model"`) 또는 객체(`{ primary, fallbacks }`)를 받을 수 있습니다.
  - `image` tool 경로의 vision 모델 구성으로 사용됩니다.
  - 선택된/기본 모델이 이미지 입력을 받을 수 없을 때 대체 라우팅에도 사용됩니다.
- `imageGenerationModel`: 문자열(`"provider/model"`) 또는 객체(`{ primary, fallbacks }`)를 받을 수 있습니다.
  - 공유 이미지 생성 기능과 이미지를 생성하는 향후 tool/플러그인 표면에서 사용됩니다.
  - 일반적인 값: Gemini 네이티브 이미지 생성을 위한 `google/gemini-3.1-flash-image-preview`, fal용 `fal/fal-ai/flux/dev`, OpenAI Images용 `openai/gpt-image-1`.
  - provider/model을 직접 선택하면 일치하는 provider 인증/API 키도 구성하세요(예: `google/*`에는 `GEMINI_API_KEY` 또는 `GOOGLE_API_KEY`, `openai/*`에는 `OPENAI_API_KEY`, `fal/*`에는 `FAL_KEY`).
  - 생략해도 `image_generate`는 인증이 설정된 provider 기본값을 추론할 수 있습니다. 먼저 현재 기본 provider를 시도하고, 그다음 provider ID 순으로 나머지 등록된 이미지 생성 provider를 시도합니다.
- `musicGenerationModel`: 문자열(`"provider/model"`) 또는 객체(`{ primary, fallbacks }`)를 받을 수 있습니다.
  - 공유 음악 생성 기능과 내장 `music_generate` tool에서 사용됩니다.
  - 일반적인 값: `google/lyria-3-clip-preview`, `google/lyria-3-pro-preview`, 또는 `minimax/music-2.5+`.
  - 생략해도 `music_generate`는 인증이 설정된 provider 기본값을 추론할 수 있습니다. 먼저 현재 기본 provider를 시도하고, 그다음 provider ID 순으로 나머지 등록된 음악 생성 provider를 시도합니다.
  - provider/model을 직접 선택하면 일치하는 provider 인증/API 키도 구성하세요.
- `videoGenerationModel`: 문자열(`"provider/model"`) 또는 객체(`{ primary, fallbacks }`)를 받을 수 있습니다.
  - 공유 비디오 생성 기능과 내장 `video_generate` tool에서 사용됩니다.
  - 일반적인 값: `qwen/wan2.6-t2v`, `qwen/wan2.6-i2v`, `qwen/wan2.6-r2v`, `qwen/wan2.6-r2v-flash`, 또는 `qwen/wan2.7-r2v`.
  - 생략해도 `video_generate`는 인증이 설정된 provider 기본값을 추론할 수 있습니다. 먼저 현재 기본 provider를 시도하고, 그다음 provider ID 순으로 나머지 등록된 비디오 생성 provider를 시도합니다.
  - provider/model을 직접 선택하면 일치하는 provider 인증/API 키도 구성하세요.
  - 번들 Qwen 비디오 생성 provider는 현재 최대 출력 비디오 1개, 입력 이미지 1개, 입력 비디오 4개, 10초 길이, 그리고 provider 수준 `size`, `aspectRatio`, `resolution`, `audio`, `watermark` 옵션을 지원합니다.
- `pdfModel`: 문자열(`"provider/model"`) 또는 객체(`{ primary, fallbacks }`)를 받을 수 있습니다.
  - `pdf` tool의 모델 라우팅에 사용됩니다.
  - 생략하면 PDF tool은 `imageModel`, 그다음 해석된 세션/기본 모델로 대체됩니다.
- `pdfMaxBytesMb`: 호출 시점에 `maxBytesMb`가 전달되지 않았을 때 `pdf` tool의 기본 PDF 크기 제한입니다.
- `pdfMaxPages`: `pdf` tool의 추출 대체 모드에서 고려하는 기본 최대 페이지 수입니다.
- `verboseDefault`: 에이전트의 기본 verbose 수준입니다. 값: `"off"`, `"on"`, `"full"`. 기본값: `"off"`.
- `elevatedDefault`: 에이전트의 기본 elevated-output 수준입니다. 값: `"off"`, `"on"`, `"ask"`, `"full"`. 기본값: `"on"`.
- `model.primary`: 형식은 `provider/model`(예: `openai/gpt-5.4`)입니다. provider를 생략하면 OpenClaw는 먼저 별칭을 시도하고, 그다음 정확히 그 모델 ID에 대해 고유하게 구성된 provider 일치를 찾으며, 그 후에야 구성된 기본 provider로 대체됩니다(더 이상 권장되지 않는 호환 동작이므로 명시적 `provider/model`을 권장). 해당 provider가 더 이상 구성된 기본 모델을 노출하지 않으면, OpenClaw는 오래된 제거된 provider 기본값을 표시하는 대신 첫 번째 구성된 provider/model으로 대체됩니다.
- `models`: `/model`용 구성된 모델 카탈로그 및 허용 목록입니다. 각 항목은 `alias`(단축키)와 `params`(예: `temperature`, `maxTokens`, `cacheRetention`, `context1m` 같은 provider별 값)를 포함할 수 있습니다.
- `params`: 모든 모델에 적용되는 전역 기본 provider 매개변수입니다. `agents.defaults.params`에서 설정합니다(예: `{ cacheRetention: "long" }`).
- `params` 병합 우선순위(구성): `agents.defaults.params`(전역 기본) 위에 `agents.defaults.models["provider/model"].params`(모델별), 그다음 `agents.list[].params`(일치하는 에이전트 ID)가 키별로 덮어씁니다. 자세한 내용은 [Prompt Caching](/ko/reference/prompt-caching)을 참고하세요.
- 이러한 필드를 변경하는 구성 작성기(예: `/models set`, `/models set-image`, fallback 추가/제거 명령)는 정규 객체 형식으로 저장하고 가능하면 기존 fallback 목록을 보존합니다.
- `maxConcurrent`: 세션 전반에서 병렬 에이전트 실행의 최대 수입니다(각 세션은 여전히 직렬화됨). 기본값: 4.

**내장 별칭 단축키** (`agents.defaults.models`에 모델이 있을 때만 적용):

| 별칭                | 모델                                   |
| ------------------- | -------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`            |
| `sonnet`            | `anthropic/claude-sonnet-4-6`          |
| `gpt`               | `openai/gpt-5.4`                       |
| `gpt-mini`          | `openai/gpt-5.4-mini`                  |
| `gpt-nano`          | `openai/gpt-5.4-nano`                  |
| `gemini`            | `google/gemini-3.1-pro-preview`        |
| `gemini-flash`      | `google/gemini-3-flash-preview`        |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

구성한 별칭은 항상 기본값보다 우선합니다.

Z.AI GLM-4.x 모델은 `--thinking off`를 설정하거나 `agents.defaults.models["zai/<model>"].params.thinking`을 직접 정의하지 않는 한 thinking 모드를 자동으로 활성화합니다.
Z.AI 모델은 기본적으로 tool 호출 스트리밍을 위해 `tool_stream`을 활성화합니다. 비활성화하려면 `agents.defaults.models["zai/<model>"].params.tool_stream`을 `false`로 설정하세요.
Anthropic Claude 4.6 모델은 명시적 thinking 수준이 설정되지 않았을 때 기본적으로 `adaptive` thinking을 사용합니다.

### `agents.defaults.cliBackends`

텍스트 전용 대체 실행(도구 호출 없음)을 위한 선택적 CLI 백엔드입니다. API provider가 실패할 때 백업으로 유용합니다.

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          modelArg: "--model",
          sessionArg: "--session",
          sessionMode: "existing",
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
        },
      },
    },
  },
}
```

- CLI 백엔드는 텍스트 우선이며, 도구는 항상 비활성화됩니다.
- `sessionArg`가 설정되면 세션이 지원됩니다.
- `imageArg`가 파일 경로를 받을 수 있으면 이미지 전달이 지원됩니다.

### `agents.defaults.heartbeat`

주기적 heartbeat 실행입니다.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m은 비활성화
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        lightContext: false, // 기본값: false; true이면 workspace bootstrap 파일 중 HEARTBEAT.md만 유지
        isolatedSession: false, // 기본값: false; true이면 각 heartbeat를 새 세션에서 실행(대화 기록 없음)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (기본값) | block
        target: "none", // 기본값: none | 옵션: last | whatsapp | telegram | discord | ...
        prompt: "HEARTBEAT.md가 있으면 읽으세요...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: 기간 문자열(ms/s/m/h). 기본값: `30m`(API 키 인증) 또는 `1h`(OAuth 인증). 비활성화하려면 `0m`으로 설정하세요.
- `suppressToolErrorWarnings`: true일 때 heartbeat 실행 중 tool 오류 경고 페이로드를 억제합니다.
- `directPolicy`: 직접/DM 전달 정책입니다. `allow`(기본값)는 직접 대상 전달을 허용합니다. `block`은 직접 대상 전달을 억제하고 `reason=dm-blocked`를 출력합니다.
- `lightContext`: true일 때 heartbeat 실행은 경량 bootstrap 컨텍스트를 사용하며 workspace bootstrap 파일 중 `HEARTBEAT.md`만 유지합니다.
- `isolatedSession`: true일 때 각 heartbeat는 이전 대화 기록 없이 새 세션에서 실행됩니다. cron `sessionTarget: "isolated"`와 동일한 격리 패턴입니다. heartbeat당 토큰 비용을 약 100K에서 약 2-5K 토큰으로 줄입니다.
- 에이전트별: `agents.list[].heartbeat`를 설정하세요. 어떤 에이전트든 `heartbeat`를 정의하면 heartbeat는 **해당 에이전트들만** 실행됩니다.
- Heartbeat는 전체 에이전트 턴을 실행하므로, 간격이 짧을수록 더 많은 토큰을 사용합니다.

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        provider: "my-provider", // 등록된 compaction provider plugin의 id (선택 사항)
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "배포 ID, 티켓 ID, host:port 쌍을 정확히 보존하세요.", // identifierPolicy=custom일 때 사용
        postCompactionSections: ["Session Startup", "Red Lines"], // []는 재삽입 비활성화
        model: "openrouter/anthropic/claude-sonnet-4-6", // 선택적 compaction 전용 모델 재정의
        notifyUser: true, // compaction 시작 시 짧은 알림 전송(기본값: false)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "세션이 compaction에 가까워지고 있습니다. 오래 유지할 기억을 지금 저장하세요.",
          prompt: "지속될 메모가 있으면 memory/YYYY-MM-DD.md에 작성하고, 저장할 것이 없으면 정확한 무음 토큰 NO_REPLY로 답하세요.",
        },
      },
    },
  },
}
```

- `mode`: `default` 또는 `safeguard`(긴 기록에 대한 청크 단위 요약). [Compaction](/ko/concepts/compaction)을 참고하세요.
- `provider`: 등록된 compaction provider plugin의 ID입니다. 설정되면 내장 LLM 요약 대신 provider의 `summarize()`가 호출됩니다. 실패 시 내장 방식으로 대체됩니다. provider를 설정하면 `mode: "safeguard"`가 강제됩니다. [Compaction](/ko/concepts/compaction)을 참고하세요.
- `timeoutSeconds`: OpenClaw가 중단하기 전에 단일 compaction 작업에 허용되는 최대 시간(초)입니다. 기본값: `900`.
- `identifierPolicy`: `strict`(기본값), `off`, 또는 `custom`. `strict`는 compaction 요약 중 내장된 불투명 식별자 보존 지침을 앞에 추가합니다.
- `identifierInstructions`: `identifierPolicy=custom`일 때 사용되는 선택적 사용자 지정 식별자 보존 텍스트입니다.
- `postCompactionSections`: compaction 후 재삽입할 선택적 AGENTS.md H2/H3 섹션 이름입니다. 기본값은 `["Session Startup", "Red Lines"]`이며, 비활성화하려면 `[]`로 설정하세요. 설정되지 않았거나 명시적으로 해당 기본 쌍으로 설정된 경우, 이전 `Every Session`/`Safety` 제목도 레거시 대체값으로 허용됩니다.
- `model`: compaction 요약 전용의 선택적 `provider/model-id` 재정의입니다. 메인 세션은 한 모델을 유지하되 compaction 요약은 다른 모델에서 실행하고 싶을 때 사용하세요. 설정하지 않으면 compaction은 세션의 primary 모델을 사용합니다.
- `notifyUser`: `true`일 때 compaction이 시작되면 사용자에게 짧은 알림(예: "컨텍스트를 압축하는 중...")을 보냅니다. 기본적으로는 compaction을 조용히 유지하기 위해 비활성화되어 있습니다.
- `memoryFlush`: 자동 compaction 전에 지속될 메모리를 저장하기 위한 무음 agentic 턴입니다. workspace가 읽기 전용이면 건너뜁니다.

### `agents.defaults.contextPruning`

LLM으로 보내기 전에 메모리 내 컨텍스트에서 **오래된 tool 결과**를 가지치기합니다. 디스크의 세션 기록은 **수정하지 않습니다**.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // 기간(ms/s/m/h), 기본 단위: 분
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[이전 tool 결과 내용이 지워졌습니다]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="cache-ttl 모드 동작">

- `mode: "cache-ttl"`는 가지치기 패스를 활성화합니다.
- `ttl`은 마지막 캐시 터치 이후 다시 가지치기를 실행할 수 있는 빈도를 제어합니다.
- 가지치기는 먼저 과도하게 큰 tool 결과를 soft-trim하고, 필요하면 더 오래된 tool 결과를 hard-clear합니다.

**Soft-trim**은 시작과 끝을 유지하고 가운데에 `...`를 삽입합니다.

**Hard-clear**는 전체 tool 결과를 placeholder로 교체합니다.

참고:

- 이미지 블록은 절대 잘리거나 지워지지 않습니다.
- 비율은 토큰 수가 아니라 문자 수 기준의 근사값입니다.
- `keepLastAssistants`보다 적은 assistant 메시지만 존재하면 가지치기를 건너뜁니다.

</Accordion>

동작 세부 정보는 [Session Pruning](/ko/concepts/session-pruning)을 참고하세요.

### 블록 스트리밍

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (minMs/maxMs 사용)
    },
  },
}
```

- Telegram이 아닌 채널은 블록 답글을 활성화하려면 명시적인 `*.blockStreaming: true`가 필요합니다.
- 채널 재정의: `channels.<channel>.blockStreamingCoalesce`(및 계정별 변형). Signal/Slack/Discord/Google Chat은 기본값으로 `minChars: 1500`을 사용합니다.
- `humanDelay`: 블록 답글 사이의 무작위 지연입니다. `natural` = 800–2500ms. 에이전트별 재정의: `agents.list[].humanDelay`.

동작 및 청크 세부 사항은 [Streaming](/ko/concepts/streaming)을 참고하세요.

### 입력 중 표시기

```json5
{
  agents: {
    defaults: {
      typingMode: "instant", // never | instant | thinking | message
      typingIntervalSeconds: 6,
    },
  },
}
```

- 기본값: 직접 채팅/멘션에는 `instant`, 멘션 없는 그룹 채팅에는 `message`.
- 세션별 재정의: `session.typingMode`, `session.typingIntervalSeconds`.

[Typing Indicators](/ko/concepts/typing-indicators)를 참고하세요.

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

임베디드 에이전트용 선택적 sandboxing입니다. 전체 가이드는 [Sandboxing](/ko/gateway/sandboxing)을 참고하세요.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        backend: "docker", // docker | ssh | openshell
        scope: "agent", // session | agent | shared
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          containerPrefix: "openclaw-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256,
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "openclaw-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
          binds: ["/home/user/source:/source:rw"],
        },
        ssh: {
          target: "user@gateway-host:22",
          command: "ssh",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // SecretRef / 인라인 내용도 지원:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          network: "openclaw-sandbox-browser",
          cdpPort: 9222,
          cdpSourceRange: "172.21.0.1/32",
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          autoStart: true,
          autoStartTimeoutMs: 12000,
        },
        prune: {
          idleHours: 24,
          maxAgeDays: 7,
        },
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "apply_patch",
          "sessions_list",
          "sessions_history",
          "sessions_send",
          "sessions_spawn",
          "session_status",
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"],
      },
    },
  },
}
```

<Accordion title="Sandbox 세부 정보">

**백엔드:**

- `docker`: 로컬 Docker 런타임(기본값)
- `ssh`: 일반 SSH 기반 원격 런타임
- `openshell`: OpenShell 런타임

`backend: "openshell"`을 선택하면 런타임별 설정은 `plugins.entries.openshell.config`로 이동합니다.

**SSH 백엔드 구성:**

- `target`: `user@host[:port]` 형식의 SSH 대상
- `command`: SSH 클라이언트 명령(기본값: `ssh`)
- `workspaceRoot`: 범위별 workspace에 사용되는 절대 원격 루트
- `identityFile` / `certificateFile` / `knownHostsFile`: OpenSSH에 전달되는 기존 로컬 파일
- `identityData` / `certificateData` / `knownHostsData`: OpenClaw가 런타임에 임시 파일로 구체화하는 인라인 내용 또는 SecretRef
- `strictHostKeyChecking` / `updateHostKeys`: OpenSSH host-key 정책 노브

**SSH 인증 우선순위:**

- `identityData`가 `identityFile`보다 우선합니다
- `certificateData`가 `certificateFile`보다 우선합니다
- `knownHostsData`가 `knownHostsFile`보다 우선합니다
- SecretRef 기반 `*Data` 값은 sandbox 세션 시작 전에 활성 비밀 런타임 스냅샷에서 해석됩니다

**SSH 백엔드 동작:**

- 생성 또는 재생성 후 원격 workspace를 한 번 시드합니다
- 그 후 원격 SSH workspace를 정규 상태로 유지합니다
- `exec`, 파일 tool, media 경로를 SSH를 통해 라우팅합니다
- 원격 변경 내용을 호스트로 자동 동기화하지 않습니다
- sandbox browser 컨테이너는 지원하지 않습니다

**Workspace 액세스:**

- `none`: `~/.openclaw/sandboxes` 아래 범위별 sandbox workspace
- `ro`: `/workspace`의 sandbox workspace, `/agent`에 읽기 전용으로 마운트된 agent workspace
- `rw`: agent workspace를 `/workspace`에 읽기/쓰기 가능하게 마운트

**범위:**

- `session`: 세션별 컨테이너 + workspace
- `agent`: 에이전트별 하나의 컨테이너 + workspace(기본값)
- `shared`: 공유 컨테이너와 workspace(세션 간 격리 없음)

**OpenShell 플러그인 구성:**

```json5
{
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          mode: "mirror", // mirror | remote
          from: "openclaw",
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
          gateway: "lab", // 선택 사항
          gatewayEndpoint: "https://lab.example", // 선택 사항
          policy: "strict", // 선택적 OpenShell 정책 id
          providers: ["openai"], // 선택 사항
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**OpenShell 모드:**

- `mirror`: exec 전에 로컬에서 원격으로 시드하고, exec 후 다시 동기화; 로컬 workspace가 정규 상태를 유지
- `remote`: sandbox 생성 시 한 번 원격으로 시드한 뒤, 원격 workspace를 정규 상태로 유지

`remote` 모드에서는 OpenClaw 외부에서 호스트 로컬에 가해진 편집은 시드 단계 이후 sandbox로 자동 동기화되지 않습니다.
전송은 OpenShell sandbox로의 SSH이지만, 플러그인이 sandbox 생명주기와 선택적 미러 동기화를 소유합니다.

**`setupCommand`**는 컨테이너 생성 후 한 번 실행됩니다(`sh -lc`를 통해). 네트워크 송신, 쓰기 가능한 루트, root 사용자가 필요합니다.

**컨테이너 기본값은 `network: "none"`**입니다 — 에이전트에 아웃바운드 액세스가 필요하면 `"bridge"`(또는 사용자 지정 bridge 네트워크)로 설정하세요.
`"host"`는 차단됩니다. `"container:<id>"`는 기본적으로 차단되며,
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`를 명시적으로 설정한 경우에만 허용됩니다(비상용).

**수신 첨부 파일**은 활성 workspace의 `media/inbound/*`에 스테이징됩니다.

**`docker.binds`**는 추가 호스트 디렉터리를 마운트합니다. 전역 및 에이전트별 bind는 병합됩니다.

**Sandboxed browser** (`sandbox.browser.enabled`): 컨테이너의 Chromium + CDP. noVNC URL이 시스템 프롬프트에 삽입됩니다. `openclaw.json`에서 `browser.enabled`가 필요하지 않습니다.
noVNC 관찰자 액세스는 기본적으로 VNC 인증을 사용하며, OpenClaw는 공유 URL에 비밀번호를 노출하는 대신 짧은 수명의 토큰 URL을 발급합니다.

- `allowHostControl: false`(기본값)는 sandbox된 세션이 호스트 browser를 대상으로 하는 것을 차단합니다.
- `network`의 기본값은 `openclaw-sandbox-browser`(전용 bridge 네트워크)입니다. 전역 bridge 연결이 명시적으로 필요할 때만 `bridge`로 설정하세요.
- `cdpSourceRange`는 선택적으로 컨테이너 가장자리에서 CDP 인바운드를 CIDR 범위로 제한합니다(예: `172.21.0.1/32`).
- `sandbox.browser.binds`는 추가 호스트 디렉터리를 sandbox browser 컨테이너에만 마운트합니다. 설정되면(`[]` 포함) browser 컨테이너에 대해 `docker.binds`를 대체합니다.
- 시작 기본값은 `scripts/sandbox-browser-entrypoint.sh`에 정의되어 있으며 컨테이너 호스트에 맞게 조정되어 있습니다:
  - `--remote-debugging-address=127.0.0.1`
  - `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
  - `--user-data-dir=${HOME}/.chrome`
  - `--no-first-run`
  - `--no-default-browser-check`
  - `--disable-3d-apis`
  - `--disable-gpu`
  - `--disable-software-rasterizer`
  - `--disable-dev-shm-usage`
  - `--disable-background-networking`
  - `--disable-features=TranslateUI`
  - `--disable-breakpad`
  - `--disable-crash-reporter`
  - `--renderer-process-limit=2`
  - `--no-zygote`
  - `--metrics-recording-only`
  - `--disable-extensions` (기본 활성화)
  - `--disable-3d-apis`, `--disable-software-rasterizer`, `--disable-gpu`는 기본적으로 활성화되며, WebGL/3D 사용에 필요하면 `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`으로 비활성화할 수 있습니다.
  - 워크플로가 확장 기능에 의존하는 경우 `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0`으로 다시 활성화합니다.
  - `--renderer-process-limit=2`는 `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`으로 변경할 수 있습니다. Chromium 기본 프로세스 제한을 사용하려면 `0`으로 설정하세요.
  - 그리고 `noSandbox`가 활성화된 경우 `--no-sandbox` 및 `--disable-setuid-sandbox`.
  - 기본값은 컨테이너 이미지 기준선이며, 컨테이너 기본값을 변경하려면 사용자 지정 진입점이 있는 사용자 지정 browser 이미지를 사용하세요.

</Accordion>

browser sandboxing과 `sandbox.docker.binds`는 현재 Docker 전용입니다.

이미지 빌드:

```bash
scripts/sandbox-setup.sh           # 메인 sandbox 이미지
scripts/sandbox-browser-setup.sh   # 선택적 browser 이미지
```

### `agents.list` (에이전트별 재정의)

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "메인 에이전트",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // 또는 { primary, fallbacks }
        thinkingDefault: "high", // 에이전트별 thinking 수준 재정의
        reasoningDefault: "on", // 에이전트별 reasoning 가시성 재정의
        fastModeDefault: false, // 에이전트별 fast mode 재정의
        params: { cacheRetention: "none" }, // 일치하는 defaults.models params를 키별로 재정의
        skills: ["docs-search"], // 설정되면 agents.defaults.skills를 대체
        identity: {
          name: "Samantha",
          theme: "도움이 되는 나무늘보",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
        subagents: { allowAgents: ["*"] },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        },
      },
    ],
  },
}
```

- `id`: 안정적인 에이전트 ID(필수).
- `default`: 여러 개가 설정되면 첫 번째가 우선합니다(경고 기록). 아무것도 설정되지 않으면 첫 번째 목록 항목이 기본값입니다.
- `model`: 문자열 형식은 `primary`만 재정의하고, 객체 형식 `{ primary, fallbacks }`는 둘 다 재정의합니다(`[]`는 전역 fallback 비활성화). `primary`만 재정의하는 cron 작업은 `fallbacks: []`를 설정하지 않는 한 기본 fallback을 계속 상속합니다.
- `params`: `agents.defaults.models`에서 선택된 모델 항목 위에 병합되는 에이전트별 스트림 params입니다. 전체 모델 카탈로그를 복제하지 않고 `cacheRetention`, `temperature`, `maxTokens` 같은 에이전트별 재정의에 사용하세요.
- `skills`: 선택적 에이전트별 skill 허용 목록입니다. 생략하면 에이전트는 설정된 경우 `agents.defaults.skills`를 상속합니다. 명시적 목록은 기본값과 병합하지 않고 대체하며, `[]`는 skill이 없음을 의미합니다.
- `thinkingDefault`: 선택적 에이전트별 기본 thinking 수준(`off | minimal | low | medium | high | xhigh | adaptive`)입니다. 메시지별 또는 세션 재정의가 없을 때 이 에이전트에 대해 `agents.defaults.thinkingDefault`를 재정의합니다.
- `reasoningDefault`: 선택적 에이전트별 기본 reasoning 가시성(`on | off | stream`)입니다. 메시지별 또는 세션 reasoning 재정의가 없을 때 적용됩니다.
- `fastModeDefault`: 선택적 에이전트별 기본 fast mode 값(`true | false`)입니다. 메시지별 또는 세션 fast-mode 재정의가 없을 때 적용됩니다.
- `runtime`: 선택적 에이전트별 런타임 설명자입니다. 에이전트가 기본적으로 ACP 하네스 세션을 사용해야 할 때 `type: "acp"`와 `runtime.acp` 기본값(`agent`, `backend`, `mode`, `cwd`)을 사용하세요.
- `identity.avatar`: workspace 상대 경로, `http(s)` URL 또는 `data:` URI입니다.
- `identity`는 기본값을 파생합니다: `emoji`에서 `ackReaction`, `name`/`emoji`에서 `mentionPatterns`.
- `subagents.allowAgents`: `sessions_spawn`용 에이전트 ID 허용 목록(`["*"]` = 아무거나, 기본값: 동일 에이전트만).
- Sandbox 상속 가드: 요청자 세션이 sandbox 상태이면, `sessions_spawn`은 sandbox 없이 실행될 대상을 거부합니다.
- `subagents.requireAgentId`: true이면 `agentId`를 생략한 `sessions_spawn` 호출을 차단합니다(명시적 프로필 선택 강제, 기본값: false).

---

## 다중 에이전트 라우팅

하나의 Gateway 안에서 여러 격리된 에이전트를 실행합니다. [Multi-Agent](/ko/concepts/multi-agent)를 참고하세요.

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

### 바인딩 match 필드

- `type` (선택 사항): 일반 라우팅에는 `route`(type 누락 시 route가 기본값), 영구 ACP 대화 바인딩에는 `acp`
- `match.channel` (필수)
- `match.accountId` (선택 사항; `*` = 모든 계정, 생략 = 기본 계정)
- `match.peer` (선택 사항; `{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (선택 사항; 채널별)
- `acp` (선택 사항; `type: "acp"` 전용): `{ mode, label, cwd, backend }`

**결정적 match 순서:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (정확 일치, peer/guild/team 없음)
5. `match.accountId: "*"` (채널 전체)
6. 기본 에이전트

각 계층 내에서는 첫 번째로 일치하는 `bindings` 항목이 우선합니다.

`type: "acp"` 항목의 경우 OpenClaw는 정확한 대화 식별자(`match.channel` + account + `match.peer.id`)로 해석하며, 위의 route 바인딩 계층 순서를 사용하지 않습니다.

### 에이전트별 액세스 프로필

<Accordion title="전체 액세스(sandbox 없음)">

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="읽기 전용 tool + workspace">

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
        tools: {
          allow: [
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="파일 시스템 액세스 없음(메시징 전용)">

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "none" },
        tools: {
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
            "gateway",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

</Accordion>

우선순위 세부 정보는 [Multi-Agent Sandbox & Tools](/ko/tools/multi-agent-sandbox-tools)를 참고하세요.

---

## 세션

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main", // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily", // daily | idle
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    parentForkMaxTokens: 100000, // 이 토큰 수를 초과하면 부모 스레드 포크 건너뜀(0은 비활성화)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // 기간 또는 false
      maxDiskBytes: "500mb", // 선택적 하드 예산
      highWaterBytes: "400mb", // 선택적 정리 목표치
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // 기본 비활성 자동 unfocus 시간 (`0`은 비활성화)
      maxAgeHours: 0, // 기본 하드 최대 사용 기간 시간 (`0`은 비활성화)
    },
    mainKey: "main", // 레거시(런타임은 항상 "main" 사용)
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="세션 필드 세부 정보">

- **`scope`**: 그룹 채팅 컨텍스트의 기본 세션 그룹화 전략입니다.
  - `per-sender`(기본값): 채널 컨텍스트 내에서 각 발신자가 격리된 세션을 가집니다.
  - `global`: 채널 컨텍스트의 모든 참가자가 하나의 세션을 공유합니다(공유 컨텍스트가 의도된 경우에만 사용).
- **`dmScope`**: DM이 그룹화되는 방식입니다.
  - `main`: 모든 DM이 메인 세션을 공유합니다.
  - `per-peer`: 채널 간 발신자 ID별로 격리합니다.
  - `per-channel-peer`: 채널 + 발신자별로 격리합니다(다중 사용자 inbox에 권장).
  - `per-account-channel-peer`: 계정 + 채널 + 발신자별로 격리합니다(다중 계정에 권장).
- **`identityLinks`**: 채널 간 세션 공유를 위한 정규 ID를 provider 접두사가 있는 peer에 매핑합니다.
- **`reset`**: 기본 리셋 정책입니다. `daily`는 로컬 시간 `atHour`에 리셋되고, `idle`은 `idleMinutes` 후 리셋됩니다. 둘 다 구성된 경우 먼저 만료되는 쪽이 우선합니다.
- **`resetByType`**: 타입별 재정의(`direct`, `group`, `thread`)입니다. 레거시 `dm`도 `direct`의 별칭으로 허용됩니다.
- **`parentForkMaxTokens`**: 포크된 스레드 세션 생성 시 허용되는 부모 세션 `totalTokens` 최대값입니다(기본값 `100000`).
  - 부모 `totalTokens`가 이 값을 초과하면 OpenClaw는 부모 대화 기록을 상속하지 않고 새 스레드 세션을 시작합니다.
  - 이 가드를 비활성화하고 항상 부모 포크를 허용하려면 `0`으로 설정하세요.
- **`mainKey`**: 레거시 필드입니다. 런타임은 이제 메인 직접 채팅 버킷에 항상 `"main"`을 사용합니다.
- **`agentToAgent.maxPingPongTurns`**: 에이전트 간 교환 중 에이전트 사이에서 허용되는 최대 응답 왕복 횟수입니다(정수, 범위: `0`–`5`). `0`은 ping-pong 체이닝을 비활성화합니다.
- **`sendPolicy`**: `channel`, `chatType`(`direct|group|channel`, 레거시 `dm` 별칭 포함), `keyPrefix`, `rawKeyPrefix`로 일치시킵니다. 첫 번째 deny가 우선합니다.
- **`maintenance`**: 세션 저장소 정리 + 보존 제어입니다.
  - `mode`: `warn`은 경고만 출력하고, `enforce`는 정리를 적용합니다.
  - `pruneAfter`: 오래된 항목의 보존 기간 기준입니다(기본값 `30d`).
  - `maxEntries`: `sessions.json`의 최대 항목 수입니다(기본값 `500`).
  - `rotateBytes`: `sessions.json`이 이 크기를 초과하면 회전합니다(기본값 `10mb`).
  - `resetArchiveRetention`: `*.reset.<timestamp>` 대화 기록 아카이브의 보존 기간입니다. 기본값은 `pruneAfter`이며, 비활성화하려면 `false`로 설정하세요.
  - `maxDiskBytes`: 선택적 세션 디렉터리 디스크 예산입니다. `warn` 모드에서는 경고를 기록하고, `enforce` 모드에서는 가장 오래된 아티팩트/세션부터 제거합니다.
  - `highWaterBytes`: 예산 정리 후의 선택적 목표치입니다. 기본값은 `maxDiskBytes`의 `80%`입니다.
- **`threadBindings`**: 스레드 바운드 세션 기능의 전역 기본값입니다.
  - `enabled`: 마스터 기본 스위치(provider가 재정의 가능; Discord는 `channels.discord.threadBindings.enabled` 사용)
  - `idleHours`: 기본 비활성 자동 unfocus 시간(`0`은 비활성화; provider가 재정의 가능)
  - `maxAgeHours`: 기본 하드 최대 사용 기간 시간(`0`은 비활성화; provider가 재정의 가능)

</Accordion>

---

## 메시지

```json5
{
  messages: {
    responsePrefix: "🦞", // 또는 "auto"
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // group-mentions | group-all | direct | all
    removeAckAfterReply: false,
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog | steer+backlog | queue | interrupt
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
      },
    },
    inbound: {
      debounceMs: 2000, // 0은 비활성화
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### 응답 접두사

채널/계정별 재정의: `channels.<channel>.responsePrefix`, `channels.<channel>.accounts.<id>.responsePrefix`.

해석 순서(가장 구체적인 것이 우선): 계정 → 채널 → 전역. `""`는 비활성화하며 상위 단계 전파도 중단합니다. `"auto"`는 `[{identity.name}]`을 파생합니다.

**템플릿 변수:**

| 변수              | 설명                   | 예시                        |
| ----------------- | ---------------------- | --------------------------- |
| `{model}`         | 짧은 모델 이름         | `claude-opus-4-6`           |
| `{modelFull}`     | 전체 모델 식별자       | `anthropic/claude-opus-4-6` |
| `{provider}`      | provider 이름          | `anthropic`                 |
| `{thinkingLevel}` | 현재 thinking 수준     | `high`, `low`, `off`        |
| `{identity.name}` | 에이전트 identity 이름 | ( `"auto"`와 동일 )         |

변수는 대소문자를 구분하지 않습니다. `{think}`는 `{thinkingLevel}`의 별칭입니다.

### Ack 반응

- 기본값은 활성 에이전트의 `identity.emoji`, 없으면 `"👀"`입니다. 비활성화하려면 `""`를 설정하세요.
- 채널별 재정의: `channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`.
- 해석 순서: 계정 → 채널 → `messages.ackReaction` → identity 대체값.
- 범위: `group-mentions`(기본값), `group-all`, `direct`, `all`.
- `removeAckAfterReply`: Slack, Discord, Telegram에서 답글 후 ack를 제거합니다.
- `messages.statusReactions.enabled`: Slack, Discord, Telegram에서 수명 주기 상태 반응을 활성화합니다.
  Slack과 Discord에서는 설정하지 않으면 ack 반응이 활성화된 경우 상태 반응도 활성화된 상태를 유지합니다.
  Telegram에서는 수명 주기 상태 반응을 활성화하려면 명시적으로 `true`로 설정해야 합니다.

### 수신 debounce

같은 발신자의 빠른 연속 텍스트 전용 메시지를 하나의 에이전트 턴으로 묶습니다. 미디어/첨부 파일은 즉시 flush됩니다. 제어 명령은 debounce를 우회합니다.

### TTS (text-to-speech)

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: { enabled: true },
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0,
        },
      },
      openai: {
        apiKey: "openai_api_key",
        baseUrl: "https://api.openai.com/v1",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

- `auto`는 기본 자동 TTS 모드를 제어합니다: `off`, `always`, `inbound`, 또는 `tagged`. `/tts on|off`는 로컬 환경설정을 재정의할 수 있고, `/tts status`는 실제 적용 상태를 보여줍니다.
- `summaryModel`은 자동 요약에 대해 `agents.defaults.model.primary`를 재정의합니다.
- `modelOverrides`는 기본적으로 활성화되며, `modelOverrides.allowProvider`의 기본값은 `false`(opt-in)입니다.
- API 키의 대체값은 `ELEVENLABS_API_KEY`/`XI_API_KEY`, `OPENAI_API_KEY`입니다.
- `openai.baseUrl`은 OpenAI TTS 엔드포인트를 재정의합니다. 해석 순서는 구성, 그다음 `OPENAI_TTS_BASE_URL`, 그다음 `https://api.openai.com/v1`입니다.
- `openai.baseUrl`이 OpenAI가 아닌 엔드포인트를 가리키면, OpenClaw는 이를 OpenAI 호환 TTS 서버로 간주하고 모델/음성 검증을 완화합니다.

---

## Talk

Talk 모드(macOS/iOS/Android)의 기본값입니다.

```json5
{
  talk: {
    provider: "elevenlabs",
    providers: {
      elevenlabs: {
        voiceId: "elevenlabs_voice_id",
        voiceAliases: {
          Clawd: "EXAVITQu4vr4xnSDxMaL",
          Roger: "CwhRBWXzGAHq8TQ4Fs17",
        },
        modelId: "eleven_v3",
        outputFormat: "mp3_44100_128",
        apiKey: "elevenlabs_api_key",
      },
    },
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

- 여러 Talk provider가 구성된 경우 `talk.provider`는 `talk.providers`의 키와 일치해야 합니다.
- 레거시 평면 Talk 키(`talk.voiceId`, `talk.voiceAliases`, `talk.modelId`, `talk.outputFormat`, `talk.apiKey`)는 호환성 전용이며 `talk.providers.<provider>`로 자동 마이그레이션됩니다.
- Voice ID의 대체값은 `ELEVENLABS_VOICE_ID` 또는 `SAG_VOICE_ID`입니다.
- `providers.*.apiKey`는 일반 텍스트 문자열 또는 SecretRef 객체를 받을 수 있습니다.
- `ELEVENLABS_API_KEY` 대체값은 Talk API 키가 구성되지 않았을 때만 적용됩니다.
- `providers.*.voiceAliases`를 사용하면 Talk 지시문에서 친숙한 이름을 사용할 수 있습니다.
- `silenceTimeoutMs`는 Talk 모드가 사용자 침묵 후 대본을 전송하기 전에 얼마나 기다릴지 제어합니다. 설정하지 않으면 플랫폼 기본 일시정지 창을 유지합니다(`macOS 및 Android에서는 700 ms, iOS에서는 900 ms`).

---

## 도구

### Tool 프로필

`tools.profile`은 `tools.allow`/`tools.deny` 이전에 기본 허용 목록을 설정합니다:

로컬 온보딩은 설정되지 않은 새 로컬 구성에 기본적으로 `tools.profile: "coding"`을 적용합니다(기존의 명시적 프로필은 보존됨).

| 프로필      | 포함 항목                                                                                                                   |
| ----------- | --------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | `session_status`만                                                                                                          |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                  |
| `full`      | 제한 없음(설정 안 함과 동일)                                                                                                |

### Tool 그룹

| 그룹               | 도구                                                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `group:runtime`    | `exec`, `process`, `code_execution` (`bash`는 `exec`의 별칭으로 허용됨)                                                  |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                   |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                                                            |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                    |
| `group:ui`         | `browser`, `canvas`                                                                                                      |
| `group:automation` | `cron`, `gateway`                                                                                                        |
| `group:messaging`  | `message`                                                                                                                |
| `group:nodes`      | `nodes`                                                                                                                  |
| `group:agents`     | `agents_list`                                                                                                            |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                       |
| `group:openclaw`   | 모든 내장 tool(provider plugin 제외)                                                                                     |

### `tools.allow` / `tools.deny`

전역 tool 허용/거부 정책입니다(deny 우선). 대소문자를 구분하지 않으며 `*` 와일드카드를 지원합니다. Docker sandbox가 꺼져 있어도 적용됩니다.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

특정 provider 또는 모델에 대해 tool을 추가로 제한합니다. 순서: 기본 프로필 → provider 프로필 → allow/deny.

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.4": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

### `tools.elevated`

sandbox 외부의 elevated exec 액세스를 제어합니다:

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["1234567890123", "987654321098765432"],
      },
    },
  },
}
```

- 에이전트별 재정의(`agents.list[].tools.elevated`)는 추가 제한만 할 수 있습니다.
- `/elevated on|off|ask|full`은 상태를 세션별로 저장하고, 인라인 지시문은 단일 메시지에 적용됩니다.
- Elevated `exec`는 sandboxing을 우회하며 구성된 이스케이프 경로(`gateway`가 기본값, exec 대상이 `node`일 때는 `node`)를 사용합니다.

### `tools.exec`

```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      notifyOnExitEmptySuccess: false,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.4"],
      },
    },
  },
}
```

### `tools.loopDetection`

Tool 루프 안전 검사는 기본적으로 **비활성화**되어 있습니다. 감지를 활성화하려면 `enabled: true`를 설정하세요.
설정은 전역 `tools.loopDetection`에 정의할 수 있으며 에이전트별로 `agents.list[].tools.loopDetection`에서 재정의할 수 있습니다.

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

- `historySize`: 루프 분석을 위해 유지되는 최대 tool 호출 기록 수입니다.
- `warningThreshold`: 경고를 위한 반복적 무진전 패턴 임계값입니다.
- `criticalThreshold`: 심각한 루프를 차단하기 위한 더 높은 반복 임계값입니다.
- `globalCircuitBreakerThreshold`: 모든 무진전 실행에 대한 하드 중단 임계값입니다.
- `detectors.genericRepeat`: 같은 tool/같은 인자 호출 반복 시 경고합니다.
- `detectors.knownPollNoProgress`: 알려진 poll tool(`process.poll`, `command_status` 등)에 대한 무진전 시 경고/차단합니다.
- `detectors.pingPong`: 교대하는 무진전 쌍 패턴에 대해 경고/차단합니다.
- `warningThreshold >= criticalThreshold` 또는 `criticalThreshold >= globalCircuitBreakerThreshold`이면 검증이 실패합니다.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // 또는 BRAVE_API_KEY env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // 선택 사항; 자동 감지를 원하면 생략
        maxChars: 50000,
        maxCharsCap: 50000,
        maxResponseBytes: 2000000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        maxRedirects: 3,
        readability: true,
        userAgent: "custom-ua",
      },
    },
  },
}
```

### `tools.media`

수신 미디어 이해(image/audio/video)를 구성합니다:

```json5
{
  tools: {
    media: {
      concurrency: 2,
      asyncCompletion: {
        directSend: false, // opt-in: 완료된 비동기 music/video를 채널로 직접 전송
      },
      audio: {
        enabled: true,
        maxBytes: 20971520,
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }],
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  },
}
```

<Accordion title="미디어 모델 항목 필드">

**Provider 항목** (`type: "provider"` 또는 생략):

- `provider`: API provider id (`openai`, `anthropic`, `google`/`gemini`, `groq` 등)
- `model`: 모델 id 재정의
- `profile` / `preferredProfile`: `auth-profiles.json` 프로필 선택

**CLI 항목** (`type: "cli"`):

- `command`: 실행할 실행 파일
- `args`: 템플릿 인자(`{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}` 등 지원)

**공통 필드:**

- `capabilities`: 선택적 목록(`image`, `audio`, `video`). 기본값: `openai`/`anthropic`/`minimax` → image, `google` → image+audio+video, `groq` → audio.
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: 항목별 재정의.
- 실패하면 다음 항목으로 대체됩니다.

Provider 인증은 표준 순서를 따릅니다: `auth-profiles.json` → env vars → `models.providers.*.apiKey`.

**비동기 완료 필드:**

- `asyncCompletion.directSend`: `true`이면 완료된 비동기 `music_generate` 및 `video_generate` 작업이 먼저 직접 채널 전달을 시도합니다. 기본값은 `false`(레거시 requester-session wake/model-delivery 경로)입니다.

</Accordion>

### `tools.agentToAgent`

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },
}
```

### `tools.sessions`

세션 tool(`sessions_list`, `sessions_history`, `sessions_send`)이 어떤 세션을 대상으로 할 수 있는지 제어합니다.

기본값: `tree` (현재 세션 + 그것이 생성한 세션, 예: subagent).

```json5
{
  tools: {
    sessions: {
      // "self" | "tree" | "agent" | "all"
      visibility: "tree",
    },
  },
}
```

참고:

- `self`: 현재 세션 키만.
- `tree`: 현재 세션 + 현재 세션이 생성한 세션(subagent).
- `agent`: 현재 에이전트 ID에 속한 모든 세션(같은 에이전트 ID 아래에서 발신자별 세션을 실행하는 경우 다른 사용자도 포함될 수 있음).
- `all`: 모든 세션. 에이전트 간 대상 지정은 여전히 `tools.agentToAgent`가 필요합니다.
- Sandbox clamp: 현재 세션이 sandbox 상태이고 `agents.defaults.sandbox.sessionToolsVisibility="spawned"`이면 `tools.sessions.visibility="all"`이어도 visibility는 `tree`로 강제됩니다.

### `tools.sessions_spawn`

`sessions_spawn`의 인라인 첨부 파일 지원을 제어합니다.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // opt-in: 인라인 파일 첨부를 허용하려면 true로 설정
        maxTotalBytes: 5242880, // 모든 파일 합계 5 MB
        maxFiles: 50,
        maxFileBytes: 1048576, // 파일당 1 MB
        retainOnSessionKeep: false, // cleanup="keep"일 때 첨부 보존
      },
    },
  },
}
```

참고:

- 첨부 파일은 `runtime: "subagent"`에서만 지원됩니다. ACP 런타임은 이를 거부합니다.
- 파일은 자식 workspace의 `.openclaw/attachments/<uuid>/`에 `.manifest.json`과 함께 구체화됩니다.
- 첨부 파일 내용은 대화 기록 저장에서 자동으로 redaction됩니다.
- Base64 입력은 엄격한 알파벳/패딩 검사와 디코드 전 크기 가드로 검증됩니다.
- 파일 권한은 디렉터리에 `0700`, 파일에 `0600`입니다.
- 정리는 `cleanup` 정책을 따릅니다: `delete`는 항상 첨부 파일을 제거하고, `keep`은 `retainOnSessionKeep: true`일 때만 유지합니다.

### `tools.experimental`

실험적 내장 tool 플래그입니다. 런타임별 자동 활성화 규칙이 적용되는 경우를 제외하면 기본적으로 꺼져 있습니다.

```json5
{
  tools: {
    experimental: {
      planTool: true, // 실험적 update_plan 활성화
    },
  },
}
```

참고:

- `planTool`: 중요하고 여러 단계가 있는 작업 추적용 구조화된 `update_plan` tool을 활성화합니다.
- 기본값: OpenAI가 아닌 provider에서는 `false`. OpenAI와 OpenAI Codex 실행은 설정되지 않은 경우 자동으로 활성화합니다. 이 자동 활성화를 끄려면 `false`로 설정하세요.
- 활성화되면 시스템 프롬프트에도 사용 지침이 추가되어 모델이 실질적인 작업에만 사용하고 동시에 최대 하나의 단계만 `in_progress`로 유지하게 됩니다.

### `agents.defaults.subagents`

```json5
{
  agents: {
    defaults: {
      subagents: {
        allowAgents: ["research"],
        model: "minimax/MiniMax-M2.7",
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`: 생성된 sub-agent의 기본 모델입니다. 생략하면 sub-agent는 호출자의 모델을 상속합니다.
- `allowAgents`: 요청 에이전트가 자체 `subagents.allowAgents`를 설정하지 않았을 때 `sessions_spawn`용 기본 대상 에이전트 ID 허용 목록입니다(`["*"]` = 아무거나, 기본값: 동일 에이전트만).
- `runTimeoutSeconds`: tool 호출에서 `runTimeoutSeconds`를 생략했을 때 `sessions_spawn`의 기본 타임아웃(초)입니다. `0`은 타임아웃 없음입니다.
- subagent별 tool 정책: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## 사용자 지정 provider 및 base URL

OpenClaw는 내장 모델 카탈로그를 사용합니다. 사용자 지정 provider는 구성의 `models.providers` 또는 `~/.openclaw/agents/<agentId>/agent/models.json`을 통해 추가합니다.

```json5
{
  models: {
    mode: "merge", // merge (기본값) | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions", // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            contextTokens: 96000,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

- 사용자 지정 인증 요구사항에는 `authHeader: true` + `headers`를 사용하세요.
- 에이전트 구성 루트는 `OPENCLAW_AGENT_DIR`(또는 레거시 환경 변수 별칭 `PI_CODING_AGENT_DIR`)로 재정의할 수 있습니다.
- 일치하는 provider ID의 병합 우선순위:
  - 비어 있지 않은 에이전트 `models.json` `baseUrl` 값이 우선합니다.
  - 비어 있지 않은 에이전트 `apiKey` 값은 해당 provider가 현재 구성/auth-profile 컨텍스트에서 SecretRef 관리가 아닐 때만 우선합니다.
  - SecretRef 관리 provider `apiKey` 값은 해석된 비밀을 유지하는 대신 소스 마커(`env` ref의 경우 `ENV_VAR_NAME`, file/exec ref의 경우 `secretref-managed`)에서 새로 고쳐집니다.
  - SecretRef 관리 provider header 값은 소스 마커(`env` ref의 경우 `secretref-env:ENV_VAR_NAME`, file/exec ref의 경우 `secretref-managed`)에서 새로 고쳐집니다.
  - 비어 있거나 누락된 에이전트 `apiKey`/`baseUrl`은 구성의 `models.providers`로 대체됩니다.
  - 일치하는 모델 `contextWindow`/`maxTokens`는 명시적 구성값과 암시적 카탈로그 값 중 더 큰 값을 사용합니다.
  - 일치하는 모델 `contextTokens`는 존재하는 경우 명시적 런타임 캡을 보존합니다. 모델의 네이티브 메타데이터를 변경하지 않고 실제 컨텍스트를 제한하려면 이를 사용하세요.
  - 구성이 `models.json`을 완전히 다시 쓰게 하려면 `models.mode: "replace"`를 사용하세요.
  - 마커 유지 저장은 소스 권위적입니다: 마커는 해석된 런타임 비밀 값이 아니라 활성 소스 구성 스냅샷(해석 전)에서 기록됩니다.

### Provider 필드 세부 정보

- `models.mode`: provider 카탈로그 동작(`merge` 또는 `replace`).
- `models.providers`: provider id를 키로 하는 사용자 지정 provider 맵.
- `models.providers.*.api`: 요청 어댑터(`openai-completions`, `openai-responses`, `anthropic-messages`, `google-generative-ai` 등).
- `models.providers.*.apiKey`: provider 자격 증명(SecretRef/env 치환 권장).
- `models.providers.*.auth`: 인증 전략(`api-key`, `token`, `oauth`, `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: Ollama + `openai-completions`에서 요청에 `options.num_ctx` 주입(기본값: `true`).
- `models.providers.*.authHeader`: 필요할 때 `Authorization` 헤더에서 자격 증명을 강제 전송.
- `models.providers.*.baseUrl`: 업스트림 API 기본 URL.
- `models.providers.*.headers`: 프록시/테넌트 라우팅용 추가 정적 헤더.
- `models.providers.*.request`: 모델 provider HTTP 요청용 전송 재정의.
  - `request.headers`: 추가 헤더(provider 기본값과 병합). 값은 SecretRef를 받을 수 있습니다.
  - `request.auth`: 인증 전략 재정의. 모드: `"provider-default"`(provider 내장 인증 사용), `"authorization-bearer"`(`token` 포함), `"header"`(`headerName`, `value`, 선택적 `prefix` 포함).
  - `request.proxy`: HTTP 프록시 재정의. 모드: `"env-proxy"`(`HTTP_PROXY`/`HTTPS_PROXY` env vars 사용), `"explicit-proxy"`(`url` 포함). 두 모드 모두 선택적 `tls` 하위 객체를 받을 수 있습니다.
  - `request.tls`: 직접 연결용 TLS 재정의. 필드: `ca`, `cert`, `key`, `passphrase`(모두 SecretRef 허용), `serverName`, `insecureSkipVerify`.
- `models.providers.*.models`: 명시적 provider 모델 카탈로그 항목.
- `models.providers.*.models.*.contextWindow`: 네이티브 모델 컨텍스트 윈도 메타데이터.
- `models.providers.*.models.*.contextTokens`: 선택적 런타임 컨텍스트 캡. 모델의 네이티브 `contextWindow`보다 작은 실제 컨텍스트 예산을 원할 때 사용하세요.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: 선택적 호환성 힌트. 비어 있지 않은 비네이티브 `baseUrl`(호스트가 `api.openai.com`이 아님)을 가진 `api: "openai-completions"`의 경우 OpenClaw는 런타임에 이를 `false`로 강제합니다. 비어 있거나 생략된 `baseUrl`은 기본 OpenAI 동작을 유지합니다.
- `models.providers.*.models.*.compat.requiresStringContent`: 문자열 전용 OpenAI 호환 chat 엔드포인트용 선택적 호환성 힌트. `true`이면 OpenClaw는 요청 전송 전에 순수 텍스트 `messages[].content` 배열을 일반 문자열로 평탄화합니다.
- `plugins.entries.amazon-bedrock.config.discovery`: Bedrock 자동 검색 설정 루트.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: 암시적 검색 켜기/끄기.
- `plugins.entries.amazon-bedrock.config.discovery.region`: 검색용 AWS 리전.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: 대상 검색을 위한 선택적 provider-id 필터.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: 검색 새로 고침 폴링 간격.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: 검색된 모델의 대체 컨텍스트 윈도.
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: 검색된 모델의 대체 최대 출력 토큰.

### Provider 예시

<Accordion title="Cerebras (GLM 4.6 / 4.7)">

```json5
{
  env: { CEREBRAS_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: {
        primary: "cerebras/zai-glm-4.7",
        fallbacks: ["cerebras/zai-glm-4.6"],
      },
      models: {
        "cerebras/zai-glm-4.7": { alias: "GLM 4.7 (Cerebras)" },
        "cerebras/zai-glm-4.6": { alias: "GLM 4.6 (Cerebras)" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      cerebras: {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" },
        ],
      },
    },
  },
}
```

Cerebras에는 `cerebras/zai-glm-4.7`을 사용하고, Z.AI 직접 연결에는 `zai/glm-4.7`을 사용하세요.

</Accordion>

<Accordion title="OpenCode">

```json5
{
  agents: {
    defaults: {
      model: { primary: "opencode/claude-opus-4-6" },
      models: { "opencode/claude-opus-4-6": { alias: "Opus" } },
    },
  },
}
```

`OPENCODE_API_KEY`(또는 `OPENCODE_ZEN_API_KEY`)를 설정하세요. Zen 카탈로그에는 `opencode/...` 참조를, Go 카탈로그에는 `opencode-go/...` 참조를 사용하세요. 단축키: `openclaw onboard --auth-choice opencode-zen` 또는 `openclaw onboard --auth-choice opencode-go`.

</Accordion>

<Accordion title="Z.AI (GLM-4.7)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-4.7" },
      models: { "zai/glm-4.7": {} },
    },
  },
}
```

`ZAI_API_KEY`를 설정하세요. `z.ai/*`와 `z-ai/*`는 허용되는 별칭입니다. 단축키: `openclaw onboard --auth-choice zai-api-key`.

- 일반 엔드포인트: `https://api.z.ai/api/paas/v4`
- 코딩 엔드포인트(기본값): `https://api.z.ai/api/coding/paas/v4`
- 일반 엔드포인트의 경우 base URL 재정의를 가진 사용자 지정 provider를 정의하세요.

</Accordion>

<Accordion title="Moonshot AI (Kimi)">

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: { "moonshot/kimi-k2.5": { alias: "Kimi K2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
        ],
      },
    },
  },
}
```

중국 엔드포인트의 경우: `baseUrl: "https://api.moonshot.cn/v1"` 또는 `openclaw onboard --auth-choice moonshot-api-key-cn`.

네이티브 Moonshot 엔드포인트는 공유 `openai-completions` 전송에서 스트리밍 사용 호환성을 광고하며, OpenClaw는 이제 내장 provider id 하나만이 아니라 엔드포인트 기능을 기준으로 이를 판단합니다.

</Accordion>

<Accordion title="Kimi Coding">

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi/kimi-code" },
      models: { "kimi/kimi-code": { alias: "Kimi Code" } },
    },
  },
}
```

Anthropic 호환 내장 provider입니다. 단축키: `openclaw onboard --auth-choice kimi-code-api-key`.

</Accordion>

<Accordion title="Synthetic (Anthropic 호환)">

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

Base URL은 `/v1`을 생략해야 합니다(Anthropic 클라이언트가 이를 추가함). 단축키: `openclaw onboard --auth-choice synthetic-api-key`.

</Accordion>

<Accordion title="MiniMax M2.7 (직접 연결)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.7" },
      models: {
        "minimax/MiniMax-M2.7": { alias: "Minimax" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

`MINIMAX_API_KEY`를 설정하세요. 단축키:
`openclaw onboard --auth-choice minimax-global-api` 또는
`openclaw onboard --auth-choice minimax-cn-api`.
모델 카탈로그는 이제 기본적으로 M2.7만 사용합니다.
Anthropic 호환 스트리밍 경로에서 OpenClaw는 명시적으로 `thinking`을 설정하지 않는 한 기본적으로 MiniMax thinking을 비활성화합니다. `/fast on` 또는 `params.fastMode: true`는 `MiniMax-M2.7`을 `MiniMax-M2.7-highspeed`로 다시 씁니다.

</Accordion>

<Accordion title="로컬 모델 (LM Studio)">

[Local Models](/ko/gateway/local-models)를 참고하세요. 요약: 충분한 하드웨어에서 LM Studio Responses API를 통해 대형 로컬 모델을 실행하고, 대체를 위해 호스팅된 모델은 병합된 상태로 유지하세요.

</Accordion>

---

## Skills

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn | bun
    },
    entries: {
      "image-lab": {
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // 또는 일반 텍스트 문자열
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: 번들 skill만을 위한 선택적 허용 목록입니다(관리형/workspace skill에는 영향 없음).
- `load.extraDirs`: 추가 공유 skill 루트(가장 낮은 우선순위).
- `install.preferBrew`: `brew`를 사용할 수 있을 때 다른 설치 방식으로 대체되기 전에 Homebrew 설치 프로그램을 우선합니다.
- `install.nodeManager`: `metadata.openclaw.install` 명세용 node 설치 프로그램 선호도 (`npm` | `pnpm` | `yarn` | `bun`).
- `entries.<skillKey>.enabled: false`는 번들/설치된 skill이라도 비활성화합니다.
- `entries.<skillKey>.apiKey`: 기본 env var를 선언하는 skill을 위한 편의 필드입니다(일반 텍스트 문자열 또는 SecretRef 객체).

---

## 플러그인

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: [],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        hooks: {
          allowPromptInjection: false,
        },
        config: { provider: "twilio" },
      },
    },
  },
}
```

- `~/.openclaw/extensions`, `<workspace>/.openclaw/extensions`, 그리고 `plugins.load.paths`에서 로드됩니다.
- 검색은 네이티브 OpenClaw 플러그인과 호환 가능한 Codex 번들 및 Claude 번들을 허용하며, manifest가 없는 Claude 기본 레이아웃 번들도 포함합니다.
- **구성 변경에는 gateway 재시작이 필요합니다.**
- `allow`: 선택적 허용 목록(목록에 있는 플러그인만 로드). `deny`가 우선합니다.
- `plugins.entries.<id>.apiKey`: 플러그인 수준 API 키 편의 필드(플러그인이 지원하는 경우).
- `plugins.entries.<id>.env`: 플러그인 범위 env var 맵.
- `plugins.entries.<id>.hooks.allowPromptInjection`: `false`이면 core가 `before_prompt_build`를 차단하고 레거시 `before_agent_start`의 프롬프트 변경 필드를 무시하며, 레거시 `modelOverride` 및 `providerOverride`는 유지합니다. 네이티브 plugin hook과 지원되는 번들 제공 hook 디렉터리에 적용됩니다.
- `plugins.entries.<id>.subagent.allowModelOverride`: 이 플러그인이 백그라운드 subagent 실행에 대해 실행별 `provider` 및 `model` 재정의를 요청하도록 명시적으로 신뢰합니다.
- `plugins.entries.<id>.subagent.allowedModels`: 신뢰된 subagent 재정의용 정규 `provider/model` 대상의 선택적 허용 목록입니다. 어떤 모델이든 의도적으로 허용하려는 경우에만 `"*"`를 사용하세요.
- `plugins.entries.<id>.config`: 플러그인 정의 구성 객체(사용 가능한 경우 네이티브 OpenClaw plugin 스키마로 검증됨).
- `plugins.entries.firecrawl.config.webFetch`: Firecrawl web-fetch provider 설정.
  - `apiKey`: Firecrawl API 키(SecretRef 허용). `plugins.entries.firecrawl.config.webSearch.apiKey`, 레거시 `tools.web.fetch.firecrawl.apiKey`, 또는 `FIRECRAWL_API_KEY` env var를 대체값으로 사용합니다.
  - `baseUrl`: Firecrawl API base URL(기본값: `https://api.firecrawl.dev`).
  - `onlyMainContent`: 페이지에서 메인 콘텐츠만 추출합니다(기본값: `true`).
  - `maxAgeMs`: 최대 캐시 사용 기간(밀리초)입니다(기본값: `172800000` / 2일).
  - `timeoutSeconds`: 스크래핑 요청 타임아웃(초)입니다(기본값: `60`).
- `plugins.entries.xai.config.xSearch`: xAI X Search (Grok 웹 검색) 설정.
  - `enabled`: X Search provider를 활성화합니다.
  - `model`: 검색에 사용할 Grok 모델(예: `"grok-4-1-fast"`).
- `plugins.entries.memory-core.config.dreaming`: memory dreaming(실험적) 설정. 단계와 임계값은 [Dreaming](/ko/concepts/dreaming)을 참고하세요.
  - `enabled`: 마스터 dreaming 스위치(기본값 `false`).
  - `frequency`: 각 전체 dreaming 스윕의 cron 주기(기본값은 `"0 3 * * *"`).
  - 단계 정책과 임계값은 구현 세부 사항입니다(사용자 대상 구성 키 아님).
- 전체 memory 구성은 [Memory configuration reference](/ko/reference/memory-config)에 있습니다:
  - `agents.defaults.memorySearch.*`
  - `memory.backend`
  - `memory.citations`
  - `memory.qmd.*`
  - `plugins.entries.memory-core.config.dreaming`
- 활성화된 Claude 번들 플러그인은 `settings.json`에서 임베디드 Pi 기본값도 제공할 수 있습니다. OpenClaw는 이를 원시 OpenClaw 구성 패치가 아니라 정제된 에이전트 설정으로 적용합니다.
- `plugins.slots.memory`: 활성 memory plugin id를 선택하거나 memory plugin을 비활성화하려면 `"none"`을 선택합니다.
- `plugins.slots.contextEngine`: 활성 context engine plugin id를 선택합니다. 다른 엔진을 설치하고 선택하지 않는 한 기본값은 `"legacy"`입니다.
- `plugins.installs`: `openclaw plugins update`가 사용하는 CLI 관리 설치 메타데이터입니다.
  - `source`, `spec`, `sourcePath`, `installPath`, `version`, `resolvedName`, `resolvedVersion`, `resolvedSpec`, `integrity`, `shasum`, `resolvedAt`, `installedAt`를 포함합니다.
  - `plugins.installs.*`는 관리 상태로 취급하세요. 수동 편집보다 CLI 명령을 선호하세요.

[Plugins](/ko/tools/plugin)를 참고하세요.

---

## 브라우저

```