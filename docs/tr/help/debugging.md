---
read_when:
    - Akıl yürütme sızıntısı için ham model çıktısını incelemeniz gerekiyor
    - Yineleme yaparken Gateway'i izleme modunda çalıştırmak istiyorsunuz
    - Tekrarlanabilir bir hata ayıklama iş akışına ihtiyacınız var
summary: 'Hata ayıklama araçları: izleme modu, ham model akışları ve akıl yürütme sızıntısını izleme'
title: Hata ayıklama
x-i18n:
    generated_at: "2026-04-06T03:07:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4bc72e8d6cad3a1acaad066f381c82309583fabf304c589e63885f2685dc704e
    source_path: help/debugging.md
    workflow: 15
---

# Hata ayıklama

Bu sayfa, özellikle bir sağlayıcı akıl yürütmeyi normal metne karıştırdığında,
akış çıktısı için hata ayıklama yardımcılarını kapsar.

## Çalışma zamanı hata ayıklama geçersiz kılmaları

Sohbette `/debug` kullanarak **yalnızca çalışma zamanına ait** yapılandırma geçersiz kılmalarını ayarlayın (disk değil, bellek).
`/debug` varsayılan olarak devre dışıdır; `commands.debug: true` ile etkinleştirin.
Bu, `openclaw.json` dosyasını düzenlemeden belirsiz ayarları açıp kapatmanız gerektiğinde kullanışlıdır.

Örnekler:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset`, tüm geçersiz kılmaları temizler ve diskteki yapılandırmaya geri döner.

## Gateway izleme modu

Hızlı yineleme için gateway'i dosya izleyici altında çalıştırın:

```bash
pnpm gateway:watch
```

Bu şu komuta karşılık gelir:

```bash
node scripts/watch-node.mjs gateway --force
```

İzleyici; `src/` altındaki derlemeyle ilgili dosyalarda, eklenti kaynak dosyalarında,
eklenti `package.json` ve `openclaw.plugin.json` meta verilerinde, `tsconfig.json`,
`package.json` ve `tsdown.config.ts` dosyalarında yeniden başlatma yapar. Eklenti meta veri değişiklikleri
bir `tsdown` yeniden derlemesini zorlamadan gateway'i yeniden başlatır; kaynak ve yapılandırma değişiklikleri ise
önce `dist`'i yeniden derler.

`gateway:watch` sonrasına herhangi bir gateway CLI bayrağı ekleyin; bunlar her
yeniden başlatmada aktarılır. Aynı depo/bayrak kümesi için aynı izleme komutunu yeniden çalıştırmak artık
arkada yinelenen izleyici üst süreçleri bırakmak yerine eski izleyicinin yerini alır.

## Geliştirme profili + geliştirme gateway'i (--dev)

Hata ayıklama için durumu yalıtmak ve güvenli, geçici bir kurulum başlatmak üzere geliştirme profilini kullanın. **İki** adet `--dev` bayrağı vardır:

- **Genel `--dev` (profil):** durumu `~/.openclaw-dev` altında yalıtır ve
  varsayılan gateway portunu `19001` yapar (türetilmiş portlar buna göre kayar).
- **`gateway --dev`: Gateway'e**, eksikse varsayılan bir yapılandırma +
  çalışma alanını otomatik oluşturmasını söyler (ve `BOOTSTRAP.md` dosyasını atlar).

Önerilen akış (geliştirme profili + geliştirme önyüklemesi):

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

Henüz genel bir kurulumunuz yoksa CLI'ı `pnpm openclaw ...` ile çalıştırın.

Bunun yaptığı:

1. **Profil yalıtımı** (genel `--dev`)
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001` (browser/canvas buna göre kayar)

2. **Geliştirme önyüklemesi** (`gateway --dev`)
   - Eksikse asgari bir yapılandırma yazar (`gateway.mode=local`, bind loopback).
   - `agent.workspace` değerini geliştirme çalışma alanına ayarlar.
   - `agent.skipBootstrap=true` ayarlar (`BOOTSTRAP.md` yok).
   - Eksikse çalışma alanı dosyalarını tohumlar:
     `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`.
   - Varsayılan kimlik: **C3‑PO** (protokol droidi).
   - Geliştirme modunda kanal sağlayıcılarını atlar (`OPENCLAW_SKIP_CHANNELS=1`).

Sıfırlama akışı (yeni başlangıç):

```bash
pnpm gateway:dev:reset
```

Not: `--dev` **genel** bir profil bayrağıdır ve bazı çalıştırıcılar tarafından yutulur.
Bunu açıkça yazmanız gerekirse ortam değişkeni biçimini kullanın:

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset`; yapılandırmayı, kimlik bilgilerini, oturumları ve geliştirme çalışma alanını
(`rm` değil, `trash` kullanarak) temizler, ardından varsayılan geliştirme kurulumunu yeniden oluşturur.

İpucu: dev olmayan bir gateway zaten çalışıyorsa (launchd/systemd), önce onu durdurun:

```bash
openclaw gateway stop
```

## Ham akış günlüğü (OpenClaw)

OpenClaw, herhangi bir filtreleme/biçimlendirme öncesinde **ham yardımcı akışını** günlüğe kaydedebilir.
Akıl yürütmenin düz metin deltaları olarak mı
(yoksa ayrı düşünme blokları olarak mı) geldiğini görmenin en iyi yolu budur.

Bunu CLI üzerinden etkinleştirin:

```bash
pnpm gateway:watch --raw-stream
```

İsteğe bağlı yol geçersiz kılma:

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

Eşdeğer ortam değişkenleri:

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

Varsayılan dosya:

`~/.openclaw/logs/raw-stream.jsonl`

## Ham parça günlüğü (pi-mono)

Bloklara ayrıştırılmadan önce **ham OpenAI-uyumlu parçaları** yakalamak için,
pi-mono ayrı bir günlükleyici sunar:

```bash
PI_RAW_STREAM=1
```

İsteğe bağlı yol:

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

Varsayılan dosya:

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> Not: bu yalnızca pi-mono'nun
> `openai-completions` sağlayıcısını kullanan süreçler tarafından üretilir.

## Güvenlik notları

- Ham akış günlükleri tam prompt'ları, araç çıktısını ve kullanıcı verilerini içerebilir.
- Günlükleri yerelde tutun ve hata ayıklamadan sonra silin.
- Günlükleri paylaşırsanız önce gizli bilgileri ve kişisel verileri temizleyin.
