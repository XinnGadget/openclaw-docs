---
read_when:
    - 새 메시징 채널 plugin을 만들고 있을 때
    - OpenClaw를 메시징 플랫폼에 연결하고 싶을 때
    - ChannelPlugin 어댑터 표면을 이해해야 할 때
sidebarTitle: Channel Plugins
summary: OpenClaw용 메시징 채널 plugin을 만드는 단계별 가이드
title: 채널 plugin 만들기
x-i18n:
    generated_at: "2026-04-05T12:50:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 68a6ad2c75549db8ce54f7e22ca9850d7ed68c5cd651c9bb41c9f73769f48aba
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# 채널 plugin 만들기

이 가이드는 OpenClaw를 메시징 플랫폼에 연결하는 채널 plugin을 만드는 과정을 안내합니다. 끝까지 따라가면 DM 보안, 페어링, 답글 스레딩, 아웃바운드 메시징을 갖춘 동작하는 채널을 만들 수 있습니다.

<Info>
  아직 OpenClaw plugin을 한 번도 만들어 본 적이 없다면 먼저
  기본 패키지 구조와 manifest 설정을 위해
  [Getting Started](/plugins/building-plugins)를 읽으세요.
</Info>

## 채널 plugin 작동 방식

채널 plugin에는 자체 send/edit/react 도구가 필요하지 않습니다. OpenClaw는 코어에 하나의 공용 `message` 도구를 유지합니다. plugin이 소유하는 것은 다음입니다:

- **Config** — 계정 해석 및 설정 wizard
- **Security** — DM 정책 및 allowlist
- **Pairing** — DM 승인 흐름
- **Session grammar** — provider별 대화 ID를 기본 채팅, 스레드 ID, 부모 대체 항목에 매핑하는 방식
- **Outbound** — 플랫폼으로 텍스트, 미디어, 투표를 보내는 기능
- **Threading** — 답글이 스레드로 연결되는 방식

코어는 공용 message 도구, 프롬프트 연결, 바깥쪽 session-key 형식,
일반적인 `:thread:` bookkeeping, 그리고 dispatch를 소유합니다.

플랫폼이 대화 ID 내부에 추가 범위를 저장한다면, 해당 파싱은
plugin의 `messaging.resolveSessionConversation(...)`에 유지하세요. 이것이
`rawId`를 기본 대화 ID, 선택적 스레드 ID, 명시적 `baseConversationId`,
그리고 모든 `parentConversationCandidates`에 매핑하는 canonical hook입니다.
`parentConversationCandidates`를 반환할 때는 가장 좁은 부모에서
가장 넓은/기본 대화 순으로 정렬하세요.

채널 레지스트리가 부팅되기 전에 동일한 파싱이 필요한 번들 plugin은
일치하는 `resolveSessionConversation(...)` export를 가진 최상위
`session-key-api.ts` 파일을 노출할 수도 있습니다. 코어는 런타임 plugin 레지스트리를
아직 사용할 수 없을 때만 그 bootstrap-safe 표면을 사용합니다.

`messaging.resolveParentConversationCandidates(...)`는
plugin이 일반/raw ID 위에 부모 대체 항목만 필요로 할 때 레거시 호환성 대체 경로로 계속 사용할 수 있습니다.
두 hook이 모두 존재하면 코어는 먼저
`resolveSessionConversation(...).parentConversationCandidates`를 사용하고,
canonical hook이 이를 생략한 경우에만
`resolveParentConversationCandidates(...)`로 대체합니다.

## 승인 및 채널 capability

대부분의 채널 plugin은 승인 전용 코드가 필요하지 않습니다.

- 코어는 같은 채팅의 `/approve`, 공용 승인 버튼 payload, 일반적인 대체 전달을 소유합니다.
- 채널에 승인별 동작이 필요할 때는 채널 plugin에 하나의 `approvalCapability` 객체를 두는 방식을 선호하세요.
- `approvalCapability.authorizeActorAction`과 `approvalCapability.getActionAvailabilityState`는 canonical 승인 인증 seam입니다.
- 중복된 로컬 승인 프롬프트 숨기기 또는 전달 전 타이핑 표시기 보내기 같은 채널별 payload 수명 주기 동작에는 `outbound.shouldSuppressLocalPayloadPrompt` 또는 `outbound.beforeDeliverPayload`를 사용하세요.
- 네이티브 승인 라우팅 또는 대체 억제에는 `approvalCapability.delivery`만 사용하세요.
- 공용 renderer 대신 채널이 정말로 사용자 지정 승인 payload가 필요할 때만 `approvalCapability.render`를 사용하세요.
- 채널이 기존 config에서 안정적인 owner 유사 DM 신원을 추론할 수 있다면, 승인별 코어 로직을 추가하지 않고도 같은 채팅의 `/approve`를 제한하기 위해 `openclaw/plugin-sdk/approval-runtime`의 `createResolvedApproverActionAuthAdapter`를 사용하세요.
- 채널에 네이티브 승인 전달이 필요하다면 채널 코드는 대상 정규화와 transport hook에만 집중시키세요. 요청 필터링, 라우팅, dedupe, 만료, gateway subscription은 코어가 소유하도록 `openclaw/plugin-sdk/approval-runtime`의 `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver`, `createApproverRestrictedNativeApprovalCapability`, `createChannelNativeApprovalRuntime`을 사용하세요.
- 네이티브 승인 채널은 `accountId`와 `approvalKind`를 모두 해당 helper를 통해 라우팅해야 합니다. `accountId`는 멀티 계정 승인 정책이 올바른 봇 계정 범위에 유지되게 하고, `approvalKind`는 코어에 하드코딩 분기를 추가하지 않고도 exec 대 plugin 승인 동작을 채널에 제공하게 합니다.
- 전달된 승인 ID 종류를 처음부터 끝까지 보존하세요. 네이티브 클라이언트는 exec 대 plugin 승인 라우팅을 채널 로컬 상태에서 추측하거나 다시 쓰면 안 됩니다.
- 서로 다른 승인 종류는 의도적으로 서로 다른 네이티브 표면을 노출할 수 있습니다.
  현재 번들 예시:
  - Slack은 exec 및 plugin ID 모두에 대해 네이티브 승인 라우팅을 유지합니다.
  - Matrix는 exec 승인에만 네이티브 DM/채널 라우팅을 유지하고, plugin 승인은 공용 같은 채팅 `/approve` 경로에 남겨 둡니다.
- `createApproverRestrictedNativeApprovalAdapter`는 여전히 호환성 래퍼로 존재하지만, 새 코드는 capability builder를 선호하고 plugin에 `approvalCapability`를 노출해야 합니다.

핫 채널 entrypoint에서는 해당 계열의 일부만 필요하다면 더 좁은 런타임 subpath를 선호하세요:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`

마찬가지로 더 넓은 umbrella 표면이 필요하지 않다면
`openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference`, 그리고
`openclaw/plugin-sdk/reply-chunking`을 선호하세요.

설정과 관련해서는 특히 다음을 참고하세요:

- `openclaw/plugin-sdk/setup-runtime`은 런타임에 안전한 설정 helper를 다룹니다:
  import-safe setup patch adapter(`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), lookup-note 출력,
  `promptResolvedAllowFrom`, `splitSetupEntries`, 그리고 위임된
  setup-proxy builder
- `openclaw/plugin-sdk/setup-adapter-runtime`은 `createEnvPatchedAccountSetupAdapter`를 위한
  좁은 env 인식 adapter seam입니다
- `openclaw/plugin-sdk/channel-setup`은 선택적 설치 setup
  builder와 몇 가지 setup-safe primitive를 다룹니다:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,
  `createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
  `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, 그리고
  `splitSetupEntries`
- 더 무거운 공용 setup/config helper(예:
  `moveSingleAccountChannelSectionToDefaultAccount(...)`)도 필요할 때만
  더 넓은 `openclaw/plugin-sdk/setup` seam을 사용하세요

채널이 setup 표면에서 단지 “먼저 이 plugin을 설치하세요”만 알리려는 경우에는
`createOptionalChannelSetupSurface(...)`를 선호하세요. 생성된
adapter/wizard는 config 쓰기와 finalization에서 fail closed하며,
검증, finalize, docs-link 문구 전반에서 동일한 설치 필요 메시지를 재사용합니다.

다른 핫 채널 경로에서도 더 넓은 레거시 표면보다 좁은 helper를 선호하세요:

- 멀티 계정 config 및 기본 계정 대체에는
  `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution`, 그리고
  `openclaw/plugin-sdk/account-helpers`
- 인바운드 route/envelope 및 record-and-dispatch 연결에는
  `openclaw/plugin-sdk/inbound-envelope`와
  `openclaw/plugin-sdk/inbound-reply-dispatch`
- 대상 파싱/매칭에는 `openclaw/plugin-sdk/messaging-targets`
- 미디어 로딩과 아웃바운드
  identity/send delegate에는 `openclaw/plugin-sdk/outbound-media`와
  `openclaw/plugin-sdk/outbound-runtime`
- thread-binding 수명 주기
  및 adapter 등록에는 `openclaw/plugin-sdk/thread-bindings-runtime`
- 레거시 agent/media
  payload 필드 레이아웃이 여전히 필요할 때만 `openclaw/plugin-sdk/agent-media-payload`
- Telegram 사용자 지정 명령
  정규화, 중복/충돌 검증, 대체 안정적 명령
  config 계약에는 `openclaw/plugin-sdk/telegram-command-config`

인증 전용 채널은 일반적으로 기본 경로로 충분합니다. 코어가 승인을 처리하고 plugin은 outbound/auth capability만 노출하면 됩니다. Matrix, Slack, Telegram, 사용자 지정 채팅 transport 같은 네이티브 승인 채널은 자체 승인 수명 주기를 직접 구현하지 말고 공용 네이티브 helper를 사용해야 합니다.

## 단계별 안내

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="패키지와 manifest">
    표준 plugin 파일을 만드세요. `package.json`의 `channel` 필드는
    이것이 채널 plugin임을 나타냅니다. 전체 패키지 메타데이터 표면은
    [Plugin Setup and Config](/plugins/sdk-setup#openclawchannel)를 참조하세요:

    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-chat",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "setupEntry": "./setup-entry.ts",
        "channel": {
          "id": "acme-chat",
          "label": "Acme Chat",
          "blurb": "Connect OpenClaw to Acme Chat."
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-chat",
      "kind": "channel",
      "channels": ["acme-chat"],
      "name": "Acme Chat",
      "description": "Acme Chat channel plugin",
      "configSchema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "acme-chat": {
            "type": "object",
            "properties": {
              "token": { "type": "string" },
              "allowFrom": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    }
    ```
    </CodeGroup>

  </Step>

  <Step title="채널 plugin 객체 만들기">
    `ChannelPlugin` 인터페이스에는 많은 선택적 adapter 표면이 있습니다. 최소 항목인
    `id`와 `setup`부터 시작하고 필요에 따라 adapter를 추가하세요.

    `src/channel.ts`를 만드세요:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // your platform API client

    type ResolvedAccount = {
      accountId: string | null;
      token: string;
      allowFrom: string[];
      dmPolicy: string | undefined;
    };

    function resolveAccount(
      cfg: OpenClawConfig,
      accountId?: string | null,
    ): ResolvedAccount {
      const section = (cfg.channels as Record<string, any>)?.["acme-chat"];
      const token = section?.token;
      if (!token) throw new Error("acme-chat: token is required");
      return {
        accountId: accountId ?? null,
        token,
        allowFrom: section?.allowFrom ?? [],
        dmPolicy: section?.dmSecurity,
      };
    }

    export const acmeChatPlugin = createChatChannelPlugin<ResolvedAccount>({
      base: createChannelPluginBase({
        id: "acme-chat",
        setup: {
          resolveAccount,
          inspectAccount(cfg, accountId) {
            const section =
              (cfg.channels as Record<string, any>)?.["acme-chat"];
            return {
              enabled: Boolean(section?.token),
              configured: Boolean(section?.token),
              tokenStatus: section?.token ? "available" : "missing",
            };
          },
        },
      }),

      // DM security: who can message the bot
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // Pairing: approval flow for new DM contacts
      pairing: {
        text: {
          idLabel: "Acme Chat username",
          message: "Send this code to verify your identity:",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // Threading: how replies are delivered
      threading: { topLevelReplyToMode: "reply" },

      // Outbound: send messages to the platform
      outbound: {
        attachedResults: {
          sendText: async (params) => {
            const result = await acmeChatApi.sendMessage(
              params.to,
              params.text,
            );
            return { messageId: result.id };
          },
        },
        base: {
          sendMedia: async (params) => {
            await acmeChatApi.sendFile(params.to, params.filePath);
          },
        },
      },
    });
    ```

    <Accordion title="createChatChannelPlugin이 대신 처리해 주는 것">
      저수준 adapter 인터페이스를 수동으로 구현하는 대신 선언적 옵션을 전달하면
      builder가 이를 조합해 줍니다:

      | 옵션 | 연결되는 항목 |
      | --- | --- |
      | `security.dm` | config 필드에서 범위가 지정된 DM 보안 해석기 |
      | `pairing.text` | 코드 교환이 있는 텍스트 기반 DM 페어링 흐름 |
      | `threading` | reply-to-mode 해석기(고정, 계정 범위, 또는 사용자 지정) |
      | `outbound.attachedResults` | 결과 메타데이터(메시지 ID)를 반환하는 send 함수 |

      완전한 제어가 필요하다면 선언적 옵션 대신 원시 adapter 객체를 직접 전달할 수도 있습니다.
    </Accordion>

  </Step>

  <Step title="entry point 연결">
    `index.ts`를 만드세요:

    ```typescript index.ts
    import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineChannelPluginEntry({
      id: "acme-chat",
      name: "Acme Chat",
      description: "Acme Chat channel plugin",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Acme Chat management");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Acme Chat management",
                hasSubcommands: false,
              },
            ],
          },
        );
      },
      registerFull(api) {
        api.registerGatewayMethod(/* ... */);
      },
    });
    ```

    채널 소유 CLI descriptor는 `registerCliMetadata(...)`에 넣어
    OpenClaw가 전체 채널 런타임을 활성화하지 않고도 루트 도움말에 이를 표시할 수 있게 하세요.
    일반 전체 로드에서도 동일한 descriptor가 실제 명령 등록에 사용됩니다.
    `registerFull(...)`은 런타임 전용 작업에 유지하세요.
    `registerFull(...)`이 gateway RPC 메서드를 등록한다면
    plugin 전용 prefix를 사용하세요. 코어 관리자 namespace(`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`)는 예약되어 있으며 항상
    `operator.admin`으로 해석됩니다.
    `defineChannelPluginEntry`는 등록 모드 분리를 자동으로 처리합니다. 모든
    옵션은 [Entry Points](/plugins/sdk-entrypoints#definechannelpluginentry)를 참조하세요.

  </Step>

  <Step title="setup entry 추가">
    온보딩 중 경량 로딩을 위해 `setup-entry.ts`를 만드세요:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw는 채널이 비활성화되었거나 구성되지 않은 경우 전체 entry 대신 이를 로드합니다.
    이렇게 하면 setup 흐름 중 무거운 런타임 코드를 끌어오지 않아도 됩니다.
    자세한 내용은 [Setup and Config](/plugins/sdk-setup#setup-entry)를 참조하세요.

  </Step>

  <Step title="인바운드 메시지 처리">
    plugin은 플랫폼에서 메시지를 수신해 OpenClaw로 전달해야 합니다.
    일반적인 패턴은 요청을 검증한 뒤 채널의 인바운드 handler를 통해
    dispatch하는 webhook입니다:

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // plugin-managed auth (verify signatures yourself)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // Your inbound handler dispatches the message to OpenClaw.
          // The exact wiring depends on your platform SDK —
          // see a real example in the bundled Microsoft Teams or Google Chat plugin package.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      인바운드 메시지 처리는 채널별입니다. 각 채널 plugin이
      자체 인바운드 파이프라인을 소유합니다. 실제 패턴은 번들 채널 plugin
      (예: Microsoft Teams 또는 Google Chat plugin 패키지)을 참고하세요.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="테스트">
`src/channel.test.ts`에 함께 위치하는 테스트를 작성하세요:

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("acme-chat plugin", () => {
      it("resolves account from config", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("inspects account without materializing secrets", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("reports missing config", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    공용 테스트 helper는 [Testing](/plugins/sdk-testing)를 참조하세요.

  </Step>
</Steps>

## 파일 구조

```
<bundled-plugin-root>/acme-chat/
├── package.json              # openclaw.channel metadata
├── openclaw.plugin.json      # Manifest with config schema
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Public exports (optional)
├── runtime-api.ts            # Internal runtime exports (optional)
└── src/
    ├── channel.ts            # ChannelPlugin via createChatChannelPlugin
    ├── channel.test.ts       # Tests
    ├── client.ts             # Platform API client
    └── runtime.ts            # Runtime store (if needed)
```

## 고급 주제

<CardGroup cols={2}>
  <Card title="스레딩 옵션" icon="git-branch" href="/plugins/sdk-entrypoints#registration-mode">
    고정, 계정 범위, 또는 사용자 지정 reply mode
  </Card>
  <Card title="Message 도구 통합" icon="puzzle" href="/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool 및 action discovery
  </Card>
  <Card title="대상 해석" icon="crosshair" href="/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="런타임 helper" icon="settings" href="/plugins/sdk-runtime">
    api.runtime를 통한 TTS, STT, 미디어, 하위 에이전트
  </Card>
</CardGroup>

<Note>
일부 번들 helper seam은 번들 plugin 유지 관리와
호환성을 위해 여전히 존재합니다. 하지만 새 채널 plugin에 권장되는 패턴은 아닙니다.
해당 번들 plugin 계열을 직접 유지 관리하는 경우가 아니라면
공용 SDK 표면의 일반적인 channel/setup/reply/runtime subpath를 선호하세요.
</Note>

## 다음 단계

- [Provider Plugins](/plugins/sdk-provider-plugins) — plugin이 모델도 제공하는 경우
- [SDK Overview](/plugins/sdk-overview) — 전체 subpath import 참조
- [SDK Testing](/plugins/sdk-testing) — 테스트 유틸리티 및 계약 테스트
- [Plugin Manifest](/plugins/manifest) — 전체 manifest schema
