---
read_when:
    - ACP üzerinden kodlama harness'leri çalıştırırken
    - Mesajlaşma kanallarında konuşmaya bağlı ACP oturumları kurarken
    - Bir mesaj kanalı konuşmasını kalıcı bir ACP oturumuna bağlarken
    - ACP backend ve plugin bağlantılarını sorun giderirken
    - Sohbetten `/acp` komutlarını kullanırken
summary: Codex, Claude Code, Cursor, Gemini CLI, OpenClaw ACP ve diğer harness aracıları için ACP çalışma zamanı oturumlarını kullanın
title: ACP Aracıları
x-i18n:
    generated_at: "2026-04-06T03:14:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 302f3fe25b1ffe0576592b6e0ad9e8a5781fa5702b31d508d9ba8908f7df33bd
    source_path: tools/acp-agents.md
    workflow: 15
---

# ACP aracıları

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/) oturumları, OpenClaw'un harici kodlama harness'lerini (örneğin Pi, Claude Code, Codex, Cursor, Copilot, OpenClaw ACP, OpenCode, Gemini CLI ve diğer desteklenen ACPX harness'leri) bir ACP backend plugin'i üzerinden çalıştırmasına olanak tanır.

OpenClaw'a doğal dille "bunu Codex'te çalıştır" veya "bir konuda Claude Code başlat" derseniz, OpenClaw bu isteği ACP çalışma zamanına yönlendirmelidir (yerel alt aracı çalışma zamanına değil). Her ACP oturum başlatması bir [arka plan görevi](/tr/automation/tasks) olarak izlenir.

Codex veya Claude Code'un mevcut OpenClaw kanal konuşmalarına doğrudan
harici bir MCP istemcisi olarak bağlanmasını istiyorsanız,
ACP yerine [`openclaw mcp serve`](/cli/mcp) kullanın.

## Hangi sayfayı istiyorum?

Birbirine karıştırılması kolay üç yakın yüzey vardır:

| Şunu yapmak istiyorsunuz...                                                           | Bunu kullanın              | Notlar                                                                                                          |
| ------------------------------------------------------------------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Codex, Claude Code, Gemini CLI veya başka bir harici harness'i OpenClaw _üzerinden_ çalıştırmak | Bu sayfa: ACP aracıları    | Sohbete bağlı oturumlar, `/acp spawn`, `sessions_spawn({ runtime: "acp" })`, arka plan görevleri, çalışma zamanı denetimleri |
| Bir OpenClaw Gateway oturumunu bir editör veya istemci için ACP sunucusu _olarak_ açığa çıkarmak | [`openclaw acp`](/cli/acp) | Köprü modu. IDE/istemci stdio/WebSocket üzerinden ACP ile OpenClaw'la konuşur                                  |

## Bu kutudan çıktığı gibi çalışıyor mu?

Genellikle evet.

- Yeni kurulumlar artık paketlenmiş `acpx` çalışma zamanı plugin'ini varsayılan olarak etkin gönderir.
- Paketlenmiş `acpx` plugin'i kendi plugin yerel sabitlenmiş `acpx` ikili dosyasını tercih eder.
- Başlangıçta OpenClaw bu ikiliyi yoklar ve gerekirse kendini onarır.
- Hızlı bir hazır olma denetimi istiyorsanız `/acp doctor` ile başlayın.

İlk kullanımda yine de olabilecekler:

- Bir hedef harness adaptörü, o harness'i ilk kez kullandığınızda isteğe bağlı olarak `npx` ile getirilebilir.
- O harness için sağlayıcı auth bilgisi yine de host üzerinde mevcut olmalıdır.
- Host'un npm/ağ erişimi yoksa, önbellekler önceden ısıtılana veya adaptör başka bir şekilde kurulana kadar ilk çalıştırma adaptör getirmeleri başarısız olabilir.

Örnekler:

- `/acp spawn codex`: OpenClaw `acpx` bootstrap etmek için hazır olmalıdır, ancak Codex ACP adaptörü yine de ilk çalıştırmada getirilmeyi gerektirebilir.
- `/acp spawn claude`: Claude ACP adaptörü için de aynı durum geçerlidir, ayrıca o host üzerindeki Claude tarafı auth gereklidir.

## Hızlı operatör akışı

Pratik bir `/acp` runbook istediğinizde bunu kullanın:

1. Bir oturum başlatın:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. Bağlı konuşmada veya konuda çalışın (veya o oturum anahtarını açıkça hedefleyin).
3. Çalışma zamanı durumunu denetleyin:
   - `/acp status`
4. Gerektiğinde çalışma zamanı seçeneklerini ayarlayın:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. Bağlamı değiştirmeden etkin bir oturuma yön verin:
   - `/acp steer günlük kaydını sıkılaştır ve devam et`
6. Çalışmayı durdurun:
   - `/acp cancel` (geçerli turu durdur), veya
   - `/acp close` (oturumu kapat + bağlamaları kaldır)

## İnsanlar için hızlı başlangıç

Doğal istek örnekleri:

- "Bu Discord kanalını Codex'e bağla."
- "Burada bir konuda kalıcı bir Codex oturumu başlat ve odaklı tut."
- "Bunu tek seferlik bir Claude Code ACP oturumu olarak çalıştır ve sonucu özetle."
- "Bu iMessage sohbetini Codex'e bağla ve takip mesajlarını aynı çalışma alanında tut."
- "Bu görev için bir konuda Gemini CLI kullan, sonra takip mesajlarını aynı konuda tut."

OpenClaw'un yapması gerekenler:

1. `runtime: "acp"` seçmek.
2. İstenen harness hedefini çözmek (`agentId`, örneğin `codex`).
3. Geçerli konuşma bağlaması istenmişse ve etkin kanal bunu destekliyorsa ACP oturumunu o konuşmaya bağlamak.
4. Aksi halde, konu bağlaması istenmişse ve geçerli kanal bunu destekliyorsa ACP oturumunu konuya bağlamak.
5. Bağlı takip mesajlarını odak kaldırılana/kapatılana/süresi dolana kadar aynı ACP oturumuna yönlendirmek.

## ACP ile alt aracılar arasındaki fark

Harici bir harness çalışma zamanı istediğinizde ACP kullanın. OpenClaw yerel devredilmiş çalıştırmalar istediğinizde alt aracıları kullanın.

| Alan          | ACP oturumu                           | Alt aracı çalıştırması                |
| ------------- | ------------------------------------- | ------------------------------------- |
| Çalışma zamanı | ACP backend plugin'i (örneğin acpx)   | OpenClaw yerel alt aracı çalışma zamanı |
| Oturum anahtarı | `agent:<agentId>:acp:<uuid>`        | `agent:<agentId>:subagent:<uuid>`     |
| Ana komutlar  | `/acp ...`                            | `/subagents ...`                      |
| Başlatma aracı | `runtime:"acp"` ile `sessions_spawn` | `sessions_spawn` (varsayılan çalışma zamanı) |

Ayrıca bkz. [Alt aracılar](/tr/tools/subagents).

## ACP, Claude Code'u nasıl çalıştırır?

ACP üzerinden Claude Code için yığın şöyledir:

1. OpenClaw ACP oturum kontrol düzlemi
2. paketlenmiş `acpx` çalışma zamanı plugin'i
3. Claude ACP adaptörü
4. Claude tarafı çalışma zamanı/oturum altyapısı

Önemli ayrım:

- ACP Claude; ACP denetimleri, oturum sürdürme, arka plan görev takibi ve isteğe bağlı konuşma/konu bağlaması olan bir harness oturumudur.
  Operatörler için pratik kural şudur:

- `/acp spawn`, bağlanabilir oturumlar, çalışma zamanı denetimleri veya kalıcı harness çalışması istiyorsanız ACP kullanın

## Bağlı oturumlar

### Geçerli konuşma bağlamaları

Geçerli konuşmanın bir alt konu oluşturmadan kalıcı bir ACP çalışma alanı olmasını istediğinizde `/acp spawn <harness> --bind here` kullanın.

Davranış:

- Kanal taşımasını, auth'u, güvenliği ve teslimatı OpenClaw yönetmeye devam eder.
- Geçerli konuşma, başlatılan ACP oturum anahtarına sabitlenir.
- Bu konuşmadaki takip mesajları aynı ACP oturumuna yönlendirilir.
- `/new` ve `/reset`, aynı bağlı ACP oturumunu yerinde sıfırlar.
- `/acp close`, oturumu kapatır ve geçerli konuşma bağlamasını kaldırır.

Bunun pratikte anlamı:

- `--bind here`, aynı sohbet yüzeyini korur. Discord'da geçerli kanal yine aynı kanal olarak kalır.
- `--bind here`, yeni çalışma başlatıyorsanız yine de yeni bir ACP oturumu oluşturabilir. Bağlama bu oturumu geçerli konuşmaya ekler.
- `--bind here`, kendi başına bir alt Discord konusu veya Telegram konusu oluşturmaz.
- ACP çalışma zamanı yine de kendi çalışma dizinine (`cwd`) veya backend tarafından yönetilen disk üzeri çalışma alanına sahip olabilir. Bu çalışma zamanı çalışma alanı sohbet yüzeyinden ayrıdır ve yeni bir mesajlaşma konusu anlamına gelmez.
- Farklı bir ACP aracısına başlatır ve `--cwd` vermezseniz, OpenClaw varsayılan olarak isteyicinin değil **hedef aracının** çalışma alanını devralır.
- Devralınan çalışma alanı yolu yoksa (`ENOENT`/`ENOTDIR`), OpenClaw yanlış ağacı sessizce yeniden kullanmak yerine backend varsayılan cwd'ye geri döner.
- Devralınan çalışma alanı varsa ama erişilemiyorsa (örneğin `EACCES`), başlatma `cwd` değerini düşürmek yerine gerçek erişim hatasını döndürür.

Zihinsel model:

- sohbet yüzeyi: insanların konuşmaya devam ettiği yer (`Discord channel`, `Telegram topic`, `iMessage chat`)
- ACP oturumu: OpenClaw'un yönlendirdiği kalıcı Codex/Claude/Gemini çalışma zamanı durumu
- alt konu/topic: yalnızca `--thread ...` tarafından oluşturulan isteğe bağlı ek mesajlaşma yüzeyi
- çalışma zamanı çalışma alanı: harness'in çalıştığı dosya sistemi konumu (`cwd`, repo checkout, backend çalışma alanı)

Örnekler:

- `/acp spawn codex --bind here`: bu sohbeti koru, bir Codex ACP oturumu başlat veya bağlan ve gelecekteki mesajları burada ona yönlendir
- `/acp spawn codex --thread auto`: OpenClaw bir alt konu/topic oluşturabilir ve ACP oturumunu oraya bağlayabilir
- `/acp spawn codex --bind here --cwd /workspace/repo`: yukarıdakiyle aynı sohbet bağlaması, ancak Codex `/workspace/repo` içinde çalışır

Geçerli konuşma bağlama desteği:

- Geçerli konuşma bağlama desteğini ilan eden sohbet/mesaj kanalları, paylaşılan konuşma bağlama yolu üzerinden `--bind here` kullanabilir.
- Özel konu/topic semantiğine sahip kanallar, aynı paylaşılan arayüzün arkasında yine de kanala özgü kanonikleştirme sağlayabilir.
- `--bind here` her zaman "geçerli konuşmayı yerinde bağla" anlamına gelir.
- Genel geçerli konuşma bağlamaları, paylaşılan OpenClaw bağlama deposunu kullanır ve normal gateway yeniden başlatmalarından sonra da kalır.

Notlar:

- `/acp spawn` üzerinde `--bind here` ile `--thread ...` birbirini dışlar.
- Discord'da `--bind here`, geçerli kanalı veya konuyu yerinde bağlar. `spawnAcpSessions`, yalnızca OpenClaw'ın `--thread auto|here` için bir alt konu oluşturması gerektiğinde gerekir.
- Etkin kanal geçerli konuşma ACP bağlamalarını açığa çıkarmıyorsa OpenClaw açık bir desteklenmiyor mesajı döndürür.
- `resume` ve "new session" soruları kanal soruları değil, ACP oturumu sorularıdır. Geçerli sohbet yüzeyini değiştirmeden çalışma zamanı durumunu yeniden kullanabilir veya değiştirebilirsiniz.

### Konuya bağlı oturumlar

Bir kanal adaptörü için konu bağlamaları etkin olduğunda, ACP oturumları konulara bağlanabilir:

- OpenClaw bir konuyu hedef ACP oturumuna bağlar.
- O konudaki takip mesajları bağlı ACP oturumuna yönlendirilir.
- ACP çıktısı aynı konuya geri teslim edilir.
- Odak kaldırma/kapatma/arşivleme/boşta zaman aşımı veya maksimum yaş dolumu bağlamayı kaldırır.

Konu bağlama desteği adaptöre özeldir. Etkin kanal adaptörü konu bağlamalarını desteklemiyorsa OpenClaw açık bir desteklenmiyor/kullanılamıyor mesajı döndürür.

Konuya bağlı ACP için gerekli özellik bayrakları:

- `acp.enabled=true`
- `acp.dispatch.enabled` varsayılan olarak açıktır (ACP dispatch'i duraklatmak için `false` ayarlayın)
- Kanal adaptörü ACP konu başlatma bayrağı etkin olmalı (adaptöre özgü)
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### Konu destekleyen kanallar

- Oturum/konu bağlama yeteneğini açığa çıkaran tüm kanal adaptörleri.
- Geçerli yerleşik destek:
  - Discord threads/channels
  - Telegram topics (gruplar/supergroup'larda forum topics ve DM topics)
- Plugin kanalları aynı bağlama arayüzü üzerinden destek ekleyebilir.

## Kanala özgü ayarlar

Geçici olmayan iş akışları için kalıcı ACP bağlamalarını üst düzey `bindings[]` girdilerinde yapılandırın.

### Bağlama modeli

- `bindings[].type="acp"` kalıcı bir ACP konuşma bağlamasını işaretler.
- `bindings[].match` hedef konuşmayı tanımlar:
  - Discord kanalı veya konusu: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Telegram forum konusu: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - BlueBubbles DM/grup sohbeti: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`  
    Kararlı grup bağlamaları için `chat_id:*` veya `chat_identifier:*` tercih edin.
  - iMessage DM/grup sohbeti: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`  
    Kararlı grup bağlamaları için `chat_id:*` tercih edin.
- `bindings[].agentId`, sahip OpenClaw aracı kimliğidir.
- İsteğe bağlı ACP geçersiz kılmaları `bindings[].acp` altında yaşar:
  - `mode` (`persistent` veya `oneshot`)
  - `label`
  - `cwd`
  - `backend`

### Aracı başına çalışma zamanı varsayılanları

Aracı başına ACP varsayılanlarını bir kez tanımlamak için `agents.list[].runtime` kullanın:

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent` (harness kimliği, örneğin `codex` veya `claude`)
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

ACP bağlı oturumları için geçersiz kılma önceliği:

1. `bindings[].acp.*`
2. `agents.list[].runtime.acp.*`
3. genel ACP varsayılanları (örneğin `acp.backend`)

Örnek:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
      {
        id: "claude",
        runtime: {
          type: "acp",
          acp: { agent: "claude", backend: "acpx", mode: "persistent" },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
    {
      type: "acp",
      agentId: "claude",
      match: {
        channel: "telegram",
        accountId: "default",
        peer: { kind: "group", id: "-1001234567890:topic:42" },
      },
      acp: { cwd: "/workspace/repo-b" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "discord", accountId: "default" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "telegram", accountId: "default" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": { requireMention: false },
          },
        },
      },
    },
    telegram: {
      groups: {
        "-1001234567890": {
          topics: { "42": { requireMention: false } },
        },
      },
    },
  },
}
```

Davranış:

- OpenClaw, yapılandırılmış ACP oturumunun kullanımdan önce var olmasını sağlar.
- O kanal veya konudaki mesajlar yapılandırılmış ACP oturumuna yönlendirilir.
- Bağlı konuşmalarda `/new` ve `/reset`, aynı ACP oturum anahtarını yerinde sıfırlar.
- Geçici çalışma zamanı bağlamaları (örneğin konu odak akışlarıyla oluşturulanlar) varsa yine uygulanır.
- Açık `cwd` verilmeden yapılan aracılar arası ACP başlatmalarında, OpenClaw aracı yapılandırmasından hedef aracı çalışma alanını devralır.
- Eksik devralınan çalışma alanı yolları backend varsayılan cwd'ye geri döner; eksik olmayan erişim hataları başlatma hataları olarak yüzeye çıkar.

## ACP oturumlarını başlatma (arayüzler)

### `sessions_spawn` içinden

Bir aracı dönüşünden veya araç çağrısından ACP oturumu başlatmak için `runtime: "acp"` kullanın.

```json
{
  "task": "Depoyu aç ve başarısız testleri özetle",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

Notlar:

- `runtime` varsayılan olarak `subagent` olur, bu nedenle ACP oturumları için açıkça `runtime: "acp"` ayarlayın.
- `agentId` atlanırsa OpenClaw, yapılandırılmışsa `acp.defaultAgent` kullanır.
- `mode: "session"`, kalıcı bağlı bir konuşmayı korumak için `thread: true` gerektirir.

Arayüz ayrıntıları:

- `task` (gerekli): ACP oturumuna gönderilen ilk istem.
- `runtime` (ACP için gerekli): `"acp"` olmalıdır.
- `agentId` (isteğe bağlı): ACP hedef harness kimliği. Ayarlıysa `acp.defaultAgent` değerine geri döner.
- `thread` (isteğe bağlı, varsayılan `false`): desteklendiği yerde konu bağlama akışı iste.
- `mode` (isteğe bağlı): `run` (tek seferlik) veya `session` (kalıcı).
  - varsayılan `run` değeridir
  - `thread: true` ve mode atlanırsa, OpenClaw çalışma zamanı yoluna göre varsayılan olarak kalıcı davranışı seçebilir
  - `mode: "session"` için `thread: true` gerekir
- `cwd` (isteğe bağlı): istenen çalışma zamanı çalışma dizini (backend/çalışma zamanı ilkesiyle doğrulanır). Atlanırsa ACP başlatma, yapılandırılmışsa hedef aracı çalışma alanını devralır; eksik devralınan yollar backend varsayılanlarına geri dönerken gerçek erişim hataları geri döndürülür.
- `label` (isteğe bağlı): oturum/banner metninde kullanılan operatör görünür etiketi.
- `resumeSessionId` (isteğe bağlı): yeni bir oturum oluşturmak yerine mevcut bir ACP oturumunu sürdür. Aracı, konuşma geçmişini `session/load` aracılığıyla yeniden oynatır. `runtime: "acp"` gerektirir.
- `streamTo` (isteğe bağlı): `"parent"`, ilk ACP çalıştırma ilerleme özetlerini sistem olayları olarak isteyici oturuma geri akıtır.
  - Kullanılabildiğinde, kabul edilen yanıtlarda tam aktarma geçmişi için tail edebileceğiniz oturum kapsamlı bir JSONL günlüğünü (`<sessionId>.acp-stream.jsonl`) işaret eden `streamLogPath` bulunabilir.

### Mevcut bir oturumu sürdürme

Yeni başlatmak yerine önceki bir ACP oturumunu devam ettirmek için `resumeSessionId` kullanın. Aracı konuşma geçmişini `session/load` üzerinden yeniden oynatır; böylece daha önce gelen her şeyin tam bağlamıyla kaldığı yerden devam eder.

```json
{
  "task": "Kaldığımız yerden devam et — kalan test hatalarını düzelt",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

Yaygın kullanım durumları:

- Bir Codex oturumunu dizüstü bilgisayarınızdan telefonunuza devredin — aracınıza kaldığınız yerden devam etmesini söyleyin
- CLI içinde etkileşimli başlattığınız bir kodlama oturumunu şimdi aracınız üzerinden başsız olarak sürdürün
- Gateway yeniden başlatması veya boşta zaman aşımıyla kesilen işi devam ettirin

Notlar:

- `resumeSessionId`, `runtime: "acp"` gerektirir — alt aracı çalışma zamanıyla kullanılırsa hata döner.
- `resumeSessionId`, upstream ACP konuşma geçmişini geri yükler; `thread` ve `mode` yine oluşturduğunuz yeni OpenClaw oturumu için normal şekilde uygulanır, bu nedenle `mode: "session"` için yine `thread: true` gerekir.
- Hedef aracı `session/load` desteğine sahip olmalıdır (Codex ve Claude Code buna sahiptir).
- Oturum kimliği bulunamazsa başlatma açık bir hatayla başarısız olur — yeni oturuma sessiz geri dönüş yapılmaz.

### Operatör smoke test'i

ACP başlatmanın
yalnızca birim testlerini geçmekle kalmayıp gerçekten uçtan uca çalıştığını hızlıca canlı doğrulamak istediğinizde, bunu bir gateway dağıtımından sonra kullanın.

Önerilen geçit:

1. Hedef host üzerindeki dağıtılmış gateway sürümünü/commit'ini doğrulayın.
2. Dağıtılmış kaynağın
   `src/gateway/sessions-patch.ts` içinde ACP soy kabulünü içerdiğini doğrulayın (`subagent:* or acp:* sessions`).
3. Canlı bir aracıya geçici bir ACPX köprü oturumu açın (örneğin
   `jpclawhq` üzerindeki `razor(main)`).
4. O aracının `sessions_spawn` çağırmasını isteyin, şu değerlerle:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - görev: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. Aracının şunları raporladığını doğrulayın:
   - `accepted=yes`
   - gerçek bir `childSessionKey`
   - doğrulayıcı hatası olmaması
6. Geçici ACPX köprü oturumunu temizleyin.

Canlı aracıya örnek istem:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

Notlar:

- Bu smoke test'i, konuya bağlı kalıcı ACP oturumlarını özellikle test etmiyorsanız
  `mode: "run"` üzerinde tutun.
- Temel geçit için `streamTo: "parent"` gerektirmeyin. Bu yol
  isteyici/oturum yeteneklerine bağlıdır ve ayrı bir entegrasyon denetimidir.
- Konuya bağlı `mode: "session"` testini,
  gerçek bir Discord konusu veya Telegram topic'i üzerinden ikinci, daha zengin bir entegrasyon
  geçişi olarak ele alın.

## Sandbox uyumluluğu

ACP oturumları şu anda OpenClaw sandbox içinde değil, host çalışma zamanında çalışır.

Geçerli sınırlamalar:

- İsteyen oturum sandbox içindeyse ACP başlatmaları hem `sessions_spawn({ runtime: "acp" })` hem de `/acp spawn` için engellenir.
  - Hata: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `runtime: "acp"` ile `sessions_spawn`, `sandbox: "require"` desteği vermez.
  - Hata: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

Sandbox zorlamalı yürütme gerektiğinde `runtime: "subagent"` kullanın.

### `/acp` komutundan

Gerektiğinde sohbetten açık operatör denetimi için `/acp spawn` kullanın.

```text
/acp spawn codex --mode persistent --thread auto
/acp spawn codex --mode oneshot --thread off
/acp spawn codex --bind here
/acp spawn codex --thread here
```

Temel bayraklar:

- `--mode persistent|oneshot`
- `--bind here|off`
- `--thread auto|here|off`
- `--cwd <absolute-path>`
- `--label <name>`

Bkz. [Slash Commands](/tr/tools/slash-commands).

## Oturum hedefi çözümleme

Çoğu `/acp` eylemi isteğe bağlı bir oturum hedefi kabul eder (`session-key`, `session-id` veya `session-label`).

Çözümleme sırası:

1. Açık hedef bağımsız değişkeni (veya `/acp steer` için `--session`)
   - önce anahtarı dener
   - sonra UUID biçimli oturum kimliğini dener
   - sonra etiketi dener
2. Geçerli konu bağlaması (bu konuşma/konu bir ACP oturumuna bağlıysa)
3. Geçerli isteyici oturumu geri dönüşü

Geçerli konuşma bağlamaları ve konu bağlamaları, 2. adımda birlikte yer alır.

Hiçbir hedef çözülemezse OpenClaw açık bir hata döndürür (`Unable to resolve session target: ...`).

## Başlatma bağlama modları

`/acp spawn`, `--bind here|off` destekler.

| Mod    | Davranış                                                              |
| ------ | --------------------------------------------------------------------- |
| `here` | Geçerli etkin konuşmayı yerinde bağla; etkin bir konuşma yoksa başarısız ol. |
| `off`  | Geçerli konuşma bağlaması oluşturma.                                  |

Notlar:

- `--bind here`, "bu kanal veya sohbet Codex destekli olsun" için en basit operatör yoludur.
- `--bind here`, bir alt konu oluşturmaz.
- `--bind here`, yalnızca geçerli konuşma bağlama desteği açığa çıkaran kanallarda kullanılabilir.
- `--bind` ile `--thread`, aynı `/acp spawn` çağrısında birlikte kullanılamaz.

## Başlatma konu modları

`/acp spawn`, `--thread auto|here|off` destekler.

| Mod    | Davranış                                                                                             |
| ------ | ---------------------------------------------------------------------------------------------------- |
| `auto` | Etkin bir konudaysa: o konuyu bağla. Konu dışında: destekleniyorsa bir alt konu oluştur/bağla.      |
| `here` | Geçerli etkin konuyu zorunlu kıl; konu içinde değilse başarısız ol.                                  |
| `off`  | Bağlama yok. Oturum bağsız başlar.                                                                   |

Notlar:

- Konu bağlama olmayan yüzeylerde varsayılan davranış fiilen `off` olur.
- Konuya bağlı başlatma, kanal ilkesi desteği gerektirir:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- Alt konu oluşturmadan geçerli konuşmayı sabitlemek istediğinizde `--bind here` kullanın.

## ACP denetimleri

Kullanılabilir komut ailesi:

- `/acp spawn`
- `/acp cancel`
- `/acp steer`
- `/acp close`
- `/acp status`
- `/acp set-mode`
- `/acp set`
- `/acp cwd`
- `/acp permissions`
- `/acp timeout`
- `/acp model`
- `/acp reset-options`
- `/acp sessions`
- `/acp doctor`
- `/acp install`

`/acp status`, etkin çalışma zamanı seçeneklerini ve mevcutsa hem çalışma zamanı düzeyi hem de backend düzeyi oturum tanımlayıcılarını gösterir.

Bazı denetimler backend yeteneklerine bağlıdır. Bir backend bir denetimi desteklemiyorsa OpenClaw açık bir desteklenmeyen-denetim hatası döndürür.

## ACP komut kılavuzu

| Komut               | Ne yapar                                                | Örnek                                                        |
| ------------------- | ------------------------------------------------------- | ------------------------------------------------------------ |
| `/acp spawn`        | ACP oturumu oluşturur; isteğe bağlı geçerli bağlama veya konu bağlaması. | `/acp spawn codex --bind here --cwd /repo`                   |
| `/acp cancel`       | Hedef oturum için uçuşta olan turu iptal eder.          | `/acp cancel agent:codex:acp:<uuid>`                         |
| `/acp steer`        | Çalışan oturuma yönlendirme talimatı gönderir.          | `/acp steer --session support inbox başarısız testlere öncelik ver` |
| `/acp close`        | Oturumu kapatır ve konu hedeflerinin bağını çözer.      | `/acp close`                                                 |
| `/acp status`       | Backend, mod, durum, çalışma zamanı seçenekleri, yetenekleri gösterir. | `/acp status`                                                |
| `/acp set-mode`     | Hedef oturum için çalışma zamanı modunu ayarlar.        | `/acp set-mode plan`                                         |
| `/acp set`          | Genel çalışma zamanı yapılandırma seçeneği yazar.       | `/acp set model openai/gpt-5.4`                              |
| `/acp cwd`          | Çalışma zamanı çalışma dizini geçersiz kılmasını ayarlar. | `/acp cwd /Users/user/Projects/repo`                       |
| `/acp permissions`  | Onay ilkesi profilini ayarlar.                          | `/acp permissions strict`                                    |
| `/acp timeout`      | Çalışma zamanı zaman aşımını ayarlar (saniye).          | `/acp timeout 120`                                           |
| `/acp model`        | Çalışma zamanı model geçersiz kılmasını ayarlar.        | `/acp model anthropic/claude-opus-4-6`                       |
| `/acp reset-options`| Oturum çalışma zamanı seçenek geçersiz kılmalarını kaldırır. | `/acp reset-options`                                     |
| `/acp sessions`     | Depodan son ACP oturumlarını listeler.                  | `/acp sessions`                                              |
| `/acp doctor`       | Backend sağlığı, yetenekler, uygulanabilir düzeltmeler. | `/acp doctor`                                                |
| `/acp install`      | Deterministik kurulum ve etkinleştirme adımlarını yazdırır. | `/acp install`                                            |

`/acp sessions`, geçerli bağlı veya isteyici oturum için depoyu okur. `session-key`, `session-id` veya `session-label` belirteçleri kabul eden komutlar, hedefleri gateway oturum keşfi üzerinden çözer; buna aracı başına özel `session.store` kökleri de dahildir.

## Çalışma zamanı seçenekleri eşlemesi

`/acp`, kolaylık komutlarına ve genel bir ayarlayıcıya sahiptir.

Eşdeğer işlemler:

- `/acp model <id>`, çalışma zamanı yapılandırma anahtarı `model` ile eşlenir.
- `/acp permissions <profile>`, çalışma zamanı yapılandırma anahtarı `approval_policy` ile eşlenir.
- `/acp timeout <seconds>`, çalışma zamanı yapılandırma anahtarı `timeout` ile eşlenir.
- `/acp cwd <path>`, çalışma zamanı cwd geçersiz kılmasını doğrudan günceller.
- `/acp set <key> <value>`, genel yoldur.
  - Özel durum: `key=cwd`, cwd geçersiz kılma yolunu kullanır.
- `/acp reset-options`, hedef oturum için tüm çalışma zamanı geçersiz kılmalarını temizler.

## acpx harness desteği (güncel)

Geçerli acpx yerleşik harness takma adları:

- `claude`
- `codex`
- `copilot`
- `cursor` (Cursor CLI: `cursor-agent acp`)
- `droid`
- `gemini`
- `iflow`
- `kilocode`
- `kimi`
- `kiro`
- `openclaw`
- `opencode`
- `pi`
- `qwen`

OpenClaw acpx backend'ini kullanırken, acpx yapılandırmanız özel aracı takma adları tanımlamıyorsa `agentId` için bu değerleri tercih edin.
Yerel Cursor kurulumunuz ACP'yi hâlâ `agent acp` olarak açığa çıkarıyorsa, yerleşik varsayılanı değiştirmek yerine acpx yapılandırmanızdaki `cursor` aracı komutunu geçersiz kılın.

Doğrudan acpx CLI kullanımı, `--agent <command>` üzerinden keyfi adaptörleri de hedefleyebilir; ancak bu ham kaçış kapağı bir acpx CLI özelliğidir (normal OpenClaw `agentId` yolu değil).

## Gerekli yapılandırma

Temel ACP tabanı:

```json5
{
  acp: {
    enabled: true,
    // İsteğe bağlı. Varsayılan true'dur; /acp denetimlerini koruyup ACP dispatch'i duraklatmak için false ayarlayın.
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: [
      "claude",
      "codex",
      "copilot",
      "cursor",
      "droid",
      "gemini",
      "iflow",
      "kilocode",
      "kimi",
      "kiro",
      "openclaw",
      "opencode",
      "pi",
      "qwen",
    ],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

Konu bağlama yapılandırması kanal adaptörüne özeldir. Discord için örnek:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true,
      },
    },
  },
}
```

Konuya bağlı ACP başlatma çalışmıyorsa, önce adaptör özellik bayrağını doğrulayın:

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

Geçerli konuşma bağlamaları alt konu oluşturmayı gerektirmez. Etkin bir konuşma bağlamı ve ACP konuşma bağlamalarını açığa çıkaran bir kanal adaptörü gerektirir.

Bkz. [Yapılandırma Başvurusu](/tr/gateway/configuration-reference).

## acpx backend için plugin kurulumu

Yeni kurulumlar paketlenmiş `acpx` çalışma zamanı plugin'ini varsayılan olarak etkin gönderir, bu nedenle ACP
genellikle elle plugin kurma adımı olmadan çalışır.

Şununla başlayın:

```text
/acp doctor
```

`acpx` devre dışı bıraktıysanız, `plugins.allow` / `plugins.deny` ile reddettiyseniz veya
yerel bir geliştirme checkout'una geçmek istiyorsanız, açık plugin yolunu kullanın:

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

Geliştirme sırasında yerel çalışma alanı kurulumu:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

Ardından backend sağlığını doğrulayın:

```text
/acp doctor
```

### acpx komut ve sürüm yapılandırması

Varsayılan olarak, paketlenmiş acpx backend plugin'i (`acpx`) plugin yerel sabitlenmiş ikili dosyayı kullanır:

1. Komut varsayılan olarak ACPX plugin paketinin içindeki plugin yerel `node_modules/.bin/acpx` yoludur.
2. Beklenen sürüm varsayılan olarak uzantı sabitlemesidir.
3. Başlangıç, ACP backend'i hemen hazır değil olarak kaydeder.
4. Arka plandaki bir ensure işi `acpx --version` değerini doğrular.
5. Plugin yerel ikili eksikse veya eşleşmiyorsa şu komutu çalıştırır:
   `npm install --omit=dev --no-save acpx@<pinned>` ve yeniden doğrular.

Plugin yapılandırmasında komut/sürümü geçersiz kılabilirsiniz:

```json
{
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "command": "../acpx/dist/cli.js",
          "expectedVersion": "any"
        }
      }
    }
  }
}
```

Notlar:

- `command`, mutlak yol, göreli yol veya komut adı (`acpx`) kabul eder.
- Göreli yollar OpenClaw çalışma alanı dizininden çözülür.
- `expectedVersion: "any"`, katı sürüm eşleştirmeyi devre dışı bırakır.
- `command` özel bir ikili/yola işaret ettiğinde plugin yerel otomatik kurulum devre dışı bırakılır.
- Backend sağlık denetimi çalışırken OpenClaw başlangıcı engellenmez.

Bkz. [Plugins](/tr/tools/plugin).

### Otomatik bağımlılık kurulumu

OpenClaw'u `npm install -g openclaw` ile global olarak kurduğunuzda, acpx
çalışma zamanı bağımlılıkları (platforma özgü ikili dosyalar)
postinstall hook'u aracılığıyla otomatik olarak kurulur. Otomatik kurulum başarısız olursa gateway yine de
normal şekilde başlar ve eksik bağımlılığı `openclaw acp doctor` üzerinden bildirir.

### Plugin araçları MCP köprüsü

Varsayılan olarak ACPX oturumları, OpenClaw plugin kayıtlı araçlarını
ACP harness'ine açığa çıkarmaz.

Codex veya Claude Code gibi ACP aracıların, bellek geri çağırma/depolama gibi kurulu
OpenClaw plugin araçlarını çağırmasını istiyorsanız, özel köprüyü etkinleştirin:

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

Bunun yaptığı:

- ACPX oturumu
  bootstrap'ine `openclaw-plugin-tools` adlı yerleşik bir MCP sunucusu enjekte eder.
- Kurulu ve etkin OpenClaw
  plugin'leri tarafından zaten kayıtlı olan plugin araçlarını açığa çıkarır.
- Özelliği açık ve varsayılan olarak kapalı tutar.

Güvenlik ve güven notları:

- Bu, ACP harness araç yüzeyini genişletir.
- ACP aracıları yalnızca gateway içinde zaten etkin olan plugin araçlarına erişim alır.
- Bunu, bu plugin'lerin OpenClaw içinde çalışmasına izin vermekle aynı güven sınırı olarak değerlendirin.
- Etkinleştirmeden önce kurulu plugin'leri gözden geçirin.

Özel `mcpServers` eskisi gibi çalışmaya devam eder. Yerleşik plugin-tools köprüsü,
genel MCP sunucu yapılandırmasının yerine geçen değil, ek bir açık katılım kolaylığıdır.

## İzin yapılandırması

ACP oturumları etkileşimsiz çalışır — dosya yazma ve shell exec izin istemlerini onaylamak veya reddetmek için TTY yoktur. acpx plugin'i, izinlerin nasıl işleneceğini kontrol eden iki yapılandırma anahtarı sağlar:

Bu ACPX harness izinleri, OpenClaw exec onaylarından ve Claude CLI `--permission-mode bypassPermissions` gibi CLI-backend sağlayıcı bayraklarından ayrıdır. ACPX `approve-all`, ACP oturumları için harness düzeyi acil durum anahtarıdır.

### `permissionMode`

Harness aracısının istem göstermeden hangi işlemleri yapabileceğini kontrol eder.

| Değer            | Davranış                                                |
| ---------------- | ------------------------------------------------------- |
| `approve-all`    | Tüm dosya yazmaları ve shell komutlarını otomatik onaylar. |
| `approve-reads`  | Yalnızca okumaları otomatik onaylar; yazmalar ve exec istem gerektirir. |
| `deny-all`       | Tüm izin istemlerini reddeder.                          |

### `nonInteractivePermissions`

Bir izin istemi gösterilmesi gerekirken etkileşimli TTY yoksa ne olacağını kontrol eder (ACP oturumları için durum her zaman budur).

| Değer  | Davranış                                                        |
| ------ | --------------------------------------------------------------- |
| `fail` | Oturumu `AcpRuntimeError` ile iptal eder. **(varsayılan)**      |
| `deny` | İzni sessizce reddeder ve devam eder (zarif bozulma).           |

### Yapılandırma

Plugin yapılandırması ile ayarlayın:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

Bu değerleri değiştirdikten sonra gateway'i yeniden başlatın.

> **Önemli:** OpenClaw şu anda varsayılan olarak `permissionMode=approve-reads` ve `nonInteractivePermissions=fail` kullanır. Etkileşimsiz ACP oturumlarında, izin istemi tetikleyen herhangi bir yazma veya exec işlemi `AcpRuntimeError: Permission prompt unavailable in non-interactive mode` hatasıyla başarısız olabilir.
>
> İzinleri kısıtlamanız gerekiyorsa, oturumlar çökmeden zarif şekilde bozulabilsin diye `nonInteractivePermissions` değerini `deny` yapın.

## Sorun giderme

| Belirti                                                                     | Olası neden                                                                    | Düzeltme                                                                                                                                                            |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured`                                     | Backend plugin'i eksik veya devre dışı.                                        | Backend plugin'ini kurup etkinleştirin, ardından `/acp doctor` çalıştırın.                                                                                         |
| `ACP is disabled by policy (acp.enabled=false)`                             | ACP genel olarak devre dışı.                                                   | `acp.enabled=true` ayarlayın.                                                                                                                                       |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`           | Normal konu mesajlarından dispatch devre dışı.                                 | `acp.dispatch.enabled=true` ayarlayın.                                                                                                                              |
| `ACP agent "<id>" is not allowed by policy`                                 | Aracı izin listesinde değil.                                                   | İzin verilen `agentId` kullanın veya `acp.allowedAgents` değerini güncelleyin.                                                                                     |
| `Unable to resolve session target: ...`                                     | Hatalı anahtar/kimlik/etiket belirteci.                                        | `/acp sessions` çalıştırın, tam anahtarı/etiketi kopyalayın, yeniden deneyin.                                                                                      |
| `--bind here requires running /acp spawn inside an active ... conversation` | `--bind here`, etkin bağlanabilir konuşma olmadan kullanıldı.                  | Hedef sohbete/kanala gidip yeniden deneyin veya bağsız başlatma kullanın.                                                                                           |
| `Conversation bindings are unavailable for <channel>.`                      | Adaptörde geçerli konuşma ACP bağlama yeteneği yok.                            | Destekleniyorsa `/acp spawn ... --thread ...` kullanın, üst düzey `bindings[]` yapılandırın veya desteklenen bir kanala geçin.                                    |
| `--thread here requires running /acp spawn inside an active ... thread`     | `--thread here`, konu bağlamı dışında kullanıldı.                              | Hedef konuya gidin veya `--thread auto`/`off` kullanın.                                                                                                             |
| `Only <user-id> can rebind this channel/conversation/thread.`               | Başka bir kullanıcı etkin bağlama hedefinin sahibidir.                         | Sahibi olarak yeniden bağlayın veya farklı bir konuşma ya da konu kullanın.                                                                                         |
| `Thread bindings are unavailable for <channel>.`                            | Adaptörde konu bağlama yeteneği yok.                                           | `--thread off` kullanın veya desteklenen bir adaptöre/kanala geçin.                                                                                                 |
| `Sandboxed sessions cannot spawn ACP sessions ...`                          | ACP çalışma zamanı host tarafındadır; isteyen oturum sandbox içindedir.        | Sandbox içindeki oturumlardan `runtime="subagent"` kullanın veya ACP başlatmayı sandbox dışı bir oturumdan yapın.                                                  |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`     | ACP çalışma zamanı için `sandbox="require"` istendi.                           | Zorunlu sandboxing için `runtime="subagent"` kullanın veya ACP'yi sandbox dışı bir oturumdan `sandbox="inherit"` ile kullanın.                                     |
| Bağlı oturum için ACP metadata'sı eksik                                     | Bayat/silinmiş ACP oturum metadata'sı.                                         | `/acp spawn` ile yeniden oluşturun, sonra konuyu yeniden bağlayın/odaklayın.                                                                                        |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`    | `permissionMode`, etkileşimsiz ACP oturumunda yazmaları/exec'i engelliyor.     | `plugins.entries.acpx.config.permissionMode` değerini `approve-all` olarak ayarlayın ve gateway'i yeniden başlatın. Bkz. [İzin yapılandırması](#permission-configuration). |
| ACP oturumu çok az çıktı ile erken başarısız oluyor                         | İzin istemleri `permissionMode`/`nonInteractivePermissions` tarafından engelleniyor. | Gateway günlüklerinde `AcpRuntimeError` arayın. Tam izinler için `permissionMode=approve-all`; zarif bozulma için `nonInteractivePermissions=deny` ayarlayın. |
| ACP oturumu işi tamamladıktan sonra süresiz takılı kalıyor                  | Harness süreci bitti ama ACP oturumu tamamlandığını bildirmedi.                | `ps aux \| grep acpx` ile izleyin; bayat süreçleri elle sonlandırın.                                                                                                |
