---
read_when:
    - OpenClaw güncellenirken
    - Bir güncellemeden sonra bir şey bozulduğunda
summary: OpenClaw'ı güvenli şekilde güncelleme (genel kurulum veya kaynak), ayrıca geri alma stratejisi
title: Güncelleme
x-i18n:
    generated_at: "2026-04-06T03:08:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: ca9fff0776b9f5977988b649e58a5d169e5fa3539261cb02779d724d4ca92877
    source_path: install/updating.md
    workflow: 15
---

# Güncelleme

OpenClaw'ı güncel tutun.

## Önerilen: `openclaw update`

Güncellemenin en hızlı yolu. Kurulum türünüzü (npm veya git) algılar, en son sürümü getirir, `openclaw doctor` çalıştırır ve gateway'i yeniden başlatır.

```bash
openclaw update
```

Kanal değiştirmek veya belirli bir sürümü hedeflemek için:

```bash
openclaw update --channel beta
openclaw update --tag main
openclaw update --dry-run   # uygulamadan önizleme
```

`--channel beta`, beta sürümünü tercih eder; ancak çalışma zamanı, beta etiketi yoksa veya en son kararlı sürümden daha eskiyse stable/latest sürümüne fallback yapar. Tek seferlik bir paket güncellemesi için ham npm beta dist-tag istiyorsanız `--tag beta` kullanın.

Kanal anlambilimi için [Development channels](/tr/install/development-channels) bölümüne bakın.

## Alternatif: yükleyiciyi yeniden çalıştırın

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

Onboarding'i atlamak için `--no-onboard` ekleyin. Kaynak kurulumları için `--install-method git --no-onboard` geçin.

## Alternatif: manuel npm, pnpm veya bun

```bash
npm i -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

```bash
bun add -g openclaw@latest
```

## Otomatik güncelleyici

Otomatik güncelleyici varsayılan olarak kapalıdır. Bunu `~/.openclaw/openclaw.json` içinde etkinleştirin:

```json5
{
  update: {
    channel: "stable",
    auto: {
      enabled: true,
      stableDelayHours: 6,
      stableJitterHours: 12,
      betaCheckIntervalHours: 1,
    },
  },
}
```

| Kanal    | Davranış                                                                                                      |
| -------- | ------------------------------------------------------------------------------------------------------------- |
| `stable` | `stableDelayHours` kadar bekler, ardından `stableJitterHours` boyunca deterministik jitter ile uygular (yayılmış dağıtım). |
| `beta`   | Her `betaCheckIntervalHours` süresinde bir kontrol eder (varsayılan: saatlik) ve hemen uygular.              |
| `dev`    | Otomatik uygulama yoktur. `openclaw update` komutunu manuel olarak kullanın.                                 |

Gateway ayrıca başlangıçta bir güncelleme ipucu da günlüğe kaydeder (`update.checkOnStart: false` ile devre dışı bırakın).

## Güncellemeden sonra

<Steps>

### doctor çalıştırın

```bash
openclaw doctor
```

Yapılandırmayı geçirir, DM ilkelerini denetler ve gateway sağlığını kontrol eder. Ayrıntılar: [Doctor](/tr/gateway/doctor)

### Gateway'i yeniden başlatın

```bash
openclaw gateway restart
```

### Doğrulayın

```bash
openclaw health
```

</Steps>

## Geri alma

### Bir sürümü sabitleyin (npm)

```bash
npm i -g openclaw@<version>
openclaw doctor
openclaw gateway restart
```

İpucu: `npm view openclaw version` mevcut yayımlanmış sürümü gösterir.

### Bir commit'i sabitleyin (kaynak)

```bash
git fetch origin
git checkout "$(git rev-list -n 1 --before=\"2026-01-01\" origin/main)"
pnpm install && pnpm build
openclaw gateway restart
```

En son sürüme dönmek için: `git checkout main && git pull`.

## Takılırsanız

- `openclaw doctor` komutunu yeniden çalıştırın ve çıktıyı dikkatlice okuyun.
- Kaynak checkout'larında `openclaw update --channel dev` için güncelleyici gerektiğinde `pnpm`'i otomatik olarak önyükler. Bir pnpm/corepack önyükleme hatası görürseniz `pnpm`'i manuel olarak kurun (veya `corepack`'i yeniden etkinleştirin) ve güncellemeyi yeniden çalıştırın.
- Şurayı kontrol edin: [Sorun giderme](/tr/gateway/troubleshooting)
- Discord'da sorun: [https://discord.gg/clawd](https://discord.gg/clawd)

## İlgili

- [Kurulum Genel Bakışı](/tr/install) — tüm kurulum yöntemleri
- [Doctor](/tr/gateway/doctor) — güncellemelerden sonraki sağlık kontrolleri
- [Geçiş](/tr/install/migrating) — ana sürüm geçiş kılavuzları
