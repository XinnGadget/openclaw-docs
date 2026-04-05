---
read_when:
    - WhatsApp/웹 채널 동작 또는 받은편지함 라우팅 작업
summary: WhatsApp 채널 지원, 접근 제어, 전달 동작 및 운영
title: WhatsApp
x-i18n:
    generated_at: "2026-04-05T12:37:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: c16a468b3f47fdf7e4fc3fd745b5c49c7ccebb7af0e8c87c632b78b04c583e49
    source_path: channels/whatsapp.md
    workflow: 15
---

# WhatsApp (웹 채널)

상태: WhatsApp Web(Baileys)을 통한 프로덕션 준비 완료. Gateway가 연결된 세션을 소유합니다.

## 설치(필요 시)

- `openclaw onboard`와 `openclaw channels add --channel whatsapp`는
  WhatsApp plugin을 처음 선택할 때 설치를 안내합니다.
- `openclaw channels login --channel whatsapp`도
  plugin이 아직 없으면 설치 흐름을 제공합니다.
- 개발 채널 + git 체크아웃: 기본값은 로컬 plugin 경로입니다.
- Stable/Beta: 기본값은 npm 패키지 `@openclaw/whatsapp`입니다.

수동 설치도 계속 사용할 수 있습니다.

```bash
openclaw plugins install @openclaw/whatsapp
```

<CardGroup cols={3}>
  <Card title="페어링" icon="link" href="/channels/pairing">
    알 수 없는 발신자에 대한 기본 DM 정책은 페어링입니다.
  </Card>
  <Card title="채널 문제 해결" icon="wrench" href="/channels/troubleshooting">
    채널 전반의 진단 및 복구 플레이북.
  </Card>
  <Card title="Gateway 구성" icon="settings" href="/gateway/configuration">
    전체 채널 config 패턴 및 예시.
  </Card>
</CardGroup>

## 빠른 설정

<Steps>
  <Step title="WhatsApp 접근 정책 구성">

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      allowFrom: ["+15551234567"],
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
}
```

  </Step>

  <Step title="WhatsApp 연결(QR)">

```bash
openclaw channels login --channel whatsapp
```

    특정 계정의 경우:

```bash
openclaw channels login --channel whatsapp --account work
```

  </Step>

  <Step title="gateway 시작">

```bash
openclaw gateway
```

  </Step>

  <Step title="첫 번째 페어링 요청 승인(페어링 모드 사용 시)">

```bash
openclaw pairing list whatsapp
openclaw pairing approve whatsapp <CODE>
```

    페어링 요청은 1시간 후 만료됩니다. 대기 중 요청은 채널당 최대 3개까지 허용됩니다.

  </Step>
</Steps>

<Note>
가능하면 OpenClaw는 WhatsApp를 별도 번호로 운영하는 것을 권장합니다. (채널 메타데이터와 설정 흐름은 그 구성을 기준으로 최적화되어 있지만, 개인 번호 설정도 지원합니다.)
</Note>

## 배포 패턴

<AccordionGroup>
  <Accordion title="전용 번호(권장)">
    가장 깔끔한 운영 모드입니다.

    - OpenClaw용 별도 WhatsApp 신원
    - 더 명확한 DM 허용 목록 및 라우팅 경계
    - 자기 자신과의 채팅 혼동 가능성 감소

    최소 정책 패턴:

    ```json5
    {
      channels: {
        whatsapp: {
          dmPolicy: "allowlist",
          allowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="개인 번호 대체 사용">
    온보딩은 개인 번호 모드를 지원하며 self-chat 친화적인 기본 구성을 기록합니다.

    - `dmPolicy: "allowlist"`
    - `allowFrom`에 개인 번호 포함
    - `selfChatMode: true`

    런타임에서는 self-chat 보호가 연결된 자기 번호와 `allowFrom`을 기준으로 동작합니다.

  </Accordion>

  <Accordion title="WhatsApp Web 전용 채널 범위">
    현재 OpenClaw 채널 아키텍처에서 메시징 플랫폼 채널은 WhatsApp Web 기반(`Baileys`)입니다.

    내장 채팅 채널 레지스트리에는 별도의 Twilio WhatsApp 메시징 채널이 없습니다.

  </Accordion>
</AccordionGroup>

## 런타임 모델

- Gateway가 WhatsApp 소켓과 재연결 루프를 소유합니다.
- 아웃바운드 전송은 대상 계정에 대해 활성 WhatsApp 리스너가 있어야 합니다.
- 상태 및 브로드캐스트 채팅은 무시됩니다(`@status`, `@broadcast`).
- 다이렉트 채팅은 DM 세션 규칙을 사용합니다(`session.dmScope`; 기본값 `main`은 DM을 agent 메인 세션으로 병합함).
- 그룹 세션은 격리됩니다(`agent:<agentId>:whatsapp:group:<jid>`).

## 접근 제어 및 활성화

<Tabs>
  <Tab title="DM 정책">
    `channels.whatsapp.dmPolicy`는 다이렉트 채팅 접근을 제어합니다.

    - `pairing`(기본값)
    - `allowlist`
    - `open`(`allowFrom`에 `"*"` 포함 필요)
    - `disabled`

    `allowFrom`은 E.164 형식 번호를 받으며(내부적으로 정규화됨).

    멀티 계정 재정의: 해당 계정에서는 `channels.whatsapp.accounts.<id>.dmPolicy`(및 `allowFrom`)가 채널 수준 기본값보다 우선합니다.

    런타임 동작 세부 사항:

    - 페어링은 채널 allow-store에 영속 저장되며 구성된 `allowFrom`과 병합됩니다
    - 허용 목록이 구성되지 않았으면 연결된 자기 번호가 기본적으로 허용됩니다
    - 아웃바운드 `fromMe` DM은 자동 페어링되지 않습니다

  </Tab>

  <Tab title="그룹 정책 + 허용 목록">
    그룹 접근은 두 계층으로 구성됩니다.

    1. **그룹 멤버십 허용 목록**(`channels.whatsapp.groups`)
       - `groups`가 생략되면 모든 그룹이 대상이 됩니다
       - `groups`가 있으면 그룹 허용 목록으로 동작합니다(`"*"` 허용 가능)

    2. **그룹 발신자 정책**(`channels.whatsapp.groupPolicy` + `groupAllowFrom`)
       - `open`: 발신자 허용 목록 우회
       - `allowlist`: 발신자가 `groupAllowFrom`(또는 `*`)과 일치해야 함
       - `disabled`: 모든 그룹 수신 차단

    발신자 허용 목록 대체 동작:

    - `groupAllowFrom`이 설정되지 않으면, 런타임은 가능할 때 `allowFrom`으로 대체합니다
    - 발신자 허용 목록은 멘션/답글 활성화보다 먼저 평가됩니다

    참고: `channels.whatsapp` 블록이 아예 없으면, `channels.defaults.groupPolicy`가 설정되어 있어도 런타임 그룹 정책 대체값은 `allowlist`입니다(경고 로그와 함께).

  </Tab>

  <Tab title="멘션 + /activation">
    그룹 응답은 기본적으로 멘션이 필요합니다.

    멘션 감지에는 다음이 포함됩니다.

    - 봇 신원에 대한 명시적 WhatsApp 멘션
    - 구성된 멘션 정규식 패턴(`agents.list[].groupChat.mentionPatterns`, 대체값 `messages.groupChat.mentionPatterns`)
    - 암묵적인 reply-to-bot 감지(답글 발신자가 봇 신원과 일치)

    보안 참고:

    - 인용/답글은 멘션 게이팅만 충족하며, 발신자 권한을 부여하지는 않습니다
    - `groupPolicy: "allowlist"`에서는 허용 목록에 없는 발신자가 허용 목록 사용자의 메시지에 답글을 달더라도 여전히 차단됩니다

    세션 수준 활성화 명령:

    - `/activation mention`
    - `/activation always`

    `activation`은 세션 상태를 업데이트하며(전역 config 아님), 소유자 게이트가 적용됩니다.

  </Tab>
</Tabs>

## 개인 번호 및 self-chat 동작

연결된 자기 번호가 `allowFrom`에도 포함되어 있으면 WhatsApp self-chat 보호가 활성화됩니다.

- self-chat 턴에서는 읽음 확인 생략
- 그렇지 않으면 자신에게 핑을 보낼 수 있는 mention-JID 자동 트리거 동작 무시
- `messages.responsePrefix`가 설정되지 않은 경우, self-chat 응답의 기본값은 `[{identity.name}]` 또는 `[openclaw]`

## 메시지 정규화 및 컨텍스트

<AccordionGroup>
  <Accordion title="수신 엔벌로프 + 답글 컨텍스트">
    들어오는 WhatsApp 메시지는 공용 수신 엔벌로프로 감싸집니다.

    인용된 답글이 있으면 다음 형식으로 컨텍스트가 추가됩니다.

    ```text
    [Replying to <sender> id:<stanzaId>]
    <quoted body or media placeholder>
    [/Replying]
    ```

    답글 메타데이터 필드도 가능하면 채워집니다(`ReplyToId`, `ReplyToBody`, `ReplyToSender`, sender JID/E.164).

  </Accordion>

  <Accordion title="미디어 플레이스홀더 및 위치/연락처 추출">
    미디어만 있는 수신 메시지는 다음과 같은 플레이스홀더로 정규화됩니다.

    - `<media:image>`
    - `<media:video>`
    - `<media:audio>`
    - `<media:document>`
    - `<media:sticker>`

    위치 및 연락처 페이로드는 라우팅 전에 텍스트 컨텍스트로 정규화됩니다.

  </Accordion>

  <Accordion title="보류 중인 그룹 기록 주입">
    그룹에서는 아직 처리되지 않은 메시지를 버퍼링했다가 봇이 최종적으로 트리거될 때 컨텍스트로 주입할 수 있습니다.

    - 기본 한도: `50`
    - config: `channels.whatsapp.historyLimit`
    - 대체값: `messages.groupChat.historyLimit`
    - `0`은 비활성화

    주입 마커:

    - `[Chat messages since your last reply - for context]`
    - `[Current message - respond to this]`

  </Accordion>

  <Accordion title="읽음 확인">
    읽음 확인은 허용된 수신 WhatsApp 메시지에 대해 기본적으로 활성화됩니다.

    전역 비활성화:

    ```json5
    {
      channels: {
        whatsapp: {
          sendReadReceipts: false,
        },
      },
    }
    ```

    계정별 재정의:

    ```json5
    {
      channels: {
        whatsapp: {
          accounts: {
            work: {
              sendReadReceipts: false,
            },
          },
        },
      },
    }
    ```

    self-chat 턴에서는 전역적으로 활성화되어 있어도 읽음 확인을 보내지 않습니다.

  </Accordion>
</AccordionGroup>

## 전달, 분할, 미디어

<AccordionGroup>
  <Accordion title="텍스트 분할">
    - 기본 분할 한도: `channels.whatsapp.textChunkLimit = 4000`
    - `channels.whatsapp.chunkMode = "length" | "newline"`
    - `newline` 모드는 단락 경계(빈 줄)를 우선하며, 이후 길이 안전 분할로 대체합니다
  </Accordion>

  <Accordion title="아웃바운드 미디어 동작">
    - 이미지, 비디오, 오디오(PTT 음성 메모), 문서 페이로드 지원
    - 음성 메모 호환성을 위해 `audio/ogg`는 `audio/ogg; codecs=opus`로 다시 작성됩니다
    - 비디오 전송 시 `gifPlayback: true`를 통해 애니메이션 GIF 재생 지원
    - 다중 미디어 응답 페이로드 전송 시 캡션은 첫 번째 미디어 항목에 적용됩니다
    - 미디어 소스는 HTTP(S), `file://`, 또는 로컬 경로일 수 있습니다
  </Accordion>

  <Accordion title="미디어 크기 제한 및 대체 동작">
    - 수신 미디어 저장 한도: `channels.whatsapp.mediaMaxMb`(기본값 `50`)
    - 아웃바운드 미디어 전송 한도: `channels.whatsapp.mediaMaxMb`(기본값 `50`)
    - 계정별 재정의는 `channels.whatsapp.accounts.<accountId>.mediaMaxMb` 사용
    - 이미지는 제한에 맞도록 자동 최적화됩니다(크기 조정/품질 스윕)
    - 미디어 전송 실패 시, 첫 번째 항목 대체 동작으로 응답을 조용히 버리지 않고 텍스트 경고를 전송합니다
  </Accordion>
</AccordionGroup>

## 반응 수준

`channels.whatsapp.reactionLevel`은 WhatsApp에서 에이전트가 이모지 반응을 얼마나 넓게 사용할지 제어합니다.

| 수준          | Ack 반응 | 에이전트 시작 반응 | 설명                                              |
| ------------- | -------- | ------------------ | ------------------------------------------------- |
| `"off"`       | 아니요   | 아니요             | 반응을 전혀 사용하지 않음                         |
| `"ack"`       | 예       | 아니요             | Ack 반응만 사용(응답 전 수신 확인)                |
| `"minimal"`   | 예       | 예(보수적)         | Ack + 보수적 가이드의 agent 반응                  |
| `"extensive"` | 예       | 예(권장)           | Ack + 권장 가이드의 agent 반응                    |

기본값: `"minimal"`.

계정별 재정의는 `channels.whatsapp.accounts.<id>.reactionLevel`을 사용합니다.

```json5
{
  channels: {
    whatsapp: {
      reactionLevel: "ack",
    },
  },
}
```

## 확인 반응

WhatsApp는 `channels.whatsapp.ackReaction`을 통해 수신 즉시 Ack 반응을 지원합니다.
Ack 반응은 `reactionLevel`에 의해 제어되며, `reactionLevel`이 `"off"`이면 억제됩니다.

```json5
{
  channels: {
    whatsapp: {
      ackReaction: {
        emoji: "👀",
        direct: true,
        group: "mentions", // always | mentions | never
      },
    },
  },
}
```

동작 참고:

- 수신이 허용된 직후 즉시 전송됨(응답 전)
- 실패는 로그에 기록되지만 일반 응답 전달을 막지 않음
- 그룹 모드 `mentions`는 멘션으로 트리거된 턴에 반응하며, 그룹 활성화 `always`는 이 검사를 우회하는 역할을 함
- WhatsApp는 `channels.whatsapp.ackReaction`을 사용합니다(레거시 `messages.ackReaction`은 여기서 사용되지 않음)

## 멀티 계정 및 자격 증명

<AccordionGroup>
  <Accordion title="계정 선택 및 기본값">
    - 계정 ID는 `channels.whatsapp.accounts`에서 가져옵니다
    - 기본 계정 선택: `default`가 있으면 그것을, 없으면 첫 번째로 구성된 계정 ID(정렬 기준)
    - 조회를 위해 계정 ID는 내부적으로 정규화됩니다
  </Accordion>

  <Accordion title="자격 증명 경로 및 레거시 호환성">
    - 현재 auth 경로: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
    - 백업 파일: `creds.json.bak`
    - `~/.openclaw/credentials/`의 레거시 기본 auth도 기본 계정 흐름에서 계속 인식/마이그레이션됩니다
  </Accordion>

  <Accordion title="로그아웃 동작">
    `openclaw channels logout --channel whatsapp [--account <id>]`는 해당 계정의 WhatsApp auth 상태를 지웁니다.

    레거시 auth 디렉터리에서는 `oauth.json`은 보존되고 Baileys auth 파일만 제거됩니다.

  </Accordion>
</AccordionGroup>

## 도구, 작업, config 쓰기

- agent 도구 지원에는 WhatsApp 반응 작업(`react`)이 포함됩니다.
- 작업 게이트:
  - `channels.whatsapp.actions.reactions`
  - `channels.whatsapp.actions.polls`
- 채널 시작 config 쓰기는 기본적으로 활성화되어 있습니다(`channels.whatsapp.configWrites=false`로 비활성화).

## 문제 해결

<AccordionGroup>
  <Accordion title="연결되지 않음(QR 필요)">
    증상: 채널 상태에 연결되지 않음으로 표시됨.

    해결 방법:

    ```bash
    openclaw channels login --channel whatsapp
    openclaw channels status
    ```

  </Accordion>

  <Accordion title="연결되었지만 연결 해제됨 / 재연결 루프">
    증상: 계정은 연결되었지만 연결 해제 또는 재연결 시도가 반복됨.

    해결 방법:

    ```bash
    openclaw doctor
    openclaw logs --follow
    ```

    필요하면 `channels login`으로 다시 연결하세요.

  </Accordion>

  <Accordion title="전송 시 활성 리스너 없음">
    대상 계정에 활성 gateway 리스너가 없으면 아웃바운드 전송은 즉시 실패합니다.

    gateway가 실행 중이고 계정이 연결되어 있는지 확인하세요.

  </Accordion>

  <Accordion title="그룹 메시지가 예상과 다르게 무시됨">
    다음 순서로 확인하세요.

    - `groupPolicy`
    - `groupAllowFrom` / `allowFrom`
    - `groups` 허용 목록 항목
    - 멘션 게이팅(`requireMention` + mention 패턴)
    - `openclaw.json`(JSON5)의 중복 키: 나중 항목이 앞선 항목을 덮어쓰므로 범위별로 `groupPolicy`는 하나만 유지하세요

  </Accordion>

  <Accordion title="Bun 런타임 경고">
    WhatsApp gateway 런타임은 Node를 사용해야 합니다. Bun은 안정적인 WhatsApp/Telegram gateway 운영과 호환되지 않는 것으로 표시됩니다.
  </Accordion>
</AccordionGroup>

## 구성 참조 포인터

기본 참조:

- [구성 참조 - WhatsApp](/gateway/configuration-reference#whatsapp)

신호가 높은 WhatsApp 필드:

- 접근: `dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`
- 전달: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `sendReadReceipts`, `ackReaction`, `reactionLevel`
- 멀티 계정: `accounts.<id>.enabled`, `accounts.<id>.authDir`, 계정 수준 재정의
- 운영: `configWrites`, `debounceMs`, `web.enabled`, `web.heartbeatSeconds`, `web.reconnect.*`
- 세션 동작: `session.dmScope`, `historyLimit`, `dmHistoryLimit`, `dms.<id>.historyLimit`

## 관련 항목

- [페어링](/channels/pairing)
- [그룹](/channels/groups)
- [보안](/gateway/security)
- [채널 라우팅](/channels/channel-routing)
- [멀티 agent 라우팅](/concepts/multi-agent)
- [문제 해결](/channels/troubleshooting)
