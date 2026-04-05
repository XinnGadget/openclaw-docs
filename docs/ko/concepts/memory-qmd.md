---
read_when:
    - 메모리 백엔드로 QMD를 설정하려고 함
    - 리랭킹 또는 추가 인덱싱 경로 같은 고급 메모리 기능이 필요함
summary: BM25, 벡터, 리랭킹 및 쿼리 확장을 제공하는 로컬 우선 검색 사이드카
title: QMD Memory Engine
x-i18n:
    generated_at: "2026-04-05T12:40:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: fa8a31ec1a6cc83b6ab413b7dbed6a88055629251664119bfd84308ed166c58e
    source_path: concepts/memory-qmd.md
    workflow: 15
---

# QMD 메모리 엔진

[QMD](https://github.com/tobi/qmd)는 OpenClaw와 함께 실행되는 로컬 우선 검색 사이드카입니다. 단일
바이너리에서 BM25, 벡터 검색, 리랭킹을 결합하며, workspace 메모리 파일을 넘어선 콘텐츠도 인덱싱할 수 있습니다.

## 내장 엔진 대비 추가 기능

- **리랭킹 및 쿼리 확장**으로 더 나은 회상 성능 제공.
- **추가 디렉터리 인덱싱** -- 프로젝트 문서, 팀 노트, 디스크의 모든 것.
- **세션 기록 인덱싱** -- 이전 대화를 회상.
- **완전 로컬** -- Bun + `node-llama-cpp`로 실행되며 GGUF 모델을 자동 다운로드.
- **자동 폴백** -- QMD를 사용할 수 없으면 OpenClaw가
  내장 엔진으로 자연스럽게 폴백.

## 시작하기

### 사전 요구 사항

- QMD 설치: `bun install -g @tobilu/qmd`
- 확장을 허용하는 SQLite 빌드(macOS에서는 `brew install sqlite`).
- QMD는 gateway의 `PATH`에 있어야 합니다.
- macOS와 Linux는 바로 작동합니다. Windows는 WSL2를 통해 가장 잘 지원됩니다.

### 활성화

```json5
{
  memory: {
    backend: "qmd",
  },
}
```

OpenClaw는
`~/.openclaw/agents/<agentId>/qmd/` 아래에 자체 포함형 QMD 홈을 만들고 사이드카 수명 주기를
자동으로 관리합니다 -- 컬렉션, 업데이트, 임베딩 실행이 모두 자동 처리됩니다.

## 사이드카 작동 방식

- OpenClaw는 workspace 메모리 파일과
  구성된 `memory.qmd.paths`에서 컬렉션을 생성한 다음, 부팅 시 및 주기적으로
  `qmd update` + `qmd embed`를 실행합니다(기본값 5분마다).
- 부팅 새로 고침은 채팅 시작을 막지 않도록 백그라운드에서 실행됩니다.
- 검색은 구성된 `searchMode`를 사용합니다(기본값: `search`; `vsearch`와 `query`도
  지원). 특정 모드가 실패하면 OpenClaw는 `qmd query`로 재시도합니다.
- QMD가 완전히 실패하면 OpenClaw는 내장 SQLite 엔진으로 폴백합니다.

<Info>
첫 번째 검색은 느릴 수 있습니다 -- QMD는 첫 `qmd query` 실행 시
리랭킹과 쿼리 확장을 위해 GGUF 모델(~2GB)을 자동 다운로드합니다.
</Info>

## 추가 경로 인덱싱

추가 디렉터리를 검색 가능하게 하려면 QMD가 해당 경로를 보도록 설정하세요.

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

추가 경로의 스니펫은 검색 결과에서
`qmd/<collection>/<relative-path>`로 표시됩니다. `memory_get`은 이 접두사를 이해하고 올바른
컬렉션 루트에서 읽습니다.

## 세션 기록 인덱싱

이전 대화를 회상할 수 있도록 세션 인덱싱을 활성화하세요.

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      sessions: { enabled: true },
    },
  },
}
```

기록은 정리된 User/Assistant 턴으로 내보내져
`~/.openclaw/agents/<id>/qmd/sessions/` 아래 전용 QMD
컬렉션에 저장됩니다.

## 검색 범위

기본적으로 QMD 검색 결과는 DM 세션에서만 표시되며(그룹이나
채널은 아님), 이를 변경하려면 `memory.qmd.scope`를 구성하세요.

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

범위 규칙이 검색을 거부하면 OpenClaw는 파생된 채널과
채팅 유형을 포함한 경고를 기록하므로 빈 결과를 더 쉽게 디버그할 수 있습니다.

## 인용

`memory.citations`가 `auto` 또는 `on`이면 검색 스니펫에
`Source: <path#line>` 바닥글이 포함됩니다. 바닥글을 생략하면서도 경로를 내부적으로 에이전트에 전달하려면
`memory.citations = "off"`를 설정하세요.

## 사용 시점

다음이 필요하다면 QMD를 선택하세요.

- 더 높은 품질의 결과를 위한 리랭킹.
- workspace 밖의 프로젝트 문서나 노트 검색.
- 과거 세션 대화 회상.
- API 키가 필요 없는 완전 로컬 검색.

더 단순한 설정이라면 [내장 엔진](/concepts/memory-builtin)이
추가 의존성 없이 잘 작동합니다.

## 문제 해결

**QMD를 찾을 수 없나요?** 바이너리가 gateway의 `PATH`에 있는지 확인하세요. OpenClaw가
서비스로 실행 중이면 심볼릭 링크를 만드세요.
`sudo ln -s ~/.bun/bin/qmd /usr/local/bin/qmd`.

**첫 검색이 매우 느린가요?** QMD는 첫 사용 시 GGUF 모델을 다운로드합니다. OpenClaw가 사용하는 것과 동일한 XDG 디렉터리로 `qmd query "test"`를 실행해 미리 워밍하세요.

**검색 시간이 초과되나요?** `memory.qmd.limits.timeoutMs`를 늘리세요(기본값: 4000ms).
느린 하드웨어에서는 `120000`으로 설정하세요.

**그룹 채팅에서 결과가 비어 있나요?** `memory.qmd.scope`를 확인하세요 -- 기본값은
DM 세션만 허용합니다.

**workspace에서 보이는 임시 리포지토리 때문에 `ENAMETOOLONG` 또는 인덱싱 손상이 발생하나요?**
QMD 순회는 현재 OpenClaw 내장 심볼릭 링크 규칙이 아니라 기본 QMD 스캐너 동작을 따릅니다. QMD가
사이클 안전 순회 또는 명시적 제외 제어를 제공할 때까지 임시 모노레포 체크아웃은
`.tmp/` 같은 숨김 디렉터리 아래나 인덱싱된 QMD 루트 밖에 두세요.

## 구성

전체 config 표면(`memory.qmd.*`), 검색 모드, 업데이트 간격,
범위 규칙 및 기타 모든 옵션은
[Memory configuration reference](/reference/memory-config)를 참조하세요.
