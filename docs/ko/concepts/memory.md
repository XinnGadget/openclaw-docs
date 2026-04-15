---
read_when:
    - 메모리가 어떻게 작동하는지 이해하고 싶습니다
    - 어떤 메모리 파일에 작성해야 하는지 알고 싶습니다
summary: OpenClaw가 세션 전반에 걸쳐 정보를 기억하는 방식
title: 메모리 개요
x-i18n:
    generated_at: "2026-04-15T14:40:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# 메모리 개요

OpenClaw는 에이전트의 워크스페이스에 **일반 Markdown 파일**을 작성하여 정보를 기억합니다. 모델이 "기억하는" 것은 디스크에 저장된 내용뿐이며, 숨겨진 상태는 없습니다.

## 작동 방식

에이전트에는 메모리 관련 파일이 세 가지 있습니다:

- **`MEMORY.md`** -- 장기 메모리입니다. 지속되는 사실, 선호도, 결정 사항을 담습니다. 모든 DM 세션이 시작될 때 로드됩니다.
- **`memory/YYYY-MM-DD.md`** -- 일일 노트입니다. 진행 중인 컨텍스트와 관찰 내용을 담습니다. 오늘과 어제의 노트는 자동으로 로드됩니다.
- **`DREAMS.md`** (선택 사항) -- 인간이 검토할 수 있도록 Dream Diary와 Dreaming 스윕 요약을 포함하며, 근거가 있는 과거 소급 항목도 포함합니다.

이 파일들은 에이전트 워크스페이스(기본값 `~/.openclaw/workspace`)에 있습니다.

<Tip>
에이전트가 무언가를 기억하길 원한다면, 이렇게 요청하면 됩니다: "내가 TypeScript를 선호한다고 기억해." 그러면 적절한 파일에 기록합니다.
</Tip>

## 메모리 도구

에이전트에는 메모리를 다루기 위한 두 가지 도구가 있습니다:

- **`memory_search`** -- 원래 표현과 문구가 다르더라도 시맨틱 검색을 사용해 관련 노트를 찾습니다.
- **`memory_get`** -- 특정 메모리 파일이나 줄 범위를 읽습니다.

두 도구 모두 활성 메모리 Plugin(기본값: `memory-core`)이 제공합니다.

## Memory Wiki 보조 Plugin

지속 메모리가 단순한 원시 노트가 아니라, 유지 관리되는 지식 베이스처럼 동작하길 원한다면 번들된 `memory-wiki` Plugin을 사용하세요.

`memory-wiki`는 지속 지식을 다음과 같은 요소를 갖춘 wiki vault로 컴파일합니다:

- 결정론적인 페이지 구조
- 구조화된 주장과 근거
- 모순 및 최신성 추적
- 생성된 대시보드
- 에이전트/런타임 소비자를 위한 컴파일된 다이제스트
- `wiki_search`, `wiki_get`, `wiki_apply`, `wiki_lint` 같은 wiki 네이티브 도구

이 Plugin은 활성 메모리 Plugin을 대체하지 않습니다. 활성 메모리 Plugin은 여전히 회상, 승격, Dreaming을 담당합니다. `memory-wiki`는 그 옆에 출처가 풍부한 지식 계층을 추가합니다.

자세한 내용은 [Memory Wiki](/ko/plugins/memory-wiki)를 참조하세요.

## 메모리 검색

임베딩 제공자가 구성되어 있으면 `memory_search`는 **하이브리드 검색**을 사용합니다. 즉, 벡터 유사도(의미적 유사성)와 키워드 매칭(ID나 코드 심볼 같은 정확한 용어)을 결합합니다. 지원되는 제공자 중 하나의 API 키만 있으면 별도 설정 없이 바로 동작합니다.

<Info>
OpenClaw는 사용 가능한 API 키를 바탕으로 임베딩 제공자를 자동 감지합니다. OpenAI, Gemini, Voyage, 또는 Mistral 키가 구성되어 있으면 메모리 검색이 자동으로 활성화됩니다.
</Info>

검색 동작 방식, 튜닝 옵션, 제공자 설정에 대한 자세한 내용은 [Memory Search](/ko/concepts/memory-search)를 참조하세요.

## 메모리 백엔드

<CardGroup cols={3}>
<Card title="내장(기본값)" icon="database" href="/ko/concepts/memory-builtin">
SQLite 기반입니다. 키워드 검색, 벡터 유사도, 하이브리드 검색을 즉시 사용할 수 있습니다. 추가 의존성이 필요하지 않습니다.
</Card>
<Card title="QMD" icon="search" href="/ko/concepts/memory-qmd">
재순위화, 쿼리 확장, 워크스페이스 외부 디렉터리 인덱싱 기능을 제공하는 local-first 사이드카입니다.
</Card>
<Card title="Honcho" icon="brain" href="/ko/concepts/memory-honcho">
사용자 모델링, 시맨틱 검색, 멀티 에이전트 인식을 지원하는 AI 네이티브 크로스 세션 메모리입니다. Plugin 설치가 필요합니다.
</Card>
</CardGroup>

## 지식 wiki 계층

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/ko/plugins/memory-wiki">
지속 메모리를 주장, 대시보드, 브리지 모드, Obsidian 친화적 워크플로를 갖춘 출처가 풍부한 wiki vault로 컴파일합니다.
</Card>
</CardGroup>

## 자동 메모리 플러시

[Compaction](/ko/concepts/compaction)이 대화를 요약하기 전에, OpenClaw는 에이전트에게 중요한 컨텍스트를 메모리 파일에 저장하라고 상기시키는 조용한 턴을 실행합니다. 이것은 기본적으로 활성화되어 있으므로 별도 설정이 필요하지 않습니다.

<Tip>
메모리 플러시는 Compaction 중 컨텍스트 손실을 방지합니다. 대화 안에 중요한 사실이 아직 파일에 기록되지 않았다면, 요약이 이루어지기 전에 자동으로 저장됩니다.
</Tip>

## Dreaming

Dreaming은 메모리를 위한 선택적 백그라운드 통합 패스입니다. 단기 신호를 수집하고, 후보를 점수화하며, 조건을 충족하는 항목만 장기 메모리(`MEMORY.md`)로 승격합니다.

장기 메모리의 신호 대 잡음비를 높게 유지하도록 설계되었습니다:

- **선택적 활성화**: 기본적으로 비활성화되어 있습니다.
- **예약 실행**: 활성화되면 `memory-core`가 전체 Dreaming 스윕을 위한 반복 Cron 작업 하나를 자동 관리합니다.
- **임계값 기반**: 승격은 점수, 회상 빈도, 쿼리 다양성 게이트를 통과해야 합니다.
- **검토 가능**: 단계 요약과 다이어리 항목이 사람이 검토할 수 있도록 `DREAMS.md`에 기록됩니다.

단계별 동작, 점수화 신호, Dream Diary 세부 정보는 [Dreaming](/ko/concepts/dreaming)을 참조하세요.

## 근거 기반 소급과 실시간 승격

이제 Dreaming 시스템에는 밀접하게 연결된 두 가지 검토 경로가 있습니다:

- **실시간 Dreaming**은 `memory/.dreams/` 아래의 단기 Dreaming 저장소를 기반으로 작동하며, 어떤 항목이 `MEMORY.md`로 승급할 수 있는지 판단할 때 일반적인 심화 단계에서 사용됩니다.
- **근거 기반 소급**은 과거의 `memory/YYYY-MM-DD.md` 노트를 독립적인 일별 파일로 읽고, 구조화된 검토 결과를 `DREAMS.md`에 기록합니다.

근거 기반 소급은 오래된 노트를 다시 재생하면서 시스템이 무엇을 지속 가능한 정보로 판단하는지 `MEMORY.md`를 직접 편집하지 않고 확인하고 싶을 때 유용합니다.

다음을 실행하면:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

근거 기반의 지속 후보는 직접 승격되지 않습니다. 대신 일반적인 심화 단계가 이미 사용하는 동일한 단기 Dreaming 저장소에 스테이징됩니다. 즉:

- `DREAMS.md`는 사람이 검토하는 표면으로 유지됩니다.
- 단기 저장소는 기계가 사용하는 순위화 표면으로 유지됩니다.
- `MEMORY.md`는 여전히 심화 승격에 의해서만 기록됩니다.

재생이 유용하지 않았다고 판단되면, 일반적인 다이어리 항목이나 정상적인 회상 상태를 건드리지 않고 스테이징된 아티팩트를 제거할 수 있습니다:

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # 인덱스 상태와 제공자 확인
openclaw memory search "query"  # 명령줄에서 검색
openclaw memory index --force   # 인덱스 다시 빌드
```

## 추가 읽을거리

- [Builtin Memory Engine](/ko/concepts/memory-builtin) -- 기본 SQLite 백엔드
- [QMD Memory Engine](/ko/concepts/memory-qmd) -- 고급 local-first 사이드카
- [Honcho Memory](/ko/concepts/memory-honcho) -- AI 네이티브 크로스 세션 메모리
- [Memory Wiki](/ko/plugins/memory-wiki) -- 컴파일된 지식 vault 및 wiki 네이티브 도구
- [Memory Search](/ko/concepts/memory-search) -- 검색 파이프라인, 제공자, 튜닝
- [Dreaming](/ko/concepts/dreaming) -- 단기 회상에서 장기 메모리로의 백그라운드 승격
- [Memory configuration reference](/ko/reference/memory-config) -- 모든 구성 옵션
- [Compaction](/ko/concepts/compaction) -- Compaction이 메모리와 상호작용하는 방식
