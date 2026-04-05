---
read_when:
    - 리포지토리의 스크립트를 실행할 때
    - ./scripts 아래의 스크립트를 추가하거나 변경할 때
summary: '리포지토리 스크립트: 목적, 범위 및 안전 참고 사항'
title: 스크립트
x-i18n:
    generated_at: "2026-04-05T12:44:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: de53d64d91c564931bdd4e8b9f4a8e88646332a07cc2a6bf1d517b89debb29cd
    source_path: help/scripts.md
    workflow: 15
---

# 스크립트

`scripts/` 디렉터리에는 로컬 워크플로와 운영 작업을 위한 헬퍼 스크립트가 들어 있습니다.
작업이 스크립트와 명확하게 연결되어 있을 때는 이를 사용하고, 그렇지 않으면 CLI를 우선하세요.

## 규칙

- 스크립트는 문서나 릴리스 체크리스트에서 참조되지 않는 한 **선택 사항**입니다.
- 사용 가능한 경우 CLI 표면을 우선하세요(예: 인증 모니터링은 `openclaw models status --check` 사용).
- 스크립트는 호스트별일 수 있다고 가정하고, 새 머신에서 실행하기 전에 내용을 읽어보세요.

## 인증 모니터링 스크립트

인증 모니터링은 [인증](/gateway/authentication)에서 다룹니다. `scripts/` 아래의 스크립트는 systemd/Termux 휴대폰 워크플로를 위한 선택적 추가 기능입니다.

## 스크립트를 추가할 때

- 스크립트는 집중된 목적을 갖고 문서화되도록 유지하세요.
- 관련 문서에 짧은 항목을 추가하세요(없다면 새로 만드세요).
