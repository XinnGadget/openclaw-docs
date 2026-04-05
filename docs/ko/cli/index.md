---
read_when:
    - CLI 명령이나 옵션을 추가하거나 수정하는 경우
    - 새 명령 표면을 문서화하는 경우
summary: '`openclaw` 명령, 하위 명령, 옵션을 위한 OpenClaw CLI 참조'
title: CLI 참조
x-i18n:
    generated_at: "2026-04-05T12:41:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7c25e5ebfe256412b44130dba39cf39b0a7d1d22e3abb417345e95c95ca139bf
    source_path: cli/index.md
    workflow: 15
---

# CLI 참조

이 페이지는 현재 CLI 동작을 설명합니다. 명령이 변경되면 이 문서를 업데이트하세요.

## 명령 페이지

- [`setup`](/cli/setup)
- [`onboard`](/cli/onboard)
- [`configure`](/cli/configure)
- [`config`](/cli/config)
- [`completion`](/cli/completion)
- [`doctor`](/cli/doctor)
- [`dashboard`](/cli/dashboard)
- [`backup`](/cli/backup)
- [`reset`](/cli/reset)
- [`uninstall`](/cli/uninstall)
- [`update`](/cli/update)
- [`message`](/cli/message)
- [`agent`](/cli/agent)
- [`agents`](/cli/agents)
- [`acp`](/cli/acp)
- [`mcp`](/cli/mcp)
- [`status`](/cli/status)
- [`health`](/cli/health)
- [`sessions`](/cli/sessions)
- [`gateway`](/cli/gateway)
- [`logs`](/cli/logs)
- [`system`](/cli/system)
- [`models`](/cli/models)
- [`memory`](/cli/memory)
- [`directory`](/cli/directory)
- [`nodes`](/cli/nodes)
- [`devices`](/cli/devices)
- [`node`](/cli/node)
- [`approvals`](/cli/approvals)
- [`sandbox`](/cli/sandbox)
- [`tui`](/cli/tui)
- [`browser`](/cli/browser)
- [`cron`](/cli/cron)
- [`tasks`](/cli/index#tasks)
- [`flows`](/cli/flows)
- [`dns`](/cli/dns)
- [`docs`](/cli/docs)
- [`hooks`](/cli/hooks)
- [`webhooks`](/cli/webhooks)
- [`pairing`](/cli/pairing)
- [`qr`](/cli/qr)
- [`plugins`](/cli/plugins) (plugin 명령)
- [`channels`](/cli/channels)
- [`security`](/cli/security)
- [`secrets`](/cli/secrets)
- [`skills`](/cli/skills)
- [`daemon`](/cli/daemon) (gateway 서비스 명령의 레거시 별칭)
- [`clawbot`](/cli/clawbot) (레거시 별칭 네임스페이스)
- [`voicecall`](/cli/voicecall) (plugin, 설치된 경우)

## 전역 플래그

- `--dev`: 상태를 `~/.openclaw-dev` 아래로 격리하고 기본 포트를 이동합니다.
- `--profile <name>`: 상태를 `~/.openclaw-<name>` 아래로 격리합니다.
- `--container <name>`: 실행 대상의 이름 있는 컨테이너를 지정합니다.
- `--no-color`: ANSI 색상을 비활성화합니다.
- `--update`: `openclaw update`의 단축형(소스 설치 전용).
- `-V`, `--version`, `-v`: 버전을 출력하고 종료합니다.

## 출력 스타일링

- ANSI 색상과 진행 표시기는 TTY 세션에서만 렌더링됩니다.
- OSC-8 하이퍼링크는 지원되는 터미널에서는 클릭 가능한 링크로 렌더링되며, 그렇지 않으면 일반 URL로 대체됩니다.
- `--json`(및 지원되는 경우 `--plain`)은 깔끔한 출력을 위해 스타일링을 비활성화합니다.
- `--no-color`는 ANSI 스타일링을 비활성화하며, `NO_COLOR=1`도 존중됩니다.
- 오래 실행되는 명령은 진행 표시기(OSC 9;4 지원 시)를 표시합니다.

## 색상 팔레트

OpenClaw는 CLI 출력에 lobster 팔레트를 사용합니다.

- `accent` (#FF5A2D): 제목, 라벨, 기본 강조.
- `accentBright` (#FF7A3D): 명령 이름, 강조.
- `accentDim` (#D14A22): 보조 강조 텍스트.
- `info` (#FF8A5B): 정보성 값.
- `success` (#2FBF71): 성공 상태.
- `warn` (#FFB020): 경고, fallback, 주의.
- `error` (#E23D2D): 오류, 실패.
- `muted` (#8B7F77): 약조, 메타데이터.

팔레트의 단일 기준 출처: `src/terminal/palette.ts`(“lobster palette”).

## 명령 트리

```
openclaw [--dev] [--profile <name>] <command>
  setup
  onboard
  configure
  config
    get
    set
    unset
    file
    schema
    validate
  completion
  doctor
  dashboard
  backup
    create
    verify
  security
    audit
  secrets
    reload
    audit
    configure
    apply
  reset
  uninstall
  update
    wizard
    status
  channels
    list
    status
    capabilities
    resolve
    logs
    add
    remove
    login
    logout
  directory
    self
    peers list
    groups list|members
  skills
    search
    install
    update
    list
    info
    check
  plugins
    list
    inspect
    install
    uninstall
    update
    enable
    disable
    doctor
    marketplace list
  memory
    status
    index
    search
  message
    send
    broadcast
    poll
    react
    reactions
    read
    edit
    delete
    pin
    unpin
    pins
    permissions
    search
    thread create|list|reply
    emoji list|upload
    sticker send|upload
    role info|add|remove
    channel info|list
    member info
    voice status
    event list|create
    timeout
    kick
    ban
  agent
  agents
    list
    add
    delete
    bindings
    bind
    unbind
    set-identity
  acp
  mcp
    serve
    list
    show
    set
    unset
  status
  health
  sessions
    cleanup
  tasks
    list
    audit
    maintenance
    show
    notify
    cancel
    flow list|show|cancel
  gateway
    call
    usage-cost
    health
    status
    probe
    discover
    install
    uninstall
    start
    stop
    restart
    run
  daemon
    status
    install
    uninstall
    start
    stop
    restart
  logs
  system
    event
    heartbeat last|enable|disable
    presence
  models
    list
    status
    set
    set-image
    aliases list|add|remove
    fallbacks list|add|remove|clear
    image-fallbacks list|add|remove|clear
    scan
    auth add|login|login-github-copilot|setup-token|paste-token
    auth order get|set|clear
  sandbox
    list
    recreate
    explain
  cron
    status
    list
    add
    edit
    rm
    enable
    disable
    runs
    run
  nodes
    status
    describe
    list
    pending
    approve
    reject
    rename
    invoke
    notify
    push
    canvas snapshot|present|hide|navigate|eval
    canvas a2ui push|reset
    camera list|snap|clip
    screen record
    location get
  devices
    list
    remove
    clear
    approve
    reject
    rotate
    revoke
  node
    run
    status
    install
    uninstall
    stop
    restart
  approvals
    get
    set
    allowlist add|remove
  browser
    status
    start
    stop
    reset-profile
    tabs
    open
    focus
    close
    profiles
    create-profile
    delete-profile
    screenshot
    snapshot
    navigate
    resize
    click
    type
    press
    hover
    drag
    select
    upload
    fill
    dialog
    wait
    evaluate
    console
    pdf
  hooks
    list
    info
    check
    enable
    disable
    install
    update
  webhooks
    gmail setup|run
  pairing
    list
    approve
  qr
  clawbot
    qr
  docs
  dns
    setup
  tui
```

참고: plugin은 추가 최상위 명령을 더할 수 있습니다(예: `openclaw voicecall`).

## 보안

- `openclaw security audit` — 일반적인 보안 발목잡이를 기준으로 config + 로컬 상태를 감사합니다.
- `openclaw security audit --deep` — 최선의 노력 기반 라이브 Gateway 프로브입니다.
- `openclaw security audit --fix` — 안전한 기본값과 상태/config 권한을 강화합니다.

## Secrets

### `secrets`

SecretRef 및 관련 런타임/config 위생을 관리합니다.

하위 명령:

- `secrets reload`
- `secrets audit`
- `secrets configure`
- `secrets apply --from <path>`

`secrets reload` 옵션:

- `--url`, `--token`, `--timeout`, `--expect-final`, `--json`

`secrets audit` 옵션:

- `--check`
- `--allow-exec`
- `--json`

`secrets configure` 옵션:

- `--apply`
- `--yes`
- `--providers-only`
- `--skip-provider-setup`
- `--agent <id>`
- `--allow-exec`
- `--plan-out <path>`
- `--json`

`secrets apply --from <path>` 옵션:

- `--dry-run`
- `--allow-exec`
- `--json`

참고:

- `reload`는 Gateway RPC이며, 해상 실패 시 마지막으로 정상 동작한 런타임 스냅샷을 유지합니다.
- `audit --check`는 발견 사항이 있으면 0이 아닌 값을 반환하며, 확인되지 않은 ref는 더 높은 우선순위의 0이 아닌 종료 코드를 사용합니다.
- 드라이런 exec 검사는 기본적으로 건너뜁니다. 사용하려면 `--allow-exec`로 옵트인하세요.

## Plugins

확장과 해당 config를 관리합니다.

- `openclaw plugins list` — plugin을 탐색합니다(기계용 출력에는 `--json` 사용).
- `openclaw plugins inspect <id>` — plugin 세부 정보를 표시합니다(`info`는 별칭).
- `openclaw plugins install <path|.tgz|npm-spec|plugin@marketplace>` — plugin을 설치합니다(또는 `plugins.load.paths`에 plugin 경로를 추가합니다. 기존 설치 대상을 덮어쓰려면 `--force` 사용).
- `openclaw plugins marketplace list <marketplace>` — 설치 전에 마켓플레이스 항목을 나열합니다.
- `openclaw plugins enable <id>` / `disable <id>` — `plugins.entries.<id>.enabled`를 전환합니다.
- `openclaw plugins doctor` — plugin 로드 오류를 보고합니다.

대부분의 plugin 변경에는 gateway 재시작이 필요합니다. [/plugin](/tools/plugin)을 참조하세요.

## Memory

`MEMORY.md` + `memory/*.md`에 대한 벡터 검색:

- `openclaw memory status` — 인덱스 통계를 표시합니다. 벡터 + 임베딩 준비 상태 검사에는 `--deep`, 오래된 회상/승격 아티팩트 수리에는 `--fix`를 사용하세요.
- `openclaw memory index` — 메모리 파일을 다시 인덱싱합니다.
- `openclaw memory search "<query>"`(또는 `--query "<query>"`) — 메모리에 대한 시맨틱 검색입니다.
- `openclaw memory promote` — 단기 회상을 순위화하고 선택적으로 상위 항목을 `MEMORY.md`에 추가합니다.

## Sandbox

격리된 agent 실행을 위한 sandbox 런타임을 관리합니다. [/cli/sandbox](/cli/sandbox)를 참조하세요.

하위 명령:

- `sandbox list [--browser] [--json]`
- `sandbox recreate [--all] [--session <key>] [--agent <id>] [--browser] [--force]`
- `sandbox explain [--session <key>] [--agent <id>] [--json]`

참고:

- `sandbox recreate`는 기존 런타임을 제거하므로 다음 사용 시 현재 config로 다시 시드됩니다.
- `ssh` 및 OpenShell `remote` 백엔드의 경우, recreate는 선택한 범위의 정식 원격 워크스페이스를 삭제합니다.

## 채팅 슬래시 명령

채팅 메시지는 `/...` 명령(텍스트 및 네이티브)을 지원합니다. [/tools/slash-commands](/tools/slash-commands)를 참조하세요.

주요 항목:

- 빠른 진단용 `/status`.
- 영속 config 변경용 `/config`.
- 런타임 전용 config 재정의용 `/debug`(메모리만, 디스크 아님, `commands.debug: true` 필요).

## 설정 + 온보딩

### `completion`

셸 자동완성 스크립트를 생성하고 선택적으로 셸 프로필에 설치합니다.

옵션:

- `-s, --shell <zsh|bash|powershell|fish>`
- `-i, --install`
- `--write-state`
- `-y, --yes`

참고:

- `--install` 또는 `--write-state`가 없으면 `completion`은 스크립트를 stdout에 출력합니다.
- `--install`은 셸 프로필에 `OpenClaw Completion` 블록을 기록하고 OpenClaw 상태 디렉터리 아래 캐시된 스크립트를 가리키게 합니다.

### `setup`

config + 워크스페이스를 초기화합니다.

옵션:

- `--workspace <dir>`: agent 워크스페이스 경로(기본값 `~/.openclaw/workspace`).
- `--wizard`: 온보딩 실행.
- `--non-interactive`: 프롬프트 없이 온보딩 실행.
- `--mode <local|remote>`: onboard 모드.
- `--remote-url <url>`: 원격 Gateway URL.
- `--remote-token <token>`: 원격 Gateway 토큰.

온보딩 플래그(`--non-interactive`, `--mode`, `--remote-url`, `--remote-token`)가 있으면 온보딩이 자동 실행됩니다.

### `onboard`

gateway, 워크스페이스, Skills를 위한 대화형 온보딩입니다.

옵션:

- `--workspace <dir>`
- `--reset` (온보딩 전에 config + 자격 증명 + 세션 초기화)
- `--reset-scope <config|config+creds+sessions|full>` (기본값 `config+creds+sessions`; 워크스페이스까지 제거하려면 `full` 사용)
- `--non-interactive`
- `--mode <local|remote>`
- `--flow <quickstart|advanced|manual>` (`manual`은 `advanced`의 별칭)
- `--auth-choice <choice>` 여기서 `<choice>`는 다음 중 하나입니다:
  `chutes`, `deepseek-api-key`, `openai-codex`, `openai-api-key`,
  `openrouter-api-key`, `kilocode-api-key`, `litellm-api-key`, `ai-gateway-api-key`,
  `cloudflare-ai-gateway-api-key`, `moonshot-api-key`, `moonshot-api-key-cn`,
  `kimi-code-api-key`, `synthetic-api-key`, `venice-api-key`, `together-api-key`,
  `huggingface-api-key`, `apiKey`, `gemini-api-key`, `google-gemini-cli`, `zai-api-key`,
  `zai-coding-global`, `zai-coding-cn`, `zai-global`, `zai-cn`, `xiaomi-api-key`,
  `minimax-global-oauth`, `minimax-global-api`, `minimax-cn-oauth`, `minimax-cn-api`,
  `opencode-zen`, `opencode-go`, `github-copilot`, `copilot-proxy`, `xai-api-key`,
  `mistral-api-key`, `volcengine-api-key`, `byteplus-api-key`, `qianfan-api-key`,
  `qwen-standard-api-key-cn`, `qwen-standard-api-key`, `qwen-api-key-cn`, `qwen-api-key`,
  `modelstudio-standard-api-key-cn`, `modelstudio-standard-api-key`,
  `modelstudio-api-key-cn`, `modelstudio-api-key`, `custom-api-key`, `skip`
- Qwen 참고: `qwen-*`가 정식 auth-choice 계열입니다. `modelstudio-*`
  ID는 레거시 호환성 별칭으로만 계속 허용됩니다.
- `--secret-input-mode <plaintext|ref>` (기본값 `plaintext`; provider 기본 env ref를 평문 키 대신 저장하려면 `ref` 사용)
- `--anthropic-api-key <key>`
- `--openai-api-key <key>`
- `--mistral-api-key <key>`
- `--openrouter-api-key <key>`
- `--ai-gateway-api-key <key>`
- `--moonshot-api-key <key>`
- `--kimi-code-api-key <key>`
- `--gemini-api-key <key>`
- `--zai-api-key <key>`
- `--minimax-api-key <key>`
- `--opencode-zen-api-key <key>`
- `--opencode-go-api-key <key>`
- `--custom-base-url <url>` (비대화형; `--auth-choice custom-api-key`와 함께 사용)
- `--custom-model-id <id>` (비대화형; `--auth-choice custom-api-key`와 함께 사용)
- `--custom-api-key <key>` (비대화형; 선택 사항; `--auth-choice custom-api-key`와 함께 사용; 생략 시 `CUSTOM_API_KEY` 사용)
- `--custom-provider-id <id>` (비대화형; 선택적 커스텀 provider id)
- `--custom-compatibility <openai|anthropic>` (비대화형; 선택 사항; 기본값 `openai`)
- `--gateway-port <port>`
- `--gateway-bind <loopback|lan|tailnet|auto|custom>`
- `--gateway-auth <token|password>`
- `--gateway-token <token>`
- `--gateway-token-ref-env <name>` (비대화형; `gateway.auth.token`을 env SecretRef로 저장; 해당 env 변수가 설정되어 있어야 하며 `--gateway-token`과 함께 사용할 수 없음)
- `--gateway-password <password>`
- `--remote-url <url>`
- `--remote-token <token>`
- `--tailscale <off|serve|funnel>`
- `--tailscale-reset-on-exit`
- `--install-daemon`
- `--no-install-daemon` (별칭: `--skip-daemon`)
- `--daemon-runtime <node|bun>`
- `--skip-channels`
- `--skip-skills`
- `--skip-search`
- `--skip-health`
- `--skip-ui`
- `--cloudflare-ai-gateway-account-id <id>`
- `--cloudflare-ai-gateway-gateway-id <id>`
- `--node-manager <npm|pnpm|bun>` (Skills용 setup/onboarding node manager; pnpm 권장, bun도 지원)
- `--json`

### `configure`

대화형 구성 마법사(모델, 채널, Skills, gateway).

옵션:

- `--section <section>` (반복 가능; 마법사를 특정 섹션으로 제한)

### `config`

비대화형 config 헬퍼(get/set/unset/file/schema/validate)입니다. 하위 명령 없이 `openclaw config`를 실행하면
마법사가 시작됩니다.

하위 명령:

- `config get <path>`: config 값을 출력합니다(점/대괄호 경로).
- `config set`: 네 가지 할당 모드를 지원합니다:
  - 값 모드: `config set <path> <value>` (JSON5 또는 문자열 파싱)
  - SecretRef 빌더 모드: `config set <path> --ref-provider <provider> --ref-source <source> --ref-id <id>`
  - provider 빌더 모드: `config set secrets.providers.<alias> --provider-source <env|file|exec> ...`
  - 배치 모드: `config set --batch-json '<json>'` 또는 `config set --batch-file <path>`
- `config set --dry-run`: `openclaw.json`을 쓰지 않고 할당을 검증합니다(exec SecretRef 검사는 기본적으로 건너뜀).
- `config set --allow-exec --dry-run`: exec SecretRef 드라이런 검사에 옵트인합니다(provider 명령을 실행할 수 있음).
- `config set --dry-run --json`: 기계가 읽을 수 있는 드라이런 출력(검사 + 완전성 신호, 작업, 확인/건너뜀 ref, 오류)을 내보냅니다.
- `config set --strict-json`: 경로/값 입력에 JSON5 파싱을 요구합니다. `--json`은 드라이런 출력 모드 밖에서는 엄격 파싱을 위한 레거시 별칭으로 유지됩니다.
- `config unset <path>`: 값을 제거합니다.
- `config file`: 활성 config 파일 경로를 출력합니다.
- `config schema`: 중첩 객체, 와일드카드, 배열 항목, 구성 브랜치 전반에 전파된 필드 `title` / `description` 문서 메타데이터와 최선의 노력 기반 라이브 plugin/channel 스키마 메타데이터를 포함하여 `openclaw.json`용 생성된 JSON 스키마를 출력합니다.
- `config validate`: gateway를 시작하지 않고 현재 config를 스키마에 대해 검증합니다.
- `config validate --json`: 기계가 읽을 수 있는 JSON 출력을 내보냅니다.

### `doctor`

상태 점검 + 빠른 수정(config + gateway + 레거시 서비스).

옵션:

- `--no-workspace-suggestions`: 워크스페이스 메모리 힌트를 비활성화합니다.
- `--yes`: 프롬프트 없이 기본값을 수락합니다(헤드리스).
- `--non-interactive`: 프롬프트를 건너뛰고 안전한 마이그레이션만 적용합니다.
- `--deep`: 추가 gateway 설치를 찾기 위해 시스템 서비스를 스캔합니다.
- `--repair` (별칭: `--fix`): 감지된 문제에 대해 자동 복구를 시도합니다.
- `--force`: 엄격히 필요하지 않아도 복구를 강제합니다.
- `--generate-gateway-token`: 새 gateway 인증 토큰을 생성합니다.

### `dashboard`

현재 토큰으로 Control UI를 엽니다.

옵션:

- `--no-open`: URL만 출력하고 브라우저는 실행하지 않습니다

참고:

- SecretRef로 관리되는 gateway 토큰의 경우, `dashboard`는 시크릿을 터미널 출력이나 브라우저 실행 인수에 노출하지 않도록 토큰이 포함되지 않은 URL을 출력하거나 엽니다.

### `update`

설치된 CLI를 업데이트합니다.

루트 옵션:

- `--json`
- `--no-restart`
- `--dry-run`
- `--channel <stable|beta|dev>`
- `--tag <dist-tag|version|spec>`
- `--timeout <seconds>`
- `--yes`

하위 명령:

- `update status`
- `update wizard`

`update status` 옵션:

- `--json`
- `--timeout <seconds>`

`update wizard` 옵션:

- `--timeout <seconds>`

참고:

- `openclaw --update`는 `openclaw update`로 재작성됩니다.

### `backup`

OpenClaw 상태의 로컬 백업 아카이브를 생성하고 검증합니다.

하위 명령:

- `backup create`
- `backup verify <archive>`

`backup create` 옵션:

- `--output <path>`
- `--json`
- `--dry-run`
- `--verify`
- `--only-config`
- `--no-include-workspace`

`backup verify <archive>` 옵션:

- `--json`

## 채널 헬퍼

### `channels`

채팅 채널 계정(WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (plugin)/Signal/iMessage/Microsoft Teams)을 관리합니다.

하위 명령:

- `channels list`: 구성된 채널과 auth profile을 표시합니다.
- `channels status`: gateway 도달 가능성과 채널 상태를 점검합니다(`--probe`는 gateway에 도달 가능한 경우 계정별 라이브 프로브/감사 검사를 실행하며, 그렇지 않으면 config 전용 채널 요약으로 대체합니다. 더 넓은 gateway 상태 프로브에는 `openclaw health` 또는 `openclaw status --deep`를 사용하세요).
- 팁: `channels status`는 일반적인 잘못된 구성을 감지할 수 있으면 수정 제안과 함께 경고를 출력합니다(그 후 `openclaw doctor`를 안내함).
- `channels logs`: gateway 로그 파일에서 최근 채널 로그를 표시합니다.
- `channels add`: 플래그를 전달하지 않으면 마법사형 설정을 사용하며, 플래그를 전달하면 비대화형 모드로 전환됩니다.
  - 단일 계정 최상위 config를 아직 사용하는 채널에 비기본 계정을 추가하면, OpenClaw는 새 계정을 쓰기 전에 계정 범위 값을 채널 계정 맵으로 승격합니다. 대부분의 채널은 `accounts.default`를 사용하며, Matrix는 기존의 일치하는 이름/기본 대상을 유지할 수 있습니다.
  - 비대화형 `channels add`는 바인딩을 자동 생성/업그레이드하지 않습니다. 채널 전용 바인딩은 기본 계정과 계속 일치합니다.
- `channels remove`: 기본적으로 비활성화만 하며, 프롬프트 없이 config 항목을 제거하려면 `--delete`를 전달하세요.
- `channels login`: 대화형 채널 로그인(WhatsApp Web 전용).
- `channels logout`: 채널 세션에서 로그아웃합니다(지원되는 경우).

공통 옵션:

- `--channel <name>`: `whatsapp|telegram|discord|googlechat|slack|mattermost|signal|imessage|msteams`
- `--account <id>`: 채널 계정 id(기본값 `default`)
- `--name <label>`: 계정 표시 이름

`channels login` 옵션:

- `--channel <channel>` (기본값 `whatsapp`; `whatsapp`/`web` 지원)
- `--account <id>`
- `--verbose`

`channels logout` 옵션:

- `--channel <channel>` (기본값 `whatsapp`)
- `--account <id>`

`channels list` 옵션:

- `--no-usage`: 모델 provider 사용량/할당량 스냅샷 건너뛰기(OAuth/API 기반만).
- `--json`: JSON 출력(`--no-usage` 설정 시 사용량 제외).

`channels status` 옵션:

- `--probe`
- `--timeout <ms>`
- `--json`

`channels capabilities` 옵션:

- `--channel <name>`
- `--account <id>` (`--channel`과 함께만 사용)
- `--target <dest>`
- `--timeout <ms>`
- `--json`

`channels resolve` 옵션:

- `<entries...>`
- `--channel <name>`
- `--account <id>`
- `--kind <auto|user|group>`
- `--json`

`channels logs` 옵션:

- `--channel <name|all>` (기본값 `all`)
- `--lines <n>` (기본값 `200`)
- `--json`

참고:

- `channels login`은 `--verbose`를 지원합니다.
- `channels capabilities --account`는 `--channel`이 설정된 경우에만 적용됩니다.
- `channels status --probe`는 채널 지원에 따라 `works`, `probe failed`, `audit ok`, `audit failed` 같은 전송 상태와 프로브/감사 결과를 표시할 수 있습니다.

자세한 내용: [/concepts/oauth](/concepts/oauth)

예시:

```bash
openclaw channels add --channel telegram --account alerts --name "Alerts Bot" --token $TELEGRAM_BOT_TOKEN
openclaw channels add --channel discord --account work --name "Work Bot" --token $DISCORD_BOT_TOKEN
openclaw channels remove --channel discord --account work --delete
openclaw channels status --probe
openclaw status --deep
```

### `directory`

디렉터리 표면을 제공하는 채널의 자기 자신, 피어, 그룹 ID를 조회합니다. [`openclaw directory`](/cli/directory)를 참조하세요.

공통 옵션:

- `--channel <name>`
- `--account <id>`
- `--json`

하위 명령:

- `directory self`
- `directory peers list [--query <text>] [--limit <n>]`
- `directory groups list [--query <text>] [--limit <n>]`
- `directory groups members --group-id <id> [--limit <n>]`

### `skills`

사용 가능한 Skills와 준비 상태 정보를 나열하고 검사합니다.

하위 명령:

- `skills search [query...]`: ClawHub Skills 검색.
- `skills search --limit <n> --json`: 검색 결과 수를 제한하거나 기계가 읽을 수 있는 출력을 내보냅니다.
- `skills install <slug>`: 활성 워크스페이스에 ClawHub Skill을 설치합니다.
- `skills install <slug> --version <version>`: 특정 ClawHub 버전을 설치합니다.
- `skills install <slug> --force`: 기존 워크스페이스 Skill 폴더를 덮어씁니다.
- `skills update <slug|--all>`: 추적 중인 ClawHub Skills를 업데이트합니다.
- `skills list`: Skills를 나열합니다(하위 명령이 없을 때 기본값).
- `skills list --json`: 기계가 읽을 수 있는 Skill 인벤토리를 stdout에 출력합니다.
- `skills list --verbose`: 누락된 요구 사항을 표에 포함합니다.
- `skills info <name>`: 한 Skill의 세부 정보를 표시합니다.
- `skills info <name> --json`: 기계가 읽을 수 있는 세부 정보를 stdout에 출력합니다.
- `skills check`: 준비 완료 대 누락된 요구 사항 요약.
- `skills check --json`: 기계가 읽을 수 있는 준비 상태 출력을 stdout에 출력합니다.

옵션:

- `--eligible`: 준비된 Skills만 표시합니다.
- `--json`: JSON 출력(스타일링 없음).
- `-v`, `--verbose`: 누락된 요구 사항 세부 정보를 포함합니다.

팁: ClawHub 기반 Skills에는 `openclaw skills search`, `openclaw skills install`, `openclaw skills update`를 사용하세요.

### `pairing`

채널 전반의 DM 페어링 요청을 승인합니다.

하위 명령:

- `pairing list [channel] [--channel <channel>] [--account <id>] [--json]`
- `pairing approve <channel> <code> [--account <id>] [--notify]`
- `pairing approve --channel <channel> [--account <id>] <code> [--notify]`

참고:

- 페어링 가능한 채널이 정확히 하나만 구성된 경우 `pairing approve <code>`도 허용됩니다.
- `list`와 `approve`는 모두 멀티 계정 채널용으로 `--account <id>`를 지원합니다.

### `devices`

gateway 디바이스 페어링 항목과 역할별 디바이스 토큰을 관리합니다.

하위 명령:

- `devices list [--json]`
- `devices approve [requestId] [--latest]`
- `devices reject <requestId>`
- `devices remove <deviceId>`
- `devices clear --yes [--pending]`
- `devices rotate --device <id> --role <role> [--scope <scope...>]`
- `devices revoke --device <id> --role <role>`

참고:

- `devices list`와 `devices approve`는 직접 페어링 범위를 사용할 수 없을 때 local loopback의 로컬 페어링 파일로 대체할 수 있습니다.
- `devices approve`는 `requestId`를 전달하지 않거나 `--latest`가 설정되면 가장 최근 대기 요청을 자동 선택합니다.
- 저장된 토큰 재연결은 토큰의 캐시된 승인 범위를 재사용하며, 명시적
  `devices rotate --scope ...`는 향후 캐시된 토큰 재연결을 위해 해당 저장된 범위 집합을 업데이트합니다.
- `devices rotate`와 `devices revoke`는 JSON 페이로드를 반환합니다.

### `qr`

현재 Gateway config에서 모바일 페어링 QR 및 설정 코드를 생성합니다. [`openclaw qr`](/cli/qr)를 참조하세요.

옵션:

- `--remote`
- `--url <url>`
- `--public-url <url>`
- `--token <token>`
- `--password <password>`
- `--setup-code-only`
- `--no-ascii`
- `--json`

참고:

- `--token`과 `--password`는 함께 사용할 수 없습니다.
- 설정 코드는 공유 gateway 토큰/비밀번호가 아니라 수명이 짧은 bootstrap 토큰을 담습니다.
- 내장 bootstrap handoff는 기본 node 토큰을 `scopes: []` 상태로 유지합니다.
- 전달된 운영자 bootstrap 토큰은 `operator.approvals`, `operator.read`, `operator.talk.secrets`, `operator.write`로 범위가 제한된 상태를 유지합니다.
- Bootstrap 범위 검사는 역할 접두사 기반이므로, 해당 운영자 허용 목록은 운영자 요청만 충족합니다. 비운영자 역할은 여전히 자신의 역할 접두사 아래 범위가 필요합니다.
- `--remote`는 `gateway.remote.url` 또는 활성 Tailscale Serve/Funnel URL을 사용할 수 있습니다.
- 스캔 후 `openclaw devices list` / `openclaw devices approve <requestId>`로 요청을 승인하세요.

### `clawbot`

레거시 별칭 네임스페이스입니다. 현재 `openclaw clawbot qr`를 지원하며, 이는 [`openclaw qr`](/cli/qr)에 매핑됩니다.

### `hooks`

내부 agent hooks를 관리합니다.

하위 명령:

- `hooks list`
- `hooks info <name>`
- `hooks check`
- `hooks enable <name>`
- `hooks disable <name>`
- `hooks install <path-or-spec>` (`openclaw plugins install`의 지원 중단 별칭)
- `hooks update [id]` (`openclaw plugins update`의 지원 중단 별칭)

공통 옵션:

- `--json`
- `--eligible`
- `-v`, `--verbose`

참고:

- plugin이 관리하는 hooks는 `openclaw hooks`로 활성화하거나 비활성화할 수 없습니다. 대신 소유 plugin을 활성화 또는 비활성화하세요.
- `hooks install`과 `hooks update`는 여전히 호환성 별칭으로 동작하지만, 지원 중단 경고를 출력하고 plugin 명령으로 전달됩니다.

### `webhooks`

웹훅 헬퍼입니다. 현재 내장 표면은 Gmail Pub/Sub 설정 + 실행기입니다:

- `webhooks gmail setup`
- `webhooks gmail run`

### `webhooks gmail`

Gmail Pub/Sub 훅 설정 + 실행기입니다. [Gmail Pub/Sub](/automation/cron-jobs#gmail-pubsub-integration)를 참조하세요.

하위 명령:

- `webhooks gmail setup` (`--account <email>` 필요, `--project`, `--topic`, `--subscription`, `--label`, `--hook-url`, `--hook-token`, `--push-token`, `--bind`, `--port`, `--path`, `--include-body`, `--max-bytes`, `--renew-minutes`, `--tailscale`, `--tailscale-path`, `--tailscale-target`, `--push-endpoint`, `--json` 지원)
- `webhooks gmail run` (동일한 플래그에 대한 런타임 재정의)

참고:

- `setup`은 Gmail watch와 OpenClaw 대상 푸시 경로를 구성합니다.
- `run`은 선택적 런타임 재정의와 함께 로컬 Gmail watcher/갱신 루프를 시작합니다.

### `dns`

광역 디스커버리 DNS 헬퍼(CoreDNS + Tailscale)입니다. 현재 내장 표면:

- `dns setup [--domain <domain>] [--apply]`

### `dns setup`

광역 디스커버리 DNS 헬퍼(CoreDNS + Tailscale)입니다. [/gateway/discovery](/gateway/discovery)를 참조하세요.

옵션:

- `--domain <domain>`
- `--apply`: CoreDNS config 설치/업데이트(sudo 필요, macOS 전용).

참고:

- `--apply`가 없으면 추천 OpenClaw + Tailscale DNS config를 출력하는 계획 헬퍼로 동작합니다.
- `--apply`는 현재 Homebrew CoreDNS를 사용하는 macOS만 지원합니다.

## 메시징 + agent

### `message`

통합 아웃바운드 메시징 + 채널 작업.

참조: [/cli/message](/cli/message)

하위 명령:

- `message send|poll|react|reactions|read|edit|delete|pin|unpin|pins|permissions|search|timeout|kick|ban`
- `message thread <create|list|reply>`
- `message emoji <list|upload>`
- `message sticker <send|upload>`
- `message role <info|add|remove>`
- `message channel <info|list>`
- `message member info`
- `message voice status`
- `message event <list|create>`

예시:

- `openclaw message send --target +15555550123 --message "Hi"`
- `openclaw message poll --channel discord --target channel:123 --poll-question "Snack?" --poll-option Pizza --poll-option Sushi`

### `agent`

Gateway(또는 `--local` 임베디드)를 통해 agent 턴 하나를 실행합니다.

세션 선택자 `--to`, `--session-id`, `--agent` 중 하나 이상을 전달하세요.

필수:

- `-m, --message <text>`

옵션:

- `-t, --to <dest>` (세션 키 및 선택적 전달용)
- `--session-id <id>`
- `--agent <id>` (agent id; 라우팅 바인딩보다 우선)
- `--thinking <off|minimal|low|medium|high|xhigh>` (provider 지원은 다를 수 있으며 CLI 수준에서 모델 게이트는 적용되지 않음)
- `--verbose <on|off>`
- `--channel <channel>` (전달 채널; 생략하면 메인 세션 채널 사용)
- `--reply-to <target>` (세션 라우팅과 별개인 전달 대상 재정의)
- `--reply-channel <channel>` (전달 채널 재정의)
- `--reply-account <id>` (전달 계정 id 재정의)
- `--local` (임베디드 실행; 그래도 plugin 레지스트리를 먼저 프리로드함)
- `--deliver`
- `--json`
- `--timeout <seconds>`

참고:

- Gateway 모드는 Gateway 요청이 실패하면 임베디드 agent로 대체됩니다.
- `--local`도 여전히 plugin 레지스트리를 프리로드하므로, plugin이 제공하는 provider, 도구, 채널을 임베디드 실행 중에도 계속 사용할 수 있습니다.
- `--channel`, `--reply-channel`, `--reply-account`는 라우팅이 아니라 응답 전달에 영향을 줍니다.

### `agents`

격리된 agent(워크스페이스 + auth + 라우팅)를 관리합니다.

하위 명령 없이 `openclaw agents`를 실행하면 `openclaw agents list`와 같습니다.

#### `agents list`

구성된 agent를 나열합니다.

옵션:

- `--json`
- `--bindings`

#### `agents add [name]`

새 격리 agent를 추가합니다. 플래그(또는 `--non-interactive`)가 전달되지 않으면 안내형 마법사를 실행하며, 비대화형 모드에서는 `--workspace`가 필요합니다.

옵션:

- `--workspace <dir>`
- `--model <id>`
- `--agent-dir <dir>`
- `--bind <channel[:accountId]>` (반복 가능)
- `--non-interactive`
- `--json`

바인딩 사양은 `channel[:accountId]`를 사용합니다. `accountId`를 생략하면 OpenClaw가 채널 기본값/plugin hooks를 통해 계정 범위를 해석할 수 있으며, 그렇지 않으면 명시적 계정 범위가 없는 채널 바인딩이 됩니다.
명시적 add 플래그를 하나라도 전달하면 명령은 비대화형 경로로 전환됩니다. `main`은 예약어이므로 새 agent id로 사용할 수 없습니다.

#### `agents bindings`

라우팅 바인딩을 나열합니다.

옵션:

- `--agent <id>`
- `--json`

#### `agents bind`

agent에 대한 라우팅 바인딩을 추가합니다.

옵션:

- `--agent <id>` (기본값은 현재 기본 agent)
- `--bind <channel[:accountId]>` (반복 가능)
- `--json`

#### `agents unbind`

agent에서 라우팅 바인딩을 제거합니다.

옵션:

- `--agent <id>` (기본값은 현재 기본 agent)
- `--bind <channel[:accountId]>` (반복 가능)
- `--all`
- `--json`

`--all` 또는 `--bind` 중 하나만 사용하세요. 둘 다는 사용할 수 없습니다.

#### `agents delete <id>`

agent를 삭제하고 해당 워크스페이스 + 상태를 정리합니다.

옵션:

- `--force`
- `--json`

참고:

- `main`은 삭제할 수 없습니다.
- `--force`가 없으면 대화형 확인이 필요합니다.

#### `agents set-identity`

agent 신원(name/theme/emoji/avatar)을 업데이트합니다.

옵션:

- `--agent <id>`
- `--workspace <dir>`
- `--identity-file <path>`
- `--from-identity`
- `--name <name>`
- `--theme <theme>`
- `--emoji <emoji>`
- `--avatar <value>`
- `--json`

참고:

- 대상 agent 선택에는 `--agent` 또는 `--workspace`를 사용할 수 있습니다.
- 명시적 신원 필드를 제공하지 않으면 명령은 `IDENTITY.md`를 읽습니다.

### `acp`

IDE를 Gateway에 연결하는 ACP 브리지를 실행합니다.

루트 옵션:

- `--url <url>`
- `--token <token>`
- `--token-file <path>`
- `--password <password>`
- `--password-file <path>`
- `--session <key>`
- `--session-label <label>`
- `--require-existing`
- `--reset-session`
- `--no-prefix-cwd`
- `--provenance <off|meta|meta+receipt>`
- `--verbose`

#### `acp client`

브리지 디버깅용 대화형 ACP 클라이언트입니다.

옵션:

- `--cwd <dir>`
- `--server <command>`
- `--server-args <args...>`
- `--server-verbose`
- `--verbose`

전체 동작, 보안 참고, 예시는 [`acp`](/cli/acp)를 참조하세요.

### `mcp`

저장된 MCP 서버 정의를 관리하고 OpenClaw 채널을 MCP stdio로 노출합니다.

#### `mcp serve`

라우팅된 OpenClaw 채널 대화를 MCP stdio로 노출합니다.

옵션:

- `--url <url>`
- `--token <token>`
- `--token-file <path>`
- `--password <password>`
- `--password-file <path>`
- `--claude-channel-mode <auto|on|off>`
- `--verbose`

#### `mcp list`

저장된 MCP 서버 정의를 나열합니다.

옵션:

- `--json`

#### `mcp show [name]`

저장된 MCP 서버 정의 하나 또는 저장된 전체 MCP 서버 객체를 표시합니다.

옵션:

- `--json`

#### `mcp set <name> <value>`

JSON 객체에서 MCP 서버 정의 하나를 저장합니다.

#### `mcp unset <name>`

저장된 MCP 서버 정의 하나를 제거합니다.

### `approvals`

exec 승인을 관리합니다. 별칭: `exec-approvals`.

#### `approvals get`

exec 승인 스냅샷과 유효 정책을 가져옵니다.

옵션:

- `--node <node>`
- `--gateway`
- `--json`
- `openclaw nodes`의 node RPC 옵션

#### `approvals set`

파일 또는 stdin의 JSON으로 exec 승인을 교체합니다.

옵션:

- `--node <node>`
- `--gateway`
- `--file <path>`
- `--stdin`
- `--json`
- `openclaw nodes`의 node RPC 옵션

#### `approvals allowlist add|remove`

agent별 exec 허용 목록을 편집합니다.

옵션:

- `--node <node>`
- `--gateway`
- `--agent <id>` (기본값 `*`)
- `--json`
- `openclaw nodes`의 node RPC 옵션

### `status`

연결된 세션 상태와 최근 수신자를 표시합니다.

옵션:

- `--json`
- `--all` (전체 진단; 읽기 전용, 붙여넣기 가능)
- `--deep` (지원되는 경우 채널 프로브를 포함해 gateway에 라이브 상태 프로브를 요청)
- `--usage` (모델 provider 사용량/할당량 표시)
- `--timeout <ms>`
- `--verbose`
- `--debug` (`--verbose`의 별칭)

참고:

- 개요에는 사용 가능한 경우 Gateway + node host 서비스 상태가 포함됩니다.
- `--usage`는 정규화된 provider 사용량 윈도우를 `X% left`로 출력합니다.

### 사용량 추적

OpenClaw는 OAuth/API 자격 증명을 사용할 수 있을 때 provider 사용량/할당량을 표시할 수 있습니다.

표면:

- `/status` (사용 가능한 경우 짧은 provider 사용량 줄 추가)
- `openclaw status --usage` (전체 provider 분해 출력)
- macOS 메뉴 바(Context 아래 Usage 섹션)

참고:

- 데이터는 provider 사용량 엔드포인트에서 직접 가져옵니다(추정치 아님).
- 사람이 읽을 수 있는 출력은 provider 전반에 걸쳐 `X% left`로 정규화됩니다.
- 현재 사용량 윈도우를 제공하는 provider: Anthropic, GitHub Copilot, Gemini CLI, OpenAI Codex, MiniMax, Xiaomi, z.ai.
- MiniMax 참고: 원시 `usage_percent` / `usagePercent`는 남은 할당량을 의미하므로, OpenClaw는 표시 전에 이를 반전합니다. 수량 기반 필드는 있을 경우 여전히 우선합니다. `model_remains` 응답은 채팅 모델 항목을 우선하고, 필요할 때 타임스탬프에서 윈도우 라벨을 파생하며, 플랜 라벨에 모델 이름을 포함합니다.
- 사용량 auth는 가능한 경우 provider별 hooks에서 가져오며, 그렇지 않으면 OpenClaw는 auth profile, env, config의 일치하는 OAuth/API 키 자격 증명으로 대체합니다. 아무것도 확인되지 않으면 사용량은 숨겨집니다.
- 자세한 내용: [Usage tracking](/concepts/usage-tracking)을 참조하세요.

### `health`

실행 중인 Gateway에서 상태 정보를 가져옵니다.

옵션:

- `--json`
- `--timeout <ms>`
- `--verbose` (라이브 프로브를 강제하고 gateway 연결 세부 정보를 출력)
- `--debug` (`--verbose`의 별칭)

참고:

- 기본 `health`는 최신 캐시된 gateway 스냅샷을 반환할 수 있습니다.
- `health --verbose`는 라이브 프로브를 강제하고 사람이 읽을 수 있는 출력을 구성된 모든 계정과 agent에 걸쳐 확장합니다.

### `sessions`

저장된 대화 세션을 나열합니다.

옵션:

- `--json`
- `--verbose`
- `--store <path>`
- `--active <minutes>`
- `--agent <id>` (agent별 세션 필터링)
- `--all-agents` (모든 agent에 걸친 세션 표시)

하위 명령:

- `sessions cleanup` — 만료되었거나 고아 상태인 세션 제거

참고:

- `sessions cleanup`은 전사 파일이 사라진 항목을 정리하기 위한 `--fix-missing`도 지원합니다.

## 초기화 / 제거

### `reset`

로컬 config/상태를 초기화합니다(CLI는 설치된 상태로 유지).

옵션:

- `--scope <config|config+creds+sessions|full>`
- `--yes`
- `--non-interactive`
- `--dry-run`

참고:

- `--non-interactive`에는 `--scope`와 `--yes`가 필요합니다.

### `uninstall`

gateway 서비스 + 로컬 데이터를 제거합니다(CLI는 유지됨).

옵션:

- `--service`
- `--state`
- `--workspace`
- `--app`
- `--all`
- `--yes`
- `--non-interactive`
- `--dry-run`

참고:

- `--non-interactive`에는 `--yes`와 명시적 범위(또는 `--all`)가 필요합니다.
- `--all`은 서비스, 상태, 워크스페이스, 앱을 함께 제거합니다.

### `tasks`

agent 전반의 [background task](/automation/tasks) 실행을 나열하고 관리합니다.

- `tasks list` — 활성 및 최근 task 실행 표시
- `tasks show <id>` — 특정 task 실행의 세부 정보 표시
- `tasks notify <id>` — task 실행의 알림 정책 변경
- `tasks cancel <id>` — 실행 중인 task 취소
- `tasks audit` — 운영 문제(오래됨, 손실, 전달 실패) 노출
- `tasks maintenance [--apply] [--json]` — task 및 TaskFlow 정리/조정(ACP/subagent 하위 세션, 활성 cron 작업, 라이브 CLI 실행)을 미리 보거나 적용
- `tasks flow list` — 활성 및 최근 Task Flow 흐름 나열
- `tasks flow show <lookup>` — id 또는 조회 키로 흐름 검사
- `tasks flow cancel <lookup>` — 실행 중인 흐름과 그 활성 task 취소

### `flows`

레거시 문서 바로가기입니다. flow 명령은 `openclaw tasks flow` 아래에 있습니다.

- `tasks flow list [--json]`
- `tasks flow show <lookup>`
- `tasks flow cancel <lookup>`

## Gateway

### `gateway`

WebSocket Gateway를 실행합니다.

옵션:

- `--port <port>`
- `--bind <loopback|tailnet|lan|auto|custom>`
- `--token <token>`
- `--auth <token|password>`
- `--password <password>`
- `--password-file <path>`
- `--tailscale <off|serve|funnel>`
- `--tailscale-reset-on-exit`
- `--allow-unconfigured`
- `--dev`
- `--reset` (개발 config + 자격 증명 + 세션 + 워크스페이스 초기화)
- `--force` (포트에서 기존 리스너 종료)
- `--verbose`
- `--cli-backend-logs`
- `--claude-cli-logs` (지원 중단 별칭)
- `--ws-log <auto|full|compact>`
- `--compact` (별칭: `--ws-log compact`)
- `--raw-stream`
- `--raw-stream-path <path>`

### `gateway service`

Gateway 서비스(launchd/systemd/schtasks)를 관리합니다.

하위 명령:

- `gateway status` (기본적으로 Gateway RPC 프로브)
- `gateway install` (서비스 설치)
- `gateway uninstall`
- `gateway start`
- `gateway stop`
- `gateway restart`

참고:

- `gateway status`는 기본적으로 서비스의 확인된 port/config를 사용해 Gateway RPC를 프로브합니다(`--url/--token/--password`로 재정의).
- `gateway status`는 스크립팅용으로 `--no-probe`, `--deep`, `--require-rpc`, `--json`을 지원합니다.
- `gateway status`는 감지 가능한 경우 레거시 또는 추가 gateway 서비스도 표시합니다(`--deep`는 시스템 수준 스캔 추가). profile 이름이 붙은 OpenClaw 서비스는 일급으로 취급되며 "추가"로 표시되지 않습니다.
- `gateway status`는 로컬 CLI config가 없거나 유효하지 않아도 진단용으로 계속 사용할 수 있습니다.
- `gateway status`는 확인된 파일 로그 경로, CLI 대 서비스 config 경로/유효성 스냅샷, 확인된 프로브 대상 URL을 출력합니다.
- 현재 명령 경로에서 gateway auth SecretRef를 확인할 수 없으면, `gateway status --json`은 프로브 연결/인증이 실패할 때만 `rpc.authWarning`을 보고합니다(프로브가 성공하면 경고는 억제됨).
- Linux systemd 설치에서는 상태 토큰 드리프트 검사가 `Environment=`와 `EnvironmentFile=` 유닛 소스를 모두 포함합니다.
- `gateway install|uninstall|start|stop|restart`는 스크립팅용 `--json`을 지원합니다(기본 출력은 사람이 읽기 쉬운 형식 유지).
- `gateway install`의 기본 런타임은 Node이며, bun은 **권장되지 않습니다**(WhatsApp/Telegram 버그).
- `gateway install` 옵션: `--port`, `--runtime`, `--token`, `--force`, `--json`.

### `daemon`

Gateway 서비스 관리 명령의 레거시 별칭입니다. [/cli/daemon](/cli/daemon)을 참조하세요.

하위 명령:

- `daemon status`
- `daemon install`
- `daemon uninstall`
- `daemon start`
- `daemon stop`
- `daemon restart`

공통 옵션:

- `status`: `--url`, `--token`, `--password`, `--timeout`, `--no-probe`, `--require-rpc`, `--deep`, `--json`
- `install`: `--port`, `--runtime <node|bun>`, `--token`, `--force`, `--json`
- `uninstall|start|stop|restart`: `--json`

### `logs`

RPC를 통해 Gateway 파일 로그를 tail합니다.

옵션:

- `--limit <n>`: 반환할 최대 로그 줄 수
- `--max-bytes <n>`: 로그 파일에서 읽을 최대 바이트 수
- `--follow`: 로그 파일 따라가기(`tail -f` 스타일)
- `--interval <ms>`: follow 시 ms 단위 폴링 간격
- `--local-time`: 타임스탬프를 로컬 시간으로 표시
- `--json`: 줄 단위 JSON 출력
- `--plain`: 구조화된 서식 비활성화
- `--no-color`: ANSI 색상 비활성화
- `--url <url>`: 명시적 Gateway WebSocket URL
- `--token <token>`: Gateway 토큰
- `--timeout <ms>`: Gateway RPC 타임아웃
- `--expect-final`: 필요 시 최종 응답을 기다림

예시:

```bash
openclaw logs --follow
openclaw logs --limit 200
openclaw logs --plain
openclaw logs --json
openclaw logs --no-color
```

참고:

- `--url`을 전달하면 CLI는 config 또는 환경 자격 증명을 자동 적용하지 않습니다.
- local loopback 페어링 실패는 구성된 로컬 로그 파일로 대체되며, 명시적 `--url` 대상에는 적용되지 않습니다.

### `gateway <subcommand>`

Gateway CLI 헬퍼입니다(RPC 하위 명령에는 `--url`, `--token`, `--password`, `--timeout`, `--expect-final` 사용).
`--url`을 전달하면 CLI는 config 또는 환경 자격 증명을 자동 적용하지 않습니다.
`--token` 또는 `--password`를 명시적으로 포함하세요. 명시적 자격 증명이 없으면 오류입니다.

하위 명령:

- `gateway call <method> [--params <json>] [--url <url>] [--token <token>] [--password <password>] [--timeout <ms>] [--expect-final] [--json]`
- `gateway health`
- `gateway status`
- `gateway probe`
- `gateway discover`
- `gateway install|uninstall|start|stop|restart`
- `gateway run`

참고:

- `gateway status --deep`는 시스템 수준 서비스 스캔을 추가합니다. 더 깊은 런타임 프로브 세부 정보에는 `gateway probe`,
  `health --verbose`, 또는 최상위 `status --deep`를 사용하세요.

일반 RPC:

- `config.schema.lookup` (얕은 스키마 노드, 일치한 힌트 메타데이터, 즉시 하위 요약으로 config 하위 트리 하나를 검사)
- `config.get` (현재 config 스냅샷 + 해시 읽기)
- `config.set` (전체 config 검증 + 쓰기; 낙관적 동시성에는 `baseHash` 사용)
- `config.apply` (config 검증 + 쓰기 + 재시작 + 깨우기)
- `config.patch` (부분 업데이트 병합 + 재시작 + 깨우기)
- `update.run` (업데이트 실행 + 재시작 + 깨우기)

팁: `config.set`/`config.apply`/`config.patch`를 직접 호출할 때 config가 이미 있으면
`config.get`의 `baseHash`를 전달하세요.
팁: 부분 편집의 경우 먼저 `config.schema.lookup`로 검사하고 `config.patch`를 우선 사용하세요.
팁: 이 config 쓰기 RPC는 제출된 config 페이로드의 ref에 대해 활성 SecretRef 해상을 사전 점검하며, 실질적으로 활성인 제출 ref를 확인할 수 없으면 쓰기를 거부합니다.
팁: 소유자 전용 `gateway` 런타임 도구는 여전히 `tools.exec.ask` 또는 `tools.exec.security` 재작성을 거부합니다. 레거시 `tools.bash.*` 별칭은 동일한 보호된 exec 경로로 정규화됩니다.

## Models

fallback 동작과 스캔 전략은 [/concepts/models](/concepts/models)를 참조하세요.

청구 참고: Anthropic의 공개 CLI 문서를 기준으로 볼 때, Claude Code CLI fallback은
로컬의 사용자 관리 자동화에는 허용될 가능성이 높다고 판단합니다. 다만,
외부 제품에서 구독 기반 사용과 관련한 Anthropic의 서드파티 harness 정책에는
충분한 모호성이 있으므로, 프로덕션 환경에는 권장하지 않습니다.
Anthropic은 또한 **2026년 4월 4일 오후 12:00 PT / 오후 8:00 BST**에 OpenClaw 사용자에게
**OpenClaw** Claude 로그인 경로가
서드파티 harness 사용으로 간주되며 구독과 별도로 청구되는 **Extra Usage**가 필요하다고 통지했습니다.
프로덕션에서는 Anthropic API 키 또는 OpenAI Codex, Alibaba Cloud Model Studio
Coding Plan, MiniMax Coding Plan, Z.AI / GLM Coding Plan 같은
다른 지원되는 구독형 provider를 우선 사용하세요.

Anthropic Claude CLI 마이그레이션:

```bash
openclaw models auth login --provider anthropic --method cli --set-default
```

온보딩 바로가기: `openclaw onboard --auth-choice anthropic-cli`

Anthropic setup-token도 레거시/수동 auth 경로로 다시 제공됩니다.
Anthropic이 OpenClaw 사용자에게
OpenClaw Claude 로그인 경로에 **Extra Usage**가 필요하다고 알렸다는 점을 전제로만 사용하세요.

레거시 별칭 참고: `claude-cli`는 지원 중단된 온보딩 auth-choice 별칭입니다.
온보딩에는 `anthropic-cli`를 사용하거나 `models auth login`을 직접 사용하세요.

### `models` (루트)

`openclaw models`는 `models status`의 별칭입니다.

루트 옵션:

- `--status-json` (`models status --json`의 별칭)
- `--status-plain` (`models status --plain`의 별칭)

### `models list`

옵션:

- `--all`
- `--local`
- `--provider <name>`
- `--json`
- `--plain`

### `models status`

옵션:

- `--json`
- `--plain`
- `--check` (종료 코드 1=만료/누락, 2=곧 만료)
- `--probe` (구성된 auth profile의 라이브 프로브)
- `--probe-provider <name>`
- `--probe-profile <id>` (반복 또는 쉼표 구분)
- `--probe-timeout <ms>`
- `--probe-concurrency <n>`
- `--probe-max-tokens <n>`
- `--agent <id>`

항상 auth 저장소의 profile에 대한 auth 개요와 OAuth 만료 상태를 포함합니다.
`--probe`는 라이브 요청을 실행합니다(토큰을 소비하고 rate limit를 유발할 수 있음).
프로브 행은 auth profile, env 자격 증명, 또는 `models.json`에서 올 수 있습니다.
`ok`, `auth`, `rate_limit`, `billing`, `timeout`,
`format`, `unknown`, `no_model` 같은 프로브 상태를 예상하세요.
명시적 `auth.order.<provider>`에 저장된 profile이 포함되지 않으면, 프로브는
해당 profile을 조용히 시도하는 대신 `excluded_by_auth_order`를 보고합니다.

### `models set <model>`

`agents.defaults.model.primary`를 설정합니다.

### `models set-image <model>`

`agents.defaults.imageModel.primary`를 설정합니다.

### `models aliases list|add|remove`

옵션:

- `list`: `--json`, `--plain`
- `add <alias> <model>`
- `remove <alias>`

### `models fallbacks list|add|remove|clear`

옵션:

- `list`: `--json`, `--plain`
- `add <model>`
- `remove <model>`
- `clear`

### `models image-fallbacks list|add|remove|clear`

옵션:

- `list`: `--json`, `--plain`
- `add <model>`
- `remove <model>`
- `clear`

### `models scan`

옵션:

- `--min-params <b>`
- `--max-age-days <days>`
- `--provider <name>`
- `--max-candidates <n>`
- `--timeout <ms>`
- `--concurrency <n>`
- `--no-probe`
- `--yes`
- `--no-input`
- `--set-default`
- `--set-image`
- `--json`

### `models auth add|login|login-github-copilot|setup-token|paste-token`

옵션:

- `add`: 대화형 auth 헬퍼(provider auth 흐름 또는 토큰 붙여넣기)
- `login`: `--provider <name>`, `--method <method>`, `--set-default`
- `login-github-copilot`: GitHub Copilot OAuth 로그인 흐름(`--yes`)
- `setup-token`: `--provider <name>`, `--yes`
- `paste-token`: `--provider <name>`, `--profile-id <id>`, `--expires-in <duration>`

참고:

- `setup-token`과 `paste-token`은 토큰 auth 방법을 제공하는 provider용 일반 토큰 명령입니다.
- `setup-token`은 대화형 TTY가 필요하며 provider의 토큰 auth 방법을 실행합니다.
- `paste-token`은 토큰 값을 프롬프트하며 `--profile-id`를 생략하면 auth profile id 기본값으로 `<provider>:manual`을 사용합니다.
- Anthropic `setup-token` / `paste-token`은 레거시/수동 OpenClaw 경로로 다시 제공됩니다. Anthropic은 OpenClaw 사용자에게 이 경로에 Claude 계정의 **Extra Usage**가 필요하다고 알렸습니다.

### `models auth order get|set|clear`

옵션:

- `get`: `--provider <name>`, `--agent <id>`, `--json`
- `set`: `--provider <name>`, `--agent <id>`, `<profileIds...>`
- `clear`: `--provider <name>`, `--agent <id>`

## System

### `system event`

시스템 이벤트를 큐에 넣고 선택적으로 heartbeat를 트리거합니다(Gateway RPC).

필수:

- `--text <text>`

옵션:

- `--mode <now|next-heartbeat>`
- `--json`
- `--url`, `--token`, `--timeout`, `--expect-final`

### `system heartbeat last|enable|disable`

Heartbeat 제어(Gateway RPC)입니다.

옵션:

- `--json`
- `--url`, `--token`, `--timeout`, `--expect-final`

### `system presence`

시스템 presence 항목을 나열합니다(Gateway RPC).

옵션:

- `--json`
- `--url`, `--token`, `--timeout`, `--expect-final`

## Cron

예약 작업을 관리합니다(Gateway RPC). [/automation/cron-jobs](/automation/cron-jobs)를 참조하세요.

하위 명령:

- `cron status [--json]`
- `cron list [--all] [--json]` (기본값은 표 출력이며, 원시 출력에는 `--json` 사용)
- `cron add` (별칭: `create`; `--name`과 정확히 하나의 `--at` | `--every` | `--cron`, 그리고 정확히 하나의 페이로드 `--system-event` | `--message` 필요)
- `cron edit <id>` (필드 패치)
- `cron rm <id>` (별칭: `remove`, `delete`)
- `cron enable <id>`
- `cron disable <id>`
- `cron runs --id <id> [--limit <n>]`
- `cron run <id> [--due]`

모든 `cron` 명령은 `--url`, `--token`, `--timeout`, `--expect-final`을 허용합니다.

`cron add|edit --model ...`은 해당 작업에 선택된 허용 모델을 사용합니다.
모델이 허용되지 않으면 cron은 경고를 표시하고 작업의 agent/default
모델 선택으로 대체합니다. 구성된 fallback 체인은 계속 적용되지만, 명시적 작업별 fallback 목록이 없는 단순
모델 재정의는 더 이상
숨겨진 추가 재시도 대상으로 agent primary를 덧붙이지 않습니다.

## Node host

### `node`

`node`는 **헤드리스 node host**를 실행하거나 백그라운드 서비스로 관리합니다. [`openclaw node`](/cli/node)를 참조하세요.

하위 명령:

- `node run --host <gateway-host> --port 18789`
- `node status`
- `node install [--host <gateway-host>] [--port <port>] [--tls] [--tls-fingerprint <sha256>] [--node-id <id>] [--display-name <name>] [--runtime <node|bun>] [--force]`
- `node uninstall`
- `node stop`
- `node restart`

auth 참고:

- `node`는 env/config에서 gateway auth를 확인합니다(`--token`/`--password` 플래그 없음): `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`, 그 다음 `gateway.auth.*`. 로컬 모드에서 node host는 의도적으로 `gateway.remote.*`를 무시하며, `gateway.mode=remote`에서는 원격 우선순위 규칙에 따라 `gateway.remote.*`가 참여합니다.
- Node-host auth 해상은 `OPENCLAW_GATEWAY_*` env 변수만 존중합니다.

## Nodes

`nodes`는 Gateway와 통신하며 페어링된 node를 대상으로 합니다. [/nodes](/nodes)를 참조하세요.

공통 옵션:

- `--url`, `--token`, `--timeout`, `--json`

하위 명령:

- `nodes status [--connected] [--last-connected <duration>]`
- `nodes describe --node <id|name|ip>`
- `nodes list [--connected] [--last-connected <duration>]`
- `nodes pending`
- `nodes approve <requestId>`
- `nodes reject <requestId>`
- `nodes rename --node <id|name|ip> --name <displayName>`
- `nodes invoke --node <id|name|ip> --command <command> [--params <json>] [--invoke-timeout <ms>] [--idempotency-key <key>]`
- `nodes notify --node <id|name|ip> [--title <text>] [--body <text>] [--sound <name>] [--priority <passive|active|timeSensitive>] [--delivery <system|overlay|auto>] [--invoke-timeout <ms>]` (mac 전용)

카메라:

- `nodes camera list --node <id|name|ip>`
- `nodes camera snap --node <id|name|ip> [--facing front|back|both] [--device-id <id>] [--max-width <px>] [--quality <0-1>] [--delay-ms <ms>] [--invoke-timeout <ms>]`
- `nodes camera clip --node <id|name|ip> [--facing front|back] [--device-id <id>] [--duration <ms|10s|1m>] [--no-audio] [--invoke-timeout <ms>]`

Canvas + 화면:

- `nodes canvas snapshot --node <id|name|ip> [--format png|jpg|jpeg] [--max-width <px>] [--quality <0-1>] [--invoke-timeout <ms>]`
- `nodes canvas present --node <id|name|ip> [--target <urlOrPath>] [--x <px>] [--y <px>] [--width <px>] [--height <px>] [--invoke-timeout <ms>]`
- `nodes canvas hide --node <id|name|ip> [--invoke-timeout <ms>]`
- `nodes canvas navigate <url> --node <id|name|ip> [--invoke-timeout <ms>]`
- `nodes canvas eval [<js>] --node <id|name|ip> [--js <code>] [--invoke-timeout <ms>]`
- `nodes canvas a2ui push --node <id|name|ip> (--jsonl <path> | --text <text>) [--invoke-timeout <ms>]`
- `nodes canvas a2ui reset --node <id|name|ip> [--invoke-timeout <ms>]`
- `nodes screen record --node <id|name|ip> [--screen <index>] [--duration <ms|10s>] [--fps <n>] [--no-audio] [--out <path>] [--invoke-timeout <ms>]`

위치:

- `nodes location get --node <id|name|ip> [--max-age <ms>] [--accuracy <coarse|balanced|precise>] [--location-timeout <ms>] [--invoke-timeout <ms>]`

## Browser

Browser 제어 CLI(전용 Chrome/Brave/Edge/Chromium)입니다. [`openclaw browser`](/cli/browser)와 [Browser tool](/tools/browser)을 참조하세요.

공통 옵션:

- `--url`, `--token`, `--timeout`, `--expect-final`, `--json`
- `--browser-profile <name>`

관리:

- `browser status`
- `browser start`
- `browser stop`
- `browser reset-profile`
- `browser tabs`
- `browser open <url>`
- `browser focus <targetId>`
- `browser close [targetId]`
- `browser profiles`
- `browser create-profile --name <name> [--color <hex>] [--cdp-url <url>] [--driver existing-session] [--user-data-dir <path>]`
- `browser delete-profile --name <name>`

검사:

- `browser screenshot [targetId] [--full-page] [--ref <ref>] [--element <selector>] [--type png|jpeg]`
- `browser snapshot [--format aria|ai] [--target-id <id>] [--limit <n>] [--interactive] [--compact] [--depth <n>] [--selector <sel>] [--out <path>]`

작업:

- `browser navigate <url> [--target-id <id>]`
- `browser resize <width> <height> [--target-id <id>]`
- `browser click <ref> [--double] [--button <left|right|middle>] [--modifiers <csv>] [--target-id <id>]`
- `browser type <ref> <text> [--submit] [--slowly] [--target-id <id>]`
- `browser press <key> [--target-id <id>]`
- `browser hover <ref> [--target-id <id>]`
- `browser drag <startRef> <endRef> [--target-id <id>]`
- `browser select <ref> <values...> [--target-id <id>]`
- `browser upload <paths...> [--ref <ref>] [--input-ref <ref>] [--element <selector>] [--target-id <id>] [--timeout-ms <ms>]`
- `browser fill [--fields <json>] [--fields-file <path>] [--target-id <id>]`
- `browser dialog --accept|--dismiss [--prompt <text>] [--target-id <id>] [--timeout-ms <ms>]`
- `browser wait [--time <ms>] [--text <value>] [--text-gone <value>] [--target-id <id>]`
- `browser evaluate --fn <code> [--ref <ref>] [--target-id <id>]`
- `browser console [--level <error|warn|info>] [--target-id <id>]`
- `browser pdf [--target-id <id>]`

## Voice call

### `voicecall`

plugin이 제공하는 voice-call 유틸리티입니다. voice-call plugin이 설치되고 활성화된 경우에만 나타납니다. [`openclaw voicecall`](/cli/voicecall)을 참조하세요.

공통 명령:

- `voicecall call --to <phone> --message <text> [--mode notify|conversation]`
- `voicecall start --to <phone> [--message <text>] [--mode notify|conversation]`
- `voicecall continue --call-id <id> --message <text>`
- `voicecall speak --call-id <id> --message <text>`
- `voicecall end --call-id <id>`
- `voicecall status --call-id <id>`
- `voicecall tail [--file <path>] [--since <n>] [--poll <ms>]`
- `voicecall latency [--file <path>] [--last <n>]`
- `voicecall expose [--mode off|serve|funnel] [--path <path>] [--port <port>] [--serve-path <path>]`

## 문서 검색

### `docs`

라이브 OpenClaw 문서 인덱스를 검색합니다.

### `docs [query...]`

라이브 문서 인덱스를 검색합니다.

## TUI

### `tui`

Gateway에 연결된 터미널 UI를 엽니다.

옵션:

- `--url <url>`
- `--token <token>`
- `--password <password>`
- `--session <key>`
- `--deliver`
- `--thinking <level>`
- `--message <text>`
- `--timeout-ms <ms>` (기본값 `agents.defaults.timeoutSeconds`)
- `--history-limit <n>`
