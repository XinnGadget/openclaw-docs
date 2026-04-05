---
read_when:
    - Slack을 설정하거나 Slack 소켓/HTTP 모드를 디버깅할 때
summary: Slack 설정 및 런타임 동작(Socket Mode + HTTP Events API)
title: Slack
x-i18n:
    generated_at: "2026-04-05T12:36:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: efb37e1f04e1ac8ac3786c36ffc20013dacdc654bfa61e7f6e8df89c4902d2ab
    source_path: channels/slack.md
    workflow: 15
---

# Slack

상태: Slack 앱 통합을 통한 DM 및 채널용 프로덕션 준비 완료. 기본 모드는 Socket Mode이며, HTTP Events API 모드도 지원됩니다.

<CardGroup cols={3}>
  <Card title="페어링" icon="link" href="/channels/pairing">
    Slack DM은 기본적으로 페어링 모드를 사용합니다.
  </Card>
  <Card title="슬래시 명령" icon="terminal" href="/tools/slash-commands">
    네이티브 명령 동작 및 명령 카탈로그.
  </Card>
  <Card title="채널 문제 해결" icon="wrench" href="/channels/troubleshooting">
    채널 전반의 진단 및 복구 플레이북.
  </Card>
</CardGroup>

## 빠른 설정

<Tabs>
  <Tab title="Socket Mode (기본값)">
    <Steps>
      <Step title="Slack 앱 및 토큰 생성">
        Slack 앱 설정에서 다음을 수행합니다.

        - **Socket Mode** 활성화
        - `connections:write` 권한이 있는 **App Token**(`xapp-...`) 생성
        - 앱을 설치하고 **Bot Token**(`xoxb-...`) 복사
      </Step>

      <Step title="OpenClaw 구성">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket",
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

        환경 변수 대체(default 계정만 해당):

```bash
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
```

      </Step>

      <Step title="앱 이벤트 구독">
        다음에 대한 봇 이벤트를 구독합니다.

        - `app_mention`
        - `message.channels`, `message.groups`, `message.im`, `message.mpim`
        - `reaction_added`, `reaction_removed`
        - `member_joined_channel`, `member_left_channel`
        - `channel_rename`
        - `pin_added`, `pin_removed`

        DM용으로 App Home **Messages Tab**도 활성화합니다.
      </Step>

      <Step title="게이트웨이 시작">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP Events API 모드">
    <Steps>
      <Step title="HTTP용 Slack 앱 구성">

        - 모드를 HTTP로 설정(`channels.slack.mode="http"`)
        - Slack **Signing Secret** 복사
        - Event Subscriptions + Interactivity + Slash command Request URL을 모두 동일한 webhook 경로(기본값 `/slack/events`)로 설정

      </Step>

      <Step title="OpenClaw HTTP 모드 구성">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events",
    },
  },
}
```

      </Step>

      <Step title="멀티 계정 HTTP에 고유 webhook 경로 사용">
        계정별 HTTP 모드가 지원됩니다.

        등록이 충돌하지 않도록 각 계정에 서로 다른 `webhookPath`를 지정하세요.
      </Step>
    </Steps>

  </Tab>
</Tabs>

## 매니페스트 및 범위 체크리스트

<AccordionGroup>
  <Accordion title="Slack 앱 매니페스트 예시" defaultOpen>

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    }
  }
}
```

  </Accordion>

  <Accordion title="선택적 사용자 토큰 범위(읽기 작업)">
    `channels.slack.userToken`을 구성한 경우, 일반적인 읽기 범위는 다음과 같습니다.

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read`(Slack 검색 읽기에 의존하는 경우)

  </Accordion>
</AccordionGroup>

## 토큰 모델

- Socket Mode에는 `botToken` + `appToken`이 필요합니다.
- HTTP 모드에는 `botToken` + `signingSecret`이 필요합니다.
- `botToken`, `appToken`, `signingSecret`, `userToken`은 일반 문자열 또는 SecretRef 객체를 받을 수 있습니다.
- 구성의 토큰이 환경 변수 대체보다 우선합니다.
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` 환경 변수 대체는 default 계정에만 적용됩니다.
- `userToken`(`xoxp-...`)은 구성 전용이며(환경 변수 대체 없음), 기본값은 읽기 전용 동작(`userTokenReadOnly: true`)입니다.
- 선택 사항: 발신 메시지가 활성 에이전트 신원(사용자 지정 `username` 및 아이콘)을 사용하게 하려면 `chat:write.customize`를 추가하세요. `icon_emoji`는 `:emoji_name:` 문법을 사용합니다.

상태 스냅샷 동작:

- Slack 계정 검사는 자격 증명별 `*Source` 및 `*Status` 필드(`botToken`, `appToken`, `signingSecret`, `userToken`)를 추적합니다.
- 상태는 `available`, `configured_unavailable`, `missing`입니다.
- `configured_unavailable`은 계정이 SecretRef 또는 다른 비인라인 비밀 소스를 통해 구성되었지만, 현재 명령/런타임 경로에서 실제 값을 해석할 수 없었음을 의미합니다.
- HTTP 모드에서는 `signingSecretStatus`가 포함되며, Socket Mode에서는 필요한 쌍이 `botTokenStatus` + `appTokenStatus`입니다.

<Tip>
작업/디렉터리 읽기에서는 구성된 경우 사용자 토큰을 우선할 수 있습니다. 쓰기에서는 여전히 봇 토큰이 우선이며, 사용자 토큰 쓰기는 `userTokenReadOnly: false`이고 봇 토큰을 사용할 수 없을 때만 허용됩니다.
</Tip>

## 작업 및 게이트

Slack 작업은 `channels.slack.actions.*`로 제어됩니다.

현재 Slack 도구에서 사용할 수 있는 작업 그룹:

| 그룹 | 기본값 |
| ---------- | ------- |
| messages   | enabled |
| reactions  | enabled |
| pins       | enabled |
| memberInfo | enabled |
| emojiList  | enabled |

현재 Slack 메시지 작업에는 `send`, `upload-file`, `download-file`, `read`, `edit`, `delete`, `pin`, `unpin`, `list-pins`, `member-info`, `emoji-list`가 포함됩니다.

## 접근 제어 및 라우팅

<Tabs>
  <Tab title="DM 정책">
    `channels.slack.dmPolicy`가 DM 접근을 제어합니다(레거시: `channels.slack.dm.policy`).

    - `pairing`(기본값)
    - `allowlist`
    - `open`(`channels.slack.allowFrom`에 `"*"`가 포함되어야 함; 레거시: `channels.slack.dm.allowFrom`)
    - `disabled`

    DM 플래그:

    - `dm.enabled`(기본값 true)
    - `channels.slack.allowFrom`(권장)
    - `dm.allowFrom`(레거시)
    - `dm.groupEnabled`(그룹 DM 기본값 false)
    - `dm.groupChannels`(선택적 MPIM allowlist)

    멀티 계정 우선순위:

    - `channels.slack.accounts.default.allowFrom`은 `default` 계정에만 적용됩니다.
    - 이름 있는 계정은 자체 `allowFrom`이 설정되지 않은 경우 `channels.slack.allowFrom`을 상속합니다.
    - 이름 있는 계정은 `channels.slack.accounts.default.allowFrom`을 상속하지 않습니다.

    DM의 페어링은 `openclaw pairing approve slack <code>`를 사용합니다.

  </Tab>

  <Tab title="채널 정책">
    `channels.slack.groupPolicy`가 채널 처리를 제어합니다.

    - `open`
    - `allowlist`
    - `disabled`

    채널 allowlist는 `channels.slack.channels` 아래에 있으며, 안정적인 채널 ID를 사용해야 합니다.

    런타임 참고: `channels.slack`이 완전히 없는 경우(환경 변수 전용 설정), 런타임은 `channels.defaults.groupPolicy`가 설정되어 있더라도 `groupPolicy="allowlist"`로 대체하고 경고를 기록합니다.

    이름/ID 해석:

    - 채널 allowlist 항목과 DM allowlist 항목은 토큰 접근이 허용되면 시작 시 해석됩니다
    - 해석되지 않은 채널 이름 항목은 구성된 상태로 유지되지만 기본적으로 라우팅에서는 무시됩니다
    - 인바운드 권한 부여와 채널 라우팅은 기본적으로 ID 우선이며, 직접 사용자 이름/슬러그 일치를 사용하려면 `channels.slack.dangerouslyAllowNameMatching: true`가 필요합니다

  </Tab>

  <Tab title="멘션 및 채널 사용자">
    채널 메시지는 기본적으로 멘션 게이팅이 적용됩니다.

    멘션 소스:

    - 명시적 앱 멘션(`<@botId>`)
    - 멘션 정규식 패턴(`agents.list[].groupChat.mentionPatterns`, 대체값 `messages.groupChat.mentionPatterns`)
    - 암묵적인 봇 답글 스레드 동작

    채널별 제어(`channels.slack.channels.<id>`; 이름은 시작 시 해석 또는 `dangerouslyAllowNameMatching`을 통해서만 가능):

    - `requireMention`
    - `users`(allowlist)
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - `toolsBySender` 키 형식: `id:`, `e164:`, `username:`, `name:`, 또는 `"*"` 와일드카드
      (레거시 접두사 없는 키도 여전히 `id:` 전용으로 매핑됨)

  </Tab>
</Tabs>

## 스레딩, 세션 및 답글 태그

- DM은 `direct`로, 채널은 `channel`로, MPIM은 `group`으로 라우팅됩니다.
- 기본 `session.dmScope=main`에서는 Slack DM이 에이전트 메인 세션으로 합쳐집니다.
- 채널 세션: `agent:<agentId>:slack:channel:<channelId>`.
- 스레드 답글은 해당되는 경우 스레드 세션 접미사(`:thread:<threadTs>`)를 만들 수 있습니다.
- `channels.slack.thread.historyScope` 기본값은 `thread`이고, `thread.inheritParent` 기본값은 `false`입니다.
- `channels.slack.thread.initialHistoryLimit`는 새 스레드 세션이 시작될 때 가져오는 기존 스레드 메시지 수를 제어합니다(기본값 `20`; 비활성화하려면 `0` 설정).

답글 스레딩 제어:

- `channels.slack.replyToMode`: `off|first|all`(기본값 `off`)
- `channels.slack.replyToModeByChatType`: `direct|group|channel`별
- 직접 채팅용 레거시 대체: `channels.slack.dm.replyToMode`

수동 답글 태그가 지원됩니다.

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

참고: `replyToMode="off"`는 Slack의 **모든** 답글 스레딩을 비활성화하며, 명시적인 `[[reply_to_*]]` 태그도 포함됩니다. 이는 명시적 태그가 `"off"` 모드에서도 계속 존중되는 Telegram과 다릅니다. 이 차이는 플랫폼의 스레딩 모델을 반영합니다. Slack 스레드는 채널에서 메시지를 숨기지만, Telegram 답글은 메인 채팅 흐름에서 계속 보입니다.

## 확인 반응

`ackReaction`은 OpenClaw가 인바운드 메시지를 처리하는 동안 확인 이모지를 전송합니다.

해결 순서:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- 에이전트 신원 이모지 대체값(`agents.list[].identity.emoji`, 없으면 "👀")

참고:

- Slack은 shortcode를 기대합니다(예: `"eyes"`).
- Slack 계정 또는 전역에서 반응을 비활성화하려면 `""`를 사용하세요.

## 텍스트 스트리밍

`channels.slack.streaming`은 라이브 미리보기 동작을 제어합니다.

- `off`: 라이브 미리보기 스트리밍 비활성화
- `partial`(기본값): 미리보기 텍스트를 최신 부분 출력으로 교체
- `block`: 청크 단위 미리보기 업데이트를 추가
- `progress`: 생성 중 진행 상태 텍스트를 표시한 다음 최종 텍스트 전송

`channels.slack.nativeStreaming`은 `streaming`이 `partial`일 때 Slack 네이티브 텍스트 스트리밍을 제어합니다(기본값: `true`).

- 네이티브 텍스트 스트리밍이 표시되려면 답글 스레드를 사용할 수 있어야 합니다. 스레드 선택은 여전히 `replyToMode`를 따릅니다. 스레드가 없으면 일반 초안 미리보기가 사용됩니다.
- 미디어 및 비텍스트 페이로드는 일반 전달로 대체됩니다.
- 스트리밍이 답글 도중 실패하면 OpenClaw는 남은 페이로드에 대해 일반 전달로 대체합니다.

Slack 네이티브 텍스트 스트리밍 대신 초안 미리보기를 사용하려면:

```json5
{
  channels: {
    slack: {
      streaming: "partial",
      nativeStreaming: false,
    },
  },
}
```

레거시 키:

- `channels.slack.streamMode`(`replace | status_final | append`)는 자동으로 `channels.slack.streaming`으로 마이그레이션됩니다.
- 불리언 `channels.slack.streaming`은 자동으로 `channels.slack.nativeStreaming`으로 마이그레이션됩니다.

## 타이핑 반응 대체

`typingReaction`은 OpenClaw가 답글을 처리하는 동안 인바운드 Slack 메시지에 임시 반응을 추가하고, 실행이 끝나면 제거합니다. 이는 기본 "is typing..." 상태 표시기를 사용하는 스레드 답글 외부에서 특히 유용합니다.

해결 순서:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

참고:

- Slack은 shortcode를 기대합니다(예: `"hourglass_flowing_sand"`).
- 이 반응은 best-effort이며, 답글 또는 실패 경로가 완료된 뒤 정리가 자동으로 시도됩니다.

## 미디어, 청크 분할 및 전달

<AccordionGroup>
  <Accordion title="인바운드 첨부 파일">
    Slack 파일 첨부는 Slack이 호스팅하는 비공개 URL에서 다운로드되며(토큰 인증 요청 흐름), 가져오기에 성공하고 크기 제한을 충족하면 미디어 저장소에 기록됩니다.

    런타임 인바운드 크기 상한은 `channels.slack.mediaMaxMb`로 재정의하지 않는 한 기본적으로 `20MB`입니다.

  </Accordion>

  <Accordion title="아웃바운드 텍스트 및 파일">
    - 텍스트 청크는 `channels.slack.textChunkLimit`을 사용합니다(기본값 4000)
    - `channels.slack.chunkMode="newline"`은 문단 우선 분할을 활성화합니다
    - 파일 전송은 Slack 업로드 API를 사용하며 스레드 답글(`thread_ts`)을 포함할 수 있습니다
    - 아웃바운드 미디어 상한은 구성된 경우 `channels.slack.mediaMaxMb`를 따르며, 그렇지 않으면 채널 전송은 미디어 파이프라인의 MIME 종류 기본값을 사용합니다
  </Accordion>

  <Accordion title="전달 대상">
    권장되는 명시적 대상:

    - DM용 `user:<id>`
    - 채널용 `channel:<id>`

    Slack DM은 사용자 대상에 전송할 때 Slack 대화 API를 통해 열립니다.

  </Accordion>
</AccordionGroup>

## 명령 및 슬래시 동작

- Slack에서는 네이티브 명령 자동 모드가 **꺼짐**입니다(`commands.native: "auto"`는 Slack 네이티브 명령을 활성화하지 않음).
- `channels.slack.commands.native: true`(또는 전역 `commands.native: true`)로 네이티브 Slack 명령 핸들러를 활성화하세요.
- 네이티브 명령이 활성화되면, Slack에 일치하는 슬래시 명령(`/<command>` 이름)을 등록하세요. 단, 예외가 하나 있습니다.
  - 상태 명령에는 `/agentstatus`를 등록하세요(Slack은 `/status`를 예약함)
- 네이티브 명령이 활성화되지 않은 경우, `channels.slack.slashCommand`를 통해 하나의 구성된 슬래시 명령을 실행할 수 있습니다.
- 네이티브 인수 메뉴는 이제 렌더링 전략을 적응적으로 선택합니다.
  - 최대 5개 옵션: 버튼 블록
  - 6-100개 옵션: 정적 선택 메뉴
  - 100개 초과 옵션: interactivity 옵션 핸들러를 사용할 수 있을 때 비동기 옵션 필터링이 있는 외부 선택
  - 인코딩된 옵션 값이 Slack 제한을 초과하면 흐름은 버튼으로 대체됩니다
- 긴 옵션 페이로드의 경우, Slash command 인수 메뉴는 선택한 값을 디스패치하기 전에 확인 대화상자를 사용합니다.

기본 슬래시 명령 설정:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

슬래시 세션은 격리된 키를 사용합니다.

- `agent:<agentId>:slack:slash:<userId>`

또한 명령 실행은 대상 대화 세션(`CommandTargetSessionKey`)에 대해 계속 라우팅됩니다.

## 대화형 답글

Slack은 에이전트가 작성한 대화형 답글 제어를 렌더링할 수 있지만, 이 기능은 기본적으로 비활성화되어 있습니다.

전역으로 활성화:

```json5
{
  channels: {
    slack: {
      capabilities: {
        interactiveReplies: true,
      },
    },
  },
}
```

또는 하나의 Slack 계정에 대해서만 활성화:

```json5
{
  channels: {
    slack: {
      accounts: {
        ops: {
          capabilities: {
            interactiveReplies: true,
          },
        },
      },
    },
  },
}
```

활성화되면 에이전트는 Slack 전용 답글 지시문을 출력할 수 있습니다.

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

이 지시문은 Slack Block Kit으로 컴파일되며, 클릭 또는 선택은 기존 Slack 상호작용 이벤트 경로를 통해 다시 라우팅됩니다.

참고:

- 이것은 Slack 전용 UI입니다. 다른 채널은 Slack Block Kit 지시문을 자체 버튼 시스템으로 번역하지 않습니다.
- 대화형 콜백 값은 에이전트가 작성한 원시 값이 아니라 OpenClaw가 생성한 불투명 토큰입니다.
- 생성된 대화형 블록이 Slack Block Kit 제한을 초과하면, OpenClaw는 잘못된 blocks 페이로드를 보내는 대신 원래 텍스트 답글로 대체합니다.

## Slack의 exec 승인

Slack은 Web UI나 터미널로 대체하는 대신, 대화형 버튼과 상호작용을 갖춘 네이티브 승인 클라이언트로 동작할 수 있습니다.

- Exec 승인은 네이티브 DM/채널 라우팅을 위해 `channels.slack.execApprovals.*`를 사용합니다.
- 플러그인 승인은 요청이 이미 Slack에 도착했고 승인 ID 종류가 `plugin:`일 때 동일한 Slack 네이티브 버튼 표면을 통해 계속 해석될 수 있습니다.
- 승인자 권한 부여는 여전히 강제됩니다. 승인자로 식별된 사용자만 Slack을 통해 요청을 승인하거나 거부할 수 있습니다.

이는 다른 채널과 동일한 공유 승인 버튼 표면을 사용합니다. Slack 앱 설정에서 `interactivity`가 활성화되어 있으면, 승인 프롬프트가 대화에 직접 Block Kit 버튼으로 렌더링됩니다.
이 버튼이 있을 때는 그것이 기본 승인 UX가 되며, OpenClaw는 도구 결과에서 채팅 승인을 사용할 수 없거나 수동 승인이 유일한 경로라고 표시하는 경우에만 수동 `/approve` 명령을 포함해야 합니다.

구성 경로:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers`(선택 사항, 가능하면 `commands.ownerAllowFrom`으로 대체)
- `channels.slack.execApprovals.target`(`dm` | `channel` | `both`, 기본값: `dm`)
- `agentFilter`, `sessionFilter`

Slack은 `enabled`가 설정되지 않았거나 `"auto"`이고 최소 한 명의 승인자가 해석되면 네이티브 exec 승인을 자동으로 활성화합니다. Slack을 네이티브 승인 클라이언트로 명시적으로 비활성화하려면 `enabled: false`로 설정하세요.
승인자가 해석될 때 네이티브 승인을 강제로 켜려면 `enabled: true`로 설정하세요.

명시적인 Slack exec 승인 구성이 없을 때의 기본 동작:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

명시적인 Slack 네이티브 구성은 승인자를 재정의하거나, 필터를 추가하거나, origin-chat 전달을 선택하려는 경우에만 필요합니다.

```json5
{
  channels: {
    slack: {
      execApprovals: {
        enabled: true,
        approvers: ["U12345678"],
        target: "both",
      },
    },
  },
}
```

공유 `approvals.exec` 전달은 별개입니다. exec 승인 프롬프트를 다른 채팅이나 명시적인 대역 외 대상으로도 라우팅해야 할 때만 사용하세요. 공유 `approvals.plugin` 전달도 별개이며, Slack 네이티브 버튼은 해당 요청이 이미 Slack에 도착한 경우 계속 플러그인 승인을 해석할 수 있습니다.

동일 채팅의 `/approve`도 이미 명령을 지원하는 Slack 채널과 DM에서 동작합니다. 전체 승인 전달 모델은 [Exec approvals](/tools/exec-approvals)를 참조하세요.

## 이벤트 및 운영 동작

- 메시지 편집/삭제/스레드 브로드캐스트는 시스템 이벤트로 매핑됩니다.
- 반응 추가/제거 이벤트는 시스템 이벤트로 매핑됩니다.
- 멤버 참여/퇴장, 채널 생성/이름 변경, 핀 추가/제거 이벤트는 시스템 이벤트로 매핑됩니다.
- `channel_id_changed`는 `configWrites`가 활성화된 경우 채널 구성 키를 마이그레이션할 수 있습니다.
- 채널 topic/purpose 메타데이터는 신뢰할 수 없는 컨텍스트로 취급되며 라우팅 컨텍스트에 주입될 수 있습니다.
- 스레드 시작자와 초기 스레드 기록 컨텍스트 시딩은 해당되는 경우 구성된 발신자 allowlist로 필터링됩니다.
- 블록 작업 및 모달 상호작용은 풍부한 페이로드 필드와 함께 구조화된 `Slack interaction: ...` 시스템 이벤트를 발생시킵니다.
  - 블록 작업: 선택된 값, 라벨, picker 값, `workflow_*` 메타데이터
  - 라우팅된 채널 메타데이터와 폼 입력이 포함된 모달 `view_submission` 및 `view_closed` 이벤트

## 구성 참조 포인터

기본 참조:

- [구성 참조 - Slack](/gateway/configuration-reference#slack)

  신호가 강한 Slack 필드:
  - 모드/인증: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM 접근: `dm.enabled`, `dmPolicy`, `allowFrom`(레거시: `dm.policy`, `dm.allowFrom`), `dm.groupEnabled`, `dm.groupChannels`
  - 호환성 토글: `dangerouslyAllowNameMatching`(비상용, 필요하지 않다면 꺼두기)
  - 채널 접근: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - 스레딩/기록: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - 전달: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - 운영/기능: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## 문제 해결

<AccordionGroup>
  <Accordion title="채널에서 답글이 없음">
    다음 순서로 확인하세요.

    - `groupPolicy`
    - 채널 allowlist(`channels.slack.channels`)
    - `requireMention`
    - 채널별 `users` allowlist

    유용한 명령:

```bash
openclaw channels status --probe
openclaw logs --follow
openclaw doctor
```

  </Accordion>

  <Accordion title="DM 메시지가 무시됨">
    다음을 확인하세요.

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy`(또는 레거시 `channels.slack.dm.policy`)
    - 페어링 승인 / allowlist 항목

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket mode가 연결되지 않음">
    봇 토큰 + 앱 토큰, 그리고 Slack 앱 설정의 Socket Mode 활성화를 검증하세요.

    `openclaw channels status --probe --json`에 `botTokenStatus` 또는
    `appTokenStatus: "configured_unavailable"`가 표시되면, Slack 계정은
    구성되어 있지만 현재 런타임이 SecretRef 기반 값을 해석할 수 없었다는 뜻입니다.

  </Accordion>

  <Accordion title="HTTP mode가 이벤트를 수신하지 않음">
    다음을 검증하세요.

    - signing secret
    - webhook 경로
    - Slack Request URL(Events + Interactivity + Slash Commands)
    - HTTP 계정별 고유 `webhookPath`

    계정 스냅샷에 `signingSecretStatus: "configured_unavailable"`가 나타나면,
    HTTP 계정은 구성되어 있지만 현재 런타임이 SecretRef 기반 signing secret을
    해석할 수 없었다는 뜻입니다.

  </Accordion>

  <Accordion title="네이티브/슬래시 명령이 실행되지 않음">
    의도한 방식이 다음 중 어느 것인지 확인하세요.

    - Slack에 일치하는 슬래시 명령을 등록한 네이티브 명령 모드(`channels.slack.commands.native: true`)
    - 또는 단일 슬래시 명령 모드(`channels.slack.slashCommand.enabled: true`)

    또한 `commands.useAccessGroups`와 채널/사용자 allowlist도 확인하세요.

  </Accordion>
</AccordionGroup>

## 관련 항목

- [페어링](/channels/pairing)
- [그룹](/channels/groups)
- [Security](/gateway/security)
- [채널 라우팅](/channels/channel-routing)
- [문제 해결](/channels/troubleshooting)
- [구성](/gateway/configuration)
- [슬래시 명령](/tools/slash-commands)
