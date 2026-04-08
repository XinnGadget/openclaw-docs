---
read_when:
    - ACP üzerinden kodlama harness'leri çalıştırma
    - Mesajlaşma kanallarında konuşmaya bağlı ACP oturumları kurma
    - Bir mesaj kanalı konuşmasını kalıcı bir ACP oturumuna bağlama
    - ACP backend ve plugin bağlantılarını sorun giderme
    - Sohbetten `/acp` komutlarını kullanma
summary: Codex, Claude Code, Cursor, Gemini CLI, OpenClaw ACP ve diğer harness agent'ları için ACP çalışma zamanı oturumlarını kullanın
title: ACP Agent'ları
x-i18n:
    generated_at: "2026-04-08T02:20:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 71c7c0cdae5247aefef17a0029360950a1c2987ddcee21a1bb7d78c67da52950
    source_path: tools/acp-agents.md
    workflow: 15
---

# ACP agent'ları

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/) oturumları, OpenClaw'ın ACP backend plugin'i üzerinden harici kodlama harness'lerini (örneğin Pi, Claude Code, Codex, Cursor, Copilot, OpenClaw ACP, OpenCode, Gemini CLI ve desteklenen diğer ACPX harness'leri) çalıştırmasını sağlar.

OpenClaw'a doğal dilde "bunu Codex'te çalıştır" veya "bir thread içinde Claude Code başlat" derseniz, OpenClaw bu isteği yerel sub-agent çalışma zamanına değil ACP çalışma zamanına yönlendirmelidir. Her ACP oturum başlatımı bir [arka plan görevi](/tr/automation/tasks) olarak izlenir.

Codex veya Claude Code'un mevcut OpenClaw kanal konuşmalarına doğrudan harici bir MCP istemcisi olarak bağlanmasını istiyorsanız,
ACP yerine [`openclaw mcp serve`](/cli/mcp) kullanın.

## Hangi sayfayı istiyorum?

Kolayca karıştırılabilen üç yakın yüzey vardır:

| Şunu yapmak istiyorsunuz...                                                                | Bunu kullanın                       | Notlar                                                                                                             |
| ------------------------------------------------------------------------------------------ | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Codex, Claude Code, Gemini CLI veya başka bir harici harness'i OpenClaw _üzerinden_ çalıştırmak | Bu sayfa: ACP agent'ları            | Sohbete bağlı oturumlar, `/acp spawn`, `sessions_spawn({ runtime: "acp" })`, arka plan görevleri, çalışma zamanı kontrolleri |
| Bir OpenClaw Gateway oturumunu bir editör veya istemci için ACP sunucusu _olarak_ açığa çıkarmak | [`openclaw acp`](/cli/acp)          | Köprü kipi. IDE/istemci ACP ile stdio/WebSocket üzerinden OpenClaw ile konuşur                                    |
| Yerel bir AI CLI'yi yalnızca metin tabanlı yedek model olarak yeniden kullanmak            | [CLI Backends](/tr/gateway/cli-backends) | ACP değildir. OpenClaw araçları yoktur, ACP kontrolleri yoktur, harness çalışma zamanı yoktur                     |

## Bu kutudan çıktığı gibi çalışır mı?

Genellikle evet.

- Yeni kurulumlar artık paketlenmiş `acpx` çalışma zamanı plugin'i etkin olarak gelir.
- Paketlenmiş `acpx` plugin'i kendi plugin'e yerel sabitlenmiş `acpx` ikilisini tercih eder.
- Başlangıçta OpenClaw bu ikiliyi yoklar ve gerekirse kendi kendini onarır.
- Hızlı bir hazırlık kontrolü istiyorsanız `/acp doctor` ile başlayın.

İlk kullanımda yine de şu durumlar olabilir:

- Hedef harness bağdaştırıcısı, o harness'i ilk kez kullandığınızda isteğe bağlı olarak `npx` ile getirilebilir.
- Sağlayıcı kimlik doğrulamasının yine de o host üzerinde mevcut olması gerekir.
- Host üzerinde npm/ağ erişimi yoksa, ilk çalıştırma bağdaştırıcı getirme işlemleri önbellekler önceden ısıtılana veya bağdaştırıcı başka bir yolla kurulana kadar başarısız olabilir.

Örnekler:

- `/acp spawn codex`: OpenClaw `acpx` bootstrap için hazır olmalıdır, ancak Codex ACP bağdaştırıcısının yine de ilk çalıştırma getirmesine ihtiyacı olabilir.
- `/acp spawn claude`: Claude ACP bağdaştırıcısı için de aynı durum geçerlidir; ayrıca o host üzerinde Claude tarafı auth gerekir.

## Hızlı operatör akışı

Pratik bir `/acp` runbook istediğinizde bunu kullanın:

1. Bir oturum başlatın:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. Bağlı konuşma veya thread içinde çalışın (veya o oturum anahtarını açıkça hedefleyin).
3. Çalışma zamanı durumunu kontrol edin:
   - `/acp status`
4. Gerektiğinde çalışma zamanı seçeneklerini ayarlayın:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. Bağlamı değiştirmeden etkin bir oturuma yön verin:
   - `/acp steer tighten logging and continue`
6. Çalışmayı durdurun:
   - `/acp cancel` (geçerli dönüşü durdurur), veya
   - `/acp close` (oturumu kapatır + bağları kaldırır)

## İnsanlar için hızlı başlangıç

Doğal istek örnekleri:

- "Bu Discord kanalını Codex'e bağla."
- "Burada bir thread içinde kalıcı bir Codex oturumu başlat ve odaklı tut."
- "Bunu tek seferlik bir Claude Code ACP oturumu olarak çalıştır ve sonucu özetle."
- "Bu iMessage sohbetini Codex'e bağla ve takip mesajlarını aynı çalışma alanında tut."
- "Bu görev için bir thread içinde Gemini CLI kullan, sonra takipleri aynı thread içinde tut."

OpenClaw'ın yapması gerekenler:

1. `runtime: "acp"` seçmek.
2. İstenen harness hedefini çözümlemek (`agentId`, örneğin `codex`).
3. Mevcut konuşma bağı isteniyorsa ve etkin kanal bunu destekliyorsa, ACP oturumunu o konuşmaya bağlamak.
4. Aksi halde thread bağı isteniyorsa ve mevcut kanal bunu destekliyorsa, ACP oturumunu o thread'e bağlamak.
5. Odağı kaldırılana/kapatılana/süresi dolana kadar sonraki bağlı mesajları aynı ACP oturumuna yönlendirmek.

## ACP ile sub-agent'lar karşılaştırması

Harici bir harness çalışma zamanı istediğinizde ACP kullanın. OpenClaw'ın yerel devredilmiş çalıştırmalarını istediğinizde sub-agent kullanın.

| Alan          | ACP oturumu                           | Sub-agent çalıştırması              |
| ------------- | ------------------------------------- | ----------------------------------- |
| Çalışma zamanı | ACP backend plugin'i (örneğin acpx)   | OpenClaw yerel sub-agent çalışma zamanı |
| Oturum anahtarı | `agent:<agentId>:acp:<uuid>`        | `agent:<agentId>:subagent:<uuid>`   |
| Ana komutlar  | `/acp ...`                            | `/subagents ...`                    |
| Başlatma aracı | `sessions_spawn` ile `runtime:"acp"` | `sessions_spawn` (varsayılan çalışma zamanı) |

Ayrıca bkz. [Sub-agents](/tr/tools/subagents).

## ACP, Claude Code'u nasıl çalıştırır

ACP üzerinden Claude Code için yığın şöyledir:

1. OpenClaw ACP oturum kontrol düzlemi
2. paketlenmiş `acpx` çalışma zamanı plugin'i
3. Claude ACP bağdaştırıcısı
4. Claude tarafı çalışma zamanı/oturum mekanizması

Önemli ayrım:

- ACP Claude; ACP kontrolleri, oturum devam ettirme, arka plan görevi takibi ve isteğe bağlı konuşma/thread bağına sahip bir harness oturumudur.
- CLI backend'leri ayrı, yalnızca metin tabanlı yerel yedek çalışma zamanlarıdır. Bkz. [CLI Backends](/tr/gateway/cli-backends).

Operatörler için pratik kural:

- `/acp spawn`, bağlanabilir oturumlar, çalışma zamanı kontrolleri veya kalıcı harness çalışması istiyorsanız: ACP kullanın
- ham CLI üzerinden basit yerel metin yedeği istiyorsanız: CLI backend'lerini kullanın

## Bağlı oturumlar

### Mevcut konuşmaya bağlar

Geçerli konuşmanın alt thread oluşturmadan kalıcı bir ACP çalışma alanına dönüşmesini istiyorsanız `/acp spawn <harness> --bind here` kullanın.

Davranış:

- Kanal taşıması, auth, güvenlik ve teslimatın sahibi OpenClaw olmaya devam eder.
- Geçerli konuşma, başlatılan ACP oturum anahtarına sabitlenir.
- Bu konuşmadaki takip mesajları aynı ACP oturumuna yönlendirilir.
- `/new` ve `/reset`, aynı bağlı ACP oturumunu yerinde sıfırlar.
- `/acp close`, oturumu kapatır ve mevcut konuşma bağını kaldırır.

Bunun pratikte anlamı:

- `--bind here`, aynı sohbet yüzeyini korur. Discord'da mevcut kanal aynı kanal olarak kalır.
- `--bind here`, yeni bir çalışma başlatıyorsanız yine de yeni bir ACP oturumu oluşturabilir. Bağ, o oturumu mevcut konuşmaya iliştirir.
- `--bind here` kendi başına alt Discord thread'i veya Telegram konusu oluşturmaz.
- ACP çalışma zamanı yine de kendi çalışma dizinine (`cwd`) veya backend tarafından yönetilen disk üstü çalışma alanına sahip olabilir. Bu çalışma zamanı çalışma alanı sohbet yüzeyinden ayrıdır ve yeni bir mesajlaşma thread'i anlamına gelmez.
- Farklı bir ACP agent'ına başlatma yaparsanız ve `--cwd` vermezseniz, OpenClaw varsayılan olarak isteği yapanın değil **hedef agent'ın** çalışma alanını devralır.
- Devralınan çalışma alanı yolu eksikse (`ENOENT`/`ENOTDIR`), OpenClaw yanlış ağacı sessizce yeniden kullanmak yerine backend varsayılan cwd'sine geri döner.
- Devralınan çalışma alanı varsa ancak erişilemiyorsa (örneğin `EACCES`), başlatma `cwd` alanını düşürmek yerine gerçek erişim hatasını döndürür.

Zihinsel model:

- sohbet yüzeyi: insanların konuşmaya devam ettiği yer (`Discord channel`, `Telegram topic`, `iMessage chat`)
- ACP oturumu: OpenClaw'ın yönlendirdiği kalıcı Codex/Claude/Gemini çalışma zamanı durumu
- alt thread/topic: yalnızca `--thread ...` tarafından oluşturulan isteğe bağlı ek mesajlaşma yüzeyi
- çalışma zamanı çalışma alanı: harness'in çalıştığı dosya sistemi konumu (`cwd`, repo checkout, backend çalışma alanı)

Örnekler:

- `/acp spawn codex --bind here`: bu sohbeti koru, bir Codex ACP oturumu başlat veya bağlan ve gelecekteki mesajları burada ona yönlendir
- `/acp spawn codex --thread auto`: OpenClaw bir alt thread/topic oluşturabilir ve ACP oturumunu oraya bağlayabilir
- `/acp spawn codex --bind here --cwd /workspace/repo`: yukarıdakiyle aynı sohbet bağı, ancak Codex `/workspace/repo` içinde çalışır

Mevcut konuşma bağlama desteği:

- Geçerli konuşma bağlama desteği bildiren sohbet/mesajlaşma kanalları `--bind here` seçeneğini paylaşılan konuşma bağlama yolu üzerinden kullanabilir.
- Özel thread/topic semantiğine sahip kanallar yine de kanal bazlı kanonikleştirmeyi aynı paylaşılan arayüzün arkasında sağlayabilir.
- `--bind here` her zaman "geçerli konuşmayı yerinde bağla" anlamına gelir.
- Genel mevcut konuşma bağları paylaşılan OpenClaw bağ deposunu kullanır ve normal gateway yeniden başlatmalarında korunur.

Notlar:

- `/acp spawn` üzerinde `--bind here` ile `--thread ...` birbirini dışlar.
- Discord'da `--bind here`, mevcut kanal veya thread'i yerinde bağlar. `spawnAcpSessions` yalnızca OpenClaw'ın `--thread auto|here` için alt thread oluşturması gerektiğinde gerekir.
- Etkin kanal mevcut konuşma ACP bağlarını açığa çıkarmıyorsa, OpenClaw açık bir desteklenmiyor mesajı döndürür.
- `resume` ve "new session" soruları kanal soruları değil, ACP oturumu sorularıdır. Geçerli sohbet yüzeyini değiştirmeden çalışma zamanı durumunu yeniden kullanabilir veya değiştirebilirsiniz.

### Thread'e bağlı oturumlar

Bir kanal bağdaştırıcısı için thread bağları etkinleştirildiğinde, ACP oturumları thread'lere bağlanabilir:

- OpenClaw bir thread'i hedef ACP oturumuna bağlar.
- Bu thread içindeki takip mesajları bağlı ACP oturumuna yönlendirilir.
- ACP çıktısı aynı thread'e geri teslim edilir.
- Odağı kaldırma/kapatma/arşivleme/boşta kalma zaman aşımı veya azami yaş süresi dolması bağlamayı kaldırır.

Thread bağlama desteği bağdaştırıcıya özeldir. Etkin kanal bağdaştırıcısı thread bağlarını desteklemiyorsa, OpenClaw açık bir desteklenmiyor/kullanılamıyor mesajı döndürür.

Thread'e bağlı ACP için gerekli özellik bayrakları:

- `acp.enabled=true`
- `acp.dispatch.enabled` varsayılan olarak açıktır (ACP dispatch'i duraklatmak için `false` ayarlayın)
- Kanal bağdaştırıcısı ACP thread-spawn bayrağı etkin olmalı (bağdaştırıcıya özgü)
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### Thread destekleyen kanallar

- Oturum/thread bağlama yeteneğini açığa çıkaran herhangi bir kanal bağdaştırıcısı.
- Mevcut yerleşik destek:
  - Discord threads/channels
  - Telegram topics (gruplar/süper gruplardaki forum konuları ve DM konuları)
- Plugin kanalları aynı bağlama arayüzü üzerinden destek ekleyebilir.

## Kanala özgü ayarlar

Kısa ömürlü olmayan iş akışları için kalıcı ACP bağlarını üst düzey `bindings[]` girdilerinde yapılandırın.

### Bağlama modeli

- `bindings[].type="acp"` kalıcı bir ACP konuşma bağı işaretler.
- `bindings[].match` hedef konuşmayı tanımlar:
  - Discord kanal veya thread: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Telegram forum konusu: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - BlueBubbles DM/grup sohbeti: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Kararlı grup bağları için `chat_id:*` veya `chat_identifier:*` tercih edin.
  - iMessage DM/grup sohbeti: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Kararlı grup bağları için `chat_id:*` tercih edin.
- `bindings[].agentId`, sahibi olan OpenClaw agent kimliğidir.
- İsteğe bağlı ACP geçersiz kılmaları `bindings[].acp` altında bulunur:
  - `mode` (`persistent` veya `oneshot`)
  - `label`
  - `cwd`
  - `backend`

### Agent başına çalışma zamanı varsayılanları

Agent başına ACP varsayılanlarını bir kez tanımlamak için `agents.list[].runtime` kullanın:

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

- OpenClaw, yapılandırılan ACP oturumunun kullanımdan önce var olduğundan emin olur.
- O kanal veya konudaki mesajlar yapılandırılan ACP oturumuna yönlendirilir.
- Bağlı konuşmalarda `/new` ve `/reset`, aynı ACP oturum anahtarını yerinde sıfırlar.
- Geçici çalışma zamanı bağları (örneğin thread-focus akışlarıyla oluşturulanlar) mevcut oldukları yerlerde yine uygulanır.
- Açık bir `cwd` olmadan agent'lar arası ACP başlatmalarında OpenClaw, agent yapılandırmasından hedef agent çalışma alanını devralır.
- Eksik devralınan çalışma alanı yolları backend varsayılan cwd'sine geri döner; eksik olmayan erişim hataları ise başlatma hatası olarak yüzeye çıkar.

## ACP oturumlarını başlatma (arayüzler)

### `sessions_spawn` içinden

Bir agent dönüşünden veya araç çağrısından ACP oturumu başlatmak için `runtime: "acp"` kullanın.

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

- `runtime` varsayılan olarak `subagent` olur; bu yüzden ACP oturumları için `runtime: "acp"` değerini açıkça ayarlayın.
- `agentId` verilmezse, yapılandırılmışsa OpenClaw `acp.defaultAgent` değerini kullanır.
- `mode: "session"` kalıcı bağlı konuşmayı korumak için `thread: true` gerektirir.

Arayüz ayrıntıları:

- `task` (zorunlu): ACP oturumuna gönderilen ilk istem.
- `runtime` (ACP için zorunlu): `"acp"` olmalıdır.
- `agentId` (isteğe bağlı): ACP hedef harness kimliği. Ayarlanmışsa `acp.defaultAgent` değerine geri döner.
- `thread` (isteğe bağlı, varsayılan `false`): desteklenen yerlerde thread bağlama akışı ister.
- `mode` (isteğe bağlı): `run` (tek seferlik) veya `session` (kalıcı).
  - varsayılan `run` değeridir
  - `thread: true` ise ve kip verilmemişse, OpenClaw çalışma zamanı yoluna göre kalıcı davranışı varsayılan yapabilir
  - `mode: "session"` için `thread: true` gerekir
- `cwd` (isteğe bağlı): istenen çalışma zamanı çalışma dizini (backend/çalışma zamanı ilkesi tarafından doğrulanır). Verilmezse ACP başlatma yapılandırılmışsa hedef agent çalışma alanını devralır; eksik devralınan yollar backend varsayılanlarına geri dönerken gerçek erişim hataları döndürülür.
- `label` (isteğe bağlı): oturum/banner metninde kullanılan operatör odaklı etiket.
- `resumeSessionId` (isteğe bağlı): yeni bir oturum oluşturmak yerine mevcut bir ACP oturumunu sürdürür. Agent konuşma geçmişini `session/load` üzerinden yeniden oynatır. `runtime: "acp"` gerektirir.
- `streamTo` (isteğe bağlı): `"parent"` ilk ACP çalıştırma ilerleme özetlerini sistem olayları olarak istek yapan oturuma akıtır.
  - Mevcut olduğunda, kabul edilen yanıtlar tam relay geçmişi için izleyebileceğiniz oturum kapsamlı JSONL günlüğüne (`<sessionId>.acp-stream.jsonl`) işaret eden `streamLogPath` içerebilir.

### Mevcut bir oturumu sürdürme

Yeni başlatmak yerine önceki bir ACP oturumunu sürdürmek için `resumeSessionId` kullanın. Agent konuşma geçmişini `session/load` üzerinden yeniden oynattığı için, önce ne olduğu tam bağlamıyla kaldığı yerden devam eder.

```json
{
  "task": "Kaldığımız yerden devam et — kalan test hatalarını düzelt",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

Yaygın kullanım durumları:

- Bir Codex oturumunu dizüstü bilgisayarınızdan telefonunuza devretmek — agent'ınıza kaldığınız yerden devam etmesini söyleyin
- CLI içinde etkileşimli başlattığınız bir kodlama oturumuna artık headless olarak agent'ınız üzerinden devam etmek
- Gateway yeniden başlatması veya boşta kalma zaman aşımı nedeniyle kesilen işi sürdürmek

Notlar:

- `resumeSessionId` için `runtime: "acp"` gerekir — sub-agent çalışma zamanı ile kullanılırsa hata döndürür.
- `resumeSessionId`, yukarı akış ACP konuşma geçmişini geri yükler; `thread` ve `mode`, oluşturduğunuz yeni OpenClaw oturumu için yine normal şekilde uygulanır; dolayısıyla `mode: "session"` için yine `thread: true` gerekir.
- Hedef agent `session/load` desteğine sahip olmalıdır (Codex ve Claude Code destekler).
- Oturum kimliği bulunamazsa, başlatma açık bir hata ile başarısız olur — yeni oturuma sessiz geri dönüş yapılmaz.

### Operatör smoke testi

Bir gateway dağıtımından sonra ACP başlatmanın
yalnızca birim testlerini geçmekle kalmayıp gerçekten uçtan uca çalıştığını hızlıca canlı doğrulamak istediğinizde bunu kullanın.

Önerilen kapı:

1. Hedef host üzerinde dağıtılan gateway sürümünü/commit'ini doğrulayın.
2. Dağıtılan kaynağın
   `src/gateway/sessions-patch.ts` içinde ACP soy kabulünü içerdiğini doğrulayın (`subagent:* or acp:* sessions`).
3. Canlı bir agent'a geçici bir ACPX bridge oturumu açın (örneğin
   `jpclawhq` üzerindeki `razor(main)`).
4. O agent'tan şu parametrelerle `sessions_spawn` çağırmasını isteyin:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - görev: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. Agent'ın şunları bildirdiğini doğrulayın:
   - `accepted=yes`
   - gerçek bir `childSessionKey`
   - doğrulayıcı hatası yok
6. Geçici ACPX bridge oturumunu temizleyin.

Canlı agent'a örnek istem:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

Notlar:

- Özellikle thread'e bağlı kalıcı ACP oturumlarını test etmiyorsanız bu smoke testi `mode: "run"` üzerinde tutun.
- Temel kapı için `streamTo: "parent"` gerektirmeyin. Bu yol istek yapan/oturum yeteneklerine bağlıdır ve ayrı bir entegrasyon kontrolüdür.
- Thread'e bağlı `mode: "session"` testini gerçek bir Discord thread'i veya Telegram konusu içinden ikinci, daha zengin bir entegrasyon geçişi olarak değerlendirin.

## Sandbox uyumluluğu

ACP oturumları şu anda OpenClaw sandbox'ı içinde değil, host çalışma zamanında çalışır.

Mevcut sınırlamalar:

- İstek yapan oturum sandbox içindeyse, ACP başlatmaları hem `sessions_spawn({ runtime: "acp" })` hem de `/acp spawn` için engellenir.
  - Hata: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `runtime: "acp"` ile `sessions_spawn`, `sandbox: "require"` desteklemez.
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

Çoğu `/acp` eylemi isteğe bağlı oturum hedefini kabul eder (`session-key`, `session-id` veya `session-label`).

Çözümleme sırası:

1. Açık hedef argümanı (veya `/acp steer` için `--session`)
   - önce anahtarı dener
   - sonra UUID biçimli oturum kimliğini
   - sonra etiketi
2. Geçerli thread bağı (bu konuşma/thread bir ACP oturumuna bağlıysa)
3. Geçerli istek yapan oturumuna geri dönüş

Mevcut konuşma bağları ve thread bağları adım 2'ye birlikte katılır.

Hiçbir hedef çözümlenemezse OpenClaw açık bir hata döndürür (`Unable to resolve session target: ...`).

## Başlatma bağ kipleri

`/acp spawn`, `--bind here|off` destekler.

| Kip    | Davranış                                                          |
| ------ | ----------------------------------------------------------------- |
| `here` | Geçerli etkin konuşmayı yerinde bağlar; etkin konuşma yoksa başarısız olur. |
| `off`  | Geçerli konuşma bağı oluşturmaz.                                  |

Notlar:

- `--bind here`, "bu kanal veya sohbeti Codex destekli yap" için en basit operatör yoludur.
- `--bind here` alt thread oluşturmaz.
- `--bind here` yalnızca geçerli konuşma bağlama desteği sunan kanallarda kullanılabilir.
- `--bind` ile `--thread` aynı `/acp spawn` çağrısında birleştirilemez.

## Başlatma thread kipleri

`/acp spawn`, `--thread auto|here|off` destekler.

| Kip    | Davranış                                                                                          |
| ------ | ------------------------------------------------------------------------------------------------- |
| `auto` | Etkin bir thread içindeyse: o thread'i bağlar. Thread dışında: destekleniyorsa bir alt thread oluşturur/bağlar. |
| `here` | Geçerli etkin thread'i zorunlu kılar; thread içinde değilse başarısız olur.                       |
| `off`  | Bağlama yok. Oturum bağımsız başlar.                                                              |

Notlar:

- Thread bağlamayan yüzeylerde varsayılan davranış fiilen `off` olur.
- Thread'e bağlı başlatma kanal ilkesi desteği gerektirir:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- Alt thread oluşturmadan geçerli konuşmayı sabitlemek istediğinizde `--bind here` kullanın.

## ACP kontrolleri

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

`/acp status`, etkili çalışma zamanı seçeneklerini ve mevcut olduğunda hem çalışma zamanı düzeyi hem de backend düzeyi oturum tanımlayıcılarını gösterir.

Bazı kontroller backend yeteneklerine bağlıdır. Bir backend bir kontrolü desteklemiyorsa, OpenClaw açık bir desteklenmeyen-kontrol hatası döndürür.

## ACP komut yemek kitabı

| Komut                | Ne yapar                                                | Örnek                                                        |
| -------------------- | ------------------------------------------------------- | ------------------------------------------------------------ |
| `/acp spawn`         | ACP oturumu oluşturur; isteğe bağlı mevcut bağ veya thread bağı. | `/acp spawn codex --bind here --cwd /repo`                   |
| `/acp cancel`        | Hedef oturum için işlemdeki dönüşü iptal eder.          | `/acp cancel agent:codex:acp:<uuid>`                         |
| `/acp steer`         | Çalışan oturuma yönlendirme talimatı gönderir.          | `/acp steer --session support inbox prioritize failing tests` |
| `/acp close`         | Oturumu kapatır ve thread hedef bağlarını kaldırır.     | `/acp close`                                                 |
| `/acp status`        | Backend, kip, durum, çalışma zamanı seçenekleri, yetenekleri gösterir. | `/acp status`                                                |
| `/acp set-mode`      | Hedef oturum için çalışma zamanı kipini ayarlar.        | `/acp set-mode plan`                                         |
| `/acp set`           | Genel çalışma zamanı yapılandırma seçeneği yazımı.      | `/acp set model openai/gpt-5.4`                              |
| `/acp cwd`           | Çalışma zamanı çalışma dizini geçersiz kılmasını ayarlar. | `/acp cwd /Users/user/Projects/repo`                         |
| `/acp permissions`   | Onay ilkesi profilini ayarlar.                          | `/acp permissions strict`                                    |
| `/acp timeout`       | Çalışma zamanı zaman aşımını ayarlar (saniye).          | `/acp timeout 120`                                           |
| `/acp model`         | Çalışma zamanı model geçersiz kılmasını ayarlar.        | `/acp model anthropic/claude-opus-4-6`                       |
| `/acp reset-options` | Oturum çalışma zamanı seçenek geçersiz kılmalarını kaldırır. | `/acp reset-options`                                         |
| `/acp sessions`      | Depodan son ACP oturumlarını listeler.                  | `/acp sessions`                                              |
| `/acp doctor`        | Backend sağlığı, yetenekler, uygulanabilir düzeltmeler. | `/acp doctor`                                                |
| `/acp install`       | Belirlenimci kurulum ve etkinleştirme adımlarını yazdırır. | `/acp install`                                               |

`/acp sessions`, mevcut bağlı veya istek yapan oturum için depoyu okur. `session-key`, `session-id` veya `session-label` kabul eden komutlar, özel agent başına `session.store` kökleri dahil olmak üzere gateway oturum keşfi üzerinden hedefleri çözümler.

## Çalışma zamanı seçenek eşlemesi

`/acp`, kolaylık komutları ve genel bir ayarlayıcıya sahiptir.

Eşdeğer işlemler:

- `/acp model <id>`, çalışma zamanı yapılandırma anahtarı `model` ile eşlenir.
- `/acp permissions <profile>`, çalışma zamanı yapılandırma anahtarı `approval_policy` ile eşlenir.
- `/acp timeout <seconds>`, çalışma zamanı yapılandırma anahtarı `timeout` ile eşlenir.
- `/acp cwd <path>`, çalışma zamanı cwd geçersiz kılmasını doğrudan günceller.
- `/acp set <key> <value>`, genel yoldur.
  - Özel durum: `key=cwd`, cwd geçersiz kılma yolunu kullanır.
- `/acp reset-options`, hedef oturum için tüm çalışma zamanı geçersiz kılmalarını temizler.

## acpx harness desteği (mevcut)

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

OpenClaw acpx backend'ini kullandığında, acpx yapılandırmanız özel agent takma adları tanımlamıyorsa `agentId` için bu değerleri tercih edin.
Yerel Cursor kurulumunuz ACP'yi hâlâ `agent acp` olarak sunuyorsa, yerleşik varsayılanı değiştirmek yerine acpx yapılandırmanızda `cursor` agent komutunu geçersiz kılın.

Doğrudan acpx CLI kullanımı ayrıca `--agent <command>` üzerinden keyfi bağdaştırıcıları hedefleyebilir, ancak bu ham kaçış kapısı bir acpx CLI özelliğidir (normal OpenClaw `agentId` yolu değildir).

## Gerekli yapılandırma

Temel ACP başlangıç yapılandırması:

```json5
{
  acp: {
    enabled: true,
    // İsteğe bağlı. Varsayılan true'dur; /acp kontrollerini korurken ACP dispatch'i duraklatmak için false ayarlayın.
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

Thread bağlama yapılandırması kanal bağdaştırıcısına özeldir. Discord için örnek:

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

Thread'e bağlı ACP başlatma çalışmıyorsa, önce bağdaştırıcı özellik bayrağını doğrulayın:

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

Mevcut konuşma bağları alt thread oluşturulmasını gerektirmez. Etkin konuşma bağlamı ve ACP konuşma bağları sunan bir kanal bağdaştırıcısı gerektirir.

Bkz. [Yapılandırma Başvurusu](/tr/gateway/configuration-reference).

## acpx backend'i için plugin kurulumu

Yeni kurulumlar paketlenmiş `acpx` çalışma zamanı plugin'i etkin olarak gelir, bu yüzden ACP
genellikle elle plugin kurulum adımı olmadan çalışır.

Şununla başlayın:

```text
/acp doctor
```

`acpx` devre dışı bırakıldıysa, `plugins.allow` / `plugins.deny` ile engellendiyse veya
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

Varsayılan olarak, paketlenmiş acpx backend plugin'i (`acpx`) plugin'e yerel sabitlenmiş ikiliyi kullanır:

1. Komut varsayılan olarak ACPX plugin paketi içindeki plugin'e yerel `node_modules/.bin/acpx` olur.
2. Beklenen sürüm varsayılan olarak extension pin'i olur.
3. Başlangıç, ACP backend'ini hemen hazır-değil olarak kaydeder.
4. Arka plandaki bir ensure işi `acpx --version` doğrulaması yapar.
5. Plugin'e yerel ikili eksikse veya sürüm uyuşmuyorsa şu komutu çalıştırır:
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
- `expectedVersion: "any"` sıkı sürüm eşlemesini devre dışı bırakır.
- `command` özel bir ikiliyi/yolu gösterdiğinde plugin'e yerel otomatik kurulum devre dışı kalır.
- Backend sağlık kontrolü çalışırken OpenClaw başlangıcı engellemez.

Bkz. [Plugins](/tr/tools/plugin).

### Otomatik bağımlılık kurulumu

OpenClaw'ı `npm install -g openclaw` ile genel olarak kurduğunuzda, acpx
çalışma zamanı bağımlılıkları (platforma özgü ikililer) bir postinstall hook'u aracılığıyla otomatik kurulur. Otomatik kurulum başarısız olursa gateway yine de normal başlar
ve eksik bağımlılığı `openclaw acp doctor` üzerinden bildirir.

### Plugin araçları MCP köprüsü

Varsayılan olarak, ACPX oturumları OpenClaw tarafından plugin kaydı yapılmış araçları
ACP harness'ine açığa çıkarmaz.

Codex veya Claude Code gibi ACP agent'larının, bellek geri çağırma/depolama gibi yüklü
OpenClaw plugin araçlarını çağırmasını istiyorsanız, ayrılmış köprüyü etkinleştirin:

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

Bunun yaptığı:

- ACPX oturum bootstrap'ine `openclaw-plugin-tools` adlı yerleşik bir MCP sunucusu enjekte eder.
- Yüklü ve etkin OpenClaw plugin'leri tarafından zaten kaydedilmiş plugin araçlarını açığa çıkarır.
- Özelliği açık ve varsayılan olarak kapalı tutar.

Güvenlik ve güven notları:

- Bu, ACP harness araç yüzeyini genişletir.
- ACP agent'ları yalnızca gateway'de zaten etkin olan plugin araçlarına erişir.
- Bunu, o plugin'lerin OpenClaw içinde yürütülmesine izin vermekle aynı güven sınırı olarak değerlendirin.
- Etkinleştirmeden önce yüklü plugin'leri gözden geçirin.

Özel `mcpServers` eskisi gibi çalışmaya devam eder. Yerleşik plugin-tools köprüsü,
genel MCP sunucusu yapılandırmasının yerine geçen değil, ek isteğe bağlı bir kolaylıktır.

### Çalışma zamanı zaman aşımı yapılandırması

Paketlenmiş `acpx` plugin'i, gömülü çalışma zamanı dönüşlerini varsayılan olarak 120 saniyelik
zaman aşımıyla çalıştırır. Bu, Gemini CLI gibi daha yavaş harness'lere
ACP başlangıcı ve ilk hazırlığı tamamlamak için yeterli zaman verir. Host'unuz farklı bir
çalışma zamanı sınırı gerektiriyorsa bunu geçersiz kılın:

```bash
openclaw config set plugins.entries.acpx.config.timeoutSeconds 180
```

Bu değeri değiştirdikten sonra gateway'i yeniden başlatın.

## İzin yapılandırması

ACP oturumları etkileşimsiz çalışır — dosya yazma ve shell-exec izin istemlerini onaylayacak veya reddedecek TTY yoktur. acpx plugin'i, izinlerin nasıl işleneceğini kontrol eden iki yapılandırma anahtarı sağlar:

Bu ACPX harness izinleri, OpenClaw exec onaylarından ve Claude CLI `--permission-mode bypassPermissions` gibi CLI-backend sağlayıcı atlama bayraklarından ayrıdır. ACPX `approve-all`, ACP oturumları için harness düzeyindeki camı kırma anahtarıdır.

### `permissionMode`

Harness agent'ının istem göstermeden hangi işlemleri yapabileceğini kontrol eder.

| Değer          | Davranış                                                       |
| -------------- | -------------------------------------------------------------- |
| `approve-all`  | Tüm dosya yazma ve shell komutlarını otomatik onaylar.         |
| `approve-reads`| Yalnızca okumaları otomatik onaylar; yazma ve exec istem gerektirir. |
| `deny-all`     | Tüm izin istemlerini reddeder.                                 |

### `nonInteractivePermissions`

İzin istemi gösterilmesi gerekirdi ama etkileşimli TTY yoksa ne olacağını kontrol eder (ACP oturumları için her zaman böyledir).

| Değer | Davranış                                                       |
| ----- | -------------------------------------------------------------- |
| `fail`| Oturumu `AcpRuntimeError` ile durdurur. **(varsayılan)**       |
| `deny`| İzni sessizce reddeder ve devam eder (zarif bozulma).          |

### Yapılandırma

Plugin yapılandırması üzerinden ayarlayın:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

Bu değerleri değiştirdikten sonra gateway'i yeniden başlatın.

> **Önemli:** OpenClaw şu anda varsayılan olarak `permissionMode=approve-reads` ve `nonInteractivePermissions=fail` kullanır. Etkileşimsiz ACP oturumlarında, izin istemi tetikleyen herhangi bir yazma veya exec işlemi `AcpRuntimeError: Permission prompt unavailable in non-interactive mode` hatasıyla başarısız olabilir.
>
> İzinleri kısıtlamanız gerekiyorsa, oturumlar çökmeden zarif biçimde bozulabilsin diye `nonInteractivePermissions` değerini `deny` olarak ayarlayın.

## Sorun giderme

| Belirti                                                                     | Olası neden                                                                   | Düzeltme                                                                                                                                                          |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured`                                     | Backend plugin'i eksik veya devre dışı.                                       | Backend plugin'ini kurup etkinleştirin, ardından `/acp doctor` çalıştırın.                                                                                       |
| `ACP is disabled by policy (acp.enabled=false)`                             | ACP genel olarak devre dışı.                                                  | `acp.enabled=true` ayarlayın.                                                                                                                                     |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`           | Normal thread mesajlarından dispatch devre dışı.                              | `acp.dispatch.enabled=true` ayarlayın.                                                                                                                            |
| `ACP agent "<id>" is not allowed by policy`                                 | Agent allowlist içinde değil.                                                 | İzinli `agentId` kullanın veya `acp.allowedAgents` değerini güncelleyin.                                                                                         |
| `Unable to resolve session target: ...`                                     | Hatalı key/id/label belirteci.                                                | `/acp sessions` çalıştırın, tam key/label'ı kopyalayın, yeniden deneyin.                                                                                         |
| `--bind here requires running /acp spawn inside an active ... conversation` | `--bind here`, etkin bağlanabilir bir konuşma olmadan kullanıldı.             | Hedef sohbet/kanala geçip yeniden deneyin veya bağımsız başlatma kullanın.                                                                                       |
| `Conversation bindings are unavailable for <channel>.`                      | Bağdaştırıcı mevcut-konuşma ACP bağlama yeteneğine sahip değil.               | Desteklenen yerlerde `/acp spawn ... --thread ...` kullanın, üst düzey `bindings[]` yapılandırın veya desteklenen bir kanala geçin.                            |
| `--thread here requires running /acp spawn inside an active ... thread`     | `--thread here`, thread bağlamı dışında kullanıldı.                           | Hedef thread'e geçin veya `--thread auto`/`off` kullanın.                                                                                                         |
| `Only <user-id> can rebind this channel/conversation/thread.`               | Etkin bağ hedefinin sahibi başka bir kullanıcı.                               | Sahibi olarak yeniden bağlayın veya farklı bir konuşma ya da thread kullanın.                                                                                     |
| `Thread bindings are unavailable for <channel>.`                            | Bağdaştırıcı thread bağlama yeteneğine sahip değil.                           | `--thread off` kullanın veya desteklenen bağdaştırıcı/kanala geçin.                                                                                               |
| `Sandboxed sessions cannot spawn ACP sessions ...`                          | ACP çalışma zamanı host tarafındadır; istek yapan oturum sandbox içindedir.   | Sandbox içindeki oturumlardan `runtime="subagent"` kullanın veya ACP başlatmayı sandbox dışı bir oturumdan yapın.                                                |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`     | ACP çalışma zamanı için `sandbox="require"` istendi.                          | Zorunlu sandbox için `runtime="subagent"` kullanın veya sandbox dışı bir oturumdan ACP ile `sandbox="inherit"` kullanın.                                         |
| Bağlı oturum için ACP metadata eksik                                        | Eski/silinmiş ACP oturum metadata'sı.                                         | `/acp spawn` ile yeniden oluşturun, sonra thread'i yeniden bağlayın/odaklayın.                                                                                   |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`    | `permissionMode`, etkileşimsiz ACP oturumunda yazma/exec'i engelliyor.        | `plugins.entries.acpx.config.permissionMode` değerini `approve-all` yapın ve gateway'i yeniden başlatın. Bkz. [İzin yapılandırması](#permission-configuration). |
| ACP oturumu çok az çıktıyla erken başarısız oluyor                          | İzin istemleri `permissionMode`/`nonInteractivePermissions` tarafından engelleniyor. | Gateway günlüklerinde `AcpRuntimeError` arayın. Tam izinler için `permissionMode=approve-all`; zarif bozulma için `nonInteractivePermissions=deny` ayarlayın. |
| ACP oturumu iş tamamlandıktan sonra süresiz takılı kalıyor                  | Harness süreci bitti ama ACP oturumu tamamlandığını bildirmedi.               | `ps aux \| grep acpx` ile izleyin; eski süreçleri elle sonlandırın.                                                                                               |
