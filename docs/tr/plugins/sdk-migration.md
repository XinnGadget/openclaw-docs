---
read_when:
    - OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED uyarısını görüyorsunuz
    - OPENCLAW_EXTENSION_API_DEPRECATED uyarısını görüyorsunuz
    - Bir plugin'i modern plugin mimarisine güncelliyorsunuz
    - Harici bir OpenClaw plugin'inin bakımını yapıyorsunuz
sidebarTitle: Migrate to SDK
summary: Eski geriye dönük uyumluluk katmanından modern plugin SDK'ye geçiş yapın
title: Plugin SDK Geçişi
x-i18n:
    generated_at: "2026-04-08T02:17:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 155a8b14bc345319c8516ebdb8a0ccdea2c5f7fa07dad343442996daee21ecad
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin SDK Geçişi

OpenClaw, geniş bir geriye dönük uyumluluk katmanından, odaklı ve belgelenmiş
import'lara sahip modern bir plugin mimarisine geçti. Plugin'iniz yeni
mimariden önce oluşturulduysa, bu kılavuz geçiş yapmanıza yardımcı olur.

## Neler değişiyor

Eski plugin sistemi, plugin'lerin tek bir giriş noktasından ihtiyaç duydukları
her şeyi içe aktarmasına izin veren iki geniş açık yüzey sağlıyordu:

- **`openclaw/plugin-sdk/compat`** — onlarca yardımcıyı yeniden dışa aktaran
  tek bir import. Yeni plugin mimarisi oluşturulurken eski hook tabanlı
  plugin'lerin çalışmaya devam etmesi için sunuldu.
- **`openclaw/extension-api`** — plugin'lere gömülü agent runner gibi
  ana makine tarafı yardımcılarına doğrudan erişim veren bir köprü.

Bu iki yüzey artık **kullanımdan kaldırılmıştır**. Çalışma zamanında hâlâ
çalışırlar, ancak yeni plugin'ler bunları kullanmamalıdır ve mevcut plugin'ler
bir sonraki büyük sürüm bunları kaldırmadan önce geçiş yapmalıdır.

<Warning>
  Geriye dönük uyumluluk katmanı gelecekteki bir büyük sürümde kaldırılacaktır.
  Bu yüzeylerden hâlâ import yapan plugin'ler bu olduğunda bozulacaktır.
</Warning>

## Bunun nedeni nedir

Eski yaklaşım bazı sorunlara neden oluyordu:

- **Yavaş başlangıç** — tek bir yardımcıyı içe aktarmak onlarca ilgisiz modülü yüklüyordu
- **Döngüsel bağımlılıklar** — geniş yeniden dışa aktarmalar import döngüleri oluşturmayı kolaylaştırıyordu
- **Belirsiz API yüzeyi** — hangi dışa aktarımların kararlı, hangilerinin dahili olduğunu ayırt etmenin yolu yoktu

Modern plugin SDK bunu düzeltir: her import yolu (`openclaw/plugin-sdk/\<subpath\>`)
net bir amaca ve belgelenmiş bir sözleşmeye sahip, küçük ve kendi içinde yeterli
bir modüldür.

Paketlenmiş kanallar için eski sağlayıcı kolaylık yüzeyleri de kaldırıldı.
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
kanal markalı yardımcı yüzeyler ve
`openclaw/plugin-sdk/telegram-core` gibi import'lar özel mono-repo kısayollarıydı,
kararlı plugin sözleşmeleri değildi. Bunun yerine dar ve genel SDK alt yollarını kullanın. Paketlenmiş
plugin çalışma alanı içinde, sağlayıcıya ait yardımcıları ilgili plugin'in kendi
`api.ts` veya `runtime-api.ts` dosyasında tutun.

Geçerli paketlenmiş sağlayıcı örnekleri:

- Anthropic, Claude'a özgü akış yardımcılarını kendi `api.ts` /
  `contract-api.ts` yüzeyinde tutar
- OpenAI, sağlayıcı oluşturucularını, varsayılan model yardımcılarını ve realtime sağlayıcı
  oluşturucularını kendi `api.ts` dosyasında tutar
- OpenRouter, sağlayıcı oluşturucu ile onboarding/yapılandırma yardımcılarını kendi
  `api.ts` dosyasında tutar

## Nasıl geçiş yapılır

<Steps>
  <Step title="Yerel onay işleyicilerini capability facts'e taşıyın">
    Onay yetenekli kanal plugin'leri artık yerel onay davranışını
    `approvalCapability.nativeRuntime` ve paylaşılan runtime-context kayıt defteri aracılığıyla açığa çıkarır.

    Temel değişiklikler:

    - `approvalCapability.handler.loadRuntime(...)` yerine
      `approvalCapability.nativeRuntime` kullanın
    - Onaya özgü auth/delivery mantığını eski `plugin.auth` /
      `plugin.approvals` bağlantısından çıkarıp `approvalCapability` üzerine taşıyın
    - `ChannelPlugin.approvals`, genel channel-plugin
      sözleşmesinden kaldırıldı; delivery/native/render alanlarını `approvalCapability` üzerine taşıyın
    - `plugin.auth`, yalnızca kanal login/logout akışları için kalır; oradaki
      onay auth hook'ları artık core tarafından okunmaz
    - İstemciler, token'lar veya Bolt
      uygulamaları gibi kanala ait runtime nesnelerini `openclaw/plugin-sdk/channel-runtime-context`
      aracılığıyla kaydedin
    - Yerel onay işleyicilerinden plugin'e ait reroute bildirimleri göndermeyin;
      yönlendirilmiş-başka-yerde bildirimleri artık core gerçek delivery sonuçlarından sahiplenir
    - `channelRuntime` değerini `createChannelManager(...)` içine geçirirken,
      gerçek bir `createPluginRuntime().channel` yüzeyi sağlayın. Kısmi stub'lar reddedilir.

    Geçerli approval capability
    düzeni için `/plugins/sdk-channel-plugins` sayfasına bakın.

  </Step>

  <Step title="Windows wrapper geri dönüş davranışını denetleyin">
    Plugin'iniz `openclaw/plugin-sdk/windows-spawn` kullanıyorsa,
    çözümlenmemiş Windows `.cmd`/`.bat` wrapper'ları artık siz açıkça
    `allowShellFallback: true` vermediğiniz sürece kapalı hata verir.

    ```typescript
    // Önce
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Sonra
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Bunu yalnızca bilerek shell aracılı geri dönüşü kabul eden
      // güvenilir uyumluluk çağıranları için ayarlayın.
      allowShellFallback: true,
    });
    ```

    Çağıranınız bilerek shell fallback'e güvenmiyorsa `allowShellFallback`
    ayarlamayın ve bunun yerine fırlatılan hatayı işleyin.

  </Step>

  <Step title="Kullanımdan kaldırılmış import'ları bulun">
    Plugin'inizde bu kullanımdan kaldırılmış yüzeylerden yapılan import'ları arayın:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Bunları odaklı import'larla değiştirin">
    Eski yüzeydeki her dışa aktarma belirli bir modern import yoluna eşlenir:

    ```typescript
    // Önce (kullanımdan kaldırılmış geriye dönük uyumluluk katmanı)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Sonra (modern odaklı import'lar)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Ana makine tarafı yardımcıları için doğrudan import etmek yerine enjekte edilen
    plugin runtime'ını kullanın:

    ```typescript
    // Önce (kullanımdan kaldırılmış extension-api köprüsü)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Sonra (enjekte edilmiş runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Aynı desen diğer eski köprü yardımcıları için de geçerlidir:

    | Eski import | Modern karşılığı |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | oturum deposu yardımcıları | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Derleyin ve test edin">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## Import yolu başvurusu

<Accordion title="Yaygın import yolu tablosu">
  | Import path | Amaç | Temel dışa aktarımlar |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Kanonik plugin giriş yardımcısı | `definePluginEntry` |
  | `plugin-sdk/core` | Kanal giriş tanımları/oluşturucuları için eski şemsiye yeniden dışa aktarma | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Kök yapılandırma şeması dışa aktarımı | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Tek sağlayıcılı giriş yardımcısı | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Odaklı kanal giriş tanımları ve oluşturucuları | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Paylaşılan kurulum sihirbazı yardımcıları | Allowlist istemleri, kurulum durumu oluşturucuları |
  | `plugin-sdk/setup-runtime` | Kurulum zamanı runtime yardımcıları | Import-safe kurulum yama bağdaştırıcıları, lookup-note yardımcıları, `promptResolvedAllowFrom`, `splitSetupEntries`, devredilmiş kurulum proxy'leri |
  | `plugin-sdk/setup-adapter-runtime` | Kurulum bağdaştırıcı yardımcıları | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Kurulum araç yardımcıları | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Çoklu hesap yardımcıları | Hesap listesi/yapılandırma/eylem kapısı yardımcıları |
  | `plugin-sdk/account-id` | Hesap kimliği yardımcıları | `DEFAULT_ACCOUNT_ID`, hesap kimliği normalleştirme |
  | `plugin-sdk/account-resolution` | Hesap arama yardımcıları | Hesap arama + varsayılan geri dönüş yardımcıları |
  | `plugin-sdk/account-helpers` | Dar hesap yardımcıları | Hesap listesi/hesap eylemi yardımcıları |
  | `plugin-sdk/channel-setup` | Kurulum sihirbazı bağdaştırıcıları | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, ayrıca `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DM eşleştirme ilkel öğeleri | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Yanıt öneki + yazıyor bağlantısı | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Yapılandırma bağdaştırıcı fabrikaları | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Yapılandırma şeması oluşturucuları | Kanal yapılandırma şeması türleri |
  | `plugin-sdk/telegram-command-config` | Telegram komut yapılandırma yardımcıları | Komut adı normalleştirme, açıklama kırpma, yinelenen/çakışma doğrulaması |
  | `plugin-sdk/channel-policy` | Grup/DM ilke çözümleme | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Hesap durumu izleme | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Gelen zarf yardımcıları | Paylaşılan route + zarf oluşturucu yardımcıları |
  | `plugin-sdk/inbound-reply-dispatch` | Gelen yanıt yardımcıları | Paylaşılan record-and-dispatch yardımcıları |
  | `plugin-sdk/messaging-targets` | Mesajlaşma hedefi ayrıştırma | Hedef ayrıştırma/eşleştirme yardımcıları |
  | `plugin-sdk/outbound-media` | Giden medya yardımcıları | Paylaşılan giden medya yükleme |
  | `plugin-sdk/outbound-runtime` | Giden runtime yardımcıları | Giden kimlik/gönderme delege yardımcıları |
  | `plugin-sdk/thread-bindings-runtime` | Thread-binding yardımcıları | Thread-binding yaşam döngüsü ve bağdaştırıcı yardımcıları |
  | `plugin-sdk/agent-media-payload` | Eski medya payload yardımcıları | Eski alan düzenleri için agent medya payload oluşturucu |
  | `plugin-sdk/channel-runtime` | Kullanımdan kaldırılmış uyumluluk shim'i | Yalnızca eski kanal runtime yardımcıları |
  | `plugin-sdk/channel-send-result` | Gönderim sonucu türleri | Yanıt sonuç türleri |
  | `plugin-sdk/runtime-store` | Kalıcı plugin depolama | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Geniş runtime yardımcıları | Runtime/logging/backup/plugin-install yardımcıları |
  | `plugin-sdk/runtime-env` | Dar runtime env yardımcıları | Logger/runtime env, timeout, retry ve backoff yardımcıları |
  | `plugin-sdk/plugin-runtime` | Paylaşılan plugin runtime yardımcıları | Plugin komutları/hook'lar/http/interactive yardımcıları |
  | `plugin-sdk/hook-runtime` | Hook pipeline yardımcıları | Paylaşılan webhook/internal hook pipeline yardımcıları |
  | `plugin-sdk/lazy-runtime` | Lazy runtime yardımcıları | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Süreç yardımcıları | Paylaşılan exec yardımcıları |
  | `plugin-sdk/cli-runtime` | CLI runtime yardımcıları | Komut biçimlendirme, beklemeler, sürüm yardımcıları |
  | `plugin-sdk/gateway-runtime` | Gateway yardımcıları | Gateway istemcisi ve channel-status yama yardımcıları |
  | `plugin-sdk/config-runtime` | Yapılandırma yardımcıları | Yapılandırma yükleme/yazma yardımcıları |
  | `plugin-sdk/telegram-command-config` | Telegram komut yardımcıları | Paketlenmiş Telegram sözleşme yüzeyi kullanılamadığında geri dönüşte kararlı Telegram komut doğrulama yardımcıları |
  | `plugin-sdk/approval-runtime` | Onay istemi yardımcıları | Exec/plugin onay payload'ı, approval capability/profile yardımcıları, yerel onay yönlendirme/runtime yardımcıları |
  | `plugin-sdk/approval-auth-runtime` | Onay auth yardımcıları | Onaylayıcı çözümleme, aynı sohbette eylem auth |
  | `plugin-sdk/approval-client-runtime` | Onay istemci yardımcıları | Yerel exec onay profile/filter yardımcıları |
  | `plugin-sdk/approval-delivery-runtime` | Onay delivery yardımcıları | Yerel approval capability/delivery bağdaştırıcıları |
  | `plugin-sdk/approval-gateway-runtime` | Onay gateway yardımcıları | Paylaşılan onay gateway çözümleme yardımcısı |
  | `plugin-sdk/approval-handler-adapter-runtime` | Onay bağdaştırıcı yardımcıları | Sıcak kanal giriş noktaları için hafif yerel onay bağdaştırıcısı yükleme yardımcıları |
  | `plugin-sdk/approval-handler-runtime` | Onay işleyici yardımcıları | Daha geniş onay işleyici runtime yardımcıları; dar bağdaştırıcı/gateway yüzeyleri yeterliyse onları tercih edin |
  | `plugin-sdk/approval-native-runtime` | Onay hedef yardımcıları | Yerel onay hedefi/hesap bağlama yardımcıları |
  | `plugin-sdk/approval-reply-runtime` | Onay yanıt yardımcıları | Exec/plugin onay yanıt payload yardımcıları |
  | `plugin-sdk/channel-runtime-context` | Kanal runtime-context yardımcıları | Genel kanal runtime-context register/get/watch yardımcıları |
  | `plugin-sdk/security-runtime` | Güvenlik yardımcıları | Paylaşılan trust, DM gating, external-content ve secret-collection yardımcıları |
  | `plugin-sdk/ssrf-policy` | SSRF ilke yardımcıları | Ana makine izin listesi ve özel ağ ilke yardımcıları |
  | `plugin-sdk/ssrf-runtime` | SSRF runtime yardımcıları | Pinned-dispatcher, guarded fetch, SSRF ilke yardımcıları |
  | `plugin-sdk/collection-runtime` | Sınırlı önbellek yardımcıları | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Tanılama geçidi yardımcıları | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Hata biçimlendirme yardımcıları | `formatUncaughtError`, `isApprovalNotFoundError`, hata grafı yardımcıları |
  | `plugin-sdk/fetch-runtime` | Sarmalanmış fetch/proxy yardımcıları | `resolveFetch`, proxy yardımcıları |
  | `plugin-sdk/host-runtime` | Ana makine normalleştirme yardımcıları | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Retry yardımcıları | `RetryConfig`, `retryAsync`, ilke çalıştırıcıları |
  | `plugin-sdk/allow-from` | Allowlist biçimlendirme | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Allowlist girdi eşleme | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Komut geçidi ve komut yüzeyi yardımcıları | `resolveControlCommandGate`, gönderen-yetkilendirme yardımcıları, komut kayıt defteri yardımcıları |
  | `plugin-sdk/secret-input` | Secret girdi ayrıştırma | Secret girdi yardımcıları |
  | `plugin-sdk/webhook-ingress` | Webhook istek yardımcıları | Webhook hedef yardımcıları |
  | `plugin-sdk/webhook-request-guards` | Webhook gövde koruma yardımcıları | İstek gövdesi okuma/sınır yardımcıları |
  | `plugin-sdk/reply-runtime` | Paylaşılan yanıt runtime'ı | Gelen dispatch, heartbeat, yanıt planlayıcı, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Dar yanıt dispatch yardımcıları | Finalize + provider dispatch yardımcıları |
  | `plugin-sdk/reply-history` | Yanıt geçmişi yardımcıları | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Yanıt başvurusu planlama | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Yanıt parça yardımcıları | Metin/markdown chunking yardımcıları |
  | `plugin-sdk/session-store-runtime` | Oturum deposu yardımcıları | Depo yolu + updated-at yardımcıları |
  | `plugin-sdk/state-paths` | Durum yolu yardımcıları | Durum ve OAuth dizini yardımcıları |
  | `plugin-sdk/routing` | Routing/session-key yardımcıları | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, session-key normalleştirme yardımcıları |
  | `plugin-sdk/status-helpers` | Kanal durum yardımcıları | Kanal/hesap durum özeti oluşturucuları, runtime-state varsayılanları, issue meta veri yardımcıları |
  | `plugin-sdk/target-resolver-runtime` | Hedef çözücü yardımcıları | Paylaşılan hedef çözücü yardımcıları |
  | `plugin-sdk/string-normalization-runtime` | Dize normalleştirme yardımcıları | Slug/dize normalleştirme yardımcıları |
  | `plugin-sdk/request-url` | İstek URL yardımcıları | Request benzeri girdilerden dize URL'leri çıkarma |
  | `plugin-sdk/run-command` | Zamanlanmış komut yardımcıları | Normalize stdout/stderr ile zamanlanmış komut çalıştırıcı |
  | `plugin-sdk/param-readers` | Param okuyucular | Yaygın araç/CLI param okuyucuları |
  | `plugin-sdk/tool-send` | Tool send çıkarımı | Araç argümanlarından kanonik gönderim hedefi alanlarını çıkarma |
  | `plugin-sdk/temp-path` | Geçici yol yardımcıları | Paylaşılan temp-download yol yardımcıları |
  | `plugin-sdk/logging-core` | Logging yardımcıları | Alt sistem logger ve redaction yardımcıları |
  | `plugin-sdk/markdown-table-runtime` | Markdown-table yardımcıları | Markdown tablo modu yardımcıları |
  | `plugin-sdk/reply-payload` | Mesaj yanıt türleri | Yanıt payload türleri |
  | `plugin-sdk/provider-setup` | Özenle seçilmiş yerel/self-hosted sağlayıcı kurulum yardımcıları | Self-hosted sağlayıcı keşif/yapılandırma yardımcıları |
  | `plugin-sdk/self-hosted-provider-setup` | Odaklı OpenAI-compatible self-hosted sağlayıcı kurulum yardımcıları | Aynı self-hosted sağlayıcı keşif/yapılandırma yardımcıları |
  | `plugin-sdk/provider-auth-runtime` | Sağlayıcı runtime auth yardımcıları | Runtime API anahtarı çözümleme yardımcıları |
  | `plugin-sdk/provider-auth-api-key` | Sağlayıcı API anahtarı kurulum yardımcıları | API anahtarı onboarding/profile-write yardımcıları |
  | `plugin-sdk/provider-auth-result` | Sağlayıcı auth-result yardımcıları | Standart OAuth auth-result oluşturucu |
  | `plugin-sdk/provider-auth-login` | Sağlayıcı etkileşimli login yardımcıları | Paylaşılan etkileşimli login yardımcıları |
  | `plugin-sdk/provider-env-vars` | Sağlayıcı env-var yardımcıları | Sağlayıcı auth env-var arama yardımcıları |
  | `plugin-sdk/provider-model-shared` | Paylaşılan sağlayıcı model/replay yardımcıları | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, paylaşılan replay-policy oluşturucuları, provider-endpoint yardımcıları ve model-id normalleştirme yardımcıları |
  | `plugin-sdk/provider-catalog-shared` | Paylaşılan sağlayıcı katalog yardımcıları | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Sağlayıcı onboarding yamaları | Onboarding yapılandırma yardımcıları |
  | `plugin-sdk/provider-http` | Sağlayıcı HTTP yardımcıları | Genel sağlayıcı HTTP/endpoint capability yardımcıları |
  | `plugin-sdk/provider-web-fetch` | Sağlayıcı web-fetch yardımcıları | Web-fetch sağlayıcı kayıt/önbellek yardımcıları |
  | `plugin-sdk/provider-web-search-contract` | Sağlayıcı web-search sözleşme yardımcıları | `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` ve kapsamlı kimlik bilgisi ayarlayıcıları/alıcıları gibi dar web-search yapılandırma/kimlik bilgisi sözleşme yardımcıları |
  | `plugin-sdk/provider-web-search` | Sağlayıcı web-search yardımcıları | Web-search sağlayıcı kayıt/önbellek/runtime yardımcıları |
  | `plugin-sdk/provider-tools` | Sağlayıcı araç/şema uyumluluk yardımcıları | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini şema temizliği + tanılama ve `resolveXaiModelCompatPatch` / `applyXaiModelCompat` gibi xAI uyumluluk yardımcıları |
  | `plugin-sdk/provider-usage` | Sağlayıcı kullanım yardımcıları | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` ve diğer sağlayıcı kullanım yardımcıları |
  | `plugin-sdk/provider-stream` | Sağlayıcı akış sarmalayıcı yardımcıları | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, akış sarmalayıcı türleri ve paylaşılan Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot sarmalayıcı yardımcıları |
  | `plugin-sdk/keyed-async-queue` | Sıralı async kuyruk | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Paylaşılan medya yardımcıları | Medya fetch/transform/store yardımcıları artı medya payload oluşturucuları |
  | `plugin-sdk/media-generation-runtime` | Paylaşılan media-generation yardımcıları | Görüntü/video/müzik üretimi için paylaşılan failover yardımcıları, aday seçimi ve eksik model mesajlaşması |
  | `plugin-sdk/media-understanding` | Media-understanding yardımcıları | Media understanding sağlayıcı türleri artı sağlayıcıya dönük görüntü/ses yardımcı dışa aktarımları |
  | `plugin-sdk/text-runtime` | Paylaşılan metin yardımcıları | Assistanta görünür metin temizleme, markdown render/chunking/table yardımcıları, redaction yardımcıları, directive-tag yardımcıları, safe-text yardımcıları ve ilgili metin/logging yardımcıları |
  | `plugin-sdk/text-chunking` | Metin parça yardımcıları | Giden metin chunking yardımcısı |
  | `plugin-sdk/speech` | Konuşma yardımcıları | Konuşma sağlayıcı türleri artı sağlayıcıya dönük directive, registry ve doğrulama yardımcıları |
  | `plugin-sdk/speech-core` | Paylaşılan konuşma çekirdeği | Konuşma sağlayıcı türleri, registry, directive'ler, normalleştirme |
  | `plugin-sdk/realtime-transcription` | Realtime transcription yardımcıları | Sağlayıcı türleri ve registry yardımcıları |
  | `plugin-sdk/realtime-voice` | Realtime voice yardımcıları | Sağlayıcı türleri ve registry yardımcıları |
  | `plugin-sdk/image-generation-core` | Paylaşılan image-generation çekirdeği | Image-generation türleri, failover, auth ve registry yardımcıları |
  | `plugin-sdk/music-generation` | Music-generation yardımcıları | Music-generation sağlayıcı/istek/sonuç türleri |
  | `plugin-sdk/music-generation-core` | Paylaşılan music-generation çekirdeği | Music-generation türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
  | `plugin-sdk/video-generation` | Video-generation yardımcıları | Video-generation sağlayıcı/istek/sonuç türleri |
  | `plugin-sdk/video-generation-core` | Paylaşılan video-generation çekirdeği | Video-generation türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
  | `plugin-sdk/interactive-runtime` | Etkileşimli yanıt yardımcıları | Etkileşimli yanıt payload normalleştirme/indirgeme |
  | `plugin-sdk/channel-config-primitives` | Kanal yapılandırma ilkel öğeleri | Dar kanal config-schema ilkel öğeleri |
  | `plugin-sdk/channel-config-writes` | Kanal config-write yardımcıları | Kanal config-write yetkilendirme yardımcıları |
  | `plugin-sdk/channel-plugin-common` | Paylaşılan kanal başlangıç bölümü | Paylaşılan kanal plugin başlangıç dışa aktarımları |
  | `plugin-sdk/channel-status` | Kanal durum yardımcıları | Paylaşılan kanal durum anlık görüntüsü/özet yardımcıları |
  | `plugin-sdk/allowlist-config-edit` | Allowlist yapılandırma yardımcıları | Allowlist yapılandırma düzenleme/okuma yardımcıları |
  | `plugin-sdk/group-access` | Grup erişim yardımcıları | Paylaşılan grup erişim kararı yardımcıları |
  | `plugin-sdk/direct-dm` | Doğrudan-DM yardımcıları | Paylaşılan doğrudan-DM auth/guard yardımcıları |
  | `plugin-sdk/extension-shared` | Paylaşılan extension yardımcıları | Passive-channel/status ve ambient proxy yardımcı ilkel öğeleri |
  | `plugin-sdk/webhook-targets` | Webhook hedef yardımcıları | Webhook hedef kayıt defteri ve route-install yardımcıları |
  | `plugin-sdk/webhook-path` | Webhook yol yardımcıları | Webhook yol normalleştirme yardımcıları |
  | `plugin-sdk/web-media` | Paylaşılan web medya yardımcıları | Uzak/yerel medya yükleme yardımcıları |
  | `plugin-sdk/zod` | Zod yeniden dışa aktarma | Plugin SDK kullanıcıları için yeniden dışa aktarılan `zod` |
  | `plugin-sdk/memory-core` | Paketlenmiş memory-core yardımcıları | Memory manager/config/file/CLI yardımcı yüzeyi |
  | `plugin-sdk/memory-core-engine-runtime` | Memory engine runtime cephesi | Memory index/search runtime cephesi |
  | `plugin-sdk/memory-core-host-engine-foundation` | Memory host foundation engine | Memory host foundation engine dışa aktarımları |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Memory host embedding engine | Memory host embedding engine dışa aktarımları |
  | `plugin-sdk/memory-core-host-engine-qmd` | Memory host QMD engine | Memory host QMD engine dışa aktarımları |
  | `plugin-sdk/memory-core-host-engine-storage` | Memory host storage engine | Memory host storage engine dışa aktarımları |
  | `plugin-sdk/memory-core-host-multimodal` | Memory host multimodal yardımcıları | Memory host multimodal yardımcıları |
  | `plugin-sdk/memory-core-host-query` | Memory host query yardımcıları | Memory host query yardımcıları |
  | `plugin-sdk/memory-core-host-secret` | Memory host secret yardımcıları | Memory host secret yardımcıları |
  | `plugin-sdk/memory-core-host-events` | Memory host event journal yardımcıları | Memory host event journal yardımcıları |
  | `plugin-sdk/memory-core-host-status` | Memory host status yardımcıları | Memory host status yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-cli` | Memory host CLI runtime | Memory host CLI runtime yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-core` | Memory host core runtime | Memory host core runtime yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-files` | Memory host file/runtime yardımcıları | Memory host file/runtime yardımcıları |
  | `plugin-sdk/memory-host-core` | Memory host core runtime takma adı | Memory host core runtime yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-host-events` | Memory host event journal takma adı | Memory host event journal yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-host-files` | Memory host file/runtime takma adı | Memory host file/runtime yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-host-markdown` | Yönetilen markdown yardımcıları | Memory'ye bitişik plugin'ler için paylaşılan managed-markdown yardımcıları |
  | `plugin-sdk/memory-host-search` | Etkin memory search cephesi | Lazy active-memory search-manager runtime cephesi |
  | `plugin-sdk/memory-host-status` | Memory host status takma adı | Memory host status yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-lancedb` | Paketlenmiş memory-lancedb yardımcıları | Memory-lancedb yardımcı yüzeyi |
  | `plugin-sdk/testing` | Test yardımcı araçları | Test yardımcıları ve mock'lar |
</Accordion>

Bu tablo, tüm SDK yüzeyi değil, bilinçli olarak yaygın geçiş alt kümesidir.
200'den fazla entrypoint'in tam listesi
`scripts/lib/plugin-sdk-entrypoints.json` içinde bulunur.

Bu liste hâlâ bazı paketlenmiş-plugin yardımcı yüzeylerini içerir; örneğin
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` ve `plugin-sdk/matrix*`. Bunlar paketlenmiş-plugin
bakımı ve uyumluluk için dışa aktarılmaya devam eder, ancak bilinçli olarak
yaygın geçiş tablosuna dahil edilmemiştir ve
yeni plugin kodu için önerilen hedef değildir.

Aynı kural şu diğer paketlenmiş yardımcı aileleri için de geçerlidir:

- tarayıcı desteği yardımcıları: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- paketlenmiş yardımcı/plugin yüzeyleri, örneğin `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` ve `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` şu anda dar token-helper
yüzeyi `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` ve `resolveCopilotApiToken` değerlerini açığa çıkarır.

Yapılan işe uyan en dar import'u kullanın. Bir dışa aktarım bulamazsanız
`src/plugin-sdk/` içindeki kaynağı inceleyin veya Discord'da sorun.

## Kaldırma zaman çizelgesi

| Ne zaman | Ne olur |
| ---------------------- | ----------------------------------------------------------------------- |
| **Şimdi** | Kullanımdan kaldırılmış yüzeyler çalışma zamanında uyarı verir |
| **Bir sonraki büyük sürüm** | Kullanımdan kaldırılmış yüzeyler kaldırılır; bunları hâlâ kullanan plugin'ler başarısız olur |

Tüm core plugin'ler zaten taşındı. Harici plugin'ler
bir sonraki büyük sürümden önce geçiş yapmalıdır.

## Uyarıları geçici olarak bastırma

Geçiş üzerinde çalışırken bu ortam değişkenlerini ayarlayın:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Bu geçici bir kaçış kapağıdır, kalıcı bir çözüm değildir.

## İlgili

- [Başlangıç](/tr/plugins/building-plugins) — ilk plugin'inizi oluşturun
- [SDK Genel Bakış](/tr/plugins/sdk-overview) — alt yollar için tam import başvurusu
- [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins) — kanal plugin'leri oluşturma
- [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins) — sağlayıcı plugin'leri oluşturma
- [Plugin İç Yapısı](/tr/plugins/architecture) — mimariyi derinlemesine inceleme
- [Plugin Manifest'i](/tr/plugins/manifest) — manifest şeması başvurusu
