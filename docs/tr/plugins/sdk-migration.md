---
read_when:
    - '`OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED` uyarısını görüyorsunuz'
    - '`OPENCLAW_EXTENSION_API_DEPRECATED` uyarısını görüyorsunuz'
    - Bir plugin'i modern plugin mimarisine güncelliyorsunuz
    - Harici bir OpenClaw plugin'inin bakımını yapıyorsunuz
sidebarTitle: Migrate to SDK
summary: Eski geriye dönük uyumluluk katmanından modern plugin SDK'ya geçin
title: Plugin SDK Geçişi
x-i18n:
    generated_at: "2026-04-07T08:48:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3691060e9dc00ca8bee49240a047f0479398691bd14fb96e9204cc9243fdb32c
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin SDK Geçişi

OpenClaw, geniş bir geriye dönük uyumluluk katmanından odaklı, belgelenmiş içe aktarmalara sahip modern bir plugin
mimarisine geçti. Plugin'iniz yeni mimariden önce oluşturulduysa,
bu kılavuz geçiş yapmanıza yardımcı olur.

## Neler değişiyor

Eski plugin sistemi, plugin'lerin tek bir giriş noktasından ihtiyaç duydukları
her şeyi içe aktarmasına izin veren iki geniş yüzey sağlıyordu:

- **`openclaw/plugin-sdk/compat`** — onlarca
  yardımcıyı yeniden dışa aktaran tek bir içe aktarma. Yeni plugin mimarisi
  oluşturulurken eski hook tabanlı plugin'leri çalışır durumda tutmak için sunuldu.
- **`openclaw/extension-api`** — plugin'lere
  gömülü ajan çalıştırıcısı gibi host tarafı yardımcılarına doğrudan erişim veren bir köprü.

Her iki yüzey de artık **kullanımdan kaldırılmıştır**. Çalışma zamanında hâlâ
çalışırlar, ancak yeni plugin'ler bunları kullanmamalıdır ve mevcut plugin'ler
sonraki büyük sürüm bunları kaldırmadan önce geçiş yapmalıdır.

<Warning>
  Geriye dönük uyumluluk katmanı gelecekteki bir büyük sürümde kaldırılacaktır.
  Hâlâ bu yüzeylerden içe aktarma yapan plugin'ler bu olduğunda bozulacaktır.
</Warning>

## Bu neden değişti

Eski yaklaşım sorunlara yol açıyordu:

- **Yavaş başlangıç** — tek bir yardımcıyı içe aktarmak onlarca alakasız modülü yüklüyordu
- **Döngüsel bağımlılıklar** — geniş yeniden dışa aktarmalar içe aktarma döngüleri oluşturmayı kolaylaştırıyordu
- **Belirsiz API yüzeyi** — hangi dışa aktarmaların kararlı, hangilerinin dahili olduğunu anlamanın bir yolu yoktu

Modern plugin SDK bunu düzeltir: her içe aktarma yolu (`openclaw/plugin-sdk/\<subpath\>`)
açık bir amaca ve belgelenmiş sözleşmeye sahip küçük, kendi kendine yeterli bir modüldür.

Paketle gelen kanallar için eski sağlayıcı kolaylık yüzeyleri de artık yok.
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
kanal markalı yardımcı yüzeyler ve
`openclaw/plugin-sdk/telegram-core` gibi içe aktarmalar kararlı
plugin sözleşmeleri değil, özel mono-repo kısayollarıydı. Bunun yerine dar, genel SDK alt yollarını kullanın. Paketle gelen
plugin çalışma alanında, sağlayıcıya ait yardımcıları o plugin'in kendi
`api.ts` veya `runtime-api.ts` dosyasında tutun.

Güncel paketle gelen sağlayıcı örnekleri:

- Anthropic, Claude'a özgü akış yardımcılarını kendi `api.ts` /
  `contract-api.ts` yüzeyinde tutar
- OpenAI, sağlayıcı oluşturucuları, varsayılan model yardımcılarını ve gerçek zamanlı sağlayıcı
  oluşturucularını kendi `api.ts` dosyasında tutar
- OpenRouter, sağlayıcı oluşturucu ve onboarding/yapılandırma yardımcılarını kendi
  `api.ts` dosyasında tutar

## Nasıl geçiş yapılır

<Steps>
  <Step title="Windows sarmalayıcı yedek davranışını denetleyin">
    Plugin'iniz `openclaw/plugin-sdk/windows-spawn` kullanıyorsa, çözümlenmeyen Windows
    `.cmd`/`.bat` sarmalayıcıları artık açıkça `allowShellFallback: true`
    geçmediğiniz sürece kapalı başarısız olur.

    ```typescript
    // Önce
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Sonra
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Bunu yalnızca shell aracılı yedeği bilerek kabul eden güvenilir
      // uyumluluk çağıranları için ayarlayın.
      allowShellFallback: true,
    });
    ```

    Çağıranınız bilerek shell yedeğine dayanmıyorsa,
    `allowShellFallback` ayarlamayın ve bunun yerine fırlatılan hatayı ele alın.

  </Step>

  <Step title="Kullanımdan kaldırılmış içe aktarmaları bulun">
    Plugin'inizde, kullanımdan kaldırılmış iki yüzeyden herhangi birinden yapılan içe aktarmaları arayın:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Odaklı içe aktarmalarla değiştirin">
    Eski yüzeydeki her dışa aktarma, belirli bir modern içe aktarma yoluna eşlenir:

    ```typescript
    // Önce (kullanımdan kaldırılmış geriye dönük uyumluluk katmanı)
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

    Host tarafı yardımcıları için, doğrudan içe aktarmak yerine
    enjekte edilmiş plugin çalışma zamanını kullanın:

    ```typescript
    // Önce (kullanımdan kaldırılmış extension-api köprüsü)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Sonra (enjekte edilmiş çalışma zamanı)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Aynı desen diğer eski köprü yardımcıları için de geçerlidir:

    | Old import | Modern equivalent |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | session store helpers | `api.runtime.agent.session.*` |

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
  | Import path | Purpose | Key exports |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Kanonik plugin giriş yardımcısı | `definePluginEntry` |
  | `plugin-sdk/core` | Kanal giriş tanımları/oluşturucuları için eski şemsiye yeniden dışa aktarma | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Kök yapılandırma şeması dışa aktarması | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Tek sağlayıcı giriş yardımcısı | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Odaklı kanal giriş tanımları ve oluşturucuları | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Paylaşılan kurulum sihirbazı yardımcıları | Allowlist istemleri, kurulum durumu oluşturucuları |
  | `plugin-sdk/setup-runtime` | Kurulum zamanı çalışma zamanı yardımcıları | İçe aktarma açısından güvenli kurulum yama adaptörleri, lookup-note yardımcıları, `promptResolvedAllowFrom`, `splitSetupEntries`, devredilmiş kurulum proxy'leri |
  | `plugin-sdk/setup-adapter-runtime` | Kurulum adaptörü yardımcıları | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Kurulum araçlama yardımcıları | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Çok hesaplı yardımcılar | Hesap listeleme/yapılandırma/eylem geçidi yardımcıları |
  | `plugin-sdk/account-id` | Hesap kimliği yardımcıları | `DEFAULT_ACCOUNT_ID`, hesap kimliği normalleştirme |
  | `plugin-sdk/account-resolution` | Hesap arama yardımcıları | Hesap arama + varsayılan yedek yardımcıları |
  | `plugin-sdk/account-helpers` | Dar hesap yardımcıları | Hesap listesi/hesap eylemi yardımcıları |
  | `plugin-sdk/channel-setup` | Kurulum sihirbazı adaptörleri | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, ayrıca `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DM eşleştirme ilkelleri | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Yanıt öneki + typing kablolaması | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Yapılandırma adaptörü fabrikaları | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Yapılandırma şeması oluşturucuları | Kanal yapılandırma şeması türleri |
  | `plugin-sdk/telegram-command-config` | Telegram komut yapılandırma yardımcıları | Komut adı normalleştirme, açıklama kırpma, yinelenen/çakışma doğrulaması |
  | `plugin-sdk/channel-policy` | Grup/DM ilke çözümleme | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Hesap durum takibi | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Gelen zarf yardımcıları | Paylaşılan rota + zarf oluşturucu yardımcıları |
  | `plugin-sdk/inbound-reply-dispatch` | Gelen yanıt yardımcıları | Paylaşılan kaydetme ve dağıtma yardımcıları |
  | `plugin-sdk/messaging-targets` | Mesajlaşma hedefi ayrıştırma | Hedef ayrıştırma/eşleştirme yardımcıları |
  | `plugin-sdk/outbound-media` | Giden medya yardımcıları | Paylaşılan giden medya yükleme |
  | `plugin-sdk/outbound-runtime` | Giden çalışma zamanı yardımcıları | Giden kimlik/gönderim yetki devri yardımcıları |
  | `plugin-sdk/thread-bindings-runtime` | İş parçacığı bağlama yardımcıları | İş parçacığı bağlama yaşam döngüsü ve adaptör yardımcıları |
  | `plugin-sdk/agent-media-payload` | Eski medya yükü yardımcıları | Eski alan düzenleri için ajan medya yükü oluşturucusu |
  | `plugin-sdk/channel-runtime` | Kullanımdan kaldırılmış uyumluluk shim'i | Yalnızca eski kanal çalışma zamanı yardımcıları |
  | `plugin-sdk/channel-send-result` | Gönderim sonuç türleri | Yanıt sonuç türleri |
  | `plugin-sdk/runtime-store` | Kalıcı plugin depolaması | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Geniş çalışma zamanı yardımcıları | Çalışma zamanı/loglama/yedekleme/plugin-kurulum yardımcıları |
  | `plugin-sdk/runtime-env` | Dar çalışma zamanı env yardımcıları | Logger/çalışma zamanı env, zaman aşımı, yeniden deneme ve geri çekilme yardımcıları |
  | `plugin-sdk/plugin-runtime` | Paylaşılan plugin çalışma zamanı yardımcıları | Plugin komutları/hook'lar/http/etkileşimli yardımcılar |
  | `plugin-sdk/hook-runtime` | Hook işlem hattı yardımcıları | Paylaşılan webhook/dahili hook işlem hattı yardımcıları |
  | `plugin-sdk/lazy-runtime` | Tembel çalışma zamanı yardımcıları | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Süreç yardımcıları | Paylaşılan exec yardımcıları |
  | `plugin-sdk/cli-runtime` | CLI çalışma zamanı yardımcıları | Komut biçimlendirme, beklemeler, sürüm yardımcıları |
  | `plugin-sdk/gateway-runtime` | Gateway yardımcıları | Gateway istemcisi ve kanal durumu yama yardımcıları |
  | `plugin-sdk/config-runtime` | Yapılandırma yardımcıları | Yapılandırma yükleme/yazma yardımcıları |
  | `plugin-sdk/telegram-command-config` | Telegram komut yardımcıları | Paketle gelen Telegram sözleşme yüzeyi kullanılamadığında yedek açısından kararlı Telegram komut doğrulama yardımcıları |
  | `plugin-sdk/approval-runtime` | Onay istemi yardımcıları | Exec/plugin onay yükü, onay yeteneği/profil yardımcıları, yerel onay yönlendirme/çalışma zamanı yardımcıları |
  | `plugin-sdk/approval-auth-runtime` | Onay auth yardımcıları | Onaylayan çözümleme, aynı sohbet eylemi auth |
  | `plugin-sdk/approval-client-runtime` | Onay istemci yardımcıları | Yerel exec onay profili/filtre yardımcıları |
  | `plugin-sdk/approval-delivery-runtime` | Onay teslim yardımcıları | Yerel onay yeteneği/teslim adaptörleri |
  | `plugin-sdk/approval-native-runtime` | Onay hedef yardımcıları | Yerel onay hedefi/hesap bağlama yardımcıları |
  | `plugin-sdk/approval-reply-runtime` | Onay yanıt yardımcıları | Exec/plugin onay yanıt yükü yardımcıları |
  | `plugin-sdk/security-runtime` | Güvenlik yardımcıları | Paylaşılan güven, DM geçidi, harici içerik ve secret toplama yardımcıları |
  | `plugin-sdk/ssrf-policy` | SSRF ilke yardımcıları | Host allowlist ve özel ağ ilkesi yardımcıları |
  | `plugin-sdk/ssrf-runtime` | SSRF çalışma zamanı yardımcıları | Sabitlenmiş dispatcher, korumalı fetch, SSRF ilke yardımcıları |
  | `plugin-sdk/collection-runtime` | Sınırlı önbellek yardımcıları | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Tanılama geçidi yardımcıları | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Hata biçimlendirme yardımcıları | `formatUncaughtError`, `isApprovalNotFoundError`, hata grafiği yardımcıları |
  | `plugin-sdk/fetch-runtime` | Sarılmış fetch/proxy yardımcıları | `resolveFetch`, proxy yardımcıları |
  | `plugin-sdk/host-runtime` | Host normalleştirme yardımcıları | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Yeniden deneme yardımcıları | `RetryConfig`, `retryAsync`, ilke çalıştırıcıları |
  | `plugin-sdk/allow-from` | Allowlist biçimlendirme | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Allowlist girdi eşleme | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Komut geçidi ve komut yüzeyi yardımcıları | `resolveControlCommandGate`, gönderen yetkilendirme yardımcıları, komut kayıt yardımcıları |
  | `plugin-sdk/secret-input` | Secret girdi ayrıştırma | Secret girdi yardımcıları |
  | `plugin-sdk/webhook-ingress` | Webhook istek yardımcıları | Webhook hedef yardımcı programları |
  | `plugin-sdk/webhook-request-guards` | Webhook gövde koruma yardımcıları | İstek gövdesi okuma/sınır yardımcıları |
  | `plugin-sdk/reply-runtime` | Paylaşılan yanıt çalışma zamanı | Gelen dağıtım, heartbeat, yanıt planlayıcı, parçalama |
  | `plugin-sdk/reply-dispatch-runtime` | Dar yanıt dağıtım yardımcıları | Tamamlama + sağlayıcı dağıtım yardımcıları |
  | `plugin-sdk/reply-history` | Yanıt geçmişi yardımcıları | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Yanıt referansı planlama | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Yanıt parça yardımcıları | Metin/markdown parçalama yardımcıları |
  | `plugin-sdk/session-store-runtime` | Oturum deposu yardımcıları | Depo yolu + updated-at yardımcıları |
  | `plugin-sdk/state-paths` | Durum yolu yardımcıları | Durum ve OAuth dizin yardımcıları |
  | `plugin-sdk/routing` | Yönlendirme/oturum anahtarı yardımcıları | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, oturum anahtarı normalleştirme yardımcıları |
  | `plugin-sdk/status-helpers` | Kanal durum yardımcıları | Kanal/hesap durum özeti oluşturucuları, çalışma zamanı durumu varsayılanları, sorun üst verisi yardımcıları |
  | `plugin-sdk/target-resolver-runtime` | Hedef çözümleyici yardımcıları | Paylaşılan hedef çözümleyici yardımcıları |
  | `plugin-sdk/string-normalization-runtime` | Dizge normalleştirme yardımcıları | Slug/dizge normalleştirme yardımcıları |
  | `plugin-sdk/request-url` | İstek URL yardımcıları | İstek benzeri girdilerden dizge URL'leri çıkarma |
  | `plugin-sdk/run-command` | Zamanlanmış komut yardımcıları | Normalleştirilmiş stdout/stderr ile zamanlanmış komut çalıştırıcısı |
  | `plugin-sdk/param-readers` | Param okuyucular | Yaygın tool/CLI param okuyucuları |
  | `plugin-sdk/tool-send` | Tool gönderim çıkarımı | Tool argümanlarından kanonik gönderim hedefi alanlarını çıkarma |
  | `plugin-sdk/temp-path` | Geçici yol yardımcıları | Paylaşılan geçici indirme yolu yardımcıları |
  | `plugin-sdk/logging-core` | Loglama yardımcıları | Alt sistem logger ve redaction yardımcıları |
  | `plugin-sdk/markdown-table-runtime` | Markdown tablo yardımcıları | Markdown tablo modu yardımcıları |
  | `plugin-sdk/reply-payload` | Mesaj yanıt türleri | Yanıt yükü türleri |
  | `plugin-sdk/provider-setup` | Düzenlenmiş yerel/self-hosted sağlayıcı kurulum yardımcıları | Self-hosted sağlayıcı keşif/yapılandırma yardımcıları |
  | `plugin-sdk/self-hosted-provider-setup` | Odaklı OpenAI uyumlu self-hosted sağlayıcı kurulum yardımcıları | Aynı self-hosted sağlayıcı keşif/yapılandırma yardımcıları |
  | `plugin-sdk/provider-auth-runtime` | Sağlayıcı çalışma zamanı auth yardımcıları | Çalışma zamanı API anahtarı çözümleme yardımcıları |
  | `plugin-sdk/provider-auth-api-key` | Sağlayıcı API anahtarı kurulum yardımcıları | API anahtarı onboarding/profil yazma yardımcıları |
  | `plugin-sdk/provider-auth-result` | Sağlayıcı auth sonucu yardımcıları | Standart OAuth auth-sonucu oluşturucusu |
  | `plugin-sdk/provider-auth-login` | Sağlayıcı etkileşimli oturum açma yardımcıları | Paylaşılan etkileşimli oturum açma yardımcıları |
  | `plugin-sdk/provider-env-vars` | Sağlayıcı env değişkeni yardımcıları | Sağlayıcı auth env değişkeni arama yardımcıları |
  | `plugin-sdk/provider-model-shared` | Paylaşılan sağlayıcı model/tekrar oynatma yardımcıları | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, paylaşılan replay-policy oluşturucuları, sağlayıcı uç nokta yardımcıları ve model kimliği normalleştirme yardımcıları |
  | `plugin-sdk/provider-catalog-shared` | Paylaşılan sağlayıcı katalog yardımcıları | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Sağlayıcı onboarding yamaları | Onboarding yapılandırma yardımcıları |
  | `plugin-sdk/provider-http` | Sağlayıcı HTTP yardımcıları | Genel sağlayıcı HTTP/uç nokta yetenek yardımcıları |
  | `plugin-sdk/provider-web-fetch` | Sağlayıcı web-fetch yardımcıları | Web-fetch sağlayıcı kayıt/önbellek yardımcıları |
  | `plugin-sdk/provider-web-search-contract` | Sağlayıcı web-search sözleşme yardımcıları | `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` ve kapsamlı kimlik bilgisi ayarlayıcı/alıcıları gibi dar web-search yapılandırma/kimlik bilgisi sözleşme yardımcıları |
  | `plugin-sdk/provider-web-search` | Sağlayıcı web-search yardımcıları | Web-search sağlayıcı kayıt/önbellek/çalışma zamanı yardımcıları |
  | `plugin-sdk/provider-tools` | Sağlayıcı tool/şema uyumluluk yardımcıları | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini şema temizliği + tanılama ve `resolveXaiModelCompatPatch` / `applyXaiModelCompat` gibi xAI uyumluluk yardımcıları |
  | `plugin-sdk/provider-usage` | Sağlayıcı kullanım yardımcıları | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` ve diğer sağlayıcı kullanım yardımcıları |
  | `plugin-sdk/provider-stream` | Sağlayıcı akış sarmalayıcı yardımcıları | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, akış sarmalayıcı türleri ve paylaşılan Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot sarmalayıcı yardımcıları |
  | `plugin-sdk/keyed-async-queue` | Sıralı async kuyruk | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Paylaşılan medya yardımcıları | Medya fetch/dönüştürme/depolama yardımcıları ve medya yükü oluşturucuları |
  | `plugin-sdk/media-generation-runtime` | Paylaşılan medya üretimi yardımcıları | Görsel/video/müzik üretimi için paylaşılan yedekleme yardımcıları, aday seçimi ve eksik model mesajlaşması |
  | `plugin-sdk/media-understanding` | Media-understanding yardımcıları | Medya anlama sağlayıcı türleri ve sağlayıcıya dönük görsel/ses yardımcı dışa aktarmaları |
  | `plugin-sdk/text-runtime` | Paylaşılan metin yardımcıları | Asistan tarafından görülebilen metin çıkarma, markdown işleme/parçalama/tablo yardımcıları, redaction yardımcıları, directive-tag yardımcıları, güvenli metin yardımcı programları ve ilgili metin/loglama yardımcıları |
  | `plugin-sdk/text-chunking` | Metin parçalama yardımcıları | Giden metin parçalama yardımcısı |
  | `plugin-sdk/speech` | Speech yardımcıları | Speech sağlayıcı türleri ve sağlayıcıya dönük directive, kayıt ve doğrulama yardımcıları |
  | `plugin-sdk/speech-core` | Paylaşılan speech çekirdeği | Speech sağlayıcı türleri, kayıt, direktifler, normalleştirme |
  | `plugin-sdk/realtime-transcription` | Gerçek zamanlı transkripsiyon yardımcıları | Sağlayıcı türleri ve kayıt yardımcıları |
  | `plugin-sdk/realtime-voice` | Gerçek zamanlı ses yardımcıları | Sağlayıcı türleri ve kayıt yardımcıları |
  | `plugin-sdk/image-generation-core` | Paylaşılan görsel üretimi çekirdeği | Görsel üretimi türleri, yedekleme, auth ve kayıt yardımcıları |
  | `plugin-sdk/music-generation` | Müzik üretimi yardımcıları | Müzik üretimi sağlayıcı/istek/sonuç türleri |
  | `plugin-sdk/music-generation-core` | Paylaşılan müzik üretimi çekirdeği | Müzik üretimi türleri, yedekleme yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
  | `plugin-sdk/video-generation` | Video üretimi yardımcıları | Video üretimi sağlayıcı/istek/sonuç türleri |
  | `plugin-sdk/video-generation-core` | Paylaşılan video üretimi çekirdeği | Video üretimi türleri, yedekleme yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
  | `plugin-sdk/interactive-runtime` | Etkileşimli yanıt yardımcıları | Etkileşimli yanıt yükü normalleştirme/indirgeme |
  | `plugin-sdk/channel-config-primitives` | Kanal yapılandırma ilkelleri | Dar kanal config-schema ilkelleri |
  | `plugin-sdk/channel-config-writes` | Kanal yapılandırma yazma yardımcıları | Kanal yapılandırma yazma yetkilendirme yardımcıları |
  | `plugin-sdk/channel-plugin-common` | Paylaşılan kanal başlangıcı | Paylaşılan kanal plugin prelude dışa aktarmaları |
  | `plugin-sdk/channel-status` | Kanal durum yardımcıları | Paylaşılan kanal durum anlık görüntüsü/özet yardımcıları |
  | `plugin-sdk/allowlist-config-edit` | Allowlist yapılandırma yardımcıları | Allowlist yapılandırma düzenleme/okuma yardımcıları |
  | `plugin-sdk/group-access` | Grup erişim yardımcıları | Paylaşılan grup erişim kararı yardımcıları |
  | `plugin-sdk/direct-dm` | Doğrudan DM yardımcıları | Paylaşılan doğrudan DM auth/koruma yardımcıları |
  | `plugin-sdk/extension-shared` | Paylaşılan uzantı yardımcıları | Pasif kanal/durum ve ambient proxy yardımcı ilkelleri |
  | `plugin-sdk/webhook-targets` | Webhook hedef yardımcıları | Webhook hedef kaydı ve route-install yardımcıları |
  | `plugin-sdk/webhook-path` | Webhook yol yardımcıları | Webhook yolu normalleştirme yardımcıları |
  | `plugin-sdk/web-media` | Paylaşılan web medya yardımcıları | Uzak/yerel medya yükleme yardımcıları |
  | `plugin-sdk/zod` | Zod yeniden dışa aktarması | Plugin SDK tüketicileri için yeniden dışa aktarılan `zod` |
  | `plugin-sdk/memory-core` | Paketle gelen memory-core yardımcıları | Memory manager/yapılandırma/dosya/CLI yardımcı yüzeyi |
  | `plugin-sdk/memory-core-engine-runtime` | Memory engine çalışma zamanı cephesi | Memory index/search çalışma zamanı cephesi |
  | `plugin-sdk/memory-core-host-engine-foundation` | Memory host foundation engine | Memory host foundation engine dışa aktarmaları |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Memory host embedding engine | Memory host embedding engine dışa aktarmaları |
  | `plugin-sdk/memory-core-host-engine-qmd` | Memory host QMD engine | Memory host QMD engine dışa aktarmaları |
  | `plugin-sdk/memory-core-host-engine-storage` | Memory host storage engine | Memory host storage engine dışa aktarmaları |
  | `plugin-sdk/memory-core-host-multimodal` | Memory host multimodal yardımcıları | Memory host multimodal yardımcıları |
  | `plugin-sdk/memory-core-host-query` | Memory host sorgu yardımcıları | Memory host sorgu yardımcıları |
  | `plugin-sdk/memory-core-host-secret` | Memory host secret yardımcıları | Memory host secret yardımcıları |
  | `plugin-sdk/memory-core-host-events` | Memory host olay günlüğü yardımcıları | Memory host olay günlüğü yardımcıları |
  | `plugin-sdk/memory-core-host-status` | Memory host durum yardımcıları | Memory host durum yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-cli` | Memory host CLI çalışma zamanı | Memory host CLI çalışma zamanı yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-core` | Memory host çekirdek çalışma zamanı | Memory host çekirdek çalışma zamanı yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-files` | Memory host dosya/çalışma zamanı yardımcıları | Memory host dosya/çalışma zamanı yardımcıları |
  | `plugin-sdk/memory-host-core` | Memory host çekirdek çalışma zamanı takma adı | Memory host çekirdek çalışma zamanı yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-host-events` | Memory host olay günlüğü takma adı | Memory host olay günlüğü yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-host-files` | Memory host dosya/çalışma zamanı takma adı | Memory host dosya/çalışma zamanı yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-host-markdown` | Yönetilen markdown yardımcıları | Memory'e bitişik plugin'ler için paylaşılan yönetilen-markdown yardımcıları |
  | `plugin-sdk/memory-host-search` | Etkin memory arama cephesi | Lazy active-memory search-manager çalışma zamanı cephesi |
  | `plugin-sdk/memory-host-status` | Memory host durum takma adı | Memory host durum yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-lancedb` | Paketle gelen memory-lancedb yardımcıları | Memory-lancedb yardımcı yüzeyi |
  | `plugin-sdk/testing` | Test yardımcı programları | Test yardımcıları ve mock'lar |
</Accordion>

Bu tablo bilerek tam SDK yüzeyi değil, yaygın geçiş alt kümesidir.
200'den fazla giriş noktasının tam listesi
`scripts/lib/plugin-sdk-entrypoints.json` içinde bulunur.

Bu liste hâlâ
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` ve `plugin-sdk/matrix*` gibi bazı paketle gelen plugin yardımcı yüzeylerini içerir. Bunlar
paketle gelen plugin bakımı ve uyumluluk için dışa aktarılmaya devam eder, ancak bilerek
yaygın geçiş tablosundan çıkarılmışlardır ve
yeni plugin kodu için önerilen hedef değildirler.

Aynı kural diğer paketle gelen yardımcı aileleri için de geçerlidir; örneğin:

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
  `plugin-sdk/thread-ownership` ve `plugin-sdk/voice-call` gibi paketle gelen yardımcı/plugin yüzeyleri

`plugin-sdk/github-copilot-token` şu anda dar token yardımcısı
yüzeyi olarak `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` ve `resolveCopilotApiToken` değerlerini sunar.

İşle eşleşen en dar içe aktarmayı kullanın. Bir dışa aktarma bulamıyorsanız,
`src/plugin-sdk/` altındaki kaynağı kontrol edin veya Discord'da sorun.

## Kaldırma zaman çizelgesi

| When                   | What happens                                                            |
| ---------------------- | ----------------------------------------------------------------------- |
| **Şimdi**              | Kullanımdan kaldırılmış yüzeyler çalışma zamanında uyarılar yayınlar    |
| **Sonraki büyük sürüm** | Kullanımdan kaldırılmış yüzeyler kaldırılır; bunları hâlâ kullanan plugin'ler başarısız olur |

Tüm çekirdek plugin'ler zaten geçirildi. Harici plugin'ler
sonraki büyük sürümden önce geçiş yapmalıdır.

## Uyarıları geçici olarak bastırma

Geçiş üzerinde çalışırken bu ortam değişkenlerini ayarlayın:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Bu kalıcı bir çözüm değil, geçici bir kaçış kapağıdır.

## İlgili

- [Başlangıç](/tr/plugins/building-plugins) — ilk plugin'inizi oluşturun
- [SDK Genel Bakışı](/tr/plugins/sdk-overview) — tam alt yol içe aktarma başvurusu
- [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins) — kanal plugin'leri oluşturma
- [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins) — sağlayıcı plugin'leri oluşturma
- [Plugin İç Yapısı](/tr/plugins/architecture) — mimariye derin bakış
- [Plugin Manifesti](/tr/plugins/manifest) — manifest şeması başvurusu
