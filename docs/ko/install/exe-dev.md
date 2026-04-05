---
read_when:
    - Gateway용으로 저렴한 상시 실행 Linux 호스트를 원하는 경우
    - 직접 VPS를 운영하지 않고 원격 Control UI 액세스를 원하는 경우
summary: 원격 액세스를 위해 exe.dev(VM + HTTPS 프록시)에서 OpenClaw Gateway 실행
title: exe.dev
x-i18n:
    generated_at: "2026-04-05T12:45:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: ff95b6f35b95df35c1b0cae3215647eefe88d2b7f19923868385036cc0dbdbf1
    source_path: install/exe-dev.md
    workflow: 15
---

# exe.dev

목표: exe.dev VM에서 OpenClaw Gateway를 실행하고, 노트북에서 `https://<vm-name>.exe.xyz`를 통해 접근 가능하게 합니다.

이 페이지는 exe.dev의 기본 **exeuntu** 이미지를 기준으로 합니다. 다른 배포판을 선택했다면 패키지를 그에 맞게 바꾸세요.

## 초보자용 빠른 경로

1. [https://exe.new/openclaw](https://exe.new/openclaw)
2. 필요에 따라 auth 키/토큰을 입력합니다
3. VM 옆의 "Agent"를 클릭하고 Shelley가 프로비저닝을 끝낼 때까지 기다립니다
4. `https://<vm-name>.exe.xyz/`를 열고 구성된 공유 시크릿으로 인증합니다(이 가이드는 기본적으로 token auth를 사용하지만 `gateway.auth.mode`를 바꾸면 password auth도 작동합니다)
5. `openclaw devices approve <requestId>`로 대기 중인 디바이스 페어링 요청을 승인합니다

## 필요한 것

- exe.dev 계정
- [exe.dev](https://exe.dev) 가상 머신에 대한 `ssh exe.dev` 액세스(선택 사항)

## Shelley를 사용한 자동 설치

[exe.dev](https://exe.dev)의 agent인 Shelley는
우리 프롬프트를 사용해 OpenClaw를 즉시 설치할 수 있습니다. 사용된 프롬프트는 아래와 같습니다.

```
Set up OpenClaw (https://docs.openclaw.ai/install) on this VM. Use the non-interactive and accept-risk flags for openclaw onboarding. Add the supplied auth or token as needed. Configure nginx to forward from the default port 18789 to the root location on the default enabled site config, making sure to enable Websocket support. Pairing is done by "openclaw devices list" and "openclaw devices approve <request id>". Make sure the dashboard shows that OpenClaw's health is OK. exe.dev handles forwarding from port 8000 to port 80/443 and HTTPS for us, so the final "reachable" should be <vm-name>.exe.xyz, without port specification.
```

## 수동 설치

## 1) VM 생성

사용자 디바이스에서:

```bash
ssh exe.dev new
```

그런 다음 연결합니다:

```bash
ssh <vm-name>.exe.xyz
```

팁: 이 VM은 **상태 유지형**으로 유지하세요. OpenClaw는 `openclaw.json`, agent별
`auth-profiles.json`, 세션, 채널/provider 상태를
`~/.openclaw/` 아래에 저장하고, 워크스페이스는 `~/.openclaw/workspace/` 아래에 저장합니다.

## 2) 사전 요구 사항 설치(VM에서)

```bash
sudo apt-get update
sudo apt-get install -y git curl jq ca-certificates openssl
```

## 3) OpenClaw 설치

OpenClaw 설치 스크립트를 실행합니다:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

## 4) OpenClaw를 포트 8000으로 프록시하도록 nginx 설정

`/etc/nginx/sites-enabled/default`를 다음 내용으로 편집합니다.

```
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    listen 8000;
    listen [::]:8000;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings for long-lived connections
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

클라이언트가 제공한 체인을 보존하는 대신 포워딩 헤더를 덮어쓰세요.
OpenClaw는 명시적으로 구성된 프록시에서만 전달된 IP 메타데이터를 신뢰하며,
추가형 `X-Forwarded-For` 체인은 보안 강화 관점에서 위험으로 간주됩니다.

## 5) OpenClaw에 액세스하고 권한 부여

`https://<vm-name>.exe.xyz/`에 접속합니다(온보딩의 Control UI 출력 참조). auth를 요청하면
VM에 구성된 공유 시크릿을 붙여넣으세요. 이 가이드는 token auth를 사용하므로, `gateway.auth.token`은
`openclaw config get gateway.auth.token`으로 가져오세요(또는 `openclaw doctor --generate-gateway-token`으로 생성).
gateway를 password auth로 바꿨다면 대신 `gateway.auth.password` / `OPENCLAW_GATEWAY_PASSWORD`를 사용하세요.
디바이스는 `openclaw devices list`와 `openclaw devices approve <requestId>`로 승인하세요. 확실하지 않다면 브라우저에서 Shelley를 사용하세요!

## 원격 액세스

원격 액세스는 [exe.dev](https://exe.dev)의 인증으로 처리됩니다. 기본적으로
포트 8000의 HTTP 트래픽은 이메일 인증과 함께
`https://<vm-name>.exe.xyz`로 전달됩니다.

## 업데이트

```bash
npm i -g openclaw@latest
openclaw doctor
openclaw gateway restart
openclaw health
```

가이드: [Updating](/install/updating)
