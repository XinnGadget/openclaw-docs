---
read_when:
    - Feishu/Lark 봇을 연결하려는 경우
    - Feishu 채널을 구성하는 경우
summary: Feishu 봇 개요, 기능 및 구성
title: Feishu
x-i18n:
    generated_at: "2026-04-05T12:35:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4e39b6dfe3a3aa4ebbdb992975e570e4f1b5e79f3b400a555fc373a0d1889952
    source_path: channels/feishu.md
    workflow: 15
---

# Feishu 봇

Feishu(Lark)는 기업에서 메시징과 협업에 사용하는 팀 채팅 플랫폼입니다. 이 plugin은 플랫폼의 WebSocket 이벤트 구독을 사용해 OpenClaw를 Feishu/Lark 봇에 연결하므로, 공개 webhook URL을 노출하지 않고도 메시지를 수신할 수 있습니다.

---

## 번들 plugin

Feishu는 현재 OpenClaw 릴리스에 번들로 포함되어 제공되므로 별도의 plugin 설치가 필요하지 않습니다.

번들된 Feishu가 포함되지 않은 이전 빌드 또는 사용자 지정 설치를 사용 중인 경우 수동으로 설치하세요.

```bash
openclaw plugins install @openclaw/feishu
```

---

## 빠른 시작

Feishu 채널을 추가하는 방법은 두 가지입니다.

### 방법 1: 온보딩(권장)

OpenClaw를 방금 설치했다면 온보딩을 실행하세요.

```bash
openclaw onboard
```

마법사는 다음 과정을 안내합니다.

1. Feishu 앱 생성 및 자격 증명 수집
2. OpenClaw에서 앱 자격 증명 구성
3. Gateway 시작

✅ **구성 후**, Gateway 상태를 확인하세요.

- `openclaw gateway status`
- `openclaw logs --follow`

### 방법 2: CLI 설정

이미 초기 설치를 완료했다면 CLI를 통해 채널을 추가하세요.

```bash
openclaw channels add
```

**Feishu**를 선택한 다음 App ID와 App Secret을 입력하세요.

✅ **구성 후**, Gateway를 관리하세요.

- `openclaw gateway status`
- `openclaw gateway restart`
- `openclaw logs --follow`

---

## 1단계: Feishu 앱 만들기

### 1. Feishu Open Platform 열기

[Feishu Open Platform](https://open.feishu.cn/app)에 접속해 로그인하세요.

Lark(글로벌) 테넌트는 [https://open.larksuite.com/app](https://open.larksuite.com/app)을 사용하고 Feishu config에서 `domain: "lark"`를 설정해야 합니다.

### 2. 앱 만들기

1. **Create enterprise app**을 클릭합니다.
2. 앱 이름과 설명을 입력합니다.
3. 앱 아이콘을 선택합니다.

![Create enterprise app](/images/feishu-step2-create-app.png)

### 3. 자격 증명 복사

**Credentials & Basic Info**에서 다음을 복사하세요.

- **App ID**(형식: `cli_xxx`)
- **App Secret**

❗ **중요:** App Secret은 비공개로 유지하세요.

![Get credentials](/images/feishu-step3-credentials.png)

### 4. 권한 구성

**Permissions**에서 **Batch import**를 클릭하고 다음을 붙여넣으세요.

```json
{
  "scopes": {
    "tenant": [
      "aily:file:read",
      "aily:file:write",
      "application:application.app_message_stats.overview:readonly",
      "application:application:self_manage",
      "application:bot.menu:write",
      "cardkit:card:read",
      "cardkit:card:write",
      "contact:user.employee_id:readonly",
      "corehr:file:download",
      "event:ip_list",
      "im:chat.access_event.bot_p2p_chat:read",
      "im:chat.members:bot_access",
      "im:message",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:message:readonly",
      "im:message:send_as_bot",
      "im:resource"
    ],
    "user": ["aily:file:read", "aily:file:write", "im:chat.access_event.bot_p2p_chat:read"]
  }
}
```

![Configure permissions](/images/feishu-step4-permissions.png)

### 5. 봇 기능 활성화

**App Capability** > **Bot**에서 다음을 수행하세요.

1. 봇 기능을 활성화합니다.
2. 봇 이름을 설정합니다.

![Enable bot capability](/images/feishu-step5-bot-capability.png)

### 6. 이벤트 구독 구성

⚠️ **중요:** 이벤트 구독을 설정하기 전에 다음을 확인하세요.

1. 이미 Feishu에 대해 `openclaw channels add`를 실행했는지
2. Gateway가 실행 중인지(`openclaw gateway status`)

**Event Subscription**에서:

1. **Use long connection to receive events**(WebSocket)를 선택합니다.
2. 이벤트 `im.message.receive_v1`을 추가합니다.
3. (선택 사항) Drive 댓글 워크플로를 위해 `drive.notice.comment_add_v1`도 추가합니다.

⚠️ Gateway가 실행 중이 아니면 long-connection 설정을 저장하지 못할 수 있습니다.

![Configure event subscription](/images/feishu-step6-event-subscription.png)

### 7. 앱 게시

1. **Version Management & Release**에서 버전을 생성합니다.
2. 검토를 위해 제출하고 게시합니다.
3. 관리자 승인을 기다립니다(기업 앱은 보통 자동 승인됨).

---

## 2단계: OpenClaw 구성

### 마법사로 구성(권장)

```bash
openclaw channels add
```

**Feishu**를 선택하고 App ID와 App Secret을 붙여넣으세요.

### config 파일로 구성

`~/.openclaw/openclaw.json`을 편집하세요.

```json5
{
  channels: {
    feishu: {
      enabled: true,
      dmPolicy: "pairing",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
          name: "My AI assistant",
        },
      },
    },
  },
}
```

`connectionMode: "webhook"`을 사용하는 경우 `verificationToken`과 `encryptKey`를 모두 설정하세요. Feishu webhook 서버는 기본적으로 `127.0.0.1`에 바인딩됩니다. 의도적으로 다른 바인딩 주소가 필요한 경우에만 `webhookHost`를 설정하세요.

#### Verification Token 및 Encrypt Key(webhook 모드)

webhook 모드를 사용할 때는 config에서 `channels.feishu.verificationToken`과 `channels.feishu.encryptKey`를 모두 설정하세요. 값을 얻으려면:

1. Feishu Open Platform에서 앱을 엽니다.
2. **Development** → **Events & Callbacks**(开发配置 → 事件与回调)로 이동합니다.
3. **Encryption** 탭(加密策略)을 엽니다.
4. **Verification Token**과 **Encrypt Key**를 복사합니다.

아래 스크린샷은 **Verification Token** 위치를 보여줍니다. **Encrypt Key**는 같은 **Encryption** 섹션에 표시됩니다.

![Verification Token location](/images/feishu-verification-token.png)

### 환경 변수로 구성

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

### Lark(글로벌) 도메인

테넌트가 Lark(국제 버전)에 있는 경우 도메인을 `lark`(또는 전체 도메인 문자열)로 설정하세요. `channels.feishu.domain` 또는 계정별(`channels.feishu.accounts.<id>.domain`)로 설정할 수 있습니다.

```json5
{
  channels: {
    feishu: {
      domain: "lark",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
        },
      },
    },
  },
}
```

### 쿼터 최적화 플래그

선택적 플래그 두 가지로 Feishu API 사용량을 줄일 수 있습니다.

- `typingIndicator`(기본값 `true`): `false`이면 입력 중 반응 호출을 건너뜁니다.
- `resolveSenderNames`(기본값 `true`): `false`이면 발신자 프로필 조회 호출을 건너뜁니다.

최상위 또는 계정별로 설정하세요.

```json5
{
  channels: {
    feishu: {
      typingIndicator: false,
      resolveSenderNames: false,
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
          typingIndicator: true,
          resolveSenderNames: false,
        },
      },
    },
  },
}
```

---

## 3단계: 시작 + 테스트

### 1. Gateway 시작

```bash
openclaw gateway
```

### 2. 테스트 메시지 보내기

Feishu에서 봇을 찾아 메시지를 보내세요.

### 3. 페어링 승인

기본적으로 봇은 페어링 코드를 응답합니다. 이를 승인하세요.

```bash
openclaw pairing approve feishu <CODE>
```

승인 후에는 정상적으로 대화할 수 있습니다.

---

## 개요

- **Feishu 봇 채널**: Gateway가 관리하는 Feishu 봇
- **결정적 라우팅**: 응답은 항상 Feishu로 돌아감
- **세션 격리**: DM은 메인 세션을 공유하고 그룹은 분리됨
- **WebSocket 연결**: Feishu SDK를 통한 long connection, 공개 URL 불필요

---

## 액세스 제어

### 다이렉트 메시지

- **기본값**: `dmPolicy: "pairing"`(알 수 없는 사용자는 페어링 코드를 받음)
- **페어링 승인**:

  ```bash
  openclaw pairing list feishu
  openclaw pairing approve feishu <CODE>
  ```

- **allowlist 모드**: 허용된 Open ID로 `channels.feishu.allowFrom`을 설정

### 그룹 채팅

**1. 그룹 정책**(`channels.feishu.groupPolicy`):

- `"open"` = 그룹의 모든 사용자 허용
- `"allowlist"` = `groupAllowFrom`만 허용
- `"disabled"` = 그룹 메시지 비활성화

기본값: `allowlist`

**2. 멘션 요구 사항**(`channels.feishu.requireMention`, `channels.feishu.groups.<chat_id>.requireMention`으로 재정의 가능):

- 명시적 `true` = @mention 필요
- 명시적 `false` = 멘션 없이 응답
- 설정되지 않았고 `groupPolicy: "open"`인 경우 = 기본값 `false`
- 설정되지 않았고 `groupPolicy`가 `"open"`이 아닌 경우 = 기본값 `true`

---

## 그룹 구성 예시

### 모든 그룹 허용, @mention 불필요(open 그룹의 기본값)

```json5
{
  channels: {
    feishu: {
      groupPolicy: "open",
    },
  },
}
```

### 모든 그룹 허용, 하지만 여전히 @mention 필요

```json5
{
  channels: {
    feishu: {
      groupPolicy: "open",
      requireMention: true,
    },
  },
}
```

### 특정 그룹만 허용

```json5
{
  channels: {
    feishu: {
      groupPolicy: "allowlist",
      // Feishu group IDs (chat_id) look like: oc_xxx
      groupAllowFrom: ["oc_xxx", "oc_yyy"],
    },
  },
}
```

### 그룹에서 메시지를 보낼 수 있는 발신자 제한(sender allowlist)

그룹 자체를 허용하는 것 외에도, 해당 그룹의 **모든 메시지**는 발신자 open_id로 제한됩니다. `groups.<chat_id>.allowFrom`에 나열된 사용자만 메시지가 처리되며, 다른 멤버의 메시지는 무시됩니다(이는 `/reset`이나 `/new` 같은 제어 명령에만 적용되는 것이 아니라 전체 발신자 수준 게이팅입니다).

```json5
{
  channels: {
    feishu: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["oc_xxx"],
      groups: {
        oc_xxx: {
          // Feishu user IDs (open_id) look like: ou_xxx
          allowFrom: ["ou_user1", "ou_user2"],
        },
      },
    },
  },
}
```

---

<a id="get-groupuser-ids"></a>

## 그룹/사용자 ID 가져오기

### 그룹 ID(chat_id)

그룹 ID는 `oc_xxx` 형태입니다.

**방법 1(권장)**

1. Gateway를 시작하고 그룹에서 봇을 @mention합니다.
2. `openclaw logs --follow`를 실행하고 `chat_id`를 찾습니다.

**방법 2**

Feishu API 디버거를 사용해 그룹 채팅을 나열합니다.

### 사용자 ID(open_id)

사용자 ID는 `ou_xxx` 형태입니다.

**방법 1(권장)**

1. Gateway를 시작하고 봇에 DM을 보냅니다.
2. `openclaw logs --follow`를 실행하고 `open_id`를 찾습니다.

**방법 2**

사용자 Open ID는 페어링 요청에서 확인합니다.

```bash
openclaw pairing list feishu
```

---

## 일반 명령

| 명령 | 설명 |
| --------- | ----------------- |
| `/status` | 봇 상태 표시 |
| `/reset`  | 세션 재설정 |
| `/model`  | 모델 표시/전환 |

> 참고: Feishu는 아직 기본 명령 메뉴를 지원하지 않으므로 명령은 텍스트로 보내야 합니다.

## Gateway 관리 명령

| 명령 | 설명 |
| -------------------------- | ----------------------------- |
| `openclaw gateway status`  | Gateway 상태 표시 |
| `openclaw gateway install` | Gateway 서비스 설치/시작 |
| `openclaw gateway stop`    | Gateway 서비스 중지 |
| `openclaw gateway restart` | Gateway 서비스 재시작 |
| `openclaw logs --follow`   | Gateway 로그 추적 |

---

## 문제 해결

### 그룹 채팅에서 봇이 응답하지 않음

1. 봇이 그룹에 추가되어 있는지 확인합니다.
2. 봇을 @mention했는지 확인합니다(기본 동작).
3. `groupPolicy`가 `"disabled"`로 설정되지 않았는지 확인합니다.
4. 로그를 확인합니다: `openclaw logs --follow`

### 봇이 메시지를 수신하지 않음

1. 앱이 게시되고 승인되었는지 확인합니다.
2. 이벤트 구독에 `im.message.receive_v1`이 포함되어 있는지 확인합니다.
3. **long connection**이 활성화되어 있는지 확인합니다.
4. 앱 권한이 완전한지 확인합니다.
5. Gateway가 실행 중인지 확인합니다: `openclaw gateway status`
6. 로그를 확인합니다: `openclaw logs --follow`

### App Secret 유출

1. Feishu Open Platform에서 App Secret을 재설정합니다.
2. config에서 App Secret을 업데이트합니다.
3. Gateway를 재시작합니다.

### 메시지 전송 실패

1. 앱에 `im:message:send_as_bot` 권한이 있는지 확인합니다.
2. 앱이 게시되었는지 확인합니다.
3. 자세한 오류는 로그를 확인합니다.

---

## 고급 구성

### 여러 계정

```json5
{
  channels: {
    feishu: {
      defaultAccount: "main",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
          name: "Primary bot",
        },
        backup: {
          appId: "cli_yyy",
          appSecret: "yyy",
          name: "Backup bot",
          enabled: false,
        },
      },
    },
  },
}
```

`defaultAccount`는 아웃바운드 API가 `accountId`를 명시적으로 지정하지 않을 때 어떤 Feishu 계정을 사용할지 제어합니다.

### 메시지 제한

- `textChunkLimit`: 아웃바운드 텍스트 청크 크기(기본값: 2000자)
- `mediaMaxMb`: 미디어 업로드/다운로드 제한(기본값: 30MB)

### 스트리밍

Feishu는 인터랙티브 카드를 통한 스트리밍 응답을 지원합니다. 활성화하면 봇은 텍스트를 생성하면서 카드를 업데이트합니다.

```json5
{
  channels: {
    feishu: {
      streaming: true, // enable streaming card output (default true)
      blockStreaming: true, // enable block-level streaming (default true)
    },
  },
}
```

전체 응답이 준비된 후 전송하려면 `streaming: false`로 설정하세요.

### ACP 세션

Feishu는 다음에 대해 ACP를 지원합니다.

- DM
- 그룹 주제 대화

Feishu ACP는 텍스트 명령 기반으로 동작합니다. 기본 slash-command 메뉴는 없으므로 대화에서 `/acp ...` 메시지를 직접 사용하세요.

#### 영구 ACP 바인딩

최상위 타입 지정 ACP 바인딩을 사용해 Feishu DM 또는 주제 대화를 영구 ACP 세션에 고정할 수 있습니다.

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "feishu",
        accountId: "default",
        peer: { kind: "direct", id: "ou_1234567890" },
      },
    },
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "feishu",
        accountId: "default",
        peer: { kind: "group", id: "oc_group_chat:topic:om_topic_root" },
      },
      acp: { label: "codex-feishu-topic" },
    },
  ],
}
```

#### 채팅에서 스레드 바인딩 ACP 생성

Feishu DM 또는 주제 대화에서 ACP 세션을 그 자리에서 생성하고 바인딩할 수 있습니다.

```text
/acp spawn codex --thread here
```

참고:

- `--thread here`는 DM과 Feishu 주제에서 작동합니다.
- 바인딩된 DM/주제의 후속 메시지는 해당 ACP 세션으로 직접 라우팅됩니다.
- v1은 일반 비주제 그룹 채팅을 대상으로 하지 않습니다.

### 멀티 에이전트 라우팅

`bindings`를 사용해 Feishu DM 또는 그룹을 서로 다른 agent로 라우팅하세요.

```json5
{
  agents: {
    list: [
      { id: "main" },
      {
        id: "clawd-fan",
        workspace: "/home/user/clawd-fan",
        agentDir: "/home/user/.openclaw/agents/clawd-fan/agent",
      },
      {
        id: "clawd-xi",
        workspace: "/home/user/clawd-xi",
        agentDir: "/home/user/.openclaw/agents/clawd-xi/agent",
      },
    ],
  },
  bindings: [
    {
      agentId: "main",
      match: {
        channel: "feishu",
        peer: { kind: "direct", id: "ou_xxx" },
      },
    },
    {
      agentId: "clawd-fan",
      match: {
        channel: "feishu",
        peer: { kind: "direct", id: "ou_yyy" },
      },
    },
    {
      agentId: "clawd-xi",
      match: {
        channel: "feishu",
        peer: { kind: "group", id: "oc_zzz" },
      },
    },
  ],
}
```

라우팅 필드:

- `match.channel`: `"feishu"`
- `match.peer.kind`: `"direct"` 또는 `"group"`
- `match.peer.id`: 사용자 Open ID(`ou_xxx`) 또는 그룹 ID(`oc_xxx`)

조회 팁은 [그룹/사용자 ID 가져오기](#get-groupuser-ids)를 참조하세요.

---

## 구성 참조

전체 구성: [Gateway configuration](/gateway/configuration)

주요 옵션:

| 설정 | 설명 | 기본값 |
| ------------------------------------------------- | --------------------------------------- | ---------------- |
| `channels.feishu.enabled`                         | 채널 활성화/비활성화 | `true`           |
| `channels.feishu.domain`                          | API 도메인(`feishu` 또는 `lark`) | `feishu`         |
| `channels.feishu.connectionMode`                  | 이벤트 전송 모드 | `websocket`      |
| `channels.feishu.defaultAccount`                  | 아웃바운드 라우팅용 기본 계정 ID | `default`        |
| `channels.feishu.verificationToken`               | webhook 모드에 필요 | -                |
| `channels.feishu.encryptKey`                      | webhook 모드에 필요 | -                |
| `channels.feishu.webhookPath`                     | webhook 라우트 경로 | `/feishu/events` |
| `channels.feishu.webhookHost`                     | webhook 바인드 호스트 | `127.0.0.1`      |
| `channels.feishu.webhookPort`                     | webhook 바인드 포트 | `3000`           |
| `channels.feishu.accounts.<id>.appId`             | App ID | -                |
| `channels.feishu.accounts.<id>.appSecret`         | App Secret | -                |
| `channels.feishu.accounts.<id>.domain`            | 계정별 API 도메인 재정의 | `feishu`         |
| `channels.feishu.dmPolicy`                        | DM 정책 | `pairing`        |
| `channels.feishu.allowFrom`                       | DM allowlist(open_id 목록) | -                |
| `channels.feishu.groupPolicy`                     | 그룹 정책 | `allowlist`      |
| `channels.feishu.groupAllowFrom`                  | 그룹 allowlist | -                |
| `channels.feishu.requireMention`                  | 기본 @mention 필요 여부 | conditional      |
| `channels.feishu.groups.<chat_id>.requireMention` | 그룹별 @mention 필요 여부 재정의 | inherited        |
| `channels.feishu.groups.<chat_id>.enabled`        | 그룹 활성화 | `true`           |
| `channels.feishu.textChunkLimit`                  | 메시지 청크 크기 | `2000`           |
| `channels.feishu.mediaMaxMb`                      | 미디어 크기 제한 | `30`             |
| `channels.feishu.streaming`                       | 스트리밍 카드 출력 활성화 | `true`           |
| `channels.feishu.blockStreaming`                  | 블록 스트리밍 활성화 | `true`           |

---

## dmPolicy 참조

| 값 | 동작 |
| ------------- | --------------------------------------------------------------- |
| `"pairing"`   | **기본값.** 알 수 없는 사용자는 페어링 코드를 받으며, 승인이 필요함 |
| `"allowlist"` | `allowFrom`에 있는 사용자만 대화 가능 |
| `"open"`      | 모든 사용자 허용(`allowFrom`에 `"*"` 필요) |
| `"disabled"`  | DM 비활성화 |

---

## 지원되는 메시지 유형

### 수신

- ✅ 텍스트
- ✅ 리치 텍스트(post)
- ✅ 이미지
- ✅ 파일
- ✅ 오디오
- ✅ 비디오/미디어
- ✅ 스티커

### 전송

- ✅ 텍스트
- ✅ 이미지
- ✅ 파일
- ✅ 오디오
- ✅ 비디오/미디어
- ✅ 인터랙티브 카드
- ⚠️ 리치 텍스트(post 스타일 서식 및 카드, 임의의 Feishu 작성 기능 전체는 아님)

### 스레드 및 응답

- ✅ 인라인 응답
- ✅ Feishu가 `reply_in_thread`를 노출하는 경우 주제 스레드 응답
- ✅ 스레드/주제 메시지에 응답할 때 미디어 응답도 스레드 인식을 유지함

## Drive 댓글

사용자가 Feishu Drive 문서(Docs, Sheets 등)에 댓글을 추가하면 Feishu가 agent를 트리거할 수 있습니다. agent는 댓글 텍스트, 문서 컨텍스트, 댓글 스레드를 받아 스레드 내에서 응답하거나 문서를 수정할 수 있습니다.

요구 사항:

- Feishu 앱 이벤트 구독 설정에서 `drive.notice.comment_add_v1`을 구독해야 합니다
  (기존 `im.message.receive_v1`과 함께)
- Drive 도구는 기본적으로 활성화되어 있으며, `channels.feishu.tools.drive: false`로 비활성화할 수 있습니다

`feishu_drive` 도구는 다음 댓글 작업을 제공합니다.

| 작업 | 설명 |
| ---------------------- | ----------------------------------- |
| `list_comments`        | 문서의 댓글 목록 표시 |
| `list_comment_replies` | 댓글 스레드의 응답 목록 표시 |
| `add_comment`          | 새 최상위 댓글 추가 |
| `reply_comment`        | 기존 댓글 스레드에 응답 |

agent가 Drive 댓글 이벤트를 처리할 때 다음을 받습니다.

- 댓글 텍스트와 발신자
- 문서 메타데이터(제목, 유형, URL)
- 스레드 내 응답을 위한 댓글 스레드 컨텍스트

문서를 수정한 후 agent는 댓글 작성자에게 알리기 위해 `feishu_drive.reply_comment`를 사용하고, 중복 전송을 피하기 위해 정확히 `NO_REPLY` / `no_reply` 무음 토큰을 출력하도록 안내됩니다.

## 런타임 작업 표면

현재 Feishu는 다음 런타임 작업을 노출합니다.

- `send`
- `read`
- `edit`
- `thread-reply`
- `pin`
- `list-pins`
- `unpin`
- `member-info`
- `channel-info`
- `channel-list`
- config에서 반응이 활성화된 경우 `react` 및 `reactions`
- `feishu_drive` 댓글 작업: `list_comments`, `list_comment_replies`, `add_comment`, `reply_comment`

## 관련 문서

- [채널 개요](/channels) — 지원되는 모든 채널
- [페어링](/channels/pairing) — DM 인증 및 페어링 흐름
- [그룹](/channels/groups) — 그룹 채팅 동작 및 멘션 게이팅
- [채널 라우팅](/channels/channel-routing) — 메시지의 세션 라우팅
- [보안](/gateway/security) — 액세스 모델 및 하드닝
