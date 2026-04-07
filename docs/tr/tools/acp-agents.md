---
read_when:
    - Kodlama harness'lerini ACP üzerinden çalıştırıyorsunuz
    - Mesajlaşma kanallarında konuşmaya bağlı ACP oturumları kuruyorsunuz
    - Bir mesajlaşma kanalı konuşmasını kalıcı bir ACP oturumuna bağlıyorsunuz
    - ACP arka ucunu ve plugin bağlantısını sorun gideriyorsunuz
    - Sohbetten `/acp` komutlarını işletiyorsunuz
summary: Codex, Claude Code, Cursor, Gemini CLI, OpenClaw ACP ve diğer harness ajanları için ACP çalışma zamanı oturumlarını kullanın
title: ACP Ajanları
x-i18n:
    generated_at: "2026-04-07T08:52:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb651ab39b05e537398623ee06cb952a5a07730fc75d3f7e0de20dd3128e72c6
    source_path: tools/acp-agents.md
    workflow: 15
---

# ACP ajanları

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/) oturumları, OpenClaw'ın harici kodlama harness'lerini (örneğin Pi, Claude Code, Codex, Cursor, Copilot, OpenClaw ACP, OpenCode, Gemini CLI ve diğer desteklenen ACPX harness'leri) bir ACP arka uç plugin'i üzerinden çalıştırmasına olanak tanır.

OpenClaw'dan doğal dilde "bunu Codex'te çalıştır" veya "bir iş parçacığında Claude Code başlat" diye isterseniz, OpenClaw bu isteği yerel alt ajan çalışma zamanına değil ACP çalışma zamanına yönlendirmelidir. Her ACP oturum başlatması bir [arka plan görevi](/tr/automation/tasks) olarak izlenir.

Codex veya Claude Code'un mevcut OpenClaw kanal konuşmalarına doğrudan
harici bir MCP istemcisi olarak bağlanmasını istiyorsanız, ACP yerine
[`openclaw mcp serve`](/cli/mcp) kullanın.

## Hangi sayfayı istiyorum?

Birbirine yakın ve kolay karıştırılan üç yüzey vardır:

| Şunu yapmak istiyorsunuz...                                                               | Bunu kullanın                        | Notlar                                                                                                            |
| ----------------------------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Codex, Claude Code, Gemini CLI veya başka bir harici harness'i OpenClaw _üzerinden_ çalıştırmak | Bu sayfa: ACP ajanları               | Sohbete bağlı oturumlar, `/acp spawn`, `sessions_spawn({ runtime: "acp" })`, arka plan görevleri, çalışma zamanı denetimleri |
| Bir OpenClaw Gateway oturumunu bir editör veya istemci için ACP sunucusu olarak dışa açmak | [`openclaw acp`](/cli/acp)           | Köprü modu. IDE/istemci stdio/WebSocket üzerinden OpenClaw ile ACP konuşur                                        |
| Yerel bir AI CLI'yi yalnızca metin tabanlı yedek model olarak yeniden kullanmak          | [CLI Backends](/tr/gateway/cli-backends) | ACP değildir. OpenClaw araçları yoktur, ACP denetimleri yoktur, harness çalışma zamanı yoktur                    |

## Bu kutudan çıktığı gibi çalışır mı?

Genellikle evet.

- Yeni kurulumlar artık paketle gelen `acpx` çalışma zamanı plugin'i varsayılan olarak etkin şekilde gelir.
- Paketle gelen `acpx` plugin'i, plugin'e yerel olarak sabitlenmiş `acpx` ikilisini tercih eder.
- Başlangıçta OpenClaw bu ikiliyi yoklar ve gerekirse kendini onarır.
- Hızlı bir hazır olma denetimi istiyorsanız `/acp doctor` ile başlayın.

İlk kullanımda yine de olabilecekler:

- Bir hedef harness adaptörü, o harness'i ilk kullandığınızda isteğe bağlı olarak `npx` ile getirilebilir.
- O harness için satıcı auth bilgileri hâlâ host üzerinde mevcut olmalıdır.
- Host'ta npm/ağ erişimi yoksa, ilk çalıştırmadaki adaptör getirmeleri önbellekler önceden ısıtılana veya adaptör başka bir yolla kurulana kadar başarısız olabilir.

Örnekler:

- `/acp spawn codex`: OpenClaw `acpx` önyüklemesi için hazır olmalıdır, ancak Codex ACP adaptörünün ilk çalıştırmada yine de getirilmesi gerekebilir.
- `/acp spawn claude`: Claude ACP adaptörü için de aynı durum geçerlidir; buna ek olarak o host'ta Claude tarafı auth gerekir.

## Hızlı operatör akışı

Pratik bir `/acp` çalışma kılavuzu istediğinizde bunu kullanın:

1. Bir oturum başlatın:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. Bağlı konuşmada veya iş parçacığında çalışın (veya o oturum anahtarını açıkça hedefleyin).
3. Çalışma zamanı durumunu kontrol edin:
   - `/acp status`
4. Gerektiğinde çalışma zamanı seçeneklerini ayarlayın:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. Bağlamı değiştirmeden etkin bir oturuma yön verin:
   - `/acp steer günlüklemeyi sıkılaştır ve devam et`
6. Çalışmayı durdurun:
   - `/acp cancel` (geçerli turu durdur), veya
   - `/acp close` (oturumu kapat + bağları kaldır)

## İnsanlar için hızlı başlangıç

Doğal istek örnekleri:

- "Bu Discord kanalını Codex'e bağla."
- "Burada bir iş parçacığında kalıcı bir Codex oturumu başlat ve odağını koru."
- "Bunu tek seferlik bir Claude Code ACP oturumu olarak çalıştır ve sonucu özetle."
- "Bu iMessage sohbetini Codex'e bağla ve takipleri aynı çalışma alanında tut."
- "Bu görev için bir iş parçacığında Gemini CLI kullan, sonra takipleri aynı iş parçacığında tut."

OpenClaw'ın yapması gereken:

1. `runtime: "acp"` seçmek.
2. İstenen harness hedefini çözmek (`agentId`, örneğin `codex`).
3. Geçerli konuşmaya bağlama istenmişse ve etkin kanal bunu destekliyorsa ACP oturumunu o konuşmaya bağlamak.
4. Aksi halde, iş parçacığına bağlama istenmişse ve geçerli kanal bunu destekliyorsa ACP oturumunu iş parçacığına bağlamak.
5. Odağı kaldırılana/kapatılana/süresi dolana kadar takip eden bağlı mesajları aynı ACP oturumuna yönlendirmek.

## ACP ve alt ajanlar

Harici bir harness çalışma zamanı istediğinizde ACP kullanın. OpenClaw yerel devredilmiş çalıştırmaları istediğinizde alt ajanları kullanın.

| Alan          | ACP oturumu                            | Alt ajan çalıştırması               |
| ------------- | -------------------------------------- | ----------------------------------- |
| Çalışma zamanı | ACP arka uç plugin'i (örneğin acpx)    | OpenClaw yerel alt ajan çalışma zamanı |
| Oturum anahtarı | `agent:<agentId>:acp:<uuid>`         | `agent:<agentId>:subagent:<uuid>`   |
| Ana komutlar  | `/acp ...`                             | `/subagents ...`                    |
| Başlatma aracı | `runtime:"acp"` ile `sessions_spawn`  | `sessions_spawn` (varsayılan çalışma zamanı) |

Ayrıca bkz. [Sub-agents](/tr/tools/subagents).

## ACP, Claude Code'u nasıl çalıştırır

ACP üzerinden Claude Code için yığın şöyledir:

1. OpenClaw ACP oturum denetim düzlemi
2. paketle gelen `acpx` çalışma zamanı plugin'i
3. Claude ACP adaptörü
4. Claude tarafı çalışma zamanı/oturum mekanizması

Önemli ayrım:

- ACP Claude; ACP denetimleri, oturum devam ettirme, arka plan görevi takibi ve isteğe bağlı konuşma/iş parçacığı bağlama ile bir harness oturumudur.
- CLI arka uçları ise ayrı, yalnızca metin tabanlı yerel yedek çalışma zamanlarıdır. Bkz. [CLI Backends](/tr/gateway/cli-backends).

Operatörler için pratik kural:

- `/acp spawn`, bağlanabilir oturumlar, çalışma zamanı denetimleri veya kalıcı harness çalışması istiyorsanız: ACP kullanın
- ham CLI üzerinden basit yerel metin yedeği istiyorsanız: CLI arka uçlarını kullanın

## Bağlı oturumlar

### Geçerli konuşmaya bağlamalar

Geçerli konuşmanın çocuk bir iş parçacığı oluşturmadan kalıcı bir ACP çalışma alanı olmasını istediğinizde `/acp spawn <harness> --bind here` kullanın.

Davranış:

- OpenClaw kanal taşımasını, auth'u, güvenliği ve teslimi sahiplenmeye devam eder.
- Geçerli konuşma, başlatılan ACP oturum anahtarına sabitlenir.
- O konuşmadaki takip mesajları aynı ACP oturumuna yönlendirilir.
- `/new` ve `/reset`, aynı bağlı ACP oturumunu yerinde sıfırlar.
- `/acp close`, oturumu kapatır ve geçerli konuşma bağını kaldırır.

Bunun pratikte anlamı:

- `--bind here` aynı sohbet yüzeyini korur. Discord'da geçerli kanal aynı kanal olarak kalır.
- Taze bir iş başlatıyorsanız `--bind here` yine de yeni bir ACP oturumu oluşturabilir. Bağlama, bu oturumu geçerli konuşmaya iliştirir.
- `--bind here` kendi başına çocuk bir Discord iş parçacığı veya Telegram konusu oluşturmaz.
- ACP çalışma zamanının yine de kendi çalışma dizini (`cwd`) veya arka uç tarafından yönetilen disk çalışma alanı olabilir. Bu çalışma zamanı çalışma alanı sohbet yüzeyinden ayrıdır ve yeni bir mesajlaşma iş parçacığı anlamına gelmez.
- Farklı bir ACP ajanına başlatır ve `--cwd` geçmezseniz, OpenClaw varsayılan olarak istekte bulunanın değil **hedef ajanın** çalışma alanını devralır.
- Devralınan çalışma alanı yolu yoksa (`ENOENT`/`ENOTDIR`), OpenClaw yanlış ağacı sessizce yeniden kullanmak yerine arka ucun varsayılan cwd'sine geri düşer.
- Devralınan çalışma alanı varsa ama erişilemiyorsa (örneğin `EACCES`), başlatma `cwd` değerini düşürmek yerine gerçek erişim hatasını döndürür.

Zihinsel model:

- sohbet yüzeyi: insanların konuşmaya devam ettiği yer (`Discord channel`, `Telegram topic`, `iMessage chat`)
- ACP oturumu: OpenClaw'ın yönlendirdiği kalıcı Codex/Claude/Gemini çalışma zamanı durumu
- çocuk iş parçacığı/konu: yalnızca `--thread ...` ile oluşturulan isteğe bağlı ek mesajlaşma yüzeyi
- çalışma zamanı çalışma alanı: harness'in çalıştığı dosya sistemi konumu (`cwd`, repo checkout'u, arka uç çalışma alanı)

Örnekler:

- `/acp spawn codex --bind here`: bu sohbeti koru, bir Codex ACP oturumu başlat veya ona bağlan ve gelecekteki mesajları burada ona yönlendir
- `/acp spawn codex --thread auto`: OpenClaw bir çocuk iş parçacığı/konu oluşturabilir ve ACP oturumunu oraya bağlayabilir
- `/acp spawn codex --bind here --cwd /workspace/repo`: yukarıdakiyle aynı sohbet bağlaması, ancak Codex `/workspace/repo` içinde çalışır

Geçerli konuşma bağlama desteği:

- Geçerli konuşmaya bağlama desteği ilan eden sohbet/mesaj kanalları, paylaşılan konuşma bağlama yolu üzerinden `--bind here` kullanabilir.
- Özel iş parçacığı/konu semantiklerine sahip kanallar yine de aynı paylaşılan arayüz arkasında kanala özgü kanonikleştirme sağlayabilir.
- `--bind here` her zaman "geçerli konuşmayı yerinde bağla" anlamına gelir.
- Genel geçerli konuşma bağları, paylaşılan OpenClaw bağlama deposunu kullanır ve normal gateway yeniden başlatmalarında da korunur.

Notlar:

- `/acp spawn` üzerinde `--bind here` ve `--thread ...` birbirini dışlar.
- Discord'da `--bind here`, geçerli kanalı veya iş parçacığını yerinde bağlar. OpenClaw'ın `--thread auto|here` için çocuk iş parçacığı oluşturması gerektiğinde yalnızca `spawnAcpSessions` gerekir.
- Etkin kanal geçerli konuşma ACP bağlarını sunmuyorsa, OpenClaw açık bir desteklenmiyor mesajı döndürür.
- `resume` ve "new session" soruları kanal soruları değil, ACP oturumu sorularıdır. Geçerli sohbet yüzeyini değiştirmeden çalışma zamanı durumunu yeniden kullanabilir veya değiştirebilirsiniz.

### İş parçacığına bağlı oturumlar

Bir kanal adaptörü için iş parçacığı bağları etkinleştirildiğinde ACP oturumları iş parçacıklarına bağlanabilir:

- OpenClaw bir iş parçacığını hedef ACP oturumuna bağlar.
- O iş parçacığındaki takip mesajları bağlı ACP oturumuna yönlendirilir.
- ACP çıktısı aynı iş parçacığına geri teslim edilir.
- Odağı kaldırma/kapatma/arşivleme/boşta kalma zaman aşımı veya maksimum yaş süresi dolduğunda bağ kaldırılır.

İş parçacığı bağlama desteği adaptöre özgüdür. Etkin kanal adaptörü iş parçacığı bağlarını desteklemiyorsa OpenClaw açık bir desteklenmiyor/kullanılamıyor mesajı döndürür.

İş parçacığına bağlı ACP için gerekli özellik bayrakları:

- `acp.enabled=true`
- `acp.dispatch.enabled` varsayılan olarak açıktır (`false` ayarlarsanız ACP dağıtımı duraklar)
- Kanal adaptörü ACP iş parçacığı başlatma bayrağı etkin olmalıdır (adaptöre özgü)
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### İş parçacığı destekleyen kanallar

- Oturum/iş parçacığı bağlama yeteneği sunan tüm kanal adaptörleri.
- Mevcut yerleşik destek:
  - Discord iş parçacıkları/kanalları
  - Telegram konuları (gruplar/süper gruplardaki forum konuları ve DM konuları)
- Plugin kanalları da aynı bağlama arayüzü üzerinden destek ekleyebilir.

## Kanala özgü ayarlar

Geçici olmayan iş akışları için kalıcı ACP bağlarını üst düzey `bindings[]` girdilerinde yapılandırın.

### Bağlama modeli

- `bindings[].type="acp"` kalıcı bir ACP konuşma bağını işaretler.
- `bindings[].match` hedef konuşmayı tanımlar:
  - Discord kanal veya iş parçacığı: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Telegram forum konusu: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - BlueBubbles DM/grup sohbeti: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Kararlı grup bağları için `chat_id:*` veya `chat_identifier:*` tercih edin.
  - iMessage DM/grup sohbeti: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Kararlı grup bağları için `chat_id:*` tercih edin.
- `bindings[].agentId`, sahibi olan OpenClaw ajan kimliğidir.
- İsteğe bağlı ACP geçersiz kılmaları `bindings[].acp` altında yaşar:
  - `mode` (`persistent` veya `oneshot`)
  - `label`
  - `cwd`
  - `backend`

### Ajan başına çalışma zamanı varsayılanları

Ajan başına ACP varsayılanlarını bir kez tanımlamak için `agents.list[].runtime` kullanın:

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

- OpenClaw, yapılandırılmış ACP oturumunun kullanımdan önce var olduğundan emin olur.
- O kanal veya konudaki mesajlar yapılandırılmış ACP oturumuna yönlendirilir.
- Bağlı konuşmalarda `/new` ve `/reset`, aynı ACP oturum anahtarını yerinde sıfırlar.
- Geçici çalışma zamanı bağları (örneğin iş parçacığı odağı akışları tarafından oluşturulanlar) mevcut oldukları yerde yine de uygulanır.
- Açık `cwd` olmadan ajanlar arası ACP başlatmaları için OpenClaw, hedef ajanın çalışma alanını ajan yapılandırmasından devralır.
- Devralınan eksik çalışma alanı yolları arka ucun varsayılan cwd'sine geri düşer; eksik olmayan erişim hataları ise başlatma hataları olarak görünür.

## ACP oturumlarını başlatma (arayüzler)

### `sessions_spawn` içinden

Bir ajan turundan veya araç çağrısından ACP oturumu başlatmak için `runtime: "acp"` kullanın.

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

- `runtime` varsayılan olarak `subagent` olur; ACP oturumları için `runtime: "acp"` değerini açıkça ayarlayın.
- `agentId` atlanırsa OpenClaw, yapılandırılmışsa `acp.defaultAgent` kullanır.
- `mode: "session"`, kalıcı bağlı konuşmayı korumak için `thread: true` gerektirir.

Arayüz ayrıntıları:

- `task` (gerekli): ACP oturumuna gönderilen ilk prompt.
- `runtime` (ACP için gerekli): `"acp"` olmalıdır.
- `agentId` (isteğe bağlı): ACP hedef harness kimliği. Ayarlanmışsa `acp.defaultAgent` değerine geri düşer.
- `thread` (isteğe bağlı, varsayılan `false`): desteklenen yerlerde iş parçacığı bağlama akışını ister.
- `mode` (isteğe bağlı): `run` (tek seferlik) veya `session` (kalıcı).
  - varsayılan `run` değeridir
  - `thread: true` ve `mode` atlandığında OpenClaw çalışma zamanı yoluna göre varsayılan olarak kalıcı davranışı seçebilir
  - `mode: "session"` için `thread: true` gerekir
- `cwd` (isteğe bağlı): istenen çalışma zamanı çalışma dizini (arka uç/çalışma zamanı ilkesi tarafından doğrulanır). Atlanırsa ACP başlatması, yapılandırılmışsa hedef ajanın çalışma alanını devralır; devralınan eksik yollar arka uç varsayılanlarına geri düşer, gerçek erişim hataları ise döndürülür.
- `label` (isteğe bağlı): oturum/banner metninde kullanılan operatöre dönük etiket.
- `resumeSessionId` (isteğe bağlı): yeni bir oturum oluşturmak yerine mevcut bir ACP oturumunu sürdürür. Ajan konuşma geçmişini `session/load` ile yeniden oynatır. `runtime: "acp"` gerektirir.
- `streamTo` (isteğe bağlı): `"parent"` ilk ACP çalıştırma ilerleme özetlerini sistem olayları olarak istekte bulunan oturuma geri akıtır.
  - Mevcut olduğunda kabul edilen yanıtlar, tam aktarma geçmişi için kuyruklayabileceğiniz oturum kapsamlı bir JSONL günlüğüne (`<sessionId>.acp-stream.jsonl`) işaret eden `streamLogPath` alanını içerir.

### Mevcut bir oturumu sürdürme

Taze başlamak yerine önceki bir ACP oturumunu sürdürmek için `resumeSessionId` kullanın. Ajan konuşma geçmişini `session/load` aracılığıyla yeniden oynatır; böylece daha önce olanların tam bağlamıyla kaldığı yerden devam eder.

```json
{
  "task": "Kaldığımız yerden devam et — kalan test hatalarını düzelt",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

Yaygın kullanım durumları:

- Bir Codex oturumunu dizüstü bilgisayarınızdan telefonunuza devredin — ajanınıza kaldığınız yerden devam etmesini söyleyin
- CLI içinde etkileşimli olarak başlattığınız bir kodlama oturumunu şimdi başsız olarak ajanınız üzerinden sürdürün
- Bir gateway yeniden başlatması veya boşta kalma zaman aşımı nedeniyle kesilen işi sürdürün

Notlar:

- `resumeSessionId`, `runtime: "acp"` gerektirir — alt ajan çalışma zamanıyla kullanılırsa hata döndürür.
- `resumeSessionId`, yukarı akış ACP konuşma geçmişini geri yükler; `thread` ve `mode` yine de oluşturduğunuz yeni OpenClaw oturumuna normal şekilde uygulanır, bu nedenle `mode: "session"` için yine `thread: true` gerekir.
- Hedef ajan `session/load` desteklemelidir (Codex ve Claude Code destekler).
- Oturum kimliği bulunamazsa başlatma açık bir hatayla başarısız olur — sessizce yeni oturuma geri düşmez.

### Operatör smoke testi

Bir gateway dağıtımından sonra ACP başlatmanın yalnızca birim testlerini geçmediğini, gerçekten uçtan uca çalıştığını hızlıca canlı doğrulamak istediğinizde bunu kullanın.

Önerilen geçit:

1. Hedef host üzerinde dağıtılan gateway sürümünü/commit'ini doğrulayın.
2. Dağıtılan kaynağın, `src/gateway/sessions-patch.ts` içinde ACP köken kabulünü içerdiğini doğrulayın (`subagent:* or acp:* sessions`).
3. Canlı bir ajana geçici bir ACPX köprü oturumu açın (örneğin `jpclawhq` üzerindeki `razor(main)`).
4. Bu ajandan aşağıdakilerle `sessions_spawn` çağırmasını isteyin:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - görev: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. Ajanın şunları bildirdiğini doğrulayın:
   - `accepted=yes`
   - gerçek bir `childSessionKey`
   - doğrulayıcı hatası yok
6. Geçici ACPX köprü oturumunu temizleyin.

Canlı ajana örnek prompt:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

Notlar:

- Bu smoke testini, özellikle iş parçacığına bağlı kalıcı ACP oturumlarını test etmiyorsanız `mode: "run"` üzerinde tutun.
- Temel geçit için `streamTo: "parent"` gerektirmeyin. Bu yol istekte bulunan/oturum yeteneklerine bağlıdır ve ayrı bir entegrasyon denetimidir.
- İş parçacığına bağlı `mode: "session"` testini, gerçek bir Discord iş parçacığından veya Telegram konusundan yapılan ikinci, daha zengin bir entegrasyon geçişi olarak değerlendirin.

## Sandbox uyumluluğu

ACP oturumları şu anda OpenClaw sandbox'ı içinde değil, host çalışma zamanında çalışır.

Mevcut sınırlamalar:

- İstekte bulunan oturum sandbox içindeyse, hem `sessions_spawn({ runtime: "acp" })` hem de `/acp spawn` için ACP başlatmaları engellenir.
  - Hata: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `runtime: "acp"` ile `sessions_spawn`, `sandbox: "require"` desteklemez.
  - Hata: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

Sandbox tarafından zorlanan yürütme gerektiğinde `runtime: "subagent"` kullanın.

### `/acp` komutundan

Sohbetten açık operatör denetimi gerektiğinde `/acp spawn` kullanın.

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
   - sonra UUID biçimli oturum kimliğini
   - sonra etiketi
2. Geçerli iş parçacığı bağı (bu konuşma/iş parçacığı bir ACP oturumuna bağlıysa)
3. Geçerli istekte bulunan oturum yedeği

Geçerli konuşma bağları ve iş parçacığı bağları 2. adıma birlikte katılır.

Hiçbir hedef çözülemezse OpenClaw açık bir hata döndürür (`Unable to resolve session target: ...`).

## Başlatma bağlama modları

`/acp spawn`, `--bind here|off` destekler.

| Mod    | Davranış                                                            |
| ------ | ------------------------------------------------------------------- |
| `here` | Geçerli etkin konuşmayı yerinde bağlar; etkin konuşma yoksa başarısız olur. |
| `off`  | Geçerli konuşma bağı oluşturmaz.                                    |

Notlar:

- `--bind here`, "bu kanalı veya sohbeti Codex destekli yap" için en basit operatör yoludur.
- `--bind here` çocuk bir iş parçacığı oluşturmaz.
- `--bind here` yalnızca geçerli konuşma bağlama desteği sunan kanallarda kullanılabilir.
- `--bind` ve `--thread` aynı `/acp spawn` çağrısında birleştirilemez.

## Başlatma iş parçacığı modları

`/acp spawn`, `--thread auto|here|off` destekler.

| Mod    | Davranış                                                                                           |
| ------ | -------------------------------------------------------------------------------------------------- |
| `auto` | Etkin bir iş parçacığında: o iş parçacığını bağlar. İş parçacığı dışında: destekleniyorsa bir çocuk iş parçacığı oluşturur/bağlar. |
| `here` | Geçerli etkin iş parçacığını gerektirir; değilse başarısız olur.                                  |
| `off`  | Bağlama yoktur. Oturum bağlı olmadan başlar.                                                       |

Notlar:

- İş parçacığı bağlama yüzeyi olmayan ortamlarda varsayılan davranış fiilen `off` olur.
- İş parçacığına bağlı başlatma için kanal ilkesi desteği gerekir:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- Çocuk iş parçacığı oluşturmadan geçerli konuşmayı sabitlemek istediğinizde `--bind here` kullanın.

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

`/acp status`, etkin çalışma zamanı seçeneklerini ve mevcut olduğunda hem çalışma zamanı düzeyi hem arka uç düzeyi oturum tanımlayıcılarını gösterir.

Bazı denetimler arka uç yeteneklerine bağlıdır. Bir arka uç bir denetimi desteklemiyorsa OpenClaw açık bir desteklenmeyen-denetim hatası döndürür.

## ACP komut tarif kitabı

| Komut                | Yaptığı iş                                               | Örnek                                                        |
| -------------------- | -------------------------------------------------------- | ------------------------------------------------------------ |
| `/acp spawn`         | ACP oturumu oluşturur; isteğe bağlı geçerli bağ veya iş parçacığı bağı. | `/acp spawn codex --bind here --cwd /repo`                   |
| `/acp cancel`        | Hedef oturum için devam eden turu iptal eder.            | `/acp cancel agent:codex:acp:<uuid>`                         |
| `/acp steer`         | Çalışan oturuma yönlendirme talimatı gönderir.           | `/acp steer --session support inbox başarısız testleri önceliklendir` |
| `/acp close`         | Oturumu kapatır ve iş parçacığı hedef bağlarını çözer.   | `/acp close`                                                 |
| `/acp status`        | Arka ucu, modu, durumu, çalışma zamanı seçeneklerini, yetenekleri gösterir. | `/acp status`                                                |
| `/acp set-mode`      | Hedef oturum için çalışma zamanı modunu ayarlar.         | `/acp set-mode plan`                                         |
| `/acp set`           | Genel çalışma zamanı yapılandırma seçeneği yazar.        | `/acp set model openai/gpt-5.4`                              |
| `/acp cwd`           | Çalışma zamanı çalışma dizini geçersiz kılmasını ayarlar. | `/acp cwd /Users/user/Projects/repo`                         |
| `/acp permissions`   | Onay ilkesi profilini ayarlar.                           | `/acp permissions strict`                                    |
| `/acp timeout`       | Çalışma zamanı zaman aşımını ayarlar (saniye).           | `/acp timeout 120`                                           |
| `/acp model`         | Çalışma zamanı model geçersiz kılmasını ayarlar.         | `/acp model anthropic/claude-opus-4-6`                       |
| `/acp reset-options` | Oturum çalışma zamanı seçenek geçersiz kılmalarını kaldırır. | `/acp reset-options`                                         |
| `/acp sessions`      | Depodan son ACP oturumlarını listeler.                   | `/acp sessions`                                              |
| `/acp doctor`        | Arka uç sağlığı, yetenekler, uygulanabilir düzeltmeler.  | `/acp doctor`                                                |
| `/acp install`       | Belirlenimci kurulum ve etkinleştirme adımlarını yazdırır. | `/acp install`                                               |

`/acp sessions`, geçerli bağlı veya istekte bulunan oturum için depoyu okur. `session-key`, `session-id` veya `session-label` kabul eden komutlar hedefleri, ajan başına özel `session.store` kökleri dahil gateway oturum keşfi üzerinden çözer.

## Çalışma zamanı seçenek eşlemesi

`/acp`, kolaylık komutları ve genel bir ayarlayıcı içerir.

Eşdeğer işlemler:

- `/acp model <id>`, çalışma zamanı yapılandırma anahtarı `model` ile eşlenir.
- `/acp permissions <profile>`, çalışma zamanı yapılandırma anahtarı `approval_policy` ile eşlenir.
- `/acp timeout <seconds>`, çalışma zamanı yapılandırma anahtarı `timeout` ile eşlenir.
- `/acp cwd <path>`, çalışma zamanı cwd geçersiz kılmasını doğrudan günceller.
- `/acp set <key> <value>`, genel yoldur.
  - Özel durum: `key=cwd`, cwd geçersiz kılma yolunu kullanır.
- `/acp reset-options`, hedef oturum için tüm çalışma zamanı geçersiz kılmalarını temizler.

## acpx harness desteği (güncel)

Mevcut acpx yerleşik harness takma adları:

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

OpenClaw, acpx arka ucunu kullandığında, acpx yapılandırmanız özel ajan takma adları tanımlamadıkça `agentId` için bu değerleri tercih edin.
Yerel Cursor kurulumunuz ACP'yi hâlâ `agent acp` olarak sunuyorsa, yerleşik varsayılanı değiştirmek yerine acpx yapılandırmanızda `cursor` ajan komutunu geçersiz kılın.

Doğrudan acpx CLI kullanımı, `--agent <command>` ile keyfi adaptörleri de hedefleyebilir, ancak bu ham kaçış kapağı acpx CLI özelliğidir (normal OpenClaw `agentId` yolu değildir).

## Gerekli yapılandırma

Çekirdek ACP tabanı:

```json5
{
  acp: {
    enabled: true,
    // İsteğe bağlı. Varsayılan true'dur; /acp denetimlerini korurken ACP dağıtımını duraklatmak için false ayarlayın.
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

İş parçacığı bağlama yapılandırması kanal adaptörüne özgüdür. Discord için örnek:

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

İş parçacığına bağlı ACP başlatma çalışmıyorsa önce adaptör özellik bayrağını doğrulayın:

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

Geçerli konuşma bağları çocuk iş parçacığı oluşturmayı gerektirmez. Etkin konuşma bağlamı ve ACP konuşma bağlarını sunan bir kanal adaptörü gerektirir.

Bkz. [Configuration Reference](/tr/gateway/configuration-reference).

## acpx arka ucu için plugin kurulumu

Yeni kurulumlar paketle gelen `acpx` çalışma zamanı plugin'i varsayılan olarak etkin halde gelir, bu yüzden ACP genellikle elle plugin kurma adımı olmadan çalışır.

Şununla başlayın:

```text
/acp doctor
```

`acpx` öğesini devre dışı bıraktıysanız, `plugins.allow` / `plugins.deny` ile reddettiyseniz veya yerel bir geliştirme checkout'una geçmek istiyorsanız açık plugin yolunu kullanın:

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

Geliştirme sırasında yerel çalışma alanı kurulumu:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

Ardından arka uç sağlığını doğrulayın:

```text
/acp doctor
```

### acpx komut ve sürüm yapılandırması

Varsayılan olarak paketle gelen acpx arka uç plugin'i (`acpx`), plugin'e yerel sabitlenmiş ikiliyi kullanır:

1. Komut, varsayılan olarak ACPX plugin paketinin içindeki plugin'e yerel `node_modules/.bin/acpx` olur.
2. Beklenen sürüm, varsayılan olarak uzantı sabitlemesine ayarlanır.
3. Başlangıç, ACP arka ucunu hemen hazır değil olarak kaydeder.
4. Bir arka plan doğrulama işi `acpx --version` değerini denetler.
5. Plugin'e yerel ikili eksikse veya sürüm eşleşmiyorsa şunu çalıştırır:
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
- `expectedVersion: "any"`, katı sürüm eşlemesini devre dışı bırakır.
- `command` özel bir ikili/yola işaret ettiğinde plugin'e yerel otomatik kurulum devre dışı bırakılır.
- Arka uç sağlık denetimi çalışırken OpenClaw başlangıcı engellenmez.

Bkz. [Plugins](/tr/tools/plugin).

### Otomatik bağımlılık kurulumu

OpenClaw'ı `npm install -g openclaw` ile genel olarak kurduğunuzda, acpx
çalışma zamanı bağımlılıkları (platforma özgü ikililer) bir postinstall hook'u
aracılığıyla otomatik olarak kurulur. Otomatik kurulum başarısız olursa gateway yine de normal şekilde başlar
ve eksik bağımlılığı `openclaw acp doctor` aracılığıyla bildirir.

### Plugin araçları MCP köprüsü

Varsayılan olarak ACPX oturumları, OpenClaw plugin tarafından kaydedilmiş araçları
ACP harness'ine **göstermez**.

Codex veya Claude Code gibi ACP ajanlarının, bellek geri çağırma/depolama gibi
kurulu OpenClaw plugin araçlarını çağırmasını istiyorsanız, ayrılmış köprüyü etkinleştirin:

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

Bunun yaptığı:

- ACPX oturum önyüklemesine `openclaw-plugin-tools` adında yerleşik bir MCP sunucusu ekler.
- Kurulu ve etkin OpenClaw
  plugin'leri tarafından zaten kaydedilmiş plugin araçlarını açığa çıkarır.
- Özelliği açık ve varsayılan olarak kapalı tutar.

Güvenlik ve güven notları:

- Bu, ACP harness araç yüzeyini genişletir.
- ACP ajanları yalnızca gateway'de zaten etkin olan plugin araçlarına erişir.
- Bunu, bu plugin'lerin OpenClaw içinde yürütülmesine izin vermekle aynı güven sınırı olarak değerlendirin.
- Etkinleştirmeden önce kurulu plugin'leri gözden geçirin.

Özel `mcpServers` her zamanki gibi çalışmaya devam eder. Yerleşik plugin araçları köprüsü,
genel MCP sunucu yapılandırmasının yerine geçen bir çözüm değil, ek bir isteğe bağlı kolaylıktır.

## İzin yapılandırması

ACP oturumları etkileşimsiz çalışır — dosya yazma ve kabuk yürütme izin istemlerini onaylamak veya reddetmek için TTY yoktur. acpx plugin'i, izinlerin nasıl ele alınacağını kontrol eden iki yapılandırma anahtarı sağlar:

Bu ACPX harness izinleri, OpenClaw exec onaylarından ve Claude CLI `--permission-mode bypassPermissions` gibi CLI arka uç satıcı atlama bayraklarından ayrıdır. ACPX `approve-all`, ACP oturumları için harness düzeyindeki acil durum anahtarıdır.

### `permissionMode`

Harness ajanının istem göstermeden hangi işlemleri yapabileceğini kontrol eder.

| Değer          | Davranış                                                 |
| -------------- | -------------------------------------------------------- |
| `approve-all`  | Tüm dosya yazmalarını ve kabuk komutlarını otomatik onaylar. |
| `approve-reads` | Yalnızca okumaları otomatik onaylar; yazma ve exec istem gerektirir. |
| `deny-all`     | Tüm izin istemlerini reddeder.                           |

### `nonInteractivePermissions`

İzin istemi gösterilecek olduğunda ama etkileşimli TTY bulunmadığında ne olacağını kontrol eder (ACP oturumları için durum her zaman budur).

| Değer  | Davranış                                                         |
| ------ | ---------------------------------------------------------------- |
| `fail` | Oturumu `AcpRuntimeError` ile durdurur. **(varsayılan)**         |
| `deny` | İzni sessizce reddeder ve devam eder (zarif bozulma).            |

### Yapılandırma

Plugin yapılandırmasıyla ayarlayın:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

Bu değerleri değiştirdikten sonra gateway'i yeniden başlatın.

> **Önemli:** OpenClaw şu anda varsayılan olarak `permissionMode=approve-reads` ve `nonInteractivePermissions=fail` kullanır. Etkileşimsiz ACP oturumlarında izin istemi tetikleyen herhangi bir yazma veya exec işlemi `AcpRuntimeError: Permission prompt unavailable in non-interactive mode` ile başarısız olabilir.
>
> İzinleri kısıtlamanız gerekiyorsa, oturumların çökmesi yerine zarifçe bozulması için `nonInteractivePermissions` değerini `deny` olarak ayarlayın.

## Sorun giderme

| Belirti                                                                     | Olası neden                                                                     | Düzeltme                                                                                                                                                            |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured`                                     | Arka uç plugin'i eksik veya devre dışı.                                         | Arka uç plugin'ini kurup etkinleştirin, sonra `/acp doctor` çalıştırın.                                                                                            |
| `ACP is disabled by policy (acp.enabled=false)`                             | ACP genel olarak devre dışı.                                                    | `acp.enabled=true` ayarlayın.                                                                                                                                       |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`           | Normal iş parçacığı mesajlarından dağıtım devre dışı.                           | `acp.dispatch.enabled=true` ayarlayın.                                                                                                                              |
| `ACP agent "<id>" is not allowed by policy`                                 | Ajan izin listesinde değil.                                                     | İzin verilen `agentId` kullanın veya `acp.allowedAgents` değerini güncelleyin.                                                                                     |
| `Unable to resolve session target: ...`                                     | Hatalı anahtar/kimlik/etiket belirteci.                                         | `/acp sessions` çalıştırın, tam anahtarı/etiketi kopyalayın, yeniden deneyin.                                                                                      |
| `--bind here requires running /acp spawn inside an active ... conversation` | `--bind here`, etkin bağlanabilir konuşma olmadan kullanıldı.                   | Hedef sohbet/kanala gidip yeniden deneyin veya bağlı olmayan başlatma kullanın.                                                                                     |
| `Conversation bindings are unavailable for <channel>.`                      | Adaptörde geçerli konuşma ACP bağlama yeteneği yok.                             | Desteklenen yerlerde `/acp spawn ... --thread ...` kullanın, üst düzey `bindings[]` yapılandırın veya desteklenen bir kanala geçin.                                |
| `--thread here requires running /acp spawn inside an active ... thread`     | `--thread here`, iş parçacığı bağlamı dışında kullanıldı.                       | Hedef iş parçacığına gidin veya `--thread auto`/`off` kullanın.                                                                                                     |
| `Only <user-id> can rebind this channel/conversation/thread.`               | Etkin bağ hedefinin sahibi başka bir kullanıcı.                                 | Sahibi olarak yeniden bağlayın veya farklı bir konuşma ya da iş parçacığı kullanın.                                                                                 |
| `Thread bindings are unavailable for <channel>.`                            | Adaptörde iş parçacığı bağlama yeteneği yok.                                    | `--thread off` kullanın veya desteklenen adaptöre/kanala geçin.                                                                                                     |
| `Sandboxed sessions cannot spawn ACP sessions ...`                          | ACP çalışma zamanı host taraflıdır; istekte bulunan oturum sandbox içindedir.   | Sandbox içi oturumlardan `runtime="subagent"` kullanın veya ACP başlatmayı sandbox dışı bir oturumdan yapın.                                                       |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`     | ACP çalışma zamanı için `sandbox="require"` istendi.                            | Zorunlu sandbox için `runtime="subagent"` kullanın veya sandbox dışı bir oturumdan ACP'yi `sandbox="inherit"` ile kullanın.                                        |
| Bağlı oturum için ACP üst verisi eksik                                      | Bayat/silinmiş ACP oturum üst verisi.                                           | `/acp spawn` ile yeniden oluşturun, sonra iş parçacığını yeniden bağlayın/odaklayın.                                                                               |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`    | `permissionMode`, etkileşimsiz ACP oturumunda yazma/exec işlemlerini engelliyor. | `plugins.entries.acpx.config.permissionMode` değerini `approve-all` yapın ve gateway'i yeniden başlatın. Bkz. [İzin yapılandırması](#izin-yapılandırması).       |
| ACP oturumu çok az çıktıyla erken başarısız oluyor                          | İzin istemleri `permissionMode`/`nonInteractivePermissions` tarafından engelleniyor. | `AcpRuntimeError` için gateway günlüklerini kontrol edin. Tam izinler için `permissionMode=approve-all`; zarif bozulma için `nonInteractivePermissions=deny` ayarlayın. |
| ACP oturumu iş tamamlandıktan sonra süresiz takılı kalıyor                  | Harness süreci bitti ama ACP oturumu tamamlandığını bildirmedi.                 | `ps aux \| grep acpx` ile izleyin; bayat süreçleri elle öldürün.                                                                                                    |
