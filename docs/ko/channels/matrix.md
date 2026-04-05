---
read_when:
    - OpenClaw에서 Matrix를 설정할 때
    - Matrix E2EE 및 검증을 구성할 때
summary: Matrix 지원 상태, 설정 방법 및 구성 예시
title: Matrix
x-i18n:
    generated_at: "2026-04-05T12:37:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: ba5c49ad2125d97adf66b5517f8409567eff8b86e20224a32fcb940a02cb0659
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix는 OpenClaw용 Matrix 번들 채널 plugin입니다.
공식 `matrix-js-sdk`를 사용하며 DM, room, thread, media, reaction, poll, location, E2EE를 지원합니다.

## 번들 plugin

Matrix는 현재 OpenClaw 릴리스에 번들 plugin으로 포함되어 있으므로, 일반적인
패키지 빌드에서는 별도 설치가 필요하지 않습니다.

이전 빌드 또는 Matrix가 제외된 사용자 지정 설치를 사용 중이라면,
수동으로 설치하세요:

npm에서 설치:

```bash
openclaw plugins install @openclaw/matrix
```

로컬 체크아웃에서 설치:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

plugin 동작 및 설치 규칙은 [Plugins](/tools/plugin)를 참조하세요.

## 설정

1. Matrix plugin을 사용할 수 있는지 확인합니다.
   - 현재 패키지된 OpenClaw 릴리스에는 이미 포함되어 있습니다.
   - 이전/사용자 지정 설치에서는 위 명령으로 수동 추가할 수 있습니다.
2. homeserver에 Matrix 계정을 만듭니다.
3. `channels.matrix`를 다음 중 하나로 구성합니다:
   - `homeserver` + `accessToken`, 또는
   - `homeserver` + `userId` + `password`.
4. 게이트웨이를 다시 시작합니다.
5. 봇과 DM을 시작하거나 room에 초대합니다.

대화형 설정 경로:

```bash
openclaw channels add
openclaw configure --section channels
```

Matrix 마법사가 실제로 묻는 항목:

- homeserver URL
- 인증 방식: 액세스 토큰 또는 비밀번호
- 비밀번호 인증을 선택한 경우에만 user ID
- 선택적 device 이름
- E2EE 활성화 여부
- 지금 Matrix room 접근을 구성할지 여부

알아두어야 할 마법사 동작:

- 선택한 계정에 대해 Matrix 인증 env var가 이미 존재하고, 해당 계정의 인증이 아직 config에 저장되지 않은 경우, 마법사는 env 바로가기를 제안하고 해당 계정에 `enabled: true`만 기록합니다.
- 다른 Matrix 계정을 대화형으로 추가하면, 입력한 계정 이름이 config와 env var에 사용되는 account ID로 정규화됩니다. 예를 들어 `Ops Bot`은 `ops-bot`이 됩니다.
- DM 허용 목록 프롬프트는 전체 `@user:server` 값을 즉시 받을 수 있습니다. 표시 이름은 실시간 디렉터리 조회에서 정확히 하나의 일치 항목을 찾은 경우에만 작동하며, 그렇지 않으면 마법사가 전체 Matrix ID로 다시 시도하라고 요청합니다.
- Room 허용 목록 프롬프트는 room ID와 alias를 직접 받을 수 있습니다. 참가 중인 room 이름도 실시간으로 확인할 수 있지만, 확인되지 않은 이름은 설정 중 입력된 그대로만 유지되며 이후 런타임 허용 목록 해석에서는 무시됩니다. `!room:server` 또는 `#alias:server`를 권장합니다.
- 런타임 room/세션 식별은 안정적인 Matrix room ID를 사용합니다. room에 선언된 alias는 조회 입력으로만 사용되며, 장기 세션 키나 안정적인 그룹 식별자로는 사용되지 않습니다.
- 저장 전에 room 이름을 해석하려면 `openclaw channels resolve --channel matrix "Project Room"`를 사용하세요.

최소 토큰 기반 설정:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

비밀번호 기반 설정(로그인 후 토큰이 캐시됨):

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix는 캐시된 자격 증명을 `~/.openclaw/credentials/matrix/`에 저장합니다.
기본 계정은 `credentials.json`을 사용하고, 이름 있는 계정은 `credentials-<account>.json`을 사용합니다.

환경 변수 대응 항목(config 키가 설정되지 않은 경우 사용됨):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

기본이 아닌 계정에는 계정 범위 env var를 사용합니다:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

계정 `ops` 예시:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

정규화된 계정 ID `ops-bot`에는 다음을 사용합니다:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix는 계정 ID의 구두점을 이스케이프하여 범위 지정 env var 충돌을 방지합니다.
예를 들어 `-`는 `_X2D_`가 되므로 `ops-prod`는 `MATRIX_OPS_X2D_PROD_*`에 매핑됩니다.

대화형 마법사는 해당 인증 env var가 이미 존재하고 선택한 계정에 Matrix 인증이 아직 config에 저장되지 않은 경우에만 env-var 바로가기를 제안합니다.

## 구성 예시

다음은 DM 페어링, room 허용 목록, E2EE 활성화를 포함한 실용적인 기준 구성입니다:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

## 스트리밍 미리보기

Matrix 답장 스트리밍은 opt-in입니다.

모델이 텍스트를 생성하는 동안 OpenClaw가 단일 초안 답장을 보내고,
그 초안을 제자리에서 수정한 뒤, 답장이
완료되면 최종 확정하도록 하려면 `channels.matrix.streaming`을 `"partial"`로 설정하세요:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"`가 기본값입니다. OpenClaw는 최종 답장을 기다렸다가 한 번만 전송합니다.
- `streaming: "partial"`은 여러 개의 부분 메시지를 보내는 대신 현재 assistant 블록에 대해 수정 가능한 미리보기 메시지 하나를 생성합니다.
- `blockStreaming: true`는 별도의 Matrix 진행 메시지를 활성화합니다. `streaming: "partial"`과 함께 사용하면 Matrix는 현재 블록의 실시간 초안을 유지하고 완료된 블록은 별도 메시지로 보존합니다.
- `streaming: "partial"`이고 `blockStreaming`이 꺼져 있으면, Matrix는 실시간 초안만 수정하고 해당 블록 또는 턴이 끝나면 완료된 답장을 한 번 전송합니다.
- 미리보기가 더 이상 하나의 Matrix 이벤트에 맞지 않으면, OpenClaw는 미리보기 스트리밍을 중단하고 일반 최종 전달로 대체합니다.
- 미디어 답장은 여전히 첨부파일을 일반 방식으로 전송합니다. 오래된 미리보기를 더 이상 안전하게 재사용할 수 없으면 OpenClaw는 최종 미디어 답장을 보내기 전에 이를 redaction 처리합니다.
- 미리보기 수정에는 추가 Matrix API 호출 비용이 듭니다. 가장 보수적인 속도 제한 동작을 원하면 스트리밍을 끄세요.

`blockStreaming`만으로는 초안 미리보기가 활성화되지 않습니다.
미리보기 수정을 위해서는 `streaming: "partial"`을 사용하고, 완료된 assistant 블록도 별도 진행 메시지로 유지하려면 그다음 `blockStreaming: true`를 추가하세요.

## 암호화 및 검증

암호화된(E2EE) room에서 발신 이미지 이벤트는 `thumbnail_file`을 사용하므로 이미지 미리보기도 전체 첨부파일과 함께 암호화됩니다. 암호화되지 않은 room은 계속 일반 `thumbnail_url`을 사용합니다. 별도 구성은 필요하지 않습니다. plugin이 E2EE 상태를 자동 감지합니다.

### 봇 간 room

기본적으로 다른 구성된 OpenClaw Matrix 계정의 Matrix 메시지는 무시됩니다.

에이전트 간 Matrix 트래픽을 의도적으로 허용하려면 `allowBots`를 사용하세요:

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true`는 허용된 room과 DM에서 다른 구성된 Matrix 봇 계정의 메시지를 허용합니다.
- `allowBots: "mentions"`는 room에서 해당 메시지가 이 봇을 명시적으로 멘션할 때만 허용합니다. DM은 여전히 허용됩니다.
- `groups.<room>.allowBots`는 하나의 room에 대해 계정 수준 설정을 재정의합니다.
- OpenClaw는 자기 자신에게 답장하는 루프를 방지하기 위해 동일한 Matrix user ID의 메시지는 계속 무시합니다.
- 여기서 Matrix는 기본적인 bot 플래그를 제공하지 않습니다. OpenClaw는 "봇이 작성한"을 "이 OpenClaw 게이트웨이에서 구성된 다른 Matrix 계정이 보낸" 것으로 간주합니다.

공유 room에서 봇 간 트래픽을 활성화할 때는 엄격한 room 허용 목록과 멘션 요구 사항을 사용하세요.

암호화 활성화:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

검증 상태 확인:

```bash
openclaw matrix verify status
```

자세한 상태(전체 진단):

```bash
openclaw matrix verify status --verbose
```

저장된 복구 키를 기계 판독 가능한 출력에 포함:

```bash
openclaw matrix verify status --include-recovery-key --json
```

교차 서명 및 검증 상태 부트스트랩:

```bash
openclaw matrix verify bootstrap
```

다중 계정 지원: 계정별 자격 증명과 선택적 `name`이 포함된 `channels.matrix.accounts`를 사용하세요. 공통 패턴은 [구성 참조](/gateway/configuration-reference#multi-account-all-channels)를 참조하세요.

자세한 부트스트랩 진단:

```bash
openclaw matrix verify bootstrap --verbose
```

부트스트랩 전에 새 교차 서명 ID 재설정을 강제:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

복구 키로 이 device 검증:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

자세한 device 검증 정보:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

room-key 백업 상태 확인:

```bash
openclaw matrix verify backup status
```

자세한 백업 상태 진단:

```bash
openclaw matrix verify backup status --verbose
```

서버 백업에서 room key 복원:

```bash
openclaw matrix verify backup restore
```

자세한 복원 진단:

```bash
openclaw matrix verify backup restore --verbose
```

현재 서버 백업을 삭제하고 새 백업 기준선을 만듭니다. 저장된
백업 키를 정상적으로 로드할 수 없으면, 이 재설정은 이후 콜드 스타트에서
새 백업 키를 로드할 수 있도록 secret storage를 다시 생성할 수도 있습니다:

```bash
openclaw matrix verify backup reset --yes
```

모든 `verify` 명령은 기본적으로 간결하며(내부 SDK의 조용한 로깅 포함), `--verbose`를 사용할 때만 자세한 진단을 표시합니다.
스크립트에서는 전체 기계 판독 가능 출력을 위해 `--json`을 사용하세요.

다중 계정 설정에서 Matrix CLI 명령은 `--account <id>`를 전달하지 않으면 암묵적인 Matrix 기본 계정을 사용합니다.
이름 있는 계정을 여러 개 구성한 경우 `channels.matrix.defaultAccount`를 먼저 설정하지 않으면, 이러한 암묵적 CLI 작업은 중단되고 계정을 명시적으로 선택하라고 요청합니다.
검증 또는 device 작업이 이름 있는 계정을 명시적으로 대상으로 하도록 하려면 항상 `--account`를 사용하세요:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

이름 있는 계정에서 암호화가 비활성화되었거나 사용할 수 없는 경우, Matrix 경고와 검증 오류는 해당 계정의 config 키를 가리킵니다. 예: `channels.matrix.accounts.assistant.encryption`.

### "검증됨"의 의미

OpenClaw는 이 Matrix device가 사용자 자신의 교차 서명 ID에 의해 검증된 경우에만 검증된 것으로 간주합니다.
실제로 `openclaw matrix verify status --verbose`는 세 가지 신뢰 신호를 표시합니다:

- `Locally trusted`: 이 device는 현재 클라이언트에서만 신뢰됨
- `Cross-signing verified`: SDK가 이 device를 교차 서명을 통해 검증된 것으로 보고함
- `Signed by owner`: 이 device가 자신의 self-signing key로 서명됨

`Verified by owner`는 교차 서명 검증 또는 소유자 서명이 있을 때만 `yes`가 됩니다.
로컬 신뢰만으로는 OpenClaw가 이 device를 완전히 검증된 것으로 취급하기에 충분하지 않습니다.

### bootstrap이 하는 일

`openclaw matrix verify bootstrap`은 암호화된 Matrix 계정의 복구 및 설정 명령입니다.
다음 작업을 순서대로 수행합니다:

- 가능하면 기존 복구 키를 재사용하며 secret storage를 bootstrap
- 교차 서명을 bootstrap하고 누락된 공개 교차 서명 키를 업로드
- 현재 device를 표시하고 교차 서명하려 시도
- 기존 서버 측 room-key 백업이 없으면 새로 생성

homeserver가 교차 서명 키 업로드에 상호작용 인증을 요구하는 경우, OpenClaw는 먼저 인증 없이 업로드를 시도하고, 다음으로 `m.login.dummy`, 마지막으로 `channels.matrix.password`가 구성된 경우 `m.login.password`로 시도합니다.

현재 교차 서명 ID를 버리고 새로 만들 의도가 있을 때만 `--force-reset-cross-signing`을 사용하세요.

현재 room-key 백업을 의도적으로 버리고 향후 메시지에 대한 새
백업 기준선을 시작하려면 `openclaw matrix verify backup reset --yes`를 사용하세요.
복구할 수 없는 이전 암호화 기록이 계속
사용 불가능한 상태로 남을 수 있고, 현재 백업 secret을 안전하게 로드할 수 없는 경우 OpenClaw가 secret storage를 다시 만들 수 있다는 점을 받아들일 때만 수행하세요.

### 새 백업 기준선

향후 암호화된 메시지는 계속 작동하도록 유지하되 복구 불가능한 이전 기록 손실을 감수할 수 있다면, 다음 명령을 순서대로 실행하세요:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

이름 있는 Matrix 계정을 명시적으로 대상으로 하려면 각 명령에 `--account <id>`를 추가하세요.

### 시작 동작

`encryption: true`일 때 Matrix는 기본적으로 `startupVerification`을 `"if-unverified"`로 설정합니다.
시작 시 이 device가 아직 검증되지 않았다면, Matrix는 다른 Matrix 클라이언트에서 self-verification을 요청하고,
이미 보류 중인 요청이 있으면 중복 요청을 건너뛰며, 재시작 후 재시도 전에 로컬 쿨다운을 적용합니다.
실패한 요청 시도는 기본적으로 성공적으로 요청을 만든 경우보다 더 빨리 재시도합니다.
자동 시작 요청을 비활성화하려면 `startupVerification: "off"`로 설정하거나, 더 짧거나 긴 재시도 창이 필요하면 `startupVerificationCooldownHours`를 조정하세요.

시작 시에는 보수적인 crypto bootstrap 단계도 자동으로 수행됩니다.
이 단계는 먼저 현재 secret storage와 교차 서명 ID를 재사용하려고 하며, 명시적인 bootstrap 복구 흐름을 실행하지 않는 한 교차 서명을 재설정하지 않습니다.

시작 시 손상된 bootstrap 상태를 발견하고 `channels.matrix.password`가 구성되어 있으면, OpenClaw는 더 엄격한 복구 경로를 시도할 수 있습니다.
현재 device가 이미 owner-signed 상태라면 OpenClaw는 이를 자동 재설정하지 않고 해당 ID를 보존합니다.

이전 공개 Matrix plugin에서 업그레이드할 때:

- OpenClaw는 가능하면 동일한 Matrix 계정, 액세스 토큰, device ID를 자동으로 재사용합니다.
- 실행 가능한 Matrix 마이그레이션 변경이 수행되기 전에 OpenClaw는 `~/Backups/openclaw-migrations/` 아래에 복구 스냅샷을 생성하거나 재사용합니다.
- 여러 Matrix 계정을 사용하는 경우, 이전 flat-store 레이아웃에서 업그레이드하기 전에 `channels.matrix.defaultAccount`를 설정하여 어떤 계정이 해당 공유 레거시 상태를 받아야 하는지 OpenClaw가 알 수 있게 하세요.
- 이전 plugin이 Matrix room-key 백업 복호화 키를 로컬에 저장했다면, 시작 시 또는 `openclaw doctor --fix` 실행 시 이를 새 복구 키 흐름으로 자동 가져옵니다.
- 마이그레이션 준비 후 Matrix 액세스 토큰이 변경된 경우, 시작 시 자동 백업 복원을 포기하기 전에 보류 중인 레거시 복원 상태가 있는 형제 토큰 해시 저장소 루트를 검색합니다.
- 동일 계정, homeserver, user에 대해 나중에 Matrix 액세스 토큰이 변경되면, OpenClaw는 빈 Matrix 상태 디렉터리에서 시작하는 대신 가장 완전한 기존 토큰 해시 저장소 루트를 우선 재사용합니다.
- 다음 게이트웨이 시작 시 백업된 room key가 새 crypto 저장소로 자동 복원됩니다.
- 이전 plugin에 백업되지 않은 로컬 전용 room key가 있었다면, OpenClaw는 이를 명확히 경고합니다. 해당 key는 이전 rust crypto 저장소에서 자동 내보내기할 수 없으므로 일부 이전 암호화 기록은 수동 복구 전까지 계속 사용할 수 없을 수 있습니다.
- 전체 업그레이드 흐름, 제한 사항, 복구 명령, 일반적인 마이그레이션 메시지는 [Matrix migration](/install/migrating-matrix)을 참조하세요.

암호화된 런타임 상태는 계정별, 사용자별 토큰 해시 루트 아래의
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`에 구성됩니다.
이 디렉터리에는 sync 저장소(`bot-storage.json`), crypto 저장소(`crypto/`),
복구 키 파일(`recovery-key.json`), IndexedDB 스냅샷(`crypto-idb-snapshot.json`),
thread 바인딩(`thread-bindings.json`), 시작 검증 상태(`startup-verification.json`)가
해당 기능 사용 시 포함됩니다.
토큰이 변경되더라도 계정 ID가 같으면 OpenClaw는 해당 계정/homeserver/user 튜플에 대해 가장 적합한 기존
루트를 재사용하므로 이전 sync 상태, crypto 상태, thread 바인딩,
시작 검증 상태를 계속 확인할 수 있습니다.

### Node crypto 저장소 모델

이 plugin의 Matrix E2EE는 Node에서 공식 `matrix-js-sdk` Rust crypto 경로를 사용합니다.
이 경로는 crypto 상태를 재시작 후에도 유지하려면 IndexedDB 기반 영속성을 기대합니다.

OpenClaw는 현재 Node에서 다음 방식으로 이를 제공합니다:

- SDK가 기대하는 IndexedDB API shim으로 `fake-indexeddb` 사용
- `initRustCrypto` 전에 `crypto-idb-snapshot.json`에서 Rust crypto IndexedDB 내용을 복원
- 초기화 후와 런타임 중에 업데이트된 IndexedDB 내용을 다시 `crypto-idb-snapshot.json`에 저장
- gateway 런타임 영속성과 CLI 유지관리 작업이 같은 스냅샷 파일에서 경쟁하지 않도록 advisory 파일 잠금을 사용해 `crypto-idb-snapshot.json`에 대한 스냅샷 복원과 저장을 직렬화

이는 사용자 지정 crypto 구현이 아니라 호환성/저장소 플러밍입니다.
스냅샷 파일은 민감한 런타임 상태이며 제한적인 파일 권한으로 저장됩니다.
OpenClaw의 보안 모델에서 gateway host와 로컬 OpenClaw 상태 디렉터리는 이미 신뢰된 운영자 경계 내부에 있으므로, 이는 별도의 원격 신뢰 경계라기보다 주로 운영상 내구성 문제입니다.

계획된 개선 사항:

- 영속적인 Matrix key material에 대한 SecretRef 지원을 추가하여 복구 키와 관련 저장소 암호화 secret을 로컬 파일뿐 아니라 OpenClaw secrets provider에서도 가져올 수 있도록 함

## 프로필 관리

선택한 계정의 Matrix self-profile을 다음 명령으로 업데이트합니다:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

이름 있는 Matrix 계정을 명시적으로 대상으로 하려면 `--account <id>`를 추가하세요.

Matrix는 `mxc://` 아바타 URL을 직접 받을 수 있습니다. `http://` 또는 `https://` 아바타 URL을 전달하면 OpenClaw는 먼저 이를 Matrix에 업로드하고, 해석된 `mxc://` URL을 다시 `channels.matrix.avatarUrl`(또는 선택한 계정 재정의)에 저장합니다.

## 자동 검증 알림

이제 Matrix는 strict DM 검증 room에 검증 수명 주기 알림을 `m.notice` 메시지로 직접 게시합니다.
여기에는 다음이 포함됩니다:

- 검증 요청 알림
- 검증 준비 알림(명시적인 "Verify by emoji" 안내 포함)
- 검증 시작 및 완료 알림
- 사용 가능한 경우 SAS 세부 정보(이모지 및 10진수)

다른 Matrix 클라이언트에서 들어오는 검증 요청은 OpenClaw가 추적하고 자동 수락합니다.
self-verification 흐름에서는 이모지 검증을 사용할 수 있게 되면 OpenClaw도 자동으로 SAS 흐름을 시작하고 자체 측을 확인합니다.
다른 Matrix 사용자/device의 검증 요청에 대해서는 OpenClaw가 요청을 자동 수락한 뒤 SAS 흐름이 정상적으로 진행되기를 기다립니다.
검증을 완료하려면 여전히 Matrix 클라이언트에서 이모지 또는 10진수 SAS를 비교하고 그곳에서 "They match"를 확인해야 합니다.

OpenClaw는 self-initiated duplicate flow를 무작정 자동 수락하지 않습니다. 시작 시 self-verification 요청이 이미 보류 중이면 새 요청 생성을 건너뜁니다.

검증 프로토콜/시스템 알림은 에이전트 채팅 파이프라인으로 전달되지 않으므로 `NO_REPLY`를 생성하지 않습니다.

### device 위생

오래된 OpenClaw 관리 Matrix device가 계정에 누적되면 암호화된 room의 신뢰 상태를 파악하기 어려워질 수 있습니다.
다음 명령으로 목록을 확인하세요:

```bash
openclaw matrix devices list
```

오래된 OpenClaw 관리 device는 다음 명령으로 제거하세요:

```bash
openclaw matrix devices prune-stale
```

### Direct Room 복구

direct-message 상태가 어긋나면 OpenClaw는 오래된 단일 room을 가리키는 stale `m.direct` 매핑을 가지게 될 수 있습니다. 피어의 현재 매핑을 확인하려면 다음을 사용하세요:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

다음으로 복구할 수 있습니다:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

복구는 Matrix 전용 로직을 plugin 내부에 유지합니다:

- 먼저 `m.direct`에 이미 매핑된 엄격한 1:1 DM을 우선 사용
- 그렇지 않으면 해당 사용자와 현재 참가 중인 엄격한 1:1 DM으로 대체
- 정상적인 DM이 없으면 새 direct room을 생성하고 `m.direct`를 다시 써서 그것을 가리키게 함

복구 흐름은 오래된 room을 자동 삭제하지 않습니다. 정상적인 DM을 선택하고 매핑만 업데이트하여 이후 Matrix 전송, 검증 알림 및 기타 direct-message 흐름이 다시 올바른 room을 대상으로 하게 합니다.

## Threads

Matrix는 자동 답장과 message-tool 전송 모두에 대해 기본 Matrix thread를 지원합니다.

- `threadReplies: "off"`는 답장을 최상위 수준으로 유지하고 수신 thread 메시지를 부모 세션에 유지합니다.
- `threadReplies: "inbound"`는 수신 메시지가 이미 해당 thread에 있을 때만 thread 내부에서 답장합니다.
- `threadReplies: "always"`는 room 답장을 트리거 메시지를 루트로 하는 thread에 유지하고, 첫 트리거 메시지부터 일치하는 thread 범위 세션을 통해 해당 대화를 라우팅합니다.
- `dm.threadReplies`는 DM에 대해서만 최상위 설정을 재정의합니다. 예를 들어 room thread는 분리하면서 DM은 평면으로 유지할 수 있습니다.
- 수신 thread 메시지에는 추가 에이전트 컨텍스트로 thread 루트 메시지가 포함됩니다.
- 이제 message-tool 전송은 대상이 같은 room이거나 같은 DM 사용자 대상인 경우, 명시적인 `threadId`가 제공되지 않으면 현재 Matrix thread를 자동 상속합니다.
- Matrix는 런타임 thread 바인딩을 지원합니다. 이제 `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`, thread에 바인딩된 `/acp spawn`이 Matrix room과 DM에서 작동합니다.
- `threadBindings.spawnSubagentSessions=true`일 때 최상위 Matrix room/DM의 `/focus`는 새 Matrix thread를 만들고 이를 대상 세션에 바인딩합니다.
- 기존 Matrix thread 안에서 `/focus` 또는 `/acp spawn --thread here`를 실행하면 현재 thread가 대신 바인딩됩니다.

## ACP 대화 바인딩

Matrix room, DM, 기존 Matrix thread는 채팅 표면을 바꾸지 않고도 영속적인 ACP 워크스페이스로 전환할 수 있습니다.

빠른 운영자 흐름:

- 계속 사용할 Matrix DM, room 또는 기존 thread 안에서 `/acp spawn codex --bind here`를 실행합니다.
- 최상위 Matrix DM 또는 room에서는 현재 DM/room이 채팅 표면으로 유지되고 이후 메시지는 생성된 ACP 세션으로 라우팅됩니다.
- 기존 Matrix thread 안에서는 `--bind here`가 현재 thread를 제자리에서 바인딩합니다.
- `/new`와 `/reset`은 동일한 바인딩된 ACP 세션을 제자리에서 재설정합니다.
- `/acp close`는 ACP 세션을 닫고 바인딩을 제거합니다.

참고:

- `--bind here`는 하위 Matrix thread를 생성하지 않습니다.
- `threadBindings.spawnAcpSessions`는 OpenClaw가 하위 Matrix thread를 만들거나 바인딩해야 하는 `/acp spawn --thread auto|here`에만 필요합니다.

### Thread 바인딩 구성

Matrix는 `session.threadBindings`의 전역 기본값을 상속하며, 채널별 재정의도 지원합니다:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrix thread 바인딩된 spawn 플래그는 opt-in입니다:

- 최상위 `/focus`가 새 Matrix thread를 만들고 바인딩하도록 허용하려면 `threadBindings.spawnSubagentSessions: true`를 설정하세요.
- `/acp spawn --thread auto|here`가 ACP 세션을 Matrix thread에 바인딩하도록 허용하려면 `threadBindings.spawnAcpSessions: true`를 설정하세요.

## Reactions

Matrix는 발신 reaction 작업, 수신 reaction 알림, 수신 ack reaction을 지원합니다.

- 발신 reaction tooling은 `channels["matrix"].actions.reactions`로 게이트됩니다.
- `react`는 특정 Matrix 이벤트에 reaction을 추가합니다.
- `reactions`는 특정 Matrix 이벤트의 현재 reaction 요약을 나열합니다.
- `emoji=""`는 해당 이벤트에 대한 봇 계정 자신의 reaction을 제거합니다.
- `remove: true`는 봇 계정의 지정된 이모지 reaction만 제거합니다.

ack reaction은 표준 OpenClaw 해석 순서를 사용합니다:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- 에이전트 ID 이모지 대체값

ack reaction 범위는 다음 순서로 해석됩니다:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

reaction 알림 모드는 다음 순서로 해석됩니다:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- 기본값: `own`

현재 동작:

- `reactionNotifications: "own"`은 봇이 작성한 Matrix 메시지를 대상으로 하는 추가된 `m.reaction` 이벤트를 전달합니다.
- `reactionNotifications: "off"`는 reaction 시스템 이벤트를 비활성화합니다.
- Matrix는 제거를 독립적인 `m.reaction` 제거가 아니라 redaction으로 표시하므로, reaction 제거는 아직 시스템 이벤트로 합성되지 않습니다.

## 기록 컨텍스트

- `channels.matrix.historyLimit`는 Matrix room 메시지가 에이전트를 트리거할 때 `InboundHistory`로 포함할 최근 room 메시지 수를 제어합니다.
- 기본값은 `messages.groupChat.historyLimit`를 따릅니다. 비활성화하려면 `0`으로 설정하세요.
- Matrix room 기록은 room 전용입니다. DM은 계속 일반 세션 기록을 사용합니다.
- Matrix room 기록은 pending-only입니다. OpenClaw는 아직 답장을 트리거하지 않은 room 메시지를 버퍼링한 뒤, 멘션이나 다른 트리거가 들어오면 그 구간을 스냅샷으로 저장합니다.
- 현재 트리거 메시지는 `InboundHistory`에 포함되지 않으며, 해당 턴의 메인 수신 본문에 남아 있습니다.
- 동일한 Matrix 이벤트를 재시도할 때는 새 room 메시지로 앞으로 이동하지 않고 원래 기록 스냅샷을 재사용합니다.

## 컨텍스트 가시성

Matrix는 가져온 답장 텍스트, thread 루트, pending history 같은 보조 room 컨텍스트에 대해 공통 `contextVisibility` 제어를 지원합니다.

- `contextVisibility: "all"`이 기본값입니다. 보조 컨텍스트는 받은 그대로 유지됩니다.
- `contextVisibility: "allowlist"`는 활성 room/user 허용 목록 검사에서 허용된 발신자만 보조 컨텍스트에 남깁니다.
- `contextVisibility: "allowlist_quote"`는 `allowlist`처럼 동작하지만, 명시적으로 인용된 답장 하나는 계속 유지합니다.

이 설정은 보조 컨텍스트의 가시성에 영향을 주며, 수신 메시지 자체가 답장을 트리거할 수 있는지 여부에는 영향을 주지 않습니다.
트리거 권한은 계속 `groupPolicy`, `groups`, `groupAllowFrom`, DM 정책 설정에서 결정됩니다.

## DM 및 room 정책 예시

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

멘션 게이팅 및 허용 목록 동작은 [Groups](/channels/groups)를 참조하세요.

Matrix DM용 페어링 예시:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

승인 전의 Matrix 사용자가 계속 메시지를 보내면, OpenClaw는 동일한 보류 중 페어링 코드를 재사용하며 새 코드를 발급하는 대신 짧은 쿨다운 후 다시 리마인더 답장을 보낼 수 있습니다.

공통 DM 페어링 흐름 및 저장소 레이아웃은 [페어링](/channels/pairing)을 참조하세요.

## Exec 승인

Matrix는 Matrix 계정의 exec 승인 클라이언트로 동작할 수 있습니다.

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (선택 사항; 기본값은 `channels.matrix.dm.allowFrom`)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, 기본값: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

승인자는 `@owner:example.org` 같은 Matrix user ID여야 합니다. `enabled`가 설정되지 않았거나 `"auto"`이고 `execApprovals.approvers` 또는 `channels.matrix.dm.allowFrom`에서 하나 이상의 승인자를 해석할 수 있으면 Matrix는 기본 exec 승인을 자동 활성화합니다. Matrix를 기본 승인 클라이언트로 명시적으로 비활성화하려면 `enabled: false`로 설정하세요. 그렇지 않으면 승인 요청은 다른 구성된 승인 경로나 exec 승인 대체 정책으로 넘어갑니다.

현재 Matrix 기본 라우팅은 exec 전용입니다:

- `channels.matrix.execApprovals.*`는 exec 승인에 대해서만 기본 DM/채널 라우팅을 제어합니다.
- plugin 승인은 계속 공통 same-chat `/approve`와 구성된 `approvals.plugin` 전달을 사용합니다.
- Matrix는 승인자를 안전하게 추론할 수 있을 때 plugin 승인 권한 부여를 위해 `channels.matrix.dm.allowFrom`을 재사용할 수 있지만, 별도의 기본 plugin 승인 DM/채널 fanout 경로를 제공하지는 않습니다.

전달 규칙:

- `target: "dm"`은 승인 프롬프트를 승인자 DM으로 보냅니다
- `target: "channel"`은 프롬프트를 원래 Matrix room 또는 DM으로 다시 보냅니다
- `target: "both"`는 승인자 DM과 원래 Matrix room 또는 DM 모두로 보냅니다

현재 Matrix는 텍스트 승인 프롬프트를 사용합니다. 승인자는 `/approve <id> allow-once`, `/approve <id> allow-always`, 또는 `/approve <id> deny`로 이를 처리합니다.

해석된 승인자만 승인 또는 거부할 수 있습니다. 채널 전달에는 명령 텍스트가 포함되므로 신뢰할 수 있는 room에서만 `channel` 또는 `both`를 활성화하세요.

Matrix 승인 프롬프트는 공통 코어 승인 planner를 재사용합니다. Matrix 전용 기본 표면은 exec 승인에 대해서만 전송 계층 역할을 합니다: room/DM 라우팅 및 메시지 전송/업데이트/삭제 동작.

계정별 재정의:

- `channels.matrix.accounts.<account>.execApprovals`

관련 문서: [Exec approvals](/tools/exec-approvals)

## 다중 계정 예시

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

최상위 `channels.matrix` 값은 계정이 재정의하지 않는 한 이름 있는 계정의 기본값으로 동작합니다.
상속된 room 항목을 특정 Matrix 계정 하나로 제한하려면 `groups.<room>.account`(또는 레거시 `rooms.<room>.account`)를 사용할 수 있습니다.
`account`가 없는 항목은 모든 Matrix 계정에 공통으로 유지되며, 기본 계정이 최상위 `channels.matrix.*`에 직접 구성된 경우 `account: "default"` 항목도 계속 작동합니다.
부분적인 공통 인증 기본값만으로는 별도의 암묵적 기본 계정이 생성되지 않습니다. OpenClaw는 해당 기본 계정에 새로운 인증(`homeserver` + `accessToken`, 또는 `homeserver` + `userId` + `password`)이 있을 때만 최상위 `default` 계정을 합성합니다. 이름 있는 계정은 이후 캐시된 자격 증명으로 인증을 만족할 수 있다면 `homeserver` + `userId`만으로도 계속 검색 가능할 수 있습니다.
Matrix에 이미 정확히 하나의 이름 있는 계정이 있거나 `defaultAccount`가 기존 이름 있는 계정 키를 가리키는 경우, 단일 계정에서 다중 계정으로의 복구/설정 승격은 새 `accounts.default` 항목을 만드는 대신 해당 계정을 보존합니다. Matrix 인증/bootstrap 키만 해당 승격된 계정으로 이동하며, 공통 전달 정책 키는 최상위에 남습니다.
암묵적 라우팅, 프로브, CLI 작업에 대해 OpenClaw가 특정 이름 있는 Matrix 계정을 우선 사용하도록 하려면 `defaultAccount`를 설정하세요.
여러 이름 있는 계정을 구성하는 경우, 암묵적 계정 선택에 의존하는 CLI 명령에 대해 `defaultAccount`를 설정하거나 `--account <id>`를 전달하세요.
한 명령에 대해 이 암묵적 선택을 재정의하려면 `openclaw matrix verify ...` 및 `openclaw matrix devices ...`에 `--account <id>`를 전달하세요.

## 비공개/LAN homeserver

기본적으로 OpenClaw는 SSRF 보호를 위해 private/internal Matrix homeserver를 차단하며,
계정별로 명시적으로 opt-in해야만 허용합니다.

homeserver가 localhost, LAN/Tailscale IP 또는 내부 호스트 이름에서 실행되는 경우,
해당 Matrix 계정에 대해 `allowPrivateNetwork`를 활성화하세요:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      allowPrivateNetwork: true,
      accessToken: "syt_internal_xxx",
    },
  },
}
```

CLI 설정 예시:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

이 opt-in은 신뢰된 private/internal 대상만 허용합니다. `http://matrix.example.org:8008` 같은
공개 평문 homeserver는 계속 차단됩니다. 가능하면 `https://`를 권장합니다.

## Matrix 트래픽 프록시

Matrix 배포에 명시적인 아웃바운드 HTTP(S) 프록시가 필요하면 `channels.matrix.proxy`를 설정하세요:

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

이름 있는 계정은 `channels.matrix.accounts.<id>.proxy`로 최상위 기본값을 재정의할 수 있습니다.
OpenClaw는 런타임 Matrix 트래픽과 계정 상태 프로브 모두에 동일한 프록시 설정을 사용합니다.

## 대상 해석

Matrix는 OpenClaw가 room 또는 user 대상을 요청하는 모든 위치에서 다음 대상 형식을 허용합니다:

- 사용자: `@user:server`, `user:@user:server`, 또는 `matrix:user:@user:server`
- Room: `!room:server`, `room:!room:server`, 또는 `matrix:room:!room:server`
- Alias: `#alias:server`, `channel:#alias:server`, 또는 `matrix:channel:#alias:server`

실시간 디렉터리 조회는 로그인된 Matrix 계정을 사용합니다:

- 사용자 조회는 해당 homeserver의 Matrix 사용자 디렉터리를 조회합니다.
- Room 조회는 명시적인 room ID와 alias를 직접 받고, 이후 해당 계정의 참가 중인 room 이름 검색으로 대체합니다.
- 참가 중 room 이름 조회는 best-effort입니다. room 이름을 ID나 alias로 해석할 수 없으면 런타임 허용 목록 해석에서 무시됩니다.

## 구성 참조

- `enabled`: 채널 활성화 또는 비활성화.
- `name`: 계정의 선택적 레이블.
- `defaultAccount`: 여러 Matrix 계정이 구성된 경우 선호되는 account ID.
- `homeserver`: homeserver URL(예: `https://matrix.example.org`).
- `allowPrivateNetwork`: 이 Matrix 계정이 private/internal homeserver에 연결되도록 허용합니다. homeserver가 `localhost`, LAN/Tailscale IP 또는 `matrix-synapse` 같은 내부 호스트로 해석되는 경우 활성화하세요.
- `proxy`: Matrix 트래픽용 선택적 HTTP(S) 프록시 URL. 이름 있는 계정은 자체 `proxy`로 최상위 기본값을 재정의할 수 있습니다.
- `userId`: 전체 Matrix user ID(예: `@bot:example.org`).
- `accessToken`: 토큰 기반 인증용 액세스 토큰. 일반 텍스트 값과 SecretRef 값은 env/file/exec provider 전반에서 `channels.matrix.accessToken`과 `channels.matrix.accounts.<id>.accessToken`에 지원됩니다. [Secrets Management](/gateway/secrets)를 참조하세요.
- `password`: 비밀번호 기반 로그인용 비밀번호. 일반 텍스트 값과 SecretRef 값이 지원됩니다.
- `deviceId`: 명시적 Matrix device ID.
- `deviceName`: 비밀번호 로그인용 device 표시 이름.
- `avatarUrl`: 프로필 동기화 및 `set-profile` 업데이트용으로 저장된 self-avatar URL.
- `initialSyncLimit`: 시작 시 sync 이벤트 제한.
- `encryption`: E2EE 활성화.
- `allowlistOnly`: DM과 room에 대해 허용 목록 전용 동작 강제.
- `allowBots`: 다른 구성된 OpenClaw Matrix 계정의 메시지를 허용(`true` 또는 `"mentions"`).
- `groupPolicy`: `open`, `allowlist`, 또는 `disabled`.
- `contextVisibility`: 보조 room 컨텍스트 가시성 모드(`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: room 트래픽용 user ID 허용 목록.
- `groupAllowFrom` 항목은 전체 Matrix user ID여야 합니다. 해석되지 않은 이름은 런타임에 무시됩니다.
- `historyLimit`: 그룹 기록 컨텍스트로 포함할 최대 room 메시지 수. 기본값은 `messages.groupChat.historyLimit`를 따릅니다. 비활성화하려면 `0`으로 설정하세요.
- `replyToMode`: `off`, `first`, 또는 `all`.
- `markdown`: 발신 Matrix 텍스트용 선택적 Markdown 렌더링 구성.
- `streaming`: `off`(기본값), `partial`, `true`, 또는 `false`. `partial`과 `true`는 제자리 수정 업데이트가 가능한 단일 메시지 초안 미리보기를 활성화합니다.
- `blockStreaming`: `true`는 초안 미리보기 스트리밍이 활성화된 동안 완료된 assistant 블록에 대해 별도 진행 메시지를 활성화합니다.
- `threadReplies`: `off`, `inbound`, 또는 `always`.
- `threadBindings`: thread 바인딩 세션 라우팅 및 수명 주기에 대한 채널별 재정의.
- `startupVerification`: 시작 시 자동 self-verification 요청 모드(`if-unverified`, `off`).
- `startupVerificationCooldownHours`: 자동 시작 검증 요청을 재시도하기 전 대기 시간.
- `textChunkLimit`: 발신 메시지 청크 크기.
- `chunkMode`: `length` 또는 `newline`.
- `responsePrefix`: 발신 답장용 선택적 메시지 접두사.
- `ackReaction`: 이 채널/계정용 선택적 ack reaction 재정의.
- `ackReactionScope`: 선택적 ack reaction 범위 재정의(`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: 수신 reaction 알림 모드(`own`, `off`).
- `mediaMaxMb`: Matrix 미디어 처리용 미디어 크기 제한(MB). 발신 전송 및 수신 미디어 처리 모두에 적용됩니다.
- `autoJoin`: 초대 자동 참가 정책(`always`, `allowlist`, `off`). 기본값: `off`.
- `autoJoinAllowlist`: `autoJoin`이 `allowlist`일 때 허용되는 room/alias. alias 항목은 초대 처리 중 room ID로 해석되며, OpenClaw는 초대된 room이 주장하는 alias 상태를 신뢰하지 않습니다.
- `dm`: DM 정책 블록(`enabled`, `policy`, `allowFrom`, `threadReplies`).
- `dm.allowFrom` 항목은 실시간 디렉터리 조회로 이미 해석한 경우가 아니면 전체 Matrix user ID여야 합니다.
- `dm.threadReplies`: DM 전용 thread 정책 재정의(`off`, `inbound`, `always`). DM에서 답장 배치와 세션 분리 모두에 대해 최상위 `threadReplies` 설정을 재정의합니다.
- `execApprovals`: Matrix 기본 exec 승인 전달(`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: exec 요청을 승인할 수 있는 Matrix user ID. `dm.allowFrom`이 이미 승인자를 식별하는 경우 선택 사항입니다.
- `execApprovals.target`: `dm | channel | both` (기본값: `dm`).
- `accounts`: 이름 있는 계정별 재정의. 최상위 `channels.matrix` 값이 이 항목의 기본값으로 동작합니다.
- `groups`: room별 정책 맵. room ID 또는 alias를 권장하며, 해석되지 않은 room 이름은 런타임에 무시됩니다. 세션/그룹 ID는 해석 후 안정적인 room ID를 사용하고, 사람이 읽는 레이블은 계속 room 이름에서 가져옵니다.
- `groups.<room>.account`: 다중 계정 설정에서 상속된 room 항목 하나를 특정 Matrix 계정으로 제한.
- `groups.<room>.allowBots`: 구성된 봇 발신자에 대한 room 수준 재정의(`true` 또는 `"mentions"`).
- `groups.<room>.users`: room별 발신자 허용 목록.
- `groups.<room>.tools`: room별 도구 허용/거부 재정의.
- `groups.<room>.autoReply`: room 수준 멘션 게이팅 재정의. `true`는 해당 room의 멘션 요구 사항을 비활성화하고, `false`는 다시 강제합니다.
- `groups.<room>.skills`: 선택적 room 수준 Skills 필터.
- `groups.<room>.systemPrompt`: 선택적 room 수준 시스템 프롬프트 스니펫.
- `rooms`: `groups`의 레거시 별칭.
- `actions`: 작업별 도구 게이팅(`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## 관련

- [채널 개요](/channels) — 지원되는 모든 채널
- [페어링](/channels/pairing) — DM 인증 및 페어링 흐름
- [그룹](/channels/groups) — 그룹 채팅 동작 및 멘션 게이팅
- [채널 라우팅](/channels/channel-routing) — 메시지용 세션 라우팅
- [보안](/gateway/security) — 접근 모델 및 보안 강화
