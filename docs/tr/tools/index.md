---
read_when:
    - OpenClaw’un hangi araçları sunduğunu anlamak istiyorsunuz
    - Araçları yapılandırmanız, izin vermeniz veya engellemeniz gerekiyor
    - Yerleşik araçlar, Skills ve plugin’ler arasında karar veriyorsunuz
summary: 'OpenClaw araçları ve plugin’lerine genel bakış: agent’ın neler yapabildiği ve nasıl genişletileceği'
title: Araçlar ve Plugin’ler
x-i18n:
    generated_at: "2026-04-06T03:13:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: b2371239316997b0fe389bfa2ec38404e1d3e177755ad81ff8035ac583d9adeb
    source_path: tools/index.md
    workflow: 15
---

# Araçlar ve Plugin’ler

Agent’ın metin üretmenin ötesinde yaptığı her şey **araçlar** aracılığıyla olur.
Araçlar, agent’ın dosya okumasını, komut çalıştırmasını, web’de gezinmesini, mesaj
göndermesini ve cihazlarla etkileşime girmesini sağlar.

## Araçlar, Skills ve plugin’ler

OpenClaw birlikte çalışan üç katmana sahiptir:

<Steps>
  <Step title="Araçlar, agent’ın çağırdığı şeylerdir">
    Araç, agent’ın çağırabildiği tiplenmiş bir işlevdir (ör. `exec`, `browser`,
    `web_search`, `message`). OpenClaw bir dizi **yerleşik araç** ile gelir ve
    plugin’ler ek araçlar kaydedebilir.

    Agent, araçları model API’sine gönderilen yapılandırılmış işlev tanımları olarak görür.

  </Step>

  <Step title="Skills, agent’a ne zaman ve nasıl kullanılacağını öğretir">
    Skill, sistem komutuna enjekte edilen bir markdown dosyasıdır (`SKILL.md`).
    Skills, agent’a araçları etkili şekilde kullanması için bağlam, kısıtlar ve
    adım adım rehberlik sağlar. Skills çalışma alanınızda, paylaşılan klasörlerde
    bulunabilir veya plugin’lerin içinde gelebilir.

    [Skills başvurusu](/tr/tools/skills) | [Skill oluşturma](/tr/tools/creating-skills)

  </Step>

  <Step title="Plugin’ler her şeyi birlikte paketler">
    Plugin, herhangi bir yetenek kombinasyonunu kaydedebilen bir pakettir:
    channels, model provider’lar, araçlar, Skills, konuşma, gerçek zamanlı transcription,
    gerçek zamanlı voice, medya anlama, görsel oluşturma, video oluşturma,
    web fetch, web search ve daha fazlası. Bazı plugin’ler **core**’dur (OpenClaw ile
    birlikte gelir), bazıları ise **external**’dır (topluluk tarafından npm üzerinde yayımlanır).

    [Plugin’leri kurun ve yapılandırın](/tr/tools/plugin) | [Kendinizinkini oluşturun](/tr/plugins/building-plugins)

  </Step>
</Steps>

## Yerleşik araçlar

Bu araçlar OpenClaw ile birlikte gelir ve herhangi bir plugin kurmadan kullanılabilir:

| Araç                                       | Ne yapar                                                              | Sayfa                                       |
| ------------------------------------------ | --------------------------------------------------------------------- | ------------------------------------------- |
| `exec` / `process`                         | Shell komutları çalıştırır, arka plan süreçlerini yönetir             | [Exec](/tr/tools/exec)                         |
| `code_execution`                           | Sandbox içinde uzak Python analizi çalıştırır                         | [Code Execution](/tr/tools/code-execution)     |
| `browser`                                  | Bir Chromium tarayıcısını denetler (gezinme, tıklama, ekran görüntüsü) | [Browser](/tr/tools/browser)                   |
| `web_search` / `x_search` / `web_fetch`    | Web’de arama yapar, X gönderilerini arar, sayfa içeriğini getirir     | [Web](/tr/tools/web)                           |
| `read` / `write` / `edit`                  | Çalışma alanında dosya G/Ç                                            |                                             |
| `apply_patch`                              | Çok parçalı dosya yamaları                                            | [Apply Patch](/tr/tools/apply-patch)           |
| `message`                                  | Tüm channels üzerinden mesaj gönderir                                 | [Agent Send](/tr/tools/agent-send)             |
| `canvas`                                   | Node Canvas’ı sürer (sunum, değerlendirme, snapshot)                  |                                             |
| `nodes`                                    | Eşleştirilmiş cihazları keşfeder ve hedefler                          |                                             |
| `cron` / `gateway`                         | Zamanlanmış işleri yönetir; gateway’i inceler, düzeltir, yeniden başlatır veya günceller |                                             |
| `image` / `image_generate`                 | Görselleri analiz eder veya oluşturur                                 | [Image Generation](/tr/tools/image-generation) |
| `music_generate`                           | Müzik parçaları oluşturur                                             | [Music Generation](/tools/music-generation) |
| `video_generate`                           | Videolar oluşturur                                                    | [Video Generation](/tools/video-generation) |
| `tts`                                      | Tek seferlik metinden konuşmaya dönüştürme                            | [TTS](/tr/tools/tts)                           |
| `sessions_*` / `subagents` / `agents_list` | Oturum yönetimi, durum ve alt agent orkestrasyonu                     | [Sub-agents](/tr/tools/subagents)              |
| `session_status`                           | Hafif `/status` tarzı geri okuma ve oturum model geçersiz kılması     | [Session Tools](/tr/concepts/session-tool)     |

Görsel işleri için analizde `image`, oluşturmada veya düzenlemede `image_generate` kullanın. `openai/*`, `google/*`, `fal/*` veya varsayılan olmayan başka bir görsel provider’ı hedefliyorsanız, önce o provider’ın auth/API anahtarını yapılandırın.

Müzik işleri için `music_generate` kullanın. `google/*`, `minimax/*` veya varsayılan olmayan başka bir müzik provider’ı hedefliyorsanız, önce o provider’ın auth/API anahtarını yapılandırın.

Video işleri için `video_generate` kullanın. `qwen/*` veya varsayılan olmayan başka bir video provider’ı hedefliyorsanız, önce o provider’ın auth/API anahtarını yapılandırın.

İş akışı odaklı ses üretimi için, ComfyUI gibi bir plugin bunu kaydettiğinde
`music_generate` kullanın. Bu, metinden konuşmaya olan `tts`’den ayrıdır.

`session_status`, sessions grubundaki hafif durum/geri okuma aracıdır.
Geçerli oturum hakkında `/status` tarzı soruları yanıtlar ve isteğe bağlı olarak
oturum başına model geçersiz kılması ayarlayabilir; `model=default` bu
geçersiz kılmayı temizler. `/status` gibi, en son transcript kullanım girdisinden
seyrek token/cache sayaçlarını ve etkin çalışma zamanı model etiketini geriye dönük doldurabilir.

`gateway`, gateway işlemleri için yalnızca sahip tarafından kullanılabilen çalışma zamanı aracıdır:

- Düzenlemelerden önce tek bir yol kapsamlı config alt ağacı için `config.schema.lookup`
- Geçerli config snapshot’ı + hash için `config.get`
- Yeniden başlatmalı kısmi config güncellemeleri için `config.patch`
- Yalnızca tam config değiştirme için `config.apply`
- Açık self-update + yeniden başlatma için `update.run`

Kısmi değişikliklerde önce `config.schema.lookup`, sonra `config.patch` tercih edin.
`config.apply` yalnızca tüm config’i bilerek değiştirdiğinizde kullanılmalıdır.
Araç ayrıca `tools.exec.ask` veya `tools.exec.security` değerlerini değiştirmeyi reddeder;
eski `tools.bash.*` takma adları aynı korumalı exec yollarına normalize edilir.

### Plugin tarafından sağlanan araçlar

Plugin’ler ek araçlar kaydedebilir. Bazı örnekler:

- [Lobster](/tr/tools/lobster) — devam ettirilebilir onaylarla tiplenmiş iş akışı çalışma zamanı
- [LLM Task](/tr/tools/llm-task) — yapılandırılmış çıktı için yalnızca JSON LLM adımı
- [Music Generation](/tools/music-generation) — iş akışı destekli provider’larla paylaşılan `music_generate` aracı
- [Diffs](/tr/tools/diffs) — diff görüntüleyici ve oluşturucu
- [OpenProse](/tr/prose) — markdown-first iş akışı orkestrasyonu

## Araç yapılandırması

### İzin ve engelleme listeleri

Agent’ın hangi araçları çağırabileceğini config içindeki `tools.allow` / `tools.deny`
ile denetleyin. Engelleme her zaman izne üstün gelir.

```json5
{
  tools: {
    allow: ["group:fs", "browser", "web_search"],
    deny: ["exec"],
  },
}
```

### Araç profilleri

`tools.profile`, `allow`/`deny` uygulanmadan önce temel bir izin listesi ayarlar.
Agent başına geçersiz kılma: `agents.list[].tools.profile`.

| Profil      | Neleri içerir                                                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `full`      | Kısıtlama yok (ayarlanmamış olmasıyla aynı)                                                                                                       |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `music_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                                        |
| `minimal`   | Yalnızca `session_status`                                                                                                                         |

### Araç grupları

İzin/engelleme listelerinde `group:*` kısa yollarını kullanın:

| Grup               | Araçlar                                                                                                   |
| ------------------ | --------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | exec, process, code_execution (`bash`, `exec` için bir takma ad olarak kabul edilir)                     |
| `group:fs`         | read, write, edit, apply_patch                                                                            |
| `group:sessions`   | sessions_list, sessions_history, sessions_send, sessions_spawn, sessions_yield, subagents, session_status |
| `group:memory`     | memory_search, memory_get                                                                                 |
| `group:web`        | web_search, x_search, web_fetch                                                                           |
| `group:ui`         | browser, canvas                                                                                           |
| `group:automation` | cron, gateway                                                                                             |
| `group:messaging`  | message                                                                                                   |
| `group:nodes`      | nodes                                                                                                     |
| `group:agents`     | agents_list                                                                                               |
| `group:media`      | image, image_generate, music_generate, video_generate, tts                                                |
| `group:openclaw`   | Tüm yerleşik OpenClaw araçları (plugin araçları hariç)                                                    |

`sessions_history`, sınırlı ve güvenlik filtreli bir geri çağırma görünümü döndürür.  
Thinking etiketlerini, `<relevant-memories>` iskeletini, düz metin tool-call XML
yüklerini (şunlar dahil: `<tool_call>...</tool_call>`,
`<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`,
`<function_calls>...</function_calls>` ve kesilmiş tool-call blokları),
seviyesi düşürülmüş tool-call iskeletini, sızmış ASCII/tam genişlikli model kontrol
token’larını ve assistant metnindeki bozuk MiniMax tool-call XML’ini ayıklar; ardından
ham transcript dökümü gibi davranmak yerine redaksiyon/kısaltma ve olası büyük satır
yer tutucuları uygular.

### Provider’a özgü kısıtlamalar

Global varsayılanları değiştirmeden belirli provider’lar için araçları kısıtlamak üzere
`tools.byProvider` kullanın:

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```
