---
read_when:
    - 에이전트에서 PDF를 분석하려는 경우
    - 정확한 pdf 도구 매개변수와 제한이 필요한 경우
    - 기본 PDF 모드와 추출 폴백을 디버깅하는 경우
summary: 기본 제공자 지원과 추출 폴백을 사용해 하나 이상의 PDF 문서를 분석하기
title: PDF 도구
x-i18n:
    generated_at: "2026-04-05T12:57:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: d7aaaa7107d7920e7c31f3e38ac19411706e646186acf520bc02f2c3e49c0517
    source_path: tools/pdf.md
    workflow: 15
---

# PDF 도구

`pdf`는 하나 이상의 PDF 문서를 분석하고 텍스트를 반환합니다.

빠른 동작 개요:

- Anthropic 및 Google 모델 제공자를 위한 기본 제공자 모드
- 다른 제공자를 위한 추출 폴백 모드(먼저 텍스트를 추출하고, 필요할 때 페이지 이미지를 사용)
- 단일(`pdf`) 또는 다중(`pdfs`) 입력 지원, 호출당 최대 10개 PDF

## 사용 가능 여부

OpenClaw가 에이전트에 대해 PDF 가능한 모델 구성을 확인할 수 있을 때만 이 도구가 등록됩니다:

1. `agents.defaults.pdfModel`
2. 폴백으로 `agents.defaults.imageModel`
3. 폴백으로 에이전트의 확인된 세션/기본 모델
4. 기본 PDF 제공자가 인증 기반이면 일반 이미지 폴백 후보보다 먼저 우선

사용 가능한 모델을 확인할 수 없으면 `pdf` 도구는 노출되지 않습니다.

사용 가능 여부 참고 사항:

- 폴백 체인은 인증을 인식합니다. 구성된 `provider/model`은
  OpenClaw가 실제로 해당 에이전트에 대해 그 제공자를 인증할 수 있을 때만 유효합니다.
- 현재 기본 PDF 제공자는 **Anthropic** 및 **Google**입니다.
- 확인된 세션/기본 제공자에 이미 구성된 vision/PDF
  모델이 있으면 PDF 도구는 다른 인증 기반
  제공자로 폴백하기 전에 이를 재사용합니다.

## 입력 참조

- `pdf` (`string`): 하나의 PDF 경로 또는 URL
- `pdfs` (`string[]`): 여러 PDF 경로 또는 URL, 총 최대 10개
- `prompt` (`string`): 분석 프롬프트, 기본값 `Analyze this PDF document.`
- `pages` (`string`): `1-5` 또는 `1,3,7-9` 같은 페이지 필터
- `model` (`string`): 선택적 모델 재정의(`provider/model`)
- `maxBytesMb` (`number`): PDF당 MB 단위 크기 상한

입력 참고 사항:

- `pdf`와 `pdfs`는 로드 전에 병합되고 중복 제거됩니다.
- PDF 입력이 제공되지 않으면 도구는 오류를 반환합니다.
- `pages`는 1부터 시작하는 페이지 번호로 파싱되며, 중복 제거, 정렬, 그리고 구성된 최대 페이지 수로 제한됩니다.
- `maxBytesMb`의 기본값은 `agents.defaults.pdfMaxBytesMb` 또는 `10`입니다.

## 지원되는 PDF 참조

- 로컬 파일 경로(`~` 확장 포함)
- `file://` URL
- `http://` 및 `https://` URL

참조 참고 사항:

- 다른 URI 스킴(예: `ftp://`)은 `unsupported_pdf_reference`와 함께 거부됩니다.
- 샌드박스 모드에서는 원격 `http(s)` URL이 거부됩니다.
- workspace-only 파일 정책이 활성화되면 허용된 루트 밖의 로컬 파일 경로는 거부됩니다.

## 실행 모드

### 기본 제공자 모드

기본 모드는 제공자 `anthropic` 및 `google`에 사용됩니다.
이 도구는 원시 PDF 바이트를 제공자 API로 직접 전송합니다.

기본 모드 제한:

- `pages`는 지원되지 않습니다. 설정되면 도구는 오류를 반환합니다.
- 다중 PDF 입력이 지원되며, 각 PDF는 프롬프트 전에 기본 문서 블록 / 인라인 PDF 파트로 전송됩니다.

### 추출 폴백 모드

폴백 모드는 기본이 아닌 제공자에 사용됩니다.

흐름:

1. 선택한 페이지에서 텍스트를 추출합니다(`agents.defaults.pdfMaxPages`까지, 기본값 `20`).
2. 추출된 텍스트 길이가 `200`자 미만이면 선택한 페이지를 PNG 이미지로 렌더링해 포함합니다.
3. 추출된 콘텐츠와 프롬프트를 선택한 모델로 전송합니다.

폴백 세부 사항:

- 페이지 이미지 추출에는 `4,000,000` 픽셀 예산이 사용됩니다.
- 대상 모델이 이미지 입력을 지원하지 않고 추출 가능한 텍스트도 없으면 도구는 오류를 반환합니다.
- 텍스트 추출에 성공했지만 이미지 추출에 텍스트 전용 모델에서
  vision이 필요하다면 OpenClaw는 렌더링된 이미지를 제거하고
  추출된 텍스트만으로 계속 진행합니다.
- 추출 폴백에는 `pdfjs-dist`가 필요합니다(이미지 렌더링에는 `@napi-rs/canvas`도 필요).

## 설정

```json5
{
  agents: {
    defaults: {
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4-mini"],
      },
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
    },
  },
}
```

전체 필드 세부 정보는 [구성 참조](/ko/gateway/configuration-reference)를 참고하세요.

## 출력 세부 정보

도구는 `content[0].text`에 텍스트를 반환하고 `details`에 구조화된 메타데이터를 반환합니다.

일반적인 `details` 필드:

- `model`: 확인된 모델 참조(`provider/model`)
- `native`: 기본 제공자 모드이면 `true`, 폴백이면 `false`
- `attempts`: 성공 전에 실패한 폴백 시도

경로 필드:

- 단일 PDF 입력: `details.pdf`
- 다중 PDF 입력: `details.pdfs[]` 내 `pdf` 항목
- 샌드박스 경로 재작성 메타데이터(해당하는 경우): `rewrittenFrom`

## 오류 동작

- PDF 입력 누락: `pdf required: provide a path or URL to a PDF document` 발생
- PDF가 너무 많음: `details.error = "too_many_pdfs"`에 구조화된 오류 반환
- 지원되지 않는 참조 스킴: `details.error = "unsupported_pdf_reference"` 반환
- `pages`가 있는 기본 모드: `pages is not supported with native PDF providers`라는 명확한 오류 발생

## 예시

단일 PDF:

```json
{
  "pdf": "/tmp/report.pdf",
  "prompt": "이 보고서를 5개의 글머리표로 요약하세요"
}
```

여러 PDF:

```json
{
  "pdfs": ["/tmp/q1.pdf", "/tmp/q2.pdf"],
  "prompt": "두 문서의 위험과 일정 변경 사항을 비교하세요"
}
```

페이지 필터가 있는 폴백 모델:

```json
{
  "pdf": "https://example.com/report.pdf",
  "pages": "1-3,7",
  "model": "openai/gpt-5.4-mini",
  "prompt": "고객에 영향을 주는 사고만 추출하세요"
}
```

## 관련 문서

- [도구 개요](/tools) — 사용 가능한 모든 에이전트 도구
- [구성 참조](/ko/gateway/configuration-reference#agent-defaults) — pdfMaxBytesMb 및 pdfMaxPages 설정
