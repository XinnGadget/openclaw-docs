---
read_when:
    - 메모리가 어떻게 작동하는지 이해하고 싶을 때
    - 어떤 메모리 파일을 작성해야 하는지 알고 싶을 때
summary: OpenClaw가 세션 전반에 걸쳐 정보를 기억하는 방식
title: 메모리 개요
x-i18n:
    generated_at: "2026-04-08T05:55:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3bb8552341b0b651609edaaae826a22fdc535d240aed4fad4af4b069454004af
    source_path: concepts/memory.md
    workflow: 15
---

# 메모리 개요

OpenClaw는 에이전트의 작업 공간에 **일반 Markdown 파일**을 작성하여 정보를 기억합니다. 모델은 디스크에 저장된 내용만 "기억"하며, 숨겨진 상태는 없습니다.

## 작동 방식

에이전트에는 메모리와 관련된 파일이 세 가지 있습니다:

- **`MEMORY.md`** -- 장기 메모리. 오래 유지되는 사실, 선호, 결정 사항입니다. 모든 DM 세션 시작 시 로드됩니다.
- **`memory/YYYY-MM-DD.md`** -- 일일 노트. 진행 중인 컨텍스트와 관찰 내용을 담습니다. 오늘과 어제의 노트는 자동으로 로드됩니다.
- **`DREAMS.md`** (실험적, 선택 사항) -- 사람이 검토할 수 있도록 만든 Dream Diary 및 dreaming sweep 요약입니다.

이 파일들은 에이전트 작업 공간(기본값: `~/.openclaw/workspace`)에 있습니다.

<Tip>
에이전트가 무언가를 기억하길 원한다면 그냥 이렇게 요청하면 됩니다: "내가 TypeScript를 선호한다고 기억해." 그러면 적절한 파일에 기록합니다.
</Tip>

## 메모리 도구

에이전트에는 메모리를 다루기 위한 두 가지 도구가 있습니다:

- **`memory_search`** -- 원문과 표현이 달라도 시맨틱 검색을 사용해 관련 노트를 찾습니다.
- **`memory_get`** -- 특정 메모리 파일 또는 줄 범위를 읽습니다.

두 도구 모두 활성 메모리 plugin(기본값: `memory-core`)에서 제공합니다.

## Memory Wiki companion plugin

지속 메모리가 단순한 원시 노트보다 관리되는 지식 베이스처럼 동작하길 원한다면, 번들된 `memory-wiki` plugin을 사용하세요.

`memory-wiki`는 지속 지식을 다음 요소를 갖춘 위키 볼트로 컴파일합니다:

- 결정론적 페이지 구조
- 구조화된 주장과 근거
- 모순 및 최신성 추적
- 생성된 대시보드
- 에이전트/런타임 소비자를 위한 컴파일된 다이제스트
- `wiki_search`, `wiki_get`, `wiki_apply`, `wiki_lint` 같은 위키 네이티브 도구

이 plugin은 활성 메모리 plugin을 대체하지 않습니다. 활성 메모리 plugin은 여전히 회상, 승격, dreaming을 담당합니다. `memory-wiki`는 그 옆에 출처 정보가 풍부한 지식 계층을 추가합니다.

자세한 내용은 [Memory Wiki](/ko/plugins/memory-wiki)를 참조하세요.

## 메모리 검색

임베딩 provider가 구성되어 있으면 `memory_search`는 **하이브리드 검색**을 사용합니다. 즉, 벡터 유사도(의미적 의미)와 키워드 매칭(ID 및 코드 심볼 같은 정확한 용어)을 결합합니다. 지원되는 provider 중 하나의 API 키만 있으면 별도 설정 없이 바로 동작합니다.

<Info>
OpenClaw는 사용 가능한 API 키를 바탕으로 임베딩 provider를 자동 감지합니다. OpenAI, Gemini, Voyage 또는 Mistral 키가 구성되어 있으면 메모리 검색이 자동으로 활성화됩니다.
</Info>

검색 작동 방식, 튜닝 옵션, provider 설정에 대한 자세한 내용은 [Memory Search](/ko/concepts/memory-search)를 참조하세요.

## 메모리 백엔드

<CardGroup cols={3}>
<Card title="내장형 (기본값)" icon="database" href="/ko/concepts/memory-builtin">
SQLite 기반입니다. 키워드 검색, 벡터 유사도, 하이브리드 검색을 별도 설정 없이 사용할 수 있습니다. 추가 의존성이 필요하지 않습니다.
</Card>
<Card title="QMD" icon="search" href="/ko/concepts/memory-qmd">
재순위 지정, 쿼리 확장, 작업 공간 외부 디렉터리 인덱싱 기능을 갖춘 로컬 우선 사이드카입니다.
</Card>
<Card title="Honcho" icon="brain" href="/ko/concepts/memory-honcho">
사용자 모델링, 시맨틱 검색, 멀티 에이전트 인식을 지원하는 AI 네이티브 교차 세션 메모리입니다. plugin 설치가 필요합니다.
</Card>
</CardGroup>

## 지식 위키 계층

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/ko/plugins/memory-wiki">
주장, 대시보드, bridge mode, Obsidian 친화적 워크플로를 갖춘 출처 정보가 풍부한 위키 볼트로 지속 메모리를 컴파일합니다.
</Card>
</CardGroup>

## 자동 메모리 플러시

[compaction](/ko/concepts/compaction)이 대화를 요약하기 전에 OpenClaw는 에이전트에게 중요한 컨텍스트를 메모리 파일에 저장하라고 상기시키는 무음 턴을 실행합니다. 이것은 기본적으로 활성화되어 있으므로 별도로 설정할 필요가 없습니다.

<Tip>
메모리 플러시는 compaction 중 컨텍스트 손실을 방지합니다. 대화에 중요한 사실이 있지만 아직 파일에 기록되지 않았다면, 요약이 이루어지기 전에 자동으로 저장됩니다.
</Tip>

## Dreaming (실험적)

Dreaming은 메모리를 위한 선택적 백그라운드 통합 패스입니다. 단기 신호를 수집하고, 후보를 점수화하며, 기준을 충족한 항목만 장기 메모리(`MEMORY.md`)로 승격합니다.

장기 메모리의 신호 대 잡음비를 높게 유지하도록 설계되었습니다:

- **옵트인**: 기본적으로 비활성화되어 있습니다.
- **예약 실행**: 활성화되면 `memory-core`가 전체 dreaming sweep을 위한 반복 cron 작업 하나를 자동으로 관리합니다.
- **임곗값 기반**: 승격은 점수, 회상 빈도, 쿼리 다양성 게이트를 통과해야 합니다.
- **검토 가능**: 단계별 요약과 다이어리 항목이 사람이 검토할 수 있도록 `DREAMS.md`에 기록됩니다.

단계 동작, 점수화 신호, Dream Diary 세부 정보는 [Dreaming (experimental)](/ko/concepts/dreaming)을 참조하세요.

## CLI

```bash
openclaw memory status          # 인덱스 상태와 provider 확인
openclaw memory search "query"  # 명령줄에서 검색
openclaw memory index --force   # 인덱스 다시 빌드
```

## 추가 읽을거리

- [Builtin Memory Engine](/ko/concepts/memory-builtin) -- 기본 SQLite 백엔드
- [QMD Memory Engine](/ko/concepts/memory-qmd) -- 고급 로컬 우선 사이드카
- [Honcho Memory](/ko/concepts/memory-honcho) -- AI 네이티브 교차 세션 메모리
- [Memory Wiki](/ko/plugins/memory-wiki) -- 컴파일된 지식 볼트 및 위키 네이티브 도구
- [Memory Search](/ko/concepts/memory-search) -- 검색 파이프라인, provider, 튜닝
- [Dreaming (experimental)](/ko/concepts/dreaming) -- 단기 회상에서 장기 메모리로의 백그라운드 승격
- [Memory configuration reference](/ko/reference/memory-config) -- 모든 구성 옵션
- [Compaction](/ko/concepts/compaction) -- compaction이 메모리와 상호작용하는 방식
