---
read_when:
    - Yeni bir mesajlaşma kanalı plugin'i oluşturuyorsunuz
    - OpenClaw'u bir mesajlaşma platformuna bağlamak istiyorsunuz
    - ChannelPlugin adaptör yüzeyini anlamanız gerekiyor
sidebarTitle: Channel Plugins
summary: OpenClaw için bir mesajlaşma kanalı plugin'i oluşturmaya yönelik adım adım kılavuz
title: Channel Plugins Oluşturma
x-i18n:
    generated_at: "2026-04-07T08:47:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0aab6cc835b292c62e33c52ad0c35f989fb1a5b225511e8bdc2972feb3c64f09
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Channel Plugins Oluşturma

Bu kılavuz, OpenClaw'u bir mesajlaşma platformuna bağlayan bir kanal plugin'i
oluşturmayı adım adım anlatır. Sonunda DM güvenliği, eşleştirme,
yanıt iş parçacığı oluşturma ve giden mesajlaşma ile çalışan bir kanala sahip olacaksınız.

<Info>
  Daha önce hiç OpenClaw plugin'i oluşturmadıysanız, temel paket
  yapısı ve manifest kurulumu için önce [Getting Started](/tr/plugins/building-plugins)
  sayfasını okuyun.
</Info>

## Kanal plugin'leri nasıl çalışır

Kanal plugin'lerinin kendi send/edit/react araçlarına ihtiyacı yoktur. OpenClaw
çekirdekte tek bir paylaşılan `message` aracını korur. Plugin'iniz şunların sahibi olur:

- **Config** — hesap çözümleme ve kurulum sihirbazı
- **Security** — DM ilkesi ve allowlist'ler
- **Pairing** — DM onay akışı
- **Session grammar** — sağlayıcıya özgü konuşma kimliklerinin temel sohbetlere, thread id'lerine ve üst fallback'lere nasıl eşlendiği
- **Outbound** — platforma metin, medya ve anket gönderme
- **Threading** — yanıtların nasıl iş parçacıklarına bağlandığı

Çekirdek; paylaşılan message aracının, prompt bağlantılarının, dış oturum-anahtarı
biçiminin, genel `:thread:` kayıtlarının ve dispatch işleminin sahibidir.

Platformunuz konuşma kimliklerinin içinde ek kapsam saklıyorsa, bu ayrıştırmayı
plugin içinde `messaging.resolveSessionConversation(...)` ile tutun. Bu,
`rawId` değerini temel konuşma kimliğine, isteğe bağlı thread
kimliğine, açık `baseConversationId` değerine ve herhangi bir
`parentConversationCandidates` değerine eşlemek için kanonik kancadır.
`parentConversationCandidates` döndürdüğünüzde, bunları en dar üst öğeden
en geniş/temel konuşmaya doğru sıralı tutun.

Kanal kayıt sistemi başlatılmadan önce aynı ayrıştırmaya ihtiyaç duyan paketlenmiş
plugin'ler ayrıca eşleşen bir `resolveSessionConversation(...)` export'una sahip
üst düzey bir `session-key-api.ts` dosyası da sunabilir. Çekirdek bu bootstrap-safe yüzeyi
yalnızca çalışma zamanı plugin kayıt sistemi henüz mevcut değilken kullanır.

`messaging.resolveParentConversationCandidates(...)`, bir plugin yalnızca genel/ham kimliğin
üstüne üst fallback'lere ihtiyaç duyduğunda eski uyumluluk yedeği olarak kullanılmaya
devam eder. Her iki kanca da varsa, çekirdek önce
`resolveSessionConversation(...).parentConversationCandidates` değerini kullanır ve yalnızca
kanonik kanca bunları atladığında `resolveParentConversationCandidates(...)` değerine geri döner.

## Onaylar ve kanal yetenekleri

Çoğu kanal plugin'inin onaya özel koda ihtiyacı yoktur.

- Çekirdek; aynı sohbet içindeki `/approve`, paylaşılan onay düğmesi payload'ları ve genel fallback tesliminin sahibidir.
- Kanalın onaya özgü davranışa ihtiyacı olduğunda kanal plugin'i üzerinde tek bir `approvalCapability` nesnesini tercih edin.
- `approvalCapability.authorizeActorAction` ve `approvalCapability.getActionAvailabilityState`, kanonik approval-auth bağlantı yüzeyidir.
- Kanalınız yerel exec onayları sunuyorsa, yerel taşıma tamamen `approvalCapability.native` altında yaşasa bile `approvalCapability.getActionAvailabilityState` uygulayın. Çekirdek, `enabled` ve `disabled` ayrımını yapmak, başlatan kanalın yerel onayları destekleyip desteklemediğine karar vermek ve kanalı yerel istemci fallback rehberliğine dahil etmek için bu kullanılabilirlik kancasını kullanır.
- Yinelenen yerel onay istemlerini gizleme veya teslimattan önce yazıyor göstergeleri gönderme gibi kanala özgü payload yaşam döngüsü davranışları için `outbound.shouldSuppressLocalPayloadPrompt` veya `outbound.beforeDeliverPayload` kullanın.
- `approvalCapability.delivery` öğesini yalnızca yerel onay yönlendirme veya fallback bastırma için kullanın.
- `approvalCapability.render` öğesini yalnızca bir kanal paylaşılan renderer yerine gerçekten özel onay payload'larına ihtiyaç duyuyorsa kullanın.
- Kanal, devre dışı yol yanıtının yerel exec onaylarını etkinleştirmek için gereken tam config ayarlarını açıklamasını istiyorsa `approvalCapability.describeExecApprovalSetup` kullanın. Kanca `{ channel, channelLabel, accountId }` alır; adlandırılmış hesap kanalları üst düzey varsayılanlar yerine `channels.<channel>.accounts.<id>.execApprovals.*` gibi hesap kapsamlı yollar oluşturmalıdır.
- Bir kanal mevcut config'den kararlı sahip benzeri DM kimliklerini çıkarabiliyorsa, onaya özel çekirdek mantığı eklemeden aynı sohbet içindeki `/approve` erişimini kısıtlamak için `openclaw/plugin-sdk/approval-runtime` içinden `createResolvedApproverActionAuthAdapter` kullanın.
- Bir kanal yerel onay teslimine ihtiyaç duyuyorsa, kanal kodunu hedef normalizasyonu ve taşıma kancalarına odaklı tutun. Çekirdeğin istek filtreleme, yönlendirme, tekrar giderme, süre sonu ve gateway aboneliğinin sahibi olması için `openclaw/plugin-sdk/approval-runtime` içinden `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver`, `createApproverRestrictedNativeApprovalCapability` ve `createChannelNativeApprovalRuntime` kullanın.
- Yerel onay kanalları bu yardımcılar üzerinden hem `accountId` hem de `approvalKind` yönlendirmelidir. `accountId`, çoklu hesap onay ilkesini doğru bot hesabı kapsamında tutar ve `approvalKind`, çekirdekte sabit kodlanmış dallanmalar olmadan exec ile plugin onay davranışını kanala açık tutar.
- Teslim edilen onay kimliği türünü uçtan uca koruyun. Yerel istemciler,
  exec ile plugin onay yönlendirmesini kanal yerel durumdan tahmin etmemeli
  veya yeniden yazmamalıdır.
- Farklı onay türleri kasıtlı olarak farklı yerel yüzeyler sunabilir.
  Güncel paketlenmiş örnekler:
  - Slack, hem exec hem de plugin kimlikleri için yerel onay yönlendirmesini kullanılabilir tutar.
  - Matrix, yalnızca exec onayları için yerel DM/kanal yönlendirmesini korur ve
    plugin onaylarını paylaşılan aynı sohbet içindeki `/approve` yolunda bırakır.
- `createApproverRestrictedNativeApprovalAdapter` hâlâ bir uyumluluk sarmalayıcısı olarak vardır, ancak yeni kod capability builder'ı tercih etmeli ve plugin üzerinde `approvalCapability` göstermelidir.

Sıcak kanal entrypoint'leri için, bu ailenin yalnızca bir bölümüne ihtiyacınız olduğunda
daha dar çalışma zamanı alt yollarını tercih edin:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`

Benzer şekilde, daha geniş üst şemsiye
yüzeyine ihtiyacınız olmadığında `openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` ve
`openclaw/plugin-sdk/reply-chunking` tercih edin.

Özellikle kurulum için:

- `openclaw/plugin-sdk/setup-runtime`, çalışma zamanı açısından güvenli kurulum yardımcılarını kapsar:
  import-safe setup patch adaptörleri (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), lookup-note çıktısı,
  `promptResolvedAllowFrom`, `splitSetupEntries` ve devredilmiş
  setup-proxy builder'ları
- `openclaw/plugin-sdk/setup-adapter-runtime`, `createEnvPatchedAccountSetupAdapter`
  için dar, env-aware adaptör bağlantı yüzeyidir
- `openclaw/plugin-sdk/channel-setup`, isteğe bağlı kurulum builder'larını ve birkaç setup-safe primitifi kapsar:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

Kanalınız env tabanlı kurulum veya auth destekliyorsa ve genel başlangıç/config
akışlarının çalışma zamanı yüklenmeden önce bu env adlarını bilmesi gerekiyorsa,
bunları plugin manifest içinde `channelEnvVars` ile bildirin. Kanal çalışma zamanı `envVars`
veya yerel sabitlerini yalnızca operatöre dönük metinler için tutun.
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled` ve
`splitSetupEntries`

- yalnızca
  `moveSingleAccountChannelSectionToDefaultAccount(...)` gibi daha ağır paylaşılan setup/config yardımcılarına da ihtiyacınız varsa
  daha geniş `openclaw/plugin-sdk/setup` bağlantı yüzeyini kullanın

Kanalınız kurulum yüzeylerinde yalnızca "önce bu plugin'i yükleyin" duyurusu yapmak istiyorsa,
`createOptionalChannelSetupSurface(...)` tercih edin. Oluşturulan
adaptör/sihirbaz config yazımlarında ve sonlandırmada fail-closed davranır; ayrıca
doğrulama, finalize ve docs-link metinleri boyunca aynı yükleme gerekli mesajını yeniden kullanır.

Diğer sıcak kanal yolları için, daha geniş eski yüzeyler yerine dar yardımcıları tercih edin:

- çoklu hesap config'i ve
  varsayılan hesap fallback'i için `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` ve
  `openclaw/plugin-sdk/account-helpers`
- gelen rota/zarf ve
  kaydet-ve-dispatch bağlantıları için `openclaw/plugin-sdk/inbound-envelope` ve
  `openclaw/plugin-sdk/inbound-reply-dispatch`
- hedef ayrıştırma/eşleştirme için `openclaw/plugin-sdk/messaging-targets`
- medya yükleme ile giden
  kimlik/gönderim delegeleri için `openclaw/plugin-sdk/outbound-media` ve
  `openclaw/plugin-sdk/outbound-runtime`
- thread-binding yaşam döngüsü
  ve adaptör kaydı için `openclaw/plugin-sdk/thread-bindings-runtime`
- yalnızca eski bir agent/media
  payload alan düzeni hâlâ gerekiyorsa `openclaw/plugin-sdk/agent-media-payload`
- Telegram özel komut
  normalizasyonu, yinelenen/çakışma doğrulaması ve fallback açısından kararlı komut
  config sözleşmesi için `openclaw/plugin-sdk/telegram-command-config`

Yalnızca auth kullanan kanallar genellikle varsayılan yolda durabilir: çekirdek onayları yönetir ve plugin yalnızca outbound/auth yeteneklerini sunar. Matrix, Slack, Telegram ve özel sohbet taşıma sistemleri gibi yerel onay kanalları, kendi onay yaşam döngülerini yazmak yerine paylaşılan yerel yardımcıları kullanmalıdır.

## Gelen mention ilkesi

Gelen mention işlemesini iki katmana ayrılmış halde tutun:

- plugin'in sahip olduğu kanıt toplama
- paylaşılan ilke değerlendirmesi

Paylaşılan katman için `openclaw/plugin-sdk/channel-inbound` kullanın.

Plugin yerel mantık için uygun örnekler:

- bota yanıt verme tespiti
- bottan alıntı tespiti
- thread katılımı kontrolleri
- servis/sistem mesajı hariç tutmaları
- bot katılımını kanıtlamak için gereken platform yerel cache'ler

Paylaşılan yardımcı için uygun örnekler:

- `requireMention`
- açık mention sonucu
- örtük mention allowlist'i
- komut bypass'ı
- son atlama kararı

Tercih edilen akış:

1. Yerel mention gerçeklerini hesaplayın.
2. Bu gerçekleri `resolveInboundMentionDecision({ facts, policy })` içine geçirin.
3. Gelen kapınızda `decision.effectiveWasMentioned`, `decision.shouldBypassMention` ve `decision.shouldSkip` kullanın.

```typescript
import {
  implicitMentionKindWhen,
  matchesMentionWithExplicit,
  resolveInboundMentionDecision,
} from "openclaw/plugin-sdk/channel-inbound";

const mentionMatch = matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const facts = {
  canDetectMention: true,
  wasMentioned: mentionMatch.matched,
  hasAnyMention: mentionMatch.hasExplicitMention,
  implicitMentionKinds: [
    ...implicitMentionKindWhen("reply_to_bot", isReplyToBot),
    ...implicitMentionKindWhen("quoted_bot", isQuoteOfBot),
  ],
};

const decision = resolveInboundMentionDecision({
  facts,
  policy: {
    isGroup,
    requireMention,
    allowedImplicitMentionKinds: requireExplicitMention ? [] : ["reply_to_bot", "quoted_bot"],
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});

if (decision.shouldSkip) return;
```

`api.runtime.channel.mentions`, çalışma zamanı enjeksiyonuna zaten bağımlı olan
paketlenmiş kanal plugin'leri için aynı paylaşılan mention yardımcılarını sunar:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

Eski `resolveMentionGating*` yardımcıları
`openclaw/plugin-sdk/channel-inbound` üzerinde yalnızca uyumluluk export'ları olarak kalır. Yeni kod,
`resolveInboundMentionDecision({ facts, policy })` kullanmalıdır.

## Adım adım anlatım

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Paket ve manifest">
    Standart plugin dosyalarını oluşturun. `package.json` içindeki `channel` alanı,
    bunun bir kanal plugin'i olmasını sağlar. Tam paket meta verisi yüzeyi için
    bkz. [Plugin Setup and Config](/tr/plugins/sdk-setup#openclawchannel):

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
          "blurb": "OpenClaw'u Acme Chat'e bağlayın."
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
      "description": "Acme Chat kanal plugin'i",
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

  <Step title="Kanal plugin nesnesini oluştur">
    `ChannelPlugin` arayüzü çok sayıda isteğe bağlı adaptör yüzeyine sahiptir. En düşük düzeyden,
    yani `id` ve `setup` ile başlayın ve ihtiyaç duydukça adaptör ekleyin.

    `src/channel.ts` oluşturun:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // platform API istemciniz

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
          idLabel: "Acme Chat kullanıcı adı",
          message: "Kimliğinizi doğrulamak için bu kodu gönderin:",
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

    <Accordion title="createChatChannelPlugin sizin için ne yapar">
      Düşük seviyeli adaptör arayüzlerini elle uygulamak yerine,
      bildirime dayalı seçenekler verirsiniz ve builder bunları birleştirir:

      | Seçenek | Bağladığı şey |
      | --- | --- |
      | `security.dm` | Config alanlarından kapsamlı DM güvenliği çözücüsü |
      | `pairing.text` | Kod alışverişiyle metin tabanlı DM eşleştirme akışı |
      | `threading` | Reply-to-mode çözücüsü (sabit, hesap kapsamlı veya özel) |
      | `outbound.attachedResults` | Sonuç meta verilerini döndüren gönderme işlevleri (mesaj kimlikleri) |

      Tam denetime ihtiyacınız varsa bildirime dayalı seçenekler yerine
      ham adaptör nesneleri de geçebilirsiniz.
    </Accordion>

  </Step>

  <Step title="Entry point'i bağla">
    `index.ts` oluşturun:

    ```typescript index.ts
    import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineChannelPluginEntry({
      id: "acme-chat",
      name: "Acme Chat",
      description: "Acme Chat kanal plugin'i",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Acme Chat yönetimi");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Acme Chat yönetimi",
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

    Kanalın sahip olduğu CLI tanımlayıcılarını `registerCliMetadata(...)` içine koyun; böylece OpenClaw
    tam kanal çalışma zamanını etkinleştirmeden bunları kök yardım ekranında gösterebilir.
    Normal tam yüklemeler ise gerçek komut kaydı için aynı tanımlayıcıları almaya devam eder.
    `registerFull(...)` bölümünü yalnızca çalışma zamanına özgü işler için tutun.
    `registerFull(...)` gateway RPC yöntemleri kaydediyorsa,
    plugin'e özgü bir önek kullanın. Çekirdek yönetici ad alanları (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) ayrılmış kalır ve her zaman
    `operator.admin` olarak çözülür.
    `defineChannelPluginEntry`, kayıt modu ayrımını otomatik olarak yönetir. Tüm
    seçenekler için bkz. [Entry Points](/tr/plugins/sdk-entrypoints#definechannelpluginentry).

  </Step>

  <Step title="Bir setup entry ekle">
    Onboarding sırasında hafif yükleme için `setup-entry.ts` oluşturun:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw, kanal devre dışı veya yapılandırılmamış olduğunda tam entry yerine bunu yükler.
    Bu, kurulum akışları sırasında ağır çalışma zamanı kodunu çekmekten kaçınır.
    Ayrıntılar için bkz. [Setup and Config](/tr/plugins/sdk-setup#setup-entry).

  </Step>

  <Step title="Gelen mesajları işle">
    Plugin'inizin platformdan mesaj alması ve bunları OpenClaw'a yönlendirmesi gerekir.
    Tipik örüntü, isteği doğrulayan ve
    bunu kanalınızın gelen işleyicisi üzerinden dispatch eden bir webhook'tur:

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // plugin tarafından yönetilen auth (imzaları kendiniz doğrulayın)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // Gelen işleyiciniz mesajı OpenClaw'a dispatch eder.
          // Tam bağlantı, platform SDK'nize bağlıdır —
          // paketlenmiş Microsoft Teams veya Google Chat plugin paketinde gerçek bir örneğe bakın.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      Gelen mesaj işleme kanala özgüdür. Her kanal plugin'i
      kendi gelen pipeline'ının sahibidir. Gerçek örüntüler için
      paketlenmiş kanal plugin'lerine
      (örneğin Microsoft Teams veya Google Chat plugin paketi) bakın.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Test">
Eş konumlu testleri `src/channel.test.ts` içinde yazın:

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("acme-chat plugin", () => {
      it("config içinden hesabı çözümler", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("gizli değerleri somutlaştırmadan hesabı inceler", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("eksik config'i bildirir", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    Paylaşılan test yardımcıları için bkz. [Testing](/tr/plugins/sdk-testing).

  </Step>
</Steps>

## Dosya yapısı

```
<bundled-plugin-root>/acme-chat/
├── package.json              # openclaw.channel meta verisi
├── openclaw.plugin.json      # Config şemasına sahip manifest
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Herkese açık export'lar (isteğe bağlı)
├── runtime-api.ts            # Dahili çalışma zamanı export'ları (isteğe bağlı)
└── src/
    ├── channel.ts            # createChatChannelPlugin ile ChannelPlugin
    ├── channel.test.ts       # Testler
    ├── client.ts             # Platform API istemcisi
    └── runtime.ts            # Çalışma zamanı deposu (gerekiyorsa)
```

## İleri konular

<CardGroup cols={2}>
  <Card title="Threading seçenekleri" icon="git-branch" href="/tr/plugins/sdk-entrypoints#registration-mode">
    Sabit, hesap kapsamlı veya özel yanıt modları
  </Card>
  <Card title="Message aracı entegrasyonu" icon="puzzle" href="/tr/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool ve eylem keşfi
  </Card>
  <Card title="Hedef çözümleme" icon="crosshair" href="/tr/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="Çalışma zamanı yardımcıları" icon="settings" href="/tr/plugins/sdk-runtime">
    api.runtime üzerinden TTS, STT, medya, subagent
  </Card>
</CardGroup>

<Note>
Bazı paketlenmiş yardımcı bağlantı yüzeyleri, paketlenmiş plugin bakımı ve
uyumluluk için hâlâ vardır. Yeni kanal plugin'leri için önerilen örüntü bunlar değildir;
o paketlenmiş plugin ailesini doğrudan sürdürmüyorsanız ortak SDK
yüzeyindeki genel channel/setup/reply/runtime alt yollarını tercih edin.
</Note>

## Sonraki adımlar

- [Provider Plugins](/tr/plugins/sdk-provider-plugins) — plugin'iniz model de sağlıyorsa
- [SDK Overview](/tr/plugins/sdk-overview) — tam alt yol import referansı
- [SDK Testing](/tr/plugins/sdk-testing) — test yardımcıları ve sözleşme testleri
- [Plugin Manifest](/tr/plugins/manifest) — tam manifest şeması
