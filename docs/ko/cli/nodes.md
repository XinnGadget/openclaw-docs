---
read_when:
    - 페어링된 노드(카메라, screen, canvas)를 관리하는 중
    - 요청을 승인하거나 노드 명령을 호출해야 함
summary: '`openclaw nodes`용 CLI 참조(status, pairing, invoke, camera/canvas/screen)'
title: nodes
x-i18n:
    generated_at: "2026-04-05T12:38:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1ce3095591c4623ad18e3eca8d8083e5c10266fbf94afea2d025f0ba8093a175
    source_path: cli/nodes.md
    workflow: 15
---

# `openclaw nodes`

페어링된 노드(기기)를 관리하고 노드 기능을 호출합니다.

관련 문서:

- 노드 개요: [Nodes](/nodes)
- 카메라: [Camera nodes](/nodes/camera)
- 이미지: [Image nodes](/nodes/images)

공통 옵션:

- `--url`, `--token`, `--timeout`, `--json`

## 일반적인 명령

```bash
openclaw nodes list
openclaw nodes list --connected
openclaw nodes list --last-connected 24h
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes reject <requestId>
openclaw nodes rename --node <id|name|ip> --name <displayName>
openclaw nodes status
openclaw nodes status --connected
openclaw nodes status --last-connected 24h
```

`nodes list`는 대기 중/페어링된 표를 출력합니다. 페어링된 행에는 가장 최근 연결 경과 시간(Last Connect)이 포함됩니다.
현재 연결된 노드만 표시하려면 `--connected`를 사용하세요. `--last-connected <duration>`을 사용하면
지정한 기간 내에 연결된 노드로 필터링할 수 있습니다(예: `24h`, `7d`).

승인 참고:

- `openclaw nodes pending`은 pairing scope만 필요합니다.
- `openclaw nodes approve <requestId>`는 대기 요청의
  추가 scope 요구 사항을 상속합니다.
  - 명령 없는 요청: pairing만
  - exec가 아닌 노드 명령: pairing + write
  - `system.run` / `system.run.prepare` / `system.which`: pairing + admin

## 호출

```bash
openclaw nodes invoke --node <id|name|ip> --command <command> --params <json>
```

호출 플래그:

- `--params <json>`: JSON 객체 문자열(기본값 `{}`).
- `--invoke-timeout <ms>`: 노드 호출 타임아웃(기본값 `15000`).
- `--idempotency-key <key>`: 선택적 멱등성 키.
- `system.run` 및 `system.run.prepare`는 여기서 차단됩니다. 셸 실행에는 `host=node`와 함께 `exec` 도구를 사용하세요.

노드에서 셸을 실행하려면 `openclaw nodes run` 대신 `host=node`와 함께 `exec` 도구를 사용하세요.
이제 `nodes` CLI는 기능 중심입니다. 직접 RPC는 `nodes invoke`로 수행하며, 그 외 pairing, camera,
screen, location, canvas, notifications를 지원합니다.
