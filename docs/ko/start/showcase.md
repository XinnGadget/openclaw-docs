---
read_when:
    - 실제 OpenClaw 사용 예시를 찾는 경우
    - 커뮤니티 프로젝트 하이라이트를 업데이트하는 경우
summary: OpenClaw로 구동되는 커뮤니티 제작 프로젝트와 통합
title: 쇼케이스
x-i18n:
    generated_at: "2026-04-05T12:56:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2917e9a476ef527ddb3e51c610bbafbd145e705c9cc29f191639fb63d238ef70
    source_path: start/showcase.md
    workflow: 15
---

# 쇼케이스

커뮤니티의 실제 프로젝트입니다. 사람들이 OpenClaw로 무엇을 만들고 있는지 확인해 보세요.

<Info>
**소개되고 싶으신가요?** 프로젝트를 [Discord의 #self-promotion](https://discord.gg/clawd)에 공유하거나 [X에서 @openclaw를 태그](https://x.com/openclaw)하세요.
</Info>

## 🎥 실제로 동작하는 OpenClaw

VelvetShark의 전체 설정 안내(28분)입니다.

<div
  style={{
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    overflow: "hidden",
    borderRadius: 16,
  }}
>
  <iframe
    src="https://www.youtube-nocookie.com/embed/SaWSPZoPX34"
    title="OpenClaw: Siri가 되었어야 할 셀프 호스팅 AI (전체 설정)"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
    frameBorder="0"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

[YouTube에서 보기](https://www.youtube.com/watch?v=SaWSPZoPX34)

<div
  style={{
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    overflow: "hidden",
    borderRadius: 16,
  }}
>
  <iframe
    src="https://www.youtube-nocookie.com/embed/mMSKQvlmFuQ"
    title="OpenClaw 쇼케이스 영상"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
    frameBorder="0"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

[YouTube에서 보기](https://www.youtube.com/watch?v=mMSKQvlmFuQ)

<div
  style={{
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    overflow: "hidden",
    borderRadius: 16,
  }}
>
  <iframe
    src="https://www.youtube-nocookie.com/embed/5kkIJNUGFho"
    title="OpenClaw 커뮤니티 쇼케이스"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
    frameBorder="0"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

[YouTube에서 보기](https://www.youtube.com/watch?v=5kkIJNUGFho)

## 🆕 Discord의 최신 소식

<CardGroup cols={2}>

<Card title="PR 검토 → Telegram 피드백" icon="code-pull-request" href="https://x.com/i/status/2010878524543131691">
  **@bangnokia** • `review` `github` `telegram`

OpenCode가 변경을 완료 → PR을 엶 → OpenClaw가 diff를 검토하고 Telegram에서 “사소한 제안”과 함께 명확한 병합 판정(먼저 적용해야 할 중요한 수정 포함)을 답장합니다.

  <img src="/assets/showcase/pr-review-telegram.jpg" alt="Telegram으로 전달된 OpenClaw PR 검토 피드백" />
</Card>

<Card title="몇 분 만에 만드는 와인 셀러 Skill" icon="wine-glass" href="https://x.com/i/status/2010916352454791216">
  **@prades_maxime** • `skills` `local` `csv`

“Robby”(@openclaw)에게 로컬 와인 셀러 skill을 요청했습니다. 샘플 CSV 내보내기와 저장 위치를 요청한 다음, 빠르게 skill을 빌드/테스트합니다(예시에서는 962병).

  <img src="/assets/showcase/wine-cellar-skill.jpg" alt="CSV로 로컬 와인 셀러 skill을 빌드하는 OpenClaw" />
</Card>

<Card title="Tesco 쇼핑 오토파일럿" icon="cart-shopping" href="https://x.com/i/status/2009724862470689131">
  **@marchattonhere** • `automation` `browser` `shopping`

주간 식단 계획 → 단골 품목 → 배송 시간 예약 → 주문 확인. API 없이 브라우저 제어만 사용합니다.

  <img src="/assets/showcase/tesco-shop.jpg" alt="채팅을 통한 Tesco 쇼핑 자동화" />
</Card>

<Card title="SNAG 스크린샷-마크다운" icon="scissors" href="https://github.com/am-will/snag">
  **@am-will** • `devtools` `screenshots` `markdown`

화면 영역을 단축키로 선택 → Gemini vision → 클립보드에 즉시 Markdown.

  <img src="/assets/showcase/snag.png" alt="SNAG 스크린샷-마크다운 도구" />
</Card>

<Card title="Agents UI" icon="window-maximize" href="https://releaseflow.net/kitze/agents-ui">
  **@kitze** • `ui` `skills` `sync`

Agents, Claude, Codex, OpenClaw 전반에서 skills/commands를 관리하는 데스크톱 앱입니다.

  <img src="/assets/showcase/agents-ui.jpg" alt="Agents UI 앱" />
</Card>

<Card title="Telegram 음성 노트 (papla.media)" icon="microphone" href="https://papla.media/docs">
  **커뮤니티** • `voice` `tts` `telegram`

papla.media TTS를 감싸고 결과를 Telegram 음성 노트로 전송합니다(귀찮은 자동 재생 없음).

  <img src="/assets/showcase/papla-tts.jpg" alt="TTS의 Telegram 음성 노트 출력" />
</Card>

<Card title="CodexMonitor" icon="eye" href="https://clawhub.ai/odrobnik/codexmonitor">
  **@odrobnik** • `devtools` `codex` `brew`

로컬 OpenAI Codex 세션을 나열/검사/감시하는 Homebrew 설치 도우미(CLI + VS Code).

  <img src="/assets/showcase/codexmonitor.png" alt="ClawHub의 CodexMonitor" />
</Card>

<Card title="Bambu 3D 프린터 제어" icon="print" href="https://clawhub.ai/tobiasbischoff/bambu-cli">
  **@tobiasbischoff** • `hardware` `3d-printing` `skill`

BambuLab 프린터의 상태, 작업, 카메라, AMS, 보정 등을 제어하고 문제를 해결합니다.

  <img src="/assets/showcase/bambu-cli.png" alt="ClawHub의 Bambu CLI skill" />
</Card>

<Card title="비엔나 교통 (Wiener Linien)" icon="train" href="https://clawhub.ai/hjanuschka/wienerlinien">
  **@hjanuschka** • `travel` `transport` `skill`

비엔나 대중교통의 실시간 출발 정보, 장애, 엘리베이터 상태, 경로 안내를 제공합니다.

  <img src="/assets/showcase/wienerlinien.png" alt="Wiener Linien skill" />
</Card>

<Card title="ParentPay 학교 급식" icon="utensils" href="#">
  **@George5562** • `automation` `browser` `parenting`

ParentPay를 통한 영국 학교 급식 예약 자동화. 테이블 셀을 안정적으로 클릭하기 위해 마우스 좌표를 사용합니다.
</Card>

<Card title="R2 업로드 (내 파일 보내기)" icon="cloud-arrow-up" href="https://clawhub.ai/skills/r2-upload">
  **@julianengel** • `files` `r2` `presigned-urls`

Cloudflare R2/S3에 업로드하고 안전한 presigned 다운로드 링크를 생성합니다. 원격 OpenClaw 인스턴스에 적합합니다.
</Card>

<Card title="Telegram으로 iOS 앱 만들기" icon="mobile" href="#">
  **@coard** • `ios` `xcode` `testflight`

지도와 음성 녹음을 포함한 완전한 iOS 앱을 빌드하고, 전부 Telegram 채팅만으로 TestFlight에 배포했습니다.

  <img src="/assets/showcase/ios-testflight.jpg" alt="TestFlight의 iOS 앱" />
</Card>

<Card title="Oura Ring 건강 어시스턴트" icon="heart-pulse" href="#">
  **@AS** • `health` `oura` `calendar`

Oura ring 데이터와 캘린더, 약속, 운동 일정을 통합한 개인 AI 건강 어시스턴트입니다.

  <img src="/assets/showcase/oura-health.png" alt="Oura ring 건강 어시스턴트" />
</Card>
<Card title="Kev의 드림 팀 (14개 이상 에이전트)" icon="robot" href="https://github.com/adam91holt/orchestrated-ai-articles">
  **@adam91holt** • `multi-agent` `orchestration` `architecture` `manifesto`

하나의 gateway 아래 14개 이상의 에이전트가 있으며, Opus 4.5 오케스트레이터가 Codex 워커에게 작업을 위임합니다. Dream Team 구성, 모델 선택, 샌드박싱, 웹훅, 하트비트, 위임 흐름을 다루는 포괄적인 [기술 문서](https://github.com/adam91holt/orchestrated-ai-articles)가 있습니다. 에이전트 샌드박싱용 [Clawdspace](https://github.com/adam91holt/clawdspace)도 있습니다. [블로그 글](https://adams-ai-journey.ghost.io/2026-the-year-of-the-orchestrator/).
</Card>

<Card title="Linear CLI" icon="terminal" href="https://github.com/Finesssee/linear-cli">
  **@NessZerra** • `devtools` `linear` `cli` `issues`

에이전트 워크플로(Claude Code, OpenClaw)와 통합되는 Linear용 CLI입니다. 터미널에서 이슈, 프로젝트, 워크플로를 관리할 수 있습니다. 첫 외부 PR이 병합되었습니다!
</Card>

<Card title="Beeper CLI" icon="message" href="https://github.com/blqke/beepcli">
  **@jules** • `messaging` `beeper` `cli` `automation`

Beeper Desktop을 통해 메시지를 읽고, 보내고, 보관합니다. Beeper 로컬 MCP API를 사용하므로 에이전트가 iMessage, WhatsApp 등 모든 채팅을 한곳에서 관리할 수 있습니다.
</Card>

</CardGroup>

## 🤖 자동화 및 워크플로

<CardGroup cols={2}>

<Card title="Winix 공기청정기 제어" icon="wind" href="https://x.com/antonplex/status/2010518442471006253">
  **@antonplex** • `automation` `hardware` `air-quality`

Claude Code가 공기청정기 제어 기능을 찾아 확인한 다음, OpenClaw가 이를 이어받아 실내 공기질을 관리합니다.

  <img src="/assets/showcase/winix-air-purifier.jpg" alt="OpenClaw를 통한 Winix 공기청정기 제어" />
</Card>

<Card title="예쁜 하늘 카메라 샷" icon="camera" href="https://x.com/signalgaining/status/2010523120604746151">
  **@signalgaining** • `automation` `camera` `skill` `images`

옥상 카메라에 의해 트리거됨: 하늘이 예쁠 때마다 하늘 사진을 찍어 달라고 OpenClaw에 요청하면, 직접 skill을 설계하고 촬영까지 했습니다.

  <img src="/assets/showcase/roof-camera-sky.jpg" alt="OpenClaw가 촬영한 옥상 카메라 하늘 스냅샷" />
</Card>

<Card title="시각적 아침 브리핑 장면" icon="robot" href="https://x.com/buddyhadry/status/2010005331925954739">
  **@buddyhadry** • `automation` `briefing` `images` `telegram`

예약된 프롬프트가 OpenClaw 페르소나를 통해 매일 아침 하나의 "장면" 이미지를 생성합니다(날씨, 작업, 날짜, 좋아하는 게시물/인용문).
</Card>

<Card title="Padel 코트 예약" icon="calendar-check" href="https://github.com/joshp123/padel-cli">
  **@joshp123** • `automation` `booking` `cli`
  
  Playtomic 이용 가능 여부 확인 + 예약 CLI입니다. 다시는 빈 코트를 놓치지 마세요.
  
  <img src="/assets/showcase/padel-screenshot.jpg" alt="padel-cli 스크린샷" />
</Card>

<Card title="회계 자료 수집" icon="file-invoice-dollar">
  **커뮤니티** • `automation` `email` `pdf`
  
  이메일에서 PDF를 수집하고, 세무사에게 보낼 문서를 준비합니다. 월간 회계 업무를 자동 조종으로 처리합니다.
</Card>

<Card title="소파 감자 개발 모드" icon="couch" href="https://davekiss.com">
  **@davekiss** • `telegram` `website` `migration` `astro`

Netflix를 보면서 Telegram만으로 개인 사이트 전체를 재구축했습니다 — Notion → Astro, 게시물 18개 이전, DNS를 Cloudflare로 이동. 노트북은 한 번도 열지 않았습니다.
</Card>

<Card title="구직 에이전트" icon="briefcase">
  **@attol8** • `automation` `api` `skill`

구인 목록을 검색하고, 이력서 키워드와 매칭하여, 관련 기회를 링크와 함께 반환합니다. JSearch API로 30분 만에 만들었습니다.
</Card>

<Card title="Jira Skill 빌더" icon="diagram-project" href="https://x.com/jdrhyne/status/2008336434827002232">
  **@jdrhyne** • `automation` `jira` `skill` `devtools`

OpenClaw가 Jira에 연결된 뒤, 즉석에서 새 skill을 생성했습니다(ClawHub에 존재하기도 전).
</Card>

<Card title="Telegram을 통한 Todoist Skill" icon="list-check" href="https://x.com/iamsubhrajyoti/status/2009949389884920153">
  **@iamsubhrajyoti** • `automation` `todoist` `skill` `telegram`

Todoist 작업을 자동화하고 OpenClaw가 Telegram 채팅에서 직접 skill을 생성하도록 했습니다.
</Card>

<Card title="TradingView 분석" icon="chart-line">
  **@bheem1798** • `finance` `browser` `automation`

브라우저 자동화로 TradingView에 로그인하고, 차트 스크린샷을 찍고, 요청 시 기술적 분석을 수행합니다. API는 필요 없고 브라우저 제어만 있으면 됩니다.
</Card>

<Card title="Slack 자동 지원" icon="slack">
  **@henrymascot** • `slack` `automation` `support`

회사 Slack 채널을 모니터링하고, 도움이 되는 답변을 하며, 알림을 Telegram으로 전달합니다. 요청받지 않았는데도 배포된 앱의 프로덕션 버그를 자율적으로 수정했습니다.
</Card>

</CardGroup>

## 🧠 지식 및 메모리

<CardGroup cols={2}>

<Card title="xuezh 중국어 학습" icon="language" href="https://github.com/joshp123/xuezh">
  **@joshp123** • `learning` `voice` `skill`
  
  OpenClaw를 통한 발음 피드백 및 학습 흐름을 갖춘 중국어 학습 엔진입니다.
  
  <img src="/assets/showcase/xuezh-pronunciation.jpeg" alt="xuezh 발음 피드백" />
</Card>

<Card title="WhatsApp 메모리 금고" icon="vault">
  **커뮤니티** • `memory` `transcription` `indexing`
  
  전체 WhatsApp 내보내기를 가져오고, 1천 개 이상의 음성 노트를 전사하며, git 로그와 교차 확인한 뒤, 링크된 markdown 보고서를 출력합니다.
</Card>

<Card title="Karakeep 시맨틱 검색" icon="magnifying-glass" href="https://github.com/jamesbrooksco/karakeep-semantic-search">
  **@jamesbrooksco** • `search` `vector` `bookmarks`
  
  Qdrant + OpenAI/Ollama 임베딩을 사용해 Karakeep 북마크에 벡터 검색을 추가합니다.
</Card>

<Card title="Inside-Out-2 메모리" icon="brain">
  **커뮤니티** • `memory` `beliefs` `self-model`
  
  세션 파일을 기억 → 신념 → 진화하는 자기 모델로 바꾸는 별도 메모리 관리자입니다.
</Card>

</CardGroup>

## 🎙️ 음성 및 전화

<CardGroup cols={2}>

<Card title="Clawdia 전화 브리지" icon="phone" href="https://github.com/alejandroOPI/clawdia-bridge">
  **@alejandroOPI** • `voice` `vapi` `bridge`
  
  Vapi 음성 어시스턴트 ↔ OpenClaw HTTP 브리지입니다. 에이전트와 거의 실시간에 가까운 전화 통화를 할 수 있습니다.
</Card>

<Card title="OpenRouter 전사" icon="microphone" href="https://clawhub.ai/obviyus/openrouter-transcribe">
  **@obviyus** • `transcription` `multilingual` `skill`

OpenRouter(Gemini 등)를 통한 다국어 오디오 전사입니다. ClawHub에서 사용할 수 있습니다.
</Card>

</CardGroup>

## 🏗️ 인프라 및 배포

<CardGroup cols={2}>

<Card title="Home Assistant 애드온" icon="home" href="https://github.com/ngutman/openclaw-ha-addon">
  **@ngutman** • `homeassistant` `docker` `raspberry-pi`
  
  SSH 터널 지원과 영구 상태를 갖춘 Home Assistant OS에서 실행되는 OpenClaw gateway입니다.
</Card>

<Card title="Home Assistant Skill" icon="toggle-on" href="https://clawhub.ai/skills/homeassistant">
  **ClawHub** • `homeassistant` `skill` `automation`
  
  자연어로 Home Assistant 장치를 제어하고 자동화합니다.
</Card>

<Card title="Nix 패키징" icon="snowflake" href="https://github.com/openclaw/nix-openclaw">
  **@openclaw** • `nix` `packaging` `deployment`
  
  재현 가능한 배포를 위한 배터리 포함형 nix 기반 OpenClaw 구성입니다.
</Card>

<Card title="CalDAV 캘린더" icon="calendar" href="https://clawhub.ai/skills/caldav-calendar">
  **ClawHub** • `calendar` `caldav` `skill`
  
  khal/vdirsyncer를 사용하는 캘린더 skill입니다. 자체 호스팅 캘린더 통합입니다.
</Card>

</CardGroup>

## 🏠 홈 및 하드웨어

<CardGroup cols={2}>

<Card title="GoHome 자동화" icon="house-signal" href="https://github.com/joshp123/gohome">
  **@joshp123** • `home` `nix` `grafana`
  
  인터페이스로 OpenClaw를 사용하는 Nix 네이티브 홈 자동화이며, 아름다운 Grafana 대시보드도 제공합니다.
  
  <img src="/assets/showcase/gohome-grafana.png" alt="GoHome Grafana 대시보드" />
</Card>

<Card title="Roborock 청소기" icon="robot" href="https://github.com/joshp123/gohome/tree/main/plugins/roborock">
  **@joshp123** • `vacuum` `iot` `plugin`
  
  자연스러운 대화를 통해 Roborock 로봇 청소기를 제어하세요.
  
  <img src="/assets/showcase/roborock-screenshot.jpg" alt="Roborock 상태" />
</Card>

</CardGroup>

## 🌟 커뮤니티 프로젝트

<CardGroup cols={2}>

<Card title="StarSwap 마켓플레이스" icon="star" href="https://star-swap.com/">
  **커뮤니티** • `marketplace` `astronomy` `webapp`
  
  완전한 천문 장비 마켓플레이스입니다. OpenClaw 생태계를 기반으로/중심으로 구축되었습니다.
</Card>

</CardGroup>

---

## 프로젝트 제출하기

공유할 것이 있나요? 소개하고 싶습니다!

<Steps>
  <Step title="공유하기">
    [Discord의 #self-promotion](https://discord.gg/clawd)에 게시하거나 [@openclaw에 트윗](https://x.com/openclaw)하세요
  </Step>
  <Step title="세부 정보 포함하기">
    무엇을 하는지 설명하고, 저장소/데모 링크를 추가하고, 가능하다면 스크린샷도 공유해 주세요
  </Step>
  <Step title="소개되기">
    눈에 띄는 프로젝트를 이 페이지에 추가하겠습니다
  </Step>
</Steps>
