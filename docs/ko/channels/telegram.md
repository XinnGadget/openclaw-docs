---
read_when:
    - Telegram 기능 또는 webhook 작업 중
summary: Telegram 봇 지원 상태, 기능 및 구성
title: Telegram
x-i18n:
    generated_at: "2026-04-05T12:38:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: 39fbf328375fbc5d08ec2e3eed58b19ee0afa102010ecbc02e074a310ced157e
    source_path: channels/telegram.md
    workflow: 15
---

# Telegram (Bot API)

상태: grammY를 통한 봇 DM 및 그룹용 프로덕션 준비 완료. 롱 폴링이 기본 모드이며 webhook 모드는 선택 사항입니다.

<CardGroup cols={3}>
  <Card title="페어링" icon="link" href="/channels/pairing">
    Telegram의 기본 DM 정책은 페어링입니다.
  </Card>
  <Card title="채널 문제 해결" icon="wrench" href="/channels/troubleshooting">
    채널 전반의 진단 및 복구 플레이북입니다.
  </Card>
  <Card title="Gateway 구성" icon="settings" href="/gateway/configuration">
    전체 채널 config 패턴과 예시입니다.
  </Card>
</CardGroup>

## 빠른 설정

<Steps>
  <Step title="BotFather에서 봇 토큰 만들기">
    Telegram을 열고 **@BotFather**와 채팅하세요(핸들이 정확히 `@BotFather`인지 확인).

    `/newbot`을 실행하고 안내를 따른 뒤 토큰을 저장하세요.

  </Step>

  <Step title="토큰 및 DM 정책 구성">

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123:abc",
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

    환경 변수 대체: `TELEGRAM_BOT_TOKEN=...` (기본 계정만).
    Telegram은 `openclaw channels login telegram`을 사용하지 **않습니다**. config/env에 토큰을 구성한 뒤 gateway를 시작하세요.

  </Step>

  <Step title="gateway 시작 및 첫 DM 승인">

```bash
openclaw gateway
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

    페어링 코드는 1시간 후 만료됩니다.

  </Step>

  <Step title="그룹에 봇 추가">
    그룹에 봇을 추가한 다음 액세스 모델에 맞게 `channels.telegram.groups`와 `groupPolicy`를 설정하세요.
  </Step>
</Steps>

<Note>
토큰 해석 순서는 계정 인식을 지원합니다. 실제로는 config 값이 환경 변수 대체보다 우선하며, `TELEGRAM_BOT_TOKEN`은 기본 계정에만 적용됩니다.
</Note>

## Telegram 측 설정

<AccordionGroup>
  <Accordion title="개인정보 보호 모드 및 그룹 가시성">
    Telegram 봇은 기본적으로 **개인정보 보호 모드**가 활성화되어 있어, 수신할 수 있는 그룹 메시지가 제한됩니다.

    봇이 모든 그룹 메시지를 봐야 한다면 다음 중 하나를 수행하세요.

    - `/setprivacy`로 개인정보 보호 모드를 비활성화하거나
    - 봇을 그룹 관리자로 설정합니다.

    개인정보 보호 모드를 전환한 경우, Telegram이 변경 사항을 적용할 수 있도록 각 그룹에서 봇을 제거했다가 다시 추가하세요.

  </Accordion>

  <Accordion title="그룹 권한">
    관리자 상태는 Telegram 그룹 설정에서 제어됩니다.

    관리자 봇은 모든 그룹 메시지를 수신하므로 항상 활성화된 그룹 동작에 유용합니다.

  </Accordion>

  <Accordion title="유용한 BotFather 토글">

    - 그룹 추가 허용/거부용 `/setjoingroups`
    - 그룹 가시성 동작용 `/setprivacy`

  </Accordion>
</AccordionGroup>

## 액세스 제어 및 활성화

<Tabs>
  <Tab title="DM 정책">
    `channels.telegram.dmPolicy`는 다이렉트 메시지 액세스를 제어합니다.

    - `pairing` (기본값)
    - `allowlist` (`allowFrom`에 발신자 ID가 최소 하나 필요)
    - `open` (`allowFrom`에 `"*"` 포함 필요)
    - `disabled`

    `channels.telegram.allowFrom`은 숫자형 Telegram 사용자 ID를 받습니다. `telegram:` / `tg:` 접두사는 허용되며 정규화됩니다.
    빈 `allowFrom`과 함께 `dmPolicy: "allowlist"`를 사용하면 모든 DM이 차단되며 config 유효성 검사에서 거부됩니다.
    온보딩은 `@username` 입력을 받아 숫자형 ID로 해석합니다.
    업그레이드 후 config에 `@username` allowlist 항목이 있다면, 이를 해석하려면 `openclaw doctor --fix`를 실행하세요(최선 시도 방식이며 Telegram 봇 토큰이 필요합니다).
    이전에 페어링 저장소 allowlist 파일에 의존했다면, `openclaw doctor --fix`가 allowlist 흐름에서 해당 항목을 `channels.telegram.allowFrom`으로 복구할 수 있습니다(예: `dmPolicy: "allowlist"`에 아직 명시적 ID가 없는 경우).

    단일 소유자 봇의 경우, 이전 페어링 승인에 의존하는 대신 액세스 정책을 config에 안정적으로 유지하기 위해 명시적 숫자형 `allowFrom` ID와 함께 `dmPolicy: "allowlist"`를 사용하는 것을 권장합니다.

    흔한 혼동: DM 페어링 승인은 "이 발신자가 어디서나 인증되었다"는 의미가 아닙니다.
    페어링은 DM 액세스만 부여합니다. 그룹 발신자 인증은 여전히 명시적 config allowlist에서 옵니다.
    "한 번 인증되면 DM과 그룹 명령 모두 동작"하게 하려면 숫자형 Telegram 사용자 ID를 `channels.telegram.allowFrom`에 넣으세요.

    ### 내 Telegram 사용자 ID 찾기

    더 안전한 방법(서드파티 봇 없음):

    1. 봇에 DM을 보냅니다.
    2. `openclaw logs --follow`를 실행합니다.
    3. `from.id`를 읽습니다.

    공식 Bot API 방법:

```bash
curl "https://api.telegram.org/bot<bot_token>/getUpdates"
```

    서드파티 방법(개인정보 보호 수준 낮음): `@userinfobot` 또는 `@getidsbot`.

  </Tab>

  <Tab title="그룹 정책 및 allowlist">
    두 가지 제어가 함께 적용됩니다.

    1. **어떤 그룹이 허용되는지** (`channels.telegram.groups`)
       - `groups` config가 없는 경우:
         - `groupPolicy: "open"`일 때: 어떤 그룹이든 그룹 ID 검사 통과 가능
         - `groupPolicy: "allowlist"`(기본값)일 때: `groups` 항목(또는 `"*"`)을 추가할 때까지 그룹 차단
       - `groups`가 구성된 경우: allowlist 역할 수행(명시적 ID 또는 `"*"`)

    2. **그룹에서 어떤 발신자가 허용되는지** (`channels.telegram.groupPolicy`)
       - `open`
       - `allowlist` (기본값)
       - `disabled`

    `groupAllowFrom`은 그룹 발신자 필터링에 사용됩니다. 설정되지 않으면 Telegram은 `allowFrom`으로 대체합니다.
    `groupAllowFrom` 항목은 숫자형 Telegram 사용자 ID여야 합니다(`telegram:` / `tg:` 접두사는 정규화됨).
    Telegram 그룹 또는 슈퍼그룹 채팅 ID를 `groupAllowFrom`에 넣지 마세요. 음수 채팅 ID는 `channels.telegram.groups` 아래에 있어야 합니다.
    숫자가 아닌 항목은 발신자 인증에서 무시됩니다.
    보안 경계(`2026.2.25+`): 그룹 발신자 인증은 DM 페어링 저장소 승인을 **상속하지 않습니다**.
    페어링은 DM 전용으로 유지됩니다. 그룹의 경우 `groupAllowFrom` 또는 그룹별/토픽별 `allowFrom`을 설정하세요.
    `groupAllowFrom`이 설정되지 않으면 Telegram은 페어링 저장소가 아니라 config의 `allowFrom`으로 대체합니다.
    단일 소유자 봇의 실용적인 패턴: 사용자 ID를 `channels.telegram.allowFrom`에 설정하고, `groupAllowFrom`은 비워 두며, 대상 그룹은 `channels.telegram.groups` 아래에서 허용하세요.
    런타임 참고: `channels.telegram`이 완전히 없으면, `channels.defaults.groupPolicy`가 명시적으로 설정되지 않은 한 런타임 기본값은 fail-closed `groupPolicy="allowlist"`입니다.

    예시: 특정 그룹 하나에서 모든 멤버 허용:

```json5
{
  channels: {
    telegram: {
      groups: {
        "-1001234567890": {
          groupPolicy: "open",
          requireMention: false,
        },
      },
    },
  },
}
```

    예시: 특정 그룹 하나에서 특정 사용자만 허용:

```json5
{
  channels: {
    telegram: {
      groups: {
        "-1001234567890": {
          requireMention: true,
          allowFrom: ["8734062810", "745123456"],
        },
      },
    },
  },
}
```

    <Warning>
      흔한 실수: `groupAllowFrom`은 Telegram 그룹 allowlist가 아닙니다.

      - `-1001234567890` 같은 음수 Telegram 그룹 또는 슈퍼그룹 채팅 ID는 `channels.telegram.groups` 아래에 넣으세요.
      - 허용된 그룹 안에서 봇을 트리거할 수 있는 사람을 제한하려면 `8734062810` 같은 Telegram 사용자 ID를 `groupAllowFrom` 아래에 넣으세요.
      - 허용된 그룹의 아무 멤버나 봇과 대화할 수 있게 하려면 `groupAllowFrom: ["*"]`를 사용하세요.
    </Warning>

  </Tab>

  <Tab title="멘션 동작">
    그룹 응답은 기본적으로 멘션이 필요합니다.

    멘션은 다음에서 올 수 있습니다.

    - 기본 `@botusername` 멘션
    - 또는 다음의 멘션 패턴:
      - `agents.list[].groupChat.mentionPatterns`
      - `messages.groupChat.mentionPatterns`

    세션 수준 명령 토글:

    - `/activation always`
    - `/activation mention`

    이 명령은 세션 상태만 업데이트합니다. 영구 저장에는 config를 사용하세요.

    영구 config 예시:

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { requireMention: false },
      },
    },
  },
}
```

    그룹 채팅 ID 가져오기:

    - 그룹 메시지를 `@userinfobot` / `@getidsbot`으로 전달
    - 또는 `openclaw logs --follow`에서 `chat.id` 읽기
    - 또는 Bot API `getUpdates` 검사

  </Tab>
</Tabs>

## 런타임 동작

- Telegram은 gateway 프로세스가 소유합니다.
- 라우팅은 결정적입니다. Telegram 인바운드 메시지는 Telegram으로 응답합니다(모델이 채널을 선택하지 않음).
- 인바운드 메시지는 응답 메타데이터와 미디어 플레이스홀더를 포함하는 공유 채널 envelope로 정규화됩니다.
- 그룹 세션은 그룹 ID별로 격리됩니다. 포럼 토픽은 토픽 격리를 위해 `:topic:<threadId>`를 덧붙입니다.
- DM 메시지는 `message_thread_id`를 포함할 수 있습니다. OpenClaw는 이를 스레드 인식 세션 키로 라우팅하고 응답 시 스레드 ID를 유지합니다.
- 롱 폴링은 채팅별/스레드별 순서를 보장하는 grammY runner를 사용합니다. 전체 runner sink 동시성은 `agents.defaults.maxConcurrent`를 사용합니다.
- Telegram Bot API에는 읽음 확인 지원이 없습니다(`sendReadReceipts`는 적용되지 않음).

## 기능 참조

<AccordionGroup>
  <Accordion title="실시간 스트림 미리보기(메시지 편집)">
    OpenClaw는 부분 응답을 실시간으로 스트리밍할 수 있습니다.

    - 다이렉트 채팅: 미리보기 메시지 + `editMessageText`
    - 그룹/토픽: 미리보기 메시지 + `editMessageText`

    요구 사항:

    - `channels.telegram.streaming`이 `off | partial | block | progress`여야 합니다(기본값: `partial`)
    - `progress`는 Telegram에서 `partial`로 매핑됩니다(채널 간 명명 호환성용)
    - 레거시 `channels.telegram.streamMode`와 불리언 `streaming` 값은 자동 매핑됩니다

    텍스트 전용 응답의 경우:

    - DM: OpenClaw는 동일한 미리보기 메시지를 유지하고 최종 편집을 그 자리에서 수행합니다(두 번째 메시지 없음)
    - 그룹/토픽: OpenClaw는 동일한 미리보기 메시지를 유지하고 최종 편집을 그 자리에서 수행합니다(두 번째 메시지 없음)

    복합 응답(예: 미디어 payload)의 경우, OpenClaw는 일반 최종 전송으로 대체한 후 미리보기 메시지를 정리합니다.

    미리보기 스트리밍은 블록 스트리밍과 별개입니다. Telegram에 대해 블록 스트리밍이 명시적으로 활성화되면 OpenClaw는 이중 스트리밍을 피하기 위해 미리보기 스트림을 건너뜁니다.

    기본 초안 전송이 사용할 수 없거나 거부되면 OpenClaw는 자동으로 `sendMessage` + `editMessageText`로 대체합니다.

    Telegram 전용 reasoning 스트림:

    - `/reasoning stream`은 생성 중 reasoning을 실시간 미리보기로 보냅니다
    - 최종 답변은 reasoning 텍스트 없이 전송됩니다

  </Accordion>

  <Accordion title="서식 및 HTML 대체">
    아웃바운드 텍스트는 Telegram `parse_mode: "HTML"`을 사용합니다.

    - Markdown 유사 텍스트는 Telegram에 안전한 HTML로 렌더링됩니다.
    - 원시 모델 HTML은 Telegram 파싱 실패를 줄이기 위해 이스케이프됩니다.
    - Telegram이 파싱된 HTML을 거부하면 OpenClaw는 일반 텍스트로 재시도합니다.

    링크 미리보기는 기본적으로 활성화되어 있으며 `channels.telegram.linkPreview: false`로 비활성화할 수 있습니다.

  </Accordion>

  <Accordion title="기본 명령 및 사용자 지정 명령">
    Telegram 명령 메뉴 등록은 시작 시 `setMyCommands`로 처리됩니다.

    기본 네이티브 명령:

    - `commands.native: "auto"`는 Telegram에 대해 기본 명령을 활성화합니다

    사용자 지정 명령 메뉴 항목 추가:

```json5
{
  channels: {
    telegram: {
      customCommands: [
        { command: "backup", description: "Git 백업" },
        { command: "generate", description: "이미지 생성" },
      ],
    },
  },
}
```

    규칙:

    - 이름은 정규화됩니다(앞의 `/` 제거, 소문자화)
    - 유효 패턴: `a-z`, `0-9`, `_`, 길이 `1..32`
    - 사용자 지정 명령은 기본 명령을 재정의할 수 없습니다
    - 충돌/중복은 건너뛰고 로그에 기록됩니다

    참고:

    - 사용자 지정 명령은 메뉴 항목일 뿐이며 동작을 자동 구현하지 않습니다
    - plugin/Skills 명령은 Telegram 메뉴에 표시되지 않아도 직접 입력하면 여전히 동작할 수 있습니다

    네이티브 명령이 비활성화되면 기본 명령은 제거됩니다. 사용자 지정/plugin 명령은 구성된 경우 여전히 등록될 수 있습니다.

    일반적인 설정 실패:

    - `setMyCommands failed`와 함께 `BOT_COMMANDS_TOO_MUCH`가 표시되면, 잘라낸 후에도 Telegram 메뉴가 여전히 넘친다는 뜻입니다. plugin/skill/사용자 지정 명령을 줄이거나 `channels.telegram.commands.native`를 비활성화하세요.
    - `setMyCommands failed`와 함께 네트워크/fetch 오류가 표시되면 보통 `api.telegram.org`에 대한 아웃바운드 DNS/HTTPS가 차단된 것입니다.

    ### 장치 페어링 명령 (`device-pair` plugin)

    `device-pair` plugin이 설치된 경우:

    1. `/pair`가 설정 코드를 생성합니다
    2. iOS 앱에 코드를 붙여넣습니다
    3. `/pair pending`이 대기 중 요청을 나열합니다(역할/범위 포함)
    4. 요청을 승인합니다:
       - 명시적 승인에는 `/pair approve <requestId>`
       - 대기 중 요청이 하나뿐이면 `/pair approve`
       - 가장 최근 요청에는 `/pair approve latest`

    설정 코드는 짧은 수명의 bootstrap 토큰을 포함합니다. 내장 bootstrap handoff는 기본 노드 토큰을 `scopes: []`로 유지합니다. handoff된 operator 토큰은 `operator.approvals`, `operator.read`, `operator.talk.secrets`, `operator.write` 범위로 제한됩니다. Bootstrap 범위 검사는 역할 접두사를 사용하므로, 해당 operator allowlist는 operator 요청만 충족하며 비-operator 역할은 여전히 자체 역할 접두사 아래 범위가 필요합니다.

    장치가 변경된 인증 세부 정보(예: 역할/범위/공개 키)로 재시도하면 이전 대기 요청은 대체되고 새 요청은 다른 `requestId`를 사용합니다. 승인 전에 `/pair pending`을 다시 실행하세요.

    자세한 내용: [페어링](/channels/pairing#pair-via-telegram-recommended-for-ios).

  </Accordion>

  <Accordion title="인라인 버튼">
    인라인 키보드 범위를 구성합니다:

```json5
{
  channels: {
    telegram: {
      capabilities: {
        inlineButtons: "allowlist",
      },
    },
  },
}
```

    계정별 재정의:

```json5
{
  channels: {
    telegram: {
      accounts: {
        main: {
          capabilities: {
            inlineButtons: "allowlist",
          },
        },
      },
    },
  },
}
```

    범위:

    - `off`
    - `dm`
    - `group`
    - `all`
    - `allowlist` (기본값)

    레거시 `capabilities: ["inlineButtons"]`는 `inlineButtons: "all"`로 매핑됩니다.

    메시지 작업 예시:

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  message: "옵션을 선택하세요:",
  buttons: [
    [
      { text: "예", callback_data: "yes" },
      { text: "아니요", callback_data: "no" },
    ],
    [{ text: "취소", callback_data: "cancel" }],
  ],
}
```

    콜백 클릭은 텍스트로 agent에 전달됩니다:
    `callback_data: <value>`

  </Accordion>

  <Accordion title="agent 및 자동화를 위한 Telegram 메시지 작업">
    Telegram 도구 작업은 다음을 포함합니다.

    - `sendMessage` (`to`, `content`, 선택적 `mediaUrl`, `replyToMessageId`, `messageThreadId`)
    - `react` (`chatId`, `messageId`, `emoji`)
    - `deleteMessage` (`chatId`, `messageId`)
    - `editMessage` (`chatId`, `messageId`, `content`)
    - `createForumTopic` (`chatId`, `name`, 선택적 `iconColor`, `iconCustomEmojiId`)

    채널 메시지 작업은 사용하기 쉬운 별칭을 노출합니다(`send`, `react`, `delete`, `edit`, `sticker`, `sticker-search`, `topic-create`).

    게이팅 제어:

    - `channels.telegram.actions.sendMessage`
    - `channels.telegram.actions.deleteMessage`
    - `channels.telegram.actions.reactions`
    - `channels.telegram.actions.sticker` (기본값: 비활성화)

    참고: `edit`와 `topic-create`는 현재 기본적으로 활성화되어 있으며 별도의 `channels.telegram.actions.*` 토글이 없습니다.
    런타임 전송은 활성 config/secrets 스냅샷(시작/리로드 시점)을 사용하므로, 작업 경로는 전송마다 임시 SecretRef 재해석을 수행하지 않습니다.

    반응 제거 의미 체계: [/tools/reactions](/tools/reactions)

  </Accordion>

  <Accordion title="응답 스레딩 태그">
    Telegram은 생성된 출력에서 명시적 응답 스레딩 태그를 지원합니다.

    - `[[reply_to_current]]`는 트리거한 메시지에 응답합니다
    - `[[reply_to:<id>]]`는 특정 Telegram 메시지 ID에 응답합니다

    `channels.telegram.replyToMode`는 처리 방식을 제어합니다.

    - `off` (기본값)
    - `first`
    - `all`

    참고: `off`는 암시적 응답 스레딩을 비활성화합니다. 명시적 `[[reply_to_*]]` 태그는 여전히 적용됩니다.

  </Accordion>

  <Accordion title="포럼 토픽 및 스레드 동작">
    포럼 슈퍼그룹:

    - 토픽 세션 키는 `:topic:<threadId>`를 덧붙입니다
    - 응답과 입력 중 표시는 토픽 스레드를 대상으로 합니다
    - 토픽 config 경로:
      `channels.telegram.groups.<chatId>.topics.<threadId>`

    일반 토픽(`threadId=1`) 특수 사례:

    - 메시지 전송은 `message_thread_id`를 생략합니다(Telegram은 `sendMessage(...thread_id=1)`을 거부함)
    - 입력 중 동작에는 여전히 `message_thread_id`가 포함됩니다

    토픽 상속: 토픽 항목은 재정의되지 않는 한 그룹 설정을 상속합니다(`requireMention`, `allowFrom`, `skills`, `systemPrompt`, `enabled`, `groupPolicy`).
    `agentId`는 토픽 전용이며 그룹 기본값에서 상속되지 않습니다.

    **토픽별 agent 라우팅**: 각 토픽은 토픽 config에서 `agentId`를 설정하여 다른 agent로 라우팅할 수 있습니다. 이를 통해 각 토픽은 자체 격리된 workspace, 메모리, 세션을 가질 수 있습니다. 예시:

    ```json5
    {
      channels: {
        telegram: {
          groups: {
            "-1001234567890": {
              topics: {
                "1": { agentId: "main" },      // General topic → main agent
                "3": { agentId: "zu" },        // Dev topic → zu agent
                "5": { agentId: "coder" }      // Code review → coder agent
              }
            }
          }
        }
      }
    }
    ```

    각 토픽은 다음과 같은 자체 세션 키를 갖게 됩니다: `agent:zu:telegram:group:-1001234567890:topic:3`

    **영구 ACP 토픽 바인딩**: 포럼 토픽은 최상위 타입 지정 ACP 바인딩을 통해 ACP harness 세션을 고정할 수 있습니다.

    - `type: "acp"` 및 `match.channel: "telegram"`이 있는 `bindings[]`

    예시:

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
            channel: "telegram",
            accountId: "default",
            peer: { kind: "group", id: "-1001234567890:topic:42" },
          },
        },
      ],
      channels: {
        telegram: {
          groups: {
            "-1001234567890": {
              topics: {
                "42": {
                  requireMention: false,
                },
              },
            },
          },
        },
      },
    }
    ```

    현재 이는 그룹 및 슈퍼그룹의 포럼 토픽에 한정됩니다.

    **채팅에서 스레드 바인딩 ACP 생성**:

    - `/acp spawn <agent> --thread here|auto`는 현재 Telegram 토픽을 새 ACP 세션에 바인딩할 수 있습니다.
    - 후속 토픽 메시지는 바인딩된 ACP 세션으로 직접 라우팅됩니다(`/acp steer` 불필요).
    - OpenClaw는 성공적으로 바인딩한 후 생성 확인 메시지를 토픽 내에 고정합니다.
    - `channels.telegram.threadBindings.spawnAcpSessions=true`가 필요합니다.

    템플릿 컨텍스트에는 다음이 포함됩니다.

    - `MessageThreadId`
    - `IsForum`

    DM 스레드 동작:

    - `message_thread_id`가 있는 개인 채팅은 DM 라우팅을 유지하지만 스레드 인식 세션 키/응답 대상을 사용합니다.

  </Accordion>

  <Accordion title="오디오, 비디오 및 스티커">
    ### 오디오 메시지

    Telegram은 음성 노트와 오디오 파일을 구분합니다.

    - 기본값: 오디오 파일 동작
    - agent 응답에 `[[audio_as_voice]]` 태그를 넣으면 음성 노트 전송 강제

    메시지 작업 예시:

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/voice.ogg",
  asVoice: true,
}
```

    ### 비디오 메시지

    Telegram은 비디오 파일과 비디오 노트를 구분합니다.

    메시지 작업 예시:

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/video.mp4",
  asVideoNote: true,
}
```

    비디오 노트는 캡션을 지원하지 않으므로, 제공된 메시지 텍스트는 별도로 전송됩니다.

    ### 스티커

    인바운드 스티커 처리:

    - 정적 WEBP: 다운로드 및 처리됨(플레이스홀더 `<media:sticker>`)
    - 애니메이션 TGS: 건너뜀
    - 비디오 WEBM: 건너뜀

    스티커 컨텍스트 필드:

    - `Sticker.emoji`
    - `Sticker.setName`
    - `Sticker.fileId`
    - `Sticker.fileUniqueId`
    - `Sticker.cachedDescription`

    스티커 캐시 파일:

    - `~/.openclaw/telegram/sticker-cache.json`

    스티커는 반복적인 vision 호출을 줄이기 위해 가능할 때 한 번 설명하고 캐시됩니다.

    스티커 작업 활성화:

```json5
{
  channels: {
    telegram: {
      actions: {
        sticker: true,
      },
    },
  },
}
```

    스티커 전송 작업:

```json5
{
  action: "sticker",
  channel: "telegram",
  to: "123456789",
  fileId: "CAACAgIAAxkBAAI...",
}
```

    캐시된 스티커 검색:

```json5
{
  action: "sticker-search",
  channel: "telegram",
  query: "손 흔드는 고양이",
  limit: 5,
}
```

  </Accordion>

  <Accordion title="반응 알림">
    Telegram 반응은 `message_reaction` 업데이트로 도착합니다(메시지 payload와 별개).

    활성화되면 OpenClaw는 다음과 같은 시스템 이벤트를 큐에 넣습니다.

    - `Telegram reaction added: 👍 by Alice (@alice) on msg 42`

    config:

    - `channels.telegram.reactionNotifications`: `off | own | all` (기본값: `own`)
    - `channels.telegram.reactionLevel`: `off | ack | minimal | extensive` (기본값: `minimal`)

    참고:

    - `own`은 봇이 보낸 메시지에 대한 사용자 반응만 의미합니다(전송된 메시지 캐시를 통한 최선 시도).
    - 반응 이벤트는 여전히 Telegram 액세스 제어(`dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`)를 따르며, 권한 없는 발신자는 버려집니다.
    - Telegram은 반응 업데이트에 스레드 ID를 제공하지 않습니다.
      - 비포럼 그룹은 그룹 채팅 세션으로 라우팅
      - 포럼 그룹은 정확한 원래 토픽이 아니라 그룹 일반 토픽 세션(`:topic:1`)으로 라우팅

    폴링/webhook용 `allowed_updates`에는 `message_reaction`이 자동으로 포함됩니다.

  </Accordion>

  <Accordion title="승인 반응">
    `ackReaction`은 OpenClaw가 인바운드 메시지를 처리하는 동안 확인 이모지를 보냅니다.

    해석 순서:

    - `channels.telegram.accounts.<accountId>.ackReaction`
    - `channels.telegram.ackReaction`
    - `messages.ackReaction`
    - agent identity 이모지 대체(`agents.list[].identity.emoji`, 없으면 "👀")

    참고:

    - Telegram은 유니코드 이모지(예: "👀")를 기대합니다.
    - 채널 또는 계정에서 반응을 비활성화하려면 `""`를 사용하세요.

  </Accordion>

  <Accordion title="Telegram 이벤트 및 명령에서의 config 쓰기">
    채널 config 쓰기는 기본적으로 활성화되어 있습니다(`configWrites !== false`).

    Telegram 트리거 쓰기에는 다음이 포함됩니다.

    - `channels.telegram.groups`를 업데이트하기 위한 그룹 마이그레이션 이벤트(`migrate_to_chat_id`)
    - `/config set` 및 `/config unset`(명령 활성화 필요)

    비활성화:

```json5
{
  channels: {
    telegram: {
      configWrites: false,
    },
  },
}
```

  </Accordion>

  <Accordion title="롱 폴링 vs webhook">
    기본값: 롱 폴링.

    webhook 모드:

    - `channels.telegram.webhookUrl` 설정
    - `channels.telegram.webhookSecret` 설정(webhook URL이 설정된 경우 필수)
    - 선택적 `channels.telegram.webhookPath` (기본값 `/telegram-webhook`)
    - 선택적 `channels.telegram.webhookHost` (기본값 `127.0.0.1`)
    - 선택적 `channels.telegram.webhookPort` (기본값 `8787`)

    webhook 모드의 기본 로컬 리스너는 `127.0.0.1:8787`에 바인딩됩니다.

    공개 엔드포인트가 다르면 앞에 reverse proxy를 두고 `webhookUrl`을 공개 URL로 지정하세요.
    외부 인그레스가 의도적으로 필요한 경우 `webhookHost`(예: `0.0.0.0`)를 설정하세요.

  </Accordion>

  <Accordion title="제한, 재시도 및 CLI 대상">
    - `channels.telegram.textChunkLimit` 기본값은 4000입니다.
    - `channels.telegram.chunkMode="newline"`은 길이 기준 분할 전에 문단 경계(빈 줄)를 우선합니다.
    - `channels.telegram.mediaMaxMb`(기본값 100)는 인바운드 및 아웃바운드 Telegram 미디어 크기를 제한합니다.
    - `channels.telegram.timeoutSeconds`는 Telegram API 클라이언트 타임아웃을 재정의합니다(설정하지 않으면 grammY 기본값 적용).
    - 그룹 컨텍스트 기록은 `channels.telegram.historyLimit` 또는 `messages.groupChat.historyLimit`(기본값 50)을 사용하며, `0`이면 비활성화됩니다.
    - 응답/인용/전달 보조 컨텍스트는 현재 수신된 그대로 전달됩니다.
    - Telegram allowlist는 주로 누가 agent를 트리거할 수 있는지 제어하며, 완전한 보조 컨텍스트 redaction 경계는 아닙니다.
    - DM 기록 제어:
      - `channels.telegram.dmHistoryLimit`
      - `channels.telegram.dms["<user_id>"].historyLimit`
    - `channels.telegram.retry` config는 복구 가능한 아웃바운드 API 오류에 대해 Telegram 전송 헬퍼(CLI/tools/actions)에 적용됩니다.

    CLI 전송 대상은 숫자형 chat ID 또는 username일 수 있습니다:

```bash
openclaw message send --channel telegram --target 123456789 --message "hi"
openclaw message send --channel telegram --target @name --message "hi"
```

    Telegram 투표는 `openclaw message poll`을 사용하며 포럼 토픽을 지원합니다:

```bash
openclaw message poll --channel telegram --target 123456789 \
  --poll-question "Ship it?" --poll-option "Yes" --poll-option "No"
openclaw message poll --channel telegram --target -1001234567890:topic:42 \
  --poll-question "Pick a time" --poll-option "10am" --poll-option "2pm" \
  --poll-duration-seconds 300 --poll-public
```

    Telegram 전용 투표 플래그:

    - `--poll-duration-seconds` (5-600)
    - `--poll-anonymous`
    - `--poll-public`
    - 포럼 토픽용 `--thread-id`(또는 `:topic:` 대상 사용)

    Telegram 전송은 다음도 지원합니다:

    - `channels.telegram.capabilities.inlineButtons`가 허용할 때 인라인 키보드용 `--buttons`
    - 아웃바운드 이미지와 GIF를 압축 사진 또는 애니메이션 미디어 업로드 대신 문서로 보내기 위한 `--force-document`

    작업 게이팅:

    - `channels.telegram.actions.sendMessage=false`는 투표를 포함한 아웃바운드 Telegram 메시지를 비활성화합니다
    - `channels.telegram.actions.poll=false`는 일반 전송은 유지한 채 Telegram 투표 생성을 비활성화합니다

  </Accordion>

  <Accordion title="Telegram의 exec 승인">
    Telegram은 승인자 DM에서 exec 승인을 지원하며, 선택적으로 원래 채팅 또는 토픽에 승인 프롬프트를 게시할 수 있습니다.

    config 경로:

    - `channels.telegram.execApprovals.enabled`
    - `channels.telegram.execApprovals.approvers` (선택 사항. 가능하면 `allowFrom` 및 direct `defaultTo`에서 추론된 숫자형 소유자 ID로 대체)
    - `channels.telegram.execApprovals.target` (`dm` | `channel` | `both`, 기본값: `dm`)
    - `agentFilter`, `sessionFilter`

    승인자는 숫자형 Telegram 사용자 ID여야 합니다. `enabled`가 설정되지 않았거나 `"auto"`이고, `execApprovals.approvers` 또는 계정의 숫자형 소유자 config(`allowFrom` 및 direct-message `defaultTo`)에서 최소 하나의 승인자를 해석할 수 있으면 Telegram은 기본 exec 승인을 자동 활성화합니다. Telegram을 기본 승인 클라이언트로 명시적으로 비활성화하려면 `enabled: false`를 설정하세요. 그렇지 않으면 승인 요청은 다른 구성된 승인 경로 또는 exec 승인 대체 정책으로 폴백됩니다.

    Telegram은 다른 채팅 채널이 사용하는 공유 승인 버튼도 렌더링합니다. 기본 Telegram 어댑터는 주로 승인자 DM 라우팅, 채널/토픽 팬아웃, 전송 전 입력 중 힌트를 추가합니다.
    이러한 버튼이 있으면 그것이 기본 승인 UX이며, OpenClaw는 도구 결과가 채팅 승인을 사용할 수 없거나 수동 승인이 유일한 경로라고 말할 때만 수동 `/approve` 명령을 포함해야 합니다.

    전송 규칙:

    - `target: "dm"`은 해석된 승인자 DM으로만 승인 프롬프트를 보냅니다
    - `target: "channel"`은 원래 Telegram 채팅/토픽으로 프롬프트를 다시 보냅니다
    - `target: "both"`는 승인자 DM과 원래 채팅/토픽 모두에 보냅니다

    해석된 승인자만 승인 또는 거부할 수 있습니다. 비승인자는 `/approve`를 사용할 수 없고 Telegram 승인 버튼도 사용할 수 없습니다.

    승인 해석 동작:

    - `plugin:` 접두사가 있는 ID는 항상 plugin 승인으로 해석됩니다.
    - 다른 승인 ID는 먼저 `exec.approval.resolve`를 시도합니다.
    - Telegram이 plugin 승인에도 허용되어 있고 gateway가 exec 승인이 알 수 없거나 만료되었다고 말하면, Telegram은 한 번 `plugin.approval.resolve`를 통해 재시도합니다.
    - 실제 exec 승인 거부/오류는 자동으로 plugin 승인 해석으로 넘어가지 않습니다.

    채널 전송은 채팅에 명령 텍스트를 표시하므로, `channel` 또는 `both`는 신뢰할 수 있는 그룹/토픽에서만 활성화하세요. 포럼 토픽에 프롬프트가 도착하면 OpenClaw는 승인 프롬프트와 승인 후 후속 메시지 모두에 대해 해당 토픽을 유지합니다. Exec 승인의 기본 만료 시간은 30분입니다.

    인라인 승인 버튼은 또한 `channels.telegram.capabilities.inlineButtons`가 대상 표면(`dm`, `group`, 또는 `all`)을 허용하는지에 따라 달라집니다.

    관련 문서: [Exec 승인](/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## 오류 응답 제어

agent가 전송 또는 공급자 오류를 만나면 Telegram은 오류 텍스트로 응답하거나 이를 숨길 수 있습니다. 이 동작은 두 개의 config 키로 제어됩니다:

| 키 | 값 | 기본값 | 설명 |
| ----------------------------------- | ----------------- | ------- | ----------------------------------------------------------------------------------------------- |
| `channels.telegram.errorPolicy`     | `reply`, `silent` | `reply` | `reply`는 채팅에 친화적인 오류 메시지를 보냅니다. `silent`는 오류 응답을 완전히 숨깁니다. |
| `channels.telegram.errorCooldownMs` | number (ms)       | `60000` | 동일한 채팅에 대한 오류 응답 사이의 최소 시간입니다. 장애 중 오류 스팸을 방지합니다. |

계정별, 그룹별, 토픽별 재정의를 지원합니다(다른 Telegram config 키와 동일한 상속 방식).

```json5
{
  channels: {
    telegram: {
      errorPolicy: "reply",
      errorCooldownMs: 120000,
      groups: {
        "-1001234567890": {
          errorPolicy: "silent", // 이 그룹에서는 오류 숨김
        },
      },
    },
  },
}
```

## 문제 해결

<AccordionGroup>
  <Accordion title="멘션 없는 그룹 메시지에 봇이 응답하지 않음">

    - `requireMention=false`인 경우 Telegram 개인정보 보호 모드가 전체 가시성을 허용해야 합니다.
      - BotFather: `/setprivacy` -> 비활성화
      - 그런 다음 그룹에서 봇을 제거했다가 다시 추가
    - `openclaw channels status`는 config가 멘션 없는 그룹 메시지를 기대할 때 경고를 표시합니다.
    - `openclaw channels status --probe`는 명시적 숫자형 그룹 ID를 검사할 수 있습니다. 와일드카드 `"*"`는 멤버십 probe를 할 수 없습니다.
    - 빠른 세션 테스트: `/activation always`.

  </Accordion>

  <Accordion title="봇이 그룹 메시지를 전혀 보지 못함">

    - `channels.telegram.groups`가 존재하면, 해당 그룹이 목록에 있거나 `"*"`가 포함되어 있어야 합니다
    - 그룹 내 봇 멤버십 확인
    - 건너뛴 이유는 `openclaw logs --follow`에서 로그 검토

  </Accordion>

  <Accordion title="명령이 일부만 동작하거나 전혀 동작하지 않음">

    - 발신자 ID를 인증하세요(페어링 및/또는 숫자형 `allowFrom`)
    - 그룹 정책이 `open`이더라도 명령 인증은 여전히 적용됩니다
    - `setMyCommands failed`와 함께 `BOT_COMMANDS_TOO_MUCH`가 표시되면 기본 메뉴 항목이 너무 많다는 뜻입니다. plugin/skill/사용자 지정 명령을 줄이거나 기본 메뉴를 비활성화하세요
    - `setMyCommands failed`와 함께 네트워크/fetch 오류가 표시되면 보통 `api.telegram.org`에 대한 DNS/HTTPS 도달성 문제를 의미합니다

  </Accordion>

  <Accordion title="폴링 또는 네트워크 불안정">

    - Node 22+와 사용자 지정 fetch/proxy 조합은 AbortSignal 타입이 맞지 않으면 즉시 abort 동작을 유발할 수 있습니다.
    - 일부 호스트는 `api.telegram.org`를 먼저 IPv6로 해석하므로, IPv6 아웃바운드가 깨져 있으면 간헐적인 Telegram API 실패가 발생할 수 있습니다.
    - 로그에 `TypeError: fetch failed` 또는 `Network request for 'getUpdates' failed!`가 포함되면, OpenClaw는 이제 이를 복구 가능한 네트워크 오류로 재시도합니다.
    - 직접 아웃바운드/TLS가 불안정한 VPS 호스트에서는 Telegram API 호출을 `channels.telegram.proxy`를 통해 라우팅하세요:

```yaml
channels:
  telegram:
    proxy: socks5://<user>:<password>@proxy-host:1080
```

    - Node 22+는 기본적으로 `autoSelectFamily=true`(WSL2 제외) 및 `dnsResultOrder=ipv4first`를 사용합니다.
    - 호스트가 WSL2이거나 IPv4 전용 동작이 명시적으로 더 잘 맞는 경우, family selection을 강제하세요:

```yaml
channels:
  telegram:
    network:
      autoSelectFamily: false
```

    - RFC 2544 벤치마크 범위 응답(`198.18.0.0/15`)은 기본적으로 Telegram 미디어 다운로드에 이미 허용되어 있습니다. 신뢰할 수 있는 가짜 IP 또는 transparent proxy가 미디어 다운로드 중 `api.telegram.org`를 다른 private/internal/special-use 주소로 재작성하는 경우, Telegram 전용 우회를 선택적으로 활성화할 수 있습니다:

```yaml
channels:
  telegram:
    network:
      dangerouslyAllowPrivateNetwork: true
```

    - 동일한 선택 기능은 계정별로도 사용할 수 있습니다:
      `channels.telegram.accounts.<accountId>.network.dangerouslyAllowPrivateNetwork`.
    - proxy가 Telegram 미디어 호스트를 `198.18.x.x`로 해석하는 경우, 먼저 위험한 플래그를 끈 상태로 두세요. Telegram 미디어는 기본적으로 RFC 2544 벤치마크 범위를 이미 허용합니다.

    <Warning>
      `channels.telegram.network.dangerouslyAllowPrivateNetwork`는 Telegram
      미디어 SSRF 보호를 약화시킵니다. Clash, Mihomo, Surge 가짜 IP 라우팅처럼 RFC 2544 벤치마크 범위를 벗어난 private 또는 special-use 응답을 합성하는 신뢰된 운영자 제어 proxy 환경에서만 사용하세요. 일반적인 공용 인터넷 Telegram 액세스에서는 비활성화된 상태로 두세요.
    </Warning>

    - 환경 변수 재정의(임시):
      - `OPENCLAW_TELEGRAM_DISABLE_AUTO_SELECT_FAMILY=1`
      - `OPENCLAW_TELEGRAM_ENABLE_AUTO_SELECT_FAMILY=1`
      - `OPENCLAW_TELEGRAM_DNS_RESULT_ORDER=ipv4first`
    - DNS 응답 검증:

```bash
dig +short api.telegram.org A
dig +short api.telegram.org AAAA
```

  </Accordion>
</AccordionGroup>

추가 도움말: [채널 문제 해결](/channels/troubleshooting).

## Telegram config 참조 포인터

기본 참조:

- `channels.telegram.enabled`: 채널 시작 활성화/비활성화.
- `channels.telegram.botToken`: 봇 토큰(BotFather).
- `channels.telegram.tokenFile`: 일반 파일 경로에서 토큰 읽기. 심볼릭 링크는 거부됩니다.
- `channels.telegram.dmPolicy`: `pairing | allowlist | open | disabled` (기본값: pairing).
- `channels.telegram.allowFrom`: DM allowlist(숫자형 Telegram 사용자 ID). `allowlist`는 발신자 ID가 하나 이상 필요합니다. `open`은 `"*"`가 필요합니다. `openclaw doctor --fix`는 레거시 `@username` 항목을 ID로 해석할 수 있고, allowlist 마이그레이션 흐름에서 페어링 저장소 파일의 allowlist 항목을 복구할 수 있습니다.
- `channels.telegram.actions.poll`: Telegram 투표 생성 활성화 또는 비활성화(기본값: 활성화. 여전히 `sendMessage` 필요).
- `channels.telegram.defaultTo`: 명시적 `--reply-to`가 없을 때 CLI `--deliver`이 사용하는 기본 Telegram 대상.
- `channels.telegram.groupPolicy`: `open | allowlist | disabled` (기본값: allowlist).
- `channels.telegram.groupAllowFrom`: 그룹 발신자 allowlist(숫자형 Telegram 사용자 ID). `openclaw doctor --fix`는 레거시 `@username` 항목을 ID로 해석할 수 있습니다. 숫자가 아닌 항목은 인증 시 무시됩니다. 그룹 인증은 DM 페어링 저장소 대체를 사용하지 않습니다(`2026.2.25+`).
- 다중 계정 우선순위:
  - 두 개 이상의 계정 ID가 구성된 경우, 기본 라우팅을 명시적으로 만들기 위해 `channels.telegram.defaultAccount`를 설정하거나 `channels.telegram.accounts.default`를 포함하세요.
  - 둘 다 설정하지 않으면 OpenClaw는 첫 번째 정규화된 계정 ID로 대체하며 `openclaw doctor`가 경고합니다.
  - `channels.telegram.accounts.default.allowFrom` 및 `channels.telegram.accounts.default.groupAllowFrom`은 `default` 계정에만 적용됩니다.
  - 이름이 있는 계정은 계정 수준 값이 설정되지 않은 경우 `channels.telegram.allowFrom` 및 `channels.telegram.groupAllowFrom`을 상속합니다.
  - 이름이 있는 계정은 `channels.telegram.accounts.default.allowFrom` / `groupAllowFrom`을 상속하지 않습니다.
- `channels.telegram.groups`: 그룹별 기본값 + allowlist(전역 기본값에는 `"*"` 사용).
  - `channels.telegram.groups.<id>.groupPolicy`: 그룹별 `groupPolicy` 재정의 (`open | allowlist | disabled`).
  - `channels.telegram.groups.<id>.requireMention`: 기본 멘션 게이팅.
  - `channels.telegram.groups.<id>.skills`: Skills 필터(생략 = 모든 Skills, 빈값 = 없음).
  - `channels.telegram.groups.<id>.allowFrom`: 그룹별 발신자 allowlist 재정의.
  - `channels.telegram.groups.<id>.systemPrompt`: 그룹용 추가 시스템 프롬프트.
  - `channels.telegram.groups.<id>.enabled`: `false`이면 그룹 비활성화.
  - `channels.telegram.groups.<id>.topics.<threadId>.*`: 토픽별 재정의(그룹 필드 + 토픽 전용 `agentId`).
  - `channels.telegram.groups.<id>.topics.<threadId>.agentId`: 이 토픽을 특정 agent로 라우팅(그룹 수준 및 바인딩 라우팅 재정의).
- `channels.telegram.groups.<id>.topics.<threadId>.groupPolicy`: `groupPolicy`의 토픽별 재정의 (`open | allowlist | disabled`).
- `channels.telegram.groups.<id>.topics.<threadId>.requireMention`: 토픽별 멘션 게이팅 재정의.
- `match.peer.id`에 정식 토픽 ID `chatId:topic:topicId`가 있는 최상위 `bindings[]` 및 `type: "acp"`: 영구 ACP 토픽 바인딩 필드([ACP Agents](/tools/acp-agents#channel-specific-settings) 참조).
- `channels.telegram.direct.<id>.topics.<threadId>.agentId`: DM 토픽을 특정 agent로 라우팅(포럼 토픽과 동일한 동작).
- `channels.telegram.execApprovals.enabled`: 이 계정에 대해 Telegram을 채팅 기반 exec 승인 클라이언트로 활성화.
- `channels.telegram.execApprovals.approvers`: exec 요청을 승인 또는 거부할 수 있는 Telegram 사용자 ID. `channels.telegram.allowFrom` 또는 direct `channels.telegram.defaultTo`가 이미 소유자를 식별하는 경우 선택 사항.
- `channels.telegram.execApprovals.target`: `dm | channel | both` (기본값: `dm`). `channel` 및 `both`는 존재하는 경우 원래 Telegram 토픽을 유지합니다.
- `channels.telegram.execApprovals.agentFilter`: 전달된 승인 프롬프트에 대한 선택적 agent ID 필터.
- `channels.telegram.execApprovals.sessionFilter`: 전달된 승인 프롬프트에 대한 선택적 세션 키 필터(부분 문자열 또는 regex).
- `channels.telegram.accounts.<account>.execApprovals`: Telegram exec 승인 라우팅 및 승인자 인증에 대한 계정별 재정의.
- `channels.telegram.capabilities.inlineButtons`: `off | dm | group | all | allowlist` (기본값: allowlist).
- `channels.telegram.accounts.<account>.capabilities.inlineButtons`: 계정별 재정의.
- `channels.telegram.commands.nativeSkills`: Telegram 기본 Skills 명령 활성화/비활성화.
- `channels.telegram.replyToMode`: `off | first | all` (기본값: `off`).
- `channels.telegram.textChunkLimit`: 아웃바운드 청크 크기(문자 수).
- `channels.telegram.chunkMode`: `length`(기본값) 또는 `newline`; 길이 청크 전 빈 줄(문단 경계)에서 분할.
- `channels.telegram.linkPreview`: 아웃바운드 메시지의 링크 미리보기 토글(기본값: true).
- `channels.telegram.streaming`: `off | partial | block | progress` (실시간 스트림 미리보기, 기본값: `partial`; `progress`는 `partial`로 매핑; `block`은 레거시 미리보기 모드 호환성). Telegram 미리보기 스트리밍은 그 자리에서 편집되는 단일 미리보기 메시지를 사용합니다.
- `channels.telegram.mediaMaxMb`: 인바운드/아웃바운드 Telegram 미디어 상한(MB, 기본값: 100).
- `channels.telegram.retry`: 복구 가능한 아웃바운드 API 오류에 대한 Telegram 전송 헬퍼(CLI/tools/actions) 재시도 정책(attempts, minDelayMs, maxDelayMs, jitter).
- `channels.telegram.network.autoSelectFamily`: Node autoSelectFamily 재정의(true=활성화, false=비활성화). 기본값은 Node 22+에서 활성화이며, WSL2는 기본적으로 비활성화됩니다.
- `channels.telegram.network.dnsResultOrder`: DNS 결과 순서 재정의(`ipv4first` 또는 `verbatim`). 기본값은 Node 22+에서 `ipv4first`입니다.
- `channels.telegram.network.dangerouslyAllowPrivateNetwork`: Telegram 미디어 다운로드가 기본 RFC 2544 벤치마크 범위 허용을 벗어난 private/internal/special-use 주소로 `api.telegram.org`를 해석하는 신뢰된 가짜 IP 또는 transparent-proxy 환경용 위험한 opt-in.
- `channels.telegram.proxy`: Bot API 호출용 proxy URL(SOCKS/HTTP).
- `channels.telegram.webhookUrl`: webhook 모드 활성화(`channels.telegram.webhookSecret` 필요).
- `channels.telegram.webhookSecret`: webhook secret(`webhookUrl` 설정 시 필수).
- `channels.telegram.webhookPath`: 로컬 webhook 경로(기본값 `/telegram-webhook`).
- `channels.telegram.webhookHost`: 로컬 webhook 바인딩 호스트(기본값 `127.0.0.1`).
- `channels.telegram.webhookPort`: 로컬 webhook 바인딩 포트(기본값 `8787`).
- `channels.telegram.actions.reactions`: Telegram 도구 반응 게이트.
- `channels.telegram.actions.sendMessage`: Telegram 도구 메시지 전송 게이트.
- `channels.telegram.actions.deleteMessage`: Telegram 도구 메시지 삭제 게이트.
- `channels.telegram.actions.sticker`: Telegram 스티커 작업 게이트 — 전송 및 검색(기본값: false).
- `channels.telegram.reactionNotifications`: `off | own | all` — 어떤 반응이 시스템 이벤트를 트리거할지 제어(설정되지 않은 경우 기본값: `own`).
- `channels.telegram.reactionLevel`: `off | ack | minimal | extensive` — agent의 반응 기능을 제어(설정되지 않은 경우 기본값: `minimal`).
- `channels.telegram.errorPolicy`: `reply | silent` — 오류 응답 동작 제어(기본값: `reply`). 계정별/그룹별/토픽별 재정의 지원.
- `channels.telegram.errorCooldownMs`: 동일한 채팅에 대한 오류 응답 사이의 최소 ms(기본값: `60000`). 장애 중 오류 스팸 방지.

- [구성 참조 - Telegram](/gateway/configuration-reference#telegram)

Telegram 전용 주요 필드:

- 시작/인증: `enabled`, `botToken`, `tokenFile`, `accounts.*` (`tokenFile`은 일반 파일을 가리켜야 하며 심볼릭 링크는 거부됨)
- 액세스 제어: `dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`, `groups.*.topics.*`, 최상위 `bindings[]` (`type: "acp"`)
- exec 승인: `execApprovals`, `accounts.*.execApprovals`
- 명령/메뉴: `commands.native`, `commands.nativeSkills`, `customCommands`
- 스레딩/응답: `replyToMode`
- 스트리밍: `streaming`(미리보기), `blockStreaming`
- 서식/전송: `textChunkLimit`, `chunkMode`, `linkPreview`, `responsePrefix`
- 미디어/네트워크: `mediaMaxMb`, `timeoutSeconds`, `retry`, `network.autoSelectFamily`, `network.dangerouslyAllowPrivateNetwork`, `proxy`
- webhook: `webhookUrl`, `webhookSecret`, `webhookPath`, `webhookHost`
- 작업/기능: `capabilities.inlineButtons`, `actions.sendMessage|editMessage|deleteMessage|reactions|sticker`
- 반응: `reactionNotifications`, `reactionLevel`
- 오류: `errorPolicy`, `errorCooldownMs`
- 쓰기/기록: `configWrites`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`

## 관련 문서

- [페어링](/channels/pairing)
- [그룹](/channels/groups)
- [보안](/gateway/security)
- [채널 라우팅](/channels/channel-routing)
- [멀티 에이전트 라우팅](/concepts/multi-agent)
- [문제 해결](/channels/troubleshooting)
