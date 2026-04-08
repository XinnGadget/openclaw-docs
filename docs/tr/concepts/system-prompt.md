---
read_when:
    - Sistem istemi metnini, araç listesini veya zaman/nabız bölümlerini düzenleme
    - Çalışma alanı bootstrap davranışını veya Skills ekleme davranışını değiştirme
summary: OpenClaw sistem isteminin neler içerdiği ve nasıl oluşturulduğu
title: Sistem İstemi
x-i18n:
    generated_at: "2026-04-08T02:14:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: e55fc886bc8ec47584d07c9e60dfacd964dc69c7db976ea373877dc4fe09a79a
    source_path: concepts/system-prompt.md
    workflow: 15
---

# Sistem İstemi

OpenClaw her ajan çalıştırması için özel bir sistem istemi oluşturur. İstem **OpenClaw'a aittir** ve pi-coding-agent varsayılan istemini kullanmaz.

İstem, OpenClaw tarafından oluşturulur ve her ajan çalıştırmasına eklenir.

Sağlayıcı eklentileri, OpenClaw'a ait tam istemi değiştirmeden önbellek farkında istem rehberliği sağlayabilir. Sağlayıcı çalışma zamanı şunları yapabilir:

- adlandırılmış küçük bir temel bölüm kümesini değiştirebilir (`interaction_style`,
  `tool_call_style`, `execution_bias`)
- istem önbelleği sınırının üstüne **kararlı bir önek** ekleyebilir
- istem önbelleği sınırının altına **dinamik bir sonek** ekleyebilir

Model ailesine özel ince ayar için sağlayıcıya ait katkıları kullanın. Eski
`before_prompt_build` istem mutasyonunu, normal sağlayıcı davranışı için değil;
uyumluluk veya gerçekten genel istem değişiklikleri için kullanın.

## Yapı

İstem bilerek kompakt tutulur ve sabit bölümler kullanır:

- **Araçlar**: yapılandırılmış araç için tek doğru kaynak hatırlatması ve çalışma zamanı araç kullanım rehberliği.
- **Güvenlik**: güç arayan davranışlardan veya gözetimi atlamaktan kaçınmaya yönelik kısa korkuluk hatırlatması.
- **Skills** (var olduğunda): modele gerektiğinde skill yönergelerini nasıl yükleyeceğini söyler.
- **OpenClaw Self-Update**: yapılandırmayı güvenli şekilde `config.schema.lookup` ile nasıl inceleyeceğiniz, yapılandırmayı `config.patch` ile nasıl yamalayacağınız, tam yapılandırmayı `config.apply` ile nasıl değiştireceğiniz ve `update.run` komutunun yalnızca açık kullanıcı isteğiyle nasıl çalıştırılacağı. Yalnızca sahip tarafından kullanılabilen `gateway` aracı ayrıca `tools.exec.ask` / `tools.exec.security` yollarını ve bunlara normalize olan eski `tools.bash.*` takma adlarını yeniden yazmayı reddeder.
- **Workspace**: çalışma dizini (`agents.defaults.workspace`).
- **Documentation**: OpenClaw belgelerinin yerel yolu (repo veya npm paketi) ve ne zaman okunması gerektiği.
- **Workspace Files (injected)**: bootstrap dosyalarının aşağıda dahil edildiğini belirtir.
- **Sandbox** (etkin olduğunda): sandbox'lı çalışma zamanını, sandbox yollarını ve yükseltilmiş exec kullanımının mevcut olup olmadığını belirtir.
- **Current Date & Time**: kullanıcı yerel saati, saat dilimi ve saat biçimi.
- **Reply Tags**: desteklenen sağlayıcılar için isteğe bağlı yanıt etiketi sözdizimi.
- **Heartbeats**: varsayılan ajan için heartbeats etkin olduğunda heartbeat istemi ve ack davranışı.
- **Runtime**: ana makine, işletim sistemi, node, model, repo kökü (algılanırsa), düşünme seviyesi (tek satır).
- **Reasoning**: mevcut görünürlük seviyesi + /reasoning geçiş ipucu.

Araçlar bölümü ayrıca uzun süren işler için çalışma zamanı rehberliği de içerir:

- gelecekteki takipler için cron kullanın (`daha sonra tekrar kontrol et`, hatırlatmalar, yinelenen işler); `exec` uyku döngüleri, `yieldMs` gecikme hileleri veya tekrarlanan `process` yoklaması yerine
- `exec` / `process` araçlarını yalnızca hemen başlayan ve arka planda çalışmaya devam eden komutlar için kullanın
- otomatik tamamlanma uyandırması etkin olduğunda, komutu bir kez başlatın ve çıktı verdiğinde veya başarısız olduğunda push tabanlı uyandırma yoluna güvenin
- çalışan bir komutu incelemeniz gerektiğinde günlükler, durum, girdi veya müdahale için `process` kullanın
- görev daha büyükse `sessions_spawn` tercih edin; alt ajan tamamlama push tabanlıdır ve istekte bulunana otomatik olarak geri bildirilir
- yalnızca tamamlanmayı beklemek için `subagents list` / `sessions_list` araçlarını bir döngü içinde yoklamayın

Deneysel `update_plan` aracı etkin olduğunda, Araçlar bölümü modele ayrıca bunu yalnızca önemsiz olmayan çok adımlı işler için kullanmasını, tam olarak bir `in_progress` adımı tutmasını ve her güncellemeden sonra tüm planı tekrar etmemesini söyler.

Sistem istemindeki güvenlik korkulukları tavsiye niteliğindedir. Model davranışını yönlendirir, ancak politikayı zorunlu kılmaz. Güçlü yaptırım için araç politikası, exec onayları, sandboxing ve kanal izin listelerini kullanın; operatörler bunları tasarım gereği devre dışı bırakabilir.

Yerel onay kartları/düğmeleri olan kanallarda, çalışma zamanı istemi artık ajana önce bu yerel onay arayüzüne güvenmesini söyler. Yalnızca araç sonucu sohbet onaylarının kullanılamadığını veya tek yolun manuel onay olduğunu söylüyorsa manuel bir `/approve` komutu eklemelidir.

## İstem modları

OpenClaw, alt ajanlar için daha küçük sistem istemleri oluşturabilir. Çalışma zamanı her çalıştırma için bir
`promptMode` ayarlar (kullanıcıya dönük bir yapılandırma değildir):

- `full` (varsayılan): yukarıdaki tüm bölümleri içerir.
- `minimal`: alt ajanlar için kullanılır; **Skills**, **Memory Recall**, **OpenClaw
  Self-Update**, **Model Aliases**, **User Identity**, **Reply Tags**,
  **Messaging**, **Silent Replies** ve **Heartbeats** bölümlerini çıkarır. Araçlar, **Güvenlik**,
  Workspace, Sandbox, Current Date & Time (biliniyorsa), Runtime ve eklenmiş
  bağlam kullanılabilir olmaya devam eder.
- `none`: yalnızca temel kimlik satırını döndürür.

`promptMode=minimal` olduğunda, ek enjekte edilmiş istemler **Group Chat Context** yerine **Subagent
Context** olarak etiketlenir.

## Workspace bootstrap ekleme

Bootstrap dosyaları kırpılır ve **Project Context** altında eklenir; böylece model açık okumalara ihtiyaç duymadan kimlik ve profil bağlamını görür:

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (yalnızca yepyeni çalışma alanlarında)
- varsa `MEMORY.md`, yoksa küçük harfli yedek olarak `memory.md`

Bu dosyaların tümü, dosyaya özgü bir geçit uygulanmadıkça, her turda **bağlam penceresine eklenir**. `HEARTBEAT.md`, varsayılan ajan için heartbeats devre dışıysa veya
`agents.defaults.heartbeat.includeSystemPromptSection` false ise normal çalıştırmalarda çıkarılır. Eklenen
dosyaları kısa tutun — özellikle zamanla büyüyebilen ve beklenmedik derecede yüksek bağlam kullanımına ve daha sık sıkıştırmaya yol açabilen `MEMORY.md` dosyasını.

> **Not:** `memory/*.md` günlük dosyaları otomatik olarak **eklenmez**. Bunlara
> gerektikçe `memory_search` ve `memory_get` araçlarıyla erişilir; bu nedenle model açıkça onları okumadıkça
> bağlam penceresine dahil edilmezler.

Büyük dosyalar bir işaretçiyle kırpılır. Dosya başına azami boyut
`agents.defaults.bootstrapMaxChars` ile kontrol edilir (varsayılan: 20000). Dosyalar genelinde eklenen toplam bootstrap
içeriği `agents.defaults.bootstrapTotalMaxChars` ile sınırlandırılır
(varsayılan: 150000). Eksik dosyalar kısa bir eksik dosya işaretçisi ekler. Kırpma
oluştuğunda OpenClaw Project Context içinde bir uyarı bloğu ekleyebilir; bunu
`agents.defaults.bootstrapPromptTruncationWarning` ile kontrol edin (`off`, `once`, `always`;
varsayılan: `once`).

Alt ajan oturumları yalnızca `AGENTS.md` ve `TOOLS.md` dosyalarını ekler (alt ajan bağlamını küçük tutmak için diğer bootstrap dosyaları
filtrelenir).

İç hook'lar, eklenen bootstrap dosyalarını değiştirmek veya tamamen değiştirmek için bu adımı `agent:bootstrap` aracılığıyla kesebilir
(örneğin `SOUL.md` dosyasını alternatif bir persona ile değiştirmek gibi).

Ajanın daha az genel duyulmasını istiyorsanız, başlangıç noktası olarak
[SOUL.md Personality Guide](/tr/concepts/soul) ile başlayın.

Eklenen her dosyanın ne kadar katkı yaptığını incelemek için (ham ve eklenmiş, kırpma ve araç şeması ek yükü dahil), `/context list` veya `/context detail` kullanın. Bkz. [Context](/tr/concepts/context).

## Zaman işleme

Sistem istemi, kullanıcı saat dilimi biliniyorsa özel bir **Current Date & Time** bölümü içerir. İstem önbelleğini kararlı tutmak için artık yalnızca
**saat dilimini** içerir (dinamik saat veya saat biçimi yoktur).

Ajanın geçerli saati bilmesi gerektiğinde `session_status` kullanın; durum kartı
bir zaman damgası satırı içerir. Aynı araç isteğe bağlı olarak oturum başına model
geçersiz kılmasını da ayarlayabilir (`model=default` bunu temizler).

Şununla yapılandırın:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

Davranışın tüm ayrıntıları için [Date & Time](/tr/date-time) bölümüne bakın.

## Skills

Uygun skills mevcut olduğunda, OpenClaw her skill için **dosya yolunu** içeren
kompakt bir **kullanılabilir skills listesi** (`formatSkillsForPrompt`) ekler. İstem, modele listelenen
konumdaki SKILL.md dosyasını (çalışma alanı, yönetilen veya paketlenmiş) yüklemek için `read` kullanmasını söyler. Uygun skill yoksa
Skills bölümü çıkarılır.

Uygunluk; skill meta veri geçitlerini, çalışma zamanı ortamı/yapılandırma denetimlerini
ve `agents.defaults.skills` veya
`agents.list[].skills` yapılandırıldığında etkin ajan skill izin listesini içerir.

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

Bu, temel istemi küçük tutarken yine de hedefli skill kullanımını mümkün kılar.

## Documentation

Mevcut olduğunda sistem istemi, yerel
OpenClaw belgeler dizinine (repo çalışma alanındaki `docs/` veya paketlenmiş npm
paketi belgeleri) işaret eden bir **Documentation** bölümü de içerir ve ayrıca genel aynayı, kaynak repoyu, topluluk Discord'unu ve
skill keşfi için ClawHub'ı ([https://clawhub.ai](https://clawhub.ai)) belirtir. İstem, modelin OpenClaw davranışı, komutlar, yapılandırma veya mimari için önce yerel belgelere başvurmasını ve mümkün olduğunda
`openclaw status` komutunu kendisinin çalıştırmasını söyler (erişimi olmadığında yalnızca kullanıcıya sormalıdır).
