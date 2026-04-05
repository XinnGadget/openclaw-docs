---
read_when:
    - provider 자격 증명과 `auth-profiles.json` ref용 SecretRef를 구성하는 경우
    - 프로덕션에서 secrets reload, audit, configure, apply를 안전하게 운영하는 경우
    - 시작 시 fail-fast, 비활성 표면 필터링, 마지막 정상 상태 유지 동작을 이해하려는 경우
summary: 'Secrets 관리: SecretRef 계약, 런타임 스냅샷 동작, 안전한 단방향 스크러빙'
title: Secrets 관리
x-i18n:
    generated_at: "2026-04-05T12:44:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: b91778cb7801fe24f050c15c0a9dd708dda91cb1ce86096e6bae57ebb6e0d41d
    source_path: gateway/secrets.md
    workflow: 15
---

# Secrets 관리

OpenClaw는 지원되는 자격 증명을 구성에 평문으로 저장하지 않아도 되도록 additive SecretRef를 지원합니다.

평문도 여전히 사용할 수 있습니다. SecretRefs는 자격 증명별 옵트인 방식입니다.

## 목표와 런타임 모델

secrets는 메모리 내 런타임 스냅샷으로 해석됩니다.

- 해석은 요청 경로에서 지연 수행되지 않고 활성화 중 eager하게 수행됩니다.
- 실질적으로 활성 상태인 SecretRef를 해석할 수 없으면 시작은 fail-fast합니다.
- reload는 원자적 교체를 사용합니다. 전체 성공이거나 마지막 정상 상태 스냅샷을 유지합니다.
- SecretRef 정책 위반(예: OAuth 모드 auth profile과 SecretRef 입력의 결합)은 런타임 교체 전에 활성화를 실패시킵니다.
- 런타임 요청은 활성 메모리 내 스냅샷에서만 읽습니다.
- 첫 번째 성공적인 config 활성화/로드 이후, 런타임 코드 경로는 성공적인 reload가 교체를 수행할 때까지 그 활성 메모리 내 스냅샷만 계속 읽습니다.
- 아웃바운드 전달 경로도 이 활성 스냅샷에서 읽습니다(예: Discord 응답/스레드 전달, Telegram action 전송). 전송할 때마다 SecretRef를 다시 해석하지 않습니다.

이렇게 하면 secret provider 장애가 hot request path에 영향을 주지 않게 됩니다.

## 활성 표면 필터링

SecretRefs는 실질적으로 활성 상태인 표면에서만 검증됩니다.

- 활성화된 표면: 해석되지 않은 refs는 시작/reload를 차단합니다.
- 비활성 표면: 해석되지 않은 refs는 시작/reload를 차단하지 않습니다.
- 비활성 refs는 코드 `SECRETS_REF_IGNORED_INACTIVE_SURFACE`와 함께 치명적이지 않은 진단을 내보냅니다.

비활성 표면의 예:

- 비활성화된 채널/계정 항목
- 어떤 활성 계정도 상속하지 않는 최상위 채널 자격 증명
- 비활성화된 tool/기능 표면
- `tools.web.search.provider`에서 선택되지 않은 웹 검색 provider 전용 키  
  auto 모드(provider 미설정)에서는 provider 자동 감지를 위해 우선순위에 따라 키를 확인하며, 하나가 해석될 때까지 계속합니다.  
  선택 후에는 선택되지 않은 provider 키는 선택될 때까지 비활성으로 처리됩니다.
- 샌드박스 SSH 인증 자료(`agents.defaults.sandbox.ssh.identityData`, `certificateData`, `knownHostsData` 및 에이전트별 재정의)는 기본 에이전트 또는 활성 에이전트의 유효한 샌드박스 백엔드가 `ssh`일 때만 활성입니다.
- `gateway.remote.token` / `gateway.remote.password` SecretRefs는 다음 중 하나가 참이면 활성입니다:
  - `gateway.mode=remote`
  - `gateway.remote.url`이 구성됨
  - `gateway.tailscale.mode`가 `serve` 또는 `funnel`
  - 위 원격 표면이 없는 로컬 모드에서는:
    - env/auth token이 구성되지 않았고 token auth가 우선될 수 있으면 `gateway.remote.token`이 활성
    - env/auth password가 구성되지 않았고 password auth가 우선될 수 있을 때만 `gateway.remote.password`가 활성
- `gateway.auth.token` SecretRef는 `OPENCLAW_GATEWAY_TOKEN`이 설정된 경우 시작 인증 해석에서는 비활성입니다. 이 런타임에서는 env token 입력이 우선하기 때문입니다.

## Gateway 인증 표면 진단

`gateway.auth.token`, `gateway.auth.password`, `gateway.remote.token`, `gateway.remote.password`에 SecretRef가 구성되면 gateway 시작/reload는 해당 표면 상태를 명시적으로 기록합니다.

- `active`: SecretRef가 유효 인증 표면의 일부이며 반드시 해석되어야 함
- `inactive`: 다른 인증 표면이 우선하거나 원격 인증이 비활성/미활성이라서 이 런타임에서는 SecretRef가 무시됨

이 항목들은 `SECRETS_GATEWAY_AUTH_SURFACE`로 기록되며, 활성 표면 정책이 사용한 이유도 포함하므로 자격 증명이 왜 active 또는 inactive로 처리되었는지 확인할 수 있습니다.

## 온보딩 참조 preflight

온보딩이 대화형 모드로 실행되고 SecretRef 저장소를 선택하면 OpenClaw는 저장 전에 preflight 검증을 수행합니다.

- Env refs: env var 이름을 검증하고 설정 중 비어 있지 않은 값이 보이는지 확인
- Provider refs (`file` 또는 `exec`): provider 선택을 검증하고 `id`를 해석하며 해석된 값 유형을 확인
- Quickstart 재사용 경로: `gateway.auth.token`이 이미 SecretRef인 경우, 온보딩은 probe/dashboard bootstrap 전에(`env`, `file`, `exec` refs에 대해) 동일한 fail-fast 게이트를 사용해 이를 해석

검증에 실패하면 온보딩은 오류를 표시하고 다시 시도할 수 있게 합니다.

## SecretRef 계약

어디서나 동일한 객체 형태를 사용합니다.

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

### `source: "env"`

```json5
{ source: "env", provider: "default", id: "OPENAI_API_KEY" }
```

검증:

- `provider`는 `^[a-z][a-z0-9_-]{0,63}$`와 일치해야 함
- `id`는 `^[A-Z][A-Z0-9_]{0,127}$`와 일치해야 함

### `source: "file"`

```json5
{ source: "file", provider: "filemain", id: "/providers/openai/apiKey" }
```

검증:

- `provider`는 `^[a-z][a-z0-9_-]{0,63}$`와 일치해야 함
- `id`는 절대 JSON pointer(` /...`)여야 함
- 세그먼트 내 RFC6901 이스케이프: `~` => `~0`, `/` => `~1`

### `source: "exec"`

```json5
{ source: "exec", provider: "vault", id: "providers/openai/apiKey" }
```

검증:

- `provider`는 `^[a-z][a-z0-9_-]{0,63}$`와 일치해야 함
- `id`는 `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`와 일치해야 함
- `id`는 `/`로 구분된 경로 세그먼트로 `.` 또는 `..`를 포함하면 안 됨(예: `a/../b`는 거부됨)

## Provider config

providers는 `secrets.providers` 아래에 정의합니다.

```json5
{
  secrets: {
    providers: {
      default: { source: "env" },
      filemain: {
        source: "file",
        path: "~/.openclaw/secrets.json",
        mode: "json", // 또는 "singleValue"
      },
      vault: {
        source: "exec",
        command: "/usr/local/bin/openclaw-vault-resolver",
        args: ["--profile", "prod"],
        passEnv: ["PATH", "VAULT_ADDR"],
        jsonOnly: true,
      },
    },
    defaults: {
      env: "default",
      file: "filemain",
      exec: "vault",
    },
    resolution: {
      maxProviderConcurrency: 4,
      maxRefsPerProvider: 512,
      maxBatchBytes: 262144,
    },
  },
}
```

### Env provider

- 선택적 허용 목록은 `allowlist`를 통해 설정
- 누락되었거나 비어 있는 env 값은 해석 실패

### File provider

- `path`에서 로컬 파일 읽기
- `mode: "json"`은 JSON 객체 payload를 기대하고 `id`를 pointer로 해석
- `mode: "singleValue"`는 ref id `"value"`를 기대하고 파일 내용을 반환
- 경로는 소유권/권한 검사를 통과해야 함
- Windows fail-closed 참고: 경로의 ACL 검증을 사용할 수 없으면 해석은 실패합니다. 신뢰된 경로에 한해 해당 provider에 `allowInsecurePath: true`를 설정해 경로 보안 검사를 우회할 수 있습니다.

### Exec provider

- 구성된 절대 바이너리 경로를 실행하며 셸은 사용하지 않음
- 기본적으로 `command`는 일반 파일(심볼릭 링크 아님)을 가리켜야 함
- Homebrew shim 같은 심볼릭 링크 명령 경로를 허용하려면 `allowSymlinkCommand: true` 설정
- OpenClaw는 해석된 대상 경로를 검증함
- 패키지 관리자 경로에는 `allowSymlinkCommand`와 `trustedDirs`를 함께 사용(예: `["/opt/homebrew"]`)
- 타임아웃, no-output 타임아웃, 출력 바이트 제한, env 허용 목록, trusted dirs 지원
- Windows fail-closed 참고: 명령 경로의 ACL 검증을 사용할 수 없으면 해석은 실패합니다. 신뢰된 경로에 한해 해당 provider에 `allowInsecurePath: true`를 설정해 경로 보안 검사를 우회할 수 있습니다.

요청 payload (stdin):

```json
{ "protocolVersion": 1, "provider": "vault", "ids": ["providers/openai/apiKey"] }
```

응답 payload (stdout):

```jsonc
{ "protocolVersion": 1, "values": { "providers/openai/apiKey": "<openai-api-key>" } } // pragma: allowlist secret
```

선택적 per-id 오류:

```json
{
  "protocolVersion": 1,
  "values": {},
  "errors": { "providers/openai/apiKey": { "message": "not found" } }
}
```

## Exec 통합 예시

### 1Password CLI

```json5
{
  secrets: {
    providers: {
      onepassword_openai: {
        source: "exec",
        command: "/opt/homebrew/bin/op",
        allowSymlinkCommand: true, // Homebrew 심볼릭 링크 바이너리에 필요
        trustedDirs: ["/opt/homebrew"],
        args: ["read", "op://Personal/OpenClaw QA API Key/password"],
        passEnv: ["HOME"],
        jsonOnly: false,
      },
    },
  },
  models: {
    providers: {
      openai: {
        baseUrl: "https://api.openai.com/v1",
        models: [{ id: "gpt-5", name: "gpt-5" }],
        apiKey: { source: "exec", provider: "onepassword_openai", id: "value" },
      },
    },
  },
}
```

### HashiCorp Vault CLI

```json5
{
  secrets: {
    providers: {
      vault_openai: {
        source: "exec",
        command: "/opt/homebrew/bin/vault",
        allowSymlinkCommand: true, // Homebrew 심볼릭 링크 바이너리에 필요
        trustedDirs: ["/opt/homebrew"],
        args: ["kv", "get", "-field=OPENAI_API_KEY", "secret/openclaw"],
        passEnv: ["VAULT_ADDR", "VAULT_TOKEN"],
        jsonOnly: false,
      },
    },
  },
  models: {
    providers: {
      openai: {
        baseUrl: "https://api.openai.com/v1",
        models: [{ id: "gpt-5", name: "gpt-5" }],
        apiKey: { source: "exec", provider: "vault_openai", id: "value" },
      },
    },
  },
}
```

### `sops`

```json5
{
  secrets: {
    providers: {
      sops_openai: {
        source: "exec",
        command: "/opt/homebrew/bin/sops",
        allowSymlinkCommand: true, // Homebrew 심볼릭 링크 바이너리에 필요
        trustedDirs: ["/opt/homebrew"],
        args: ["-d", "--extract", '["providers"]["openai"]["apiKey"]', "/path/to/secrets.enc.json"],
        passEnv: ["SOPS_AGE_KEY_FILE"],
        jsonOnly: false,
      },
    },
  },
  models: {
    providers: {
      openai: {
        baseUrl: "https://api.openai.com/v1",
        models: [{ id: "gpt-5", name: "gpt-5" }],
        apiKey: { source: "exec", provider: "sops_openai", id: "value" },
      },
    },
  },
}
```

## MCP 서버 환경 변수

`plugins.entries.acpx.config.mcpServers`를 통해 구성된 MCP 서버 env vars는 SecretInput을 지원합니다. 이를 통해 API 키와 토큰을 평문 config에 두지 않아도 됩니다.

```json5
{
  plugins: {
    entries: {
      acpx: {
        enabled: true,
        config: {
          mcpServers: {
            github: {
              command: "npx",
              args: ["-y", "@modelcontextprotocol/server-github"],
              env: {
                GITHUB_PERSONAL_ACCESS_TOKEN: {
                  source: "env",
                  provider: "default",
                  id: "MCP_GITHUB_PAT",
                },
              },
            },
          },
        },
      },
    },
  },
}
```

평문 문자열 값도 여전히 사용할 수 있습니다. `${MCP_SERVER_API_KEY}` 같은 env-template refs와 SecretRef 객체는 MCP 서버 프로세스가 시작되기 전에 gateway 활성화 중 해석됩니다. 다른 SecretRef 표면과 마찬가지로, 해석되지 않은 refs는 `acpx` plugin이 실질적으로 활성일 때만 활성화를 차단합니다.

## Sandbox SSH 인증 자료

핵심 `ssh` 샌드박스 백엔드도 SSH 인증 자료에 대한 SecretRef를 지원합니다.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "ssh",
        ssh: {
          target: "user@gateway-host:22",
          identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
      },
    },
  },
}
```

런타임 동작:

- OpenClaw는 각 SSH 호출 시 지연 해석하지 않고 샌드박스 활성화 중 these refs를 해석합니다.
- 해석된 값은 제한적인 권한의 임시 파일에 기록되고 생성된 SSH config에서 사용됩니다.
- 유효한 샌드박스 백엔드가 `ssh`가 아니면 이러한 refs는 비활성 상태로 남아 시작을 차단하지 않습니다.

## 지원되는 자격 증명 표면

정식 지원 및 미지원 자격 증명은 다음 문서에 정리되어 있습니다.

- [SecretRef 자격 증명 표면](/reference/secretref-credential-surface)

런타임에서 생성되거나 회전하는 자격 증명과 OAuth refresh 자료는 읽기 전용 SecretRef 해석 범위에서 의도적으로 제외됩니다.

## 필수 동작과 우선순위

- ref가 없는 필드: 변경 없음
- ref가 있는 필드: 활성 표면에서는 활성화 중 필수
- 평문과 ref가 모두 있으면, 지원되는 우선순위 경로에서는 ref가 우선
- redaction sentinel `__OPENCLAW_REDACTED__`는 내부 config redaction/복원을 위해 예약되어 있으며, 제출된 config 데이터의 리터럴 값으로는 거부됨

경고 및 audit 신호:

- `SECRETS_REF_OVERRIDES_PLAINTEXT` (런타임 경고)
- `REF_SHADOWED` (`auth-profiles.json` 자격 증명이 `openclaw.json` refs보다 우선할 때의 audit finding)

Google Chat 호환 동작:

- `serviceAccountRef`가 평문 `serviceAccount`보다 우선
- 형제 ref가 설정되면 평문 값은 무시됨

## 활성화 트리거

Secret 활성화는 다음 시점에 실행됩니다.

- 시작(사전 검사 + 최종 활성화)
- Config reload hot-apply 경로
- Config reload restart-check 경로
- `secrets.reload`를 통한 수동 reload
- 활성 표면 SecretRef가 제출된 config payload 내에서 해석 가능한지, 편집을 디스크에 저장하기 전에 확인하는 Gateway config write RPC preflight (`config.set` / `config.apply` / `config.patch`)

활성화 계약:

- 성공하면 스냅샷이 원자적으로 교체됨
- 시작 실패는 gateway 시작을 중단시킴
- 런타임 reload 실패는 마지막 정상 상태 스냅샷을 유지
- Write-RPC preflight 실패는 제출된 config를 거부하고 디스크 config와 활성 런타임 스냅샷을 모두 변경하지 않음
- 아웃바운드 helper/tool 호출에 명시적인 per-call 채널 토큰을 제공해도 SecretRef 활성화는 트리거되지 않음. 활성화 지점은 시작, reload, 명시적 `secrets.reload`에 한정됨

## Degraded 및 recovered 신호

정상 상태 이후 reload 시 활성화가 실패하면 OpenClaw는 degraded secrets 상태에 들어갑니다.

일회성 시스템 이벤트 및 로그 코드:

- `SECRETS_RELOADER_DEGRADED`
- `SECRETS_RELOADER_RECOVERED`

동작:

- Degraded: 런타임은 마지막 정상 상태 스냅샷 유지
- Recovered: 다음 성공적인 활성화 후 한 번만 발생
- 이미 degraded 상태에서 반복 실패하면 경고 로그는 남기지만 이벤트를 과도하게 발생시키지 않음
- 시작 fail-fast는 런타임이 활성화된 적이 없으므로 degraded 이벤트를 발생시키지 않음

## 명령 경로 해석

명령 경로는 gateway snapshot RPC를 통해 지원되는 SecretRef 해석에 옵트인할 수 있습니다.

크게 두 가지 동작이 있습니다.

- 엄격한 명령 경로(예: `openclaw memory`의 원격 메모리 경로, 원격 shared-secret refs가 필요한 `openclaw qr --remote`)는 활성 스냅샷에서 읽고, 필요한 SecretRef를 사용할 수 없으면 fail-fast합니다.
- 읽기 전용 명령 경로(예: `openclaw status`, `openclaw status --all`, `openclaw channels status`, `openclaw channels resolve`, `openclaw security audit`, 읽기 전용 doctor/config repair 흐름)도 활성 스냅샷을 우선 사용하지만, 대상 SecretRef를 해당 명령 경로에서 사용할 수 없을 때는 중단하지 않고 degraded 동작을 합니다.

읽기 전용 동작:

- gateway가 실행 중이면 이러한 명령은 먼저 활성 스냅샷에서 읽습니다.
- gateway 해석이 불완전하거나 gateway를 사용할 수 없으면, 해당 명령 표면에 대해 대상 로컬 폴백을 시도합니다.
- 대상 SecretRef를 여전히 사용할 수 없으면, 명령은 “구성되었지만 이 명령 경로에서는 사용할 수 없음”과 같은 명시적 진단과 함께 degraded 읽기 전용 출력으로 계속 진행합니다.
- 이 degraded 동작은 명령 로컬에만 해당합니다. 런타임 시작, reload, 전송/인증 경로를 약화시키지 않습니다.

기타 참고:

- 백엔드 secret 회전 이후 스냅샷 새로 고침은 `openclaw secrets reload`로 처리합니다.
- 이러한 명령 경로가 사용하는 Gateway RPC 메서드: `secrets.resolve`

## Audit 및 configure 워크플로

기본 운영자 흐름:

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets audit --check
```

### `secrets audit`

findings에는 다음이 포함됩니다.

- 저장 시 평문 값(`openclaw.json`, `auth-profiles.json`, `.env`, 생성된 `agents/*/agent/models.json`)
- 생성된 `models.json` 항목의 평문 민감 provider 헤더 잔여물
- 해석되지 않은 refs
- 우선순위 shadowing (`auth-profiles.json`이 `openclaw.json` refs보다 우선)
- 레거시 잔여물(`auth.json`, OAuth reminders)

Exec 참고:

- 기본적으로 audit는 명령 부작용을 피하기 위해 exec SecretRef 해석 가능성 검사를 건너뜁니다.
- audit 중 exec providers를 실행하려면 `openclaw secrets audit --allow-exec`를 사용하세요.

헤더 잔여물 참고:

- 민감한 provider 헤더 감지는 이름 휴리스틱 기반입니다(일반적인 인증/자격 증명 헤더 이름 및 `authorization`, `x-api-key`, `token`, `secret`, `password`, `credential` 같은 조각).

### `secrets configure`

다음 작업을 수행하는 대화형 도우미입니다.

- 먼저 `secrets.providers` 구성(`env`/`file`/`exec`, 추가/편집/제거)
- 한 에이전트 범위에 대해 `openclaw.json`과 `auth-profiles.json`의 지원되는 secret 보유 필드를 선택 가능
- 대상 picker에서 새 `auth-profiles.json` 매핑을 직접 생성 가능
- SecretRef 세부 정보(`source`, `provider`, `id`) 수집
- preflight 해석 수행
- 즉시 적용 가능

Exec 참고:

- `--allow-exec`가 설정되지 않으면 preflight는 exec SecretRef 검사를 건너뜁니다.
- `configure --apply`에서 바로 적용하고 계획에 exec refs/providers가 포함되어 있다면, apply 단계에서도 `--allow-exec`를 유지하세요.

유용한 모드:

- `openclaw secrets configure --providers-only`
- `openclaw secrets configure --skip-provider-setup`
- `openclaw secrets configure --agent <id>`

`configure` apply 기본값:

- 대상 provider에 대해 `auth-profiles.json`의 일치하는 정적 자격 증명을 스크러빙
- `auth.json`의 레거시 정적 `api_key` 항목을 스크러빙
- `<config-dir>/.env`의 일치하는 알려진 secret 줄을 스크러빙

### `secrets apply`

저장된 계획 적용:

```bash
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --allow-exec
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run --allow-exec
```

Exec 참고:

- dry-run은 `--allow-exec`가 설정되지 않으면 exec 검사를 건너뜁니다.
- 쓰기 모드는 `--allow-exec`가 설정되지 않으면 exec SecretRefs/providers를 포함한 계획을 거부합니다.

엄격한 대상/경로 계약 세부 정보와 정확한 거부 규칙은 다음을 참조하세요.

- [Secrets Apply Plan Contract](/gateway/secrets-plan-contract)

## 단방향 안전 정책

OpenClaw는 과거 평문 secret 값을 포함하는 rollback 백업을 의도적으로 기록하지 않습니다.

안전 모델:

- 쓰기 모드 전에 preflight가 반드시 성공해야 함
- 커밋 전에 런타임 활성화가 검증됨
- apply는 원자적 파일 교체와 실패 시 best-effort 복원을 사용해 파일을 업데이트함

## 레거시 인증 호환 참고

정적 자격 증명의 경우, 런타임은 더 이상 평문 레거시 인증 저장소에 의존하지 않습니다.

- 런타임 자격 증명 소스는 해석된 메모리 내 스냅샷입니다.
- 레거시 정적 `api_key` 항목은 발견되면 스크러빙됩니다.
- OAuth 관련 호환 동작은 별도로 유지됩니다.

## Web UI 참고

일부 SecretInput union은 form 모드보다 raw editor 모드에서 구성하기 더 쉽습니다.

## 관련 문서

- CLI 명령: [secrets](/cli/secrets)
- 계획 계약 세부 정보: [Secrets Apply Plan Contract](/gateway/secrets-plan-contract)
- 자격 증명 표면: [SecretRef 자격 증명 표면](/reference/secretref-credential-surface)
- 인증 설정: [인증](/gateway/authentication)
- 보안 태세: [보안](/gateway/security)
- 환경 변수 우선순위: [환경 변수](/help/environment)
