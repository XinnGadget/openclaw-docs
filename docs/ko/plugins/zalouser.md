---
read_when:
    - OpenClaw에서 Zalo Personal(비공식) 지원을 사용하려고 할 때
    - zalouser plugin을 구성하거나 개발하고 있을 때
summary: 'Zalo Personal plugin: 네이티브 `zca-js`를 통한 QR 로그인 + 메시징(plugin 설치 + channel config + tool)'
title: Zalo Personal Plugin
x-i18n:
    generated_at: "2026-04-05T12:50:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3218c3ee34f36466d952aec1b479d451a6235c7c46918beb28698234a7fd0968
    source_path: plugins/zalouser.md
    workflow: 15
---

# Zalo Personal (plugin)

네이티브 `zca-js`를 사용해 일반 Zalo 사용자 계정을 자동화하는 OpenClaw용 Zalo Personal 지원 plugin입니다.

> **Warning:** 비공식 자동화는 계정 정지/차단으로 이어질 수 있습니다. 사용에 따른 책임은 본인에게 있습니다.

## 명명

채널 ID는 `zalouser`입니다. 이는 **개인 Zalo 사용자 계정**(비공식)을 자동화한다는 점을 명확히 하기 위함입니다. `zalo`는 향후 공식 Zalo API 통합 가능성을 위해 예약해 둡니다.

## 실행 위치

이 plugin은 **Gateway 프로세스 내부에서** 실행됩니다.

원격 Gateway를 사용한다면, **Gateway가 실행되는 머신**에 설치/구성한 뒤 Gateway를 재시작하세요.

외부 `zca`/`openzca` CLI 바이너리는 필요하지 않습니다.

## 설치

### 옵션 A: npm에서 설치

```bash
openclaw plugins install @openclaw/zalouser
```

이후 Gateway를 재시작하세요.

### 옵션 B: 로컬 폴더에서 설치 (개발)

```bash
PLUGIN_SRC=./path/to/local/zalouser-plugin
openclaw plugins install "$PLUGIN_SRC"
cd "$PLUGIN_SRC" && pnpm install
```

이후 Gateway를 재시작하세요.

## 구성

채널 구성은 `plugins.entries.*`가 아니라 `channels.zalouser` 아래에 있습니다:

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      dmPolicy: "pairing",
    },
  },
}
```

## CLI

```bash
openclaw channels login --channel zalouser
openclaw channels logout --channel zalouser
openclaw channels status --probe
openclaw message send --channel zalouser --target <threadId> --message "Hello from OpenClaw"
openclaw directory peers list --channel zalouser --query "name"
```

## 에이전트 도구

도구 이름: `zalouser`

작업: `send`, `image`, `link`, `friends`, `groups`, `me`, `status`

채널 메시지 작업은 메시지 반응용 `react`도 지원합니다.
