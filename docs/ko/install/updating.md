---
read_when:
    - OpenClaw를 업데이트하는 경우
    - 업데이트 후 문제가 발생한 경우
summary: OpenClaw를 안전하게 업데이트하는 방법(전역 설치 또는 소스), 그리고 롤백 전략
title: 업데이트
x-i18n:
    generated_at: "2026-04-05T12:47:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: b40429d38ca851be4fdf8063ed425faf4610a4b5772703e0481c5f1fb588ba58
    source_path: install/updating.md
    workflow: 15
---

# 업데이트

OpenClaw를 최신 상태로 유지하세요.

## 권장: `openclaw update`

가장 빠른 업데이트 방법입니다. 설치 유형(npm 또는 git)을 감지하고, 최신 버전을 가져오고, `openclaw doctor`를 실행한 다음 Gateway를 재시작합니다.

```bash
openclaw update
```

채널을 전환하거나 특정 버전을 대상으로 하려면:

```bash
openclaw update --channel beta
openclaw update --tag main
openclaw update --dry-run   # 적용 없이 미리 보기
```

`--channel beta`는 beta를 우선 사용하지만, beta 태그가 없거나 최신 stable 릴리스보다 오래된 경우 런타임은 stable/latest로 대체합니다. 일회성 패키지 업데이트에 원시 npm beta dist-tag를 사용하려면 `--tag beta`를 사용하세요.

채널 의미는 [Development channels](/install/development-channels)를 참조하세요.

## 대안: 설치 프로그램 다시 실행

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

온보딩을 건너뛰려면 `--no-onboard`를 추가하세요. 소스 설치의 경우 `--install-method git --no-onboard`를 전달하세요.

## 대안: 수동 npm, pnpm 또는 bun

```bash
npm i -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

```bash
bun add -g openclaw@latest
```

## 자동 업데이트 도구

자동 업데이트 도구는 기본적으로 꺼져 있습니다. `~/.openclaw/openclaw.json`에서 활성화하세요.

```json5
{
  update: {
    channel: "stable",
    auto: {
      enabled: true,
      stableDelayHours: 6,
      stableJitterHours: 12,
      betaCheckIntervalHours: 1,
    },
  },
}
```

| Channel  | 동작                                                                                                      |
| -------- | ------------------------------------------------------------------------------------------------------------- |
| `stable` | `stableDelayHours`만큼 기다린 후, `stableJitterHours` 전반에 걸쳐 결정적 지터와 함께 적용합니다(점진적 롤아웃). |
| `beta`   | `betaCheckIntervalHours`마다(기본값: 매시간) 확인하고 즉시 적용합니다.                              |
| `dev`    | 자동 적용 없음. `openclaw update`를 수동으로 사용하세요.                                                           |

Gateway는 시작 시 업데이트 힌트도 로그에 남깁니다(`update.checkOnStart: false`로 비활성화).

## 업데이트 후

<Steps>

### doctor 실행

```bash
openclaw doctor
```

config를 마이그레이션하고, DM 정책을 감사하며, gateway 상태를 확인합니다. 자세한 내용: [Doctor](/gateway/doctor)

### Gateway 재시작

```bash
openclaw gateway restart
```

### 확인

```bash
openclaw health
```

</Steps>

## 롤백

### 버전 고정(npm)

```bash
npm i -g openclaw@<version>
openclaw doctor
openclaw gateway restart
```

팁: `npm view openclaw version`은 현재 게시된 버전을 보여줍니다.

### 커밋 고정(소스)

```bash
git fetch origin
git checkout "$(git rev-list -n 1 --before=\"2026-01-01\" origin/main)"
pnpm install && pnpm build
openclaw gateway restart
```

최신으로 돌아가려면: `git checkout main && git pull`.

## 막혔을 때

- `openclaw doctor`를 다시 실행하고 출력을 주의 깊게 읽어 보세요.
- 확인: [Troubleshooting](/gateway/troubleshooting)
- Discord에서 문의: [https://discord.gg/clawd](https://discord.gg/clawd)

## 관련

- [Install Overview](/install) — 모든 설치 방법
- [Doctor](/gateway/doctor) — 업데이트 후 상태 확인
- [Migrating](/install/migrating) — 주요 버전 마이그레이션 가이드
