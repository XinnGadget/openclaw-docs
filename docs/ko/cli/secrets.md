---
read_when:
    - 런타임에서 secret ref를 다시 해석하는 경우
    - 평문 잔여물과 해석되지 않은 ref를 감사하는 경우
    - SecretRef를 구성하고 단방향 스크럽 변경 사항을 적용하는 경우
summary: '`openclaw secrets`용 CLI 참조(reload, audit, configure, apply)'
title: secrets
x-i18n:
    generated_at: "2026-04-05T12:39:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: f436ba089d752edb766c0a3ce746ee6bca1097b22c9b30e3d9715cb0bb50bf47
    source_path: cli/secrets.md
    workflow: 15
---

# `openclaw secrets`

`openclaw secrets`를 사용해 SecretRef를 관리하고 활성 런타임 스냅샷을 정상 상태로 유지하세요.

명령 역할:

- `reload`: ref를 다시 해석하고 전체 성공 시에만 런타임 스냅샷을 교체하는 gateway RPC(`secrets.reload`)입니다(config 쓰기 없음).
- `audit`: 평문, 해석되지 않은 ref, 우선순위 드리프트를 대상으로 구성/auth/생성된 모델 저장소와 레거시 잔여물을 읽기 전용으로 검사합니다(`--allow-exec`가 설정되지 않으면 exec ref는 건너뜀).
- `configure`: 공급자 설정, 대상 매핑, 사전 점검을 위한 대화형 플래너입니다(TTY 필요).
- `apply`: 저장된 계획을 실행합니다(검증 전용은 `--dry-run`; dry-run은 기본적으로 exec 검사를 건너뛰고, 쓰기 모드는 `--allow-exec`가 설정되지 않으면 exec가 포함된 계획을 거부함). 이후 대상 평문 잔여물을 스크럽합니다.

권장 운영자 루프:

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
openclaw secrets audit --check
openclaw secrets reload
```

계획에 `exec` SecretRef/공급자가 포함되어 있다면 dry-run과 실제 쓰기 apply 명령 모두에 `--allow-exec`를 전달하세요.

CI/게이트용 종료 코드 참고:

- `audit --check`는 항목이 발견되면 `1`을 반환합니다.
- 해석되지 않은 ref는 `2`를 반환합니다.

관련 문서:

- Secrets 가이드: [Secrets Management](/gateway/secrets)
- 자격 증명 표면: [SecretRef Credential Surface](/reference/secretref-credential-surface)
- 보안 가이드: [Security](/gateway/security)

## 런타임 스냅샷 다시 로드

secret ref를 다시 해석하고 런타임 스냅샷을 원자적으로 교체합니다.

```bash
openclaw secrets reload
openclaw secrets reload --json
openclaw secrets reload --url ws://127.0.0.1:18789 --token <token>
```

참고:

- gateway RPC 메서드 `secrets.reload`를 사용합니다.
- 해석에 실패하면 gateway는 마지막으로 알려진 정상 스냅샷을 유지하고 오류를 반환합니다(부분 활성화 없음).
- JSON 응답에는 `warningCount`가 포함됩니다.

옵션:

- `--url <url>`
- `--token <token>`
- `--timeout <ms>`
- `--json`

## 감사

OpenClaw 상태에서 다음을 검사합니다:

- 평문 secret 저장소
- 해석되지 않은 ref
- 우선순위 드리프트(`auth-profiles.json` 자격 증명이 `openclaw.json` ref를 가림)
- 생성된 `agents/*/agent/models.json` 잔여물(공급자 `apiKey` 값 및 민감한 공급자 헤더)
- 레거시 잔여물(레거시 auth 저장소 항목, OAuth 알림)

헤더 잔여물 참고:

- 민감한 공급자 헤더 감지는 이름 휴리스틱 기반입니다(일반적인 auth/자격 증명 헤더 이름과 `authorization`, `x-api-key`, `token`, `secret`, `password`, `credential` 같은 조각).

```bash
openclaw secrets audit
openclaw secrets audit --check
openclaw secrets audit --json
openclaw secrets audit --allow-exec
```

종료 동작:

- `--check`는 항목이 발견되면 0이 아닌 값으로 종료합니다.
- 해석되지 않은 ref는 더 높은 우선순위의 0이 아닌 종료 코드를 사용합니다.

보고서 형태의 주요 항목:

- `status`: `clean | findings | unresolved`
- `resolution`: `refsChecked`, `skippedExecRefs`, `resolvabilityComplete`
- `summary`: `plaintextCount`, `unresolvedRefCount`, `shadowedRefCount`, `legacyResidueCount`
- finding 코드:
  - `PLAINTEXT_FOUND`
  - `REF_UNRESOLVED`
  - `REF_SHADOWED`
  - `LEGACY_RESIDUE`

## 구성(대화형 도우미)

공급자 및 SecretRef 변경 사항을 대화형으로 빌드하고, 사전 점검을 실행한 뒤, 선택적으로 적용합니다:

```bash
openclaw secrets configure
openclaw secrets configure --plan-out /tmp/openclaw-secrets-plan.json
openclaw secrets configure --apply --yes
openclaw secrets configure --providers-only
openclaw secrets configure --skip-provider-setup
openclaw secrets configure --agent ops
openclaw secrets configure --json
```

흐름:

- 먼저 공급자 설정(`secrets.providers` 별칭에 대해 `add/edit/remove`)
- 다음으로 자격 증명 매핑(필드 선택 후 `{source, provider, id}` ref 할당)
- 마지막으로 사전 점검 및 선택적 적용

플래그:

- `--providers-only`: `secrets.providers`만 구성하고 자격 증명 매핑은 건너뜁니다.
- `--skip-provider-setup`: 공급자 설정을 건너뛰고 자격 증명을 기존 공급자에 매핑합니다.
- `--agent <id>`: `auth-profiles.json` 대상 검색 및 쓰기를 하나의 agent 저장소 범위로 제한합니다.
- `--allow-exec`: 사전 점검/apply 중 exec SecretRef 검사를 허용합니다(공급자 명령을 실행할 수 있음).

참고:

- 대화형 TTY가 필요합니다.
- `--providers-only`와 `--skip-provider-setup`은 함께 사용할 수 없습니다.
- `configure`는 `openclaw.json`의 secret 보유 필드와 선택한 agent 범위의 `auth-profiles.json`을 대상으로 합니다.
- `configure`는 picker 흐름에서 새 `auth-profiles.json` 매핑을 직접 생성하는 것을 지원합니다.
- 정식 지원 표면: [SecretRef Credential Surface](/reference/secretref-credential-surface).
- 적용 전에 사전 점검 해석을 수행합니다.
- 사전 점검/apply에 exec ref가 포함되면 두 단계 모두에서 `--allow-exec`를 유지하세요.
- 생성된 계획은 기본적으로 스크럽 옵션(`scrubEnv`, `scrubAuthProfilesForProviderTargets`, `scrubLegacyAuthJson` 모두 활성화됨)을 사용합니다.
- 스크럽된 평문 값에 대한 apply 경로는 단방향입니다.
- `--apply` 없이도 CLI는 사전 점검 후 `Apply this plan now?`를 계속 묻습니다.
- `--apply`를 사용할 때(`--yes` 없음) CLI는 되돌릴 수 없는 추가 확인을 요청합니다.
- `--json`은 계획 + 사전 점검 보고서를 출력하지만, 이 명령은 여전히 대화형 TTY가 필요합니다.

Exec 공급자 안전 참고:

- Homebrew 설치는 종종 `/opt/homebrew/bin/*` 아래의 심볼릭 링크 바이너리를 노출합니다.
- 신뢰된 패키지 관리자 경로에 필요할 때만 `allowSymlinkCommand: true`를 설정하고, `trustedDirs`(예: `["/opt/homebrew"]`)와 함께 사용하세요.
- Windows에서 공급자 경로에 대한 ACL 검증을 사용할 수 없으면 OpenClaw는 fail-closed로 동작합니다. 신뢰된 경로에 한해, 해당 공급자에 `allowInsecurePath: true`를 설정해 경로 보안 검사를 우회할 수 있습니다.

## 저장된 계획 적용

이전에 생성한 계획을 적용하거나 사전 점검합니다:

```bash
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --allow-exec
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run --allow-exec
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --json
```

Exec 동작:

- `--dry-run`은 파일을 쓰지 않고 사전 점검을 검증합니다.
- exec SecretRef 검사는 dry-run에서 기본적으로 건너뜁니다.
- 쓰기 모드는 `--allow-exec`가 설정되지 않으면 exec SecretRef/공급자가 포함된 계획을 거부합니다.
- 어느 모드에서든 exec 공급자 검사/실행을 허용하려면 `--allow-exec`를 사용하세요.

계획 계약 세부 사항(허용되는 대상 경로, 유효성 검사 규칙, 실패 의미 체계):

- [Secrets Apply Plan Contract](/gateway/secrets-plan-contract)

`apply`가 업데이트할 수 있는 항목:

- `openclaw.json`(SecretRef 대상 + 공급자 upsert/delete)
- `auth-profiles.json`(공급자 대상 스크럽)
- 레거시 `auth.json` 잔여물
- 값이 마이그레이션된 `~/.openclaw/.env`의 알려진 secret 키

## 롤백 백업이 없는 이유

`secrets apply`는 이전 평문 값을 포함하는 롤백 백업을 의도적으로 작성하지 않습니다.

안전성은 엄격한 사전 점검 + 실패 시 최선 시도의 메모리 내 복원을 포함한 거의 원자적인 apply에서 나옵니다.

## 예시

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets audit --check
```

`audit --check`가 여전히 평문 항목을 보고하면, 보고된 나머지 대상 경로를 업데이트한 뒤 감사를 다시 실행하세요.
