---
read_when:
    - 첫 번째 에이전트 실행 시 무엇이 일어나는지 이해하려는 경우
    - 부트스트래핑 파일이 어디에 있는지 설명하는 경우
    - 온보딩 정체성 설정을 디버깅하는 경우
sidebarTitle: Bootstrapping
summary: 워크스페이스와 정체성 파일을 초기화하는 에이전트 부트스트래핑 절차
title: 에이전트 부트스트래핑
x-i18n:
    generated_at: "2026-04-05T12:54:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4a08b5102f25c6c4bcdbbdd44384252a9e537b245a7b070c4961a72b4c6c6601
    source_path: start/bootstrapping.md
    workflow: 15
---

# 에이전트 부트스트래핑

부트스트래핑은 에이전트 워크스페이스를 준비하고 정체성 세부 정보를 수집하는 **첫 실행** 절차입니다. 이는 온보딩 후, 에이전트가 처음 시작될 때 수행됩니다.

## 부트스트래핑이 하는 일

첫 번째 에이전트 실행 시 OpenClaw는 워크스페이스(기본값
`~/.openclaw/workspace`)를 부트스트랩합니다:

- `AGENTS.md`, `BOOTSTRAP.md`, `IDENTITY.md`, `USER.md`를 시드합니다.
- 짧은 질의응답 절차를 실행합니다(한 번에 한 질문씩).
- 정체성과 환경설정을 `IDENTITY.md`, `USER.md`, `SOUL.md`에 기록합니다.
- 완료되면 `BOOTSTRAP.md`를 제거하여 한 번만 실행되도록 합니다.

## 실행 위치

부트스트래핑은 항상 **gateway host**에서 실행됩니다. macOS 앱이
원격 Gateway에 연결되는 경우, 워크스페이스와 부트스트래핑 파일은 해당 원격
머신에 있습니다.

<Note>
Gateway가 다른 머신에서 실행되는 경우, 워크스페이스 파일은 gateway
host에서 편집하세요(예: `user@gateway-host:~/.openclaw/workspace`).
</Note>

## 관련 문서

- macOS 앱 온보딩: [온보딩](/start/onboarding)
- 워크스페이스 레이아웃: [에이전트 워크스페이스](/ko/concepts/agent-workspace)
