---
read_when:
    - 서드파티 OpenClaw plugins를 찾으려는 경우
    - 직접 plugin을 게시하거나 목록에 올리고 싶은 경우
summary: '커뮤니티 유지 관리 OpenClaw plugins: 찾아보기, 설치하기, 직접 제출하기'
title: 커뮤니티 Plugins
x-i18n:
    generated_at: "2026-04-05T12:49:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 01804563a63399fe564b0cd9b9aadef32e5211b63d8467fdbbd1f988200728de
    source_path: plugins/community.md
    workflow: 15
---

# 커뮤니티 Plugins

커뮤니티 plugins는 새로운 채널, tools, providers 또는 기타 기능으로 OpenClaw를 확장하는 서드파티 패키지입니다. 이들은 커뮤니티가 빌드하고 유지 관리하며, [ClawHub](/tools/clawhub) 또는 npm에 게시되고, 한 줄 명령으로 설치할 수 있습니다.

ClawHub는 커뮤니티 plugins의 정식 검색 표면입니다. 단지 검색 가능하게 하려고 여기 이 페이지에 plugin을 추가하는 docs-only PR은 열지 마세요. 대신 ClawHub에 게시하세요.

```bash
openclaw plugins install <package-name>
```

OpenClaw는 먼저 ClawHub를 확인하고 자동으로 npm으로 폴백합니다.

## 등록된 plugins

### Codex App Server Bridge

Codex App Server 대화를 위한 독립형 OpenClaw 브리지입니다. 채팅을 Codex 스레드에 바인딩하고, 일반 텍스트로 대화하며, 재개, 계획, 리뷰, 모델 선택, 압축 등 다양한 기능을 채팅 네이티브 명령으로 제어할 수 있습니다.

- **npm:** `openclaw-codex-app-server`
- **repo:** [github.com/pwrdrvr/openclaw-codex-app-server](https://github.com/pwrdrvr/openclaw-codex-app-server)

```bash
openclaw plugins install openclaw-codex-app-server
```

### DingTalk

Stream 모드를 사용하는 엔터프라이즈 로봇 통합입니다. 모든 DingTalk 클라이언트를 통해 텍스트, 이미지, 파일 메시지를 지원합니다.

- **npm:** `@largezhou/ddingtalk`
- **repo:** [github.com/largezhou/openclaw-dingtalk](https://github.com/largezhou/openclaw-dingtalk)

```bash
openclaw plugins install @largezhou/ddingtalk
```

### Lossless Claw (LCM)

OpenClaw용 무손실 컨텍스트 관리 plugin입니다. DAG 기반 대화 요약과 증분 압축을 통해 전체 컨텍스트 충실도를 유지하면서 토큰 사용량을 줄입니다.

- **npm:** `@martian-engineering/lossless-claw`
- **repo:** [github.com/Martian-Engineering/lossless-claw](https://github.com/Martian-Engineering/lossless-claw)

```bash
openclaw plugins install @martian-engineering/lossless-claw
```

### Opik

에이전트 trace를 Opik으로 내보내는 공식 plugin입니다. 에이전트 동작, 비용, 토큰, 오류 등을 모니터링할 수 있습니다.

- **npm:** `@opik/opik-openclaw`
- **repo:** [github.com/comet-ml/opik-openclaw](https://github.com/comet-ml/opik-openclaw)

```bash
openclaw plugins install @opik/opik-openclaw
```

### QQbot

QQ Bot API를 통해 OpenClaw를 QQ에 연결합니다. 개인 채팅, 그룹 멘션, 채널 메시지, 음성, 이미지, 비디오, 파일을 포함한 리치 미디어를 지원합니다.

- **npm:** `@tencent-connect/openclaw-qqbot`
- **repo:** [github.com/tencent-connect/openclaw-qqbot](https://github.com/tencent-connect/openclaw-qqbot)

```bash
openclaw plugins install @tencent-connect/openclaw-qqbot
```

### wecom

Tencent WeCom 팀이 만든 OpenClaw용 WeCom 채널 plugin입니다. WeCom Bot WebSocket 지속 연결로 구동되며, 다이렉트 메시지 및 그룹 채팅, 스트리밍 응답, 선제적 메시징, 이미지/파일 처리, Markdown 서식, 내장 액세스 제어, 문서/회의/메시징 Skills를 지원합니다.

- **npm:** `@wecom/wecom-openclaw-plugin`
- **repo:** [github.com/WecomTeam/wecom-openclaw-plugin](https://github.com/WecomTeam/wecom-openclaw-plugin)

```bash
openclaw plugins install @wecom/wecom-openclaw-plugin
```

## plugin 제출하기

유용하고, 문서화되어 있으며, 안전하게 운영할 수 있는 커뮤니티 plugins를 환영합니다.

<Steps>
  <Step title="ClawHub 또는 npm에 게시">
    plugin은 `openclaw plugins install \<package-name\>`으로 설치 가능해야 합니다.
    [ClawHub](/tools/clawhub)(권장) 또는 npm에 게시하세요.
    전체 가이드는 [Building Plugins](/plugins/building-plugins)를 참조하세요.

  </Step>

  <Step title="GitHub에 호스팅">
    소스 코드는 공개 리포지토리에 있어야 하며, 설정 문서와 이슈 트래커를 포함해야 합니다.

  </Step>

  <Step title="소스 문서 변경에만 docs PR 사용">
    plugin을 검색 가능하게 만들기 위해 docs PR이 필요하지는 않습니다. 대신 ClawHub에 게시하세요.

    docs PR은 OpenClaw 소스 문서에 실제 콘텐츠 변경이 필요할 때만 열어야 합니다. 예를 들어 설치 가이드 수정이나 메인 문서 세트에 속하는 교차 리포지토리 문서 추가 같은 경우입니다.

  </Step>
</Steps>

## 품질 기준

| 요구 사항 | 이유 |
| --------------------------- | --------------------------------------------- |
| ClawHub 또는 npm에 게시됨 | 사용자가 `openclaw plugins install`을 사용할 수 있어야 함 |
| 공개 GitHub repo | 소스 검토, 이슈 추적, 투명성 |
| 설정 및 사용 문서 | 사용자가 구성 방법을 알아야 함 |
| 활발한 유지 관리 | 최근 업데이트 또는 응답성 있는 이슈 처리 |

낮은 노력의 래퍼, 불분명한 소유권, 유지 관리되지 않는 패키지는 거절될 수 있습니다.

## 관련 문서

- [Plugins 설치 및 구성](/tools/plugin) — 모든 plugin 설치 방법
- [Building Plugins](/plugins/building-plugins) — 직접 만들기
- [Plugin Manifest](/plugins/manifest) — manifest 스키마
