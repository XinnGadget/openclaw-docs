---
read_when:
    - macOS 로그를 수집하거나 private data 로깅을 조사하는 경우
    - voice wake/세션 수명 주기 문제를 디버깅하는 경우
summary: 'OpenClaw 로깅: 회전형 진단 파일 로그 + 통합 로그 개인정보 플래그'
title: macOS 로깅
x-i18n:
    generated_at: "2026-04-05T12:48:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: c08d6bc012f8e8bb53353fe654713dede676b4e6127e49fd76e00c2510b9ab0b
    source_path: platforms/mac/logging.md
    workflow: 15
---

# 로깅 (macOS)

## 회전형 진단 파일 로그 (Debug pane)

OpenClaw는 macOS 앱 로그를 swift-log(기본적으로 통합 로깅)를 통해 라우팅하며, 지속적인 캡처가 필요할 때는 로컬 회전형 파일 로그를 디스크에 쓸 수 있습니다.

- 상세 수준: **Debug pane → Logs → App logging → Verbosity**
- 활성화: **Debug pane → Logs → App logging → “Write rolling diagnostics log (JSONL)”**
- 위치: `~/Library/Logs/OpenClaw/diagnostics.jsonl` (자동 회전됨. 이전 파일은 `.1`, `.2`, … 접미사 사용)
- 지우기: **Debug pane → Logs → App logging → “Clear”**

참고:

- 기본적으로는 **비활성화**되어 있습니다. 적극적으로 디버깅할 때만 활성화하세요.
- 이 파일은 민감한 정보로 취급해야 하며, 검토 없이 공유하지 마세요.

## macOS의 통합 로깅 private data

통합 로깅은 서브시스템이 `privacy -off`를 선택하지 않는 한 대부분의 payload를 가립니다. Peter의 macOS [logging privacy shenanigans](https://steipete.me/posts/2025/logging-privacy-shenanigans) (2025) 글에 따르면 이는 서브시스템 이름을 키로 하는 `/Library/Preferences/Logging/Subsystems/` 아래의 plist로 제어됩니다. 새 로그 항목에만 플래그가 적용되므로, 문제를 재현하기 전에 활성화하세요.

## OpenClaw (`ai.openclaw`)에 활성화

- 먼저 plist를 임시 파일에 쓴 다음, 루트 권한으로 원자적으로 설치하세요.

```bash
cat <<'EOF' >/tmp/ai.openclaw.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>DEFAULT-OPTIONS</key>
    <dict>
        <key>Enable-Private-Data</key>
        <true/>
    </dict>
</dict>
</plist>
EOF
sudo install -m 644 -o root -g wheel /tmp/ai.openclaw.plist /Library/Preferences/Logging/Subsystems/ai.openclaw.plist
```

- 재부팅은 필요 없습니다. logd가 파일을 빠르게 감지하지만, private payload가 포함되는 것은 새 로그 줄부터입니다.
- 더 풍부한 출력은 기존 도우미로 확인할 수 있습니다. 예: `./scripts/clawlog.sh --category WebChat --last 5m`

## 디버깅 후 비활성화

- 재정의 제거: `sudo rm /Library/Preferences/Logging/Subsystems/ai.openclaw.plist`
- 필요하면 `sudo log config --reload`를 실행해 logd가 즉시 재정의를 해제하도록 강제할 수 있습니다.
- 이 표면에는 전화번호와 메시지 본문이 포함될 수 있다는 점을 기억하세요. 추가 세부 정보가 필요한 동안에만 plist를 유지하세요.
