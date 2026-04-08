---
read_when:
    - Yeni bir mesajlaşma kanal eklentisi oluşturuyorsunuz
    - OpenClaw'u bir mesajlaşma platformuna bağlamak istiyorsunuz
    - ChannelPlugin bağdaştırıcı yüzeyini anlamanız gerekiyor
sidebarTitle: Channel Plugins
summary: OpenClaw için bir mesajlaşma kanal eklentisi oluşturmaya yönelik adım adım kılavuz
title: Kanal Eklentileri Oluşturma
x-i18n:
    generated_at: "2026-04-08T02:17:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: d23365b6d92006b30e671f9f0afdba40a2b88c845c5d2299d71c52a52985672f
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Kanal Eklentileri Oluşturma

Bu kılavuz, OpenClaw'u bir mesajlaşma platformuna bağlayan bir kanal eklentisi
oluşturmayı adım adım açıklar. Sonunda DM güvenliği,
eşleştirme, yanıt iş parçacığı oluşturma ve giden mesajlaşma özelliklerine sahip çalışan bir kanalınız olacak.

<Info>
  Daha önce hiç OpenClaw eklentisi oluşturmadıysanız, temel paket
  yapısı ve manifest kurulumu için önce [Getting Started](/tr/plugins/building-plugins) bölümünü okuyun.
</Info>

## Kanal eklentileri nasıl çalışır

Kanal eklentilerinin kendi send/edit/react araçlarına ihtiyacı yoktur. OpenClaw, çekirdekte tek bir ortak
`message` aracını tutar. Eklentiniz şunların sahibidir:

- **Config** — hesap çözümleme ve kurulum sihirbazı
- **Security** — DM politikası ve allowlist'ler
- **Pairing** — DM onay akışı
- **Session grammar** — sağlayıcıya özgü konuşma kimliklerinin temel sohbetlere, iş parçacığı kimliklerine ve üst fallback'lerine nasıl eşlendiği
- **Outbound** — platforma metin, medya ve anket gönderme
- **Threading** — yanıtların nasıl iş parçacığına bağlandığı

Çekirdek; ortak message aracına, istem bağlantısına, dış oturum anahtarı biçimine,
genel `:thread:` kayıt tutmaya ve dağıtıma sahiptir.

Platformunuz konuşma kimlikleri içinde ek kapsam depoluyorsa, bu ayrıştırmayı
eklenti içinde `messaging.resolveSessionConversation(...)` ile tutun. Bu,
`rawId` değerini temel konuşma kimliğine, isteğe bağlı iş parçacığı
kimliğine, açık `baseConversationId` değerine ve herhangi bir `parentConversationCandidates`
değerine eşlemek için kanonik hook'tur.
`parentConversationCandidates` döndürdüğünüzde, bunları en dar üstten en geniş/temel konuşmaya
doğru sıralı tutun.

Kanal kayıt defteri başlatılmadan önce aynı ayrıştırmaya ihtiyaç duyan paketlenmiş eklentiler,
eşleşen bir `resolveSessionConversation(...)` dışa aktarımıyla üst düzey bir
`session-key-api.ts` dosyası da sunabilir. Çekirdek bu bootstrap açısından güvenli yüzeyi
yalnızca çalışma zamanı eklenti kayıt defteri henüz kullanılabilir değilken kullanır.

`messaging.resolveParentConversationCandidates(...)`, bir eklentinin yalnızca
genel/raw kimliğin üstüne parent fallback'lerine ihtiyaç duyduğu eski uyumluluk fallback'i olarak kullanılmaya devam eder.
Her iki hook da varsa, çekirdek önce
`resolveSessionConversation(...).parentConversationCandidates` kullanır ve yalnızca bu kanonik hook
bunları atladığında `resolveParentConversationCandidates(...)` değerine fallback yapar.

## Onaylar ve kanal yetenekleri

Çoğu kanal eklentisinin onaya özel koda ihtiyacı yoktur.

- Çekirdek aynı sohbette `/approve`, ortak onay düğmesi payload'ları ve genel fallback teslimini yönetir.
- Kanal onaya özgü davranış gerektiriyorsa, kanal eklentisinde tek bir `approvalCapability` nesnesi tercih edin.
- `ChannelPlugin.approvals` kaldırıldı. Onay teslimi/yerel işleme/auth bilgilerini `approvalCapability` içine koyun.
- `plugin.auth` yalnızca login/logout içindir; çekirdek artık bu nesneden onay auth hook'larını okumaz.
- `approvalCapability.authorizeActorAction` ve `approvalCapability.getActionAvailabilityState`, kanonik onay-auth bağlantı yüzeyidir.
- Aynı sohbette onay auth kullanılabilirliği için `approvalCapability.getActionAvailabilityState` kullanın.
- Kanalınız yerel exec onayları sunuyorsa, başlatan yüzey/yerel istemci durumu aynı sohbet onay auth'undan farklı olduğunda `approvalCapability.getExecInitiatingSurfaceState` kullanın. Çekirdek bu exec'e özgü hook'u `enabled` ile `disabled` durumunu ayırt etmek, başlatan kanalın yerel exec onaylarını destekleyip desteklemediğine karar vermek ve kanalı yerel istemci fallback rehberliğine dahil etmek için kullanır. `createApproverRestrictedNativeApprovalCapability(...)` bunu yaygın durum için doldurur.
- Yinelenen yerel onay istemlerini gizlemek veya teslimattan önce yazıyor göstergeleri göndermek gibi kanala özgü payload yaşam döngüsü davranışları için `outbound.shouldSuppressLocalPayloadPrompt` veya `outbound.beforeDeliverPayload` kullanın.
- `approvalCapability.delivery` yalnızca yerel onay yönlendirmesi veya fallback bastırma için kullanılmalıdır.
- `approvalCapability.nativeRuntime` değerini kanala ait yerel onay bilgileri için kullanın. Çekirdek onay yaşam döngüsünü oluşturabilsin diye bunu sıcak kanal giriş noktalarında `createLazyChannelApprovalNativeRuntimeAdapter(...)` ile tembel tutun; bu, çalışma zamanı modülünüzü gerektiğinde içe aktarabilir.
- `approvalCapability.render` yalnızca bir kanal ortak işleyici yerine gerçekten özel onay payload'larına ihtiyaç duyuyorsa kullanılmalıdır.
- Kanal, devre dışı bırakılmış yoldaki yanıtta yerel exec onaylarını etkinleştirmek için gereken tam yapılandırma düğmelerini açıklamak istiyorsa `approvalCapability.describeExecApprovalSetup` kullanın. Hook `{ channel, channelLabel, accountId }` alır; adlandırılmış hesap kanalları üst düzey varsayılanlar yerine `channels.<channel>.accounts.<id>.execApprovals.*` gibi hesap kapsamlı yollar göstermelidir.
- Bir kanal mevcut yapılandırmadan kararlı owner benzeri DM kimliklerini çıkarabiliyorsa, onaya özgü çekirdek mantığı eklemeden aynı sohbette `/approve` erişimini kısıtlamak için `openclaw/plugin-sdk/approval-runtime` içinden `createResolvedApproverActionAuthAdapter` kullanın.
- Kanal yerel onay teslimine ihtiyaç duyuyorsa, kanal kodunu hedef normalizasyonu ile taşıma/sunum bilgilerine odaklı tutun. `openclaw/plugin-sdk/approval-runtime` içinden `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver` ve `createApproverRestrictedNativeApprovalCapability` kullanın. Kanala özgü bilgileri `approvalCapability.nativeRuntime` arkasına, ideal olarak `createChannelApprovalNativeRuntimeAdapter(...)` veya `createLazyChannelApprovalNativeRuntimeAdapter(...)` üzerinden koyun; böylece çekirdek işleyiciyi birleştirebilir ve istek filtreleme, yönlendirme, tekilleştirme, süre sonu, gateway aboneliği ve başka yere yönlendirildi bildirimlerine sahip olabilir. `nativeRuntime` birkaç küçük bağlantı yüzeyine ayrılmıştır:
- `availability` — hesabın yapılandırılmış olup olmadığı ve bir isteğin işlenip işlenmemesi gerektiği
- `presentation` — ortak onay görünüm modelini bekleyen/çözümlenen/süresi dolan yerel payload'lara veya son eylemlere eşleme
- `transport` — hedefleri hazırlama ve yerel onay mesajlarını gönderme/güncelleme/silme
- `interactions` — yerel düğmeler veya tepkiler için isteğe bağlı bind/unbind/clear-action hook'ları
- `observe` — isteğe bağlı teslim tanılama hook'ları
- Kanalın istemci, token, Bolt uygulaması veya webhook alıcısı gibi çalışma zamanı sahipli nesnelere ihtiyacı varsa, bunları `openclaw/plugin-sdk/channel-runtime-context` üzerinden kaydedin. Genel runtime-context kayıt defteri, çekirdeğin onaya özgü sarmalayıcı glue eklemeden kanal başlangıç durumundan yetenek odaklı işleyicileri bootstrap etmesini sağlar.
- Yalnızca yetenek odaklı bağlantı yüzeyi henüz yeterince ifade edici değilse daha alt düzey `createChannelApprovalHandler` veya `createChannelNativeApprovalRuntime` kullanımına başvurun.
- Yerel onay kanalları, hem `accountId` hem de `approvalKind` değerini bu yardımcılar üzerinden yönlendirmelidir. `accountId`, çok hesaplı onay politikasını doğru bot hesabına kapsamlı tutar; `approvalKind` ise exec ile eklenti onayı davranışını çekirdekte sabit dallanmalar olmadan kanal için kullanılabilir kılar.
- Çekirdek artık onay yeniden yönlendirme bildirimlerinin de sahibidir. Kanal eklentileri, `createChannelNativeApprovalRuntime` içinden kendi "onay DM'lere / başka bir kanala gitti" takip mesajlarını göndermemelidir; bunun yerine ortak onay yetenek yardımcıları üzerinden doğru origin + approver-DM yönlendirmesini sunmalı ve çekirdeğin başlatan sohbete herhangi bir bildirim göndermeden önce gerçek teslimleri toplamasına izin vermelidir.
- Teslim edilen onay kimliği türünü uçtan uca koruyun. Yerel istemciler, exec ile eklenti onay yönlendirmesini kanal yerel durumundan tahmin etmemeli veya yeniden yazmamalıdır.
- Farklı onay türleri kasıtlı olarak farklı yerel yüzeyler sunabilir.
  Mevcut paketlenmiş örnekler:
  - Slack, hem exec hem de eklenti kimlikleri için yerel onay yönlendirmesini kullanılabilir tutar.
  - Matrix, aynı yerel DM/kanal yönlendirmesini ve reaction UX'ini exec
    ve eklenti onayları için korurken auth'un onay türüne göre farklılaşmasına yine de izin verir.
- `createApproverRestrictedNativeApprovalAdapter` hâlâ bir uyumluluk sarmalayıcısı olarak vardır, ancak yeni kod capability oluşturucuyu tercih etmeli ve eklentide `approvalCapability` sunmalıdır.

Sıcak kanal giriş noktaları için, bu ailenin yalnızca bir parçasına ihtiyacınız
varsa daha dar runtime alt yollarını tercih edin:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-gateway-runtime`
- `openclaw/plugin-sdk/approval-handler-adapter-runtime`
- `openclaw/plugin-sdk/approval-handler-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`
- `openclaw/plugin-sdk/channel-runtime-context`

Benzer şekilde, daha geniş üst yüzeye ihtiyacınız olmadığında
`openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` ve
`openclaw/plugin-sdk/reply-chunking` yollarını tercih edin.

Özellikle kurulum için:

- `openclaw/plugin-sdk/setup-runtime`, runtime-safe kurulum yardımcılarını kapsar:
  import-safe kurulum yama bağdaştırıcıları (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), lookup-note çıktısı,
  `promptResolvedAllowFrom`, `splitSetupEntries` ve devredilen
  setup-proxy oluşturucular
- `openclaw/plugin-sdk/setup-adapter-runtime`, `createEnvPatchedAccountSetupAdapter` için dar, ortam farkında bağdaştırıcı bağlantı yüzeyidir
- `openclaw/plugin-sdk/channel-setup`, isteğe bağlı kurulum setup
  oluşturucularını ve setup-safe birkaç ilkel yapıyı kapsar:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

Kanalınız env odaklı kurulum veya auth destekliyorsa ve genel başlangıç/config
akışlarının çalışma zamanı yüklenmeden önce bu env adlarını bilmesi gerekiyorsa,
bunları eklenti manifestinde `channelEnvVars` ile bildirin. Kanal runtime `envVars`
veya yerel sabitlerini yalnızca operatöre dönük kopya için tutun.
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled` ve
`splitSetupEntries`

- yalnızca daha ağır ortak kurulum/config yardımcılarına da ihtiyacınız varsa daha geniş `openclaw/plugin-sdk/setup` bağlantı yüzeyini kullanın; örneğin
  `moveSingleAccountChannelSectionToDefaultAccount(...)`

Kanalınız yalnızca setup
yüzeylerinde "önce bu eklentiyi yükleyin" bilgisini göstermek istiyorsa,
`createOptionalChannelSetupSurface(...)` tercih edin. Oluşturulan
adapter/sihirbaz config yazımlarında ve sonlandırmada güvenli şekilde başarısız olur ve aynı yükleme-gerekli iletisini doğrulama, sonlandırma ve docs-link
metni boyunca yeniden kullanır.

Diğer sıcak kanal yolları için de, daha geniş eski
yüzeyler yerine dar yardımcıları tercih edin:

- çok hesaplı config ve
  varsayılan hesap fallback'i için `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` ve
  `openclaw/plugin-sdk/account-helpers`
- gelen rota/zarf ve
  record-and-dispatch bağlantısı için `openclaw/plugin-sdk/inbound-envelope` ve
  `openclaw/plugin-sdk/inbound-reply-dispatch`
- hedef ayrıştırma/eşleştirme için `openclaw/plugin-sdk/messaging-targets`
- medya yükleme ile giden
  kimlik/gönderim delegeleri için `openclaw/plugin-sdk/outbound-media` ve
  `openclaw/plugin-sdk/outbound-runtime`
- iş parçacığı bağı yaşam döngüsü
  ve bağdaştırıcı kaydı için `openclaw/plugin-sdk/thread-bindings-runtime`
- yalnızca eski bir agent/media
  payload alan düzeni hâlâ gerekliyse `openclaw/plugin-sdk/agent-media-payload`
- Telegram özel komut
  normalizasyonu, yinelenen/çakışma doğrulaması ve fallback açısından kararlı komut
  config sözleşmesi için `openclaw/plugin-sdk/telegram-command-config`

Yalnızca auth kullanan kanallar genellikle varsayılan yolda durabilir: çekirdek onayları yönetir ve eklenti yalnızca outbound/auth yeteneklerini sunar. Matrix, Slack, Telegram ve özel sohbet taşıma sistemleri gibi yerel onay kanalları kendi onay yaşam döngülerini yazmak yerine ortak yerel yardımcıları kullanmalıdır.

## Gelen mention politikası

Gelen mention işlemeyi iki katmana ayrılmış tutun:

- eklentiye ait kanıt toplama
- ortak politika değerlendirmesi

Ortak katman için `openclaw/plugin-sdk/channel-inbound` kullanın.

Eklentiye yerel mantık için iyi uyum sağlayan alanlar:

- bota yanıt algılama
- bottan alıntı algılama
- iş parçacığına katılım denetimleri
- hizmet/sistem mesajı hariç tutmaları
- bot katılımını kanıtlamak için gereken platform yerel önbellekler

Ortak yardımcı için iyi uyum sağlayan alanlar:

- `requireMention`
- açık mention sonucu
- örtük mention allowlist'i
- komut bypass'ı
- son atlama kararı

Tercih edilen akış:

1. Yerel mention bilgilerini hesaplayın.
2. Bu bilgileri `resolveInboundMentionDecision({ facts, policy })` içine geçirin.
3. Gelen kapıda `decision.effectiveWasMentioned`, `decision.shouldBypassMention` ve `decision.shouldSkip` kullanın.

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

`api.runtime.channel.mentions`, çalışma zamanı eklemeye zaten bağlı olan
paketlenmiş kanal eklentileri için aynı ortak mention yardımcılarını sunar:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

Eski `resolveMentionGating*` yardımcıları
`openclaw/plugin-sdk/channel-inbound` üzerinde yalnızca uyumluluk dışa aktarımları olarak kalır. Yeni kod
`resolveInboundMentionDecision({ facts, policy })` kullanmalıdır.

## Adım adım açıklama

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Paket ve manifest">
    Standart eklenti dosyalarını oluşturun. `package.json` içindeki `channel` alanı
    bunun bir kanal eklentisi olmasını sağlar. Tam paket meta veri yüzeyi için
    [Plugin Setup and Config](/tr/plugins/sdk-setup#openclawchannel) bölümüne bakın:

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

  <Step title="Kanal eklentisi nesnesini oluşturun">
    `ChannelPlugin` arayüzü birçok isteğe bağlı bağdaştırıcı yüzeyi içerir. Önce en küçük haliyle —
    `id` ve `setup` — başlayın ve ihtiyaç duydukça bağdaştırıcılar ekleyin.

    `src/channel.ts` oluşturun:

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

    <Accordion title="createChatChannelPlugin size sizin için ne yapar">
      Alt düzey bağdaştırıcı arayüzlerini elle uygulamak yerine,
      bildirimsel seçenekler verirsiniz ve oluşturucu bunları birleştirir:

      | Seçenek | Bağladığı şey |
      | --- | --- |
      | `security.dm` | Config alanlarından kapsamlı DM güvenlik çözümleyicisi |
      | `pairing.text` | Kod değişimiyle metin tabanlı DM eşleştirme akışı |
      | `threading` | Reply-to modu çözümleyicisi (sabit, hesap kapsamlı veya özel) |
      | `outbound.attachedResults` | Sonuç meta verisi döndüren gönderim işlevleri (mesaj kimlikleri) |

      Tam denetime ihtiyacınız varsa bildirimsel seçenekler yerine ham bağdaştırıcı nesneleri de verebilirsiniz.
    </Accordion>

  </Step>

  <Step title="Giriş noktasını bağlayın">
    `index.ts` oluşturun:

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

    Kanal sahipli CLI descriptor'larını `registerCliMetadata(...)` içine koyun; böylece OpenClaw
    tam kanal çalışma zamanını etkinleştirmeden bunları kök yardımda gösterebilir,
    normal tam yüklemeler ise gerçek komut
    kaydı için aynı descriptor'ları almaya devam eder. `registerFull(...)` değerini çalışma zamanına özgü işler için tutun.
    Eğer `registerFull(...)` gateway RPC yöntemleri kaydediyorsa, eklentiye
    özgü bir önek kullanın. Çekirdek yönetici ad alanları (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) ayrılmıştır ve her zaman
    `operator.admin` olarak çözülür.
    `defineChannelPluginEntry`, kayıt modu ayrımını otomatik olarak yönetir. Tüm
    seçenekler için [Entry Points](/tr/plugins/sdk-entrypoints#definechannelpluginentry) bölümüne bakın.

  </Step>

  <Step title="Bir setup girişi ekleyin">
    Onboarding sırasında hafif yükleme için `setup-entry.ts` oluşturun:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw, kanal devre dışı olduğunda
    veya yapılandırılmadığında tam giriş yerine bunu yükler.
    Kurulum akışları sırasında ağır çalışma zamanı kodunu çekmekten kaçınır.
    Ayrıntılar için [Setup and Config](/tr/plugins/sdk-setup#setup-entry) bölümüne bakın.

  </Step>

  <Step title="Gelen mesajları işleyin">
    Eklentinizin platformdan mesaj alması ve bunları
    OpenClaw'a iletmesi gerekir. Tipik desen, isteği doğrulayan ve
    bunu kanalınızın gelen işleyicisi üzerinden dağıtan bir webhook'tur:

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
      Gelen mesaj işleme kanala özgüdür. Her kanal eklentisi
      kendi gelen işlem hattına sahiptir. Gerçek kalıplar için paketlenmiş kanal eklentilerine
      (örneğin Microsoft Teams veya Google Chat eklenti paketine) bakın.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Test">
Eş konumlu testleri `src/channel.test.ts` içine yazın:

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

    Ortak test yardımcıları için [Testing](/tr/plugins/sdk-testing) bölümüne bakın.

  </Step>
</Steps>

## Dosya yapısı

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

## Gelişmiş konular

<CardGroup cols={2}>
  <Card title="İş parçacığı seçenekleri" icon="git-branch" href="/tr/plugins/sdk-entrypoints#registration-mode">
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
Bazı paketlenmiş yardımcı bağlantı yüzeyleri, paketlenmiş eklenti bakımı ve
uyumluluk için hâlâ vardır. Bunlar yeni kanal eklentileri için önerilen desen değildir;
o paketlenmiş eklenti ailesini doğrudan sürdürmüyorsanız ortak SDK
yüzeyinden genel channel/setup/reply/runtime alt yollarını tercih edin.
</Note>

## Sonraki adımlar

- [Provider Plugins](/tr/plugins/sdk-provider-plugins) — eklentiniz model de sağlıyorsa
- [SDK Overview](/tr/plugins/sdk-overview) — tam alt yol içe aktarma başvurusu
- [SDK Testing](/tr/plugins/sdk-testing) — test yardımcı programları ve sözleşme testleri
- [Plugin Manifest](/tr/plugins/manifest) — tam manifest şeması
