---
read_when:
    - 워크스페이스를 수동으로 부트스트랩하는 경우
summary: TOOLS.md용 워크스페이스 템플릿
title: TOOLS.md 템플릿
x-i18n:
    generated_at: "2026-04-05T12:54:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: eed204d57e7221ae0455a87272da2b0730d6aee6ddd2446a851703276e4a96b7
    source_path: reference/templates/TOOLS.md
    workflow: 15
---

# TOOLS.md - 로컬 메모

Skills는 도구가 _어떻게_ 작동하는지를 정의합니다. 이 파일은 _당신만의_ 세부 정보, 즉 설정에만 고유한 내용을 위한 것입니다.

## 여기에 들어갈 내용

예를 들면 다음과 같습니다.

- 카메라 이름과 위치
- SSH 호스트와 별칭
- 선호하는 TTS 음성
- 스피커/방 이름
- 기기 별명
- 환경별로만 해당하는 모든 것

## 예시

```markdown
### 카메라

- living-room → 메인 구역, 180° 광각
- front-door → 출입구, 동작 트리거

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- 선호 음성: "Nova" (따뜻하고, 약간 영국식)
- 기본 스피커: Kitchen HomePod
```

## 왜 분리하나요?

Skills는 공유됩니다. 당신의 설정은 당신만의 것입니다. 둘을 분리해 두면 메모를 잃지 않고 Skills를 업데이트할 수 있고, 인프라를 노출하지 않고 Skills를 공유할 수 있습니다.

---

업무에 도움이 되는 것은 무엇이든 추가하세요. 이것은 당신의 치트 시트입니다.
