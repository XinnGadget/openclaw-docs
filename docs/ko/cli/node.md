---
read_when:
    - 헤드리스 노드 호스트를 실행할 때
    - system.run용 비 macOS 노드를 페어링할 때
summary: '`openclaw node`용 CLI 참조(헤드리스 노드 호스트)'
title: node
x-i18n:
    generated_at: "2026-04-05T12:38:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6123b33ec46f2b85f2c815947435ac91bbe84456165ff0e504453356da55b46d
    source_path: cli/node.md
    workflow: 15
---

# `openclaw node`

Gateway WebSocket에 연결하고 이 머신에서
`system.run` / `system.which`를 노출하는 **헤드리스 노드 호스트**를 실행합니다.

## 왜 노드 호스트를 사용하나요?

네트워크의 다른 머신에서 **전체 macOS 컴패니언 앱을 설치하지 않고도**
에이전트가 **명령을 실행**하게 하려면 노드 호스트를 사용하세요.

일반적인 사용 사례:

- 원격 Linux/Windows 머신(빌드 서버, 실험실 머신, NAS)에서 명령 실행
- exec는 gateway에서 **샌드박싱된 상태**로 유지하면서, 승인된 실행은 다른 호스트에 위임
- 자동화 또는 CI 노드용 경량 헤드리스 실행 대상 제공

실행은 여전히 노드 호스트의 **exec 승인** 및 에이전트별 허용 목록으로 보호되므로,
명령 액세스 범위를 명확하고 제한적으로 유지할 수 있습니다.

## 브라우저 프록시(무구성)

노드에서 `browser.enabled`가 비활성화되지 않은 경우 노드 호스트는 자동으로 브라우저 프록시를 광고합니다. 이를 통해 추가 구성 없이 에이전트가 해당 노드에서 브라우저 자동화를 사용할 수 있습니다.

기본적으로 프록시는 노드의 일반 브라우저 프로필 표면을 노출합니다. `nodeHost.browserProxy.allowProfiles`를 설정하면 프록시는 제한적으로 동작합니다. 허용 목록에 없는 프로필 대상 지정은 거부되며, 영구 프로필 생성/삭제 라우트는 프록시를 통해 차단됩니다.

필요하면 노드에서 비활성화하세요.

```json5
{
  nodeHost: {
    browserProxy: {
      enabled: false,
    },
  },
}
```

## 실행(포그라운드)

```bash
openclaw node run --host <gateway-host> --port 18789
```

옵션:

- `--host <host>`: Gateway WebSocket 호스트(기본값: `127.0.0.1`)
- `--port <port>`: Gateway WebSocket 포트(기본값: `18789`)
- `--tls`: gateway 연결에 TLS 사용
- `--tls-fingerprint <sha256>`: 예상 TLS 인증서 지문(sha256)
- `--node-id <id>`: 노드 ID 재정의(페어링 토큰 지움)
- `--display-name <name>`: 노드 표시 이름 재정의

## 노드 호스트용 Gateway 인증

`openclaw node run` 및 `openclaw node install`은 config/env에서 gateway 인증을 해석합니다(노드 명령에는 `--token`/`--password` 플래그 없음).

- 먼저 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`를 확인합니다.
- 그다음 로컬 config 폴백: `gateway.auth.token` / `gateway.auth.password`.
- 로컬 모드에서 노드 호스트는 의도적으로 `gateway.remote.token` / `gateway.remote.password`를 상속하지 않습니다.
- `gateway.auth.token` / `gateway.auth.password`가 SecretRef를 통해 명시적으로 구성되었지만 해석되지 않으면, 노드 인증 해석은 fail closed로 동작합니다(원격 폴백에 의해 가려지지 않음).
- `gateway.mode=remote`에서는 원격 우선순위 규칙에 따라 원격 클라이언트 필드(`gateway.remote.token` / `gateway.remote.password`)도 사용할 수 있습니다.
- 노드 호스트 인증 해석은 `OPENCLAW_GATEWAY_*` 환경 변수만 존중합니다.

## 서비스(백그라운드)

헤드리스 노드 호스트를 사용자 서비스로 설치합니다.

```bash
openclaw node install --host <gateway-host> --port 18789
```

옵션:

- `--host <host>`: Gateway WebSocket 호스트(기본값: `127.0.0.1`)
- `--port <port>`: Gateway WebSocket 포트(기본값: `18789`)
- `--tls`: gateway 연결에 TLS 사용
- `--tls-fingerprint <sha256>`: 예상 TLS 인증서 지문(sha256)
- `--node-id <id>`: 노드 ID 재정의(페어링 토큰 지움)
- `--display-name <name>`: 노드 표시 이름 재정의
- `--runtime <runtime>`: 서비스 런타임(`node` 또는 `bun`)
- `--force`: 이미 설치된 경우 재설치/덮어쓰기

서비스 관리:

```bash
openclaw node status
openclaw node stop
openclaw node restart
openclaw node uninstall
```

포그라운드 노드 호스트(서비스 없음)에는 `openclaw node run`을 사용하세요.

서비스 명령은 기계 판독 가능한 출력을 위해 `--json`을 지원합니다.

## 페어링

첫 번째 연결은 Gateway에 보류 중인 디바이스 페어링 요청(`role: node`)을 생성합니다.
다음으로 승인하세요.

```bash
openclaw devices list
openclaw devices approve <requestId>
```

노드가 변경된 인증 세부 정보(role/scopes/public key)로 페어링을 다시 시도하면,
이전 보류 요청은 대체되고 새 `requestId`가 생성됩니다.
승인 전에 `openclaw devices list`를 다시 실행하세요.

노드 호스트는 노드 ID, 토큰, 표시 이름, gateway 연결 정보를
`~/.openclaw/node.json`에 저장합니다.

## Exec 승인

`system.run`은 로컬 exec 승인에 의해 제어됩니다.

- `~/.openclaw/exec-approvals.json`
- [Exec 승인](/tools/exec-approvals)
- `openclaw approvals --node <id|name|ip>` (Gateway에서 편집)

승인된 비동기 노드 exec의 경우, OpenClaw는 프롬프트 전에 정규 `systemRunPlan`을 준비합니다.
이후 승인된 `system.run` 전달은 저장된 해당
plan을 재사용하므로, 승인 요청이 생성된 뒤 명령/cwd/세션 필드를 편집해도
노드가 실행하는 내용이 바뀌는 대신 거부됩니다.
