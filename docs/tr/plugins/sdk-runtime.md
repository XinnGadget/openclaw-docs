---
read_when:
    - Bir plugin içinden çekirdek yardımcıları çağırmanız gerekiyor (TTS, STT, image gen, web search, subagent)
    - api.runtime'ın ne sunduğunu anlamak istiyorsunuz
    - Plugin kodundan config, agent veya medya yardımcılarına erişiyorsunuz
sidebarTitle: Runtime Helpers
summary: api.runtime -- plugin'ler için kullanılabilen enjekte edilmiş çalışma zamanı yardımcıları
title: Plugin Çalışma Zamanı Yardımcıları
x-i18n:
    generated_at: "2026-04-07T08:48:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: acb9e56678e9ed08d0998dfafd7cd1982b592be5bc34d9e2d2c1f70274f8f248
    source_path: plugins/sdk-runtime.md
    workflow: 15
---

# Plugin Çalışma Zamanı Yardımcıları

Kayıt sırasında her plugin'e enjekte edilen `api.runtime` nesnesi için referans.
Host iç bileşenlerini doğrudan import etmek yerine bu yardımcıları kullanın.

<Tip>
  **Adım adım bir kılavuz mu arıyorsunuz?** Bu yardımcıların bağlam içinde nasıl
  kullanıldığını gösteren adım adım rehberler için [Channel Plugins](/tr/plugins/sdk-channel-plugins)
  veya [Provider Plugins](/tr/plugins/sdk-provider-plugins) sayfalarına bakın.
</Tip>

```typescript
register(api) {
  const runtime = api.runtime;
}
```

## Çalışma zamanı ad alanları

### `api.runtime.agent`

Agent kimliği, dizinler ve oturum yönetimi.

```typescript
// Agent'ın çalışma dizinini çözümle
const agentDir = api.runtime.agent.resolveAgentDir(cfg);

// Agent çalışma alanını çözümle
const workspaceDir = api.runtime.agent.resolveAgentWorkspaceDir(cfg);

// Agent kimliğini al
const identity = api.runtime.agent.resolveAgentIdentity(cfg);

// Varsayılan düşünme düzeyini al
const thinking = api.runtime.agent.resolveThinkingDefault(cfg, provider, model);

// Agent zaman aşımını al
const timeoutMs = api.runtime.agent.resolveAgentTimeoutMs(cfg);

// Çalışma alanının var olduğundan emin ol
await api.runtime.agent.ensureAgentWorkspace(cfg);

// Gömülü bir Pi agent'ı çalıştır
const agentDir = api.runtime.agent.resolveAgentDir(cfg);
const result = await api.runtime.agent.runEmbeddedPiAgent({
  sessionId: "my-plugin:task-1",
  runId: crypto.randomUUID(),
  sessionFile: path.join(agentDir, "sessions", "my-plugin-task-1.jsonl"),
  workspaceDir: api.runtime.agent.resolveAgentWorkspaceDir(cfg),
  prompt: "Son değişiklikleri özetle",
  timeoutMs: api.runtime.agent.resolveAgentTimeoutMs(cfg),
});
```

**Oturum deposu yardımcıları** `api.runtime.agent.session` altındadır:

```typescript
const storePath = api.runtime.agent.session.resolveStorePath(cfg);
const store = api.runtime.agent.session.loadSessionStore(cfg);
await api.runtime.agent.session.saveSessionStore(cfg, store);
const filePath = api.runtime.agent.session.resolveSessionFilePath(cfg, sessionId);
```

### `api.runtime.agent.defaults`

Varsayılan model ve sağlayıcı sabitleri:

```typescript
const model = api.runtime.agent.defaults.model; // örn. "anthropic/claude-sonnet-4-6"
const provider = api.runtime.agent.defaults.provider; // örn. "anthropic"
```

### `api.runtime.subagent`

Arka plan subagent çalıştırmalarını başlatın ve yönetin.

```typescript
// Bir subagent çalıştırması başlat
const { runId } = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Bu sorguyu odaklı takip aramalarına genişlet.",
  provider: "openai", // isteğe bağlı geçersiz kılma
  model: "gpt-4.1-mini", // isteğe bağlı geçersiz kılma
  deliver: false,
});

// Tamamlanmasını bekle
const result = await api.runtime.subagent.waitForRun({ runId, timeoutMs: 30000 });

// Oturum mesajlarını oku
const { messages } = await api.runtime.subagent.getSessionMessages({
  sessionKey: "agent:main:subagent:search-helper",
  limit: 10,
});

// Bir oturumu sil
await api.runtime.subagent.deleteSession({
  sessionKey: "agent:main:subagent:search-helper",
});
```

<Warning>
  Model geçersiz kılmaları (`provider`/`model`), config içinde
  `plugins.entries.<id>.subagent.allowModelOverride: true` ile operatör onayı gerektirir.
  Güvenilmeyen plugin'ler yine de subagent çalıştırabilir, ancak geçersiz kılma istekleri reddedilir.
</Warning>

### `api.runtime.taskFlow`

Bir Task Flow çalışma zamanını mevcut bir OpenClaw session key'e veya güvenilir araç
bağlamına bağlayın, ardından her çağrıda owner geçmeden Task Flow'lar oluşturun ve yönetin.

```typescript
const taskFlow = api.runtime.taskFlow.fromToolContext(ctx);

const created = taskFlow.createManaged({
  controllerId: "my-plugin/review-batch",
  goal: "Yeni pull request'leri incele",
});

const child = taskFlow.runTask({
  flowId: created.flowId,
  runtime: "acp",
  childSessionKey: "agent:main:subagent:reviewer",
  task: "PR #123'ü incele",
  status: "running",
  startedAt: Date.now(),
});

const waiting = taskFlow.setWaiting({
  flowId: created.flowId,
  expectedRevision: created.revision,
  currentStep: "await-human-reply",
  waitJson: { kind: "reply", channel: "telegram" },
});
```

Kendi bağlama katmanınızdan zaten güvenilir bir OpenClaw session key'iniz varsa
`bindSession({ sessionKey, requesterOrigin })` kullanın. Ham kullanıcı girdisinden bağlama yapmayın.

### `api.runtime.tts`

Metinden konuşmaya sentezi.

```typescript
// Standart TTS
const clip = await api.runtime.tts.textToSpeech({
  text: "OpenClaw'dan merhaba",
  cfg: api.config,
});

// Telefoni için optimize edilmiş TTS
const telephonyClip = await api.runtime.tts.textToSpeechTelephony({
  text: "OpenClaw'dan merhaba",
  cfg: api.config,
});

// Kullanılabilir sesleri listele
const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Çekirdek `messages.tts` config'i ve sağlayıcı seçimini kullanır. PCM ses
buffer'ı + örnekleme hızı döndürür.

### `api.runtime.mediaUnderstanding`

Görüntü, ses ve video analizi.

```typescript
// Bir görüntüyü açıkla
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

// Sesi yazıya dök
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  mime: "audio/ogg", // isteğe bağlı, MIME çıkarılamadığında
});

// Bir videoyu açıkla
const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});

// Genel dosya analizi
const result = await api.runtime.mediaUnderstanding.runFile({
  filePath: "/tmp/inbound-file.pdf",
  cfg: api.config,
});
```

Çıktı üretilmediğinde `{ text: undefined }` döndürür (örn. girdi atlandığında).

<Info>
  `api.runtime.stt.transcribeAudioFile(...)`, uyumluluk takma adı olarak
  `api.runtime.mediaUnderstanding.transcribeAudioFile(...)` için kullanılmaya devam eder.
</Info>

### `api.runtime.imageGeneration`

Görüntü üretimi.

```typescript
const result = await api.runtime.imageGeneration.generate({
  prompt: "Gün batımını resmeden bir robot",
  cfg: api.config,
});

const providers = api.runtime.imageGeneration.listProviders({ cfg: api.config });
```

### `api.runtime.webSearch`

Web araması.

```typescript
const providers = api.runtime.webSearch.listProviders({ config: api.config });

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: { query: "OpenClaw plugin SDK", count: 5 },
});
```

### `api.runtime.media`

Düşük seviyeli medya yardımcıları.

```typescript
const webMedia = await api.runtime.media.loadWebMedia(url);
const mime = await api.runtime.media.detectMime(buffer);
const kind = api.runtime.media.mediaKindFromMime("image/jpeg"); // "image"
const isVoice = api.runtime.media.isVoiceCompatibleAudio(filePath);
const metadata = await api.runtime.media.getImageMetadata(filePath);
const resized = await api.runtime.media.resizeToJpeg(buffer, { maxWidth: 800 });
```

### `api.runtime.config`

Config yükleme ve yazma.

```typescript
const cfg = await api.runtime.config.loadConfig();
await api.runtime.config.writeConfigFile(cfg);
```

### `api.runtime.system`

Sistem düzeyinde yardımcılar.

```typescript
await api.runtime.system.enqueueSystemEvent(event);
api.runtime.system.requestHeartbeatNow();
const output = await api.runtime.system.runCommandWithTimeout(cmd, args, opts);
const hint = api.runtime.system.formatNativeDependencyHint(pkg);
```

### `api.runtime.events`

Olay abonelikleri.

```typescript
api.runtime.events.onAgentEvent((event) => {
  /* ... */
});
api.runtime.events.onSessionTranscriptUpdate((update) => {
  /* ... */
});
```

### `api.runtime.logging`

Loglama.

```typescript
const verbose = api.runtime.logging.shouldLogVerbose();
const childLogger = api.runtime.logging.getChildLogger({ plugin: "my-plugin" }, { level: "debug" });
```

### `api.runtime.modelAuth`

Model ve sağlayıcı auth çözümleme.

```typescript
const auth = await api.runtime.modelAuth.getApiKeyForModel({ model, cfg });
const providerAuth = await api.runtime.modelAuth.resolveApiKeyForProvider({
  provider: "openai",
  cfg,
});
```

### `api.runtime.state`

Durum dizini çözümleme.

```typescript
const stateDir = api.runtime.state.resolveStateDir();
```

### `api.runtime.tools`

Bellek araç fabrikaları ve CLI.

```typescript
const getTool = api.runtime.tools.createMemoryGetTool(/* ... */);
const searchTool = api.runtime.tools.createMemorySearchTool(/* ... */);
api.runtime.tools.registerMemoryCli(/* ... */);
```

### `api.runtime.channel`

Kanala özgü çalışma zamanı yardımcıları (bir kanal plugin'i yüklendiğinde kullanılabilir).

`api.runtime.channel.mentions`, çalışma zamanı enjeksiyonu kullanan
paketlenmiş kanal plugin'leri için paylaşılan gelen mention-ilke yüzeyidir:

```typescript
const mentionMatch = api.runtime.channel.mentions.matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const decision = api.runtime.channel.mentions.resolveInboundMentionDecision({
  facts: {
    canDetectMention: true,
    wasMentioned: mentionMatch.matched,
    implicitMentionKinds: api.runtime.channel.mentions.implicitMentionKindWhen(
      "reply_to_bot",
      isReplyToBot,
    ),
  },
  policy: {
    isGroup,
    requireMention,
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});
```

Kullanılabilir mention yardımcıları:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

`api.runtime.channel.mentions`, eski
`resolveMentionGating*` uyumluluk yardımcılarını kasıtlı olarak sunmaz. Normalize edilmiş
`{ facts, policy }` yolunu tercih edin.

## Çalışma zamanı referanslarını saklama

Çalışma zamanı referansını `register` callback'i dışında kullanmak için saklamak üzere
`createPluginRuntimeStore` kullanın:

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>("my-plugin runtime başlatılmadı");

// Entry point'inizde
export default defineChannelPluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Örnek",
  plugin: myPlugin,
  setRuntime: store.setRuntime,
});

// Diğer dosyalarda
export function getRuntime() {
  return store.getRuntime(); // başlatılmadıysa hata fırlatır
}

export function tryGetRuntime() {
  return store.tryGetRuntime(); // başlatılmadıysa null döndürür
}
```

## Diğer üst düzey `api` alanları

`api.runtime` dışında API nesnesi ayrıca şunları da sağlar:

| Alan                    | Tür                       | Açıklama                                                                                    |
| ----------------------- | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                | `string`                  | Plugin kimliği                                                                              |
| `api.name`              | `string`                  | Plugin görünen adı                                                                          |
| `api.config`            | `OpenClawConfig`          | Geçerli config snapshot'u (mevcutsa etkin bellek içi çalışma zamanı snapshot'u)            |
| `api.pluginConfig`      | `Record<string, unknown>` | `plugins.entries.<id>.config` içinden gelen plugin'e özgü config                            |
| `api.logger`            | `PluginLogger`            | Kapsamlı logger (`debug`, `info`, `warn`, `error`)                                          |
| `api.registrationMode`  | `PluginRegistrationMode`  | Geçerli yükleme modu; `"setup-runtime"` hafif ön tam giriş başlangıç/kurulum penceresidir  |
| `api.resolvePath(input)`| `(string) => string`      | Plugin köküne göre bir yolu çözümle                                                         |

## İlgili

- [SDK Overview](/tr/plugins/sdk-overview) -- alt yol referansı
- [SDK Entry Points](/tr/plugins/sdk-entrypoints) -- `definePluginEntry` seçenekleri
- [Plugin Internals](/tr/plugins/architecture) -- yetenek modeli ve kayıt sistemi
