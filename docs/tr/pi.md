---
read_when:
    - OpenClaw içindeki Pi SDK entegrasyon tasarımını anlamak istiyorsunuz
    - Pi için aracı oturum yaşam döngüsünü, araçları veya sağlayıcı bağlantılarını değiştiriyorsunuz
summary: OpenClaw'ın gömülü Pi aracı entegrasyonunun ve oturum yaşam döngüsünün mimarisi
title: Pi Entegrasyon Mimarisi
x-i18n:
    generated_at: "2026-04-06T03:09:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 28594290b018b7cc2963d33dbb7cec6a0bd817ac486dafad59dd2ccabd482582
    source_path: pi.md
    workflow: 15
---

# Pi Entegrasyon Mimarisi

Bu belge, OpenClaw'ın AI aracı yeteneklerini desteklemek için [pi-coding-agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) ve ona eşlik eden paketlerle (`pi-ai`, `pi-agent-core`, `pi-tui`) nasıl entegre olduğunu açıklar.

## Genel bakış

OpenClaw, bir AI kodlama aracısını mesajlaşma ağ geçidi mimarisine gömmek için pi SDK'sını kullanır. Pi'yi bir alt süreç olarak başlatmak veya RPC kipini kullanmak yerine OpenClaw, `createAgentSession()` aracılığıyla doğrudan pi'nin `AgentSession` sınıfını içe aktarır ve örnekler. Bu gömülü yaklaşım şunları sağlar:

- Oturum yaşam döngüsü ve olay işleme üzerinde tam denetim
- Özel araç ekleme (mesajlaşma, sandbox, kanala özgü eylemler)
- Kanal/bağlam başına sistem prompt özelleştirmesi
- Dallanma/sıkıştırma desteğiyle oturum kalıcılığı
- Geri dönüş ile çok hesaplı kimlik doğrulama profili döndürme
- Sağlayıcıdan bağımsız model değiştirme

## Paket bağımlılıkları

```json
{
  "@mariozechner/pi-agent-core": "0.64.0",
  "@mariozechner/pi-ai": "0.64.0",
  "@mariozechner/pi-coding-agent": "0.64.0",
  "@mariozechner/pi-tui": "0.64.0"
}
```

| Paket               | Amaç                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------ |
| `pi-ai`             | Çekirdek LLM soyutlamaları: `Model`, `streamSimple`, mesaj türleri, sağlayıcı API'leri               |
| `pi-agent-core`     | Aracı döngüsü, araç yürütme, `AgentMessage` türleri                                                    |
| `pi-coding-agent`   | Üst düzey SDK: `createAgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`, yerleşik araçlar |
| `pi-tui`            | Uçbirim kullanıcı arayüzü bileşenleri (OpenClaw'ın yerel TUI kipinde kullanılır)                      |

## Dosya yapısı

```
src/agents/
├── pi-embedded-runner.ts          # pi-embedded-runner/ içinden yeniden dışa aktarımlar
├── pi-embedded-runner/
│   ├── run.ts                     # Ana giriş: runEmbeddedPiAgent()
│   ├── run/
│   │   ├── attempt.ts             # Oturum kurulumu ile tek deneme mantığı
│   │   ├── params.ts              # RunEmbeddedPiAgentParams türü
│   │   ├── payloads.ts            # Çalıştırma sonuçlarından yanıt yükleri oluşturma
│   │   ├── images.ts              # Vision model görsel ekleme
│   │   └── types.ts               # EmbeddedRunAttemptResult
│   ├── abort.ts                   # İptal hatası algılama
│   ├── cache-ttl.ts               # Bağlam budama için önbellek TTL izleme
│   ├── compact.ts                 # El ile/otomatik sıkıştırma mantığı
│   ├── extensions.ts              # Gömülü çalıştırmalar için pi eklentilerini yükleme
│   ├── extra-params.ts            # Sağlayıcıya özgü akış parametreleri
│   ├── google.ts                  # Google/Gemini dönüş sıralama düzeltmeleri
│   ├── history.ts                 # Geçmiş sınırlama (DM ve grup)
│   ├── lanes.ts                   # Oturum/genel komut şeritleri
│   ├── logger.ts                  # Alt sistem günlüğü
│   ├── model.ts                   # ModelRegistry aracılığıyla model çözümleme
│   ├── runs.ts                    # Etkin çalıştırma izleme, iptal, kuyruk
│   ├── sandbox-info.ts            # Sistem promptu için sandbox bilgisi
│   ├── session-manager-cache.ts   # SessionManager örneği önbellekleme
│   ├── session-manager-init.ts    # Oturum dosyası başlatma
│   ├── system-prompt.ts           # Sistem promptu oluşturucu
│   ├── tool-split.ts              # Araçları builtIn ve custom olarak bölme
│   ├── types.ts                   # EmbeddedPiAgentMeta, EmbeddedPiRunResult
│   └── utils.ts                   # ThinkLevel eşleme, hata açıklaması
├── pi-embedded-subscribe.ts       # Oturum olayı aboneliği/dağıtımı
├── pi-embedded-subscribe.types.ts # SubscribeEmbeddedPiSessionParams
├── pi-embedded-subscribe.handlers.ts # Olay işleyici fabrikası
├── pi-embedded-subscribe.handlers.lifecycle.ts
├── pi-embedded-subscribe.handlers.types.ts
├── pi-embedded-block-chunker.ts   # Akış blok yanıt parçalama
├── pi-embedded-messaging.ts       # Mesajlaşma aracı gönderim izleme
├── pi-embedded-helpers.ts         # Hata sınıflandırma, dönüş doğrulama
├── pi-embedded-helpers/           # Yardımcı modüller
├── pi-embedded-utils.ts           # Biçimlendirme yardımcıları
├── pi-tools.ts                    # createOpenClawCodingTools()
├── pi-tools.abort.ts              # Araçlar için AbortSignal sarmalama
├── pi-tools.policy.ts             # Araç izin listesi/engelleme listesi ilkesi
├── pi-tools.read.ts               # Okuma aracı özelleştirmeleri
├── pi-tools.schema.ts             # Araç şeması normalizasyonu
├── pi-tools.types.ts              # AnyAgentTool tür takma adı
├── pi-tool-definition-adapter.ts  # AgentTool -> ToolDefinition bağdaştırıcısı
├── pi-settings.ts                 # Ayar geçersiz kılmaları
├── pi-hooks/                      # Özel pi kancaları
│   ├── compaction-safeguard.ts    # Koruma eklentisi
│   ├── compaction-safeguard-runtime.ts
│   ├── context-pruning.ts         # Cache-TTL bağlam budama eklentisi
│   └── context-pruning/
├── model-auth.ts                  # Kimlik doğrulama profili çözümleme
├── auth-profiles.ts               # Profil deposu, bekleme süresi, geri dönüş
├── model-selection.ts             # Varsayılan model çözümleme
├── models-config.ts               # models.json oluşturma
├── model-catalog.ts               # Model kataloğu önbelleği
├── context-window-guard.ts        # Bağlam penceresi doğrulama
├── failover-error.ts              # FailoverError sınıfı
├── defaults.ts                    # DEFAULT_PROVIDER, DEFAULT_MODEL
├── system-prompt.ts               # buildAgentSystemPrompt()
├── system-prompt-params.ts        # Sistem prompt parametresi çözümleme
├── system-prompt-report.ts        # Hata ayıklama raporu oluşturma
├── tool-summaries.ts              # Araç açıklama özetleri
├── tool-policy.ts                 # Araç ilkesi çözümleme
├── transcript-policy.ts           # Transkript doğrulama ilkesi
├── skills.ts                      # Skill anlık görüntüsü/prompt oluşturma
├── skills/                        # Skill alt sistemi
├── sandbox.ts                     # Sandbox bağlamı çözümleme
├── sandbox/                       # Sandbox alt sistemi
├── channel-tools.ts               # Kanala özgü araç ekleme
├── openclaw-tools.ts              # OpenClaw'a özgü araçlar
├── bash-tools.ts                  # exec/process araçları
├── apply-patch.ts                 # apply_patch aracı (OpenAI)
├── tools/                         # Tek tek araç uygulamaları
│   ├── browser-tool.ts
│   ├── canvas-tool.ts
│   ├── cron-tool.ts
│   ├── gateway-tool.ts
│   ├── image-tool.ts
│   ├── message-tool.ts
│   ├── nodes-tool.ts
│   ├── session*.ts
│   ├── web-*.ts
│   └── ...
└── ...
```

Kanala özgü mesaj eylemi çalışma zamanları artık `src/agents/tools` altında değil,
eklentiye ait uzantı dizinlerinde bulunur; örneğin:

- Discord eklentisi eylem çalışma zamanı dosyaları
- Slack eklentisi eylem çalışma zamanı dosyası
- Telegram eklentisi eylem çalışma zamanı dosyası
- WhatsApp eklentisi eylem çalışma zamanı dosyası

## Çekirdek entegrasyon akışı

### 1. Gömülü bir aracı çalıştırma

Ana giriş noktası `pi-embedded-runner/run.ts` içindeki `runEmbeddedPiAgent()` fonksiyonudur:

```typescript
import { runEmbeddedPiAgent } from "./agents/pi-embedded-runner.js";

const result = await runEmbeddedPiAgent({
  sessionId: "user-123",
  sessionKey: "main:whatsapp:+1234567890",
  sessionFile: "/path/to/session.jsonl",
  workspaceDir: "/path/to/workspace",
  config: openclawConfig,
  prompt: "Hello, how are you?",
  provider: "anthropic",
  model: "claude-sonnet-4-6",
  timeoutMs: 120_000,
  runId: "run-abc",
  onBlockReply: async (payload) => {
    await sendToChannel(payload.text, payload.mediaUrls);
  },
});
```

### 2. Oturum oluşturma

`runEmbeddedAttempt()` içinde (`runEmbeddedPiAgent()` tarafından çağrılır), pi SDK kullanılır:

```typescript
import {
  createAgentSession,
  DefaultResourceLoader,
  SessionManager,
  SettingsManager,
} from "@mariozechner/pi-coding-agent";

const resourceLoader = new DefaultResourceLoader({
  cwd: resolvedWorkspace,
  agentDir,
  settingsManager,
  additionalExtensionPaths,
});
await resourceLoader.reload();

const { session } = await createAgentSession({
  cwd: resolvedWorkspace,
  agentDir,
  authStorage: params.authStorage,
  modelRegistry: params.modelRegistry,
  model: params.model,
  thinkingLevel: mapThinkingLevel(params.thinkLevel),
  tools: builtInTools,
  customTools: allCustomTools,
  sessionManager,
  settingsManager,
  resourceLoader,
});

applySystemPromptOverrideToSession(session, systemPromptOverride);
```

### 3. Olay aboneliği

`subscribeEmbeddedPiSession()`, pi'nin `AgentSession` olaylarına abone olur:

```typescript
const subscription = subscribeEmbeddedPiSession({
  session: activeSession,
  runId: params.runId,
  verboseLevel: params.verboseLevel,
  reasoningMode: params.reasoningLevel,
  toolResultFormat: params.toolResultFormat,
  onToolResult: params.onToolResult,
  onReasoningStream: params.onReasoningStream,
  onBlockReply: params.onBlockReply,
  onPartialReply: params.onPartialReply,
  onAgentEvent: params.onAgentEvent,
});
```

İşlenen olaylar şunları içerir:

- `message_start` / `message_end` / `message_update` (akış metni/düşünme)
- `tool_execution_start` / `tool_execution_update` / `tool_execution_end`
- `turn_start` / `turn_end`
- `agent_start` / `agent_end`
- `auto_compaction_start` / `auto_compaction_end`

### 4. Prompt gönderme

Kurulumdan sonra oturuma prompt gönderilir:

```typescript
await session.prompt(effectivePrompt, { images: imageResult.images });
```

SDK, LLM'e gönderme, araç çağrılarını yürütme ve yanıtları akıtma dahil tüm aracı döngüsünü yönetir.

Görsel ekleme prompt yereldir: OpenClaw, geçerli prompttan görsel başvurularını yükler ve
bunları yalnızca o dönüş için `images` aracılığıyla geçirir. Eski geçmiş dönüşlerini yeniden tarayıp
görsel yüklerini yeniden eklemez.

## Araç mimarisi

### Araç hattı

1. **Temel araçlar**: pi'nin `codingTools` araçları (read, bash, edit, write)
2. **Özel değiştirmeler**: OpenClaw, bash'i `exec`/`process` ile değiştirir, read/edit/write araçlarını sandbox için özelleştirir
3. **OpenClaw araçları**: mesajlaşma, browser, canvas, sessions, cron, gateway vb.
4. **Kanal araçları**: Discord/Telegram/Slack/WhatsApp'e özgü eylem araçları
5. **İlke filtreleme**: Araçlar profil, sağlayıcı, aracı, grup ve sandbox ilkelerine göre filtrelenir
6. **Şema normalizasyonu**: Şemalar Gemini/OpenAI farklılıkları için temizlenir
7. **AbortSignal sarmalama**: Araçlar iptal sinyallerine uyacak şekilde sarılır

### Araç tanımı bağdaştırıcısı

pi-agent-core'un `AgentTool` tipi, pi-coding-agent'in `ToolDefinition` tipinden farklı bir `execute` imzasına sahiptir. `pi-tool-definition-adapter.ts` içindeki bağdaştırıcı bunu köprüler:

```typescript
export function toToolDefinitions(tools: AnyAgentTool[]): ToolDefinition[] {
  return tools.map((tool) => ({
    name: tool.name,
    label: tool.label ?? name,
    description: tool.description ?? "",
    parameters: tool.parameters,
    execute: async (toolCallId, params, onUpdate, _ctx, signal) => {
      // pi-coding-agent imzası pi-agent-core'dan farklıdır
      return await tool.execute(toolCallId, params, signal, onUpdate);
    },
  }));
}
```

### Araç bölme stratejisi

`splitSdkTools()`, tüm araçları `customTools` aracılığıyla geçirir:

```typescript
export function splitSdkTools(options: { tools: AnyAgentTool[]; sandboxEnabled: boolean }) {
  return {
    builtInTools: [], // Boş. Her şeyi geçersiz kılıyoruz
    customTools: toToolDefinitions(options.tools),
  };
}
```

Bu, OpenClaw'ın ilke filtreleme, sandbox entegrasyonu ve genişletilmiş araç kümesinin sağlayıcılar arasında tutarlı kalmasını sağlar.

## Sistem promptu oluşturma

Sistem promptu `buildAgentSystemPrompt()` içinde (`system-prompt.ts`) oluşturulur. Araçlar, Araç Çağrısı Stili, Güvenlik korkulukları, OpenClaw CLI başvurusu, Skills, Belgeler, Çalışma Alanı, Sandbox, Mesajlaşma, Yanıt Etiketleri, Ses, Sessiz Yanıtlar, Heartbeats, Çalışma Zamanı meta verileri ve etkin olduğunda Bellek ile Tepkiler dahil bölümlerle tam bir prompt derler; ayrıca isteğe bağlı bağlam dosyaları ve ek sistem prompt içeriği de eklenebilir. Alt aracılarda kullanılan en düşük prompt kipi için bölümler kırpılır.

Prompt, oturum oluşturulduktan sonra `applySystemPromptOverrideToSession()` ile uygulanır:

```typescript
const systemPromptOverride = createSystemPromptOverride(appendPrompt);
applySystemPromptOverrideToSession(session, systemPromptOverride);
```

## Oturum yönetimi

### Oturum dosyaları

Oturumlar, ağaç yapısına sahip (id/parentId bağlantılı) JSONL dosyalarıdır. Pi'nin `SessionManager` sınıfı kalıcılığı yönetir:

```typescript
const sessionManager = SessionManager.open(params.sessionFile);
```

OpenClaw bunu, araç sonucu güvenliği için `guardSessionManager()` ile sarar.

### Oturum önbellekleme

`session-manager-cache.ts`, tekrarlayan dosya ayrıştırmasını önlemek için SessionManager örneklerini önbelleğe alır:

```typescript
await prewarmSessionFile(params.sessionFile);
sessionManager = SessionManager.open(params.sessionFile);
trackSessionManagerAccess(params.sessionFile);
```

### Geçmiş sınırlama

`limitHistoryTurns()`, konuşma geçmişini kanal türüne göre (DM ve grup) kırpar.

### Sıkıştırma

Otomatik sıkıştırma, bağlam taşmasında tetiklenir. Yaygın taşma imzaları arasında
`request_too_large`, `context length exceeded`, `input exceeds the
maximum number of tokens`, `input token count exceeds the maximum number of
input tokens`, `input is too long for the model` ve `ollama error: context
length exceeded` bulunur. `compactEmbeddedPiSessionDirect()`, el ile
sıkıştırmayı yönetir:

```typescript
const compactResult = await compactEmbeddedPiSessionDirect({
  sessionId, sessionFile, provider, model, ...
});
```

## Kimlik doğrulama ve model çözümleme

### Kimlik doğrulama profilleri

OpenClaw, sağlayıcı başına birden çok API anahtarı içeren bir kimlik doğrulama profili deposu tutar:

```typescript
const authStore = ensureAuthProfileStore(agentDir, { allowKeychainPrompt: false });
const profileOrder = resolveAuthProfileOrder({ cfg, store: authStore, provider, preferredProfile });
```

Profiller, bekleme süresi izlemeyle birlikte başarısızlıklarda döndürülür:

```typescript
await markAuthProfileFailure({ store, profileId, reason, cfg, agentDir });
const rotated = await advanceAuthProfile();
```

### Model çözümleme

```typescript
import { resolveModel } from "./pi-embedded-runner/model.js";

const { model, error, authStorage, modelRegistry } = resolveModel(
  provider,
  modelId,
  agentDir,
  config,
);

// pi'nin ModelRegistry ve AuthStorage yapılarını kullanır
authStorage.setRuntimeApiKey(model.provider, apiKeyInfo.apiKey);
```

### Geri dönüş

Yapılandırıldığında `FailoverError`, model geri dönüşünü tetikler:

```typescript
if (fallbackConfigured && isFailoverErrorMessage(errorText)) {
  throw new FailoverError(errorText, {
    reason: promptFailoverReason ?? "unknown",
    provider,
    model: modelId,
    profileId,
    status: resolveFailoverStatus(promptFailoverReason),
  });
}
```

## Pi eklentileri

OpenClaw, özel davranışlar için özel pi eklentileri yükler:

### Sıkıştırma koruması

`src/agents/pi-hooks/compaction-safeguard.ts`, uyarlanabilir belirteç bütçeleme ile araç başarısızlığı ve dosya işlemi özetleri dahil olmak üzere sıkıştırmaya korkuluklar ekler:

```typescript
if (resolveCompactionMode(params.cfg) === "safeguard") {
  setCompactionSafeguardRuntime(params.sessionManager, { maxHistoryShare });
  paths.push(resolvePiExtensionPath("compaction-safeguard"));
}
```

### Bağlam budama

`src/agents/pi-hooks/context-pruning.ts`, önbellek TTL tabanlı bağlam budamayı uygular:

```typescript
if (cfg?.agents?.defaults?.contextPruning?.mode === "cache-ttl") {
  setContextPruningRuntime(params.sessionManager, {
    settings,
    contextWindowTokens,
    isToolPrunable,
    lastCacheTouchAt,
  });
  paths.push(resolvePiExtensionPath("context-pruning"));
}
```

## Akış ve blok yanıtlar

### Blok parçalama

`EmbeddedBlockChunker`, akış metnini ayrı yanıt bloklarına dönüştürmeyi yönetir:

```typescript
const blockChunker = blockChunking ? new EmbeddedBlockChunker(blockChunking) : null;
```

### Düşünme/nihai etiket temizleme

Akış çıktısı, `<think>`/`<thinking>` bloklarını çıkarmak ve `<final>` içeriğini ayıklamak için işlenir:

```typescript
const stripBlockTags = (text: string, state: { thinking: boolean; final: boolean }) => {
  // <think>...</think> içeriğini çıkar
  // enforceFinalTag ayarlıysa yalnızca <final>...</final> içeriğini döndür
};
```

### Yanıt yönergeleri

`[[media:url]]`, `[[voice]]`, `[[reply:id]]` gibi yanıt yönergeleri ayrıştırılır ve çıkarılır:

```typescript
const { text: cleanedText, mediaUrls, audioAsVoice, replyToId } = consumeReplyDirectives(chunk);
```

## Hata işleme

### Hata sınıflandırma

`pi-embedded-helpers.ts`, uygun işleme için hataları sınıflandırır:

```typescript
isContextOverflowError(errorText)     // Bağlam çok büyük
isCompactionFailureError(errorText)   // Sıkıştırma başarısız oldu
isAuthAssistantError(lastAssistant)   // Kimlik doğrulama başarısızlığı
isRateLimitAssistantError(...)        // Hız sınırı uygulandı
isFailoverAssistantError(...)         // Geri dönüş olmalı
classifyFailoverReason(errorText)     // "auth" | "rate_limit" | "quota" | "timeout" | ...
```

### Düşünme seviyesi geri dönüşü

Bir düşünme seviyesi desteklenmiyorsa geri düşülür:

```typescript
const fallbackThinking = pickFallbackThinkingLevel({
  message: errorText,
  attempted: attemptedThinking,
});
if (fallbackThinking) {
  thinkLevel = fallbackThinking;
  continue;
}
```

## Sandbox entegrasyonu

Sandbox kipi etkin olduğunda araçlar ve yollar kısıtlanır:

```typescript
const sandbox = await resolveSandboxContext({
  config: params.config,
  sessionKey: sandboxSessionKey,
  workspaceDir: resolvedWorkspace,
});

if (sandboxRoot) {
  // Sandboxlı read/edit/write araçlarını kullan
  // Exec kapsayıcı içinde çalışır
  // Browser köprü URL'sini kullanır
}
```

## Sağlayıcıya özgü işleme

### Anthropic

- Ret sihirli dize temizleme
- Art arda gelen roller için dönüş doğrulaması
- Katı yukarı akış Pi araç parametresi doğrulaması

### Google/Gemini

- Eklentiye ait araç şeması temizleme

### OpenAI

- Codex modelleri için `apply_patch` aracı
- Düşünme seviyesi düşürme işleme

## TUI entegrasyonu

OpenClaw ayrıca doğrudan pi-tui bileşenlerini kullanan yerel bir TUI kipine de sahiptir:

```typescript
// src/tui/tui.ts
import { ... } from "@mariozechner/pi-tui";
```

Bu, pi'nin yerel kipine benzer etkileşimli uçbirim deneyimini sağlar.

## Pi CLI'den temel farklar

| Özellik         | Pi CLI                  | OpenClaw Gömülü                                                                              |
| --------------- | ----------------------- | --------------------------------------------------------------------------------------------- |
| Çağırma         | `pi` komutu / RPC       | `createAgentSession()` aracılığıyla SDK                                                       |
| Araçlar         | Varsayılan kodlama araçları | Özel OpenClaw araç paketi                                                                  |
| Sistem promptu  | AGENTS.md + promptlar   | Kanal/bağlam başına dinamik                                                                   |
| Oturum depolama | `~/.pi/agent/sessions/` | `~/.openclaw/agents/<agentId>/sessions/` (veya `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`) |
| Kimlik doğrulama| Tek kimlik bilgisi      | Döndürmeli çoklu profil                                                                       |
| Eklentiler      | Diskten yüklenir        | Programatik + disk yolları                                                                    |
| Olay işleme     | TUI oluşturma           | Geri çağırım tabanlı (`onBlockReply` vb.)                                                     |

## Geleceğe yönelik değerlendirmeler

Olası yeniden çalışma alanları:

1. **Araç imzası hizalaması**: Şu anda pi-agent-core ile pi-coding-agent imzaları arasında uyarlama yapılıyor
2. **Oturum yöneticisi sarmalama**: `guardSessionManager` güvenlik ekliyor ancak karmaşıklığı artırıyor
3. **Eklenti yükleme**: Pi'nin `ResourceLoader` yapısı daha doğrudan kullanılabilir
4. **Akış işleyici karmaşıklığı**: `subscribeEmbeddedPiSession` büyüdü
5. **Sağlayıcı farklılıkları**: Pi'nin potansiyel olarak işleyebileceği çok sayıda sağlayıcıya özgü kod yolu var

## Testler

Pi entegrasyonu kapsamı şu paketlere yayılır:

- `src/agents/pi-*.test.ts`
- `src/agents/pi-auth-json.test.ts`
- `src/agents/pi-embedded-*.test.ts`
- `src/agents/pi-embedded-helpers*.test.ts`
- `src/agents/pi-embedded-runner*.test.ts`
- `src/agents/pi-embedded-runner/**/*.test.ts`
- `src/agents/pi-embedded-subscribe*.test.ts`
- `src/agents/pi-tools*.test.ts`
- `src/agents/pi-tool-definition-adapter*.test.ts`
- `src/agents/pi-settings.test.ts`
- `src/agents/pi-hooks/**/*.test.ts`

Canlı/isteğe bağlı:

- `src/agents/pi-embedded-runner-extraparams.live.test.ts` (`OPENCLAW_LIVE_TEST=1` etkinleştirin)

Güncel çalıştırma komutları için bkz. [Pi Development Workflow](/tr/pi-dev).
