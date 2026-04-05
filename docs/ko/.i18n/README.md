---
x-i18n:
    generated_at: "2026-04-05T12:34:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: adff26fa8858af2759b231ea48bfc01f89c110cd9b3774a8f783e282c16f77fb
    source_path: .i18n/README.md
    workflow: 15
---

# OpenClaw 문서 i18n 자산

이 폴더에는 소스 문서 리포지토리용 번역 구성이 저장됩니다.

생성된 로캘 트리와 실시간 translation memory는 이제 게시 리포지토리에 있습니다:

- 리포지토리: `openclaw/docs`
- 로컬 체크아웃: `~/Projects/openclaw-docs`

## 소스 오브 트루스

- 영어 문서는 `openclaw/openclaw`에서 작성됩니다.
- 소스 문서 트리는 `docs/` 아래에 있습니다.
- 소스 리포지토리는 더 이상 `docs/zh-CN/**`, `docs/ja-JP/**`, `docs/es/**`, `docs/pt-BR/**`, `docs/ko/**`, `docs/de/**`, `docs/fr/**`, 또는 `docs/ar/**` 같은 생성된 로캘 트리를 커밋된 상태로 유지하지 않습니다.

## 엔드투엔드 흐름

1. `openclaw/openclaw`에서 영어 문서를 수정합니다.
2. `main`에 푸시합니다.
3. `openclaw/openclaw/.github/workflows/docs-sync-publish.yml`이 문서 트리를 `openclaw/docs`로 미러링합니다.
4. 동기화 스크립트는 게시 리포지토리의 `docs/docs.json`을 다시 작성하여, 소스 리포지토리에 더 이상 커밋되지 않더라도 생성된 로캘 선택기 블록이 그곳에 존재하도록 합니다.
5. `openclaw/docs/.github/workflows/translate-zh-cn.yml`은 하루에 한 번, 필요 시, 그리고 소스 리포지토리의 릴리스 디스패치 이후에 `docs/zh-CN/**`를 새로 고칩니다.
6. `openclaw/docs/.github/workflows/translate-ja-jp.yml`은 `docs/ja-JP/**`에 대해 동일하게 수행합니다.
7. `openclaw/docs/.github/workflows/translate-es.yml`, `translate-pt-br.yml`, `translate-ko.yml`, `translate-de.yml`, `translate-fr.yml`, 그리고 `translate-ar.yml`은 `docs/es/**`, `docs/pt-BR/**`, `docs/ko/**`, `docs/de/**`, `docs/fr/**`, 그리고 `docs/ar/**`에 대해 동일하게 수행합니다.

## 분리 구조가 존재하는 이유

- 생성된 로캘 출력을 주 제품 리포지토리 밖에 유지하기 위해서입니다.
- Mintlify를 단일 게시 문서 트리에서 유지하기 위해서입니다.
- 게시 리포지토리가 생성된 로캘 트리를 소유하도록 하여 기본 제공 언어 전환기를 유지하기 위해서입니다.

## 이 폴더의 파일

- `glossary.<lang>.json` — 프롬프트 가이드로 사용되는 선호 용어 매핑.
- `ar-navigation.json`, `de-navigation.json`, `es-navigation.json`, `fr-navigation.json`, `ja-navigation.json`, `ko-navigation.json`, `pt-BR-navigation.json`, `zh-Hans-navigation.json` — 동기화 중 게시 리포지토리에 다시 삽입되는 Mintlify 로캘 선택기 블록.
- `<lang>.tm.jsonl` — 워크플로 + 모델 + 텍스트 해시를 키로 사용하는 translation memory.

이 리포지토리에서 `docs/.i18n/zh-CN.tm.jsonl`, `docs/.i18n/ja-JP.tm.jsonl`, `docs/.i18n/es.tm.jsonl`, `docs/.i18n/pt-BR.tm.jsonl`, `docs/.i18n/ko.tm.jsonl`, `docs/.i18n/de.tm.jsonl`, `docs/.i18n/fr.tm.jsonl`, 그리고 `docs/.i18n/ar.tm.jsonl` 같은 생성된 로캘 TM 파일은 의도적으로 더 이상 커밋되지 않습니다.

## 용어집 형식

`glossary.<lang>.json`은 항목 배열입니다:

```json
{
  "source": "troubleshooting",
  "target": "故障排除"
}
```

필드:

- `source`: 우선적으로 사용할 영어(또는 원본) 구문입니다.
- `target`: 선호되는 번역 출력입니다.

## 번역 메커니즘

- `scripts/docs-i18n`은 여전히 번역 생성을 담당합니다.
- 문서 모드는 각 번역된 페이지에 `x-i18n.source_hash`를 기록합니다.
- 각 게시 워크플로는 현재 영어 소스 해시를 저장된 로캘 `x-i18n.source_hash`와 비교하여 보류 파일 목록을 미리 계산합니다.
- 보류 개수가 `0`이면 비용이 큰 번역 단계는 완전히 건너뜁니다.
- 보류 중인 파일이 있으면 워크플로는 해당 파일만 번역합니다.
- 게시 워크플로는 일시적인 모델 형식 실패를 재시도하지만, 동일한 해시 검사가 각 재시도마다 실행되므로 변경되지 않은 파일은 계속 건너뜁니다.
- 소스 리포지토리는 게시된 GitHub 릴리스 후에도 zh-CN, ja-JP, es, pt-BR, ko, de, fr, 및 ar 새로 고침을 디스패치하므로, 릴리스 문서가 일일 cron을 기다리지 않고도 따라잡을 수 있습니다.

## 운영 참고 사항

- 동기화 메타데이터는 게시 리포지토리의 `.openclaw-sync/source.json`에 기록됩니다.
- 소스 리포지토리 시크릿: `OPENCLAW_DOCS_SYNC_TOKEN`
- 게시 리포지토리 시크릿: `OPENCLAW_DOCS_I18N_OPENAI_API_KEY`
- 로캘 출력이 오래된 것처럼 보이면 먼저 `openclaw/docs`에서 해당하는 `Translate <locale>` 워크플로를 확인하세요.
