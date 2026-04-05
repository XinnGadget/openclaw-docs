---
read_when:
    - macOS UI 없이 노드 페어링 승인을 구현하는 경우
    - 원격 노드 승인을 위한 CLI 흐름을 추가하는 경우
    - 노드 관리를 위해 gateway 프로토콜을 확장하는 경우
summary: iOS 및 기타 원격 노드를 위한 Gateway 소유 노드 페어링(옵션 B)
title: Gateway 소유 페어링
x-i18n:
    generated_at: "2026-04-05T12:43:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8f90818c84daeb190f27df7413e23362372806f2c4250e4954295fbf6df70233
    source_path: gateway/pairing.md
    workflow: 15
---

# Gateway 소유 페어링(옵션 B)

Gateway 소유 페어링에서는 어떤 노드가 참여할 수 있는지에 대한 단일 기준이 **Gateway**입니다. UI(macOS 앱, 향후 클라이언트)는 단지 대기 중인 요청을 승인하거나 거부하는 프런트엔드일 뿐입니다.

**중요:** WS 노드는 `connect` 중에 **장치 페어링**(role `node`)을 사용합니다.
`node.pair.*`는 별도의 페어링 저장소이며 WS 핸드셰이크를 제어하지 **않습니다**.
명시적으로 `node.pair.*`를 호출하는 클라이언트만 이 흐름을 사용합니다.

## 개념

- **대기 중인 요청**: 노드가 참여를 요청한 상태이며 승인이 필요합니다.
- **페어링된 노드**: 인증 토큰이 발급된 승인된 노드입니다.
- **전송 계층**: Gateway WS 엔드포인트는 요청을 전달하지만 멤버십은 결정하지 않습니다. (레거시 TCP bridge 지원은 제거되었습니다.)

## 페어링 작동 방식

1. 노드가 Gateway WS에 연결하고 페어링을 요청합니다.
2. Gateway가 **대기 중인 요청**을 저장하고 `node.pair.requested`를 발생시킵니다.
3. 요청을 승인하거나 거부합니다(CLI 또는 UI).
4. 승인되면 Gateway는 **새 토큰**을 발급합니다(재페어링 시 토큰은 교체됨).
5. 노드는 해당 토큰으로 다시 연결하며 이제 “페어링됨” 상태가 됩니다.

대기 중인 요청은 **5분** 후 자동으로 만료됩니다.

## CLI 워크플로(headless 친화적)

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes reject <requestId>
openclaw nodes status
openclaw nodes rename --node <id|name|ip> --name "Living Room iPad"
```

`nodes status`는 페어링된/연결된 노드와 그 기능을 표시합니다.

## API 표면(gateway 프로토콜)

이벤트:

- `node.pair.requested` — 새 대기 요청이 생성될 때 발생합니다.
- `node.pair.resolved` — 요청이 승인/거부/만료될 때 발생합니다.

메서드:

- `node.pair.request` — 대기 요청을 생성하거나 재사용합니다.
- `node.pair.list` — 대기 중인 노드 + 페어링된 노드를 나열합니다(`operator.pairing`).
- `node.pair.approve` — 대기 요청을 승인합니다(토큰 발급).
- `node.pair.reject` — 대기 요청을 거부합니다.
- `node.pair.verify` — `{ nodeId, token }`을 검증합니다.

참고:

- `node.pair.request`는 노드별로 멱등적입니다. 반복 호출은 동일한 대기 요청을 반환합니다.
- 동일한 대기 노드에 대한 반복 요청은 저장된 노드 메타데이터와 운영자 가시성을 위한 최신 allowlist 선언 명령 스냅샷도 갱신합니다.
- 승인 시에는 **항상** 새 토큰이 생성되며, `node.pair.request`에서는 토큰이 절대 반환되지 않습니다.
- 요청은 자동 승인 흐름을 위한 힌트로 `silent: true`를 포함할 수 있습니다.
- `node.pair.approve`는 추가 승인 범위를 강제하기 위해 대기 요청의 선언된 명령을 사용합니다:
  - 명령 없는 요청: `operator.pairing`
  - 비-exec 명령 요청: `operator.pairing` + `operator.write`
  - `system.run` / `system.run.prepare` / `system.which` 요청:
    `operator.pairing` + `operator.admin`

중요:

- 노드 페어링은 신뢰/정체성 흐름과 토큰 발급입니다.
- 이것이 노드별 실시간 노드 명령 표면을 고정하지는 **않습니다**.
- 실시간 노드 명령은 gateway의 전역 노드 명령 정책(`gateway.nodes.allowCommands` / `denyCommands`)이 적용된 후 노드가 연결 시 선언하는 내용에서 결정됩니다.
- 노드별 `system.run` allow/ask 정책은 페어링 기록이 아니라 노드의 `exec.approvals.node.*`에 있습니다.

## 노드 명령 게이팅(2026.3.31+)

<Warning>
**호환성 깨짐 변경:** `2026.3.31`부터 노드 페어링이 승인될 때까지 노드 명령은 비활성화됩니다. 장치 페어링만으로는 더 이상 선언된 노드 명령이 노출되지 않습니다.
</Warning>

노드가 처음 연결되면 페어링이 자동으로 요청됩니다. 페어링 요청이 승인될 때까지 해당 노드의 모든 대기 중 노드 명령은 필터링되며 실행되지 않습니다. 페어링 승인을 통해 신뢰가 확립되면 노드가 선언한 명령은 일반 명령 정책의 적용을 받으며 사용 가능해집니다.

이는 다음을 의미합니다:

- 이전에 장치 페어링만으로 명령을 노출하던 노드는 이제 노드 페어링을 완료해야 합니다.
- 페어링 승인 전에 큐에 들어간 명령은 지연되지 않고 폐기됩니다.

## 노드 이벤트 신뢰 경계(2026.3.31+)

<Warning>
**호환성 깨짐 변경:** 노드에서 시작된 실행은 이제 축소된 신뢰 표면에 머뭅니다.
</Warning>

노드에서 시작된 요약과 관련 세션 이벤트는 의도된 신뢰 표면으로 제한됩니다. 이전에 더 넓은 호스트 또는 세션 도구 액세스에 의존하던 알림 기반 또는 노드 트리거 흐름은 조정이 필요할 수 있습니다. 이 강화는 노드 이벤트가 노드의 신뢰 경계가 허용하는 범위를 넘어 호스트 수준 도구 액세스로 권한 상승할 수 없도록 보장합니다.

## 자동 승인(macOS 앱)

macOS 앱은 다음 조건일 때 선택적으로 **자동 승인**을 시도할 수 있습니다:

- 요청이 `silent`로 표시되어 있고,
- 앱이 동일한 사용자로 gateway 호스트에 대한 SSH 연결을 검증할 수 있는 경우.

자동 승인이 실패하면 일반적인 “승인/거부” 프롬프트로 대체됩니다.

## 저장소(로컬, 비공개)

페어링 상태는 Gateway 상태 디렉터리 아래에 저장됩니다(기본값 `~/.openclaw`):

- `~/.openclaw/nodes/paired.json`
- `~/.openclaw/nodes/pending.json`

`OPENCLAW_STATE_DIR`를 재정의하면 `nodes/` 폴더도 함께 이동합니다.

보안 참고:

- 토큰은 비밀 정보이므로 `paired.json`을 민감한 파일로 취급하세요.
- 토큰 교체에는 재승인(또는 노드 항목 삭제)이 필요합니다.

## 전송 계층 동작

- 전송 계층은 **상태 비저장**이며 멤버십을 저장하지 않습니다.
- Gateway가 오프라인이거나 페어링이 비활성화되어 있으면 노드는 페어링할 수 없습니다.
- Gateway가 원격 모드에 있어도 페어링은 여전히 원격 Gateway의 저장소를 기준으로 수행됩니다.
