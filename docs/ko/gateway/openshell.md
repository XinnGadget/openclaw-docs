---
read_when:
    - 로컬 Docker 대신 클라우드 관리형 sandbox를 사용하려는 경우
    - OpenShell plugin을 설정하는 경우
    - mirror와 remote 워크스페이스 모드 중 하나를 선택해야 하는 경우
summary: OpenClaw 에이전트용 관리형 sandbox 백엔드로 OpenShell 사용
title: OpenShell
x-i18n:
    generated_at: "2026-04-05T12:43:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: aaf9027d0632a70fb86455f8bc46dc908ff766db0eb0cdf2f7df39c715241ead
    source_path: gateway/openshell.md
    workflow: 15
---

# OpenShell

OpenShell은 OpenClaw용 관리형 sandbox 백엔드입니다. Docker
컨테이너를 로컬에서 실행하는 대신, OpenClaw는 `openshell` CLI에 sandbox 수명 주기를 위임하며,
이 CLI는 SSH 기반 명령 실행이 가능한 원격 환경을 프로비저닝합니다.

OpenShell plugin은 일반 [SSH backend](/gateway/sandboxing#ssh-backend)와 동일한 코어 SSH 전송 및 원격 파일 시스템
브리지를 재사용합니다. 여기에 OpenShell 전용 수명 주기(`sandbox create/get/delete`, `sandbox ssh-config`)
와 선택적인 `mirror` 워크스페이스 모드를 추가합니다.

## 전제 조건

- `PATH`에 설치된 `openshell` CLI(또는
  `plugins.entries.openshell.config.command`로 사용자 지정 경로 설정)
- sandbox 접근 권한이 있는 OpenShell 계정
- 호스트에서 실행 중인 OpenClaw 게이트웨이

## 빠른 시작

1. plugin을 활성화하고 sandbox 백엔드를 설정합니다:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "openshell",
        scope: "session",
        workspaceAccess: "rw",
      },
    },
  },
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          from: "openclaw",
          mode: "remote",
        },
      },
    },
  },
}
```

2. 게이트웨이를 다시 시작합니다. 다음 에이전트 턴에서 OpenClaw는 OpenShell
   sandbox를 생성하고 도구 실행을 그쪽으로 라우팅합니다.

3. 확인:

```bash
openclaw sandbox list
openclaw sandbox explain
```

## 워크스페이스 모드

이것은 OpenShell을 사용할 때 가장 중요한 결정입니다.

### `mirror`

**로컬
워크스페이스를 정본으로 유지**하려면 `plugins.entries.openshell.config.mode: "mirror"`를 사용하세요.

동작:

- `exec` 전에 OpenClaw가 로컬 워크스페이스를 OpenShell sandbox로 동기화합니다.
- `exec` 후 OpenClaw가 원격 워크스페이스를 다시 로컬 워크스페이스로 동기화합니다.
- 파일 도구는 여전히 sandbox 브리지를 통해 동작하지만, 턴 사이에서는 로컬 워크스페이스가
  소스 오브 트루스로 유지됩니다.

다음에 가장 적합합니다:

- OpenClaw 외부에서 로컬 파일을 편집하며 그 변경 사항이
  sandbox에 자동으로 반영되길 원하는 경우
- OpenShell sandbox가 Docker 백엔드처럼 최대한
  비슷하게 동작하길 원하는 경우
- 각 `exec` 턴 후 호스트 워크스페이스에 sandbox 쓰기 결과가 반영되길 원하는 경우

트레이드오프: 각 exec 전후에 추가 동기화 비용이 듭니다.

### `remote`

**OpenShell 워크스페이스를 정본으로 만들고 싶다면**
`plugins.entries.openshell.config.mode: "remote"`를 사용하세요.

동작:

- sandbox가 처음 생성될 때 OpenClaw는 로컬 워크스페이스를
  한 번만 원격 워크스페이스로 시드합니다.
- 그 이후 `exec`, `read`, `write`, `edit`, `apply_patch`는
  원격 OpenShell 워크스페이스에 직접 작동합니다.
- OpenClaw는 원격 변경 사항을 로컬 워크스페이스로 다시 동기화하지 않습니다.
- 파일 및 미디어 도구가 sandbox 브리지를 통해 읽기 때문에 프롬프트 시점 미디어 읽기는 여전히 동작합니다.

다음에 가장 적합합니다:

- sandbox가 주로 원격 측에서 유지되어야 하는 경우
- 턴별 동기화 오버헤드를 줄이고 싶은 경우
- 호스트 로컬 편집이 원격 sandbox 상태를 조용히 덮어쓰지 않기를 원하는 경우

중요: 초기 시드 이후에 OpenClaw 외부에서 호스트의 파일을 편집하면,
원격 sandbox는 그 변경 사항을 보지 못합니다.
다시 시드하려면 `openclaw sandbox recreate`를 사용하세요.

### 모드 선택

|                          | `mirror`                    | `remote`                   |
| ------------------------ | --------------------------- | -------------------------- |
| **정본 워크스페이스**    | 로컬 호스트                 | 원격 OpenShell             |
| **동기화 방향**          | 양방향(각 exec마다)         | 1회 시드                   |
| **턴별 오버헤드**        | 높음(업로드 + 다운로드)     | 낮음(직접 원격 작업)       |
| **로컬 편집이 보이는가?** | 예, 다음 exec에서           | 아니요, recreate 전까지    |
| **적합한 용도**          | 개발 워크플로               | 장기 실행 에이전트, CI     |

## 구성 참조

모든 OpenShell config는 `plugins.entries.openshell.config` 아래에 있습니다:

| 키                        | 유형                     | 기본값        | 설명 |
| ------------------------- | ------------------------ | ------------- | ----------------------------------------------------- |
| `mode`                    | `"mirror"` 또는 `"remote"` | `"mirror"`    | 워크스페이스 동기화 모드 |
| `command`                 | `string`                 | `"openshell"` | `openshell` CLI의 경로 또는 이름 |
| `from`                    | `string`                 | `"openclaw"`  | 최초 생성 시 sandbox 소스 |
| `gateway`                 | `string`                 | —             | OpenShell 게이트웨이 이름(`--gateway`) |
| `gatewayEndpoint`         | `string`                 | —             | OpenShell 게이트웨이 엔드포인트 URL(`--gateway-endpoint`) |
| `policy`                  | `string`                 | —             | sandbox 생성용 OpenShell 정책 ID |
| `providers`               | `string[]`               | `[]`          | sandbox 생성 시 연결할 provider 이름 |
| `gpu`                     | `boolean`                | `false`       | GPU 리소스 요청 |
| `autoProviders`           | `boolean`                | `true`        | sandbox 생성 중 `--auto-providers` 전달 |
| `remoteWorkspaceDir`      | `string`                 | `"/sandbox"`  | sandbox 내부의 기본 쓰기 가능 워크스페이스 |
| `remoteAgentWorkspaceDir` | `string`                 | `"/agent"`    | 에이전트 워크스페이스 마운트 경로(읽기 전용 접근용) |
| `timeoutSeconds`          | `number`                 | `120`         | `openshell` CLI 작업 타임아웃 |

sandbox 수준 설정(`mode`, `scope`, `workspaceAccess`)은 다른 백엔드와 마찬가지로
`agents.defaults.sandbox` 아래에서 구성합니다.
전체 매트릭스는 [Sandboxing](/gateway/sandboxing)을 참조하세요.

## 예시

### 최소 remote 설정

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "openshell",
      },
    },
  },
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          from: "openclaw",
          mode: "remote",
        },
      },
    },
  },
}
```

### GPU를 사용하는 mirror 모드

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "openshell",
        scope: "agent",
        workspaceAccess: "rw",
      },
    },
  },
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          from: "openclaw",
          mode: "mirror",
          gpu: true,
          providers: ["openai"],
          timeoutSeconds: 180,
        },
      },
    },
  },
}
```

### 사용자 지정 게이트웨이를 사용하는 에이전트별 OpenShell

```json5
{
  agents: {
    defaults: {
      sandbox: { mode: "off" },
    },
    list: [
      {
        id: "researcher",
        sandbox: {
          mode: "all",
          backend: "openshell",
          scope: "agent",
          workspaceAccess: "rw",
        },
      },
    ],
  },
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          from: "openclaw",
          mode: "remote",
          gateway: "lab",
          gatewayEndpoint: "https://lab.example",
          policy: "strict",
        },
      },
    },
  },
}
```

## 수명 주기 관리

OpenShell sandbox는 일반 sandbox CLI를 통해 관리됩니다:

```bash
# 모든 sandbox 런타임 나열(Docker + OpenShell)
openclaw sandbox list

# 유효 정책 검사
openclaw sandbox explain

# 재생성(원격 워크스페이스 삭제, 다음 사용 시 다시 시드)
openclaw sandbox recreate --all
```

`remote` 모드에서는 **recreate가 특히 중요합니다**. 이 명령은 해당 범위의 정본
원격 워크스페이스를 삭제합니다. 다음 사용 시 로컬 워크스페이스에서
새 원격 워크스페이스를 시드합니다.

`mirror` 모드에서는 로컬 워크스페이스가 정본으로 유지되므로
recreate는 주로 원격 실행 환경을 재설정합니다.

### recreate가 필요한 경우

다음 중 하나를 변경한 후 recreate하세요:

- `agents.defaults.sandbox.backend`
- `plugins.entries.openshell.config.from`
- `plugins.entries.openshell.config.mode`
- `plugins.entries.openshell.config.policy`

```bash
openclaw sandbox recreate --all
```

## 현재 제한 사항

- sandbox 브라우저는 OpenShell 백엔드에서 지원되지 않습니다.
- `sandbox.docker.binds`는 OpenShell에 적용되지 않습니다.
- `sandbox.docker.*` 아래의 Docker 전용 런타임 설정은 Docker
  백엔드에만 적용됩니다.

## 동작 방식

1. OpenClaw는 `openshell sandbox create`를 호출합니다(구성에 따라 `--from`, `--gateway`,
   `--policy`, `--providers`, `--gpu` 플래그 포함).
2. OpenClaw는 sandbox의 SSH 연결
   세부 정보를 얻기 위해 `openshell sandbox ssh-config <name>`를 호출합니다.
3. 코어는 SSH config를 임시 파일에 기록하고, 일반 SSH 백엔드와 동일한 원격 파일 시스템 브리지를 사용하여
   SSH 세션을 엽니다.
4. `mirror` 모드에서는: exec 전에 로컬에서 원격으로 동기화하고, 실행한 뒤 exec 후 다시 동기화합니다.
5. `remote` 모드에서는: 생성 시 한 번 시드한 뒤 원격
   워크스페이스에서 직접 작업합니다.

## 함께 보기

- [Sandboxing](/gateway/sandboxing) -- 모드, 범위, 백엔드 비교
- [Sandbox vs Tool Policy vs Elevated](/gateway/sandbox-vs-tool-policy-vs-elevated) -- 차단된 도구 디버깅
- [Multi-Agent Sandbox and Tools](/tools/multi-agent-sandbox-tools) -- 에이전트별 재정의
- [Sandbox CLI](/cli/sandbox) -- `openclaw sandbox` 명령
