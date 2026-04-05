---
read_when:
    - Mattermost 설정
    - Mattermost 라우팅 디버깅
summary: Mattermost 봇 설정 및 OpenClaw 구성
title: Mattermost
x-i18n:
    generated_at: "2026-04-05T12:36:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: f21dc7543176fda0b38b00fab60f0daae38dffcf68fa1cf7930a9f14ec57cb5a
    source_path: channels/mattermost.md
    workflow: 15
---

# Mattermost

상태: 번들 plugin(봇 토큰 + WebSocket 이벤트). 채널, 그룹, DM이 지원됩니다.
Mattermost는 자체 호스팅 가능한 팀 메시징 플랫폼입니다. 제품 세부 정보와 다운로드는 공식 사이트
[mattermost.com](https://mattermost.com)에서 확인하세요.

## 번들 plugin

Mattermost는 현재 OpenClaw 릴리스에 번들 plugin으로 포함되어 있으므로, 일반적인
패키지 빌드에서는 별도 설치가 필요하지 않습니다.

구버전 빌드 또는 Mattermost가 제외된 커스텀 설치를 사용하는 경우,
수동으로 설치하세요.

CLI로 설치(npm 레지스트리):

```bash
openclaw plugins install @openclaw/mattermost
```

로컬 체크아웃(git 리포지토리에서 실행 중인 경우):

```bash
openclaw plugins install ./path/to/local/mattermost-plugin
```

자세한 내용: [Plugins](/tools/plugin)

## 빠른 설정

1. Mattermost plugin을 사용할 수 있는지 확인합니다.
   - 현재 패키지된 OpenClaw 릴리스에는 이미 번들로 포함되어 있습니다.
   - 구버전/커스텀 설치는 위 명령으로 수동 추가할 수 있습니다.
2. Mattermost 봇 계정을 만들고 **봇 토큰**을 복사합니다.
3. Mattermost **기본 URL**을 복사합니다(예: `https://chat.example.com`).
4. OpenClaw를 구성하고 gateway를 시작합니다.

최소 구성:

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
    },
  },
}
```

## 네이티브 슬래시 명령

네이티브 슬래시 명령은 옵트인 방식입니다. 활성화하면 OpenClaw가 Mattermost API를 통해 `oc_*` 슬래시 명령을 등록하고
gateway HTTP 서버에서 콜백 POST를 수신합니다.

```json5
{
  channels: {
    mattermost: {
      commands: {
        native: true,
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // Mattermost가 gateway에 직접 도달할 수 없을 때 사용합니다(리버스 프록시/공개 URL).
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
    },
  },
}
```

참고:

- `native: "auto"`는 Mattermost에서 기본적으로 비활성화됩니다. 활성화하려면 `native: true`로 설정하세요.
- `callbackUrl`이 생략되면 OpenClaw는 gateway host/port + `callbackPath`에서 이를 파생합니다.
- 멀티 계정 설정에서는 `commands`를 최상위에 두거나
  `channels.mattermost.accounts.<id>.commands` 아래에 둘 수 있습니다(계정 값이 최상위 필드를 재정의함).
- 명령 콜백은 OpenClaw가 `oc_*` 명령을 등록할 때 Mattermost가 반환한
  명령별 토큰으로 검증됩니다.
- 슬래시 콜백은 등록 실패, 부분적 시작, 또는
  콜백 토큰이 등록된 명령 중 어느 것과도 일치하지 않으면 차단된 상태로 실패합니다.
- 도달 가능성 요구 사항: 콜백 엔드포인트는 Mattermost 서버에서 도달 가능해야 합니다.
  - Mattermost가 OpenClaw와 같은 호스트/네트워크 네임스페이스에서 실행되지 않는 한 `callbackUrl`을 `localhost`로 설정하지 마세요.
  - 해당 URL이 `/api/channels/mattermost/command`를 OpenClaw로 리버스 프록시하지 않는 한 `callbackUrl`을 Mattermost 기본 URL로 설정하지 마세요.
  - 빠른 확인 방법은 `curl https://<gateway-host>/api/channels/mattermost/command`입니다. GET 요청은 `404`가 아니라 OpenClaw에서 `405 Method Not Allowed`를 반환해야 합니다.
- Mattermost 송신 허용 목록 요구 사항:
  - 콜백 대상이 private/tailnet/internal 주소를 가리키는 경우, Mattermost
    `ServiceSettings.AllowedUntrustedInternalConnections`에 콜백 호스트/도메인을 포함하도록 설정하세요.
  - 전체 URL이 아니라 호스트/도메인 항목을 사용하세요.
    - 올바름: `gateway.tailnet-name.ts.net`
    - 잘못됨: `https://gateway.tailnet-name.ts.net`

## 환경 변수(기본 계정)

환경 변수를 선호한다면 gateway 호스트에 다음을 설정하세요.

- `MATTERMOST_BOT_TOKEN=...`
- `MATTERMOST_URL=https://chat.example.com`

환경 변수는 **기본** 계정(`default`)에만 적용됩니다. 다른 계정은 반드시 config 값을 사용해야 합니다.

## 채팅 모드

Mattermost는 DM에 자동으로 응답합니다. 채널 동작은 `chatmode`로 제어됩니다.

- `oncall`(기본값): 채널에서 @멘션될 때만 응답합니다.
- `onmessage`: 모든 채널 메시지에 응답합니다.
- `onchar`: 메시지가 트리거 접두사로 시작할 때 응답합니다.

구성 예시:

```json5
{
  channels: {
    mattermost: {
      chatmode: "onchar",
      oncharPrefixes: [">", "!"],
    },
  },
}
```

참고:

- `onchar`는 명시적인 @멘션에도 계속 응답합니다.
- `channels.mattermost.requireMention`은 레거시 구성에서 존중되지만 `chatmode` 사용이 권장됩니다.

## 스레딩 및 세션

채널 및 그룹 응답을 메인 채널에 유지할지, 트리거한 게시물 아래 스레드를 시작할지 제어하려면
`channels.mattermost.replyToMode`를 사용하세요.

- `off`(기본값): 수신 게시물이 이미 스레드 안에 있는 경우에만 스레드에서 응답합니다.
- `first`: 최상위 채널/그룹 게시물의 경우 해당 게시물 아래에 스레드를 시작하고
  대화를 스레드 범위 세션으로 라우팅합니다.
- `all`: 현재 Mattermost에서는 `first`와 동일하게 동작합니다.
- 다이렉트 메시지는 이 설정을 무시하고 비스레드 상태를 유지합니다.

구성 예시:

```json5
{
  channels: {
    mattermost: {
      replyToMode: "all",
    },
  },
}
```

참고:

- 스레드 범위 세션은 트리거한 게시물 ID를 스레드 루트로 사용합니다.
- `first`와 `all`은 현재 동일합니다. Mattermost에 스레드 루트가 생기면
  후속 청크와 미디어가 모두 그 동일한 스레드에서 계속되기 때문입니다.

## 접근 제어(DM)

- 기본값: `channels.mattermost.dmPolicy = "pairing"`(알 수 없는 발신자는 페어링 코드를 받음).
- 승인 방법:
  - `openclaw pairing list mattermost`
  - `openclaw pairing approve mattermost <CODE>`
- 공개 DM: `channels.mattermost.dmPolicy="open"`과 `channels.mattermost.allowFrom=["*"]`.

## 채널(그룹)

- 기본값: `channels.mattermost.groupPolicy = "allowlist"`(멘션 게이트 방식).
- `channels.mattermost.groupAllowFrom`으로 발신자를 허용 목록에 추가합니다(사용자 ID 권장).
- 채널별 멘션 재정의는 `channels.mattermost.groups.<channelId>.requireMention`
  또는 기본값용 `channels.mattermost.groups["*"].requireMention` 아래에 있습니다.
- `@username` 일치는 변경 가능하며 `channels.mattermost.dangerouslyAllowNameMatching: true`일 때만 활성화됩니다.
- 공개 채널: `channels.mattermost.groupPolicy="open"`(멘션 게이트 방식).
- 런타임 참고: `channels.mattermost`가 완전히 없으면, 런타임은 그룹 검사에 `groupPolicy="allowlist"`로 대체됩니다(`channels.defaults.groupPolicy`가 설정되어 있어도 마찬가지임).

예시:

```json5
{
  channels: {
    mattermost: {
      groupPolicy: "open",
      groups: {
        "*": { requireMention: true },
        "team-channel-id": { requireMention: false },
      },
    },
  },
}
```

## 아웃바운드 전달 대상

`openclaw message send` 또는 cron/웹훅에서 다음 대상 형식을 사용하세요.

- 채널에는 `channel:<id>`
- DM에는 `user:<id>`
- DM에는 `@username`(Mattermost API를 통해 확인됨)

접두사 없는 불투명 ID(예: `64ifufp...`)는 Mattermost에서 **모호**합니다(사용자 ID인지 채널 ID인지 구분 안 됨).

OpenClaw는 이를 **사용자 우선**으로 해석합니다.

- ID가 사용자로 존재하면(`GET /api/v4/users/<id>` 성공), OpenClaw는 `/api/v4/channels/direct`를 통해 다이렉트 채널을 확인하여 **DM**을 전송합니다.
- 그렇지 않으면 해당 ID는 **채널 ID**로 처리됩니다.

결정적인 동작이 필요하면 항상 명시적 접두사(`user:<id>` / `channel:<id>`)를 사용하세요.

## DM 채널 재시도

OpenClaw가 Mattermost DM 대상으로 전송할 때 먼저 다이렉트 채널을 확인해야 하는 경우,
기본적으로 일시적인 다이렉트 채널 생성 실패를 재시도합니다.

Mattermost plugin 전체에 대해 그 동작을 전역 조정하려면 `channels.mattermost.dmChannelRetry`를 사용하고,
특정 계정 하나에 대해서만 조정하려면 `channels.mattermost.accounts.<id>.dmChannelRetry`를 사용하세요.

```json5
{
  channels: {
    mattermost: {
      dmChannelRetry: {
        maxRetries: 3,
        initialDelayMs: 1000,
        maxDelayMs: 10000,
        timeoutMs: 30000,
      },
    },
  },
}
```

참고:

- 이는 모든 Mattermost API 호출이 아니라 DM 채널 생성(`/api/v4/channels/direct`)에만 적용됩니다.
- 재시도는 rate limit, 5xx 응답, 네트워크 오류 또는 타임아웃 오류 같은 일시적 실패에 적용됩니다.
- `429`를 제외한 4xx 클라이언트 오류는 영구 오류로 처리되며 재시도하지 않습니다.

## 반응(message 도구)

- `channel=mattermost`와 함께 `message action=react`를 사용하세요.
- `messageId`는 Mattermost 게시물 ID입니다.
- `emoji`는 `thumbsup` 또는 `:+1:` 같은 이름을 받습니다(콜론은 선택 사항).
- 반응을 제거하려면 `remove=true`(boolean)를 설정하세요.
- 반응 추가/제거 이벤트는 라우팅된 agent 세션으로 시스템 이벤트로 전달됩니다.

예시:

```
message action=react channel=mattermost target=channel:<channelId> messageId=<postId> emoji=thumbsup
message action=react channel=mattermost target=channel:<channelId> messageId=<postId> emoji=thumbsup remove=true
```

구성:

- `channels.mattermost.actions.reactions`: 반응 동작 활성화/비활성화(기본값 true).
- 계정별 재정의: `channels.mattermost.accounts.<id>.actions.reactions`.

## 인터랙티브 버튼(message 도구)

클릭 가능한 버튼이 포함된 메시지를 보냅니다. 사용자가 버튼을 클릭하면 에이전트가
선택값을 받아 응답할 수 있습니다.

채널 기능에 `inlineButtons`를 추가하여 버튼을 활성화하세요.

```json5
{
  channels: {
    mattermost: {
      capabilities: ["inlineButtons"],
    },
  },
}
```

`buttons` 파라미터와 함께 `message action=send`를 사용하세요. 버튼은 2차원 배열(버튼 행)입니다.

```
message action=send channel=mattermost target=channel:<channelId> buttons=[[{"text":"Yes","callback_data":"yes"},{"text":"No","callback_data":"no"}]]
```

버튼 필드:

- `text`(필수): 표시 레이블.
- `callback_data`(필수): 클릭 시 다시 전송되는 값(action ID로 사용됨).
- `style`(선택 사항): `"default"`, `"primary"`, 또는 `"danger"`.

사용자가 버튼을 클릭하면:

1. 모든 버튼이 확인 줄로 교체됩니다(예: "✓ **Yes** selected by @user").
2. 에이전트는 선택 내용을 수신 메시지로 받아 응답합니다.

참고:

- 버튼 콜백은 HMAC-SHA256 검증을 사용합니다(자동, 별도 구성 불필요).
- Mattermost는 API 응답에서 callback data를 제거합니다(보안 기능). 따라서 클릭 시 모든 버튼이 제거되며, 일부만 제거하는 것은 불가능합니다.
- 하이픈 또는 밑줄이 포함된 action ID는 자동으로 정리됩니다
  (Mattermost 라우팅 제한).

구성:

- `channels.mattermost.capabilities`: 기능 문자열 배열. 에이전트 시스템 프롬프트에서
  버튼 도구 설명을 활성화하려면 `"inlineButtons"`를 추가하세요.
- `channels.mattermost.interactions.callbackBaseUrl`: 버튼 콜백용 선택적 외부 기본 URL
  (예: `https://gateway.example.com`). Mattermost가 바인드 host의 gateway에 직접
  도달할 수 없을 때 사용하세요.
- 멀티 계정 설정에서는 동일한 필드를
  `channels.mattermost.accounts.<id>.interactions.callbackBaseUrl` 아래에도 설정할 수 있습니다.
- `interactions.callbackBaseUrl`이 생략되면 OpenClaw는
  `gateway.customBindHost` + `gateway.port`에서 콜백 URL을 파생한 다음, `http://localhost:<port>`로 대체합니다.
- 도달 가능성 규칙: 버튼 콜백 URL은 Mattermost 서버에서 도달 가능해야 합니다.
  Mattermost와 OpenClaw가 같은 호스트/네트워크 네임스페이스에서 실행될 때만 `localhost`가 작동합니다.
- 콜백 대상이 private/tailnet/internal인 경우, 해당 host/domain을 Mattermost
  `ServiceSettings.AllowedUntrustedInternalConnections`에 추가하세요.

### Direct API 통합(외부 스크립트)

외부 스크립트와 웹훅은 에이전트의 `message` 도구를 거치지 않고
Mattermost REST API를 통해 직접 버튼을 게시할 수 있습니다. 가능하면 extension의 `buildButtonAttachments()`를 사용하세요.
원시 JSON을 게시하는 경우 다음 규칙을 따르세요.

**페이로드 구조:**

```json5
{
  channel_id: "<channelId>",
  message: "Choose an option:",
  props: {
    attachments: [
      {
        actions: [
          {
            id: "mybutton01", // 영숫자만 허용 — 아래 참조
            type: "button", // 필수, 없으면 클릭이 조용히 무시됨
            name: "Approve", // 표시 레이블
            style: "primary", // 선택 사항: "default", "primary", "danger"
            integration: {
              url: "https://gateway.example.com/mattermost/interactions/default",
              context: {
                action_id: "mybutton01", // 버튼 id와 일치해야 함(이름 조회용)
                action: "approve",
                // ... 사용자 정의 필드 ...
                _token: "<hmac>", // 아래 HMAC 섹션 참조
              },
            },
          },
        ],
      },
    ],
  },
}
```

**중요 규칙:**

1. attachment는 최상위 `attachments`가 아니라 `props.attachments`에 넣어야 합니다(그렇지 않으면 조용히 무시됨).
2. 모든 action에는 `type: "button"`이 필요합니다. 없으면 클릭이 조용히 삼켜집니다.
3. 모든 action에는 `id` 필드가 필요합니다. Mattermost는 ID가 없는 action을 무시합니다.
4. Action `id`는 **영숫자만** 허용됩니다(`[a-zA-Z0-9]`). 하이픈과 밑줄은
   Mattermost의 서버 측 action 라우팅을 깨뜨립니다(`404` 반환). 사용 전에 제거하세요.
5. 확인 메시지에 원시 ID 대신 버튼 이름(예: "Approve")이 표시되도록
   `context.action_id`는 버튼의 `id`와 일치해야 합니다.
6. `context.action_id`는 필수입니다. 없으면 interaction 핸들러가 `400`을 반환합니다.

**HMAC 토큰 생성:**

gateway는 HMAC-SHA256으로 버튼 클릭을 검증합니다. 외부 스크립트는 gateway의 검증 로직과
일치하는 토큰을 생성해야 합니다.

1. 봇 토큰에서 secret을 파생합니다:
   `HMAC-SHA256(key="openclaw-mattermost-interactions", data=botToken)`
2. `_token`을 제외한 모든 필드로 context 객체를 만듭니다.
3. **정렬된 키**와 **공백 없음**으로 직렬화합니다(gateway는 정렬된 키로 `JSON.stringify`를 사용하며,
   이는 압축된 출력을 생성합니다).
4. 서명: `HMAC-SHA256(key=secret, data=serializedContext)`
5. 결과 hex digest를 context의 `_token`으로 추가합니다.

Python 예시:

```python
import hmac, hashlib, json

secret = hmac.new(
    b"openclaw-mattermost-interactions",
    bot_token.encode(), hashlib.sha256
).hexdigest()

ctx = {"action_id": "mybutton01", "action": "approve"}
payload = json.dumps(ctx, sort_keys=True, separators=(",", ":"))
token = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

context = {**ctx, "_token": token}
```

일반적인 HMAC 함정:

- Python의 `json.dumps`는 기본적으로 공백을 추가합니다(`{"key": "val"}`). JavaScript의 압축 출력(`{"key":"val"}`)과 맞추려면
  `separators=(",", ":")`를 사용하세요.
- 항상 **모든** context 필드(`_token` 제외)에 서명하세요. gateway는 `_token`을 제거한 뒤
  남은 모든 것을 서명합니다. 일부만 서명하면 조용한 검증 실패가 발생합니다.
- `sort_keys=True`를 사용하세요. gateway는 서명 전에 키를 정렬하고, Mattermost는
  페이로드를 저장할 때 context 필드를 재정렬할 수 있습니다.
- secret은 랜덤 바이트가 아니라 봇 토큰에서 파생하세요(결정적). secret은
  버튼을 생성하는 프로세스와 이를 검증하는 gateway에서 동일해야 합니다.

## 디렉터리 어댑터

Mattermost plugin에는 Mattermost API를 통해 채널 및 사용자 이름을 확인하는
디렉터리 어댑터가 포함되어 있습니다. 이를 통해
`openclaw message send` 및 cron/웹훅 전달에서 `#channel-name`과 `@username` 대상을 사용할 수 있습니다.

별도 구성은 필요하지 않습니다. 어댑터는 계정 config의 봇 토큰을 사용합니다.

## 멀티 계정

Mattermost는 `channels.mattermost.accounts` 아래에서 여러 계정을 지원합니다.

```json5
{
  channels: {
    mattermost: {
      accounts: {
        default: { name: "Primary", botToken: "mm-token", baseUrl: "https://chat.example.com" },
        alerts: { name: "Alerts", botToken: "mm-token-2", baseUrl: "https://alerts.example.com" },
      },
    },
  },
}
```

## 문제 해결

- 채널에서 응답이 없음: 봇이 채널에 들어가 있는지 확인하고 멘션하세요(oncall), 트리거 접두사를 사용하세요(onchar), 또는 `chatmode: "onmessage"`로 설정하세요.
- 인증 오류: 봇 토큰, 기본 URL, 계정 활성화 여부를 확인하세요.
- 멀티 계정 문제: 환경 변수는 `default` 계정에만 적용됩니다.
- 네이티브 슬래시 명령이 `Unauthorized: invalid command token.`을 반환함: OpenClaw가
  콜백 토큰을 수락하지 않았습니다. 일반적인 원인:
  - 슬래시 명령 등록이 실패했거나 시작 시 일부만 완료됨
  - 콜백이 잘못된 gateway/계정으로 도달함
  - Mattermost에 이전 콜백 대상을 가리키는 오래된 명령이 여전히 남아 있음
  - gateway가 슬래시 명령을 다시 활성화하지 않고 재시작됨
- 네이티브 슬래시 명령이 작동을 멈추면 로그에서
  `mattermost: failed to register slash commands` 또는
  `mattermost: native slash commands enabled but no commands could be registered`
  를 확인하세요.
- `callbackUrl`이 생략되었고 로그에서 콜백이
  `http://127.0.0.1:18789/...`로 확인되었다는 경고가 나오면, 그 URL은
  Mattermost가 OpenClaw와 같은 호스트/네트워크 네임스페이스에서 실행될 때만
  도달 가능할 가능성이 높습니다. 대신 명시적으로 외부에서 도달 가능한
  `commands.callbackUrl`을 설정하세요.
- 버튼이 흰색 상자로 보임: 에이전트가 잘못된 버튼 데이터를 보내고 있을 수 있습니다. 각 버튼에 `text`와 `callback_data` 필드가 모두 있는지 확인하세요.
- 버튼은 렌더링되지만 클릭해도 아무 일도 일어나지 않음: Mattermost 서버 config의 `AllowedUntrustedInternalConnections`에 `127.0.0.1 localhost`가 포함되어 있는지, 그리고 ServiceSettings에서 `EnablePostActionIntegration`이 `true`인지 확인하세요.
- 버튼 클릭 시 404 반환: 버튼 `id`에 하이픈 또는 밑줄이 포함되어 있을 가능성이 높습니다. Mattermost의 action 라우터는 영숫자가 아닌 ID에서 깨집니다. `[a-zA-Z0-9]`만 사용하세요.
- Gateway 로그에 `invalid _token`이 표시됨: HMAC 불일치입니다. 모든 context 필드(일부가 아님)에 서명하는지, 키를 정렬하는지, 압축 JSON(공백 없음)을 사용하는지 확인하세요. 위의 HMAC 섹션을 참조하세요.
- Gateway 로그에 `missing _token in context`가 표시됨: 버튼 context에 `_token` 필드가 없습니다. integration 페이로드를 만들 때 이를 포함했는지 확인하세요.
- 확인 메시지에 버튼 이름 대신 원시 ID가 표시됨: `context.action_id`가 버튼의 `id`와 일치하지 않습니다. 둘 다 동일한 정리된 값으로 설정하세요.
- 에이전트가 버튼을 모름: Mattermost 채널 config에 `capabilities: ["inlineButtons"]`를 추가하세요.

## 관련 항목

- [Channels Overview](/channels) — 지원되는 모든 채널
- [Pairing](/channels/pairing) — DM 인증 및 페어링 흐름
- [Groups](/channels/groups) — 그룹 채팅 동작 및 멘션 게이팅
- [Channel Routing](/channels/channel-routing) — 메시지 세션 라우팅
- [Security](/gateway/security) — 접근 모델 및 보안 강화
