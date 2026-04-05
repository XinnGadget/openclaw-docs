---
read_when: You are managing sandbox runtimes or debugging sandbox/tool-policy behavior.
status: active
summary: 격리된 에이전트 실행을 위한 sandbox 런타임을 관리하고 유효 sandbox 정책을 검사합니다
title: Sandbox CLI
x-i18n:
    generated_at: "2026-04-05T12:38:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: fa2783037da2901316108d35e04bb319d5d57963c2764b9146786b3c6474b48a
    source_path: cli/sandbox.md
    workflow: 15
---

# Sandbox CLI

격리된 에이전트 실행을 위한 sandbox 런타임을 관리합니다.

## 개요

OpenClaw는 보안을 위해 에이전트를 격리된 sandbox 런타임에서 실행할 수 있습니다. `sandbox` 명령은 업데이트나 구성 변경 후 해당 런타임을 검사하고 다시 만드는 데 도움을 줍니다.

현재 이는 일반적으로 다음을 의미합니다.

- Docker sandbox 컨테이너
- `agents.defaults.sandbox.backend = "ssh"`일 때의 SSH sandbox 런타임
- `agents.defaults.sandbox.backend = "openshell"`일 때의 OpenShell sandbox 런타임

`ssh` 및 OpenShell `remote`의 경우, 다시 만들기는 Docker보다 더 중요합니다.

- 원격 workspace는 초기 시드 이후 정본입니다
- `openclaw sandbox recreate`는 선택한 범위의 해당 정본 원격 workspace를 삭제합니다
- 다음 사용 시 현재 로컬 workspace에서 다시 시드합니다

## 명령

### `openclaw sandbox explain`

**유효한** sandbox 모드/범위/workspace 액세스, sandbox 도구 정책, 상승 권한 게이트를 검사합니다(fix-it config 키 경로 포함).

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

### `openclaw sandbox list`

모든 sandbox 런타임을 상태 및 구성과 함께 나열합니다.

```bash
openclaw sandbox list
openclaw sandbox list --browser  # 브라우저 컨테이너만 나열
openclaw sandbox list --json     # JSON 출력
```

**출력에는 다음이 포함됩니다.**

- 런타임 이름 및 상태
- 백엔드 (`docker`, `openshell` 등)
- config 레이블 및 현재 config와 일치하는지 여부
- 생성 후 경과 시간
- 유휴 시간(마지막 사용 이후 경과 시간)
- 연결된 세션/에이전트

### `openclaw sandbox recreate`

업데이트된 config로 다시 생성되도록 sandbox 런타임을 제거합니다.

```bash
openclaw sandbox recreate --all                # 모든 컨테이너 다시 만들기
openclaw sandbox recreate --session main       # 특정 세션
openclaw sandbox recreate --agent mybot        # 특정 에이전트
openclaw sandbox recreate --browser            # 브라우저 컨테이너만
openclaw sandbox recreate --all --force        # 확인 건너뛰기
```

**옵션:**

- `--all`: 모든 sandbox 컨테이너 다시 만들기
- `--session <key>`: 특정 세션의 컨테이너 다시 만들기
- `--agent <id>`: 특정 에이전트의 컨테이너 다시 만들기
- `--browser`: 브라우저 컨테이너만 다시 만들기
- `--force`: 확인 프롬프트 건너뛰기

**중요:** 런타임은 에이전트가 다음에 사용될 때 자동으로 다시 생성됩니다.

## 사용 사례

### Docker 이미지 업데이트 후

```bash
# 새 이미지 가져오기
docker pull openclaw-sandbox:latest
docker tag openclaw-sandbox:latest openclaw-sandbox:bookworm-slim

# 새 이미지를 사용하도록 config 업데이트
# config 편집: agents.defaults.sandbox.docker.image (또는 agents.list[].sandbox.docker.image)

# 컨테이너 다시 만들기
openclaw sandbox recreate --all
```

### sandbox 구성 변경 후

```bash
# config 편집: agents.defaults.sandbox.* (또는 agents.list[].sandbox.*)

# 새 config 적용을 위해 다시 만들기
openclaw sandbox recreate --all
```

### SSH 대상 또는 SSH 인증 자료 변경 후

```bash
# config 편집:
# - agents.defaults.sandbox.backend
# - agents.defaults.sandbox.ssh.target
# - agents.defaults.sandbox.ssh.workspaceRoot
# - agents.defaults.sandbox.ssh.identityFile / certificateFile / knownHostsFile
# - agents.defaults.sandbox.ssh.identityData / certificateData / knownHostsData

openclaw sandbox recreate --all
```

핵심 `ssh` 백엔드의 경우, 다시 만들기는 SSH 대상의 범위별 원격 workspace 루트를 삭제합니다. 다음 실행 시 로컬 workspace에서 다시 시드합니다.

### OpenShell 소스, 정책 또는 모드 변경 후

```bash
# config 편집:
# - agents.defaults.sandbox.backend
# - plugins.entries.openshell.config.from
# - plugins.entries.openshell.config.mode
# - plugins.entries.openshell.config.policy

openclaw sandbox recreate --all
```

OpenShell `remote` 모드의 경우, 다시 만들기는 해당 범위의 정본 원격 workspace를 삭제합니다. 다음 실행 시 로컬 workspace에서 다시 시드합니다.

### setupCommand 변경 후

```bash
openclaw sandbox recreate --all
# 또는 에이전트 하나만:
openclaw sandbox recreate --agent family
```

### 특정 에이전트에만 적용

```bash
# 한 에이전트의 컨테이너만 업데이트
openclaw sandbox recreate --agent alfred
```

## 왜 이것이 필요한가요?

**문제:** sandbox 구성을 업데이트하면 다음과 같은 일이 발생합니다.

- 기존 런타임은 이전 설정으로 계속 실행됩니다
- 런타임은 24시간 비활성 상태가 되어야만 정리됩니다
- 자주 사용되는 에이전트는 이전 런타임을 무기한 유지합니다

**해결책:** `openclaw sandbox recreate`를 사용해 이전 런타임을 강제로 제거하세요. 이후 필요할 때 현재 설정으로 자동 재생성됩니다.

팁: 백엔드별 수동 정리보다 `openclaw sandbox recreate`를 우선 사용하세요.
이 명령은 Gateway의 런타임 레지스트리를 사용하므로 범위/세션 키가 바뀔 때 불일치를 방지합니다.

## 구성

sandbox 설정은 `~/.openclaw/openclaw.json`의 `agents.defaults.sandbox` 아래에 있습니다(에이전트별 재정의는 `agents.list[].sandbox`에 둡니다).

```jsonc
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "all", // off, non-main, all
        "backend": "docker", // docker, ssh, openshell
        "scope": "agent", // session, agent, shared
        "docker": {
          "image": "openclaw-sandbox:bookworm-slim",
          "containerPrefix": "openclaw-sbx-",
          // ... more Docker options
        },
        "prune": {
          "idleHours": 24, // 24시간 유휴 후 자동 정리
          "maxAgeDays": 7, // 7일 후 자동 정리
        },
      },
    },
  },
}
```

## 함께 보기

- [Sandbox 문서](/gateway/sandboxing)
- [에이전트 구성](/concepts/agent-workspace)
- [Doctor 명령](/gateway/doctor) - sandbox 설정 확인
