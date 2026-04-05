---
read_when:
    - 전체 agent 턴을 실행하지 않고 도구를 호출할 때
    - 도구 정책 강제가 필요한 자동화를 구축할 때
summary: Gateway HTTP 엔드포인트를 통해 단일 도구를 직접 호출합니다
title: Tools Invoke API
x-i18n:
    generated_at: "2026-04-05T12:44:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: e924f257ba50b25dea0ec4c3f9eed4c8cac8a53ddef18215f87ac7de330a37fd
    source_path: gateway/tools-invoke-http-api.md
    workflow: 15
---

# Tools Invoke (HTTP)

OpenClaw의 Gateway는 단일 도구를 직접 호출하기 위한 간단한 HTTP 엔드포인트를 노출합니다. 이 엔드포인트는 항상 활성화되어 있으며 Gateway 인증과 도구 정책을 사용합니다. OpenAI 호환 `/v1/*` 표면과 마찬가지로, 공유 비밀 bearer 인증은 전체 gateway에 대한 신뢰된 운영자 액세스로 취급됩니다.

- `POST /tools/invoke`
- Gateway와 같은 포트 사용(WS + HTTP 멀티플렉스): `http://<gateway-host>:<port>/tools/invoke`

기본 최대 페이로드 크기는 2 MB입니다.

## 인증

Gateway 인증 구성을 사용합니다.

일반적인 HTTP 인증 경로:

- 공유 비밀 인증(`gateway.auth.mode="token"` 또는 `"password"`):
  `Authorization: Bearer <token-or-password>`
- 신뢰된 ID 포함 HTTP 인증(`gateway.auth.mode="trusted-proxy"`):
  구성된 ID 인식 프록시를 통해 라우팅하고, 해당 프록시가 필요한 ID 헤더를 주입하도록 합니다
- 비공개 인그레스 오픈 인증(`gateway.auth.mode="none"`):
  인증 헤더가 필요하지 않음

참고:

- `gateway.auth.mode="token"`일 때는 `gateway.auth.token`(또는 `OPENCLAW_GATEWAY_TOKEN`)을 사용하세요.
- `gateway.auth.mode="password"`일 때는 `gateway.auth.password`(또는 `OPENCLAW_GATEWAY_PASSWORD`)를 사용하세요.
- `gateway.auth.mode="trusted-proxy"`일 때는 HTTP 요청이 구성된 non-loopback 신뢰 프록시 소스에서 와야 합니다. 동일 호스트의 loopback 프록시는 이 모드를 충족하지 않습니다.
- `gateway.auth.rateLimit`이 구성되어 있고 인증 실패가 너무 많이 발생하면 엔드포인트는 `Retry-After`와 함께 `429`를 반환합니다.

## 보안 경계(중요)

이 엔드포인트는 해당 gateway 인스턴스에 대한 **전체 운영자 액세스** 표면으로 취급하세요.

- 여기의 HTTP bearer 인증은 좁은 범위의 사용자별 스코프 모델이 아닙니다.
- 이 엔드포인트에 대한 유효한 Gateway token/password는 소유자/운영자 자격 증명처럼 취급해야 합니다.
- 공유 비밀 인증 모드(`token`, `password`)에서는 호출자가 더 좁은 `x-openclaw-scopes` 헤더를 보내더라도 엔드포인트가 정상적인 전체 운영자 기본값을 복원합니다.
- 공유 비밀 인증은 또한 이 엔드포인트에서의 직접 도구 호출을 owner-sender 턴으로 취급합니다.
- 신뢰된 ID 포함 HTTP 모드(예: trusted proxy 인증 또는 비공개 인그레스의 `gateway.auth.mode="none"`)는 `x-openclaw-scopes`가 있으면 이를 따르고, 없으면 정상적인 운영자 기본 스코프 집합으로 대체됩니다.
- 이 엔드포인트는 loopback/tailnet/비공개 인그레스에만 두세요. 공용 인터넷에 직접 노출하지 마세요.

인증 매트릭스:

- `gateway.auth.mode="token"` 또는 `"password"` + `Authorization: Bearer ...`
  - 공유 gateway 운영자 비밀의 소유를 증명함
  - 더 좁은 `x-openclaw-scopes`를 무시함
  - 전체 기본 운영자 스코프 집합을 복원함:
    `operator.admin`, `operator.approvals`, `operator.pairing`,
    `operator.read`, `operator.talk.secrets`, `operator.write`
  - 이 엔드포인트의 직접 도구 호출을 owner-sender 턴으로 취급함
- 신뢰된 ID 포함 HTTP 모드(예: trusted proxy 인증 또는 비공개 인그레스의 `gateway.auth.mode="none"`)
  - 어떤 외부 신뢰 ID 또는 배포 경계를 인증함
  - 헤더가 있으면 `x-openclaw-scopes`를 따름
  - 헤더가 없으면 정상적인 운영자 기본 스코프 집합으로 대체됨
  - 호출자가 명시적으로 스코프를 좁히고 `operator.admin`을 생략한 경우에만 owner 의미 체계를 잃음

## 요청 본문

```json
{
  "tool": "sessions_list",
  "action": "json",
  "args": {},
  "sessionKey": "main",
  "dryRun": false
}
```

필드:

- `tool` (string, 필수): 호출할 도구 이름.
- `action` (string, 선택 사항): 도구 스키마가 `action`을 지원하고 args 페이로드에 해당 값이 없으면 args에 매핑됩니다.
- `args` (object, 선택 사항): 도구별 인수.
- `sessionKey` (string, 선택 사항): 대상 세션 키. 생략되거나 `"main"`이면 Gateway는 구성된 메인 세션 키를 사용합니다(`session.mainKey`와 기본 agent를 따르며, 전역 범위에서는 `global`).
- `dryRun` (boolean, 선택 사항): 향후 사용을 위해 예약됨. 현재는 무시됩니다.

## 정책 + 라우팅 동작

도구 사용 가능 여부는 Gateway agent가 사용하는 것과 동일한 정책 체인을 통해 필터링됩니다:

- `tools.profile` / `tools.byProvider.profile`
- `tools.allow` / `tools.byProvider.allow`
- `agents.<id>.tools.allow` / `agents.<id>.tools.byProvider.allow`
- 그룹 정책(세션 키가 그룹 또는 채널에 매핑되는 경우)
- 하위 agent 정책(하위 agent 세션 키로 호출하는 경우)

도구가 정책에 의해 허용되지 않으면 엔드포인트는 **404**를 반환합니다.

중요한 경계 참고 사항:

- Exec 승인은 별도의 이 HTTP 엔드포인트 권한 경계가 아니라 운영자 가드레일입니다. Gateway 인증 + 도구 정책을 통해 여기서 도구에 도달할 수 있다면, `/tools/invoke`는 호출별 추가 승인 프롬프트를 더하지 않습니다.
- 신뢰 경계를 넘는 분리가 필요하다면 Gateway bearer 자격 증명을 신뢰할 수 없는 호출자와 공유하지 마세요. 그런 분리가 필요하면 별도의 gateway를 실행하세요(가급적 별도의 OS 사용자/호스트에서).

Gateway HTTP는 또한 기본적으로 하드 deny list를 적용합니다(세션 정책이 해당 도구를 허용하더라도):

- `exec` — 직접 명령 실행(RCE 표면)
- `spawn` — 임의 자식 프로세스 생성(RCE 표면)
- `shell` — 셸 명령 실행(RCE 표면)
- `fs_write` — 호스트에서의 임의 파일 변경
- `fs_delete` — 호스트에서의 임의 파일 삭제
- `fs_move` — 호스트에서의 임의 파일 이동/이름 바꾸기
- `apply_patch` — 패치 적용은 임의 파일을 다시 쓸 수 있음
- `sessions_spawn` — 세션 오케스트레이션, 원격 agent 생성은 RCE임
- `sessions_send` — 세션 간 메시지 주입
- `cron` — 영구 자동화 control plane
- `gateway` — gateway control plane, HTTP를 통한 재구성 방지
- `nodes` — 노드 명령 릴레이는 페어링된 호스트의 system.run에 도달할 수 있음
- `whatsapp_login` — 터미널 QR 스캔이 필요한 대화형 설정, HTTP에서 멈춤

이 deny list는 `gateway.tools`를 통해 사용자 지정할 수 있습니다:

```json5
{
  gateway: {
    tools: {
      // HTTP /tools/invoke에서 추가로 차단할 도구
      deny: ["browser"],
      // 기본 deny list에서 도구 제거
      allow: ["gateway"],
    },
  },
}
```

그룹 정책이 컨텍스트를 확인하는 데 도움이 되도록 선택적으로 다음을 설정할 수 있습니다:

- `x-openclaw-message-channel: <channel>` (예: `slack`, `telegram`)
- `x-openclaw-account-id: <accountId>` (여러 계정이 있을 때)

## 응답

- `200` → `{ ok: true, result }`
- `400` → `{ ok: false, error: { type, message } }` (잘못된 요청 또는 도구 입력 오류)
- `401` → 인증되지 않음
- `429` → 인증 속도 제한 적용됨(`Retry-After` 설정)
- `404` → 도구를 사용할 수 없음(존재하지 않거나 허용 목록에 없음)
- `405` → 허용되지 않는 메서드
- `500` → `{ ok: false, error: { type, message } }` (예상치 못한 도구 실행 오류, 메시지는 정제됨)

## 예시

```bash
curl -sS http://127.0.0.1:18789/tools/invoke \
  -H 'Authorization: Bearer secret' \
  -H 'Content-Type: application/json' \
  -d '{
    "tool": "sessions_list",
    "action": "json",
    "args": {}
  }'
```
