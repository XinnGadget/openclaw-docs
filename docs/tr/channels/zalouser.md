---
read_when:
    - OpenClaw için Zalo Kişisel kurulumu
    - Zalo Kişisel girişini veya mesaj akışını hata ayıklama
summary: Yerel `zca-js` üzerinden Zalo kişisel hesap desteği (QR ile giriş), yetenekler ve yapılandırma
title: Zalo Kişisel
x-i18n:
    generated_at: "2026-04-07T08:43:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 08f50edb2f4c6fe24972efe5e321f5fd0572c7d29af5c1db808151c7c943dc66
    source_path: channels/zalouser.md
    workflow: 15
---

# Zalo Kişisel (resmi olmayan)

Durum: deneysel. Bu entegrasyon, OpenClaw içinde yerel `zca-js` aracılığıyla bir **kişisel Zalo hesabını** otomatikleştirir.

> **Uyarı:** Bu resmi olmayan bir entegrasyondur ve hesabın askıya alınmasına/banlanmasına neden olabilir. Riski size aittir.

## Birlikte gelen plugin

Zalo Kişisel, mevcut OpenClaw sürümlerinde birlikte gelen bir plugin olarak sunulur, bu nedenle normal paketlenmiş derlemelerde ayrı bir kurulum gerekmez.

Daha eski bir derlemede veya Zalo Kişisel'i içermeyen özel bir kurulum kullanıyorsanız,
onu manuel olarak kurun:

- CLI ile kurun: `openclaw plugins install @openclaw/zalouser`
- Ya da kaynak kod checkout'undan: `openclaw plugins install ./path/to/local/zalouser-plugin`
- Ayrıntılar: [Plugins](/tr/tools/plugin)

Harici bir `zca`/`openzca` CLI ikili dosyası gerekmez.

## Hızlı kurulum (başlangıç)

1. Zalo Kişisel plugin'inin kullanılabilir olduğundan emin olun.
   - Mevcut paketlenmiş OpenClaw sürümleri bunu zaten birlikte sunar.
   - Eski/özel kurulumlar bunu yukarıdaki komutlarla manuel olarak ekleyebilir.
2. Giriş yapın (QR, Gateway makinesinde):
   - `openclaw channels login --channel zalouser`
   - QR kodunu Zalo mobil uygulamasıyla tarayın.
3. Kanalı etkinleştirin:

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      dmPolicy: "pairing",
    },
  },
}
```

4. Gateway'i yeniden başlatın (veya kurulumu tamamlayın).
5. DM erişimi varsayılan olarak pairing kullanır; ilk temas sırasında pairing kodunu onaylayın.

## Nedir?

- Tamamen `zca-js` aracılığıyla süreç içinde çalışır.
- Gelen mesajları almak için yerel olay dinleyicileri kullanır.
- Yanıtları doğrudan JS API üzerinden gönderir (metin/medya/bağlantı).
- Zalo Bot API'nin mevcut olmadığı “kişisel hesap” kullanım senaryoları için tasarlanmıştır.

## Adlandırma

Kanal kimliği `zalouser` olarak belirlenmiştir; böylece bunun **kişisel bir Zalo kullanıcı hesabını** (resmi olmayan) otomatikleştirdiği açık olur. `zalo` adını gelecekte olası resmi bir Zalo API entegrasyonu için ayırıyoruz.

## Kimlikleri bulma (dizin)

Eşleri/grupları ve kimliklerini keşfetmek için dizin CLI'ını kullanın:

```bash
openclaw directory self --channel zalouser
openclaw directory peers list --channel zalouser --query "name"
openclaw directory groups list --channel zalouser --query "work"
```

## Sınırlar

- Giden metin ~2000 karaktere bölünür (Zalo istemci sınırları).
- Streaming varsayılan olarak engellenir.

## Erişim denetimi (DM'ler)

`channels.zalouser.dmPolicy` şunları destekler: `pairing | allowlist | open | disabled` (varsayılan: `pairing`).

`channels.zalouser.allowFrom`, kullanıcı kimliklerini veya adlarını kabul eder. Kurulum sırasında adlar, plugin'in süreç içi kişi araması kullanılarak kimliklere çözülür.

Şununla onaylayın:

- `openclaw pairing list zalouser`
- `openclaw pairing approve zalouser <code>`

## Grup erişimi (isteğe bağlı)

- Varsayılan: `channels.zalouser.groupPolicy = "open"` (gruplara izin verilir). Ayarlanmamışken varsayılanı geçersiz kılmak için `channels.defaults.groupPolicy` kullanın.
- Şununla bir allowlist ile sınırlandırın:
  - `channels.zalouser.groupPolicy = "allowlist"`
  - `channels.zalouser.groups` (anahtarlar kararlı grup kimlikleri olmalıdır; mümkün olduğunda adlar başlangıçta kimliklere çözülür)
  - `channels.zalouser.groupAllowFrom` (izin verilen gruplarda hangi göndericilerin botu tetikleyebileceğini kontrol eder)
- Tüm grupları engelleyin: `channels.zalouser.groupPolicy = "disabled"`.
- Yapılandırma sihirbazı, grup allowlist'leri isteyebilir.
- Başlangıçta OpenClaw, allowlist'lerdeki grup/kullanıcı adlarını kimliklere çözer ve eşlemeyi günlüğe kaydeder.
- Grup allowlist eşleştirmesi varsayılan olarak yalnızca kimlik üzerinden yapılır. Çözümlenmemiş adlar, `channels.zalouser.dangerouslyAllowNameMatching: true` etkinleştirilmediği sürece kimlik doğrulama için yok sayılır.
- `channels.zalouser.dangerouslyAllowNameMatching: true`, değiştirilebilir grup adı eşleştirmesini yeniden etkinleştiren acil durum uyumluluk modudur.
- `groupAllowFrom` ayarlanmamışsa, çalışma zamanı grup gönderici kontrolleri için `allowFrom` değerine geri döner.
- Gönderici kontrolleri hem normal grup mesajları hem de kontrol komutları için geçerlidir (örneğin `/new`, `/reset`).

Örnek:

```json5
{
  channels: {
    zalouser: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["1471383327500481391"],
      groups: {
        "123456789": { allow: true },
        "Work Chat": { allow: true },
      },
    },
  },
}
```

### Grup bahsetme geçidi

- `channels.zalouser.groups.<group>.requireMention`, grup yanıtlarının bahsetme gerektirip gerektirmediğini kontrol eder.
- Çözümleme sırası: tam grup kimliği/adı -> normalize edilmiş grup slug'ı -> `*` -> varsayılan (`true`).
- Bu hem allowlist'e alınmış gruplar hem de açık grup modu için geçerlidir.
- Bir bot mesajını alıntılamak, grup etkinleştirmesi için örtük bir bahsetme sayılır.
- Yetkili kontrol komutları (örneğin `/new`) bahsetme geçidini atlayabilir.
- Bir grup mesajı bahsetme gerektiği için atlandığında, OpenClaw bunu bekleyen grup geçmişi olarak saklar ve sonraki işlenen grup mesajına dahil eder.
- Grup geçmişi sınırı varsayılan olarak `messages.groupChat.historyLimit` değeridir (geri dönüş: `50`). Bunu hesap başına `channels.zalouser.historyLimit` ile geçersiz kılabilirsiniz.

Örnek:

```json5
{
  channels: {
    zalouser: {
      groupPolicy: "allowlist",
      groups: {
        "*": { allow: true, requireMention: true },
        "Work Chat": { allow: true, requireMention: false },
      },
    },
  },
}
```

## Çoklu hesap

Hesaplar, OpenClaw durumundaki `zalouser` profillerine eşlenir. Örnek:

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      defaultAccount: "default",
      accounts: {
        work: { enabled: true, profile: "work" },
      },
    },
  },
}
```

## Yazıyor, tepkiler ve teslim alındıları

- OpenClaw, bir yanıt göndermeden önce bir yazıyor olayı gönderir (best-effort).
- Mesaj tepki eylemi `react`, kanal eylemlerinde `zalouser` için desteklenir.
  - Bir mesajdan belirli bir tepki emojisini kaldırmak için `remove: true` kullanın.
  - Tepki semantiği: [Reactions](/tr/tools/reactions)
- Olay meta verileri içeren gelen mesajlar için OpenClaw, teslim edildi + görüldü alındıları gönderir (best-effort).

## Sorun giderme

**Giriş kalıcı olmuyor:**

- `openclaw channels status --probe`
- Yeniden giriş yapın: `openclaw channels logout --channel zalouser && openclaw channels login --channel zalouser`

**Allowlist/grup adı çözümlenmedi:**

- `allowFrom`/`groupAllowFrom`/`groups` içinde sayısal kimlikler veya tam arkadaş/grup adları kullanın.

**Eski CLI tabanlı kurulumdan yükselttiniz:**

- Eski harici `zca` süreç varsayımlarını kaldırın.
- Kanal artık harici CLI ikili dosyaları olmadan tamamen OpenClaw içinde çalışır.

## İlgili

- [Kanallara Genel Bakış](/tr/channels) — desteklenen tüm kanallar
- [Pairing](/tr/channels/pairing) — DM kimlik doğrulaması ve pairing akışı
- [Gruplar](/tr/channels/groups) — grup sohbeti davranışı ve bahsetme geçidi
- [Kanal Yönlendirme](/tr/channels/channel-routing) — mesajlar için oturum yönlendirmesi
- [Güvenlik](/tr/gateway/security) — erişim modeli ve sağlamlaştırma
