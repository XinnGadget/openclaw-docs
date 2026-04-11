---
x-i18n:
    generated_at: "2026-04-11T15:15:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2a8884fc2c304bf96d4675f0c1d1ff781d6dc1ae8c49d92ce08040c9c7709035
    source_path: reference/rich-output-protocol.md
    workflow: 15
---

# 리치 출력 프로토콜

어시스턴트 출력은 소수의 전달/렌더링 지시어를 포함할 수 있습니다:

- 첨부 전달용 `MEDIA:`
- 오디오 표현 힌트용 `[[audio_as_voice]]`
- 답장 메타데이터용 `[[reply_to_current]]` / `[[reply_to:<id>]]`
- Control UI 리치 렌더링용 `[embed ...]`

이 지시어들은 서로 별개입니다. `MEDIA:` 및 reply/voice 태그는 전달 메타데이터로 유지되며, `[embed ...]`는 웹 전용 리치 렌더 경로입니다.

## `[embed ...]`

`[embed ...]`는 Control UI를 위한 유일한 에이전트 대상 리치 렌더 구문입니다.

자체 닫힘 예시:

```text
[embed ref="cv_123" title="상태" /]
```

규칙:

- 새 출력에서는 `[view ...]`를 더 이상 사용할 수 없습니다.
- embed 쇼트코드는 어시스턴트 메시지 표면에서만 렌더링됩니다.
- URL 기반 embed만 렌더링됩니다. `ref="..."` 또는 `url="..."`를 사용하세요.
- 블록 형식의 인라인 HTML embed 쇼트코드는 렌더링되지 않습니다.
- 웹 UI는 표시 텍스트에서 쇼트코드를 제거하고 embed를 인라인으로 렌더링합니다.
- `MEDIA:`는 embed 별칭이 아니며 리치 embed 렌더링에 사용해서는 안 됩니다.

## 저장된 렌더링 형태

정규화되어 저장되는 어시스턴트 콘텐츠 블록은 구조화된 `canvas` 항목입니다:

```json
{
  "type": "canvas",
  "preview": {
    "kind": "canvas",
    "surface": "assistant_message",
    "render": "url",
    "viewId": "cv_123",
    "url": "/__openclaw__/canvas/documents/cv_123/index.html",
    "title": "Status",
    "preferredHeight": 320
  }
}
```

저장되거나 렌더링되는 리치 블록은 이 `canvas` 형태를 직접 사용합니다. `present_view`는 인식되지 않습니다.
