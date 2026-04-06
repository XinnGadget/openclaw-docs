---
read_when:
    - '`OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED` uyarısını görüyorsunuz'
    - '`OPENCLAW_EXTENSION_API_DEPRECATED` uyarısını görüyorsunuz'
    - Bir plugin'i modern plugin mimarisine güncelliyorsunuz
    - Harici bir OpenClaw plugin'inin bakımını yapıyorsunuz
sidebarTitle: Migrate to SDK
summary: Eski geri uyumluluk katmanından modern plugin SDK'sına geçiş yapın
title: Plugin SDK Geçişi
x-i18n:
    generated_at: "2026-04-06T03:10:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: b71ce69b30c3bb02da1b263b1d11dc3214deae5f6fc708515e23b5a1c7bb7c8f
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin SDK Geçişi

OpenClaw, geniş bir geri uyumluluk katmanından odaklı, belgelenmiş içe aktarmalara sahip modern bir plugin
mimarisine geçti. Plugin'iniz yeni mimariden önce
geliştirildiyse, bu kılavuz geçiş yapmanıza yardımcı olur.

## Neler değişiyor

Eski plugin sistemi, plugin'lerin tek bir giriş noktasından
ihtiyaç duydukları her şeyi içe aktarmasına izin veren iki geniş yüzey sağlıyordu:

- **`openclaw/plugin-sdk/compat`** — onlarca
  yardımcıyı yeniden dışa aktaran tek bir içe aktarma. Yeni plugin mimarisi inşa edilirken eski hook tabanlı plugin'lerin çalışmaya devam etmesi için tanıtıldı.
- **`openclaw/extension-api`** — plugin'lere
  gömülü agent çalıştırıcısı gibi host tarafı yardımcılarına doğrudan erişim veren bir köprü.

Her iki yüzey de artık **kullanım dışı**. Çalışma zamanında hâlâ çalışırlar, ancak yeni
plugin'ler bunları kullanmamalıdır ve mevcut plugin'ler bunlar sonraki büyük sürümde kaldırılmadan önce geçiş yapmalıdır.

<Warning>
  Geri uyumluluk katmanı gelecekteki bir büyük sürümde kaldırılacaktır.
  Hâlâ bu yüzeylerden içe aktarma yapan plugin'ler bu gerçekleştiğinde bozulacaktır.
</Warning>

## Bunun nedeni neydi

Eski yaklaşım sorunlara yol açıyordu:

- **Yavaş başlangıç** — tek bir yardımcıyı içe aktarmak onlarca ilgisiz modülü yüklüyordu
- **Döngüsel bağımlılıklar** — geniş yeniden dışa aktarmalar içe aktarma döngüleri oluşturmayı kolaylaştırıyordu
- **Belirsiz API yüzeyi** — hangi dışa aktarmaların kararlı, hangilerinin dahili olduğunu anlamanın bir yolu yoktu

Modern plugin SDK bunu düzeltir: her içe aktarma yolu (`openclaw/plugin-sdk/\<subpath\>`)
küçük, kendi kendine yeten, açık amaçlı ve belgelenmiş sözleşmeye sahip bir modüldür.

Paketlenmiş kanallar için eski sağlayıcı kolaylık arayüzleri de kaldırıldı. 
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
kanal markalı yardımcı arayüzleri ve
`openclaw/plugin-sdk/telegram-core` gibi içe aktarmalar, kararlı plugin sözleşmeleri değil,
özel mono-repo kısayollarıydı. Bunun yerine dar, genel SDK alt yollarını kullanın. Paketlenmiş
plugin çalışma alanı içinde, sağlayıcıya ait yardımcıları o plugin'in kendi
`api.ts` veya `runtime-api.ts` dosyasında tutun.

Geçerli paketlenmiş sağlayıcı örnekleri:

- Anthropic, Claude'a özgü akış yardımcılarını kendi `api.ts` /
  `contract-api.ts` arayüzünde tutar
- OpenAI, sağlayıcı oluşturucuları, varsayılan model yardımcılarını ve gerçek zamanlı sağlayıcı
  oluşturucularını kendi `api.ts` dosyasında tutar
- OpenRouter, sağlayıcı oluşturucuyu ve onboarding/yapılandırma yardımcılarını kendi
  `api.ts` dosyasında tutar

## Nasıl geçiş yapılır

<Steps>
  <Step title="Windows sarmalayıcı geri dönüş davranışını denetleyin">
    Plugin'iniz `openclaw/plugin-sdk/windows-spawn` kullanıyorsa, çözümlenmemiş Windows
    `.cmd`/`.bat` sarmalayıcıları artık açıkça
    `allowShellFallback: true` geçmediğiniz sürece kapalı şekilde başarısız olur.

    ```typescript
    // Önce
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Sonra
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Bunu yalnızca kabuk aracılı geri dönüşü kasıtlı olarak
      // kabul eden güvenilir uyumluluk çağıranları için ayarlayın.
      allowShellFallback: true,
    });
    ```

    Çağıranınız kabuk geri dönüşüne kasıtlı olarak dayanmıyorsa,
    `allowShellFallback` ayarlamayın ve bunun yerine fırlatılan hatayı ele alın.

  </Step>

  <Step title="Kullanım dışı içe aktarmaları bulun">
    Plugin'inizde kullanım dışı yüzeylerden biri üzerinden yapılan içe aktarmaları arayın:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Bunları odaklı içe aktarmalarla değiştirin">
    Eski yüzeydeki her dışa aktarma, belirli bir modern içe aktarma yoluna karşılık gelir:

    ```typescript
    // Önce (kullanım dışı geri uyumluluk katmanı)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Sonra (modern odaklı içe aktarmalar)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Host tarafı yardımcıları için doğrudan içe aktarma yapmak yerine
    enjekte edilen plugin çalışma zamanını kullanın:

    ```typescript
    // Önce (kullanım dışı extension-api köprüsü)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Sonra (enjekte edilen çalışma zamanı)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Aynı kalıp diğer eski köprü yardımcıları için de geçerlidir:

    | Eski içe aktarma | Modern karşılığı |
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

## İçe aktarma yolu başvurusu

<Accordion title="Yaygın içe aktarma yolu tablosu">
  | İçe aktarma yolu | Amaç | Temel dışa aktarmalar |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Kanonik plugin giriş yardımcısı | `definePluginEntry` |
  | `plugin-sdk/core` | Kanal giriş tanımları/oluşturucuları için eski şemsiye yeniden dışa aktarma | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Kök yapılandırma şeması dışa aktarımı | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Tek sağlayıcılı giriş yardımcısı | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Odaklı kanal giriş tanımları ve oluşturucuları | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Paylaşılan kurulum sihirbazı yardımcıları | Allowlist istemleri, kurulum durumu oluşturucuları |
  | `plugin-sdk/setup-runtime` | Kurulum zamanı çalışma zamanı yardımcıları | İçe aktarma açısından güvenli kurulum yama bağdaştırıcıları, lookup-note yardımcıları, `promptResolvedAllowFrom`, `splitSetupEntries`, devredilmiş kurulum proxy'leri |
  | `plugin-sdk/setup-adapter-runtime` | Kurulum bağdaştırıcı yardımcıları | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Kurulum araç yardımcıları | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Çok hesaplı yardımcılar | Hesap listesi/yapılandırma/eylem geçidi yardımcıları |
  | `plugin-sdk/account-id` | Hesap kimliği yardımcıları | `DEFAULT_ACCOUNT_ID`, hesap kimliği normalleştirme |
  | `plugin-sdk/account-resolution` | Hesap arama yardımcıları | Hesap arama + varsayılan geri dönüş yardımcıları |
  | `plugin-sdk/account-helpers` | Dar hesap yardımcıları | Hesap listesi/hesap eylemi yardımcıları |
  | `plugin-sdk/channel-setup` | Kurulum sihirbazı bağdaştırıcıları | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, ayrıca `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DM eşleme ilkelleri | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Yanıt öneki + yazıyor durumu bağlantısı | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Yapılandırma bağdaştırıcı fabrikaları | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Yapılandırma şeması oluşturucuları | Kanal yapılandırma şeması türleri |
  | `plugin-sdk/telegram-command-config` | Telegram komut yapılandırma yardımcıları | Komut adı normalleştirme, açıklama kırpma, yinelenen/çakışma doğrulaması |
  | `plugin-sdk/channel-policy` | Grup/DM ilke çözümleme | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Hesap durumu izleme | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Gelen zarf yardımcıları | Paylaşılan rota + zarf oluşturucu yardımcıları |
  | `plugin-sdk/inbound-reply-dispatch` | Gelen yanıt yardımcıları | Paylaşılan kaydet ve dağıt yardımcıları |
  | `plugin-sdk/messaging-targets` | Mesajlaşma hedefi ayrıştırma | Hedef ayrıştırma/eşleştirme yardımcıları |
  | `plugin-sdk/outbound-media` | Giden medya yardımcıları | Paylaşılan giden medya yükleme |
  | `plugin-sdk/outbound-runtime` | Giden çalışma zamanı yardımcıları | Giden kimlik/gönderme temsilci yardımcıları |
  | `plugin-sdk/thread-bindings-runtime` | İş parçacığı bağlama yardımcıları | İş parçacığı bağlama yaşam döngüsü ve bağdaştırıcı yardımcıları |
  | `plugin-sdk/agent-media-payload` | Eski medya payload yardımcıları | Eski alan düzenleri için agent medya payload oluşturucu |
  | `plugin-sdk/channel-runtime` | Kullanım dışı uyumluluk shim'i | Yalnızca eski kanal çalışma zamanı yardımcıları |
  | `plugin-sdk/channel-send-result` | Gönderim sonucu türleri | Yanıt sonucu türleri |
  | `plugin-sdk/runtime-store` | Kalıcı plugin depolaması | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Geniş çalışma zamanı yardımcıları | Çalışma zamanı/günlükleme/yedekleme/plugin kurulum yardımcıları |
  | `plugin-sdk/runtime-env` | Dar çalışma zamanı ortam yardımcıları | Logger/çalışma zamanı ortamı, zaman aşımı, yeniden deneme ve backoff yardımcıları |
  | `plugin-sdk/plugin-runtime` | Paylaşılan plugin çalışma zamanı yardımcıları | Plugin komutları/hook'lar/http/etkileşimli yardımcılar |
  | `plugin-sdk/hook-runtime` | Hook ardışık düzen yardımcıları | Paylaşılan webhook/dahili hook ardışık düzen yardımcıları |
  | `plugin-sdk/lazy-runtime` | Tembel çalışma zamanı yardımcıları | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Süreç yardımcıları | Paylaşılan exec yardımcıları |
  | `plugin-sdk/cli-runtime` | CLI çalışma zamanı yardımcıları | Komut biçimlendirme, beklemeler, sürüm yardımcıları |
  | `plugin-sdk/gateway-runtime` | Gateway yardımcıları | Gateway istemcisi ve channel-status yama yardımcıları |
  | `plugin-sdk/config-runtime` | Yapılandırma yardımcıları | Yapılandırma yükleme/yazma yardımcıları |
  | `plugin-sdk/telegram-command-config` | Telegram komut yardımcıları | Paketlenmiş Telegram sözleşme yüzeyi kullanılamadığında geri dönüş açısından kararlı Telegram komut doğrulama yardımcıları |
  | `plugin-sdk/approval-runtime` | Onay istemi yardımcıları | Exec/plugin onay payload, onay yeteneği/profil yardımcıları, yerel onay yönlendirme/çalışma zamanı yardımcıları |
  | `plugin-sdk/approval-auth-runtime` | Onay kimlik doğrulama yardımcıları | Onaylayıcı çözümleme, aynı sohbet eylem kimlik doğrulaması |
  | `plugin-sdk/approval-client-runtime` | Onay istemci yardımcıları | Yerel exec onay profili/filtre yardımcıları |
  | `plugin-sdk/approval-delivery-runtime` | Onay teslim yardımcıları | Yerel onay yeteneği/teslim bağdaştırıcıları |
  | `plugin-sdk/approval-native-runtime` | Onay hedef yardımcıları | Yerel onay hedefi/hesap bağlama yardımcıları |
  | `plugin-sdk/approval-reply-runtime` | Onay yanıt yardımcıları | Exec/plugin onay yanıt payload yardımcıları |
  | `plugin-sdk/security-runtime` | Güvenlik yardımcıları | Paylaşılan güven, DM geçitleme, harici içerik ve gizli bilgi toplama yardımcıları |
  | `plugin-sdk/ssrf-policy` | SSRF ilke yardımcıları | Host allowlist ve özel ağ ilke yardımcıları |
  | `plugin-sdk/ssrf-runtime` | SSRF çalışma zamanı yardımcıları | Sabitlenmiş dağıtıcı, korumalı fetch, SSRF ilke yardımcıları |
  | `plugin-sdk/collection-runtime` | Sınırlandırılmış önbellek yardımcıları | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Tanılama geçitleme yardımcıları | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Hata biçimlendirme yardımcıları | `formatUncaughtError`, `isApprovalNotFoundError`, hata grafiği yardımcıları |
  | `plugin-sdk/fetch-runtime` | Sarmalanmış fetch/proxy yardımcıları | `resolveFetch`, proxy yardımcıları |
  | `plugin-sdk/host-runtime` | Host normalleştirme yardımcıları | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Yeniden deneme yardımcıları | `RetryConfig`, `retryAsync`, ilke çalıştırıcıları |
  | `plugin-sdk/allow-from` | Allowlist biçimlendirme | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Allowlist girdi eşleme | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Komut geçitleme ve komut yüzeyi yardımcıları | `resolveControlCommandGate`, gönderen yetkilendirme yardımcıları, komut kayıt yardımcıları |
  | `plugin-sdk/secret-input` | Gizli girdi ayrıştırma | Gizli girdi yardımcıları |
  | `plugin-sdk/webhook-ingress` | Webhook istek yardımcıları | Webhook hedef yardımcı programları |
  | `plugin-sdk/webhook-request-guards` | Webhook gövde koruma yardımcıları | İstek gövdesi okuma/sınır yardımcıları |
  | `plugin-sdk/reply-runtime` | Paylaşılan yanıt çalışma zamanı | Gelen dağıtım, heartbeat, yanıt planlayıcı, parçalara ayırma |
  | `plugin-sdk/reply-dispatch-runtime` | Dar yanıt dağıtım yardımcıları | Sonlandırma + sağlayıcı dağıtım yardımcıları |
  | `plugin-sdk/reply-history` | Yanıt geçmişi yardımcıları | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Yanıt referans planlama | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Yanıt parça yardımcıları | Metin/markdown parçalara ayırma yardımcıları |
  | `plugin-sdk/session-store-runtime` | Oturum deposu yardımcıları | Depo yolu + updated-at yardımcıları |
  | `plugin-sdk/state-paths` | Durum yolu yardımcıları | Durum ve OAuth dizin yardımcıları |
  | `plugin-sdk/routing` | Yönlendirme/oturum anahtarı yardımcıları | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, oturum anahtarı normalleştirme yardımcıları |
  | `plugin-sdk/status-helpers` | Kanal durum yardımcıları | Kanal/hesap durum özeti oluşturucuları, çalışma zamanı durumu varsayılanları, sorun meta verisi yardımcıları |
  | `plugin-sdk/target-resolver-runtime` | Hedef çözümleyici yardımcıları | Paylaşılan hedef çözümleyici yardımcıları |
  | `plugin-sdk/string-normalization-runtime` | Dize normalleştirme yardımcıları | Slug/dize normalleştirme yardımcıları |
  | `plugin-sdk/request-url` | İstek URL yardımcıları | İstek benzeri girdilerden dize URL çıkarma |
  | `plugin-sdk/run-command` | Zamanlamalı komut yardımcıları | Normalize edilmiş stdout/stderr ile zamanlamalı komut çalıştırıcı |
  | `plugin-sdk/param-readers` | Parametre okuyucuları | Yaygın araç/CLI parametre okuyucuları |
  | `plugin-sdk/tool-send` | Araç gönderim çıkarımı | Araç argümanlarından kanonik gönderim hedef alanlarını çıkar |
  | `plugin-sdk/temp-path` | Geçici yol yardımcıları | Paylaşılan geçici indirme yolu yardımcıları |
  | `plugin-sdk/logging-core` | Günlükleme yardımcıları | Alt sistem logger ve redaksiyon yardımcıları |
  | `plugin-sdk/markdown-table-runtime` | Markdown tablo yardımcıları | Markdown tablo modu yardımcıları |
  | `plugin-sdk/reply-payload` | Mesaj yanıt türleri | Yanıt payload türleri |
  | `plugin-sdk/provider-setup` | Düzenlenmiş yerel/self-hosted sağlayıcı kurulum yardımcıları | Self-hosted sağlayıcı keşif/yapılandırma yardımcıları |
  | `plugin-sdk/self-hosted-provider-setup` | Odaklı OpenAI uyumlu self-hosted sağlayıcı kurulum yardımcıları | Aynı self-hosted sağlayıcı keşif/yapılandırma yardımcıları |
  | `plugin-sdk/provider-auth-runtime` | Sağlayıcı çalışma zamanı kimlik doğrulama yardımcıları | Çalışma zamanı API anahtarı çözümleme yardımcıları |
  | `plugin-sdk/provider-auth-api-key` | Sağlayıcı API anahtarı kurulum yardımcıları | API anahtarı onboarding/profil yazma yardımcıları |
  | `plugin-sdk/provider-auth-result` | Sağlayıcı auth-result yardımcıları | Standart OAuth auth-result oluşturucu |
  | `plugin-sdk/provider-auth-login` | Sağlayıcı etkileşimli oturum açma yardımcıları | Paylaşılan etkileşimli oturum açma yardımcıları |
  | `plugin-sdk/provider-env-vars` | Sağlayıcı ortam değişkeni yardımcıları | Sağlayıcı kimlik doğrulama ortam değişkeni arama yardımcıları |
  | `plugin-sdk/provider-model-shared` | Paylaşılan sağlayıcı model/yeniden oynatma yardımcıları | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, paylaşılan replay-policy oluşturucuları, sağlayıcı uç nokta yardımcıları ve model kimliği normalleştirme yardımcıları |
  | `plugin-sdk/provider-catalog-shared` | Paylaşılan sağlayıcı katalog yardımcıları | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Sağlayıcı onboarding yamaları | Onboarding yapılandırma yardımcıları |
  | `plugin-sdk/provider-http` | Sağlayıcı HTTP yardımcıları | Genel sağlayıcı HTTP/uç nokta yetenek yardımcıları |
  | `plugin-sdk/provider-web-fetch` | Sağlayıcı web-fetch yardımcıları | Web-fetch sağlayıcı kaydı/önbellek yardımcıları |
  | `plugin-sdk/provider-web-search` | Sağlayıcı web-search yardımcıları | Web-search sağlayıcı kaydı/önbellek/yapılandırma yardımcıları |
  | `plugin-sdk/provider-tools` | Sağlayıcı araç/şema uyumluluk yardımcıları | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini şema temizleme + tanılama ve `resolveXaiModelCompatPatch` / `applyXaiModelCompat` gibi xAI uyumluluk yardımcıları |
  | `plugin-sdk/provider-usage` | Sağlayıcı kullanım yardımcıları | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` ve diğer sağlayıcı kullanım yardımcıları |
  | `plugin-sdk/provider-stream` | Sağlayıcı akış sarmalayıcı yardımcıları | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, akış sarmalayıcı türleri ve paylaşılan Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot sarmalayıcı yardımcıları |
  | `plugin-sdk/keyed-async-queue` | Sıralı async kuyruğu | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Paylaşılan medya yardımcıları | Medya fetch/dönüştürme/depolama yardımcıları ve medya payload oluşturucuları |
  | `plugin-sdk/media-understanding` | Medya anlama yardımcıları | Medya anlama sağlayıcı türleri ve sağlayıcıya dönük görsel/ses yardımcı dışa aktarmaları |
  | `plugin-sdk/text-runtime` | Paylaşılan metin yardımcıları | Assistant görünür metin temizleme, markdown işleme/parçalama/tablo yardımcıları, redaksiyon yardımcıları, directive-tag yardımcıları, safe-text yardımcıları ve ilgili metin/günlükleme yardımcıları |
  | `plugin-sdk/text-chunking` | Metin parçalara ayırma yardımcıları | Giden metin parçalara ayırma yardımcısı |
  | `plugin-sdk/speech` | Konuşma yardımcıları | Konuşma sağlayıcı türleri ve sağlayıcıya dönük directive, registry ve doğrulama yardımcıları |
  | `plugin-sdk/speech-core` | Paylaşılan konuşma çekirdeği | Konuşma sağlayıcı türleri, registry, directives, normalleştirme |
  | `plugin-sdk/realtime-transcription` | Gerçek zamanlı transkripsiyon yardımcıları | Sağlayıcı türleri ve registry yardımcıları |
  | `plugin-sdk/realtime-voice` | Gerçek zamanlı ses yardımcıları | Sağlayıcı türleri ve registry yardımcıları |
  | `plugin-sdk/image-generation-core` | Paylaşılan görsel oluşturma çekirdeği | Görsel oluşturma türleri, failover, kimlik doğrulama ve registry yardımcıları |
  | `plugin-sdk/music-generation` | Müzik oluşturma yardımcıları | Müzik oluşturma sağlayıcı/istek/sonuç türleri |
  | `plugin-sdk/music-generation-core` | Paylaşılan müzik oluşturma çekirdeği | Müzik oluşturma türleri, failover yardımcıları, sağlayıcı arama ve model başvurusu ayrıştırma |
  | `plugin-sdk/video-generation` | Video oluşturma yardımcıları | Video oluşturma sağlayıcı/istek/sonuç türleri |
  | `plugin-sdk/video-generation-core` | Paylaşılan video oluşturma çekirdeği | Video oluşturma türleri, failover yardımcıları, sağlayıcı arama ve model başvurusu ayrıştırma |
  | `plugin-sdk/interactive-runtime` | Etkileşimli yanıt yardımcıları | Etkileşimli yanıt payload normalleştirme/azaltma |
  | `plugin-sdk/channel-config-primitives` | Kanal yapılandırma ilkelleri | Dar kanal config-schema ilkelleri |
  | `plugin-sdk/channel-config-writes` | Kanal yapılandırma yazma yardımcıları | Kanal yapılandırma yazma yetkilendirme yardımcıları |
  | `plugin-sdk/channel-plugin-common` | Paylaşılan kanal başlangıç bölümü | Paylaşılan kanal plugin başlangıç bölümü dışa aktarmaları |
  | `plugin-sdk/channel-status` | Kanal durum yardımcıları | Paylaşılan kanal durum anlık görüntüsü/özeti yardımcıları |
  | `plugin-sdk/allowlist-config-edit` | Allowlist yapılandırma yardımcıları | Allowlist yapılandırma düzenleme/okuma yardımcıları |
  | `plugin-sdk/group-access` | Grup erişimi yardımcıları | Paylaşılan grup erişimi karar yardımcıları |
  | `plugin-sdk/direct-dm` | Doğrudan DM yardımcıları | Paylaşılan doğrudan DM kimlik doğrulama/koruma yardımcıları |
  | `plugin-sdk/extension-shared` | Paylaşılan extension yardımcıları | Pasif kanal/durum yardımcı ilkelileri |
  | `plugin-sdk/webhook-targets` | Webhook hedef yardımcıları | Webhook hedef registry ve rota kurulum yardımcıları |
  | `plugin-sdk/webhook-path` | Webhook yol yardımcıları | Webhook yol normalleştirme yardımcıları |
  | `plugin-sdk/web-media` | Paylaşılan web medya yardımcıları | Uzak/yerel medya yükleme yardımcıları |
  | `plugin-sdk/zod` | Zod yeniden dışa aktarımı | Plugin SDK tüketicileri için yeniden dışa aktarılan `zod` |
  | `plugin-sdk/memory-core` | Paketlenmiş memory-core yardımcıları | Bellek yöneticisi/yapılandırma/dosya/CLI yardımcı yüzeyi |
  | `plugin-sdk/memory-core-engine-runtime` | Bellek motoru çalışma zamanı cephesi | Bellek dizin/aroma çalışma zamanı cephesi |
  | `plugin-sdk/memory-core-host-engine-foundation` | Bellek host foundation motoru | Bellek host foundation motoru dışa aktarmaları |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Bellek host embedding motoru | Bellek host embedding motoru dışa aktarmaları |
  | `plugin-sdk/memory-core-host-engine-qmd` | Bellek host QMD motoru | Bellek host QMD motoru dışa aktarmaları |
  | `plugin-sdk/memory-core-host-engine-storage` | Bellek host depolama motoru | Bellek host depolama motoru dışa aktarmaları |
  | `plugin-sdk/memory-core-host-multimodal` | Bellek host çok modlu yardımcıları | Bellek host çok modlu yardımcıları |
  | `plugin-sdk/memory-core-host-query` | Bellek host sorgu yardımcıları | Bellek host sorgu yardımcıları |
  | `plugin-sdk/memory-core-host-secret` | Bellek host gizli bilgi yardımcıları | Bellek host gizli bilgi yardımcıları |
  | `plugin-sdk/memory-core-host-status` | Bellek host durum yardımcıları | Bellek host durum yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-cli` | Bellek host CLI çalışma zamanı | Bellek host CLI çalışma zamanı yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-core` | Bellek host çekirdek çalışma zamanı | Bellek host çekirdek çalışma zamanı yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-files` | Bellek host dosya/çalışma zamanı yardımcıları | Bellek host dosya/çalışma zamanı yardımcıları |
  | `plugin-sdk/memory-lancedb` | Paketlenmiş memory-lancedb yardımcıları | Memory-lancedb yardımcı yüzeyi |
  | `plugin-sdk/testing` | Test yardımcı programları | Test yardımcıları ve mock'lar |
</Accordion>

Bu tablo kasıtlı olarak tam SDK
yüzeyi değil, yaygın geçiş alt kümesidir. 200+'den fazla giriş noktasının tam listesi
`scripts/lib/plugin-sdk-entrypoints.json` içinde bulunur.

Bu liste hâlâ
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` ve `plugin-sdk/matrix*` gibi bazı paketlenmiş plugin yardımcı arayüzlerini içerir. Bunlar paketlenmiş plugin bakımı ve uyumluluğu için dışa aktarılmaya devam eder, ancak kasıtlı olarak
yaygın geçiş tablosunda yer almazlar ve yeni plugin kodu için önerilen hedef değildirler.

Aynı kural aşağıdaki gibi diğer paketlenmiş yardımcı aileleri için de geçerlidir:

- browser destek yardımcıları: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` ve `plugin-sdk/voice-call` gibi paketlenmiş yardımcı/plugin yüzeyleri

`plugin-sdk/github-copilot-token` şu anda dar belirteç yardımcı
yüzeyi olan `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` ve `resolveCopilotApiToken` öğelerini dışa aktarır.

İşle en iyi eşleşen en dar içe aktarmayı kullanın. Bir dışa aktarma bulamazsanız,
`src/plugin-sdk/` içindeki kaynağı kontrol edin veya Discord'da sorun.

## Kaldırma zaman çizelgesi

| Ne zaman | Ne olur |
| ---------------------- | ----------------------------------------------------------------------- |
| **Şimdi** | Kullanım dışı yüzeyler çalışma zamanında uyarı verir |
| **Sonraki büyük sürüm** | Kullanım dışı yüzeyler kaldırılır; bunları hâlâ kullanan plugin'ler başarısız olur |

Tüm çekirdek plugin'ler zaten geçirilmiştir. Harici plugin'ler
sonraki büyük sürümden önce geçiş yapmalıdır.

## Uyarıları geçici olarak bastırma

Geçiş üzerinde çalışırken şu ortam değişkenlerini ayarlayın:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Bu geçici bir kaçış kapağıdır, kalıcı bir çözüm değildir.

## İlgili

- [Başlangıç](/tr/plugins/building-plugins) — ilk plugin'inizi geliştirin
- [SDK Overview](/tr/plugins/sdk-overview) — tam alt yol içe aktarma başvurusu
- [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins) — kanal plugin'leri geliştirme
- [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins) — sağlayıcı plugin'leri geliştirme
- [Plugin İç Yapısı](/tr/plugins/architecture) — mimariye derin bakış
- [Plugin Manifest](/tr/plugins/manifest) — manifest şeması başvurusu
