---
read_when:
    - Tailscale + CoreDNS를 통한 광역 검색(DNS-SD)을 원할 때
    - You’re setting up split DNS for a custom discovery domain (example: openclaw.internal)
summary: '`openclaw dns`용 CLI 참조(광역 검색 도우미)'
title: dns
x-i18n:
    generated_at: "2026-04-05T12:37:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4831fbb7791adfed5195bc4ba36bb248d2bc8830958334211d3c96f824617927
    source_path: cli/dns.md
    workflow: 15
---

# `openclaw dns`

광역 검색(Tailscale + CoreDNS)을 위한 DNS 도우미입니다. 현재는 macOS + Homebrew CoreDNS에 중점을 두고 있습니다.

관련 문서:

- Gateway 검색: [검색](/gateway/discovery)
- 광역 검색 구성: [구성](/gateway/configuration)

## 설정

```bash
openclaw dns setup
openclaw dns setup --domain openclaw.internal
openclaw dns setup --apply
```

## `dns setup`

유니캐스트 DNS-SD 검색을 위한 CoreDNS 설정을 계획하거나 적용합니다.

옵션:

- `--domain <domain>`: 광역 검색 도메인(예: `openclaw.internal`)
- `--apply`: CoreDNS 구성을 설치하거나 업데이트하고 서비스를 재시작합니다(`sudo` 필요, macOS 전용)

표시 내용:

- 확인된 검색 도메인
- 존 파일 경로
- 현재 tailnet IP
- 권장 `openclaw.json` 검색 구성
- 설정할 Tailscale Split DNS 네임서버/도메인 값

참고:

- `--apply` 없이 실행하면 이 명령은 계획 도우미로만 동작하며 권장 설정을 출력합니다.
- `--domain`을 생략하면 OpenClaw는 config의 `discovery.wideArea.domain`을 사용합니다.
- `--apply`는 현재 macOS에서만 지원되며 Homebrew CoreDNS를 전제로 합니다.
- `--apply`는 필요 시 존 파일을 부트스트랩하고, CoreDNS import stanza가 존재하도록 보장하며, `coredns` brew 서비스를 재시작합니다.
