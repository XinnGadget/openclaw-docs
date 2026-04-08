---
read_when:
    - Heartbeat ritmini veya mesajlaşmasını ayarlarken
    - Zamanlanmış görevler için heartbeat ile cron arasında karar verirken
summary: Heartbeat yoklama mesajları ve bildirim kuralları
title: Heartbeat
x-i18n:
    generated_at: "2026-04-08T02:15:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: a8021d747637060eacb91ec5f75904368a08790c19f4fca32acda8c8c0a25e41
    source_path: gateway/heartbeat.md
    workflow: 15
---

# Heartbeat (Gateway)

> **Heartbeat mi Cron mu?** Hangisinin ne zaman kullanılacağına ilişkin yönlendirme için [Otomasyon ve Görevler](/tr/automation) bölümüne bakın.

Heartbeat, modeli size spam yapmadan dikkat gerektiren her şeyi
ortaya çıkarabilsin diye ana oturumda **düzenli aracı dönüşleri** çalıştırır.

Heartbeat, zamanlanmış bir ana oturum dönüşüdür — [arka plan görevi](/tr/automation/tasks) kaydı **oluşturmaz**.
Görev kayıtları, ayrık işler içindir (ACP çalıştırmaları, alt aracılar, yalıtılmış cron işleri).

Sorun giderme: [Zamanlanmış Görevler](/tr/automation/cron-jobs#troubleshooting)

## Hızlı başlangıç (başlangıç seviyesi)

1. Heartbeat'i etkin bırakın (varsayılan `30m`, Anthropic OAuth/token kimlik doğrulaması için `1h`, buna Claude CLI yeniden kullanımı da dahildir) veya kendi ritminizi ayarlayın.
2. Aracı çalışma alanında küçük bir `HEARTBEAT.md` kontrol listesi ya da `tasks:` bloğu oluşturun (isteğe bağlı ama önerilir).
3. Heartbeat mesajlarının nereye gideceğine karar verin (varsayılan `target: "none"` değeridir; son kişiye yönlendirmek için `target: "last"` ayarlayın).
4. İsteğe bağlı: saydamlık için heartbeat muhakeme teslimini etkinleştirin.
5. İsteğe bağlı: heartbeat çalıştırmalarının yalnızca `HEARTBEAT.md` dosyasına ihtiyacı varsa hafif bootstrap bağlamı kullanın.
6. İsteğe bağlı: her heartbeat'te tam konuşma geçmişinin gönderilmesini önlemek için yalıtılmış oturumları etkinleştirin.
7. İsteğe bağlı: heartbeat'leri etkin saatlerle sınırlayın (yerel saat).

Örnek yapılandırma:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // son kişiye açık teslim (varsayılan "none")
        directPolicy: "allow", // varsayılan: doğrudan/DM hedeflerine izin ver; bastırmak için "block" ayarla
        lightContext: true, // isteğe bağlı: bootstrap dosyalarından yalnızca HEARTBEAT.md enjekte edilir
        isolatedSession: true, // isteğe bağlı: her çalıştırmada yeni oturum (konuşma geçmişi yok)
        // activeHours: { start: "08:00", end: "24:00" },
        // includeReasoning: true, // isteğe bağlı: ayrı `Reasoning:` mesajını da gönder
      },
    },
  },
}
```

## Varsayılanlar

- Aralık: `30m` (veya algılanan kimlik doğrulama modu Anthropic OAuth/token kimlik doğrulaması olduğunda `1h`; buna Claude CLI yeniden kullanımı da dahildir). `agents.defaults.heartbeat.every` ya da aracı başına `agents.list[].heartbeat.every` ayarlayın; devre dışı bırakmak için `0m` kullanın.
- İstem gövdesi (`agents.defaults.heartbeat.prompt` ile yapılandırılabilir):
  `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
- Heartbeat istemi, kullanıcı mesajı olarak **aynen** gönderilir. Sistem
  istemi yalnızca varsayılan aracı için heartbeat etkin olduğunda
  ve çalışma dahili olarak işaretlendiğinde bir “Heartbeat” bölümü içerir.
- Heartbeat `0m` ile devre dışı bırakıldığında, normal çalıştırmalar da `HEARTBEAT.md`
  dosyasını bootstrap bağlamına eklemez; böylece model yalnızca heartbeat'e özel yönergeleri görmez.
- Etkin saatler (`heartbeat.activeHours`) yapılandırılan saat diliminde denetlenir.
  Pencerenin dışında heartbeat'ler, pencere içindeki sonraki tik gelene kadar atlanır.

## Heartbeat istemi ne içindir

Varsayılan istem bilinçli olarak geniş tutulmuştur:

- **Arka plan görevleri**: “Consider outstanding tasks” ifadesi, aracıyı
  takipleri (gelen kutusu, takvim, hatırlatıcılar, kuyruktaki işler) gözden geçirmeye ve acil olanları öne çıkarmaya yönlendirir.
- **İnsanla yoklama**: “Checkup sometimes on your human during day time” ifadesi,
  ara sıra hafif bir “bir şeye ihtiyacın var mı?” mesajını teşvik eder, ancak
  yapılandırılmış yerel saat diliminizi kullanarak gece spam'ini önler (bkz. [/concepts/timezone](/tr/concepts/timezone)).

Heartbeat, tamamlanan [arka plan görevlerine](/tr/automation/tasks) tepki verebilir, ancak heartbeat çalıştırmasının kendisi bir görev kaydı oluşturmaz.

Bir heartbeat'in çok belirli bir şey yapmasını istiyorsanız (ör. “Gmail PubSub
istatistiklerini kontrol et” veya “gateway sağlığını doğrula”), `agents.defaults.heartbeat.prompt` değerini (veya
`agents.list[].heartbeat.prompt`) özel bir gövdeye ayarlayın (aynen gönderilir).

## Yanıt sözleşmesi

- Dikkat gerektiren bir şey yoksa **`HEARTBEAT_OK`** ile yanıt verin.
- Heartbeat çalıştırmaları sırasında OpenClaw, `HEARTBEAT_OK` ifadesi yanıtın **başında veya sonunda**
  göründüğünde bunu bir onay olarak değerlendirir. Kalan içerik **≤ `ackMaxChars`** ise
  (varsayılan: 300), bu belirteç çıkarılır ve yanıt
  bırakılır.
- `HEARTBEAT_OK` bir yanıtın **ortasında** görünürse, özel
  olarak ele alınmaz.
- Uyarılar için **`HEARTBEAT_OK` eklemeyin**; yalnızca uyarı metnini döndürün.

Heartbeat dışında, bir mesajın başında/sonunda bulunan başıboş `HEARTBEAT_OK`
çıkarılır ve günlüğe yazılır; yalnızca `HEARTBEAT_OK` olan bir mesaj bırakılır.

## Yapılandırma

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // varsayılan: 30m (0m devre dışı bırakır)
        model: "anthropic/claude-opus-4-6",
        includeReasoning: false, // varsayılan: false (varsa ayrı bir Reasoning: mesajı gönderilir)
        lightContext: false, // varsayılan: false; true ise çalışma alanı bootstrap dosyalarından yalnızca HEARTBEAT.md tutulur
        isolatedSession: false, // varsayılan: false; true ise her heartbeat yeni bir oturumda çalışır (konuşma geçmişi yok)
        target: "last", // varsayılan: none | seçenekler: last | none | <kanal id> (çekirdek veya plugin, ör. "bluebubbles")
        to: "+15551234567", // isteğe bağlı kanala özgü geçersiz kılma
        accountId: "ops-bot", // isteğe bağlı çok hesaplı kanal kimliği
        prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        ackMaxChars: 300, // HEARTBEAT_OK sonrasında izin verilen en fazla karakter
      },
    },
  },
}
```

### Kapsam ve öncelik

- `agents.defaults.heartbeat`, genel heartbeat davranışını ayarlar.
- `agents.list[].heartbeat`, bunun üzerine birleştirilir; herhangi bir aracıda `heartbeat` bloğu varsa heartbeat yalnızca **bu aracılarda** çalışır.
- `channels.defaults.heartbeat`, tüm kanallar için görünürlük varsayılanlarını ayarlar.
- `channels.<channel>.heartbeat`, kanal varsayılanlarını geçersiz kılar.
- `channels.<channel>.accounts.<id>.heartbeat` (çok hesaplı kanallar) kanal başına ayarları geçersiz kılar.

### Aracı başına heartbeat

Herhangi bir `agents.list[]` girdisi `heartbeat` bloğu içeriyorsa, heartbeat
yalnızca **bu aracılarda** çalışır. Aracı başına blok, `agents.defaults.heartbeat`
üzerine birleştirilir (böylece ortak varsayılanları bir kez ayarlayıp aracı bazında geçersiz kılabilirsiniz).

Örnek: iki aracı, heartbeat yalnızca ikinci aracıda çalışır.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // son kişiye açık teslim (varsayılan "none")
      },
    },
    list: [
      { id: "main", default: true },
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "whatsapp",
          to: "+15551234567",
          prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        },
      },
    ],
  },
}
```

### Etkin saatler örneği

Belirli bir saat diliminde heartbeat'leri mesai saatleriyle sınırlayın:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // son kişiye açık teslim (varsayılan "none")
        activeHours: {
          start: "09:00",
          end: "22:00",
          timezone: "America/New_York", // isteğe bağlı; ayarlıysa userTimezone kullanılır, aksi halde ana makine saat dilimi
        },
      },
    },
  },
}
```

Bu pencerenin dışında (Doğu saatine göre sabah 9'dan önce veya akşam 10'dan sonra), heartbeat'ler atlanır. Pencere içindeki bir sonraki zamanlanmış tik normal şekilde çalışır.

### 7/24 kurulum

Heartbeat'lerin gün boyu çalışmasını istiyorsanız şu kalıplardan birini kullanın:

- `activeHours` değerini tamamen çıkarın (zaman penceresi kısıtlaması yoktur; varsayılan davranış budur).
- Tam günlük bir pencere ayarlayın: `activeHours: { start: "00:00", end: "24:00" }`.

Aynı `start` ve `end` zamanını ayarlamayın (örneğin `08:00` ile `08:00`).
Bu, sıfır genişlikte bir pencere olarak değerlendirilir; bu nedenle heartbeat'ler her zaman atlanır.

### Çok hesaplı örnek

Telegram gibi çok hesaplı kanallarda belirli bir hesabı hedeflemek için `accountId` kullanın:

```json5
{
  agents: {
    list: [
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "telegram",
          to: "12345678:topic:42", // isteğe bağlı: belirli bir konuya/ileti dizisine yönlendir
          accountId: "ops-bot",
        },
      },
    ],
  },
  channels: {
    telegram: {
      accounts: {
        "ops-bot": { botToken: "YOUR_TELEGRAM_BOT_TOKEN" },
      },
    },
  },
}
```

### Alan notları

- `every`: heartbeat aralığı (süre dizesi; varsayılan birim = dakika).
- `model`: heartbeat çalıştırmaları için isteğe bağlı model geçersiz kılması (`provider/model`).
- `includeReasoning`: etkinleştirildiğinde, varsa ayrı `Reasoning:` mesajını da gönderir (`/reasoning on` ile aynı biçim).
- `lightContext`: true olduğunda, heartbeat çalıştırmaları hafif bootstrap bağlamı kullanır ve çalışma alanı bootstrap dosyalarından yalnızca `HEARTBEAT.md` tutulur.
- `isolatedSession`: true olduğunda, her heartbeat önceki konuşma geçmişi olmadan yeni bir oturumda çalışır. Cron `sessionTarget: "isolated"` ile aynı yalıtım kalıbını kullanır. Heartbeat başına token maliyetini ciddi ölçüde azaltır. En yüksek tasarruf için `lightContext: true` ile birleştirin. Teslim yönlendirmesi yine ana oturum bağlamını kullanır.
- `session`: heartbeat çalıştırmaları için isteğe bağlı oturum anahtarı.
  - `main` (varsayılan): aracı ana oturumu.
  - Açık oturum anahtarı (`openclaw sessions --json` veya [sessions CLI](/cli/sessions) çıktısından kopyalayın).
  - Oturum anahtarı biçimleri için bkz. [Sessions](/tr/concepts/session) ve [Groups](/tr/channels/groups).
- `target`:
  - `last`: son kullanılan harici kanala gönder.
  - açık kanal: `discord`, `matrix`, `telegram` veya `whatsapp` gibi yapılandırılmış herhangi bir kanal veya plugin kimliği.
  - `none` (varsayılan): heartbeat'i çalıştır ama harici olarak **gönderme**.
- `directPolicy`: doğrudan/DM teslim davranışını kontrol eder:
  - `allow` (varsayılan): doğrudan/DM heartbeat teslimine izin verir.
  - `block`: doğrudan/DM teslimi bastırır (`reason=dm-blocked`).
- `to`: isteğe bağlı alıcı geçersiz kılması (kanala özgü kimlik; ör. WhatsApp için E.164 veya Telegram sohbet kimliği). Telegram konuları/ileti dizileri için `<chatId>:topic:<messageThreadId>` kullanın.
- `accountId`: çok hesaplı kanallar için isteğe bağlı hesap kimliği. `target: "last"` olduğunda, hesap kimliği destekliyorsa çözümlenen son kanala uygulanır; aksi halde yok sayılır. Hesap kimliği, çözümlenen kanal için yapılandırılmış bir hesapla eşleşmezse teslim atlanır.
- `prompt`: varsayılan istem gövdesini geçersiz kılar (birleştirilmez).
- `ackMaxChars`: `HEARTBEAT_OK` sonrasında teslimden önce izin verilen en fazla karakter.
- `suppressToolErrorWarnings`: true olduğunda, heartbeat çalıştırmaları sırasında araç hata uyarısı yüklerini bastırır.
- `activeHours`: heartbeat çalıştırmalarını bir zaman penceresiyle sınırlar. `start` (HH:MM, dahil; gün başlangıcı için `00:00` kullanın), `end` (HH:MM, hariç; gün sonu için `24:00` kullanılabilir) ve isteğe bağlı `timezone` içeren nesne.
  - Çıkarılırsa veya `"user"` ise: ayarlıysa `agents.defaults.userTimezone` kullanılır, aksi halde ana sistem saat dilimine düşülür.
  - `"local"`: her zaman ana sistem saat dilimini kullanır.
  - Herhangi bir IANA tanımlayıcısı (ör. `America/New_York`): doğrudan kullanılır; geçersizse yukarıdaki `"user"` davranışına düşülür.
  - Etkin bir pencere için `start` ve `end` eşit olmamalıdır; eşit değerler sıfır genişlik olarak değerlendirilir (her zaman pencere dışında).
  - Etkin pencerenin dışında, heartbeat'ler pencere içindeki sonraki tike kadar atlanır.

## Teslim davranışı

- Heartbeat'ler varsayılan olarak aracının ana oturumunda çalışır (`agent:<id>:<mainKey>`),
  veya `session.scope = "global"` olduğunda `global` içinde. Bunu belirli bir
  kanal oturumuna (Discord/WhatsApp/vb.) geçirmek için `session` ayarlayın.
- `session` yalnızca çalışma bağlamını etkiler; teslim `target` ve `to` ile kontrol edilir.
- Belirli bir kanal/alıcıya teslim etmek için `target` + `to` ayarlayın.
  `target: "last"` ile teslim, bu oturum için son harici kanalı kullanır.
- Heartbeat teslimleri varsayılan olarak doğrudan/DM hedeflerine izin verir. Doğrudan hedeflere gönderimi bastırırken heartbeat dönüşünü yine de çalıştırmak için `directPolicy: "block"` ayarlayın.
- Ana kuyruk meşgulse, heartbeat atlanır ve daha sonra yeniden denenir.
- `target`, hiçbir harici hedefe çözülmezse çalışma yine gerçekleşir, ancak
  giden mesaj gönderilmez.
- `showOk`, `showAlerts` ve `useIndicator` değerlerinin tümü devre dışıysa, çalışma en başta `reason=alerts-disabled` olarak atlanır.
- Yalnızca uyarı teslimi devre dışıysa, OpenClaw heartbeat'i yine de çalıştırabilir, zamanı gelen görev zaman damgalarını güncelleyebilir, oturum boşta zaman damgasını geri yükleyebilir ve dışa dönük uyarı yükünü bastırabilir.
- Yalnızca heartbeat yanıtları oturumu canlı tutmaz; son `updatedAt`
  geri yüklenir, böylece boşta kalma süresi dolumu normal davranır.
- Ayrık [arka plan görevleri](/tr/automation/tasks), ana oturumun bir şeyi hızlıca fark etmesi gerektiğinde sistem olayı kuyruğa alıp heartbeat'i uyandırabilir. Bu uyandırma, heartbeat çalıştırmasını arka plan görevi yapmaz.

## Görünürlük denetimleri

Varsayılan olarak, `HEARTBEAT_OK` onayları bastırılırken uyarı içeriği
teslim edilir. Bunu kanal veya hesap bazında ayarlayabilirsiniz:

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false # HEARTBEAT_OK öğesini gizle (varsayılan)
      showAlerts: true # Uyarı mesajlarını göster (varsayılan)
      useIndicator: true # Gösterge olayları yay (varsayılan)
  telegram:
    heartbeat:
      showOk: true # Telegram'da OK onaylarını göster
  whatsapp:
    accounts:
      work:
        heartbeat:
          showAlerts: false # Bu hesap için uyarı teslimini bastır
```

Öncelik: hesap başına → kanal başına → kanal varsayılanları → yerleşik varsayılanlar.

### Her bayrak ne yapar

- `showOk`: model yalnızca OK içeren bir yanıt döndürdüğünde `HEARTBEAT_OK` onayı gönderir.
- `showAlerts`: model OK olmayan bir yanıt döndürdüğünde uyarı içeriğini gönderir.
- `useIndicator`: UI durum yüzeyleri için gösterge olayları yayar.

**Üçü de** false ise OpenClaw heartbeat çalıştırmasını tamamen atlar (model çağrısı yok).

### Kanal başına ve hesap başına örnekler

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false
      showAlerts: true
      useIndicator: true
  slack:
    heartbeat:
      showOk: true # tüm Slack hesapları
    accounts:
      ops:
        heartbeat:
          showAlerts: false # yalnızca ops hesabı için uyarıları bastır
  telegram:
    heartbeat:
      showOk: true
```

### Yaygın kalıplar

| Amaç | Yapılandırma |
| ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| Varsayılan davranış (sessiz OK'ler, uyarılar açık) | _(yapılandırma gerekmez)_ |
| Tamamen sessiz (mesaj yok, gösterge yok) | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: false }` |
| Yalnızca gösterge (mesaj yok) | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: true }` |
| Yalnızca tek bir kanalda OK'ler | `channels.telegram.heartbeat: { showOk: true }` |

## HEARTBEAT.md (isteğe bağlı)

Çalışma alanında `HEARTBEAT.md` dosyası varsa, varsayılan istem aracıya onu
okumasını söyler. Bunu “heartbeat kontrol listeniz” olarak düşünün: küçük, sabit
ve her 30 dakikada bir eklenmesi güvenli.

Normal çalıştırmalarda, `HEARTBEAT.md` yalnızca varsayılan aracı için heartbeat yönergesi
etkin olduğunda enjekte edilir. Heartbeat ritmini `0m` ile devre dışı bırakmak veya
`includeSystemPromptSection: false` ayarlamak, bunu normal bootstrap
bağlamından çıkarır.

`HEARTBEAT.md` dosyası varsa ancak fiilen boşsa (yalnızca boş satırlar ve `# Heading`
gibi markdown başlıkları içeriyorsa), OpenClaw API çağrılarını azaltmak için heartbeat çalıştırmasını atlar.
Bu atlama `reason=empty-heartbeat-file` olarak bildirilir.
Dosya yoksa heartbeat yine çalışır ve model ne yapılacağına karar verir.

İstem şişmesini önlemek için dosyayı küçük tutun (kısa kontrol listesi veya hatırlatıcılar).

Örnek `HEARTBEAT.md`:

```md
# Heartbeat kontrol listesi

- Hızlı tarama: gelen kutularında acil bir şey var mı?
- Gündüzse ve bekleyen başka bir şey yoksa hafif bir yoklama yap.
- Bir görev engelliyse _neyin eksik olduğunu_ yaz ve bir dahaki sefere Peter'a sor.
```

### `tasks:` blokları

`HEARTBEAT.md`, heartbeat içinde aralık tabanlı kontroller için küçük, yapılandırılmış bir `tasks:`
bloğunu da destekler.

Örnek:

```md
tasks:

- name: inbox-triage
  interval: 30m
  prompt: "Check for urgent unread emails and flag anything time sensitive."
- name: calendar-scan
  interval: 2h
  prompt: "Check for upcoming meetings that need prep or follow-up."

# Ek yönergeler

- Uyarıları kısa tut.
- Zamanı gelen tüm görevlerden sonra dikkat gerektiren bir şey yoksa HEARTBEAT_OK ile yanıt ver.
```

Davranış:

- OpenClaw, `tasks:` bloğunu ayrıştırır ve her görevi kendi `interval` değerine göre denetler.
- Yalnızca zamanı **gelmiş** görevler, o tik için heartbeat istemine eklenir.
- Zamanı gelen görev yoksa, boşa model çağrısı yapılmaması için heartbeat tamamen atlanır (`reason=no-tasks-due`).
- `HEARTBEAT.md` içindeki görev olmayan içerik korunur ve zamanı gelen görev listesinden sonra ek bağlam olarak eklenir.
- Görev son çalıştırma zaman damgaları oturum durumunda (`heartbeatTaskState`) saklanır; bu nedenle aralıklar normal yeniden başlatmalarda korunur.
- Görev zaman damgaları yalnızca bir heartbeat çalıştırması normal yanıt yolunu tamamladıktan sonra ilerletilir. Atlanan `empty-heartbeat-file` / `no-tasks-due` çalıştırmaları görevleri tamamlanmış olarak işaretlemez.

Görev modu, tek bir heartbeat dosyasında birkaç düzenli kontrol tutmak istediğinizde ancak her tikte bunların tümü için ödeme yapmak istemediğinizde kullanışlıdır.

### Aracı HEARTBEAT.md dosyasını güncelleyebilir mi?

Evet — ona bunu söylerseniz.

`HEARTBEAT.md`, aracı çalışma alanındaki normal bir dosyadır; bu nedenle aracıya
(normal bir sohbette) şuna benzer bir şey söyleyebilirsiniz:

- “Günlük takvim kontrolü eklemek için `HEARTBEAT.md` dosyasını güncelle.”
- “`HEARTBEAT.md` dosyasını daha kısa ve gelen kutusu takiplerine odaklı olacak şekilde yeniden yaz.”

Bunun proaktif olarak gerçekleşmesini istiyorsanız, heartbeat isteminize şu gibi açık bir satır da ekleyebilirsiniz: “Kontrol listesi bayatlarsa daha iyisiyle HEARTBEAT.md dosyasını güncelle.”

Güvenlik notu: gizli bilgileri (API anahtarları, telefon numaraları, özel token'lar) `HEARTBEAT.md`
dosyasına koymayın — istem bağlamının parçası haline gelir.

## Elle uyandırma (isteğe bağlı)

Aşağıdaki komutla bir sistem olayı kuyruğa alabilir ve anında heartbeat tetikleyebilirsiniz:

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
```

Birden fazla aracıda `heartbeat` yapılandırılmışsa, elle uyandırma bu
aracı heartbeat'lerinin her birini hemen çalıştırır.

Bir sonraki zamanlanmış tiki beklemek için `--mode next-heartbeat` kullanın.

## Muhakeme teslimi (isteğe bağlı)

Varsayılan olarak heartbeat'ler yalnızca son “yanıt” yükünü teslim eder.

Saydamlık istiyorsanız şunu etkinleştirin:

- `agents.defaults.heartbeat.includeReasoning: true`

Etkinleştirildiğinde, heartbeat'ler ayrıca başında
`Reasoning:` bulunan ayrı bir mesaj da teslim eder (`/reasoning on` ile aynı biçim). Bu, aracı
birden fazla oturumu/codex'i yönetirken size neden sizi dürtmeye karar verdiğini görmek istediğinizde yararlı olabilir
— ancak isteyeceğinizden daha fazla dahili ayrıntı da sızdırabilir. Grup sohbetlerinde
bunu kapalı tutmayı tercih edin.

## Maliyet farkındalığı

Heartbeat'ler tam aracı dönüşleri çalıştırır. Daha kısa aralıklar daha çok token tüketir. Maliyeti azaltmak için:

- Tam konuşma geçmişini göndermemek için `isolatedSession: true` kullanın (çalıştırma başına ~100K token'dan ~2-5K'ya düşer).
- Bootstrap dosyalarını yalnızca `HEARTBEAT.md` ile sınırlamak için `lightContext: true` kullanın.
- Daha ucuz bir `model` ayarlayın (ör. `ollama/llama3.2:1b`).
- `HEARTBEAT.md` dosyasını küçük tutun.
- Yalnızca dahili durum güncellemeleri istiyorsanız `target: "none"` kullanın.

## İlgili

- [Otomasyon ve Görevler](/tr/automation) — tüm otomasyon mekanizmalarına hızlı bakış
- [Arka Plan Görevleri](/tr/automation/tasks) — ayrık işlerin nasıl izlendiği
- [Saat Dilimi](/tr/concepts/timezone) — saat diliminin heartbeat zamanlamasını nasıl etkilediği
- [Sorun Giderme](/tr/automation/cron-jobs#troubleshooting) — otomasyon sorunlarını ayıklama
