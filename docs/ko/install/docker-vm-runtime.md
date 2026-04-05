---
read_when:
    - Docker로 클라우드 VM에 OpenClaw를 배포하는 경우
    - 공통 바이너리 bake, 영속성, 업데이트 흐름이 필요한 경우
summary: 장기 실행 OpenClaw Gateway 호스트를 위한 공통 Docker VM 런타임 단계
title: Docker VM Runtime
x-i18n:
    generated_at: "2026-04-05T12:45:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 854403a48fe15a88cc9befb9bebe657f1a7c83f1df2ebe2346fac9a6e4b16992
    source_path: install/docker-vm-runtime.md
    workflow: 15
---

# Docker VM Runtime

GCP, Hetzner 및 유사한 VPS provider와 같은 VM 기반 Docker 설치를 위한 공통 런타임 단계입니다.

## 필요한 바이너리를 이미지에 bake하기

실행 중인 컨테이너 안에서 바이너리를 설치하는 것은 함정입니다.
런타임에 설치한 모든 것은 재시작 시 사라집니다.

Skills에 필요한 모든 외부 바이너리는 이미지 빌드 시점에 설치되어야 합니다.

아래 예시는 세 가지 일반적인 바이너리만 보여줍니다.

- Gmail 액세스용 `gog`
- Google Places용 `goplaces`
- WhatsApp용 `wacli`

이들은 예시일 뿐이며 완전한 목록이 아닙니다.
동일한 패턴으로 필요한 만큼 바이너리를 설치할 수 있습니다.

나중에 추가 바이너리에 의존하는 새 Skills를 추가하면 다음을 반드시 해야 합니다.

1. Dockerfile 업데이트
2. 이미지 재빌드
3. 컨테이너 재시작

**예시 Dockerfile**

```dockerfile
FROM node:24-bookworm

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

# 예시 바이너리 1: Gmail CLI
RUN curl -L https://github.com/steipete/gog/releases/latest/download/gog_Linux_x86_64.tar.gz \
  | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/gog

# 예시 바이너리 2: Google Places CLI
RUN curl -L https://github.com/steipete/goplaces/releases/latest/download/goplaces_Linux_x86_64.tar.gz \
  | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/goplaces

# 예시 바이너리 3: WhatsApp CLI
RUN curl -L https://github.com/steipete/wacli/releases/latest/download/wacli_Linux_x86_64.tar.gz \
  | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/wacli

# 아래에 같은 패턴으로 더 많은 바이너리 추가

WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY ui/package.json ./ui/package.json
COPY scripts ./scripts

RUN corepack enable
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build
RUN pnpm ui:install
RUN pnpm ui:build

ENV NODE_ENV=production

CMD ["node","dist/index.js"]
```

<Note>
위 다운로드 URL은 x86_64 (amd64)용입니다. ARM 기반 VM(예: Hetzner ARM, GCP Tau T2A)의 경우 각 도구의 릴리스 페이지에서 적절한 ARM64 변형 URL로 교체하세요.
</Note>

## 빌드 및 실행

```bash
docker compose build
docker compose up -d openclaw-gateway
```

빌드 중 `pnpm install --frozen-lockfile` 단계에서 `Killed` 또는 `exit code 137`로 실패하면 VM 메모리가 부족한 것입니다.
다시 시도하기 전에 더 큰 머신 클래스를 사용하세요.

바이너리 확인:

```bash
docker compose exec openclaw-gateway which gog
docker compose exec openclaw-gateway which goplaces
docker compose exec openclaw-gateway which wacli
```

예상 출력:

```
/usr/local/bin/gog
/usr/local/bin/goplaces
/usr/local/bin/wacli
```

Gateway 확인:

```bash
docker compose logs -f openclaw-gateway
```

예상 출력:

```
[gateway] listening on ws://0.0.0.0:18789
```

## 무엇이 어디에 영속되는가

OpenClaw는 Docker에서 실행되지만, Docker가 기준 정보원은 아닙니다.
모든 장기 상태는 재시작, 재빌드, 재부팅 후에도 유지되어야 합니다.

| 구성 요소 | 위치 | 영속화 메커니즘 | 참고 |
| ------------------- | --------------------------------- | ---------------------- | ------------------------------------------------------------- |
| Gateway config | `/home/node/.openclaw/` | 호스트 볼륨 마운트 | `openclaw.json`, `.env` 포함 |
| 모델 auth profiles | `/home/node/.openclaw/agents/` | 호스트 볼륨 마운트 | `agents/<agentId>/agent/auth-profiles.json` (OAuth, API 키) |
| Skill configs | `/home/node/.openclaw/skills/` | 호스트 볼륨 마운트 | Skill 수준 상태 |
| 에이전트 workspace | `/home/node/.openclaw/workspace/` | 호스트 볼륨 마운트 | 코드 및 에이전트 아티팩트 |
| WhatsApp 세션 | `/home/node/.openclaw/` | 호스트 볼륨 마운트 | QR 로그인 유지 |
| Gmail keyring | `/home/node/.openclaw/` | 호스트 볼륨 + 비밀번호 | `GOG_KEYRING_PASSWORD` 필요 |
| 외부 바이너리 | `/usr/local/bin/` | Docker 이미지 | 빌드 시점에 bake되어야 함 |
| Node 런타임 | 컨테이너 파일시스템 | Docker 이미지 | 이미지 빌드마다 재빌드 |
| OS 패키지 | 컨테이너 파일시스템 | Docker 이미지 | 런타임에 설치하지 말 것 |
| Docker 컨테이너 | 일시적 | 재시작 가능 | 삭제해도 안전 |

## 업데이트

VM에서 OpenClaw를 업데이트하려면:

```bash
git pull
docker compose build
docker compose up -d
```
