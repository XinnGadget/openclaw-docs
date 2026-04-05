---
read_when:
    - 기기 모델 식별자 매핑 또는 NOTICE/라이선스 파일을 업데이트하는 경우
    - Instances UI에서 기기 이름이 표시되는 방식을 변경하는 경우
summary: OpenClaw가 macOS 앱에서 보기 쉬운 이름을 위해 Apple 기기 모델 식별자를 어떻게 벤더링하는지 설명합니다.
title: 기기 모델 데이터베이스
x-i18n:
    generated_at: "2026-04-05T12:53:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1d99c2538a0d8fdd80fa468fa402f63479ef2522e83745a0a46527a86238aeb2
    source_path: reference/device-models.md
    workflow: 15
---

# 기기 모델 데이터베이스(보기 쉬운 이름)

macOS companion 앱은 Apple 모델 식별자(예: `iPad16,6`, `Mac16,6`)를 사람이 읽기 쉬운 이름으로 매핑하여 **Instances** UI에 보기 쉬운 Apple 기기 모델 이름을 표시합니다.

매핑은 다음 경로 아래 JSON으로 벤더링되어 있습니다:

- `apps/macos/Sources/OpenClaw/Resources/DeviceModels/`

## 데이터 소스

현재는 MIT 라이선스 저장소의 매핑을 벤더링하고 있습니다:

- `kyle-seongwoo-jun/apple-device-identifiers`

빌드를 결정적으로 유지하기 위해 JSON 파일은 특정 업스트림 커밋에 고정되어 있습니다(`apps/macos/Sources/OpenClaw/Resources/DeviceModels/NOTICE.md`에 기록됨).

## 데이터베이스 업데이트

1. 고정할 업스트림 커밋을 선택합니다(iOS용 하나, macOS용 하나).
2. `apps/macos/Sources/OpenClaw/Resources/DeviceModels/NOTICE.md`에서 커밋 해시를 업데이트합니다.
3. 해당 커밋에 고정된 JSON 파일을 다시 다운로드합니다:

```bash
IOS_COMMIT="<commit sha for ios-device-identifiers.json>"
MAC_COMMIT="<commit sha for mac-device-identifiers.json>"

curl -fsSL "https://raw.githubusercontent.com/kyle-seongwoo-jun/apple-device-identifiers/${IOS_COMMIT}/ios-device-identifiers.json" \
  -o apps/macos/Sources/OpenClaw/Resources/DeviceModels/ios-device-identifiers.json

curl -fsSL "https://raw.githubusercontent.com/kyle-seongwoo-jun/apple-device-identifiers/${MAC_COMMIT}/mac-device-identifiers.json" \
  -o apps/macos/Sources/OpenClaw/Resources/DeviceModels/mac-device-identifiers.json
```

4. `apps/macos/Sources/OpenClaw/Resources/DeviceModels/LICENSE.apple-device-identifiers.txt`가 여전히 업스트림과 일치하는지 확인합니다(업스트림 라이선스가 변경되면 교체하세요).
5. macOS 앱이 문제 없이 빌드되는지 확인합니다(경고 없음):

```bash
swift build --package-path apps/macos
```
