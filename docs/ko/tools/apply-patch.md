---
read_when:
    - 여러 파일에 걸쳐 구조화된 파일 편집이 필요한 경우
    - 패치 기반 편집을 문서화하거나 디버깅하려는 경우
summary: apply_patch 도구로 여러 파일 패치 적용하기
title: apply_patch 도구
x-i18n:
    generated_at: "2026-04-05T12:55:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: acca6e702e7ccdf132c71dc6d973f1d435ad6d772e1b620512c8969420cb8f7a
    source_path: tools/apply-patch.md
    workflow: 15
---

# apply_patch 도구

구조화된 패치 형식을 사용해 파일 변경을 적용합니다. 이는 여러 파일 또는
여러 hunk를 수정할 때, 단일 `edit` 호출이 취약할 수 있는 경우에 적합합니다.

이 도구는 하나 이상의 파일 작업을 감싸는 단일 `input` 문자열을 받습니다:

```
*** Begin Patch
*** Add File: path/to/file.txt
+line 1
+line 2
*** Update File: src/app.ts
@@
-old line
+new line
*** Delete File: obsolete.txt
*** End Patch
```

## 매개변수

- `input`(필수): `*** Begin Patch`와 `*** End Patch`를 포함한 전체 패치 내용.

## 참고

- 패치 경로는 상대 경로(워크스페이스 디렉터리 기준)와 절대 경로를 모두 지원합니다.
- `tools.exec.applyPatch.workspaceOnly`의 기본값은 `true`(워크스페이스 내부만)입니다. `apply_patch`가 워크스페이스 디렉터리 밖에 쓰기/삭제하도록 의도한 경우에만 `false`로 설정하세요.
- 파일 이름을 변경하려면 `*** Update File:` hunk 안에서 `*** Move to:`를 사용하세요.
- 필요할 경우 `*** End of File`은 EOF 전용 삽입을 표시합니다.
- OpenAI 및 OpenAI Codex 모델에서는 기본적으로 사용할 수 있습니다.
  비활성화하려면 `tools.exec.applyPatch.enabled: false`로 설정하세요.
- 모델별로 제한하려면
  `tools.exec.applyPatch.allowModels`를 사용할 수 있습니다.
- config는 `tools.exec` 아래에만 있습니다.

## 예시

```json
{
  "tool": "apply_patch",
  "input": "*** Begin Patch\n*** Update File: src/index.ts\n@@\n-const foo = 1\n+const foo = 2\n*** End Patch"
}
```
