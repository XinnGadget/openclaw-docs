---
read_when:
    - Linux 컴패니언 앱 상태를 찾고 있을 때
    - 플랫폼 지원 범위나 기여를 계획할 때
summary: Linux 지원 + 컴패니언 앱 상태
title: Linux 앱
x-i18n:
    generated_at: "2026-04-05T12:48:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5dbfc89eb65e04347479fc6c9a025edec902fb0c544fb8d5bd09c24558ea03b1
    source_path: platforms/linux.md
    workflow: 15
---

# Linux 앱

Gateway는 Linux에서 완전히 지원됩니다. **Node가 권장 런타임**입니다.
Bun은 Gateway에 권장되지 않습니다(WhatsApp/Telegram 버그 때문).

네이티브 Linux 컴패니언 앱은 계획되어 있습니다. 직접 만들어 보고 싶다면 기여를 환영합니다.

## 초보자용 빠른 경로(VPS)

1. Node 24 설치(권장, 호환성을 위해 Node 22 LTS(현재 `22.14+`)도 계속 동작)
2. `npm i -g openclaw@latest`
3. `openclaw onboard --install-daemon`
4. 노트북에서: `ssh -N -L 18789:127.0.0.1:18789 <user>@<host>`
5. `http://127.0.0.1:18789/`를 열고 구성된 공유 비밀로 인증(기본값은 token, `gateway.auth.mode: "password"`를 설정했다면 password)

전체 Linux 서버 가이드: [Linux Server](/vps). 단계별 VPS 예시: [exe.dev](/install/exe-dev)

## 설치

- [Getting Started](/ko/start/getting-started)
- [Install & updates](/install/updating)
- 선택적 흐름: [Bun (experimental)](/install/bun), [Nix](/install/nix), [Docker](/install/docker)

## Gateway

- [Gateway 운영 가이드](/gateway)
- [Configuration](/gateway/configuration)

## Gateway 서비스 설치 (CLI)

다음 중 하나를 사용하세요:

```
openclaw onboard --install-daemon
```

또는:

```
openclaw gateway install
```

또는:

```
openclaw configure
```

프롬프트가 나오면 **Gateway service**를 선택하세요.

복구/마이그레이션:

```
openclaw doctor
```

## 시스템 제어 (systemd user unit)

OpenClaw는 기본적으로 systemd **user** 서비스를 설치합니다. 공유 또는 항상 켜져 있어야 하는 서버에는 **system** 서비스를 사용하세요. `openclaw gateway install`과 `openclaw onboard --install-daemon`은 이미 현재의 canonical unit을 렌더링해 주므로, 사용자 지정 system/service-manager 설정이 필요한 경우에만 직접 작성하세요. 전체 서비스 가이드는 [Gateway 운영 가이드](/gateway)에 있습니다.

최소 설정:

`~/.config/systemd/user/openclaw-gateway[-<profile>].service`를 생성하세요:

```
[Unit]
Description=OpenClaw Gateway (profile: <profile>, v<version>)
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group

[Install]
WantedBy=default.target
```

활성화:

```
systemctl --user enable --now openclaw-gateway[-<profile>].service
```
