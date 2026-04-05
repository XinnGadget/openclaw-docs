---
read_when:
    - CLI에서 exec 승인을 편집하려는 경우
    - 게이트웨이 또는 노드 호스트의 허용 목록을 관리해야 하는 경우
summary: 게이트웨이 또는 노드 호스트의 exec 승인을 위한 `openclaw approvals` CLI 참조
title: approvals
x-i18n:
    generated_at: "2026-04-05T12:37:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7b2532bfd3e6e6ce43c96a2807df2dd00cb7b4320b77a7dfd09bee0531da610e
    source_path: cli/approvals.md
    workflow: 15
---

# `openclaw approvals`

**로컬 호스트**, **게이트웨이 호스트**, 또는 **노드 호스트**의 exec 승인을 관리합니다.
기본적으로 명령은 디스크의 로컬 approvals 파일을 대상으로 합니다. 게이트웨이를 대상으로 하려면 `--gateway`를, 특정 노드를 대상으로 하려면 `--node`를 사용하세요.

별칭: `openclaw exec-approvals`

관련 항목:

- Exec approvals: [Exec approvals](/tools/exec-approvals)
- Nodes: [Nodes](/nodes)

## 일반 명령

```bash
openclaw approvals get
openclaw approvals get --node <id|name|ip>
openclaw approvals get --gateway
```

이제 `openclaw approvals get`은 로컬, 게이트웨이, 노드 대상에 대한 유효한 exec 정책을 표시합니다.

- 요청된 `tools.exec` 정책
- 호스트 approvals-file 정책
- 우선순위 규칙 적용 후의 유효 결과

우선순위는 의도된 동작입니다.

- 호스트 approvals 파일은 강제 가능한 기준 정보입니다
- 요청된 `tools.exec` 정책은 의도를 더 좁히거나 넓힐 수 있지만, 유효 결과는 여전히 호스트 규칙에서 파생됩니다
- `--node`는 노드 호스트 approvals 파일과 게이트웨이 `tools.exec` 정책을 결합합니다. 둘 다 런타임에 계속 적용되기 때문입니다
- 게이트웨이 config를 사용할 수 없으면 CLI는 노드 approvals 스냅샷으로 대체하고 최종 런타임 정책을 계산할 수 없었다고 표시합니다

## 파일에서 approvals 교체

```bash
openclaw approvals set --file ./exec-approvals.json
openclaw approvals set --stdin <<'EOF'
{ version: 1, defaults: { security: "full", ask: "off" } }
EOF
openclaw approvals set --node <id|name|ip> --file ./exec-approvals.json
openclaw approvals set --gateway --file ./exec-approvals.json
```

`set`은 엄격한 JSON만이 아니라 JSON5를 허용합니다. `--file` 또는 `--stdin` 중 하나만 사용하고, 둘 다 함께 사용하지는 마세요.

## "절대 프롬프트하지 않음" / YOLO 예시

호스트가 exec 승인에서 절대 멈추지 않아야 한다면, 호스트 approvals 기본값을 `full` + `off`로 설정하세요.

```bash
openclaw approvals set --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

노드 버전:

```bash
openclaw approvals set --node <id|name|ip> --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

이것은 **호스트 approvals 파일**만 변경합니다. 요청된 OpenClaw 정책도 일치시키려면 다음도 설정하세요.

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
```

이 예시에서 `tools.exec.host=gateway`인 이유:

- `host=auto`는 여전히 "가능하면 샌드박스, 그렇지 않으면 게이트웨이"를 의미합니다.
- YOLO는 라우팅이 아니라 승인에 관한 것입니다.
- 샌드박스가 구성되어 있어도 호스트 exec를 사용하려면 `gateway` 또는 `/exec host=gateway`로 호스트 선택을 명시적으로 지정하세요.

이것은 현재 호스트 기본 YOLO 동작과 일치합니다. 승인이 필요하다면 더 엄격하게 조이세요.

## 허용 목록 도우미

```bash
openclaw approvals allowlist add "~/Projects/**/bin/rg"
openclaw approvals allowlist add --agent main --node <id|name|ip> "/usr/bin/uptime"
openclaw approvals allowlist add --agent "*" "/usr/bin/uname"

openclaw approvals allowlist remove "~/Projects/**/bin/rg"
```

## 공통 옵션

`get`, `set`, `allowlist add|remove`는 모두 다음을 지원합니다.

- `--node <id|name|ip>`
- `--gateway`
- 공유 노드 RPC 옵션: `--url`, `--token`, `--timeout`, `--json`

대상 지정 참고 사항:

- 대상 플래그가 없으면 디스크의 로컬 approvals 파일을 의미합니다
- `--gateway`는 게이트웨이 호스트 approvals 파일을 대상으로 합니다
- `--node`는 ID, 이름, IP 또는 ID 접두사를 확인한 후 하나의 노드 호스트를 대상으로 합니다

`allowlist add|remove`는 다음도 지원합니다.

- `--agent <id>`(기본값은 `*`)

## 참고

- `--node`는 `openclaw nodes`와 동일한 리졸버를 사용합니다(ID, 이름, IP 또는 ID 접두사).
- `--agent`의 기본값은 `"*"`이며, 이는 모든 에이전트에 적용됩니다.
- 노드 호스트는 `system.execApprovals.get/set`을 광고해야 합니다(macOS 앱 또는 헤드리스 노드 호스트).
- Approvals 파일은 호스트별로 `~/.openclaw/exec-approvals.json`에 저장됩니다.
