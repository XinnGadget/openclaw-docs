---
read_when:
    - OpenClaw를 새 노트북/서버로 옮기고 있는 경우
    - 세션, 인증, 채널 로그인(WhatsApp 등)을 유지하려는 경우
summary: 한 머신의 OpenClaw 설치를 다른 머신으로 이동(마이그레이션)하기
title: 마이그레이션 가이드
x-i18n:
    generated_at: "2026-04-05T12:46:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 403f0b9677ce723c84abdbabfad20e0f70fd48392ebf23eabb7f8a111fd6a26d
    source_path: install/migrating.md
    workflow: 15
---

# OpenClaw를 새 머신으로 마이그레이션하기

이 가이드는 온보딩을 다시 하지 않고 OpenClaw gateway를 새 머신으로 옮기는 방법을 설명합니다.

## 마이그레이션되는 항목

**상태 디렉터리**(기본값 `~/.openclaw/`)와 **workspace**를 복사하면 다음이 유지됩니다.

- **Config** -- `openclaw.json` 및 모든 gateway 설정
- **Auth** -- 에이전트별 `auth-profiles.json`(API 키 + OAuth), 그리고 `credentials/` 아래의 채널/provider 상태
- **세션** -- 대화 기록 및 에이전트 상태
- **채널 상태** -- WhatsApp 로그인, Telegram 세션 등
- **Workspace 파일** -- `MEMORY.md`, `USER.md`, Skills, 프롬프트

<Tip>
이전 머신에서 `openclaw status`를 실행해 상태 디렉터리 경로를 확인하세요.
사용자 지정 프로필은 `~/.openclaw-<profile>/` 또는 `OPENCLAW_STATE_DIR`로 설정된 경로를 사용합니다.
</Tip>

## 마이그레이션 단계

<Steps>
  <Step title="gateway 중지 및 백업">
    **이전** 머신에서 파일이 복사 중 변경되지 않도록 gateway를 중지한 다음, 아카이브합니다.

    ```bash
    openclaw gateway stop
    cd ~
    tar -czf openclaw-state.tgz .openclaw
    ```

    여러 프로필(예: `~/.openclaw-work`)을 사용하는 경우 각각 따로 아카이브하세요.

  </Step>

  <Step title="새 머신에 OpenClaw 설치">
    새 머신에 CLI를(필요하면 Node도) [설치](/install)하세요.
    온보딩이 새 `~/.openclaw/`를 생성해도 괜찮습니다. 다음 단계에서 이를 덮어쓰게 됩니다.
  </Step>

  <Step title="상태 디렉터리와 workspace 복사">
    `scp`, `rsync -a` 또는 외장 드라이브로 아카이브를 전송한 다음 압축을 풉니다.

    ```bash
    cd ~
    tar -xzf openclaw-state.tgz
    ```

    숨김 디렉터리가 포함되었는지, 그리고 파일 소유권이 gateway를 실행할 사용자와 일치하는지 확인하세요.

  </Step>

  <Step title="doctor 실행 및 확인">
    새 머신에서 [Doctor](/gateway/doctor)를 실행해 config 마이그레이션을 적용하고 서비스를 복구합니다.

    ```bash
    openclaw doctor
    openclaw gateway restart
    openclaw status
    ```

  </Step>
</Steps>

## 일반적인 함정

<AccordionGroup>
  <Accordion title="프로필 또는 state-dir 불일치">
    이전 gateway가 `--profile` 또는 `OPENCLAW_STATE_DIR`를 사용했는데 새 환경에서는 그렇지 않다면,
    채널은 로그아웃된 것처럼 보이고 세션은 비어 있게 됩니다.
    마이그레이션한 것과 **같은** 프로필 또는 state-dir로 gateway를 실행한 다음 `openclaw doctor`를 다시 실행하세요.
  </Accordion>

  <Accordion title="openclaw.json만 복사하는 경우">
    config 파일만으로는 충분하지 않습니다. 모델 인증 프로필은
    `agents/<agentId>/agent/auth-profiles.json` 아래에 있고, 채널/provider 상태는 여전히
    `credentials/` 아래에 있습니다. 항상 상태 디렉터리 **전체**를 마이그레이션하세요.
  </Accordion>

  <Accordion title="권한 및 소유권">
    루트로 복사했거나 사용자를 변경한 경우, gateway가 자격 증명을 읽지 못할 수 있습니다.
    상태 디렉터리와 workspace가 gateway를 실행하는 사용자 소유인지 확인하세요.
  </Accordion>

  <Accordion title="원격 모드">
    UI가 **원격** gateway를 가리키는 경우, 세션과 workspace는 원격 호스트가 소유합니다.
    로컬 노트북이 아니라 gateway 호스트 자체를 마이그레이션하세요. [FAQ](/help/faq#where-things-live-on-disk)를 참조하세요.
  </Accordion>

  <Accordion title="백업에 포함된 secrets">
    상태 디렉터리에는 인증 프로필, 채널 자격 증명, 기타 provider 상태가 포함됩니다.
    백업은 암호화해 저장하고, 안전하지 않은 전송 채널은 피하며, 노출이 의심되면 키를 교체하세요.
  </Accordion>
</AccordionGroup>

## 확인 체크리스트

새 머신에서 다음을 확인하세요.

- [ ] `openclaw status`에 gateway가 실행 중으로 표시됨
- [ ] 채널이 여전히 연결되어 있음(재페어링 불필요)
- [ ] dashboard가 열리고 기존 세션이 표시됨
- [ ] Workspace 파일(memory, configs)이 존재함
