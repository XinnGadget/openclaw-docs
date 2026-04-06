---
read_when:
    - Yeni bir mesajlaşma kanalı plugin'i oluşturuyorsunuz
    - OpenClaw'ı bir mesajlaşma platformuna bağlamak istiyorsunuz
    - ChannelPlugin bağdaştırıcı yüzeyini anlamanız gerekiyor
sidebarTitle: Channel Plugins
summary: OpenClaw için bir mesajlaşma kanalı plugin'i oluşturmaya yönelik adım adım kılavuz
title: Kanal Plugin'leri Oluşturma
x-i18n:
    generated_at: "2026-04-06T03:09:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66b52c10945a8243d803af3bf7e1ea0051869ee92eda2af5718d9bb24fbb8552
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Kanal Plugin'leri Oluşturma

Bu kılavuz, OpenClaw'ı bir mesajlaşma platformuna bağlayan bir kanal plugin'inin nasıl oluşturulacağını adım adım açıklar. Sonunda DM güvenliği,
eşleme, yanıt iş parçacığı oluşturma ve giden mesajlaşma içeren çalışan bir kanalınız olacaktır.

<Info>
  Daha önce hiç OpenClaw plugin'i oluşturmadıysanız, temel paket
  yapısı ve manifest kurulumu için önce [Başlangıç](/tr/plugins/building-plugins)
  bölümünü okuyun.
</Info>

## Kanal plugin'leri nasıl çalışır

Kanal plugin'lerinin kendi gönder/düzenle/reaksiyon araçlarına ihtiyacı yoktur. OpenClaw çekirdekte tek bir
paylaşılan `message` aracını tutar. Plugin'iniz şunlara sahip olur:

- **Yapılandırma** — hesap çözümleme ve kurulum sihirbazı
- **Güvenlik** — DM ilkesi ve izin listeleri
- **Eşleme** — DM onay akışı
- **Oturum dil bilgisi** — sağlayıcıya özgü konuşma kimliklerinin temel sohbetlere, iş parçacığı kimliklerine ve üst geri dönüşlerine nasıl eşlendiği
- **Giden** — platforma metin, medya ve anket gönderme
- **İş parçacığı oluşturma** — yanıtların nasıl iş parçacığına bağlandığı

Çekirdek; paylaşılan mesaj aracına, prompt bağlantılarına, dış oturum anahtarı biçimine,
genel `:thread:` kayıt tutmaya ve dağıtıma sahiptir.

Platformunuz konuşma kimlikleri içinde ek kapsam saklıyorsa, bu ayrıştırmayı
plugin içinde `messaging.resolveSessionConversation(...)` ile tutun. Bu,
`rawId` değerini temel konuşma kimliğine, isteğe bağlı iş parçacığı
kimliğine, açık `baseConversationId` değerine ve varsa
`parentConversationCandidates` değerlerine eşlemek için kanonik hook'tur.
`parentConversationCandidates` döndürdüğünüzde bunları en dar üst öğeden en geniş/temel konuşmaya doğru sıralı tutun.

Kanal kayıt defteri başlatılmadan önce aynı ayrıştırmaya ihtiyaç duyan paketli plugin'ler,
eşleşen bir `resolveSessionConversation(...)` dışa aktarımıyla üst düzey bir
`session-key-api.ts` dosyası da sunabilir. Çekirdek bu bootstrap için güvenli yüzeyi
yalnızca çalışma zamanı plugin kayıt defteri henüz kullanılamadığında kullanır.

`messaging.resolveParentConversationCandidates(...)`, bir plugin'in yalnızca
genel/ham kimliğin üstüne üst geri dönüşleri eklemesi gerektiğinde
eski uyumluluk geri dönüşü olarak kullanılmaya devam eder. Her iki hook da varsa,
çekirdek önce `resolveSessionConversation(...).parentConversationCandidates`
değerini kullanır ve yalnızca kanonik hook bunları atladığında
`resolveParentConversationCandidates(...)` değerine geri döner.

## Onaylar ve kanal yetenekleri

Çoğu kanal plugin'inin onaya özel koda ihtiyacı yoktur.

- Çekirdek aynı sohbette `/approve`, paylaşılan onay düğmesi yükleri ve genel geri dönüş teslimatına sahiptir.
- Kanal onaya özel davranış gerektiriyorsa kanal plugin'inde tek bir `approvalCapability` nesnesini tercih edin.
- `approvalCapability.authorizeActorAction` ve `approvalCapability.getActionAvailabilityState`, kanonik onay-yetkilendirme bağlantı yüzeyidir.
- Kanalınız yerel exec onaylarını açığa çıkarıyorsa, yerel taşıma tamamen `approvalCapability.native` altında yaşasa bile `approvalCapability.getActionAvailabilityState` uygulayın. Çekirdek bu kullanılabilirlik hook'unu `enabled` ile `disabled` durumlarını ayırt etmek, başlatan kanalın yerel onayları destekleyip desteklemediğine karar vermek ve kanalı yerel istemci geri dönüş rehberine dahil etmek için kullanır.
- Yinelenen yerel onay istemlerini gizlemek veya teslimat öncesi yazıyor göstergeleri göndermek gibi kanala özgü yük yaşam döngüsü davranışları için `outbound.shouldSuppressLocalPayloadPrompt` veya `outbound.beforeDeliverPayload` kullanın.
- `approvalCapability.delivery` değerini yalnızca yerel onay yönlendirmesi veya geri dönüş bastırma için kullanın.
- `approvalCapability.render` değerini yalnızca bir kanal paylaşılan oluşturucu yerine gerçekten özel onay yüklerine ihtiyaç duyuyorsa kullanın.
- Kanal devre dışı yol yanıtının yerel exec onaylarını etkinleştirmek için gereken tam yapılandırma düğmelerini açıklamasını istiyorsa `approvalCapability.describeExecApprovalSetup` kullanın. Hook `{ channel, channelLabel, accountId }` alır; adlandırılmış hesap kanalları üst düzey varsayılanlar yerine `channels.<channel>.accounts.<id>.execApprovals.*` gibi hesap kapsamlı yollar oluşturmalıdır.
- Bir kanal mevcut yapılandırmadan kararlı sahip benzeri DM kimliklerini çıkarabiliyorsa, onaya özel çekirdek mantığı eklemeden aynı sohbette `/approve` erişimini kısıtlamak için `openclaw/plugin-sdk/approval-runtime` içinden `createResolvedApproverActionAuthAdapter` kullanın.
- Bir kanal yerel onay teslimatına ihtiyaç duyuyorsa, kanal kodunu hedef normalizasyonu ve taşıma hook'larına odaklı tutun. İstek filtreleme, yönlendirme, yineleme kaldırma, sona erme ve gateway aboneliğinin çekirdekte kalması için `openclaw/plugin-sdk/approval-runtime` içinden `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver`, `createApproverRestrictedNativeApprovalCapability` ve `createChannelNativeApprovalRuntime` kullanın.
- Yerel onay kanalları hem `accountId` hem de `approvalKind` değerlerini bu yardımcılar üzerinden yönlendirmelidir. `accountId`, çok hesaplı onay ilkesini doğru bot hesabı kapsamında tutar; `approvalKind` ise çekirdekte sabit kodlu dallar olmadan exec ile plugin onayı davranışının kanal için kullanılabilir kalmasını sağlar.
- Teslim edilen onay kimliği türünü uçtan uca koruyun. Yerel istemciler exec ile plugin onayı yönlendirmesini kanal yerel durumundan tahmin etmemeli veya yeniden yazmamalıdır.
- Farklı onay türleri bilerek farklı yerel yüzeyler açığa çıkarabilir.
  Mevcut paketli örnekler:
  - Slack, hem exec hem de plugin kimlikleri için yerel onay yönlendirmesini kullanılabilir tutar.
  - Matrix, yalnızca exec onayları için yerel DM/kanal yönlendirmesini korur ve
    plugin onaylarını paylaşılan aynı-sohbet `/approve` yolunda bırakır.
- `createApproverRestrictedNativeApprovalAdapter` hâlâ uyumluluk sarmalayıcısı olarak vardır, ancak yeni kodda capability oluşturucusu tercih edilmeli ve plugin üzerinde `approvalCapability` açığa çıkarılmalıdır.

Sıcak kanal giriş noktaları için, bu ailenin yalnızca bir bölümüne ihtiyaç duyduğunuzda
daha dar çalışma zamanı alt yollarını tercih edin:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`

Benzer şekilde, daha geniş şemsiye
yüzeye ihtiyacınız olmadığında `openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` ve
`openclaw/plugin-sdk/reply-chunking` tercih edin.

Özellikle kurulum için:

- `openclaw/plugin-sdk/setup-runtime`, çalışma zamanı için güvenli kurulum yardımcılarını kapsar:
  içe aktarma için güvenli kurulum yama bağdaştırıcıları (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), arama notu çıktısı,
  `promptResolvedAllowFrom`, `splitSetupEntries` ve devredilmiş
  setup-proxy oluşturucuları
- `openclaw/plugin-sdk/setup-adapter-runtime`, `createEnvPatchedAccountSetupAdapter`
  için dar, ortam farkındalıklı bağdaştırıcı bağlantı yüzeyidir
- `openclaw/plugin-sdk/channel-setup`, isteğe bağlı kurulum oluşturucularını ve birkaç kurulum için güvenli ilkel yüzeyi kapsar:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,
  `createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
  `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled` ve
  `splitSetupEntries`
- daha ağır paylaşılan kurulum/yapılandırma yardımcılarına da ihtiyacınız olduğunda
  `moveSingleAccountChannelSectionToDefaultAccount(...)` gibi
  daha geniş `openclaw/plugin-sdk/setup` bağlantı yüzeyini kullanın

Kanalınız yalnızca kurulum yüzeylerinde "önce bu plugin'i yükleyin" bilgisini vermek istiyorsa, `createOptionalChannelSetupSurface(...)` tercih edin. Üretilen
bağdaştırıcı/sihirbaz yapılandırma yazmalarında ve sonlandırmada kapalı güvenli davranır ve
doğrulama, sonlandırma ve belge bağlantısı metninde aynı kurulum-gerekli iletisini yeniden kullanır.

Diğer sıcak kanal yolları için de, daha geniş eski yüzeyler yerine dar yardımcıları tercih edin:

- çok hesaplı yapılandırma ve
  varsayılan hesap geri dönüşü için `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` ve
  `openclaw/plugin-sdk/account-helpers`
- gelen rota/zarf ile
  kaydet-ve-dağıt bağlantısı için `openclaw/plugin-sdk/inbound-envelope` ve
  `openclaw/plugin-sdk/inbound-reply-dispatch`
- hedef ayrıştırma/eşleştirme için `openclaw/plugin-sdk/messaging-targets`
- medya yükleme ile giden
  kimlik/gönderim delege yüzeyleri için `openclaw/plugin-sdk/outbound-media` ve
  `openclaw/plugin-sdk/outbound-runtime`
- iş parçacığı bağlama yaşam döngüsü
  ve bağdaştırıcı kaydı için `openclaw/plugin-sdk/thread-bindings-runtime`
- yalnızca eski ajan/medya
  yük alan düzeni hâlâ gerekiyorsa `openclaw/plugin-sdk/agent-media-payload`
- Telegram özel komut
  normalizasyonu, yinelenen/çakışma doğrulaması ve geri dönüşte kararlı komut
  yapılandırması sözleşmesi için `openclaw/plugin-sdk/telegram-command-config`

Yalnızca kimlik doğrulama yapan kanallar genellikle varsayılan yolda durabilir: çekirdek onayları yönetir ve plugin yalnızca giden/kimlik doğrulama yetenekleri açığa çıkarır. Matrix, Slack, Telegram ve özel sohbet taşımaları gibi yerel onay kanalları, kendi onay yaşam döngülerini yazmak yerine paylaşılan yerel yardımcıları kullanmalıdır.

## Adım adım uygulama

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Paket ve manifest">
    Standart plugin dosyalarını oluşturun. `package.json` içindeki `channel` alanı,
    bunun bir kanal plugin'i olmasını sağlar. Tam paket meta veri yüzeyi için
    bkz. [Plugin Kurulumu ve Yapılandırması](/tr/plugins/sdk-setup#openclawchannel):

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

  <Step title="Kanal plugin nesnesini oluşturun">
    `ChannelPlugin` arayüzünün birçok isteğe bağlı bağdaştırıcı yüzeyi vardır. En az olanla başlayın
    — `id` ve `setup` — ve ihtiyaç duydukça bağdaştırıcı ekleyin.

    `src/channel.ts` dosyasını oluşturun:

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

    <Accordion title="createChatChannelPlugin sizin için ne yapar">
      Düşük seviyeli bağdaştırıcı arayüzlerini elle uygulamak yerine,
      bildirimsel seçenekler verirsiniz ve oluşturucu bunları birleştirir:

      | Seçenek | Bağladığı şey |
      | --- | --- |
      | `security.dm` | Yapılandırma alanlarından kapsamlı DM güvenlik çözümleyicisi |
      | `pairing.text` | Kod alışverişli metin tabanlı DM eşleme akışı |
      | `threading` | Yanıtlama modu çözümleyicisi (sabit, hesap kapsamlı veya özel) |
      | `outbound.attachedResults` | Sonuç meta verisi döndüren gönderim işlevleri (mesaj kimlikleri) |

      Tam denetime ihtiyacınız varsa bildirimsel seçenekler yerine ham bağdaştırıcı nesneleri de geçebilirsiniz.
    </Accordion>

  </Step>

  <Step title="Giriş noktasını bağlayın">
    `index.ts` dosyasını oluşturun:

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

    Kanalın sahip olduğu CLI tanımlayıcılarını `registerCliMetadata(...)` içine koyun; böylece OpenClaw
    tam kanal çalışma zamanını etkinleştirmeden kök yardımda bunları gösterebilir,
    normal tam yüklemeler ise gerçek komut kaydı için aynı tanımlayıcıları almaya devam eder.
    `registerFull(...)` değerini yalnızca çalışma zamanına özel işler için tutun.
    `registerFull(...)` gateway RPC yöntemleri kaydediyorsa,
    plugin'e özgü bir önek kullanın. Çekirdek yönetici ad alanları (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) ayrılmış kalır ve her zaman
    `operator.admin` değerine çözülür.
    `defineChannelPluginEntry`, kayıt modu ayrımını otomatik olarak yönetir. Tüm
    seçenekler için bkz. [Giriş Noktaları](/tr/plugins/sdk-entrypoints#definechannelpluginentry).

  </Step>

  <Step title="Bir kurulum girişi ekleyin">
    Onboarding sırasında hafif yükleme için `setup-entry.ts` oluşturun:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw, kanal devre dışıysa veya yapılandırılmamışsa tam giriş yerine bunu yükler.
    Bu, kurulum akışları sırasında ağır çalışma zamanı kodunun içe alınmasını önler.
    Ayrıntılar için bkz. [Kurulum ve Yapılandırma](/tr/plugins/sdk-setup#setup-entry).

  </Step>

  <Step title="Gelen mesajları işleyin">
    Plugin'inizin platformdan mesaj alması ve bunları OpenClaw'a iletmesi gerekir.
    Tipik desen, isteği doğrulayan ve
    kendi kanalınızın gelen işleyicisi üzerinden dağıtan bir webhook'tur:

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
      Gelen mesaj işleme kanala özgüdür. Her kanal plugin'i
      kendi gelen işlem hattına sahiptir. Gerçek desenler için paketli kanal plugin'lerine
      (örneğin Microsoft Teams veya Google Chat plugin paketi) bakın.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Test">
Birlikte konumlandırılmış testleri `src/channel.test.ts` içine yazın:

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

    Paylaşılan test yardımcıları için bkz. [Testing](/tr/plugins/sdk-testing).

  </Step>
</Steps>

## Dosya yapısı

```
<bundled-plugin-root>/acme-chat/
├── package.json              # openclaw.channel meta verileri
├── openclaw.plugin.json      # Yapılandırma şemasını içeren manifest
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Genel dışa aktarımlar (isteğe bağlı)
├── runtime-api.ts            # İç çalışma zamanı dışa aktarımları (isteğe bağlı)
└── src/
    ├── channel.ts            # createChatChannelPlugin ile ChannelPlugin
    ├── channel.test.ts       # Testler
    ├── client.ts             # Platform API istemcisi
    └── runtime.ts            # Çalışma zamanı deposu (gerekirse)
```

## İleri düzey konular

<CardGroup cols={2}>
  <Card title="İş parçacığı seçenekleri" icon="git-branch" href="/tr/plugins/sdk-entrypoints#registration-mode">
    Sabit, hesap kapsamlı veya özel yanıt modları
  </Card>
  <Card title="Mesaj aracı entegrasyonu" icon="puzzle" href="/tr/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool ve eylem keşfi
  </Card>
  <Card title="Hedef çözümleme" icon="crosshair" href="/tr/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="Çalışma zamanı yardımcıları" icon="settings" href="/tr/plugins/sdk-runtime">
    api.runtime üzerinden TTS, STT, medya, alt ajan
  </Card>
</CardGroup>

<Note>
Bazı paketli yardımcı bağlantı yüzeyleri, paketli plugin bakımı ve
uyumluluk için hâlâ vardır. Bunlar yeni kanal plugin'leri için önerilen desen değildir;
bu paketli plugin ailesini doğrudan korumuyorsanız
ortak SDK yüzeyindeki genel channel/setup/reply/runtime alt yollarını tercih edin.
</Note>

## Sonraki adımlar

- [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins) — plugin'iniz modeller de sağlıyorsa
- [SDK Genel Bakış](/tr/plugins/sdk-overview) — tam alt yol içe aktarma başvurusu
- [SDK Testing](/tr/plugins/sdk-testing) — test yardımcıları ve sözleşme testleri
- [Plugin Manifest](/tr/plugins/manifest) — tam manifest şeması
